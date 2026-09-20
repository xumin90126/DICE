"""
P7.2 Validation engine.

Creates ValidationTasks from Observations, applies Human Records, derives
ValidatedEvidence, and builds full audit chains. Enforces immutability and
the ACCEPT-only-evidence rule.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .validation_config import (
    TASK_PENDING, TASK_IN_REVIEW, TASK_RESOLVED,
    DECISION_ACCEPT, DECISION_REJECT, DECISION_NEED_REVIEW,
    EVIDENCE_VALIDATED, EVIDENCE_REJECTED, EVIDENCE_NEEDS_REVIEW,
    REVISION_ORIGINAL, REVISION_SUPERSEDED,
)
from .validation_models import (
    ValidationTask, ValidationRecord, ValidatedEvidence, ValidationAuditChain,
    _task_id, _record_id, _evidence_id,
)


# ── Task creation ────────────────────────────────────────────────────────────

def create_validation_task(observation: Dict[str, Any],
                           span_text_lookup: Dict[str, str],
                           visual_reference: Dict[str, Any],
                           created_time: str,
                           priority: int = 0,
                           dataset_tag: str = "HUMAN_VALIDATION") -> ValidationTask:
    """Derive a ValidationTask from a P7.1 StructureHypothesis (dict).

    observation: StructureHypothesis.to_dict()
    span_text_lookup: {span_id -> text} for candidate_content derivation (P4 span text)
    visual_reference: {png_path, bbox_highlight}
    """
    obs_id = observation["hypothesis_id"]
    doc_id = observation["document_id"]
    pno = observation["page_number"]
    span_ids = observation.get("span_ids", [])
    bbox = observation.get("geometry", {}).get("bbox", [0, 0, 0, 0])

    # candidate_content = derived view (text resolved from span_ids, NOT copied facts)
    texts = [span_text_lookup.get(sid, "") for sid in span_ids]
    candidate_content = {
        "text": " ".join(t for t in texts if t),
        "span_ids": span_ids,
        "bbox": bbox,
    }

    # system_reasoning = decision_trace summary (signals + decision + confidence)
    reasoning = []
    for step in observation.get("decision_trace", []):
        reasoning.append({
            "step": step.get("step"),
            "summary": {k: v for k, v in step.items() if k != "step"},
        })

    return ValidationTask(
        task_id=_task_id(doc_id, pno, obs_id),
        observation_id=obs_id,
        document_id=doc_id,
        page_number=pno,
        observation_type=observation["hypothesis_type"],
        candidate_content=candidate_content,
        visual_reference=visual_reference,
        confidence=observation.get("confidence", "UNKNOWN"),
        system_reasoning=reasoning,
        task_status=TASK_PENDING,
        created_time=created_time,
        priority=priority,
        dataset_tag=dataset_tag,
        provenance={
            "source": "P7.1 StructureHypothesis",
            "observation_confidence": observation.get("confidence"),
            "construction_method": observation.get("construction_method"),
        },
    )


# ── Record creation ──────────────────────────────────────────────────────────

def create_validation_record(task: ValidationTask,
                             decision: str,
                             reviewer_reason: str,
                             reviewer_id: str,
                             timestamp: str,
                             duration_seconds: float,
                             reviewer_notes: str = "",
                             dataset_tag: str = "HUMAN_VALIDATION",
                             supersedes_validation_id: Optional[str] = None) -> ValidationRecord:
    """Create an immutable ValidationRecord from REAL human interaction.

    duration_seconds MUST come from real interaction timing. No fixed/estimated/faked values.
    """
    if decision not in (DECISION_ACCEPT, DECISION_REJECT, DECISION_NEED_REVIEW):
        raise ValueError(f"Invalid decision: {decision}")
    if duration_seconds < 0:
        raise ValueError("duration_seconds must be non-negative (real interaction)")

    rec_id = _record_id(task.observation_id, reviewer_id, timestamp)
    revision = REVISION_SUPERSEDED if supersedes_validation_id else REVISION_ORIGINAL

    return ValidationRecord(
        validation_id=rec_id,
        task_id=task.task_id,
        observation_id=task.observation_id,
        reviewer_decision=decision,
        reviewer_reason=reviewer_reason,
        reviewer_notes=reviewer_notes,
        timestamp=timestamp,
        duration_seconds=duration_seconds,
        reviewer_id=reviewer_id,
        revision_status=revision,
        supersedes_validation_id=supersedes_validation_id,
        dataset_tag=dataset_tag,
        provenance={"source": "human_ui", "task_priority": task.priority},
    )


# ── Evidence derivation ──────────────────────────────────────────────────────

def derive_evidence(observation: Dict[str, Any],
                    task: ValidationTask,
                    record: ValidationRecord,
                    span_text_lookup: Dict[str, str]) -> Optional[ValidatedEvidence]:
    """Derive ValidatedEvidence ONLY if decision == ACCEPT.

    REJECT / NEED_REVIEW -> return None (no evidence produced).
    """
    if record.reviewer_decision != DECISION_ACCEPT:
        return None

    span_ids = observation.get("span_ids", [])
    texts = [span_text_lookup.get(sid, "") for sid in span_ids]
    obs_type = observation["hypothesis_type"]
    # evidence_type = strip "_CANDIDATE" suffix (HEADING_CANDIDATE -> HEADING)
    ev_type = obs_type.replace("_CANDIDATE", "") if obs_type.endswith("_CANDIDATE") else obs_type

    return ValidatedEvidence(
        evidence_id=_evidence_id(observation["hypothesis_id"], record.validation_id),
        observation_id=observation["hypothesis_id"],
        validation_id=record.validation_id,
        document_id=observation["document_id"],
        page_number=observation["page_number"],
        evidence_type=ev_type,
        validated_content={
            "text": " ".join(t for t in texts if t),
            "span_ids": span_ids,
            "bbox": observation.get("geometry", {}).get("bbox", [0, 0, 0, 0]),
        },
        source_geometry=observation.get("geometry", {}),
        validation_provenance={
            "reviewer_id": record.reviewer_id,
            "timestamp": record.timestamp,
            "reviewer_reason": record.reviewer_reason,
            "duration_seconds": record.duration_seconds,
        },
        status=EVIDENCE_VALIDATED,
    )


# ── Audit chain ──────────────────────────────────────────────────────────────

def build_audit_chain(evidence: ValidatedEvidence,
                      record: ValidationRecord,
                      task: ValidationTask,
                      observation: Dict[str, Any]) -> ValidationAuditChain:
    """Full reverse traceability: Evidence -> Record -> Task -> Observation -> Page."""
    return ValidationAuditChain(
        evidence_id=evidence.evidence_id,
        validation_id=record.validation_id,
        task_id=task.task_id,
        observation_id=observation["hypothesis_id"],
        observation_type=observation["hypothesis_type"],
        document_id=observation["document_id"],
        page_number=observation["page_number"],
        source_bbox=observation.get("geometry", {}).get("bbox", [0, 0, 0, 0]),
        source_span_ids=observation.get("span_ids", []),
        source_region_ids=observation.get("region_ids", []),
        reviewer_decision=record.reviewer_decision,
        reviewer_id=record.reviewer_id,
        timestamp=record.timestamp,
        observation_status=observation.get("status", "PROPOSED"),
        chain_complete=True,
    )


def verify_no_evidence_on_reject(record: ValidationRecord,
                                 evidence: Optional[ValidatedEvidence]) -> bool:
    """REJECT / NEED_REVIEW must NOT produce evidence."""
    if record.reviewer_decision in (DECISION_REJECT, DECISION_NEED_REVIEW):
        return evidence is None
    return True


def verify_observation_immutable(observation: Dict[str, Any]) -> bool:
    """Observation status must remain PROPOSED (never mutated by validation)."""
    return observation.get("status") == "PROPOSED"


def verify_no_duplicate_evidence(existing_evidence_ids: List[str],
                                 new_evidence: Optional[ValidatedEvidence]) -> bool:
    """Resubmit must not create duplicate Evidence for same observation+validation."""
    if new_evidence is None:
        return True
    return new_evidence.evidence_id not in existing_evidence_ids


def task_status_after_decision(decision: str) -> str:
    """Map Human decision to task terminal status."""
    return TASK_RESOLVED  # all decisions resolve the task
