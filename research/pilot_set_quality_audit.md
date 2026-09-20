# DICE 54 Potential Pilot Candidates — Pilot Set Quality Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY PILOT SET QUALITY AUDIT
**Input**: 54 Potential Pilot Candidates from Human Construction Audit

---

## 1. Summary

| Metric | Count |
|---|---|
| Total candidates | 54 |
| Independent | 43 |
| Same-pattern (in duplicate groups) | 11 |
| RECOMMENDED | 42 |
| CONDITIONAL | 6 |
| REDUNDANT | 6 |
| Independent RECOMMENDED | 39 |

**Assessment**: The 54-candidate set has structural improvements over the historical 45-case set, but has identifiable issues: 11 candidates in 5 same-pattern groups, 2 documents dominating at 41% each, and 3 missing coverage dimensions (N, S, U).

---

## 2. Duplicate & Independence Audit

### Multi-Dimensional Detection

Detection used normalized text patterns (numbers→NUM, citations→[CITE], model names→MODEL), structural role (NUM_NUM, TEXT_NUM, NUM_TEXT, TEXT_TEXT), same doc+page, and position proximity.

### 5 Same-Pattern Groups Found (11 cases)

| Group | Type | Document | Cases | Pattern |
|---|---|---|---|---|
| dup_1 | SAME_PATTERN | resnet p5 | AMB-016, AMB-018 | "Nlayers" / "NUM" — same table, different rows |
| dup_2 | SAME_PATTERN | resnet p11 | AMB-082, AMB-084 | "baseline Faster R-CNN (MODEL)" / "NUM" — same table |
| dup_3 | SAME_PATTERN | resnet p12 | AMB-041, AMB-114, AMB-117 | "MODEL [CITE] (YEAR)" / "NUM" — same table, 3 rows |
| dup_4 | SAME_PATTERN | cs_001 p2 | AMB-432, AMB-433 | "N" / "Title" — section headers, same pattern |
| dup_5 | SAME_PATTERN | med_001 p17 | AMB-389, AMB-390 | "(Fig." / "N.X)" — same sentence, figure refs split |

### Independence Status

| Status | Count |
|---|---|
| INDEPENDENT | 43 |
| REDUNDANT (in same-pattern group) | 11 |

**Recommendation**: For each group, keep 1 representative, mark others as REDUNDANT. This would reduce effective set from 54 to ~49 independent cases.

---

## 3. Source Concentration

### Document Concentration

| Document | Count | Share | Status |
|---|---|---|---|
| is11_resnet | 22 | 41% | ⚠️ DOMINANT |
| is11_med_001 | 22 | 41% | ⚠️ DOMINANT |
| is11_cs_001 | 6 | 11% | OK |
| is11_efficientnet | 4 | 7% | Under-represented |

**Risk**: Two documents each contribute 41% of the set. If either document's findings are anomalous, they could skew results. EfficientNet is severely under-represented (only 4 cases, all PROSE).

### Page Concentration

18 pages have ≥2 cases. Maximum 3 per page (enforced by construction constraint). Key multi-case pages:

| Page | Count | Cases |
|---|---|---|
| resnet p8 | 3 | AMB-062, AMB-061, AMB-063 |
| resnet p1 | 3 | AMB-004, AMB-005, AMB-001 |
| resnet p12 | 3 | AMB-114, AMB-117, AMB-111 |
| med_001 p17 | 3 | AMB-389, AMB-390, AMB-394 |
| med_001 p13 | 3 | AMB-382, AMB-380, AMB-381 |

### Family Concentration

| Family | Count | Share |
|---|---|---|
| PROSE | 20 | 37% |
| ROW_LABEL_VALUE | 15 | 28% |
| FIGURE_CAPTION | 11 | 20% |
| TABLE_HEADER | 4 | 7% |
| TABLE_NUMERIC | 2 | 4% |
| OTHER | 1 | 2% |
| AXIS | 1 | 2% |

**Assessment**: PROSE + FIGURE_CAPTION = 57% — this is a major improvement over historical 84% TABLE. However, ROW_LABEL_VALUE at 28% still carries redundancy risk.

---

## 4. Research Question Coverage

### Coverage Opportunity Distribution

| Code | Label | Count | Status |
|---|---|---|---|
| B | Boundary (genuine MERGE/KEEP ambiguity) | 34 | ✅ Well covered |
| C | Cue conflict (potential structural conflict) | 13 | ⚠️ Machine-flagged, needs verification |
| P | Positive/ordinary (controls) | 7 | ✅ Controls present |
| N | Negative (cue plausible but wrong) | 0 | ❌ MISSING |
| S | System ≠ GT | 0 | ❌ MISSING (requires GT) |
| U | UNKNOWN / evidence insufficient | 0 | ❌ MISSING (requires TLD) |

### Missing Coverage

| Missing | Why | Impact |
|---|---|---|
| **N (Negative)** | No cases where Cue looks plausible but correct interpretation differs | Cannot test "Cue induces wrong MERGE/KEEP" |
| **S (System≠GT)** | Requires GT adjudication — not yet performed | Cannot test "Cue pushes Human toward wrong answer" |
| **U (UNKNOWN)** | Requires TLD computation to identify evidence-insufficient cases | Cannot test "UNKNOWN preservation / abstention boundary" |

**Critical gap**: N and S coverage cannot be filled without GT adjudication and Cue computation. U coverage cannot be filled without TLD computation. These are prerequisites for a complete Human Effort Reduction experiment.

---

## 5. Evidence Availability

| Evidence Type | Available | Note |
|---|---|---|
| Text (A/B content) | ✅ 54/54 | All candidates have text_a, text_b |
| Page context | ✅ 54/54 | PDFs exist, same-line context extractable |
| Geometry (bbox, h_gap, dy) | ✅ 54/54 | All have geometric features |
| Structural context (style, line_obs) | ✅ 54/54 | All have style signatures and line counts |
| TLD (table structure) | ❌ 0/54 | table_line_detector NOT run on candidates |
| Cue (evidence summary) | ❌ 0/54 | Evidence Cue NOT computed |

### B1 vs B2 Compatibility

| Condition | Available? | What's Missing |
|---|---|---|
| B1 (current evidence) | ✅ Yes | Text + geometry + style + line_obs |
| B2 (evidence + Cue) | ⚠️ Partial | Geometric Cue computable, but TLD-based Cue not available |

**Impact**: Without TLD, the Cue can only summarize geometric features (h_gap, dy, same_style, line_obs_count). It cannot tell Human "these spans are in different table columns" or "this is a table cell boundary". This significantly limits Cue informativeness for the 15 ROW_LABEL_VALUE cases where the key ambiguity is row-vs-column.

---

## 6. Research Role Distribution

| Role | Count | Description |
|---|---|---|
| CORE | 35 | Directly answers Evidence Distillation RQ (PROSE boundaries, figure captions, genuine row ambiguity) |
| SUPPORTING | 6 | Helpful but not core (section headers, reference entries, figure labels) |
| CONTROL | 7 | Baseline/sanity check (trivial table cells, headers, axis ticks) |
| REDUNDANT_RISK | 6 | In same-pattern groups — may create pseudo-independence |

---

## 7. Recommendation Distribution

| Recommendation | Count | Description |
|---|---|---|
| RECOMMENDED | 42 | Independent + valuable for Pilot |
| CONDITIONAL | 6 | Supporting role, value uncertain |
| REDUNDANT | 6 | In same-pattern groups, keep only 1 per group |

### Effective Independent Set

If REDUNDANT cases are reduced to 1 per group:
- 5 groups, 11 cases → keep 5, remove 6
- Effective set: 54 - 6 = **48 candidates**
- Independent RECOMMENDED: **39**

---

## 8. Historical 45 vs Audited 54 Comparison

| Dimension | Historical 45 | Audited 54 | Improvement |
|---|---|---|---|
| Independent cases | ~35 (many same-table) | 43 | ↑ |
| Trivial proportion | 84% | 13% (controls) | ↑ 71pp |
| Boundary coverage | ~6 | 34 | ↑ 5.7x |
| PROSE + FIGURE | 6 | 31 | ↑ 5.2x |
| Document max share | 40% | 41% | ≈ same |
| MISSING coverage | N, S, U | N, S, U | same gaps |
| TLD available | 21/30 | 0/54 | ↓ (not computed yet) |

---

## 9. Final Gate

### Q1: Are the 54 cases sufficiently independent?

**CONDITIONAL** — 43/54 are independent, but 11 are in 5 same-pattern groups. After deduplication (keep 1 per group), 48 effective independent cases remain. This is acceptable for a Pilot but should be reported.

### Q2: Do the 54 cases cover the core research question?

**CONDITIONAL** — Boundary coverage (B=34) is strong. Conflict coverage (C=13) exists but is machine-flagged and unverified. Three critical dimensions are missing: N (Negative), S (System≠GT), U (UNKNOWN). N and S require GT adjudication; U requires TLD computation.

### Q3: Is evidence sufficient for B1 vs B2?

**CONDITIONAL** — B1 is fully available (text + geometry + style). B2 is partially available: geometric Cue is computable, but TLD-based Cue is not. This limits Cue informativeness for table-related cases (15 ROW_LABEL_VALUE).

### Q4: Are there serious near-duplicates?

**YES** — 5 same-pattern groups affecting 11 cases. Not exact duplicates, but structural duplicates from same tables/pages.

### Q5: Is there serious source concentration?

**YES** — Two documents (resnet, med_001) each contribute 41%. EfficientNet severely under-represented (4 cases, 7%).

### Q6: Are there critical missing coverage dimensions?

**YES**:
- NO_NEGATIVE: No cases where Cue looks plausible but correct interpretation differs
- NO_SYSTEM_GT: Cannot assess without GT adjudication
- NO_UNKNOWN: Cannot identify without TLD computation

---

## 10. Final Assessment

### Is the 54-case set ready for GT Adjudication / Pilot Preparation?

**CONDITIONAL**

### What is known:
- 43/54 cases are independent
- 34 cases have genuine boundary coverage
- B1 evidence is fully available
- Structural diversity is much improved over historical 45

### What requires action before Pilot:
1. **Deduplicate**: Reduce 5 same-pattern groups to 1 representative each (54→48)
2. **Compute TLD**: Required for U coverage and Cue informativeness on table cases
3. **GT adjudication**: Required for S coverage and to verify B/C classifications
4. **Address document concentration**: Consider adding EfficientNet cases if available in untapped pool
5. **Cue computation**: Required before B2 condition can be tested

### What remains hypothesized:
- 13 "C" (conflict) cases are machine-flagged, may not all be genuine conflicts after GT
- ROW_LABEL_VALUE cases may prove trivial after TLD reveals clear column separation
- PROSE boundaries may have ceiling effect if all turn out to be KEEP_SEPARATE

---

## 11. Governance

```
DICE_CORE_MODIFICATION = FALSE
P1_P7_MODIFICATION = FALSE
TLD_MODIFICATION = FALSE
ATOMIC_OBSERVATION_MODIFICATION = FALSE
GT_MODIFICATION = FALSE
FORMAL_EXPERIMENT = FALSE

FROZEN_BASELINE = INTACT
FROZEN_EXPERIMENT = INTACT

PRODUCTION = FALSE
RUNTIME_AUTHORITY = ZERO

FINAL_EVALUATION_SET = NOT_ESTABLISHED

STOP = TRUE
```
