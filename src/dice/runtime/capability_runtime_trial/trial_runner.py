"""Phase 16.20: Capability Runtime Trial — Declaration-driven Runner.

This module implements `CapabilityRuntimeTrialRunner.run()` — the minimal,
Human-driven, read-only orchestration chain of the Capability Runtime Trial.
It wires ALREADY-FROZEN zero-authority components into ONE observation chain
and packages the results into a read-only `CapabilityRuntimeObservation`.

Wiring sequence (Step 2 fixed order, Phase 16.15 §6.1; boundary step migrated
to Declaration-driven evaluation in Phase 16.20):

    CapabilityRuntimeRequest(capability_id, document_span, intent="observe")
        [1] CapabilityLoader.load_capability(capability_id)     → CapabilityLoadResult
        [2] InvocationContextRecorder.record_invocation(...)    → InvocationContext
        [3] boundary evaluation (declaration-driven, report-only)
            3a. BoundaryDeclarationReader.load_projection(capability_id)
                → CapabilityBoundaryProjection
            3b. GenericBoundaryEvaluator.evaluate(projection, span)
                → BoundaryEvaluationReport
        [4] [WITHIN only] DatasheetPipeline.run(document_span)  → MappingEvidence
        [5] AuditTrace.record_trace(...)                        → TraceRecord
        [6] package → CapabilityRuntimeObservation

The Runner is PURE ORCHESTRATION. It performs NO selection, NO matching, NO
routing, NO planning, NO execution, NO decision, NO retry, NO fallback, NO
scoring, NO ranking, NO auto registration, NO registry mutation. Its zero
authority is inherited by CONSTRUCTION — it only calls zero-authority
components and passes observation artifacts forward (Phase 16.15 §8.2/§8.3).

CRITICAL BOUNDARY (Phase 16.14 §8 / 16.15 §7.4): boundary evaluation is
REPORT-ONLY. A NEGATIVE_BOUNDARY_HIT / SCHEMA_MISMATCH outcome does NOT
block, retry, fallback, or re-route — it simply produces a factual
BoundaryEvaluationReport and skips the Pipeline (because the schema does not
match, the pipeline would extract nothing). "Not running the Pipeline" is
the PRESENTATION of an observation result, never a Runtime blocking decision.

DECLARATION-DRIVEN (Phase 16.20): the boundary facts are NOT hardcoded here.
They live in the Capability Definition's boundary serialization
(`dice/capabilities/<ID>/boundary_declaration.json`), read as a frozen
projection. This module therefore carries ZERO capability-specific semantic
identifiers — no unit symbol, no span-category name, no concrete value is
embedded in the evaluation path.
"""

from __future__ import annotations

from typing import Optional
from uuid import uuid4

from dice.runtime.composition.shadow.capability_runtime.audit_trace import (
    AuditTrace,
)
from dice.runtime.composition.shadow.capability_runtime.capability_loader import (
    CapabilityLoader,
)
from dice.runtime.composition.shadow.capability_runtime.invocation_context import (
    InvocationContextRecorder,
)
from dice.runtime.composition.shadow.capability_runtime.models.loader import (
    LookupStatus,
)
from dice.runtime.extensions.datasheet.normalization_adapter import DocumentSpan
from dice.runtime.extensions.datasheet.pipeline import DatasheetPipeline

from .boundary_evaluation import (
    BoundaryDeclarationReader,
    GenericBoundaryEvaluator,
)
from .models import (
    BoundaryEvaluationReport,
    BoundaryStatus,
    CapabilityRuntimeRequest,
)
from .observation import CapabilityRuntimeObservation


class CapabilityRuntimeTrialRunner:
    """Minimal orchestration carrier for the Capability Runtime Trial.

    The Runner wires the frozen L3 components (CapabilityLoader /
    InvocationContextRecorder / AuditTrace), the declaration-driven boundary
    evaluation (reader + evaluator), and the DatasheetPipeline into a single
    Human-driven, read-only observation chain. It performs NO selection, NO
    routing, NO planning, NO execution, NO decision, NO retry, NO fallback,
    NO scoring, NO ranking (Runtime Authority = ZERO).

    Usage (Human-driven, per call):
        runner = CapabilityRuntimeTrialRunner()
        observation = runner.run(request)
    """

    def __init__(self) -> None:
        # Frozen zero-authority components (instances are stateless; held
        # only to carry the wiring — no authority, no mutable state).
        self._loader = CapabilityLoader()
        self._invocation = InvocationContextRecorder()
        self._reader = BoundaryDeclarationReader()
        self._evaluator = GenericBoundaryEvaluator()
        self._pipeline = DatasheetPipeline()
        self._audit = AuditTrace()

    # ────────────────────────────────────────────────────────────────────
    # Public orchestration entry (the ONLY public method)
    # ────────────────────────────────────────────────────────────────────

    def run(self, request: CapabilityRuntimeRequest) -> CapabilityRuntimeObservation:
        """Carry one Human-authorized Capability consumption request.

        Sequences the frozen components into the observation chain [1]→[6]
        and returns a READ-ONLY `CapabilityRuntimeObservation` package (load
        result / invocation context / boundary report / evidence record /
        trace record). ZERO decision, selection, routing, execution.

        Args:
            request: the Human-specified CapabilityRuntimeRequest (fact).

        Returns:
            CapabilityRuntimeObservation (observation package).
        """
        capability_id = request.capability_id
        document_span = request.document_span
        invocation_id = f"inv_{uuid4().hex}"

        # [1] Exact Lookup (Human-specified identity; never a query).
        load_result = self._loader.load_capability(capability_id)

        # [2] Record the Human-authorized invocation context (fact).
        input_reference = self._input_reference(document_span)
        invocation_result = self._invocation.record_invocation(
            capability_id=capability_id,
            input_reference=input_reference,
            invocation_id=invocation_id,
            authorized_by="human",
            input_ref_type="observation",
        )
        invocation_context = invocation_result.context

        # [3] Boundary evaluation (declaration-driven, report-only).
        boundary_report = self._evaluate_boundary(capability_id, document_span)

        # [4] [WITHIN only] run the existing pipeline (observation → evidence).
        evidence_record = None
        if boundary_report.boundary_status is BoundaryStatus.WITHIN:
            evidence_record = self._pipeline.run(document_span)

        # [5] Record the trace of the already-occurred invocation (append-only).
        trace_result = self._audit.record_trace(
            invocation_id=invocation_id,
            capability_id=capability_id,
            invoked_at=(
                invocation_context.invoked_at if invocation_context else ""
            ),
            capability_version="",
            input_ref_id=input_reference,
            output_ref_id=self._output_reference(evidence_record),
        )

        # [6] Package the observation (pure carrier, zero authority).
        return CapabilityRuntimeObservation(
            capability_id=capability_id,
            load_result=load_result,
            invocation_context=invocation_context,
            boundary_report=boundary_report,
            evidence_record=evidence_record,
            trace_record=trace_result.record,
        )

    # ────────────────────────────────────────────────────────────────────
    # Private helpers (read-only, deterministic, no decision)
    # ────────────────────────────────────────────────────────────────────

    @staticmethod
    def _input_reference(document_span: Optional[DocumentSpan]) -> str:
        """Read-only ID reference to the input span (no data copy)."""
        if document_span is None:
            return ""
        return document_span.span_id or document_span.document_id or ""

    @staticmethod
    def _output_reference(evidence_record) -> str:
        """Read-only ID reference to the output (no data copy).

        MappingEvidence has no independent id field; the output's identity is
        referenced by the input span it was produced from (fact, no copy).
        Empty when there is no evidence (boundary != WITHIN) — an honest
        "no output" fact, never a fabricated reference.
        """
        if evidence_record is None:
            return ""
        return evidence_record.input_document_span or ""

    def _evaluate_boundary(
        self,
        capability_id: str,
        document_span: Optional[DocumentSpan],
    ) -> BoundaryEvaluationReport:
        """Evaluate the input span against the declared boundary (read-only).

        Declaration-driven, REPORT-ONLY (Phase 16.20): first reads a frozen
        projection of the capability's boundary declaration, then delegates to
        the generic evaluator. Produces a factual three-state observation
        (WITHIN / NEGATIVE_BOUNDARY_HIT / SCHEMA_MISMATCH). It NEVER corrects,
        retries, falls back, routes, blocks, or authorizes anything.

        Args:
            capability_id: the Human-specified capability identity (exact).
            document_span: the frozen-schema span to observe (may be None).

        Returns:
            BoundaryEvaluationReport (observation).
        """
        projection = self._reader.load_projection(capability_id)
        return self._evaluator.evaluate(projection, document_span, capability_id)


__all__ = [
    "CapabilityRuntimeTrialRunner",
]
