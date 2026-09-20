"""
Phase 6.6 Human Review Artifact Generator.

Generates human-readable Markdown review files for each EvolutionProposal,
so reviewers can make informed approve/reject decisions without any Web UI
or external platform dependency.

Each artifact includes:
    - Proposal metadata (ID, source, gap_type, timestamp)
    - Evidence summary (all 5 validation metrics)
    - Current capability status (from Registry, if available)
    - Recommended changes (from proposal's recommended_action)
    - Impact prediction (estimated impact, affected documents)
    - Approve/Reject decision fields (for human to fill)

Output path: knowledge/review/{proposal_id}.md

Design principles:
    - READ-ONLY pipeline consumer — never modifies Registry, Capability, or Proposal
    - Self-contained — each file has everything needed for a decision
    - Decision-ready — includes explicit [ ] approve / [ ] reject checkboxes
    - Plain Markdown — no HTML, no JS, readable in any editor
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from dice.evidence_store.models import (
    EvolutionProposal,
    EvidenceSummary,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _format_ts(iso_ts: str) -> str:
    """Format ISO timestamp for human readability."""
    if not iso_ts:
        return "N/A"
    try:
        dt = datetime.fromisoformat(iso_ts)
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except (ValueError, TypeError):
        return iso_ts[:19] if len(iso_ts) >= 19 else iso_ts


# ═══════════════════════════════════════════════════════════════════════════
# Action descriptions for human context
# ═══════════════════════════════════════════════════════════════════════════

ACTION_DESCRIPTIONS: dict[str, str] = {
    "extend_existing_capability_pattern": (
        "Extend an existing capability's pattern matching or extraction rules "
        "to cover the detected variation. This is the lowest-risk action — the "
        "structural pattern is already recognized, only minor adjustments needed."
    ),
    "extend_vocabulary": (
        "Add domain-specific vocabulary terms or parameter constraints to existing "
        "capabilities. The structural detection works, but terminology is missing "
        "from the current vocabulary lists."
    ),
    "add_new_capability_candidate": (
        "Create a new capability candidate for a genuinely underserved domain. "
        "This is the highest-effort action — requires defining scope, patterns, "
        "extraction rules, and validation constraints from scratch."
    ),
    "improve_detector": (
        "Improve the detection pipeline heuristics. Repeated validation failures "
        "suggest the detection logic itself may need tuning before considering "
        "new capabilities."
    ),
}

ACTION_DIFFICULTY: dict[str, str] = {
    "extend_existing_capability_pattern": "🟢 Low",
    "extend_vocabulary": "🟡 Medium",
    "add_new_capability_candidate": "🔴 High",
    "improve_detector": "🟠 Medium-High",
}

ACTION_IMPACT: dict[str, str] = {
    "extend_existing_capability_pattern": "Incremental — expands coverage of existing gaps",
    "extend_vocabulary": "Incremental — improves term recognition for known patterns",
    "add_new_capability_candidate": "Structural — opens new domain coverage",
    "improve_detector": "Foundational — improves detection for all future matches",
}


# ═══════════════════════════════════════════════════════════════════════════
# Review Artifact Generator
# ═══════════════════════════════════════════════════════════════════════════


class ReviewArtifactGenerator:
    """
    Generates human-readable Markdown review files from EvolutionProposals.

    Usage:
        generator = ReviewArtifactGenerator(output_dir="knowledge/review")
        paths = generator.generate(proposals, registry=registry, decisions=decisions)

        for path in paths:
            print(f"Review artifact: {path}")
    """

    def __init__(self, output_dir: str = "knowledge/review"):
        self.output_dir = output_dir

    # ═══════════════════════════════════════════════════════════════════
    # Public API
    # ═══════════════════════════════════════════════════════════════════

    def generate(
        self,
        proposals: list[EvolutionProposal],
        registry: Any = None,
        decisions: Optional[list[Any]] = None,
        candidates: Optional[list[Any]] = None,
    ) -> list[str]:
        """
        Generate review artifacts for a batch of EvolutionProposals.

        Args:
            proposals: EvolutionProposals from ProposalGenerator
            registry: Optional CapabilityRegistry for context
            decisions: Optional EvolutionDecisions for context
            candidates: Optional EvolutionCandidates for context

        Returns:
            List of generated file paths.
        """
        os.makedirs(self.output_dir, exist_ok=True)
        paths: list[str] = []

        for i, proposal in enumerate(proposals):
            path = self._generate_one(proposal, i + 1, registry, decisions, candidates)
            paths.append(path)

        return paths

    def generate_one(
        self,
        proposal: EvolutionProposal,
        registry: Any = None,
        index: int = 1,
    ) -> str:
        """
        Generate a single review artifact.

        Returns the file path.
        """
        os.makedirs(self.output_dir, exist_ok=True)
        return self._generate_one(proposal, index, registry)

    # ═══════════════════════════════════════════════════════════════════
    # Internal: generate a single artifact
    # ═══════════════════════════════════════════════════════════════════

    def _generate_one(
        self,
        proposal: EvolutionProposal,
        index: int = 1,
        registry: Any = None,
        decisions: Optional[list[Any]] = None,
        candidates: Optional[list[Any]] = None,
    ) -> str:
        """Build and write a single Markdown review file."""
        filename = f"{proposal.proposal_id}.md"
        filepath = os.path.join(self.output_dir, filename)

        md = self._build_markdown(proposal, index, registry, decisions, candidates)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md)

        return filepath

    # ═══════════════════════════════════════════════════════════════════
    # Markdown builder
    # ═══════════════════════════════════════════════════════════════════

    def _build_markdown(
        self,
        proposal: EvolutionProposal,
        index: int,
        registry: Any = None,
        decisions: Optional[list[Any]] = None,
        candidates: Optional[list[Any]] = None,
    ) -> str:
        """Assemble the complete Markdown review document."""

        es = proposal.evidence_summary
        if isinstance(es, EvidenceSummary):
            es_dict = es.to_dict()
        elif isinstance(es, dict):
            es_dict = es
        else:
            es_dict = {}

        lines: list[str] = []

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # HEADER
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        decision_emoji = "🔴" if proposal.human_review_status == "pending_review" else "🟢"

        lines.append(f"# {decision_emoji} Review #{index}: {proposal.proposal_id}")
        lines.append("")
        lines.append(f"> **Status**: `{proposal.human_review_status}`")
        lines.append(f"> **Generated**: {_format_ts(proposal.generated_at)}")
        lines.append(f"> **Confidence**: `{proposal.confidence:.2%}`")
        lines.append("")
        lines.append("---")
        lines.append("")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 1. PROPOSAL SUMMARY
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        lines.append("## 1. Proposal Summary")
        lines.append("")
        lines.append("| Field | Value |")
        lines.append("|-------|-------|")
        lines.append(f"| Proposal ID | `{proposal.proposal_id}` |")
        lines.append(f"| Source Candidate | `{proposal.source_candidate_id}` |")
        lines.append(f"| Source Decision | `{proposal.source_decision_id}` |")
        lines.append(f"| Gap Type | `{proposal.gap_type}` |")
        lines.append("")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 2. EVIDENCE SUMMARY
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        lines.append("## 2. Evidence Summary")
        lines.append("")

        freq = es_dict.get("occurrence_frequency", 0)
        spread = es_dict.get("document_spread", 0)
        failures = es_dict.get("repeated_failure_count", 0)
        overlap = es_dict.get("existing_capability_overlap", 0)
        impact = es_dict.get("estimated_impact", 0.0)

        lines.append("| Metric | Value | Interpretation |")
        lines.append("|--------|-------|----------------|")
        lines.append(
            f"| Occurrence Frequency | `{freq}` | "
            f"{self._freq_label(freq)} |"
        )
        lines.append(
            f"| Document Spread | `{spread}` | "
            f"{self._spread_label(spread)} |"
        )
        lines.append(
            f"| Repeated Failures | `{failures}` | "
            f"{self._failure_label(failures)} |"
        )
        lines.append(
            f"| Capability Overlap | `{overlap}` | "
            f"{self._overlap_label(overlap)} |"
        )
        lines.append(
            f"| Estimated Impact | `{impact:.0f}` | "
            f"{self._impact_label(impact)} |"
        )
        lines.append("")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 3. RECOMMENDED ACTION
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        lines.append("## 3. Recommended Action")
        lines.append("")

        action = proposal.recommended_action
        difficulty = ACTION_DIFFICULTY.get(action, "⚪ Unknown")
        impact_desc = ACTION_IMPACT.get(action, "Unknown")
        action_desc = ACTION_DESCRIPTIONS.get(action, "")

        lines.append(f"**Action**: `{action}`")
        lines.append(f"**Difficulty**: {difficulty}")
        lines.append(f"**Scope**: {impact_desc}")
        lines.append("")

        if action_desc:
            lines.append(f"> {action_desc}")
            lines.append("")

        lines.append("### Rationale")
        lines.append("")
        lines.append(proposal.rationale)
        lines.append("")

        # ── Phase 6.10: Review Level (risk-based routing) ──
        review_level = getattr(proposal, "review_level", "HUMAN_REVIEW")
        level_icon = {
            "AUTO_REVIEW": "🟢",
            "HUMAN_REVIEW": "🟡",
            "ARCHITECTURE_REVIEW": "🔴",
        }.get(review_level, "🟡")
        level_desc = {
            "AUTO_REVIEW": "Light-touch review. Low-risk extension of existing capability.",
            "HUMAN_REVIEW": "Standard human review. Moderate scope change (vocabulary/detection).",
            "ARCHITECTURE_REVIEW": "Architecture-level review. New capability or registry impact — needs cross-cutting analysis.",
        }.get(review_level, "Standard human review.")
        lines.append("### Review Level")
        lines.append("")
        lines.append(f"**Level**: {level_icon} `{review_level}`")
        lines.append(f"> {level_desc}")
        lines.append("")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 4. CURRENT CAPABILITY STATUS
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        lines.append("## 4. Current Capability Status")
        lines.append("")

        if registry is not None:
            try:
                active_caps = registry.list_active()
                lines.append(f"**Registry**: `{len(active_caps)}` active capabilities")
                lines.append("")

                if active_caps:
                    lines.append("| Capability | Status | Executions | Maturity |")
                    lines.append("|------------|--------|------------|----------|")
                    for cap in active_caps[:15]:  # top 15 only
                        name = getattr(cap, "name", cap.id) if hasattr(cap, "name") else cap.id
                        status_val = getattr(cap, "status", "?")
                        if hasattr(status_val, "value"):
                            status_val = status_val.value
                        exec_count = getattr(cap, "execution_count", 0)
                        maturity = getattr(cap, "maturity", "?")
                        if hasattr(maturity, "value"):
                            maturity = maturity.value
                        lines.append(
                            f"| `{name[:35]}` | `{str(status_val)[:15]}` | "
                            f"{exec_count} | `{str(maturity)[:12]}` |"
                        )
                    if len(active_caps) > 15:
                        lines.append(f"| ... | ... | ... | ... |")
                        lines.append(f"| _(+{len(active_caps) - 15} more)_ | | | |")
                    lines.append("")
            except Exception as e:
                lines.append(f"> ⚠ Could not query Registry: `{e}`")
                lines.append("")
        else:
            lines.append("> ℹ No Registry provided — capability status unavailable.")
            lines.append("")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 5. IMPACT PREDICTION
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        lines.append("## 5. Impact Prediction")
        lines.append("")

        if action == "add_new_capability_candidate":
            lines.append("**If approved**, a new capability will be registered as a `draft` candidate. ")
            lines.append("This will:")
            lines.append("")
            lines.append("- Increase Registry size by +1")
            lines.append("- Add a new pattern → capability matching path")
            lines.append("- Require extraction rule + validation constraint definition")
            lines.append("- Need ≥3 cross-document verifications before promotion to `beta`")
            lines.append("")
            lines.append("**Risk**: Low — candidate starts as `draft`, no production impact.")
        elif action == "extend_vocabulary":
            lines.append("**If approved**, vocabulary/parameter constraints will be extended ")
            lines.append("on existing capabilities. This will:")
            lines.append("")
            lines.append("- Improve pattern matching for domain-specific terms")
            lines.append("- Potentially increase overlap counts for related patterns")
            lines.append("- May reduce false-negatives in matching pipeline")
            lines.append("")
            lines.append("**Risk**: Very Low — vocabulary extension is additive only.")
        elif action == "extend_existing_capability_pattern":
            lines.append("**If approved**, an existing capability's pattern matching rules ")
            lines.append("will be extended. This will:")
            lines.append("")
            lines.append("- Broaden the capability's detection scope")
            lines.append("- Potentially capture the currently-unmatched signals")
            lines.append("- May require regression testing on covered documents")
            lines.append("")
            lines.append("**Risk**: Low — pattern extension is scoped to one capability.")
        elif action == "improve_detector":
            lines.append("**If approved**, detection pipeline heuristics will be tuned. ")
            lines.append("This will:")
            lines.append("")
            lines.append("- Improve detection accuracy across all capabilities")
            lines.append("- May change match scores for existing patterns")
            lines.append("- Requires full regression testing")
            lines.append("")
            lines.append("**Risk**: Medium — detector changes affect all matching.")

        lines.append("")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 6. HUMAN DECISION
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        lines.append("## 6. Human Decision")
        lines.append("")
        lines.append("> ⚠ **Action Required**: Review the evidence above and select one option.")
        lines.append("> Check the appropriate box and save this file. The system will process")
        lines.append("> your decision in the next evolution cycle.")
        lines.append("")
        lines.append("### Decision")
        lines.append("")
        lines.append("- [ ] **✅ APPROVE** — Proceed with the recommended action")
        lines.append("- [ ] **❌ REJECT** — Decline this proposal (provide reason below)")
        lines.append("- [ ] **⏸ DEFER** — Not enough information, gather more evidence")
        lines.append("")
        lines.append("### Reviewer Notes")
        lines.append("")
        lines.append("```")
        lines.append("Reviewer: _______________")
        lines.append("Date:     _______________")
        lines.append("")
        lines.append("Comments:")
        lines.append("")
        lines.append("")
        lines.append("")
        lines.append("```")
        lines.append("")
        lines.append("### Decision Result _(to be filled by system after review)_")
        lines.append("")
        lines.append("| Field | Value |")
        lines.append("|-------|-------|")
        lines.append("| Decision | _pending_ |")
        lines.append("| Reviewed At | _pending_ |")
        lines.append("| Reviewed By | _pending_ |")
        lines.append("| Implementation Status | _not started_ |")
        lines.append("")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # FOOTER
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        lines.append("---")
        lines.append("")
        lines.append(
            f"*Generated by DICE Phase 6.6 Review Artifact Generator | "
            f"{_format_ts(_now())} | "
            f"Evidence-driven Capability Evolution*"
        )
        lines.append("")

        return "\n".join(lines)

    # ═══════════════════════════════════════════════════════════════════
    # Label helpers
    # ═══════════════════════════════════════════════════════════════════

    @staticmethod
    def _freq_label(freq: int) -> str:
        if freq >= 50:
            return "🟢 Very High"
        elif freq >= 20:
            return "🟡 High"
        elif freq >= 5:
            return "🟠 Medium"
        else:
            return "🔴 Low"

    @staticmethod
    def _spread_label(spread: int) -> str:
        if spread >= 5:
            return "🟢 Wide (cross-domain)"
        elif spread >= 3:
            return "🟡 Moderate"
        elif spread >= 2:
            return "🟠 Narrow"
        else:
            return "🔴 Single-document"

    @staticmethod
    def _failure_label(failures: int) -> str:
        if failures >= 5:
            return "🔴 High failure rate"
        elif failures >= 3:
            return "🟠 Notable"
        elif failures > 0:
            return "🟡 Minor"
        else:
            return "✅ None"

    @staticmethod
    def _overlap_label(overlap: int) -> str:
        if overlap >= 5:
            return "🟢 Well-covered by existing capabilities"
        elif overlap >= 3:
            return "🟡 Partial coverage"
        elif overlap >= 1:
            return "🟠 Minimal coverage"
        else:
            return "🔴 True gap — no capability handles this"

    @staticmethod
    def _impact_label(impact: float) -> str:
        if impact >= 400:
            return "🔴 Critical — frequent × wide spread"
        elif impact >= 100:
            return "🟠 Significant"
        elif impact >= 20:
            return "🟡 Moderate"
        else:
            return "🟢 Low"


# ═══════════════════════════════════════════════════════════════════════════
# Convenience: one-shot generation
# ═══════════════════════════════════════════════════════════════════════════


def generate_review_artifacts(
    proposals: list[EvolutionProposal],
    output_dir: str = "knowledge/review",
    registry: Any = None,
    decisions: Optional[list[Any]] = None,
    candidates: Optional[list[Any]] = None,
) -> dict[str, Any]:
    """
    One-shot: generate review artifacts for all proposals.

    Returns:
        {
            "proposals_total": N,
            "artifacts_generated": M,
            "output_dir": "...",
            "files": ["path1.md", "path2.md", ...],
        }
    """
    generator = ReviewArtifactGenerator(output_dir=output_dir)
    paths = generator.generate(
        proposals, registry=registry, decisions=decisions, candidates=candidates
    )

    return {
        "proposals_total": len(proposals),
        "artifacts_generated": len(paths),
        "output_dir": os.path.abspath(output_dir),
        "files": paths,
    }
