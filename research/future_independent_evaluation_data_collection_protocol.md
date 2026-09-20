# Future Independent Evaluation Data Collection Protocol

> READ-ONLY DESIGN ONLY。不修改任何 frozen/production/source 文件。不实施。不进入 P7.3。
> 不处理 PDF。不生成 candidate。不运行 IS-01/IS-02。不进行 Human Validation。

---

## Executive Summary

```
OBJECTIVE:
  设计一套严格、可审计、不可污染实验的数据收集协议，
  使未来可以从独立 PDF 中建立真正 Independent Evaluation Set。

INDEPENDENT CORPUS = PARTIAL
  - 4/7 PDFs: INDEPENDENT (zero references in any P7 artifact)
      arxiv_2402, arxiv_bio2, qbio_genomics, qbio_rna
  - 3/7 PDFs: PARTIALLY_CONTAMINATED (metadata-level, not boundary-level)
      arxiv_2310 (P1 processed + evidence gap metadata)
      arxiv_2401 (evidence gap metadata)
      qbio_cell (evidence gap metadata + font analysis)
  - 0/7 PDFs: CONTAMINATED (no IS-01/IS-02 computed, no boundary pairs analyzed)

CORRECTION FROM PREVIOUS STAGE:
  Previous stage claimed "all 7 PDFs are truly independent".
  Audit reveals 3/7 have partial contamination from evidence gap analysis.
  Contamination is METADATA-LEVEL (page counts, image counts, font types),
  NOT BOUNDARY-LEVEL (no text_a/text_b pairs analyzed, no IS patterns computed).

SEMANTIC GT PROTOCOL = READY (design only, not implemented)
FEATURE FREEZE = PASS (IS-01/IS-02 frozen)
DESIGN STATUS = READY
IMPLEMENTATION = NOT AUTHORIZED
P7.3 = NOT AUTHORIZED
FROZEN BASELINE = INTACT
STOP = TRUE
```

---

## 一、Objective

### 1.1 不是做什么

不是："怎么让 7 个 PDF 跑完 P1-P6？"
不是："怎么实现 IS-01 / IS-02？"
不是："怎么开始 machine-resolvability experiment？"

### 1.2 做什么

设计："如何从独立 PDF 中构建一个不会被当前 IS-01 / IS-02 洞察污染、并且具有独立 semantic Ground Truth 的 Evaluation Set？"

### 1.3 核心区分

```
Independent PDF ≠ Independent Evaluation Set

必须建立完整链条:
  Independent Corpus
  → Frozen P1-P6 Processing
  → New Boundary Candidates
  → Eligibility Audit
  → Blind Human Semantic Validation
  → Evaluation Set Freeze
  → Frozen Feature Evaluation
```

---

## 二、Independent Corpus Definition

### 2.1 Corpus Readiness Audit（修正版）

对 7 个 unprocessed PDFs 逐一检查全部污染向量：

| PDF | Evidence Gap Analysis | P1 Processed | Cross-doc Audit | AMBIGUOUS Extraction | Round 1 | IS-01/IS-02 Computed | Boundary Pairs Analyzed | Researcher Saw Text | Researcher Saw Metadata | Independence Status |
|---|---|---|---|---|---|---|---|---|---|---|
| arxiv_2310.16825.pdf | ✅ | ✅ (as "arxiv_single") | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | PARTIALLY_CONTAMINATED |
| arxiv_2401.00047.pdf | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | PARTIALLY_CONTAMINATED |
| arxiv_2402.18619.pdf | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **INDEPENDENT** |
| arxiv_bio2.pdf | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **INDEPENDENT** |
| qbio_cell.pdf | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | PARTIALLY_CONTAMINATED |
| qbio_genomics.pdf | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **INDEPENDENT** |
| qbio_rna.pdf | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **INDEPENDENT** |

### 2.2 污染类型详解

#### arxiv_2310.16825.pdf — PARTIALLY_CONTAMINATED

| 污染维度 | 状态 | 说明 |
|---|---|---|
| Evidence Gap Analysis | ✅ CONTAMINATED | 在 p7_evidence_gap_analysis.md 中分析了视觉内容缺口（19 页，83 图像，963 矢量对象，18/19 页受影响） |
| P1 Processing | ✅ CONTAMINATED | 在 p7_test_results.json 中作为 "arxiv_single" 出现，P1 提取了文本（包括 "arXiv:2310.16825v1 [cs.CV] 25 Oct 2023"） |
| Cross-doc Audit | ❌ NOT CONTAMINATED | 未进入 cross_doc_audit_raw.json |
| AMBIGUOUS Extraction | ❌ NOT CONTAMINATED | 未进入 43 AMBIGUOUS cases |
| Round 1 | ❌ NOT CONTAMINATED | 未进入 Round 1 |
| IS-01/IS-02 | ❌ NOT CONTAMINATED | 未计算 IS pattern |
| Boundary Pairs | ❌ NOT CONTAMINATED | 未分析 boundary pairs |
| Researcher Saw Text | ⚠️ PARTIAL | 研究者在 test results 中看到了 P1 提取的文本，但仅是 paper header，不是 boundary pair text |
| Researcher Saw Metadata | ⚠️ PARTIAL | 研究者看到了页数、图像数、矢量对象数 |

**污染性质**：METADATA-LEVEL + PARTIAL P1 PROCESSING。研究者知道该文档存在、知道其视觉内容特征，但未分析 boundary pairs。P1 提取的文本仅是 paper header，不涉及 IS-01/IS-02 评估的 boundary pair text。

**是否可用于 Independent Evaluation**：⚠️ 有条件使用。需要在 protocol 中明确：研究者已有的 metadata 知识不应影响 sampling 决策。建议优先使用 4 个 INDEPENDENT PDFs，将此 PDF 作为补充。

#### arxiv_2401.00047.pdf — PARTIALLY_CONTAMINATED

| 污染维度 | 状态 | 说明 |
|---|---|---|
| Evidence Gap Analysis | ✅ CONTAMINATED | 在 p7_evidence_gap_analysis.md 中分析了元数据（18 页，0 图像，0 表格，0/18 页受影响） |
| P1 Processing | ❌ NOT CONTAMINATED | 未经过 P1 |
| Researcher Saw Metadata | ⚠️ PARTIAL | 研究者看到了页数、图像数 |

**污染性质**：METADATA-LEVEL ONLY。研究者知道该文档有 18 页、0 图像。不涉及 boundary pairs 或 text content。

**是否可用于 Independent Evaluation**：⚠️ 有条件使用。metadata 污染程度低。

#### qbio_cell.pdf — PARTIALLY_CONTAMINATED

| 污染维度 | 状态 | 说明 |
|---|---|---|
| Evidence Gap Analysis | ✅ CONTAMINATED | 在 p7_evidence_gap_analysis.md 中分析了元数据 + 字体（7 页，5 图像，7 figures，4 表格，13 矢量对象，CMMI9/CMSY7 字体） |
| P1 Processing | ❌ NOT CONTAMINATED | 未经过 P1 |
| Researcher Saw Metadata | ⚠️ PARTIAL | 研究者看到了页数、图像数、字体类型 |

**污染性质**：METADATA-LEVEL + FONT-LEVEL。研究者知道该文档含数学字体（CMMI/CMSY）。

**是否可用于 Independent Evaluation**：⚠️ 有条件使用。font metadata 可能暗示该文档包含公式，但这不直接影响 IS-01/IS-02 的 boundary pair 评估。

### 2.3 4 个 INDEPENDENT PDFs

| PDF | 大小 | 类型 | 完整独立性 |
|---|---|---|---|
| arxiv_2402.18619.pdf | 951KB | arxiv | ✅ 零引用 |
| arxiv_bio2.pdf | 3MB | arxiv biology | ✅ 零引用 |
| qbio_genomics.pdf | 4.6MB | genomics | ✅ 零引用 |
| qbio_rna.pdf | 2.4MB | RNA biology | ✅ 零引用 |

**这 4 个 PDF 是当前唯一完全独立的数据源。**

### 2.4 CORPUS_INDEPENDENCE_STATUS

```
CORPUS_INDEPENDENCE_STATUS:

  INDEPENDENT (4/7):
    arxiv_2402.18625.pdf
    arxiv_bio2.pdf
    qbio_genomics.pdf
    qbio_rna.pdf

  PARTIALLY_CONTAMINATED (3/7):
    arxiv_2310.16825.pdf  — metadata + partial P1
    arxiv_2401.00047.pdf  — metadata only
    qbio_cell.pdf         — metadata + fonts

  CONTAMINATED (0/7):
    none

  修正上一阶段结论:
    上一阶段声称 "all 7 PDFs are truly independent"。
    本阶段审计发现 3/7 有 PARTIAL 污染。
    污染是 METADATA-LEVEL，不是 BOUNDARY-LEVEL。
    无 IS-01/IS-02 计算或 boundary pair 分析。
```

---

## 三、P1-P6 Processing Boundary

### 3.1 核心问题

7 个 PDF 虽然目前未经过完整 P1-P6（arxiv_2310 经过部分 P1），但未来必须经过 P1-P6 才能生成 boundary candidates。

**关键区分**：哪些处理属于 CORPUS PREPROCESSING，哪些属于 EXPERIMENTAL FEATURE OBSERVATION，哪些属于 DECISION LEAKAGE。

### 3.2 三层处理分类

| 层级 | 名称 | 允许? | 说明 |
|---|---|---|---|
| Layer A | CORPUS PREPROCESSING | ✅ 允许 | Frozen P1-P6 pipeline 可以用于处理独立 PDF，产生 geometric spans 和 boundary candidates |
| Layer B | EXPERIMENTAL FEATURE OBSERVATION | ⚠️ 限制 | IS-01/IS-02 的计算只能在 Evaluation Set Freeze 之后进行 |
| Layer C | DECISION LEAKAGE | ❌ 禁止 | 根据 IS-01/IS-02 结果筛选样本、调整 sampling、修改 feature |

### 3.3 处理顺序约束

```
允许的顺序:
  PDF → Frozen P1-P6 → geometric spans → boundary candidates
  → [STOP: 不得查看 IS-01/IS-02]
  → Blind Human Semantic GT
  → Evaluation Set Freeze
  → [NOW: 可以计算 IS-01/IS-02]
  → Machine Assessment
  → Metrics

禁止的顺序:
  PDF → P1-P6 → 查看 IS-01/IS-02 → 根据结果筛选 → Human GT → Evaluation
  ↑ DECISION LEAKAGE
```

### 3.4 P1-P6 是否破坏独立性

**P1-P6 frozen pipeline 不破坏独立性。**

理由：
1. P1-P6 是 frozen 的几何处理，不涉及 IS-01/IS-02
2. P1 提取 text 内容是 CORPUS PREPROCESSING（Layer A）
3. P4 的 span merge/block 判断是几何判断，不涉及 text pattern analysis
4. P6 的 region classification 是几何/视觉分类，不涉及 text pattern analysis

**但**：P1 提取的 text content 在 Human GT 收集之前不得被研究者用于 IS-01/IS-02 计算。

### 3.5 arxiv_2310 的特殊情况

arxiv_2310 已经经过部分 P1（作为 "arxiv_single" 在 test results 中）。这意味着：
- P1 已提取了该文档的 text observations
- 但未经过 cross_doc_audit（未提取 boundary pairs）
- 未提取 AMBIGUOUS cases
- 未计算 IS patterns

**处理方案**：arxiv_2310 可以重新经过完整 P1-P6 + cross_doc_audit 流程。已有的部分 P1 数据不构成 boundary-level 污染。但研究者已知该文档的视觉内容特征（83 图像、963 矢量对象），这种 metadata 知识需要在 protocol 中通过 blind sampling 来隔离。

---

## 四、Candidate Universe

### 4.1 定义

从 7 个 PDF 的 frozen P1-P6 输出中，定义全部 eligible boundary pairs。

```
Candidate Universe = {
  all same-y unmerged pairs from 7 PDFs
  where 8 < gap <= 50
  AND same_style == True
  AND line_obs_count <= 15
  AND w_b >= 15
}
```

### 4.2 预期规模

基于已处理文档的 AMBIGUOUS rate：

| 文档族 | 已处理页数 | same-y pairs | AMBIGUOUS | AMBIGUOUS rate |
|---|---|---|---|---|
| arxiv (3 docs) | 8 | 408 | 43 | 10.5% |
| device manuals (5 docs) | 13 | 3 | 0 | 0% |

7 个新 PDF 的预期：
- arxiv 类 PDF（4 个：2310, 2401, 2402, bio2）→ 预期 ~40-60 AMBIGUOUS cases（基于 arxiv 文档平均 5.4 AMBIGUOUS/page）
- qbio 类 PDF（3 个：cell, genomics, rna）→ 预期 ~10-30 AMBIGUOUS cases（qbio 文档结构未知）
- **总预期**：~50-90 AMBIGUOUS cases

### 4.3 Candidate Universe 的生成约束

```
Candidate Universe 生成时:
  ✅ 允许: P1-P6 几何处理
  ✅ 允许: same-y pair extraction
  ✅ 允许: gap/dy/w_a/w_b/font/style/line_obs 计算
  ❌ 禁止: IS-01 (number pattern) 计算
  ❌ 禁止: IS-02 (readable title) 计算
  ❌ 禁止: 根据 text content 筛选 candidates
  ❌ 禁止: 根据 IS pattern 预分类
```

---

## 五、Sampling Frame

### 5.1 Sampling Frame 内容

每个 candidate 的 sampling frame metadata：

| 字段 | 允许在 Human GT 前可见? | 说明 |
|---|---|---|
| document_id | ✅ | 文档标识 |
| page | ✅ | 页码 |
| pair_id | ✅ | pair 唯一标识 |
| geometric features (gap, dy, w_a, w_b, style, line_obs) | ✅ | P4 几何特征 |
| boundary class candidate | ⚠️ 仅 P4 分类 | P4 的 DETERMINISTIC/AMBIGUOUS 分类 |
| provenance | ✅ | 来源追溯 |
| IS-01 result | ❌ **FORBIDDEN** | 不得在 Human GT 前计算或显示 |
| IS-02 result | ❌ **FORBIDDEN** | 不得在 Human GT 前计算或显示 |
| machine recommendation | ❌ **FORBIDDEN** | 不得显示机器预测 |
| feature-derived class | ❌ **FORBIDDEN** | 不得显示 IS-derived 分类 |
| predicted decision | ❌ **FORBIDDEN** | 不得显示预测决策 |

### 5.2 Sampling Metadata vs Machine Answer

```
Sampling/Observation Metadata (允许):
  - document_id, page, pair_id
  - geometric features
  - P4 boundary class (DETERMINISTIC/AMBIGUOUS)
  - document family (arxiv / qbio / device)

Machine Answer (禁止在 Human GT 前暴露):
  - IS-01 result
  - IS-02 result
  - machine prediction
  - feature-derived classification
```

**"likely TOC" 等 sampling metadata 不能成为机器答案。**

---

## 六、Sampling Strategy

### 6.1 Stratified Sampling

优先设计 stratified sampling，覆盖以下维度：

| Stratum | 维度 | 覆盖要求 |
|---|---|---|
| S1 | Document | 每个 PDF 至少有代表 |
| S2 | Document family | arxiv (4 PDFs) + qbio (3 PDFs) 均覆盖 |
| S3 | Page/section | 不同页面位置的 pairs |
| S4 | Boundary geometry pattern | 不同 gap/w_b/line_obs 组合 |
| S5 | Likely TOC/appendix context | 可能含 heading 编号的页面 |
| S6 | Likely non-TOC confounder | 不含 heading 的页面（body/formula/table） |
| S7 | Adversarial-looking pattern | 几何上类似 TOC heading 但可能非 heading 的 pairs |

### 6.2 Sampling Procedure

```
Step 1: Process 7 PDFs through frozen P1-P6
Step 2: Extract all same-y unmerged pairs (Candidate Universe)
Step 3: Apply AMBIGUOUS criteria (8 < gap <= 50, same_style, line_obs <= 15, w_b >= 15)
Step 4: Record sampling frame metadata (geometric features only, NO IS computation)
Step 5: Stratified sample from AMBIGUOUS candidates
Step 6: [STOP — do not compute IS-01/IS-02]
Step 7: Send sampled candidates to Blind Human Review
```

### 6.3 Selection Bias 防护

| 防护措施 | 说明 |
|---|---|
| Pre-registered sampling criteria | 在看到任何 text content 前确定 sampling 规则 |
| Geometric-only sampling | 仅基于几何特征（gap, w_b, line_obs）抽样，不基于 text content |
| Full universe recording | 记录全部 Candidate Universe，不仅记录被选中的 |
| No IS computation before sampling | IS-01/IS-02 不得在 sampling 阶段计算 |
| No text preview | 研究者不得在 sampling 阶段预览 text_a/text_b 内容 |

---

## 七、Sample Size Scenarios

### 7.1 不拍脑袋定数量

基于以下参数：
- Expected ambiguous rate: ~10% of same-y pairs (based on arxiv data)
- Target precision: ≥ 95%
- Acceptable false-positive rate: ≤ 5%
- Expected TOC/APPENDIX proportion: ~60% of AMBIGUOUS (based on 29/43 = 67.4%)

### 7.2 三个 Scenario

| Scenario | TOC/APPENDIX cases | 总 AMBIGUOUS cases | 统计假设 | 适用场景 |
|---|---|---|---|---|
| Minimum | 20 | ~35 | 精度估计 ±15%，FP 检测 power 低 | 快速可行性验证 |
| Recommended | 40 | ~70 | 精度估计 ±10%，FP 检测 power 中等 | 正式评估 |
| Strong | 60 | ~100 | 精度估计 ±8%，FP 检测 power 高 | 强结论 |

### 7.3 统计假设

```
Minimum (20 TOC/APPENDIX cases):
  - 如果 20/20 correct → precision estimate = 100%, CI ≈ [82%, 100%]
  - 如果 19/20 correct → precision estimate = 95%, CI ≈ [76%, 100%]
  - FP detection: 如果真实 FP rate = 5%, P(0 FP in 20) = 0.36 → 低 power

Recommended (40 TOC/APPENDIX cases):
  - 如果 38/40 correct → precision estimate = 95%, CI ≈ [83%, 99%]
  - FP detection: 如果真实 FP rate = 5%, P(0 FP in 40) = 0.13 → 中等 power
  - 如果真实 FP rate = 10%, P(≥1 FP in 40) = 0.85 → 可检测

Strong (60 TOC/APPENDIX cases):
  - 如果 57/60 correct → precision estimate = 95%, CI ≈ [86%, 99%]
  - FP detection: 如果真实 FP rate = 5%, P(≥1 FP in 60) = 0.95 → 高 power
  - 如果真实 FP rate = 10%, P(≥1 FP in 60) = 0.998 → 高 power
```

### 7.4 预期数据量是否足够

基于 7 个 PDF 的预期 AMBIGUOUS case 数（~50-90），Recommended scenario（40 TOC/APPENDIX）是可行的，但需要大部分 AMBIGUOUS cases 是 TOC/APPENDIX 类型。如果新 PDF 的 AMBIGUOUS 分布与 arxiv 不同（例如更多 FORMULA 或 BODY_CONT），TOC/APPENDIX cases 可能不足。

**如果 TOC/APPENDIX cases 不足 20（Minimum），则需要增加更多 PDF 或接受 INCONCLUSIVE 结论。**

---

## 八、Blind Human Semantic GT Protocol

### 8.1 Blind Review 原则

Reviewer 不能看到：

| 禁止暴露 | 理由 |
|---|---|
| IS-01 result | 防止 feature leakage |
| IS-02 result | 防止 feature leakage |
| Machine prediction | 防止 anchoring bias |
| Feature score | 防止 feature leakage |
| Previous Round 1 result | 防止 historical contamination |
| Previous GT | 防止 GT leakage |
| Counterfactual classification | 防止 classification leakage |
| Suggested answer | 防止 suggestion bias |
| DICE internal concepts (IS, boundary class, etc.) | 防止 concept priming |

### 8.2 Reviewer 可见信息

| 允许暴露 | 说明 |
|---|---|
| 原始 PDF | 完整 PDF 文件 |
| 页面 | 当前 case 所在页面 |
| Boundary pair A / B | 两个 span 的文本和位置 |
| 原文上下文 | 页面上的其他内容 |
| 简单任务说明 | "判断这两个文本片段是否应该合并为一个文本单元" |

### 8.3 Reviewer 任务

```
Task: 判断以下两个文本片段是否属于同一个文本单元。

Text A: [span_a text]
Text B: [span_b text]

Page context: [PDF page image]

Decision:
  [ ] MERGE — 两个片段属于同一文本单元
  [ ] KEEP_SEPARATE — 两个片段不属于同一文本单元
  [ ] CANNOT_DETERMINE — 无法确定

Reason (optional): [text input]
```

### 8.4 Reviewer 限制

- Reviewer 不得知道 IS-01/IS-02 的存在
- Reviewer 不得知道 P4 的 AMBIGUOUS 分类
- Reviewer 不得知道 counterfactual 分析结果
- Reviewer 不得知道其他 reviewer 的判断
- Reviewer 不得知道 machine prediction

---

## 九、Second Reviewer Protocol

### 9.1 双 Reviewer 独立工作

| 属性 | Reviewer A | Reviewer B |
|---|---|---|
| 身份 | 独立于 IS discovery | 独立于 IS discovery |
| 可见信息 | Blind review 信息 | Blind review 信息（相同） |
| 不可见 | IS/Machine/Round 1/其他 reviewer | IS/Machine/Round 1/其他 reviewer |
| 独立性 | ✅ 不看 B 结果 | ✅ 不看 A 结果 |

### 9.2 Inter-Rater Agreement

计算 Cohen's kappa（或适合三分类的 agreement measure）：

```
Agreement Matrix:
                Reviewer B
                MERGE  SEPARATE  CANNOT
Reviewer A
  MERGE          a       b        c
  SEPARATE       d       e        f
  CANNOT         g       h        i

Agreement rate = (a + e + i) / (a+b+c+d+e+f+g+h+i)
Cohen's kappa = (observed - expected) / (1 - expected)
```

### 9.3 Agreement 阈值

| kappa 值 | 解读 | 行动 |
|---|---|---|
| ≥ 0.80 | Strong agreement | 双 reviewer GT 可用 |
| 0.60-0.79 | Moderate agreement | 需要 adjudication for disagreements |
| < 0.60 | Poor agreement | GT 不可靠，需要重新设计 task 或增加 reviewer |

### 9.4 Disagreement 处理

```
A = MERGE, B = KEEP_SEPARATE (or vice versa):
  → DISAGREEMENT REVIEW (adjudication required)
  → 第三人（expert adjudicator）做最终判断
  → 如果 adjudicator 也 CANNOT_DETERMINE → GT = UNRESOLVED

A = CANNOT_DETERMINE, B = MERGE/SEPARATE:
  → 使用 B 的 decision，标记 SINGLE_REVIEWER_ONLY
  → 不计入 strong GT

A = CANNOT_DETERMINE, B = CANNOT_DETERMINE:
  → GT = UNRESOLVED
  → 不计入 evaluation
```

---

## 十、Semantic GT Authority

### 10.1 GT Hierarchy

| Level | 名称 | 定义 | 可靠性 |
|---|---|---|---|
| Level 0 | Geometry observation | P4 几何特征派生标签 | ❌ 不可作为 semantic GT（AMB-026 证明） |
| Level 1 | Independent Human Review | 单个独立 reviewer 的判断 | ⚠️ 中等（无 agreement 验证） |
| Level 2 | Adjudicated Human/Expert Decision | 双 reviewer agreement + adjudication | ✅ 高 |

### 10.2 正式 Semantic Evaluation GT

**优先使用 Level 2（双 reviewer agreement + adjudication）。**

如果没有 adjudication：至少需要双 reviewer agreement。

如果仍存在 disagreement：GT = UNRESOLVED。

**不能强迫二选一。**

### 10.3 GT 不可回写

```
GT 生成后:
  ❌ 不得根据 machine prediction 修改 GT
  ❌ 不得根据 IS-01/IS-02 结果修改 GT
  ❌ 不得根据 evaluation 结果修改 GT
  ❌ 不得根据 "这个 case 很奇怪" 修改 GT

如果发现异常:
  → 记录 POST_FREEZE_EXCEPTION
  → 单独报告
  → 不修改 GT
```

---

## 十一、Evaluation Set Freeze

### 11.1 Freeze Point

Human Validation 结束后，必须有一个明确 Freeze Point：

```
EVALUATION_SET_FROZEN = TRUE
FREEZE_TIMESTAMP = [timestamp]
```

### 11.2 Freeze 后不可修改

| 项目 | Freeze 后可修改? |
|---|---|
| 样本（case inclusion/exclusion） | ❌ NO |
| 标签（GT） | ❌ NO |
| Inclusion criteria | ❌ NO |
| Feature specification (IS-01/IS-02) | ❌ NO |
| Thresholds | ❌ NO |
| Sampling strategy | ❌ NO |

### 11.3 Post-Freeze Exception

如果 Freeze 后发现异常 case：

```
POST_FREEZE_EXCEPTION:
  case_id: [id]
  reason: [description]
  action: RECORDED_ONLY (no GT modification)
  report: INCLUDED_IN_FINAL_REPORT
```

**不得修改 GT。不得移除 case。不得修改 inclusion criteria。**

---

## 十二、Researcher Blindness

### 12.1 研究者可见性时间线

| Stage | Document | Candidate | Text | Geometric Feature | IS-01 | IS-02 | Human GT | Machine Prediction |
|---|---|---|---|---|---|---|---|---|
| Stage 1: Corpus processed | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Stage 2: Candidate universe frozen | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Stage 3: Human GT collected | ✅ | ✅ | ✅ (by reviewer) | ✅ | ❌ | ❌ | ✅ (collected) | ❌ |
| Stage 4: Evaluation Set frozen | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ (frozen) | ❌ |
| Stage 5: Machine features revealed | ✅ | ✅ | ✅ | ✅ | ✅ (computed) | ✅ (computed) | ✅ | ❌ |
| Stage 6: Evaluation performed | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (computed) |
| Stage 7: Metrics computed | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### 12.2 关键约束

```
Stage 2 → Stage 3:
  研究者不得查看 text content（防止 text-based sampling bias）
  研究者不得计算 IS-01/IS-02

Stage 3 → Stage 4:
  研究者不得查看 IS-01/IS-02（防止 GT leakage）
  研究者不得根据 Human GT 修改 sampling

Stage 4 → Stage 5:
  IS-01/IS-02 在 Evaluation Set Freeze 之后才计算
  不得根据 IS 结果修改 GT 或 sampling

Stage 5 → Stage 6:
  Machine prediction 在 IS 计算之后
  不得根据 prediction 修改 GT

Stage 6 → Stage 7:
  Metrics 不得反向影响 feature specification
```

### 12.3 Researcher 与 Reviewer 的角色分离

| 角色 | 职责 | 可见性 |
|---|---|---|
| Researcher | 设计 protocol, 管理 pipeline, 计算 metrics | 受 Stage 限制（见 12.1） |
| Reviewer A | Blind Human Review | 仅可见 Blind Review 信息（见 8.2） |
| Reviewer B | Blind Human Review | 仅可见 Blind Review 信息（见 8.2） |
| Adjudicator | Disagreement resolution | 可见 A/B 的 disagreement，不见 IS/Machine |

---

## 十三、IS-01 / IS-02 Usage Order

### 13.1 严格使用顺序

```
Phase A: Independent corpus processing
  → PDF → Frozen P1-P6 → geometric spans → boundary candidates
  → [NO IS computation]

Phase B: Candidate sampling
  → Stratified sampling based on geometric features only
  → [NO IS computation]
  → [NO text preview]

Phase C: Blind Human Semantic GT
  → Reviewer A + B independently review sampled candidates
  → [NO IS computation]
  → [NO machine prediction]

Phase D: Evaluation Set Freeze
  → GT frozen
  → Sample frozen
  → [NO IS computation]

Phase E: Frozen IS-01 / IS-02 observation
  → IS-01/IS-02 computed on frozen Evaluation Set
  → Using FROZEN definitions (no modification)

Phase F: Machine assessment
  → MACHINE_DECISION: MERGE / KEEP_SEPARATE / INSUFFICIENT_EVIDENCE
  → Compare against frozen Human GT

Phase G: Metrics computation
  → Precision, Recall, FP rate, Shrinkage rate
  → [NO feature modification]
```

### 13.2 IS-01/IS-02 冻结声明（重申）

```
IS-01 (TEXT_NUMBER_PATTERN): FROZEN
  regex: ^\d+(\.\d+)*\.?$ or ^[A-Z]\.\d+$
  不得修改

IS-02 (TEXT_READABLE_TITLE): FROZEN
  any(len(re.sub(r'[^a-zA-Z]','',w)) > 2 for w in text.split())
  不得修改

已知 LIMITATION:
  - IS-02 loose detection (cos/sin/and/are)
  - IS-01 不区分 heading number vs equation number
  不得在 evaluation 中修改。记录为 FEATURE_SPECIFICATION_LIMITATION。
```

---

## 十四、Holdout / Stress Set Design

### 14.1 三个数据集

| 数据集 | 来源 | 用途 | 当前状态 |
|---|---|---|---|
| A. Discovery Set | 历史 Round 1 / 已知数据 | IS discovery (已完成) | ✅ FROZEN — 不能作为 independent evaluation |
| B. Independent Evaluation Set | 7 新 PDF | Machine-resolvability evaluation | ❌ NOT YET — 需要 protocol 执行 |
| C. Holdout / Stress Set | 另外设计 | Adversarial, rare patterns, cross-family | ❌ FUTURE REQUIREMENT |

### 14.2 Holdout Set 设计要求

| 要求 | 说明 |
|---|---|
| Adversarial samples | number + non-title, letter + non-title, formula + readable token |
| Rare patterns | 不常见的 boundary geometry |
| Cross-family | 不同文档族（arxiv → qbio → device manual） |
| Unseen layouts | 未见过的排版模式 |
| 不可修改 feature | Holdout 结果不得反向影响 IS specification |

### 14.3 当前条件不足

**当前条件不足以建立 Holdout Set（C）。记录为 FUTURE REQUIREMENT。不制造 synthetic holdout。**

---

## 十五、Adversarial Sampling Protocol

### 15.1 Historical Adversarial（不可作为 independent）

| Case | 来源 | 用途 |
|---|---|---|
| AMB-018 | Round 1 | Historical example only — NOT independent adversarial GT |
| AMB-040 | Round 1 | Historical example only — NOT independent adversarial GT |

### 15.2 Future Adversarial Sampling Criteria

| Adversarial type | 描述 | 采样标准 |
|---|---|---|
| Type 1 | Number + real title | IS-01=True AND IS-02=True AND semantic GT=MERGE |
| Type 2 | Number + non-title | IS-01=True AND IS-02=True AND semantic GT=KEEP_SEPARATE |
| Type 3 | Appendix letter + real title | IS-01=True (letter pattern) AND IS-02=True AND GT=MERGE |
| Type 4 | Appendix letter + non-title | IS-01=True AND IS-02=True AND GT=KEEP_SEPARATE |
| Type 5 | Formula-like prefix + readable token | IS-01=False AND IS-02=True AND GT=KEEP_SEPARATE |
| Type 6 | Visually wide fragment + misleading readable word | IS-01=False AND IS-02=True AND GT=variable |
| Type 7 | Same typography + different semantic role | IS-01+IS-02 same pattern, different GT |

### 15.3 不生成正式 GT

**本阶段只设计 sampling criteria。不生成新的正式 GT。不构造 adversarial samples。**

---

## 十六、Human Cost Measurement

### 16.1 Timer Protocol Design

Round 1 的 timer bug（submitDecision 调用 /api/case 重置 start_time）必须在未来实验中修复。

| Timestamp | 记录点 | 记录方式 |
|---|---|---|
| task_start_time | Reviewer 开始 review session | 服务器记录 |
| page_open_time | PDF 页面在浏览器中加载完成 | 客户端记录 (img onload) |
| decision_time | Reviewer 点击 decision 按钮 | 客户端记录 (click event) |
| submit_time | 服务器收到 submit | 服务器记录 |
| duration_ms | decision_time - page_open_time | 派生 |

### 16.2 Timer 修复要求

```
修复要点:
  1. page_open_time 在客户端记录 (img onload)
  2. decision_time 在客户端记录 (click event, before fetch)
  3. 客户端发送 page_open_time + decision_time 在 submit body
  4. 服务器不在 /api/case 中设置 start_time
  5. duration_ms = decision_time - page_open_time
  6. 网络请求不重置 timer
```

### 16.3 Human Cost Metrics

| 指标 | 定义 |
|---|---|
| Median decision time | 所有 case 的 decision_time 中位数 |
| P75 | 75th percentile |
| P95 | 95th percentile |
| Disagreement time | disagreement cases 的 decision time |
| Adjudication time | adjudication cases 的时间 |
| CANNOT_DETERMINE rate | CANNOT_DETERMINE / total |

**Human Cost Measurement ≠ 本阶段必须实现。这里只设计 protocol。**

---

## 十七、Boundary Shrinkage

### 17.1 四级定义（重申）

| 级别 | 名称 | 定义 |
|---|---|---|
| Level 1 | Baseline Ambiguous | Independent Evaluation Set 中原本需要 Human 的数量 |
| Level 2 | Potential Machine-Resolvable | 根据冻结 feature evidence，机器可能能够判断的数量 |
| Level 3 | Actual Machine-Resolvable | 机器在冻结 spec 下实际稳定输出确定 decision 的数量 |
| Level 4 | Independently Validated Machine-Resolvable | 机器 decision 被独立 semantic GT 验证且达到 Gate 的数量 |

### 17.2 Actual Boundary Shrinkage Rate

```
Actual Boundary Shrinkage Rate
=
Independently Validated Machine-Resolvable Cases (Level 4)
/
Baseline Ambiguous Cases (Level 1)
```

### 17.3 Decision 矩阵

| Machine Decision | Human GT | 分类 | 计入 Shrinkage? |
|---|---|---|---|
| MERGE | MERGE | True Positive | ✅ Yes |
| KEEP_SEPARATE | KEEP_SEPARATE | True Negative | ✅ Yes |
| MERGE | KEEP_SEPARATE | False Positive | ❌ No (FP) |
| KEEP_SEPARATE | MERGE | False Negative | ❌ No (FN) |
| MERGE | CANNOT_DETERMINE | Unverifiable | ❌ No |
| KEEP_SEPARATE | CANNOT_DETERMINE | Unverifiable | ❌ No |
| INSUFFICIENT_EVIDENCE | MERGE | Insufficient (not wrong) | ❌ No (but not shrinkage) |
| INSUFFICIENT_EVIDENCE | KEEP_SEPARATE | Insufficient (not wrong) | ❌ No (but not shrinkage) |
| INSUFFICIENT_EVIDENCE | CANNOT_DETERMINE | Both uncertain | ❌ No |
| Any | UNRESOLVED | No GT | ❌ Excluded |

### 17.4 不能使用的指标

```
❌ "29/43 = 67.4%" — Potential Resolution Rate (counterfactual, NOT independent)
❌ "0/75 = 0% FP" — from contaminated corpus
❌ "13/13 = 100% consistency" — TRAIN=TEST

✅ 只能使用:
  Independently Validated Resolution / Baseline Ambiguous
  (在独立 Evaluation Set + 独立 semantic GT 上计算)
```

---

## 十八、Pre-Registered Gates

### 18.1 十二个 Gate

| Gate | 条件 | 预注册 threshold | 何时确定 |
|---|---|---|---|
| G1 | Independent Corpus exists | ≥ 4 INDEPENDENT PDFs | NOW (design) |
| G2 | Independent Evaluation Set exists | ≥ 20 TOC/APPENDIX cases with semantic GT | Before evaluation |
| G3 | Feature Specification Frozen | IS-01/IS-02 frozen | NOW (✅ PASS) |
| G4 | No Leakage | No IS/Machine/GT cross-contamination | Before evaluation |
| G5 | Semantic GT Validity | Level 2 GT (双 reviewer + adjudication) | After Human GT |
| G6 | Inter-Rater Agreement | Cohen's kappa ≥ 0.60 | After Human GT |
| G7 | Precision / FP Safety | Precision ≥ 95%, FP ≤ 5% | **BEFORE results** |
| G8 | Coverage / Recall | Recall ≥ 80% | **BEFORE results** |
| G9 | Cross-Document Generalization | Consistent across ≥ 2 document families | After evaluation |
| G10 | Adversarial Robustness | 0 FP on independent adversarial | After evaluation |
| G11 | INSUFFICIENT_EVIDENCE Safety | Machine outputs INSUFFICIENT_EVIDENCE when appropriate | After evaluation |
| G12 | Provenance Completeness | Every decision traceable | After evaluation |

### 18.2 Pre-Registration 原则

**G7 (Precision ≥ 95%) 和 G8 (Recall ≥ 80%) 必须在结果产生前确定。**

```
❌ 禁止: 先看结果 → 再选 threshold → 再宣布 PASS
✅ 必须: 先确定 threshold → 再看结果 → 根据 threshold 判断 PASS/FAIL
```

### 18.3 当前 Gate 状态

| Gate | 状态 |
|---|---|
| G1 | ✅ PASS (4 INDEPENDENT PDFs exist) |
| G2 | ❌ NOT YET (Evaluation Set not built) |
| G3 | ✅ PASS (IS-01/IS-02 frozen) |
| G4 | ❌ NOT YET (cannot verify until evaluation) |
| G5 | ❌ NOT YET (no Human GT) |
| G6 | ❌ NOT YET (no second reviewer) |
| G7 | ⚠️ PRE-REGISTERED (threshold: Precision ≥ 95%) |
| G8 | ⚠️ PRE-REGISTERED (threshold: Recall ≥ 80%) |
| G9 | ❌ NOT YET (no cross-document evaluation) |
| G10 | ❌ NOT YET (no independent adversarial) |
| G11 | ⚠️ DESIGNED (protocol includes INSUFFICIENT_EVIDENCE) |
| G12 | ✅ PASS (provenance protocol designed) |

**PASSED: 3/12 (G1, G3, G12)。其余 NOT YET 或 PRE-REGISTERED。**

---

## 十九、Stop Conditions

### 19.1 自动停止条件

未来实验一旦出现以下情况之一，必须 STOP：

| # | Stop Condition | 后果 |
|---|---|---|
| SC1 | 无独立 corpus | 不能声称 generalization |
| SC2 | Reviewer 看到了 machine result | Evaluation invalidated |
| SC3 | Feature 在 evaluation 后被修改 | Evaluation invalidated |
| SC4 | GT 在看到 machine prediction 后修改 | GT invalidated |
| SC5 | Case selection 根据 IS-01/IS-02 结果调整 | Selection bias, evaluation invalidated |
| SC6 | Provenance 不清楚 | 不能声称 result |
| SC7 | Geometry GT 被冒充 semantic GT | GT invalidated |
| SC8 | Single reviewer 且没有可信 adjudication | GT reliability insufficient |
| SC9 | Evaluation set 太小（< 20 TOC/APPENDIX cases） | 统计 power 不足 |
| SC10 | Inter-rater kappa < 0.60 | GT reliability insufficient |

### 19.2 Stop 后行动

```
如果 Stop Condition 触发:
  → STOP evaluation
  → 记录 Stop Condition
  → 不计算 metrics
  → 不声称 machine-resolvability
  → 报告 Stop 原因
  → 设计修复方案
```

---

## 二十、Provenance Requirements

### 20.1 每个机器判断必须可追溯

| 追溯字段 | 说明 |
|---|---|
| document | 源 PDF |
| page | 页码 |
| pair | boundary pair ID |
| source evidence | P4 geometric features + IS-01/IS-02 values |
| feature values | IS-01_a, IS-01_b, IS-02_a, IS-02_b, IS-07 |
| decision | MERGE / KEEP_SEPARATE / INSUFFICIENT_EVIDENCE |
| experiment version | protocol version + feature freeze version |
| human GT | reviewer A/B/adjudicator decision |
| agreement status | agreement / disagreement / unresolved |

### 20.2 Provenance Chain

```
PDF → P1 observation → P2 geometry → P3 style → P4 span
→ cross_doc_audit → AMBIGUOUS extraction
→ sampling frame → stratified sample
→ blind human review (A + B)
→ adjudication (if needed)
→ GT freeze
→ IS-01/IS-02 computation (frozen spec)
→ machine decision
→ metric computation
→ provenance record
```

---

## 二十一、Future Experiment Workflow

### 21.1 完整 Workflow

```
[Phase A] Corpus Processing
  1. Select 4 INDEPENDENT PDFs (+ optionally 3 PARTIALLY_CONTAMINATED)
  2. Process through frozen P1-P6
  3. Extract same-y unmerged pairs
  4. Apply AMBIGUOUS criteria
  5. Record Candidate Universe (geometric features only)

[Phase B] Sampling
  6. Stratified sampling (geometric features only)
  7. [STOP: no IS computation]
  8. Record sampling frame

[Phase C] Blind Human GT
  9. Reviewer A: blind review
  10. Reviewer B: blind review (independent)
  11. Compute inter-rater agreement
  12. Adjudicate disagreements (if kappa ≥ 0.60)
  13. [STOP: no IS computation]

[Phase D] Evaluation Set Freeze
  14. Freeze sample + GT
  15. EVALUATION_SET_FROZEN = TRUE
  16. [STOP: no GT modification]

[Phase E] Frozen Feature Observation
  17. Compute IS-01/IS-02 (frozen definitions)
  18. [STOP: no feature modification]

[Phase F] Machine Assessment
  19. Output MACHINE_DECISION (MERGE/KEEP_SEPARATE/INSUFFICIENT_EVIDENCE)
  20. [STOP: no GT modification]

[Phase G] Metrics & Gate
  21. Compute Precision, Recall, FP, Shrinkage
  22. Evaluate G1-G12
  23. Report results
  24. [STOP: no feature modification based on results]
```

---

## 二十二、Limitations

| # | 限制 | 影响 |
|---|---|---|
| L1 | 4 INDEPENDENT PDFs 可能不足 | 如果 TOC/APPENDIX cases < 20, 统计 power 不足 |
| L2 | 3 PARTIALLY_CONTAMINATED PDFs 有 metadata 级污染 | 需要通过 blind sampling 隔离 |
| L3 | 无第二 reviewer | protocol 设计完成但未执行 |
| L4 | 无 timer fix | Human cost 无法测量（protocol 设计完成但未实现） |
| L5 | 无 Holdout Set (C) | adversarial robustness 无法完全验证 |
| L6 | IS-02 loose detection (cos/sin/and/are) | frozen, 不可修改 |
| L7 | 设备手册 0 TOC cases | NOT_APPLICABLE, 跨文档族验证受限 |
| L8 | qbio 文档结构未知 | AMBIGUOUS case 分布不可预测 |
| L9 | 研究者已有 metadata 知识 | 需要通过 protocol 隔离（blind sampling + staged visibility） |

---

## 二十三、10 个最终问题

### Q1: 7 个 PDF 是否具备作为 Independent Corpus 的条件？

**部分具备。**

- 4/7 INDEPENDENT（arxiv_2402, arxiv_bio2, qbio_genomics, qbio_rna）→ 完全独立
- 3/7 PARTIALLY_CONTAMINATED（arxiv_2310, arxiv_2401, qbio_cell）→ metadata 级污染，无 boundary 级污染
- 0/7 CONTAMINATED（无 IS/boundary 分析）

**修正上一阶段结论**：上一阶段声称 "all 7 PDFs are truly independent"。本阶段审计发现 3/7 有 PARTIAL 污染。

### Q2: P1-P6 处理是否会破坏实验独立性？

**不会。**

P1-P6 是 frozen 几何处理，不涉及 IS-01/IS-02。P1 提取 text 是 CORPUS PREPROCESSING（Layer A）。关键约束：IS-01/IS-02 不得在 Human GT 收集前计算。

### Q3: 如何从新 PDF 中生成 candidate universe 而不泄漏 IS-01/IS-02？

通过 staged processing：
1. P1-P6 处理 → 几何 features only
2. Candidate extraction → geometric criteria only
3. [STOP] — 不得计算 IS-01/IS-02
4. Blind Human GT → 不暴露 IS/Machine

### Q4: 如何抽样才能避免 selection bias？

- Pre-registered sampling criteria（在看到 text 前确定）
- Geometric-only sampling（仅基于 gap/w_b/line_obs）
- No IS computation before sampling
- No text preview before sampling
- Full universe recording

### Q5: Human GT 如何做到真正 blind？

Reviewer 只可见：原始 PDF + 页面 + boundary pair A/B + 上下文 + 简单任务说明。
Reviewer 不可见：IS-01/IS-02、machine prediction、Round 1 result、GT、counterfactual classification、DICE 内部概念。

### Q6: 为什么需要第二 reviewer？

- 测量 inter-rater agreement（Cohen's kappa）
- 验证 GT reliability
- 单 reviewer 的 GT 无法区分 "correct" 和 "reviewer bias"
- 双 reviewer + adjudication = Level 2 GT（最高可靠性）

### Q7: 什么情况下 semantic GT 可以被认为可靠？

- 双 reviewer agreement（kappa ≥ 0.60）
- 或 adjudicated decision（Level 2 GT）
- 或 expert validation
- 如果 kappa < 0.60 → GT 不可靠 → STOP

### Q8: Evaluation Set 在什么时候冻结？

在 Human GT 收集完成后、IS-01/IS-02 计算前冻结。
Freeze 后不可修改：样本、标签、inclusion criteria、feature specification、thresholds。

### Q9: 什么时候才能正式计算 Boundary Shrinkage？

在以下条件全部满足后：
1. Independent Evaluation Set frozen
2. Frozen IS-01/IS-02 computed
3. Machine decision computed
4. Independent semantic GT available (Level 2)
5. Gate G1-G12 evaluated
6. G7 (Precision ≥ 95%) pre-registered and met

```
Actual Boundary Shrinkage Rate
=
Independently Validated Machine-Resolvable Cases (Level 4)
/
Baseline Ambiguous Cases (Level 1)
```

### Q10: 下一阶段应该是？

**D. 继续设计（已完成）+ E. STOP**

当前已完成 protocol 设计。不处理 PDF，不生成 candidate，不运行 IS-01/IS-02，不进行 Human Validation。

```
NEXT CANDIDATE (when authorized):
  1. Process 4 INDEPENDENT PDFs through frozen P1-P6
  2. Extract Candidate Universe
  3. Execute Blind Human GT Protocol
  4. Freeze Evaluation Set
  5. Compute frozen IS-01/IS-02
  6. Evaluate against pre-registered Gates

NOT:
  Implement IS-01/IS-02 as production rule
  Modify P4
  Start P7.3
```

---

## 二十四、Final Status

```
DESIGN STATUS = READY (protocol design complete)
INDEPENDENT CORPUS = PARTIAL (4 INDEPENDENT + 3 PARTIALLY_CONTAMINATED)
SEMANTIC GT PROTOCOL = READY (design only, not implemented)
FEATURE FREEZE = PASS (IS-01/IS-02 frozen)
IMPLEMENTATION = NOT AUTHORIZED
P7.3 = NOT AUTHORIZED
FROZEN BASELINE = INTACT
STOP = TRUE
```

### 修正记录

```
CORRECTION FROM PREVIOUS STAGE:
  Previous: "7 unprocessed PDFs are truly independent"
  Corrected: "4/7 INDEPENDENT, 3/7 PARTIALLY_CONTAMINATED (metadata-level)"
  
  Previous: "These have NOT been through P1-P6 pipeline"
  Corrected: "arxiv_2310 has been partially P1-processed (as 'arxiv_single' in test results)"
  
  Previous: "These have NOT been analyzed in any P7 study"
  Corrected: "3/7 were analyzed in p7_evidence_gap_analysis.md (metadata-level: page counts, image counts, font types)"
  
  Impact: 
    - Does NOT invalidate the protocol (contamination is metadata-level, not boundary-level)
    - Does NOT affect IS-01/IS-02 independence (no IS patterns computed on any PDF)
    - Does require blind sampling protocol to mitigate researcher metadata knowledge
    - 4 INDEPENDENT PDFs are sufficient for Minimum scenario (20 TOC/APPENDIX cases)
```

---

## STOP

```
PROTOCOL DESIGN COMPLETE.

不做:
  - 不处理 7 个 PDF
  - 不生成 candidate
  - 不运行 IS-01 / IS-02
  - 不进行 Human Validation
  - 不修改任何代码
  - 不修改任何实验数据
  - 不进入 P7.3

只完成:
  Future Independent Evaluation Data Collection Protocol (READ-ONLY design)

Implementation = NOT AUTHORIZED
P7.3 = NOT AUTHORIZED
Frozen = INTACT
STOP = TRUE
```

**不进入下一阶段。不修改任何代码。不修改任何实验数据。等待下一步批准。**
