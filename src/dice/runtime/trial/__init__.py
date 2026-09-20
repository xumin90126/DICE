"""
受控生产试运行运行时 — Controlled Production Trial (Phase 4).

独立的试运行管理层：不属于 Evidence Runtime、不属于 Capability Runtime、
不属于 Execution Runtime、不属于审批/激活/护栏层。

回答一个问题：

    "已通过全部治理层验证的请求，在受控条件下试运行效果如何？"

架构位置：
    Evidence Runtime → Capability Runtime → Execution Runtime
                                                 ↓
                                         Approval Layer
                                                 ↓
                                         Activation Boundary
                                                 ↓
                                         Production Guardrail
                                                 ↓
                                         Permission Check
                                                 ↓
                                         Controlled Trial Runtime (本层)
                                                 ↓
                                         Trial Execution Record

设计约束：
    - 禁止执行真实生产动作
    - 禁止绕过任何一层治理
    - 禁止自动批准
    - 禁止自动扩大试运行范围
    - 禁止自动移除人工审查
"""

from dice.runtime.trial.models import (
    TrialConfiguration,
    TrialExecutionRecord,
    TrialMetrics,
    TrialBatchResult,
    TrialStatus,
    TrialBlockReason,
    TrialExecutionPhase,
    TrialRiskLevel,
)
from dice.runtime.trial.trial_manager import (
    TrialScopeChange,
    TrialManager,
)
from dice.runtime.trial.trial_runner import (
    ControlledTrialRunner,
)
from dice.runtime.trial.monitor import (
    FailureDistribution,
    RiskReport,
    TrialMonitor,
)

__all__ = [
    # 数据模型
    "TrialConfiguration",
    "TrialExecutionRecord",
    "TrialMetrics",
    "TrialBatchResult",
    "TrialStatus",
    "TrialBlockReason",
    "TrialExecutionPhase",
    "TrialRiskLevel",
    # 管理器
    "TrialScopeChange",
    "TrialManager",
    # 执行器
    "ControlledTrialRunner",
    # 监控
    "FailureDistribution",
    "RiskReport",
    "TrialMonitor",
]