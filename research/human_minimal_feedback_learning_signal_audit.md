# Human Minimal Feedback → Learning Signal Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY / NO IMPLEMENTATION / NO NEW MODULE / FROZEN INTACT / STOP

---

## A. Executive Summary

```
MINIMAL_FEEDBACK_LEARNING_STATUS = PARTIAL
CURRENT_LEARNING_LEVEL = L3
```

> **Human 在极低认知负担下提供的最小反馈（ACCEPT/SPLIT/MERGE/UNKNOWN）可以支持 Machine 发现 Evidence-Grounded Learning Signal Candidate（L3 已达到），但存在一个根本性矛盾：稳定的信号是冗余的（Machine 已有该 Evidence），高信息增量的信号是不稳定的（Human 审阅者之间存在分歧）。当前没有任何 Candidate 达到 L4（Human-validated Reusable Signal）。**

核心发现：

1. **5 个 Learning Signal Candidate 已发现**（L3），其中 4/5 通过了反事实测试（Machine 可从 Evidence 中检测结构，不需要 Human 解释）。
2. **但 4/5 的 Evidence-Grounded Candidate 具有 LOW 信息增量**——Human 只是确认 Machine 已有的 Evidence（BOUNDARY_CONFIRMATION），reuse 节省的 Human effort 极少。
3. **唯一具有 HIGH 信息增量的 Candidate（LSC-02 SENTENCE_BOUNDARY）不稳定**——同一 Evidence 结构（period+capital）导致 Reviewer A 说 SPLIT、Reviewer B 说 MERGE，3/3 案例存在分歧。
4. **Ceiling Effect**：GT 分布为 43 KEEP_SEPARATE / 2 MERGE（96% SPLIT），无任何 Candidate 存在 Negative Cases（同一 Evidence → 不同反馈），无法学习边界。
5. **悖论**：稳定的信号是冗余的；新颖的信号是不稳定的。这是 minimal feedback learning 的根本张力。

---

## B. Current Feedback Inventory

### 数据来源

| 来源 | 数量 | 类型 |
|---|---|---|
| P722 Judgments | 55 | A=15, B1=10, B2=30（最小反馈：KEEP_SEPARATE/MERGE/UNKNOWN） |
| Pilot Judgments | 27 | 最小反馈 + 4 条自然语言反馈 |
| Reviewer A Rationales | 45 | 完整判断 + 解释 |
| Reviewer B Rationales | 45 | 完整判断 + 解释 |
| GT Adjudication | 45 | 冻结最终标签（43 SPLIT, 2 MERGE） |
| **Total** | **172** | — |

### 反馈分布

| 反馈类型 | P722 | Pilot | Reviewer A | Reviewer B | GT |
|---|---|---|---|---|---|
| KEEP_SEPARATE (SPLIT) | 47 | 25 | 43 | 39 | 43 |
| MERGE | 6 | 2 | 2 | 6 | 2 |
| UNKNOWN | 2 | 0 | 0 | 0 | 0 |

### 自然语言反馈

4 条自由文本反馈，全部来自 Pilot P01。内容主要提及：
- "不同表格列"（TABLE_COLUMN_REFERENCE）
- "句子前后半部分"（SENTENCE_REFERENCE）
- "同一内容单元"（SEMANTIC_UNIT_REFERENCE）
- UI 改进建议（"判断选项应该是合适/不合适"）

---

## C. Feedback Information Taxonomy

| 类型 | 数量 | 说明 |
|---|---|---|
| BOUNDARY_CONFIRMATION | 116 | Human 确认 Machine 已有的 Evidence 正确 |
| CONFLICT_SIGNAL | 4 | Reviewer A/B 分歧（同一 Evidence → 不同判断） |
| HUMAN_ONLY_INFORMATION | 4 | 自然语言反馈提供额外信息 |
| EVIDENCE_SUFFICIENCY_SIGNAL | 2 | Human 说 UNKNOWN（Evidence 不足） |
| BOUNDARY_CORRECTION | 1 | Human 判断与 GT 不符（P722 A 条件 AMB-005） |

**关键观察**：116/127（91%）的反馈是 BOUNDARY_CONFIRMATION——Human 主要在确认 Machine 已有的 Evidence，而非提供新信息。

---

## D. Candidate Learning Signals

### LSC-01: TABLE_NUMERIC_DIFF_CELL → SPLIT

| 属性 | 值 |
|---|---|
| Evidence | BOTH_NUMERIC + DIFF_CELL + TABLE (TLD) |
| Feedback | SPLIT (KEEP_SEPARATE) |
| Case Count | 9 |
| Document Count | 3 (resnet, efficientnet, cs_001) |
| Page Count | 4 |
| Independent Settings | 3 |
| Recurrence | STABLE — 9/9 uniform GT, full reviewer agreement |
| Independence | PARTIAL — 55% concentration on resnet p6 |
| Evidence Grounding | EVIDENCE_SUPPORTED |
| Negatives | 0 |
| Conflicts | 0 |
| Boundary Cases | 0 |
| Counterfactual | POTENTIALLY_EVIDENCE_GROUNDED |
| Info Gain | LOW — BOUNDARY_CONFIRMATION |
| Reusability | PARTIAL — stable but ceiling effect, no negatives, TLD coverage 41% |

### LSC-02: SENTENCE_BOUNDARY_PERIOD_CAPITAL → SPLIT

| 属性 | 值 |
|---|---|
| Evidence | CAPITAL + PERIOD |
| Feedback | SPLIT (KEEP_SEPARATE) at GT level |
| Case Count | 3 |
| Document Count | 3 |
| Page Count | 3 |
| Independent Settings | 3 |
| Recurrence | STABLE at GT level — 3/3 KEEP_SEPARATE |
| Independence | INDEPENDENT — 3 docs, 3 pages |
| Evidence Grounding | PARTIAL — period+capital detectable but NOT SUFFICIENT |
| Negatives | 0 |
| Conflicts | 3 — Reviewer B said MERGE on 3/3 cases |
| Boundary Cases | CRITICAL — reviewer disagreement IS the boundary |
| Counterfactual | DEPENDENT_ON_HUMAN_EXPLANATION |
| Info Gain | HIGH — SEMANTIC_CORRECTION |
| Reusability | NOT_READY — Human disagreement prevents safe reuse |

### LSC-03: FIGURE_CAPTION → MERGE

| 属性 | 值 |
|---|---|
| Evidence | CAPITAL + FIG |
| Feedback | MERGE |
| Case Count | 2 |
| Document Count | 1 (resnet only) |
| Page Count | 2 |
| Independent Settings | 1 |
| Recurrence | STABLE — 2/2 MERGE, full agreement |
| Independence | NOT_INDEPENDENT — 1 doc only |
| Evidence Grounding | EVIDENCE_SUPPORTED |
| Negatives | 0 |
| Conflicts | 0 |
| Counterfactual | POTENTIALLY_EVIDENCE_GROUNDED |
| Info Gain | LOW — BOUNDARY_CONFIRMATION |
| Reusability | NOT_READY — insufficient independence |

### LSC-04: MIXED_NUMERIC_TEXT → SPLIT

| 属性 | 值 |
|---|---|
| Evidence | MIXED_NUMERIC_TEXT (one numeric, one text) |
| Feedback | SPLIT (KEEP_SEPARATE) |
| Case Count | 5 |
| Document Count | 4 |
| Page Count | 5 |
| Independent Settings | 5 |
| Recurrence | STABLE — 5/5 KEEP_SEPARATE, full agreement |
| Independence | INDEPENDENT — 4 docs, 5 pages |
| Evidence Grounding | EVIDENCE_SUPPORTED |
| Negatives | 0 |
| Conflicts | 0 |
| Counterfactual | POTENTIALLY_EVIDENCE_GROUNDED |
| Info Gain | LOW — REDUNDANT_CONFIRMATION |
| Reusability | PARTIAL — stable and independent, but very low info gain |

### LSC-05: TABLE_DIFF_CELL_NON_NUMERIC → SPLIT

| 属性 | 值 |
|---|---|
| Evidence | CAPITAL + DIFF_CELL + TABLE (non-numeric table items) |
| Feedback | SPLIT (KEEP_SEPARATE) |
| Case Count | 4 |
| Document Count | 2 |
| Page Count | 4 |
| Independent Settings | 4 |
| Recurrence | STABLE — 4/4 KEEP_SEPARATE, full agreement |
| Independence | INDEPENDENT — 2 docs, 4 pages |
| Evidence Grounding | EVIDENCE_SUPPORTED |
| Negatives | 0 |
| Conflicts | 0 |
| Counterfactual | POTENTIALLY_EVIDENCE_GROUNDED |
| Info Gain | LOW — BOUNDARY_CONFIRMATION |
| Reusability | PARTIAL — stable, independent, but ceiling effect |

---

## E. Counterfactual Test

> 假设 Machine 从来没有看到 Human 的解释文字。只给 Machine：Candidate + P1–P7 Evidence + Human 最小反馈。Machine 能否仍然从 Evidence 中找到重复结构？

| Candidate | Result | Reason |
|---|---|---|
| LSC-01 | POTENTIALLY_EVIDENCE_GROUNDED | TLD provides is_in_table + different_cell; Machine can detect |
| LSC-02 | DEPENDENT_ON_HUMAN_EXPLANATION | Same evidence → different reviewer judgments; paragraph context missing |
| LSC-03 | POTENTIALLY_EVIDENCE_GROUNDED | FIG pattern is detectable; but only 2 cases, 1 doc |
| LSC-04 | POTENTIALLY_EVIDENCE_GROUNDED | Numeric vs text detection is trivial for Machine |
| LSC-05 | POTENTIALLY_EVIDENCE_GROUNDED | TLD provides structural evidence |

**结果**：4/5 通过反事实测试（Machine 可从 Evidence 检测结构），1/5 依赖 Human 解释。

**但**：通过反事实测试的 4 个 Candidate 全部具有 LOW 信息增量——Machine 已经能检测的结构，Human 只是在确认。

---

## F. Information Gain

### 三种信息增量类型

| 类型 | 候选 | Human 给 Machine 增加了什么 |
|---|---|---|
| A. SEMANTIC_CORRECTION (HIGH) | LSC-02 | Human 解决 Machine 无法判定的歧义（period+capital → SPLIT or MERGE?） |
| B. BOUNDARY_CONFIRMATION (LOW) | LSC-01, LSC-03, LSC-05 | Human 确认 Machine 已有的 Evidence 正确 |
| C. REDUNDANT_CONFIRMATION (VERY LOW) | LSC-04 | Human 重复描述 Machine 已计算的内容（numeric vs text） |

### 悖论

```
稳定的信号 ←→ 冗余的信号
LSC-01, LSC-04, LSC-05: 稳定但 LOW info gain
  → Machine 已有 Evidence → Human 只是确认 → reuse 节省少

新颖的信号 ←→ 不稳定的信号
LSC-02: HIGH info gain 但不稳定
  → Evidence 歧义 → Human 分歧 → 信号不可复用
```

**这是 minimal feedback learning 的根本张力**：
- Human 最小反馈（SPLIT/MERGE）能确认 Machine 已有的稳定结构
- 但无法提供 Machine 缺少的语义判断（那需要 Human 解释原因）
- 而需要 Human 解释的地方，Human 之间又会分歧

---

## G. Reusability Readiness

| Candidate | Readiness | 理由 |
|---|---|---|
| LSC-01 | PARTIAL | Stable but ceiling effect, no negatives, TLD coverage 41% |
| LSC-02 | NOT_READY | Reviewer disagreement (CONFLICT), dependent on human explanation |
| LSC-03 | NOT_READY | Only 2 cases, 1 doc, no independence |
| LSC-04 | PARTIAL | Stable, independent, but very low info gain |
| LSC-05 | PARTIAL | Stable, independent, but ceiling effect |

**无任何 Candidate 达到 READY_FOR_HUMAN_VALIDATION**——所有 Candidate 都缺少 negative cases 和 boundary cases。

---

## H. Learning Level

```
CURRENT_LEARNING_LEVEL = L3
```

| Level | 状态 | 说明 |
|---|---|---|
| L0 Feedback Storage | ✓ | 172 instances stored |
| L1 Feedback Accumulation | ✓ | Across P722, pilot, reviewers |
| L2 Evidence-linked Feedback | ✓ | Each feedback linked to evidence structure |
| L3 Candidate Discovery | ✓ | 5 candidates identified |
| L4 Human-validated Reusable Signal | ✗ | No candidate validated on future cases |
| L5 Future-case Reuse | ✗ | No reuse attempted |
| L6 Measured Effort Reduction | ✗ | No measurement |
| L7 Stable Iterative Learning | ✗ | No iteration |

**L3 ≠ Learning**。只有达到 L4 + L5 + L6 之后，才可以讨论 Iterative Learning。

---

## I. Bottleneck

### Bottleneck 1: CEILING EFFECT

GT 分布为 43 KEEP_SEPARATE / 2 MERGE（96% SPLIT）。所有 5 个 Candidate 都是正例（同一 Evidence → 同一反馈），**无任何 Negative Cases**（同一 Evidence → 不同反馈）。

没有 Negative Cases → Machine 无法学习边界 → reuse 不安全。

这不是架构问题，而是**数据分布问题**：当前语料库的 MERGE 案例太少。

### Bottleneck 2: STABILITY-NOVELTY PARADOX

稳定的信号（LSC-01, LSC-04, LSC-05）是冗余的——Machine 已有 Evidence，Human 只在确认。新颖的信号（LSC-02）是不稳定的——同一 Evidence 导致 Human 分歧。

这意味着：**minimal feedback（只有 SPLIT/MERGE/UNKNOWN）在当前 Evidence 体系下，无法同时达到稳定和新颖**。

---

## J. Next-Step Recommendation

只允许推荐：

1. **收集更多 MERGE 案例**：当前 2/45 MERGE 案例导致 ceiling effect。需要更多 MERGE 案例来发现 negative cases 和 boundary cases。
2. **收集独立 Human Feedback**：当前 n=1 参与者（P722）+ 2 reviewers。需要更多独立参与者来验证信号稳定性。
3. **做最小 Human Validation**：在 LSC-04（最独立、最稳定的 Candidate）上做 future case test，验证是否可达到 L4。
4. **暂不推进 LSC-02**：reviewer 分歧意味着需要 paragraph context observation 才能安全复用。

**禁止推荐**：Learning Engine, Pattern Engine, ML training, LLM fine-tuning, 新 DICE Core layer。

---

## K. CS1-CS4 回查

| 候选 | 是否来自 Human Feedback？ | Evidence Grounding？ | 独立重复？ | Negative？ | Conflict？ | 可复用？ |
|---|---|---|---|---|---|---|
| CS1 (DIFFERENT_TABLE_COLUMNS) | 是（70 TABLE_STRUCTURE mentions） | YES (TLD) | PARTIAL (55% one page) | NO | 1 (AMB-005 false positive) | PARTIAL |
| CS2 (SENTENCE_BOUNDARY) | 是（8 SENTENCE_BOUNDARY mentions） | PARTIAL (period+capital) | YES (3 docs) | NO | YES (3/3 reviewer disagreement) | NOT_READY |
| CS3 (FIGURE_CAPTION) | 是（13 FIGURE_CAPTION mentions） | YES (FIG pattern) | NO (1 doc) | NO | NO | NOT_READY |
| CS4 (CATEGORY_HETEROGENEITY) | 是（57 NUMERIC_VALUE mentions） | YES (numeric detection) | YES (4 docs) | NO | NO | PARTIAL (low info gain) |

**关键回查结论**：

- CS1 的 keyword recurrence（70 mentions）确实对应 Evidence-Grounded structure（TLD different_cell），但存在 ceiling effect 和 false positive（AMB-005）。
- CS2 的 keyword recurrence（8 mentions）对应可检测的 text pattern，但同一 pattern 导致 reviewer 分歧——**keyword recurrence ≠ stable signal**。
- CS3 和 CS4 的 keyword recurrence 对应可检测的 evidence，但独立性不足或信息增量极低。
- **此前的 CS1 "成立"结论需要修正**：CS1 在 Evidence Grounding 上成立，但在 Reusability 上仅为 PARTIAL（无 negatives，ceiling effect，TLD 覆盖率限制）。

---

## L. Evidence Structure Grouping (Counterfactual)

将 45 GT 案例按 Evidence Structure 签名分组：

| Signature | Cases | GT | Reviewer A/B Agreement |
|---|---|---|---|
| NONE | 12 | 12 SPLIT | 12/12 |
| BOTH_NUMERIC\|DIFF_CELL\|TABLE | 9 | 9 SPLIT | 9/9 |
| MIXED_NUMERIC_TEXT | 5 | 5 SPLIT | 5/5 |
| BOTH_NUMERIC | 5 | 5 SPLIT | 5/5 |
| CAPITAL\|DIFF_CELL\|TABLE | 4 | 4 SPLIT | 4/4 |
| CAPITAL\|PERIOD | 3 | 3 SPLIT | **0/3** ← disagreement |
| CAPITAL | 2 | 2 SPLIT | 2/2 |
| CAPITAL\|FIG | 2 | 2 MERGE | 2/2 |
| CAPITAL\|DIFF_CELL\|PERIOD\|TABLE | 1 | 1 SPLIT | **0/1** ← disagreement |
| DIFF_CELL\|TABLE | 1 | 1 SPLIT | 1/1 |
| CAPITAL\|DIFF_CELL\|MIXED_NUMERIC_TEXT\|TABLE | 1 | 1 SPLIT | 1/1 |

**关键发现**：
- 所有 11 组在 GT 层面都是 uniform（同一 Evidence → 同一 GT）
- 但 CAPITAL\|PERIOD 组在 reviewer 层面有分歧（A=SPLIT, B=MERGE）
- 这意味着：**GT 稳定 ≠ Human 判断稳定**

---

## M. Confidence / Limitations

### Confidence

| 发现 | 置信度 | 依据 |
|---|---|---|
| 5 个 Candidate 已发现 | HIGH | 45 GT 案例完整分组 |
| 4/5 通过反事实测试 | HIGH | Evidence structure 可由 Machine 计算 |
| LSC-02 有 reviewer 分歧 | HIGH | 3/3 案例中 Reviewer B 说 MERGE |
| Ceiling Effect 限制 reuse | HIGH | 96% KEEP_SEPARATE, 0 negatives |
| Stability-Novelty Paradox | MEDIUM-HIGH | 基于 5 个 Candidate 的 info gain vs stability 分析 |

### Limitations

- n=1 P722 参与者 + 2 reviewers，跨参与者稳定性未验证
- 4 文档（3 tech + 1 medical），语料多样性有限
- TLD 覆盖率 41%，非 TLD 页面的 Evidence 结构分析基于有限样本
- 无 future case test（L4 未达到）
- GT 是 adjudicated 结果，可能不完全反映实时 Human 判断过程
- 自由文本反馈仅 4 条，不足以做统计推断

---

## N. Anti-Overdesign Gate

```
DICE_CORE_MODIFICATION              = NO
P1_P7_MODIFICATION                  = NO
TLD_MODIFICATION                    = NO
ATOMIC_OBSERVATION_MODIFICATION     = NO
EVIDENCE_CUE_MODIFICATION           = NO
NEW_MODULE                          = NO
NEW_ENGINE                          = NO
ML_TRAINING                         = NO
LLM_TRAINING                        = NO
RUNTIME_CHANGE                      = NO
CAPABILITY_REGISTRATION_CHANGE      = NO
FROZEN_BASELINE                     = INTACT
FROZEN_EXPERIMENT                   = INTACT
FORMAL_EXPERIMENT                   = NOT_STARTED
STOP                                = TRUE
```

---

## O. Governance Gate

```
DICE_CORE_MODIFICATION      = NO
P1_P7_MODIFICATION          = NO
TLD_MODIFICATION            = NO
ATOMIC_OBSERVATION_CHANGE   = NO
AGGREGATION_CHANGE          = NO
COMPRESSION_CHANGE          = NO
EVIDENCE_CUE_CHANGE         = NO
SIGNAL_MODIFICATION         = NO
UI_MODIFICATION             = NO
NEW_OBJECT_IMPLEMENTATION   = NO
NEW_MODULE                  = NO
NEW_ENGINE                  = NO
RUNTIME_CHANGE              = NO
ML_TRAINING                 = NO
FROZEN_BASELINE             = INTACT (drift=0/7)
FROZEN_EXPERIMENT           = INTACT
FORMAL_EXPERIMENT           = NOT_STARTED
CS1_REUSE                   = BLOCKED
HUMAN_VALIDATION            = BLOCKED
STOP                        = TRUE
```

---

## P. 最终结论

> **如果把 Human 的操作压缩到只有 ACCEPT / SPLIT / MERGE / UNKNOWN，那么这些极简反馈是否足以支持 Machine 逐步发现可复用的 Evidence-Grounded Learning Signal？**

### 答案：PARTIAL

### 理由

**支持 PARTIAL（非 YES）的因素**：
1. 4/5 Candidate 通过反事实测试——Machine 可从 Evidence 检测结构
2. Feedback 已链接到 Evidence（L2 达成）
3. Candidate 已发现（L3 达成）
4. 框架在原理上可行——瓶颈是数据，不是架构

**反对 YES 的因素**：
1. 4/5 Evidence-Grounded Candidate 具有 LOW 信息增量——Human 确认 Machine 已有的 Evidence，reuse 节省极少
2. 唯一 HIGH 信息增量的 Candidate（LSC-02）不稳定——reviewer 分歧
3. Ceiling Effect：96% SPLIT，0 negative cases，无法学习边界
4. 无 future case test（L4 未达到）
5. **Stability-Novelty Paradox**：稳定的信号冗余，新颖的信号不稳定

### 核心原则验证

> *Human should provide the smallest possible semantic feedback; Machine should do the abstraction, recurrence detection, evidence linkage, and reusable-signal discovery.*

当前状态：
- Human 最小反馈：✅ 已收集（172 instances）
- Machine abstraction：✅ Evidence structure grouping 完成
- Recurrence detection：✅ 5 candidates found
- Evidence linkage：✅ 4/5 evidence-grounded
- Reusable-signal discovery：❌ No candidate reached L4

> *Do not make Human explain the document. Make Human correct the Machine.*

当前状态：
- Human 主要在确认 Machine（116/127 = 91% BOUNDARY_CONFIRMATION）
- Human 极少需要解释文档（仅 4 条自由文本反馈）
- 但在需要 Human 语义判断的地方（LSC-02），Human 之间会分歧

> *Human Feedback is not Knowledge. Human Feedback is a learning signal candidate source.*

当前状态：
- Human Feedback 确实只是 Candidate Source（L3）
- 无任何 Candidate 成为 Reusable Knowledge（L4 未达到）

`STOP = TRUE`。
