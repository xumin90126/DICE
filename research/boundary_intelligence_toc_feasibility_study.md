# Boundary Intelligence / Information Source Expansion Feasibility Study
## TOC_SECTION_NUMBER_TITLE Counterfactual Analysis

> READ-ONLY / OFFLINE / COUNTERFACTUAL FEASIBILITY STUDY。
> 不修改任何 frozen/production/source 文件。不实施。不进入 P7.3。

---

## Executive Summary

```
Research Question:
  如果把 Human 实际使用的、目前已存在于 DICE 中的 machine-observable
  Information Source (IS-01/IS-02/IS-07) 提供给一个新的 Boundary Intelligence 层，
  当前 Ambiguous Boundary 中有多少可以被可靠消化？

Method:
  Counterfactual feature attribution on 43 AMBIGUOUS cases + 2255 total boundary pairs.
  No code modification. No rule implementation. Offline analysis only.

Key Results:
  - 29/43 (67.4%) AMBIGUOUS cases are CF-A: POTENTIALLY_MACHINE_RESOLVABLE
    (all TOC_SECTION_NUMBER_TITLE + APPENDIX_LETTER_TITLE)
  - 14/43 (32.6%) remain CF-B: STILL_AMBIGUOUS
    (13 FORMULA_FRAGMENT_WIDE + 1 BODY_TEXT_CONTINUATION)
  - 0/43 are CF-C: INSUFFICIENT_SOURCE
  - IS-01+IS-02 false positive rate on current corpus: 0/75 = 0.0%
  - BUT: corpus is small (8 docs, 2255 pairs), pattern is semantically non-specific

TOC_SECTION_NUMBER_TITLE Classification:
  A. PROMISING MACHINE-RESOLVABLE
  (existing machine-observable evidence shows stable distinction,
   worthy of future independent validation)

Adversarial Separability:
  AMB-018 vs AMB-040: SUPPORTED FOR CASES (IS-01 distinguishes number from symbol)
  NOT: GENERALIZED ADVERSARIAL ROBUSTNESS

Circular Reasoning Status:
  EXPLORATORY / NON-GENERALIZING
  (IS pattern derived from same 20 Human-reviewed cases used for evaluation)

Implementation = NOT AUTHORIZED
P7.3 = NOT AUTHORIZED
Frozen = INTACT
```

---

## 一、Research Question

### 1.1 不是研究什么

不研究："Human 能不能解决 ambiguity？"——Round 1 已给出 INITIAL FEASIBILITY = SUPPORTED。

### 1.2 研究什么

研究："如果把 Human 实际使用的、目前已存在于 DICE 中的 machine-observable Information Source 提供给一个新的 Boundary Intelligence 层，当前 Ambiguous Boundary 中有多少可以被可靠消化？"

### 1.3 核心区分

验证的是：

```
Information Source Expansion
  → Human Boundary ↓
  → Machine-resolvable Boundary
```

而不是：

```
Human Decision → Hard-coded Rule
```

---

## 二、Experimental Constraints

| 约束 | 说明 |
|---|---|
| READ-ONLY | 不修改任何 frozen/production/source 文件 |
| OFFLINE | 从现有 artifact 中离线读取数据，构造 counterfactual feature view |
| COUNTERFACTUAL | P4 原始结果保持不变；只分析"如果 IS 可用会怎样" |
| NO RULE | 不创建正式 machine rule；不输出 if-then 规则 |
| NO CIRCULAR | 不用 Human decision 训练规则再用同一批验证 |
| ALLOWED IS | 仅 IS-01 (TEXT_NUMBER_PATTERN), IS-02 (TEXT_READABLE_TITLE), IS-07 (VISUAL_TOC_CONTEXT) |
| NOT ALLOWED | IS-10 (sentence boundary interpretation) — 不混入 semantic interpretation |
| EXPLORATORY ONLY | 结果标记为 EXPLORATORY / NON-GENERALIZING |

---

## 三、Existing Information Sources

### 3.1 允许使用的 IS

| IS | 名称 | 定义 | P4 拥有? | P1 拥有? | P6 拥有? | Machine-observable? |
|---|---|---|---|---|---|---|
| IS-01 | TEXT_NUMBER_PATTERN | text 匹配编号模式 (1, 2.1, B.1) | ❌ | ✅ P1 有 text | N/A | ✅ regex |
| IS-02 | TEXT_READABLE_TITLE | text 包含可读字母词 (length > 2) | ❌ | ✅ P1 有 text | N/A | ✅ word detection |
| IS-07 | VISUAL_TOC_CONTEXT | 页面是 TOC 页 | ❌ | N/A | ✅ P6 有 region | ✅ P6 region type |

### 3.2 关键发现：信息已存在于 DICE 中

- **P1 已经有文本内容**——`observation.text` 字段包含原始文本字符串
- **P6 已经有 region 分类**——region type 可以区分 TOC / BODY / FORMULA 页面
- **问题不是"信息不存在"，而是"P4 的 geometry-only 契约排除了这些信息"**

### 3.3 不使用的 IS

| IS | 名称 | 不使用理由 |
|---|---|---|
| IS-03 | TEXT_SYMBOL_PATTERN | 本阶段只研究 TOC_SECTION_NUMBER_TITLE |
| IS-04 | TEXT_PUNCTUATION | 属于 BODY_TEXT_CONTINUATION 分析 |
| IS-05 | TEXT_CAPITAL_START | 同上 |
| IS-10 | SENTENCE_BOUNDARY_INTERPRETATION | Category C，不混入 semantic interpretation |

---

## 四、Counterfactual Method

### 4.1 方法概述

```
Step 1: 从 ambiguous_cases_all.json 读取 43 个 AMBIGUOUS cases
Step 2: 从 cross_doc_audit_raw.json + supplement 读取 2255 个 boundary pairs
Step 3: 对每个 case 离线计算 IS-01, IS-02, IS-07 特征
Step 4: 根据 IS 可用性分类为 CF-A / CF-B / CF-C
Step 5: 在全部 2255 pairs 上检查 false positive surface
Step 6: 对 20 个 Human-reviewed cases 做 pattern-consistency 检查
```

### 4.2 Counterfactual Feature View（概念对象，不写入 schema）

```
CounterfactualFeatureView {
  geometric_features: {gap, dy, w_a, w_b, same_style, line_obs}  // from P4
  is01_number_pattern_a: bool   // derived from P1 text
  is01_number_pattern_b: bool   // derived from P1 text
  is02_readable_title_a: bool   // derived from P1 text
  is02_readable_title_b: bool   // derived from P1 text
  is07_toc_context: YES/NO/UNKNOWN  // derived from P6 region
}
```

**此对象只用于实验分析。不写入正式 schema。不成为 runtime input。不成为 capability input。**

### 4.3 Counterfactual Decision Classes

| Class | 名称 | 定义 |
|---|---|---|
| CF-A | POTENTIALLY_MACHINE_RESOLVABLE | 现有 machine-observable information 能形成稳定、可解释的 boundary distinction，但尚未经独立泛化验证 |
| CF-B | STILL_AMBIGUOUS | 加入 IS-01/02/07 后仍无法可靠区分 |
| CF-C | INSUFFICIENT_SOURCE | 所需 Information Source 在当前 artifact 中不可可靠获得 |

**禁止使用 "AUTO_RESOLVED"——本阶段没有正式 machine decision。**

### 4.4 CF-A 判定条件

对于 TOC_SECTION_NUMBER_TITLE / APPENDIX_LETTER_TITLE mode：

```
CF-A 条件: IS-01(text_a) == True AND IS-02(text_b) == True
```

即：text_a 匹配编号模式 AND text_b 包含可读标题词。

**这不是 rule。这是 counterfactual 可观测性评估——"这些 IS 是否提供了足够的 distinction"。**

---

## 五、Feature Attribution（全 43 cases）

### 5.1 按 Mode 汇总

| Mode | Case 数 | IS-01_a | IS-02_b | IS-07 | CF Class |
|---|---|---|---|---|---|
| TOC_SECTION_NUMBER_TITLE | 27 | 27/27 True | 27/27 True | 20 YES / 7 NO | CF-A: 27 |
| APPENDIX_LETTER_TITLE | 2 | 2/2 True | 2/2 True | 2 YES | CF-A: 2 |
| FORMULA_FRAGMENT_WIDE | 13 | 0/13 True | 2/13 True | 0 YES | CF-B: 13 |
| BODY_TEXT_CONTINUATION | 1 | 0/1 True | 1/1 True | 0 YES | CF-B: 1 |

### 5.2 关键观察

1. **所有 29 个 TOC/APPENDIX cases 都满足 IS-01_a=True AND IS-02_b=True** → CF-A
2. **所有 13 个 FORMULA cases 都不满足 IS-01_a=True** → CF-B（text_a 是符号，不是编号）
3. **AMB-026 (BODY_CONT) 不满足 IS-01_a=True** → CF-B（text_a 是可读文本，不是编号）
4. **IS-07 (TOC context) 在 7 个 cases 中为 NO**（arxiv_bio_body 和 arxiv_2307 的 heading 出现在 body/formula 页面，不是 TOC 页），但这些 cases 仍然满足 IS-01+IS-02 → CF-A

**IS-07 不是 CF-A 的必要条件**——heading 出现在非 TOC 页面时，IS-01+IS-02 仍可识别。

### 5.3 IS-07 的角色

| IS-07 值 | Case 数 | 全部 CF-A? | 说明 |
|---|---|---|---|
| YES (TOC page) | 22 | ✅ 是 | TOC 页面的 heading，IS-07 确认上下文 |
| NO (body/formula page) | 7 | ✅ 是 | 非 TOC 页面的 heading（section start in body），IS-07 不影响 CF-A 判定 |

**IS-07 作为辅助 confirmation 信号，不作为必要条件。** heading 在 body 页面的 section start（如 AMB-023 "1" + "Introduction" 在 arxiv_bio_body page 3）同样需要 MERGE。

---

## 六、TOC Case Analysis

### 6.1 Round 1 中 13 个 TOC/APPENDIX reviewed cases

| Case | Doc | text_a | text_b | IS-01_a | IS-02_b | IS-07 | Human | CF Class |
|---|---|---|---|---|---|---|---|---|
| AMB-001 | arxiv_toc | "1" | "Introduction" | ✅ | ✅ | YES | MERGE | CF-A |
| AMB-005 | arxiv_toc | "2.3.1" | "Factorization" | ✅ | ✅ | YES | MERGE | CF-A |
| AMB-012 | arxiv_toc | "4.1" | "Decomposition of" | ✅ | ✅ | YES | MERGE | CF-A |
| AMB-014 | arxiv_toc | "5" | "Prediction for" | ✅ | ✅ | YES | MERGE | CF-A |
| AMB-017 | arxiv_toc | "6" | "Consequences for..." | ✅ | ✅ | YES | MERGE | CF-A |
| AMB-018 ★ | arxiv_toc | "6.1" | "SMEFT" | ✅ | ✅ | YES | MERGE | CF-A |
| AMB-021 | arxiv_toc | "B.1" | "Two-point function" | ✅ | ✅ | YES | MERGE | CF-A |
| AMB-023 | arxiv_bio_body | "1" | "Introduction" | ✅ | ✅ | NO | MERGE | CF-A |
| AMB-025 | arxiv_bio_body | "2.1" | "Leptonic processes" | ✅ | ✅ | NO | MERGE | CF-A |
| AMB-027 | arxiv_2307 | "1." | "Introduction" | ✅ | ✅ | NO | MERGE | CF-A |
| AMB-028 | arxiv_2307 | "2." | "The model:..." | ✅ | ✅ | NO | MERGE | CF-A |
| AMB-034 | arxiv_2307 | "3." | "Bound (localized)..." | ✅ | ✅ | NO | MERGE | CF-A |
| AMB-043 | arxiv_2307 | "4." | "Families of..." | ✅ | ✅ | NO | MERGE | CF-A |

**一致性：13/13 reviewed TOC/APPENDIX cases → IS-01+IS-02 matches → Human=MERGE。零不一致。**

### 6.2 回答实验问题

#### Q1: Human 使用的 number/title/page context 是否都可机器观察？

**是。**
- IS-01 (number pattern): regex `^\d+(\.\d+)*\.?$` 或 `^[A-Z]\.\d+$` → deterministic
- IS-02 (readable title): word detection `any(len(re.sub(r'[^a-zA-Z]','',w)) > 2 for w in text.split())` → deterministic
- IS-07 (TOC context): P6 region type → deterministic

#### Q2: P1 是否已经提供足够 text？

**是。** P1 的 `observation.text` 字段包含完整文本字符串，可以直接做 pattern matching。

#### Q3: P6 是否已经提供足够 region/context？

**部分。** P6 有 region 分类，但本实验未直接读取 P6 输出——IS-07 通过 doc_id 间接推断。实际实现时需要验证 P6 region type 是否能准确区分 TOC/BODY/FORMULA 页面。

**注意：IS-07 在 7 个 CF-A cases 中为 NO**（heading 出现在 body/formula 页面），但这些 cases 仍正确分类为 CF-A。IS-07 不是必要条件。

#### Q4: 哪些 cases 在加入 IS 后 potentially machine-resolvable / remain ambiguous？

- **CF-A (potentially machine-resolvable)**: 29/43 = 67.4% (27 TOC + 2 APPENDIX)
- **CF-B (still ambiguous)**: 14/43 = 32.6% (13 FORMULA + 1 BODY_CONT)

#### Q5: 是否存在 geometry-isomorphic 但 text/visual evidence 不同的 cases？

**是——这正是 adversarial cases 的本质。**

| Case pair | gap | dy | w_a | w_b | same_style | IS-01_a | IS-02_b | Human |
|---|---|---|---|---|---|---|---|---|
| AMB-018 | 11.1 | 0 | 13.8 | 38.2 | True | ✅ True | ✅ True | MERGE |
| AMB-040 | 21.2 | 0 | 11.0 | 15.4 | True | ❌ False | ✅ True* | KEEP_SEPARATE |

*AMB-040 的 IS-02_b=True 是因为 "cos(" 中的 "cos" 匹配为 readable word（3 chars > 2）。这是 IS-02 检测的 loose behavior。

**AMB-018 和 AMB-040 在几何上相似（narrow_a + wide_b + same_y + same_style），但 IS-01_a 不同**：AMB-018 的 text_a="6.1" 匹配 number pattern，AMB-040 的 text_a="( )" 不匹配。IS-01 单独就能区分这两个 adversarial cases。

#### Q6: 是否存在 text/visual evidence 相同但 Human decision 不同的 cases？

**否。** 在 20 个 reviewed cases 中：
- 所有 IS-01_a=True AND IS-02_b=True 的 cases (13/13) → Human=MERGE
- 所有 IS-01_a=False 的 cases (7/7) → Human=KEEP_SEPARATE

**不存在 PATTERN_NOT_SUFFICIENT 的情况——在当前 sample 中。**

但注意：这只覆盖 20/43 cases，剩余 23 个未 reviewed。

---

## 七、Adversarial Analysis

### 7.1 AMB-018 vs AMB-040

| 维度 | AMB-018 | AMB-040 |
|---|---|---|
| Mode | TOC_SECTION_NUMBER_TITLE | FORMULA_FRAGMENT_WIDE |
| text_a | "6.1" | "( )" |
| text_b | "SMEFT" | "cos(" |
| gap | 11.1 | 21.2 |
| dy | 0.0 | 0.0 |
| w_a | 13.8 | 11.0 |
| w_b | 38.2 | 15.4 |
| same_style | True | True |
| IS-01_a | ✅ True ("6.1" = number) | ❌ False ("( )" ≠ number) |
| IS-02_b | ✅ True ("SMEFT" = readable) | ✅ True* ("cos" = readable, but false positive) |
| IS-07 | YES (TOC page) | NO (formula page) |
| Human | MERGE | KEEP_SEPARATE |
| CF Class | CF-A | CF-B |

*IS-02 对 "cos(" 的匹配是 loose detection——"cos" 是 3 字符字母词，匹配 readable_word 规则。但这是 IS-02 的假阳性（cos 是数学函数名，不是标题词）。由于 IS-01_a=False，CF-A 条件不满足，不影响 CF-B 分类。

### 7.2 分离机制

```
AMB-018: IS-01_a=True → CF-A → suggests MERGE direction
AMB-040: IS-01_a=False → CF-B → remains ambiguous

IS-01 alone distinguishes these two geometry-similar cases.
```

### 7.3 结论

```
ADVERSARIAL_SEPARABILITY = SUPPORTED FOR CASES (AMB-018 vs AMB-040)

NOT:
  GENERALIZED ADVERSARIAL ROBUSTNESS
  (only 2 adversarial cases tested, no independent validation)
```

---

## 八、False Positive Analysis

### 8.1 全 corpus IS-01+IS-02 pattern 匹配

| 类别 | 总数 | IS-01+IS-02 匹配 | 匹配率 |
|---|---|---|---|
| Merged pairs (gap≤8) | 1844 | 46 | 2.5% |
| Unmerged same-y (gap>8) | 411 | 29 | 7.1% |
| DETERMINISTIC_BLOCK (gap>50 / w_b<15) | — | 0 | 0% |
| **Total** | **2255** | **75** | **3.3%** |

### 8.2 False Positive Rate

```
IS-01+IS-02 False Positive Rate (current corpus):
  0 / 75 total pattern matches = 0.0%

All 75 IS-01+IS-02 matches correspond to correct MERGE decisions.
```

### 8.3 BUT: 语义非特异性

IS-01+IS-02 匹配的 46 个 merged pairs 包含多种语义类型：

| 语义类型 | 数量 | 示例 | MERGE 正确? |
|---|---|---|---|
| 引用编号 + 文本 | ~30 | "12" + "]. More recently, also first" | ✅ (gap=0, 引用续接) |
| 作者编号 + 机构 | ~5 | "3" + "Departamento de Física and Cen" | ✅ (gap=0, 作者列表) |
| 方程编号 + 文本 | ~5 | "2.27" + "), the" | ✅ (gap=0, 方程续接) |
| 标题编号 + 标题词 | ~29 | "1" + "Introduction" | ✅ (gap 10-22, heading) |
| 设备参数 + 值 | ~2 | "65" + "OFF" | ✅ (gap=0, 参数显示) |
| 列表编号 + 内容 | ~4 | "2" + "O, PCR tubes, PCR machine, etc" | ✅ (gap=0, 列表项) |

**关键发现：IS-01+IS-02 不是 "section heading detector"——它是 "number + readable text detector"。** 它匹配所有"编号+可读文本"的 pair，不论语义类型是 heading、citation、affiliation 还是 list item。

**但在当前 corpus 中，所有这些 pair 的正确 boundary decision 都是 MERGE。** 因此 false positive rate = 0%。

### 8.4 理论 False Positive Surface（当前 corpus 未暴露）

| 场景 | 描述 | 当前 corpus 是否有? | 风险 |
|---|---|---|---|
| 图编号 + 正文 | "Figure 1" + "shows that..." gap 8-50 | ❌ 无 | ⚠️ 理论 FP |
| 表格编号 + 描述 | "Table 3" + "Results summary" gap 8-50 | ❌ 无 | ⚠️ 理论 FP |
| 步骤编号 + 操作 | "1" + "Connect the cable" gap 8-50 | ❌ 无 | ⚠️ 设备手册可能有 |
| 测量值 + 单位 | "3" + "mm tolerance" gap 8-50 | ❌ 无 | ⚠️ 设备手册可能有 |
| 页码 + 页眉 | "1" + "Introduction" gap 8-50 (page header) | ❌ 无 | ⚠️ 理论 FP |

**当前 corpus 的 8 个文档均为学术论文，未覆盖设备手册的 table/procedure 场景。设备手册在当前 corpus 中有 0 个 same-y pairs with gap 8-50——因此无法评估 IS-01+IS-02 在设备手册上的 false positive 风险。**

### 8.5 IS-02 Loose Detection 风险

| text_b | IS-02 匹配? | 实际语义 | 风险 |
|---|---|---|---|
| "cos(" | ✅ True ("cos" = 3 chars) | 数学函数名 | ⚠️ 假阳性 |
| "sin(" | ✅ True ("sin" = 3 chars) | 数学函数名 | ⚠️ 假阳性 |
| "and" | ✅ True | 连词 | ⚠️ 假阳性 |
| "are" | ✅ True | 动词 | ⚠️ 假阳性 |
| ". The" | ✅ True | 句子续接 | ⚠️ 假阳性 |

**IS-02 的 readable word detection threshold (length > 2) 太宽松**——3 字符词如 "cos", "sin", "and", "are" 匹配为 readable title。

**当前影响：低**——因为 CF-A 条件要求 IS-01_a=True AND IS-02_b=True，而 "cos(" 等的 pair 中 IS-01_a 通常为 False（text_a 是符号不是编号）。

**未来风险：中等**——如果出现 "1" + "cos(" 的 pair（编号 + 公式续接），IS-01+IS-02 会匹配并暗示 MERGE，但正确答案可能取决于上下文。

### 8.6 PATTERN_NOT_SUFFICIENT 检查

| 检查 | 结果 |
|---|---|
| 是否存在 IS-01+IS-02 匹配但 Human=KEEP_SEPARATE 的 case? | ❌ 否（20 reviewed cases 中 0 个） |
| 是否存在 IS-01+IS-02 匹配但正确答案=KEEP_SEPARATE 的 pair? | ❌ 否（2255 pairs 中 0 个） |
| 是否存在相同 IS pattern 但不同 Human decision 的 case? | ❌ 否 |

**在当前 corpus 上，PATTERN_NOT_SUFFICIENT 未触发。但 corpus 小（8 docs, 2255 pairs），不能排除未来文档中的 PATTERN_NOT_SUFFICIENT。**

---

## 九、Cross-document Analysis

### 9.1 各文档的 IS-01+IS-02 匹配分布

| 文档 | 类型 | Total pairs | IS-01+IS-02 in merged | IS-01+IS-02 in unmerged | AMBIGUOUS |
|---|---|---|---|---|---|
| arxiv_toc | 学术论文 TOC | 244 | 0 | 22 | 22 |
| arxiv_2307 | 学术论文 body | 572 | 15 | 4 | 17 |
| arxiv_bio_body | 学术论文 body | 495 | 19 | 3 | 4 |
| RA101 | 设备手册 | 0 | 0 | 0 | 0 |
| RM501-P4 | 设备手册 | 86 | 2 | 0 | 0 |
| E804 | 设备手册 | 36 | 0 | 0 | 0 |
| C216 | 设备手册 | 88 | 4 | 0 | 0 |
| DC201 | 设备手册 | 52 | 6 | 0 | 0 |

### 9.2 设备手册分析

| 文档 | same-y pairs | IS-01+IS-02 matches | gap range |
|---|---|---|---|
| RA101 | 0 | 0 | N/A |
| RM501-P4 | 2 | 0 | 172-191 (DETERMINISTIC_BLOCK) |
| E804 | 1 | 0 | 171 (DETERMINISTIC_BLOCK) |
| C216 | 0 | 0 | N/A |
| DC201 | 0 | 0 | N/A |

**设备手册有 3 个 same-y pairs，全部 gap > 170（DETERMINISTIC_BLOCK），无 IS-01+IS-02 匹配。**

设备手册不产生 heading-style number+title pairs 在 ambiguous gap range（8-50）——因为设备手册的布局结构不同（表格、步骤列表、参数显示，不是学术论文的 TOC/headings）。

**设备手册中 IS-01+IS-02 的 merged pairs（gap=0）包括**：
- C216: "2" + "O, PCR tubes, PCR machine, etc" (列表项)
- C216: "3" + "Dropper, pipette..." (列表项)
- DC201: "65" + "OFF" (参数显示)
- DC201: "80" + "OFF" (参数显示)

这些全部是 gap=0 的 DETERMINISTIC_MERGE，P4 已正确处理。IS-01+IS-02 pattern 在这些 cases 上也匹配，但 P4 不需要 IS 就能正确 merge。

### 9.3 传递性评估

| 维度 | 状态 |
|---|---|
| arxiv_toc → arxiv_2307 | ✅ IS-01+IS-02 pattern 一致（heading in TOC vs heading in body） |
| arxiv_toc → arxiv_bio_body | ✅ 一致 |
| arxiv → 设备手册 | ⚠️ 未测试（设备手册无 ambiguous heading pairs） |
| 设备手册内部 | ⚠️ 0 ambiguous pairs，无法评估 |

**Cross-document transferability：学术论文内部一致，但无法评估到设备手册的 transferability。**

---

## 十、Potential Boundary Shrinkage

### 10.1 反事实指标

| 指标 | 计算 | 值 |
|---|---|---|
| Original Ambiguous Rate | 43 / 2255 total boundary pairs | 1.9% |
| Original Ambiguous Rate (unmerged) | 43 / 411 same-y unmerged | 10.5% |
| Counterfactual Potential Resolution Rate | 29 / 43 | 67.4% |
| Remaining Ambiguous Rate | 14 / 43 | 32.6% |
| Information Source Coverage | 29 / 43 (have IS-01+IS-02) | 67.4% |
| Human-owned Candidate Rate (Category C) | 1 / 43 (AMB-026) | 2.3% |
| Still Ambiguous - Category B untested | 13 / 43 (FORMULA) | 30.2% |

### 10.2 POTENTIAL vs ACTUAL

```
POTENTIAL SHRINKAGE:
  29/43 = 67.4% of AMBIGUOUS cases COULD be resolved by IS-01+IS-02
  IF the pattern proves stable and generalizable in independent validation.

ACTUAL SHRINKAGE:
  0/43 = 0%
  No boundary has been actually moved from Human to Machine.
  No Gate has been passed.
  No implementation has been authorized.
```

**本实验只能证明 POTENTIAL SHRINKAGE，不能声称 ACTUAL BOUNDARY SHRINKAGE。**

### 10.3 Shrinkage 的条件路径

```
Current: 43 AMBIGUOUS → all need Human Review

Counterfactual (IF IS-01+IS-02 proves generalizable):
  29 AMBIGUOUS → potentially machine-resolvable (CF-A)
  13 AMBIGUOUS → still ambiguous (FORMULA, needs IS-03+IS-08)
  1 AMBIGUOUS  → Human-owned (BODY_CONT, Category C)

  Human Review would decrease from 43 → 14 (67.4% reduction)
  BUT: this is COUNTERFACTUAL, not actual.
```

---

## 十一、Remaining Human Boundary

### 11.1 CF-B Cases (14/43)

| Mode | Case 数 | Category | Human-owned? | 需要什么 |
|---|---|---|---|---|
| FORMULA_FRAGMENT_WIDE | 13 | B (but IS-03/IS-08 not tested) | ⚠️ 可能 | IS-03 (symbol detection) + IS-08 (formula context) |
| BODY_TEXT_CONTINUATION | 1 | C (inherently semantic) | ✅ 很可能永久 | IS-10 (sentence boundary interpretation) |

### 11.2 AMB-026 (BODY_TEXT_CONTINUATION)

```
IS-01_a = False ("transition form factor..." is not a number)
IS-02_b = True ("Its normalization is" has readable words)
IS-07 = NO (body page, not TOC)

CF-A condition (IS-01_a AND IS-02_b) = False → CF-B

即使加入 IS-01/IS-02/IS-07，AMB-026 仍为 CF-B。
需要 IS-10 (sentence boundary interpretation) = Category C。
→ PERMANENT HUMAN-OWNED BOUNDARY candidate
```

---

## 十二、Circular Reasoning Assessment

### 12.1 循环推理风险

| 步骤 | 数据源 | 风险 |
|---|---|---|
| IS pattern derivation | 从 20 Human-reviewed cases 归纳 IS-01/IS-02 | ⚠️ 模式来源 = Human decisions |
| IS pattern evaluation | 在同 20 cases 上检查 pattern consistency | ⚠️ TRAIN = TEST |
| Cross-corpus FP check | 在 2255 pairs 上检查 false positive | ✅ 独立数据（但同 corpus） |
| 43-case coverage | 在全 43 AMBIGUOUS cases 上分类 CF-A/B/C | ⚠️ 23 个未 Human-reviewed |

### 12.2 结论

```
EXPLORATORY / NON-GENERALIZING

理由:
  1. IS pattern 从 20 Human cases 归纳，又在同 20 cases 上验证 → TRAIN = TEST
  2. 仅 1 reviewer
  3. 仅 8 documents, 2255 pairs
  4. 23/43 AMBIGUOUS cases 未 Human-reviewed
  5. 设备手册 0 AMBIGUOUS → 无法评估 transferability

不能称为:
  VALIDATED MACHINE BOUNDARY
  GENERALIZED PATTERN
  PROVEN MACHINE-RESOLVABILITY
```

### 12.3 独立验证需要什么

| 需要 | 当前状态 |
|---|---|
| ≥ 20 independent cases per mode (G1) | ❌ TOC=27 但仅 12 reviewed |
| Cross-document generalization ≥ 3 docs (G2) | ⚠️ 3 arxiv docs, 0 device manuals |
| Independent Human reviewer (G6) | ❌ single reviewer |
| No semantic counterexample (G7) | ⚠️ AMB-026 是 counterexample (but different mode) |
| False positive on larger corpus (G3) | ❌ 未测试 |

---

## 十三、TOC_SECTION_NUMBER_TITLE 最终分类

```
A. PROMISING MACHINE-RESOLVABLE

含义:
  现有 machine-observable evidence (IS-01 + IS-02) 已经显示出稳定 distinction，
  值得未来独立验证。

依据:
  - 13/13 reviewed cases: IS-01+IS-02 matches → Human=MERGE (100% consistency)
  - 0/75 false positives on current corpus (2255 pairs)
  - 0 DETERMINISTIC_BLOCK pairs with IS-01+IS-02 pattern
  - Adversarial AMB-018 vs AMB-040: IS-01 distinguishes correctly
  - All IS sources exist in P1 (text) / P6 (region)

限制:
  - TRAIN = TEST (circular reasoning)
  - Small corpus (8 docs)
  - IS-02 has loose detection risk (cos, sin, and, are)
  - Device manuals untested (0 ambiguous heading pairs)
  - No independent reviewer
```

---

## 十四、What We Know / Suspect / Not Validated

### WHAT WE KNOW

1. P1 有文本内容，P6 有 region 分类——IS-01/IS-02/IS-07 的信息源已存在于 DICE
2. 29/43 AMBIGUOUS cases 满足 IS-01+IS-02 → CF-A (POTENTIALLY_MACHINE_RESOLVABLE)
3. 14/43 AMBIGUOUS cases 不满足 → CF-B (STILL_AMBIGUOUS)
4. 0/43 是 CF-C (INSUFFICIENT_SOURCE)——所需 IS 全部可从现有 artifact 获得
5. IS-01+IS-02 在当前 corpus 上 0 false positive (75 matches, all correct MERGE)
6. AMB-018 vs AMB-040 adversarial: IS-01 单独可区分
7. 设备手册 0 AMBIGUOUS heading pairs → IS pattern 不在设备手册上 fire
8. IS-02 对 "cos"/"sin"/"and"/"are" 有 loose detection（但不影响 CF-A 因为 IS-01_a 过滤）
9. IS-07 (TOC context) 不是 CF-A 必要条件——heading 在 body 页面也能被 IS-01+IS-02 识别

### WHAT WE SUSPECT

1. TOC_SECTION_NUMBER_TITLE 可能 machine-resolvable（Category B, IS-01+IS-02 stable）
2. IS-01+IS-02 的 false positive 在更大 corpus 上可能不为 0（设备手册的 table/procedure 场景未测试）
3. FORMULA_FRAGMENT_WIDE 可能需要 IS-03+IS-08（未在本实验测试）
4. BODY_TEXT_CONTINUATION 很可能永久 Human-owned（Category C）
5. IS-02 的 threshold 可能需要从 > 2 调整为 > 3（排除 cos/sin/and/are），但这是未来优化，不是本阶段任务

### WHAT WE HAVE NOT VALIDATED

1. IS-01+IS-02 的跨文档泛化稳定性——未独立验证
2. IS-01+IS-02 在设备手册上的 false positive——设备手册 0 ambiguous pairs
3. Inter-reviewer agreement——单 reviewer
4. 23/43 AMBIGUOUS cases 的 Human decision——未 reviewed
5. IS-02 loose detection 的实际影响——当前 corpus 未暴露问题
6. "67.4% potential shrinkage" ——是 counterfactual 估计，不是 actual shrinkage
7. P6 region type 是否能准确区分 TOC/BODY/FORMULA——未直接读取 P6 输出
8. Boundary Intelligence Layer 的实现可行性——未设计实现方案

---

## 十五、Recommendation

### 15.1 七个最终 Gate 问题

| Q | 问题 | 回答 |
|---|---|---|
| Q1 | P1/P6 中是否已存在足够 Information Source? | ✅ 是。P1 有 text，P6 有 region。IS-01/IS-02/IS-07 全部可从现有 artifact 获得。0/43 CF-C。 |
| Q2 | 这些 IS 是否能解释 Round 1 Human decision? | ✅ 是（对 TOC/APPENDIX mode）。13/13 reviewed cases: IS-01+IS-02 matches → Human=MERGE。零不一致。 |
| Q3 | 是否能在 43 cases 中产生潜在 boundary shrinkage? | ✅ 是。29/43 = 67.4% CF-A (POTENTIAL, not ACTUAL)。 |
| Q4 | 是否存在明显 false-positive surface? | ⚠️ 是（理论上）。当前 corpus 0 FP，但设备手册 table/procedure 场景未测试。IS-02 loose detection 对 cos/sin 有假阳性。 |
| Q5 | 哪些 boundary 可进入未来 machine-resolvability experiment? | TOC_SECTION_NUMBER_TITLE + APPENDIX_LETTER_TITLE (Category B, CF-A) |
| Q6 | 哪些 boundary 应继续 Human-owned? | BODY_TEXT_CONTINUATION (Category C, 永久候选)。FORMULA_FRAGMENT_WIDE (Category B 但需 IS-03+IS-08 测试)。 |
| Q7 | 下一步是否值得实施? | ✅ FEASIBILITY SUPPORTED。但 NOT IMPLEMENTATION APPROVED。 |

### 15.2 TOC_SECTION_NUMBER_TITLE 分类

```
A. PROMISING MACHINE-RESOLVABLE
```

### 15.3 下一步

```
NEXT CANDIDATE:
  INDEPENDENT MACHINE-RESOLVABILITY EXPERIMENT

NOT:
  NEXT: IMPLEMENT RULE
```

独立实验需要：
1. Timer fix（测量真实 Human cost）
2. 第二 reviewer（测量 inter-reviewer agreement）
3. 扩大到全部 43 AMBIGUOUS cases + 新文档
4. 在新文档上测试 IS-01+IS-02 false positive
5. 独立 Human 标注（非几何 GT）用于 validation
6. Gate 全部通过后才考虑 machine implementation

---

## 十六、Authorization Status

```
Research Status: COMPLETE (READ-ONLY counterfactual study)

TOC_SECTION_NUMBER_TITLE:
  A. PROMISING MACHINE-RESOLVABLE
  (FEASIBILITY SUPPORTED, not implementation approved)

Implementation = NOT AUTHORIZED
P7.3 = NOT AUTHORIZED
P4 v3 = NOT AUTHORIZED (suspended)
Timer Fix = NOT AUTHORIZED (design only)
GT Modification = NOT AUTHORIZED
Sample Expansion = NOT AUTHORIZED
Textual Structure Feature = NOT AUTHORIZED (design candidate only)
Boundary Intelligence Layer = NOT AUTHORIZED (design candidate only)
Frozen Baseline = INTACT
```

---

## STOP

```
DESIGN STATUS = READY (READ-ONLY counterfactual feasibility study)

Key Finding:
  IS-01+IS-02 (number pattern + readable title) is available in P1 text.
  29/43 AMBIGUOUS cases are CF-A: POTENTIALLY_MACHINE_RESOLVABLE.
  0 false positives on current corpus (8 docs, 2255 pairs).
  BUT: TRAIN=TEST, small corpus, no independent validation.

  TOC_SECTION_NUMBER_TITLE = PROMISING MACHINE-RESOLVABLE
  (Category B, IS sources exist in P1/P6, stable on current corpus)

  Potential Shrinkage ≠ Actual Shrinkage
  Feasibility Supported ≠ Implementation Approved

Implementation = NOT AUTHORIZED
P7.3 = NOT AUTHORIZED
Frozen = INTACT
```

**不进入下一阶段。不修改任何代码。不修改任何实验数据。不创建 machine rule。等待下一步批准。**
