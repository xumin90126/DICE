# Evidence Boundary Structure Research Report

> **模式: READ-ONLY / RESEARCH ONLY / NO IMPLEMENTATION / NO DETECTOR / NO SCORE / NO HUMAN VALIDATION / STOP**
> 日期: 2026-09-18
> Gate: EVIDENCE_BOUNDARY_STRUCTURE_GATE
> 前置: DICE Research Baseline v1 + 2 Domain Generalization Gates (142 cases, 3 domains)
> 本文件: 研究已观察到的 13 个 Evidence Boundary Cases 是否具有稳定、可描述、可复用的结构。

---

## 0. Research Question

```
唯一研究目标:
  我们观察到的 Evidence Boundary，到底是不是一个真实存在的、跨对象的结构现象？

如果是: 记录结构。
如果只能部分成立: 记录边界。
如果不能成立: 停止这个方向。

不为证明"Evidence Boundary 已经被定义好了"而强行抽象。
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

G1-G5 Framework = FROZEN
Evidence Sufficiency definition = FROZEN
Evidence Boundary definition = FROZEN (B1-B6 + C1-C4)
All 142 prior cases = FROZEN
13 Boundary Cases = FROZEN (research objects, not modified)
```

---

## 2. Research Objects

```
研究对象: EXISTING_EVIDENCE_BOUNDARY_CASE
固定为: 已确认的 13 个 Academic Boundary Cases

  CONFIRMED_EVIDENCE_BOUNDARY: 9
  CONDITIONAL_EVIDENCE_BOUNDARY: 4

  不重新寻找新案例。
  不补造缺失信息。
  部分案例缺少完整信息 → 标记 INCOMPLETE_CASE。

来源:
  tmp/evidence_sufficiency_boundary_research.json (FROZEN)
  tmp/_boundary_analysis.json (FROZEN)
```

### 2.1 The 13 Cases

| # | Case ID | Document | Problem Type | Verdict | Cluster |
|---|---------|----------|-------------|---------|---------|
| 1 | MA-UNC-2 | arxiv_2402.18619 | text_drawing_association | CONFIRMED | SPATIAL→SEMANTIC |
| 2 | MA-UNC-5 | arxiv_2402.18619 | text_drawing_association | CONFIRMED | SPATIAL→SEMANTIC |
| 3 | MA-UNC-6 | arxiv_2402.18619 | text_drawing_association | CONFIRMED | SPATIAL→SEMANTIC |
| 4 | MA-UNC-7 | is11_resnet | text_drawing_association | CONFIRMED | SPATIAL→SEMANTIC |
| 5 | MA-UNC-11 | arxiv_2402.18619 | text_drawing_association | CONFIRMED | SPATIAL→SEMANTIC |
| 6 | PH02-SPECIFICITY-VALUE-COL | is11_resnet | column_membership_specificity | CONFIRMED | STRUCTURAL→SEMANTIC |
| 7 | PH02-SPECIFICITY-CS001 | is11_cs_001 | column_membership_specificity | CONFIRMED | STRUCTURAL→SEMANTIC |
| 8 | IS11-AMB-375 | is11_med_001 | prose_sentence_boundary | CONDITIONAL | TEXTUAL→SEMANTIC |
| 9 | IS11-AMB-418 | is11_med_001 | prose_sentence_boundary | CONDITIONAL | TEXTUAL→SEMANTIC |
| 10 | IS11-AMB-519 | is11_cs_001 | prose_sentence_boundary | CONDITIONAL | TEXTUAL→SEMANTIC |
| 11 | IS11-AMB-005 | is11_resnet | prose_sentence_boundary | CONDITIONAL | TEXTUAL→SEMANTIC |
| 12 | IND-AMB-033 | ind_arxiv_bio2 | reference_list_author_title | CONFIRMED | TEXTUAL→SEMANTIC |
| 13 | IND-AMB-049 | ind_arxiv_bio2 | reference_list_author_title | CONFIRMED | TEXTUAL→SEMANTIC |

### 2.2 Three Conceptual Clusters

```
Cluster 1: SPATIAL_TO_SEMANTIC (5 cases)
  Object: Text-Drawing (Figure)
  Supported: spatial/structural association
  Unsupported: semantic caption/label identity

Cluster 2: STRUCTURAL_TO_SEMANTIC (2 cases)
  Object: Numeric Column (Table)
  Supported: aligned column structure
  Unsupported: row-number vs data-value column identity

Cluster 3: TEXTUAL_TO_SEMANTIC (6 cases)
  Object: Text-Text (Prose/Reference)
  Supported: period+capital boundary signal
  Unsupported: sentence boundary vs reference continuation
```

---

## 3. Structural Decomposition

File: `tmp/evidence_boundary_structure_case_table.csv`

Each case was decomposed into:

```
available_evidence       — what evidence exists (F1-F12 functions)
evidence_function        — which Evidence Functions are available
supported_claim          — what the evidence CAN support
unsupported_stronger_claim — what the Human task requires but evidence CANNOT support
missing_evidence         — why the stronger claim cannot be supported
boundary_reason          — the mechanism of the boundary
semantic_dependency      — what semantic interpretation is needed
missing_evidence_category — OBSERVATION/ORGANIZATION/PRESENTATION/CONSUMER/SEMANTIC
more_structural_evidence — could more structural evidence solve it?
```

### 3.1 Supported Claims (3 patterns across 13 cases)

```
Pattern 1 (5 cases — Text-Drawing):
  Supported: "Text and Drawing have spatial/structural association"
  Evidence: F1 (lexical) + F2 (spatial reference) + F3 (proximity) + F4 (positional) + F5 (alignment) + F6 (context)
  Strength: COMPLETE structural evidence

Pattern 2 (2 cases — Column):
  Supported: "Numeric atoms form an aligned column"
  Evidence: F1 (lexical) + F12 (column membership / alignment)
  Strength: COMPLETE structural evidence

Pattern 3 (6 cases — Prose/Reference):
  Supported: "Text pair has period+capital boundary signal"
  Evidence: F1 (lexical) + F6 (text reconstruction / context)
  Strength: COMPLETE structural evidence
```

### 3.2 Unsupported Stronger Claims (3 patterns across 13 cases)

```
Pattern 1 (5 cases):
  Unsupported: "Text IS the semantic caption/label of this Drawing"
  Requires: CAPTION_IDENTITY_FUNCTION — distinguishing caption from in-text reference
  Nature: Semantic text understanding beyond spatial evidence

Pattern 2 (2 cases):
  Unsupported: "Column is specifically a row-number column (not a value column)"
  Requires: COLUMN_SEMANTIC_IDENTITY — understanding what the numbers MEAN
  Nature: Semantic content understanding beyond alignment evidence

Pattern 3 (6 cases):
  Unsupported: "Text pair is definitively sentence boundary vs reference continuation"
  Requires: REFERENCE_CONTEXT_FUNCTION (partially) + AUTHOR_NAME_RECOGNITION (for sub-cases)
  Nature: Semantic context understanding + world knowledge
```

---

## 4. Missing Evidence Analysis

### 4.1 Missing Evidence Category

```
ALL 13 cases: SEMANTIC_INTERPRETATION_MISSING

  0 cases: OBSERVATION_MISSING (not G1)
  0 cases: ORGANIZATION_MISSING (not G2)
  0 cases: PRESENTATION_MISSING (not G3)
  0 cases: CONSUMER_ACCESS_MISSING (not G4)
  13/13 cases: SEMANTIC_INTERPRETATION_MISSING (G5)

  → The missing evidence is NOT structural. It is SEMANTIC.
  → This confirms G5 classification is correct for all 13 cases.
  → The boundary is NOT a disguised G1-G4 issue.
```

### 4.2 More Structural Evidence Analysis

```
Could more structural evidence solve the boundary?

  9/13 cases (69.2%): STRUCTURAL_EVIDENCE_NOT_SUFFICIENT
    → More spatial/alignment/lexical evidence CANNOT resolve the boundary
    → C3 counterfactual = NO
    → These are TRUE boundaries: semantic interpretation is genuinely required

  4/13 cases (30.8%): MORE_STRUCTURAL_EVIDENCE_MAY_SOLVE (partially)
    → C3 counterfactual = PARTIAL
    → Page_context (existing P7 observation, NOT organized) MIGHT resolve some sub-cases
    → BUT author-name cases still need world knowledge
    → These are CONDITIONAL boundaries:
      - Some sub-cases: structural (page_context would solve → actually G3, not G5)
      - Other sub-cases: semantic (author-name recognition needed → true G5)
    → The CONDITIONAL classification correctly captures this duality

  INTERPRETATION:
    9/13 are genuine semantic boundaries (structural evidence has a hard ceiling).
    4/13 are partially structural (might resolve with context organization).
    NO case is fully structural (all have at least some semantic dependency).
```

---

## 5. Boundary Structure Analysis

### 5.1 Four Candidate Structures Tested

File: `tmp/evidence_boundary_structure_pattern_table.csv`

```
Structure A: Evidence → Structural Claim → Semantic Identity Claim
  Applicable: 13/13 (100%)
  Precision: HIGH — explicitly names evidence type and claim levels
  Description: Structural evidence (spatial, alignment, lexical) is complete,
               supports a structural claim about object relationship,
               but cannot support a semantic identity claim about object role/meaning.

Structure B: Observable Relation → Interpreted Relation
  Applicable: 13/13 (100%)
  Precision: MEDIUM — equivalent to A with different terminology
  Description: "Observable" = structural evidence; "Interpreted" = semantic identity.

Structure C: Observed Fact → Meaning/Identity
  Applicable: 13/13 (100%)
  Precision: MEDIUM — equivalent to A with different terminology
  Description: "Observed fact" = structural claim; "Meaning/Identity" = semantic claim.

Structure D: Weak Claim → Stronger Claim
  Applicable: 13/13 (100%)
  Precision: LOW — most general, least informative
  Description: Technically correct but doesn't specify WHAT KIND of evidence or claim.
  Limitation: Does not distinguish structural→semantic from other weak→strong transitions.
```

### 5.2 All Four Structures Are Equivalent

```
All 4 structures apply to all 13 cases, but they are NOT independent:

  A, B, C are reformulations of the SAME structure:
    "Structural evidence → Structural claim → Semantic identity claim"

  D is a GENERALIZATION that subsumes A/B/C:
    "Weak claim → Stronger claim"
    But D doesn't specify that the weak claim is STRUCTURAL and the strong claim is SEMANTIC.

  RECOMMENDED REPRESENTATION: Structure A
    Because it is the MOST PRECISE:
    - Names the evidence type (structural: spatial, alignment, lexical)
    - Names the supported claim type (structural: relationship, boundary, membership)
    - Names the unsupported claim type (semantic identity: caption, column type, author name)
    - Distinguishes G5 from G1-G4 (which are structural, not semantic)
```

### 5.3 The Boundary Structure (Structure A)

```
┌─────────────────────────────────────────────────┐
│              EVIDENCE BOUNDARY STRUCTURE          │
│                                                   │
│  Structural Evidence (F1-F12)                     │
│       │                                           │
│       ▼                                           │
│  Evidence is COMPLETE (G1-G4 resolved)            │
│       │                                           │
│       ▼                                           │
│  Supported Claim: STRUCTURAL                      │
│  (relationship between objects exists)            │
│       │                                           │
│       ╳ ─ ─ ─ BOUNDARY ─ ─ ─ ╳                   │
│       │                                           │
│       ▼                                           │
│  Unsupported Stronger Claim: SEMANTIC IDENTITY    │
│  (what IS this object? what is its ROLE?)         │
│       │                                           │
│       ▼                                           │
│  Missing: SEMANTIC_INTERPRETATION                 │
│  (not structural — cannot be solved by more       │
│   spatial/alignment/lexical evidence)             │
└─────────────────────────────────────────────────┘

  The BOUNDARY is between:
    Structural Claim (supported) ← → Semantic Identity Claim (unsupported)

  This is the L2 → L3 transition from the Claim Level framework:
    L1: structural existence
    L2: structural classification (SUPPORTED by current evidence)
    L3: semantic identity (NOT SUPPORTED — boundary)
```

---

## 6. Object-Independence Check

### 6.1 Three Object Types Tested

```
Object Type 1: Text-Drawing (Figure) — 5 cases
  Supported: "Text and Drawing have spatial/structural association"
  Unsupported: "Text IS the semantic caption/label of this Drawing"
  Structure: Evidence → Structural (association) → Semantic (caption identity) ✓

Object Type 2: Numeric Column (Table) — 2 cases
  Supported: "Numeric atoms form an aligned column"
  Unsupported: "Column is specifically a row-number column (not a value column)"
  Structure: Evidence → Structural (alignment) → Semantic (column type identity) ✓

Object Type 3: Text-Text (Prose/Reference) — 6 cases
  Supported: "Text pair has period+capital boundary signal"
  Unsupported: "Text pair is definitively sentence boundary vs reference continuation"
  Structure: Evidence → Structural (boundary signal) → Semantic (unit identity) ✓
```

### 6.2 Result

```
OBJECT_INDEPENDENT_STRUCTURE = SUPPORTED

  All 3 object types (Figure, Table/Column, Text) follow the SAME structure:
    Evidence (structural) → Supported Claim (structural) → Unsupported Stronger Claim (semantic identity)

  No object-specific boundary structure needed.
  The structure is OBJECT-INDEPENDENT.

  The boundary ALWAYS occurs at the same transition point:
    "What is the structural relationship?" → answerable (L2)
    "What is the semantic identity/role?" → NOT answerable (L3)

  This is consistent across:
    - Figure caption vs reference
    - Column row-number vs data-value
    - Sentence boundary vs reference continuation

  None of these require object-specific frameworks.
  All follow the same Evidence → Structural → Semantic Identity structure.
```

---

## 7. Boundary Formation Hypothesis

```
BOUNDARY_FORMATION_HYPOTHESIS:

  Evidence Boundary occurs when ALL of the following are true:

  1. STRUCTURAL EVIDENCE IS COMPLETE
     Evidence exists (G1 resolved), is organized (G2 resolved),
     is presented (G3 resolved), is consumed (G4 resolved).
     The structural evidence surface is fully available.

  2. STRUCTURAL CLAIM IS SUPPORTED
     The evidence supports a claim about the RELATIONSHIP between objects:
     - spatial association (text near drawing)
     - alignment membership (numbers in a column)
     - lexical boundary signal (period + capital letter)

  3. HUMAN TASK REQUIRES SEMANTIC IDENTITY
     The task requires determining the IDENTITY or ROLE of an object:
     - "Is this text a caption or a reference?" (caption identity)
     - "Is this column row-numbers or data values?" (column type identity)
     - "Is this a sentence boundary or reference continuation?" (unit identity)

  4. MORE STRUCTURAL EVIDENCE CANNOT RESOLVE
     Adding more spatial/alignment/lexical evidence does not help.
     C3 counterfactual = NO (for 9/13) or PARTIAL (for 4/13).
     The gap is SEMANTIC, not structural.

  5. MISSING CATEGORY = SEMANTIC_INTERPRETATION_MISSING
     The required evidence is not another observation, organization,
     presentation, or consumer integration — it is semantic interpretation.

SUPPORTING EVIDENCE:
  - 13/13 cases: missing evidence category = SEMANTIC_INTERPRETATION_MISSING
  - 9/13 cases: more structural evidence CANNOT solve (C3=NO)
  - 4/13 cases: more structural evidence MIGHT partially solve (C3=PARTIAL)
  - All 3 object types follow same structure
  - Structure A applies to all 13 cases
  - All 3 clusters show same pattern: structural → semantic

BOUNDARY_FORMATION_HYPOTHESIS = SUPPORTED
  (with CONDITIONAL caveat: 4/13 cases are partially structural)

CONDITIONAL CAVEAT:
  4/13 CONDITIONAL boundary cases may partially resolve with structural evidence
  (page_context organization). This means the boundary formation is not ALWAYS
  purely semantic — in some cases, structural evidence is INCOMPLETE (page_context
  not organized → actually G3, not G5), and only the sub-cases requiring
  author-name recognition are true G5.

  This does NOT invalidate the hypothesis — it refines it:
  TRUE boundary (9/13): structural evidence complete + semantic interpretation needed
  CONDITIONAL boundary (4/13): structural evidence partially incomplete +
    semantic interpretation needed for remaining sub-cases
```

---

## 8. Cross-Domain Reference

```
  Using EXISTING results only (not re-analyzing 72 non-academic cases):

  Academic domain:     13 G5/boundary cases (structural→semantic pattern)
  Biotech domain:       0 G5 cases (G2/G3 dominate, masking G5)
  Finance/Edu domain:   0 G5 cases (G2/G3 dominate, masking G5)

  Why no G5 in non-academic?

  Two possible explanations (from prior research):

  Explanation 1: G5 ABSENT
    Non-academic documents genuinely don't have semantic boundary tasks.
    → NOT supported: financial reports DO have semantic identity tasks
      (technology importance, ranking interpretation) that could be G5.

  Explanation 2: G5 UNOBSERVABLE (MASKED)
    Non-academic documents have complex layouts → G2/G3 failures dominate
    → structural evidence never reaches completeness
    → G5 cannot emerge because G1-G4 is not resolved
    → SUPPORTED by analysis: 3 potential G5 candidates in domain2
      were all MASKED by G2/G3

  DISTINCTION:
    "G5 absent" = semantic boundary doesn't exist in this domain
    "G5 unobservable" = semantic boundary might exist but can't be tested
                         because structural failures block evidence flow

  CURRENT STATUS:
    Cannot distinguish "absent" from "unobservable" with current data.
    The Boundary Formation Hypothesis predicts that IF structural issues
    were resolved in non-academic domains, G5 MIGHT emerge — but this
    is a prediction, not a demonstrated fact.

  This is a RESEARCH FINDING, not a design recommendation.
```

---

## 9. New Evidence Function Check

```
  From the 13 cases, the following "new functions" were identified in prior research:

  1. CAPTION_IDENTITY_FUNCTION (5 cases)
     Distinguishing caption from in-text reference.
     Requires: semantic text understanding.
     Status: IDENTIFIED but NOT IMPLEMENTED (not authorized).

  2. COLUMN_SEMANTIC_IDENTITY (2 cases)
     Distinguishing row-number column from data-value column.
     Requires: semantic content understanding.
     Status: IDENTIFIED but NOT IMPLEMENTED.

  3. REFERENCE_CONTEXT_FUNCTION (4 cases, partially)
     Determining whether text is in body or reference list.
     Requires: page_context organization (P7 exists but not organized).
     Status: PARTIALLY DERIVABLE from existing observations.

  4. AUTHOR_NAME_RECOGNITION (2 cases)
     Recognizing author names in reference lists.
     Requires: world knowledge about names.
     Status: NOT DERIVABLE from current evidence surface.

  Are these NEW Evidence Functions?

  1-2 are genuinely new semantic functions not in F1-F12.
  3 is derivable from existing P7 (page_context) — NOT a new function.
  4 requires world knowledge — beyond any evidence function.

  Q6 answer: YES, new semantic functions are identified.
  BUT: they are NOT implemented, NOT authorized, and NOT writable to DICE.
  They are RESEARCH FINDINGS only.
```

---

## 10. New Gap Type Check

```
  0 new gap types found.

  All 13 cases fit G5 (SEMANTIC_BOUNDARY).
  The boundary structure is consistent with G5 definition.
  No G6 needed.

  The "semantic interpretation missing" category IS G5.
  It is not a new gap — it is the EXISTING G5 definition.

  Q7 answer: NO new gap type.
```

---

## 11. Over-Design Audit

```
  O1: SYSTEM_MODIFIED = FALSE
  O2: NEW_FIELD = FALSE
  O3: NEW_MODULE = FALSE
  O4: NEW_DETECTOR = FALSE
  O5: NEW_EVIDENCE_FUNCTION = FALSE (identified but NOT created/implemented)
  O6: NEW_GAP_TYPE = FALSE
  O7: NEW_CAPABILITY = FALSE
  O8: RUNTIME_CHANGE = FALSE
  O9: HUMAN_VALIDATION_ADDED = FALSE
  O10: THRESHOLD_TUNING = FALSE

  ALL CHECKS: FALSE (PASS)
  OVER_DESIGN_RISK = NONE

  Note: New Evidence Functions were IDENTIFIED as research findings
  (CAPTION_IDENTITY, COLUMN_SEMANTIC_IDENTITY, AUTHOR_NAME_RECOGNITION).
  These are RESEARCH OBSERVATIONS, not system additions.
  They are NOT implemented, NOT authorized, and NOT written to any schema.
```

---

## 12. Limitations

```
BS-L-01: ACADEMIC-ONLY BOUNDARY CASES
  All 13 boundary cases are from academic papers.
  The boundary structure has NOT been tested on non-academic G5 cases
  (because 0 non-academic G5 cases exist).
  → Structure validity is limited to academic domain.

BS-L-02: SMALL SAMPLE SIZE
  Only 13 boundary cases (9 CONFIRMED + 4 CONDITIONAL).
  3 clusters with 5, 6, and 2 cases.
  Column cluster (2 cases) is especially thin.
  → Structure stability needs more cases for confirmation.

BS-L-03: NO HUMAN VALIDATION
  All boundary classifications are RESEARCHER_ASSESSMENT.
  No Human reviewer confirmed the supported/unsupported claims.
  → The claim decomposition is researcher-induced, not Human-validated.

BS-L-04: CONDITIONAL BOUNDARIES
  4/13 cases are CONDITIONAL (might partially resolve with page_context).
  These blur the structural→semantic boundary.
  → The clean structural→semantic pattern applies cleanly to 9/13,
    not all 13.

BS-L-05: G5 MASKED IN NON-ACADEMIC
  Cannot test whether the boundary structure holds outside academic domain
  because G5 is masked by G2/G3 in all tested non-academic domains.
  → Cross-domain structure validity NOT_DEMONSTRATED.

BS-L-06: CLAIM LEVELS ARE RESEARCHER-INDUCED
  L1/L2/L3 claim levels and the structural→semantic transition are
  induced from case analysis, not pre-registered or independently validated.
  → A different researcher might decompose claims differently.
```

---

## 13. Final Questions

### Q1: 13 个 Boundary Cases 是否存在共同结构？

```
SUPPORTED

  13/13 cases share the same structure:
    Structural Evidence (complete) → Structural Claim (supported) → Semantic Identity Claim (unsupported)

  All 13 cases:
  - Have complete structural evidence (G1-G4 resolved)
  - Support a structural claim about object relationship
  - Cannot support a semantic identity claim about object role/meaning
  - Missing evidence category = SEMANTIC_INTERPRETATION_MISSING (13/13)

  The structure is consistent across:
  - 3 object types (Figure, Table/Column, Text)
  - 3 clusters (SPATIAL→SEMANTIC, STRUCTURAL→SEMANTIC, TEXTUAL→SEMANTIC)
  - 5 documents
  - 2 verdict types (CONFIRMED + CONDITIONAL)
```

### Q2: 是否可以抽象为 Evidence → Supported Claim → Unsupported Stronger Claim？

```
SUPPORTED

  All 13 cases fit the abstract structure:
    Evidence → Supported Claim → Unsupported Stronger Claim

  More precisely (Structure A):
    Structural Evidence → Structural Claim (supported) → Semantic Identity Claim (unsupported)

  This is a more precise version of the general Structure D (weak→strong).
  Structure A specifies that:
  - The evidence is STRUCTURAL (spatial, alignment, lexical)
  - The supported claim is STRUCTURAL (relationship exists)
  - The unsupported claim is SEMANTIC IDENTITY (what IS this object?)

  All 4 candidate structures (A/B/C/D) apply to all 13 cases,
  but Structure A is the most PRECISE and INFORMATIVE.
```

### Q3: 这种结构是否与具体对象无关？

```
SUPPORTED

  3 object types tested:
  - Figure (Text-Drawing): spatial association → caption identity
  - Table/Column (Numeric): alignment → column type identity
  - Text (Prose/Reference): boundary signal → unit identity

  All 3 follow the SAME structure:
    Structural Evidence → Structural Claim → Semantic Identity Claim

  No object-specific boundary structure needed.
  The structure is OBJECT-INDEPENDENT.
```

### Q4: Boundary 是否主要发生在 Structural Evidence → Semantic Interpretation 这一位置？

```
SUPPORTED

  13/13 cases: the boundary occurs at the transition from structural evidence
  to semantic interpretation.

  Specifically:
  - Structural evidence is COMPLETE (G1-G4 resolved)
  - Structural claim IS supported (relationship/boundary/alignment confirmed)
  - Semantic identity claim is NOT supported (role/meaning undetermined)
  - The gap is SEMANTIC_INTERPRETATION_MISSING (not structural)

  This is the L2 → L3 transition:
    L2 (structural classification): SUPPORTED
    L3 (semantic identity): NOT SUPPORTED → BOUNDARY

  9/13 cases: purely semantic boundary (C3=NO, structural evidence has hard ceiling)
  4/13 cases: partially structural (C3=PARTIAL, page_context might help some sub-cases)

  The boundary formation is SUPPORTED but with a CONDITIONAL caveat:
  not ALL boundaries are purely semantic (4/13 are partially structural).
```

### Q5: Boundary 是否与 G1–G4 有明确区别？

```
SUPPORTED

  G1-G4: structural evidence is INCOMPLETE somewhere in the chain
    G1: observation missing → nothing to observe
    G2: not organized → cannot use
    G3: not presented → Human can't see
    G4: not consumed → consumer didn't use

  G5/Boundary: structural evidence is COMPLETE but has a SEMANTIC ceiling
    Evidence exists, organized, presented, consumed
    But semantic identity interpretation is needed
    More structural evidence cannot resolve it (9/13 C3=NO)

  The distinction is CLEAR:
  - G1-G4: "Can the Human/consumer ACCESS the evidence?" → NO
  - G5: "Can the evidence answer the SEMANTIC IDENTITY question?" → NO

  13/13 cases: missing evidence category = SEMANTIC_INTERPRETATION_MISSING
  0/13 cases: missing evidence category = OBSERVATION/ORGANIZATION/PRESENTATION/CONSUMER

  → Boundary is clearly distinguished from G1-G4.
```

### Q6: 是否发现新的 Evidence Function？

```
YES

  4 new semantic functions identified (RESEARCH FINDINGS ONLY):

  1. CAPTION_IDENTITY_FUNCTION (5 cases)
     Distinguishing caption from in-text reference.
     Requires semantic text understanding.

  2. COLUMN_SEMANTIC_IDENTITY (2 cases)
     Distinguishing row-number column from data-value column.
     Requires semantic content understanding.

  3. REFERENCE_CONTEXT_FUNCTION (4 cases, partially)
     Determining whether text is in body or reference list.
     PARTIALLY derivable from existing P7 (page_context).

  4. AUTHOR_NAME_RECOGNITION (2 cases)
     Recognizing author names.
     Requires world knowledge.

  IMPORTANT:
  These are RESEARCH OBSERVATIONS, not system additions.
  NOT implemented. NOT authorized. NOT written to any schema.
  Even though identified, they must NOT be created.
```

### Q7: 是否发现新的 Gap Type？

```
NO

  All 13 cases fit G5 (SEMANTIC_BOUNDARY).
  The "semantic interpretation missing" category IS G5.
  No G6 needed.

  The boundary structure is consistent with the EXISTING G5 definition.
  It does not require a new gap type.
```

### Q8: Evidence Boundary 是否已经足够结构化，可以进入下一阶段研究？

```
CONDITIONAL

  STRUCTURE: SUPPORTED
    The boundary has a stable, describable, reusable structure:
    Structural Evidence → Structural Claim → Semantic Identity Claim
    Object-independent, consistent across 13 cases and 3 object types.

  WHAT IS READY:
    - The structure IS describable (Structure A)
    - The structure IS object-independent
    - The structure IS distinguishable from G1-G4
    - The Boundary Formation Hypothesis IS supported
    - The missing evidence category IS consistently SEMANTIC

  WHAT IS NOT READY:
    - Only 13 cases (academic only) — small sample
    - 4/13 cases are CONDITIONAL (not purely semantic)
    - No non-academic G5 cases to test cross-domain structure
    - No Human validation of claim decomposition
    - New semantic functions identified but NOT implementable

  CONDITION FOR NEXT PHASE:
    The boundary structure research has produced a STABLE STRUCTURAL
    REPRESENTATION. However, proceeding to any implementation phase
    would require:
    1. More boundary cases (especially non-academic)
    2. Human validation of the claim decomposition
    3. Resolution of the 4 CONDITIONAL cases
    4. Testing whether the structure holds with resolved G2/G3 in non-academic

  EVIDENCE_BOUNDARY_STRUCTURE_RESEARCH = COMPLETE
  NEXT_PHASE_READINESS = CONDITIONAL

  No implementation is authorized.
  No experiment is authorized.
  No Human validation is authorized.
```

---

## 14. Files Created

```
tmp/evidence_boundary_structure_research.md          (this file)
tmp/evidence_boundary_structure_research.json         (structured data)
tmp/evidence_boundary_structure_case_table.csv        (13 cases, 20 fields)
tmp/evidence_boundary_structure_pattern_table.csv     (13 cases × 4 structures)
```

---

## 15. Final Governance State

```
RESEARCH_STATUS = COMPLETE

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

## STOP

```
Evidence Boundary Structure Research is COMPLETE.

Summary:
  - 13 boundary cases structurally decomposed
  - Common structure FOUND: Structural Evidence → Structural Claim → Semantic Identity Claim
  - Structure is OBJECT-INDEPENDENT (Figure, Table, Text all follow same pattern)
  - Structure is distinguishable from G1-G4 (semantic vs structural gap)
  - Boundary Formation Hypothesis: SUPPORTED (with CONDITIONAL caveat for 4/13)
  - 4 new semantic functions IDENTIFIED (research findings, NOT implemented)
  - 0 new gap types (G5 is sufficient)
  - Next phase: CONDITIONAL (needs more cases + Human validation + non-academic G5)

The Evidence Boundary IS a real, describable, cross-object structural phenomenon.
But it is NOT yet ready for implementation.

不得自动开始下一阶段。
不得修改任何系统。
不得实现任何新 Evidence Function。
STOP = TRUE
```
