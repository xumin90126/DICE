# AO Visual Geometry Value Experiment

> **模式: EXPERIMENT COMPLETE / READ-ONLY ANALYSIS / FROZEN BASELINE INTACT / STOP**
> 日期: 2026-09-17
> 授权: EXPERIMENT = AUTHORIZED (scope = value assessment only, no algorithm modification)

---

## 1. Experiment Question

> 加入 AO Visual Geometry Evidence 后，是否能够显著增加对真实文档失败案例的解释能力，并发现原来不可见的高价值问题？

核心链路：

```
真实文档 → Existing Evidence → Failure Case → AO Visual Geometry Evidence
→ Failure Explanation 是否增加？ → Problem Value 是否增加？
```

本实验不是 Figure/Caption/Chart Detection benchmark。只测 Explanation Gain。

---

## 2. Existing Failure Case Selection

### 来源

```
IS-11 Semantic Ground Truth (FROZEN, 45 cases, 2 MERGE):
  - 2 MERGE cases (M-A caption association) — med_001 p20, p24
  - 4 ADJUDICATED cases (ambiguous boundaries)
  - 39 KEEP_SEPARATE cases (table text / prose boundaries)

P7 Evidence Gap Analysis:
  - arxiv_2402.18619 p28 (216 vector primitives, 0 NTB — visual content skipped)

Selection criteria (WITHOUT looking at vector geometry — avoid selection bias):
  - Group 1 (visual_relevance_positive): known MERGE + known visual-skipped
  - Group 2 (visual_relevance_marginal): adjudicated ambiguous
  - Group 3 (negative_control): table text boundary (short numeric text)
```

### Corpus restoration

IS-11 corpus PDFs were deleted from `/tmp` (temporary storage). Re-downloaded from arxiv.org (public open access) using the same arxiv IDs from `is11_corpus_acquisition_report.md`. SHA-256 verified: med_001, resnet_001, cs_001 all match frozen corpus hashes. This is corpus restoration, NOT new corpus creation.

---

## 3. Case Set

```
VISUAL_VALUE_CASE_SET: 13 cases

Group 1 — visual_relevance_positive (3 cases):
  IS11-AMB-414:  med_001 p20, MERGE, "FIG. 9:" + "Left:"
  IS11-AMB-422:  med_001 p24, MERGE, "FIG. 12:" + "Distribution..."
  EXT-ARXIV2402-P28: arxiv_2402 p28, VISUAL_CONTENT_SKIPPED, "Fig. 14"

Group 2 — visual_relevance_marginal (4 cases):
  IS11-AMB-005:  resnet p1, ADJUDICATED, prose boundary
  IS11-AMB-375:  med_001 p6, ADJUDICATED, reference + text
  IS11-AMB-418:  med_001 p20, ADJUDICATED, near figure context
  IS11-AMB-519:  cs_001 p3, ADJUDICATED, prose boundary

Group 3 — negative_control (6 cases):
  IS11-AMB-024:  resnet p6, TABLE_TEXT, "28.54" vs "10.02"
  IS11-AMB-032:  resnet p6, TABLE_TEXT, "-" vs "8.43"
  IS11-AMB-034:  resnet p6, TABLE_TEXT, "21.59" vs "5.71"
  IS11-AMB-052:  resnet p7, TABLE_TEXT, "0.46M" vs "7.51"
  IS11-AMB-064:  resnet p8, TABLE_TEXT, "training data" vs "07+12"
  IS11-AMB-074:  resnet p8, TABLE_TEXT, "41.5" vs "21.2"
```

SAMPLE_SIZE_LIMITATION = TRUE (13 cases, small sample — no significance testing)

---

## 4. E0 — Existing Evidence

### E0 Classification Distribution

```
EXPLAINABLE:            6  (all negative controls — table text boundary)
PARTIALLY_EXPLAINABLE:  6  (2 MERGE + 4 adjudicated)
NOT_EXPLAINABLE:        1  (arxiv_2402 p28 — visual content skipped)
```

### Key E0 Findings

```
MERGE cases (AMB-414, AMB-422):
  E0 = PARTIALLY_EXPLAINABLE
  P2 geometry (same_y_band, h_gap) can show text proximity between "FIG. 9:" and "Left:"
  BUT: P2 cannot determine if text is near a figure
  → Missing dimension: "is there visual content near this text?"
  → NTB = 0 (raster), no vector drawing evidence
  → E0 cannot answer: "why should these be merged? because they are caption of a figure"

VISUAL_CONTENT_SKIPPED (EXT-ARXIV2402-P28):
  E0 = NOT_EXPLAINABLE
  630 P1 text atoms, 0 NTB, no visual evidence
  P7 evidence gap: 216 vector primitives completely invisible
  → E0 cannot even observe that visual content exists on this page

NEGATIVE_CONTROLS (6 table text cases):
  E0 = EXPLAINABLE
  P2 geometry fully explains table text boundary
  → No visual evidence needed
```

---

## 5. E1 — Existing + Vector Geometry

### E1 Classification Distribution

```
NEW_DIAGNOSTIC_EVIDENCE:    3  (2 MERGE + 1 visual-skipped)
NEW_SUPPORTING_EVIDENCE:   9  (4 adjudicated + 5 negative controls)
NO_NEW_EVIDENCE:           1  (1 negative control — no extent on page)
```

### Key E1 Findings

```
MERGE cases (AMB-414, AMB-422):
  E1 = NEW_DIAGNOSTIC_EVIDENCE

  AMB-414 (med_001 p20):
    DRAWING_GEOMETRY_FACT: 235 primitives
    DRAWING_EXTENT_FACT: 1 extent, bbox=[88.45,127.28,526.03,305.95], 16 primitives, area=78181
    text_a "FIG. 9:" is 34.5pt below the drawing extent
    → NEW: "text is near a drawing extent" — previously invisible fact
    → This is the missing dimension for caption association

  AMB-422 (med_001 p24):
    DRAWING_GEOMETRY_FACT: 635 primitives
    DRAWING_EXTENT_FACT: 1 extent, bbox=[176.83,144.96,469.99,517.0], 2 primitives, area=109066
    text_a "FIG. 12:" is 54.8pt below the drawing extent
    → NEW: "text is near a drawing extent" — previously invisible fact

VISUAL_CONTENT_SKIPPED (EXT-ARXIV2402-P28):
  E1 = NEW_DIAGNOSTIC_EVIDENCE
    DRAWING_GEOMETRY_FACT: 216 primitives (was 0 in E0)
    DRAWING_EXTENT_FACT: 1 extent, bbox=[123.73,77.15,503.18,178.35], 12 primitives
    text_a "Fig. 14" is 17.2pt below the drawing extent
    → NEW: "216 vector primitives now observable" — was completely invisible in E0

ADJUDICATED cases (4):
  E1 = NEW_SUPPORTING_EVIDENCE
  Drawings exist on page but don't directly resolve the ambiguity
  → Supporting but not diagnostic

NEGATIVE_CONTROLS (6):
  E1 = NEW_SUPPORTING_EVIDENCE (5) / NO_NEW_EVIDENCE (1)
  Drawings exist on some pages but are NOT diagnostic for table text boundary
  → Correctly NOT elevated to diagnostic
```

---

## 6. Explanation Gain

```
EXPLANATION_GAIN:

  NOT_EXPLAINABLE → NEW_DIAGNOSTIC:    1 case (EXT-ARXIV2402-P28)
  PARTIALLY_EXPLAINABLE → NEW_DIAGNOSTIC: 2 cases (AMB-414, AMB-422)
  Total diagnostic gain:               3 cases (out of 13)

  No case went from EXPLAINABLE to NEW_DIAGNOSTIC (correct — negative controls stayed non-diagnostic)
```

### What was newly explainable?

```
1. AMB-414 (med_001 p20, MERGE):
   E0: "P2 shows text proximity, but cannot determine if text is near a figure"
   E1: "Drawing extent [88.45,127.28,526.03,305.95] exists, text_a is 34.5pt below it"
   → The missing dimension "is there visual content near this text?" is NOW answerable

2. AMB-422 (med_001 p24, MERGE):
   E0: "P2 shows text proximity, but cannot determine if text is near a figure"
   E1: "Drawing extent [176.83,144.96,469.99,517.0] exists, text_a is 54.8pt below it"
   → The missing dimension is NOW answerable

3. EXT-ARXIV2402-P28 (arxiv_2402 p28, visual skipped):
   E0: "216 vector primitives skipped, 0 NTB, no visual evidence"
   E1: "216 primitives observable, 1 extent aggregated, text near extent"
   → The visual content is NOW observable
```

---

## 7. Failure Localization Gain

```
FAILURE_LOCALIZATION_GAIN:

  NEWLY_LOCALIZED:  3 cases (AMB-414, AMB-422, EXT-ARXIV2402-P28)
  UNCHANGED:       10 cases

Localization shift:
  AMB-414: E0="Evidence Representation Gap (visual missing)" → E1="Evidence Organization Gap (proximity + prefix available, needs hypothesis)"
  AMB-422: E0="Evidence Representation Gap (visual missing)" → E1="Evidence Organization Gap (proximity + prefix available, needs hypothesis)"
  EXT-ARXIV2402-P28: E0="Perception Missing (vector skipped)" → E1="Evidence Representation Gap resolved; now Evidence Organization Gap"
```

### What shifted?

```
Before (E0):
  "We cannot observe visual content" → failure localized as Perception Missing / Representation Gap

After (E1):
  "We CAN observe visual content (drawing extent + text proximity)"
  → failure shifts from "Perception Missing" to "Evidence Organization Gap"
  → the problem is no longer "we can't see it" but "we can see it but need to organize/interpret"

This is a meaningful localization shift:
  Perception Missing → Evidence Organization Gap
  (harder problem) → (more tractable problem)
```

---

## 8. Problem Value Gain

```
PROBLEM_VALUE_GAIN:

  HIGH_VALUE_CASE_GAIN:     3 cases (AMB-414, AMB-422, EXT-ARXIV2402-P28)
    → These cases went from "ambiguous/unobservable" to "specific evidence available"
    → Worth Human Semantic / Boundary Review

  DIAGNOSTIC_VALUE_GAIN:    3 cases (same as above)
    → Failure mechanism is now more clearly diagnosable

  NO_VALUE_GAIN:            1 case (AMB-052 — no extent on page)
    → New evidence present but no diagnostic value

  SUPPORTING_ONLY:          9 cases
    → New evidence present but doesn't change diagnosis
```

### High-value case justification

```
AMB-414 (MERGE, "FIG. 9:" + "Left:"):
  E0: "P2 shows same_y_band, h_gap — but WHY merge? No visual context."
  E1: "Drawing extent exists (78181 area, 16 primitives), text_a 34.5pt below extent"
  → NOW worth Human Review: "Is this text a caption of the nearby drawing?"
  → Specific, evidence-backed question (not vague "looks interesting")

AMB-422 (MERGE, "FIG. 12:" + "Distribution..."):
  E0: "P2 shows same_y_band — but WHY merge? No visual context."
  E1: "Drawing extent exists (109066 area, 2 primitives), text_a 54.8pt below extent"
  → NOW worth Human Review: "Is this text a caption of the nearby drawing?"

EXT-ARXIV2402-P28 (visual skipped):
  E0: "216 primitives invisible — complete perception gap"
  E1: "216 primitives observable, 1 extent, text near extent"
  → NOW worth Human Review: "What is the relationship between text and drawing on this page?"
```

---

## 9. Counterfactual Analysis

```
COUNTERFACTUAL_CHECK:

For each NEW_DIAGNOSTIC_EVIDENCE case:
  "Without DRAWING_GEOMETRY_FACT / DRAWING_EXTENT_FACT, could this diagnosis be made from E0?"

  AMB-414: NO
    → Without vector geometry, E0 has 0 NTB, 0 drawing evidence
    → Cannot determine "text is near a figure" from text-only evidence
    → Diagnosis is FULLY DEPENDENT on new evidence

  AMB-422: NO
    → Same reasoning: 0 NTB, 0 drawing evidence in E0
    → Cannot determine "text is near a figure"
    → Fully dependent on new evidence

  EXT-ARXIV2402-P28: NO
    → Without vector geometry, 216 primitives are invisible
    → Cannot even observe that visual content exists
    → Fully dependent on new evidence

COUNTERFACTUAL_NO_DEPENDENCE (fully dependent): 3
COUNTERFACTUAL_PARTIAL_DEPENDENCE:             9
COUNTERFACTUAL_FULL_DEPENDENCE (diagnosis possible without): 1
```

### Key insight

```
3 cases where counterfactual = NO:
  These are the cases where Vector Geometry Evidence provides GENUINELY NEW diagnostic capability.
  The diagnosis CANNOT be made from existing evidence alone.
  → This is the real value of the new Observation Surface.
```

---

## 10. Negative Controls

```
NEGATIVE_CONTROLS: 6 cases (table text boundary)

Purpose: verify that Vector Geometry doesn't just "add evidence to everything"
  but specifically improves diagnostic capability for visual-related failures.

Results:
  NEW_DIAGNOSTIC_EVIDENCE:  0  (correctly NOT elevated)
  NEW_SUPPORTING_EVIDENCE: 5  (drawings exist but not diagnostic for table text)
  NO_NEW_EVIDENCE:         1  (no extent on page)

NEGATIVE_CONTROL_FALSE_VALUE = 0
  → No negative control was incorrectly elevated to diagnostic level
  → Vector Geometry does NOT cause false diagnostic value for non-visual failures

Detail:
  AMB-024 (resnet p6, "28.54" vs "10.02"):
    83 drawings, 1 extent on page, text near extent (17.5pt)
    BUT: table text boundary is fully explained by P2 geometry
    → Drawings near text does NOT mean "caption association" — this is table content
    → Correctly classified as NEW_SUPPORTING (not diagnostic)

  AMB-052 (resnet p7, "0.46M" vs "7.51"):
    53 drawings, 0 extents
    → NO_NEW_EVIDENCE (no aggregated extent)
    → Correctly non-diagnostic
```

### Anti-bias verification

```
"Drawing near text" does NOT automatically mean "caption":
  - resnet p6/p8: drawing extent near table text, but it's TABLE BORDER, not figure
  - Vector Geometry correctly shows "drawing extent exists" (geometric fact)
  - It does NOT claim "this is a figure" (semantic interpretation forbidden)
  - The diagnostic value comes from COMBINING drawing extent + FIG-prefix + MERGE label
  - NOT from drawing extent alone

This confirms the Anti-Bias Rule:
  "drawing extent" ≠ "figure"
  "text near drawing" ≠ "caption"
  The value is in the EVIDENCE ORGANIZATION step, not in automatic semantic interpretation.
```

---

## 11. Case-level Findings

### Case 1: IS11-AMB-414 (MERGE, med_001 p20)

```
E0: PARTIALLY_EXPLAINABLE
  P1: 363 atoms, P2: geometry shows same_y_band + h_gap
  NTB: 0 (no raster), NO visual evidence
  Problem: "FIG. 9:" + "Left:" should merge, but E0 can't show WHY (no figure evidence)

E1: NEW_DIAGNOSTIC_EVIDENCE
  DRAWING_GEOMETRY_FACT: 235 primitives
  DRAWING_EXTENT_FACT: 1 extent [88.45,127.28,526.03,305.95], 16 primitives, area=78181
  text_a "FIG. 9:" is 34.5pt below extent
  Problem: NOW we know "text is near a drawing extent" — the missing dimension

Counterfactual: NO (without vector geometry, cannot make this diagnosis)
Value: HIGH_VALUE_CASE_GAIN
```

### Case 2: IS11-AMB-422 (MERGE, med_001 p24)

```
E0: PARTIALLY_EXPLAINABLE
  P1: 214 atoms, P2: geometry shows same_y_band + h_gap
  NTB: 0, NO visual evidence
  Problem: "FIG. 12:" + "Distribution..." should merge, but E0 can't show WHY

E1: NEW_DIAGNOSTIC_EVIDENCE
  DRAWING_GEOMETRY_FACT: 635 primitives
  DRAWING_EXTENT_FACT: 1 extent [176.83,144.96,469.99,517.0], 2 primitives, area=109066
  text_a "FIG. 12:" is 54.8pt below extent
  Problem: NOW we know "text is near a drawing extent"

Counterfactual: NO
Value: HIGH_VALUE_CASE_GAIN
```

### Case 3: EXT-ARXIV2402-P28 (visual skipped)

```
E0: NOT_EXPLAINABLE
  P1: 630 atoms, NTB: 0
  216 vector primitives completely invisible
  Problem: cannot even observe visual content exists

E1: NEW_DIAGNOSTIC_EVIDENCE
  DRAWING_GEOMETRY_FACT: 216 primitives (ALL recorded)
  DRAWING_EXTENT_FACT: 1 extent [123.73,77.15,503.18,178.35], 12 primitives
  text_a "Fig. 14" is 17.2pt below extent
  Problem: visual content NOW observable, text near drawing

Counterfactual: NO
Value: HIGH_VALUE_CASE_GAIN
```

### Cases 4-7: Adjudicated Ambiguous

```
E0: PARTIALLY_EXPLAINABLE → E1: NEW_SUPPORTING_EVIDENCE
  Drawings exist on page but don't directly resolve the ambiguity
  Counterfactual: PARTIALLY (some diagnosis possible, but less complete)
  Value: SUPPORTING_ONLY (not HIGH_VALUE)
```

### Cases 8-13: Negative Controls

```
E0: EXPLAINABLE → E1: NEW_SUPPORTING_EVIDENCE (5) / NO_NEW_EVIDENCE (1)
  Drawings exist on some pages but NOT diagnostic for table text boundary
  NEGATIVE_CONTROL_FALSE_VALUE = 0
  Counterfactual: PARTIALLY (9) / YES (1)
  Value: NO_VALUE_GAIN (correctly — table text doesn't need visual evidence)
```

---

## 12. Quantitative Summary

```
N total cases: 13

E0:
  EXPLAINABLE:            6
  PARTIALLY_EXPLAINABLE:  6
  NOT_EXPLAINABLE:        1

E1:
  NO_NEW_EVIDENCE:           1
  NEW_SUPPORTING_EVIDENCE:   9
  NEW_DIAGNOSTIC_EVIDENCE:   3

EXPLANATION_GAIN:
  NOT_EXPLAINABLE → NEW_DIAGNOSTIC:     1
  PARTIALLY_EXPLAINABLE → NEW_DIAGNOSTIC: 2
  Total diagnostic gain:                3

FAILURE_LOCALIZATION_GAIN:
  NEWLY_LOCALIZED:  3
  UNCHANGED:       10

PROBLEM_VALUE_GAIN:
  HIGH_VALUE_CASE_GAIN:     3
  DIAGNOSTIC_VALUE_GAIN:    3
  NO_VALUE_GAIN:            1
  SUPPORTING_ONLY:          9

COUNTERFACTUAL:
  NO (fully dependent on new evidence):      3
  PARTIALLY:                                9
  YES (diagnosis possible without):          1

NEGATIVE_CONTROL_FALSE_VALUE: 0
  (6 negative controls, 0 incorrectly elevated to diagnostic)

SAMPLE_SIZE_LIMITATION = TRUE (13 cases — no significance testing)
```

---

## 13. Limitations

```
1. Small sample size (13 cases):
   - No significance testing possible
   - Results are indicative, not statistically proven
   - 3 diagnostic gains out of 13 cases (23%) — but denominator is small

2. Case selection bias risk:
   - MERGE cases were known to have visual relevance (FIG-prefix in text)
   - This is NOT selection bias on vector geometry (selection was based on text labels, not drawings)
   - But: the 2 MERGE cases are from a SINGLE document (med_001)
   - Generalization to other documents/corpora is unverified

3. Negative control limitation:
   - 6 negative controls are all from resnet (table pages)
   - No negative controls from med_001 or cs_001
   - "Drawing near table text" is a specific pattern; other patterns untested

4. No semantic validation:
   - "text near drawing extent" is a geometric fact, not a semantic claim
   - Whether this geometric fact is USEFUL for caption association requires Hypothesis layer
   - This experiment only shows the evidence is AVAILABLE, not that it is SUFFICIENT

5. Corpus restoration:
   - IS-11 PDFs were re-downloaded from arxiv (SHA-256 verified)
   - This is NOT new corpus creation, but the PDFs were not in their original location
   - No GT modification (IS-11 JSON is FROZEN and unchanged)

6. Only MERGE cases tested for M-A:
   - 2 MERGE cases is very small
   - No negative MERGE cases (cases where text has FIG-prefix but should NOT merge)
   - Counterfactual cases for caption association not available in IS-11

7. No M-B (table locality) testing:
   - efficientnet p5-p8 TLD failure cases not directly tested
   - M-B core problem (prose=table geometric overlap) is not visual — confirmed in prior audit
   - Visual geometry is NOT expected to help M-B (and this experiment doesn't claim it does)
```

---

## 14. Interpretation

### What the data shows

```
3 cases (23% of 13) show NEW_DIAGNOSTIC_EVIDENCE with counterfactual=NO:
  - These are cases where Vector Geometry provides GENUINELY NEW diagnostic capability
  - The diagnosis CANNOT be made from existing evidence alone
  - All 3 are visual-relevance cases (MERGE caption + visual-skipped)

0 negative controls were incorrectly elevated:
  - Vector Geometry does NOT cause false diagnostic value
  - "Drawing near text" is correctly NOT diagnostic for table text boundary

Failure localization shifted for 3 cases:
  - "Perception Missing" → "Evidence Organization Gap"
  - The problem is now more tractable (can see visual content, need to organize/interpret)
```

### What the data does NOT show

```
NOT shown:
  - Figure detection accuracy improvement (not tested)
  - Caption detection accuracy improvement (not tested)
  - Overall document recognition improvement (not tested)
  - That "text near drawing" = "caption" (this is semantic interpretation, forbidden)
  - That M-B table locality is improved (M-B is prose=table overlap, not visual)
  - Statistical significance (sample too small)

VECTOR_GEOMETRY_EVIDENCE = OBSERVABLE ≠ DOCUMENT_RECOGNITION = IMPROVED
  These two are strictly separate.
  The experiment only shows the former.
```

### The genuine value

```
The genuine value is:
  "We can NOW observe that drawing content exists and where it is,
   relative to text. We could NOT observe this before."

This is NOT the same as:
  "We can NOW identify figures and captions."

The value is at the Evidence layer, not the Interpretation layer.
The Evidence Organization step (consumer) is still needed to form hypotheses.
```

---

## 15. Decision

```
VALUE_PARTIALLY_SUPPORTED
```

### Reasoning

```
POSITIVE evidence:
  ✓ 3 real cases with NEW_DIAGNOSTIC_EVIDENCE (counterfactual=NO)
  ✓ 0 negative control false positives
  ✓ Failure localization shifted (Perception Missing → Evidence Organization Gap)
  ✓ 3 HIGH_VALUE_CASE_GAIN (worth Human Review)

PARTIAL (not STRONG POSITIVE) because:
  ✗ Sample size very small (13 cases, 3 diagnostic gains)
  ✗ 2 of 3 diagnostic cases from single document (med_001)
  ✗ No negative MERGE cases tested (could "text near drawing" mislead?)
  ✗ No statistical significance
  ✗ Value is at Evidence layer only — semantic interpretation still needed
  ✗ M-B (table locality) not improved (confirmed: visual ≠ table overlap problem)

NOT VALUE_NOT_DEMONSTRATED because:
  - 3 counterfactual=NO cases prove genuine new diagnostic capability
  - 0 negative control false positives prove no misleading value

NOT VALUE_NEGATIVE because:
  - No evidence of misleading or harmful value
  - No negative controls incorrectly elevated

NOT STRONG POSITIVE because:
  - Does not meet "multiple real independent cases" threshold (2/3 from same doc)
  - Does not demonstrate sufficient breadth of value
```

---

## 16. Final Governance Status

```text
AO_VISUAL_GEOMETRY_VALUE_EXPERIMENT = COMPLETE

EXPERIMENT_DECISION = VALUE_PARTIALLY_SUPPORTED

EXPLANATION_GAIN = 3 cases (NOT_EXPLAINABLE/PARTIALLY → NEW_DIAGNOSTIC)
FAILURE_LOCALIZATION_GAIN = 3 cases (NEWLY_LOCALIZED)
PROBLEM_VALUE_GAIN = 3 HIGH_VALUE_CASE_GAIN
COUNTERFACTUAL_NO_DEPENDENCE = 3 (genuine new diagnostic capability)
NEGATIVE_CONTROL_FALSE_VALUE = 0

SAMPLE_SIZE_LIMITATION = TRUE (13 cases, no significance testing)

VECTOR_GEOMETRY_EVIDENCE = OBSERVABLE (confirmed)
DOCUMENT_RECOGNITION_IMPROVED = NOT_DEMONSTRATED (not tested, not claimed)

FIGURE_DETECTION = NOT_TESTED
CAPTION_DETECTION = NOT_TESTED
CHART_DETECTION = NOT_TESTED
FLOWCHART_DETECTION = NOT_TESTED

SEMANTIC_GAP_REMAINS = TRUE
  "text near drawing extent" ≠ "caption"
  Evidence Organization → Semantic Hypothesis still needed

IMPLEMENTATION = COMPLETE (DRAWING_GEOMETRY_FACT + DRAWING_EXTENT_FACT)
EXPERIMENT = COMPLETE (value assessment)

FROZEN_BASELINE = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d, P1=74d23ec7)
P1_P6_REGRESSION = UNCHANGED
P7.1 = UNCHANGED
TLD = UNCHANGED
IS-11 = UNCHANGED (FROZEN, not modified)
IS-14 = UNCHANGED

CAPABILITY = UNCHANGED
RUNTIME_AUTHORITY = ZERO
PRODUCTION = FALSE

STOP = TRUE
```

---

## Experiment Principle Adherence

- ✅ Used existing real failure cases (IS-11 GT + P7 evidence gap)
- ✅ Did NOT create synthetic cases
- ✅ Did NOT use LLM for semantic judgment
- ✅ Did NOT modify any algorithm based on results
- ✅ Did NOT modify TLD / IS-11 / IS-14 / P7 / Capability / Runtime
- ✅ Included negative controls (6 table text cases)
- ✅ Ran counterfactual checks (3 NO, 9 PARTIALLY, 1 YES)
- ✅ Did NOT equate "observable" with "improved"
- ✅ Did NOT claim figure/caption detection improvement
- ✅ Reported sample size limitation honestly
- ✅ Did NOT auto-enter M-A / M-B / Human Feedback / L3 / Capability
- ✅ Frozen baseline intact (drift=0/7)

`STOP = TRUE`.
