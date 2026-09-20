# P7 Text Structure Contract — Heading / Caption / Paragraph

> 这三类最容易「提前语义化」。本契约逐一界定其候选定义、最低证据、禁止的捷径。

---

## 1. Heading

### 定义
`heading_candidate` = 一个「在样式、阅读位置、区域关系、间距模式上表现出『章节标题样』文本块」的**假设**，绝不等于 `is_heading = true`。

### 最低独立信号（≥2 类，缺一不可自动判）
1. **Style Evidence**：与相邻 body 文本存在样式对比（font_size_delta、bold、italic、style_signature 差异）。
2. **Reading Position Evidence**：位于 region 首 / 列首 / 前一段之后的大垂直间隙之后。
3. **Region Evidence**：属于 COLUMN/DENSE 区域的顶部（而非 FULL_WIDTH 中间），或自身为独立的 SPARSE/短行。
4. **Spacing Evidence**：与上一段存在大于密集阈值的垂直间隙，或与下一段存在明显间距。

### 禁止的捷径
```
bold → heading ❌
font_size=18 → heading ❌
top_of_page → heading ❌
短行 → heading ❌
```
任一单信号只能作为**事实**记录，不得单独产生 heading hypothesis。

### 输出字段
`{role_candidate: heading, heading_level_candidate: null, supporting_facts: [...], conflicting_evidence: [...], confidence, decision_trace}` — `heading_level` 仅在后续验证层判定，P7 不产出。

---

## 2. Caption

### 定义
`caption_candidate` = 一个「与某个对象区域存在空间邻近 + 相对位置 + 样式关系的文本块」的**假设**。

### 核心问题：object relationship 缺失
Caption 必须绑定「它描述的对象」。当前 P1–P6 **无可靠的 Visual/Table 对象观察**（Figure/Image/Chart/Table-cell 均缺失）。因此：

- **判定**：Caption 在 P7 中**暂缓**（`REQUIRES_UPSTREAM_EXTENSION`），仅保留弱 `possible_caption`（P7.3）作为 Human-First 提案。
- **弱信号**：文本块位于某个非文本空隙/区域的正下方或正上方 + 样式延续/差异 + 邻近关系。但 `caption ≠ small text`。
- **禁止**：`small text below gap → caption ❌`；`proximity alone → caption ❌`。

### 结论
在扩展 Visual/Table Object Observation 之前，P7 不自动产出 caption hypothesis（只可进入 Human-First 弱提案，置信 UNKNOWN/LOW）。

---

## 3. Paragraph

### 重新判定
Paragraph 在 DICE 分层中的正确定位是 **Layer B（几何分组关系）**，不是独立语义单元。

### 判定依据（P1–P6 现状）
- P4 Span 已做「同线/邻行」几何合并。
- P5 Reading Order 给出 span 顺序。
- P6 DENSE_REGION 已经是「垂直连续 span 簇」的几何区域。

因此，Paragraph 的「几何分组」**已经实质上由 P4+P6 承载**。P7 若产出 `possible_paragraph`，只是「把 DENSE_REGION 内的连续 span 显式组织为关系对象」，不新增语义。

### 结论
- Paragraph = **几何分组关系**（belongs_to / contiguous），可自动构造（P7.1）。
- 不带「段落语义」（主题、段落边界语义）——那些属于更上层或 Human Validation。
- 禁止：`paragraph = 传统 parser 的语义对象` ❌；`DENSE_REGION 自动 = 一个 paragraph` ❌（一个 DENSE_REGION 可能含多段）。

---

## 4. 三类共同约束

1. 均产出 **Hypothesis / Relation**，绝不产出 `is_* = true` 语义结论。
2. 均须携带 `supporting_facts`（Layer A 事实引用）+ `decision_trace`。
3. 均遵守不确定性传播契约（上游 LOW/AMBIGUOUS 不得静默抹除）。
4. 均禁止关键词/LLM/embedding/document-specific patch。
