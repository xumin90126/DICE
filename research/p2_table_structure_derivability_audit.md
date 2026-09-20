# P2 Geometry → Table Structure Derivability Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY / NO MODIFICATION / FROZEN INTACT / STOP

---

## 1. Executive Summary

```
FINAL_STATUS = P2_STRUCTURAL_EXPRESSIBILITY_PARTIALLY_SUPPORTED

P2 can express:
  Level-1 (Geometry Facts):   FULL — bbox, alignment, distance, overlap, bands
  Level-2 (Structural Relations): PARTIAL — SameBandSeparatedPair, XAligned, YAligned,
    LocalGridCandidate, LocalRowCandidate, LocalColumnCandidate
  Level-3 (Structural Interpretation): NONE — Table Membership, Cell Assignment,
    Header, Body NOT expressible from P2 alone

KEY FINDING:
  P2 geometry is IDENTICAL for Table, Prose, and Figure cases.
  SameBandSeparatedPair (G1) = True for ALL 545 candidate pairs (Table=539, Prose=4, Figure=2).
  LocalGridCandidate (G4) = True for Table (517), Prose (3), AND Figure (1).
  → P2 CANNOT distinguish Table from Prose/Figure.
  → P2 provides NECESSARY but NOT SUFFICIENT conditions for table structure.

TLD adds information P2 CANNOT express:
  - TABLE MEMBERSHIP (is_in_table) — NOT derivable from P2
  - CELL ASSIGNMENT (a_cell=[row,col]) — NOT derivable from P2
  - TABLE BOUNDARIES — NOT derivable from P2

TLD is NOT a pure P2 derivation:
  TLD = P2 geometry + visual line heuristics + regex pattern matching + thresholds
  → TLD is a STRUCTURAL INTERPRETATION layer, not a P2 derivation

MINIMUM_SAFE_STRUCTURAL_FACT = SAME_BAND_SEPARATED_PAIR (G1)
  - Deterministic: YES (same_y_band=True AND h_gap>0 AND v_overlap>0)
  - Semantic leakage: NONE (pure geometry)
  - Authority: 0 (no structural interpretation)
  - But: does NOT distinguish table from prose/figure

TLD_INFORMATION_OVERLAP = PARTIAL
  - TLD's row/column USES P2 alignment (organization)
  - TLD's table membership CREATES new fact (interpretation)
  - TLD's cell assignment CREATES new fact (interpretation)

P2_TLD_RELATION = EVIDENCE_SOURCE → INTERPRETATION_LAYER
  P2 = Structural Evidence Source (raw geometry)
  TLD = Structural Interpretation / Detection (table, cell, membership)
  IS-11 consumer = uses TLD interpretation only, NOT P2 evidence

M_B_DEPENDENCY = HYBRID (uses P2 for diagnosis, consumer uses TLD)
PH02_RELATION = P2 granularity sufficient, but alignment group is page-wide (locality issue)

PRIMARY_BOTTLENECK = D (Consumer Integration) — P2 evidence exists, IS-11 doesn't use it
  But P2 alone CANNOT replace TLD (no table membership)
  → Future: safe P2 organization into Structural Context (research only, not engineered)

NO LLM NEEDED. NO DOCUMENT DISCOURSE NEEDED. NO NEW OBSERVATION NEEDED.
STOP = TRUE
```

> **P2 Geometry 可以确定性表达 Level-2 Structural Relations（SameBandSeparatedPair, XAligned, YAligned, LocalGridCandidate, LocalRowCandidate, LocalColumnCandidate），但不能表达任何 Level-3 Structural Interpretation（Table Membership, Cell Assignment, Header, Body）。P2 几何对 Table、Prose、Figure 完全相同——SameBandSeparatedPair 在全部 545 个候选对上为 True。TLD 增加了 P2 无法表达的信息（table membership, cell assignment），且 TLD 不是纯 P2 派生——它使用了额外的视觉行重建启发式和 regex。P2 是 Structural Evidence Source，TLD 是 Structural Interpretation Layer。最小安全结构事实是 SameBandSeparatedPair（无语义泄漏，但不足以区分 table/prose/figure）。**

---

## 2. P2 Frozen Source Verification

```
P2_SOURCE = perception/sandbox/geometry/
P2_ENGINE = geometry_engine.py (sha256=388e7939d334458e, VERIFIED)
P2_CONFIG = geometry_config.py (sha256=7ef3629e5a9b819c, VERIFIED)
P2_SCHEMA = geometry_observation.py (sha256=7731377cb8468c91, VERIFIED)

P2_FROZEN_PARAMS:
  y_band_tolerance = 3.0pt
  x_band_tolerance = 3.0pt
  alignment_tolerance = 2.0pt
  overlap_tolerance = 0.5pt
  horizontal_distance_threshold = 12.0pt
  vertical_distance_threshold = 12.0pt
  iou_tolerance = 0.001
  containment_ratio_threshold = 0.95

P2_DESIGN_PRINCIPLE: "Pure geometric facts, not interpretations. NO semantic classification."
```

---

## 3. P2 Direct Fields (Level-1 Geometry Facts)

### SingleObservationGeometry

| Field | Type | Source | Semantic? |
|---|---|---|---|
| bbox | [x0,y0,x1,y1] | P1 (copied) | NO |
| width | float | x1-x0 | NO |
| height | float | y1-y0 | NO |
| center_x | float | (x0+x1)/2 | NO |
| center_y | float | (y0+y1)/2 | NO |
| normalized_x | float | cx/page_width | NO |
| normalized_y | float | cy/page_height | NO |
| same_y_band_members | List[str] | page-wide y-band | NO |
| same_x_band_members | List[str] | page-wide x-band | NO |
| left_alignment_group | List[str] | page-wide x0 alignment | NO |
| right_alignment_group | List[str] | page-wide x1 alignment | NO |
| top_alignment_group | List[str] | page-wide y0 alignment | NO |
| bottom_alignment_group | List[str] | page-wide y1 alignment | NO |
| center_alignment_group | List[str] | page-wide center alignment | NO |
| spatial_cluster_members | List[str] | within v_dist_threshold | NO |
| x_projection_overlap_count | int | count of x-overlapping obs | NO |

### PairwiseRelation

| Field | Type | Source | Semantic? |
|---|---|---|---|
| direction | str | LEFT_OF/RIGHT_OF/ABOVE/BELOW/OVERLAPPING/CONTAINED_BY/CONTAINS/SAME_POSITION | NO |
| horizontal_distance | float | x gap | NO |
| vertical_distance | float | y gap | NO |
| horizontal_overlap | float | x overlap length | NO |
| vertical_overlap | float | y overlap length | NO |
| bbox_overlap_area | float | h_overlap × v_overlap | NO |
| iou | float | intersection/union | NO |
| left_alignment | bool | \|Δx0\| ≤ 2.0pt | NO |
| right_alignment | bool | \|Δx1\| ≤ 2.0pt | NO |
| top_alignment | bool | \|Δy0\| ≤ 2.0pt | NO |
| bottom_alignment | bool | \|Δy1\| ≤ 2.0pt | NO |
| center_alignment | bool | both cx and cy aligned | NO |
| same_y_band | bool | \|Δcy\| ≤ 3.0pt | NO |
| same_x_band | bool | \|Δcx\| ≤ 3.0pt | NO |

> **All P2 fields are pure geometry. NO semantic classification. NO table/column/row/cell/header/body concepts.**

---

## 4. P2 Structural Derivability Matrix

| Structural Fact | P2 Direct | Deterministically Derivable | Required Inputs | Semantic Leakage | Status |
|---|---|---|---|---|---|
| Same Y Band | YES | YES | center_y, y_band_tolerance | NONE | **SAFE** |
| Horizontally Separated | YES | YES | horizontal_distance > 0 | NONE | **SAFE** |
| X Alignment | YES | YES | left/right_alignment | NONE | **SAFE** |
| Vertical Continuity | YES | YES | vertical_distance, spatial_cluster | NONE | **SAFE** |
| **G1: SameBandSeparatedPair** | DERIVED | YES | same_y_band=True, h_gap>0, v_overlap>0 | NONE | **SAFE** |
| **G2: XAlignedCluster** | DERIVED | YES | left_alignment OR right_alignment | NONE | **SAFE** |
| **G3: YAlignedCluster** | DERIVED | YES | same_y_band | NONE | **SAFE** |
| **G4: LocalGridCandidate** | DERIVED | YES | same_y_band, same_style, line_obs≥3 | **PARTIAL** — same for prose | **UNSAFE** |
| **G5: LocalRowCandidate** | DERIVED | YES | same_y_band, h_gap>0 | **PARTIAL** — same for prose | **UNSAFE** |
| **G6: LocalColumnCandidate** | DERIVED | YES | (left/right alignment), v_gap>0 | NONE | **SAFE** (but requires vertical pair) |
| Same Table Row | NO | **NO** | requires table membership | HIGH | **NOT EXPRESSIBLE** |
| Different Table Column | NO | **NO** | requires table membership | HIGH | **NOT EXPRESSIBLE** |
| Same Table Cell | NO | **NO** | requires cell assignment | HIGH | **NOT EXPRESSIBLE** |
| Table Header | NO | **NO** | requires header detection | HIGH | **NOT EXPRESSIBLE** |
| Table Body | NO | **NO** | requires body detection | HIGH | **NOT EXPRESSIBLE** |
| Row Number Column | NO | **NO** | requires column type detection | HIGH | **NOT EXPRESSIBLE** |
| **Table Membership** | NO | **NO** | requires table detection | HIGH | **NOT EXPRESSIBLE FROM P2 ALONE** |

---

## 5. Level-2 Relation Proofs

### G1: SAME_BAND_SEPARATED_PAIR

```
Input: same_y_band(A,B) = True
       horizontal_distance(A,B) > 0
       vertical_overlap(A,B) > 0

Transform: logical AND of three P2 boolean facts

Output: SAME_BAND_SEPARATED_PAIR = True

Authority = 0
Semantic interpretation = NONE
```

### G2: X_ALIGNED_CLUSTER

```
Input: left_alignment(A,B) = True  OR  right_alignment(A,B) = True

Transform: logical OR of two P2 boolean facts

Output: X_ALIGNED_CLUSTER = True

Authority = 0
Semantic interpretation = NONE
```

### G5: LOCAL_ROW_CANDIDATE

```
Input: same_y_band(A,B) = True
       horizontal_distance(A,B) > 0

Transform: logical AND

Output: LOCAL_ROW_CANDIDATE = True

Authority = 0
Semantic interpretation = NONE (candidate only, not assertion)
```

> **WARNING: G5 is "row candidate" not "table row". Prose words on the same line also satisfy G5.**

---

## 6. Counterexample Pressure Tests

### Case 1: Figure Caption (AMB-414)

```
Text A: 'FIG. 9:'  Text B: 'Left:'
GT: MERGE (figure caption, NOT table)

P2 Facts:
  same_y_band = True (|Δcy|=0.00)
  h_gap = 18.1 > 0
  v_overlap = 11.9 > 0
  same_style = True
  line_obs = 5

G1 (SameBandSeparatedPair) = True ✓
G4 (LocalGridCandidate) = True ✓
G5 (LocalRowCandidate) = True ✓

→ P2 geometry for Figure Caption is IDENTICAL to Table
→ G1, G4, G5 CANNOT distinguish Figure Caption from Table
→ If interpreted as "table row", this is SEMANTIC LEAKAGE
```

### Case 2: Prose (AMB-005)

```
Text A: 'unsurprising) and then degrades rapidly.'  Text B: 'Unexpectedly,'
GT: KEEP_SEPARATE (prose sentence boundary, NOT table)

P2 Facts:
  same_y_band = True
  h_gap = 10.0 > 0
  v_overlap = 10.0 > 0
  same_style = True
  line_obs = 3

G1 = True ✓
G4 = True ✓
G5 = True ✓

→ P2 geometry for Prose is IDENTICAL to Table
→ G1, G4, G5 CANNOT distinguish Prose from Table
```

### Case 3: Multi-Column Text (hypothetical)

```
Two text fragments in different columns of a multi-column layout:
  same_y_band = True (same y position)
  h_gap > 0 (different x positions)

G1 = True ✓
G5 = True ✓

→ Multi-column prose would produce IDENTICAL P2 geometry to table
→ P2 has NO independent evidence for table membership
```

### Counterexample Conclusion

```
G1, G4, G5 are TRUE for: Table (539), Prose (4), Figure (2) = ALL 545 pairs
→ P2 Level-2 relations CANNOT distinguish Table from non-Table
→ Any Level-3 interpretation (table row, table column) would have SEMANTIC LEAKAGE
→ Table Membership is NOT EXPRESSIBLE FROM P2 ALONE
```

---

## 7. P2 vs TLD Information Comparison

| Information | P2 | TLD | Who Provides? |
|---|---|---|---|
| bbox | YES | NO | P2 |
| x/y alignment | YES | NO | P2 |
| distance/overlap | YES | NO | P2 |
| same_y_band | YES | NO | P2 |
| alignment groups | YES | NO | P2 |
| spatial clusters | YES | NO | P2 |
| **table membership** | **NO** | **YES** | **TLD** |
| **cell assignment** | **NO** | **YES** | **TLD** |
| **different_cell** | **NO** | **YES** | **TLD** |
| **table boundaries** | **NO** | **YES** | **TLD** |
| header detection | NO | NO | NEITHER |

### TLD Adds 3 Critical Facts P2 Cannot Express:

1. **TABLE MEMBERSHIP** (is_in_table) — whether a span is inside a table
2. **CELL ASSIGNMENT** (a_cell=[row,col]) — which cell a span belongs to
3. **TABLE BOUNDARIES** — where the table region is

> **Without these 3 facts, P2 cannot determine if two same-band-separated spans are in the same table or not.**

### TLD is NOT a Pure P2 Derivation

TLD uses:
- P2 geometry (alignment, same_y_band) — **organization**
- Visual line reconstruction — **heuristic** (not in P2)
- `_VALUE_RE` regex pattern matching — **heuristic** (not in P2)
- Fragment count / column stability thresholds — **heuristic** (not in P2)

```
TLD = P2 geometry + visual line heuristics + regex + thresholds
→ TLD is a STRUCTURAL INTERPRETATION layer, not a P2 derivation
→ TLD_INFORMATION_OVERLAP = PARTIAL
```

---

## 8. M-B Dependency Analysis

```
M_B_DEPENDENCY = HYBRID
```

- M-B **diagnosed** using P2 facts: found that frozen geometry evidence is complete
- M-B found: IS-11 consumer connects to TLD (chunker heuristic), NOT to frozen P2 structural facts
- M-B's "correct-vs-blind" comparison proved evidence is complete on blind pages
- But M-B did NOT prove P2 can replace TLD — it proved P2 evidence EXISTS but is NOT USED

> **M-B is NOT a P2 derivation. M-B is a diagnosis that P2 evidence exists but IS-11 consumer doesn't use it. The consumer uses TLD, not P2.**

---

## 9. PH-02 Relation Analysis

```
PH02_RELATION = P2 granularity sufficient, but alignment group locality is insufficient
```

PH-02 failed because:
- `left_alignment_group` was treated as "column"
- The group was **page-wide** — included table column members AND body text members
- Heterogeneous group → whole-group test failed

P2's `left_alignment_group` is page-wide by design:
- It lists ALL observations on the page with aligned left edge
- It does NOT have local scope (e.g., "within a table region")
- This is the PH-02 lesson: page-wide groups are heterogeneous

```
P2_GRANULARITY_SUFFICIENT = YES (individual bbox, pairwise facts are fine)
P2_LOCALITY_INSUFFICIENT = YES (alignment groups are page-wide, not local)
```

> **PH-02's failure was NOT because P2 lacks granularity, but because the research object (page-wide alignment group) was too coarse. Individual P2 facts are sufficient; page-wide groups are not.**

---

## 10. Minimum Safe Structural Representation

### Safe (Authority=0, No Semantic Leakage):

```
G1: SAME_BAND_SEPARATED_PAIR
    = same_y_band(A,B) AND h_gap(A,B) > 0 AND v_overlap(A,B) > 0
    → Safe: pure geometry, no interpretation
    → But: does NOT distinguish table from prose/figure

G2: X_ALIGNED_CLUSTER
    = left_alignment(A,B) OR right_alignment(A,B)
    → Safe: pure geometry
    → But: page-wide (PH-02 lesson), needs local scope

G3: Y_ALIGNED_CLUSTER
    = same_y_band(A,B)
    → Safe: pure geometry
    → But: trivially true for all same-y pairs

G6: LOCAL_COLUMN_CANDIDATE
    = (left_alignment OR right_alignment) AND v_gap > 0
    → Safe: pure geometry, requires vertical pair
    → But: not applicable to same-y pairs (the IS-11 scope)
```

### Unsafe (Semantic Leakage):

```
G4: LOCAL_GRID_CANDIDATE
    = same_y_band AND same_style AND line_obs ≥ 3
    → Unsafe: same_style and line_obs are P3/P2-derived but
      this combination is TRUE for prose (3/4) and figure (1/2)
    → If interpreted as "table grid", this is semantic leakage

G5: LOCAL_ROW_CANDIDATE
    = same_y_band AND h_gap > 0
    → Unsafe: TRUE for ALL same-y separated pairs (prose, figure, table)
    → If interpreted as "table row", this is semantic leakage
```

### NOT Expressible:

```
SAME_TABLE_ROW: requires table membership
DIFFERENT_TABLE_COLUMN: requires table membership
SAME_TABLE_CELL: requires cell assignment
TABLE_HEADER: requires header detection
TABLE_BODY: requires body detection
TABLE_MEMBERSHIP: NOT EXPRESSIBLE FROM P2 ALONE
```

---

## 11. Key Conceptual Distinction

```
Geometry Fact ≠ Structural Object
Structural Relation ≠ Structural Interpretation

same_y_band = True          → Geometry Fact (safe)
SAME_BAND_SEPARATED_PAIR    → Structural Relation (safe, but not table-specific)
SAME_TABLE_ROW              → Structural Interpretation (NOT expressible from P2)
TABLE_MEMBERSHIP            → Structural Interpretation (NOT expressible from P2)
```

> **P2 provides geometry facts and structural relations. TLD provides structural interpretation. The boundary between them is: TABLE MEMBERSHIP. P2 cannot determine if a span is in a table; TLD can (using heuristics). This is the irreducible gap.**

---

## 12. Final Research Questions

### Q1: P2 有哪些直接 Geometry Facts?

bbox, width, height, center, same_y_band, same_x_band, left/right/top/bottom/center alignment, horizontal/vertical distance, overlap, IoU, direction, alignment groups (page-wide), spatial clusters, x_projection_overlap_count.

### Q2: P2 可以确定性推导哪些 Level-2 Structural Relations?

G1 SameBandSeparatedPair, G2 XAlignedCluster, G3 YAlignedCluster, G4 LocalGridCandidate, G5 LocalRowCandidate, G6 LocalColumnCandidate. All deterministic, all pure geometry.

### Q3: P2 可以直接支持哪些 Level-3 Structural Interpretations?

**NONE.** No Level-3 interpretation (table row, table column, table cell, table membership, header, body) is expressible from P2 alone.

### Q4: 哪些看起来可以推导，但实际存在 Semantic Leakage?

G4 LocalGridCandidate and G5 LocalRowCandidate. Both are TRUE for Table, Prose, AND Figure. If interpreted as "table grid" or "table row", they produce semantic leakage.

### Q5: P2 能否表达 Row Structure?

**PARTIAL.** P2 can express "same y band" and "same band separated pair" (row candidate). But P2 CANNOT express "same table row" (requires table membership).

### Q6: P2 能否表达 Column Structure?

**PARTIAL.** P2 can express "x alignment" and "local column candidate" (for vertical pairs). But P2 CANNOT express "same table column" (requires table membership). Also, alignment groups are page-wide (PH-02 lesson).

### Q7: P2 能否表达 Cell Structure?

**NO.** Cell assignment requires table membership and cell coordinates, which P2 cannot express.

### Q8: P2 能否表达 Table Membership?

**NO. NOT EXPRESSIBLE FROM P2 ALONE.** This is the irreducible gap. P2 geometry is identical for table, prose, and figure cases.

### Q9: P2 能否表达 Header?

**NO.** Header detection requires table structure and header/body distinction, none expressible from P2.

### Q10: TLD 相比 P2 到底增加了什么信息?

3 critical facts: (1) Table Membership (is_in_table), (2) Cell Assignment (a_cell=[row,col]), (3) Table Boundaries. These are structural interpretations NOT derivable from P2.

### Q11: M-B 使用的是 P2、TLD 还是 Hybrid?

**HYBRID.** M-B uses P2 facts for diagnosis (evidence exists), but the actual IS-11 consumer uses TLD (not P2). M-B proved P2 evidence exists but is not used by consumer.

### Q12: PH-02 的失败是否来自 P2 粒度问题?

**NO — P2 granularity is sufficient.** PH-02 failed because the research object (page-wide left_alignment_group) was too coarse. Individual P2 facts are fine; page-wide groups are heterogeneous.

### Q13: 当前最小安全 Structural Representation 是什么?

**G1: SAME_BAND_SEPARATED_PAIR** (same_y_band=True AND h_gap>0 AND v_overlap>0). Pure geometry, no semantic leakage, authority=0. But does NOT distinguish table from prose/figure.

### Q14: 是否需要新的 Observation?

**NO.** P2 provides all geometry facts. TLD provides structural interpretation. The gap is Consumer Integration (D), not missing observation.

### Q15: 是否需要修改 TLD?

**NO.** TLD is FROZEN. Cannot modify.

### Q16: 是否需要 LLM?

**NO.** All structural detection is deterministic (TLD heuristics + P2 geometry).

### Q17: 是否需要 Document Discourse?

**NO.** No case requires discourse understanding. Local structural evidence is sufficient (when TLD works).

---

## 13. Critical Question Answer

> **TLD 是在创造新的 Structural Evidence，还是在把已有 P2 Geometry 组织成 Structural Interpretation？**

**BOTH, but primarily INTERPRETING:**

- TLD's row/column detection: **ORGANIZES** P2 alignment facts
- TLD's table membership: **CREATES** new structural fact (not in P2)
- TLD's cell assignment: **CREATES** new structural fact (not in P2)
- TLD's visual line reconstruction: **USES** additional heuristics (not in P2)

> **TLD is primarily a STRUCTURAL INTERPRETATION / DETECTION layer. P2 is a STRUCTURAL EVIDENCE SOURCE. The future research question is NOT "how to improve Table Detector" but "how to safely organize frozen P2 evidence into Structural Context without semantic leakage" — but this is RESEARCH ONLY, not to be engineered.**

---

## 14. Retrospective vs Generalizable

```
All Level-2 relations are RETROSPECTIVELY_DERIVABLE on current 545 pairs.
None are GENERALIZABLE without independent corpus validation.
```

> **"可推导" ≠ "可泛化"。当前 545 pairs 上的 P2→Level-2 derivation 是 retrospective。没有独立 corpus 验证时，不得声明 generalizable。**

---

## 15. Final Status

```
FINAL_STATUS = P2_STRUCTURAL_EXPRESSIBILITY_PARTIALLY_SUPPORTED

P2 can express Level-1 (full) and Level-2 (partial) but NOT Level-3.
P2 geometry is identical for Table/Prose/Figure.
Table Membership is NOT EXPRESSIBLE FROM P2 ALONE.

MINIMUM_SAFE_STRUCTURAL_FACT = SAME_BAND_SEPARATED_PAIR (G1)
TLD_INFORMATION_OVERLAP = PARTIAL
P2_TLD_RELATION = EVIDENCE_SOURCE → INTERPRETATION_LAYER
M_B_DEPENDENCY = HYBRID
PH02_RELATION = P2 granularity sufficient, locality insufficient

PRIMARY_BOTTLENECK = D (Consumer Integration) — P2 evidence exists, not used
  But P2 alone CANNOT replace TLD (no table membership)
  → Safe P2 organization into Structural Context = future research (NOT engineered)

RECOMMENDED_NEXT_STEP = READ-ONLY audit of TLD's visual line heuristics
  → Understand what TLD adds beyond P2 (visual line reconstruction, regex, thresholds)
  → This informs whether safe P2 organization is feasible
```

---

## 16. Anti-Overdesign Gate

```
NOT writing: "P2 can detect Table"
NOT writing: "same_y_band + h_gap > 0 = different_column"
NOT writing: "x alignment = table column"
NOT writing: "repeated alignment = table"
NOT writing: "P2 replaces TLD"
NOT creating: Structural Context Engine
NOT creating: Table Detector
NOT creating: Relation Engine
NOT creating: Pattern Engine
NOT creating: Learning Engine
NOT introducing: LLM
NOT modifying: P2, TLD, IS-11, Signal 3, GT
NOT implementing: any derivation
```

> **All forbidden semantic leaps avoided. Level-2 relations labeled as "candidate" not "assertion". Level-3 interpretations marked NOT EXPRESSIBLE.**

---

## 17. Governance Gate

```
DICE_CORE_MODIFICATION              = NO
P2_MODIFICATION                     = NO
P1_P7_MODIFICATION                  = NO
TLD_MODIFICATION                    = NO
IS11_MODIFICATION                   = NO
M_B_MODIFICATION                    = NO
PH02_MODIFICATION                   = NO
GT_MODIFICATION                     = NO
SIGNAL_MODIFICATION                 = NO
EVIDENCE_CUE_MODIFICATION           = NO
LLM                                 = NO
NEW_OBSERVATION                     = NO
NEW_MODULE                          = NO
NEW_ENGINE                          = NO
RUNTIME_CHANGE                      = NO
CAPABILITY_CHANGE                   = NO
FROZEN_BASELINE                     = INTACT (drift=0/7, P2=388e7939/7ef3629e/7731377c, TLD=022f5c21, GT=7349963d)
FROZEN_EXPERIMENT                   = INTACT
IMPLEMENTATION_AUTHORIZED           = FALSE
EXPERIMENT_AUTHORIZED               = FALSE
FORMAL_EXPERIMENT                   = NOT_STARTED
STOP                                = TRUE
```

---

## 18. 最终原则验证

> *Geometry Fact ≠ Structural Object*

✓ 遵守：P2 Level-1 是 Geometry Fact，Level-3 是 Structural Object。明确区分。P2 不能表达 Table Membership。

> *Structural Relation ≠ Structural Interpretation*

✓ 遵守：Level-2 (SameBandSeparatedPair) ≠ Level-3 (SameTableRow)。Level-2 是 geometry 组合，Level-3 需要 table membership。

> *不要把"可推导"写成"可泛化"*

✓ 遵守：所有 Level-2 derivation 标记为 RETROSPECTIVELY_DERIVABLE，不声明 GENERALIZABLE。

> *禁止: same_y_band + h_gap > 0 = different_column*

✓ 遵守：G5 (LocalRowCandidate) 标记为 UNSAFE（semantic leakage），明确指出 prose 和 figure 也满足此条件。

> *禁止: P2 replaces TLD*

✓ 遵守：明确写出 P2 不能表达 Table Membership，TLD 增加了 3 个 P2 无法表达的关键事实。

`STOP = TRUE`。
