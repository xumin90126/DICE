# M-A Human Validation Pilot Analysis

> **模式: READ-ONLY ANALYSIS / NO MODIFICATION / FROZEN INTACT / STOP**
> 日期: 2026-09-17
> 前置: M-A Human Validation Pilot (79 cases) + Data Integrity Audit (PASS)
> 本文件: 分析真实 Human Validation Pilot 数据，回答 M-A 是否已构成可操作的 Human Review Object。

---

## 1. Executive Summary

```
M-A Human Validation Pilot provides real evidence that the current
Text + Vector Geometry + Evidence Organization pipeline can produce
Human-reviewable Text-Drawing Association cases.

The strongest observed pattern is:
  caption_like text (FIG.N / Figure N.) near a drawing extent
  → 100% Human-confirmed association (39/39 YES)

At the same time:
  - Type B negatives (non-FIG text near drawing) show 50% YES —
    proximity alone does NOT define association.
  - Ambiguous fragments ("Fig." standalone) show 63% YES, 21% NO, 16% UNCERTAIN —
    FIG-prefix without full pattern is insufficient.
  - 9 of 14 UNCERTAIN cases are Evidence Insufficiency (no drawing extent
    on page or text too short), NOT Semantic Boundary.

The Pilot supports the existence of a useful Human Review Object,
but does NOT establish:
  - general document-recognition accuracy
  - machine classification accuracy
  - inter-rater reliability (single-rater pilot)
  - broad cross-document generalization (5 arxiv-style papers only)
```

---

## 2. Data Integrity Confirmation

```
From m_a_human_validation_data_integrity_audit.md (PASS):

  UNIQUE_CASES = 79
  REVIEW_EVENTS = 80 (includes 1 revision)
  FINAL_JUDGMENTS = 79
  YES = 61, NO = 4, UNCERTAIN = 14
  SUM = 79 ✓
  COVERAGE = 79/79 = 100%
  SKIPPED = 0
  REVISION_CASES = 1 (case #46: uncertain → yes)
  CASE_TYPE = MUTUALLY_EXCLUSIVE (6 types, sum = 79)
  DATA_INTEGRITY = PASS
  HUMAN_JUDGMENT_MODIFIED = NO
  FROZEN_BASELINE_DRIFT = 0
```

---

## 3. Human Validation Population

```
N_HUMANS = 1 (single-rater pilot)
  → Inter-rater agreement: NOT_AVAILABLE
  → Cannot claim reliability beyond single observer

REAL_HUMAN_VALIDATION = TRUE
  → Judgments made by a real human through the review interface
  → Not simulated, not algorithm-generated

DOCUMENTS = 5 (all arxiv-style scientific papers):
  is11_med_001:        15 cases
  is11_resnet:         14 cases
  is11_efficientnet:   15 cases
  is11_cs_001:          4 cases
  arxiv_2402.18619:    31 cases

DOCUMENT_TYPE = scientific papers only
  → Generalization to other document types NOT_DEMONSTRATED

CASE_TYPES (mutually exclusive):
  caption_like:        39
  ambiguous_fragment:  19
  subfigure_label:      4
  reference_like:       1
  Type_A_negative:      8
  Type_B_negative:      8
  TOTAL:               79
```

---

## 4. Human Completion Behavior

### Level 1 — Observed Behavior

```
Coverage:        79/79 = 100% (all cases reviewed)
Skip rate:       0/79 = 0%
Revision rate:   1/79 = 1.3% (case #46: uncertain → yes, 3.5s later)
UNCERTAIN rate:  14/79 = 17.7%
```

### Level 2 — Interface-supported Inference

```
The review interface provided:
  ✓ Real PDF page image with highlighted text + drawing
  ✓ Full Page + Focus View
  ✓ Zoom controls
  ✓ Evidence Panel (text, spatial relation, context)
  ✓ Three equal-weight buttons (YES / NO / UNCERTAIN)

Human did NOT need to:
  ✗ Find the text (highlighted)
  ✗ Find the drawing (highlighted)
  ✗ Understand bbox coordinates (visual overlay)
  ✗ Understand vector primitives (not shown)
  ✗ Understand FIG-prefix detection (text shown as-is)

Human COULD:
  ✓ See text and drawing on real page
  ✓ See spatial relationship (descriptive: "文字位于图形区域下方")
  ✓ Make a judgment (one click)
```

### Level 3 — Actual Cognitive Load

```
NOT_MEASURED

  No time-per-case data collected.
  No NASA-TLX or subjective rating collected.
  No interview conducted.

  Cannot claim:
    ✗ "low cognitive load"
    ✗ "easy"
    ✗ "fast"
    ✗ "low effort"

  Can only claim:
    ✓ Task was completed (100% coverage)
    ✓ Human used UNCERTAIN when unsure (not forced into binary)
```

---

## 5. Association Judgment Distribution

```
Final Judgments (79 unique cases):

  YES:        61 (77.2%)
  NO:          4 (5.1%)
  UNCERTAIN:  14 (17.7%)

  YES + NO + UNCERTAIN = 79 ✓

NOTE:
  61 YES is NOT "M-A accuracy = 77.2%".
  YES means Human confirmed association, not machine correctness.
  There is no machine prediction being compared to ground truth.
```

---

## 6. Case-Type Analysis

### Cross-tabulation

| Case Type | N | YES | NO | UNC | YES% | NO% | UNC% |
|-----------|---|-----|----|----|------|-----|------|
| caption_like | 39 | 39 | 0 | 0 | 100% | 0% | 0% |
| ambiguous_fragment | 19 | 12 | 4 | 3 | 63% | 21% | 16% |
| subfigure_label | 4 | 4 | 0 | 0 | 100% | 0% | 0% |
| reference_like | 1 | 1 | 0 | 0 | 100% | 0% | 0% |
| Type A negative | 8 | 1 | 0 | 7 | 12.5% | 0% | 87.5% |
| Type B negative | 8 | 4 | 0 | 4 | 50% | 0% | 50% |
| **TOTAL** | **79** | **61** | **4** | **14** | | | |

### Interpretation

```
caption_like (n=39): 100% YES
  → "FIG.N:" / "Figure N." + near drawing extent = universally confirmed association
  → STRONGEST pattern in this pilot
  → BUT: 39 cases is NOT the full caption population; cannot generalize to "all captions"

ambiguous_fragment (n=19): 63% YES, 21% NO, 4 UNCERTAIN
  → "Fig." / "FIG." standalone fragment + near drawing = mixed signal
  → 4 NO cases: Human explicitly rejected association
  → 3 UNCERTAIN: Human could not determine (see §8)
  → FIG-prefix ALONE is insufficient for association

subfigure_label (n=4): 100% YES
  → "Fig. 14a/b/c/d" sub-figure labels = confirmed association
  → n=4 is very small; cannot generalize

reference_like (n=1): 100% YES
  → "Fig. 3). When..." = 1 case, Human said YES
  → n=1: no statistical meaning

Type A negative (n=8): 12.5% YES, 87.5% UNCERTAIN
  → FIG-prefix + NOT near drawing = mostly UNCERTAIN
  → 0 NO: Human did NOT explicitly reject (see §9)

Type B negative (n=8): 50% YES, 50% UNCERTAIN
  → Near drawing + NO FIG-prefix = split between YES and UNCERTAIN
  → 0 NO: Human did NOT explicitly reject (see §9)
```

---

## 7. Evidence Pattern Analysis

### Spatial Evidence by Judgment

```
                    YES (n=61)    NO (n=4)     UNCERTAIN (n=14)
Distance (median):  18.4pt        25.5pt       38.4pt
Distance (range):   0–56.9pt      17.8–56.8pt  0–56.4pt
                    (1 case no extent)          (7 cases no extent)

V-order:
  below:             45            3            1
  above:              8            1            5
  inside:             7            0            1
  none:               1            0            7

X-overlap:
  True:              49            3            4
  False:             12            1            10
```

### Descriptive Observations (NOT rules, NOT thresholds)

```
1. Distance:
   YES cases: median 18.4pt (closer)
   NO cases: median 25.5pt (farther)
   UNCERTAIN: median 38.4pt (farthest, but 7 have no extent at all)
   → Closer text tends toward YES, but this is descriptive, not a rule.
   → NO threshold should be derived from this.

2. Vertical ordering:
   YES: 45/61 (74%) below the drawing — dominant pattern
   NO: 3/4 (75%) below — same position, different judgment
   → Position alone does NOT determine judgment.

3. X-overlap:
   YES: 49/61 (80%) have x-overlap
   UNCERTAIN: 10/14 (71%) have NO x-overlap
   → X-overlap correlates with YES, but is NOT necessary
   (12 YES cases have no x-overlap; AMB-422 has no overlap but was YES)

4. Drawing extent presence:
   YES: 60/61 have extent (1 Type A YES without extent)
   NO: 4/4 have extent
   UNCERTAIN: 7/14 have NO extent
   → Absence of extent strongly correlates with UNCERTAIN
   → This is Evidence Insufficiency, NOT Semantic Boundary
```

### FIG-prefix Role

```
FIG-prefix + near drawing (candidates, n=63):
  YES: 56 (88.9%), NO: 4 (6.3%), UNC: 3 (4.8%)
  → High association confirmation rate

FIG-prefix + NOT near drawing (Type A, n=8):
  YES: 1 (12.5%), NO: 0, UNC: 7 (87.5%)
  → Mostly UNCERTAIN — Human cannot assess without spatial context
  → FIG-prefix ALONE does NOT produce YES

Near drawing + NO FIG-prefix (Type B, n=8):
  YES: 4 (50%), NO: 0, UNC: 4 (50%)
  → Split — proximity without FIG-prefix is ambiguous
  → Some non-FIG text IS associated (axis labels, annotations)

OBSERVED PATTERN (not rule):
  FIG-prefix + near drawing → high YES rate
  FIG-prefix + not near drawing → mostly UNCERTAIN
  Near drawing + no FIG-prefix → mixed YES / UNCERTAIN
```

---

## 8. UNCERTAIN Case Analysis

### Classification of 14 UNCERTAIN Cases

```
Category A: Evidence Insufficiency — No drawing extent (7 cases)
  These are Type A negatives where the page has no aggregated drawing extent.
  Human cannot assess spatial relation because there is no drawing to compare.

  UNC#1:  efficientnet p3, "Figure" — no extent on page
  UNC#4:  efficientnet p4, "Figure" — no extent on page
  UNC#8:  med_001 p18, "Figure" — no extent on page
  UNC#9:  efficientnet p2, "Figure" — no extent on page
  UNC#10: med_001 p15, "figure" — no extent on page
  UNC#12: resnet p7, "Fig. 6 (middle) shows..." — no extent on page
  UNC#13: arxiv p11, "Fig. 3a that connects..." — no extent on page

  Assessment: EVIDENCE_INSUFFICIENCY
  → Drawing may exist but was filtered out (too small / border-like)
  → OR drawing is on a different page (cross-page reference)
  → This is NOT a semantic boundary — it's an observation gap

Category B: Evidence Insufficiency — Text too short (2 cases)
  Non-FIG text near drawing, but text is too short to determine role.

  UNC#11: efficientnet p6, "omit" — 4 chars, near extent 21.9pt above
  UNC#14: med_001 p15, "max" — 3 chars, near extent 33.1pt above

  Assessment: EVIDENCE_INSUFFICIENCY
  → Cannot determine if "omit" / "max" is axis label, annotation, or body text fragment
  → Text content is insufficient for Human to judge

Category C: Possible Semantic Boundary — Ambiguous FIG fragment (3 cases)
  Standalone "Fig." fragment near drawing — could be caption start or in-text reference.

  UNC#5: arxiv p19, "Fig." 56.4pt above, context: "given by lines in Fig. 9"
  UNC#6: arxiv p26, "Fig." 38.8pt above, context: "cf. Fig. 3b"
  UNC#7: resnet p4, "Fig." 38.4pt below, context: "34-layer plain net is in Fig. 3"

  Assessment: POSSIBLE_SEMANTIC_BOUNDARY
  → Context suggests in-text reference ("in Fig. 9", "cf. Fig. 3b", "in Fig. 3")
  → But "Fig." is near a drawing extent — could also be a caption fragment
  → Human cannot determine: is this a caption for THIS drawing, or a reference to ANOTHER drawing?
  → This IS a genuine semantic ambiguity

Category D: Possible Semantic Boundary — Non-FIG text near drawing (2 cases)
  Non-FIG text near drawing, role ambiguous.

  UNC#2: arxiv p15, ", with" — inside extent, could be annotation or body text
  UNC#3: arxiv p18, "scaling" — above extent, could be axis label or body text

  Assessment: POSSIBLE_SEMANTIC_BOUNDARY
  → Text is near drawing but role is unclear
  → Could be diagram-internal text (label/annotation) or adjacent body text
  → Human cannot determine from evidence alone
```

### Summary

```
UNCERTAIN BREAKDOWN:
  Evidence Insufficiency (no extent):     7 (50%)
  Evidence Insufficiency (text too short): 2 (14%)
  Possible Semantic Boundary (FIG fragment): 3 (21%)
  Possible Semantic Boundary (non-FIG text): 2 (14%)
  TOTAL:                                  14 (100%)

  Evidence Insufficiency:  9/14 = 64%
  Possible Semantic Boundary: 5/14 = 36%
  UNKNOWN: 0/14 = 0%
```

### Key Finding

```
MAJORITY of UNCERTAIN is Evidence Insufficiency (64%), NOT Semantic Boundary (36%).

This means:
  - 7 cases lack a drawing extent on the page (Type A without extent)
    → These are Observation gaps, NOT semantic ambiguity
    → Fixable by improving DRAWING_EXTENT_FACT aggregation

  - 2 cases have text too short to judge ("omit", "max")
    → These are P1 atom splitting artifacts
    → Need multi-atom context (same_y reconstruction)

  - Only 5 cases are genuine Semantic Boundary
    → "Fig." fragment that could be caption or reference
    → Non-FIG text that could be label or body text

H3 (Human uncertainty mainly corresponds to Semantic Boundary):
  → NOT_SUPPORTED
  → Majority of uncertainty is Evidence Insufficiency, not Semantic Boundary
  → Semantic Boundary exists but is the minority (5/14 = 36%)
```

---

## 9. Type A / Type B Negative Control Analysis

### Type A (FIG-prefix, NOT near drawing) — n=8

```
YES: 1 (12.5%)
NO: 0 (0%)
UNCERTAIN: 7 (87.5%)

Analysis:
  7 UNCERTAIN: All have NO drawing extent on page.
    → Human cannot assess — no drawing to compare against
    → This is NOT "Human confirmed negative" — it's "Human cannot judge"
    → These are NOT validated negatives

  1 YES (arxiv p10, "Figure 3a describes two equivalent options..."):
    → Full sentence with FIG-prefix on a page without drawing extent
    → Human judged YES despite no spatial proximity
    → Possible reason: text explicitly describes figure content ("describes two equivalent options")
    → This reveals: Human may use textual semantics, not just spatial evidence
    → SEMANTIC_ROLE = UNKNOWN (cannot determine why Human said YES)

NEGATIVE_CONTROL_VALIDATED = FALSE
  → 0 NO judgments means Type A was NOT explicitly rejected by Human
  → 87.5% UNCERTAIN means Human mostly could not judge
  → Type A negatives are Evidence-level exclusions, NOT Semantic GT negatives
  → SEMANTIC_NEGATIVE_GROUND_TRUTH = NOT_ESTABLISHED (confirmed)
```

### Type B (near drawing, NO FIG-prefix) — n=8

```
YES: 4 (50%)
NO: 0 (0%)
UNCERTAIN: 4 (50%)

4 YES Cases (detailed):

  1. efficientnet p8: "Accuracy(%)"
     → Inside extent [325,242,524,389], distance=0pt, x-overlap=True
     → This is likely an AXIS LABEL inside the drawing
     → Human judged YES — "associated with drawing"
     → This is a DIAGRAM-INTERNAL text, not a caption
     → SEMANTIC_ROLE = UNKNOWN (axis label? annotation?)

  2. arxiv p17: "the"
     → Below extent, distance=5.1pt, x-overlap=True
     → Single word "the" — likely body text fragment adjacent to drawing
     → Human judged YES — possibly because it's directly below drawing
     → SEMANTIC_ROLE = UNKNOWN

  3. cs_001 p5: "compared to"
     → Below extent, distance=7.1pt, x-overlap=True
     → Text fragment "compared to" — likely caption continuation or body text
     → Human judged YES
     → SEMANTIC_ROLE = UNKNOWN

  4. resnet p1: "networks."
     → Below extent, distance=13.5pt, x-overlap=True
     → Text fragment "networks." — likely body text or caption continuation
     → Human judged YES
     → SEMANTIC_ROLE = UNKNOWN

4 UNCERTAIN Cases:
  → 2 are very short text ("omit", "max") — Evidence Insufficiency
  → 2 are longer (", with", "scaling") — Possible Semantic Boundary

Analysis:
  Type B YES = 50% reveals:
    → "text near drawing" CAN be associated even without FIG-prefix
    → Some of these are likely axis labels, annotations, or diagram-internal text
    → Human's "association" judgment is BROADER than "caption" association
    → Human may interpret "associated" as "spatially/visually related" not "is caption of"

  Type B NO = 0 reveals:
    → Human did NOT explicitly reject any Type B case
    → Either Human sees all near-drawing text as potentially associated
    → Or Human is uncertain about the distinction (uses UNCERTAIN instead of NO)

NEGATIVE_CONTROL_VALIDATED = FALSE
  → 0 NO means Type B was NOT explicitly rejected
  → 50% YES + 50% UNCERTAIN means mixed signal
  → Type B negatives are Evidence-level exclusions, NOT validated Semantic negatives
```

### Negative Control Overall Assessment

```
Type A + Type B combined (n=16):
  YES: 5 (31.2%)
  NO: 0 (0%)
  UNCERTAIN: 11 (68.8%)

  NEGATIVE_CONTROL_VALIDATED = FALSE
  → 0 NO judgments across all 16 negatives
  → Human did NOT explicitly reject ANY negative control
  → 68.8% UNCERTAIN — mostly Evidence Insufficiency
  → 31.2% YES — Human saw association despite absence of expected signal

  This means:
    → Negative controls are NOT validated as "not associated"
    → They are Evidence-level exclusions (organization correctly filtered them)
    → But Human did NOT confirm them as semantic negatives
    → SEMANTIC_NEGATIVE_GROUND_TRUTH = NOT_ESTABLISHED

  FPR = 5/16 = 31.2%
    Formula: YES / neg_total (includes UNCERTAIN in denominator)
    Meaning: 31.2% of Evidence-level negatives were judged YES by Human
    This is NOT "machine classifier FPR" — there is no classifier.
    This measures: how often Human sees association in cases the organization excluded.

  FPR_excl_unc = 5/(5+0) = 100%
    Formula: YES / (YES + NO)
    Meaning: among cases where Human made a definitive judgment,
    ALL 5 were YES, 0 were NO.
    CAUTION: n=5 is extremely small. 0 NO may reflect Human's reluctance
    to use NO rather than true association rate.
```

---

## 10. Association Validity Interpretation

### Why 56/63, not 61/79

```
Total YES = 61 (across all 79 cases)
But Association Validity = 56/63

Reason:
  79 cases = 63 candidates + 16 negative controls

  Candidate YES = 56 (caption_like 39 + ambiguous_fragment 12 + subfigure_label 4 + reference_like 1)
  Negative YES = 5 (Type A 1 + Type B 4)

  Association Validity = candidate_YES / candidate_total = 56/63 = 88.9%
  This measures: "what fraction of machine-identified candidates did Human confirm?"

  61/79 = 77.2% would be WRONG because:
    → It includes 5 negative-control YES judgments in the numerator
    → It includes 16 negative controls in the denominator
    → Negative controls are NOT candidates — they are controls
    → Mixing them inflates the denominator and conflates two different questions

CORRECT METRIC NAME:
  "Candidate Association Confirmation Rate" (not "accuracy")
  = Human-confirmed YES / Machine-identified candidates
  = 56/63 = 88.9%
```

### What 88.9% Means

```
  88.9% of cases where the organization said "this text might be associated with this drawing"
  were confirmed by Human as YES.

  This does NOT mean:
    ✗ "M-A is 88.9% accurate" (no ground truth comparison)
    ✗ "88.9% of captions are detected" (not all captions are in the candidate set)
    ✗ "Machine correctly identifies associations" (machine only identifies candidates, not associations)

  This DOES mean:
    ✓ The candidate generation rule (FIG-prefix + near extent) produces
      cases that Human mostly confirms as associated
    ✓ The Evidence Organization pipeline is producing useful review candidates
```

---

## 11. Human Review Object Assessment

### A. Locatability (can Human see text + drawing?)

```
SUPPORTED

  ✓ All 79 cases had text highlighted on real PDF page image
  ✓ 71/79 had drawing extent highlighted (8 Type A had no extent — by design)
  ✓ Focus View auto-scrolled to text+drawing region
  ✓ Zoom supported

  Human did NOT need to find targets manually.
```

### B. Comprehensibility (can Human understand what to judge?)

```
SUPPORTED

  ✓ Human completed 100% of cases (0 skip)
  ✓ Human used all three options (YES, NO, UNCERTAIN)
  ✓ Human made 1 revision (shows active engagement, not random clicking)
  ✓ UNCERTAIN was used 14 times (Human distinguishes "can't judge" from "yes/no")

  Human understood: "is this text associated with this drawing?"
```

### C. Operability (can Human make YES/NO/UNCERTAIN?)

```
SUPPORTED

  ✓ Three equal-weight buttons
  ✓ Keyboard shortcuts (Y/N/U)
  ✓ Auto-advance after judgment
  ✓ Previous/Skip navigation
  ✓ 79/79 completed, 0 skipped
```

### D. Semantic Boundary (do cases exist that evidence alone cannot resolve?)

```
PARTIALLY_SUPPORTED

  5 of 14 UNCERTAIN cases are Possible Semantic Boundary:
    → 3 ambiguous_fragment "Fig." (caption vs reference)
    → 2 Type_B non-FIG text (label vs body text)

  9 of 14 UNCERTAIN cases are Evidence Insufficiency:
    → 7 no extent on page
    → 2 text too short

  Semantic Boundary EXISTS but is the MINORITY of uncertainty.
  Evidence Insufficiency is the MAJORITY.
```

### E. Candidate Value (do candidates contain Human-confirmed associations?)

```
SUPPORTED

  caption_like: 39/39 YES (100%)
  subfigure_label: 4/4 YES (100%)
  reference_like: 1/1 YES (100%)
  ambiguous_fragment: 12/19 YES (63%)

  Overall: 56/63 = 88.9% candidate confirmation rate
  → Candidates are predominantly Human-confirmed associations
```

---

## 12. Hypothesis Assessment

### H1: M-A can construct a Human-judgeable Text-Drawing Association Review Object

```
H1 = SUPPORTED

Evidence:
  ✓ 100% completion (79/79, 0 skip)
  ✓ Human used YES/NO/UNCERTAIN meaningfully
  ✓ Locatability: SUPPORTED (highlighted text + drawing)
  ✓ Comprehensibility: SUPPORTED (100% completion, meaningful distribution)
  ✓ Operability: SUPPORTED (all three options used)
  ✓ Candidate Value: SUPPORTED (88.9% confirmation)

Caveats:
  - Single-rater pilot (no inter-rater reliability)
  - 5 arxiv papers only (document type limited)
  - Cognitive load NOT measured (only completion observed)
```

### H2: Evidence Organization produces high-value Candidate Space

```
H2 = SUPPORTED

Evidence:
  ✓ Candidate confirmation rate: 56/63 = 88.9%
  ✓ caption_like: 100% YES (strongest pattern)
  ✓ Candidate space reduction: 6484 → 63 (99.0% reduction, from previous research)
  → The organization rule (FIG-prefix + near extent) produces mostly confirmed candidates

Caveats:
  - 4 NO cases (6.3%) — some candidates are NOT associated
  - 3 UNCERTAIN cases (4.8%) — some candidates are ambiguous
  - 4 ambiguous_fragment NO cases are standalone "Fig." near drawing but NOT caption
```

### H3: Human uncertainty mainly corresponds to Semantic Boundary

```
H3 = NOT_SUPPORTED

Evidence:
  UNCERTAIN breakdown (14 cases):
    Evidence Insufficiency: 9/14 = 64%
      → 7 no drawing extent (Type A without extent)
      → 2 text too short ("omit", "max")
    Possible Semantic Boundary: 5/14 = 36%
      → 3 ambiguous "Fig." fragment (caption vs reference)
      → 2 non-FIG text near drawing (label vs body text)

  MAJORITY of uncertainty is Evidence Insufficiency, NOT Semantic Boundary.
  → 7 cases lack drawing extent (Observation gap, fixable)
  → 2 cases have insufficient text (P1 atom splitting, fixable)
  → Only 5 cases are genuine semantic ambiguity

  H3 is NOT_SUPPORTED because:
    → "Mainly" is not met (36% vs 64%)
    → Most uncertainty can be reduced by improving evidence, not by semantic resolution
```

### H4: FIG-prefix is Candidate Space Reduction cue, not Association Truth

```
H4 = SUPPORTED

Evidence:
  FIG-prefix + near drawing (n=63): 88.9% YES
    → High confirmation rate — good candidate filter

  FIG-prefix + NOT near drawing (Type A, n=8): 12.5% YES, 87.5% UNCERTAIN
    → Low YES rate — FIG-prefix alone does NOT produce YES
    → Mostly UNCERTAIN (no spatial context to judge)

  Near drawing + NO FIG-prefix (Type B, n=8): 50% YES
    → 50% YES — proximity without FIG-prefix still produces some YES
    → FIG-prefix is NOT necessary for association
    → Type B YES cases ("Accuracy(%)", "the", "compared to", "networks.")
      show non-FIG text can be associated (axis labels, annotations)

  Conclusion:
    → FIG-prefix REDUCES candidate space (from 6484 to 63)
    → FIG-prefix does NOT DETERMINE association truth
    → Non-FIG text can be associated (Type B YES = 50%)
    → FIG-prefix without proximity does NOT produce YES (Type A = 12.5%)
    → FIG-prefix is a CANDIDATE_SPACE_REDUCTION cue, confirmed
```

---

## 13. Limitations

```
1. Single-rater pilot (N_HUMANS = 1)
   → No inter-rater reliability
   → Cannot distinguish personal judgment bias from general pattern
   → Need ≥2 raters for full experiment

2. 5 documents, all arxiv scientific papers
   → Document type limited to scientific papers
   → Other types (reports, slides, textbooks) untested
   → Cross-document generalization: CONDITIONAL (5 docs, 1 type)

3. caption_like concentration check:
   arxiv_2402:18619:  12 caption_like (31% of 39)
   is11_med_001:      11 caption_like (28%)
   is11_resnet:        6 caption_like (15%)
   is11_efficientnet:  7 caption_like (18%)
   is11_cs_001:        3 caption_like (8%)
   → caption_like is spread across ALL 5 documents
   → NOT concentrated in one document
   → But all are scientific papers with similar caption conventions

4. Small sample sizes for sub-types:
   subfigure_label: n=4
   reference_like: n=1
   → Cannot draw statistical conclusions from these

5. 0 NO in negative controls
   → Human did NOT explicitly reject any negative
   → May reflect Human's interpretation of "associated" (broad)
   → May reflect reluctance to use NO
   → Negative controls NOT validated as semantic negatives

6. Evidence Insufficiency in UNCERTAIN (9/14)
   → 7 cases lack drawing extent (Observation gap)
   → 2 cases have text too short (P1 atom splitting)
   → These are fixable evidence problems, not fundamental design issues

7. No time-per-case data
   → Cannot measure cognitive load
   → Cannot identify difficult cases by time

8. No pre-registered acceptance criteria
   → Cannot formally evaluate "pass/fail" of the pilot
   → Can only describe observed patterns

9. "Association" interpretation is broad:
   → Human YES on Type B ("Accuracy(%)", "the", "networks.")
   → Human may interpret "associated" as "spatially near" not "is caption of"
   → This is broader than the original M-A design intended
   → May need clearer task definition in full experiment
```

---

## 14. G9 Acceptance Criteria Pre-Registration Status

```
From m_a_pre_experiment_gate_design.md (G9):

7 metrics were designed:
  1. Candidate-space reduction: 99.0% (CONFIRMED, pre-existing)
  2. Association validity: 88.9% (MEASURED in pilot)
  3. False positive rate: 31.2% (MEASURED in pilot)
  4. Boundary rate: 17.7% (MEASURED in pilot)
  5. Human agreement: NOT_AVAILABLE (single rater)
  6. Human review burden: NOT_MEASURED (no time data)
  7. Evidence sufficiency: 64% of UNCERTAIN = insufficiency (MEASURED)

Pre-registration status:
  → Metrics 1-4, 7 are NOW MEASURED (from pilot data)
  → Metrics 5-6 are NOT_AVAILABLE (require multi-rater + time tracking)

  → Acceptance THRESHOLDS are still TO_BE_PRE_REGISTERED
    - Cannot set "pass" threshold based on pilot results (anti-p-hacking)
    - Must pre-register BEFORE full experiment
    - Pilot results can INFORM threshold selection, but threshold must be
      declared and frozen before full experiment begins

G9_ACCEPTANCE_CRITERIA = NEEDS_PRE_REGISTRATION
  → Metrics designed: YES
  → Metrics measured in pilot: YES (5/7)
  → Thresholds pre-registered: NO
  → Full experiment requires: pre-registered thresholds + multi-rater + time tracking
```

---

## 15. M-A Readiness

```
PILOT STATUS:
  M-A_HUMAN_VALIDATION_PILOT = COMPLETE
  → 79 cases, 100% coverage, real Human judgments
  → Data integrity: PASS
  → Analysis: COMPLETE (this report)

FULL_EXPERIMENT_READY = CONDITIONAL

  Conditions met:
    ✓ Research Object defined (H1: SUPPORTED)
    ✓ Evidence boundary defined (H4: SUPPORTED)
    ✓ Human task defined (ASSOCIATION_JUDGMENT)
    ✓ Sampling frame designed (5 strata)
    ✓ Ground truth process designed (3 levels, adjudication)
    ✓ Candidate space reduction confirmed (99.0%)
    ✓ Association validity measured (88.9%)
    ✓ Pilot completed (79/79, single rater)

  Conditions NOT met:
    ✗ Pre-registered acceptance thresholds (G9)
    ✗ Multi-rater protocol (N_HUMANS ≥ 2)
    ✗ Time-per-case tracking (cognitive load measurement)
    ✗ Document type diversity (only arxiv papers)
    ✗ Negative control validation (0 NO — negatives not confirmed)
    ✗ Evidence insufficiency resolution (9/14 UNCERTAIN are fixable gaps)

  FULL_EXPERIMENT_READY = CONDITIONAL
    → Design is READY
    → Pilot results are PROMISING
    → But: thresholds not pre-registered, single rater, limited document types
    → Full experiment requires: pre-registration + multi-rater + diverse documents
```

---

## 16. Governance Status

```text
M-A_HUMAN_VALIDATION_PILOT_ANALYSIS = COMPLETE

FROZEN_BASELINE = INTACT (drift=0/4)
  P1: 74d23ec784d65782 (UNCHANGED)
  TLD: 022f5c21e872ad9e (UNCHANGED)
  GT: 7349963d0d23b5ef (UNCHANGED)
  layout_analyzer: 8f69f0d206b3e565 (UNCHANGED)

HUMAN_JUDGMENT_MODIFIED = NO
HUMAN_VALIDATION_RE_RUN = NO
M-A_ALGORITHM_MODIFIED = NO
P1_MODIFIED = NO
P2_MODIFIED = NO
P6_MODIFIED = NO

CAPABILITY = UNCHANGED
RUNTIME_AUTHORITY = ZERO
PRODUCTION = FALSE

IMPLEMENTATION = NOT AUTHORIZED
HUMAN_FEEDBACK = NOT AUTHORIZED
L3 = NOT AUTHORIZED

STOP = TRUE
```

---

## 17. Final Decision

```
PILOT_ANALYSIS_STATUS = COMPLETE

HYPOTHESIS ASSESSMENT:
  H1 (Human Review Object exists):         SUPPORTED
  H2 (High-value Candidate Space):          SUPPORTED
  H3 (Uncertainty = Semantic Boundary):     NOT_SUPPORTED
  H4 (FIG-prefix = Reduction cue):          SUPPORTED

KEY FINDINGS:
  1. caption_like + near drawing → 100% Human-confirmed (strongest pattern)
  2. 88.9% candidate confirmation rate (56/63)
  3. UNCERTAIN is 64% Evidence Insufficiency, 36% Semantic Boundary
  4. 0 NO in negative controls (not validated as semantic negatives)
  5. Type B YES (50%) reveals "association" is broader than "caption"
  6. Single-rater, 5 arxiv papers, no time data

M-A_OVERALL_STATUS:
  The Pilot validates that M-A can construct a Human-reviewable
  Text-Drawing Association Review Object with high candidate value.

  However:
  - H3 is NOT supported (uncertainty is mainly evidence insufficiency)
  - Negative controls are NOT validated (0 NO)
  - Single-rater, limited documents, no cognitive load measurement
  - Acceptance thresholds not pre-registered

  Therefore:
  - M-A is NOT "proven" or "validated"
  - M-A is PROMISING and ready for full experiment DESIGN
  - Full experiment requires: pre-registration + multi-rater + diverse documents

FULL_EXPERIMENT_READY = CONDITIONAL
```

---

## Research Principle Adherence

- ✅ Used FINAL judgment (not raw events) for all statistics
- ✅ Case #46 counted as 1 unique case (final = YES)
- ✅ Did NOT claim machine accuracy (no machine prediction compared to GT)
- ✅ Did NOT claim "M-A accuracy = 88.9%" (used "Candidate Association Confirmation Rate")
- ✅ Did NOT claim low cognitive load (only completion observed)
- ✅ Did NOT claim inter-rater reliability (single rater)
- ✅ Did NOT claim cross-document generalization (5 arxiv papers, 1 type)
- ✅ Did NOT derive thresholds from results (descriptive only)
- ✅ Did NOT tune FIG-prefix rule or distance threshold
- ✅ Analyzed all 14 UNCERTAIN cases individually
- ✅ Distinguished Evidence Insufficiency from Semantic Boundary
- ✅ Did NOT auto-define UNCERTAIN as Semantic Boundary
- ✅ Reported FPR formula explicitly (with and without UNCERTAIN)
- ✅ Did NOT modify Human Judgment
- ✅ Did NOT modify M-A algorithm
- ✅ Did NOT modify P1/P2/P6/AO/TLD
- ✅ Frozen baseline intact (drift=0)
- ✅ Did NOT enter Human Feedback / L3 / Capability
- ✅ STOP = TRUE

`STOP = TRUE`.
