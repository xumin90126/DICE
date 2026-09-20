# P7 Structure Concept Matrix — Fact / Relation / Hypothesis / Semantic

> 逐项判定每个结构概念的正确归属。四类：**Fact**（Layer A 观察事实）、**Relation**（Layer B 结构关系）、**Hypothesis**（Layer C 结构假设）、**Semantic**（语义解释，P7 不得输出）。

| Concept | Example | Source Layer | Fact / Relation / Hypothesis / Semantic | Automatic? | Requires Validation? |
|---|---|---|---|---|---|
| **Heading** | `possible_heading`, `heading_candidate` | P3 Style + P5 Order + P6 Region + P2 Spacing | **Hypothesis**（`is_heading` 本身是 Semantic，禁止） | 自动产出 candidate ✅；自动判 `is_heading=true` ❌ | ✅ 必须 |
| **Section** | `possible_section`（heading 及其下属内容的范围） | P5 Reading Order + P6 Region + Heading Hypothesis | **Hypothesis**（范围界定是假设） | 自动产出 candidate ✅ | ✅ 必须 |
| **Paragraph** | `possible_paragraph`（垂直连续 span 分组） | P4 Span + P5 Order + P6 DENSE_REGION | **Relation**（几何分组；「段落语义」是 Semantic） | 自动分组 ✅ | 弱（几何分组可自动，语义化须验证） |
| **Caption** | `possible_caption` | P2 Proximity + P5 Order + P6 Region（**缺 object**） | **Hypothesis**（且证据不足） | 自动产出 candidate 谨慎 ⚠️ | ✅ 必须 |
| **Table** | `possible_table_region` | P2 对齐组 + P6 DENSE_REGION + x_projection | **Hypothesis**（`is_table` 是 Semantic） | 自动产出 candidate ✅ | ✅ 必须 |
| **Table Cell** | `cell(x,y)`、`row/column` | **无 cell 级几何/grid** | **Semantic**（且上游缺失） | ❌ | —（REQUIRES_UPSTREAM） |
| **Figure** | `possible_figure` | **无 Visual Object Observation** | **Semantic**（且上游缺失） | ❌ | —（UPSTREAM GAP） |
| **Image** | `possible_image` | **无 Visual Object Observation** | **Semantic**（且上游缺失） | ❌ | —（UPSTREAM GAP） |
| **Chart** | `possible_chart` | **无 Visual Object Observation** | **Semantic**（且上游缺失） | ❌ | —（UPSTREAM GAP） |
| **Flowchart** | `possible_flowchart` | **无 vector/shape/arrow/connectivity** | **Semantic**（且上游缺失） | ❌ | —（REQUIRES_VISUAL_GRAPHIC_LAYER） |
| **Formula** | `possible_formula` | P1 char + P3 superscript + P2 孤立几何（**缺 baseline/subscript/symbol-class**） | **Hypothesis**（弱，`is_formula` 是 Semantic） | 自动产出弱 candidate ⚠️ | ✅ 必须 |
| **List** | `possible_list`, `list_item` | P2 left-alignment + P5 垂直序列 + P3 样式 + P6 Region | **Hypothesis**（list 是结构语义，item 是假设） | 自动产出 candidate ✅ | ✅ 必须 |
| **Header** | `possible_header` | P6 PAGE_TOP_REGION + full-width + 跨页重复 pattern | **Hypothesis**（`is_header` 是 Semantic） | 自动产出 candidate ✅ | ✅ 必须 |
| **Footer** | `possible_footer` | P6 PAGE_BOTTOM_REGION + full-width + 跨页重复 | **Hypothesis** | 自动产出 candidate ✅ | ✅ 必须 |
| **Page Number** | `possible_page_number` | P6 SPARSE_REGION + margin 几何 + 数值/符号 pattern | **Hypothesis**（`is_page_number` 是 Semantic；数值 pattern 属 Textual Evidence，默认不引入） | 自动产出 candidate 谨慎 ⚠️ | ✅ 必须 |
| **Footnote** | `possible_footnote` | P6 BOTTOM/SPARSE + P3 小字号 + P5 位置 | **Hypothesis** | 自动产出 candidate ✅（弱） | ✅ 必须 |
| **Reference** | `possible_reference` | P5 Order + P6 Region + P3 样式（**文本内容不引入**） | **Hypothesis**（弱） | 自动产出 candidate 谨慎 ⚠️ | ✅ 必须 |
| **Multi-column continuation** | `possible_continuation(col_a → col_b)` | P5 ColumnGroup + ReadingOrder + P6 COLUMN_REGION | **Relation + Hypothesis**（列续接关系是确定性几何，语义接续是假设） | 自动产出 relation ✅；接续语义须验证 | 弱（relation 可自动） |

**汇总判定**：
- **纯 Fact（Layer A）**：0 个（Structure 概念没有一个是「观察事实」——都由 P1–P6 产出）。
- **Relation（Layer B）**：Paragraph（几何分组）、Multi-column continuation（几何续接）——可确定性自动构造。
- **Hypothesis（Layer C）**：Heading/Section/Caption/Table/Formula/List/Header/Footer/Page Number/Footnote/Reference——P7 的主要产出，全部带 confidence + 证据 + decision_trace。
- **Semantic（禁止/上游缺失）**：Table Cell、Figure、Image、Chart、Flowchart——P7 不得输出 `is_* = true` 的语义结论，其中后四者连候选都因上游缺失而不应产生。
