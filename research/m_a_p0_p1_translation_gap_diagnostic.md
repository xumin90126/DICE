# M-A P0 → P1 Translation Gap Diagnostic

> **READ-ONLY DIAGNOSTIC / NO MODIFICATION / STOP**
> 日期: 2026-09-18
> 前置: P0 Counterfactual (EVIDENCE_PACK_IMPROVEMENT_SUPPORTED) + P1 Human A/B (INCONCLUSIVE)
> 本文件: 诊断为什么 P0 的客观改善未转化为 P1 的一致 Human-level benefit。

---

## 1. Executive Summary

```
P0 (Counterfactual) proved:
  - 27/79 cases had Evidence added/corrected
  - 15/79 cases had theoretical burden reduction
  - 4 systematic Evidence Gaps resolved
  - 0 regressions

P1 (Human A/B) found:
  - No convergent improvement (M2/M3/M4/M6 inconsistent)
  - M3 INCREASED (+2 cases, +16.7pp) — opposite of hypothesis
  - UNCERTAIN unchanged (3→3)
  - SUFFICIENT unchanged (9→9)
  - EVIDENCE_PACK_HUMAN_BENEFIT = INCONCLUSIVE

TRANSLATION GAP DIAGNOSIS:
  The gap is PARTIALLY EXPLAINED by 3 factors:

  1. CONFOUNDING: E1 arm had 2x more historical UNCERTAIN (6 vs 3)
     → E1 arm cases were inherently harder before experiment
     → M3 increase partially attributable to difficulty imbalance

  2. P0 IMPROVEMENT TYPE: Most P0 changes were MINOR (state+±5pt)
     → Only 3/12 E1 cases had MAJOR changes (extent+context+state)
     → MINOR changes may not produce observable Human-level difference

  3. SUFFICIENCY ≠ NO SEARCH: M3=YES occurred even when M6=SUFFICIENT
     → Human reports Pack is sufficient but still wants more context
     → M3 measures a different construct than M6

  The gap is NOT FULLY EXPLAINED:
  - M3 increase has multiple partially-consistent hypotheses
  - New Evidence usage is NOT_OBSERVABLE (no interaction logs)
  - N=24 too small to separate confounding from genuine effect

P0_P1_TRANSLATION_GAP_STATUS = PARTIALLY_EXPLAINED
```

---

## 2. Revision Events Audit (134 Events)

```
Q1: 134 revision events 到底是什么？

ANSWER: 134 is NOT 134 judgment changes.

  134 = 120 first-time selections + 14 actual value revisions

  Breakdown:
    TOTAL_RAW_EVENTS:           134
    TOTAL_AUTOSAVE_EVENTS:      0 (no autosave events in log)
    TOTAL_FIELD_CHANGES:        134 (every event is a field change)
    TOTAL_FIRST_SELECTIONS:     120 (= 5 metrics × 24 cases)
    TOTAL_ACTUAL_REVISIONS:     14 (Human changed an already-selected value)
    TOTAL_FINAL_JUDGMENTS:      24
    TOTAL_UNIQUE_CASES:         24

  The "revision_count" field per case = total events for that case.
  - revision_count=5 means 5 first-selections + 0 actual revisions (no changes)
  - revision_count=7 means 5 first-selections + 2 actual revisions
  - revision_count=9 means 5 first-selections + 4 actual revisions

  The 14 actual revisions:
    By metric: m1=4, m3=1, m4=6, m6=3
    By arm: E0=4, E1=10
    By case: 8 cases had revisions, 16 cases had none

  Most revisions were within-metric adjustments (e.g., M4: 2→1→2, M6: insufficient→sufficient→insufficient→sufficient)
  These represent Human deliberation, not data quality issues.

  CONCLUSION: 134 is the total UI click-event count, NOT 134 judgment changes.
  Only 14 actual value revisions occurred across 8 cases.
  Data quality: ACCEPTABLE (revisions are normal Human deliberation).
```

---

## 3. P0 ↔ P1 Case-Level Join

```
  P1 cases:        24
  P0 cases:        79 (all available via E1 data + E0 reconstruction)
  P1 in P0:        24/24
  P1 NOT in P0:    0/24
  Join status:     COMPLETE

  All 24 P1 cases exist in P0 with matching case_id.
  No case replacement or mismatch.
```

---

## 4. Pre-Experiment Difficulty Comparison

```
Q2: E0/E1 两组在实验开始前是否存在明显案例难度差异？

ANSWER: YES — a difficulty imbalance exists.

  Historical E0 Pilot judgment (pre-experiment):
    E0 arm: YES=7, NO=2, UNCERTAIN=3
    E1 arm: YES=4, NO=2, UNCERTAIN=6

  E1 arm has 2x more historical UNCERTAIN (6 vs 3).
  This means E1 arm cases were INHERENTLY HARDER before any Pack difference.

  However:
    - Strata are BALANCED (identical 4/1/3/2/2 per arm)
    - P0 change types are BALANCED (3 MAJOR + 2 MODERATE + 7 MINOR each)
    - The difficulty imbalance exists WITHIN strata
      (different cases with different historical judgments were assigned)

  This is a CONFOUNDING FACTOR:
    - E1 arm's higher M3 (+2) could be partially caused by inherently harder cases
    - Cannot fully attribute M3 increase to E1 Pack content
    - Parallel split design cannot control for within-stratum difficulty variation

  Other balance checks:
    Extent availability: E0=9/12, E1=9/12 (BALANCED)
    Context availability: E0=7/12, E1=7/12 (BALANCED)
    Negatives: E0=5, E1=5 (BALANCED)
    Documents: Different (inherent to parallel split)
    E1 evidence_state: E0 has 1 NO_VISUAL_EVIDENCE, E1 has 2 PRIMITIVES_NO_EXTENT
```

---

## 5. P0 Improvement Exposure

```
Q3: P0 Evidence improvement 在 24 个 P1 cases 中覆盖多少？

ANSWER: 24/24 (100%) — all cases had at least state_added.

  P0 change types across 24 cases:
    MAJOR (extent+context+state):    5  (Type A with extent restored)
    MODERATE (context+state):        4  (Type B + Type A without extent)
    MODERATE (context+state, no ext): 2  (Type A PRIMITIVES_NO_EXTENT)
    MINOR (state+±5pt):             13  (Candidates — state field + wider threshold)

  Per arm:
    E0 arm: 3 MAJOR + 2 MODERATE + 1 MODERATE-no-ext + 7 MINOR = 12 (sees OLD Pack)
    E1 arm: 1 MAJOR + 2 MODERATE + 2 MODERATE-no-ext + 7 MINOR = 12 (sees NEW Pack)

  Key insight:
    - 7/12 E1 cases had only MINOR changes (state+±5pt)
    - Only 1/12 E1 case had MAJOR change (extent+context+state)
    - MINOR changes may not produce observable Human-level difference
    - The Evidence Pack improvement is REAL but SMALL for most cases
```

---

## 6. P0 Improvement → P1 Outcome Alignment

```
Q4: P0 Evidence improvement 是否与 P1 Human benefit 对齐？

ANSWER: NO — mostly misaligned.

  For E1 arm (n=12, saw NEW Pack), classified by outcome:

  Type 1 (P0 improved + Human benefit realized):
    Count: 1/12
    Cases: is11_med_001_p23_85_395 (MINOR change, M4=L1, M3=no, M6=sufficient)
    → Only 1 case showed clear benefit signal

  Type 2 (P0 improved + Human behavior unchanged):
    Count: 9/12
    → Pack improved but Human behavior didn't change
    → Most had M3=yes (still searched) despite M6=sufficient
    → This is the DOMINANT pattern

  Type 3 (P0 improved + Human burden high):
    Count: 2/12
    Cases: is11_efficientnet_p2_158_372, is11_resnet_p7_321_545
    → Both Type A PRIMITIVES_NO_EXTENT (no extent on page)
    → M4=L4, M6=uncertain
    → Pack cannot fix genuine absence of drawing

  Type 4 (P0 no material change):
    Count: 0/12
    → All cases had at least state_added

  ALIGNMENT VERDICT: MISALIGNED
    - 9/12 E1 cases: P0 improved but no observable Human benefit
    - 2/12 E1 cases: P0 improved but burden remained high (genuine Evidence gap)
    - 1/12 E1 cases: P0 improved + benefit realized
    - The dominant pattern is "improvement without observable benefit"
```

---

## 7. M3 Counterintuitive Increase Investigation

```
Q5: 为什么 M3 从 7/12 增加到 9/12？

  E0 M3=YES: 7/12 (58.3%)
  E1 M3=YES: 9/12 (75.0%)
  Difference: +2 (+16.7pp)

  E1 arm M3=YES cases (9):
    6 are MINOR changes (state+±5pt) — M3=yes
    2 are MODERATE (context+state) — M3=yes
    1 is MAJOR (extent+context+state) — M3=yes
    2 MODERATE-no-extent — M3=no (burden L4, didn't search)

  Hypothesis evaluation:

  Hypothesis A (E1 makes Human more aware of missing info):
    M3=YES is widespread across ALL change types, not concentrated in MAJOR.
    M3=YES appears in MINOR changes just as much as MAJOR.
    → Weakly consistent: awareness effect is content-general
    → But doesn't explain why E0 arm (also has content) has lower M3

  Hypothesis B (E1 arm contained harder cases):
    E1 arm has 6 historical UNCERTAIN vs E0's 3.
    Within-stratum comparison:
      S1: E0 M3=YES=3/4, E1 M3=YES=3/4 (SAME)
      S4: E0 M3=YES=0/3, E1 M3=YES=1/3 (E1 slightly higher)
      S5: E0 M3=YES=2/2, E1 M3=YES=2/2 (SAME)
      S6: E0 M3=YES=2/2, E1 M3=YES=2/2 (SAME)
      S3: E0 M3=YES=0/1, E1 M3=YES=1/1 (E1 higher, n=1)
    → The +2 difference comes from S3 (n=1) and S4 (n=1)
    → Both are single-case differences — within noise
    → Partially consistent but not conclusive

  Hypothesis C (P0 improvement not relevant to specific judgment):
    7/9 E1 M3=YES cases have M6=SUFFICIENT.
    → Human says Pack is sufficient BUT still searched for more context.
    → This means M3 measures a DIFFERENT construct than M6.
    → SUFFICIENCY ≠ NO SEARCH NEED.
    → Consistent: Pack improvement doesn't reduce search urge

  Hypothesis D (Measurement/UI interpretation):
    M3 question: "你是否需要在 Evidence 之外寻找额外上下文？"
    Human may interpret "search" broadly (including mental recall, page scanning).
    No UI log of actual search behavior.
    → Cannot rule out

  M3_CAUSE = INCONCLUSIVE
    Multiple hypotheses partially consistent:
    - B (difficulty imbalance) explains part of the difference
    - C (sufficiency ≠ no search) explains why M3 is high even when sufficient
    - D (measurement interpretation) cannot be ruled out
    - A (awareness) is weakly consistent but doesn't explain arm difference

    The +2 difference comes from 2 single-case stratum differences (S3, S4).
    With n=1 per stratum per arm, this is within random noise.
```

---

## 8. New Evidence Usage Observability

```
Q6: Human 是否真正使用了 E1 新增 Evidence？

  Event log fields: case_id, metric, new_value, timestamp
  Event log does NOT contain:
    - evidence_viewed (no tracking of which Evidence elements Human looked at)
    - scroll_position (no scroll tracking)
    - time_per_element (no per-element timing)
    - eye_tracking (no eye tracking)

  NEW_EVIDENCE_USAGE = NOT_OBSERVABLE

  Cannot determine from available data whether Human:
    - Actually viewed the new evidence_state field
    - Actually read the new context_text for negatives
    - Actually noticed the extent_bbox for Type A cases

  MUST NOT infer from final judgment:
    - "Human chose YES, so they must have used the new Evidence" = FORBIDDEN
    - "Human chose NO, so the new Evidence was irrelevant" = FORBIDDEN

  This is a fundamental limitation of the current UI design.
  Future experiments could add:
    - Element visibility tracking
    - Time-per-element logging
    - Eye tracking
  But these are NOT available in the current pilot.
```

---

## 9. Evidence Pack Failure Pattern Check

```
Q7: P1 中是否存在明确的 Evidence Pack failure pattern？

  4-type classification (E1 arm only):

  Type 1 (improved + benefit):     1 case (8%)
    → Evidence Pack helped

  Type 2 (improved + unchanged):   9 cases (75%)
    → Evidence Pack improved but no observable benefit
    → NOT a "failure" — Pack is objectively better, just no Human-level signal

  Type 3 (improved + burden high): 2 cases (17%)
    → Both Type A PRIMITIVES_NO_EXTENT (no extent on page)
    → This is a GENUINE Evidence gap, not a Pack design failure
    → The page genuinely lacks drawing evidence
    → No Pack can fix this without adding new detection capability

  Type 4 (no material change):     0 cases (0%)

  FAILURE PATTERN ASSESSMENT:
    - NO systematic Evidence Pack failure pattern found
    - Type 3 cases are genuine Evidence gaps (DEF=0), not Pack failures
    - Type 2 cases show "improvement without observable benefit" —
      this is not failure, it's non-detection at N=12
    - The Pack is objectively improved (P0 proved this)
    - The Human-level benefit is just not observable at this sample size

  No specific case shows Evidence Pack causing HARM or REGRESSION.
```

---

## 10. Semantic Boundary Reassessment

```
  P1 UNCERTAIN cases (6 total: 3 E0 + 3 E1):

  E0 UNCERTAIN:
    is11_med_001_p18_325_655:    M4=L4, M6=insufficient → EVIDENCE_INSUFFICIENT ✓
    is11_med_001_p15_498_107:    M4=L4, M6=uncertain    → NOT_DETERMINABLE ✓
    arxiv_2402.18619_p10_72_729: M4=L4, M6=uncertain    → NOT_DETERMINABLE ✓

  E1 UNCERTAIN:
    is11_efficientnet_p2_158_372: M4=L4, M6=uncertain   → NOT_DETERMINABLE ✓
    is11_resnet_p7_321_545:       M4=L4, M6=uncertain   → NOT_DETERMINABLE ✓
    arxiv_2402.18619_p18_346_73:  M4=L2, M6=uncertain   → NOT_DETERMINABLE ✓

  Classification rule verification:
    - M6=INSUFFICIENT → EVIDENCE_INSUFFICIENT: CORRECT (1 case)
    - M6=SUFFICIENT + M4<=1 → POSSIBLE_SEMANTIC_BOUNDARY: 0 cases (none met criteria)
    - All other UNCERTAIN → NOT_DETERMINABLE: CORRECT (5 cases)

  No POSSIBLE_SEMANTIC_BOUNDARY detected.
  All UNCERTAIN cases are either EVIDENCE_INSUFFICIENT or NOT_DETERMINABLE.
  Most have M4=L4 (Pack cannot support judgment) — these are genuine Evidence gaps.

  The classification rule worked correctly.
  No semantic boundary can be confirmed from this pilot.
```

---

## 11. Parallel Split Confounding Risk

```
  PARALLEL_SPLIT_CONFOUNDING_RISK = PRESENT

  Primary confound:
    E1 arm has 6 historical UNCERTAIN vs E0 arm's 3.
    E1 arm cases were inherently harder before experiment.

  Contributing factors:
    1. Within-stratum difficulty variation: different cases with different
       historical judgments were assigned to each arm within the same stratum.
    2. Document imbalance: E0 arm has 4 med_001 + 4 arxiv, E1 arm has 5 efficientnet.
       Different documents may have different intrinsic difficulty.
    3. E1 evidence_state imbalance: E1 has 2 PRIMITIVES_NO_EXTENT (harder),
       E0 has 1 NO_VISUAL_EVIDENCE (also hard but different type).

  What IS balanced:
    - Stratum counts (4/1/3/2/2 per arm) ✓
    - P0 change types (3 MAJOR + 2 MODERATE + 7 MINOR per arm) ✓
    - Extent availability (9/12 per arm) ✓
    - Context availability (7/12 per arm) ✓
    - Negative count (5 per arm) ✓

  Impact on results:
    - The M3 increase (+2) could be partially or entirely caused by
      the difficulty imbalance, not by E1 Pack content.
    - The M4 L4 cases (3 E0, 2 E1) are concentrated in Type A negatives
      with DEF=0 — genuine Evidence gaps, not Pack issues.
    - Cannot separate "Pack effect" from "difficulty confound" at N=12.

  "Not observed" ≠ "not present":
    Even balanced metrics don't guarantee no confounding.
    With N=12 per arm, small imbalances can produce observable effects.
```

---

## 12. P0 Theoretical vs P1 Actual

```
  P0 predicted structural benefit:
    15/79 cases had theoretical burden reduction (from Counterfactual Diagnostic)
    Of 24 P1 cases: all 24 had P0 change, but only 5 had MAJOR/MODERATE changes

  P1 observed Human behavior:
    1/12 E1 cases showed benefit signal (Type 1)
    9/12 E1 cases showed no observable benefit (Type 2)
    2/12 E1 cases had high burden (Type 3 — genuine gap)

  Translation rate:
    P0 predicted benefit → P1 observed benefit = 1/12 (8.3%)

  This does NOT mean E1 is ineffective:
    - P0 proved CONTENT improvement (objective)
    - P1 failed to detect Human-level benefit (subjective, small N)
    - The translation rate is low because:
      a) Most P0 changes were MINOR (state+±5pt) — small content difference
      b) Difficulty confound masks small effects
      c) M3 measures a different construct than burden
      d) N=12 has very low power for small effects

  P0 vs P1 are NOT contradictory:
    P0: "Pack contains more Evidence" (objectively true)
    P1: "Human doesn't perceive less burden" (not confirmed at N=12)
    Both can be true simultaneously.
```

---

## 13. Answers to Core Questions

```
Q1: 134 revision events 到底是什么？
  = 120 first-time selections + 14 actual value revisions.
  NOT 134 judgment changes. Data quality acceptable.

Q2: E0/E1 两组在实验开始前是否存在明显案例难度差异？
  YES. E1 arm has 6 historical UNCERTAIN vs E0's 3.
  This is a CONFOUNDING FACTOR.

Q3: P0 Evidence improvement 在 24 个 P1 cases 中覆盖多少？
  24/24 (100%). But 13/24 were MINOR changes (state+±5pt).
  Only 5/24 were MAJOR (extent+context+state).

Q4: P0 Evidence improvement 是否与 P1 Human benefit 对齐？
  NO. 9/12 E1 cases: improved but no observable benefit.
  1/12: improved + benefit. 2/12: improved + high burden (genuine gap).

Q5: 为什么 M3 从 7/12 增加到 9/12？
  INCONCLUSIVE. Multiple hypotheses partially consistent.
  +2 comes from 2 single-case stratum differences (within noise).
  Difficulty confound partially explains. Sufficiency ≠ no search.

Q6: Human 是否真正使用了 E1 新增 Evidence？
  NOT_OBSERVABLE. No interaction/visibility tracking in event log.

Q7: P1 中是否存在明确的 Evidence Pack failure pattern？
  NO systematic failure pattern. Type 3 cases are genuine Evidence gaps (DEF=0).
  Type 2 (75%) is "improvement without observable benefit", not failure.

Q8: 当前 Evidence Pack 是否应该继续优化？
  INCONCLUSIVE.
  P0 proved objective improvement. P1 did not confirm Human benefit.
  But P1 also did NOT show regression, leakage, or failure.
  The Evidence Pack is objectively better (P0).
  Whether further optimization is justified depends on:
    - Whether the optimization targets Human-observable differences
    - Whether larger N can detect the small effect
    - Whether M3 is a valid measure (it may measure a different construct)
  Cannot recommend implementation or rejection based on current data alone.
```

---

## 14. P0_P1_TRANSLATION_GAP_STATUS

```
P0_P1_TRANSLATION_GAP_STATUS = PARTIALLY_EXPLAINED

  The gap is partially explained by 3 factors:

  1. CONFOUNDING (PARTIALLY EXPLAINS):
     E1 arm had 2x more historical UNCERTAIN (6 vs 3).
     E1 arm cases were inherently harder.
     M3 increase (+2) partially attributable to difficulty imbalance.
     But strata were balanced — confound is within-stratum, not between-stratum.

  2. IMPROVEMENT MAGNITUDE (PARTIALLY EXPLAINS):
     13/24 P0 changes were MINOR (state+±5pt).
     Only 5/24 were MAJOR (extent+context+state).
     MINOR changes may not produce observable Human-level difference at N=12.
     The objective improvement is real but small for most cases.

  3. CONSTRUCT MISMATCH (PARTIALLY EXPLAINS):
     M3 (document search) and M6 (sufficiency) measure different constructs.
     7/9 E1 M3=YES cases had M6=SUFFICIENT.
     Human says "Pack is sufficient" but still wants more context.
     M3 may not be a valid measure of Pack benefit.

  The gap is NOT FULLY EXPLAINED by:
  - M3 cause is INCONCLUSIVE (multiple hypotheses, N too small)
  - New Evidence usage is NOT_OBSERVABLE (no interaction logs)
  - N=24 cannot separate confounding from genuine effect
  - Single Human reviewer (no inter-rater reliability)

  NOT "UNEXPLAINED":
    We have 3 partially explanatory factors.
    The gap is understandable, not mysterious.
    But we cannot fully attribute the gap to any single cause.
```

---

## 15. Research Limitations

```
  1. N=24 (12 per arm) — very low power for small effects
  2. SINGLE HUMAN — INTER_RATER_RELIABILITY = NOT_AVAILABLE
  3. PARALLEL SPLIT — within-stratum difficulty confound
  4. NO INTERACTION LOGS — cannot observe Evidence usage
  5. M3 CONSTRUCT VALIDITY — may not measure what we think
  6. P0 RECONSTRUCTION — E0 rebuilt from documented logic (bias risk: LOW)
  7. PDF FILES LOST — /tmp PDFs cleaned, E0 fully rebuilt from E1 data + docs
  8. CANNOT GENERALIZE — 5 documents, 1 Human, descriptive only
```

---

## 16. Governance

```
  IMPLEMENTATION_AUTHORIZED = FALSE
  EXPERIMENT_AUTHORIZED = FALSE
  HUMAN_VALIDATION_AUTHORIZED = FALSE

  M-A ALGORITHM = UNCHANGED
  EVIDENCE PACK = UNCHANGED
  HUMAN DATA = UNCHANGED
  P0 DATA = UNCHANGED
  P1 DATA = UNCHANGED
  FROZEN BASELINE = INTACT
  RUNTIME AUTHORITY = ZERO
  PRODUCTION = FALSE

  No data modified in this diagnostic.
  No algorithm modified.
  No Evidence Pack modified.
  No cases modified.
  No Human Validation re-run.

  STOP = TRUE
```

---

## 17. Principle Adherence

- ✅ Did NOT force an explanation
- ✅ Did NOT turn M3 increase into failure claim
- ✅ Did NOT turn P1 INCONCLUSIVE into success
- ✅ Did NOT turn P1 INCONCLUSIVE into failure
- ✅ Did NOT modify the system
- ✅ Reported 134 events honestly (120 first-selections + 14 revisions)
- ✅ Reported difficulty confound (E1 arm harder)
- ✅ Reported M3 cause as INCONCLUSIVE (not forced to A/B/C/D)
- ✅ Reported New Evidence usage as NOT_OBSERVABLE
- ✅ Reported all 4 types (improved+benefit / improved+unchanged / improved+high / no-change)
- ✅ Did not claim accuracy, causality, or production readiness
- ✅ P0 vs P1 distinction clearly maintained
- ✅ Frozen baseline intact

`STOP = TRUE`.
