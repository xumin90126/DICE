# Independent Machine-Resolvability Experiment
## Experimental Design & Data Isolation Audit

> READ-ONLY RESEARCH / DESIGN。不修改任何 frozen/production/source 文件。不实施。不进入 P7.3。

---

## Executive Summary

```
DATA INDEPENDENCE = PARTIAL
  - 20/43 cases: DIRECTLY CONTAMINATED (IS-01/IS-02 discovery source)
  - 23/43 cases: INDIRECTLY CONTAMINATED (counterfactual analysis)
  - 0/43 cases: evaluation eligible
  - 7 unprocessed PDFs: truly independent but need pipeline processing
  - 0 semantic GT exists for any case

FEATURE FREEZE = PASS
  - IS-01 / IS-02 frozen as experimental definitions
  - No modification allowed during evaluation

SEMANTIC GT = NOT_AVAILABLE
  - Only geometry-based GT exists
  - AMB-026 proved geometry GT ≠ semantic GT
  - No independent Human validation performed

DESIGN STATUS = READY (design complete, data collection needed)
IMPLEMENTATION = NOT AUTHORIZED
P7.3 = NOT AUTHORIZED
Frozen = INTACT

KEY FINDING:
  当前只能证明 feasibility hypothesis，
  不能证明 independent machine-resolvability。
  不存在可直接使用的 Independent Evaluation Set。
  需要先收集新的独立数据。

NEXT STEP:
  Future Independent Evaluation Data Collection Protocol
  (NOT: implement rule)
```

---

## 一、Research Question

### 1.1 不是研究什么

不研究："IS-01 + IS-02 能不能匹配？"——counterfactual study 已给出 29/43 = 67.4% POTENTIALLY_MACHINE_RESOLVABLE。

不研究："Human 能不能解决 ambiguity？"——Round 1 已给出 INITIAL FEASIBILITY = SUPPORTED。

### 1.2 研究什么

研究："我们是否真的拥有一个独立 Evaluation Set，可以验证 IS-01 + IS-02 是否具有跨样本、跨文档的机器可判定性？"

以及："在数据独立性成立的前提下，如何设计一个可复现、可审计的 Independent Machine-Resolvability Experiment？"

### 1.3 核心区分

```
POTENTIALLY_MACHINE_RESOLVABLE (counterfactual study)
  ≠
MACHINE_RESOLVABLE (independent evaluation)

Potential Shrinkage
  ≠
Actual Shrinkage

Feasibility Hypothesis
  ≠
Independently Validated Machine-Resolvability
```

---

## 二、Current Evidence

### 2.1 已有发现链

| 阶段 | 产出 | 结论 |
|---|---|---|
| Round 1 Human Boundary Review | 20/43 cases, 95% accuracy | INITIAL FEASIBILITY = SUPPORTED |
| Boundary Semantics Convergence | 3-layer boundary definition | Human provides Layer 2/3 evidence |
| Information Source Gap Analysis | IS-01~IS-10 taxonomy | Gap is Category B (machine-observable) + C (semantic) |
| TOC Feasibility Study | 29/43 CF-A, 0 FP on corpus | PROMISING MACHINE-RESOLVABLE (but TRAIN=TEST) |

### 2.2 当前 29/43 = 67.4% 的性质

```
29/43 = 67.4% 是:
  POTENTIAL RESOLUTION RATE (counterfactual estimate)

不是:
  ACTUAL BOUNDARY SHRINKAGE
  INDEPENDENTLY VALIDATED MACHINE-RESOLVABILITY
  PROVEN GENERALIZATION
```

### 2.3 为什么不能直接使用 29/43

IS-01 / IS-02 的发现来源与 Round 1 Human Cases 存在数据重叠：

```
Round 1 (20 cases)
  → 分析 Human 使用的信息源
  → 发现 IS-01 (number pattern) + IS-02 (readable title)
  → 在同 20 cases 上验证 IS pattern consistency
  → 在全 43 cases 上做 counterfactual classification
  → 得到 29/43 CF-A

Discovery Set = Evaluation Set → TRAIN = TEST → 循环推理
```

---

## 三、Data Provenance Audit

### 3.1 全 corpus 数据源清单

| 文档 | PDF 来源 | 已处理? | 页数 | boundary pairs | same-y unmerged | AMBIGUOUS | AMBIGUOUS mode 分布 |
|---|---|---|---|---|---|---|---|
| arxiv_toc | arxiv_bio.pdf (TOC page) | ✅ | 1 | 74 | 47 | 22 | TOC_NUM_TITLE=20, APPENDIX=2 |
| arxiv_2307 | arxiv_2307.07845.pdf | ✅ | 3 | 706 | 338 | 17 | TOC_NUM_TITLE=4, FORMULA=13 |
| arxiv_bio_body | arxiv_bio.pdf (body pages) | ✅ | 4 | 973 | 23 | 4 | TOC_NUM_TITLE=3, BODY_CONT=1 |
| RA101 | RA101 device manual | ✅ | 3 | 80 | 0 | 0 | N/A |
| RM501-P4 | RM501 device manual | ✅ | 2 | 151 | 2 | 0 | N/A |
| E804 | E804 device manual | ✅ | 2 | 54 | 1 | 0 | N/A |
| C216 | C216 device manual | ✅ | 3 | 72 | 0 | 0 | N/A |
| DC201 | DC201 device manual | ✅ | 3 | 145 | 0 | 0 | N/A |
| **总计 (已处理)** | | | **21** | **2255** | **411** | **43** | |

### 3.2 未处理 PDF 清单（真正独立数据源）

| PDF | 大小 | 类型 | 已处理? | 已分析? | 独立性 |
|---|---|---|---|---|---|
| arxiv_2310.16825.pdf | 27MB | arxiv physics | ❌ | ❌ | ✅ INDEPENDENT |
| arxiv_2401.00047.pdf | 370KB | arxiv | ❌ | ❌ | ✅ INDEPENDENT |
| arxiv_2402.18619.pdf | 951KB | arxiv | ❌ | ❌ | ✅ INDEPENDENT |
| arxiv_bio2.pdf | 3MB | arxiv biology | ❌ | ❌ | ✅ INDEPENDENT |
| qbio_cell.pdf | 5MB | quantitative biology | ❌ | ❌ | ✅ INDEPENDENT |
| qbio_genomics.pdf | 4.6MB | genomics | ❌ | ❌ | ✅ INDEPENDENT |
| qbio_rna.pdf | 2.4MB | RNA biology | ❌ | ❌ | ✅ INDEPENDENT |

**这 7 个 PDF 是当前唯一真正独立的数据源。但它们尚未经过 P1-P6 pipeline 处理，不能直接使用。**

### 3.3 数据 provenance 链

```
PDF documents (8 processed)
    ↓ P1 extraction (observation with text)
    ↓ P2 geometry (bbox, gap, dy)
    ↓ P3 style (font, size, style_sig)
    ↓ P4 span (merge/block/ambiguous)
    ↓ cross_doc_audit_collect.py
    ↓ cross_doc_audit_raw.json (762 same-y pairs across 8 docs)
    ↓ cross_doc_audit_supplement.json (arxiv_bio_body additional)
    ↓ extract_ambiguous.py
    ↓ ambiguous_cases_all.json (43 AMBIGUOUS cases)
    ↓ select_round1.py
    ↓ round1_cases.json (20 selected)
    ↓ Human review (boundary_review_server.py + HTML)
    ↓ round1_results.json (20 decisions)
    ↓ Information Source analysis
    ↓ IS-01 / IS-02 / IS-07 discovery (from 20 reviewed cases)
    ↓ counterfactual analysis (on all 43)
    ↓ TOC feasibility study (on 2255 pairs)
```

### 3.4 逐 case provenance（43 cases）

| Provenance Status | Case 数 | IS discovery | Counterfactual | Round 1 | Semantic GT | Evaluation Eligible |
|---|---|---|---|---|---|---|
| CONTAMINATED_DIRECT | 20 | ✅ used | ✅ used | ✅ reviewed | ❌ none | ❌ NO |
| CONTAMINATED_INDIRECT | 23 | ❌ not used | ✅ used | ❌ not reviewed | ❌ none | ❌ NO |
| INDEPENDENT | 0 | — | — | — | — | — |

**0/43 cases are evaluation eligible.**

详细 case-level provenance 见 `independent_machine_resolvability_experiment_matrix.json`。

---

## 四、Discovery / Development / Evaluation / Human Validation Split

### 4.1 DISCOVERY SET

| 属性 | 值 |
|---|---|
| 定义 | 允许用于发现哪些信息源可能重要、哪些 boundary class 值得研究、初步 feature hypothesis |
| 成员 | 20 Round 1 reviewed cases |
| 使用历史 | IS-01 / IS-02 从这些 case 的 text_a/text_b 内容中发现 |
| 污染类型 | DIRECT — feature discovery source |
| 可用于最终性能评价? | ❌ NO |
| 可用于 exploratory analysis? | ✅ YES (已完成) |

### 4.2 DEVELOPMENT SET

| 属性 | 值 |
|---|---|
| 定义 | 可以用于冻结实验定义前的 exploratory analysis（feature 可计算性、edge case、failure mode） |
| 成员 | 23 unreviewed AMBIGUOUS cases + 2255 boundary pairs |
| 使用历史 | counterfactual CF-A/B/C classification + false positive surface analysis |
| 污染类型 | INDIRECT — cases were seen and classified using IS-01/IS-02 |
| 可用于最终性能评价? | ❌ NO |
| 可用于 exploratory analysis? | ✅ YES (已完成) |
| 限制 | IS-01/IS-02 NOT derived from these cases, but researcher has seen their IS pattern values |

**为什么 23 unreviewed cases 不能作为 Independent Evaluation Set：**

1. **间接污染**：这 23 个 case 在 counterfactual analysis 中被分类为 CF-A/CF-B。研究者已经看到它们的 text_a、text_b 和 IS pattern 值。虽然 IS-01/IS-02 的定义不是从这些 case 推导的，但研究者的知识可能影响未来对 IS 定义修改的判断。

2. **同文档族**：这 23 个 case 来自与 Discovery Set 相同的 3 个文档（arxiv_toc, arxiv_2307, arxiv_bio_body）。同文档的数据可能共享排版模式，不能验证跨文档泛化。

3. **无语义 GT**：这 23 个 case 没有任何 Human decision 或 semantic expert annotation。只有 geometry-based GT（extract_ambiguous.py 的几何规则），而 AMB-026 已证明 geometry GT ≠ semantic GT。

4. **已知结果**：研究者已知这 23 个 case 中哪些是 CF-A（16 个 TOC/APPENDIX），哪些是 CF-B（7 个 FORMULA）。这种先验知识会污染任何"独立"评估。

### 4.3 INDEPENDENT EVALUATION SET

| 属性 | 值 |
|---|---|
| 定义 | 未参与 IS 发现、feature design、threshold tuning、case selection、adversarial construction、counterfactual classification 的数据 |
| 当前成员 | 0 cases |
| 候选来源 | 7 unprocessed PDFs |
| 状态 | NOT YET AVAILABLE — 需要先通过 P1-P6 pipeline 处理 |
| 独立性要求 | 未见过 text content、未计算过 IS pattern、无先验分类 |

**当前不存在可直接使用的 Independent Evaluation Set。**

### 4.4 HUMAN VALIDATION SET

| 属性 | 值 |
|---|---|
| 定义 | 由独立 Human / Expert 提供的 semantic Ground Truth |
| 当前成员 | 0 cases |
| 现有 Human data | 20 Round 1 decisions (reviewer_1) — 但这些是 Discovery Set 的一部分 |
| 独立性 | ❌ 不独立 — reviewer_1 的 decision 影响了 IS 发现 |
| 需要 | 第二 reviewer + 新文档的 Human annotation |

**Human Validation Set ≠ Independent Evaluation Set。** Evaluation Set 是样本来源；Human Validation 是 GT 生成机制。

---

## 五、Contamination Analysis

### 5.1 污染类型定义

| 类型 | 定义 | 影响 |
|---|---|---|
| DIRECT_CONTAMINATION | 数据直接参与了 IS 发现 / feature design | 不能用于任何 evaluation |
| INDIRECT_CONTAMINATION | 数据被 seen / classified 但未参与 IS 发现 | 不能用于 independent evaluation |
| COLLATERAL_CONTAMINATION | 同文档族数据，共享排版模式 | 跨文档泛化结论不可靠 |
| GT_CONTAMINATION | GT 来源与 evaluation 目标不独立 | GT 不能作为 evaluation truth |

### 5.2 逐 case 污染分析

#### 20 Round 1 reviewed cases (DIRECT_CONTAMINATION)

| 污染维度 | 状态 | 说明 |
|---|---|---|
| IS discovery | ✅ CONTAMINATED | IS-01/IS-02 从这些 case 的 text content 发现 |
| Feature design | ✅ CONTAMINATED | regex/word detection 规则受这些 case 影响 |
| Threshold tuning | ❌ NOT CONTAMINATED | 无 threshold 被调整 |
| Case selection | ✅ CONTAMINATED | adversarial AMB-018/040 从这些 case 构造 |
| Counterfactual | ✅ CONTAMINATED | 全部 20 被 CF 分类 |
| Human decision | ✅ CONTAMINATED | Human MERGE/SEPARATE 影响了 IS 发现 |

#### 23 unreviewed cases (INDIRECT_CONTAMINATION)

| 污染维度 | 状态 | 说明 |
|---|---|---|
| IS discovery | ❌ NOT CONTAMINATED | IS-01/IS-02 不是从这些 case 发现的 |
| Feature design | ❌ NOT CONTAMINATED | feature 规则未因这些 case 修改 |
| Threshold tuning | ❌ NOT CONTAMINATED | 无 threshold 被调整 |
| Case selection | ❌ NOT CONTAMINATED | 未用于 adversarial 构造 |
| Counterfactual | ✅ CONTAMINATED | 全部 23 被 CF-A/CF-B 分类 |
| Researcher knowledge | ✅ CONTAMINATED | 研究者已看到 text_a/text_b 和 IS pattern 值 |
| Same document family | ✅ CONTAMINATED | 来自相同 3 个 arxiv 文档 |
| Semantic GT | ❌ NOT AVAILABLE | 无 Human decision |

#### 2255 boundary pairs (COLLATERAL_CONTAMINATION)

| 污染维度 | 状态 | 说明 |
|---|---|---|
| False positive analysis | ✅ CONTAMINATED | 用于计算 IS-01+IS-02 FP rate (0/75) |
| Same documents | ✅ CONTAMINATED | 来自相同 8 个已处理文档 |

#### Geometry GT (GT_CONTAMINATION)

| 污染维度 | 状态 | 说明 |
|---|---|---|
| GT source | extract_ambiguous.py | 几何规则：w_a≥25 AND w_b≥25 AND len≥10 |
| GT independence | ❌ NOT INDEPENDENT | GT 基于几何特征，与 P4 几何信息同源 |
| Semantic validity | ❌ NOT VALID | AMB-026 证明 geometry GT ≠ semantic GT |

### 5.3 污染结论

```
CONTAMINATION ANALYSIS RESULT:

  Direct contamination:     20/43 cases (Round 1 = IS discovery source)
  Indirect contamination:   23/43 cases (counterfactual analysis, same docs)
  Collateral contamination: 2255 pairs (same document family)
  GT contamination:         43/43 cases (geometry GT, not semantic)

  Evaluation eligible:      0/43 cases

  CONCLUSION: No Independent Evaluation Set exists in current processed data.
```

---

## 六、Frozen IS-01 / IS-02 Experimental Definitions

### 6.1 冻结声明

```
FEATURE FREEZE = PASS

IS-01 and IS-02 are frozen as EXPERIMENTAL INFORMATION SOURCE DEFINITIONS.
They are NOT production rules.
They are NOT decision rules.
They are NOT machine boundary rules.
```

### 6.2 IS-01: TEXT_NUMBER_PATTERN (FROZEN)

| 属性 | 值 |
|---|---|
| 类型 | Experimental Information Source Definition |
| 输入 | P1 observation.text (string) |
| 输出 | boolean |
| 定义 | text 匹配编号模式 |
| 规则 | `re.match(r'^\d+(\.\d+)*\.?$', text.strip()) OR re.match(r'^[A-Z]\.\d+$', text.strip())` |
| 发现来源 | 20 Round 1 reviewed cases |
| 冻结时间 | 本阶段 |
| 修改权限 | ❌ NOT ALLOWED during evaluation |

### 6.3 IS-02: TEXT_READABLE_TITLE (FROZEN)

| 属性 | 值 |
|---|---|
| 类型 | Experimental Information Source Definition |
| 输入 | P1 observation.text (string) |
| 输出 | boolean |
| 定义 | text 包含可读字母词 |
| 规则 | `any(len(re.sub(r'[^a-zA-Z]', '', w)) > 2 for w in text.split())` |
| 发现来源 | 20 Round 1 reviewed cases |
| 冻结时间 | 本阶段 |
| 修改权限 | ❌ NOT ALLOWED during evaluation |

### 6.4 IS-07: VISUAL_TOC_CONTEXT (FROZEN)

| 属性 | 值 |
|---|---|
| 类型 | Experimental Information Source Definition |
| 输入 | P6 region type |
| 输出 | YES / NO / UNKNOWN |
| 定义 | 页面是否为 TOC 页 |
| 发现来源 | document metadata |
| 冻结时间 | 本阶段 |
| 修改权限 | ❌ NOT ALLOWED during evaluation |
| 注意 | IS-07 不是 CF-A 的必要条件（heading 在 body 页面也可被 IS-01+IS-02 识别） |

### 6.5 已知 FEATURE_SPECIFICATION_LIMITATION

| 限制 | 说明 | 修改权限 |
|---|---|---|
| IS-02 loose detection | "cos", "sin", "and", "are" (3 chars > 2) 匹配为 readable word | ❌ NOT ALLOWED — 记录为 limitation |
| IS-01 不区分 heading number vs equation number | "2.27" 匹配 number pattern 但是方程编号 | ❌ NOT ALLOWED — 记录为 limitation |
| IS-07 依赖 doc_id 而非 P6 region | 当前通过 doc_id 推断，未直接读取 P6 输出 | ❌ NOT ALLOWED — 记录为 limitation |

**如果发现 IS-01 / IS-02 定义存在问题，记录为 FEATURE_SPECIFICATION_LIMITATION，不得现场修改。**

### 6.6 Feature ≠ Rule

```
Feature (IS-01/IS-02)
  = machine-observable signal

Information Source
  = evidence provider

Decision Rule
  = if feature then action  ← FORBIDDEN

Machine-resolvable
  = independent validation passed  ← NOT YET ACHIEVED

Pattern Match
  = feature fires on input  ← NOT EQUAL to correct decision
```

---

## 七、Ground Truth Authority

### 7.1 GT 分类

| GT 类型 | 定义 | 当前状态 | 可用? |
|---|---|---|---|
| GT-GEOMETRIC | 基于 P4 几何特征的派生标签 | ✅ 存在 (extract_ambiguous.py) | ⚠️ 仅用于几何评估，不用于语义评估 |
| GT-SEMANTIC | 基于独立 Human/Expert 语义判断的标签 | ❌ 不存在 | ❌ NOT AVAILABLE |
| GT-UNRESOLVED | 无法确定正确答案的 case | ❌ 不存在 | N/A |

### 7.2 Geometry GT ≠ Semantic Boundary GT

AMB-026 证明：
- GT-GEOMETRIC: SHOULD_MERGE (w_a≥25 AND w_b≥25 AND len≥10)
- Human semantic judgment: KEEP_SEPARATE (不同句子)
- 结论：几何 GT 在 body text 场景下与语义定义不一致

### 7.3 对 TOC_SECTION_NUMBER_TITLE 的影响

对于 TOC_SECTION_NUMBER_TITLE：
- GT-GEOMETRIC: SHOULD_MERGE (来自 extract_ambiguous.py 的 is_body_continuation 逻辑)

但 GT-GEOMETRIC 的 is_body_continuation 判断使用 w_a≥25 AND w_b≥25 AND len≥10——这对 TOC heading 可能碰巧正确，但 GT 来源不独立于 P4 几何信息。

**如果实验声称 semantic machine-resolvability，必须存在独立 Human/Expert GT。当前不存在。**

### 7.4 未来 Semantic GT 生成方案（设计，不实施）

| 方案 | 说明 | 独立性 |
|---|---|---|
| 第二 reviewer 对新文档做 Human review | 在 unprocessed PDFs 上运行 P1-P6 → 提取 AMBIGUOUS → Human review | ✅ 独立（新文档 + 新 reviewer） |
| 专家标注 | 领域专家对新文档的 boundary cases 做语义标注 | ✅ 独立 |
| Round 1 reviewer 对新文档做 review | 同一 reviewer 但新文档 | ⚠️ 部分独立（reviewer 可能记忆 IS pattern） |

**推荐方案：第二 reviewer + 新文档。** 这同时解决 inter-reviewer agreement 和 data independence 问题。

---

## 八、Machine-Resolvable Definition

### 8.1 正式定义

```
MACHINE_RESOLVABLE
```

**定义**：在冻结的 Evidence Source + Frozen Feature Specification 下，系统能够对一个 boundary case 给出确定的 MERGE 或 KEEP_SEPARATE，且该判断：

| 条件 | 说明 |
|---|---|
| 不依赖 Round 1 标签 | Evaluation data 未参与 IS discovery |
| 不依赖 Human decision 泄漏 | 无 Human decision 用于 evaluation GT（除非独立 Human Validation） |
| 不依赖未来人工修正 | 不允许 evaluation 后修改 feature |
| 不需要临时增加规则 | 不允许 evaluation 中增加 heuristic |
| 具有明确 provenance | 每个 decision 可追溯到 document/page/pair/source evidence |
| 可以在独立样本上复现 | 在未见过的新文档上得到一致结果 |

### 8.2 等级区分

| 等级 | 名称 | 条件 | 当前状态 |
|---|---|---|---|
| Level 0 | POTENTIALLY_MACHINE_RESOLVABLE | counterfactual 分析显示 IS 可能区分 | ✅ 29/43 (但 TRAIN=TEST) |
| Level 1 | MACHINE_RESOLVABLE (development) | 在 development set 上稳定输出确定 decision | ❌ 未测试（无独立 dev set） |
| Level 2 | MACHINE_RESOLVABLE (independent) | 在 independent evaluation set 上稳定输出 | ❌ 无 independent set |
| Level 3 | INDEPENDENTLY_VALIDATED_MACHINE_RESOLVABLE | 在 independent set 上 + 独立 semantic GT 验证 + Gate 全通过 | ❌ 无 GT + 无 independent set |

**当前最高等级：Level 0 (POTENTIALLY_MACHINE_RESOLVABLE)。**

**只有 Level 3 才能称为 ACTUAL BOUNDARY SHRINKAGE。**

### 8.3 INSUFFICIENT_EVIDENCE

机器在证据不足时必须能够拒绝强判：

```
MACHINE_DECISION output:
  MERGE              — evidence supports merge
  KEEP_SEPARATE      — evidence supports separate
  INSUFFICIENT_EVIDENCE — evidence insufficient, refuse to decide
```

**INSUFFICIENT_EVIDENCE 不是失败——它是系统诚实的表现。** 符合 DICE 核心原则："Evidence insufficient → 不做强结论。"

---

## 九、Experimental Protocol

### 9.1 实验输入

```
Input per boundary case:
  - P4 geometry evidence: {gap, dy, w_a, w_b, same_style, line_obs_count}
  - IS-01(text_a): boolean (frozen definition)
  - IS-01(text_b): boolean (frozen definition)
  - IS-02(text_a): boolean (frozen definition)
  - IS-02(text_b): boolean (frozen definition)
  - IS-07(page_context): YES/NO/UNKNOWN (frozen definition)
```

### 9.2 实验输出

```
Output per boundary case:
  MACHINE_DECISION: MERGE | KEEP_SEPARATE | INSUFFICIENT_EVIDENCE
  DECISION_EVIDENCE: {which IS fired, what values}
  PROVENANCE: {document, page, pair_id, source_artifact}
```

### 9.3 决策逻辑（概念性，非 production rule）

**这不是 if-then rule。这是 counterfactual evaluation protocol。**

```
For each boundary case:
  Step 1: Compute IS-01(text_a), IS-02(text_b) using frozen definitions
  Step 2: If IS-01(text_a)==True AND IS-02(text_b)==True:
            → MACHINE_DECISION = MERGE
            → DECISION_EVIDENCE = {IS-01_a: True, IS-02_b: True}
  Step 3: If IS-01(text_a)==False AND IS-02(text_b)==False:
            → MACHINE_DECISION = KEEP_SEPARATE
            → DECISION_EVIDENCE = {IS-01_a: False, IS-02_b: False}
  Step 4: Otherwise (mixed signals):
            → MACHINE_DECISION = INSUFFICIENT_EVIDENCE
            → DECISION_EVIDENCE = {IS-01_a: ?, IS-02_b: ?}
```

### 9.4 实验前提条件

| 条件 | 当前状态 | 需要什么 |
|---|---|---|
| Independent Evaluation Set exists | ❌ NO | 处理 7 unprocessed PDFs |
| Feature Specification frozen | ✅ YES | IS-01/IS-02 frozen in this document |
| Semantic GT available | ❌ NO | 第二 reviewer + 新文档 |
| No evaluation leakage | ❌ CANNOT VERIFY | 需要新数据 |
| Gate defined | ✅ YES | 见第十节 |

### 9.5 实验无法在当前阶段执行

**原因：不存在 Independent Evaluation Set。**

```
当前可执行的:
  ❌ Independent evaluation (no independent data)
  ❌ Semantic GT validation (no semantic GT)
  ❌ Cross-document generalization (same 3 docs)
  ❌ Adversarial robustness (only 2 historical adversarial cases)

当前只能执行的:
  ✅ Experimental design (this document)
  ✅ Provenance audit (completed)
  ✅ Data collection protocol design (this document)
```

---

## 十、Adversarial Design

### 10.1 Historical Adversarial Analysis (NOT independent)

| Case | Mode | text_a | text_b | IS-01_a | IS-02_b | Human | CF |
|---|---|---|---|---|---|---|---|
| AMB-018 | TOC_NUM_TITLE | "6.1" | "SMEFT" | ✅ True | ✅ True | MERGE | CF-A |
| AMB-040 | FORMULA_WIDE | "( )" | "cos(" | ❌ False | ✅ True* | KEEP_SEPARATE | CF-B |

*IS-02 loose detection: "cos" matches as readable word (3 chars > 2)

**这些 adversarial cases 来自 Round 1，只能作为 HISTORICAL ADVERSARIAL ANALYSIS，不能作为 INDEPENDENT EVALUATION。**

### 10.2 IS-01 separation mechanism

```
AMB-018: IS-01_a=True → MERGE direction
AMB-040: IS-01_a=False → INSUFFICIENT_EVIDENCE / KEEP_SEPARATE direction

IS-01 alone distinguishes these two geometry-similar cases.
```

### 10.3 Future Adversarial Sample Design（设计，不实施）

| Adversarial type | 描述 | 当前 corpus 有? | 风险 |
|---|---|---|---|
| Number + non-title | "1" + "mm tolerance" (measurement) | ❌ 无 | IS-01+IS-02 → MERGE (可能 FP) |
| Figure number + caption | "Figure 3" + "shows that..." | ❌ 无 | IS-01+IS-02 → MERGE (可能 FP) |
| Equation number + text | "2.27" + "where..." | ❌ 无 (gap=0 已 merge) | IS-01+IS-02 → MERGE (gap>8 时可能 FP) |
| List number + item | "1" + "Connect cable" | ❌ 无 | IS-01+IS-02 → MERGE (可能 FP) |
| Page number + header | "1" + "Introduction" (page header) | ❌ 无 | IS-01+IS-02 → MERGE (FP) |
| Letter + non-title | "A" + "circuit board" | ❌ 无 | IS-01+IS-02 → MERGE (可能 FP) |

**这些 adversarial samples 需要在新文档中寻找或构造。当前 corpus 未暴露这些 FP 风险。**

---

## 十一、Cross-Document Generalization

### 11.1 当前文档覆盖

| 文档族 | 文档数 | TOC/APPENDIX cases | FORMULA cases | BODY_CONT cases |
|---|---|---|---|---|
| arxiv (processed) | 3 | 29 | 13 | 1 |
| device manuals (processed) | 5 | 0 | 0 | 0 |
| arxiv (unprocessed) | 4 | ? | ? | ? |
| qbio (unprocessed) | 3 | ? | ? | ? |

### 11.2 设备手册分析

| 文档 | same-y pairs | AMBIGUOUS | TOC/APPENDIX | 评估 |
|---|---|---|---|---|
| RA101 | 0 | 0 | 0 | NOT_APPLICABLE |
| RM501-P4 | 2 | 0 | 0 | NOT_APPLICABLE |
| E804 | 1 | 0 | 0 | NOT_APPLICABLE |
| C216 | 0 | 0 | 0 | NOT_APPLICABLE |
| DC201 | 0 | 0 | 0 | NOT_APPLICABLE |

**设备手册不存在 TOC_SECTION_NUMBER_TITLE boundary cases。** 设备手册的布局结构（表格、步骤列表、参数显示）不产生学术论文式的 heading 编号+标题 pairs。

### 11.3 跨文档泛化要求

```
G7 — Cross-Document Generalization:
  不能只在 arxiv_toc 上成立。
  至少需要跨 document / source family 验证。

当前状态:
  - arxiv_toc: ✅ 有 TOC cases
  - arxiv_2307: ✅ 有 TOC cases (heading in body pages)
  - arxiv_bio_body: ✅ 有 TOC cases (heading in body pages)
  - device manuals: ❌ 0 TOC cases (NOT_APPLICABLE)
  - unprocessed PDFs: ❓ 未知

跨 document family 验证:
  - arxiv → qbio: ❓ 未测试
  - arxiv → device manual: ❌ NOT_APPLICABLE (设备手册无 TOC heading)
```

**跨文档泛化无法在当前数据上验证。需要处理 unprocessed PDFs。**

---

## 十二、Metrics

### 12.1 Boundary Shrinkage 四级定义

| 级别 | 名称 | 定义 | 当前值 |
|---|---|---|---|
| 1 | Baseline Ambiguity | Independent Evaluation Set 中原本需要 Human 的数量 | UNKNOWN (无 independent set) |
| 2 | Potential Machine-Resolvable | 根据冻结 feature evidence，机器可能能够判断的数量 | 29/43 = 67.4% (counterfactual, NOT independent) |
| 3 | Actual Machine-Resolvable | 机器在冻结 spec 下实际稳定输出确定 decision 的数量 | UNKNOWN (无 independent set) |
| 4 | Independently Validated Machine-Resolvable | 机器 decision 被独立 semantic GT 验证且达到 Gate 的数量 | UNKNOWN (无 GT + 无 independent set) |

### 12.2 Actual Boundary Shrinkage Rate

```
Actual Boundary Shrinkage Rate
=
Independently Validated Machine-Resolvable Cases
/
Baseline Ambiguous Cases

当前值: UNKNOWN (无法计算)
```

**只有第 4 级才能称为 ACTUAL BOUNDARY SHRINKAGE。当前无法计算。**

### 12.3 评估指标（未来实验用）

| 指标 | 定义 | Gate |
|---|---|---|
| Precision | correct MERGE / total MERGE | ≥ 95% |
| Recall | correct MERGE / total should-merge | ≥ 80% |
| INSUFFICIENT_EVIDENCE Rate | INSUFFICIENT_EVIDENCE / total | 报告，无 gate |
| False Positive Rate | wrong MERGE / total MERGE | ≤ 5% |
| Cross-document Consistency | same decision on same pattern across docs | 100% |
| Adversarial Robustness | correct on independent adversarial samples | 100% |

---

## 十三、Pass / Fail Gates

### 13.1 十个 Gate

| Gate | 条件 | 当前状态 |
|---|---|---|
| G1 | Independent Evaluation Set Exists | ❌ FAIL — 0/43 eligible, 7 PDFs unprocessed |
| G2 | Feature Specification Frozen | ✅ PASS — IS-01/IS-02 frozen in this document |
| G3 | No Evaluation Leakage | ❌ FAIL — all 43 cases seen in counterfactual analysis |
| G4 | Semantic Ground Truth Validity | ❌ FAIL — no semantic GT, only geometry GT |
| G5 | Precision Constraint (≥ 95%) | ⚠️ CANNOT EVALUATE — no independent set |
| G6 | Recall / Coverage Constraint (≥ 80%) | ⚠️ CANNOT EVALUATE — no independent set |
| G7 | Cross-Document Generalization | ❌ FAIL — same 3 arxiv docs, device manuals NOT_APPLICABLE |
| G8 | Adversarial Robustness | ⚠️ PARTIAL — 2 historical adversarial cases only |
| G9 | INSUFFICIENT_EVIDENCE Safety | ⚠️ DESIGNED — protocol includes INSUFFICIENT_EVIDENCE output |
| G10 | Provenance Completeness | ✅ PASS — full provenance chain documented |

### 13.2 Gate 总结

```
G1:  ❌ FAIL
G2:  ✅ PASS
G3:  ❌ FAIL
G4:  ❌ FAIL
G5:  ⚠️ CANNOT EVALUATE
G6:  ⚠️ CANNOT EVALUATE
G7:  ❌ FAIL
G8:  ⚠️ PARTIAL
G9:  ⚠️ DESIGNED
G10: ✅ PASS

PASSED:     2/10 (G2, G10)
FAILED:     4/10 (G1, G3, G4, G7)
CANNOT EVAL: 2/10 (G5, G6)
PARTIAL:    2/10 (G8, G9)

OVERALL: NOT PASSED
```

**当前不允许任何 Machine Boundary Promotion。**

---

## 十四、Boundary Shrinkage Definition

### 14.1 四级 Shrinkage

```
Level 1: Baseline Ambiguity
  = Independent Evaluation Set 中原本需要 Human 的数量
  当前: UNKNOWN (无 independent set)

Level 2: Potential Machine-Resolvable
  = 根据冻结 feature evidence，机器可能能够判断的数量
  当前: 29/43 = 67.4% (counterfactual, NOT independent)
  性质: POTENTIAL, NOT ACTUAL

Level 3: Actual Machine-Resolvable
  = 机器在冻结 spec 下实际稳定输出确定 decision 的数量
  当前: UNKNOWN (无 independent set)
  性质: ACTUAL (但需要 independent evaluation)

Level 4: Independently Validated Machine-Resolvable
  = 机器 decision 被独立 semantic GT 验证且达到 Gate 的数量
  当前: UNKNOWN (无 GT + 无 independent set)
  性质: VALIDATED

Actual Boundary Shrinkage Rate = Level 4 / Level 1
当前: UNKNOWN
```

### 14.2 不能使用的指标

```
❌ 不能使用 "29/43 = 67.4%" 作为实际 shrinkage。
   这只是 Potential Resolution Rate (counterfactual estimate)。

❌ 不能使用 "0/75 = 0% FP" 作为独立 FP rate。
   这来自与 discovery set 同源的 corpus。

❌ 不能使用 "13/13 = 100% consistency" 作为泛化证据。
   这是 TRAIN=TEST 一致性。
```

---

## 十五、Failure Modes

### 15.1 已识别的 Failure Modes

| # | Failure Mode | 描述 | 当前风险 |
|---|---|---|---|
| F1 | IS-02 loose detection | "cos"/"sin"/"and"/"are" 匹配为 readable word | ⚠️ MEDIUM (当前 IS-01_a 过滤缓解) |
| F2 | Number + non-title FP | "1" + "mm tolerance" 匹配 IS-01+IS-02 | ⚠️ 未测试 (设备手册未覆盖) |
| F3 | Equation number + text | "2.27" + "where..." 在 gap 8-50 时匹配 | ⚠️ 未测试 |
| F4 | List number + item | "1" + "Connect cable" 匹配 | ⚠️ 未测试 (设备手册 NOT_APPLICABLE) |
| F5 | Page number + header | "1" + "Introduction" 作为 page header | ⚠️ 未测试 |
| F6 | Same pattern, different decision | IS-01+IS-02 匹配但正确答案非 MERGE | ❌ 未在独立数据上测试 |
| F7 | IS-01 不区分 heading vs equation number | "2.27" 匹配 number pattern | ⚠️ FEATURE_SPECIFICATION_LIMITATION |
| F8 | Geometry GT 不等于 semantic GT | AMB-026 证明 | ✅ 已识别 |

### 15.2 未识别的 Failure Modes

```
当前 corpus (8 docs, 2255 pairs) 未暴露的 failure modes:
  - 设备手册 table/procedure 中的 number+text pairs
  - 图表编号 + caption text
  - 多栏排版中的跨栏 number+text
  - 非英文文档的 numbering pattern
  - 脚注编号 + 脚注文本

这些 failure modes 只能在新文档上发现。
```

---

## 十六、Limitations

| # | 限制 | 影响 |
|---|---|---|
| L1 | 无 Independent Evaluation Set | 无法验证独立 machine-resolvability |
| L2 | 无 Semantic GT | 无法验证 semantic correctness |
| L3 | 单 reviewer | 无 inter-reviewer agreement |
| L4 | 同文档族 (3 arxiv docs) | 跨文档泛化不可验证 |
| L5 | 设备手册 0 TOC cases | NOT_APPLICABLE, 无法测试设备手册 FP |
| L6 | 7 unprocessed PDFs | 需要 pipeline 处理才能使用 |
| L7 | IS-02 loose detection | 已知 limitation, frozen |
| L8 | TRAIN=TEST | counterfactual 结果不能作为独立证据 |
| L9 | 研究者先验知识 | 研究者已知全部 43 cases 的 IS pattern |
| L10 | Timer 未修复 | Human cost 无法测量 |

---

## 十七、Future Human Validation Plan

### 17.1 方案设计（不实施）

```
Step 1: Process 7 unprocessed PDFs through P1-P6 pipeline
  → 产生新的 boundary pairs
  → 提取新的 AMBIGUOUS cases
  → 这些 case 对 IS-01/IS-02 pattern 完全 UNSEEN

Step 2: Recruit second reviewer (reviewer_2)
  → reviewer_2 不参与 IS 发现
  → reviewer_2 对新 AMBIGUOUS cases 做 Human review
  → 产生独立 semantic GT

Step 3: Run frozen IS-01/IS-02 on new AMBIGUOUS cases
  → 输出 MACHINE_DECISION (MERGE / KEEP_SEPARATE / INSUFFICIENT_EVIDENCE)
  → 不修改 IS 定义

Step 4: Compare MACHINE_DECISION against reviewer_2 semantic GT
  → 计算 Precision, Recall, FP rate
  → 检查 Gate G5/G6/G7/G8

Step 5: If Gate passed:
  → INDEPENDENTLY_VALIDATED_MACHINE_RESOLVABLE
  → Actual Boundary Shrinkage 可计算

Step 6: If Gate not passed:
  → KEEP HUMAN BOUNDARY
  → 记录 failure modes
  → 不修改 IS 定义
```

### 17.2 前提条件

| 条件 | 当前状态 |
|---|---|
| 7 PDFs processed through P1-P6 | ❌ NOT DONE |
| New AMBIGUOUS cases extracted | ❌ NOT DONE |
| Second reviewer recruited | ❌ NOT DONE |
| Timer fix implemented | ❌ NOT DONE |
| Feature specification frozen | ✅ DONE (this document) |

### 17.3 不实施

**以上全部为设计。不实施。不修改任何代码。不招募 reviewer。不处理 PDFs。**

---

## 十八、Implementation Boundary

### 18.1 禁止清单

| # | 禁止 | 理由 |
|---|---|---|
| 1 | 不修改 P4 | frozen |
| 2 | 不修改 P7.1 | frozen |
| 3 | 不修改 P7.2 | frozen |
| 4 | 不修改 Frozen 730 | frozen |
| 5 | 不修改 calibration_filter | frozen |
| 6 | 不修改 schema | frozen |
| 7 | 不将 IS-01/IS-02 实现为正式规则 | experimental definition only |
| 8 | 不开始 P7.3 | NOT AUTHORIZED |
| 9 | 不注册 Capability | NOT AUTHORIZED |
| 10 | 不修改 IS-01/IS-02 定义 | frozen in this document |
| 11 | 不处理 unprocessed PDFs | NOT AUTHORIZED (design only) |
| 12 | 不招募 reviewer | NOT AUTHORIZED (design only) |
| 13 | 不修改 Round 1 数据 | frozen |
| 14 | 不修改 GT | frozen |
| 15 | 不修改 timer | NOT AUTHORIZED |
| 16 | 不自动 merge/split | NOT AUTHORIZED |
| 17 | 不 LLM 自动判断 | NOT AUTHORIZED |
| 18 | 不制造 synthetic independence | FORBIDDEN |
| 19 | 不随机拆分 Round 1 | FORBIDDEN |
| 20 | 不把 23 unreviewed 当 independent | FORBIDDEN |

### 18.2 允许清单

| # | 允许 |
|---|---|
| 1 | 读取已有代码/文档/JSON |
| 2 | 数据 provenance 审计 |
| 3 | 数据划分分析 |
| 4 | 生成实验设计文档 |
| 5 | 生成只读实验矩阵 |
| 6 | 生成统计报告 |
| 7 | counterfactual / offline analysis |
| 8 | 设计未来实验 |

---

## 十九、Final Gate Status

### 19.1 8 个最终问题

#### Q1: 现有数据中是否真的存在 Independent Evaluation Set？

**否。**

- 20/43 cases: DIRECTLY CONTAMINATED (IS discovery source)
- 23/43 cases: INDIRECTLY CONTAMINATED (counterfactual analysis, same docs)
- 0/43 cases: evaluation eligible
- 7 unprocessed PDFs: truly independent but NOT processed

#### Q2: 哪些数据已经被 Round 1 / IS-01 / IS-02 discovery 污染？

- 20 Round 1 reviewed cases: DIRECT contamination (IS-01/IS-02 derived from these)
- 23 unreviewed cases: INDIRECT contamination (counterfactual analysis, researcher has seen IS patterns)
- 2255 boundary pairs: COLLATERAL contamination (same document family, used in FP analysis)
- 43 GT labels: GT_CONTAMINATION (geometry GT, not semantic)

#### Q3: 哪些数据仍然可以作为独立 evaluation？

**当前无已处理的独立数据。**

唯一独立数据源是 7 个 unprocessed PDFs，但它们需要先通过 P1-P6 pipeline 处理。

#### Q4: IS-01 + IS-02 是否可以在"未见过"的样本上进行测试？

**当前不能。** 需要先处理 unprocessed PDFs，提取新的 AMBIGUOUS cases，然后使用冻结的 IS-01/IS-02 定义进行测试。

#### Q5: 现有 P4 geometry GT 是否足以作为 semantic GT？

**否。** AMB-026 证明 geometry GT ≠ semantic GT。GT-GEOMETRIC 使用 w_a≥25 AND w_b≥25 AND len≥10 的几何规则，不进行语义判断。

#### Q6: 如果不足，未来需要什么 Human Validation？

需要：
1. 第二 reviewer（独立于 IS discovery）
2. 新文档的 Human review（unprocessed PDFs）
3. 语义专家标注（非几何 GT）
4. Timer fix（测量真实 Human cost）

#### Q7: 未来如何测量真正的 Boundary Shrinkage？

```
Actual Boundary Shrinkage Rate
=
Independently Validated Machine-Resolvable Cases (Level 4)
/
Baseline Ambiguous Cases (Level 1)

需要:
  1. Independent Evaluation Set (processed unprocessed PDFs)
  2. Frozen IS-01/IS-02 (✅ done)
  3. Independent Semantic GT (second reviewer + new docs)
  4. Gate 全通过 (G1-G10)
```

#### Q8: 下一步到底应该？

**D. 暂停该方向（等待数据收集）。**

理由：
- 无 Independent Evaluation Set → 无法执行独立评估
- 无 Semantic GT → 无法验证 semantic correctness
- 同文档族 → 无法验证跨文档泛化
- 不能制造 synthetic independence
- 不能随机拆分 Round 1
- 不能把 23 unreviewed 当 independent

**正确路径：**

```
当前: DESIGN COMPLETE, DATA COLLECTION NEEDED

NEXT CANDIDATE:
  Future Independent Evaluation Data Collection Protocol
  1. Process 7 unprocessed PDFs through P1-P6
  2. Extract new AMBIGUOUS cases
  3. Recruit second reviewer
  4. Run frozen IS-01/IS-02
  5. Compare against independent semantic GT
  6. Evaluate Gate G1-G10

NOT:
  Implement Rule
  Modify P4
  Start P7.3
```

### 19.2 最终状态

```
DESIGN STATUS = READY (design complete, data collection needed)
DATA INDEPENDENCE = PARTIAL (no independent processed data exists)
FEATURE FREEZE = PASS (IS-01/IS-02 frozen)
SEMANTIC GT = NOT_AVAILABLE
IMPLEMENTATION = NOT AUTHORIZED
P7.3 = NOT AUTHORIZED
FROZEN BASELINE = INTACT
STOP = TRUE
```

---

## STOP

```
本阶段结论:

  1. 数据独立性审计完成。
     0/43 cases evaluation eligible。
     7 unprocessed PDFs 是唯一独立数据源（需处理）。

  2. IS-01/IS-02 已冻结为 experimental definitions。
     不允许在 evaluation 中修改。

  3. 实验设计完成。
     但无法在当前阶段执行（无 independent set + 无 semantic GT）。

  4. 当前只能证明 feasibility hypothesis，
     不能证明 independent machine-resolvability。

  5. 不存在可直接使用的 Independent Evaluation Set。
     需要先收集新的独立数据。

NEXT CANDIDATE:
  Future Independent Evaluation Data Collection Protocol

Implementation = NOT AUTHORIZED
P7.3 = NOT AUTHORIZED
Frozen = INTACT
STOP = TRUE
```

**不进入下一阶段。不修改任何代码。不修改任何实验数据。不制造 synthetic independence。等待下一步批准。**
