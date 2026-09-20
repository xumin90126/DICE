# Visual / Non-text Observation Surface Design Research

> **模式: READ-ONLY / DESIGN-RESEARCH ONLY / NO IMPLEMENTATION / NO EXPERIMENT / FROZEN INTACT / STOP**
> 日期: 2026-09-17
> 前置: `p6_observation_boundary_reassessment.md`（PRIMARY=C OBSERVATION_SURFACE_TOO_NARROW）
> 本文件研究 DICE 是否应该、以及以什么最小方式获得图形/非文本几何事实的观察能力。

---

## 1. Executive Summary

```
VISUAL_OBSERVATION_SURFACE_STATUS = CONDITIONAL

PRIMARY_DIAGNOSIS   = C (OBSERVATION_SURFACE_TOO_NARROW)
SECONDARY_DIAGNOSIS = D (REPRESENTATION_GAP)

VECTOR_GEOMETRY_EVIDENCE = AVAILABLE_BUT_NOT_EXPOSED
  PyMuPDF page.get_drawings() 返回纯几何事实 (bbox, type, items: line/rect/quad)
  chunker/layout_analyzer.py:269-325 已执行纯几何提取 (filter + merge → extent)
  但同时执行语义操作 (PNG render, caption regex, "image" label)
  Observation 层 (P1-P6/AO/NTB) 明确不覆盖

MINIMAL_OBSERVATION_SURFACE = 3 candidate facts:
  1. DRAWING_GEOMETRY_FACT (per-primitive: bbox, type, item_ops)
  2. DRAWING_EXTENT_FACT (aggregated: merged bbox, primitive_count, area)
  3. TEXT_DRAWING_SPATIAL_RELATION (text bbox ↔ drawing extent: distance/overlap/containment)

ARCHITECTURE_PLACEMENT = Atomic Observation Extension (CONDITIONAL)
  P2 只处理 text geometry — 不重复
  P6 基于 text spans — 不适合
  新独立层 — 过重，不 justified
  AO 已有 NON_TEXT_BLOCK_ATOM — 自然扩展点

SEMANTIC_GAP_REMAINS = TRUE
  Visual geometry ≠ "这是 figure/table/chart"
  proximity + prefix ≠ caption
  需 Hypothesis 层补充

FUTURE_EXPERIMENT_ROUTE = CONDITIONAL
  若授权 visual geometry observation → M-A 可能从 NOT_READY 转为可验证实验
  但需 negative cases + 预注册规则 + 接受 semantic gap

IMPLEMENTATION = NOT AUTHORIZED
EXPERIMENT     = NOT AUTHORIZED
FROZEN_BASELINE = INTACT
STOP           = TRUE
```

---

## 2. Research Question

> DICE 的 Observation Layer 到底应该暴露哪些纯粹的 Visual / Non-text Facts，
> 才能在不引入语义判断的情况下，为后续 Evidence Organization 提供足够证据？

### 区分两个层次

```
Visual Semantic Identity ("这是 Figure/Table/Chart")  → Hypothesis / Interpretation
    禁止进入 Observation

Visual Geometric Existence ("此区域存在矢量基元 + bbox")  → Observation
    当前 MISSING，但底层 AVAILABLE
```

---

## 3. Existing Visual Evidence Inventory

### 3.1 代码级扫描结果

| # | 文件 | 行号 | 原始 API | 原始事实 | 当前处理 | 纯 Observation? | 引入语义? | 可拆为纯事实? | 风险 |
|---|------|------|---------|---------|---------|----------------|----------|-------------|------|
| 1 | `chunker/layout_analyzer.py` | 269 | `page.get_drawings()` | List of drawing dicts (rect, type, items, color, fill, width) | 提取 rect → filter (size/border) → merge_nearby → extent | **YES** (269-283, 285-325) | NO (此阶段) | **YES** | 无 |
| 2 | `chunker/layout_analyzer.py` | 348 | `page.get_images()` | Embedded raster image xref list | `get_image_rects(xref)` → bbox | **YES** (bbox 提取) | NO (此阶段) | **YES** | 无 |
| 3 | `chunker/layout_analyzer.py` | 372-381 | `page.get_pixmap()` | Rendered PNG | 渲染区域为 base64 PNG | NO | **YES** (视觉内容恢复) | NO | OCR/visual recovery forbidden in AO |
| 4 | `chunker/layout_analyzer.py` | 386-396 | regex `Fig\|图\|Figure\|Table` | Text block content | Regex 匹配 caption | NO | **YES** (语义推断) | NO | 词法推断 must stay hypothesis |
| 5 | `chunker/layout_analyzer.py` | 413-414 | dict label | — | `"type": "image"` | NO | **YES** (语义标签) | NO | Semantic label forbidden in AO |
| 6 | `chunker/layout_analyzer.py` | 399-411 | bbox containment | Text block center ∈ expanded region | 排除"图内文本" | **PARTIAL** (containment is geometry) | **YES** (决策"是图内标签") | **YES** (containment fact) | 排除决策是 semantic |
| 7 | `perception/sandbox/observations/atomic_text.py` | 256 | `block_type != 0` | Non-text block type | **Skip** (跳过) | — | — | — | P1 explicitly skips non-text |
| 8 | `tmp/perception/atomic_observation/non_text_block.py` | 64-110 | `page.get_text("dict")` blocks[type≠0] | Raster image bbox + type | 记录 bbox/type, content=null | **YES** | NO | **YES** | Only raster, NOT vector |
| 9 | `perception/sandbox/geometry/geometry_engine.py` | — | P2 pairwise/single | Text span geometry | same_y_band, h_gap, left_alignment | YES | NO | — | **Only text atoms, NO drawings** |
| 10 | `perception/sandbox/region/region_config.py` | 39-41 | — | VISUAL_REGION deleted | "requires identifying image/figure/table" | — | — | — | Deletion conflated existence with identity |

### 3.2 关键发现

```
chunker/layout_analyzer.py:detect_images() 可分解为:

  Stage 1 (PURE GEOMETRY, lines 269-325):
    get_drawings() → rect filter (size/border) → merge_nearby(gap=50) → extent
    → 纯 bbox 提取 + 几何聚类 + 面积过滤
    → 无语义标签，无内容恢复，无词法推断
    → 这是合法的 Observation 候选

  Stage 2 (SEMANTIC, lines 360-424):
    PNG render → caption regex → "image" label → text exclusion
    → 视觉内容恢复 + 词法推断 + 语义分类 + 语义决策
    → 必须留在 chunker (consumer)，不得进入 Observation

  Stage 1 的事实已存在于生产代码中，但未作为 Observation 暴露给 Evidence 层。
```

---

## 4. get_drawings() Evidence Analysis

### 4.1 API 返回结构 [OBSERVED, 实测]

```python
page.get_drawings() → List[dict]
  每个 dict:
    rect: Rect(x0, y0, x1, y1)           # 纯几何 bbox
    type: 's' (stroke) / 'f' (fill) / 'fs' (fill+stroke)  # 纯类型
    items: List[tuple]                    # 纯基元
      ('l', Point, Point)                 #   line
      ('re', Rect)                        #   rectangle
      ('qu', Quad, Point, Point, Point)   #   quadratic curve
      ('c', Point, Point, Point, Point)   #   cubic curve
    color: tuple (r,g,b)                  # 纯样式
    fill: tuple or None                   # 纯样式
    width: float                          # 纯样式
    stroke_opacity: float                 # 纯样式
    fill_opacity: float or None           # 纯样式
    layer: str                            # 纯层级
    seqno: int                            # 纯序号
```

### 4.2 实测数据

```
arxiv_2402.18619 (35 pages):
  Page 28 (figure):  216 drawings, 12 filtered, 1 merged region, density=0.219
  Page 1 (text):      15 drawings,  0 filtered (all < 15pt or border)
  Page 31 (refs):    137 drawings,  0 filtered (all < 15pt or border)

  → Figure page: high drawing density (0.219)
  → Text page: drawings exist but are tiny (page border, decorative lines)
  → Reference page: drawings exist but are tiny (reference formatting)

  判别性: drawing density 能区分 "有图区域" vs "纯文本区域"
  但: density ≠ "这是 figure" (table border 也 high density)
```

### 4.3 哪些事实可进入 Observation Layer?

| 事实 | 来源 | 纯 Observation? | 理由 |
|------|------|----------------|------|
| rect (bbox) | get_drawings().rect | **YES** | 纯坐标，无语义 |
| type (stroke/fill) | get_drawings().type | **YES** | 纯类型，描述绘图方式 |
| items (line/rect/quad/curve) | get_drawings().items | **YES** | 纯基元类型 |
| item count | len(items) | **YES** | 纯计数 |
| color/fill/width | get_drawings() | **YES** | 纯样式（与 P3 style 对应） |
| merged extent | merge_nearby output | **YES** | 纯聚合 bbox |
| primitive_count per region | count in merged extent | **YES** | 纯计数 |
| area | rect.width * rect.height | **YES** | 纯几何 |
| density | primitive_count / area | **YES** | 纯比率（无语义标签） |
| text-drawing distance | computed from bboxes | **YES** | 纯空间关系 |
| text-drawing overlap | computed from bboxes | **YES** | 纯空间关系 |
| text-drawing containment | bbox containment | **YES** | 纯空间关系 |
| "这是 image" | layout_analyzer label | **NO** | 语义标签 |
| "这是 caption" | regex match | **NO** | 语义推断 |
| PNG content | get_pixmap() | **NO** | 视觉内容恢复 |

---

## 5. Current P6 / Atomic Observation Boundary

### 5.1 P6 RegionObservation

```
Region taxonomy (geometric ONLY):
  PAGE_TOP_REGION / PAGE_BOTTOM_REGION / FULL_WIDTH_REGION /
  COLUMN_REGION / DENSE_REGION / SPARSE_REGION / UNKNOWN_REGION

Deleted:
  TEXT_REGION   — "requires semantic text-vs-nontext knowledge"
  VISUAL_REGION — "requires identifying image/figure/table; a void is not a visual object"

P6 input: P4 spans + P5 column layout (TEXT spans only)
P6 does NOT read: get_drawings(), get_images(), non-text blocks
```

**P6 无法自然容纳 visual geometry** — P6 的设计是 "from text spans → geometric regions"。
Drawing 不是 text span。放入 P6 会破坏设计一致性。

### 5.2 Atomic Observation (NON_TEXT_BLOCK_ATOM)

```
NTB covers: page.get_text("dict").blocks[type != 0] = RASTER IMAGE blocks only
NTB does NOT cover: page.get_drawings() = VECTOR DRAWING primitives
NTB fields: atom_id, bbox, pdf_block_type, content=null (permanent)
NTB forbidden: image/figure/chart semantic naming, OCR, content recovery
```

**NTB 是自然扩展点** — 它已经是 "non-text surface"，只覆盖 raster。
Vector drawing 是同一 non-text domain 的另一个 surface。

### 5.3 P2 GeometryObservation

```
P2 covers: text atom pairwise/single geometry
  - same_y_band, h_gap, v_gap, left_alignment_group, same_x_band
  - center_x, center_y, normalized_x/y
P2 does NOT cover: non-text drawing geometry
P2 input: TEXT atoms only (from P1)
```

**P2 不重复** — P2 只处理 text geometry；visual geometry 处理 non-text。

---

## 6. Observation vs Interpretation Boundary

### 三层边界

```
Layer A — Raw / Geometric Evidence (PyMuPDF 原始返回)
  drawing rect, type, items, color, fill, width
  → 纯 PDF 底层数据，无任何变换

Layer B — Structured Observation (DICE Observation Layer 候选)
  drawing_bbox, primitive_type, primitive_count, drawing_extent,
  text_drawing_distance, text_drawing_overlap, text_drawing_containment
  → 纯几何事实，有 provenance，确定性，无语义标签

Layer C — Semantic Hypothesis / Interpretation (禁止进入 Observation)
  is_figure, is_table, is_chart, is_caption, is_flowchart,
  caption_of, figure_of, belongs_to_figure, semantic_role
  → 语义判断，需 Hypothesis 层
```

### 候选字段归类

| Candidate | A (Raw) | B (Observation) | C (Semantic) | 允许? |
|-----------|---------|-----------------|-------------|-------|
| drawing bbox (rect) | ✓ | ✓ | | **YES** — 纯坐标 |
| primitive type (stroke/fill) | ✓ | ✓ | | **YES** — 纯类型 |
| primitive items (line/rect/quad) | ✓ | ✓ | | **YES** — 纯基元 |
| primitive count | ✓ | ✓ | | **YES** — 纯计数 |
| drawing extent (merged bbox) | | ✓ | | **YES** — 纯聚合 |
| area | | ✓ | | **YES** — 纯几何 |
| drawing density (count/area) | | ✓ | | **YES** — 纯比率 |
| text-drawing distance | | ✓ | | **YES** — 纯空间 |
| text-drawing overlap | | ✓ | | **YES** — 纯空间 |
| text-drawing containment | | ✓ | | **YES** — 纯空间 |
| color/fill/width | ✓ | ✓ | | **YES** — 纯样式 |
| "drawing is figure" | | | ✓ | **NO** — 语义 |
| "drawing is chart" | | | ✓ | **NO** — 语义 |
| "drawing is table border" | | | ✓ | **NO** — 语义 |
| "text is caption" | | | ✓ | **NO** — 语义 |
| "text belongs to figure" | | | ✓ | **NO** — 语义 |
| "figure-caption association" | | | ✓ | **NO** — 语义 |
| PNG content | | | ✓ | **NO** — 视觉恢复 |
| caption regex match | | | ✓ | **NO** — 词法推断 |

---

## 7. Candidate Visual Observation Facts

### Candidate A — DRAWING_GEOMETRY_FACT

```
Fields:
  drawing_id        = "DRAW|{doc}|p{page}|{seq}" (纯函数, 无 timestamp/random)
  document_id       = str
  page_reference    = int
  bbox              = [x0, y0, x1, y1] (PyMuPDF rect 原值, _round_bbox 约定)
  primitive_type    = "s" / "f" / "fs" (stroke/fill/fill+stroke)
  item_operations   = [("l",...), ("re",...), ("qu",...)] (verbatim)
  item_count        = int
  color             = (r,g,b) or None
  fill              = (r,g,b) or None
  width             = float or None
  coordinate_system = "pymupdf_page_1.26.x_y_down"
  source_sha        = PyMuPDF version + extraction code sha
  params_hash       = definition hash
  geometry_source   = "pymupdf:get_drawings"

判定:
  drawing_id = 纯技术标识 (YES)
  bbox = NOT P2 (P2 只处理 text; this is non-text) (YES, 不重复)
  primitive_type = 不携带语义 ("stroke" ≠ "figure") (YES)
  item_count = 有意义事实 (基元数量) (YES)
  重复 P2? NO (P2 = text geometry; this = non-text geometry)

VERDICT: VALID candidate
```

### Candidate B — DRAWING_EXTENT_FACT

```
Fields:
  extent_id          = "DEXT|{doc}|p{page}|{seq}" (纯函数)
  document_id        = str
  page_reference     = int
  extent_bbox        = [x0, y0, x1, y1] (merged bbox)
  width              = float
  height             = float
  area               = float
  primitive_count    = int (drawings within extent)
  merge_gap          = float (clustering parameter, declared)
  coordinate_system  = "pymupdf_page_1.26.x_y_down"
  source_sha         = ...
  params_hash        = ...
  geometry_source    = "pymupdf:get_drawings + merge_nearby(gap={merge_gap})"

判定:
  extent_bbox = 聚合 bbox, NOT in P2 (P2 无 aggregation) (YES, 不重复)
  width/height/area = 纯几何派生 (YES)
  primitive_count = 纯计数 (YES)
  density (count/area) = 可派生, 但不存储为字段 (hypothesis 侧计算)

  是否重复 P6? NO — P6 的 DENSE_REGION 基于 text span 密度;
  DRAWING_EXTENT 基于 vector primitive 聚合, 不同输入

VERDICT: VALID candidate
  但: merge_nearby 的 gap=50 是阈值 → 需声明为 params, 非 hardcoded
  但: area filter (>=2000, w>40, h>30) 是阈值 → 同上
  → 这些阈值必须 declared in params_hash, 非 frozen
```

### Candidate C — TEXT_DRAWING_SPATIAL_RELATION

```
Fields:
  relation_id        = "TDSR|{text_atom_id}|{drawing_extent_id}" (纯函数)
  text_atom_id       = P1 TEXT_ATOM id (frozen)
  drawing_extent_id  = DRAWING_EXTENT_FACT id
  distance           = float (min distance between bboxes)
  overlap_ratio      = float (intersection area / text area)
  containment        = bool (text center ∈ drawing extent)
  spatial_position   = "above" / "below" / "left" / "right" / "inside" / "overlap"
  coordinate_system  = ...
  geometry_source    = "layer:relation_def@text_drawing_spatial_v1"

判定:
  distance/overlap/containment = 纯几何 (YES)
  spatial_position = 纯空间方位 (YES, 不携带 "caption" 语义)
  重复 P2? NO — P2 的 IN_REGION 是 text↔region;
  这是 text↔drawing_extent, 不同对象

  禁止: "caption_of" / "belongs_to_figure" / "is_caption"

VERDICT: VALID candidate
  但: spatial_position 的方位词 ("above"/"below") 是纯空间, 非语义
  → "above" ≠ "caption" (caption 可 above 或 below figure)
```

### Candidate D — Drawing Density / Distribution

```
  density = primitive_count / area

判定:
  "某区域存在多少 vector primitives" = 纯计数/比率 (YES)
  "visual_complexity = figure" = 语义 (NO)

  density 字段本身不携带语义标签
  但: density 高 → 暗示 "visual content" → 接近语义边界

  保守做法: 不存储 density 为字段; 让 hypothesis 侧从 primitive_count + area 计算
  → DRAWING_EXTENT_FACT 已包含 primitive_count + area → density 可派生

VERDICT: 不需要独立字段; density 是派生值, hypothesis 侧计算
```

### Candidate E — Non-text Block Existence

```
当前 NON_TEXT_BLOCK_ATOM 覆盖:
  RASTER IMAGE (get_text("dict").blocks[type≠0])
  → bbox, pdf_block_type, content=null

不覆盖:
  VECTOR DRAWING (get_drawings())
  → 这是本研究的核心缺口

  Mixed Vector + Text Figure: 部分覆盖 (text = P1, vector = MISSING)
  Flowchart: 不覆盖 (vector)
  Chart: 不覆盖 (vector)
  Table-like Vector Object: 不覆盖 (vector)

→ 当前 Observation 只能表达 "raster image 存在" (NTB)
→ 不能表达 "vector drawing 存在" (MISSING)
→ 这是 Observation Surface Gap
```

---

## 8. Redundancy / Anti-Bloat Analysis

### ANTI-BLOAT CHECK

| 检查项 | 结果 | 理由 |
|--------|------|------|
| 是否重复 P2 geometry? | **NO** | P2 = text pairwise/single; visual = non-text drawing |
| 是否重复 P6 region? | **NO** | P6 = text span clustering; visual = drawing primitive clustering |
| 是否重复 AO NON_TEXT_BLOCK? | **PARTIAL** | NTB = raster image; visual = vector drawing — 同一 domain 不同 surface |
| 是否只是 detector 输出换名? | **NO** | 不产出 detector 判定; 只产出几何事实 |
| 是否只为 Figure/Caption 实验预埋? | **NO** | visual geometry 对 Mixed Layout / Flowchart / Table border 都有用 |
| 是否引入 semantic interpretation? | **NO** | 所有候选字段是纯几何 (bbox/count/distance) |
| 已有 Observation 能表达? | **NO** | vector drawing 在任何 surface 都不存在 |

### 解决的是真实 Representation Gap 还是实验便利?

```
真实 Representation Gap:
  - 5/6 文档含被跳过的视觉内容 (P7 Evidence Gap Analysis)
  - 94 raster + ~2006 vector objects 被 P1 完全跳过
  - M-A 2 个 MERGE case: NTB=0, vector figure 存在但不可观测
  - M-B: 矢量表格无 NTB

→ 这是真实缺口，非实验便利
→ DO NOT ADD only for experiment convenience
→ ADD because Document 中真实存在的事实当前无法被 Observation 表达
```

---

## 9. Architecture Placement Comparison

### Option A — Atomic Observation Extension

```
P1–P6
↓
Atomic Observation
├── TEXT_ATOM (P1 frozen)
├── NON_TEXT_BLOCK_ATOM (raster image, existing)
├── DRAWING_GEOMETRY_FACT (vector drawing, NEW candidate)
├── DRAWING_EXTENT_FACT (aggregated, NEW candidate)
└── TEXT_DRAWING_SPATIAL_RELATION (NEW candidate)
```

| 维度 | 评估 |
|------|------|
| 与已有架构一致? | **YES** — AO 已有 NTB (non-text surface); vector drawing 是同 domain 扩展 |
| 保持 "事实暴露"? | **YES** — 纯 bbox/count/spatial facts, 无语义 |
| 不需要新增大型层? | **YES** — 扩展现有 AO, 不新增层 |
| AO 会膨胀? | **LOW RISK** — 增加 3 个 fact types; NTB 已是先例 |
| vector geometry 是 atomic fact? | **YES** — drawing primitive 是原子级 (bbox + type + items) |
| 与 P2/P6 职责重叠? | **NO** — P2=text, P6=text-span-region, AO=non-text |

```
SUPPORTED
```

### Option B — P6 Observation Surface Extension

```
P6 RegionObservation
+ pure non-text geometric evidence (DRAWING_DENSE_REGION?)
```

| 维度 | 评估 |
|------|------|
| P6 当前 Region 语义? | Geometric ONLY (PAGE_TOP/BOTTOM/FULL_WIDTH/COLUMN/DENSE/SPARSE/UNKNOWN) |
| Drawing geometry 天然属于 Region? | **PARTIAL** — drawing extent 是一种 "region"，但输入不是 text spans |
| P6 能容纳? | **NO** — P6 设计 = "from P4 spans + P5 column layout"; drawing 不是 span |
| 破坏设计一致性? | **YES** — 在 text-span-based 层引入 non-text input |

```
NOT JUSTIFIED
  P6 的设计原则是 text-span-based region; vector drawing 不是 text span。
  在 P6 中加入 drawing 会破坏 "from P4 spans + P5 column" 的输入链。
  且任何 "DRAWING_REGION" 标签都接近语义（暗示 "这是 visual area"）。
```

### Option C — New Independent Visual Observation Layer

```
P1–P6
↓
Visual Observation (NEW)
↓
Atomic Observation
```

| 维度 | 评估 |
|------|------|
| P1-P6/AO 确实无法容纳? | **NO** — AO 可以扩展 (Option A) |
| 需要新层? | **NO** — 过重 |
| 独立性优势? | **LOW** — visual geometry 与 NTB 同 domain |
| 架构复杂度? | **HIGH** — 新层 = 新 registry/schema/contract/determinism |

```
NOT JUSTIFIED
  AO (Option A) 可自然扩展; 新独立层过重。
  只有当 AO 无法容纳时才考虑, 但当前 AO 是自然扩展点。
```

### 总结

```
Option A (AO Extension)  = SUPPORTED
Option B (P6 Extension)  = NOT JUSTIFIED
Option C (New Layer)     = NOT JUSTIFIED

ARCHITECTURE_PLACEMENT = Atomic Observation Extension (CONDITIONAL)
  CONDITIONAL 因为: 需修订 AO CONTRACT §13 ("vector drawings 不覆盖")
  修订 CONTRACT = 设计决策, 需授权
```

---

## 10. Minimal Candidate Observation Surface

### 最小候选集合 (3 facts)

```
MINIMAL_CANDIDATE_SET:

1. DRAWING_GEOMETRY_FACT
   - per-primitive: drawing_id, bbox, primitive_type, item_ops, item_count
   - source: page.get_drawings()
   - pure geometry: YES, no semantic
   - provenance: source_sha + params_hash + coordinate_system
   - deterministic: YES (pure function of PDF + PyMuPDF version)

2. DRAWING_EXTENT_FACT
   - aggregated: extent_id, extent_bbox, width, height, area, primitive_count
   - source: merge_nearby(DRAWING_GEOMETRY_FACT.bbox, gap=declared)
   - pure geometry: YES, no semantic
   - params: merge_gap, min_area, min_width, min_height (all declared in params_hash)
   - deterministic: YES

3. TEXT_DRAWING_SPATIAL_RELATION
   - spatial: relation_id, text_atom_id, drawing_extent_id, distance, overlap_ratio, containment, spatial_position
   - source: bbox computation between P1 TEXT_ATOM and DRAWING_EXTENT_FACT
   - pure geometry: YES, no semantic
   - spatial_position: above/below/left/right/inside/overlap (pure spatial, NOT "caption")
   - deterministic: YES
```

### 为什么是"最小"

```
不包含:
  - density (派生值, hypothesis 侧计算)
  - is_figure / is_table / is_caption (语义, 禁止)
  - PNG content (视觉恢复, 禁止)
  - caption regex (词法推断, 禁止)
  - color/fill/width (样式, 可后续扩展, 非最小必需)

3 facts 覆盖:
  - "drawing 存在 + 位置" (DRAWING_GEOMETRY_FACT)
  - "drawing 区域聚合 + 密度" (DRAWING_EXTENT_FACT)
  - "text 与 drawing 的空间关系" (TEXT_DRAWING_SPATIAL_RELATION)

这 3 个 facts 回答 "这里有什么可观测事实"，不回答 "这是什么"。
```

### 不使用"充分"

```
不声称 MINIMAL_SUFFICIENT_SET
使用 MINIMAL_CANDIDATE_SET
  — 因为 "充分" 需证明能支持具体实验, 当前无实验授权
  — "候选" 表示需 Design Research 验证
```

---

## 11. Semantic Boundary That Still Remains

```
SEMANTIC_GAP_REMAINS = TRUE
```

### 即使有 Visual Geometry Observation，仍无法仅凭该 Observation 得到:

```
Figure      — "drawing dense region" ≠ "figure" (table border 也 dense)
Caption     — "text near drawing" ≠ "caption" (footnote 也 near)
Chart       — "drawing with rects" ≠ "chart" (table 也有 rects)
Flowchart   — "connected paths" ≠ "flowchart" (circuit diagram 也 connected)
Table       — "vector lines" ≠ "table" (figure border 也 lines)
```

### 必须形成的三步链

```
Visual Geometry Evidence (Observation)
        ↓
Evidence Organization (Query / Association)
        ↓
Semantic Hypothesis (Interpretation)

而不是:

Visual Geometry
        ↓
Figure Detector (禁止)
```

### 具体例子: Figure/Caption

```
Visual Geometry says:
  "drawing extent [73,77,522,338] exists on page 28"
  "text 'FIG. 9:' bbox [85,531,143,544] is 0pt below drawing extent"
  "text 'Left:' bbox [143,531,168,544] is 0pt below drawing extent, 0pt right of 'FIG. 9:'"

Evidence Organization can query:
  "text with FIG-prefix + distance < 40pt from drawing extent"

Semantic Hypothesis (hypothesis side) can infer:
  "this text pair is likely a caption of the nearby figure"
  → but this is HYPOTHESIS, not OBSERVATION
  → still needs validation (human or counterfactual)
```

---

## 12. Future Experiment Preconditions

### Figure / Caption

```
如果有 Visual Geometry Observation:
  drawing extent + text proximity + FIG-prefix

是否可能形成 Evidence Sufficiency?
  HELPFUL — proximity + prefix 缩小 candidate set
  INSUFFICIENT — proximity + prefix ≠ caption (footnote/reference also near)

  → 可测试的 Evidence 组合更丰富
  → 但仍需 negative cases (figure + footnote / reference)
  → 仍需接受 semantic gap (human validation 补充)

  Spatial Proximity ≠ Caption — 必须遵守
```

### Flowchart

```
如果有 Visual Geometry Observation:
  drawing primitive distribution + connected paths + text/drawing relationship

是否可能形成 Evidence?
  HELPFUL — "drawing-dense region with connected paths" 可观测
  INSUFFICIENT — "connected paths" ≠ "flowchart" (circuit / diagram 也 connected)
  UNKNOWN — 是否有纯几何信号区分 flowchart vs figure vs chart? 需研究

  → 当前无 flowchart 案例 (INSUFFICIENT_EVIDENCE)
  → 不声称 visual observation 解决 flowchart
```

### Mixed Layout

```
如果有 Visual Geometry Observation:
  text region (P6) + drawing extent + spatial partition

是否可能形成 Evidence?
  HELPFUL — text/drawing 空间分区是纯几何
  最接近纯 Observation 的方向 — 比 Figure/Caption 更不需要语义

  → Mixed Layout 可能是最适合的未来实验对象
  → 但: 当前无 mixed-layout 失败案例
  → 需先收集真实 mixed-layout failure cases
```

### 未来实验路线总结

```
FUTURE_EXPERIMENT_ROUTE = CONDITIONAL

条件:
  1. 授权 visual geometry observation surface (设计 + 实现)
  2. 构造 negative case set
  3. 预注册 proximity/spatial rules (hypothesis side)
  4. 接受 semantic gap (human validation 补充)
  5. 选择最合适的实验对象 (Mixed Layout > Figure/Caption > Flowchart)
```

---

## 13. Negative Boundary

### 即使未来增加 Visual Geometry Observation，也仍然无法仅凭该 Observation 得到:

```
Figure identity      — 需 Hypothesis: "drawing dense + specific shape → figure"
Caption identity     — 需 Hypothesis: "text near drawing + FIG-prefix → caption"
Chart identity       — 需 Hypothesis: "drawing with data-like rects → chart"
Flowchart identity   — 需 Hypothesis: "connected paths + decision diamonds → flowchart"
Table identity       — 需 Hypothesis: "vector grid lines → table"
```

### 必须遵守的链

```
Visual Geometry Evidence
        ↓
Evidence Organization (Query / Association)
        ↓
Semantic Hypothesis (Interpretation, validated by Human or counterfactual)

禁止:
Visual Geometry → Figure Detector
Visual Geometry → Caption Classifier
Visual Geometry → Table Detector
```

### Observation Layer 不得回答

```
"这是什么?" (What is this?)
```

### Observation Layer 只能回答

```
"这里有什么可观测事实?" (What observable facts exist here?)
```

---

## 14. Final Decision

### Q1: DICE 是否存在真实的 Visual Observation Surface Gap?

```
YES — 真实 Gap 存在
  - 5/6 文档含被跳过的视觉内容 (94 raster + ~2006 vector objects)
  - vector drawing 在任何 Observation surface 都不存在
  - P1 显式跳过 block_type != 0; AO NTB 只覆盖 raster; P6 删除 VISUAL_REGION
```

### Q2: Gap 类型?

```
PRIMARY   = C (OBSERVATION_SURFACE_TOO_NARROW)
  - P6 删除 VISUAL_REGION 时把 "visual existence" 与 "visual identity" 合并
  - 纯几何 vector drawing observation 被错误丢失
  - 底层 AVAILABLE (get_drawings) 但未暴露

SECONDARY = D (REPRESENTATION_GAP)
  - 即使暴露 vector geometry, 仍无法表达 "caption_of" / "figure_of" 语义关系
  - 需 Hypothesis 层补充
```

### Q3: get_drawings() 中哪些可进入 Observation?

```
ALL of the following are pure geometry, NO semantic:
  - rect (bbox) — 纯坐标
  - type (stroke/fill) — 纯类型
  - items (line/rect/quad/curve) — 纯基元
  - item_count — 纯计数
  - color/fill/width — 纯样式
  - merged extent — 纯聚合
  - text-drawing distance/overlap/containment — 纯空间

NONE of the following may enter Observation:
  - "image" label — 语义
  - "caption" regex — 词法推断
  - PNG content — 视觉恢复
  - "figure/table/chart" identity — 语义
```

### Q4: 哪些已被 P2/P6/AO 覆盖?

```
P2: text pairwise/single geometry — NOT duplicated (P2 = text, visual = non-text)
P6: text-span region — NOT duplicated (P6 = text spans, visual = drawing primitives)
AO NTB: raster image bbox — PARTIAL overlap (NTB = raster, visual = vector; same domain, different surface)
  → AO extension is natural (NTB + DRAWING = complete non-text coverage)
```

### Q5: 最小候选集合?

```
MINIMAL_CANDIDATE_SET (3 facts, not claiming "sufficient"):
  1. DRAWING_GEOMETRY_FACT — per-primitive bbox/type/items/count
  2. DRAWING_EXTENT_FACT — aggregated extent/area/primitive_count
  3. TEXT_DRAWING_SPATIAL_RELATION — text↔drawing distance/overlap/containment/position
```

### Q6: Architecture placement?

```
Atomic Observation Extension = SUPPORTED
  - AO 已有 NTB (non-text surface); vector drawing 是同 domain 自然扩展
  - 不重复 P2 (text) / P6 (text-span region)
  - 不新增大型层

P6 Extension = NOT JUSTIFIED
  - P6 = text-span-based; drawing 不是 text span

New Layer = NOT JUSTIFIED
  - AO 可扩展; 新层过重

ARCHITECTURE_PLACEMENT = Atomic Observation Extension (CONDITIONAL)
  CONDITIONAL: 需修订 AO CONTRACT §13 ("vector drawings 不覆盖")
```

### Q7: 是否足够支持未来实验?

```
CONDITIONAL
  缺失条件:
    1. 授权 visual geometry observation surface (设计 + 实现)
    2. 构造 negative case set (figure + footnote / reference / continuation)
    3. 预注册 spatial/proximity rules (hypothesis side)
    4. 接受 semantic gap (human validation 补充)
    5. 选择实验对象 (Mixed Layout 最合适, 但无现有 failure cases)
```

### Q8: 是否需要下一步设计研究?

```
DESIGN_RESEARCH = REQUIRED
  - AO CONTRACT §13 修订方案设计
  - DRAWING_GEOMETRY_FACT schema 设计 (字段封闭性, forbidden semantics)
  - merge_nearby 参数声明 (gap/area/width/height thresholds → params_hash)
  - TEXT_DRAWING_SPATIAL_RELATION relation_def 设计
  - determinism 验证方案 (同 PDF + 同 PyMuPDF → 逐字节一致)
  - 与 chunker/layout_analyzer.py 的边界划分 (纯 geometry vs semantic)

  不得自动提出 implementation。
```

---

## 15. Governance Status

```text
VISUAL_OBSERVATION_SURFACE_STATUS = CONDITIONAL

PRIMARY_DIAGNOSIS   = C (OBSERVATION_SURFACE_TOO_NARROW)
SECONDARY_DIAGNOSIS = D (REPRESENTATION_GAP)

VECTOR_GEOMETRY_EVIDENCE = AVAILABLE_BUT_NOT_EXPOSED

MINIMAL_OBSERVATION_SURFACE =
  1. DRAWING_GEOMETRY_FACT (per-primitive: bbox, type, items, count)
  2. DRAWING_EXTENT_FACT (aggregated: extent, area, primitive_count)
  3. TEXT_DRAWING_SPATIAL_RELATION (text↔drawing: distance, overlap, containment, position)

ARCHITECTURE_PLACEMENT = Atomic Observation Extension (CONDITIONAL)
  Option A (AO Extension)  = SUPPORTED
  Option B (P6 Extension)  = NOT JUSTIFIED
  Option C (New Layer)     = NOT JUSTIFIED

SEMANTIC_GAP_REMAINS    = TRUE
  Visual Geometry ≠ Figure/Caption/Chart/Flowchart/Table identity
  Requires: Observation → Evidence Organization → Semantic Hypothesis

FUTURE_EXPERIMENT_ROUTE = CONDITIONAL
  Requires: observation authorization + negative cases + pre-registered rules + semantic gap acceptance

DESIGN_RESEARCH_REQUIRED = TRUE

IMPLEMENTATION = NOT AUTHORIZED
EXPERIMENT     = NOT AUTHORIZED
FROZEN_BASELINE = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d, layout_analyzer=8f69f0d2)
PRODUCTION     = FALSE
RUNTIME_AUTHORITY = ZERO
STOP           = TRUE
```

---

## 16. 研究原则遵守确认

- ✅ 只读代码检查，未修改任何文件
- ✅ 区分 Visual Semantic Identity (禁止) 与 Visual Geometric Existence (可观测)
- ✅ 逐项归类 Observation (Layer A/B) vs Interpretation (Layer C)
- ✅ Anti-Bloat Check: 不重复 P2/P6, 不只为实验预埋, 不引入语义
- ✅ 不声称 "sufficient" (使用 "candidate")
- ✅ 不输出 is_figure/is_caption/caption_of 等语义字段
- ✅ 不输出 confidence/score/rank/decision
- ✅ Negative Boundary 明确: Visual Geometry ≠ Figure/Caption/Table identity
- ✅ Architecture 归属基于证据 (AO SUPPORTED, P6/New Layer NOT JUSTIFIED)
- ✅ 不自行进入 implementation

`STOP = TRUE`。
