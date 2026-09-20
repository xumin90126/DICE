# DCE-07 TLD Band Locality Counterfactual Audit

**Date**: 2026-09-15
**Mode**: READ-ONLY / COUNTERFACTUAL AUDIT / NO MODIFICATION / FROZEN INTACT / STOP
**Predecessor**: DCE-06 TLD Failure Mechanism Audit

---

## 1. Executive Summary

```
FINAL_STATUS = LOCALITY_IS_PLAUSIBLE_BUT_UNSAFE
               ROUTE_CLOSED

COUNTERFACTUAL VERDICT:
  3 locality bases tested (L1, L2, L3).
  None safely recovers failure cases without creating false positives.

L1 (Candidate-centered locality):
  With correct TLD anchors (len>=2): NOT_SUPPORTED
    → Band extends to page boundary (no wide_text breakers between candidate and edges)
    → Result = same as actual TLD (no recovery, no regression)
  With modified anchors (is_multicol): PLAUSIBLE_BUT_UNSAFE
    → Recovers AMB-262 (1/3 failures)
    → Creates FALSE POSITIVES on AMB-008 (prose, align=0.805) and AMB-042 (prose, align=1.000)
    → Changes TLD internal logic (anchor definition), not just band scope → INVALID counterfactual

L2 (Geometry-locality by column-pattern break):
  Does not create local bands (prose and table share x-positions)
  Creates REGRESSIONS on success cases (AMB-032: 3 tables instead of 1, AMB-346: 2 instead of 1)
  Creates FALSE POSITIVES on negative controls (AMB-008: 2 tables, AMB-042: 1 table)

L3 (Existing TLD structural locality):
  = actual TLD (wide_text breaker is the only locality mechanism)
  NOT_SUPPORTED for failure cases (no wide_text breakers on failure pages)

FUNDAMENTAL ISSUE:
  Locality ≠ Table.
  A local region of prose with citations has the same geometric properties as a table:
    - same_y_band (multiple fragments on same y)
    - x-gaps ≥ 12pt (citation formatting)
    - stable column alignment (prose has regular x-positions)
    - sufficient text ratio (prose contains text words)
    - y-spacing regularity (some prose regions have regular spacing)
  Without semantic content understanding, there is NO geometric signal that
  safely distinguishes "prose with citations" from "table data".

LOCAL ISOLATION (DCE-06) PROVES:
  The table CAN pass TLD checks when manually isolated.
  BUT: no geometry-only method can automatically find the table boundaries.

AMB-462 (Mechanism 2):
  Locality does NOT help.
  text_ratio=0.163 is inherent (numeric table), not contamination.
  Locality cannot solve Mechanism 2.

RECOVERY: 0/3 Mechanism 1 failures safely recovered (with correct TLD anchors)
REGRESSION: 2/3 negative controls become false positives (with modified anchors)
TP PRESERVATION: 3/3 success cases preserved (with correct anchors)

CLASSIFICATION: L1 = PLAUSIBLE_BUT_UNSAFE
  → Route CLOSED
  → Does NOT proceed to minimal design stage

NEXT_MINIMAL_RESEARCH_TARGET = UNKNOWN
  Band Locality: CLOSED (unsafe)
  Column Stability: THRESHOLD_TUNING (forbidden)
  Text Ratio: THRESHOLD_TUNING (forbidden)
  Other mechanism: NONE_IDENTIFIED

LLM_NEEDED = NO
NEW_OBSERVATION_NEEDED = NO
NEW_MODULE_NEEDED = NO

STOP = TRUE
```

---

## 2. Research Question

> **如果 TLD 的 Band Formation 具有合理的 Locality，而不是把整个页面内容放进一个 Global Band，现有 TLD 是否能够恢复这些失败案例中的 Table Structure？**

> **这种 Locality 是否会导致明显的 False Positive / collateral damage？**

**Answer:**

1. Locality CAN recover AMB-262 (when using modified anchors), but NOT AMB-135 or AMB-313.
2. Locality creates UNACCEPTABLE false positives on prose pages (AMB-008, AMB-042).
3. With correct TLD anchors, locality does NOT create local bands at all (band extends to page boundary).
4. **Locality is PLAUSIBLE_BUT_UNSAFE. Route CLOSED.**

---

## 3. Counterfactual Methods

### L1: Candidate-centered Locality

**Principle**: Only allow rows within proximity of the target candidate's y-position to participate in band/column analysis.

**Implementation**: Starting from the candidate's row, extend up/down while consecutive rows are multicol or short_single. Break on wide_text or y-discontinuity (> 2.5× row height).

**Evidence basis**: P2 geometry (candidate bbox y, row y-continuity, multicol classification).

**Two variants tested**:
- L1-correct: Uses TLD's exact anchor definition (`len(rows[i]) >= 2`)
- L1-modified: Uses `is_multicol` for anchors (changes TLD internal logic)

### L2: Geometry-locality by Column-pattern Break

**Principle**: Scan all rows. Form bands of consecutive multicol rows. Break when a row's x-positions don't align (>50%) to the band's established column centers.

**Implementation**: Track running column centers. When a new multicol row's alignment to current centers drops below 50%, break the band.

**Evidence basis**: P2 geometry (x-positions, column clustering, alignment ratio).

### L3: Existing TLD Structural Locality

**Principle**: Use TLD's existing band formation as-is. The wide_text breaker is the only locality mechanism.

**Implementation**: = actual TLD.

**Evidence basis**: Frozen TLD source code.

---

## 4. Cases

| Case | Role | Page | PDF | Actual TLD | Target |
|---|---|---|---|---|---|
| AMB-135 | FAILURE (M1+M2) | 5 | efficientnet | 0 tables | Table (architecture spec) |
| AMB-262 | FAILURE (M1) | 7 | efficientnet | 0 tables | Table (model comparison) |
| AMB-313 | FAILURE (M1) | 8 | efficientnet | 0 tables | Table (transfer learning) |
| AMB-462 | FAILURE (M2) | 3 | cs_001 | 1 table (wrong) | Table (benchmark scores) |
| AMB-032 | SUCCESS | 6 | resnet | 1 table (correct) | Table |
| AMB-074 | SUCCESS | 8 | resnet | 1 table (correct) | Table |
| AMB-346 | SUCCESS | 9 | resnet | 1 table (correct) | Table |
| AMB-008 | NEGATIVE | 3 | resnet | 0 tables | Prose with citations |
| AMB-042 | NEGATIVE | 7 | resnet | 0 tables | Prose + table-like content |
| AMB-397 | NEGATIVE | 19 | med_001 | 0 tables | Formula/prose |
| AMB-519 | PARTIAL | 3 | cs_001 | 1 table (FP on prose) | Prose |
| AMB-414 | PARTIAL | 20 | med_001 | 0 tables | Figure caption |

**Negative control selection rationale**: AMB-008 (resnet page 3), AMB-042 (resnet page 7), and AMB-397 (med page 19) have high multicol content (29, 22, 29 multicol rows respectively) with 0 wide_text breakers — the same conditions as failure cases. TLD correctly returns 0 tables because global column alignment is low. These are the HARDEST negative controls (if locality creates false positives here, it's unsafe).

---

## 5. Counterfactual Results

### L1-correct (Candidate-centered, TLD exact anchors)

| Case | Actual | L1-correct | Align | Text Ratio | Fail Stage | Band Size | Anchors | Recovered | Regression |
|---|---|---|---|---|---|---|---|---|---|
| AMB-135 | 0 | 0 | 0.268 | 0.382 | E | 81 | 56 | NO | NO |
| AMB-262 | 0 | 0 | 0.226 | 0.518 | E | 79 | 54 | NO | NO |
| AMB-313 | 0 | 0 | 0.538 | 0.585 | E | 61 | 41 | NO | NO |
| AMB-462 | 1 | 0 | 1.000 | 0.163 | F | 8 | 8 | NO | NO |
| AMB-032 | 1 | 1 | 0.986 | 0.760 | NONE | 86 | 47 | N/A | NO |
| AMB-074 | 1 | 1 | 0.973 | 0.772 | NONE | 63 | 35 | N/A | NO |
| AMB-346 | 1 | 1 | 0.995 | 0.909 | NONE | 66 | 36 | N/A | NO |
| AMB-008 | 0 | 0 | 0.410 | 0.524 | E | 82 | 45 | N/A | NO |
| AMB-042 | 0 | 0 | 0.717 | 0.617 | E | 85 | 39 | N/A | NO |
| AMB-397 | 0 | 0 | 0.814 | 0.159 | F | 36 | 33 | N/A | NO |
| AMB-519 | 1 | 1 | 1.000 | 0.611 | NONE | 8 | 7 | N/A | NO |
| AMB-414 | 0 | 0 | 1.000 | 0.386 | F | 26 | 11 | N/A | NO |

**L1-correct analysis**: Band sizes are 81-86 for failure/negative cases (essentially the entire page). The candidate-centered extension goes to page boundaries because there are no wide_text breakers. **L1-correct = actual TLD** (no change). No recovery, no regression.

### L1-modified (Candidate-centered, is_multicol anchors)

| Case | Actual | L1-mod | Align | Text Ratio | Fail Stage | Recovered | Regression |
|---|---|---|---|---|---|---|---|
| AMB-135 | 0 | 0 | 0.512 | 0.382 | E | NO | NO |
| AMB-262 | 0 | **1** | 0.755 | 0.518 | NONE | **YES** | NO |
| AMB-313 | 0 | 0 | 0.616 | 0.585 | E | NO | NO |
| AMB-462 | 1 | 0 | 1.000 | 0.163 | F | NO | NO |
| AMB-032 | 1 | 1 | 1.000 | 0.760 | NONE | N/A | NO |
| AMB-074 | 1 | 1 | 0.975 | 0.772 | NONE | N/A | NO |
| AMB-346 | 1 | 1 | 0.993 | 0.909 | NONE | N/A | NO |
| AMB-008 | 0 | **1** | 0.805 | 0.524 | NONE | N/A | **YES (FP)** |
| AMB-042 | 0 | **1** | 1.000 | 0.617 | NONE | N/A | **YES (FP)** |
| AMB-397 | 0 | 0 | 0.888 | 0.159 | F | N/A | NO |

**L1-modified analysis**: Recovers AMB-262 (1/3) but creates false positives on AMB-008 and AMB-042 (prose pages). The modified anchor definition (`is_multicol` instead of `len >= 2`) removes TLD's formula rejection mechanism, allowing prose to pass. **INVALID counterfactual** — changes TLD internal logic, not just band scope.

### L2 (Geometry-locality by column-pattern break)

| Case | Actual | L2 | Bands | Tables | Recovered | Regression |
|---|---|---|---|---|---|---|
| AMB-135 | 0 | 0 | 1 (page-global) | 0 | NO | NO |
| AMB-262 | 0 | 0 | 1 (page-global) | 0 | NO | NO |
| AMB-313 | 0 | 0 | 1 (page-global) | 0 | NO | NO |
| AMB-462 | 1 | 1 | 2 | 1 | NO | NO |
| AMB-032 | 1 | **3** | 3 | 3 | N/A | **YES (split)** |
| AMB-074 | 1 | 1 | 1 | 1 | N/A | NO |
| AMB-346 | 1 | **2** | 2 | 2 | N/A | **YES (split)** |
| AMB-008 | 0 | **2** | 2 | 2 | N/A | **YES (FP)** |
| AMB-042 | 0 | **1** | 1 | 1 | N/A | **YES (FP)** |
| AMB-397 | 0 | 0 | 2 | 0 | N/A | NO |

**L2 analysis**: Column-pattern break (50% threshold) doesn't create local bands on failure cases (prose shares x-positions with tables). Creates REGRESSIONS: splits success tables into multiple fragments, creates false positives on prose. **UNSAFE.**

### L3 (Existing TLD)

L3 = actual TLD. The wide_text breaker is the only locality mechanism. On failure pages (AMB-135, AMB-262, AMB-313), there are 0-2 wide_text rows (all above the table, none below), so the band extends to page bottom. **NOT_SUPPORTED** for failure cases.

---

## 6. Why L1-correct Doesn't Create Local Bands

```
L1 candidate-centered extension logic:
  1. Start at target row (candidate's y-position)
  2. Extend upward: while row is multicol OR short_single → absorb
     Break on: wide_text OR y-discontinuity (> 2.5× row height)
  3. Extend downward: same logic

On failure pages (AMB-135, AMB-262, AMB-313):
  - Target row is multicol (table row)
  - Above target: 0-2 wide_text rows (title, abstract) → break quickly
  - Below target: NO wide_text rows → extend to page bottom
  - All non-table rows below target are either:
    - multicol (prose with citations, formulas) → absorbed as ANCHOR
    - short_single (section numbers, labels) → absorbed as non-anchor
    - other (2+ fragments, no x-gaps) → absorbed if y-continuous
  - Result: band = entire page (same as actual TLD)

On success pages (AMB-032, AMB-074, AMB-346):
  - Table dominates page (95-97% coverage)
  - Band = table (same as actual TLD)
  - No change needed

On negative control pages (AMB-008, AMB-042):
  - All rows are multicol or short_single
  - No wide_text breakers → band = entire page
  - With correct TLD anchors: align < 0.75 → correctly rejected
  - With modified anchors: align > 0.75 → FALSE POSITIVE
```

**Root cause**: The candidate-centered extension uses the SAME absorption logic as TLD's band formation (multicol = anchor, short_single = absorb, wide_text = break). Since failure pages have no wide_text breakers below the table, the extension goes to page bottom. **Changing the starting point doesn't change the band scope.**

---

## 7. Why L1-modified Creates False Positives

```
AMB-008 (resnet page 3 — PROSE with citations):
  Actual TLD: 0 tables (align=0.410 with len>=2 anchors)
  L1-modified: 1 table (align=0.805 with is_multicol anchors)

  Why the difference?
    TLD anchors (len>=2): includes 45 rows (29 multicol + 16 non-multicol 2+ fragment)
    Modified anchors (is_multicol): includes only 29 rows

    The 16 non-multicol 2+ fragment rows are FORMULA fragments:
      "F | ( | x | )+"  (formula, fragments close together, no x-gaps >= 12pt)
      "We can also use | W | in Eqn.(1). But" (prose with embedded formula)

    These formula fragments have x-positions that DON'T align to prose columns.
    When included (TLD anchors): they pull column centers away → alignment drops to 0.410
    When excluded (modified anchors): prose columns cluster nicely → alignment rises to 0.805

  PROBLEM: The modified anchor definition removes TLD's formula rejection mechanism.
  TLD deliberately uses len>=2 (not is_multicol) to include formula fragments in
  column center computation, because formula fragments DESTABILIZE column centers
  and help reject non-table regions.

  By using is_multicol, we disable this protection → prose passes as table.
```

---

## 8. Why L2 Doesn't Work

```
L2 column-pattern break: break band when row alignment to current centers < 50%

On AMB-135 (failure):
  First multicol row (prose at y=69.5): establishes initial centers
    x-positions: ~55, ~127, ~310, ~346 (prose + citation positions)
  Table rows (y=111-210): fragments at x=127, 152, 320, 354, 428, 482, 521
    Some align to prose centers (127 → 127, 320 → 310 within 16pt)
    Alignment: ~50% (borderline, doesn't trigger break)
  Contaminating rows (y=310+): mixed positions, some align, some don't
  Result: band never breaks → 1 page-global band (same as actual)

On AMB-032 (success — TABLE SPLITS):
  Table has 38 multicol rows with consistent columns
  Some rows have slightly different x-positions (different table sections)
  L2 breaks at these points → 3 separate bands → 3 tables (was 1)
  REGRESSION: one table split into three

FUNDAMENTAL ISSUE:
  Prose with citations and table data share x-positions:
    - Left margin (~55pt): both prose and table start here
    - Citation positions (~127, ~310): prose citations and table columns overlap
  Column-pattern consistency CANNOT distinguish them.
```

---

## 9. Geometric Signal Tests

### Y-spacing Regularity

| Case | Region | Mean Gap | Stdev | CV | Regular? |
|---|---|---|---|---|---|
| AMB-135 | TABLE | 7.1pt | 3.0 | 0.42 | NO |
| AMB-135 | NON-TABLE | 39.8pt | 54.7 | 1.37 | NO |
| AMB-262 | TABLE | 8.6pt | 1.3 | 0.16 | YES |
| AMB-262 | NON-TABLE | 12.2pt | 9.9 | 0.81 | NO |
| AMB-313 | TABLE | 7.9pt | 3.1 | 0.39 | NO |
| AMB-042 (NEG) | TABLE-like | 12.0pt | 0.2 | 0.01 | YES |

**Analysis**: Y-spacing regularity distinguishes table from non-table on AMB-262 (CV 0.16 vs 0.81) but NOT on AMB-135 (0.42) or AMB-313 (0.39 — both irregular). And AMB-042 (negative control) has CV=0.01 (very regular) — would create false positive. **UNSAFE.**

### Fragment Count Consistency

| Case | Region | Mean Fragments | Stdev | CV | Consistent? |
|---|---|---|---|---|---|
| AMB-135 | TABLE | 7.6 | 2.7 | 0.36 | NO |
| AMB-135 | NON-TABLE | 7.4 | 7.4 | 1.00 | NO |
| AMB-262 | TABLE | 11.9 | 3.8 | 0.32 | NO |
| AMB-032 | ALL | 3.6 | 1.7 | 0.49 | NO |
| AMB-008 | ALL | 4.8 | 5.1 | 1.07 | NO |

**Analysis**: Fragment count consistency does NOT distinguish table from non-table. **NOT_SUPPORTED.**

---

## 10. Recovery Analysis

```
L1-correct:
  RECOVERY_COUNT = 0/3 (AMB-135, AMB-262, AMB-313 all still fail)
  RECOVERY_RATE = 0%
  → Band extends to page boundary = same as actual TLD

L1-modified:
  RECOVERY_COUNT = 1/3 (AMB-262 recovered)
  RECOVERY_RATE = 33%
  → But INVALID counterfactual (changes anchor definition)
  → And creates false positives

L2:
  RECOVERY_COUNT = 0/3
  RECOVERY_RATE = 0%
  → Column-pattern break doesn't trigger

L3:
  RECOVERY_COUNT = 0/3
  RECOVERY_RATE = 0%
  → = actual TLD

COUNTERFACTUAL RECOVERY RATE (L1-correct, valid): 0%
```

---

## 11. Regression Analysis

```
L1-correct:
  REGRESSION_COUNT = 0/7 (3 success + 3 negative + 1 partial)
  TP_PRESERVED = 3/3
  FP_CREATED = 0/3

L1-modified:
  REGRESSION_COUNT = 2/7 (AMB-008 FP, AMB-042 FP)
  TP_PRESERVED = 3/3
  FP_CREATED = 2/3 (prose pages accepted as tables)

L2:
  REGRESSION_COUNT = 4/7 (AMB-032 split, AMB-346 split, AMB-008 FP, AMB-042 FP)
  TP_PRESERVED = 1/3 (only AMB-074 preserved correctly)
  FP_CREATED = 2/3
  TP_SPLIT = 2/3 (success tables fragmented)
```

---

## 12. Mechanism 2 Control (AMB-462)

```
AMB-462 (Mechanism 2 — Inherent Low Text Ratio):
  Actual: 1 table (wrong table, Band 0 accepted, Band 1 rejected at text_ratio=0.163)
  L1-correct: 0 tables (Band 1 text_ratio=0.163, FAIL at Stage F)
  L1-modified: 0 tables (same)
  L2: 1 table (same as actual — Band 0 accepted, Band 1 rejected)

  Locality does NOT help AMB-462.
  text_ratio=0.163 is inherent (67/80 cells are numeric benchmark scores).
  Band is already properly isolated (2 bands, wide_text separator exists).
  The failure is Mechanism 2 (text_ratio threshold), NOT Mechanism 1 (contamination).

  CONFIRMED: Locality cannot solve Mechanism 2.
```

---

## 13. Locality Safety Analysis

### Core Question: Locality ≠ Table?

**PROVEN UNSAFE.**

Evidence:
1. **AMB-008 (prose with citations)**: Local isolation gives align=0.805, text_ratio=0.524 → ACCEPTED as table. But this is PROSE, not a table. 27/29 multicol rows are prose-like (contain spaces, commas).

2. **AMB-042 (prose + table-like content)**: Local isolation gives align=1.000, text_ratio=0.617 → ACCEPTED as table. 22/22 multicol rows are prose-like. The page has a small table mixed with prose, but the locality method accepts the ENTIRE page as one table.

3. **Y-spacing regularity**: AMB-042 (negative control) has CV=0.01 (more regular than actual table AMB-262's CV=0.16). This signal would create false positives.

### Why Prose Looks Like a Table Locally

```
Prose with citations:
  "In fact, a few prior | Zoph et al. | , | 2018 | ; | Real et al."
  → 6 fragments on same y, with x-gaps ≥ 12pt
  → Appears as multicol (same as table row)
  → Fragments at consistent x-positions across paragraphs (left margin, citation position)
  → Column alignment HIGH (prose has regular formatting)
  → Text ratio HIGH (prose contains text words)

Table data:
  "1 | Conv3x3 | 224 | × | 224 | 32 | 1"
  → 7 fragments on same y, with x-gaps ≥ 12pt
  → Appears as multicol
  → Fragments at consistent x-positions across rows
  → Column alignment HIGH
  → Text ratio VARIABLE (numeric tables fail, text tables pass)

GEOMETRIC PROPERTIES ARE IDENTICAL.
Without semantic content understanding, there is NO geometric signal
that safely distinguishes prose with citations from table data.
```

---

## 14. Negative Control Analysis

| Control | Page Content | MC Rows | Wide Text | Actual TLD | L1-correct | L1-modified | L2 |
|---|---|---|---|---|---|---|---|
| AMB-008 | Prose + formulas + citations | 29 | 0 | 0 tables ✓ | 0 ✓ | **1 FP** ✗ | **2 FP** ✗ |
| AMB-042 | Prose + table-like content | 22 | 0 | 0 tables ✓ | 0 ✓ | **1 FP** ✗ | **1 FP** ✗ |
| AMB-397 | Formulas + prose | 29 | 0 | 0 tables ✓ | 0 ✓ | 0 ✓ | 0 ✓ |

**AMB-008 and AMB-042 have 0 wide_text breakers** — the same condition as failure cases. This is the hardest test for locality. L1-modified and L2 both create false positives on these pages, proving locality is unsafe.

**AMB-397 survives** because its content is formula-heavy (text_ratio=0.159 < 0.45), which blocks false positives regardless of alignment. But this is the text_ratio check saving us, not locality.

---

## 15. Success vs Failure Comparison

| Metric | Failure (135/262/313) | Success (032/074/346) | Negative (008/042) | Distinguishes? |
|---|---|---|---|---|
| MC count | 31/37/31 | 38/41/24 | 29/22 | NO (overlap) |
| Wide text | 1/2/1 | 0/0/1 | 0/0 | NO (failure & negative both have 0-2) |
| Band size | 81/79/61 | 86/63/66 | 82/85 | NO (all page-global) |
| Table/page % | 15/11/12% | 95/95/97% | N/A | YES but requires GT |
| Global align | 0.27/0.23/0.54 | 0.99/0.75/1.0 | 0.41/0.72 | PARTIALLY (but 0.72 borderline) |
| Local align | 0.99/1.0/0.96 | N/A (= global) | 0.81/1.0 | NO (negative also high locally) |
| Y-spacing CV | 0.42/0.16/0.39 | N/A | N/A/0.01 | NO (negative has lower CV) |

**No geometric metric safely distinguishes failure cases from negative controls.** The only distinguishing factor is table/page coverage (requires GT) and global alignment (but negative controls can have alignment up to 0.72, close to the 0.75 threshold).

---

## 16. Anti-Overdesign Gate

```
NEW_OBSERVATION_NEEDED = NO
  P1/P2 provides sufficient L1/L2 geometry.
  The issue is not missing observation but inability to distinguish
  prose from table using geometry alone.

NEW_MODULE_NEEDED = NO
  No new module would help without semantic understanding.
  A "locality module" would need table/non-table classification,
  which requires semantic understanding (forbidden).

NEW_ENGINE_NEEDED = NO
  No new processing pipeline needed.

LLM_NEEDED = NO
  The failure is geometric (can't distinguish prose from table),
  not semantic. LLM would be overkill and is forbidden.
  
  However: the fundamental issue (prose vs table distinction)
  IS a semantic problem. This audit does NOT recommend LLM —
  it reports that the geometric route is closed.
  Whether a semantic route exists is a separate question
  that this audit does NOT address.

FORBIDDEN ESCALATIONS:
  ✗ Locality Failure → "Table Understanding Engine" (NO)
  ✗ Locality Failure → "Document Understanding Engine" (NO)
  ✗ Locality Failure → "Discourse Engine" (NO)
  ✗ Locality Failure → "LLM Table Reasoner" (NO)
  ✗ Locality Failure → "Evidence Organization Engine" (NO)
  ✗ Locality Failure → "Relation Engine" (NO)
  ✗ Locality Failure → "Pattern Engine" (NO)
  ✗ Locality Failure → "Learning Engine" (NO)
```

---

## 17. Learning Signal Gate

```
TRUE_REUSABLE_SIGNAL_FOUND = NO

  Observed phenomena:
    - "local isolation passes" (table CAN pass TLD checks when manually isolated)
    - "prose with citations looks like table" (geometric properties identical)
    - "y-spacing regularity" (works on some cases, fails on others)
  
  These are OBSERVED PHENOMENA, NOT generalizable learning signals.
  
  "local isolation passes" ≠ Learning Signal (requires GT to identify table region)
  "prose looks like table" ≠ Learning Signal (is a limitation, not a signal)
  "y-spacing regularity" ≠ Learning Signal (not generalizable, creates FP)
  
  No new Learning Signal created.
  No existing Learning Signal modified.
```

---

## 18. Classification

```
L0 = NOT_SUPPORTED
L1 = PLAUSIBLE_BUT_UNSAFE
L2 = COUNTERFACTUAL_SUPPORTED
L3 = COUNTERFACTUAL_SUPPORTED_WITH_LOW_REGRESSION
L4 = READY_FOR_MINIMAL_DESIGN

RESULT: L1 = PLAUSIBLE_BUT_UNSAFE

  Local isolation (DCE-06) proves the table CAN pass when isolated → PLAUSIBLE
  But no geometry-only method can safely find table boundaries → UNSAFE
  False positives on prose pages (AMB-008, AMB-042) → UNSAFE
  No geometric signal distinguishes prose from table → UNSAFE

  → Does NOT proceed to L2/L3/L4
  → Route CLOSED
```

---

## 19. Mechanism Comparison

```
Mechanism 1 (Page-Global Contamination):
  Locality counterfactual: FAILED
    L1-correct: no local bands created (same as actual)
    L1-modified: recovers 1/3 but creates 2 FP (invalid + unsafe)
    L2: no recovery, creates regressions
  → Locality cannot safely solve Mechanism 1

Mechanism 2 (Inherent Low Text Ratio):
  Locality counterfactual: NOT APPLICABLE
    AMB-462: band already properly isolated, text_ratio=0.163 inherent
    Locality doesn't help (can't fix text_ratio by changing band scope)
  → Locality cannot solve Mechanism 2 (by design — different mechanism)

OVERALL:
  Mechanism 1: Locality route CLOSED (unsafe)
  Mechanism 2: Locality route NOT APPLICABLE (different mechanism)
  Both mechanisms remain UNRESOLVED by counterfactual locality.
```

---

## 20. Final Questions Answered

### Q1: Locality Counterfactual 能否恢复 AMB-135, AMB-262, AMB-313?

**NO (with correct TLD anchors).** L1-correct creates the same page-global band as actual TLD (no wide_text breakers → band extends to page boundary). 0/3 recovered.

**PARTIALLY (with modified anchors, but INVALID).** L1-modified recovers AMB-262 (1/3) but changes TLD's anchor definition (not just band scope). AMB-135 and AMB-313 still fail.

### Q2: 能否保持已有 TLD 正确案例?

**YES (L1-correct).** All 3 success cases preserved (align > 0.75, text_ratio > 0.45). TP_PRESERVED = 3/3.

### Q3: 是否制造新的 False Positive?

**YES (L1-modified and L2).** L1-modified creates FP on AMB-008 (prose) and AMB-042 (prose). L2 creates FP on AMB-008 and AMB-042, plus splits success tables.

**NO (L1-correct).** But L1-correct doesn't recover any failures either.

### Q4: AMB-462 是否仍然失败?

**YES.** AMB-462 fails at text_ratio=0.163 (Mechanism 2, inherent). Locality doesn't help — band is already properly isolated. The failure is text_ratio threshold, not contamination.

### Q5: Locality 是真正的最小修复方向还是看起来合理但不安全的假设?

**PLAUSIBLE_BUT_UNSAFE.** Local isolation (DCE-06) proves the table CAN pass TLD checks when isolated — this makes it PLAUSIBLE. But no geometry-only method can safely derive the local table boundaries without creating false positives on prose — this makes it UNSAFE.

The fundamental reason: **Locality ≠ Table.** Prose with citations has the same geometric properties as table data. Without semantic content understanding, there's no geometric way to distinguish them.

### Q6: 下一步如果继续，最小研究对象是什么?

**UNKNOWN.** All identified routes are closed:
- Band Locality: CLOSED (unsafe, creates false positives)
- Column Stability: THRESHOLD_TUNING (forbidden — would need to change 0.75 threshold)
- Text Ratio: THRESHOLD_TUNING (forbidden — would need to change 0.45 threshold or _is_text_cell logic)
- Other mechanism: NONE_IDENTIFIED

No safe minimal fix direction has been identified within the constraints (READ-ONLY, no threshold tuning, no new module, no LLM).

---

## 21. Root Cause of Locality Failure

```
The locality counterfactual fails because:

1. BAND SCOPE ≠ TABLE SCOPE
   Changing the band starting point (candidate-centered) doesn't change the band scope.
   The band still extends to page boundaries because the absorption logic is the same.
   (multicol = anchor, short_single = absorb, wide_text = break)

2. NO GEOMETRIC TABLE BOUNDARY SIGNAL
   Table boundaries cannot be derived from P1/P2 geometry alone.
   - y-spacing regularity: works on some tables, fails on others, creates FP on prose
   - column-pattern consistency: prose and table share x-positions
   - fragment count consistency: no clear distinction
   - text ratio: already in TLD (can't change threshold)

3. PROSE ≈ TABLE (geometrically)
   Prose with citations has:
   - Multiple fragments on same y (same as table rows)
   - x-gaps ≥ 12pt (citation formatting = column gaps)
   - Consistent x-positions across rows (prose formatting = column alignment)
   - Text content (text words = text cells)
   These are the EXACT signals TLD uses to identify tables.
   Without semantic understanding, prose with citations IS indistinguishable
   from a table.

4. TLD's FORMULA REJECTION IS LOAD-BEARING
   TLD uses len>=2 (not is_multicol) for anchors, deliberately including
   formula fragments in column center computation.
   Formula fragments destabilize column centers → alignment drops → non-table rejected.
   Changing to is_multicol (L1-modified) removes this protection → FP on prose.
```

---

## 22. Limitations

1. **12-case sample**: Only 12 cases tested (4 failure + 3 success + 3 negative + 2 partial). Results may not generalize to all 45 IS-11 cases or P7 cases.

2. **3 locality bases only**: Only L1 (candidate), L2 (geometry), L3 (existing TLD) tested. Other locality bases (e.g., semantic content, font analysis) are not tested because they require new observations (forbidden).

3. **L2 break threshold (50%)**: The column-pattern break threshold was set at 50%. A different threshold might produce different results, but threshold tuning is forbidden.

4. **Y-spacing CV threshold (0.3)**: The y-spacing regularity threshold was set at 0.3. A different threshold might distinguish better, but threshold tuning is forbidden.

5. **No P7 cross-validation**: P7 has no TLD, so counterfactual results cannot be cross-validated on P7.

6. **Negative controls may not cover all prose types**: Only resnet and med_001 prose pages tested. Other document types (e.g., two-column papers, books) may have different prose patterns.

7. **AMB-042 ambiguous**: AMB-042 (resnet page 7) has both prose AND a small table. It was classified as NEGATIVE because TLD returns 0 tables, but the page does contain table-like content. This makes the false positive classification debatable.

---

## 23. Governance Gate

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

FROZEN_BASELINE                     = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d)
FROZEN_EXPERIMENT                   = INTACT

IMPLEMENTATION_AUTHORIZED           = FALSE
EXPERIMENT_AUTHORIZED               = FALSE
FORMAL_EXPERIMENT                   = NOT_STARTED

STOP                                = TRUE
```

`STOP = TRUE`。
