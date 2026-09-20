"""
Phase 6.1-L2.2: ValidationExecutor — Logic (Phase C implemented).

Evaluates validation rules over collected evidence (read-only judgment).
Produces a ValidationResult — a pure observation, never an action.

Phase C implements ``evaluate_evidence()`` + supporting contract-driven
evaluators (4 generic evidence-structure evaluators). This module enforces:

    C-C1  Assessment Only    — produces Assessment, never approval/rejection
    C-C2  Evidence First     — every Assessment derives from ValidationEvidence
    C-C3  Rule Framework     — rules are Contract references; check_logic is
                               human-readable only, NEVER executed
    C-C4  Evaluator Boundary — 4 generic evaluators (ISOLATION/COVERAGE/
                               CONSISTENCY/BOUNDARY), no scenario branching
    C-C5  ValidationResult   — existing schema preserved, no new fields
    C-C6  Incremental Gate   — Implementation → Tests → Boundary → Review

Data chain (C-C2):
    Evidence → Assessment → ValidationResult

Forbidden:
    - ❌ approval / rejection / activation / production decision / capability decision
    - ❌ check_logic execution
    - ❌ scenario-specific if/else
    - ❌ severity-driven status / priority hidden gate
    - ❌ Production / Registry / Runtime / Storage access
    - ❌ execute_validation (out of Phase C scope)
    - ❌ ValidationResult / ValidationRule / ValidationEvidence model changes

Shadow guarantees:
    - shadow_marked = True on all artifacts
    - origin = "composition_shadow_storage"
    - is_hypothetical = True
"""

from __future__ import annotations

from time import perf_counter
from typing import Any, Dict, List, Optional

from .models import (
    CheckResult,
    RuleSeverity,
    RuleType,
    ValidationEvidence,
    ValidationResult,
    ValidationRule,
    ValidationStatus,
)


class ValidationExecutor:
    """Read-only rule executor (Shadow-only, Phase C implemented)."""

    SHADOW_ORIGIN: str = "composition_shadow_storage"

    # Status rank for worst-wins aggregation (FAIL > WARN > PASS).
    _STATUS_RANK: Dict[str, int] = {"PASS": 0, "WARN": 1, "FAIL": 2}
    _RANK_TO_STATUS: Dict[int, ValidationStatus] = {
        0: ValidationStatus.PASS,
        1: ValidationStatus.WARN,
        2: ValidationStatus.FAIL,
    }

    def __init__(self) -> None:
        self._initialized: bool = True
        # Contract-driven dispatch table (rule_type → generic evaluator).
        # Never scenario-specific; keyed by the 4 contract RuleType values.
        self._evaluators = {
            "isolation": self._evaluate_isolation,
            "coverage": self._evaluate_coverage,
            "consistency": self._evaluate_consistency,
            "boundary": self._evaluate_boundary,
        }

    # ── Public behavior method ──

    def evaluate_evidence(
        self,
        evidence: List[ValidationEvidence],
        rules: List[ValidationRule],
    ) -> ValidationResult:
        """Evaluate validation rules over collected evidence (read-only).

        Four logical steps (contract-driven, single FAIL never short-circuits):
            1. Rule dispatch (rule_type → generic evaluator).
            2. Per-rule assessment (each rule → CheckResult).
            3. Aggregate (worst status wins: FAIL > WARN > PASS).
            4. Candidate verdicts mapping (from evidence snapshots).

        Safe degradation (never raises):
            - non-list / None ``evidence`` or ``rules`` → empty result
            - empty ``evidence`` or empty ``rules`` → empty result (zero rules)

        Args:
            evidence: Collected ValidationEvidence (read-only copies).
            rules: ValidationRule definitions (contract-driven).

        Returns:
            ValidationResult (pure observation, never an action).
        """
        # ── Safe degradation: non-list / None inputs → empty result ──
        if not isinstance(evidence, (list, tuple)):
            evidence = []
        if not isinstance(rules, (list, tuple)):
            rules = []

        evidence_list: List[ValidationEvidence] = [
            e for e in evidence if isinstance(e, ValidationEvidence)
        ]
        rules_list: List[ValidationRule] = [
            r for r in rules if isinstance(r, ValidationRule)
        ]

        # ── Empty input → empty ValidationResult (zero rule execution) ──
        if not evidence_list or not rules_list:
            return self._empty_result()

        start = perf_counter()

        # Step 1-2: dispatch + per-rule assessment (single FAIL does not return early).
        check_results: List[CheckResult] = []
        for rule in rules_list:
            check_results.append(self._dispatch(rule, evidence_list))

        # Step 3: aggregate worst status.
        overall = self._aggregate(check_results)

        # Step 4: candidate verdicts mapping.
        candidate_verdicts = self._extract_candidate_verdicts(evidence_list)

        duration_ms = (perf_counter() - start) * 1000.0

        return self._build_result(
            check_results=check_results,
            overall_status=overall,
            request_id=self._extract_request_id(evidence_list),
            simulation_result_id=self._extract_simulation_result_id(evidence_list),
            candidate_verdicts=candidate_verdicts,
            duration_ms=duration_ms,
        )

    # ── Dispatch + generic evaluators ──

    def _dispatch(self, rule: ValidationRule, evidence: List[ValidationEvidence]) -> CheckResult:
        """Dispatch a rule to its generic evaluator by ``rule_type``.

        Unknown rule_type degrades safely to a WARN CheckResult (never raises,
        never short-circuits) — C-C4 evaluator boundary.
        """
        rule_type = self._normalize_rule_type(rule)
        evaluator = self._evaluators.get(rule_type or "")
        if evaluator is None:
            return self._unsupported_result(rule, rule_type)
        return evaluator(rule, evidence)

    def _evaluate_isolation(
        self, rule: ValidationRule, evidence: List[ValidationEvidence]
    ) -> CheckResult:
        """ISOLATION: shadow-marker integrity (structure only)."""
        violated = 0
        for ev in evidence:
            ok = (
                getattr(ev, "shadow_marked", False) is True
                and getattr(ev, "origin", "") == self.SHADOW_ORIGIN
                and getattr(ev, "is_hypothetical", False) is True
            )
            if not ok:
                violated += 1

        if violated == 0:
            status, message = "PASS", "all evidence satisfy shadow-marker isolation"
        elif violated == len(evidence):
            status, message = "FAIL", "shadow-marker violation (all evidence fail isolation)"
        else:
            status, message = "WARN", "partial shadow-marker degradation"

        return self._build_check_result(
            rule, status, message,
            {"violated": violated, "evidence_count": len(evidence)},
        )

    def _evaluate_coverage(
        self, rule: ValidationRule, evidence: List[ValidationEvidence]
    ) -> CheckResult:
        """COVERAGE: completeness (incomplete / missing_fields / expected count)."""
        incomplete = [ev for ev in evidence if getattr(ev, "incomplete", False)]
        if incomplete:
            missing = sorted({
                f for ev in incomplete
                for f in (getattr(ev, "missing_fields", []) or [])
            })
            message = "incomplete evidence detected"
            if missing:
                message += f": missing {missing}"
            return self._build_check_result(
                rule, "FAIL", message,
                {"missing_fields": missing, "incomplete_count": len(incomplete)},
            )

        expected = self._expected_count(rule)
        if expected is not None and len(evidence) < expected:
            message = f"evidence count {len(evidence)} below expected {expected}"
            return self._build_check_result(
                rule, "WARN", message,
                {"evidence_count": len(evidence), "expected_count": expected},
            )

        return self._build_check_result(
            rule, "PASS", "evidence coverage complete",
            {"evidence_count": len(evidence)},
        )

    def _evaluate_consistency(
        self, rule: ValidationRule, evidence: List[ValidationEvidence]
    ) -> CheckResult:
        """CONSISTENCY: request_id agreement + trace/result reference pairing."""
        request_ids = {
            getattr(ev, "request_id", "") for ev in evidence
            if getattr(ev, "request_id", "")
        }
        if len(request_ids) > 1:
            return self._build_check_result(
                rule, "FAIL", "request_id conflict across evidence",
                {"request_ids": sorted(request_ids)},
            )

        broken = [
            ev.evidence_id for ev in evidence
            if bool(getattr(ev, "source_trace_ref", ""))
            != bool(getattr(ev, "source_result_ref", ""))
        ]
        if broken:
            return self._build_check_result(
                rule, "FAIL", "broken trace/result reference pairing",
                {"broken_evidence": broken},
            )

        partial = [
            ev.evidence_id for ev in evidence
            if not getattr(ev, "request_id", "")
            or not getattr(ev, "source_trace_ref", "")
            or not getattr(ev, "source_result_ref", "")
        ]
        if partial:
            return self._build_check_result(
                rule, "WARN", "partial reference degradation",
                {"partial_evidence": partial},
            )

        return self._build_check_result(
            rule, "PASS", "evidence consistency holds",
            {"evidence_count": len(evidence)},
        )

    def _evaluate_boundary(
        self, rule: ValidationRule, evidence: List[ValidationEvidence]
    ) -> CheckResult:
        """BOUNDARY: zero Production/Registry reference (structure only)."""
        forbidden_tokens = ("production", "registry", "activation", "capability")
        for ev in evidence:
            origin = getattr(ev, "origin", "")
            if origin and origin != self.SHADOW_ORIGIN:
                return self._build_check_result(
                    rule, "FAIL", "boundary violation: non-shadow origin",
                    {"origin": origin},
                )
            snapshot = getattr(ev, "source_snapshot", {})
            if isinstance(snapshot, dict):
                for key in snapshot.keys():
                    key_lower = str(key).lower()
                    if any(tok in key_lower for tok in forbidden_tokens):
                        return self._build_check_result(
                            rule, "FAIL",
                            f"boundary violation: forbidden reference '{key}'",
                            {"field": key},
                        )
        return self._build_check_result(
            rule, "PASS", "no production/registry boundary violation",
            {"evidence_count": len(evidence)},
        )

    def _unsupported_result(
        self, rule: ValidationRule, rule_type: Optional[str]
    ) -> CheckResult:
        """WARN CheckResult for an unsupported rule_type (safe skip)."""
        return self._build_check_result(
            rule, "WARN",
            f"unsupported rule type '{rule_type or ''}' (safe skip, no assessment)",
            {"unsupported_rule_type": rule_type or ""},
        )

    # ── Aggregation + result construction ──

    def _aggregate(self, check_results: List[CheckResult]) -> ValidationStatus:
        """Worst-wins aggregation (FAIL > WARN > PASS)."""
        if not check_results:
            return ValidationStatus.PASS
        worst = max(self._STATUS_RANK.get(c.status, 0) for c in check_results)
        return self._RANK_TO_STATUS[worst]

    def _build_result(
        self,
        check_results: List[CheckResult],
        overall_status: ValidationStatus,
        request_id: str,
        simulation_result_id: str,
        candidate_verdicts: Dict[str, str],
        duration_ms: float,
    ) -> ValidationResult:
        """Assemble a ValidationResult with forced shadow markers (R-1~R-8)."""
        passed = sum(1 for c in check_results if c.status == "PASS")
        failed = sum(1 for c in check_results if c.status == "FAIL")
        warned = sum(1 for c in check_results if c.status == "WARN")
        return ValidationResult(
            request_id=request_id,
            simulation_result_id=simulation_result_id,
            overall_status=overall_status,
            total_rules=len(check_results),
            passed_rules=passed,
            failed_rules=failed,
            warned_rules=warned,
            check_results=check_results,
            candidate_verdicts=candidate_verdicts,
            duration_ms=duration_ms,
            shadow_marked=True,
            origin=self.SHADOW_ORIGIN,
            is_hypothetical=True,
        )

    def _empty_result(self) -> ValidationResult:
        """Empty ValidationResult (zero rule execution, zero fact generation)."""
        return ValidationResult(
            overall_status=ValidationStatus.PASS,
            total_rules=0,
            passed_rules=0,
            failed_rules=0,
            warned_rules=0,
            check_results=[],
            candidate_verdicts={},
            duration_ms=0.0,
            shadow_marked=True,
            origin=self.SHADOW_ORIGIN,
            is_hypothetical=True,
        )

    def _build_check_result(
        self,
        rule: ValidationRule,
        status: str,
        message: str,
        extra_details: Optional[Dict[str, Any]] = None,
    ) -> CheckResult:
        """Build a per-rule CheckResult (check_logic + severity as annotations)."""
        details: Dict[str, Any] = {
            "check_logic": getattr(rule, "check_logic", "") or "",
            "severity": self._severity_value(rule),
        }
        if extra_details:
            details.update(extra_details)
        return CheckResult(
            rule_id=getattr(rule, "rule_id", "") or "",
            rule_name=getattr(rule, "rule_name", "") or "",
            rule_type=self._normalize_rule_type(rule) or "",
            status=status,
            message=message,
            details=details,
        )

    # ── Pure extraction helpers ──

    @staticmethod
    def _normalize_rule_type(rule: ValidationRule) -> Optional[str]:
        """Normalize rule_type to a lowercase string (None if absent)."""
        rt = getattr(rule, "rule_type", None)
        if isinstance(rt, RuleType):
            return rt.value
        if isinstance(rt, str):
            return rt.strip().lower() or None
        return None

    @staticmethod
    def _severity_value(rule: ValidationRule) -> str:
        """Severity as an observation annotation (never drives status)."""
        sev = getattr(rule, "severity", None)
        if isinstance(sev, RuleSeverity):
            return sev.value
        return str(sev) if sev is not None else ""

    @staticmethod
    def _expected_count(rule: ValidationRule) -> Optional[int]:
        """Expected evidence count from rule params (None if absent)."""
        params = getattr(rule, "params", {}) or {}
        for key in ("expected_count", "candidate_count", "expected_evidence"):
            value = params.get(key)
            if isinstance(value, int) and not isinstance(value, bool):
                return value
        return None

    @staticmethod
    def _extract_request_id(evidence: List[ValidationEvidence]) -> str:
        """R-2: first non-empty request_id from evidence."""
        for ev in evidence:
            rid = getattr(ev, "request_id", "")
            if rid:
                return rid
        return ""

    @staticmethod
    def _extract_simulation_result_id(evidence: List[ValidationEvidence]) -> str:
        """R-3: source_result_ref first, then snapshot simulation_result_id."""
        for ev in evidence:
            ref = getattr(ev, "source_result_ref", "")
            if ref:
                return ref
        for ev in evidence:
            snapshot = getattr(ev, "source_snapshot", {})
            if isinstance(snapshot, dict):
                for key in ("simulation_result_id", "result_id"):
                    value = snapshot.get(key)
                    if value:
                        return str(value)
        return ""

    @staticmethod
    def _extract_candidate_verdicts(
        evidence: List[ValidationEvidence],
    ) -> Dict[str, str]:
        """R-7: candidate verdicts from evidence snapshots (observation only)."""
        verdicts: Dict[str, str] = {}
        for ev in evidence:
            snapshot = getattr(ev, "source_snapshot", {})
            if not isinstance(snapshot, dict):
                continue
            cv = snapshot.get("candidate_verdicts")
            if isinstance(cv, dict):
                for k, v in cv.items():
                    verdicts[str(k)] = str(v)
            cands = snapshot.get("candidates")
            if isinstance(cands, list):
                for c in cands:
                    if isinstance(c, dict):
                        cid = c.get("candidate_id") or c.get("id")
                        cstatus = c.get("status") or c.get("verdict")
                        if cid is not None:
                            verdicts[str(cid)] = str(cstatus)
        return verdicts

    def __repr__(self) -> str:
        return (
            f"ValidationExecutor(initialized={self._initialized}, "
            f"status=IMPLEMENTED_PHASE_C)"
        )
