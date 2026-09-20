# M-A Caption Association Design Research

> **模式: DESIGN RESEARCH ONLY / READ-ONLY / NO IMPLEMENTATION / NO EXPERIMENT / FROZEN INTACT / STOP**
> 日期: 2026-09-17
> 前置: `tmp/evidence_organization_independence_research.md`（CONDITIONAL, READY_FOR_DESIGN_RESEARCH）
> 本文件: 将 M-A 从"有 126 个 candidate 的方向"提升为边界清楚、Human 判断单位明确、正负边界可定义的 Research Object。

---

## 1. Research Question

> 定义一个 Evidence-grounded、可验证、可审计的 Caption Association Research Object，并确定它是否具备进入正式实验的条件。

核心研究链：

```
Text Observation + Drawing Extent Observation + Spatial Evidence + Lexical Observation
        ↓
Caption Candidate (Evidence Organization)
        ↓
Semantic Interpretation (caption identity — needs Hypothesis)
        ↓
Human Validation (minimal judgment unit)
```

严格区分：

```
caption_candidate ≠ caption
```

---

## 2. Current Evidence Surface

```
Available Evidence (after AO Visual Geometry Extension):

  P1 TEXT_ATOM (frozen):
    - text content (lexical: "FIG.", "Figure", "Table" prefix detectable)
    - bbox, observation_id
    - Atom-level splitting: "FIG. 1: Schematic" may be one atom or split

  P2 GeometryObservation (frozen):
    - same_y_band, h_gap, v_gap, left_alignment_group
    - text-text pairwise geometry

  P5 ReadingOrder (frozen):
    - column groups, reading sequence

  P6 RegionObservation (frozen):
    - PAGE_TOP/BOTTOM/FULL_WIDTH/COLUMN/DENSE/SPARSE/UNKNOWN

  DRAWING_GEOMETRY_FACT (implemented):
    - per-primitive: drawing_id, bbox, draw_type, item_count, item_types
    - ALL primitives (no pre-filter)

  DRAWING_EXTENT_FACT (implemented):
    - aggregated: extent_id, bbox, width, height, area, primitive_count, constituent_seqnos
    - 3-stage geometric pipeline (12 params)

  Consumer-computed (NOT stored):
    - text-extent distance (bbox arithmetic)
    - text-extent x-overlap (bbox arithmetic)
    - text-extent vertical ordering (above/below/inside)
```

### Available Data (from previous phases)

```
5 PDFs, 95 pages total
50 text-near-extent instances
126 FIG-prefix + near-extent candidates
280 FIG-prefix + NOT-near-extent (Type A negatives)
9257 proximity + NO-FIG-prefix (Type B negatives)
3 core diagnostic cases (AMB-414, AMB-422, EXT-P28)
6 IS-11 negative controls (table text)
7 multi-drawing boundary pages
```

---

## 3. M-A Research Object

### Formal Definition

```
M-A Research Object = Text-Drawing Association

  The problem of determining whether a text atom is structurally
  associated with a drawing extent, using geometric and lexical
  evidence, WITHOUT determining the semantic identity of either.

Layer assignment:

  Observation (Layer A/B):
    - P1 text atom (content, bbox)
    - DRAWING_EXTENT_FACT (extent bbox, primitive_count)
    - P2 text-text geometry (same_y, h_gap)
    - Spatial: text-extent distance, x-overlap, vertical ordering (consumer-computed)

  Evidence Organization (Layer C):
    - caption_candidate = text with FIG-prefix + near extent + spatial alignment
    - This is a STRUCTURAL hypothesis, not a semantic claim

  Semantic Interpretation (Layer D — NOT this research):
    - caption = text IS the caption of the drawing
    - caption_of = semantic relation
    - These require Hypothesis + Human Validation

  Human Validation (Layer E — designed, not executed):
    - minimal judgment: "is this text associated with this drawing?"
    - NOT: "is this a caption?" (semantic)
    - NOT: "what type of drawing?" (semantic)
```

### What M-A does NOT study

```
  NOT: Figure Detection (is the drawing a figure?)
  NOT: Caption Classification (is the text a caption?)
  NOT: Caption-Of Relation (semantic relation)
  NOT: MERGE/KEEP_SEPARATE Decision (requires semantic interpretation)
  NOT: Figure Content Understanding (requires OCR/visual recovery)
```

---

## 4. Caption Candidate Definition

### CAPTION_CANDIDATE (Evidence Organization, not Semantic)

```
A text atom T is a CAPTION_CANDIDATE for drawing extent E if:

  1. T has FIG-prefix lexical pattern (P1 observation)
     - T.text matches: ^(fig\.?\s*\d+|figure\s*\d+) [case-insensitive]
     - OR T.text starts with "FIG." / "Figure" / "Fig." (atom-level)

  2. T is spatially near E (consumer-computed from bboxes)
     - distance(T.bbox, E.bbox) < TO_BE_PRE_REGISTERED
     - Currently observed: 15-55pt range for known positives

  3. T x-overlaps or is x-adjacent to E (consumer-computed)
     - T.bbox.x0 < E.bbox.x1 AND T.bbox.x1 > E.bbox.x0
     - OR horizontal gap < TO_BE_PRE_REGISTERED

What CAPTION_CANDIDATE means:
  "Based on existing evidence, this text is worth entering the
   Caption Association research/validation set."

What CAPTION_CANDIDATE does NOT mean:
  ❌ "This text IS a caption"
  ❌ "This text is the caption of this drawing"
  ❌ "This drawing IS a figure"
  ❌ "These texts should be merged"

CAPTION_CANDIDATE is:
  ✓ An Evidence Organization output (structural)
  ✓ A candidate for Human Validation
  ✓ Reducible to observable facts (no semantic judgment)
```

### Can CAPTION_CANDIDATE be constructed without semantic judgment?

```
YES — construction uses only:
  - P1 text content (lexical pattern matching)
  - DRAWING_EXTENT_FACT bbox (geometric)
  - Spatial distance computation (bbox arithmetic)
  - X-overlap computation (bbox arithmetic)

NO semantic judgment is required to construct a CAPTION_CANDIDATE.
The construction is purely Evidence Organization.
```

---

## 5. FIG-prefix Evidence Role

### Formal Role

```
FIG-prefix = CANDIDATE_SPACE_REDUCTION (Organization Support)

  Evidence:
    caption_like pattern (FIG.N / Figure N.): 62 atoms, 71% near extent
    ambiguous fragment (FIG. / Fig. alone): 220 atoms, 29% near extent

  Role:
    FIG-prefix narrows candidate space from 9257 (all text near extents)
    to 126 (FIG-prefix + near extent) = 98.6% reduction

  NOT:
    ❌ Semantic classification ("this is a caption")
    ❌ Caption detector
    ❌ Figure label
```

### Lexical Form Analysis

```
Three lexical forms observed in corpus:

  1. caption_like: "FIG. 1:", "Figure 3.", "Fig. 7:"
     - Pattern: ^(fig\.?\s*\d+|figure\s*\d+)
     - 62 atoms, 71% near extent
     - STRONG signal (likely caption, not reference)
     - But: 18 NOT near extent (29%) — some are references ("Figure 3 shows...")

  2. reference_like: "see Fig.", "in Figure", "as shown in Fig."
     - 0 atoms detected at P1 atom level
     - REASON: P1 splits "see Fig. 1" into separate atoms: "see", "Fig.", "1"
     - "Fig." as standalone atom is AMBIGUOUS (could be caption or reference)
     - NOT_IDENTIFIABLE_FROM_CURRENT_CORPUS at atom level

  3. ambiguous: "FIG." / "Fig." / "Figure" as standalone fragment
     - 220 atoms, 29% near extent
     - WEAK signal (fragment without number/context)
     - Could be caption fragment OR reference fragment
     - Cannot distinguish without surrounding atom context

### Key limitation

  P1 atom splitting creates ambiguity:
    - "FIG. 9: Left:" → P1 may split into "FIG.", "9:", "Left:" (separate atoms)
    - "see Fig. 9" → P1 splits into "see", "Fig.", "9" (separate atoms)
    - The standalone "Fig." atom appears in BOTH cases
    - At atom level, cannot distinguish caption from reference

  This means:
    - FIG-prefix at ATOM level is a WEAK discriminator (29% near for fragments)
    - FIG-prefix + NUMBER at atom level is a STRONG discriminator (71% near)
    - Full caption-like pattern (FIG.N + description) is the best discriminator
    - But P1 splitting may prevent detecting the full pattern in one atom

  IMPLICATION:
    - FIG-prefix should be used as CANDIDATE_SPACE_REDUCTION (weak filter)
    - NOT as a definitive caption indicator
    - Additional context (surrounding atoms, reading order) may help
    - But this requires Evidence Organization beyond single-atom level
```

---

## 6. Spatial Evidence Design

### Conceptual Analysis (no threshold values)

```
For each spatial relation, mark: NECESSARY / SUPPORTING / UNKNOWN / NOT_REQUIRED

  1. distance (text-extent vertical distance)
     SUPPORTING
     - 87% of caption-like texts near extent are within 60pt
     - But: no fixed threshold — 15-55pt range observed
     - Cannot be NECESSARY (some captions may be 70pt away)
     - TO_BE_PRE_REGISTERED threshold needed for experiment

  2. vertical ordering (text above/below/inside extent)
     SUPPORTING
     - 87% captions BELOW drawing, 11% ABOVE, 2% INSIDE
     - "below" is dominant but NOT universal
     - Cannot require "must be below" (11% above)
     - Should be SUPPORTING signal, not NECESSARY

  3. x-overlap (text x-range overlaps extent x-range)
     SUPPORTING
     - Most caption-like texts x-overlap with extent
     - But: AMB-422 has x_overlap=FALSE (text at x=[85,129], extent at x=[177,470])
     - Cannot be NECESSARY (some captions are left-aligned, not overlapping)
     - Should be SUPPORTING

  4. horizontal alignment (text left-aligns with extent)
     UNKNOWN
     - Some captions align with extent left edge
     - But: some captions are centered, some are left-aligned at page margin
     - Not enough data to determine if this is discriminative
     - Need more analysis

  5. extent containment (text inside extent bbox)
     NOT_REQUIRED
     - Only 2% of captions are "inside" extent
     - These are likely equation labels inside drawings, not captions
     - Should NOT be used as caption criterion

  6. multiple-drawing ambiguity (text near 2+ extents)
     NECESSARY (as a design consideration)
     - 7 pages with 2+ FIG-prefix texts near 2+ extents
     - Association ambiguity: which text belongs to which drawing?
     - Must be addressed in evaluation protocol (see §7)
     - Currently: nearest extent by distance is the natural default
     - But: "nearest" may not always be correct
```

### Spatial Rule Summary

```
NECESSARY: multiple-drawing ambiguity handling
SUPPORTING: distance, vertical ordering, x-overlap
UNKNOWN: horizontal alignment
NOT_REQUIRED: extent containment

NO threshold values are pre-registered in this design.
All thresholds = TO_BE_PRE_REGISTERED.
```

---

## 7. Multiple-Drawing Boundary

### Observed Cases

```
7 pages with 2+ FIG-prefix texts near 2+ extents:

  efficientnet p4: 2 extents, "Figure 3." near #0, "Figure 4." near #1
  arxiv_2402 p17: 3 extents, "Fig. 7:" near #0, "Fig. 8:" near #2
  arxiv_2402 p19: 2 extents, "Fig. 10:" near #0, "Fig. 11:" near #1
  arxiv_2402 p24: 2 extents, "Fig. 13:" near #1
  med_001 p8: 2 extents, "FIG. 1:" near #0
  arxiv_2402 p12: 3 extents, "Fig. 3:" near #2
  arxiv_2402 p18: 2 extents, "Fig. 9:" near #0
```

### Association Ambiguity Analysis

```
When text T is near 2+ extents (E1, E2):

  Current evidence can compute:
    - distance(T, E1), distance(T, E2)
    - x-overlap(T, E1), x-overlap(T, E2)
    - vertical ordering(T, E1), vertical ordering(T, E2)

  Can current evidence DETERMINE association?
    → AMBIGUOUS (in most cases)

  Reason:
    - If T is much closer to E1 than E2 → LIKELY associated with E1
    - But: "closer" is a heuristic, not a deterministic rule
    - If distances are similar → genuinely ambiguous
    - FIG-prefix number may help ("Fig. 7" → match with extent that is figure 7)
      but: extent doesn't carry figure number (semantic identity)

  Conclusion:
    - Nearest-extent-by-distance is a reasonable DEFAULT heuristic
    - But: association is AMBIGUOUS when distances are similar
    - This is a boundary case that requires Human Validation
    - NOT a case for automatic winner selection
```

### Design Decision

```
MULTIPLE_DRAWING_AMBIGUITY:
  - When text is near 1 extent → DETERMINABLE (single candidate)
  - When text is near 2+ extents with clear distance difference → LIKELY DETERMINABLE
  - When text is near 2+ extents with similar distances → AMBIGUOUS (Human Validation)
  - No automatic winner selection
  - Ambiguous cases enter Boundary Set for Human Validation
```

---

## 8. Caption vs Reference Boundary

### Observed Patterns

```
Case A: Caption (FIG-prefix + near drawing)
  "FIG. 1: Schematic diagram illustrating..."
  → text has FIG-prefix + number + description
  → text is near drawing extent
  → likely caption

Case B: Reference (FIG-prefix + near drawing + reference wording)
  "Figure 14a shows the results obtained..."
  → text has FIG-prefix + number + "shows" (reference verb)
  → text may be near drawing extent (on same page as drawing)
  → likely reference, NOT caption

Can current evidence distinguish Case A from Case B?

  From caption-like not-near analysis:
    18 caption-like texts NOT near extent:
      - 3 (17%): no drawings on page (cross-page reference)
      - 4 (22%): drawings exist but no extent (Observation gap)
      - 11 (61%): extent exists but text far (>60pt) → reference

  This means:
    - FIG-prefix + NOT near → mostly reference (61% far, 17% cross-page)
    - FIG-prefix + near → mostly caption (71% near for caption_like pattern)
    - BUT: some FIG-prefix + near may still be references
      (e.g., "Figure 14a shows..." on same page as Figure 14 drawing)

  Can we distinguish "FIG. 1:" (caption) from "Figure 1 shows" (reference)
  using P1 lexical evidence alone?

  At ATOM level:
    - "FIG." atom → ambiguous (caption or reference fragment)
    - "Figure" atom → ambiguous
    - "shows" atom → may indicate reference, but P1 doesn't classify verbs

  At PATTERN level (if P1 preserves full caption text in one atom):
    - "FIG. 1:" pattern (prefix + number + colon) → likely caption
    - "Figure 1 shows" pattern (prefix + number + verb) → likely reference
    - But P1 may split these into separate atoms

  CONCLUSION:
    Current evidence CANNOT reliably distinguish caption from reference
    when both are near a drawing extent.
```

### Semantic Boundary

```
SEMANTIC_INTERPRETATION_REQUIRED = TRUE

  Distinguishing caption from reference requires understanding:
    - "FIG. 1: Schematic..." → caption (describes the drawing)
    - "Figure 1 shows..." → reference (cites the drawing in prose)

  This distinction is SEMANTIC:
    - "shows" / "illustrates" / "depicts" = reference verb
    - ":" after number = caption delimiter
    - But: these are lexical patterns, not geometric facts
    - P1 records text content but doesn't classify sentence structure

  The Evidence Organization can:
    ✓ Identify caption CANDIDATES (FIG-prefix + near extent)
    ✓ Narrow the search space (98.6% reduction)
    ✗ Cannot determine if candidate IS caption or reference
    → This is the legitimate Semantic Boundary of M-A
```

---

## 9. Caption vs Footnote / Body Text Boundary

### Can geometric conditions distinguish caption from other text types?

```
Text types near drawing extents:

  Caption:     FIG-prefix + near extent + below drawing (87%)
  Footnote:    NO FIG-prefix + near extent (may be below drawing)
  Body Text:   NO FIG-prefix + near extent (prose near drawing)
  Table Text:  NO FIG-prefix + near extent (table cells near drawing border)
  Equation:    NO FIG-prefix + near extent (equation symbols inside drawing)
  Reference:   FIG-prefix + may be near extent ("see Fig. 1" on same page)

Geometric conditions:
  - distance: caption ~15-55pt, body text can be 0-60pt → OVERLAP
  - vertical ordering: caption 87% below, body text can be below → OVERLAP
  - x-overlap: caption may overlap, body text may overlap → OVERLAP

Can geometric conditions ALONE distinguish caption from body text/footnote?
  → NO

Reason:
  - 9257 text atoms near extents without FIG-prefix
  - These include body text, table cells, equations, footnotes
  - Geometrically, they are in the same spatial zone as captions
  - Without lexical signal (FIG-prefix), geometry cannot distinguish

  The ONLY discriminator is FIG-prefix (lexical):
    - With FIG-prefix: 126 candidates (potential captions)
    - Without FIG-prefix: 9257 texts (not caption candidates)
    - But even with FIG-prefix: 31% near + 69% not near

GEOMETRIC_ORGANIZATION_LIMIT = IDENTIFIED

  Pure geometric organization can:
    ✓ Identify "text is near drawing" (spatial fact)
    ✓ Compute distance, overlap, ordering (spatial relations)
    ✗ Cannot distinguish caption from body text/footnote/table text
    → Lexical signal (FIG-prefix) is ESSENTIAL
    → Even with lexical signal, caption vs reference is semantic
```

### Text Type Discrimination Matrix

```
                    | FIG-prefix | Near extent | Distinguishable by geometry?
  Caption           |    YES     |    YES      | NO (geometry alone insufficient)
  Reference         |    YES     |  MAYBE      | NO (same prefix, different role)
  Footnote          |    NO      |    YES      | NO (same position, different content)
  Body Text         |    NO      |    YES      | NO (same position)
  Table Text        |    NO      |    YES      | NO (same position)
  Equation          |    NO      |  INSIDE     | NO (inside extent)
  Page Number       |    NO      |  MAYBE      | NO (same position)

  → Only FIG-prefix provides ANY discrimination
  → Even FIG-prefix cannot distinguish caption from reference
  → GEOMETRIC_ORGANIZATION_LIMIT = IDENTIFIED
```

---

## 10. Evidence Organization vs Semantic Interpretation

### Three-Layer Boundary for M-A

```
Layer 1 — Observation (pure facts):
  ✓ text atom content: "FIG. 9:" (P1)
  ✓ text atom bbox: [85, 340, 125, 352] (P1)
  ✓ drawing extent bbox: [88, 127, 526, 306] (DRAWING_EXTENT_FACT)
  ✓ drawing extent primitive_count: 16 (DRAWING_EXTENT_FACT)
  ✓ text-extent distance: 34.5pt (consumer-computed)
  ✓ text-extent x-overlap: TRUE (consumer-computed)
  ✓ text-extent vertical ordering: BELOW (consumer-computed)
  ✓ text-text same_y_band: TRUE (P2)
  ✓ text-text h_gap: 18.1pt (P2)

Layer 2 — Evidence Organization (structural hypothesis):
  ✓ text IS caption_candidate (FIG-prefix + near extent + spatial alignment)
  ✓ text_a + text_b ARE_ADJACENT (P2 same_y + h_gap)
  ✓ nearest extent IDENTIFIED (single candidate)
  ✗ caption_candidate ≠ caption (structural, not semantic)

Layer 3 — Semantic Interpretation (requires Hypothesis + validation):
  ✗ text IS_CAPTION of drawing (semantic identity)
  ✗ drawing IS_FIGURE (semantic identity)
  ✗ text_a + text_b SHOULD_MERGE (semantic decision)
  ✗ text IS NOT reference (semantic distinction)
  → These require Human Validation or Hypothesis layer
  → Cannot be answered from Observation alone

BOUNDARY:
  Organization can produce: caption_candidate (structural)
  Interpretation must produce: caption (semantic)
  The gap between them is the SEMANTIC BOUNDARY
```

---

## 11. Minimal Human Validation Unit

### Design Analysis

```
Candidate judgment units:

  A. "Is this text a Caption?"
    → Semantic judgment (requires understanding "caption" concept)
    → Too heavy — Human is doing Interpretation, not Validation

  B. "Is this text associated with this drawing?"
    → Structural judgment (spatial + lexical evidence presented)
    → Lighter — Human validates the structural association
    → Does NOT require understanding "caption" vs "reference"
    → BUT: "associated" is still somewhat semantic

  C. "Keep / Reject" (merge decision)
    → Decision judgment (too close to algorithm output)
    → NOT suitable — Human should validate evidence, not make algorithm decisions

  D. "Boundary / Non-boundary"
    → Structural judgment (is this a text-drawing boundary?)
    → Lightest — but may be too vague for caption association

RECOMMENDED: B — "Is this text associated with this drawing?"

Reasoning:
  - Human sees: text content + drawing extent bbox + spatial relationship
  - Human judges: "is this text about/for this drawing?"
  - Human does NOT need to:
    ✗ Manually find the drawing (extent is presented)
    ✗ Manually find relevant text (candidate is presented)
    ✗ Reconstruct page structure (evidence is organized)
    ✗ Write reasons (just yes/no)
    ✗ Specify detector/feature/algorithm
  - Human DOES:
    ✓ See the text content ("FIG. 9: Left:")
    ✓ See the drawing extent (bbox + primitive_count)
    ✓ See spatial relationship (distance, x-overlap, below)
    ✓ Judge: "associated" or "not associated"

MINIMAL_HUMAN_VALIDATION_UNIT = "Is this text associated with this drawing? (Yes/No)"

  This is:
    ✓ Minimal (one binary judgment)
    ✓ Evidence-grounded (evidence is presented)
    ✓ Not reconstructive (Human doesn't rebuild structure)
    ✓ Not algorithmic (Human doesn't specify detector)
    ✓ Validating Organization (not doing Interpretation)

  This is NOT:
    ✗ "Is this a caption?" (semantic)
    ✗ "What type of drawing?" (semantic)
    ✗ "Should these merge?" (decision)
    ✗ "Explain why" (diagnostic)
```

---

## 12. Human Evidence Pack Requirements

### Information Needs (design only, no UI)

```
For each CAPTION_CANDIDATE, the Evidence Pack must present:

  1. Text content (P1):
     - Full text of the candidate atom
     - If split across atoms: full concatenated text of adjacent same_y atoms
     - Example: "FIG. 9: Left: ..."

  2. Drawing extent context (DRAWING_EXTENT_FACT):
     - Extent bbox [x0, y0, x1, y1]
     - Primitive count (density signal)
     - Area (size signal)
     - NOT: PNG rendering (forbidden in Observation)
     - NOT: Figure/table identity (semantic, forbidden)

  3. Spatial relationship (consumer-computed):
     - Text bbox [x0, y0, x1, y1]
     - Distance to extent (e.g., "34.5pt below")
     - X-overlap status (e.g., "x-overlaps: yes")
     - Vertical ordering (e.g., "text is below extent")

  4. Lexical observation (P1):
     - FIG-prefix detected: yes/no
     - Pattern type: caption_like / ambiguous / none

  5. Adjacent text context (P2):
     - Same-y-band members (e.g., "FIG. 9:" + "Left:" + "Right:")
     - h_gap between members
     - This shows whether caption has continuation text

  6. Page context (optional, for boundary cases):
     - Number of extents on page (multiple-drawing context)
     - P6 region type (COLUMN/DENSE/SPARSE)
     - Other FIG-prefix texts on page (for disambiguation)

  NOT included:
    ✗ Drawing PNG/image (visual recovery, forbidden)
    ✗ Semantic labels (is_figure, is_caption, forbidden)
    ✗ Confidence score (forbidden)
    ✗ Algorithm recommendation (forbidden)
    ✗ Full page reconstruction (too heavy for minimal judgment)
```

---

## 13. Positive / Negative / Boundary Design

### Candidate vs Positive vs Boundary

```
126 CAPTION_CANDIDATES are NOT 126 positives.

  Candidate = evidence suggests "worth validating"
  Positive = Human confirms "this text is associated with this drawing"
  Boundary = Human is uncertain or case is ambiguous

Design:

  POSITIVE SET:
    - Candidates where Human validates "associated" = YES
    - Expected: most caption_like + near extent cases
    - But: some may be references (validated as "not associated")

  NEGATIVE SET:
    Type A: 280 FIG-prefix + NOT near extent
      → Expected: mostly references (FIG-prefix without spatial context)
      → Human validates: "not associated" (text is about a different drawing or cross-page)
    Type B: 9257 proximity + NO FIG-prefix
      → Expected: body text, table cells, equations
      → NOT all need Human validation (too many)
      → Sample subset for validation

  BOUNDARY SET:
    - Multiple-drawing cases (7 pages, text near 2+ extents)
      → Human validates: "which drawing is this text associated with?"
    - Caption vs reference cases (FIG-prefix + near extent + reference wording)
      → Human validates: "is this a caption or a reference?"
    - Edge distance cases (text at 55-70pt, near threshold boundary)
      → Human validates: "is this near enough to be associated?"
```

### Set Design

```
POSITIVE_SET: TO_BE_VALIDATED (from 126 candidates)
  - Not automatically positive — requires Human Validation
  - Design estimate: ~70-80% may validate as positive (based on 71% near rate)

NEGATIVE_SET:
  Type A: 280 FIG-prefix + NOT near extent
    → Natural negatives (reference-like, no spatial context)
    → Subsample for validation (e.g., 30-50 cases)
  Type B: sample from 9257 proximity + NO FIG-prefix
    → Natural negatives (body text near drawing)
    → Subsample for validation (e.g., 30-50 cases)

BOUNDARY_SET:
  Multiple-drawing: 7 pages (text near 2+ extents)
  Caption vs reference: candidates where text contains reference-like wording
    → NOT_IDENTIFIABLE_FROM_CURRENT_CORPUS at atom level
    → Need Human Validation to identify these
  Edge distance: candidates at 50-70pt distance
    → Currently: 60pt threshold is arbitrary
    → TO_BE_PRE_REGISTERED

TOTAL VALIDATION BURDEN:
  ~126 positives + ~60-100 negatives + ~7-15 boundary = ~200-240 cases
  (manageable for Human Validation)
```

---

## 14. Cross-Document Independence

```
5 PDFs analyzed:

  is11_med_001:        12 FIG-prefix + near extent candidates
  is11_resnet:          6 candidates
  is11_efficientnet:    6 candidates
  is11_cs_001:          3 candidates
  arxiv_2402.18619:    23 candidates (but many are Fig. fragments)

ALL 5 documents have the Text-Drawing Spatial Association pattern.

CANDIDATE_INDEPENDENCE ≠ VALIDATED_PATTERN_INDEPENDENCE

  Candidates are identified across 5 documents → cross-document candidate independence = DEMONSTRATED
  But: candidates are NOT validated (no Human/GT confirmation)
  → Pattern independence is CANDIDATE-level, not VALIDATED-level

Document type limitation:
  All 5 are arxiv scientific papers
  Other document types (reports, slides, textbooks) untested
  → Generalization to non-scientific documents is NOT_DEMONSTRATED

CROSS_DOCUMENT_GENERALIZATION = DEMONSTRATED (for arxiv scientific papers)
  BUT: limited to 1 document type
  AND: at candidate level (not validated)
```

---

## 15. Future Evaluation Protocol

### Design (not execution)

```
POPULATION:
  All text atoms + drawing extents across available corpus (5 PDFs, 95 pages)

SAMPLING FRAME:
  Stratified sampling:
    - Stratum 1: FIG-prefix + near extent (126 candidates) → potential positives
    - Stratum 2: FIG-prefix + NOT near extent (280) → Type A negatives
    - Stratum 3: Near extent + NO FIG-prefix (9257) → Type B negatives (subsample)
    - Stratum 4: Multiple-drawing pages (7) → boundary cases

POSITIVE SET:
  Human-validated "associated" from Stratum 1
  (NOT all 126 — requires validation)

NEGATIVE SET:
  Human-validated "not associated" from Stratum 2 + Stratum 3 subsample

BOUNDARY SET:
  Multiple-drawing cases from Stratum 4
  + edge-distance cases (50-70pt)
  + caption-vs-reference cases (identified during validation)

GROUND TRUTH:
  Human Validation (minimal judgment unit: "associated? yes/no")
  NOT: algorithm output
  NOT: LLM judgment
  NOT: automatic classification

HUMAN ADJUDICATION UNIT:
  Single text-drawing pair: "Is this text associated with this drawing? (Yes/No)"
  For boundary cases: "Which drawing is this text associated with?"

PRIMARY METRIC:
  Explanation Gain (from E0 to E1)
  NOT: accuracy / precision / recall (these require semantic ground truth)
  Instead: "how many failures become newly diagnosable?"

FAILURE TAXONOMY:
  See §16

ACCEPTANCE CRITERIA:
  TO_BE_PRE_REGISTERED
  (cannot define without evidence on validation results)

THRESHOLDS:
  distance threshold: TO_BE_PRE_REGISTERED
  x-overlap criterion: TO_BE_PRE_REGISTERED
  (must not auto-define without evidence)
```

---

## 16. Failure Taxonomy Mapping

```
Existing DICE failure taxonomy:
  A = Perception Missing
  B = Perception Incorrect
  C = Evidence Representation Loss
  D = Evidence Organization Failure
  E = Interpretation / Decision Logic Failure
  F = Genuine Semantic Boundary
  G = Unknown

M-A Caption Association failure mapping:

  Before Vector Geometry:
    VISUAL_REGION_EVIDENCE = MISSING
    → Failure type: A (Perception Missing) — visual content invisible
    → Or C (Evidence Representation Loss) — no surface for visual facts

  After Vector Geometry:
    Evidence is AVAILABLE but organization is undefined
    → Failure type: D (Evidence Organization Failure)
    → "Can observe drawings, but cannot organize text-drawing associations"

  After Evidence Organization (if implemented):
    caption_candidate produced, but caption identity unresolved
    → Failure type: F (Genuine Semantic Boundary)
    → "caption_candidate ≠ caption — semantic interpretation required"

  If MERGE decision is wrong:
    → Failure type: E (Interpretation / Decision Logic Failure)
    → "semantic hypothesis (caption_of) was incorrect"

Most likely M-A failure categories:
  PRIMARY: D (Evidence Organization Failure) — current state
  SECONDARY: F (Genuine Semantic Boundary) — after organization
  TERTIARY: E (Interpretation / Decision Logic Failure) — after hypothesis
```

---

## 17. H-MA Research Hypothesis

```
H-MA:

  Text-Drawing Spatial Association can reduce the candidate search space
  using existing geometric and lexical Evidence, while final Caption
  Association remains a semantic interpretation problem requiring
  Human validation.

Evidence supporting H-MA:
  - 126 candidates from 9257 texts (98.6% reduction) — search space reduction confirmed
  - 71% caption_like pattern near extent — lexical discrimination confirmed
  - 280 + 9257 natural negatives — negative set available
  - 3 diagnostic cases with counterfactual=NO — genuine new diagnostic capability
  - Cross-document (5/5 PDFs) — not document-specific

Evidence challenging H-MA:
  - Pure geometric organization NOT demonstrated (185 texts/extent = noise)
  - FIG-prefix is essential but imperfect (31% near, 69% not near)
  - Caption vs reference boundary is semantic (cannot resolve from evidence)
  - P1 atom splitting creates lexical ambiguity
  - 0 validated cases (all 126 are candidates, not confirmed positives)

H-MA is a HYPOTHESIS, not a verified conclusion.
```

---

## 18. Readiness Gate

```
RESEARCH_OBJECT_DEFINED = PASS
  - Text-Drawing Association is formally defined
  - Three-layer boundary (Observation → Organization → Interpretation) established
  - What M-A studies and does NOT study is clear

EVIDENCE_BOUNDARY_DEFINED = PASS
  - Observation: P1 + P2 + DRAWING_EXTENT_FACT + spatial relations
  - Organization: caption_candidate (FIG-prefix + near extent + spatial alignment)
  - Interpretation: caption identity (semantic, requires Hypothesis + Human)
  - Boundary: caption_candidate ≠ caption

HUMAN_VALIDATION_UNIT_DEFINED = PASS
  - Minimal unit: "Is this text associated with this drawing? (Yes/No)"
  - Evidence Pack requirements defined (text + extent + spatial + lexical + context)
  - Human does NOT: find drawing, find text, reconstruct, write reasons, specify algorithm

POSITIVE_SET_DESIGNABLE = CONDITIONAL
  - 126 candidates available
  - BUT: not validated (candidates ≠ positives)
  - Positive set requires Human Validation to confirm
  - Design is complete; execution requires authorization

NEGATIVE_SET_DESIGNABLE = PASS
  - 280 Type A negatives (FIG-prefix + NOT near extent)
  - 9257 Type B negatives (proximity + NO FIG-prefix)
  - Both types are natural (not synthetic)
  - Subsample design defined (60-100 cases)

BOUNDARY_SET_DESIGNABLE = CONDITIONAL
  - 7 multiple-drawing pages identified
  - BUT: caption-vs-reference boundary cases NOT identifiable from current corpus
    (P1 atom splitting prevents reference detection at atom level)
  - Edge-distance boundary cases require pre-registered threshold
  - Design is partially complete

EVALUATION_PROTOCOL_DESIGNABLE = CONDITIONAL
  - Population, sampling frame, strata defined
  - Human adjudication unit defined
  - Primary metric (Explanation Gain) defined
  - BUT: thresholds TO_BE_PRE_REGISTERED
  - BUT: acceptance criteria TO_BE_PRE_REGISTERED
  - Cannot complete without validation evidence

IMPLEMENTATION_READY = FAIL
  - Design research is complete
  - But: no implementation is authorized
  - No thresholds pre-registered
  - No validation executed
  - No GT constructed
  - Implementation requires separate authorization
```

### Gate Summary

```
RESEARCH_OBJECT_DEFINED       = PASS
EVIDENCE_BOUNDARY_DEFINED     = PASS
HUMAN_VALIDATION_UNIT_DEFINED = PASS
POSITIVE_SET_DESIGNABLE       = CONDITIONAL
NEGATIVE_SET_DESIGNABLE       = PASS
BOUNDARY_SET_DESIGNABLE       = CONDITIONAL
EVALUATION_PROTOCOL_DESIGNABLE= CONDITIONAL
IMPLEMENTATION_READY          = FAIL

DESIGN_READY ≠ IMPLEMENTATION_READY (confirmed)
```

---

## 19. Remaining Conditions

### Before M-A can enter formal Experiment

```
MINIMUM GATES (must be satisfied before experiment execution):

  G1: Pre-register distance threshold
    - Currently: 60pt (arbitrary, from observation)
    - Need: evidence-based threshold or pre-registered value
    - Status: TO_BE_PRE_REGISTERED

  G2: Pre-register x-overlap criterion
    - Currently: boolean (overlap / no overlap)
    - Need: define what counts as "aligned"
    - Status: TO_BE_PRE_REGISTERED

  G3: Execute Human Validation on candidate set
    - 126 candidates need "associated? yes/no" validation
    - 60-100 negatives need validation
    - 7-15 boundary cases need validation
    - Status: NOT AUTHORIZED (requires separate authorization)

  G4: Construct validated Positive/Negative/Boundary sets
    - From Human Validation results
    - Status: BLOCKED on G3

  G5: Define acceptance criteria
    - Based on validation results
    - Status: TO_BE_PRE_REGISTERED (blocked on G3)

  G6: Address P1 atom splitting limitation
    - Caption-like pattern detection requires multi-atom context
    - Either: extend P1 (NOT AUTHORIZED) or accept atom-level limitation
    - Status: DESIGN_DECISION_REQUIRED

  G7: Address caption-vs-reference semantic boundary
    - Accept that Organization cannot resolve this
    - Route to Human Validation (boundary set)
    - Status: ACCEPTED (semantic boundary is legitimate)
```

---

## 20. Final Decision

```
M-A_STATUS = DESIGN_READY_WITH_CONDITIONS
```

### Reasoning

```
DESIGN_READY because:
  ✓ Research Object formally defined (Text-Drawing Association)
  ✓ Evidence boundary clear (Observation → Organization → Interpretation)
  ✓ Caption Candidate definition complete (evidence-grounded, no semantic)
  ✓ FIG-prefix role confirmed (Organization Support, not Interpretation)
  ✓ Spatial evidence design complete (conceptual, no thresholds)
  ✓ Multiple-drawing boundary analyzed
  ✓ Caption vs Reference boundary identified (semantic, legitimate)
  ✓ Human Validation unit defined (minimal: "associated? yes/no")
  ✓ Evidence Pack requirements defined
  ✓ Positive/Negative/Boundary set design complete
  ✓ Cross-document independence confirmed (5/5 PDFs)
  ✓ Evaluation protocol designed (strata, sampling, metric)
  ✓ Failure taxonomy mapped (D → F → E)
  ✓ H-MA hypothesis formally stated

WITH_CONDITIONS because:
  ✗ Thresholds TO_BE_PRE_REGISTERED (G1, G2)
  ✗ Human Validation NOT executed (G3 — requires authorization)
  ✗ Validated sets NOT constructed (G4 — blocked on G3)
  ✗ Acceptance criteria NOT defined (G5 — blocked on G3)
  ✗ P1 atom splitting limitation unresolved (G6 — design decision required)
  ✗ Implementation NOT authorized
  ✗ Experiment NOT authorized

The design is complete.
The conditions are clear.
The next step is Human Validation (requires separate authorization).
```

### Sub-assessments

```
EXTENT_VALUE = ESSENTIAL (confirmed from previous phases)
CROSS_DOCUMENT_STATUS = DEMONSTRATED (5/5 PDFs, candidate level)
PURE_GEOMETRIC_ORGANIZATION_STATUS = NOT_DEMONSTRATED (185 texts/extent = noise)
SEMANTIC_BOUNDARY = IDENTIFIED (caption_candidate ≠ caption; Organization → Interpretation)
M-A_READINESS = READY_FOR_DESIGN_RESEARCH → DESIGN_READY_WITH_CONDITIONS
```

---

## 21. Governance Status

```text
M-A_CAPTION_ASSOCIATION_DESIGN_RESEARCH = COMPLETE

M-A_STATUS = DESIGN_READY_WITH_CONDITIONS

RESEARCH_OBJECT = Text-Drawing Association (formally defined)
CAPTION_CANDIDATE = Evidence-grounded (FIG-prefix + near extent + spatial alignment)
  ≠ caption (semantic identity requires Hypothesis + Human Validation)

FIG_PREFIX_ROLE = CANDIDATE_SPACE_REDUCTION (Organization Support)
  126 candidates from 9257 texts (98.6% reduction)
  NOT semantic classification

SPATIAL_EVIDENCE:
  NECESSARY: multiple-drawing ambiguity handling
  SUPPORTING: distance, vertical ordering, x-overlap
  UNKNOWN: horizontal alignment
  NOT_REQUIRED: extent containment
  ALL thresholds: TO_BE_PRE_REGISTERED

SEMANTIC_BOUNDARY = IDENTIFIED
  Organization: caption_candidate (structural) — CAN produce
  Interpretation: caption (semantic) — CANNOT produce from evidence alone
  Caption vs Reference: semantic distinction, requires Human Validation
  Caption vs Footnote/Body: geometric limit identified, lexical signal essential

HUMAN_VALIDATION_UNIT = "Is this text associated with this drawing? (Yes/No)"
  Minimal, evidence-grounded, not reconstructive, not algorithmic

NATURAL_NEGATIVE_CONTROLS:
  Type A: 280 (FIG-prefix + NOT near extent)
  Type B: 9257 (proximity + NO FIG-prefix)

MULTIPLE_DRAWING_BOUNDARY: 7 pages (AMBIGUOUS for similar-distance cases)

VERTICAL_ORDERING: 87% below, 11% above, 2% inside (below is dominant, not universal)

H-MA HYPOTHESIS:
  Text-Drawing Spatial Association reduces candidate search space;
  final Caption Association remains semantic interpretation requiring Human validation.

READINESS GATE:
  RESEARCH_OBJECT_DEFINED       = PASS
  EVIDENCE_BOUNDARY_DEFINED     = PASS
  HUMAN_VALIDATION_UNIT_DEFINED = PASS
  POSITIVE_SET_DESIGNABLE       = CONDITIONAL
  NEGATIVE_SET_DESIGNABLE       = PASS
  BOUNDARY_SET_DESIGNABLE       = CONDITIONAL
  EVALUATION_PROTOCOL_DESIGNABLE= CONDITIONAL
  IMPLEMENTATION_READY          = FAIL

REMAINING CONDITIONS (before experiment):
  G1: Pre-register distance threshold (TO_BE_PRE_REGISTERED)
  G2: Pre-register x-overlap criterion (TO_BE_PRE_REGISTERED)
  G3: Execute Human Validation (NOT AUTHORIZED)
  G4: Construct validated sets (BLOCKED on G3)
  G5: Define acceptance criteria (BLOCKED on G3)
  G6: P1 atom splitting limitation (DESIGN_DECISION_REQUIRED)
  G7: Caption-vs-reference semantic boundary (ACCEPTED — route to Human Validation)

AO_VISUAL_GEOMETRY = IMPLEMENTED (COMPLETE)
AO_VALUE_EXPERIMENT = COMPLETE (VALUE_PARTIALLY_SUPPORTED)
EVIDENCE_ORGANIZATION_DIAGNOSTIC = COMPLETE (PARTIALLY_TESTABLE)
EVIDENCE_ORGANIZATION_INDEPENDENCE = COMPLETE (CONDITIONAL)
M-A_DESIGN_RESEARCH = COMPLETE (DESIGN_READY_WITH_CONDITIONS)

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
EXPERIMENT = NOT AUTHORIZED
HUMAN_VALIDATION = NOT AUTHORIZED
HUMAN_FEEDBACK = NOT AUTHORIZED
L3 = NOT AUTHORIZED

STOP = TRUE
```

---

## Research Principle Adherence

- ✅ Used only existing evidence (5 PDFs, 126 candidates, 280+9257 negatives)
- ✅ No new corpus creation
- ✅ No threshold values pre-registered (all TO_BE_PRE_REGISTERED)
- ✅ No implementation
- ✅ No experiment execution
- ✅ No Human Validation execution
- ✅ Strictly distinguished caption_candidate ≠ caption
- ✅ FIG-prefix = Organization Support (not Interpretation)
- ✅ Semantic boundary identified (not hidden)
- ✅ Human Validation unit is minimal (not reconstructive)
- ✅ Multiple-drawing boundary analyzed (not ignored)
- ✅ Caption vs Reference boundary identified (semantic, legitimate)
- ✅ P1 atom splitting limitation reported honestly
- ✅ Cross-document independence at candidate level (not claimed at validated level)
- ✅ H-MA is hypothesis (not verified conclusion)
- ✅ Did NOT claim caption detection works
- ✅ Did NOT claim accuracy improvement
- ✅ Did NOT modify any code/AO/P1-P7/TLD/IS-11
- ✅ Frozen baseline intact
- ✅ DESIGN_READY ≠ IMPLEMENTATION_READY (confirmed)

`STOP = TRUE`.
