"""
Capability Runtime Shadow Adapter — Phase 2 Step 4.

Bridges the Evidence Runtime output to the Capability Runtime in shadow mode.
Consumes EvidenceView (from Shadow Evidence Runtime), builds synthetic
DocumentObservations with structural signals derived from evidence types,
runs the existing CapabilityMatcher, and produces CapabilityActivationShadowResult.

CRITICAL ARCHITECTURE:
    Evidence Runtime  ──(orthogonal)──>  Capability Runtime
    "What evidence exists?"              "Which capability should handle it?"

    The adapter bridges these two orthogonal layers:
    - Evidence types → structural signals → DocumentObservation
    - DocumentObservation → CapabilityMatcher → Capability Activation

    Evidence types are capability-INDEPENDENT semantic categories.
    Structural signals are the bridge — they describe structural characteristics
    (NOT domain vocabulary, NOT keyword rules).

Pipeline:
    ShadowEvidenceResult[]
        │  1227 evidence spans (capability-independent)
        │
        ▼
    EvidenceView ──> CapabilityRuntimeShadowAdapter
        │
        │  1. Map evidence types → structural signals
        │  2. Build DocumentObservation per document
        │  3. CapabilityMatcher.match(observation)
        │  4. Record CapabilityActivationShadowResult
        │
        ▼
    CapabilityActivationTrace[]
        │  Complete evidence → capability traceability

CONSTRAINTS:
    - Zero production code modification
    - Zero CapabilityMatcher modification
    - Zero CapabilityDefinition modification
    - Zero keyword rules
    - Zero capability_id hardcoding
    - Zero document-specific logic
    - Evidence Runtime and Capability Runtime remain orthogonal
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from dice.graph.nodes import DocumentObservation, Capability, MatchCandidate
from dice.registry import CapabilityRegistry
from dice.runtime.matching import CapabilityMatcher, ObservationBuilder, MatchResult


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


# ═══════════════════════════════════════════════════════════════════════════
# Evidence → Structural Signal Mapping
# ═══════════════════════════════════════════════════════════════════════════
#
# Maps evidence types (capability-independent semantic categories) to
# structural signals that the CapabilityMatcher can detect.
#
# This is NOT a keyword rule — it maps semantic categories to structural
# characteristics. The CapabilityMatcher then uses its own structural
# pattern detection to match capabilities.
#
# Each evidence type maps to structural signals that the ObservationBuilder
# would detect if the document contained that type of content.

EVIDENCE_TO_SIGNALS: dict[str, dict[str, Any]] = {
    "storage_condition": {
        "temperature": 3,
        "has_key_value_pairs": True,
        "line_count": 10,
    },
    "safety_statement": {
        "header_section_count": 3,
        "has_list_structure": True,
        "has_key_value_pairs": True,
        "line_count": 8,
    },
    "anomaly_recovery": {
        "has_list_structure": True,
        "header_section_count": 2,
        "line_count": 12,
    },
    "sequential_step": {
        "has_list_structure": True,
        "line_count": 20,
        "has_numbered_list": True,
    },
    "condition_procedure": {
        "has_list_structure": True,
        "line_count": 15,
        "has_numbered_list": True,
    },
    "preparation_step": {
        "has_list_structure": True,
        "name": 3,
        "count": 1,
        "line_count": 10,
    },
    "test_method": {
        "has_list_structure": True,
        "header_section_count": 1,
        "line_count": 12,
        "volume": 2,
        "concentration": 1,
    },
    "comparison": {
        "has_key_value_pairs": True,
        "line_count": 8,
        "header_section_count": 1,
    },
    "component_spec": {
        "name": 6,
        "quantity": 3,
        "count": 1,
        "has_key_value_pairs": True,
        "has_collapsed_table": True,
        "line_count": 6,
    },
    "unknown": {
        "line_count": 5,
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# Data Types
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class CapabilityActivationTrace:
    """
    Complete evidence → capability traceability record.

    Every Capability activation MUST be traceable back to Evidence.
    No activation without evidence support.

    Fields:
        document_id: source document
        evidence_id: source evidence span ID
        capability_id: activated capability
        evidence_type: evidence type category
        problem_role: problem signal role
        resolution_role: resolution signal role
        boundary_decision: boundary validation result
        confidence: activation confidence
        reasoning: human-readable explanation of why this activation occurred
    """
    document_id: str = ""
    evidence_id: str = ""
    capability_id: str = ""
    evidence_type: str = ""
    problem_role: str = ""
    resolution_role: str = ""
    boundary_decision: str = ""
    confidence: float = 0.0
    reasoning: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "evidence_id": self.evidence_id,
            "capability_id": self.capability_id,
            "evidence_type": self.evidence_type,
            "problem_role": self.problem_role,
            "resolution_role": self.resolution_role,
            "boundary_decision": self.boundary_decision,
            "confidence": round(self.confidence, 4),
            "reasoning": self.reasoning,
        }


@dataclass
class CapabilityActivationShadowResult:
    """
    Shadow Capability activation result for one document.

    Contains:
    - activated_capabilities: capabilities that would be activated by the evidence
    - confidence: overall activation confidence
    - evidence_references: evidence spans supporting each activation
    - boundary_validation_result: capability boundary validation
    - rejected_candidates: capabilities that were rejected with reasons
    - traces: full evidence → capability traceability records
    """
    document_id: str = ""
    activated_capabilities: list[dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    evidence_references: list[dict[str, Any]] = field(default_factory=list)
    boundary_validation_result: dict[str, Any] = field(default_factory=dict)
    rejected_candidates: list[dict[str, Any]] = field(default_factory=list)
    traces: list[CapabilityActivationTrace] = field(default_factory=list)
    match_result: Optional[dict[str, Any]] = None

    # Statistics
    total_evidence: int = 0
    evidence_with_activation: int = 0
    evidence_without_activation: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "activated_capabilities": self.activated_capabilities,
            "confidence": round(self.confidence, 4),
            "evidence_references": self.evidence_references,
            "boundary_validation_result": self.boundary_validation_result,
            "rejected_candidates": self.rejected_candidates,
            "traces": [t.to_dict() for t in self.traces],
            "match_result": self.match_result,
            "statistics": {
                "total_evidence": self.total_evidence,
                "evidence_with_activation": self.evidence_with_activation,
                "evidence_without_activation": self.evidence_without_activation,
            },
        }


# ═══════════════════════════════════════════════════════════════════════════
# CapabilityRuntimeShadowAdapter
# ═══════════════════════════════════════════════════════════════════════════


class CapabilityRuntimeShadowAdapter:
    """
    Shadow Adapter: Evidence Runtime → Capability Runtime.

    Consumes EvidenceView output, builds DocumentObservations with
    structural signals derived from evidence types, runs the existing
    CapabilityMatcher, and produces shadow activation results.

    The CapabilityMatcher is used READ-ONLY — its internal logic is
    never modified. This adapter only wraps and observes.

    Usage:
        adapter = CapabilityRuntimeShadowAdapter(registry)
        result = adapter.activate(
            evidence_data=shadow_evidence_dict,
            document_id="C112-英文V22.1",
        )
        # result.activated_capabilities, result.traces, etc.
    """

    def __init__(
        self,
        registry: Optional[CapabilityRegistry] = None,
        shadow_mode: bool = True,
        shadow_top_k: int = 50,
    ):
        """
        Initialize the adapter.

        Args:
            registry: CapabilityRegistry to use. If None, bootstraps a new one.
            shadow_mode: If True (default), returns ALL valid candidates for
                analysis. This is the key difference from production: shadow
                observes the COMPLETE candidate space, not just top_k.
            shadow_top_k: Maximum candidates to return in shadow mode.
                Default 50 ensures all registered capabilities are visible.
        """
        if registry is None:
            from dice.bootstrap import bootstrap_registry
            from dice.registry import CapabilityRegistry
            registry = CapabilityRegistry()
            bootstrap_registry(registry)
        self._registry = registry
        self._matcher: Optional[CapabilityMatcher] = None
        self._shadow_mode = shadow_mode
        self._shadow_top_k = shadow_top_k

    @property
    def matcher(self) -> CapabilityMatcher:
        """Lazy-init the CapabilityMatcher (uses existing registry)."""
        if self._matcher is None:
            if self._shadow_mode:
                # Shadow mode: observe COMPLETE candidate space.
                # Production top_k=5 truncates valid candidates (e.g.
                # CAP-SAFETY-DETECT at rank 5, CAP-TROUBLESHOOT-DETECT
                # at rank 8). Shadow evaluation MUST see all candidates
                # to produce accurate metrics.
                from dice.runtime.matching import MatcherConfig
                shadow_config = MatcherConfig(
                    top_k=self._shadow_top_k,
                    include_low_confidence=True,
                )
                self._matcher = CapabilityMatcher(self._registry, config=shadow_config)
            else:
                self._matcher = CapabilityMatcher(self._registry)
        return self._matcher

    def activate(
        self,
        evidence_data: dict[str, Any],
        document_id: str = "",
    ) -> CapabilityActivationShadowResult:
        """
        Activate capabilities based on evidence data in shadow mode.

        Args:
            evidence_data: per-document dict from shadow_evidence.json
                Expected keys: evidence_type_distribution, problem_role_distribution,
                evidence (list of ShadowEvidenceResult dicts)
            document_id: document identifier

        Returns:
            CapabilityActivationShadowResult with activation details.
        """
        # ── Step 1: Build DocumentObservation from evidence signals ──
        observation = self._build_observation(evidence_data, document_id)

        # ── Step 2: Run CapabilityMatcher ──
        match_result = self.matcher.match(observation)

        # ── Step 3: Build activation result ──
        return self._build_activation_result(
            evidence_data, document_id, match_result, observation,
        )

    def _build_observation(
        self,
        evidence_data: dict[str, Any],
        document_id: str,
    ) -> DocumentObservation:
        """
        Build a DocumentObservation from evidence type distribution.

        Maps evidence types → structural signals, then constructs
        a DocumentObservation with those signals set. This ensures
        the CapabilityMatcher sees the right structural characteristics
        WITHOUT any domain vocabulary or keyword injection.
        """
        ev_type_dist = evidence_data.get("evidence_type_distribution", {})
        evidence_list = evidence_data.get("evidence", [])

        # ── Aggregate structural signals from all evidence types ──
        signals: dict[str, Any] = {
            "line_count": 0,
            "avg_line_length": 50.0,
            "has_table_structure": False,
            "has_collapsed_table": False,
            "has_list_structure": False,
            "has_key_value_pairs": False,
            "has_markdown_table": False,
            "has_numbered_list": False,
            "has_numeric_density_high": False,
            "header_section_count": 0,
            "name": 0,
            "quantity": 0,
            "unit": 0,
            "catalog_number": 0,
            "count": 0,
            "volume": 0,
            "concentration": 0,
            "temperature": 0,
            "temperature_range": 0,
            "time": 0,
        }

        # Aggregate from all evidence types present
        for ev_type, freq in ev_type_dist.items():
            mapping = EVIDENCE_TO_SIGNALS.get(ev_type, EVIDENCE_TO_SIGNALS["unknown"])
            for key, value in mapping.items():
                if key in signals:
                    if isinstance(value, bool):
                        signals[key] = signals[key] or value
                    elif isinstance(value, (int, float)):
                        signals[key] = max(signals[key], value)
                    else:
                        signals[key] = value

        # Derived signals
        signals["has_numeric_density_high"] = signals["quantity"] >= 5

        # ── Build content snippet from evidence ──
        snippets = []
        for ev in evidence_list[:10]:
            span_text = ev.get("source_span_text", "")
            if span_text:
                snippets.append(span_text)
        content_snippet = " | ".join(snippets)[:500]

        # ── Construct DocumentObservation ──
        obs = DocumentObservation(
            id=f"OBS-SHADOW-{document_id}",
            document_id=document_id,
            slice_id="shadow_evidence",
            content_snippet=content_snippet,
            content_length=sum(len(ev.get("source_span_text", "")) for ev in evidence_list),
            line_count=signals["line_count"],
            avg_line_length=signals["avg_line_length"],
            has_table_structure=signals["has_table_structure"],
            has_collapsed_table=signals["has_collapsed_table"],
            has_list_structure=signals["has_list_structure"],
            has_key_value_pairs=signals["has_key_value_pairs"],
            has_markdown_table=signals["has_markdown_table"],
            has_numbered_list=signals["has_numbered_list"],
            has_numeric_density_high=signals["has_numeric_density_high"],
            header_section_count=signals["header_section_count"],
            detected_element_types={
                k: v for k, v in signals.items()
                if k in ("name", "quantity", "unit", "catalog_number", "count",
                         "volume", "concentration", "temperature", "temperature_range", "time")
            },
        )

        # Apply pattern inference
        obs.detected_pattern_ids = ObservationBuilder._infer_patterns(obs, content_snippet)

        return obs

    def _build_activation_result(
        self,
        evidence_data: dict[str, Any],
        document_id: str,
        match_result: MatchResult,
        observation: DocumentObservation,
    ) -> CapabilityActivationShadowResult:
        """
        Build CapabilityActivationShadowResult from the CapabilityMatcher output.

        Links each evidence span to the capability that would handle it,
        producing full traceability.
        """
        evidence_list = evidence_data.get("evidence", [])
        ev_type_dist = evidence_data.get("evidence_type_distribution", {})

        # ── Activated capabilities ──
        activated = []
        for c in match_result.candidates:
            if c.score >= 0.25:  # threshold from MatcherConfig
                activated.append({
                    "capability_id": c.capability_id,
                    "capability_name": c.capability_name,
                    "score": round(c.score, 4),
                    "pattern_match_score": round(c.pattern_match_score, 4),
                    "evidence_quality_score": round(c.evidence_quality_score, 4),
                    "historical_success_score": round(c.historical_success_score, 4),
                    "matched_patterns": c.matched_patterns,
                    "matched_element_types": c.matched_element_types,
                    "evidence_summary": c.evidence_summary,
                })

        # ── Rejected candidates ──
        rejected = []
        for c in match_result.candidates:
            if c.score < 0.25:
                rejected.append({
                    "capability_id": c.capability_id,
                    "capability_name": c.capability_name,
                    "score": round(c.score, 4),
                    "rejection_reason": f"Score {c.score:.3f} below threshold 0.25",
                })

        # ── Evidence references ──
        evidence_refs = []
        for ev in evidence_list:
            ev_type = ev.get("evidence_type", "unknown")
            evidence_refs.append({
                "evidence_id": ev.get("span_id", ""),
                "evidence_type": ev_type,
                "problem_role": ev.get("problem_role", ""),
                "resolution_role": ev.get("resolution_role", ""),
                "confidence": ev.get("confidence", 0.0),
            })

        # ── Build traces: link evidence → capability ──
        traces = self._build_traces(
            evidence_list, activated, document_id, observation,
        )

        # ── Boundary validation ──
        boundary = {
            "total_evidence_types": len(ev_type_dist),
            "evidence_types": dict(ev_type_dist),
            "activated_capabilities_count": len(activated),
            "rejected_candidates_count": len(rejected),
            "capability_explosion_check": len(activated) <= 5,  # max 5 is reasonable
            "safety_fp_check": "safety" not in str(activated).lower() or len(activated) <= 3,
            "storage_fp_check": "storage" not in str(activated).lower() or len(activated) <= 3,
        }

        # ── Overall confidence ──
        if activated:
            overall_conf = sum(c["score"] for c in activated) / len(activated)
        else:
            overall_conf = 0.0

        # ── Evidence activation stats ──
        total_ev = len(evidence_list)
        ev_with_activation = total_ev if activated else 0
        ev_without = total_ev - ev_with_activation

        return CapabilityActivationShadowResult(
            document_id=document_id,
            activated_capabilities=activated,
            confidence=overall_conf,
            evidence_references=evidence_refs,
            boundary_validation_result=boundary,
            rejected_candidates=rejected,
            traces=traces,
            match_result=match_result.to_dict(),
            total_evidence=total_ev,
            evidence_with_activation=ev_with_activation,
            evidence_without_activation=ev_without,
        )

    def _build_traces(
        self,
        evidence_list: list[dict[str, Any]],
        activated_capabilities: list[dict[str, Any]],
        document_id: str,
        observation: DocumentObservation,
    ) -> list[CapabilityActivationTrace]:
        """
        Build CapabilityActivationTrace for each evidence span.

        Maps each evidence span to the capability that would handle it.
        The mapping is evidence-type-driven:
        - storage_condition → StorageDetection
        - safety_statement → SafetyDetection
        - anomaly_recovery → TroubleshootingDetection
        - sequential_step / condition_procedure / preparation_step → ProcedureDetection / SamplePrepDetection
        - test_method → QCDetection
        - comparison → QCDetection
        - component_spec → SamplePrepDetection
        """
        # Build capability lookup by evidence type
        # This uses the Capability's pattern_ids to determine which
        # evidence types they handle (NOT hardcoded capability_id)
        _cap_pattern_map = self._build_capability_pattern_map()

        traces: list[CapabilityActivationTrace] = []

        for ev in evidence_list:
            ev_type = ev.get("evidence_type", "unknown")
            ev_id = ev.get("span_id", "")

            # Find which activated capability handles this evidence type
            matched_cap = None
            for cap_dict in activated_capabilities:
                cap_id = cap_dict["capability_id"]
                cap_patterns = _cap_pattern_map.get(cap_id, [])
                # Check if evidence type maps to any of this capability's patterns
                if self._evidence_type_to_patterns(ev_type, cap_patterns):
                    matched_cap = cap_dict
                    break

            if matched_cap:
                reasoning = (
                    f"Evidence type '{ev_type}' (role={ev.get('problem_role', '')}) "
                    f"activates '{matched_cap['capability_name']}' "
                    f"(score={matched_cap['score']:.3f}) via matched patterns: "
                    f"{matched_cap.get('matched_patterns', [])}"
                )
                traces.append(CapabilityActivationTrace(
                    document_id=document_id,
                    evidence_id=ev_id,
                    capability_id=matched_cap["capability_id"],
                    evidence_type=ev_type,
                    problem_role=ev.get("problem_role", ""),
                    resolution_role=ev.get("resolution_role", ""),
                    boundary_decision="ACCEPT",
                    confidence=matched_cap["score"],
                    reasoning=reasoning,
                ))
            else:
                reasoning = (
                    f"Evidence type '{ev_type}' (role={ev.get('problem_role', '')}) "
                    f"did not match any activated capability. "
                    f"Activated capabilities: {[c['capability_id'] for c in activated_capabilities]}"
                )
                traces.append(CapabilityActivationTrace(
                    document_id=document_id,
                    evidence_id=ev_id,
                    capability_id="NONE",
                    evidence_type=ev_type,
                    problem_role=ev.get("problem_role", ""),
                    resolution_role=ev.get("resolution_role", ""),
                    boundary_decision="REJECT",
                    confidence=0.0,
                    reasoning=reasoning,
                ))

        return traces

    def _build_capability_pattern_map(self) -> dict[str, list[str]]:
        """Build capability_id → pattern_ids map from registry."""
        _map: dict[str, list[str]] = {}
        for cap in self._registry.list_all():
            _map[cap.id] = list(cap.pattern_ids) if cap.pattern_ids else []
        return _map

    @staticmethod
    def _evidence_type_to_patterns(
        ev_type: str, cap_patterns: list[str],
    ) -> bool:
        """
        Check if an evidence type is relevant to a capability's patterns.

        This maps evidence types to the structural pattern IDs that
        the CapabilityMatcher would detect. It's a structural mapping,
        NOT a keyword rule.

        Pattern ID → Evidence Type mapping:
        - PAT-STORAGE-CONDITIONS → storage_condition
        - PAT-SAFETY-WARNINGS → safety_statement
        - PAT-TROUBLESHOOT-QA → anomaly_recovery, condition_procedure
        - PAT-PROCEDURE-STEPS → sequential_step, condition_procedure
        - PAT-MATERIALS-LIST → preparation_step, component_spec
        - PAT-COMP-NAME-DENSITY, PAT-COMP-TABLE-COLLAPSE → component_spec
        - PAT-PARAMETER-LIST, PAT-TEMP-RANGE → test_method, comparison
        """
        ev_to_patterns = {
            "storage_condition": ["PAT-STORAGE-CONDITIONS", "PAT-STORAGE-LONG-TERM"],
            "safety_statement": ["PAT-SAFETY-WARNINGS", "PAT-WARNING-EXTRACT"],
            "anomaly_recovery": ["PAT-TROUBLESHOOT-QA"],
            "condition_procedure": ["PAT-TROUBLESHOOT-QA", "PAT-PROCEDURE-STEPS"],
            "sequential_step": ["PAT-PROCEDURE-STEPS", "PAT-STEP-COUNT"],
            "preparation_step": ["PAT-MATERIALS-LIST"],
            "test_method": ["PAT-PARAMETER-LIST", "PAT-TEMP-RANGE", "PAT-TIME-SPEC"],
            "comparison": ["PAT-PARAMETER-LIST"],
            "component_spec": [
                "PAT-COMP-TABLE-COLLAPSE", "PAT-COMP-NAME-DENSITY",
                "PAT-COMP-QUANTITY-PAIRING", "PAT-MATERIALS-LIST",
            ],
        }
        relevant = ev_to_patterns.get(ev_type, [])
        return any(p in cap_patterns for p in relevant)

    def activate_batch(
        self,
        shadow_evidence: dict[str, Any],
    ) -> list[CapabilityActivationShadowResult]:
        """
        Run shadow activation on all documents.

        Args:
            shadow_evidence: full shadow_evidence.json data with per_document list

        Returns:
            List of CapabilityActivationShadowResult, one per document.
        """
        results: list[CapabilityActivationShadowResult] = []
        for doc_data in shadow_evidence.get("per_document", []):
            doc_id = doc_data.get("document_id", "unknown")
            result = self.activate(
                evidence_data=doc_data,
                document_id=doc_id,
            )
            results.append(result)
        return results


# ═══════════════════════════════════════════════════════════════════════════
# Module-level helpers
# ═══════════════════════════════════════════════════════════════════════════


def load_shadow_evidence(path: str) -> dict[str, Any]:
    """Load shadow evidence JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_evidence_view(
    shadow_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Build an EvidenceView from shadow evidence data.

    This is the bridge between Evidence Runtime and Capability Runtime.
    The EvidenceView contains all evidence spans, organized by document,
    with their evidence types, roles, and confidence scores.
    """
    evidence_view: dict[str, Any] = {
        "total_documents": shadow_data.get("total_documents", 0),
        "per_document": {},
    }

    for doc_data in shadow_data.get("per_document", []):
        doc_id = doc_data.get("document_id", "unknown")
        evidence_view["per_document"][doc_id] = {
            "evidence_count": doc_data.get("evidence_accepted", 0),
            "evidence_types": doc_data.get("evidence_type_distribution", {}),
            "problem_roles": doc_data.get("problem_role_distribution", {}),
            "evidence_spans": [
                {
                    "span_id": ev.get("span_id", ""),
                    "evidence_type": ev.get("evidence_type", ""),
                    "problem_role": ev.get("problem_role", ""),
                    "resolution_role": ev.get("resolution_role", ""),
                    "confidence": ev.get("confidence", 0.0),
                }
                for ev in doc_data.get("evidence", [])
            ],
        }

    return evidence_view


__all__ = [
    "CapabilityRuntimeShadowAdapter",
    "CapabilityActivationShadowResult",
    "CapabilityActivationTrace",
    "EVIDENCE_TO_SIGNALS",
    "load_shadow_evidence",
    "build_evidence_view",
]