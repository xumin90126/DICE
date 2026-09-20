"""
Phase 2.3: Experience Injection — Enhance Capability through historical success.

Key principle: Capability grows through EXPERIENCE, not RULE ACCUMULATION.

Allowed knowledge targets:
    ✅ Pattern Library      — new detection patterns from structural analysis
    ✅ Evidence Vocabulary  — new vocabulary entries from semantic mining
    ✅ Capability Knowledge — updated scope, confidence, metadata

Forbidden:
    ❌ New doc_class rules
    ❌ New if-else conditions
    ❌ Hardcoded mappings
"""

from dice.runtime.experience.importer import (
    ExperienceCase,
    ExperienceImporter,
    import_experience_cases,
)
from dice.runtime.experience.miner import (
    EvidencePattern,
    RecognitionPattern,
    FailureContrast,
    MiningResult,
    ExperienceMiner,
)
from dice.runtime.experience.injector import (
    KnowledgeInjector,
    InjectionResult,
    inject_experience,
)
from dice.runtime.experience.execution_models import (
    ExecutionExperience,
    ExecutionResult,
)
from dice.runtime.experience.feedback_loop import (
    EnhancementSignal,
    HealthReport,
    EvolutionProposal,
    ExperienceGraph,
    GraphWriteResult,
    FeedbackLoop,
    FeedbackResult,
)

__all__ = [
    # Phase 2.3: Experience Injection
    "ExperienceCase", "ExperienceImporter", "import_experience_cases",
    "EvidencePattern", "RecognitionPattern", "FailureContrast",
    "MiningResult", "ExperienceMiner",
    "KnowledgeInjector", "InjectionResult", "inject_experience",
    # Phase 4.2: Execution Feedback
    "ExecutionExperience", "ExecutionResult",
    # Phase 4.3: Feedback Loop
    "EnhancementSignal", "HealthReport", "EvolutionProposal",
    "ExperienceGraph", "GraphWriteResult",
    "FeedbackLoop", "FeedbackResult",
]
