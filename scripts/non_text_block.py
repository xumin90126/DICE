"""Atomic Observation Layer v1 — NON_TEXT_BLOCK_ATOM enumeration.

The ONLY new extraction surface sanctioned by the implementation contract
(tmp/atomic_observation_implementation_contract.md section 2.2).

Reads the SAME PyMuPDF "dict" structure that frozen P1
`_extract_block_observations` reads (atomic_text.py:243-256 skips type != 0);
this module records the skipped non-text blocks as structure-only facts.

FORBIDDEN (by contract): any semantic role naming (image/figure/chart/...),
OCR, content recovery, deduplication, arbitration, visual interpretation.

Known limitation (declared, not worked around): vector drawings
(page.get_drawings) are NOT covered by this surface.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from typing import Any, Dict, Iterator, List, Optional

_LAYER_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_LAYER_DIR, "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from perception.sandbox.observations.atomic_text import (  # noqa: E402  (frozen, read-only reuse)
    _round_bbox,
    pymupdf_version,
)

COORDINATE_SYSTEM = "pymupdf_page_1.26.x_y_down"
ATOM_KIND = "NON_TEXT_BLOCK_ATOM"

# Frozen anchor of the shared parse surface (registry-frozen P1 module).
P1_FROZEN_SHA = "74d23ec784d657825780b35627f1b766ad87bd4dd74d88bbe4d560941f3b724a"


def atom_id_for(document_id: str, page_reference: int, block_index: int) -> str:
    """Pure-function atom identity (contract 2.2). No timestamp, no randomness."""
    return f"NTB|{document_id}|p{page_reference}|{block_index}"


def params_hash() -> str:
    """Hash over the registered enumeration definition (no runtime parameters)."""
    definition = json.dumps(
        {
            "surface": "page.get_text('dict').blocks[type != 0]",
            "fields": ["atom_id", "atom_kind", "document_id", "page_reference",
                        "bbox", "pdf_block_type", "content", "coordinate_system",
                        "source_sha", "params_hash", "schema_version",
                        "pymupdf_version", "geometry_source"],
            "content": None,
            "rounding": "frozen _round_bbox",
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(definition.encode("utf-8")).hexdigest()


def enumerate_non_text_blocks(pdf_path: str,
                              document_id: str,
                              pages: Optional[List[int]] = None) -> List[Dict[str, Any]]:
    """Enumerate NON_TEXT_BLOCK_ATOMs for a document.

    pages: 1-based page references; None = all pages. Output is ordered by
    (page_reference, block_index) — PDF-declared deterministic emission order.
    """
    import fitz  # sanctioned: same parse surface as frozen P1

    ph = params_hash()
    ph_p1 = P1_FROZEN_SHA
    fitz_ver = pymupdf_version()
    geometry_source = (
        "frozen:atomic_text.py@" + ph_p1 + " (parse surface only; blocks type!=0, "
        "skipped by frozen P1)"
    )
    out: List[Dict[str, Any]] = []
    doc = fitz.open(pdf_path)
    try:
        page_refs = pages if pages is not None else list(range(1, doc.page_count + 1))
        for pno in sorted(page_refs):
            page = doc[pno - 1]
            raw = page.get_text("dict")
            for block_index, block in enumerate(raw.get("blocks", [])):
                btype = block.get("type", 0)
                if btype == 0:
                    continue  # text blocks are TEXT_ATOM territory (frozen P1)
                out.append(
                    {
                        "atom_id": atom_id_for(document_id, pno, block_index),
                        "atom_kind": ATOM_KIND,
                        "document_id": document_id,
                        "page_reference": pno,
                        "bbox": _round_bbox(block.get("bbox")),
                        "pdf_block_type": btype,
                        "content": None,
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


__all__ = ["enumerate_non_text_blocks", "atom_id_for", "params_hash",
           "ATOM_KIND", "COORDINATE_SYSTEM"]
