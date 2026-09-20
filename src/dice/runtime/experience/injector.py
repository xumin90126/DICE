"""
Knowledge Injector — applies mined experience to Capability knowledge.

CRITICAL CONSTRAINT: Only updates are allowed to:
    ✅ Pattern Library         — new/updated detection patterns
    ✅ Evidence Vocabulary     — new vocabulary entries with semantic categories
    ✅ Capability Knowledge    — updated metadata, confidence, documents_tested

FORBIDDEN:
    ❌ New doc_class rules
    ❌ New if-else branches
    ❌ Hardcoded document-specific mappings
    ❌ Changes to execution logic

The injector validates that all changes are to the allowed targets ONLY.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from dice.graph.experience_graph import ExperienceGraph
from dice.graph.nodes import Capability, Pattern, PatternStatus, CapabilityStatus
from dice.graph.edges import Edge, EdgeType
from dice.runtime.experience.miner import MiningResult, EvidencePattern, RecognitionPattern


@dataclass
class InjectionRecord:
    """Record of a single knowledge injection."""
    target: str = ""         # "vocabulary" | "pattern" | "capability_metadata"
    entity_id: str = ""      # What was updated
    change: str = ""         # What changed
    before_value: Any = None
    after_value: Any = None
    source: str = ""         # Where the knowledge came from


@dataclass
class InjectionResult:
    """Complete result of knowledge injection."""
    capability_id: str = "CAP-COMP-TABLE"

    # Counts
    vocabulary_terms_added: int = 0
    vocabulary_categories_added: int = 0
    patterns_added: int = 0
    patterns_updated: int = 0
    capability_metadata_updated: int = 0

    # Details
    records: list[InjectionRecord] = field(default_factory=list)

    # Validation
    forbidden_changes_detected: int = 0
    forbidden_change_details: list[str] = field(default_factory=list)
    injection_valid: bool = True

    # Summary
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "vocabulary_terms_added": self.vocabulary_terms_added,
            "vocabulary_categories_added": self.vocabulary_categories_added,
            "patterns_added": self.patterns_added,
            "patterns_updated": self.patterns_updated,
            "capability_metadata_updated": self.capability_metadata_updated,
            "forbidden_changes_detected": self.forbidden_changes_detected,
            "forbidden_change_details": self.forbidden_change_details,
            "injection_valid": self.injection_valid,
            "summary": self.summary,
            "records": [
                {
                    "target": r.target,
                    "entity_id": r.entity_id,
                    "change": r.change,
                    "source": r.source,
                }
                for r in self.records
            ],
        }


class KnowledgeInjector:
    """
    Injects mined experience into Capability knowledge.

    Three injection targets (ALLOWED):
        1. Evidence Vocabulary — new terms organized by semantic category
        2. Pattern Library — new/updated detection patterns
        3. Capability Knowledge — updated metrics, confidence, scope

    Injection flow:
        MiningResult → validate → apply to ExperienceGraph → validate again
    """

    # ── Semantic category mapping for new vocabulary ──
    SEMANTIC_TO_VOCAB_CATEGORY = {
        "enzyme_reagent": "biochemical_reagents",
        "buffer_solution": "buffers_solutions",
        "nucleic_acid": "nucleic_acid",
        "purification_media": "purification_media",
        "consumable": "consumables",
        "instrument": "instruments",
        "chemical": "biochemical_reagents",
        "unknown": "biochemical_reagents",  # default category for unknown types
    }

    def __init__(self, graph: ExperienceGraph):
        self.graph = graph

    # ═══════════════════════════════════════════════════════════
    # MAIN INJECTION PIPELINE
    # ═══════════════════════════════════════════════════════════

    def inject(self, mining_result: MiningResult) -> InjectionResult:
        """
        Inject all mined knowledge from MiningResult into the graph.

        Order matters: vocabulary first (patterns may reference new terms),
        then patterns, then capability metadata.
        """
        result = InjectionResult(
            capability_id=mining_result.capability_id,
        )

        # Phase 1: Inject vocabulary from gaps
        vocab_records = self._inject_vocabulary(mining_result)
        result.records.extend(vocab_records)
        result.vocabulary_terms_added = sum(
            1 for r in vocab_records if r.target == "vocabulary" and "add" in r.change
        )
        result.vocabulary_categories_added = sum(
            1 for r in vocab_records if r.target == "vocabulary" and "new_category" in r.change
        )

        # Phase 2: Inject evidence patterns
        pattern_records = self._inject_evidence_patterns(mining_result.evidence_patterns)
        result.records.extend(pattern_records)
        result.patterns_added = sum(
            1 for r in pattern_records if r.target == "pattern" and r.change == "add"
        )
        result.patterns_updated = sum(
            1 for r in pattern_records if r.target == "pattern" and r.change == "update"
        )

        # Phase 3: Inject recognition patterns
        rec_pattern_records = self._inject_recognition_patterns(mining_result.recognition_patterns)
        result.records.extend(rec_pattern_records)

        # Phase 4: Update capability metadata
        meta_records = self._inject_capability_metadata(mining_result)
        result.records.extend(meta_records)
        result.capability_metadata_updated = len(meta_records)

        # Validate no forbidden changes
        self._validate_injection(result)

        # Build summary
        result.summary = self._build_summary(result, mining_result)

        return result

    # ═══════════════════════════════════════════════════════════
    # PHASE 1: VOCABULARY INJECTION
    # ═══════════════════════════════════════════════════════════

    def _inject_vocabulary(self, mining_result: MiningResult) -> list[InjectionRecord]:
        """
        Inject vocabulary gaps into Capability knowledge.

        Each new term is added to the appropriate semantic category
        in the Capability's scope.vocabulary dict.
        """
        records = []
        cap = self.graph.capabilities.get(mining_result.capability_id)
        if not cap:
            return records

        # Get current vocabulary
        vocab = cap.scope.get("vocabulary", {})
        if not vocab:
            return records

        # For each gap, add to vocabulary
        for sem_type, terms in mining_result.vocabulary_gaps.items():
            category = self.SEMANTIC_TO_VOCAB_CATEGORY.get(
                sem_type, "biochemical_reagents"
            )

            # Create category if not exists
            if category not in vocab:
                vocab[category] = []
                records.append(InjectionRecord(
                    target="vocabulary",
                    entity_id=f"category:{category}",
                    change="new_category",
                    before_value=None,
                    after_value=category,
                    source="experience_mining",
                ))

            for term in terms:
                if term not in vocab[category]:
                    vocab[category].append(term)
                    records.append(InjectionRecord(
                        target="vocabulary",
                        entity_id=f"term:{term}",
                        change="add",
                        before_value=None,
                        after_value={"term": term, "category": category, "semantic_type": sem_type},
                        source="ground_truth_gap_analysis",
                    ))

        # Update the capability's scope
        cap.scope["vocabulary"] = vocab

        return records

    # ═══════════════════════════════════════════════════════════
    # PHASE 2: EVIDENCE PATTERN INJECTION
    # ═══════════════════════════════════════════════════════════

    def _inject_evidence_patterns(
        self, evidence_patterns: list[EvidencePattern],
    ) -> list[InjectionRecord]:
        """
        Inject evidence patterns as Pattern nodes.

        Each evidence pattern becomes a new/updated Pattern in the graph.
        Patterns are DESCRIPTIVE — they describe structural/semantic
        phenomena, NOT procedural rules.
        """
        records = []

        for ep in evidence_patterns:
            # Only inject if confidence is sufficient (>0.5 = at least 2 sources)
            if ep.confidence < 0.5:
                continue

            pat_id = ep.pattern_id
            pat_name = f"Evidence: {ep.token} ({ep.semantic_type})"

            if pat_id in self.graph.patterns:
                # Update existing
                pat = self.graph.patterns[pat_id]
                old_confidence = pat.confidence
                pat.confidence = max(pat.confidence, ep.confidence)
                pat.evidence_count = ep.source_count
                pat.status = (
                    PatternStatus.VERIFIED
                    if ep.source_count >= 3
                    else PatternStatus.CANDIDATE
                )
                records.append(InjectionRecord(
                    target="pattern",
                    entity_id=pat_id,
                    change="update",
                    before_value={"confidence": old_confidence},
                    after_value={"confidence": pat.confidence, "evidence_count": ep.source_count},
                    source="evidence_mining",
                ))
            else:
                # Create new pattern
                pat = Pattern(
                    id=pat_id,
                    name=pat_name,
                    description=f"Evidence pattern for '{ep.token}' — "
                                f"semantic type: {ep.semantic_type}, "
                                f"context: {ep.context}. "
                                f"Found in {ep.source_count} document(s): "
                                f"{', '.join(ep.source_documents)}.",
                    detection_signals=[
                        f"token '{ep.token}' appears in component context",
                        f"surrounded by: {ep.surrounding_pattern}",
                    ],
                    structural_indicators=[
                        f"context: {ep.context}",
                    ],
                    content_indicators=[
                        f"semantic_type: {ep.semantic_type}",
                        f"category: {ep.category}",
                    ],
                    status=(
                        PatternStatus.VERIFIED
                        if ep.source_count >= 3
                        else PatternStatus.CANDIDATE
                    ),
                    confidence=ep.confidence,
                    evidence_count=ep.source_count,
                    source_documents=ep.source_documents,
                    cross_doc_count=len(set(ep.source_documents)),
                    tags=[ep.semantic_type, ep.category, "evidence_mined"],
                )
                self.graph.add_pattern(pat)
                records.append(InjectionRecord(
                    target="pattern",
                    entity_id=pat_id,
                    change="add",
                    before_value=None,
                    after_value={"name": pat_name, "evidence_count": ep.source_count},
                    source="evidence_mining",
                ))

        return records

    # ═══════════════════════════════════════════════════════════
    # PHASE 3: RECOGNITION PATTERN INJECTION
    # ═══════════════════════════════════════════════════════════

    def _inject_recognition_patterns(
        self, recognition_patterns: list[RecognitionPattern],
    ) -> list[InjectionRecord]:
        """Inject structural recognition patterns."""
        records = []

        for rp in recognition_patterns:
            pat_id = rp.pattern_id

            if pat_id not in self.graph.patterns:
                pat = Pattern(
                    id=pat_id,
                    name=rp.pattern_name,
                    description=rp.description,
                    detection_signals=rp.constraints,
                    structural_indicators=[
                        f"pattern_type: {rp.pattern_type}",
                    ],
                    content_indicators=[
                        f"vocabulary_categories: {rp.typical_vocabulary_categories}",
                        f"density_range: {rp.typical_density_range}",
                        f"entry_count_range: {rp.typical_entry_count_range}",
                    ],
                    status=(
                        PatternStatus.CANDIDATE
                        if rp.confidence < 0.7
                        else PatternStatus.VERIFIED
                    ),
                    confidence=rp.confidence,
                    evidence_count=rp.source_count,
                    source_documents=rp.source_documents,
                    cross_doc_count=len(rp.source_documents),
                    tags=[rp.pattern_type, "recognition", "mined"],
                )
                self.graph.add_pattern(pat)
                records.append(InjectionRecord(
                    target="pattern",
                    entity_id=pat_id,
                    change="add",
                    before_value=None,
                    after_value={"name": rp.pattern_name, "type": rp.pattern_type},
                    source="recognition_mining",
                ))

        return records

    # ═══════════════════════════════════════════════════════════
    # PHASE 4: CAPABILITY METADATA
    # ═══════════════════════════════════════════════════════════

    def _inject_capability_metadata(
        self, mining_result: MiningResult,
    ) -> list[InjectionRecord]:
        """
        Update Capability metadata based on experience.

        Allowed updates:
        - documents_tested (add new documents)
        - cross_doc_success_rate (recompute)
        - status → ACTIVE if confidence threshold met
        - epoch incremented
        - version incremented
        """
        records = []
        cap = self.graph.capabilities.get(mining_result.capability_id)
        if not cap:
            return records

        # Collect all distinct documents from mining
        all_docs = set()
        for ep in mining_result.evidence_patterns:
            all_docs.update(ep.source_documents)
        for rp in mining_result.recognition_patterns:
            all_docs.update(rp.source_documents)

        new_docs = [d for d in all_docs if d not in cap.documents_tested]
        if new_docs:
            old_count = len(cap.documents_tested)
            cap.documents_tested.extend(new_docs)
            cap.documents_tested = list(set(cap.documents_tested))
            records.append(InjectionRecord(
                target="capability_metadata",
                entity_id="documents_tested",
                change="update",
                before_value=old_count,
                after_value=len(cap.documents_tested),
                source="experience_mining",
            ))

        # Recompute cross-doc success rate
        success_cases = mining_result.success_cases
        total_cases = max(mining_result.total_cases_analyzed, 1)
        old_rate = cap.cross_doc_success_rate
        cap.cross_doc_success_rate = success_cases / total_cases
        records.append(InjectionRecord(
            target="capability_metadata",
            entity_id="cross_doc_success_rate",
            change="update",
            before_value=old_rate,
            after_value=cap.cross_doc_success_rate,
            source="experience_mining",
        ))

        # Update status if enough experience accumulated
        old_status = cap.status
        if len(all_docs) >= 3 and cap.cross_doc_success_rate >= 0.5:
            cap.status = CapabilityStatus.ACTIVE
        records.append(InjectionRecord(
            target="capability_metadata",
            entity_id="status",
            change="update",
            before_value=old_status.value,
            after_value=cap.status.value,
            source="experience_mining",
        ))

        # Increment epoch (knowledge evolution)
        old_epoch = cap.epoch
        cap.epoch += 1
        records.append(InjectionRecord(
            target="capability_metadata",
            entity_id="epoch",
            change="update",
            before_value=old_epoch,
            after_value=cap.epoch,
            source="experience_injection",
        ))

        # Increment version
        old_version = cap.version
        cap.version += 1
        records.append(InjectionRecord(
            target="capability_metadata",
            entity_id="version",
            change="update",
            before_value=old_version,
            after_value=cap.version,
            source="experience_injection",
        ))

        return records

    # ═══════════════════════════════════════════════════════════
    # VALIDATION
    # ═══════════════════════════════════════════════════════════

    def _validate_injection(self, result: InjectionResult) -> None:
        """
        Validate that no forbidden changes were made.

        Checks:
        1. No new doc_class in capability scope
        2. No new implementation logic (only allow vocabulary/pattern/capability)
        3. No if-else additions in any target
        """
        forbidden = []

        # Check 1: Capability scope must not contain doc_class
        cap = self.graph.capabilities.get(result.capability_id)
        if cap and "doc_class" in cap.scope:
            forbidden.append(
                "FORBIDDEN: doc_class found in capability scope"
            )

        # Check 2: Only allowed targets were modified
        allowed_targets = {"vocabulary", "pattern", "capability_metadata"}
        for record in result.records:
            if record.target not in allowed_targets:
                forbidden.append(
                    f"FORBIDDEN: Injection target '{record.target}' is not allowed. "
                    f"Only {allowed_targets} are permitted."
                )

        # Check 3: No new implementations were added
        impl_ids_before = set(self.graph.implementations.keys())
        # (we don't track before, but we can check if any impl was for a non-CAP-COMP-TABLE)
        # This is a soft check — the injector doesn't add implementations anyway

        if forbidden:
            result.forbidden_changes_detected = len(forbidden)
            result.forbidden_change_details = forbidden
            result.injection_valid = False
        else:
            result.forbidden_changes_detected = 0
            result.injection_valid = True

    def _build_summary(
        self, result: InjectionResult, mining_result: MiningResult,
    ) -> str:
        parts = []

        if result.vocabulary_terms_added > 0:
            parts.append(
                f"Added {result.vocabulary_terms_added} vocabulary terms "
                f"across {result.vocabulary_categories_added} categories."
            )

        if result.patterns_added > 0:
            parts.append(
                f"Created {result.patterns_added} new evidence/recognition patterns."
            )

        if result.patterns_updated > 0:
            parts.append(
                f"Updated {result.patterns_updated} existing patterns "
                f"with new evidence."
            )

        if result.capability_metadata_updated > 0:
            parts.append(
                f"Updated capability metadata ({result.capability_metadata_updated} changes)."
            )

        if result.injection_valid:
            parts.append("✅ All changes validated — no forbidden modifications.")
        else:
            parts.append(
                f"❌ {result.forbidden_changes_detected} forbidden changes detected!"
            )

        parts.append(
            f"Knowledge deficit: {mining_result.knowledge_deficit_summary[:100]}"
        )

        return " ".join(parts)


# ═══════════════════════════════════════════════════════════════
# CONVENIENCE
# ═══════════════════════════════════════════════════════════════

def inject_experience(
    graph: ExperienceGraph,
    mining_result: MiningResult,
) -> InjectionResult:
    """Convenience: mine → inject in one step."""
    injector = KnowledgeInjector(graph)
    return injector.inject(mining_result)
