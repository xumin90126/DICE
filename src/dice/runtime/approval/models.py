"""
Approval 数据模型 — Phase 3 Step 1.

Human Approval Layer 的核心数据结构。

设计原则：
    1. 每一个 ApprovalRequest 必须可追溯：Document → Evidence → Capability → Execution Plan
    2. 任何状态变化必须通过 ApprovalTrace 记录
    3. 状态机严格控制：PENDING → APPROVED/REJECTED/EXPIRED
    4. 禁止自动批准——所有状态变更需显式调用

架构约束：
    - 不属于 Evidence Runtime
    - 不属于 Capability Runtime
    - 不属于 Execution Runtime
    - 是独立的治理层
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


# ═══════════════════════════════════════════════════════════════════════════
# 枚举类型
# ═══════════════════════════════════════════════════════════════════════════


class ApprovalStatus(str, Enum):
    """审批状态枚举。

    状态转换规则：
        PENDING   → APPROVED  (人工批准)
        PENDING   → REJECTED  (人工拒绝)
        PENDING   → EXPIRED   (超时过期)
        REJECTED  → PENDING   (重新提交，可选)
        EXPIRED   → PENDING   (重新提交，可选)
    """
    PENDING = "PENDING"       # 待审批
    APPROVED = "APPROVED"     # 已批准
    REJECTED = "REJECTED"     # 已拒绝
    EXPIRED = "EXPIRED"       # 已过期


class ApprovalRiskLevel(str, Enum):
    """审批风险等级枚举。

    决定审批策略：
        LOW      → 可批量审批
        MEDIUM   → 需逐一审批
        HIGH     → 需多重审批
        CRITICAL → 禁止自动执行，需人工确认
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalDecision(str, Enum):
    """审批决策枚举——记录人工做出的最终决定。"""
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    DEFER = "DEFER"       # 暂缓——待补充证据后重新提交
    EXPIRE = "EXPIRE"     # 过期——超时自动过期


# ═══════════════════════════════════════════════════════════════════════════
# 辅助函数
# ═══════════════════════════════════════════════════════════════════════════


def _now() -> str:
    """当前 UTC 时间戳。"""
    return datetime.now(timezone.utc).isoformat()


def _uid(prefix: str = "") -> str:
    """生成短唯一 ID。"""
    return f"{prefix}{uuid.uuid4().hex[:8]}"


# ═══════════════════════════════════════════════════════════════════════════
# ApprovalRequest — 审批请求
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class ApprovalRequest:
    """审批请求——从 Execution Plan 生成的审批单元。

    每一个 ApprovalRequest 可以完整追溯：
        Document → Evidence → Capability → Execution Plan → Approval

    Fields:
        request_id: 唯一审批请求 ID
        document_id: 源文档标识
        evidence_trace: 证据追溯链（Evidence Runtime 输出）
        capability_id: 激活的能力标识
        capability_name: 能力名称
        execution_plan: 执行计划（来自 Execution Shadow）
        execution_confidence: 执行置信度 (0-1)
        risk_level: 风险等级
        validation_result: 影子验证结果 (PASS/WARN/FAIL)
        status: 当前审批状态
        reviewer: 审批人
        review_comment: 审批意见
        review_decision: 审批决策（APPROVE/REJECT/DEFER/EXPIRE）
        created_time: 创建时间
        updated_time: 最后更新时间
        metadata: 扩展元数据
    """
    request_id: str = ""
    document_id: str = ""
    evidence_trace: dict[str, Any] = field(default_factory=dict)
    capability_id: str = ""
    capability_name: str = ""
    execution_plan: dict[str, Any] = field(default_factory=dict)
    execution_confidence: float = 0.0
    risk_level: ApprovalRiskLevel = ApprovalRiskLevel.LOW
    validation_result: str = ""
    status: ApprovalStatus = ApprovalStatus.PENDING
    reviewer: str = ""
    review_comment: str = ""
    review_decision: ApprovalDecision = ApprovalDecision.DEFER
    created_time: str = ""
    updated_time: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.request_id:
            self.request_id = _uid("APR-")
        if not self.created_time:
            self.created_time = _now()
        if not self.updated_time:
            self.updated_time = self.created_time

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "document_id": self.document_id,
            "evidence_trace": self.evidence_trace,
            "capability_id": self.capability_id,
            "capability_name": self.capability_name,
            "execution_plan": self.execution_plan,
            "execution_confidence": round(self.execution_confidence, 4),
            "risk_level": self.risk_level.value,
            "validation_result": self.validation_result,
            "status": self.status.value,
            "reviewer": self.reviewer,
            "review_comment": self.review_comment,
            "review_decision": self.review_decision.value,
            "created_time": self.created_time,
            "updated_time": self.updated_time,
            "metadata": self.metadata,
        }

    def is_pending(self) -> bool:
        return self.status == ApprovalStatus.PENDING

    def is_approved(self) -> bool:
        return self.status == ApprovalStatus.APPROVED

    def is_resolved(self) -> bool:
        """审批是否已完成（已批准或已拒绝）。"""
        return self.status in (ApprovalStatus.APPROVED, ApprovalStatus.REJECTED)

    def to_summary(self) -> str:
        """生成审批请求的摘要描述。"""
        return (
            f"[{self.status.value}] {self.capability_name} "
            f"({self.capability_id}) → {self.execution_plan.get('selected_action', '?')} "
            f"| 置信度: {self.execution_confidence:.2f} "
            f"| 风险: {self.risk_level.value}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# ApprovalTrace — 审批追溯记录
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class ApprovalTrace:
    """审批追溯记录——每次状态变更的不可变记录。

    任何状态变化必须可审计。例如：
        Execution Plan: create_storage_requirement_check
        ↓
        Human: APPROVED
        ↓
        Trace: Reviewer approved because evidence coverage sufficient

    Fields:
        trace_id: 追溯记录唯一 ID
        request_id: 关联的审批请求
        document_id: 源文档
        capability_id: 关联的能力
        execution_plan: 执行计划摘要
        previous_status: 变更前状态
        new_status: 变更后状态
        decision: 决策类型
        operator: 操作者（"human" 或 "system"）
        timestamp: 记录时间
        reason: 变更原因
        metadata: 扩展元数据
    """
    trace_id: str = ""
    request_id: str = ""
    document_id: str = ""
    capability_id: str = ""
    execution_plan: str = ""
    previous_status: ApprovalStatus = ApprovalStatus.PENDING
    new_status: ApprovalStatus = ApprovalStatus.PENDING
    decision: ApprovalDecision = ApprovalDecision.DEFER
    operator: str = ""
    timestamp: str = ""
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.trace_id:
            self.trace_id = _uid("TRC-")
        if not self.timestamp:
            self.timestamp = _now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "request_id": self.request_id,
            "document_id": self.document_id,
            "capability_id": self.capability_id,
            "execution_plan": self.execution_plan,
            "previous_status": self.previous_status.value,
            "new_status": self.new_status.value,
            "decision": self.decision.value,
            "operator": self.operator,
            "timestamp": self.timestamp,
            "reason": self.reason,
            "metadata": self.metadata,
        }

    def to_summary(self) -> str:
        """生成追溯记录的摘要描述。"""
        return (
            f"[{self.timestamp}] {self.operator}: "
            f"{self.previous_status.value} → {self.new_status.value} "
            f"({self.decision.value}) — {self.reason}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# ApprovalBatch — 批量审批结果
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class ApprovalBatch:
    """批量审批结果——用于多文档审批的汇总。"""
    batch_id: str = ""
    generated_at: str = ""
    total_requests: int = 0
    requests: list[ApprovalRequest] = field(default_factory=list)
    traces: list[ApprovalTrace] = field(default_factory=list)
    statistics: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.batch_id:
            self.batch_id = _uid("APB-")
        if not self.generated_at:
            self.generated_at = _now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "generated_at": self.generated_at,
            "total_requests": self.total_requests,
            "requests": [r.to_dict() for r in self.requests],
            "traces": [t.to_dict() for t in self.traces],
            "statistics": self.statistics,
        }


__all__ = [
    "ApprovalRequest",
    "ApprovalTrace",
    "ApprovalDecision",
    "ApprovalStatus",
    "ApprovalRiskLevel",
    "ApprovalBatch",
]