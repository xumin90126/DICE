# Boundary Handoff Learning Design Research

> **模式: READ-ONLY / DESIGN RESEARCH ONLY / NO CODE / NO IMPLEMENTATION / NO HUMAN VALIDATION / STOP**
> 日期: 2026-09-19
> Gate: BOUNDARY_HANDOFF_LEARNING_DESIGN_RESEARCH
> 前置: Evidence Boundary Expansion Research (COMPLETE, 18 E4 G5 confirmed)
> 本文件: 研究 Human 到达 G5 Boundary 后需要什么 Evidence；这种需求能否形成可复用的 Boundary Handoff Pattern。

---

## 0. Core Question

```
Human 到达 G5 Evidence Boundary 后，
为完成最后判断究竟需要什么 Evidence？
这种 Evidence Requirement 能否被安全地压缩、复用，
并用于未来的 Human Handoff？

DICE 不学习 Human 的答案。
DICE 研究 Human 在 Evidence Boundary 上需要什么 Evidence。

最终目标：
Human 只负责不可自动化的最后语义判断，
而 DICE 负责把 Human 做这个判断所需要的 Evidence 尽可能提前准备好。
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
18 E4 genuine G5 cases (from Evidence Boundary Expansion Research)
  - 5 T1 caption_vs_reference (MA-UNC-2/5/6/7/11)
  - 3 T1 ambiguous_fragment caption_vs_reference (M-A UNCERTAIN)
  - 2 CE2 pair (caption_vs_reference, decisive proof)
  - 4 T1 Type_B_negative text_role (M-A UNCERTAIN)
  - 2 T2 author_name (IND-AMB-033/049)
  - 2 T2 column_type (PH02-SPECIFICITY-VALUE-COL/CS001)

13 G5 boundary structure cases (from Evidence Boundary Structure Research)
M-A 79-case Human Validation data
Prior Human-Evidence Binding research findings
```

---

## 3. Human Evidence Requirement Analysis (R1–R6)

### 3.1 Classification Framework

```
R1 = Existing Evidence (already provided in Pack)
R2 = Existing-but-not-packaged Evidence (system has, Pack doesn't)
R3 = Derivable Evidence (can be reorganized from existing)
R4 = External/Document Context (needs larger document context)
R5 = Semantic Knowledge (needs Human's semantic understanding)
R6 = Unresolvable (even with all evidence, Human must make semantic judgment)
```

### 3.2 Results (18 E4 cases)

| Requirement | Count | % |
|-------------|------:|---:|
| R1 (existing provided) | 18 | 100% |
| R2 (existing not packaged) | 2 partial | 11.1% |
| R3 (derivable) | 2 partial | 11.1% |
| R4 (document context) | 2 YES + 16 PARTIAL | 100% |
| **R5 (semantic knowledge)** | **18** | **100%** |
| **R6 (unresolvable)** | **18** | **100%** |

```
KEY FINDING:
  ALL 18 E4 cases require R5 (Semantic Knowledge) — 100%.
  ALL 18 E4 cases are R6 (Unresolvable by structural evidence) — 100%.

  This means:
  → Every genuine G5 boundary requires Human semantic judgment.
  → No amount of structural evidence can resolve these boundaries.
  → The Human's requirement is NOT "more evidence" but "semantic understanding."

  R1 = YES for all 18:
  → Structural evidence IS already provided (FIG + EXTENT + spatial + context).
  → The Pack is not missing structural evidence.
  → The boundary is not about evidence QUANTITY but evidence TYPE.

  R4 = PARTIAL for 16, YES for 2:
  → Document context (page section, surrounding text) MAY help in some cases.
  → But even with context, semantic judgment is still needed (R5=YES).
  → Context reduces burden but doesn't eliminate the boundary.

  R5 = YES for all 18:
  → Human MUST use semantic understanding to cross the boundary.
  → This is the irreducible Human contribution.
  → DICE cannot provide "semantic understanding" as evidence.

  R6 = YES for all 18:
  → Even with ALL available evidence + context, the boundary persists.
  → The judgment requires Human semantic interpretation.
  → This is the G5 boundary by definition.
```

---

## 4. Boundary Type Classification

| Boundary Type | Count | Documents | Requirement Dimensions |
|--------------|------:|----------:|----------------------|
| CAPTION_VS_REFERENCE | 10 | 3 | LOCAL_CONTEXT + SEMANTIC_UNDERSTANDING |
| TEXT_ROLE_AMBIGUITY | 4 | 3 | LOCAL_CONTEXT + SPATIAL_RELATION + SEMANTIC_UNDERSTANDING |
| AUTHOR_NAME_RECOGNITION | 2 | 1 | ENTITY_CONTEXT + SEMANTIC_UNDERSTANDING |
| COLUMN_SEMANTIC_TYPE | 2 | 2 | ENTITY_CONTEXT + SEMANTIC_UNDERSTANDING |

```
4 boundary types identified across 18 cases.

  CAPTION_VS_REFERENCE (10 cases, 3 docs):
    Text near drawing could be a caption (describing) or in-text reference (citing).
    Structural evidence (FIG + proximity + alignment) is identical for both.
    Human needs: semantic understanding of what the text says/does.

  TEXT_ROLE_AMBIGUITY (4 cases, 3 docs):
    Short text near drawing (e.g., "scaling", "omit", "max", ", with").
    Could be axis label, annotation, or body text fragment.
    Human needs: semantic understanding of the text's function.

  AUTHOR_NAME_RECOGNITION (2 cases, 1 doc):
    "Le." could be surname (reference continuation) or sentence fragment.
    Period+capital pattern is identical for both.
    Human needs: world knowledge about names.

  COLUMN_SEMANTIC_TYPE (2 cases, 2 docs):
    Numeric column could be row-numbers (1,2,3...) or data values.
    Column alignment is identical for both.
    Human needs: semantic understanding of what numbers represent.
```

---

## 5. CE2 Special Check (Q4)

### 5.1 The Question

```
CE2 pair:
  is11_efficientnet_p8_467_415 → judgment NO
  is11_resnet_p6_478_168 → judgment YES

  Structural Evidence: IDENTICAL (FIG=True, EXTENT_EXISTS, VR=below, XO=True, dist~25, ctx=5)
  Human Judgment: DIFFERENT (NO vs YES)

Question: Are their Human Evidence Requirements also different?
```

### 5.2 The Answer

```
Evidence Requirement: SAME

  CE2-NO:
    Requirement type: R5_SEMANTIC_KNOWLEDGE
    Dimensions: LOCAL_CONTEXT + SEMANTIC_UNDERSTANDING
    R5: YES (semantic text understanding)
    R6: YES (unresolvable by evidence)

  CE2-YES:
    Requirement type: R5_SEMANTIC_KNOWLEDGE
    Dimensions: LOCAL_CONTEXT + SEMANTIC_UNDERSTANDING
    R5: YES (semantic text understanding)
    R6: YES (unresolvable by evidence)

  → Evidence is identical
  → Judgment is different
  → Requirement is SAME

INTERPRETATION:
  The Handoff Pattern is VALID.
  Same boundary type (CAPTION_VS_REFERENCE) → same Evidence Requirement.

  The DIFFERENCE in judgment comes from the semantic content of the text itself:
  - CE2-NO: the text's semantic content indicates it's NOT a caption
  - CE2-YES: the text's semantic content indicates it IS a caption

  But the REQUIREMENT (what Human needs to make this determination) is the same:
  → Both need LOCAL_CONTEXT + SEMANTIC_UNDERSTANDING
  → Both need to understand what the text means

  This means:
  → DICE cannot predict the judgment from structural evidence (CE2 proves this).
  → BUT DICE CAN predict what Evidence the Human will need (same for both cases).
  → The Handoff Pattern describes the REQUIREMENT, not the ANSWER.
  → This is the key distinction: Requirement ≠ Answer.

  IMPLICATION FOR HANDOFF:
  If a future case has the same boundary type (CAPTION_VS_REFERENCE),
  DICE can prepare the same Evidence Package (local context + semantic cue)
  regardless of what the final judgment will be.
  The Human then makes the semantic judgment using the prepared evidence.
  → This is Boundary Handoff: prepare evidence, not provide answers.
```

---

## 6. Boundary Handoff Pattern Candidates

### 6.1 Pattern Matrix

| Pattern | Boundary Type | Evidence Requirement | Cases | Docs | Reusable | Status |
|---------|--------------|---------------------|------:|-----:|:--------:|--------|
| P1 | CAPTION_VS_REFERENCE | LOCAL_CONTEXT + SEMANTIC_UNDERSTANDING | 10 | 3 | REUSABLE | B2 |
| P2 | TEXT_ROLE_AMBIGUITY | LOCAL_CONTEXT + SPATIAL_RELATION + SEMANTIC_UNDERSTANDING | 4 | 3 | REUSABLE | B2 |
| P3 | AUTHOR_NAME_RECOGNITION | ENTITY_CONTEXT + SEMANTIC_UNDERSTANDING | 2 | 1 | CONDITIONAL | B2 |
| P4 | COLUMN_SEMANTIC_TYPE | ENTITY_CONTEXT + SEMANTIC_UNDERSTANDING | 2 | 2 | REUSABLE | B2 |

### 6.2 Pattern Details

```
P1: CAPTION_VS_REFERENCE (REUSABLE)
  Cases: 10 (MA-UNC-2/5/6/7/11 + 3 M-A ambiguous + 2 CE2)
  Documents: 3 (arxiv_2402.18619, is11_resnet, is11_efficientnet)
  C1 (≥2 cases): YES (10)
  C2 (cross-document): YES (3 docs)
  C3 (not same text): YES (different texts, different drawings)
  C4 (similar requirement): YES (all need LOCAL_CONTEXT + SEMANTIC_UNDERSTANDING)
  C5 (no semantic label needed): YES (requirement is about evidence type, not answer)
  C6 (doesn't give answer): YES (requirement ≠ answer)
  C7 (boundary → requirement): YES (caption_vs_reference → local_context + semantic)
  → ALL C1-C7 MET → REUSABLE

  Evidence Requirement:
  - Local text context (already provided as ctx=5)
  - Semantic understanding of text content (Human's irreducible contribution)
  - DICE can ensure: local context is complete, text is readable, drawing is visible
  - DICE cannot provide: the semantic interpretation itself

  Boundary Level: B2
  → DICE can provide the context Human needs
  → Human still must make semantic judgment
  → But DICE can ensure the context is COMPLETE (not missing)

P2: TEXT_ROLE_AMBIGUITY (REUSABLE)
  Cases: 4 (Type_B_negative: "scaling", "omit", "max", ", with")
  Documents: 3 (arxiv_2402.18619, is11_efficientnet, is11_med_001)
  C1-C7: ALL MET → REUSABLE

  Evidence Requirement:
  - Local text context (surrounding text)
  - Spatial relation to drawing (already provided)
  - Semantic understanding of text's function (Human's contribution)
  - DICE can ensure: surrounding text context is wider (currently ctx=5)
  - DICE cannot provide: the semantic role determination

  Boundary Level: B2
  → DICE can provide wider context
  → Human still must determine semantic role

P3: AUTHOR_NAME_RECOGNITION (CONDITIONAL)
  Cases: 2 (IND-AMB-033/049)
  Documents: 1 (ind_arxiv_bio2) — NOT cross-document
  C1: YES (2), C2: NO (1 doc), C4: YES
  → CONDITIONAL (needs more cases from different documents)

  Evidence Requirement:
  - Page context (body text vs reference list) — R2/R3 (exists, not packaged)
  - Entity context (is this a person's name?) — R5 (world knowledge)
  - DICE can provide: page section context (if reorganized)
  - DICE cannot provide: world knowledge about names

  Boundary Level: B2 (with page context) / B2 (without)
  → Page context reduces burden but doesn't eliminate need for world knowledge

P4: COLUMN_SEMANTIC_TYPE (REUSABLE)
  Cases: 2 (PH02-SPECIFICITY-VALUE-COL/CS001)
  Documents: 2 (is11_resnet, is11_cs_001)
  C1-C7: ALL MET → REUSABLE

  Evidence Requirement:
  - Column header or surrounding text (may indicate type) — R4 (document context)
  - Entity context (what do these numbers represent?) — R5 (semantic)
  - DICE can provide: column header, table title, surrounding text
  - DICE cannot provide: semantic meaning of numbers

  Boundary Level: B2
  → DICE can provide table context
  → Human still must determine semantic type
```

---

## 7. Boundary Level Analysis (B0–B3)

### 7.1 Current State

```
ALL 4 patterns are at Boundary Level B2:

  B0 (Human reads from scratch): NOT current state
    → DICE already provides structural evidence (R1=YES for all 18)

  B1 (DICE provides partial evidence): PARTIALLY current state
    → DICE provides structural evidence but not all context (R4=PARTIAL for 16)

  B2 (DICE provides main evidence, Human needs semantic judgment): CURRENT STATE
    → All 18 cases: structural evidence complete, Human needs semantic understanding
    → This is the CURRENT operational level

  B3 (DICE provides Minimum Sufficient Handoff Package): NOT YET
    → Would require: organizing page_context (R2/R3) for author_name cases
    → Would require: wider local context for text_role cases
    → Would require: table context for column_type cases
    → NOT authorized to implement

  B4 (Human no longer needed): FORBIDDEN
    → G5 means Human IS needed; B4 is not a goal
```

### 7.2 Level Distribution

| Level | Patterns | Cases | Description |
|-------|---------|------:|-------------|
| B0 | 0 | 0 | Human reads from scratch |
| B1 | 0 | 0 | DICE provides partial evidence |
| **B2** | **4** | **18** | **DICE provides main evidence, Human needs semantic judgment** |
| B3 | 0 | 0 | Minimum Sufficient Handoff Package |
| B4 | 0 | 0 | FORBIDDEN |

```
ALL patterns are at B2.
This is the stable state: DICE provides structural evidence, Human provides semantic judgment.
Moving to B3 would require evidence reorganization (NOT authorized).
B4 is forbidden (G5 means Human is needed).
```

---

## 8. Evidence Learning Path (Q9)

### 8.1 The Allowed Path

```
ALLOWED (researched, not implemented):

  Human Judgment
      ↓
  Evidence Requirement (what did Human need?)
      ↓
  Boundary Handoff Pattern Candidate
      ↓
  Future Human Handoff (DICE prepares evidence)

  This path:
  - Does NOT learn Human's answer
  - Does NOT create a rule
  - Does NOT create a capability
  - Only records WHAT EVIDENCE the Human needed
  - Uses this to prepare better Evidence Packs in the future

FORBIDDEN:

  Human Judgment → Semantic Label ❌
  Human Judgment → Rule ❌
  Human Judgment → Capability ❌
  Human Judgment → Automatic Decision ❌
  Handoff Pattern → Automatic Semantic Decision ❌
```

### 8.2 Safety Check

```
Can Human Judgment be safely converted to Evidence Requirement?

  YES — with strict conditions:

  1. Record WHAT evidence was needed, NOT what the answer was
     → "Human needed local context + semantic understanding"
     → NOT "Human said this is a caption"

  2. The requirement is about EVIDENCE TYPE, not SEMANTIC LABEL
     → "LOCAL_CONTEXT + SEMANTIC_UNDERSTANDING"
     → NOT "caption=true"

  3. The pattern describes a RELATIONSHIP, not a RULE
     → "CAPTION_VS_REFERENCE boundary → needs local context"
     → NOT "IF FIG+below THEN caption"

  4. The pattern does NOT predict the judgment
     → CE2 proves: same pattern, different judgment
     → The pattern predicts the REQUIREMENT, not the ANSWER

  5. The pattern is a CANDIDATE, not a validated signal
     → Requires more cases, more documents, multi-reviewer validation
     → NOT authorized to implement

  CONCLUSION:
  Human Judgment → Evidence Requirement is SAFE.
  It records what evidence Human needs, not what answer Human gave.
  This is the fundamental distinction between Evidence Learning and Answer Learning.
```

---

## 9. "Unlearnable" Boundary Check (Q8)

### 9.1 Is Any G5 Boundary Completely Without Pattern?

```
NO — all 18 E4 cases fit into one of 4 patterns.

  P1 (CAPTION_VS_REFERENCE): 10 cases
  P2 (TEXT_ROLE_AMBIGUITY): 4 cases
  P3 (AUTHOR_NAME_RECOGNITION): 2 cases (conditional)
  P4 (COLUMN_SEMANTIC_TYPE): 2 cases

  Every G5 case has a describable Evidence Requirement.
  Every G5 case fits into a pattern (at least conditionally).
  → No case is "completely unlearnable" in terms of Evidence Requirement.

  BUT:
  → All 18 cases require R5 (semantic knowledge) — 100%.
  → All 18 cases are R6 (unresolvable by evidence) — 100%.
  → The JUDGMENT is unlearnable (requires Human semantic understanding).
  → The REQUIREMENT is learnable (can be described and prepared for).

  This is the key insight:
  → We cannot learn the ANSWER (Human must provide it).
  → We CAN learn the REQUIREMENT (what evidence to prepare).
  → HANDOFF_PATTERN_NOT_SUPPORTED = FALSE for all 18 cases.
  → But JUDGMENT_AUTOMATION_NOT_SUPPORTED = TRUE for all 18 cases.
```

---

## 10. Over-Design Audit

```
  O1: New field? → NO
  O2: New Schema? → NO
  O3: New Observation? → NO
  O4: New Semantic Label? → NO (requirement dimensions are analysis-only)
  O5: New Rule? → NO
  O6: New Detector? → NO
  O7: New Signal? → NO (pattern candidates, not signals)
  O8: New Capability? → NO
  O9: Increased Human Annotation? → NO
  O10: One-Case-One-Patch? → NO (4 patterns cover 18 cases)

  ALL CHECKS: FALSE
  OVER_DESIGN_AUDIT = PASS
```

---

## 11. Limitations

```
  BHL-L-01: SINGLE HUMAN REVIEWER
    All M-A judgments from one reviewer.
    Evidence Requirements may be reviewer-specific.

  BHL-L-02: NO IMPLEMENTATION TEST
    B3 level (Minimum Sufficient Handoff) is theoretical.
    Actual Human benefit from prepared evidence unverified.

  BHL-L-03: P3 NOT CROSS-DOCUMENT
    AUTHOR_NAME_RECOGNITION has only 1 document (2 cases).
    Conditional — needs more cases from different documents.

  BHL-L-04: R5=100% MEANS NO STRUCTURAL EXPANSION
    All 18 cases need semantic knowledge.
    No pattern can reach B3 by structural evidence alone.
    B3 would require providing CONTEXT (R4), not ANSWERS (R5).

  BHL-L-05: PATTERN ≠ SIGNAL
    4 patterns are CANDIDATES, not validated signals.
    They describe requirements, not rules.
    Cannot be used for automatic decisions.

  BHL-L-06: CE2 IS SINGLE INSTANCE
    CE2 proves Requirement=Same despite Judgment=Different.
    But it's one pair. More pairs would strengthen the finding.

  BHL-L-07: NO HUMAN TIME DATA
    Cannot claim Human review time decreases.
    "Human will be faster" is NOT_DEMONSTRATED.
```

---

## 12. Final Questions

### Q1: 18 个 genuine G5 cases 中，有多少存在可描述的 Human Evidence Requirement？

```
18/18 (100%)

  ALL 18 E4 cases have a describable Evidence Requirement.
  All require R5 (Semantic Knowledge) + R6 (Unresolvable by evidence).
  4 distinct requirement dimensions identified.
  No case has UNKNOWN requirement.
```

### Q2: 这些 Requirement 是否跨案例重复？

```
YES

  4 patterns with repeated requirements:
  - P1: 10 cases share LOCAL_CONTEXT + SEMANTIC_UNDERSTANDING
  - P2: 4 cases share LOCAL_CONTEXT + SPATIAL_RELATION + SEMANTIC_UNDERSTANDING
  - P3: 2 cases share ENTITY_CONTEXT + SEMANTIC_UNDERSTANDING
  - P4: 2 cases share ENTITY_CONTEXT + SEMANTIC_UNDERSTANDING

  18/18 cases fit into a pattern with at least 1 other case.
```

### Q3: 是否存在跨文档的 Requirement Pattern？

```
YES — for 3 of 4 patterns:

  P1 (CAPTION_VS_REFERENCE): 3 documents ✅
  P2 (TEXT_ROLE_AMBIGUITY): 3 documents ✅
  P3 (AUTHOR_NAME_RECOGNITION): 1 document ❌ (CONDITIONAL)
  P4 (COLUMN_SEMANTIC_TYPE): 2 documents ✅

  16/18 cases (88.9%) are in cross-document patterns.
  2/18 cases (11.1%) are in single-document pattern (conditional).
```

### Q4: CE2 中相同 Evidence、不同 Judgment 的两个案例，其 Human Evidence Requirement 是否相同？

```
YES — Requirement is SAME.

  CE2-NO: LOCAL_CONTEXT + SEMANTIC_UNDERSTANDING, R5=YES, R6=YES
  CE2-YES: LOCAL_CONTEXT + SEMANTIC_UNDERSTANDING, R5=YES, R6=YES

  Evidence: identical
  Judgment: different (NO vs YES)
  Requirement: SAME

  IMPLICATION:
  → The Handoff Pattern is valid: same boundary → same requirement.
  → The difference in judgment comes from semantic content, not evidence need.
  → DICE can prepare the same Evidence Package for both cases.
  → The Human then makes different judgments using the same evidence.
  → This is the essence of Boundary Handoff: prepare evidence, not answers.
```

### Q5: 能否形成稳定的 Boundary → Evidence Requirement 关系？

```
YES — for 3 of 4 patterns (REUSABLE):

  CAPTION_VS_REFERENCE → LOCAL_CONTEXT + SEMANTIC_UNDERSTANDING
  TEXT_ROLE_AMBIGUITY → LOCAL_CONTEXT + SPATIAL_RELATION + SEMANTIC_UNDERSTANDING
  COLUMN_SEMANTIC_TYPE → ENTITY_CONTEXT + SEMANTIC_UNDERSTANDING

  1 pattern is CONDITIONAL (AUTHOR_NAME_RECOGNITION, needs cross-document).

  The relationship is stable because:
  - Same boundary type → same requirement (across cases and documents)
  - CE2 confirms: even with different judgments, requirement is the same
  - The requirement describes WHAT evidence to prepare, not WHAT answer to give
```

### Q6: 能否形成 Evidence Requirement → Boundary Handoff Pattern？

```
YES — 4 Pattern Candidates identified:

  P1: CAPTION_VS_REFERENCE → 10 cases, 3 docs, REUSABLE, B2
  P2: TEXT_ROLE_AMBIGUITY → 4 cases, 3 docs, REUSABLE, B2
  P3: AUTHOR_NAME_RECOGNITION → 2 cases, 1 doc, CONDITIONAL, B2
  P4: COLUMN_SEMANTIC_TYPE → 2 cases, 2 docs, REUSABLE, B2

  3 REUSABLE + 1 CONDITIONAL = 4 Pattern Candidates.
  All at B2 (DICE provides evidence, Human makes semantic judgment).

  CRITICAL: These are CANDIDATES, not validated signals.
  They describe Evidence Requirements, not Rules.
  They cannot be used for automatic decisions.
```

### Q7: 多少 Pattern 可以达到 B1/B2/B3？

```
  B1 (partial evidence): 0 patterns
  B2 (main evidence + Human semantic): 4 patterns (ALL)
  B3 (Minimum Sufficient Handoff): 0 patterns (NOT YET)

  ALL patterns are at B2.
  Moving to B3 would require:
  - Organizing page_context for P3 (R2/R3)
  - Providing wider local context for P2 (R4)
  - Providing table context for P4 (R4)
  - NOT authorized to implement.

  B4 (Human no longer needed): FORBIDDEN.
  G5 means Human IS needed. B4 is never a goal.
```

### Q8: 多少 G5 完全不存在稳定 Handoff Pattern？

```
0/18 (0%)

  ALL 18 G5 cases fit into a pattern.
  No case is "completely unlearnable" in terms of Evidence Requirement.

  BUT:
  → The JUDGMENT is unlearnable (R5=100%, R6=100%).
  → The REQUIREMENT is learnable (all 18 have describable requirements).
  → We cannot learn the ANSWER, but we CAN learn what evidence to PREPARE.

  HANDOFF_PATTERN_NOT_SUPPORTED = FALSE for all 18 cases.
  JUDGMENT_AUTOMATION_NOT_SUPPORTED = TRUE for all 18 cases.
```

### Q9: Human Judgment 是否可以安全地转化为 Evidence Requirement 而不是 Semantic Rule？

```
YES — with strict conditions:

  SAFE PATH:
  Human Judgment → Evidence Requirement → Handoff Pattern Candidate
  → Records WHAT evidence was needed, not WHAT answer was given.
  → Pattern describes requirement type, not semantic label.
  → CE2 proves: same requirement, different judgment → no answer leakage.

  FORBIDDEN PATH:
  Human Judgment → Semantic Label → Rule → Automatic Decision
  → Would learn the answer, not the requirement.
  → Would create a rule that predicts judgment from evidence.
  → CE2 proves this is impossible (identical evidence → different judgment).

  The distinction:
  Evidence Requirement = "Human needed local context + semantic understanding"
  Semantic Rule = "IF FIG+below THEN caption=YES"

  The former is safe (describes need).
  The latter is forbidden (predicts answer).

  CONDITION: The conversion must NEVER record the answer.
  Only the requirement. This is enforceable by design.
```

### Q10: 下一阶段应该 STOP 还是 DESIGN_RESEARCH 还是 EXPERIMENT_DESIGN？

```
STOP.

  REASONING:
  1. All 18 G5 cases require R5 (semantic knowledge) — 100%.
     → No structural evidence can eliminate the need for Human semantic judgment.
     → The boundary is genuine and irreducible.

  2. 4 Handoff Pattern Candidates identified (3 REUSABLE + 1 CONDITIONAL).
     → The REQUIREMENT is learnable.
     → But implementing it (B3) requires evidence reorganization (NOT authorized).

  3. ALL patterns are at B2 (current operational level).
     → Moving to B3 requires IMPLEMENTATION.
     → B4 is FORBIDDEN.

  4. CE2 confirms: Requirement is same even when Judgment differs.
     → The pattern is valid but cannot predict the answer.
     → This is the fundamental limit of Evidence-Based systems.

  5. No further READ-ONLY research can advance the patterns.
     → Patterns are identified.
     → Requirements are classified.
     → What remains is IMPLEMENTATION (not authorized) or VALIDATION (not authorized).

  WHAT WAS LEARNED:
  - 18/18 G5 cases have describable Evidence Requirements.
  - 4 reusable patterns identified (3 cross-document REUSABLE).
  - CE2 proves: same requirement, different judgment → pattern is valid.
  - All patterns at B2: DICE provides evidence, Human provides semantic judgment.
  - The KEY INSIGHT: we can learn the REQUIREMENT but not the ANSWER.

  WHAT WOULD BE NEEDED TO CONTINUE:
  - Implement B3 (organize page_context, wider local context, table context) — NOT authorized.
  - Multi-reviewer validation of pattern stability — NOT authorized.
  - Cross-domain pattern testing — NOT authorized.

  NONE possible in READ-ONLY mode.
  → STOP.
```

---

## 13. The Deep Finding: Requirement vs Answer

```
This research reveals the fundamental distinction:

  ANSWER (Human's judgment):
    → Cannot be learned from structural evidence.
    → CE2 proves: identical evidence → different judgment.
    → R5=100%, R6=100%: semantic judgment is irreducible.
    → DICE cannot predict the answer.

  REQUIREMENT (what evidence Human needs):
    → CAN be learned from boundary type.
    → 4 stable patterns across 18 cases.
    → CE2 proves: same boundary → same requirement (even with different answers).
    → DICE can predict what evidence to prepare.

  THIS IS THE BOUNDARY HANDOFF PRINCIPLE:

  DICE does NOT learn: "This text is a caption."
  DICE DOES learn: "Caption-vs-reference boundaries need local context + semantic understanding."

  The former is an ANSWER (forbidden).
  The latter is a REQUIREMENT (allowed).

  This distinction makes Evidence Learning safe:
  → DICE prepares evidence based on pattern.
  → Human makes judgment based on evidence.
  → DICE never provides the answer.
  → Human never becomes a confirmation button.

  This is the correct relationship between DICE and Human:
  DICE = Evidence Provider (prepares what Human needs)
  Human = Semantic Judge (makes the irreducible judgment)
  G5 = The boundary between them (where evidence ends, judgment begins)
```

---

## 14. Files Created

```
tmp/boundary_handoff_learning_research.md          (this file)
tmp/boundary_handoff_learning_research.json         (structured data)
tmp/boundary_handoff_learning_case_table.csv        (18 cases, 18 fields)
```

---

## 15. Final Governance State

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
NEW_OBSERVATION = NONE
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
Boundary Handoff Learning Design Research is COMPLETE.

SUMMARY:
  - 18 E4 genuine G5 cases analyzed for Human Evidence Requirement
  - R5 (semantic knowledge needed): 18/18 (100%)
  - R6 (unresolvable by evidence): 18/18 (100%)
  - 4 Boundary Handoff Pattern Candidates identified:
    P1: CAPTION_VS_REFERENCE (10 cases, 3 docs, REUSABLE, B2)
    P2: TEXT_ROLE_AMBIGUITY (4 cases, 3 docs, REUSABLE, B2)
    P3: AUTHOR_NAME_RECOGNITION (2 cases, 1 doc, CONDITIONAL, B2)
    P4: COLUMN_SEMANTIC_TYPE (2 cases, 2 docs, REUSABLE, B2)
  - 3 REUSABLE + 1 CONDITIONAL = 4 patterns
  - ALL at B2 (DICE provides evidence, Human makes semantic judgment)
  - CE2: Evidence identical, Judgment different, Requirement SAME
    → Pattern valid: same boundary → same requirement
    → Difference in judgment from semantic content, not evidence need

KEY INSIGHT:
  We cannot learn the ANSWER (R5=100%, R6=100%).
  We CAN learn the REQUIREMENT (4 stable patterns).
  DICE prepares evidence based on pattern.
  Human makes judgment based on evidence.
  DICE never provides the answer.
  Human never becomes a confirmation button.

  This is the correct DICE-Human relationship at the G5 boundary.

  不得自动进入 Implementation。
  不得创建任何 Rule / Signal / Capability。
  不得把 Pattern 当作 Signal。
  不得把 Requirement 当作 Answer。
  STOP = TRUE
```
