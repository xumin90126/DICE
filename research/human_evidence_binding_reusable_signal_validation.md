# Human-Evidence Binding Reusable Signal Validation Gate

> **模式: 严格 READ-ONLY / RESEARCH GATE / NO CODE / NO IMPLEMENTATION**
> 日期: 2026-09-19
> Gate: HUMAN_EVIDENCE_BINDING_REUSABLE_SIGNAL_VALIDATION_GATE
> 前置: Human-Evidence Binding Reusability Gate (COMPLETE, 37 candidates identified)
> 本文件: 验证 37 个 Reusable Signal Candidate 是否具有足够的跨案例、跨文档、Evidence-grounded 稳定性。

---

## 0. Core Question

```
已发现的 37 个 Reusable Signal Candidate，
是否具有足够的跨案例、跨文档、Evidence-grounded 稳定性，
值得进入下一阶段独立验证？

如果证据不足 → NOT_READY
如果部分成立 → CONDITIONAL
如果全部成立 → SUPPORTED_FOR_NEXT_VALIDATION

注意：SUPPORTED_FOR_NEXT_VALIDATION 仍然不是 Validated Signal。
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

Prior Reusability Gate = FROZEN (37 candidates identified, not validated)
M-A 79-case data = FROZEN
Evidence Pack E1 = FROZEN
G1-G5 Framework = FROZEN
```

---

## 2. Research Objects

### 2.1 Candidate Group A

```
caption_like + FIG=YES + EXTENT_EXISTS → Human YES
  34 cases
  5 documents
  Human judgment consistency = 100% YES (34/34)
```

### 2.2 Candidate Group B

```
Type_B_negative + FIG=NO + EXTENT_EXISTS → Human YES
  3 cases
  3 documents
  Human judgment consistency = 100% YES (3/3)
  SAMPLE SIZE WARNING: too small for strong conclusions
```

---

## 3. Q1: Cross-Case Evidence Configuration Stability

### 3.1 Group A Configuration Analysis

```
All 34 Group A cases share these EXACT fields:

  case_type: caption_like          (34/34)
  e1_evidence_state: EXTENT_EXISTS  (34/34)
  fig_prefix: True                  (34/34)
  e1_extent: set                    (34/34)
  e1_ctx_count: 5                   (34/34)
  drawing_extent_present: True      (34/34)
  vertical_relation: below          (34/34)

  BUT two fields VARY within the group:

  x_overlap: True (29/34), False (5/34)
  distance_pt: varies from 2.5 to 55.2 (28 unique values)

  → The 34 cases are NOT identical configurations.
  → They are a FAMILY of similar configurations.
  → The common subset is: caption_like + FIG=YES + EXTENT_EXISTS + VR=below + ctx=5
  → The variable subset is: x_overlap (True/False) and distance_pt (wide range)
```

### 3.2 Configuration Stability Assessment

```
EVIDENCE_CONFIGURATION_STABILITY = MEDIUM

  Reasons for MEDIUM (not HIGH):
  1. x_overlap varies: 29 True vs 5 False → not uniform
  2. distance_pt varies: 2.5 to 55.2pt → wide range
  3. The 34 cases are a FAMILY, not identical instances

  Reasons for MEDIUM (not LOW):
  1. 6 out of 8 config fields are IDENTICAL across all 34
  2. The variable fields (x_overlap, distance) do NOT affect judgment
  3. All 34 cases received the SAME Human judgment (YES)
  4. The variation is within a coherent structural pattern

  KEY DISTINCTION:
  These cases share "the same Case Type" (caption_like)
  more than they share "the same Evidence Configuration."
  
  The case_type field is a HUMAN-ASSIGNED label that groups cases
  by Human-perceived similarity, not by identical structural evidence.

  → This is "same task type with consistent judgment"
  → NOT "identical evidence pattern with consistent judgment"
```

---

## 4. Q2: Cross-Document Independence

### 4.1 Per-Document Distribution

```
Group A (34 cases across 5 documents):

  arxiv_2402.18619:    12 cases (35.3%)  ← largest
  is11_med_001:        11 cases (32.4%)
  is11_resnet:          5 cases (14.7%)
  is11_efficientnet:    4 cases (11.8%)
  is11_cs_001:          2 cases  (5.9%)
```

### 4.2 Single-Document Dominance Check

```
  Largest document: arxiv_2402.18619 with 12/34 = 35.3%

  Is 35.3% "single-document dominance"?
  → NO single document exceeds 50%
  → But arxiv_2402.18619 + is11_med_001 = 23/34 = 67.6%
  → Two documents account for 2/3 of all cases

  All 5 documents contribute ≥2 cases.
  The pattern is NOT driven by a single document.

  BUT: all 5 documents are from the SAME domain (academic papers).
  → This is cross-DOCUMENT, NOT cross-DOMAIN.
  → Cross-domain generalization is NOT demonstrated.
  → Cross-domain is NOT required by this Gate (per instructions).
```

### 4.3 Publisher/Layout Specificity Check

```
  All 5 documents are academic papers with similar layout conventions:
  - arXiv-style or conference paper format
  - FIG-prefixed captions below figures
  - Standard academic figure-caption layout

  → The pattern may be specific to academic paper layout.
  → Non-academic documents (biotech manuals, financial reports) were NOT tested.
  → Publisher/layout specificity is POSSIBLE but not confirmed.

  CROSS_DOCUMENT_INDEPENDENCE = SUPPORTED

  (for academic document domain; cross-domain NOT tested and NOT required)
```

---

## 5. Q3: Human Judgment Evidence Grounding

### 5.1 Grounding Classification (A–E)

```
For each of the 37 candidates, classified how Human's YES judgment
relates to Evidence:

  A = Evidence itself sufficient (burden_e1=0, EXTENT_EXISTS)
  B = Evidence + local context needed
  C = Human must view original PDF
  D = Human uses information outside Evidence
  E = Cannot determine
```

### 5.2 Results

| Grounding | Group A | Group B | Total | % |
|-----------|--------:|--------:|------:|---:|
| A (evidence sufficient) | 34 | 3 | 37 | 100% |
| B (evidence + context) | 0 | 0 | 0 | 0% |
| C (document access) | 0 | 0 | 0 | 0% |
| D (external info) | 0 | 0 | 0 | 0% |
| E (cannot determine) | 0 | 0 | 0 | 0% |

```
EVIDENCE_GROUNDING = A

  ALL 37 candidates have:
  - E1 evidence state = EXTENT_EXISTS (drawing extent observed)
  - burden_e1 = 0 (E1 Pack sufficient for judgment)
  - Human did NOT need to access the original PDF
  - Human did NOT use external information

  This means: Human's YES judgment was made using ONLY the Evidence Pack.
  The judgment is FULLY evidence-grounded.

  This is the STRONGEST possible grounding result.
  No candidate required document access or external knowledge.
```

---

## 6. Q4: Semantic Label Dependency

### 6.1 The Critical Test

```
Can the candidate be described using ONLY structural Evidence fields,
WITHOUT the case_type label?

  Structural fields available:
    fig_prefix (True/False)
    e1_evidence_state (EXTENT_EXISTS, etc.)
    e1_extent (set/None)
    e1_ctx_count (5, 3, 2)
    vertical_relation (above, below, inside, none)
    x_overlap (True/False)
    drawing_extent_present (True/False)
    distance_pt (numeric)

  If we describe Group A using ONLY these fields (NO case_type):
    Config = FIG=True + EXTENT_EXISTS + extent=SET + ctx=5 + VR=below
```

### 6.2 Counter-Discovery

```
11 NON-caption_like cases ALSO match this structural config:

  ambiguous_fragment + FIG=True + EXTENT_EXISTS + VR=below + ctx=5
    → 11 cases
    → Judgments: 8 YES, 3 NO, 3 UNCERTAIN (MIXED!)

  These ambiguous_fragment cases have the SAME structural evidence
  as Group A (caption_like), but DIFFERENT Human judgments.

  CRITICAL IMPLICATION:
  The structural config (FIG=True + EXTENT_EXISTS + VR=below + ctx=5)
  does NOT uniquely predict YES.

  Only when we ADD case_type=caption_like does the pattern become
  100% consistent (34/34 YES).

  case_type is a HUMAN-ASSIGNED SEMANTIC LABEL.
  It encodes Human's judgment about what the text IS (caption-like vs ambiguous).

  WITHOUT this semantic label, the structural evidence produces MIXED judgments.
  WITH this semantic label, the judgments are 100% consistent.

  → The candidate REQUIRES a semantic label to be distinguishable.
  → The semantic label is EXISTING (case_type is in the Evidence Pack).
  → But it IS a semantic label, not a pure structural feature.
```

### 6.3 Result

```
SEMANTIC_LABEL_DEPENDENCY = TRUE

  The Reusable Signal Candidate depends on case_type (a semantic label)
  to distinguish YES cases from NO/UNCERTAIN cases with the same
  structural evidence.

  This means:
  - Pure structural evidence is NOT sufficient to form the signal.
  - A semantic label (case_type) is needed.
  - The label is EXISTING (not newly created).
  - But the dependency is real: without the label, the pattern breaks.

  IMPLICATION for Reusable Signal:
  If case_type is available in future Evidence Packs, the candidate
  can be described. If case_type is NOT available (new document without
  Human-assigned case_type), the candidate CANNOT be applied.

  This is a CONDITION, not a blocker. But it must be recorded.
```

---

## 7. Q5: One-Case-One-Patch Risk

### 7.1 Risk Assessment

```
ONE_CASE_ONE_PATCH_RISK = LOW (with caveat)

  Evidence AGAINST risk:
  1. 34 cases share the SAME case_type + FIG + EXTENT + VR → one pattern, not 34 patches
  2. ALL 34 received the SAME judgment (YES) → consistent, not ad hoc
  3. 5 documents contribute → cross-document, not single-case
  4. The five-level hierarchy prevents single-case → rule
  5. No rules created, no capabilities created

  Caveat (why not zero risk):
  1. distance_pt varies widely (2.5 to 55.2pt) → the "pattern" has a wide spatial range
  2. x_overlap varies (True/False) → structural variation within the group
  3. The pattern is more "same task type" than "identical evidence"
  4. The semantic label dependency (Q4) means the pattern relies on Human judgment
     about case_type, not purely on structural evidence

  RISK = LOW
  The 34 cases genuinely form ONE pattern (caption_like → YES),
  not 34 individual patches. The variation in distance/x_overlap
  does not break the pattern because the judgment is consistent.
```

---

## 8. Q6: Boundary / Counterexample Audit

### 8.1 Counterexample Search Results

```
Searched ALL 79 cases for:
  Cases with SIMILAR Evidence Configuration to Group A
  but DIFFERENT Human Judgment.

Found 16 counterexample/boundary cases:

  TRUE COUNTEREXAMPLES (same structural config, different judgment):
    3 cases: ambiguous_fragment + FIG=True + EXTENT_EXISTS + VR=below → NO
      arxiv_2402.18619_p19_339_297: J=NO, VR=below, XO=YES
      is11_efficientnet_p8_467_415: J=NO, VR=below, XO=YES
      is11_efficientnet_p4_188_461: J=NO, VR=below, XO=NO

  BOUNDARY CASES (same structural config, uncertain):
    1 case: ambiguous_fragment + FIG=True + EXTENT_EXISTS + VR=below → UNCERTAIN
      is11_resnet_p4_464_620: J=UNCERTAIN, VR=below, XO=NO

  BORDERLINE (same structural config, same judgment, different case_type):
    8 cases: ambiguous_fragment + FIG=True + EXTENT_EXISTS + VR=below → YES
      These are consistent with Group A but classified as ambiguous_fragment.

  GROUP B COUNTEREXAMPLES:
    4 cases: Type_B_negative + FIG=NO + EXTENT_EXISTS → UNCERTAIN
      (different VR/XO from Group B candidates)
```

### 8.2 Counterexample Analysis

```
The 3 TRUE counterexamples are CRITICAL:

  They have the SAME structural evidence as Group A:
    - FIG=True (FIG prefix present)
    - EXTENT_EXISTS (drawing extent observed)
    - VR=below (text below drawing)
    - e1_ctx_count=5 (full context available)

  But received judgment NO:
    - The text is NOT associated with the drawing.

  WHY is this possible?
  The structural evidence (FIG prefix + below + extent) looks IDENTICAL.
  But the Human determined the text is NOT a caption for this drawing.

  Possible reasons (from analysis notes):
    - The text may be a caption for a DIFFERENT drawing
    - The text may be a section heading that happens to be near
    - The text may be a reference to a figure elsewhere
    - The "ambiguous_fragment" classification indicates the text's role
      was genuinely ambiguous

  These counterexamples prove:
  → The structural config (FIG + below + extent) does NOT guarantee YES.
  → case_type=caption_like is what separates YES from NO.
  → Without case_type, the structural pattern has counterexamples.
  → WITH case_type, the counterexamples are excluded (they're ambiguous_fragment).

  IMPLICATION:
  The Reusable Signal Candidate is BOUND to case_type.
  If case_type is available → pattern is clean (34/34 YES).
  If case_type is NOT available → pattern has 3 counterexamples (3 NO + 1 UNCERTAIN).
```

### 8.3 Boundary Summary

```
  Counterexamples found: YES
  True counterexamples (same config, NO): 3
  Boundary cases (same config, UNCERTAIN): 1
  Borderline (same config, YES, different case_type): 8

  The candidate pattern HAS boundaries:
  - It works when case_type=caption_like (34/34 YES)
  - It FAILS when case_type=ambiguous_fragment (3 NO, 1 UNCERTAIN out of 11)
  - The boundary is at case_type, not at structural evidence

  This is important: the candidate's stability depends on the
  case_type label being correctly assigned. If a future case is
  misclassified (caption_like when it should be ambiguous_fragment),
  the candidate would produce a false YES.
```

---

## 9. Q7: Minimal Reusable Signal Form

### 9.1 Proposed Form

```
Reusable Signal Candidate =
{
    Evidence Configuration: case_type + fig_prefix + e1_evidence_state + vertical_relation,
    Human Judgment: YES,
    Provenance: text_id + drawing_extent_id + document_id + page,
    Cross-case occurrence: 34 cases, 5 documents
}
```

### 9.2 Assessment

```
MINIMAL_REUSABLE_SIGNAL_FORM = CONDITIONALLY_SUPPORTED

  The form uses ONLY existing Evidence Pack fields:
  - No new schema
  - No rule, threshold, score, confidence
  - No classifier, semantic label (new), recommendation, action, capability, runtime

  BUT: the form depends on case_type (Q4 finding).
  - case_type is an EXISTING field
  - But it is a SEMANTIC LABEL (Human-assigned)
  - Without it, the form has counterexamples (Q6)

  CONDITION:
  The minimal form is supported IF case_type is available in the Evidence Pack.
  It is NOT supported if only pure structural fields are available.

  This is a CONDITION, not a rejection. But it must be explicit.
```

---

## 10. Q8: D3 Validation

### 10.1 D3 Condition Check

| Condition | Status | Evidence |
|-----------|:------:|----------|
| D3-C1 Evidence-linked | ✅ YES | All 37 have text_id + drawing_extent |
| D3-C2 Provenance complete | ✅ YES | 37/37 PROVENANCE_COMPLETE |
| D3-C3 Repeated across independent cases | ✅ YES | 34 cases, 5 documents |
| D3-C4 Consistent Human judgment | ✅ YES | 34/34 YES (Group A), 3/3 YES (Group B) |
| D3-C5 Comparable Evidence Configuration | ⚠️ PARTIAL | x_overlap varies, distance varies; family not identical |
| D3-C6 Not case-specific | ✅ YES | 5 documents, no single-doc dominance |
| D3-C7 No free-text required | ✅ YES | 0/37 require free text |
| D3-C8 No semantic label required | ❌ FALSE | case_type needed (Q4) |

### 10.2 D3 Status

```
D3_STATUS = D3_LIKE_CANDIDATE (not fully D3)

  Two conditions fail or are partial:
  1. D3-C5 (PARTIAL): Configuration is a FAMILY, not identical instances
     - x_overlap: 29 True / 5 False
     - distance: 2.5 to 55.2pt (28 unique values)
  2. D3-C8 (FALSE): Semantic label dependency
     - case_type IS needed to separate YES from NO/UNCERTAIN
     - Without case_type, 3 counterexamples exist

  → The candidate is "D3-like" but NOT fully D3.
  → It cannot be called "D3 validated signal."
  → It is a "D3 candidate with two unresolved conditions."
```

---

## 11. Level Classification

```
Level 1: Case-specific Human Judgment
  → 14 UNCERTAIN cases (G5 boundary)

Level 2: Evidence-linked Human Judgment
  → 20 cases (single instance or inconsistent group)

Level 3: Repeated Evidence Instance
  → 8 cases (repeated but limited)

Level 4: Reusable Signal Candidate
  → 37 cases (THIS GATE's研究对象)
  → BUT: D3-C5 PARTIAL + D3-C8 FALSE → candidate with conditions

Level 5: Validated Reusable Signal
  → NOT_REACHED (requires multi-reviewer validation)

Level 6: Capability
  → FORBIDDEN

CURRENT MAXIMUM: Level 4 (Reusable Signal Candidate, with conditions)
```

---

## 12. Over-Design Audit

```
  O1: Created new Schema?
    → NO. Only analyzed existing fields.

  O2: Created new Evidence Field?
    → NO. Used existing case_type, fig_prefix, e1_evidence_state, etc.

  O3: Created Semantic Label?
    → NO. case_type is EXISTING (not newly created).
    → DISCOVERED that case_type IS a semantic label (Q4 finding), but did NOT create one.

  O4: Created Rule?
    → NO. No rules created. Candidate ≠ rule.

  O5: Created Detector?
    → NO. No detectors created.

  O6: Introduced Similarity / Embedding?
    → NO. Only exact-match grouping on existing fields.

  O7: Treated Candidate as Signal?
    → NO. Candidate remains "candidate" throughout.
    → D3-C5 and D3-C8 failures prevent promotion to validated signal.

  O8: Treated Signal as Capability?
    → NO. No signal validated. No capability created.

  O9: One-Case-One-Patch?
    → NO. 34 cases form one pattern (LOW risk, Q5).

  O10: Increased Human Annotation Burden?
    → NO. No new annotation required. Analysis used existing data.

  ALL CHECKS: FALSE
  OVER_DESIGN_AUDIT = PASS
```

---

## 13. Final Decision

### 13.1 Condition Summary

| Condition | Status |
|-----------|--------|
| Q1 Config Stability | MEDIUM (family, not identical) |
| Q2 Cross-Document | SUPPORTED (5 docs, no single-doc dominance) |
| Q3 Evidence Grounding | A (100% evidence-sufficient) |
| Q4 Semantic Label Dependency | TRUE (case_type needed) |
| Q5 One-Case-One-Patch Risk | LOW |
| Q6 Counterexamples | YES (3 true, 1 boundary) |
| Q7 Minimal Form | CONDITIONALLY_SUPPORTED |
| Q8 D3 Status | D3_LIKE_CANDIDATE (C5 partial, C8 false) |

### 13.2 Decision

```
REUSABLE_SIGNAL_CANDIDATE = CONDITIONAL

  The candidate has SIGNIFICANT strengths:
  - 100% evidence-grounded (Q3=A)
  - Cross-document supported (Q2=YES, 5 docs)
  - 100% judgment consistency (34/34 YES)
  - Low one-case-one-patch risk (Q5=LOW)
  - No free text needed
  - Provenance complete

  But has TWO UNRESOLVED conditions:
  1. Semantic Label Dependency (Q4=TRUE, D3-C8=FALSE)
     → case_type is needed to separate YES from NO/UNCERTAIN
     → Without it, 3 counterexamples exist
     → case_type is existing but IS a semantic label

  2. Configuration Family (Q1=MEDIUM, D3-C5=PARTIAL)
     → x_overlap and distance vary within the group
     → The 34 cases are a family, not identical instances
     → The boundary between "family" and "identical" is unclear

  These conditions do NOT invalidate the candidate.
  But they prevent promotion to "SUPPORTED_FOR_NEXT_VALIDATION."

  WHAT IS MISSING for SUPPORTED_FOR_NEXT_VALIDATION:
  1. Resolve semantic label dependency:
     → Either find a structural proxy for case_type
     → Or accept case_type as a prerequisite (requires research)
  2. Resolve configuration family:
     → Either narrow the config to identical instances
     → Or demonstrate that the family is coherent (requires more cases)
  3. Multi-reviewer validation:
     → 34/34 YES from ONE reviewer may be reviewer-specific
     → Inter-rater reliability UNKNOWN

  NONE of these can be resolved in this READ-ONLY Gate.
  They require either:
  - Human Validation (NOT authorized)
  - New Evidence Pack fields (NOT authorized)
  - New experiments (NOT authorized)

  → CONDITIONAL is the honest assessment.
```

---

## 14. Final Questions

### Q1: 37 个候选是否真的共享一个 Evidence Configuration？

```
PARTIALLY — they share a Configuration FAMILY, not identical instances.

  6/8 fields are identical (case_type, fig_prefix, e1_evidence_state, e1_extent,
  e1_ctx_count, vertical_relation, drawing_extent_present).
  2/8 fields vary (x_overlap: True/False, distance_pt: 2.5-55.2pt).

  EVIDENCE_CONFIGURATION_STABILITY = MEDIUM
```

### Q2: 是否真正跨独立文档重复？

```
YES — 5 documents, no single-document dominance.

  arxiv_2402.18619: 12 (35.3%)
  is11_med_001: 11 (32.4%)
  is11_resnet: 5 (14.7%)
  is11_efficientnet: 4 (11.8%)
  is11_cs_001: 2 (5.9%)

  No document exceeds 50%. All contribute ≥2 cases.
  CROSS_DOCUMENT_INDEPENDENCE = SUPPORTED

  Caveat: all 5 are academic papers (same domain).
  Cross-domain NOT tested (and NOT required by this Gate).
```

### Q3: Human 的判断是否 Evidence-grounded？

```
YES — 100% Evidence-grounded.

  37/37 cases: grounding = A (evidence sufficient)
  - burden_e1 = 0 (E1 Pack sufficient)
  - EXTENT_EXISTS (drawing observed)
  - No document access needed
  - No external knowledge needed

  EVIDENCE_GROUNDING = A
```

### Q4: 是否需要 Semantic Label 才能形成 Signal？

```
YES — semantic label dependency exists.

  SEMANTIC_LABEL_DEPENDENCY = TRUE

  Without case_type (semantic label):
  - 11 ambiguous_fragment cases share the SAME structural config
  - But have MIXED judgments (8 YES, 3 NO, 1 UNCERTAIN)
  - Structural evidence ALONE does not distinguish YES from NO

  With case_type=caption_like:
  - 34/34 YES (100% consistent)
  - Counterexamples excluded

  case_type is EXISTING (not newly created).
  But it IS a semantic label (Human-assigned).
```

### Q5: 是否存在 One-Case-One-Patch 风险？

```
LOW risk.

  ONE_CASE_ONE_PATCH_RISK = LOW

  34 cases form ONE pattern (caption_like → YES), not 34 patches.
  Judgment is consistent (34/34 YES).
  Cross-document (5 docs).
  Five-level hierarchy prevents single-case → rule.

  Caveat: distance/x_overlap vary → family, not identical.
  But variation does not break judgment consistency.
```

### Q6: 是否存在现有 Counterexample？

```
YES — 3 true counterexamples + 1 boundary case.

  3 TRUE counterexamples:
    ambiguous_fragment + FIG=True + EXTENT_EXISTS + VR=below → NO
    (same structural config as Group A, different judgment)

  1 BOUNDARY case:
    ambiguous_fragment + FIG=True + EXTENT_EXISTS + VR=below → UNCERTAIN

  These prove: structural config alone does NOT guarantee YES.
  case_type is needed to exclude counterexamples.
  The candidate's boundary is at case_type, not at structural evidence.
```

### Q7: 最小 Reusable Signal 是否可以只由 Evidence Configuration + Human Judgment + Provenance + Repeated Occurrence 构成？

```
CONDITIONALLY_SUPPORTED.

  The form CAN be expressed using only existing fields:
  {case_type, fig_prefix, e1_evidence_state, VR, Judgment, Provenance, Count}

  BUT: it requires case_type (a semantic label) to work.
  Without case_type, the form has counterexamples.

  MINIMAL_REUSABLE_SIGNAL_FORM = CONDITIONALLY_SUPPORTED
  (supported IF case_type is available; not supported with structural-only fields)
```

### Q8: D3 Candidate 是否成立？

```
D3_LIKE_CANDIDATE — not fully D3.

  D3-C1 through C4, C6, C7: YES (6/8 met)
  D3-C5 (comparable config): PARTIAL (family, not identical)
  D3-C8 (no semantic label): FALSE (case_type needed)

  Two conditions fail → cannot be called "D3 validated signal."
  It is a "D3-like candidate with two unresolved conditions."
```

### Q9: 当前是否已经有资格进入"Validated Reusable Signal"研究？

```
NO — NOT YET.

  Three blockers:
  1. Semantic label dependency (Q4) — unresolved
  2. Configuration family (Q1=MEDIUM) — not identical
  3. Single Human reviewer — inter-rater UNKNOWN

  Additionally:
  4. Counterexamples exist (Q6) — pattern has boundaries
  5. P1 A/B INCONCLUSIVE — no Human-level benefit demonstrated

  Level 4 (Candidate) is the current maximum.
  Level 5 (Validated Signal) requires:
  - Multi-reviewer validation (NOT authorized)
  - Semantic label resolution (NOT authorized to create new fields)
  - Configuration narrowing (requires more data or research)
```

### Q10: 下一步是否应该继续研究，还是应该 STOP？

```
STOP — but with recorded conditions for future resumption.

  REASONING:
  - The candidate has genuine structural merit (34/34 YES, 5 docs, evidence-grounded)
  - But it has two unresolved conditions that CANNOT be resolved in READ-ONLY mode
  - No further READ-ONLY analysis can resolve:
    a) Semantic label dependency (requires either new fields or Human validation)
    b) Inter-rater reliability (requires new Human validation)
    c) Configuration family (requires more data or implementation)
  - Continuing READ-ONLY research would repeat the same findings

  WHAT TO DO IF RESUMED IN THE FUTURE:
  1. Multi-reviewer validation: have ≥2 Humans judge the same 79 cases
     → Check if 34/34 YES holds across reviewers
  2. Semantic label resolution: research whether case_type can be
     structurally derived (without creating new semantic labels)
  3. Configuration narrowing: analyze if sub-groups (XO=True vs False)
     have different stability profiles
  4. Cross-domain test: apply the pattern to non-academic documents
     → Check if caption_like → YES holds outside academic domain

  ALL of these require authorization that is currently FALSE.

  STOP = TRUE
  The candidate is RECORDED but NOT VALIDATED.
  Future research is POSSIBLE but NOT AUTHORIZED.
```

---

## 15. Limitations

```
  RV-L-01: SINGLE HUMAN REVIEWER
    34/34 YES from one reviewer. Inter-rater reliability UNKNOWN.
    → The candidate's consistency may be reviewer-specific.

  RV-L-02: SEMANTIC LABEL DEPENDENCY
    case_type is needed but is a Human-assigned semantic label.
    → Without it, 3 counterexamples exist.
    → The candidate is not purely structural.

  RV-L-03: CONFIGURATION FAMILY
    34 cases share 6/8 fields but vary in x_overlap and distance.
    → Not identical instances; a family of similar configs.

  RV-L-04: COUNTEREXAMPLES EXIST
    3 ambiguous_fragment cases with same structural config → NO.
    → The structural pattern has boundaries.
    → case_type is the boundary, not structural evidence.

  RV-L-05: SAME DOMAIN
    All 5 documents are academic papers.
    → Cross-domain generalization NOT tested.

  RV-L-06: P1 INCONCLUSIVE
    No Human-level benefit demonstrated.
    → Cannot claim the candidate improves system performance.

  RV-L-07: NO IMPLEMENTATION TEST
    The candidate is a research finding, not a tested system component.
    → Actual binding behavior in a live system unverified.

  RV-L-08: GROUP B TOO SMALL
    3 cases is insufficient for strong conclusions.
    → Group B is an auxiliary observation, not a validated candidate.
```

---

## 16. Files Created

```
tmp/human_evidence_binding_reusable_signal_validation.md          (this file)
tmp/human_evidence_binding_reusable_signal_validation.json         (structured data)
tmp/human_evidence_binding_reusable_signal_validation_case_table.csv (53 rows: 37 candidates + 16 counterexamples)
```

---

## 17. Final Governance State

```
RESEARCH_STATUS = COMPLETE

SYSTEM_MODIFIED = FALSE
IMPLEMENTATION_AUTHORIZED = FALSE
EXPERIMENT_AUTHORIZED = FALSE
HUMAN_VALIDATION_AUTHORIZED = FALSE

FROZEN_BASELINE = INTACT
BASELINE_DRIFT = 0

NEW_SCHEMA = NONE
NEW_FIELD = NONE
NEW_RULE = NONE
NEW_DETECTOR = NONE
NEW_CAPABILITY = NONE

RUNTIME_AUTHORITY = ZERO
PRODUCTION = FALSE

STOP = TRUE
```

---

## STOP

```
Human-Evidence Binding Reusable Signal Validation Gate is COMPLETE.

SUMMARY:
  - 37 Reusable Signal Candidates validated against 8 strict conditions
  - 6/8 D3 conditions met; 2 fail (C5 partial, C8 false)
  - KEY FINDING: Semantic Label Dependency (case_type needed)
    → Structural evidence alone has 3 counterexamples
    → case_type separates YES from NO/UNCERTAIN
    → case_type is existing but IS a semantic label
  - KEY STRENGTH: 100% Evidence-grounded (37/37 grounding=A)
  - KEY STRENGTH: Cross-document (5 docs, no single-doc dominance)
  - KEY STRENGTH: 100% judgment consistency (34/34 YES)
  - KEY WEAKNESS: Counterexamples exist (3 NO + 1 UNCERTAIN)
  - KEY WEAKNESS: Single Human reviewer (inter-rater UNKNOWN)

FINAL DECISION: CONDITIONAL
  The candidate has genuine structural merit but two unresolved conditions.
  Cannot be promoted to SUPPORTED_FOR_NEXT_VALIDATION.
  Cannot be promoted to Validated Reusable Signal (Level 5).
  Future resumption requires authorization currently FALSE.

  Candidate ≠ Validated Signal ≠ Rule ≠ Capability

  不得自动进入下一阶段。
  不得创建任何 Rule。
  不得创建任何 Capability。
  不得把 Candidate 当作 Validated Signal。
  不得把 Conditional 当作 Pass。
  STOP = TRUE
```
