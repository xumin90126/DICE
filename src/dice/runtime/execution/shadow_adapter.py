"""
Execution Runtime Shadow Adapter — Phase 2 Step 5.

Consumes CapabilityActivationShadowResult, produces simulated
ExecutionPlanShadowResult. Simulates execution plans with
input validation, confidence scoring, and trace generation.

CRITICAL ARCHITECTURE:
    Capability Runtime  ──(orthogonal)──>  Execution Runtime
    "Which capability?"                    "How to execute it?"

    Evidence → Capability → Execution Plan

    This adapter bridges Capability activation to Execution planning
    WITHOUT executing real actions. It validates the execution boundary
    by checking:
    - Required inputs vs available evidence
    - Execution confidence
    - Risk level
    - Trace completeness

CONSTRAINTS:
    - Zero real execution
    - Zero ExecutionRuntime modification
    - Zero CapabilityMatcher modification
    - Zero CapabilityDefinition modification
    - Zero keyword rules
    - Zero document-specific logic
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


# ═══════════════════════════════════════════════════════════════════════════
# Capability → Action Mapping
# ═══════════════════════════════════════════════════════════════════════════
#
# Maps each capability to its expected execution action and required inputs.
# This is a STRUCTURAL mapping — no keyword rules, no document-specific logic.
#
# Each entry defines:
#   - action: the execution action name
#   - category: execution category (extract, validate, check, detect)
#   - required_inputs: evidence types needed for execution
#   - optional_inputs: evidence types that improve execution but not required
#   - risk_level: inherent risk level of this execution

CAPABILITY_ACTION_MAP: dict[str, dict[str, Any]] = {
    "CAP-STORAGE-DETECT": {
        "action": "create_storage_requirement_check",
        "category": "check",
        "required_inputs": ["storage_condition"],
        "optional_inputs": ["temperature_range", "time_duration"],
        "risk_level": "low",
        "description": "验证文档是否包含存储条件要求",
    },
    "CAP-STORAGE-LONG-TERM": {
        "action": "create_long_term_storage_check",
        "category": "check",
        "required_inputs": ["storage_condition"],
        "optional_inputs": ["temperature_range", "time_duration"],
        "risk_level": "low",
        "description": "验证文档是否包含长期存储条件",
    },
    "CAP-SAFETY-DETECT": {
        "action": "create_safety_requirement_check",
        "category": "detect",
        "required_inputs": ["safety_statement"],
        "optional_inputs": ["warning_statement"],
        "risk_level": "high",
        "description": "检测文档中的安全警告和要求",
    },
    "CAP-WARNING-EXTRACT": {
        "action": "extract_warning_statements",
        "category": "extract",
        "required_inputs": ["safety_statement"],
        "optional_inputs": ["warning_statement"],
        "risk_level": "medium",
        "description": "提取文档中的警告声明",
    },
    "CAP-TROUBLESHOOT-DETECT": {
        "action": "create_troubleshooting_check",
        "category": "detect",
        "required_inputs": ["anomaly_recovery", "condition_procedure"],
        "optional_inputs": ["test_method"],
        "risk_level": "medium",
        "description": "检测文档中的故障排除指南",
    },
    "CAP-PROCEDURE-DETECT": {
        "action": "create_procedure_validation",
        "category": "validate",
        "required_inputs": ["sequential_step", "condition_procedure"],
        "optional_inputs": ["preparation_step"],
        "risk_level": "low",
        "description": "验证文档中的操作步骤完整性",
    },
    "CAP-PREP-MATERIALS-DETECT": {
        "action": "create_materials_check",
        "category": "check",
        "required_inputs": ["preparation_step", "component_spec"],
        "optional_inputs": ["test_method"],
        "risk_level": "low",
        "description": "检查文档中的材料准备要求",
    },
}

# Evidence types that might be available from Evidence Runtime
ALL_EVIDENCE_TYPES = [
    "storage_condition", "safety_statement", "anomaly_recovery",
    "sequential_step", "condition_procedure", "preparation_step",
    "test_method", "comparison", "component_spec",
]

# ═══════════════════════════════════════════════════════════════════════════
# Data Types
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class ExecutionPlanShadowResult:
    """
    Shadow Execution Plan for one capability activation.

    Fields:
        document_id: 源文档标识
        capability_id: 激活的能力标识
        capability_name: 能力名称
        selected_action: 选择的执行动作
        action_category: 执行类别 (extract/validate/check/detect)
        required_inputs: 执行所需的输入证据类型
        available_inputs: 实际可用的输入证据类型
        missing_inputs: 缺失的输入证据类型
        execution_confidence: 执行置信度 (0-1)
        risk_level: 风险等级 (low/medium/high/critical)
        validation_result: 验证结果 (PASS/WARN/FAIL)
        reasoning: 人可读的推理说明
        trace_reference: 证据→能力→执行的完整追溯
    """
    document_id: str = ""
    capability_id: str = ""
    capability_name: str = ""
    selected_action: str = ""
    action_category: str = ""
    required_inputs: list[str] = field(default_factory=list)
    available_inputs: list[str] = field(default_factory=list)
    missing_inputs: list[str] = field(default_factory=list)
    execution_confidence: float = 0.0
    risk_level: str = "low"
    validation_result: str = "PASS"
    reasoning: str = ""
    trace_reference: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "capability_id": self.capability_id,
            "capability_name": self.capability_name,
            "selected_action": self.selected_action,
            "action_category": self.action_category,
            "required_inputs": self.required_inputs,
            "available_inputs": self.available_inputs,
            "missing_inputs": self.missing_inputs,
            "execution_confidence": round(self.execution_confidence, 4),
            "risk_level": self.risk_level,
            "validation_result": self.validation_result,
            "reasoning": self.reasoning,
            "trace_reference": self.trace_reference,
        }


@dataclass
class ExecutionShadowBatchResult:
    """
    Batch shadow execution result for all documents.
    """
    batch_id: str = ""
    generated_at: str = ""
    total_documents: int = 0
    total_plans: int = 0
    plans: list[ExecutionPlanShadowResult] = field(default_factory=list)
    statistics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "generated_at": self.generated_at,
            "total_documents": self.total_documents,
            "total_plans": self.total_plans,
            "plans": [p.to_dict() for p in self.plans],
            "statistics": self.statistics,
        }


# ═══════════════════════════════════════════════════════════════════════════
# ExecutionRuntimeShadowAdapter
# ═══════════════════════════════════════════════════════════════════════════


class ExecutionRuntimeShadowAdapter:
    """
    执行运行时影子适配器。

    消费 CapabilityActivationShadowResult，生成模拟的 ExecutionPlanShadowResult。
    不对文档执行实际操作——仅验证执行边界。

    使用方式:
        adapter = ExecutionRuntimeShadowAdapter()
        result = adapter.simulate_execution(
            capability_activation=cap_activation_dict,
            evidence_data=evidence_dict,
        )
        # result.selected_action, result.validation_result, etc.
    """

    def __init__(self) -> None:
        """初始化适配器。无需外部依赖。"""
        pass

    def simulate_execution(
        self,
        capability_activation: dict[str, Any],
        evidence_data: dict[str, Any],
        document_id: str = "",
    ) -> ExecutionPlanShadowResult:
        """
        模拟单个能力的执行计划。

        参数:
            capability_activation: 单个能力激活的字典
                (从 CapabilityActivationShadowResult.activated_capabilities 获取)
            evidence_data: 文档的证据数据
                (从 shadow_evidence.json 的 per_document 获取)
            document_id: 文档标识

        返回:
            ExecutionPlanShadowResult 包含完整的执行计划模拟
        """
        cap_id = capability_activation.get("capability_id", "")
        cap_name = capability_activation.get("capability_name", "")
        cap_score = capability_activation.get("score", 0.0)

        # ── Step 1: 确定执行动作 ──
        action_def = CAPABILITY_ACTION_MAP.get(cap_id)
        if action_def is None:
            # 未知能力——使用通用执行计划
            return self._make_generic_plan(
                cap_id, cap_name, cap_score, evidence_data, document_id,
            )

        action = action_def["action"]
        category = action_def["category"]
        required = action_def["required_inputs"]
        optional = action_def.get("optional_inputs", [])
        base_risk = action_def["risk_level"]
        description = action_def.get("description", "")

        # ── Step 2: 检查可用输入 ──
        available_evidence_types = self._extract_evidence_types(evidence_data)

        available_inputs = [
            et for et in required + optional
            if et in available_evidence_types
        ]
        missing_inputs = [
            et for et in required
            if et not in available_evidence_types
        ]

        # ── Step 3: 计算执行置信度 ──
        # 基础：能力匹配分数
        base_confidence = cap_score

        # 输入完整性加成
        if len(required) > 0:
            input_completeness = 1.0 - (len(missing_inputs) / len(required))
        else:
            input_completeness = 1.0

        # 可选输入加成
        optional_bonus = 0.0
        if optional:
            optional_available = len([
                o for o in optional if o in available_inputs
            ])
            optional_bonus = 0.1 * (optional_available / len(optional))

        execution_confidence = min(1.0, base_confidence * 0.7 + input_completeness * 0.25 + optional_bonus)

        # ── Step 4: 确定风险等级 ──
        if missing_inputs:
            if base_risk == "high":
                risk_level = "critical"
            elif base_risk == "medium":
                risk_level = "high"
            else:
                risk_level = "medium"
        else:
            risk_level = base_risk

        # ── Step 5: 验证结果 ──
        if missing_inputs:
            if len(missing_inputs) == len(required):
                validation_result = "FAIL"
            else:
                validation_result = "WARN"
        else:
            validation_result = "PASS"

        # ── Step 6: 生成推理说明 ──
        reasoning = self._build_reasoning(
            cap_name, action, description,
            required, available_inputs, missing_inputs,
            execution_confidence, validation_result,
        )

        # ── Step 7: 构建追溯引用 ──
        trace_reference = {
            "evidence_id": capability_activation.get("evidence_id", ""),
            "capability_score": cap_score,
            "matched_patterns": capability_activation.get("matched_patterns", []),
            "evidence_type_distribution": {
                k: v for k, v in evidence_data.get("evidence_type_distribution", {}).items()
                if k in required + optional
            },
        }

        return ExecutionPlanShadowResult(
            document_id=document_id,
            capability_id=cap_id,
            capability_name=cap_name,
            selected_action=action,
            action_category=category,
            required_inputs=required,
            available_inputs=available_inputs,
            missing_inputs=missing_inputs,
            execution_confidence=execution_confidence,
            risk_level=risk_level,
            validation_result=validation_result,
            reasoning=reasoning,
            trace_reference=trace_reference,
        )

    def simulate_batch(
        self,
        shadow_data: dict[str, Any],
        capability_activation_results: list[dict[str, Any]],
    ) -> ExecutionShadowBatchResult:
        """
        对所有文档和所有能力激活执行批量模拟。

        参数:
            shadow_data: shadow_evidence.json 完整数据
            capability_activation_results: CapabilityActivationShadowResult 列表
                (从 Step 4 的 shadow_comparison.json 获取)

        返回:
            ExecutionShadowBatchResult 包含所有执行计划
        """
        batch_id = _uid("EXEC-BATCH-")
        plans: list[ExecutionPlanShadowResult] = []

        # 构建文档证据索引
        doc_evidence_index: dict[str, dict[str, Any]] = {}
        for doc_data in shadow_data.get("per_document", []):
            doc_id = doc_data.get("document_id", "unknown")
            doc_evidence_index[doc_id] = doc_data

        for cap_result in capability_activation_results:
            doc_id = cap_result.get("document_id", "")
            evidence_data = doc_evidence_index.get(doc_id, {})

            # 获取该文档的已激活能力
            activated_caps = cap_result.get("activated_capabilities", [])

            for cap_activation in activated_caps:
                plan = self.simulate_execution(
                    capability_activation=cap_activation,
                    evidence_data=evidence_data,
                    document_id=doc_id,
                )
                plans.append(plan)

        # ── 统计信息 ──
        stats = self._compute_statistics(plans)

        return ExecutionShadowBatchResult(
            batch_id=batch_id,
            generated_at=_now(),
            total_documents=len(capability_activation_results),
            total_plans=len(plans),
            plans=plans,
            statistics=stats,
        )

    # ═══════════════════════════════════════════════════════════════════
    # 内部方法
    # ═══════════════════════════════════════════════════════════════════

    @staticmethod
    def _extract_evidence_types(evidence_data: dict[str, Any]) -> set[str]:
        """从证据数据中提取可用的证据类型。"""
        types: set[str] = set()
        ev_type_dist = evidence_data.get("evidence_type_distribution", {})
        for ev_type, count in ev_type_dist.items():
            if count > 0:
                types.add(ev_type)
        return types

    def _make_generic_plan(
        self,
        cap_id: str,
        cap_name: str,
        cap_score: float,
        evidence_data: dict[str, Any],
        document_id: str,
    ) -> ExecutionPlanShadowResult:
        """为未知能力生成通用执行计划。"""
        available_types = self._extract_evidence_types(evidence_data)

        return ExecutionPlanShadowResult(
            document_id=document_id,
            capability_id=cap_id,
            capability_name=cap_name,
            selected_action="generic_execution",
            action_category="unknown",
            required_inputs=[],
            available_inputs=sorted(available_types),
            missing_inputs=[],
            execution_confidence=cap_score * 0.5,
            risk_level="medium",
            validation_result="WARN",
            reasoning=(
                f"未知能力 '{cap_name}' ({cap_id})——无预定义执行动作。"
                f"使用通用执行计划，置信度降低至 {cap_score * 0.5:.3f}。"
            ),
            trace_reference={"capability_score": cap_score},
        )

    @staticmethod
    def _build_reasoning(
        cap_name: str,
        action: str,
        description: str,
        required: list[str],
        available: list[str],
        missing: list[str],
        confidence: float,
        validation: str,
    ) -> str:
        """构建人可读的推理说明。"""
        parts = [
            f"能力 '{cap_name}' → 执行动作 '{action}'",
            f"({description})" if description else "",
        ]
        parts = [p for p in parts if p]

        parts.append(f"必需输入: {required}")
        parts.append(f"可用输入: {available}")
        if missing:
            parts.append(f"缺失输入: {missing}")
        parts.append(f"执行置信度: {confidence:.3f}")
        parts.append(f"验证结果: {validation}")

        return " | ".join(parts)

    @staticmethod
    def _compute_statistics(
        plans: list[ExecutionPlanShadowResult],
    ) -> dict[str, Any]:
        """计算批量执行统计信息。"""
        if not plans:
            return {}

        total = len(plans)
        pass_count = sum(1 for p in plans if p.validation_result == "PASS")
        warn_count = sum(1 for p in plans if p.validation_result == "WARN")
        fail_count = sum(1 for p in plans if p.validation_result == "FAIL")

        # 风险分布
        risk_dist: dict[str, int] = {}
        for p in plans:
            risk_dist[p.risk_level] = risk_dist.get(p.risk_level, 0) + 1

        # 能力分布
        cap_dist: dict[str, int] = {}
        for p in plans:
            cap_dist[p.capability_id] = cap_dist.get(p.capability_id, 0) + 1

        # 平均置信度
        avg_confidence = sum(p.execution_confidence for p in plans) / total if total > 0 else 0.0

        # 缺失输入分析
        plans_with_missing = sum(1 for p in plans if p.missing_inputs)
        total_missing = sum(len(p.missing_inputs) for p in plans)

        return {
            "total_plans": total,
            "validation_pass": pass_count,
            "validation_warn": warn_count,
            "validation_fail": fail_count,
            "pass_rate": round(pass_count / total, 4) if total > 0 else 0.0,
            "risk_distribution": risk_dist,
            "capability_distribution": cap_dist,
            "avg_execution_confidence": round(avg_confidence, 4),
            "plans_with_missing_inputs": plans_with_missing,
            "total_missing_inputs": total_missing,
        }


# ═══════════════════════════════════════════════════════════════════════════
# 模块级辅助函数
# ═══════════════════════════════════════════════════════════════════════════


# ── 能力类型分类（基于 Step 4 的 semantic_distribution） ──
_SEMANTIC_CAPABILITIES: set[str] = {
    "CAP-PREP-MATERIALS-DETECT",
    "CAP-PROCEDURE-DETECT",
    "CAP-STORAGE-DETECT",
    "CAP-SAFETY-DETECT",
    "CAP-STORAGE-LONG-TERM",
    "CAP-WARNING-EXTRACT",
    "CAP-TROUBLESHOOT-DETECT",
}


def _capability_id_to_name(cap_id: str) -> str:
    """从能力 ID 推导人类可读的名称。"""
    # 移除 CAP- 前缀，将剩余部分转为可读名称
    name = cap_id.removeprefix("CAP-")
    # 将连字符替换为空格，每个单词首字母大写
    parts = name.split("-")
    readable = " ".join(p.title() for p in parts)
    return readable


def _classify_capability_type(cap_id: str) -> str:
    """判断能力是语义型还是结构型。"""
    return "semantic" if cap_id in _SEMANTIC_CAPABILITIES else "structural"


def load_capability_activation_results(path: str) -> list[dict[str, Any]]:
    """从 Step 4 的 comparison_report.json 加载能力激活结果。

    数据格式适配:
        comparison_report.json 中 shadow 字段为:
        {
            "capabilities": ["CAP-STORAGE-DETECT", ...],    # 字符串列表
            "scores": {"CAP-STORAGE-DETECT": 0.82, ...}     # Dict[str, float]
        }

        转换为:
        {
            "document_id": "...",
            "activated_capabilities": [
                {
                    "capability_id": "CAP-STORAGE-DETECT",
                    "capability_name": "Storage Detect",
                    "score": 0.82,
                    "matched_patterns": [],
                    "capability_type": "semantic"
                },
                ...
            ]
        }
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results: list[dict[str, Any]] = []
    for doc_data in data.get("per_document", []):
        shadow = doc_data.get("shadow", {})
        cap_ids: list[str] = shadow.get("capabilities", [])
        scores: dict[str, float] = shadow.get("scores", {})

        activated_caps = []
        for cap_id in cap_ids:
            score = scores.get(cap_id, 0.0)
            if score < 0.25:  # 只取阈值以上的
                continue
            activated_caps.append({
                "capability_id": cap_id,
                "capability_name": _capability_id_to_name(cap_id),
                "score": score,
                "matched_patterns": [],  # Step 4 影子输出不包含 patterns 字段
                "capability_type": _classify_capability_type(cap_id),
            })

        results.append({
            "document_id": doc_data.get("document_id", ""),
            "activated_capabilities": activated_caps,
        })

    return results


def load_shadow_evidence(path: str) -> dict[str, Any]:
    """加载 shadow_evidence.json。"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


__all__ = [
    "ExecutionRuntimeShadowAdapter",
    "ExecutionPlanShadowResult",
    "ExecutionShadowBatchResult",
    "CAPABILITY_ACTION_MAP",
    "load_capability_activation_results",
    "load_shadow_evidence",
]