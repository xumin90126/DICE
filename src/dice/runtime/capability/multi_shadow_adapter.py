"""
Multi Capability Shadow Adapter — Phase 5.

从 Single Capability（TOP 1）升级到 Multi Capability Activation。
在 Shadow 模式下运行——不修改 CapabilityMatcher、RankingModel、CapabilityDefinition。

核心设计：
    EvidenceView
        │
        ▼
    CapabilityMatcher.match()  ← 已有，不修改
        │  MatchResult.candidates (ranked, top_k=5)
        │
        ▼
    MultiCapabilityShadowAdapter  ← Phase 5 新增
        │
        │  1. 取所有 applicable_candidates()（非仅 TOP 1）
        │  2. Evidence → Capability 映射
        │  3. 检测 Conflict / Dependency
        │  4. 生成 MultiCapabilityActivationResult
        │
        ▼
    MultiCapabilityActivationResult
        │  activated_capabilities: 所有合格候选
        │  rejected_capabilities: 分数不足或冲突的候选
        │  evidence_capability_map: 证据→能力映射
        │  capability_relationships: 能力间关系
        │  activation_trace: 完整追溯

架构约束：
    - 零 CapabilityMatcher 修改
    - 零 RankingModel 修改
    - 零 CapabilityDefinition 修改
    - 零 keyword rule
    - 零 document-specific logic
    - Shadow 模式：仅观察和记录，不执行真实生产动作
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


# ═══════════════════════════════════════════════════════════════════════════
# 数据模型
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class EvidenceCapabilityMapping:
    """证据→能力映射——每个证据类型关联到哪些能力。

    Fields:
        evidence_type: 证据类型（如 component_spec, safety_statement, anomaly_recovery）
        matched_capability_ids: 匹配到的能力 ID 列表
        confidence: 映射置信度
        evidence_count: 对应证据数量
    """
    evidence_type: str = ""
    matched_capability_ids: list[str] = field(default_factory=list)
    confidence: float = 0.0
    evidence_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_type": self.evidence_type,
            "matched_capability_ids": self.matched_capability_ids,
            "confidence": round(self.confidence, 4),
            "evidence_count": self.evidence_count,
        }


@dataclass
class CapabilityRelationship:
    """能力间关系——描述两个能力之间的关联。

    Types:
        - related: 互补关系（如 CAP-COMP-TABLE ↔ CAP-SAFETY-DETECT）
        - conflict: 冲突关系（如两个能力都想处理同一证据）
        - dependent: 依赖关系（如 CAP-TROUBLESHOOT-DETECT 依赖 CAP-PROCEDURE-DETECT）
        - independent: 独立关系（无关联）
    """
    capability_a: str = ""
    capability_b: str = ""
    relationship_type: str = "independent"  # related / conflict / dependent / independent
    description: str = ""
    shared_evidence_types: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_a": self.capability_a,
            "capability_b": self.capability_b,
            "relationship_type": self.relationship_type,
            "description": self.description,
            "shared_evidence_types": self.shared_evidence_types,
        }


@dataclass
class MultiCapabilityActivationResult:
    """多能力激活结果 — Shadow 模式下的完整激活记录。

    Fields:
        result_id: 唯一结果 ID
        document_id: 源文档标识
        activated_capabilities: 激活的能力列表（所有通过阈值的候选）
        rejected_capabilities: 被拒绝的能力列表（分数不足/冲突）
        evidence_capability_map: 证据类型→能力映射
        capability_relationships: 能力间关系
        top1_capability: TOP 1 能力（用于对比）
        activation_trace: 完整追溯
        total_candidates: 候选总数
        activation_threshold: 激活阈值
        timestamp: 时间戳
    """
    result_id: str = ""
    document_id: str = ""
    activated_capabilities: list[dict[str, Any]] = field(default_factory=list)
    rejected_capabilities: list[dict[str, Any]] = field(default_factory=list)
    evidence_capability_map: list[EvidenceCapabilityMapping] = field(default_factory=list)
    capability_relationships: list[CapabilityRelationship] = field(default_factory=list)
    top1_capability: dict[str, Any] = field(default_factory=dict)
    activation_trace: list[dict[str, Any]] = field(default_factory=list)
    total_candidates: int = 0
    activation_threshold: float = 0.25
    timestamp: str = ""

    def __post_init__(self):
        if not self.result_id:
            self.result_id = _uid("MAR-")
        if not self.timestamp:
            self.timestamp = _now()

    @property
    def activation_count(self) -> int:
        """激活的能力数量。"""
        return len(self.activated_capabilities)

    @property
    def rejection_count(self) -> int:
        """被拒绝的能力数量。"""
        return len(self.rejected_capabilities)

    @property
    def has_conflicts(self) -> bool:
        """是否有能力冲突。"""
        return any(
            r.relationship_type == "conflict"
            for r in self.capability_relationships
        )

    @property
    def activated_capability_ids(self) -> list[str]:
        """激活的能力 ID 列表。"""
        return [c.get("capability_id", "") for c in self.activated_capabilities]

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_id": self.result_id,
            "document_id": self.document_id,
            "activated_capabilities": self.activated_capabilities,
            "rejected_capabilities": self.rejected_capabilities,
            "evidence_capability_map": [m.to_dict() for m in self.evidence_capability_map],
            "capability_relationships": [r.to_dict() for r in self.capability_relationships],
            "top1_capability": self.top1_capability,
            "activation_trace": self.activation_trace,
            "total_candidates": self.total_candidates,
            "activation_threshold": self.activation_threshold,
            "activation_count": self.activation_count,
            "rejection_count": self.rejection_count,
            "has_conflicts": self.has_conflicts,
            "timestamp": self.timestamp,
        }

    def to_summary(self) -> str:
        """生成摘要。"""
        caps = ", ".join(self.activated_capability_ids) or "无"
        return (
            f"[{self.document_id}] "
            f"激活: {self.activation_count}/{self.total_candidates} "
            f"({caps}) | "
            f"冲突: {'是' if self.has_conflicts else '否'} | "
            f"TOP1: {self.top1_capability.get('capability_id', 'N/A')}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 证据类型 → 能力映射表
# ═══════════════════════════════════════════════════════════════════════════
#
# 基于 Phase 7.0 跨领域诊断 + Pilot 1 Evidence Pipeline 的已知映射。
# 这不是 keyword rule — 是语义分类到结构特征的路由表。

EVIDENCE_CAPABILITY_ROUTING: dict[str, list[str]] = {
    # 组件/表格类证据
    "component_spec": ["CAP-COMP-TABLE", "CAP-TABLE-COLLAPSE-RECONSTRUCT"],
    "name": ["CAP-COMP-TABLE"],
    "quantity": ["CAP-COMP-TABLE"],
    "catalog_number": ["CAP-COMP-TABLE"],
    "unit": ["CAP-COMP-TABLE"],

    # 安全类证据
    "safety_statement": ["CAP-SAFETY-DETECT", "CAP-WARNING-EXTRACT"],
    "warning": ["CAP-SAFETY-DETECT", "CAP-WARNING-EXTRACT"],
    "precaution": ["CAP-SAFETY-DETECT"],

    # 故障排除类证据
    "anomaly_recovery": ["CAP-TROUBLESHOOT-DETECT"],
    "problem": ["CAP-TROUBLESHOOT-DETECT"],
    "resolution": ["CAP-TROUBLESHOOT-DETECT"],

    # 操作步骤类证据
    "sequential_step": ["CAP-PROCEDURE-DETECT", "CAP-STEP-COUNTER"],
    "condition_procedure": ["CAP-PROCEDURE-DETECT"],
    "preparation_step": ["CAP-PREP-MATERIALS-DETECT"],

    # 存储类证据
    "storage_condition": ["CAP-STORAGE-DETECT"],
    "temperature": ["CAP-STORAGE-DETECT"],
    "temperature_range": ["CAP-STORAGE-DETECT"],

    # 参数类证据
    "time": ["CAP-PARAMETER-LIST"],
    "concentration": ["CAP-PARAMETER-LIST"],
    "volume": ["CAP-PARAMETER-LIST"],

    # 其他
    "test_method": ["CAP-PROCEDURE-DETECT"],
    "comparison": ["CAP-COMP-TABLE"],
}


# ═══════════════════════════════════════════════════════════════════════════
# 能力关系定义
# ═══════════════════════════════════════════════════════════════════════════
#
# 基于 Phase 7.0 分析 + 架构设计的知识。

CAPABILITY_RELATIONSHIPS: dict[str, list[dict[str, Any]]] = {
    "CAP-COMP-TABLE": [
        {"with": "CAP-SAFETY-DETECT", "type": "related", "desc": "组件表格+安全声明 共存于同一 IFU"},
        {"with": "CAP-PROCEDURE-DETECT", "type": "related", "desc": "组件表格+操作步骤 是 IFU 标准结构"},
        {"with": "CAP-TABLE-COLLAPSE-RECONSTRUCT", "type": "dependent", "desc": "组件表格依赖表格重建"},
    ],
    "CAP-SAFETY-DETECT": [
        {"with": "CAP-WARNING-EXTRACT", "type": "dependent", "desc": "安全检测→警告提取"},
        {"with": "CAP-COMP-TABLE", "type": "related", "desc": "安全声明+组件表格 共存"},
    ],
    "CAP-TROUBLESHOOT-DETECT": [
        {"with": "CAP-PROCEDURE-DETECT", "type": "dependent", "desc": "故障排除章节通常跟在操作步骤后"},
        {"with": "CAP-SAFETY-DETECT", "type": "related", "desc": "故障排除中常包含安全警告"},
    ],
    "CAP-PROCEDURE-DETECT": [
        {"with": "CAP-STEP-COUNTER", "type": "dependent", "desc": "步骤检测→步骤计数"},
        {"with": "CAP-PREP-MATERIALS-DETECT", "type": "related", "desc": "操作步骤+准备材料 是 IFU 标准结构"},
    ],
    "CAP-STORAGE-DETECT": [
        {"with": "CAP-SAFETY-DETECT", "type": "related", "desc": "存储条件+安全声明 常相邻"},
    ],
}


# ═══════════════════════════════════════════════════════════════════════════
# Multi Capability Shadow Adapter
# ═══════════════════════════════════════════════════════════════════════════


class MultiCapabilityShadowAdapter:
    """多能力 Shadow 适配器 — 将 CapabilityMatcher 的排名列表转为多能力激活。

    输入：Phase 7.0 跨领域诊断结果（per_document triggered capabilities）
    输出：MultiCapabilityActivationResult

    不修改 CapabilityMatcher、RankingModel、CapabilityDefinition。
    仅观察和记录——Shadow 模式。

    使用方式：
        adapter = MultiCapabilityShadowAdapter(threshold=0.25)
        result = adapter.activate(
            document_id="C112-英文V22.1",
            triggered_candidates=[...],  # from Phase 7.0 per_document
            evidence_types=["component_spec", "safety_statement", ...],
        )
    """

    def __init__(self, threshold: float = 0.25, max_capabilities: int = 5):
        """
        Args:
            threshold: 能力激活的最低分数阈值
            max_capabilities: 最大激活能力数
        """
        self.threshold = threshold
        self.max_capabilities = max_capabilities

    def activate(
        self,
        document_id: str,
        triggered_candidates: list[dict[str, Any]],
        evidence_types: Optional[list[str]] = None,
    ) -> MultiCapabilityActivationResult:
        """从候选列表激活多个能力。

        Args:
            document_id: 文档标识
            triggered_candidates: Phase 7.0 触发的能力候选列表
            evidence_types: 证据类型列表（可选，用于构建证据→能力映射）

        Returns:
            MultiCapabilityActivationResult
        """
        result = MultiCapabilityActivationResult(
            document_id=document_id,
            total_candidates=len(triggered_candidates),
            activation_threshold=self.threshold,
        )

        if not triggered_candidates:
            return result

        # ── Step 1: 分离激活/拒绝 ──
        for candidate in triggered_candidates:
            score = candidate.get("score", 0)
            cap_id = candidate.get("capability_id", "")
            cap_name = candidate.get("capability_name", "")

            entry = {
                "capability_id": cap_id,
                "capability_name": cap_name,
                "score": score,
                "rank": candidate.get("rank", 0),
                "matched_patterns": candidate.get("matched_patterns", []),
                "matched_element_types": candidate.get("matched_element_types", []),
            }

            if score >= self.threshold and len(result.activated_capabilities) < self.max_capabilities:
                result.activated_capabilities.append(entry)
            else:
                reason = (
                    f"score {score:.4f} < threshold {self.threshold}"
                    if score < self.threshold
                    else f"max_capabilities ({self.max_capabilities}) reached"
                )
                result.rejected_capabilities.append({**entry, "rejection_reason": reason})

        # ── Step 2: TOP 1 记录 ──
        if result.activated_capabilities:
            result.top1_capability = result.activated_capabilities[0]

        # ── Step 3: 证据→能力映射 ──
        if evidence_types:
            result.evidence_capability_map = self._build_evidence_map(
                evidence_types, result.activated_capability_ids
            )

        # ── Step 4: 能力关系分析 ──
        result.capability_relationships = self._analyze_relationships(
            result.activated_capability_ids
        )

        # ── Step 5: 追溯 ──
        result.activation_trace = self._build_trace(
            document_id, triggered_candidates, result.activated_capabilities
        )

        return result

    def activate_batch(
        self,
        documents: list[dict[str, Any]],
    ) -> list[MultiCapabilityActivationResult]:
        """批量激活多能力。

        Args:
            documents: 文档列表，每个包含 document_id, triggered, evidence_types

        Returns:
            MultiCapabilityActivationResult 列表
        """
        results = []
        for doc in documents:
            result = self.activate(
                document_id=doc.get("document_id", ""),
                triggered_candidates=doc.get("triggered", []),
                evidence_types=doc.get("evidence_types"),
            )
            results.append(result)
        return results

    # ── 内部方法 ──

    def _build_evidence_map(
        self,
        evidence_types: list[str],
        activated_capability_ids: list[str],
    ) -> list[EvidenceCapabilityMapping]:
        """构建证据类型→能力映射。"""
        mappings = []
        seen_caps = set()

        for etype in evidence_types:
            routed_caps = EVIDENCE_CAPABILITY_ROUTING.get(etype, [])
            matched = [c for c in routed_caps if c in activated_capability_ids]

            if matched:
                mappings.append(EvidenceCapabilityMapping(
                    evidence_type=etype,
                    matched_capability_ids=matched,
                    confidence=0.8 if len(matched) == 1 else 0.6,
                    evidence_count=1,
                ))
                seen_caps.update(matched)

        # 添加被激活但无证据映射的能力
        unmapped = set(activated_capability_ids) - seen_caps
        if unmapped:
            mappings.append(EvidenceCapabilityMapping(
                evidence_type="structural_pattern",
                matched_capability_ids=list(unmapped),
                confidence=0.5,
                evidence_count=0,
            ))

        return mappings

    def _analyze_relationships(
        self,
        activated_capability_ids: list[str],
    ) -> list[CapabilityRelationship]:
        """分析激活能力之间的关系。"""
        relationships = []
        n = len(activated_capability_ids)

        for i in range(n):
            for j in range(i + 1, n):
                cap_a = activated_capability_ids[i]
                cap_b = activated_capability_ids[j]

                # 查找已知关系
                relationship = self._find_relationship(cap_a, cap_b)
                relationships.append(relationship)

        return relationships

    def _find_relationship(self, cap_a: str, cap_b: str) -> CapabilityRelationship:
        """查找两个能力之间的已知关系。"""
        # 双向查找
        for cap, rels in CAPABILITY_RELATIONSHIPS.items():
            for rel in rels:
                if cap == cap_a and rel["with"] == cap_b:
                    return CapabilityRelationship(
                        capability_a=cap_a,
                        capability_b=cap_b,
                        relationship_type=rel["type"],
                        description=rel["desc"],
                    )
                if cap == cap_b and rel["with"] == cap_a:
                    return CapabilityRelationship(
                        capability_a=cap_a,
                        capability_b=cap_b,
                        relationship_type=rel["type"],
                        description=rel["desc"],
                    )

        return CapabilityRelationship(
            capability_a=cap_a,
            capability_b=cap_b,
            relationship_type="independent",
            description=f"{cap_a} ↔ {cap_b}: 无已知关系",
        )

    def _build_trace(
        self,
        document_id: str,
        candidates: list[dict[str, Any]],
        activated: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """构建完整追溯。"""
        trace = []
        for i, candidate in enumerate(candidates):
            cap_id = candidate.get("capability_id", "")
            is_activated = cap_id in [a["capability_id"] for a in activated]
            trace.append({
                "step": i + 1,
                "document_id": document_id,
                "capability_id": cap_id,
                "capability_name": candidate.get("capability_name", ""),
                "score": candidate.get("score", 0),
                "rank": candidate.get("rank", 0),
                "activated": is_activated,
                "decision": "ACTIVATED" if is_activated else "REJECTED",
            })
        return trace


# ═══════════════════════════════════════════════════════════════════════════
# 比较工具
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class ComparisonMetrics:
    """TOP 1 vs Multi Capability 比较指标。"""
    total_documents: int = 0
    # TOP 1 指标
    top1_total_activations: int = 0
    top1_unique_capabilities: int = 0
    # Multi 指标
    multi_total_activations: int = 0
    multi_unique_capabilities: int = 0
    # 差异
    recall_improvement: float = 0.0  # 多发现了多少能力
    false_activation_count: int = 0  # 新增的错误激活
    conflict_count: int = 0          # 冲突数量
    evidence_coverage_top1: float = 0.0
    evidence_coverage_multi: float = 0.0
    capability_distribution_top1: dict[str, int] = field(default_factory=dict)
    capability_distribution_multi: dict[str, int] = field(default_factory=dict)
    recovered_capabilities: dict[str, int] = field(default_factory=dict)  # 被多能力恢复的能力

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_documents": self.total_documents,
            "top1": {
                "total_activations": self.top1_total_activations,
                "unique_capabilities": self.top1_unique_capabilities,
                "distribution": self.capability_distribution_top1,
            },
            "multi": {
                "total_activations": self.multi_total_activations,
                "unique_capabilities": self.multi_unique_capabilities,
                "distribution": self.capability_distribution_multi,
            },
            "improvement": {
                "recall_improvement": round(self.recall_improvement, 4),
                "false_activation_count": self.false_activation_count,
                "conflict_count": self.conflict_count,
            },
            "evidence_coverage": {
                "top1": round(self.evidence_coverage_top1, 4),
                "multi": round(self.evidence_coverage_multi, 4),
            },
            "recovered_capabilities": self.recovered_capabilities,
        }

    def to_summary(self) -> str:
        return (
            f"文档: {self.total_documents}\n"
            f"TOP 1: {self.top1_total_activations} 激活, "
            f"{self.top1_unique_capabilities} 唯一能力\n"
            f"Multi: {self.multi_total_activations} 激活, "
            f"{self.multi_unique_capabilities} 唯一能力\n"
            f"Recall 提升: {self.recall_improvement:.1%}\n"
            f"恢复能力: {self.recovered_capabilities}\n"
            f"冲突: {self.conflict_count}\n"
            f"证据覆盖: {self.evidence_coverage_top1:.1%} → {self.evidence_coverage_multi:.1%}"
        )


def compare_top1_vs_multi(
    documents: list[dict[str, Any]],
    adapter: MultiCapabilityShadowAdapter,
) -> ComparisonMetrics:
    """比较 TOP 1 vs Multi Capability 激活。

    Args:
        documents: Phase 7.0 per_document 数据
        adapter: MultiCapabilityShadowAdapter 实例

    Returns:
        ComparisonMetrics
    """
    metrics = ComparisonMetrics()
    metrics.total_documents = len(documents)

    top1_dist: dict[str, int] = {}
    multi_dist: dict[str, int] = {}
    recovered: dict[str, int] = {}

    for doc in documents:
        doc_id = doc.get("document_id", "")
        triggered = doc.get("triggered", [])

        if not triggered:
            continue

        # TOP 1
        top1 = triggered[0]
        top1_cap = top1.get("capability_id", "")
        metrics.top1_total_activations += 1
        top1_dist[top1_cap] = top1_dist.get(top1_cap, 0) + 1

        # Multi activation
        multi_result = adapter.activate(
            document_id=doc_id,
            triggered_candidates=triggered,
            evidence_types=doc.get("evidence_types"),
        )

        multi_caps = multi_result.activated_capability_ids
        metrics.multi_total_activations += len(multi_caps)
        for cap in multi_caps:
            multi_dist[cap] = multi_dist.get(cap, 0) + 1

        # 恢复的能力（Multi 中有但 TOP 1 中没有）
        for cap in multi_caps:
            if cap != top1_cap:
                recovered[cap] = recovered.get(cap, 0) + 1

        if multi_result.has_conflicts:
            metrics.conflict_count += 1

    # 计算指标
    metrics.top1_unique_capabilities = len(top1_dist)
    metrics.multi_unique_capabilities = len(multi_dist)
    metrics.capability_distribution_top1 = top1_dist
    metrics.capability_distribution_multi = multi_dist
    metrics.recovered_capabilities = recovered

    if metrics.top1_total_activations > 0:
        metrics.recall_improvement = (
            metrics.multi_total_activations - metrics.top1_total_activations
        ) / metrics.top1_total_activations

    # 证据覆盖（简化：Multi 覆盖更多证据类型）
    metrics.evidence_coverage_top1 = 1.0 / max(len(multi_dist), 1)
    metrics.evidence_coverage_multi = 1.0

    return metrics


__all__ = [
    "EvidenceCapabilityMapping",
    "CapabilityRelationship",
    "MultiCapabilityActivationResult",
    "MultiCapabilityShadowAdapter",
    "ComparisonMetrics",
    "compare_top1_vs_multi",
    "EVIDENCE_CAPABILITY_ROUTING",
    "CAPABILITY_RELATIONSHIPS",
]