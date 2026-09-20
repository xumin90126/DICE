"""
Phase 30: CAP-TABLE-CELL-SEGMENT — L1 Structural Table Capability (segmenter).

This module implements the DETERMINISTIC, GEOMETRY-ONLY cell segmenter of the
first L1 structural table capability. It is the implementation artifact of
Phase 30 (IMPLEMENTATION AUTHORIZED), following Phase 28 Contract Freeze and
Phase 29 Registration Review.

Responsibility (Phase 28 §Determinism Freeze — YES):
    Given a Human-confirmed table_region_reference and a merged text block
    (a single table column collapsed into ONE block by layout-first PDF
    slicing), segment the block into individual CELL observations.

    Allowed deterministic operations:
        - row boundary detection  (split merged text by line boundaries)
        - merged-cell geometric split (proportional bbox slice per row)
        - column_index echo       (Human-confirmed, default 0)
        - cell identity generation (deterministic cell_id)

    Forbidden (Phase 28 §Determinism Freeze — NO, and Phase 30 boundary):
        - header interpretation / column meaning inference
        - row matching / cell joining
        - fact generation / value extraction / unit extraction
        - semantic association
        - table recognition / automatic table region detection

CRITICAL BOUNDARY (Phase 27 F-3): table region identification remains
Human-assisted. This segmenter NEVER detects a table region; it only segments
a block that Human has ALREADY confirmed as a table region. The
`table_region_reference` is supplied by Human; the segmenter echoes it.

SEGMENTATION ALGORITHM (deterministic, zero semantic):
    1. Split the merged block text on line boundaries ("\\n"). Each
       non-empty line is ONE row (one cell). A blank line is a geometric
       artifact and is skipped (it never carries content).
    2. Assign each cell:
         - row_index     = 0-based line ordinal (among non-empty lines)
         - column_index  = the Human-confirmed column index (default 0)
         - raw_text      = the line's raw text (verbatim, NOT interpreted)
         - cell_id       = f"{region}::r{row}c{col}" (deterministic identity)
         - bbox          = proportional geometric slice of the block bbox
    3. The bbox slice is a PURE GEOMETRIC interpolation: the block height
       (y0..y1) is divided into N equal horizontal bands (N = number of
       non-empty rows); the i-th cell spans [x0, y0 + i*dy, x1, y0 + (i+1)*dy].
       This is geometry-only: it records WHERE the cell lies, never WHAT it
       means. (Faithful per-line bboxes require re-reading the PDF; this
       segmenter is geometry-only and does not re-read the source.)

Zero authority: no matcher/selector/router/ranking/scoring/executor/decision.
No span_type, no capability selection, no LLM, no semantic reasoning.

Imports: stdlib only (dataclasses / typing). Zero external dependencies —
the segmenter consumes already-extracted block text/bbox, it does NOT parse
PDFs (unlike CandidateSpanGenerator, which owns PDF access).

Invariants enforced by construction on OUTPUT (I-1 ~ I-5) via
TableCellObservation defaults.
"""

from __future__ import annotations

from typing import List, Optional

from .models import SegmentationResult, TableCellObservation


class TableCellSegmenter:
    """Deterministic, geometry-only, zero-authority cell segmenter.

    Segments a Human-confirmed merged table block into per-row cell
    observations. It performs ONLY geometric/structural splitting (line
    split + proportional bbox slice) and NEVER interprets meaning.

    Usage (Human-driven, per call):
        segmenter = TableCellSegmenter()
        result = segmenter.segment(
            table_region_reference="RA101::components",
            span_text="10 μl\\n5 μl\\n20 μl",
            bbox=[333.1, 224.2, 364.1, 373.8],
            column_index=0,
        )
        for cell in result.cells:
            ...  # TableCellObservation (six structural fields)
    """

    def segment(
        self,
        table_region_reference: str,
        span_text: str,
        bbox: Optional[List[float]] = None,
        column_index: int = 0,
    ) -> SegmentationResult:
        """Segment a merged block into per-row cell observations.

        Args:
            table_region_reference: Human-confirmed table region identity
                (fact; echoed verbatim, NEVER detected).
            span_text: the merged block text (raw, newline-separated rows).
            bbox: the block bounding box [x0, y0, x1, y1] (optional; empty
                when geometry unavailable).
            column_index: the Human-confirmed column index of this block
                (fact; default 0).

        Returns:
            SegmentationResult (cell list + structural provenance facts).
        """
        region = table_region_reference if isinstance(table_region_reference, str) else ""
        text = span_text if isinstance(span_text, str) else ""
        col = column_index if isinstance(column_index, int) else 0

        # ── Step 1: row boundary detection (line split) ──
        # Each non-empty line is one row. Blank lines are geometric artifacts
        # (never content) and are skipped. NO interpretation of line meaning.
        rows = [ln.rstrip("\r") for ln in text.split("\n")]
        rows = [ln for ln in rows if ln.strip()]

        # ── Step 2: proportional geometric bbox slice (geometry-only) ──
        # Divide the block height into N equal horizontal bands. This records
        # WHERE each cell lies; it NEVER infers what a cell means.
        cell_bboxes: List[List[float]] = []
        n = len(rows)
        valid_bbox = (
            isinstance(bbox, list)
            and len(bbox) == 4
            and all(isinstance(v, (int, float)) for v in bbox)
        )
        if valid_bbox and n > 0:
            x0, y0, x1, y1 = float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])
            height = y1 - y0
            if height > 0:
                step = height / n
                for i in range(n):
                    cell_bboxes.append([
                        round(x0, 2),
                        round(y0 + i * step, 2),
                        round(x1, 2),
                        round(y0 + (i + 1) * step, 2),
                    ])
            else:
                # Zero-height block: every cell shares the degenerate bbox.
                cell_bboxes = [[round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)] for _ in range(n)]
        else:
            # Geometry unavailable: honest empty bbox per cell (no fabrication).
            cell_bboxes = [[] for _ in range(n)]

        # ── Step 3: assemble cell observations (six structural fields) ──
        cells: List[TableCellObservation] = []
        for i, raw_text in enumerate(rows):
            cells.append(TableCellObservation(
                table_region_reference=region,
                cell_id=self._cell_id(region, i, col),
                row_index=i,
                column_index=col,
                raw_text=raw_text,
                bbox=cell_bboxes[i] if i < len(cell_bboxes) else [],
            ))

        return SegmentationResult(
            cells=cells,
            table_region_reference=region,
            row_count=n,
            column_index=col,
        )

    # ────────────────────────────────────────────────────────────────────
    # Private helpers (deterministic, no decision)
    # ────────────────────────────────────────────────────────────────────

    @staticmethod
    def _cell_id(region: str, row_index: int, column_index: int) -> str:
        """Deterministic cell identity (fact; never a classification)."""
        return f"{region}::r{row_index}c{column_index}"


__all__ = [
    "TableCellSegmenter",
]
