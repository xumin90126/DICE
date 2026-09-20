"""
生产安全护栏数据模型 — Phase 3 Step 3.

Production Guardrail Layer 的核心数据结构。

设计原则：
    1. ProductionExecutionPermissionResult 只消费已通过的 ActivationDecision
    2. 权限状态严格控制：ALLOW / BLOCK / REVIEW_REQUIRED
    3. 任何权限决策必须可审计
    4. 禁止绕过激活边界直接进入执行

架构约束：
    - 不属于任何 Runtime 层
    - 是独立的生产安全入口层
    - 六层架构中的最后一层（执行前最终门禁）
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


class PermissionStatus(str, Enum):
    """权限状态枚举。

    状态转换规则：
        未评估 → ALLOW           (五重检查全部通过)
        未评估 → BLOCK           (任何安全门禁失败)
        未评估 → REVIEW_REQUIRED (证据链或回滚能力不足，需人工审查)

    终态：
        ALLOW           → 可进入执行入口
        BLOCK           → 禁止进入执行
        REVIEW_REQUIRED → 暂停，等待人工审查
    """
    ALLOW = "ALLOW"                       # 允许进入执行
    BLOCK = "BLOCK"                       # 阻止进入执行
    REVIEW_REQUIRED = "REVIEW_REQUIRED"   # 需要人工审查


class GuardrailCheckType(str, Enum):
    """护栏检查类型枚举。"""
    APPROVAL_VALIDATION = "approval_validation"           # 审批验证
    ACTIVATION_VALIDATION = "activation_validation"       # 激活验证
    EXECUTION_SAFETY = "execution_safety"                 # 执行安全
    EVIDENCE_COVERAGE = "evidence_coverage"               # 证据覆盖
    ROLLBACK_CAPABILITY = "rollback_capability"           # 回滚能力


class GuardrailBlockReason(str, Enum):
    """护栏阻止原因枚举。"""
    APPROVAL_NOT_APPROVED = "approval_not_approved"
    APPROVAL_TRACE_INCOMPLETE = "approval_trace_incomplete"
    ACTIVATION_NOT_ALLOWED = "activation_not_allowed"
    ACTIVATION_AUDIT_MISSING = "activation_audit_missing"
    RISK_LEVEL_TOO_HIGH = "risk_level_too_high"
    CONFIDENCE_TOO_LOW = "confidence_too_low"
    EXECUTION_INPUTS_MISSING = "execution_inputs_missing"
    EVIDENCE_CHAIN_BROKEN = "evidence_chain_broken"
    EVIDENCE_COVERAGE_INSUFFICIENT = "evidence_coverage_insufficient"
    ROLLBACK_PATH_MISSING = "rollback_path_missing"
    RECOVERY_UNDEFINED = "recovery_undefined"
    UNAUTHORIZED_EXECUTION_ATTEMPT = "unauthorized_execution_attempt"


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
# GuardrailCheckResult — 单项检查结果
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class GuardrailCheckResult:
    """单项护栏检查结果。

    Fields:
        check_type: 检查类型
        passed: 是否通过
        detail: 检查详情
        risk_level: 本检查的风险等级
        recommendation: 如果未通过，给出的建议
        metadata: 扩展元数据
    """
    check_type: GuardrailCheckType = GuardrailCheckType.APPROVAL_VALIDATION
    passed: bool = False
    detail: str = ""
    risk_level: str = "low"
    recommendation: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_type": self.check_type.value,
            "passed": self.passed,
            "detail": self.detail,
            "risk_level": self.risk_level,
            "recommendation": self.recommendation,
            "metadata": self.metadata,
        }

    def to_summary(self) -> str:
        icon = "✓" if self.passed else "✗"
        return f"{icon} [{self.check_type.value}] {self.detail}"


# ═══════════════════════════════════════════════════════════════════════════
# ProductionExecutionPermissionResult — 执行权限结果
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class ProductionExecutionPermissionResult:
    """生产执行权限结果——最终安全入口的决策输出。

    每一条 ProductionExecutionPermissionResult 可以完整追溯：
        ApprovalRequest → ActivationDecision → Guardrail → PermissionResult

    Fields:
        permission_id: 唯一权限结果 ID
        request_id: 关联的审批请求 ID
        document_id: 源文档标识
        activation_id: 关联的激活决策 ID
        execution_plan_id: 执行计划标识
        capability_id: 关联的能力标识
        permission_status: 权限状态（ALLOW / BLOCK / REVIEW_REQUIRED）
        allowed: 是否允许进入执行（ALLOW 时为 True）
        blocked_reason: 阻止原因（如果 BLOCKED）
        risk_level: 当前风险等级
        confidence: 当前置信度
        approval_reference: 审批引用
        activation_reference: 激活引用
        guardrail_checks: 五重检查结果
        audit_trace: 审计追溯引用
        reasoning: 综合推理
        created_time: 创建时间
        metadata: 扩展元数据
    """
    permission_id: str = ""
    request_id: str = ""
    document_id: str = ""
    activation_id: str = ""
    execution_plan_id: str = ""
    capability_id: str = ""
    permission_status: PermissionStatus = PermissionStatus.BLOCK
    allowed: bool = False
    blocked_reason: str = ""
    risk_level: str = "low"
    confidence: float = 0.0
    approval_reference: str = ""
    activation_reference: str = ""
    guardrail_checks: list[GuardrailCheckResult] = field(default_factory=list)
    audit_trace: str = ""
    reasoning: str = ""
    created_time: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.permission_id:
            self.permission_id = _uid("GDR-")
        if not self.created_time:
            self.created_time = _now()

    def is_allowed(self) -> bool:
        """是否允许进入执行。"""
        return self.permission_status == PermissionStatus.ALLOW

    def is_blocked(self) -> bool:
        """是否被阻止。"""
        return self.permission_status == PermissionStatus.BLOCK

    def needs_review(self) -> bool:
        """是否需要人工审查。"""
        return self.permission_status == PermissionStatus.REVIEW_REQUIRED

    def passed_checks(self) -> list[GuardrailCheckResult]:
        """获取通过的检查项。"""
        return [c for c in self.guardrail_checks if c.passed]

    def failed_checks(self) -> list[GuardrailCheckResult]:
        """获取失败的检查项。"""
        return [c for c in self.guardrail_checks if not c.passed]

    def check_count(self) -> dict[str, int]:
        """统计检查项通过/失败/审查数量。"""
        passed = sum(1 for c in self.guardrail_checks if c.passed)
        failed = len(self.guardrail_checks) - passed
        return {
            "total": len(self.guardrail_checks),
            "passed": passed,
            "failed": failed,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "permission_id": self.permission_id,
            "request_id": self.request_id,
            "document_id": self.document_id,
            "activation_id": self.activation_id,
            "execution_plan_id": self.execution_plan_id,
            "capability_id": self.capability_id,
            "permission_status": self.permission_status.value,
            "allowed": self.allowed,
            "blocked_reason": self.blocked_reason,
            "risk_level": self.risk_level,
            "confidence": self.confidence,
            "approval_reference": self.approval_reference,
            "activation_reference": self.activation_reference,
            "guardrail_checks": [c.to_dict() for c in self.guardrail_checks],
            "audit_trace": self.audit_trace,
            "reasoning": self.reasoning,
            "created_time": self.created_time,
            "metadata": self.metadata,
        }

    def to_summary(self) -> str:
        """生成执行权限结果的摘要描述。"""
        icon_map = {
            PermissionStatus.ALLOW: "✅",
            PermissionStatus.BLOCK: "❌",
            PermissionStatus.REVIEW_REQUIRED: "⚠️",
        }
        icon = icon_map.get(self.permission_status, "❓")
        checks = f"{self.check_count()['passed']}/{self.check_count()['total']} 通过"
        block_info = ""
        if self.blocked_reason:
            block_info = f" | 阻止原因: {self.blocked_reason}"
        return (
            f"{icon} [{self.permission_status.value}] "
            f"文档: {self.document_id} | "
            f"能力: {self.capability_id} | "
            f"风险: {self.risk_level} | "
            f"置信度: {self.confidence:.2f} | "
            f"检查: [{checks}]"
            f"{block_info}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# GuardrailAuditRecord — 护栏审计记录
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class GuardrailAuditRecord:
    """护栏审计记录——每次权限决策的不可变记录。

    Fields:
        audit_id: 审计记录唯一 ID
        permission_id: 关联的权限结果
        request_id: 关联的审批请求
        document_id: 源文档
        permission_status: 权限结果
        validated_by: 验证者（"system" 或 "human"）
        validation_checks: 各项检查结果
        timestamp: 记录时间
        reason: 决策原因
        metadata: 扩展元数据
    """
    audit_id: str = ""
    permission_id: str = ""
    request_id: str = ""
    document_id: str = ""
    permission_status: PermissionStatus = PermissionStatus.BLOCK
    validated_by: str = ""
    validation_checks: dict[str, bool] = field(default_factory=dict)
    timestamp: str = ""
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.audit_id:
            self.audit_id = _uid("GDA-")
        if not self.timestamp:
            self.timestamp = _now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "permission_id": self.permission_id,
            "request_id": self.request_id,
            "document_id": self.document_id,
            "permission_status": self.permission_status.value,
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
            f"{self.permission_status.value} | "
            f"检查: [{checks}] | "
            f"原因: {self.reason}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# GuardrailBatchResult — 批量护栏结果
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class GuardrailBatchResult:
    """批量护栏结果——用于多文档权限决策的汇总。"""
    batch_id: str = ""
    generated_at: str = ""
    total_permissions: int = 0
    permissions: list[ProductionExecutionPermissionResult] = field(default_factory=list)
    audit_records: list[GuardrailAuditRecord] = field(default_factory=list)
    statistics: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.batch_id:
            self.batch_id = _uid("GDB-")
        if not self.generated_at:
            self.generated_at = _now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "generated_at": self.generated_at,
            "total_permissions": self.total_permissions,
            "permissions": [p.to_dict() for p in self.permissions],
            "audit_records": [a.to_dict() for a in self.audit_records],
            "statistics": self.statistics,
        }


__all__ = [
    "ProductionExecutionPermissionResult",
    "GuardrailCheckResult",
    "GuardrailAuditRecord",
    "GuardrailBatchResult",
    "PermissionStatus",
    "GuardrailCheckType",
    "GuardrailBlockReason",
]