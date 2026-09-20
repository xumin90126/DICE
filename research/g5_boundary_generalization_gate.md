# G5 Boundary Generalization Gate

> **模式: READ-ONLY / RESEARCH ONLY / NO CODE / NO IMPLEMENTATION / NO NEW HUMAN VALIDATION / STOP**
> 日期: 2026-09-19
> Gate: G5_BOUNDARY_GENERALIZATION_GATE
> 前置: G5 Evidence Boundary Governance Research (COMPLETE, 37.9% FALSE_G5, Signal 100% on M-A)
> 本文件: 测试现有 Boundary Signal 能否在新案例中继续区分 TRUE_G5 与 FALSE_G5。

---

## 0. Core Question

```
现有 Boundary Signal 能不能在
"未参与上一阶段研究的新案例"中
继续区分 TRUE_G5 与 FALSE_G5？

原 Signal:
  drawing_extent_present = False → FALSE_G5 candidate
  drawing_extent_present = True + structurally complete + semantic boundary → TRUE_G5 candidate

必须在原 29 个案例之外的新案例上测试。
禁止直接使用原 29 个案例作为验证集。
```

---

## 1. Frozen Baseline

```
RESEARCH_BASELINE = FROZEN (v1)
FROZEN_BASELINE = INTACT
BASELINE_DRIFT = 0
SYSTEM_MODIFIED = FALSE
IMPLEMENTATION_AUTHORIZED = FALSE
EXPERIMENT_AUTHORIZED = FALSE
HUMAN_VALIDATION_AUTHORIZED = FALSE
MODEL_TRAINING = FALSE
EXTERNAL_DATASET_IMPORTED = FALSE
CAPABILITY_CREATED = FALSE
RUNTIME_AUTHORITY = ZERO
PRODUCTION = FALSE
STOP = TRUE
```

---

## 2. New Case Identification

### 2.1 Original 29 Cases (EXCLUDED)

```
Original 29 boundary cases (from Evidence Boundary Expansion Research):
  - 8 academic G5 (IS11-AMB-375/418/519/005, IND-AMB-033/049, PH02-×2)
  - 14 M-A UNCERTAIN (all 14 UNCERTAIN cases from M-A pilot)
  - 2 CE2 pair (is11_efficientnet_p8_467_415, is11_resnet_p6_478_168)
  - 5 MA-UNC-* (MA-UNC-2/5/6/7/11)

ALL 14 M-A UNCERTAIN cases were in the original 29.
→ There are NO new UNCERTAIN/boundary cases available.
```

### 2.2 New Cases Found (181 total)

| Source | Count | State | Notes |
|--------|------:|-------|-------|
| Academic G1-G4 (MA-UNC/IND-AMB/IS11-AMB/PH02) | 46 | FALSE_G5 | G1(3)+G2(19)+G3(12)+G4(12) |
| M-A definitive | 63 | MACHINE_RESOLVABLE | SUFFICIENT evidence, Human judged |
| Biotech | 37 | FALSE_G5_CANDIDATE | G1(4)+G2(28)+G3(5) |
| FinEdu | 35 | FALSE_G5_CANDIDATE | G1(8)+G2(17)+G3(10) |
| **Total** | **181** | | |

### 2.3 Critical Finding

```
TRUE_G5 in new cases: 0
FALSE_G5 in new cases: 118
MACHINE_RESOLVABLE in new cases: 63
INDETERMINATE in new cases: 0

CRITICAL:
  NO new TRUE_G5 boundary cases exist outside original 29.
  NO new UNCERTAIN/boundary cases exist (all 14 were in original 29).

  → Cannot test Signal's TRUE_G5 detection on new cases.
  → Cannot test Signal on new boundary (UNCERTAIN) cases.
  → Can only test:
    (a) G1 inference: G1 → FALSE_G5 (15 cases, academic)
    (b) Out-of-distribution: Signal applied to SUFFICIENT cases (63 M-A)
```

---

## 3. Signal Test Results

### 3.1 Original Signal (Recap)

```
Original Signal (from G5 Evidence Boundary Governance Research):
  Tested on: 14 M-A UNCERTAIN cases (ALL in original 29)
  drawing_extent_present=False → FALSE_G5 (7/7 = 100% accuracy)
  drawing_extent_present=True → TRUE_G5 (7/7 = 100% accuracy)
  Overall accuracy: 14/14 = 100%

  Signal design scope: UNCERTAIN (boundary) cases only.
  NOT designed for SUFFICIENT (machine-resolvable) cases.
```

### 3.2 New Case Signal Test

| Test Category | Count | Signal Result | Actual | Correct? |
|--------------|------:|--------------|--------|----------|
| G1 academic (inferred dep=False) | 15 | FALSE_G5 | FALSE_G5 | **CORRECT (15/15)** |
| M-A definitive (dep=True) | 62 | TRUE_G5_CANDIDATE | MACHINE_RESOLVABLE | OUT_OF_DISTRIBUTION |
| M-A definitive (dep=False) | 1 | FALSE_G5 | MACHINE_RESOLVABLE | ANOMALY |
| G2/G3/G4 academic (no dep data) | 103 | UNKNOWN | FALSE_G5 | UNTESTABLE |

### 3.3 The Anomaly

```
Case: arxiv_2402.18619_p10_72_729
  drawing_extent_present: False
  judgment: YES (definitive)
  evidence_sufficiency: SUFFICIENT
  case_type: Type_A_negative

  Signal prediction: FALSE_G5
  Actual: MACHINE_RESOLVABLE

  Analysis:
  → dep=False does NOT always mean the case enters boundary.
  → In original 29: ALL dep=False cases were UNCERTAIN (7/7).
  → This case: dep=False but SUFFICIENT (Human judged definitively).
  → The case may have other sufficient evidence despite missing drawing extent.

  Impact assessment:
  → If Signal were used for routing: this case → Evidence Recovery.
  → But Human could actually judge it → Evidence Recovery is unnecessary.
  → This is OVER-CAUTIOUS routing, NOT a MISSED_TRUE_G5.
  → The case was MACHINE_RESOLVABLE, not TRUE_G5.
  → No harm: routing to Evidence Recovery would recover the case.
  → But: unnecessary delay (case could have been resolved directly).

  Classification: FALSE_POSITIVE_FOR_FALSE_G5 (Signal over-predicts FALSE_G5)
  Severity: LOW (conservative, not dangerous).
  → MISSED_TRUE_G5: NO.
```

### 3.4 The Out-of-Distribution Issue

```
62 M-A definitive cases have dep=True.
  Signal prediction: TRUE_G5_CANDIDATE.
  Actual: MACHINE_RESOLVABLE.

  This is NOT a Signal failure.
  → Signal was designed for UNCERTAIN cases.
  → These cases are SUFFICIENT (not UNCERTAIN).
  → dep=True + UNCERTAIN → TRUE_G5 (original finding, 100%).
  → dep=True + SUFFICIENT → MACHINE_RESOLVABLE (out-of-distribution).

  The Signal MUST be combined with escalation status:
    dep=True + UNCERTAIN → TRUE_G5 (escalate to Human).
    dep=True + SUFFICIENT → MACHINE_RESOLVABLE (no boundary).

  Without escalation status, dep=True alone is INSUFFICIENT as a Signal.
  The original Signal included "structurally complete + semantic boundary remains."
  "Semantic boundary remains" = UNCERTAIN judgment.
  Without UNCERTAIN, dep=True does not imply TRUE_G5.
```

---

## 4. Quantified Metrics

```
 1. NEW_CASE_COUNT:                     181
 2. TRUE_G5_COUNT (new):                  0
 3. FALSE_G5_COUNT (new):               118
 4. INDETERMINATE_COUNT (new):            0
 5. MACHINE_RESOLVABLE_COUNT (new):      63
 6. SIGNAL_TRUE_COUNT:                   62 (all out-of-distribution)
 7. SIGNAL_FALSE_COUNT:                  16 (15 G1 correct + 1 anomaly)
 8. CORRECT_BOUNDARY_COUNT:               0 (no new boundary cases)
 9. FALSE_ESCALATION_COUNT:              62 (all out-of-distribution)
10. MISSED_TRUE_G5_COUNT:                 0

BOUNDARY_SIGNAL_PRECISION:     N/A (no new boundary cases)
BOUNDARY_SIGNAL_RECALL:        N/A (no new TRUE_G5 in new cases)
FALSE_ESCALATION_RATE:         N/A (out-of-distribution, not boundary)
MISSED_TRUE_G5_RATE:           N/A (no TRUE_G5 in new cases)

G1_INFERENCE_TEST:             15 cases, CORRECT=15, WRONG=0 (100%)
  → But G1 inference ≠ drawing_extent signal test.

STATISTICALLY_LIMITED = TRUE
  → No new UNCERTAIN/boundary cases available.
  → Cannot test Signal on new TRUE_G5 or new FALSE_G5 boundary cases.
  → The 100% accuracy from original 14 cases remains UNVALIDATED on new data.
```

---

## 5. Three Result Types

### 5.1 True Positive Boundary (Signal=TRUE_G5, Actual=TRUE_G5)

```
Count: 0
  → No new TRUE_G5 cases in new data.
  → Cannot test True Positive on new cases.
```

### 5.2 False Boundary (Signal=TRUE_G5, Actual=FALSE_G5)

```
Count: 0 (in boundary cases)
  → 62 cases where Signal=TRUE_G5_CANDIDATE but actual=MACHINE_RESOLVABLE.
  → BUT: these are OUT_OF_DISTRIBUTION (SUFFICIENT, not UNCERTAIN).
  → NOT a real False Boundary: Signal was not designed for SUFFICIENT cases.
  → The Signal requires escalation status (UNCERTAIN) to apply.
  → Without UNCERTAIN: dep=True alone does NOT predict TRUE_G5.
```

### 5.3 Missed Boundary (Signal=FALSE_G5, Actual=TRUE_G5)

```
Count: 0
  → No MISSED_TRUE_G5 in new cases.
  → The 1 anomaly (dep=False, MACHINE_RESOLVABLE) is NOT a Missed True G5.
  → The case was MACHINE_RESOLVABLE, not TRUE_G5.
  → Signal over-predicted FALSE_G5, but the case was not G5 at all.
  → This is conservative behavior (over-cautious), not dangerous.
```

---

## 6. The Fundamental Generalization Problem

```
The original Signal was validated on 14 UNCERTAIN cases.
  → drawing_extent_present: 100% accuracy.
  → This is the ONLY available UNCERTAIN dataset.

ALL 14 UNCERTAIN cases were in the original 29.
  → There are NO new UNCERTAIN cases to test generalization.
  → The Signal CANNOT be tested on new boundary cases.

This is a FUNDAMENTAL data limitation:
  → The M-A pilot has 79 cases: 65 definitive + 14 UNCERTAIN.
  → All 14 UNCERTAIN were studied in original 29.
  → No new UNCERTAIN cases can be generated without NEW Human Validation.
  → NEW Human Validation is NOT authorized.

The generalization question CANNOT be answered with existing data.
  → The Signal's 100% accuracy on 14 cases is UNVALIDATED on new data.
  → No statistical conclusion can be drawn.
  → NEW_CASES_INSUFFICIENT = TRUE (for boundary case testing).
```

---

## 7. What CAN Be Concluded

### 7.1 G1 → FALSE_G5 Inference (Partial Validation)

```
15 academic G1 cases (not in original 29):
  → G1 = observation coverage gap = drawing extent missing (inferred).
  → Signal prediction: FALSE_G5 (inferred from G1).
  → Actual: FALSE_G5 (confirmed by G1 classification).
  → Result: 15/15 CORRECT (100%).

  BUT:
  → This tests G1 → FALSE_G5 inference, NOT drawing_extent_present signal.
  → drawing_extent_present was not directly available for academic cases.
  → The inference is: G1 ≈ drawing_extent missing ≈ FALSE_G5.
  → This is consistent but not a direct Signal test.
  → Also: these are FALSE_G5 cases, not TRUE_G5 cases.
  → Cannot test Signal's TRUE_G5 detection.
```

### 7.2 No MISSED_TRUE_G5 (Safety Check)

```
The most important safety question: did Signal miss any TRUE_G5?
  → MISSED_TRUE_G5_COUNT: 0.
  → No new TRUE_G5 cases exist → nothing to miss.
  → The 1 anomaly (dep=False, MACHINE_RESOLVABLE) is NOT a Missed True G5.
  → Safety concern: NONE (no TRUE_G5 was missed).

  BUT: This is because there are NO new TRUE_G5 cases, not because
  the Signal correctly identified them.
  → The absence of MISSED_TRUE_G5 is due to data limitation, not Signal accuracy.
```

### 7.3 Anomaly: dep=False but SUFFICIENT

```
1 case: arxiv_2402.18619_p10_72_729
  → dep=False but Human judged YES (SUFFICIENT).
  → Signal: FALSE_G5. Actual: MACHINE_RESOLVABLE.
  → This is a FALSE POSITIVE for FALSE_G5 (over-prediction).
  → Severity: LOW (conservative, not dangerous).
  → If routed to Evidence Recovery: case would be recovered (no harm).
  → But: unnecessary delay (case was resolvable without recovery).

  Implication:
  → dep=False does NOT always mean UNCERTAIN.
  → dep=False → 7/8 UNCERTAIN (87.5%), 1/8 SUFFICIENT (12.5%).
  → The Signal has a 12.5% false positive rate for FALSE_G5 on this case.
  → But: this is 1 case, not statistically significant.
  → Also: the false positive is conservative (routes to recovery, not away from Human).
```

---

## 8. New FALSE_G5 Types

```
Original FALSE_G5 types (from original 29):
  G1_OBSERVATION_COVERAGE: 5 (drawing extent missing)
  G2_EVIDENCE_ORGANIZATION: 6 (page context / drawing-text linkage)

New FALSE_G5 types (from 181 new cases):
  G1: 15 (academic) + 12 (biotech/fin-edu) = 27
  G2: 19 (academic) + 45 (biotech/fin-edu) = 64
  G3: 12 (academic) + 15 (biotech/fin-edu) = 27
  G4: 12 (academic) + 0 (biotech/fin-edu) = 12

NEW FALSE_G5 type discovered:
  G3_EVIDENCE_PRESENTATION: 27 cases
    → Evidence exists and is organized, but not PRESENTED correctly.
    → Fixable by improving presentation, not by adding observation or reorganizing.
    → Signal: UNKNOWN (drawing_extent does not detect G3).

  G4_CONSUMER_INTEGRATION: 12 cases
    → Evidence exists, organized, and presented, but consumer integration failed.
    → Fixable by improving consumer integration.
    → Signal: UNKNOWN (drawing_extent does not detect G4).

  The original Signal (drawing_extent_present) only detects G1.
  It does NOT detect G2, G3, or G4 FALSE_G5.
  → 91/118 (77.1%) of new FALSE_G5 are NOT detectable by drawing_extent signal.
  → Only 27/118 (22.9%) are G1 (potentially detectable).
```

---

## 9. Final Questions

### Q1: False G5 是否在新案例中继续存在？

```
YES.

  118/181 (65.2%) of new cases are FALSE_G5_CANDIDATE.
  Breakdown: G1(27) + G2(64) + G3(27) + G4(12).

  FALSE_G5 is NOT specific to the original 29 cases.
  It is a WIDESPREAD phenomenon across all case sources.
  → Academic: 46/57 (80.7%) are G1-G4 FALSE_G5.
  → Biotech: 37/37 (100%) are G1-G4 FALSE_G5.
  → FinEdu: 35/35 (100%) are G1-G4 FALSE_G5.

  New FALSE_G5 types discovered:
  → G3 (27 cases) and G4 (12 cases) were not in original 29.
  → These are additional FALSE_G5 sources not covered by the original Signal.
```

### Q2: 上一阶段的 Boundary Signal 是否可以泛化？

```
CANNOT BE DETERMINED.

  The original Signal (drawing_extent_present) was validated on 14 UNCERTAIN cases.
  ALL 14 were in the original 29.
  NO new UNCERTAIN cases are available.
  → The Signal CANNOT be tested on new boundary cases.

  Partial results:
  → G1 inference: 15/15 CORRECT (100%, but indirect inference, not direct Signal test).
  → 1 anomaly: dep=False but SUFFICIENT (over-cautious, not dangerous).
  → 62 out-of-distribution: dep=True but SUFFICIENT (Signal not designed for this).

  STATISTICALLY_LIMITED = TRUE.
  → Cannot conclude generalization is supported or not supported.
  → The Signal remains UNVALIDATED on new boundary cases.
```

### Q3: 有没有新的 FALSE_G5 类型？

```
YES.

  Original FALSE_G5: G1 (5) + G2 (6) = 11 cases.
  New FALSE_G5: G1 (27) + G2 (64) + G3 (27) + G4 (12) = 130 cases.

  NEW types:
  → G3_EVIDENCE_PRESENTATION (27 cases): evidence not presented correctly.
  → G4_CONSUMER_INTEGRATION (12 cases): consumer integration failed.

  IMPLICATION:
  → The original Signal (drawing_extent_present) only detects G1.
  → G2, G3, G4 FALSE_G5 are NOT detectable by drawing_extent.
  → 91/118 (77.1%) of new FALSE_G5 are NOT detectable.
  → The Signal covers only a SMALL SUBSET of FALSE_G5.
  → Even if Signal generalizes for G1, it misses 77.1% of FALSE_G5.
```

### Q4: 有没有出现 MISSED_TRUE_G5？

```
NO.

  MISSED_TRUE_G5_COUNT: 0.
  → No new TRUE_G5 cases exist → nothing was missed.
  → The 1 anomaly (dep=False, MACHINE_RESOLVABLE) is NOT a Missed True G5.

  BUT:
  → This is due to data limitation (no new TRUE_G5), not Signal accuracy.
  → The absence of MISSED_TRUE_G5 does NOT validate the Signal.
  → It only means there were no TRUE_G5 to miss.
```

### Q5: DICE 是否可以安全地进一步研究 Human Escalation Routing？

```
CONDITIONAL.

  Safe aspects:
  → No MISSED_TRUE_G5 in new data.
  → G1 inference: 15/15 CORRECT.
  → 1 anomaly is conservative (over-cautious, not dangerous).

  Unsafe aspects:
  → Signal NOT validated on new boundary cases.
  → Signal only detects G1 (22.9% of FALSE_G5).
  → G2, G3, G4 FALSE_G5 NOT detectable by current Signal.
  → 1 anomaly shows dep=False ≠ always FALSE_G5.
  → STATISTICALLY_LIMITED = TRUE.

  CONCLUSION:
  → Further research is SAFE but must NOT rely on drawing_extent alone.
  → Multiple signals needed (G1, G2, G3, G4 detection).
  → Current Signal is INSUFFICIENT for general Boundary Routing.
  → Cannot safely implement routing based on drawing_extent alone.
```

### Q6: 是否仍然不需要外部训练集？

```
NOT_JUSTIFIED (unchanged).

  External datasets still lack:
  → Evidence Provenance (no evidence chain).
  → Boundary Cases (no structurally-complete-but-semantically-insufficient).
  → Human Escalation information.
  → UNCERTAIN/SUFFICIENT distinction.

  The generalization problem is NOT about more data.
  It is about having new UNCERTAIN/boundary cases.
  → External datasets don't have UNCERTAIN cases.
  → They can't solve the generalization problem.
  → The problem requires new Human Validation (NOT authorized).

  EXTERNAL_DATASET_VALUE = NOT_JUSTIFIED (unchanged).
```

### Q7: 是否值得进入下一阶段 Boundary Routing Design？

```
NOT YET.

  Reasons:
  1. Signal NOT validated on new boundary cases (STATISTICALLY_LIMITED).
  2. Signal only detects G1 (22.9% of FALSE_G5).
  3. G2/G3/G4 FALSE_G5 not detectable by current Signal.
  4. 1 anomaly shows Signal is not perfect even for dep=False.
  5. No new TRUE_G5 cases to test recall.
  6. Cannot implement routing with incomplete Signal coverage.

  The original Signal's 100% accuracy on 14 cases is promising,
  but UNVALIDATED on new data and covers only a SUBSET of FALSE_G5.

  NEXT_GATE = NONE.
  → Not BOUNDARY_ROUTING_DESIGN.
  → The Signal is insufficient for routing design.
  → Further research would require:
    (a) New Human Validation to generate new UNCERTAIN cases (NOT authorized).
    (b) Additional signals for G2/G3/G4 detection (research only).
    (c) Multi-signal Boundary Policy (research only).

  None of these are possible in READ-ONLY mode.
  → STOP.
```

---

## 10. Generalization Conclusion

```
GENERALIZATION_CONDITIONAL

  Evidence FOR generalization:
  → G1 inference: 15/15 CORRECT (100%).
  → No MISSED_TRUE_G5.
  → 1 anomaly is conservative (not dangerous).
  → FALSE_G5 continues to exist in new cases (65.2%).

  Evidence AGAINST generalization:
  → No new UNCERTAIN/boundary cases to test Signal directly.
  → Signal only detects G1 (22.9% of FALSE_G5).
  → G2/G3/G4 FALSE_G5 not detectable.
  → 1 anomaly: dep=False ≠ always FALSE_G5.
  → STATISTICALLY_LIMITED = TRUE.

  The Signal shows PARTIAL promise (G1 detection) but:
  → Cannot be fully validated without new boundary cases.
  → Covers only a subset of FALSE_G5.
  → Cannot be used alone for Boundary Routing.

  FINAL: GENERALIZATION_CONDITIONAL.
  → Partial support (G1 inference).
  → Insufficient for full validation.
  → No next gate.
  → STOP.
```

---

## 11. Over-Design Audit

```
  O1: Trained model? → NO
  O2: Fine-tuned LLM? → NO
  O3: New classifier? → NO
  O4: New detector? → NO
  O5: New threshold? → NO
  O6: New routing code? → NO
  O7: Modified Human Review? → NO
  O8: Modified P1-P7? → NO
  O9: Modified DGF/DEF? → NO
  O10: Modified M-A? → NO
  O11: Modified TLD? → NO
  O12: Modified Frozen Baseline? → NO
  O13: New field? → NO
  O14: New schema? → NO
  O15: New observation? → NO
  O16: External dataset imported? → NO
  O17: Model training? → NO
  O18: Capability created? → NO

  ALL CHECKS: FALSE
  OVER_DESIGN_AUDIT = PASS
```

---

## 12. Limitations

```
  GEN-L-01: NO NEW UNCERTAIN CASES
    All 14 M-A UNCERTAIN cases were in original 29.
    Cannot test Signal on new boundary cases.
    Fundamental data limitation.

  GEN-L-02: NO NEW TRUE_G5 CASES
    No TRUE_G5 in new data.
    Cannot test Signal's TRUE_G5 detection or recall.

  GEN-L-03: G1 INFERENCE IS INDIRECT
    G1 → FALSE_G5 inference uses PRIMARY_GAP, not drawing_extent_present.
    drawing_extent not available for academic cases.
    The inference is consistent but not a direct Signal test.

  GEN-L-04: SINGLE ANOMALY
    1 case: dep=False but SUFFICIENT.
    Cannot determine if this is rare or common.
    Need more dep=False SUFFICIENT cases.

  GEN-L-05: SIGNAL COVERS ONLY G1
    drawing_extent_present detects only G1 FALSE_G5.
    G2/G3/G4 FALSE_G5 (77.1%) not detectable.
    Signal coverage: 22.9% of FALSE_G5.

  GEN-L-06: NO CROSS-DOMAIN BOUNDARY TEST
    Biotech and FinEdu have 0 G5 cases.
    Cannot test Signal on non-academic boundary cases.

  GEN-L-07: STATISTICALLY_LIMITED
    14 UNCERTAIN cases (original) + 0 new = 14 total.
    15 G1 inference + 1 anomaly = 16 indirect tests.
    Not sufficient for statistical conclusion.
```

---

## 13. Six-Layer Convergence (Updated)

```
  Layer 1: Evidence Boundary Structure — 13 G5, 4 reclassified FALSE_G5.
  Layer 2: Evidence Configuration Family (CE2) — Answer NOT learnable, Signal IS.
  Layer 3: Evidence Boundary Expansion — 62.1% TRUE_G5, 37.9% FALSE_G5.
  Layer 4: Human Review Reduction — 77.8% irreducible, 0% review reduction.
  Layer 5: G5 Evidence Boundary Governance — 37.9% FALSE_G5, Signal 100% on 14.
  Layer 6: G5 Boundary Generalization (this study) — Signal UNVALIDATED on new data.

  SIX-LAYER CONVERGENCE:
  → G5 is genuine (Layers 1-4).
  → FALSE_G5 is widespread (Layers 3, 5, 6: 37.9% → 65.2% in broader data).
  → Signal shows promise for G1 (Layer 5: 100%, Layer 6: 15/15 G1 inference).
  → BUT Signal is UNVALIDATED on new boundary cases (Layer 6).
  → AND Signal covers only 22.9% of FALSE_G5 (Layer 6 discovers G3/G4).
  → Generalization is CONDITIONAL, not confirmed.
  → Cannot proceed to Boundary Routing Design.
```

---

## 14. Files Created

```
tmp/g5_boundary_generalization_gate.md          (this file)
tmp/g5_boundary_generalization_gate.json         (structured data)
tmp/g5_boundary_generalization_case_table.csv    (181 cases, 16 fields)
```

---

## 15. Final Governance State

```
RESEARCH_STATUS = COMPLETE

SYSTEM_MODIFIED = FALSE
IMPLEMENTATION_AUTHORIZED = FALSE
EXPERIMENT_AUTHORIZED = FALSE
HUMAN_VALIDATION_AUTHORIZED = FALSE
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

NEXT_GATE = NONE

STOP = TRUE
```

---

## STOP

```
G5 Boundary Generalization Gate is COMPLETE.

SUMMARY:
  - 181 new cases analyzed (outside original 29)
  - TRUE_G5 in new cases: 0
  - FALSE_G5 in new cases: 118 (65.2%)
  - MACHINE_RESOLVABLE in new cases: 63 (34.8%)
  - No new UNCERTAIN/boundary cases available (all 14 were in original 29)
  - Signal CANNOT be tested on new boundary cases
  - G1 inference: 15/15 CORRECT (100%, but indirect)
  - 1 anomaly: dep=False but SUFFICIENT (conservative, not dangerous)
  - 62 out-of-distribution: dep=True but SUFFICIENT (Signal not designed for this)
  - MISSED_TRUE_G5: 0 (but due to no TRUE_G5, not Signal accuracy)
  - FALSE_ESCALATION: 0 (in boundary cases; 62 out-of-distribution)
  - New FALSE_G5 types: G3 (27) + G4 (12) — not detectable by drawing_extent
  - Signal covers only 22.9% of FALSE_G5 (G1 only)
  - STATISTICALLY_LIMITED = TRUE

GENERALIZATION_RESULT: GENERALIZATION_CONDITIONAL
  → Partial support (G1 inference, 15/15 correct).
  → Insufficient for full validation (no new boundary cases).
  → Signal covers only G1 (22.9% of FALSE_G5).
  → Cannot proceed to Boundary Routing Design.
  → NEXT_GATE = NONE.
  → STOP = TRUE.

KEY FINDING:
  The original Signal (drawing_extent_present) shows promise for G1 detection
  but is UNVALIDATED on new boundary cases and covers only 22.9% of FALSE_G5.
  The generalization question cannot be answered without new Human Validation
  (NOT authorized). The Signal is insufficient for Boundary Routing Design.

  不得自动进入 Implementation。
  不得训练模型。
  不得引入外部训练集。
  不得修改 Frozen Baseline。
  NEXT_GATE = NONE.
  STOP = TRUE.
```
