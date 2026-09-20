# Evaluation Object Closure Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY / NO MODIFICATION / FROZEN INTACT / STOP

---

## 1. Executive Summary

```
EVALUATION_OBJECT_FINAL = MIXED
  Boundary Family A: STRUCTURAL_OBJECT (41/45 = 91%) — table columns + figure captions
  Boundary Family B: TEXTUAL_STRUCTURE (4/45 = 9%) — prose sentence boundary

EVALUATION_OBJECT_CONFIDENCE = HIGH (based on 45 cases, reviewer rationales, counterfactual tests)

CROSS_CASE_COHERENCE = PARTIAL (89% structural, 9% textual — different levels)
HUMAN_FEEDBACK_COHERENCE = FAIL (MERGE/KEEP_SEPARATE has different semantics per family)

KEY FINDING:
  The 45-case pool mixes TWO distinct boundary families under one MERGE/KEEP_SEPARATE label:
    Family A (91%): Structural Object Boundary — tests Perception quality (TLD, FIG detection)
    Family B (9%): Textual Structure Boundary — tests Content Unit standard (sentence vs paragraph)

  These are DIFFERENT problems:
    - Family A uses structural evidence (TLD, FIG prefix) — 0 disagreements
    - Family B uses textual evidence (period, capital) — 4 disagreements (ALL)
    - MERGE means "same caption" in Family A, "same paragraph" in Family B
    - KEEP_SEPARATE means "different columns" in Family A, "different sentences" in Family B

  COUNTERFACTUAL TESTS:
    - If Sentence solved: 4/45 resolved, 41 still need Human (structural)
    - If Structural solved: 41/45 resolved, 4 still need Human (content unit)
    - If Evidence Boundary solved: 45/45 resolved — but Evidence Unit undefined

RECOMMENDED_ROUTE = F (Evaluation Object not cleanly defined; continue READ-ONLY)
  + Sub-route: separate Family A and Family B research tracks

PERSISTENT_SEMANTIC_AMBIGUITY = NOT_FOUND
LLM_NEEDED = NO
DOCUMENT_DISCOURSE_NEEDED = NO
STOP = TRUE
```

> **DICE 当前 45-case Boundary Research 的 Evaluation Object 是 MIXED——混合了两个不同的 boundary family：Structural Object Boundary（91%，table columns + figure captions，0 分歧）和 Textual Structure Boundary（9%，prose sentence boundary，4 分歧）。这两个 family 使用不同的 evidence（TLD/FIG vs period/capital），处于不同的 ontology 层级（document structure vs textual structure），并且 MERGE/KEEP_SEPARATE 在它们之间没有一致的语义。不能将它们统一在一个 Boundary metric 下。当前 Evaluation Object 尚未清晰定义。**

---

## 2. Research Question

> DICE 的 Boundary Intelligence 到底是在解决什么对象的边界问题？

---

## 3. Full 45-Case Boundary Object Classification

### 3.1 Classification Results

| Group | Cases | % | Disagreements | Primary Object | Key Evidence |
|---|---|---|---|---|---|
| **A_PROSE** | 4 | 9% | **4 (100%)** | SENTENCE | period_end + cap_start |
| **B_TABLE** | 39 | 87% | 0 (0%) | STRUCTURAL_OBJECT | TLD, h_gap, column position |
| **C_FIGURE** | 2 | 4% | 0 (0%) | STRUCTURAL_OBJECT | has_fig_prefix |
| **D_MIXED** | 0 | 0% | 0 | — | — |

### 3.2 Boundary Object Distribution

| Primary Object | Count | % |
|---|---|---|
| STRUCTURAL_OBJECT | 41 | 91% |
| SENTENCE | 4 | 9% |
| CONTENT_UNIT (as primary) | 0 | 0% |
| EVIDENCE_UNIT (as primary) | 0 | 0% |
| UNKNOWN | 0 | 0% |

> **91% of cases test Structural Object Boundary. Only 9% test Sentence/Textual Structure Boundary.**

---

## 4. Group A (Prose) — Sentence or Evidence Boundary?

### 4.1 What Reviewers Actually Judge

All 4 prose cases have identical disagreement structure:
- Both reviewers AGREE on facts: sentence boundary (period + capital) + same paragraph
- Reviewer A: "different sentences → KEEP_SEPARATE" (text unit = sentence)
- Reviewer B: "same paragraph → MERGE" (text unit = paragraph)

### 4.2 Is This Sentence Boundary or Evidence Boundary?

**This is TEXTUAL STRUCTURE BOUNDARY (Sentence), NOT Evidence Boundary.**

- Reviewers judge whether two spans belong to the same sentence/paragraph
- They do NOT judge whether spans should form an Evidence Unit
- The disagreement is about Content Unit definition (sentence vs paragraph)
- Adjudicator resolved with sentence boundary (period + cap → KEEP_SEPARATE)

> **Group A tests Textual Structure Boundary. The 4 disagreements are Standard Gap (content unit undefined), not Evidence Boundary issues.**

---

## 5. Group B (Table) — Column, Structural, or Evidence?

### 5.1 What Reviewers Actually Judge

All 39 table cases (0 disagreements):
- Reviewer rationales consistently reference: "different table columns", "different cells", "column headers"
- Both reviewers agree: different table columns → KEEP_SEPARATE

### 5.2 Is This Column Boundary, Structural Object, or Evidence Unit?

**This is STRUCTURAL_OBJECT Boundary.**

- Reviewers judge whether two spans are in different table columns
- This is a structural property of the document (table structure)
- TLD detection is the key evidence (is_in_table, different_cell)
- It is NOT Evidence Boundary — reviewers don't mention "evidence" or "verification"
- It IS Structural Object Boundary — "are these different structural elements?"

> **Group B tests Structural Object Boundary (table column separation). The key evidence is TLD, not text content. 0 disagreements → standard is clear for table cases.**

### 5.3 TLD Coverage Gap

- 27/39 table cases have TLD=False (TLD missed the table)
- But reviewers still agreed (KEEP_SEPARATE) — they used text content + context
- TLD coverage gap is an EVIDENCE_ORGANIZATION issue, not a standard gap

---

## 6. Group C (Figure Caption) — Caption or Evidence?

### 6.1 What Reviewers Actually Judge

Both figure cases (0 disagreements):
- Reviewer rationales: "figure label + caption body = same caption"
- Both agree: MERGE (label belongs to caption)

### 6.2 Is This Caption Boundary, Figure Object, or Evidence?

**This is STRUCTURAL_OBJECT Boundary (Figure Caption composition).**

- Reviewers judge whether label + body form one caption object
- This is a structural property (figure caption is a structural object)
- has_fig_prefix is the key evidence
- It is NOT Evidence Boundary — reviewers judge caption composition, not evidence grouping

> **Group C tests Structural Object Boundary (figure caption composition). Key evidence: FIG prefix. 0 disagreements → standard is clear for figure cases.**

---

## 7. Counterfactual Tests

### 7.1 CF1: If Sentence Boundary = PERFECT

| Status | Count | Cases |
|---|---|---|
| NO_HUMAN_AFTER_SENTENCE | 4 (9%) | A_PROSE (4 disagreements resolved) |
| HUMAN_STILL_NEEDED_STRUCTURAL | 41 (91%) | B_TABLE + C_FIGURE |
| UNKNOWN | 0 | — |

> **Sentence Boundary solves 4/45 (9%). The remaining 91% need Structural Object boundary. Sentence is a LOCAL subproblem.**

### 7.2 CF2: If Structural Object = PERFECT

| Status | Count | Cases |
|---|---|---|
| NO_HUMAN_AFTER_STRUCTURAL | 41 (91%) | B_TABLE + C_FIGURE |
| HUMAN_STILL_NEEDED_CONTENT_UNIT | 4 (9%) | A_PROSE (sentence vs paragraph) |
| UNKNOWN | 0 | — |

> **Structural Object solves 41/45 (91%). Prose still needs Content Unit standard. Structural is the DOMINANT object.**

### 7.3 CF3: If Evidence Boundary = PERFECT

| Status | Count | Cases |
|---|---|---|
| ALL_RESOLVED | 45 (100%) | All cases |

> **If Evidence Boundary were perfect, all 45 cases would be resolved. BUT: Evidence Unit is NOT defined in DICE, and IS-11 tests pairwise (not grouping). Evidence Boundary subsumes both families but is not currently computable.**

---

## 8. MERGE/KEEP_SEPARATE Semantic Consistency (C3)

### 8.1 MERGE Semantics

| Family | MERGE means | Evidence |
|---|---|---|
| C_FIGURE | "figure label + caption body = same caption" | Structural composition |
| A_PROSE (Reviewer B) | "same paragraph = same text unit" | Textual grouping |

> **MERGE has DIFFERENT semantics: structural composition vs textual grouping. NOT consistent.**

### 8.2 KEEP_SEPARATE Semantics

| Family | KEEP_SEPARATE means | Evidence |
|---|---|---|
| B_TABLE | "different table columns/cells" | Structural separation |
| A_PROSE | "different sentences" | Textual separation |

> **KEEP_SEPARATE has DIFFERENT semantics: structural separation vs textual separation. NOT consistent.**

### 8.3 C3 Verdict

```
HUMAN_FEEDBACK_COHERENCE = FAIL
```

> **MERGE/KEEP_SEPARATE does NOT have consistent semantics across case types. The 45-case protocol mixes different boundary judgments under one label space. This is the root cause of evaluation design ambiguity.**

---

## 9. Three Criteria Check

### C1: Research Relevance (serves Evidence Quality?)

| Object | Relevance | Coverage |
|---|---|---|
| O1 Sentence | PARTIAL (prose only) | 9% |
| O2 Structural Object | YES (Perception quality foundation) | 91% |
| O3 Content Unit | YES (but undefined) | 100% (meta) |
| O4 Evidence Boundary | YES (but undefined, harder problem) | 100% (meta) |
| O5 Capability Evidence | UNKNOWN (insufficient data) | ? |

### C2: Cross-case Coherence

| Object | Coherence | Notes |
|---|---|---|
| O1 Sentence | NO (prose only) | 9% coverage |
| O2 Structural | PARTIAL (89% + misses prose) | Coherent for table/figure |
| O3 Content Unit | META (undefined, per-type definitions) | 100% but not unified |
| O4 Evidence | META (undefined) | 100% but not computable |

### C3: Human Feedback Coherence

**FAIL** — MERGE/KEEP_SEPARATE has different semantics per family (see Section 8).

---

## 10. Boundary vs Evidence Unit Construction

### 10.1 Relationship

```
IS-11 task: "Are these two spans the same text unit?" (pairwise MERGE/KEEP)
  → This is a PAIRWISE boundary judgment

Evidence Unit Construction: "Which spans should form one Evidence Unit?" (grouping)
  → This is a GROUPING judgment
```

- Pairwise boundary is a PROJECTION of Evidence Unit grouping
- If Evidence Unit grouping were known, pairwise boundary would be deterministic
- BUT: Evidence Unit Construction is HARDER (needs grouping, context, capability)
- AND: Evidence Unit is NOT defined in DICE

### 10.2 Does DICE Need "Document Boundary Understanding" or "Evidence Unit Construction"?

**Both, but at different stages:**

- Boundary Research (IS-11) = **Perception Quality Gate** — "Does Perception correctly separate spans?"
- Evidence Unit Construction = **Later stage** — "Which spans form verifiable Evidence?"

> **Boundary Research serves Perception Quality, not Evidence Construction. It is a NECESSARY but NOT SUFFICIENT step. The true value of Boundary Research is testing whether Machine can correctly identify when spans should be separated — this is foundational for Evidence Construction but is NOT Evidence Construction itself.**

---

## 11. Two Boundary Families — Not One

### Family A: Structural Object Boundary (41/45 = 91%)

```
Object: Document structural objects (tables, figures, captions)
Question: "Are these spans in different structural objects?"
Evidence: TLD (table detection), FIG prefix, geometry
Disagreements: 0 (reviewers agree)
Standard: Clear (implicit: table cell, figure caption)
Role: Perception Quality Gate
```

### Family B: Textual Structure Boundary (4/45 = 9%)

```
Object: Textual structure (sentences within paragraphs)
Question: "Are these spans different sentences?"
Evidence: period_end + cap_start (E3, derivable)
Disagreements: 4 (ALL disagreements — standard gap)
Standard: Ambiguous (text unit undefined: sentence vs paragraph)
Role: Content Unit Standard Clarification
```

### They Are Different Problems

| Dimension | Family A | Family B |
|---|---|---|
| Ontology level | Document structure | Textual structure |
| Key evidence | TLD, FIG prefix | period, capital |
| Disagreements | 0 | 4 (100%) |
| Standard clarity | Clear (implicit) | Ambiguous (undefined) |
| Resolution | Structural detection | Standard clarification |
| What it tests | Perception quality | Content unit definition |

> **These two families should NOT be evaluated under one unified Boundary metric. They test different capabilities at different ontology levels.**

---

## 12. Hierarchy Assessment

### Proposed Conceptual Hierarchy (RESEARCH_HYPOTHESIS only — NOT engineered)

```
Document
 ├── Structural Objects ← Family A (91%)
 │    ├── Table (columns, cells)
 │    ├── Figure (captions)
 │    └── Caption (label + body)
 │
 ├── Textual Structure ← Family B (9%)
 │    ├── Paragraph
 │    └── Sentence
 │
 └── Evidence Unit ← Future (undefined)
      └── (capability-relevant grouping)
```

### Assessment

```
HIERARCHY_NOT_ESTABLISHED (as engineering ontology)
```

- Evidence: Family A and Family B are at DIFFERENT levels (document vs textual)
- They use DIFFERENT evidence (TLD/FIG vs period/capital)
- They have DIFFERENT disagreement patterns (0 vs 4)
- BUT: insufficient data to establish full ontology
- This is a RESEARCH_HYPOTHESIS, not an engineering design

---

## 13. Human Minimal Feedback Re-examination

### Current Feedback: MERGE / KEEP_SEPARATE / UNKNOWN

| Feedback Type | Family A meaning | Family B meaning | Consistent? |
|---|---|---|---|
| MERGE | "same caption object" | "same paragraph" | **NO** |
| KEEP_SEPARATE | "different columns" | "different sentences" | **NO** |
| UNKNOWN | "uncertain about structure" | "uncertain about standard" | **NO** |

> **Current MERGE/KEEP_SEPARATE is NOT a single semantic judgment. It means different things in different case types. This is the evaluation design's biggest problem.**

### Is There a Unified Minimal Question?

Candidate: "Should these two spans be treated as one unit for downstream verification?"

- For Family A: "one unit" = same structural object (table cell, caption)
- For Family B: "one unit" = same content unit (sentence, paragraph)
- For Evidence: "one unit" = same Evidence Unit

> **No single question achieves consistent semantics across all 45 cases. The "text unit" in the current protocol is overloaded — it means different things for different case types.**

---

## 14. Is There a Unified Minimal Human Judgment?

### Analysis

The 45-case pool does NOT support a single unified minimal judgment because:
1. Family A (91%) tests structural detection — reviewers use TLD/FIG evidence
2. Family B (9%) tests content unit definition — reviewers use text features
3. The two families have different evidence, different standards, different disagreement patterns

### Candidate (if forced to unify)

> "Should these two spans enter the same downstream Evidence Unit?"

But this is O4 (Evidence Boundary), which:
- Is NOT defined in DICE
- Is a harder problem (grouping, not pairwise)
- Would require Evidence Unit definition first

> **No unified minimal judgment is currently available. The evaluation protocol needs to either (a) separate families or (b) define Evidence Unit first.**

---

## 15. DICE Core Chain Positioning

```
Document → Perception → Evidence → Human Validation → Capability
                        ↑
                   IS-11 Boundary tests HERE
```

- IS-11 tests **Perception output quality** — "Did Perception correctly separate spans?"
- It does NOT test Evidence Construction (which comes later)
- It does NOT test Capability Evidence (which comes even later)
- Boundary Research = Perception Quality Gate

### Where Each Family Fits

| Family | Chain Position | What It Tests |
|---|---|---|
| A (Structural) | P2-P4 output quality | TLD/FIG detection correctness |
| B (Textual) | P1 output quality | Text structure (sentence) identification |

> **Both families test Perception quality, but at different perception stages (P1 text vs P2-P4 structural).**

---

## 16. Does DICE Need Boundary Research or Evidence Unit Construction?

### Answer

**DICE needs BOTH, but they are different stages:**

1. **Boundary Research (current IS-11)**: Tests whether Perception correctly separates spans
   - Independent value: catches Perception errors (TLD misses, text structure gaps)
   - Current status: MIXED evaluation object, needs family separation

2. **Evidence Unit Construction (future)**: Decides which spans form verifiable Evidence
   - Depends on: Boundary Research results + Evidence Unit definition
   - NOT yet started in DICE
   - Would subsume Boundary Research if fully defined

### Recommendation

> **Retain Boundary Research as Perception Quality Gate, but SEPARATE the two families. Do NOT prematurely jump to Evidence Unit Construction — Evidence Unit is undefined, and IS-11's pairwise format doesn't test grouping.**

---

## 17. Final Research Questions

### Q1: Text Unit 是否必须定义？

**YES, but PER FAMILY.** For Family B (prose), text unit = sentence must be defined. For Family A (structural), text unit = structural object is already implicit.

### Q2: 最小合理定义？

**Per family:**
- Family A: text unit = structural object (table cell, figure caption) — already clear
- Family B: text unit = sentence (period + capital delimited) — needs clarification

### Q3: Sentence Standard 是否足以支持当前研究目标？

**NO.** Sentence Standard covers 9%. The dominant object (91%) is Structural Object Boundary.

### Q4: Sentence Standard 是否误伤 Figure Caption？

**NO.** 0 false positives (figure labels end with ':', not '.').

### Q5: 当前 Boundary Research 的真正 Evaluation Object？

**MIXED: Structural Object Boundary (91%) + Textual Structure Boundary (9%).**

### Q6: 多少分歧由 Standard Gap 解释？

**4/4 (100%) — all in Family B (prose).**

### Q7: 多少无法由 Standard Gap 解释？

**0 disagreements.** (AMB-032 is EVIDENCE_ORGANIZATION_GAP, not a disagreement.)

### Q8: AMB-032 的 ORG_GAP 是否仍成立？

**YES.** Preserved as EVIDENCE_ORGANIZATION_GAP (Family A, TLD correct but not organized for participant).

### Q9: Persistent Semantic Ambiguity？

**NOT_FOUND.**

### Q10: LLM？

**NO.**

### Q11: Document Discourse？

**NO.**

---

## 18. Final Decision

### EVALUATION_OBJECT_FINAL

```
MIXED
  Family A: STRUCTURAL_OBJECT (91%) — Perception Quality Gate
  Family B: TEXTUAL_STRUCTURE (9%) — Content Unit Standard Gap
```

### EVALUATION_OBJECT_CONFIDENCE

```
HIGH
  - 45 cases fully classified
  - Reviewer rationales analyzed
  - 3 counterfactual tests passed
  - C1/C2/C3 criteria checked
  - Two families clearly distinguished
```

### Role Assignments

```
SENTENCE_BOUNDARY_ROLE        = SUB_PROBLEM (Family B, 9%, standard gap)
STRUCTURAL_BOUNDARY_ROLE      = PRIMARY (Family A, 91%, perception quality)
CONTENT_UNIT_ROLE             = META_CONCEPT (undefined, per-family definitions)
EVIDENCE_BOUNDARY_ROLE        = FUTURE (subsumes both, but undefined)
CAPABILITY_EVIDENCE_ROLE      = NOT_ASSESSABLE (insufficient data)
```

### Coherence

```
CROSS_CASE_COHERENCE      = PARTIAL (two families at different levels)
HUMAN_FEEDBACK_COHERENCE  = FAIL (MERGE/KEEP has different semantics per family)
```

### Recommended Route

```
ROUTE F: Evaluation Object not cleanly defined; continue READ-ONLY
  + Sub-route: separate Family A and Family B research tracks
    1. ACKNOWLEDGE mixing
    2. CLARIFY families are different problems
    3. Family A: focus on TLD/structural detection quality
    4. Family B: clarify Content Unit standard (sentence)
    5. DO NOT unify under one Boundary metric
    6. CONTINUE READ-ONLY research per family
```

### Other Status

```
DOCUMENT_DISCOURSE_NEEDED  = NO
LLM_NEEDED                 = NO
NEW_OBSERVATION_NEEDED     = NO
NEW_ARCHITECTURE_NEEDED    = NO
HIERARCHY_NOT_ESTABLISHED  = (as engineering ontology; research hypothesis only)
PERSISTENT_SEMANTIC_AMBIGUITY = NOT_FOUND
```

---

## 19. Anti-Overdesign Gate

```
No new Ontology engineered
No new Boundary Engine
No Evidence Unit Engine
No new Human UI
No Query Ontology
No Learning Engine
No Pattern Engine
No LLM
No Signal 3 modification
No GT modification
No implementation
No experiment
```

---

## 20. Governance Gate

```
DICE_CORE_MODIFICATION              = NO
P1_P7_MODIFICATION                  = NO
P2_MODIFICATION                     = NO
TLD_MODIFICATION                    = NO
IS11_MODIFICATION                   = NO
GT_MODIFICATION                     = NO
SIGNAL_MODIFICATION                 = NO
LLM                                 = NO
NEW_MODULE                          = NO
NEW_ENGINE                          = NO
RUNTIME_CHANGE                      = NO
CAPABILITY_CHANGE                   = NO
FROZEN_BASELINE                     = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d)
FROZEN_EXPERIMENT                   = INTACT
IMPLEMENTATION_AUTHORIZED           = FALSE
EXPERIMENT_AUTHORIZED               = FALSE
FORMAL_EXPERIMENT                   = NOT_STARTED
STOP                                = TRUE
```

---

## 21. 最终原则验证

> *不要把 Sentence, Table Cell, Figure Caption, Paragraph, Evidence 当成同一级 Ontology*

✓ 遵守：明确区分了 Structural Object（Family A, document level）和 Textual Structure（Family B, paragraph level）。Hierarchy NOT established as engineering ontology。

> *不要追求"大一统"*

✓ 遵守：明确指出两个 family 是不同问题，不应统一在一个 Boundary metric 下。推荐 ROUTE F（分别研究）。

> *如果 Boundary 只是构建 Evidence Unit 的中间手段，则应转向 Evidence Unit Construction*

✓ 回答：Boundary Research 有独立价值（Perception Quality Gate），但 IS-11 的 pairwise 格式不测试 Evidence Unit Construction（grouping）。不应过早跳转到 Evidence Unit Construction——Evidence Unit 未定义。

> *C3: 同一个 MERGE/KEEP/UNKNOWN 在不同 Case 中具有相同语义*

✓ 检查：C3 = FAIL。MERGE 在 Figure 意为 "same caption"，在 Prose 意为 "same paragraph"。KEEP_SEPARATE 在 Table 意为 "different columns"，在 Prose 意为 "different sentences"。语义不一致。

`STOP = TRUE`。
