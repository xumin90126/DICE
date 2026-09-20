# P7 Scope Decision

> 依据 P1–P6 实际可用证据，明确划分 P7 的四个范围。P7.1 才可在获批后实现。

---

## P7.1 — CAN IMPLEMENT NOW（当前事实已足够 → 自动产出候选）

前提：只产出 **StructureHypothesis / StructureRelation**，永不下 `is_* = true` 语义结论。

| 对象 | 可用证据 | 产出形态 |
|---|---|---|
| **Heading candidate** | P3 样式对比 + P5 位置 + P6 Region + P2 间距 | `possible_heading`（≥2 独立信号） |
| **Paragraph grouping** | P4 Span 连续 + P5 顺序 + P6 DENSE_REGION | `paragraph_group`（几何关系） |
| **Section candidate** | heading candidate + P5 顺序边界 | `possible_section`（范围候选） |
| **List candidate** | P2 左对齐 + P5 垂直序列 + P3 样式一致 | `possible_list` |
| **Header candidate** | P6 PAGE_TOP_REGION + full-width + 跨页重复 pattern | `possible_header` |
| **Footer candidate** | P6 PAGE_BOTTOM_REGION + full-width + 跨页重复 | `possible_footer` |
| **Multi-column continuation** | P5 ColumnGroup + ReadingOrder + P6 COLUMN_REGION | `continuation_relation`（几何续接） |

**实现约束**：确定性、无关键词/LLM/embedding、无语义分类、无 document-specific patch、遵守不确定性传播契约、不改 P1–P6。

---

## P7.2 — REQUIRES UPSTREAM EXTENSION（必须先扩展 P1–P6）

| 对象 | 缺失的上游观察 | 所需扩展 |
|---|---|---|
| **Figure / Image / Chart** | Visual Object Observation | P1 需增加 image/vector bbox 提取（跳过非文本块之前先记录其 bbox） |
| **Flowchart** | Graphic/Vector Observation | 需 shape/arrow/text-node/connectivity 观察层 |
| **Table Cell** | Table Cell Geometry | 需 cell 级几何、行列 grid 观察 |
| **Formula（可靠级）** | baseline/subscript/symbol-class | 需 character-level baseline、下标位、符号类别观察 |
| **Caption（可靠级）** | 可靠 object reference | 依赖 Visual/Table Object Observation 先落地 |

**规则**：在扩展上游之前，P7 **不得**实现这些对象的自动候选（Caption/Formula 的弱候选见 P7.3）。

---

## P7.3 — HUMAN-FIRST / VALIDATION-FIRST（自动系统仅提案，优先进 Human Validation）

| 对象 | 弱信号来源 | 处置 |
|---|---|---|
| **Caption candidate** | 邻近 + 相对位置 + 样式（缺 object） | 弱提案，置信 UNKNOWN/LOW，直接进 Human Validation |
| **Formula candidate** | superscript + 孤立几何 + 符号密度近似 | 弱提案，置信 LOW，进 Human Validation |
| **Page Number candidate** | margin 几何 + SPARSE_REGION（数值 pattern 默认不引入） | 弱提案，置信 LOW，进 Human Validation |
| **Reference candidate** | 顺序 + 区域 + 样式（文本内容不引入） | 弱提案，置信 LOW，进 Human Validation |
| **Footnote candidate** | 底部 + 小字号 + 位置 | 弱提案，置信 LOW，进 Human Validation |

**规则**：这些对象只产生 hypothesis，且 `confidence ∈ {LOW, UNKNOWN}`，**必须**流入 Human Validation，绝不自动进入 Evidence。

---

## OUT OF SCOPE（明确排除，P7 不做）

| 项 | 原因 |
|---|---|
| OCR | 属上游 P1，非结构识别 |
| LLM / Embedding 语义理解 | 违反确定性/可复现原则 |
| Flowchart graph extraction | 无 graphic 观察层 |
| Table cell reconstruction | 无 cell 几何 |
| 语义角色最终分类（`is_heading=true` 等） | 属 Validation/治理，非 P7 |
| Evidence 生成 | P7 只到 hypothesis，Evidence 是治理侧 |
| 完整 Document Object Model（Docling 式） | 属序列化/治理层，非 P7 目标 |
| 跨页结构自动合并 | 默认禁止（Header/Footer 仅 pattern，非对象合并） |
| 任何 document-specific / RM501 / DC201 / arxiv 特例 | 违反确定性原则 |

---

## 批准建议

**建议：仅批准 P7.1 进入 Implementation。**

P7.1 在纯几何+样式事实之上确定性可行、无需改上游、无需语义规则、无 document-specific patch，且不与 Evidence 混淆。P7.2 必须先做上游扩展评审；P7.3 需先定义 Human Validation 基础设施（human gate 展示字段）；Out of Scope 永不进入 P7。
