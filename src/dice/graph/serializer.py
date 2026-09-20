"""
YAML serializer for the Experience Graph.

Supports bidirectional conversion:
    ExperienceGraph ↔ dict ↔ YAML file
"""

from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any, Optional

from dice.graph.experience_graph import ExperienceGraph
from dice.graph.nodes import (
    Observation, Evidence, Pattern, CapabilityCandidate,
    Capability, Implementation, Rule, Evolution, Fix,
    PatternStatus, CapabilityStatus, ConfidenceLevel,
)
from dice.graph.edges import Edge, EdgeType


class GraphSerializer:
    """Serialize/deserialize ExperienceGraph to/from YAML."""

    @staticmethod
    def to_yaml(graph: ExperienceGraph, path: Optional[str] = None) -> str:
        """Serialize graph to YAML string or file."""
        data = graph.to_dict()
        yaml_str = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
        if path:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(yaml_str)
        return yaml_str

    @staticmethod
    def from_yaml(path: str) -> ExperienceGraph:
        """Deserialize graph from YAML file."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return GraphSerializer.from_dict(data)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> ExperienceGraph:
        """Reconstruct ExperienceGraph from dict."""
        graph = ExperienceGraph(
            name=data.get("meta", {}).get("name", "experience_graph"),
            version=data.get("meta", {}).get("version", "1.0"),
        )

        nodes = data.get("nodes", {})

        # Reconstruct nodes
        for obs_data in nodes.get("observations", []):
            obs = Observation(
                id=obs_data["id"],
                phenomenon=obs_data.get("phenomenon", ""),
                timestamp=obs_data.get("timestamp", ""),
            )
            graph.add_observation(obs)

        for evd_data in nodes.get("evidences", []):
            evd = Evidence(
                id=evd_data["id"],
                observation_ids=evd_data.get("observation_ids", []),
                pattern_id=evd_data.get("pattern_id", ""),
                phenomenon=evd_data.get("phenomenon", ""),
                source_document=evd_data.get("source_document", ""),
                source_slice=evd_data.get("source_slice", ""),
                evidence_strength=evd_data.get("evidence_strength", 0.0),
                is_confirmed=evd_data.get("is_confirmed", True),
            )
            graph.add_evidence(evd)

        for pat_data in nodes.get("patterns", []):
            pat = Pattern(
                id=pat_data["id"],
                name=pat_data.get("name", ""),
                description=pat_data.get("description", ""),
                detection_signals=pat_data.get("detection_signals", []),
                structural_indicators=pat_data.get("structural_indicators", []),
                content_indicators=pat_data.get("content_indicators", []),
                status=PatternStatus(pat_data.get("status", "candidate")),
                confidence=pat_data.get("confidence", 0.0),
                evidence_count=pat_data.get("evidence_count", 0),
                evidence_ids=pat_data.get("evidence_ids", []),
                source_documents=pat_data.get("source_documents", []),
            )
            graph.add_pattern(pat)

        for cand_data in nodes.get("candidates", []):
            cand = CapabilityCandidate(
                id=cand_data["id"],
                name=cand_data.get("name", ""),
                pattern_ids=cand_data.get("pattern_ids", []),
                verification_score=cand_data.get("verification_score", 0.0),
            )
            graph.add_candidate(cand)

        for cap_data in nodes.get("capabilities", []):
            cap = Capability(
                id=cap_data["id"],
                name=cap_data.get("name", ""),
                layer=cap_data.get("layer", "chapter_handler"),
                status=CapabilityStatus(cap_data.get("status", "proposed")),
                maturity=ConfidenceLevel(cap_data.get("maturity", "low")),
                maturity_score=cap_data.get("maturity_score", 0.0),
                version=cap_data.get("version", 1),
                pattern_ids=cap_data.get("pattern_ids", []),
                documents_tested=cap_data.get("documents_tested", []),
                cross_doc_success_rate=cap_data.get("cross_doc_success_rate", 0.0),
            )
            graph.add_capability(cap)

        for impl_data in nodes.get("implementations", []):
            impl = Implementation(
                id=impl_data["id"],
                capability_id=impl_data.get("capability_id", ""),
                name=impl_data.get("name", ""),
                strategy=impl_data.get("strategy", ""),
                config=impl_data.get("config", {}),
                rule_ids=impl_data.get("rule_ids", []),
            )
            graph.add_implementation(impl)

        for rule_data in nodes.get("rules", []):
            rule = Rule(
                id=rule_data["id"],
                implementation_id=rule_data.get("implementation_id", ""),
                name=rule_data.get("name", ""),
                rule_type=rule_data.get("rule_type", ""),
                pattern=rule_data.get("pattern", ""),
            )
            graph.add_rule(rule)

        for evo_data in nodes.get("evolutions", []):
            evo = Evolution(
                id=evo_data["id"],
                capability_id=evo_data.get("capability_id", ""),
                from_version=evo_data.get("from_version", 0),
                to_version=evo_data.get("to_version", 0),
                change_type=evo_data.get("change_type", ""),
            )
            graph.add_evolution(evo)

        for fix_data in nodes.get("fixes", []):
            fix = Fix(
                id=fix_data["id"],
                target=fix_data.get("target", ""),
                old_value=fix_data.get("old_value", ""),
                new_value=fix_data.get("new_value", ""),
            )
            graph.add_fix(fix)

        # Reconstruct edges
        for edge_data in data.get("edges", []):
            edge = Edge(
                id=edge_data.get("id", ""),
                source_id=edge_data["source_id"],
                target_id=edge_data["target_id"],
                edge_type=EdgeType(edge_data["edge_type"]),
                source_type=edge_data.get("source_type", ""),
                target_type=edge_data.get("target_type", ""),
                weight=edge_data.get("weight", 1.0),
            )
            graph.add_edge(edge)

        return graph
