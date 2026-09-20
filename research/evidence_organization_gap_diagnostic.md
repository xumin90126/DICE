# Evidence Organization Gap Diagnostic Research

> **模式: DIAGNOSTIC RESEARCH / READ-ONLY / NO IMPLEMENTATION / FROZEN INTACT / STOP**
> 日期: 2026-09-17
> 前置: `tmp/ao_visual_geometry_value_experiment.md`（VALUE_PARTIALLY_SUPPORTED, 3 diagnostic cases）
> 本文件研究: Vector Geometry Evidence 的诊断价值来源，以及 Evidence Organization 是否成为新瓶颈。

---

## 1. Research Question

> 为什么新增 Vector Geometry Evidence 能让 3 个案例从"无法定位"变成"可以定位"？这种提升到底来自什么 Evidence？
>
> 加入 Vector Geometry 后，Evidence Organization 是否已经成为可独立研究的问题？

---

## 2. Core Cases

```
3 core cases (from VALUE experiment, counterfactual=NO):

  IS11-AMB-414:  med_001 p20, MERGE, "FIG. 9:" + "Left:"
  IS11-AMB-422:  med_001 p24, MERGE, "FIG. 12:" + "Distribution of errors..."
  EXT-ARXIV2402-P28: arxiv_2402 p28, VISUAL_CONTENT_SKIPPED, "Fig. 14"

6 negative controls (from VALUE experiment, correctly NOT diagnostic):
  IS11-AMB-024/032/034: resnet p6, table text
  IS11-AMB-052: resnet p7, table text
  IS11-AMB-064/074: resnet p8, table text
```

---

## 3. E0 Evidence

### Case 1: IS11-AMB-414 (med_001 p20)

```
E0 KNOWS:
  P1 atoms: 363
  text_a "FIG. 9:" bbox: [85.0, 340.5, 125.4, 352.5]
  text_b "Left:" bbox: [143.5, 340.5, 167.4, 352.5]
  P2 same_y_band: TRUE (dy=0.0 — same y)
  P2 h_gap: 18.1pt
  text_a has "FIG." prefix (P1 lexical fact)
  NTB (raster): 0

E0 DOES NOT KNOW:
  Is there visual content (drawing) on this page? → NO (NTB=0, no vector evidence)
  Where is the drawing relative to text_a? → UNKNOWN
  Is text_a spatially near a drawing? → CANNOT ANSWER
  Does a drawing extent overlap with text_a's x-range? → CANNOT ANSWER
```

### Case 2: IS11-AMB-422 (med_001 p24)

```
E0 KNOWS:
  P1 atoms: 214
  text_a "FIG. 12:" bbox: [85.0, 571.8, 128.7, 583.7]
  text_b "Distribution..." bbox: [139.1, 571.8, 249.0, 583.7]
  P2 same_y_band: TRUE (dy=0.0)
  P2 h_gap: 10.5pt
  text_a has "FIG." prefix
  NTB: 0

E0 DOES NOT KNOW:
  Same as AMB-414: no visual evidence at all
```

### Case 3: EXT-ARXIV2402-P28 (arxiv_2402 p28)

```
E0 KNOWS:
  P1 atoms: 630
  text_a "Fig. 14" bbox: [151.9, 82.3, 181.2, 94.3]
  text_a has "Fig." prefix
  NTB: 0

E0 DOES NOT KNOW:
  216 vector primitives exist on this page → COMPLETELY INVISIBLE
  Is there a drawing? → CANNOT ANSWER
  Where is the drawing? → CANNOT ANSWER
  Is text near drawing? → CANNOT ANSWER
```

### E0 Common Gap

```
ALL 3 cases share the same E0 gap:
  "Is there visual content near this text?" → CANNOT ANSWER

This is NOT a geometry gap (P2 geometry works fine for text-text).
This is NOT a reading order gap (P5 works for text).
This is a VISUAL EVIDENCE GAP: no surface observes drawing existence/position.
```

---

## 4. E1 Evidence

### Case 1: IS11-AMB-414 (E0 + Vector Geometry)

```
DRAWING_GEOMETRY_FACT: 235 primitives (ALL recorded)
DRAWING_EXTENT_FACT: 1 extent
  extent bbox: [88.45, 127.28, 526.03, 305.95]
  primitive_count: 16
  area: 78181.38

text_a "FIG. 9:" is 34.5pt BELOW the drawing extent
text_a x-overlaps with extent: TRUE (text_x=[85,125], extent_x=[88,526])
```

### Case 2: IS11-AMB-422 (E0 + Vector Geometry)

```
DRAWING_GEOMETRY_FACT: 635 primitives
DRAWING_EXTENT_FACT: 1 extent
  extent bbox: [176.83, 144.96, 469.99, 517.0]
  primitive_count: 2
  area: 109066.48

text_a "FIG. 12:" is 54.8pt BELOW the drawing extent
text_a x-overlaps with extent: FALSE (text_x=[85,129], extent_x=[177,470])
```

### Case 3: EXT-ARXIV2402-P28 (E0 + Vector Geometry)

```
DRAWING_GEOMETRY_FACT: 216 primitives
DRAWING_EXTENT_FACT: 1 extent
  extent bbox: [123.73, 77.15, 503.18, 178.35]
  primitive_count: 12
  area: 38398.5

text_a "Fig. 14" is 17.2pt ABOVE the drawing extent (inside extent y-range)
text_a x-overlaps with extent: TRUE (text_x=[152,181], extent_x=[124,503])
```

---

## 5. Evidence Delta

### What specifically changed from E0 to E1?

```
DELTA = 3 new facts per case:

  1. DRAWING_EXTENT_FACT.bbox exists on page
     → "There IS an aggregated visual region at [x0,y0,x1,y1]"
     → E0 had ZERO information about visual region existence

  2. text_a bbox ↔ extent bbox spatial distance
     → "text_a is N pt below/above the extent"
     → E0 could NOT compute this (no extent existed)

  3. text_a bbox ↔ extent bbox x-overlap
     → "text_a x-overlaps / does not overlap with extent"
     → E0 could NOT compute this (no extent existed)

PLUS:
  4. DRAWING_GEOMETRY_FACT primitive_count within extent
     → "extent contains N primitives (density signal)"
     → E0 had ZERO information about drawing density
```

### Delta is NOT:

```
  NOT "figure identity" (no is_figure)
  NOT "caption identity" (no is_caption)
  NOT "caption_of relationship" (no semantic relation)
  NOT "PNG content" (no visual recovery)
  NOT "caption regex" (no lexical inference beyond P1's existing text)

The delta is PURELY GEOMETRIC:
  extent exists + extent bbox + text-extent distance + text-extent overlap
```

---

## 6. Contribution Decomposition

### E0 + A (DRAWING_GEOMETRY_FACT only, no extent)

```
Case AMB-414:
  235 primitives recorded
  Nearest primitive to text_a: 15.3pt
  149 primitives within 100pt of text_a

  CAN answer: "There are many drawing primitives near text_a"
  CANNOT answer: "Is text_a near the drawing AS A WHOLE?"
  → Individual primitives are scattered; no aggregated region
  → "149 primitives within 100pt" is noisy (includes page decorations, table borders, etc.)
  → Cannot distinguish "text is near a figure" from "text is near scattered lines"

  VERDICT: PARTIAL — knows individual proximity, not aggregated region

Case AMB-422:
  635 primitives, nearest 15.3pt, 208 within 100pt
  VERDICT: PARTIAL — same issue (scattered, no aggregation)

Case EXT-ARXIV2402-P28:
  216 primitives, nearest 5.9pt, 204 within 100pt
  VERDICT: PARTIAL — same issue
```

### E0 + B (DRAWING_EXTENT_FACT only, no individual primitives)

```
Case AMB-414:
  1 extent: bbox=[88.45,127.28,526.03,305.95], 16 primitives, area=78181
  text_a is 34.5pt below extent, x-overlaps=TRUE

  CAN answer: "text_a is 34.5pt below an aggregated visual region, x-overlaps"
  CAN answer: "the visual region has 16 primitives and area 78181"
  → This is the KEY diagnostic fact: "text is near a drawing AS A WHOLE"

  VERDICT: YES — aggregated extent + text-extent distance = diagnostic

Case AMB-422:
  1 extent: bbox=[176.83,144.96,469.99,517.0], 2 primitives, area=109066
  text_a is 54.8pt below extent, x-overlaps=FALSE
  VERDICT: YES — extent + distance = diagnostic

Case EXT-ARXIV2402-P28:
  1 extent: bbox=[123.73,77.15,503.18,178.35], 12 primitives, area=38398
  text_a is 17.2pt above extent, x-overlaps=TRUE
  VERDICT: YES — extent + distance = diagnostic
```

### E0 + A + B (Full)

```
All 3 cases: A provides individual primitive details, B provides aggregated extent
→ A+B gives the most complete picture
→ But the DIAGNOSTIC value comes from B (extent), not A (individual primitives)
```

---

## 7. Primitive vs Extent Contribution

```
GAIN_SOURCE = EXTENT_GAIN (all 3 cases)

Reason:
  The aggregated extent (DRAWING_EXTENT_FACT) is what makes
  "text near drawing AS A WHOLE" answerable.

  Individual primitives (DRAWING_GEOMETRY_FACT) show scattered proximity
  but cannot distinguish "text near a figure" from "text near scattered lines/table borders".

  The extent provides:
    1. A single aggregated bbox (the "visual region" as a geometric fact)
    2. text-extent distance (how far is text from the visual region)
    3. text-extent x-overlap (does text align with the visual region)
    4. primitive_count (density signal — how complex is the visual region)

  These 4 facts TOGETHER transform the problem from:
    "text is near 149 scattered primitives" (noisy, uninterpretable)
  to:
    "text is 34.5pt below a 16-primitive extent with x-overlap" (structured, diagnosable)

  DRAWING_GEOMETRY_FACT contributes:
    - Raw existence (primitives exist on page)
    - Individual proximity (nearest primitive distance)
    - But NOT the aggregated region that enables diagnosis

  DRAWING_EXTENT_FACT contributes:
    - Aggregated region (single bbox)
    - Text-extent spatial relation (distance, overlap)
    - Density signal (primitive_count)
    - THIS is what enables the diagnostic gain
```

### Decomposition Summary

| Case | A alone | B alone | A+B | Gain Source |
|------|---------|---------|-----|-------------|
| AMB-414 | PARTIAL | YES | YES | EXTENT_GAIN |
| AMB-422 | PARTIAL | YES | YES | EXTENT_GAIN |
| EXT-P28 | PARTIAL | YES | YES | EXTENT_GAIN |

---

## 8. Evidence Organization Sufficiency

### After E1, what evidence do we have for each case?

```
For AMB-414 (MERGE, "FIG. 9:" + "Left:"):

  Available Evidence:
    1. P1: text_a="FIG. 9:" at [85,340,125,352] (lexical: "FIG." prefix)
    2. P1: text_b="Left:" at [143,340,167,352] (lexical: short label)
    3. P2: same_y_band=TRUE, h_gap=18.1pt (text_a and text_b are adjacent)
    4. DRAWING_EXTENT_FACT: extent [88,127,526,306] exists, 16 primitives
    5. Spatial: text_a is 34.5pt below extent, x-overlaps=TRUE
    6. Spatial: text_b is also near extent (same_y as text_a)

  Is this SUFFICIENT to describe the failure's structural relationship?
    → PARTIALLY_SUFFICIENT

  What's described:
    - text_a + text_b are adjacent (P2)
    - text_a has "FIG." prefix (P1 lexical)
    - A drawing extent exists nearby (DRAWING_EXTENT_FACT)
    - text_a is spatially close to extent (spatial relation)

  What's NOT described:
    - Is text_a actually a caption? (semantic — NOT answerable from evidence)
    - Is the extent actually a figure? (semantic — NOT answerable from evidence)
    - Should text_a + text_b be merged because they are caption? (semantic — needs hypothesis)
```

### Sufficiency Assessment

```
Case AMB-414: PARTIALLY_SUFFICIENT
  → Evidence describes "text near drawing" but not "text IS caption of figure"
  → The structural relationship is observable; the semantic relationship is not

Case AMB-422: PARTIALLY_SUFFICIENT
  → Same: structural relationship observable, semantic not

Case EXT-ARXIV2402-P28: PARTIALLY_SUFFICIENT
  → Evidence describes "216 primitives + extent + text near extent"
  → But cannot answer "what is the drawing?" or "is text a caption?"
```

### Overall Sufficiency

```
ALL 3 cases: PARTIALLY_SUFFICIENT

  The evidence is sufficient to:
    ✓ Observe that drawing content exists
    ✓ Observe where the drawing is (extent bbox)
    ✓ Observe text-drawing spatial distance
    ✓ Observe text-drawing x-overlap
    ✓ Observe text-text geometry (P2)
    ✓ Observe text lexical prefix (P1)

  The evidence is NOT sufficient to:
    ✗ Determine if the drawing is a figure (semantic)
    ✗ Determine if the text is a caption (semantic)
    ✗ Determine if text-drawing proximity means "caption-of" (semantic relation)
    ✗ Distinguish "caption near figure" from "footnote near figure" (semantic ambiguity)
```

---

## 9. Organization vs Interpretation Boundary

### Can the problem be solved by structural relations alone?

```
For AMB-414 (MERGE decision):

  Structural facts available:
    - text_a "FIG. 9:" + text_b "Left:" are same_y, h_gap=18.1pt
    - text_a is 34.5pt below drawing extent, x-overlaps
    - text_a has "FIG." prefix

  Can we decide MERGE from these structural facts alone?
    → NO

  Why NOT?
    - "FIG." prefix + near drawing + near text_b → SUGGESTS caption
    - BUT: "FIG." prefix could also be a reference ("see FIG. 9")
    - BUT: text near drawing could be footnote, not caption
    - BUT: text_b "Left:" could be a label inside the figure, not a caption continuation
    - The MERGE decision requires knowing: "is text_a+b the caption OF the drawing?"
    - This is a SEMANTIC RELATION (caption_of), not a spatial relation

  SEMANTIC_INTERPRETATION_REQUIRED = TRUE
    → To fully resolve the MERGE, we need to know "this text is a caption"
    → Structural evidence (proximity + prefix) is NECESSARY but NOT SUFFICIENT
    → The semantic step ("text near drawing + FIG prefix → caption") is a HYPOTHESIS
    → This hypothesis requires validation (human / counterfactual)
```

### For each case

```
AMB-414: SEMANTIC_INTERPRETATION_REQUIRED = TRUE
  → Structural evidence available, but MERGE decision needs "is this caption?"
  → "text near drawing" ≠ "caption" (footnote also near drawing)

AMB-422: SEMANTIC_INTERPRETATION_REQUIRED = TRUE
  → Same reasoning

EXT-ARXIV2402-P28: SEMANTIC_INTERPRETATION_REQUIRED = TRUE
  → "text near drawing" ≠ "caption of figure"
  → Need to know "what is the drawing?" and "what is the text's role?"
```

### Key distinction

```
Organization (structural): "text_a is 34.5pt below extent, x-overlaps, same_y as text_b"
  → This IS now answerable (was NOT before Vector Geometry)

Interpretation (semantic): "text_a is the caption of the figure"
  → This is NOT answerable from evidence alone
  → Requires Hypothesis layer + validation

The diagnostic gain came from Organization (structural facts now available).
But the final MERGE decision still requires Interpretation (semantic hypothesis).
```

---

## 10. Negative Controls

### Why do negative controls have drawings but NO diagnostic value?

```
6 negative controls (resnet p6/p7/p8, table text):

  ALL have drawings on page (83-367 primitives)
  SOME have text near extent (AMB-024: 17.5pt, AMB-074: 15.3pt)
  BUT: ALL correctly classified as NEW_SUPPORTING_EVIDENCE (not diagnostic)

Why no diagnostic value?

  1. text has NO "FIG." prefix
     → "28.54", "-", "21.59", "0.46M", "training data", "41.5"
     → None starts with "FIG." — these are table cell content, not caption-like

  2. failure type is KEEP_SEPARATE (boundary, not association)
     → The question is "should these be separated?" — answered by P2 geometry
     → P2 same_y_band + h_gap fully explains the separation
     → Visual evidence is IRRELEVANT to this question

  3. "drawing near text" ≠ "caption"
     → resnet p6 has drawing extent near "28.54" — but "28.54" is a TABLE CELL
     → The drawing is likely a TABLE BORDER or adjacent figure, not the text's caption
     → Proximity alone does NOT imply caption relationship

  NEGATIVE_CONTROL_FALSE_VALUE = 0
    → No negative control was incorrectly elevated to diagnostic
    → "drawing near text" correctly does NOT trigger diagnostic for table text
    → The diagnostic value requires BOTH:
      (a) text has "FIG." prefix (lexical signal)
      (b) text is near drawing extent (spatial signal)
      (c) failure is MERGE/association (not boundary)
    → All three conditions needed; negative controls miss (a) and (c)
```

### Anti-bias confirmation

```
"drawing exists" ≠ "problem is visual"
"drawing near text" ≠ "caption"

The diagnostic value is NOT from drawing alone.
It is from the COMBINATION of:
  - text lexical prefix ("FIG.")
  - text-drawing spatial proximity
  - failure type (association, not boundary)

This combination is an Evidence Organization pattern (structural + lexical),
NOT a semantic interpretation ("this is a caption").
```

---

## 11. Repeated Mechanism

### EVIDENCE_ORGANIZATION_PATTERN (research hypothesis, not implementation)

```
Observed in all 3 diagnostic cases:

  Pattern: Text-Drawing Spatial Association

  Conditions:
    1. text has "FIG."/"Fig." prefix (P1 lexical fact)
    2. drawing extent exists on same page (DRAWING_EXTENT_FACT)
    3. text is spatially near extent (distance < ~60pt)
    4. text x-overlaps or is adjacent to extent (spatial alignment)
    5. failure type is MERGE/association (not boundary)

  When ALL 5 conditions hold:
    → The failure is newly diagnosable as "text-drawing association problem"
    → E0 could not diagnose this (condition 2-4 were invisible)
    → E1 can diagnose this (all conditions observable)

  When conditions 1 or 5 are missing (negative controls):
    → No diagnostic value (correctly)
    → Drawing proximity alone is not diagnostic

  This is NOT:
    - Figure Detector (no is_figure)
    - Caption Detector (no is_caption)
    - Semantic Classifier (no semantic role)

  This IS:
    - Evidence Organization Pattern (structural + lexical conditions)
    - Research hypothesis for future Evidence Organization study
```

### Pattern abstraction

```
Evidence → Relation → Diagnostic usefulness

  Evidence:
    P1 text (lexical: "FIG." prefix)
    P2 text-text geometry (same_y, h_gap)
    DRAWING_EXTENT_FACT (extent bbox, primitive_count)
    Spatial: text-extent distance, x-overlap

  Relation (consumer-computed, NOT stored):
    text_a IS_NEAR drawing_extent (distance < threshold)
    text_a X_ALIGNS drawing_extent (x-overlap)
    text_a HAS_FIG_PREFIX (lexical)
    text_a + text_b ARE_ADJACENT (P2 same_y + h_gap)

  Diagnostic usefulness:
    IF HAS_FIG_PREFIX + IS_NEAR + X_ALIGNS + ARE_ADJACENT
    THEN "text-drawing association problem" is diagnosable
    → Worth Human Semantic / Boundary Review

  This pattern is a RESEARCH HYPOTHESIS, not an implementation.
  It must not be implemented without:
    - negative cases (text with FIG prefix but NOT caption)
    - boundary cases (footnote near figure)
    - independent documents
    - pre-registered evaluation rules
```

---

## 12. M-A Readiness Reassessment

### Q1: Did Vector Geometry solve M-A's VISUAL_REGION_EVIDENCE = MISSING?

```
YES — PARTIALLY

  M-A original gap (from m_a_caption_association_readiness_review.md):
    "VISUAL_REGION_EVIDENCE = MISSING"
    → Could not observe if visual content exists near text

  Now:
    DRAWING_EXTENT_FACT provides:
      - "visual region exists" (extent bbox)
      - "visual region position" (bbox coordinates)
      - "text-visual distance" (spatial relation, consumer-computed)

  The gap "VISUAL_REGION_EVIDENCE = MISSING" is now:
    VISUAL_REGION_EVIDENCE = AVAILABLE (as DRAWING_EXTENT_FACT)

  BUT: "VISUAL_REGION" as a SEMANTIC LABEL is still MISSING (and should remain so)
    → We have geometric extent, NOT semantic "figure region"
    → This is correct: Observation ≠ Interpretation
```

### Q2: Can we now research Evidence Organization / Association?

```
YES — with conditions

  Available evidence for Evidence Organization research:
    ✓ P1 text (lexical: "FIG." prefix, text content)
    ✓ P2 text-text geometry (same_y, h_gap, alignment)
    ✓ DRAWING_GEOMETRY_FACT (primitive existence, type, count)
    ✓ DRAWING_EXTENT_FACT (aggregated extent, position, density)
    ✓ Spatial: text-extent distance, x-overlap (consumer-computed)

  These are SUFFICIENT to research:
    "How should text-drawing spatial associations be organized as evidence?"

  These are NOT sufficient to research:
    "Is this text a caption?" (semantic — needs Hypothesis + validation)
```

### Q3: What is still missing?

```
1. Negative cases:
    - text with "FIG." prefix but NOT a caption (e.g., "see FIG. 9 for details")
    - text near drawing but NOT a caption (e.g., footnote near figure)
    - Currently: 0 negative cases in IS-11 corpus
    → WITHOUT negative cases, any association rule has unknown false-positive rate

2. Boundary cases:
    - text at edge of drawing (partially overlapping)
    - multiple drawings on one page (which one is text associated with?)
    - text between two drawings (ambiguous association)
    → Currently: untested

3. Independent documents:
    - 2 of 3 diagnostic cases are from med_001 (same document)
    - Need cases from at least 2-3 independent documents
    → Currently: med_001 + arxiv_2402 (only 2 documents)

4. Semantic ambiguity:
    - "FIG." prefix can be caption OR reference ("see FIG. 9")
    - text near drawing can be caption OR footnote OR label
    - Without semantic resolution, association is ambiguous
    → SEMANTIC_INTERPRETATION_REQUIRED = TRUE (confirmed in §9)

5. Pre-registered evaluation rule:
    - What distance threshold counts as "near"? (34.5pt? 54.8pt? 100pt?)
    - What x-overlap ratio counts as "aligned"?
    - How to handle multiple extents?
    → Currently: NOT DEFINED (must not auto-define without authorization)
```

---

## 13. Remaining Gaps

```
PRIMARY_BOTTLENECK = EVIDENCE_ORGANIZATION_GAP
  - Visual evidence is now AVAILABLE (DRAWING_EXTENT_FACT)
  - But how to ORGANIZE text-drawing associations is undefined
  - The "Text-Drawing Spatial Association" pattern (§11) is a research hypothesis
  - No consumer has been built to test this pattern
  - No pre-registered rules for proximity thresholds / overlap criteria

SECONDARY_BOTTLENECK = SEMANTIC_INTERPRETATION_GAP
  - Even with perfect organization, "text near drawing" ≠ "caption"
  - MERGE decision requires knowing "is this a caption?"
  - This is a semantic step that Evidence alone cannot answer
  - Requires Hypothesis layer + Human Validation

REMAINING_GAPS:
  1. Negative cases (0 available — must be collected before any experiment)
  2. Boundary cases (untested — multiple drawings, partial overlap)
  3. Independent documents (only 2 docs — need 2+ more)
  4. Pre-registered evaluation rules (undefined — must not auto-define)
  5. Semantic resolution mechanism (caption vs reference vs footnote — needs Hypothesis)
```

---

## 14. Final Decision

```
EVIDENCE_ORGANIZATION_PARTIALLY_TESTABLE
```

### Reasoning

```
PARTIALLY TESTABLE because:

  POSITIVE:
    ✓ Visual evidence is now AVAILABLE (DRAWING_EXTENT_FACT)
    ✓ 3 real cases show diagnostic gain (counterfactual=NO)
    ✓ Diagnostic gain source identified: EXTENT_GAIN (aggregated extent)
    ✓ Repeated mechanism found: "Text-Drawing Spatial Association" pattern
    ✓ Negative controls confirm no false diagnostic value
    ✓ Evidence Organization is now a CONCRETE research object
      (text + geometry + extent + spatial relation → association pattern)

  NOT FULLY TESTABLE because:
    ✗ SEMANTIC_INTERPRETATION_REQUIRED = TRUE
      → "text near drawing" ≠ "caption"
      → MERGE decision needs semantic hypothesis, not just structural evidence
      → Evidence Organization can provide STRUCTURAL evidence, but not SEMANTIC resolution

    ✗ 0 negative cases available
      → Cannot test false-positive rate of any association pattern
      → "FIG." prefix can be caption OR reference — untested

    ✗ Only 2 independent documents
      → 2/3 diagnostic cases from med_001
      → Pattern may be document-specific

    ✗ No pre-registered evaluation rules
      → "near" threshold undefined (34.5pt? 54.8pt?)
      → "x-overlap" criterion undefined
      → Must not auto-define without authorization

  NOT "NOT_YET_TESTABLE" because:
    - Evidence Organization IS now a concrete research object
    - The pattern (text-drawing spatial association) IS observable
    - The diagnostic value IS real (3 counterfactual=NO cases)
    - The bottleneck HAS shifted from "Perception Missing" to "Evidence Organization"

  NOT "NOW_TESTABLE" because:
    - Semantic interpretation is still required for final MERGE decision
    - Negative cases are missing (cannot evaluate false-positive rate)
    - Only 2 documents (insufficient independence)
```

### Bottleneck shift confirmed

```
BEFORE Vector Geometry:
  PRIMARY_BOTTLENECK = PERCEPTION_MISSING (visual content invisible)
  → Could not even observe that drawings exist

AFTER Vector Geometry:
  PRIMARY_BOTTLENECK = EVIDENCE_ORGANIZATION_GAP
  → Can observe drawings, but cannot organize text-drawing associations
  → The problem shifted from "can't see" to "can see but can't organize"

  SECONDARY_BOTTLENECK = SEMANTIC_INTERPRETATION_GAP
  → Even with organization, "caption" is a semantic concept
  → Requires Hypothesis layer + Human Validation

The shift from Perception Missing → Evidence Organization is GENUINE:
  - 3 cases now have structural evidence that was completely invisible before
  - The problem is now about ORGANIZING evidence, not about MISSING evidence
  - This is a more tractable problem type
```

---

## 15. Governance Status

```text
EVIDENCE_ORGANIZATION_GAP_DIAGNOSTIC = COMPLETE

EVIDENCE_ORGANIZATION_STATUS = PARTIALLY_TESTABLE

PRIMARY_BOTTLENECK = EVIDENCE_ORGANIZATION_GAP
  Visual evidence available, but text-drawing association organization undefined

SECONDARY_BOTTLENECK = SEMANTIC_INTERPRETATION_GAP
  "text near drawing" ≠ "caption" — semantic hypothesis still needed

REMAINING_GAPS:
  1. Negative cases (0 available)
  2. Boundary cases (untested)
  3. Independent documents (only 2)
  4. Pre-registered evaluation rules (undefined)
  5. Semantic resolution mechanism (needs Hypothesis)

DIAGNOSTIC_GAIN_SOURCE = EXTENT_GAIN
  DRAWING_EXTENT_FACT (aggregated extent) is the key diagnostic contributor
  DRAWING_GEOMETRY_FACT (individual primitives) provides supporting but non-diagnostic evidence

EVIDENCE_ORGANIZATION_PATTERN = "Text-Drawing Spatial Association" (research hypothesis)
  Conditions: FIG-prefix + near extent + x-align + MERGE failure type
  NOT implemented, NOT a detector, NOT a classifier

SEMANTIC_INTERPRETATION_REQUIRED = TRUE
  Structural evidence is NECESSARY but NOT SUFFICIENT for MERGE decision
  "caption_of" is a semantic relation, not a spatial relation

M_A_READINESS:
  VISUAL_REGION_EVIDENCE = AVAILABLE (was MISSING)
  SAFE_ALGORITHM_ROUTE = NOT_CURRENTLY_AVAILABLE (still needs negative cases + rules)
  M-A may become testable IF:
    - negative cases collected
    - pre-registered rules defined
    - independent documents added
    - semantic gap accepted (Human Validation)

AO_VISUAL_GEOMETRY = IMPLEMENTED (COMPLETE)
AO_VALUE_EXPERIMENT = COMPLETE (VALUE_PARTIALLY_SUPPORTED)
EVIDENCE_ORGANIZATION_DIAGNOSTIC = COMPLETE (PARTIALLY_TESTABLE)

FROZEN_BASELINE = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d, P1=74d23ec7)
P1_P6 = UNCHANGED
P7.1 = UNCHANGED
TLD = UNCHANGED
IS-11 = UNCHANGED (FROZEN, not modified)
IS-14 = UNCHANGED

CAPABILITY = UNCHANGED
RUNTIME_AUTHORITY = ZERO
PRODUCTION = FALSE

IMPLEMENTATION = NOT AUTHORIZED
EXPERIMENT_IMPLEMENTATION = NOT AUTHORIZED

STOP = TRUE
```

---

## Research Principle Adherence

- ✅ Only analyzed 3 core cases + 6 negative controls (no new case selection)
- ✅ E0/E1/E0+A/E0+B/E0+A+B decomposition performed
- ✅ Identified EXTENT_GAIN as diagnostic source (not GEOMETRY_PRIMITIVE_GAIN)
- ✅ Confirmed SEMANTIC_INTERPRETATION_REQUIRED = TRUE
- ✅ Did NOT smuggle "caption" conclusion from "FIG." prefix
- ✅ Negative controls explained (drawing exists ≠ diagnostic value)
- ✅ Repeated mechanism identified as research hypothesis (not implementation)
- ✅ M-A readiness assessed honestly (AVAILABLE but NOT_CURRENTLY_AVAILABLE)
- ✅ Did NOT output threshold/classifier/rule/algorithm
- ✅ Did NOT implement Evidence Organization
- ✅ Did NOT implement M-A
- ✅ Did NOT modify any code/AO/P1-P7/TLD/IS-11
- ✅ Frozen baseline intact

`STOP = TRUE`.
