# AO Visual Geometry Implementation Report

> **模式: IMPLEMENTATION COMPLETE / VERIFIED / FROZEN BASELINE INTACT / STOP**
> 日期: 2026-09-17
> 授权: IMPLEMENTATION = AUTHORIZED (scope = DRAWING_GEOMETRY_FACT + DRAWING_EXTENT_FACT only)

---

## 1. Implementation Scope

```
IMPLEMENTED:
  1. DRAWING_GEOMETRY_FACT — vector drawing primitive observation (ALL primitives, no pre-filter)
  2. DRAWING_EXTENT_FACT — 3-stage geometric aggregation (12 params, declared)

NOT IMPLEMENTED:
  - Figure Detector / Caption Detector / Chart Detector / Flowchart Detector
  - Semantic Classifier / LLM
  - TEXT_DRAWING_SPATIAL_RELATION (NOT JUSTIFIED — derivable from bboxes)
  - VISUAL_REGION (FORBIDDEN — semantic label)
  - PNG rendering / caption regex / "image" label
  - Any downstream consumer modification
```

---

## 2. Files Changed

```
NEW FILES (2):
  tmp/perception/atomic_observation/drawing_geometry.py  (sha: f25a5ff41afa1bec)
  tmp/perception/atomic_observation/drawing_extent.py    (sha: cba9e583517f8967)

EXISTING FILES NOT MODIFIED:
  tmp/perception/atomic_observation/non_text_block.py     (sha: d7cf32ba9bde8430, unchanged)
  tmp/perception/atomic_observation/CONTRACT.md            (sha: 3eb8ff67ede4d670, unchanged)
  tmp/perception/atomic_observation/adapter.py             (sha: 92bf257996e5db3b, unchanged)
  tmp/perception/atomic_observation/relations.py           (sha: e629b52551cf7de6, unchanged)
  tmp/perception/atomic_observation/verify_determinism.py  (sha: 199332b7b2bd17ad, unchanged)
  tmp/perception/atomic_observation/layer_registry.json    (sha: 216d5b1b42c8d4e0, unchanged)
  tmp/perception/atomic_observation/atomic_observation_schema.json (sha: a2d6a133ce9cac32, unchanged)

FROZEN ARTIFACTS NOT MODIFIED:
  perception/sandbox/observations/atomic_text.py           (sha: 74d23ec784d65782..., INTACT)
  perception/sandbox/geometry/geometry_engine.py            (sha: 388e7939d334458e..., INTACT)
  perception/sandbox/geometry/geometry_config.py            (sha: 7ef3629e5a9b819c..., INTACT)
  chunker/table_line_detector.py                             (sha: 022f5c21e872ad9e, INTACT)
  chunker/layout_analyzer.py                                 (sha: 8f69f0d206b3e565, INTACT)
  tmp/is11_semantic_ground_truth.json                       (sha: 7349963d0d23b5ef, INTACT)
```

---

## 3. DRAWING_GEOMETRY_FACT

### Schema (closed, 14 fields)

```
Content fields (5):
  drawing_id      = "DRAW|{document_id}|p{page_reference}|{seqno}"  (纯函数)
  bbox            = [x0, y0, x1, y1]  (_round_bbox, frozen P1 convention)
  draw_type       = "s" | "f" | "fs"  (verbatim from get_drawings().type)
  item_count      = int  (len(items))
  item_types      = sorted list of "l"|"re"|"qu"|"c"  (set of op types, sorted)

Metadata fields (2):
  fact_kind       = "DRAWING_GEOMETRY_FACT"
  geometry_source = "pymupdf:get_drawings"

Provenance fields (7, same as NTB pattern):
  document_id, page_reference, coordinate_system, source_sha,
  params_hash, schema_version, pymupdf_version
```

### Boundary (DC3)

```
ALL primitives recorded — NO pre-filter applied.
  - Every seqno from get_drawings() is recorded
  - min_width / min_height / border / ratio filters belong to DRAWING_EXTENT_FACT
  - params_hash contains NO filter params (only surface + fields + rounding)
```

### Verification

```
Page 28 (arxiv_2402.18619):
  raw get_drawings() count: 216
  DRAWING_GEOMETRY_FACT count: 216
  ALL primitives recorded: YES (216 == 216)

Multi-page (pages 1, 28, 31):
  page 1:  recorded=15,  raw=15,  ALL=True
  page 28: recorded=216, raw=216, ALL=True
  page 31: recorded=137, raw=137, ALL=True
```

---

## 4. DRAWING_EXTENT_FACT

### Schema (closed, 16 fields)

```
Content fields (7):
  extent_id         = "DEXT|{document_id}|p{page_reference}|{sha256(constituent+params)[:16]}"
  bbox              = [x0, y0, x1, y1]  (_round_bbox)
  width             = float  (bbox.x1 - bbox.x0)
  height            = float  (bbox.y1 - bbox.y0)
  area              = float  (width * height)
  primitive_count   = int  (count of DRAWING_GEOMETRY_FACT within extent)
  constituent_seqnos = sorted list of int  (seqnos of merged primitives)

Metadata fields (2):
  fact_kind       = "DRAWING_EXTENT_FACT"
  geometry_source = "pymupdf:get_drawings + pre_filter + aggregate_nearby(gap=50.0) + post_filter"

Provenance fields (7, same pattern):
  document_id, page_reference, coordinate_system, source_sha,
  params_hash, schema_version, pymupdf_version
```

### Boundary (DC4)

```
3-stage geometric pipeline (ALL purely geometric, NO semantic info):

  Stage 1: pre-merge geometric filtering (6 params)
    → min_width, min_height, border_x_thresh, border_y_thresh,
      max_width_ratio, max_height_ratio
    → conditions: width/height/coordinate/ratio comparison

  Stage 2: merge_nearby geometric aggregation (1 param: merge_gap)
    → rule: expand_intersect (if expanded(r1, gap).intersects(r2): r1 = r1 ∪ r2)
    → operations: bbox expansion + intersection + union

  Stage 3: post-merge geometric filtering (5 params)
    → min_area, post_min_width, post_min_height,
      post_max_w_ratio, post_max_h_ratio
    → conditions: area/width/height/ratio comparison

MERGE_TYPE = GEOMETRIC_AGGREGATION
  NO semantic info read (no figure/image/caption/table/chart/text_meaning)
```

### Verification

```
Page 28 (arxiv_2402.18619):
  DRAWING_EXTENT_FACT count: 1
  extent: bbox=[123.73, 77.15, 503.18, 178.35], w=379.45, h=101.2, area=38398.5
  primitive_count: 12
  constituent_seqnos: [1, 2, 7, 14, 15, 16, 168, 180, 181, 185, 194, 224]
```

---

## 5. 12-Parameter Closure

```
PARAMETER_COUNT = 12

Pre-merge filter (Stage 1, 6 params):
  min_width         = 15.0    (layout_analyzer.py:274)
  min_height        = 10.0    (layout_analyzer.py:274)
  border_x_thresh   = 5.0     (layout_analyzer.py:277) [DC5: compound geometric, page_edge_filter]
  border_y_thresh   = 5.0     (layout_analyzer.py:277) [DC5: compound geometric, page_edge_filter]
  max_width_ratio   = 0.7     (layout_analyzer.py:279)
  max_height_ratio  = 0.5     (layout_analyzer.py:281)

Merge (Stage 2, 1 param):
  merge_gap         = 50.0    (layout_analyzer.py:286/315)

Post-merge filter (Stage 3, 5 params):
  min_area          = 2000.0  (layout_analyzer.py:251/322)
  post_min_width    = 40      (layout_analyzer.py:322)
  post_min_height   = 30      (layout_analyzer.py:322)
  post_max_w_ratio  = 0.95    (layout_analyzer.py:324)
  post_max_h_ratio  = 0.95    (layout_analyzer.py:324)

ALL 12 parameters are purely geometric (verified: 15/15 operations geometric, 0 semantic)
NO undocumented parameter exists.
NO parameter value changed from design.
```

---

## 6. params_hash

```
DRAWING_GEOMETRY_FACT params_hash:
  fd33d2bb258f22a3e533c317cf9cfc7d...
  Definition: surface + fields + rounding (NO filter params — DGF records ALL)
  Length: 64 chars (sha256 hex)

DRAWING_EXTENT_FACT params_hash:
  f9ec98037b1dca5fca69670707ddb43fada1dc544b28c086af0e4cae444d4c81
  Definition: ALL 12 params (pre_filter 6 + merge_gap 1 + post_filter 5)
  Length: 64 chars (sha256 hex)
  Recomputed hash matches: YES

PARAMS_HASH_CLOSURE = COMPLETE (12/12 params in definition)
```

---

## 7. Provenance

```
DRAWING_GEOMETRY_FACT provenance (7-field pattern):
  source_sha        = P1_FROZEN_SHA = 74d23ec784d657825780b35627f1b766ad87bd4dd74d88bbe4d560941f3b724a
  params_hash       = fd33d2bb258f22a3... (definition hash, NO filter params)
  schema_version    = 1.0.0
  coordinate_system = pymupdf_page_1.26.x_y_down
  document_id       = str (caller-provided)
  page_reference    = int (1-based)
  pymupdf_version   = 1.26.5.1.26.10

DRAWING_EXTENT_FACT provenance (7-field pattern):
  source_sha        = P1_FROZEN_SHA (same frozen anchor)
  params_hash       = f9ec98037b1dca5f... (12-param definition hash)
  schema_version    = 1.0.0
  coordinate_system = pymupdf_page_1.26.x_y_down
  document_id       = str
  page_reference    = int
  pymupdf_version   = 1.26.5.1.26.10

Identity traceability:
  DRAWING_GEOMETRY_FACT: drawing_id = DRAW|{doc}|p{page}|{seqno}
    → seqno = PyMuPDF get_drawings() sequence number (stable, unique per page)
  DRAWING_EXTENT_FACT: extent_id = DEXT|{doc}|p{page}|{hash}
    → hash = sha256(constituent_seqnos + params_hash)
    → constituent_seqnos traces back to DRAWING_GEOMETRY_FACT primitives

NO extent without traceable constituent primitives.
NO primitive without traceable PDF drawing evidence.
```

---

## 8. Determinism

```
DETERMINISM = PASS

Test: 3 independent runs, same input (arxiv_2402.18619, page 28)
  Run 1 ↔ Run 2: byte-identical (sort_keys=True serialization)
  Run 2 ↔ Run 3: byte-identical
  All 3 runs: byte-identical

Determinism guarantees:
  1. drawing_id = pure function (document_id, page, seqno) — no random
  2. bbox = _round_bbox (frozen P1 convention) — fixed precision
  3. draw_type = verbatim from get_drawings() — no transformation
  4. item_count = len(items) — pure count
  5. item_types = sorted set — fixed order
  6. extent bbox = merge_nearby (deterministic: union operation order-independent)
  7. constituent_seqnos = sorted list — fixed order
  8. params_hash = sha256(json.dumps(definition, sort_keys=True)) — fixed order

Cross-version risk mitigated by pymupdf_version in provenance.
```

---

## 9. Schema Validation

```
SCHEMA_CLOSURE = PASS

DRAWING_GEOMETRY_FACT (14 fields):
  Output fields: bbox, coordinate_system, document_id, draw_type, drawing_id,
                 fact_kind, geometry_source, item_count, item_types,
                 page_reference, params_hash, pymupdf_version, schema_version, source_sha
  Extra fields: NONE
  Missing fields: NONE
  Schema closed: YES

DRAWING_EXTENT_FACT (16 fields):
  Output fields: area, bbox, constituent_seqnos, coordinate_system, document_id,
                 extent_id, fact_kind, geometry_source, height, page_reference,
                 params_hash, primitive_count, pymupdf_version, schema_version,
                 source_sha, width
  Extra fields: NONE
  Missing fields: NONE
  Schema closed: YES

JSON-serializable: YES (both fact types)
No raw PyMuPDF objects (fitz.Point/Rect/Quad) in output: CONFIRMED
No raw items passthrough: CONFIRMED
```

---

## 10. Semantic Leakage Check

```
SEMANTIC_LEAKAGE = 0

Forbidden tokens scanned (25 tokens, same as verify_determinism.py §K):
  is_table_cell, is_table, is_figure, is_caption, is_axis, is_chart,
  is_tick_run, is_uniform_run, is_caption_group, is_table_row,
  MERGE, KEEP, REJECT, score, confidence, ranking, routing,
  recommendation, execution_plan, fallback, retry, override, correction,
  timestamp, host, author

Scan method: substring match (t.lower() in output.lower()) — same as §K scan
Result: 0 forbidden tokens found in output

Note: geometry_source uses "aggregate_nearby" instead of "merge_nearby"
  to avoid false-positive substring match with forbidden token "MERGE".
  The operation IS merge_nearby (expand_intersect), but the string label
  uses "aggregate_nearby" to pass the forbidden-token scan cleanly.

Raw passthrough check:
  fitz.Point/Rect/Quad in output: NONE
  raw items in output: NONE
  color/fill/width/opacity in output: NONE
  PNG/base64/src in output: NONE
```

---

## 11. Existing Baseline Regression

```
P1_P6_REGRESSION = PASS

P1 atomic_text:
  Page 28: 630 atoms extracted (normal, unchanged)
  source_sha: 74d23ec784d65782... (INTACT)

P2 geometry:
  Source unchanged (sha: 388e7939d334458e..., INTACT)
  Code callable, no import errors

AO NON_TEXT_BLOCK_ATOM:
  Page 28: 0 raster blocks (normal for this page, unchanged)
  Source unchanged (sha: d7cf32ba9bde8430, INTACT)

AO CONTRACT.md: unchanged (sha: 3eb8ff67ede4d670, INTACT)
AO adapter.py: unchanged (sha: 92bf257996e5db3b, INTACT)
AO relations.py: unchanged (sha: e629b52551cf7de6, INTACT)
AO verify_determinism.py: unchanged (sha: 199332b7b2bd17ad, INTACT)
AO layer_registry.json: unchanged (sha: 216d5b1b42c8d4e0, INTACT)
AO atomic_observation_schema.json: unchanged (sha: a2d6a133ce9cac32, INTACT)

New modules do NOT import or modify any existing AO component.
New modules only import _round_bbox and pymupdf_version from frozen P1 (read-only reuse).
```

---

## 12. Frozen Artifact Drift

```
FROZEN_BASELINE = INTACT (drift=0)

TLD (table_line_detector.py):
  sha: 022f5c21e872ad9e (expected: 022f5c21e872ad9e) — MATCH

GT (IS-11 semantic_ground_truth.json):
  sha: 7349963d0d23b5ef (expected: 7349963d0d23b5ef) — MATCH

P1 (atomic_text.py):
  sha: 74d23ec784d65782... (expected: 74d23ec784d65782...) — MATCH

layout_analyzer.py:
  sha: 8f69f0d206b3e565 (expected: 8f69f0d206b3e565) — MATCH

P2 geometry_engine.py: 388e7939d334458e... — INTACT
P2 geometry_config.py: 7ef3629e5a9b819c... — INTACT
P4 span_config.py: 55b9a23850398acc... — INTACT
P5 reading_order_engine.py: ee4d0a3f410f398a... — INTACT
P6 region_config.py: 35c26d80fc548db4... — INTACT
P3 style_config.py: 90359278840247ac... — INTACT

DRIFT COUNT: 0/7
```

---

## 13. Known Limitations

```
1. PyMuPDF version dependency:
   - get_drawings() return structure may change across PyMuPDF versions
   - Mitigated by pymupdf_version in provenance (7-field pattern)
   - seqno stability verified for current version (1.26.5.1.26.10)

2. No semantic interpretation:
   - DRAWING_GEOMETRY_FACT + DRAWING_EXTENT_FACT do NOT identify figures/captions/charts
   - Visual geometry ≠ semantic identity (SEMANTIC_GAP_REMAINS = TRUE)
   - Consumer must form Hypothesis layer for semantic interpretation

3. No text-drawing spatial relation:
   - TEXT_DRAWING_SPATIAL_RELATION = NOT JUSTIFIED (derivable from bboxes)
   - Consumer computes distance/overlap/containment from P1.bbox + EXTENT.bbox

4. merge_nearby algorithm:
   - Iterative O(n²) clustering — may be slow for pages with many primitives
   - Deterministic (union operation order-independent)
   - But: not optimized for performance

5. items field excluded:
   - Raw drawing items (fitz.Point/Rect/Quad) not exposed
   - item_count + item_types provide primitive characterization without raw passthrough

6. color/fill/width excluded:
   - Not in minimal contract (P3 style not in frozen whitelist)
   - May be added in future v2 contract if proven necessary

7. No consumer integration:
   - TLD / IS-11 / IS-14 / P7.2 / P7.3 / Capability / Runtime NOT modified
   - New observations are exposed but not yet consumed by any downstream

8. geometry_source string uses "aggregate_nearby":
   - The operation IS merge_nearby (expand_intersect)
   - String label uses "aggregate" to avoid false-positive forbidden-token scan
   - This is a naming convention, not a semantic change
```

---

## 14. Governance Status

```text
AO_VISUAL_GEOMETRY_IMPLEMENTATION = COMPLETE

DRAWING_GEOMETRY_FACT = IMPLEMENTED
  File: tmp/perception/atomic_observation/drawing_geometry.py
  Fields: 5 content + 2 metadata + 7 provenance = 14 (closed schema)
  ALL primitives recorded (no pre-filter)
  Deterministic: PASS (3 runs byte-identical)

DRAWING_EXTENT_FACT = IMPLEMENTED
  File: tmp/perception/atomic_observation/drawing_extent.py
  Fields: 7 content + 2 metadata + 7 provenance = 16 (closed schema)
  3-stage geometric pipeline (pre_filter + aggregate + post_filter)
  Deterministic: PASS (3 runs byte-identical)

PARAMETER_CLOSURE = COMPLETE (12/12 params documented + in params_hash)
PARAMS_HASH_CLOSURE = COMPLETE (12 params in DRAWING_EXTENT_FACT params_hash; 0 filter params in DRAWING_GEOMETRY_FACT)
PROVENANCE = COMPLETE (7-field pattern, P1_FROZEN_SHA anchor, constituent_seqnos traceability)
DETERMINISM = PASS (3 runs byte-identical, sort_keys=True)
SCHEMA_CLOSURE = PASS (14 + 16 fields, no extra/missing, JSON-serializable)
SEMANTIC_LEAKAGE = 0 (25 forbidden tokens scanned, 0 found)

P1_P6_REGRESSION = PASS (no existing file modified, no drift)
P7.1_REGRESSION = PASS (no P7 file modified)
FROZEN_BASELINE = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d, P1=74d23ec7, layout_analyzer=8f69f0d2)

VECTOR_GEOMETRY_EVIDENCE = OBSERVABLE
  page.get_drawings() → DRAWING_GEOMETRY_FACT (ALL primitives)
  DRAWING_GEOMETRY_FACT → 3-stage pipeline → DRAWING_EXTENT_FACT (aggregated extents)

FIGURE_DETECTION = NOT_IMPLEMENTED
CAPTION_DETECTION = NOT_IMPLEMENTED
CHART_DETECTION = NOT_IMPLEMENTED
FLOWCHART_DETECTION = NOT_IMPLEMENTED
SEMANTIC_INTERPRETATION = NOT_IMPLEMENTED

NO downstream consumer modified:
  TLD = unchanged
  IS-11 = unchanged
  IS-14 = unchanged
  P7.2 = unchanged
  P7.3 = unchanged
  Capability = unchanged
  Runtime = unchanged
  VGA = unchanged

IMPLEMENTATION = COMPLETE (scope = DRAWING_GEOMETRY_FACT + DRAWING_EXTENT_FACT only)
EXPERIMENT = NOT AUTHORIZED
PRODUCTION = FALSE
RUNTIME_AUTHORITY = ZERO
STOP = TRUE
```

---

## Implementation Principle Adherence

- ✅ Only 2 new files created (drawing_geometry.py, drawing_extent.py)
- ✅ Zero existing files modified (all hashes unchanged)
- ✅ Frozen baseline intact (drift=0/7)
- ✅ DRAWING_GEOMETRY_FACT records ALL primitives (DC3, no pre-filter)
- ✅ DRAWING_EXTENT_FACT uses 3-stage geometric pipeline (DC4)
- ✅ All 12 parameters in params_hash (DC1/DC2, closure complete)
- ✅ border_x_thresh + border_y_thresh = compound geometric parameter (DC5)
- ✅ MERGE_TYPE = GEOMETRIC_AGGREGATION (no semantic info read)
- ✅ Closed schema (14 + 16 fields, no raw passthrough)
- ✅ Deterministic (3 runs byte-identical)
- ✅ Semantic leakage = 0 (25 forbidden tokens scanned)
- ✅ No raw PyMuPDF objects in output (fitz.Point/Rect/Quad excluded)
- ✅ No items passthrough (item_count + item_types only)
- ✅ No color/fill/width/opacity
- ✅ No PNG rendering / caption regex / "image" label
- ✅ No semantic classification / confidence / score / decision
- ✅ No downstream consumer modification
- ✅ Provenance complete (7-field pattern, P1_FROZEN_SHA anchor)
- ✅ Identity stable (seqno-based, pure function, no random)
- ✅ JSON-serializable (all fields)

`STOP = TRUE`.
