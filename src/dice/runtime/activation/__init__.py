"""激活边界运行时 — Controlled Activation Boundary (Phase 3 Step 2).

独立的激活边界层：不属于 Evidence Runtime、不属于 Capability Runtime、
不属于 Execution Runtime、不属于 Approval Layer。

回答一个问题：

    "已批准的审批请求，是否允许进入真实执行？"

架构位置：
    Evidence Runtime → Capability Runtime → Execution Runtime
                                                 ↓
                                         Approval Layer
                                                 ↓
                                         Activation Boundary (本层)
                                                 ↓
                                         Controlled Execution Entry

设计约束：
    - 禁止执行真实动作
    - 禁止绕过审批层
    - 禁止自动批准
    - 四重门禁验证，全部通过才允许激活
"""

from dice.runtime.activation.models import (
    ActivationDecision,
    ActivationAuditRecord,
    ActivationBatchResult,
    ActivationStatus,
    ActivationBlockReason,
    ActivationRiskLevel,
)
from dice.runtime.activation.boundary import (
    ActivationBoundary,
)
from dice.runtime.activation.scope_manager import (
    ActivationScope,
    ActivationScopeManager,
)
from dice.runtime.activation.permission import (
    PermissionDecision,
    ExecutionPermissionChecker,
)

__all__ = [
    # Phase 3 Step 2
    "ActivationDecision",
    "ActivationAuditRecord",
    "ActivationBatchResult",
    "ActivationStatus",
    "ActivationBlockReason",
    "ActivationRiskLevel",
    "ActivationBoundary",
    # Phase 3 Step 4
    "ActivationScope",
    "ActivationScopeManager",
    "PermissionDecision",
    "ExecutionPermissionChecker",
]