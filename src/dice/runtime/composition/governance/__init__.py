"""
Phase 6.0: Composite Governance — package init

STATUS: DESIGN_ONLY
"""

from .composite_governance import (
    ApprovalStatus,
    GovernanceDecision,
    CompositeApprovalRequest,
    CompositeGovernancePolicy,
    CompositeGovernance,
)

__all__ = [
    "ApprovalStatus",
    "GovernanceDecision",
    "CompositeApprovalRequest",
    "CompositeGovernancePolicy",
    "CompositeGovernance",
]