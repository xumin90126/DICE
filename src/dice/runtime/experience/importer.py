"""
Experience Importer — imports historical successful slice processing cases.

Each case captures the full context: raw content, extraction result,
rules/patterns used, and ground truth. These become the training data
for Experience Mining.

CRITICAL: Cases are imported as EVIDENCE, not as rules. They describe
what worked and why — they don't prescribe what to do.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


@dataclass
class ExperienceCase:
    """
    A single historical success case for experience injection.

    Captures the full context of a successful component extraction,
    enabling mining of patterns without adding rules.
    """
    # ── Identity ──
    case_id: str = ""
    document_id: str = ""
    product_name: str = ""
    doc_class: str = ""  # for tracking only, NOT for rule creation

    # ── Content ──
    slice_id: str = ""           # e.g. "04_components"
    content: str = ""            # raw text that was processed
    content_hash: str = ""       # for dedup

    # ── Extraction Result ──
    extraction_result: dict[str, Any] = field(default_factory=dict)
    # e.g. {"components": [{"name": "RNase A", "quantity": "250", "unit": "μL"}], ...}

    # ── What was actually correct ──
    ground_truth: list[dict[str, Any]] = field(default_factory=list)
    # List of correct component objects

    # ── What rules/patterns were active ──
    active_patterns: list[str] = field(default_factory=list)
    # Pattern IDs that successfully matched
    active_strategy: str = ""
    # "anchor_split" or "density_scan"

    # ── Capability execution metadata ──
    capability_id: str = "CAP-COMP-TABLE"
    confidence: float = 0.0
    evidence_count: int = 0
    extraction_quality: float = 0.0          # % of components with quantity+unit

    # ── Status ──
    is_success: bool = True
    category: str = "success"                # "success", "partial", "failure"
    notes: str = ""

    # ── Timestamp ──
    imported_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "document_id": self.document_id,
            "product_name": self.product_name,
            "doc_class": self.doc_class,
            "slice_id": self.slice_id,
            "content": self.content,
            "content_length": len(self.content),
            "extraction_result": self.extraction_result,
            "ground_truth": self.ground_truth,
            "active_patterns": self.active_patterns,
            "active_strategy": self.active_strategy,
            "capability_id": self.capability_id,
            "confidence": self.confidence,
            "evidence_count": self.evidence_count,
            "extraction_quality": self.extraction_quality,
            "is_success": self.is_success,
            "category": self.category,
            "notes": self.notes,
            "imported_at": self.imported_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExperienceCase":
        return cls(
            case_id=data.get("case_id", ""),
            document_id=data.get("document_id", ""),
            product_name=data.get("product_name", ""),
            doc_class=data.get("doc_class", ""),
            slice_id=data.get("slice_id", ""),
            content=data.get("content", ""),
            extraction_result=data.get("extraction_result", {}),
            ground_truth=data.get("ground_truth", []),
            active_patterns=data.get("active_patterns", []),
            active_strategy=data.get("active_strategy", ""),
            capability_id=data.get("capability_id", "CAP-COMP-TABLE"),
            confidence=data.get("confidence", 0.0),
            evidence_count=data.get("evidence_count", 0),
            extraction_quality=data.get("extraction_quality", 0.0),
            is_success=data.get("is_success", True),
            category=data.get("category", "success"),
            notes=data.get("notes", ""),
            imported_at=data.get("imported_at", ""),
        )


class ExperienceImporter:
    """
    Imports historical success cases from various sources.

    Sources:
        1. CapabilityResult objects (from test execution)
        2. JSON/Markdown log files
        3. Manual ground truth entries

    The importer does NOT modify capability knowledge. It only collects
    cases for the miner to analyze.
    """

    def __init__(self):
        self.cases: list[ExperienceCase] = []

    # ═══════════════════════════════════════════════════════════
    # IMPORT METHODS
    # ═══════════════════════════════════════════════════════════

    def import_from_builtin_ground_truth(
        self,
        document_id: str,
        product_name: str,
        doc_class: str,
        slice_id: str,
        content: str,
        ground_truth: list[dict[str, Any]],
        extraction_result: Optional[dict[str, Any]] = None,
        active_patterns: Optional[list[str]] = None,
        active_strategy: str = "",
        confidence: float = 0.0,
    ) -> ExperienceCase:
        """
        Import a case with known ground truth.

        This is the primary method for Phase 2.3 — we know what the
        correct components are for each document, and we capture the
        Capability's actual performance against that ground truth.
        """
        import hashlib

        case_id = f"CASE-{document_id}-{slice_id}"
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]

        # Compute extraction quality
        if extraction_result and ground_truth:
            extracted_names = {
                c.get("name", "").lower()
                for c in extraction_result.get("components", [])
            }
            truth_names = {
                c.get("name", "").lower()
                for c in ground_truth
            }
            if truth_names:
                extraction_quality = len(extracted_names & truth_names) / len(truth_names)
            else:
                extraction_quality = 0.0

            # Determine category
            if extraction_quality >= 0.8:
                category = "success"
            elif extraction_quality >= 0.4:
                category = "partial"
            else:
                category = "failure"
        else:
            extraction_quality = 0.0
            category = "unknown"

        case = ExperienceCase(
            case_id=case_id,
            document_id=document_id,
            product_name=product_name,
            doc_class=doc_class,
            slice_id=slice_id,
            content=content,
            content_hash=content_hash,
            extraction_result=extraction_result or {},
            ground_truth=ground_truth,
            active_patterns=active_patterns or [],
            active_strategy=active_strategy,
            confidence=confidence,
            is_success=(category == "success"),
            category=category,
            extraction_quality=extraction_quality,
        )

        self.cases.append(case)
        return case

    def import_from_capability_result(
        self,
        case_id: str,
        document_id: str,
        slice_id: str,
        content: str,
        extraction_result: dict[str, Any],
        ground_truth: list[dict[str, Any]],
        active_patterns: list[str],
        confidence: float,
        doc_class: str = "",
        product_name: str = "",
    ) -> ExperienceCase:
        """Import from a CapabilityResult object."""
        return self.import_from_builtin_ground_truth(
            document_id=document_id,
            product_name=product_name,
            doc_class=doc_class,
            slice_id=slice_id,
            content=content,
            ground_truth=ground_truth,
            extraction_result=extraction_result,
            active_patterns=active_patterns,
            confidence=confidence,
        )

    def import_batch(self, cases_data: list[dict[str, Any]]) -> list[ExperienceCase]:
        """Import multiple cases from a list of dicts."""
        results = []
        for data in cases_data:
            case = self.import_from_builtin_ground_truth(
                document_id=data["document_id"],
                product_name=data.get("product_name", ""),
                doc_class=data.get("doc_class", ""),
                slice_id=data.get("slice_id", "04_components"),
                content=data["content"],
                ground_truth=data.get("ground_truth", []),
                extraction_result=data.get("extraction_result", {}),
                active_patterns=data.get("active_patterns", []),
                active_strategy=data.get("active_strategy", ""),
                confidence=data.get("confidence", 0.0),
            )
            results.append(case)
        return results

    # ═══════════════════════════════════════════════════════════
    # QUERY
    # ═══════════════════════════════════════════════════════════

    def get_success_cases(self) -> list[ExperienceCase]:
        """Return all cases with category='success'."""
        return [c for c in self.cases if c.category == "success"]

    def get_partial_cases(self) -> list[ExperienceCase]:
        """Return partial-success cases."""
        return [c for c in self.cases if c.category == "partial"]

    def get_failure_cases(self) -> list[ExperienceCase]:
        """Return failure cases."""
        return [c for c in self.cases if c.category == "failure"]

    def get_by_doc_class(self, doc_class: str) -> list[ExperienceCase]:
        """Get cases by legacy doc_class (for analysis only)."""
        return [c for c in self.cases if c.doc_class == doc_class]

    def get_stats(self) -> dict[str, Any]:
        """Get importer statistics."""
        total = len(self.cases)
        if total == 0:
            return {"total": 0}

        return {
            "total": total,
            "success": len(self.get_success_cases()),
            "partial": len(self.get_partial_cases()),
            "failure": len(self.get_failure_cases()),
            "by_doc_class": {
                dc: len(self.get_by_doc_class(dc))
                for dc in sorted(set(c.doc_class for c in self.cases))
            },
            "avg_confidence": (
                sum(c.confidence for c in self.cases) / total
                if total else 0.0
            ),
            "avg_quality": (
                sum(c.extraction_quality for c in self.cases) / total
                if total else 0.0
            ),
        }

    def save(self, path: str) -> None:
        """Save all cases to JSON."""
        data = {
            "stats": self.get_stats(),
            "cases": [c.to_dict() for c in self.cases],
        }
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self, path: str) -> None:
        """Load cases from JSON."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.cases = [ExperienceCase.from_dict(c) for c in data.get("cases", [])]


def import_experience_cases(
    cases_data: list[dict[str, Any]],
) -> ExperienceImporter:
    """Convenience: import batch of experience cases."""
    importer = ExperienceImporter()
    importer.import_batch(cases_data)
    return importer
