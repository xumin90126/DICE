"""
Phase 6.1-L2.2: ValidationContract — Logic (Phase A implemented).

Defines and validates the Validation input/output contract. Pure
contract checking — no side effects, no write operations.

This module enforces the C4 Rule Governance Boundary by keeping the
contract declarative (never scenario-specific if/else accumulation,
never hard-coded business decisions).

Phase A implements ``validate_contract()`` + supporting schema
validation helpers. The remaining 6 behavior methods across other
modules stay ``NotImplementedError`` (Phase B-F pending).

Forbidden:
    - ❌ Any Runtime dependency
    - ❌ Any write operation
    - ❌ Hard-coded business decisions

Shadow guarantees:
    - shadow_marked = True on all artifacts
    - origin = "composition_shadow_storage"
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .models import ValidationRequest, ValidationStatus

# Input Contract version (aligned with Schema v1.0).
CONTRACT_VERSION = "1.0"

# Input Contract 默认必填字段（最小契约集）。
DEFAULT_REQUIRED_FIELDS: Tuple[str, ...] = (
    "request_id",
    "simulation_result_id",
    "candidate_count",
    "status",
)

# 可选源引用字段（ID-based 只读引用；空值合法）。
# simulation_result_id 已作为必填字段检查，此处不再重复。
SOURCE_REFERENCE_FIELDS: Tuple[str, ...] = (
    "observation_id",
    "document_id",
)


class ValidationContract:
    """Contract validator (Shadow-only, Phase A implemented)."""

    def __init__(self) -> None:
        self._initialized: bool = True

    # ── Public contract entry point ──

    def validate_contract(
        self,
        request: ValidationRequest,
        contract_spec: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Validate the Validation input/output contract.

        Checks (contract-driven, pure observation, zero side effects):
            1. Field completeness   (required fields present + well-typed)
            2. Source references    (optional ID-only references valid)
            3. Shadow markers       (shadow_marked / origin / is_hypothetical)

        Args:
            request: ValidationRequest whose contract fields are checked.
            contract_spec: Optional override of required fields / strict mode.

        Returns:
            Dict with ``passed`` (bool), ``violations`` (list of structured
            dicts), ``checked_fields`` (list), and ``contract_version``.
        """
        violations: List[Dict[str, Any]] = []
        checked_fields: List[str] = []

        spec = self._normalize_contract_spec(contract_spec)

        # ── Safe degradation on a null request (contract cannot pass) ──
        if request is None:
            violations.append(
                self._violation("required_field", "request", "request is None", "error")
            )
            return {
                "passed": False,
                "violations": violations,
                "checked_fields": ["request"],
                "contract_version": spec["contract_version"],
            }

        self._check_required_fields(
            request, spec["required_fields"], violations, checked_fields
        )
        self._check_source_references(
            request, spec["strict"], violations, checked_fields
        )
        self._check_shadow_markers(request, violations, checked_fields)

        passed = not self._has_blocking_violation(violations, spec["strict"])

        return {
            "passed": passed,
            "violations": violations,
            "checked_fields": checked_fields,
            "contract_version": spec["contract_version"],
        }

    # ── Supporting schema validation helpers ──

    def _normalize_contract_spec(
        self, contract_spec: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Normalize a contract spec into canonical form.

        Returns a dict with ``required_fields`` (tuple), ``strict`` (bool),
        and ``contract_version`` (str). Missing / malformed values degrade
        to contract defaults — no exception escapes the shadow boundary.
        """
        if not isinstance(contract_spec, dict):
            contract_spec = {}

        required = contract_spec.get("required_fields")
        if not isinstance(required, (list, tuple)):
            required = list(DEFAULT_REQUIRED_FIELDS)
        else:
            # Keep only string field names (filter non-string noise).
            required = [f for f in required if isinstance(f, str)]

        version = contract_spec.get("contract_version", CONTRACT_VERSION)
        return {
            "required_fields": tuple(required),
            "strict": bool(contract_spec.get("strict", False)),
            "contract_version": str(version),
        }

    def _check_required_fields(
        self,
        request: ValidationRequest,
        required_fields: Tuple[str, ...],
        violations: List[Dict[str, Any]],
        checked_fields: List[str],
    ) -> None:
        """Check required field completeness + well-typedness.

        - request_id: non-empty string
        - simulation_result_id: non-empty string (source reference)
        - candidate_count: int >= 0 (bool excluded)
        - status: a ValidationStatus value
        """
        for field in required_fields:
            checked_fields.append(field)
            if field == "request_id":
                value = getattr(request, "request_id", "")
                if not isinstance(value, str) or not value.strip():
                    violations.append(
                        self._violation(
                            "required_field", field, "missing or empty string", "error"
                        )
                    )
            elif field == "simulation_result_id":
                value = getattr(request, "simulation_result_id", "")
                if not isinstance(value, str) or not value.strip():
                    violations.append(
                        self._violation(
                            "required_field",
                            field,
                            "missing or empty source reference",
                            "error",
                        )
                    )
            elif field == "candidate_count":
                value = getattr(request, "candidate_count", None)
                if (
                    isinstance(value, bool)
                    or not isinstance(value, int)
                    or value < 0
                ):
                    violations.append(
                        self._violation(
                            "required_field",
                            field,
                            "must be a non-negative integer",
                            "error",
                        )
                    )
            elif field == "status":
                value = getattr(request, "status", None)
                if not self._is_valid_status(value):
                    violations.append(
                        self._violation(
                            "required_field", field, "invalid validation status", "error"
                        )
                    )

    def _check_source_references(
        self,
        request: ValidationRequest,
        strict: bool,
        violations: List[Dict[str, Any]],
        checked_fields: List[str],
    ) -> None:
        """Check optional ID-only source references are well-typed strings.

        Empty / None references are legal (optional). A non-string value is
        a ``warning`` in lenient mode and an ``error`` in strict mode.
        """
        for field in SOURCE_REFERENCE_FIELDS:
            checked_fields.append(field)
            value = getattr(request, field, "")
            if value is None or value == "":
                continue
            if not isinstance(value, str):
                severity = "error" if strict else "warning"
                violations.append(
                    self._violation(
                        "source_reference",
                        field,
                        "must be a string reference",
                        severity,
                    )
                )

    def _check_shadow_markers(
        self,
        request: ValidationRequest,
        violations: List[Dict[str, Any]],
        checked_fields: List[str],
    ) -> None:
        """Check shadow markers are correctly set (C1 / C2 / C3).

        - shadow_marked is True
        - origin == "composition_shadow_storage"
        - is_hypothetical is True
        """
        checked_fields.extend(["shadow_marked", "origin", "is_hypothetical"])

        if getattr(request, "shadow_marked", False) is not True:
            violations.append(
                self._violation("shadow_marker", "shadow_marked", "must be True", "error")
            )
        if getattr(request, "origin", "") != "composition_shadow_storage":
            violations.append(
                self._violation(
                    "shadow_marker",
                    "origin",
                    "must be composition_shadow_storage",
                    "error",
                )
            )
        if getattr(request, "is_hypothetical", False) is not True:
            violations.append(
                self._violation(
                    "shadow_marker", "is_hypothetical", "must be True", "error"
                )
            )

    # ── Pure helpers ──

    @staticmethod
    def _violation(
        check: str, field: str, reason: str, severity: str
    ) -> Dict[str, Any]:
        """Build a structured violation record (pure, no side effects)."""
        return {
            "check": check,
            "field": field,
            "reason": reason,
            "severity": severity,
        }

    @staticmethod
    def _is_valid_status(value: Any) -> bool:
        """Return True if ``value`` is a valid ValidationStatus."""
        if isinstance(value, ValidationStatus):
            return True
        if isinstance(value, str):
            return value in {s.value for s in ValidationStatus}
        return False

    @staticmethod
    def _has_blocking_violation(
        violations: List[Dict[str, Any]], strict: bool
    ) -> bool:
        """Return True if any violation blocks the contract.

        An ``error`` violation always blocks. A ``warning`` violation blocks
        only under strict mode.
        """
        for v in violations:
            if v["severity"] == "error":
                return True
            if strict and v["severity"] == "warning":
                return True
        return False

    def __repr__(self) -> str:
        return f"ValidationContract(initialized={self._initialized}, status=IMPLEMENTED_PHASE_A)"
