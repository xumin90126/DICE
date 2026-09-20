# DCE-06 TLD Failure Mechanism Audit

**Date**: 2026-09-14
**Mode**: READ-ONLY / FORENSIC FAILURE ANALYSIS / NO MODIFICATION / FROZEN INTACT / STOP
**Predecessor**: DCE-05 Table Column Identity Expressibility Audit

---

## 1. Executive Summary

```
FINAL_STATUS = TLD_FAILURE_MECHANISM_LOCATED

TWO DISTINCT FAILURE MECHANISMS IDENTIFIED:

  Mechanism 1 (Page-Global Contamination):
    AMB-135 (PRIMARY), AMB-262 (ONLY), AMB-313 (ONLY)
    
    Root Cause Chain:
      1. PDF page has small table (11-15% of page) + other content
      2. PDF extraction splits prose into multiple spans (citations, math symbols)
      3. TLD sees multi-fragment prose rows as multicol (≥2 fragments with gaps ≥12pt)
      4. TLD band breaker (is_wide_text) only triggers on SINGLE-fragment wide rows
      5. Multi-fragment prose rows DON'T break the band
      6. Band extends from table to page bottom (page-global, no locality constraint)
      7. Non-table multicol rows pollute column center clustering (_cluster_xs)
      8. Column centers become unstable (mixed table + formula + prose positions)
      9. Average alignment drops below 0.75 (AMB-135: 0.27, AMB-262: 0.23, AMB-313: 0.54)
     10. Table rejected at Stage E (column stability check)
    
    PROOF (Local Isolation Test):
      AMB-135 LOCAL: align=0.991 (PASS), text_ratio=0.195 (FAIL)
      AMB-262 LOCAL: align=1.000 (PASS), text_ratio=0.822 (PASS) ← WOULD PASS
      AMB-313 LOCAL: align=0.958 (PASS), text_ratio=0.516 (PASS) ← WOULD PASS
    
    "Greedy Band" hypothesis: PROVEN (not hypothesis)
      Failure: table covers 11-15% of page → 17-28 contaminating multicol rows
      Success: table covers 95-97% of page → 0 contaminating multicol rows

  Mechanism 2 (Inherent Low Text Ratio):
    AMB-135 (SECONDARY), AMB-462 (ONLY)
    
    Root Cause:
      Target table is numeric/symbolic-heavy.
      _is_text_cell rejects short numeric strings and math symbols.
      AMB-135: 74/118 cells are math fragments (Stage='1', Resolution='224 × 224', #Channels='32')
      AMB-462: 67/80 cells are math fragments (ARCe='54.7', ARCc='23.0', HS='37.0')
      → text_ratio < 0.45 even in perfect isolation
      → Table rejected at Stage F (text ratio check)
    
    This is NOT contamination — the table itself is inherently numeric.

AMB-135 = Mechanism 1 (PRIMARY) + Mechanism 2 (SECONDARY)
  → FIRST_FAILURE_STAGE = Stage E (column stability)
  → Even if Stage E passed, Stage F would fail

AMB-262 = Mechanism 1 (ONLY)
  → FIRST_FAILURE_STAGE = Stage E (column stability)
  → If Stage E passed, Stage F would pass (text_ratio=0.518 > 0.45)

AMB-462 = Mechanism 2 (ONLY)
  → FIRST_FAILURE_STAGE = Stage F (text ratio)
  → Band formation CORRECT (2 properly separated bands)
  → Column stability PERFECT (align=1.0)
  → But text_ratio=0.163 < 0.45

SUCCESS CASES (AMB-032, AMB-074, AMB-346):
  → Table DOMINATES page (95-97% y-span coverage)
  → Global band = table (no contamination)
  → Column stability HIGH (0.75-1.0)
  → Text ratio PASSES (0.60-0.87)

FAILURE TYPE:
  AMB-135: T9 (Mixed: T8 Page-global contamination + T7 Text ratio threshold)
  AMB-262: T8 (Page-global contamination)
  AMB-313: T8 (Page-global contamination)
  AMB-462: T7 (Text ratio threshold)

TLD vs Consumer:
  Case B (TLD has capability but Detection fails) — CONFIRMED
  TLD data model CAN express different_column (proven on 13/45 success cases)
  Failure is in Detection Algorithm, NOT Representation, NOT Consumer

P2 SUFFICIENCY:
  P2 provides sufficient底层 evidence (same_y_band, h_gap, fragment positions)
  P2 CANNOT interpret as table columns (L3), but provides all L1/L2 geometry

TLD_CHANGE_NECESSITY = POSSIBLY_NEEDED
  - Band formation locality constraint (Mechanism 1)
  - Text ratio threshold for numeric tables (Mechanism 2)
  - BUT: TLD is FROZEN, NOT authorized this round

POSSIBLE_EXTERNAL_ROUTE = YES
  P2 geometry (same_y_band + h_gap + fragment count) could support locality pre-filter
  But: would be a new module, NOT authorized

LLM_NEEDED = NO
NEW_OBSERVATION_NEEDED = NO
NEW_MODULE_NEEDED = NO
NEW_ENGINE_NEEDED = NO

TRUE_REUSABLE_SIGNAL_FOUND = NO
  "greedy band" and "column stability < 0.75" are observed failure mechanisms,
  NOT generalizable learning signals.

STOP = TRUE
```

---

## 2. Research Questions Answered

### Q1: AMB-135 为什么没有被 TLD 识别成 Table?

**DUAL failure:**

1. **PRIMARY — Page-Global Contamination (Stage E)**:
   - Table covers only 15% of page (y=111-210, 99pt / 659pt page span)
   - 14 table multicol rows + 17 contaminating multicol rows = 31 total anchors
   - Global column centers: 5 (mixed formula + table positions)
   - Global alignment: 0.268 < 0.75 → **FAIL at Stage E**
   - LOCAL isolation: alignment = 0.991 (would PASS)

2. **SECONDARY — Inherent Low Text Ratio (Stage F)**:
   - Even in local isolation, text_ratio = 0.195 < 0.45
   - 74/118 cells are math fragments ('1', '224', '×', '32', 'α', 'φ')
   - Table is architecture specification (Stage/Operator/Resolution/#Channels/#Layers)
   - Numeric/symbolic columns dominate → _is_text_cell rejects most cells
   - **FAIL at Stage F** (even if Stage E passed)

**FIRST_FAILURE_STAGE = Stage E (column stability)**

### Q2: AMB-262 为什么没有被 TLD 识别成 Table?

**SINGLE failure:**

1. **Page-Global Contamination (Stage E)**:
   - Table covers only 11% of page (y=107-177, 70pt / 659pt page span)
   - 9 table multicol rows + 28 contaminating multicol rows = 37 total anchors
   - Global column centers: 4 (too few for 13-14 fragment rows)
   - Global alignment: 0.226 < 0.75 → **FAIL at Stage E**
   - LOCAL isolation: alignment = 1.000, text_ratio = 0.822 → **WOULD PASS ALL CHECKS**

**FIRST_FAILURE_STAGE = Stage E (column stability)**

### Q3: 这两个 Failure 是否属于同一种机制?

**PARTIALLY SAME:**

- **SAME PRIMARY mechanism**: Page-global contamination → column stability failure
  - Both: small table on mixed-content page → global band includes non-table content
  - Both: LOCAL isolation passes alignment check
  - Both: "greedy band" proven (no wide_text breakers below table)

- **DIFFERENT secondary mechanism**:
  - AMB-135: ADDITIONAL inherent text_ratio failure (0.195 < 0.45 even in isolation)
  - AMB-262: NO secondary failure (text_ratio = 0.518 > 0.45 globally, 0.822 locally)

**AMB-135 = T9 (Mixed: T8 + T7)**
**AMB-262 = T8 (Page-global contamination only)**

### Q4: Failure 发生在 TLD 的哪一个具体阶段?

```
Stage A (Input/line extraction): PASS (402 vlines extracted)
Stage B (Row grouping): PASS (82 rows, 31 multicol identified)
Stage C (Band formation): PASS-BUT-DEFECTIVE
  → 1 band formed (y=69.5-706.7, 81 members, 56 anchors)
  → Band is page-global (no locality constraint)
  → This is WHERE contamination enters, but not WHERE it's detected
Stage D (Column grouping): PASS-BUT-CONTAMINATED
  → 5 column centers computed from 56 contaminated anchors
  → Centers are unstable (mixed table + formula positions)
Stage E (Column stability): *** FIRST FAILURE ***
  → avg_alignment = 0.268 < 0.75 → REJECT
Stage F (Text ratio): WOULD ALSO FAIL (0.382 < 0.45)
  → But never reached because Stage E already rejected

For AMB-262:
Stage E: avg_alignment = 0.226 < 0.75 → REJECT (FIRST FAILURE)
Stage F: text_ratio = 0.518 > 0.45 → WOULD PASS (but never reached)
```

### Q5: 失败案例与成功案例之间，最小可解释差异是什么?

**TABLE-TO-PAGE RATIO:**

| Case | Table y-span | Page y-span | Coverage | Contaminating MC rows | Result |
|---|---|---|---|---|---|
| AMB-032 (SUCCESS) | 629pt | 659pt | 95% | 0 | align=0.986, PASS |
| AMB-074 (SUCCESS) | 631pt | 661pt | 95% | 0 | align=0.750, PASS |
| AMB-346 (SUCCESS) | 640pt | 660pt | 97% | 0 | align=0.995, PASS |
| AMB-135 (FAIL) | 99pt | 659pt | 15% | 17 | align=0.268, FAIL |
| AMB-262 (FAIL) | 70pt | 659pt | 11% | 28 | align=0.226, FAIL |

**最小差异**: Success cases have tables that DOMINATE the page (95-97%). Failure cases have tables that are SMALL fractions (11-15%). When the table dominates, the global band = table, so no contamination. When the table is small, the global band includes non-table multicol rows, causing contamination.

### Q6: "greedy band" 是否已经被证明?

**PROVEN (not hypothesis).**

Evidence:
1. **Failure cases**: Table covers 11-15% of page → 17-28 contaminating multicol rows → alignment 0.23-0.27
2. **Success cases**: Table covers 95-97% of page → 0 contaminating multicol rows → alignment 0.75-1.0
3. **Local isolation test**: Removing contamination raises alignment from 0.23-0.27 to 0.96-1.00

The "greedy band" is the MECHANISM (how contamination enters), but the ROOT CAUSE is:
- TLD band formation has NO locality constraint (only breaks on is_wide_text)
- PDF extraction splits prose into multiple fragments (making prose appear as multicol)
- These two factors combine: multi-fragment prose doesn't break the band → band extends to page bottom

### Q7: 这是 TLD Detection 还是 TLD Representation 还是 Consumer Integration?

**TLD Detection (Case B).**

- TLD data model CAN express different_column (proven on 13/45 success cases)
- TLD Detection Algorithm fails on specific pages (column stability check rejects)
- IS-11 Consumer correctly consumes different_cell when TLD provides it
- NOT Representation (TLD model can express)
- NOT Consumer Integration (IS-11 already integrated)

### Q8: P2 是否已经提供足够底层 Evidence?

**YES.**

P2 provides:
- same_y_band (L1): A/B on same horizontal band
- h_gap (L1): horizontal distance between A/B
- fragment positions (L1): x0, y0, x1, y1 for each span
- fragment count on same y (L2): derivable from P2

P2 CANNOT interpret as "table columns" (L3), but provides ALL L1/L2 geometry needed.
The issue is TLD's organization of this geometry, not P2's provision of it.

### Q9: 是否真的需要 New Observation / LLM / New Module?

**NO to all.**

- NEW_OBSERVATION_NEEDED = NO (P2 provides sufficient geometry)
- LLM_NEEDED = NO (failure is structural/algorithmic, not semantic)
- NEW_MODULE_NEEDED = NO (TLD already has the capability, just fails on detection)
- NEW_ENGINE_NEEDED = NO (no new processing pipeline needed)

### Q10: 下一步如果继续，应该研究 TLD 内部哪一个最小问题?

**TLD Band Formation Locality (Mechanism 1).**

The smallest TLD internal issue is: band formation has no locality constraint. It only breaks on `is_wide_text` (single-fragment wide rows). Multi-fragment prose rows (which PDF extraction creates from citations/math) don't break the band.

A potential direction (NOT authorized this round): add a locality constraint to band formation — e.g., break band when consecutive multicol rows have significantly different column x-positions from the band's established column centers.

Secondary issue: text_ratio threshold (Mechanism 2) rejects numeric-heavy tables. A potential direction: adjust text_ratio computation to exclude known numeric columns, or use a different metric. But this is threshold tuning, which is FORBIDDEN.

---

## 3. TLD Pipeline Stage Definitions

From Frozen TLD source code (`chunker/table_line_detector.py`, 270 lines):

```
Stage A: Input / line extraction
  → fitz.get_text('dict') → VLine objects
  → NOT in TLD (TLD receives VLine list from caller)

Stage B: Row grouping (group_lines_into_rows, line 52-79)
  → Sort by (y0, x0)
  → Group by y_tol=3.0
  → Output: List[List[VLine]] (rows)

Stage C: Band formation (lines 154-172)
  → Scan rows sequentially
  → is_multicol(r): ≥2 fragments with ≥1 gap ≥ col_gap(12.0) → ANCHOR
  → is_wide_text(r): 1 fragment, width > 0.40*page_width, text > 40 chars → BREAKER
  → is_short_single(r): 1 fragment, width ≤ 0.40*page_width, text ≤ 40 chars → ABSORB
  → else (OTHER): ABSORB if band started
  → Band requires ≥3 anchors and ≥3 members
  → Output: List[List[int]] (band row indices)

Stage D: Column grouping (_cluster_xs, line 27-42)
  → Collect x0 from ALL anchor rows in band
  → Cluster with tol=10.0
  → Output: List[float] (column centers)
  → Reject if < 2 centers

Stage E: Column stability (lines 187-197)
  → For each anchor row: count fragments within 16pt of nearest column center
  → alignment = hit_count / fragment_count
  → avg_alignment = mean of all anchor row alignments
  → Reject if avg_alignment < 0.75

Stage F: Text ratio (lines 199-204)
  → ALL cells in band (not just anchor rows)
  → text_ratio = _is_text_cell(t) count / total cell count
  → _is_text_cell: len ≥ 3 AND NOT _is_math_fragment
  → _is_math_fragment: math chars, single-char symbols, short numeric strings
  → Reject if text_ratio < 0.45

Stage G: Table acceptance (lines 207-264)
  → Header absorption, grid construction, bbox computation
  → Output: table dict
```

---

## 4. Full Pipeline Trace

### AMB-135 (FAILURE — Mechanism 1 + Mechanism 2)

```
Stage A: 402 vlines
Stage B: 82 rows, 31 multicol, 1 wide_text, 0 short_single
  Target row: idx=14, type=MULTICOL
Stage C: 1 band
  Band 0: y=69.5-706.7 (h=637.2), 81 members, 56 anchors, target=True
  member_types: {MULTICOL: 31, OTHER: 50}
  → NO wide_text below target → band extends to page bottom
Stage D: 5 column centers [55.3, 109.5, 258.7, 284.0, 336.1, 472.8]
  → Contaminated: mixed table + formula + prose positions
Stage E: avg_alignment = 0.268 < 0.75 → *** FAIL ***
Stage F: text_ratio = 0.382 (153/401) < 0.45 → WOULD ALSO FAIL
Final: 0 tables

LOCAL ISOLATION (y=111-210):
  14 anchor rows, 14 column centers, align=0.991 (PASS)
  text_ratio = 0.195 (21/107) < 0.45 → FAIL (inherent)
  → Mechanism 1 (contamination) + Mechanism 2 (inherent text ratio)
```

### AMB-262 (FAILURE — Mechanism 1 only)

```
Stage A: 414 vlines
Stage B: 82 rows, 37 multicol, 2 wide_text, 6 short_single
  Target row: idx=7, type=MULTICOL
Stage C: 1 band
  Band 0: y=107.8-706.2 (h=598.4), 79 members, 54 anchors, target=True
  member_types: {MULTICOL: 37, OTHER: 36, SHORT_SINGLE: 6}
  → 2 wide_text above target, 0 below → band extends to page bottom
Stage D: 4 column centers [64.2, 170.9, 353.1, 488.2]
  → Contaminated: too few centers for 13-14 fragment rows
Stage E: avg_alignment = 0.226 < 0.75 → *** FAIL ***
Stage F: text_ratio = 0.518 (212/409) > 0.45 → WOULD PASS
Final: 0 tables

LOCAL ISOLATION (y=107-177):
  9 anchor rows, 14 column centers, align=1.000 (PASS)
  text_ratio = 0.822 (88/107) > 0.45 → PASS
  → Mechanism 1 ONLY (pure contamination)
```

### AMB-313 (MISS — Mechanism 1 only)

```
Stage A: 249 vlines
Stage B: 62 rows, 31 multicol, 1 wide_text, 10 short_single
  Target row: idx=9, type=MULTICOL
Stage C: 1 band
  Band 0: y=70.9-707.5 (h=636.6), 61 members, 41 anchors, target=True
  member_types: {MULTICOL: 31, OTHER: 20, SHORT_SINGLE: 10}
Stage D: 9 column centers
Stage E: avg_alignment = 0.538 < 0.75 → *** FAIL ***
Stage F: text_ratio = 0.585 > 0.45 → WOULD PASS
Final: 0 tables

LOCAL ISOLATION (y=260-340):
  9 anchor rows, 9 column centers, align=0.958 (PASS)
  text_ratio = 0.516 (33/64) > 0.45 → PASS
  → Mechanism 1 ONLY (pure contamination)
```

### AMB-462 (PARTIAL — Mechanism 2 only)

```
Stage A: 244 vlines
Stage B: 47 rows, 17 multicol, 5 wide_text, 2 short_single
  Target row: idx=9, type=MULTICOL
Stage C: 2 bands (PROPERLY SEPARATED by wide_text)
  Band 0: y=75.7-167.7 (h=92.0), 8 members, 8 anchors, target=False → ACCEPTED
  Band 1: y=216.1-308.1 (h=92.0), 8 members, 8 anchors, target=True
Stage D (Band 1): 10 column centers
Stage E (Band 1): avg_alignment = 1.000 > 0.75 → PASS
Stage F (Band 1): text_ratio = 0.163 (13/80) < 0.45 → *** FAIL ***
  → Inherent: 67/80 cells are numeric (54.7, 23.0, 37.0, 60.0, etc.)
  → _is_text_cell rejects short numeric strings
Final: 1 table (Band 0 only — wrong table)

→ NO contamination. Band formation CORRECT.
→ Pure Mechanism 2 (inherent low text ratio for numeric table)
```

### AMB-032 (SUCCESS — Control)

```
Stage A: 204 vlines
Stage B: 86 rows, 38 multicol, 0 wide_text, 6 short_single
Stage C: 1 band (y=74.8-733.3, 86 members, 47 anchors)
  → Table DOMINATES page (95% coverage)
  → 0 contaminating multicol rows
Stage D: 20 column centers
Stage E: avg_alignment = 0.986 > 0.75 → PASS
Stage F: text_ratio = 0.760 > 0.45 → PASS
Final: 1 table (CORRECT)
```

### AMB-074 (SUCCESS — Control)

```
Stage A: 206 vlines
Stage B: 82 rows, 41 multicol, 0 wide_text, 11 short_single
Stage C: 1 band (y=72.6-733.3, 82 members, 48 anchors)
  → Table DOMINATES page (95% coverage)
Stage D: 8 column centers
Stage E: avg_alignment = 0.750 > 0.75 → PASS (barely)
Stage F: text_ratio = 0.694 > 0.45 → PASS
Final: 1 table (CORRECT)
```

### AMB-346 (SUCCESS — Control)

```
Stage A: 176 vlines
Stage B: 67 rows, 24 multicol, 1 wide_text, 6 short_single
Stage C: 1 band (y=67.8-707.5, 66 members, 36 anchors)
  → Table DOMINATES page (97% coverage)
Stage D: 18 column centers
Stage E: avg_alignment = 0.995 > 0.75 → PASS
Stage F: text_ratio = 0.909 > 0.45 → PASS
Final: 1 table (CORRECT)
```

---

## 5. Band Formation Analysis

### Why 56/54 anchors in one band?

**TLD band formation logic (source lines 154-172):**

```python
for i, r in enumerate(rows):
    if is_multicol(r):        # ≥2 frags, ≥1 gap ≥12pt → ANCHOR
        cur.append((i, True))
        anchor_count += 1
    elif is_wide_text(r):     # 1 frag, wide, long → BREAKER
        if anchor_count >= 3 and len(cur) >= 3:
            bands.append(cur)
        cur = []
        anchor_count = 0
    else:                     # short_single OR other → ABSORB
        if cur:
            cur.append((i, False))
```

**Key finding**: The ONLY band breaker is `is_wide_text` (single-fragment, width > 0.40*page_width, text > 40 chars).

**Why bands are page-global on failure pages:**

1. PDF text extraction splits prose lines into multiple spans:
   - "In fact, a few prior" + "Zoph et al." + "," + "2018" + ";" → 5 fragments
   - These fragments have x-gaps ≥ 12pt (citation formatting)
   - TLD sees this as `is_multicol = True` (ANCHOR, not BREAKER)

2. Formula lines are also multicol:
   - "depth:" + "d" + "=" + "α" + "φ" → 5 fragments with gaps
   - TLD sees this as `is_multicol = True` (ANCHOR, not BREAKER)

3. No `is_wide_text` rows between table and page bottom:
   - AMB-135: 1 wide_text (title at y=47.2), 0 below table → band y=69.5-706.7
   - AMB-262: 2 wide_text (title + abstract at y=47.2, 87.4), 0 below table → band y=107.8-706.2

**Why bands are local on success pages:**

Success pages (AMB-032, AMB-074, AMB-346) have tables that span 95-97% of the page. The entire page IS the table. Even though the band is page-global, it equals the table — no contamination.

### Band Member Classification

| Case | Band Members | Anchors | Non-Anchor | Table MC | Contaminating MC | Contamination Ratio |
|---|---|---|---|---|---|---|
| AMB-135 | 81 | 56 | 25 | 14 | 17 | 55% of anchors |
| AMB-262 | 79 | 54 | 25 | 9 | 28 | 76% of anchors |
| AMB-313 | 61 | 41 | 20 | 9 | 22 | 54% of anchors |
| AMB-462 (Band 1) | 8 | 8 | 0 | 8 | 0 | 0% (properly isolated) |
| AMB-032 | 86 | 47 | 39 | 38 | 0 | 0% |
| AMB-074 | 82 | 48 | 34 | 41 | 0 | 0% |
| AMB-346 | 66 | 36 | 30 | 24 | 0 | 0% |

---

## 6. Page-Global Contamination Test

```
GLOBAL_CONTAMINATION_TEST:

  AMB-135:
    TARGET_TABLE_LOCALITY: y=111-210 (15% of page)
    PAGE_GLOBAL_BAND: y=69.5-706.7 (97% of page)
    GLOBAL_CONTAMINATION = TRUE
    Cause: No wide_text breakers below table. Multi-fragment prose absorbed as anchors.

  AMB-262:
    TARGET_TABLE_LOCALITY: y=107-177 (11% of page)
    PAGE_GLOBAL_BAND: y=107.8-706.2 (91% of page)
    GLOBAL_CONTAMINATION = TRUE
    Cause: No wide_text breakers below table. Multi-fragment prose absorbed as anchors.

  AMB-313:
    TARGET_TABLE_LOCALITY: y=260-340 (12% of page)
    PAGE_GLOBAL_BAND: y=70.9-707.5 (97% of page)
    GLOBAL_CONTAMINATION = TRUE
    Cause: Same as above.

  AMB-462:
    TARGET_TABLE_LOCALITY: y=216-308 (Band 1, properly isolated)
    PAGE_GLOBAL_BAND: N/A (2 separate bands formed correctly)
    GLOBAL_CONTAMINATION = FALSE
    Cause: wide_text breaker at y=188.2 (Table 2 caption) separates bands.

  AMB-032 (SUCCESS):
    TARGET_TABLE_LOCALITY: y=74.8-733.3 (95% of page)
    PAGE_GLOBAL_BAND: y=74.8-733.3 (same)
    GLOBAL_CONTAMINATION = FALSE (band = table)

  AMB-074 (SUCCESS):
    TARGET_TABLE_LOCALITY: y=72.6-733.3 (95% of page)
    PAGE_GLOBAL_BAND: y=72.6-733.3 (same)
    GLOBAL_CONTAMINATION = FALSE (band = table)

  AMB-346 (SUCCESS):
    TARGET_TABLE_LOCALITY: y=67.8-707.5 (97% of page)
    PAGE_GLOBAL_BAND: y=67.8-707.5 (same)
    GLOBAL_CONTAMINATION = FALSE (band = table)
```

**Contamination source**: TLD band formation itself (page-global, only breaks on `is_wide_text`). NOT line grouping (lines are correctly grouped by y). The issue is that `is_wide_text` is the ONLY breaker, and multi-fragment prose doesn't trigger it.

---

## 7. Column Stability Failure Decomposition

### AMB-135 (align=0.268)

```
GLOBAL column centers (5): [55.3, 109.5, 258.7, 284.0, 336.1, 472.8]
  → These are MIXED positions from table + formulas + prose

Target table columns (14, from local isolation):
  [55.3, 109.5, 126.9, 166.9, 201.8, 277.8, 288.2, 319.8, 339.7, 354.1, 373.0, 439.7, 480.8, 520.2]

Contaminating columns (from non-table multicol rows):
  Formula rows: x positions at ~152, ~160, ~170, ~180 (depth/width/resolution formulas)
  Prose rows: x positions at ~55, ~127, ~310, ~346, ~383, ~435, ~459, ~545, ~569, ~605
  → These DON'T align to table columns

Missing members (table columns not in global centers):
  126.9, 166.9, 201.8, 277.8, 288.2, 319.8, 339.7, 354.1, 373.0, 439.7, 480.8, 520.2
  → 12 of 14 table columns MISSING from global centers

Extra members (non-table positions in global centers):
  109.5 (formula 'd' position), 258.7 (prose position), 472.8 (prose position)

Column center variance:
  Table columns span x=55-520 (14 distinct positions)
  Global centers span x=55-473 (5 positions, too few)
  → Global clustering MERGED table columns with formula/prose positions

WHY alignment is low:
  1. Global centers have only 5 positions (table has 14)
  2. Table fragments at x=127, 167, 202, 278, 288, 320, 340, 354, 373, 440, 481, 520
     → NONE within 16pt of global centers [55, 110, 259, 284, 336, 473]
     → Only x=55 (within 16pt of 55.3) and x=354 (within 16pt of 336? No, 354-336=18 > 16)
     → Most table fragments DON'T align → low hit ratio → low alignment
```

### AMB-262 (align=0.226)

```
GLOBAL column centers (4): [64.2, 170.9, 353.1, 488.2]
  → Too few for 13-14 fragment rows

Target table columns (14, from local isolation):
  [61.2, 118.1, 159.9, 188.1, 214.3, 265.0, 293.8, 339.3, 365.4, 395.2, 421.0, 472.0, 501.0, 515.8]

Contaminating columns: mixed formula/prose positions across page

Missing members: 10 of 14 table columns not in global centers
Extra members: formula/prose positions merged into 4 global centers

WHY alignment is low:
  1. Global centers have only 4 positions (table has 14)
  2. _cluster_xs with tol=10.0 MERGES nearby positions
  3. Contaminating rows have DIFFERENT x patterns → centers shift
  4. Table fragments don't align to shifted centers → low hit ratio
```

---

## 8. Text Ratio Failure Decomposition

### AMB-135 (text_ratio=0.382 globally, 0.195 locally)

```
TARGET TABLE (y=111-210):
  cells: 118, text_cells: 23, ratio: 0.195 → FAIL (even in isolation)
  
  Math fragments (74/118): 
    '1', '2', '3', '224', '×', '224', '32', '112', '×', '112', '16', 
    'α', 'φ', 'β', 'γ', ',', 'i', 'F', 'ˆ', 'H', 'W', 'C', 'L'
  
  Text cells (23/118):
    'compound scaling method', 'Stage', 'Operator', 'Resolution', 
    '#Channels', '#Layers', 'Conv3x3', 'MBConv1, k3x3', 'MBConv6, k3x3', etc.

  → Table is architecture specification: Stage/Operator/Resolution/#Channels/#Layers
  → 4 of 5 columns are numeric/symbolic → inherently low text ratio
  → NOT contamination (fails even in perfect isolation)

CONTAMINATION (rest of band):
  cells: 283, text_cells: 130, ratio: 0.459 → barely passes

COMBINED (what TLD computes):
  cells: 401, text_cells: 153, ratio: 0.382 → FAIL
  → Contamination makes it worse, but target alone already fails

CONCLUSION: 
  A. Target table text ratio low: YES (0.195)
  B. Contamination contributes: YES (drags 0.195 to 0.382, but both < 0.45)
  C. Both: YES
  → Answer: C (both contribute, but target is primary cause)
```

### AMB-262 (text_ratio=0.518 globally, 0.822 locally)

```
TARGET TABLE (y=107-177):
  cells: 107, text_cells: 88, ratio: 0.822 → PASS

CONTAMINATION:
  cells: 302, text_cells: 124, ratio: 0.411 → would fail alone

COMBINED: 0.518 → PASS (contamination dilutes but table's high ratio saves it)

CONCLUSION:
  Target table text ratio: PASS (0.822)
  → Text ratio failure is NOT an issue for AMB-262
  → Only column stability (Mechanism 1) causes failure
```

### AMB-462 (text_ratio=0.163, properly isolated band)

```
TARGET TABLE (Band 1, y=216-308):
  cells: 80, text_cells: 13, ratio: 0.163 → FAIL
  
  Numeric cells (67/80):
    '54.7', '23.0', '37.0', '60.0', '20.2', '68.9', '54.8', '45.5',
    '51.8', '21.4', '35.1', '58.2', '20.0', '68.1', '55.2', '44.3', etc.
  
  Text cells (13/80):
    'Models', 'Size', 'ARCe', 'ARCc', 'WGe', 'Avg.', 
    'LLaMA LLM', 'BitNet b1.58', '700M', etc.

  → Table is benchmark results: 8 numeric score columns + 2 text columns
  → _is_text_cell rejects '54.7' (len=4, math-heavy: 3 digits + 1 dot)
  → _is_text_cell rejects 'HS', 'BQ', 'OQ', 'PQ' (len=2, too short)
  → Inherent: 80% of cells are numeric → text_ratio always < 0.45

CONTAMINATION: NONE (band properly isolated)
  → Pure Mechanism 2 (inherent low text ratio)
```

---

## 9. Success vs Failure Comparison Matrix

| Mechanism | AMB-135 (FAIL) | AMB-262 (FAIL) | AMB-313 (FAIL) | AMB-462 (FAIL) | AMB-032 (SUCCESS) | AMB-074 (SUCCESS) | AMB-346 (SUCCESS) | Root Cause? |
|---|---|---|---|---|---|---|---|---|
| Input vlines | 402 | 414 | 249 | 244 | 204 | 206 | 176 | NO (sufficient) |
| Row count | 82 | 82 | 62 | 47 | 86 | 82 | 67 | NO |
| Multicol count | 31 | 37 | 31 | 17 | 38 | 41 | 24 | NO |
| Band count | 1 | 1 | 1 | 2 | 1 | 1 | 1 | NO |
| Band height | 637pt | 598pt | 637pt | 92pt | 659pt | 661pt | 640pt | SYMPTOM |
| Band locality | PAGE-GLOBAL | PAGE-GLOBAL | PAGE-GLOBAL | LOCAL (correct) | PAGE-GLOBAL | PAGE-GLOBAL | PAGE-GLOBAL | MECHANISM (for 135/262/313) |
| Table/page coverage | 15% | 11% | 12% | 14% | 95% | 95% | 97% | ROOT CAUSE (for 135/262/313) |
| Contaminating MC | 17 | 28 | 22 | 0 | 0 | 0 | 0 | ROOT CAUSE (for 135/262/313) |
| Column centers | 5 | 4 | 9 | 10 | 20 | 8 | 18 | SYMPTOM |
| Column stability | 0.268 | 0.226 | 0.538 | 1.000 | 0.986 | 0.750 | 0.995 | SYMPTOM |
| Text ratio | 0.382 | 0.518 | 0.585 | 0.163 | 0.760 | 0.694 | 0.909 | ROOT CAUSE (for 462, secondary for 135) |
| First fail stage | E | E | E | F | NONE | NONE | NONE | — |

### SYMPTOM vs MECHANISM vs ROOT_CAUSE

```
For AMB-135/AMB-262/AMB-313 (Mechanism 1):
  SYMPTOM: column_stability < 0.75, low column center count
  MECHANISM: page-global contamination (non-table multicol rows pollute column centers)
  ROOT_CAUSE: TLD band formation has no locality constraint + PDF splits prose into multicol

For AMB-135 (Mechanism 2, secondary):
  SYMPTOM: text_ratio < 0.45
  MECHANISM: _is_text_cell rejects numeric/symbolic cells
  ROOT_CAUSE: table is inherently numeric-heavy (architecture specification)

For AMB-462 (Mechanism 2, only):
  SYMPTOM: text_ratio = 0.163 < 0.45
  MECHANISM: _is_text_cell rejects numeric score values
  ROOT_CAUSE: table is inherently numeric-heavy (benchmark results)
```

---

## 10. Failure Mechanism Classification

| Case | Primary | Secondary | Evidence |
|---|---|---|---|
| AMB-135 | **T8** (Page-global contamination) | **T7** (Text ratio threshold) | align=0.268 (local 0.991), text_ratio=0.195 (local, inherent) |
| AMB-262 | **T8** (Page-global contamination) | — | align=0.226 (local 1.000), text_ratio=0.518 (pass) |
| AMB-313 | **T8** (Page-global contamination) | — | align=0.538 (local 0.958), text_ratio=0.585 (pass) |
| AMB-462 | **T7** (Text ratio threshold) | — | align=1.000 (pass), text_ratio=0.163 (inherent), band properly isolated |

```
T1 = Input Evidence unavailable          → NOT APPLICABLE (P1/P2 sufficient)
T2 = Line grouping failure               → NOT APPLICABLE (rows correctly grouped)
T3 = Band formation failure              → PARTIALLY (AMB-135/262/313: page-global band, but formation "works" per its own logic)
T4 = Column grouping failure             → NOT APPLICABLE (clustering works, but on contaminated input)
T5 = Stability calculation failure       → NOT APPLICABLE (calculation correct, but on contaminated centers)
T6 = Candidate filtering failure         → NOT APPLICABLE
T7 = Threshold / acceptance failure      → AMB-135 (secondary), AMB-462 (primary)
T8 = Page-global contamination           → AMB-135 (primary), AMB-262 (primary), AMB-313 (primary)
T9 = Mixed                               → AMB-135 (T8 + T7)
T10 = UNKNOWN                            → NOT APPLICABLE
```

---

## 11. TLD vs Consumer Analysis

```
Case A: TLD cannot express target structure
  → FALSE. TLD data model CAN express different_column (proven on 13/45 success cases)

Case B: TLD can express but Detection fails
  → TRUE. TLD detection algorithm fails at Stage E (column stability) or Stage F (text ratio)
  → Data model capability ≠ detection algorithm coverage

Case C: TLD produces correct structure but Consumer doesn't use
  → FALSE. IS-11 consumes different_cell when TLD provides it (13/45 TN, 0 FP)

VERDICT: Case B (TLD Detection Failure)
  → NOT Representation Failure (data model can express)
  → NOT Consumer Integration Failure (consumer integrated)
  → IS Detection/Coverage Failure (algorithm fails on specific page patterns)
```

---

## 12. P2 Sufficiency Analysis

```
P2 PROVIDES:
  ✓ same_y_band (L1): A/B y-coordinate proximity
  ✓ h_gap (L1): A/B horizontal distance
  ✓ fragment x0/y0/x1/y1 (L1): exact positions
  ✓ fragment count on same y (L2): derivable
  ✓ x-gap pattern (L2): derivable from fragment positions

P2 CANNOT EXPRESS:
  ✗ "table membership" (L3): requires structural interpretation
  ✗ "column membership" (L3): requires column clustering
  ✗ "different_column" (L3): requires table + column detection

P2 SUFFICIENCY:
  P2 provides ALL L1/L2 geometry needed for TLD.
  TLD's failure is in organizing this geometry (band formation + column stability),
  NOT in P2's provision of it.
  → P2 IS SUFFICIENT at L1/L2 level
  → L3 interpretation gap is TLD's responsibility, not P2's

VERDICT: P2_SUFFICIENT = YES (for L1/L2 evidence provision)
```

---

## 13. Change Necessity Analysis

```
TLD_CHANGE_NECESSITY = POSSIBLY_NEEDED

  Mechanism 1 (Page-Global Contamination):
    Issue: Band formation has no locality constraint
    Potential direction: Add locality break (e.g., when consecutive multicol rows 
                         have column x-positions significantly different from band's 
                         established centers)
    Impact: Would resolve AMB-262, AMB-313, and AMB-135's primary failure
    Risk: May break success cases where table spans entire page
    Status: POSSIBLY_NEEDED but NOT CLEARLY_NEEDED (only 2/45 IS-11 cases affected)
    
  Mechanism 2 (Inherent Low Text Ratio):
    Issue: _is_text_cell rejects numeric table cells
    Potential direction: Adjust text_ratio computation or threshold
    Impact: Would resolve AMB-462 and AMB-135's secondary failure
    Risk: May accept formula regions as tables (false positives)
    Status: POSSIBLY_NEEDED but involves threshold tuning (FORBIDDEN)
    
  OVERALL: POSSIBLY_NEEDED
    → NOT CLEARLY_NEEDED (only 2/45 IS-11 cases truly affected by Mechanism 1)
    → NOT NOT_JUSTIFIED (failure mechanism is real and located)
    → Even if CLEARLY_NEEDED: NOT AUTHORIZED this round (TLD is FROZEN)
```

---

## 14. Possible External Route

```
POSSIBLE_EXTERNAL_ROUTE = YES

  P2 geometry provides:
    - same_y_band (A/B on same horizontal band)
    - h_gap (horizontal gap between A/B)
    - fragment count on same y
    - x-gap pattern

  A consumer-side locality pre-filter could potentially:
    1. Identify local multicol clusters (same_y_band + ≥3 fragments + gaps)
    2. Feed only local cluster to TLD (avoiding page-global contamination)
    3. TLD would then see clean local input → pass column stability

  BUT:
    - This would be a NEW MODULE (NOT authorized)
    - This would be a CONSUMER-SIDE PRE-PROCESSING (not TLD modification)
    - Risk: may introduce new false positives
    - This audit does NOT design or implement this route
    - Only REPORTS its possibility
```

---

## 15. Anti-Overdesign Gate

```
NEW_OBSERVATION_NEEDED = NO
  P1/P2 already provide sufficient L1/L2 geometry.
  TLD already provides the observation (is_in_table, different_cell).
  Failure is in detection algorithm, not missing observation.

NEW_MODULE_NEEDED = NO
  TLD already has the capability (data model can express different_column).
  No new module needed — existing TLD just fails on specific patterns.

NEW_ENGINE_NEEDED = NO
  No new processing pipeline needed.
  TLD's existing pipeline is sufficient when it detects correctly.

LLM_NEEDED = NO
  Failure is structural/algorithmic (band formation locality, text ratio threshold).
  NOT semantic understanding.
  No document understanding, discourse understanding, or semantic organization needed.

  FORBIDDEN escalations:
    ✗ TLD Failure → "Document Understanding" (NO — it's algorithmic)
    ✗ TLD Failure → "Discourse Understanding" (NO — it's structural)
    ✗ TLD Failure → "Semantic Organization" (NO — it's geometric)
    ✗ TLD Failure → "LLM" (NO — it's deterministic)
```

---

## 16. Learning Signal Gate

```
TRUE_REUSABLE_SIGNAL_FOUND = NO

  Observed failure mechanisms:
    - "greedy band" (page-global band formation)
    - "column stability < 0.75" (contaminated column centers)
    - "text ratio < 0.45" (inherent numeric table)
  
  These are OBSERVED FAILURE MECHANISMS, NOT generalizable learning signals.
  
  Why NOT learning signals:
    1. "greedy band" is a specific algorithmic property of TLD's band formation,
       not a pattern that generalizes to other modules or tasks.
    2. "column stability < 0.75" is a threshold-specific symptom, not a signal.
    3. "text ratio < 0.45" is a threshold-specific symptom for a specific table type.
    
  Observed Failure Mechanism ≠ Generalizable Learning Signal
  
  No new Learning Signal created.
  No existing Learning Signal modified.
```

---

## 17. Final Bottleneck

```
For DCE-06 (TLD Failure Mechanism):

  PRIMARY: D (Evidence Perception / TLD Detection)
    → TLD detection algorithm fails on specific page patterns
    → Not Consumer (IS-11 integrated)
    → Not Evidence Organization (TLD organizes when it detects)
    → Not Human Semantic (0% E5)
    → Not Evaluation Standard (already policy)
    → Not Evidence Missing (raw evidence exists)

  SECONDARY: NONE
    → Once TLD detects, everything works
    → No secondary bottleneck

For Overall System (all 45 cases):
  PRIMARY: C (Consumer Integration) — 17/45 cases (DCE-01 to DCE-04, unchanged)
  SECONDARY: D (Evidence Perception) — 2/45 cases (DCE-05 TLD Detection, unchanged)
```

---

## 18. Final Questions Answered

### Q1: AMB-135 为什么失败?
**Page-Global Contamination (primary) + Inherent Low Text Ratio (secondary).**
Table covers 15% of page. 17 contaminating multicol rows pollute column centers (align=0.268). Even in isolation, text_ratio=0.195 (numeric-heavy architecture table).

### Q2: AMB-262 为什么失败?
**Page-Global Contamination (only).**
Table covers 11% of page. 28 contaminating multicol rows pollute column centers (align=0.226). Local isolation passes all checks (align=1.000, text_ratio=0.822).

### Q3: 两者是不是同一个 Failure Mechanism?
**PARTIALLY.** Same PRIMARY mechanism (T8 Page-global contamination). AMB-135 has ADDITIONAL SECONDARY mechanism (T7 Text ratio threshold). AMB-262 has no secondary.

### Q4: Failure 最早发生在哪个 TLD Stage?
**Stage E (Column Stability).** Both AMB-135 and AMB-262 fail at avg_alignment < 0.75. Stage C (band formation) is WHERE contamination enters, but Stage E is WHERE it's detected and causes rejection.

### Q5: 成功案例为什么没有失败?
**Table dominates page (95-97% coverage).** Global band = table. No contaminating multicol rows. Column stability high (0.75-1.0). Text ratio passes (0.60-0.87).

### Q6: "greedy band" 是否已经被证明?
**PROVEN.** Local isolation test shows alignment rises from 0.23-0.27 (global) to 0.96-1.00 (local). Success cases have 0 contaminating rows. Failure cases have 17-28 contaminating rows.

### Q7: 这是 TLD Detection 还是 TLD Representation 还是 Consumer Integration?
**TLD Detection (Case B).** TLD data model CAN express different_column. Detection algorithm fails. Consumer correctly consumes when TLD provides.

### Q8: P2 是否已经提供足够底层 Evidence?
**YES.** P2 provides all L1/L2 geometry (same_y_band, h_gap, fragment positions). L3 interpretation is TLD's responsibility.

### Q9: 是否真的需要 New Observation / LLM / New Module?
**NO to all.** Failure is algorithmic (band formation locality + text ratio threshold). Not semantic, not missing evidence, not missing module.

### Q10: 下一步如果继续，应该研究 TLD 内部哪一个最小问题?
**TLD Band Formation Locality.** The smallest issue is: band formation only breaks on `is_wide_text` (single-fragment wide rows). Multi-fragment prose (from PDF citation/math splitting) doesn't break the band. A locality constraint would resolve Mechanism 1 (AMB-262, AMB-313, AMB-135 primary).

Secondary: Text ratio threshold for numeric tables (Mechanism 2) — but this involves threshold tuning (FORBIDDEN).

---

## 19. Root Cause Chain Summary

```
Mechanism 1 (AMB-135 primary, AMB-262, AMB-313):

  PDF page has small table (11-15% of page) + formulas + prose with citations
    ↓
  PDF extraction splits prose into multiple spans (citations, math symbols)
    ↓
  TLD sees multi-fragment prose as is_multicol=True (ANCHOR, not BREAKER)
    ↓
  TLD band breaker (is_wide_text) only triggers on SINGLE-fragment wide rows
    ↓
  Multi-fragment prose rows DON'T break the band
    ↓
  Band extends from table to page bottom (page-global, 91-97% of page)
    ↓
  Non-table multicol rows (17-28) pollute _cluster_xs column center computation
    ↓
  Column centers unstable (mixed table + formula + prose positions)
    ↓
  avg_alignment drops below 0.75 (0.23-0.54)
    ↓
  Table rejected at Stage E (column stability check)
    ↓
  IS-11 fallback → MERGE/ABSTAIN (FP/UNKNOWN)
    ↓
  Human: KEEP_SEPARATE (uses page visual to see different columns)

Mechanism 2 (AMB-135 secondary, AMB-462 primary):

  Table is numeric/symbolic-heavy (architecture spec / benchmark results)
    ↓
  Most cells are short numeric strings or math symbols
    ↓
  _is_text_cell returns False for most cells (len < 3 OR _is_math_fragment)
    ↓
  text_ratio < 0.45 (0.163-0.195)
    ↓
  Table rejected at Stage F (text ratio check)
    ↓
  (For AMB-462: band properly formed, align=1.0, but text_ratio fails)
```

---

## 20. Limitations

1. **8-case sample**: Only 8 cases traced (2 failures, 4 success, 2 partial/miss). Mechanisms may differ on untraced cases.

2. **Local isolation test is synthetic**: The y-ranges for local isolation were manually identified. TLD does not perform local isolation — this test proves the mechanism, not a solution.

3. **TLD source analysis**: Based on current Frozen TLD (sha256=022f5c21). Production behavior may differ if TLD is updated (but TLD is FROZEN).

4. **AMB-462 different mechanism**: AMB-462's failure (text ratio, not contamination) is a separate mechanism. The 2/45 IS-11 critical cases (AMB-135, AMB-262) share Mechanism 1, but AMB-462 shows Mechanism 2 can also cause failure independently.

5. **Text ratio decomposition**: _is_text_cell and _is_math_fragment are TLD-internal heuristics. Their behavior on edge cases (e.g., '700M', 'HS', 'BQ') may not match human intuition of "text vs numeric".

6. **No P7 cross-validation**: P7 has no TLD, so DCE-06 mechanisms cannot be cross-validated on P7.

---

## 21. Governance Gate

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
