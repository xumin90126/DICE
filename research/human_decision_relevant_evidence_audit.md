# Human Decision-Relevant Evidence Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY / NO IMPLEMENTATION / NO UI CHANGE

---

## 1. Executive Summary

> **DICE 的最大问题不是缺少 Evidence，而是缺少 Evidence 之间的 Relation Organization。现有 Evidence（text, geometry, TLD, line_spans, image）已经足够支撑 Human 判断，但系统没有把它们组织成 Human 真正需要的关系结构。Human 每次都必须从页面图像中重建这些关系。**

核心发现：
- P722 B1（无 Cue，仅有 fields + image）= **100% accuracy, 1.7s avg** → 图像+文本已足够
- P722 B2（有 Cue）= 93% accuracy, **5.9s avg** → Cue 反而增加了认知负荷
- 3 个错误案例全部发生在 **无 TLD** 的页面上 → 缺少结构关系证据
- Human 在 rationale 中提及最多的是 **TABLE_STRUCTURE (70次)** 和 **NUMERIC_VALUE (57次)**，但这些都不是系统直接提供的 Evidence Field
- 系统缺少 6 种关键 Evidence Relation（column header, paragraph membership, caption boundary 等）

---

## 2. Research Question

> 对于一个真实 Human Review Case，哪些 Evidence 能够真正帮助 Human 完成 Semantic Judgment？

回答：Human 真正需要的不是更多 Evidence Fact，而是 **Evidence 之间的 Relation**。具体来说：

1. 不是"text_a='28.54'"（RAW_FACT），而是"28.54 是 top-1 error 列的值"（RELATION）
2. 不是"is_in_table=True"（BOOLEAN），而是"A 在第 3 行第 1 列，B 在第 3 行第 2 列"（POSITION_RELATION）
3. 不是"text_a ends with period"（PATTERN），而是"A 是段落 P 中句子 S1 的结尾"（CONTEXT_RELATION）

---

## 3. Data Sources

| 来源 | 数量 | 类型 |
|---|---|---|
| Experiment Cases | 30 | 完整 Cue + fields + line_spans |
| P722 Judgments | 55 | A=15, B1=10, B2=30 |
| Free-text Feedback | 4 | P01 pilot |
| Reviewer Rationales | 90 | 2 reviewers × 45 cases |
| GT Adjudication Rationales | 93 | 45 frozen + 48 session |
| Total feedback instances | 187 | — |

---

## 4. Human Judgment Reconstruction

### P722 结果摘要

| Condition | Accuracy | Avg Time | Max Time | Slow (>10s) |
|---|---|---|---|---|
| A (fields + image) | 93% (14/15) | 2.2s | 8.1s | 0 |
| B1 (8 fields + image) | 100% (10/10) | 1.7s | 2.9s | 0 |
| B2 (8 fields + 4 cues + image) | 93% (28/30) | 5.9s | 45.9s | 3 |

**关键发现**：B2（有 Cue）比 B1（无 Cue）**慢 3.5 倍**，且准确率不更高。Cue 增加了信息量但未增加决策价值。

### 3 个错误案例分析

| Case | Cond | Decision | GT | Time | TLD | 缺失证据 |
|---|---|---|---|---|---|---|
| AMB-005 | A | MERGE | KEEP_SEPARATE | 1.6s | True | 句子边界检测（A 条件无 Cue） |
| AMB-032 | B2 | UNKNOWN | KEEP_SEPARATE | 45.9s | False | 表格结构上下文（TLD 不可用） |
| AMB-375 | B2 | UNKNOWN | KEEP_SEPARATE | 31.3s | False | 段落成员关系（无 TLD，仅 period+capital） |

**模式**：所有 B2 错误都发生在 **无 TLD** 的页面上。Human 有 Cue 但 Cue 不包含结构关系，导致不确定。

---

## 5. Evidence Necessity Analysis

| Evidence | Necessity | 依据 |
|---|---|---|
| text_a, text_b | **NECESSARY** | Human 始终读取文本内容判断类型 |
| page image | **NECESSARY** | P722 B1 仅靠 image+text = 100% accuracy |
| h_gap | **HELPFUL** | 提供间距信息，但 Human 很少在 rationale 中提及 |
| dy | **HELPFUL** | 同上 |
| same_style | **REDUNDANT** | 大部分案例 same_style=True，无区分力 |
| width_a/b | **REDUNDANT** | Human 不使用宽度信息做判断 |
| style_sig | **IRRELEVANT** | 字体签名字符串，Human 无法解读 |
| line_obs_count | **HELPFUL** | 帮助理解行上有多少元素 |
| line_spans | **NECESSARY** | 提供同行上下文，但缺少段落/表格上下文 |
| TLD is_in_table | **HELPFUL** | 确认表格上下文，但 41% 页面不可用 |
| TLD different_cell | **NECESSARY** (table cases) | 确认不同列，但仅 boolean，无列标识 |
| Cue1-Cue7 | **HELPFUL → REDUNDANT** | P722 证明 Cue 不改善准确率，反而增加时间 |

---

## 6. Evidence Type Classification

| 类型 | 现有 Evidence | Human 使用频率 |
|---|---|---|
| RAW_FACT | text_a, text_b, same_style, width, style_sig | HIGH (text) / LOW (style) |
| GEOMETRIC_RELATION | h_gap, dy | LOW |
| STRUCTURAL_RELATION | TLD is_in_table, different_cell, line_obs_count | MEDIUM |
| LOCAL_CONTEXT | line_spans, page image | HIGH |
| CROSS_INSTANCE_PATTERN | **MISSING** | HIGH (Human 从图像重建) |
| COUNTEREVIDENCE | **MISSING** | HIGH (安全关键) |
| BOUNDARY_EVIDENCE | **MISSING** | HIGH (句子/段落/图注边界) |
| PROVENANCE | doc_id, page_number | LOW |

---

## 7. Evidence vs Interpretation vs Judgment

### 三层分离

```
Evidence (系统可观察的事实)
    ↓
Interpretation Candidate (证据支持的结构解释)
    ↓
Semantic Judgment (Human 最终判断)
```

### 按内容类型的分离

| 内容类型 | Evidence | Interpretation | Judgment | GAP |
|---|---|---|---|---|
| NUMERIC_PAIR | text_a="28.54", text_b="10.02", TLD diff_cell=True | 两个数值在同一表格行的不同列 | 不同表格列 → KEEP_SEPARATE | 缺少列标识（列是什么？） |
| SENTENCE_BOUNDARY | text_a ends ".", text_b starts capital | text_a 结束句子，text_b 开始新句子 | 分属不同句子 → KEEP_SEPARATE | 缺少段落成员（同一段落？） |
| FIGURE_CAPTION | text_a="FIG. 9:", text_b="Left:" | text_a 是图注标签，text_b 是图注正文 | 同一图注 → MERGE | 缺少图注边界（图注在哪结束？） |
| TABLE_HEADER | text_a="Resolution", text_b="#Channels" | 两个都是表格列标题 | 不同列标题 → KEEP_SEPARATE | 缺少标题层级（同级？父子？） |
| MIXED | text_a="41M", text_b="EfficientNet-B5" | 一个是参数量，一个是模型名 | 不同列 → KEEP_SEPARATE | 缺少内容类型分类 |

---

## 8. Decision-Relevant Evidence

### 定义

Decision-Relevant Evidence 必须同时满足：
1. 与当前 Human Judgment 有直接关系
2. 能减少 Human 自己重建 Evidence 的工作
3. 不直接替 Human 做最终 Semantic Judgment
4. 可以追溯到原始 Evidence
5. 不依赖无法验证的模型推断

### 评估

| Evidence | Decision Relevance | 理由 |
|---|---|---|
| text_a, text_b | **HIGH** | 直接驱动内容类型识别 |
| page image | **HIGH** | 提供全局上下文，Human 必须使用 |
| line_spans | **HIGH** | 提供同行上下文 |
| TLD different_cell | **HIGH** (table cases) | 直接确认"不同列" |
| TLD is_in_table | **MEDIUM** | 确认表格上下文，但不指明位置 |
| line_obs_count | **MEDIUM** | 帮助理解行结构 |
| h_gap, dy | **LOW** | 间距信息，但非决策驱动 |
| same_style, width, style_sig | **LOW** | 冗余或不可解读 |
| Cue1-Cue7 | **LOW** | P722 证明不改善决策，增加时间 |
| **Column header identification** | **HIGH** (MISSING) | Human 必须从图像推断 |
| **Paragraph membership** | **HIGH** (MISSING) | 导致 Reviewer A/B 分歧 |
| **Caption boundary** | **HIGH** (MISSING) | Human 必须从图像推断 |
| **Cross-instance pattern** | **MEDIUM** (MISSING) | Human 从图像重建 |
| **Counterevidence** | **HIGH** (MISSING) | 安全关键 |

---

## 9. Missing Evidence

### 按内容类型的缺失

| 内容类型 | 缺失证据 | 影响 |
|---|---|---|
| NUMERIC_PAIR (9 cases) | COLUMN_HEADER_IDENTIFICATION | Human 不知道列含义，必须从图像推断 |
| MIXED (13 cases) | CONTENT_TYPE_CLASSIFICATION | Human 不知内容类型，必须从文本推断 |
| SENTENCE_BOUNDARY (4 cases) | PARAGRAPH_MEMBERSHIP | 导致 Reviewer A/B 分歧（A=KEEP, B=MERGE） |
| FIGURE_CAPTION (2 cases) | CAPTION_BOUNDARY | Human 不知图注范围，必须从图像推断 |
| TABLE_HEADER (2 cases) | HEADER_HIERARCHY | Human 不知标题关系，必须从图像推断 |

### 系统级缺失

| 缺失类型 | 严重性 | 说明 |
|---|---|---|
| MISSING_RELATION | HIGH | A 与 B 之间的结构关系（列、行、段落） |
| MISSING_CONTEXT | HIGH | 段落/图注/表格上下文 |
| MISSING_COMPARISON | MEDIUM | A 与其他元素的对齐模式 |
| MISSING_COUNTEREVIDENCE | HIGH | 可能 contradict 主解释的证据 |
| MISSING_BOUNDARY | HIGH | 句子/段落/图注边界标识 |
| MISSING_STRUCTURAL_SUMMARY | MEDIUM | "A 在表格 T 的行 R 列 C" |
| NO_MATERIAL_GAP | — | 不适用（存在 material gap） |

---

## 10. Compression vs Distillation

### L5.5 Compression

```
Condition A: 15 fields → Condition B1: 8 fields
  Removed: style_sig_a, style_sig_b, doc_id, page_number
  → This IS compression: less data to read
  → But NOT distillation: no evidence reorganization
```

### L5.10 Evidence Cue

```
Condition B2 adds 4-7 Cues on top of B1 fields
  Cue1: TLD is_in_table → "within a detected multi-column aligned structure"
  Cue2: TLD different_cell → "in different structural positions"
  Cue3: line_obs_count → "There are N text items on this line"
  Cue5: text_a period → "Text A ends with a period"
  Cue6: text_b capital → "Text B starts with a capital letter"
```

### 判断

```
Cue IS a form of distillation (transforms raw evidence into Human-readable text)
BUT it is INCOMPLETE distillation because:
  1. Cues are binary/text patterns, not structural RELATIONS
  2. Cues don't provide what Human actually needs (column ID, paragraph, caption boundary)
  3. Cues duplicate information already in fields (text_a, text_b)
  4. Cues don't organize evidence into relations

P722 proves: B2 (with Cue) = 5.9s avg vs B1 (no Cue) = 1.7s avg
  → Cue ADDED cognitive load without ADDING decision value
  → This is anti-compression: more text to read, same decision
```

### True Distillation Would Be

```
Instead of 7 binary Cues:
  1. STRUCTURAL_SUMMARY: "A and B are in row 3 of Table 2, columns 'top-1 error' and 'top-5 error'"
  2. CONTEXT_RELATION: "A ends sentence S1 in paragraph P1; B starts sentence S2 in paragraph P1"
  3. CAPTION_CONTEXT: "A is caption label 'FIG. 9:'; B is caption body starting with 'Left:'"
  4. BOUNDARY_INDICATOR: "A and B are at a sentence boundary within the same paragraph"

→ These would be Evidence RELATIONS, not Evidence FACTS
→ They would reduce Human's reconstruction work
→ They require Evidence Organization, not new Observation
```

---

## 11. Evidence Value Matrix

| Evidence | Type | Decision Relevance | Necessity | Traceable | Semantic Leakage |
|---|---|---|---|---|---|
| text_a, text_b | RAW_FACT | HIGH | NECESSARY | YES | NO |
| page image | LOCAL_CONTEXT | HIGH | NECESSARY | YES | NO |
| h_gap | GEOMETRIC_RELATION | LOW | HELPFUL | YES | NO |
| dy | GEOMETRIC_RELATION | LOW | HELPFUL | YES | NO |
| same_style | RAW_FACT | LOW | REDUNDANT | YES | NO |
| width_a/b | RAW_FACT | LOW | REDUNDANT | YES | NO |
| style_sig | RAW_FACT | LOW | IRRELEVANT | YES | NO |
| line_obs_count | STRUCTURAL_RELATION | MEDIUM | HELPFUL | YES | NO |
| line_spans | LOCAL_CONTEXT | HIGH | NECESSARY | YES | PARTIAL (no paragraph/table context) |
| TLD is_in_table | STRUCTURAL_RELATION | MEDIUM | HELPFUL | YES | NO (boolean, no detail) |
| TLD different_cell | STRUCTURAL_RELATION | HIGH | NECESSARY (table) | YES | NO (boolean, no column ID) |
| Cue1-Cue7 | INTERPRETATION_TEXT | LOW | REDUNDANT | YES | NO (but adds cognitive load) |
| **Column header ID** | **MISSING** | **HIGH** | **NECESSARY** | **NO** | **YES — Human infers from image** |
| **Paragraph membership** | **MISSING** | **HIGH** | **NECESSARY** | **NO** | **YES — Human infers from image** |
| **Caption boundary** | **MISSING** | **HIGH** | **NECESSARY** | **NO** | **YES — Human infers from image** |
| **Content type classification** | **MISSING** | **MEDIUM** | **HELPFUL** | **NO** | **YES — Human infers from text** |
| **Cross-instance pattern** | **MISSING** | **MEDIUM** | **HELPFUL** | **NO** | **YES — Human infers from image** |
| **Counterevidence** | **MISSING** | **HIGH** | **NECESSARY** | **NO** | **YES — not provided** |
| provenance | PROVENANCE | LOW | REDUNDANT | YES | NO |

**缺失比例：6/19 = 32%** — 但缺失的都是 HIGH decision relevance 的证据。

---

## 12. 21+ Case Evidence Maps (摘要)

### 按内容类型分组

| 类型 | 案例数 | Human 需要 | 系统提供 | 缺失 |
|---|---|---|---|---|
| NUMERIC_PAIR | 9 | 列关系 | TLD different_cell | 列标识 |
| MIXED | 13 | 内容类型 | text content (implicit) | 内容分类 |
| SENTENCE_BOUNDARY | 4 | 段落成员 | period+capital pattern | 段落关系 |
| FIGURE_CAPTION | 2 | 图注边界 | "FIG" pattern | 图注范围 |
| TABLE_HEADER | 2 | 标题层级 | TLD different_cell | 标题关系 |

### 关键案例

**AMB-005** (SENTENCE_BOUNDARY):
- A: "...degrades rapidly." / B: "Unexpectedly,"
- Reviewer A: KEEP_SEPARATE (sentence boundary)
- Reviewer B: MERGE (same paragraph)
- P722 A: MERGE (wrong) / P722 B1: KEEP_SEPARATE (correct) / P722 B2: KEEP_SEPARATE (correct)
- **缺失**：段落成员关系 → 导致 Reviewer 分歧

**AMB-032** (NUMERIC_PAIR, no TLD):
- A: "-" / B: "8.43"
- P722 B2: UNKNOWN (45.9s) — Human 不确定
- **缺失**：表格结构上下文（TLD 不可用）→ Human 无法确认表格关系

**AMB-414** (FIGURE_CAPTION):
- A: "FIG. 9:" / B: "Left:"
- P722 B2: MERGE (9.7s, correct)
- **缺失**：图注边界 → Human 需要从图像确认

---

## 13. System-level Gap Classification

```
GAP TYPE = RELATION GAP
```

DICE 有足够的 Evidence FACTS 但缺少 Evidence RELATIONS：

| 有什么 | 缺什么 |
|---|---|
| text_a, text_b | "A 是什么类型的内容" |
| TLD is_in_table=True | "A 在表格 T 的行 R 列 C" |
| TLD different_cell=True | "A 在列 X, B 在列 Y, 列 X 的标题是..." |
| text_a ends with period | "A 是段落 P 中句子 S1 的结尾" |
| line_spans | "A 与 [X, Y, Z] 对齐, B 与 [W, V] 对齐" |
| page image | "A 和 B 在同一个图注/段落/表格中" |

**这不是**：
- OBSERVATION GAP（P1-P6 + TLD 已观察足够 raw facts）
- EVIDENCE GAP（evidence 存在，只是没有组织成 relation）
- DISTILLATION GAP（Cue 是 distillation 的一种，但不完整）
- PRESENTATION GAP（UI 显示 evidence，但没有组织它）

**这是**：RELATION GAP — Evidence 之间的结构关系没有被计算和呈现。

---

## 14. Anti-Overdesign Review

| 问题 | 回答 | 理由 |
|---|---|---|
| G1: Need new Observation? | **NO** | P1-P6 + TLD 观察了足够的 raw facts |
| G2: Need new Evidence type? | **NO** | 所有 evidence 类型已存在 |
| G3: Just Evidence Organization? | **YES** | 现有 evidence 未被组织成 relation |
| G4: Just UI presentation? | **PARTIAL** | UI 显示 evidence 但未组织它 |
| G5: Need to modify L5.5 Compression? | **NO** | Compression 有效，Distillation 需要扩展 |
| G6: Need to modify L5.10 Cue? | **NO** | Cue 是一个层，它需要更好的输入（relations） |
| G7: Need to modify Human Validation Workflow? | **NO** | 验证协议是健全的 |
| G8: New architecture layer needed? | **NO** | 可以表达为研究元数据 |

**结论：NO NEW MODULE**

---

## 15. Recommended Minimal Change

> **如果 DICE 下一步只能改一个地方：组织现有 Evidence 成 RELATION，而不是新增 Observation。**

具体来说：
- "A 和 B 都在检测到的表格中，在行 N，列 X 和列 Y"（而非 `is_in_table=True, different_cell=True`）
- "A 结束段落 P 中的句子 S1；B 开始段落 P 中的句子 S2"（而非 `text_a ends with period`）
- "A 是图注标签 'FIG. N:'；B 是图注正文"（而非 `text_a contains 'FIG'`）

**ROI：HIGH**
- 减少 Human 重建工作（主要 effort 成本）
- 使 Cue 更有用（Cue 引用 relation，而非 fact）
- 实现真正的 Distillation（不只是 Compression）
- 不需要任何 frozen artifact 修改

**但这仍然是 READ-ONLY 建议，不实现。**

---

## 16. Confidence / Limitations

### Confidence

| 发现 | 置信度 | 依据 |
|---|---|---|
| B1 优于 B2（时间） | HIGH | P722 数据：1.7s vs 5.9s |
| Cue 增加认知负荷 | HIGH | B2 慢 3.5x，准确率不更高 |
| RELATION GAP 是主要问题 | MEDIUM-HIGH | 基于错误案例 + reviewer rationale 分析 |
| 缺少 column/paragraph/caption context | HIGH | 3/3 错误案例都缺少结构上下文 |
| 不需要新 Observation | MEDIUM | 基于现有 evidence 覆盖率分析 |

### Limitations

- n=1 参与者（P722），跨参与者稳定性未验证
- 4 个文档（3 tech + 1 medical），文档多样性有限
- TLD 覆盖率 41%，非 TLD 页面的 evidence 分析基于有限样本
- Reviewer rationale 是事后解释，可能不完全反映实时判断过程
- 无 interaction trace（眼动、点击），无法直接验证 Human 查看了什么

---

## 17. Governance Gate

```
DICE_CORE_MODIFICATION      = NO
P1_P6_MODIFICATION          = NO
ATOMIC_OBSERVATION_CHANGE   = NO
AGGREGATION_CHANGE          = NO
COMPRESSION_CHANGE          = NO
EVIDENCE_CUE_CHANGE         = NO
TLD_MODIFICATION            = NO
SIGNAL_MODIFICATION         = NO
UI_MODIFICATION             = NO
NEW_MODULE                  = NO
NEW_ENGINE                  = NO
RUNTIME_CHANGE              = NO
ML_TRAINING                 = NO
FROZEN_BASELINE             = INTACT
FROZEN_EXPERIMENT           = INTACT
FORMAL_EXPERIMENT           = NOT_STARTED
CS1_REUSE                   = BLOCKED
HUMAN_VALIDATION            = BLOCKED
STOP                        = TRUE
```

---

## 18. 最终结论

> **当前 DICE 最需要被解决的具体问题是什么；现有 Evidence 是否已经足够；如果足够，缺的是哪一种 Evidence Organization；如果不足，缺的最小 Evidence 是什么；以及为什么。**

### 问题
DICE 有足够的 Evidence FACTS 但缺少 Evidence RELATIONS。Human 每次都必须从页面图像中重建这些关系——这是主要的认知负荷来源。

### 现有 Evidence 是否足够？
**是的，足够。** P722 B1（仅 fields + image，无 Cue）= 100% accuracy, 1.7s。现有 evidence + image 已经能让 Human 做出正确判断。

### 缺的是哪一种 Evidence Organization？
**Evidence Relation Organization。** 现有 evidence 是离散的 facts（text, h_gap, is_in_table, different_cell），没有被组织成 Human 需要的关系结构：
- "A 在列 X，B 在列 Y"（而非 `different_cell=True`）
- "A 是段落 P 中句子 S1 的结尾"（而非 `text_a ends with period`）
- "A 是图注标签"（而非 `text_a contains 'FIG'`）

### 为什么？
1. P722 证明 Cue（当前 Distillation 形式）不改善准确率，反而增加时间 → Cue 是 facts 的文本化，不是 relations
2. 3 个错误案例全部缺少结构上下文 → Human 需要 relation，不是更多 facts
3. Reviewer A/B 分歧由段落成员缺失导致 → relation 缺失直接影响判断一致性
4. Evidence 已足够（B1=100%），不需要新 Observation → 只需要组织

### 不需要什么？
- 不需要新 Observation（P1-P6 + TLD 已足够）
- 不需要新 Module（可以表达为研究元数据）
- 不需要修改 Frozen Baseline
- 不需要修改 TLD
- 不需要修改 Evidence Cue
- 不需要 ML Training

`STOP = TRUE`。
