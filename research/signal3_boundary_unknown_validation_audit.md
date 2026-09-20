# Signal 3 Boundary & UNKNOWN Validation Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY / NO MODIFICATION / NO THRESHOLD TUNING / FROZEN INTACT / STOP

---

## 1. Executive Summary

```
SIGNAL_3_FROZEN_DESCRIPTION     = line_obs_count >= 3 AND NOT has_fig_prefix → KEEP_SEPARATE
SIGNAL_3_DEFINITION_AMBIGUOUS   = FALSE
BOUNDARY_CAPABILITY             = FAIL
L4_CANDIDATE                    = FALSE
FINAL_STATUS                    = L4_NOT_READY_RETAIN_L3

CASE CLASSIFICATION:
  CLEARLY_SUPPORTED             = 38 (84%)
  CLEARLY_UNSUPPORTED           = 2 (4%)
  BOUNDARY                      = 4 (9%)
  CONFLICT                      = 0 (0%)
  UNKNOWN                       = 1 (2%)

BOUNDARY_OVERCOMMIT             = TRUE (4 cases: AMB-005, AMB-375, AMB-418, AMB-032)
  Signal 3 gives DECISIVE KEEP where:
    - 3 cases have reviewer disagreement (A=KEEP, B=MERGE)
    - 2 cases have P722 Human UNKNOWN (31-46s deliberation)

COUNTERFACTUAL_BOUNDARY_GAIN    = >0 (Human reveals ambiguity Machine cannot derive)
BOUNDARY_DISTINGUISHING_FEATURE = TEXT_CONTENT_TYPE (numeric=clear, prose=boundary)
  → E5 (Human Semantic), NOT in Signal 3 feature set
  → Signal 3 CANNOT distinguish clear from boundary

L4 GATE: 10 PASS, 5 PARTIAL, 2 FAIL
  Critical FAIL: #8 (UNKNOWN), #9 (CONFLICT)

STOP                            = TRUE
```

> **Signal 3 的核心问题不是准确率（38/38 clear cases 正确），而是边界能力。Signal 3 的输出空间只有 {KEEP_SEPARATE, UNCOVERED}——没有 UNKNOWN 输出。在 4 个 Human 不确定的案例上（3 个 reviewer 分歧 + 2 个 P722 UNKNOWN），Signal 3 给出确定性 KEEP_SEPARATE。区分 clear 和 boundary 的特征是 TEXT_CONTENT_TYPE（numeric=clear, prose=boundary），属于 E5（Human Semantic），不在 Signal 3 的 feature set 中。Signal 3 不具备进入 L4 Human Validation 的资格。维持 L3。**

---

## 2. Frozen Signal 3 Definition

### SIGNAL_3_FROZEN_DESCRIPTION

```
Definition: line_obs_count >= 3 AND NOT has_fig_prefix → KEEP_SEPARATE

Feature set:
  1. line_obs_count
     Source: NOT in P2 output, DERIVABLE from P1 (count same-y observations)
     Threshold: >= 3
  2. has_fig_prefix (text_a or text_b starts with 'FIG')
     Source: NOT explicitly computed, DERIVABLE from P1 text (trivial string check)
     Condition: NOT has_fig_prefix

Composite rule: IF line_obs_count >= 3 AND NOT has_fig_prefix THEN KEEP_SEPARATE

Coverage: 42/45 cases (93%)
Prediction: KEEP_SEPARATE for all 42 covered cases
Accuracy on covered: 42/42 (100%) — 0 false positive
Uncovered: 3 cases (AMB-414, AMB-422, AMB-519)

Output space: {KEEP_SEPARATE (triggers), UNCOVERED (does not trigger)}
```

> **本审计不修改 Signal 3。定义从上一阶段审计恢复，无歧义。**

---

## 3. Case Classification

### Classification Summary

| Category | Count | % | Description |
|---|---|---|---|
| CLEARLY_SUPPORTED | 38 | 84% | Signal 3 triggers, GT=KEEP, reviewer agreement |
| CLEARLY_UNSUPPORTED | 2 | 4% | Signal 3 correctly does NOT trigger (FIG prefix), GT=MERGE |
| BOUNDARY | 4 | 9% | Reviewer disagreement or P722 UNKNOWN |
| CONFLICT | 0 | 0% | No Signal 3 → KEEP vs GT=MERGE |
| UNKNOWN | 1 | 2% | P722 UNKNOWN, reviewer agreement |

### A. CLEARLY_SUPPORTED (38 cases)

- All 38: line_obs ≥ 3, NOT FIG, GT=KEEP_SEPARATE, reviewer agreement (A=B=KEEP)
- Cross-document: 4 documents (is11_resnet, is11_efficientnet, is11_med_001, is11_cs_001)
- line_obs range: 3-13
- P722 B2 available: 17/38, all correct (100%), avg time 3.4s
- Near-boundary (line_obs=3): 4 cases, all with reviewer agreement

### B. CLEARLY_UNSUPPORTED (2 cases)

| Case | GT | line_obs | FIG | S3 triggers? | Reason |
|---|---|---|---|---|---|
| AMB-414 | MERGE | 5 | YES | NO (correct) | FIG prefix → correctly excluded |
| AMB-422 | MERGE | 2 | YES | NO (correct) | FIG prefix → correctly excluded |

> Signal 3 的 FIG 排除条件正确工作：2 个 MERGE 案例都有 FIG 前缀，Signal 3 正确不触发。

### C. BOUNDARY / AMBIGUOUS (4 cases)

| Case | GT | line_obs | FIG | S3 | Rev A | Rev B | P722 B2 | Overcommit? |
|---|---|---|---|---|---|---|---|---|
| AMB-519 | KEEP | 2 | N | NO (uncovered) | KEEP | MERGE | KEEP (2.0s) | No (uncovered) |
| AMB-005 | KEEP | 3 | N | YES → KEEP | KEEP | MERGE | KEEP (3.4s) | **YES** |
| AMB-375 | KEEP | 3 | N | YES → KEEP | KEEP | MERGE | **UNKNOWN (31.3s)** | **YES (severe)** |
| AMB-418 | KEEP | 7 | N | YES → KEEP | KEEP | MERGE | KEEP (12.2s) | **YES** |

> 3/4 BOUNDARY 案例被 Signal 3 覆盖并给出确定性 KEEP_SEPARATE，但 reviewer 分歧（50/50 split）。AMB-375 同时有 reviewer 分歧和 P722 UNKNOWN——最严重的 overcommit。

### D. CONFLICT (0 cases)

无直接 CONFLICT：Signal 3 从不预测 KEEP_SEPARATE 而 GT=MERGE。

但存在 BOUNDARY-level CONFLICT：Signal 3 → KEEP (decisive)，Human → DISAGREEMENT (uncertain)。

### E. UNKNOWN (1 case)

| Case | GT | line_obs | FIG | S3 | Reviewer | P722 B2 | Root cause |
|---|---|---|---|---|---|---|---|
| AMB-032 | KEEP | 3 | N | YES → KEEP | A=B=KEEP | UNKNOWN (45.9s) | Evidence Missing (TLD missed table) |

> AMB-032: reviewer 一致（KEEP），但 P722 Human 选 UNKNOWN。Signal 3 预测正确（匹配 GT），但 Human 不确定。根因是 Consumer/Integration Gap（TLD 未检测到表格），不是 Signal 3 的边界问题。

---

## 4. Boundary Overcommit Test

### 4.1 Test Question

> Signal 3 是否能够表达："我虽然看到了这个 feature pattern，但 Evidence 不足以让我做出确定判断。"

### 4.2 Test Result

```
BOUNDARY_CAPABILITY = FAIL
```

Signal 3 的输出空间：
- 触发时：**KEEP_SEPARATE**（始终，无置信度级别）
- 不触发时：**UNCOVERED**（无预测，不是 UNKNOWN）

**Signal 3 没有 UNKNOWN 输出。** 当 Signal 3 触发时，它始终给出 KEEP_SEPARATE，没有机制表达"我看到了 pattern 但不确定"。

### 4.3 Overcommit Cases

| Case | Signal 3 | Human Reality | Severity |
|---|---|---|---|
| AMB-005 | KEEP (decisive) | Reviewer disagreement (50/50) | MODERATE |
| AMB-375 | KEEP (decisive) | Reviewer disagreement + P722 UNKNOWN (31.3s) | **SEVERE** |
| AMB-418 | KEEP (decisive) | Reviewer disagreement (50/50) | MODERATE |
| AMB-032 | KEEP (decisive) | P722 UNKNOWN (45.9s) | MODERATE |

### 4.4 Core Problem

> **AMB-024 (CLEAR, line_obs=3, reviewer agreement) 和 AMB-375 (BOUNDARY, line_obs=3, reviewer disagreement) 有完全相同的 Signal 3 特征。Signal 3 对两者给出相同预测——无法区分 clear 和 boundary。**

---

## 5. What Distinguishes Boundary from Clear?

### 5.1 Analysis at Same line_obs=3

| Case | Class | Text A | Text B | Text Type | Reviewer |
|---|---|---|---|---|---|
| AMB-024 | CLEAR | '28.54' | '10.02' | numeric | A=B=KEEP |
| AMB-034 | CLEAR | '21.59' | '5.71' | numeric | A=B=KEEP |
| AMB-074 | CLEAR | '41.5' | '21.2' | numeric | A=B=KEEP |
| AMB-102 | CLEAR | 'our single model' | '60.5' | mixed | A=B=KEEP |
| AMB-005 | **BOUNDARY** | 'unsurprising) and then' | 'Unexpectedly,' | **prose** | A=KEEP, B=MERGE |
| AMB-375 | **BOUNDARY** | '[23].' | 'Each' | **prose** | A=KEEP, B=MERGE |
| AMB-032 | UNKNOWN | '-' | '8.43' | numeric | A=B=KEEP |

### 5.2 Pattern

```
Numeric values → CLEARLY_SUPPORTED (table values, reviewer agreement)
Short labels → CLEARLY_SUPPORTED (table headers, reviewer agreement)
Prose text → BOUNDARY (sentence vs paragraph ambiguity, reviewer disagreement)
```

### 5.3 Key Finding

> **区分 clear 和 boundary 的特征是 TEXT_CONTENT_TYPE（numeric vs prose）。这属于 E5（Human Semantic Interpretation）。Signal 3 的 feature set 只有 line_obs_count + has_fig_prefix——不包含 text type。Signal 3 无法区分 clear 和 boundary。**

### 5.4 Important Note

> 添加 text type 特征会构成 **修改 Signal 3**——本审计禁止。这不是 threshold 调整问题，而是 Signal 3 的结构性限制。

---

## 6. UNKNOWN Root Cause Analysis

### AMB-032 (P722 UNKNOWN, 45.9s)

```
Text: '-' / '8.43' — numeric table values
Reviewers: AGREED (KEEP_SEPARATE)
Root cause: A. Evidence Missing — TLD detected 0 tables
→ Human had numeric values but no table structure evidence → uncertain → UNKNOWN
→ Signal 3 correct (matches GT) but Human uncertain due to Consumer/Integration Gap
→ NOT a Signal 3 boundary issue
```

### AMB-375 (P722 UNKNOWN, 31.3s + reviewer disagreement)

```
Text: '[23].' / 'Each' — citation + prose
Reviewers: DISAGREED (A=KEEP, B=MERGE)
Root cause: C. Semantic Ambiguity — sentence boundary vs paragraph boundary
→ Human couldn't determine if sentence boundary (KEEP) or paragraph flow (MERGE)
→ Signal 3 gives DECISIVE KEEP where Humans are AMBIGUOUS
→ IS a Signal 3 boundary issue
```

### UNKNOWN Classification

| Root Cause | Cases | Signal 3 Issue? |
|---|---|---|
| A. Evidence Missing (TLD gap) | 1 (AMB-032) | NO — Consumer/Integration Gap |
| C. Semantic Ambiguity (prose) | 1 (AMB-375) | YES — Signal 3 overcommits |
| D. Human Disagreement | 3 (AMB-005, 375, 418) | YES — Signal 3 overcommits |

> **Signal 3 的真正缺口不是"更好的 KEEP/MERGE prediction"，而是"正确识别什么时候不能做确定判断"。**

---

## 7. Counterfactual Boundary Test

### Test Design

| State | Machine Has | Machine Lacks |
|---|---|---|
| STATE A (no Human) | P1 text, P2 geometry, line_obs, has_fig | Boundary information |
| STATE B (with Human) | P1 + P2 + **Human labels + disagreement signal** | — |

### Results

| Case | STATE A: Can Machine identify boundary? | STATE B: What Human reveals | Boundary Info Gain | Classification |
|---|---|---|---|---|
| AMB-005 | **NO** (same features as clear cases) | Disagreement (A=KEEP, B=MERGE) | **>0** | POTENTIALLY_REUSABLE_BOUNDARY_SIGNAL |
| AMB-032 | **NO** (same features as clear cases) | P722 UNKNOWN (45.9s) | **>0** | POTENTIALLY_REUSABLE_BOUNDARY_SIGNAL |
| AMB-375 | **NO** (same features as clear cases) | Disagreement + UNKNOWN | **>0** | **PERSISTENT_HUMAN_SEMANTIC_BOUNDARY** |
| AMB-418 | **NO** (same features as clear cases) | Disagreement (A=KEEP, B=MERGE) | **>0** | POTENTIALLY_REUSABLE_BOUNDARY_SIGNAL |

### Key Finding

> **Machine 无法从现有特征识别 boundary——clear 和 boundary 案例有相同的 Signal 3 特征。Human feedback（disagreement / UNKNOWN）揭示了 Machine 无法推导的 boundary information。Boundary Information Gain > 0。但这是 boundary identification 的缺口，不是 KEEP/MERGE prediction 的缺口。**

---

## 8. Reviewer Disagreement Analysis

### 4 Disagreement Cases (all A=KEEP_SEPARATE, B=MERGE, final=KEEP_SEPARATE)

| Case | Signal 3 | line_obs | Text Type | Root Cause |
|---|---|---|---|---|
| AMB-005 | KEEP (overcommit) | 3 | prose | Sentence vs paragraph boundary |
| AMB-375 | KEEP (overcommit) | 3 | prose | Citation + sentence boundary |
| AMB-418 | KEEP (overcommit) | 7 | prose | Sentence vs caption paragraph |
| AMB-519 | UNCOVERED | 2 | prose | Sentence vs paragraph (line_obs < 3) |

> **所有 4 个分歧案例都是 prose text（句子边界 vs 段落边界）。Signal 3 在 3/4 上 overcommit（AMB-519 因 line_obs=2 未覆盖）。Human disagreement exists + Signal 3 produces deterministic KEEP → BOUNDARY_OVERCOMMIT = TRUE。**

---

## 9. L4 Gate Evaluation

### 17 Criteria

| # | Criterion | Result | Reason |
|---|---|---|---|
| 1 | Evidence-grounded | **PASS** | Both features traceable to P1/P2 |
| 2 | Human info gain > 0 | **PASS** | Rule discovery requires Human labels |
| 3 | Non-pure keyword recurrence | PARTIAL | has_fig is keyword, but composite includes line_obs |
| 4 | Non post-hoc threshold | PARTIAL | threshold=3 is post-hoc |
| 5 | Non case-specific | PARTIAL | 42 cases, 4 docs, but all IS-11 academic papers |
| 6 | Has clear supported cases | **PASS** | 38 CLEARLY_SUPPORTED |
| 7 | Has clear unsupported/boundary | **PASS** | 2 unsupported + 4 boundary + 1 UNKNOWN |
| 8 | **Can retain UNKNOWN** | **FAIL** | No UNKNOWN output — always KEEP_SEPARATE when triggers |
| 9 | **Can expose CONFLICT** | **FAIL** | No CONFLICT output — ignores reviewer disagreement |
| 10 | Doesn't force all-case coverage | **PASS** | 3 uncovered (7%) |
| 11 | No semantic authority | PARTIAL | has_fig_prefix is semantic (text pattern) |
| 12 | No Runtime Authority | **PASS** | Offline analysis |
| 13 | No LLM dependency | **PASS** | All features deterministic |
| 14 | No new Observation | **PASS** | All derivable from P1/P2 |
| 15 | No new Architecture Layer | **PASS** | No new module |
| 16 | No Frozen modification | **PASS** | P1-P7, TLD, GT intact |
| 17 | Minimal Human Validation | PARTIAL | Can use [suitable/unsuitable/uncertain] but Signal 3 can't express 'uncertain' |

### Summary

```
PASS: 10 | PARTIAL: 5 | FAIL: 2
```

### Critical Failures

**#8 (Can retain UNKNOWN): FAIL**
- Signal 3 output = {KEEP_SEPARATE, UNCOVERED}
- 没有 UNKNOWN 输出
- 4 个 boundary 案例得到确定性 KEEP_SEPARATE

**#9 (Can expose CONFLICT): FAIL**
- Signal 3 没有 CONFLICT 输出
- reviewer 分歧时仍给出 KEEP_SEPARATE

### L4 Decision

```
L4_CANDIDATE = FALSE
```

> **Signal 3 fails #8 (UNKNOWN) and #9 (CONFLICT) — the two most critical boundary criteria. Signal 3 cannot express uncertainty or expose conflict. This is the CORE failure for L4 readiness.**

---

## 10. Final Output Matrix

| Dimension | Result |
|---|---|
| Evidence Grounding | PASS (E1 text + E3 line_obs) |
| Information Gain | >0 (rule level, not feature level) |
| Novelty | PARTIAL (composite rule, but components simple) |
| Supported Cases | 38 CLEARLY_SUPPORTED (84%) |
| Unsupported Cases | 2 CLEARLY_UNSUPPORTED (4%) |
| Boundary Cases | 4 BOUNDARY (9%) |
| Conflict Cases | 0 direct CONFLICT, but boundary-level conflict on 3 |
| UNKNOWN Cases | 1 P722 UNKNOWN (2%), + 1 dual (AMB-375) |
| Boundary Overcommit | **TRUE** (4 cases) |
| Cross-document support | YES (4 documents) |
| Reviewer consistency | FAIL (3/4 disagreement cases overcommitted) |
| Reusability potential | MODERATE (if boundary issue resolved) |
| **L4 Candidate** | **FALSE** |

---

## 11. Human Validation Requirement

### If Signal 3 Were L4-Ready

最小反馈形式：
```
[合适] (Signal 3 prediction matches Human judgment)
[不合适] (Signal 3 prediction contradicts Human judgment)
[不确定] (Human cannot determine — boundary case)
```

### Current Status

Signal 3 **无法** 使用这种最小反馈完成验证，因为：
- Signal 3 自身无法表达 [不确定]
- 当 Human 说 [不确定] 时，Signal 3 已经给出了 [KEEP_SEPARATE]
- 验证会暴露 Signal 3 的 overcommit，但无法修复它（不允许修改 Signal 3）

> **Signal 3 无法用最小反馈完成验证 → L4_CANDIDATE = FALSE**

---

## 12. Future Validation Requirement

```
FUTURE_VALIDATION_REQUIRED = TRUE (if L4 reached)
最小独立性: Level B (different document)
优先要求: different page + no near-duplicate
禁止: same-page, near-duplicate, same-table duplicate, GT leakage
最小数量: 10 future cases
```

> 当前不构造 Future Cases。Future validation 仅在 L4 达到后才需要。

---

## 13. Final Research Questions

### Q1. Signal 3 是否存在真实的 Evidence-grounded novelty？

**PARTIAL.** Feature 层面无 novelty（所有特征已存在或可派生）。Rule 层面有 novelty（composite rule 需要 Human labels 发现）。但 composite rule 的组件（threshold + keyword）简单，novelty 程度有限。

### Q2. Signal 3 是否只是 supervised pattern fitting？

**YES, primarily.** Signal 3 是通过 Human labels 发现的 feature → label 关联。没有独立的 evidence-grounded 推理机制。一旦规则发现，就是确定性 pattern matching。

### Q3. Signal 3 是否存在明确 Boundary？

**NO.** Signal 3 没有内置 boundary 机制。38 个 clear 案例和 4 个 boundary 案例有相同的 Signal 3 特征——Signal 3 无法区分。

### Q4. Signal 3 是否能够合理产生 UNKNOWN？

**NO.** Signal 3 输出空间 = {KEEP_SEPARATE, UNCOVERED}。没有 UNKNOWN 输出。这是 L4 Gate 的 critical failure (#8)。

### Q5. Signal 3 是否存在 Boundary Overcommit？

**YES.** 4 个案例（AMB-005, AMB-375, AMB-418, AMB-032）中 Signal 3 给出确定性 KEEP_SEPARATE，而 Human 不确定（3 个 reviewer 分歧 + 2 个 P722 UNKNOWN）。

### Q6. Signal 3 是否值得进行 Human Validation？

**NO — 当前不值得。** Signal 3 缺乏 boundary capability（#8 FAIL, #9 FAIL）。在没有 UNKNOWN/CONFLICT 输出的情况下进行 Human Validation 会暴露 overcommit 但无法解决它。

### Q7. 如果值得，Human Validation 的最小反馈是什么？

**N/A（当前不值得）。** 如果未来 Signal 3 获得 boundary capability，最小反馈为 [合适 / 不合适 / 不确定]。

### Q8. 如果值得，需要多少最小独立 Future Cases？

**N/A（当前不值得）。** 如果未来进入 L4，需要 Level B（不同文档），至少 10 个 future cases。

### Q9. 如果不值得，Signal 3 应该 CLOSE 还是 RETAIN_AS_L3_CANDIDATE？

**RETAIN_AS_L3_CANDIDATE.**

理由：
- 38/38 clear cases 正确（84% 覆盖率，0 false positive）
- 跨 4 个文档
- Feature 可派生，不需新 observation
- 但 boundary capability 不足，不能进入 L4
- 未来如果发现 boundary distinguishing feature（如 text type），可重新评估

> **Signal 3 有明确的 supported 核心能力（clear cases），但缺乏 boundary capability。关闭太早——保留为 L3 candidate，等待 boundary evidence。**

### Q10. 下一步是否需要 LLM / 新 Observation / 新 Architecture / Signal Engine / Learning Engine？

```
LLM                     = NO
新 Observation          = NO
新 Architecture Layer   = NO
Signal Engine           = NO
Learning Engine         = NO
```

> **全部 NO。Signal 3 的 boundary 缺口是 feature set 限制，不是架构问题。现有 Evidence 足以分析 boundary——只是 Signal 3 当前不包含区分 boundary 的特征。**

---

## 14. Final Status

```
FINAL_STATUS = L4_NOT_READY_RETAIN_L3
```

Signal 3 仍然是 L3 candidate，需要额外 boundary evidence 后才能进入 L4。

不关闭（RETAIN），因为：
1. 38/38 clear cases 正确
2. 跨 4 个文档
3. 无需新 observation / architecture / LLM
4. Boundary distinguishing feature (text type) 已被识别但不在 Signal 3 中

---

## 15. Anti-Overdesign Gate

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
NEW_LLM_PIPELINE                    = NO
NEW_OBSERVATION                     = NO
RUNTIME_CHANGE                      = NO
CAPABILITY_CHANGE                   = NO
FROZEN_BASELINE_DRIFT               = 0/7
IMPLEMENTATION_AUTHORIZED           = FALSE
FORMAL_LEARNING                     = FALSE
STOP                                = TRUE
```

---

## 16. Governance Gate

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

## 17. 最终原则验证

> *本任务不是优化 Signal 3。不是寻找最佳 threshold。*

✓ 遵守：未修改 Signal 3，未调参，未 grid search。

> *本阶段只研究 BOUNDARY。*

✓ 遵守：核心分析是 boundary capability 和 overcommit。

> *不得把 disagreement 压缩成确定性 KEEP。*

✓ 遵守：4 个 disagreement 案例被保留为 BOUNDARY，未被强制归入 KEEP。

> *Signal 3 是否有能力表达 SUPPORTED 和 UNKNOWN 之间的边界。*

✓ 回答：**FAIL** — Signal 3 没有 UNKNOWN 输出。

> *L3 ≠ L4 ≠ L5/L6*

✓ 遵守：L3 candidate maintained，L4 not reached，L5/L6 not discussed as achieved。

`STOP = TRUE`。
