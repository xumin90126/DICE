# Evidence Pack Completeness Diagnostic

> **模式: READ-ONLY RESEARCH / DIAGNOSTIC ONLY / NO MODIFICATION / FROZEN INTACT / STOP**
> 日期: 2026-09-17
> 前置: M-A Evidence Sufficiency Gap Diagnostic (PRIMARY_BOTTLENECK=EVIDENCE_PACK_COMPLETENESS)
> 本文件: 诊断 Human Review Evidence Pack 的完整性与最小上下文需求。

---

## 1. Executive Summary

```
This diagnostic examines 4 cases where the previous Evidence Sufficiency Gap
Diagnostic found "EVIDENCE_SUFFICIENT_BUT_CURRENT_PACK_INCOMPLETE" — meaning
evidence existed in the system but was not presented to the Human reviewer.

ROOT CAUSE FOUND:
  The data generation script (generate_data.py) hardcodes:
    context_text = ''
    context_atoms = []
  for ALL 16 negative controls (Type A + Type B).

  For the 63 candidate cases, same_y context WAS collected and shown.
  For the 16 negative controls, same_y context was NOT collected at all.

  Additionally, for Type A negatives:
    extent_bbox = None
  even when extents DO exist on the page — because the script only stores
  the nearest extent if text is within 60pt. For Type A (text NOT near
  any extent), extent_bbox is set to None, causing the Evidence Pack to
  display "本页未识别到图形区域" (no drawing region on this page) — which
  is FALSE when extents exist elsewhere on the page.

E0 vs E1 COMPARISON:
  E0 = what Human actually saw (current Evidence Pack)
  E1 = what system already had (complete existing evidence)

  For ALL 4 cases:
    E0 = INSUFFICIENT (Human could not judge → UNCERTAIN)
    E1 = SUFFICIENT (Human could theoretically judge with existing evidence)

  The evidence EXISTS. The Pack did not deliver it.

DOCUMENT RECONSTRUCTION BURDEN:
  With E0 (current pack): Human needs PAGE_CONTEXT or MULTI_SENTENCE_CONTEXT
  With E1 (complete evidence): Human needs only LOCAL_CONTEXT_ONLY

  The Pack incompleteness CAUSES unnecessary document reconstruction.
  Human is forced to "reconstruct" rather than "validate".

SEMANTIC_BOUNDARY:
  NOT_DEMONSTRATED — all 4 cases can be resolved with existing evidence.
  No case requires semantic interpretation beyond what Human can do
  with complete same-page evidence.

CONCLUSION:
  The bottleneck is NOT "missing new Evidence" or "missing semantic understanding".
  The bottleneck is "existing Evidence not organized into the Pack".

  Next research focus should be:
    Evidence Pack / Evidence Organization:
    how to compress existing Evidence into Human-verifiable minimal evidence units.
  NOT:
    "stronger Caption Detector" or "semantic classifier".
```

---

## 2. Human Observation

```
HUMAN_OBSERVATION (Qualitative — not quantitative):

  "当前 Review 页面同时提供了文字片段和图片，但文字与图片之间存在一定
  空间距离。仅凭当前展示的文字片段与图片，Human 很难判断该文字是否
  真正描述该图片。为了精准判断，Human 往往需要重新阅读文档中的前后文
  甚至更大范围的内容，这会显著增加 Review 成本，并使 Human 从'验证
  Evidence'退化为'重新理解 Document'。"

USAGE POLICY:
  - This is a qualitative observation from a single Human reviewer.
  - It is NOT a quantitative measurement (no time, NASA-TLX, or rating data).
  - It is used as a RESEARCH INPUT to guide diagnostic direction.
  - It must be VERIFIED against actual Evidence data, not taken as conclusion.
  - It must NOT be used to claim "low cognitive load" or "high cognitive load".

DICE PRINCIPLE CHECK:
  "Human should validate, not reconstruct."
  "DICE should compress evidence for humans, not transfer abstraction work to humans."

  The Human observation suggests the current Pack violates both principles:
    → Human is reconstructing (reading document context)
    → DICE is transferring abstraction work (Human must build own context)
```

---

## 3. Research Question

```
A Human must judge Text-Drawing Association. What is the MINIMAL Evidence
the Human needs? Does the current Evidence Pack provide it?

Focus chain:
  Existing Evidence → Evidence Pack → Human Association Judgment

NOT focused on:
  Document → Machine Semantic Understanding
```

---

## 4. Scope and Frozen Baseline

```
SCOPE:
  4 target cases (from Evidence Sufficiency Gap Diagnostic):
    #2: is11_efficientnet_p4_66_331   (Type A, text="Figure")
    #5: is11_med_001_p15_498_107      (Type A, text="figure")
    #6: is11_efficientnet_p6_79_415   (Type B, text="omit")
    #9: is11_med_001_p15_244_342      (Type B, text="max")

  2 reference cases (for comparison — what a COMPLETE Pack looks like):
    caption_like YES: is11_efficientnet_p4_55_218 (text="Figure 3.")
    ambiguous YES:    is11_resnet_p6_478_168 (text="Fig.")

FROZEN BASELINE: INTACT (drift=0/4)
  P1: 74d23ec784d65782 (UNCHANGED)
  TLD: 022f5c21e872ad9e (UNCHANGED)
  GT: 7349963d0d23b5ef (UNCHANGED)
  layout_analyzer: 8f69f0d206b3e565 (UNCHANGED)
  DGF: f25a5ff41afa1bec (UNCHANGED)
  DEF: cba9e583517f8967 (UNCHANGED)

HUMAN_VALIDATION_DATA: UNCHANGED
M-A_ALGORITHM: UNCHANGED
generate_data.py: UNCHANGED (READ-ONLY analysis only)
```

---

## 5. Four Target Cases

| # | case_id | document | page | text | type | Human judgment |
|---|---------|----------|------|------|------|----------------|
| #2 | is11_efficientnet_p4_66_331 | efficientnet | 4 | Figure | Type A | UNCERTAIN |
| #5 | is11_med_001_p15_498_107 | med_001 | 15 | figure | Type A | UNCERTAIN |
| #6 | is11_efficientnet_p6_79_415 | efficientnet | 6 | omit | Type B | UNCERTAIN |
| #9 | is11_med_001_p15_244_342 | med_001 | 15 | max | Type B | UNCERTAIN |

```
All 4 cases: Human judgment = UNCERTAIN
All 4 cases: Previous diagnostic = EVIDENCE_SUFFICIENT_BUT_CURRENT_PACK_INCOMPLETE
```

---

## 6. Current Evidence Pack Reconstruction

### What the Evidence Pack showed to Human (E0)

```
The review interface (app.js renderEvidencePanel) showed:
  1. text_content          → Target Text
  2. extent_bbox (yes/no)  → "已在页面中标出" or "本页未识别到图形区域"
  3. spatial_distance      → "距离 Xpt" (only if extent exists)
  4. vertical_ordering     → "位于图形区域下方/上方/内" (only if extent exists)
  5. context_text          → Context text (only if non-empty)
  6. Page image            → PDF page with SVG overlays for text + drawing

For reference cases (caption_like YES):
  ALL 6 fields populated → Human could judge → YES

For target cases:
  #2: text="Figure" + extent=None(FALSE) + distance=N/A + context=EMPTY
  #5: text="figure" + extent=None(FALSE) + distance=N/A + context=EMPTY
  #6: text="omit"   + extent=shown + distance=21.9pt + above + context=EMPTY
  #9: text="max"    + extent=shown + distance=33.1pt + above + context=EMPTY
```

### ROOT CAUSE: generate_data.py

```
In generate_data.py:

  collect_candidates() (lines 96-106):
    → Collects same_y context (±3pt) for ALL candidate cases
    → context_text = joined text of same_y atoms
    → context_atoms = list of same_y atom objects

  collect_sampled_negatives() (lines 168-219):
    → Type A (line 183): context_text = '' (HARDCODED EMPTY)
    → Type A (line 184): context_atoms = [] (HARDCODED EMPTY)
    → Type B (line 216): context_text = '' (HARDCODED EMPTY)
    → Type B (line 217): context_atoms = [] (HARDCODED EMPTY)

  Result:
    63 candidates: context collected and shown ✓
    16 negatives: context NOT collected at all ✗

  Additionally, for Type A:
    extent_bbox = None (line 176)
    → Even when extents EXIST on the page, Pack shows "no drawing region"
    → This is because the script only stores the NEAREST extent
      if text is within 60pt. For Type A (not near), extent=None.
    → The Pack does not distinguish "no extent on page" from
      "extent exists but text is not near it".
```

---

## 7. System Evidence vs Human-Visible Evidence

### E0 (what Human saw) vs E1 (what system had)

```
#2 (efficientnet p4, "Figure"):
  E0: text="Figure" + "本页未识别到图形区域" (FALSE) + no context
  E1: 2 extents on page [87,74,529,184] and [313,268,535,441]
      + same_y: "in Figure in 3 3 (left) show that the accuracy quickly saturates"
      → Extent 1 is 146pt from text, Extent 2 is 72pt from text
      → Context reveals: "in Figure 3 (left) show that..." = in-text reference

#5 (med_001 p15, "figure"):
  E0: text="figure" + "本页未识别到图形区域" (FALSE) + no context
  E1: 1 extent on page [123,382,525,527]
      + same_y: "under the curve AUC(fmolecule), f), and five inner products... The figure"
      → Extent is 264pt from text (very far)
      → Context reveals: body text containing "figure" as common noun

#6 (efficientnet p6, "omit"):
  E0: text="omit" + extent shown [307,445,532,625] + 21.9pt above + no context
  E1: same_y (29 atoms): "We omit ensemble and multi-crop models (Hu et al., 2018)..."
      → Context reveals: "We [omit] ensemble and multi-crop models" = body text

#9 (med_001 p15, "max"):
  E0: text="max" + extent shown [123,382,525,527] + 33.1pt above + no context
  E1: same_y (29 atoms at ±5pt, 0 at ±3pt):
      "stemming from the Coulomb matrix denoted as CM(ϵ, max, ..."
      → Context reveals: mathematical notation, NOT figure label
      → ADDITIONAL ISSUE: ±3pt threshold misses context (delta=4.9pt)
```

### Reference Case (what a COMPLETE Pack looks like)

```
caption_like YES (efficientnet p4, "Figure 3."):
  text="Figure 3."
  extent=[87.5, 74.6, 529.5, 184.4] (shown)
  distance=33.7pt below (shown)
  context="Figure 3. Scaling Up a Baseline Model with Different Network Width..."
  → ALL fields populated → Human judged YES

ambiguous YES (resnet p6, "Fig."):
  text="Fig."
  extent=[333.8, 72.0, 535.9, 143.0] (shown)
  distance=25.1pt below (shown)
  context="building block (on 56×56 feature maps) as in Fig. 3 for ResNet-"
  → ALL fields populated → Human judged YES
```

---

## 8. Evidence Availability Matrix

### Case #2 (efficientnet p4, "Figure")

| Evidence | System Available | Pack Available | Human Saw | Missing? |
|----------|:----------------:|:--------------:|:---------:|:-------:|
| target text | YES | YES | YES | — |
| target text bbox | YES | YES | YES | — |
| drawing image (page) | YES | YES | YES | — |
| drawing bbox (nearest) | YES | NO (None) | NO | YES |
| drawing bbox (ALL extents) | YES (2 extents) | NO | NO | YES |
| distance | YES (146pt, 72pt) | NO (-1) | NO | YES |
| x-overlap | YES | NO | NO | YES |
| vertical relation | YES | NO (none) | NO | YES |
| FIG-prefix | YES | YES (implicit) | YES | — |
| previous text | YES | NO | NO | YES |
| next text | YES | NO | NO | YES |
| same_y context | YES (29 atoms) | NO (empty) | NO | YES |
| page-level context | YES | NO | NO | YES |
| cross-page reference | YES (text says "Figure 3") | NO | NO | — |

### Case #6 (efficientnet p6, "omit")

| Evidence | System Available | Pack Available | Human Saw | Missing? |
|----------|:----------------:|:--------------:|:---------:|:-------:|
| target text | YES | YES | YES | — |
| target text bbox | YES | YES | YES | — |
| drawing image (page) | YES | YES | YES | — |
| drawing bbox | YES | YES | YES | — |
| distance | YES | YES (21.9pt) | YES | — |
| x-overlap | YES | NO | NO | YES |
| vertical relation | YES | YES (above) | YES | — |
| FIG-prefix | NO (not FIG) | NO | NO | — |
| previous text | YES | NO | NO | YES |
| next text | YES | NO | NO | YES |
| same_y context | YES (29 atoms) | NO (empty) | NO | YES |
| page-level context | YES | NO | NO | YES |

### Pattern

```
For ALL 4 target cases:
  - Target text: SHOWN ✓
  - Drawing extent: SHOWN for Type B (#6, #9), NOT SHOWN (false None) for Type A (#2, #5)
  - Spatial relation: SHOWN for Type B, NOT SHOWN for Type A
  - Same_y context: NOT SHOWN for ALL 4 (hardcoded empty for negatives)

For reference cases (caption_like YES):
  - ALL fields populated ✓
  - Same_y context WAS collected and shown ✓

The difference between SUCCESS and UNCERTAIN is:
  → Successful cases had same_y context shown
  → UNCERTAIN cases had same_y context hidden (because they are negatives)
```

---

## 9. Human Evidence Sufficiency Analysis

### E1 Human Sufficiency (counterfactual: if ALL existing evidence were shown)

```
#2 (efficientnet p4, "Figure"):
  E1 = 2 extents (146pt, 72pt away) + same_y "in Figure 3 (left) show that..."
  SUFFICIENCY = SUFFICIENT
  → Human can see: drawing exists but is far from text
  → Human can see: context says "in Figure 3" = in-text reference
  → Human can judge: NO (this text references a figure, does not describe nearby drawing)

#5 (med_001 p15, "figure"):
  E1 = 1 extent (264pt away) + same_y "under the curve AUC... The figure"
  SUFFICIENCY = SUFFICIENT
  → Human can see: drawing exists but is very far (264pt)
  → Human can see: context shows "figure" is used as common noun in body text
  → Human can judge: NO (body text, not a caption)

#6 (efficientnet p6, "omit"):
  E1 = extent (shown) + same_y "We omit ensemble and multi-crop models..."
  SUFFICIENCY = SUFFICIENT
  → Human can see: "We [omit] ensemble and multi-crop models" = body text
  → Human can judge: NO (body text, not a figure label)

#9 (med_001 p15, "max"):
  E1 = extent (shown) + same_y(±5pt) "stemming from the Coulomb matrix... CM(ϵ, max, ..."
  SUFFICIENCY = SUFFICIENT
  → Human can see: "CM(ϵ, [max], ...)" = mathematical notation
  → Human can judge: NO (math notation, not a figure label)

ALL 4 CASES: E1_HUMAN_SUFFICIENCY = SUFFICIENT
  → Existing evidence is ENOUGH for Human to make a judgment.
  → The problem is NOT missing evidence.
  → The problem is evidence not reaching the Human.
```

---

## 10. Context Granularity Analysis

```
Context levels (from finest to coarsest):
  A. Same-line context (same_y ±3-5pt)
  B. Same-y neighboring text (same_y band)
  C. Previous sentence
  D. Next sentence
  E. Same paragraph
  F. Previous paragraph
  G. Same page
  H. Previous page
  I. Next page
  J. Cross-page reference

For each target case, what level does Human ACTUALLY need?

#2 "Figure":
  Needs: A (same_y) — "in Figure 3 (left) show that the accuracy quickly saturates"
  → Same-line context reveals this is an in-text reference
  → Does NOT need paragraph or page context

#5 "figure":
  Needs: A (same_y) — "under the curve AUC... The figure"
  → Same-line context reveals "figure" is a common noun in body text
  → Does NOT need paragraph or page context

#6 "omit":
  Needs: A (same_y) — "We omit ensemble and multi-crop models..."
  → Same-line context reveals this is body text
  → Does NOT need paragraph or page context

#9 "max":
  Needs: A (same_y ±5pt) — "stemming from the Coulomb matrix... CM(ϵ, max, ..."
  → Same-line context reveals this is math notation
  → Does NOT need paragraph or page context
  → NOTE: ±3pt threshold MISSES this context (delta=4.9pt)

ALL 4 CASES: Minimal context needed = SAME_LINE (Level A)
  → Human does NOT need paragraph, page, or cross-page context.
  → Same_y context (already available in P2) is sufficient.
  → The Pack just didn't deliver it.
```

---

## 11. Document Reconstruction Burden

```
DOCUMENT_RECONSTRUCTION_BURDEN:

  With E0 (current Evidence Pack):
    #2: PAGE_CONTEXT — Human must scan page to find drawings and understand context
    #5: PAGE_CONTEXT — Human must scan page to find drawings and understand context
    #6: MULTI_SENTENCE_CONTEXT — Human must read surrounding text to understand "omit"
    #9: MULTI_SENTENCE_CONTEXT — Human must read surrounding text to understand "max"

  With E1 (complete existing evidence):
    #2: LOCAL_CONTEXT_ONLY — same_y "in Figure 3 (left)..." is enough
    #5: LOCAL_CONTEXT_ONLY — same_y "under the curve AUC... The figure" is enough
    #6: LOCAL_CONTEXT_ONLY — same_y "We omit ensemble..." is enough
    #9: LOCAL_CONTEXT_ONLY — same_y "CM(ϵ, max, ..." is enough

  REDUCTION:
    4/4 cases: PAGE_CONTEXT/MULTI_SENTENCE → LOCAL_CONTEXT_ONLY
    → The Pack incompleteness CAUSES unnecessary document reconstruction.
    → Human is forced to "reconstruct" (read document) rather than "validate" (check evidence).
    → This directly violates: "Human should validate, not reconstruct."

  This is NOT about the Human needing "more semantic understanding".
  This is about the Pack not delivering SAME-LINE CONTEXT that already exists.
```

---

## 12. Minimal Sufficient Evidence

```
MINIMAL_SUFFICIENT_EVIDENCE (for Text-Drawing Association Judgment):

NECESSARY (must be present for Human to judge):
  1. TARGET TEXT          — the text fragment to judge
  2. ALL EXTENTS ON PAGE  — all drawing extents (not just nearest)
                            → Human needs to see what drawings exist
                            → Even if text is far from all extents, that IS information
  3. SPATIAL RELATION     — distance + vertical ordering + x-overlap
                            → For EACH extent, not just nearest
  4. SAME_Y CONTEXT       — same-line neighboring text (±5pt recommended)
                            → Reconstructs the sentence containing the target text
                            → Critical for short text fragments ("omit", "max")

SUPPORTING (helps but not strictly necessary):
  5. PAGE IMAGE           — visual page context (already provided)
  6. TEXT BBOX            — text position on page (already provided)
  7. FIG-PREFIX           — whether text starts with "Fig"/"Figure" (implicit in text)

OPTIONAL (not required for these 4 cases):
  8. Previous/Next sentence — same_y context usually suffices
  9. Same paragraph         — not needed when same_y is available
  10. Cross-page reference  — NOT needed for these 4 cases

NOT_REQUIRED (and NOT authorized):
  11. Semantic classification (caption/reference/body text)
  12. Confidence score
  13. Machine recommendation
  14. LLM interpretation

CURRENT STATUS:
  Items 1, 5, 6, 7: ALREADY PROVIDED ✓
  Item 2: INCOMPLETE — only nearest extent shown; Type A shows "none" (false)
  Item 3: INCOMPLETE — only for nearest extent; Type A shows "none"
  Item 4: MISSING — hardcoded empty for ALL 16 negatives

  → 2 of 4 NECESSARY items are incomplete/missing.
  → Both are fixable with Evidence Pack redesign (no new observation needed).
```

---

## 13. Cross-Page Context

```
CROSS_PAGE_CONTEXT_REQUIRED:

  #2: NO — same-page evidence sufficient (2 extents + same_y context)
  #5: NO — same-page evidence sufficient (1 extent + same_y context)
  #6: NO — same-page evidence sufficient (1 extent + same_y context)
  #9: NO — same-page evidence sufficient (1 extent + same_y context)

  ALL 4 CASES: CROSS_PAGE_CONTEXT_REQUIRED = NO

  → Although some texts ARE cross-page references (e.g., #2 "in Figure 3"),
    Human does NOT need to navigate to the other page to judge ASSOCIATION.
  → Human only needs to determine: "is THIS text associated with a drawing on THIS page?"
  → Same_y context + all extents on page is sufficient for this judgment.
  → Cross-page reference handling is a secondary concern, not the primary bottleneck.
```

---

## 14. Case-Level Failure Chains

```
#2 (efficientnet p4, "Figure"):

  Document
    ↓
  DGF = YES (141 primitives)
    ↓
  DEF = YES (2 extents formed)
    ↓
  Spatial relation = YES (146pt, 72pt)
    ↓
  Same_y context = YES ("in Figure 3 (left) show that...")
    ↓
  Evidence Pack = NO (extent=None, context=empty)
    ↓ ❌ BREAK
  Human sees: "Figure" + "no drawing on page" (FALSE)
    ↓
  Human = UNCERTAIN (cannot judge without reading document)

#5 (med_001 p15, "figure"):

  Document
    ↓
  DGF = YES (12338 primitives)
    ↓
  DEF = YES (1 extent formed)
    ↓
  Spatial relation = YES (264pt)
    ↓
  Same_y context = YES ("under the curve AUC... The figure")
    ↓
  Evidence Pack = NO (extent=None, context=empty)
    ↓ ❌ BREAK
  Human sees: "figure" + "no drawing on page" (FALSE)
    ↓
  Human = UNCERTAIN

#6 (efficientnet p6, "omit"):

  Document
    ↓
  DGF = YES
    ↓
  DEF = YES (1 extent, shown)
    ↓
  Spatial relation = YES (21.9pt above, shown)
    ↓
  Same_y context = YES (29 atoms: "We omit ensemble...")
    ↓
  Evidence Pack = PARTIAL (extent shown, but context=empty)
    ↓ ❌ BREAK
  Human sees: "omit" + drawing + distance + NO context
    ↓
  Human = UNCERTAIN (cannot determine if "omit" is body text or label)

#9 (med_001 p15, "max"):

  Document
    ↓
  DGF = YES
    ↓
  DEF = YES (1 extent, shown)
    ↓
  Spatial relation = YES (33.1pt above, shown)
    ↓
  Same_y context = YES at ±5pt (29 atoms: "CM(ϵ, max, ...")
    ↓  but 0 atoms at ±3pt (threshold issue)
  Evidence Pack = PARTIAL (extent shown, but context=empty + threshold miss)
    ↓ ❌ BREAK
  Human sees: "max" + drawing + distance + NO context
    ↓
  Human = UNCERTAIN (cannot determine if "max" is math notation or label)
```

---

## 15. Observation vs Organization vs Pack Completeness vs Semantic Boundary

```
Layer 1 — Observation Coverage:
  #2: PASS (DGF=141, DEF=2 — observations exist)
  #5: PASS (DGF=12338, DEF=1 — observations exist)
  #6: PASS (DGF>0, DEF=1 — observations exist)
  #9: PASS (DGF>0, DEF=1 — observations exist)
  → NO Observation Gap in any of these 4 cases.

Layer 2 — Evidence Organization:
  #2: PASS (2 extents formed, spatial relations computed)
  #5: PASS (1 extent formed, spatial relations computed)
  #6: PASS (1 extent formed, spatial relations computed)
  #9: PASS (1 extent formed, spatial relations computed)
  → NO Organization Gap in these 4 cases.

Layer 2b — Evidence Pack Completeness:
  #2: FAIL (extent=None when 2 exist; context=empty when same_y available)
  #5: FAIL (extent=None when 1 exists; context=empty when same_y available)
  #6: FAIL (context=empty when same_y available)
  #9: FAIL (context=empty when same_y available; ±3pt threshold misses)
  → ALL 4 cases FAIL at Pack Completeness.
  → This is the PRIMARY bottleneck.

Layer 3 — Semantic Boundary:
  #2: NOT_DEMONSTRATED (E1 sufficient — same_y context resolves ambiguity)
  #5: NOT_DEMONSTRATED (E1 sufficient — same_y context resolves ambiguity)
  #6: NOT_DEMONSTRATED (E1 sufficient — same_y context resolves ambiguity)
  #9: NOT_DEMONSTRATED (E1 sufficient — same_y context resolves ambiguity)
  → NO Semantic Boundary in any of these 4 cases.
  → All can be resolved with existing evidence, no semantic interpretation needed.
```

---

## 16. Revised Bottleneck

```
PREVIOUS (from Evidence Sufficiency Gap Diagnostic):
  PRIMARY = EVIDENCE_PACK_COMPLETENESS
  SECONDARY = CROSS_PAGE_REFERENCE_HANDLING

REVISED (this diagnostic):
  PRIMARY = EVIDENCE_PACK_PRESENTATION_GAP
    → Existing evidence not organized into Pack
    → 4/4 cases: same_y context available but not shown
    → 2/4 cases: extent exists but shown as None (false "no drawing")

  SECONDARY = SAME_Y_CONTEXT_COLLECTION_DISABLED_FOR_NEGATIVES
    → generate_data.py hardcodes context_text='' for all 16 negatives
    → This is a script-level decision, not an algorithm limitation
    → DESIGN_GAP: context should be collected for ALL cases

  TERTIARY = SAME_Y_THRESHOLD_TOO_NARROW
    → ±3pt threshold misses #9's context (delta=4.9pt)
    → ±5pt would catch it
    → DESIGN_GAP: threshold should be investigated (NOT tuned)

  CROSS_PAGE_REFERENCE_HANDLING:
    → DOWNGRADED — not needed for these 4 cases
    → All 4 can be resolved with same-page evidence
    → Remains a concern for other cases but is NOT the current bottleneck

BOTTLENECK CHAIN:
  Evidence exists (P1, P2, DGF, DEF)
    → Evidence organized (spatial relations computed)
      → Evidence Pack INCOMPLETE (context not collected for negatives)
        → Human cannot judge from Pack alone
          → Human reconstructs document (violates DICE principle)
            → Human = UNCERTAIN
```

---

## 17. Research Implications

```
1. The Human's difficulty is NOT caused by missing observation or semantic ambiguity.
   It is caused by the Evidence Pack not delivering existing evidence.

2. The next research focus should be:
   "How to compress existing Evidence into Human-verifiable minimal evidence units."
   NOT:
   "How to build a stronger Caption Detector or semantic classifier."

3. Specifically:
   a. Evidence Pack should show ALL extents on page (not just nearest within 60pt)
      → For Type A: show "drawing exists but is Npt away" not "no drawing on page"
   b. Evidence Pack should collect same_y context for ALL cases (including negatives)
      → This is a script change, NOT an algorithm change
   c. same_y threshold (±3pt) should be investigated for fine atoms
      → ±5pt may be needed for cases where fine atoms have different y from coarse

4. The DICE principle "Human should validate, not reconstruct" is currently VIOLATED
   because the Pack forces Human to read document context that already exists as
   same_y evidence.

5. If the Pack were complete (E1), all 4 UNCERTAIN cases could theoretically
   become definitive judgments (NO). This would:
   → Reduce UNCERTAIN from 14 to 10 (if only these 4 are Pack-fixable)
   → Reduce Document Reconstruction Burden from PAGE_CONTEXT to LOCAL_CONTEXT_ONLY
   → NOT require any algorithm modification, threshold tuning, or semantic classifier
```

---

## 18. What Is NOT Demonstrated

```
This diagnostic does NOT demonstrate:
  ✗ M-A has solved Evidence Pack completeness
  ✗ All UNCERTAIN cases are fixable (only 4 of 14 examined)
  ✗ The 4 cases would DEFINITELY become NO (counterfactual = SUFFICIENT, not "will be NO")
  ✗ Same_y context is always sufficient (only tested on 4 cases)
  ✗ ±5pt threshold is optimal (only 1 case tested)
  ✗ Cross-page references are never needed (only these 4 cases don't need them)
  ✗ The Pack redesign would improve accuracy (no re-run authorized)
  ✗ Cognitive load is high or low (no quantitative data)

This diagnostic DOES demonstrate:
  ✓ 4 specific cases have existing evidence not shown to Human
  ✓ The root cause is generate_data.py hardcoding empty context for negatives
  ✓ Same_y context (P2) is available and sufficient for these 4 cases
  ✓ All 4 extents exist on page but 2 were shown as "None" (false)
  ✓ The bottleneck is Pack presentation, not observation or semantic boundary
  ✓ Document Reconstruction Burden is caused by Pack incompleteness
```

---

## 19. Design Gaps Only

```
All findings are recorded as DESIGN_GAPS. NO implementation authorized.

DG1: Evidence Pack should show ALL extents on page
  → Currently: only nearest extent (within 60pt) is stored
  → Problem: Type A cases show "no drawing" when drawings exist elsewhere on page
  → Fix: store all extents on page, show distances to each
  → STATUS: DESIGN_GAP (not implemented)

DG2: Evidence Pack should collect same_y context for ALL cases
  → Currently: context_text='' hardcoded for all 16 negatives
  → Problem: Type B cases ("omit", "max") have no context shown
  → Fix: run same_y collection for negatives same as candidates
  → STATUS: DESIGN_GAP (not implemented)

DG3: same_y threshold ±3pt may be too narrow for fine atoms
  → Currently: abs(a2.bbox[1] - tb[1]) < 3
  → Problem: #9 "max" has context at 4.9pt delta (missed by ±3pt)
  → Fix: investigate ±5pt (NOT tune — just investigate)
  → STATUS: DESIGN_GAP (not implemented)

DG4: For Type A, Pack should distinguish "no extent on page" from "extent exists but far"
  → Currently: extent_bbox=None → "本页未识别到图形区域" (ambiguous)
  → Problem: Human cannot tell if drawing exists but is far, vs. no drawing at all
  → Fix: show "drawing exists at Npt distance" even when >60pt
  → STATUS: DESIGN_GAP (not implemented)

DG5: Minimal Sufficient Evidence specification
  → Target Text + All Extents + Spatial Relation + Same_y Context
  → Currently: 2 of 4 NECESSARY items incomplete/missing
  → STATUS: RESEARCH_SPECIFICATION (not implemented)
```

---

## 20. Governance Check

```
FROZEN_BASELINE = INTACT (drift=0/4)
  P1: 74d23ec784d65782 (UNCHANGED)
  TLD: 022f5c21e872ad9e (UNCHANGED)
  GT: 7349963d0d23b5ef (UNCHANGED)
  layout_analyzer: 8f69f0d206b3e565 (UNCHANGED)
  DGF: f25a5ff41afa1bec (UNCHANGED)
  DEF: cba9e583517f8967 (UNCHANGED)

M-A_ALGORITHM = UNCHANGED
P1 = UNCHANGED
P2 = UNCHANGED
P5 = UNCHANGED
P6 = UNCHANGED
AO = UNCHANGED
generate_data.py = UNCHANGED (READ-ONLY analysis)

HUMAN_VALIDATION_DATA = UNCHANGED
HUMAN_VALIDATION_RE_RUN = NO

No code modified.
No data modified.
No thresholds changed.
No Evidence Pack modified.
No UI modified.

DESIGN_GAPS recorded (NOT implemented):
  DG1: show all extents on page
  DG2: collect same_y context for all cases
  DG3: investigate ±5pt threshold
  DG4: distinguish "no extent" from "extent far"
  DG5: minimal sufficient evidence specification
```

---

## 21. Final Decision

```
EVIDENCE_PACK_COMPLETENESS_STATUS = PARTIALLY_SUPPORTED

  → Evidence Pack provides target text, page image, and (for candidates) same_y context.
  → Evidence Pack does NOT provide same_y context for negatives (16 cases).
  → Evidence Pack does NOT show all extents for Type A (shows false "no drawing").
  → 4 of 4 examined cases have existing evidence not delivered to Human.

PRIMARY_CURRENT_BOTTLENECK = EVIDENCE_PACK_PRESENTATION_GAP
  → Existing evidence (P2 same_y, DEF extents) not organized into Pack
  → Root cause: generate_data.py hardcodes empty context for negatives

SECONDARY_CURRENT_BOTTLENECK = SAME_Y_CONTEXT_COLLECTION_DISABLED_FOR_NEGATIVES
  → 16 negative controls have no context collected
  → This is a script-level decision, not an algorithm limitation

MINIMAL_SUFFICIENT_EVIDENCE =
  TARGET_TEXT + ALL_EXTENTS_ON_PAGE + SPATIAL_RELATION + SAME_Y_CONTEXT

  → 2 of 4 NECESSARY items currently incomplete/missing
  → Both fixable with Pack redesign (no new observation needed)
  → NOT requiring: semantic classifier, LLM, confidence score, threshold tuning

DOCUMENT_RECONSTRUCTION_BURDEN =
  CURRENT_PACK: PAGE_CONTEXT / MULTI_SENTENCE_CONTEXT
  COMPLETE_EVIDENCE: LOCAL_CONTEXT_ONLY
  → Pack incompleteness causes unnecessary document reconstruction
  → Violates "Human should validate, not reconstruct"

SEMANTIC_BOUNDARY = NOT_DEMONSTRATED
  → All 4 cases can be resolved with existing same-page evidence
  → No case requires semantic interpretation beyond Human's capability
  → The 5 possible Semantic Boundary cases (from pilot analysis) are
    in the OTHER 5 UNCERTAIN, not these 4

KEY FINDING:
  Human's difficulty is NOT caused by:
    ✗ Missing new Evidence
    ✗ Missing semantic understanding
    ✗ Missing cross-page navigation
    ✗ Missing stronger algorithm

  Human's difficulty IS caused by:
    ✓ Existing Evidence not organized into Pack
    ✓ Same_y context hardcoded empty for negatives
    ✓ Extents shown as "None" when they exist on page

  → Next research focus should be:
    Evidence Pack / Evidence Organization:
    how to compress existing Evidence into Human-verifiable minimal evidence units.

IMPLEMENTATION_AUTHORIZED = FALSE
EXPERIMENT_AUTHORIZED = FALSE
HUMAN_VALIDATION_AUTHORIZED = FALSE

FROZEN_BASELINE = INTACT
STOP = TRUE
```

---

## Research Principle Adherence

- ✅ Read actual Evidence Pack code (app.js renderEvidencePanel)
- ✅ Read actual data generation code (generate_data.py)
- ✅ Compared human-facing vs internal candidate data
- ✅ Reconstructed E0 (what Human saw) from candidates.json
- ✅ Reconstructed E1 (what system had) from P1/P2/DGF/DEF
- ✅ Distinguished AVAILABLE_IN_SYSTEM vs SHOWN_TO_HUMAN
- ✅ Built Evidence Availability Matrix for each case
- ✅ Identified root cause (hardcoded empty context for negatives)
- ✅ Analyzed Document Reconstruction Burden (E0 vs E1)
- ✅ Defined Minimal Sufficient Evidence
- ✅ Did NOT modify any code or data
- ✅ Did NOT modify Evidence Pack
- ✅ Did NOT re-run Human Validation
- ✅ Did NOT claim Semantic Boundary (0 cases)
- ✅ Did NOT claim cognitive load (qualitative observation only)
- ✅ Did NOT tune thresholds (only investigated ±3pt vs ±5pt)
- ✅ Recorded DESIGN_GAPS without implementing
- ✅ Frozen baseline intact (drift=0)
- ✅ STOP = TRUE

`STOP = TRUE`.
