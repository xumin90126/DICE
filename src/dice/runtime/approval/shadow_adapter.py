"""
Shadow Execution → Approval 集成适配器 — Phase 3 Step 1.

消费 ExecutionPlanShadowResult，生成 ApprovalRequest。

职责：
    1. 将 Execution Plan Shadow 结果转换为 ApprovalRequest
    2. 构建完整的证据追溯链
    3. 批量审批请求生成

禁止：
    ✖ 执行真实动作
    ✖ 调用生产 ExecutionRuntime
    ✖ 自动批准
    ✖ 修改任何 Runtime 层
"""

from __future__ import annotations

import json
from typing import Any, Optional

from dice.runtime.approval.models import (
    ApprovalRequest,
    ApprovalBatch,
    ApprovalRiskLevel,
)
from dice.runtime.approval.workflow import ApprovalWorkflowEngine


def _to_risk_level(value: str) -> ApprovalRiskLevel:
    risk_map = {
        "low": ApprovalRiskLevel.LOW,
        "medium": ApprovalRiskLevel.MEDIUM,
        "high": ApprovalRiskLevel.HIGH,
        "critical": ApprovalRiskLevel.CRITICAL,
    }
    return risk_map.get(value.lower(), ApprovalRiskLevel.LOW)


class ApprovalShadowAdapter:
    """审批影子适配器。

    将 Execution Plan Shadow 结果安全地转换为审批请求，
    不执行任何真实动作。

    使用方式：
        adapter = ApprovalShadowAdapter()
        requests = adapter.convert_batch(execution_plans)

        engine = ApprovalWorkflowEngine()
        for req in requests:
            engine.approve(req, reviewer="张三", comment="已审核通过")
    """

    def __init__(self) -> None:
        """初始化适配器。无需外部依赖。"""
        self._workflow_engine: Optional[ApprovalWorkflowEngine] = None

    @property
    def workflow_engine(self) -> ApprovalWorkflowEngine:
        """获取或创建关联的工作流引擎。"""
        if self._workflow_engine is None:
            self._workflow_engine = ApprovalWorkflowEngine()
        return self._workflow_engine

    def convert(
        self,
        execution_plan: dict[str, Any],
        evidence_trace: Optional[dict[str, Any]] = None,
    ) -> ApprovalRequest:
        """
        将单个 Execution Plan Shadow 结果转换为审批请求。

        参数:
            execution_plan: ExecutionPlanShadowResult.to_dict() 的输出
            evidence_trace: 可选的证据追溯信息

        返回:
            ApprovalRequest 审批请求
        """
        return self.workflow_engine.create_request(
            execution_plan=execution_plan,
            evidence_trace=evidence_trace,
        )

    def convert_batch(
        self,
        execution_plans: list[dict[str, Any]],
        evidence_traces: Optional[dict[str, dict[str, Any]]] = None,
    ) -> ApprovalBatch:
        """
        批量转换 Execution Plan Shadow 结果。

        参数:
            execution_plans: ExecutionPlanShadowResult 列表
            evidence_traces: 可选的文档级证据追溯映射

        返回:
            ApprovalBatch 批量审批结果
        """
        return self.workflow_engine.create_batch(
            execution_plans=execution_plans,
            evidence_traces=evidence_traces,
        )

    def get_approval_queue(self) -> list[dict[str, Any]]:
        """
        获取当前待审批队列（用于人工审核展示）。

        返回:
            list[dict] 每个待审批请求的摘要信息
        """
        pending = self.workflow_engine.get_pending_requests()
        return [
            {
                "request_id": req.request_id,
                "document_id": req.document_id,
                "capability": f"{req.capability_name} ({req.capability_id})",
                "execution_action": req.execution_plan.get("selected_action", ""),
                "confidence": req.execution_confidence,
                "risk_level": req.risk_level.value,
                "validation": req.validation_result,
                "created": req.created_time,
            }
            for req in pending
        ]

    def get_statistics(self) -> dict[str, Any]:
        """获取审批统计信息。"""
        return self.workflow_engine.get_statistics()


# ═══════════════════════════════════════════════════════════════════════════
# 独立的辅助函数（不依赖 WorkflowEngine）
# ═══════════════════════════════════════════════════════════════════════════


def load_execution_plan_results(path: str) -> list[dict[str, Any]]:
    """
    从 Phase 2 Step 5 的 execution_comparison_report.json 加载执行计划。

    注意：execution_comparison_report.json 的结构为：
    {
        "per_document": [
            {
                "document_id": "VSB102",
                "shadow": {"plans": [...]},
                "production": {...}
            },
            ...
        ]
    }

    返回展平的 ExecutionPlanShadowResult 列表。
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    plans: list[dict[str, Any]] = []
    for doc_data in data.get("per_document", []):
        doc_id = doc_data.get("document_id", "")
        shadow = doc_data.get("shadow", {})
        doc_plans = shadow.get("plans", [])

        for plan in doc_plans:
            plan["document_id"] = plan.get("document_id", doc_id)
            plans.append(plan)

    return plans


def load_execution_plan_batch(path: str) -> list[dict[str, Any]]:
    """
    从 execution_plan_distribution.json 加载所有执行计划。

    这是 execution_plan_distribution.json 的结构：
    [
        {
            "document_id": "...",
            "capability_id": "...",
            "selected_action": "...",
            ...
        },
        ...
    ]
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("plans", [])
    return []


__all__ = [
    "ApprovalShadowAdapter",
    "load_execution_plan_results",
    "load_execution_plan_batch",
]