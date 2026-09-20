# DICE Human Feedback → Reusable Signal → Future Case Reuse Feasibility Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY / DESIGN & EVIDENCE AUDIT
**Scope**: Judge whether DICE has achieved Human Feedback → Machine Learning → Future Reuse → Human Review Reduction

---

## 1. Executive Verdict

> **当前 DICE 尚未实现 Human Feedback → Machine Learning → Future Reuse → Human Review Reduction 闭环。**

DICE 当前处于 **L1 (Feedback Captured)** 到 **L2 (Evidence-Linked)** 之间。系统可以存储 Human Feedback 并部分关联到 Evidence，但没有Reusable Signal 验证工作流，没有 Future Case 复用机制，没有可测量的 Human Review 减少。

当前 DICE = **C1 (Compression) + C2 (Distillation)**，不是 C3 (Reusable Learning)。

---

## 2. Current Real Loop

```
Document                    EXISTS ✅ (4 PDFs, 60 pages)
    ↓
Evidence                    EXISTS ✅ (P1-P6, TLD, geometry, style, text)
    ↓
Candidate                   EXISTS ✅ (545 candidates, 48 working set)
    ↓
Human Review                EXISTS ✅ (2 reviewers × 45 cases + 48-case GT + P722 55 decisions)
    ↓
Feedback Capture            EXISTS ✅ (4 free-text + 90 reviewer rationales + 93 GT rationales)
    ↓
Evidence Linkage            PARTIAL ⚠️ (CS1: 17/35 TLD-linked in 45-set; CS2: 20/20; CS3: 12/12)
    ↓
Reusable Signal Extraction  PARTIAL ⚠️ (manual analysis identified 4 candidates, no automation)
    ↓
Human Validation of Signal  MISSING ❌ (no validation workflow, no cross-participant verification)
    ↓
Future Case Reuse           MISSING ❌ (no reuse mechanism, no matching engine)
    ↓
Measured Human Reduction    MISSING ❌ (no baseline, no comparison, no measurement)
    ↓
Quality Preservation        MISSING ❌ (cannot measure without reuse)
    ↓
Error Containment           MISSING ❌ (cannot measure without reuse)
    ↓
Boundary Preservation       MISSING ❌ (cannot measure without reuse)
```

**Summary**: 4 EXISTS, 2 PARTIAL, 6 MISSING. The loop is broken between Feedback Capture and Future Case Reuse.

---

## 3. Audit A: Human Feedback Content

### A1: What did Humans actually feedback?

| Source | Count | Type | Content |
|---|---|---|---|
| P01 Pilot | 4 | Free-text | "不同表格列", "句子前后半部分", "同一内容单元", UI feedback |
| Reviewer A | 45 | Rationale | "table columns", "sentence boundary", "figure caption" |
| Reviewer B | 45 | Rationale | "table columns", "sentence boundary", "figure caption" |
| GT Adjudication | 45 | Rationale | Adjudication explanation |
| 48-case GT | 48 | Rationale | GT rationale |
| P722 Experiment | 55 | Decision only | No free-text (UI didn't capture) |

### A2: Decision ≠ Explanation ≠ Reusable Signal

| Feedback Type | Example | Is it a Decision? | Is it an Explanation? | Is it a Reusable Signal? |
|---|---|---|---|---|
| "KEEP_SEPARATE" | P722 decision | ✅ YES | ❌ NO | ❌ NO |
| "different table columns" | Reviewer rationale | ❌ NO | ✅ YES | ⚠️ CANDIDATE (needs validation) |
| "前一句话的后半部分" | P01 feedback | ❌ NO | ✅ YES | ⚠️ CANDIDATE |
| "认可同一内容单元" | P01 feedback | ❌ NO | ✅ YES | ⚠️ CANDIDATE |

**Key finding**: All current feedback is either decisions or explanations. None has been validated as a reusable signal.

### Feedback → Evidence Mapping

| Feedback | Evidence Exists | Evidence Linkable | Cross-case Repeatable |
|---|---|---|---|
| "不同表格列" | ✅ TLD is_in_table + different_cell | ✅ YES (17/35 in 45-set, 7/16 in 48-set) | ✅ YES (51 cases, 4 docs) |
| "句子边界" | ✅ text_a period + text_b capital | ✅ YES (20/20) | ✅ YES (20 cases, 4 docs) |
| "图注连续性" | ✅ "FIG" marker in text_a | ✅ YES (12/12) | ✅ YES (12 cases, 2 docs) |
| "章节标题" | ✅ single digit + title text | ✅ YES (2/2) | ⚠️ WEAK (2 cases, 1 doc) |

---

## 4. Audit B: Evidence-Grounded Signal Candidates

### Candidate Signal Matrix

| Signal | Evidence | Cases | Docs | GT Distribution | Evidence Coverage |
|---|---|---|---|---|---|
| CS1: DIFFERENT_TABLE_COLUMNS | TLD is_in_table + different_cell | 51 | 4 | 49 KEEP, 2 MERGE | 24/51 (47%) |
| CS2: SENTENCE_BOUNDARY | text_a period + text_b capital | 20 | 4 | 20 KEEP | 20/20 (100%) |
| CS3: FIGURE_CAPTION_CONTINUITY | "FIG" in text_a | 12 | 2 | 11 MERGE, 1 KEEP | 12/12 (100%) |
| CS4: SECTION_HEADER | digit + title | 2 | 1 | 2 MERGE | 2/2 (100%) |

### 7-Point Check

| Signal | 5.1 Evidence-backed | 5.2 Repeatable | 5.3 Cross-doc | 5.4 Human-verifiable | 5.5 Boundary-preservable | 5.6 Future-applicable | Status |
|---|---|---|---|---|---|---|---|
| CS1 | ✅ YES | ✅ 51 cases | ✅ 4 docs | ✅ YES | ⚠️ PARTIAL | ✅ YES | CANDIDATE |
| CS2 | ✅ YES | ✅ 20 cases | ✅ 4 docs | ✅ YES | ⚠️ PARTIAL | ✅ YES | CANDIDATE |
| CS3 | ✅ YES | ✅ 12 cases | ⚠️ 2 docs | ✅ YES | ⚠️ PARTIAL | ✅ YES | CANDIDATE |
| CS4 | ✅ YES | ⚠️ 2 cases | ❌ 1 doc | ✅ YES | ⚠️ PARTIAL | ✅ YES | WEAK CANDIDATE |

### 5.5 Boundary-preservable Analysis

All four candidates can express YES/NO but struggle with:

| Boundary State | Can CS1 express? | Can CS2 express? | Can CS3 express? |
|---|---|---|---|
| Supported (YES) | ✅ | ✅ | ✅ |
| Unsupported (NO) | ✅ | ✅ | ✅ |
| Unknown | ❌ TLD has no "uncertain" | ❌ period+capital is binary | ❌ FIG is binary |
| Out-of-scope | ❌ | ❌ | ❌ |
| Conflict | ❌ | ❌ | ❌ |

**Critical gap**: No candidate signal can express UNKNOWN or CONFLICT. This means if a future case has ambiguous evidence, the signal would force a YES/NO answer, risking over-generalization.

---

## 5. Audit C: C1/C2/C3 Distinction

| Level | Description | DICE Status | What it does | What it doesn't do |
|---|---|---|---|---|
| C1 | Evidence Compression | ✅ IMPLEMENTED (L5.5) | Reduces 21→3 groups, less information to read | Does NOT reduce review count |
| C2 | Evidence Distillation | ✅ IMPLEMENTED (L5.10) | Raw Evidence → Cue, easier to understand | Does NOT reduce review count, may reduce time |
| C3 | Reusable Learning | ❌ NOT IMPLEMENTED | Feedback → Signal → Future Reuse → Review↓ | Everything missing |

**Current DICE = C1 + C2. NOT C3.**

### Why C2 ≠ Learning

C2 (Evidence Distillation / Cue) makes evidence easier for Human to understand. It may reduce decision time (E1: faster same judgment). But:

- Human still reviews every case (E2: review count unchanged)
- No validated knowledge is inherited (E3: no skip)
- No future case benefits from past feedback

**Distillation Gap ≠ Learning Gap** (as identified in previous iteration audit).

---

## 6. Audit D: Minimum Verifiable Loop Candidate

### Best Candidate: CS1 (DIFFERENT_TABLE_COLUMNS)

**Why CS1 is the strongest**:
- 51 cases across 4 documents
- TLD evidence exists and is computable
- Human feedback explicitly mentions "不同表格列"
- GT strongly supports (49/51 KEEP_SEPARATE)
- Evidence is structural (not semantic) — more stable

### But: No Currently Valid Reusable Signal

CS1 cannot become a validated reusable signal because:

1. **No validation workflow**: No mechanism for Human to validate "this signal applies to this evidence structure"
2. **No reuse mechanism**: No way to apply validated signal to future cases
3. **No baseline comparison**: Cannot measure "review with signal" vs "review without signal"
4. **Evidence coverage incomplete**: Only 47% of CS1 cases have TLD evidence (24/51)
5. **Boundary expression missing**: Cannot express UNKNOWN/CONFLICT
6. **n=1 participant**: Cross-participant validation not available
7. **Image confound**: Cannot distinguish image-grounded from evidence-grounded judgments

### What would be needed (NOT authorized this round):

```
Step 1: Define signal validation protocol
    → "Given evidence structure X, Human validates: does signal Y apply?"
Step 2: Validate CS1 on existing 51 cases
    → Human reviews: "TLD says different_cell — is KEEP_SEPARATE correct?"
Step 3: Apply validated signal to NEW cases (from 545 pool, not yet reviewed)
    → Signal proposes KEEP_SEPARATE for new TLD-matched cases
Step 4: Compare: Reuse ON vs Reuse OFF
    → Measure: review count, time, accuracy, UNKNOWN preservation
```

---

## 7. Audit E: Counterfactual Human Effort Reduction

| Signal | E1 (faster, same judgment) | E2 (still must re-judge) | E3 (inherit, skip review) | Classification |
|---|---|---|---|---|
| CS1 | ✅ YES — Cue "different cells" speeds decision | ✅ YES — Human must verify Cue | ❌ NO — no validation/reuse | **Evidence Helpfulness** |
| CS2 | ✅ YES — period+capital speeds decision | ✅ YES — not always sentence boundary | ❌ NO — no validation/reuse | **Evidence Helpfulness** |
| CS3 | ✅ YES — "FIG" pattern speeds recognition | ✅ YES — FIG can be in-text reference | ❌ NO — no validation/reuse | **Evidence Helpfulness** |

**All three candidates achieve E1 (faster) but NOT E3 (skip review).**

This means: current signals can reduce **time** but not **review count**. This is C2 (Distillation), not C3 (Learning).

---

## 8. Audit F: Automation Bias Risk

| Signal | Risk | Counter-evidence | Boundary needed |
|---|---|---|---|
| CS1 | TLD diff_cell → blind KEEP_SEPARATE | No MERGE case with diff_cell=True in corpus (untested) | Need UNKNOWN when TLD is uncertain |
| CS2 | period+capital → blind KEEP_SEPARATE | AMB-387: colon-ending → MERGE (not period) | Need to distinguish sentence end from paragraph end |
| CS3 | "FIG" → blind MERGE | AMB-063: "(Fig. 6, right)." → KEEP_SEPARATE (in-text ref) | Need to distinguish "FIG. N:" (caption) from "(Fig. N)" (in-text) |

### Over-generalization Risk

```
One Human Feedback
    ↓
"different table columns → KEEP_SEPARATE"
    ↓
Applied to ALL future TLD diff_cell cases
    ↓
But: some diff_cell cases might be MERGE
    ↓
Human blindly accepts → automation bias
```

**Mitigation requirement**: Any reuse mechanism must preserve:
- UNKNOWN (when evidence is ambiguous)
- CONFLICT (when evidence disagrees)
- Human override (when signal is wrong)

---

## 9. Current Maturity Level

| Level | Description | Status | Evidence |
|---|---|---|---|
| L0 | Human-only decision | ✅ PASSED | Historical state |
| L1 | Feedback captured | ✅ CURRENT | 4 free-text + 90 rationales + 55 decisions stored |
| L2 | Feedback evidence-linked | ⚠️ PARTIAL | CS1: 47% TLD-linked, CS2: 100%, CS3: 100% — but manual linkage only |
| L3 | Reusable candidate discovered | ⚠️ PARTIAL (manual) | 4 candidates identified by manual analysis, no automation |
| L4 | Human validates reusable signal | ❌ MISSING | No validation workflow exists |
| L5 | Validated knowledge reused | ❌ MISSING | No reuse mechanism |
| L6 | Reuse reduces Human effort | ❌ MISSING | No measurement |
| L7 | Repeated iterative improvement | ❌ MISSING | No iteration |

**CURRENT_LEVEL = L1→L2 (transitional)**

DICE has feedback capture (L1) and partial evidence linkage (L2), but has NOT reached L3 (automated reusable candidate discovery) or L4 (human-validated signal).

---

## 10. Smallest Next Experiment (Design Only, NOT Implemented)

### Experiment: CS1 Signal Validation + Reuse Pilot

```
Phase 1: Signal Definition (no code)
    → Define: "When TLD detects is_in_table=True AND different_cell=True,
       the evidence structure supports KEEP_SEPARATE"
    → This is a CANDIDATE signal, NOT a rule
    → Status = CANDIDATE, authority = 0

Phase 2: Human Validation (protocol only)
    → Present 10 TLD-matched cases to Human
    → Human validates: "Does this evidence structure support KEEP_SEPARATE?"
    → Record: validated / rejected / uncertain
    → If ≥8/10 validated → signal reaches R4 (Human-validated candidate)

Phase 3: Reuse Test (protocol only)
    → Select 10 NEW cases from 545 pool (not yet reviewed)
    → Condition A (Reuse OFF): Human reviews from scratch
    → Condition B (Reuse ON): Human sees "signal proposes KEEP_SEPARATE (validated)"
       → Human can: accept / reject / mark UNKNOWN
    → Measure: review time, decision accuracy, UNKNOWN preservation

Phase 4: Measurement
    → FRR (Feedback Reuse Ratio) = cases covered by validated signal / feedback instances
    → Review reduction = (A_time - B_time) / A_time
    → Quality preservation = B_accuracy ≥ A_accuracy
    → Boundary preservation = B_UNKNOWN_rate ≥ A_UNKNOWN_rate
```

### What This Experiment Would Test

| Hypothesis | How to test |
|---|---|
| Signal reduces review time | A_time > B_time |
| Signal maintains quality | A_accuracy ≈ B_accuracy |
| Signal preserves boundary | B_UNKNOWN_rate ≥ A_UNKNOWN_rate |
| Signal avoids automation bias | B_override_rate > 0 (Human sometimes rejects signal) |

### What This Experiment Would NOT Test

- Cross-participant signal stability (still n=1)
- Long-term iterative improvement (no iteration)
- Error propagation across reuse cycles (no cycles)
- Cross-corpus generalization (same 4 PDFs)

---

## 11. Anti-Overdesign Gate

| Question | Answer | Justification |
|---|---|---|
| Need new DICE Core Module? | **NO** | Existing scripts + metadata sufficient |
| Need new Signal Object? | **NO** | Can be expressed as research metadata, not runtime object |
| Need Pattern Engine? | **NO** | Manual signal identification sufficient for pilot |
| Need Learning Engine? | **NO** | Validation protocol is manual, not automated |
| Need ML Training? | **NO** | Signal is structural, not statistical |
| Need Evidence Layer modification? | **NO** | TLD + text features already exist |
| Need Human Validation Schema modification? | **NO** | Existing ValidationRecord can store validation |
| Need Runtime modification? | **NO** | Signal has zero runtime authority |

### What IS Needed (Minimal, Not Authorized)

1. **Signal validation protocol** (document, not code)
2. **Reuse experiment design** (document, not code)
3. **10-20 new cases from 545 pool** for reuse test (data selection, not new collection)
4. **Measurement framework** (metrics definition, not implementation)

All are research methodology, not DICE system modifications.

---

## 12. Core Question Answer

### 当前 DICE 是否实现了 Human Feedback → Machine Learning → Future Reuse → Human Review Reduction?

```
IMPLEMENTED = NO
```

| Component | Status |
|---|---|
| Feedback Capture | ✅ IMPLEMENTED (L1) |
| Reusable Signal | ⚠️ PARTIAL (manual candidates, no automation) |
| Human Validation of Signal | ❌ MISSING |
| Future Case Reuse | ❌ MISSING |
| Measured Human Reduction | ❌ MISSING |
| Quality Preservation | ❌ MISSING (cannot measure without reuse) |
| Error Containment | ❌ MISSING (cannot measure without reuse) |
| Boundary Preservation | ❌ MISSING (cannot measure without reuse) |

### Distance to Closed Loop

```
Current: L1→L2 (Feedback Captured, Evidence-Linked PARTIAL)
Target:  L5→L6 (Validated Reuse, Measured Reduction)
Gap:     3-4 levels (L3 automated discovery, L4 validation, L5 reuse, L6 measurement)
```

### What's Missing (The Real Gap)

The gap is NOT:
- ❌ More data (545 candidates exist)
- ❌ Better TLD (frozen, working)
- ❌ Better Cue (frozen, working)
- ❌ More documents (4 PDFs sufficient for pilot)

The gap IS:
1. **Signal validation workflow** — no mechanism for Human to validate "this signal applies to this evidence"
2. **Reuse mechanism** — no way to apply validated signal to future cases
3. **Measurement framework** — no baseline comparison to measure reduction
4. **Boundary expression** — signals cannot express UNKNOWN/CONFLICT
5. **Cross-participant verification** — n=1, no signal stability evidence

---

## 13. Governance

```
CORE MODIFICATION = NO
NEW MODULE = NO
NEW ENGINE = NO
ML TRAINING = NO
RUNTIME CHANGE = NO
FROZEN BASELINE = INTACT
EXPERIMENT AUTHORIZATION = NOT GRANTED
STOP = TRUE
```
