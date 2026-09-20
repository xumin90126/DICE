# Candidate Semantic Coherence / Candidate Value Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY / NO MODIFICATION / FROZEN INTACT / STOP

---

## 1. Executive Summary

```
FINAL_STATUS = CANDIDATES_HAVE_SUFFICIENT_COHERENCE

KEY FINDING:
  DICE Candidate Construction is PURELY GEOMETRIC:
    same_y_band + horizontal_gap (8-50pt) + line_obs ≤ 15 + w_b ≥ 15pt
    NO semantic coherence check during construction
    NO TLD called during construction
    NO IS-01/IS-02/IS-11 computed during construction

  But: in 114 GT'd cases (45 IS-11 + 69 P7):
    CONSTRUCTION_FALSE_POSITIVE = 0/114 (0%)
    VALID_CANDIDATE = 101/114 (89%)
    STRUCTURALLY_RELATED_BUT_UNCERTAIN = 13/114 (11%)

  → Candidates DO have structural/semantic coherence
  → The geometric construction, while crude, produces valid candidates
  → Reviewers ALWAYS see a structural relation (table, prose, figure, reference)

HUMAN FEEDBACK:
  F2 (Boundary Validation) = 45/45 (100%)
  F5 (Construction Correction) = 0/45 (0%)
  → Human is judging BOUNDARY, NOT correcting CANDIDATE CONSTRUCTION
  → Human is NOT telling System "this candidate shouldn't exist"

INFORMATION GAIN:
  IG-0 (no new info, machine correct) = 25/45 (55%)
  IG-1 (unused existing evidence) = 16/45 (35%)
  IG-2 (new info, content unit definition) = 4/45 (8%)
  IG-3 (reusable signal) = 0/45 (0%)
  → 0 reusable Candidate Construction signal

PRIMARY_BOTTLENECK = B (Evidence Organization) / D (Consumer Integration)
  → NOT Candidate Construction (0% FP)
  → NOT Human Semantic Judgment (0% persistent ambiguity)
  → 35% of feedback points to existing evidence not used by machine

STOP = TRUE
```

> **DICE 当前的 Candidate 虽然由纯几何条件构造（same_y_band + gap 8-50pt），但在 114 个有 GT 的案例中 Construction False Positive = 0%。所有 Candidate 都具有结构/语义一致性——reviewer 总能看到某种关系（table column, sentence boundary, figure caption, reference entry）。Human Feedback 是 100% Boundary Validation（F2），0% Construction Correction（F5）。Human 不是在告诉 System "这个 Candidate 不应该存在"，而是在判断一个已合理构造的 Candidate 的边界。Information Gain 中 0% 为 IG-3（可复用信号）。当前瓶颈不是 Candidate Construction，而是 Evidence Organization / Consumer Integration（35% IG-1）。**

---

## 2. Research Questions

### RQ1: 当前 Candidate 的基本构造依据是什么？

**PURELY GEOMETRIC.** Candidate = any two same-y-band text fragments with:
- horizontal gap between 8-50pt
- line_obs_count ≤ 15
- w_b ≥ 15pt

No semantic coherence check. No TLD. No IS-01/IS-02/IS-11. Pure geometric pairing.

### RQ2: Candidate 内部是否具有足够的 Semantic/Structural Coherence?

**YES — in GT'd cases.** 89% VALID_CANDIDATE, 11% STRUCTURALLY_RELATED_BUT_UNCERTAIN, 0% CONSTRUCTION_FALSE_POSITIVE.

### RQ3: Candidate Quality 分类?

| Category | IS-11 (45) | P7 (69) | Total (114) |
|---|---|---|---|
| VALID_CANDIDATE | 41 (91%) | 60 (86%) | 101 (89%) |
| STRUCTURALLY_RELATED_BUT_UNCERTAIN | 4 (9%) | 9 (13%) | 13 (11%) |
| CONSTRUCTION_FALSE_POSITIVE | 0 (0%) | 0 (0%) | 0 (0%) |
| INSUFFICIENT_EVIDENCE | 0 | 0 | 0 |
| UNKNOWN | 0 | 0 | 0 |

### RQ4: Human 当前反馈的价值是什么?

**F2 (Boundary Validation) — 100%.** Human is judging the boundary of a valid candidate, NOT correcting candidate construction.

### RQ5: Human Feedback 是否包含 Candidate Construction 改进信号?

**NO.** 0% F5 (Construction Correction). 0% IG-3 (reusable signal). Human feedback contains boundary information, not construction information.

---

## 3. Candidate Construction Trace

### 3.1 Construction Mechanism

```
Document
  ↓ P1 (text extraction)
  ↓ P2 (geometry: bbox, same_y_band, h_gap)
  ↓ Candidate Generation Trigger:
       same_y_band = True
       AND 8.0 ≤ h_gap ≤ 50.0
       AND line_obs_count ≤ 15
       AND w_b ≥ 15.0
  ↓ Candidate = (text_a, text_b) pair
  ↓ NO TLD, NO IS-01/IS-02/IS-11, NO semantic check
```

### 3.2 Construction Output

- **545 candidates** from 4 documents (60 pages)
- **45 sampled** for IS-11 GT (stratified by geometry)
- **69 cases** in P7 independent evaluation (different sampling)
- **83 selected** for potential evaluation case set

### 3.3 Key Observation

> **Candidate Construction does NOT check whether A and B belong to the same structural/semantic unit. It only checks geometric proximity. Yet in 114 GT'd cases, 0% are Construction False Positives.**

This means: the geometric criteria (same_y_band + gap 8-50) are SUFFICIENT to produce structurally coherent candidates in the current corpus. Text fragments on the same line with a moderate gap almost always have some structural relation (same table row, same sentence, same caption, same reference).

---

## 4. Candidate Semantic Coherence Analysis

### 4.1 Coherence Types Found

| Coherence Type | Count | Description |
|---|---|---|
| STRUCTURAL (table column/cell) | 39 | Both reviewers identify as table cells/columns |
| STRUCTURAL (figure caption) | 2 | Both reviewers identify as figure caption parts |
| TEXTUAL (sentence boundary) | 4 | Both reviewers see sentence boundary (disagree on standard) |
| STRUCTURAL (agreed, other) | 0 | Other agreed structural relation |

### 4.2 Coherence Hierarchy Check

```
Geometry Relation (same_y_band + h_gap)
  → Structural Relation (same table row, same caption)
    → Semantic Coherence (same content unit)
```

**Result:** In all 45 cases, geometry relation → structural relation → semantic coherence. The hierarchy holds. No case where geometry relation exists but structural/semantic coherence is absent.

> **Geometry Relation → Structural Relation → Semantic Coherence: validated for 45/45 cases.**

---

## 5. Focus Case Analysis

### AMB-135

```
Construction: same_y_band + h_gap=30.0 → geometric pairing
Candidate: '4' + 'MBConv6, k5x5'
Quality: VALID_CANDIDATE (both reviewers: different table columns)
Feedback: F2 (Boundary Validation) — human says KEEP_SEPARATE
IG: IG-1 (machine FP, human used table structure evidence machine didn't)
→ Candidate IS valid. Machine decision was wrong. NOT construction error.
```

### AMB-032

```
Construction: same_y_band + h_gap=33.9 → geometric pairing
Candidate: '-' + '8.43'
Quality: VALID_CANDIDATE (both reviewers: different table cells)
Feedback: F2 (Boundary Validation, reviewer) / F4 (Evidence Sufficiency, P722 participant)
IG: IG-0 (machine TN, TLD correct)
→ Candidate IS valid. P722 participant couldn't verify → evidence organization gap.
```

### AMB-375

```
Construction: same_y_band + h_gap=9.7 → geometric pairing
Candidate: '[23].' + 'Each'
Quality: STRUCTURALLY_RELATED_BUT_UNCERTAIN (sentence boundary, standard ambiguous)
Feedback: F2 (Boundary Validation) — reviewer disagreement (sentence vs paragraph)
IG: IG-2 (content unit definition not in current evidence)
→ Candidate IS valid (both see sentence boundary). Standard gap, not construction error.
```

### AMB-414

```
Construction: same_y_band + h_gap=18.1 → geometric pairing
Candidate: 'FIG. 9:' + 'Left:'
Quality: VALID_CANDIDATE (both reviewers: figure caption parts)
Feedback: F2 (Boundary Validation) — human says MERGE
IG: IG-0 (machine ABSTAIN, but candidate is valid)
→ Candidate IS valid. Machine couldn't determine (no figure detector).
```

### AMB-462

```
Construction: same_y_band + h_gap=12.0 → geometric pairing
Candidate: 'WGe' + 'Avg.'
Quality: VALID_CANDIDATE (both reviewers: different table headers)
Feedback: F2 (Boundary Validation) — human says KEEP_SEPARATE
IG: IG-1 (TLD detected wrong table, human used text content)
→ Candidate IS valid. TLD partial failure. NOT construction error.
```

### AMB-519

```
Construction: same_y_band + h_gap=10.0 → geometric pairing
Candidate: 'facto backbone for open-source LLMs.' + 'To embrace the open-source community, our design'
Quality: STRUCTURALLY_RELATED_BUT_UNCERTAIN (sentence boundary, standard ambiguous)
Feedback: F2 (Boundary Validation) — reviewer disagreement
IG: IG-2 (content unit definition)
→ Candidate IS valid (both see sentence boundary). Standard gap.
```

---

## 6. Human Feedback Type Distribution

| Feedback Type | Count | % | Description |
|---|---|---|---|
| F1 (Candidate Validity) | 0 | 0% | Human judging if candidate should exist |
| **F2 (Boundary Validation)** | **45** | **100%** | **Human judging boundary of valid candidate** |
| F3 (Semantic Interpretation) | 0 | 0% | Human doing higher-level semantic judgment |
| F4 (Evidence Sufficiency) | 2* | — | P722 participant couldn't determine (AMB-032, AMB-375) |
| F5 (Construction Correction) | 0 | 0% | Human correcting candidate construction |

*F4 is participant-level (P722), not reviewer-level. Reviewers agreed on both cases.

> **Human Feedback is 100% F2 (Boundary Validation). Human is NOT correcting Candidate Construction.**

---

## 7. Feedback Information Gain

| IG Level | Count | % | Description |
|---|---|---|---|
| IG-0 (no new info) | 25 | 55% | Machine already correct (TN), human confirms |
| IG-1 (unused evidence) | 16 | 35% | Human uses existing evidence machine didn't use |
| IG-2 (new info) | 4 | 8% | Human provides content unit definition (prose) |
| IG-3 (reusable signal) | 0 | 0% | No reusable Candidate Construction signal |

### IG-1 Analysis (35%)

All 16 IG-1 cases are where:
- TLD missed table → machine ABSTAIN
- Human used text content + visual context to determine boundary
- Evidence EXISTS in P1/P2 but machine (IS-11 consumer) didn't use it

> **IG-1 = Consumer/Integration Gap (D). Human points to existing evidence not used by machine. NOT construction signal.**

### IG-2 Analysis (8%)

All 4 IG-2 cases are prose sentence boundary disagreements:
- Human provides "content unit = sentence" definition
- This is STANDARD_GAP (from previous audit)
- NOT construction signal — candidate IS valid

> **IG-2 = Standard Gap. Human provides content unit definition. NOT construction signal.**

### IG-3 Analysis (0%)

**ZERO reusable Candidate Construction signals found.**

- No F5 (Construction Correction) → no construction error to learn from
- No case where Human says "this candidate shouldn't exist"
- All candidates are valid → no construction improvement signal

> **Human Feedback does NOT contain Candidate Construction improvement information.**

---

## 8. Construction Correction Pattern Search

### 8.1 Search Result

**NO Construction Correction patterns found.**

In all 114 GT'd cases:
- 0 cases where Human says "these shouldn't be paired"
- 0 cases where reviewers see NO structural relation
- All candidates have at least one reviewer identifying a structural/semantic relation

### 8.2 Why No Construction Correction?

The geometric construction criteria (same_y_band + gap 8-50) are **coarse but sufficient**:
- Same-y-band + moderate gap → almost always same table row, same sentence, same caption, or same reference
- The criteria don't check semantic coherence, but the resulting pairs happen to be coherent
- This is because text fragments on the same line with a moderate gap are almost always structurally related in academic papers

### 8.3 Potential Risk

The 545-candidate universe has:
- 51 "OTHER" family candidates (9%) — might include unrelated pairs
- 326 "LOW" evaluation opportunity (60%) — might include trivially separable pairs
- But: without GT on these 500 candidates, Construction FP rate is UNKNOWN

> **In GT'd cases: 0% Construction FP. In unGT'd 500 candidates: UNKNOWN.**

---

## 9. Causal Chain Analysis

```
Candidate Construction (Geometric)
  → same_y_band + gap 8-50 → 545 candidates
  → NO semantic check
  → But 0% Construction FP in 114 GT'd cases

Candidate Quality (Structural Coherence)
  → 89% VALID, 11% UNCERTAIN, 0% FP
  → Candidates DO have coherence

Human Judgment (Boundary)
  → 91% boundary agreed, 9% boundary disputed
  → Human judges BOUNDARY, not CANDIDATE VALIDITY

Feedback
  → 100% F2 (Boundary Validation)
  → 0% F5 (Construction Correction)

Information Gain
  → 55% IG-0, 35% IG-1, 8% IG-2, 0% IG-3
  → 0% reusable construction signal

Potential Reusable Signal
  → NONE FOUND
  → Human feedback = boundary info, not construction info

Future Candidate Construction Improvement
  → NOT SUPPORTED by current Human Feedback
  → 0% F5, 0% IG-3
```

> **Human Feedback 主要发生在 BOUNDARY VALIDATION 层（F2, 100%），不在 CANDIDATE CONSTRUCTION 层（F5, 0%）。**

---

## 10. Error Assumption Check

### 1. 是否把 "Candidate 被 Human 判错" 错误理解成 "Boundary 判断问题"?

**Previous audits did NOT make this error.** All audits correctly identified boundary issues, not construction issues. This audit confirms: 0% Construction FP.

### 2. 是否很多 Human Feedback 在纠正 Candidate Construction?

**NO.** 0% F5. All Human Feedback is F2 (Boundary Validation).

### 3. 是否大量 Candidate 本身没有足够的 semantic coherence?

**NO.** 89% VALID, 0% FP. Candidates DO have coherence.

### 4. Candidate 质量低是否会掩盖 Construction 问题?

**N/A.** Candidate quality is NOT low (89% valid). No construction problem to mask.

### 5. Human Feedback 是否能改变未来 Candidate Construction?

**NO.** 0% F5, 0% IG-3. Human feedback contains boundary information, not construction information.

---

## 11. P722 UNKNOWN Cases — F4 (Evidence Sufficiency)

| Case | P722 Decision | Time | Expanded Fields | GT | Candidate Quality |
|---|---|---|---|---|---|
| AMB-032 | UNKNOWN | 45.9s | ALL 7 geometry fields | KEEP | VALID (table cell) |
| AMB-375 | UNKNOWN | 31.3s | ALL 7 geometry fields | KEEP | UNCERTAIN (prose) |

Both P722 UNKNOWN cases:
- Candidate IS valid (reviewers agreed)
- Participant couldn't determine boundary from exposed evidence
- This is Evidence Organization Gap (C), NOT Construction problem

> **P722 UNKNOWN = F4 (Evidence Sufficiency). Candidate valid, but evidence not organized for participant.**

---

## 12. Final Questions

### Q: DICE 当前真正需要优化的是什么?

**B. Evidence Organization** (primary)

- 0% Construction FP → Candidate Construction is NOT the problem
- 100% F2 → Human is doing Boundary Validation, not Construction Correction
- 35% IG-1 → Human points to existing evidence not used by machine
- This is the Consumer/Integration Gap (D) from previous audits

### Q: Human Feedback 是否包含 Candidate Construction 的 Learning Signal?

**NO.**

- 0% F5 (Construction Correction)
- 0% IG-3 (reusable signal)
- Human is validating boundaries, not correcting construction
- No case where Human says "this candidate shouldn't exist"

### Q: 如果不能，缺失的是什么信息?

The missing information is NOT about Candidate Construction. It's about:
1. **Evidence Organization** (35% IG-1): existing P2 evidence not used by IS-11 consumer
2. **Standard clarity** (8% IG-2): content unit definition for prose sentence boundary
3. **Table structure exposure** (2 P722 UNKNOWN): TLD cell info not exposed to participants

> **缺失的不是 Candidate Construction 信息，而是 Evidence Organization / Consumer Integration 信息。**

---

## 13. Candidate Value Distribution

### IS-11 (45 cases, with GT)

| Category | Count | % |
|---|---|---|
| VALID_CANDIDATE | 41 | 91% |
| STRUCTURALLY_RELATED_BUT_SEMANTICALLY_UNCERTAIN | 4 | 9% |
| CONSTRUCTION_FALSE_POSITIVE | 0 | 0% |
| INSUFFICIENT_EVIDENCE | 0 | 0% |
| UNKNOWN | 0 | 0% |

### P7 (69 cases, with GT)

| Category | Count | % |
|---|---|---|
| VALID_CANDIDATE | 60 | 86% |
| STRUCTURALLY_RELATED_BUT_SEMANTICALLY_UNCERTAIN | 9 | 13% |
| CONSTRUCTION_FALSE_POSITIVE | 0 | 0% |
| INSUFFICIENT_EVIDENCE | 0 | 0% |
| UNKNOWN | 0 | 0% |

### Combined (114 cases)

| Category | Count | % |
|---|---|---|
| VALID_CANDIDATE | 101 | 89% |
| STRUCTURALLY_RELATED_BUT_SEMANTICALLY_UNCERTAIN | 13 | 11% |
| CONSTRUCTION_FALSE_POSITIVE | 0 | 0% |

### 545-candidate universe (500 without GT)

| Category | Count | Note |
|---|---|---|
| GT'd | 114 | 0% Construction FP |
| UnGT'd | 431 | Construction FP UNKNOWN |
| "OTHER" family | 51 | Might include unrelated pairs |
| "LOW" eval opportunity | 326 | Might include trivially separable |

---

## 14. Final Output

```
FINAL_STATUS = CANDIDATES_HAVE_SUFFICIENT_COHERENCE

CANDIDATE_QUALITY_DISTRIBUTION:
  VALID_CANDIDATE: 101/114 (89%)
  STRUCTURALLY_RELATED_BUT_SEMANTICALLY_UNCERTAIN: 13/114 (11%)
  CONSTRUCTION_FALSE_POSITIVE: 0/114 (0%)
  INSUFFICIENT_EVIDENCE: 0/114 (0%)
  UNKNOWN: 0/114 (0%)

CONSTRUCTION_FALSE_POSITIVE_RATE = 0/114 (0%) [in GT'd cases]
  Note: 431/545 unGT'd candidates have UNKNOWN FP rate

HUMAN_FEEDBACK_TYPE_DISTRIBUTION:
  F1 (Candidate Validity): 0/45 (0%)
  F2 (Boundary Validation): 45/45 (100%)
  F3 (Semantic Interpretation): 0/45 (0%)
  F4 (Evidence Sufficiency): 2 [P722 participant-level]
  F5 (Construction Correction): 0/45 (0%)

FEEDBACK_INFORMATION_GAIN:
  IG-0: 25/45 (55%)
  IG-1: 16/45 (35%)
  IG-2: 4/45 (8%)
  IG-3: 0/45 (0%)

CANDIDATE_CONSTRUCTION_BOTTLENECK = NONE (0% Construction FP)
BOUNDARY_VALIDATION_BOTTLENECK = YES (100% F2, 35% IG-1)
EVIDENCE_ORGANIZATION_BOTTLENECK = YES (35% IG-1, 2 P722 F4)
POTENTIAL_LEARNING_SIGNAL_COUNT = 0
TRUE_REUSABLE_SIGNAL_FOUND = NO
CURRENT_LEARNING_LEVEL = L3 (unchanged)

PRIMARY_BOTTLENECK = B (Evidence Organization) / D (Consumer Integration)
  → NOT Candidate Construction (0% FP)
  → NOT Human Semantic Judgment (0% persistent ambiguity)
  → 35% of feedback points to existing evidence not used by machine

RECOMMENDED_NEXT_STEP = Continue READ-ONLY research on Evidence Organization
  → Focus: how to safely organize P2 evidence for IS-11 consumer when TLD fails
  → NOT: Candidate Construction improvement (no signal)
  → NOT: Learning Engine (no IG-3)
```

---

## 15. Key Principle Validation

> *Candidate 是 System 构造出来的研究对象，Human 不应该负责替 System 重建 Candidate。*

✓ 遵守：0% F5。Human 不需要重建 Candidate。所有 Candidate 都有结构一致性。

> *Human Feedback 的真正价值，不是告诉 System "这个答案错了"，而是帮助 System 逐渐学会 "什么东西值得被构造成 Candidate"。*

✓ 分析：当前 Human Feedback (100% F2) 的价值是 **Boundary Validation**，不是 **Construction Learning**。0% IG-3 意味着 Human Feedback 不包含 Construction 改进信号。

> *如果一个 Candidate 本身没有价值，那么让 Human 更高效地审阅它，并不能解决根本问题。*

✓ 分析：Candidate **有**价值（89% VALID, 0% FP）。问题不在 Candidate 价值，而在 **Machine Boundary Resolution**（35% IG-1 = evidence not used）。

---

## 16. Governance Gate

```
DICE_CORE_MODIFICATION              = NO
P1_P7_MODIFICATION                  = NO
P2_MODIFICATION                     = NO
TLD_MODIFICATION                    = NO
IS11_MODIFICATION                   = NO
GT_MODIFICATION                     = NO
SIGNAL_MODIFICATION                 = NO
EVIDENCE_CUE_MODIFICATION           = NO
LLM                                 = NO
NEW_OBSERVATION                     = NO
NEW_MODULE                          = NO
NEW_ENGINE                          = NO
RUNTIME_CHANGE                      = NO
CAPABILITY_CHANGE                   = NO
FROZEN_BASELINE                     = INTACT (drift=0/7)
FROZEN_EXPERIMENT                   = INTACT
IMPLEMENTATION_AUTHORIZED           = FALSE
EXPERIMENT_AUTHORIZED               = FALSE
FORMAL_EXPERIMENT                   = NOT_STARTED
STOP                                = TRUE
```

---

## 17. Data Sources & Caveats

```
Datasets used:
  1. IS-11 GT (45 cases) — with full reviewer rationales
  2. IS-11 Candidate Universe (545 candidates) — construction metadata
  3. P7 Independent (69 cases) — with boundary class and GT
  4. P722 Experiment (55 judgments) — participant behavior
  5. Potential Evaluation Case Set (83 selected from 545) — structure family

Overlap note:
  - IS-11 45 cases are a subset of 545 candidates
  - P7 69 cases are from a DIFFERENT corpus (ind_qbio_rna)
  - P722 55 judgments are on IS-11 45 cases (subset)
  - No double-counting across IS-11 and P7 (different corpora)

Retrospective labeling:
  - Candidate Quality classification is RETROSPECTIVE (based on GT)
  - NOT prospective evidence
  - Cannot be used as Learning Signal without independent validation

GT usage:
  - GT used ONLY for auditing candidate quality
  - GT NOT used for candidate construction (construction is geometry-only)
  - GT NOT used for any implementation
```

`STOP = TRUE`。
