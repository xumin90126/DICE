"""
激活边界数据模型 — Phase 3 Step 2.

Controlled Activation Boundary 的核心数据结构。

设计原则：
    1. ActivationDecision 只消费已批准的 ApprovalRequest
    2. 激活状态严格控制：PENDING → ALLOWED / BLOCKED
    3. 任何激活决策必须可审计
    4. 禁止绕过审批层直接激活

架构约束：
    - 不属于 Evidence Runtime
    - 不属于 Capability Runtime
    - 不属于 Execution Runtime
    - 不属于 Approval Layer
    - 是独立的激活边界层
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


class ActivationStatus(str, Enum):
    """激活状态枚举。

    状态转换规则：
        PENDING     → ALLOWED   (所有验证通过，允许进入执行)
        PENDING     → BLOCKED   (任何验证失败，阻止进入执行)
        ALLOWED     → EXECUTED  (已进入执行阶段)
        EXECUTED    → (终态)
        BLOCKED     → (终态，需重新提交审批)
    """
    PENDING = "PENDING"       # 待验证
    ALLOWED = "ALLOWED"       # 允许激活
    BLOCKED = "BLOCKED"       # 阻止激活
    EXECUTED = "EXECUTED"     # 已执行


class ActivationBlockReason(str, Enum):
    """激活阻止原因枚举。"""
    APPROVAL_NOT_APPROVED = "approval_not_approved"
    APPROVAL_TRACE_MISSING = "approval_trace_missing"
    EXECUTION_PLAN_VALIDATION_FAILED = "execution_plan_validation_failed"
    RISK_VALIDATION_FAILED = "risk_validation_failed"
    CAPABILITY_TRACE_MISSING = "capability_trace_missing"
    EVIDENCE_CHAIN_INCOMPLETE = "evidence_chain_incomplete"
    UNAUTHORIZED_EXECUTION = "unauthorized_execution"
    INVALID_STATE_TRANSITION = "invalid_state_transition"


class ActivationRiskLevel(str, Enum):
    """激活风险等级枚举。

    决定激活后的执行策略：
        LOW      → 可直接执行，仅记录日志
        MEDIUM   → 需确认后执行，记录完整审计
        HIGH     → 需二次确认后执行，记录完整审计 + 告警
        CRITICAL → 禁止自动执行，必须人工确认
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


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
# ActivationDecision — 激活决策
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class ActivationDecision:
    """激活决策——审批通过后，决定是否允许执行计划进入真实执行。

    每一条 ActivationDecision 可以完整追溯：
        ApprovalRequest → Activation Boundary → ActivationDecision

    Fields:
        decision_id: 唯一激活决策 ID
        request_id: 关联的审批请求 ID
        document_id: 源文档标识
        execution_plan_id: 执行计划标识
        capability_id: 关联的能力标识
        approval_status: 审批状态（必须为 APPROVED）
        activation_status: 激活状态（ALLOWED/BLOCKED）
        validation_result: 验证结果摘要
        block_reasons: 阻止原因列表（如果 BLOCKED）
        risk_level: 风险等级
        approved_by: 审批人
        approval_timestamp: 审批时间
        audit_trace_reference: 审计追溯引用
        reasoning: 决策推理
        created_time: 决策创建时间
        metadata: 扩展元数据
    """
    decision_id: str = ""
    request_id: str = ""
    document_id: str = ""
    execution_plan_id: str = ""
    capability_id: str = ""
    approval_status: str = ""
    activation_status: ActivationStatus = ActivationStatus.PENDING
    validation_result: dict[str, Any] = field(default_factory=dict)
    block_reasons: list[str] = field(default_factory=list)
    risk_level: ActivationRiskLevel = ActivationRiskLevel.LOW
    approved_by: str = ""
    approval_timestamp: str = ""
    audit_trace_reference: str = ""
    reasoning: str = ""
    created_time: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.decision_id:
            self.decision_id = _uid("ACT-")
        if not self.created_time:
            self.created_time = _now()

    @property
    def is_allowed(self) -> bool:
        """是否允许激活。"""
        return self.activation_status == ActivationStatus.ALLOWED

    @property
    def is_blocked(self) -> bool:
        """是否被阻止。"""
        return self.activation_status == ActivationStatus.BLOCKED

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "request_id": self.request_id,
            "document_id": self.document_id,
            "execution_plan_id": self.execution_plan_id,
            "capability_id": self.capability_id,
            "approval_status": self.approval_status,
            "activation_status": self.activation_status.value,
            "validation_result": self.validation_result,
            "block_reasons": self.block_reasons,
            "risk_level": self.risk_level.value,
            "approved_by": self.approved_by,
            "approval_timestamp": self.approval_timestamp,
            "audit_trace_reference": self.audit_trace_reference,
            "reasoning": self.reasoning,
            "created_time": self.created_time,
            "metadata": self.metadata,
        }

    def to_summary(self) -> str:
        """生成激活决策的摘要描述。"""
        status_icon = "✅" if self.is_allowed else "❌"
        block_info = ""
        if self.block_reasons:
            block_info = f" | 阻止原因: {', '.join(self.block_reasons)}"
        return (
            f"{status_icon} [{self.activation_status.value}] "
            f"文档: {self.document_id} | "
            f"能力: {self.capability_id} | "
            f"审批: {self.approval_status} | "
            f"风险: {self.risk_level.value}"
            f"{block_info}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# ActivationAuditRecord — 激活审计记录
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class ActivationAuditRecord:
    """激活审计记录——每次激活决策的不可变记录。

    Fields:
        audit_id: 审计记录唯一 ID
        decision_id: 关联的激活决策
        request_id: 关联的审批请求
        document_id: 源文档
        activation_status: 激活结果
        validated_by: 验证者（"system" 或 "human"）
        validation_checks: 各项验证检查结果
        timestamp: 记录时间
        reason: 决策原因
        metadata: 扩展元数据
    """
    audit_id: str = ""
    decision_id: str = ""
    request_id: str = ""
    document_id: str = ""
    activation_status: ActivationStatus = ActivationStatus.PENDING
    validated_by: str = ""
    validation_checks: dict[str, bool] = field(default_factory=dict)
    timestamp: str = ""
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.audit_id:
            self.audit_id = _uid("ADA-")
        if not self.timestamp:
            self.timestamp = _now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "decision_id": self.decision_id,
            "request_id": self.request_id,
            "document_id": self.document_id,
            "activation_status": self.activation_status.value,
            "validated_by": self.validated_by,
            "validation_checks": self.validation_checks,
            "timestamp": self.timestamp,
            "reason": self.reason,
            "metadata": self.metadata,
        }

    def to_summary(self) -> str:
        """生成审计记录的摘要描述。"""
        checks = ", ".join(
            f"{k}={'✓' if v else '✗'}" for k, v in self.validation_checks.items()
        )
        return (
            f"[{self.timestamp}] {self.validated_by}: "
            f"{self.activation_status.value} | "
            f"检查: [{checks}] | "
            f"原因: {self.reason}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# ActivationBatchResult — 批量激活结果
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class ActivationBatchResult:
    """批量激活结果——用于多文档激活的汇总。"""
    batch_id: str = ""
    generated_at: str = ""
    total_decisions: int = 0
    decisions: list[ActivationDecision] = field(default_factory=list)
    audit_records: list[ActivationAuditRecord] = field(default_factory=list)
    statistics: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.batch_id:
            self.batch_id = _uid("ACB-")
        if not self.generated_at:
            self.generated_at = _now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "generated_at": self.generated_at,
            "total_decisions": self.total_decisions,
            "decisions": [d.to_dict() for d in self.decisions],
            "audit_records": [a.to_dict() for a in self.audit_records],
            "statistics": self.statistics,
        }


__all__ = [
    "ActivationDecision",
    "ActivationAuditRecord",
    "ActivationBatchResult",
    "ActivationStatus",
    "ActivationBlockReason",
    "ActivationRiskLevel",
]