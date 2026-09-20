"""
DICE Runtime package — Capability execution, evaluation, and comparison.

Phase 3.2: Pattern Discovery Pipeline.
    Execution Experience → Pattern Candidate Generator → Pattern Candidates.
Phase 3.0: Three-Layer Unified Execution Chain.
    L1 Structure Detection → L2 Semantic Evidence → L3 Structure Extraction.
Phase 2.3+: Includes Experience Injection for self-evolving capabilities.
"""

from dice.runtime.result import CapabilityResult, EvidenceItem
from dice.runtime.capability_registry import register_components_table_capability
from dice.runtime.selector import CapabilitySelector, SelectionResult
from dice.runtime.executor import CapabilityExecutor
from dice.runtime.evaluator import CapabilityEvaluator, CapabilityEvaluationReport
from dice.runtime.comparison import LegacyComparison, ComparisonReport, ComparisonRow
from dice.runtime.layers import (
    ThreeLayerRuntime, LayerTrace, LayerResult,
    StructureDetector, SemanticEvidenceLayer, StructureExtractor,
    create_runtime,
)
from dice.runtime.experience import (
    ExperienceCase, ExperienceImporter,
    EvidencePattern, RecognitionPattern, FailureContrast,
    MiningResult, ExperienceMiner,
    KnowledgeInjector, InjectionResult,
)
from dice.runtime.pattern_discovery import (
    PatternCandidate, CapabilityCandidate, DiscoveryReport,
    PatternCandidateGenerator, ExecutionExperience,
    StructureSignature, StructuralElement, StructuralRelation,
    discover_patterns,
)
from dice.runtime.promotion import (
    PromotionState, PatternEvaluator, PatternEvaluation,
    CapabilityPromoter, PromotionResult, PromotionGateResult,
    RegressionGuard, PromotionReport, run_promotion_pipeline,
)

__all__ = [
    "CapabilityResult", "EvidenceItem",
    "register_components_table_capability",
    "CapabilitySelector", "SelectionResult",
    "CapabilityExecutor",
    "CapabilityEvaluator", "CapabilityEvaluationReport",
    "LegacyComparison", "ComparisonReport", "ComparisonRow",
    # Three-Layer Runtime (Phase 3.0)
    "ThreeLayerRuntime", "LayerTrace", "LayerResult",
    "StructureDetector", "SemanticEvidenceLayer", "StructureExtractor",
    "create_runtime",
    # Experience Injection (Phase 2.3)
    "ExperienceCase", "ExperienceImporter",
    "EvidencePattern", "RecognitionPattern", "FailureContrast",
    "MiningResult", "ExperienceMiner",
    "KnowledgeInjector", "InjectionResult",
    # Pattern Discovery (Phase 3.2)
    "PatternCandidate", "CapabilityCandidate", "DiscoveryReport",
    "PatternCandidateGenerator", "ExecutionExperience",
    "StructureSignature", "StructuralElement", "StructuralRelation",
    "discover_patterns",
    # Capability Promotion (Phase 3.3)
    "PromotionState", "PatternEvaluator", "PatternEvaluation",
    "CapabilityPromoter", "PromotionResult", "PromotionGateResult",
    "RegressionGuard", "PromotionReport", "run_promotion_pipeline",
]
