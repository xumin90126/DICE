"""
试运行管理器 — Phase 4.

TrialManager：管理受控生产试运行的配置和生命周期。

职责：
    1. 创建和管理 TrialConfiguration
    2. 启用/禁用试运行
    3. 验证文档/能力/动作是否在试运行范围内
    4. 记录配置变更审计

设计约束：
    - 禁止自动扩大试运行范围
    - 禁止自动添加能力
    - 禁止自动添加文档
    - 禁止自动添加执行动作
    - 禁止自动降低风险等级限制
    - 禁止自动移除人工审查要求
    - 不属于任何 Runtime 层——是独立的试运行管理层
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from dice.runtime.trial.models import (
    TrialConfiguration,
    TrialRiskLevel,
    _now,
    _uid,
)


# ═══════════════════════════════════════════════════════════════════════════
# TrialScopeChange — 试运行范围变更审计记录
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class TrialScopeChange:
    """试运行范围变更审计记录。

    Fields:
        change_id: 变更唯一 ID
        trial_id: 关联的试运行配置
        change_type: 变更类型（add_capability, remove_capability 等）
        before_value: 变更前的值
        after_value: 变更后的值
        changed_by: 变更者
        changed_time: 变更时间
        reason: 变更原因
    """
    change_id: str = ""
    trial_id: str = ""
    change_type: str = ""
    before_value: Any = None
    after_value: Any = None
    changed_by: str = ""
    changed_time: str = ""
    reason: str = ""

    def __post_init__(self):
        if not self.change_id:
            self.change_id = _uid("TSC-")
        if not self.changed_time:
            self.changed_time = _now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "change_id": self.change_id,
            "trial_id": self.trial_id,
            "change_type": self.change_type,
            "before_value": self.before_value,
            "after_value": self.after_value,
            "changed_by": self.changed_by,
            "changed_time": self.changed_time,
            "reason": self.reason,
        }


# ═══════════════════════════════════════════════════════════════════════════
# TrialManager
# ═══════════════════════════════════════════════════════════════════════════


class TrialManager:
    """试运行管理器——管理受控生产试运行的配置。

    使用方式：
        manager = TrialManager()
        config = manager.create_trial(
            name="第一次试运行",
            document_scope=["doc_001"],
            allowed_capabilities=["CAP-TROUBLESHOOT-DETECT"],
            allowed_actions=["detect_troubleshooting"],
        )
        manager.enable_trial(config.trial_id)
    """

    def __init__(self, storage_dir: Optional[str] = None):
        """
        Args:
            storage_dir: 配置存储目录，默认 dice_output/phase4_trials/
        """
        if storage_dir is None:
            storage_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "dice_output",
                "phase4_trials",
            )
        self.storage_dir = storage_dir
        self._configs: dict[str, TrialConfiguration] = {}
        self._change_logs: list[TrialScopeChange] = []
        os.makedirs(self.storage_dir, exist_ok=True)

    # ── 创建和查询 ──────────────────────────────────────────────────

    def create_trial(
        self,
        name: str,
        description: str = "",
        document_scope: Optional[list[str]] = None,
        allowed_capabilities: Optional[list[str]] = None,
        allowed_actions: Optional[list[str]] = None,
        risk_level_limit: TrialRiskLevel = TrialRiskLevel.LOW,
        max_daily_documents: int = 5,
        max_batch_size: int = 1,
        require_human_review: bool = True,
        created_by: str = "system",
        metadata: Optional[dict[str, Any]] = None,
    ) -> TrialConfiguration:
        """创建新的试运行配置。

        默认 disabled——必须显式调用 enable_trial() 启用。

        Returns:
            新创建的 TrialConfiguration
        """
        config = TrialConfiguration(
            name=name,
            description=description,
            document_scope=document_scope or [],
            allowed_capabilities=allowed_capabilities or [],
            allowed_actions=allowed_actions or [],
            risk_level_limit=risk_level_limit,
            max_daily_documents=max_daily_documents,
            max_batch_size=max_batch_size,
            require_human_review=require_human_review,
            enabled=False,  # 默认禁用
            created_by=created_by,
            metadata=metadata or {},
        )
        self._configs[config.trial_id] = config
        self._save_config(config)
        return config

    def get_trial(self, trial_id: str) -> Optional[TrialConfiguration]:
        """获取试运行配置。"""
        if trial_id in self._configs:
            return self._configs[trial_id]
        # 尝试从磁盘加载
        config = self._load_config(trial_id)
        if config:
            self._configs[trial_id] = config
        return config

    def list_trials(self) -> list[TrialConfiguration]:
        """列出所有试运行配置。"""
        return list(self._configs.values())

    def get_active_trials(self) -> list[TrialConfiguration]:
        """获取所有已启用的试运行。"""
        return [c for c in self._configs.values() if c.enabled]

    # ── 启用/禁用 ──────────────────────────────────────────────────

    def enable_trial(self, trial_id: str) -> bool:
        """启用试运行。"""
        config = self.get_trial(trial_id)
        if config is None:
            return False
        config.enabled = True
        config.updated_time = _now()
        self._save_config(config)
        return True

    def disable_trial(self, trial_id: str, reason: str = "") -> bool:
        """禁用试运行。"""
        config = self.get_trial(trial_id)
        if config is None:
            return False
        config.enabled = False
        config.updated_time = _now()
        self._record_change(
            config.trial_id,
            "disable_trial",
            True,
            False,
            reason=reason,
        )
        self._save_config(config)
        return True

    # ── 范围管理 ───────────────────────────────────────────────────

    def add_capability(
        self, trial_id: str, capability_id: str, reason: str = ""
    ) -> bool:
        """添加能力到试运行范围。"""
        config = self.get_trial(trial_id)
        if config is None or capability_id in config.allowed_capabilities:
            return False
        before = list(config.allowed_capabilities)
        config.allowed_capabilities.append(capability_id)
        config.updated_time = _now()
        self._record_change(
            trial_id, "add_capability", before, config.allowed_capabilities, reason
        )
        self._save_config(config)
        return True

    def remove_capability(
        self, trial_id: str, capability_id: str, reason: str = ""
    ) -> bool:
        """从试运行范围中移除能力。"""
        config = self.get_trial(trial_id)
        if config is None or capability_id not in config.allowed_capabilities:
            return False
        before = list(config.allowed_capabilities)
        config.allowed_capabilities.remove(capability_id)
        config.updated_time = _now()
        self._record_change(
            trial_id, "remove_capability", before, config.allowed_capabilities, reason
        )
        self._save_config(config)
        return True

    def add_document(
        self, trial_id: str, document_id: str, reason: str = ""
    ) -> bool:
        """添加文档到试运行范围。"""
        config = self.get_trial(trial_id)
        if config is None or document_id in config.document_scope:
            return False
        before = list(config.document_scope)
        config.document_scope.append(document_id)
        config.updated_time = _now()
        self._record_change(
            trial_id, "add_document", before, config.document_scope, reason
        )
        self._save_config(config)
        return True

    def add_action(
        self, trial_id: str, action: str, reason: str = ""
    ) -> bool:
        """添加执行动作到试运行范围。"""
        config = self.get_trial(trial_id)
        if config is None or action in config.allowed_actions:
            return False
        before = list(config.allowed_actions)
        config.allowed_actions.append(action)
        config.updated_time = _now()
        self._record_change(
            trial_id, "add_action", before, config.allowed_actions, reason
        )
        self._save_config(config)
        return True

    # ── 验证 ───────────────────────────────────────────────────────

    def validate_document(self, trial_id: str, document_id: str) -> bool:
        """验证文档是否在试运行范围内。"""
        config = self.get_trial(trial_id)
        if config is None or not config.enabled:
            return False
        # 空 document_scope = 全部禁止
        if not config.document_scope:
            return False
        return config.is_document_allowed(document_id)

    def validate_capability(self, trial_id: str, capability_id: str) -> bool:
        """验证能力是否在试运行范围内。"""
        config = self.get_trial(trial_id)
        if config is None or not config.enabled:
            return False
        if not config.allowed_capabilities:
            return False
        return config.is_capability_allowed(capability_id)

    def validate_action(self, trial_id: str, action: str) -> bool:
        """验证执行动作是否在试运行范围内。"""
        config = self.get_trial(trial_id)
        if config is None or not config.enabled:
            return False
        if not config.allowed_actions:
            return False
        return config.is_action_allowed(action)

    def validate_risk(self, trial_id: str, risk_level: str) -> bool:
        """验证风险等级是否在试运行范围内。"""
        config = self.get_trial(trial_id)
        if config is None or not config.enabled:
            return False
        return config.is_risk_allowed(risk_level)

    # ── 审计 ───────────────────────────────────────────────────────

    def get_change_log(self, trial_id: str) -> list[TrialScopeChange]:
        """获取试运行的变更日志。"""
        return [c for c in self._change_logs if c.trial_id == trial_id]

    def get_all_change_logs(self) -> list[TrialScopeChange]:
        """获取所有变更日志。"""
        return list(self._change_logs)

    # ── 内部方法 ───────────────────────────────────────────────────

    def _record_change(
        self,
        trial_id: str,
        change_type: str,
        before_value: Any,
        after_value: Any,
        reason: str = "",
        changed_by: str = "system",
    ):
        """记录范围变更。"""
        change = TrialScopeChange(
            trial_id=trial_id,
            change_type=change_type,
            before_value=before_value,
            after_value=after_value,
            changed_by=changed_by,
            reason=reason,
        )
        self._change_logs.append(change)

    def _save_config(self, config: TrialConfiguration):
        """保存配置到磁盘。"""
        filepath = os.path.join(self.storage_dir, f"{config.trial_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)

    def _load_config(self, trial_id: str) -> Optional[TrialConfiguration]:
        """从磁盘加载配置。"""
        filepath = os.path.join(self.storage_dir, f"{trial_id}.json")
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return TrialConfiguration(
                trial_id=data.get("trial_id", ""),
                name=data.get("name", ""),
                description=data.get("description", ""),
                document_scope=data.get("document_scope", []),
                allowed_capabilities=data.get("allowed_capabilities", []),
                allowed_actions=data.get("allowed_actions", []),
                risk_level_limit=TrialRiskLevel(data.get("risk_level_limit", "low")),
                max_daily_documents=data.get("max_daily_documents", 5),
                max_batch_size=data.get("max_batch_size", 1),
                require_human_review=data.get("require_human_review", True),
                enabled=data.get("enabled", False),
                created_by=data.get("created_by", ""),
                created_time=data.get("created_time", ""),
                updated_time=data.get("updated_time", ""),
                metadata=data.get("metadata", {}),
            )
        except Exception:
            return None


__all__ = [
    "TrialScopeChange",
    "TrialManager",
]