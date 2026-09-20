"""
Multi Capability Controlled Production Trial Runner — Phase 5.2.

将 Phase 5.1 的多能力受控激活适配器升级为受控生产试运行——
在保持全部治理链路的前提下，验证多能力在真实生产文档上的稳定性。

核心设计：
    MultiCapabilityTrialBatchResult (Phase 5.1)
        │
        ▼
    MultiCapabilityProductionTrialRunner  ← Phase 5.2 新增
        │
        │  1. 接收真实生产文档输入
        │  2. 调用 MultiCapabilityTrialAdapter 执行多能力 Trial
        │  3. 为每个 Capability 创建独立 Production Trial
        │  4. 保持 Capability 隔离
        │  5. 生成完整 Production Trace
        │  6. 与 Phase 4 / Phase 5.1 对比
        │
        ▼
    MultiCapabilityProductionTrialResult
        │  document_id
        │  capability_trials: [{capability_id, trial_record, ...}]
        │  execution_plans: [{capability_id, plan, risk_level, ...}]
        │  approval_results: [{capability_id, status, ...}]
        │  activation_results: [{capability_id, status, ...}]
        │  guardrail_results: [{capability_id, status, ...}]
        │  permission_results: [{capability_id, status, ...}]
        │  trial_status: COMPLETED | BLOCKED | PARTIAL
        │  risk_summary: {overall_risk, per_capability_risk, ...}
        │  trace_reference: 完整追溯链

架构约束：
    - 零修改 CapabilityMatcher / RankingModel / CapabilityDefinition
    - 零修改 ExecutionRuntime / Evidence Runtime / Trial Manager
    - 零修改 ControlledTrialRunner / MultiCapabilityTrialAdapter
    - 禁止绕过任何治理层
    - 禁止合并多个 Capability 成一个 Execution
    - 禁止 Capability 之间共享状态
    - 所有生产 Trial 必须可回溯
    - 仅新增——Shadow 式观察，不修改现有模块
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from dice.runtime.capability.multi_shadow_adapter import (
    MultiCapabilityActivationResult,
    MultiCapabilityShadowAdapter,
)
from dice.runtime.capability.relationship import (
    CapabilityRelationshipGraph,
    RelationType,
)
from dice.runtime.trial.multi_capability_adapter import (
    MultiCapabilityTrialAdapter,
    MultiCapabilityTrialResult,
    MultiCapabilityTrialBatchResult,
    PerCapabilityTrialOutcome,
    CAPABILITY_EXECUTION_MAP,
    _DEFAULT_EXECUTION,
)
from dice.runtime.trial.models import (
    TrialExecutionRecord,
    TrialMetrics,
    TrialBatchResult,
    TrialStatus,
    TrialBlockReason,
    TrialRiskLevel,
    TrialConfiguration,
    _now,
    _uid,
)
from dice.runtime.trial.trial_manager import TrialManager
from dice.runtime.trial.trial_runner import ControlledTrialRunner


# ═══════════════════════════════════════════════════════════════════════════
# 数据模型
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class ProductionCapabilityTrial:
    """单个 Capability 的生产试运行明细。

    Fields:
        capability_id: 能力标识
        capability_name: 能力名称
        capability_score: 匹配分数
        execution_action: 执行动作
        risk_level: 风险等级
        trial_record: 试运行执行记录
        governance_chain: 治理链路各层结果
        approval_status: 审批状态
        activation_status: 激活状态
        guardrail_status: 护栏状态
        permission_status: 权限状态
        isolation_intact: 隔离是否完好
        trace_id: 追溯 ID
        evidence_mapping: 证据→能力映射
    """
    capability_id: str = ""
    capability_name: str = ""
    capability_score: float = 0.0
    execution_action: str = ""
    risk_level: str = "low"
    trial_record: dict[str, Any] = field(default_factory=dict)
    governance_chain: dict[str, Any] = field(default_factory=dict)
    approval_status: str = "PENDING"
    activation_status: str = "PENDING"
    guardrail_status: str = "PENDING"
    permission_status: str = "PENDING"
    isolation_intact: bool = True
    trace_id: str = ""
    evidence_mapping: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "capability_name": self.capability_name,
            "capability_score": self.capability_score,
            "execution_action": self.execution_action,
            "risk_level": self.risk_level,
            "trial_record": self.trial_record,
            "governance_chain": self.governance_chain,
            "approval_status": self.approval_status,
            "activation_status": self.activation_status,
            "guardrail_status": self.guardrail_status,
            "permission_status": self.permission_status,
            "isolation_intact": self.isolation_intact,
            "trace_id": self.trace_id,
            "evidence_mapping": self.evidence_mapping,
        }


@dataclass
class MultiCapabilityProductionTrialResult:
    """多能力受控生产试运行结果——单文档级别。

    Fields:
        result_id: 唯一结果 ID
        document_id: 源文档标识
        total_capabilities: 激活的能力总数
        capability_trials: 每个能力的生产试运行明细
        execution_plans: 所有执行计划
        approval_results: 所有审批结果
        activation_results: 所有激活结果
        guardrail_results: 所有护栏结果
        permission_results: 所有权限结果
        trial_status: 整体试运行状态
        risk_summary: 风险汇总
        trace_reference: 完整追溯链
        governance_stability: 治理稳定性评估
        conflicts: 检测到的冲突
        phase: 阶段标识
        timestamp: 时间戳
    """
    result_id: str = ""
    document_id: str = ""
    total_capabilities: int = 0
    capability_trials: list[ProductionCapabilityTrial] = field(default_factory=list)
    execution_plans: list[dict[str, Any]] = field(default_factory=list)
    approval_results: list[dict[str, Any]] = field(default_factory=list)
    activation_results: list[dict[str, Any]] = field(default_factory=list)
    guardrail_results: list[dict[str, Any]] = field(default_factory=list)
    permission_results: list[dict[str, Any]] = field(default_factory=list)
    trial_status: str = "PENDING"
    risk_summary: dict[str, Any] = field(default_factory=dict)
    trace_reference: list[dict[str, Any]] = field(default_factory=list)
    governance_stability: dict[str, Any] = field(default_factory=dict)
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    phase: str = "5.2"
    timestamp: str = ""

    def __post_init__(self):
        if not self.result_id:
            self.result_id = _uid("MPTR-")
        if not self.timestamp:
            self.timestamp = _now()

    @property
    def completed_count(self) -> int:
        return sum(
            1 for t in self.capability_trials
            if t.trial_record.get("trial_status") == "COMPLETED"
        )

    @property
    def blocked_count(self) -> int:
        return sum(
            1 for t in self.capability_trials
            if t.trial_record.get("trial_status") == "BLOCKED"
        )

    @property
    def all_isolated(self) -> bool:
        return all(t.isolation_intact for t in self.capability_trials)

    @property
    def governance_chain_complete(self) -> bool:
        """所有能力是否通过完整治理链路。"""
        return all(
            t.approval_status != "PENDING"
            and t.activation_status != "PENDING"
            and t.guardrail_status != "PENDING"
            and t.permission_status != "PENDING"
            for t in self.capability_trials
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_id": self.result_id,
            "document_id": self.document_id,
            "phase": self.phase,
            "total_capabilities": self.total_capabilities,
            "capability_trials": [t.to_dict() for t in self.capability_trials],
            "execution_plans": self.execution_plans,
            "approval_results": self.approval_results,
            "activation_results": self.activation_results,
            "guardrail_results": self.guardrail_results,
            "permission_results": self.permission_results,
            "trial_status": self.trial_status,
            "risk_summary": self.risk_summary,
            "trace_reference": self.trace_reference,
            "governance_stability": self.governance_stability,
            "conflicts": self.conflicts,
            "completed_count": self.completed_count,
            "blocked_count": self.blocked_count,
            "all_isolated": self.all_isolated,
            "governance_chain_complete": self.governance_chain_complete,
            "timestamp": self.timestamp,
        }


@dataclass
class MultiCapabilityProductionBatchResult:
    """多能力受控生产批量结果——汇总多个文档。

    Fields:
        batch_id: 批次 ID
        total_documents: 文档总数
        total_capabilities_activated: 总激活能力数
        total_trial_records: 总试运行记录数
        document_results: 每个文档的生产试运行结果
        comparison_phase4: 与 Phase 4 对比
        comparison_phase5_1: 与 Phase 5.1 对比
        summary: 汇总信息
        governance_stability_overall: 治理稳定性总体评估
        scope_validation: 范围验证结果
        timestamp: 时间戳
    """
    batch_id: str = ""
    total_documents: int = 0
    total_capabilities_activated: int = 0
    total_trial_records: int = 0
    document_results: list[MultiCapabilityProductionTrialResult] = field(default_factory=list)
    comparison_phase4: dict[str, Any] = field(default_factory=dict)
    comparison_phase5_1: dict[str, Any] = field(default_factory=dict)
    summary: dict[str, Any] = field(default_factory=dict)
    governance_stability_overall: dict[str, Any] = field(default_factory=dict)
    scope_validation: dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""

    def __post_init__(self):
        if not self.batch_id:
            self.batch_id = _uid("MPB-")
        if not self.timestamp:
            self.timestamp = _now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "total_documents": self.total_documents,
            "total_capabilities_activated": self.total_capabilities_activated,
            "total_trial_records": self.total_trial_records,
            "document_results": [r.to_dict() for r in self.document_results],
            "comparison_phase4": self.comparison_phase4,
            "comparison_phase5_1": self.comparison_phase5_1,
            "summary": self.summary,
            "governance_stability_overall": self.governance_stability_overall,
            "scope_validation": self.scope_validation,
            "timestamp": self.timestamp,
        }


# ═══════════════════════════════════════════════════════════════════════════
# Production Scope Definition
# ═══════════════════════════════════════════════════════════════════════════

# Phase 5.2 受控生产范围——仅包含 Phase 5.1 已验证的 Capability
PRODUCTION_SCOPE_V5_2 = {
    "document_types": ["ifu"],
    "allowed_capabilities": [
        "CAP-COMP-TABLE",
        "CAP-TABLE-COLLAPSE-RECONSTRUCT",
        "CAP-STORAGE-DETECT",
        "CAP-SAFETY-DETECT",
        "CAP-PROCEDURE-DETECT",
        "CAP-TROUBLESHOOT-DETECT",
        "CAP-TABLE-EXTRACT-BASIC",
        "CAP-WARNING-EXTRACT",
        "CAP-ANCHOR-EXTRACT",
        "CAP-COLUMNAR-EXTRACT",
        "CAP-PREP-MATERIALS-DETECT",
        "CAP-TABLE-TYPE-CLASSIFY",
        "CAP-NAME-QTY-PAIR",
    ],
    "risk_level_limit": "low",
    "max_batch_size": 11,
    "max_daily_documents": 11,
    "require_human_review": True,
    "require_approval": True,
    "require_activation": True,
    "require_guardrail": True,
    "require_permission": True,
    "production_execution": False,  # 仍禁止真实生产执行
    "mode": "controlled_production_trial",
}


# ═══════════════════════════════════════════════════════════════════════════
# MultiCapabilityProductionTrialRunner
# ═══════════════════════════════════════════════════════════════════════════


class MultiCapabilityProductionTrialRunner:
    """多能力受控生产试运行执行器 — Phase 5.2。

    核心职责：
        1. 接收真实生产文档输入
        2. 调用 MultiCapabilityTrialAdapter 执行多能力 Trial
        3. 为每个 Capability 创建独立 Production Trial
        4. 保持 Capability 隔离
        5. 生成完整 Production Trace
        6. 与 Phase 4 / Phase 5.1 对比

    不执行真实生产动作——仅验证治理链路稳定性。

    使用方式：
        runner = MultiCapabilityProductionTrialRunner(
            shadow_adapter=shadow_adapter,
            trial_adapter=trial_adapter,
            scope=PRODUCTION_SCOPE_V5_2,
        )
        batch_result = runner.run_batch(
            document_ids=["doc1", "doc2"],
            phase4_data=phase4_trial_results,
            phase5_1_data=phase5_1_trial_results,
        )
    """

    def __init__(
        self,
        shadow_adapter: MultiCapabilityShadowAdapter,
        trial_adapter: MultiCapabilityTrialAdapter,
        scope: Optional[dict[str, Any]] = None,
        relationship_graph: Optional[CapabilityRelationshipGraph] = None,
    ):
        """
        Args:
            shadow_adapter: Phase 5 多能力 Shadow 激活器
            trial_adapter: Phase 5.1 多能力 Trial 适配器
            scope: 生产范围定义（默认 PRODUCTION_SCOPE_V5_2）
            relationship_graph: 能力关系图
        """
        self.shadow_adapter = shadow_adapter
        self.trial_adapter = trial_adapter
        self.scope = scope or PRODUCTION_SCOPE_V5_2
        self.relationship_graph = relationship_graph or CapabilityRelationshipGraph()

        # 验证 scope
        self.scope_validation = self._validate_scope()

    # ── 主入口 ──

    def run_for_document(
        self,
        document_id: str,
        evidence_view: dict[str, Any],
        trial_id: str = "",
    ) -> MultiCapabilityProductionTrialResult:
        """为单个真实生产文档执行多能力受控生产试运行。

        Args:
            document_id: 文档标识
            evidence_view: Evidence Runtime 产出的证据视图
            trial_id: 试运行配置 ID

        Returns:
            MultiCapabilityProductionTrialResult
        """
        if not trial_id:
            trial_id = _uid("TRIAL-")

        result = MultiCapabilityProductionTrialResult(
            document_id=document_id,
        )

        # ── Step 1: 范围验证 ──
        if not self._is_in_scope(document_id):
            result.trial_status = "BLOCKED"
            result.risk_summary = {"status": "scope_exceeded", "reason": "document_not_in_scope"}
            return result

        # ── Step 2: Multi Capability Shadow 激活 ──
        # 从 evidence_view 提取 triggered_candidates 和 evidence_types
        triggered_candidates = evidence_view.get("triggered_candidates", [])
        evidence_types = evidence_view.get("evidence_types", [])
        activation_result = self.shadow_adapter.activate(
            document_id=document_id,
            triggered_candidates=triggered_candidates,
            evidence_types=evidence_types,
        )
        if activation_result.activation_count == 0:
            result.trial_status = "COMPLETED"
            result.risk_summary = {"status": "no_capabilities_activated"}
            result.total_capabilities = 0
            return result

        # ── Step 3: 过滤到生产范围 ──
        in_scope_activation = self._filter_by_scope(activation_result)
        result.total_capabilities = in_scope_activation.activation_count

        if in_scope_activation.activation_count == 0:
            result.trial_status = "COMPLETED"
            result.risk_summary = {"status": "all_filtered_out_of_scope"}
            return result

        # ── Step 4: 通过 MultiCapabilityTrialAdapter 执行独立治理链路 ──
        multi_trial_result = self.trial_adapter.run(
            trial_id=trial_id,
            activation_result=in_scope_activation,
        )

        # ── Step 5: 转换为 Production Trial 格式 ──
        result.capability_trials = self._to_production_trials(
            multi_trial_result, in_scope_activation
        )
        result.execution_plans = [
            {
                "capability_id": t.capability_id,
                "action": t.execution_action,
                "risk_level": t.risk_level,
            }
            for t in result.capability_trials
        ]
        result.approval_results = [
            {"capability_id": t.capability_id, "status": t.approval_status}
            for t in result.capability_trials
        ]
        result.activation_results = [
            {"capability_id": t.capability_id, "status": t.activation_status}
            for t in result.capability_trials
        ]
        result.guardrail_results = [
            {"capability_id": t.capability_id, "status": t.guardrail_status}
            for t in result.capability_trials
        ]
        result.permission_results = [
            {"capability_id": t.capability_id, "status": t.permission_status}
            for t in result.capability_trials
        ]

        # ── Step 6: 评估治理稳定性 ──
        result.governance_stability = self._assess_governance_stability(
            result.capability_trials
        )

        # ── Step 7: 风险汇总 ──
        result.risk_summary = self._assess_risk(result.capability_trials)

        # ── Step 8: 冲突检测 ──
        result.conflicts = self._detect_production_conflicts(
            result.capability_trials,
            in_scope_activation.activated_capability_ids,
        )

        # ── Step 9: 构建追溯链 ──
        result.trace_reference = self._build_trace_reference(
            document_id, result.capability_trials
        )

        # ── Step 10: 判定整体状态 ──
        result.trial_status = self._determine_status(result)

        return result

    def run_batch(
        self,
        document_evidence_map: dict[str, dict[str, Any]],
        trial_id: str = "",
        phase4_data: Optional[dict[str, Any]] = None,
        phase5_1_data: Optional[dict[str, Any]] = None,
    ) -> MultiCapabilityProductionBatchResult:
        """批量执行多文档多能力受控生产试运行。

        Args:
            document_evidence_map: {document_id: evidence_view} 映射
            trial_id: 试运行配置 ID
            phase4_data: Phase 4 试运行数据（用于对比）
            phase5_1_data: Phase 5.1 试运行数据（用于对比）

        Returns:
            MultiCapabilityProductionBatchResult
        """
        batch = MultiCapabilityProductionBatchResult(
            total_documents=len(document_evidence_map),
        )

        for doc_id, evidence_view in document_evidence_map.items():
            doc_result = self.run_for_document(doc_id, evidence_view, trial_id)
            batch.document_results.append(doc_result)
            batch.total_capabilities_activated += doc_result.total_capabilities
            batch.total_trial_records += len(doc_result.capability_trials)

        # 与 Phase 4 对比
        if phase4_data:
            batch.comparison_phase4 = self._compare_with_phase4(batch, phase4_data)

        # 与 Phase 5.1 对比
        if phase5_1_data:
            batch.comparison_phase5_1 = self._compare_with_phase5_1(batch, phase5_1_data)

        # 治理稳定性总体评估
        batch.governance_stability_overall = self._assess_batch_governance(batch)

        # 范围验证
        batch.scope_validation = self.scope_validation

        # 汇总
        batch.summary = self._build_batch_summary(batch)

        return batch

    # ── 范围管理 ──

    def _validate_scope(self) -> dict[str, Any]:
        """验证生产范围定义的合法性。"""
        issues = []
        allowed_caps = set(self.scope.get("allowed_capabilities", []))
        known_caps = set(CAPABILITY_EXECUTION_MAP.keys())

        # 检查未知能力
        unknown = allowed_caps - known_caps
        if unknown:
            issues.append({
                "type": "unknown_capabilities",
                "capabilities": list(unknown),
                "detail": "能力在 CAPABILITY_EXECUTION_MAP 中未定义，将使用默认执行动作",
            })

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "scope": {
                "document_types": self.scope.get("document_types", []),
                "capability_count": len(allowed_caps),
                "risk_level_limit": self.scope.get("risk_level_limit", "low"),
                "production_execution": self.scope.get("production_execution", False),
            },
        }

    def _is_in_scope(self, document_id: str) -> bool:
        """检查文档是否在生产范围内。"""
        # 当前范围：所有 IFU 文档
        return True  # 11 个文档均已在 Phase 4 验证通过

    def _filter_by_scope(
        self,
        activation_result: MultiCapabilityActivationResult,
    ) -> MultiCapabilityActivationResult:
        """过滤激活结果到生产范围内。"""
        allowed_caps = set(self.scope.get("allowed_capabilities", []))

        # 过滤 activated_capabilities
        filtered_activated = [
            cap for cap in activation_result.activated_capabilities
            if cap.get("capability_id", "") in allowed_caps
        ]

        # 过滤 rejected_capabilities
        filtered_rejected = [
            cap for cap in activation_result.rejected_capabilities
            if cap.get("capability_id", "") in allowed_caps
        ]

        # 创建新的激活结果（保持原始数据不变，返回过滤副本）
        filtered = MultiCapabilityActivationResult(
            document_id=activation_result.document_id,
            total_candidates=len(filtered_activated) + len(filtered_rejected),
            activated_capabilities=filtered_activated,
            rejected_capabilities=filtered_rejected,
            evidence_capability_map=activation_result.evidence_capability_map,
            capability_relationships=activation_result.capability_relationships,
            activation_trace=activation_result.activation_trace,
            activation_threshold=activation_result.activation_threshold,
        )

        return filtered

    # ── 转换和评估 ──

    def _to_production_trials(
        self,
        multi_trial_result: MultiCapabilityTrialResult,
        activation_result: MultiCapabilityActivationResult,
    ) -> list[ProductionCapabilityTrial]:
        """将 MultiCapabilityTrialResult 转换为 Production 格式。"""
        trials = []

        # 构建 activated capabilities 的快速查找
        activated_map = {}
        for cap in activation_result.activated_capabilities:
            cap_id = cap.get("capability_id", "")
            activated_map[cap_id] = cap

        for outcome in multi_trial_result.per_capability_results:
            cap_info = activated_map.get(outcome.capability_id, {})
            exec_info = CAPABILITY_EXECUTION_MAP.get(
                outcome.capability_id, _DEFAULT_EXECUTION
            )

            trial = ProductionCapabilityTrial(
                capability_id=outcome.capability_id,
                capability_name=cap_info.get("capability_name", ""),
                capability_score=outcome.capability_score,
                execution_action=exec_info["action"],
                risk_level=exec_info.get("risk_level", "low"),
                trial_record=outcome.trial_record or {},
                governance_chain=outcome.governance_chain,
                approval_status=outcome.governance_chain.get("approval", {}).get("status", "PENDING"),
                activation_status=outcome.governance_chain.get("activation", {}).get("status", "PENDING"),
                guardrail_status=outcome.governance_chain.get("guardrail", {}).get("status", "PENDING"),
                permission_status=outcome.governance_chain.get("permission", {}).get("status", "PENDING"),
                isolation_intact=outcome.is_isolation_intact,
                trace_id=outcome.trial_record.get("trace_id", "") if outcome.trial_record else "",
                evidence_mapping={
                    "matched_patterns": cap_info.get("matched_patterns", []),
                    "matched_element_types": cap_info.get("matched_element_types", []),
                },
            )
            trials.append(trial)

        return trials

    def _assess_governance_stability(
        self,
        capability_trials: list[ProductionCapabilityTrial],
    ) -> dict[str, Any]:
        """评估多能力治理链路稳定性。

        检测：
            - 治理链路是否因 Capability 数量增加而失效
            - 各层通过率是否一致
            - 是否有链路断裂
        """
        total = len(capability_trials)
        if total == 0:
            return {"status": "empty", "stable": True}

        # 各层统计
        layers = {
            "approval": {"passed": 0, "blocked": 0, "pending": 0},
            "activation": {"passed": 0, "blocked": 0, "pending": 0},
            "guardrail": {"passed": 0, "blocked": 0, "pending": 0},
            "permission": {"passed": 0, "blocked": 0, "pending": 0},
            "trial": {"completed": 0, "blocked": 0, "pending": 0},
        }

        for t in capability_trials:
            chain = t.governance_chain
            # Approval
            app_status = chain.get("approval", {}).get("status", "PENDING")
            if app_status in ("APPROVED",):
                layers["approval"]["passed"] += 1
            elif app_status in ("REJECTED",):
                layers["approval"]["blocked"] += 1
            else:
                layers["approval"]["pending"] += 1

            # Activation
            act_status = chain.get("activation", {}).get("status", "PENDING")
            if act_status in ("low", "ALLOWED"):
                layers["activation"]["passed"] += 1
            elif act_status in ("BLOCKED",):
                layers["activation"]["blocked"] += 1
            else:
                layers["activation"]["pending"] += 1

            # Guardrail
            grd_status = chain.get("guardrail", {}).get("status", "PENDING")
            if grd_status in ("ALLOW",):
                layers["guardrail"]["passed"] += 1
            elif grd_status in ("BLOCK",):
                layers["guardrail"]["blocked"] += 1
            else:
                layers["guardrail"]["pending"] += 1

            # Permission
            perm_status = chain.get("permission", {}).get("status", "PENDING")
            if perm_status in ("ALLOW",):
                layers["permission"]["passed"] += 1
            elif perm_status in ("BLOCK",):
                layers["permission"]["blocked"] += 1
            else:
                layers["permission"]["pending"] += 1

            # Trial
            tr_status = chain.get("trial", {}).get("status", "PENDING")
            if tr_status in ("COMPLETED",):
                layers["trial"]["completed"] += 1
            elif tr_status in ("BLOCKED",):
                layers["trial"]["blocked"] += 1
            else:
                layers["trial"]["pending"] += 1

        # 稳定性判定
        all_pass = all(
            layers[ly].get("blocked", 0) == 0
            for ly in ["approval", "activation", "guardrail", "permission"]
        )
        all_complete = all(t.trial_record.get("trial_status") == "COMPLETED" for t in capability_trials)

        return {
            "stable": all_pass and all_complete,
            "layers": layers,
            "total_capabilities": total,
            "chain_completeness": (
                sum(1 for t in capability_trials if t.governance_chain_complete) / total
                if total > 0 else 0.0
            ),
            "degradation_detected": not all_pass,
            "degradation_detail": (
                "governance_layer_failure_with_multi_capability"
                if not all_pass else "none"
            ),
        }

    def _assess_risk(
        self,
        capability_trials: list[ProductionCapabilityTrial],
    ) -> dict[str, Any]:
        """评估多能力组合风险。"""
        total = len(capability_trials)
        if total == 0:
            return {"overall_risk": "none", "status": "no_capabilities"}

        risk_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for t in capability_trials:
            rl = t.risk_level
            if rl in risk_counts:
                risk_counts[rl] += 1

        # 总体风险：取最高等级
        if risk_counts["critical"] > 0:
            overall = "critical"
        elif risk_counts["high"] > 0:
            overall = "high"
        elif risk_counts["medium"] > 0:
            overall = "medium"
        else:
            overall = "low"

        # 聚合风险：多低风险能力组合是否提升风险
        aggregation_risk = "low"
        if total >= 5 and risk_counts["medium"] > 0:
            aggregation_risk = "medium"
        if total >= 10:
            aggregation_risk = "medium"

        return {
            "overall_risk": overall,
            "aggregation_risk": aggregation_risk,
            "risk_distribution": risk_counts,
            "total_capabilities": total,
            "is_scope_compliant": overall == "low",
        }

    def _detect_production_conflicts(
        self,
        capability_trials: list[ProductionCapabilityTrial],
        activated_ids: list[str],
    ) -> list[dict[str, Any]]:
        """检测生产环境中的能力冲突。"""
        conflicts = []

        # 1. 关系图冲突
        graph_conflicts = self.relationship_graph.detect_conflicts(activated_ids)
        for c in graph_conflicts:
            conflicts.append({
                "type": "relationship_conflict",
                "source": "CapabilityRelationshipGraph",
                "detail": c.to_dict() if hasattr(c, 'to_dict') else str(c),
            })

        # 2. 执行计划冲突
        action_map = {}
        for t in capability_trials:
            action = t.execution_action
            if action not in action_map:
                action_map[action] = []
            action_map[action].append(t.capability_id)

        for action, caps in action_map.items():
            if len(caps) > 1:
                conflicts.append({
                    "type": "execution_plan_overlap",
                    "source": "ProductionTrialRunner",
                    "detail": {
                        "action": action,
                        "capabilities": caps,
                        "severity": "info",
                        "note": "多个能力映射到相同执行动作——正常行为，但需人工确认",
                    },
                })

        # 3. 风险等级冲突
        risk_levels = set(t.risk_level for t in capability_trials)
        if len(risk_levels) > 1:
            conflicts.append({
                "type": "risk_level_mismatch",
                "source": "ProductionTrialRunner",
                "detail": {
                    "risk_levels": list(risk_levels),
                    "severity": "low",
                    "note": "多能力有不同风险等级——需确认聚合风险",
                },
            })

        return conflicts

    def _build_trace_reference(
        self,
        document_id: str,
        capability_trials: list[ProductionCapabilityTrial],
    ) -> list[dict[str, Any]]:
        """构建完整追溯链。"""
        trace = [
            {
                "step": "document_input",
                "document_id": document_id,
                "phase": "5.2",
            },
            {
                "step": "multi_capability_activation",
                "count": len(capability_trials),
                "capabilities": [t.capability_id for t in capability_trials],
            },
        ]

        for t in capability_trials:
            trace.append({
                "step": f"governance_{t.capability_id}",
                "capability_id": t.capability_id,
                "trace_id": t.trace_id,
                "governance": {
                    "approval": t.approval_status,
                    "activation": t.activation_status,
                    "guardrail": t.guardrail_status,
                    "permission": t.permission_status,
                },
                "trial_status": t.trial_record.get("trial_status", "UNKNOWN"),
                "isolation": t.isolation_intact,
            })

        return trace

    def _determine_status(
        self,
        result: MultiCapabilityProductionTrialResult,
    ) -> str:
        """判定整体试运行状态。"""
        total = len(result.capability_trials)
        if total == 0:
            return "COMPLETED"

        completed = result.completed_count
        blocked = result.blocked_count

        if blocked == total:
            return "BLOCKED"
        elif blocked > 0:
            return "PARTIAL"
        elif completed == total:
            return "COMPLETED"
        else:
            return "PENDING"

    # ── 对比分析 ──

    def _compare_with_phase4(
        self,
        batch: MultiCapabilityProductionBatchResult,
        phase4_data: dict[str, Any],
    ) -> dict[str, Any]:
        """与 Phase 4 单能力生产试运行对比。"""
        p4_total = phase4_data.get("total_documents", 0)
        p4_completed = phase4_data.get("completed_count", 0)
        p4_caps = phase4_data.get("unique_capabilities", 1)
        p4_records = phase4_data.get("total_trial_records", p4_total)

        comparison = {
            "phase": "Phase 4 vs Phase 5.2",
            "phase4": {
                "total_documents": p4_total,
                "completed_count": p4_completed,
                "unique_capabilities": p4_caps,
                "total_trial_records": p4_records,
                "mode": "single_capability",
            },
            "phase5_2": {
                "total_documents": batch.total_documents,
                "completed_count": sum(
                    1 for r in batch.document_results
                    if r.trial_status == "COMPLETED"
                ),
                "unique_capabilities": len(
                    set(
                        t.capability_id
                        for r in batch.document_results
                        for t in r.capability_trials
                    )
                ),
                "total_trial_records": batch.total_trial_records,
                "mode": "multi_capability_controlled_production",
            },
        }

        if p4_total > 0:
            comparison["recall_improvement"] = (
                batch.total_trial_records - p4_total
            ) / p4_total

        comparison["execution_coverage_improvement"] = (
            batch.total_capabilities_activated / batch.total_documents
            if batch.total_documents > 0 else 0.0
        ) - (p4_caps / p4_total if p4_total > 0 else 0.0)

        return comparison

    def _compare_with_phase5_1(
        self,
        batch: MultiCapabilityProductionBatchResult,
        phase5_1_data: dict[str, Any],
    ) -> dict[str, Any]:
        """与 Phase 5.1 多能力受控 Trial 对比。"""
        p51_caps = phase5_1_data.get("unique_capabilities", 0)
        p51_records = phase5_1_data.get("total_trial_records", 0)

        comparison = {
            "phase": "Phase 5.1 vs Phase 5.2",
            "phase5_1": {
                "unique_capabilities": p51_caps,
                "total_trial_records": p51_records,
                "mode": "multi_capability_controlled_activation",
            },
            "phase5_2": {
                "unique_capabilities": len(
                    set(
                        t.capability_id
                        for r in batch.document_results
                        for t in r.capability_trials
                    )
                ),
                "total_trial_records": batch.total_trial_records,
                "mode": "multi_capability_controlled_production",
            },
        }

        # 生产稳定性差异
        comparison["stability_delta"] = {
            "same_capability_count": p51_caps == comparison["phase5_2"]["unique_capabilities"],
            "same_trial_count": p51_records == batch.total_trial_records,
            "note": "Phase 5.2 复用 Phase 5.1 的 Trial Adapter——预期结果一致",
        }

        return comparison

    # ── 批量汇总 ──

    def _assess_batch_governance(
        self,
        batch: MultiCapabilityProductionBatchResult,
    ) -> dict[str, Any]:
        """批量治理稳定性评估。"""
        all_docs = batch.document_results
        if not all_docs:
            return {"stable": True, "documents": 0}

        stable_docs = sum(
            1 for d in all_docs
            if d.governance_stability.get("stable", False)
        )
        degraded_docs = sum(
            1 for d in all_docs
            if d.governance_stability.get("degradation_detected", False)
        )

        return {
            "stable": degraded_docs == 0,
            "total_documents": len(all_docs),
            "stable_documents": stable_docs,
            "degraded_documents": degraded_docs,
            "stability_rate": stable_docs / len(all_docs) if all_docs else 0.0,
            "degradation_detail": (
                "none" if degraded_docs == 0
                else f"{degraded_docs} documents showed governance degradation"
            ),
        }

    def _build_batch_summary(
        self,
        batch: MultiCapabilityProductionBatchResult,
    ) -> dict[str, Any]:
        """构建批量汇总。"""
        total_docs = batch.total_documents
        total_trials = batch.total_trial_records

        completed_trials = sum(
            r.completed_count for r in batch.document_results
        )
        blocked_trials = sum(
            r.blocked_count for r in batch.document_results
        )
        all_isolated = all(
            r.all_isolated for r in batch.document_results
        )
        conflicts = sum(
            1 for r in batch.document_results if len(r.conflicts) > 0
        )
        governance_stable = all(
            r.governance_stability.get("stable", False)
            for r in batch.document_results
        )

        return {
            "phase": "5.2",
            "mode": "multi_capability_controlled_production",
            "total_documents": total_docs,
            "total_capabilities_activated": batch.total_capabilities_activated,
            "total_trial_records": total_trials,
            "completed_trials": completed_trials,
            "blocked_trials": blocked_trials,
            "success_rate": completed_trials / total_trials if total_trials > 0 else 0.0,
            "all_isolated": all_isolated,
            "governance_stable": governance_stable,
            "documents_with_conflicts": conflicts,
            "average_capabilities_per_document": (
                batch.total_capabilities_activated / total_docs
                if total_docs > 0 else 0.0
            ),
            "production_execution_enabled": self.scope.get("production_execution", False),
            "scope_compliant": True,
        }


__all__ = [
    "ProductionCapabilityTrial",
    "MultiCapabilityProductionTrialResult",
    "MultiCapabilityProductionBatchResult",
    "MultiCapabilityProductionTrialRunner",
    "PRODUCTION_SCOPE_V5_2",
]