# M-A Evidence Sufficiency Gap Diagnostic

> **模式: READ-ONLY DIAGNOSTIC / NO MODIFICATION / FROZEN INTACT / STOP**
> 日期: 2026-09-17
> 前置: M-A Human Validation Pilot Analysis (14 UNCERTAIN, 9 Evidence Insufficiency)
> 本文件: 诊断 9 个 Evidence Insufficiency 案例的具体瓶颈层级。

---

## 1. Executive Summary

```
The previous pilot analysis classified 9 of 14 UNCERTAIN cases as "Evidence
Insufficiency" — 7 with no drawing extent and 2 with short text.

This diagnostic re-examines each case against the actual Drawing Geometry Fact
(DGF) and Drawing Extent Fact (DEF) data, and finds that the original
classification was imprecise. The 9 cases break down into THREE different
gap types:

  OBSERVATION_COVERAGE_GAP:                      2 cases
    → No visual content on page at all (DGF=0, NTB=0, images=0)
    → Text is a cross-page reference; figure is on another page

  EVIDENCE_ORGANIZATION_GAP:                     3 cases
    → Vector primitives exist (DGF>0) but no extent formed (DEF=0)
    → Primitives are too small/scattered or are page structure elements
    → Aggregation parameters filtered them out

  EVIDENCE_SUFFICIENT_BUT_CURRENT_PACK_INCOMPLETE: 4 cases
    → Evidence EXISTS (extent on page, or same_y context available)
    → But the Evidence Pack did not show it to Human
    → 2 cases: extent exists on page but was not shown (Type A excluded)
    → 2 cases: same_y context can reconstruct full text but was not shown

This means:
  - Only 2 of 9 cases are true Observation Coverage Gaps (nothing to observe)
  - 3 cases are Organization Gaps (primitives exist but aggregation missed them)
  - 4 cases have sufficient evidence that was not presented to Human
  - 0 cases are Semantic Boundary (all 9 are evidence/packaging issues)

The primary bottleneck is NOT "missing observation" but
"existing evidence not organized/presented to Human".
```

---

## 2. Research Question

> 这 9 个 UNCERTAIN 到底为什么无法形成足够的 Evidence？缺失发生在哪一层？

```
Layer 1 — Observation:    有没有事实被观察到？
Layer 2 — Organization:   已有事实有没有被组织成可理解的 Evidence？
Layer 3 — Semantic:       Evidence 是否仍不足以回答 Association 问题？
```

---

## 3. Input / Frozen Baseline

```
Source data:
  tmp/m_a_human_validation_pilot_case_analysis.csv (79 cases)
  tmp/m_a_human_review_pilot/data/candidates_internal.json (case metadata)
  tmp/m_a_human_review_pilot/data/human_session_1.json (Human judgments)

Observation surfaces (READ-ONLY):
  P1 atomic_text.py (sha=74d23ec784d65782, FROZEN)
  DRAWING_GEOMETRY_FACT (sha=f25a5ff41afa1bec, IMPLEMENTED)
  DRAWING_EXTENT_FACT (sha=cba9e583517f8967, IMPLEMENTED)

Frozen baseline: INTACT (drift=0/4)
Human data: UNCHANGED
M-A algorithm: UNCHANGED
```

---

## 4. 9 Target Cases

| # | case_id | document | page | text | UNCERTAIN reason (original) |
|---|---------|----------|------|------|---------------------------|
| 1 | is11_efficientnet_p3_319_69 | efficientnet | 3 | Figure | No extent on page |
| 2 | is11_efficientnet_p4_66_331 | efficientnet | 4 | Figure | No extent on page |
| 3 | is11_med_001_p18_325_655 | med_001 | 18 | Figure | No extent on page |
| 4 | is11_efficientnet_p2_158_372 | efficientnet | 2 | Figure | No extent on page |
| 5 | is11_med_001_p15_498_107 | med_001 | 15 | figure | No extent on page |
| 6 | is11_efficientnet_p6_79_415 | efficientnet | 6 | omit | Text too short |
| 7 | is11_resnet_p7_321_545 | resnet | 7 | Fig. 6 (middle) shows... | No extent on page |
| 8 | arxiv_2402.18619_p11_72_651 | arxiv_2402 | 11 | Fig. 3a that connects... | No extent on page |
| 9 | is11_med_001_p15_244_342 | med_001 | 15 | max | Text too short |

```
N = 9 (verified from CSV)
```

---

## 5. Drawing Observation Availability

### Critical Finding: "No Extent" ≠ "No Drawing"

```
For the 7 "no extent" cases, DGF was checked on each page:

  Case                              DGF    DEF    Raw Drawing?
  is11_efficientnet_p3_319_69         4      0    YES (4 stroke primitives)
  is11_efficientnet_p4_66_331       141      2    YES (141 primitives, 2 extents!)
  is11_med_001_p18_325_655            0      0    NO (nothing on page)
  is11_efficientnet_p2_158_372      233      0    YES (233 primitives)
  is11_med_001_p15_498_107        12338      1    YES (12338 primitives, 1 extent!)
  is11_resnet_p7_321_545             53      0    YES (53 stroke primitives)
  arxiv_2402.18619_p11_72_651         0      0    NO (nothing on page)

  DGF=0 (truly no drawing):     2 cases (#3, #8)
  DGF>0 (drawing exists):       5 cases (#1, #2, #4, #5, #7)

  Of the 5 with DGF>0:
    DEF=0 (no extent formed):   3 cases (#1, #4, #7)
    DEF>0 (extent exists!):     2 cases (#2, #5) ← Evidence Pack said "no extent" but extent EXISTS
```

### Raster Image Check

```
All 7 pages checked for raster blocks (NTB) and embedded images:
  ALL 7 pages: raster_blocks=0, embedded_images=0

  → No raster figures on any of these pages
  → The referenced figures are vector drawings on OTHER pages
  → Or the page is pure text (cases #3, #8)
```

---

## 6. Drawing Extent Availability

```
For the 7 "no extent" cases:

  DEF=0 confirmed:  5 cases (#1, #3, #4, #7, #8)
  DEF>0 FOUND:      2 cases (#2, #5) ← EXTENT EXISTS but was NOT shown to Human

Case #2 (efficientnet p4):
  DGF=141, DEF=2 (two extents formed on page)
  Text "Figure" is Type A negative (>60pt from any extent)
  → Evidence Pack showed "no drawing region" because candidate generation
    excluded this case (not near any extent)
  → But extents DO exist on the page — Human was not shown them
  → GAP: Evidence Pack incomplete (showed "no extent" when extent exists)

Case #5 (med_001 p15):
  DGF=12338, DEF=1 (one extent formed on page)
  Text "figure" is Type A negative (>60pt from extent)
  → Same issue: extent exists but Evidence Pack showed "no drawing region"
  → GAP: Evidence Pack incomplete
```

---

## 7. Evidence Organization Analysis

### 3 cases where DGF>0 but DEF=0 (primitives exist, no extent formed)

```
Case #1 (efficientnet p3): 4 primitives, all strokes
  → 4 horizontal lines, 0pt height, spread across 82% of page
  → These are page separators/decoration, NOT drawing content
  → min_height=10 filter excluded them (height=0)
  → Correct exclusion: these are not drawings

Case #4 (efficientnet p2): 233 primitives (f, fs, s)
  → 121 fill-stroke, 64 fill, 48 stroke
  → 8 horizontal + 8 vertical lines (>50pt)
  → Y-spread: 24% of page (concentrated in upper page)
  → Text is in lower page, 0 primitives within 100pt
  → Large vector content exists but did not form extent
  → POSSIBLE aggregation parameter issue (primitives may be too scattered
    or below area threshold)
  → DESIGN_GAP: needs investigation (not implementation)

Case #7 (resnet p7): 53 primitives, all strokes
  → 53 stroke primitives, 10 horizontal lines (page-wide)
  → All small (median 0pt width, 12pt height)
  → These are table borders / page structure, NOT drawing content
  → min_width=15 filter excluded most
  → Correct exclusion: these are not drawings
```

### Summary

```
Of 3 EVIDENCE_ORGANIZATION_GAP cases:
  #1: Correct exclusion (page separators, not drawings)
  #4: Possible aggregation gap (233 primitives, no extent — needs investigation)
  #7: Correct exclusion (table borders, not drawings)

  → Only #4 is a potential true organization gap
  → #1 and #7 are correctly excluded (primitives are not drawing content)
  → But the TEXT is still a cross-page reference in all 3 cases
```

---

## 8. Short-Text Cases

### Case #6: "omit" (efficientnet p6)

```
Target atom: text="omit", bbox=[79.5, 414.8, 94.7, 423.1]
  → P1 fine-grained atom (split from longer text)

Same-y context (P2 same_y_band, 30 atoms at y=414.8):
  "We" "omit" "ensemble" "and" "multi-crop" "models" "(Hu..."

Reconstructed: "We [omit] ensemble and multi-crop models (Hu..."

Analysis:
  → "omit" is body text, NOT a figure label
  → Same_y context (P2) CAN reconstruct the full sentence
  → The Evidence Pack DID have a context_text field, but it was empty
  → P2 same_y context was available but not populated for Type B negatives

Drawing extent on page: 1 extent exists [307, 445, 532, 625]
  → Text is 21.9pt from extent, x-overlap=False
  → Text is body text near a drawing but NOT associated with it

EVIDENCE_SUFFICIENT_BUT_CURRENT_PACK_INCOMPLETE:
  → If Evidence Pack showed same_y context ("We [omit] ensemble..."),
    Human could determine this is body text → NO judgment
  → The evidence EXISTS (P2 same_y) but was NOT presented
```

### Case #9: "max" (med_001 p15)

```
Target atom: text="max", bbox=[359.1, 90.6, 374.8, 98.5]
  → P1 fine-grained atom

Same-y context (30 atoms at y=85.7-98.5):
  "stemming" "from" "the" "Coulomb" "matrix" "denoted" "as" "CM(" "ϵ" "max" ","

Reconstructed: "stemming from the Coulomb matrix denoted as CM(ϵ, [max], ..."

Analysis:
  → "max" is a mathematical variable in body text
  → Same_y context reconstructs the full mathematical expression
  → Evidence Pack context_text was empty

Drawing extent on page: 1 extent exists [123, 382, 525, 527]
  → Text is 284pt from extent (very far)
  → Text is mathematical notation, NOT a figure label

EVIDENCE_SUFFICIENT_BUT_CURRENT_PACK_INCOMPLETE:
  → If Evidence Pack showed same_y context ("CM(ϵ, [max], ...)"),
    Human could determine this is math notation → NO judgment
  → The evidence EXISTS (P2 same_y) but was NOT presented
```

---

## 9. Case-Level Diagnosis

| case_id | page | text | DGF | DEF | drawing_exists | extent_exists | neighboring_context | evidence_sufficient | primary_gap | counterfactual |
|---------|------|------|-----|-----|----------------|---------------|---------------------|---------------------|-------------|----------------|
| efficientnet p3 | 3 | Figure | 4 | 0 | YES | NO | Page separators, not drawing | NO | EVIDENCE_ORGANIZATION_GAP | NO |
| efficientnet p4 | 4 | Figure | 141 | 2 | YES | YES | Extent exists but not shown to Human | PARTIAL | EVIDENCE_SUFFICIENT_BUT_PACK_INCOMPLETE | YES |
| med_001 p18 | 18 | Figure | 0 | 0 | NO | NO | Pure text page, cross-page ref | NO | OBSERVATION_COVERAGE_GAP | NO |
| efficientnet p2 | 2 | Figure | 233 | 0 | YES | NO | Large vector content, no extent formed | PARTIAL | EVIDENCE_ORGANIZATION_GAP | UNKNOWN |
| med_001 p15 | 15 | figure | 12338 | 1 | YES | YES | Extent exists but not shown to Human | PARTIAL | EVIDENCE_SUFFICIENT_BUT_PACK_INCOMPLETE | YES |
| efficientnet p6 | 6 | omit | 0 | 1 | NO | YES | Same_y: "We omit ensemble..." | PARTIAL | EVIDENCE_SUFFICIENT_BUT_PACK_INCOMPLETE | YES |
| resnet p7 | 7 | Fig. 6 shows... | 53 | 0 | YES | NO | Table borders, not drawing | NO | EVIDENCE_ORGANIZATION_GAP | NO |
| arxiv p11 | 11 | Fig. 3a connects... | 0 | 0 | NO | NO | Pure text page, cross-page ref | NO | OBSERVATION_COVERAGE_GAP | NO |
| med_001 p15 | 15 | max | 12338 | 1 | YES | YES | Same_y: "CM(ϵ, max, ...)" | PARTIAL | EVIDENCE_SUFFICIENT_BUT_PACK_INCOMPLETE | YES |

---

## 10. Observation vs Organization vs Semantic Boundary

```
Layer 1 — Observation Coverage Gap: 2 cases
  #3 (med_001 p18): DGF=0, NTB=0, images=0 → nothing to observe
  #8 (arxiv p11): DGF=0, NTB=0, images=0 → nothing to observe
  → Both are pure text pages with cross-page references
  → The referenced figures are on other pages
  → No amount of aggregation or organization can help

Layer 2 — Evidence Organization Gap: 3 cases
  #1 (efficientnet p3): 4 primitives (page separators) → correctly excluded
  #4 (efficientnet p2): 233 primitives → no extent formed (possible aggregation gap)
  #7 (resnet p7): 53 primitives (table borders) → correctly excluded
  → #1 and #7: primitives are NOT drawing content (correct exclusion)
  → #4: large vector content exists but aggregation did not form extent
  → Even if extent formed, text is a cross-page reference in all 3 cases

Layer 2b — Evidence Pack Incomplete: 4 cases
  #2 (efficientnet p4): extent EXISTS on page but not shown (Type A excluded)
  #5 (med_001 p15): extent EXISTS on page but not shown (Type A excluded)
  #6 (efficientnet p6): same_y context available but not shown (context_text empty)
  #9 (med_001 p15): same_y context available but not shown (context_text empty)
  → Evidence EXISTS but was not presented to Human
  → Fixable by Evidence Pack redesign (show all extents + same_y context)

Layer 3 — Semantic Boundary: 0 cases
  → None of the 9 cases are genuine semantic ambiguity
  → All 9 are evidence/packaging issues, not interpretation limits
```

---

## 11. Counterfactual Human Judgment

```
If the missing evidence were available, could Human make a judgment?

  YES (evidence would suffice): 4 cases
    #2: If Human saw existing extent → could judge NO (text far from drawing)
    #5: If Human saw existing extent → could judge NO (text far from drawing)
    #6: If Human saw same_y context ("We omit ensemble...") → could judge NO (body text)
    #9: If Human saw same_y context ("CM(ϵ, max, ...)") → could judge NO (math notation)

  NO (even with evidence, cannot judge): 4 cases
    #1: Primitives are page separators, not drawing → cross-page reference
    #3: No drawing on page → cross-page reference
    #7: Primitives are table borders → cross-page reference
    #8: No drawing on page → cross-page reference
    → These are cross-page references; the figure is on ANOTHER page
    → Even with perfect evidence on THIS page, Human cannot judge association
      because the drawing is not here

  UNKNOWN: 1 case
    #4: 233 primitives exist but no extent formed
    → If extent formed, Human could see the drawing
    → But text may still be a cross-page reference
    → Cannot determine without seeing the formed extent
```

---

## 12. Evidence Sufficiency Findings

### Finding 1: "No Extent" was misleading

```
The original pilot analysis said "7 cases have no drawing extent."
Actual finding:
  - 2 cases: truly no drawing (DGF=0) → Observation Coverage Gap
  - 3 cases: primitives exist but no extent (DGF>0, DEF=0) → Organization Gap
  - 2 cases: extent EXISTS but was not shown (DEF>0) → Pack Incomplete

  Only 2 of 7 "no extent" cases are true Observation Coverage Gaps.
  5 of 7 have some form of drawing evidence on the page.
```

### Finding 2: Short text was solvable with same_y context

```
Both "omit" and "max" are P1 fine-grained atoms.
P2 same_y_band can reconstruct the full sentence:
  "We [omit] ensemble and multi-crop models..."
  "CM(ϵ, [max], ...)"

The context_text field in the Evidence Pack was EMPTY for Type B negatives.
If same_y context had been shown, Human could have determined:
  → "omit" = body text → NO (not associated)
  → "max" = math notation → NO (not associated)

This is NOT a semantic boundary. It is an Evidence Pack completeness gap.
```

### Finding 3: No Semantic Boundary in these 9 cases

```
All 9 cases are evidence/packaging issues:
  - 2 Observation Coverage Gap (nothing to observe)
  - 3 Evidence Organization Gap (primitives not forming extent)
  - 4 Evidence Pack Incomplete (evidence exists but not shown)

  0 cases are Semantic Boundary.
  → The 5 Semantic Boundary cases are in the OTHER 5 UNCERTAIN (not these 9)
  → These 9 are all fixable through evidence improvement, not semantic resolution
```

---

## 13. Revised Bottleneck

```
ORIGINAL (from pilot analysis):
  "64% of UNCERTAIN is Evidence Insufficiency"
  → Implied: these cases lack evidence

REVISED (this diagnostic):
  Evidence Insufficiency breaks down into:
    OBSERVATION_COVERAGE_GAP:                    2/9 (22%)
    EVIDENCE_ORGANIZATION_GAP:                   3/9 (33%)
    EVIDENCE_SUFFICIENT_BUT_CURRENT_PACK_INCOMPLETE: 4/9 (44%)

  → Only 22% are true observation gaps (nothing to observe)
  → 33% are organization gaps (primitives exist but no extent)
  → 44% have SUFFICIENT evidence that was NOT presented to Human

PRIMARY_CURRENT_BOTTLENECK = EVIDENCE_PACK_COMPLETENESS
  → 4 of 9 cases could be resolved by showing existing evidence
  → This does NOT require new observation or algorithm change
  → Only requires Evidence Pack redesign (show all extents + same_y context)

SECONDARY_CURRENT_BOTTLENECK = CROSS_PAGE_REFERENCE_HANDLING
  → 4 of 9 cases are cross-page references (figure on another page)
  → Current system has no mechanism to link text to drawings on other pages
  → This is a known limitation (single-page scope of DRAWING_EXTENT_FACT)
  → Addressing this would require cross-page Evidence Organization (DESIGN_GAP)
```

---

## 14. Research Implications

```
1. Evidence Pack redesign could resolve 4/9 UNCERTAIN:
  → Show ALL extents on page (not just nearest)
  → Show same_y context for ALL cases (including Type B negatives)
  → This is a UI/Pack design change, NOT an algorithm change
  → DESIGN_GAP: recorded, NOT implemented

2. Aggregation parameter investigation needed for 1 case (#4):
  → 233 primitives did not form extent
  → May need parameter review (but NOT threshold tuning)
  → DESIGN_GAP: recorded, NOT implemented

3. Cross-page reference handling is a known limitation:
  → 4 cases reference figures on other pages
  → Current DRAWING_EXTENT_FACT is single-page scope
  → Cross-page organization is a future design question
  → DESIGN_GAP: recorded, NOT implemented

4. P1 atom splitting is NOT the primary issue:
  → Only affects 2 cases (#6, #9)
  → P2 same_y can reconstruct context without P1 change
  → Confirms G2 finding: P1 modification NOT_REQUIRED
```

---

## 15. What Is NOT Demonstrated

```
This diagnostic does NOT demonstrate:
  ✗ M-A has solved Evidence Sufficiency
  ✗ All UNCERTAIN cases are fixable
  ✗ Cross-page references can be resolved
  ✗ Aggregation parameters are wrong
  ✗ The 4 "Pack Incomplete" cases would definitely become NO
    (counterfactual = YES means "could judge", not "would judge NO")

This diagnostic DOES demonstrate:
  ✓ The 9 "Evidence Insufficiency" cases are NOT all the same type
  ✓ 4 cases have existing evidence not presented to Human
  ✓ 2 cases are true observation gaps (pure text pages)
  ✓ 3 cases have primitives that didn't form extents (2 correctly excluded)
  ✓ 0 cases are Semantic Boundary
  ✓ The bottleneck is Evidence Pack completeness, not observation coverage
```

---

## 16. Governance Check

```
FROZEN_BASELINE = INTACT (drift=0/4)
  P1: 74d23ec784d65782 (UNCHANGED)
  TLD: 022f5c21e872ad9e (UNCHANGED)
  GT: 7349963d0d23b5ef (UNCHANGED)
  layout_analyzer: 8f69f0d206b3e565 (UNCHANGED)

DRAWING_GEOMETRY_FACT: f25a5ff41afa1bec (UNCHANGED)
DRAWING_EXTENT_FACT: cba9e583517f8967 (UNCHANGED)

HUMAN_VALIDATION_DATA: UNCHANGED
M-A_ALGORITHM: UNCHANGED
P1: UNCHANGED
P2: UNCHANGED
P6: UNCHANGED
AO: UNCHANGED

No code modified.
No data modified.
No thresholds changed.
No aggregation parameters changed.
No Evidence Pack modified.
No Human Validation re-run.

DESIGN_GAPS recorded (NOT implemented):
  1. Evidence Pack should show ALL extents on page (not just nearest)
  2. Evidence Pack should show same_y context for ALL cases
  3. Case #4 aggregation parameter investigation needed
  4. Cross-page reference handling (future design question)
```

---

## 17. Final Decision

```
DIAGNOSTIC_STATUS = COMPLETE

6 QUESTIONS ANSWERED:

Q1: How many of 7 "no extent" cases are truly no drawing observation?
  → 2 (med_001 p18, arxiv p11: DGF=0, NTB=0, images=0)

Q2: How many have primitives but no extent?
  → 3 (efficientnet p3: 4 primitives; efficientnet p2: 233; resnet p7: 53)
  → Of these, 2 are correctly excluded (page separators / table borders)
  → 1 is a possible aggregation gap (233 primitives, no extent)

Q3: Are the 2 short-text cases evidence gaps or context-solvable?
  → Context-solvable: both "omit" and "max" have same_y context
    that reconstructs the full sentence
  → EVIDENCE_SUFFICIENT_BUT_CURRENT_PACK_INCOMPLETE

Q4: How many are Observation Coverage Gap?
  → 2

Q5: How many are Evidence Organization Gap?
  → 3

Q6: How many are Semantic Boundary?
  → 0

PRIMARY_CURRENT_BOTTLENECK = EVIDENCE_PACK_COMPLETENESS
  4/9 cases have existing evidence not shown to Human

SECONDARY_CURRENT_BOTTLENECK = CROSS_PAGE_REFERENCE_HANDLING
  4/9 cases reference figures on other pages (single-page scope limitation)

IMPLEMENTATION_AUTHORIZED = FALSE
EXPERIMENT_AUTHORIZED = FALSE
HUMAN_VALIDATION_AUTHORIZED = FALSE

STOP = TRUE
```

---

## Research Principle Adherence

- ✅ Read raw DGF/DEF data for each page (not trusted previous summary)
- ✅ Checked raster blocks (NTB) and embedded images
- ✅ Checked P2 same_y context for short-text cases
- ✅ Distinguished Observation / Organization / Pack / Semantic layers
- ✅ Did NOT modify any code or data
- ✅ Did NOT modify aggregation parameters
- ✅ Did NOT modify Evidence Pack
- ✅ Did NOT modify thresholds
- ✅ Did NOT re-run Human Validation
- ✅ Did NOT claim Semantic Boundary (0 cases)
- ✅ Did NOT claim M-A solved
- ✅ Recorded DESIGN_GAPS without implementing
- ✅ Frozen baseline intact (drift=0)
- ✅ STOP = TRUE

`STOP = TRUE`.
