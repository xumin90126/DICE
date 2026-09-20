"""
Phase 6.1-L3: Capability Loader (Component 4).

The Capability Loader is the FOURTH passive carrier module of the L3
Capability Runtime. Its single responsibility is:

    RESOLVE a Human-specified capability identity to a read-only reference.

It is an EXACT LOOKUP PROVIDER (RED-LDR-004). It resolves a given,
explicitly-specified `capability_id` to a read-only `CapabilityReference`.
It NEVER recommends, ranks, scores, selects, optimizes, falls back, routes,
activates, decides, or executes. Selection authority and execution
authority belong solely to Human.

Contract (from phase6_1_l3_capability_loader_design_package.md §4):

    Input     A Human-specified, explicit capability_id (not a query/feature)
    Output    CapabilityLoadResult (FOUND + read-only reference, or a
              factual failure status: NOT_FOUND / INVALID_IDENTITY / UNAVAILABLE)
    Duty      Exact identity lookup against the frozen capability table
    Error     unknown identity -> NOT_FOUND (CAPABILITY_NOT_FOUND);
              missing/malformed identity -> INVALID_IDENTITY (INVALID_IDENTITY)
    Forbidden recommendation / ranking / scoring / selection / optimization
              / automatic fallback / routing / activation / execution

Implementation constraints (LDR-L1~LDR-L5):
    - LDR-L1  Exact Lookup Only: input must be an explicit capability_id,
              no identity -> no output; no fuzzy/similarity matching
    - LDR-L2  No Selection / Routing / Ranking: zero selection, routing,
              ranking, scoring, confidence, priority fields
    - LDR-L3  Read-only Reference: reference is a readonly_reference, NOT
              an execution handle, NOT an activation token
    - LDR-L4  No Production / Activation / Governance: three authorities
              all zero; production_execution always False
    - LDR-L5  Incremental Gate: this module is self-contained; zero Registry
              read/write, zero Layer 1-8 coupling
"""

from __future__ import annotations

from typing import Dict, Optional

from .models.loader import (
    CapabilityLoadResult,
    CapabilityMetadata,
    CapabilityReference,
    LookupStatus,
)


# ═══════════════════════════════════════════════════════════════════════════
# Frozen Capability Identity Table (read-only, static, NEVER modified)
# ═══════════════════════════════════════════════════════════════════════════
#
# This is a FROZEN SNAPSHOT of the 21 known capability identities (mirrors
# the FROZEN Registry=21). It is a module-level constant — the EXACT LOOKUP
# source. It is NOT the live Registry: the Loader does NOT import, read, or
# write the production Registry (zero Layer 1-8 coupling, invariant I-6).
#
# Semantics: this table answers ONE factual question — "does the given
# identity exist, and what is its read-only display name?" It does NOT
# rank, score, recommend, or select. There is no priority, no confidence,
# no suitability, no ordering significance (a plain dict, not an ordered
# preference list).
FROZEN_CAPABILITY_TABLE: Dict[str, str] = {
    "CAP-COMP-TABLE": "ComponentsTableUnderstanding",
    "CAP-STORAGE-DETECT": "StorageConditionsDetection",
    "CAP-SAFETY-DETECT": "SafetyWarningsDetection",
    "CAP-TROUBLESHOOT-DETECT": "TroubleshootingDetection",
    "CAP-PROCEDURE-DETECT": "ProcedureDetection",
    "CAP-PREP-MATERIALS-DETECT": "PrepMaterialsDetection",
    "CAP-TABLE-EXTRACT-BASIC": "BasicTableExtraction",
    "CAP-PARAMETER-LIST": "ParameterListExtraction",
    "CAP-STORAGE-LONG-TERM": "LongTermStorageDetection",
    "CAP-WARNING-EXTRACT": "WarningPhraseExtraction",
    "CAP-STEP-COUNTER": "StepCounter",
    "CAP-TEMP-RANGE": "TemperatureRangeExtraction",
    "CAP-TIME-EXTRACT": "TimeSpecExtraction",
    "CAP-CATALOG-EXTRACT": "CatalogNumberExtraction",
    "CAP-QUANTITY-VALIDATE": "QuantityConsistencyValidation",
    "CAP-UNIT-CONSISTENCY": "UnitConsistencyValidation",
    "CAP-TABLE-TYPE-CLASSIFY": "TableTypeClassification",
    "CAP-TABLE-COLLAPSE-RECONSTRUCT": "CollapsedTableReconstruction",
    "CAP-ANCHOR-EXTRACT": "AnchorDrivenExtraction",
    "CAP-COLUMNAR-EXTRACT": "ColumnarTextExtraction",
    "CAP-NAME-QTY-PAIR": "NameQuantityPairExtraction",
    "CAP-UNSPSC-MATCH": "UnspscProductClassificationMatching",
}


class CapabilityLoader:
    """
    Exact Lookup Provider for Human-specified capability identities.

    Usage (Human-driven, per call):
        loader = CapabilityLoader()
        result = loader.load_capability("CAP-STORAGE-DETECT")
        if result.found:
            ref = result.capability_reference   # CapabilityReference (read-only)
        else:
            # result.lookup_status -> NOT_FOUND / INVALID_IDENTITY
            # result.reason_code  -> factual code (no action, no alternative)

    The Loader has EXACTLY ONE public method: load_capability().
    It has NO select/route/recommend/resolve/dispatch/rank/score methods.
    """

    # ── Factual lookup basis (read-only, frozen) ──
    LOOKUP_BASIS: str = "frozen_capability_table_v1"

    # ── Factual reason codes (observation only, NOT actions) ──
    RC_NOT_FOUND: str = "CAPABILITY_NOT_FOUND"
    RC_INVALID_IDENTITY: str = "INVALID_IDENTITY"
    RC_UNAVAILABLE: str = "CAPABILITY_UNAVAILABLE"

    def load_capability(self, capability_id: str) -> CapabilityLoadResult:
        """
        Resolve a Human-specified capability identity to a read-only reference.

        Exact Lookup Only (LDR-L1): the input must be an explicit, already-
        specified `capability_id`. This method performs a single exact
        membership check against the frozen table. It NEVER performs fuzzy
        matching, similarity search, ranking, scoring, recommendation,
        selection, routing, fallback, retry, activation, or execution.

        Args:
            capability_id: The exact capability identity Human specified.

        Returns:
            CapabilityLoadResult (observation):
                FOUND            -> capability_reference (readonly_reference)
                INVALID_IDENTITY -> malformed/empty identity (no reference)
                NOT_FOUND        -> well-formed but absent identity (no reference)
        """
        # 1. Identity format validation (exact identity, not a query/feature).
        if not self._is_valid_identity(capability_id):
            return self._failure(
                capability_id=capability_id,
                status=LookupStatus.INVALID_IDENTITY,
                reason_code=self.RC_INVALID_IDENTITY,
            )

        # 2. Exact lookup (membership check; NO fuzzy/similarity matching).
        name = FROZEN_CAPABILITY_TABLE.get(capability_id)
        if name is None:
            return self._failure(
                capability_id=capability_id,
                status=LookupStatus.NOT_FOUND,
                reason_code=self.RC_NOT_FOUND,
            )

        # 3. Resolve a read-only reference (reference, NOT an execution handle).
        return self._found(capability_id=capability_id, name=name)

    # ────────────────────────────────────────────────────────────────────
    # Private helpers (read-only, deterministic, no decision)
    # ────────────────────────────────────────────────────────────────────

    @staticmethod
    def _is_valid_identity(capability_id) -> bool:
        """True if the input is a non-empty string (exact identity required).

        This is a FORMAT check only (LDR-L1: exact identity required). It
        does NOT judge whether the identity is a "good" or "suitable"
        capability — only whether a well-formed identity was supplied.
        """
        return isinstance(capability_id, str) and bool(capability_id.strip())

    def _found(self, capability_id: str, name: str) -> CapabilityLoadResult:
        """Assemble a FOUND observation with a read-only reference."""
        metadata = CapabilityMetadata(name=name)
        reference = CapabilityReference(
            capability_id=capability_id,
            metadata=metadata,
            reference_kind="readonly_reference",  # NOT an execution handle / token
            parent=None,                          # invariant I-1: never anything else
            shadow_marked=True,                   # invariant I-2
            origin="composition_shadow_storage",  # invariant I-4
            is_hypothetical=True,                 # invariant I-3
            production_execution=False,           # invariant I-5: never True
        )
        return CapabilityLoadResult(
            capability_id=capability_id,
            lookup_status=LookupStatus.FOUND,
            capability_reference=reference,
            reason_code="",
            evidence_reference=(f"{self.LOOKUP_BASIS}#{capability_id}",),
            parent=None,
            shadow_marked=True,
            origin="composition_shadow_storage",
            is_hypothetical=True,
            production_execution=False,
        )

    @staticmethod
    def _failure(
        capability_id,
        status: LookupStatus,
        reason_code: str,
    ) -> CapabilityLoadResult:
        """Assemble a factual failure observation (report-only, no action).

        The failure is a pure observation: no retry, no fallback, no
        alternative selection, no routing, no activation (LDR-L2).
        """
        echoed_id = capability_id if isinstance(capability_id, str) else ""
        return CapabilityLoadResult(
            capability_id=echoed_id,
            lookup_status=status,
            capability_reference=None,
            reason_code=reason_code,
            evidence_reference=(),
            parent=None,
            shadow_marked=True,
            origin="composition_shadow_storage",
            is_hypothetical=True,
            production_execution=False,
        )
