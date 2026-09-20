"""
Phase 6.1 EvolutionObserver — scans MatchEvidenceStore for evolution signals.

This module is READ-ONLY. It analyzes accumulated MatchRecords and produces
EvolutionCandidates describing detected gaps. It NEVER:
    - Modifies CapabilityRegistry
    - Creates or registers new Capabilities
    - Auto-applies any changes
    - Calls CapabilityMatcher or Runtime

All output is DESCRIPTIVE observation. Candidates start as "draft" and
require explicit validation before any downstream action (future phase).

Detection strategies:
    1. Unmatched signals — patterns/elements with zero capability match
    2. Low confidence — consistently low match scores across records
    3. Repeated failures — same failure signature across ≥3 records
    4. Potential capability gap — recurring structural pattern with no handler
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from dice.evidence_store.models import MatchRecord, EvolutionCandidate
from dice.evidence_store.store import MatchEvidenceStore
from dice.evidence_store.provenance import ProvenanceResolver, ProvenanceResult, PatternProvenance


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


# ═══════════════════════════════════════════════════════════════════════════
# Config
# ═══════════════════════════════════════════════════════════════════════════

DEFAULT_LOW_CONFIDENCE_THRESHOLD = 0.3
DEFAULT_REPEATED_FAILURE_MIN = 3
DEFAULT_GAP_MIN_FREQUENCY = 3           # min records for potential_capability_gap


class EvolutionObserver:
    """
    Observes MatchEvidenceStore for evolution signals.

    Produces EvolutionCandidates — DESCRIPTIVE gap descriptions that
    require explicit validation before any Registry modification.

    Usage:
        store = MatchEvidenceStore()
        observer = EvolutionObserver()
        candidates = observer.analyze(store)

        for c in candidates:
            print(f"[{c.gap_type}] {c.description} "
                  f"(frequency={c.frequency}, confidence={c.confidence:.2f})")
    """

    def __init__(
        self,
        low_confidence_threshold: float = DEFAULT_LOW_CONFIDENCE_THRESHOLD,
        repeated_failure_min: int = DEFAULT_REPEATED_FAILURE_MIN,
        gap_min_frequency: int = DEFAULT_GAP_MIN_FREQUENCY,
    ):
        self._low_conf_threshold = low_confidence_threshold
        self._failure_min = repeated_failure_min
        self._gap_min_freq = gap_min_frequency
        self._provenance_resolver = ProvenanceResolver()
        # Phase 6.10: track ignored signals for audit
        self._ignored_signals: list[dict[str, Any]] = []

    # ═══════════════════════════════════════════════════════════════════
    # MAIN ENTRY POINT
    # ═══════════════════════════════════════════════════════════════════

    def analyze(self, store: MatchEvidenceStore) -> list[EvolutionCandidate]:
        """
        Scan the store and produce all detected EvolutionCandidates.

        Returns list of candidates (all "draft" status, never auto-applied).
        Returns empty list if store has insufficient records.
        """
        records = store.get_all()
        if len(records) < self._gap_min_freq:
            return []

        candidates: list[EvolutionCandidate] = []

        # ── Strategy 1: Unmatched signals ──
        candidates.extend(self._find_unmatched_signals(store, records))

        # ── Strategy 2: Low confidence ──
        candidates.extend(self._find_low_confidence(store, records))

        # ── Strategy 3: Repeated failures ──
        candidates.extend(self._find_repeated_failures(store, records))

        # ── Strategy 4: Potential capability gaps ──
        candidates.extend(self._find_potential_gaps(store, records))

        return candidates

    # ═══════════════════════════════════════════════════════════════════
    # STRATEGY 1: Unmatched Signals
    # ═══════════════════════════════════════════════════════════════════

    def _find_unmatched_signals(
        self, store: MatchEvidenceStore, records: list[MatchRecord]
    ) -> list[EvolutionCandidate]:
        """
        Find patterns/element types that appear across multiple records
        but have NO matching capability.

        A signal is "unmatched" when it's detected by ObservationBuilder
        (in detected_patterns or element_types) but no capability in the
        match result references it.
        """
        candidates: list[EvolutionCandidate] = []

        # Collect all unmatched signals across records
        signal_records: dict[str, list[MatchRecord]] = {}
        for r in records:
            for sig in r.unmatched_signals:
                signal_records.setdefault(sig, []).append(r)

        for sig, sig_recs in signal_records.items():
            if len(sig_recs) < self._gap_min_freq:
                continue

            # ── Phase 6.10: Provenance Gate ──
            provenance = self._resolve_signal_provenance(sig)
            if not self._provenance_resolver.is_eligible_for_evolution(provenance):
                self._ignored_signals.append({
                    "pattern_id": sig,
                    "provenance": provenance.provenance.value,
                    "reason": self._provenance_resolver.ignore_reason(provenance)[
                        "ignored_reason"
                    ],
                    "source_strategy": "unmatched_signals",
                })
                continue

            documents = list(set(r.document_id for r in sig_recs))
            avg_score = (
                sum(r.top_capability_score for r in sig_recs) / len(sig_recs)
                if sig_recs else 0.0
            )

            candidate = EvolutionCandidate(
                id=_uid("EVO-"),
                gap_type="unmatched_signals",
                description=(
                    f"Signal '{sig}' detected in {len(sig_recs)} records "
                    f"across {len(documents)} document(s) but has NO matching "
                    f"capability. Average top score: {avg_score:.3f}."
                ),
                record_ids=[r.id for r in sig_recs],
                pattern_signature={
                    "unmatched_signal": sig,
                    "signal_type": "pattern" if not sig.startswith("elem:") else "element",
                },
                frequency=len(sig_recs),
                first_seen_at=min(r.timestamp for r in sig_recs if r.timestamp),
                last_seen_at=max(r.timestamp for r in sig_recs if r.timestamp),
                avg_confidence=avg_score,
                common_elements=self._most_frequent_elements(sig_recs, top_n=5),
                suggested_direction=(
                    f"Signal '{sig}' appears repeatedly without a matching "
                    f"capability. Consider whether a handler for this signal "
                    f"type would improve match quality."
                ),
                status="draft",
                confidence=min(0.9, 0.3 + 0.1 * len(sig_recs)),
            )
            candidates.append(candidate)

        return candidates

    # ═══════════════════════════════════════════════════════════════════
    # STRATEGY 2: Low Confidence
    # ═══════════════════════════════════════════════════════════════════

    def _find_low_confidence(
        self, store: MatchEvidenceStore, records: list[MatchRecord]
    ) -> list[EvolutionCandidate]:
        """
        Find records where the top capability match score is consistently
        below the low-confidence threshold.

        When multiple records from the same structural pattern cluster
        have low scores, this suggests a capability gap.
        """
        low_conf = store.get_low_confidence(self._low_conf_threshold)

        if len(low_conf) < self._gap_min_freq:
            return []

        # Cluster by structural pattern signature
        clusters = self._cluster_by_signature(low_conf)

        candidates: list[EvolutionCandidate] = []
        for sig_key, cluster_recs in clusters.items():
            if len(cluster_recs) < self._gap_min_freq:
                continue

            documents = list(set(r.document_id for r in cluster_recs))
            avg_score = (
                sum(r.top_capability_score for r in cluster_recs) / len(cluster_recs)
                if cluster_recs else 0.0
            )

            candidate = EvolutionCandidate(
                id=_uid("EVO-"),
                gap_type="low_confidence",
                description=(
                    f"Low-confidence matches detected: {len(cluster_recs)} records "
                    f"with similar structure across {len(documents)} document(s) "
                    f"(avg top score: {avg_score:.3f}, threshold: {self._low_conf_threshold}). "
                    f"Structural signature: {sig_key[:100]}"
                ),
                record_ids=[r.id for r in cluster_recs],
                pattern_signature={
                    "signature_key": sig_key,
                    "avg_top_score": avg_score,
                    "threshold": self._low_conf_threshold,
                },
                frequency=len(cluster_recs),
                first_seen_at=min(r.timestamp for r in cluster_recs if r.timestamp),
                last_seen_at=max(r.timestamp for r in cluster_recs if r.timestamp),
                avg_confidence=avg_score,
                common_elements=self._most_frequent_elements(cluster_recs, top_n=5),
                suggested_direction=(
                    f"Records with this structure consistently score below "
                    f"{self._low_conf_threshold}. The structure may not be "
                    f"covered by any registered Capability."
                ),
                status="draft",
                confidence=min(0.95, 0.4 + 0.1 * len(cluster_recs)),
            )
            candidates.append(candidate)

        return candidates

    # ═══════════════════════════════════════════════════════════════════
    # STRATEGY 3: Repeated Failures
    # ═══════════════════════════════════════════════════════════════════

    def _find_repeated_failures(
        self, store: MatchEvidenceStore, records: list[MatchRecord]
    ) -> list[EvolutionCandidate]:
        """
        Find validation failure patterns that repeat across ≥min records
        with the same structural signature.
        """
        failure_groups = store.get_repeated_failures(self._failure_min)

        candidates: list[EvolutionCandidate] = []
        for sig_key, failure_recs in failure_groups.items():
            documents = list(set(r.document_id for r in failure_recs))
            reasons = list(set(
                r.failure_reason for r in failure_recs if r.failure_reason
            ))

            candidate = EvolutionCandidate(
                id=_uid("EVO-"),
                gap_type="repeated_failure",
                description=(
                    f"Repeated validation failure: {len(failure_recs)} records "
                    f"across {len(documents)} document(s) share the same failure "
                    f"signature. Reasons: {reasons[:3]}"
                ),
                record_ids=[r.id for r in failure_recs],
                pattern_signature={
                    "signature_key": sig_key,
                    "failure_reasons": reasons,
                    "failure_count": len(failure_recs),
                },
                frequency=len(failure_recs),
                first_seen_at=min(r.timestamp for r in failure_recs if r.timestamp),
                last_seen_at=max(r.timestamp for r in failure_recs if r.timestamp),
                avg_confidence=(
                    sum(r.top_capability_score for r in failure_recs) / len(failure_recs)
                    if failure_recs else 0.0
                ),
                common_elements=self._most_frequent_elements(failure_recs, top_n=5),
                suggested_direction=(
                    f"Same validation failure occurs {len(failure_recs)} times. "
                    f"Review the failure reasons and consider whether a new or "
                    f"modified capability could handle this content type."
                ),
                status="draft",
                confidence=min(0.9, 0.5 + 0.1 * len(failure_recs)),
            )
            candidates.append(candidate)

        return candidates

    # ═══════════════════════════════════════════════════════════════════
    # STRATEGY 4: Potential Capability Gaps
    # ═══════════════════════════════════════════════════════════════════

    def _find_potential_gaps(
        self, store: MatchEvidenceStore, records: list[MatchRecord]
    ) -> list[EvolutionCandidate]:
        """
        Find recurring structural patterns across records where the top
        match score is below a threshold AND the pattern is consistent.

        This is the most important strategy — it detects "there's a content
        type that keeps appearing but nothing handles it well."

        Clustering approach:
        1. Group records by their STRUCTURAL signature (flags + element types)
        2. For each cluster, check if top scores are consistently low
        3. If yes → potential_capability_gap candidate
        """
        # Only consider records with low-ish confidence for clustering
        low_to_medium = [
            r for r in records
            if r.top_capability_score < 0.5
        ]

        if len(low_to_medium) < self._gap_min_freq:
            return []

        clusters = self._cluster_by_signature(low_to_medium)

        candidates: list[EvolutionCandidate] = []
        for sig_key, cluster_recs in clusters.items():
            if len(cluster_recs) < self._gap_min_freq:
                continue

            documents = list(set(r.document_id for r in cluster_recs))
            avg_score = (
                sum(r.top_capability_score for r in cluster_recs) / len(cluster_recs)
                if cluster_recs else 0.0
            )

            # Collect dominant patterns across cluster
            all_patterns: list[str] = []
            for r in cluster_recs:
                all_patterns.extend(r.detected_patterns)
            from collections import Counter
            top_patterns = [p for p, _ in Counter(all_patterns).most_common(5)]

            # Collect dominant element types
            all_elements: dict[str, int] = {}
            for r in cluster_recs:
                for k, v in r.element_types.items():
                    all_elements[k] = all_elements.get(k, 0) + v

            candidate = EvolutionCandidate(
                id=_uid("EVO-"),
                gap_type="potential_capability_gap",
                description=(
                    f"Potential capability gap: {len(cluster_recs)} records "
                    f"across {len(documents)} document(s) share a common "
                    f"structural pattern but have low match scores "
                    f"(avg: {avg_score:.3f}). Dominant patterns: {top_patterns[:3]}. "
                    f"This may indicate a content type not covered by registered "
                    f"capabilities."
                ),
                record_ids=[r.id for r in cluster_recs],
                pattern_signature={
                    "signature_key": sig_key,
                    "dominant_patterns": top_patterns,
                    "dominant_elements": dict(
                        sorted(all_elements.items(), key=lambda x: -x[1])[:5]
                    ),
                    "avg_top_score": avg_score,
                    "record_count": len(cluster_recs),
                },
                frequency=len(cluster_recs),
                first_seen_at=min(r.timestamp for r in cluster_recs if r.timestamp),
                last_seen_at=max(r.timestamp for r in cluster_recs if r.timestamp),
                avg_confidence=avg_score,
                common_elements=self._most_frequent_elements(cluster_recs, top_n=5),
                suggested_direction=(
                    f"A recurring structural pattern was detected in "
                    f"{len(cluster_recs)} records but no capability scores "
                    f"above 0.5 for it. Consider registering a new capability "
                    f"for this content type after manual review."
                ),
                status="draft",
                confidence=min(0.95, 0.35 + 0.1 * len(cluster_recs)),
            )
            candidates.append(candidate)

        return candidates

    # ═══════════════════════════════════════════════════════════════════
    # Phase 6.10: Provenance helpers
    # ═══════════════════════════════════════════════════════════════════

    def _resolve_signal_provenance(self, signal_id: str) -> ProvenanceResult:
        """
        Resolve the provenance of an unmatched signal.

        Delegates to ProvenanceResolver with default metadata lookup.
        This is a thin wrapper — provenance logic lives in ProvenanceResolver,
        not here.

        Args:
            signal_id: Pattern ID or element signal identifier

        Returns:
            ProvenanceResult with classification and eligibility.
        """
        return self._provenance_resolver.resolve(
            pattern_id=signal_id,
            tags=[],
            confidence=0.0,
            evidence_count=0,
            status="",
        )

    def get_ignored_signals(self) -> list[dict[str, Any]]:
        """
        Return signals that were excluded from evolution candidate generation
        by the provenance gate.

        Each entry:
            {
                "pattern_id": "PAT-PARAMETER-LIST",
                "provenance": "discrimination-test",
                "reason": "expected validation signal",
                "source_strategy": "unmatched_signals",
            }

        Returns:
            List of ignored signal records (empty if no signals were excluded).
        """
        return list(self._ignored_signals)

    # ═══════════════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════════════

    def _cluster_by_signature(
        self, records: list[MatchRecord]
    ) -> dict[str, list[MatchRecord]]:
        """
        Cluster records by structural signature.

        Signature = sorted(structure_flag_keys_where_true) + sorted(element_type_keys_where_gt_0)
        Only uses keys where value is positive/True to avoid noise.
        """
        clusters: dict[str, list[MatchRecord]] = {}
        for r in records:
            # Extract active flags
            active_flags = sorted(
                k for k, v in r.structure_flags.items() if v
            )
            # Extract element types with values > 0
            active_elements = sorted(
                k for k, v in r.element_types.items() if v > 0
            )
            # Build signature key
            sig_key = (
                "flags:" + ",".join(active_flags)
                + "|elems:" + ",".join(active_elements)
            )
            clusters.setdefault(sig_key, []).append(r)

        return clusters

    def _most_frequent_elements(
        self, records: list[MatchRecord], top_n: int = 5
    ) -> list[str]:
        """Find most common element types across a group of records."""
        from collections import Counter
        counter: Counter = Counter()
        for r in records:
            for k, v in r.element_types.items():
                if v > 0:
                    counter[k] += v
        return [elem for elem, _ in counter.most_common(top_n)]


# ═══════════════════════════════════════════════════════════════════════════
# Convenience: analyze at a glance
# ═══════════════════════════════════════════════════════════════════════════


def analyze_store(
    store: MatchEvidenceStore,
    low_conf_threshold: float = DEFAULT_LOW_CONFIDENCE_THRESHOLD,
    failure_min: int = DEFAULT_REPEATED_FAILURE_MIN,
    gap_min_freq: int = DEFAULT_GAP_MIN_FREQUENCY,
) -> dict[str, Any]:
    """
    One-shot analysis: scan store, return summary dict.

    Returns:
        {
            "total_records": N,
            "candidates_found": M,
            "by_type": {"unmatched_signals": 2, "low_confidence": 1, ...},
            "candidates": [EvolutionCandidate.to_dict(), ...],
            "ignored_signals": [{pattern_id, provenance, reason, ...}, ...],
            "ignored_count": K,
        }
    """
    observer = EvolutionObserver(
        low_confidence_threshold=low_conf_threshold,
        repeated_failure_min=failure_min,
        gap_min_frequency=gap_min_freq,
    )
    candidates = observer.analyze(store)

    by_type: dict[str, int] = {}
    for c in candidates:
        by_type[c.gap_type] = by_type.get(c.gap_type, 0) + 1

    return {
        "total_records": store.count(),
        "candidates_found": len(candidates),
        "by_type": by_type,
        "candidates": [c.to_dict() for c in candidates],
        # Phase 6.10: governance audit trail
        "ignored_signals": observer.get_ignored_signals(),
        "ignored_count": len(observer.get_ignored_signals()),
    }
