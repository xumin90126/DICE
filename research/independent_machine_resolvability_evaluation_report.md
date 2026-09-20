# Independent Machine-Resolvability Evaluation Report

## FROZEN OUT-OF-SAMPLE EVALUATION — NO RULE TUNING / NO IMPLEMENTATION

| 字段 | 值 |
|------|-----|
| 实验类型 | Independent Machine-Resolvability Evaluation |
| 评估集 | Frozen 69 cases (4 independent PDFs) |
| 特征规范 | FROZEN IS-01 / IS-02 |
| 决策协议 | FROZEN §9.3 |
| 确定性验证 | DETERMINISTIC = TRUE ✅ (Run 1 = Run 2) |
| 执行时间 | 2026-09-09 |
| G7 (Precision ≥ 95%) | **FAIL** (Precision = 0.000) |
| G8 (Recall ≥ 80%) | **FAIL** (Recall = 0.000) |
| 最终结论 | **MACHINE-RESOLVABILITY NOT DEMONSTRATED** |
| STOP | TRUE |

---

## 1. Experimental Objective

验证在冻结的 IS-01 (TEXT_NUMBER_PATTERN) + IS-02 (TEXT_READABLE_TITLE) 特征规范下，系统是否能在独立评估集上对 boundary cases 做出确定且正确的 MERGE / KEEP_SEPARATE / INSUFFICIENT_EVIDENCE 决策，且达到预注册的 G7 (Precision ≥ 95%) 和 G8 (Recall ≥ 80%) 门限。

---

## 2. Frozen Inputs

### 2.1 Evaluation Set

| 属性 | 值 |
|------|-----|
| 来源 | `independent_evaluation_sampling_frame.json` (FROZEN) |
| 总案例数 | 69 |
| 采样种子 | 20240908 |
| 分层方法 | 纯几何分层 (gap bins, w_b bins, line_obs bins, w_a bins) |
| 文档覆盖 | ind_arxiv_2402=4, ind_arxiv_bio2=25, ind_qbio_genomics=23, ind_qbio_rna=17 |
| 独立性 | 4 PDFs 完全独立 (零 P7 制品引用) |

### 2.2 Semantic Ground Truth

| 属性 | 值 |
|------|-----|
| 来源 | `independent_evaluation_semantic_gt.json` (FROZEN) |
| GT 层级 | Level 2 (双审查者一致 68 + 裁定 1) |
| 一致率 | 98.6% (Cohen's Kappa = 0.968) |
| GT 分布 | MERGE=24, KEEP_SEPARATE=45 |
| 可用率 | 69/69 = 100% |
| GT 来源 | 人工语义判断 (非几何 GT) |

### 2.3 Frozen Input Hashes

| 输入 | SHA256 (前16位) |
|------|-----------------|
| Evaluation Set | (记录于 results.json) |
| Semantic GT | (记录于 results.json) |
| Feature Spec | FROZEN in experiment_design.md §6.2-6.3 |
| Decision Protocol | FROZEN in experiment_design.md §9.3 |

---

## 3. Frozen Feature Definitions

### 3.1 IS-01: TEXT_NUMBER_PATTERN (FROZEN)

```
re.match(r'^\d+(\.\d+)*\.?$', text.strip()) OR re.match(r'^[A-Z]\.\d+$', text.strip())
```

- 输入: text_a (string)
- 输出: boolean
- 已知限制: 不区分 heading number 与 equation number (FROZEN, 不可修改)

### 3.2 IS-02: TEXT_READABLE_TITLE (FROZEN)

```
any(len(re.sub(r'[^a-zA-Z]', '', w)) > 2 for w in text.split())
```

- 输入: text_b (string)
- 输出: boolean
- 已知限制: "cos"/"sin"/"and"/"are" 等短词匹配为 readable (3 chars > 2) (FROZEN, 不可修改)

---

## 4. Decision Protocol

### 4.1 冻结协议 (experiment_design.md §9.3)

```
Step 1: Compute IS-01(text_a), IS-02(text_b) using frozen definitions
Step 2: IS-01(text_a)==True AND IS-02(text_b)==True  → MERGE
Step 3: IS-01(text_a)==False AND IS-02(text_b)==False → KEEP_SEPARATE
Step 4: Otherwise (mixed signals)                     → INSUFFICIENT_EVIDENCE
```

### 4.2 协议性质

此协议是 **确定性映射** (deterministic mapping)，非 if-then production rule。同一输入必定产生同一输出。

### 4.3 未自行发明新规则

本实验严格使用冻结设计文档 §9.3 中定义的唯一决策映射。未增加任何新规则、阈值或启发式。

---

## 5. Evaluation Set

69 cases 来自 4 个独立 PDF，通过冻结 P1-P6 管道提取 AMBIGUOUS 状态案例，经纯几何分层随机采样 (seed=20240908) 选出。

### 5.1 Boundary Class 分布

| Boundary Class | 数量 |
|---------------|------|
| BODY_TEXT_CONTINUATION | 27 |
| REFERENCE_LIST_ENTRY | 16 |
| TABLE_CELL | 11 |
| OTHER_AMBIGUOUS | 9 |
| TABLE_CELL_PAIR | 4 |
| FIGURE_LABEL | 2 |
| **TOC_SECTION_NUMBER_TITLE** | **0** |
| **APPENDIX_LETTER_TITLE** | **0** |

**重要发现**: 独立评估集中 **零** TOC_SECTION_NUMBER_TITLE 和 APPENDIX_LETTER_TITLE 案例。这 4 个 PDF 的 AMBIGUOUS 案例主要来自参考文献列表、正文续行和表格单元格。

---

## 6. Ground Truth

| GT 标签 | 数量 | 占比 |
|---------|------|------|
| MERGE | 24 | 34.8% |
| KEEP_SEPARATE | 45 | 65.2% |
| UNRESOLVED | 0 | 0.0% |

GT 层级:
- LEVEL_2_AGREED: 68 (双审查者一致)
- LEVEL_2_ADJUDICATED: 1 (第三审查者裁定)

---

## 7. Confusion Matrix

以 Semantic GT 为唯一正式 ground truth:

| | GT: MERGE | GT: KEEP_SEPARATE | 总计 |
|---|-----------|-------------------|------|
| **Machine: MERGE** | TP = 0 | FP = 3 | 3 |
| **Machine: KEEP_SEPARATE** | FN = 2 | TN = 8 | 10 |
| **Machine: INSUFFICIENT_EVIDENCE** | 22 | 34 | 56 |
| **总计** | 24 | 45 | 69 |

- TP (machine MERGE + GT MERGE) = **0**
- FP (machine MERGE + GT KEEP_SEPARATE) = **3**
- TN (machine KEEP_SEPARATE + GT KEEP_SEPARATE) = **8**
- FN (machine KEEP_SEPARATE + GT MERGE) = **2**
- ABSTAIN (INSUFFICIENT_EVIDENCE) = **56**

---

## 8. Overall Metrics

| 指标 | 公式 | 值 |
|------|------|-----|
| Precision | TP / (TP + FP) = 0 / (0 + 3) | **0.000** |
| Recall | TP / (TP + FN) = 0 / (0 + 2) | **0.000** |
| F1 | 2·P·R / (P + R) | **0.000** |
| Accuracy | (TP + TN) / total = (0 + 8) / 69 | **0.116** |
| FPR | FP / (FP + TN) = 3 / (3 + 8) | **0.273** |
| FNR | FN / (FN + TP) = 2 / (2 + 0) | **1.000** |
| Coverage | 确定性 decisions / total = 13 / 69 | **0.188** |
| Abstention Rate | INSUFFICIENT_EVIDENCE / total = 56 / 69 | **0.812** |

### 8.1 IS Feature Observation Summary

| 特征 | True | False |
|------|------|-------|
| IS-01(text_a) | 11 (15.9%) | 58 (84.1%) |
| IS-02(text_b) | 51 (73.9%) | 18 (26.1%) |

---

## 9. G7 Result: Precision ≥ 95%

| 字段 | 值 |
|------|-----|
| 阈值 | 0.95 |
| 实际值 | 0.000 |
| TP | 0 |
| FP | 3 |
| **G7** | **FAIL** ❌ |

Precision = 0/3 = 0%。机器在所有 3 次做出 MERGE 决策时全部错误。

---

## 10. G8 Result: Recall ≥ 80%

| 字段 | 值 |
|------|-----|
| 阈值 | 0.80 |
| 实际值 | 0.000 |
| TP | 0 |
| FN | 2 |
| Abstain on GT=MERGE | 22 |
| **G8** | **FAIL** ❌ |

Recall = 0/2 = 0%。机器在覆盖范围内正确识别的 MERGE 案例为零。另有 22 个 GT=MERGE 案例被 abstain。

---

## 11. Cross-Document Analysis

| 文档 | 总数 | GT MERGE | GT KEEP_SEP | TP | FP | TN | FN | ABSTAIN | Precision | Recall | FPR | Abstention | 标记 |
|------|------|----------|-------------|----|----|----|----|---------|-----------|--------|-----|-----------|------|
| ind_arxiv_2402 | 4 | 2 | 2 | 0 | 0 | 0 | 0 | 4 | 0.000 | 0.000 | 0.000 | 100% | LOW_SAMPLE |
| ind_arxiv_bio2 | 25 | 7 | 18 | 0 | 0 | 5 | 0 | 20 | 0.000 | 0.000 | 0.000 | 80% | |
| ind_qbio_genomics | 23 | 9 | 14 | 0 | 0 | 2 | 0 | 21 | 0.000 | 0.000 | 0.000 | 91% | |
| ind_qbio_rna | 17 | 6 | 11 | 0 | 3 | 1 | 2 | 11 | 0.000 | 0.000 | 0.273 | 65% | |

### 11.1 跨文档发现

1. **ind_arxiv_2402** (LOW_SAMPLE): 仅 4 个案例，全部 abstain。无法得出有意义结论。
2. **ind_arxiv_bio2**: 25 个案例，20 个 abstain (80%)。5 个 TN (正确 KEEP_SEPARATE)，0 个 FP/FN/TP。
3. **ind_qbio_genomics**: 23 个案例，21 个 abstain (91%)。2 个 TN，0 个 FP/FN/TP。
4. **ind_qbio_rna**: 17 个案例，是唯一产生 FP 和 FN 的文档。3 个 FP + 2 个 FN，全部错误决策集中于此文档。

**跨文档泛化失败**: 没有任何一个文档产生 TP。所有 FP 集中在 ind_qbio_rna (表格单元格场景)。

---

## 12. Boundary-Class Analysis

| Boundary Class | 总数 | TP | FP | TN | FN | ABSTAIN | Precision | Recall |
|---------------|------|----|----|----|----|---------|-----------|--------|
| BODY_TEXT_CONTINUATION | 27 | 0 | 0 | 3 | 1 | 23 | N/A | 0.000 |
| REFERENCE_LIST_ENTRY | 16 | 0 | 0 | 0 | 1 | 15 | N/A | 0.000 |
| TABLE_CELL | 11 | 0 | 3 | 0 | 0 | 8 | 0.000 | N/A |
| OTHER_AMBIGUOUS | 9 | 0 | 0 | 2 | 0 | 7 | N/A | N/A |
| TABLE_CELL_PAIR | 4 | 0 | 0 | 3 | 0 | 1 | N/A | N/A |
| FIGURE_LABEL | 2 | 0 | 0 | 0 | 0 | 2 | N/A | N/A |
| TOC_SECTION_NUMBER_TITLE | 0 | — | — | — | — | — | N/A | N/A |
| APPENDIX_LETTER_TITLE | 0 | — | — | — | — | — | N/A | N/A |

### 12.1 关键发现

1. **TOC_SECTION_NUMBER_TITLE = 0**: 独立评估集中无 TOC 编号+标题案例。IS-01+IS-02 原始设计目标场景在独立数据中 **不存在**。
2. **TABLE_CELL 是唯一 FP 来源**: 3 个 FP 全部来自 TABLE_CELL 类 (表格中的数字+可读词对)。
3. **BODY_TEXT_CONTINUATION 和 REFERENCE_LIST_ENTRY 各贡献 1 个 FN**: 引用片段 ("et"/"al.,", "al.,"/"2025).") 被 IS-01+IS-02 判为 KEEP_SEPARATE，但 GT=MERGE。

### 12.2 OUT_OF_SCOPE 标记

以下 boundary class **不属于** IS-01+IS-02 的原始设计目标 (TOC_SECTION_NUMBER_TITLE / APPENDIX_LETTER_TITLE):

- BODY_TEXT_CONTINUATION (27 cases) — OUT_OF_SCOPE
- REFERENCE_LIST_ENTRY (16 cases) — OUT_OF_SCOPE
- TABLE_CELL (11 cases) — OUT_OF_SCOPE
- OTHER_AMBIGUOUS (9 cases) — OUT_OF_SCOPE
- TABLE_CELL_PAIR (4 cases) — OUT_OF_SCOPE
- FIGURE_LABEL (2 cases) — OUT_OF_SCOPE

**69/69 = 100% 的独立评估案例属于 OUT_OF_SCOPE**。目标 boundary class (TOC_SECTION_NUMBER_TITLE + APPENDIX_LETTER_TITLE) 在独立评估集中覆盖率为 0%。

**未删除任何案例**。所有 69 个案例均参与评估，但上述 boundary class 的结果不应用于支持 TOC/Appendix machine-resolvability 的 claim。

---

## 13. Historical Adversarial Analysis

### 13.1 历史 Adversarial Cases (非独立评估)

| Case | text_a | text_b | IS-01_a | IS-02_b | Machine (protocol) | Human | 正确? |
|------|--------|--------|---------|---------|-------------------|-------|------|
| AMB-018 | "6.1" | "SMEFT" | True | True | MERGE | MERGE | ✓ (TP) |
| AMB-040 | "( )" | "cos(" | False | True* | INSUFFICIENT_EVIDENCE | KEEP_SEPARATE | ✓ (abstain correct) |

*IS-02 loose detection: "cos" matches as readable word (3 chars > 2)

**注意**: 这些案例来自 Round 1 (Discovery Set)，**不是独立评估**。不计入 G7/G8 指标。仅作为 HISTORICAL ADVISORY ANALYSIS 报告。

### 13.2 历史 vs 独立对比

| 维度 | 历史 (Round 1) | 独立评估 |
|------|---------------|---------|
| AMB-018-like (number+title, GT=MERGE) | 1 case, protocol 正确 | **0 cases** (目标场景不存在) |
| AMB-040-like (formula, GT=KEEP_SEP) | 1 case, protocol 正确 abstain | 0 cases (但 9 cases 有 IS-02 loose detection) |
| FP on table cells | 未测试 | **3 cases** (全部 FP) |

---

## 14. Independent Adversarial Analysis

### 14.1 Independent Adversarial Subset

独立评估集中存在 3 个 adversarial-like cases (machine MERGE + GT KEEP_SEPARATE):

| Case | text_a | text_b | IS-01_a | IS-02_b | GT | Machine | 失败模式 |
|------|--------|--------|---------|---------|----|---------|---------|
| IND-AMB-247 | "121" | "40 mM Hepes" | True | True | KEEP_SEPARATE | MERGE | Number + readable token in table cell |
| IND-AMB-223 | "5." | "SARS-CoV-2" | True | True | KEEP_SEPARATE | MERGE | Number + readable token in table cell |
| IND-AMB-235 | "6." | "RNA" | True | True | KEEP_SEPARATE | MERGE | Number + readable token in table cell |

### 14.2 独立 Adversarial 结论

3/3 adversarial cases 全部失败 (100% FP rate on adversarial subset)。失败模式一致: **表格中的数字 + 可读词对**，IS-01 匹配数字，IS-02 匹配真实可读词 (Hepes/SARS/RNA)，但语义上它们属于不同表格列，不应合并。

---

## 15. Failure Analysis

### 15.1 失败分类

| 类别 | 数量 | 说明 |
|------|------|------|
| A. IS-01 failure | 0 | IS-01 本身未失效 |
| B. IS-02 failure | 0 | IS-02 本身未失效 (loose detection 存在但未直接导致 FP) |
| C. Feature combination insufficient | 2 | IS-01_a=False + IS-02_b=False → KEEP_SEPARATE, but GT=MERGE |
| D. Geometry/feature evidence insufficient | 56 | 混合信号 → INSUFFICIENT_EVIDENCE |
| E. Semantic boundary not recoverable | 0 | (包含在 D 中) |
| F. Out-of-scope | 69 | 所有案例均非 TOC_SECTION_NUMBER_TITLE |
| G. Implementation defect | 0 | 无代码错误 |

### 15.2 逐 Case 失败分析

#### False Positives (3 cases) — A_IS01_IS02_FP

| Case | text_a | text_b | 失败原因 |
|------|--------|--------|---------|
| IND-AMB-247 | "121" | "40 mM Hepes" | IS-01 匹配 "121" (数字), IS-02 匹配 "Hepes" (可读词)。但 "121" 是 RNA 长度, "40 mM Hepes" 是缓冲液描述 — 不同表格列 |
| IND-AMB-223 | "5." | "SARS-CoV-2" | IS-01 匹配 "5." (编号), IS-02 匹配 "SARS" (可读词)。但 "5." 是 case 编号, "SARS-CoV-2" 是样本名 — 不同表格列 |
| IND-AMB-235 | "6." | "RNA" | IS-01 匹配 "6." (编号), IS-02 匹配 "RNA" (可读词)。但 "6." 是 case 编号, "RNA" 是样本类型 — 不同表格列 |

**FP 模式**: number + readable token in TABLE_CELL。这正是实验设计文档 §10.3 中预测的 "Number + non-title" adversarial 类型。

#### False Negatives (2 cases) — C_FEATURE_COMBINATION_INSUFFICIENT

| Case | text_a | text_b | 失败原因 |
|------|--------|--------|---------|
| IND-AMB-200 | "et" | "al.," | 两者均无 IS-01 匹配 (非数字) 和 IS-02 匹配 (≤2 字母词) → KEEP_SEPARATE。但 GT=MERGE (引用片段 "et al.,") |
| IND-AMB-201 | "al.," | "2025)." | IS-01_a=False ("al.," 非数字), IS-02_b=False ("2025)." 无 >2 字母词) → KEEP_SEPARATE。但 GT=MERGE (引用片段 "al., 2025).") |

**FN 模式**: 引用列表中的连续文本片段，既非数字也无可读词，IS-01+IS-02 无法识别。

#### Abstentions (56 cases) — D_INSUFFICIENT_EVIDENCE

| 子类 | 数量 | 说明 |
|------|------|------|
| IS-01_a=True + IS-02_b=False | 8 | 数字在 text_a, 但 text_b 无可读词 → abstain |
| IS-01_a=False + IS-02_b=True | 48 | text_a 非数字, 但 text_b 有可读词 → abstain |

Abstention 按 GT:
- GT=MERGE: 22 cases (missed MERGE opportunities)
- GT=KEEP_SEPARATE: 34 cases (correctly abstained)

---

## 16. False Positive Analysis

### 16.1 FALSE POSITIVE MODE

**FP 模式确认**: number + readable token in TABLE_CELL

3/3 FP 案例呈现完全一致的模式:
1. text_a 是表格中的数字 (编号或数值)
2. text_b 是表格中另一列的可读词 (样本名/描述)
3. IS-01 正确匹配数字模式
4. IS-02 正确匹配可读词 (>2 字母)
5. 但语义上它们属于不同表格列 → GT=KEEP_SEPARATE

### 16.2 IS-02 Loose Detection 检查

| 检查项 | 结果 |
|--------|------|
| FP 由 IS-02 loose detection (cos/sin/and/are) 直接导致 | ❌ 否 |
| FP 中 IS-02 匹配的可读词 | "Hepes", "SARS", "RNA" — 均为真实可读词 |
| IS-02 loose detection 存在的案例 | 9 cases (但全部因 IS-01_a=False 而 abstain, 未导致 FP) |

**关键发现**: IS-02 loose detection **未直接导致 FP**。FP 的根因是 IS-01+IS-02 的 feature 组合在 TABLE_CELL 场景下的 **语义不足** — 它们能正确识别数字和可读词，但无法区分 "TOC 编号+标题" 与 "表格数字+描述"。

### 16.3 IS-01 + IS-02 是否足以承担 deterministic semantic boundary decision?

**否。** 在当前独立评估集上:
- IS-01+IS-02 产生 MERGE 决策的 3 次全部错误 (FP rate = 100%)
- 正确 MERGE 决策 (TP) = 0
- 这直接证明 IS-01+IS-02 **不足以** 承担 deterministic semantic boundary decision

---

## 17. False Negative Analysis

2 个 FN 案例均为引用列表中的文本片段:
- "et" + "al.," → GT=MERGE (引用作者缩写)
- "al.," + "2025)." → GT=MERGE (引用年份结尾)

这些案例中 text_a 和 text_b 既非数字也无可读词 (>2 字母)，IS-01+IS-02 均返回 False，协议判为 KEEP_SEPARATE。

**根因**: IS-01 仅检测数字模式，IS-02 仅检测可读词。引用列表中的短文本片段 ("et", "al.,", "2025).") 不满足任一条件。

---

## 18. Abstention Analysis

### 18.1 Abstention 统计

| 维度 | 值 |
|------|-----|
| 总 abstention | 56 / 69 = 81.2% |
| Abstain + GT=MERGE | 22 |
| Abstain + GT=KEEP_SEPARATE | 34 |
| IS-01_a=True + IS-02_b=False | 8 (全部 GT=KEEP_SEPARATE) |
| IS-01_a=False + IS-02_b=True | 48 (22 GT=MERGE + 26 GT=KEEP_SEPARATE) |

### 18.2 Abstention 是否集中于某一 boundary class?

| Boundary Class | Abstain | 总数 | Abstain Rate |
|---------------|---------|------|-------------|
| BODY_TEXT_CONTINUATION | 23 | 27 | 85.2% |
| REFERENCE_LIST_ENTRY | 15 | 16 | 93.8% |
| TABLE_CELL | 8 | 11 | 72.7% |
| OTHER_AMBIGUOUS | 7 | 9 | 77.8% |
| TABLE_CELL_PAIR | 1 | 4 | 25.0% |
| FIGURE_LABEL | 2 | 2 | 100% |

Abstention 跨所有 boundary class 普遍存在，未高度集中于单一类别。但 REFERENCE_LIST_ENTRY (93.8%) 和 FIGURE_LABEL (100%) 的 abstention 率最高。

### 18.3 Abstention 是否跨 document 稳定?

| 文档 | Abstain | 总数 | Abstain Rate |
|------|---------|------|-------------|
| ind_arxiv_2402 | 4 | 4 | 100% |
| ind_arxiv_bio2 | 20 | 25 | 80% |
| ind_qbio_genomics | 21 | 23 | 91% |
| ind_qbio_rna | 11 | 17 | 65% |

Abstention 跨文档稳定存在 (65%-100%)。

### 18.4 Abstention 是否减少 false positive?

**是。** 8 个 IS-01_a=True + IS-02_b=False 的 abstention 案例全部 GT=KEEP_SEPARATE。如果协议在 IS-01_a=True 时强制 MERGE (不等待 IS-02_b)，将产生 8 个额外 FP。INSUFFICIENT_EVIDENCE 机制正确阻止了这些 FP。

### 18.5 Abstention 是否导致 recall 降低?

**是。** 22 个 GT=MERGE 案例被 abstain，导致 recall = 0%。如果这些案例能被正确识别，recall 将显著提升。但由于 IS-01+IS-02 无法区分它们，abstain 是诚实且正确的拒绝。

---

## 19. Boundary Shrinkage

### 19.1 三个必须分别报告的数字

| 数字 | 公式 | 值 |
|------|------|-----|
| **1. Potential Resolution Rate** | Level 2 / Level 1 = 11 / 69 | **15.9%** |
| **2. Machine Deterministic Resolution Rate** | Level 3 / Level 1 = 13 / 69 | **18.8%** |
| **3. Independently Validated Boundary Shrinkage Rate** | Level 4 / Level 1 = 0 / 69 | **0.0%** |

### 19.2 四级 Shrinkage

| 级别 | 名称 | 定义 | 值 |
|------|------|------|-----|
| Level 1 | Baseline Ambiguity | 独立评估集中需要 Human 的数量 | 69 |
| Level 2 | Potential Machine-Resolvable | IS-01_a=True 的案例数 (可能可判定) | 11 (15.9%) |
| Level 3 | Actual Machine-Resolved | 机器给出确定 decision (非 abstain) | 13 (18.8%) |
| Level 4 | Independently Validated | 机器 decision 正确 AND G7+G8 通过 | 0 (0.0%) |

### 19.3 Actual Boundary Shrinkage Rate

```
Actual Boundary Shrinkage Rate
= Independently Validated Machine-Resolved Cases / Baseline Ambiguous Cases
= 0 / 69
= 0.0%
```

**BOUNDARY_SHRINKAGE = NOT_VALIDATED** (G7/G8 未通过)

---

## 20. Limitations

| # | 限制 | 影响 |
|---|------|------|
| L1 | 独立评估集中 0 个 TOC_SECTION_NUMBER_TITLE 案例 | IS-01+IS-02 的原始设计目标场景未被测试 |
| L2 | 81.2% abstention rate | 机器在大多数案例上无法做出确定决策 |
| L3 | 3/3 MERGE 决策全部错误 | IS-01+IS-02 在 TABLE_CELL 场景下产生 100% FP |
| L4 | 0 TP | 机器从未正确识别 MERGE 案例 |
| L5 | IS-02 loose detection (cos/sin/and/are) | 存在但未直接导致 FP (因 IS-01_a=False 而 abstain) |
| L6 | IS-01 不区分 heading number vs table number | "5." 和 "6." 匹配 number pattern 但实为表格 case 编号 |
| L7 | 仅 4 个独立 PDF | 样本量有限，特别是 ind_arxiv_2402 仅 4 个案例 |
| L8 | Timer 未修复 | Human cost 无法测量 (NOT AUTHORIZED) |
| L9 | 无 TOC 页面文档 | 4 个 PDF 均无 TOC 页面，无法验证 TOC 场景 |

---

## 21. No Post-Hoc Tuning Statement

本实验严格遵守以下纪律:

- ❌ 未修改 IS-01 regex
- ❌ 未修改 IS-02 readable-title definition
- ❌ 未修改 threshold
- ❌ 未增加新 feature
- ❌ 未删除 feature
- ❌ 未修改 candidate
- ❌ 未修改 Evaluation Set
- ❌ 未修改 Human GT
- ❌ 未修改 Sampling Frame
- ❌ 未修改 Sampling Seed
- ❌ 未修改 P4 或任何 frozen production code
- ❌ 未手工修正 false positive
- ❌ 未删除 failure case
- ❌ 未增加样本

所有结果保持原始状态。任何改进只能进入 NEXT INDEPENDENT EXPERIMENT。

---

## 22. Reproducibility

### 22.1 实验 Hash

| 输入 | Hash |
|------|------|
| Evaluation Set | `independent_evaluation_sampling_frame.json` (FROZEN) |
| Semantic GT | `independent_evaluation_semantic_gt.json` (FROZEN) |
| Feature Spec | FROZEN in `independent_machine_resolvability_experiment_design.md` §6.2-6.3 |
| Decision Protocol | FROZEN in `independent_machine_resolvability_experiment_design.md` §9.3 |
| Evaluation Script | `independent_machine_resolvability_evaluate.py` |

### 22.2 确定性验证

| 检查 | 结果 |
|------|------|
| Run 1 vs Run 2 decision mismatches | 0 |
| Run 1 vs Run 2 metrics match | TRUE |
| DETERMINISTIC | **TRUE** ✅ |

同一输入 → 同一输出。实验可完全复现。

---

## 23. Final Gate

| Gate | 条件 | 结果 |
|------|------|------|
| G1 | Independent Evaluation Set Exists | ✅ PASS (69 frozen cases, 4 independent PDFs) |
| G2 | Feature Freeze | ✅ PASS (IS-01/IS-02 frozen, unmodified) |
| G3 | No Leakage | ✅ PASS (provenance audit 9/9 passed) |
| G4 | Semantic GT Validity | ✅ PASS (Level 2 GT, kappa=0.968) |
| G5 | Provenance | ✅ PASS (full provenance chain documented) |
| G6 | Determinism | ✅ PASS (Run 1 = Run 2, 0 mismatches) |
| **G7** | **Precision ≥ 95%** | **❌ FAIL** (Precision = 0.000) |
| **G8** | **Recall ≥ 80%** | **❌ FAIL** (Recall = 0.000) |
| G9 | Cross-Document Generalization | ❌ FAIL (0 TP in any document; all FP in ind_qbio_rna) |
| G10 | Adversarial Robustness | ❌ FAIL (3/3 adversarial FP) |
| G11 | INSUFFICIENT_EVIDENCE Safety | ✅ PASS (abstention correctly prevented 8 additional FP) |
| G12 | Boundary Shrinkage Evidence | ❌ FAIL (0% shrinkage, gates not passed) |

### Gate 总结

```
PASSED:  7/12 (G1, G2, G3, G4, G5, G6, G11)
FAILED:  5/12 (G7, G8, G9, G10, G12)
```

---

## 24. Final Conclusion

### 结论: C. MACHINE-RESOLVABILITY NOT DEMONSTRATED

**理由:**

1. **G7 FAIL**: Precision = 0.000 (远低于 95% 阈值)。所有 3 次 MERGE 决策全部错误。
2. **G8 FAIL**: Recall = 0.000 (远低于 80% 阈值)。零个正确的 MERGE 识别。
3. **G9 FAIL**: 跨文档泛化失败。无任何文档产生 TP。
4. **G10 FAIL**: Adversarial robustness 失败。3/3 adversarial FP。
5. **G12 FAIL**: Boundary shrinkage = 0%。无独立验证的机器可判定性。
6. **目标场景缺失**: 独立评估集中 0 个 TOC_SECTION_NUMBER_TITLE 案例。IS-01+IS-02 的原始设计目标场景未被测试。
7. **高 abstention**: 81.2% 的案例无法做出确定决策。

### 不会声称

- ❌ "Boundary Intelligence 已解决"
- ❌ "IS-01 + IS-02 足以承担 deterministic semantic boundary decision"
- ❌ "所有 PDF 都能解决"
- ❌ "所有 TOC 都能解决"
- ❌ "Human Validation 可以取消"
- ❌ "P4 可以删除"
- ❌ "DICE 已解决 document understanding"

### 只能声称

在当前 frozen feature specification (IS-01 + IS-02)、当前独立 corpus (4 PDFs)、当前 evaluation protocol (§9.3) 下，对被测试 boundary class 获得了 **MACHINE-RESOLVABILITY NOT DEMONSTRATED** 的证据。IS-01+IS-02 在独立评估集上产生了 0% precision、0% recall、81.2% abstention、3 个 false positive (全部来自 TABLE_CELL 场景)。

---

## 25. STOP

```
EXPERIMENT_STATUS = COMPLETE
DATA_INDEPENDENCE = PASS
EVALUATION_FREEZE = INTACT
FEATURE_FREEZE = INTACT
DETERMINISTIC = TRUE

G7 = FAIL
G8 = FAIL

MACHINE_RESOLVABILITY = NOT_DEMONSTRATED
BOUNDARY_SHRINKAGE = NOT_VALIDATED

IMPLEMENTATION = NOT AUTHORIZED
P7.3 = NOT AUTHORIZED
FROZEN BASELINE = INTACT
STOP = TRUE
```

实验完成。不修改规则。不修复 false positive。不进入 P7.3。不注册 capability。不修改 P4。

所有问题转化为: NEXT INFORMATION SOURCE / NEXT EXPERIMENT
