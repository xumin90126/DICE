"""
激活边界引擎 — Phase 3 Step 2.

Controlled Activation Boundary：审批通过后，决定是否允许执行计划进入真实执行。

职责：
    1. 消费已批准的 ApprovalRequest
    2. 执行四重门禁验证
    3. 生成 ActivationDecision（ALLOWED / BLOCKED）
    4. 记录完整激活审计记录

设计约束：
    - 禁止执行真实动作——本层只负责门禁，不负责执行
    - 禁止绕过审批层——只有 APPROVED 的请求才能进入激活
    - 禁止自动批准——审批状态必须由 Approval Layer 显式设置
    - 不属于任何 Runtime 层——是独立的激活边界层

激活门禁（四重验证，全部通过才允许激活）：
    Gate 1: 审批状态验证 — approval_status == APPROVED
    Gate 2: 审批追溯完整性 — approval_trace 存在且完整
    Gate 3: 执行计划完整性 — validation_result == PASS
    Gate 4: 风险验证 — risk_level 在允许范围内

任何门禁失败 → activation_status = BLOCKED
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
    ActivationAuditRecord,
    ActivationBatchResult,
    ActivationStatus,
    ActivationBlockReason,
    ActivationRiskLevel,
)


# ═══════════════════════════════════════════════════════════════════════════
# 风险等级映射
# ═══════════════════════════════════════════════════════════════════════════

_APPROVAL_TO_ACTIVATION_RISK = {
    ApprovalRiskLevel.LOW: ActivationRiskLevel.LOW,
    ApprovalRiskLevel.MEDIUM: ActivationRiskLevel.MEDIUM,
    ApprovalRiskLevel.HIGH: ActivationRiskLevel.HIGH,
    ApprovalRiskLevel.CRITICAL: ActivationRiskLevel.CRITICAL,
}


def _map_risk(approval_risk: ApprovalRiskLevel) -> ActivationRiskLevel:
    """将审批风险等级映射为激活风险等级。"""
    return _APPROVAL_TO_ACTIVATION_RISK.get(approval_risk, ActivationRiskLevel.LOW)


# ═══════════════════════════════════════════════════════════════════════════
# ActivationBoundary
# ═══════════════════════════════════════════════════════════════════════════


class ActivationBoundary:
    """激活边界引擎。

    审批通过后，执行四重门禁验证，决定是否允许执行计划进入真实执行。

    使用方式：
        boundary = ActivationBoundary()

        # 从已批准的审批请求创建激活决策
        decision = boundary.evaluate(approved_request, approval_traces)

        if decision.is_allowed:
            # 可以进入执行——但 ActivationBoundary 不负责执行
            pass
        else:
            # 被阻止——查看 block_reasons 了解原因
            print(decision.block_reasons)
    """

    # 允许自动激活的最低风险等级
    DEFAULT_AUTO_ACTIVATION_RISK = ActivationRiskLevel.MEDIUM

    def __init__(self) -> None:
        """初始化激活边界引擎。"""
        # 激活决策存储
        self._decisions: dict[str, ActivationDecision] = {}
        # 审计记录存储
        self._audit_records: list[ActivationAuditRecord] = []

    # ═══════════════════════════════════════════════════════════════════
    # 核心方法：评估激活
    # ═══════════════════════════════════════════════════════════════════

    def evaluate(
        self,
        approval_request: ApprovalRequest,
        approval_traces: Optional[list[ApprovalTrace]] = None,
        capability_trace: Optional[dict[str, Any]] = None,
        evidence_chain: Optional[dict[str, Any]] = None,
    ) -> ActivationDecision:
        """
        评估审批请求是否允许进入激活。

        参数:
            approval_request: 审批请求（必须为 APPROVED 状态）
            approval_traces: 审批追溯记录列表
            capability_trace: 可选的能力追溯信息
            evidence_chain: 可选的证据链信息

        返回:
            ActivationDecision 激活决策（ALLOWED 或 BLOCKED）
        """
        # 映射风险等级
        activation_risk = _map_risk(approval_request.risk_level)

        # 创建决策对象
        decision = ActivationDecision(
            request_id=approval_request.request_id,
            document_id=approval_request.document_id,
            execution_plan_id=approval_request.execution_plan.get("plan_id", ""),
            capability_id=approval_request.capability_id,
            approval_status=approval_request.status.value,
            activation_status=ActivationStatus.PENDING,
            risk_level=activation_risk,
            approved_by=approval_request.reviewer,
            approval_timestamp=approval_request.updated_time,
        )

        # 执行四重门禁验证
        validation_result, block_reasons = self._run_gates(
            approval_request=approval_request,
            approval_traces=approval_traces or [],
            capability_trace=capability_trace,
            evidence_chain=evidence_chain,
        )

        decision.validation_result = validation_result
        decision.block_reasons = block_reasons

        if block_reasons:
            decision.activation_status = ActivationStatus.BLOCKED
            decision.reasoning = f"激活被阻止，原因: {', '.join(block_reasons)}"
        else:
            decision.activation_status = ActivationStatus.ALLOWED
            decision.reasoning = (
                f"四重门禁全部通过: "
                f"审批状态={approval_request.status.value}, "
                f"风险等级={activation_risk.value}, "
                f"审批人={approval_request.reviewer}"
            )

        decision.audit_trace_reference = self._generate_audit_reference(decision)

        # 存储决策
        self._decisions[decision.decision_id] = decision

        # 记录审计
        self._record_audit(
            decision=decision,
            validation_result=validation_result,
            block_reasons=block_reasons,
        )

        return decision

    def evaluate_batch(
        self,
        approval_requests: list[ApprovalRequest],
        all_traces: Optional[dict[str, list[ApprovalTrace]]] = None,
    ) -> ActivationBatchResult:
        """
        批量评估审批请求。

        参数:
            approval_requests: 审批请求列表
            all_traces: 请求 ID → 追溯记录列表的映射

        返回:
            ActivationBatchResult 批量激活结果
        """
        traces_map = all_traces or {}
        decisions: list[ActivationDecision] = []

        for req in approval_requests:
            traces = traces_map.get(req.request_id, [])
            decision = self.evaluate(req, approval_traces=traces)
            decisions.append(decision)

        # 统计
        stats = self._compute_batch_statistics(decisions)

        result = ActivationBatchResult(
            total_decisions=len(decisions),
            decisions=decisions,
            audit_records=list(self._audit_records),
            statistics=stats,
        )

        return result

    # ═══════════════════════════════════════════════════════════════════
    # 四重门禁验证
    # ═══════════════════════════════════════════════════════════════════

    def _run_gates(
        self,
        approval_request: ApprovalRequest,
        approval_traces: list[ApprovalTrace],
        capability_trace: Optional[dict[str, Any]],
        evidence_chain: Optional[dict[str, Any]],
    ) -> tuple[dict[str, Any], list[str]]:
        """执行四重门禁验证。

        返回:
            (validation_result, block_reasons)
        """
        validation_result: dict[str, Any] = {}
        block_reasons: list[str] = []

        # Gate 1: 审批状态验证
        gate1 = self._gate_approval_status(approval_request)
        validation_result["gate1_approval_status"] = gate1
        if not gate1["passed"]:
            block_reasons.append(gate1["reason"])

        # Gate 2: 审批追溯完整性
        gate2 = self._gate_approval_trace(approval_request, approval_traces)
        validation_result["gate2_approval_trace"] = gate2
        if not gate2["passed"]:
            block_reasons.append(gate2["reason"])

        # Gate 3: 执行计划完整性
        gate3 = self._gate_execution_plan(approval_request)
        validation_result["gate3_execution_plan"] = gate3
        if not gate3["passed"]:
            block_reasons.append(gate3["reason"])

        # Gate 4: 风险验证
        gate4 = self._gate_risk_validation(approval_request)
        validation_result["gate4_risk_validation"] = gate4
        if not gate4["passed"]:
            block_reasons.append(gate4["reason"])

        return validation_result, block_reasons

    # ═══════════════════════════════════════════════════════════════════
    # Gate 1: 审批状态验证
    # ═══════════════════════════════════════════════════════════════════

    def _gate_approval_status(
        self, request: ApprovalRequest
    ) -> dict[str, Any]:
        """验证审批状态是否为 APPROVED。"""
        if request.status == ApprovalStatus.APPROVED:
            return {
                "passed": True,
                "detail": f"审批状态: {request.status.value}",
                "reason": "",
            }
        return {
            "passed": False,
            "detail": f"审批状态: {request.status.value}（期望: APPROVED）",
            "reason": ActivationBlockReason.APPROVAL_NOT_APPROVED.value,
        }

    # ═══════════════════════════════════════════════════════════════════
    # Gate 2: 审批追溯完整性
    # ═══════════════════════════════════════════════════════════════════

    def _gate_approval_trace(
        self,
        request: ApprovalRequest,
        traces: list[ApprovalTrace],
    ) -> dict[str, Any]:
        """验证审批追溯记录是否完整。"""
        # 检查是否有追溯记录
        if not traces:
            return {
                "passed": False,
                "detail": "审批追溯记录为空",
                "reason": ActivationBlockReason.APPROVAL_TRACE_MISSING.value,
            }

        # 检查是否有 APPROVE 决策的追溯记录
        approve_traces = [
            t for t in traces
            if t.request_id == request.request_id
        ]
        if not approve_traces:
            return {
                "passed": False,
                "detail": f"未找到请求 {request.request_id} 的审批追溯记录",
                "reason": ActivationBlockReason.APPROVAL_TRACE_MISSING.value,
            }

        # 检查是否有最终 APPROVE 决策
        has_approve = any(
            t.new_status == ApprovalStatus.APPROVED
            for t in approve_traces
        )
        if not has_approve:
            return {
                "passed": False,
                "detail": "追溯记录中未找到 APPROVED 状态变更",
                "reason": ActivationBlockReason.APPROVAL_TRACE_MISSING.value,
            }

        return {
            "passed": True,
            "detail": f"审批追溯完整: {len(approve_traces)} 条记录",
            "reason": "",
        }

    # ═══════════════════════════════════════════════════════════════════
    # Gate 3: 执行计划完整性
    # ═══════════════════════════════════════════════════════════════════

    def _gate_execution_plan(
        self, request: ApprovalRequest
    ) -> dict[str, Any]:
        """验证执行计划是否完整且验证通过。"""
        validation = request.validation_result

        # 检查 validation_result 字段
        if validation == "FAIL":
            return {
                "passed": False,
                "detail": "执行计划验证结果: FAIL",
                "reason": ActivationBlockReason.EXECUTION_PLAN_VALIDATION_FAILED.value,
            }

        # 检查执行计划是否包含必要字段
        plan = request.execution_plan
        if not plan:
            return {
                "passed": False,
                "detail": "执行计划为空",
                "reason": ActivationBlockReason.EXECUTION_PLAN_VALIDATION_FAILED.value,
            }

        # 检查 selected_action 是否存在
        if not plan.get("selected_action"):
            return {
                "passed": False,
                "detail": "执行计划缺少 selected_action",
                "reason": ActivationBlockReason.EXECUTION_PLAN_VALIDATION_FAILED.value,
            }

        return {
            "passed": True,
            "detail": (
                f"执行计划完整: action={plan.get('selected_action')}, "
                f"验证={validation or 'PASS'}"
            ),
            "reason": "",
        }

    # ═══════════════════════════════════════════════════════════════════
    # Gate 4: 风险验证
    # ═══════════════════════════════════════════════════════════════════

    def _gate_risk_validation(
        self, request: ApprovalRequest
    ) -> dict[str, Any]:
        """验证风险等级是否在允许范围内。"""
        activation_risk = _map_risk(request.risk_level)

        # 检查风险等级是否允许自动激活
        if activation_risk == ActivationRiskLevel.CRITICAL:
            return {
                "passed": False,
                "detail": (
                    f"风险等级: {activation_risk.value}，"
                    f"CRITICAL 级别需要人工二次确认"
                ),
                "reason": ActivationBlockReason.RISK_VALIDATION_FAILED.value,
            }

        # 检查执行置信度
        if request.execution_confidence < 0.5:
            return {
                "passed": False,
                "detail": (
                    f"执行置信度过低: {request.execution_confidence:.2f} "
                    f"（最低要求: 0.50）"
                ),
                "reason": ActivationBlockReason.RISK_VALIDATION_FAILED.value,
            }

        return {
            "passed": True,
            "detail": (
                f"风险等级: {activation_risk.value}, "
                f"置信度: {request.execution_confidence:.2f}"
            ),
            "reason": "",
        }

    # ═══════════════════════════════════════════════════════════════════
    # 查询方法
    # ═══════════════════════════════════════════════════════════════════

    def get_decision(self, decision_id: str) -> Optional[ActivationDecision]:
        """获取激活决策。"""
        return self._decisions.get(decision_id)

    def get_audit_records(
        self, decision_id: str = ""
    ) -> list[ActivationAuditRecord]:
        """获取激活审计记录。

        参数:
            decision_id: 可选，筛选特定决策的审计记录。
                         为空时返回所有记录。
        """
        if decision_id:
            return [a for a in self._audit_records if a.decision_id == decision_id]
        return list(self._audit_records)

    def get_allowed_decisions(self) -> list[ActivationDecision]:
        """获取所有允许激活的决策。"""
        return [d for d in self._decisions.values() if d.is_allowed]

    def get_blocked_decisions(self) -> list[ActivationDecision]:
        """获取所有被阻止的决策。"""
        return [d for d in self._decisions.values() if d.is_blocked]

    def get_statistics(self) -> dict[str, Any]:
        """获取激活统计信息。"""
        total = len(self._decisions)
        if total == 0:
            return {"total": 0}

        allowed = sum(1 for d in self._decisions.values() if d.is_allowed)
        blocked = sum(1 for d in self._decisions.values() if d.is_blocked)

        risk_counts: dict[str, int] = {}
        block_reason_counts: dict[str, int] = {}
        for d in self._decisions.values():
            risk_counts[d.risk_level.value] = risk_counts.get(d.risk_level.value, 0) + 1
            for reason in d.block_reasons:
                block_reason_counts[reason] = block_reason_counts.get(reason, 0) + 1

        return {
            "total": total,
            "allowed": allowed,
            "blocked": blocked,
            "allow_rate": round(allowed / total, 4) if total > 0 else 0.0,
            "risk_distribution": risk_counts,
            "block_reason_distribution": block_reason_counts,
            "total_audit_records": len(self._audit_records),
        }

    # ═══════════════════════════════════════════════════════════════════
    # 内部方法
    # ═══════════════════════════════════════════════════════════════════

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _generate_audit_reference(self, decision: ActivationDecision) -> str:
        """生成审计追溯引用。"""
        return (
            f"audit://activation/{decision.decision_id}"
            f"?request={decision.request_id}"
            f"&document={decision.document_id}"
            f"&capability={decision.capability_id}"
        )

    def _record_audit(
        self,
        decision: ActivationDecision,
        validation_result: dict[str, Any],
        block_reasons: list[str],
    ) -> None:
        """记录激活审计。"""
        # 构建验证检查结果
        checks = {
            f"gate{i+1}_{k}": v.get("passed", False)
            for i, (k, v) in enumerate(validation_result.items())
        }

        reason = (
            f"允许激活: {decision.reasoning}"
            if decision.is_allowed
            else f"阻止激活: {', '.join(block_reasons)}"
        )

        record = ActivationAuditRecord(
            decision_id=decision.decision_id,
            request_id=decision.request_id,
            document_id=decision.document_id,
            activation_status=decision.activation_status,
            validated_by="system",
            validation_checks=checks,
            reason=reason,
        )
        self._audit_records.append(record)

    @staticmethod
    def _compute_batch_statistics(
        decisions: list[ActivationDecision],
    ) -> dict[str, Any]:
        """计算批量激活统计。"""
        if not decisions:
            return {}

        allowed = sum(1 for d in decisions if d.is_allowed)
        blocked = sum(1 for d in decisions if d.is_blocked)

        risk_counts: dict[str, int] = {}
        for d in decisions:
            risk_counts[d.risk_level.value] = risk_counts.get(d.risk_level.value, 0) + 1

        return {
            "total_decisions": len(decisions),
            "allowed": allowed,
            "blocked": blocked,
            "allow_rate": round(allowed / len(decisions), 4),
            "risk_distribution": risk_counts,
        }


__all__ = [
    "ActivationBoundary",
]