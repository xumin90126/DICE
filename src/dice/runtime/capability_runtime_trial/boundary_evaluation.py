"""Phase 16.20: Declaration-driven Generic Boundary Evaluation.

This module migrates the hardcoded boundary evaluation (Phase 16.16 Step 2)
into a Declaration-driven, capability-agnostic Generic Boundary Evaluation.
It contains THREE zero-authority pieces:

    1. CapabilityBoundaryProjection — a FROZEN, read-only projection of a
       Capability Definition's boundary fields (positive_boundary /
       negative_boundary / boundary_constraints). A projection is a DERIVED
       snapshot read from the single source of truth (the Definition's
       boundary serialization, `dice/capabilities/<ID>/boundary_declaration.json`).
       It is NOT a parallel boundary table, NOT Runtime-owned, NOT mutated.

    2. BoundaryDeclarationReader — a zero-authority projection reader. It
       resolves a Human-specified capability identity to its boundary
       declaration (read-only) and produces a frozen projection. It NEVER
       selects, routes, ranks, scores, recommends, or holds capability
       knowledge.

    3. GenericBoundaryEvaluator — a generic, capability-agnostic evaluator.
       It compares observed DocumentSpan facts against the projection's
       declared constraints using ONLY deterministic fact comparisons
       (membership / equality / presence) and outputs a BoundaryEvaluationReport
       (observation-only). It NEVER interprets semantics, selects, discovers,
       routes, enforces policy, corrects, or falls back.

CRITICAL BOUNDARY (Phase 16.19 §Q2/Q7): the evaluator carries ZERO capability
knowledge. It does not know what any specific unit or span category "means";
it only reads the projection's declared values and compares them
deterministically. The control flow is a FIXED four-segment comparison
(capability-independent), so adding a capability adds a declaration DATA row
(O(N) data) without adding a control-flow branch (O(1) logic) — the
Non-Rule Guarantee.

Failure modes are REPORT-ONLY (Phase 16.19 §Q5): a missing / malformed
declaration or an incomplete observed fact produces a SCHEMA_MISMATCH
observation. There is NO legacy fallback, NO hidden hardcoded branch, NO
automatic repair, NO default capability.

Invariants enforced by construction on the OUTPUT projection (I-1 ~ I-5):
    parent always None / shadow_marked always True / is_hypothetical always
    True / origin always "composition_shadow_storage" /
    production_execution always False
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from dice.runtime.extensions.datasheet.normalization_adapter import DocumentSpan

from .models import BoundaryEvaluationReport, BoundaryStatus


# ──────────────────────────────────────────────────────────────────────────
# Declaration-status vocabulary (factual states, NOT actions)
# ──────────────────────────────────────────────────────────────────────────
STATUS_RESOLVED = "resolved"
STATUS_MISSING = "missing"
STATUS_MALFORMED = "malformed"


@dataclass(frozen=True)
class CapabilityBoundaryProjection:
    """A FROZEN, read-only projection of a Capability Definition's boundary.

    Produced by BoundaryDeclarationReader.load_projection(). It is a DERIVED
    snapshot of the boundary fields (positive_boundary / negative_boundary /
    boundary_constraints) read from the single source of truth. It is NOT a
    parallel table, NOT Runtime-owned, and holds ZERO capability knowledge:
    the tuple values are opaque facts (the evaluator compares them, it does
    not interpret them).

    Fields:
        capability_id       : echo of the Human-specified identity (fact)
        declaration_status  : one of "resolved" / "missing" / "malformed"
                              (a factual read result, never an action)
        required_span_types : tuple of accepted span_type values
                              (positive boundary; opaque to the evaluator)
        excluded_span_types : tuple of excluded span_type values
                              (negative boundary; opaque to the evaluator)
        required_unit_tokens: tuple of required unit tokens
                              (boundary constraints; opaque to the evaluator)
        boundary_reason     : explanatory metadata (passthrough only, NOT
                              evaluated)
        source              : read-only provenance reference to the
                              declaration file (fact)
        parent / shadow_marked / origin / is_hypothetical /
        production_execution: invariant fields (I-1 ~ I-5)
    """

    capability_id: str = ""
    declaration_status: str = STATUS_MISSING
    required_span_types: Tuple[str, ...] = ()
    excluded_span_types: Tuple[str, ...] = ()
    required_unit_tokens: Tuple[str, ...] = ()
    boundary_reason: str = ""
    source: str = ""

    # ── Invocation ownership (invariant I-1) ──
    parent: Optional[str] = None  # ALWAYS None — never set by any caller

    # ── Shadow Marker (invariant I-2 / I-3 / I-4 / I-5) ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"
    is_hypothetical: bool = True
    production_execution: bool = False  # invariant I-5: never True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "declaration_status": self.declaration_status,
            "required_span_types": list(self.required_span_types),
            "excluded_span_types": list(self.excluded_span_types),
            "required_unit_tokens": list(self.required_unit_tokens),
            "boundary_reason": self.boundary_reason,
            "source": self.source,
            "parent": self.parent,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "is_hypothetical": self.is_hypothetical,
            "production_execution": self.production_execution,
        }


class BoundaryDeclarationReader:
    """Zero-authority projection reader (Phase 16.19 §Q1/M-4).

    Resolves a Human-specified capability identity to its boundary
    declaration (read-only) and produces a FROZEN CapabilityBoundaryProjection.
    It reads the single source of truth — the Definition's boundary
    serialization — and derives a projection on each call. It NEVER maintains
    a parallel table, NEVER caches/mutates declaration data, NEVER selects /
    routes / ranks / scores / recommends, and holds ZERO capability knowledge.

    Declaration shape validated (malformed otherwise, Phase 16.19 §Q5):
        positive_boundary.required_span_types  -> list[str]   (required)
        positive_boundary.boundary_reason       -> str         (optional)
        negative_boundary.exclusions[*].excluded_span_types -> list[str] (required)
        boundary_constraints.required_unit_tokens -> list[str] (required)

    Usage (Human-driven, per call):
        reader = BoundaryDeclarationReader()
        projection = reader.load_projection("<capability-id>")
    """

    # ── Relative location of the Definition boundary serialization ──
    _DECLARATION_FILENAME = "boundary_declaration.json"

    def load_projection(self, capability_id: str) -> CapabilityBoundaryProjection:
        """Resolve a capability identity to its frozen boundary projection.

        Args:
            capability_id: the Human-specified capability identity (exact).

        Returns:
            CapabilityBoundaryProjection (resolved / missing / malformed).
        """
        path = self._declaration_path(capability_id)
        if path is None or not path.exists():
            return CapabilityBoundaryProjection(
                capability_id=self._safe_id(capability_id),
                declaration_status=STATUS_MISSING,
                source="",
            )
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError, UnicodeDecodeError, ValueError):
            return CapabilityBoundaryProjection(
                capability_id=self._safe_id(capability_id),
                declaration_status=STATUS_MALFORMED,
                source=str(path),
            )
        status, fields = self._extract(data)
        return CapabilityBoundaryProjection(
            capability_id=self._safe_id(capability_id),
            declaration_status=status,
            source=str(path),
            **fields,
        )

    # ────────────────────────────────────────────────────────────────────
    # Private helpers (read-only, deterministic, no decision)
    # ────────────────────────────────────────────────────────────────────

    def _declaration_path(self, capability_id: str) -> Optional[Path]:
        """Resolve the declaration file path for a capability identity.

        Returns None for an empty / non-string identity (no path to read).
        """
        if not isinstance(capability_id, str) or not capability_id.strip():
            return None
        base = Path(__file__).resolve().parents[3] / "dice" / "capabilities"
        return base / capability_id / self._DECLARATION_FILENAME

    @staticmethod
    def _safe_id(capability_id: str) -> str:
        return capability_id if isinstance(capability_id, str) else ""

    @staticmethod
    def _is_str_list(value: Any) -> bool:
        return isinstance(value, list) and all(
            isinstance(item, str) for item in value
        )

    def _extract(self, data: Any) -> Tuple[str, Dict[str, Any]]:
        """Validate the declaration shape and extract the projection values.

        Returns (status, fields). `status` is "resolved" when the shape is
        valid, else "malformed". No interpretation, no repair — a malformed
        declaration is reported, never fixed.
        """
        if not isinstance(data, dict):
            return STATUS_MALFORMED, {}

        pos = data.get("positive_boundary")
        neg = data.get("negative_boundary")
        cons = data.get("boundary_constraints")

        # positive_boundary.required_span_types (list[str], required)
        if not isinstance(pos, dict) or not self._is_str_list(
            pos.get("required_span_types")
        ):
            return STATUS_MALFORMED, {}
        required_span_types = tuple(pos["required_span_types"])

        # negative_boundary.exclusions[*].excluded_span_types (list[dict], required)
        excluded: list = []
        if not isinstance(neg, dict) or not isinstance(neg.get("exclusions"), list):
            return STATUS_MALFORMED, {}
        for exclusion in neg["exclusions"]:
            if not isinstance(exclusion, dict) or not self._is_str_list(
                exclusion.get("excluded_span_types")
            ):
                return STATUS_MALFORMED, {}
            excluded.extend(exclusion["excluded_span_types"])

        # boundary_constraints.required_unit_tokens (list[str], required)
        if not isinstance(cons, dict) or not self._is_str_list(
            cons.get("required_unit_tokens")
        ):
            return STATUS_MALFORMED, {}
        required_unit_tokens = tuple(cons["required_unit_tokens"])

        # boundary_reason (str, optional; passthrough only)
        boundary_reason = pos.get("boundary_reason", "")
        boundary_reason = boundary_reason if isinstance(boundary_reason, str) else ""

        return STATUS_RESOLVED, {
            "required_span_types": required_span_types,
            "excluded_span_types": tuple(excluded),
            "required_unit_tokens": required_unit_tokens,
            "boundary_reason": boundary_reason,
        }


class GenericBoundaryEvaluator:
    """Generic, capability-agnostic boundary evaluator (Phase 16.19 §Q2).

    Compares observed DocumentSpan facts against a projection's declared
    constraints using a FIXED four-segment comparison (capability-independent)
    and outputs a BoundaryEvaluationReport (observation-only). It performs
    ONLY deterministic fact comparisons — membership (`in`), equality (`==`),
    presence (`any(tok in text)`) — and NEVER interprets semantics, selects,
    discovers, routes, enforces policy, corrects, or falls back.

    Usage (Human-driven, per call):
        evaluator = GenericBoundaryEvaluator()
        report = evaluator.evaluate(projection, document_span, capability_id)
    """

    def evaluate(
        self,
        projection: CapabilityBoundaryProjection,
        document_span: Optional[DocumentSpan],
        capability_id: str = "",
    ) -> BoundaryEvaluationReport:
        """Evaluate an observed span against a frozen boundary projection.

        Args:
            projection: the frozen boundary projection (from the reader).
            document_span: the frozen-schema span to observe (may be None).
            capability_id: the Human-specified identity (echoed in reasons).

        Returns:
            BoundaryEvaluationReport (WITHIN / NEGATIVE_BOUNDARY_HIT /
            SCHEMA_MISMATCH) — a factual observation, never an action.
        """
        identity = capability_id or projection.capability_id

        # ── Declaration integrity (report-only, no fallback / repair) ──
        if projection.declaration_status == STATUS_MISSING:
            return BoundaryEvaluationReport(
                boundary_status=BoundaryStatus.SCHEMA_MISMATCH,
                violated_fields=["boundary_declaration.missing"],
                reason=f"no boundary declaration for {identity!r}",
            )
        if projection.declaration_status == STATUS_MALFORMED:
            return BoundaryEvaluationReport(
                boundary_status=BoundaryStatus.SCHEMA_MISMATCH,
                violated_fields=["boundary_declaration.malformed"],
                reason=f"boundary declaration for {identity!r} is malformed",
            )

        # ── Observed-fact completeness (Phase 16.19 §Q5) ──
        if document_span is None:
            return BoundaryEvaluationReport(
                boundary_status=BoundaryStatus.SCHEMA_MISMATCH,
                violated_fields=["input_schema.document_span"],
                reason="document_span is absent (no span to observe)",
            )

        span_type = document_span.span_type
        span_text = document_span.span_text

        # ① Negative boundary (membership) → NEGATIVE_BOUNDARY_HIT.
        if span_type in projection.excluded_span_types:
            return BoundaryEvaluationReport(
                boundary_status=BoundaryStatus.NEGATIVE_BOUNDARY_HIT,
                violated_fields=["negative_boundary.exclusions"],
                reason=(
                    f"span_type {span_type!r} is a declared exclusion "
                    f"for {identity!r}"
                ),
            )

        # ② Positive span_type (membership) → SCHEMA_MISMATCH.
        if span_type not in projection.required_span_types:
            return BoundaryEvaluationReport(
                boundary_status=BoundaryStatus.SCHEMA_MISMATCH,
                violated_fields=["input_schema.span_type"],
                reason=(
                    f"span_type {span_type!r} is not a required span type "
                    f"for {identity!r}"
                ),
            )

        # ③ Unit token (presence) → SCHEMA_MISMATCH.
        if not any(tok in span_text for tok in projection.required_unit_tokens):
            return BoundaryEvaluationReport(
                boundary_status=BoundaryStatus.SCHEMA_MISMATCH,
                violated_fields=["boundary_constraints.required_unit_tokens"],
                reason=(
                    "span_text carries no required unit token from "
                    "boundary_constraints.required_unit_tokens"
                ),
            )

        # Positive boundary satisfied → WITHIN.
        return BoundaryEvaluationReport(
            boundary_status=BoundaryStatus.WITHIN,
            violated_fields=[],
            reason=f"span is within the positive boundary of {identity!r}",
        )


__all__ = [
    "CapabilityBoundaryProjection",
    "BoundaryDeclarationReader",
    "GenericBoundaryEvaluator",
    "STATUS_RESOLVED",
    "STATUS_MISSING",
    "STATUS_MALFORMED",
]
