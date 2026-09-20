# DCE-05 Table Column Identity Expressibility Audit

**Date**: 2026-09-13
**Mode**: READ-ONLY / FORENSIC RESEARCH / NO MODIFICATION / FROZEN INTACT / STOP
**Predecessor**: Decision-Critical Evidence Consumption Audit

---

## 1. Executive Summary

```
FINAL_STATUS = DCE05_IS_DIFFERENT_COLUMN_NOT_COLUMN_IDENTITY
               TLD_CAN_EXPRESS_BUT_DETECTION_FAILS

KEY FINDING:
  上一轮将 DCE-05 定义为 "table_column_identity" (semantic)。
  本轮证明：Human 实际依赖的是 "different_column" (structural)，NOT "column identity" (semantic)。

  区分：
    column_identity = "4 在 stage index 列, MBConv6 在 operator 列" (semantic, L4)
    different_column = "4 和 MBConv6 在不同列" (structural, L3)
    
  Human rationale 提到 column identity ("stage index", "operator type") 作为解释,
  但 Decision-Critical 的是 different_column ("two separate columns" → KEEP_SEPARATE)。

TLD EXPRESSIBILITY:
  TLD 数据模型 CAN express different_column:
    - is_in_table: YES
    - a_cell = [row, col]: YES
    - b_cell = [row, col]: YES
    - different_cell: YES
  证明: 13/45 cases TLD 正确检测, IS-11 正确消费 → TN

TLD DETECTION FAILURE:
  TLD 在 2/45 cases (AMB-135, AMB-262) 上 Detection Failure:
    AMB-135: column_stability=0.27 (< 0.75), text_ratio=0.38 (< 0.45)
    AMB-262: column_stability=0.23 (< 0.75)
  
  原因: TLD band detection 过于 greedy — 将整个页面的连续 multicol 行作为一个 band,
        导致 column centers 不稳定 (mixed content: tables + formulas + text)。

  这不是 Representation Failure (TLD 数据模型能表达)
  这不是 Consumer Integration Failure (IS-11 消费 different_cell when TLD provides)
  这是 TLD Detection/Coverage Failure

P2 EXPRESSIBILITY:
  P2 CANNOT express different_column:
    - same_y_band: YES (L1)
    - h_gap: YES (L1)
    - multiple fragments on same y: YES (L2 derivable)
    - "table columns": NOT_EXPRESSIBLE (L3, requires structural interpretation)

DCE-05 CLASSIFICATION:
  D5-G (Mixed):
    - When TLD detects: D5-A (Existing + Already Consumed) — 13/45 cases
    - When TLD fails: D5-C (Existing Low-Level Evidence but Representation not achieved) — 2/45 cases
    - NOT D5-D (Genuinely Missing Observation) — TLD already provides the observation
    - NOT D5-E (Genuine Human Semantic Judgment) — different_column is structural

PRIMARY_BOTTLENECK (for DCE-05) = D (Evidence Perception / TLD Detection Failure)
  → NOT C (Consumer Integration) — IS-11 already consumes different_cell
  → NOT B (Evidence Organization) — TLD organizes when it detects
  → NOT E (Human Semantic Judgment) — 0% E5
  → NOT G (Evidence Insufficient) — evidence exists in TLD model, just not detected

LLM_NEEDED = NO (different_column is structural, not semantic)
NEW_OBSERVATION_NEEDED = NO (TLD already provides the observation)

STOP = TRUE
```

> **DCE-05 不是 "table_column_identity" (semantic)，而是 "different_column" (structural)。TLD 数据模型能表达 different_column（13/45 cases 正确），但在 2/45 cases 上 Detection Failure（column stability + text ratio 检查失败）。这不是 Consumer Integration 问题（IS-11 已消费 different_cell），也不是 Representation Missing（TLD 能表达），而是 TLD Detection/Coverage Failure。不需要 LLM，不需要新 Observation。**

---

## 2. Research Questions

### Q1: Human 是否真的依赖 table_column_identity?

**NO.** Human 依赖的是 **different_column** (structural)，不是 column_identity (semantic)。

证据：所有 reviewer rationale 中的 decision-critical 判断都是 "two separate columns" / "different columns" / "different cells"，而不是 "column A is stage index, column B is operator"。

column_identity 出现在 rationale 中作为 **解释**（why they're different），但 **Decision-Critical** 的是 different_column（that they're different）。

### Q2: 这个信息在 DICE 中存在吗?

**YES — in TLD data model.** TLD computes:
- `is_in_table`: bool
- `a_cell = [row_idx, col_idx]`: structural position
- `b_cell = [row_idx, col_idx]`: structural position
- `different_cell`: bool (a_cell != b_cell)

### Q3: 是 Consumer 没消费，还是 Evidence 无法表达?

**Neither.** IS-11 **does consume** `different_cell` when TLD provides it (13/45 cases → TN). The problem is TLD **Detection Failure** — TLD's data model CAN express different_column, but its detection algorithm fails on specific table types.

---

## 3. Case Selection

| Case | Type | GT | TLD Status | Purpose |
|---|---|---|---|---|
| AMB-135 | Table (TLD miss) | KEEP | 0 tables | Key: Machine FP, TLD detection fail |
| AMB-262 | Table (TLD miss) | KEEP | 0 tables | Key: Re-verify Type D |
| AMB-032 | Table (TLD hit) | KEEP | 1 table, correct | Key: TLD works, P722 UNKNOWN |
| AMB-313 | Table header (TLD miss) | KEEP | 0 tables | Key: Header row detection |
| AMB-462 | Table header (TLD partial) | KEEP | 1 table (wrong) | Key: TLD detected different table |
| AMB-024 | Table (TLD hit) | KEEP | 1 table, correct | Control: CLEAR KEEP |
| AMB-074 | Table (TLD hit) | KEEP | 1 table, correct | Control: CLEAR KEEP |
| AMB-346 | Table (TLD hit) | KEEP | 1 table, correct | Control: CLEAR KEEP |
| AMB-414 | Figure caption | MERGE | 0 tables | Control: Non-table (figure) |
| AMB-519 | Prose | KEEP | 1 table (FP) | Control: Non-table (prose) |

---

## 4. Evidence Consumption Chain

### AMB-135 Full Information Chain

```
P1:
  text_a = "4"
  text_b = "MBConv6, k5x5"

P2:
  bbox_a = [320.4, 158.2, 324.1, 165.7]
  bbox_b = [354.1, 158.2, 404.6, 165.7]
  same_y_band = True (y_a = y_b = 158.2)
  h_gap = 30.0
  same-y band has 12 vlines with 5 column gaps (≥12pt)

TLD:
  tables_detected = 0
  REASON: column_stability = 0.27 (threshold 0.75) + text_ratio = 0.38 (threshold 0.45)
  → Band detection found 1 band (56 anchor rows), but:
    - Column centers: 5 (mixed formula + table positions)
    - Alignment: 0.27 (formulas don't align to table columns)
    - Text ratio: 0.38 (many numeric/math fragments: '4', '56', '×', 'α', 'φ')

IS-01:
  is01_a = True ("4" matches ^\d+(\.\d+)*\.?$)

IS-02:
  is02_b = True ("MBConv6, k5x5" has alpha > 2)

Current IS-11:
  TLD miss → fallback → is01=True + is02=True → MERGE (FP)

Human:
  Reads: "4" = stage index, "MBConv6" = operator type
  Sees: Table 1 architecture table with multiple columns
  Decision: different columns → KEEP_SEPARATE

COUNTERFACTUAL:
  Q1 (remove different_column): Human cannot determine → UNKNOWN
  Q2 (only different_column): Sufficient → KEEP_SEPARATE
  Q3 (TLD doesn't provide): Machine FP (MERGE instead of KEEP)
  Q4 (TLD provides): Would resolve FP → TN

  If TLD column identity removed from Human:
    Human still sees page layout → can identify different columns visually
    → Human does NOT need TLD output, Human needs PAGE VISUAL
    
  If Machine only gets P1/P2 (no TLD):
    Machine CANNOT determine different_column from geometry alone
    P2 knows same_y_band + h_gap + 12 fragments, but cannot interpret as "table columns"
    → NOT expressible from P1/P2 without structural interpretation
```

### AMB-262 Full Information Chain

```
P1:
  text_a = "41M"
  text_b = "EfficientNet-B5"

P2:
  bbox_a = [188.6, 144.1, 201.4, 150.8]
  bbox_b = [213.4, 144.1, 256.5, 150.8]
  same_y_band = True
  h_gap = 12.0
  same-y band has 13 vlines with 4 column gaps

TLD:
  tables_detected = 0
  REASON: column_stability = 0.23 (threshold 0.75)
  → Band detection found 1 band (54 anchor rows), but:
    - Column centers: 4 (too few for 13-fragment rows)
    - Alignment: 0.23 (rows have varying column structures)
    - Text ratio: 0.52 (PASS, but column stability FAILS)

IS-01: is01_a = False ("41M" not pure number)
IS-02: is02_b = True ("EfficientNet-B5" has alpha > 2)

Current IS-11: fallback → mixed → ABSTAIN

Human: "41M" and "EfficientNet-B5" are values in different columns → KEEP_SEPARATE

DCE-01 to DCE-04 coverage:
  DCE-01 (fig): No
  DCE-02 (period+cap): No
  DCE-03 (both_numbers): No ("EfficientNet-B5" not pure number)
  DCE-04 (both_text): No ("41M" → is02_a = False, "M" has only 1 alpha char)
  → UNRESOLVED by DCE-01 to DCE-04

RE-VERIFICATION:
  AMB-262 does NOT have "DCE-05 missing" in the sense of "evidence doesn't exist."
  TLD data model CAN express different_column.
  TLD Detection Algorithm fails on this page (column stability 0.23 < 0.75).
  → This is TLD Detection Failure, NOT Evidence Missing.
  → D5-G (Mixed): TLD can express but detection fails.
```

### AMB-032 Separate Analysis

```
TLD: 1 table detected, A=[29,1], B=[29,2], different_cell=True
IS-11: different_cell → KEEP_SEPARATE (TN) — CORRECT

P722 B2: UNKNOWN (45.9s, expanded ALL 7 geometry fields)
  → P722 participant could NOT see TLD cell info
  → Participant only had geometry fields
  → Could not determine table membership from geometry alone

ANALYSIS:
  TLD correct → IS-11 correct (E1, consumed)
  P722 participant: Evidence Exposure Gap (TLD info not exposed)
  Human reviewer: Used table structure (from page visual) → KEEP

  Does Human still need column identity after TLD provides different_cell?
  NO. different_cell alone is sufficient for KEEP_SEPARATE.
  Human reviewer mentions "top-1 error" and "top-5 error" as explanation,
  but the DECISION is based on "different columns" (different_cell).

  P722 UNKNOWN is NOT because Human needs column identity.
  P722 UNKNOWN is because TLD cell info was NOT EXPOSED to participant.
  → This is an Evidence Exposure Gap (experiment UI), not Evidence Missing.
```

---

## 5. Human Dependency Analysis

### Human Column Dependency Assessment

| Case | Human Used Table Context | Human Used Column Context | Human Used Cell Context | Human Used Text Content | Column Dependency | Usage Status |
|---|---|---|---|---|---|---|
| AMB-135 | YES | YES (different columns) | YES (different cells) | YES (stage index, operator) | different_column | EXPLICIT |
| AMB-262 | YES | YES (different columns) | YES (different cells) | YES (41M, EfficientNet) | different_column | EXPLICIT |
| AMB-032 | YES | YES (different columns) | YES (different cells) | YES (top-1, top-5 error) | different_column | EXPLICIT |
| AMB-313 | YES | YES (different headers) | YES (different cells) | YES (Test Size, #Classes) | different_column | EXPLICIT |
| AMB-462 | YES | YES (different headers) | YES (different cells) | YES (WGe, Avg.) | different_column | EXPLICIT |
| AMB-024 | YES | YES | YES | YES | different_column | EXPLICIT |
| AMB-074 | YES | YES | YES | YES | different_column | EXPLICIT |
| AMB-346 | YES | YES | YES | YES | different_column | EXPLICIT |
| AMB-414 | NO | NO | NO | YES (FIG prefix) | NONE | N/A |
| AMB-519 | NO | NO | NO | YES (sentence boundary) | NONE | N/A |

### Key Finding

**ALL table cases: Human dependency = different_column (structural), NOT column_identity (semantic).**

- Column_identity ("stage index", "operator type") appears in rationale as EXPLANATION
- Decision-Critical evidence = "two separate columns" / "different columns" (different_column)
- different_column is STRUCTURAL (L3), not SEMANTIC (L4)

---

## 6. P2 Expressibility Test

| Question | P2 Can Express? | Evidence |
|---|---|---|
| 1. A/B same horizontal band? | **FULL** | same_y_band (y tolerance 3.0pt) |
| 2. A/B horizontally separated? | **FULL** | h_gap (x distance between bboxes) |
| 3. A/B belong to same local structure? | **PARTIAL** | same_y_band + multiple fragments → geometric pattern, but no structural interpretation |
| 4. A/B belong to same table? | **NOT_EXPRESSIBLE** | P2 has no table concept |
| 5. A/B belong to same row? | **PARTIAL** | same_y_band = same visual row, but P2 cannot confirm it's a table row |
| 6. A/B belong to different columns? | **NOT_EXPRESSIBLE** | P2 has no column concept |
| 7. A/B belong to different cells? | **NOT_EXPRESSIBLE** | P2 has no cell concept |

> **P2 can detect the GEOMETRIC PATTERN (same_y + multiple fragments + gaps) but CANNOT interpret it as TABLE COLUMNS. P2 provides L1 (geometry) and partial L2 (structural relation), but NOT L3 (structural interpretation).**

---

## 7. TLD Expressibility Test

### TLD Data Model Capability

| Feature | TLD Can Express? | How |
|---|---|---|
| table membership | **CAN_EXPRESS** | is_in_table (bbox containment check) |
| row membership | **CAN_EXPRESS** | a_cell[0] (row index from group_lines_into_rows) |
| column membership | **CAN_EXPRESS** | a_cell[1] (column index from sorted x position) |
| cell membership | **CAN_EXPRESS** | a_cell = [row, col] |
| different_cell | **CAN_EXPRESS** | a_cell != b_cell |
| headers | **CAN_EXPRESS** | headers list (first row of grid) |

### TLD Case Results

| Case | TLD Can Express? | TLD Result | Failure Reason |
|---|---|---|---|
| AMB-135 | CAN_EXPRESS | **MISS** (0 tables) | column_stability=0.27 (<0.75), text_ratio=0.38 (<0.45) |
| AMB-262 | CAN_EXPRESS | **MISS** (0 tables) | column_stability=0.23 (<0.75) |
| AMB-032 | CAN_EXPRESS | **CORRECT** (1 table, diff_cell) | — |
| AMB-313 | CAN_EXPRESS | **MISS** (0 tables) | consecutive multicol=1 (band not formed with target) |
| AMB-462 | CAN_EXPRESS | **PARTIAL** (1 table, but wrong) | TLD detected different table, missed target table |
| AMB-024 | CAN_EXPRESS | **CORRECT** | — |
| AMB-074 | CAN_EXPRESS | **CORRECT** | — |
| AMB-346 | CAN_EXPRESS | **CORRECT** | — |
| AMB-414 | CAN_EXPRESS | **CORRECT** (0 tables, correct) | Not a table (figure caption) |
| AMB-519 | CAN_EXPRESS | **WRONG** (1 table, FP) | TLD detected table on prose text |

### TLD Detection Failure Analysis

**AMB-135 Failure Chain:**
```
Page has 82 rows, 56 are multicol (mixed: formulas + table data + text)
TLD band detection: 1 band (indices 1-81, 56 anchor rows)
Column centers: 5 (mixed formula + table positions)
Column alignment: 0.27 (formulas don't align to table columns)
→ FAIL column stability (0.27 < 0.75)
Text ratio: 0.38 (many math fragments: '4', '56', '×', 'α', 'φ')
→ FAIL text ratio (0.38 < 0.45)
Result: 0 tables detected
```

**AMB-262 Failure Chain:**
```
Page has 82 rows, 54 are multicol (model comparison table + other content)
TLD band detection: 1 band (indices 3-81, 54 anchor rows)
Column centers: 4 (too few for 13-14 fragment rows)
Column alignment: 0.23 (rows have varying column structures)
→ FAIL column stability (0.23 < 0.75)
Text ratio: 0.52 (PASS)
Result: 0 tables detected
```

**Root Cause:** TLD's band detection is page-wide and greedy. When a page has mixed content (tables + formulas + text), the band includes everything, causing column instability.

---

## 8. DCE-05 Necessity Test

| Case | Without DCE-05 (different_column) | Result |
|---|---|---|
| AMB-135 | Machine: is01+is02 → MERGE (FP). Human: uses page visual → KEEP | R3 (Decision incorrect for machine) |
| AMB-262 | Machine: mixed → ABSTAIN. Human: uses page visual → KEEP | R2 (Decision UNKNOWN for machine) |
| AMB-032 | TLD provides different_cell → KEEP (TN) | R0 (Decision unchanged — DCE-05 provided) |
| AMB-313 | DCE-04 (both_text) resolves → KEEP | R0 (Resolved by DCE-04) |
| AMB-462 | DCE-04 (both_text) resolves → KEEP | R0 (Resolved by DCE-04) |
| AMB-024 | TLD provides different_cell → KEEP (TN) | R0 |
| AMB-074 | TLD provides different_cell → KEEP (TN) | R0 |
| AMB-346 | TLD provides different_cell → KEEP (TN) | R0 |
| AMB-414 | DCE-01 (has_fig) resolves → MERGE | R0 (Resolved by DCE-01) |
| AMB-519 | DCE-02 (period+cap) resolves → KEEP | R0 (Resolved by DCE-02) |

| Result | Count | Cases |
|---|---|---|
| R0 (unchanged) | 8 | AMB-032, AMB-313, AMB-462, AMB-024, AMB-074, AMB-346, AMB-414, AMB-519 |
| R2 (UNKNOWN/ABSTAIN) | 1 | AMB-262 |
| R3 (incorrect) | 1 | AMB-135 |

> **DCE-05 is Decision-Critical for ONLY 2/10 cases (AMB-135, AMB-262). For the other 8, either TLD already provides it (5 cases) or DCE-01 to DCE-04 resolve (3 cases).**

---

## 9. DCE-05 Sufficiency Test

| Question | Result |
|---|---|
| different_column alone → KEEP_SEPARATE? | **S3 (sufficient)** — when confirmed as table cells |
| different_column alone → MERGE? | NO — different_column → KEEP_SEPARATE |
| different_column → UNKNOWN? | NO — different_column is a definitive structural fact |

> **different_column alone is SUFFICIENT (S3) for KEEP_SEPARATE. This is already implemented in IS-11 (different_cell → KEEP_SEPARATE override).**

---

## 10. Semantic Leakage Test

```
different_column (structural fact)
  → KEEP_SEPARATE (boundary decision)

Is this a semantic leap?
  NO. different_column means the two text fragments are in different cells of a table.
  Table cells are atomic structural units.
  Different cells → different structural units → KEEP_SEPARATE.
  This is a STRUCTURAL inference, not a SEMANTIC judgment.

  Already implemented: IS-11 different_cell → KEEP_SEPARATE (FROZEN, 13/45 TN, 0 FP)

  DCE-05 ≠ Decision Rule (new)
  DCE-05 = Existing Decision Policy (already implemented)
  The issue is NOT the rule, but the EVIDENCE AVAILABILITY (TLD detection).
```

---

## 11. DCE Comparison

| DCE | Existing | Derivable | Decision-critical | Cross-corpus | Semantic leap | Status |
|---|---|---|---|---|---|---|
| DCE-01 FIG prefix | YES (P1) | YES (regex) | YES (2 cases) | NO (P7 FP) | NO | Corpus-specific pattern |
| DCE-02 period+cap | YES (P1) | YES (regex) | YES (3 cases) | NO (P7 FP) | NO | Corpus-specific + standard |
| DCE-03 both numeric | YES (P1) | YES (regex) | YES (7 cases) | UNKNOWN | NO | Unvalidated |
| DCE-04 both text | YES (P1) | YES (regex) | YES (5 cases) | NO (P7 FP) | NO | Corpus-specific pattern |
| **DCE-05 different_column** | **YES (TLD)** | **YES (TLD model)** | **YES (2 cases)** | **YES (universal)** | **NO** | **TLD Detection Failure** |

> **DCE-05 is the ONLY DCE that is: (1) universal (cross-corpus), (2) already implemented as decision policy, (3) already consumed by IS-11 when available. The gap is purely TLD Detection.**

---

## 12. E4 Re-Examination

### Previous Audit: E4 = 0

### This Audit's Finding

```
RAW_EVIDENCE_EXISTS = TRUE (P1 text + P2 geometry exist on ALL 45 cases)

DECISION_RELEVANT_REPRESENTATION:
  For 13/45 cases (TLD correct): FULL (different_cell provided and consumed)
  For 30/45 cases (TLD miss):
    - 28/30: Resolved by DCE-01 to DCE-04 (corpus-specific derivable features)
    - 2/30: different_column NOT ACHIEVED (AMB-135, AMB-262)
  
  → DECISION_RELEVANT_REPRESENTATION = PARTIAL (43/45 = 96% resolved, 2/45 = 4% missing)
  → The 2/45 "missing" is NOT raw evidence missing, but TLD Detection Failure
  → TLD data model CAN express it, but detection algorithm fails on specific pages
```

> **E4 (Evidence Missing) = 0 for raw evidence. But Decision-Relevant Structural Representation is PARTIAL: 2/45 cases where TLD fails to produce different_column. This is TLD Detection Failure, not raw evidence missing.**

---

## 13. DCE-05 Classification

```
D5-G (Mixed):
  When TLD detects (13/45): D5-A (Existing + Already Consumed)
    → TLD provides different_cell, IS-11 consumes → KEEP_SEPARATE (TN)
    → No gap
  
  When TLD fails (2/45): D5-C (Existing Low-Level Evidence but Representation not achieved)
    → P1 text + P2 geometry exist (raw evidence)
    → TLD data model CAN express different_column (representation capability exists)
    → TLD detection algorithm fails (representation not achieved on this case)
    → NOT D5-D (TLD is not a missing observation — it exists but fails)
    → NOT D5-B (Consumer doesn't lack integration — it consumes when available)
  
  NOT D5-D: TLD already provides the observation. No new observation needed.
  NOT D5-E: different_column is structural, not semantic. 0% E5.
  NOT D5-F: Not a standard issue (different_column → KEEP is already policy).
```

---

## 14. AMB-262 Re-Verification

```
Previous audit: AMB-262 = Type D (DCE-05 missing)

This audit:
  AMB-262 text: "41M" + "EfficientNet-B5"
  GT: KEEP_SEPARATE
  
  Does AMB-262 have same table / same row / different column structure?
    YES — same-y band has 13 vlines (clearly a table row)
    The page (EfficientNet page 7) has a model comparison table
    
  Does Human use column distinction?
    YES — rationale: "41M and EfficientNet-B5 are values in different columns"
    Decision-critical: different_column (structural)
  
  Is P1/P2 sufficient?
    P1: text exists
    P2: same_y_band=True, h_gap=12.0, 13 vlines on same y
    P2 CANNOT determine: these are table columns (NOT EXPRESSIBLE)
  
  Does TLD fail?
    YES — 0 tables detected
    REASON: column_stability=0.23 (< 0.75)
    TLD band too greedy (54 anchor rows from entire page)
  
  Is this Detection Failure or Representation Failure?
    DETECTION FAILURE — TLD data model CAN express different_column
    TLD detection algorithm fails due to column stability check
  
  DOWNGRADE from Type D:
    NOT Type D (Genuinely Missing Observation) — TLD observation exists
    IS TLD Detection Failure (observation capability exists, detection fails)
    → D5-G (Mixed): D5-A when TLD works + D5-C when TLD fails
```

---

## 15. Information Layer Assignment

```
same_y_band → L1 (Raw/Geometry Evidence)
h_gap → L1
multiple fragments on same y → L2 (Deterministic Structural Relation)
  (derivable from P2: same_y_band + fragment count + gap pattern)

different_column → L3 (Structural Interpretation)
  (requires table detection + cell assignment)
  TLD CAN express L3 (when detection works)
  P2 CANNOT express L3 (no table/column/cell concept)

column_identity → L4 (Semantic Interpretation)
  ("stage index" vs "operator type")
  NOT needed for Boundary Decision
  Human mentions as explanation, not as decision-critical evidence
  → DCE-05 is L3, NOT L4
```

---

## 16. Bottleneck Reassessment

### For DCE-05 specifically:

| Option | Verdict | Reason |
|---|---|---|
| A (Candidate Construction) | REJECTED | 0% Construction FP |
| B (Evidence Organization) | REJECTED | TLD organizes when it detects |
| C (Consumer Integration) | REJECTED | IS-11 consumes different_cell when TLD provides |
| **D (Evidence Perception)** | **PRIMARY** | TLD detection fails on 2/45 cases |
| E (Human Semantic Judgment) | REJECTED | 0% E5, different_column is structural |
| F (Evaluation Standard) | REJECTED | different_cell → KEEP is already policy |
| G (Evidence Insufficient) | PARTIAL | 2/45 cases where representation not achieved |
| H (Mixed) | ACCEPTABLE | D + G |

### For Overall System (all 45 cases):

| Bottleneck | Cases | % |
|---|---|---|
| C (Consumer Integration) — DCE-01 to DCE-04 | 17 | 38% |
| D (Evidence Perception) — DCE-05 TLD Detection | 2 | 4% |
| NONE (TLD correct) | 13 | 29% |
| NONE (Fallback correct) | 13 | 29% |

> **PRIMARY_BOTTLENECK = C (Consumer Integration) — 17/45 cases (DCE-01 to DCE-04)**
> **SECONDARY_BOTTLENECK = D (Evidence Perception) — 2/45 cases (DCE-05 TLD Detection)**

### Key Correction from Previous Audit

Previous audit classified DCE-05 as:
- "DCE-05: table_column_identity (semantic/structural) — NOT deterministic — requires semantic/structural capability"
- "Type D: Missing + Critical — requires TLD improvement or equivalent"

This audit corrects:
- DCE-05 is NOT "table_column_identity" (semantic) — it's "different_column" (structural)
- TLD CAN express it (deterministic structural relation, not semantic)
- The gap is NOT "missing observation" — it's "TLD detection failure"
- The bottleneck is NOT C (Consumer Integration) for DCE-05 — it's D (Evidence Perception)
- IS-11 already has the decision policy (different_cell → KEEP_SEPARATE)
- IS-11 already consumes it when TLD provides it

---

## 17. LLM and New Observation Assessment

```
LLM_NEEDED = NO
  different_column is a STRUCTURAL fact, not a semantic judgment.
  TLD already computes it deterministically (when detection works).
  No semantic understanding needed.

NEW_OBSERVATION_NEEDED = NO
  TLD already provides the observation (is_in_table, different_cell, a_cell, b_cell).
  The issue is TLD DETECTION ALGORITHM, not missing observation.
  No new module/engine/observation needed.
```

---

## 18. Learning Signal Analysis

| LS Level | Count | Description |
|---|---|---|
| LS-0 | 8 | TLD provides different_cell, IS-11 consumes → TN (no new info) |
| LS-1 | 0 | No existing evidence unused (IS-11 consumes when TLD provides) |
| LS-2 | 0 | No derivable relations (different_column requires TLD, not regex) |
| LS-3 | 0 | No reusable signal (TLD detection failure is algorithm-specific, not a signal) |

> **0% LS-3. DCE-05 does not produce Learning Signal. The gap is TLD Detection Algorithm, not Learning.**

---

## 19. Anti-Overdesign Review

```
Proposed new layers: NONE
  - No Evidence Organization Engine (evidence is organized when TLD works)
  - No Relation Engine (TLD provides cell relations)
  - No Semantic Engine (different_column is structural, not semantic)
  - No Discourse Engine (not needed)
  - No Learning Engine (0 LS-3)
  - No LLM (structural fact, not semantic)
  - No Pattern Engine (no reusable pattern)
  - No Query Engine (not needed)

The ONLY finding: TLD Detection Algorithm has coverage limitations.
  - This is a TLD internal algorithm issue, not a new layer.
  - TLD is FROZEN — cannot be modified in this audit.
  - Any improvement would require TLD modification (not authorized).
```

---

## 20. Final Questions

### Q1: table_column_identity 是不是真的 Decision-Critical?

**NO — "table_column_identity" (semantic) is NOT Decision-Critical.**
**"different_column" (structural) IS Decision-Critical for 2/45 cases.**

### Q2: Human 是否真的依赖它?

**YES — Human depends on different_column (structural), NOT column_identity (semantic).**
All reviewer rationales use "different columns" as decision-critical evidence.

### Q3: 它目前在哪里?

**In TLD data model.** TLD computes is_in_table, a_cell, b_cell, different_cell.
- Available: 13/45 cases (TLD correct)
- Unavailable: 2/45 cases (TLD detection failure)

### Q4: 缺的是 Raw Evidence 还是 Decision-Relevant Representation?

**Decision-Relevant Representation PARTIALLY missing.**
- Raw evidence (P1 text, P2 geometry) exists on ALL 45 cases
- TLD representation (different_cell) exists on 43/45 cases (13 TLD + 30 DCE-01-04)
- TLD representation missing on 2/45 cases (AMB-135, AMB-262) due to Detection Failure

### Q5: TLD 是否已经具备表达它的能力?

**YES — TLD data model CAN express different_column.**
Proven on 13/45 cases where TLD correctly detects and IS-11 correctly consumes.

### Q6: 如果 TLD 有能力但 Case 失败，是 Detection Failure 还是 Consumer Integration?

**Detection Failure.**
- TLD detection algorithm fails (column stability < 0.75, text ratio < 0.45)
- IS-11 consumer correctly consumes different_cell when TLD provides it
- The gap is in TLD's DETECTION, not in IS-11's CONSUMPTION

### Q7: 下一步最小解决方向?

**Structural Representation (TLD Detection Algorithm improvement).**
- NOT Consumer Integration (already integrated)
- NOT New Observation (TLD already provides it)
- NOT Evaluation Standard (already policy)
- NOT No Action (2 cases unresolved)
- TLD Detection Algorithm needs improvement (but TLD is FROZEN, not authorized)

---

## 21. Limitations

1. **TLD Detection Diagnosis**: Diagnosis is from TLD source code analysis and direct execution. Production TLD (if different) may have different behavior.

2. **2-Case Sample**: DCE-05 is Decision-Critical for only 2/45 cases. Statistics are not generalizable.

3. **TLD Frozen**: TLD cannot be modified. Any detection improvement would require TLD modification (not authorized in this audit).

4. **Column Identity vs Different Column**: The distinction is inferred from reviewer rationales (text analysis), not from eye-tracking or think-aloud protocols.

5. **P7 Cross-Validation**: P7 has no TLD, so DCE-05 cannot be cross-validated on P7.

6. **AMB-462 Partial Detection**: TLD detected a table but not the one containing A/B. This is classified as PARTIAL, but the root cause might be different from AMB-135/AMB-262.

---

## 22. Statistics

```
TOTAL_CASES_ANALYZED: 10 (5 focus + 5 controls)

DCE05_CASES: 10
DCE05_CRITICAL_COUNT: 2 (AMB-135, AMB-262)
DCE05_RELEVANT_COUNT: 3 (AMB-313, AMB-462 — resolved by DCE-04; AMB-032 — resolved by TLD)
DCE05_SUPPORTING_COUNT: 5 (TLD-correct controls)
DCE05_REDUNDANT_COUNT: 0

R0_COUNT: 8
R1_COUNT: 0
R2_COUNT: 1 (AMB-262)
R3_COUNT: 1 (AMB-135)

S0_COUNT: 0
S1_COUNT: 0
S2_COUNT: 0
S3_COUNT: 2 (AMB-135, AMB-262 — different_column alone sufficient)

RAW_EVIDENCE_EXISTS_COUNT: 10/10 (100%)
DECISION_RELEVANT_REPRESENTATION_EXISTS_COUNT: 8/10 (80%)
DECISION_RELEVANT_REPRESENTATION_PARTIAL_COUNT: 0
DECISION_RELEVANT_REPRESENTATION_MISSING_COUNT: 2/10 (20%)

P2_FULL_COUNT: 2 (same_y_band, h_gap)
P2_PARTIAL_COUNT: 2 (same local structure, same row)
P2_NOT_EXPRESSIBLE_COUNT: 3 (same table, different columns, different cells)

TLD_CAN_EXPRESS_COUNT: 10/10 (100% — data model capability)
TLD_CORRECT_COUNT: 6/10 (60%)
TLD_MISS_COUNT: 3/10 (30%)
TLD_PARTIAL_COUNT: 1/10 (10%)
TLD_WRONG_COUNT: 1/10 (10% — AMB-519 FP on prose)

HUMAN_COLUMN_DEPENDENCY_COUNT: 8/10 (80% — all table cases)
HUMAN_TABLE_DEPENDENCY_COUNT: 8/10 (80%)
HUMAN_TEXT_DEPENDENCY_COUNT: 10/10 (100%)
HUMAN_SEMANTIC_DEPENDENCY_COUNT: 0/10 (0%)
HUMAN_USAGE_UNCERTAIN_COUNT: 0/10 (0%)

DCE05_TYPE: D5-G (Mixed: D5-A when TLD works + D5-C when TLD fails)

LLM_NEEDED: NO
NEW_OBSERVATION_NEEDED: NO

LS0_COUNT: 8
LS1_COUNT: 0
LS2_COUNT: 0
LS3_COUNT: 0

PRIMARY_BOTTLENECK (DCE-05): D (Evidence Perception / TLD Detection Failure)
SECONDARY_BOTTLENECK: G (Evidence Insufficient on 2 cases)

TRUE_REUSABLE_SIGNAL_FOUND: NO
CURRENT_LEARNING_LEVEL: L3
RECOMMENDED_NEXT_STEP: READ_ONLY_AUDIT
```

---

## 23. Final Answer

```
P1/P2/TLD
   ↓
能不能安全得到 "same row + different column"
   ↓
YES (TLD data model CAN express)
   ↓
但 TLD Detection Algorithm 在 2/45 cases 上 FAILS
   ↓
问题属于: D (Evidence Perception / TLD Detection Failure)
   ↓
NOT Consumer Integration (IS-11 already consumes when TLD provides)
NOT Representation Missing (TLD data model can express)
NOT Semantic Judgment (different_column is structural)
NOT New Observation (TLD already provides it)
```

---

## 24. Governance Gate

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
