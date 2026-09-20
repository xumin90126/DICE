"""Atomic Observation Layer v1 — DRAWING_GEOMETRY_FACT enumeration.

Vector drawing primitive observation surface. Records ALL vector drawing
primitives returned by PyMuPDF page.get_drawings() as pure geometric facts.

This is the companion surface to NON_TEXT_BLOCK_ATOM (which covers raster
image blocks from get_text("dict").blocks[type != 0]). DRAWING_GEOMETRY_FACT
covers VECTOR drawing primitives from the independent get_drawings() API.

BOUNDARY (DC3):
  Records ALL primitives — NO pre-filter applied.
  min_width / min_height / border / ratio filters belong to DRAWING_EXTENT_FACT
  (Stage 1 pre-merge filter), NOT this surface.
  This is raw observation: every seqno is recorded.

FORBIDDEN (by contract): any semantic role naming (image/figure/chart/...),
OCR, content recovery, deduplication, arbitration, visual interpretation,
raw items passthrough, color/fill/width/opacity exposure.

Authorization: IMPLEMENTATION = AUTHORIZED (scope = this module only).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from typing import Any, Dict, List, Optional

_LAYER_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_LAYER_DIR, "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from perception.sandbox.observations.atomic_text import (  # noqa: E402  (frozen, read-only reuse)
    _round_bbox,
    pymupdf_version,
)

COORDINATE_SYSTEM = "pymupdf_page_1.26.x_y_down"
FACT_KIND = "DRAWING_GEOMETRY_FACT"

# Frozen anchor of the shared parse surface (registry-frozen P1 module).
P1_FROZEN_SHA = "74d23ec784d657825780b35627f1b766ad87bd4dd74d88bbe4d560941f3b724a"


def drawing_id_for(document_id: str, page_reference: int, seqno: int) -> str:
    """Pure-function drawing identity. No timestamp, no randomness."""
    return f"DRAW|{document_id}|p{page_reference}|{seqno}"


def params_hash() -> str:
    """Hash over the registered enumeration definition (no filter params).

    DRAWING_GEOMETRY_FACT records ALL primitives with NO pre-filter.
    Therefore params_hash contains only surface + fields + rounding —
    no filter parameters (those belong to DRAWING_EXTENT_FACT).
    """
    definition = json.dumps(
        {
            "surface": "page.get_drawings()",
            "fields": ["drawing_id", "fact_kind", "document_id", "page_reference",
                        "bbox", "draw_type", "item_count", "item_types",
                        "coordinate_system", "source_sha", "params_hash",
                        "schema_version", "pymupdf_version", "geometry_source"],
            "pre_filter": "NONE",
            "rounding": "frozen _round_bbox",
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(definition.encode("utf-8")).hexdigest()


def _extract_item_types(items: list) -> List[str]:
    """Extract sorted unique operation types from drawing items.

    Returns a sorted list of operation type strings ('l', 're', 'qu', 'c').
    Does NOT expose raw items or their coordinates — only the type labels.
    """
    op_types = set()
    for item in items:
        if isinstance(item, (tuple, list)) and len(item) > 0:
            op_types.add(str(item[0]))
    return sorted(op_types)


def enumerate_drawing_geometry(pdf_path: str,
                               document_id: str,
                               pages: Optional[List[int]] = None) -> List[Dict[str, Any]]:
    """Enumerate DRAWING_GEOMETRY_FACTs for a document.

    Records ALL vector drawing primitives from page.get_drawings().
    No pre-filter applied — every seqno is recorded (DC3).

    pages: 1-based page references; None = all pages. Output is ordered by
    (page_reference, seqno) — PyMuPDF-declared deterministic emission order.
    """
    import fitz  # sanctioned: independent PyMuPDF API

    ph = params_hash()
    ph_p1 = P1_FROZEN_SHA
    fitz_ver = pymupdf_version()
    geometry_source = "pymupdf:get_drawings"

    out: List[Dict[str, Any]] = []
    doc = fitz.open(pdf_path)
    try:
        page_refs = pages if pages is not None else list(range(1, doc.page_count + 1))
        for pno in sorted(page_refs):
            page = doc[pno - 1]
            drawings = page.get_drawings()
            for d in drawings:
                seqno = d.get("seqno", 0)
                rect = d.get("rect")
                if rect is None:
                    continue  # drawing without rect is not observable
                draw_type = d.get("type", "")
                items = d.get("items", [])
                item_count = len(items)
                item_types = _extract_item_types(items)

                out.append(
                    {
                        "drawing_id": drawing_id_for(document_id, pno, seqno),
                        "fact_kind": FACT_KIND,
                        "document_id": document_id,
                        "page_reference": pno,
                        "bbox": _round_bbox([
                            float(rect.x0), float(rect.y0),
                            float(rect.x1), float(rect.y1),
                        ]),
                        "draw_type": str(draw_type),
                        "item_count": int(item_count),
                        "item_types": item_types,
                        "coordinate_system": COORDINATE_SYSTEM,
                        "source_sha": ph_p1,
                        "params_hash": ph,
                        "schema_version": "1.0.0",
                        "pymupdf_version": fitz_ver,
                        "geometry_source": geometry_source,
                    }
                )
    finally:
        doc.close()
    return out


__all__ = ["enumerate_drawing_geometry", "drawing_id_for", "params_hash",
           "FACT_KIND", "COORDINATE_SYSTEM"]
