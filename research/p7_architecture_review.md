# P7 开发前 Structure Boundary Review — 完整架构审查

**性质**：READ-ONLY。本阶段不实现 P7、不修改 P1–P6、不修改 Frozen Baseline、不创建 Capability。
**目标**：在任何 P7 代码之前，严格定义 P7 的职责、输入边界、概念分层、输出对象、证据门槛、不确定性传播、Human Validation 边界与 Scope。

---

## 0. 已核实的上游事实基线（P1–P6 实际提供什么）

| 层 | 实际可用的 Observation Fact（非假设） |
|---|---|
| P1 Atomic | text, bbox, source_type(character/word/span/line/block), source_index, reading_order_hint, font_name, font_size, font_flags, line_index, block_index。**无 image/vector/drawing 观察**（`atomic_text.py` 明确 `if block_type != 0: skip non-text blocks`） |
| P2 Geometry | bbox/width/height/center/normalized_x/y, same_y_band_members, same_x_band_members, **left/right/top/bottom/center_alignment_group**, spatial_cluster_members, x_projection_overlap_count；PairwiseRelation 8 向 + distance/overlap/IoU/alignment(bool) |
| P3 Style | font_family, normalized_font_size, **bold(bit4)/italic(bit1)/superscript(bit0)** 为权威布尔；**underline=null、subscript=null**（PyMuPDF 1.26.5 不编码）；style_signature；StyleComparison 含 font_size_delta |
| P4 Span | ExperimentalSpan v2：span_id/text/source_observation_ids/bbox/width/height/center/dominant_style_signature/merge_decision_trace/provenance |
| P5 Reading Order | ReadingOrderObservation(reading_order_index, previous/next_span_id, column_group_id, page_region, order_reason, confidence), ColumnGroup, PageColumnLayout, ReadingOrderDecisionTrace |
| P6 Region | RegionObservation(region_type, source_span_ids, region_geometry, region_features, decision_trace, confidence, parent_region_id)，7 种几何类型，2 层层级 |

**关键结论**：当前上游事实是「纯文本 + 纯几何 + 纯样式」，**不存在**视觉对象、矢量图形、表格单元格、基线/下标、符号类别 五类观察。

---

## 1. P7 输入边界

### Q1：P7 直接读哪些层？
P7 **不散读**各层，而是通过一个统一只读输入接口 `PerceptionPageContext` 聚合访问：
- 主消费：P6 RegionObservation + P5 ReadingOrderObservation + P4 ExperimentalSpan（三者已向上引用 P3 Style / P2 Geometry / P1 Atomic 的 observation_id）。
- 按需引用：P3 StyleObservation、P2 GeometryObservation（通过 P4 span 的 `source_observation_ids` 回溯）。
- **唯一例外（须写入 Contract）**：P7 评估 Formula 假设时，可声明读取 P1 `character` 层（superscript 位 + 字符 bbox），仅作 formula 假设证据，不改写 P1。

### Q2：是否允许跳层？
**不允许。** 默认原则「不绕过已建立的层」成立。`Atomic → P7` 直接跳层被禁止。唯一例外（见上）是「读 char 层做 formula 证据」，且必须显式声明、不改写、写入 decision_trace——这不是跳层，而是「通过 span→observation 引用链的合法回溯」。

---

## 2. 四层概念（Layer A/B/C/D）

| 层 | 定义 | 归属 | 谁产出 |
|---|---|---|---|
| **A — Observation Fact** | 回答「我观察到了什么」。bbox/font_size/bold/distance/alignment/density/column/reading_index/region_id/confidence | 客观事实 | **P1–P6 产出，P7 只消费** |
| **B — Structural Relation** | 回答「对象之间存在什么结构关系」。belongs_to/contains/precedes/follows/adjacent_to/aligned_with/overlaps/shares_region | 几何/拓扑关系（≠语义） | **P7 可确定性构造** |
| **C — Structure Hypothesis** | 回答「可能是什么」。possible_heading/possible_caption/possible_table_region/possible_formula/possible_list | 假设/候选（≠事实） | **P7 的主要产出** |
| **D — Validated Structure** | validated_heading/validated_table/… | 治理产物 | **不属于 P7**，须经 Human Validation |

**核心判定**：`Layer B ≠ Layer C`（`A before B` 不能推出 `A is heading`）；`Layer C ≠ Layer D`（hypothesis 永不自动升级为 validated）。

---

## 3. Structure Fact 是否存在？

**判定：P7 不存在独立的「Structure Fact」。**

「Structure Fact」这类概念（heading_candidate/caption_candidate/table_candidate/…）**不属于** Layer A（Observation Fact）——它们不是「观察到的」，而是「推断出的」。它们的正确归属是：
- `heading_candidate` 等 = **Layer C（Structure Hypothesis）**，是 P7 从 Layer A 事实 + Layer B 关系合成的**假设**，携带 confidence、支持证据、冲突证据、decision_trace。
- 「validated_heading」= **Layer D**，治理产物，不在 P7。

因此：P7 的产物只有两类——**Layer B（结构关系，确定性）** 与 **Layer C（结构假设，带证据与置信）**。绝不产出 Layer A（那属于 P1–P6），也不产出 Layer D（那属于治理）。

---

## 4. P7 最小输出对象（Option 比较）

| Option | 对象 | 是否符合 DICE | 判定 |
|---|---|---|---|
| A | StructureObservation | ❌ 命名暗示「观察事实」，与 P1–P6 的 Observation 概念冲突，会把假设伪装成事实 | 拒绝 |
| B | StructureCandidate | ✅ 语义准确（候选） | 可用 |
| C | StructureHypothesis | ✅ 语义最准确（假设） | **采用为主对象** |
| D | StructureRelation + StructureHypothesis + ValidationCandidate | ✅ 分层完整 | **采用**（主对象 Hypothesis，Relation 作为其支持证据，ValidationCandidate 是治理侧产物不属 P7） |

**最终判定**：P7 最小输出 = **`StructureHypothesis`**（主对象，Layer C），其内嵌 `supporting_relations`（Layer B 关系证据）+ `supporting_facts`（Layer A 事实引用）+ `decision_trace`。**不建完整 DOM**（Docling 式 DOM 是治理/序列化层，属 P7 之后，非 P7 目标）。

---

## 5. Evidence Threshold 原则（不做 magic number）

对每个 Structure Hypothesis，最低要求 **N 类互相独立的 Observable Evidence**（N ≥ 2 默认，具体值在 P7 实现时定，但原则固定）：

禁止：`single_signal → final_structure`。
倾向：`multiple independent signals → hypothesis`。

六类证据的可用性与归属：
1. **Geometry Evidence**（P2：对齐/间距/距离/IoU/密度）— 可用。
2. **Style Evidence**（P3：bold/italic/size/签名对比）— 可用。
3. **Reading Order Evidence**（P5：index/prev-next/列关系/order_reason）— 可用。
4. **Region Evidence**（P6：region_type/parent/confidence/features）— 可用。
5. **Textual / Symbol Evidence**（文本内容、符号类别、数字模式）— **P7 默认不引入**；仅当未来增加「符号类别观察」上游时才允许。关键词分类被禁止。
6. **Visual Object Evidence**（图像/矢量对象）— **当前不存在**（UPSTREAM GAP）。

---

## 6. 不确定性传播（详见 uncertainty_propagation_contract.md）

核心原则：**Downstream cannot silently erase upstream uncertainty.**

- `StructureHypothesis.confidence = min(所有引用上游证据的 confidence)` 为基线。
- 新增独立证据**可以**提高置信，但必须：可解释、写入 decision_trace、说明「哪条新证据为何提高」。
- 上游 `LOW/AMBIGUOUS/UNKNOWN` 必须原样传导进 hypothesis 的 confidence 与 provenance。

---

## 7. Human Validation 边界

### Q1：Structure Validation 在 Evidence Validation 之前，还是其中一部分？
**之前（pre-evidence gate）。** Structure Validation 回答「这个结构假设是否成立」；Evidence Validation 回答「这个事实是否可作为证据」。两者是不同治理阶段，P7 输出只到 Structure Hypothesis，不进入 Evidence。

### Q2：Validated Heading 是否自动等于 Evidence？
**默认 NO。** Validated Structure（Layer D）是「结构已验证」，但它要成为 Evidence 仍需经过独立的 Evidence 治理流程（归属、权重、版本、引用链）。P7 链条的末端只是「Evidence Candidate」，不是 Evidence。

### Q3：Human Validation 的最小单位？
**Structure Hypothesis**（不是 region / span / relation）。一个 hypothesis 携带其 source span/region/bbox/支持与冲突证据/decision_trace，作为可审阅的原子单位。

### Q4：是否允许 PARTIALLY_VALIDATED？
**允许，字段级。** 例如 `{role: heading = VALIDATED, heading_level = UNVALIDATED}`。状态机在 P7 之后的 Validation 层定义，P7 只产出 hypothesis 字段 + 每字段的独立证据，供逐字段验证。

---

## 8. Table / Figure / Formula / Flowchart 专项

| 对象 | 当前上游事实 | 判定 |
|---|---|---|
| **Table** | P2 有 2D 对齐组 + x_projection，但**无 cell 级几何、无 grid、无行列结构** | 只能 `possible_table_region`（hypothesis，多信号：多 span 行列对齐 + 密度 + 区域关系）。**不得重建 cell** |
| **Figure / Image** | **无 Visual Object Observation**（P1 跳过非文本块） | **UPSTREAM_OBSERVATION_GAP**。禁止从 whitespace/text-absence 猜 Image |
| **Chart** | 同上 | **UPSTREAM_OBSERVATION_GAP** |
| **Formula** | char 层 + superscript(bit0) 存在，但 subscript/underline=null、无 baseline 关系、无 symbol-density 度量 | 只能弱 `possible_formula`（多信号：superscript + 孤立几何 + 符号密度近似 + 阅读位置）。缺口：baseline/subscript/symbol-class |
| **Flowchart** | 无 vector/shape/arrow/text-node/connectivity 观察 | **NOT_SUPPORTED / REQUIRES_VISUAL_GRAPHIC_OBSERVATION_LAYER** |

---

## 9. Heading / Caption / Paragraph 专项（详见 text_structure_contract.md）

- **Heading**：`heading_candidate` 可行（P7.1）。证据 = style contrast + reading position + region relationship + spacing（≥2 独立信号）。单信号（如仅 bold）→ 只记录事实，不产生 hypothesis。
- **Caption**：caption 必须有 object relationship；当前**无可靠 object** → **暂缓**。判定为 P7.3（弱 signal 仅 proposal）或 `REQUIRES_UPSTREAM_EXTENSION`。
- **Paragraph**：判定为 **几何分组（Layer B relation）**，非独立语义单元。P6 `DENSE_REGION` 内的垂直连续 span 可组织为 `possible_paragraph`（分组，不带「段落语义」）。

---

## 10. P7 与 CandidateSpan v2 的关系

`ExperimentalSpan ≠ Structure`。P7 不得 `Span → 直接 Heading`。必须 `Span + Geometry + Style + Reading Order + Region → Hypothesis`。

Structure Hypothesis 允许的粒度：
- 单个 Span：✅（如孤立的 `possible_heading`）
- 多个 Span：✅（如一个 `possible_paragraph` 分组）
- 单个 Region：✅（如 `possible_table_region` 引用一个 DENSE_REGION）
- 多个 Region：✅（谨慎，须同页 + 明确关系）
- 跨 Column：✅ 谨慎（如 multi-column continuation，须列关系 + 阅读顺序证据）
- 跨 Page：**默认禁止自动合并**（Header/Footer 的「跨页重复」是 pattern 证据，不是「合并为一个对象」）。

---

## 11. 与 Document→Evidence 链路的衔接

```
Observed Document Facts (P1–P6)
        ↓ (P7 只读消费)
Structural Relations (Layer B)
        ↓
Structure Hypotheses (Layer C, P7 产出)
        ↓ (pre-evidence gate)
Human Validation  →  Validated Structure (Layer D)
        ↓ (独立 Evidence 治理)
Evidence Candidate → Evidence → Validation → Capability → Runtime
```

**兼容性审查**：该链条**不冲突**现有 `Document → Evidence → Validation → Capability → Runtime`。因为 P7 的 Hypothesis 是「Evidence 的候选来源之一」，不是 Evidence 本身；`Runtime Authority = ZERO` 全程保持。四层边界 `Observation ≠ Hypothesis ≠ Validated Structure ≠ Evidence` 由 Contract 强制，不破坏。

---

## 12. 最终问题 A–K 回答

- **A（P7 一句话职责）**：P7 = 在 P1–P6 已观察事实之上，确定性构造「结构关系 + 结构假设」，输出可验证、可追溯、可治理的 StructureHypothesis；不做语义最终分类，不当 Evidence。
- **B（最小输出对象）**：StructureHypothesis（Layer C 候选），内嵌 supporting_relations（Layer B）与 supporting_facts（Layer A 引用）与 decision_trace。非 Fact、非 Validated Structure。
- **C（Heading/Caption/Paragraph 可否进 P7）**：Heading → 可（candidate，P7.1）；Caption → 暂缓（缺 object，P7.3/upstream）；Paragraph → 可（几何分组关系，非语义单元，P7.1）。
- **D（Table 可否进 P7，到什么粒度）**：可到 `possible_table_region`（hypothesis），**不到** cell 重建（REQUIRES_UPSTREAM_EXTENSION）。
- **E（Image/Figure 可否进 P7）**：**否**。无 Visual Object Observation，UPSTREAM_OBSERVATION_GAP。
- **F（Formula 可否进 P7）**：仅弱 `possible_formula`，且须明确缺口（baseline/subscript/symbol-class 观察缺失）。
- **G（Flowchart 可否进 P7）**：**否**。REQUIRES_VISUAL_GRAPHIC_OBSERVATION_LAYER。
- **H（哪些对象须先扩展 P1–P6）**：Visual Object Observation、Graphic/Vector Observation、Formula atomic（baseline/subscript/symbol-class）、Table Cell Geometry。
- **I（P7 自动输出可否直接成 Evidence）**：**否**。必须经 Human Validation + Evidence 治理。
- **J（Human Validation 位置）**：Structure Hypothesis 之后、Validated Structure 之前（pre-evidence gate）。
- **K（是否破坏四层边界）**：**否**。Contract 强制 `Observation ≠ Hypothesis ≠ Validated Structure ≠ Evidence`。

---

## 13. 是否建议批准进入 P7 Implementation？

**建议：有条件批准，仅限 P7.1 范围（详见 p7_scope_decision.md）。**

P7 在 P7.1（Heading/Paragraph/List/Section/Header/Footer/Page-Number/Multi-column-continuation 的**候选**输出）内可以纯几何+样式确定性工作，无需语义规则、无需改上游、无需 document-specific patch。P7.2/P7.3 与 Out-of-Scope 对象**不得**在未扩展上游前实现。

**STOP 条件未触发**：P7.1 不引入语义规则、不依赖缺失事实、不与 Evidence 混淆、Human Validation 边界已定义、不需改 P1–P6。
