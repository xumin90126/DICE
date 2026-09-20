"""
Shadow Evidence Runtime Adapter — Phase 2 Step 2.

Migrates the Pilot 1-validated Evidence Runtime Layer into production as a
shadow adapter. Reads document text, runs the full four-stage evidence pipeline,
and outputs EvidenceResult[] — WITHOUT affecting any production path.

Pipeline (from Step 3.6 Architecture Freeze):
    Document Text
        │
        ▼
    Stage 1: CombinedEvidenceExtractor
        — Extract all evidence spans (problem→resolution pairs + single-signal)
        │
        ▼
    Stage 2: SpanRoleValidator
        — Classify problem_signal_role and resolution_signal_role
        │
        ▼
    Stage 3: EvidenceTypeClassifier
        — Classify each span into EvidenceType (capability-independent)
        │
        ▼
    Stage 4: CapabilityIndependentValidator
        — Produce EvidenceResult with boundary validation

CONSTRAINTS:
    - Zero production code modification
    - Zero CapabilityDefinition modification
    - Zero keyword rules added
    - Zero capability_id hardcoding
    - EvidenceResult is capability-independent
"""

from __future__ import annotations

import re
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ═══════════════════════════════════════════════════════════════════════════
# Frozen Data Types (from Pilot 1 Step 4.2 Contract)
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class ShadowEvidenceSpan:
    """Candidate evidence fragment — capability-agnostic."""
    span_id: str = ""
    span_text: str = ""
    char_start: int = 0
    char_end: int = 0
    line_start: int = 0
    line_end: int = 0
    problem_signal: str = ""
    problem_signal_type: str = ""
    resolution_signal: str = ""
    resolution_signal_type: str = ""
    single_signal: str = ""
    single_signal_type: str = ""
    pair_distance: int = 0
    context_window: str = ""
    document_section: str = ""
    problem_signal_role: str = ""
    resolution_signal_role: str = ""


@dataclass
class ShadowEvidenceResult:
    """Frozen Step 4.2 contract — capability-independent evidence result."""
    span_id: str = ""
    document_id: str = ""
    evidence_type: str = ""
    problem_role: str = ""
    resolution_role: str = ""
    confidence: float = 0.0
    boundary_verdict: str = ""  # "ACCEPT" | "REJECT"
    rejection_reason: str = ""
    source_span: dict[str, Any] = field(default_factory=dict)
    classification_path: str = ""


@dataclass
class ShadowRunResult:
    """Complete result of one shadow run."""
    document_id: str = ""
    filename: str = ""
    char_count: int = 0
    spans_extracted: int = 0
    evidence_accepted: int = 0
    evidence_rejected: int = 0
    evidence_results: list[ShadowEvidenceResult] = field(default_factory=list)
    evidence_type_distribution: dict[str, int] = field(default_factory=dict)
    problem_role_distribution: dict[str, int] = field(default_factory=dict)
    run_time_ms: float = 0.0
    timestamp: str = field(default_factory=_now)


# ═══════════════════════════════════════════════════════════════════════════
# Combined Pattern Definitions (from Pilot 1, frozen)
# ═══════════════════════════════════════════════════════════════════════════

ANOMALY_PATTERNS = [
    r"\bno\s+amplification\b", r"\bno\s+signal\b", r"\bno\s+band\b",
    r"\bno\s+product\b", r"\bno\s+colony\b", r"\bno\s+result\b",
    r"\bno\s+peak\b", r"\bno\s+growth\b", r"\bno\s+fragment\b",
    r"\bfailed\b", r"\bfailure\b", r"\bfail\b",
    r"\bunexpected\b", r"\babnormal\b", r"\baberrant\b",
    r"\bartifact\b", r"\bmissing\b", r"\babsent\b",
    r"\bnot\s+detected\b", r"\bnot\s+observed\b", r"\bnot\s+visible\b",
    r"\bnot\s+present\b", r"\bnot\s+found\b", r"\bnot\s+obtained\b",
    r"\bsmear\b", r"\bdegradation\b", r"\bcontamination\b",
    r"\bdegraded\b", r"\bsheared\b", r"\bfragmented\b",
    r"\bpoor\s+quality\b", r"\bpoor\s+resolution\b",
    r"\blow\s+yield\b", r"\blow\s+quality\b", r"\blow\s+efficiency\b",
    r"\blow\s+intensity\b", r"\blow\s+signal\b",
    r"\bweak\s+signal\b", r"\bweak\s+band\b",
    r"\binsufficient\b", r"\btoo\s+low\b", r"\btoo\s+high\b",
    r"\btoo\s+much\b", r"\btoo\s+little\b", r"\bnot\s+enough\b",
    r"\binadequat\b", r"\bprecipitate\w*\b", r"\bprecipitation\b",
    r"\binhibitor\b", r"\binhibition\b", r"\binterfer\w*\b",
    r"\bnuclease\b", r"\bRNase\b", r"\bDNase\b",
    r"\bprimer[\s-]?dimer\b",
    r"\bnon[\s-]?specific\s+(?:amplification|band|product)\b",
    r"\bcarry[\s-]?over\b", r"\bcross[\s-]?contamination\b",
    r"\bevaporat\w*\b", r"\bdry\w*\s*out\b",
]

RECOVERY_PATTERNS = [
    r"\bre[\s-]?(?:purif|extract|amplif|optimiz|suspend|dissolve|run|mix|load|prepare)",
    r"\btroubleshoot\b", r"\btrouble\s*shoot\b",
    r"\brepeat\s+(?:the|with|using|from)\b",
    r"\bincrease\s+(?:the\s+)?(?:volume|amount|time|temperature|concentration)\b",
    r"\bdecrease\s+(?:the\s+)?(?:volume|amount|time|temperature|concentration)\b",
    r"\badjust\s+(?:the\s+)?(?:concentration|volume|pH|ratio|amount)\b",
    r"\bprolong\s+(?:the\s+)?(?:incubation|extension|time)\b",
    r"\buse\s+(?:fresh|new|different)\s+(?:reagent|buffer|enzyme|primer)\b",
    r"\bcheck\s+(?:for\s+)?(?:contamination|degradation|inhibitor)\b",
    r"\bfollow\s+the\s+(?:standard|general|normal)\s+(?:protocol|procedure|instruction)\b",
    r"\brefer\s+to\s+(?:the\s+)?(?:standard|instruction|protocol)\b",
    r"\buse\s+(?:the\s+)?(?:standard|general|recommended)\s+(?:protocol|method|procedure)\b",
    r"\badd\s+(?:\w+\s+)?(?:PBS|buffer|water|reagent|solution)\b",
    r"\bconfirm\s+(?:the\s+)?(?:result|volume|concentration|amount)\b",
]

CONDITIONAL_ANCHORS = [
    r"\bif\s+the\b", r"\bif\s+no\b", r"\bif\s+any\b",
    r"\bif\s+not\b", r"\bif\s+a\b", r"\bif\s+an\b",
    r"\bwhen\s+the\b", r"\bwhen\s+a\b", r"\bwhen\s+no\b",
    r"\bwhen\s+an\b", r"\bbefore\s+the\b", r"\bafter\s+the\b",
]

STORAGE_PATTERNS = [
    r"\bstore\s+at\b", r"\bstable\s+at\b",
    r"\b-?\d+\s*(?:°C|℃|°F)\b",
    r"\bdry\b", r"\bdark\b", r"\broom\s+temp\b",
    r"\bstable\s+for\b", r"\bshelf\s+life\b",
    r"\bexpir\w+\b", r"\bstorage\b", r"\bstore\b",
    r"\bprotect\s+from\b", r"\bkeep\s+away\b",
    r"\bstability\b",
]

SAFETY_PATTERNS = [
    r"\bdanger\b", r"\bwarning\b", r"\bcaution\b", r"\bhazard\b",
    r"\bharmful\b", r"\btoxic\b", r"\birritant\b",
    r"\bcorrosive\b", r"\bflammable\b",
    r"\bwear\s+(?:gloves|goggles|mask|protective)\b",
    r"\bventilation\b", r"\bPPE\b",
    r"\bpersonal\s+protective\b",
    r"\bseek\s+medical\b", r"\bfirst\s+aid\b",
    r"\bH302\b", r"\bH315\b", r"\bH319\b",
    r"\blethal\b", r"\bfatal\b", r"\bcarcinogen\b", r"\bmutagen\b",
    r"\bpoison\b", r"\binhal\w*\b", r"\bingest\w*\b",
    r"\bavoid\s+contact\b", r"\bdo\s+not\s+(?:ingest|inhale|eat|drink)\b",
]

PROCEDURE_PATTERNS = [
    r"(?:^|\n)\s*(\d+[\.\)]|step\s+\d+)",
    r"\b(then|next|after\s+that|finally)\b",
]

ACTION_VERBS = [
    r"\b(add|mix|pipette|incubate|centrifuge|wash|elute|transfer)\b",
    r"\bresuspend\b", r"\baspirate\b", r"\bdilute\b",
    r"\bpellet\b", r"\bcollect\b", r"\bdiscard\b",
    r"\bprepare\b", r"\bvortex\b", r"\bheat\b", r"\bcool\b",
    r"\bplace\b", r"\bremove\b", r"\brepeat\b",
    r"\bseal\b", r"\bcover\b", r"\bclose\b", r"\bopen\b",
    r"\bcheck\b", r"\bensure\b", r"\bverify\b",
    r"\bproceed\b", r"\bperform\b", r"\bstop\b",
]

QC_PATTERNS = [
    r"\btest\s+(?:purpose|protocol|method|result|summary)\b",
    r"\bvalidation\s+method\b", r"\bjudgment\s+criteri\b",
    r"\bperformance\s+test\b", r"\bstability\s+test\b",
    r"\bspecificity\s+test\b", r"\bsensitivity\s+test\b",
    r"\bdeter\w+\s+(?:by|the|whether)\b",
    r"\bevaluat\w*\s+(?:the|by|method)\b",
    r"\bassay\b", r"\banalysis\b",
    r"\bpass\s+criteri\b", r"\baccept\w*\s+criteri\b",
    r"\bconcentration\s+(?:determin|measur)\b",
]

COMPARISON_PATTERNS = [
    r"\bcompar\w+\b", r"\bversus\b", r"\bvs\.?\b",
    r"\brelative\s+to\b",
    r"\bhigher\s+than\b", r"\blower\s+than\b",
    r"\bbetter\s+than\b", r"\bworse\s+than\b",
    r"\bsuperior\s+to\b", r"\binferior\s+to\b",
    r"\bcompetitive\b", r"\bcompetitor\b",
    r"\bbenchmark\b", r"\boutperforms?\b",
]

COMPONENT_PATTERNS = [
    r"\bcomponent\b", r"\bkit\s+content", r"\bmaterial\b",
    r"\breagent\s+provided\b", r"\bsupplied\b",
]

SAMPLE_PREP_PATTERNS = [
    r"\bsample\s+preparation\b", r"\bsample\s+prep\b",
    r"\binput\s+(?:material|DNA|RNA|sample)\b",
    r"\bstarting\s+material\b",
    r"\btemplate\s+(?:preparation|DNA|RNA)\b",
]

PATTERN_MAP = {
    "anomaly": (ANOMALY_PATTERNS, "problem_signal"),
    "recovery": (RECOVERY_PATTERNS, "resolution_signal"),
    "conditional": (CONDITIONAL_ANCHORS, "conditional_signal"),
    "storage": (STORAGE_PATTERNS, "storage_signal"),
    "safety": (SAFETY_PATTERNS, "safety_signal"),
    "procedure": (PROCEDURE_PATTERNS, "procedure_signal"),
    "action": (ACTION_VERBS, "action_signal"),
    "qc": (QC_PATTERNS, "qc_signal"),
    "comparison": (COMPARISON_PATTERNS, "comparison_signal"),
    "component": (COMPONENT_PATTERNS, "component_signal"),
    "sample_prep": (SAMPLE_PREP_PATTERNS, "sample_prep_signal"),
}

PROXIMITY_THRESHOLD = 500
CONTEXT_WINDOW = 300


# ═══════════════════════════════════════════════════════════════════════════
# Stage 1: CombinedEvidenceExtractor
# ═══════════════════════════════════════════════════════════════════════════

class CombinedEvidenceExtractor:
    """Extract ALL evidence spans from document using combined patterns."""

    def extract(self, content: str) -> list[ShadowEvidenceSpan]:
        all_spans: list[ShadowEvidenceSpan] = []

        ts_spans = self._extract_pairs(content)
        all_spans.extend(ts_spans)

        single_spans = self._extract_singles(content)
        all_spans.extend(single_spans)

        all_spans = self._deduplicate(all_spans)
        return all_spans

    def _extract_pairs(self, content: str) -> list[ShadowEvidenceSpan]:
        p_matches = self._scan_patterns(content, ANOMALY_PATTERNS + CONDITIONAL_ANCHORS, "problem")
        r_matches = self._scan_patterns(content, RECOVERY_PATTERNS, "resolution")

        if not p_matches or not r_matches:
            return []

        # Filter: resolution containing anomaly vocab → invalid
        problem_words = set()
        for pm in p_matches:
            words = re.findall(r'\b\w+\b', pm["text"].lower())
            problem_words.update(w for w in words if len(w) > 3)

        r_matches = [
            rm for rm in r_matches
            if not any(
                len(w) > 3 and w in problem_words
                for w in re.findall(r'\b\w+\b', rm["text"].lower())
            )
        ]
        if not r_matches:
            return []

        generic_triggers = {
            "if the", "if no", "if any", "if not", "if a", "if an",
            "when the", "when a", "when no", "when an",
            "unless", "except",
        }

        def _is_anomaly(pm: dict) -> bool:
            for gt in generic_triggers:
                if gt in pm["text"].lower():
                    return False
            return True

        p_matches.sort(key=lambda pm: (0 if _is_anomaly(pm) else 1, pm["position"]))
        r_matches.sort(key=lambda m: m["position"])

        spans = []
        paired_r = set()
        lines = content.split("\n")

        for pi, p_match in enumerate(p_matches):
            best_r = None
            best_dist = float("inf")
            for ri, r_match in enumerate(r_matches):
                if ri in paired_r and not _is_anomaly(p_match):
                    continue
                r_pos = r_match["position"]
                if r_pos < p_match["position"] and (p_match["position"] - r_pos) > 50:
                    continue
                dist = abs(p_match["position"] - r_pos)
                if dist <= PROXIMITY_THRESHOLD and dist < best_dist:
                    best_r = r_match
                    best_dist = dist

            if best_r is not None:
                paired_r.add(r_matches.index(best_r))
                p_pos = p_match["position"]
                r_pos = best_r["position"]
                span_start = min(p_pos, r_pos)
                span_end = max(p_pos + len(p_match["text"]), r_pos + len(best_r["text"]))

                ctx_start = max(0, span_start - CONTEXT_WINDOW)
                ctx_end = min(len(content), span_end + CONTEXT_WINDOW)
                span_text = content[span_start:span_end]
                context = content[ctx_start:ctx_end]

                p_line = self._find_line(lines, p_pos)
                r_line = self._find_line(lines, r_pos)

                spans.append(ShadowEvidenceSpan(
                    span_id=f"SHADOW-EV-P-{len(spans):03d}",
                    span_text=span_text,
                    char_start=span_start,
                    char_end=span_end,
                    line_start=min(p_line, r_line),
                    line_end=max(p_line, r_line),
                    problem_signal=p_match["text"],
                    problem_signal_type=p_match["signal_type"],
                    resolution_signal=best_r["text"],
                    resolution_signal_type=best_r["signal_type"],
                    pair_distance=best_dist,
                    context_window=context,
                    document_section=self._find_section(content, span_start),
                ))

        return spans

    def _extract_singles(self, content: str) -> list[ShadowEvidenceSpan]:
        single_categories = ["storage", "safety", "procedure", "qc", "comparison", "component", "sample_prep"]
        all_matches = []
        for cat in single_categories:
            patterns, sig_type = PATTERN_MAP[cat]
            cat_matches = self._scan_patterns(content, patterns, sig_type)
            all_matches.extend(cat_matches)

        all_matches.sort(key=lambda m: m["position"])
        lines = content.split("\n")
        spans = []

        for mi, match in enumerate(all_matches):
            pos = match["position"]
            tlen = len(match["text"])
            already_covered = any(
                s.char_start <= pos <= s.char_end for s in spans
            )
            if already_covered:
                continue

            ctx_start = max(0, pos - CONTEXT_WINDOW)
            ctx_end = min(len(content), pos + tlen + CONTEXT_WINDOW)
            line = self._find_line(lines, pos)

            spans.append(ShadowEvidenceSpan(
                span_id=f"SHADOW-EV-S-{len(spans):03d}",
                span_text=content[pos:pos + tlen],
                char_start=pos,
                char_end=pos + tlen,
                line_start=line,
                line_end=line,
                single_signal=match["text"],
                single_signal_type=match["signal_type"],
                context_window=content[ctx_start:ctx_end],
                document_section=self._find_section(content, pos),
            ))

        return spans

    def _scan_patterns(self, content: str, patterns: list[str], sig_type: str) -> list[dict]:
        results = []
        text_lower = content.lower()
        seen = set()
        for pat in patterns:
            for m in re.finditer(pat, text_lower, re.IGNORECASE):
                pos = m.start()
                matched = content[m.start():m.end()]
                key = (pos, matched)
                if key not in seen:
                    seen.add(key)
                    results.append({"position": pos, "text": matched, "signal_type": sig_type})
        return results

    def _find_line(self, lines: list[str], pos: int) -> int:
        char_count = 0
        for i, line in enumerate(lines):
            char_count += len(line) + 1
            if char_count > pos:
                return i + 1
        return len(lines)

    def _find_section(self, content: str, pos: int) -> str:
        before = content[:pos]
        headers = re.findall(
            r"(?:^|\n)\s*([\d.]+(?:[./]|\s+)?[A-Z][^\n]{2,60})",
            before, re.MULTILINE,
        )
        return headers[-1].strip() if headers else ""

    def _deduplicate(self, spans: list[ShadowEvidenceSpan]) -> list[ShadowEvidenceSpan]:
        if not spans:
            return []
        spans.sort(key=lambda s: (s.char_start, -(s.char_end - s.char_start)))
        kept = []
        for span in spans:
            if not any(
                s.char_start <= span.char_start and span.char_end <= s.char_end
                for s in kept
            ):
                kept.append(span)
        return kept


# ═══════════════════════════════════════════════════════════════════════════
# Stage 2: SpanRoleValidator (from Pilot 1 Step 3.5 — frozen)
# ═══════════════════════════════════════════════════════════════════════════

class SpanRoleValidator:
    """Classify problem_signal_role and resolution_signal_role on each span."""

    ANOMALY_MARKERS = [
        r'\bunexpected\b', r'\bobserved\b', r'\bfailed\b', r'\bfailure\b',
        r'\bmissing\b', r'\babsent\b', r'\bnot\s+detected\b',
        r'\bnot\s+observed\b', r'\bnot\s+visible\b', r'\bnot\s+present\b',
        r'\babnormal\b', r'\baberrant\b', r'\bartifact\b',
        r'\bno\s+(?:signal|amplification|band|product|result|colony|peak|growth|fragment)\b',
        r'\bpoor\s+(?:quality|resolution)\b',
        r'\blow\s+(?:yield|quality|efficiency|intensity|signal)\b',
        r'\binsufficient\b', r'\btoo\s+(?:low|high|little|much)\b',
        r'\bweak\s+(?:signal|band)\b', r'\bnot\s+enough\b', r'\binadequat\b',
        r'\binhibitor\b', r'\binhibition\b', r'\binterfer\w*\b',
        r'\bprimer[\s-]*dimer\b', r'\bcontamination\b', r'\bcross[\s-]*contamination\b',
        r'\bdegradation\b', r'\bdegraded\b', r'\bsmear\b', r'\bsheared\b',
        r'\bfragmented\b', r'\bcarry[\s-]*over\b',
        r'\bevaporat\w*\b', r'\bdry\w*\s*out\b',
        r'\bnon[\s-]*specific\s+(?:amplification|band|product)\b',
    ]

    PROCEDURE_ANCHORS = [
        r'\bcheck\s+(?:for|the|all|each|any|whether)\b',
        r'\bconfirm\s+(?:the|that|all|by|using)\b',
        r'\bensure\s+(?:the|that|all|proper|no|adequate)\b',
        r'\bverify\s+(?:that|the|by)\b',
        r'\bbefore\s+(?:use|proceeding|starting|beginning|each|every)\b',
        r'\bprior\s+to\s+(?:use|each|the)\b',
        r'\bmake\s+sure\s+',
        r'\bto\s+avoid\b',
    ]

    MATERIAL_PATTERNS = [
        r'^\s*[-–—]?\s*(?:free|depleted|resistant|treated|inactivated|deficient)\b',
        r'\blow[\s-]*(?:binding|retention|adsorption|background)\b',
        r'\b(?:certified|validated|verified|guaranteed)\s+(?:nuclease|rnase|dnase|pyrogen)[\s-]*free\b',
    ]

    SPEC_MARKERS = [
        r'\b(?:according|per)\s+(?:to\s+)?(?:the\s+)?specif',
        r'\bwithin\s+(?:the\s+)?(?:specif|range|limit|tolerance)',
        r'\bthreshold\b',
    ]

    RECOVERY_ACTIONS = [
        r"\bre[\s-]?(?:purif|extract|amplif|optimiz|suspend|dissolve|run|mix|load|prepare)",
        r"\brepeat\b", r"\btroubleshoot\b",
        r"\bincrease\s+(?:the\s+)?\w+\b", r"\bdecrease\s+(?:the\s+)?\w+\b",
        r"\badjust\b", r"\bprolong\b",
        r"\buse\s+(?:fresh|new|different)\b",
        r"\bcheck\s+(?:for\s+)?(?:contamination|degradation|inhibitor)\b",
    ]

    PROCEDURE_ACTIONS = [
        r"\bwarm\b", r"\bheat\b", r"\bcool\b", r"\bvortex\b",
        r"\bcentrifuge\b", r"\badd\b", r"\btransfer\b", r"\bincubate\b",
        r"\bseal\b", r"\bmix\b", r"\bdilute\b", r"\bpipette\b",
        r"\bwash\b", r"\belute\b", r"\bprepare\b", r"\baspirate\b",
        r"\bpellet\b", r"\bcollect\b", r"\bdiscard\b", r"\bplace\b",
        r"\bremove\b", r"\bcover\b", r"\bclose\b", r"\bopen\b",
        r"\bconfirm\b", r"\bensure\b", r"\bverify\b", r"\bproceed\b",
        r"\bperform\b", r"\bresuspend\b", r"\bdissolve\b",
    ]

    def validate_pair(self, span: ShadowEvidenceSpan) -> ShadowEvidenceSpan:
        span.problem_signal_role = self._classify_problem_role(span)
        span.resolution_signal_role = self._classify_resolution_role(span)
        return span

    def validate_single(self, span: ShadowEvidenceSpan) -> ShadowEvidenceSpan:
        st = (span.single_signal_type or "").lower()
        if "safety" in st:
            span.problem_signal_role = "SAFETY_RISK"
            span.resolution_signal_role = "SAFETY_INSTRUCTION"
        elif "storage" in st:
            span.problem_signal_role = "STORAGE_REQUIREMENT"
            span.resolution_signal_role = "STORAGE_INSTRUCTION"
        elif "qc" in st or "comparison" in st:
            span.problem_signal_role = "SPECIFICATION_CRITERIA"
            span.resolution_signal_role = "TEST_RESULT"
        elif "procedure" in st or "action" in st:
            span.problem_signal_role = "PROCEDURE_CONDITION"
            span.resolution_signal_role = "PROCEDURE_STEP"
        elif "component" in st:
            span.problem_signal_role = "MATERIAL_DESCRIPTION"
            span.resolution_signal_role = "COMPONENT_SPEC"
        elif "sample_prep" in st:
            span.problem_signal_role = "PREPARATION_CONDITION"
            span.resolution_signal_role = "PREPARATION_ACTION"
        else:
            span.problem_signal_role = "UNKNOWN"
            span.resolution_signal_role = "UNKNOWN"
        return span

    def _classify_problem_role(self, span: ShadowEvidenceSpan) -> str:
        if not span.problem_signal:
            return "UNKNOWN"
        prob_text = span.problem_signal
        local_before = span.span_text[:span.span_text.find(prob_text)] if prob_text in span.span_text else span.span_text[:span.char_end - span.char_start]
        local_scope = span.span_text

        for marker in self.ANOMALY_MARKERS:
            if re.search(marker, local_scope, re.IGNORECASE):
                for anchor in self.PROCEDURE_ANCHORS:
                    if re.search(anchor, local_before, re.IGNORECASE):
                        return "PROCEDURE_CONDITION"
                return "ANOMALY_EVENT"

        for anchor in self.PROCEDURE_ANCHORS:
            if re.search(anchor, local_before, re.IGNORECASE):
                return "PROCEDURE_CONDITION"

        if re.search(r'\bif\b\s*$', local_before, re.IGNORECASE):
            return "PROCEDURE_CONDITION"

        ctx = span.context_window.lower()
        for marker in self.SPEC_MARKERS:
            if re.search(marker, ctx, re.IGNORECASE):
                return "SPECIFICATION_CRITERIA"

        for pat in self.MATERIAL_PATTERNS:
            if re.search(pat, local_scope, re.IGNORECASE):
                return "MATERIAL_DESCRIPTION"

        return "PROCEDURE_CONDITION"

    def _classify_resolution_role(self, span: ShadowEvidenceSpan) -> str:
        if not span.resolution_signal:
            return "UNKNOWN"
        res_text = span.resolution_signal.lower()
        for pat in self.RECOVERY_ACTIONS:
            if re.search(pat, res_text, re.IGNORECASE):
                return "RECOVERY_ACTION"
        for pat in self.PROCEDURE_ACTIONS:
            if re.search(pat, res_text, re.IGNORECASE):
                return "PROCEDURE_STEP"
        return "UNKNOWN"


# ═══════════════════════════════════════════════════════════════════════════
# Stage 3: EvidenceTypeClassifier (capability-independent)
# ═══════════════════════════════════════════════════════════════════════════

class EvidenceTypeClassifier:
    """Classify EvidenceSpan into evidence type — capability-independent."""

    # Evidence type enum values (from Pilot 1 Step 3.2 freeze)
    EVIDENCE_TYPES = [
        "anomaly_recovery", "batch_compatibility", "condition_procedure",
        "sequential_step", "preparation_step", "safety_statement",
        "hazard_warning", "precaution", "storage_condition",
        "stability_parameter", "test_method", "qc_criterion",
        "comparison", "component_spec", "document_structure", "unknown",
    ]

    def classify(self, span: ShadowEvidenceSpan) -> tuple[str, float, str]:
        """Classify span → (evidence_type, confidence, explanation)."""
        ctx = span.context_window.lower()
        st = span.span_text.lower()

        # 1. SAFETY (highest priority)
        for pat in SAFETY_PATTERNS[:10]:
            if re.search(pat, ctx, re.IGNORECASE):
                return ("safety_statement", 0.85, "Safety vocabulary detected")

        # 2. ANOMALY_RECOVERY
        if span.problem_signal and span.resolution_signal and span.pair_distance > 0:
            has_anomaly = span.problem_signal_role == "ANOMALY_EVENT"
            has_recovery = span.resolution_signal_role == "RECOVERY_ACTION"

            if has_anomaly and has_recovery:
                if self._is_storage_context(span):
                    return ("storage_condition", 0.75, "Anomaly vocab in storage context")
                return ("anomaly_recovery", 0.88, "Anomaly event + recovery action pair")
            elif has_anomaly:
                return ("anomaly_recovery", 0.65, "Anomaly event detected")
            elif span.problem_signal_role == "PROCEDURE_CONDITION":
                return ("condition_procedure", 0.75, "Procedure condition with resolution")
            else:
                return ("condition_procedure", 0.60, "Generic condition pair")

        # 3. Single-signal classification
        sig_type = (span.single_signal_type or "").lower()

        if "safety" in sig_type:
            return ("safety_statement", 0.80, "Safety signal detected")
        if "storage" in sig_type:
            return ("storage_condition", 0.80, "Storage condition signal")
        if "qc" in sig_type:
            return ("test_method", 0.75, "QC/test method signal")
        if "comparison" in sig_type:
            return ("comparison", 0.75, "Comparison signal")
        if "procedure" in sig_type or "action" in sig_type:
            return ("sequential_step", 0.70, "Procedure/action signal")
        if "component" in sig_type:
            return ("component_spec", 0.70, "Component specification")
        if "sample_prep" in sig_type:
            return ("preparation_step", 0.70, "Sample preparation signal")

        return ("unknown", 0.30, f"Unclassifiable signal type: {sig_type}")

    def _is_storage_context(self, span: ShadowEvidenceSpan) -> bool:
        ctx_lower = span.context_window.lower()
        section = (span.document_section or "").lower()
        storage_section_markers = [r"\bstorage\b", r"\bstability\b", r"\bpreservation\b"]
        for pat in storage_section_markers:
            if re.search(pat, section):
                return True
        storage_anchors = [
            r"\bstore\b", r"\bstorage\b", r"\bshelf\s+life\b",
            r"\bexpir\w+\b", r"\bprotect\s+from\b",
        ]
        has_storage_anchor = any(re.search(pat, ctx_lower, re.IGNORECASE) for pat in storage_anchors)
        if has_storage_anchor:
            temp_markers = [r"\b-?\d+\s*(?:°C|°F|℃)\b", r"\bfreeze\b", r"\bthaw\b"]
            if any(re.search(pat, ctx_lower, re.IGNORECASE) for pat in temp_markers):
                return True
        return False


# ═══════════════════════════════════════════════════════════════════════════
# Stage 4: CapabilityIndependentValidator
# ═══════════════════════════════════════════════════════════════════════════

class CapabilityIndependentValidator:
    """Produces EvidenceResult from classified span — capability-independent."""

    def validate(self, span: ShadowEvidenceSpan, evidence_type: str,
                 confidence: float, classification_path: str,
                 document_id: str) -> ShadowEvidenceResult:
        accepted = evidence_type != "unknown" and confidence >= 0.30
        rejection_reason = ""
        if not accepted:
            if evidence_type == "unknown":
                rejection_reason = f"Cannot classify evidence: sig_type={span.single_signal_type}"
            elif confidence < 0.30:
                rejection_reason = f"Confidence too low ({confidence:.2f})"

        return ShadowEvidenceResult(
            span_id=span.span_id,
            document_id=document_id,
            evidence_type=evidence_type,
            problem_role=span.problem_signal_role or "UNKNOWN",
            resolution_role=span.resolution_signal_role or "UNKNOWN",
            confidence=confidence,
            boundary_verdict="ACCEPT" if accepted else "REJECT",
            rejection_reason=rejection_reason,
            source_span={
                "span_id": span.span_id,
                "span_text": span.span_text[:200],
                "char_start": span.char_start,
                "char_end": span.char_end,
                "document_section": span.document_section,
                "problem_signal": span.problem_signal,
                "resolution_signal": span.resolution_signal,
                "single_signal": span.single_signal,
            },
            classification_path=classification_path,
        )


# ═══════════════════════════════════════════════════════════════════════════
# Shadow Adapter — Main Entry Point
# ═══════════════════════════════════════════════════════════════════════════

class EvidenceRuntimeShadowAdapter:
    """
    Shadow Evidence Runtime Adapter.

    Runs the complete Pilot 1 Evidence Runtime pipeline in shadow mode.
    Reads document text, outputs EvidenceResult[] — no production path affected.

    Usage:
        adapter = EvidenceRuntimeShadowAdapter()
        result = adapter.run(document_text, document_id, filename)
        # result.evidence_results → list of ShadowEvidenceResult
        # result.to_dict() → serializable for JSON output
    """

    def __init__(self):
        self.extractor = CombinedEvidenceExtractor()
        self.role_validator = SpanRoleValidator()
        self.classifier = EvidenceTypeClassifier()
        self.validator = CapabilityIndependentValidator()

    def run(self, content: str, document_id: str = "",
            filename: str = "") -> ShadowRunResult:
        """Run full shadow evidence pipeline on one document."""
        import time
        t0 = time.time()

        # Stage 1: Extract evidence spans
        all_spans = self.extractor.extract(content)

        # Stage 2: Role validation
        for span in all_spans:
            if span.problem_signal and span.resolution_signal and span.pair_distance > 0:
                self.role_validator.validate_pair(span)
            else:
                self.role_validator.validate_single(span)

        # Stage 3+4: Classify + validate → EvidenceResult[]
        evidence_results = []
        ev_type_dist: dict[str, int] = {}
        prob_role_dist: dict[str, int] = {}

        for span in all_spans:
            ev_type, confidence, explanation = self.classifier.classify(span)
            er = self.validator.validate(
                span, ev_type, confidence, explanation, document_id,
            )

            if er.boundary_verdict == "ACCEPT":
                ev_type_dist[er.evidence_type] = ev_type_dist.get(er.evidence_type, 0) + 1
                prob_role_dist[er.problem_role] = prob_role_dist.get(er.problem_role, 0) + 1

            evidence_results.append(er)

        accepted = [e for e in evidence_results if e.boundary_verdict == "ACCEPT"]
        rejected = [e for e in evidence_results if e.boundary_verdict == "REJECT"]

        run_time_ms = (time.time() - t0) * 1000

        return ShadowRunResult(
            document_id=document_id,
            filename=filename,
            char_count=len(content),
            spans_extracted=len(all_spans),
            evidence_accepted=len(accepted),
            evidence_rejected=len(rejected),
            evidence_results=evidence_results,
            evidence_type_distribution=ev_type_dist,
            problem_role_distribution=prob_role_dist,
            run_time_ms=run_time_ms,
        )

    def run_batch(self, documents: list[dict]) -> list[ShadowRunResult]:
        """
        Run shadow pipeline on multiple documents.

        Each document dict: {"content": str, "document_id": str, "filename": str}
        """
        results = []
        for doc in documents:
            result = self.run(
                content=doc["content"],
                document_id=doc.get("document_id", ""),
                filename=doc.get("filename", ""),
            )
            results.append(result)
        return results