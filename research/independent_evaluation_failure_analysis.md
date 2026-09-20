# Independent Evaluation Failure Analysis & Next Information Source Decision

## READ-ONLY / NO IMPLEMENTATION / NO POST-HOC TUNING

| 字段 | 值 |
|------|-----|
| 分析类型 | Failure Analysis & Next Information Source Decision |
| 分析对象 | Frozen Independent Machine-Resolvability Evaluation Results |
| 约束 | READ-ONLY — 不修改 IS-01/IS-02/P4/任何 frozen 文件 |
| 执行时间 | 2026-09-09 |
| IMPLEMENTATION | NOT AUTHORIZED |
| P7.3 | NOT AUTHORIZED |
| FROZEN BASELINE | INTACT |
| STOP | TRUE |

---

## 1. Executive Summary

本报告对 Independent Machine-Resolvability Evaluation 的结果 (TP=0, FP=3, FN=2, TN=8, ABSTAIN=56) 进行逐 case 失败分析，确定失败根因，并决定下一信息源优先级。

**核心发现:**

1. **TP=0 的首要原因**: Target-Class Absence — 独立评估集中 0 个 TOC_SECTION_NUMBER_TITLE 案例。IS-01+IS-02 的原始设计目标场景未被测试。
2. **3 个 FP 的根因**: Information Source Gap — IS-01+IS-02 能识别"数字+可读词"模式，但缺少 TABLE_CELL_CONTEXT (IS-11) 来区分"TOC 编号+标题"与"表格数字+描述"。
3. **2 个 FN 的根因**: Semantic Irreducibility — 引用片段 ("et"/"al.,") 既非数字也无可读词，需要句子边界解释 (IS-10, Category C)。
4. **56 个 abstention**: 38 个为正确保守 (genuine info gap)，17 个无法确定，0 个过度保守。
5. **IS-01+IS-02 TOC-specific hypothesis**: UNTESTED (非 REFUTED) — 目标场景在独立语料中不存在。
6. **IS-01+IS-02 general boundary decision**: NOT_SUPPORTED — 在非目标场景上已产生结构性 FP。

**最终决策:**
- 下一信息源优先级: IS-11 (TABLE_CELL_CONTEXT) → DESIGN_EXPERIMENT
- IS-10 (SENTENCE_BOUNDARY) → HUMAN_OWNED
- IS-07 (VISUAL_TOC_CONTEXT) → MORE_DATA_NEEDED (需含 TOC 页面的 PDF)

---

## 2. Immutable Baseline

以下数字为不可变基线，本分析不修改任何结果:

| 指标 | 值 |
|------|-----|
| Evaluation Set | 69 (FROZEN) |
| Semantic GT | MERGE=24, KEEP_SEPARATE=45 (FROZEN) |
| Machine MERGE | 3 |
| Machine KEEP_SEPARATE | 10 |
| Machine INSUFFICIENT_EVIDENCE | 56 |
| TP | 0 |
| FP | 3 |
| TN | 8 |
| FN | 2 |
| Precision | 0.000 |
| Recall | 0.000 |
| Coverage | 18.8% |
| Abstention Rate | 81.2% |
| FPR | 27.3% |
| Boundary Shrinkage | 0.0% |

---

## 3. Case-Level Failure Matrix

完整的 69-case 失败矩阵已生成至 `independent_evaluation_failure_matrix.json`。每个 case 记录包含: case_id, document_id, page, text_a, text_b, geometric_metadata, boundary_class, human_gt, human_reason_a/b, is01_a, is02_b, machine_decision, outcome, failure_category, abstention_subtype, information_sufficiency, missing_information, human_info_sources_used, could_additional_info_resolve, confidence, notes。

---

## 4. Outcome Decomposition

| Outcome | Count | % |
|---------|-------|---|
| TRUE_POSITIVE | 0 | 0% |
| FALSE_POSITIVE | 3 | 4.3% |
| TRUE_NEGATIVE | 8 | 11.6% |
| FALSE_NEGATIVE | 2 | 2.9% | 
| ABSTENTION | 56 | 81.2% |
| **Total** | **69** | **100%** |

### 4.1 Correct vs Incorrect Abstention

对 56 个 abstention 逐 case 分析后:

| Abstention Sub-Type | Count | % of Abstain | 说明 |
|---------------------|-------|-------------|------|
| E_INFORMATION_SOURCE_MISSING | 36 | 64.3% | 缺少机器可观测信息源 (正确保守) |
| G_UNKNOWN | 17 | 30.4% | 无法可靠分类 |
| D_OUT_OF_SCOPE | 2 | 3.6% | 非目标类，abstain 正确 |
| C_TARGET_CLASS_MISSING | 1 | 1.8% | 潜在目标类但语料缺失 |

| 分类 | Count | 说明 |
|------|-------|------|
| **Correct Abstention** (genuine info gap) | 38 | 67.9% of abstain |
| **Over-Conservative** (protocol limitation) | 0 | 0% |
| **Unknown** | 17 | 30.4% |

**关键发现**: 0 个过度保守 abstention。INSUFFICIENT_EVIDENCE 机制在所有可判定案例中都正确拒绝——没有案例表明"现有冻结信息源理论上已足够但协议错误地 abstain"。

---

## 5. False Positive Analysis (3 cases)

### 5.1 逐 Case 分析

#### FP-1: IND-AMB-247

| 字段 | 值 |
|------|-----|
| text_a | "121" |
| text_b | "40 mM Hepes" |
| IS-01_a | True (`^\d+(\.\d+)*\.?$` 匹配 "121") |
| IS-02_b | True ("Hepes" = 5 字母 > 2) |
| Machine | MERGE (IS-01=True AND IS-02=True → Step 2) |
| GT | KEEP_SEPARATE |
| Document | ind_qbio_rna, page 35 |
| Boundary Class | TABLE_CELL |

**Q1: 为什么 IS-01 = TRUE?**
"121" 匹配 `^\d+(\.\d+)*\.?$` — 它是一个纯数字，表示 RNA 长度 (121 nucleotides)。

**Q2: 为什么 IS-02 = TRUE?**
"40 mM Hepes" 中 "Hepes" 是 5 个字母的可读词 (> 2)，匹配 IS-02 定义。

**Q3: 为什么这两个 textual signals 在这里不能推出 MERGE?**
"121" 是表格中 RNA 长度列的数值，"40 mM Hepes" 是表格中缓冲液列的描述。它们位于**同一行的不同列**——语义上是独立的数据单元。IS-01 检测到"数字"，IS-02 检测到"可读词"，但它们的组合在 TABLE_CELL 场景下不意味着"编号+标题"关系。

**Q4: Human 做决定时用了哪些额外信息?**
- IS-11 TABLE_CELL_CONTEXT: 识别出这是表格单元格
- IS-12 ROW_COLUMN_POSITION: 识别出两者在不同列 (RNA length 列 vs buffer 列)

**Q5: 这些 signals 是否已存在于 DICE P1-P6 中?**
- P6 region detection: 已有 DENSE/SPARSE region 类型，可识别表格区域
- 但 P4 decision protocol 不使用 P6 region type 作为输入

**Q6: 为什么 decision protocol 没有使用?**
冻结协议 §9.3 仅使用 IS-01(text_a) 和 IS-02(text_b)，不包含 IS-11/IS-12。

**Q7: 缺失的是哪个 information source?**
IS-11 (TABLE_CELL_CONTEXT) + IS-12 (ROW_COLUMN_POSITION)。

**Q8: 属于 INFORMATION SOURCE GAP 还是 DECISION-PROTOCOL GAP?**
**INFORMATION SOURCE GAP** — 缺少 table 结构信息源，而非协议逻辑错误。协议忠实地执行了 IS-01+IS-02 → MERGE 的映射，问题在于输入信息不足。

#### FP-2: IND-AMB-223

| 字段 | 值 |
|------|-----|
| text_a | "5." |
| text_b | "SARS-CoV-2" |
| IS-01_a | True (`^\d+(\.\d+)*\.?$` 匹配 "5.") |
| IS-02_b | True ("SARS" = 4 字母 > 2) |
| Machine | MERGE |
| GT | KEEP_SEPARATE |
| Document | ind_qbio_rna, page 34 |
| Boundary Class | TABLE_CELL |

**分析**: "5." 是表格 case 编号，"SARS-CoV-2" 是样本名称。同样的 Information Source Gap: 缺少 IS-11+IS-12。

#### FP-3: IND-AMB-235

| 字段 | 值 |
|------|-----|
| text_a | "6." |
| text_b | "RNA" |
| IS-01_a | True |
| IS-02_b | True ("RNA" = 3 字母 > 2) |
| Machine | MERGE |
| GT | KEEP_SEPARATE |
| Document | ind_qbio_rna, page 34 |
| Boundary Class | TABLE_CELL |

**分析**: "6." 是表格 case 编号，"RNA" 是样本类型。同样的 Information Source Gap。

### 5.2 FP 共同模式

| 特征 | 3/3 FP 共有 |
|------|-------------|
| Boundary Class | TABLE_CELL (100%) |
| Document | ind_qbio_rna (100%) |
| IS-01 match | 数字/编号 (100%) |
| IS-02 match | 真实可读词 (100%) — 非 loose detection |
| Missing IS | IS-11 + IS-12 (100%) |
| 失败类型 | INFORMATION SOURCE GAP (100%) |

### 5.3 IS-02 Loose Detection 检查

IS-02 loose detection (cos/sin/and/are) **未直接导致任何 FP**。3 个 FP 中的 IS-02 匹配词 ("Hepes", "SARS", "RNA") 均为真实可读词。FP 根因不是 IS-02 的 loose detection，而是缺少 table 结构上下文。

---

## 6. False Negative Analysis (2 cases)

### 6.1 FN-1: IND-AMB-200

| 字段 | 值 |
|------|-----|
| text_a | "et" |
| text_b | "al.," |
| IS-01_a | False ("et" 非数字) |
| IS-02_b | False ("al.," 无 >2 字母词) |
| Machine | KEEP_SEPARATE (IS-01=False AND IS-02=False → Step 3) |
| GT | MERGE |
| Document | ind_qbio_rna, page 32 |
| Boundary Class | REFERENCE_LIST_ENTRY |

**Q1: 为什么 Human 能够判断 MERGE?**
Human 识别出 "et" 和 "al.," 是引用中 "et al.," 的连续片段——它们属于同一个引用作者列表条目。

**Q2: Human 使用了什么信息?**
- IS-10 SENTENCE_BOUNDARY_INTERPRETATION: 理解 "et al.," 是一个完整的引用缩写
- IS-14 DOCUMENT_STRUCTURE_ROLE: 识别出这是参考文献列表中的条目

**Q3: 信息类型?**
E. Semantic interpretation — "et al.," 的含义需要语义理解，非纯模式匹配。

**Q4-Q5: 机器是否有这些信息?**
- IS-10 原始信号 (IS-04 punctuation + IS-05 capital) 机器可观测，但 **interpretation** 是 Category C (semantic)
- IS-14 (document structure role) 不在当前冻结 spec 中

**Q6-Q8: 是否可机器观察?**
IS-10 的 interpretation 是 **inherently semantic** — 属于 Human-owned boundary (Category C)。原始信号可观测，但"et al.,"是一个完整引用缩写这一判断需要语义理解。

### 6.2 FN-2: IND-AMB-201

| 字段 | 值 |
|------|-----|
| text_a | "al.," |
| text_b | "2025)." |
| IS-01_a | False |
| IS-02_b | False |
| Machine | KEEP_SEPARATE |
| GT | MERGE |
| Document | ind_qbio_rna, page 32 |
| Boundary Class | BODY_TEXT_CONTINUATION |

**分析**: "al.," 和 "2025)." 是引用 "(Stagno et al., 2025)." 的连续片段。同样的 Category C 语义解释问题。

### 6.3 FN 共同模式

| 特征 | 2/2 FN 共有 |
|------|-------------|
| IS-01_a | False (非数字) |
| IS-02_b | False (无可读词) |
| Missing IS | IS-10 SENTENCE_BOUNDARY (Category C) |
| 失败类型 | SEMANTIC IRREDUCIBILITY |
| 可机器观察? | 原始信号 YES，interpretation NO |

---

## 7. Abstention Analysis (56 cases)

### 7.1 Abstention 分类

| 类型 | Count | % | 说明 |
|------|-------|---|------|
| E_INFORMATION_SOURCE_MISSING | 36 | 64.3% | 缺少机器可观测信息源 (正确保守) |
| G_UNKNOWN | 17 | 30.4% | 无法可靠分类 |
| D_OUT_OF_SCOPE | 2 | 3.6% | 非目标类 (FIGURE_LABEL) |
| C_TARGET_CLASS_MISSING | 1 | 1.8% | 潜在目标类但语料缺失 |

### 7.2 Correct Abstention Rate

| 分类 | Count | % of Abstain |
|------|-------|-------------|
| Correct Abstention (E + D) | 38 | 67.9% |
| Over-Conservative (F) | 0 | 0% |
| Unknown (G + C) | 18 | 32.1% |

**INSUFFICIENT_EVIDENCE 作为 ERROR CONTAINMENT:**

8 个 IS-01_a=True + IS-02_b=False 的 abstention **全部** GT=KEEP_SEPARATE。如果协议在 IS-01_a=True 时强制 MERGE (不等待 IS-02_b)，将产生 **8 个额外 FP**。INSUFFICIENT_EVIDENCE 机制正确阻止了这些 FP。

**但有代价**: 22 个 GT=MERGE 的案例被 abstain，导致 recall=0%。这些案例大多是引用列表片段和正文续行，需要 IS-10 (Category C) 才能正确判断。

### 7.3 Abstention 按 Boundary Class

| Boundary Class | Abstain | Total | Abstain % | 主要子类型 |
|---------------|---------|-------|-----------|-----------|
| BODY_TEXT_CONTINUATION | 23 | 27 | 85.2% | E_INFO_MISSING (12), G_UNKNOWN (11) |
| REFERENCE_LIST_ENTRY | 15 | 16 | 93.8% | E_INFO_MISSING (15) |
| TABLE_CELL | 8 | 11 | 72.7% | E_INFO_MISSING (8) |
| OTHER_AMBIGUOUS | 7 | 9 | 77.8% | G_UNKNOWN (6) |
| TABLE_CELL_PAIR | 1 | 4 | 25.0% | E_INFO_MISSING (1) |
| FIGURE_LABEL | 2 | 2 | 100% | D_OUT_OF_SCOPE (2) |

### 7.4 Abstention 按 Document

| Document | Abstain | Total | Abstain % |
|----------|---------|-------|-----------|
| ind_arxiv_2402 | 4 | 4 | 100% |
| ind_arxiv_bio2 | 20 | 25 | 80% |
| ind_qbio_genomics | 21 | 23 | 91% |
| ind_qbio_rna | 11 | 17 | 65% |

Abstention 跨文档稳定存在 (65%-100%)，未集中于单一文档。

---

## 8. Target-Class Absence

### 8.1 核心事实

| 维度 | 值 |
|------|-----|
| TOC_SECTION_NUMBER_TITLE in evaluation set | **0** |
| APPENDIX_LETTER_TITLE in evaluation set | **0** |
| 4 independent PDFs 中的 TOC 页面 | **0** |
| 候选宇宙中 IS-01+IS-02 match 的案例 | 13/254 |
| 这 13 个案例的实际类型 | **全部 TABLE_CELL** (非 TOC) |

### 8.2 含义

IS-01+IS-02 的原始设计假设是: "text_a 是编号 (IS-01) + text_b 是可读标题 (IS-02) → MERGE"。这一假设的**目标场景**是 TOC 页面中的 "6.1" + "SMEFT" 类型对。

在独立评估集中:
- 0 个真正的 TOC 页面
- 13 个 IS-01+IS-02 match 的案例全部来自表格 (非 TOC)
- 这 13 个中 3 个被采样，全部成为 FP

### 8.3 正确的表述

**不能说**: "TOC machine-resolvability 被证伪"

**应当说**: "当前独立语料没有提供足够目标类 (TOC_SECTION_NUMBER_TITLE=0)，因此不能评价 TOC-specific recall。但当前 feature combination 在 observed non-target cases 已出现 false-positive behavior (3/3 TABLE_CELL FP)，因此不具备一般 boundary decision sufficiency。"

---

## 9. TABLE_CELL Failure Mode

### 9.1 是否为新 Boundary Class?

**是。** 这是一种 PROVISIONAL FAILURE MODE:

**TEXTUALLY_SIMILAR_BUT_STRUCTURALLY_SEPARATE**

特征:
- text_a 和 text_b 在文本模式上匹配 IS-01+IS-02 (数字 + 可读词)
- 但语义上属于不同结构单元 (不同表格列)
- 几何上 gap 在 AMBIGUOUS 范围内 (8-50pt)
- 缺少 table 结构上下文时无法区分

### 9.2 Candidate Universe 中的频率

| Boundary Class | Universe | Sampled | FP |
|---------------|----------|---------|-----|
| TABLE_CELL | 40 (15.7%) | 11 | 3 (27.3% of sampled) |
| TABLE_CELL_PAIR | 15 (5.9%) | 4 | 0 |
| **Total table-related** | **55 (21.7%)** | **15** | **3** |

TABLE_CELL 在候选宇宙中占 15.7% — **不是偶然现象**。它是一个系统性的 boundary class，在表格密集的生物学论文 (ind_qbio_rna, ind_qbio_genomics) 中普遍存在。

### 9.3 跨文档分布

| Document | TABLE_CELL in Universe |
|----------|----------------------|
| ind_qbio_rna | 34 |
| ind_qbio_genomics | 6 |
| ind_arxiv_bio2 | 0 |
| ind_arxiv_2402 | 0 |

TABLE_CELL 仅存在于 qbio 文档中，arxiv 论文中不存在。这反映了文档类型差异: 生物学论文包含大量数据表格，而 arxiv 计算机科学论文以正文和引用为主。

---

## 10. Human Information Source Matrix

### 10.1 IS-01~IS-14 使用频率

| IS | 名称 | 类别 | Human 使用 | Machine 有? | 频率 |
|----|------|------|-----------|------------|------|
| IS-11 | TABLE_CELL_CONTEXT | PROPOSED | ✅ | ❌ | 37/69 (53.6%) |
| IS-12 | ROW_COLUMN_POSITION | PROPOSED | ✅ | ❌ | 36/69 (52.2%) |
| IS-02 | TEXT_READABLE_TITLE | FROZEN | ✅ | ✅ | 29/69 (42.0%) |
| IS-09 | VISUAL_BODY_CONTEXT | FROZEN | ✅ | ❌ (in P6, not in protocol) | 27/69 (39.1%) |
| IS-14 | DOCUMENT_STRUCTURE_ROLE | PROPOSED | ✅ | ❌ | 26/69 (37.7%) |
| IS-10 | SENTENCE_BOUNDARY | Category C | ✅ | ❌ | 23/69 (33.3%) |
| IS-13 | HEADER_RELATION | PROPOSED | ✅ | ❌ | 16/69 (23.2%) |
| IS-05 | TEXT_CAPITAL_START | FROZEN | ✅ | ❌ (in spec, not in protocol) | 16/69 (23.2%) |
| IS-04 | TEXT_PUNCTUATION | FROZEN | ✅ | ❌ (in spec, not in protocol) | 12/69 (17.4%) |
| IS-03 | TEXT_SYMBOL_PATTERN | FROZEN | ✅ | ❌ | 6/69 (8.7%) |
| IS-01 | TEXT_NUMBER_PATTERN | FROZEN | ✅ | ✅ | 2/69 (2.9%) |

### 10.2 关键洞察

**Human 最常使用的信息源 (IS-11, IS-12) 恰好是 machine 完全没有的。** 53.6% 的人工决策依赖 table 结构上下文，而冻结协议仅使用 IS-01 (2.9% match) 和 IS-02 (42.0% match)。

这意味着: 即使将冻结 spec 中所有已定义但未使用的 IS (IS-03~IS-09) 全部加入协议，仍无法覆盖 IS-11/IS-12 的信息缺口——因为这些信息源尚未定义。

---

## 11. Information Sufficiency Analysis

### 11.1 总体统计

| Sufficiency | Count | % |
|-------------|-------|---|
| SUFFICIENT | 8 | 11.6% |
| PARTIALLY_SUFFICIENT | 40 | 58.0% |
| INSUFFICIENT | 21 | 30.4% |
| UNKNOWN | 0 | 0% |

### 11.2 解读

- **SUFFICIENT (8)**: 8 个 TN — 机器有足够信息做出正确 KEEP_SEPARATE
- **PARTIALLY_SUFFICIENT (40)**: 机器有部分信息但缺少关键信息源 — 包括 3 FP + 2 FN + 35 abstention
- **INSUFFICIENT (21)**: 需要 Category C 语义解释 — 全部是引用片段和正文续行

### 11.3 Missing Information Sources

| Missing IS | Count | Machine-Observable? |
|-----------|-------|-------------------|
| IS-11 TABLE_CELL_CONTEXT | 28 | YES (P6 region) |
| IS-12 ROW_COLUMN_POSITION | 28 | YES (geometry) |
| IS-10 SENTENCE_BOUNDARY | 23 | NO (Category C) |
| IS-14 DOCUMENT_STRUCTURE_ROLE | 13 | PARTIALLY |
| IS-13 HEADER_RELATION | 13 | PARTIALLY |
| IS-09 VISUAL_BODY_CONTEXT | 1 | YES (P6 region) |
| IS-05 TEXT_CAPITAL_START | 1 | YES |

---

## 12. Document-Level Analysis

| Document | Total | GT_M | GT_KS | TP | FP | TN | FN | ABSTAIN | Correct Abstain | Unknown Abstain |
|----------|-------|------|-------|----|----|----|----|---------|----------------|----------------|
| ind_arxiv_2402 | 4 | 2 | 2 | 0 | 0 | 0 | 0 | 4 | 4 | 0 |
| ind_arxiv_bio2 | 25 | 7 | 18 | 0 | 0 | 5 | 0 | 20 | 11 | 9 |
| ind_qbio_genomics | 23 | 9 | 14 | 0 | 0 | 2 | 0 | 21 | 14 | 7 |
| ind_qbio_rna | 17 | 6 | 11 | 0 | 3 | 1 | 2 | 11 | 9 | 2 |

### 12.1 文档级发现

1. **ind_arxiv_2402** (4 cases, LOW_SAMPLE): 全部 abstain，无法得出有意义结论。
2. **ind_arxiv_bio2** (25 cases): 5 个 TN，0 个错误决策。20 个 abstain 中 11 个正确保守。
3. **ind_qbio_genomics** (23 cases): 2 个 TN，0 个错误决策。21 个 abstain 中 14 个正确保守。
4. **ind_qbio_rna** (17 cases): **唯一产生 FP 和 FN 的文档**。3 FP + 2 FN 全部来自此文档的 TABLE_CELL 和引用片段。

**ind_qbio_rna 是失败集中点**: 它包含表格 (TABLE_CELL) 和引用列表 (REFERENCE_LIST_ENTRY) 两种 boundary class，前者导致 FP，后者导致 FN。

---

## 13. Boundary-Class Analysis

| Boundary Class | Total | TP | FP | TN | FN | ABSTAIN | Correct Abstain | Failure Type |
|---------------|-------|----|----|----|----|---------|----------------|-------------|
| BODY_TEXT_CONTINUATION | 27 | 0 | 0 | 3 | 1 | 23 | 12 | IS-10 (semantic) |
| REFERENCE_LIST_ENTRY | 16 | 0 | 0 | 0 | 1 | 15 | 15 | IS-10 + IS-14 |
| TABLE_CELL | 11 | 0 | 3 | 0 | 0 | 8 | 8 | IS-11 + IS-12 |
| OTHER_AMBIGUOUS | 9 | 0 | 0 | 2 | 0 | 7 | 0 | UNKNOWN |
| TABLE_CELL_PAIR | 4 | 0 | 0 | 3 | 0 | 1 | 1 | IS-11 |
| FIGURE_LABEL | 2 | 0 | 0 | 0 | 0 | 2 | 2 | OUT_OF_SCOPE |
| **TOC_SECTION_NUMBER_TITLE** | **0** | — | — | — | — | — | — | **UNTESTED** |
| **APPENDIX_LETTER_TITLE** | **0** | — | — | — | — | — | — | **UNTESTED** |

### 13.1 POST-HOC ANALYTIC CATEGORY 标记

以下 boundary class 是事后观察得到的分析类别 (非 pre-registered):
- TABLE_CELL (POST-HOC)
- TABLE_CELL_PAIR (POST-HOC)
- REFERENCE_LIST_ENTRY (POST-HOC)
- BODY_TEXT_CONTINUATION (POST-HOC)
- FIGURE_LABEL (POST-HOC)
- OTHER_AMBIGUOUS (POST-HOC)

Pre-registered 类别 (来自原始实验设计):
- TOC_SECTION_NUMBER_TITLE (0 cases in independent set)
- APPENDIX_LETTER_TITLE (0 cases in independent set)
- FORMULA_FRAGMENT_WIDE (0 cases — 4 PDFs 无公式密集页)

---

## 14. Hypothesis Status

### 14.1 TOC-Specific Hypothesis

**Hypothesis**: "IS-01 (TEXT_NUMBER_PATTERN) + IS-02 (TEXT_READABLE_TITLE) 可以在 TOC 页面上对 TOC_SECTION_NUMBER_TITLE boundary cases 做出正确的 MERGE 决策。"

**Status: UNTESTED**

理由:
- 独立评估集中 0 个 TOC_SECTION_NUMBER_TITLE 案例
- 4 个独立 PDF 中 0 个 TOC 页面
- 无法评价 TOC-specific recall
- 历史 counterfactual (29/43=67.4%) 仅在 TRAIN=TEST 数据上成立

**不能说 REFUTED** — 目标场景未被测试。也不能说 SUPPORTED — 无独立证据。

### 14.2 General Semantic Boundary Decision Hypothesis

**Hypothesis**: "IS-01 + IS-02 足以承担 general deterministic semantic boundary decision。"

**Status: NOT_SUPPORTED**

理由:
- 3 个 FP 证明 IS-01+IS-02 在 TABLE_CELL 场景下产生结构性 false positive
- 0 TP 证明在非目标场景上无正确 MERGE 能力
- 81.2% abstention 证明覆盖范围极低
- 2 个 FN 证明在引用片段场景下无法识别 MERGE

### 14.3 区分总结

| Hypothesis | Status | 证据 |
|-----------|--------|------|
| TOC-specific (IS-01+IS-02 on TOC pages) | **UNTESTED** | 0 target cases in independent set |
| General boundary decision (IS-01+IS-02 on all AMBIGUOUS) | **NOT_SUPPORTED** | 3 FP, 0 TP, 81.2% abstain |

---

## 15. Re-analysis of 0% Precision / 0% Recall

### 15.1 Precision = 0

**原因: C. Feature combination creates structural false positives**

IS-01+IS-02 的组合在 TABLE_CELL 场景下产生了结构性 FP: 数字 + 可读词的模式在表格中普遍存在 (13/254 universe = 5.1%)，但语义上它们不属于同一文本单元。

这不是"decision rule invalid" (规则逻辑正确执行了 IS-01+IS-02 → MERGE 的映射)，也不是"evaluation target class absent" (虽然 TOC 确实缺失，但 FP 发生在非目标场景上)。

### 15.2 Recall = 0

**原因: D. Evaluation corpus contains target classes not covered by feature hypothesis**

24 个 GT=MERGE 案例中:
- 0 个被正确识别 (TP=0)
- 2 个被错误判为 KEEP_SEPARATE (FN)
- 22 个被 abstain

这 24 个 MERGE 案例主要是引用列表片段和正文续行——这些 boundary class 不在 IS-01+IS-02 的设计目标内。IS-01+IS-02 是为 TOC 编号+标题设计的，对引用片段 ("et"/"al.,") 和正文续行天然无法覆盖。

---

## 16. Evidence Boundary Intelligence 核心假设检验

**假设**: "Boundary decision quality depends on evidence sufficiency, not simply feature matching."

**数据支持: YES**

证据:
1. **0 TP + 3 FP**: IS-01+IS-02 的 feature matching 在信息不足时产生错误决策 (FP) 而非正确决策 (TP)
2. **56 abstention**: 当信息不足时，INSUFFICIENT_EVIDENCE 机制正确拒绝决策 (38/56 = 67.9% 正确保守)
3. **8 个 IS-01_a=True + IS-02_b=False abstain 全部 GT=KEEP_SEPARATE**: 如果仅凭 IS-01 做 MERGE，将产生 8 个额外 FP——evidence sufficiency 的判断 (IS-02_b=False → 混合信号 → abstain) 正确阻止了这些 FP
4. **Human 使用 IS-11/IS-12 (53.6%) 而 machine 没有**: 信息源差异直接导致决策质量差异

**结论**: 数据支持"boundary decision quality depends on evidence sufficiency"的假设。IS-01+IS-02 的失败不是因为 feature matching 本身错误，而是因为 evidence insufficient (缺少 IS-11/IS-12/IS-10 等关键信息源)。

---

## 17. Information Source Priority

### 17.1 Priority Matrix

| Rank | IS | Action | Reason |
|------|-----|--------|--------|
| 1 | IS-11 TABLE_CELL_CONTEXT | DESIGN_EXPERIMENT | 45.9% failure coverage, machine-observable, low semantic risk |
| 2 | IS-12 ROW_COLUMN_POSITION | DESIGN_EXPERIMENT | Co-occurs with IS-11, test together |
| 3 | IS-10 SENTENCE_BOUNDARY | HUMAN_OWNED | Category C semantic, not implementable as deterministic rule |
| 4 | IS-14 DOCUMENT_STRUCTURE_ROLE | DEFER | Medium coverage, partially semantic |
| 5 | IS-13 HEADER_RELATION | DEFER | Sub-component of IS-11 |
| N/A | IS-07 VISUAL_TOC_CONTEXT | MORE_DATA_NEEDED | Target class absent, need TOC-containing PDFs |

### 17.2 Do Not Build Yet 判断

| IS | Build Now? | 理由 |
|----|-----------|------|
| IS-11 | ❌ NO | 3/69 FP 样本太少；universe 中 40 个 TABLE_CELL 但仅 11 个被采样；需要 targeted data collection 达到 ≥30 个 TABLE_CELL 案例才能有效评估 |
| IS-12 | ❌ NO | 同 IS-11 |
| IS-10 | ❌ NEVER | Category C — inherently semantic，不可作为 deterministic rule 实现 |
| IS-14 | ❌ DEFER | 需先完成 IS-11 实验再评估 |
| IS-13 | ❌ DEFER | IS-11 子组件 |

---

## 18. Next Experiment

### 18.1 实验名称

**Table Structural Context Information Source Experiment**

### 18.2 Research Question

在冻结的 IS-01/IS-02 基础上增加 IS-11 (TABLE_CELL_CONTEXT) + IS-12 (ROW_COLUMN_POSITION)，是否能使 TABLE_CELL boundary cases 获得正确的 KEEP_SEPARATE 决策？

### 18.3 设计参数

| 参数 | 值 |
|------|-----|
| Information Source | IS-11 + IS-12 (PROPOSED) |
| Independent Data | 需要新的含表格 PDF (当前 4 PDF 有 40 TABLE_CELL，但仅 11 sampled) |
| Ground Truth | Level 2 Semantic GT (双审查者 + 裁定, blind protocol) |
| Blind Protocol | 审查者仅看 text_a, text_b, page_context |
| Success Criteria | Precision ≥ 95% AND Recall ≥ 80% on TABLE_CELL subset (pre-registered) |
| Failure Criteria | TABLE_CELL 上任何 FP → IS-11 不足以独立解决 |
| Contamination Prevention | 新 PDF 必须独立; IS-11 定义在评估前冻结; GT 在 machine evaluation 前收集 |
| Sample Requirements | ≥30 TABLE_CELL cases |

### 18.4 状态

**DESIGN ONLY — NOT AUTHORIZED for execution**

---

## 19. Limitations

| # | 限制 | 影响 |
|---|------|------|
| L1 | 17/56 abstention 无法可靠分类 (G_UNKNOWN) | 分类可能不完全准确 |
| L2 | Human IS 使用频率基于 reason 文本分析 | 可能遗漏未显式提及的信息源 |
| L3 | TABLE_CELL 分析仅基于 11 个采样案例 (3 FP) | 样本量不足以做统计推断 |
| L4 | IS-11/IS-12 为 PROPOSED，未经验证 | 机器可观测性为理论推断 |
| L5 | 0 个 TOC 页面 | TOC-specific hypothesis 无法测试 |
| L6 | 仅 4 个独立 PDF | 文档类型覆盖有限 |

---

## 20. Final Decision

### 20.1 12 个必须回答的问题

**Q1: 为什么 TP = 0?**
Target-Class Absence — 独立评估集中 0 个 TOC_SECTION_NUMBER_TITLE 案例。IS-01+IS-02 的设计目标场景 (TOC 编号+标题) 在独立语料中不存在。24 个 GT=MERGE 案例全部是非目标类 (引用片段/正文续行)，IS-01+IS-02 天然无法覆盖。

**Q2: 为什么 3 个 FP 全部发生在 TABLE_CELL?**
IS-01+IS-02 的"数字+可读词"模式在 TABLE_CELL 场景下产生结构性 FP。表格中的数值和描述性文本恰好匹配 IS-01 (数字) 和 IS-02 (可读词)，但语义上属于不同列。缺少 IS-11 (TABLE_CELL_CONTEXT) 来区分。

**Q3: 为什么 FN / unresolved MERGE 没有被识别?**
2 个 FN 是引用片段 ("et"/"al.,")，既非数字也无可读词，IS-01+IS-02 均返回 False。22 个 abstained MERGE 需要句子边界解释 (IS-10, Category C)，属于 inherently semantic。

**Q4: 56 个 abstention 中有多少是正确保守?**
38/56 = 67.9% 正确保守 (E_INFORMATION_SOURCE_MISSING=36 + D_OUT_OF_SCOPE=2)。

**Q5: 有多少是过度保守?**
0/56 = 0% 过度保守。没有案例表明"现有冻结信息源理论上已足够但协议错误地 abstain"。

**Q6: TOC hypothesis 到底是 SUPPORTED / UNTESTED / REFUTED?**
**UNTESTED** — 目标场景 (TOC_SECTION_NUMBER_TITLE) 在独立评估集中为 0。不能说 REFUTED (未被测试)，也不能说 SUPPORTED (无独立证据)。

**Q7: IS-01 + IS-02 的真正失败原因是什么?**
Information Source Insufficiency — IS-01+IS-02 是为 TOC 编号+标题设计的 narrow feature combination，缺少 (a) table 结构上下文 (IS-11) 来避免 TABLE_CELL FP，(b) 句子边界解释 (IS-10) 来识别引用片段 MERGE。

**Q8: 问题是 Feature insufficiency 还是 Decision protocol limitation?**
**Feature insufficiency** (primary) — 缺少 IS-11/IS-12/IS-10 等关键信息源。Protocol limitation (secondary) — 即使有 IS-03~IS-09 (已定义但未使用)，当前 §9.3 协议也不使用它们。

**Q9: Human 比 machine 多看到了什么信息?**
- IS-11 TABLE_CELL_CONTEXT (53.6%) — table 结构角色
- IS-12 ROW_COLUMN_POSITION (52.2%) — 行列位置
- IS-10 SENTENCE_BOUNDARY (33.3%) — 句子边界解释
- IS-14 DOCUMENT_STRUCTURE_ROLE (37.7%) — 文档结构角色

**Q10: 这些信息中哪些是 machine-observable?**
- IS-11: YES (P6 region detection 可识别表格区域)
- IS-12: YES (x/y 坐标聚类可识别行列)
- IS-10: NO (Category C — inherently semantic)
- IS-14: PARTIALLY (reference list 可通过 [N] 模式检测，但 role assignment 需要上下文)

**Q11: 最值得验证的下一 information source 是什么?**
IS-11 (TABLE_CELL_CONTEXT) — 45.9% failure coverage，machine-observable，low semantic risk。但需要 targeted data collection (≥30 TABLE_CELL cases) 才能 design experiment。

**Q12: 下一步应该 BUILD / DESIGN EXPERIMENT / MORE DATA / HUMAN-OWNED / STOP?**
- IS-11+IS-12: **DESIGN_EXPERIMENT** (需要 more data first)
- IS-10: **HUMAN_OWNED** (Category C)
- IS-07 (TOC): **MORE_DATA_NEEDED** (需要含 TOC 页面的 PDF)
- 整体: **STOP** — 当前分析完成，不进入实现

### 20.2 最终状态

```
FAILURE_ANALYSIS_STATUS = COMPLETE
NEXT_INFORMATION_SOURCE = IS-11 TABLE_CELL_CONTEXT (Priority 1)
NEXT_ACTION = DESIGN_EXPERIMENT (not BUILD)
IS-10_SENTENCE_BOUNDARY = HUMAN_OWNED
IS-07_TOC_CONTEXT = MORE_DATA_NEEDED

IMPLEMENTATION = NOT AUTHORIZED
P7.3 = NOT AUTHORIZED
P4 = FROZEN
P7.1 = FROZEN
P7.2 = FROZEN
IS-01 = FROZEN
IS-02 = FROZEN
Evaluation Set = FROZEN
Semantic GT = FROZEN
Historical Results = IMMUTABLE
FROZEN BASELINE = INTACT
STOP = TRUE
```

---

## STOP

本分析完成。不修改规则。不修改实验。不修复 FP。不进入 P7.3。

所有发现转化为: NEXT INFORMATION SOURCE / NEXT EXPERIMENT (DESIGN ONLY)。
