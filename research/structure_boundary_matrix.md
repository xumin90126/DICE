# P7 Structure Boundary Matrix

> 依据 P1–P6 实际可用证据逐对象判定。原则：证据不足写 `NOT_SUPPORTED_BY_CURRENT_OBSERVATIONS` 或 `REQUIRES_UPSTREAM_EXTENSION`，不因「未来想识别」就默认 P7 必须实现。

| Structure | Available Upstream Evidence | Automatic Candidate Allowed | Automatic Final Classification Allowed | Human Validation Required | Out-of-Scope / Upstream Gap |
|---|---|---|---|---|---|
| **Heading** | P3 样式对比(bold/italic/size) + P5 阅读位置(region 首/段首) + P6 Region 关系 + P2 间距模式 | ✅ 多信号→`possible_heading` | ❌ | ✅ 是 | 单信号(bold)不得产出 |
| **Section** | Heading hypothesis + P5 Reading Order(前后边界) + P6 Region | ✅ 基于 heading 的范围候选 | ❌ | ✅ 是 | 无 heading 证据时不得推断 |
| **Paragraph** | P4 Span 垂直连续 + P5 顺序 + P6 DENSE_REGION | ✅ 几何分组(relation) | ❌（语义段落） | 弱（几何分组自动） | 语义化须验证 |
| **Caption** | P2 邻近/相对位置 + P5 顺序 + P6 Region | ⚠️ 谨慎（缺 object 关系） | ❌ | ✅ 是 | **REQUIRES_UPSTREAM_EXTENSION**（可靠 object） |
| **Table** | P2 2D 对齐组 + P6 DENSE_REGION + x_projection 密度 | ✅ `possible_table_region` | ❌ | ✅ 是 | cell 重建 = REQUIRES_UPSTREAM |
| **Table Cell** | **无 cell 级几何/grid/行列** | ❌ | ❌ | — | **NOT_SUPPORTED_BY_CURRENT_OBSERVATIONS** |
| **Figure** | **无 Visual Object Observation** | ❌ | ❌ | — | **NOT_SUPPORTED / UPSTREAM_OBSERVATION_GAP** |
| **Image** | **无 Visual Object Observation** | ❌ | ❌ | — | **UPSTREAM_OBSERVATION_GAP** |
| **Chart** | **无 Visual Object Observation** | ❌ | ❌ | — | **UPSTREAM_OBSERVATION_GAP** |
| **Flowchart** | **无 vector/shape/arrow/connectivity** | ❌ | ❌ | — | **REQUIRES_VISUAL_GRAPHIC_OBSERVATION_LAYER** |
| **Formula** | P1 char + P3 superscript(bit0) + P2 孤立几何；**缺 baseline/subscript/symbol-class** | ⚠️ 弱 `possible_formula`（多信号） | ❌ | ✅ 是 | baseline/subscript/symbol-class = REQUIRES_UPSTREAM |
| **List** | P2 left-alignment + P5 垂直序列 + P3 样式一致 + P6 Region | ✅ `possible_list` | ❌ | ✅ 是 | 无对齐证据不得推断 |
| **Header** | P6 PAGE_TOP_REGION + full-width + 跨页重复 pattern | ✅ `possible_header` | ❌ | ✅ 是 | 跨页重复是 pattern 证据，非对象合并 |
| **Footer** | P6 PAGE_BOTTOM_REGION + full-width + 跨页重复 | ✅ `possible_footer` | ❌ | ✅ 是 | 同上 |
| **Page Number** | P6 SPARSE_REGION + margin 几何；数值/符号 pattern(Textual Evidence 默认不引入) | ⚠️ 谨慎（弱） | ❌ | ✅ 是 | Textual pattern = 默认不引入 |
| **Footnote** | P6 BOTTOM/SPARSE + P3 小字号 + P5 位置 | ✅ 弱 `possible_footnote` | ❌ | ✅ 是 | 弱信号 |
| **Reference** | P5 Order + P6 Region + P3 样式；文本内容不引入 | ⚠️ 谨慎（弱） | ❌ | ✅ 是 | 引用语义需文本内容 = 默认不引入 |

**统计**：
- **自动候选 ✅**：Heading / Section / Paragraph(分组) / Table(region) / List / Header / Footer / Footnote — 8 项（P7.1 候选）。
- **谨慎 ⚠️**：Caption / Formula / Page Number / Reference — 4 项（弱信号，P7.3 或 upstream）。
- **不可 ⚠️❌**：Table Cell / Figure / Image / Chart / Flowchart — 5 项（REQUIRES_UPSTREAM_EXTENSION / NOT_SUPPORTED）。
- **自动最终分类 ❌**：全部 17 项都不允许（P7 永不下 `is_* = true` 结论）。
