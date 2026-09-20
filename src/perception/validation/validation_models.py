"""
P7.2 Validation data models.

Three strictly separated objects + one derived:
  A. Observation  = P7.1 StructureHypothesis (referenced, NOT copied; immutable PROPOSED)
  B. ValidationTask   = derived review unit (references observation_id)
  C. ValidationRecord = immutable Human verdict
  D. ValidatedEvidence = DERIVED (only from Observation + ACCEPT + Record)

Observation != Validated Structure != Evidence.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from .validation_config import (
    TASK_PENDING, DECISION_ACCEPT, DECISION_REJECT, DECISION_NEED_REVIEW,
    EVIDENCE_VALIDATED, REVISION_ORIGINAL,
)


def _task_id(document_id: str, page_number: int, observation_id: str) -> str:
    raw = f"{document_id}|p{page_number}|{observation_id}|validation_task"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def _record_id(observation_id: str, reviewer_id: str, timestamp: str) -> str:
    raw = f"{observation_id}|{reviewer_id}|{timestamp}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def _evidence_id(observation_id: str, validation_id: str) -> str:
    raw = f"{observation_id}|{validation_id}|validated_evidence"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


@dataclass
class ValidationTask:
    """Derived review unit. References observation_id; does NOT copy Observation facts."""

    task_id: str
    observation_id: str                 # = StructureHypothesis.hypothesis_id
    document_id: str
    page_number: int
    observation_type: str               # HEADING_CANDIDATE etc.
    candidate_content: Dict[str, Any]   # derived view: {text, span_ids, bbox} from P4
    visual_reference: Dict[str, Any]    # {png_path, bbox_highlight}
    confidence: str                     # from Observation
    system_reasoning: List[Dict[str, Any]]  # decision_trace summary
    task_status: str = TASK_PENDING
    created_time: str = ""
    priority: int = 0
    dataset_tag: str = "HUMAN_VALIDATION"
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationRecord:
    """Immutable Human verdict. Created once; corrections create a NEW record."""

    validation_id: str
    task_id: str
    observation_id: str
    reviewer_decision: str             # ACCEPT / REJECT / NEED_REVIEW
    reviewer_reason: str
    reviewer_notes: str
    timestamp: str
    duration_seconds: float            # REAL human interaction time (not faked)
    reviewer_id: str
    revision_status: str = REVISION_ORIGINAL
    supersedes_validation_id: Optional[str] = None
    dataset_tag: str = "HUMAN_VALIDATION"
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ValidatedEvidence:
    """DERIVED object. Only exists when Observation + Human ACCEPT + Record align.
    References observation_id + validation_id; does NOT become a free-standing
    knowledge object divorced from provenance."""

    evidence_id: str
    observation_id: str
    validation_id: str
    document_id: str
    page_number: int
    evidence_type: str                 # derived from observation_type (CANDIDATE stripped)
    validated_content: Dict[str, Any]  # text + bbox (same source as candidate_content)
    source_geometry: Dict[str, Any]    # from Observation.geometry
    validation_provenance: Dict[str, Any]  # {reviewer_id, timestamp, reason}
    status: str = EVIDENCE_VALIDATED
    coord_origin: str = "PDF_TOP_LEFT"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationAuditChain:
    """Full reverse-traceability: Evidence -> Record -> Task -> Observation -> P7.1 -> Page."""

    evidence_id: str
    validation_id: str
    task_id: str
    observation_id: str
    observation_type: str
    document_id: str
    page_number: int
    source_bbox: List[float]
    source_span_ids: List[str]
    source_region_ids: List[str]
    reviewer_decision: str
    reviewer_id: str
    timestamp: str
    observation_status: str            # must stay PROPOSED
    chain_complete: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
