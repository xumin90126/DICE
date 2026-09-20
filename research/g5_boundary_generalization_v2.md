# G5 Boundary Generalization V2 — G5_BOUNDARY_GENERALIZATION_V2

> **模式: READ-ONLY RESEARCH / NO IMPLEMENTATION / NO SYSTEM CHANGE / STOP**
> 日期: 2026-09-20
> Gate: G5_BOUNDARY_GENERALIZATION_V2
> 前置: NEW_G5_HUMAN_VALIDATION (COMPLETE, 16 new TRUE_G5)
> 本文件: 验证 16 个 NEW TRUE_G5 是否支持 G5 Evidence Boundary 的跨案例、跨文档 Generalization。

---

## 0. Task Executed

```
验证 NEW_G5_HUMAN_VALIDATION 获得的 16 个 TRUE_G5
是否能够支持 G5 Evidence Boundary 的跨案例、跨文档 Generalization。

数据来源:
  - tmp/g5_boundary_case_acquisition_results.* (16 new TRUE_G5)
  - tmp/evidence_boundary_expansion_research.* (18 original TRUE_G5)
  - tmp/g5_evidence_boundary_governance_research.* (11 FALSE_G5 + Signal)
  - tmp/g5_boundary_generalization_gate.* (181 new cases, V1 result)
  - tmp/boundary_handoff_learning_research.* (18 E4 cases)
  - tmp/human_review_reduction_research.* (77.8% irreducible)
  - tmp/evidence_boundary_structure_research.* (13 G5 structure)
  - tmp/m_a_human_validation_pilot_case_analysis.csv (79 cases, full evidence)
  - tmp/evidence_configuration_family_case_table.csv (50 cases, structural config)

不重新生成候选。
不重新进行 Human Validation。
不增加新的 Human Review。
```

---

## 1. Governance

```
RESEARCH_BASELINE = FROZEN (v1)
FROZEN_BASELINE = INTACT
BASELINE_DRIFT = 0
SYSTEM_MODIFIED = FALSE
IMPLEMENTATION_AUTHORIZED = FALSE
MODEL_TRAINING = FALSE
EXTERNAL_DATASET_IMPORTED = FALSE
CAPABILITY_CREATED = FALSE
RUNTIME_AUTHORITY = ZERO
PRODUCTION = FALSE
STOP = TRUE
```

---

## 2. Combined TRUE_G5 Set

### 2.1 Construction

```
Source 1: Original 18 TRUE_G5 (from Evidence Boundary Expansion Research, E4 level)
Source 2: New 16 TRUE_G5 (from NEW_G5_HUMAN_VALIDATION, Tier 1 A/B/C/D validation)
Combined: 34 TRUE_G5 cases.

All 34 cases are TRUE_G5:
  - Evidence structurally complete (drawing_extent=True or N/A for text-text boundaries)
  - No G1/G2/G3/G4 gap that remains unfixed
  - Semantic identity / semantic role unresolved by structural evidence alone
  - Human semantic judgment required
```

### 2.2 Document Distribution

```
arxiv_2402.18619:    16 TRUE_G5  (47.1%)
is11_resnet:          7 TRUE_G5  (20.6%)
is11_efficientnet:    5 TRUE_G5  (14.7%)
ind_arxiv_bio2:       2 TRUE_G5  (5.9%)  [P3 only]
is11_cs_001:          2 TRUE_G5  (5.9%)
is11_med_001:         2 TRUE_G5  (5.9%)
─────────────────────────────────
Total:               34 TRUE_G5 across 6 documents

CROSS_DOCUMENT_G5 = 6

Note: arxiv_2402.18619 contributes 47.1% — largest single document.
      BUT no single document exceeds 50% → not dominated by one document.
      5 of 6 documents have ≥2 TRUE_G5 cases.
```

### 2.3 Pattern Distribution

```
P1_CAPTION_VS_REFERENCE:  22 cases (64.7%)  — 4 documents
P2_TEXT_ROLE:              8 cases (23.5%)  — 5 documents
P3_AUTHOR_NAME:            2 cases (5.9%)   — 1 document
P4_COLUMN_TYPE:            2 cases (5.9%)   — 2 documents
───────────────────────────────────────────
Total:                    34 cases           — 6 documents

P1 is the dominant pattern (64.7%).
P2 is the second pattern (23.5%).
P1 + P2 = 88.2% of all TRUE_G5.
P3 + P4 = 11.8% (minority patterns, not replicated in new data).
```

---

## 3. Per-Pattern Detailed Analysis

### 3.1 P1 / NP1 — CAPTION_VS_REFERENCE

```
historical_count:     10  (original)
new_count:            12  (from Human Validation, all CE2-like)
total:                22
document_count:        4  (arxiv_2402.18619, is11_resnet, is11_efficientnet, is11_med_001)
ce2_like_count:       14  (2 original CE2 + 12 new CE2-like)

evidence_structure:
  fig_prefix:         True (17/22 with data, 5 N/A from original structure research)
  drawing_extent:     True (17/22 with data, 5 N/A)
  vertical_relation:  below/above (spatial relation present)
  x_overlap:          True/False (variable)
  distance_pt:        20-57pt (proximate but not zero)

semantic_boundary_structure:
  Structural Evidence:   FIG prefix + drawing extent + spatial relation + proximity
  Structural Claim:      "This text is spatially associated with this drawing"
  Semantic Identity:     UNRESOLVED — "Is this text a caption or an in-text reference?"
  → CE2 PROVES this: same structural evidence → different judgments (YES=caption, NO=reference)

whether_cross_document:  YES (4 documents, max single doc = 59%)
whether_cross_case:      YES (22 distinct case instances)
whether_repeated:        YES (22 cases, same boundary type)
whether_new_variation:   NO (NP1 is same pattern as P1, CE2-like is same boundary)

REPLICATION: YES — P1 replicated with 12 new cases across 4 documents.
```

### 3.2 P2 / NP2 — TEXT_ROLE

```
historical_count:      4  (original, all Type_B_negative)
new_count:             4  (from Human Validation, all Type_B_negative, fig_prefix=False)
total:                 8
document_count:        5  (arxiv_2402.18619, is11_efficientnet, is11_med_001, is11_resnet, is11_cs_001)
ce2_like_count:        0  (none CE2-like)

evidence_structure:
  fig_prefix:         False (8/8 = 100%) — NO lexical signal
  drawing_extent:     True (8/8 = 100%)
  vertical_relation:  above/below (spatial relation present)
  x_overlap:          False (variable)
  distance_pt:        proximate

semantic_boundary_structure:
  Structural Evidence:   drawing extent + spatial relation + proximity
  Structural Claim:      "This text is spatially associated with this drawing"
  Semantic Identity:     UNRESOLVED — "What is the role of this text? (axis label? annotation? body text?)"
  No lexical signal (no "Fig." prefix) → machine cannot determine text role from structure alone

whether_cross_document:  YES (5 documents, max single doc = 38%)
whether_cross_case:      YES (8 distinct case instances)
whether_repeated:        YES (8 cases, same boundary type)
whether_new_variation:   YES — NP2 is a sub-variant of P2:
  Historical P2: Type_B_negative, fig_prefix=mixed (some True, some False)
  New NP2:       Type_B_negative, fig_prefix=False (100% no lexical signal)
  → NP2 is a STRONGER form of P2 (no lexical signal at all)
  → BUT same boundary type (text role ambiguity)
  → NOT a completely new pattern

REPLICATION: YES — P2 replicated with 4 new cases across 5 documents.
             New sub-variant NP2 discovered (stronger form, no lexical signal).
```

### 3.3 P3 — AUTHOR_NAME_RECOGNITION

```
historical_count:      2  (original: IND-AMB-033, IND-AMB-049)
new_count:             0  (NOT replicated in new data)
total:                 2
document_count:        1  (ind_arxiv_bio2 only)
ce2_like_count:        0

evidence_structure:
  This is a TEXT-TEXT boundary, not text-drawing.
  Structural Evidence:   text position + text format
  Semantic Identity:     UNRESOLVED — "Is 'Le.' an author name or a text fragment?"
  Requires world knowledge (author name recognition)

whether_cross_document:  NO (1 document only — ind_arxiv_bio2)
whether_cross_case:      YES (2 cases)
whether_repeated:        YES (2 cases, same boundary type)
whether_new_variation:   N/A (no new cases)

REPLICATION: NO — P3 NOT replicated.
  Only 2 cases, 1 document, 0 new cases.
  Cannot determine if P3 generalizes.
  P3 may be document-specific or domain-specific (biotech).
```

### 3.4 P4 — COLUMN_SEMANTIC_TYPE

```
historical_count:      2  (original: PH02-SPECIFICITY-VALUE-COL, PH02-SPECIFICITY-CS001)
new_count:             0  (NOT replicated in new data)
total:                 2
document_count:        2  (is11_resnet, is11_cs_001)
ce2_like_count:        0

evidence_structure:
  This is a TABLE boundary, not text-drawing.
  Structural Evidence:   column position + cell values
  Semantic Identity:     UNRESOLVED — "Is this column row-numbers or data-values?"
  Requires understanding of table semantics

whether_cross_document:  YES (2 documents, but 1 case per document)
whether_cross_case:      YES (2 cases)
whether_repeated:        YES (2 cases, same boundary type)
whether_new_variation:   N/A (no new cases)

REPLICATION: NO — P4 NOT replicated.
  Only 2 cases, 1 per document, 0 new cases.
  Cross-document (2 docs) but sample too small (1 case per doc).
  Cannot determine if P4 generalizes.
```

### 3.5 Pattern Replication Summary

```
Pattern   | Historical | New | Total | Docs | Replicated?
----------|-----------:|----:|------:|-----:|:-----------
P1        |         10 |  12 |    22 |    4 | YES
P2        |          4 |   4 |     8 |    5 | YES (with new sub-variant NP2)
P3        |          2 |   0 |     2 |    1 | NO
P4        |          2 |   0 |     2 |    2 | NO (insufficient sample)
----------|-----------|-----|-------|------|----------
Total     |         18 |  16 |    34 |    6 |

PATTERN_REPLICATION_RATE = 2/4 = 50%
  → P1 and P2 replicated with new data.
  → P3 and P4 NOT replicated (no new cases).
  → P1 + P2 account for 88.2% of all TRUE_G5.
  → Replication is concentrated in the two dominant patterns.
```

---

## 4. Boundary Structure Verification

### 4.1 The Core Boundary Structure

```
Expected structure (from Boundary Structure Research):

  Structural Evidence (complete)
    ↓
  Structural Claim (supported)
    ↓
  Semantic Identity / Semantic Role (unresolved)
    ↓
  TRUE_G5

The key question: Does this structure hold across all 34 TRUE_G5?
```

### 4.2 Verification Results

```
Pattern   | Structural Evidence Complete | Semantic Identity Unresolved | Structure Holds
----------|:----------------------------:|:----------------------------:|:---------------
P1        |                  22/22 (100%) |                   22/22 (100%) | YES
P2        |                   8/8  (100%) |                    8/8  (100%) | YES
P3        |                   2/2  (100%) |                    2/2  (100%) | YES
P4        |                   2/2  (100%) |                    2/2  (100%) | YES
----------|------------------------------|------------------------------|----------------
Total     |                  34/34 (100%) |                   34/34 (100%) | YES

STRUCTURAL_EVIDENCE_SUFFICIENT = 34/34 (100%)
SEMANTIC_BOUNDARY_PRESENT = 34/34 (100%)

→ No TRUE_G5 has drawing_extent=False (0/34).
→ All TRUE_G5 have structural evidence complete.
→ All TRUE_G5 have semantic identity unresolved.
→ Boundary Structure is STABLE across all 34 cases and all 4 patterns.
```

### 4.3 The CAPTION_VS_REFERENCE Example (P1)

```
For P1 (22 cases, the dominant pattern):

  Spatial relation (above/below)     → Structural Evidence
  + drawing extent (present)         → Structural Evidence
  + text context (5 tokens)          → Structural Evidence
  + document context (page layout)   → Structural Evidence
  ─────────────────────────────────────
  = Structural Claim: "This text is spatially associated with this drawing"
  ─────────────────────────────────────
  BUT: Semantic Identity UNRESOLVED:
       "Is this text a CAPTION (describes the figure) or a REFERENCE (mentions the figure)?"

  CE2 PROOF:
    is11_efficientnet_p8_467_415: identical evidence → NO (reference)
    is11_resnet_p6_478_168:       identical evidence → YES (caption)
    → Same structural evidence, different semantic identity.
    → Structural evidence CANNOT resolve semantic identity.
    → This IS the G5 boundary.

  This structure is:
    - Stable across 22 cases
    - Stable across 4 documents
    - Stable across 14 CE2-like cases (direct proof)
    - Not a single-document artifact
```

---

## 5. CE2 Special Analysis

### 5.1 Strict CE2 Analysis (per user requirements)

```
CE2-like cases (combined): 14
  Original CE2:    2 (is11_efficientnet_p8_467_415=NO, is11_resnet_p6_478_168=YES)
  New CE2-like:   12 (from Human Validation, Tier 1a)

Questions to answer (NO claims of "perfect" or "universal"):
```

### 5.2 Q1: 新增 CE2-like cases 是否仍然表现为 TRUE_G5？

```
YES — in current sample.
  12 new CE2-like cases → 12 TRUE_G5.
  All 12 classified as TRUE_G5 through A/B/C/D validation.
  
  Cannot claim "always TRUE_G5" — only "12/12 in current sample".
```

### 5.3 Q2: Evidence 是否仍然高度相同？

```
YES — within each CE2 config group, structural evidence is identical.

  Config Group 1 (6 cases): fig=True|dep=True|VR=below|XO=True|type=ambiguous_fragment
    → 6 cases share EXACT same structural evidence.
    → 3 documents (arxiv_2402.18619, is11_efficientnet, is11_resnet).

  Config Group 2 (3 cases): fig=True|dep=True|VR=below|XO=False|type=ambiguous_fragment
    → 3 cases share EXACT same structural evidence.
    → 2 documents (arxiv_2402.18619, is11_efficientnet).

  Config Group 3 (3 cases): fig=True|dep=True|VR=above|XO=True|type=ambiguous_fragment
    → 3 cases share EXACT same structural evidence.
    → 3 documents (arxiv_2402.18619, is11_med_001, is11_resnet).

  Evidence identical: CONFIRMED within each group.
```

### 5.4 Q3: Human judgment 是否仍然存在差异？

```
YES — within each CE2 config group, judgments differ.

  Config Group 1: judgments = {YES, NO} → 5 YES, 1 NO
  Config Group 2: judgments = {YES, NO} → 2 YES, 1 NO
  Config Group 3: judgments = {YES, NO} → 2 YES, 1 NO

  Judgment different: CONFIRMED in all 3 groups.
```

### 5.5 Q4: 差异是否继续来自 semantic content？

```
YES — structural evidence is identical within each group, so the differentiator
      MUST be something beyond structural evidence.

  Within each group:
    - fig_prefix: identical (True)
    - drawing_extent: identical (True)
    - vertical_relation: identical
    - x_overlap: identical
    - distance_pt: similar (within pt range)
    - case_type: identical (ambiguous_fragment)

  The ONLY remaining differentiator is the semantic content of the text:
    - What does the text actually say?
    - Does it describe the figure (caption) or mention it (reference)?
    - This requires reading and understanding the text content.

  Difference source: semantic content. CONFIRMED (by elimination).
```

### 5.6 Q5: 是否存在反例？

```
CE2 COUNTEREXAMPLE SEARCH:
  Looking for: CE2-like pattern (same evidence → different judgment) that is NOT TRUE_G5.

  Non-TRUE_G5 cases from Human Validation (2 total):
    arxiv_2402.18619_p18_432_93:  MACHINE_RESOLVABLE, ce2_like=NO → NOT a counterexample
    is11_resnet_p4_320_146:       FALSE_G5 (G3),       ce2_like=NO → NOT a counterexample

  CE2_COUNTEREXAMPLE_COUNT = 0

  In current sample (n=14 CE2-like cases):
    → No counterexample observed.
    → Cannot claim "universally true" or "100% generalization".
    → Can only state: "no counterexample observed in current sample (n=14)."
    → A larger sample might reveal counterexamples.
    → The CE2-like pattern is a STRONG G5 indicator in current data,
       but its generalization boundary is unknown.
```

---

## 6. Cross-Document Validation

### 6.1 Document Independence Check

```
6 documents with TRUE_G5:
  arxiv_2402.18619:    16 cases (47.1%)  ← largest, but < 50%
  is11_resnet:          7 cases (20.6%)
  is11_efficientnet:    5 cases (14.7%)
  ind_arxiv_bio2:       2 cases (5.9%)
  is11_cs_001:          2 cases (5.9%)
  is11_med_001:         2 cases (5.9%)

CROSS_DOCUMENT_G5 = 6

No single document exceeds 50% → G5 is NOT a single-document artifact.
5 of 6 documents have ≥2 TRUE_G5 cases → cross-document repetition confirmed.

BUT: arxiv_2402.18619 contributes 47.1% — significant concentration.
     This document is a multi-page arxiv paper with many figures.
     The concentration is expected (more figures = more caption-reference ambiguities).
     The pattern (P1) is still cross-document (4 docs).
```

### 6.2 Same-Document vs Cross-Document

```
P1_CAPTION_VS_REFERENCE:
  Cross-document: YES (4 docs)
  Same-document repetition: YES (arxiv_2402.18619 has 9-13 cases of P1)
  → P1 appears both within single documents AND across documents.
  → Cross-document generalization: supported for P1.

P2_TEXT_ROLE:
  Cross-document: YES (5 docs)
  Same-document repetition: YES (arxiv_2402.18619 has 3 cases of P2)
  → P2 appears across 5 documents — strongest cross-document pattern.
  → Cross-document generalization: supported for P2.

P3_AUTHOR_NAME:
  Cross-document: NO (1 doc only — ind_arxiv_bio2)
  Same-document repetition: YES (2 cases in 1 document)
  → P3 is single-document only. Cannot claim cross-document generalization.
  → P3 may be domain-specific (biotech arxiv).

P4_COLUMN_TYPE:
  Cross-document: YES (2 docs — is11_resnet, is11_cs_001)
  BUT: only 1 case per document → insufficient sample.
  → Cross-document technically yes, but sample too small to confirm.
```

### 6.3 Cross-Document Summary

```
P1: cross-document (4 docs) — STABLE
P2: cross-document (5 docs) — STABLE
P3: single-document (1 doc) — NOT cross-document stable
P4: cross-document (2 docs) — INSUFFICIENT SAMPLE

→ G5 boundary is cross-document stable for the two DOMINANT patterns (P1, P2).
→ P3 and P4 cannot be confirmed as cross-document stable.
→ Cross-document generalization is PARTIAL: supported for P1+P2, not for P3+P4.
```

---

## 7. New Pattern Check

### 7.1 Check for New Boundary Patterns

```
Examined all 34 TRUE_G5 cases for:
  - New Semantic Boundary type (beyond caption/reference, text-role, author-name, column-type)
  - New Evidence Structure (beyond text-drawing, text-text, table)
  - New Human Requirement (beyond semantic identity resolution)
  - New Task Type (beyond Text-Drawing Association)

Result:
  NEW_BOUNDARY_PATTERN = 0

  All 34 TRUE_G5 cases fit existing P1-P4 patterns:
    P1 (CAPTION_VS_REFERENCE): 22 cases — text-drawing, caption vs reference
    P2 (TEXT_ROLE):             8 cases — text-drawing, axis/annotation/body role
    P3 (AUTHOR_NAME):           2 cases — text-text, name vs fragment
    P4 (COLUMN_TYPE):           2 cases — table, row-number vs data-value

  NP2 (TEXT_ROLE_WITHOUT_LEXICAL_SIGNAL) is a SUB-VARIANT of P2:
    - Same boundary type (text role ambiguity)
    - Same evidence structure (text-drawing)
    - Same human requirement (semantic identity resolution)
    - Difference: no "Fig." lexical signal (stronger form)
    - NOT a new pattern.

  No new semantic boundary, evidence structure, human requirement, or task type discovered.
```

### 7.2 Implication

```
The G5 boundary space appears to be NARROW:
  - 4 patterns cover all 34 TRUE_G5 cases.
  - P1 + P2 cover 88.2%.
  - No new pattern emerged from 16 new cases.

  This could mean:
    (a) The G5 boundary is genuinely narrow (few semantic boundary types exist in this task), OR
    (b) The test data doesn't cover enough diversity to reveal new patterns, OR
    (c) The screening (Tier 1) was biased toward P1/P2 patterns.

  Cannot determine which explanation is correct from current data.
```

---

## 8. Three-State Distinction

### 8.1 The Three States

```
State 1: Evidence Insufficient (G1/G2/G3/G4)
  → Evidence Recovery / Organization / Presentation / Integration gap exists.
  → After fixing the gap, the case may become machine-resolvable.
  → NOT a semantic boundary.

  Combined count (from all gates):
    G1 (Observation Coverage):  32 cases (5+27)
    G2 (Evidence Organization): 70 cases (6+64)
    G3 (Evidence Presentation): 28 cases (0+27+1)
    G4 (Consumer Integration):  12 cases (0+12)
    Total: 142 cases

State 2: Evidence Sufficient + Machine Resolvable
  → Structural evidence is sufficient for machine to determine the answer.
  → No semantic boundary. Current capability covers this.

  Combined count: 65 cases (64 from Generalization V1 + 1 from Human Validation)

State 3: Evidence Sufficient + Semantic Boundary (TRUE_G5)
  → Evidence is structurally complete.
  → BUT semantic identity / semantic role cannot be determined from evidence alone.
  → Human semantic judgment required.
  → Current capability boundary does NOT cover this.

  Combined count: 34 cases (18 original + 16 new)
```

### 8.2 Distribution

```
                    Count    Percentage
State 1 (G1-G4):      142       57.7%
State 2 (Machine):     65       26.4%
State 3 (TRUE_G5):     34       13.8%
────────────────────────────────────────
Total:                241      100.0%

TRUE_G5 is 13.8% of all cases examined.
This is a MINORITY but STABLE state.
```

### 8.3 The Key Question: "Human 为什么需要介入？"

```
Human intervention is needed when and only when:
  State 3 is reached: Evidence Sufficient + Semantic Boundary.

  In this state:
    - Evidence is NOT the problem (structural evidence is complete).
    - Machine capability is NOT the problem (capability works for State 2).
    - The problem is: semantic identity cannot be resolved from evidence alone.

  This is NOT about:
    - Teaching machine to imitate Human's YES/NO answer (Answer Learning — prohibited).
    - Building a G5 detector (Implementation — prohibited).

  This IS about:
    - Recognizing that a stable, observable boundary exists.
    - The boundary has a specific structure (Structural Evidence Sufficient + Semantic Unresolved).
    - The boundary is cross-document for dominant patterns (P1, P2).
    - Human judgment at this boundary is about Evidence Sufficiency, not about the answer.
```

---

## 9. Descriptive vs Deployable Distinction (Critical)

### 9.1 What IS Supported (Descriptive Generalization)

```
A. Multiple documents exhibit the same boundary structure:
   "Evidence Complete + Semantic Identity Unresolved"
   → 6 documents, 34 cases, 4 patterns.
   → This is a RESEARCH FINDING.

B. The dominant patterns (P1, P2) replicate across documents:
   → P1: 4 docs, 22 cases.
   → P2: 5 docs, 8 cases.
   → This is a RESEARCH FINDING.

C. CE2-like pattern (same evidence → different judgment) is observed:
   → 14 cases, 4 docs, 3 config groups.
   → No counterexample in current sample (n=14).
   → This is a RESEARCH FINDING.

D. Boundary Structure is stable:
   → 34/34 cases have Structural Evidence Complete + Semantic Unresolved.
   → 0/34 cases have drawing_extent=False.
   → This is a RESEARCH FINDING.
```

### 9.2 What is NOT Supported (Deployable Auto-Classification)

```
A. Automatic TRUE_G5 detection for arbitrary new cases:
   → NOT implemented.
   → NOT claimed.
   → The drawing_extent_present signal (from Governance gate) was UNVALIDATED
      on new boundary cases in Generalization V1 (0 new UNCERTAIN).
   → CE2-like screening requires finding mixed-judgment groups, which itself
      requires Human judgments — circular dependency.

B. Automatic routing to Human:
   → NOT implemented.
   → NOT claimed.
   → Descriptive findings do NOT equal deployable routing rules.

C. Universal CE2 = TRUE_G5 claim:
   → NOT claimed.
   → "No counterexample in n=14" ≠ "universally true".
   → Larger sample needed.

D. P3/P4 generalization:
   → NOT supported (P3 single-document, P4 insufficient sample).
```

---

## 10. Q&A (Research Questions)

### Q1: G5 是否能够在 NEW TRUE_G5 上复现？

```
YES — for dominant patterns.
  P1 (CAPTION_VS_REFERENCE): 10 → 22 (12 new cases replicated).
  P2 (TEXT_ROLE): 4 → 8 (4 new cases replicated).
  P3 (AUTHOR_NAME): 2 → 2 (0 new, NOT replicated).
  P4 (COLUMN_TYPE): 2 → 2 (0 new, NOT replicated).

  G5 replicates on P1 and P2 (88.2% of all TRUE_G5).
  G5 does NOT replicate on P3 and P4 (11.8%).
  → PARTIAL replication.
```

### Q2: G5 是否跨 document 稳定存在？

```
YES — for P1 and P2.
  P1: 4 documents (max single doc = 59%, balanced).
  P2: 5 documents (max single doc = 38%, balanced).
  Total: 6 documents with TRUE_G5.

  NO — for P3.
  P3: 1 document only (ind_arxiv_bio2).

  INSUFFICIENT — for P4.
  P4: 2 documents, 1 case each.

  → Cross-document stable for dominant patterns, not for minority patterns.
```

### Q3: 历史 Boundary Pattern 是否能够在新的 TRUE_G5 中复现？

```
PARTIAL.
  P1: REPLICATED (12 new cases, 4 docs).
  P2: REPLICATED (4 new cases, 5 docs, with new sub-variant NP2).
  P3: NOT REPLICATED (0 new cases).
  P4: NOT REPLICATED (0 new cases).

  PATTERN_REPLICATION_RATE = 2/4 = 50%.
```

### Q4: 是否出现新的 Boundary Pattern？

```
NO.
  NEW_BOUNDARY_PATTERN = 0.
  All 34 TRUE_G5 fit existing P1-P4.
  NP2 is a sub-variant of P2, not a new pattern.
```

### Q5: 是否存在"Evidence Sufficient + Semantic Boundary"的稳定结构？

```
YES.
  STRUCTURAL_EVIDENCE_SUFFICIENT = 34/34 (100%).
  SEMANTIC_BOUNDARY_PRESENT = 34/34 (100%).
  No TRUE_G5 has drawing_extent=False (0/34).

  The structure "Structural Evidence Complete → Semantic Identity Unresolved"
  holds across all 34 cases, 4 patterns, 6 documents.

  This is the most stable finding of this gate.
```

### Q6: 是否能够开始支持 Machine 知道"Evidence 已够但 Capability 不足，应交 Human"？

```
DESCRIPTIVELY: YES.
  The three-state distinction is observable and stable:
    State 1 (Evidence Insufficient): 142 cases.
    State 2 (Machine Resolvable): 65 cases.
    State 3 (Semantic Boundary): 34 cases.

  State 3 has a stable structure:
    - Structural evidence complete.
    - Semantic identity unresolved.
    - Human judgment required.
    - Cross-document (for P1, P2).

DEPLOYABLY: NO.
  This gate does NOT implement:
    - Automatic State 3 detection.
    - Routing rules.
    - Confidence scores.
    - G5 classifier.
  
  The finding SUPPORTS the concept that Machine could eventually recognize
  "Evidence sufficient but capability boundary insufficient → defer to Human."
  But the mechanism for this recognition is NOT designed or implemented.
  
  This is a RESEARCH FINDING, not a DEPLOYABLE CAPABILITY.
```

---

## 11. Metrics Summary

```
NEW_TRUE_G5_COUNT = 16
CROSS_DOCUMENT_G5 = 6
PATTERN_REPLICATION_RATE = 2/4 (50%)
NEW_PATTERN_COUNT = 0
CE2_NEW_CASE_COUNT = 12
CE2_NEW_TRUE_G5_COUNT = 12
CE2_COUNTEREXAMPLE_COUNT = 0
STRUCTURAL_EVIDENCE_SUFFICIENT = 34/34 (100%)
SEMANTIC_BOUNDARY_PRESENT = 34/34 (100%)
MACHINE_RESOLVABLE = 65
INDETERMINATE = 0
```

---

## 12. Generalization Status Determination

### 12.1 Criteria Evaluation

```
SUPPORTED requires:
  ✓ Multiple independent documents:     6 documents (PASS)
  ✓ Multiple new cases:                 16 new TRUE_G5 (PASS)
  ✓ At least one pattern repeated:      P1 + P2 replicated (PASS)
  ✓ Boundary structure stable:          34/34 structure holds (PASS)
  ✓ Sufficient new TRUE_G5:             16 ≥ 3 (PASS)
  ✗ No significant limitations:         LIMITATIONS EXIST (FAIL)

CONDITIONALLY_SUPPORTED requires:
  ✓ Core criteria pass:                 All 5 core criteria pass (PASS)
  ✓ Major pattern replicates:           P1 (dominant, 64.7%) replicates (PASS)
  ✓ Cross-document for major pattern:   P1 in 4 docs, P2 in 5 docs (PASS)
  ✗ All patterns replicate:             P3, P4 do not replicate (PARTIAL)
  ✗ No sample limitations:              CE2 n=14, P3 n=2, P4 n=2 (LIMITED)
```

### 12.2 Limitations

```
L1: P3 NOT replicated (0 new cases, 1 document).
    → P3 may be document-specific or domain-specific.
    → Cannot confirm P3 generalizes.

L2: P4 NOT replicated (0 new cases, 2 documents, 1 case each).
    → P4 sample too small to confirm generalization.
    → 1 case per document is insufficient.

L3: CE2 sample limited (n=14).
    → No counterexample observed, but n=14 is small.
    → Cannot claim CE2-like is "universal" or "perfect".
    → Can only state: "no counterexample in current sample."

L4: Academic domain only.
    → All 6 documents are academic papers (arxiv, is11).
    → Biotech/FinEdu domains had 0 G5 in prior gates.
    → Cross-domain G5 generalization untested.

L5: arxiv_2402.18619 concentration (47.1%).
    → Single document contributes 47.1% of TRUE_G5.
    → Not > 50%, but significant.
    → P1 cross-document is still valid (4 docs), but concentration exists.

L6: No new pattern discovered.
    → Could mean G5 boundary is genuinely narrow.
    → Could mean test data lacks diversity.
    → Cannot determine which.

L7: No deployable mechanism designed.
    → This gate is descriptive, not deployable.
    → No automatic detection, routing, or classification implemented.
```

### 12.3 Determination

```
G5_GENERALIZATION_STATUS = CONDITIONALLY_SUPPORTED

Reason:
  All 5 core criteria PASS:
    - 6 independent documents
    - 16 new TRUE_G5
    - P1 + P2 (dominant patterns, 88.2%) replicated
    - Boundary structure stable (34/34)
    - Sufficient new TRUE_G5 (16 ≥ 3)

  BUT 7 limitations exist:
    - P3/P4 not replicated
    - CE2 sample limited (n=14)
    - Academic domain only
    - arxiv concentration (47.1%)
    - No new pattern (boundary may be narrow)
    - No deployable mechanism
    - Descriptive only, not deployable

  → G5 generalization is CONDITIONALLY supported:
    The dominant patterns (P1, P2) show stable cross-document generalization
    with a stable boundary structure. But minority patterns (P3, P4) do not
    replicate, the CE2 sample is limited, and the domain is narrow.
    
  This is NOT "SUPPORTED" because:
    - Not all patterns replicate (P3, P4).
    - CE2 generalization boundary unknown (n=14).
    - Academic domain only.
    
  This is NOT "NOT_SUPPORTED" because:
    - P1 (dominant, 64.7%) replicates across 4 documents.
    - P2 (second, 23.5%) replicates across 5 documents.
    - Boundary structure is 100% stable.
    - 16 new TRUE_G5 confirm the boundary.
```

---

## 13. Over-Design Audit

```
  O1: Modified P1-P7? → NO
  O2: Modified TLD? → NO
  O3: Modified DGF/DEF? → NO
  O4: Modified layout analyzer? → NO
  O5: Modified parser? → NO
  O6: Modified runtime? → NO
  O7: Modified capability registry? → NO
  O8: Modified frozen baseline? → NO
  O9: Modified existing research files? → NO
  O10: Trained model? → NO
  O11: Imported external dataset? → NO
  O12: Built G5 detector? → NO
  O13: Built Boundary classifier? → NO
  O14: Built routing rule? → NO
  O15: Built scoring/confidence/ranking? → NO
  O16: Built recommendation system? → NO
  O17: Auto-generated Capability? → NO
  O18: Auto-registered Capability? → NO
  O19: Modified Runtime Authority? → NO
  O20: Implemented deployable classification? → NO

  ALL CHECKS: FALSE
  OVER_DESIGN_AUDIT = PASS
```

---

## 14. Capability Expansion (NOT Implemented)

```
Long-term roadmap (for reference only, NOT implemented in this gate):

  G5 Boundary Identification (DONE — descriptive)
    → Human Teaching (NOT STARTED)
    → Validated Evidence (NOT STARTED)
    → Capability Eligibility (NOT STARTED)
    → Capability Learning (NOT STARTED)
    → Capability Registration (NOT STARTED)
    → Replay (NOT STARTED)
    → Shadow Execution (NOT STARTED)
    → Controlled Rollout (NOT STARTED)

  This gate only validates that the G5 boundary has a stable, generalizable structure.
  All subsequent phases remain NOT STARTED.
  No capability was created, learned, or registered.
```

---

## 15. Files Created

```
tmp/g5_boundary_generalization_v2.md   (this file)
tmp/g5_boundary_generalization_v2.json (structured data)
tmp/g5_boundary_generalization_v2.csv  (34 cases × 15 fields)
```

---

## 16. Final Status

```
STATUS = COMPLETE
GATE = G5_BOUNDARY_GENERALIZATION_V2
G5_GENERALIZATION_STATUS = CONDITIONALLY_SUPPORTED
NEW_TRUE_G5_COUNT = 16
CROSS_DOCUMENT_G5 = 6
PATTERN_REPLICATION_RATE = 2/4 (50%)
NEW_PATTERN_COUNT = 0
CE2_NEW_CASE_COUNT = 12
CE2_NEW_TRUE_G5_COUNT = 12
CE2_COUNTEREXAMPLE_COUNT = 0
STRUCTURAL_EVIDENCE_SUFFICIENT = 34/34 (100%)
SEMANTIC_BOUNDARY_PRESENT = 34/34 (100%)
MACHINE_RESOLVABLE = 65
INDETERMINATE = 0
SYSTEM_MODIFIED = FALSE
FROZEN_BASELINE_INTACT = TRUE
STOP = TRUE
```

---

## STOP

```
G5_BOUNDARY_GENERALIZATION_V2 is COMPLETE.

SUMMARY:
  - Combined TRUE_G5: 34 (18 original + 16 new)
  - 6 documents, 4 patterns
  - P1 (CAPTION_VS_REFERENCE): 22 cases, 4 docs — REPLICATED
  - P2 (TEXT_ROLE): 8 cases, 5 docs — REPLICATED (with new sub-variant NP2)
  - P3 (AUTHOR_NAME): 2 cases, 1 doc — NOT REPLICATED
  - P4 (COLUMN_TYPE): 2 cases, 2 docs — NOT REPLICATED
  - Boundary Structure: 34/34 stable (Structural Evidence Complete + Semantic Unresolved)
  - CE2-like: 14 cases, 0 counterexample (n=14, cannot claim universal)
  - No new pattern discovered
  - Three-state distinction: 142 G1-G4 / 65 Machine / 34 TRUE_G5
  - G5_GENERALIZATION_STATUS = CONDITIONALLY_SUPPORTED

KEY FINDING:
  The G5 boundary ("Evidence Sufficient + Semantic Identity Unresolved")
  has a STABLE and OBSERVABLE structure that replicates across documents
  for the two dominant patterns (P1: caption vs reference, P2: text role).
  
  BUT:
  - Minority patterns (P3, P4) do not replicate.
  - CE2-like generalization boundary is unknown (n=14, no counterexample).
  - Academic domain only.
  - This is DESCRIPTIVE generalization, NOT deployable auto-classification.

  The finding supports the CONCEPT that Machine could eventually recognize
  "Evidence sufficient but capability boundary insufficient → defer to Human."
  But the mechanism for this recognition is NOT designed or implemented.

  不得自动进入 Implementation。
  不得训练模型。
  不得创建 Capability。
  不得修改系统。
  STOP = TRUE.
```
