"""
Phase 6 Evidence Store Package.

Independent from dice/evidence.py (execution-level evidence).
Records matching pipeline outputs for Evolution-driven analysis.

Modules:
    models             — MatchRecord, EvolutionCandidate, EvolutionDecision, EvidenceSummary, EvolutionProposal
    store              — MatchEvidenceStore (CRUD + persistence)
    observer           — EvolutionObserver (gap detection)
    validator          — EvolutionValidator (validation gate)
    proposal_generator — ProposalGenerator (evolution proposal generation)
"""

from dice.evidence_store.models import (
    MatchRecord,
    EvolutionCandidate,
    EvolutionDecision,
    EvolutionProposal,
    EvidenceSummary,
)
from dice.evidence_store.store import MatchEvidenceStore
from dice.evidence_store.observer import EvolutionObserver, analyze_store
from dice.evidence_store.validator import (
    EvolutionValidator,
    CandidateConsolidator,
    validate_candidates,
)
from dice.evidence_store.proposal_generator import (
    ProposalGenerator,
    generate_proposals,
)
from dice.evidence_store.review_artifact import (
    ReviewArtifactGenerator,
    generate_review_artifacts,
)

__all__ = [
    "MatchRecord",
    "EvolutionCandidate",
    "EvolutionDecision",
    "EvolutionProposal",
    "EvidenceSummary",
    "MatchEvidenceStore",
    "EvolutionObserver",
    "analyze_store",
    "EvolutionValidator",
    "CandidateConsolidator",
    "validate_candidates",
    "ProposalGenerator",
    "generate_proposals",
    "ReviewArtifactGenerator",
    "generate_review_artifacts",
]
