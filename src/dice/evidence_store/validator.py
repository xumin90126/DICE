"""
Phase 6.2 EvolutionValidationGate — validates EvolutionCandidates.

This module evaluates whether an EvolutionCandidate has sufficient
evidence quality to warrant human review. It NEVER:

    - Modifies CapabilityRegistry
    - Creates or registers new Capabilities
    - Auto-applies any changes
    - Updates EvolutionCandidate status

All output is PRESCRIPTIVE assessment. The decision (reject/review/approve_for_human)
is a recommendation, not an action.

Pipeline:
    EvolutionObserver.analyze()
        → list[EvolutionCandidate]
    CandidateConsolidator.consolidate()
        → merged list (same = no-op; overlapping = merged)
    EvolutionValidator.validate_batch()
        → list[EvolutionDecision]

Design:
    EvolutionValidator.validate(candidate, store, registry)
        → computes 5 evidence metrics
        → applies three-tier decision rules
        → returns EvolutionDecision

Decision rules:
    - Single occurrence (freq=1 or doc_spread=1) → reject
    - Cross-document repetition (≥5 records, ≥2 docs) → review
    - High-frequency stable gap (≥50 records, ≥3 docs) → approve_for_human

Metrics:
    - occurrence_frequency: total records supporting candidate
    - document_spread: distinct document_ids
    - repeated_failure_count: records with validation_result="fail"
    - existing_capability_overlap: # capabilities that could handle this
    - estimated_impact: frequency × document_spread
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from dice.evidence_store.models import (
    EvolutionCandidate,
    EvolutionDecision,
    EvidenceSummary,
)
from dice.evidence_store.store import MatchEvidenceStore
from dice.evidence_store.provenance import ProvenanceResolver, ProvenanceResult, PatternProvenance


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


# ═══════════════════════════════════════════════════════════════════════════
# ConsolidationResult — CandidateConsolidator output wrapper
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class ConsolidationResult:
    """
    Result of CandidateConsolidator.consolidate().

    Separates eligible (merged) candidates from those excluded by the
    provenance gate. Validator only consumes .candidates — the rest is
    audit metadata for governance/traceability.

    Phase 6.10: Introduced to decouple provenance filtering from
    EvolutionValidator. Validator API surface is unchanged.
    """

    candidates: list[Any] = field(default_factory=list)
    # Candidates eligible for validation (after provenance gate + merge)

    ignored_candidates: list[dict[str, Any]] = field(default_factory=list)
    # Candidates excluded by provenance gate:
    #   {candidate_id, pattern_ids, provenance, reason}


# ═══════════════════════════════════════════════════════════════════════════
# CandidateConsolidator — merge duplicate candidates by structure signature
# ═══════════════════════════════════════════════════════════════════════════


class CandidateConsolidator:
    """
    Merges EvolutionCandidates that share the same structural signature.

    The EvolutionObserver's four strategies can independently flag the same
    underlying gap pattern from different angles (unmatched signals, low
    confidence, repeated failures, potential gaps). This consolidator merges
    those overlapping candidates before validation, so the EvolutionValidator
    sees the true aggregate evidence picture.

    Consolidation key: gap_type + sorted(common_elements) + signature_key
    from pattern_signature. Candidates with identical keys are merged.

    Phase 6.10 — Provenance Gate:
        Before consolidation, candidates whose associated patterns have
        provenance=discrimination-test or provenance=validation-only are
        excluded from merge. This prevents test instrumentation patterns
        from contaminating real gap analysis (see Phase 6.9 post-mortem).

        Excluded candidates are recorded in _ignored_candidates for audit.

    Merge rules:
        - frequency:     summed across all merged candidates
        - record_ids:    union (deduplicated)
        - confidence:    max of all merged candidates
        - avg_confidence: weighted average by frequency
        - common_elements: union with frequency-weighted ordering
        - gap_type:      primary gap_type is the most frequent; all sources
                          stored in source_gap_types
        - pattern_signature: merged dict
        - description:   combined with summary

    Usage:
        consolidator = CandidateConsolidator()
        merged = consolidator.consolidate(candidates)
        # merged candidates → EvolutionValidator
    """

    def __init__(self):
        self._provenance_resolver = ProvenanceResolver()
        # Phase 6.10: track candidates excluded by provenance gate
        self._ignored_candidates: list[dict[str, Any]] = []

    def consolidate(
        self, candidates: list[EvolutionCandidate]
    ) -> ConsolidationResult:
        """
        Merge candidates with the same structural signature.

        Phase 6.10: Candidates are first filtered through the provenance
        gate. Discrimination-test and validation-only candidates are excluded
        and recorded in _ignored_candidates before any merge logic runs.

        Args:
            candidates: Raw candidates from EvolutionObserver

        Returns:
            ConsolidationResult with .candidates (merged, eligible) and
            .ignored_candidates (excluded by provenance gate, for audit).
        """
        if not candidates:
            self._ignored_candidates.clear()
            return ConsolidationResult(candidates=[], ignored_candidates=[])

        # ── Phase 6.10: Provenance Gate ──
        eligible: list[EvolutionCandidate] = []
        ignored: list[dict[str, Any]] = []
        for c in candidates:
            provenance = self._resolve_candidate_provenance(c)
            if self._provenance_resolver.is_eligible_for_evolution(provenance):
                eligible.append(c)
            else:
                pattern_ids = self._extract_pattern_ids(c)
                ignored.append({
                    "candidate_id": c.id,
                    "pattern_ids": pattern_ids,
                    "provenance": provenance.provenance.value,
                    "reason": (
                        self._provenance_resolver.ignore_reason(provenance)[
                            "ignored_reason"
                        ]
                    ),
                })

        self._ignored_candidates = ignored

        # All candidates excluded → nothing to consolidate
        if not eligible:
            return ConsolidationResult(
                candidates=[], ignored_candidates=list(ignored)
            )

        # Group by consolidation key
        groups: dict[str, list[EvolutionCandidate]] = {}
        for c in eligible:
            key = self._build_key(c)
            groups.setdefault(key, []).append(c)

        # Merge each group
        merged: list[EvolutionCandidate] = []
        for key, group in groups.items():
            if len(group) == 1:
                merged.append(group[0])
            else:
                merged.append(self._merge(group, key))

        return ConsolidationResult(
            candidates=merged, ignored_candidates=list(ignored)
        )

    def _build_key(self, candidate: EvolutionCandidate) -> str:
        """
        Build a structural signature key for consolidation.

        Components:
            - gap_type
            - sorted common_elements (the recurring element types)
            - signature_key from pattern_signature, normalized to strip
              document-specific prefixes (observer strategies that group by
              document_id inject per-doc keys — these must be collapsed)

        Normalization: detects and strips document-ID-prefixed sig_keys
        like "FREQ-DOC-000::..." → "..." so same-structure candidates
        from different documents coalesce.
        """
        elements = ",".join(sorted(candidate.common_elements)) if candidate.common_elements else "(none)"

        sig_key = ""
        sig = candidate.pattern_signature
        if isinstance(sig, dict):
            raw = sig.get("signature_key", "")
            sig_key = self._normalize_sig_key(raw)

        return f"{candidate.gap_type}|{elements}|{sig_key}"

    def _normalize_sig_key(self, raw_key: str) -> str:
        """
        Strip document-ID prefixes from signature keys.

        Observer strategies like _find_repeated_failures embed document
        IDs in their group key: "DOC-000::pattern_list". This is useful
        for within-document grouping but prevents cross-document
        consolidation. We strip the prefix to recover the structural
        pattern.

        Pattern: "{doc_id}::" prefix → stripped
        """
        if not raw_key:
            return ""
        # Strip known document-ID prefix pattern: "XXX-####::..." → "..."
        # Matches: FREQ-DOC-000::, DOC-001::, NDM609ME::, etc.
        import re
        stripped = re.sub(r'^[\w-]+::', '', raw_key, count=1)
        return stripped

    def _merge(
        self, group: list[EvolutionCandidate], key: str
    ) -> EvolutionCandidate:
        """
        Merge a group of candidates sharing the same structural signature.

        Rules as specified:
        - Combine frequency (sum)
        - Combine document_count (union of record_ids → count unique docs)
        - Combine evidence ids (union)
        - Keep highest confidence
        - Preserve all source gap_types
        """
        # ── Frequency: sum ──
        total_freq = sum(c.frequency for c in group)

        # ── Record IDs: union ──
        all_record_ids: list[str] = []
        seen_ids: set[str] = set()
        for c in group:
            for rid in c.record_ids:
                if rid not in seen_ids:
                    seen_ids.add(rid)
                    all_record_ids.append(rid)

        # ── Confidence: max ──
        max_conf = max(c.confidence for c in group)

        # ── Avg confidence: weighted by frequency ──
        total_freq_for_avg = sum(c.frequency for c in group)
        weighted_avg = (
            sum(c.avg_confidence * c.frequency for c in group) / total_freq_for_avg
            if total_freq_for_avg > 0 else 0.0
        )

        # ── Common elements: union with frequency-weighted ordering ──
        elem_freq: dict[str, int] = {}
        for c in group:
            for elem in c.common_elements:
                elem_freq[elem] = elem_freq.get(elem, 0) + c.frequency
        merged_elements = [
            e for e, _ in sorted(elem_freq.items(), key=lambda x: -x[1])
        ]

        # ── Gap types: collect all sources, pick most frequent as primary ──
        gap_type_counts: dict[str, int] = {}
        for c in group:
            gap_type_counts[c.gap_type] = gap_type_counts.get(c.gap_type, 0) + 1
        primary_gap_type = max(gap_type_counts, key=lambda k: gap_type_counts[k])
        all_gap_types = sorted(gap_type_counts.keys())

        # ── Pattern signature: merge ──
        merged_sig: dict[str, Any] = {"source_gap_types": all_gap_types}
        for c in group:
            sig = c.pattern_signature
            if isinstance(sig, dict):
                for k, v in sig.items():
                    if k not in merged_sig:
                        merged_sig[k] = v

        # ── Timestamps: earliest first, latest last ──
        first_seen = min(
            (c.first_seen_at for c in group if c.first_seen_at),
            default=_now(),
        )
        last_seen = max(
            (c.last_seen_at for c in group if c.last_seen_at),
            default=_now(),
        )

        # ── Description: combined ──
        all_desc = [c.description for c in group if c.description]
        combined_desc = f"[Merged from {len(group)} candidates ({', '.join(all_gap_types)})] " + (
            all_desc[0][:250] if all_desc else ""
        )

        # ── Suggested direction: take from most frequent ──
        primary = max(group, key=lambda c: c.frequency)

        return EvolutionCandidate(
            id=_uid("EVO-MERGED-"),
            gap_type=primary_gap_type,
            description=combined_desc,
            record_ids=all_record_ids,
            pattern_signature=merged_sig,
            frequency=total_freq,
            first_seen_at=first_seen,
            last_seen_at=last_seen,
            avg_confidence=round(weighted_avg, 4),
            common_elements=merged_elements,
            suggested_direction=primary.suggested_direction,
            status="draft",
            confidence=round(max_conf, 4),
        )

    # ═══════════════════════════════════════════════════════════════════
    # Phase 6.10: Provenance helpers
    # ═══════════════════════════════════════════════════════════════════

    def _resolve_candidate_provenance(
        self, candidate: EvolutionCandidate
    ) -> ProvenanceResult:
        """
        Resolve the provenance of an EvolutionCandidate by examining its
        pattern signature and metadata.

        Delegates to ProvenanceResolver. Extracts the best available
        metadata (tags, confidence, evidence_count) from the candidate's
        structure.

        Args:
            candidate: An EvolutionCandidate from the EvolutionObserver

        Returns:
            ProvenanceResult with classification and eligibility.
        """
        # ── Extract pattern_id(s) ──
        pattern_ids = self._extract_pattern_ids(candidate)
        primary_id = pattern_ids[0] if pattern_ids else candidate.id

        # ── Extract tags from pattern_signature ──
        tags: list[str] = []
        sig = candidate.pattern_signature
        if isinstance(sig, dict):
            # Direct tags
            for tag in sig.get("tags", []):
                if isinstance(tag, str):
                    tags.append(tag)
            # Implicit: source_gap_types may hint at discrimination-test
            source_types = sig.get("source_gap_types", [])
            if isinstance(source_types, list):
                tags.extend(str(s) for s in source_types)

        # ── Confidence: use candidate's observer confidence ──
        confidence = float(candidate.confidence)

        # ── Evidence count: use candidate.frequency as proxy ──
        evidence_count = candidate.frequency

        # ── Status: from candidate ──
        status = candidate.status

        return self._provenance_resolver.resolve(
            pattern_id=primary_id,
            tags=tags,
            confidence=confidence,
            evidence_count=evidence_count,
            status=status,
        )

    def _extract_pattern_ids(self, candidate: EvolutionCandidate) -> list[str]:
        """
        Extract pattern identifiers from an EvolutionCandidate's signature.

        Examines pattern_signature for identifiable pattern IDs in order:
            1. unmatched_signal (string)
            2. dominant_patterns (list of strings)
            3. signature_key (string)
            4. gap_type + common_elements (derived fallback)

        Returns:
            List of pattern ID strings (never empty).
        """
        sig = candidate.pattern_signature
        if isinstance(sig, dict):
            # Priority 1: explicit unmatched signal
            us = sig.get("unmatched_signal", "")
            if us:
                return [str(us)]

            # Priority 2: dominant patterns
            dps = sig.get("dominant_patterns", [])
            if dps:
                return [str(p) for p in dps]

            # Priority 3: signature key
            sk = sig.get("signature_key", "")
            if sk:
                return [str(sk)]

        # Priority 4: derived from gap_type + common_elements
        derived = f"{candidate.gap_type}:{','.join(candidate.common_elements[:3])}"
        return [derived] if derived else [candidate.id]

    def get_ignored_candidates(self) -> list[dict[str, Any]]:
        """
        Return candidates that were excluded from consolidation by the
        provenance gate.

        Each entry:
            {
                "candidate_id": "EVO-xxxxxxxx",
                "pattern_ids": ["PAT-PARAMETER-LIST", ...],
                "provenance": "discrimination-test",
                "reason": "expected validation signal",
            }

        Returns:
            List of ignored candidate records (empty if none excluded).
        """
        return list(self._ignored_candidates)


# ═══════════════════════════════════════════════════════════════════════════
# Decision thresholds
# ═══════════════════════════════════════════════════════════════════════════

REVIEW_MIN_FREQUENCY = 5          # ≥5 records to consider review
REVIEW_MIN_DOC_SPREAD = 2         # ≥2 documents for review
APPROVE_MIN_FREQUENCY = 50        # ≥50 records for escalate
APPROVE_MIN_DOC_SPREAD = 3        # ≥3 documents for escalate
OVERLAP_LOW_THRESHOLD = 2         # ≤2 overlapping capabilities = likely gap
OVERLAP_HIGH_THRESHOLD = 5        # ≥5 overlapping capabilities = well-covered

# ── Debug flag (temporary, remove after Phase 6.2 verification) ──
_DEBUG = False


class EvolutionValidator:
    """
    Validates EvolutionCandidates against Evidence Store and Registry.

    Computes the five evidence metrics and applies three-tier decision rules
    to determine whether a candidate warrants human attention.

    Usage:
        validator = EvolutionValidator()
        decision = validator.validate(candidate, store, registry)

        print(f"[{decision.decision}] {decision.reason}")
        print(f"  Confidence: {decision.confidence:.2f}")
        for k, v in decision.evidence_summary.to_dict().items():
            print(f"  {k}: {v}")
    """

    def validate(
        self,
        candidate: EvolutionCandidate,
        store: MatchEvidenceStore,
        registry: Any = None,  # CapabilityRegistry, optional for overlap check
    ) -> EvolutionDecision:
        """
        Validate a single EvolutionCandidate.

        Args:
            candidate: EvolutionCandidate from EvolutionObserver
            store: MatchEvidenceStore with all MatchRecords
            registry: Optional CapabilityRegistry for overlap analysis

        Returns:
            EvolutionDecision with decision level and evidence metrics
        """
        # ───────────────────────────────────────────────────────────────
        # Step 1: Compute evidence metrics
        # ───────────────────────────────────────────────────────────────
        summary = self._compute_evidence(candidate, store, registry)

        # ── Temporary debug: trace decision pipeline ──
        if _DEBUG:
            print(f"  [DEBUG validate] candidate={candidate.id[:24]} "
                  f"gap={candidate.gap_type} "
                  f"freq={summary.occurrence_frequency} "
                  f"docs={summary.document_spread} "
                  f"overlap={summary.existing_capability_overlap} "
                  f"impact={summary.estimated_impact}")

        # ───────────────────────────────────────────────────────────────
        # Step 2: Apply decision rules
        # ───────────────────────────────────────────────────────────────
        decision, confidence, reason = self._decide(candidate, summary)

        if _DEBUG:
            print(f"    → decision={decision} confidence={confidence:.3f}")
            print(f"    → reason={reason[:120]}")

        return EvolutionDecision(
            candidate_id=candidate.id,
            decision=decision,
            confidence=confidence,
            evidence_summary=summary,
            reason=reason,
        )

    def validate_batch(
        self,
        candidates: list[EvolutionCandidate],
        store: MatchEvidenceStore,
        registry: Any = None,
        consolidate: bool = True,
    ) -> list[EvolutionDecision]:
        """
        Validate multiple candidates. Returns list of decisions.

        If consolidate=True (default), runs CandidateConsolidator first
        to merge overlapping candidates with the same structural signature.
        This ensures the validator sees the aggregate evidence picture.
        """
        if consolidate and len(candidates) > 1:
            consolidator = CandidateConsolidator()
            result = consolidator.consolidate(candidates)
            candidates = result.candidates

        return [
            self.validate(c, store, registry)
            for c in candidates
        ]

    # ═══════════════════════════════════════════════════════════════════
    # Evidence Metrics Computation
    # ═══════════════════════════════════════════════════════════════════

    def _compute_evidence(
        self,
        candidate: EvolutionCandidate,
        store: MatchEvidenceStore,
        registry: Any = None,
    ) -> EvidenceSummary:
        """
        Compute the five quantitative evidence metrics for a candidate.

        1. occurrence_frequency — from candidate.frequency
        2. document_spread — distinct document_ids across candidate.record_ids
        3. repeated_failure_count — records with validation_result="fail"
        4. existing_capability_overlap — from registry query (if available)
        5. estimated_impact — occurrence_frequency × document_spread
        """
        # ── Metric 1: Occurrence frequency ──
        occurrence = candidate.frequency

        # ── Metric 2: Document spread ──
        doc_ids: set[str] = set()
        all_records = store.get_all()
        for r in all_records:
            if r.id in candidate.record_ids and r.document_id:
                doc_ids.add(r.document_id)
        # Fallback: if no records found by ID, use total unique docs in store
        if not doc_ids:
            doc_ids = set(store.get_document_ids())
        doc_spread = len(doc_ids)

        # ── Metric 3: Repeated failure count ──
        failure_count = 0
        for r in store.get_all():
            if r.id in candidate.record_ids and r.is_failure:
                failure_count += 1
        # If no explicit failures, use frequency as proxy for low-confidence records
        if failure_count == 0 and candidate.avg_confidence < 0.3:
            failure_count = occurrence

        # ── Metric 4: Existing capability overlap ──
        overlap, strategy = self._compute_overlap(candidate, store, registry)

        # ── Temporary debug: trace which strategy produces the overlap ──
        # Remove after Phase 6.2 verification is complete.
        if _DEBUG:
            print(f"  [DEBUG _compute_evidence] candidate={candidate.id[:24]} "
                  f"gap={candidate.gap_type} "
                  f"overlap={overlap} strategy={strategy}")

        # ── Metric 5: Estimated impact ──
        impact = float(occurrence) * float(doc_spread)

        return EvidenceSummary(
            occurrence_frequency=occurrence,
            document_spread=doc_spread,
            repeated_failure_count=failure_count,
            existing_capability_overlap=overlap,
            estimated_impact=impact,
        )

    # ═══════════════════════════════════════════════════════════════════
    # Non-discriminative term filtering for overlap normalization
    # ═══════════════════════════════════════════════════════════════════
    #
    # The overlap metric should reflect GENUINE functional similarity
    # between a candidate gap and existing capabilities — not linguistic
    # proximity caused by shared generic vocabulary.
    #
    # Problem: capability descriptions share a common vocabulary of
    #   - action/process verbs   (detects, identifies, extracts, validates...)
    #   - generic content nouns  (content, text, data, entries, sections...)
    #   - structural qualifiers  (structured, pattern-based, list-format...)
    #
    # These terms appear in virtually every capability description and do
    # NOT help distinguish one capability's domain from another. They
    # inflate overlap counts, making unrelated capabilities appear similar.
    #
    # Solution: normalize capability text by stripping non-discriminative
    # terms before keyword matching. The filtered text retains only:
    #   - Domain-specific nouns    (component, table, temperature, safety...)
    #   - Functional domain terms  (name, quantity, unit, catalog, storage...)
    #
    # This ensures overlap reflects what the capability ACTUALLY handles,
    # not how its description is phrased.
    #
    # NON_DISCRIMINATIVE_TERMS — words that appear across all/most
    # capability descriptions regardless of domain. Categories:
    #   Verbs:    generic detection/extraction/validation actions
    #   Medium:   generic data-structure nouns (the "what it works on", not
    #             the domain it addresses)
    #   Struct:   organizational qualifiers (how data is arranged)
    #   Qualify:  domain-independent modifiers and connectives

    _NON_DISCRIMINATIVE_TERMS: set[str] = {
        # ── Generic action/process verbs ──
        "detects", "detection", "identifies", "identification",
        "extracts", "extraction", "validates", "validation",
        "classifies", "classification", "handles", "handling",
        "reconstructs", "reconstruction", "understands", "understanding",
        "distinguishes", "shares", "uses", "performs", "counters",
        # ── Generic medium/carrier nouns ──
        "content", "text", "data", "entries", "sections",
        "elements", "element", "items", "item",
        # ── Structural/format qualifiers ──
        "structured", "structure", "structures",
        "pattern", "patterns", "pattern-based",
        "format", "formats", "list", "lists",
        # ── Domain-independent modifiers ──
        "using", "based", "from", "with", "for",
        "into", "within", "across", "any", "all",
        "multiple", "various", "specific", "common",
        "simplified", "basic", "intact", "different",
        "potential", "possible",
    }

    @classmethod
    def _normalize_capability_text(cls, name: str, scope: str, description: str) -> str:
        """
        Strip non-discriminative terms from capability text.

        Retains functional and domain-specific terms that distinguish one
        capability from another (component, table, temperature, safety,
        quantity, catalog, procedure, etc.).
        """
        import re

        raw = f"{name} {scope} {description}".lower()
        # Tokenize: split on non-alpha boundaries, preserving compound tokens
        tokens = re.findall(r'[a-z]+', raw)

        filtered = [
            t for t in tokens
            if t not in cls._NON_DISCRIMINATIVE_TERMS
        ]
        return " ".join(filtered)

    def _compute_overlap(
        self,
        candidate: EvolutionCandidate,
        store: MatchEvidenceStore,
        registry: Any = None,
        _debug: bool = False,  # temporary debug flag
    ) -> tuple[int, str]:
        """
        Estimate how many existing Capabilities could theoretically handle
        this candidate's pattern.

        ALL overlap evaluation paths use non-discriminative term filtering:
        capability descriptions are normalized before keyword matching to
        remove generic vocabulary shared across all capabilities. This
        ensures overlap reflects true functional domain proximity, not
        linguistic coincidence.

        Strategy:
            A (primary): Registry keyword match with normalized capability
               text. Available whenever registry is not None.
            B (fallback): Estimate from MatchRecord data. Only used when
               registry is NOT available. Records estimated overlap from
               the capabilities that appeared in candidate's records.

        IMPORTANT: Strategy B is gated by registry availability, NOT by
        Strategy A's result. When registry is available, the normalized
        keyword match IS the final answer — even if it's 0. This prevents
        un-normalized MatchRecord matches from bypassing the filter.

        Returns:
            (overlap_count, strategy_label)
            overlap_count: 0 = true gap, >0 = some overlap exists
            strategy_label: "A" | "A(normalized)" | "B(fallback)"
        """
        strategy_label = "?"

        # Strategy A: Normalized registry keyword match
        if registry is not None:
            try:
                active_caps = registry.list_active()
                # Build a keyword set from candidate
                keywords = set(candidate.common_elements)
                keywords.add(candidate.gap_type)
                sig = candidate.pattern_signature
                if isinstance(sig, dict):
                    # Add dominant patterns/elements from signature
                    for pat in sig.get("dominant_patterns", []):
                        if isinstance(pat, str):
                            keywords.add(pat.lower())
                    for elem in sig.get("dominant_elements", {}):
                        keywords.add(str(elem).lower())

                # Filter: only keywords with len > 3
                active_kw = {kw for kw in keywords if kw and len(kw) > 3}

                overlap_count = 0
                matched_cap_details: list[str] = []

                for cap in active_caps:
                    name = cap.name.lower() if hasattr(cap, "name") else ""
                    scope = str(cap.scope).lower() if hasattr(cap, "scope") else ""
                    desc = cap.description.lower() if hasattr(cap, "description") else ""

                    raw_text = f"{name} {scope} {desc}"
                    # ── Normalize: strip non-discriminative terms ──
                    cap_text = self._normalize_capability_text(name, scope, desc)

                    # Heuristic: ≥2 keyword matches = potential overlap
                    matching_kw = [
                        kw for kw in active_kw
                        if kw.lower() in cap_text
                    ]
                    if len(matching_kw) >= 2:
                        overlap_count += 1
                        matched_cap_details.append(
                            f"{cap.id}(kw={matching_kw[:3]})"
                        )

                strategy_label = "A(normalized)"

                if _debug:
                    print(f"  [DEBUG overlap] candidate={candidate.id[:20]}")
                    print(f"    strategy={strategy_label}")
                    print(f"    keywords={sorted(active_kw)}")
                    print(f"    raw_text(first cap): {raw_text[:120]}")
                    cap_text_demo = self._normalize_capability_text(
                        active_caps[0].name.lower() if hasattr(active_caps[0], "name") else "",
                        str(active_caps[0].scope).lower() if hasattr(active_caps[0], "scope") else "",
                        active_caps[0].description.lower() if hasattr(active_caps[0], "description") else "",
                    )
                    print(f"    norm_text(first cap): {cap_text_demo[:120]}")
                    print(f"    overlap_count={overlap_count}")
                    if matched_cap_details:
                        print(f"    matched: {matched_cap_details}")

                return overlap_count, strategy_label

            except Exception as e:
                if _debug:
                    print(f"  [DEBUG overlap] Strategy A failed: {e}")
                pass  # registry query failed → fall through

        # Strategy B: Estimate from MatchRecords (registry unavailable ONLY)
        strategy_label = "B(fallback)"
        overlap_count = 0
        if store.count() > 0:
            all_related_caps: set[str] = set()
            for r in store.get_all():
                if r.id in candidate.record_ids:
                    for mc in r.matched_capabilities:
                        cid = mc.get("capability_id", "")
                        score = mc.get("score", 0.0)
                        if cid and score > 0.15:
                            all_related_caps.add(cid)
            overlap_count = len(all_related_caps)

        if _debug:
            print(f"  [DEBUG overlap] candidate={candidate.id[:20]}")
            print(f"    strategy={strategy_label} (no registry)")
            print(f"    overlap_count={overlap_count}")

        return overlap_count, strategy_label

    # ═══════════════════════════════════════════════════════════════════
    # Decision Rules
    # ═══════════════════════════════════════════════════════════════════

    def _decide(
        self,
        candidate: EvolutionCandidate,
        summary: EvidenceSummary,
    ) -> tuple[str, float, str]:
        """
        Apply three-tier decision rules to the evidence summary.

        Tier 1 — REJECT: insufficient evidence
            - Single occurrence (frequency == 1)
            - Single document (document_spread == 1)
            - High existing capability overlap (≥5)

        Tier 2 — REVIEW: enough evidence for human inspection
            - Cross-document repetition (≥5 records, ≥2 documents)
            - Moderate impact with low overlap

        Tier 3 — APPROVE_FOR_HUMAN: strong signal, escalate
            - High frequency (≥50 records)
            - Wide document spread (≥3 documents)
            - Low existing capability overlap (≤2)
            - High estimated impact

        Returns:
            (decision, confidence, reason)
        """
        freq = summary.occurrence_frequency
        spread = summary.document_spread
        failures = summary.repeated_failure_count
        overlap = summary.existing_capability_overlap
        impact = summary.estimated_impact

        # ───────────────────────────────────────────────────────────────
        # Tier 3: APPROVE_FOR_HUMAN — strong evidence of a stable gap
        # ───────────────────────────────────────────────────────────────
        # Two paths to approval:
        #   A) High frequency + wide spread + low overlap (clean gap)
        #   B) Very high impact (≥400) with moderate overlap (≤5) —
        #      suggests a pattern important enough to review despite
        #      partial capability coverage
        if (
            freq >= APPROVE_MIN_FREQUENCY
            and spread >= APPROVE_MIN_DOC_SPREAD
            and overlap <= OVERLAP_LOW_THRESHOLD
        ):
            conf = min(0.95, 0.6 + 0.005 * freq)
            return (
                "approve_for_human",
                round(conf, 4),
                (
                    f"High-frequency stable gap: {freq} records across "
                    f"{spread} documents, with only {overlap} overlapping "
                    f"capabilit{'y' if overlap == 1 else 'ies'} "
                    f"(estimated impact: {impact:.0f}). "
                    f"This pattern occurs frequently enough and is poorly "
                    f"covered by existing capabilities to warrant human "
                    f"review for potential capability design."
                ),
            )

        # Path B: very high impact with moderate overlap
        if impact >= 400 and overlap <= 5 and spread >= APPROVE_MIN_DOC_SPREAD:
            conf = min(0.85, 0.45 + 0.004 * spread)
            return (
                "approve_for_human",
                round(conf, 4),
                (
                    f"Very high-impact recurring pattern: {freq} records "
                    f"across {spread} documents (impact: {impact:.0f}). "
                    f"While {overlap} capabilities show some overlap, the "
                    f"scale and persistence of this gap warrants human "
                    f"review for potential capability design."
                ),
            )

        # ───────────────────────────────────────────────────────────────
        # Tier 2: REVIEW — cross-document repetition warrants attention
        # ───────────────────────────────────────────────────────────────
        if freq >= REVIEW_MIN_FREQUENCY and spread >= REVIEW_MIN_DOC_SPREAD:
            if overlap >= OVERLAP_HIGH_THRESHOLD:
                # High overlap → downgrade confidence
                conf = min(0.6, 0.3 + 0.03 * spread)
                return (
                    "review",
                    round(conf, 4),
                    (
                        f"Cross-document repetition ({freq} records, {spread} docs) "
                        f"but {overlap} existing capabilities overlap — pattern may "
                        f"already be partially covered. Review to determine if gap "
                        f"is real or due to capability tuning issues."
                    ),
                )
            else:
                conf = min(0.85, 0.4 + 0.06 * spread)
                return (
                    "review",
                    round(conf, 4),
                    (
                        f"Cross-document repetition detected: {freq} records "
                        f"across {spread} documents with {failures} failures "
                        f"and only {overlap} overlapping capabilit{'y' if overlap == 1 else 'ies'}. "
                        f"Estimated impact: {impact:.0f}. "
                        f"This warrants human inspection to determine whether "
                        f"a new capability is needed."
                    ),
                )

        # ───────────────────────────────────────────────────────────────
        # Tier 1: REJECT — insufficient evidence
        # ───────────────────────────────────────────────────────────────
        if freq <= 1 or spread <= 1:
            return (
                "reject",
                0.9,
                (
                    f"Insufficient evidence: only {freq} record(s) across "
                    f"{spread} document(s). A single occurrence does not "
                    f"constitute a reliable gap signal. More data is needed "
                    f"before this candidate warrants human review."
                ),
            )

        # Default: borderline → reject with note
        return (
            "reject",
            0.55,
            (
                f"Borderline evidence: {freq} records across {spread} "
                f"document(s) does not meet the minimum threshold for review "
                f"(requires ≥{REVIEW_MIN_FREQUENCY} records, ≥{REVIEW_MIN_DOC_SPREAD} docs). "
                f"Continue accumulating evidence before re-evaluating."
            ),
        )


# ═══════════════════════════════════════════════════════════════════════════
# Convenience: validate all candidates at once
# ═══════════════════════════════════════════════════════════════════════════


def validate_candidates(
    candidates: list[EvolutionCandidate],
    store: MatchEvidenceStore,
    registry: Any = None,
    consolidate: bool = True,
) -> dict[str, Any]:
    """
    One-shot validation: consolidate + evaluate all candidates, return summary.

    By default, runs CandidateConsolidator before validation to merge
    overlapping candidates.

    Returns:
        {
            "total_candidates": N,
            "rejected": R,
            "review": V,
            "approve_for_human": A,
            "decisions": [EvolutionDecision.to_dict(), ...],
        }
    """
    # ── Consolidation pass ──
    if consolidate and len(candidates) > 1:
        consolidator = CandidateConsolidator()
        result = consolidator.consolidate(candidates)
        candidates = result.candidates

    validator = EvolutionValidator()
    decisions = validator.validate_batch(
        candidates, store, registry, consolidate=False  # already consolidated
    )

    counts = {"reject": 0, "review": 0, "approve_for_human": 0}
    for d in decisions:
        if d.decision in counts:
            counts[d.decision] += 1

    return {
        "total_candidates": len(candidates),
        **counts,
        "decisions": [d.to_dict() for d in decisions],
    }
