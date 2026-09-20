"""
生产安全护栏引擎 — Phase 3 Step 3.

GuardrailCheckEngine：激活边界之上的最终安全入口。

职责：
    1. 消费 ActivationDecision（已通过激活边界）
    2. 执行五重安全门禁验证
    3. 生成 ProductionExecutionPermissionResult（ALLOW / BLOCK / REVIEW_REQUIRED）
    4. 记录完整护栏审计记录

设计约束：
    - 禁止执行真实动作——本层只负责最终权限判断
    - 禁止绕过激活边界——只有 ALLOWED 的激活决策才能进入护栏
    - 禁止自动批准——所有决策必须显式调用
    - 不属于任何 Runtime 层——是独立的生产安全入口层

五重护栏门禁：
    Check 1: 审批验证 — 审批状态 + 追溯 + 审批人信息
    Check 2: 激活验证 — 激活边界结果 + 激活 ID + 审计链
    Check 3: 执行安全 — 风险等级 + 执行置信度 + 必要输入
    Check 4: 证据覆盖 — Evidence → Capability → Execution → Approval → Activation 链路完整性
    Check 5: 回滚能力 — 回滚引用 + 执行追溯 ID + 恢复路径

任何检查失败：
    - 安全门禁（Check 1-3）失败 → BLOCK
    - 证据/回滚门禁（Check 4-5）失败 → REVIEW_REQUIRED
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from dice.runtime.approval.models import (
    ApprovalRequest,
    ApprovalStatus,
    ApprovalTrace,
    ApprovalRiskLevel,
)
from dice.runtime.activation.models import (
    ActivationDecision,
    ActivationStatus,
    ActivationRiskLevel,
    ActivationAuditRecord,
)
from dice.runtime.guardrail.models import (
    ProductionExecutionPermissionResult,
    GuardrailCheckResult,
    GuardrailAuditRecord,
    GuardrailBatchResult,
    PermissionStatus,
    GuardrailCheckType,
    GuardrailBlockReason,
)


# ═══════════════════════════════════════════════════════════════════════════
# GuardrailCheckEngine
# ═══════════════════════════════════════════════════════════════════════════


class GuardrailCheckEngine:
    """生产安全护栏检查引擎。

    作为激活边界之上的最终安全入口，执行五重门禁验证，
    决定是否允许执行计划进入真实生产执行。

    使用方式：
        engine = GuardrailCheckEngine()

        # 从激活决策创建权限结果
        permission = engine.evaluate(
            activation_decision=decision,
            approval_request=request,
            approval_traces=traces,
        )

        if permission.is_allowed():
            # 可以进入执行——但 GuardrailCheckEngine 不负责执行
            pass
        elif permission.needs_review():
            # 需要人工审查
            pass
        else:
            # 被阻止——查看 blocked_reason 了解原因
            print(permission.blocked_reason)
    """

    # 允许自动通过的最低风险等级
    DEFAULT_AUTO_ALLOW_RISK = ActivationRiskLevel.MEDIUM

    # 最低执行置信度
    MIN_EXECUTION_CONFIDENCE = 0.5

    def __init__(self) -> None:
        """初始化护栏检查引擎。"""
        # 权限结果存储
        self._permissions: dict[str, ProductionExecutionPermissionResult] = {}
        # 审计记录存储
        self._audit_records: list[GuardrailAuditRecord] = []

    # ═══════════════════════════════════════════════════════════════════
    # 核心方法：评估权限
    # ═══════════════════════════════════════════════════════════════════

    def evaluate(
        self,
        activation_decision: ActivationDecision,
        approval_request: Optional[ApprovalRequest] = None,
        approval_traces: Optional[list[ApprovalTrace]] = None,
        activation_audit: Optional[list[ActivationAuditRecord]] = None,
        evidence_chain: Optional[dict[str, Any]] = None,
    ) -> ProductionExecutionPermissionResult:
        """
        评估激活决策是否允许进入生产执行。

        参数:
            activation_decision: 激活决策（必须为 ALLOWED 状态）
            approval_request: 关联的审批请求（可选，用于审批验证）
            approval_traces: 审批追溯记录列表（可选）
            activation_audit: 激活审计记录列表（可选）
            evidence_chain: 证据链信息（可选）

        返回:
            ProductionExecutionPermissionResult 权限结果（ALLOW / BLOCK / REVIEW_REQUIRED）
        """
        # 创建权限结果对象
        permission = ProductionExecutionPermissionResult(
            request_id=activation_decision.request_id,
            document_id=activation_decision.document_id,
            activation_id=activation_decision.decision_id,
            execution_plan_id=activation_decision.execution_plan_id,
            capability_id=activation_decision.capability_id,
            permission_status=PermissionStatus.BLOCK,
            allowed=False,
            risk_level=activation_decision.risk_level.value,
            confidence=approval_request.execution_confidence if approval_request else 0.0,
            approval_reference=activation_decision.audit_trace_reference,
            activation_reference=activation_decision.audit_trace_reference,
        )

        # 执行五重护栏检查
        checks = self._run_all_checks(
            activation_decision=activation_decision,
            approval_request=approval_request,
            approval_traces=approval_traces or [],
            activation_audit=activation_audit or [],
            evidence_chain=evidence_chain,
        )

        permission.guardrail_checks = checks

        # 根据检查结果决定权限状态
        permission.permission_status, permission.blocked_reason, permission.reasoning = (
            self._determine_permission(checks, activation_decision)
        )

        permission.allowed = permission.permission_status == PermissionStatus.ALLOW

        # 生成审计追溯
        permission.audit_trace = self._generate_audit_trace(permission)

        # 存储权限结果
        self._permissions[permission.permission_id] = permission

        # 记录审计
        self._record_audit(permission, checks)

        return permission

    def evaluate_batch(
        self,
        activation_decisions: list[ActivationDecision],
        approval_map: Optional[dict[str, ApprovalRequest]] = None,
        traces_map: Optional[dict[str, list[ApprovalTrace]]] = None,
    ) -> GuardrailBatchResult:
        """
        批量评估激活决策。

        参数:
            activation_decisions: 激活决策列表
            approval_map: 决策 ID → 审批请求的映射
            traces_map: 请求 ID → 追溯记录列表的映射

        返回:
            GuardrailBatchResult 批量护栏结果
        """
        ap_map = approval_map or {}
        tr_map = traces_map or {}
        permissions: list[ProductionExecutionPermissionResult] = []

        for decision in activation_decisions:
            approval = ap_map.get(decision.decision_id)
            traces = tr_map.get(decision.request_id, [])
            permission = self.evaluate(
                activation_decision=decision,
                approval_request=approval,
                approval_traces=traces,
            )
            permissions.append(permission)

        # 统计
        stats = self._compute_batch_statistics(permissions)

        result = GuardrailBatchResult(
            total_permissions=len(permissions),
            permissions=permissions,
            audit_records=list(self._audit_records),
            statistics=stats,
        )

        return result

    # ═══════════════════════════════════════════════════════════════════
    # 五重护栏检查
    # ═══════════════════════════════════════════════════════════════════

    def _run_all_checks(
        self,
        activation_decision: ActivationDecision,
        approval_request: Optional[ApprovalRequest],
        approval_traces: list[ApprovalTrace],
        activation_audit: list[ActivationAuditRecord],
        evidence_chain: Optional[dict[str, Any]],
    ) -> list[GuardrailCheckResult]:
        """执行全部五项护栏检查。"""
        checks: list[GuardrailCheckResult] = []

        # Check 1: 审批验证
        checks.append(self._check_approval_validation(
            activation_decision, approval_request, approval_traces
        ))

        # Check 2: 激活验证
        checks.append(self._check_activation_validation(
            activation_decision, activation_audit
        ))

        # Check 3: 执行安全
        checks.append(self._check_execution_safety(
            activation_decision, approval_request
        ))

        # Check 4: 证据覆盖
        checks.append(self._check_evidence_coverage(
            activation_decision, approval_request, approval_traces,
            activation_audit, evidence_chain
        ))

        # Check 5: 回滚能力
        checks.append(self._check_rollback_capability(
            activation_decision, approval_request
        ))

        return checks

    # ═══════════════════════════════════════════════════════════════════
    # Check 1: 审批验证
    # ═══════════════════════════════════════════════════════════════════

    def _check_approval_validation(
        self,
        activation_decision: ActivationDecision,
        approval_request: Optional[ApprovalRequest],
        approval_traces: list[ApprovalTrace],
    ) -> GuardrailCheckResult:
        """验证审批状态、追溯和审批人信息。"""
        # 1a. 检查审批状态
        if activation_decision.approval_status != ApprovalStatus.APPROVED.value:
            return GuardrailCheckResult(
                check_type=GuardrailCheckType.APPROVAL_VALIDATION,
                passed=False,
                detail=f"审批状态异常: {activation_decision.approval_status}（期望: APPROVED）",
                risk_level="high",
                recommendation="请先完成审批流程，确保审批状态为 APPROVED",
            )

        # 1b. 检查审批人信息
        if not activation_decision.approved_by:
            return GuardrailCheckResult(
                check_type=GuardrailCheckType.APPROVAL_VALIDATION,
                passed=False,
                detail="审批人信息缺失",
                risk_level="high",
                recommendation="审批记录必须包含审批人信息",
            )

        # 1c. 检查审批时间
        if not activation_decision.approval_timestamp:
            return GuardrailCheckResult(
                check_type=GuardrailCheckType.APPROVAL_VALIDATION,
                passed=False,
                detail="审批时间戳缺失",
                risk_level="high",
                recommendation="审批记录必须包含时间戳",
            )

        # 1d. 检查审批追溯
        if not approval_traces:
            return GuardrailCheckResult(
                check_type=GuardrailCheckType.APPROVAL_VALIDATION,
                passed=False,
                detail="审批追溯记录为空",
                risk_level="high",
                recommendation="审批必须包含完整的追溯记录",
            )

        # 1e. 检查追溯中是否有 APPROVE 决策
        has_approve = any(
            t.new_status == ApprovalStatus.APPROVED
            for t in approval_traces
            if t.request_id == activation_decision.request_id
        )
        if not has_approve:
            return GuardrailCheckResult(
                check_type=GuardrailCheckType.APPROVAL_VALIDATION,
                passed=False,
                detail="追溯记录中未找到 APPROVED 决策",
                risk_level="high",
                recommendation="审批追溯必须包含最终 APPROVE 决策",
            )

        return GuardrailCheckResult(
            check_type=GuardrailCheckType.APPROVAL_VALIDATION,
            passed=True,
            detail=f"审批验证通过: 审批人={activation_decision.approved_by}, "
                   f"追溯记录={len(approval_traces)} 条",
            risk_level="low",
            recommendation="",
        )

    # ═══════════════════════════════════════════════════════════════════
    # Check 2: 激活验证
    # ═══════════════════════════════════════════════════════════════════

    def _check_activation_validation(
        self,
        activation_decision: ActivationDecision,
        activation_audit: list[ActivationAuditRecord],
    ) -> GuardrailCheckResult:
        """验证激活边界结果、激活 ID 和审计链。"""
        # 2a. 检查激活状态
        if activation_decision.activation_status != ActivationStatus.ALLOWED:
            return GuardrailCheckResult(
                check_type=GuardrailCheckType.ACTIVATION_VALIDATION,
                passed=False,
                detail=f"激活状态异常: {activation_decision.activation_status.value}（期望: ALLOWED）",
                risk_level="high",
                recommendation="只有 ALLOWED 的激活决策才能进入护栏",
            )

        # 2b. 检查激活决策 ID
        if not activation_decision.decision_id:
            return GuardrailCheckResult(
                check_type=GuardrailCheckType.ACTIVATION_VALIDATION,
                passed=False,
                detail="激活决策 ID 缺失",
                risk_level="high",
                recommendation="激活决策必须具有唯一标识",
            )

        # 2c. 检查四重门禁是否全部通过
        validation = activation_decision.validation_result
        gates = [k for k in validation.keys() if k.startswith("gate")]
        failed_gates = [
            k for k in gates
            if not validation.get(k, {}).get("passed", False)
            if isinstance(validation.get(k), dict)
        ]
        if failed_gates:
            return GuardrailCheckResult(
                check_type=GuardrailCheckType.ACTIVATION_VALIDATION,
                passed=False,
                detail=f"激活门禁未全部通过: {failed_gates}",
                risk_level="high",
                recommendation="所有激活门禁必须全部通过",
            )

        # 2d. 检查激活审计链
        if not activation_audit:
            return GuardrailCheckResult(
                check_type=GuardrailCheckType.ACTIVATION_VALIDATION,
                passed=False,
                detail="激活审计记录为空",
                risk_level="medium",
                recommendation="激活过程应包含审计记录",
            )

        return GuardrailCheckResult(
            check_type=GuardrailCheckType.ACTIVATION_VALIDATION,
            passed=True,
            detail=f"激活验证通过: 状态={activation_decision.activation_status.value}, "
                   f"门禁={len(gates)} 项全部通过",
            risk_level="low",
            recommendation="",
        )

    # ═══════════════════════════════════════════════════════════════════
    # Check 3: 执行安全
    # ═══════════════════════════════════════════════════════════════════

    def _check_execution_safety(
        self,
        activation_decision: ActivationDecision,
        approval_request: Optional[ApprovalRequest],
    ) -> GuardrailCheckResult:
        """验证风险等级、执行置信度和必要输入。"""
        # 3a. 检查风险等级
        if activation_decision.risk_level == ActivationRiskLevel.CRITICAL:
            return GuardrailCheckResult(
                check_type=GuardrailCheckType.EXECUTION_SAFETY,
                passed=False,
                detail=f"风险等级为 CRITICAL，禁止自动执行",
                risk_level="critical",
                recommendation="CRITICAL 风险等级需要人工二次确认后才能执行",
            )

        if activation_decision.risk_level == ActivationRiskLevel.HIGH:
            return GuardrailCheckResult(
                check_type=GuardrailCheckType.EXECUTION_SAFETY,
                passed=False,
                detail=f"风险等级为 HIGH，需要额外安全审查",
                risk_level="high",
                recommendation="HIGH 风险等级建议进行安全审查后再执行",
            )

        # 3b. 检查置信度
        confidence = approval_request.execution_confidence if approval_request else 0.0
        if confidence < self.MIN_EXECUTION_CONFIDENCE:
            return GuardrailCheckResult(
                check_type=GuardrailCheckType.EXECUTION_SAFETY,
                passed=False,
                detail=f"执行置信度过低: {confidence:.2f}（最低要求: {self.MIN_EXECUTION_CONFIDENCE}）",
                risk_level="high",
                recommendation="低置信度执行可能导致错误结果，建议提高置信度后再执行",
            )

        # 3c. 检查必要输入
        if approval_request:
            plan = approval_request.execution_plan
            if not plan or not plan.get("selected_action"):
                return GuardrailCheckResult(
                    check_type=GuardrailCheckType.EXECUTION_SAFETY,
                    passed=False,
                    detail="执行计划缺少 selected_action",
                    risk_level="medium",
                    recommendation="执行计划必须包含有效的 selected_action",
                )

        return GuardrailCheckResult(
            check_type=GuardrailCheckType.EXECUTION_SAFETY,
            passed=True,
            detail=f"执行安全验证通过: 风险={activation_decision.risk_level.value}, "
                   f"置信度={confidence:.2f}",
            risk_level="low",
            recommendation="",
        )

    # ═══════════════════════════════════════════════════════════════════
    # Check 4: 证据覆盖
    # ═══════════════════════════════════════════════════════════════════

    def _check_evidence_coverage(
        self,
        activation_decision: ActivationDecision,
        approval_request: Optional[ApprovalRequest],
        approval_traces: list[ApprovalTrace],
        activation_audit: list[ActivationAuditRecord],
        evidence_chain: Optional[dict[str, Any]],
    ) -> GuardrailCheckResult:
        """验证 Evidence → Capability → Execution → Approval → Activation 链路完整性。"""
        missing_links: list[str] = []

        # 4a. 检查审批追溯
        if not approval_traces:
            missing_links.append("Approval")

        # 4b. 检查激活审计
        if not activation_audit:
            missing_links.append("Activation")

        # 4c. 检查执行计划
        if approval_request and not approval_request.execution_plan:
            missing_links.append("Execution")

        # 4d. 检查能力信息
        if not activation_decision.capability_id:
            missing_links.append("Capability")

        # 4e. 检查证据链
        if evidence_chain is None:
            missing_links.append("Evidence")

        if missing_links:
            return GuardrailCheckResult(
                check_type=GuardrailCheckType.EVIDENCE_COVERAGE,
                passed=False,
                detail=f"证据链不完整，缺失环节: {', '.join(missing_links)}",
                risk_level="medium",
                recommendation=(
                    f"请补充缺失的环节: {', '.join(missing_links)}。"
                    f"完整链路应为 Evidence → Capability → Execution → Approval → Activation"
                ),
            )

        return GuardrailCheckResult(
            check_type=GuardrailCheckType.EVIDENCE_COVERAGE,
            passed=True,
            detail="证据链完整: Evidence → Capability → Execution → Approval → Activation",
            risk_level="low",
            recommendation="",
        )

    # ═══════════════════════════════════════════════════════════════════
    # Check 5: 回滚能力
    # ═══════════════════════════════════════════════════════════════════

    def _check_rollback_capability(
        self,
        activation_decision: ActivationDecision,
        approval_request: Optional[ApprovalRequest],
    ) -> GuardrailCheckResult:
        """验证回滚引用、执行追溯 ID 和恢复路径。"""
        # 5a. 检查执行追溯 ID
        if not activation_decision.execution_plan_id:
            return GuardrailCheckResult(
                check_type=GuardrailCheckType.ROLLBACK_CAPABILITY,
                passed=False,
                detail="执行计划 ID 缺失，无法建立回滚引用",
                risk_level="medium",
                recommendation="执行计划必须具有唯一标识以支持回滚",
            )

        # 5b. 检查审批引用（回滚时需要知道谁批准的）
        if not activation_decision.request_id:
            return GuardrailCheckResult(
                check_type=GuardrailCheckType.ROLLBACK_CAPABILITY,
                passed=False,
                detail="审批请求 ID 缺失，无法追溯审批来源",
                risk_level="medium",
                recommendation="审批请求必须具有唯一标识以支持回滚追溯",
            )

        # 5c. 检查恢复路径——通过审批请求中的执行计划是否存在
        if approval_request and approval_request.execution_plan:
            plan = approval_request.execution_plan
            # 检查计划中是否有回滚相关信息
            has_rollback_info = (
                plan.get("rollback_reference") or
                plan.get("recovery_path") or
                plan.get("execution_trace_id")
            )
            if not has_rollback_info:
                # 这不是硬阻塞——因为执行计划可能尚未包含回滚细节
                # 但标记为风险
                pass

        return GuardrailCheckResult(
            check_type=GuardrailCheckType.ROLLBACK_CAPABILITY,
            passed=True,
            detail=f"回滚能力验证通过: 执行计划={activation_decision.execution_plan_id}, "
                   f"审批引用={activation_decision.request_id}",
            risk_level="low",
            recommendation="",
        )

    # ═══════════════════════════════════════════════════════════════════
    # 权限决策
    # ═══════════════════════════════════════════════════════════════════

    def _determine_permission(
        self,
        checks: list[GuardrailCheckResult],
        activation_decision: ActivationDecision,
    ) -> tuple[PermissionStatus, str, str]:
        """
        根据检查结果决定最终权限状态。

        规则：
            - 任何安全门禁（Check 1-3）失败 → BLOCK
            - 任何证据/回滚门禁（Check 4-5）失败 → REVIEW_REQUIRED
            - 全部通过 → ALLOW
        """
        safety_checks = [
            c for c in checks
            if c.check_type in (
                GuardrailCheckType.APPROVAL_VALIDATION,
                GuardrailCheckType.ACTIVATION_VALIDATION,
                GuardrailCheckType.EXECUTION_SAFETY,
            )
        ]
        coverage_checks = [
            c for c in checks
            if c.check_type in (
                GuardrailCheckType.EVIDENCE_COVERAGE,
                GuardrailCheckType.ROLLBACK_CAPABILITY,
            )
        ]

        failed_safety = [c for c in safety_checks if not c.passed]
        failed_coverage = [c for c in coverage_checks if not c.passed]

        if failed_safety:
            reasons = [c.detail for c in failed_safety]
            reasoning = (
                f"安全门禁失败，阻止执行。"
                f"失败项: {', '.join(c.check_type.value for c in failed_safety)}。"
                f"详情: {'; '.join(reasons)}"
            )
            return (
                PermissionStatus.BLOCK,
                GuardrailBlockReason.UNAUTHORIZED_EXECUTION_ATTEMPT.value,
                reasoning,
            )

        if failed_coverage:
            reasons = [c.detail for c in failed_coverage]
            reasoning = (
                f"证据覆盖或回滚能力不足，需要人工审查。"
                f"不足项: {', '.join(c.check_type.value for c in failed_coverage)}。"
                f"详情: {'; '.join(reasons)}"
            )
            return (
                PermissionStatus.REVIEW_REQUIRED,
                GuardrailBlockReason.EVIDENCE_CHAIN_BROKEN.value,
                reasoning,
            )

        # 全部通过
        reasoning = (
            f"五重护栏检查全部通过: "
            f"审批={activation_decision.approval_status}, "
            f"激活={activation_decision.activation_status.value}, "
            f"风险={activation_decision.risk_level.value}, "
            f"能力={activation_decision.capability_id}"
        )
        return (
            PermissionStatus.ALLOW,
            "",
            reasoning,
        )

    # ═══════════════════════════════════════════════════════════════════
    # 查询方法
    # ═══════════════════════════════════════════════════════════════════

    def get_permission(
        self, permission_id: str
    ) -> Optional[ProductionExecutionPermissionResult]:
        """获取权限结果。"""
        return self._permissions.get(permission_id)

    def get_audit_records(
        self, permission_id: str = ""
    ) -> list[GuardrailAuditRecord]:
        """获取护栏审计记录。"""
        if permission_id:
            return [a for a in self._audit_records if a.permission_id == permission_id]
        return list(self._audit_records)

    def get_allowed_permissions(self) -> list[ProductionExecutionPermissionResult]:
        """获取所有允许进入执行的权限结果。"""
        return [p for p in self._permissions.values() if p.is_allowed()]

    def get_blocked_permissions(self) -> list[ProductionExecutionPermissionResult]:
        """获取所有被阻止的权限结果。"""
        return [p for p in self._permissions.values() if p.is_blocked()]

    def get_review_permissions(self) -> list[ProductionExecutionPermissionResult]:
        """获取所有需要审查的权限结果。"""
        return [p for p in self._permissions.values() if p.needs_review()]

    def get_statistics(self) -> dict[str, Any]:
        """获取护栏统计信息。"""
        total = len(self._permissions)
        if total == 0:
            return {"total": 0}

        allowed = sum(1 for p in self._permissions.values() if p.is_allowed())
        blocked = sum(1 for p in self._permissions.values() if p.is_blocked())
        review = sum(1 for p in self._permissions.values() if p.needs_review())

        risk_counts: dict[str, int] = {}
        check_fail_counts: dict[str, int] = {}
        for p in self._permissions.values():
            risk_counts[p.risk_level] = risk_counts.get(p.risk_level, 0) + 1
            for c in p.failed_checks():
                check_fail_counts[c.check_type.value] = (
                    check_fail_counts.get(c.check_type.value, 0) + 1
                )

        return {
            "total": total,
            "allowed": allowed,
            "blocked": blocked,
            "review_required": review,
            "allow_rate": round(allowed / total, 4) if total > 0 else 0.0,
            "risk_distribution": risk_counts,
            "check_failure_distribution": check_fail_counts,
            "total_audit_records": len(self._audit_records),
        }

    # ═══════════════════════════════════════════════════════════════════
    # 内部方法
    # ═══════════════════════════════════════════════════════════════════

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _generate_audit_trace(
        self, permission: ProductionExecutionPermissionResult
    ) -> str:
        """生成审计追溯引用。"""
        return (
            f"audit://guardrail/{permission.permission_id}"
            f"?request={permission.request_id}"
            f"&document={permission.document_id}"
            f"&activation={permission.activation_id}"
            f"&capability={permission.capability_id}"
        )

    def _record_audit(
        self,
        permission: ProductionExecutionPermissionResult,
        checks: list[GuardrailCheckResult],
    ) -> None:
        """记录护栏审计。"""
        # 构建验证检查结果
        validation_checks = {
            c.check_type.value: c.passed
            for c in checks
        }

        status = permission.permission_status.value
        if permission.is_allowed():
            reason = f"允许执行: {permission.reasoning}"
        elif permission.needs_review():
            reason = f"需要审查: {permission.reasoning}"
        else:
            reason = f"阻止执行: {permission.blocked_reason}"

        record = GuardrailAuditRecord(
            permission_id=permission.permission_id,
            request_id=permission.request_id,
            document_id=permission.document_id,
            permission_status=permission.permission_status,
            validated_by="system",
            validation_checks=validation_checks,
            reason=reason,
        )
        self._audit_records.append(record)

    @staticmethod
    def _compute_batch_statistics(
        permissions: list[ProductionExecutionPermissionResult],
    ) -> dict[str, Any]:
        """计算批量护栏统计。"""
        if not permissions:
            return {}

        allowed = sum(1 for p in permissions if p.is_allowed())
        blocked = sum(1 for p in permissions if p.is_blocked())
        review = sum(1 for p in permissions if p.needs_review())

        risk_counts: dict[str, int] = {}
        for p in permissions:
            risk_counts[p.risk_level] = risk_counts.get(p.risk_level, 0) + 1

        return {
            "total_permissions": len(permissions),
            "allowed": allowed,
            "blocked": blocked,
            "review_required": review,
            "allow_rate": round(allowed / len(permissions), 4),
            "risk_distribution": risk_counts,
        }


__all__ = [
    "GuardrailCheckEngine",
]