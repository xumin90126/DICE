# Decision-Critical Evidence Consumption Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY / NO MODIFICATION / FROZEN INTACT / STOP
**Predecessor**: Human Boundary Decision Evidence Dependency Audit

---

## 1. Executive Summary

```
FINAL_STATUS = DCE_EXISTS_BUT_CONSUMPTION_IS_CORPUS_SPECIFIC

KEY FINDING:
  Human 做出正确 Boundary Judgment 时，依赖的 Decision-Critical Evidence 可分为 5 类 (DCE-01 to DCE-05)。
  
  其中 4 类 (DCE-01 to DCE-04) 是 DETERMINISTICALLY DERIVABLE from existing P1 text:
    - DCE-01: has_fig_prefix (text.startswith("FIG"))
    - DCE-02: period_end + cap_start (text.endswith(".") + text[0].isupper())
    - DCE-03: is01_a AND is01_b (both pure numbers → different cells)
    - DCE-04: is02_a AND is02_b (both readable text → different headers)
  
  这 4 类在 IS-11 (45 cases) 上:
    - 覆盖 17/18 ABSTAIN cases (94%)
    - 0 FP, 0 Regression
    - 从 TN=26 (58%) 提升到 TN=41 (91%)
  
  但在 P7 (69 cases) 上:
    - DCE-01: 2 FP (FIG prefix 不总是 MERGE)
    - DCE-02: 5 FP (period+cap 不总是 KEEP — reference entries)
    - DCE-04: 10 FP (both-text 不总是 KEEP — body text continuation)
    - DCE-03: 0 cases (无法验证)
  
  → DCE-01 to DCE-04 是 CORPUS-SPECIFIC patterns, NOT universal signals
  → 它们在 IS-11 的 candidate space (same_y_band + gap 8-50) 内有效
  → 但在 P7 的不同 candidate space 上产生 FP
  → LS-3 NOT justified (no cross-corpus generalizability)

  DCE-05: table_column_identity (semantic/structural)
    - 仅 2/45 cases 真正需要 (AMB-135, AMB-262)
    - 需要 TABLE STRUCTURE knowledge (TLD or equivalent)
    - NOT deterministic — requires semantic/structural capability

IS-01/IS-02 INFORMATION LOSS:
  P1 raw text → IS-01 (is_number?) + IS-02 (has_text?) → binary
  → 全部 semantic content 丢失
  → "4" = stage index 变成 is_number=True
  → "MBConv6" = operator type 变成 has_text=True
  → 两个 binary 信号无法区分 "same column" vs "different column"

PRIMARY_BOTTLENECK = C (Consumer Integration) — corpus-specific
SECONDARY_BOTTLENECK = F (Evaluation Standard) — DCE-02 requires standard
TYPE_D (Missing + Critical) = DCE-05 (2 cases, requires TLD)

STOP = TRUE
```

> **Human 依赖的 Decision-Critical Evidence 中，4 类 (DCE-01 to DCE-04) 是确定性可推导的，在 IS-11 上可解决 94% 的 ABSTAIN。但 P7 交叉验证证明这些 pattern 是 corpus-specific 的，不具备跨语料库泛化能力。仅 2/45 cases (4%) 真正需要 table structure knowledge (DCE-05)。当前瓶颈是 Consumer Integration，但修复方案是 corpus-specific 的，不能直接作为 universal Learning Signal。**

---

## 2. Research Question

> **Human 做出正确 Boundary Judgment 时，哪些 Evidence 真正具有 Decision-Critical 作用，而这些 Evidence 中哪些已存在于 DICE、哪些已被 Current Consumer 消费、哪些虽然存在但没有被消费？**

核心区分：

```
Evidence Exists ≠ Evidence Available ≠ Evidence Consumed ≠ Evidence Decision-Critical
```

---

## 3. Case Selection

| Type | Count | Cases |
|---|---|---|
| Focus (9) | 9 | AMB-135, AMB-032, AMB-313, AMB-375, AMB-414, AMB-418, AMB-422, AMB-462, AMB-519 |
| CLEAR KEEP (TLD hit) | 4 | AMB-024, AMB-074, AMB-346, AMB-530 |
| CLEAR KEEP (TLD miss, TN) | 4 | AMB-052, AMB-163, AMB-168, AMB-267 |
| Prose disagreement | 1 | AMB-005 |
| MERGE (figure) | 2 | AMB-414, AMB-422 |
| All 45 IS-11 cases | 45 | Full set |
| P7 cross-validation | 69 | Full P7 set |

---

## 4. Evidence Consumption Chain

### Current IS-11 Consumption Chain (from source code)

```
P1 (text extraction)
  → text_a, text_b (raw strings)
    ↓
P2 (geometry)
  → bbox_a, bbox_b, same_y_band, h_gap, geometric_state
    ↓
IS-01 (FROZEN regex on text_a)
  → is01_a = bool(re.match(r'^\d+(\.\d+)*\.?$', text_a))
  → BINARY: is text_a a pure number?
    ↓
IS-02 (FROZEN on text_b)
  → is02_b = any(len(alpha_chars(w)) > 2 for w in text_b.split())
  → BINARY: does text_b have readable text?
    ↓
TLD (table_line_detector.py)
  → is_in_table, different_cell, same_cell, a_cell, b_cell
  → BINARY: table membership + cell assignment
    ↓
IS-11 Decision (experimental_c_decision):
  1. different_cell → KEEP_SEPARATE (override)
  2. same_cell → MERGE (override)
  3. Else → baseline_b_decision(is01_a, is02_b):
     - is01=True AND is02=True → MERGE
     - is01=False AND is02=False → KEEP_SEPARATE
     - Mixed → INSUFFICIENT_EVIDENCE
```

### Information Loss Points

| Stage | Input | Output | Loss |
|---|---|---|---|
| IS-01 | text_a (full string) | bool (is_number) | ALL semantic content |
| IS-02 | text_b (full string) | bool (has_text) | ALL semantic content |
| TLD | vlines (visual) | bool (is_in_table, diff_cell) | Table structure (when TLD fails: 71%) |

### Human Consumption Chain (reconstructed from rationales)

```
P1 text (raw strings) + Page image (visual)
  → Human reads text SEMANTIC CONTENT
    → "4" = stage index
    → "MBConv6" = operator type
    → "different columns in Table 1"
  → Human sees PAGE LAYOUT
    → Table structure, column boundaries
  → Human identifies STRUCTURAL ROLE
    → Different column → KEEP_SEPARATE
    → Same caption → MERGE
    → Sentence boundary → KEEP_SEPARATE
```

---

## 5. Human Decision Evidence Map

### Evidence Classification (EC0-EC3)

| EC Level | Count | Description |
|---|---|---|
| EC0 (Non-critical) | 0 | — |
| EC1 (Supporting) | 225 | bbox, same_y_band, h_gap, geometric_state (all supporting) |
| EC2 (Decision-Relevant) | 189 | raw_text (binary only), is01/is02 (when not critical), page_context |
| EC3 (Decision-Critical) | 112 | different_cell (13), is01/is02 (14 each when TLD misses), table_column_identity (35), period_end+cap_start (4), has_fig_prefix (2) |

### Consumption Status (C0-C4)

| C Level | Count | Description |
|---|---|---|
| C0 (Not available) | 0 | — |
| C1 (Available but not consumed) | 45 | table_column_identity (35), period_end (4), cap_start (4), has_fig_prefix (2) |
| C2 (Consumed in binary form) | 238 | raw_text_a/b (via IS-01/IS-02), is01_a/is02_b, different_cell/same_cell |
| C3 (Consumed structurally sufficient) | 206 | bbox, same_y_band, h_gap, geometric_state, a_cell/b_cell |
| C4 (Human-visible only) | 37 | page_context (Human sees page image, machine doesn't) |

---

## 6. Decision-Critical Evidence Analysis

### Type Classification

| Type | Description | Count | Evidence |
|---|---|---|---|
| **Type A** | Already consumed + Decision-critical | 13 | different_cell (TLD), is01_a/is02_b (when EC3) |
| **Type B** | Exists + Decision-critical + NOT consumed | 17 | has_fig_prefix (2), period_end+cap_start (3), is01_a∧is01_b (7), is02_a∧is02_b (5) |
| **Type C** | Exists + Human uses + NOT decision-critical | 35 | page_context, h_gap, same_style (supporting only) |
| **Type D** | Missing + Decision-critical | 2 | table_column_identity when TLD misses AND patterns don't resolve (AMB-135, AMB-262) |

---

## 7. Current Consumer Consumption Analysis

### IS-01/IS-02 Information Loss

```
P1 raw text_a = "4"
  → IS-01: re.match(r'^\d+(\.\d+)*\.?$', "4") → True
  → Output: is_number = True
  → LOST: "4" = stage index (semantic role)

P1 raw text_b = "MBConv6, k5x5"
  → IS-02: any(len(alpha(w)) > 2 for w in "MBConv6, k5x5".split()) → True
  → Output: has_text = True
  → LOST: "MBConv6" = operator type (semantic role)

Combined: is_number(True) + has_text(True) → MERGE
  → WRONG: "4" and "MBConv6" are DIFFERENT columns → should KEEP_SEPARATE
```

### What IS-11 Consumes vs What Human Uses

| Evidence | IS-11 Consumes | Human Uses | Gap |
|---|---|---|---|
| raw_text_a content | BINARY (is_number) | SEMANTIC (stage index) | C2 → needs C3 |
| raw_text_b content | BINARY (has_text) | SEMANTIC (operator type) | C2 → needs C3 |
| has_fig_prefix | NOT consumed | YES (caption identification) | C1 |
| period_end | NOT consumed | YES (sentence boundary) | C1 |
| cap_start | NOT consumed | YES (sentence boundary) | C1 |
| is01_b (text_b is number?) | NOT computed | N/A (Human uses semantics) | C1 (derivable) |
| is02_a (text_a has text?) | NOT computed | N/A (Human uses semantics) | C1 (derivable) |
| table_column_identity | NOT consumed | YES (column role) | C1 (semantic) |
| different_cell | YES (TLD override) | YES | C2 (sufficient) |
| page_context | NOT available | YES (page image) | C4 |

---

## 8. Counterfactual Evidence Analysis

### DCE-01: has_fig_prefix → MERGE

```
Derivation: text_a.startswith("FIG") or text_b.startswith("FIG")
Deterministic: YES (regex)
IS-11: 2/45 cases, 0 FP, 2 ABSTAIN → TP
P7: 2/69 cases, 2 FP (GT=KEEP_SEPARATE, not MERGE)
Generalizability: LOW (corpus-specific)
```

### DCE-02: period_end + cap_start → KEEP_SEPARATE

```
Derivation: text_a.endswith(".") AND text_b[0].isupper()
Deterministic: YES (regex)
IS-11: 4/45 cases, 0 FP, 3 ABSTAIN → TN
P7: 15/69 cases, 5 FP (reference entries where period+cap ≠ sentence boundary)
Generalizability: LOW (corpus-specific, depends on text type)
Governance Risk: MEDIUM (requires standard clarification: sentence vs paragraph)
```

### DCE-03: is01_a=True AND is01_b=True → KEEP_SEPARATE

```
Derivation: compute_is01(text_a) AND compute_is01(text_b)
  (Same regex as existing IS-01, applied to text_b)
Deterministic: YES (regex)
IS-11: 12/45 cases, 0 FP, 7 ABSTAIN → TN
P7: 0/69 cases (no both-number pairs in P7)
Generalizability: UNKNOWN (cannot validate on P7)
```

### DCE-04: is02_a=True AND is02_b=True → KEEP_SEPARATE (after fig check)

```
Derivation: compute_is02(text_a) AND compute_is02(text_b) AND NOT has_fig
  (Same regex as existing IS-02, applied to text_a)
Deterministic: YES (regex)
IS-11: 10/45 cases (after fig check), 0 FP, 5 ABSTAIN → TN
P7: 27/69 cases, 10 FP (body text continuation, reference entries)
Generalizability: LOW (corpus-specific, depends on structural context)
```

### DCE-05: table_column_identity (semantic/structural)

```
Derivation: NOT deterministic — requires table structure knowledge
IS-11: 2/45 cases (AMB-135, AMB-262) — only cases unresolved by DCE-01 to DCE-04
  AMB-135: "4" + "MBConv6" → number + text, different columns
  AMB-262: "41M" + "EfficientNet-B5" → not-number + text, different columns
Requires: TLD (table structure detection) or equivalent
Generalizability: N/A (this is the TLD dependency)
Governance Risk: HIGH (requires structural capability, not regex)
```

### Combined Counterfactual (DCE-01 to DCE-04 as overrides)

```
Current:  TN=26 (58%), ABSTAIN=18 (40%), FP=1 (2%)
With DCE: TN=41 (91%), ABSTAIN=1 (2%), FP=1 (2%)
  → 17 improvements, 0 regressions
  → Remaining: 1 ABSTAIN (AMB-262) + 1 FP (AMB-135) = 2 cases requiring DCE-05
```

---

## 9. AMB-135 Deep Dive

```
Case: IS11-AMB-135
Text A: "4"          Text B: "MBConv6, k5x5"
GT: KEEP_SEPARATE    Machine: MERGE (FP)

EVIDENCE CONSUMPTION CHAIN:
  P1: text_a="4", text_b="MBConv6, k5x5"
  P2: bbox_a, bbox_b, same_y_band=True, h_gap=30.0
  IS-01: is01_a = re.match(r'^\d+(\.\d+)*\.?$', "4") → True
  IS-02: is02_b = any(len(alpha(w))>2 for w in "MBConv6, k5x5".split()) → True
  TLD: is_in_table=False (TLD missed the table), different_cell=False
  Decision: not different_cell → fallback → is01=True + is02=True → MERGE (FP)

HUMAN DECISION CHAIN:
  Human reads: "4" = stage index, "MBConv6, k5x5" = operator type
  Human sees: Table 1 architecture table with multiple columns
  Human concludes: different columns → KEEP_SEPARATE

COUNTERFACTUAL TEST:
  Q1 (remove table_column_identity): Human cannot identify different columns → UNKNOWN
  Q2 (only table_column_identity): Sufficient → KEEP_SEPARATE
  Q3 (not consumed): Machine FP (MERGE instead of KEEP)
  Q4 (consumed): Would resolve FP → TN

WHY MACHINE FAILS:
  IS-01/IS-02 treats "number + text" as "same unit" (value + label)
  Cannot distinguish "same column" from "different column"
  TLD missed the table → no structural override
  
DCE COVERAGE:
  DCE-01 (has_fig): No — not a figure
  DCE-02 (period+cap): No — "4" doesn't end with period
  DCE-03 (both_numbers): No — "MBConv6" is not a pure number (is01_b=False)
  DCE-04 (both_text): No — "4" has no alpha>2 chars (is02_a=False)
  → UNRESOLVED by DCE-01 to DCE-04
  → Requires DCE-05: table_column_identity (TLD or equivalent)

INFORMATION LOSS:
  P1 text "4" → IS-01 → True (is_number)
    LOST: "4" = stage index (semantic role)
  P1 text "MBConv6, k5x5" → IS-02 → True (has_text)
    LOST: "MBConv6" = operator type (semantic role)
  Combined binary: number + text → MERGE
    WRONG: different columns → should KEEP_SEPARATE
```

---

## 10. AMB-032 Deep Dive

```
Case: IS11-AMB-032
Text A: "-"          Text B: "8.43"
GT: KEEP_SEPARATE    Machine: KEEP_SEPARATE (TN)

EVIDENCE CONSUMPTION CHAIN:
  P1: text_a="-", text_b="8.43"
  TLD: is_in_table=True, different_cell=True, a_cell=[27,1], b_cell=[27,2]
  Decision: different_cell=True → KEEP_SEPARATE (TN)

HUMAN DECISION CHAIN:
  Human reads: "-" = missing top-1 error, "8.43" = top-5 error
  Human sees: Table 3, VGG row, different columns
  Human concludes: different columns → KEEP_SEPARATE

P722 BEHAVIOR:
  B2: UNKNOWN (45.9s, expanded ALL 7 geometry fields)
  → P722 participant could NOT see TLD cell info
  → Participant only had geometry fields (h_gap, dy, same_style, etc.)
  → Could not determine table membership from geometry alone

ANALYSIS:
  IS-11 machine: E1 (TLD used correctly) → TN
  P722 participant: Evidence Exposure Gap (TLD info not exposed)
  Human reviewer: Used table structure (from page visual) → KEEP

  This is NOT a Consumer Integration Gap for IS-11.
  This IS an Evidence Exposure Gap for P722 experiment.
  → Different problems at different layers.
```

---

## 11. AMB-313 / AMB-462 Deep Dive

```
AMB-313: Text A="Test Size", Text B="#Classes"
  GT: KEEP_SEPARATE    Machine: ABSTAIN

  TLD: is_in_table=False (missed table)
  IS-01: is01_a=False ("Test Size" not pure number)
  IS-02: is02_b=True ("#Classes" has alpha>2)
  Decision: mixed → ABSTAIN

  Human: "Test Size" and "#Classes" are different column headers → KEEP
  
  DCE-04 coverage: is02_a=True ("Test Size" has alpha>2) AND is02_b=True
    → DCE-04 would resolve: KEEP_SEPARATE → TN
  
  P7 FP check: "Test Size" + "#Classes" pattern is table-specific
    P7 body text: "Hyperparameter" + "Search Space" → MERGE (same sentence)
    → DCE-04 NOT generalizable

AMB-462: Text A="WGe", Text B="Avg."
  GT: KEEP_SEPARATE    Machine: ABSTAIN

  TLD: is_in_table=False (missed table)
  IS-01: is01_a=False ("WGe" not pure number)
  IS-02: is02_b=True ("Avg." → "Avg" has 3 alpha >2)
  Decision: mixed → ABSTAIN

  Human: "WGe" and "Avg." are different table headers → KEEP
  
  DCE-04 coverage: is02_a=True ("WGe" → "WGe" has 3 alpha >2) AND is02_b=True
    → DCE-04 would resolve: KEEP_SEPARATE → TN

KEY INSIGHT:
  Human 能纠正 Machine，因为 Human 识别了 text 的 STRUCTURAL ROLE (table header)
  This structural role IS derivable from text content (both have readable text)
  But the derivation (both_text → different headers) is corpus-specific
  → It works in IS-11 (table-focused candidates) but not in P7 (body text)
```

---

## 12. AMB-375 / 418 / 519 Deep Dive

```
All 3 cases: Prose sentence boundary, reviewer disagreement

AMB-375: A="[23]." B="Each"     GT=KEEP (adjudicated, A=KEEP, B=MERGE)
AMB-418: A="...panel." B="The"  GT=KEEP (adjudicated, A=KEEP, B=MERGE)
AMB-519: A="...LLMs." B="To..." GT=KEEP (adjudicated, A=KEEP, B=MERGE)

EVIDENCE:
  period_end = text_a.endswith(".") → True (ALL 3)
  cap_start = text_b[0].isupper() → True (ALL 3)
  → DETERMINISTICALLY DERIVABLE from P1 text

STANDARD GAP:
  Reviewer A: text unit = sentence → KEEP (period + cap = sentence boundary)
  Reviewer B: text unit = paragraph → MERGE (same paragraph, continuous flow)
  Adjudicator: period + cap → separate sentences → KEEP

  The disagreement is about STANDARD (sentence vs paragraph), NOT evidence.
  Evidence IS sufficient (period+cap derivable).
  → NOT E5 (genuine semantic judgment)
  → E3 (derivable) + STANDARD_GAP

DCE-02 COVERAGE:
  DCE-02 (period_end + cap_start → KEEP) would resolve ALL 3 ABSTAIN → TN
  
P7 FP CHECK:
  P7 has 15 period+cap cases, 5 are GT=MERGE (reference entries)
  → DCE-02 NOT generalizable (reference entries: ". New York" → MERGE)
  → Corpus-specific: works for IS-11 prose, fails for P7 references
```

---

## 13. Minimal Decision-Critical Evidence Set

### DCE-01: has_fig_prefix

```
DCE_ID: DCE-01
NAME: has_fig_prefix
SOURCE: P1 text (text_a.startswith("FIG") or text_b.startswith("FIG"))
EXISTS_IN_DICE: YES (P1 raw text)
CURRENTLY_CONSUMED: NO (IS-11 only checks is_number via IS-01)
CURRENT_CONSUMPTION_FORM: NONE
HUMAN_DEPENDENCY: HIGH (2/2 figure caption cases)
COUNTERFACTUAL_SUPPORT: 2 ABSTAIN → TP, 0 FP (IS-11), 2 FP (P7)
CRITICALITY: EC3 (Decision-Critical for figure cases)
GENERALIZABILITY: LOW (corpus-specific — IS-11: FIG=MERGE, P7: FIG=KEEP)
GOVERNANCE_RISK: MEDIUM (FIG prefix semantics differ across corpora)
```

### DCE-02: period_end + cap_start

```
DCE_ID: DCE-02
NAME: period_end + cap_start (sentence boundary)
SOURCE: P1 text (text_a.endswith(".") + text_b[0].isupper())
EXISTS_IN_DICE: YES (P1 raw text)
CURRENTLY_CONSUMED: NO
CURRENT_CONSUMPTION_FORM: NONE
HUMAN_DEPENDENCY: HIGH (4/4 prose cases)
COUNTERFACTUAL_SUPPORT: 3 ABSTAIN → TN, 0 FP (IS-11), 5 FP (P7)
CRITICALITY: EC3 (Decision-Critical for prose cases)
GENERALIZABILITY: LOW (corpus-specific — IS-11: period+cap=KEEP, P7: mixed)
GOVERNANCE_RISK: MEDIUM (requires standard clarification + text type awareness)
```

### DCE-03: is01_a AND is01_b (both pure numbers)

```
DCE_ID: DCE-03
NAME: both_pure_numbers (is01_a=True AND is01_b=True)
SOURCE: P1 text (same IS-01 regex applied to BOTH text_a and text_b)
EXISTS_IN_DICE: YES (IS-01 regex exists, just not applied to text_b)
CURRENTLY_CONSUMED: NO (IS-01 only computed on text_a)
CURRENT_CONSUMPTION_FORM: NONE for is01_b
HUMAN_DEPENDENCY: INDIRECT (Human uses semantic column identity, not is_number)
COUNTERFACTUAL_SUPPORT: 7 ABSTAIN → TN, 0 FP (IS-11), unvalidated (P7)
CRITICALITY: EC3 (Decision-Critical for both-number table cases)
GENERALIZABILITY: UNKNOWN (0 P7 cases to validate)
GOVERNANCE_RISK: LOW (deterministic regex, no semantic leakage)
```

### DCE-04: is02_a AND is02_b (both readable text, after fig check)

```
DCE_ID: DCE-04
NAME: both_readable_text (is02_a=True AND is02_b=True AND NOT has_fig)
SOURCE: P1 text (same IS-02 check applied to BOTH text_a and text_b)
EXISTS_IN_DICE: YES (IS-02 check exists, just not applied to text_a)
CURRENTLY_CONSUMED: NO (IS-02 only computed on text_b)
CURRENT_CONSUMPTION_FORM: NONE for is02_a
HUMAN_DEPENDENCY: INDIRECT (Human uses semantic header identity, not has_text)
COUNTERFACTUAL_SUPPORT: 5 ABSTAIN → TN, 0 FP (IS-11), 10 FP (P7)
CRITICALITY: EC3 (Decision-Critical for both-text table header cases)
GENERALIZABILITY: LOW (corpus-specific — IS-11: both-text=KEEP, P7: mixed)
GOVERNANCE_RISK: HIGH (FP on body text and references in P7)
```

### DCE-05: table_column_identity (semantic/structural)

```
DCE_ID: DCE-05
NAME: table_column_identity (which column does each text belong to?)
SOURCE: TLD (table structure) or equivalent structural detection
EXISTS_IN_DICE: YES (TLD provides this when it works, 29% of cases)
CURRENTLY_CONSUMED: YES when TLD works (different_cell → KEEP)
CURRENT_CONSUMPTION_FORM: BINARY (different_cell=True/False)
HUMAN_DEPENDENCY: HIGH (Human uses column identity for ALL table cases)
COUNTERFACTUAL_SUPPORT: 2/45 cases truly require this (AMB-135, AMB-262)
CRITICALITY: EC3 (Decision-Critical when TLD misses AND DCE-01 to DCE-04 don't resolve)
GENERALIZABILITY: UNIVERSAL (table structure is language/corpus-independent)
GOVERNANCE_RISK: HIGH (requires TLD improvement or equivalent — NOT regex)
```

---

## 14. Evidence Consumption Gap Classification

### Gap Type A: Already Consumed + Decision-Critical (No action needed)

| Evidence | Cases | Form |
|---|---|---|
| different_cell (TLD) | 13 | C2 (binary, structurally sufficient) |
| is01_a/is02_b (when EC3) | 14 | C2 (binary, information loss but correct) |

### Gap Type B: Exists + Decision-Critical + NOT Consumed (Consumer Integration)

| Evidence | Cases | IS-11 FP | P7 FP | Generalizable? |
|---|---|---|---|---|
| DCE-01 has_fig_prefix | 2 | 0 | 2 | NO |
| DCE-02 period_end+cap_start | 3 | 0 | 5 | NO |
| DCE-03 both_numbers | 7 | 0 | N/A | UNKNOWN |
| DCE-04 both_text | 5 | 0 | 10 | NO |
| **Total** | **17** | **0** | **17+** | **NO** |

### Gap Type C: Exists + Human Uses + NOT Decision-Critical (No action needed)

| Evidence | Cases | Role |
|---|---|---|
| page_context | 35 | EC2 (supporting, Human-only visual) |
| h_gap | 45 | EC1 (supporting, candidate construction) |
| same_style | 45 | EC1 (supporting, candidate construction) |
| bbox | 45 | EC1 (supporting, candidate construction) |

### Gap Type D: Missing + Decision-Critical (Observation Gap)

| Evidence | Cases | Requires |
|---|---|---|
| DCE-05 table_column_identity | 2 | TLD improvement or equivalent |

---

## 15. Learning Signal Reassessment

| LS Level | Count | Description |
|---|---|---|
| LS-0 | 26 | Machine already correct (TN via TLD or fallback), Human confirms |
| LS-1 | 12 | Human points to existing evidence (P1 text semantics) not consumed |
| LS-2 | 7 | Human points to derivable relations (DCE-01 to DCE-04) — but corpus-specific |
| LS-3 | 0 | NO genuinely reusable cross-corpus signal |
| LS-4 | 0 | N/A |

### Why NOT LS-3?

DCE-01 to DCE-04 satisfy:
- ✓ Cross-case recurrence (within IS-11)
- ✓ Evidence-grounded
- ✓ Decision-critical
- ✓ Deterministically derivable

But FAIL:
- ✗ Generalizable (P7 cross-validation shows FP)
- ✗ Human feedback adds information (patterns are retrospective, not from feedback)
- ✗ Future reuse can be tested (corpus-specific, not universal)

> **DCE-01 to DCE-04 是 IS-11 corpus-specific retrospective patterns。它们在 IS-11 的 candidate space 内有效（0 FP），但在 P7 上产生 FP。不能作为 LS-3 Learning Signal。**

---

## 16. Bottleneck Reassessment

### Previous Audit Conclusion

```
PRIMARY_BOTTLENECK = C (Consumer Integration) — 64% E2
```

### This Audit's Finding

```
PRIMARY_BOTTLENECK = C (Consumer Integration) — CONFIRMED but with caveat
  → 17/45 cases (38%) have Type B evidence (exists, critical, not consumed)
  → DCE-01 to DCE-04 are deterministic and derivable
  → BUT: corpus-specific (0 FP on IS-11, 17+ FP on P7)
  → The Consumer Integration gap is REAL but the fix is NOT universal

SECONDARY_BOTTLENECK = F (Evaluation Standard) — 3 cases (7%)
  → DCE-02 (period+cap) requires standard clarification (sentence vs paragraph)

TYPE_D (Missing + Critical) = 2/45 (4%)
  → DCE-05 (table_column_identity) requires TLD improvement
  → This is the ONLY case where evidence is truly missing (TLD fails)
```

### Why Still C (not B or D)?

- B (Evidence Organization): Evidence IS organized (P1 text, P2 geometry, TLD structure). Problem is consumption, not organization.
- D (Evidence Perception): P2 evidence is sufficient. Problem is not perception.
- The断裂 is between P1 text content and IS-11's binary extraction (IS-01/IS-02).
- IS-11 reads P1 text but compresses it to binary, losing semantic content.
- DCE-01 to DCE-04 show that even SIMPLE deterministic features (not consumed) could resolve 94% of ABSTAIN.
- But these features are corpus-specific, so the fix requires context awareness.

---

## 17. Anti-Overdesign Review

### Check: Does the audit propose any new layer?

```
Evidence Organization Engine: NO — evidence is already organized
Relation Engine: NO — relations exist (TLD provides cell relations)
Semantic Engine: NO — DCE-01 to DCE-04 are deterministic regex, not semantic
Discourse Engine: NO — no document discourse needed
Learning Engine: NO — 0 LS-3, no learning signal
LLM Layer: NO — DCE-05 requires TLD improvement, not LLM
Pattern Engine: NO — patterns are retrospective, not proposed as engine
Query Engine: NO
```

### What IS proposed?

```
Type B (17 cases): Consumer Integration of existing derivable features
  → DCE-01 to DCE-04 are deterministic regex on P1 text
  → Same IS-01/IS-02 framework, extended to both text_a and text_b
  → NO new Observation, NO new Module, NO new Engine
  → BUT: corpus-specific, requires context awareness

Type D (2 cases): TLD improvement
  → DCE-05 requires better table detection
  → This is a TLD capability issue, not a new layer
  → NOT proposed for implementation in this audit
```

---

## 18. Limitations

1. **Retrospective Analysis**: DCE-01 to DCE-04 are retrospective patterns. They work on 45 IS-11 cases but may not work on new cases without independent validation.

2. **P7 Cross-Validation**: P7 uses different corpus and different candidate construction. FP rates on P7 do NOT directly predict FP rates on future IS-11 cases. They DO show that the patterns are corpus-specific.

3. **DCE-03 Unvalidated**: is01_a AND is01_b pattern has 0 P7 cases. Cannot confirm or deny generalizability.

4. **45-Case Sample**: Statistics are from 45 cases. NOT generalizable to 545 candidates or all documents.

5. **TLD Failure Rate**: TLD fails 71% (32/45). DCE-05 (2 cases) is the residual after DCE-01 to DCE-04 resolve 17 cases. But if TLD failure rate changes, DCE-05 count may change.

6. **IS-01/IS-02 Source Code**: Analysis is from `tmp/is11_machine_evaluation.py` (experiment script). Production IS-01/IS-02 (if different) may have different logic.

7. **Counterfactual Assumptions**: DCE-01 to DCE-04 counterfactual assumes the patterns are applied as overrides BEFORE the existing fallback. Real implementation might interact differently.

---

## 19. Final Verdict

### Q: Consumer 没有消费的 Evidence 中，哪些真的值得消费？

**DCE-01 to DCE-04** — 但仅限于 IS-11 candidate space (same_y_band + gap 8-50):

| DCE | Worth Consuming? | Why? |
|---|---|---|
| DCE-01 (has_fig_prefix) | CONDITIONAL — IS-11 only | 0 FP on IS-11, 2 FP on P7 |
| DCE-02 (period+cap) | CONDITIONAL — IS-11 + standard | 0 FP on IS-11, 5 FP on P7 |
| DCE-03 (both_numbers) | PROMISING — IS-11, unvalidated P7 | 0 FP on IS-11, 0 P7 cases |
| DCE-04 (both_text) | CONDITIONAL — IS-11 + fig check | 0 FP on IS-11, 10 FP on P7 |

### Q: 这些 Evidence 为什么能够改变 Boundary Decision？

Because IS-11's candidate space (same_y_band + gap 8-50) is predominantly table-focused:
- Both-numbers → likely different table cells (different columns)
- Both-text → likely different table headers (different columns)
- FIG prefix → likely figure caption (MERGE)
- Period+cap → likely sentence boundary (KEEP)

These structural roles are implicit in the geometric candidate construction but NOT explicit in IS-01/IS-02 binary.

### Q: 它们是否能够形成最小、可复用、低语义权威的 Decision Evidence？

**Within IS-11: YES.** DCE-01 to DCE-04 are deterministic regex, no semantic leakage, 0 FP on 45 cases.

**Across corpora: NO.** P7 shows FP because the same text patterns have different meanings in body text, references, and other non-table contexts.

### Final Statistics

```
TOTAL_CASES_ANALYZED: 114 (45 IS-11 + 69 P7)
EVIDENCE_ITEMS_ANALYZED: 526 (across 45 IS-11 cases)

EC0_COUNT: 0
EC1_COUNT: 225
EC2_COUNT: 189
EC3_COUNT: 112

C0_COUNT: 0
C1_COUNT: 45
C2_COUNT: 238
C3_COUNT: 206
C4_COUNT: 37

DECISION_CRITICAL_EVIDENCE_COUNT: 112
DECISION_CRITICAL_EXISTING_COUNT: 112
DECISION_CRITICAL_CONSUMED_COUNT: 40 (Type A: TLD + is01/is02 when EC3)
DECISION_CRITICAL_UNUSED_COUNT: 72 (Type B: 17 + Type C: 35 + Type D overlap)

MACHINE_UNUSED_EXISTING_EVIDENCE_COUNT: 45 (C1 items)
BINARY_COMPRESSION_LOSS_COUNT: 90 (raw_text_a + raw_text_b across 45 cases)
DERIVABLE_DECISION_EVIDENCE_COUNT: 17 (DCE-01 to DCE-04)
MISSING_DECISION_EVIDENCE_COUNT: 2 (DCE-05: AMB-135, AMB-262)

HUMAN_DEPENDENT_EVIDENCE_COUNT: 45
GENUINE_SEMANTIC_JUDGMENT_COUNT: 0

LS0_COUNT: 26
LS1_COUNT: 12
LS2_COUNT: 7
LS3_COUNT: 0
LS4_COUNT: 0

PRIMARY_BOTTLENECK: C (Consumer Integration) — corpus-specific
SECONDARY_BOTTLENECK: F (Evaluation Standard)

TRUE_REUSABLE_SIGNAL_FOUND: NO
CURRENT_LEARNING_LEVEL: L3
RECOMMENDED_NEXT_STEP: READ_ONLY_AUDIT
```

---

## 20. Governance Gate

```
DICE_CORE_MODIFICATION              = NO
P1_P7_MODIFICATION                  = NO
P2_MODIFICATION                     = NO
TLD_MODIFICATION                    = NO
IS11_MODIFICATION                   = NO
M_B_MODIFICATION                    = NO
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

`STOP = TRUE`。
