# Cross-Document Text-Unit Relation Audit

> READ-ONLY audit. 不修改 P4 / P7.1 / Frozen 730 / calibration_filter / 任何代码。
> 目标：判断「同一文本单元的形成是否可以通过可迁移的 layout/reading-order features 判断，而不是依赖单一页面阈值」。

---

## 0. 审计范围

| 文档 | 类型 | 页数 | 审计页 |
|---|---|---|---|
| arxiv_toc (arxiv_bio p2) | 学术论文目录页 | 39 | p2 (TOC) |
| RA101 | 设备手册 | 16 | p1-3 |
| RM501-P4 | 设备手册 | 2 | p1-2 |
| E804 | 设备手册 | 2 | p1-2 |
| C216 | 设备手册 | 12 | p1-3 |
| DC201 | 设备手册 | 8 | p1,2,5 |
| arxiv_2307 | 学术论文(含公式) | 7 | p1-3 |

对每页执行 P1→P2→P3→P4 全流程（只读），提取 117+116+214+84+108+201+921 = 1761 条 source observation，构造 90+36+65+31+36+56+553 = 867 条 span，统计 1761 对相邻 observation 的 gap / Δy / font / style / merge decision。

原始数据：`tmp/perception/p7/cross_doc_audit_raw.json`

---

## 1. 同一文本单元但当前未合并的案例

### 跨文档统计

| 文档 | P1 obs | P4 spans | P4 merged | same-y 未合并 |
|---|---|---|---|---|
| arxiv_toc | 117 | 90 | 27 | **47** |
| RA101 | 116 | 36 | 80 | 0 |
| RM501-P4 | 214 | 65 | 149 | 2 |
| E804 | 84 | 31 | 53 | 1 |
| C216 | 108 | 36 | 72 | 0 |
| DC201 | 201 | 56 | 145 | 0 |
| arxiv_2307 | 921 | 553 | 368 | **338** |

**关键发现**：
- **设备手册（RA101/RM501/E804/C216/DC201）几乎没有 same-y 未合并对**（0-2 条，且全部是跨栏 gap>170pt，不是漏合并）
- **未合并集中在 arxiv_toc（47 条）和 arxiv_2307（338 条）**
- arxiv_toc 的 47 条未合并 = TOC 条目被拆成「序号 + 标题 + 页码」碎片
- arxiv_2307 的 338 条未合并 = **数学公式中的符号碎片**（γ, u, r, S, (, ), −, + 等）

### Case A："1" + "Introduction"（TOC 数字+标题）

arxiv_toc p2，23 对：
- "1" → "Introduction"：gap=10.0pt, dy=0.0, same_font=✅, same_style=✅
- "2.1" → "Leptonic processes"：gap=11.1pt, dy=0.0, same_font=✅
- "2.3.1" → "Factorization"：gap=12.4pt, dy=0.0, same_font=✅
- 全部 gap 在 10.0–22.1pt 范围，dy≈0，same_font=✅，same_style=✅
- **P4 max_horizontal_gap=8.0pt 导致这些对不合并**

### Case B：罗马数字 + 小标题

**0 对。** 真实语料中未出现罗马数字小标题（设备手册用阿拉伯数字，arxiv 用 X.Y 编号）。

### Case C：表格中相邻短字段

34 对，主要在 arxiv_2307（数学公式碎片）和 arxiv_toc（页码碎片）：
- "2.2" → "K"：gap=11.1pt, dy=0.3, same_font=❌（公式片段）
- "∗" → "6"：gap=311.6pt（跨栏，页码）
- arxiv_2307: "2" → "†"：gap=28.7pt（脚注标记）

### Case D：正文相邻短行

2 对，均在 arxiv_toc：
- "2.3.1" → "Factorization"：gap=12.4pt
- "2.3.2" → "Fits to"：gap=12.4pt
- 这些实际是 TOC 子条目（序号+标题），不是正文段落

### Case E：TOC 条目

47 对，全部在 arxiv_toc p2：
- 序号 → 标题：gap=10-12pt（应合并）
- 标题 → 页码：gap=170-338pt（跨栏，不应合并）
- 页码 → 下一序号：gap=200-300pt（跨栏，不应合并）

### Case F：页眉/页脚

0 对 same-y 未合并。设备手册的页眉页脚已被 P4 正确处理。

---

## 2. 当前合并正确的案例

894 对被 P4 正确合并：
- gap 分布：overlap(776) + 0-4pt(81) + 4-8pt(37) → 绝大多数合并的 gap≤8pt 或有重叠
- Δy 分布：0-1pt(180) + 1-3pt(106) + 3-8pt(21) + 8-14pt(504) + >14pt(83)
- 8-14pt Δy 的 504 对 = 跨行合并（同列下一行），这是 P4 的核心能力

**结论**：P4 的 max_horizontal_gap=8.0pt 对 894 对正确合并是有效的。问题不在"合并了不该合并的"，而在"漏合并了该合并的"。

---

## 3. 扩大 horizontal gap threshold 的潜在误合并

### threshold=12pt

| 类型 | 对数 | 应合并? |
|---|---|---|
| TOC 数字+标题（TRUE merge） | 17 | ✅ |
| 数学符号碎片（FALSE merge） | 79 | ❌ |
| **Precision** | **17.7%** | — |

### threshold=20pt

| 类型 | 对数 | 应合并? |
|---|---|---|
| TOC 数字+标题（TRUE merge） | 19 | ✅ |
| 数学符号/跨栏/正文碎片（FALSE merge） | 157 | ❌ |
| **Precision** | **10.8%** | — |

### 误合并类型明细（gap 8-12pt）

- arxiv_2307 数学公式碎片："( " → ",",  "r" → "t", "u" → "r e", "S" → "u" 等（75 对）
  - 这些是公式中的变量/符号，gap 8-12pt 但**不应合并**（合开会破坏公式结构）
- arxiv_2307 正文→脚注标记："of their chemical potential in" → "2"（脚注引用，gap=8.1pt, same_font=❌）

**结论**：扩大 threshold 会产生大量误合并（precision 10-18%），主要受害者是数学公式。

---

## 4. Gap 分布

| Gap 范围 | same-y 未合并对数 | 占比 | 主要内容 |
|---|---|---|---|
| 8-12pt | 96 | 25% | TOC 序号+标题(17) + 数学符号(75) + 正文→脚注(4) |
| 12-20pt | 80 | 21% | TOC 子条目(6) + 数学符号(74) |
| 20-50pt | 136 | 35% | 数学符号 + 跨栏残留 |
| >50pt | 76 | 20% | 跨栏（标题→页码），不应合并 |

**关键**：8-12pt 区间同时包含 TRUE merge（TOC 序号+标题）和 FALSE merge（数学符号），**gap 值无法区分**。

---

## 5. Δy / baseline

- TRUE merge（TOC 数字+标题）：23/23 对 dy<1pt（同一基线）
- FALSE merge（数学符号）：243/277 对 dy<1pt（也同一基线！）
- **Δy 无法区分**：TOC 条目和公式符号都在同一行（dy≈0）

---

## 6. Font / font_size

- TRUE merge：23/23 same_font=✅, same_style=✅
- FALSE merge（数学符号）：243/277 same_font=✅, 229/277 same_style=✅
- **same_font 无法区分**：TOC 序号与标题用同一字体；公式符号之间也用同一字体（CMMI）

---

## 7. Reading order

- TRUE merge：序号在标题之前（source_index 相邻）
- FALSE merge（数学符号）：符号之间也 source_index 相邻
- **reading order 相邻性无法区分**

---

## 8-11. Table region / Column region / Page structure / Graphic boundary

- TRUE merge 全部发生在 TOC 页（arxiv_toc p2）
- FALSE merge（数学符号）全部发生在正文页（arxiv_2307 p1-3）
- 设备手册（RA101/RM501/E804/C216/DC201）**完全没有** same-y 未合并问题
- **页面结构（TOC 页 vs 正文页 vs 公式页）可以区分**，但这需要 page-level classification

---

## 12. Punctuation / numbering pattern

- TRUE merge：text_a = 数字编号（"1", "2.1", "2.3.1", "B.1"），text_b = 标题文本
- FALSE merge：text_a = 数学符号（"γ", "u", "r", "(", ")", "−", "+"），text_b = 数学符号
- **文本内容可以区分**，但这需要 textual analysis（P7.1 契约禁止在决策路径中使用文本证据）

---

## 13. Surrounding whitespace

- TRUE merge（TOC）：序号与标题之间 gap=10-12pt，标题与右侧页码之间 gap=170-338pt
- FALSE merge（公式）：符号之间 gap=8-12pt，周围密集排列更多符号
- **周围密度可以部分区分**（TOC 行稀疏，公式行密集），但需要 context window 分析

---

## 8 个必须回答的问题

### Q1. 单一 horizontal-gap threshold 是否具有跨文档迁移性？

**否。**

- threshold=8pt：漏合并 23 对 TRUE merge（全部在 arxiv_toc TOC 页）
- threshold=12pt：误合并 79 对 FALSE merge（主要在 arxiv_2307 公式页），precision=17.7%
- threshold=20pt：误合并 157 对，precision=10.8%

8-12pt gap 区间同时包含 TOC 序号+标题（应合并）和数学公式符号（不应合并）。**没有任何单一 gap 阈值能同时正确处理这两种场景。**

### Q2. 10pt gap 是否足以证明应该 merge？

**否。**

gap=10pt 的 same-y 对中：
- TRUE merge（TOC "1"→"Introduction"）：17 对
- FALSE merge（数学符号 "("→",", "r"→"t"）：75 对
- precision = 17/(17+75) = 18.5%

10pt gap 本身不提供合并依据。需要**额外特征**（文本内容、页面结构、周围密度）才能判断。

### Q3. width<15pt 是否具有跨文档迁移性？

**否。**

- arxiv_toc：width<15pt 的候选是页码/序号（应过滤）✅
- arxiv_2307：width<15pt 的候选是数学符号（不应简单过滤，因为它们可能是公式的一部分）❌
- 设备手册：width<15pt 的候选可能是表格短字段（如 "5V", "10ms"），不应过滤 ❌

### Q4. y±5pt 是否具有跨文档迁移性？

**否。**

- arxiv_toc：同 y 行 = 同一 TOC 条目的碎片（应合并）✅
- arxiv_2307：同 y 行 = 同一公式行的符号（不应合并）❌
- 设备手册：同 y 行 = 表格同行单元格（不应合并）❌

### Q5. 当前 calibration_filter 是否属于 page-specific patch？

**是。**

calibration_filter 的 width<15pt + y±5pt 规则只对 arxiv_toc p2 有效：
- TRUE merge（23 对应合并的 TOC 序号+标题）全部在 arxiv_toc
- 设备手册完全没有这个问题（0-2 same-y 未合并，且全部是跨栏）
- arxiv_2307 的 338 对未合并是公式碎片，用 calibration_filter 会误合并

### Q6. 问题真正属于 P4/text reconstruction，还是 P7.1 semantic observation？

**属于 P4/text reconstruction。**

- 碎片的产生在 P4 span 构造阶段（P1 产生独立 observation → P4 decide_merge 判断是否合并 → P7.1 基于 span 生成 candidate）
- P7.1 忠实地基于 P4 给它的 span 工作——如果 P4 合并了，P7.1 不会拆开；如果 P4 没合并，P7.1 不会合并
- 问题不在 P7.1 的 heading 判断逻辑，而在 P4 的 span 合并决策
- P7.1 是 semantic observation 层，不应承担 text reconstruction 职责

### Q7. 如果需要 P4 v3，应该优化"阈值"还是"文本单元关系模型"？

**应该优化"文本单元关系模型"，不是"阈值"。**

证据：
1. 没有任何单一阈值（8pt / 12pt / 20pt）能同时正确处理 TOC 页和公式页
2. 区分 TRUE merge 和 FALSE merge 需要的特征是：
   - **文本内容模式**（数字编号 vs 数学符号）—— 但这需要 textual analysis
   - **页面结构**（TOC 页 vs 公式页 vs 表格页）—— 但这需要 page-level classification
   - **周围密度**（TOC 行稀疏 vs 公式行密集）—— 这是最可能的可迁移几何特征
3. P4 v3 不应调阈值，而应引入**上下文感知的文本单元关系模型**：
   - 不只看 A-B 对的 gap/dy/font
   - 还看 A-B 对在同一行的**周围 observation 密度**（行内有多少个 observation）
   - 还看 A-B 对的**行角色**（是否在行首/行尾，是否有右侧远距离 observation = 页码模式）

### Q8. 如果无法证明存在可迁移规则，必须明确报告

**无法证明存在基于单一几何阈值的可迁移规则。**

但存在**基于多特征组合的可迁移信号**（尚需验证）：
1. **行内 observation 密度**：TOC 行通常 2-3 个 observation（序号+标题+页码），公式行通常 5-15 个 observation
2. **右侧远距离 observation 存在性**：TOC 行的标题右侧 170-338pt 处有页码 observation，公式行没有
3. **w_b > 30pt**：TOC 标题宽度 >30pt，公式符号宽度 <15pt（但这是 content-dependent，不是纯几何）

这些信号需要进一步验证才能确认迁移性，**本轮不实施**。

---

## ROOT CAUSE

碎片问题的根因在 **P4 `span_rules.decide_merge` 的 `max_horizontal_gap=8.0pt`**：

- arxiv_toc p2 的 TOC 条目「序号 + 标题」之间的 gap = 10-12pt > 8.0pt → P4 不合并 → P7.1 收到独立 span → 产生碎片 heading candidate
- 但这个 8.0pt 阈值对设备手册（RA101/RM501/E804/C216/DC201）完全有效（0 same-y 未合并）
- 对 arxiv_2307 公式页也有效（公式符号不应合并，8pt 阈值正确阻止了合并）

**根因不是"8pt 太小"，而是"P4 用单一 gap 阈值处理所有页面结构，缺乏上下文感知"。**

---

## TRANSFERABILITY ASSESSMENT

| 规则 | 迁移性 | 证据 |
|---|---|---|
| max_horizontal_gap=8pt | 对设备手册✅ 对 TOC 页❌ 对公式页✅ | 阈值本身不可迁移，但当前 8pt 对 5/7 文档有效 |
| width<15pt 过滤 | ❌ 只对 arxiv_toc 有效 | arxiv_2307 公式符号和设备手册表格字段会被误杀 |
| y±5pt 合并 | ❌ 只对 arxiv_toc 有效 | arxiv_2307 公式行和设备手册表格行会误合并 |
| gap threshold 调大 | ❌ precision 10-18% | 79-157 对误合并（主要数学公式） |
| 行内 observation 密度 | ⚠️ 待验证 | TOC 行 2-3 obs vs 公式行 5-15 obs，信号存在但未验证 |
| 右侧远距离 observation | ⚠️ 待验证 | TOC 行有页码(gap>170pt)，公式行没有 |

**结论：不存在已验证的可迁移单一规则。calibration_filter 是 page-specific patch，不具备跨文档迁移性。**

---

## RECOMMENDED NEXT LAYER

### 建议：进入 P4 v3 Design（不实施，仅设计）

**P4 v3 应优化"文本单元关系模型"，不是"阈值"。**

P4 v3 的 decide_merge 应从「单对 A-B 的 gap/dy/font」升级为「上下文感知的文本单元关系」：

1. **行级上下文**：不只看 A-B 对，还看同一 y 行的所有 observation 数量和分布
2. **行角色判断**：A 是否在行首？B 右侧是否有远距离 observation（页码模式）？
3. **行密度信号**：行内 observation 数量（TOC 行 2-3 个 vs 公式行 5-15 个）
4. **保持纯几何**：不引入文本内容分析（P7.1 契约边界），只用 layout/geometry/reading-order features

**关键约束**：
- P4 v3 是 unfrozen 新版本，不修改 frozen P4
- P4 v3 的输出仍遵循现有 span schema（不破坏 P5-P7.1）
- P4 v3 需要在全部 7 个文档上验证迁移性后才能正式采用
- 如果行密度/行角色信号也无法迁移，则必须承认 P4 无法自动解决 TOC 碎片问题，该问题交由 Human Validation 处理

### 不建议的方向

- ❌ 调大 max_horizontal_gap 阈值（precision 10-18%，误合并数学公式）
- ❌ 继续使用 calibration_filter 作为正式修复（page-specific，不可迁移）
- ❌ 在 P7.1 引入文本内容分析（违反 Observation contract 边界）
- ❌ 为提高 precision 而增加 heuristic（违反"不允许为得到更高 precision 而增加 heuristic"原则）

---

## 是否建议进入 P4 v3 Design

**建议进入 P4 v3 Design（仅设计，不实施）。**

理由：
1. 根因已定位（P4 单一阈值缺乏上下文感知）
2. 存在待验证的可迁移信号（行密度 / 行角色 / 右侧远距离 observation）
3. P4 v3 不修改 frozen P4，是独立新版本
4. 但必须先验证信号迁移性，如果无法迁移则 STOP 并承认 Human Validation 是唯一可行路径

**STOP。本轮 READ-ONLY 审计完成。不修改任何代码。不进入 P7.3。等待下一步批准。**
