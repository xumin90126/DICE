# Evidence Configuration Family Design Research

> **模式: READ-ONLY / NO CODE / NO IMPLEMENTATION / NO HUMAN VALIDATION / STOP**
> 日期: 2026-09-19
> Gate: EVIDENCE_CONFIGURATION_FAMILY_DESIGN_RESEARCH
> 前置: Reusable Signal Validation Gate (COMPLETE, CONDITIONAL)
> 本文件: 研究现有 Evidence 能否客观描述一个稳定的 Evidence Configuration Family。

---

## 0. Core Question

```
唯一问题:

  37 个 Reusable Signal Candidates + 16 个 Counterexamples，
  是否存在一个可客观描述的 Evidence Configuration Family？

  不是寻找规则。
  不是 "FIG + EXTENT = Caption"。
  而是: 哪些 Evidence 差异仍属于同一结构模式，哪些差异意味着不同模式。

  如果不能 → NOT_SUPPORTED
  如果部分可以 → CONDITIONAL
  如果可以 → SUPPORTED

  三种结果都接受。不要强行得到 SUPPORTED。
```

---

## 1. Frozen Baseline

```
RESEARCH_BASELINE = FROZEN (v1)
FROZEN_BASELINE = INTACT
BASELINE_DRIFT = 0
SYSTEM_MODIFIED = FALSE
IMPLEMENTATION_AUTHORIZED = FALSE
EXPERIMENT_AUTHORIZED = FALSE
HUMAN_VALIDATION_AUTHORIZED = FALSE
RUNTIME_AUTHORITY = ZERO
PRODUCTION = FALSE
STOP = TRUE
```

---

## 2. Data Used

```
M-A 79-case Human Validation (FROZEN)
  - 79 cases: 61 YES, 4 NO, 14 UNCERTAIN
  - 5 documents, single Human reviewer
  - Text-Drawing Association task (T1)

Prior Reusable Signal Validation Gate findings:
  - 37 candidates (34 Group A + 3 Group B)
  - 3 true counterexamples + 1 boundary
  - Semantic label dependency discovered (case_type needed)

Only existing Evidence Pack fields used:
  fig_prefix, e1_evidence_state, e1_extent, e1_ctx_count,
  vertical_relation, x_overlap, drawing_extent_present,
  distance_pt, burden_e1

NO new fields. NO semantic labels (new). NO case_type as grouping key.
```

---

## 3. Q1: Exact Configuration Comparison

### 3.1 Group A Structural Fields (34 caption_like + YES cases)

```
EXACT_CONFIGURATION = NOT fully identical

  7/9 fields are IDENTICAL across all 34 cases:
    case_type: caption_like               (34/34) ← semantic label
    e1_evidence_state: EXTENT_EXISTS       (34/34)
    fig_prefix: True                       (34/34)
    e1_extent: set                         (34/34)
    e1_ctx_count: 5                        (34/34)
    drawing_extent_present: True           (34/34)
    vertical_relation: below               (34/34)

  2/9 fields VARY:
    x_overlap: True (29/34), False (5/34)
    distance_pt: ranges from 2.5 to 55.2pt (28 unique values)

  → The 34 cases are NOT identical configurations.
  → They are a FAMILY: 7 shared fields + 2 variable fields.
  → The variation in x_overlap and distance does NOT affect judgment (all YES).
```

### 3.2 Configuration Family Assessment

```
CONFIGURATION_FAMILY = EXISTS (but with internal variation)

  The family is defined by:
    SHARED: FIG=YES + EXTENT_EXISTS + extent=SET + ctx=5 + VR=below + dep=YES + burden=0
    VARIABLE: x_overlap (True/False) + distance_pt (2.5-55.2pt)

  The variable fields are CONTINUOUS/BOOLEAN variations within a coherent pattern.
  They do not create separate sub-families because:
    - Both XO=True and XO=False cases received YES
    - Both dist=2.5 and dist=55.2 cases received YES
    - The judgment is consistent regardless of these variations

  BUT: this consistency holds ONLY for case_type=caption_like.
  When case_type=ambiguous_fragment enters the same structural config,
  judgments become MIXED (see Q3).
```

---

## 4. Q2: Which Variations Are "Allowed"?

### 4.1 Distance Variation

```
A. distance:
  Range: 2.5pt to 55.2pt (28 unique values)
  Distribution: continuous, no clear clusters

  Is distance variation "allowed" within the family?
  → YES for case_type=caption_like: all 34 YES regardless of distance.
  → NO for structural-only grouping: distance > 20 introduces counterexamples.

  Finding:
  - dist ≤ 20 + XO=True: 16 cases, 100% YES (includes 1 ambiguous_fragment)
  - dist > 20: counterexamples appear (3 NO + 1 UNCERTAIN, all ambiguous_fragment)
  - Distance itself does NOT cause different judgments.
  - But distance > 20 correlates with ambiguous_fragment cases having different judgments.

  CONCLUSION: distance is an ALLOWED variation within the caption_like family,
  but it is a BOUNDARY INDICATOR for structural-only grouping.
```

### 4.2 X_Overlap Variation

```
B. x_overlap:
  True: 29/34 caption_like YES cases
  False: 5/34 caption_like YES cases

  Is x_overlap variation "allowed"?
  → YES for case_type=caption_like: both XO=True and XO=False → YES.
  → For structural-only grouping:
    XO=True: 37 cases, 94.6% YES (35 YES, 2 NO)
    XO=False: 9 cases, 77.8% YES (7 YES, 1 NO, 1 UNC)

  CONCLUSION: x_overlap is an ALLOWED variation within caption_like.
  But XO=False has lower YES rate in structural-only grouping.
```

### 4.3 Text/Context Variation

```
C. text/context:
  Every case has different text content (different captions, different figures).
  This is INSTANCE variation, not Configuration variation.

  The Evidence Configuration (FIG + EXTENT + VR + spatial) is the same
  regardless of the specific text content.

  CONCLUSION: text variation is purely INSTANCE variation.
  It does NOT represent a different Evidence Configuration.
```

### 4.4 Summary

```
ALLOWED VARIATIONS (within caption_like family):
  - distance_pt: any value (2.5 to 55.2pt) → judgment remains YES
  - x_overlap: True or False → judgment remains YES
  - text content: always different → instance variation, not config variation

NOT ALLOWED (breaks the family):
  - case_type change: caption_like → ambiguous_fragment → judgment may change
  - This is NOT a structural evidence change; it's a semantic label change.
```

---

## 5. Q3: Why Are Counterexamples Different?

### 5.1 Root Cause Analysis

```
3 TRUE COUNTEREXAMPLES (judgment=NO):
  CE1: arxiv_2402.18619_p19_339_297
    case_type: ambiguous_fragment
    config: FIG=True + EXTENT_EXISTS + VR=below + XO=True + dist=56.8
    judgment: NO

  CE2: is11_efficientnet_p8_467_415
    case_type: ambiguous_fragment
    config: FIG=True + EXTENT_EXISTS + VR=below + XO=True + dist=25.5
    judgment: NO

  CE3: is11_efficientnet_p4_188_461
    case_type: ambiguous_fragment
    config: FIG=True + EXTENT_EXISTS + VR=below + XO=False + dist=20.1
    judgment: NO

1 BOUNDARY CASE (judgment=UNCERTAIN):
  CE4: is11_resnet_p4_464_620
    case_type: ambiguous_fragment
    config: FIG=True + EXTENT_EXISTS + VR=below + XO=False + dist=38.4
    judgment: UNCERTAIN
    analysis_note: "Ambiguous fragment: 'Fig.' near drawing but context suggests
      reference ('in Fig. 9', 'cf. Fig. 3b'). Could be caption or reference —
      semantic ambiguity."
```

### 5.2 What Is Different?

```
For each counterexample, compared structural evidence to nearby YES cases:

  CE1 (dist=56.8, XO=YES):
    Nearby YES: arxiv_2402.18619_p28_457_234 (dist=55.2, XO=YES, case_type=caption_like)
    → IDENTICAL structural config (dist within 1.6pt, same XO, same VR)
    → DIFFERENT case_type (ambiguous_fragment vs caption_like)
    → DIFFERENT judgment (NO vs YES)

  CE2 (dist=25.5, XO=YES):
    Nearby YES: is11_resnet_p6_478_168 (dist=25.1, XO=YES, case_type=ambiguous_fragment)
    → IDENTICAL structural config (dist within 0.4pt, same XO, same VR)
    → SAME case_type (both ambiguous_fragment!)
    → DIFFERENT judgment (NO vs YES)
    → THIS IS THE MOST CRITICAL FINDING (see below)

  CE3 (dist=20.1, XO=NO):
    Nearby YES: is11_med_001_p16_85_484 (dist=15.3, XO=NO, case_type=caption_like)
    → SIMILAR structural config (dist within 4.8pt, same XO, same VR)
    → DIFFERENT case_type (ambiguous_fragment vs caption_like)
    → DIFFERENT judgment (NO vs YES)

  CE4 (dist=38.4, XO=NO):
    Nearby YES: is11_med_001_p13_85_307 (dist=32.1, XO=NO, case_type=caption_like)
    → SIMILAR structural config (dist within 6.3pt, same XO, same VR)
    → DIFFERENT case_type (ambiguous_fragment vs caption_like)
    → DIFFERENT judgment (UNCERTAIN vs YES)
```

### 5.3 Classification

```
For each counterexample, the difference from YES cases is:

  CE1: SEMANTIC_DIFFERENCE
    Structural evidence identical to nearby YES.
    Difference is case_type (caption_like vs ambiguous_fragment).
    → Human determined text is NOT a caption despite identical spatial evidence.

  CE2: SEMANTIC_DIFFERENCE (CRITICAL)
    Structural evidence identical to nearby YES.
    SAME case_type (both ambiguous_fragment).
    → Even case_type doesn't separate them.
    → Two ambiguous_fragment cases with nearly identical distance (25.5 vs 25.1)
       received DIFFERENT judgments (NO vs YES).
    → This means the difference is NOT in any existing Evidence field.
    → The difference is in Human's semantic assessment of the text content.

  CE3: SEMANTIC_DIFFERENCE
    Structural evidence similar to nearby YES.
    Difference is case_type.

  CE4: SEMANTIC_DIFFERENCE
    Structural evidence similar to nearby YES.
    Difference is case_type + semantic ambiguity (analysis_note confirms).
    → "Could be caption or reference — semantic ambiguity"
    → This is the G5 boundary: evidence complete but identity ambiguous.
```

### 5.4 Critical Finding

```
EVIDENCE_FAMILY_CANNOT_DETERMINE_JUDGMENT = TRUE

  CE2 is the decisive case:
    - is11_efficientnet_p8_467_415: ambiguous_fragment, dist=25.5, XO=YES → NO
    - is11_resnet_p6_478_168: ambiguous_fragment, dist=25.1, XO=YES → YES

    These two cases have:
    - SAME case_type (ambiguous_fragment)
    - SAME fig_prefix (True)
    - SAME e1_evidence_state (EXTENT_EXISTS)
    - SAME vertical_relation (below)
    - SAME x_overlap (True)
    - NEARLY SAME distance (25.5 vs 25.1pt)
    - SAME burden_e1 (0)
    - SAME e1_ctx_count (5)

    But DIFFERENT judgments: NO vs YES.

    → ALL existing Evidence fields are identical.
    → The difference is NOT in any current Evidence field.
    → The difference is in the SEMANTIC CONTENT of the text
       (what the text actually says, which determines whether it's
       a caption or an in-text reference).

    → The Evidence Configuration Family CANNOT determine judgment
       for ambiguous_fragment cases.
    → Structural evidence is NECESSARY but NOT SUFFICIENT.
    → Semantic interpretation is required for ambiguous cases.

  THIS IS THE G5 BOUNDARY:
    Evidence is complete (all structural fields present).
    But the text's identity (caption vs reference) cannot be
    determined from structural evidence alone.
```

---

## 6. Q4: Can We Group Without Semantic Label?

### 6.1 Exhaustive Structural-Only Grouping Test

```
Tested ALL combinations of existing structural fields (NO case_type):

  Config                                    Cases  YES   NO  UNC  YES%
  FIG=YES+EXTENT+VR=below                    46    42    3    1  91.3%
  + XO=True                                  37    35    2    0  94.6%
  + XO=True + dist≤25                        18    18    0    0 100.0%
  + XO=True + dist≤20                        16    16    0    0 100.0%
  + XO=True + dist≤15                        13    13    0    0 100.0%
  + XO=True + dist≤10                        12    12    0    0 100.0%
  + XO=True + dist≤50                        32    31    1    0  96.9%
  + XO=False                                 9      7    1    1  77.8%
  + XO=True + dist>20                        21    19    2    0  90.5%
```

### 6.2 Key Results

```
BEST 100% YES group (structural-only):
  FIG=YES + EXTENT + VR=below + XO=True + dist≤25
  → 18 cases, 100% YES
  → But only covers 18/34 caption_like YES cases (52.9%)
  → The remaining 16 YES cases have dist>25 or XO=False

PROBLEM:
  To cover ALL 34 caption_like YES cases, we need 10 structural sub-configs:
    VR=below|XO=YES|dist=0-20:    15 cases
    VR=below|XO=YES|dist=40+:      8 cases
    VR=below|XO=YES|dist=20-40:    6 cases
    VR=below|XO=NO|dist=20-40:     2 cases
    VR=below|XO=NO|dist=0-20:      2 cases
    VR=above|XO=YES|dist=0:        2 cases
    VR=above|XO=NO|dist=0-20:      1 case
    VR=above|XO=NO|dist=0:         1 case
    VR=below|XO=NO|dist=40+:       1 case
    VR=inside|XO=YES|dist=0:       1 case

  10 sub-configs to cover 34 YES cases.
  Some sub-configs have only 1-2 cases → too small for pattern.
  Each sub-config would need its own boundary check.

  AND: even within these sub-configs, ambiguous_fragment cases
  with the SAME structural config have different judgments.

  CONCLUSION:
  Structural-only grouping CANNOT achieve a stable family.
  - Best 100% group covers only 52.9% of YES cases.
  - Covering all YES requires 10 sub-configs (fragmented).
  - Even within sub-configs, counterexamples exist.
  - case_type is the ONLY field that cleanly separates YES from NO/UNCERTAIN.
```

### 6.3 Result

```
FAMILY_DEFINITION = NOT_SUPPORTED (without semantic label)

  Without case_type:
  - Best structural-only family: 91.3% YES (4 counterexamples)
  - Best 100% subgroup: only 18 cases (52.9% coverage)
  - Cannot cover all 34 YES cases without fragmentation
  - Counterexamples have IDENTICAL structural evidence

  With case_type:
  - 34/34 YES (100%)
  - Clean separation from counterexamples
  - But case_type IS a semantic label (Human-assigned)

  → The family CANNOT be defined without a semantic label.
  → FAMILY_DEFINITION (structural-only) = NOT_SUPPORTED.
```

---

## 7. Q5: One-Case-One-Patch Risk

### 7.1 Assessment

```
ONE_CASE_ONE_PATCH_RISK = MEDIUM

  Evidence AGAINST high risk:
  - 34 cases share 7/9 structural fields → one family, not 34 patches
  - 2 variable fields (distance, x_overlap) → not per-case conditions
  - Judgment is consistent (34/34 YES) → not ad hoc

  Evidence FOR medium risk (not low):
  - Covering all 34 YES without semantic label requires 10 sub-configs
  - Some sub-configs have only 1-2 cases → fragile
  - No structural threshold cleanly separates YES from NO
  - CE2 proves: even identical structural + case_type → different judgment
  - Any structural boundary (dist≤20, XO=True) excludes some YES cases

  RISK = MEDIUM:
  The family is NOT one-case-one-patch (it's a genuine family).
  But defining it structurally requires many sub-groups,
  and even then, counterexamples exist.
  The family is real but its STRUCTURAL BOUNDARY is unclear.
```

---

## 8. Q6: Final Conclusion

### 8.1 Evidence Summary

```
FOR a stable Evidence Configuration Family:
  - 7/9 structural fields are identical across 34 YES cases
  - 100% judgment consistency within case_type=caption_like
  - Cross-document (5 documents)
  - distance and x_overlap are allowed variations (don't affect judgment)
  - Text content is instance variation, not config variation

AGAINST a stable Evidence Configuration Family (structural-only):
  - 2/9 fields vary (distance, x_overlap)
  - Structural-only grouping: 91.3% YES (4 counterexamples)
  - Best 100% subgroup: only 52.9% coverage
  - 10 sub-configs needed for full coverage (fragmented)
  - CE2: identical structural + case_type → different judgment
  - EVIDENCE_FAMILY_CANNOT_DETERMINE_JUDGMENT = TRUE (for ambiguous cases)
  - case_type (semantic label) is REQUIRED for clean separation

THE DECISIVE FINDING:
  CE2 (is11_efficientnet_p8_467_415 vs is11_resnet_p6_478_168):
    - ALL existing Evidence fields identical
    - SAME case_type (ambiguous_fragment)
    - DIFFERENT judgment (NO vs YES)
    → The difference is NOT in any Evidence field.
    → The difference is in the SEMANTIC CONTENT of the text.
    → No Evidence Configuration can resolve this.
    → This is the G5 Semantic Boundary.
```

### 8.2 Decision

```
EVIDENCE_CONFIGURATION_FAMILY = CONDITIONAL

  The family EXISTS structurally (7/9 fields shared, consistent judgment).
  But its BOUNDARY is NOT determinable from structural evidence alone.

  CONDITION 1: case_type needed
    Without case_type, 4 counterexamples exist.
    case_type is a semantic label, not a structural field.

  CONDITION 2: semantic content needed for ambiguous cases
    CE2 proves: even with case_type, identical configs → different judgments.
    The text's semantic content (caption vs in-text reference) determines
    the judgment, not the structural evidence.

  CONDITION 3: structural boundary unclear
    No distance threshold or XO value cleanly separates YES from NO.
    The boundary is semantic, not structural.

  → The family is REAL but CONDITIONAL.
  → It exists as a structural pattern (FIG + EXTENT + below → mostly YES).
  → But its boundary requires semantic assessment (case_type + text content).
  → Structural evidence alone is NECESSARY but NOT SUFFICIENT.
```

---

## 9. Over-Design Audit

```
  O1: Created new Schema? → NO
  O2: Created new Evidence Field? → NO
  O3: Created Semantic Label? → NO (discovered case_type IS semantic, didn't create)
  O4: Created Rule? → NO
  O5: Created Detector? → NO
  O6: Introduced Similarity/Embedding? → NO
  O7: Treated Candidate as Signal? → NO
  O8: Treated Signal as Capability? → NO
  O9: One-Case-One-Patch? → NO (MEDIUM risk, not HIGH; genuine family)
  O10: Increased Human Burden? → NO

  ALL CHECKS: FALSE
  OVER_DESIGN_AUDIT = PASS
```

---

## 10. Limitations

```
  ECF-L-01: SINGLE HUMAN REVIEWER
    All judgments from one reviewer.
    CE2's NO vs YES distinction may be reviewer-specific.

  ECF-L-02: CE2 IS DECISIVE BUT SINGLE INSTANCE
    Only 1 case pair (CE2 vs nearby YES) demonstrates identical-evidence-different-judgment.
    More such pairs would strengthen the finding.

  ECF-L-03: STRUCTURAL BOUNDARY UNTESTED AT FINER GRAIN
    Distance bins (≤20, 20-40, 40+) are coarse.
    Finer analysis might reveal structural patterns.
    But CE2 (25.5 vs 25.1pt) suggests fine-grain won't help.

  ECF-L-04: case_type IS HUMAN-ASSIGNED
    case_type was assigned during M-A Human Validation.
    It encodes Human's semantic assessment.
    It is NOT a machine-derivable structural field.

  ECF-L-05: SAME DOMAIN
    All 5 documents are academic papers.
    Cross-domain family stability untested.
```

---

## 11. Final Questions

### Q1: 37 个案例是否存在 Evidence Configuration Family？

```
YES — a CONDITIONAL family exists.

  7/9 structural fields identical across 34 Group A cases.
  Judgment 100% consistent within case_type=caption_like.
  distance and x_overlap are allowed variations.

  BUT: the family's boundary requires case_type (semantic label).
  Structural-only grouping: 91.3% YES (4 counterexamples).

  EXACT_CONFIGURATION = NOT identical (family, not clones)
  CONFIGURATION_FAMILY = EXISTS (conditional on semantic label)
```

### Q2: distance / x_overlap 变化是否属于正常实例差异？

```
YES — within caption_like family.

  distance: 2.5 to 55.2pt, all YES → allowed variation.
  x_overlap: True/False, all YES → allowed variation.
  text content: always different → instance variation, not config variation.

  BUT: for structural-only grouping, distance > 20 introduces counterexamples.
  → The variation is allowed WITHIN the semantic family but NOT within
     a structural-only family.
```

### Q3: 3 个 Counterexamples 与 34 个 YES 到底有什么 Evidence 差异？

```
SEMANTIC_DIFFERENCE — not structural.

  CE1: identical structural evidence to nearby YES → SEMANTIC_DIFFERENCE
  CE2: identical structural evidence AND case_type to nearby YES → SEMANTIC_DIFFERENCE (CRITICAL)
  CE3: similar structural evidence to nearby YES → SEMANTIC_DIFFERENCE
  CE4: similar structural evidence, semantic ambiguity confirmed → SEMANTIC_DIFFERENCE (G5 boundary)

  CE2 is decisive:
    is11_efficientnet_p8_467_415 (NO) vs is11_resnet_p6_478_168 (YES)
    → ALL Evidence fields identical (including case_type)
    → Difference is in text's semantic content (what the text says)
    → EVIDENCE_FAMILY_CANNOT_DETERMINE_JUDGMENT = TRUE

  The counterexamples prove:
  → Structural evidence is NECESSARY but NOT SUFFICIENT.
  → Semantic interpretation is required for ambiguous cases.
  → This is the G5 Semantic Boundary (Evidence Boundary).
```

### Q4: 是否必须依赖 semantic label 才能分组？

```
YES — semantic label is required.

  Structural-only best: 91.3% YES (4 counterexamples).
  Structural-only 100%: only 18/34 cases covered (52.9%).
  With case_type: 100% YES (34/34, all counterexamples excluded).

  FAMILY_DEFINITION (structural-only) = NOT_SUPPORTED.
  The family REQUIRES case_type (semantic label) for clean separation.
```

### Q5: 是否存在 One-Case-One-Patch 风险？

```
MEDIUM risk.

  NOT high: 34 cases share 7/9 fields → genuine family, not patches.
  NOT low: 10 sub-configs needed for structural-only coverage.
  Some sub-configs have 1-2 cases → fragile.
  No structural threshold cleanly separates YES from NO.
```

### Q6: 当前是否有资格继续研究 Reusable Signal？

```
NO — NOT READY for Reusable Signal research.

  Three blockers:
  1. Semantic label dependency: family requires case_type (not structural)
  2. Evidence cannot determine judgment: CE2 proves identical evidence → different judgment
  3. G5 boundary confirmed: ambiguous cases require semantic interpretation

  The Evidence Configuration Family is REAL but CONDITIONAL.
  Its boundary is semantic, not structural.
  No amount of additional structural evidence can resolve the boundary.

  → Reusable Signal research would require:
    a) A way to derive case_type structurally (NOT authorized)
    b) OR Human semantic validation for ambiguous cases (NOT authorized)
    c) OR accepting the G5 boundary and working within it

  None of these are possible in READ-ONLY mode.
  → STOP.
```

---

## 12. The Deep Finding: G5 Confirmation

```
This research has independently re-confirmed the G5 Semantic Boundary
through a completely different path:

  Original G5 discovery (Evidence Boundary Structure Research):
    → Text-Drawing Association: structural evidence complete, but
      caption vs reference identity cannot be determined.
    → 13 G5 cases identified in academic corpus.

  This research (Evidence Configuration Family):
    → CE2: two cases with IDENTICAL structural evidence + SAME case_type
      received DIFFERENT judgments (NO vs YES).
    → The difference is in the text's semantic content.
    → No Evidence Configuration can resolve this.
    → This IS the G5 Semantic Boundary.

  CONVERGENT VALIDATION:
    Two independent research paths arrived at the same boundary:
    → Structural evidence has a ceiling.
    → Semantic identity (caption vs reference) cannot be determined
      from structural evidence alone.
    → This ceiling is the G5 Evidence Boundary.

  IMPLICATION:
    The Evidence Configuration Family is bounded by G5.
    Within non-ambiguous cases (caption_like), the family is stable.
    At the ambiguous boundary (ambiguous_fragment), G5 prevents
    structural resolution.

    This is not a failure of the family — it is a fundamental
    property of the Evidence Boundary.
```

---

## 13. Files Created

```
tmp/evidence_configuration_family_research.md          (this file)
tmp/evidence_configuration_family_research.json         (structured data)
tmp/evidence_configuration_family_case_table.csv        (50 cases, 10 fields)
```

---

## 14. Final Governance State

```
RESEARCH_STATUS = COMPLETE

SYSTEM_MODIFIED = FALSE
IMPLEMENTATION_AUTHORIZED = FALSE
EXPERIMENT_AUTHORIZED = FALSE
HUMAN_VALIDATION_AUTHORIZED = FALSE

FROZEN_BASELINE = INTACT
BASELINE_DRIFT = 0

NEW_FIELD = NONE
NEW_SCHEMA = NONE
NEW_RULE = NONE
NEW_DETECTOR = NONE
NEW_SIGNAL = NONE
NEW_CAPABILITY = NONE

RUNTIME_AUTHORITY = ZERO
PRODUCTION = FALSE

STOP = TRUE
```

---

## STOP

```
Evidence Configuration Family Design Research is COMPLETE.

SUMMARY:
  - 50 cases analyzed (34 candidates + 8 borderline + 4 counterexamples + 4 Group B)
  - EXACT_CONFIGURATION = NOT identical (7/9 fields shared, 2 vary)
  - CONFIGURATION_FAMILY = EXISTS but CONDITIONAL
  - Distance and x_overlap are allowed variations within caption_like
  - 3 counterexamples: SEMANTIC_DIFFERENCE (not structural)
  - CE2 (CRITICAL): identical evidence + same case_type → different judgment
    → EVIDENCE_FAMILY_CANNOT_DETERMINE_JUDGMENT = TRUE
  - Structural-only grouping: best 100% = 52.9% coverage
  - Semantic label (case_type) REQUIRED for clean separation
  - FAMILY_DEFINITION (structural-only) = NOT_SUPPORTED
  - ONE_CASE_ONE_PATCH_RISK = MEDIUM
  - G5 Semantic Boundary independently re-confirmed via CE2

FINAL DECISION: CONDITIONAL
  The family is real but bounded by G5.
  Structural evidence is necessary but not sufficient.
  Semantic interpretation is required at the boundary.
  No further READ-ONLY research can resolve this.

  不得自动进入下一阶段。
  不得创建任何 Rule / Signal / Capability。
  不得把 Conditional 当作 Supported。
  STOP = TRUE
```
