"""
生产安全护栏运行时 — Phase 3 Step 3.

Production Guardrail Layer：激活边界之上的最终安全入口。

职责：
    1. 最终权限判断——只有 ALLOW 才能进入执行
    2. 安全策略检查——五重验证全部通过
    3. 执行前阻断——任何检查失败立即 BLOCK
    4. 审计记录生成——完整可追溯的决策链

架构约束：
    - 不属于 Evidence Runtime
    - 不属于 Capability Runtime
    - 不属于 Execution Runtime
    - 不属于 Approval Layer
    - 不属于 Activation Boundary
    - 是独立的生产安全入口层

禁止：
    - 调用真实 ExecutionRuntime
    - 修改 ExecutionRuntime
    - 修改 Capability Runtime
    - 修改 Approval Layer
    - 自动批准执行
"""

from dice.runtime.guardrail.models import (
    ProductionExecutionPermissionResult,
    GuardrailCheckResult,
    GuardrailAuditRecord,
    GuardrailBatchResult,
    PermissionStatus,
    GuardrailCheckType,
    GuardrailBlockReason,
)

from dice.runtime.guardrail.guardrail import (
    GuardrailCheckEngine,
)

__all__ = [
    # 数据模型
    "ProductionExecutionPermissionResult",
    "GuardrailCheckResult",
    "GuardrailAuditRecord",
    "GuardrailBatchResult",
    "PermissionStatus",
    "GuardrailCheckType",
    "GuardrailBlockReason",
    # 引擎
    "GuardrailCheckEngine",
]