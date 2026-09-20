"""
Approval Workflow Engine — Phase 3 Step 1.

Human Approval 工作流引擎，管理审批请求的完整生命周期。

职责：
    1. 创建审批请求（从 ExecutionPlanShadowResult 转换）
    2. 审批状态管理（submit / approve / reject / expire）
    3. 审批记录（所有状态变更通过 ApprovalTrace 记录）
    4. 批量审批支持

设计约束：
    - 禁止自动批准——所有状态变更需显式调用
    - 禁止自动执行——本层只负责审批，不负责执行
    - 任何状态变化必须可审计
    - 不属于任何 Runtime 层——是独立的治理层

状态机：
    PENDING ──approve()──→ APPROVED
    PENDING ──reject()───→ REJECTED
    PENDING ──expire()───→ EXPIRED
    REJECTED ──resubmit()→ PENDING (可选)
    EXPIRED ──resubmit()─→ PENDING (可选)
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from dice.runtime.approval.models import (
    ApprovalRequest,
    ApprovalTrace,
    ApprovalBatch,
    ApprovalStatus,
    ApprovalRiskLevel,
    ApprovalDecision,
)


# ═══════════════════════════════════════════════════════════════════════════
# 风险等级映射
# ═══════════════════════════════════════════════════════════════════════════

_RISK_MAP = {
    "low": ApprovalRiskLevel.LOW,
    "medium": ApprovalRiskLevel.MEDIUM,
    "high": ApprovalRiskLevel.HIGH,
    "critical": ApprovalRiskLevel.CRITICAL,
}


def _to_risk_level(value: str) -> ApprovalRiskLevel:
    """将字符串风险等级转换为枚举。"""
    return _RISK_MAP.get(value.lower(), ApprovalRiskLevel.LOW)


# ═══════════════════════════════════════════════════════════════════════════
# 状态转换白名单
# ═══════════════════════════════════════════════════════════════════════════

_VALID_TRANSITIONS: dict[ApprovalStatus, set[ApprovalStatus]] = {
    ApprovalStatus.PENDING: {
        ApprovalStatus.APPROVED,
        ApprovalStatus.REJECTED,
        ApprovalStatus.EXPIRED,
    },
    ApprovalStatus.REJECTED: {
        ApprovalStatus.PENDING,  # 允许重新提交
    },
    ApprovalStatus.EXPIRED: {
        ApprovalStatus.PENDING,  # 允许重新提交
    },
    ApprovalStatus.APPROVED: set(),  # 终态：不可变更
}


# ═══════════════════════════════════════════════════════════════════════════
# ApprovalWorkflowEngine
# ═══════════════════════════════════════════════════════════════════════════


class ApprovalWorkflowEngine:
    """审批工作流引擎。

    管理审批请求的完整生命周期，从创建到最终决策。
    所有状态变更通过 ApprovalTrace 记录，确保完整审计链。

    使用方式：
        engine = ApprovalWorkflowEngine()

        # 从 ExecutionPlanShadowResult 创建审批请求
        request = engine.create_request(execution_plan_result)

        # 提交审批
        engine.submit(request)

        # 人工审批
        engine.approve(request, reviewer="张三", comment="证据充分，批准执行")
        # 或
        engine.reject(request, reviewer="张三", comment="证据不足，需补充")

        # 查看追溯
        for trace in engine.get_traces(request.request_id):
            print(trace.to_summary())
    """

    def __init__(self) -> None:
        """初始化审批工作流引擎。"""
        # 审批请求存储
        self._requests: dict[str, ApprovalRequest] = {}
        # 追溯记录存储
        self._traces: list[ApprovalTrace] = []
        # 默认过期时间（小时）
        self._default_expiry_hours: int = 72

    # ═══════════════════════════════════════════════════════════════════
    # 创建审批请求
    # ═══════════════════════════════════════════════════════════════════

    def create_request(
        self,
        execution_plan: dict[str, Any],
        evidence_trace: Optional[dict[str, Any]] = None,
    ) -> ApprovalRequest:
        """
        从 Execution Plan Shadow 结果创建审批请求。

        参数:
            execution_plan: ExecutionPlanShadowResult.to_dict() 的输出
            evidence_trace: 可选的证据追溯信息

        返回:
            ApprovalRequest 审批请求
        """
        risk_str = execution_plan.get("risk_level", "low")
        risk_level = _to_risk_level(risk_str)

        request = ApprovalRequest(
            document_id=execution_plan.get("document_id", ""),
            evidence_trace=evidence_trace or {},
            capability_id=execution_plan.get("capability_id", ""),
            capability_name=execution_plan.get("capability_name", ""),
            execution_plan=execution_plan,
            execution_confidence=execution_plan.get("execution_confidence", 0.0),
            risk_level=risk_level,
            validation_result=execution_plan.get("validation_result", ""),
            status=ApprovalStatus.PENDING,
        )

        self._requests[request.request_id] = request

        # 记录创建追溯
        self._record_trace(
            request_id=request.request_id,
            document_id=request.document_id,
            capability_id=request.capability_id,
            execution_plan=execution_plan.get("selected_action", ""),
            previous_status=ApprovalStatus.PENDING,
            new_status=ApprovalStatus.PENDING,
            decision=ApprovalDecision.DEFER,
            operator="system",
            reason="审批请求已创建",
        )

        return request

    def create_batch(
        self,
        execution_plans: list[dict[str, Any]],
        evidence_traces: Optional[dict[str, dict[str, Any]]] = None,
    ) -> ApprovalBatch:
        """
        批量创建审批请求。

        参数:
            execution_plans: ExecutionPlanShadowResult 列表
            evidence_traces: 可选的文档级证据追溯映射

        返回:
            ApprovalBatch 批量审批结果
        """
        requests: list[ApprovalRequest] = []
        for plan in execution_plans:
            doc_id = plan.get("document_id", "")
            ev_trace = (evidence_traces or {}).get(doc_id, {})
            request = self.create_request(plan, ev_trace)
            requests.append(request)

        # 统计
        stats = self._compute_batch_statistics(requests)

        batch = ApprovalBatch(
            total_requests=len(requests),
            requests=requests,
            statistics=stats,
        )

        return batch

    # ═══════════════════════════════════════════════════════════════════
    # 审批状态管理
    # ═══════════════════════════════════════════════════════════════════

    def submit(self, request: ApprovalRequest) -> ApprovalRequest:
        """
        提交审批请求（将从 PENDING 状态显式提交）。

        注意：create_request 已自动设置为 PENDING 状态。
        此方法用于显式确认提交意图。
        """
        if not request.is_pending():
            raise ValueError(
                f"只能提交 PENDING 状态的请求，当前状态: {request.status.value}"
            )
        return request

    def approve(
        self,
        request: ApprovalRequest,
        reviewer: str = "",
        comment: str = "",
    ) -> ApprovalRequest:
        """
        批准执行计划。

        参数:
            request: 要批准的审批请求
            reviewer: 审批人标识
            comment: 审批意见

        返回:
            更新后的 ApprovalRequest

        异常:
            ValueError: 如果请求不在 PENDING 状态
        """
        self._validate_transition(request, ApprovalStatus.APPROVED)

        request.status = ApprovalStatus.APPROVED
        request.reviewer = reviewer
        request.review_comment = comment
        request.review_decision = ApprovalDecision.APPROVE
        request.updated_time = self._now()

        self._record_trace(
            request_id=request.request_id,
            document_id=request.document_id,
            capability_id=request.capability_id,
            execution_plan=request.execution_plan.get("selected_action", ""),
            previous_status=ApprovalStatus.PENDING,
            new_status=ApprovalStatus.APPROVED,
            decision=ApprovalDecision.APPROVE,
            operator=reviewer or "human",
            reason=comment or "审批通过",
        )

        return request

    def reject(
        self,
        request: ApprovalRequest,
        reviewer: str = "",
        comment: str = "",
    ) -> ApprovalRequest:
        """
        拒绝执行计划。

        参数:
            request: 要拒绝的审批请求
            reviewer: 审批人标识
            comment: 拒绝原因

        返回:
            更新后的 ApprovalRequest

        异常:
            ValueError: 如果请求不在 PENDING 状态
        """
        self._validate_transition(request, ApprovalStatus.REJECTED)

        request.status = ApprovalStatus.REJECTED
        request.reviewer = reviewer
        request.review_comment = comment
        request.review_decision = ApprovalDecision.REJECT
        request.updated_time = self._now()

        self._record_trace(
            request_id=request.request_id,
            document_id=request.document_id,
            capability_id=request.capability_id,
            execution_plan=request.execution_plan.get("selected_action", ""),
            previous_status=ApprovalStatus.PENDING,
            new_status=ApprovalStatus.REJECTED,
            decision=ApprovalDecision.REJECT,
            operator=reviewer or "human",
            reason=comment or "审批拒绝",
        )

        return request

    def expire(
        self,
        request: ApprovalRequest,
        reason: str = "",
    ) -> ApprovalRequest:
        """
        将审批请求标记为过期。

        参数:
            request: 要标记为过期的审批请求
            reason: 过期原因

        返回:
            更新后的 ApprovalRequest

        异常:
            ValueError: 如果请求不在 PENDING 状态
        """
        self._validate_transition(request, ApprovalStatus.EXPIRED)

        request.status = ApprovalStatus.EXPIRED
        request.review_decision = ApprovalDecision.EXPIRE
        request.updated_time = self._now()

        self._record_trace(
            request_id=request.request_id,
            document_id=request.document_id,
            capability_id=request.capability_id,
            execution_plan=request.execution_plan.get("selected_action", ""),
            previous_status=ApprovalStatus.PENDING,
            new_status=ApprovalStatus.EXPIRED,
            decision=ApprovalDecision.EXPIRE,
            operator="system",
            reason=reason or "审批请求已过期",
        )

        return request

    def resubmit(
        self,
        request: ApprovalRequest,
        comment: str = "",
    ) -> ApprovalRequest:
        """
        重新提交已拒绝或已过期的审批请求。

        参数:
            request: 要重新提交的审批请求
            comment: 重新提交原因

        返回:
            更新后的 ApprovalRequest

        异常:
            ValueError: 如果请求不在 REJECTED 或 EXPIRED 状态
        """
        if request.status not in (ApprovalStatus.REJECTED, ApprovalStatus.EXPIRED):
            raise ValueError(
                f"只能重新提交 REJECTED 或 EXPIRED 状态的请求，"
                f"当前状态: {request.status.value}"
            )

        previous = request.status
        request.status = ApprovalStatus.PENDING
        request.review_decision = ApprovalDecision.DEFER
        request.updated_time = self._now()

        self._record_trace(
            request_id=request.request_id,
            document_id=request.document_id,
            capability_id=request.capability_id,
            execution_plan=request.execution_plan.get("selected_action", ""),
            previous_status=previous,
            new_status=ApprovalStatus.PENDING,
            decision=ApprovalDecision.DEFER,
            operator="system",
            reason=comment or "重新提交审批",
        )

        return request

    def auto_expire_stale(
        self,
        max_age_hours: Optional[int] = None,
    ) -> int:
        """
        自动过期超过指定时间的 PENDING 请求。

        参数:
            max_age_hours: 最大等待时间（小时），默认使用 _default_expiry_hours

        返回:
            已过期的请求数量
        """
        max_hours = max_age_hours or self._default_expiry_hours
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_hours)
        expired_count = 0

        for request in list(self._requests.values()):
            if not request.is_pending():
                continue
            try:
                created = datetime.fromisoformat(request.created_time)
                if created.replace(tzinfo=timezone.utc) < cutoff:
                    self.expire(request, f"超过 {max_hours} 小时未处理，自动过期")
                    expired_count += 1
            except (ValueError, TypeError):
                continue

        return expired_count

    # ═══════════════════════════════════════════════════════════════════
    # 查询
    # ═══════════════════════════════════════════════════════════════════

    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """获取审批请求。"""
        return self._requests.get(request_id)

    def get_traces(self, request_id: str = "") -> list[ApprovalTrace]:
        """获取审批追溯记录。

        参数:
            request_id: 可选，筛选特定请求的追溯记录。
                        为空时返回所有记录。
        """
        if request_id:
            return [t for t in self._traces if t.request_id == request_id]
        return list(self._traces)

    def get_pending_requests(self) -> list[ApprovalRequest]:
        """获取所有待审批的请求。"""
        return [r for r in self._requests.values() if r.is_pending()]

    def get_approved_requests(self) -> list[ApprovalRequest]:
        """获取所有已批准的请求。"""
        return [r for r in self._requests.values() if r.is_approved()]

    def get_statistics(self) -> dict[str, Any]:
        """获取审批统计信息。"""
        total = len(self._requests)
        if total == 0:
            return {"total": 0}

        status_counts: dict[str, int] = {}
        risk_counts: dict[str, int] = {}
        for r in self._requests.values():
            status_counts[r.status.value] = status_counts.get(r.status.value, 0) + 1
            risk_counts[r.risk_level.value] = risk_counts.get(r.risk_level.value, 0) + 1

        return {
            "total": total,
            "status_distribution": status_counts,
            "risk_distribution": risk_counts,
            "pending": status_counts.get("PENDING", 0),
            "approved": status_counts.get("APPROVED", 0),
            "rejected": status_counts.get("REJECTED", 0),
            "expired": status_counts.get("EXPIRED", 0),
            "total_traces": len(self._traces),
        }

    # ═══════════════════════════════════════════════════════════════════
    # 内部方法
    # ═══════════════════════════════════════════════════════════════════

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _validate_transition(
        self,
        request: ApprovalRequest,
        target: ApprovalStatus,
    ) -> None:
        """验证状态转换是否合法。"""
        allowed = _VALID_TRANSITIONS.get(request.status, set())
        if target not in allowed:
            raise ValueError(
                f"不允许的状态转换: {request.status.value} → {target.value}"
            )

    def _record_trace(
        self,
        request_id: str,
        document_id: str,
        capability_id: str,
        execution_plan: str,
        previous_status: ApprovalStatus,
        new_status: ApprovalStatus,
        decision: ApprovalDecision,
        operator: str,
        reason: str,
    ) -> None:
        """记录状态变更追溯。"""
        trace = ApprovalTrace(
            request_id=request_id,
            document_id=document_id,
            capability_id=capability_id,
            execution_plan=execution_plan,
            previous_status=previous_status,
            new_status=new_status,
            decision=decision,
            operator=operator,
            reason=reason,
        )
        self._traces.append(trace)

    @staticmethod
    def _compute_batch_statistics(
        requests: list[ApprovalRequest],
    ) -> dict[str, Any]:
        """计算批量审批统计。"""
        if not requests:
            return {}

        risk_counts: dict[str, int] = {}
        for r in requests:
            risk_counts[r.risk_level.value] = risk_counts.get(r.risk_level.value, 0) + 1

        avg_confidence = (
            sum(r.execution_confidence for r in requests) / len(requests)
            if requests else 0.0
        )

        return {
            "total_requests": len(requests),
            "risk_distribution": risk_counts,
            "avg_execution_confidence": round(avg_confidence, 4),
        }


__all__ = [
    "ApprovalWorkflowEngine",
]