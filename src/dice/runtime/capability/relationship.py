"""
Capability Relationship Graph — Phase 5.

描述 Capability 之间的关系：互补、冲突、依赖、独立。

关系类型：
    - related: 两个能力互补，常共存于同一文档
    - conflict: 两个能力可能对同一证据产生冲突输出
    - dependent: 能力 A 的激活依赖于能力 B
    - independent: 无已知关系

使用方式：
    graph = CapabilityRelationshipGraph()
    rel = graph.get_relationship("CAP-COMP-TABLE", "CAP-SAFETY-DETECT")
    # → CapabilityRelation(type="related", desc="...")
    graph.get_related("CAP-COMP-TABLE")
    # → ["CAP-SAFETY-DETECT", "CAP-PROCEDURE-DETECT", ...]
    graph.get_conflicts(["CAP-SAFETY-DETECT", "CAP-STORAGE-DETECT"])
    # → [] (无冲突)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# ═══════════════════════════════════════════════════════════════════════════
# 枚举
# ═══════════════════════════════════════════════════════════════════════════


class RelationType(str, Enum):
    """能力关系类型。"""
    RELATED = "related"          # 互补关系
    CONFLICT = "conflict"        # 冲突关系
    DEPENDENT = "dependent"      # 依赖关系
    INDEPENDENT = "independent"  # 独立关系


# ═══════════════════════════════════════════════════════════════════════════
# 数据模型
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class CapabilityRelation:
    """能力关系。

    Fields:
        source: 源能力 ID
        target: 目标能力 ID
        relation_type: 关系类型
        description: 关系描述
        strength: 关系强度 (0.0-1.0)
        bidirectional: 是否为双向关系
    """
    source: str = ""
    target: str = ""
    relation_type: RelationType = RelationType.INDEPENDENT
    description: str = ""
    strength: float = 0.5
    bidirectional: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "relation_type": self.relation_type.value,
            "description": self.description,
            "strength": self.strength,
            "bidirectional": self.bidirectional,
        }


@dataclass
class CapabilityCluster:
    """能力簇——一组紧密关联的能力。

    Fields:
        cluster_id: 簇 ID
        capability_ids: 簇内能力 ID 列表
        cluster_type: 簇类型（structural / semantic / procedural）
        description: 簇描述
    """
    cluster_id: str = ""
    capability_ids: list[str] = field(default_factory=list)
    cluster_type: str = ""  # structural / semantic / procedural
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "cluster_id": self.cluster_id,
            "capability_ids": self.capability_ids,
            "cluster_type": self.cluster_type,
            "description": self.description,
        }


# ═══════════════════════════════════════════════════════════════════════════
# 关系图定义
# ═══════════════════════════════════════════════════════════════════════════
#
# 基于 Phase 7.0 跨领域分析 + Phase 4 试运行发现。

RELATIONSHIP_DEFINITIONS: list[CapabilityRelation] = [
    # ── 组件表格簇 ──
    CapabilityRelation(
        source="CAP-COMP-TABLE",
        target="CAP-TABLE-COLLAPSE-RECONSTRUCT",
        relation_type=RelationType.DEPENDENT,
        description="组件表格理解依赖表格重建",
        strength=0.9,
    ),
    CapabilityRelation(
        source="CAP-COMP-TABLE",
        target="CAP-ANCHOR-EXTRACT",
        relation_type=RelationType.DEPENDENT,
        description="组件表格依赖锚点提取来定位",
        strength=0.7,
    ),

    # ── 安全/警告簇 ──
    CapabilityRelation(
        source="CAP-SAFETY-DETECT",
        target="CAP-WARNING-EXTRACT",
        relation_type=RelationType.DEPENDENT,
        description="安全检测→警告短语提取",
        strength=0.9,
    ),

    # ── 操作步骤簇 ──
    CapabilityRelation(
        source="CAP-PROCEDURE-DETECT",
        target="CAP-STEP-COUNTER",
        relation_type=RelationType.DEPENDENT,
        description="步骤检测→步骤计数",
        strength=0.85,
    ),
    CapabilityRelation(
        source="CAP-PROCEDURE-DETECT",
        target="CAP-PREP-MATERIALS-DETECT",
        relation_type=RelationType.RELATED,
        description="操作步骤+准备材料 是 IFU 标准结构",
        strength=0.7,
    ),
    CapabilityRelation(
        source="CAP-PROCEDURE-DETECT",
        target="CAP-TROUBLESHOOT-DETECT",
        relation_type=RelationType.RELATED,
        description="故障排除章节通常跟在操作步骤后",
        strength=0.6,
    ),

    # ── 跨簇互补关系 ──
    CapabilityRelation(
        source="CAP-COMP-TABLE",
        target="CAP-SAFETY-DETECT",
        relation_type=RelationType.RELATED,
        description="组件表格+安全声明 共存于同一 IFU",
        strength=0.7,
    ),
    CapabilityRelation(
        source="CAP-COMP-TABLE",
        target="CAP-PROCEDURE-DETECT",
        relation_type=RelationType.RELATED,
        description="组件表格+操作步骤 是 IFU 标准结构",
        strength=0.8,
    ),
    CapabilityRelation(
        source="CAP-COMP-TABLE",
        target="CAP-STORAGE-DETECT",
        relation_type=RelationType.RELATED,
        description="组件表格+存储条件 共存于 IFU",
        strength=0.6,
    ),
    CapabilityRelation(
        source="CAP-SAFETY-DETECT",
        target="CAP-STORAGE-DETECT",
        relation_type=RelationType.RELATED,
        description="安全声明+存储条件 常相邻",
        strength=0.6,
    ),
    CapabilityRelation(
        source="CAP-SAFETY-DETECT",
        target="CAP-TROUBLESHOOT-DETECT",
        relation_type=RelationType.RELATED,
        description="故障排除中常包含安全警告",
        strength=0.5,
    ),
    CapabilityRelation(
        source="CAP-TROUBLESHOOT-DETECT",
        target="CAP-PROCEDURE-DETECT",
        relation_type=RelationType.DEPENDENT,
        description="故障排除依赖操作步骤检测作为上下文",
        strength=0.5,
    ),

    # ── 参数簇 ──
    CapabilityRelation(
        source="CAP-PARAMETER-LIST",
        target="CAP-COMP-TABLE",
        relation_type=RelationType.RELATED,
        description="参数列表+组件表格 共享数值数据",
        strength=0.5,
    ),
]

# 能力簇定义
CAPABILITY_CLUSTERS: list[CapabilityCluster] = [
    CapabilityCluster(
        cluster_id="CLUSTER-COMPONENTS",
        capability_ids=["CAP-COMP-TABLE", "CAP-TABLE-COLLAPSE-RECONSTRUCT", "CAP-ANCHOR-EXTRACT"],
        cluster_type="structural",
        description="组件表格簇：表格检测→重建→锚点提取",
    ),
    CapabilityCluster(
        cluster_id="CLUSTER-SAFETY",
        capability_ids=["CAP-SAFETY-DETECT", "CAP-WARNING-EXTRACT"],
        cluster_type="semantic",
        description="安全检测簇：安全声明检测→警告提取",
    ),
    CapabilityCluster(
        cluster_id="CLUSTER-PROCEDURE",
        capability_ids=["CAP-PROCEDURE-DETECT", "CAP-STEP-COUNTER", "CAP-PREP-MATERIALS-DETECT", "CAP-TROUBLESHOOT-DETECT"],
        cluster_type="procedural",
        description="操作步骤簇：步骤检测→计数→材料准备→故障排除",
    ),
    CapabilityCluster(
        cluster_id="CLUSTER-STORAGE",
        capability_ids=["CAP-STORAGE-DETECT"],
        cluster_type="semantic",
        description="存储条件簇：存储条件检测",
    ),
    CapabilityCluster(
        cluster_id="CLUSTER-PARAMETER",
        capability_ids=["CAP-PARAMETER-LIST"],
        cluster_type="structural",
        description="参数列表簇：参数/数值检测",
    ),
]


# ═══════════════════════════════════════════════════════════════════════════
# CapabilityRelationshipGraph
# ═══════════════════════════════════════════════════════════════════════════


class CapabilityRelationshipGraph:
    """能力关系图 — 查询和管理能力之间的关系。

    使用方式：
        graph = CapabilityRelationshipGraph()
        rel = graph.get_relationship("CAP-COMP-TABLE", "CAP-SAFETY-DETECT")
        related = graph.get_related("CAP-COMP-TABLE")
        conflicts = graph.detect_conflicts(["CAP-SAFETY-DETECT", "CAP-STORAGE-DETECT"])
        cluster = graph.get_cluster("CAP-COMP-TABLE")
    """

    def __init__(self):
        self._relations: dict[str, dict[str, CapabilityRelation]] = {}
        self._clusters: dict[str, CapabilityCluster] = {}

        # 加载预定义关系
        for rel in RELATIONSHIP_DEFINITIONS:
            self._add_relation_internal(rel)

        # 加载预定义簇
        for cluster in CAPABILITY_CLUSTERS:
            self._clusters[cluster.cluster_id] = cluster

    # ── 关系查询 ──

    def get_relationship(self, cap_a: str, cap_b: str) -> CapabilityRelation:
        """获取两个能力之间的关系。"""
        # 双向查找
        if cap_a in self._relations and cap_b in self._relations[cap_a]:
            return self._relations[cap_a][cap_b]
        if cap_b in self._relations and cap_a in self._relations[cap_b]:
            return self._relations[cap_b][cap_a]

        return CapabilityRelation(
            source=cap_a,
            target=cap_b,
            relation_type=RelationType.INDEPENDENT,
            description=f"{cap_a} ↔ {cap_b}: 无已知关系",
        )

    def get_related(self, capability_id: str) -> list[str]:
        """获取与指定能力相关的所有能力 ID。"""
        related = []
        if capability_id in self._relations:
            for target, rel in self._relations[capability_id].items():
                if rel.relation_type in (RelationType.RELATED, RelationType.DEPENDENT):
                    related.append(target)
        # 反向查找
        for source, targets in self._relations.items():
            if source == capability_id:
                continue
            if capability_id in targets:
                rel = targets[capability_id]
                if rel.relation_type in (RelationType.RELATED, RelationType.DEPENDENT):
                    related.append(source)
        return related

    def get_dependencies(self, capability_id: str) -> list[str]:
        """获取指定能力依赖的能力 ID。"""
        deps = []
        if capability_id in self._relations:
            for target, rel in self._relations[capability_id].items():
                if rel.relation_type == RelationType.DEPENDENT and rel.source == capability_id:
                    deps.append(target)
        return deps

    def get_dependents(self, capability_id: str) -> list[str]:
        """获取依赖指定能力的能力 ID。"""
        deps = []
        for source, targets in self._relations.items():
            if capability_id in targets:
                rel = targets[capability_id]
                if rel.relation_type == RelationType.DEPENDENT and rel.source == source:
                    deps.append(source)
        return deps

    # ── 冲突检测 ──

    def detect_conflicts(self, capability_ids: list[str]) -> list[CapabilityRelation]:
        """检测一组能力之间的冲突。"""
        conflicts = []
        for i in range(len(capability_ids)):
            for j in range(i + 1, len(capability_ids)):
                rel = self.get_relationship(capability_ids[i], capability_ids[j])
                if rel.relation_type == RelationType.CONFLICT:
                    conflicts.append(rel)
        return conflicts

    def has_conflicts(self, capability_ids: list[str]) -> bool:
        """检查一组能力是否存在冲突。"""
        return len(self.detect_conflicts(capability_ids)) > 0

    # ── 簇查询 ──

    def get_cluster(self, capability_id: str) -> Optional[CapabilityCluster]:
        """获取能力所属的簇。"""
        for cluster in self._clusters.values():
            if capability_id in cluster.capability_ids:
                return cluster
        return None

    def get_cluster_members(self, cluster_id: str) -> list[str]:
        """获取簇内所有能力 ID。"""
        cluster = self._clusters.get(cluster_id)
        return cluster.capability_ids if cluster else []

    def list_clusters(self) -> list[CapabilityCluster]:
        """列出所有能力簇。"""
        return list(self._clusters.values())

    # ── 批量分析 ──

    def analyze_activation_set(
        self, capability_ids: list[str]
    ) -> dict[str, Any]:
        """分析一组激活能力的完整关系。

        Returns:
            {
                "clusters": 涉及的能力簇,
                "conflicts": 冲突列表,
                "dependencies_met": 依赖是否满足,
                "recommendation": 建议
            }
        """
        result = {
            "capability_ids": capability_ids,
            "clusters": [],
            "conflicts": [],
            "relationships": [],
            "dependencies_met": True,
            "recommendation": "",
        }

        seen_clusters = set()
        for cap_id in capability_ids:
            cluster = self.get_cluster(cap_id)
            if cluster and cluster.cluster_id not in seen_clusters:
                result["clusters"].append(cluster.to_dict())
                seen_clusters.add(cluster.cluster_id)

        result["conflicts"] = [c.to_dict() for c in self.detect_conflicts(capability_ids)]

        # 检查依赖
        for cap_id in capability_ids:
            deps = self.get_dependencies(cap_id)
            for dep in deps:
                if dep not in capability_ids:
                    result["dependencies_met"] = False
                    result["relationships"].append({
                        "type": "unmet_dependency",
                        "capability": cap_id,
                        "depends_on": dep,
                    })

        # 关系列表
        for i in range(len(capability_ids)):
            for j in range(i + 1, len(capability_ids)):
                rel = self.get_relationship(capability_ids[i], capability_ids[j])
                result["relationships"].append(rel.to_dict())

        # 建议
        if result["conflicts"]:
            result["recommendation"] = "存在冲突——需要人工审查"
        elif not result["dependencies_met"]:
            result["recommendation"] = "依赖未满足——建议激活依赖能力"
        else:
            result["recommendation"] = "无冲突，依赖满足——可以安全激活"

        return result

    # ── 内部方法 ──

    def _add_relation_internal(self, rel: CapabilityRelation):
        """添加关系。"""
        if rel.source not in self._relations:
            self._relations[rel.source] = {}
        self._relations[rel.source][rel.target] = rel

        # 双向添加
        if rel.bidirectional:
            if rel.target not in self._relations:
                self._relations[rel.target] = {}
            self._relations[rel.target][rel.source] = CapabilityRelation(
                source=rel.target,
                target=rel.source,
                relation_type=rel.relation_type,
                description=rel.description,
                strength=rel.strength,
                bidirectional=True,
            )

    def add_relation(self, rel: CapabilityRelation):
        """添加自定义关系。"""
        self._add_relation_internal(rel)

    def to_dict(self) -> dict[str, Any]:
        """导出完整关系图。"""
        relations = []
        seen = set()
        for source, targets in self._relations.items():
            for target, rel in targets.items():
                key = tuple(sorted([source, target]))
                if key not in seen:
                    relations.append(rel.to_dict())
                    seen.add(key)

        return {
            "relations": relations,
            "clusters": [c.to_dict() for c in self._clusters.values()],
            "total_relations": len(relations),
            "total_clusters": len(self._clusters),
        }


__all__ = [
    "RelationType",
    "CapabilityRelation",
    "CapabilityCluster",
    "CapabilityRelationshipGraph",
    "RELATIONSHIP_DEFINITIONS",
    "CAPABILITY_CLUSTERS",
]