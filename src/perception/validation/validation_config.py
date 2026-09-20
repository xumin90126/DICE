"""
P7.2 Human Validation Infrastructure — configuration & vocabulary.

Validation is a GOVERNANCE layer, not a perception layer. It consumes P7.1
StructureHypothesis (Observation) and produces Validated Evidence via real
Human decision. No auto-ACCEPT, no LLM, no threshold auto-tuning.
"""
from __future__ import annotations

# ── Task status ──────────────────────────────────────────────────────────────
TASK_PENDING = "PENDING_HUMAN_REVIEW"
TASK_IN_REVIEW = "IN_REVIEW"
TASK_RESOLVED = "RESOLVED"
ALL_TASK_STATUSES = [TASK_PENDING, TASK_IN_REVIEW, TASK_RESOLVED]

# ── Human decisions ──────────────────────────────────────────────────────────
DECISION_ACCEPT = "ACCEPT"
DECISION_REJECT = "REJECT"
DECISION_NEED_REVIEW = "NEED_REVIEW"
ALL_DECISIONS = [DECISION_ACCEPT, DECISION_REJECT, DECISION_NEED_REVIEW]

# Only ACCEPT derives Evidence
EVIDENCE_DERIVING_DECISION = DECISION_ACCEPT

# ── Evidence status ──────────────────────────────────────────────────────────
EVIDENCE_VALIDATED = "VALIDATED"
EVIDENCE_REJECTED = "REJECTED_BLOCKED"        # observation kept, no evidence
EVIDENCE_NEEDS_REVIEW = "NEEDS_REVIEW_BLOCKED"

# ── Record revision (immutable corrections) ──────────────────────────────────
REVISION_ORIGINAL = "ORIGINAL"
REVISION_SUPERSEDED = "SUPERSEDED"

# ── Dataset provenance tag ───────────────────────────────────────────────────
DATASET_TEST = "TEST"            # synthetic fixture, never in official dataset
DATASET_HUMAN_VALIDATION = "HUMAN_VALIDATION"  # real human interaction
