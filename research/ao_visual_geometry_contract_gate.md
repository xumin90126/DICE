# AO Visual Geometry Contract Gate — Final Design Review

> **模式: READ-ONLY / FINAL DESIGN GATE / NO IMPLEMENTATION / NO EXPERIMENT / FROZEN INTACT / STOP**
> 日期: 2026-09-17
> 前置: `tmp/visual_observation_surface_design_research.md` + `tmp/ao_visual_geometry_contract_design.md`
> 本文件对 DRAWING_GEOMETRY_FACT + DRAWING_EXTENT_FACT 设计执行最终 Gate 审查。

---

## 1. Gate Purpose

审查一个核心问题:

> DRAWING_EXTENT_FACT 中的 geometric aggregation 是否仍然属于合法 Observation？

即:

```
多个 drawing primitives
        ↓
纯几何 merge rule
        ↓
一个 aggregated extent
```

是否满足 `Observation ≠ Interpretation`？

同时执行 10 个 Gate (G1-G10) 对整个候选 Contract 做最终审查。

---

## 2. Existing Design Baseline

```
ARCHITECTURE_PLACEMENT = ATOMIC_OBSERVATION

Candidate Facts:
  DRAWING_GEOMETRY_FACT (5 content fields):
    drawing_id, bbox, draw_type, item_count, item_types

  DRAWING_EXTENT_FACT (6 content fields):
    extent_id, bbox, width, height, area, primitive_count, constituent_seqnos

  TEXT_DRAWING_SPATIAL_RELATION = NOT JUSTIFIED (derivable from bboxes)

FIELD_CLOSURE = SUPPORTED (closed allowlist schema)
SEMANTIC_GAP_REMAINS = TRUE
```

---

## 3. G1 — DRAWING_GEOMETRY_FACT

### 逐字段确认

| 字段 | 来自真实底层 evidence? | Deterministic? | Closed schema? | 包含 semantic interpretation? | 与 P2/P6 重复? |
|------|----------------------|----------------|----------------|-------------------------------|----------------|
| drawing_id | YES — `(doc, page, seqno)` 纯函数 | YES — 无随机/timestamp | YES — 固定格式 | NO | NO |
| bbox | YES — `get_drawings().rect` | YES — `_round_bbox` (frozen P1) | YES | NO (纯坐标) | NO (P2=text, this=non-text) |
| draw_type | YES — `get_drawings().type` verbatim | YES — 无变换 | YES — `"s"/"f"/"fs"` 枚举 | NO (stroke/fill ≠ figure) | NO |
| item_count | YES — `len(get_drawings().items)` | YES — 纯计数 | YES — int | NO | NO |
| item_types | YES — `set(op[0] for op in items)` | YES — sorted set | YES — `"l"/"re"/"qu"/"c"` 枚举 | NO (op type ≠ shape type) | NO |

### 验证

```
[OBSERVED] rect present in 216/216 drawings → bbox always available
[OBSERVED] type present in 216/216 → draw_type always available
[OBSERVED] items present in 216/216 → item_count + item_types always available
[OBSERVED] seqno stable across calls, unique per page → drawing_id stable
```

### 判定

```
G1 = PASS

理由:
  - 全部 5 字段来自 get_drawings() 真实底层 evidence
  - 全部 deterministic (纯函数 / verbatim / 纯计数)
  - closed schema (固定字段集, 枚举类型)
  - 无 semantic interpretation (stroke/fill/line/rect 是 PDF primitive type, 非 semantic shape)
  - 不与 P2 (text geometry) / P6 (text-span region) 重复
```

---

## 4. G2 — DRAWING_EXTENT_FACT

### 逐字段确认

| 字段 | 来自真实底层 evidence? | Deterministic? | Closed schema? | 包含 semantic? | 与 P2/P6 重复? |
|------|----------------------|----------------|----------------|----------------|----------------|
| extent_id | YES — `hash(constituent_seqnos + params)` | YES | YES | NO | NO |
| bbox | YES — merge_nearby output | YES [OBSERVED] | YES | NO (纯坐标) | NO |
| width | YES — `bbox.x1 - bbox.x0` | YES | YES | NO | NO |
| height | YES — `bbox.y1 - bbox.y0` | YES | YES | NO | NO |
| area | YES — `width * height` | YES | YES | NO | NO |
| primitive_count | YES — count of primitives in extent | YES | YES | NO | NO |
| constituent_seqnos | YES — sorted list of seqnos | YES | YES | NO (identity trace) | NO |

### 判定

```
G2 = PASS

理由:
  - 全部 7 字段来自 merge_nearby 的纯几何聚合
  - merge deterministic [OBSERVED: 两次调用结果逐项一致]
  - closed schema (固定字段集)
  - 无 semantic interpretation (extent 是 aggregated bbox, 非 "figure region")
  - 不与 P2 (text geometry) / P6 (text-span region) 重复
  - constituent_seqnos 提供 identity trace (可追溯到 DRAWING_GEOMETRY_FACT)
```

---

## 5. G3 — Merge Rule Boundary

### A: 输入是否全部是纯几何事实？

```
[OBSERVED — 代码逐行审计, layout_analyzer.py:268-324]

merge_nearby 的全部 15 个操作:

  L269  get_drawings()           → GEOMETRIC (返回 rect/type/items)
  L273  rect = d["rect"]         → GEOMETRIC (bbox)
  L274  rect.width < 15          → GEOMETRIC (width comparison)
  L274  rect.height < 10         → GEOMETRIC (height comparison)
  L277  rect.x0 <= 5             → GEOMETRIC (x-coordinate)
  L277  rect.y0 <= 5             → GEOMETRIC (y-coordinate)
  L279  rect.width > pw * 0.7    → GEOMETRIC (width ratio)
  L281  rect.height > ph * 0.5   → GEOMETRIC (height ratio)
  L305  expanded = Rect(r-gap..)  → GEOMETRIC (bbox expansion)
  L307  expanded.intersects(r2)  → GEOMETRIC (bbox intersection)
  L308  r = r | r2               → GEOMETRIC (bbox union)
  L321  area = width * height    → GEOMETRIC (area calc)
  L322  area >= min_area         → GEOMETRIC (area threshold)
  L322  rect.width > 40          → GEOMETRIC (width threshold)
  L324  rect.width < pw * 0.95   → GEOMETRIC (width ratio)

  输入类型: bbox, width, height, area, coordinate, distance, intersection
  全部纯几何: YES (15/15)
```

### B: 是否读取语义信息？

```
读取 figure/image/caption/table/chart/text_meaning/semantic_role 的操作: 0

  merge_nearby 不读取:
    - text content (不调用 get_text)
    - figure/caption labels (不调用 regex)
    - image classification (不调用 detector)
    - semantic role (不查询 P6 region_type)
    - PNG rendering (不调用 get_pixmap)

  merge_nearby 只读取:
    - rect (bbox)
    - width, height (size)
    - area (derived from width/height)
    - page_rect (page dimensions)
    - spatial intersection (bbox overlap)
```

### 判定

```
G3 = PASS

MERGE_TYPE = GEOMETRIC_AGGREGATION

  输入: 纯 bbox list (来自 DRAWING_GEOMETRY_FACT)
  规则: expand_intersect (if expanded(r1, gap).intersects(r2): r1 = r1 ∪ r2)
  输出: merged bbox list (aggregated extent)
  语义分组: NONE

  merge_nearby 满足 Observation ≠ Interpretation:
    - 只做几何聚合 (空间近邻 → bbox union)
    - 不做语义分组 ("这些属于同一 figure")
    - 不做内容判断 ("这是 image/table/chart")
    - 不做词法推断 ("FIG prefix → caption")
```

---

## 6. G4 — Merge Parameter Closure

### 从真实代码中提取的全部参数

```
[OBSERVED — layout_analyzer.py:268-324, 逐行提取]

PRE-MERGE FILTER (lines 272-283):
  1.  min_width         = 15.0    (L274: rect.width < 15)
  2.  min_height        = 10.0    (L274: rect.height < 10)
  3.  border_x_thresh   = 5.0     (L277: rect.x0 <= 5)
  4.  border_y_thresh   = 5.0     (L277: rect.y0 <= 5)
  5.  max_width_ratio   = 0.7     (L279: rect.width > page_rect.width * 0.7)
  6.  max_height_ratio  = 0.5     (L281: rect.height > page_rect.height * 0.5)

MERGE (line 286/315):
  7.  merge_gap         = 50.0    (L286/315: gap=50)

POST-MERGE FILTER (lines 320-324):
  8.  min_area          = 2000.0  (L251/322: area >= min_area)
  9.  post_min_width    = 40      (L322: rect.width > 40)
  10. post_min_height   = 30      (L322: rect.height > 30)
  11. post_max_w_ratio  = 0.95    (L324: rect.width < page_rect.width * 0.95)
  12. post_max_h_ratio  = 0.95    (L324: rect.height < page_rect.height * 0.95)

TOTAL: 12 parameters
```

### 参数几何性验证

```
ALL 12 parameters are purely geometric:
  - width/height comparisons (6 params)
  - coordinate comparisons (2 params)
  - area threshold (1 param)
  - distance threshold (1 param)
  - ratio thresholds (2 params)

NO parameter reads semantic info.
```

### 与前序设计的对比

```
前序设计 (ao_visual_geometry_contract_design.md §8 Q3) 列出的参数:
  merge_gap, min_w, min_h, max_w_ratio, max_h_ratio, min_area = 6 params

真实代码中的参数:
  12 params (see above)

MISSING from design: 6 params
  - border_x_thresh (5.0)
  - border_y_thresh (5.0)
  - post_min_width (40)
  - post_min_height (30)
  - post_max_w_ratio (0.95)
  - post_max_h_ratio (0.95)
```

### 判定

```
G4 = INCOMPLETE

PARAMETER_CLOSURE = INCOMPLETE

理由:
  - 真实代码有 12 个参数影响 merge/extent 输出
  - 前序设计只列出了 6 个
  - 6 个参数未声明 (border_x, border_y, post_min_w, post_min_h, post_max_w_ratio, post_max_h_ratio)
  - 如果实现时遗漏这 6 个参数 → params_hash 不完整 → deterministic replay 不可复现
  - 这 6 个参数全部是纯几何的 (可以声明), 但当前设计未声明

修复要求:
  所有 12 个参数 MUST 在 params_hash 中声明:
    params_hash = sha256({
      "surface": "pymupdf:get_drawings",
      "merge_rule": "expand_intersect",
      "pre_filter": {
        "min_width": 15.0, "min_height": 10.0,
        "border_x_thresh": 5.0, "border_y_thresh": 5.0,
        "max_width_ratio": 0.7, "max_height_ratio": 0.5
      },
      "merge_gap": 50.0,
      "post_filter": {
        "min_area": 2000.0,
        "min_width": 40, "min_height": 30,
        "max_width_ratio": 0.95, "max_height_ratio": 0.95
      },
      "rounding": "frozen _round_bbox"
    })
```

---

## 7. G5 — Semantic Grouping Boundary

### 核心测试: merge 是否制造了"对象"？

```
假设:
  A (seqno=1, bbox=[185,77,255,177])
  B (seqno=2, bbox=[124,82,290,158])
  C (seqno=3, bbox=[138,174,288,177])

经过 merge_nearby(gap=50):
  A + B + C → Extent X (bbox=[124,77,290,177])

Extent X 声明什么?
  extent_id = "DEXT|doc|p28|{hash([1,2,3] + params)}"
  bbox = [124, 77, 290, 177]
  primitive_count = 3
  constituent_seqnos = [1, 2, 3]

Extent X 不声明什么?
  ❌ "A, B, C 属于同一个 Figure"
  ❌ "Extent X 是一个 visual region"
  ❌ "Extent X 是一个 image"
  ❌ "A, B, C 是 figure 的组成部分"
  ❌ "Extent X 的 semantic_role = figure"
```

### 判定

```
G5 = PASS

OBJECT_SEMANTIC_LEAKAGE = FALSE

理由:
  - Extent 只声明: "这些 primitive 根据预先声明的几何 aggregation rule
    (expand_intersect, gap=50) 形成了一个 aggregated extent"
  - Extent 不声明: "这些 primitive 属于同一个 Figure"
  - extent_id = 纯函数 (constituent_seqnos + params_hash), 无 semantic
  - bbox = merged bbox (纯坐标), 无 semantic
  - primitive_count = 纯计数, 无 semantic
  - constituent_seqnos = identity trace (可追溯), 无 semantic

  Observation 声明的是 "geometric aggregation result", 不是 "semantic object"。
  Consumer 可以基于 extent 形成 hypothesis ("这可能是 figure"),
  但 Observation 本身不产生 semantic identity。
```

---

## 8. G6 — Extent Storage Decision

### Option A: 只保存 DRAWING_GEOMETRY_FACT, Consumer 自己计算 extent

```
优点:
  - 最小 schema (只有 1 个 fact type)
  - 无 merge 依赖 (consumer 自行实现 merge)
  - 无参数声明负担 (consumer 选择自己的 params)

缺点:
  - merge_nearby 是非平凡算法 (迭代聚类, O(n²) per iteration)
  - primitive_count + constituent_seqnos 不可平凡派生 (需运行 merge 才知道哪些 primitive 被合并)
  - 如果 consumer 使用不同 params → 不同 extent → 不可复现
  - 每个 consumer 必须重新实现 merge_nearby → 代码重复
  - 无稳定 reusable evidence (每次查询都要重算)
```

### Option B: 保存 DRAWING_GEOMETRY_FACT + DRAWING_EXTENT_FACT

```
优点:
  - extent 是 stable reusable fact (同 input + 同 params → 同 output, deterministic [OBSERVED])
  - primitive_count + constituent_seqnos 是 merge 产物 (不可平凡派生)
  - params 声明在 params_hash → 可复现
  - consumer 可直接查询 extent, 无需重算
  - 与 GAP_SEQUENCE 模式一致 (AO 已存储非平凡 measurement)

缺点:
  - 增加 1 个 fact type → schema 复杂度增加
  - 依赖 merge params → params 变化时 extent 需重算
  - post-merge size filter (min_area, min_width, min_height) 是 selection criteria
```

### 与现有 AO 模式对比

```
GAP_SEQUENCE (AO §4):
  - 存储: YES (seq, a_id, b_id, gap)
  - 计算: 非平凡 (same_y_band grouping + gap extraction + sorting)
  - 参数: 冻结 P2 函数 (frozen dependency)
  - 理由: "measurement, 不是 classifier"

DRAWING_EXTENT_FACT:
  - 存储: 候选 YES
  - 计算: 非平凡 (filter + merge_nearby iterative clustering + filter)
  - 参数: 新代码 (非 frozen, 需 source_sha)
  - 理由: geometric aggregation, 不是 detector

类比:
  GAP_SEQUENCE = grouping (same_y_band) + measurement (gap) + sorting
  DRAWING_EXTENT = filter + merge (expand_intersect) + filter
  两者都是 "非平凡 computation + 参数声明 + stored result"
```

### 关键问题: post-merge size filter 是否让 AO 变成 layout detector？

```
post-merge filter:
  min_area=2000, min_width=40, min_height=30, max_w_ratio=0.95, max_h_ratio=0.95

这是 SIZE filter (面积/宽度/高度), 不是 semantic classification:
  - 不输出 "figure" / "table" / "image" label
  - 不调用 detector / classifier / LLM
  - 不做 content recovery / regex match
  - 只做 numeric comparison (area >= 2000)

与 P2 对比:
  P2 overlap_tolerance = 0.5 → "Overlap values below this are treated as 0"
  → 也是 numeric filter, 非语义

  DRAWING_EXTENT min_area = 2000 → "Extents with area < 2000 are not recorded"
  → 同样是 numeric filter, 非语义

但:
  min_area=2000 的选择受语义目标影响 ("找 figures/diagrams")
  → 这是 INDIRECT semantic influence (阈值选择的动机), 不是 DIRECT semantic output
  → 阈值本身是 declared param (在 params_hash)
  → consumer 知道 filter 存在, 可自行调整

结论: post-merge filter 是 declared geometric selection, 非 semantic detection
  → 不让 AO 变成 layout detector
  → 但: DRAWING_GEOMETRY_FACT 记录 ALL primitives (无 filter), 提供 raw observation
  → DRAWING_EXTENT_FACT 记录 filtered + merged extents (params declared)
  → 两者共存: raw observation + aggregated measurement
```

### 判定

```
G6 = PASS

EXTENT_STORAGE = JUSTIFIED

理由:
  1. merge_nearby 是非平凡算法 (迭代聚类), 非 trivial bbox arithmetic
  2. primitive_count + constituent_seqnos 是 merge 产物, 不可平凡派生
  3. 同 input + 同 params → 同 output (deterministic [OBSERVED])
  4. 与 GAP_SEQUENCE 模式一致 (AO 已存储非平凡 measurement)
  5. post-merge filter 是 declared geometric selection, 非 semantic detection
  6. DRAWING_GEOMETRY_FACT (all primitives) + DRAWING_EXTENT_FACT (filtered+merged) 共存
  7. 不让 AO 变成 layout detector (无 semantic label, 无 detector call)

条件:
  - ALL 12 params MUST be in params_hash (当前 INCOMPLETE, 见 G4)
  - DRAWING_GEOMETRY_FACT MUST record ALL primitives (无 pre-filter)
  - DRAWING_EXTENT_FACT MUST declare all filter params
```

---

## 9. G7 — Identity

### seqno 验证

```
[OBSERVED]
  seqno stable across calls: YES (同页同 PDF, 两次 get_drawings() 结果逐项一致)
  seqno unique per page: YES (1-253, no duplicates)
  seqno present in all drawings: YES (216/216)

来源: PyMuPDF get_drawings() 返回的 sequence number
  - 是 PyMuPDF 对 page content stream 中 drawing 操作的枚举序号
  - 不是 PDF 原生字段 (PDF 不直接存储 drawing seqno)
  - 但: 是 PyMuPDF 确定性解析的产物 (同 PDF + 同 PyMuPDF version → 同 seqno)

跨版本风险:
  - PyMuPDF 版本变化 → content stream 解析顺序可能变化 → seqno 可能变化
  - 缓解: pymupdf_version 在 7-field provenance 中 (与 NTB pattern 一致)
```

### drawing_id 稳定性

```
drawing_id = "DRAW|{document_id}|p{page_reference}|{seqno}"

  document_id: 稳定 (文件级)
  page_reference: 稳定 (页码)
  seqno: 稳定 (同 PyMuPDF version)
  pymupdf_version: 在 provenance 中

  → identity 稳定 (同 PDF + 同 PyMuPDF version)
  → 跨版本变化可检测 (pymupdf_version 不匹配 → identity 不兼容)
```

### extent_id 稳定性

```
extent_id = "DEXT|{document_id}|p{page_reference}|{hash(constituent_seqnos + params_hash)[:16]}"

  constituent_seqnos: 来自 DRAWING_GEOMETRY_FACT (稳定, 同上)
  params_hash: 来自 declared params (稳定, 除非 params 变化)

  → identity 稳定 (同 primitives + 同 params)
  → params 变化 → params_hash 变化 → extent_id 变化 (正确行为)
```

### 与 NTB 对比

```
NTB identity: "NTB|{doc}|p{page}|{block_index}"
  block_index = PyMuPDF get_text("dict") 的 block 枚举序号
  同样是 PyMuPDF 确定性解析产物
  同样有跨版本风险
  同样用 pymupdf_version 缓解

DRAWING identity: "DRAW|{doc}|p{page}|{seqno}"
  seqno = PyMuPDF get_drawings() 的 drawing 枚举序号
  与 NTB pattern 完全一致

→ IDENTITY pattern consistent with existing AO
```

### 判定

```
G7 = PASS

IDENTITY = STABLE

理由:
  - seqno stable across calls [OBSERVED]
  - seqno unique per page [OBSERVED]
  - drawing_id = 纯函数 (doc, page, seqno), 无随机
  - extent_id = 纯函数 (constituent_seqnos + params_hash), 无随机
  - 跨版本风险由 pymupdf_version 缓解 (与 NTB pattern 一致)
  - 不发明新的 hash/id 算法 (复用现有 AO pattern)
```

---

## 10. G8 — Contract Closure

### Closed Schema 检查

```
DRAWING_GEOMETRY_FACT:
  Content fields (5): drawing_id, bbox, draw_type, item_count, item_types
  Provenance fields (7): document_id, page_reference, coordinate_system,
    source_sha, params_hash, schema_version, pymupdf_version
  geometry_source: "pymupdf:get_drawings"

  Closed: YES (固定 12 字段, 无 arbitrary fields)
  Forbidden: items, color, fill, width, opacity, closePath, dashes, ...
```

```
DRAWING_EXTENT_FACT:
  Content fields (7): extent_id, bbox, width, height, area,
    primitive_count, constituent_seqnos
  Provenance fields (7): same pattern
  geometry_source: "pymupdf:get_drawings + merge_nearby(gap=declared)"

  Closed: YES (固定 14 字段, 无 arbitrary fields)
  Forbidden: density, is_figure, is_visual_region, visual_complexity, ...
```

### Forbidden Semantics 检查

```
[验证: 候选 schema 中是否包含任何 forbidden semantics]

  is_figure:      NO (不在字段中)
  is_chart:       NO
  is_table:       NO
  is_flowchart:   NO
  is_caption:     NO
  caption_of:     NO
  figure_of:      NO
  chart_of:       NO
  belongs_to_figure: NO
  semantic_role:  NO
  visual_role:    NO
  confidence:     NO
  score:          NO
  ranking:        NO
  decision:       NO
  recommendation: NO
  selection:      NO
  routing:        NO
  fallback:       NO
  override:       NO
  authority:      NO

  → ZERO forbidden semantics in candidate schema
```

### Raw Payload 绕过风险

```
  raw_pymupdf_drawing_dict: FORBIDDEN (不在 schema 中)
  raw_items: FORBIDDEN (不在 schema 中)
  raw_layout_analyzer_dict: FORBIDDEN (不在 schema 中)
  raw_detector_output: FORBIDDEN (不在 schema 中)

  → 无法通过 raw payload 绕过 closed schema
  → consumer 只能读取 declared fields
```

### 判定

```
G8 = PASS

FIELD_CLOSURE = SUPPORTED

理由:
  - Closed schema (固定字段集, allowlist)
  - 无 raw passthrough (items/color/fill/width 排除)
  - ZERO forbidden semantics in schema
  - verify_determinism.py §K 扫描可扩展覆盖新 fact types
  - 与 NTB/RegionFact/Relations 的 closed schema pattern 一致
```

---

## 11. G9 — P2 / P6 / AO Anti-Duplication

### 逐层对比

```
P2 GeometryObservation:
  Input: TEXT atoms (from P1)
  Fields: same_y_band, h_gap, v_gap, left_alignment_group, same_x_band,
          center_x, center_y, normalized_x/y
  Surface: text span pairwise/single geometry
  → 只处理 TEXT, 不处理 drawing

P6 RegionObservation:
  Input: P4 spans + P5 column layout (TEXT spans)
  Types: PAGE_TOP/BOTTOM/FULL_WIDTH/COLUMN/DENSE/SPARSE/UNKNOWN
  Surface: text-span-based geometric region
  → 只处理 TEXT spans, 不处理 drawing

AO NON_TEXT_BLOCK_ATOM:
  Input: page.get_text("dict").blocks[type != 0]
  Covers: RASTER IMAGE blocks (type=1)
  Fields: atom_id, bbox, pdf_block_type, content=null
  Surface: raster non-text block
  → 只覆盖 raster, 不覆盖 vector

AO DRAWING_GEOMETRY_FACT (candidate):
  Input: page.get_drawings()
  Covers: VECTOR DRAWING primitives
  Fields: drawing_id, bbox, draw_type, item_count, item_types
  Surface: vector drawing primitive
  → 只覆盖 vector, 不覆盖 raster

AO DRAWING_EXTENT_FACT (candidate):
  Input: DRAWING_GEOMETRY_FACT (merged)
  Covers: VECTOR DRAWING aggregated extent
  Fields: extent_id, bbox, width, height, area, primitive_count, constituent_seqnos
  Surface: vector drawing extent
  → 只覆盖 vector extent, 不重复 any existing surface
```

### 重叠分析

```
P2 ↔ DRAWING_GEOMETRY: NO overlap (text vs vector)
P2 ↔ DRAWING_EXTENT: NO overlap (text pairwise vs vector aggregation)
P6 ↔ DRAWING_EXTENT: NO overlap (text-span region vs vector extent)
  → P6 DENSE_REGION 基于 text span 密度; DRAWING_EXTENT 基于 vector primitive 聚合
  → 不同输入, 不同计算, 不同事实
NTB ↔ DRAWING_GEOMETRY: NO overlap (raster vs vector)
  → 不同 PyMuPDF surface (get_text dict vs get_drawings)
  → 同属 non-text domain, 不同 surface
IN_REGION ↔ DRAWING_EXTENT: NO overlap
  → IN_REGION = text atom ↔ region containment
  → DRAWING_EXTENT = vector primitive aggregation
```

### 判定

```
G9 = PASS

SURFACE_DUPLICATION = FALSE

理由:
  - P2 = text geometry (不同 input)
  - P6 = text-span region (不同 input)
  - NTB = raster non-text (不同 surface)
  - DRAWING_GEOMETRY = vector drawing primitive (新 surface)
  - DRAWING_EXTENT = vector drawing extent (新 fact, 非重复)
  - 零字段级重复 (逐层对比确认)
```

---

## 12. G10 — Future Experiment Boundary

### 能进入"可研究"状态的方向

```
Mixed Layout:
  当前: text region (P6) 无 drawing extent → 无法做 text/drawing 空间分区
  如果有 DRAWING_EXTENT_FACT:
    → text region (P6 COLUMN/DENSE/SPARSE) + drawing extent → 空间分区可观测
    → 最接近纯几何的方向 (比 Figure/Caption 更不需要语义)
    → 可能进入 "可研究" 状态
  但: 无现有 mixed-layout failure cases → 需先收集

Figure / Caption:
  当前: VISUAL_REGION_EVIDENCE = MISSING → M-A NOT_READY
  如果有 DRAWING_GEOMETRY_FACT + DRAWING_EXTENT_FACT:
    → drawing extent 存在 + 位置可观测
    → consumer 可计算 text proximity (derived from bboxes)
    → 可测试 "FIG-prefix + proximity" 组合
    → 从 "完全无 visual evidence" 缩小到 "visual + proximity + prefix"
    → 可能进入 "可研究" 状态 (但 semantic gap remains)
  但: 需 negative cases (figure + footnote / reference) + 预注册规则
```

### 仍然不能直接解决

```
  Figure identity:     "drawing extent" ≠ "figure" (table border 也 extent)
  Caption identity:    "text near drawing + FIG-prefix" ≠ "caption" (footnote 也 near)
  Chart identity:      "drawing with rects" ≠ "chart" (table 也有 rects)
  Flowchart identity:  "connected paths" ≠ "flowchart" (circuit 也 connected)
  Table identity:      "vector lines" ≠ "table" (figure border 也 lines)
  caption_of:          语义关系, 需 Hypothesis
  figure_of:           语义关系, 需 Hypothesis
```

### 必须保持的链

```
Visual Geometry Evidence (Observation)
        ↓
Evidence Organization (Consumer: query + bbox arithmetic + hypothesis)
        ↓
Semantic Hypothesis (Interpretation, validated by Human or counterfactual)

禁止:
  DRAWING_GEOMETRY_FACT → Figure Detector
  DRAWING_EXTENT_FACT → Visual Region Detector
```

### 判定

```
G10 = PASS

FUTURE_EXPERIMENT_ROUTE = CONDITIONAL

理由:
  - 能打开 Mixed Layout / Figure-Caption 的 "可研究" 状态
  - 但不能直接解决任何 semantic identity
  - semantic gap remains (需 Hypothesis 层)
  - 需 negative cases + 预注册规则 + 授权
```

---

## 13. Final Decision

### Gate 汇总

| Gate | 判定 | 关键发现 |
|------|------|---------|
| G1 DRAWING_GEOMETRY_FACT | PASS | 5 字段全部纯几何, deterministic, closed, no semantic, no duplication |
| G2 DRAWING_EXTENT_FACT | PASS | 7 字段全部纯几何聚合, deterministic, closed, no semantic |
| G3 Merge Rule | PASS | 15/15 操作纯几何, 0 语义读取, GEOMETRIC_AGGREGATION |
| G4 Parameter Closure | **INCOMPLETE** | **12 params total, 6 undocumented in design** |
| G5 Object Semantic Leakage | PASS | FALSE — extent 不声明 figure/visual identity |
| G6 Extent Storage | PASS | JUSTIFIED — 非平凡 computation, stable, consistent with GAP_SEQUENCE |
| G7 Identity | PASS | STABLE — seqno + pymupdf_version, consistent with NTB |
| G8 Contract Closure | PASS | SUPPORTED — closed schema, zero forbidden semantics |
| G9 Duplication | PASS | FALSE — no field-level duplication |
| G10 Future Experiment | PASS | CONDITIONAL — opens research, semantic gap remains |

### 关键问题: G4 INCOMPLETE

```
G4 是唯一未 PASS 的 Gate。

问题:
  真实代码有 12 个参数影响 merge/extent 输出。
  前序设计只列出了 6 个。
  6 个参数未声明:
    - border_x_thresh (5.0)
    - border_y_thresh (5.0)
    - post_min_width (40)
    - post_min_height (30)
    - post_max_w_ratio (0.95)
    - post_max_h_ratio (0.95)

影响:
  如果实现时遗漏这 6 个参数 → params_hash 不完整 → deterministic replay 不可复现
  → 违反 AO CONTRACT §6 Determinism

修复:
  所有 12 个参数 MUST 在 params_hash 中声明 (见 §6 修复要求)
  这是 design documentation gap, 非架构缺陷
```

### 最终判定

```
AO_VISUAL_GEOMETRY_CONTRACT_GATE = CONDITIONAL_ON_DESIGN_CHANGE

理由:
  - 10 个 Gate 中 9 个 PASS
  - G4 (Parameter Closure) = INCOMPLETE (6/12 params 未声明)
  - 架构本身 sound (merge 是 geometric aggregation, 无 semantic leakage, 无 duplication)
  - 但: parameter documentation 不完整 → 需 design change before implementation

Required Design Changes (before implementation authorization):
  DC1: 完整列出所有 12 个 merge/filter 参数 (pre-merge 6 + merge 1 + post-merge 5)
  DC2: 所有 12 参数纳入 params_hash 定义
  DC3: 明确声明 DRAWING_GEOMETRY_FACT 记录 ALL primitives (无 pre-filter)
  DC4: 明确声明 DRAWING_EXTENT_FACT 的 post-merge filter 是 declared geometric selection
  DC5: border filter (rect.x0 <= 5 and rect.y0 <= 5) 文档化为 compound param

这些是 documentation completion, 非架构变更。
完成后 → 可重新 Gate → 若 PASS → READY_FOR_AUTHORIZED_IMPLEMENTATION。
```

---

## 14. Future Authorized Scope

### 仅作为设计边界记录, 不执行

```
Future Authorized Scope (IF explicitly authorized later):

1. DRAWING_GEOMETRY_FACT
   - enumerate page.get_drawings() ALL primitives (no pre-filter)
   - 5 content fields: drawing_id, bbox, draw_type, item_count, item_types
   - 7 provenance fields (same as NTB pattern)
   - closed schema (no raw passthrough)

2. DRAWING_EXTENT_FACT
   - merge_nearby with ALL 12 params declared in params_hash
   - 7 content fields: extent_id, bbox, width, height, area, primitive_count, constituent_seqnos
   - 7 provenance fields
   - closed schema

3. Closed schema enforcement
   - verify_determinism.py §K scan extended to cover DRAWING_GEOMETRY_FACT + DRAWING_EXTENT_FACT
   - forbidden semantics scan (is_figure, is_caption, caption_of, ...)

4. Provenance (7-field pattern, same as NTB)
   - source_sha, params_hash, schema_version, coordinate_system,
     document_id, page_reference, pymupdf_version

5. params_hash (12 params)
   - pre_filter: min_width, min_height, border_x_thresh, border_y_thresh,
     max_width_ratio, max_height_ratio
   - merge_gap
   - post_filter: min_area, post_min_width, post_min_height,
     post_max_w_ratio, post_max_h_ratio

6. Deterministic validation (design, not execution now)
   - same PDF + same PyMuPDF + same params → byte-identical
   - sort_keys=True serialization

7. Existing baseline regression
   - P1-P7 / TLD / GT / frozen artifacts unchanged
   - drift=0/7 maintained
```

### 明确排除

```
EXCLUDED from future scope:
  - TEXT_DRAWING_SPATIAL_RELATION (derivable from bboxes, NOT JUSTIFIED)
  - VISUAL_REGION (semantic label, FORBIDDEN)
  - Figure Detector
  - Caption Detector
  - Chart Detector
  - Flowchart Detector
  - Semantic Classifier
  - LLM
  - PNG rendering (in Observation layer)
  - caption regex matching (in Observation layer)
  - "image" label (in Observation layer)
  - color/fill/width/opacity (not minimal)
  - items raw passthrough (non-serializable, provenance complex)
  - density (derived, not stored)
```

---

## 15. Governance Status

```text
AO_VISUAL_GEOMETRY_CONTRACT_GATE = CONDITIONAL_ON_DESIGN_CHANGE

DRAWING_GEOMETRY_FACT = PASS (5 content fields, all geometric, deterministic, closed)
DRAWING_EXTENT_FACT   = PASS (7 content fields, geometric aggregation, deterministic, closed)

MERGE_TYPE = GEOMETRIC_AGGREGATION
  15/15 operations geometric, 0 semantic info read
  Input: pure bbox list
  Rule: expand_intersect (gap=declared)
  Output: merged bbox (aggregated extent, not semantic object)

PARAMETER_CLOSURE = INCOMPLETE
  12 params total in real code
  6 params undocumented in previous design
  Required: all 12 params MUST be in params_hash

OBJECT_SEMANTIC_LEAKAGE = FALSE
  Extent declares "geometric aggregation result", not "semantic object"
  No figure/table/chart/caption identity in schema

EXTENT_STORAGE = JUSTIFIED
  merge_nearby is non-trivial (iterative clustering)
  primitive_count + constituent_seqnos are merge products (not trivially derivable)
  Consistent with GAP_SEQUENCE pattern (stored measurement)
  post-merge filter is declared geometric selection, not semantic detection

IDENTITY = STABLE
  seqno: stable across calls [OBSERVED], unique per page [OBSERVED]
  drawing_id: pure function (doc, page, seqno)
  extent_id: pure function (constituent_seqnos + params_hash)
  Cross-version risk mitigated by pymupdf_version in provenance (consistent with NTB)

FIELD_CLOSURE = SUPPORTED
  Closed allowlist schema (fixed fields, no raw passthrough)
  Zero forbidden semantics in candidate schema

SURFACE_DUPLICATION = FALSE
  P2=text geometry, P6=text-span region, NTB=raster, DRAWING=vector
  Zero field-level duplication

SEMANTIC_GAP_REMAINS = TRUE
  Visual Geometry ≠ Figure/Caption/Chart/Flowchart/Table identity
  Requires: Observation → Evidence Organization → Semantic Hypothesis

FUTURE_EXPERIMENT_ROUTE = CONDITIONAL
  Opens Mixed Layout / Figure-Caption research
  But: semantic gap remains, negative cases needed

REQUIRED_DESIGN_CHANGES (before implementation):
  DC1: List all 12 merge/filter params (currently 6/12 documented)
  DC2: All 12 params in params_hash definition
  DC3: DRAWING_GEOMETRY_FACT = ALL primitives (no pre-filter) — explicit
  DC4: DRAWING_EXTENT_FACT post-merge filter = declared geometric selection — explicit
  DC5: Border filter documented as compound param

IMPLEMENTATION = NOT AUTHORIZED
EXPERIMENT     = NOT AUTHORIZED
FROZEN_BASELINE = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d, layout_analyzer=8f69f0d2)
PRODUCTION     = FALSE
RUNTIME_AUTHORITY = ZERO
STOP           = TRUE
```

---

## 研究原则遵守确认

- ✅ 只读代码检查 (layout_analyzer.py:268-324 逐行审计)
- ✅ merge 规则逐操作分类 (15/15 操作, 全部 geometric)
- ✅ 参数从真实代码提取 (12 params, 非猜测)
- ✅ 参数几何性验证 (12/12 pure geometric)
- ✅ 参数完整性检查 (发现 6/12 未文档化)
- ✅ Object semantic leakage 测试 (extent 不声明 figure identity)
- ✅ Extent storage 必要性比较 (Option A vs B, 与 GAP_SEQUENCE 对比)
- ✅ Identity 稳定性验证 (seqno [OBSERVED], 与 NTB pattern 对比)
- ✅ Contract closure 检查 (closed schema, zero forbidden semantics)
- ✅ Anti-duplication 检查 (P2/P6/NTB 逐层对比)
- ✅ Future experiment boundary (能打开什么, 不能解决什么)
- ✅ 不自行进入 implementation
- ✅ 不修改任何文件
- ✅ 只生成一个文件

`STOP = TRUE`。
