"""Phase 17.2: Extraction Layer Migration — Declaration-driven Generic Extractor.

This module migrates the extraction layer from a capability-specific,
code-level binding (if-elif dispatch + one method per capability + one regex
per capability) into a DECLARATION-DRIVEN, capability-agnostic Generic
Extractor. It is the extraction-layer counterpart of the boundary-layer
migration already completed in Phase 16.20, and is authorized by the
Phase 17.1 Extraction Generalization Design (D-17.1-1 ~ D-17.1-7).

Architecture (Before → After):

    Before (Phase 16.4):
        ExtractionAdapter
            +-- one method per capability  (capability-specific methods)
            +-- one regex per capability   (capability-specific regexes)
            +-- if capability_reference == ...  (if-elif dispatch)
            +-- a capability→attribute mapping table (parallel table)

    After (Phase 17.2):
        ExtractionAdapter                    (compat surface, thin delegate)
            +-- GenericExtractor             (capability-independent, fixed
            |                                   four-segment control flow)
            |       +-- ExtractionDeclarationReader (zero-authority projection
            |       |                               reader; single source =
            |       |                               extraction_declaration.json)
            |       +-- ExtractionProjection        (frozen read-only projection)
            |       +-- ExtractedFact               (observation output)
            |       +-- UNIT_CANON                  (global unit normalization)
            +-- ExtractionProjection / ExtractionDeclarationReader (re-exported)

CRITICAL BOUNDARY (Phase 17.1 §Q3):
    GenericExtractor performs ONLY four deterministic segments:
        Step A — read the extraction declaration projection (exact key)
        Step B — validate the declaration status (report-only)
        Step C — apply the deterministic regex pattern (compile + search)
        Step D — UNIT_CANON normalization + ExtractedFact output
    It NEVER selects, discovers, ranks, scores, or decides. The control flow
    is a FIXED four-segment sequence (capability-independent); adding a
    capability adds a declaration DATA row (O(N) data) WITHOUT adding a
    control-flow branch (O(1) logic) — the Non-Rule Guarantee (Phase 17.1 §5.4).

EXTRACTION STATUS VOCABULARY (Phase 17.1 §Q6 — factual states, NOT actions):
    EXTRACTED              — pattern matched + unit normalized (success)
    NO_MATCH               — pattern did not match the span (honest "no value")
    DECLARATION_MISSING    — extraction declaration file absent
    DECLARATION_MALFORMED  — declaration missing required fields / wrong types
    UNSUPPORTED_PATTERN    — pattern cannot compile / strategy kind unsupported

    All failures produce an EMPTY observation (empty attribute/value/unit)
    with a factual `extraction_status`. There is NO fallback extractor, NO
    hidden hardcoded branch, NO automatic repair, NO default extractor —
    the deleted per-capability methods / regex / dispatch no longer exist, so
    "falling back" is structurally impossible (Phase 17.1 §Q6.3).

SINGLE SOURCE OF TRUTH (Phase 17.1 §Q2):
    Extraction strategy facts live in the Capability Definition's extraction
    serialization `dice/capabilities/<ID>/extraction_declaration.json`. The
    reader resolves a Human-specified capability identity to a FROZEN
    projection. This is NOT a parallel extractor registry: the declaration
    holds only DATA (pattern string / group names / attribute name), never a
    code reference / import path / callable (Phase 17.1 §2.4).

Invariants enforced by construction on all OUTPUT artifacts (I-1 ~ I-5):
    parent always None / shadow_marked always True / is_hypothetical always
    True / origin always "composition_shadow_storage" /
    production_execution always False
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .schema_adapter import SchemaMappingCandidate


# ──────────────────────────────────────────────────────────────────────────
# Extraction status vocabulary (factual states, NOT actions)
# ──────────────────────────────────────────────────────────────────────────
STATUS_EXTRACTED = "extracted"
STATUS_NO_MATCH = "no_match"
STATUS_DECLARATION_MISSING = "declaration_missing"
STATUS_DECLARATION_MALFORMED = "declaration_malformed"
STATUS_UNSUPPORTED_PATTERN = "unsupported_pattern"


# ──────────────────────────────────────────────────────────────────────────
# Declaration read-result vocabulary (provenance state, NOT actions)
# ──────────────────────────────────────────────────────────────────────────
_DECL_RESOLVED = "resolved"
_DECL_MISSING = "missing"
_DECL_MALFORMED = "malformed"


# ──────────────────────────────────────────────────────────────────────────
# Single frozen strategy kind. GenericExtractor supports EXACTLY this one
# deterministic application and performs ZERO kind dispatch (a dispatch over
# `kind` would re-introduce execution routing — Phase 17.1 §3.6). Any other
# kind value is reported as UNSUPPORTED_PATTERN.
# ──────────────────────────────────────────────────────────────────────────
_STRATEGY_KIND = "deterministic_regex"


# ──────────────────────────────────────────────────────────────────────────
# Global unit-normalization infrastructure (shared, NOT per-capability).
#
# This is the SAME frozen dictionary from Phase 16.4 (C-3). It is a global
# "unit token → canonical unit symbol" normalization map — a shared
# POST-PROCESSING infrastructure, NOT a "capability → extractor" binding
# table (Phase 17.1 §0.4). It is preserved verbatim as a global declaration.
# ──────────────────────────────────────────────────────────────────────────
_UNIT_DEG_C = "\u00b0C"     # °C — canonical degree Celsius
_UNIT_DEG_C_ALT = "\u2103"  # ℃ — single-char degree Celsius variant
_UNIT_MU = "\u03bc"         # μ — Greek small letter mu (canonical micro sign)

UNIT_CANON: Dict[str, str] = {
    # degree unit
    _UNIT_DEG_C: _UNIT_DEG_C,       # °C → °C (identity)
    _UNIT_DEG_C_ALT: _UNIT_DEG_C,   # ℃ → °C
    # volume unit (micro-litre)
    _UNIT_MU + "l": _UNIT_MU + "l",  # μl → μl (identity)
    "\u00b5l": _UNIT_MU + "l",       # µl → μl (micro sign variant)
    "\u00b5L": _UNIT_MU + "l",       # µL → μl
    "ul": _UNIT_MU + "l",            # ul → μl (Latin 'u')
    # length unit (micro-metre)
    _UNIT_MU + "m": _UNIT_MU + "m",  # μm → μm (identity)
    "\u00b5m": _UNIT_MU + "m",       # µm → μm
    "um": _UNIT_MU + "m",            # um → μm (Latin 'u')
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ──────────────────────────────────────────────────────────────────────────
# ExtractionProjection — FROZEN read-only projection of an extraction declaration
# ──────────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class ExtractionProjection:
    """A FROZEN, read-only projection of a Capability Definition's extraction
    declaration.

    Produced by ExtractionDeclarationReader.load_projection(). It is a DERIVED
    snapshot of the extraction strategy fields (attribute_name / strategy.kind /
    strategy.pattern / capture group names / unit normalization) read from the
    single source of truth (`dice/capabilities/<ID>/extraction_declaration.json`).
    It is NOT a parallel registry, NOT Runtime-owned, and holds ZERO authority:
    the values are opaque data (the Generic Extractor applies them, it does not
    interpret their semantics).

    Fields:
        capability_id        : echo of the Human-specified identity (fact)
        declaration_status   : "resolved" / "missing" / "malformed" (a factual
                               read result, never an action)
        attribute_name       : declared attribute name (opaque data)
        strategy_kind        : declared strategy kind (opaque data)
        pattern              : declared regex source string (opaque data)
        capture_value_group  : declared value capture-group name (opaque data)
        capture_unit_group   : declared unit capture-group name (opaque data)
        unit_normalization   : declared normalization reference (opaque data)
        source               : read-only provenance reference (fact)
        parent / shadow_marked / origin / is_hypothetical /
        production_execution : invariant fields (I-1 ~ I-5)
    """

    capability_id: str = ""
    declaration_status: str = _DECL_MISSING
    attribute_name: str = ""
    strategy_kind: str = ""
    pattern: str = ""
    capture_value_group: str = ""
    capture_unit_group: str = ""
    unit_normalization: str = ""
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
            "attribute_name": self.attribute_name,
            "strategy_kind": self.strategy_kind,
            "pattern": self.pattern,
            "capture_value_group": self.capture_value_group,
            "capture_unit_group": self.capture_unit_group,
            "unit_normalization": self.unit_normalization,
            "source": self.source,
            "parent": self.parent,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "is_hypothetical": self.is_hypothetical,
            "production_execution": self.production_execution,
        }


# ──────────────────────────────────────────────────────────────────────────
# ExtractionDeclarationReader — zero-authority projection reader
# ──────────────────────────────────────────────────────────────────────────
class ExtractionDeclarationReader:
    """Zero-authority projection reader (Phase 17.1 §Q3 Step A).

    Resolves a Human-specified capability identity to its extraction
    declaration (read-only) and produces a FROZEN ExtractionProjection. It
    reads the single source of truth — the Definition's extraction
    serialization — and derives a projection on each call. It NEVER maintains
    a parallel registry, NEVER caches/mutates declaration data, and holds ZERO
    capability knowledge (the declaration values are opaque data).

    Declaration shape validated (malformed otherwise, Phase 17.1 §Q6):
        capability_id             -> str (echo only)
        attribute_name            -> str (required, non-empty)
        strategy.kind             -> str (required, non-empty)
        strategy.pattern          -> str (required, non-empty)
        strategy.capture_value_group  -> str (required, non-empty)
        strategy.capture_unit_group   -> str (required, non-empty)
        strategy.unit_normalization   -> str (optional; default "unit_canon")

    Usage (Human-driven, per call):
        reader = ExtractionDeclarationReader()
        projection = reader.load_projection("<capability-id>")
    """

    # ── Relative location of the Definition extraction serialization ──
    _DECLARATION_FILENAME = "extraction_declaration.json"

    def load_projection(self, capability_id: str) -> ExtractionProjection:
        """Resolve a capability identity to its frozen extraction projection.

        Args:
            capability_id: the Human-specified capability identity (exact).

        Returns:
            ExtractionProjection (resolved / missing / malformed).
        """
        path = self._declaration_path(capability_id)
        if path is None or not path.exists():
            return ExtractionProjection(
                capability_id=self._safe_id(capability_id),
                declaration_status=_DECL_MISSING,
                source="",
            )
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError, UnicodeDecodeError, ValueError):
            return ExtractionProjection(
                capability_id=self._safe_id(capability_id),
                declaration_status=_DECL_MALFORMED,
                source=str(path),
            )
        status, fields = self._extract(data)
        return ExtractionProjection(
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
        # extraction_adapter.py lives at dice/runtime/extensions/datasheet/;
        # parents[4] is the workspace root, under which dice/capabilities sits.
        base = Path(__file__).resolve().parents[4] / "dice" / "capabilities"
        return base / capability_id / self._DECLARATION_FILENAME

    @staticmethod
    def _safe_id(capability_id: str) -> str:
        return capability_id if isinstance(capability_id, str) else ""

    def _extract(self, data: Any):
        """Validate the declaration shape and extract the projection values.

        Returns (status, fields). `status` is "resolved" when the shape is
        valid, else "malformed". No interpretation, no repair — a malformed
        declaration is reported, never fixed.
        """
        if not isinstance(data, dict):
            return _DECL_MALFORMED, {}

        attribute_name = data.get("attribute_name")
        if not isinstance(attribute_name, str) or not attribute_name:
            return _DECL_MALFORMED, {}

        strategy = data.get("strategy")
        if not isinstance(strategy, dict):
            return _DECL_MALFORMED, {}

        kind = strategy.get("kind")
        pattern = strategy.get("pattern")
        capture_value_group = strategy.get("capture_value_group")
        capture_unit_group = strategy.get("capture_unit_group")
        for value in (kind, pattern, capture_value_group, capture_unit_group):
            if not isinstance(value, str) or not value:
                return _DECL_MALFORMED, {}

        unit_normalization = strategy.get("unit_normalization", "unit_canon")
        unit_normalization = (
            unit_normalization if isinstance(unit_normalization, str) else ""
        )

        return _DECL_RESOLVED, {
            "attribute_name": attribute_name,
            "strategy_kind": kind,
            "pattern": pattern,
            "capture_value_group": capture_value_group,
            "capture_unit_group": capture_unit_group,
            "unit_normalization": unit_normalization,
        }


# ──────────────────────────────────────────────────────────────────────────
# ExtractedFact — extraction OUTPUT (observation artifact)
# ──────────────────────────────────────────────────────────────────────────
@dataclass
class ExtractedFact:
    """Extraction OUTPUT — a declarative extracted fact (read-only observation).

    Produced by GenericExtractor. It records a single extracted fact, together
    with a READ-ONLY reference to the EXISTING capability identity to which the
    fact belongs, and a factual extraction status (one of the five states in
    the EXTRACTION STATUS VOCABULARY).

    This is a FACTUAL observation, NOT a selection, NOT a decision, NOT an
    execution plan. `capability_reference` is a read-only identity reference
    (fact), never a `selected_capability` (decision).

    Fields:
        source_span           : read-only reference to the source span (fact)
        attribute_name        : declared attribute name (fact; from the
                                extraction declaration, never runtime-inferred)
        raw_value             : the raw substring matched in the span (fact)
        normalized_value      : the deterministic normalized value (fact)
        unit                  : the canonical unit symbol (fact; lookup-only
                                from UNIT_CANON)
        capability_reference  : read-only identity reference to an EXISTING
                                capability (fact; NEVER selected_capability)
        extraction_status     : one of the five factual status states (fact)
        extraction_metadata   : declarative extraction metadata (fact)
        parent / shadow_marked / origin / is_hypothetical /
        production_execution  : invariant fields (I-1 ~ I-5)
        extracted_at          : ISO-8601 timestamp (fact)
    """

    # ── Read-only source reference ──
    source_span: str = ""                # read-only span identifier (fact)

    # ── Declarative attribute name (design-time-fixed, NOT runtime-inferred) ──
    attribute_name: str = ""

    # ── Raw substring (traceable to source) ──
    raw_value: str = ""

    # ── Deterministic normalized value ──
    normalized_value: str = ""

    # ── Canonical unit symbol (lookup-only) ──
    unit: str = ""

    # ── Read-only capability identity reference ──
    capability_reference: str = ""

    # ── Factual extraction status (one of the five states) ──
    extraction_status: str = STATUS_NO_MATCH

    # ── Declarative extraction metadata (read-only, zero execution) ──
    extraction_metadata: Dict[str, Any] = field(default_factory=dict)

    # ── Invocation ownership (invariant I-1) ──
    parent: Optional[str] = None         # ALWAYS None — never set by any caller

    # ── Shadow Marker (invariant I-2 / I-3 / I-4 / I-5) ──
    shadow_marked: bool = True
    origin: str = "composition_shadow_storage"
    is_hypothetical: bool = True
    production_execution: bool = False   # invariant I-5: never True

    # ── Metadata ──
    extracted_at: str = field(default_factory=_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_span": self.source_span,
            "attribute_name": self.attribute_name,
            "raw_value": self.raw_value,
            "normalized_value": self.normalized_value,
            "unit": self.unit,
            "capability_reference": self.capability_reference,
            "extraction_status": self.extraction_status,
            "extraction_metadata": dict(self.extraction_metadata),
            "parent": self.parent,
            "shadow_marked": self.shadow_marked,
            "origin": self.origin,
            "is_hypothetical": self.is_hypothetical,
            "production_execution": self.production_execution,
            "extracted_at": self.extracted_at,
        }


# ──────────────────────────────────────────────────────────────────────────
# GenericExtractor — capability-independent deterministic extractor
# ──────────────────────────────────────────────────────────────────────────
class GenericExtractor:
    """Capability-independent deterministic extractor (Phase 17.1 §Q3).

    Applies a declaration-driven deterministic extraction pattern to a span
    text using a FIXED four-segment control flow:

        Step A — read the extraction declaration projection (exact key)
        Step B — validate the declaration status (report-only)
        Step C — apply the deterministic regex pattern (compile + search)
        Step D — UNIT_CANON normalization + ExtractedFact output

    The extractor holds ZERO capability knowledge: it reads the projection's
    opaque values (pattern string / group names / attribute name) and applies
    them deterministically. It NEVER selects a capability, NEVER discovers
    one, NEVER ranks / scores / decides / routes (Phase 17.1 §3.1).

    Usage (Human-driven, per call):
        extractor = GenericExtractor()
        fact = extractor.extract(capability_id, span_text, source_span, span_type)
    """

    def __init__(self, reader: Optional[ExtractionDeclarationReader] = None) -> None:
        self._reader = reader if reader is not None else ExtractionDeclarationReader()

    def extract(
        self,
        capability_id: str,
        span_text: str,
        source_span: str = "",
        span_type: str = "",
    ) -> ExtractedFact:
        """Extract a deterministic fact for a Human-specified capability.

        Fixed four-segment control flow (capability-independent). All
        non-success paths produce an EMPTY observation with a factual
        extraction_status — never a fallback, never a repair.

        Args:
            capability_id: the Human-specified capability identity (exact).
            span_text: the normalized span text to observe.
            source_span: optional read-only source-span identifier (fact).
            span_type: optional declarative span category (fact).

        Returns:
            ExtractedFact (observation artifact, invariants I-1~I-5).
        """
        safe_id = capability_id if isinstance(capability_id, str) else ""

        # ── Step A: read the declaration projection (exact key) ──
        projection = self._reader.load_projection(safe_id)

        # ── Step B: validate declaration status (report-only) ──
        if projection.declaration_status == _DECL_MISSING:
            return self._empty(
                source_span, span_type, safe_id, STATUS_DECLARATION_MISSING
            )
        if projection.declaration_status == _DECL_MALFORMED:
            return self._empty(
                source_span, span_type, safe_id, STATUS_DECLARATION_MALFORMED
            )

        # ── Step C: apply the deterministic regex pattern ──
        # Single frozen strategy kind; zero kind dispatch (Phase 17.1 §3.6).
        if projection.strategy_kind != _STRATEGY_KIND:
            return self._empty(
                source_span, span_type, safe_id, STATUS_UNSUPPORTED_PATTERN
            )
        try:
            compiled = re.compile(projection.pattern)
        except re.error:
            return self._empty(
                source_span, span_type, safe_id, STATUS_UNSUPPORTED_PATTERN
            )
        # The declared capture groups must exist in the compiled pattern;
        # otherwise the declaration's group contract is unsupported.
        if (
            projection.capture_value_group not in compiled.groupindex
            or projection.capture_unit_group not in compiled.groupindex
        ):
            return self._empty(
                source_span, span_type, safe_id, STATUS_UNSUPPORTED_PATTERN
            )

        matched = compiled.search(span_text)
        if matched is None:
            return self._empty(source_span, span_type, safe_id, STATUS_NO_MATCH)

        # ── Step D: extract value/unit capture groups + normalize unit ──
        raw_value = matched.group(0)
        value = (matched.group(projection.capture_value_group) or "").strip()
        unit_token = matched.group(projection.capture_unit_group)
        unit = UNIT_CANON.get(unit_token, "")
        if unit == "":
            # An unknown unit token cannot be normalized (lookup-only, C-3):
            # honest "no extraction", never an inference.
            return self._empty(source_span, span_type, safe_id, STATUS_NO_MATCH)

        return ExtractedFact(
            source_span=source_span,
            attribute_name=projection.attribute_name,
            raw_value=raw_value,
            normalized_value=value,
            unit=unit,
            capability_reference=safe_id,
            extraction_status=STATUS_EXTRACTED,
            extraction_metadata={
                "span_type": span_type,
                "extraction_mode": "deterministic",
            },
        )

    # ────────────────────────────────────────────────────────────────────
    # Private helper (read-only, deterministic, no decision)
    # ────────────────────────────────────────────────────────────────────

    @staticmethod
    def _empty(
        source_span: str,
        span_type: str,
        capability_id: str,
        status: str,
    ) -> ExtractedFact:
        """Build an EMPTY fact (honest observation, never an inference)."""
        return ExtractedFact(
            source_span=source_span,
            attribute_name="",
            raw_value="",
            normalized_value="",
            unit="",
            capability_reference=capability_id,
            extraction_status=status,
            extraction_metadata={
                "span_type": span_type,
                "extraction_mode": "none",
            },
        )


# ──────────────────────────────────────────────────────────────────────────
# ExtractionAdapter — compat surface (thin delegate to GenericExtractor)
# ──────────────────────────────────────────────────────────────────────────
class ExtractionAdapter:
    """Component 3 of 4 — deterministic fact extraction (compat surface).

    Preserves the Phase 16.4 public interface (`extract(candidate) ->
    ExtractedFact`) so the pipeline and existing callers remain compatible,
    while delegating the actual extraction to the capability-independent
    GenericExtractor. The adapter only unpacks the candidate's read-only facts
    (capability identity + normalized text + span provenance) and forwards
    them; it holds ZERO authority of its own.

    Usage (Human-driven):
        adapter = ExtractionAdapter()
        fact = adapter.extract(candidate)
    """

    def __init__(self) -> None:
        self._extractor = GenericExtractor()

    def extract(self, candidate: SchemaMappingCandidate) -> ExtractedFact:
        """Extract a deterministic fact from a schema-mapping candidate.

        Unpacks the candidate's read-only capability reference, normalized
        text, span identifier, and span type, then delegates to the Generic
        Extractor. ZERO selection, ZERO routing, ZERO execution, ZERO
        identity creation.

        Args:
            candidate: the schema-mapping candidate (component 2 output).

        Returns:
            ExtractedFact (observation artifact, invariants I-1~I-5).
        """
        capability_reference = candidate.target_capability_input_schema.get(
            "capability_reference", ""
        )
        text = candidate.source_schema.get("normalized_text", "")
        return self._extractor.extract(
            capability_id=capability_reference,
            span_text=text,
            source_span=candidate.span_id,
            span_type=candidate.span_type,
        )


__all__ = [
    "ExtractedFact",
    "ExtractionAdapter",
    "GenericExtractor",
    "ExtractionProjection",
    "ExtractionDeclarationReader",
    "UNIT_CANON",
    "STATUS_EXTRACTED",
    "STATUS_NO_MATCH",
    "STATUS_DECLARATION_MISSING",
    "STATUS_DECLARATION_MALFORMED",
    "STATUS_UNSUPPORTED_PATTERN",
]
