# M-A Human A/B Evidence Sufficiency Pilot — Result Analysis

> **READ-ONLY ANALYSIS / NO MODIFICATION / STOP**
> 日期: 2026-09-18
> N = 24 cases (12 E0, 12 E1), single-human pilot, descriptive comparison only.

---

## 1. Data Integrity Audit

```
DATA INTEGRITY AUDIT: PASS

  Total cases:              24
  Unique case IDs:          24
  Duplicate cases:           0
  E0 arm:                   12
  E1 arm:                   12
  Missing judgments:         0
  Case ID mismatch:          0
  Sampling frame match:    24/24

  Total revision events:   134
  Event log entries:        134
  M5 values:                {NOT_AVAILABLE}

  All 24 cases have complete M1, M2, M3, M4, M6.
  M5 = NOT_AVAILABLE (pre-registered, not analyzed).
  Revision audit trail preserved (134 events).
```

---

## 2. Blinding / Leakage Audit

```
BLINDING / LEAKAGE AUDIT: PASS

  Pack fields:
    case_id, context_text, document_id, evidence_state, extent_bbox,
    page_image, page_image_width, page_image_height, page_reference,
    page_scale, presentation_order, spatial_distance, text_bbox,
    text_content, vertical_ordering

  Forbidden fields in Pack: NONE
  Forbidden fields in results: NONE
  Forbidden visible terms in HTML: NONE

  Non-visible implementation comments:
    JS comments contain "E0"/"E1" (NON_VISIBLE_IMPLEMENTATION_COMMENT)
    These are code comments, NOT visible to Human in rendered UI.
    The "#e0e0e0" in HTML is a CSS hex color, NOT a version label.

  BLINDING_STATUS = PARTIAL
    ✓ No version labels visible
    ✓ No case_type / GT / historical judgment visible
    ✓ No arm / stratum visible
    ✗ Pack content differs (intrinsic, by design)

  No data contamination detected.
  No semantic leakage detected.
```

---

## 3. E0 vs E1 Descriptive Comparison

### M1: Association Judgment (Human Judgment Distribution)

```
  Value       E0 (n=12)    E1 (n=12)    Difference
  ─────────────────────────────────────────────────
  yes              6            5          -1
  no               3            4          +1
  uncertain        3            3           0

  NOTE: This is Human Judgment Distribution, NOT machine accuracy.
  YES rate is NOT accuracy. Negative YES is NOT false positive.
```

### M2: PDF Reopen Required

```
  E0 YES:  1/12  (8.3%)
  E1 YES:  0/12  (0.0%)
  Difference: -1  (-8.3pp)

  E1 eliminated the single PDF reopen case.
  However, E0 already had very low reopen rate (1/12).
  Absolute improvement: small (1 case).
```

### M3: Additional Document Search Required

```
  E0 YES:  7/12  (58.3%)
  E1 YES:  9/12  (75.0%)
  Difference: +2  (+16.7pp)

  E1 INCREASED additional document search rate.
  This is UNEXPECTED and COUNTERINTUITIVE.
  
  Possible interpretation:
    E1 provides more Evidence (context, evidence_state),
    which may make Human MORE aware of what is missing,
    leading to MORE active search for additional context.
    OR: the specific cases in E1 arm happened to require more search.
    
  This does NOT support the hypothesis that E1 reduces search need.
```

### M4: Human Reconstruction Burden

```
  Level    E0    E1    Difference
  ─────────────────────────────────
  L0        0     1      +1
  L1        3     2      -1
  L2        6     7      +1
  L3        0     0       0
  L4        3     2      -1

  L3+L4:   E0=3, E1=2, diff=-1
  L0+L1:   E0=3, E1=3, diff= 0

  E1 reduced L4 by 1 (3→2).
  E1 gained 1 L0 case (0→1).
  But E1 also gained 1 L2 case (6→7) and lost 1 L1 (3→2).
  
  Net: slight reduction in extreme burden (L4: 3→2),
       but no clear overall burden reduction.
  L3 (must open PDF) = 0 in both arms.
```

### M5: Time to Judgment

```
  NOT_AVAILABLE (pre-registered)
  Not analyzed. No time data fabricated.
```

### M6: Evidence Sufficiency

```
  Value           E0    E1    Difference
  ─────────────────────────────────────────
  sufficient       9     9       0
  insufficient     1     0      -1
  uncertain        2     3      +1

  E1 eliminated the 1 INSUFFICIENT case (→ 0).
  But E1 gained 1 UNCERTAIN sufficiency case (2→3).
  SUFFICIENT count unchanged (9→9).
  
  No clear improvement in perceived sufficiency.
```

---

## 4. Summary Table

| Metric | E0 (n=12) | E1 (n=12) | Difference | Interpretation |
|--------|-----------|-----------|------------|----------------|
| M1 YES | 6 | 5 | -1 | descriptive, not accuracy |
| M1 NO | 3 | 4 | +1 | descriptive |
| M1 UNCERTAIN | 3 | 3 | 0 | no change |
| M2 PDF Reopen YES | 1 (8.3%) | 0 (0.0%) | -1 (-8.3pp) | slight improvement |
| M3 Search YES | 7 (58.3%) | 9 (75.0%) | +2 (+16.7pp) | **increased** |
| M4 L0 | 0 | 1 | +1 | slight improvement |
| M4 L1 | 3 | 2 | -1 | slight worsening |
| M4 L2 | 6 | 7 | +1 | slight worsening |
| M4 L3 | 0 | 0 | 0 | unchanged |
| M4 L4 | 3 | 2 | -1 | slight improvement |
| M6 SUFFICIENT | 9 | 9 | 0 | unchanged |
| M6 INSUFFICIENT | 1 | 0 | -1 | slight improvement |
| M6 UNCERTAIN | 2 | 3 | +1 | slight worsening |

---

## 5. UNCERTAIN Analysis

```
  E0 UNCERTAIN: 3 cases
  E1 UNCERTAIN: 3 cases
  Difference: 0 (no change in UNCERTAIN count)

  E0 UNCERTAIN breakdown:
    EVIDENCE_INSUFFICIENT:        1
    POSSIBLE_SEMANTIC_BOUNDARY:   0
    NOT_DETERMINABLE:             2

  E1 UNCERTAIN breakdown:
    EVIDENCE_INSUFFICIENT:        0
    POSSIBLE_SEMANTIC_BOUNDARY:   0
    NOT_DETERMINABLE:             3

  E0 UNCERTAIN cases:
    is11_med_001_p18_325_655:    M4=L4, M6=insufficient  → EVIDENCE_INSUFFICIENT
    is11_med_001_p15_498_107:    M4=L4, M6=uncertain     → NOT_DETERMINABLE
    arxiv_2402.18619_p10_72_729: M4=L4, M6=uncertain     → NOT_DETERMINABLE

  E1 UNCERTAIN cases:
    is11_efficientnet_p2_158_372: M4=L4, M6=uncertain    → NOT_DETERMINABLE
    is11_resnet_p7_321_545:       M4=L4, M6=uncertain    → NOT_DETERMINABLE
    arxiv_2402.18619_p18_346_73:  M4=L2, M6=uncertain    → NOT_DETERMINABLE

  Key observation:
    - UNCERTAIN count unchanged (3→3)
    - E1 eliminated 1 EVIDENCE_INSUFFICIENT (1→0)
    - But E1 gained 1 NOT_DETERMINABLE (2→3)
    - NO POSSIBLE_SEMANTIC_BOUNDARY in either arm
    - All E1 UNCERTAIN cases are NOT_DETERMINABLE (M6=uncertain)
    - 2 of 3 E1 UNCERTAIN cases still have L4 burden

  The UNCERTAIN cases in both arms are predominantly:
    - Type A negatives (no extent on page, DEF=0)
    - Burden L4 (Pack cannot support judgment)
    - This is a GENUINE Evidence gap (no drawing on page), not a Pack design issue
```

---

## 6. Stratified Analysis

### S1_COMPLETE_YES (n=8, E0=4, E1=4) — Regression Test

```
  E0: M1={yes:4}, M4=[1,2,2,2], M6={sufficient:4}, PDF_reopen=0
  E1: M1={yes:4}, M4=[1,1,0,2], M6={sufficient:4}, PDF_reopen=0

  No regression: E1 maintained YES=4/4, SUFFICIENT=4/4.
  Slight burden improvement: E1 has L0=1 (E0 had L0=0).
  E1 arm slightly lower average M4 (1.0 vs 1.75).
  
  REGRESSION_CHECK: NO REGRESSION in S1.
```

### S3_COMPLETE_UNCERTAIN (n=2, E0=1, E1=1) — Semantic Boundary Test

```
  E0 (arxiv_2402.18619_p19_147_496): M1=no, M4=L2, M6=sufficient, PDF_reopen=YES
  E1 (is11_resnet_p4_464_620):       M1=yes, M4=L2, M6=sufficient, PDF_reopen=NO

  E0 case: Human judged NO (was UNCERTAIN in E0 Pilot).
  E1 case: Human judged YES (was UNCERTAIN in E0 Pilot).
  
  These are DIFFERENT cases (parallel split), so cannot directly compare.
  Both resolved from UNCERTAIN to definitive judgment.
  No POSSIBLE_SEMANTIC_BOUNDARY detected.
  
  NOTE: n=1 per arm — cannot draw conclusions.
```

### S4_TYPE_A_NEGATIVE (n=6, E0=3, E1=3) — E1 Improvement Test

```
  E0: M1={uncertain:3},          M4=[4,4,4], M6={insufficient:1, uncertain:2}
  E1: M1={uncertain:2, no:1},    M4=[4,4,2], M6={uncertain:2, sufficient:1}

  E1 results:
    - 1 case resolved to NO (was UNCERTAIN in E0 Pilot)
    - 1 case has L2 burden (E0 all had L4)
    - 1 case reported SUFFICIENT (E0 had 0 SUFFICIENT)
  
  Mixed signal:
    - E1 slightly improved (1 NO, 1 L2, 1 SUFFICIENT)
    - But 2 E1 cases still L4 + UNCERTAIN
    - These L4 cases are pages with NO drawing (DEF=0, PRIMITIVES_NO_EXTENT)
    - No Pack can fix genuine absence of drawing on page
    
  E1 improvement: PARTIAL — helps when extent exists, 
    but cannot help when page genuinely lacks drawing evidence.
```

### S5_TYPE_B_NEGATIVE (n=4, E0=2, E1=2) — E1 Context Fix Test

```
  E0: M1={yes:2},      M4=[1,1], M6={sufficient:2}
  E1: M1={no:1, uncertain:1}, M4=[2,2], M6={sufficient:1, uncertain:1}

  UNEXPECTED: E1 arm shows WORSE outcomes than E0.
    E0: both YES, L1, SUFFICIENT
    E1: 1 NO + 1 UNCERTAIN, both L2, 1 SUFFICIENT + 1 UNCERTAIN
  
  This is COUNTERINTUITIVE — E1 added context, but Human judged
  more conservatively (NO/UNCERTAIN instead of YES).
  
  Possible interpretation:
    - E1's additional context revealed that the text is NOT
      associated with the drawing (more evidence → more conservative)
    - OR: different cases in each arm (parallel split, n=2 per arm)
    - The specific E1 cases may have been harder than E0 cases
    
  CANNOT conclude E1 worsened Type B — n=2 is too small,
  and these are DIFFERENT cases.
```

### S6_NO_JUDGMENT (n=4, E0=2, E1=2) — Leakage Test

```
  E0: M1={no:2}, M4=[2,2], M6={sufficient:2}
  E1: M1={no:2}, M4=[2,2], M6={sufficient:2}

  PERFECT CONSISTENCY: both arms maintain NO judgment.
  No semantic leakage detected.
  E1 did NOT induce YES on cases that were previously NO.
  
  LEAKAGE_CHECK: PASS (0 leakage).
```

---

## 7. Negative Control Analysis

```
  Type A negative (FIG-prefix, not near extent):
    E0 arm (3 cases): UNCERTAIN=3
    E1 arm (3 cases): UNCERTAIN=2, NO=1

  Type B negative (near extent, no FIG-prefix):
    E0 arm (2 cases): YES=2
    E1 arm (2 cases): NO=1, UNCERTAIN=1

  Human Judgment Distribution (NOT machine FPR):
    Type A: E0 100% UNCERTAIN, E1 67% UNCERTAIN + 33% NO
    Type B: E0 100% YES, E1 50% NO + 50% UNCERTAIN

  NOTE:
    - "YES" on a negative control is "Human judged YES", NOT "false positive"
    - This is NOT machine accuracy measurement
    - N=3 and N=2 are too small for any statistical conclusion
    - The Type B difference (E0 YES=2 vs E1 NO/UNCERTAIN) is
      consistent with E1 providing MORE context, leading to
      MORE CONSERVATIVE judgment — but cannot confirm with n=2
```

---

## 8. Consistency Check: Multiple Metrics Convergence

```
  For EVIDENCE_PACK_HUMAN_BENEFIT to be SUPPORTED, we need
  CONVERGENT evidence across M2, M3, M4, M6:

  M2 (PDF Reopen):     E0=8.3% → E1=0.0%   → IMPROVED (slight, -1 case)
  M3 (Doc Search):     E0=58.3% → E1=75.0% → WORSENED (+2 cases)
  M4 (L3+L4 burden):   E0=3 → E1=2         → IMPROVED (slight, -1 case)
  M4 (L0+L1 low burden): E0=3 → E1=3       → UNCHANGED
  M6 (SUFFICIENT):     E0=9 → E1=9         → UNCHANGED
  M6 (INSUFFICIENT):   E0=1 → E1=0         → IMPROVED (slight, -1 case)
  M6 (UNCERTAIN):      E0=2 → E1=3         → WORSENED (+1 case)

  CONVERGENCE ASSESSMENT:
    Improvements: M2 (-1), M4 L4 (-1), M6 INSUFFICIENT (-1)
    Worsening:    M3 (+2), M6 UNCERTAIN (+1)
    Unchanged:    M1 UNCERTAIN (0), M4 L0+L1 (0), M6 SUFFICIENT (0)

  The signals are MIXED and SMALL:
    - 3 slight improvements (1 case each)
    - 1 clear worsening (M3: +2 cases)
    - 1 slight worsening (M6 UNCERTAIN: +1 case)
    - Several unchanged

  NO CONVERGENT improvement pattern.
  The M3 worsening is particularly concerning:
    E1 was supposed to REDUCE document search need,
    but it INCREASED it.
```

---

## 9. Regression Check

```
  E1_REGRESSION = FALSE

  S1 (regression test): NO regression
    E0: YES=4/4, SUFFICIENT=4/4
    E1: YES=4/4, SUFFICIENT=4/4
    E1 maintained all YES judgments on clear positive cases.

  S6 (leakage test): NO regression
    E0: NO=2/2
    E1: NO=2/2
    E1 did NOT induce YES on previously NO cases.

  No systemic regression detected.
  The M3 increase and S5 pattern are NOT regressions —
  they are descriptive differences between different cases
  in parallel split design.
```

---

## 10. Counterfactual vs A/B Relationship

```
  P0 (Counterfactual Diagnostic):
    Proved: E0→E1 Evidence Pack content improved
    Proved: 4 systematic Evidence Gaps resolved
    Proved: Theoretical burden reduction (15/79 cases)
    Method: READ-ONLY reconstruction, not Human judgment
    
  P1 (Human A/B Pilot):
    Tested: Whether REAL Human experiences burden reduction
    Result: MIXED — no convergent improvement signal
    Method: Real Human judgment on 24 cases

  IMPORTANT DISTINCTION:
    P0 proved Evidence Pack CONTENT improved.
    P1 did NOT confirm Human-level burden reduction.
    
    These are NOT contradictory:
    - P0: "The Pack contains more Evidence" (objectively true)
    - P1: "Human perceives less burden" (not confirmed)
    
    Possible explanations:
    1. N=24 is too small to detect the effect
    2. The burden reduction is real but small (1-2 cases)
    3. E1's additional Evidence may increase awareness of
       what's missing, paradoxically increasing search behavior
    4. The parallel split design compares DIFFERENT cases,
       adding noise that masks small effects
    
    CANNOT conclude P0 is wrong.
    CANNOT conclude P1 proves E1 is ineffective.
    Can only say: P1 did not provide convergent evidence
    of Human-level burden reduction.
```

---

## 11. Answers to 8 Research Questions

### Q1: E1 是否减少 PDF Reopen?

```
  YES, but marginally.
  E0: 1/12 (8.3%) → E1: 0/12 (0.0%)
  Difference: -1 case (-8.3pp)
  
  E1 eliminated the single PDF reopen case.
  However, E0 already had very low reopen rate.
  This is a 1-case improvement — not conclusive.
```

### Q2: E1 是否减少 Additional Document Search?

```
  NO. E1 INCREASED search rate.
  E0: 7/12 (58.3%) → E1: 9/12 (75.0%)
  Difference: +2 cases (+16.7pp)
  
  This is the OPPOSITE of the hypothesis.
  E1 did NOT reduce document search need.
  Possible: E1's additional context made Human more aware
  of missing information, increasing search behavior.
```

### Q3: E1 是否降低 Human Reconstruction Burden?

```
  INCONCLUSIVE — mixed signals.
  L4: 3→2 (improved, -1 case)
  L3: 0→0 (unchanged)
  L0+L1: 3→3 (unchanged)
  L2: 6→7 (worsened, +1 case)
  
  No convergent burden reduction pattern.
  The extreme burden (L4) decreased slightly,
  but mid-level burden (L2) increased.
```

### Q4: E1 是否提高 Evidence Sufficiency?

```
  NO clear improvement.
  SUFFICIENT: 9→9 (unchanged)
  INSUFFICIENT: 1→0 (improved, -1 case)
  UNCERTAIN: 2→3 (worsened, +1 case)
  
  E1 eliminated 1 INSUFFICIENT but added 1 UNCERTAIN.
  Net SUFFICIENT count unchanged.
```

### Q5: E1 是否改变 UNCERTAIN 的构成?

```
  UNCERTAIN count unchanged (3→3).
  
  E0: 1 EVIDENCE_INSUFFICIENT + 2 NOT_DETERMINABLE
  E1: 0 EVIDENCE_INSUFFICIENT + 3 NOT_DETERMINABLE
  
  E1 eliminated 1 evidence-insufficient UNCERTAIN,
  but gained 1 not-determinable UNCERTAIN.
  No POSSIBLE_SEMANTIC_BOUNDARY in either arm.
  
  The remaining UNCERTAIN cases are predominantly:
    Type A negatives with DEF=0 (genuine no drawing on page)
    Burden L4 (Pack cannot support judgment)
    These are genuine Evidence gaps, not Pack design failures.
```

### Q6: E1 是否出现明显 Human Judgment Regression?

```
  NO regression detected.
  
  S1 (clear positives): E1 maintained YES=4/4, SUFFICIENT=4/4.
  S6 (NO judgments): E1 maintained NO=2/2.
  
  No systemic judgment flip or degradation.
```

### Q7: 是否发现任何数据污染 / leakage / case mismatch?

```
  NO contamination detected.
  
  Data integrity: PASS (24/24, 0 missing, 0 duplicates)
  Blinding: PASS (no version labels visible)
  Case ID alignment: PERFECT (24/24)
  Semantic leakage: NONE
  Frozen baseline: INTACT (drift=0)
  
  The only non-visible items are JS code comments
  (NON_VISIBLE_IMPLEMENTATION_COMMENT), not Human-facing.
```

### Q8: 综合而言 EVIDENCE_PACK_HUMAN_BENEFIT = ?

```
  INCONCLUSIVE

  Rationale:
    1. No convergent improvement across M2/M3/M4/M6.
       - M2 improved slightly (1 case)
       - M3 worsened (+2 cases) — OPPOSITE of hypothesis
       - M4 mixed (L4 improved, L2 worsened)
       - M6 unchanged (SUFFICIENT 9→9)
    
    2. UNCERTAIN count unchanged (3→3).
       No reduction in uncertainty.
    
    3. The improvements are all 1-case effects (very small).
       The worsening (M3) is 2-case (larger than any improvement).
    
    4. S1 regression test PASSED (no regression).
       S6 leakage test PASSED (no leakage).
       But "no regression" ≠ "improvement".
    
    5. N=24, single-human, parallel split — limited power.
       Small effects may be masked by case-level noise.
    
    6. P0 (Counterfactual) proved Evidence CONTENT improved,
       but P1 (Human A/B) did not confirm Human-level benefit.
       This gap may be due to:
         - Small sample size
         - Parallel split noise (different cases in each arm)
         - E1 increasing search awareness
         - Genuine lack of Human-perceived benefit

  NOT "NOT_SUPPORTED":
    There are SOME positive signals (M2, M4 L4, M6 INSUFFICIENT).
    S4 Type A showed partial improvement.
    No regression or leakage.
    
  NOT "SUPPORTED":
    No convergent improvement.
    M3 worsened significantly.
    SUFFICIENT count unchanged.
    UNCERTAIN count unchanged.
    
  = INCONCLUSIVE
    The pilot did not provide sufficient evidence to conclude
    that E1 reduces Human Reconstruction Burden.
    Further research with larger N needed.
```

---

## 12. Research Limitations

```
  1. SAMPLE SIZE: N=24 (12 per arm)
    - Very small, cannot detect small effects
    - Descriptive comparison only
    - No statistical significance testing
    
  2. SINGLE HUMAN REVIEWER
    - INTER_RATER_RELIABILITY = NOT_AVAILABLE
    - MULTI_HUMAN_GENERALIZATION = NOT_TESTED
    - Single reviewer's behavior may not represent population
    - Same reviewer did E0 Pilot before (secondary carryover risk)
    
  3. PARALLEL SPLIT DESIGN
    - Different cases in each arm
    - Case-level difficulty varies
    - Cannot control for case difficulty differences
    - Adds noise to arm-level comparison
    
  4. M3 COUNTERINTUITIVE RESULT
    - E1 increased document search (+2 cases)
    - This may be a genuine effect or noise
    - Cannot determine with N=12 per arm
    
  5. M5 NOT AVAILABLE
    - No timing data
    - Cannot assess whether E1 made judgment faster
    - Do NOT fabricate or estimate time
    
  6. COGNITIVE LOAD NOT MEASURED
    - No NASA-TLX or workload measure
    - "100% completion" ≠ "low cognitive load"
    - Can only discuss Document Reconstruction Burden
    
  7. GENERALIZATION LIMITS
    - 5 documents only
    - Cannot generalize to all document domains
    - Cannot generalize to production environment
    - Cannot claim causal effect
    
  8. P0 vs P1 GAP
    - P0 (Counterfactual) proved content improvement
    - P1 (Human A/B) did not confirm Human benefit
    - This gap requires further investigation
    - May need larger N or within-subject design
```

---

## 13. Effect Size Summary

```
  All effects are SMALL (1-2 cases out of 12):
  
  Largest improvement: M2 PDF Reopen (-1 case, -8.3pp)
  Largest worsening:  M3 Document Search (+2 cases, +16.7pp)
  
  No effect exceeds 2 cases in magnitude.
  With N=12 per arm, 1-case differences are within noise.
  
  No statistical significance claimed.
  All comparisons are PILOT EVIDENCE only.
```

---

## 14. Final Governance

```
  IMPLEMENTATION_AUTHORIZED = FALSE
  EXPERIMENT_AUTHORIZED = FALSE
  HUMAN_VALIDATION_AUTHORIZED = FALSE
  
  M-A ALGORITHM = UNCHANGED
  EVIDENCE PACK = UNCHANGED
  HUMAN DATA = UNCHANGED (ab_pilot_results.json preserved as-is)
  FROZEN BASELINE = INTACT
  RUNTIME AUTHORITY = ZERO
  PRODUCTION = FALSE
  
  No data modified in this analysis.
  No algorithm modified.
  No Evidence Pack modified.
  No cases modified.
  No Human Validation re-run.
  No thresholds tuned.
  No post-hoc rule changes.
  
  STOP = TRUE
```

---

## 15. Core Principle Adherence

- ✅ READ-ONLY analysis only — no data modified
- ✅ Data integrity verified (24/24, 0 missing, 0 duplicates)
- ✅ Blinding verified (no visible version labels)
- ✅ M1 reported as Human Judgment Distribution, NOT accuracy
- ✅ No FPR or machine accuracy claims
- ✅ Negative control YES = "Human judged YES", NOT "false positive"
- ✅ M5 = NOT_AVAILABLE (not fabricated)
- ✅ No cognitive load claims (no NASA-TLX)
- ✅ No statistical significance claims
- ✅ No causal effect claims
- ✅ No production readiness claims
- ✅ No generalization claims
- ✅ Single-human limitation explicitly stated
- ✅ INTER_RATER_RELIABILITY = NOT_AVAILABLE
- ✅ P0 vs P1 distinction clearly explained
- ✅ Regression check performed (no regression)
- ✅ Leakage check performed (no leakage)
- ✅ Frozen baseline intact (drift=0)
- ✅ All 8 research questions answered
- ✅ Honest reporting of counterintuitive M3 result
- ✅ Did NOT overclaim benefit
- ✅ STOP = TRUE

`STOP = TRUE`.
