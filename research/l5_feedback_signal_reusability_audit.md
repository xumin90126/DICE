# Human Feedback Signal Reusability Audit

## READ-ONLY Audit — No Implementation

**Date**: 2026-09-12
**Scope**: Audit existing Human Feedback data for reusable signal evidence
**Authority**: L5 Human Validation
**Governance**: READ_ONLY=TRUE, DESIGN_ONLY=TRUE, FROZEN_BASELINE=INTACT, IMPLEMENTATION_AUTHORIZED=FALSE

---

## 1. Executive Conclusion

> **当前数据是否已经证明存在 Reusable Human Feedback Signal？**

### **PARTIAL**

当前数据中**存在**一个达到 R3 级别（Repeated + Evidence-linked Candidate）的候选信号 CS1-DIFFERENT_TABLE_COLUMNS，以及两个达到 R2 级别（Repeated Feedback Expression）的候选信号 CS2-SENTENCE_BOUNDARY 和 CS3-FIGURE_CAPTION_CONTINUITY。

但**没有**任何一个候选信号达到 R5（Human-Validated Reusable Signal）或更高。

**关键限制**：
- n=1 参与者 → 跨参与者验证 NOT AVAILABLE
- Human 始终看到页面图像 → 无法区分信号是 image-grounded 还是 evidence-grounded
- TLD 存在假阴性（AMB-313, AMB-462）→ 证据链接不完整
- 所有候选信号存在 Semantic Leap 风险 → 不能自动转为规则
- 无验证工作流 → 无法升级为 Validated Reusable Knowledge

**结论**：存在 Reusable Signal 的**候选证据**，但不足以证明 Reusable Signal 的**存在**。当前阶段是 Candidate Discovery，不是 Validation，更不是 Learning。

---

## 2. Human Feedback Inventory

### Complete Inventory (27 judgments)

| Type | Count | Description |
|---|---|---|
| A. Direct Decision | 23 | KEEP_SEPARATE/MERGE/UNKNOWN without explanation |
| B. Explicit Correction | 0 | Human disagrees with System (System≠GT=0, no corrections) |
| C. Semantic/Structural Explanation | 4 | Voice feedback with reasoning |
| D. Evidence Relevance Feedback | 1 | UI button mismatch feedback (FB4) |
| E. Boundary Feedback | 1 | "类别还是不一样的" (FB4) |
| F. Uncertainty / UNKNOWN | 0 | No UNKNOWN selections |
| G. Voice Feedback | 4 | Free-text/voice transcripts |

### Voice Feedback Detail

| FB# | Workflow | Item | Decision | Time | Content Summary |
|---|---|---|---|---|---|
| FB1 | B | grp\|16bfcb76b820 | KEEP_SEPARATE | 132.9s | Per-instance analysis: 2 sentence boundaries, 2 table columns, 2 captions |
| FB2 | B | grp\|885e943771cd | KEEP_SEPARATE | 66.5s | Group-level: "表格中同一行的不同列数据" |
| FB3 | B | grp\|1ad8a7b55945 | KEEP_SEPARATE | 73.8s | Group-level: "同一表格中的内容...不同列" |
| FB4 | C | grp\|16bfcb76b820 | KEEP_SEPARATE | 116.5s | UI feedback + "类别还是不一样的" (boundary signal) |

### Key Observation

23/27 judgments are **Direct Decision only** (no explanation). Only 4/27 contain reusable information. Of these 4, only FB1 contains per-instance reasoning; FB2 and FB3 are group-level generalizations; FB4 is mixed (UI feedback + boundary observation).

---

## 3. Feedback → Evidence Mapping

### FB1: Per-Instance Breakdown (grp|16bfcb76b820, 6 members)

| Instance | Human Feedback | Case | Evidence Available | Linkage | Potential Signal |
|---|---|---|---|---|---|
| 例子1 | "前一句话的后半部分和后一句话的前半部分" | AMB-005 | text_a ends with ".", text_b starts with capital, is_in_table=True | **PARTIALLY_SUPPORTED** (text pattern + TLD, but TLD says table — confound) | CS2: SENTENCE_BOUNDARY |
| 例子2 | "同一个表格中的不同列的名称" | AMB-313 | is_in_table=**False**, different_cell=**False** (TLD false negative!) | **EVIDENCE_UNSUPPORTED** (Human sees table in image, TLD doesn't detect it) | CS1: DIFFERENT_TABLE_COLUMNS |
| 实例3 | "认可他们是同一内容单元" | AMB-414 | text_a="FIG. 9:", is_in_table=False | **PARTIALLY_SUPPORTED** (text pattern only, no structural evidence) | CS3: FIGURE_CAPTION_CONTINUITY |
| 实例4 | "认可他们是同一语义单元" | AMB-422 | text_a="FIG. 12:", is_in_table=False | **PARTIALLY_SUPPORTED** (text pattern only) | CS3: FIGURE_CAPTION_CONTINUITY |
| 例子5 | "一句话的后半部分和下一句话的前半部" | AMB-519 | text_a ends with ".", text_b starts with capital, is_in_table=False | **EVIDENCE_SUPPORTED** (text pattern, no table confound) | CS2: SENTENCE_BOUNDARY |
| 例子6 | "同一张表格的不同列的名称" | AMB-530 | is_in_table=True, different_cell=True | **EVIDENCE_SUPPORTED** (TLD fully supports) | CS1: DIFFERENT_TABLE_COLUMNS |

### FB2: Group-Level (grp|885e943771cd, 4 members)

| Case | Evidence | Linkage | Potential Signal |
|---|---|---|---|
| AMB-024 | is_in_table=True, different_cell=True | EVIDENCE_SUPPORTED | CS1 |
| AMB-074 | is_in_table=True, different_cell=True | EVIDENCE_SUPPORTED | CS1 |
| AMB-462 | is_in_table=**False**, different_cell=**False** (TLD false negative!) | EVIDENCE_UNSUPPORTED | CS1 |
| AMB-522 | is_in_table=True, different_cell=True | EVIDENCE_SUPPORTED | CS1 |

### FB3: Group-Level (grp|1ad8a7b55945, 11 members)

| Case | Evidence | Linkage |
|---|---|---|
| AMB-034 | is_in_table=True, different_cell=True | EVIDENCE_SUPPORTED |
| AMB-130 | is_in_table=True, different_cell=True | EVIDENCE_SUPPORTED |
| AMB-135 | is_in_table=True, different_cell=True | EVIDENCE_SUPPORTED |
| AMB-262 | is_in_table=True, different_cell=True | EVIDENCE_SUPPORTED |
| AMB-346 | is_in_table=True, different_cell=True | EVIDENCE_SUPPORTED |
| AMB-350 | is_in_table=True, different_cell=True | EVIDENCE_SUPPORTED |
| AMB-457 | is_in_table=True, different_cell=True | EVIDENCE_SUPPORTED |
| AMB-467 | is_in_table=True, different_cell=True | EVIDENCE_SUPPORTED |
| AMB-483 | is_in_table=True, different_cell=True | EVIDENCE_SUPPORTED |
| AMB-505 | is_in_table=True, different_cell=True | EVIDENCE_SUPPORTED |
| AMB-514 | is_in_table=True, different_cell=True | EVIDENCE_SUPPORTED |

### FB4: Mixed (UI + Boundary)

| Content | Type | Reusable? |
|---|---|---|
| "判断选项不贴合" | D. Evidence Relevance Feedback | NO (process feedback, one-off) |
| "类别还是不一样的" | E. Boundary Feedback | YES (boundary signal about aggregation limitation) |

### Linkage Summary

| Linkage Status | Count | Cases |
|---|---|---|
| EVIDENCE_SUPPORTED | 15 | AMB-024, 074, 130, 135, 262, 346, 350, 457, 467, 483, 505, 514, 034, 519, 530 |
| PARTIALLY_SUPPORTED | 4 | AMB-005 (table+sentence confound), AMB-414, AMB-422 (text pattern only) |
| EVIDENCE_UNSUPPORTED | 2 | AMB-313, AMB-462 (TLD false negative — Human sees table, TLD doesn't) |

---

## 4. Candidate Signal Table

| candidate_id | CS1 | CS2 | CS3 |
|---|---|---|---|
| **Signal Name** | DIFFERENT_TABLE_COLUMNS | SENTENCE_BOUNDARY | FIGURE_CAPTION_CONTINUITY |
| **Feedback Examples** | "表格中同一行的不同列数据", "不同列的名称" | "前一句话的后半部分和后一句话的前半部分" | "认可他们是同一内容单元" |
| **Feedback Sources** | FB1 (2 instances), FB2 (4 cases), FB3 (11 cases) | FB1 (2 instances) | FB1 (2 instances) |
| **Case Count** | 17 | 2 | 2 |
| **Document Count** | 3 (resnet, efficientnet, cs_001) | 2 (resnet, cs_001) | 1 (med_001) |
| **Page Count** | 3+ | 2 | 1 |
| **Evidence Linkage** | TLD is_in_table + different_cell (15/17 supported) | Text pattern: A ends with ".", B starts with capital (2/2) | Text pattern: A starts with "FIG." (2/2) |
| **Evidence Type** | Structural (TLD) | Text pattern (P1 text) | Text pattern (P1 text) |
| **Semantic Stability** | HIGH — "不同列" consistently used across 3 feedbacks | MEDIUM — 2 instances, same phrasing | MEDIUM — 2 instances, same concept |
| **Negative Evidence** | 2 TLD false negatives (AMB-313, AMB-462); no is_in_table=True + MERGE case | NOT TESTABLE (no MERGE case with period-ending text_a) | NOT TESTABLE (no KEEP_SEPARATE case with FIG. prefix) |
| **Boundary Evidence** | is_in_table=False appears in both MERGE (captions) and KEEP_SEPARATE (sentences) | AMB-005 has table confound (is_in_table=True) | None |
| **UNKNOWN Evidence** | 0 UNKNOWN cases | 0 UNKNOWN cases | 0 UNKNOWN cases |
| **Cross-Document** | YES (3 documents) | YES (2 documents) | NO (1 document) |
| **Cross-Participant** | NOT AVAILABLE (n=1) | NOT AVAILABLE (n=1) | NOT AVAILABLE (n=1) |
| **Image-Grounded Confound** | YES — Human saw page image showing table | YES — Human saw page image showing prose | YES — Human saw page image showing figure |
| **Reusability Status** | REPEATED_CANDIDATE (R3) | REPEATED_CANDIDATE (R2) | REPEATED_CANDIDATE (R2) |

### Additional Signal: CS4-CATEGORY_HETEROGENEITY

| candidate_id | CS4 |
|---|---|
| **Signal Name** | CATEGORY_HETEROGENEITY |
| **Feedback** | "每一个处的类别还是不一样的" (FB4) |
| **Type** | E. Boundary Feedback (NOT decision signal) |
| **Case Count** | 1 group (6 members with 3 semantic categories) |
| **Evidence** | grp\|16bfcb76b820 contains: 2 sentence boundaries, 2 table columns, 2 captions |
| **Reusability Status** | ONE-OFF (R1) — but important boundary observation |
| **Note** | This is a signal about the LIMITATION of structural aggregation, not a reusable decision signal |

---

## 5. Signal Recurrence Analysis

### What Actually Repeats?

| Dimension | CS1 | CS2 | CS3 |
|---|---|---|---|
| Keyword recurrence | "表格" ×3, "不同列" ×3 | "前一句话" ×1, "后一句话" ×1 | "同一内容单元" ×1, "同一语义" ×1 |
| Feedback recurrence | 3/4 feedbacks | 1/4 feedbacks | 1/4 feedbacks |
| Case recurrence | 17/21 cases | 2/21 cases | 2/21 cases |
| Evidence recurrence | TLD=True in 15/17 | Period+capital in 2/2 | FIG. prefix in 2/2 |
| Document recurrence | 3 documents | 2 documents | 1 document |

### Keyword Recurrence vs Evidence-Grounded Signal Recurrence

**Critical Finding**: "表格" appears in 3/4 voice feedbacks, but this may be **keyword recurrence** rather than **evidence-grounded signal recurrence**.

**Reason**: Human always saw the page image. The page image visually shows a table. Human mentions "表格" because they **see** it in the image, not necessarily because they read TLD's `is_in_table=True`.

**Evidence for evidence-grounded (not just keyword)**:
1. Human used "表格" to JUSTIFY the decision (causal, not descriptive)
2. Human distinguished table cases from sentence and caption cases
3. Human used "不同列" specifically — positional distinction, not just "表格"
4. TLD is_in_table=True correlates with Human's table mention in 15/17 cases

**Evidence for image-grounded (confound)**:
1. 2 cases (AMB-313, AMB-462) where TLD=False but Human said "表格" → Human saw table in image that TLD missed
2. No condition where Human saw evidence WITHOUT image → cannot isolate image effect
3. Human never referenced evidence field names → no proof they read structural evidence

**Conclusion**: CS1 recurrence is **likely evidence-grounded** but **cannot be confirmed** without an image-free condition. This is a **critical experimental confound** that must be resolved before claiming evidence-grounded reusability.

---

## 6. Semantic Leap / Overreach Audit

| Candidate | Human Said | Safe Interpretation | Semantic Leap | Verdict |
|---|---|---|---|---|
| CS1 | "表格中同一行的不同列数据" | "A and B are in different structural positions within a multi-column aligned structure" | "if is_in_table=True AND different_cell=True then KEEP_SEPARATE" | **SEMANTIC LEAP** — converts observation into decision rule |
| CS2 | "前一句话的后半部分和后一句话的前半部分" | "A ends with a period, B starts with a capital — they may span a sentence boundary" | "if text_a ends with period then KEEP_SEPARATE" | **SEMANTIC LEAP** — converts text pattern into decision rule; also misses decimal numbers |
| CS3 | "认可他们是同一内容单元" | "A starts with 'FIG.' and B follows — they may form a continuous caption" | "if text_a starts with 'FIG.' then MERGE" | **SEMANTIC LEAP** — converts caption pattern into merge rule |
| CS4 | "类别还是不一样的" | "Structural group contains multiple semantic categories" | "structural grouping is insufficient for semantic grouping" | **SAFE** — this is a boundary observation, not a decision rule |

### Semantic Leap Detection Principle

```
Human observation:  "这两个在表格的不同列" (structural observation)
     ↓
Safe candidate:     "A and B are in different structural positions" (structural fact)
     ↓
SEMANTIC LEAP:      "if is_in_table AND different_cell → KEEP_SEPARATE" (decision rule)
```

The leap occurs when a **structural observation** is converted into a **decision rule**. The safe boundary is: System may present the structural fact as context; Human makes the decision.

**All 3 decision-type candidates (CS1, CS2, CS3) have Semantic Leap risk.** They are SAFE only if presented as evidence cues (L5.10 safe translations), NOT as decision rules.

---

## 7. Current Reusability Level

```
R0 = No observable reusable signal
R1 = One-off feedback only
R2 = Repeated feedback expression
R3 = Repeated + Evidence-linked candidate
R4 = Cross-case reusable candidate
R5 = Human-validated reusable signal
R6 = Reused on new cases
R7 = Reuse produces measured improvement
```

| Candidate | Level | Justification | Blockers to Next Level |
|---|---|---|---|
| CS1 DIFFERENT_TABLE_COLUMNS | **R3** | 3 feedbacks, 17 cases, 3 documents, TLD supports 15/17 | n=1 (no cross-participant), image confound, TLD false negatives, no validation workflow |
| CS2 SENTENCE_BOUNDARY | **R2** | 2 instances, 2 documents, text pattern supports 2/2 | Only 2 cases, no negative evidence, image confound |
| CS3 FIGURE_CAPTION_CONTINUITY | **R2** | 2 instances, 1 document, text pattern supports 2/2 | Only 2 cases, 1 document, no negative evidence, image confound |
| CS4 CATEGORY_HETEROGENEITY | **R1** | 1 feedback, 1 group | One-off boundary observation |

### DICE Overall Position: **R3** (for CS1 only)

- CS1 is the strongest candidate, reaching R3
- CS2 and CS3 are at R2
- R4 is blocked by: n=1, image confound, no cross-participant validation
- R5 is blocked by: no validation workflow
- R6–R7: not reachable without R5

---

## 8. Learning Readiness

| Stage | Status | Evidence |
|---|---|---|
| Feedback Capture | **IMPLEMENTED** | 27 judgments, 4 voice feedbacks, auto-save |
| Evidence Linkage | **PARTIAL** | case_id→evidence link exists; feedback_text→evidence_field link missing; 2 TLD false negatives |
| Signal Candidate Discovery | **PARTIAL** | 3 candidates identified (this audit); but no automated discovery mechanism; candidates identified by manual analysis |
| Human Validation | **MISSING** | No validation workflow for candidates |
| Reuse | **MISSING** | No mechanism to apply validated signals to new cases |
| Measured Improvement | **MISSING** | No baseline comparison, no reuse outcome measurement |

### Learning = TRUE?

**NO.** Current state is at **Storage + Manual Candidate Discovery**. No validation, no reuse, no measured improvement.

---

## 9. ValidationRecord Sufficiency

| Field | Present? | Blocks Current Research? |
|---|---|---|
| feedback_text | YES | NO |
| case_id | YES | NO |
| decision | YES | NO |
| time_seconds | YES | NO |
| evidence_refs | NO | NO (can be derived from case_id→sampling frame) |
| signal_type | NO | NO (candidates identified manually in this audit) |
| signal_status | NO | NO (no validation workflow exists) |
| scope | NO | NO (no validated signals to scope) |
| boundary | NO | NO (no validated signals to bound) |
| recurrence_count | NO | NO (recurrence analyzed manually in this audit) |
| provenance_chain | PARTIAL | NO (participant_id + case_id sufficient for audit) |
| validation_status | NO | NO (no validation workflow exists) |

**Conclusion**: Current ValidationRecord is **sufficient for audit-level research**. Missing fields would become necessary only if:
- Automated signal extraction is implemented (needs signal_type, signal_status)
- Validation workflow is created (needs validation_status, scope, boundary)
- Reuse mechanism is built (needs recurrence_count, provenance_chain complete)

None of these are currently authorized. **No schema change needed.**

### CURRENT REPRESENTATION GAP

The gap is NOT in the schema. The gap is in the **process**: no mechanism to extract, validate, or reuse signals. This is a process gap, not a data structure gap.

---

## 10. Next Evidence Required

### To Move from R3 → R4 (Cross-case reusable candidate)

| Priority | Evidence Needed | Why |
|---|---|---|
| 1 | **n>3 participants** on same 21 cases | Verify CS1 recurrence is not participant-specific |
| 2 | **Image-free condition** (evidence cues only, no page image) | Distinguish image-grounded from evidence-grounded |
| 3 | **TLD false negative resolution** (AMB-313, AMB-462) | Ensure evidence linkage is complete |

### To Move from R4 → R5 (Human-validated reusable signal)

| Priority | Evidence Needed | Why |
|---|---|---|
| 4 | **Validation workflow** (Human reviews candidate, accepts/rejects) | Grant reusable semantic authority |
| 5 | **Negative cases** (is_in_table=True + MERGE) | Test false positive rate of CS1 |
| 6 | **Conflict cases** (System proposes MERGE, evidence says table) | Test override behavior |

### To Move from R5 → R6 (Reused on new cases)

| Priority | Evidence Needed | Why |
|---|---|---|
| 7 | **New case corpus** (not the original 21) | Test generalization |
| 8 | **Reuse mechanism** (show validated signal for matching cases) | Apply validated knowledge |

### To Move from R6 → R7 (Measured improvement)

| Priority | Evidence Needed | Why |
|---|---|---|
| 9 | **Baseline comparison** (same cases without reuse) | Measure effort reduction |
| 10 | **Quality measurement** (accuracy, false accept/reject) | Prove quality maintained |

### Minimum Evidence to Justify Automated Signal Extraction

**Not until**: n>3 participants + cross-participant CS1 recurrence confirmed + image-free condition tested + at least 1 negative case (is_in_table=True + MERGE) found and Human correctly overrides.

---

## 11. Anti-Overdesign Gate

| Gate | Question | Answer | Justification |
|---|---|---|---|
| G1 | Need Feedback Engine? | **NO** | 3 candidates identified by manual analysis; no automation needed at R3 |
| G2 | Need Signal object? | **NO** | Candidates expressed as audit findings; no system object needed until R5 |
| G3 | Need Pattern? | **NO** | CS1 is a candidate, not a pattern; patterns require n>10 + statistical validation |
| G4 | Need ML/LLM extraction? | **NO** | Manual analysis sufficient at current scale (4 feedbacks, 27 judgments) |
| G5 | Need new database/schema? | **NO** | ValidationRecord sufficient for audit; gap is process, not schema |
| G6 | Need new Human workflow? | **NO** | Validation workflow is FUTURE_CANDIDATE, needed only at R4→R5 transition |
| G7 | Existing ValidationRecord + Evidence sufficient? | **YES** for audit-level research; **NO** for implementation (process gap) |
| G8 | Minimum evidence for automated extraction? | n>3 + cross-participant recurrence + image-free test + 1 negative case |

---

## 12. Final Conclusion

### Reusable Signal Existence

**PARTIAL — One candidate (CS1) reaches R3, but is not validated.**

CS1-DIFFERENT_TABLE_COLUMNS has the strongest evidence:
- 3 voice feedbacks mention "表格"/"不同列"
- 17/21 cases have table-related feedback
- TLD is_in_table=True in 15/17 cases
- 3 documents, cross-document recurrence
- Human used it causally (to justify KEEP_SEPARATE)

But CS1 is **NOT** a Validated Reusable Signal because:
- n=1 → no cross-participant validation
- Image confound → cannot confirm evidence-grounded
- TLD false negatives → evidence linkage incomplete
- No validation workflow → no Human-validated status
- Semantic Leap risk → cannot be converted to rule

### Designation

- CS1: **Potential Reusable Signal Candidate** (NOT Reusable Knowledge)
- CS2: **Potential Reusable Signal Candidate** (weaker, R2)
- CS3: **Potential Reusable Signal Candidate** (weaker, R2)
- CS4: **Boundary Observation** (not a decision signal)

### What This Audit Proves

1. **Reusable signal candidates DO exist** in current feedback data
2. **Evidence linkage IS possible** (TLD maps to Human's "表格" observation)
3. **Recurrence IS observable** (CS1 appears in 3/4 feedbacks, 17/21 cases)
4. **Semantic stability IS present** (consistent use of "不同列" across feedbacks)

### What This Audit Does NOT Prove

1. Cross-participant validity (n=1)
2. Evidence-grounded (not image-grounded) basis
3. Generalization beyond current corpus
4. False positive resistance
5. Learning = TRUE

---

## 13. Governance

```
READ_ONLY = TRUE
DESIGN_ONLY = TRUE

CODE_MODIFICATION = 0
UI_MODIFICATION = 0
DATA_MUTATION = 0
GT_MODIFICATION = 0
TLD_MODIFICATION = 0
ATOMIC_MODIFICATION = 0
AGGREGATION_MODIFICATION = 0
COMPRESSION_MODIFICATION = 0
VALIDATION_RECORD_MODIFICATION = 0

NEW_PRIMITIVE = 0
NEW_CONTRACT = 0
NEW_ARCHITECTURE = 0
PATTERN_ENGINE = 0
FEEDBACK_ENGINE = 0
LEARNING_ENGINE = 0
ML_TRAINING = 0
LLM_FINE_TUNING = 0
SIGNAL_OBJECT = 0
NEW_SCHEMA = 0

FUTURE_CANDIDATES:
  - Signal Extraction Process (after n>3 + cross-participant recurrence)
  - Validation Workflow (after R4 confirmed)
  - Reuse Mechanism (after R5 validated)
  - Outcome Measurement (after R6 reuse)

PRODUCTION = FALSE
FROZEN_BASELINE = INTACT
IMPLEMENTATION_AUTHORIZED = FALSE
STOP = TRUE
```

### Evidence Classification

- This audit = **B-class** (engineering analysis based on real pilot data)
- CS1 candidate existence = **B-class** (derived from P01 analysis, real feedback)
- CS1 reusability = **C-class** (hypothesis, not validated, blocked by n=1 + image confound)
- CS2/CS3 candidates = **C-class** (insufficient recurrence, only 2 cases each)
- CS4 boundary observation = **B-class** (directly observed in feedback, real)

### Pilot Limitations Preserved

```
n = 1 participant
27 judgments (21 A + 3 B + 3 C)
4 voice feedbacks (all B/C phase, 0 in A phase)
MERGE = 2 (both captions)
Conflict = 0
System ≠ GT = 0
UNKNOWN = 0
Image confound: Human always saw page image
TLD false negatives: 2/21 (AMB-313, AMB-462)
```
