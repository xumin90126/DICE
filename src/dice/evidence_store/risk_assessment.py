"""
Phase 6.10 Evolution Risk Assessment — pre-review risk triage.

Assigns a risk level (LOW / MEDIUM / HIGH) to evolution proposals
BEFORE they reach human review. This helps reviewers prioritise:
LOW → safe, rubber-stamp → HIGH → needs careful scrutiny.

DESIGN: READ-ONLY metadata layer. The assessor NEVER:
    - Modifies CapabilityRegistry
    - Modifies EvolutionProposal
    - Modifies Runtime or Matching
    - Changes proposal decisions

All output is advisory — the human reviewer always has the final say.

Usage:
    assessor = EvolutionRiskAssessor()
    assessment = assessor.assess(proposal, evidence, provenance)
    # assessment.risk_level → "LOW" | "MEDIUM" | "HIGH"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from dice.evidence_store.models import EvolutionProposal, EvidenceSummary
from dice.evidence_store.provenance import ProvenanceResult, PatternProvenance


# ═══════════════════════════════════════════════════════════════════════════
# EvolutionRiskAssessment — output dataclass
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class EvolutionRiskAssessment:
    """
    Risk triage result for a single evolution proposal.

    Fields:
        risk_level      — "LOW" | "MEDIUM" | "HIGH"
        reasons          — human-readable reasons for the assigned level
        affected_scope   — what this proposal touches (capability names,
                           vocabulary domains, registry paths)
        rollback_required — True if the proposal could require rollback
                            procedures after implementation

    LOW  = safe, well-understood extension of existing capability
    MEDIUM = vocabulary expansion, detection improvement, moderate change
    HIGH = new capability, registry modification, unknown provenance
    """

    risk_level: str = "MEDIUM"
    reasons: list[str] = field(default_factory=list)
    affected_scope: list[str] = field(default_factory=list)
    rollback_required: bool = False


# ═══════════════════════════════════════════════════════════════════════════
# EvolutionRiskAssessor
# ═══════════════════════════════════════════════════════════════════════════


class EvolutionRiskAssessor:
    """
    Assigns a risk level to evolution proposals based on three axes:

    1. recommended_action (what kind of change)
    2. evidence metrics (how much coverage exists)
    3. pattern provenance (where the signal came from)

    Risk rules (first match wins — ordered HIGH → MEDIUM → LOW):

    HIGH:
        - recommended_action == "add_new_capability_candidate"
          → truly new capability; registry may change
        - provenance == UNKNOWN
          → cannot verify origin; need extra scrutiny

    MEDIUM:
        - recommended_action == "extend_vocabulary"
          → vocabulary expansion changes domain understanding
        - recommended_action == "improve_detector"
          → detector logic changes affect downstream matching

    LOW:
        - recommended_action == "extend_existing_capability_pattern"
          → extending an existing pattern; safe, well-bounded
        - existing capability already covers this domain
          → evidence_summary.existing_capability_overlap > 0
        - provenance is PRODUCTION or CANDIDATE
          → known origin, legitimate signal

    Usage:
        assessor = EvolutionRiskAssessor()
        assessment = assessor.assess(proposal, evidence, provenance)
    """

    # ── Action → risk level mapping ──
    _ACTION_RISK: dict[str, str] = {
        "add_new_capability_candidate": "HIGH",
        "extend_vocabulary": "MEDIUM",
        "improve_detector": "MEDIUM",
        "extend_existing_capability_pattern": "LOW",
    }

    # ── Provenance flags that escalate risk ──
    _HIGH_RISK_PROVENANCES = frozenset({
        PatternProvenance.UNKNOWN,
    })

    _LOW_RISK_PROVENANCES = frozenset({
        PatternProvenance.PRODUCTION,
        PatternProvenance.CANDIDATE,
    })

    def assess(
        self,
        proposal: EvolutionProposal,
        evidence: EvidenceSummary,
        provenance: ProvenanceResult | PatternProvenance | str,
    ) -> EvolutionRiskAssessment:
        """
        Assess the risk level of an evolution proposal.

        Args:
            proposal:   EvolutionProposal from ProposalGenerator
            evidence:   EvidenceSummary with quantitative metrics
            provenance: PatternProvenance enum, ProvenanceResult, or string
                        (e.g. "production", "discrimination-test")

        Returns:
            EvolutionRiskAssessment with risk_level, reasons, scope, rollback flag.
        """
        # ── Normalise provenance ──
        prov: Optional[PatternProvenance] = self._normalise_provenance(provenance)

        reasons: list[str] = []
        scope: list[str] = []
        rollback = False

        action = proposal.recommended_action or ""

        # ── HIGH-risk checks ──
        if action == "add_new_capability_candidate":
            reasons.append(
                "New capability proposal: may require CapabilityRegistry "
                "modification — no existing capability covers this pattern."
            )
            scope.append("CapabilityRegistry (new capability registration)")
            rollback = True
            return EvolutionRiskAssessment(
                risk_level="HIGH",
                reasons=reasons,
                affected_scope=scope,
                rollback_required=rollback,
            )

        if prov is not None and prov in self._HIGH_RISK_PROVENANCES:
            reasons.append(
                f"Unknown provenance ({prov.value}): cannot verify pattern "
                f"origin — elevated risk of false evolution."
            )
            scope.append("provenance verification")
            # Unknown provenance + non-trivial action stays HIGH
            if action in ("extend_vocabulary", "improve_detector", "add_new_capability_candidate"):
                return EvolutionRiskAssessment(
                    risk_level="HIGH",
                    reasons=reasons,
                    affected_scope=scope,
                    rollback_required=rollback,
                )

        # ── MEDIUM-risk checks ──
        if action == "extend_vocabulary":
            reasons.append(
                "Vocabulary expansion: modifies domain term coverage — "
                "changes affect cross-document recognition."
            )
            scope.append("vocabulary domain terms")
            return EvolutionRiskAssessment(
                risk_level="MEDIUM",
                reasons=reasons,
                affected_scope=scope,
                rollback_required=rollback,
            )

        if action == "improve_detector":
            reasons.append(
                "Detector improvement: modifies detection logic — "
                "changes affect downstream matching pipeline."
            )
            scope.append("detector logic")
            # Provenance UNKNOWN with improve_detector → escalate
            if prov is not None and prov in self._HIGH_RISK_PROVENANCES:
                return EvolutionRiskAssessment(
                    risk_level="HIGH",
                    reasons=reasons + [
                        f"Coupled with unknown provenance ({prov.value}) — "
                        f"detector changes from unverified source."
                    ],
                    affected_scope=scope,
                    rollback_required=True,
                )
            return EvolutionRiskAssessment(
                risk_level="MEDIUM",
                reasons=reasons,
                affected_scope=scope,
                rollback_required=rollback,
            )

        # ── LOW-risk check ──
        if action == "extend_existing_capability_pattern":
            reasons.append(
                "Pattern extension: well-bounded change to an existing "
                "capability — low blast radius."
            )
            # Check existing capability overlap
            overlap = getattr(evidence, "existing_capability_overlap", 0)
            if overlap > 0:
                reasons.append(
                    f"Existing capability overlap = {overlap}: pattern "
                    f"already covered by known capability."
                )
                scope.append(f"existing capability (overlap={overlap})")
            scope.append("capability pattern extension")

            # Provenance confidence boost
            if prov is not None and prov in self._LOW_RISK_PROVENANCES:
                reasons.append(
                    f"Known provenance ({prov.value}): signal from verified source."
                )

            return EvolutionRiskAssessment(
                risk_level="LOW",
                reasons=reasons,
                affected_scope=scope,
                rollback_required=False,
            )

        # ── Fallback: unrecognised action ──
        reasons.append(f"Unrecognised action '{action}' — treating as MEDIUM.")
        return EvolutionRiskAssessment(
            risk_level="MEDIUM",
            reasons=reasons,
            affected_scope=scope,
            rollback_required=rollback,
        )

    def assess_batch(
        self,
        proposals: list[EvolutionProposal],
        evidence_map: dict[str, EvidenceSummary],
        provenance_map: dict[str, ProvenanceResult | PatternProvenance | str],
    ) -> list[EvolutionRiskAssessment]:
        """
        Batch-assess multiple proposals.

        Args:
            proposals:      List of EvolutionProposals
            evidence_map:   {proposal_id → EvidenceSummary}
            provenance_map: {proposal_id → ProvenanceResult|PatternProvenance|str}

        Returns:
            List of EvolutionRiskAssessment, one per proposal.
        """
        results: list[EvolutionRiskAssessment] = []
        for p in proposals:
            evidence = evidence_map.get(
                p.proposal_id, EvidenceSummary()
            )
            prov = provenance_map.get(
                p.proposal_id, PatternProvenance.UNKNOWN
            )
            results.append(self.assess(p, evidence, prov))
        return results

    # ═══════════════════════════════════════════════════════════════════
    # Helpers
    # ═══════════════════════════════════════════════════════════════════

    def _normalise_provenance(
        self, value: ProvenanceResult | PatternProvenance | str
    ) -> Optional[PatternProvenance]:
        """Normalise various provenance representations to PatternProvenance enum."""
        if isinstance(value, PatternProvenance):
            return value
        if isinstance(value, ProvenanceResult):
            return value.provenance
        if isinstance(value, str):
            try:
                return PatternProvenance(value)
            except ValueError:
                return None
        return None
