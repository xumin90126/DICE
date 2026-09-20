# P6 Observation Boundary Reassessment

> **模式: READ-ONLY / NO IMPLEMENTATION / NO EXPERIMENT EXECUTION / FROZEN INTACT / STOP**
> 日期: 2026-09-17
> 前置: `m_a_caption_association_readiness_review.md`（M-A = NOT_READY, VISUAL_REGION_EVIDENCE = MISSING）
> 本文件审查 P6 删除 VISUAL_REGION 的设计边界是否过度收缩。

---

## 1. Executive Summary

```
PRIMARY_DIAGNOSIS = C (OBSERVATION_SURFACE_TOO_NARROW)
SECONDARY          = D (REPRESENTATION_GAP)

P6_VISUAL_REGION_REMOVAL = OVERLY_BROAD
  P6 删除 VISUAL_REGION 时，把两个不同层次的边界合并了：
    A. Visual semantic identity ("这是 Figure/Table/Chart") — 正确禁止
    B. Visual geometric existence ("此区域存在非文本几何基元 + bbox") — 错误丢失

VECTOR_GEOMETRY_EVIDENCE = AVAILABLE_BUT_NOT_EXPOSED
  PyMuPDF page.get_drawings() 返回丰富的矢量几何数据（bbox, type, items: paths/lines/rects/quads）
  chunker/layout_analyzer.py:269 已调用 get_drawings() 并聚类为图片区域（但带语义解释）
  Observation 层（P6/AO/NTB）明确不覆盖 — declared as "documented limitation"
  → 底层存在，chunker 已用，但 Observation 层未暴露

P7 EVIDENCE GAP ANALYSIS 已独立确认:
  "5/6 文档含被跳过的视觉内容（94 图像 + ~2006 矢量对象）；视觉对象覆盖率 = 0%"
  "Visual Object Observation = 最大缺口"

DESIGN_RESEARCH_REQUIRED = TRUE
  存在设计层面的候选缺口：纯几何矢量观测 surface（bbox + primitive_count + extent，无语义标签）
  但不得自行实现、不得恢复 VISUAL_REGION、不得新增 schema

POTENTIAL_NEW_EXPERIMENT_ROUTE = CONDITIONAL_TRUE
  若未来授权纯矢量几何观测 surface，M-A 可能从 Representation Gap 转为可验证的
  Evidence Organization / Association 实验 — 但 SEMANTIC_GAP_REMAINS = TRUE
  （visual extent + text proximity + FIG-prefix 仍不足以完全区分 caption vs ordinary text）

SAFE_ALGORITHM_ROUTE = NOT_CURRENTLY_AVAILABLE (不变)
  本审查不改变上轮结论。只识别设计缺口，不授权任何行动。
```

---

## 2. Historical P6 VISUAL_REGION Removal Decision

### 2.1 删除记录 [OBSERVED]

来源: `tmp/perception/p6/region_schema.json`:

```json
"deleted_region_types": {
  "TEXT_REGION": "requires semantic text-vs-nontext knowledge; P1 has only text spans; collides with DENSE_REGION.",
  "VISUAL_REGION": "requires identifying image/figure/table; P1 has only text spans; a void is not a visual object; '这是 Image' forbidden."
}
```

来源: `tmp/perception/p6/p6_validation_report.md` §7:

> TEXT_REGION and VISUAL_REGION were deleted because they require semantic
> interpretation (text-vs-nontext / image-vs-whitespace) that P1-P5 geometric
> facts cannot determine.

来源: P6 design principles:

> Region taxonomy is geometric ONLY (no heading/title/body/caption/table/
> image/formula/flowchart/page_number/header/footer).

### 2.2 删除原因分解

```
P6_VISUAL_REGION_REMOVAL_REASON:

1. 为什么删除？
   → "requires identifying image/figure/table" — 认为视觉区域需要语义识别

2. 删除解决了什么风险？
   → 防止 P6（geometric region layer）产出语义标签（"这是 Image"）
   → 保持 Observation ≠ Interpretation 原则
   → 防止 "a void is not a visual object"（空白不是视觉对象）

3. 删除依赖什么假设？
   → 假设: P1 只有 text spans → P6 无法从 text 推断 visual region
   → 假设: visual region 必须语义识别（image/figure/table）
   → 假设: 没有其他 surface 能提供非文本几何事实

4. 当时是否考虑 vector drawing？
   → NO [OBSERVED]: P6 validation report 无 vector drawing 讨论
   → non_text_block.py 明确: "vector drawings (page.get_drawings) are NOT covered"
   → AO CONTRACT §13: "矢量绘图 (get_drawings) 不覆盖 — 与冻结 P1 block 层同一 surface 限制"
   → 删除时假设 "visual region = semantic identification"，未考虑 "vector geometry = pure observation"

5. 当时是否区分 "visual existence" 与 "visual semantic identity"？
   → NO [OBSERVED]: 删除理由将二者合并
   → "requires identifying image/figure/table" = 把 "存在视觉内容" 等同于 "识别为 figure/table"
   → 未考虑: "此区域有 N 个矢量基元，bbox [x0,y0,x1,y1]" 是纯几何观测，不需要语义识别

6. 当前哪些真实失败暴露了该设计边界？
   → M-A: 2 个 caption MERGE case (med_001 p20/p24) — 图是矢量绘制，NTB=0
   → M-B: TLD page-global contamination — 矢量表格（eff p5-p8）无 NTB
   → P7 Evidence Gap Analysis: 5/6 文档含被跳过视觉内容（94 图像 + ~2006 矢量对象）
   → chunker/layout_analyzer.py 已用 get_drawings() 但 Observation 层未暴露
```

---

## 3. Why the Original Decision Was Reasonable

删除 VISUAL_REGION 的**动机**是正确的:

1. **P6 是几何 region 层，不是语义分类层** — 正确。P6 不应输出 "这是 Image"。
2. **"a void is not a visual object"** — 正确。P6 从 text spans 推断 region，文本空白不等于视觉对象。
3. **防止语义泄漏** — 正确。P6 如果输出 VISUAL_REGION，会暗示 "这是 figure/image"，违反 Observation ≠ Interpretation。
4. **P1 只提取 text spans** — 事实正确。P1 `atomic_text.py` 显式跳过 `block_type != 0`。

**删除的动机合理，但删除的范围过宽。**

---

## 4. What New Failures Exposed

### 4.1 M-A Caption Association [OBSERVED]

- 2 个 MERGE case (med_001 p20/p24): 图是矢量绘制
- NTB = 0 (non_text_block 只覆盖 raster image, type != 0)
- VISUAL_REGION 被 P6 删除 → 无法表达 "图存在 + 位置"
- → M-A 无法确认 "文本在图附近" 这一关联前提

### 4.2 M-B Table Locality [OBSERVED]

- efficientnet p5-p8: 矢量表格无 NTB
- TLD page-global contamination 部分源于无法定位表格的视觉边界
- → 但 M-B 的核心问题是 prose=table 几何重叠，非视觉缺失（见 §11）

### 4.3 P7 Evidence Gap Analysis [OBSERVED, 独立确认]

```
6 个真实文档检测:
  94 raster images + ~2006 vector objects 被 P1 完全跳过
  5/6 文档含被跳过的视觉内容
  arxiv_2310: 18/19 页受影响
  视觉对象覆盖率 = 0%
```

P7 Evidence Gap Analysis 结论: "Visual Object Observation = 最大缺口"。

### 4.4 chunker/layout_analyzer.py 已用 get_drawings() [OBSERVED]

```python
# chunker/layout_analyzer.py:269 (sha 8f69f0d2, frozen)
drawings = page.get_drawings()
# → 聚类为 image_regions
# → 渲染 PNG
# → regex 匹配 "Fig|图|Figure|Table" 找 caption
```

chunker 已在**生产 chunking 管线**中使用 get_drawings()，但:
- 带语义解释（"image", "caption" 标签）
- 渲染 PNG（视觉内容恢复）
- regex caption 匹配（语义推断）
- 不在 Observation 层暴露（不供 P1-P7/AO 查询）

→ **信息存在且已被使用，但未作为纯 observation 暴露给 Evidence 层。**

---

## 5. Observation Boundary Matrix

| Candidate Observable | 是否已有 | 来源 | 是否 Frozen | 是否纯 Observation | 是否 Semantic | 是否可能复用 |
|---|---|---|---|---|---|---|
| raster image bbox | YES | non_text_block (NTB) | YES | YES | NO | YES |
| **vector drawing bbox** | **AVAILABLE_BUT_NOT_EXPOSED** | PyMuPDF get_drawings() | NO (not in AO) | **YES** | **NO** | **YES** |
| **vector drawing primitive (path/line/rect/quad)** | **AVAILABLE_BUT_NOT_EXPOSED** | PyMuPDF get_drawings().items | NO | **YES** | **NO** | **YES** |
| non-text primitive extent | AVAILABLE_BUT_NOT_EXPOSED | get_drawings() rect aggregation | NO | YES | NO | YES |
| text region bbox | NO (TEXT_REGION deleted) | P6 deleted | — | YES (if geometric) | NO (if "text" label) | PARTIAL |
| text/non-text spatial relation | NO | not computed | NO | YES (containment/overlap) | NO | YES |
| visual density (primitive count per area) | NO | derivable from get_drawings | NO | YES | NO | YES |
| primitive count | NO | derivable from get_drawings | NO | YES | NO | YES |
| region containment | PARTIAL | AO IN_REGION (bbox_containment_v1) | YES | YES | NO | YES |
| reading-order relation | PARTIAL | P5 column groups | YES | YES | NO | PARTIAL (no full sequence) |
| caption-like text | NO | FIG-prefix 词法 | — | **NO** (interpretation) | **YES** | NO (must stay hypothesis) |
| figure identity | NO | — | — | NO | **YES** | NO |
| table identity | NO | — | — | NO | **YES** | NO |
| chart identity | NO | — | — | NO | **YES** | NO |

### 关键发现

**纯观测性 Visual Evidence 候选**（bbox / primitive_count / extent / spatial_relation）:
- 全部 AVAILABLE_BUT_NOT_EXPOSED
- 全部 YES for 纯 Observation（不含语义标签）
- 全部 NO for Semantic
- 全部 YES for 可能复用

**语义标识候选**（caption-like / figure / table / chart identity）:
- 全部 SEMANTIC = TRUE
- 不得包装为 Observation

---

## 6. Vector Drawing Analysis

### 6.1 PyMuPDF 能力 [OBSERVED, 实测]

```python
page.get_drawings() → List[dict]
  每个 dict 包含:
    - rect: Rect (bbox) — 纯几何
    - type: 's' (stroke) / 'f' (fill) / 'fs' (fill+stroke) — 纯类型
    - items: [('l', p1, p2), ('re', rect), ('qu', quad)] — 纯基元
    - color, fill, width, opacity — 纯样式
    - layer, seqno — 纯序号
```

实测 (arxiv_2402.18619):
- Page 28 (含 Fig.14): 216 drawings, extent [73,77,522,338], items: {qu, l, re}
- Page 1 (text): 15 drawings
- Page 31 (references): 137 drawings

### 6.2 当前 DICE 覆盖状态

```
VECTOR_GEOMETRY_EVIDENCE = AVAILABLE_BUT_NOT_EXPOSED
```

| 层 | 是否覆盖 vector drawing | 证据 |
|----|----------------------|------|
| P1 atomic_text | NO | `if block_type != 0: skip` (atomic_text.py:256) |
| P2 geometry | NO | 只处理 text span 的 pairwise/single geometry |
| P6 region | NO | VISUAL_REGION deleted; 只有 PAGE_TOP/BOTTOM/FULL_WIDTH/COLUMN/DENSE/SPARSE/UNKNOWN |
| AO NON_TEXT_BLOCK | NO | "vector drawings (page.get_drawings) are NOT covered" (CONTRACT §13) |
| chunker/layout_analyzer | **YES** (but semantic) | `detect_images()` calls get_drawings(), clusters, renders PNG, regex caption — sha 8f69f0d2 frozen |

### 6.3 关键区分

```
可以观察 (pure observation):
  - drawing primitive bbox (rect)
  - primitive type (stroke/fill)
  - primitive items (line/rect/quad/path)
  - primitive count per region
  - drawing extent (aggregated bbox)
  - text/drawing spatial relation (overlap/containment/proximity)

不能直接观察 (semantic interpretation):
  - "这是 figure"
  - "这是 chart"
  - "这是 flowchart"
  - "这是 table border"
```

---

## 7. Observation vs Interpretation Boundary

### 7.1 允许的纯观测

```
bbox                    — vector drawing 的 rect（纯坐标）
extent                  — 聚合后的 drawing 区域范围（纯坐标）
primitive_count         — 某区域内 drawing 基元数量（纯计数）
line_count              — line 基元数量
rectangle_count         — rectangle 基元数量
path_extent             — path 的 bbox 范围
text/non-text overlap   — text bbox 与 drawing bbox 的重叠（纯几何）
distance                — text bbox 到 drawing bbox 的距离（纯几何）
containment             — text bbox 是否在 drawing extent 内（纯几何）
spatial adjacency       — text 与 drawing 的空间邻接关系（纯几何）
```

### 7.2 禁止的语义输出

```
is_figure / is_table / is_chart / is_caption / is_flowchart /
caption_of / figure_contains / table_contains / semantic_role
```

除非已有 frozen schema 明确允许 — 当前无。

### 7.3 chunker/layout_analyzer 的边界违反

`detect_images()` 做了以下语义操作:
- 标记为 "image" (语义标签)
- regex 匹配 "Fig|图|Figure|Table" 找 caption (语义推断)
- 渲染 PNG (视觉内容恢复)
- 排除 "图内文本" (语义决策)

**这些在 chunker（生产管线）中是可接受的**（chunker 的职责就是做 chunking 决策）。
**但在 Observation 层中是禁止的**（Observation ≠ Interpretation）。

→ 如果未来暴露 vector geometry，必须以**纯几何事实**形式暴露，
不得复制 chunker 的语义操作。

---

## 8. Minimal Visual Evidence Candidates

**审查候选名称，不是授权实现。不新增 schema，不写代码。**

### 候选 1: DrawingGeometryFact

```
纯观测性: drawing primitive 的 bbox + type + count
语义性: NO（不输出 "这是 figure"）
可测量: YES（get_drawings() 返回 rect, type, items）
确定性: YES（纯函数 of PDF + PyMuPDF version）
provenance: YES（source_sha = PyMuPDF version + extraction code sha）
```

### 候选 2: TextVisualSpatialRelation

```
纯观测性: text bbox 与 drawing extent 的空间关系（overlap/distance/containment）
语义性: NO（不输出 "text 是 caption of figure"）
可测量: YES（bbox 间几何计算）
确定性: YES
provenance: YES（text source = P1, drawing source = get_drawings）
```

### 候选 3: DrawingDensityFact

```
纯观测性: 某区域内 drawing primitive 密度（count / area）
语义性: NO（不输出 "这是 dense figure region"）
可测量: YES
确定性: YES
provenance: YES
```

### 不提候选: VisualRegion / FigureRegion / CaptionRegion

```
原因: 这些携带语义标签（"visual", "figure", "caption"）
      违反 Observation ≠ Interpretation
      不应作为 Observation 层输出
```

---

## 9. P2 / P6 / Atomic Observation Boundary

### 9.1 与 P2 的关系

```
P2: text span 的 pairwise/single geometry (same_y_band, h_gap, left_alignment_group, ...)
    → 只处理 TEXT atoms 的几何关系

Visual Observation: non-text drawing primitive 的 geometry (bbox, extent, count)
    → 处理 NON-TEXT 几何事实

DUPLICATION_RISK = FALSE
  P2 只处理 text；Visual Observation 只处理 non-text drawing
  二者不重复

NO_NEW_INFORMATION = FALSE
  Visual Observation 提供 P2 当前没有的 vector/non-text primitive facts
  P2 无法从 text span 推断 drawing 的存在或位置

NEW_EVIDENCE_CLASS = POSSIBLE
```

### 9.2 与 P6 的关系

```
P6: geometric region from P4 spans + P5 column layout
    → 基于 text spans 聚类为 PAGE_TOP/BOTTOM/FULL_WIDTH/COLUMN/DENSE/SPARSE/UNKNOWN
    → VISUAL_REGION 被删除

Visual Observation: non-text drawing geometry
    → 不依赖 text spans
    → 不输出 region_type 语义标签

是否应属于 P6？
  → NO [INFERRED]: P6 的设计原则是 "from P4 spans + P5 column layout"
  → Visual Observation 的输入是 get_drawings()，不是 text spans
  → 放入 P6 会破坏 P6 的 "text-span-based region" 设计一致性

是否应属于 Atomic Observation？
  → POSSIBLE [INFERRED]: AO 已有 NON_TEXT_BLOCK_ATOM（raster image）
  → Vector drawing 是 NON_TEXT_BLOCK_ATOM 的自然扩展（同属 non-text surface）
  → 但 AO CONTRACT 明确 "vector drawings 不覆盖" — 需修订 CONTRACT
  → 修订 CONTRACT = 设计决策，需授权
```

### 9.3 架构归属

```
ARCHITECTURAL_PLACEMENT = UNRESOLVED
  候选: Atomic Observation 层扩展（NON_TEXT_BLOCK_ATOM → 增加 vector drawing）
  候选: 新独立层（DrawingObservation）
  候选: P6 扩展（但破坏 text-span-based 设计）
  → 不强行决定。需 Design Research。
```

---

## 10. Real Failure Case Analysis

### 10.1 M-A 两个 caption MERGE cases

| 证据 | AMB-414 (med p20) | AMB-422 (med p24) |
|------|-------------------|-------------------|
| vector content | YES (矢量图) | YES (矢量图) |
| text blocks | YES ("FIG. 9:", "Left:") | YES ("FIG. 12:", "Distribution...") |
| P2 geometry | YES (same_y_band, h_gap 18.11/10.47) | YES |
| P5 reading order | PARTIAL (column groups only) | PARTIAL |
| P3 style | EXISTS but not used | EXISTS but not used |
| P6 region | DENSE/SPARSE (no VISUAL) | DENSE/SPARSE |
| NTB (raster) | 0 | 0 |
| **vector drawing geometry** | **MISSING (not exposed)** | **MISSING (not exposed)** |

**到底缺什么？**

缺的是: **vector drawing 的存在 + 位置 (bbox/extent)**。
- 如果有 drawing extent，可以计算 "FIG. 9:" text bbox 与 drawing extent 的空间关系
- 如果 text 在 drawing 附近 (distance < threshold)，这是 caption association 的**纯几何证据**
- 当前无法做此计算 → 无法形成关联证据

**缺的是 Query / Organization / Association 还是 Evidence？**

缺的是 **Evidence (vector drawing geometry)**，不是 Query。
CC-01 说 EXPRESSIBLE=YES 的前提是 "NTB presence" — 但 NTB=0。
如果有 vector drawing geometry，CC-01 的关联查询才真正可执行。

### 10.2 M-B table cases

| 证据 | 状态 |
|------|------|
| vector content | YES (矢量表格线) |
| text blocks | YES |
| P2 geometry | YES (45/45 sufficient) |
| vector drawing geometry | MISSING (not exposed) |

**Visual observation 是否有助于 table？**

**PARTIALLY [INFERRED]**:
- 矢量表格线（rect/line 基元）可作为表格区域证据
- 但 M-B 的核心问题是 prose=table 几何重叠（DCE-07 PROVEN）
- Visual observation 可能帮助**定位表格边界**（drawing dense region）
- 但**不能区分 prose 与 table 的内容**（prose 也在 drawing 附近？不一定）
- → Visual observation 对 M-B 有**边际帮助**，但不解决核心问题

**不扩大适用范围**: Visual observation 不是 M-B 的解药。M-B 的核心问题（prose 几何 = table 几何）不会因增加 drawing bbox 而消失。

---

## 11. Figure / Caption Assessment

### 如果有 Visual Geometry Evidence，Figure/Caption 任务能得到什么？

```
visual extent (drawing bbox)
  + caption candidate proximity (text bbox ↔ drawing extent distance)
  + text/non-text spatial relation (overlap/containment/adjacency)
  + FIG-prefix 词法 (hypothesis side)
```

**是否足够区分 caption vs ordinary text？**

```
HELPFUL — visual extent + proximity 提供了 "文本在图附近" 的纯几何证据
          → 这是当前完全缺失的维度
          → 可排除 "不 near figure 的文本" (减少 false association)

INSUFFICIENT — "near figure" ≠ "caption"
              → footnote 也 near figure
              → reference 也可能 near figure
              → continuation paragraph 也可能 near figure
              → 仍需 FIG-prefix 词法 + 可能 style 辅助
```

---

## 12. Flowchart Assessment

### 如果有 Visual Geometry Evidence，Flowchart 任务能得到什么？

```
drawing primitive distribution (line/rect/quad count + density)
  + connected visual geometry (paths connecting rectangles)
  + text/drawing relationship (text inside drawing rects)
```

**是否足够？**

```
HELPFUL — primitive count + distribution 可识别 "drawing-dense region"
          → 这是 flowchart/figure/chart 的共同特征
          → 当前完全无法观测

INSUFFICIENT — "drawing-dense region" ≠ "flowchart"
              → figure 也 drawing-dense
              → chart 也 drawing-dense
              → table border 也 drawing-dense
              → 区分 flowchart vs figure vs chart 需语义理解

UNKNOWN — 是否有纯几何信号区分 "connected paths"（flowchart）vs "isolated rects"（figure）？
          → 需 Design Research，当前无证据
```

---

## 13. Mixed Layout Assessment

### 如果有 Visual Geometry Evidence，Mixed Layout 任务能得到什么？

```
text region (P6 COLUMN/DENSE/SPARSE)
  + non-text region (drawing extent)
  + spatial partition (text vs drawing 的空间分布)
```

**是否足够？**

```
HELPFUL — text/drawing 空间分区可识别 "此区域是图，此区域是文本"
          → 有助于 page-level layout 理解
          → 可解释 P6 的 "大间隙"（当前 deferred to P7）

INSUFFICIENT — "drawing region" ≠ "figure region"
              → 仍需语义识别

但: Mixed Layout 的需求更接近纯几何（空间分区），比 Figure/Caption 更不需要语义
```

---

## 14. Semantic Gap Assessment

> 即使拥有 Visual Geometry Evidence，Figure/Caption association 是否仍然需要 semantic understanding？

**YES — SEMANTIC_GAP_REMAINS = TRUE**

### 分析

即使有:
```
visual region exists (drawing extent bbox)
  + text is nearby (distance < threshold)
  + text has FIG prefix ("FIG. 9:")
```

**仍然需要区分**:
- caption (label + description of figure) — 应 MERGE
- footnote (text near figure but not caption) — 应 KEEP_SEPARATE
- source note (text near figure citing source) — 应 KEEP_SEPARATE
- continuation paragraph (text near figure but different paragraph) — 应 KEEP_SEPARATE
- reference (text near figure citing reference) — 应 KEEP_SEPARATE

FIG-prefix 是强信号但**不完美**:
- "FIG. 9:" + "Left:" → caption (MERGE) ✓
- "FIG. 9:" + nearby reference text → 可能误 MERGE ✗
- "Table 3" + nearby text → 不是 figure caption

### 但: Semantic Gap 比当前状态小

当前: 无 visual evidence → 完全无法判断 "near figure"
有 visual evidence: 可判断 "near figure" → 缩小到 FIG-prefix + proximity 组合
→ 仍需 semantic 判断，但**可测试的 Evidence 组合更丰富**

```
SEMANTIC_GAP_REMAINS = TRUE
但 GAP_SIZE < 当前 (从 "完全无 visual evidence" 缩小到 "visual + proximity + prefix")
```

---

## 15. Potential New Experiment Route

### 如果增加纯 Visual Observation Surface

```
当前状态:
  Representation Gap → Visual evidence missing → M-A NOT_READY

如果未来授权 visual geometry observation:
  Visual evidence exists (drawing bbox + extent)
    ↓
  Association query can be tested (text bbox ↔ drawing extent proximity)
    ↓
  Counterfactual cases can be constructed (figure + caption vs figure + footnote vs figure + reference)
    ↓
  Semantic leap can be REDUCED (from "geometry → caption" to "proximity + prefix → caption candidate")
    ↓
  但 semantic leap NOT ELIMINATED (proximity + prefix ≠ caption)
```

```
POTENTIAL_NEW_EXPERIMENT_ROUTE = CONDITIONAL_TRUE
  条件:
    1. 授权新 visual geometry observation surface (设计 + 实现)
    2. 构造 negative case set (figure + footnote / reference / continuation)
    3. 预注册 proximity threshold + FIG-prefix 组合规则
    4. 证明 semantic gap 可接受 (或需 human validation 补充)
```

**禁止提前称为 EXPERIMENT_READY。** 以上是条件性路线，非授权。

---

## 16. Primary Diagnosis

```
PRIMARY   = C (OBSERVATION_SURFACE_TOO_NARROW)
SECONDARY = D (REPRESENTATION_GAP)
```

### 诊断理由

```
C (OBSERVATION_SURFACE_TOO_NARROW):
  P6 删除 VISUAL_REGION 时，把 "visual semantic identity"（正确禁止）
  与 "visual geometric existence"（错误丢失）合并为一个决策。
  纯几何的 vector drawing observation（bbox/extent/count，无语义标签）
  在 PyMuPDF 中 AVAILABLE，被 chunker 使用，但未被 Observation 层暴露。
  → Observation surface 过窄。

D (REPRESENTATION_GAP):
  即使 vector geometry 被暴露，Figure/Caption 仍需要语义判断
  (proximity + prefix ≠ caption)。
  → Representation 层仍有 gap（无法表达 "caption_of" 语义关系）。
  但 D 是 SECONDARY — 先解决 C，才能评估 D 的严重程度。
```

### 不选其他分类的理由

```
A (CURRENT_OBSERVATION_SUFFICIENT): NO — vector geometry 明确 MISSING
B (EVIDENCE_QUERY_GAP): PARTIAL — 但核心是 Evidence 不存在，非 Query 不够
E (SEMANTIC_GAP): TRUE 但是 SECONDARY — 先有 visual evidence 才能评估 semantic gap
F (MIXED): C + D 的组合
G (UNKNOWN): NO — 诊断清晰
```

---

## 17. Architecture Implication

### 当前架构缺口

```
PDF
  ↓
PyMuPDF
  ├── get_text("dict") blocks[type=0]  → P1 AtomicText → P2/P3/P4/P5/P6 → AO TEXT_ATOM
  ├── get_text("dict") blocks[type!=0] → AO NON_TEXT_BLOCK_ATOM (raster only)
  ├── get_drawings()                   → ★ NOT IN ANY OBSERVATION SURFACE ★
  └── get_images()                     → chunker detect_images() (semantic, not AO)
```

### 候选架构方向（不授权，仅记录）

```
选项 A: 扩展 AO NON_TEXT_BLOCK_ATOM → 增加 vector drawing enumeration
  优点: 与现有 NTB 设计一致（同属 non-text surface）
  缺点: 需修订 AO CONTRACT §13（"vector drawings 不覆盖"）
  风险: vector drawing 数量大（216/页），需设计聚合策略

选项 B: 新独立 DrawingObservation 层
  优点: 不影响现有 AO/P6
  缺点: 新增层 = 架构复杂度

选项 C: P6 扩展（恢复几何版 VISUAL_REGION，如 DRAWING_DENSE_REGION）
  优点: 与 P6 region 体系一致
  缺点: P6 基于 text spans；drawing 不是 text span；设计不一致
  风险: 语义泄漏（DRAWING_DENSE → 暗示 "这是 figure"）

ARCHITECTURAL_PLACEMENT = UNRESOLVED
  需 Design Research，不强行决定。
```

---

## 18. What Is NOT Authorized

```
NOT AUTHORIZED:
  - 恢复 VISUAL_REGION（P6 设计决策，需显式授权修订）
  - 新增 observation schema
  - 新增 detector
  - 修改 P2 / P6 / P7 / TLD / GT / frozen artifact
  - 修改 AO CONTRACT
  - threshold tuning
  - LLM / semantic classifier
  - caption / figure / table / flowchart classifier
  - 执行任何新实验
  - 写代码
  - 修改 chunker/layout_analyzer.py（frozen, 8f69f0d2）
```

---

## 19. Final Recommendation

```
DESIGN_RESEARCH_REQUIRED = TRUE
```

### 建议方向（不授权执行）

1. **Design Research: 纯几何 Vector Drawing Observation Surface**
   - 研究问题: 如何以纯观测性（bbox/extent/count，无语义标签）暴露 get_drawings() 数据？
   - 约束: Observation ≠ Interpretation; 无 is_figure/is_table/is_caption
   - 架构归属: AO 扩展 vs 新层 vs P6 扩展 — 需设计研究
   - 与 P2/P6/NTB 的边界: 不重复 text geometry; 不输出语义 region type

2. **Corpus 扩展评估**
   - 当前 IS-11/P7 corpus 无 figure + ordinary-text negative cases
   - 需评估: 扩大 corpus 是否能提供 negative/boundary cases
   - 但: 不得补造 GT

3. **重新审视 P6 VISUAL_REGION 删除决策**
   - 区分 "visual existence"（纯几何，可观测）与 "visual semantic identity"（语义，禁止）
   - 考虑: 是否存在纯几何的 drawing region type（如 DRAWING_DENSE_REGION）
   - 风险: 任何 "drawing" 标签都可能暗示语义 → 需谨慎设计

### 不建议

- 强行提出第三个 algorithm experiment（无证据支持）
- 恢复 VISUAL_REGION 作为语义标签（违反 Observation ≠ Interpretation）
- 复制 chunker detect_images() 的语义操作（regex caption / PNG rendering）
- 把 "可能有帮助" 写成 "已证明有效"

### 对前序审查的更新

```
M-A (caption association):
  原结论: NOT_READY (VISUAL_REGION_EVIDENCE = MISSING)
  本审查补充: VECTOR_GEOMETRY_EVIDENCE = AVAILABLE_BUT_NOT_EXPOSED
  → 缺口性质从 "完全不存在" 修正为 "底层存在但 Observation 层未暴露"
  → 如果未来授权 visual geometry observation，M-A 可能从 NOT_READY 转为 CONDITIONAL_READY
  → 但 SEMANTIC_GAP_REMAINS = TRUE

M-B (table locality):
  原结论: NOT_READY (DCE-07 CLOSED)
  本审查: Visual observation 对 M-B 有边际帮助但不解决核心问题（prose=table）
  → M-B 结论不变: NOT_READY, DO NOT REVIVE

SAFE_ALGORITHM_ROUTE = NOT_CURRENTLY_AVAILABLE (不变)
  本审查识别了设计缺口，但未打开安全实验路线。
  需先完成 Design Research，再评估是否打开。
```

---

## 最终状态

```text
PRIMARY_DIAGNOSIS            = C (OBSERVATION_SURFACE_TOO_NARROW)
SECONDARY_DIAGNOSIS          = D (REPRESENTATION_GAP)

P6_VISUAL_REGION_REMOVAL     = OVERLY_BROAD (visual existence ≠ visual identity)
VECTOR_GEOMETRY_EVIDENCE     = AVAILABLE_BUT_NOT_EXPOSED
SEMANTIC_GAP_REMAINS         = TRUE
POTENTIAL_NEW_EXPERIMENT_ROUTE = CONDITIONAL_TRUE (requires design research + authorization)
DESIGN_RESEARCH_REQUIRED     = TRUE

IMPLEMENTATION_AUTHORIZED    = FALSE
EXPERIMENT_AUTHORIZED        = FALSE
FROZEN_BASELINE              = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d)
DICE_CORE_DRIFT              = 0
PRODUCTION                   = FALSE
RUNTIME_AUTHORITY            = ZERO
STOP                         = TRUE
```

存在设计层面的候选缺口（纯几何矢量观测 surface）。
需要进一步 Design Research。
**不自行进入 implementation。**

`STOP = TRUE`。
