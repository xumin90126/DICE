# New G5 Boundary Case Acquisition Design Research

> **模式: READ-ONLY / RESEARCH DESIGN ONLY / NO CODE / NO IMPLEMENTATION / NO HUMAN VALIDATION / STOP**
> 日期: 2026-09-19
> Gate: G5_BOUNDARY_CASE_ACQUISITION_DESIGN_RESEARCH
> 前置: G5 Boundary Generalization Gate (COMPLETE, GENERALIZATION_CONDITIONAL, 0 new TRUE_G5)
> 本文件: 设计最小成本 Human Validation Protocol，从已有 181 新案例中获取新 G5 Boundary Cases。

---

## 0. Core Question

```
如何以最小 Human 成本，
获得一批真正新的 G5 Boundary Cases，
用于验证 Evidence Boundary Governance？

前序研究结论：
  - 181 个新案例中 0 个 TRUE_G5
  - 原因：所有 14 个 UNCERTAIN 案例都在原 29 中
  - Signal 无法在新数据上验证
  - 需要新的 TRUE_G5 Boundary Cases

本研究只设计 Protocol，不执行。
```

---

## 1. Frozen Baseline

```
RESEARCH_BASELINE = FROZEN (v1)
FROZEN_BASELINE = INTACT
BASELINE_DRIFT = 0
SYSTEM_MODIFIED = FALSE
IMPLEMENTATION_AUTHORIZED = FALSE
MODEL_TRAINING = FALSE
EXTERNAL_DATASET_IMPORTED = FALSE
CAPABILITY_CREATED = FALSE
RUNTIME_AUTHORITY = ZERO
PRODUCTION = FALSE
STOP = TRUE
```

---

## 2. Data Used

```
181 new cases (from G5 Boundary Generalization Gate):
  - 63 M-A definitive (MACHINE_RESOLVABLE)
  - 46 academic G1-G4 (FALSE_G5)
  - 37 biotech G1-G4 (FALSE_G5)
  - 35 fin/edu G1-G4 (FALSE_G5)

Original 29 boundary cases (for historical G5 pattern analysis):
  - 18 TRUE_G5 (E4)
  - 11 FALSE_G5 (E2/E3)

M-A pilot 79 cases (full evidence state: fig_prefix, drawing_extent, VR, XO, distance)
Evidence Configuration Family 50 cases (structural config groups)
```

---

## 3. Historical G5 Pattern Analysis

### 3.1 What Did TRUE_G5 Cases Look Like?

```
From original 18 TRUE_G5 (9 with M-A data):

  case_type distribution:
    ambiguous_fragment: 5 (55.6%)
    Type_B_negative: 4 (44.4%)

  drawing_extent_present: True (9/9 = 100%)
  fig_prefix: mixed (True 5, False 4)
  vertical_relation: mixed (above 5, below 3, inside 1)
  x_overlap: mixed (True 6, False 3)

  final_judgment:
    uncertain: 7 (77.8%) — couldn't judge, evidence at boundary
    yes: 1 (CE2_YES) — definitive but different from paired case
    no: 1 (CE2_NO) — definitive but different from paired case

  sem_boundary_assessment:
    YES (standalone "Fig." fragment): 3
    POSSIBLE (non-FIG text near drawing): 2
    NO (text fragment too short): 2
    N/A (not UNCERTAIN, CE2): 2
```

### 3.2 What Did FALSE_G5 Cases Look Like?

```
From original 11 FALSE_G5 (7 with M-A data):

  case_type: Type_A_negative (7/7 = 100%)
  drawing_extent_present: False (7/7 = 100%)
  final_judgment: uncertain (7/7 = 100%)

  → FALSE_G5 signature: Type_A_negative + dep=False + UNCERTAIN
```

### 3.3 What Did MACHINE_RESOLVABLE Cases Look Like?

```
From 63 new M-A definitive:

  case_type distribution:
    caption_like: 39 (61.9%) → 100% YES, 0% G5
    ambiguous_fragment: 14 (22.2%) → mixed YES/NO
    Type_B_negative: 4 (6.3%) → all YES
    subfigure_label: 4 (6.3%) → all YES
    reference_like: 1 (1.6%) → YES
    Type_A_negative: 1 (1.6%) → YES (anomaly: dep=False but SUFFICIENT)

  drawing_extent_present: True (62), False (1)
```

### 3.4 The Critical Overlap

```
case_types that appear in BOTH TRUE_G5 and MACHINE_RESOLVABLE:
  ambiguous_fragment: TRUE_G5=5, MACHINE_RESOLVABLE=14 → NOT reliable signal alone
  Type_B_negative: TRUE_G5=4, MACHINE_RESOLVABLE=4 → NOT reliable signal alone

  → case_type alone CANNOT distinguish TRUE_G5 from MACHINE_RESOLVABLE.
  → Multiple fields must be used in combination.
  → The key differentiator is UNCERTAIN status (judgment difficulty),
    but this is only known AFTER Human review.
```

---

## 4. CE2-Like Pattern Discovery

### 4.1 Mixed-Judgment Evidence Configurations

```
Among 63 new M-A definitive cases, found 3 evidence configurations
where MULTIPLE cases share IDENTICAL structural evidence
but receive DIFFERENT Human judgments:

  Config 1: fig=True|dep=True|VR=below|XO=True|type=ambiguous_fragment
    6 cases: 5 YES, 1 NO
    → Same structure, different judgment = CE2 pattern

  Config 2: fig=True|dep=True|VR=below|XO=False|type=ambiguous_fragment
    3 cases: 2 YES, 1 NO
    → Same structure, different judgment = CE2 pattern

  Config 3: fig=True|dep=True|VR=above|XO=True|type=ambiguous_fragment
    3 cases: 2 YES, 1 NO
    → Same structure, different judgment = CE2 pattern

  Total: 12 cases in 3 CE2-like configs.
```

### 4.2 Why These Are Strongest G5 Candidates

```
CE2 proved: identical evidence → different judgment → semantic content is differentiator.
  → This IS the G5 signature.

The 12 mixed-config cases show the SAME pattern:
  → Identical structural evidence (fig, dep, VR, XO, case_type all same)
  → Different Human judgments (YES vs NO)
  → The difference must come from semantic content (not structure)
  → These are the STRONGEST candidates for TRUE_G5

  The Human made a definitive judgment (YES/NO),
  but the judgment was based on SEMANTIC CONTENT, not structure.
  → If we ask "did you need semantic understanding?" → likely YES → TRUE_G5.

  These 12 cases are Tier 1a (highest priority).
```

---

## 5. Tier Classification Design

### 5.1 Criteria (Multi-Field, Not Single Field)

```
Tier 1a (HIGHEST priority, 12 cases):
  Criteria: ambiguous_fragment + dep=True + in CE2-like mixed-judgment config
  Historical G5 signal: CE2 pattern (identical evidence → different judgment)
  Expected G5 rate: HIGHEST (CE2-like signature)

Tier 1b (HIGH priority, 6 cases):
  Criteria: ambiguous_fragment or Type_B_negative + dep=True + NOT in mixed config
  Historical G5 rate: 26-50% (from original 29)
  Expected G5 rate: 12-35% (definitive cases, lower than UNCERTAIN)

Tier 2 (MODERATE priority, 15 cases):
  Criteria: subfigure_label, reference_like, or non-standard caption_like
  Historical G5 rate: unknown (new case_types or non-standard configs)
  Purpose: test new case_types for potential G5

Tier 3 (SKIP, 130 cases):
  Criteria: academic/biotech/fin-edu G1-G4, or Type_A_negative with dep=False
  Historical G5 rate: 0%
  Use: negative examples only

Tier 4 (SKIP, 29 cases):
  Criteria: caption_like standard config (fig=True, dep=True, VR=below, XO=True)
  Historical G5 rate: 0%, 100% YES
  Use: negative examples only
```

### 5.2 Distribution

| Tier | Count | % | Human Review? | Expected G5 |
|------|------:|---:|:---:|---|
| Tier 1a | 12 | 6.3% | YES (highest) | 2-4 (CE2-like) |
| Tier 1b | 6 | 3.1% | YES (high) | 0-2 |
| Tier 2 | 15 | 7.8% | Phase 2 | NOT_ESTIMABLE |
| Tier 3 | 130 | 67.7% | NO | 0 |
| Tier 4 | 29 | 15.1% | NO | 0 |
| **Total** | **192** | 100% | | |

### 5.3 No Single Field Used as Signal

```
This tier classification does NOT use any single field as a G5 signal.

  NOT drawing_extent_present alone (proven insufficient in Generalization Gate).
  NOT fig_prefix alone (mixed in both TRUE_G5 and MACHINE_RESOLVABLE).
  NOT case_type alone (appears in both TRUE_G5 and MACHINE_RESOLVABLE).
  NOT distance alone (varies within TRUE_G5).

  Instead, uses MULTI-FIELD COMBINATION:
  - case_type + dep + structural config + judgment pattern (mixed/not)
  - The CE2-like mixed-judgment pattern is the strongest signal.
  - It requires ≥2 cases with same config and different judgments.
```

---

## 6. Minimal Human Task Design

### 6.1 The Task

```
For each Tier 1/2 case, Human answers ONE question:

  "现有 Evidence 是否已经足够让机器完成该任务？"

  A. 足够 → MACHINE_RESOLVABLE
  B. 不足，但可以通过已有/可获得 Evidence 解决 → FALSE_G5 (G1-G4)
  C. Evidence 已经充分，但仍需要语义判断 → TRUE_G5 candidate
  D. UNCERTAIN → cannot determine

  Human does NOT:
  - Write the answer (YES/NO)
  - Write rules
  - Write explanations
  - Write detectors
  - Write features
  - Write semantic labels
  - Modify Evidence
```

### 6.2 Why This Task Works

```
The task asks about EVIDENCE SUFFICIENCY, not SEMANTIC ANSWER.

  A → Evidence is sufficient → machine could handle → MACHINE_RESOLVABLE.
  B → Evidence is insufficient but recoverable → FALSE_G5 (G1-G4).
  C → Evidence is sufficient BUT semantic judgment still needed → TRUE_G5.
  D → Cannot determine → INDETERMINATE.

  This is the SAME distinction as the 4-state classification:
  MACHINE_RESOLVABLE / FALSE_G5 / TRUE_G5 / INDETERMINATE.

  The task does NOT learn Human's answer.
  It learns Human's ASSESSMENT OF EVIDENCE SUFFICIENCY.
  → This is a Boundary Signal, not an Answer.
  → Consistent with CE2 finding: Answer ≠ Learning Signal, Boundary Signal IS.
```

### 6.3 CE2 Protection

```
For Tier 1a (mixed-config) cases, the Human task has special significance:

  These cases already have different judgments (YES vs NO) with identical evidence.
  If Human answers:
    C for both → confirms TRUE_G5 (evidence sufficient, semantic judgment needed).
    A for both → contradicts CE2 (evidence was sufficient, but judgments differ).
    A for one, C for other → MIXED (one machine-resolvable, one G5).

  The most likely outcome (based on CE2):
  → Both get C → TRUE_G5 confirmed.
  → This would produce new TRUE_G5 cases for Generalization validation.
```

---

## 7. Acquisition Strategy Comparison

### 7.1 Three Strategies

| Metric | A: All 181 | B: Tiered T1+T2 | C: Top-K T1 |
|--------|-----------:|:---------------:|:-----------:|
| Human cases | 192 | 33 | 18 |
| Expected G5 yield | 2-6 | 2-6 | 2-6 |
| Review reduction | 0% | 82.8% | 90.6% |
| Candidate coverage | 100% | 17.2% | 9.4% |
| Selection bias | NONE | MODERATE | HIGH |
| Missed G5 risk | LOW | LOW | MODERATE |

### 7.2 Recommended: Strategy B (Tiered T1→T2)

```
Phase 1: Review Tier 1 (18 cases)
  - 12 Tier 1a (CE2-like, highest priority)
  - 6 Tier 1b (same case_type, high priority)
  - Expected TRUE_G5: 2-6
  - Expected FALSE_G5: ~0 (dep=True, no G1/G2)
  - Expected MACHINE_RESOLVABLE: ~12-16
  - Human cost: 18 minimal tasks (A/B/C/D)

Phase 2: If Tier 1 yields <3 TRUE_G5, review Tier 2 (15 cases)
  - New case_types (subfigure_label, reference_like)
  - Non-standard caption_like
  - Expected TRUE_G5: NOT_ESTIMABLE
  - Human cost: 15 additional minimal tasks

Phase 3: Tier 3 (130) + Tier 4 (29) NOT reviewed
  - Historical G5 rate: 0%
  - Used as negative examples for Generalization validation

Total maximum Human cost: 33 minimal tasks (Strategy B).
Total minimum Human cost: 18 minimal tasks (if Tier 1 sufficient).
```

### 7.3 Why Strategy B

```
Strategy B balances:
  - HIGH G5 yield (same as A, because G5 only in Tier 1/2)
  - LOW Human cost (82.8% reduction vs A)
  - LOW selection bias (Tier 3/4 have 0% historical G5)
  - LOW missed G5 risk (Tier 3/4 have 0% historical G5)

Strategy A (all 181) wastes 159 reviews on cases with 0% G5 probability.
Strategy C (Tier 1 only) misses Tier 2 new case_types.
Strategy B is optimal.
```

---

## 8. Targeted vs Random Screening

### 8.1 The Question

```
如果我们只让 Human 审查"Evidence 已经比较完整、但语义仍然可能存在冲突"的案例，
是否会比随机抽取更容易发现 TRUE_G5？
```

### 8.2 The Data

```
Targeted (Tier 1, 18 cases):
  Historical G5 rate for ambiguous_fragment+Type_B_negative with dep=True:
    - UNCERTAIN cases: 7/7 = 100% (original 29)
    - Definitive cases (CE2): 2/2 = 100% (CE2 pair)
    - All definitive: 2/16 = 12.5% (including CE2 + 14 new)
    - Mixed-config cases: unknown (12 new, not yet tested)
  Expected TRUE_G5 from 18 Tier 1: 2-6 (12-35% rate)

Random (18 from 181):
  Overall definitive G5 rate: 2/65 = 3.1% (CE2 pair among 65 definitive)
  Expected TRUE_G5 from 18 random: ~1 (3.1% rate)

Efficiency ratio: 2-6x (targeted vs random)
```

### 8.3 The Answer

```
CONDITIONAL

  Evidence FOR:
  - Targeted cases have same case_type as historical TRUE_G5 (26-50% rate).
  - 12 cases show CE2-like mixed-judgment pattern (strongest G5 signal).
  - Historical G5 rate for these case_types: 26-50% vs 3.1% overall.
  - Efficiency ratio: 2-6x.

  Evidence AGAINST:
  - Only 2 CE2 definitive TRUE_G5 cases (very small sample).
  - 0/18 new Tier 1 cases confirmed as TRUE_G5 yet.
  - The 26-50% rate is from UNCERTAIN cases, Tier 1 are DEFINITIVE.
  - Definitive G5 rate (12.5%) is much lower than UNCERTAIN (100%).
  - Statistical significance: NOT_ACHIEVABLE.

  CONCLUSION: CONDITIONAL
  - Pattern is supported (same case_type, CE2-like mixed configs).
  - Statistics are insufficient (2 CE2 cases, 18 Tier 1 cases).
  - Targeted screening is LIKELY more efficient but NOT PROVEN.
  - The mixed-config pattern (12 cases) is the strongest evidence.
```

---

## 9. Acceptance Metrics

### 9.1 Minimum Acceptance Criteria

```
For the next phase (Human Validation), define:

1. NEW_TRUE_G5_COUNT
   Target: ≥3 (to add to existing 18 for Generalization validation)
   Minimum: ≥1 (at least one new TRUE_G5 to test Signal)
   If 0: Generalization remains unvalidatable.

2. NEW_FALSE_G5_COUNT
   Expected: ~0 (Tier 1 has dep=True, no G1/G2)
   If >0: new FALSE_G5 type discovered (G2 from dep=True cases)

3. NEW_MACHINE_RESOLVABLE_COUNT
   Expected: ~12-16 (remaining Tier 1 cases)

4. HUMAN_CASE_COUNT
   Phase 1: 18 (Tier 1)
   Phase 2: +15 (Tier 2, if needed)
   Maximum: 33

5. G5_YIELD
   = NEW_TRUE_G5_COUNT / HUMAN_CASE_COUNT
   Target: ≥17% (3/18)
   Historical baseline: 12-35%

6. HUMAN_REVIEW_REDUCTION
   = (192 - HUMAN_CASE_COUNT) / 192
   Phase 1: 90.6% (174/192 skipped)
   Phase 2: 82.8% (159/192 skipped)

7. CANDIDATE_COVERAGE
   = Tier 1+2 cases / total new cases
   = 33/192 = 17.2%

8. MISSED_G5_RISK
   Risk of TRUE_G5 in Tier 3/4 (not reviewed):
   Historical: 0% (G1-G4 = 0% G5, caption_like standard = 0% G5)
   Risk: LOW (but not zero — untested case_types in Tier 3/4)
```

### 9.2 Success Criteria

```
SUCCESS: NEW_TRUE_G5_COUNT ≥ 3
  → Enough new TRUE_G5 to attempt Generalization validation.
  → Combined with original 18: 21 total TRUE_G5 cases.
  → Can re-test Signal on 3+ new TRUE_G5.

PARTIAL_SUCCESS: NEW_TRUE_G5_COUNT = 1-2
  → Some new TRUE_G5 but insufficient for statistical validation.
  → Can test Signal qualitatively but not quantitatively.

FAILURE: NEW_TRUE_G5_COUNT = 0
  → No new TRUE_G5 found.
  → Signal remains unvalidatable.
  → May indicate: G5 is rarer in definitive cases than expected.
  → Or: targeted screening insufficient.
```

---

## 10. Selection Bias Analysis

### 10.1 Bias Sources

```
1. CASE_TYPE BIAS:
   Tier 1 only includes ambiguous_fragment + Type_B_negative.
   Other case_types (subfigure_label, reference_like) in Tier 2.
   caption_like, Type_A_negative excluded (Tier 3/4).
   → Bias: only tests G5 for specific case_types.
   → Mitigation: Tier 2 includes new case_types.

2. DEP=TRUE BIAS:
   Tier 1 requires dep=True.
   dep=False cases excluded (Tier 3).
   → Bias: only tests G5 for structurally complete cases.
   → Justification: G5 requires structurally complete evidence (Layer 1-5 confirmed).

3. DEFINITIVE BIAS:
   All 181 new cases are definitive (YES/NO, not UNCERTAIN).
   Original TRUE_G5 were mostly UNCERTAIN (7/9).
   → Bias: tests G5 in definitive cases, not UNCERTAIN.
   → Risk: definitive G5 rate (12.5%) << UNCERTAIN G5 rate (100%).
   → Mitigation: the minimal task (A/B/C) converts definitive to G5 assessment.

4. DOMAIN BIAS:
   All cases from academic papers.
   Biotech/FinEdu have 0 G5.
   → Bias: only tests G5 in academic domain.
   → Acknowledged: cross-domain G5 untested.

5. MIXED-CONFIG BIAS:
   Tier 1a (12 cases) are specifically from mixed-judgment configs.
   → Bias: over-represents CE2-like cases.
   → Justification: CE2 is the strongest G5 signal.
   → Risk: may over-estimate G5 rate.
```

### 10.2 Bias Mitigation

```
1. Tier 2 includes new case_types → reduces case_type bias.
2. Tier 3/4 used as negative examples → provides contrast.
3. The minimal task (A/B/C) does NOT ask for YES/NO → reduces answer bias.
4. Multiple Human reviewers (if authorized) → reduces reviewer bias.
5. Record ALL results (including MACHINE_RESOLVABLE) → prevents cherry-picking.

REMAINING BIAS:
  - Definitive bias (all new cases are definitive, not UNCERTAIN).
  - Domain bias (all academic).
  - These are ACKNOWLEDGED but NOT eliminable without new data.
```

---

## 11. Final Questions

### Q1: 181 个案例中哪些最值得 Human Review？

```
Tier 1a (12 cases, HIGHEST priority):
  - ambiguous_fragment + dep=True + CE2-like mixed-judgment config
  - Same structural evidence → different Human judgments
  - This IS the G5 signature (CE2 pattern)
  - Cases: arxiv_2402.18619_p28_457_234, arxiv_2402.18619_p28_479_214,
    is11_efficientnet_p6_511_629, arxiv_2402.18619_p10_132_629,
    arxiv_2402.18619_p28_256_214, arxiv_2402.18619_p19_339_297,
    arxiv_2402.18619_p10_183_252, is11_efficientnet_p4_188_461,
    is11_resnet_p5_359_225, is11_resnet_p1_412_338,
    arxiv_2402.18619_p19_83_745, is11_med_001_p15_261_316

Tier 1b (6 cases, HIGH priority):
  - ambiguous_fragment or Type_B_negative + dep=True + not in mixed config
  - Same case_type as historical TRUE_G5 (26-50% rate)
  - Cases: is11_efficientnet_p8_328_261, arxiv_2402.18619_p17_184_561,
    is11_cs_001_p5_292_225, arxiv_2402.18619_p18_432_93,
    is11_resnet_p4_320_146, is11_resnet_p1_435_316

Total Tier 1: 18 cases for Phase 1 Human Review.
```

### Q2: 为什么？

```
1. Historical G5 pattern: TRUE_G5 cases had case_type=ambiguous_fragment(5) or Type_B_negative(4).
   These case_types produced 9/9 TRUE_G5 in original 29 (100% of TRUE_G5 with M-A data).

2. CE2-like mixed configs: 12 cases show identical structural evidence → different judgments.
   This is the CE2 signature → strongest G5 indicator.

3. dep=True: ALL TRUE_G5 had drawing_extent=True (9/9=100%).
   Excluding dep=False (FALSE_G5) eliminates 130 known FALSE_G5 cases.

4. Multi-field combination: NOT using any single field alone.
   Using case_type + dep + mixed-config pattern together.

5. Efficiency: 18 cases capture all historical G5 case_types,
   while excluding 159 cases with 0% historical G5 rate.
```

### Q3: 如何最大限度减少 Human 数量？

```
1. Tier screening: 192 → 18 (Phase 1) = 90.6% reduction.
2. Minimal task: ONE question (A/B/C/D) per case, not full review.
3. Phase 2 conditional: only if Phase 1 yields <3 TRUE_G5.
4. Tier 3/4 excluded: 0% historical G5, used as negative examples.

Maximum Human cost: 33 tasks (Phase 1+2).
Minimum Human cost: 18 tasks (Phase 1 only).
Each task: ONE question (A/B/C/D), ~30 seconds estimated.

Total estimated time: 18-33 × 30s = 9-17 minutes.
```

### Q4: 如何避免 Selection Bias？

```
Acknowledged biases:
  1. Case_type bias: only ambiguous_fragment + Type_B_negative in Tier 1.
     → Mitigated by Tier 2 (new case_types).
  2. Definitive bias: all new cases are definitive (not UNCERTAIN).
     → Acknowledged, NOT eliminable without new data.
  3. Domain bias: all academic papers.
     → Acknowledged, biotech/fin-edu have 0 G5.

Mitigations:
  1. Tier 2 includes new case_types (subfigure_label, reference_like).
  2. Tier 3/4 used as negative examples (not ignored).
  3. Record ALL results (including MACHINE_RESOLVABLE).
  4. Minimal task doesn't ask for YES/NO (reduces answer bias).
  5. Report biases transparently in results.

REMAINING RISK:
  - If TRUE_G5 only occurs in UNCERTAIN cases (not definitive),
    Tier 1 screening may yield 0 TRUE_G5.
  - This would mean: G5 cannot be found in definitive cases.
  - This is a VALID research finding (not a failure).
```

### Q5: 最小 Human Review Protocol 是什么？

```
PROTOCOL:

  Input: 18 Tier 1 cases (Phase 1).
  Task per case: ONE question.

  Question: "现有 Evidence 是否已经足够让机器完成该任务？"

  A. 足够 → MACHINE_RESOLVABLE
  B. 不足，但可以通过已有/可获得 Evidence 解决 → FALSE_G5
  C. Evidence 已经充分，但仍需要语义判断 → TRUE_G5
  D. UNCERTAIN → INDETERMINATE

  Human does NOT:
  - Write YES/NO answer
  - Write rules or explanations
  - Modify Evidence or system

  Output:
  - 18 A/B/C/D responses
  - Classification: TRUE_G5 (C), FALSE_G5 (B), MACHINE_RESOLVABLE (A), INDETERMINATE (D)

  Phase 2 (conditional):
  - If NEW_TRUE_G5 < 3: review 15 Tier 2 cases with same protocol.
  - If NEW_TRUE_G5 ≥ 3: proceed to Generalization validation.

  Total: 18-33 minimal tasks.
```

### Q6: 需要多少新 TRUE_G5 才足以进行下一阶段研究？

```
MINIMUM: 1 new TRUE_G5
  → Can qualitatively test Signal on 1 new case.
  → Insufficient for statistical validation.

TARGET: 3 new TRUE_G5
  → Combined with original 18: 21 total.
  → Can test Signal on 3 new cases (in addition to original 14 UNCERTAIN).
  → Still small but meaningful for pattern validation.

IDEAL: 6 new TRUE_G5
  → Combined with original 18: 24 total.
  → More robust Signal validation.
  → But NOT_ESTIMABLE whether achievable.

STATISTICAL THRESHOLD:
  Not defined. The research does NOT use statistical significance tests
  (sample sizes too small throughout). Pattern-based validation only.

  If NEW_TRUE_G5 = 0:
  → Signal remains unvalidatable.
  → May indicate G5 is UNCERTAIN-specific (not in definitive cases).
  → This is a valid finding, not a failure.
```

### Q7: 是否值得进行这次 Human Validation？

```
SUPPORTED.

  Reasons:
  1. 18 cases with historical 26-50% G5 rate → 2-6 expected TRUE_G5.
  2. 12 CE2-like mixed-config cases → strongest G5 signal.
  3. Minimal task (A/B/C/D) → low Human cost (~9-17 minutes).
  4. 90.6% review reduction vs full review.
  5. Cannot advance Generalization without new TRUE_G5.
  6. No alternative path exists in READ-ONLY mode.

  Risks:
  1. May yield 0 TRUE_G5 (definitive G5 rate unknown).
  2. Selection bias (case_type, definitive, domain).
  3. Small sample (18 cases).

  Risk assessment:
  - If 0 TRUE_G5: valid finding (G5 may be UNCERTAIN-specific).
  - If 1-2: partial success (qualitative validation).
  - If 3+: success (pattern validation possible).
  - Human cost is minimal (18 tasks, ~15 minutes).
  - No system modification required.

  CONCLUSION: WORTH IT.
  Low cost, high potential value, no system risk.
```

### Q8: 下一阶段是否应该只做 Human Validation？

```
YES — if NEXT_GATE is authorized.

  The next phase should be:
  NEXT_GATE = NEW_G5_HUMAN_VALIDATION

  Content:
  1. Execute the minimal Human Review Protocol (18-33 A/B/C/D tasks).
  2. Classify results: TRUE_G5 / FALSE_G5 / MACHINE_RESOLVABLE / INDETERMINATE.
  3. If ≥1 new TRUE_G5: re-run G5 Boundary Generalization Gate with new data.
  4. If 0 new TRUE_G5: report finding (G5 may be UNCERTAIN-specific).

  NOT in next phase:
  - No Signal design.
  - No Routing implementation.
  - No model training.
  - No system modification.
  - Only Human Validation + Generalization re-test.

  The next phase is PURELY Human Validation.
  No system development.
  No new capabilities.
  No new detectors.
  Just: ask 18-33 questions, classify, re-test Signal.
```

---

## 12. The Complete Pipeline Design

```
181 new cases
       ↓
Candidate Screening (multi-field evidence state analysis)
       ↓
Tier 1a (12 CE2-like) + Tier 1b (6 same-case-type)
       ↓
Minimal Human Validation (A/B/C/D, 18 tasks)
       ↓
Classify: TRUE_G5 (C) / FALSE_G5 (B) / MACHINE_RESOLVABLE (A) / INDETERMINATE (D)
       ↓
If TRUE_G5 ≥ 3:
  → New Boundary Set (original 18 + new TRUE_G5)
  → Re-run G5 Boundary Generalization Gate
  → Test Signal on new TRUE_G5

If TRUE_G5 < 3:
  → Phase 2: Tier 2 (15 cases)
  → Re-evaluate

If TRUE_G5 = 0:
  → Finding: G5 may be UNCERTAIN-specific
  → Report and STOP

NOTE: This pipeline is DESIGNED only.
      NOT implemented.
      NEXT_GATE = NEW_G5_HUMAN_VALIDATION (if authorized).
```

---

## 13. Over-Design Audit

```
  O1: Modified system code? → NO
  O2: Modified P1-P7? → NO
  O3: Modified DGF/DEF? → NO
  O4: Modified M-A? → NO
  O5: Modified TLD? → NO
  O6: Modified Human Review UI? → NO
  O7: Trained model? → NO
  O8: Downloaded external data? → NO
  O9: Implemented Routing? → NO
  O10: Implemented Boundary Detector? → NO
  O11: Modified Frozen Baseline? → NO
  O12: Created Capability? → NO
  O13: Entered Runtime? → NO
  O14: New field? → NO
  O15: New schema? → NO
  O16: New observation? → NO
  O17: New threshold? → NO
  O18: Executed Human Validation? → NO (DESIGNED only)

  ALL CHECKS: FALSE
  OVER_DESIGN_AUDIT = PASS
```

---

## 14. Limitations

```
  ACQ-L-01: SMALL TIER 1 SAMPLE
    18 cases for Phase 1.
    Expected TRUE_G5: 2-6 (uncertain estimate).
    May yield 0 if G5 is UNCERTAIN-specific.

  ACQ-L-02: DEFINITIVE BIAS
    All 181 new cases are definitive (YES/NO).
    Original TRUE_G5 were mostly UNCERTAIN (7/9).
    Definitive G5 rate (12.5%) << UNCERTAIN (100%).
    Tier 1 may have lower G5 rate than historical.

  ACQ-L-03: NO CROSS-DOMAIN
    All cases from academic papers.
    Biotech/FinEdu have 0 G5.
    Cannot test G5 in non-academic domains.

  ACQ-L-04: SINGLE REVIEWER
    Protocol assumes single Human reviewer.
    Inter-rater reliability unknown.
    (Multi-reviewer would require additional authorization.)

  ACQ-L-05: MIXED-CONFIG OVER-REPRESENTATION
    Tier 1a (12 cases) are specifically CE2-like.
    May over-estimate G5 rate.
    But: CE2 is the strongest G5 signal (justified).

  ACQ-L-06: NOT_ESTIMABLE G5 YIELD
    Expected 2-6 is based on historical rates (26-50%).
    But historical rates are from UNCERTAIN cases.
    Tier 1 are DEFINITIVE → rate may be much lower (12.5%).
    True expected: 2 (conservative) to 6 (optimistic).

  ACQ-L-07: NO STATISTICAL THRESHOLD
    Cannot define statistical significance threshold.
    Sample sizes too small throughout.
    Pattern-based validation only.
```

---

## 15. Seven-Layer Convergence (Updated)

```
  Layer 1: Evidence Boundary Structure — 13 G5, 4 reclassified.
  Layer 2: Evidence Configuration Family (CE2) — Answer NOT learnable, Signal IS.
  Layer 3: Evidence Boundary Expansion — 62.1% TRUE_G5, 37.9% FALSE_G5.
  Layer 4: Human Review Reduction — 77.8% irreducible.
  Layer 5: G5 Evidence Boundary Governance — 37.9% FALSE_G5, Signal 100% on 14.
  Layer 6: G5 Boundary Generalization — Signal UNVALIDATED, 0 new TRUE_G5.
  Layer 7: Case Acquisition Design (this study) — 18 Tier 1 candidates, 2-6 expected G5.

  SEVEN-LAYER CONVERGENCE:
  → G5 is genuine (Layers 1-4).
  → FALSE_G5 is widespread (Layers 3, 5, 6).
  → Signal shows promise but UNVALIDATED (Layers 5, 6).
  → Cannot validate without new TRUE_G5 (Layer 6).
  → 18 Tier 1 candidates identified for Human Validation (Layer 7).
  → 12 CE2-like cases are strongest candidates.
  → Minimal Human task designed (A/B/C/D).
  → Strategy B recommended (82.8% reduction, 2-6 expected G5).
  → NEXT_GATE = NEW_G5_HUMAN_VALIDATION (if authorized).
```

---

## 16. Files Created

```
tmp/g5_boundary_case_acquisition_design.md          (this file)
tmp/g5_boundary_case_acquisition_design.json         (structured data)
tmp/g5_boundary_case_acquisition_candidates.csv      (192 cases, 14 fields)
```

---

## 17. Final Governance State

```
RESEARCH_STATUS = COMPLETE

SYSTEM_MODIFIED = FALSE
IMPLEMENTATION_AUTHORIZED = FALSE
MODEL_TRAINING = FALSE
EXTERNAL_DATASET_IMPORTED = FALSE
CAPABILITY_CREATED = FALSE

FROZEN_BASELINE = INTACT
BASELINE_DRIFT = 0

NEW_FIELD = NONE
NEW_SCHEMA = NONE
NEW_OBSERVATION = NONE
NEW_RULE = NONE
NEW_DETECTOR = NONE
NEW_SIGNAL = NONE
NEW_CAPABILITY = NONE

RUNTIME_AUTHORITY = ZERO
PRODUCTION = FALSE

NEXT_GATE = NEW_G5_HUMAN_VALIDATION

STOP = TRUE
```

---

## STOP

```
New G5 Boundary Case Acquisition Design Research is COMPLETE.

SUMMARY:
  - 192 new cases analyzed (from G5 Boundary Generalization Gate)
  - Tier classification: Tier 1a (12 CE2-like), Tier 1b (6 same-type), Tier 2 (15 new types), Tier 3 (130 FALSE_G5), Tier 4 (29 MACHINE_RESOLVABLE)
  - 18 Tier 1 cases identified for Human Review (90.6% reduction)
  - 12 CE2-like mixed-config cases (strongest G5 signal)
  - Expected TRUE_G5: 2-6 (12-35% historical rate)
  - Minimal Human task: A/B/C/D (one question per case)
  - Strategy B recommended: Tier 1 → Tier 2 (max 33 tasks)
  - Targeted vs Random: CONDITIONAL (2-6x efficiency, but small sample)
  - No single field used as signal (multi-field combination)
  - Selection bias: acknowledged (case_type, definitive, domain)
  - NEXT_GATE = NEW_G5_HUMAN_VALIDATION

KEY FINDING:
  12 cases show CE2-like pattern (identical structural evidence → different judgments).
  These are the strongest G5 candidates.
  The minimal task (A/B/C/D) can convert definitive judgments to G5 assessments.
  Expected 2-6 new TRUE_G5 from 18 cases (~15 minutes of Human time).

  不得自动进入 Implementation。
  不得训练模型。
  不得引入外部训练集。
  不得修改 Frozen Baseline。
  NEXT_GATE = NEW_G5_HUMAN_VALIDATION (if authorized).
  STOP = TRUE.
```
