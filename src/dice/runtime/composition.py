"""
Composition Engine — Phase 5.3.

Combines multiple Capabilities into composition proposals when a single
Capability is insufficient for a DocumentObservation. Acts as a
higher-order matching layer: given a ranked candidate list, it explores
whether combining the top-N candidates yields better coverage than
any single capability alone.

ARCHITECTURE:
    MatchResult (from CapabilityMatcher)
            │
            ▼
    CompositionEngine.compose()
            │
            ├── 1. Enumerate viable subsets (size 2..max_size)
            ├── 2. Score each CompositionCandidate
            ├── 3. Gate validation (5 gates)
            ├── 4. Produce CompositionProposal(s)
            └── 5. Return ranked list

HARD BOUNDARIES (Phase 5.3):
    1. CompositionEngine does NOT modify Registry
    2. CompositionEngine does NOT create Capability
    3. Only produces Candidate + Proposal (data objects)
    4. Proposal MUST pass Validation Gate
    5. Preserves Experience → Evidence → Proposal trace chain
    6. ZERO Agent / auto-modification
"""

from __future__ import annotations

import hashlib
import itertools
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from dice.graph.nodes import DocumentObservation, MatchCandidate
from dice.registry import CapabilityRegistry


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ═══════════════════════════════════════════════════════════════════════════
# Data Schemas
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class CompositionCandidate:
    """
    A proposed combination of Capabilities for handling an Observation.

    This is a DATA OBJECT — it proposes a combination but does NOT
    register anything in the Registry. It is the input to the
    Validation Gate.

    Attributes:
        id: unique composition candidate ID
        capability_ids: ordered list of capability IDs in the composition
        composition_score: composite quality score (0.0–1.0)
        coverage_score: fraction of observation signals covered by union
        complementarity_score: how complementary the caps are (0=redundant, 1=orthogonal)
        novelty_score: improvement over best single-cap score
        individual_scores: per-capability match scores from MatchResult
        coverage_map: signal_type → list of covering capability_ids
        uncovered_signals: signal_types NOT covered by any cap
        redundancy_ratio: fraction of signals covered by >1 cap
        reasoning: human-readable composition rationale
    """

    id: str = ""
    capability_ids: list[str] = field(default_factory=list)
    composition_score: float = 0.0
    coverage_score: float = 0.0
    complementarity_score: float = 0.0
    novelty_score: float = 0.0
    individual_scores: dict[str, float] = field(default_factory=dict)
    coverage_map: dict[str, list[str]] = field(default_factory=dict)
    uncovered_signals: list[str] = field(default_factory=list)
    redundancy_ratio: float = 0.0
    reasoning: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "capability_ids": self.capability_ids,
            "composition_score": round(self.composition_score, 4),
            "coverage_score": round(self.coverage_score, 4),
            "complementarity_score": round(self.complementarity_score, 4),
            "novelty_score": round(self.novelty_score, 4),
            "individual_scores": {
                k: round(v, 4) for k, v in self.individual_scores.items()
            },
            "coverage_map": self.coverage_map,
            "uncovered_signals": self.uncovered_signals,
            "redundancy_ratio": round(self.redundancy_ratio, 4),
            "reasoning": self.reasoning,
        }


@dataclass
class CompositionProposal:
    """
    A validated composition proposal — output of the Composition Engine.

    The proposal carries validation gate results and evidence traceability.
    It is a PROPOSAL: it does NOT auto-register or auto-execute anything.

    The Experience → Evidence → Proposal chain:
        - evidence_support: references to Evidence nodes that justify this composition
        - source_match_id: back-link to the MatchResult that spawned this analysis
        - signature: cryptographic hash ensuring proposal integrity
    """

    id: str = ""
    candidate: Optional[CompositionCandidate] = None

    # ── Evidence chain ──
    evidence_support: list[str] = field(default_factory=list)
    source_match_id: str = ""
    source_document_id: str = ""

    # ── Validation gates ──
    validation_gates: dict[str, dict[str, Any]] = field(default_factory=dict)
    gates_passed: int = 0
    total_gates: int = 5
    is_validated: bool = False

    # ── Identity ──
    confidence: float = 0.0
    status: str = "pending_review"  # pending_review | validated | rejected
    signature: str = ""
    created_at: str = field(default_factory=_now)
    reviewed_at: str = ""
    review_notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "candidate": self.candidate.to_dict() if self.candidate else None,
            "evidence_support": self.evidence_support,
            "source_match_id": self.source_match_id,
            "source_document_id": self.source_document_id,
            "validation_gates": self.validation_gates,
            "gates_passed": self.gates_passed,
            "total_gates": self.total_gates,
            "is_validated": self.is_validated,
            "confidence": round(self.confidence, 4),
            "status": self.status,
            "signature": self.signature,
            "created_at": self.created_at,
        }


# ═══════════════════════════════════════════════════════════════════════════
# Composition Engine
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class CompositionConfig:
    """
    Configuration for the Composition Engine.

    All thresholds are tunable but have sensible defaults derived
    from Phase 5.0–5.2 empirical data.
    """

    # Candidate enumeration
    min_individual_score: float = 0.25    # caps below this are excluded from composition
    max_composition_size: int = 3         # max caps per composition
    max_combinations: int = 20            # max combinations to evaluate (prunes search)

    # Scoring weights (must sum to 1.0)
    weight_coverage: float = 0.35
    weight_complementarity: float = 0.30
    weight_novelty: float = 0.25
    weight_confidence: float = 0.10

    # Validation gate thresholds
    gate_min_coverage: float = 0.50          # Gate 1: coverage must exceed this
    gate_min_complementarity: float = 0.30   # Gate 2: complementarity floor
    gate_min_novelty: float = 0.05           # Gate 3: must improve over single-cap
    gate_min_confidence: float = 0.35        # Gate 4: overall proposal confidence
    gate_min_component_score: float = 0.25   # Gate 5: each cap indiv. score floor


DEFAULT_COMPOSITION_CONFIG = CompositionConfig()


class CompositionEngine:
    """
    Composition Engine — discovers viable multi-capability compositions.

    Reads from:
        - CapabilityRegistry (to get capability metadata)
        - MatchResult (ranked single-cap candidates)
        - DocumentObservation (signal structure)

    Produces:
        - CompositionCandidate → CompositionProposal (ranked list)

    Does NOT:
        - Modify Registry
        - Create Capability entries
        - Auto-execute anything
    """

    def __init__(
        self,
        registry: CapabilityRegistry,
        config: Optional[CompositionConfig] = None,
    ):
        self.registry = registry
        self.config = config or DEFAULT_COMPOSITION_CONFIG

    # ──────────────────────── Public API ────────────────────────

    def compose(
        self,
        observation: DocumentObservation,
        match_result: Any,
    ) -> list[CompositionProposal]:
        """
        Generate composition proposals from a matching result.

        Args:
            observation: structural observation of the content
            match_result: MatchResult from CapabilityMatcher.match()

        Returns:
            Ranked list of CompositionProposal (may be empty if no
            composition passes all gates)
        """
        # Step 0: Extract candidate scores from match result
        candidate_scores = self._extract_candidate_scores(match_result)
        if len(candidate_scores) < 2:
            return []  # need ≥2 viable caps to compose

        # Step 1: Determine observation signals
        all_signals = self._extract_observation_signals(observation)

        # Step 2: Build per-cap signal coverage
        cap_signals = self._build_capability_signal_map(candidate_scores.keys())

        # Step 3: Enumerate viable compositions
        candidates = self._enumerate_candidates(
            candidate_scores, cap_signals, all_signals
        )

        # Step 4: Score each candidate
        best_single_score = max(candidate_scores.values()) if candidate_scores else 0.0
        best_single_cap = max(candidate_scores, key=candidate_scores.get) if candidate_scores else ""
        best_single_coverage = self._single_cap_coverage(
            best_single_cap, cap_signals, all_signals
        )
        for c in candidates:
            self._score_candidate(c, candidate_scores, cap_signals, all_signals,
                                  best_single_coverage)

        # Step 5: Sort by composition_score desc
        candidates.sort(key=lambda c: c.composition_score, reverse=True)

        # Step 6: Gate validation → Proposal
        proposals = []
        for i, c in enumerate(candidates):
            proposal = self._validate_and_create_proposal(
                c, i, observation, candidate_scores
            )
            proposals.append(proposal)

        return proposals

    # ──────────────────────── Step 0: Extract ────────────────────────

    def _extract_candidate_scores(self, match_result: Any) -> dict[str, float]:
        """Extract {capability_id → score} from MatchResult, filtering by threshold."""
        scores = {}
        if not hasattr(match_result, "candidates"):
            return scores

        for cand in match_result.candidates:
            if not hasattr(cand, "capability_id") or not hasattr(cand, "score"):
                continue
            if cand.score >= self.config.min_individual_score:
                scores[cand.capability_id] = cand.score

        return scores

    # ──────────────────────── Step 1: Signals ────────────────────────

    def _extract_observation_signals(
        self, observation: DocumentObservation
    ) -> list[str]:
        """
        Extract signal identifiers from the observation.

        Phase 5.3 V3: PURE pattern_ids only. The signal space must align
        1:1 with capability.pattern_ids so coverage denominators match.
        elem:* signals are excluded because they dilute the denominator
        (Observation has them, Capability signal map doesn't in V2),
        causing false-low coverage scores.
        """
        signals = []

        # Pattern IDs only — common language between observation & capability
        for pid in observation.detected_pattern_ids:
            signals.append(pid)

        return signals

    # ──────────────────────── Step 2: Capability ↔ Signal mapping ────

    def _build_capability_signal_map(
        self, capability_ids: set[str]
    ) -> dict[str, set[str]]:
        """
        Build {capability_id → set of signal keys} using pattern_ids.

        Phase 5.3 V3: PURE pattern_ids only. Direct 1:1 mapping from
        capability.pattern_ids to signal keys. Each pattern_id IS a signal
        key. This ensures coverage calculation aligns with the matching layer.

        elem:* signals removed to keep denominator consistent with
        _extract_observation_signals (which also only produces pattern_ids).
        """
        cap_signals: dict[str, set[str]] = {}

        for cap_id in capability_ids:
            cap = self.registry.get(cap_id)
            if cap is None:
                continue

            signals = set()

            # Pattern coverage: each pattern_id IS a signal key
            for pid in cap.pattern_ids:
                signals.add(pid)

            cap_signals[cap_id] = signals

        return cap_signals

    # ──────────────────────── Step 3: Enumeration ────────────────────

    def _enumerate_candidates(
        self,
        candidate_scores: dict[str, float],
        cap_signals: dict[str, set[str]],
        all_signals: list[str],
    ) -> list[CompositionCandidate]:
        """
        Generate all viable subsets of capabilities (size 2..max_composition_size).

        Prunes aggressively via max_combinations to avoid combinatorial
        explosion with 21+ capabilities.
        """
        sorted_caps = sorted(
            candidate_scores.keys(),
            key=lambda cid: candidate_scores[cid],
            reverse=True,
        )

        # Limit to top-scoring candidates for enumeration
        top_n = min(12, len(sorted_caps))
        pool = sorted_caps[:top_n]

        candidates: list[CompositionCandidate] = []
        counter = 0

        for size in range(2, self.config.max_composition_size + 1):
            for combo in itertools.combinations(pool, size):
                if counter >= self.config.max_combinations:
                    break

                cap_ids = list(combo)

                # Quick pre-check: does this combo cover ANYTHING the best
                # single cap doesn't already cover alone?
                best_cap = sorted_caps[0] if sorted_caps else ""
                best_signals = cap_signals.get(best_cap, set()) & set(all_signals)
                combo_signals = set()
                for cid in cap_ids:
                    combo_signals |= (cap_signals.get(cid, set()) & set(all_signals))
                if combo_signals == best_signals and len(cap_ids) > 1:
                    continue  # no additional coverage → skip

                cand = CompositionCandidate(
                    id=f"COMP-CAND-{counter + 1:03d}",
                    capability_ids=cap_ids,
                )
                candidates.append(cand)
                counter += 1

        return candidates

    # ──────────────────────── Step 4: Scoring ────────────────────────

    def _score_candidate(
        self,
        candidate: CompositionCandidate,
        candidate_scores: dict[str, float],
        cap_signals: dict[str, set[str]],
        all_signals: list[str],
        best_single_coverage: float,
    ) -> None:
        """
        Compute the four scoring dimensions for a CompositionCandidate.

        Dimensions:
            1. Coverage: fraction of total signals covered by union of caps
            2. Complementarity: 1 - redundancy (how orthogonal are the caps)
            3. Novelty: coverage improvement over best single cap
            4. Confidence: mean of individual cap scores
        """
        all_signal_set = set(all_signals)
        if not all_signal_set:
            candidate.composition_score = 0.0
            return

        # ── Union of signals covered by all caps ──
        union_signals: set[str] = set()
        per_cap_coverage: dict[str, set[str]] = {}

        for cap_id in candidate.capability_ids:
            covered = (cap_signals.get(cap_id, set()) & all_signal_set)
            per_cap_coverage[cap_id] = covered
            union_signals |= covered

        # ── Coverage Map: signal → list of covering caps ──
        coverage_map: dict[str, list[str]] = {}
        for sig in union_signals:
            coverage_map[sig] = [
                cid for cid in candidate.capability_ids
                if sig in per_cap_coverage[cid]
            ]

        # 1. Coverage Score
        coverage = len(union_signals) / len(all_signal_set)
        candidate.coverage_score = coverage

        # 2. Complementarity Score
        # overlap = sum of signals covered by >1 cap
        # pure complementarity = 1 - (overlap_signals / union_signals)
        overlap_count = sum(
            1 for caps in coverage_map.values() if len(caps) > 1
        )
        if len(union_signals) > 0:
            complementarity = 1.0 - (overlap_count / len(union_signals))
            candidate.redundancy_ratio = overlap_count / len(union_signals)
        else:
            complementarity = 0.0
            candidate.redundancy_ratio = 0.0
        candidate.complementarity_score = complementarity

        # 3. Novelty Score: coverage improvement over best single cap.
        # Formula: novel_coverage = max(0, composition_coverage - best_single_coverage)
        # + structure bonus for complementarity
        if best_single_coverage > 0:
            coverage_delta = max(0.0, coverage - best_single_coverage)
            # Scale delta: a 10% coverage improvement is significant
            novelty = coverage_delta * 2.0 + complementarity * 0.15
        else:
            novelty = coverage + complementarity * 0.15
        candidate.novelty_score = min(1.0, novelty)

        # 4. Confidence: mean of individual scores
        scores = [candidate_scores.get(cid, 0.0) for cid in candidate.capability_ids]
        mean_confidence = sum(scores) / len(scores) if scores else 0.0

        # ── Composite Score ──
        cfg = self.config
        candidate.composition_score = (
            cfg.weight_coverage * coverage
            + cfg.weight_complementarity * complementarity
            + cfg.weight_novelty * candidate.novelty_score
            + cfg.weight_confidence * mean_confidence
        )
        candidate.composition_score = min(1.0, candidate.composition_score)

        # ── Individual scores ──
        candidate.individual_scores = {
            cid: candidate_scores.get(cid, 0.0)
            for cid in candidate.capability_ids
        }

        # ── Coverage map ──
        candidate.coverage_map = coverage_map

        # ── Uncovered signals ──
        candidate.uncovered_signals = sorted(all_signal_set - union_signals)

        # ── Reasoning ──
        candidate.reasoning = (
            f"Composition of {len(candidate.capability_ids)} capabilities "
            f"({', '.join(candidate.capability_ids)}) achieves "
            f"{coverage:.1%} coverage (+{candidate.novelty_score:.2f} novelty) "
            f"with {complementarity:.1%} complementarity. "
            f"{len(candidate.uncovered_signals)}/{len(all_signal_set)} signals "
            f"remain uncovered."
        )

    # ──────────────────────── Step 5: Validation Gate ────────────────

    def _validate_and_create_proposal(
        self,
        candidate: CompositionCandidate,
        index: int,
        observation: DocumentObservation,
        candidate_scores: dict[str, float],
    ) -> CompositionProposal:
        """
        Run the 5-gate validation and produce a CompositionProposal.

        Gates:
            1. Coverage Gate: coverage > gate_min_coverage
            2. Complementarity Gate: complementarity > gate_min_complementarity
            3. Novelty Gate: novelty > gate_min_novelty
            4. Confidence Gate: composition_score > gate_min_confidence
            5. Component Score Gate: each cap score > gate_min_component_score
        """
        cfg = self.config
        gates: dict[str, dict[str, Any]] = {}
        passed = 0

        # Gate 1: Coverage
        ok = candidate.coverage_score >= cfg.gate_min_coverage
        gates["G1_coverage"] = {
            "passed": ok,
            "threshold": cfg.gate_min_coverage,
            "actual": round(candidate.coverage_score, 4),
            "reason": f"Coverage {candidate.coverage_score:.1%} >= {cfg.gate_min_coverage:.1%}" if ok
                       else f"Coverage {candidate.coverage_score:.1%} < {cfg.gate_min_coverage:.1%}",
        }
        if ok:
            passed += 1

        # Gate 2: Complementarity
        ok = candidate.complementarity_score >= cfg.gate_min_complementarity
        gates["G2_complementarity"] = {
            "passed": ok,
            "threshold": cfg.gate_min_complementarity,
            "actual": round(candidate.complementarity_score, 4),
            "reason": f"Complementarity {candidate.complementarity_score:.1%} >= {cfg.gate_min_complementarity:.1%}" if ok
                       else f"Complementarity {candidate.complementarity_score:.1%} < {cfg.gate_min_complementarity:.1%} — caps too redundant",
        }
        if ok:
            passed += 1

        # Gate 3: Novelty
        ok = candidate.novelty_score >= cfg.gate_min_novelty
        gates["G3_novelty"] = {
            "passed": ok,
            "threshold": cfg.gate_min_novelty,
            "actual": round(candidate.novelty_score, 4),
            "reason": f"Novelty {candidate.novelty_score:.3f} >= {cfg.gate_min_novelty:.3f}" if ok
                       else f"Novelty {candidate.novelty_score:.3f} < {cfg.gate_min_novelty:.3f} — single cap sufficient",
        }
        if ok:
            passed += 1

        # Gate 4: Overall Confidence
        ok = candidate.composition_score >= cfg.gate_min_confidence
        gates["G4_confidence"] = {
            "passed": ok,
            "threshold": cfg.gate_min_confidence,
            "actual": round(candidate.composition_score, 4),
            "reason": f"Composition score {candidate.composition_score:.3f} >= {cfg.gate_min_confidence:.3f}" if ok
                       else f"Composition score {candidate.composition_score:.3f} < {cfg.gate_min_confidence:.3f}",
        }
        if ok:
            passed += 1

        # Gate 5: Individual Component Scores
        all_ok = True
        failures = []
        for cid in candidate.capability_ids:
            s = candidate_scores.get(cid, 0.0)
            if s < cfg.gate_min_component_score:
                all_ok = False
                failures.append(f"{cid}={s:.3f}")
        gates["G5_component_scores"] = {
            "passed": all_ok,
            "threshold": cfg.gate_min_component_score,
            "actual": {cid: round(candidate_scores.get(cid, 0.0), 4)
                       for cid in candidate.capability_ids},
            "reason": "All component scores >= threshold" if all_ok
                       else f"Below threshold: {', '.join(failures)}",
        }
        if all_ok:
            passed += 1

        # ── Determine status ──
        is_validated = passed == 5
        if is_validated:
            status = "validated"
        elif passed >= 3:
            status = "pending_review"
        else:
            status = "rejected"

        # ── Evidence support ──
        evidence_support = self._collect_evidence(candidate)

        # ── Signature ──
        sig = self._compute_signature(candidate, observation)

        return CompositionProposal(
            id=f"COMP-PROP-{index + 1:03d}",
            candidate=candidate,
            evidence_support=evidence_support,
            source_match_id=getattr(observation, "id", ""),
            source_document_id=observation.document_id,
            validation_gates=gates,
            gates_passed=passed,
            total_gates=5,
            is_validated=is_validated,
            confidence=candidate.composition_score,
            status=status,
            signature=sig,
        )

    # ──────────────────────── Helpers ───────────────────────────────

    def _single_cap_coverage(
        self,
        cap_id: str,
        cap_signals: dict[str, set[str]],
        all_signals: list[str],
    ) -> float:
        """Compute coverage of a single capability over the observation signals."""
        if not cap_id or not all_signals:
            return 0.0
        covered = cap_signals.get(cap_id, set()) & set(all_signals)
        return len(covered) / len(all_signals)

    def _collect_evidence(self, candidate: CompositionCandidate) -> list[str]:
        """
        Collect evidence IDs from Registry for all capabilities in the composition.
        This provides the Experience → Evidence → Proposal chain.
        """
        evidence = []
        for cap_id in candidate.capability_ids:
            cap = self.registry.get(cap_id)
            if cap:
                # Use source_pattern_ids as evidence trace
                for pid in cap.source_pattern_ids:
                    evd_id = f"EVD-{cap_id}-{pid}"
                    if evd_id not in evidence:
                        evidence.append(evd_id)
                # Also track documents tested
                for doc in cap.documents_tested:
                    evd_id = f"EVD-DOC-{doc}"
                    if evd_id not in evidence:
                        evidence.append(evd_id)
        return evidence

    def _compute_signature(
        self,
        candidate: CompositionCandidate,
        observation: DocumentObservation,
    ) -> str:
        """Compute a deterministic hash for proposal provenance."""
        content = (
            "+".join(sorted(candidate.capability_ids))
            + "|"
            + observation.document_id
            + "|"
            + str(len(observation.detected_pattern_ids))
        )
        return hashlib.sha256(content.encode()).hexdigest()[:16]
