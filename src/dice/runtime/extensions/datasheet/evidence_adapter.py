"""
Phase 16.1: Datasheet Extension — Evidence Adapter (Skeleton).

CAND-002 (datasheet EXTEND) Implementation Adapter layer, component 4 of 4.
This module is a STRUCTURE-ONLY skeleton: it defines the interface-contract
OUTPUT type (`MappingEvidence`) and the adapter class with its method
signature. NO business evidence-assembly logic is implemented here — the
produce() body raises NotImplementedError by design.

Architecture position (Phase 14.5 Review 1 = B. Implementation Adapter layer):
    The terminal observation step. It assembles an ExtractedFact into a
    `MappingEvidence` observation artifact. MappingEvidence is APPEND-ONLY
    observation: it records what was observed, never what to do next.

Chain position (single-direction data flow, Phase 14.5 §6.2):
    ExtractedFact (component 3 out) → MappingEvidence (component 4 out)

Interface contract (Phase 15 Review 4):
    Input  : ExtractedFact
    Output : MappingEvidence
    FORBIDDEN outputs: CapabilityDecision / SelectedCapability / ExecutionPlan

Responsibilities:
    IN  : evidence adapter (append-only observation assembly, zero authority)
    OUT : capability selection / document_type routing / ranking / decision /
          execution planning / any recommendation

Field whitelist (ALLOWED only):
    input document span / mapped capability identity / extracted fact /
    validation metadata  (all read-only, append-only)
FORBIDDEN:
    decision / recommendation / ranking / score / confidence / priority /
    selection / routing / fallback / activation / execution_plan /
    CapabilityDecision / SelectedCapability / ExecutionPlan

CRITICAL: MappingEvidence is an APPEND-ONLY observation. It carries the fact
"this input span maps to that existing capability identity with this extracted
fact". It does NOT carry a decision to execute anything, does NOT select a
capability, and does NOT produce an execution plan.

Invariants enforced by construction on the OUTPUT artifact:
    parent always None / shadow_marked always True / is_hypothetical always
    True / origin always "composition_shadow_storage" /
    production_execution always False  (I-1 ~ I-5)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .extraction_adapter import ExtractedFact


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class MappingEvidence:
    """Interface-contract OUTPUT — an append-only mapping observation.

    Produced by EvidenceAdapter.produce(). This is the terminal artifact of
    the datasheet extension pipeline. It records, as an APPEND-ONLY
    observation, the mapping between an input document span, an existing
    capability identity, and an extracted fact, plus validation metadata.

    MappingEvidence expresses ONLY (Phase 16.1 §2):
        - input document span   (fact)
        - mapped capability identity (read-only reference, fact)
        - extracted fact        (fact)
        - validation metadata   (fact)
    It is FORBIDDEN from expressing:
        CapabilityDecision / SelectedCapability / ExecutionPlan

    It carries ZERO decision/selection/routing/execution authority.

    Invariants (I-1 ~ I-5) enforced by construction.

    Fields:
        input_document_span   : read-only reference to the source span (fact)
        mapped_capability     : read-only identity reference to an existing
                                capability (fact; NEVER selected_capability)
        extracted_fact        : read-only reference to the extracted fact (fact)
        validation_metadata   : declarative validation metadata (fact)
        parent / shadow_marked / origin / is_hypothetical /
        production_execution  : invariant fields (I-1 ~ I-5)
        produced_at           : ISO-8601 timestamp (fact)
    """

    # ── Input document span reference ──
    input_document_span: str = ""        # read-only span identifier (fact)

    # ── Mapped capability identity (read-only, NOT selected_capability) ──
    mapped_capability: str = ""          # existing identity reference (fact)

    # ── Extracted fact reference ──
    extracted_fact: str = ""             # read-only fact reference (fact)

    # ── Declarative validation metadata (append-only, zero execution) ──
    validation_metadata: Dict[str, Any] = field(default_factory=dict)

    # ── Invocation ownership (invariant I-1) ──
    parent: Optional[str] = None         # ALWAYS None — never set by any caller

    # ── Shadow Marker (invariant I-2 / I-3 / I-4 / I-5) ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"
    is_hypothetical: bool = True
    production_execution: bool = False   # invariant I-5: never True

    # ── Metadata ──
    produced_at: str = field(default_factory=_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_document_span": self.input_document_span,
            "mapped_capability": self.mapped_capability,
            "extracted_fact": self.extracted_fact,
            "validation_metadata": dict(self.validation_metadata),
            "parent": self.parent,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "is_hypothetical": self.is_hypothetical,
            "production_execution": self.production_execution,
            "produced_at": self.produced_at,
        }


class EvidenceAdapter:
    """Component 4 of 4 — append-only evidence assembly (zero authority).

    Turns an `ExtractedFact` into a `MappingEvidence` as an APPEND-ONLY
    observation. It assembles the fact reference, the mapped capability
    identity, and validation metadata into the terminal pipeline artifact.
    It does NOT produce a CapabilityDecision, SelectedCapability, or
    ExecutionPlan; it does NOT select, route, rank, score, or decide.

    Usage (Human-driven):
        adapter = EvidenceAdapter()
        evidence = adapter.produce(fact)

    SKELETON NOTE (Phase 16.1): produce() raises NotImplementedError.
    The evidence-assembly algorithm is business logic to be implemented in a
    later phase. This class provides only the signature and the data-model
    contract.
    """

    def produce(self, fact: ExtractedFact) -> MappingEvidence:
        """Assemble an ExtractedFact into a MappingEvidence.

        Phase 16.2 — append-only evidence-object creation + validation
        metadata generation. Records the input span, mapped capability
        identity, extracted fact, and validation metadata as facts. ZERO
        decision, ZERO selection, ZERO routing, ZERO execution planning.

        Args:
            fact: the extracted fact (component 3 output).

        Returns:
            MappingEvidence (observation artifact, invariants I-1~I-5).
        """
        # Validation metadata generation (Phase 16.2 allowed scope): records
        # only observation facts about the evidence, never a decision.
        validation_metadata = {
            "validation_mode": "observation_only",
            "capability_reference_present": bool(fact.capability_reference),
            "extraction_mode": fact.extraction_metadata.get(
                "extraction_mode", ""
            ),
            "authority": "zero",
        }
        return MappingEvidence(
            input_document_span=fact.source_span,
            mapped_capability=fact.capability_reference,
            extracted_fact=fact.normalized_value,
            validation_metadata=validation_metadata,
        )


__all__ = [
    "MappingEvidence",
    "EvidenceAdapter",
]
