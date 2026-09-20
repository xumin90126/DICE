# Signal 3 Boundary Evidence Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY / NO MODIFICATION / NO THRESHOLD TUNING / FROZEN INTACT / STOP

---

## 1. Executive Summary

```
ROOT_CAUSE_PRIMARY    = B. DETERMINISTIC_DERIVATION_GAP
ROOT_CAUSE_SECONDARY  = D. HUMAN_SEMANTIC_GAP

KEY_DISCOVERY:
  period_end=True AND cap_start=True:
    BOUNDARY cases: 4/4 (100%)
    CLEAR cases:    0/38 (0%)
    UNSUPPORTED:    0/2 (0%)
    UNKNOWN:        0/1 (0%)
  → PERFECT discrimination on current 45 cases

  BUT:
  1. This feature is NOT in Signal 3 → adding = MODIFYING (forbidden)
  2. n=4 BOUNDARY cases — too few for generalization
  3. Even with BOUNDARY identified, KEEP/MERGE is SEMANTIC:
     All 4 BOUNDARY cases have reviewer disagreement (A=KEEP, B=MERGE)
     Period+capital identifies BOUNDARY but doesn't resolve KEEP vs MERGE

BOUNDARY_EXPRESSIBLE         = PARTIALLY (derivable feature exists, but not in Signal 3)
UNKNOWN_EXPRESSIBLE          = NO (Signal 3 has no UNKNOWN output)
BOUNDARY_NOT_EXPRESSIBLE     = FALSE (a derivable feature exists: period+capital)

SIGNAL_3_FINAL_STATUS        = RETAIN_AS_L3_CANDIDATE
L4_CANDIDATE_READY           = FALSE

STOP                         = TRUE
```

> **Signal 3 无法区分 CLEAR 与 BOUNDARY 的主要原因（PRIMARY）是 DETERMINISTIC_DERIVATION_GAP：存在一个可从 P1 文本确定性派生的特征组合（period_end + cap_start），在当前 45 个案例上完美区分 BOUNDARY（4/4）与 CLEAR（0/38），但该特征不在 Signal 3 的 feature set 中，且当前系统未计算。次要原因（SECONDARY）是 HUMAN_SEMANTIC_GAP：即使 BOUNDARY 被识别，所有 4 个 BOUNDARY 案例的 KEEP/MERGE 决策仍需要语义解释——reviewer 分歧 50/50，无法通过确定性规则解决。Signal 3 维持 L3 Candidate。**

---

## 2. Boundary Case Matrix

| Case | Audit Class | GT | line_obs | FIG | S3 Triggers | Text A | Text B | period_end | cap_start | period+cap | Reviewer A | Reviewer B | P722 B2 | Boundary Reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AMB-024 | CLEAR | KEEP | 3 | N | Y | '28.54' | '10.02' | N | N | **N** | KEEP | KEEP | N/A | Numeric table values |
| AMB-034 | CLEAR | KEEP | 3 | N | Y | '21.59' | '5.71' | N | N | **N** | KEEP | KEEP | N/A | Numeric table values |
| AMB-074 | CLEAR | KEEP | 3 | N | Y | '41.5' | '21.2' | N | N | **N** | KEEP | KEEP | KEEP(3s) | Numeric table values |
| AMB-102 | CLEAR | KEEP | 3 | N | Y | 'our single model...' | '60.5' | N | N | **N** | KEEP | KEEP | N/A | Mixed table label+value |
| AMB-032 | UNKNOWN | KEEP | 3 | N | Y | '-' | '8.43' | N | N | **N** | KEEP | KEEP | **UNKNOWN(46s)** | Evidence Missing (TLD gap) |
| AMB-005 | BOUNDARY | KEEP | 3 | N | Y | '...rapidly.' | 'Unexpectedly,' | Y | Y | **Y** | KEEP | **MERGE** | KEEP(3s) | Sentence vs paragraph |
| AMB-375 | BOUNDARY | KEEP | 3 | N | Y | '[23].' | 'Each' | Y | Y | **Y** | KEEP | **MERGE** | **UNKNOWN(31s)** | Citation + sentence boundary |
| AMB-418 | BOUNDARY | KEEP | 7 | N | Y | '...left panel.' | 'The' | Y | Y | **Y** | KEEP | **MERGE** | KEEP(12s) | Sentence vs caption paragraph |
| AMB-519 | BOUNDARY | KEEP | 2 | N | N | '...LLMs.' | 'To embrace...' | Y | Y | **Y** | KEEP | **MERGE** | KEEP(2s) | Sentence vs paragraph (uncovered) |
| AMB-414 | UNSUPPORTED | MERGE | 5 | Y | N | 'FIG. 9:' | 'Left:' | N | N | N | MERGE | MERGE | MERGE(10s) | Figure caption |
| AMB-422 | UNSUPPORTED | MERGE | 2 | Y | N | 'FIG. 12:' | 'Distribution...' | N | N | N | MERGE | MERGE | MERGE(1s) | Figure caption |

---

## 3. AMB-024 vs AMB-375 Comparison

### 3.1 Feature-by-Feature Comparison

| Feature | AMB-024 (CLEAR) | AMB-375 (BOUNDARY) | Difference? |
|---|---|---|---|
| **text_a** | '28.54' | '[23].' | Content differs |
| **text_b** | '10.02' | 'Each' | Content differs |
| **text_a length** | 5 | 5 | SAME |
| **text_b length** | 5 | 4 | ~SAME |
| **text type A** | numeric | short (citation) | DIFFERENT |
| **text type B** | numeric | short (word) | DIFFERENT |
| **period_end** | **N** | **Y** | **DIFFERENT** |
| **cap_start** | **N** | **Y** | **DIFFERENT** |
| **bbox_a** | [170.2, 125.4, 190.4, 134.4] | [470.7, 121.5, 492.2, 133.5] | Position differs |
| **bbox_b** | [215.3, 125.4, 235.5, 134.4] | [501.9, 121.5, 527.1, 133.5] | Position differs |
| **dy** | 0.0 | 0.0 | SAME |
| **h_gap** | 25.0 | 9.7 | DIFFERENT |
| **w_a** | 20.2 | 21.5 | ~SAME |
| **w_b** | 20.2 | 25.2 | ~SAME |
| **same_style** | True | True | SAME |
| **line_obs** | 3 | 3 | SAME |
| **has_fig_prefix** | False | False | SAME |
| **style_sig_a** | NimbusRomNo9L-Regu\|9.0 | SFRM1200\|12.0 | DIFFERENT (font/size) |
| **style_sig_b** | NimbusRomNo9L-Regu\|9.0 | SFRM1200\|12.0 | DIFFERENT (font/size) |
| **TLD is_in_table** | True | False | **DIFFERENT** |
| **TLD different_cell** | True | False | **DIFFERENT** |
| **doc_id** | is11_resnet | is11_med_001 | DIFFERENT |
| **page** | 6 | 6 | SAME |
| **Signal 3 features** | line_obs=3, no FIG | line_obs=3, no FIG | **IDENTICAL** |

### 3.2 Key Differences

**Three features differ between CLEAR and BOUNDARY:**

1. **period_end + cap_start**: AMB-024 (N/N) vs AMB-375 (Y/Y) — **PERFECT discriminator**
2. **TLD is_in_table**: AMB-024 (True) vs AMB-375 (False) — TLD correctly identifies table vs non-table
3. **h_gap**: AMB-024 (25.0) vs AMB-375 (9.7) — larger gap for table columns

**BUT**: All three are NOT in Signal 3's feature set. Signal 3 only uses line_obs_count + has_fig_prefix, which are IDENTICAL for both cases.

### 3.3 Why Human Can Distinguish

> **AMB-024**: Human sees numeric values ('28.54'/'10.02') + TLD says "in table" → clear table cells → KEEP_SEPARATE. No ambiguity.

> **AMB-375**: Human sees '[23].' (citation ending sentence) + 'Each' (start of new sentence) → sentence boundary. But Reviewer B considers it "same paragraph" → MERGE. The disagreement is about whether "same paragraph" overrides "different sentences". This is a **semantic interpretation** that Humans resolve differently.

---

## 4. Evidence Dependency Analysis

### 4.1 Feature Classification

| Feature | Exists in P1-P7? | Derivable? | Evidence Category | In Signal 3? |
|---|---|---|---|---|
| text_a, text_b | YES (P1) | YES | E1 | NO (only has_fig_prefix check) |
| bbox, h_gap, dy | YES (P2) | YES | E1 | NO |
| line_obs_count | NO (not in P2) | YES (count same-y P1 obs) | E3 | YES (threshold ≥ 3) |
| has_fig_prefix | NO (not computed) | YES (trivial string check) | E3 | YES (NOT condition) |
| **period_end** | YES (text in P1) | **YES** (trivial: text.endswith('.')) | **E3** | **NO** |
| **cap_start** | YES (text in P1) | **YES** (trivial: text[0].isupper()) | **E3** | **NO** |
| TLD is_in_table | YES (TLD output) | YES | E1 | NO |
| text_content_type | YES (text in P1) | YES (length + digit check) | E3 | NO |

### 4.2 Key Finding

> **period_end 和 cap_start 都是 E3（Derived Evidence）——可从 P1 文本通过确定性字符串操作派生，不需要 Human 反馈，不需要新 Observation。但它们不在 Signal 3 的 feature set 中，且当前系统未计算。**

---

## 5. TEXT_CONTENT_TYPE Audit

### 5.1 Derivability

```
TEXT_CONTENT_TYPE:
  numeric:   text.replace('.','').replace(',','').replace('-','').isdigit()  → trivial
  prose:     len(text) > 15                                                  → trivial
  short:     len(text) <= 15 and not numeric                                 → trivial

DERIVABLE_FROM_EXISTING_EVIDENCE = TRUE
Evidence Category = E3 (Derived)
```

### 5.2 Does TEXT_CONTENT_TYPE Resolve Boundary?

**NO — partially only.**

| Text Type | CLEAR cases | BOUNDARY cases |
|---|---|---|
| numeric/numeric | 21 | 0 |
| mixed (numeric+other) | 9 | 0 |
| short/short | 7 | 1 (AMB-375) |
| prose involved | 1 (AMB-102) | 3 (AMB-005, 418, 519) |

> **AMB-375 是 short/short 但 BOUNDARY——TEXT_CONTENT_TYPE 无法区分 AMB-375 与 CLEAR short/short 案例（如 AMB-313 'Test Size'/'#Classes'）。TEXT_CONTENT_TYPE 不是完美的 discriminator。**

### 5.3 period_end + cap_start is Better

```
period_end=True AND cap_start=True:
  BOUNDARY: 4/4 (100%)
  CLEAR:    0/38 (0%)
  → PERFECT discrimination
```

> **period_end + cap_start 比 TEXT_CONTENT_TYPE 更准确——它完美区分了所有 4 个 BOUNDARY 案例与所有 38 个 CLEAR 案例，包括 AMB-375（short/short 但 period+capital=True）。**

---

## 6. Semantic Leakage Test

### 6.1 Feature Derivation (No Semantic Leakage)

```
period_end = text_a.rstrip().endswith('.')  → PURE STRING CHECK
cap_start  = text_b[0].isupper()            → PURE STRING CHECK

SEMANTIC_LEAKAGE_IN_DERIVATION = 0
```

### 6.2 Interpretation (Semantic Leakage Present)

```
Interpreting period+capital as "sentence boundary":
  "period + capital means different sentences"     → INTERPRETATION
  "different sentences means KEEP_SEPARATE"         → INTERPRETATION
  "same paragraph means MERGE"                      → INTERPRETATION (Reviewer B)

SEMANTIC_INTERPRETATION_REQUIRED = TRUE (for KEEP/MERGE decision)
```

### 6.3 Classification

| Aspect | Category | Semantic Leakage |
|---|---|---|
| Feature derivation (period, capital) | E3 (Derived) | 0 |
| Feature → BOUNDARY identification | E3 (Derived) | 0 |
| BOUNDARY → KEEP/MERGE decision | E5 (Human Semantic) | Non-zero |

> **特征派生无语义泄漏。但将 period+capital 解释为 KEEP/MERGE 决策依据需要语义解释——reviewer 分歧 50/50 证明这是 PERSISTENT_HUMAN_SEMANTIC_BOUNDARY。**

---

## 7. UNKNOWN Analysis

### 7.1 AMB-032 (P722 UNKNOWN, 45.9s)

```
Text: '-' / '8.43' — numeric table values
TLD: is_in_table=True, different_cell=True (TLD CORRECT)
Reviewers: AGREED (A=B=KEEP_SEPARATE)
period_end: N, cap_start: N → period+cap = N → NOT BOUNDARY
```

**Root cause**: A. Evidence Missing (Consumer/Integration Gap)
- TLD correctly detected table, but P722 participant couldn't verify from presented evidence
- Participant expanded ALL geometry fields, spent 45.9s, still said UNKNOWN
- This is participant-level uncertainty, NOT evidence-level boundary
- Signal 3 correctly predicts KEEP_SEPARATE (matches GT)

### 7.2 Can UNKNOWN Be Expressed from Existing Evidence?

```
UNKNOWN_BOUNDARY_NOT_EXPRESSIBLE = FALSE (partially)
```

- For BOUNDARY cases (period+cap=True): UNKNOWN could be expressed if BOUNDARY is identified → but Signal 3 doesn't have this feature
- For AMB-032 (UNKNOWN): no structural feature distinguishes it from CLEAR → UNKNOWN is NOT expressible from existing evidence
- **Signal 3's output space = {KEEP_SEPARATE, UNCOVERED}** — no UNKNOWN output

### 7.3 Summary

| UNKNOWN Case | Root Cause | Signal 3 Issue? | Expressible? |
|---|---|---|---|
| AMB-032 | A. Evidence Missing (TLD gap, participant uncertainty) | NO | NO (same features as CLEAR) |
| AMB-375 | C. Semantic Ambiguity (sentence vs paragraph) | YES (overcommit) | PARTIALLY (if period+cap added) |

---

## 8. Counterfactual Test

### 8.1 For BOUNDARY Cases (period+cap=True)

| Case | STATE A (no Human) | STATE B (with Human) | Boundary Info Gain | Classification |
|---|---|---|---|---|
| AMB-005 | Machine has text with period+capital, but can't interpret | Human reveals: disagreement (KEEP vs MERGE) | >0 | PERSISTENT_HUMAN_SEMANTIC_BOUNDARY |
| AMB-375 | Machine has text with period+capital, but can't interpret | Human reveals: disagreement + UNKNOWN | >0 | PERSISTENT_HUMAN_SEMANTIC_BOUNDARY |
| AMB-418 | Machine has text with period+capital, but can't interpret | Human reveals: disagreement (KEEP vs MERGE) | >0 | PERSISTENT_HUMAN_SEMANTIC_BOUNDARY |
| AMB-519 | Machine has text with period+capital, but can't interpret | Human reveals: disagreement (KEEP vs MERGE) | >0 | PERSISTENT_HUMAN_SEMANTIC_BOUNDARY |

### 8.2 For UNKNOWN Case (AMB-032)

| Case | STATE A (no Human) | STATE B (with Human) | Info Gain | Classification |
|---|---|---|---|---|
| AMB-032 | Machine has TLD=True (table detected), but participant can't verify | Human reviewers: AGREED (KEEP) | 0 (reviewers agree, participant issue) | EVIDENCE_ORGANIZATION_GAIN |

### 8.3 Key Finding

> **对于 BOUNDARY 案例：STATE A 中 Machine 可以计算 period+capital（E3, derivable），但无法解释其含义（KEEP vs MERGE）。STATE B 中 Human 揭示了分歧——这是 Machine 无法从现有 Evidence 确定的 boundary information。Boundary Information Gain > 0。分类为 PERSISTENT_HUMAN_SEMANTIC_BOUNDARY。**

---

## 9. Boundary Expressibility

### 9.1 Is There a Stable E_CLEAR vs E_BOUNDARY Difference?

**YES — period_end + cap_start:**

```
E_CLEAR:    period_end=False OR cap_start=False
E_BOUNDARY: period_end=True AND cap_start=True

These are STABLE and OBSERVABLE in existing Evidence (P1 text).
The difference is STRUCTURAL (string properties), not SEMANTIC.
```

### 9.2 But: Boundary Identification ≠ Boundary Resolution

```
BOUNDARY_IDENTIFICATION (derivable):
  period+cap=True → BOUNDARY
  → E3 (Derived), no semantic leakage
  → Machine CAN identify BOUNDARY without Human

BOUNDARY_RESOLUTION (not derivable):
  BOUNDARY → KEEP or MERGE?
  → E5 (Human Semantic)
  → Human reviewers DISAGREE (50/50)
  → Machine CANNOT resolve without Human
```

### 9.3 Classification

```
BOUNDARY_NOT_EXPRESSIBLE = FALSE
  → A derivable feature (period+cap) exists that identifies BOUNDARY

BOUNDARY_RESOLUTION_EXPRESSIBLE = FALSE
  → Even with BOUNDARY identified, KEEP/MERGE requires Human semantic judgment
```

---

## 10. Four-Way Root Cause Classification

### 10.1 Analysis

| Cause | Applicable? | Evidence |
|---|---|---|
| **A. EVIDENCE_ORGANIZATION_GAP** | PARTIAL | Text exists in P1, but period+capital not organized as decision input. TLD false positive on AMB-005 (prose detected as table). |
| **B. DETERMINISTIC_DERIVATION_GAP** | **YES (PRIMARY)** | period_end and cap_start ARE derivable from P1 (trivial string checks). They are NOT currently computed. They PERFECTLY discriminate BOUNDARY (4/4) from CLEAR (0/38) on current data. Signal 3 lacks these features. |
| **C. OBSERVATION_GAP** | NO | All evidence is in P1 text. No new observation required. |
| **D. HUMAN_SEMANTIC_GAP** | **YES (SECONDARY)** | Even with BOUNDARY identified (via period+cap), KEEP/MERGE decision requires semantic interpretation. All 4 BOUNDARY cases have reviewer disagreement (50/50). Period+capital identifies BOUNDARY but doesn't resolve KEEP vs MERGE. |

### 10.2 Decision

```
PRIMARY   = B. DETERMINISTIC_DERIVATION_GAP
SECONDARY = D. HUMAN_SEMANTIC_GAP
```

### 10.3 Explanation

1. **Proximate cause (B)**: Signal 3 lacks period+capital features → cannot identify BOUNDARY. These features are derivable from P1 text (E3) but not computed.

2. **Ultimate cause (D)**: Even if BOUNDARY identified, KEEP/MERGE for prose/sentence-boundary cases requires semantic interpretation. Human reviewers disagree 50/50 → not solvable by deterministic rules.

3. **B is solvable** (features derivable), **D is not** (Human disagreement).

4. **Solving B alone** would allow BOUNDARY identification (mark as UNKNOWN/uncertain) but not KEEP/MERGE resolution.

5. **Solving D** requires Human validation (L4), but Signal 3 not ready for L4 (B not solved, and even if solved, D remains).

---

## 11. Signal 3 Final Status

### 11.1 Decision

```
SIGNAL_3_FINAL_STATUS = RETAIN_AS_L3_CANDIDATE
```

### 11.2 Reasoning

| Factor | Result | Impact |
|---|---|---|
| Core ability (CLEAR cases) | 38/38 correct | RETAIN (not CLOSE) |
| Boundary capability | FAIL (no UNKNOWN output) | NOT L4 |
| Derivable boundary feature exists | YES (period+cap) | RETAIN (future potential) |
| Boundary resolution requires semantic | YES (reviewer disagreement) | NOT L4 |
| Feature not in Signal 3 | YES (would need modification) | NOT L4 (forbidden to modify) |
| No new observation needed | YES | RETAIN (evidence sufficient) |
| No LLM needed | YES | RETAIN (no architecture needed) |

> **Signal 3 的核心能力（CLEAR cases, 38/38）是真实的。Boundary 缺口有一个可识别的原因（B: period+capital 可派生但未包含）。但即使 boundary 可识别，resolution 仍需语义判断（D）。保留为 L3 Candidate——核心能力不应关闭，boundary gap 有明确的未来研究方向。**

---

## 12. L4 Readiness

```
L4_CANDIDATE_READY = FALSE
```

### 12.1 Reasons

1. **Signal 3 lacks boundary identification feature** (period+cap not included) — cannot modify (forbidden)
2. **Even if boundary identified, KEEP/MERGE is semantic** (reviewer disagreement 50/50)
3. **Signal 3 has no UNKNOWN output** — cannot express uncertainty
4. **Signal 3 has no CONFLICT output** — cannot expose disagreement
5. **n=4 BOUNDARY cases** — too few for generalization
6. **No future cases** — cannot validate

### 12.2 What Would Be Needed for L4

1. A mechanism to identify BOUNDARY cases (period+cap or equivalent)
2. A mechanism to output UNKNOWN for BOUNDARY cases
3. Human validation on BOUNDARY cases (minimal feedback: suitable/unsuitable/uncertain)
4. Future independent cases (Level B, ≥10 cases)

> **当前 Signal 3 不具备这些条件。L4 NOT READY。**

---

## 13. Final Output Matrix

| Dimension | Result |
|---|---|
| Evidence Grounding | PASS (E1 text + E3 derivable features) |
| Information Gain | >0 (rule level, not feature level) |
| Novelty | PARTIAL (composite rule, components simple) |
| Supported Cases | 38 CLEARLY_SUPPORTED (84%) |
| Unsupported Cases | 2 CLEARLY_UNSUPPORTED (4%) |
| Boundary Cases | 4 BOUNDARY (9%) |
| Conflict Cases | 0 direct, 4 boundary-level (reviewer disagreement) |
| UNKNOWN Cases | 1 (2%) + 1 dual (AMB-375) |
| Boundary Overcommit | TRUE (4 cases) |
| Cross-document support | YES (4 documents) |
| Reviewer consistency | FAIL (4/4 boundary cases have disagreement) |
| Reusability potential | MODERATE (if boundary identification added) |
| L4 Candidate | FALSE |
| Boundary Expressible | PARTIALLY (period+cap derivable, but not in Signal 3) |
| UNKNOWN Expressible | NO (Signal 3 has no UNKNOWN output) |

---

## 14. Final Research Questions

### Q1. CLEAR vs BOUNDARY 的核心差异是什么？

**period_end + cap_start。** CLEAR 案例的 text_a 不以句号结尾（或 text_b 不以大写开头）；BOUNDARY 案例的 text_a 以句号结尾且 text_b 以大写开头。这表示句子边界（sentence boundary），触发 KEEP/MERGE 的语义分歧。

### Q2. 这个差异是否已经存在于现有 Evidence？

**YES。** period_end 和 cap_start 都可从 P1 文本确定性派生（trivial string checks）。Evidence 存在于 P1 text output。

### Q3. 如果存在，是 Organization 问题还是 Derivation 问题？

**Derivation 问题（B）。** 特征可派生但当前未计算。这不是 Organization 问题（evidence 已在 P1 中显式存在），而是 Derivation 问题（需要计算 period_end 和 cap_start）。

### Q4. 如果不存在，是否需要 New Observation？

**NO。** 所有 evidence 都在 P1 文本中。不需要新 Observation。

### Q5. Human 是否真的提供了新的 Semantic Information？

**YES — 对于 BOUNDARY resolution。** Human 提供了 KEEP/MERGE 的语义判断。即使 Machine 能识别 BOUNDARY（通过 period+cap），KEEP/MERGE 决策仍需要 Human 语义解释。Reviewer 分歧 50/50 证明这不是确定性可解的。

### Q6. UNKNOWN 是否可以从现有 Evidence 中表达？

**PARTIALLY。** 对于 BOUNDARY 案例（period+cap=True），可以表达为 UNKNOWN（如果添加该特征）。但对于 AMB-032（UNKNOWN due to Evidence Missing），无法从现有 evidence 区分——它与 CLEAR 案例有相同特征。

### Q7. Signal 3 是否存在可验证 Boundary？

**YES — 但不在 Signal 3 中。** period+cap 是一个可验证的 boundary marker（4/4 BOUNDARY, 0/38 CLEAR）。但它不在 Signal 3 的 feature set 中。添加它需要修改 Signal 3（forbidden）。

### Q8. Signal 3 是否仍然值得保留？

**YES — RETAIN_AS_L3_CANDIDATE。** 核心能力（38/38 CLEAR）是真实的。Boundary gap 有明确原因（B: derivable feature missing）和明确限制（D: semantic resolution needed）。不应关闭。

### Q9. 是否具备进入 L4 Human Validation 的条件？

**NO。** Signal 3 缺乏 boundary identification feature（period+cap），没有 UNKNOWN 输出，无法表达 uncertainty。即使添加 boundary feature，KEEP/MERGE resolution 仍需语义判断。

### Q10. 下一步是否需要 LLM / 新 Observation / 新 Architecture / Signal Engine / Learning Engine？

| Component | Needed? | Reason |
|---|---|---|
| LLM | **NO** | All features deterministic (string checks) |
| 新 Observation | **NO** | All evidence in P1 text |
| 新 Architecture Layer | **NO** | No new module needed |
| Signal Engine | **NO** | Offline analysis sufficient |
| Learning Engine | **NO** | L3 candidate, not L4+ |

> **全部 NO。现有 Evidence 足以分析 boundary——只需计算 period_end 和 cap_start（trivial derivation）。但计算它们不等于修改 Signal 3（forbidden）。**

---

## 15. Future Research Route

### PRIMARY = B. DETERMINISTIC_DERIVATION_GAP

**下一步允许**：offline derivation audit
- 计算 period_end 和 cap_start 对所有 45 案例的 discrimination power（已完成：4/4 BOUNDARY, 0/38 CLEAR）
- 验证在更多数据上是否稳定（需要 future cases）
- 不得立即实现
- 不得修改 Signal 3

### SECONDARY = D. HUMAN_SEMANTIC_GAP

**下一步允许**：考虑 L4 Human Validation Candidate
- 但仅在 B 解决后（即 boundary identification feature 确认后）
- Human Validation 最小反馈：[合适 / 不合适 / 不确定]
- 需要 future independent cases (Level B, ≥10)
- 仍然不是 Learning，不是 Future Reuse

---

## 16. Anti-Overdesign Gate

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
NEW_SIGNAL                          = NO
NEW_OBSERVATION                     = NO
NEW_LLM_PIPELINE                    = NO
RUNTIME_CHANGE                      = NO
CAPABILITY_CHANGE                   = NO
FROZEN_BASELINE_DRIFT               = 0/7
IMPLEMENTATION_AUTHORIZED           = FALSE
FORMAL_LEARNING                     = FALSE
STOP                                = TRUE
```

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

> *不得把"相关"当成"决定性"。*

✓ 遵守：period+cap 在当前 45 案例上完美区分，但 n=4 BOUNDARY 案例太少，明确标注"too few for generalization"。

> *不要把 Human Semantic Gap 轻易判成 E5。*

✓ 遵守：先检查了所有 E1-E4 可能性。确认特征可派生（E3）后才将 interpretation 归为 E5。检查了 period+cap 的 6 项条件（充分展示、清晰追溯、无 Observation 缺口、无 Organization 缺口、无简单 derivation、无可验证 structural distinction）——前 5 项满足，第 6 项不满足（period+cap 是 structural distinction 但不在 Signal 3 中）。因此 D 是 SECONDARY 而非 PRIMARY。

> *不得输出规则化结果。*

✓ 遵守：未输出 IF prose THEN UNKNOWN 或 IF period THEN BOUNDARY 等规则。period+cap 仅作为"被审计的假设"和"boundary marker candidate"，不作为推荐规则。

> *A/B/C/D 不得全部写成 TRUE。*

✓ 遵守：PRIMARY = B, SECONDARY = D, C = NO, A = PARTIAL。

`STOP = TRUE`。
