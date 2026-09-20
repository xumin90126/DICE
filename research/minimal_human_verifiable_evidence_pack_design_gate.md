# Minimal Human-Verifiable Evidence Pack Design Gate

> **模式: READ-ONLY DESIGN GATE / NO MODIFICATION / FROZEN INTACT / STOP**
> 日期: 2026-09-17
> 前置: Evidence Pack Completeness Diagnostic (PARTIALLY_SUPPORTED)
> 本文件: 判断 Human 完成 Text-Drawing Association 判断所需的最小充分 Evidence Pack 设计。

---

## 1. Executive Summary

```
Human difficulty in the M-A Pilot is NOT caused by missing observation or
missing semantic understanding. It is caused by existing Evidence not being
organized into the Pack:

  - 16 negative controls have same_y context hardcoded to empty
  - 2 Type A cases show "no drawing on page" when drawings DO exist
  - ±3pt same_y threshold misses context for 6 of 16 negatives

The minimum sufficient Evidence Pack is:
  TARGET_TEXT + ALL_PAGE_EXTENTS + SPATIAL_RELATION + SAME_Y_CONTEXT

This does NOT require semantic classification, LLM, or new algorithms.
It requires Evidence Pack redesign: unify the collection pipeline so ALL
cases (positive, negative, boundary) receive the same evidence fields.

3 of 14 UNCERTAIN cases are closer to genuine Semantic Boundary (context
was shown but Human still uncertain). 2 are inconclusive (Pack incomplete).
9 are evidence/packaging issues.
```

---

## 2. Gate Results

```
G1  DRAWING_EXTENT_POLICY          = CONDITIONAL
G2  CONTEXT_SCOPE                  = CONDITIONAL
G3  SAME_Y_POLICY                  = CONDITIONAL
G4  NEGATIVE_CONTROL_CONTEXT       = FAIL
G5  EVIDENCE_STATE                 = FAIL
G6  HUMAN_RECONSTRUCTION_BOUNDARY  = CONDITIONAL
G7  MINIMUM_SUFFICIENT_EVIDENCE    = CONDITIONAL
G8  CASE_TYPE_CONSISTENCY          = FAIL
G9  M_A_BOUNDARY                   = PASS
G10 IMPLEMENTATION_SCOPE           = PASS
```

### Gate Result Summary

```
PASS:         2  (G9, G10)
CONDITIONAL:  6  (G1, G2, G3, G6, G7)
FAIL:         3  (G4, G5, G8)

DESIGN_READY = CONDITIONAL
  → Design direction is clear (unify pipeline, show all extents + context)
  → 3 specific parameters need pre-registration before implementation
  → 3 FAILs are all in the current implementation, not the design concept
```

---

## 3. Gate Analysis

### G1 — Drawing Extent Policy

```
Question: Should Pack show A) nearest extent, B) nearby extents, C) all page extents, D) other?

ANALYSIS:
  Current: only nearest extent within 60pt is stored (generate_data.py line 55-62)
  Type A: extent_bbox = None even when extents exist on page

  Real data check:
    Max extents on any page in corpus: 3 (arxiv p12)
    Type A cases with DEF>0 on page: 3 of 8
      - efficientnet p4: 2 extents (72pt, 146pt from text)
      - med_001 p15: 1 extent (264pt from text)
      - arxiv p10: 1 extent (156pt from text)

  Multi-extent candidate pages: 8 of 36
    Cases on these pages: mostly YES (nearest extent was sufficient)
    → For candidates, nearest extent WAS sufficient
    → The issue is ONLY for Type A where nearest = None

  Would "ALL extents" cause Evidence Dump?
    Max 3 per page → NO, not a dump
    But: showing 3 extents with 3 distances may add visual clutter

  Key distinction:
    For Type A (text NOT near any extent):
      → Human needs to know: "drawing exists but is Npt away"
      → Currently sees: "no drawing on page" (FALSE)
      → Fix: show nearest extent even if >60pt, with distance
    For candidates (text NEAR an extent):
      → Nearest extent is sufficient
      → Other extents on page are not needed (Human can see page image)

DRAWING_EXTENT_POLICY = B+ (show nearest extent ALWAYS, even if far)
  → If text is near (<60pt): show nearest extent (current behavior, works)
  → If text is NOT near: show nearest extent with distance (current: shows None)
  → Do NOT show ALL extents (unnecessary for candidates, only nearest matters)
  → The page image already shows all drawings visually

RATIONALE:
  - "ALL extents" is NOT necessary — the page image shows them visually
  - What IS necessary: never show "None" when an extent exists
  - The Pack needs the nearest extent + its distance, ALWAYS
  - If DEF=0 on page: show "NO_VISUAL_EVIDENCE_OBSERVED" (true state)
  - If DEF>0 but text is far: show "drawing at Npt" (not "no drawing")

HUMAN_BURDEN:
  - With policy B+: Human always knows if a drawing exists and how far
  - No need to scan page image to find drawings
  - No Evidence Dump (max 1 extent shown in Pack, page image shows rest)

G1 = CONDITIONAL
  → Policy B+ is justified by data
  → But the specific "how far is still relevant" threshold is NOT pre-registered
  → Current 60pt cutoff is a generation parameter, not a Pack design parameter
  → Needs pre-registration before implementation
```

### G2 — Context Scope

```
Question: How much text context does Human need?

ANALYSIS:
  Judgment vs context availability:
    YES with context:    56  (all candidates with context)
    YES without context:  5  (all negatives — Pack incomplete)
    NO with context:      4  (all had same_y shown)
    NO without context:   0
    UNC with context:     3  (ambiguous_fragment — semantic boundary candidates)
    UNC without context: 11  (all negatives — Pack incomplete)

  → ALL definitive judgments (YES+NO=65) with context present: 60/65 = 92.3%
  → ALL UNCERTAIN without context: 11/14 = 78.6%
  → Context presence strongly correlates with definitive judgment

  same_y context analysis:
    - Captures all atoms on the same horizontal line (±3pt)
    - For captions: captures full caption text (1-2 lines) → SUFFICIENT
    - For body text: captures one line of paragraph → PARTIAL but SUFFICIENT
      (Human can identify "We omit ensemble..." as body text from one line)
    - Truncated at 200 chars (generate_data.py line 106)

  Is same_y = sentence?
    - NOT always. same_y captures one visual line.
    - A sentence may wrap across 2-3 lines.
    - But for Association Judgment, one line is usually sufficient:
      → "We omit ensemble and multi-crop models" → clearly body text
      → "in Figure 3 (left) show that..." → clearly reference
      → "Figure 3. Scaling Up a Baseline Model..." → clearly caption

  Do we need sentence-level or paragraph-level context?
    - For the 4 Pack-incomplete cases: same_y (one line) is SUFFICIENT (E1 analysis)
    - For the 3 semantic boundary cases: same_y WAS shown, still UNCERTAIN
      → More context (sentence/paragraph) MIGHT help, but untested
      → Cannot claim sentence/paragraph is REQUIRED based on current data

CONTEXT_SCOPE = SAME_Y_CONTEXT (one visual line, ±threshold)
  SAME_Y_CONTEXT     = REQUIRED (for all cases)
  SENTENCE_CONTEXT   = NOT_REQUIRED (same_y suffices for tested cases)
  PARAGRAPH_CONTEXT  = NOT_REQUIRED (would be Document Dump)
  PAGE_CONTEXT       = NOT_REQUIRED (page image already provided)
  CROSS_PAGE_CONTEXT = NOT_REQUIRED (not needed for any tested case)

RATIONALE:
  - same_y context is the minimal context that resolves 4/4 Pack-incomplete cases
  - same_y context is already available in P2 (no new observation needed)
  - Sentence/paragraph context would increase burden without proven benefit
  - Cross-page context is NOT needed (all 4 cases resolved with same-page evidence)

G2 = CONDITIONAL
  → same_y is clearly the right scope
  → But the ±threshold parameter needs pre-registration (see G3)
  → And whether same_y suffices for the 2 inconclusive Type_B cases is untested
```

### G3 — SAME_Y Parameter

```
Question: Is ±3pt sufficient, or should it be ±5pt?

ANALYSIS (READ-ONLY measurement, no code modification):
  Compared ±3pt vs ±5pt for all 79 cases:

  Negatives (16 cases):
    Cases where ±3pt ≠ ±5pt: 6 of 16
      - ", with":          ±3pt=22  ±5pt=24  (+2 atoms)
      - "the":             ±3pt=19  ±5pt=20  (+1 atom)
      - "Figure" (p18):    ±3pt=32  ±5pt=35  (+3 atoms)
      - "figure" (p15):    ±3pt=21  ±5pt=24  (+3 atoms)
      - "Fig. 6 shows...": ±3pt=9   ±5pt=29  (+20 atoms!)
      - "max":             ±3pt=0   ±5pt=19  (+19 atoms!)

  Candidates (63 cases):
    Cases where ±3pt ≠ ±5pt: 11 of 63

  Critical case: "max" (med_001 p15)
    ±3pt: 0 atoms → context completely empty
    ±5pt: 19 atoms → "stemming from the Coulomb matrix denoted as CM(ϵ, max, ..."
    → ±3pt causes TOTAL context loss for this case

  Critical case: "Fig. 6 shows..." (resnet p7)
    ±3pt: 9 atoms
    ±5pt: 29 atoms → significantly more context
    → ±3pt captures only partial context

  Would ±5pt introduce irrelevant context?
    - ±5pt adds atoms from adjacent lines (4-5pt y-offset)
    - In PDF text, line height is typically 10-12pt
    - ±5pt may capture atoms from the PREVIOUS or NEXT line
    - This could introduce irrelevant atoms
    - But: for "max" (±3pt=0), ±5pt=19 captures the correct same line
      → The 4.9pt offset is within the same visual line, not adjacent line
    - For "Fig. 6 shows" (±3pt=9, ±5pt=29): the extra 20 atoms may include
      adjacent line content — needs visual verification

SAME_Y_POLICY = REQUIRED, parameter NOT YET DETERMINED
  PARAMETER = NOT YET DETERMINED
  PARAMETER_STATUS = TO_BE_PRE_REGISTERED

RATIONALE:
  - ±3pt is clearly insufficient (causes total context loss for "max")
  - ±5pt resolves "max" but may introduce noise for other cases
  - The correct parameter may be between 3 and 5, or may need to be
    adaptive (based on line height)
  - This MUST be pre-registered before implementation, NOT tuned on results
  - Current evidence shows ±3pt is too narrow but does NOT prove ±5pt is optimal

G3 = CONDITIONAL
  → ±3pt is demonstrably insufficient (data-driven finding)
  → ±5pt is promising but NOT proven optimal
  → Parameter must be pre-registered, not reverse-engineered from results
```

### G4 — Negative Control Context

```
Question: Should negatives use the same Evidence Collection Pipeline?

ANALYSIS:
  Current state (generate_data.py):
    Candidates (63):  context_text collected, context_atoms collected ✓
    Type A (8):       context_text = '' (hardcoded), context_atoms = [] (hardcoded)
    Type B (8):       context_text = '' (hardcoded), context_atoms = [] (hardcoded)

  This means:
    - 63 candidates: Human sees same_y context → can judge
    - 16 negatives:  Human sees NO context → must reconstruct document

  Is this evidence-availability-driven?
    NO. The same_y atoms EXIST for all 16 negatives (verified in G3 analysis):
      - "max": 19 atoms available at ±5pt (0 shown)
      - "omit": 29 atoms available at ±3pt (0 shown)
      - "Figure" (Type A): 21-32 atoms available (0 shown)

  The context is NOT missing from the system.
  The context is missing from the Pack because the script hardcodes it empty.

  Principle violation:
    "Case Type can differ, but Evidence Collection should not differ
     to produce expected results."

    If negatives have LESS evidence than positives, Human cannot fairly
    judge them. The comparison is biased:
      - Positives: Human has full evidence → can confirm association
      - Negatives: Human has partial evidence → forced to UNCERTAIN
      - This makes negatives LOOK harder than they are

NEGATIVE_CONTROL_CONTEXT = MUST_BE_UNIFIED
  NEGATIVE_CONTROL_EVIDENCE_PIPELINE = UNIFIED (should be)
  EMPTY_CONTEXT_MEANING = must distinguish:
    - TRUE_EMPTY: no same_y atoms exist (genuine evidence absence)
    - COLLECTOR_EMPTY: atoms exist but were not collected (current bug)

  A field should be empty ONLY when no same_y atoms exist.
  It should NOT be empty because the case type triggered a hardcoded skip.

G4 = FAIL
  → Current pipeline is NOT unified
  → Negatives have hardcoded empty context
  → This is a script-design flaw, not evidence-availability-driven
  → Must be fixed (as DESIGN_GAP) before any re-run
```

### G5 — Evidence State

```
Question: What does "extent = None" mean?

ANALYSIS:
  Current app.js logic (line 152-157):
    if extent_bbox is not null → "已在页面中标出" (shown on page)
    if extent_bbox is null     → "本页未识别到图形区域" (no drawing on page)

  Problem: "None" conflates 3 different states:
    State 1: Page truly has no drawing (DGF=0, DEF=0)
      → 5 Type A cases (efficientnet p3, med_001 p18, efficientnet p2,
        resnet p7, arxiv p11)
      → "no drawing on page" is TRUE

    State 2: Page has primitives but no extent formed (DGF>0, DEF=0)
      → 1 Type A case (efficientnet p2: DGF=233, DEF=0)
      → "no drawing on page" is MISLEADING (primitives exist but didn't aggregate)

    State 3: Page has extents but text is not near any (DGF>0, DEF>0, dist>60pt)
      → 2 Type A cases (efficientnet p4: DEF=2, med_001 p15: DEF=1)
      → "no drawing on page" is FALSE (drawings exist, just not near text)

  Human sees the SAME message for all 3 states → cannot distinguish

EVIDENCE_STATE_MODEL:
  Must distinguish at minimum:
    1. NO_VISUAL_EVIDENCE_OBSERVED (DGF=0, DEF=0) — truly nothing on page
    2. VISUAL_EVIDENCE_OBSERVED_BUT_NO_EXTENT (DGF>0, DEF=0) — primitives exist
    3. EXTENT_EXISTS_BUT_NOT_NEAR (DEF>0, min_dist>threshold) — drawing far from text
    4. EXTENT_NEAR (DEF>0, min_dist≤threshold) — drawing near text (current "shown")

  These are EVIDENCE states, NOT semantic labels.
  They describe what was observed, not what the drawing IS.

SEMANTIC_LEAKAGE = FALSE (if implemented correctly)
  → States 1-4 describe observation coverage, not figure/caption/table identity
  → No semantic label is introduced
  → Human still makes the association judgment

  However, State 2 ("primitives exist but no extent") reveals that the
  aggregation pipeline filtered something. This is an observation-level
  fact, not a semantic interpretation. It is safe to report.

G5 = FAIL
  → Current state model conflates 3 different conditions into 1 message
  → 2 of 3 states are MISLEADING to Human
  → Must be redesigned (as DESIGN_GAP) to distinguish states
  → The 4-state model is safe (no semantic leakage)
```

### G6 — Human Reconstruction Boundary

```
Question: Where does Evidence Compression end, Document Reconstruction begin?

CURRENT BURDEN:
  Candidates (63 cases):     NONE (Pack complete, Human judges directly)
  Type A (8 cases):          PAGE_CONTEXT (must scan page, find drawings)
  Type B (8 cases):          MULTI_SENTENCE_CONTEXT (must read surrounding text)
  Ambiguous UNC (3 cases):   LOCAL_CONTEXT (already provided) + semantic reasoning

DESIRED BURDEN:
  ALL cases: LOCAL_CONTEXT_ONLY
  Human should only need: target text + extent(s) + spatial relation + same_y context

MINIMUM_EVIDENCE_BOUNDARY:
  Evidence Compression ENDS at: same_y context + nearest extent + spatial relation
  Document Reconstruction STARTS at: needing to read BEYOND the same_y line

  If Human needs to read beyond same_y → Pack is incomplete
  If Human can judge from same_y + extent → Pack is sufficient

  Human should NOT:
    ✗ Open the PDF document
    ✗ Scan the entire page
    ✗ Read multiple paragraphs
    ✗ Navigate to other pages
    ✗ Build their own text-drawing relationship

  Human SHOULD:
    ✓ Read target text
    ✓ See drawing extent + distance
    ✓ Read same_y context (one line)
    ✓ Make semantic judgment

HUMAN_RECONSTRUCTION_BURDEN_CURRENT = PAGE_CONTEXT / MULTI_SENTENCE_CONTEXT (for negatives)
HUMAN_RECONSTRUCTION_BURDEN_DESIRED = LOCAL_CONTEXT_ONLY (for all cases)

G6 = CONDITIONAL
  → Boundary is clearly defined
  → But 3 ambiguous_fragment cases had complete Pack and were still UNCERTAIN
  → For those, the boundary may need to extend to "semantic reasoning"
  → This is NOT document reconstruction — it is semantic validation
  → The boundary holds: compression ends at same_y, reconstruction starts beyond
```

### G7 — Minimum Sufficient Evidence

```
Question: What is the minimal Evidence Pack?

REQUIRED (Human cannot judge without it):
  1. TARGET_TEXT — the text fragment to judge
     → Currently: PROVIDED for all 79 cases ✓
  
  2. NEAREST_DRAWING_EXTENT — the closest drawing extent on the page
     → Currently: PROVIDED for candidates + Type B, MISSING (None) for Type A
     → Must ALWAYS be provided, even if far from text
     → If DEF=0 on page: report NO_VISUAL_EVIDENCE_OBSERVED
  
  3. SPATIAL_RELATION — distance + vertical ordering + x-overlap
     → Currently: PROVIDED for candidates + Type B, MISSING for Type A
     → Must ALWAYS be provided (even if distance is large)
  
  4. SAME_Y_CONTEXT — same-line neighboring text atoms
     → Currently: PROVIDED for 63 candidates, MISSING for 16 negatives
     → Must be collected for ALL cases using unified pipeline

CONDITIONAL (needed for specific case types):
  5. EVIDENCE_STATE — which observation state (G5 model)
     → Needed for Type A to distinguish "no drawing" from "drawing far away"
     → Not needed for candidates (extent is always near)

OPTIONAL (helpful but not required):
  6. PAGE_IMAGE — visual page with overlays
     → Currently: PROVIDED for all cases ✓
     → Supports Human's visual verification but not strictly necessary for judgment
  
  7. TEXT_BBOX — text position on page
     → Currently: PROVIDED ✓
     → Used for SVG overlay highlighting

NOT_REQUIRED:
  8. ALL_EXTENTS_ON_PAGE — not needed (page image shows them visually)
     → Previous diagnostic suggested this, but G1 analysis shows it's unnecessary
     → Nearest extent + page image is sufficient
  
  9. SENTENCE_CONTEXT — not needed (same_y suffices for tested cases)
  10. PARAGRAPH_CONTEXT — not needed (would be Document Dump)
  11. CROSS_PAGE_CONTEXT — not needed for any tested case
  
  12. SEMANTIC_LABEL — NOT authorized (caption, figure, table, etc.)
  13. CONFIDENCE_SCORE — NOT authorized
  14. MACHINE_RECOMMENDATION — NOT authorized
  15. LLM_INTERPRETATION — NOT authorized

OVERLY_VERBOSE_EVIDENCE:
  - Showing ALL extents with ALL distances → clutter (max 3 per page, but unnecessary)
  - Full paragraph text → Document Dump
  - Cross-page drawing references → scope creep

MINIMAL_SUFFICIENT_EVIDENCE =
  1. TARGET_TEXT
  2. NEAREST_DRAWING_EXTENT (always, even if far; or NO_VISUAL_EVIDENCE_OBSERVED)
  3. SPATIAL_RELATION (distance + vertical_ordering + x_overlap)
  4. SAME_Y_CONTEXT (same-line text atoms, unified pipeline)
  5. EVIDENCE_STATE (4-state model, conditional for Type A)

G7 = CONDITIONAL
  → 4 REQUIRED items identified, 2 currently incomplete
  → EVIDENCE_STATE (item 5) needs design before implementation
  → same_y threshold (part of item 4) needs pre-registration
```

### G8 — Case-Type Consistency

```
Question: Should Positive/Negative/Boundary use the same Evidence Pack Schema?

ANALYSIS:
  Current evidence fields by case type:

  Field               Candidates(63)  TypeA(8)    TypeB(8)
  text_content        YES             YES         YES
  text_bbox           YES             YES         YES
  extent_bbox         YES             None        YES
  spatial_distance    YES             -1          YES
  vertical_ordering   YES             none        YES
  x_overlap           YES             False       YES
  context_text        YES             ''          ''
  context_atoms       YES             []          []

  PIPELINE_CONSISTENCY = FALSE

  3 fields differ between candidates and negatives:
    1. extent_bbox: set vs None (Type A loses extent info)
    2. spatial_distance: computed vs -1 (Type A loses spatial relation)
    3. context_text: collected vs '' (ALL negatives lose context)

  Is this evidence-availability-driven?
    NO. Verified:
    - Type A pages with DEF>0: extent EXISTS but was set to None (script choice)
    - Type B same_y atoms: EXIST (29 for "omit", 19 for "max") but not collected
    - Type A same_y atoms: EXIST (21-32) but not collected

  The differences are script-design-driven, NOT evidence-availability-driven.

  Principle:
    "Case Type can differ, but Evidence Collection should not differ
     to produce expected results."

    Current system VIOLATES this:
      - Negatives are given LESS evidence → harder to judge
      - This biases the experiment: negatives look more uncertain than they are
      - FPR and Boundary Rate may be inflated by Pack incompleteness

DESIGN:
  All Cases → Unified Evidence Pack
  - Same collection pipeline for ALL cases
  - Same fields populated (text, extent, spatial, context)
  - Fields may be empty ONLY when evidence genuinely doesn't exist
    (e.g., DEF=0 on page → extent genuinely absent)
  - Fields must NOT be empty because of case-type conditional logic

  Differences allowed:
    - extent_bbox may be None IF AND ONLY IF DEF=0 on page (genuine absence)
    - context_text may be '' IF AND ONLY IF no same_y atoms exist
    - These are evidence-availability-driven, not script-design-driven

G8 = FAIL
  → Current pipeline is NOT unified
  → 3 fields differ by case type due to script logic, not evidence availability
  → Must be unified before any re-run or Full Experiment
```

### G9 — M-A Boundary

```
Question: Does the Pack remain non-semantic?

ANALYSIS:
  The proposed Minimal Sufficient Evidence Pack contains ONLY:
    - TARGET_TEXT (raw text, no classification)
    - NEAREST_DRAWING_EXTENT (geometric bbox, no figure/caption label)
    - SPATIAL_RELATION (distance, ordering, overlap — pure geometry)
    - SAME_Y_CONTEXT (raw neighboring text, no interpretation)
    - EVIDENCE_STATE (observation coverage state, not semantic identity)

  NONE of these fields contain:
    - Caption/Figure/Table classification
    - Association score or confidence
    - Machine recommendation
    - Semantic role assignment
    - LLM interpretation

  The Evidence State model (G5) uses states like:
    NO_VISUAL_EVIDENCE_OBSERVED
    VISUAL_EVIDENCE_OBSERVED_BUT_NO_EXTENT
    EXTENT_EXISTS_BUT_NOT_NEAR
    EXTENT_NEAR

  These describe OBSERVATION COVERAGE, not semantic identity.
  "EXTENT_NEAR" means "a drawing extent was observed near the text" —
  this is a geometric fact, not a claim that "this is a figure caption."

  The Human still makes ALL semantic judgments:
    "Does this text describe this drawing?"
    "Is this a caption or a reference?"
    "Is this body text or a label?"

PACK_REMAINS_NON_SEMANTIC = TRUE

G9 = PASS
  → No semantic labels introduced
  → No scores, confidence, or recommendations
  → Human retains full semantic judgment authority
  → Evidence Pack provides only observation-level facts
```

### G10 — Implementation Scope

```
Question: If authorized, what would need to change?

IMPLEMENTATION_SCOPE:
  1. generate_data.py — collect_sampled_negatives() function
     → Remove hardcoded context_text='' and context_atoms=[]
     → Run same_y collection for negatives (same as candidates)
     → Store nearest extent even if >60pt (for Type A)
     → Add evidence_state field (4-state model)

  2. generate_data.py — collect_candidates() function
     → May need to also store evidence_state (currently implicit)
     → same_y threshold parameter needs pre-registration

  3. app.js — renderEvidencePanel() function
     → Update to display evidence_state (4 messages instead of 2)
     → Show "drawing at Npt" instead of "no drawing" when extent exists but far
     → Show same_y context for ALL cases (currently hidden if empty)

  4. Pre-registration document
     → same_y threshold (±3pt vs ±5pt vs other)
     → "Relevant" distance threshold (when is extent "near" vs "far")
     → Evidence state definitions

FILES_LIKELY_AFFECTED:
  - tmp/m_a_human_review_pilot/generate_data.py
  - tmp/m_a_human_review_pilot/assets/app.js
  - tmp/m_a_human_review_pilot/data/candidates_internal.json (regenerated)
  - tmp/m_a_human_review_pilot/data/candidates.json (regenerated)
  - tmp/m_a_human_review_pilot/data/candidates_embedded.js (regenerated)

FILES_MUST_REMAIN_FROZEN:
  - perception/sandbox/observations/atomic_text.py (P1)
  - tmp/perception/atomic_observation/drawing_geometry.py (DGF)
  - tmp/perception/atomic_observation/drawing_extent.py (DEF)
  - chunker/table_line_detector.py (TLD)
  - chunker/layout_analyzer.py
  - tmp/is11_semantic_ground_truth.json (GT)
  - Any M-A algorithm code
  - Any P2/P5/P6 code

G10 = PASS
  → Scope is clearly defined
  → Only 2 files need modification (generate_data.py + app.js)
  → All frozen files remain untouched
  → No new detectors, classifiers, or algorithms needed
```

---

## 4. Final Design

```
DESIGN_READY = CONDITIONAL

  The design concept is clear and evidence-supported:
    → Unify evidence collection pipeline for ALL cases
    → Show nearest extent ALWAYS (even if far)
    → Collect same_y context for ALL cases
    → Distinguish 4 evidence states

  3 parameters need pre-registration before implementation:
    PR1: same_y threshold (±3pt insufficient, ±5pt promising, NOT yet determined)
    PR2: "near" vs "far" distance threshold (current 60pt, needs review)
    PR3: evidence_state definitions (4-state model, needs formal specification)

  3 FAILs (G4, G5, G8) are all in current implementation, not design concept:
    → G4 FAIL: negatives have hardcoded empty context (fix: unify pipeline)
    → G5 FAIL: extent=None conflates 3 states (fix: 4-state model)
    → G8 FAIL: pipeline differs by case type (fix: unified collection)

MINIMAL_SUFFICIENT_EVIDENCE =
  1. TARGET_TEXT
  2. NEAREST_DRAWING_EXTENT (always provided; or NO_VISUAL_EVIDENCE_OBSERVED)
  3. SPATIAL_RELATION (distance + vertical_ordering + x_overlap)
  4. SAME_Y_CONTEXT (unified collection for ALL cases)
  5. EVIDENCE_STATE (4-state model: NO_EVIDENCE / PRIMITIVES_NO_EXTENT / EXTENT_FAR / EXTENT_NEAR)

DRAWING_EXTENT_POLICY = B+ (nearest extent always, even if far; page image shows rest)

CONTEXT_SCOPE = SAME_Y_CONTEXT (one visual line)
  SENTENCE_CONTEXT = NOT_REQUIRED
  PARAGRAPH_CONTEXT = NOT_REQUIRED
  PAGE_CONTEXT = NOT_REQUIRED
  CROSS_PAGE_CONTEXT = NOT_REQUIRED

SAME_Y_CONTEXT = REQUIRED (unified pipeline, parameter TO_BE_PRE_REGISTERED)

NEGATIVE_CONTROL_CONTEXT = MUST_BE_UNIFIED (same pipeline as candidates)

EVIDENCE_STATE_MODEL = 4-STATE
  1. NO_VISUAL_EVIDENCE_OBSERVED (DGF=0, DEF=0)
  2. PRIMITIVES_EXIST_NO_EXTENT (DGF>0, DEF=0)
  3. EXTENT_EXISTS_BUT_FAR (DEF>0, min_dist>threshold)
  4. EXTENT_NEAR (DEF>0, min_dist≤threshold)

HUMAN_RECONSTRUCTION_BURDEN =
  CURRENT: PAGE_CONTEXT / MULTI_SENTENCE_CONTEXT (for negatives)
  DESIRED: LOCAL_CONTEXT_ONLY (for all cases)

PACK_REMAINS_NON_SEMANTIC = TRUE
```

---

## 5. What We Should NOT Add

```
NOT NEEDED in Evidence Pack:
  - ALL extents on page (page image shows them; nearest is sufficient)
  - Sentence-level context (same_y suffices for tested cases)
  - Paragraph-level context (would be Document Dump)
  - Cross-page drawing references (not needed for any tested case)
  - Previous/next page context (scope creep)

SHOULD NOT BE DEVELOPED NOW:
  - Caption detector / classifier
  - Semantic role assigner
  - Association score / confidence
  - Machine recommendation system
  - LLM-based text interpretation
  - Vision-language model integration
  - Threshold tuning / optimization
  - ROC curve / parameter sweep

FIELDS THAT MUST NOT ENTER THE PACK:
  - caption = TRUE/FALSE
  - figure_caption = TRUE/FALSE
  - association_score = 0.93
  - machine_recommendation = "YES"
  - semantic_role = "caption" / "reference" / "body_text"
  - confidence = 0.87
  - ranking = 1/5
```

---

## 6. Implementation Boundary

```
IF future authorization is granted, the minimum changes would be:

1. generate_data.py (Evidence Pack generation):
   - Unify collect_candidates() and collect_sampled_negatives() context collection
   - Remove hardcoded context_text='' for negatives
   - Store nearest extent for Type A (even if >60pt)
   - Add evidence_state field (4-state model)
   - Pre-register same_y threshold parameter

2. app.js (Evidence Pack display):
   - Update renderEvidencePanel() for 4-state evidence model
   - Show "drawing at Npt" when extent exists but is far
   - Display same_y context for ALL cases

3. Pre-registration document:
   - same_y threshold (PR1)
   - near/far distance threshold (PR2)
   - evidence_state definitions (PR3)

NO changes to:
  - P1 (atomic_text.py) — FROZEN
  - DGF (drawing_geometry.py) — FROZEN
  - DEF (drawing_extent.py) — FROZEN
  - TLD (table_line_detector.py) — FROZEN
  - layout_analyzer.py — FROZEN
  - GT (is11_semantic_ground_truth.json) — FROZEN
  - Any M-A algorithm — NOT AUTHORIZED
  - Any P2/P5/P6 code — FROZEN

IMPLEMENTATION_AUTHORIZED = FALSE (this is design only)
```

---

## 7. Semantic Boundary Re-Assessment

```
Previous pilot analysis: 5 of 14 UNCERTAIN = "Possible Semantic Boundary"
This gate re-assessed all 5:

  3 ambiguous_fragment "Fig." cases:
    → same_y context WAS shown (e.g., "in Fig. 9, are clearly visible")
    → Human SAW context but was STILL uncertain
    → This IS closer to genuine semantic boundary:
      "Fig." near a drawing, context says "in Fig. 9" —
      is this a caption for THIS drawing or a reference to Fig. 9?
    → ASSESSMENT: POSSIBLE_SEMANTIC_BOUNDARY (3 cases)

  2 Type_B cases (", with" and "scaling"):
    → same_y context was NOT shown (hardcoded empty)
    → CANNOT determine if semantic boundary — Pack incomplete
    → ASSESSMENT: INCONCLUSIVE (2 cases)

REVISED SEMANTIC BOUNDARY COUNT:
  TRUE_SEMANTIC_BOUNDARY (context present, still uncertain): 3/14
  INCONCLUSIVE (Pack incomplete, cannot assess):             2/14
  EVIDENCE_INSUFFICIENCY (fixable):                          9/14

  → Cannot claim 5 semantic boundary — 2 are Pack-incomplete
  → After Pack fix, the 2 inconclusive cases should be re-evaluated
  → Only then can true semantic boundary count be determined
```

---

## 8. Governance

```
IMPLEMENTATION_AUTHORIZED = FALSE
EXPERIMENT_AUTHORIZED = FALSE
HUMAN_VALIDATION_AUTHORIZED = FALSE
HUMAN_FEEDBACK = NOT_AUTHORIZED
L3 = NOT_AUTHORIZED
CAPABILITY = NOT_AUTHORIZED
RUNTIME_AUTHORITY = ZERO
PRODUCTION = FALSE

FROZEN_BASELINE = INTACT
FROZEN_DRIFT = 0
  P1: 74d23ec784d65782 (UNCHANGED)
  TLD: 022f5c21e872ad9e (UNCHANGED)
  GT: 7349963d0d23b5ef (UNCHANGED)
  layout_analyzer: 8f69f0d206b3e565 (UNCHANGED)
  DGF: f25a5ff41afa1bec (UNCHANGED)
  DEF: cba9e583517f8967 (UNCHANGED)
  generate_data.py: 18776af7e2f203ff (UNCHANGED)
  app.js: 8b7f4122b06f315d (UNCHANGED)

No code modified.
No data modified.
No thresholds changed.
No Evidence Pack modified.
No Human Validation re-run.

DESIGN_GAPS recorded (NOT implemented):
  DG1: Unify evidence collection pipeline (remove hardcoded empty context)
  DG2: Store nearest extent for Type A (even if >60pt)
  DG3: Add 4-state evidence_state model
  DG4: Pre-register same_y threshold (±3pt insufficient, ±5pt promising)
  DG5: Pre-register near/far distance threshold

STOP = TRUE
```

---

## Research Principle Adherence

- ✅ Analyzed ALL 79 cases for extent/context availability (not just 4)
- ✅ Verified "ALL extents" would NOT cause Evidence Dump (max 3/page)
- ✅ Compared ±3pt vs ±5pt for all 79 cases (data-driven, not guessed)
- ✅ Identified that "ALL extents" is NOT necessary (page image suffices)
- ✅ Re-assessed 5 semantic boundary cases (3 confirmed, 2 inconclusive)
- ✅ Distinguished evidence-availability-driven vs script-design-driven gaps
- ✅ Did NOT modify any code
- ✅ Did NOT tune any thresholds
- ✅ Did NOT re-run Human Validation
- ✅ Did NOT claim semantic boundary for Pack-incomplete cases
- ✅ Did NOT introduce semantic labels in Pack design
- ✅ Recorded DESIGN_GAPS without implementing
- ✅ Frozen baseline intact (drift=0)
- ✅ STOP = TRUE

`STOP = TRUE`.
