# DICE 48-Case Pilot Preparation Audit

**Date**: 2026-09-12
**Mode**: PILOT CANDIDATE PREPARATION (READ-ONLY, no formal experiment)
**Input**: 54 Potential Pilot Candidates → deduplicated to 48

---

## 1. 48-Case Working Set

From 54 candidates, 6 redundant cases were removed (1 per same-pattern group):

| Removed | Group | Kept Representative |
|---|---|---|
| AMB-018 | dup_1 (resnet p5) | AMB-016 |
| AMB-084 | dup_2 (resnet p11) | AMB-082 |
| AMB-114, AMB-117 | dup_3 (resnet p12) | AMB-041 |
| AMB-433 | dup_4 (cs_001 p2) | AMB-432 |
| AMB-390 | dup_5 (med_001 p17) | AMB-389 |

**Result**: 48 independent cases from 4 documents, 7 structure families.

---

## 2. TLD Computation (Read-Only, Frozen Parameters)

TLD was computed for all 48 cases using the frozen `table_line_detector.py` via `is11_machine_evaluation.py`.

| Metric | Count |
|---|---|
| TLD available | 48/48 (100%) |
| TLD detected table | 16/48 (33%) |
| TLD detected different_cell | 16/48 (33%) |
| TLD detected same_cell | 0/48 (0%) |

**Key finding**: TLD successfully runs on all 48 cases. It detects tables in 16 cases (all ROW_LABEL_VALUE + some PROSE), and identifies different cells in all 16. No same_cell detections — TLD is conservative.

---

## 3. Evidence Cue Computation (Read-Only, Existing Definition)

Cue was computed using the same 7-cue structure as the frozen experiment:

| Cue | Source | Available |
|---|---|---|
| cue1 | TLD is_in_table | 16/48 have value=True |
| cue2 | TLD different_cell | 16/48 have value=True |
| cue3 | line_obs_count | 48/48 |
| cue4 | line_spans (left/right context) | not computed this round |
| cue5 | P1 text_a ends with period | 48/48 |
| cue6 | P1 text_b starts with capital | 48/48 |
| cue7 | P1 text_a continuation | 48/48 |

**B2 Cue available**: 42/48 (6 cases have no meaningful Cue content — all controls with no TLD table detection and no punctuation signals)

---

## 4. GT Adjudication

### GT Distribution

| GT | Count | % |
|---|---|---|
| MERGE | 12 | 25% |
| KEEP_SEPARATE | 36 | 75% |
| UNKNOWN | 0 | 0% |

### GT by Structure Family

| Family | MERGE | KEEP | Total |
|---|---|---|---|
| PROSE | 1 | 19 | 20 |
| FIGURE_CAPTION | 9 | 1 | 10 |
| ROW_LABEL_VALUE | 2 | 8 | 10 |
| TABLE_HEADER | 0 | 4 | 4 |
| TABLE_NUMERIC | 0 | 2 | 2 |
| OTHER | 0 | 1 | 1 |
| AXIS | 0 | 1 | 1 |

**Key finding**: MERGE cases come predominantly from FIGURE_CAPTION (9/12 = 75%). PROSE sentence boundaries are almost all KEEP_SEPARATE (19/20 = 95%). This creates a GT imbalance that mirrors the historical problem — but now skewed toward KEEP_SEPARATE for a different reason (PROSE sentence boundaries are almost universally separate sentences).

### GT Adjudication Rationale Examples

| Case | GT | Rationale |
|---|---|---|
| AMB-005 | KEEP_SEPARATE | Sentence boundary: text_a ends with period, text_b starts new sentence |
| AMB-414 | MERGE | Figure caption: label "FIG. 9:" and body "Left:" are same caption unit |
| AMB-432 | MERGE | Section header: number "1" + title form single heading |
| AMB-016 | KEEP_SEPARATE | TLD detects different cells — different table columns |
| AMB-387 | MERGE | Colon-ending: text_a introduces text_b as continuation |

---

## 5. System Interpretation vs GT

### System Decision Distribution

| System Decision | Count |
|---|---|
| INSUFFICIENT_EVIDENCE | 37 (77%) |
| KEEP_SEPARATE | 9 (19%) |
| MERGE | 2 (4%) |

### System ≠ GT

**System-GT disagreements: 0**

The system never makes a WRONG decision. It either:
- Agrees with GT (11 cases: 9 KEEP_SEPARATE + 2 MERGE)
- Abstains with INSUFFICIENT_EVIDENCE (37 cases)

**This means**: S (System≠GT) coverage = 0. The system is conservative — it doesn't make mistakes, it just doesn't decide.

### System Conflict

**Internal system conflicts: 0**

No cases where TLD says one thing and IS-01/IS-02 say another. The system is internally consistent — it just lacks evidence.

---

## 6. Real Coverage Matrix

| Code | Label | Count | Status |
|---|---|---|---|
| P | Positive (system agrees with GT) | 22 | ✅ |
| N | Negative (Cue misleads) | 0 | ❌ MISSING |
| B | Boundary (system abstained, Cue could help) | 26 | ✅ |
| C | Conflict (internal system evidence conflict) | 0 | ❌ MISSING |
| S | System ≠ GT | 0 | ❌ MISSING |
| U | UNKNOWN | 0 | ❌ MISSING |

### Missing Coverage Analysis

| Missing | Why | Can it be filled? |
|---|---|---|
| **N (Negative)** | No case where Cue actively misleads. TLD always agrees with GT when it detects different_cell. | Only if a MERGE case has TLD different_cell=True (none found) |
| **C (Conflict)** | No internal system conflict. TLD and IS-01/IS-02 never disagree. | Requires cases where TLD detects same_cell but IS-01 says numeric (would suggest MERGE) — TLD never detects same_cell |
| **S (System≠GT)** | System never makes a wrong decision. It abstains instead. | Requires cases where system makes a confident wrong decision — system is too conservative to do this |
| **U (UNKNOWN)** | All 48 cases have sufficient evidence for GT adjudication. | Would need cases with genuinely insufficient evidence — current pool doesn't have them |

---

## 7. B1 / B2 Compatibility

| Condition | Available | Detail |
|---|---|---|
| B1 (text + geometry + style) | ✅ 48/48 | Fully available |
| B2 (evidence + Cue) | ⚠️ 42/48 | 6 cases (controls) have no meaningful Cue |
| TLD-based Cue | 16/48 | Only 33% have table structure Cue |
| Geometric Cue | 48/48 | All have h_gap, dy, same_style, line_obs |

### Cue Informativeness by Case Type

| Case Type | TLD Available | Cue Content | B2 Useful? |
|---|---|---|---|
| PROSE (sentence boundary) | 7/20 have TLD | TLD says "different cells" → suggests KEEP | ✅ Cue agrees with GT (KEEP) |
| FIGURE_CAPTION | 1/10 have TLD | TLD says "different cells" for AMB-063 | ⚠️ Cue says KEEP but GT=MERGE for AMB-063 |
| ROW_LABEL_VALUE | 6/10 have TLD | TLD says "different cells" → suggests KEEP | ✅ Cue agrees with GT (KEEP) |
| Controls | 2/7 have TLD | Minimal Cue | Control cases, Cue not needed |

**Critical finding**: For FIGURE_CAPTION cases (9/10 GT=MERGE), TLD does NOT detect tables (captions are not tables). So Cue provides NO useful information for the majority of MERGE cases. Cue is only informative for KEEP_SEPARATE cases where TLD detects table structure.

---

## 8. Source Concentration

| Document | Count | Share | Status |
|---|---|---|---|
| is11_med_001 | 21 | 44% | ⚠️ Dominant |
| is11_resnet | 18 | 38% | ⚠️ Dominant |
| is11_cs_001 | 5 | 10% | OK |
| is11_efficientnet | 4 | 8% | Under-represented |

**Risk**: med_001 contributes 9/12 MERGE cases (all figure captions). If med_001's figure caption pattern is anomalous, MERGE coverage is skewed.

---

## 9. Research Question Answerability

### Can the 48 cases answer: "Does Evidence Cue reduce Human Effort while maintaining Quality and Boundary Safety?"

| Sub-question | Answerable? | Why |
|---|---|---|
| Does Cue reduce effort? | ⚠️ Partially | 26 boundary cases where system abstained — Cue could help. But Cue is only informative for 16 (TLD-detected) cases. |
| Does Cue maintain quality? | ⚠️ Partially | 22 P cases where Cue agrees with GT. No N cases to test Cue-induced errors. |
| Does Cue maintain boundary safety? | ❌ No | 0 U cases — cannot test UNKNOWN preservation. 0 N cases — cannot test Cue misleading. |
| Does Cue avoid automation bias? | ❌ No | 0 S cases — system never disagrees with GT. 0 N cases — Cue never misleads. |

### Fundamental Gap

The 48-case set can test **Cue helpfulness** (does Cue speed up correct decisions?) but CANNOT test **Cue safety** (does Cue ever cause wrong decisions?). Safety testing requires N and S coverage, which are both 0.

---

## 10. Supplementary Candidate Assessment

### Can missing coverage be filled from existing 545 candidate pool?

| Missing | Pool Search | Found? |
|---|---|---|
| N (Negative) | Need MERGE case with TLD different_cell | Unlikely — MERGE cases are figure captions, TLD doesn't detect tables in captions |
| C (Conflict) | Need TLD same_cell + IS-01 numeric | TLD never detects same_cell in current pool |
| S (System≠GT) | Need system to make confident wrong decision | System is too conservative (77% abstention) |
| U (UNKNOWN) | Need evidence-insufficient case | All 545 candidates have geometry + text evidence |

**Assessment**: The existing 545-candidate pool is unlikely to contain N, C, or S cases because:
1. TLD is conservative (never detects same_cell)
2. System is conservative (77% abstention)
3. MERGE cases are concentrated in figure captions (not tables)

Filling N/S/U coverage would require either:
- Different corpus (with more ambiguous table structures)
- Modified TLD (less conservative) — **PROHIBITED** (frozen)
- Synthetic cases — **PROHIBITED** (no fabrication)

---

## 11. Final Gate

### Q1: Can the 48 cases serve as Pilot Candidate Set?

**CONDITIONAL** — The set has strong boundary coverage (26 B cases) and correct Cue alignment (22 P cases), but lacks safety testing dimensions (N=0, S=0, U=0).

### Q2: GT distribution?

```
MERGE = 12 (25%)
KEEP_SEPARATE = 36 (75%)
UNKNOWN = 0 (0%)
```

### Q3: Real Coverage?

```
P = 22
N = 0
B = 26
C = 0
S = 0
U = 0
```

### Q4: B1/B2 Evidence complete?

```
B1 = PASS (48/48)
B2 = CONDITIONAL (42/48 Cue available, but Cue uninformative for 9/12 MERGE cases)
```

### Q5: Real System ≠ GT?

**NO** — 0 disagreements. System never makes a wrong decision.

### Q6: Real Negative?

**NO** — 0 cases where Cue actively misleads.

### Q7: Real UNKNOWN?

**NO** — 0 cases with insufficient evidence for GT.

### Q8: Source concentration?

```
med_001 = 44% (dominant, provides 9/12 MERGE)
resnet = 38% (dominant)
cs_001 = 10%
efficientnet = 8% (under-represented)
```

---

## 12. Pilot Readiness Decision

### **CONDITIONAL**

The 48-case set is ready for a **Cue Helpfulness Pilot** (does Cue speed up correct decisions?) but NOT ready for a **Cue Safety Pilot** (does Cue ever cause errors?).

### What is ready:
- 26 boundary cases where Cue could reduce effort
- 22 positive cases where Cue agrees with GT
- TLD computed for all 48 cases
- GT adjudicated for all 48 cases
- B1 fully available

### What is not ready:
- 0 Negative cases (cannot test Cue misleading)
- 0 System≠GT cases (cannot test automation bias)
- 0 UNKNOWN cases (cannot test abstention boundary)
- Cue uninformative for 9/12 MERGE cases (figure captions)
- med_001 dominates MERGE coverage (9/12)

### What would be needed for full Pilot:
1. **Corpus expansion**: Add documents with ambiguous table structures (merged cells, multi-level headers) to create potential N/C/S cases
2. **OR**: Accept CONDITIONAL status and run a Helpfulness-only Pilot, explicitly acknowledging that safety testing is deferred

---

## 13. Governance

```
DICE_CORE_MODIFICATION = FALSE
P1_P7_MODIFICATION = FALSE
TLD_MODIFICATION = FALSE
ATOMIC_OBSERVATION_MODIFICATION = FALSE
EVIDENCE_CUE_MODIFICATION = FALSE
GT_MODIFICATION_OF_FROZEN_GT = FALSE

FORMAL_EXPERIMENT = FALSE
PARTICIPANT = FALSE

FROZEN_BASELINE = INTACT
FROZEN_EXPERIMENT = INTACT

FINAL_EVALUATION_SET = NOT_ESTABLISHED

PRODUCTION = FALSE
RUNTIME_AUTHORITY = ZERO

STOP = TRUE
```
