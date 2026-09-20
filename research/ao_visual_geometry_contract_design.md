# Atomic Observation §13 — Visual Geometry Contract Design Research

> **模式: DESIGN RESEARCH ONLY / READ-ONLY / NO IMPLEMENTATION / NO EXPERIMENT / FROZEN INTACT / STOP**
> 日期: 2026-09-17
> 前置: `tmp/visual_observation_surface_design_research.md`（VISUAL_OBSERVATION_SURFACE_STATUS = CONDITIONAL）
> 本文件研究: 如果未来授权，AO §13 的安全 Contract 应该如何定义。

---

## 1. Executive Summary

```
AO_VISUAL_GEOMETRY_CONTRACT = CONDITIONAL

ARCHITECTURE_PLACEMENT = ATOMIC_OBSERVATION (confirmed)
  AO 已有 NON_TEXT_BLOCK_ATOM (raster); vector drawing 是同 domain 自然扩展

MINIMAL_CONTRACT =
  1. DRAWING_GEOMETRY_FACT (per-primitive, closed schema, 5 content fields + 7 provenance)
  2. DRAWING_EXTENT_FACT (aggregated, closed schema, 5 content fields + 7 provenance)
  TEXT_DRAWING_SPATIAL_RELATION = NOT JUSTIFIED (derivable from two bboxes; Anti-Bloat)

FIELD_CLOSURE = SUPPORTED (closed allowlist schema, no raw passthrough)

SEMANTIC_GAP_REMAINS = TRUE

KEY DECISIONS:
  - items field: EXCLUDED (heavy, non-serializable, provenance complex) → item_count + item_types only
  - color/fill/width: EXCLUDED (not minimal, P3-equivalent but P3 not in frozen whitelist)
  - TEXT_DRAWING_SPATIAL_RELATION: NOT JUSTIFIED (bbox arithmetic, derivable by consumer)
  - merge: belongs to Observation IF params declared in params_hash (geometric aggregation, not semantic grouping)
  - identity: (page, seqno) for primitives; (page, merge_params_hash, constituent_seqnos) for extents
  - §13 revision: extend §13.1 (remove "vector drawings 不覆盖" limitation) + add §2.3 DRAWING_GEOMETRY_FACT + §2.4 DRAWING_EXTENT_FACT

DESIGN CORRECTION (DC1-DC5, applied after Gate G4=INCOMPLETE):
  DC1: 12 params documented (pre-merge 6 + merge 1 + post-merge 5), from layout_analyzer.py:268-324
  DC2: all 12 params in params_hash definition (was 6, now 12 — closure complete)
  DC3: DRAWING_GEOMETRY_FACT = ALL primitives (no pre-filter) — raw observation
  DC4: DRAWING_EXTENT_FACT = 3-stage geometric pipeline (pre_filter + merge + post_filter)
  DC5: border_x_thresh + border_y_thresh = compound geometric parameter (page_edge_filter)

IMPLEMENTATION = NOT AUTHORIZED
EXPERIMENT     = NOT AUTHORIZED
FROZEN_BASELINE = INTACT
STOP           = TRUE
```

---

## 2. Current AO §13 Boundary

### Q1: 当前 §13 的边界是什么？

来源: `tmp/perception/atomic_observation/CONTRACT.md` §13:

```
## 13. Known limitations

1. 矢量绘图 (get_drawings) 不覆盖 — 与冻结 P1 block 层同一 surface 限制。
2. raster 内容不可达 (无 OCR) — 仅 presence/bbox。
3. P3 style_signature 未暴露 (P3 函数不在冻结白名单)。
4. 截断 P2 artifact 只暴露 singles; GAP_SEQUENCE 拒绝截断数据。
5. 层不调用任何 detector (registered_but_never_invoked); RegionFact 数据来自 detector
   既有 artifact 的 Case A 暴露。
```

当前 §13.1 明确声明: **vector drawings 不覆盖**。

### Q2: 当前 §13 为什么没有覆盖 Vector Geometry?

```
原因链 [OBSERVED]:

1. P1 atomic_text.py:256 显式跳过 block_type != 0
   → P1 只提取 text spans, 不提取 non-text blocks
2. NON_TEXT_BLOCK_ATOM 只读 page.get_text("dict").blocks[type != 0]
   → 只覆盖 raster image blocks (PyMuPDF dict 中的 type=1)
   → 不读 page.get_drawings() (vector drawing 是独立 API)
3. §13.1 声明 "与冻结 P1 block 层同一 surface 限制"
   → 把 get_drawings() 的缺失归因于 P1 surface 限制
   → 但: get_drawings() 是独立 API, 不依赖 P1 block 层
   → 这个归因不准确 [INFERRED]: get_drawings() 不受 P1 surface 限制

4. AO CONTRACT §2.2: "矢量绘图 (get_drawings) 不在覆盖范围 — 声明为 documented limitation"
   → 设计时将 vector drawing 视为 "与 raster 同属 non-text", 但只实现了 raster
   → vector 被声明为 limitation 而非永久禁止
```

**关键发现**: §13.1 的归因 ("与冻结 P1 block 层同一 surface 限制") **不准确**。
get_drawings() 是 PyMuPDF 独立 API，不依赖 P1 block 层。
NTB 读取的是 `get_text("dict")` 的 blocks；get_drawings() 读取的是独立的 drawing path 数据。
二者是不同的 PyMuPDF surface。

### Q3: 新增 Visual Geometry 应该 extend §13 还是 create another section?

```
EXTEND §13 + ADD §2.3 / §2.4

理由:
  §13 是 "Known limitations" — 修订 §13.1 = 移除 "vector drawings 不覆盖" 的 limitation 声明
  §2 是 "Atom contract" — 新增 §2.3 DRAWING_GEOMETRY_FACT + §2.4 DRAWING_EXTENT_FACT
  不创建新 section — vector geometry 属于 AO 的 non-text domain (与 NTB 同家族)

  §13.1 修订为:
    "矢量绘图 (get_drawings) 覆盖 — 见 §2.3 DRAWING_GEOMETRY_FACT / §2.4 DRAWING_EXTENT_FACT。
     仅暴露纯几何事实 (bbox/type/count/extent); 禁 items 透传 / OCR / 视觉解释 / 语义命名。"
```

---

## 3. Raw Evidence Inventory

### PyMuPDF get_drawings() 返回结构 [OBSERVED, 实测]

```
page.get_drawings() → List[dict]
  每个 dict 包含 (全部 present in 216/216 drawings):
    rect: Rect(x0,y0,x1,y1)     # 纯几何 bbox, 100% present
    type: 's'/'f'/'fs'           # stroke/fill/fill+stroke, 100% present
    items: List[tuple]           # 基元操作, 100% present
      ('l', Point, Point)        #   line
      ('re', Rect)               #   rectangle
      ('qu', Quad, P1,P2,P3)     #   quadratic curve
      ('c', P1,P2,P3,P4)         #   cubic curve
    seqno: int                   # PDF-declared sequence number, unique per page, stable across calls
    color: (r,g,b) or None       # stroke color
    fill: (r,g,b) or None        # fill color
    width: float or None         # stroke width
    stroke_opacity: float        # opacity
    fill_opacity: float or None  # fill opacity
    closePath: bool              # path closed
    dashes: list                 # dash pattern
    lineCap: tuple               # line cap style
    lineJoin: float              # line join style
    layer: str                   # layer name
    even_odd: bool or None       # fill rule
```

### 稳定性验证 [OBSERVED]

```
seqno stable across calls: YES (同页同 PDF, get_drawings() 两次调用结果逐项一致)
count stable: YES
rect present in all: YES (216/216)
type present in all: YES
items present in all: YES
seqno unique per page: YES (1-253, no duplicates)
```

### items 序列化问题 [OBSERVED]

```
items 包含 fitz.Point / fitz.Rect / fitz.Quad 对象
JSON-serializable: NO (需要转换 Point→(x,y), Rect→(x0,y0,x1,y1))
→ 如果暴露 items, 需要转换逻辑 → 增加 provenance 复杂性
→ 转换逻辑本身需要 sha 锚定 → 额外 versioning
```

---

## 4. Observation / Interpretation Boundary

### 三层边界

```
Layer A — Raw PDF / PyMuPDF Evidence:
  get_drawings() 原始返回 (rect, type, items, color, fill, width, seqno, ...)
  → PyMuPDF 底层数据, 未变换

Layer B — Atomic Observation Fact (Contract 候选):
  DRAWING_GEOMETRY_FACT: drawing_id, bbox, draw_type, item_count, item_types
  DRAWING_EXTENT_FACT: extent_id, bbox, width, height, area, primitive_count
  → 纯几何事实, closed schema, provenance-backed, deterministic

Layer C — Semantic Hypothesis / Interpretation (禁止):
  is_figure, is_table, is_chart, is_caption, is_flowchart,
  caption_of, figure_of, belongs_to_figure, semantic_role
  → 需 Hypothesis 层
```

### A → B 允许的转换

```
rect → bbox (_round_bbox, frozen P1 convention)         ALLOWED
type → draw_type (verbatim 's'/'f'/'fs')                ALLOWED
len(items) → item_count (pure count)                    ALLOWED
items ops → item_types (set of 'l'/'re'/'qu'/'c')       ALLOWED (type extraction, no args)
seqno → identity component                              ALLOWED

merge_nearby(bboxes, gap) → extent_bbox                 ALLOWED (geometric aggregation, params declared)
count(primitives in extent) → primitive_count           ALLOWED (pure count)
width/height/area from bbox                              ALLOWED (pure geometry)
```

### A → B 禁止的转换

```
items → raw passthrough (fitz objects, non-serializable)  FORBIDDEN
items → semantic shape classification                      FORBIDDEN
color → "blue_box = node"                                  FORBIDDEN
fill → "filled_rect = table_cell"                          FORBIDDEN
width → "thick_line = connector"                           FORBIDDEN
PNG render from region                                      FORBIDDEN
caption regex match                                         FORBIDDEN
"type": "image" label                                       FORBIDDEN
```

### B → C (Consumer 职责, 非 Observation)

```
DRAWING_GEOMETRY_FACT + DRAWING_EXTENT_FACT
  → Consumer computes distance/overlap/containment (bbox arithmetic)
  → Consumer forms hypothesis: "text near drawing + FIG-prefix → caption candidate"
  → Consumer validates hypothesis (human / counterfactual)
```

---

## 5. DRAWING_GEOMETRY_FACT Design

### 逐字段研究

| 字段 | Raw Evidence | Observation | Semantic Risk | 是否必要 | 结论 |
|------|-------------|-------------|---------------|---------|------|
| drawing_id | — | `DRAW\|{doc}\|p{page}\|{seqno}` | NO (纯函数 identity) | YES (determinism) | **INCLUDE** |
| document_id | PDF path | verbatim | NO | YES (provenance) | **INCLUDE** |
| page_reference | page index | int | NO | YES (provenance) | **INCLUDE** |
| bbox | get_drawings().rect | _round_bbox (frozen) | NO (纯坐标) | YES (core fact) | **INCLUDE** |
| draw_type | get_drawings().type | verbatim 's'/'f'/'fs' | NO (stroke/fill ≠ figure) | YES (primitive property) | **INCLUDE** |
| item_count | len(get_drawings().items) | int | NO (pure count) | YES (density signal) | **INCLUDE** |
| item_types | set(op[0] for op in items) | {'l','re','qu','c'} | NO (op type ≠ shape type) | YES (primitive characterization) | **INCLUDE** |
| items | get_drawings().items | — | LOW but HEAVY | NO (see §5.2) | **EXCLUDE** |
| stroke_color | get_drawings().color | (r,g,b) | LOW (color ≠ semantic) | NO (not minimal; P3 not in whitelist) | **EXCLUDE** |
| fill_color | get_drawings().fill | (r,g,b) | LOW | NO (same as color) | **EXCLUDE** |
| stroke_width | get_drawings().width | float | LOW (width ≠ connector) | NO (not minimal) | **EXCLUDE** |
| stroke_opacity | get_drawings().stroke_opacity | float | NO | NO (not minimal) | **EXCLUDE** |
| fill_opacity | get_drawings().fill_opacity | float | NO | NO (not minimal) | **EXCLUDE** |
| closePath | get_drawings().closePath | bool | NO | NO (not minimal) | **EXCLUDE** |
| dashes | get_drawings().dashes | list | NO | NO (not minimal) | **EXCLUDE** |
| lineCap | get_drawings().lineCap | tuple | NO | NO (not minimal) | **EXCLUDE** |
| lineJoin | get_drawings().lineJoin | float | NO | NO (not minimal) | **EXCLUDE** |
| layer | get_drawings().layer | str | LOW (layer name may be semantic) | NO | **EXCLUDE** |
| even_odd | get_drawings().even_odd | bool | NO | NO (not minimal) | **EXCLUDE** |
| seqno | get_drawings().seqno | int | NO (PDF sequence) | YES (identity component) | **INCLUDE (in drawing_id)** |

### 5.1 primitive_type 判定

```
draw_type = 's' (stroke) / 'f' (fill) / 'fs' (fill+stroke)
  → 纯 PDF rendering type, 不携带语义
  → 's' ≠ "line" ≠ "arrow" ≠ "connector"
  → 'fs' ≠ "filled box" ≠ "table cell"

item_types = {'l', 're', 'qu', 'c'}
  → 纯几何基元操作类型
  → 'l' = line operation, 're' = rectangle operation, 'qu' = quadratic, 'c' = cubic
  → 're' ≠ "rectangle shape" ≠ "table cell" ≠ "node"
  → 'l' ≠ "connector" ≠ "arrow"

ALLOW CANDIDATE
  draw_type 和 item_types 是底层 PDF geometry type, 不被解释为 semantic shape。
```

### 5.2 items 字段排除理由

```
items EXCLUDED because:

1. Schema 过重:
   - 每个 drawing 的 items 是变长 list of tuples
   - tuples 包含 fitz.Point/Rect/Quad (非 JSON-serializable)
   - 需要转换逻辑 (Point→(x,y), Rect→(x0,y0,x1,y1), Quad→4 points)
   - 转换逻辑本身需要 sha 锚定 → 额外 versioning

2. Provenance 难以维护:
   - items 的精确内容依赖 PyMuPDF 版本的 Point/Rect/Quad 表示
   - 跨版本可能不一致 → 破坏 determinism
   - bbox 已由 _round_bbox 稳定化, 但 items 的内部坐标无此保证

3. Deterministic replay 复杂化:
   - items 中的浮点数精度可能跨版本漂移
   - 序列化需要固定 key 序 + 固定精度 → 复杂

4. Consumer 依赖底层 PyMuPDF 结构:
   - 暴露 items → consumer 可能依赖 fitz 对象结构
   - 违反 closed schema 原则
   - 未来 PyMuPDF 版本变化 → consumer 破损

5. 信息替代:
   - item_count + item_types 提供足够的基元表征
   - bbox + draw_type + item_count + item_types ≥ 足够的 Observation
   - items 的精确坐标不增加判别性 (bbox 已包含范围)

替代方案: item_count (int) + item_types (sorted set of op strings)
  → 纯计数 + 纯类型集
  → JSON-serializable, deterministic, lightweight
```

### 5.3 color/fill/width 排除理由

```
color/fill/width EXCLUDED because:

1. 不在最小集合:
   - 当前研究问题是 "visual geometric existence"
   - color/fill/width 是 rendering 属性, 非几何存在性
   - P3 style (size/font/bold) 未暴露 (§13.3: P3 不在冻结白名单)
   - 同理: drawing color/fill/width 不应在最小 contract 中

2. 语义风险 (LOW but present):
   - stroke_color = (0,0,1) → consumer 可能推断 "blue = hyperlink"
   - fill = (0.9,0.9,0.9) → consumer 可能推断 "gray = table header"
   - 虽然这些是 consumer 推断 (非 Observation), 但暴露 color 增加 semantic leakage 风险

3. 可后续扩展:
   - 如果未来证明 color 对判别性必要, 可在 v2 contract 中增加
   - 当前 minimal contract 不包含

4. Anti-Bloat:
   - 不因为 "以后可能有用" 就加入
   - 当前 failure cases (M-A/M-B) 不依赖 color/fill/width
```

### 5.4 DRAWING_GEOMETRY_FACT 最终定义

```
[DC3 — DRAWING_GEOMETRY_FACT = ALL primitives, 无 pre-filter]

BOUNDARY: DRAWING_GEOMETRY_FACT 记录 page.get_drawings() 返回的全部 vector drawing
  primitives, 不执行任何 pre-merge filtering。

  即: 所有 seqno 的 drawing 都被记录, 包括:
    - 太小的 primitive (width < 15, height < 10) — 仍然记录
    - 页面边框 (x0 <= 5, y0 <= 5) — 仍然记录
    - 背景矩形 (width > 0.7 * page_width) — 仍然记录

  Pre-merge filter (min_width/min_height/border/ratio) 属于 DRAWING_EXTENT_FACT
  的 Stage 1 (pre-merge geometric filtering), NOT DRAWING_GEOMETRY_FACT。
  → DRAWING_GEOMETRY_FACT 是 raw observation (ALL primitives)
  → DRAWING_EXTENT_FACT 是 derived selection (filtered + merged)
  → 二者不混淆: raw observation 不携带 selection criteria

  这样设计的理由:
    - DRAWING_GEOMETRY_FACT 是 "expose-first" 的 raw observation
    - consumer 可能需要 ALL primitives (包括页面装饰线、边框)
    - 如果在 Observation 层 pre-filter → 丢失信息 → consumer 无法访问 raw data
    - filter 属于 Derived Selection (DRAWING_EXTENT_FACT), params declared

DRAWING_GEOMETRY_FACT (closed schema):

Content fields (5):
  drawing_id      = "DRAW|{document_id}|p{page_reference}|{seqno}"  (纯函数)
  bbox            = [x0, y0, x1, y1]  (_round_bbox, frozen P1 convention)
  draw_type       = "s" | "f" | "fs"  (verbatim from get_drawings().type)
  item_count      = int  (len(items))
  item_types      = sorted list of "l"|"re"|"qu"|"c"  (set of op types, sorted)

Provenance fields (7, same as existing AO pattern):
  document_id     = str
  page_reference  = int
  coordinate_system = "pymupdf_page_1.26.x_y_down"
  source_sha      = PyMuPDF version hash + extraction code sha
  params_hash     = definition hash (surface, fields, rounding — NO filter params)
  schema_version  = "1.0.0"
  pymupdf_version = str

geometry_source = "pymupdf:get_drawings"

params_hash NOTE: DRAWING_GEOMETRY_FACT 的 params_hash 不含 filter 参数
  (因为 DGF 记录 ALL primitives, 无 filter)
  → params_hash = sha256({"surface": "pymupdf:get_drawings",
     "fields": [drawing_id, bbox, draw_type, item_count, item_types],
     "rounding": "frozen _round_bbox"})

Forbidden fields:
  items (raw passthrough), color, fill, width, opacity, closePath,
  dashes, lineCap, lineJoin, layer, even_odd
  is_figure, is_table, is_chart, is_caption, caption_of, figure_of,
  semantic_role, confidence, score, ranking, decision
```

---

## 6. DRAWING_EXTENT_FACT Design

### 逐字段研究

| 字段 | 来源 | Observation? | Semantic Risk | 是否必要 | 结论 |
|------|------|-------------|---------------|---------|------|
| extent_id | 纯函数 | NO | YES (identity) | **INCLUDE** |
| bbox | merge_nearby output | YES (纯坐标) | NO | YES (core fact) | **INCLUDE** |
| width | bbox.x1 - bbox.x0 | YES (纯几何) | NO | YES (extent characterization) | **INCLUDE** |
| height | bbox.y1 - bbox.y0 | YES | NO | YES | **INCLUDE** |
| area | width * height | YES (纯几何) | NO | YES | **INCLUDE** |
| primitive_count | count of DRAWING_GEOMETRY_FACT in extent | YES (pure count) | NO | YES (density signal) | **INCLUDE** |
| constituent_seqnos | list of seqnos merged into extent | YES (identity trace) | NO | YES (provenance) | **INCLUDE** |
| merge_gap | merge_nearby parameter | YES (declared param) | NO | YES (params_hash) | **INCLUDE (in params_hash)** |
| density | primitive_count / area | DERIVED | LOW (high density → "figure"?) | NO (derived, not stored) | **EXCLUDE (derived)** |

### 6.1 是否重复 P2?

```
P2 GeometryObservation:
  - same_y_band, h_gap, v_gap, left_alignment_group, same_x_band
  - center_x, center_y, normalized_x/y
  - 输入: TEXT atoms (from P1)
  - 不处理: non-text drawing

DRAWING_EXTENT_FACT:
  - bbox, width, height, area, primitive_count
  - 输入: vector drawing primitives (from get_drawings())
  - 不处理: text

DUPLICATION_RISK = FALSE
  P2 = text geometry; DRAWING_EXTENT = vector geometry
  不同输入, 不同事实, 不重复
```

### 6.2 DRAWING_EXTENT_FACT 最终定义

```
[DC4 — DRAWING_EXTENT_FACT = declared geometric aggregation + declared geometric post-filter]

BOUNDARY: DRAWING_EXTENT_FACT 是 Derived Selection, 不是 raw observation。
  生成管线 (3 阶段, 全部纯几何):

    DRAWING_GEOMETRY_FACT (ALL primitives, raw observation)
        ↓
    Stage 1: pre-merge geometric filtering (6 params)
        → 过滤: min_width, min_height, border_x_thresh, border_y_thresh,
                 max_width_ratio, max_height_ratio
        → 纯几何条件: width/height/coordinate/ratio comparison
        ↓
    Stage 2: merge_nearby geometric aggregation (1 param: merge_gap)
        → 规则: expand_intersect (if expanded(r1, gap).intersects(r2): r1 = r1 | r2)
        → 纯几何: bbox expansion + intersection + union
        ↓
    Stage 3: post-merge geometric filtering (5 params)
        → 过滤: min_area, post_min_width, post_min_height,
                 post_max_w_ratio, post_max_h_ratio
        → 纯几何条件: area/width/height/ratio comparison
        ↓
    DRAWING_EXTENT_FACT (aggregated extent, closed schema)

  全部 3 阶段的全部 12 参数都是纯几何条件 (verified G3: 15/15 operations geometric)
  → NOT Figure Detection / Chart Detection / Flowchart Detection / Visual Object Detection
  → 所有条件只涉及: bbox, width, height, area, coordinate, intersection
  → 无任何语义判断: 不读 figure/image/caption/table/chart/text_meaning/semantic_role

DRAWING_EXTENT_FACT (closed schema):

Content fields (7):
  extent_id         = "DEXT|{document_id}|p{page_reference}|{hash(constituent_seqnos + params_hash)[:16]}"
  bbox              = [x0, y0, x1, y1]  (_round_bbox)
  width             = float  (bbox.x1 - bbox.x0)
  height            = float  (bbox.y1 - bbox.y0)
  area              = float  (width * height)
  primitive_count   = int  (count of DRAWING_GEOMETRY_FACT within extent)
  constituent_seqnos = sorted list of int  (seqnos of merged primitives)

Provenance fields (7, same pattern):
  document_id, page_reference, coordinate_system, source_sha,
  params_hash (12 params — see §8 Q3-DC2 for full definition),
  schema_version, pymupdf_version

geometry_source = "pymupdf:get_drawings + pre_filter + merge_nearby(gap=50) + post_filter"

Forbidden:
  density (derived, not stored), is_figure, is_visual_region, is_table,
  visual_complexity, semantic_role, confidence, score
```

---

## 7. TEXT_DRAWING_SPATIAL_RELATION Design

### 核心问题: Stored Fact vs Derived Fact

```
TEXT_DRAWING_SPATIAL_RELATION 候选字段:
  distance, overlap, containment, above/below/left/right

这些全部可由两个 bbox 计算:
  text_bbox (from P1 TEXT_ATOM) + drawing_bbox (from DRAWING_EXTENT_FACT)
  → distance = bbox arithmetic
  → overlap = bbox intersection
  → containment = bbox containment (IN_REGION bbox_containment_v1 已存在)
  → above/below/left/right = bbox position comparison
```

### Anti-Bloat 分析

```
Stored Fact 理由:
  - 如果 consumer 频繁查询 text-drawing 关系, materialize 可提升性能
  - 但: AO 设计原则是 "expose-first, query-on-demand", 非 "precompute all relations"

Derived Fact 理由:
  - text_bbox 已存在 (P1 TEXT_ATOM)
  - drawing_bbox 已存在 (DRAWING_EXTENT_FACT)
  - distance/overlap/containment 是平凡 bbox 运算 (无新测量)
  - IN_REGION (bbox_containment_v1) 已存在 — containment 是其子集
  - 存储 spatial relation = 存储可派生事实 = bloat

  AO CONTRACT §4: GAP_SEQUENCE 是 "measurement" (新测量, 非派生)
  TEXT_DRAWING_SPATIAL_RELATION 不是新测量 — 是两个 bbox 的算术
  → 不符合 "新测量" 标准
```

### 判定

```
TEXT_DRAWING_SPATIAL_RELATION = NOT JUSTIFIED

理由:
  1. 全部字段可由已有 bbox (P1 + DRAWING_EXTENT) 派生
  2. IN_REGION (bbox_containment_v1) 已覆盖 containment
  3. distance/overlap 是平凡 bbox 运算, 非 "新测量"
  4. 存储 = bloat (违反 Anti-Bloat)
  5. Consumer 可自行计算 (bbox arithmetic, 无需层支持)

替代: Consumer 从 P1 TEXT_ATOM.bbox + DRAWING_EXTENT_FACT.bbox 派生
  → 不需要 Observation Layer 存储
```

---

## 8. Merge / Aggregation Contract

### Q1: merge 是否属于 Observation?

```
YES — IF params declared

merge_nearby(rects, gap=50) 是纯几何聚合:
  - 输入: list of Rect (纯坐标)
  - 操作: if expanded(r1, gap).intersects(r2): r1 = r1 | r2
  - 输出: merged Rect (纯坐标)
  - 无语义判断 (不判断 "这些属于同一 figure")
  - 无内容恢复 (不渲染 PNG)
  - 无词法推断 (不 regex caption)

这是 geometric aggregation, 不是 semantic grouping。
```

### Q2: merge 的依据是什么?

```
依据: spatial proximity (distance < gap)
  - gap = 50pt (declared parameter)
  - 如果两个 drawing bbox 的扩展区域相交 → 合并
  - 纯空间近邻, 不依赖内容/语义

NOT 依据:
  - "属于同一 figure" (语义)
  - "是同一表格的线" (语义)
  - "是 flowchart 的连接" (语义)
```

### Q3: 参数是否必须显式声明?

```
YES — 必须在 params_hash 中声明

[DC1/DC2 — 完整记录 12 个参数, 来源: layout_analyzer.py:268-324 逐行审计]

DRAWING_EXTENT_FACT 的生成管线 (3 阶段, 12 参数):

  Stage 1 — Pre-merge geometric filtering (layout_analyzer.py:272-283):
    对每个 get_drawings() primitive, 过滤掉:
      - 太小的 primitive (min_width / min_height)
      - 页面边框 (border_x_thresh / border_y_thresh)
      - 背景矩形 (max_width_ratio / max_height_ratio)

    参数 (6):
      min_width         = 15.0    (L274: rect.width < 15 → skip)
      min_height        = 10.0    (L274: rect.height < 10 → skip)
      border_x_thresh   = 5.0     (L277: rect.x0 <= 5 → skip) [compound, see Q5-DC5]
      border_y_thresh   = 5.0     (L277: rect.y0 <= 5 → skip) [compound, see Q5-DC5]
      max_width_ratio   = 0.7     (L279: rect.width > page_rect.width * 0.7 → skip)
      max_height_ratio  = 0.5     (L281: rect.height > page_rect.height * 0.5 → skip)

    全部纯几何: width/height/coordinate/ratio comparison
    注意: 这 6 个参数属于 DRAWING_EXTENT_FACT 的 pre-merge filter,
          NOT DRAWING_GEOMETRY_FACT (后者记录 ALL primitives, 无 filter — 见 §5.4 DC3)

  Stage 2 — Merge geometric aggregation (layout_analyzer.py:286-315):
    对过滤后的 bboxes, 执行 expand_intersect 聚类:
      if expanded(r1, gap).intersects(r2): r1 = r1 | r2

    参数 (1):
      merge_gap         = 50.0    (L286/315: gap=50)

    纯几何: bbox expansion + intersection + union

  Stage 3 — Post-merge geometric filtering (layout_analyzer.py:320-324):
    对 merged extents, 过滤掉太小的或页面级背景:

    参数 (5):
      min_area          = 2000.0  (L251/322: area >= min_area)
      post_min_width    = 40      (L322: rect.width > 40)
      post_min_height   = 30      (L322: rect.height > 30)
      post_max_w_ratio  = 0.95    (L324: rect.width < page_rect.width * 0.95)
      post_max_h_ratio  = 0.95    (L324: rect.height < page_rect.height * 0.95)

    全部纯几何: area/width/height/ratio comparison

TOTAL: 12 parameters (6 pre-merge + 1 merge + 5 post-merge)
ALL 12 are purely geometric (no semantic info read — verified G3: 15/15 operations geometric)
```

### Q3-DC2: params_hash 闭包定义 (12/12 参数)

```
[DC2 — 所有 12 参数纳入 params_hash, 无遗漏]

params_hash = sha256(json.dumps({
  "surface": "pymupdf:get_drawings",
  "merge_rule": "expand_intersect",
  "pre_filter": {
    "min_width": 15.0,
    "min_height": 10.0,
    "border_x_thresh": 5.0,
    "border_y_thresh": 5.0,
    "max_width_ratio": 0.7,
    "max_height_ratio": 0.5
  },
  "merge_gap": 50.0,
  "post_filter": {
    "min_area": 2000.0,
    "post_min_width": 40,
    "post_min_height": 30,
    "post_max_w_ratio": 0.95,
    "post_max_h_ratio": 0.95
  },
  "rounding": "frozen _round_bbox"
}, sort_keys=True))

参数变化 → params_hash 变化 → 不同 version → deterministic replay 可区分
任何参数遗漏 → params_hash 不完整 → deterministic replay 不可复现 → 违反 AO §6

[DC5 — border_x_thresh / border_y_thresh 是 compound geometric parameter]
  border_x_thresh + border_y_thresh 共同构成 "page-edge boundary filter":
    if rect.x0 <= border_x_thresh AND rect.y0 <= border_y_thresh: skip
  这是一个 compound geometric condition (两个坐标条件的 AND):
    - 仅用于 geometric boundary filtering (排除页面边框)
    - NOT 解释为 figure boundary / visual boundary / object boundary
    - NOT 独立的 semantic parameter
  在 params_hash 中作为两个独立 float 声明 (border_x_thresh, border_y_thresh),
  但在设计文档中标记为 compound geometric parameter (page_edge_filter)
```

### Q4: merge 是否改变 primitive identity?

```
YES — 但 extent 是 NEW fact, 不是 replacement

原始: 12 DRAWING_GEOMETRY_FACT (each with seqno + bbox)
合并: 1 DRAWING_EXTENT_FACT (with constituent_seqnos = [1,2,3,...,12])

identity 变化:
  primitive identity (seqno) 在 extent 中丢失 → 但保留在 constituent_seqnos 中
  extent identity = hash(constituent_seqnos + merge_params) → 稳定 (只要 primitives + params 不变)

这不是 semantic grouping:
  - semantic grouping = "这些 primitives 属于同一 figure" (语义判断)
  - geometric aggregation = "这些 primitives 的 bbox 在 gap=50pt 内" (纯几何)

区分:
  DRAWING_GEOMETRY_FACT 保留 per-primitive identity (不变)
  DRAWING_EXTENT_FACT 是 additional fact (新增, 不替换)
  → 两者共存, consumer 可选择使用 primitive 或 extent
```

---

## 9. Field Closure

### OPEN SCHEMA vs CLOSED SCHEMA

```
CLOSED SCHEMA = SUPPORTED

理由:
  1. AO CONTRACT §2.2 NTB 已是 closed schema (固定字段集, content=null 永久)
  2. AO CONTRACT §3 RegionFact 已是 closed schema (字段封闭, 禁 semantic type)
  3. AO CONTRACT §4 Relations 已是 closed schema (输出封闭字段集)
  4. AO CONTRACT §12 "Explicit forbidden semantics" 强制扫描 = closed enforcement
  5. OPEN schema = raw passthrough → consumer 可读取 semantic labels → 破坏 boundary

Closed schema 要求:
  - 每个 fact type 有固定字段集 (allowlist)
  - 禁止 arbitrary fields
  - 禁止 raw_pymupdf_object / raw_detector_output / raw_layout_analyzer_dict
  - verify_determinism.py §K 扫描 forbidden semantics (已有, 需扩展覆盖新 fact types)
```

### Forbidden passthrough

```
FORBIDDEN:
  raw_pymupdf_drawing_dict (整个 get_drawings() 返回透传)
  raw_items (items list 透传, 含 fitz 对象)
  raw_layout_analyzer_output (chunker detect_images() 输出)
  raw_detector_state (任何 detector 内部状态)

理由: 这些包含 semantic labels / non-serializable objects / version-dependent structure
  → 破坏 closed schema → semantic leakage risk
```

---

## 10. Identity / Provenance / Determinism

### Identity

```
DRAWING_GEOMETRY_FACT identity:
  drawing_id = "DRAW|{document_id}|p{page_reference}|{seqno}"

  seqno: PyMuPDF get_drawings() 返回的 PDF-declared sequence number
  - stable across calls: YES [OBSERVED]
  - unique per page: YES [OBSERVED]
  - PDF-declared (not PyMuPDF-generated): YES [INFERRED from stability]

  依赖: (document_id, page_reference, seqno) → 稳定 identity
  风险: seqno 可能跨 PyMuPDF 版本变化 → 需在 source_sha 中记录 pymupdf_version

DRAWING_EXTENT_FACT identity:
  extent_id = "DEXT|{document_id}|p{page_reference}|{sha256(constituent_seqnos + params_hash)[:16]}"

  依赖: constituent_seqnos (来自 DRAWING_GEOMETRY_FACT) + merge params
  - 如果 primitives 不变 + params 不变 → extent_id 稳定
  - 如果 merge_gap 变化 → params_hash 变化 → extent_id 变化 (正确行为)
```

### Provenance (7-field pattern, same as existing AO)

```
每个 fact 受 7 字段约束 (AO CONTRACT §5):
  source_sha        = extraction code sha + PyMuPDF sha
  params_hash       = definition hash (surface, fields, params, rounding)
  schema_version    = "1.0.0"
  coordinate_system = "pymupdf_page_1.26.x_y_down"
  document_id       = str
  page_reference    = int
  pymupdf_version   = str

  timestamp/host/author 禁入 identity (与现有 AO 一致)
```

### Determinism (设计条件, 不执行测试)

```
Determinism 保证条件 (设计, 非验证):

  同 document + 同 PyMuPDF version + 同 extraction code + 同 params
  → 逐字节一致 (sort_keys=True serialization)

  保证机制:
  1. drawing_id = 纯函数 (document_id, page, seqno) — 无随机
  2. bbox = _round_bbox (frozen P1 convention) — 固定精度
  3. draw_type = verbatim from get_drawings() — 无变换
  4. item_count = len(items) — 纯计数
  5. item_types = sorted set — 固定序
  6. extent bbox = merge_nearby (deterministic: same input → same output) [OBSERVED]
  7. constituent_seqnos = sorted list — 固定序
  8. params_hash = sha256(json.dumps(definition, sort_keys=True)) — 固定序

  风险:
  - PyMuPDF 版本变化 → get_drawings() 返回可能变化 → source_sha 记录版本
  - merge_nearby 的 while-loop 顺序可能影响结果 → 但实测 deterministic [OBSERVED]
    (因为 merge 是 union 操作, 顺序不影响最终 bbox)

  Deterministic test 条件 (未来执行, 非现在):
  - 同 PDF 两次调用 → 逐字节一致
  - 不同 PDF → 不同结果 (正确)
  - 不同 merge_gap → 不同 params_hash → 不同 extent (正确)
```

---

## 11. Raster / Vector Boundary

### NON_TEXT_BLOCK_ATOM vs DRAWING_GEOMETRY_FACT

```
NON_TEXT_BLOCK_ATOM (existing):
  surface = page.get_text("dict").blocks[type != 0]
  covers = RASTER IMAGE blocks (PyMuPDF type=1)
  fields = atom_id, bbox, pdf_block_type, content=null
  identity = NTB|{doc}|p{page}|{block_index}

DRAWING_GEOMETRY_FACT (candidate):
  surface = page.get_drawings()
  covers = VECTOR DRAWING primitives (paths/lines/rects/curves)
  fields = drawing_id, bbox, draw_type, item_count, item_types
  identity = DRAW|{doc}|p{page}|{seqno}
```

### 是否属于同一 observation family?

```
YES — 同属 "non-text observation" family

  NON_TEXT_BLOCK_ATOM = raster non-text existence
  DRAWING_GEOMETRY_FACT = vector non-text geometry

  二者:
  - 不同 surface (get_text dict vs get_drawings)
  - 不同 identity scheme (block_index vs seqno)
  - 不同 content (null vs bbox/type/count)
  - 但同属 "non-text observation" — 都是 P1 跳过的内容

  不重新引入 VISUAL_REGION:
  - VISUAL_REGION = semantic region label ("这是 visual area") → FORBIDDEN
  - DRAWING_GEOMETRY_FACT = per-primitive geometric fact → ALLOWED
  - DRAWING_EXTENT_FACT = aggregated geometric extent → ALLOWED
  - 无 region_type / semantic label / visual_role

SEMANTIC / STRUCTURAL OVERREACH = FALSE
  不制造 "Visual Region" — 只暴露 per-primitive + aggregated geometry
```

---

## 12. Consumer Boundary

### Producer → Observation → Consumer

```
Producer (extraction code):
  reads get_drawings() → creates DRAWING_GEOMETRY_FACT
  reads DRAWING_GEOMETRY_FACT → merge → creates DRAWING_EXTENT_FACT
  → 纯几何提取 + 聚合, 无语义

Observation Layer (AO):
  stores DRAWING_GEOMETRY_FACT + DRAWING_EXTENT_FACT
  → closed schema, provenance, deterministic
  → 不调用 detector, 不做 semantic classification

Consumer (Evidence Organization / Hypothesis):
  reads DRAWING_GEOMETRY_FACT + DRAWING_EXTENT_FACT + P1 TEXT_ATOM
  → computes text-drawing distance/overlap (bbox arithmetic, derived)
  → forms hypothesis: "text near drawing + FIG-prefix → caption candidate"
  → validates hypothesis (human / counterfactual)
```

### Consumer 可以做什么

```
  - 查询 DRAWING_GEOMETRY_FACT by page → 获取页面所有 vector primitives
  - 查询 DRAWING_EXTENT_FACT by page → 获取聚合区域
  - 计算 P1 TEXT_ATOM.bbox ↔ DRAWING_EXTENT_FACT.bbox 的 distance/overlap (derived)
  - 声明 required_atoms / required_regions (闭集内, AO §10)
  - 形成 semantic hypothesis (hypothesis side, 非 Observation)
```

### Consumer 不得做什么

```
  - 不得要求 Observation Layer 产出 is_figure / is_caption / caption_of
  - 不得要求 Observation Layer 执行 PNG rendering / caption regex
  - 不得绕过 closed schema 读取 raw get_drawings() 返回
  - 不得修改 DRAWING_GEOMETRY_FACT / DRAWING_EXTENT_FACT schema
```

### Observation Producer 不得做什么

```
  - 不得替 Consumer 做语义解释
  - 不得产出 "image" / "figure" / "caption" label
  - 不得执行 caption regex / PNG rendering
  - 不得产出 confidence / score / ranking / decision
```

---

## 13. Anti-Bloat Analysis

### 逐项判定

| Candidate | 判定 | 理由 |
|-----------|------|------|
| DRAWING_GEOMETRY_FACT | **SUPPORTED** | 纯几何 per-primitive fact; 不重复 P2(text)/P6(text-span); 真实缺口 (vector 不存在); closed schema |
| DRAWING_EXTENT_FACT | **SUPPORTED** | 纯几何 aggregated fact; merge 是 geometric aggregation (params declared); 不重复 P2/P6; primitive_count 提供密度信号 |
| TEXT_DRAWING_SPATIAL_RELATION | **NOT JUSTIFIED** | 全部可由 P1.bbox + EXTENT.bbox 派生 (bbox arithmetic); IN_REGION 已覆盖 containment; 存储 = bloat |
| MERGED_DRAWING_EXTENT (as semantic region) | **FORBIDDEN** | 如果带 "visual_region" / "figure_region" label → 语义标签 → 违反 §12 |
| DRAWING_DENSITY (stored field) | **NOT JUSTIFIED** | density = primitive_count / area → 派生值 → consumer 计算, 不存储 |
| VISUAL_REGION | **FORBIDDEN** | P6 显式删除; 语义标签; "这是 visual area" → 违反 Observation ≠ Interpretation |
| RAW_PYMUPDF_PAYLOAD | **FORBIDDEN** | raw get_drawings() dict 透传 → 破坏 closed schema → semantic leakage risk |

### Anti-Bloat 原则遵守

```
不因为 "以后可能有用" 就加入:
  - items: 排除 (heavy, non-serializable, 可用 item_count+item_types 替代)
  - color/fill/width: 排除 (not minimal, P3 not in whitelist)
  - density: 排除 (derived, not stored)
  - TEXT_DRAWING_SPATIAL_RELATION: 排除 (derivable from bboxes)

只加入真实缺口:
  - DRAWING_GEOMETRY_FACT: vector primitive 不存在 → 真实缺口
  - DRAWING_EXTENT_FACT: vector aggregation 不存在 → 真实缺口

不重复已有:
  - P2 = text geometry → 不重复
  - P6 = text-span region → 不重复
  - AO NTB = raster image → 不重复 (不同 surface)
  - IN_REGION = bbox containment → 不重复 (不同对象)
```

---

## 14. Future Experiment Gate

### 未来进入 implementation / experiment 前必须满足的 Gate

```
G1 Contract approved
    AO CONTRACT §13 修订方案经 governance 审批
    §2.3 DRAWING_GEOMETRY_FACT + §2.4 DRAWING_EXTENT_FACT schema 确认
    → 当前状态: DESIGN PROPOSAL (本文件), 未审批

G2 Frozen baseline preserved
    P1-P7 / TLD / GT / frozen artifacts 不修改
    → 当前状态: INTACT (drift=0/7)

G3 Observation implementation authorized
    明确授权实现 DRAWING_GEOMETRY_FACT + DRAWING_EXTENT_FACT
    → 当前状态: NOT AUTHORIZED

G4 Deterministic / provenance validation defined
    determinism test 条件已设计 (§10)
    provenance 7-field pattern 已定义 (§10)
    verify_determinism.py §K 扫描扩展方案已定义 (覆盖新 fact types)
    → 当前状态: DEFINED (设计, 未执行)

G5 Negative cases available
    figure + ordinary paragraph / reference / footnote negative cases
    → 当前状态: NOT AVAILABLE (0 negative cases in corpus)

G6 Semantic boundary preserved
    no is_figure / is_caption / caption_of in schema
    no PNG rendering / caption regex in producer
    closed schema enforced
    → 当前状态: DESIGNED (本文件)

G7 Experiment object selected
    Mixed Layout (最合适) vs Figure/Caption vs Flowchart
    → 当前状态: NOT SELECTED

G8 Pre-registered evaluation rule
    proximity threshold + FIG-prefix combination rule
    success/failure criteria
    → 当前状态: NOT DEFINED
```

### Gate 状态总结

```
G1: DESIGN PROPOSAL (not approved)
G2: INTACT
G3: NOT AUTHORIZED
G4: DEFINED (not executed)
G5: NOT AVAILABLE
G6: DESIGNED
G7: NOT SELECTED
G8: NOT DEFINED

→ 8 Gates 中 0 个 fully satisfied
→ EXPERIMENT = NOT AUTHORIZED
```

---

## 15. Final Contract Proposal

### §13 修订方案 (DESIGN PROPOSAL, 非实际修改)

```
§13 Known limitations (修订):

1. [REVISED] 矢量绘图 (get_drawings) 覆盖 — 见 §2.3 DRAWING_GEOMETRY_FACT /
   §2.4 DRAWING_EXTENT_FACT。仅暴露纯几何事实 (bbox/type/count/extent);
   禁 items 透传 / OCR / 视觉解释 / 语义命名 / PNG 渲染 / caption regex。
2. raster 内容不可达 (无 OCR) — 仅 presence/bbox。 [UNCHANGED]
3. P3 style_signature 未暴露 (P3 函数不在冻结白名单)。 [UNCHANGED]
4. 截断 P2 artifact 只暴露 singles; GAP_SEQUENCE 拒绝截断数据。 [UNCHANGED]
5. 层不调用任何 detector; RegionFact 数据来自 detector 既有 artifact 的 Case A 暴露。 [UNCHANGED]
6. [NEW] drawing color/fill/width/opacity 未暴露 (非最小 contract; P3 style 未在冻结白名单)。
7. [NEW] drawing items 原始结构未暴露 (非 JSON-serializable; provenance 复杂; consumer 依赖 fitz 结构)。
8. [NEW] text-drawing spatial relation 未 materialized (可由 P1.bbox + EXTENT.bbox 派生; IN_REGION 已覆盖 containment)。
```

### §2.3 DRAWING_GEOMETRY_FACT (NEW)

```
§2.3 DRAWING_GEOMETRY_FACT [CONTRACT — 新增枚举面]

[DC3 — 记录 ALL primitives, 无 pre-filter]

BOUNDARY: 记录 page.get_drawings() 返回的全部 vector drawing primitives。
  不执行任何 pre-merge filtering (min_width/min_height/border/ratio 属于 §2.4)。
  → raw observation: ALL primitives exposed, no selection criteria applied
  → params_hash 不含 filter 参数 (只有 surface + fields + rounding)

| 允许字段 | 禁止字段 |
|---------|---------|
| drawing_id = "DRAW\|{doc}\|p{page}\|{seqno}" (纯函数) | 任何 "image/figure/chart" 词汇或语义 |
| document_id, page_reference | items 原始透传 (fitz 对象) |
| bbox (_round_bbox, frozen P1 convention) | color / fill / width / opacity |
| draw_type = "s"/"f"/"fs" (verbatim) | semantic role / region 归属预设 |
| item_count = int (len(items)) | "这是图形" 类判断 |
| item_types = sorted ["l"/"re"/"qu"/"c"] | density (derived, not stored) |
| coordinate_system, source_sha, params_hash (no filter params), schema_version, pymupdf_version | confidence / score / ranking / decision |
| ANY pre-merge filter param (min_width, border, ratio — 属于 §2.4) | |

枚举来源: page.get_drawings() — PyMuPDF 独立 API (不依赖 P1 block 层)。
seqno = PDF-declared sequence number (stable, unique per page)。
content = 不适用 (drawing 无 text content)。
ALL primitives recorded — 无 size/border/background 过滤。

稳定性声明: 若未来任何字段无法证明 generic → 删字段, 不加字段。
```

### §2.4 DRAWING_EXTENT_FACT (NEW)

```
§2.4 DRAWING_EXTENT_FACT [CONTRACT — 新增聚合面]

[DC4 — declared geometric aggregation + declared geometric post-filter]

BOUNDARY: Derived Selection (非 raw observation)。
  生成管线 (3 阶段, 12 参数, 全部纯几何):
    Stage 1: pre-merge geometric filtering (6 params)
    Stage 2: merge_nearby geometric aggregation (1 param)
    Stage 3: post-merge geometric filtering (5 params)
  全部条件: bbox/width/height/area/coordinate/intersection (纯几何)
  → NOT Figure/Chart/Flowchart/Visual Object Detection

| 允许字段 | 禁止字段 |
|---------|---------|
| extent_id = "DEXT\|{doc}\|p{page}\|{hash}" (纯函数) | VISUAL_REGION / FIGURE_REGION 语义类型 |
| document_id, page_reference | is_figure / is_table / is_visual |
| bbox (merged, _round_bbox) | density (derived, not stored) |
| width, height, area (纯几何派生) | PNG rendering / caption regex |
| primitive_count (count of DRAWING_GEOMETRY_FACT in extent) | "image" label / semantic classification |
| constituent_seqnos (sorted list of int) | confidence / score / decision |
| coordinate_system, source_sha, params_hash (12 params), schema_version, pymupdf_version | |

聚合来源: 3-stage geometric pipeline (pre_filter + merge_nearby + post_filter)。
  Stage 1 params: min_width=15, min_height=10, border_x_thresh=5, border_y_thresh=5,
                   max_width_ratio=0.7, max_height_ratio=0.5
  Stage 2 params: merge_gap=50
  Stage 3 params: min_area=2000, post_min_width=40, post_min_height=30,
                   post_max_w_ratio=0.95, post_max_h_ratio=0.95
[DC5] border_x_thresh + border_y_thresh = compound geometric parameter (page_edge_filter):
  仅用于 geometric boundary filtering (排除页面边框)
  NOT 解释为 figure boundary / visual boundary / object boundary

merge 是 geometric aggregation (非 semantic grouping)。
ALL 12 params MUST 在 params_hash 中声明 (见 §8 Q3-DC2)。
```

---

## 16. Remaining Semantic Gap

```
SEMANTIC_GAP_REMAINS = TRUE
```

### 即使有 DRAWING_GEOMETRY_FACT + DRAWING_EXTENT_FACT

```
仍无法仅凭 Observation 得到:

  Figure identity:
    "drawing extent with high primitive_count" ≠ "figure"
    (table border 也 high primitive_count)

  Caption identity:
    "text near drawing extent + FIG-prefix" ≠ "caption"
    (footnote 也 near drawing; "Table N:" 也有 prefix)
    → 需 Hypothesis: "FIG-prefix + proximity + specific gap range → caption candidate"
    → 需 validation: human / counterfactual

  Chart identity:
    "drawing with rect primitives" ≠ "chart"
    (table 也有 rect primitives)

  Flowchart identity:
    "connected paths + text in rects" ≠ "flowchart"
    (circuit diagram 也 connected)

  Table identity:
    "vector grid lines" ≠ "table"
    (figure border 也 lines)
```

### 必须形成的三步链

```
DRAWING_GEOMETRY_FACT + DRAWING_EXTENT_FACT (Observation)
        ↓
Evidence Organization (Consumer: query + bbox arithmetic + hypothesis)
        ↓
Semantic Hypothesis (Interpretation, validated by Human or counterfactual)

禁止:
  DRAWING_GEOMETRY_FACT → Figure Detector
  DRAWING_EXTENT_FACT → Visual Region
```

### Visual Geometry Observation 能打开什么?

```
打开:
  - "此页存在 vector drawing primitives" (存在性)
  - "primitives 聚合为 extent [x0,y0,x1,y1]" (位置)
  - "extent 内有 N 个 primitives" (密度信号)
  - consumer 可计算 text ↔ drawing 空间关系 (派生)

不打开:
  - "这是 figure" (语义)
  - "这是 caption" (语义)
  - "text 是 figure 的 caption" (语义关联)
  - "这是 flowchart" (语义)
```

---

## 17. Governance Status

### Q1: AO 是否适合作为 Vector Geometry Observation 的承载层?

```
YES — AO 是自然承载层
  - AO 已有 NON_TEXT_BLOCK_ATOM (raster non-text) → vector 是同 domain 扩展
  - AO 已有 closed schema pattern (NTB/RegionFact/Relations) → 新 fact types 遵循同一 pattern
  - AO 已有 provenance/determinism/params_hash 机制 → 新 fact types 复用
  - AO 已有 forbidden semantics 扫描 (§12/§K) → 新 fact types 纳入扫描
  - P2 (text geometry) / P6 (text-span region) 不适合 → AO 是唯一自然扩展点
```

### Q2: §13 应如何修订?

```
EXTEND §13 + ADD §2.3 / §2.4
  - §13.1 修订: 从 "不覆盖" 改为 "覆盖, 见 §2.3/§2.4"
  - §13.6-8 新增: color/fill/width/items/spatial-relation 未暴露的理由
  - §2.3 新增: DRAWING_GEOMETRY_FACT contract
  - §2.4 新增: DRAWING_EXTENT_FACT contract
  - 不创建新 section (vector 属于 AO non-text domain)
```

### Q3: 最小 Contract 是什么?

```
2 fact types, 11 content fields total:

DRAWING_GEOMETRY_FACT (5 content + 7 provenance):
  drawing_id, bbox, draw_type, item_count, item_types

DRAWING_EXTENT_FACT (6 content + 7 provenance):
  extent_id, bbox, width, height, area, primitive_count, constituent_seqnos
```

### Q4: 哪些字段必须删除?

```
从候选中删除:
  items (raw passthrough — heavy, non-serializable, provenance complex)
  stroke_color (not minimal, P3 not in whitelist)
  fill_color (same)
  stroke_width (same)
  stroke_opacity (not minimal)
  fill_opacity (not minimal)
  closePath (not minimal)
  dashes (not minimal)
  lineCap (not minimal)
  lineJoin (not minimal)
  layer (may be semantic)
  even_odd (not minimal)
  density (derived, not stored)
```

### Q5: 哪些字段应保持 derived?

```
Derived (consumer 计算, 不存储):
  density = primitive_count / area
  text_drawing_distance = bbox arithmetic (P1.bbox ↔ EXTENT.bbox)
  text_drawing_overlap = bbox intersection
  text_drawing_containment = IN_REGION (bbox_containment_v1, 已存在)
  spatial_position (above/below/left/right) = bbox comparison
```

### Q6: merge 是否属于 Observation?

```
YES — IF ALL 12 params declared in params_hash

  merge_nearby 是 geometric aggregation (纯空间近邻, 非语义分组)
  3-stage pipeline (12 params total):
    Stage 1: pre-merge geometric filtering (6 params: min_w, min_h, border_x, border_y, max_w_ratio, max_h_ratio)
    Stage 2: merge_nearby geometric aggregation (1 param: merge_gap)
    Stage 3: post-merge geometric filtering (5 params: min_area, post_min_w, post_min_h, post_max_w_ratio, post_max_h_ratio)
  ALL 12 params MUST 在 params_hash 中声明 (DC2 closure complete)
  merge 不改变 primitive identity (DRAWING_GEOMETRY_FACT 保留 ALL primitives)
  extent 是 NEW fact (DRAWING_EXTENT_FACT, 不替换 primitive)
  border_x_thresh + border_y_thresh = compound geometric parameter (DC5, page_edge_filter)
```

### Q7: 是否需要新的 Relation Observation?

```
NO — TEXT_DRAWING_SPATIAL_RELATION = NOT JUSTIFIED
  全部可由 P1.bbox + EXTENT.bbox 派生 (bbox arithmetic)
  IN_REGION (bbox_containment_v1) 已覆盖 containment
  存储 = bloat (违反 Anti-Bloat)
  consumer 可自行计算
```

### Q8: 如何保证 closed schema?

```
CLOSED SCHEMA = SUPPORTED
  - 每个 fact type 有固定字段集 (allowlist)
  - 禁止 arbitrary fields / raw passthrough
  - verify_determinism.py §K 扫描 forbidden semantics (扩展覆盖新 fact types)
  - 与现有 NTB/RegionFact/Relations 的 closed schema pattern 一致
```

### Q9: Visual Geometry Observation 能打开什么未来实验?

```
CONDITIONAL — 若授权:
  - M-A (caption association): 从 "VISUAL_REGION_EVIDENCE = MISSING" 转为 "AVAILABLE"
    → 可测试 text proximity + FIG-prefix 组合
    → 但仍需 negative cases + semantic gap acceptance
  - Mixed Layout: text/drawing 空间分区 (最接近纯几何)
    → 但无现有 failure cases
  - Flowchart: drawing density + connected paths
    → 但区分 flowchart vs figure 需语义
```

### Q10: 仍然无法解决什么?

```
  - Figure/Caption/Chart/Flowchart/Table identity (需 Hypothesis)
  - caption_of / figure_of 语义关系 (需 Interpretation)
  - prose vs table 区分 (M-B 问题不变 — visual geometry 不解决几何重叠)
  - 无 negative cases (corpus 缺口)
  - 无 flowchart/equation failure cases (观察空白)
```

---

## 最终状态

```text
AO_VISUAL_GEOMETRY_CONTRACT = CONDITIONAL

ARCHITECTURE_PLACEMENT = ATOMIC_OBSERVATION

MINIMAL_CONTRACT =
  1. DRAWING_GEOMETRY_FACT (5 content fields: drawing_id, bbox, draw_type, item_count, item_types)
  2. DRAWING_EXTENT_FACT (6 content fields: extent_id, bbox, width, height, area, primitive_count, constituent_seqnos)
  TEXT_DRAWING_SPATIAL_RELATION = NOT JUSTIFIED (derivable)

FIELD_CLOSURE = SUPPORTED (closed allowlist schema)

EXCLUDED_FIELDS =
  items (raw passthrough), color, fill, width, opacity, closePath,
  dashes, lineCap, lineJoin, layer, even_odd, density (derived)

MERGE_CONTRACT =
  geometric aggregation (not semantic grouping)
  3-stage pipeline: pre_filter(6) + merge(1) + post_filter(5) = 12 params
  ALL 12 params declared in params_hash (DC2 closure complete)
  extent = NEW fact (not replacement for primitives)

PARAMETER_CLOSURE = COMPLETE (12/12 params documented + in params_hash)
  Pre-merge: min_width, min_height, border_x_thresh, border_y_thresh,
             max_width_ratio, max_height_ratio
  Merge:     merge_gap
  Post-merge: min_area, post_min_width, post_min_height,
              post_max_w_ratio, post_max_h_ratio

DRAWING_GEOMETRY_FACT_BOUNDARY = ALL primitives (raw observation, no pre-filter)
DRAWING_EXTENT_FACT_BOUNDARY = 3-stage geometric pipeline (derived selection)
BORDER_FILTER_BOUNDARY = compound geometric parameter (page_edge_filter, not semantic)

IDENTITY =
  DRAWING_GEOMETRY_FACT: (document_id, page, seqno) — stable [OBSERVED]
  DRAWING_EXTENT_FACT: hash(constituent_seqnos + params_hash) — stable

§13 REVISION =
  §13.1: "不覆盖" → "覆盖, 见 §2.3/§2.4" (DESIGN PROPOSAL)
  §2.3: DRAWING_GEOMETRY_FACT contract (NEW)
  §2.4: DRAWING_EXTENT_FACT contract (NEW)
  §13.6-8: 新增排除字段理由

SEMANTIC_GAP_REMAINS = TRUE
  Visual Geometry ≠ Figure/Caption/Chart/Flowchart/Table identity

FUTURE_EXPERIMENT_ROUTE = CONDITIONAL
  G1-G8: 0/8 fully satisfied

DESIGN_RESEARCH_REQUIRED = TRUE (contract schema 细节 + determinism test 设计)

IMPLEMENTATION = NOT AUTHORIZED
EXPERIMENT     = NOT AUTHORIZED
FROZEN_BASELINE = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d)
PRODUCTION     = FALSE
RUNTIME_AUTHORITY = ZERO
STOP           = TRUE
```

---

## 研究原则遵守确认

- ✅ 只读代码检查 (get_drawings, non_text_block.py, CONTRACT.md, layout_analyzer.py)
- ✅ 未修改任何文件
- ✅ 逐字段研究 (5 content fields × semantic risk × necessity)
- ✅ items 排除有技术理由 (non-serializable, provenance complex, heavy)
- ✅ color/fill/width 排除有 Anti-Bloat 理由 (not minimal, P3 not in whitelist)
- ✅ TEXT_DRAWING_SPATIAL_RELATION 排除有 Anti-Bloat 理由 (derivable from bboxes)
- ✅ merge 判定为 geometric aggregation (params declared, not semantic grouping)
- ✅ closed schema (allowlist, no raw passthrough)
- ✅ identity/provenance/determinism 设计 (不执行 test)
- ✅ 不重新引入 VISUAL_REGION
- ✅ Negative Boundary 明确
- ✅ Consumer boundary 明确 (Producer 不替 Consumer 做语义)
- ✅ Anti-Bloat: 不因 "以后可能有用" 就加入
- ✅ 不自行进入 implementation
- ✅ DESIGN PROPOSAL (非实际修改)

`STOP = TRUE`。
