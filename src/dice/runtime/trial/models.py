"""
试运行数据模型 — Phase 4.

Controlled Production Trial 的核心数据结构。

设计原则：
    1. TrialConfiguration 显式定义试运行边界——绝不能自动扩大
    2. TrialExecutionRecord 完整记录每次试运行的全链路结果
    3. TrialMetrics 收集试运行统计数据，用于后续决策
    4. 试运行不是真实生产执行——只记录，不执行

架构约束：
    - 不属于 Evidence Runtime
    - 不属于 Capability Runtime
    - 不属于 Execution Runtime
    - 不属于审批层 / 激活层 / 护栏层
    - 是独立的试运行管理层
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


class TrialStatus(str, Enum):
    """试运行状态枚举。

    状态转换规则：
        PENDING       → RUNNING    (开始执行)
        RUNNING       → COMPLETED  (全部通过)
        RUNNING       → BLOCKED    (被某层阻断)
        COMPLETED     → (终态)
        BLOCKED       → (终态，需人工审查)
    """
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"


class TrialBlockReason(str, Enum):
    """试运行阻断原因枚举。"""
    EVIDENCE_EXTRACTION_FAILED = "evidence_extraction_failed"
    CAPABILITY_MATCH_FAILED = "capability_match_failed"
    EXECUTION_PLAN_FAILED = "execution_plan_failed"
    APPROVAL_REJECTED = "approval_rejected"
    ACTIVATION_BLOCKED = "activation_blocked"
    GUARDRAIL_BLOCKED = "guardrail_blocked"
    PERMISSION_BLOCKED = "permission_blocked"
    SCOPE_EXCEEDED = "scope_exceeded"
    BATCH_LIMIT_EXCEEDED = "batch_limit_exceeded"
    DAILY_LIMIT_EXCEEDED = "daily_limit_exceeded"


class TrialExecutionPhase(str, Enum):
    """试运行执行阶段枚举。"""
    EVIDENCE = "evidence"
    CAPABILITY = "capability"
    EXECUTION = "execution"
    APPROVAL = "approval"
    ACTIVATION = "activation"
    GUARDRAIL = "guardrail"
    PERMISSION = "permission"


class TrialRiskLevel(str, Enum):
    """试运行风险等级枚举。"""
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
# TrialConfiguration — 试运行配置
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class TrialConfiguration:
    """试运行配置——定义受控生产试运行的边界。

    Fields:
        trial_id: 唯一试运行 ID
        name: 试运行名称（人类可读）
        description: 试运行描述
        document_scope: 允许的文档 ID 白名单（空 = 全部禁止）
        allowed_capabilities: 允许的能力 ID 白名单（空 = 全部禁止）
        allowed_actions: 允许的执行动作白名单（空 = 全部禁止）
        risk_level_limit: 允许的最高风险等级
        max_daily_documents: 每日最大文档数
        max_batch_size: 最大批次大小
        require_human_review: 是否要求每次执行后人工审查
        enabled: 是否启用
        created_by: 创建者
        created_time: 创建时间
        updated_time: 最后更新时间
        metadata: 扩展元数据
    """
    trial_id: str = ""
    name: str = ""
    description: str = ""
    document_scope: list[str] = field(default_factory=list)
    allowed_capabilities: list[str] = field(default_factory=list)
    allowed_actions: list[str] = field(default_factory=list)
    risk_level_limit: TrialRiskLevel = TrialRiskLevel.LOW
    max_daily_documents: int = 5
    max_batch_size: int = 1
    require_human_review: bool = True
    enabled: bool = False
    created_by: str = ""
    created_time: str = ""
    updated_time: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.trial_id:
            self.trial_id = _uid("TRIAL-")
        now = _now()
        if not self.created_time:
            self.created_time = now
        if not self.updated_time:
            self.updated_time = now

    def is_capability_allowed(self, capability_id: str) -> bool:
        """检查能力是否在试运行范围内。"""
        return capability_id in self.allowed_capabilities

    def is_action_allowed(self, action: str) -> bool:
        """检查执行动作是否在试运行范围内。"""
        return action in self.allowed_actions

    def is_document_allowed(self, document_id: str) -> bool:
        """检查文档是否在试运行范围内。"""
        return document_id in self.document_scope

    def is_risk_allowed(self, risk_level: str) -> bool:
        """检查风险等级是否满足限制。"""
        order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        return order.get(risk_level, 99) <= order.get(self.risk_level_limit.value, 0)

    def to_dict(self) -> dict[str, Any]:
        return {
            "trial_id": self.trial_id,
            "name": self.name,
            "description": self.description,
            "document_scope": self.document_scope,
            "allowed_capabilities": self.allowed_capabilities,
            "allowed_actions": self.allowed_actions,
            "risk_level_limit": self.risk_level_limit.value,
            "max_daily_documents": self.max_daily_documents,
            "max_batch_size": self.max_batch_size,
            "require_human_review": self.require_human_review,
            "enabled": self.enabled,
            "created_by": self.created_by,
            "created_time": self.created_time,
            "updated_time": self.updated_time,
            "metadata": self.metadata,
        }


# ═══════════════════════════════════════════════════════════════════════════
# TrialExecutionRecord — 试运行执行记录
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class TrialExecutionRecord:
    """试运行执行记录——完整记录一次受控试运行的全链路结果。

    不执行真实生产动作——仅记录每层决策结果。

    Fields:
        record_id: 唯一记录 ID
        trial_id: 关联的试运行配置
        document_id: 源文档标识
        capability_id: 匹配到的能力标识
        execution_action: 预期的执行动作
        trial_status: 试运行状态
        block_reason: 阻断原因（如果有）
        evidence_result: Evidence Runtime 输出摘要
        capability_result: Capability Runtime 输出摘要
        execution_result: Execution Runtime 输出摘要
        approval_status: 审批状态
        activation_result: 激活决策结果
        guardrail_result: 护栏检查结果
        permission_result: 权限检查结果
        trace_id: 全链路追溯 ID
        started_time: 开始时间
        completed_time: 完成时间
        human_review: 人工审查记录
        metadata: 扩展元数据
    """
    record_id: str = ""
    trial_id: str = ""
    document_id: str = ""
    capability_id: str = ""
    execution_action: str = ""
    trial_status: TrialStatus = TrialStatus.PENDING
    block_reason: str = ""
    evidence_result: dict[str, Any] = field(default_factory=dict)
    capability_result: dict[str, Any] = field(default_factory=dict)
    execution_result: dict[str, Any] = field(default_factory=dict)
    approval_status: str = ""
    activation_result: dict[str, Any] = field(default_factory=dict)
    guardrail_result: dict[str, Any] = field(default_factory=dict)
    permission_result: dict[str, Any] = field(default_factory=dict)
    trace_id: str = ""
    started_time: str = ""
    completed_time: str = ""
    human_review: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.record_id:
            self.record_id = _uid("TER-")
        if not self.trace_id:
            self.trace_id = _uid("TRACE-")

    @property
    def is_completed(self) -> bool:
        """是否全部通过。"""
        return self.trial_status == TrialStatus.COMPLETED

    @property
    def is_blocked(self) -> bool:
        """是否被阻断。"""
        return self.trial_status == TrialStatus.BLOCKED

    @property
    def blocked_at_layer(self) -> str:
        """返回被阻断的层级。"""
        if not self.block_reason:
            return ""
        layer_map = {
            "evidence_extraction_failed": "Evidence Runtime",
            "capability_match_failed": "Capability Runtime",
            "execution_plan_failed": "Execution Runtime",
            "approval_rejected": "Approval Layer",
            "activation_blocked": "Activation Boundary",
            "guardrail_blocked": "Production Guardrail",
            "permission_blocked": "Permission Check",
            "scope_exceeded": "Trial Scope",
            "batch_limit_exceeded": "Trial Scope",
            "daily_limit_exceeded": "Trial Scope",
        }
        return layer_map.get(self.block_reason, "Unknown")

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "trial_id": self.trial_id,
            "document_id": self.document_id,
            "capability_id": self.capability_id,
            "execution_action": self.execution_action,
            "trial_status": self.trial_status.value,
            "block_reason": self.block_reason,
            "evidence_result": self.evidence_result,
            "capability_result": self.capability_result,
            "execution_result": self.execution_result,
            "approval_status": self.approval_status,
            "activation_result": self.activation_result,
            "guardrail_result": self.guardrail_result,
            "permission_result": self.permission_result,
            "trace_id": self.trace_id,
            "started_time": self.started_time,
            "completed_time": self.completed_time,
            "human_review": self.human_review,
            "metadata": self.metadata,
        }

    def to_summary(self) -> str:
        """生成执行记录的摘要描述。"""
        status_icon = "✅" if self.is_completed else "❌"
        block_info = f" | 阻断: {self.blocked_at_layer}" if self.is_blocked else ""
        return (
            f"{status_icon} [{self.record_id}] "
            f"文档: {self.document_id} | "
            f"能力: {self.capability_id} | "
            f"动作: {self.execution_action} | "
            f"状态: {self.trial_status.value}"
            f"{block_info}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# TrialMetrics — 试运行指标
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class TrialMetrics:
    """试运行指标——收集试运行期间的统计数据。

    Fields:
        trial_id: 关联的试运行配置
        total_documents: 处理的文档总数
        completed_count: 全部通过的文档数
        blocked_count: 被阻断的文档数
        blocked_by_layer: 各层阻断分布
        success_rate: 执行成功率
        approval_rate: 审批通过率
        guardrail_failures: 护栏失败次数
        permission_failures: 权限失败次数
        evidence_gaps: 证据缺失列表
        capability_gaps: 能力缺失列表
        execution_gaps: 执行缺失列表
        generated_time: 指标生成时间
    """
    trial_id: str = ""
    total_documents: int = 0
    completed_count: int = 0
    blocked_count: int = 0
    blocked_by_layer: dict[str, int] = field(default_factory=dict)
    success_rate: float = 0.0
    approval_rate: float = 0.0
    guardrail_failures: int = 0
    permission_failures: int = 0
    evidence_gaps: list[dict[str, Any]] = field(default_factory=list)
    capability_gaps: list[dict[str, Any]] = field(default_factory=list)
    execution_gaps: list[dict[str, Any]] = field(default_factory=list)
    generated_time: str = ""

    def __post_init__(self):
        if not self.generated_time:
            self.generated_time = _now()

    def compute_rates(self):
        """根据计数计算比率。"""
        if self.total_documents > 0:
            self.success_rate = self.completed_count / self.total_documents
            self.approval_rate = (
                self.completed_count / self.total_documents
                if self.total_documents > 0
                else 0.0
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "trial_id": self.trial_id,
            "total_documents": self.total_documents,
            "completed_count": self.completed_count,
            "blocked_count": self.blocked_count,
            "blocked_by_layer": self.blocked_by_layer,
            "success_rate": self.success_rate,
            "approval_rate": self.approval_rate,
            "guardrail_failures": self.guardrail_failures,
            "permission_failures": self.permission_failures,
            "evidence_gaps": self.evidence_gaps,
            "capability_gaps": self.capability_gaps,
            "execution_gaps": self.execution_gaps,
            "generated_time": self.generated_time,
        }

    def to_summary(self) -> str:
        """生成指标摘要。"""
        return (
            f"试运行 [{self.trial_id}] 指标:\n"
            f"  文档总数: {self.total_documents}\n"
            f"  ✅ 通过: {self.completed_count} | "
            f"❌ 阻断: {self.blocked_count}\n"
            f"  成功率: {self.success_rate:.1%} | "
            f"审批通过率: {self.approval_rate:.1%}\n"
            f"  护栏失败: {self.guardrail_failures} | "
            f"权限失败: {self.permission_failures}\n"
            f"  证据缺失: {len(self.evidence_gaps)} | "
            f"能力缺失: {len(self.capability_gaps)} | "
            f"执行缺失: {len(self.execution_gaps)}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# TrialBatchResult — 批量试运行结果
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class TrialBatchResult:
    """批量试运行结果——汇总多次试运行。"""
    batch_id: str = ""
    trial_id: str = ""
    generated_at: str = ""
    total_records: int = 0
    records: list[TrialExecutionRecord] = field(default_factory=list)
    metrics: Optional[TrialMetrics] = None
    summary: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.batch_id:
            self.batch_id = _uid("TBR-")
        if not self.generated_at:
            self.generated_at = _now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "trial_id": self.trial_id,
            "generated_at": self.generated_at,
            "total_records": self.total_records,
            "records": [r.to_dict() for r in self.records],
            "metrics": self.metrics.to_dict() if self.metrics else None,
            "summary": self.summary,
        }


__all__ = [
    "TrialStatus",
    "TrialBlockReason",
    "TrialExecutionPhase",
    "TrialRiskLevel",
    "TrialConfiguration",
    "TrialExecutionRecord",
    "TrialMetrics",
    "TrialBatchResult",
]