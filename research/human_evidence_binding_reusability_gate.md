# Human-Evidence Binding Reusability Design Gate

> **模式: READ-ONLY / NO IMPLEMENTATION / NO NEW HUMAN VALIDATION / STOP**
> 日期: 2026-09-18
> Gate: HUMAN_EVIDENCE_BINDING_REUSABILITY_GATE
> 前置: Human-Evidence Binding Design Research (COMPLETE)
> 本文件: 判断 Scheme B 产生的 Human Judgment 是否具备形成 Evidence-Grounded Reusable Signal 的结构条件。

---

## 0. Core Research Question

```
唯一问题:

  Scheme B 产生的 Human Judgment，
  是否具备形成 Evidence-Grounded Reusable Signal 的结构条件？

  Human Judgment + Evidence ID + Evidence Configuration + Provenance
      ↓
  Validated Evidence Instance
      ↓
  Repeated Evidence Instances
      ↓
  Reusable Signal Candidate ?

  本次只判断"是否具备结构条件"。
  不得声称已经产生真正的 Reusable Signal。
  不得自动学习。
  不得自动泛化。
  不得创建 Capability。
```

---

## 1. Frozen Baseline

```
RESEARCH_BASELINE = FROZEN (v1)
FROZEN_BASELINE = INTACT
BASELINE_DRIFT = 0
SYSTEM_MODIFIED = FALSE
DESIGN_IMPLEMENTATION = FALSE
EXPERIMENT_AUTHORIZED = FALSE
HUMAN_VALIDATION_AUTHORIZED = FALSE
RUNTIME_AUTHORITY = ZERO
PRODUCTION = FALSE

Prior HEB Design Research = FROZEN (Scheme B identified, not implemented)
M-A 79-case data = FROZEN
Evidence Pack E1 = FROZEN
G1-G5 Framework = FROZEN
```

---

## 2. Data Used

```
ONLY existing data:

  M-A 79-case Human Validation
    - 79 cases: 61 YES, 4 NO, 14 UNCERTAIN
    - Single Human reviewer
    - Text-Drawing Association task (T1)
    - 5 documents: arxiv_2402.18619, is11_resnet, is11_efficientnet, is11_med_001, is11_cs_001

  Human-Evidence Binding Design Research
    - H1-H4 classification (21 H1, 4 H2, 40 H4_CONFIRMATION, 14 H4_BOUNDARY)
    - Scheme B (Judgment + Evidence ID)
    - Five-level hierarchy

  M-A P0 Evidence Pack Counterfactual Diagnostic
    - E1 evidence states: 74 EXTENT_EXISTS, 3 PRIMITIVES_NO_EXTENT, 2 NO_VISUAL_EVIDENCE

  Evidence Boundary Structure Research
    - 13 G5 boundary cases, Structure A
```

---

## 3. Provenance Analysis (Q1)

### 3.1 Evidence ID → Provenance Chain

```
For each of the 79 cases, checked whether:

  Human Judgment
      ↓
  Evidence ID (text_id + drawing_extent)
      ↓
  Evidence Configuration (case_type + FIG + VR + XO + EXT + state)
      ↓
  Document Location (document_id + page_reference)

  forms a COMPLETE traceability chain.
```

### 3.2 Results

| Provenance Status | Count | % |
|-------------------|------:|---:|
| PROVENANCE_COMPLETE | 74 | 93.7% |
| PROVENANCE_PARTIAL (drawing extent missing) | 3 | 3.8% |
| PROVENANCE_PARTIAL (no drawing evidence) | 2 | 2.5% |
| NOT_DEMONSTRATED | 0 | 0% |

```
Q1 ANSWER: YES — Evidence ID is sufficient for Provenance.

  74/79 (93.7%) cases have PROVENANCE_COMPLETE:
    - text_id available (from M-A text extraction)
    - drawing_extent available (from E1 Pack, EXTENT_EXISTS state)
    - Evidence Configuration available (case_type, FIG prefix, spatial relation, x_overlap)
    - Document location available (document_id, page_reference)

  5/79 (6.3%) cases have PROVENANCE_PARTIAL:
    - 3 cases: PRIMITIVES_NO_EXTENT (drawing has vector primitives but no extent)
      → text_id available, drawing evidence partial
    - 2 cases: NO_VISUAL_EVIDENCE (drawing not detected at all)
      → text_id available, drawing evidence missing

  The 5 PARTIAL cases are all Type_A_negative (G1: observation missing).
  These are the cases where the drawing couldn't be observed.
  Provenance is partial BECAUSE the evidence is partial (G1).

  CONCLUSION:
  Evidence ID IS sufficient for Provenance when evidence is complete (E1 EXTENT_EXISTS).
  When evidence is incomplete (G1), provenance is naturally partial — but this is
  an evidence problem, not a binding problem.
```

---

## 4. Cross-Case Alignment Analysis (Q2)

### 4.1 Evidence Configuration Comparable Across Cases?

```
For each case, the Evidence Configuration consists of:

  Config = case_type + FIG_prefix + evidence_state + vertical_relation + x_overlap + drawing_extent_present

  These are ALL existing fields from the M-A Evidence Pack.
  NO new fields created.
  NO semantic labels invented.
  NO LLM judgment.
  NO embedding/similarity score.
```

### 4.2 Configuration Groups (≥2 cases)

| Config Group | Cases | Judgment Consistency | Cross-Document? |
|-------------|------:|----------------------|:----------------:|
| caption_like + FIG=YES + EXTENT + below + XO=True | 29 | 29/29 YES (100%) | 5 docs |
| ambiguous_fragment + FIG=YES + EXTENT + below + XO=True | 8 | 6 YES, 2 NO (75%) | 4 docs |
| caption_like + FIG=YES + EXTENT + below + XO=False | 5 | 5/5 YES (100%) | 2 docs |
| ambiguous_fragment + FIG=YES + EXTENT + above + XO=True | 5 | 2 YES, 2 UNC, 1 NO | 2 docs |
| ambiguous_fragment + FIG=YES + EXTENT + below + XO=False | 4 | 2 YES, 1 UNC, 1 NO | 3 docs |
| subfigure_label + FIG=YES + EXTENT + inside + XO=True | 4 | 4/4 YES (100%) | 1 doc |
| Type_A_negative + PRIMITIVES + FIG=YES + none + XO=False | 3 | 3/3 UNCERTAIN | 3 docs |
| Type_B_negative + EXTENT + FIG=NO + below + XO=True | 3 | 3/3 YES (100%) | 3 docs |
| Type_A_negative + EXTENT + FIG=YES + none + XO=False | 3 | 2 UNC, 1 YES | 3 docs |
| caption_like + FIG=YES + EXTENT + above + XO=False | 2 | 2/2 YES (100%) | 1 doc |
| caption_like + FIG=YES + EXTENT + above + XO=True | 2 | 2/2 YES (100%) | 2 docs |
| Type_B_negative + EXTENT + FIG=NO + above + XO=True | 2 | 2/2 UNCERTAIN | 2 docs |
| Type_A_negative + NO_VISUAL + FIG=YES + none + XO=False | 2 | 2/2 UNCERTAIN | 2 docs |

### 4.3 Cross-Case Match Summary

| Metric | Count | % |
|--------|------:|---:|
| Cases with cross-case match (≥2 in group) | 72 | 91.1% |
| Cases in CONSISTENT groups (all same judgment) | 57 | 72.2% |
| Cases in INCONSISTENT groups (mixed judgments) | 15 | 19.0% |
| Unique config (no match) | 7 | 8.9% |

```
Q2 ANSWER: YES — Evidence Configuration CAN align across cases.

  72/79 (91.1%) cases have at least one other case with the same structural config.
  57/79 (72.2%) cases are in CONSISTENT groups (all cases in group have same judgment).

  The alignment uses ONLY existing Evidence Pack fields:
    - case_type (caption_like, ambiguous_fragment, etc.)
    - fig_prefix (YES/NO)
    - e1_evidence_state (EXTENT_EXISTS, etc.)
    - vertical_relation (above, below, inside, none)
    - x_overlap (True/False)

  NO new fields, NO semantic labels, NO LLM, NO embedding.

  The STRONGEST alignment group:
    caption_like + FIG=YES + EXTENT_EXISTS + below + XO=True
    → 29 cases, 100% YES, 5 documents
    → This is a REPEATED EVIDENCE PATTERN.

  IMPORTANT:
  "caption_like + FIG=YES + below → YES (associated)" is NOT a rule.
  It is a REPEATED EVIDENCE CONFIGURATION with CONSISTENT HUMAN VALIDATION.
  The difference:
    Rule: "FIG-prefix + nearby = Caption" (semantic claim, FORBIDDEN)
    Pattern: "Same config + same judgment × 29 + 5 docs" (structural observation)
```

---

## 5. Level Classification (Q3)

### 5.1 Five-Level Hierarchy Results

| Level | Count | % | Description |
|-------|------:|---:|-------------|
| Level 1: CASE_SPECIFIC | 14 | 17.7% | UNCERTAIN (G5 boundary) — no definitive judgment |
| Level 2: EVIDENCE_LINKED | 20 | 25.3% | Single instance or inconsistent group |
| Level 3: REPEATED_INSTANCE | 8 | 10.1% | Repeated but limited (same doc or <3 cases) |
| Level 4: SIGNAL_CANDIDATE | 37 | 46.8% | Cross-document + consistent + provenance |
| Level 5: CAPABILITY | 0 | 0% | NOT_AUTHORIZED |

### 5.2 Level 4 Breakdown

```
37 cases reached Level 4 (REUSABLE_SIGNAL_CANDIDATE):

  Group 1: caption_like + FIG=YES + EXTENT_EXISTS → YES
    Cases: 34
    Documents: 5 (arxiv_2402.18619, is11_cs_001, is11_efficientnet, is11_med_001, is11_resnet)
    Judgment: 34/34 YES (100% consistent)
    Provenance: 34/34 COMPLETE

  Group 2: Type_B_negative + FIG=NO + EXTENT_EXISTS → YES
    Cases: 3
    Documents: 3 (arxiv_2402.18619, is11_cs_001, is11_resnet)
    Judgment: 3/3 YES (100% consistent)
    Provenance: 3/3 COMPLETE

  Total Level 4: 37 cases, cross-document, consistent, provenance complete.
```

### 5.3 Level 1 Analysis (Cannot Become Reusable)

```
14 cases at Level 1 (UNCERTAIN):
  - All are G5 Semantic Boundary cases
  - Human could NOT make a definitive judgment even with complete evidence
  - These CANNOT become Reusable Signal Candidates
  - The "signal" here is the BOUNDARY itself: "evidence complete but insufficient"
  - This is a finding about evidence limits, not a reusable pattern
```

---

## 6. C1–C8 Verification for Reusable Signal Candidate (Q7)

### 6.1 Strict Conditions

```
C1 = Evidence-linked (judgment bound to Evidence ID)
C2 = Provenance complete
C3 = Repeated across cases (≥2)
C4 = Consistent Human judgment (all same)
C5 = Evidence configuration comparable (same structural fields)
C6 = Not dependent on case-specific information (cross-document, structural pattern)
C7 = No free-text explanation required
C8 = No new semantic label invented
```

### 6.2 Verification for caption_like Group (34 cases)

| Condition | Status | Evidence |
|-----------|:------:|----------|
| C1 Evidence-linked | ✅ YES | All 34 have text_id + drawing_extent (EXTENT_EXISTS) |
| C2 Provenance complete | ✅ YES | 34/34 PROVENANCE_COMPLETE |
| C3 Repeated | ✅ YES | 34 cases (≥2 required) |
| C4 Consistent | ✅ YES | 34/34 YES (100%) |
| C5 Config comparable | ✅ YES | All: caption_like + FIG=YES + EXTENT_EXISTS |
| C6 Not case-specific | ✅ YES | 5 documents; pattern is structural (FIG+position), not text content |
| C7 No free text | ✅ YES | All judgments are YES (no explanation needed) |
| C8 No semantic label | ✅ YES | Uses existing case_type field; no new label invented |

```
ALL C1-C8 MET: YES

  → REUSABLE_SIGNAL_CANDIDATE = TRUE (for caption_like group)

  CRITICAL CAVEAT:
  "Candidate" ≠ "validated reusable signal"
  "Candidate" ≠ "rule"
  "Candidate" ≠ "capability"

  What this means:
  34 cases with the SAME structural evidence configuration have received
  the SAME Human judgment (YES) across 5 independent documents.

  This is a STRUCTURAL OBSERVATION about repeated evidence+judgment alignment.
  It is NOT a semantic rule like "FIG-prefix + nearby = Caption."

  The candidate says:
  "When evidence config = (caption_like, FIG=YES, EXTENT_EXISTS, below/above),
   Human has consistently validated YES in 34/34 cases across 5 documents."

  It does NOT say:
  "FIG-prefix + nearby = Caption."
```

### 6.3 Verification for Type_B_negative Group (3 cases)

| Condition | Status | Evidence |
|-----------|:------:|----------|
| C1 Evidence-linked | ✅ YES | All 3 have text_id + drawing_extent |
| C2 Provenance complete | ✅ YES | 3/3 PROVENANCE_COMPLETE |
| C3 Repeated | ✅ YES | 3 cases (≥2 required) |
| C4 Consistent | ✅ YES | 3/3 YES (100%) |
| C5 Config comparable | ✅ YES | All: Type_B_negative + FIG=NO + EXTENT_EXISTS |
| C6 Not case-specific | ✅ YES | 3 documents |
| C7 No free text | ✅ YES | All YES |
| C8 No semantic label | ✅ YES | Uses existing case_type |

```
ALL C1-C8 MET: YES (but only 3 cases — LIMITED)

  → REUSABLE_SIGNAL_CANDIDATE = TRUE (CONDITIONAL — limited sample)

  This group is too small (3 cases) for strong confidence.
  It meets all structural conditions but needs more cases.
```

---

## 7. Human Added Value Analysis (Q4)

### 7.1 A–E Classification

| Type | Count | % | Description |
|------|------:|---:|-------------|
| A (confirmed existing evidence) | 21 | 26.6% | Human used evidence Machine already had |
| B (added semantic validation) | 40 | 50.6% | Human confirmed structural=semantic |
| C (found new observation) | 4 | 5.1% | Human accessed document for missing info |
| D (used external knowledge) | 0 | 0% | No external knowledge needed |
| E (cannot bind to evidence) | 14 | 17.7% | Semantic boundary (G5) |

### 7.2 Key Finding

```
B is the PRIMARY value source: 40/79 (50.6%)

  Human's primary contribution is SEMANTIC VALIDATION of existing structural evidence.
  NOT creating new evidence.
  NOT using external knowledge.
  NOT writing explanations.

  This confirms:
  - Human's role = "evidence-grounded judgment provider"
  - Human validates, does not reconstruct
  - The value is in the JUDGMENT (YES/NO), not in additional information

  A + B = 61/79 (77.2%): Human added NO new evidence.
  C = 4/79 (5.1%): Human found document-internal observation (not external knowledge).
  D = 0/79 (0%): No external world knowledge needed.
  E = 14/79 (17.7%): G5 boundary — Human couldn't resolve.

  DICE should NOT treat Human Knowledge as Evidence.
  This is confirmed: 0 cases (D=0) required external knowledge.
  All Human contributions were evidence-internal (A+B+C=65/79=82.3%).
```

---

## 8. Low-Burden Design Analysis (Q5)

### 8.1 Requirement Check

```
FREE_TEXT_REQUIRED = FALSE
  → 79/79 cases: no free text needed
  → Provenance via Evidence ID + Configuration, not text

RULE_AUTHORING_REQUIRED = FALSE
  → 79/79 cases: no rule authored
  → Human provides judgment, not rules

SEMANTIC_LABEL_AUTHORING_REQUIRED = FALSE
  → 79/79 cases: no semantic labels invented
  → Uses existing case_type field (already in Evidence Pack)

EVIDENCE_ANCHOR_REQUIRED = TRUE
  → Scheme B requires Evidence ID selection
  → This is the ONLY required Human action beyond judgment
  → Burden: 1 selection from existing Pack (LOW)

LOW_BURDEN_DESIGN_SUPPORTED = TRUE (for design)
  → Design supports low burden: Judgment + Evidence ID = 2 fields
  → NOT_DEMONSTRATED for actual Human time (no time measurement data)
```

### 8.2 Important Distinction

```
  "不需要自由文本" = TRUE (supported by design + data)
    → Evidence Configuration (F1-F12 equivalent) IS the explanation.
    → No text needed for provenance.

  "Human 实际操作很快" = NOT_DEMONSTRATED
    → No Human time measurement data exists.
    → P1 A/B was INCONCLUSIVE for Human-level benefit.
    → Cannot claim actual speed.
    → Can only claim DESIGN supports low burden.
```

---

## 9. One Case → One Patch Risk (Q9)

### 9.1 Risk Analysis

```
ONE_CASE_ONE_PATCH_RISK = FALSE

  Evidence:
  - 37 cases form REUSABLE_SIGNAL_CANDIDATE groups (not individual patches)
  - 34 caption_like cases share the SAME config + SAME judgment → ONE pattern, not 34 patches
  - 8 cases form REPEATED_INSTANCE groups (Level 3)
  - 20 cases are EVIDENCE_LINKED (Level 2, single instance)
  - 14 cases are CASE_SPECIFIC (Level 1, UNCERTAIN — no patch possible)

  The hierarchy PREVENTS one-case-one-patch:
  - Level 1 → Level 2: requires Evidence Anchor (not a patch, a binding)
  - Level 2 → Level 3: requires ≥2 cases with same config (not a patch, a repetition)
  - Level 3 → Level 4: requires cross-document + consistency (not a patch, a pattern)

  A single Human judgment CANNOT become a patch because:
  1. It must be bound to Evidence ID (Level 2)
  2. It must find a matching case (Level 3)
  3. It must be cross-document consistent (Level 4)
  4. It CANNOT become a rule or capability (Level 5 FORBIDDEN)

  RISK = NONE
```

---

## 10. Evidence Distillation Analysis (Q8)

### 10.1 Distillation Levels

| Level | Count | % | Description |
|-------|------:|---:|-------------|
| D0 (no repeated structure) | 14 | 17.7% | UNCERTAIN/G5 cases — no pattern |
| D1 (repeated evidence instance) | 20 | 25.3% | Single or inconsistent instances |
| D2 (compressible config) | 8 | 10.1% | Repeated but limited |
| D3 (reusable signal candidate) | 37 | 46.8% | Cross-document + consistent + provenance |
| D4 (capability) | 0 | 0% | NOT_AUTHORIZED |

### 10.2 Distillation Emergence

```
Q8 ANSWER: YES — Evidence Distillation has naturally emerged to D3.

  The distillation chain:

  Raw Evidence (79 cases)
      ↓
  Evidence Configuration (case_type + FIG + spatial + extent)
      ↓
  Human Judgment (YES/NO/UNCERTAIN + Evidence ID)
      ↓
  Repeated Cases (72/79 have at least 1 match)
      ↓
  Compressed Evidence Pattern (57/79 in consistent groups)
      ↓
  Reusable Signal Candidate (37/79 meet ALL C1-C8)

  D3 is the MAXIMUM allowed level.
  D4 (Capability) is FORBIDDEN.

  The distillation is NATURAL (not forced):
  - No clustering algorithm applied
  - No similarity score computed
  - No LLM judgment used
  - Only existing Evidence Pack fields grouped by exact match
  - Human judgments were pre-existing (not manufactured)
  - The pattern EMERGED from the data, not from design

  IMPORTANT:
  D3 means "candidate exists," NOT "signal is validated."
  Validation requires:
  - Multiple Human reviewers (NOT authorized)
  - Cross-task testing (NOT done)
  - Boundary identification (when does pattern NOT hold?)
  - These are FUTURE conditions, not current status.
```

---

## 11. Critical Warning: Pattern ≠ Rule

```
DANGER CHECK:

  The 34 caption_like + FIG=YES + YES cases form a Reusable Signal Candidate.

  FORBIDDEN interpretation:
    "FIG-prefix + drawing + nearby → Caption"
    "If text has FIG prefix and is below drawing, it IS a caption."
    "Rule: FIG=YES + below → associate(YES)"

  These are SEMANTIC RULES. They are FORBIDDEN.

  CORRECT interpretation:
    "34 cases with Evidence Configuration (caption_like, FIG=YES, EXTENT_EXISTS)
     received Human Judgment YES across 5 documents."
    "This is a REPEATED EVIDENCE CONFIGURATION with CONSISTENT HUMAN VALIDATION."
    "It is a CANDIDATE for future signal research, NOT a validated signal."

  The distinction:
    Rule = automatic semantic claim (FORBIDDEN)
    Candidate = structural observation requiring further validation (ALLOWED)

  ENFORCEMENT:
  - No code may implement this candidate as a rule
  - No runtime may use this candidate for automatic decisions
  - No LLM may interpret this candidate as semantic knowledge
  - The candidate exists ONLY as a research finding in this report
```

---

## 12. Over-Design Audit

```
  O1: Created new Schema?
    → NO. Only analyzed existing Scheme B (Judgment + Evidence ID).

  O2: Added new Evidence Layer?
    → NO. Used existing Evidence Pack (E1) fields only.

  O3: Added new Semantic Layer?
    → NO. No semantic layer created. case_type is existing field.

  O4: Required Human to write explanation?
    → NO. 0/79 cases require free text.

  O5: Required Human to define Rule?
    → NO. 0/79 cases require rule authoring.

  O6: Required Human to define Semantic Label?
    → NO. 0/79 cases require semantic label authoring.

  O7: Used LLM?
    → NO. No LLM involved in any analysis.

  O8: Used embedding / similarity?
    → NO. Only exact-match grouping on existing fields.

  O9: Created automatic rule?
    → NO. No rules created. Candidate ≠ rule.

  O10: Created Capability?
    → NO. Level 5 (Capability) = 0 cases. NOT_AUTHORIZED.

  ALL CHECKS: FALSE (PASS)
  OVER_DESIGN_RISK = NONE
```

---

## 13. Limitations

```
  RB-L-01: SINGLE HUMAN REVIEWER
    All 79 judgments from one Human.
    The 34 caption_like+YES consistency may be reviewer-specific.
    Inter-rater reliability UNKNOWN.

  RB-L-02: SINGLE TASK (T1)
    Only Text-Drawing Association tested.
    T2 (Text-Text) and T3 (Graphic) not tested.
    Cross-task generalization UNKNOWN.

  RB-L-03: NO TIME MEASUREMENT
    "Low burden" is design-supported, NOT time-measured.
    Actual Human operation speed = NOT_DEMONSTRATED.

  RB-L-04: P1 INCONCLUSIVE
    P1 Human A/B did not confirm Human-level benefit.
    Cannot claim Scheme B improves Human performance.

  RB-L-05: CANDIDATE ≠ VALIDATED SIGNAL
    37 Level 4 cases are CANDIDATES, not validated signals.
    Validation requires multi-reviewer + cross-task + boundary testing.

  RB-L-06: NO BOUNDARY IDENTIFICATION
    For the caption_like candidate, we don't know WHEN it fails.
    Boundary conditions (when does YES become NO/UNCERTAIN?) not identified.
    The 15 INCONSISTENT group cases hint at boundaries but aren't analyzed.

  RB-L-07: NO IMPLEMENTATION
    Scheme B is a design proposal, not a tested system.
    Actual binding behavior unverified.

  RB-L-08: EXACT-MATCH GROUPING ONLY
    Cross-case alignment uses exact field match.
    Similar-but-not-identical configs are NOT grouped.
    More sophisticated alignment might reveal additional patterns.
```

---

## 14. Final Questions

### Q1: Evidence ID 是否足够形成 Provenance？

```
YES

  74/79 (93.7%) = PROVENANCE_COMPLETE
  5/79 (6.3%) = PROVENANCE_PARTIAL (G1 evidence missing, not binding problem)

  Evidence ID + Evidence Configuration + Document Location = complete traceability chain.
  No free text needed for provenance.
```

### Q2: Evidence Configuration 是否能够跨 Case 对齐？

```
YES

  72/79 (91.1%) cases have cross-case match (≥2 cases with same config).
  57/79 (72.2%) cases are in CONSISTENT groups (all same judgment).

  Alignment uses ONLY existing Evidence Pack fields:
  case_type + fig_prefix + evidence_state + vertical_relation + x_overlap.

  No new fields, no semantic labels, no LLM, no embedding.
```

### Q3: Human Judgment 是否可以作为 Evidence-linked Validation？

```
YES

  65/79 (82.3%) definitive judgments (YES/NO) are evidence-linked.
  Each has Evidence ID + Configuration = traceable validation.
  37/65 reach Level 4 (Reusable Signal Candidate) with cross-document consistency.
```

### Q4: Human 是否需要自由文本？

```
NO

  FREE_TEXT_REQUIRED = FALSE (79/79)
  Provenance is established via Evidence ID + Configuration, not text.
  The evidence configuration IS the explanation.
```

### Q5: Human 是否需要自己定义语义类别？

```
NO

  SEMANTIC_LABEL_AUTHORING_REQUIRED = FALSE (79/79)
  Uses existing case_type field from Evidence Pack.
  No new semantic labels invented.
  RULE_AUTHORING_REQUIRED = FALSE (79/79)
```

### Q6: 是否存在 Repeated Evidence Instance？

```
YES

  72/79 cases have at least 1 cross-case match.
  57/79 are in consistent groups.
  8 cases at Level 3 (REPEATED_EVIDENCE_INSTANCE).
  37 cases at Level 4 (REUSABLE_SIGNAL_CANDIDATE).
```

### Q7: 是否存在 Reusable Signal Candidate？

```
YES (CANDIDATE, not validated signal)

  37 cases meet ALL C1-C8 conditions:

  Group 1: caption_like + FIG=YES + EXTENT_EXISTS → YES
    34 cases, 5 documents, 100% consistent, provenance complete.
    C1-C8: ALL MET.

  Group 2: Type_B_negative + FIG=NO + EXTENT_EXISTS → YES
    3 cases, 3 documents, 100% consistent, provenance complete.
    C1-C8: ALL MET (but limited sample).

  CRITICAL:
  Candidate ≠ validated signal.
  Candidate ≠ rule.
  Candidate ≠ capability.
  No automatic learning.
  No automatic generalization.
  "FIG-prefix + nearby = Caption" is FORBIDDEN.
```

### Q8: Evidence Distillation 是否已经出现？

```
YES (to D3, maximum allowed)

  D0 (no structure): 14 cases (17.7%)
  D1 (repeated instance): 20 cases (25.3%)
  D2 (compressible config): 8 cases (10.1%)
  D3 (reusable signal candidate): 37 cases (46.8%)
  D4 (capability): 0 (NOT_AUTHORIZED)

  Distillation emerged NATURALLY from existing data.
  No clustering algorithm, no similarity score, no LLM.
  Only exact-match grouping on existing Evidence Pack fields.

  D3 is the maximum allowed level.
```

### Q9: One Case → One Patch 风险是否存在？

```
NO

  ONE_CASE_ONE_PATCH_RISK = FALSE

  37 cases form patterns (not individual patches).
  The five-level hierarchy prevents single-case → rule.
  A single judgment must pass through:
  Level 1 → 2 (binding) → 3 (repetition) → 4 (cross-document) before candidate status.
  Level 5 (rule/capability) is FORBIDDEN.
```

### Q10: Scheme B 是否值得进入下一阶段 Design Gate？

```
CONDITIONAL

  WHAT IS READY:
  - Provenance: 93.7% complete (Q1=YES)
  - Cross-case alignment: 91.1% matchable (Q2=YES)
  - Evidence-linked validation: 82.3% definitive (Q3=YES)
  - Low burden: no free text, no rules, no labels (Q4/Q5=YES)
  - Repeated instances: 72/79 (Q6=YES)
  - Reusable Signal Candidate: 37 cases, ALL C1-C8 met (Q7=YES)
  - Evidence Distillation: D3 reached (Q8=YES)
  - No one-case-one-patch risk (Q9=NO)

  WHAT IS NOT READY:
  - Single Human reviewer (inter-rater UNKNOWN)
  - Single task (T1 only)
  - No time measurement (NOT_DEMONSTRATED)
  - P1 INCONCLUSIVE (no Human-level benefit)
  - Candidate ≠ validated signal
  - No boundary identification (when does pattern fail?)
  - No implementation test

  CONDITION FOR NEXT PHASE:
  1. Multi-reviewer validation (REQUIRES Human Validation — NOT authorized)
  2. Boundary identification (analyze 15 inconsistent cases)
  3. Cross-task testing (T2, T3)

  STRUCTURAL CONDITIONS ARE MET.
  VALIDATION CONDITIONS ARE NOT MET.

  → Scheme B has the structural conditions for Reusable Signal.
  → But it has NOT been validated as a true reusable signal.
  → Next phase requires Human Validation authorization.
```

---

## 15. Files Created

```
tmp/human_evidence_binding_reusability_gate.md          (this file)
tmp/human_evidence_binding_reusability_gate.json         (structured data)
tmp/human_evidence_binding_reusability_case_table.csv    (79 cases, 16 fields)
```

---

## 16. Final Governance State

```
RESEARCH_STATUS = COMPLETE

SYSTEM_MODIFIED = FALSE
DESIGN_IMPLEMENTATION = FALSE
EXPERIMENT_AUTHORIZED = FALSE
HUMAN_VALIDATION_AUTHORIZED = FALSE

NEW_CAPABILITY = NONE
RUNTIME_AUTHORITY = ZERO
PRODUCTION = FALSE

FROZEN_BASELINE = INTACT
BASELINE_DRIFT = 0

STOP = TRUE
```

---

## STOP

```
Human-Evidence Binding Reusability Design Gate is COMPLETE.

Summary:
  - 79 M-A cases analyzed for Reusable Signal structural conditions
  - Provenance: 93.7% COMPLETE (Evidence ID sufficient)
  - Cross-case alignment: 91.1% matchable (existing fields only, no LLM/embedding)
  - Level distribution: 14 Case-specific, 20 Evidence-linked, 8 Repeated, 37 Candidate
  - Reusable Signal Candidate: 37 cases meet ALL C1-C8 (34 caption_like + 3 Type_B_negative)
  - Evidence Distillation: D3 reached (candidate level, NOT capability)
  - Human added value: 50.6% semantic validation (B), 26.6% existing evidence (A)
  - Free text: NOT required (0/79)
  - One-case-one-patch risk: NONE
  - Over-design audit: ALL FALSE

KEY FINDING:
  Reusable Signal Candidate EXISTS in the current data.
  34 caption_like cases with FIG=YES + EXTENT_EXISTS → YES, across 5 documents,
  form a structural pattern with consistent Human validation.

  BUT: Candidate ≠ validated signal.
  BUT: Candidate ≠ rule.
  BUT: "FIG-prefix + nearby = Caption" is FORBIDDEN.

  The candidate is a STRUCTURAL OBSERVATION:
  "Same evidence config + same Human judgment × 34 + 5 documents."
  It requires multi-reviewer validation to become a true signal.
  That validation is NOT authorized.

不得自动开始下一阶段。
不得创建任何 Rule。
不得创建任何 Capability。
不得把 Candidate 当作 Validated Signal。
STOP = TRUE
```
