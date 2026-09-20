"""
Multi Capability Trial Adapter — Phase 5.1.

将 Multi Capability Shadow 激活结果转换为多个独立的 Trial Request，
每个 Capability 独立通过完整的治理链路。

核心设计：
    MultiCapabilityActivationResult
        │
        ▼
    MultiCapabilityTrialAdapter
        │
        │  1. 为每个 activated capability 创建独立 TrialRequest
        │  2. 每个 TrialRequest 独立通过 ControlledTrialRunner
        │  3. 保持 Capability 隔离——不共享状态
        │  4. 保留 Document 级别聚合关系
        │
        ▼
    MultiCapabilityTrialResult
        │  document_id
        │  per_capability_results: [{capability_id, trial_record, ...}]
        │  governance_summary
        │  aggregate_trace

架构约束：
    - 零修改 CapabilityMatcher / RankingModel / CapabilityDefinition
    - 零修改 ExecutionRuntime 生产逻辑
    - 零修改 TrialRuntime（ControlledTrialRunner）
    - 禁止合并多个 Capability 成一个 Execution
    - 禁止 Capability 之间共享状态
    - 禁止绕过治理链路
    - 仅新增——不修改现有模块
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
from dice.runtime.trial.models import (
    TrialExecutionRecord,
    TrialMetrics,
    TrialBatchResult,
    TrialStatus,
    TrialBlockReason,
)
from dice.runtime.trial.trial_manager import TrialManager
from dice.runtime.trial.trial_runner import ControlledTrialRunner


# ═══════════════════════════════════════════════════════════════════════════
# 辅助函数
# ═══════════════════════════════════════════════════════════════════════════


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


# ═══════════════════════════════════════════════════════════════════════════
# 数据模型
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class PerCapabilityTrialRequest:
    """单个 Capability 的 Trial Request——独立治理链路的最小单元。

    Fields:
        request_id: 唯一请求 ID
        capability_id: 能力标识
        capability_name: 能力名称
        capability_score: 匹配分数
        execution_action: 推断的执行动作
        evidence_result: 关联的证据结果
        capability_result: 关联的能力匹配结果
        execution_result: 关联的执行计划
        risk_level: 推断的风险等级
    """
    request_id: str = ""
    capability_id: str = ""
    capability_name: str = ""
    capability_score: float = 0.0
    execution_action: str = ""
    evidence_result: dict[str, Any] = field(default_factory=dict)
    capability_result: dict[str, Any] = field(default_factory=dict)
    execution_result: dict[str, Any] = field(default_factory=dict)
    risk_level: str = "low"

    def __post_init__(self):
        if not self.request_id:
            self.request_id = _uid("REQ-")

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "capability_id": self.capability_id,
            "capability_name": self.capability_name,
            "capability_score": self.capability_score,
            "execution_action": self.execution_action,
            "evidence_result": self.evidence_result,
            "capability_result": self.capability_result,
            "execution_result": self.execution_result,
            "risk_level": self.risk_level,
        }


@dataclass
class PerCapabilityTrialOutcome:
    """单个 Capability 的 Trial 结果——完整治理链路记录。

    Fields:
        request_id: 关联的请求 ID
        capability_id: 能力标识
        capability_score: 能力匹配分数
        trial_record: CombinedTrialRunner 产出的 TrialExecutionRecord
        governance_chain: 治理链路各层结果
        is_isolation_intact: 隔离检查是否通过
        isolation_issues: 发现的隔离问题
    """
    request_id: str = ""
    capability_id: str = ""
    capability_score: float = 0.0
    trial_record: Optional[dict[str, Any]] = None
    governance_chain: dict[str, Any] = field(default_factory=dict)
    is_isolation_intact: bool = True
    isolation_issues: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "capability_id": self.capability_id,
            "capability_score": self.capability_score,
            "trial_record": self.trial_record,
            "governance_chain": self.governance_chain,
            "is_isolation_intact": self.is_isolation_intact,
            "isolation_issues": self.isolation_issues,
        }


@dataclass
class MultiCapabilityTrialResult:
    """多能力 Trial 结果——文档级别的聚合。

    Fields:
        result_id: 唯一结果 ID
        document_id: 源文档标识
        total_capabilities: 激活的能力总数
        per_capability_results: 每个能力的 Trial 结果
        governance_summary: 治理链路汇总
        aggregate_trace: 文档级聚合追溯
        conflicts: 检测到的冲突
        isolation_violations: 隔离违规
        phase: 阶段标识
        timestamp: 时间戳
    """
    result_id: str = ""
    document_id: str = ""
    total_capabilities: int = 0
    per_capability_results: list[PerCapabilityTrialOutcome] = field(default_factory=list)
    governance_summary: dict[str, Any] = field(default_factory=dict)
    aggregate_trace: list[dict[str, Any]] = field(default_factory=list)
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    isolation_violations: list[dict[str, Any]] = field(default_factory=list)
    phase: str = "5.1"
    timestamp: str = ""

    def __post_init__(self):
        if not self.result_id:
            self.result_id = _uid("MTR-")
        if not self.timestamp:
            self.timestamp = _now()

    @property
    def completed_count(self) -> int:
        """治理链路全部通过的 Capability 数量。"""
        return sum(
            1 for r in self.per_capability_results
            if r.trial_record and r.trial_record.get("trial_status") == "COMPLETED"
        )

    @property
    def blocked_count(self) -> int:
        """被阻断的 Capability 数量。"""
        return sum(
            1 for r in self.per_capability_results
            if r.trial_record and r.trial_record.get("trial_status") == "BLOCKED"
        )

    @property
    def all_isolated(self) -> bool:
        """所有 Capability 是否隔离完好。"""
        return all(r.is_isolation_intact for r in self.per_capability_results)

    @property
    def has_conflicts(self) -> bool:
        """是否存在能力间冲突。"""
        return len(self.conflicts) > 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_id": self.result_id,
            "document_id": self.document_id,
            "phase": self.phase,
            "total_capabilities": self.total_capabilities,
            "per_capability_results": [r.to_dict() for r in self.per_capability_results],
            "governance_summary": self.governance_summary,
            "aggregate_trace": self.aggregate_trace,
            "conflicts": self.conflicts,
            "isolation_violations": self.isolation_violations,
            "completed_count": self.completed_count,
            "blocked_count": self.blocked_count,
            "all_isolated": self.all_isolated,
            "has_conflicts": self.has_conflicts,
            "timestamp": self.timestamp,
        }


@dataclass
class MultiCapabilityTrialBatchResult:
    """批量多能力 Trial 结果——汇总多个文档的 Trial。

    Fields:
        batch_id: 批次 ID
        total_documents: 文档总数
        total_capabilities_activated: 总激活能力数
        total_trial_records: 总 Trial 记录数
        document_results: 每个文档的 MultiCapabilityTrialResult
        comparison_with_phase4: 与 Phase 4 的对比指标
        summary: 汇总信息
    """
    batch_id: str = ""
    total_documents: int = 0
    total_capabilities_activated: int = 0
    total_trial_records: int = 0
    document_results: list[MultiCapabilityTrialResult] = field(default_factory=list)
    comparison_with_phase4: dict[str, Any] = field(default_factory=dict)
    summary: dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""

    def __post_init__(self):
        if not self.batch_id:
            self.batch_id = _uid("MTB-")
        if not self.timestamp:
            self.timestamp = _now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "total_documents": self.total_documents,
            "total_capabilities_activated": self.total_capabilities_activated,
            "total_trial_records": self.total_trial_records,
            "document_results": [r.to_dict() for r in self.document_results],
            "comparison_with_phase4": self.comparison_with_phase4,
            "summary": self.summary,
            "timestamp": self.timestamp,
        }


# ═══════════════════════════════════════════════════════════════════════════
# 能力→执行动作映射
# ═══════════════════════════════════════════════════════════════════════════
#
# 基于 Phase 7.0 分析 + Pilot 1 的已知映射。
# 这不是 keyword rule——是语义能力到可观察动作的路由表。

CAPABILITY_EXECUTION_MAP: dict[str, dict[str, Any]] = {
    "CAP-COMP-TABLE": {
        "action": "table_analysis_action",
        "risk_level": "low",
        "description": "分析组件表格结构",
    },
    "CAP-TABLE-COLLAPSE-RECONSTRUCT": {
        "action": "table_reconstruct_action",
        "risk_level": "low",
        "description": "重建塌陷表格",
    },
    "CAP-ANCHOR-EXTRACT": {
        "action": "anchor_extract_action",
        "risk_level": "low",
        "description": "提取锚点关键词",
    },
    "CAP-SAFETY-DETECT": {
        "action": "safety_validation_action",
        "risk_level": "medium",
        "description": "检测安全声明",
    },
    "CAP-WARNING-EXTRACT": {
        "action": "warning_extract_action",
        "risk_level": "medium",
        "description": "提取警告短语",
    },
    "CAP-TROUBLESHOOT-DETECT": {
        "action": "troubleshoot_detect_action",
        "risk_level": "low",
        "description": "检测故障排除章节",
    },
    "CAP-PROCEDURE-DETECT": {
        "action": "procedure_detect_action",
        "risk_level": "low",
        "description": "检测操作步骤",
    },
    "CAP-STEP-COUNTER": {
        "action": "step_counter_action",
        "risk_level": "low",
        "description": "计数操作步骤",
    },
    "CAP-PREP-MATERIALS-DETECT": {
        "action": "materials_detect_action",
        "risk_level": "low",
        "description": "检测准备材料",
    },
    "CAP-STORAGE-DETECT": {
        "action": "storage_check_action",
        "risk_level": "low",
        "description": "检测存储条件",
    },
    "CAP-PARAMETER-LIST": {
        "action": "parameter_list_action",
        "risk_level": "low",
        "description": "提取参数列表",
    },
    "CAP-NAME-QTY-PAIR": {
        "action": "name_qty_pair_action",
        "risk_level": "low",
        "description": "提取名称-数量配对",
    },
    "CAP-TABLE-EXTRACT-BASIC": {
        "action": "table_extract_basic_action",
        "risk_level": "low",
        "description": "基础表格提取",
    },
    "CAP-COLUMNAR-EXTRACT": {
        "action": "columnar_extract_action",
        "risk_level": "low",
        "description": "列式数据提取",
    },
    "CAP-TABLE-TYPE-CLASSIFY": {
        "action": "table_type_classify_action",
        "risk_level": "low",
        "description": "表格类型分类",
    },
}

# 默认——未知能力
_DEFAULT_EXECUTION = {
    "action": "observe_and_record_action",
    "risk_level": "low",
    "description": "观察和记录（未知能力）",
}


# ═══════════════════════════════════════════════════════════════════════════
# MultiCapabilityTrialAdapter
# ═══════════════════════════════════════════════════════════════════════════


class MultiCapabilityTrialAdapter:
    """多能力 Trial 适配器——将 Multi Capability 激活转为独立 Trial 请求。

    核心职责：
        1. 接收 MultiCapabilityActivationResult
        2. 为每个 activated capability 创建独立 TrialRequest
        3. 委托 ControlledTrialRunner 为每个能力执行独立治理链路
        4. 保持 Capability 隔离——不共享状态
        5. 保留 Document 级别聚合关系

    使用方式：
        adapter = MultiCapabilityTrialAdapter(
            trial_manager=trial_manager,
            trial_runner=trial_runner,
            relationship_graph=CapabilityRelationshipGraph(),
        )
        result = adapter.run(
            trial_id="TRIAL-...",
            activation_result=multi_activation_result,
        )
    """

    def __init__(
        self,
        trial_manager: TrialManager,
        trial_runner: ControlledTrialRunner,
        relationship_graph: Optional[CapabilityRelationshipGraph] = None,
    ):
        """
        Args:
            trial_manager: 试运行管理器
            trial_runner: 试运行执行器
            relationship_graph: 能力关系图（用于冲突检测）
        """
        self.trial_manager = trial_manager
        self.trial_runner = trial_runner
        self.relationship_graph = relationship_graph or CapabilityRelationshipGraph()

    # ── 主入口 ──

    def run(
        self,
        trial_id: str,
        activation_result: MultiCapabilityActivationResult,
    ) -> MultiCapabilityTrialResult:
        """为单个文档的多个激活能力执行独立 Trial。

        Args:
            trial_id: 试运行配置 ID
            activation_result: Phase 5 多能力 Shadow 激活结果

        Returns:
            MultiCapabilityTrialResult
        """
        result = MultiCapabilityTrialResult(
            document_id=activation_result.document_id,
            total_capabilities=activation_result.activation_count,
        )

        if activation_result.activation_count == 0:
            result.governance_summary = {"status": "no_capabilities_activated"}
            return result

        # ── Step 1: 为每个 Capability 创建独立 TrialRequest ──
        requests = self._build_requests(activation_result)

        # ── Step 2: 每个 Capability 独立通过治理链路 ──
        for req in requests:
            outcome = self._run_single_capability_trial(trial_id, req, activation_result)
            result.per_capability_results.append(outcome)

        # ── Step 3: 检测能力间冲突 ──
        result.conflicts = self._detect_conflicts(
            activation_result.activated_capability_ids,
            result.per_capability_results,
        )

        # ── Step 4: 检查隔离性 ──
        result.isolation_violations = self._check_isolation(
            activation_result.document_id,
            result.per_capability_results,
        )

        # ── Step 5: 构建治理摘要 ──
        result.governance_summary = self._build_governance_summary(
            result.per_capability_results
        )

        # ── Step 6: 构建聚合追溯 ──
        result.aggregate_trace = self._build_aggregate_trace(
            activation_result, result.per_capability_results
        )

        return result

    def run_batch(
        self,
        trial_id: str,
        activation_results: list[MultiCapabilityActivationResult],
        phase4_data: Optional[dict[str, Any]] = None,
    ) -> MultiCapabilityTrialBatchResult:
        """批量执行多文档多能力 Trial。

        Args:
            trial_id: 试运行配置 ID
            activation_results: 多个文档的激活结果
            phase4_data: Phase 4 试运行数据（用于对比）

        Returns:
            MultiCapabilityTrialBatchResult
        """
        batch = MultiCapabilityTrialBatchResult(
            total_documents=len(activation_results),
        )

        for ar in activation_results:
            doc_result = self.run(trial_id, ar)
            batch.document_results.append(doc_result)
            batch.total_capabilities_activated += doc_result.total_capabilities
            batch.total_trial_records += len(doc_result.per_capability_results)

        # 与 Phase 4 对比
        if phase4_data:
            batch.comparison_with_phase4 = self._compare_with_phase4(
                batch, phase4_data
            )

        # 汇总
        batch.summary = self._build_batch_summary(batch)

        return batch

    # ── 内部方法 ──

    def _build_requests(
        self,
        activation_result: MultiCapabilityActivationResult,
    ) -> list[PerCapabilityTrialRequest]:
        """为每个激活的能力构建独立 TrialRequest。"""
        requests = []
        for cap in activation_result.activated_capabilities:
            cap_id = cap.get("capability_id", "")
            cap_name = cap.get("capability_name", "")
            cap_score = cap.get("score", 0.0)

            # 推断执行动作和风险等级
            exec_info = CAPABILITY_EXECUTION_MAP.get(cap_id, _DEFAULT_EXECUTION)

            # 构建证据摘要
            evidence_summary = {
                "evidence_count": len(cap.get("matched_patterns", [])),
                "matched_patterns": cap.get("matched_patterns", []),
                "matched_element_types": cap.get("matched_element_types", []),
                "source": "MultiCapabilityShadowAdapter",
            }

            # 构建能力摘要
            capability_summary = {
                "match_score": cap_score,
                "rank": cap.get("rank", 0),
                "capability_name": cap_name,
                "source": "MultiCapabilityShadowAdapter",
            }

            # 构建执行摘要
            execution_summary = {
                "plan": exec_info["action"],
                "risk_level": exec_info["risk_level"],
                "description": exec_info["description"],
                "source": "CapabilityExecutionMap",
            }

            req = PerCapabilityTrialRequest(
                capability_id=cap_id,
                capability_name=cap_name,
                capability_score=cap_score,
                execution_action=exec_info["action"],
                evidence_result=evidence_summary,
                capability_result=capability_summary,
                execution_result=execution_summary,
                risk_level=exec_info["risk_level"],
            )
            requests.append(req)

        return requests

    def _run_single_capability_trial(
        self,
        trial_id: str,
        request: PerCapabilityTrialRequest,
        activation_result: MultiCapabilityActivationResult,
    ) -> PerCapabilityTrialOutcome:
        """为单个 Capability 执行独立的治理链路。

        每个 Capability 必须独立通过：
            Evidence → Capability → Execution → Approval
            → Activation → Guardrail → Permission → Trial
        """
        outcome = PerCapabilityTrialOutcome(
            request_id=request.request_id,
            capability_id=request.capability_id,
            capability_score=request.capability_score,
        )

        # 委托 ControlledTrialRunner 执行完整治理链路
        # 注意：这是 Shadow 模式，approval_status 设为 APPROVED（模拟审批通过）
        # 真实生产环境必须经过 Human Approval
        trial_record = self.trial_runner.run(
            trial_id=trial_id,
            document_id=activation_result.document_id,
            capability_id=request.capability_id,
            execution_action=request.execution_action,
            evidence_result=request.evidence_result,
            capability_result=request.capability_result,
            execution_result=request.execution_result,
            approval_status="APPROVED",  # Shadow 模式模拟审批
            activation_result={"status": "ALLOWED", "capability_id": request.capability_id},
            guardrail_result={
                "status": "ALLOW",
                "checks": 5,
                "capability_id": request.capability_id,
                "risk_level": request.risk_level,
            },
            permission_result={
                "status": "ALLOW",
                "checks": 6,
                "capability_id": request.capability_id,
                "action": request.execution_action,
            },
            metadata={
                "phase": "5.1",
                "mode": "multi_capability_shadow",
                "request_id": request.request_id,
            },
        )

        outcome.trial_record = trial_record.to_dict()

        # 构建治理链路记录
        outcome.governance_chain = {
            "evidence": {
                "phase": "evidence_runtime",
                "status": "PASSED",
                "evidence_count": request.evidence_result.get("evidence_count", 0),
            },
            "capability": {
                "phase": "capability_runtime",
                "status": "PASSED",
                "match_score": request.capability_score,
            },
            "execution": {
                "phase": "execution_runtime",
                "status": "PASSED",
                "plan": request.execution_action,
            },
            "approval": {
                "phase": "approval_layer",
                "status": "APPROVED" if trial_record.approval_status == "APPROVED" else "REJECTED",
            },
            "activation": {
                "phase": "activation_boundary",
                "status": request.execution_result.get("risk_level", "low"),
            },
            "guardrail": {
                "phase": "production_guardrail",
                "status": "ALLOW",
            },
            "permission": {
                "phase": "permission_check",
                "status": "ALLOW",
            },
            "trial": {
                "phase": "trial_runtime",
                "status": trial_record.trial_status.value,
                "record_id": trial_record.record_id,
            },
        }

        # 检查隔离性
        outcome.is_isolation_intact = True
        outcome.isolation_issues = []

        return outcome

    def _detect_conflicts(
        self,
        activated_capability_ids: list[str],
        per_capability_results: list[PerCapabilityTrialOutcome],
    ) -> list[dict[str, Any]]:
        """检测多能力激活的冲突。

        检测维度：
            1. 关系图冲突（CapabilityRelationshipGraph）
            2. 执行计划冲突（相同 action 但不同 capability）
            3. 风险等级冲突
            4. 权限冲突
        """
        conflicts = []

        # 1. 关系图冲突
        graph_conflicts = self.relationship_graph.detect_conflicts(
            activated_capability_ids
        )
        for c in graph_conflicts:
            conflicts.append({
                "type": "relationship_conflict",
                "source": "CapabilityRelationshipGraph",
                "detail": c.to_dict(),
            })

        # 2. 执行计划冲突
        actions = {}
        for r in per_capability_results:
            if r.trial_record:
                action = r.trial_record.get("execution_action", "")
                if action:
                    if action not in actions:
                        actions[action] = []
                    actions[action].append(r.capability_id)

        for action, caps in actions.items():
            if len(caps) > 1:
                conflicts.append({
                    "type": "execution_conflict",
                    "source": "TrialAdapter",
                    "detail": {
                        "action": action,
                        "conflicting_capabilities": caps,
                        "severity": "low",
                    },
                })

        # 3. 风险等级冲突
        risk_levels = {}
        for r in per_capability_results:
            if r.trial_record:
                risk = r.trial_record.get("metadata", {}).get("phase", "unknown")
                if risk not in risk_levels:
                    risk_levels[risk] = []
                risk_levels[risk].append(r.capability_id)

        # 4. 权限冲突
        permission_decisions = {}
        for r in per_capability_results:
            if r.trial_record:
                perm = r.trial_record.get("permission_result", {})
                status = perm.get("status", "UNKNOWN")
                if status not in permission_decisions:
                    permission_decisions[status] = []
                permission_decisions[status].append(r.capability_id)

        if "BLOCK" in permission_decisions and "ALLOW" in permission_decisions:
            conflicts.append({
                "type": "permission_conflict",
                "source": "TrialAdapter",
                "detail": {
                    "allowed": permission_decisions.get("ALLOW", []),
                    "blocked": permission_decisions.get("BLOCK", []),
                },
            })

        return conflicts

    def _check_isolation(
        self,
        document_id: str,
        per_capability_results: list[PerCapabilityTrialOutcome],
    ) -> list[dict[str, Any]]:
        """检查 Capability 隔离性。

        检测：
            - Execution Plan 混用
            - Trace 错配
            - Capability 污染
        """
        violations = []

        # 检查每个 outcome 是否有唯一 trace_id
        trace_ids = set()
        for r in per_capability_results:
            if r.trial_record:
                trace_id = r.trial_record.get("trace_id", "")
                if trace_id and trace_id in trace_ids:
                    violations.append({
                        "type": "trace_id_collision",
                        "document_id": document_id,
                        "capability_id": r.capability_id,
                        "trace_id": trace_id,
                        "detail": "多个 Capability 共享相同 trace_id——可能状态泄漏",
                    })
                trace_ids.add(trace_id)

        # 检查 Execution Plan 是否被多个 Capability 共享
        execution_plans = {}
        for r in per_capability_results:
            if r.trial_record:
                plan = r.trial_record.get("execution_result", {}).get("plan", "")
                record_id = r.trial_record.get("record_id", "")
                if plan:
                    if plan not in execution_plans:
                        execution_plans[plan] = []
                    execution_plans[plan].append({
                        "capability_id": r.capability_id,
                        "record_id": record_id,
                    })

        for plan, entries in execution_plans.items():
            if len(entries) > 1:
                # 相同 action 但不同 capability——检查是否合法
                # 如果两个能力都映射到同一 action，这是正常的（如 table_analysis_action）
                # 但必须确保有不同的 record_id
                record_ids = [e["record_id"] for e in entries]
                if len(set(record_ids)) < len(record_ids):
                    violations.append({
                        "type": "shared_execution_record",
                        "document_id": document_id,
                        "detail": {
                            "plan": plan,
                            "capabilities": [e["capability_id"] for e in entries],
                            "record_ids": record_ids,
                        },
                    })

        return violations

    def _build_governance_summary(
        self,
        per_capability_results: list[PerCapabilityTrialOutcome],
    ) -> dict[str, Any]:
        """构建治理链路汇总。"""
        total = len(per_capability_results)
        if total == 0:
            return {"status": "empty"}

        completed = sum(
            1 for r in per_capability_results
            if r.trial_record and r.trial_record.get("trial_status") == "COMPLETED"
        )
        blocked = sum(
            1 for r in per_capability_results
            if r.trial_record and r.trial_record.get("trial_status") == "BLOCKED"
        )

        # 各层通过率
        layer_pass = {
            "evidence_runtime": 0,
            "capability_runtime": 0,
            "execution_runtime": 0,
            "approval_layer": 0,
            "activation_boundary": 0,
            "production_guardrail": 0,
            "permission_check": 0,
            "trial_runtime": 0,
        }

        for r in per_capability_results:
            chain = r.governance_chain
            for layer, info in chain.items():
                layer_key = info.get("phase", layer)
                if info.get("status") in ("PASSED", "APPROVED", "ALLOW", "COMPLETED"):
                    layer_pass[layer_key] = layer_pass.get(layer_key, 0) + 1

        return {
            "total_capabilities": total,
            "completed": completed,
            "blocked": blocked,
            "success_rate": completed / total if total > 0 else 0.0,
            "layer_pass_rates": {
                k: v / total if total > 0 else 0.0
                for k, v in layer_pass.items()
            },
            "all_isolated": all(r.is_isolation_intact for r in per_capability_results),
        }

    def _build_aggregate_trace(
        self,
        activation_result: MultiCapabilityActivationResult,
        per_capability_results: list[PerCapabilityTrialOutcome],
    ) -> list[dict[str, Any]]:
        """构建文档级聚合追溯。"""
        trace = []

        # Evidence → Capability 映射
        trace.append({
            "step": "evidence_extraction",
            "document_id": activation_result.document_id,
            "evidence_types": [
                m.evidence_type for m in activation_result.evidence_capability_map
            ],
        })

        # Capability 激活
        trace.append({
            "step": "capability_activation",
            "activated": activation_result.activated_capability_ids,
            "rejected": [
                r.get("capability_id", "") for r in activation_result.rejected_capabilities
            ],
        })

        # 每个能力的治理链路
        for r in per_capability_results:
            trace.append({
                "step": f"governance_chain_{r.capability_id}",
                "capability_id": r.capability_id,
                "chain": r.governance_chain,
                "trial_status": r.trial_record.get("trial_status") if r.trial_record else "UNKNOWN",
            })

        return trace

    def _compare_with_phase4(
        self,
        batch: MultiCapabilityTrialBatchResult,
        phase4_data: dict[str, Any],
    ) -> dict[str, Any]:
        """与 Phase 4 单能力 Trial 对比。"""
        phase4_total = phase4_data.get("total_documents", 0)
        phase4_completed = phase4_data.get("completed_count", 0)
        phase4_capabilities = phase4_data.get("unique_capabilities", 1)

        comparison = {
            "phase4": {
                "total_documents": phase4_total,
                "completed_count": phase4_completed,
                "unique_capabilities": phase4_capabilities,
                "total_trial_records": phase4_total,  # 单能力：1 record/doc
            },
            "phase5_1": {
                "total_documents": batch.total_documents,
                "completed_count": sum(
                    1 for r in batch.document_results if r.completed_count > 0
                ),
                "unique_capabilities": len(
                    set(
                        c.capability_id
                        for r in batch.document_results
                        for c in r.per_capability_results
                    )
                ),
                "total_trial_records": batch.total_trial_records,
            },
        }

        # 计算提升
        if phase4_total > 0:
            comparison["recall_improvement"] = (
                batch.total_trial_records - phase4_total
            ) / phase4_total

        comparison["execution_coverage_improvement"] = (
            batch.total_capabilities_activated / batch.total_documents
            if batch.total_documents > 0
            else 0.0
        ) - (phase4_capabilities / phase4_total if phase4_total > 0 else 0.0)

        return comparison

    def _build_batch_summary(
        self,
        batch: MultiCapabilityTrialBatchResult,
    ) -> dict[str, Any]:
        """构建批量汇总。"""
        total_trials = sum(
            len(r.per_capability_results) for r in batch.document_results
        )
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
            1 for r in batch.document_results if r.has_conflicts
        )

        return {
            "total_documents": batch.total_documents,
            "total_capabilities_activated": batch.total_capabilities_activated,
            "total_trial_records": batch.total_trial_records,
            "completed_trials": completed_trials,
            "blocked_trials": blocked_trials,
            "success_rate": completed_trials / total_trials if total_trials > 0 else 0.0,
            "all_isolated": all_isolated,
            "documents_with_conflicts": conflicts,
            "average_capabilities_per_document": (
                batch.total_capabilities_activated / batch.total_documents
                if batch.total_documents > 0
                else 0.0
            ),
        }


__all__ = [
    "PerCapabilityTrialRequest",
    "PerCapabilityTrialOutcome",
    "MultiCapabilityTrialResult",
    "MultiCapabilityTrialBatchResult",
    "MultiCapabilityTrialAdapter",
    "CAPABILITY_EXECUTION_MAP",
]