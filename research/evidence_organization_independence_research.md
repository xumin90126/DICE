# Evidence Organization Independence Research

> **模式: READ-ONLY DIAGNOSTIC RESEARCH / NO IMPLEMENTATION / FROZEN INTACT / STOP**
> 日期: 2026-09-17
> 前置: `tmp/evidence_organization_gap_diagnostic.md`（PARTIALLY_TESTABLE, EXTENT_GAIN, 3 diagnostic cases）
> 本文件研究: DRAWING_EXTENT_FACT 的 Evidence Organization 价值是否具有跨文档独立性，以及纯几何 Organization 与 Semantic Interpretation 的边界。

---

## 1. Research Question

> DRAWING_EXTENT_FACT 所体现的 Evidence Organization 价值，是否具有跨文档、跨案例的独立研究价值？
>
> 纯几何 Evidence Organization 能够走到哪里，在哪个边界开始必须进入 Semantic Interpretation？

---

## 2. Existing Evidence Surface

```
Available Observation Surfaces (after AO Visual Geometry Extension):

  P1 TEXT_ATOM (frozen):
    - text content (lexical: "FIG.", "Figure", "Table" prefix detectable)
    - bbox

  P2 GeometryObservation (frozen):
    - same_y_band, h_gap, v_gap, left_alignment_group
    - text-text pairwise geometry

  DRAWING_GEOMETRY_FACT (implemented):
    - per-primitive: drawing_id, bbox, draw_type, item_count, item_types
    - ALL primitives (no pre-filter)

  DRAWING_EXTENT_FACT (implemented):
    - aggregated: extent_id, bbox, width, height, area, primitive_count, constituent_seqnos
    - 3-stage geometric pipeline (12 params)

  Consumer-computed (NOT stored):
    - text-extent distance (bbox arithmetic)
    - text-extent x-overlap (bbox arithmetic)
    - text-extent containment (bbox arithmetic)
```

---

## 3. Primitive vs Extent Contribution

### E0+A (primitives only, no extent) — from previous diagnostic

```
Case AMB-414: 235 primitives, 149 within 100pt of text_a → PARTIAL
Case AMB-422: 635 primitives, 208 within 100pt of text_a → PARTIAL
Case EXT-P28: 216 primitives, 204 within 100pt of text_a → PARTIAL

PRIMITIVE_ONLY = INSUFFICIENT (all 3 cases)

Reason:
  Individual primitives show scattered proximity but cannot form
  "text is near the drawing AS A WHOLE". 149 primitives within 100pt
  includes page decorations, table borders, equation lines — noise.
  Cannot distinguish "text near figure" from "text near scattered lines".
```

### E0+B (extent only) — from previous diagnostic

```
Case AMB-414: 1 extent, text_a 34.5pt below, x-overlap=TRUE → YES
Case AMB-422: 1 extent, text_a 54.8pt below, x-overlap=FALSE → YES
Case EXT-P28: 1 extent, text_a 17.2pt above, x-overlap=TRUE → YES

EXTENT_CONTRIBUTION = ESSENTIAL (all 3 cases)

Reason:
  The aggregated extent provides a single bbox representing "the drawing as a whole".
  text-extent distance + x-overlap = structured, diagnosable spatial relation.
  This is what transforms "149 scattered primitives" into "text 34.5pt below a 16-primitive extent".
```

### Summary

| Case | PRIMITIVE_ONLY | EXTENT_CONTRIBUTION | Gain Source |
|------|---------------|---------------------|-------------|
| AMB-414 | INSUFFICIENT | ESSENTIAL | EXTENT_GAIN |
| AMB-422 | INSUFFICIENT | ESSENTIAL | EXTENT_GAIN |
| EXT-P28 | INSUFFICIENT | ESSENTIAL | EXTENT_GAIN |

---

## 4. Cross-Document Analysis

### Survey: ALL 5 available PDFs scanned for vector drawings

```
Document           Pages  Primitives  Extents  Pages w/ drawings  Pages w/ extents
is11_med_001        29     38928       12       18/29              11/29
is11_resnet         12      1364        6       11/12               6/12
is11_efficientnet   11      1332        6       11/11               5/11
is11_cs_001          8       660        3        6/8                3/8
arxiv_2402.18619    35      5207       23       29/35              13/35

ALL 5 documents have vector drawings.
ALL 5 documents have aggregated extents.
```

### Text-Drawing Spatial Relationships (pure geometric)

```
50 text-near-extent instances across 5 documents
9257 total text atoms near extents
Average: 185.1 text atoms per extent

  → "text near drawing" is pervasive — nearly every page with a drawing
     has 100-400 text atoms within 60pt of the extent
  → Pure geometric proximity is NOT discriminating
```

### Q1: Is Text-Drawing Spatial Association only in med_001?

```
NO — pattern is cross-document

  med_001:        12 text-near-extent instances
  arxiv_2402:     23 text-near-extent instances
  resnet:          6 text-near-extent instances
  efficientnet:    6 text-near-extent instances
  cs_001:          3 text-near-extent instances

  ALL 5 documents have text near drawing extents.
  The pattern is NOT med_001-specific.
```

### Q2: Does EXT-P28 represent the same mechanism?

```
YES — same mechanism

  EXT-P28 (arxiv_2402 p28):
    - 216 primitives, 1 extent, text "Fig. 14" near extent
    - Same pattern: FIG-prefix text + drawing extent + spatial proximity
    - Different document from med_001 → cross-document confirmation

  Additionally, arxiv_2402 has 22 OTHER text-near-extent instances
  with FIG-prefix texts (Fig. 2, Fig. 3, Fig. 4, ... Fig. 15)
  → The pattern is richly present across multiple pages of arxiv_2402
```

### Q3: Other documents with vector drawing but NO caption/association failure?

```
YES — natural negative controls exist

  resnet p6: drawing extent + text "28.54" near extent (17.5pt)
    → text is TABLE CELL content, NOT caption
    → has drawing + near text, but NO FIG-prefix, NO association failure
    → Natural negative: "drawing near text without FIG-prefix"

  efficientnet p7: drawing extent + text "Food-101" near extent (52pt)
    → text is TABLE content, NOT caption
    → Natural negative: "drawing near table text"

  arxiv_2402 p12: drawing extent + text "σ" near extent (2.8pt)
    → text is EQUATION symbol inside drawing
    → Natural negative: "text inside drawing (equation label, not caption)"
```

### Q4: Can these serve as natural negative controls?

```
YES — 280 FIG-prefix texts NOT near extent are natural negatives

  These are references ("see Fig. 3", "in Figure 5") that have FIG-prefix
  but are NOT spatially near a drawing extent.

  They demonstrate:
    - FIG-prefix alone is NOT sufficient (69% of FIG-prefix texts are references)
    - Need FIG-prefix + spatial proximity to extent
    - 280 natural negative cases (previously 0 negative cases available)

  PLUS: 9257 text atoms near extents without FIG-prefix
    → "text near drawing without FIG-prefix" = 9257 natural negatives
    → These are body text, table cells, equations near drawings
    → Demonstrate: proximity alone is NOT sufficient
```

---

## 5. Natural Negative Controls

```
TWO types of natural negative controls discovered:

Type A: FIG-prefix WITHOUT proximity (280 cases)
  - Text has "FIG." / "Figure" / "Table" prefix
  - Text is NOT within 60pt of any drawing extent
  - These are in-text references: "see Fig. 3", "as shown in Figure 5"
  → Proves: FIG-prefix alone ≠ caption (69% are references)

Type B: Proximity WITHOUT FIG-prefix (9257 cases)
  - Text is within 60pt of a drawing extent
  - Text does NOT have "FIG." / "Figure" / "Table" prefix
  - These are body text, table cells, equations, labels near drawings
  → Proves: proximity alone ≠ caption (185 texts per extent = noise)

Combined positive: FIG-prefix + proximity (126 cases)
  - Text has FIG-prefix AND is within 60pt of drawing extent
  - These are potential caption candidates
  → 126/406 = 31% of FIG-prefix texts are near extents
  → This is the discriminating combination
```

### Negative control value

```
PREVIOUS STATE (from evidence_organization_gap_diagnostic.md):
  "0 negative cases available — must be collected before any experiment"

CURRENT STATE:
  280 Type A negatives (FIG-prefix without proximity)
  9257 Type B negatives (proximity without FIG-prefix)
  → Natural negatives are ABUNDANT and cross-document

This is a significant readiness improvement:
  from "0 negative cases" to "280 + 9257 natural negatives"
```

---

## 6. Geometry-Only Organization

### Test: Without FIG-prefix or any lexical signal

```
Question: Can pure geometric evidence (text near extent) form a meaningful
Evidence Organization relation?

Data:
  50 text-near-extent instances across 5 documents
  Average 185.1 text atoms per extent
  Maximum: 383 text atoms near one extent (efficientnet p7)

Analysis:
  If "text near extent (< 60pt)" is the organization rule:
    → Every extent has ~185 text atoms "associated" with it
    → This includes body text, table cells, equations, page numbers, labels
    → 185 associations per extent is NOT a meaningful organization — it's noise

  Pure geometric proximity does NOT distinguish:
    - caption (should associate) from body text (should not)
    - table cell (should not) from caption (should)
    - equation label (should not) from caption (should)
    - page number (should not) from caption (should)

PURE_GEOMETRIC_ORGANIZATION = NOT_DEMONSTRATED

Reason:
  185 text atoms per extent = noise level
  Pure geometric proximity has NO discriminating power
  Cannot form meaningful Evidence Organization from geometry alone
```

---

## 7. Geometry + Lexical Observation

### Test: Add FIG-prefix as P1 lexical observation (not semantic label)

```
Question: Does adding FIG-prefix lexical signal help Evidence Organization
or does it start承担 Semantic Interpretation?

Data:
  406 total FIG/Table-prefix texts across 5 documents
  126 near extent (31%) — potential captions
  280 not near extent (69%) — likely references

Analysis:
  With FIG-prefix filter:
    → 126 candidates instead of 9257 (98.6% reduction)
    → This IS meaningful discrimination
    → FIG-prefix + proximity = discriminating combination

  BUT: FIG-prefix is a LEXICAL observation, not a geometric one:
    - "FIG." is detected from P1 text content (string matching)
    - It is NOT a geometric fact (not bbox/distance/overlap)
    - It is NOT a semantic label (P1 doesn't classify "this is a caption")
    - It IS a lexical pattern (text starts with "FIG" / "Figure" / "Table")

  Is FIG-prefix helping Organization or Interpretation?
    → It helps ORGANIZATION: it narrows the candidate set from 9257 to 126
    → It does NOT do INTERPRETATION: it doesn't say "this IS a caption"
    → "FIG." prefix can be caption OR reference (31% vs 69%)
    → The lexical signal is a FILTER, not a CLASSIFIER

  ORGANIZATION_SUPPORT = TRUE (narrows candidates)
  INTERPRETATION_SUPPORT = FALSE (doesn't classify as caption)

  → FIG-prefix is ORGANIZATION_SUPPORT
  → It is a lexical observation used for Evidence Organization
  → It does NOT cross into Semantic Interpretation
  → BUT: the final "is this a caption?" decision still needs Interpretation
```

### Comparison

```
Geometry only:       9257 candidates → NOT discriminating → NOT_DEMONSTRATED
Geometry + lexical:  126 candidates → discriminating → PARTIALLY_SUPPORTED

The lexical signal is ESSENTIAL for meaningful organization.
Without it, geometry alone produces noise (185 texts per extent).
With it, the candidate set narrows to 126 (31% of FIG-prefix texts).

But 126 is still not "caption identified":
  - Some of the 126 may be references that happen to be near a drawing
  - Some may be table captions (near a table drawing, not figure)
  - The final "is this a caption?" still requires Semantic Interpretation
```

---

## 8. Organization / Interpretation Boundary

### Three-layer boundary for each fact type

```
Layer 1 — Observation (pure facts, no interpretation):
  ✓ drawing extent exists at [x0,y0,x1,y1] (DRAWING_EXTENT_FACT)
  ✓ text "FIG. 9:" exists at [85,340,125,352] (P1 TEXT_ATOM)
  ✓ text is 34.5pt below extent (consumer-computed spatial relation)
  ✓ text x-overlaps with extent (consumer-computed spatial relation)
  ✓ text has "FIG." prefix (P1 lexical observation)
  ✓ text_b "Left:" is same_y_band with text_a, h_gap=18.1pt (P2 geometry)

Layer 2 — Organization (structural relations, no semantic identity):
  ✓ text_a IS_NEAR drawing_extent (distance < threshold)
  ✓ text_a X_ALIGNS drawing_extent (x-overlap)
  ✓ text_a HAS_FIG_PREFIX (lexical filter)
  ✓ text_a + text_b ARE_ADJACENT (P2 same_y + h_gap)
  ✓ text_a is a CAPTION_CANDIDATE (FIG-prefix + near extent + adjacent text)
    → This is an Organization hypothesis, NOT a semantic claim
    → "caption candidate" ≠ "caption" (still needs validation)

Layer 3 — Interpretation (semantic identity, requires Hypothesis + validation):
  ✗ text_a IS_CAPTION of drawing (semantic relation: caption_of)
  ✗ drawing IS_FIGURE (semantic identity)
  ✗ text_a + text_b SHOULD_MERGE (semantic decision)
    → These require knowing "what is this text?" and "what is this drawing?"
    → Cannot be answered from Observation alone
    → Requires Hypothesis layer + Human Validation
```

### Key boundary

```
Organization can answer:
  "Is text_a structurally associated with the drawing extent?"
  → YES (FIG-prefix + proximity + x-overlap)

Interpretation must answer:
  "Is text_a the caption of the figure?"
  → UNKNOWN from evidence alone
  → "FIG." prefix can be caption or reference
  → proximity can be caption or footnote
  → Needs semantic resolution

The boundary is at "caption_candidate" (Organization) vs "caption" (Interpretation).
Organization can narrow to candidates; Interpretation resolves identity.
```

---

## 9. Research Object Assessment

### Can "Text + Drawing Extent + Geometric Relation" form a stable research object?

```
EVIDENCE_ORGANIZATION_RESEARCH_OBJECT = SUPPORTED

Evidence:
  1. Cross-document: pattern present in ALL 5 documents (not med_001-specific)
  2. 126 natural positive instances (FIG-prefix + near extent)
  3. 280 natural negative instances (FIG-prefix + NOT near extent)
  4. 9257 natural negative instances (proximity + NO FIG-prefix)
  5. Discriminating combination: FIG-prefix + proximity (31% vs noise)
  6. Clear three-layer boundary (Observation → Organization → Interpretation)

The research object is:
  "How should text-drawing spatial associations be organized as evidence,
   given that FIG-prefix + proximity is discriminating but not sufficient
   for semantic identity?"

This is a STABLE research object because:
  - The evidence surface is defined (DRAWING_EXTENT_FACT + P1 + P2)
  - The organization pattern is observable (FIG-prefix + proximity + x-overlap)
  - The boundary is clear (Organization → candidates; Interpretation → identity)
  - Natural positives and negatives exist across documents
  - The pattern is NOT document-specific

The research object is NOT:
  - A figure detector (no is_figure)
  - A caption detector (no is_caption)
  - A semantic classifier (no semantic role)
  - An implementation (not authorized)
```

---

## 10. M-A Readiness

### M-A current state

```
GAINED (since original m_a_caption_association_readiness_review.md):
  ✓ VISUAL_REGION_EVIDENCE = AVAILABLE (was MISSING)
  ✓ DRAWING_EXTENT_EVIDENCE = AVAILABLE
  ✓ Cross-document pattern confirmed (5/5 documents)
  ✓ 126 natural positive instances (FIG-prefix + near extent)
  ✓ 280 natural negative instances (FIG-prefix + NOT near extent)
  ✓ 9257 natural negative instances (proximity + NO FIG-prefix)
  ✓ Discriminating combination identified (FIG-prefix + proximity)

STILL MISSING:
  ✗ Boundary cases (multiple drawings on one page — which one is text associated with?)
  ✗ Pre-registered evaluation rules (what distance threshold? what x-overlap criterion?)
  ✗ Semantic boundary definition (caption vs reference vs footnote — needs Hypothesis)
  ✗ Independent validation (126 candidates are identified but not validated as captions)
  ✗ Table caption vs figure caption (both have prefix, different association)

M-A_READINESS = READY_FOR_DESIGN_RESEARCH

Reason:
  - Evidence surface is AVAILABLE (not MISSING anymore)
  - Natural positives (126) and negatives (280 + 9257) are AVAILABLE
  - Cross-document pattern is CONFIRMED (5/5 documents)
  - BUT: no pre-registered rules, no boundary cases, no semantic resolution
  - → Ready for DESIGN RESEARCH (define rules, boundary cases, evaluation)
  - → NOT ready for EXPERIMENT (rules undefined, semantic gap unresolved)
```

---

## 11. Limitations

```
1. Pure geometric organization NOT demonstrated:
   - 185 text atoms per extent = noise
   - Geometry alone cannot form meaningful organization
   - Lexical signal (FIG-prefix) is ESSENTIAL
   → This means DRAWING_EXTENT_FACT alone is NOT sufficient for organization
   → The value is in COMBINATION with P1 lexical observation

2. FIG-prefix is not a perfect discriminator:
   - 31% of FIG-prefix texts are near extents (potential captions)
   - 69% are references (NOT near extents)
   - But: some of the 31% may still be references near drawings by coincidence
   - And: some captions may NOT have FIG-prefix (e.g., "Left:" without "FIG.")
   → FIG-prefix + proximity is better than either alone, but not perfect

3. No validation of 126 candidates:
   - 126 FIG-prefix-near-extent instances are CANDIDATES, not validated captions
   - Without Human Validation, we don't know the true positive rate
   - Some may be table captions (near table drawing, not figure)
   → The 126 count is an upper bound on caption candidates

4. Multiple drawings per page:
   - arxiv_2402 p28 has 1 extent but 5 FIG-prefix texts (Fig. 14a, 14b, 14c, 14d, 15)
   - Which text belongs to which part of the drawing?
   - Current extent is a single aggregated bbox — cannot distinguish sub-regions
   → Boundary case: multiple captions for one drawing (untested)

5. No table caption vs figure caption distinction:
   - "Table 3." near a drawing extent — is it a table caption or figure caption?
   - The drawing might be a table (vector grid lines)
   - Current evidence cannot distinguish table drawing from figure drawing
   → Semantic ambiguity remains

6. Sample still limited to 5 documents:
   - All 5 are arxiv papers (scientific documents)
   - Other document types (reports, slides, textbooks) untested
   - Pattern may not generalize to non-scientific documents

7. "near" threshold (60pt) is arbitrary:
   - No pre-registered justification for 60pt
   - Different thresholds would yield different candidate counts
   - Must be pre-registered before any experiment
```

---

## 12. Final Decision

```
EVIDENCE_ORGANIZATION_INDEPENDENCE = CONDITIONAL
```

### Reasoning

```
SUPPORTED aspects:
  ✓ Cross-document pattern (5/5 documents, not med_001-specific)
  ✓ 126 natural positive instances (FIG-prefix + near extent)
  ✓ 280 + 9257 natural negative instances
  ✓ EXTENT is ESSENTIAL (primitives alone are insufficient)
  ✓ Clear Organization/Interpretation boundary
  ✓ Research object is stable and well-defined
  ✓ M-A advanced from NOT_READY to READY_FOR_DESIGN_RESEARCH

CONDITIONAL (not SUPPORTED) because:
  ✗ Pure geometric organization NOT demonstrated (185 texts/extent = noise)
  ✗ Lexical signal (FIG-prefix) is ESSENTIAL — geometry alone is insufficient
  ✗ 126 candidates NOT validated (true positive rate unknown)
  ✗ No pre-registered evaluation rules
  ✗ Boundary cases untested (multiple drawings, table vs figure)
  ✗ SEMANTIC_INTERPRETATION_REQUIRED = TRUE (caption identity needs Hypothesis)

The independence is CONDITIONAL:
  - DRAWING_EXTENT_FACT has independent value (EXTENT_GAIN confirmed)
  - BUT the organization value requires COMBINATION with lexical signal
  - Pure geometric organization is NOT independently demonstrated
  - The research object is stable but needs design research before testing
```

### Sub-assessments

```
EXTENT_VALUE = ESSENTIAL
  DRAWING_EXTENT_FACT is the key diagnostic contributor (EXTENT_GAIN)
  Without extent, primitives are scattered noise
  With extent, "text near drawing as a whole" becomes answerable

CROSS_DOCUMENT_STATUS = DEMONSTRATED
  Pattern present in ALL 5 documents
  126 positives + 280 negatives across 5 documents
  NOT med_001-specific

PURE_GEOMETRIC_ORGANIZATION_STATUS = NOT_DEMONSTRATED
  185 text atoms per extent = noise
  Geometry alone cannot form meaningful organization
  Lexical signal (FIG-prefix) is ESSENTIAL for discrimination

SEMANTIC_BOUNDARY = CLEAR
  Organization: "text is a caption_candidate" (FIG-prefix + proximity)
  Interpretation: "text IS a caption" (semantic identity)
  Boundary: caption_candidate → caption requires Hypothesis + validation
  SEMANTIC_INTERPRETATION_REQUIRED = TRUE

M-A_READINESS = READY_FOR_DESIGN_RESEARCH
  Evidence: AVAILABLE (was MISSING)
  Positives: 126 natural instances (was 2)
  Negatives: 280 + 9257 natural instances (was 0)
  Cross-document: CONFIRMED (was 1 document)
  BUT: rules undefined, boundary cases untested, semantic gap unresolved
  → Ready for design research, NOT ready for experiment
```

### Case counts

```
CORE_CASE_COUNT = 3 (original diagnostic cases)
INDEPENDENT_DOCUMENT_COUNT = 5 (all available PDFs)
POSITIVE_CASE_COUNT = 126 (FIG-prefix + near extent, cross-document)
NATURAL_NEGATIVE_CASE_COUNT = 280 (FIG-prefix + NOT near extent) + 9257 (proximity + NO FIG-prefix)
BOUNDARY_CASE_COUNT = 0 (multiple drawings per page, table vs figure — untested)

CROSS_DOCUMENT_GENERALIZATION = DEMONSTRATED
  (5/5 documents have the pattern; NOT med_001-specific)
  BUT: limited to arxiv scientific papers (5 documents, 1 document type)
```

---

## 13. Governance Status

```text
EVIDENCE_ORGANIZATION_INDEPENDENCE = CONDITIONAL

EXTENT_VALUE = ESSENTIAL
  DRAWING_EXTENT_FACT is the key diagnostic contributor
  Without extent: scattered primitives = noise
  With extent: "text near drawing as a whole" = answerable

CROSS_DOCUMENT_STATUS = DEMONSTRATED
  Pattern in 5/5 documents, 126 positives, 280+9257 negatives
  NOT med_001-specific

PURE_GEOMETRIC_ORGANIZATION_STATUS = NOT_DEMONSTRATED
  185 text atoms per extent = noise
  FIG-prefix lexical signal is ESSENTIAL for discrimination
  Geometry alone cannot form meaningful organization

SEMANTIC_BOUNDARY = CLEAR
  Organization: caption_candidate (FIG-prefix + proximity) — structural
  Interpretation: caption (semantic identity) — requires Hypothesis
  SEMANTIC_INTERPRETATION_REQUIRED = TRUE

M-A_READINESS = READY_FOR_DESIGN_RESEARCH
  Evidence AVAILABLE (was MISSING)
  126 natural positives (was 2)
  280 + 9257 natural negatives (was 0)
  Cross-document CONFIRMED (was 1 doc)
  BUT: rules undefined, boundary cases untested, semantic gap unresolved

EVIDENCE_ORGANIZATION_RESEARCH_OBJECT = SUPPORTED
  Stable, well-defined, cross-document
  "How should text-drawing spatial associations be organized as evidence?"

LEXICAL_SIGNAL_ROLE = ORGANIZATION_SUPPORT
  FIG-prefix narrows candidates from 9257 to 126 (98.6% reduction)
  Does NOT classify as caption (31% near, 69% not near)
  Helps Organization, does NOT do Interpretation

CASE_COUNTS:
  CORE_CASE_COUNT = 3
  INDEPENDENT_DOCUMENT_COUNT = 5
  POSITIVE_CASE_COUNT = 126
  NATURAL_NEGATIVE_CASE_COUNT = 280 + 9257
  BOUNDARY_CASE_COUNT = 0 (untested)

AO_VISUAL_GEOMETRY = IMPLEMENTED (COMPLETE)
AO_VALUE_EXPERIMENT = COMPLETE (VALUE_PARTIALLY_SUPPORTED)
EVIDENCE_ORGANIZATION_DIAGNOSTIC = COMPLETE (PARTIALLY_TESTABLE)
EVIDENCE_ORGANIZATION_INDEPENDENCE = COMPLETE (CONDITIONAL)

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

- ✅ Used only existing data (5 PDFs, IS-11 GT, AO observations)
- ✅ No new case creation (used natural positives/negatives from cross-doc scan)
- ✅ Tested geometry-only organization (185 texts/extent = NOT discriminating)
- ✅ Tested geometry + lexical (126 candidates = discriminating)
- ✅ Identified FIG-prefix as ORGANIZATION_SUPPORT (not INTERPRETATION_SUPPORT)
- ✅ Established clear Organization/Interpretation boundary
- ✅ Did NOT smuggle "caption" from "FIG." prefix
- ✅ Reported cross-document generalization (5/5 docs, not med_001-specific)
- ✅ Reported 280 + 9257 natural negative controls (was 0)
- ✅ Did NOT implement Evidence Organization
- ✅ Did NOT implement M-A
- ✅ Did NOT modify any code/AO/P1-P7/TLD/IS-11
- ✅ Frozen baseline intact
- ✅ Did NOT auto-enter M-A / Human Feedback / L3 / Capability

`STOP = TRUE`.
