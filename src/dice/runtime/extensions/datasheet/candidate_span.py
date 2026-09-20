"""
Phase 16.8: Datasheet Extension — CandidateSpan model + Generator.

CAND-002 (datasheet EXTEND) — UPSTREAM candidate generation layer.

This module introduces the FIRST real-PDF access point of the datasheet
extension: a deterministic, zero-authority generator that reads a source
PDF (PyMuPDF / fitz, READ-ONLY) and segments it into CandidateSpan
observations via LAYOUT-FIRST text-block segmentation.

Position in the data flow (Phase 16.7 Design Review):
    source PDF (real, read-only)
      → CandidateSpanGenerator.generate  → list[CandidateSpan]
      → Human Validation Gate (separate module) → DocumentSpan
      → DatasheetPipeline (Phase 16.4/16.5, unchanged)

CRITICAL BOUNDARY (Phase 16.7 T-1 ~ T-8, Phase 16.8 Scope):
    T-1  zero capability association — CandidateSpan has NO capability field
    T-2  zero span_type field — span_type is owned by Human (T-2 / B-3)
    T-3  CandidateSpan carries position_metadata; DocumentSpan does not (B-4)
    T-5  deterministic only (Layout-first + optional regex hint), zero LLM
    T-7  six authorities ZERO — no matcher/selector/router/ranking/scoring/
         executor/decision

    The generator performs NO semantic classification. It segments text
    blocks geometrically. The optional `hint()` method flags "worth a human
    look" candidates via design-time-fixed STRUCTURAL regexes (document-format
    features only, zero domain semantics) — this is a HINT, never a span_type,
    never a capability, never a decision.

Imports: only stdlib + `fitz` (PyMuPDF). `fitz` is a READ-ONLY PDF parsing
library with zero decision/selection/routing authority (Phase 16.8 Scope IN
step 1 "PDF text/layout extraction").
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

import fitz  # PyMuPDF — READ-ONLY PDF text/layout extraction (zero authority)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CandidateSpan:
    """Candidate-layer observation — a raw text block cut from a PDF page.

    STRICT 4-FIELD CONTRACT (Phase 16.8 Step 2):
        document_id       : source document identifier (fact)
        page_reference    : 1-based source page number (fact)
        span_text         : raw text block (fact)
        position_metadata : provenance (block_index / block_no / bbox) (fact)

    FORBIDDEN fields (never present by construction — T-1 / T-2):
        span_type / capability_reference / mapped_capability / decision /
        score / selected_capability
    """

    document_id: str = ""
    page_reference: int = 0
    span_text: str = ""
    position_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "page_reference": self.page_reference,
            "span_text": self.span_text,
            "position_metadata": dict(self.position_metadata),
        }


@dataclass
class GenerationResult:
    """Generator output wrapper — candidate list + provenance facts.

    Carries ONLY the candidate list plus a design-time-fixed provenance
    record (source file / page count / block count). Zero span_type, zero
    capability, zero classification.
    """

    candidates: List[CandidateSpan] = field(default_factory=list)
    source_file: str = ""
    page_count: int = 0
    block_count: int = 0
    generated_at: str = field(default_factory=_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_file": self.source_file,
            "page_count": self.page_count,
            "block_count": self.block_count,
            "generated_at": self.generated_at,
            "candidate_count": len(self.candidates),
            "candidates": [c.to_dict() for c in self.candidates],
        }


# Design-time-fixed candidate-hint patterns (Phase 16.7 §5.2 step ③).
#
# These are OPTIONAL, DETERMINISTIC, and carry ZERO classification authority:
# they flag "worth a human look" candidates only. They NEVER assign span_type,
# NEVER assign capability, NEVER decide anything. A hint is a fact-flag, not a
# category. The regex engine here performs PATTERN LOOKUP ONLY (re.search),
# never semantic reasoning.
#
# SEMANTIC ISOLATION (Phase 18.3): this namespace holds ONLY document-structure
# primitives (format features such as a colon key-value line). Capability
# semantic hints (concrete unit tokens, attribute names, capability identities)
# were REMOVED in Phase 18.3 — the single source of truth for any
# unit / attribute / capability semantics is the capability declaration files,
# never the candidate generator. Extending this namespace requires the new
# pattern to be a STRUCTURAL/format feature (e.g. a table-row or number-unit
# layout cue), never a unit- or attribute-bearing semantic.
CANDIDATE_HINT_PATTERNS: Dict[str, str] = {
    "colon_kv": r"\b[A-Za-z][A-Za-z /&,-]{1,40}:\s*\S",
}


class CandidateSpanGenerator:
    """Deterministic, zero-authority PDF → CandidateSpan generator.

    Uses PyMuPDF (fitz) for READ-ONLY text/layout extraction. Layout-first
    segmentation: each page's text blocks become CandidateSpan observations
    (geometric/text segmentation only, zero semantics). The optional `hint()`
    method applies design-time-fixed STRUCTURAL regexes as candidate hints
    (fact-flags), NEVER as span_type / capability / decision.

    ZERO authority (T-7): no matcher/selector/router/ranking/scoring/executor/
    decision. No span_type field, no capability field, no LLM, no NLP semantic
    reasoning, no document_type routing.
    """

    def generate(self, pdf_path: str, document_id: str) -> GenerationResult:
        """Extract text blocks from a source PDF into CandidateSpan observations.

        Args:
            pdf_path: filesystem path to the source PDF (READ-ONLY).
            document_id: the source document identifier (FACT). The caller
                supplies the file→id mapping; this generator never derives
                semantics from the filename or content.

        Returns:
            GenerationResult (candidate list + provenance facts).
        """
        doc = fitz.open(pdf_path)
        try:
            candidates: List[CandidateSpan] = []
            block_index = 0
            for page_number in range(doc.page_count):
                page = doc[page_number]
                blocks = page.get_text("blocks")
                for b in blocks:
                    # b = (x0, y0, x1, y1, text, block_no, block_type)
                    x0, y0, x1, y1, text, block_no, block_type = b
                    if block_type != 0:
                        continue  # only text blocks (skip images/drawings)
                    cleaned = text.strip()
                    if not cleaned:
                        continue  # skip empty blocks (geometric filter)
                    candidates.append(CandidateSpan(
                        document_id=document_id,
                        page_reference=page_number + 1,
                        span_text=cleaned,
                        position_metadata={
                            "block_index": block_index,
                            "block_no": block_no,
                            "bbox": [round(x0, 1), round(y0, 1),
                                     round(x1, 1), round(y1, 1)],
                        },
                    ))
                    block_index += 1
            return GenerationResult(
                candidates=candidates,
                source_file=pdf_path,
                page_count=doc.page_count,
                block_count=block_index,
            )
        finally:
            doc.close()

    def hint(self, span_text: str) -> List[str]:
        """Return design-time-fixed candidate hints for one span (fact-flags).

        This is an OPTIONAL, OUT-OF-BAND candidate hint — it is NEVER stored
        on CandidateSpan (the 4-field contract stays pure) and NEVER drives a
        span_type / capability / decision. It only reports which deterministic
        STRUCTURAL patterns matched, as a "worth a human look" flag.

        Args:
            span_text: a candidate span text (fact).

        Returns:
            List of matched structural hint names (e.g. ["colon_kv"]), possibly
            empty.
        """
        hints: List[str] = []
        for name, pattern in CANDIDATE_HINT_PATTERNS.items():
            if re.search(pattern, span_text):
                hints.append(name)
        return hints


__all__ = [
    "CandidateSpan",
    "GenerationResult",
    "CandidateSpanGenerator",
    "CANDIDATE_HINT_PATTERNS",
]
