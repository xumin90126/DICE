"""
激活范围管理器 — Phase 3 Step 4.

Production Activation Scope Manager：管理允许进入生产执行的范围。

职责：
    1. 定义 ActivationScope——哪些能力/动作/文档可以进入真实执行
    2. 管理白名单——Capability、Action、Document 类型
    3. 限制风险等级、批次大小
    4. 禁止自动扩大 scope

设计约束：
    - 禁止自动扩大 scope
    - 禁止自动添加 capability
    - 禁止自动批准 execution
    - 禁止根据文档内容动态放开权限

不属于任何 Runtime 层——是独立的范围管理层。
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from dice.runtime.activation.models import ActivationRiskLevel


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
# ActivationScope — 激活范围
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class ActivationScope:
    """激活范围——定义哪些操作可以进入真实生产执行。

    设计原则：
        - 生产能力不是全部开放
        - 通过白名单严格限制
        - 每次变更都需要显式操作

    Fields:
        scope_id: 唯一范围 ID
        name: 范围名称（人类可读）
        description: 范围描述
        allowed_capabilities: 允许的能力 ID 白名单（空列表 = 全部禁止）
        allowed_actions: 允许的执行动作白名单（空列表 = 全部禁止）
        document_types: 允许的文档类型白名单（空列表 = 全部禁止）
        risk_level_limit: 允许的最高风险等级（默认 LOW）
        max_batch_size: 最大批次大小（默认 1）
        enabled: 是否启用
        require_human_approval: 是否要求人工审批（默认 True）
        created_by: 创建者
        created_time: 创建时间
        updated_time: 最后更新时间
        metadata: 扩展元数据
    """
    scope_id: str = ""
    name: str = ""
    description: str = ""
    allowed_capabilities: list[str] = field(default_factory=list)
    allowed_actions: list[str] = field(default_factory=list)
    document_types: list[str] = field(default_factory=list)
    risk_level_limit: ActivationRiskLevel = ActivationRiskLevel.LOW
    max_batch_size: int = 1
    enabled: bool = False
    require_human_approval: bool = True
    created_by: str = ""
    created_time: str = ""
    updated_time: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.scope_id:
            self.scope_id = _uid("SCOPE-")
        now = _now()
        if not self.created_time:
            self.created_time = now
        if not self.updated_time:
            self.updated_time = now

    def allows_capability(self, capability_id: str) -> bool:
        """检查是否允许指定能力。"""
        if not self.enabled:
            return False
        if not self.allowed_capabilities:
            return False
        return capability_id in self.allowed_capabilities

    def allows_action(self, action: str) -> bool:
        """检查是否允许指定动作。"""
        if not self.enabled:
            return False
        if not self.allowed_actions:
            return False
        return action in self.allowed_actions

    def allows_document_type(self, doc_type: str) -> bool:
        """检查是否允许指定文档类型。"""
        if not self.enabled:
            return False
        if not self.document_types:
            return False
        return doc_type in self.document_types

    def allows_risk_level(self, risk_level: ActivationRiskLevel) -> bool:
        """检查风险等级是否在允许范围内。"""
        if not self.enabled:
            return False
        # 风险等级排序：LOW < MEDIUM < HIGH < CRITICAL
        risk_order = {
            ActivationRiskLevel.LOW: 0,
            ActivationRiskLevel.MEDIUM: 1,
            ActivationRiskLevel.HIGH: 2,
            ActivationRiskLevel.CRITICAL: 3,
        }
        return risk_order.get(risk_level, 99) <= risk_order.get(self.risk_level_limit, 0)

    def allows_batch_size(self, size: int) -> bool:
        """检查批次大小是否在允许范围内。"""
        if not self.enabled:
            return False
        return size <= self.max_batch_size

    def to_dict(self) -> dict[str, Any]:
        return {
            "scope_id": self.scope_id,
            "name": self.name,
            "description": self.description,
            "allowed_capabilities": self.allowed_capabilities,
            "allowed_actions": self.allowed_actions,
            "document_types": self.document_types,
            "risk_level_limit": self.risk_level_limit.value,
            "max_batch_size": self.max_batch_size,
            "enabled": self.enabled,
            "require_human_approval": self.require_human_approval,
            "created_by": self.created_by,
            "created_time": self.created_time,
            "updated_time": self.updated_time,
            "metadata": self.metadata,
        }

    def to_summary(self) -> str:
        """生成范围摘要描述。"""
        status = "✅ 启用" if self.enabled else "❌ 禁用"
        caps = ", ".join(self.allowed_capabilities) if self.allowed_capabilities else "（无）"
        actions = ", ".join(self.allowed_actions) if self.allowed_actions else "（无）"
        return (
            f"[{status}] {self.name}: "
            f"能力=[{caps}], "
            f"动作=[{actions}], "
            f"风险限制={self.risk_level_limit.value}, "
            f"批次上限={self.max_batch_size}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# ActivationScopeManager — 范围管理器
# ═══════════════════════════════════════════════════════════════════════════


class ActivationScopeManager:
    """激活范围管理器。

    管理所有 ActivationScope，提供查询、创建、更新、启用/禁用功能。

    设计约束：
        - 禁止自动扩大 scope
        - 禁止自动添加 capability
        - 禁止自动批准 execution
        - 所有变更必须显式调用

    使用方式：
        manager = ActivationScopeManager()

        # 创建测试范围
        scope = manager.create_scope(
            name="Test Scope",
            allowed_capabilities=["CAP-TROUBLESHOOT-DETECT"],
            allowed_actions=["detect_troubleshooting"],
            risk_level_limit=ActivationRiskLevel.LOW,
        )

        # 检查能力是否在范围内
        if manager.is_capability_allowed("CAP-TROUBLESHOOT-DETECT"):
            ...
    """

    def __init__(self) -> None:
        """初始化范围管理器。"""
        self._scopes: dict[str, ActivationScope] = {}
        self._change_log: list[dict[str, Any]] = []

    # ═══════════════════════════════════════════════════════════════════
    # 范围管理
    # ═══════════════════════════════════════════════════════════════════

    def create_scope(
        self,
        name: str,
        description: str = "",
        allowed_capabilities: Optional[list[str]] = None,
        allowed_actions: Optional[list[str]] = None,
        document_types: Optional[list[str]] = None,
        risk_level_limit: ActivationRiskLevel = ActivationRiskLevel.LOW,
        max_batch_size: int = 1,
        enabled: bool = False,
        require_human_approval: bool = True,
        created_by: str = "system",
        metadata: Optional[dict[str, Any]] = None,
    ) -> ActivationScope:
        """创建新的激活范围。

        默认 disabled——必须显式启用。

        参数:
            name: 范围名称
            description: 范围描述
            allowed_capabilities: 允许的能力 ID 白名单
            allowed_actions: 允许的执行动作白名单
            document_types: 允许的文档类型白名单
            risk_level_limit: 允许的最高风险等级
            max_batch_size: 最大批次大小
            enabled: 是否立即启用（默认 False）
            require_human_approval: 是否要求人工审批
            created_by: 创建者
            metadata: 扩展元数据

        返回:
            ActivationScope 新创建的范围
        """
        scope = ActivationScope(
            name=name,
            description=description,
            allowed_capabilities=allowed_capabilities or [],
            allowed_actions=allowed_actions or [],
            document_types=document_types or [],
            risk_level_limit=risk_level_limit,
            max_batch_size=max_batch_size,
            enabled=enabled,
            require_human_approval=require_human_approval,
            created_by=created_by,
            metadata=metadata or {},
        )

        self._scopes[scope.scope_id] = scope
        self._log_change("create", scope.scope_id, f"创建范围: {name}", created_by)

        return scope

    def enable_scope(self, scope_id: str, by: str = "system") -> bool:
        """启用指定范围。

        参数:
            scope_id: 范围 ID
            by: 操作者

        返回:
            bool 是否成功
        """
        scope = self._scopes.get(scope_id)
        if not scope:
            return False

        scope.enabled = True
        scope.updated_time = _now()
        self._log_change("enable", scope_id, f"启用范围: {scope.name}", by)
        return True

    def disable_scope(self, scope_id: str, by: str = "system") -> bool:
        """禁用指定范围。

        参数:
            scope_id: 范围 ID
            by: 操作者

        返回:
            bool 是否成功
        """
        scope = self._scopes.get(scope_id)
        if not scope:
            return False

        scope.enabled = False
        scope.updated_time = _now()
        self._log_change("disable", scope_id, f"禁用范围: {scope.name}", by)
        return True

    def update_scope(
        self,
        scope_id: str,
        allowed_capabilities: Optional[list[str]] = None,
        allowed_actions: Optional[list[str]] = None,
        document_types: Optional[list[str]] = None,
        risk_level_limit: Optional[ActivationRiskLevel] = None,
        max_batch_size: Optional[int] = None,
        by: str = "system",
    ) -> Optional[ActivationScope]:
        """更新范围配置。

        禁止自动扩大 scope——每次变更都需要显式调用此方法。

        参数:
            scope_id: 范围 ID
            allowed_capabilities: 新的能力白名单
            allowed_actions: 新的动作白名单
            document_types: 新的文档类型白名单
            risk_level_limit: 新的风险等级限制
            max_batch_size: 新的批次大小限制
            by: 操作者

        返回:
            Optional[ActivationScope] 更新后的范围，不存在时返回 None
        """
        scope = self._scopes.get(scope_id)
        if not scope:
            return None

        changes: list[str] = []

        if allowed_capabilities is not None:
            scope.allowed_capabilities = allowed_capabilities
            changes.append(f"能力白名单: {len(allowed_capabilities)} 项")
        if allowed_actions is not None:
            scope.allowed_actions = allowed_actions
            changes.append(f"动作白名单: {len(allowed_actions)} 项")
        if document_types is not None:
            scope.document_types = document_types
            changes.append(f"文档类型: {len(document_types)} 项")
        if risk_level_limit is not None:
            scope.risk_level_limit = risk_level_limit
            changes.append(f"风险限制: {risk_level_limit.value}")
        if max_batch_size is not None:
            scope.max_batch_size = max_batch_size
            changes.append(f"批次上限: {max_batch_size}")

        scope.updated_time = _now()
        self._log_change(
            "update", scope_id,
            f"更新范围: {scope.name} ({', '.join(changes)})",
            by,
        )

        return scope

    # ═══════════════════════════════════════════════════════════════════
    # 查询方法
    # ═══════════════════════════════════════════════════════════════════

    def get_scope(self, scope_id: str) -> Optional[ActivationScope]:
        """获取指定范围。"""
        return self._scopes.get(scope_id)

    def get_enabled_scopes(self) -> list[ActivationScope]:
        """获取所有已启用的范围。"""
        return [s for s in self._scopes.values() if s.enabled]

    def get_all_scopes(self) -> list[ActivationScope]:
        """获取所有范围。"""
        return list(self._scopes.values())

    def is_capability_allowed(self, capability_id: str) -> bool:
        """检查是否有任何已启用范围允许指定能力。"""
        for scope in self.get_enabled_scopes():
            if scope.allows_capability(capability_id):
                return True
        return False

    def is_action_allowed(self, action: str) -> bool:
        """检查是否有任何已启用范围允许指定动作。"""
        for scope in self.get_enabled_scopes():
            if scope.allows_action(action):
                return True
        return False

    def is_document_type_allowed(self, doc_type: str) -> bool:
        """检查是否有任何已启用范围允许指定文档类型。"""
        for scope in self.get_enabled_scopes():
            if scope.allows_document_type(doc_type):
                return True
        return False

    def get_scopes_for_capability(
        self, capability_id: str
    ) -> list[ActivationScope]:
        """获取允许指定能力的所有已启用范围。"""
        return [
            s for s in self.get_enabled_scopes()
            if s.allows_capability(capability_id)
        ]

    # ═══════════════════════════════════════════════════════════════════
    # 变更日志
    # ═══════════════════════════════════════════════════════════════════

    def _log_change(
        self,
        action: str,
        scope_id: str,
        detail: str,
        by: str,
    ) -> None:
        """记录范围变更。"""
        self._change_log.append({
            "timestamp": _now(),
            "action": action,
            "scope_id": scope_id,
            "detail": detail,
            "by": by,
        })

    def get_change_log(self) -> list[dict[str, Any]]:
        """获取变更日志。"""
        return list(self._change_log)

    # ═══════════════════════════════════════════════════════════════════
    # 统计
    # ═══════════════════════════════════════════════════════════════════

    def get_statistics(self) -> dict[str, Any]:
        """获取范围统计信息。"""
        total = len(self._scopes)
        enabled = len(self.get_enabled_scopes())
        disabled = total - enabled

        all_caps: set[str] = set()
        all_actions: set[str] = set()
        all_doc_types: set[str] = set()
        for scope in self.get_enabled_scopes():
            all_caps.update(scope.allowed_capabilities)
            all_actions.update(scope.allowed_actions)
            all_doc_types.update(scope.document_types)

        return {
            "total_scopes": total,
            "enabled": enabled,
            "disabled": disabled,
            "total_unique_capabilities": len(all_caps),
            "total_unique_actions": len(all_actions),
            "total_unique_document_types": len(all_doc_types),
            "total_changes": len(self._change_log),
        }


__all__ = [
    "ActivationScope",
    "ActivationScopeManager",
]