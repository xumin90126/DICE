# DICE Potential Evaluation Candidate Set — Construction Report

**Date**: 2026-09-12
**Mode**: IMPLEMENTATION (EVALUATION_RESEARCH_TOOLING_ONLY)
**Script**: `tmp/potential_evaluation_case_construction.py`
**Output**: `tmp/potential_evaluation_case_set.json`

---

## 1. Summary

From the existing 545-candidate pool, a **Potential Evaluation Candidate Set** of **83 candidates** was constructed using structural classification, triviality filtering, coverage construction, evidence availability recording, and independence constraints.

**Key improvement over historical 45-case set**:
- Trivial proportion: 84% → 8% (controls only)
- Potential boundary coverage: ~6 → 65
- Page concentration: max 8/page → max 3/page
- Ceiling risk HIGH: ~84% → 8%

**Important**: This is a **Potential Set**, NOT a validated Evaluation Set. Human Difficulty has NOT been assessed. GT has NOT been used for selection. Pilot observation is required before any formal use.

---

## 2. Input Verification

| Property | Value | Status |
|---|---|---|
| Input file | `tmp/is11_independent_candidate_universe.json` | READ-ONLY |
| Candidate count | 545 | ✅ matches expected |
| Input SHA256 | `5e86a1e94b89e0873ffabe34ac5e178b...` | recorded |
| Input size | 583,112 bytes | — |
| Input mutation | 0 | ✅ byte-identical after run |
| GT fields in candidates | NONE | ✅ no GT leakage |
| Human data in candidates | NONE | ✅ no human difficulty leakage |

---

## 3. Determinism Verification

| Run | SHA256 |
|---|---|
| Run 1 | `defbd4df3e4ee684cd1e3c05676c8723...` |
| Run 2 | `defbd4df3e4ee684cd1e3c05676c8723...` |

**DETERMINISM = PASS** (identical hashes)

---

## 4. Structural Classification (545 Candidates)

### By Structure Family

| Family | Count | % |
|---|---|---|
| TABLE_NUMERIC | 261 | 48% |
| ROW_LABEL_VALUE | 113 | 21% |
| TABLE_HEADER | 53 | 10% |
| OTHER | 51 | 9% |
| PROSE | 44 | 8% |
| AXIS | 12 | 2% |
| FIGURE_CAPTION | 11 | 2% |

### By Evaluation Opportunity

| Opportunity | Count | % |
|---|---|---|
| LOW | 326 | 60% |
| MEDIUM | 122 | 22% |
| UNKNOWN | 51 | 9% |
| HIGH | 46 | 8% |

### By Cue Relevance

| Relevance | Count | % |
|---|---|---|
| LOW | 326 | 60% |
| HIGH | 90 | 17% |
| MEDIUM | 78 | 14% |
| UNKNOWN | 51 | 9% |

### By Evidence Availability

| Availability | Count | % |
|---|---|---|
| PARTIAL | 545 | 100% |

All candidates have PARTIAL evidence availability: image (PDF exists) + structural evidence (geometry + style) are available, but TLD and Cue are NOT computed at candidate level.

### By Ceiling Risk (Pre-Pilot, Structural)

| Risk | Count | % |
|---|---|---|
| HIGH | 326 | 60% |
| MEDIUM | 122 | 22% |
| UNKNOWN | 51 | 9% |
| LOW | 46 | 8% |

### Potential Coverage

| Dimension | Count |
|---|---|
| Potential boundary | 151/545 |
| Potential conflict | 194/545 |
| Near-duplicate groups | 44 |
| Candidates in dup groups | 100 |
| Unique doc+page | 39 |

---

## 5. Selection Results

### Overview

| Metric | Value |
|---|---|
| Total candidates | 545 |
| Selected | 83 |
| Excluded | 462 |
| Controls (LOW kept) | 7 |

### Selected by Structure Family

| Family | Count | % of selected |
|---|---|---|
| ROW_LABEL_VALUE | 32 | 39% |
| PROSE | 31 | 37% |
| FIGURE_CAPTION | 11 | 13% |
| TABLE_HEADER | 4 | 5% |
| OTHER | 2 | 2% |
| TABLE_NUMERIC | 2 | 2% (controls) |
| AXIS | 1 | 1% (control) |

### Selected by Evaluation Opportunity

| Opportunity | Count |
|---|---|
| HIGH | 37 |
| MEDIUM | 37 |
| LOW | 7 (controls) |
| UNKNOWN | 2 |

### Selected by Ceiling Risk

| Risk | Count |
|---|---|
| LOW | 37 |
| MEDIUM | 37 |
| HIGH | 7 (controls) |
| UNKNOWN | 2 |

### Document Distribution

| Document | Count | Share | Exceeds 35%? |
|---|---|---|---|
| is11_resnet | 26 | 31% | No |
| is11_med_001 | 24 | 29% | No |
| is11_efficientnet | 22 | 26% | No |
| is11_cs_001 | 11 | 13% | No |

### Exclusion Reasons

| Reason | Count |
|---|---|
| LOW_EVALUATION_VALUE | 319 |
| PAGE_CONCENTRATION_LIMIT | 138 |
| NEAR_DUPLICATE | 5 |

### Page Concentration

- Max cases per page: **3** (enforced constraint)
- Unique pages represented: **38**
- Pages with >10 candidates in pool: 13 (concentration existed in pool, resolved by constraint)

---

## 6. Historical 45-Case vs Potential Set Comparison

### Descriptive Comparison (NOT claiming effectiveness)

| Dimension | Historical 45 | Potential 83 | Change |
|---|---|---|---|
| **Trivial / LOW proportion** | 84% (38/45) | 8% (7/83, controls) | ↓ 76pp |
| **Structure families** | 6 | 7 | +1 |
| **Potential boundary** | ~6 | 65 | ↑ 10x |
| **UNKNOWN opportunity** | 0 | 2 | ↑ from 0 |
| **Potential conflict** | 2 | 30 | ↑ 15x |
| **Max cases/page** | 8 | 3 | ↓ 63% |
| **Ceiling risk HIGH** | ~84% | 8% | ↓ 76pp |
| **Ceiling risk LOW** | ~13% | 45% | ↑ 32pp |
| **Document max share** | 40% (efficientnet) | 31% (resnet) | ↓ 9pp |

### Structural Improvements

1. **Trivial proportion reduced**: 84% → 8%. The dominant failure mode of the historical set (overwhelmingly trivial table pairs) is addressed.
2. **Boundary coverage expanded**: ~6 → 65 potential boundary cases. The MERGE/KEEP_SEPARATE decision boundary now has substantial representation.
3. **Page concentration controlled**: max 8/page → max 3/page. Independence is structurally enforced.
4. **Ceiling risk redistributed**: HIGH ceiling risk cases reduced from 84% to 8% (controls only). LOW ceiling risk cases increased from 13% to 45%.
5. **Document balance improved**: most over-represented document share reduced from 40% to 31%.

### What This Does NOT Prove

- ❌ Does NOT prove the Potential Set is "more effective" — only that it addresses known structural problems
- ❌ Does NOT prove cases are "difficult" — Human Difficulty requires Pilot observation
- ❌ Does NOT prove Cue will have measurable effect — requires formal experiment
- ❌ Does NOT establish GT distribution — GT must be adjudicated AFTER selection
- ❌ Does NOT validate case independence beyond structural heuristics — true independence requires near-duplicate audit

---

## 7. Selection Methodology

### Classification Features Used (ALL structural, NO GT, NO human data)

| Feature | Source | Used For |
|---|---|---|
| text_a, text_b content | P1 output | Structure family classification |
| is_numeric() | deterministic | TABLE_NUMERIC vs PROSE |
| text length | deterministic | HEADER vs PROSE |
| punctuation pattern | deterministic | PROSE_BOUNDARY detection |
| figure markers ("FIG") | deterministic | FIGURE_CAPTION detection |
| h_gap | P3 geometric | Conflict detection |
| dy | P3 geometric | Independence |
| same_style | P3 style | Conflict detection |
| line_obs_count | P3 context | Cue relevance |
| bbox positions | P1 output | Near-duplicate detection |
| page, doc_id | P1 metadata | Independence grouping |

### Selection Priority (Applied in Order)

1. Research-question alignment (HIGH > MEDIUM > UNKNOWN > LOW)
2. Potential boundary / competing interpretation
3. Potential conflict
4. Cue relevance
5. Evidence sufficiency
6. Structural family coverage
7. Document diversity
8. Page diversity
9. Near-duplicate reduction

### Independence Constraints

| Constraint | Value | Rationale |
|---|---|---|
| Max per page | 3 | Same-page cases share layout context |
| Max per document | 35% | Prevent single-document dominance |
| Near-duplicate | Jaccard > 0.7 OR (y-diff < 5 AND Jaccard > 0.5) | Detect same-table pairs |
| Control ratio | 10% | Retain trivial cases as controls |

---

## 8. Evidence Availability

All 545 candidates have **PARTIAL** evidence availability:

| Evidence | Available? | Note |
|---|---|---|
| Image (PDF) | ✅ Yes | All 4 PDFs exist; images can be generated |
| TLD | ❌ Not computed | table_line_detector.py was NOT called during candidate generation |
| Structural evidence | ✅ Yes | Geometry + style features present in candidate data |
| Cue | ❌ Not computed | Evidence Cue not computed at candidate level |

**Implication**: TLD and Cue must be computed for the Potential Set before it can be used in a Pilot. This is a known gap, not a failure.

---

## 9. Control Cases

7 LOW evaluation value cases were retained as controls:

| Case ID | Family | Reason |
|---|---|---|
| (various) | TABLE_NUMERIC, TABLE_HEADER, AXIS | Surface-trivial, kept for baseline comparison |

**Rationale**: If all cases are complex, it's impossible to distinguish "Cue reduces effort" from "task is generally harder". Control cases provide a baseline for comparison. However, controls are limited to ~10% to prevent re-creating the historical ceiling effect.

---

## 10. Selection Ledger

The full selection ledger for all 545 candidates is in `tmp/potential_evaluation_case_set.json` under `selection_ledger`. Each entry records:

```
case_id
structure_family
evaluation_opportunity
cue_relevance
potential_boundary
potential_conflict
evidence_availability
ceiling_risk
independence_group
near_duplicate_group
selected (true/false)
exclusion_reason
is_control
```

### Exclusion Reasons Summary

| Reason | Count | Description |
|---|---|---|
| LOW_EVALUATION_VALUE | 319 | Trivial numeric/header pairs excluded |
| PAGE_CONCENTRATION_LIMIT | 138 | Exceeded ≤3/page constraint |
| NEAR_DUPLICATE | 5 | Text similarity > 0.7 with already-selected case |

**Note**: `LOW_EVALUATION_VALUE` exclusion is based on structural triviality (two numbers in different columns, two short headers), NOT on human difficulty or GT.

---

## 11. Known Limitations

1. **TLD not available**: TLD was not computed for candidates. Potential conflict/boundary assessments are based on geometric features only, not table structure detection.
2. **Cue not computed**: Cue relevance is estimated from evidence complexity, not actual Cue output. Actual Cue must be computed before Pilot.
3. **No GT adjudication**: The Potential Set has no GT. GT must be adjudicated AFTER selection (to prevent GT leakage).
4. **No Pilot validation**: Human Difficulty is NOT assessed. Ceiling risk is structural estimate only.
5. **Near-duplicate heuristic**: Jaccard similarity on word tokens may miss semantic duplicates with different surface forms.
6. **Document diversity**: 4 documents is exploratory, not generalizable. More documents would be needed for cross-layout claims.
7. **ROW_LABEL_VALUE dominance**: 32/83 selected are ROW_LABEL_VALUE. Some may still be trivial (short label + number). Pilot will reveal which are genuinely ambiguous.

---

## 12. What Requires Pilot Evidence

| Question | Requires |
|---|---|
| Which cases are non-trivial (time > 3s)? | Pilot behavioral data |
| What is B1 accuracy on non-trivial cases? | Pilot behavioral data |
| Which cases produce disagreement? | Multi-participant Pilot |
| Where does Cue actually change behavior? | B1 vs B2 Pilot comparison |
| Is UNKNOWN rate sufficient? | Pilot UNKNOWN usage data |
| Are ROW_LABEL_VALUE cases genuinely ambiguous? | Pilot behavioral data |
| True independence after semantic dedup? | Pilot cross-case analysis |

---

## 13. Next Steps (NOT Authorized This Round)

```
Potential Set (83 candidates) [THIS ROUND — DONE]
    ↓
Compute TLD for selected candidates [FUTURE]
    ↓
Compute Cue for selected candidates [FUTURE]
    ↓
GT adjudication (after selection, no leakage) [FUTURE]
    ↓
Pilot subset (10-15 cases) [FUTURE]
    ↓
Observe Human Difficulty [FUTURE]
    ↓
Case Quality Audit [FUTURE]
    ↓
Frozen Evaluation Set [FUTURE]
    ↓
Formal Human Experiment [FUTURE]
```

---

## 14. Governance

```
IMPLEMENTATION_SCOPE = EVALUATION_RESEARCH_TOOLING_ONLY
DICE_CORE_MODIFICATION = FALSE
FROZEN_BASELINE = INTACT
FROZEN_EXPERIMENT = INTACT
PRODUCTION = FALSE
RUNTIME_AUTHORITY = ZERO
ITERATIVE_LEARNING = INSUFFICIENT_EVIDENCE
FORMAL_HUMAN_EXPERIMENT = NOT_AUTHORIZED
EVALUATION_SET_VALIDITY = NOT_YET_ESTABLISHED
STOP = TRUE
```
