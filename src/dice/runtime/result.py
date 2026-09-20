"""
Unified CapabilityResult format.

All capability executions produce this standardized output, which MUST
contain not just the final fields but also WHY the judgment was made
(evidence), WHAT patterns were used, and HOW confident the result is.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from dice.models import SourceRef


@dataclass
class EvidenceItem:
    """
    A single piece of evidence collected during capability execution.

    Each evidence item links back to the specific content that triggered it,
    enabling full traceability from result → evidence → source document.
    """
    id: str = ""
    evidence_type: str = ""              # e.g. "component_identified", "quantity_extracted"
    description: str = ""                # human-readable: what was found
    source: Optional[SourceRef] = None   # where in the document
    content_snippet: str = ""            # the actual text that produced this evidence
    extraction: dict[str, Any] = field(default_factory=dict)  # what was extracted
    confidence: float = 0.0              # confidence for this specific piece of evidence
    match_type: str = ""                 # "exact", "fuzzy", "inferred"


@dataclass
class CapabilityResult:
    """
    Unified output format for ALL capability executions.

    Design constraint: MUST contain the "why" (evidence + patterns), not just
    the "what" (result fields).
    """
    # ── Identity ──
    capability_id: str = ""
    capability_name: str = ""
    implementation_version: str = ""

    # ── Result ──
    result: dict[str, Any] = field(default_factory=dict)
    # e.g. {"components": [...], "total_count": 9, "covered_count": 9}

    # ── Confidence ──
    confidence: float = 0.0              # overall confidence 0.0–1.0
    confidence_breakdown: dict[str, float] = field(default_factory=dict)
    # e.g. {"pattern_match": 0.9, "extraction_quality": 0.85, "completeness": 0.7}

    # ── Evidence (the "why") ──
    evidence: list[EvidenceItem] = field(default_factory=list)
    evidence_count: int = 0

    # ── Patterns used ──
    pattern_ids_used: list[str] = field(default_factory=list)
    pattern_match_details: dict[str, Any] = field(default_factory=dict)
    # e.g. {"PAT-COMP-TABLE-COLLAPSE": {"matched": True, "score": 0.95}}

    # ── Diagnosis ──
    diagnosis: str = ""                  # human-readable explanation of the judgment
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    # ── Metadata ──
    execution_time_ms: float = 0.0
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    document_id: str = ""
    slice_id: str = ""

    # ── Layer Analysis (Phase 3.0+) ──
    reasoning_layer: str = ""               # "L1_STRUCTURE" | "L2_SEMANTIC" | "L3_STRUCTURAL" | "UNCERTAIN"
    strategy_case: str = ""                 # "A" | "B" | "C"
    layer_contributions: dict[str, Any] = field(default_factory=dict)
    # e.g. {"L1": {"activated": True, "score": 0.8}, "L2": {...}, "L3": {...}}

    # ── Status ──
    is_success: bool = True

    def add_evidence(self, item: EvidenceItem) -> None:
        self.evidence.append(item)
        self.evidence_count = len(self.evidence)

    def add_warning(self, warning: str) -> None:
        self.warnings.append(warning)

    def add_error(self, error: str) -> None:
        self.errors.append(error)
        self.is_success = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "capability_name": self.capability_name,
            "implementation_version": self.implementation_version,
            "result": self.result,
            "confidence": self.confidence,
            "confidence_breakdown": self.confidence_breakdown,
            "evidence_count": self.evidence_count,
            "evidence": [
                {
                    "id": e.id,
                    "type": e.evidence_type,
                    "description": e.description,
                    "source": (
                        f"{e.source.source_document}/{e.source.source_slice}"
                        if e.source else "unknown"
                    ),
                    "extraction": e.extraction,
                    "confidence": e.confidence,
                }
                for e in self.evidence
            ],
            "pattern_ids_used": self.pattern_ids_used,
            "pattern_match_details": self.pattern_match_details,
            "diagnosis": self.diagnosis,
            "warnings": self.warnings,
            "errors": self.errors,
            "is_success": self.is_success,
            "reasoning_layer": self.reasoning_layer,
            "strategy_case": self.strategy_case,
            "layer_contributions": self.layer_contributions,
            "document_id": self.document_id,
            "slice_id": self.slice_id,
            "timestamp": self.timestamp,
        }
