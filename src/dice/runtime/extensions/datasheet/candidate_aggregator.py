"""
Phase 44: CandidateAggregator — deterministic Evidence → CapabilityCandidateObservation
aggregation layer.

CAND-002 (datasheet EXTEND) — Capability Candidate Discovery, the aggregation
module authorized by Phase 44 (Implementation Authorization). This is the
FIRST population of the Phase 16.11 draft-container slot fields.

This module implements a DETERMINISTIC, ZERO-AUTHORITY pure-function layer that
aggregates Human validation decision history (`ValidationRecord`) into draft
`CapabilityCandidateObservation` observations. It answers the Human's
question "here is what you have already validated, grouped by span_type, so you
can decide whether a Capability is worth forming" — WITHOUT deciding anything.

CRITICAL BOUNDARY (Phase 44 Scope; Phase 42 §2 / Phase 43 §2 frozen):
    - CANDIDATE != CAPABILITY. The output is a `CapabilityCandidateObservation`
      with `status` ALWAYS "draft". There is NO promotion path here, NO
      registry entry, NO runtime availability, NO capability activation.
    - ZERO AUTHORITY: no semantic inference, no capability naming, no LLM, no
      selection / routing / ranking / scoring / decision / recommendation.
    - GROUPING KEY = `span_type` — a HUMAN-ASSIGNED fact (never inferred by the
      system). The aggregator deliberately does NOT group by `attribute_name`
      (that would require crossing into declaration semantics = inference).
    - PURE FUNCTION: reads only; never mutates inputs, never writes files,
      never touches registry / bootstrap / loader / runtime / declarations.

FORBIDDEN (never present by construction):
    registry / bootstrap / loader import · runtime wiring · automatic capability
    creation · automatic registration · semantic inference · LLM usage ·
    capability naming (candidate_id is a semantically-neutral observation id).

Invariants (I-1 ~ I-5) on every output are inherited from the dataclass
defaults (parent None / shadow_marked True / origin composition_shadow_storage /
is_hypothetical True / production_execution False) — never overridden here.
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional

from .capability_candidate_observation import (
    CapabilityCandidateObservation,
    DRAFT_STATUS,
)
from .evidence_adapter import MappingEvidence
from .schema_adapter import DECLARATIVE_SPAN_TYPE_TO_CAPABILITY
from .validation_memory import (
    ValidationRecord,
    DECISION_ACCEPT,
    DECISION_REJECT,
)

# The EQS "full total" threshold (Phase 43 §3.7). A FULL-TOTAL EQS (4/4) is the
# only observation that may set `eqs_threshold_met = True`. This is an
# OBSERVATION FACT, not a decision gate — the Human decides what to do with it.
_EQS_FULL_TOTAL = 4


class CandidateAggregator:
    """Deterministic, zero-authority Evidence → CandidateObservation aggregation.

    Aggregates a read-only list of `ValidationRecord` (Human decision history)
    into a list of `CapabilityCandidateObservation` (draft observations), one
    per distinct non-empty `span_type`.

    KEY CONTRACTS:
        - DETERMINISTIC   : same input → same output (stable grouping + sorted
          iteration). No randomness, no timestamps that affect grouping, no
          external state.
        - APPEND-ONLY OUT : produces fresh `CapabilityCandidateObservation`
          objects; never mutates the input records or the (optional) evidence.
        - NO MUTATION     : reads inputs only. No file I/O, no store/registry
          writes.
        - ZERO AUTHORITY  : no selection / routing / ranking / scoring /
          decision / recommendation / naming / activation. The only "shape"
          of intelligence here is deterministic counting + set membership.

    Usage (Human-driven):
        aggregator = CandidateAggregator()
        candidates = aggregator.aggregate(memory.all_records())
    """

    def aggregate(
        self,
        records: List[ValidationRecord],
        evidence: Optional[List[MappingEvidence]] = None,
    ) -> List[CapabilityCandidateObservation]:
        """Aggregate validation records into draft candidate observations.

        Grouping key = `span_type` (Human-assigned fact). Records with an empty
        `span_type` cannot form a meaningful candidate identity (`cand-`), so
        they are skipped — a factual "no grouping key", NOT a decision.

        Args:
            records: read-only list of ValidationRecord (Human decision history).
            evidence: OPTIONAL list of MappingEvidence, used ONLY to derive the
                `eqs_threshold_met` observation fact. When None (or empty),
                `eqs_threshold_met` is False — an honest "not evaluated", never
                a fabricated "failed".

        Returns:
            Deterministically ordered list of CapabilityCandidateObservation
            (status ALWAYS "draft"), one per distinct non-empty span_type.
        """
        # ── 1. Deterministic grouping by Human-assigned span_type ──
        groups: Dict[str, List[ValidationRecord]] = {}
        for record in records:
            span_type = (record.span_type or "").strip()
            if not span_type:
                # Empty span_type → no candidate identity; factual skip.
                continue
            groups.setdefault(span_type, []).append(record)

        # ── 2. Build one draft observation per group (sorted for determinism) ──
        candidates: List[CapabilityCandidateObservation] = []
        for span_type in sorted(groups.keys()):
            candidates.append(
                self._build_candidate(span_type, groups[span_type], evidence)
            )
        return candidates

    # ──────────────────────────────────────────────────────────────────────
    # Private helpers (deterministic counting + set membership ONLY)
    # ──────────────────────────────────────────────────────────────────────

    def _build_candidate(
        self,
        span_type: str,
        records: List[ValidationRecord],
        evidence: Optional[List[MappingEvidence]],
    ) -> CapabilityCandidateObservation:
        """Compute the six discovery signals for one span_type group (Phase 43 §3).

        All six signals are deterministic statistics 1:1 mapped onto the
        EXISTING CapabilityCandidateObservation fields (ZERO schema change):

            1 occurrence frequency  → accept_count + reject_count
            2 document coverage     → document_count (distinct document_id)
            3 evidence count        → accept_count
            4 failure recurrence    → reject_count
            5 structural similarity → attribute_pattern (pattern consensus)
            6 validation history    → reason_distribution
            + eqs_threshold_met     → from optional evidence flow (EQS full score)
        """
        accept_count = sum(1 for r in records if r.decision == DECISION_ACCEPT)
        reject_count = sum(1 for r in records if r.decision == DECISION_REJECT)

        # Signal 2 — distinct document coverage (F-1 cross-document count).
        document_count = len({r.document_id for r in records if r.document_id})

        # Signal 6 — reason → count distribution (sorted for determinism).
        reason_counter: Counter = Counter(
            r.reason for r in records if r.reason
        )
        reason_distribution: Dict[str, int] = dict(sorted(reason_counter.items()))

        # Signal 5 — structural pattern consensus (structural similarity,
        # NOT semantic attribute inference). pattern_evidence holds STRUCTURAL
        # pattern names (colon_kv / number_unit / table_row), sorted by
        # (frequency desc, name asc) for determinism.
        pattern_counter: Counter = Counter()
        for r in records:
            for pattern_name in r.pattern_evidence:
                if pattern_name:
                    pattern_counter[pattern_name] += 1
        attribute_pattern = ",".join(
            p for p, _ in sorted(
                pattern_counter.items(), key=lambda kv: (-kv[1], kv[0])
            )
        )

        # eqs_threshold_met — observation fact from the optional evidence flow.
        eqs_threshold_met = self._compute_eqs_threshold(span_type, evidence)

        return CapabilityCandidateObservation(
            candidate_id=f"cand-{span_type}",  # semantically-neutral observation id
            span_type=span_type,
            attribute_pattern=attribute_pattern,
            document_count=document_count,
            accept_count=accept_count,
            reject_count=reject_count,
            reason_distribution=reason_distribution,
            eqs_threshold_met=eqs_threshold_met,
            status=DRAFT_STATUS,  # ALWAYS "draft" — never promoted here
        )

    def _compute_eqs_threshold(
        self,
        span_type: str,
        evidence: Optional[List[MappingEvidence]],
    ) -> bool:
        """Derive `eqs_threshold_met` from the optional evidence flow.

        True IFF at least one MappingEvidence whose `mapped_capability` equals
        the declarative identity for this span_type carries a full-score EQS
        (eqs_total == 4) inside its validation_metadata. The span_type →
        capability identity correspondence is a LOOKUP into the design-time-fixed
        `DECLARATIVE_SPAN_TYPE_TO_CAPABILITY` table (a fact, NOT inference).

        When evidence is None/empty, or the span_type has no declarative
        mapping, the result is False — an honest "not evaluated / not
        applicable", never a fabricated EQS.
        """
        if not evidence:
            return False
        capability_id = DECLARATIVE_SPAN_TYPE_TO_CAPABILITY.get(span_type, "")
        if not capability_id:
            return False
        for item in evidence:
            if item.mapped_capability != capability_id:
                continue
            eqs = item.validation_metadata.get("evidence_quality_score")
            if isinstance(eqs, dict) and eqs.get("eqs_total", 0) >= _EQS_FULL_TOTAL:
                return True
        return False


__all__ = [
    "CandidateAggregator",
]
