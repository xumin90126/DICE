"""
生产执行权限检查器 — Phase 3 Step 4.

ExecutionPermissionChecker：控制哪些已批准的请求可以进入有限生产执行。

职责：
    1. 检查 Capability 是否在允许范围内
    2. 检查 Execution Action 是否允许
    3. 检查 Risk Level 是否符合限制
    4. 检查 Batch Size 是否超过限制
    5. 检查是否存在有效 Approval
    6. 检查是否存在 Guardrail PASS

设计约束：
    - 禁止自动批准——所有检查必须显式调用
    - 禁止自动扩大 scope——scope 由 ScopeManager 管理
    - 不属于任何 Runtime 层——是独立的权限检查层
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from dice.runtime.approval.models import ApprovalRequest, ApprovalStatus
from dice.runtime.activation.models import (
    ActivationDecision,
    ActivationStatus,
    ActivationRiskLevel,
)
from dice.runtime.guardrail.models import (
    ProductionExecutionPermissionResult,
    PermissionStatus,
)
from dice.runtime.activation.scope_manager import (
    ActivationScope,
    ActivationScopeManager,
)


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
# PermissionDecision — 权限决策
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class PermissionDecision:
    """权限决策——Production Execution Permission Checker 的输出。

    Fields:
        decision_id: 唯一决策 ID
        request_id: 关联的审批请求 ID
        allowed: 是否允许执行
        reason: 决策原因
        failed_checks: 失败的检查项列表
        passed_checks: 通过的检查项列表
        scope_id: 匹配的范围 ID（如果有）
        capability_id: 关联的能力 ID
        action: 执行动作
        risk_level: 当前风险等级
        audit_reference: 审计追溯引用
        created_time: 创建时间
        metadata: 扩展元数据
    """
    decision_id: str = ""
    request_id: str = ""
    allowed: bool = False
    reason: str = ""
    failed_checks: list[str] = field(default_factory=list)
    passed_checks: list[str] = field(default_factory=list)
    scope_id: str = ""
    capability_id: str = ""
    action: str = ""
    risk_level: str = ""
    audit_reference: str = ""
    created_time: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.decision_id:
            self.decision_id = _uid("PERM-")
        if not self.created_time:
            self.created_time = _now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "request_id": self.request_id,
            "allowed": self.allowed,
            "reason": self.reason,
            "failed_checks": self.failed_checks,
            "passed_checks": self.passed_checks,
            "scope_id": self.scope_id,
            "capability_id": self.capability_id,
            "action": self.action,
            "risk_level": self.risk_level,
            "audit_reference": self.audit_reference,
            "created_time": self.created_time,
            "metadata": self.metadata,
        }

    def to_summary(self) -> str:
        """生成权限决策的摘要描述。"""
        icon = "✅" if self.allowed else "❌"
        checks_info = (
            f"通过: {len(self.passed_checks)}, "
            f"失败: {len(self.failed_checks)}"
        )
        return (
            f"{icon} {'允许' if self.allowed else '阻止'} | "
            f"能力: {self.capability_id} | "
            f"动作: {self.action} | "
            f"风险: {self.risk_level} | "
            f"[{checks_info}] | "
            f"原因: {self.reason}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# ExecutionPermissionChecker
# ═══════════════════════════════════════════════════════════════════════════


class ExecutionPermissionChecker:
    """生产执行权限检查器。

    检查六项条件，全部通过才允许进入有限生产执行。

    六重检查：
        1. Capability 是否在允许范围
        2. Execution Action 是否允许
        3. Risk Level 是否符合限制
        4. Batch Size 是否超过限制
        5. 是否存在有效 Approval
        6. 是否存在 Guardrail PASS

    使用方式：
        checker = ExecutionPermissionChecker(scope_manager)

        decision = checker.check(
            activation_decision=decision,
            approval_request=request,
            guardrail_permission=permission,
            action="extract_components",
            batch_size=1,
        )

        if decision.allowed:
            # 可以进入有限生产执行
            pass
        else:
            # 被阻止——查看 failed_checks 了解原因
            print(decision.failed_checks)
    """

    def __init__(self, scope_manager: Optional[ActivationScopeManager] = None) -> None:
        """初始化权限检查器。

        参数:
            scope_manager: 激活范围管理器。如果未提供，将创建默认实例。
        """
        self._scope_manager = scope_manager or ActivationScopeManager()
        self._decisions: dict[str, PermissionDecision] = {}

    # ═══════════════════════════════════════════════════════════════════
    # 核心方法：检查权限
    # ═══════════════════════════════════════════════════════════════════

    def check(
        self,
        activation_decision: ActivationDecision,
        approval_request: ApprovalRequest,
        guardrail_permission: ProductionExecutionPermissionResult,
        action: str = "",
        batch_size: int = 1,
        document_type: str = "",
    ) -> PermissionDecision:
        """检查是否允许进入有限生产执行。

        参数:
            activation_decision: 激活决策（必须为 ALLOWED）
            approval_request: 审批请求（必须为 APPROVED）
            guardrail_permission: 护栏权限结果（必须为 ALLOW）
            action: 执行动作名称
            batch_size: 批次大小
            document_type: 文档类型

        返回:
            PermissionDecision 权限决策
        """
        capability_id = activation_decision.capability_id
        risk_level = activation_decision.risk_level

        decision = PermissionDecision(
            request_id=activation_decision.request_id,
            capability_id=capability_id,
            action=action,
            risk_level=risk_level.value,
        )

        passed_checks: list[str] = []
        failed_checks: list[str] = []

        # Check 1: Capability 是否在允许范围
        check1 = self._check_capability_in_scope(capability_id)
        if check1["passed"]:
            passed_checks.append(check1["name"])
            decision.scope_id = check1.get("scope_id", "")
        else:
            failed_checks.append(check1["name"])

        # Check 2: Execution Action 是否允许
        if action:
            check2 = self._check_action_allowed(action)
            if check2["passed"]:
                passed_checks.append(check2["name"])
            else:
                failed_checks.append(check2["name"])

        # Check 3: Risk Level 是否符合限制
        check3 = self._check_risk_level(risk_level)
        if check3["passed"]:
            passed_checks.append(check3["name"])
        else:
            failed_checks.append(check3["name"])

        # Check 4: Batch Size 是否超过限制
        check4 = self._check_batch_size(batch_size)
        if check4["passed"]:
            passed_checks.append(check4["name"])
        else:
            failed_checks.append(check4["name"])

        # Check 5: 是否存在有效 Approval
        check5 = self._check_approval_valid(approval_request)
        if check5["passed"]:
            passed_checks.append(check5["name"])
        else:
            failed_checks.append(check5["name"])

        # Check 6: 是否存在 Guardrail PASS
        check6 = self._check_guardrail_pass(guardrail_permission)
        if check6["passed"]:
            passed_checks.append(check6["name"])
        else:
            failed_checks.append(check6["name"])

        # 汇总结果
        decision.passed_checks = passed_checks
        decision.failed_checks = failed_checks
        decision.allowed = len(failed_checks) == 0

        if decision.allowed:
            decision.reason = (
                f"六重权限检查全部通过: "
                f"能力={capability_id}, 动作={action}, "
                f"风险={risk_level.value}, 批次={batch_size}"
            )
        else:
            decision.reason = (
                f"权限检查失败，失败项: {', '.join(failed_checks)}"
            )

        decision.audit_reference = (
            f"audit://permission/{decision.decision_id}"
            f"?request={decision.request_id}"
            f"&capability={capability_id}"
            f"&action={action}"
        )

        # 存储决策
        self._decisions[decision.decision_id] = decision

        return decision

    def check_batch(
        self,
        requests: list[dict[str, Any]],
    ) -> list[PermissionDecision]:
        """批量检查权限。

        参数:
            requests: 请求列表，每个请求包含:
                - activation_decision: ActivationDecision
                - approval_request: ApprovalRequest
                - guardrail_permission: ProductionExecutionPermissionResult
                - action: str
                - batch_size: int (可选，默认 1)
                - document_type: str (可选)

        返回:
            list[PermissionDecision] 权限决策列表
        """
        decisions: list[PermissionDecision] = []
        for req in requests:
            decision = self.check(
                activation_decision=req["activation_decision"],
                approval_request=req["approval_request"],
                guardrail_permission=req["guardrail_permission"],
                action=req.get("action", ""),
                batch_size=req.get("batch_size", 1),
                document_type=req.get("document_type", ""),
            )
            decisions.append(decision)
        return decisions

    # ═══════════════════════════════════════════════════════════════════
    # Check 1: Capability 是否在允许范围
    # ═══════════════════════════════════════════════════════════════════

    def _check_capability_in_scope(
        self, capability_id: str
    ) -> dict[str, Any]:
        """检查能力是否在允许范围内。"""
        if not capability_id:
            return {
                "name": "capability_in_scope",
                "passed": False,
                "detail": "capability_id 为空",
                "scope_id": "",
            }

        if self._scope_manager.is_capability_allowed(capability_id):
            scopes = self._scope_manager.get_scopes_for_capability(capability_id)
            scope_id = scopes[0].scope_id if scopes else ""
            return {
                "name": "capability_in_scope",
                "passed": True,
                "detail": f"能力 {capability_id} 在允许范围内",
                "scope_id": scope_id,
            }

        return {
            "name": "capability_in_scope",
            "passed": False,
            "detail": f"能力 {capability_id} 不在任何已启用范围内",
            "scope_id": "",
        }

    # ═══════════════════════════════════════════════════════════════════
    # Check 2: Execution Action 是否允许
    # ═══════════════════════════════════════════════════════════════════

    def _check_action_allowed(self, action: str) -> dict[str, Any]:
        """检查执行动作是否允许。"""
        if not action:
            return {
                "name": "action_allowed",
                "passed": False,
                "detail": "执行动作为空",
            }

        if self._scope_manager.is_action_allowed(action):
            return {
                "name": "action_allowed",
                "passed": True,
                "detail": f"动作 {action} 在允许范围内",
            }

        return {
            "name": "action_allowed",
            "passed": False,
            "detail": f"动作 {action} 不在任何已启用范围内",
        }

    # ═══════════════════════════════════════════════════════════════════
    # Check 3: Risk Level 是否符合限制
    # ═══════════════════════════════════════════════════════════════════

    def _check_risk_level(
        self, risk_level: ActivationRiskLevel
    ) -> dict[str, Any]:
        """检查风险等级是否在允许范围内。"""
        # 检查所有已启用范围是否允许此风险等级
        enabled_scopes = self._scope_manager.get_enabled_scopes()
        if not enabled_scopes:
            return {
                "name": "risk_level_check",
                "passed": False,
                "detail": "没有已启用的范围——无法检查风险等级",
            }

        for scope in enabled_scopes:
            if scope.allows_risk_level(risk_level):
                return {
                    "name": "risk_level_check",
                    "passed": True,
                    "detail": (
                        f"风险等级 {risk_level.value} 在范围内 "
                        f"（限制: {scope.risk_level_limit.value}）"
                    ),
                }

        return {
            "name": "risk_level_check",
            "passed": False,
            "detail": (
                f"风险等级 {risk_level.value} 超过所有已启用范围的限制"
            ),
        }

    # ═══════════════════════════════════════════════════════════════════
    # Check 4: Batch Size 是否超过限制
    # ═══════════════════════════════════════════════════════════════════

    def _check_batch_size(self, batch_size: int) -> dict[str, Any]:
        """检查批次大小是否超过限制。"""
        enabled_scopes = self._scope_manager.get_enabled_scopes()
        if not enabled_scopes:
            return {
                "name": "batch_size_check",
                "passed": False,
                "detail": "没有已启用的范围——无法检查批次大小",
            }

        for scope in enabled_scopes:
            if scope.allows_batch_size(batch_size):
                return {
                    "name": "batch_size_check",
                    "passed": True,
                    "detail": (
                        f"批次大小 {batch_size} 在范围内 "
                        f"（限制: {scope.max_batch_size}）"
                    ),
                }

        return {
            "name": "batch_size_check",
            "passed": False,
            "detail": (
                f"批次大小 {batch_size} 超过所有已启用范围的限制"
            ),
        }

    # ═══════════════════════════════════════════════════════════════════
    # Check 5: 是否存在有效 Approval
    # ═══════════════════════════════════════════════════════════════════

    def _check_approval_valid(
        self, approval_request: ApprovalRequest
    ) -> dict[str, Any]:
        """检查是否存在有效审批。"""
        if approval_request.status != ApprovalStatus.APPROVED:
            return {
                "name": "approval_valid",
                "passed": False,
                "detail": (
                    f"审批状态: {approval_request.status.value} "
                    f"（期望: APPROVED）"
                ),
            }

        if not approval_request.reviewer:
            return {
                "name": "approval_valid",
                "passed": False,
                "detail": "审批人信息缺失",
            }

        return {
            "name": "approval_valid",
            "passed": True,
            "detail": (
                f"审批有效: 审批人={approval_request.reviewer}, "
                f"状态={approval_request.status.value}"
            ),
        }

    # ═══════════════════════════════════════════════════════════════════
    # Check 6: 是否存在 Guardrail PASS
    # ═══════════════════════════════════════════════════════════════════

    def _check_guardrail_pass(
        self, guardrail_permission: ProductionExecutionPermissionResult
    ) -> dict[str, Any]:
        """检查护栏是否通过。"""
        if guardrail_permission.permission_status != PermissionStatus.ALLOW:
            return {
                "name": "guardrail_pass",
                "passed": False,
                "detail": (
                    f"护栏状态: {guardrail_permission.permission_status.value} "
                    f"（期望: ALLOW）"
                ),
            }

        passed = guardrail_permission.check_count()["passed"]
        total = guardrail_permission.check_count()["total"]
        if passed < total:
            return {
                "name": "guardrail_pass",
                "passed": False,
                "detail": f"护栏检查未全部通过: {passed}/{total}",
            }

        return {
            "name": "guardrail_pass",
            "passed": True,
            "detail": f"护栏全部通过: {passed}/{total}",
        }

    # ═══════════════════════════════════════════════════════════════════
    # 查询方法
    # ═══════════════════════════════════════════════════════════════════

    def get_decision(self, decision_id: str) -> Optional[PermissionDecision]:
        """获取权限决策。"""
        return self._decisions.get(decision_id)

    def get_allowed_decisions(self) -> list[PermissionDecision]:
        """获取所有允许的决策。"""
        return [d for d in self._decisions.values() if d.allowed]

    def get_blocked_decisions(self) -> list[PermissionDecision]:
        """获取所有被阻止的决策。"""
        return [d for d in self._decisions.values() if not d.allowed]

    def get_statistics(self) -> dict[str, Any]:
        """获取权限检查统计信息。"""
        total = len(self._decisions)
        if total == 0:
            return {"total": 0}

        allowed = sum(1 for d in self._decisions.values() if d.allowed)
        blocked = total - allowed

        fail_counts: dict[str, int] = {}
        for d in self._decisions.values():
            for check in d.failed_checks:
                fail_counts[check] = fail_counts.get(check, 0) + 1

        return {
            "total_checks": total,
            "allowed": allowed,
            "blocked": blocked,
            "allow_rate": round(allowed / total, 4) if total > 0 else 0.0,
            "failure_distribution": fail_counts,
            "scope_statistics": self._scope_manager.get_statistics(),
        }


__all__ = [
    "PermissionDecision",
    "ExecutionPermissionChecker",
]