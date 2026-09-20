# DICE 2.0 Boundary Intelligence: 从认知障碍到独立机器评估

## 完整研究脉络记录（论文用）

> 本文档记录了从 Human Annotation 导致的认知障碍问题出发，经过一系列修改、实验、数据对比，最终完成 Independent Machine-Resolvability Evaluation 的完整研究链。所有数据均为实际执行结果，未做任何事后修改。

---

## 目录

1. [研究起点：Human Annotation 认知障碍](#1-研究起点human-annotation-认知障碍)
2. [Cross-Document Text-Unit Relation Audit](#2-cross-document-text-unit-relation-audit)
3. [P4 v3 Span Design](#3-p4-v3-span-design)
4. [Evidence Boundary Decision Design](#4-evidence-boundary-decision-design)
5. [Human-on-the-Boundary Empirical Validation (Round 1)](#5-human-on-the-boundary-empirical-validation-round-1)
6. [Round 1 Integrity Audit: 发现认知障碍](#6-round-1-integrity-audit-发现认知障碍)
7. [Boundary Semantics Convergence](#7-boundary-semantics-convergence)
8. [Information Source Gap Analysis (IS-01~IS-10)](#8-information-source-gap-analysis-is-01is-10)
9. [TOC Feasibility Study (Counterfactual)](#9-toc-feasibility-study-counterfactual)
10. [Independent Machine-Resolvability Experiment Design](#10-independent-machine-resolvability-experiment-design)
11. [Independent Evaluation Data Collection](#11-independent-evaluation-data-collection)
12. [Independent Machine-Resolvability Evaluation (最终实验)](#12-independent-machine-resolvability-evaluation-最终实验)
13. [完整数据对比表](#13-完整数据对比表)
14. [研究脉络图](#14-研究脉络图)

---

## 1. 研究起点：Human Annotation 认知障碍

### 1.1 问题背景

DICE 2.0 Perception Pipeline (P1-P6) 在处理 PDF 文档时，P4 Span 阶段将文本单元合并为 span。但存在一类 **AMBIGUOUS** 状态的文本对——它们的几何特征（gap、y 偏移、样式）不足以确定是否应合并，需要人工判断。

为验证 P4 的 AMBIGUOUS 处理是否合理，设计了 Human Boundary Review 实验，让人工审查者对 20 个 AMBIGUOUS 案例做出 MERGE / KEEP_SEPARATE 判断。

### 1.2 认知障碍的具体表现

#### 障碍一：Timer Bug 导致 Human Cost 无法测量

Human Boundary Review 的 Web 界面 (`boundary_review.html`) 中，`submitDecision()` 函数在调用 `/api/submit` 提交决策之前，先调用了 `/api/case` 预取下一个案例。这个预取调用重置了 `start_time_ms`，导致所有记录的 `duration_ms` 值仅为 1-6ms（网络往返时间），而非人类的思考时间。

| 指标 | 原始记录值 | 实际含义 |
|------|-----------|---------|
| duration_ms | 1-6ms | 网络往返时间 |
| 中位 inter-decision gap | 5492ms (5.5s) | 导航+思考+提交的混合时间 |
| P75 inter-decision gap | 28601ms (28.6s) | 同上 |
| P95 inter-decision gap | 51003ms (51.0s) | 同上 |
| 总会话时间 | 307.1s (5.1min) | 包含所有操作 |
| 平均每案例 | 15.4s | 混合时间 |

**影响**: Human Cost 无法被准确测量。这是方法学上的严重缺陷——无法回答"人工判断需要多少时间"这一基本问题。

#### 障碍二：Geometry GT ≠ Semantic GT (AMB-026)

Round 1 的 20 个案例中，AMB-026 暴露了一个根本性的认知冲突：

| 维度 | 值 |
|------|-----|
| Case ID | AMB-026 |
| 文档 | arxiv_bio_body |
| text_a | "transition form factor of primary interest to us." |
| text_b | "Its normalization is" |
| Geometry GT (extract_ambiguous.py) | SHOULD_MERGE (w_a≥25 AND w_b≥25 AND len≥10) |
| Human semantic judgment | KEEP_SEPARATE (不同句子) |
| 误差类型 | 人工判断与几何 GT 不一致 |

**这意味着**: 以几何规则生成的 Ground Truth（GT-GEOMETRIC）在 body text 场景下与人类语义判断不一致。如果使用 GT-GEOMETRIC 作为评估标准，人工判断的"准确率"会被错误地记为 95%（19/20），而实际上 AMB-026 的人工判断在语义上是正确的。

#### 障碍三：单审查者，无 Inter-Rater Agreement

Round 1 仅有 reviewer_1 一人参与，无法测量审查者间一致性。无法确认判断结果是否可复现。

### 1.3 认知障碍的方法学影响

这三个障碍共同导致：
1. **Human Cost 无法量化** → 无法评估"人工边界判断"的实际成本
2. **GT 有效性存疑** → 几何 GT 不能作为语义评估的标准
3. **结果不可泛化** → 单审查者 + 同文档族 = 无法验证跨文档一致性

这些障碍不是"实现 bug"可以简单修复的——它们指向了一个更深的问题：**如何科学地验证 boundary 决策的正确性？**

---

## 2. Cross-Document Text-Unit Relation Audit

### 2.1 目的

在认知障碍发现后，首先需要全面了解 P4 AMBIGUOUS 问题在跨文档层面的分布和特征。

### 2.2 审计范围

| 维度 | 值 |
|------|-----|
| 文档数 | 8 (3 arxiv + 5 device manuals) |
| 总 boundary pairs | 2255 |
| P4 merged pairs | 1844 |
| same-y 未合并对 | 411 |
| AMBIGUOUS cases | 43 |
| AMBIGUOUS 占总对数 | 43/2255 = 1.9% |
| AMBIGUOUS 占未合并 | 43/411 = 10.5% |

### 2.3 跨文档分布

| 文档族 | 文档数 | same-y 未合并 | AMBIGUOUS | 特征 |
|--------|--------|-------------|-----------|------|
| arxiv (已处理) | 3 | 408 | 43 | TOC 编号、公式碎片、正文续行 |
| device manuals | 5 | 3 | 0 | 完全无 AMBIGUOUS 问题 |

**关键发现**: 设备手册（RA101/RM501/E804/C216/DC201）完全没有 same-y 未合并问题。AMBIGUOUS 仅存在于学术论文（arxiv）文档中。

### 2.4 AMBIGUOUS 模式分布

| 模式 | 数量 | 占比 |
|------|------|------|
| TOC_SECTION_NUMBER_TITLE | 27 | 62.8% |
| FORMULA_FRAGMENT_WIDE | 13 | 30.2% |
| BODY_TEXT_CONTINUATION | 1 | 2.3% |
| APPENDIX_LETTER_TITLE | 2 | 4.7% |

---

## 3. P4 v3 Span Design

### 3.1 冻结的 SpanConfig

在审计基础上，P4 Span 阶段的配置被冻结为 v3：

| 参数 | 值 | 说明 |
|------|-----|------|
| max_horizontal_gap | 8.0pt | 同行最大水平间距 |
| max_vertical_gap | 14.0pt | 跨行最大垂直间距 |
| same_line_tolerance | 3.0pt | 同行判定容差 |
| cross_column_gap_threshold | 30.0pt | 跨栏间距阈值 |
| overlap_tolerance | 0.5pt | 重叠容差 |

### 3.2 三态关系模型

P4 v3 引入了三态决策模型，取代了原来的二态（merge/block）：

| 状态 | 条件 | 含义 |
|------|------|------|
| DETERMINISTIC_MERGE | gap≤8, same_y, same_style | 几何确定合并 |
| DETERMINISTIC_BLOCK | gap>50 OR different_style OR line_obs>15 OR w_b<15 | 几何确定分离 |
| AMBIGUOUS | 8<gap≤50, same_style, line_obs≤15, w_b≥15 | 几何不足，需语义判断 |

**核心改进**: AMBIGUOUS 状态承认了几何信息的不足，将"无法确定"作为正式输出，而非强行二选一。

---

## 4. Evidence Boundary Decision Design

### 4.1 设计目标

定义"什么是一个文本单元"的语义标准，以及如何在 evidence 不足时安全地拒绝决策。

### 4.2 核心概念

- **Evidence Boundary**: 系统在证据不足时必须拒绝强判，输出 INSUFFICIENT_EVIDENCE
- **决策输出**: MERGE / KEEP_SEPARATE / INSUFFICIENT_EVIDENCE
- **DICE 核心原则**: "Evidence insufficient → 不做强结论"

---

## 5. Human-on-the-Boundary Empirical Validation (Round 1)

### 5.1 实验设计

| 维度 | 值 |
|------|-----|
| 案例池 | 43 AMBIGUOUS cases |
| 选取 | 20 cases (分层随机) |
| 审查者 | reviewer_1 (单人) |
| 包含 adversarial | AMB-018 (TOC编号+标题), AMB-040 (公式碎片) |
| 展示方式 | Web 界面 (boundary_review.html) |

### 5.2 实验结果

| 指标 | 值 |
|------|-----|
| 完成率 | 20/20 = 100% |
| MERGE 决策 | 13 |
| KEEP_SEPARATE 决策 | 7 |
| CANNOT_DETERMINE | 0 |
| 对 Geometry GT 准确率 | 19/20 = 95.0% |
| 误差案例 | AMB-026 (Body text continuation) |

### 5.3 Adversarial Cases 结果

| Case | text_a → text_b | 人工决策 | GT | 正确? |
|------|----------------|---------|-----|------|
| AMB-018 | "6.1" → "SMEFT" | MERGE | SHOULD_MERGE | ✅ |
| AMB-040 | "( )" → "cos(" | KEEP_SEPARATE | SHOULD_NOT_MERGE | ✅ |

### 5.4 信息源分析发现

通过分析 reviewer_1 在 20 个案例上使用的判断依据，发现了两个关键的 machine-observable 信息源：

- **IS-01 (TEXT_NUMBER_PATTERN)**: text_a 匹配编号模式 → 支持 MERGE 方向
- **IS-02 (TEXT_READABLE_TITLE)**: text_b 包含可读字母词 → 支持 MERGE 方向

---

## 6. Round 1 Integrity Audit: 发现认知障碍

### 6.1 审计发现

| 维度 | 状态 | 说明 |
|------|------|------|
| 案例记录 | PASS | 20/20 唯一，全部来自原始 43 池 |
| 决策记录 | PASS | 全部有效决策，无重复/覆盖 |
| Duration 测量 | **INVALID** | start_time_ms 被 /api/case 预取重置 |
| Ground Truth 完整性 | **DISPUTED** | AMB-026 GT 基于几何，人工判断语义正确 |

### 6.2 AMB-026 深度分析

| 视角 | 判断 | 依据 |
|------|------|------|
| Geometry GT (extract_ambiguous.py) | SHOULD_MERGE | w_a≥25 AND w_b≥25 AND len≥10 |
| Human semantic judgment | KEEP_SEPARATE | 两个不同句子，句号分隔 |
| 结论 | GT-GEOMETRIC ≠ GT-SEMANTIC | 几何规则在 body text 场景失效 |

### 6.3 排除 AMB-026 后的准确率

| 口径 | 准确率 |
|------|--------|
| 对 Geometry GT (含 AMB-026) | 19/20 = 95.0% |
| 排除 AMB-026 ( disputed) | 19/19 = 100.0% |
| 语义假设 (非官方) | 20/20 = 100.0% (HYPOTHETICAL) |

### 6.4 审计结论

```
overall = EMPIRICALLY_SUPPORTED
  - Human feasibility: SUPPORTED (adversarial resolved)
  - Human cost: INVALID (timer broken)
  - GT validity: DISPUTED (geometry ≠ semantic)
  - Inter-reviewer: NOT MEASURED (single reviewer)
```

---

## 7. Boundary Semantics Convergence

### 7.1 语义 GT 层级定义

为解决"GT 有效性存疑"问题，定义了四级 GT 层级：

| 层级 | 名称 | 定义 | 可靠性 |
|------|------|------|--------|
| Level 0 | Geometry GT | 基于 P4 几何特征的派生标签 | 不足 (AMB-026 证明) |
| Level 1 | Single Reviewer GT | 单审查者语义判断 | 中等 |
| Level 2 | Dual Reviewer + Adjudication | 双审查者一致或裁定 | 高 |
| Level 3 | Expert Annotation | 领域专家标注 | 最高 |

**正式评估要求 Level 2 及以上。**

### 7.2 Boundary Shrinkage 四级定义

| 级别 | 名称 | 定义 |
|------|------|------|
| Level 1 | Baseline Ambiguity | 评估集中需要 Human 的数量 |
| Level 2 | Potential Machine-Resolvable | 冻结 feature evidence 显示可能可判定 |
| Level 3 | Actual Machine-Resolvable | 机器实际给出确定 decision |
| Level 4 | Independently Validated | 机器 decision 被独立 GT 验证且 Gate 通过 |

```
Actual Boundary Shrinkage Rate = Level 4 / Level 1
```

**只有 Level 4 / Level 1 才能称为 ACTUAL BOUNDARY SHRINKAGE。**

---

## 8. Information Source Gap Analysis (IS-01~IS-10)

### 8.1 信息源分类体系

将人类在 boundary 判断中可能使用的信息源分为三类：

| 类别 | 名称 | 性质 | 机器可观测? |
|------|------|------|-----------|
| A | Existing Uncombined | 已有但未组合的特征 | ✅ |
| B | New Machine-Observable | 新的机器可观测特征 | ✅ |
| C | Inherently Semantic | 本质语义特征 | ❌ |

### 8.2 IS-01~IS-10 完整分类

| IS | 名称 | 定义 | 类别 |
|----|------|------|------|
| IS-01 | TEXT_NUMBER_PATTERN | text_a 匹配编号模式 (1, 2.1, B.1) | B |
| IS-02 | TEXT_READABLE_TITLE | text_b 包含可读字母词 (length > 2) | B |
| IS-03 | TEXT_SYMBOL_PATTERN | text 为非字母或极短 (数学符号) | B |
| IS-04 | TEXT_PUNCTUATION | text_a 以句号结尾 (句子边界信号) | B |
| IS-05 | TEXT_CAPITAL_START | text_b 大写开头 (句子开始信号) | B |
| IS-06 | TEXT_APPENDIX_LETTER | text_a 匹配附录字母模式 (B.1, A.2) | B |
| IS-07 | VISUAL_TOC_CONTEXT | 页面为 TOC 页 | B |
| IS-08 | VISUAL_FORMULA_CONTEXT | 页面为公式密集页 | B |
| IS-09 | VISUAL_BODY_CONTEXT | 页面为正文页 | B |
| IS-10 | SENTENCE_BOUNDARY_INTERPRETATION | 标点+大小写 → 句子边界 → 不同文本单元 | **C** |

### 8.3 冻结的 IS-01 / IS-02 定义

从 Round 1 的 20 个审查案例中发现并冻结：

**IS-01 (TEXT_NUMBER_PATTERN) FROZEN:**
```python
re.match(r'^\d+(\.\d+)*\.?$', text.strip()) OR re.match(r'^[A-Z]\.\d+$', text.strip())
```
- 已知限制: 不区分 heading number 与 equation number

**IS-02 (TEXT_READABLE_TITLE) FROZEN:**
```python
any(len(re.sub(r'[^a-zA-Z]', '', w)) > 2 for w in text.split())
```
- 已知限制: "cos"/"sin"/"and"/"are" 匹配 (3 chars > 2)

---

## 9. TOC Feasibility Study (Counterfactual)

### 9.1 反事实分析

在全 43 个 AMBIGUOUS 案例上，使用冻结的 IS-01/IS-02 进行反事实分类：

| 分类 | 数量 | 占比 | 模式 |
|------|------|------|------|
| CF-A (POTENTIALLY_MACHINE_RESOLVABLE) | 29 | 67.4% | TOC_NUM_TITLE (27) + APPENDIX (2) |
| CF-B (STILL_AMBIGUOUS) | 14 | 32.6% | FORMULA (13) + BODY_CONT (1) |
| CF-C (INSUFFICIENT_SOURCE) | 0 | 0.0% | none |

### 9.2 FP 分析

在全 corpus (2255 pairs) 上测试 IS-01+IS-02 的 false positive rate:

| 指标 | 值 |
|------|-----|
| FP pairs | 0/75 = 0% |
| Round 1 consistency | 20/20 = 100% |

### 9.3 致命问题：TRAIN = TEST

```
Round 1 (20 cases)
  → 分析 Human 使用的信息源
  → 发现 IS-01 (number pattern) + IS-02 (readable title)
  → 在同 20 cases 上验证 IS pattern consistency
  → 在全 43 cases 上做 counterfactual classification
  → 得到 29/43 CF-A

Discovery Set = Evaluation Set → TRAIN = TEST → 循环推理
```

**29/43 = 67.4% 只是 POTENTIAL RESOLUTION RATE，不是 ACTUAL BOUNDARY SHRINKAGE。**

### 9.4 数据污染审计

| 污染类型 | 案例数 | 说明 |
|---------|--------|------|
| DIRECT_CONTAMINATION | 20/43 | Round 1 reviewed = IS 发现来源 |
| INDIRECT_CONTAMINATION | 23/43 | counterfactual 分析，研究者已看 IS pattern |
| 评估合格 | 0/43 | 无独立评估案例可用 |

---

## 10. Independent Machine-Resolvability Experiment Design

### 10.1 冻结的决策协议 (§9.3)

```
Step 1: Compute IS-01(text_a), IS-02(text_b) using frozen definitions
Step 2: IS-01(text_a)==True AND IS-02(text_b)==True  → MERGE
Step 3: IS-01(text_a)==False AND IS-02(text_b)==False → KEEP_SEPARATE
Step 4: Otherwise (mixed signals)                     → INSUFFICIENT_EVIDENCE
```

### 10.2 Pre-Registered Gates

| Gate | 条件 | 设定时间 |
|------|------|---------|
| G7 | Precision ≥ 95% | 实验前预注册 |
| G8 | Recall ≥ 80% | 实验前预注册 |

### 10.3 7 个未处理 PDF 的独立性审计

| PDF | 独立性 | 污染 |
|-----|--------|------|
| arxiv_2402.18619.pdf | INDEPENDENT | ZERO |
| arxiv_bio2.pdf | INDEPENDENT | ZERO |
| qbio_genomics.pdf | INDEPENDENT | ZERO |
| qbio_rna.pdf | INDEPENDENT | ZERO |
| arxiv_2310.16825.pdf | PARTIALLY_CONTAMINATED | metadata + P1 processed |
| arxiv_2401.00047.pdf | PARTIALLY_CONTAMINATED | metadata only |
| qbio_cell.pdf | PARTIALLY_CONTAMINATED | metadata + fonts |

**4 个完全独立的 PDF 被选为独立评估语料。**

---

## 11. Independent Evaluation Data Collection

### 11.1 候选宇宙生成

在 4 个独立 PDF 上执行冻结 P1-P6 管道：

| 文档 | AMBIGUOUS cases |
|------|----------------|
| ind_arxiv_2402 | 4 |
| ind_arxiv_bio2 | 103 |
| ind_qbio_genomics | 85 |
| ind_qbio_rna | 62 |
| **总计** | **254** |

### 11.2 采样框冻结

| 维度 | 值 |
|------|-----|
| 采样方法 | 分层随机 |
| 种子 | 20240908 |
| 分层维度 | 纯几何 (gap bins, w_b bins, line_obs bins, w_a bins) |
| 采样量 | 69 / 254 (27.2%) |

### 11.3 双盲人工审查

| 维度 | 值 |
|------|-----|
| 审查者数 | 2 (Reviewer A + Reviewer B) |
| 协议 | BLIND (仅看 case_id, page, text_a, text_b, page_context) |
| 隔离 | 完全独立 subagent，无共享状态 |
| 禁止看到 | IS-01/IS-02, 几何元数据, 机器预测, Round 1, DICE 概念 |

### 11.4 审查结果与一致性

| 指标 | 值 |
|------|-----|
| Reviewer A | MERGE=24, KEEP_SEPARATE=45 |
| Reviewer B | MERGE=25, KEEP_SEPARATE=44 |
| 简单一致率 | 68/69 = **98.6%** |
| Cohen's Kappa | **0.968** (Strong agreement) |
| 分歧数 | 1 (IND-AMB-032) |
| 裁定 | 第三独立审查者 → KEEP_SEPARATE |

### 11.5 语义 GT 冻结

| 维度 | 值 |
|------|-----|
| 总案例 | 69 |
| 可用 GT | 69/69 = **100%** |
| GT 标签 | MERGE=24, KEEP_SEPARATE=45 |
| GT 层级 | LEVEL_2_AGREED=68, LEVEL_2_ADJUDICATED=1 |
| IS-01/IS-02 已计算 | **FALSE** (禁止) |
| 机器预测已计算 | **FALSE** (禁止) |

### 11.6 溯源审计

9/9 checks PASS:
- IS-01/IS-02 未计算 ✅
- 机器指标未计算 ✅
- 盲审包含仅允许字段 ✅
- 代码未引用 Round 1 数据 ✅
- 采样框纯几何分层 ✅
- GT 冻结且无机器计算 ✅
- 审查结果仅含 decision/reason ✅
- 无机器预测文件存在 ✅
- 裁定者盲审 ✅

---

## 12. Independent Machine-Resolvability Evaluation (最终实验)

### 12.1 实验条件

| 维度 | 值 |
|------|-----|
| 评估集 | Frozen 69 cases |
| 特征规范 | FROZEN IS-01 / IS-02 |
| 决策协议 | FROZEN §9.3 |
| GT | Level 2 Semantic GT (kappa=0.968) |
| 确定性验证 | Run 1 = Run 2 (0 mismatches) |

### 12.2 混淆矩阵

| | GT: MERGE | GT: KEEP_SEPARATE | 总计 |
|---|-----------|-------------------|------|
| Machine: MERGE | **TP = 0** | **FP = 3** | 3 |
| Machine: KEEP_SEPARATE | **FN = 2** | **TN = 8** | 10 |
| Machine: INSUFFICIENT_EVIDENCE | 22 | 34 | 56 |
| **总计** | **24** | **45** | **69** |

### 12.3 核心指标

| 指标 | 公式 | 值 | Gate |
|------|------|-----|------|
| Precision | TP/(TP+FP) = 0/3 | **0.000** | G7≥95% **FAIL** ❌ |
| Recall | TP/(TP+FN) = 0/2 | **0.000** | G8≥80% **FAIL** ❌ |
| F1 | 2PR/(P+R) | **0.000** | — |
| Accuracy | (TP+TN)/total = 8/69 | **0.116** | — |
| FPR | FP/(FP+TN) = 3/11 | **0.273** | — |
| Coverage | 13/69 | **0.188** | — |
| Abstention Rate | 56/69 | **0.812** | — |

### 12.4 IS 特征观测

| 特征 | True | False |
|------|------|-------|
| IS-01(text_a) | 11 (15.9%) | 58 (84.1%) |
| IS-02(text_b) | 51 (73.9%) | 18 (26.1%) |

### 12.5 三个分别报告的数字

| 数字 | 公式 | 值 |
|------|------|-----|
| 1. Potential Resolution Rate | Level 2 / Level 1 = 11/69 | **15.9%** |
| 2. Machine Deterministic Resolution Rate | Level 3 / Level 1 = 13/69 | **18.8%** |
| 3. Independently Validated Boundary Shrinkage Rate | Level 4 / Level 1 = 0/69 | **0.0%** |

### 12.6 跨文档分析

| 文档 | 总数 | TP | FP | TN | FN | ABSTAIN | Precision | Recall | 标记 |
|------|------|----|----|----|----|---------|-----------|--------|------|
| ind_arxiv_2402 | 4 | 0 | 0 | 0 | 0 | 4 | 0.000 | 0.000 | LOW_SAMPLE |
| ind_arxiv_bio2 | 25 | 0 | 0 | 5 | 0 | 20 | 0.000 | 0.000 | |
| ind_qbio_genomics | 23 | 0 | 0 | 2 | 0 | 21 | 0.000 | 0.000 | |
| ind_qbio_rna | 17 | 0 | 3 | 1 | 2 | 11 | 0.000 | 0.000 | |

**无任何文档产生 TP。所有 FP 和 FN 集中在 ind_qbio_rna。**

### 12.7 Boundary Class 分析

| Boundary Class | 总数 | TP | FP | TN | FN | ABSTAIN |
|---------------|------|----|----|----|----|---------|
| BODY_TEXT_CONTINUATION | 27 | 0 | 0 | 3 | 1 | 23 |
| REFERENCE_LIST_ENTRY | 16 | 0 | 0 | 0 | 1 | 15 |
| TABLE_CELL | 11 | 0 | **3** | 0 | 0 | 8 |
| OTHER_AMBIGUOUS | 9 | 0 | 0 | 2 | 0 | 7 |
| TABLE_CELL_PAIR | 4 | 0 | 0 | 3 | 0 | 1 |
| FIGURE_LABEL | 2 | 0 | 0 | 0 | 0 | 2 |
| **TOC_SECTION_NUMBER_TITLE** | **0** | — | — | — | — | — |
| **APPENDIX_LETTER_TITLE** | **0** | — | — | — | — | — |

**关键发现: 独立评估集中 0 个 TOC_SECTION_NUMBER_TITLE 案例——IS-01+IS-02 的原始设计目标场景在独立数据中不存在。**

### 12.8 False Positive 详细分析

3 个 FP 全部来自 TABLE_CELL，呈现完全一致的模式：

| Case | text_a | text_b | IS-01_a | IS-02_b | GT | 失败模式 |
|------|--------|--------|---------|---------|----|---------| 
| IND-AMB-247 | "121" | "40 mM Hepes" | True | True | KEEP_SEPARATE | 表格数字+可读词 |
| IND-AMB-223 | "5." | "SARS-CoV-2" | True | True | KEEP_SEPARATE | 表格编号+样本名 |
| IND-AMB-235 | "6." | "RNA" | True | True | KEEP_SEPARATE | 表格编号+样本类型 |

**FALSE POSITIVE MODE**: number + readable token in TABLE_CELL。IS-01 正确匹配数字，IS-02 正确匹配可读词，但语义上它们属于不同表格列。

### 12.9 False Negative 详细分析

2 个 FN 均为引用列表中的文本片段：

| Case | text_a | text_b | IS-01_a | IS-02_b | GT | 失败模式 |
|------|--------|--------|---------|---------|----|---------|
| IND-AMB-200 | "et" | "al.," | False | False | MERGE | 引用作者缩写 |
| IND-AMB-201 | "al.," | "2025)." | False | False | MERGE | 引用年份结尾 |

**FN 模式**: 引用列表中的短文本片段既非数字也无可读词，IS-01+IS-02 均返回 False。

### 12.10 Abstention 分析

| 子类 | 数量 | 说明 |
|------|------|------|
| IS-01_a=True + IS-02_b=False | 8 | 全部 GT=KEEP_SEPARATE (正确 abstain) |
| IS-01_a=False + IS-02_b=True | 48 | 22 GT=MERGE + 26 GT=KEEP_SEPARATE |
| Abstain on GT=MERGE | 22 | 错过的 MERGE 机会 |
| Abstain on GT=KEEP_SEPARATE | 34 | 正确拒绝 |

**INSUFFICIENT_EVIDENCE 安全机制有效**: 8 个 IS-01_a=True + IS-02_b=False 的 abstain 全部 GT=KEEP_SEPARATE，正确阻止了 8 个潜在 FP。

### 12.11 IS-02 Loose Detection 检查

| 检查项 | 结果 |
|--------|------|
| 存在 IS-02 loose detection 的案例 | 9 |
| 由 loose detection 直接导致的 FP | **0** |
| Loose detection 案例的结果 | 全部 abstain (因 IS-01_a=False) |

**IS-02 loose detection (cos/sin/and/are) 未直接导致 FP。** FP 的根因是 IS-01+IS-02 在 TABLE_CELL 场景下的语义不足。

### 12.12 Gate 结果

| Gate | 条件 | 结果 |
|------|------|------|
| G1 | Independent Evaluation Set Exists | ✅ PASS |
| G2 | Feature Freeze | ✅ PASS |
| G3 | No Leakage | ✅ PASS |
| G4 | Semantic GT Validity | ✅ PASS |
| G5 | Provenance | ✅ PASS |
| G6 | Determinism | ✅ PASS |
| **G7** | **Precision ≥ 95%** | **❌ FAIL** (0.000) |
| **G8** | **Recall ≥ 80%** | **❌ FAIL** (0.000) |
| G9 | Cross-Document Generalization | ❌ FAIL (0 TP) |
| G10 | Adversarial Robustness | ❌ FAIL (3/3 FP) |
| G11 | INSUFFICIENT_EVIDENCE Safety | ✅ PASS |
| G12 | Boundary Shrinkage Evidence | ❌ FAIL (0%) |

**7/12 PASS, 5/12 FAIL**

### 12.13 最终结论

**C. MACHINE-RESOLVABILITY NOT DEMONSTRATED**

---

## 13. 完整数据对比表

### 13.1 从 Round 1 到独立评估的演进

| 维度 | Round 1 (Discovery) | Counterfactual | Independent Evaluation |
|------|-------------------|---------------|----------------------|
| 案例数 | 20 | 43 | 69 |
| 文档数 | 3 (同族 arxiv) | 3 (同族 arxiv) | 4 (独立) |
| 审查者 | 1 (reviewer_1) | N/A | 2 + 1 adjudicator |
| GT 类型 | Geometry GT | Geometry GT | Semantic GT (Level 2) |
| GT 有效性 | DISPUTED (AMB-026) | DISPUTED | VALID (kappa=0.968) |
| Inter-rater | NOT MEASURED | N/A | 98.6% (kappa=0.968) |
| 数据独立性 | DIRECT_CONTAMINATED | INDIRECT_CONTAMINATED | INDEPENDENT |
| IS-01/IS-02 来源 | 从 Round 1 发现 | 同左 | 冻结 (非从此发现) |
| Timer | BROKEN | N/A | N/A (不测量) |

### 13.2 从 Counterfactual 到独立评估的性能对比

| 指标 | Counterfactual (43 cases) | Independent (69 cases) | 变化 |
|------|--------------------------|----------------------|------|
| Potential Resolution Rate | 29/43 = 67.4% | 11/69 = 15.9% | **-51.5pp** |
| Machine Deterministic Rate | N/A (counterfactual) | 13/69 = 18.8% | — |
| Validated Shrinkage | UNKNOWN | 0/69 = 0.0% | — |
| FP Rate | 0/75 = 0% | 3/11 = 27.3% | **+27.3pp** |
| Precision | N/A | 0.000 | — |
| Recall | N/A | 0.000 | — |
| Abstention | N/A | 81.2% | — |
| TOC_SECTION_NUMBER_TITLE | 27/43 = 62.8% | 0/69 = 0% | **-62.8pp** |

### 13.3 关键认知反转

| 认知 | Counterfactual 结论 | Independent 结论 | 反转原因 |
|------|-------------------|-----------------|---------|
| IS-01+IS-02 有效性 | "PROMISING" (67.4%) | "NOT_DEMONSTRATED" (0%) | TRAIN=TEST → 独立测试 |
| FP Rate | 0% (0/75) | 27.3% (3/11) | 同 corpus → 独立 corpus |
| 目标场景覆盖 | 62.8% TOC | 0% TOC | arxiv TOC → bio/RNA 无 TOC |
| Boundary Shrinkage | "POTENTIAL 67.4%" | "0% VALIDATED" | counterfactual → actual |

---

## 14. 研究脉络图

```
Human Annotation 认知障碍
├── Timer Bug → Human Cost 不可测
├── Geometry GT ≠ Semantic GT (AMB-026) → GT 有效性存疑  
└── 单审查者 → 无 Inter-Rater Agreement
      │
      ▼
Cross-Document Audit (8 docs, 2255 pairs, 43 AMBIGUOUS)
      │
      ▼
P4 v3 Span Design (三态模型: MERGE/BLOCK/AMBIGUOUS)
      │
      ▼
Evidence Boundary Decision (INSUFFICIENT_EVIDENCE 概念)
      │
      ▼
Human Boundary Review Round 1 (20 cases, 95% accuracy)
      ├── 发现 IS-01 (TEXT_NUMBER_PATTERN)
      └── 发现 IS-02 (TEXT_READABLE_TITLE)
            │
            ▼
Round 1 Integrity Audit
      ├── Timer: INVALID
      ├── GT: DISPUTED (AMB-026)
      └── Single reviewer: NOT MEASURED
            │
      ┌─────┴─────┐
      ▼           ▼
Boundary Semantics    Information Source Gap
Convergence            Analysis (IS-01~IS-10)
(GT Hierarchy L0-L3)   (Category A/B/C)
(Shrinkage L1-L4)       
      │                 │
      └─────┬───────────┘
            ▼
TOC Feasibility Study (Counterfactual)
      ├── 29/43 = 67.4% CF-A (POTENTIAL)
      ├── 0/75 = 0% FP (on same corpus)
      └── TRAIN = TEST problem discovered
            │
            ▼
Data Independence Audit
      ├── 20 DIRECT_CONTAMINATED
      ├── 23 INDIRECT_CONTAMINATED
      └── 0/43 evaluation eligible
            │
            ▼
Independent Evaluation Data Collection
      ├── 4 independent PDFs → 254 AMBIGUOUS
      ├── Sampling: 69 cases (seed=20240908)
      ├── Dual blind review: kappa=0.968
      ├── Adjudication: 1 case → KEEP_SEPARATE
      ├── Semantic GT: 69/69 usable (Level 2)
      └── Provenance audit: 9/9 PASS
            │
            ▼
Independent Machine-Resolvability Evaluation
      ├── Confusion Matrix: TP=0, FP=3, TN=8, FN=2, ABSTAIN=56
      ├── Precision=0.000 → G7 FAIL
      ├── Recall=0.000 → G8 FAIL
      ├── 3 FP: TABLE_CELL (number + readable token)
      ├── 2 FN: REFERENCE fragments (et/al.,)
      ├── 81.2% abstention
      ├── 0 TOC_SECTION_NUMBER_TITLE in independent set
      ├── Determinism: TRUE (Run 1 = Run 2)
      ├── Gates: 7/12 PASS, 5/12 FAIL
      └── Conclusion: MACHINE-RESOLVABILITY NOT DEMONSTRATED
            │
            ▼
      STOP — 不修改规则，不修复 FP
      所有问题 → NEXT INFORMATION SOURCE / NEXT EXPERIMENT
```

---

## 15. 补充关键数据（论文用）

### 15.1 P7.1 Evidence Gap: Human Validation 作为瓶颈

P7.1 StructureHypothesis 管道在真实语料上运行的结果：

| 指标 | 值 |
|------|-----|
| 总假设数 | 175 |
| 总关系数 | 367 |
| 已验证假设 | **0 / 175** |
| 产出 Evidence | **0** |
| Source Span 覆盖率 | 0.988 |
| Source Region 覆盖率 | 0.931 |
| 孤立假设 | 0 |
| 重复假设 | 0 |
| 语义泄漏 | 0 |
| 确定性可复现 | True |

**关键发现**: 175 个假设 / 0 个验证 → 新感知栈产出 **0 个 Evidence**。链 `Document → Observation → Relation → StructureHypothesis → Human Validation → Validated Structure → Evidence` 在 Human Validation 这个唯一从未通过的 gate 处阻塞。

这是"已经阻塞"，不是"将要阻塞"——Human Validation 不是可选增强，而是整个 Evidence 产出的必经之路。

### 15.2 视觉内容证据缺口

P1 在提取文本时跳过了所有非文本块 (`if block_type != 0: skip`)。对 6 个真实文档的 PyMuPDF 分析：

| 文档 | 页数 | 图片页 | 图片数 | 向量页 | 向量数 | 受影响页 |
|------|------|--------|--------|--------|--------|---------|
| RM501 (设备手册) | 2 | 2 | 3 | 2 | 44 | 2/2 |
| DC201 (设备手册) | 8 | 1 | 1 | 7 | 192 | 7/8 |
| arxiv_2310 (CS论文) | 19 | 10 | 83 | 13 | 963 | 18/19 |
| arxiv_bio (生物论文) | 39 | 0 | 0 | 39 | 794 | 39/39 |
| arxiv_2401 | 18 | 0 | 0 | 0 | 0 | 0/18 |
| qbio_cell (生物论文) | 7 | 5 | 7 | 4 | 13 | 6/7 |

**5/6 文档包含被 P1 完全跳过的视觉内容** (94 images + ~2006 vector objects)。视觉对象覆盖率 = **0%**。

### 15.3 P4 阈值敏感性分析

Cross-Document Audit 中对 P4 的 `max_horizontal_gap=8.0pt` 阈值做了敏感性测试：

| 阈值 | TRUE merge | FALSE merge | Precision |
|------|-----------|-------------|-----------|
| 8.0pt (frozen) | — | — | (仅合并确定对) |
| 12pt | 17 | 79 | **17.7%** |
| 20pt | 19 | 157 | **10.8%** |
| gap=10pt alone | 17 | 75 | **18.5%** |

**结论**: 不存在单一几何阈值可以同时保持高 precision 和高 recall。8-12pt gap 区域同时包含 TRUE merge (TOC 编号+标题) 和 FALSE merge (数学公式符号)——gap 值无法区分。

### 15.4 三态模型的 762 对统计

对 8 个文档的 762 same-y observation pairs 的完整分类：

| 状态 | 对数 | 占比 | 处理方式 |
|------|------|------|---------|
| DETERMINISTIC_MERGE (gap≤8) | 351 | 46.1% | P4 自动合并 |
| DETERMINISTIC_BLOCK_CROSS (gap>50) | 84 | 11.0% | 自动阻止 |
| DETERMINISTIC_BLOCK_FONT (diff style) | 84 | 11.0% | 自动阻止 |
| DETERMINISTIC_BLOCK_DENSE (line_obs>15) | 71 | 9.3% | 自动阻止 |
| DETERMINISTIC_BLOCK_NARROW (w_b<15) | 129 | 16.9% | 自动阻止 |
| **AMBIGUOUS** | **43** | **5.6%** | **Human Review** |
| **总计** | **762** | **100%** | |

**94.4% 机器确定处理，5.6% 需要 Human Review。** AMBIGUOUS 仅存在于 arxiv 论文中，5 个设备手册全部为 0。

### 15.5 组合几何过滤器精度递进

对 307 same-y unmerged pairs (排除 gap≤8 的 351 对) 的多特征过滤链：

| 过滤阶段 | 剩余 TRUE | 剩余 FALSE | Precision |
|---------|----------|-----------|-----------|
| 初始 (gap>8, same_y) | 30 | 307 | 8.9% |
| + same_font | 30 | 27 | 52.6% |
| + same_style | 30 | 27 | 52.6% |
| + w_b≥25 | 30 | 27 | 52.6% |
| + gap<50 | 30 | 13 | 69.8% |
| + line_obs≤10 | 30 | 13 | 69.8% |

**最终: 30 TRUE / 13 FALSE = 69.8% precision, 0% false negative。** 13 个不可消除的 FALSE 全部来自 arxiv_2307 的公式碎片→正文过渡 (w_b 在 15-21pt 灰色区域)。

### 15.6 Round 1 按 Mode 的准确率

| Mode | 案例数 | 准确率 | 备注 |
|------|--------|--------|------|
| TOC_SECTION_NUMBER_TITLE | 12 | 12/12 = 100% | 全部 MERGE |
| FORMULA_FRAGMENT_WIDE | 6 | 6/6 = 100% | 全部 KEEP_SEPARATE |
| APPENDIX_LETTER_TITLE | 1 | 1/1 = 100% | MERGE |
| BODY_TEXT_CONTINUATION | 1 | 0/1 = 0% | AMB-026 (GT disputed) |

**BODY_TEXT_CONTINUATION 是唯一的人机分歧来源** (n=1, 统计上无意义，但揭示了 GT 本体论问题)。

### 15.7 Round 1 按文档的准确率

| 文档 | 案例数 | 准确率 | 中位 gap | 决策分布 |
|------|--------|--------|---------|---------|
| arxiv_toc | 7 | 7/7 = 100% | ~3.0s | 全部 MERGE |
| arxiv_2307 | 10 | 10/10 = 100% | ~6.7s | 4 MERGE / 6 KEEP_SEPARATE |
| arxiv_bio_body | 3 | 2/3 = 67% | ~3.0s | 含 AMB-026 (disputed) |

### 15.8 Timer 修复设计（未实施）

Integrity Audit 中设计了修复方案，但 **NOT AUTHORIZED** 实施：

```
状态机: CASE_OPEN → CASE_DISPLAYED → HUMAN_DECISION → CASE_SUBMITTED
记录 4 个时间戳:
  - case_open_ts: 案例加载开始
  - case_displayed_ts: 页面图像渲染完成
  - decision_click_ts: 审查者点击决策按钮
  - case_submitted_ts: API 提交完成

派生指标:
  - load_time = case_displayed_ts - case_open_ts
  - think_time = decision_click_ts - case_displayed_ts  ← 纯思考时间
  - submit_rtt = case_submitted_ts - decision_click_ts
  - total_case_time = case_submitted_ts - case_open_ts

修复: 移除 /api/case 中的 start_time_ms 重置 (L109-113)
```

### 15.9 IS-01~IS-10 在 Round 1 中的使用频率

| IS | 名称 | 类别 | Round 1 使用次数 | P4 是否有 | 机器可观测 |
|----|------|------|-----------------|---------|-----------|
| IS-01 | TEXT_NUMBER_PATTERN | B (文本) | 12 | ❌ | ✅ regex |
| IS-02 | TEXT_READABLE_TITLE | B (文本) | 14 | ❌ | ✅ 词检测 |
| IS-03 | TEXT_SYMBOL_PATTERN | B (文本) | 13 (7+6) | ❌ | ✅ 字符类 |
| IS-04 | TEXT_PUNCTUATION | B (文本) | 5 | ❌ | ✅ 字符检查 |
| IS-05 | TEXT_CAPITAL_START | B (文本) | 15 | ❌ | ✅ 大小写 |
| IS-06 | TEXT_APPENDIX_LETTER | B (文本) | 1 | ❌ | ✅ regex |
| IS-07 | VISUAL_TOC_CONTEXT | B (视觉) | 7 | ❌ | ✅ P6 region |
| IS-08 | VISUAL_FORMULA_CONTEXT | B (视觉) | 10 | ❌ | ✅ P6 region |
| IS-09 | VISUAL_BODY_CONTEXT | B (视觉) | 3 | ❌ | ✅ P6 region |
| IS-10 | SENTENCE_BOUNDARY | **C (语义)** | 1 | ❌ | ⚠️ 部分 |

**核心洞察**: "差距不是 'P4 有数据但没组合'，而是 'P4 的契约排除了文本和视觉信息——这些信息个体上是机器可观测的，但集体上需要解释。'"

### 15.10 Gate 体系对照

不同阶段定义了不同编号的 Gate 体系。为论文统一对照：

| 论文用编号 | 条件 | 早期定义 | 独立评估定义 | 最终状态 |
|-----------|------|---------|------------|---------|
| Gate-1 | 独立评估集存在 | G1 ❌ FAIL | G1 ✅ PASS | ✅ PASS |
| Gate-2 | 特征规范冻结 | G2 ✅ PASS | G2 ✅ PASS | ✅ PASS |
| Gate-3 | 无评估泄漏 | G3 ❌ FAIL | G3 ✅ PASS | ✅ PASS |
| Gate-4 | 语义 GT 有效性 | G4 ❌ FAIL | G4 ✅ PASS | ✅ PASS |
| Gate-5 | 溯源完整性 | G9 ✅ PASS | G5 ✅ PASS | ✅ PASS |
| Gate-6 | 确定性 | N/A | G6 ✅ PASS | ✅ PASS |
| Gate-7 | Precision ≥ 95% | G3 (FP<5%) ❌ | G7 ❌ FAIL | ❌ FAIL |
| Gate-8 | Recall ≥ 80% | G1 (≥20 cases) ❌ | G8 ❌ FAIL | ❌ FAIL |
| Gate-9 | 跨文档泛化 | G2 (≥3 docs) ⚠️ | G9 ❌ FAIL | ❌ FAIL |
| Gate-10 | Adversarial 鲁棒性 | G5 ✅ PASS | G10 ❌ FAIL | ❌ FAIL |
| Gate-11 | INSUFFICIENT_EVIDENCE 安全 | N/A | G11 ✅ PASS | ✅ PASS |
| Gate-12 | Boundary Shrinkage 证据 | N/A | G12 ❌ FAIL | ❌ FAIL |

**最终: 7/12 PASS, 5/12 FAIL。** 从早期 2/9 → 独立评估 7/12，基础设施类 Gate 全部通过，但性能类 Gate (Precision/Recall/Generalization/Adversarial/Shrinkage) 全部 FAIL。

---

## 附录: 文件清单

| 阶段 | 关键文件 |
|------|---------|
| Cross-Document Audit | `cross_document_text_unit_relation_audit.md` |
| P4 v3 Design | `p4_v3_design.md`, `p4_v3_feature_matrix.md` |
| Evidence Boundary | `evidence_boundary_decision_design.md` |
| Round 1 | `human_boundary_review_round1_report.md`, `_metrics.json` |
| Integrity Audit | `human_boundary_round1_integrity_audit.md`, `_metrics.json` |
| Boundary Semantics | `human_boundary_semantics_design.md`, `_matrix.json` |
| Information Gap | `boundary_intelligence_information_gap_analysis.md`, `_matrix.json` |
| TOC Feasibility | `boundary_intelligence_toc_feasibility_study.md`, `_matrix.json` |
| Experiment Design | `independent_machine_resolvability_experiment_design.md`, `_matrix.json` |
| Data Collection | `independent_evaluation_collection_report.md`, `_manifest.json`, `_matrix.json` |
| Machine Evaluation | `independent_machine_resolvability_evaluation_report.md`, `_results.json`, `_metrics.json` |

---

## 附录: 冻结基线完整性

全程冻结基线保持 INTACT：

| 组件 | 哈希 | 状态 |
|------|------|------|
| P7.1 (6 files) | — | 0 drift |
| P7.2 (8 files) | — | 0 drift |
| P1-P6 (25 files) | — | 0 changed |
| Frozen 730 | a10b368e | PASS |
| span_rules.py | 1c8e3830 | PASS |
| calibration_filter.py | 6ab1ee78 | PASS |

**全程未修改任何 frozen/production 代码。所有实验在 READ-ONLY 基线上执行。**
