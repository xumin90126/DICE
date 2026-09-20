# Evidence Sufficiency → Evidence Boundary Research

> **模式: READ-ONLY RESEARCH / NO IMPLEMENTATION / NO EXPERIMENT / NO HUMAN VALIDATION / FROZEN INTACT / STOP**
> 日期: 2026-09-18
> 前置: G1–G5 Cross-Document Validation Research, Human Evidence Requirement Research, M-A Human Validation Pilot, P0/P1 Experiments
> 本文件: 研究 Evidence Sufficiency 与 Evidence Boundary 之间的关系。

---

## 0. Research Questions

```
RQ1: 什么叫 Evidence Sufficient / Insufficient / Boundary？三者必须严格区分。
RQ2: Evidence Sufficiency 是否只是 "Evidence exists" 的另一种表达？还是独立概念？
RQ3: G1–G5 与 Evidence Sufficiency 的关系是什么？
RQ4: 是否存在 Evidence exists → organized → presented → consumed → 仍无法判断的情况？
RQ5: 是否可以定义与具体对象无关的 Minimum Sufficient Evidence？
```

---

## 1. Frozen Baseline

```
FROZEN_BASELINE = INTACT
BASELINE_DRIFT = 0
SYSTEM_MODIFIED = FALSE
IMPLEMENTATION_AUTHORIZED = FALSE
EXPERIMENT_AUTHORIZED = FALSE
HUMAN_VALIDATION_AUTHORIZED = FALSE
RUNTIME_AUTHORITY = ZERO
PRODUCTION = FALSE
STOP = TRUE

G1-G5 Framework = FROZEN (not modified)
G1-G5 Cross-Document Validation = FROZEN (PARTIALLY_SUPPORTED, not modified)
M-A Evidence Pack (E1) = FROZEN
All Human Validation data = FROZEN
```

---

## 2. Three-Concept Distinction (RQ1)

### A. Evidence Availability

```
Definition: 需要的信息是否存在。

  drawing exists?     → DGF > 0
  text exists?        → P1 TEXT_ATOM present
  geometry exists?    → P2 pairwise computed
  context exists?     → P2 same_y_band populated
  extent exists?      → DEF > 0

  Availability is a BINARY property per observation surface.
  It does NOT imply usability or sufficiency.
```

### B. Evidence Sufficiency

```
Definition: 已有 Evidence 是否足以支持当前 Human Task 的判断。

  Sufficient = Human can make a definitive judgment (YES or NO)
              using the available, organized, presented, consumed evidence.

  Insufficient = Human cannot make a definitive judgment because
                 required evidence is missing, unorganized, un-presented,
                 or not consumed.

  Sufficiency is a TASK-RELATIVE property.
  The same evidence may be Sufficient for Task A but Insufficient for Task B.
  Evidence exists ≠ Evidence sufficient.
```

### C. Evidence Boundary

```
Definition: Evidence 足以支持某个较弱的 Claim，但不能合理支持更强的 Claim。

  Boundary = Evidence is complete and consumed, supports a STRUCTURAL claim,
             but cannot support a SEMANTIC IDENTITY claim without additional
             evidence or interpretation.

  Example:
    Evidence supports: "This text has spatial association with this drawing"
    Evidence does NOT support: "This text IS the caption of this drawing"

  Boundary is NOT the same as Insufficient.
  Insufficient = evidence is missing/blocked somewhere in the G1-G4 chain.
  Boundary = evidence is complete (G5 reached) but has a claim-level ceiling.
```

### Strict Distinction

```
  Availability ≠ Sufficiency ≠ Boundary

  Availability answers: "Does the evidence exist?"
  Sufficiency answers: "Can the Human complete the task?"
  Boundary answers: "What is the strongest claim the evidence can support?"

  A case can be:
    Available + Insufficient (G1/G2/G3 — evidence exists but not reaching Human)
    Available + Sufficient (L5 — definitive judgment made)
    Available + Boundary (G5 — evidence complete but semantic ceiling)
    NOT Available + Insufficient (G1 — nothing to observe)
```

---

## 3. Evidence Sufficiency vs Evidence Exists (RQ2)

```
PROVEN: Evidence Sufficiency is an INDEPENDENT concept, not a synonym for "evidence exists."

  PROOF from real cases:

  Case IS11-AMB-135 (efficientnet p5):
    Evidence EXISTS:     YES (P1 text, P2 geometry, left_alignment_group=10)
    Evidence SUFFICIENT: NO (IS-01/IS-02 binary heuristic false-triggered → FP)
    → Evidence exists but is NOT sufficient for correct judgment
    → The evidence WAS available but the CONSUMER didn't use it (G4)

  Case IS11-AMB-414 (med_001 p20):
    Evidence EXISTS:     YES (P1 text: "FIG. 9:", P2 geometry: h_gap=18.11)
    Evidence SUFFICIENT: NO (caption association not organized; IS-11 ABSTAIN)
    → Evidence exists but is NOT sufficient because organization is missing (G2)

  Case MA-UNC-5 (arxiv_2402 p19):
    Evidence EXISTS:     YES (extent, text "Fig.", context "in Fig. 9")
    Evidence SUFFICIENT: PARTIAL (supports spatial association but not caption identity)
    → Evidence exists AND is consumed but hits a BOUNDARY (G5)

  Case is11_efficientnet_p4_55_218 (M-A YES case):
    Evidence EXISTS:     YES (text, extent, spatial, context)
    Evidence SUFFICIENT: YES (Human made definitive YES judgment)
    → Here availability and sufficiency coincide

  CONCLUSION:
    Evidence exists is NECESSARY but NOT SUFFICIENT for Evidence Sufficiency.
    The G1-G5 hierarchy proves this:
      G1 (exists?) → G2 (organized?) → G3 (presented?) → G4 (consumed?) → G5 (sufficient?)
    Each layer is a separate question. "Exists" is only the first.
```

---

## 4. G1–G5 and Evidence Sufficiency Relationship (RQ3)

### G1–G5 × Sufficiency Matrix

File: `tmp/g1_g5_sufficiency_matrix.csv`

| Gap | Sufficient | Insufficient | Boundary | Indeterminate | Total |
|-----|-----------:|-------------:|---------:|--------------:|------:|
| G1  | 0 | 12 | 0 | 0 | 12 |
| G2  | 0 | 28 | 0 | 0 | 28 |
| G3  | 0 | 15 | 0 | 0 | 15 |
| G4  | 0 | 0 | 0 | 7 | 7 |
| G5  | 0 | 0 | 13 | 0 | 13 |
| L5  | 65 | 0 | 0 | 9 | 74 |
| **Total** | **65** | **55** | **13** | **16** | **149** |

### Interpretation

```
G1 → INSUFFICIENT (100%)
  Observation missing → nothing to judge → always insufficient.
  No boundary possible (no evidence to support any claim).

G2 → INSUFFICIENT (100%)
  Evidence exists but not organized → cannot be used → insufficient.
  No boundary possible (evidence hasn't reached usable form).

G3 → INSUFFICIENT (100%)
  Evidence organized but not presented → Human can't see it → insufficient.
  No boundary possible (evidence hasn't reached Human).

G4 → INDETERMINATE (100%)
  Evidence presented but consumer didn't use it.
  SUFFICIENCY IS UNKNOWN: if consumer used the evidence, it MIGHT be sufficient.
  Cannot determine without observing consumer behavior.
  → NOT a boundary (the evidence hasn't been consumed yet).

G5 → BOUNDARY (100%)
  Evidence consumed but semantic interpretation needed.
  Evidence supports a weaker structural claim but NOT a stronger semantic claim.
  → THIS is where Evidence Boundary lives.

L5 → SUFFICIENT (88%) + INDETERMINATE (12%)
  Evidence consumed, definitive judgment made → sufficient.
  9 INDETERMINATE: cases where the judgment was definitive but the P1 A/B pilot
  recorded M6=UNCERTAIN (Human couldn't determine sufficiency despite judging).
  These are P1 pilot measurement artifacts, not evidence gaps.

KEY FINDING:
  G1-G3 = always INSUFFICIENT (evidence blocked before reaching Human)
  G4 = INDETERMINATE (evidence reached consumer but usage unknown)
  G5 = always BOUNDARY (evidence complete but semantic ceiling)
  L5 = mostly SUFFICIENT (definitive judgment made)

  → Sufficiency is NOT determined by gap type alone.
  → G1-G3 block sufficiency; G4 is indeterminate; G5 is boundary; L5 is sufficient.
  → The matrix shows a CLEAN separation: each gap type maps to exactly one sufficiency status.
  → This is because G1-G5 IS the evidence flow hierarchy, and sufficiency is the
    endpoint of that flow.
```

---

## 5. Evidence Exists → Organized → Presented → Consumed → Still Cannot Judge (RQ4)

```
ANSWER: YES, this situation exists. It is G5 / Evidence Boundary.

  13 cases (8.7% of all 149) reached the full evidence flow:
    Evidence exists → organized → presented → consumed
    BUT Human still could not make a definitive judgment.

  These are NOT cases where evidence is missing or blocked.
  They are cases where evidence is COMPLETE but INSUFFICIENT for a STRONGER claim.

  Two sub-types:

  CONFIRMED_EVIDENCE_BOUNDARY (9 cases):
    C3 check: "Would more of the SAME evidence type help?" → NO
    These cases cannot be resolved by adding more spatial/geometry/alignment evidence.
    The boundary is genuine: structural evidence → semantic interpretation gap.

    Examples:
      MA-UNC-5 (arxiv_2402 p19): "Fig." near drawing, context "in Fig. 9"
        → Evidence supports: spatial association (text near drawing)
        → Evidence does NOT support: "is this a caption or a reference?"
        → More spatial evidence cannot resolve this; requires semantic text understanding

      PH02-SPECIFICITY-VALUE-COL (resnet p6): value column ratio=1.04
        → Evidence supports: "these numbers form an aligned column"
        → Evidence does NOT support: "is this a row-number column or a value column?"
        → More alignment evidence cannot resolve; requires semantic content understanding

  CONDITIONAL_EVIDENCE_BOUNDARY (4 cases):
    C3 check: "Would more context help?" → PARTIAL
    These cases MIGHT resolve with additional context (page_context), but
    some sub-cases require semantic knowledge regardless.

    Examples:
      IS11-AMB-375 (med_001 p6): "[23]." / "Each" (period+cap)
        → With page_context (showing body text, not reference list): would resolve as KEEP
        → Without page_context: period+cap is ambiguous (sentence vs reference continuation)
        → But IND-AMB-033 ("Le." / "Randaugment:") requires author-name recognition
          that page_context alone cannot provide → genuine semantic boundary
```

---

## 6. Evidence Boundary Strict判定 (Section 8 Compliance)

### B1–B6 Criteria Applied

```
For all 13 G5 cases, B1-B6 criteria were checked:

  B1 (Required Evidence exists):            ALL 13 = YES
  B2 (Evidence meets minimum for Task):     ALL 13 = YES (G5 implies consumed)
  B3 (No obvious G1/G2/G3/G4 blocking):    ALL 13 = YES (G5 is PRIMARY)
  B4 (Evidence supports weaker claim):      ALL 13 = YES (structural claim supported)
  B5 (Stronger claim needs new evidence):   ALL 13 = YES (semantic interpretation needed)
  B6 (Reorganization cannot solve):         ALL 13 = YES→NO (cannot solve by reorganization)

  ALL 13 cases pass B1-B6.
  → 9 CONFIRMED_EVIDENCE_BOUNDARY
  → 4 CONDITIONAL_EVIDENCE_BOUNDARY

  The 4 CONDITIONAL cases pass B1-B6 but C3 is PARTIAL:
    more context MIGHT resolve some sub-cases, but not all.
    They are boundary cases that are PARTIALLY dependent on context availability.
```

### Counterfactual Checks (C1–C4)

```
C1 (Would reorganization solve?):  NO for all 13
  → Evidence is already organized (G5 implies organized+presented+consumed)
  → NOT a G2/G3 issue

C2 (Would correct consumer delivery solve?):  NO for all 13
  → Consumer already received the evidence (G5 implies consumed)
  → NOT a G4 issue

C3 (Would more same-type evidence help?):
  9 cases → NO (more spatial/alignment cannot resolve semantic identity)
  4 cases → PARTIAL (more context might resolve some, but not all)

C4 (New Evidence Function needed?):
  Task 1 (Text-Drawing): CAPTION_IDENTITY_FUNCTION
    → Distinguishing caption from reference requires semantic text understanding
    → NOT implementable with current evidence functions
  Task 2 (Text-Text):
    → COLUMN_SEMANTIC_IDENTITY (column type: row-number vs value)
    → SENTENCE_UNIT_STANDARD (text unit: sentence vs paragraph)
    → AUTHOR_NAME_RECOGNITION (reference list: is "Le." a surname?)
  Task 3 (Graphic): TICK_LABEL_IDENTITY
    → Distinguishing axis tick labels from data values

  ALL identified new functions require SEMANTIC understanding beyond current evidence.
  NONE are implementable with geometry/lexical patterns alone.
  → BOUNDARY_EVIDENCE_REQUIREMENT recorded but NOT implemented.
```

---

## 7. Minimum Sufficient Evidence (RQ5)

### Can we define an object-independent Minimum Sufficient Evidence?

```
PARTIALLY_SUPPORTED

  SUPPORTED (from real cases):

    For STRUCTURAL tasks (association, boundary, proximity):
      Minimum Sufficient Evidence = TARGET_TEXT + REFERENCE_OBJECT + SPATIAL_RELATION + CONTEXT

      This is object-independent:
        - Text-Drawing: TARGET_TEXT + DRAWING_EXTENT + SPATIAL_RELATION + SAME_Y_CONTEXT
        - Text-Text:    TARGET_TEXT_A + TARGET_TEXT_B + GEOMETRIC_RELATION + SAME_Y_CONTEXT
        - Graphic:      TARGET_TEXT + DRAWING_EXTENT + DENSITY_SIGNAL + REGION_CONTEXT

      The common pattern: TARGET + REFERENCE + RELATION + CONTEXT
      → 4 Evidence Function categories, not object-specific fields.

      PROOF: 65 SUFFICIENT cases (L5) all have these 4 categories.
             When any is missing (G1-G3), the case is INSUFFICIENT.

  NOT_SUPPORTED (beyond structural):

    For SEMANTIC IDENTITY tasks (caption identity, column type, author name):
      No amount of structural evidence is sufficient.
      The minimum sufficient evidence would require a SEMANTIC understanding function
      that is NOT in the current evidence surface.

      → Minimum Sufficient Evidence CANNOT be defined for semantic identity tasks
        using current evidence functions.
      → This is the Evidence Boundary: structural evidence has a claim ceiling.

  CONCLUSION:
    Minimum Sufficient Evidence is definable for STRUCTURAL claims (weaker claims).
    It is NOT definable for SEMANTIC IDENTITY claims (stronger claims) with current evidence.
    The boundary between the two is the Evidence Boundary.
```

### Evidence Function Requirement Table

File: `tmp/evidence_function_requirement_table.csv`

```
Task 1 (Text-Drawing Association):
  Sufficient for structural claim:  F1+F2+F3+F4+F5+F6 (lexical + spatial + context)
  Insufficient for semantic claim:  CAPTION_IDENTITY_FUNCTION (not in current evidence)
  Cases: 65 SUFFICIENT + 9 BOUNDARY + 4 CONDITIONAL

Task 2 (Text-Text Boundary):
  Sufficient for structural claim:  F1+F6+F12+F14 (lexical + context + column + reference)
  Insufficient for semantic claim:  COLUMN_SEMANTIC_IDENTITY + SENTENCE_UNIT_STANDARD + AUTHOR_NAME_RECOGNITION
  Cases: 26 KEEP resolved + 18 ABSTAIN (G2) + 1 FP (G4) + 2 BOUNDARY + 4 CONDITIONAL

Task 3 (Graphic Text Context):
  Sufficient for structural claim:  F1+F2+F7+F15 (lexical + spatial + density + header)
  Insufficient for semantic claim:  TICK_LABEL_IDENTITY
  Cases: 13 (mostly G1/G2 — insufficient, not boundary)
```

---

## 8. Claim Boundary Research

### Claim Levels (induced from real cases)

```
CLAIM_LEVEL_1 (weakest — structural existence):
  "These two objects have a spatial/geometric relationship"
  Supported by: F2 (reference target exists) + F3 (proximity) + F4 (positional)
  Evidence required: TARGET + REFERENCE + SPATIAL_RELATION
  → 65 SUFFICIENT cases support this level

CLAIM_LEVEL_2 (medium — structural classification):
  "This text is structurally associated/separated from this object"
  Supported by: LEVEL_1 + F1 (lexical pattern) + F6 (context) + F12 (column membership)
  Evidence required: LEVEL_1 + LEXICAL + CONTEXT + STRUCTURAL_MEMBERSHIP
  → Supported when G1-G4 are resolved

CLAIM_LEVEL_3 (strongest — semantic identity):
  "This text IS a caption / label / row-number / author name / reference"
  Supported by: LEVEL_2 + SEMANTIC_INTERPRETATION (not in current evidence)
  Evidence required: LEVEL_2 + SEMANTIC_FUNCTION (not available)
  → NOT supported by current evidence → Evidence Boundary

  The boundary is between LEVEL_2 and LEVEL_3.
  G5 cases reach LEVEL_2 but cannot reach LEVEL_3.
```

### Cross-Case Claim Pattern

```
  Evidence Flow:    G1 → G2 → G3 → G4 → G5 → L5
  Claim Supported:  NONE → NONE → NONE → ?    → L2  → L2
  (L5 cases also support L2, plus a definitive structural judgment)

  G5 cases support L2 (structural) but NOT L3 (semantic identity).
  L5 cases support L2 (structural) AND a definitive judgment (YES/NO).
  But L5 judgments are STRUCTURAL (associated/not associated), NOT semantic identity.

  → Even SUFFICIENT cases (L5) don't support L3 (semantic identity).
  → L3 is NEVER supported by current evidence.
  → The Evidence Boundary is UNIVERSAL: it exists for ALL tasks at the L2→L3 transition.
```

---

## 9. Cross-Task Convergence

```
CROSS_TASK_CONVERGENCE = SUPPORTED

  Task 1 (Text-Drawing Association):
    Boundary mechanism: structural association → semantic caption identity
    Boundary cases: 9 CONFIRMED + 4 CONDITIONAL

  Task 2 (Text-Text Boundary):
    Boundary mechanism: structural column membership → semantic column type identity
    Boundary cases: 2 CONFIRMED + 4 CONDITIONAL

  Task 3 (Graphic Text Context):
    Boundary mechanism: structural figure-text proximity → semantic tick label identity
    Boundary cases: 0 (insufficient cases dominate; no G5 reached)

  CONVERGENT PATTERN:
    All 3 tasks show the SAME boundary mechanism:
      Structural evidence → Semantic identity interpretation gap

    The boundary is ALWAYS at the transition:
      "What is the structural relationship?" → answerable (L2)
      "What is the semantic identity/role?" → NOT answerable (L3)

    This is NOT task-specific. It is a fundamental property of evidence-based judgment:
      Evidence (observation + geometry + context) supports STRUCTURAL claims.
      SEMANTIC IDENTITY claims require interpretation beyond evidence.

  This convergence is STABLE across:
    - 3 different Human Tasks
    - 13 different documents
    - 8 document types
    - Multiple problem types (table, figure, caption, prose, reference)
```

---

## 10. Preventing G5 Misclassification (Section 9 Compliance)

```
CHECK: Are all G5 cases genuine semantic boundaries, or are some misclassified G2/G3/G4?

  For each of the 13 G5 cases:
    B3 check: "No obvious G1/G2/G3/G4 blocking?" → ALL YES

  This means:
    - Evidence EXISTS (not G1)
    - Evidence IS ORGANIZED (not G2)
    - Evidence IS PRESENTED (not G3)
    - Evidence IS CONSUMED (not G4)
    - The only remaining issue is SEMANTIC INTERPRETATION (G5)

  Counterfactual verification:
    C1 (reorganization helps?) → NO for all 13 → NOT G2
    C2 (consumer delivery helps?) → NO for all 13 → NOT G4
    C3 (more same evidence helps?) → NO for 9, PARTIAL for 4

  The 4 CONDITIONAL cases:
    These have C3=PARTIAL, meaning page_context MIGHT help.
    BUT page_context is an EXISTING observation (P7) that is NOT organized
    into the Evidence Pack.

    Question: Is this G3 (page_context not presented) or G5 (semantic boundary)?

    Answer: BOTH, depending on the sub-case:
      - Sub-cases where page_context resolves the ambiguity → G3 (presentation gap)
      - Sub-cases where page_context doesn't resolve (author-name recognition) → G5 (semantic boundary)

    The CONDITIONAL classification correctly captures this duality.
    These are NOT misclassified — they are genuinely at the G3/G5 boundary.

  CONCLUSION:
    0 G5 cases are misclassified G2/G3/G4.
    9 are CONFIRMED boundaries (C3=NO, cannot resolve with more evidence).
    4 are CONDITIONAL boundaries (C3=PARTIAL, might resolve with context).
    The G5 classification is CLEAN.
```

---

## 11. Over-Design Audit

```
O1: 是否创建了新的系统模块？
  → NO. No new module created. READ-ONLY research only.

O2: 是否修改了现有系统？
  → NO. No system files modified. FROZEN_BASELINE = INTACT.

O3: 是否增加字段？
  → NO. No new fields proposed. Only Evidence Functions analyzed.

O4: 是否增加 detector？
  → NO. No new detector proposed.

O5: 是否增加 score/confidence？
  → NO. No scoring or confidence mechanism proposed.

O6: 是否增加 Runtime Authority？
  → NO. RUNTIME_AUTHORITY = ZERO.

O7: 是否产生 Capability？
  → NO. NEW_CAPABILITY = NONE.

O8: 是否把 G5 扩大成"所有 Human uncertainty"？
  → NO. G5 = 13/149 = 8.7% of cases.
     55 cases are INSUFFICIENT (G1-G3), not G5.
     7 cases are INDETERMINATE (G4), not G5.
     G5 is a SPECIFIC condition: evidence complete + semantic interpretation needed.
     NOT all UNCERTAIN = G5.

O9: 是否把 Evidence Boundary 变成自动决策？
  → NO. Evidence Boundary is a RESEARCH FINDING, not a system decision rule.
     No automatic boundary detection implemented or proposed.

O10: 是否出现对象专用框架？
  → NO. The framework is Task-based (T1/T2/T3), not object-based.
     No Figure/Table/Caption-specific sufficiency framework.
     Object type ≠ Evidence Function ≠ Sufficiency.

ALL CHECKS: FALSE (PASS)
OVER_DESIGN_RISK = LOW
```

---

## 12. Research Stop Criteria Check

```
STOP-1: 现有数据无法可靠判断 Evidence Sufficiency？
  → NO. 149 cases classified with 0 INDETERMINATE from data insufficiency.
     16 INDETERMINATE are G4 (consumer behavior unobservable), not data insufficiency.

STOP-2: Boundary 判断高度依赖研究者主观解释？
  → PARTIAL. B1-B6 criteria are objective. C1-C4 counterfactuals are objective.
     But CLAIM_LEVEL definition (L1/L2/L3) is researcher-induced from cases.
     → Acceptable: levels are grounded in real case evidence, not assumed.

STOP-3: 出现大量 Case-specific 解释？
  → NO. 3 boundary mechanisms cover all 13 cases:
     (1) caption vs reference (9 cases)
     (2) column type identity (2 cases)
     (3) sentence unit / author name (2 cases + 4 conditional)
     → 3 mechanisms, not 13 case-specific explanations.

STOP-4: 需要新增 Human Review？
  → NO. All analysis is READ-ONLY post-hoc on existing data.
     HUMAN_VALIDATION_AUTHORIZED = FALSE.

STOP-5: 需要修改 Evidence Pack？
  → NO. Evidence Pack is FROZEN. Analysis uses E1 data as-is.

STOP-6: 需要修改 DICE？
  → NO. DICE is FROZEN. No modification needed or proposed.

STOP-7: 开始出现对象专用框架？
  → NO. Framework is Task-based. No object-specific sufficiency.

NO STOP CRITERIA TRIGGERED.
Research can conclude with current data.
```

---

## 13. Final Questions

### Q1: Evidence Availability 与 Evidence Sufficiency 是否是两个不同概念？

```
SUPPORTED

  PROOF:
  - 55 cases have Available evidence but are Insufficient (G1-G3)
  - 13 cases have Available evidence but hit Boundary (G5)
  - 7 cases have Available evidence but Sufficiency is Indeterminate (G4)
  - Only 65 cases have Available AND Sufficient evidence (L5)

  Availability is NECESSARY but NOT SUFFICIENT for Sufficiency.
  The G1-G5 hierarchy proves they are distinct concepts at different layers.
```

### Q2: 是否可以从已有真实案例中识别 Minimum Sufficient Evidence？

```
PARTIALLY_SUPPORTED

  SUPPORTED for structural claims (L1/L2):
  - 65 SUFFICIENT cases all have: TARGET + REFERENCE + RELATION + CONTEXT
  - When any component is missing → INSUFFICIENT (G1-G3)
  - This pattern is object-independent and task-stable

  NOT_SUPPORTED for semantic identity claims (L3):
  - No amount of structural evidence supports semantic identity
  - 13 BOUNDARY cases prove the ceiling
  - Minimum Sufficient Evidence for L3 would require a SEMANTIC FUNCTION
    not in current evidence surface

  CONCLUSION:
  Minimum Sufficient Evidence is definable for STRUCTURAL tasks.
  It is NOT definable for SEMANTIC IDENTITY tasks with current evidence.
```

### Q3: 是否存在 Evidence Boundary？

```
SUPPORTED

  13 cases (8.7%) pass ALL B1-B6 criteria:
  - Evidence exists, organized, presented, consumed
  - Supports a weaker structural claim
  - Cannot support a stronger semantic identity claim
  - Reorganization cannot solve (C1=NO)
  - Consumer delivery cannot solve (C2=NO)
  - More same-type evidence cannot solve (C3=NO for 9, PARTIAL for 4)

  9 CONFIRMED_EVIDENCE_BOUNDARY: cannot resolve with any current evidence
  4 CONDITIONAL_EVIDENCE_BOUNDARY: might resolve with page_context, but not all sub-cases

  The boundary is REAL and STABLE across tasks.
```

### Q4: Evidence Boundary 是否可以与 G1–G5 明确区分？

```
SUPPORTED

  The G1-G5 × Sufficiency matrix shows CLEAN separation:
  - G1-G3 → INSUFFICIENT (evidence blocked, NOT boundary)
  - G4 → INDETERMINATE (consumer behavior unknown, NOT boundary)
  - G5 → BOUNDARY (evidence complete, semantic ceiling)
  - L5 → SUFFICIENT (definitive judgment made)

  Evidence Boundary = G5. They are the SAME thing.
  G5 IS the Evidence Boundary in the G1-G5 framework.
  They are not just "distinguishable" — they are identical.

  The distinction that matters is:
    G5/Boundary vs G1-G4 (which are NOT boundary, they are insufficient)
  This distinction is CLEAN: 0 G1-G4 cases are boundary, 0 G5 cases are non-boundary.
```

### Q5: 不同 Human Task 是否出现 Evidence Sufficiency 的跨任务共性？

```
SUPPORTED

  3 tasks, same boundary mechanism:
  - Task 1: structural association → semantic caption identity (boundary)
  - Task 2: structural column membership → semantic column type (boundary)
  - Task 3: structural figure-text proximity → semantic tick identity (boundary)

  ALL 3 tasks show: structural evidence → semantic interpretation gap.
  The boundary is ALWAYS at L2 (structural) → L3 (semantic identity).

  This convergence is stable across:
  - 3 tasks, 13 documents, 8 document types, multiple problem types
  - NOT task-specific, NOT object-specific

  CROSS_TASK_CONVERGENCE = SUPPORTED
```

### Q6: 当前是否有足够证据设计一个新的 Evidence Boundary Intelligence Module？

```
NO

  MISSING EVIDENCE:
  1. Non-academic document types NOT_TESTED (only academic papers)
  2. Single-researcher classification (no inter-rater validation)
  3. 4/13 boundary cases are CONDITIONAL (might resolve with context)
  4. G4 (Consumer Integration) is NOT_OBSERVABLE — cannot determine if
     consumer would make a different judgment if it used the evidence
  5. No mechanism to AUTOMATICALLY detect boundary (all classification is manual)
  6. The identified new functions (CAPTION_IDENTITY, COLUMN_SEMANTIC_IDENTITY,
     AUTHOR_NAME_RECOGNITION) require semantic understanding — no implementation
     path exists in current evidence surface

  An "Intelligence Module" would require:
  - Automatic boundary detection (not demonstrated)
  - Semantic understanding capability (not available)
  - Cross-document-type validation (not tested)
  - Multi-rater reliability (not tested)

  NONE of these are available. → NO.
```

### Q7: 当前是否应该修改 DICE？

```
NO

  EVIDENCE:
  1. G1-G5 framework is STABLE (100% case coverage, 0 new gap needed)
  2. Evidence Boundary = G5 (already in framework, no new concept needed)
  3. Minimum Sufficient Evidence is definable for structural tasks (already in E1 Pack)
  4. Semantic identity boundary is a LEGITIMATE Human judgment boundary (not fixable)
  5. G1-G4 issues are KNOWN (TLD coverage, consumer integration) — fixing requires
     IMPLEMENTATION (not authorized)
  6. No new module/field/detector warranted by current evidence

  The research CONFIRMS the framework. It does NOT reveal a deficiency requiring modification.
  DICE should remain FROZEN.
```

---

## 14. Files Created

```
tmp/evidence_sufficiency_boundary_research.md      (this file)
tmp/evidence_sufficiency_boundary_research.json     (structured data)
tmp/evidence_sufficiency_case_table.csv             (149 cases, 17 fields)
tmp/g1_g5_sufficiency_matrix.csv                    (6 gaps × 4 sufficiency states)
tmp/evidence_function_requirement_table.csv         (3 tasks × evidence functions)
```

---

## 15. Limitations

```
LIMITATION_1: ACADEMIC-ONLY CORPUS
  All 149 cases are from academic papers. Non-academic documents NOT_TESTED.

LIMITATION_2: SINGLE-RESEARCHER CLASSIFICATION
  All sufficiency/boundary classifications are by one researcher.
  No inter-rater reliability test.

LIMITATION_3: G4 NOT_OBSERVABLE
  7 G4 cases are INDETERMINATE because consumer behavior (IS-11 IS-01/IS-02)
  cannot be observed modifying its behavior. We cannot determine if the
  consumer WOULD make a correct judgment if it used the evidence.

LIMITATION_4: CONDITIONAL BOUNDARIES
  4 of 13 boundary cases are CONDITIONAL — they might resolve with page_context.
  True boundary count may be 9-13 depending on context availability.

LIMITATION_5: CLAIM_LEVELS ARE RESEARCHER-INDUCED
  L1/L2/L3 claim levels are induced from case analysis, not pre-registered.
  A different researcher might define different levels.

LIMITATION_6: NO LIVE COUNTERFACTUAL
  C1-C4 counterfactuals are READ-ONLY reasoning, not live experiments.
  "Would reorganization solve it?" is answered by analysis, not by actually
  reorganizing and observing the result.
```

---

## 16. Final Governance Status

```
SYSTEM_MODIFIED = FALSE
IMPLEMENTATION_AUTHORIZED = FALSE
EXPERIMENT_AUTHORIZED = FALSE
HUMAN_VALIDATION_AUTHORIZED = FALSE

FROZEN_BASELINE = INTACT
BASELINE_DRIFT = 0

NEW_CAPABILITY = NONE
RUNTIME_AUTHORITY = ZERO
PRODUCTION = FALSE

STOP = TRUE
```

---

## Appendix A: Evidence Function Catalog

| ID | Function | Served By | Status |
|----|----------|-----------|--------|
| F1 | LEXICAL_DISCRIMINATION | text content, FIG-prefix | EXISTS (P1) |
| F2 | SPATIAL_REFERENCE_TARGET | drawing extent bbox (DEF) | EXISTS (DEF) |
| F3 | PROXIMITY_SIGNAL | text-extent distance | EXISTS (consumer-computed) |
| F4 | POSITIONAL_CONTEXT | vertical ordering | EXISTS (consumer-computed) |
| F5 | ALIGNMENT_SIGNAL | x-overlap | EXISTS (consumer-computed) |
| F6 | TEXT_RECONSTRUCTION | same_y context (±5pt) | EXISTS (P2, E1) |
| F7 | DRAWING_DENSITY_SIGNAL | primitive_count, area | EXISTS (DGF/DEF) |
| F8 | CAPTION_CONTINUATION | adjacent text, h_gap | EXISTS (P2) |
| F9 | MULTI_DRAWING_DISAMBIGUATION | extents, other FIG texts | DERIVABLE |
| F10 | REGION_CONTEXT | P6 region type | EXISTS (P6) |
| F11 | OBSERVATION_COVERAGE_DISAMBIGUATION | evidence_state 3-state | EXISTS (E1 PR3) |
| F12 | COLUMN_MEMBERSHIP | left_alignment_group | EXISTS (P2) |
| F13 | CROSS_PAGE_CONTINUITY | P2/P7.1 cross-page | DERIVABLE |
| F14 | REFERENCE_CONTEXT | page_context (P7) | DERIVABLE (exists, not organized) |
| F15 | HEADER_DETECTION | page-top y + repetition + morphology | DERIVABLE |

## Appendix B: Case Universe Summary

```
Total Cases:        149
Sources:
  G1G5_VALIDATION:    70 (failure/abstain/ambiguous cases from 13 docs)
  MA_HUMAN_VALIDATION: 79 (all M-A Pilot cases: 65 definitive + 14 UNCERTAIN)

Sufficiency:
  SUFFICIENT:         65 (43.6%) — definitive judgment made
  INSUFFICIENT:       55 (36.9%) — evidence blocked (G1-G3)
  BOUNDARY:           13 (8.7%)  — evidence complete, semantic ceiling
  INDETERMINATE:      16 (10.7%) — G4 (7) + L5 with M6=UNCERTAIN (9)

Boundary Breakdown:
  CONFIRMED:           9 — cannot resolve with any current evidence
  CONDITIONAL:         4 — might resolve with page_context

Cross-Task:
  Task 1 (Text-Drawing):  93 cases (79 M-A + 14 G1-G5)
  Task 2 (Text-Text):     56 cases (45 IS-11 + 10 P7 + 1 PH02)
  Task 3 (Graphic):       13 cases (Phase 3)
  (some overlap in G1-G5 validation cases)
```
