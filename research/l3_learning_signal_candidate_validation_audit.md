# L3 Learning Signal Candidate Validation Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY / NO IMPLEMENTATION / NO NEW MODULE / FROZEN INTACT / STOP

---

## 1. Executive Summary

```
TRUE_LEARNING_SIGNAL_FOUND       = NO
CURRENT_LEARNING_LEVEL           = L3 (maintained — NOT upgraded to L4)
L4_CANDIDATE                     = FALSE (all 3 signals fail L4 criteria)

SIGNAL_1 (has_fig_prefix → MERGE)     = TEMPORARY_MACHINE_GAP + KEYWORD_RECURRENCE
SIGNAL_2 (line_obs ≥ 6 → KEEP)        = TEMPORARY_MACHINE_GAP + POST-HOC THRESHOLD
SIGNAL_3 (line_obs≥3 AND NOT fig → KEEP) = TEMPORARY_MACHINE_GAP + BOUNDARY_OVERCOMMIT

COUNTERFACTUAL_INFO_GAIN          = >0 (all 3 — rule discovery requires Human labels)
FEATURE_INFO_GAIN                 = 0 (all features exist in P1/P2 or are derivable)

E2_DEEP_SPLIT:
  E2-A (complete info, unorganized)  = 35/35 (100%)
  E2-B (proxy discovery via Human)   = 35/35 (100%)
  E2-C (semantic boundary)           = 0/35 (0%)

E5_DEEP_SPLIT:
  E5-FIG (keyword recurrence)        = 2/10 (20%) — KEYWORD_RECURRENCE
  E5-PROSE (sentence structure)      = 8/10 (80%) — 7/8 reclassifiable to E2

BOUNDARY_OVERCOMMIT:
  4 disagreement cases (reviewers split 50/50) → Signal 3 gives decisive answer
  2 P722 UNKNOWN cases → Signal 3 gives decisive answer where Human was uncertain

FUTURE_REUSE                      = INSUFFICIENT (0 future cases)
IMPLEMENTATION_AUTHORIZED         = FALSE
STOP                              = TRUE
```

> **3 个 Signal Candidates 的 Counterfactual Information Gain > 0——Human Feedback 提供了 Machine 无法自行发现的规则（feature → label 关联）。但所有特征（text, line_obs_count）已存在于 P1/P2 或可确定性派生。信息增益在规则发现层面，不在特征层面。3 个信号均被分类为 TEMPORARY_MACHINE_GAP，均未满足 L4 的 9 项条件。Signal 3 虽然在当前 45 案例上达到 93% 覆盖率和 0 false positive，但在 4 个 reviewer 分歧案例上存在 BOUNDARY_OVERCOMMIT——Signal 3 在 Human 不确定时给出确定性答案。Learning Level 维持 L3。**

---

## 2. Research Question

> **判断当前 3 个 Learning Signal Candidates 是否真正满足："Human Feedback 提供了 Machine 过去没有显式掌握、且未来可以被安全复用的信息。"**

核心判据：如果 Machine 在 Human Feedback 之前，仅利用已存在的 P1-P7 / TLD / Evidence / Structural Facts，就可以确定该 Signal，则 SIGNAL_INFORMATION_GAIN = 0。

---

## 3. Feature Origin Verification

### 3.1 Candidate Universe Metadata (FROZEN)

```json
{
  "note": "NO IS-01, IS-02, IS-11, ambiguity_mode, or ground_truth_label computed.
           Text_a/text_b are P1 output (CORPUS PREPROCESSING).
           All features are geometric only (pure geometric slice).
           table_line_detector.py was NOT called."
}
```

### 3.2 Feature Availability Matrix

| Feature | Source | Exists in P1-P7? | Derivable without Human? |
|---|---|---|---|
| text_a, text_b | P1 (corpus preprocessing) | **YES** | YES |
| bbox_a, bbox_b | P2 (geometry) | **YES** | YES |
| h_gap, dy | P2 (geometry) | **YES** | YES |
| same_style | P3 (style) | **YES** | YES |
| line_obs_count | NOT in P2 output | **DERIVABLE** from P1 (count same-y observations) | YES |
| line_spans | P4 (span_v2) | **YES** | YES |
| has_fig_prefix | NOT explicitly computed | **DERIVABLE** from P1 text (trivial string check) | YES |
| TLD is_in_table | TLD (table_line_detector) | **YES** (but failed on H2) | YES (but unreliable) |

### 3.3 Key Finding

> **ALL features used by the 3 signal candidates are either explicitly in P1-P7 output or deterministically derivable from existing output. No feature requires Human feedback for computation. The information gain is NOT in feature availability — it is in RULE DISCOVERY (feature → label association).**

---

## 4. Signal Candidate Evaluation Cards

### 4.1 Signal 1: has_fig_prefix → MERGE

#### A. Human Feedback 中出现了什么信息？

Human 对 2 个 MERGE 案例提供了 MERGE 标签。这两个案例的 text_a 都以 "FIG." 开头。

#### B. 该信息是否已存在于 P1-P7 / TLD / Evidence？

- `text_a` = "FIG. 9:" / "FIG. 12:" → **YES, in P1**
- `has_fig_prefix` = text.startsWith("FIG") → **DERIVABLE, trivial string check**
- TLD is_in_table = False → **YES, but TLD didn't help** (detected 0 tables)

#### C. 如果 Human 不提供反馈，Machine 是否可以仅通过现有 Evidence 推导出该 Signal？

**NO.** Machine 有 text（可以检查 "FIG." 前缀），但没有 MERGE 标签。Machine 无法知道 "FIG." 前缀与 MERGE 的关联。

#### D. INFO_GAIN

- Feature info gain = 0 (text exists, has_fig_prefix derivable)
- Rule info gain = **> 0** (association requires Human labels)

#### E. Machine 缺失的最小信息

"FIG. 前缀 → MERGE" 这个关联规则。Machine 没有任何方式从现有 evidence 独立推导出这个规则——它需要知道哪些案例是 MERGE。

#### F. 信息类别

- Feature: E1 (Existing Explicit — text in P1)
- Rule: E5 (Human Semantic Interpretation — text pattern → label)

#### G. Human 是否提供了新的语义信息？

**YES.** Human 提供了 "FIG. 前缀意味着这两个 text span 是同一 figure caption 的部分，应 MERGE"。这是语义解释。

#### H. 是否可跨案例稳定复用？

**UNTESTED.** n=2，全部来自 1 个文档（is11_med_001）。无法验证跨文档稳定性。

#### I. 是否存在至少两个不同 document/page/context？

**NO.** 2 个案例都来自 is11_med_001（不同 page: 20, 24）。同一文档。

#### J. 是否存在反例？

**无反例。** 43 个非 FIG 案例全部 KEEP_SEPARATE。但样本量 n=2 太小，无法确认无反例。

#### K. 是否存在 UNKNOWN / CONFLICT 边界？

**NO.** 2 个 FIG 案例都是明确的 MERGE，无 reviewer 分歧。但 n=2 无法排除边界情况。

#### L. 是否只是 keyword recurrence？

**YES — 这是 KEYWORD_RECURRENCE。** "FIG." 是学术论文中的标准前缀，但在当前数据中只在 2 个案例中出现，全部来自 1 个文档。这更像是关键词重复而非可泛化的 Learning Signal。

**Classification: TEMPORARY_MACHINE_GAP + KEYWORD_RECURRENCE**

---

### 4.2 Signal 2: line_obs_count ≥ 6 → KEEP_SEPARATE

#### A. Human Feedback 中出现了什么信息？

Human 对 28 个 line_obs_count ≥ 6 的案例提供了 KEEP_SEPARATE 标签。

#### B. 该信息是否已存在于 P1-P7 / TLD / Evidence？

- `line_obs_count` → **NOT in P2 output**, but **DERIVABLE** from P1 (count observations on same y-band)
- TLD is_in_table = False for most → **YES, but TLD didn't help**

#### C. 如果 Human 不提供反馈，Machine 是否可以推导出该 Signal？

**NO.** Machine 可以计算 line_obs_count（从 P1 派生），但没有 KEEP_SEPARATE 标签。Machine 无法知道 threshold = 6 或 line_obs_count 与 KEEP_SEPARATE 的关联。

#### D. INFO_GAIN

- Feature info gain = 0 (line_obs_count derivable)
- Rule info gain = **> 0** (threshold + association requires Human labels)

#### E. Machine 缺失的最小信息

"line_obs_count ≥ 6 → KEEP_SEPARATE" 这个阈值规则。特别是 threshold = 6 这个具体数值。

#### F. 信息类别

- Feature: E3 (Derived — line_obs_count not in P2, but derivable from P1)
- Rule: E2-B (Proxy Discovery — line_obs_count is proxy for "table row membership")

#### G. Human 是否提供了新的语义信息？

**PARTIAL.** Human 没有直接提供语义信息。Human 提供的是 LABEL（KEEP_SEPARATE），System 通过分析发现 line_obs_count 是一个有用的 proxy。语义解释（"多个 items 在同一行 = 表格行"）是 System 从标签反推的。

#### H. 是否可跨案例稳定复用？

**MODERATE.** 28 个案例，4 个文档。但 threshold = 6 是 post-hoc 选择，存在 overfitting 风险。

#### I. 是否存在至少两个不同 document/page/context？

**YES.** 4 个文档（is11_resnet, is11_efficientnet, is11_med_001, is11_cs_001）。

#### J. 是否存在反例？

**NO false positive** on current 45 cases。但 threshold = 6 排除了 17 个 line_obs 3-5 的案例，这些案例中有 KEEP_SEPARATE（正确排除）但也可能有未来的 MERGE 案例（未知）。

#### K. 是否存在 UNKNOWN / CONFLICT 边界？

**PARTIAL.** 4 个 reviewer 分歧案例中：
- AMB-005: line_obs=3 → 不触发 Signal 2
- AMB-375: line_obs=3 → 不触发
- AMB-418: line_obs=7 → 触发，预测 KEEP_SEPARATE（matches final, but reviewer B said MERGE）
- AMB-519: line_obs=2 → 不触发

1/4 分歧案例被 Signal 2 覆盖，且给出确定性答案。

#### L. 是否只是 threshold fitting？

**YES — 这是 POST-HOC THRESHOLD FITTING.** threshold = 6 是通过分析 45 个案例事后选择的，不是自然阈值。在其他数据集上，最优阈值可能是 5 或 7。

**Classification: TEMPORARY_MACHINE_GAP + POST-HOC THRESHOLD**

---

### 4.3 Signal 3: line_obs_count ≥ 3 AND NOT has_fig_prefix → KEEP_SEPARATE

#### A. Human Feedback 中出现了什么信息？

Human 对 42 个满足条件的案例提供了 KEEP_SEPARATE 标签。

#### B. 该信息是否已存在于 P1-P7 / TLD / Evidence？

- `line_obs_count` → **DERIVABLE** from P1
- `has_fig_prefix` → **DERIVABLE** from P1 text
- 两个特征都可在无 Human 反馈时计算

#### C. 如果 Human 不提供反馈，Machine 是否可以推导出该 Signal？

**NO.** Machine 有两个特征，但没有 KEEP_SEPARATE 标签。Machine 无法知道 composite rule。

#### D. INFO_GAIN

- Feature info gain = 0 (both features derivable)
- Rule info gain = **> 0** (composite rule requires Human labels)

#### E. Machine 缺失的最小信息

"line_obs ≥ 3 AND NOT fig → KEEP_SEPARATE" 这个复合规则。特别是 threshold = 3 和 NOT fig 的组合。

#### F. 信息类别

- Features: E1 (text) + E3 (line_obs derivable)
- Rule: E2-B (Proxy Discovery) + E5 (text pattern component)

#### G. Human 是否提供了新的语义信息？

**PARTIAL.** "NOT fig" 组件是文本模式识别（E5）。line_obs ≥ 3 是 proxy threshold（E2-B）。组合后，Human 间接提供了 "非 FIG 文本 + 多个同行 items = 表格列" 的语义关联。

#### H. 是否可跨案例稳定复用？

**MODERATE.** 42 个案例，4 个文档。但 composite rule 有 post-hoc 组件。

#### I. 是否存在至少两个不同 document/page/context？

**YES.** 4 个文档。

#### J. 是否存在反例？

**0 false positive** on current 45 cases。但：

#### K. 是否存在 UNKNOWN / CONFLICT 边界？

**YES — BOUNDARY_OVERCOMMIT.**

4 个 reviewer 分歧案例（A=KEEP_SEPARATE, B=MERGE, final=KEEP_SEPARATE）：
- AMB-005: line_obs=3, no FIG → Signal 3 触发 → KEEP_SEPARATE（matches final, but 50% reviewer said MERGE）
- AMB-375: line_obs=3, no FIG → Signal 3 触发 → KEEP_SEPARATE（matches final, but P722 B2 Human said UNKNOWN, 31.3s）
- AMB-418: line_obs=7, no FIG → Signal 3 触发 → KEEP_SEPARATE（matches final, but 50% reviewer said MERGE）
- AMB-519: line_obs=2, no FIG → Signal 3 不触发 → 未覆盖

**3/4 分歧案例被 Signal 3 覆盖，且全部给出确定性 KEEP_SEPARATE。但其中：**
- 3 个案例有 reviewer 说 MERGE（50% 分歧）
- 1 个案例（AMB-375）在 P722 B2 中 Human 说 UNKNOWN（31.3s，展开所有字段）

> **Signal 3 在 Human 不确定时给出确定性答案——这是 BOUNDARY_OVERCOMMIT。Signal 3 无法识别 AMBIGUOUS 案例为 UNKNOWN。**

#### L. 是否只是 keyword recurrence + threshold？

**PARTIAL.** "NOT fig" 是 keyword 检查。"line_obs ≥ 3" 是 threshold。组合后比单独使用更强，但仍然是 post-hoc rule fitting。

**Classification: TEMPORARY_MACHINE_GAP + BOUNDARY_OVERCOMMIT**

---

## 5. Counterfactual Analysis

### 5.1 Test Design

| State | Machine Has | Machine Lacks |
|---|---|---|
| STATE A (no Human) | P1 text, P2 geometry, P4 spans, TLD output | KEEP_SEPARATE / MERGE labels |
| STATE B (with Human) | P1 + P2 + P4 + TLD + **Human labels** | — |

### 5.2 Results

| Signal | STATE A: Can Machine derive? | STATE B: Can Machine derive? | Counterfactual Gain | Classification |
|---|---|---|---|---|
| Signal 1 (has_fig → MERGE) | **NO** (has fig feature, but no MERGE label → no rule) | **YES** (Human provides MERGE label → rule discovered) | **> 0** | TEMPORARY_MACHINE_GAP |
| Signal 2 (line_obs≥6 → KEEP) | **NO** (has line_obs, but no KEEP label → no threshold) | **YES** (Human provides KEEP label → threshold found) | **> 0** | TEMPORARY_MACHINE_GAP |
| Signal 3 (composite → KEEP) | **NO** (has both features, but no label → no rule) | **YES** (Human provides label → composite rule found) | **> 0** | TEMPORARY_MACHINE_GAP |

### 5.3 Critical Distinction

> **Counterfactual Info Gain > 0 for all 3 signals — BUT the gain is in RULE DISCOVERY, not in FEATURE AVAILABILITY. Machine has all features; Human provides the LABELS that enable rule discovery. This is supervised pattern fitting, not genuine learning without validation and reuse.**

### 5.4 Classification of Information Gain

All 3 signals are **TEMPORARY_MACHINE_GAP**:
- Machine CAN compute all features (E1/E3)
- Machine CANNOT discover the rule without Human labels
- Once rule is discovered, Machine CAN apply it automatically
- Human is needed for DISCOVERY (label provision), not for APPLICATION

**NONE are PERSISTENT_HUMAN_SEMANTIC_SIGNAL**:
- No signal requires ongoing Human semantic judgment for every case
- All signals, once discovered, could be automated

**NONE are REORGANIZATION_ONLY**:
- Reorganization would mean Machine could derive the rule without Human
- But Machine cannot (no labels) → not pure reorganization

---

## 6. E2 78% Deep Split

### E2-A: Machine already has COMPLETE information, just not organized

```
Count: 35/35 (100% of E2)
Features: text (P1), line_obs_count (derivable from P1), geometry (P2)
Rule: MISSING (requires Human labels)
Info Gain for features: 0
Info Gain for rule: > 0
```

> **所有 E2 案例的底层特征已完整存在于 P1/P2。Machine 缺的不是信息，而是规则。**

### E2-B: Machine has PARTIAL information, Human exposes a new relation interpretation

```
Count: 35/35 (100% of E2)
Proxy: line_obs_count → "table row membership"
Missing: Machine doesn't compute "is this a table row?" explicitly
Human feedback reveals: line_obs_count is a useful proxy for KEEP_SEPARATE
```

> **line_obs_count 是 "table row membership" 的 proxy。TLD 试图直接检测表格但失败。Human feedback 间接揭示了 line_obs_count 作为 proxy 的价值。**

### E2-C: Human feedback exposes a new semantic boundary

```
Count: 0/35 (0% of E2)
Reason: E2 cases have no FIG prefix → no semantic boundary issue
E2-C applies to E5 cases instead
```

### E2 Split Summary

| Sub-category | Count | Nature | Info Gain |
|---|---|---|---|
| E2-A (complete info, unorganized) | 35 (100%) | Features exist, rule missing | Rule > 0 |
| E2-B (proxy discovery) | 35 (100%) | line_obs as proxy for table row | Proxy > 0 |
| E2-C (semantic boundary) | 0 (0%) | Not applicable to E2 | — |

> **E2 的 78% 不是单纯的 "Evidence Organization"。它包含 REORGANIZATION (E2-A, features exist) + PROXY DISCOVERY (E2-B, Human reveals proxy utility)。两者都有 info gain > 0，但都是在规则层面，不在特征层面。**

---

## 7. E5 22% Deep Split

### E5-FIG: Keyword Recurrence

```
Count: 2/10 (20% of E5)
Cases: AMB-414 ('FIG. 9:' / 'Left:'), AMB-422 ('FIG. 12:' / 'Distribution...')
GT: MERGE (2/2)
Pattern: text starts with 'FIG' → MERGE
Nature: KEYWORD_RECURRENCE
Cross-document: NO (both from is11_med_001)
n = 2 → generalization UNTESTED
```

> **"FIG." 前缀 → MERGE 是关键词重复。n=2，单一文档。这不足以构成可泛化的 Learning Signal。**

### E5-PROSE: Sentence Structure

```
Count: 8/10 (80% of E5)
Cases: AMB-005, AMB-375, AMB-380, AMB-401, AMB-407, AMB-409, AMB-418, AMB-519
GT: KEEP_SEPARATE (8/8)
Pattern: sentence boundary / punctuation / prose structure
```

**Reclassification check:**

| Case | line_obs | FIG? | Signal 3 covers? | Actual evidence |
|---|---|---|---|---|
| AMB-005 | 3 | N | YES → KEEP | Sentence boundary (prose) |
| AMB-375 | 3 | N | YES → KEEP | Citation + sentence (prose) |
| AMB-380 | 7 | N | YES → KEEP | Figure diagram labels (E2-like) |
| AMB-401 | 10 | N | YES → KEEP | Axis tick labels (E2-like) |
| AMB-407 | 10 | N | YES → KEEP | Axis tick labels (E2-like) |
| AMB-409 | 10 | N | YES → KEEP | Axis tick labels (E2-like) |
| AMB-418 | 7 | N | YES → KEEP | Sentence boundary (prose) |
| AMB-519 | 2 | N | **NO** (line_obs < 3) | Sentence boundary (prose) |

> **7/8 E5-PROSE 案例可被 Signal 3 覆盖（line_obs ≥ 3），实际上应重分类为 E2。只有 AMB-519（line_obs=2）是真正的 E5——需要 Human 语义判断（句子边界）。**

### E5 Corrected Distribution

| Sub-category | Count | Nature |
|---|---|---|
| E5-FIG (keyword) | 2 | KEYWORD_RECURRENCE, n=2, 1 doc |
| E5-PROSE (reclassifiable to E2) | 7 | Covered by Signal 3 |
| E5-PROSE (genuine semantic) | 1 (AMB-519) | PERSISTENT_HUMAN_SEMANTIC_JUDGMENT |

> **E5 的 22% 深度拆分后：真正需要 Human 语义判断的只有 1 个案例（AMB-519，line_obs=2，句子边界）。其余 9 个要么是关键词重复（2），要么可被 Signal 3 覆盖（7）。**

---

## 8. Novelty / Grounding / Reusability / Discrimination

### Signal Matrix

| Candidate | Novelty | Grounding | Reusability | Discriminative Value | Counterfactual Gain | Classification |
|---|---|---|---|---|---|---|
| Signal 1 (has_fig→MERGE) | **LOW** (keyword) | E1 (text in P1) | **LOW** (n=2, 1 doc) | **HIGH** (2/2 MERGE, 0/43 others) | >0 | TEMPORARY_MACHINE_GAP |
| Signal 2 (line_obs≥6→KEEP) | **LOW** (threshold) | E3 (derivable from P1) | **MODERATE** (28 cases, 4 docs) | **MODERATE** (62% coverage, 0 FP) | >0 | TEMPORARY_MACHINE_GAP |
| Signal 3 (composite→KEEP) | **MODERATE** (composite) | E1+E3 | **MODERATE** (42 cases, 4 docs) | **HIGH** (93% coverage) **BUT** boundary overcommit | >0 | TEMPORARY_MACHINE_GAP |

### Four Core Properties Detail

#### 1. NOVELTY

| Signal | Novelty | Reason |
|---|---|---|
| Signal 1 | LOW | "FIG." is a standard academic keyword, not novel information |
| Signal 2 | LOW | line_obs_count is a simple count, threshold is post-hoc |
| Signal 3 | MODERATE | Composite rule is non-trivial, but components are simple |

> **Human 提供的是 LABELS，不是新的特征或新的计算方法。Novelty 在规则发现层面，不在信息层面。**

#### 2. GROUNDING

| Signal | Grounding | Evidence | Traceable? |
|---|---|---|---|
| Signal 1 | YES | text_a in P1 | YES (trivial string check) |
| Signal 2 | YES | line_obs_count derivable from P1 | YES (count same-y observations) |
| Signal 3 | YES | text + line_obs | YES (both traceable) |

> **所有信号都 evidence-grounded——可追溯到 P1/P2 中的具体 evidence。**

#### 3. REUSABILITY

| Signal | Cross-document? | Cross-page? | n | Future cases? |
|---|---|---|---|---|
| Signal 1 | NO (1 doc) | YES (2 pages) | 2 | 0 |
| Signal 2 | YES (4 docs) | YES | 28 | 0 |
| Signal 3 | YES (4 docs) | YES | 42 | 0 |

> **Signal 2 和 3 有跨文档支持（4 个文档），但无 future cases 验证。Signal 1 仅 1 个文档，n=2。**

#### 4. DISCRIMINATIVE VALUE

| Signal | KEEP | MERGE | UNKNOWN | Boundary (disagree) |
|---|---|---|---|---|
| Signal 1 | 0/43 | **2/2** | N/A | N/A |
| Signal 2 | 28/43 | 0/2 | N/A | 1/4 (overcommit) |
| Signal 3 | **42/43** | 0/2 | N/A | **3/4 (overcommit)** |

> **Signal 3 的 discriminative value 最高（93% coverage），但在 4 个分歧案例上 BOUNDARY_OVERCOMMIT——给出确定性答案而非 UNKNOWN。**

---

## 9. Boundary Overcommit Analysis

### 9.1 Reviewer Disagreement Cases (4 cases)

| Case | Reviewer A | Reviewer B | Final | line_obs | Signal 3 predicts | P722 B2 Human |
|---|---|---|---|---|---|---|
| AMB-005 | KEEP_SEPARATE | MERGE | KEEP_SEPARATE | 3 | KEEP_SEPARATE | KEEP_SEPARATE (followed cue) |
| AMB-375 | KEEP_SEPARATE | MERGE | KEEP_SEPARATE | 3 | KEEP_SEPARATE | **UNKNOWN** (31.3s!) |
| AMB-418 | KEEP_SEPARATE | MERGE | KEEP_SEPARATE | 7 | KEEP_SEPARATE | KEEP_SEPARATE (12.2s) |
| AMB-519 | KEEP_SEPARATE | MERGE | KEEP_SEPARATE | 2 | **uncovered** | KEEP_SEPARATE (2.0s) |

### 9.2 P722 UNKNOWN Cases (2 cases)

| Case | Condition | Decision | Time | GT | Signal 3 predicts |
|---|---|---|---|---|---|
| AMB-032 | B2 | **UNKNOWN** | 45.9s | KEEP_SEPARATE | KEEP_SEPARATE (line_obs=3) |
| AMB-375 | B2 | **UNKNOWN** | 31.3s | KEEP_SEPARATE | KEEP_SEPARATE (line_obs=3) |

### 9.3 Finding

> **Signal 3 在 2 个 P722 UNKNOWN 案例上给出确定性 KEEP_SEPARATE。但 P722 Human 在这些案例上花费 31-46 秒后选择了 UNKNOWN。Signal 3 无法识别这些案例为 AMBIGUOUS——它在 Human 不确定时仍然给出确定性答案。这是 BOUNDARY_OVERCOMMIT。**

> **一个真正的 Learning Signal 应该能够：(1) 正确分类明确案例，(2) 识别模糊案例为 UNKNOWN。Signal 3 只做到 (1)，未做到 (2)。**

---

## 10. L4 Candidate Decision

### 10.1 L4 Requirements (9 criteria)

| # | Criterion | Signal 1 | Signal 2 | Signal 3 |
|---|---|---|---|---|
| 1 | Human provided info Machine couldn't determine | YES (rule) | YES (rule) | YES (rule) |
| 2 | Evidence-grounded | YES | YES | YES |
| 3 | Non case-specific | **NO** (n=2, 1 doc) | PARTIAL | PARTIAL |
| 4 | Cross document/page reuse possible | **NO** | YES (4 docs) | YES (4 docs) |
| 5 | Has positive examples | 2 | 28 | 42 |
| 6 | Has negative examples or boundary conditions | **NO** | PARTIAL | YES (4 disagree) |
| 7 | Doesn't require Human to write rules | YES | YES | YES |
| 8 | No Runtime Authority | YES | YES | YES |
| 9 | No new Architecture Layer | YES | YES | YES |

### 10.2 Decision

```
L4_CANDIDATE (Signal 1) = FALSE (fails #3, #4, #6)
L4_CANDIDATE (Signal 2) = FALSE (fails #6 — boundary overcommit on AMB-418)
L4_CANDIDATE (Signal 3) = FALSE (fails #6 — boundary overcommit on 3/4 disagree cases)
```

> **没有任何信号满足全部 9 项 L4 条件。Signal 3 最强但失败于 #6（boundary conditions）——它在分歧案例上 BOUNDARY_OVERCOMMIT。**

---

## 11. Learning Level Assessment

| Level | Status | Evidence |
|---|---|---|
| L0 Raw Human Judgment | ✓ | Human provides KEEP_SEPARATE / MERGE |
| L1 Feedback Storage | ✓ | GT stores feedback |
| L2 Evidence Reorganization / Aggregation | ✓ | SAME_BAND_SEPARATED_PAIR (zero info gain) |
| **L3 Evidence-grounded Signal Candidate** | **✓** | 3 candidates with info gain > 0, evidence-grounded |
| L4 Human-validated Reusable Signal | **✗** | No signal meets all 9 criteria |
| L5 Future Case Reuse | ✗ | 0 future cases |
| L6 Measured HRR | ✗ | Not measurable |
| L7 Continuous validated improvement | ✗ | — |

```
CURRENT_LEARNING_LEVEL = L3 (maintained — NOT upgraded)
```

> **L3 Candidate Discovery 已建立——3 个 evidence-grounded signal candidates 被发现，info gain > 0。但尚未证明 Human-validated reusable learning。L4 未达到。**

---

## 12. True Learning Signal Assessment

```
TRUE_LEARNING_SIGNAL_FOUND = NO
```

### Why NO?

1. **所有特征的 info gain = 0** — text, line_obs_count 都已存在于 P1/P2 或可派生
2. **规则发现的 info gain > 0** — 但这是 supervised pattern fitting，不是 genuine learning
3. **无 Human validation** — L4 未达到
4. **无 future case reuse** — L5 未达到
5. **Boundary overcommit** — Signal 3 在分歧案例上过度确定
6. **Keyword recurrence** — Signal 1 是关键词重复 (n=2)
7. **Post-hoc threshold** — Signal 2/3 的阈值是事后选择

### What WAS found?

- **TEMPORARY_MACHINE_GAP** — Machine 有特征但没有规则。Human feedback 帮助发现规则。
- **EVIDENCE_REORGANIZATION + PROXY DISCOVERY** — line_obs_count 作为 table row membership 的 proxy。
- **COUNTERFACTUAL_INFO_GAIN > 0** — 但在规则层面，不在特征层面。

---

## 13. Final Research Questions

### Q1: 3 个 Candidate 中哪个最值得进入下一阶段？

**Signal 3 (line_obs ≥ 3 AND NOT fig → KEEP_SEPARATE)。**

理由：
- 最高覆盖率（93%）
- 0 false positive on current 45 cases
- 跨 4 个文档
- 但需要解决 BOUNDARY_OVERCOMMIT 问题

### Q2: 哪些 Candidate 应永久关闭？

**Signal 1 (has_fig_prefix → MERGE) 应关闭。**

理由：
- n=2，单一文档
- KEYWORD_RECURRENCE
- 无跨文档验证
- 覆盖率仅 4%

Signal 2 可合并入 Signal 3（Signal 3 是 Signal 2 的超集）。

### Q3: 是否需要 Future Independent Cases？

**YES — 这是进入 L4/L5 的必要条件。**

### Q4: Future Case 的最小独立性条件？

- **Level A（最强）**：不同文档 + 不同页面 + 非近似重复
- **Level B**：不同文档
- **Level C（弱）**：同文档 + 不同页面
- **Level D（禁止）**：同页面

最小要求：至少 Level B（不同文档），至少 10 个 future cases。

### Q5: Human 下一阶段是否只需要 [合适 / 不合适 / 不确定] 最小反馈？

**YES — Human 只需要提供最小标签（KEEP_SEPARATE / MERGE / UNKNOWN）。**

- 不需要 Human 写规则
- 不需要 Human 指定特征
- 不需要 Human 描述文档结构
- 只需要 Human 对 future cases 提供 KEEP_SEPARATE / MERGE / UNKNOWN

但 **UNKNOWN** 标签是关键的——当前 GT 只有 KEEP_SEPARATE 和 MERGE，没有 UNKNOWN。P722 显示 Human 在某些案例上选择 UNKNOWN（AMB-032, AMB-375）。Future validation 应允许 UNKNOWN。

### Q6: 是否仍然需要 Human 提供自然语言理由？

**NO — 不需要。**

- 自然语言理由用于事后分析（如本审计），不用于 signal discovery
- Signal discovery 只需要 LABEL（KEEP_SEPARATE / MERGE / UNKNOWN）
- System 从 LABEL + Evidence 反推规则

### Q7: 是否真的需要 LLM？

**NO — 不需要。**

- 所有 signal candidates 基于确定性特征（text pattern, line_obs_count）
- 无案例需要 LLM 语义理解
- 规则发现是统计分析，不是 LLM 推理

### Q8: 是否真的需要新的 DICE Architecture Layer？

**NO — 不需要。**

- 所有特征已存在于 P1/P2 或可派生
- 规则发现是 offline 分析，不需要 runtime 架构
- Consumer/Integration Gap 是 IS-11 的问题，不是架构问题
- 不需要 Evidence Organization Engine、Learning Engine、Signal Engine

---

## 14. Research Route

```
A = Existing Evidence sufficient but poorly organized     → YES (primary)
B = Deterministic derived Evidence sufficient              → YES (line_obs derivable)
C = New Observation genuinely required                    → NO
D = Persistent Human Semantic Judgment remains            → PARTIAL (1 case: AMB-519)
E = Evidence insufficient / Future validation required    → YES (primary)
```

**主因：A + E**

- A：Evidence 已存在但未组织（features in P1/P2, rules not discovered）
- E：Future validation required（0 future cases, L4 not reached）

---

## 15. Anti-Overdesign Gate

```
NEW_MODULE                = NO
NEW_ENGINE                = NO
NEW_OBSERVATION           = NO
NEW_LLM_PIPELINE          = NO
TLD_MODIFICATION          = NO
P7_MODIFICATION           = NO
IS11_MODIFICATION         = NO
RUNTIME_MODIFICATION      = NO
GT_MODIFICATION           = NO
FROZEN_BASELINE_DRIFT     = 0/7
IMPLEMENTATION_AUTHORIZED = FALSE
STOP                      = TRUE
```

> **现有 Evidence 已足以回答本审计的所有问题。不得因为"未来可能需要"而新增架构。**

---

## 16. Limitations

1. **45 GT cases, 4 documents**：Signal candidates 的泛化性无法确认
2. **2 MERGE cases only**：Signal 1 基于 n=2，统计意义极弱
3. **4 disagreement cases**：Signal 3 的 boundary overcommit 基于 4 个案例
4. **0 future cases**：完全无法验证 L5
5. **P722 n=1 participant**：UNKNOWN 决策基于单一参与者
6. **Post-hoc threshold**：line_obs ≥ 3 和 ≥ 6 是事后选择，overfitting 风险
7. **line_obs_count not in P2**：需要派生计算，当前系统不暴露
8. **"FIG." keyword**：学术论文特定，其他文档类型可能不适用
9. **GT 无 UNKNOWN 标签**：所有分歧案例被强制 resolve，可能丢失 ambiguity 信息

---

## 17. Governance Gate

```
DICE_CORE_MODIFICATION              = NO
P1_P7_MODIFICATION                  = NO
P2_MODIFICATION                     = NO
TLD_MODIFICATION                    = NO
IS11_MODIFICATION                   = NO
GT_MODIFICATION                     = NO
EXPERIMENT_MODIFICATION             = NO
NEW_MODULE                          = NO
NEW_ENGINE                          = NO
LLM                                 = NO
RUNTIME_CHANGE                      = NO
CAPABILITY_CHANGE                   = NO
FROZEN_BASELINE                     = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d)
IMPLEMENTATION_AUTHORIZED           = FALSE
FORMAL_LEARNING                     = FALSE
STOP                                = TRUE
```

---

## 18. 最终原则验证

> *不能因为 Human 的反馈可以被描述成一个关键词/类别，就直接认定为 Learning Signal。*

✓ 遵守：Signal 1 被识别为 KEYWORD_RECURRENCE，不是 Learning Signal。

> *如果 Machine 在 Human Feedback 之前，仅利用已存在的 Evidence 就可以确定该 Signal，则 INFO_GAIN = 0。*

✓ 遵守：特征层面 INFO_GAIN = 0（所有特征已存在）。规则层面 INFO_GAIN > 0（需要 Human labels）。

> *区分 Evidence Reorganization / Evidence Distillation / Evidence Interpretation / Genuine Learning Signal。*

✓ 遵守：
- Evidence Reorganization = features exist (E2-A)
- Evidence Distillation = proxy discovery (E2-B, line_obs as proxy)
- Evidence Interpretation = text pattern → label (E5-FIG)
- Genuine Learning Signal = NOT FOUND (L4 not reached)

> *不得因为发现重复模式就直接 L4。*

✓ 遵守：3 个重复模式被发现但均未升级到 L4。

`STOP = TRUE`。
