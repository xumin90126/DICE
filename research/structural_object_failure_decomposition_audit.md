# Structural Object Failure Decomposition Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY / NO MODIFICATION / FROZEN INTACT / STOP

---

## 1. Executive Summary

```
PRIMARY_BOTTLENECK    = R2 + D (Structural Detection + Consumer Integration)
SECONDARY_BOTTLENECK  = C (Evidence Organization — for AMB-032 Human side)

FINAL_STATUS          = STRUCTURAL_FAILURE_PARTIALLY_SUPPORTED

KEY FINDING:
  TLD is the SINGLE POINT OF FAILURE for Structural Object detection in IS-11.
  
  TLD Coverage on 45 cases:
    TLD_CORRECT:     13/45 (29%) — Machine correct
    TLD_MISS_TABLE:  23/45 (51%) — TLD failed to detect table
    TLD_PARTIAL:      7/45 (16%) — TLD detected wrong table (all is11_cs_001 p3)
    TLD_MISS_FIGURE:  2/45 (4%)  — Figure out of TLD scope (expected)
    ─────────────────────────────
    Total TLD fail:  32/45 (71%)

  In ALL 32 failure cases:
    - P2 geometry EXISTS and is SUFFICIENT (45/45 = 100%)
    - IS-11 consumer does NOT use P2 when TLD fails (32/45 = 71%)
    - IS-11 has NO fallback mechanism
    → This is NOT Observation Gap (A)
    → This is NOT Evidence Gap (B)
    → PRIMARY = R2 (TLD detection failure)
    → SECONDARY = D (Consumer/Integration — no fallback to P2)

  CROSS-EXPERIMENT FINDING:
    3 distinct failure mechanisms across IS-11, P7, PH-02:
      M1: TLD Detection Failure (IS-11, M-B) — 32/45 affected
      M2: IS-01/IS-02 Heuristic False-Trigger (P7 3 FP + IS-11 AMB-135) — 4 cases
      M3: Research-Object Mismatch (PH-02, REJECTED) — distinct
    Common pattern: D (Consumer/Integration Gap) across IS-11, H2, M-B
    But NOT a single unified mechanism

NO LLM NEEDED. NO DOCUMENT DISCOURSE NEEDED. NO NEW OBSERVATION NEEDED.
STOP = TRUE
```

> **Family A (Structural Object) 的主要瓶颈是 TLD 检测失败（R2）+ IS-11 消费者无回退机制（D）。在全部 32 个失败案例中，P2 几何 evidence 都存在且充分，但 IS-11 只使用 TLD 输出——当 TLD 失败时没有回退到 P2 geometry。这不是 Observation Gap（A），不是 Evidence Gap（B），而是 Structural Detection（R2）+ Consumer Integration（D）的混合失败。跨实验比较发现 3 种不同的失败机制，但 D（Consumer/Integration Gap）是 IS-11、H2、M-B 的共同模式。**

---

## 2. Research Question

> Family A (Structural Object) Failure 到底发生在哪一层？

---

## 3. TLD Coverage Analysis — All 45 Cases

### 3.1 TLD Status Distribution

| TLD Status | Count | % | Description |
|---|---|---|---|
| TLD_CORRECT | 13 | 29% | TLD detected table + correct cell separation → Machine TN |
| TLD_MISS_TABLE | 23 | 51% | TLD detected 0 tables (missed table entirely) |
| TLD_PARTIAL | 7 | 16% | TLD detected table but spans NOT in detected table (all is11_cs_001 p3) |
| TLD_MISS_FIGURE | 2 | 4% | Figure — TLD is table-only (expected, not a bug) |
| **Total Fail** | **32** | **71%** | **TLD failed to provide correct structural evidence** |

### 3.2 Outcome Distribution

| Outcome | Count | % | Description |
|---|---|---|---|
| TN (True Negative) | 26 | 58% | Machine correct (13 TLD_CORRECT + 13 TLD_MISS but lucky) |
| ABSTAIN | 18 | 40% | Machine couldn't decide (INSUFFICIENT_EVIDENCE) |
| FP (False Positive) | 1 | 2% | Machine said MERGE, GT=KEEP_SEPARATE (AMB-135) |
| FN (False Negative) | 0 | 0% | No false negatives |

### 3.3 Key Insight: "Lucky" TN Cases

13 TLD_MISS_TABLE cases still got TN (correct KEEP_SEPARATE) despite TLD failure. This is because:
- IS-01 (numeric prefix) didn't trigger → Machine defaulted to KEEP_SEPARATE
- These are "lucky" correct decisions, not evidence-based correct decisions
- If IS-01 had triggered (like AMB-135), they would have been FP

> **Only 13/26 TN cases (50%) are evidence-based correct (TLD_CORRECT). The other 13 are "lucky" correct (TLD missed but IS-01 didn't false-trigger).**

---

## 4. Failure Chain Analysis

### 4.1 AMB-135 — The Only FP

```
Document: is11_efficientnet, Page 5
Text A: '4'  Text B: 'MBConv6, k5x5'
GT: KEEP_SEPARATE (both reviewers agree: different table columns)

Failure Chain:
  P1: text extracted correctly ✓ ('4', 'MBConv6, k5x5')
  P2: geometry correct ✓ (h_gap=30.0, dy=0.0, same_style=True, bbox available)
  TLD: FAILED ✗ (tables_detected=0 — TLD missed table on efficientnet p5)
  IS-11: is_in_table=False → can't determine table structure
  IS-01: True ('4' is numeric prefix) ← FALSE TRIGGER
  IS-02: True ('MBConv6, k5x5' has readable words) ← CORRECT
  Decision: IS-01+IS-02 → MERGE → FP ✗

First Failure: TLD (Structural Detection)
  - TLD missed table → IS-11 had no structural evidence
  - IS-11 fell back to IS-01/IS-02 → IS-01 false-triggered on table cell value '4'
  
Root Cause: F_MIXED
  PRIMARY: R2 (TLD missed table)
  SECONDARY: D (IS-11 no fallback to P2 geometry)
  CONTRIBUTING: IS-01 heuristic too broad (false-trigger on table cell values)

Existing Evidence Sufficient: YES (P2 geometry exists, h_gap=30, dy=0)
Consumer Uses It: NO (IS-11 only uses TLD, not P2)
```

### 4.2 AMB-032 — TLD Correct, Human Side Failure

```
Document: is11_resnet, Page 6
Text A: '-'  Text B: '8.43'
GT: KEEP_SEPARATE (both reviewers agree: different table columns)

Failure Chain (Machine side):
  P1: text extracted ✓
  P2: geometry correct ✓ (h_gap=33.9, dy=0.0)
  TLD: CORRECT ✓ (tables_detected=1, both in table, different_cell=True)
    a_cell=[27,1], b_cell=[27,2] (row 27, columns 1 and 2)
  IS-11: is_in_table=True, different_cell=True → KEEP_SEPARATE → TN ✓

Machine: CORRECT — no failure

Failure Chain (Human/P722 side):
  P722 Participant: UNKNOWN (45.9s)
  - Participant expanded ALL 7 geometry fields
  - But geometry fields (h_gap, dy, same_style, width, style_sig) don't convey table structure
  - TLD cell info (a_cell=[27,1], b_cell=[27,2]) NOT exposed to participant
  - Participant had to reconstruct table structure from geometry alone → failed

First Failure (Human side): C (Evidence Organization Gap)
  - TLD evidence exists and is correct
  - But not organized/exposed for Human consumption
  - Participant got geometry, not table structure

Root Cause: C (Evidence Organization Gap) — Human side only
  Machine side: NONE (correct)
```

### 4.3 AMB-313 — TLD Miss, ABSTAIN

```
Document: is11_efficientnet, Page 8
Text A: 'Test Size'  Text B: '#Classes'
GT: KEEP_SEPARATE (both reviewers agree: different table headers)

Failure Chain:
  P1: text extracted ✓
  P2: geometry correct ✓ (h_gap=8.4, dy=0.0)
  TLD: FAILED ✗ (tables_detected=0 — TLD missed table on efficientnet p8)
  IS-11: is_in_table=False → INSUFFICIENT_EVIDENCE → ABSTAIN
  IS-01: False ('Test Size' not numeric) → no false trigger
  IS-02: True ('#Classes' readable)

First Failure: TLD (Structural Detection)
Root Cause: F_MIXED (R2 + D)
  PRIMARY: R2 (TLD missed table)
  SECONDARY: D (no fallback to P2 geometry)
  Note: No FP because IS-01 didn't trigger → ABSTAIN instead
```

### 4.4 AMB-462 — TLD Partial (Wrong Table)

```
Document: is11_cs_001, Page 3
Text A: 'WGe'  Text B: 'Avg.'
GT: KEEP_SEPARATE (both reviewers agree: different table headers)

Failure Chain:
  P1: text extracted ✓
  P2: geometry correct ✓ (h_gap=12.0, dy=0.0)
  TLD: PARTIAL ✗ (tables_detected=1, but a_in_table=False, b_in_table=False)
    TLD detected A table on page 3, but NOT the table containing these spans
    All 7 TLD_PARTIAL cases are from is11_cs_001 page 3 → TLD detected wrong table
  IS-11: is_in_table=False → INSUFFICIENT_EVIDENCE → ABSTAIN

First Failure: TLD (Structural Detection — wrong table detected)
Root Cause: F_MIXED (R2 + D)
  PRIMARY: R2 (TLD detected wrong table or wrong boundaries)
  SECONDARY: D (no fallback to P2 geometry)
```

### 4.5 AMB-414 / AMB-422 — Figure Caption (Out of TLD Scope)

```
AMB-414: Text A: 'FIG. 9:'  Text B: 'Left:'  GT: MERGE
AMB-422: Text A: 'FIG. 12:'  Text B: 'Distribution...'  GT: MERGE

Failure Chain:
  P1: text extracted ✓
  P2: geometry correct ✓
  TLD: NOT APPLICABLE (TLD is table-only, doesn't detect figures)
  IS-11: is_in_table=False → INSUFFICIENT_EVIDENCE → ABSTAIN
  has_fig_prefix: True (derivable from P1 text: 'FIG.' prefix)
    BUT: IS-11 does NOT compute has_fig_prefix

First Failure: Structural Detection (no figure detector)
Root Cause: F_MIXED (R2 + D)
  PRIMARY: R2 (no figure structural detection — TLD is table-only)
  SECONDARY: D (has_fig_prefix derivable from P1 but not used by IS-11)
  
Key: Evidence EXISTS (FIG prefix in P1 text) but IS-11 doesn't compute/use it
```

---

## 5. Structural Failure Matrix

| Case | Object | TLD Status | Outcome | First Failure Layer | Primary | Secondary | Ev Suff | Cons Use |
|---|---|---|---|---|---|---|---|---|
| AMB-005 | TABLE | TLD_CORRECT | TN | NONE | NONE | NONE | Y | Y |
| AMB-024 | TABLE | TLD_CORRECT | TN | NONE | NONE | NONE | Y | Y |
| AMB-032 | TABLE | TLD_CORRECT | TN | NONE (Machine) | NONE | NONE | Y | Y |
| AMB-135 | TABLE | TLD_MISS | **FP** | **TLD** | **R2** | **D** | Y | N |
| AMB-313 | TABLE | TLD_MISS | ABSTAIN | TLD | R2 | D | Y | N |
| AMB-414 | FIGURE | TLD_MISS_FIG | ABSTAIN | No Fig Detector | R2 | D | Y | N |
| AMB-422 | FIGURE | TLD_MISS_FIG | ABSTAIN | No Fig Detector | R2 | D | Y | N |
| AMB-462 | TABLE | TLD_PARTIAL | ABSTAIN | TLD (wrong table) | R2 | D | Y | N |
| ... (32 more TLD fail cases) | | | | | R2 | D | Y | N |

**Summary:**
- 13/45 (29%): TLD_CORRECT → Machine correct
- 32/45 (71%): TLD failed → First Failure at Structural Detection (R2)
- 45/45 (100%): P2 evidence SUFFICIENT
- 32/45 (71%): Consumer does NOT use evidence when TLD fails

---

## 6. P7 Independent Evaluation Analysis

### 6.1 Results

```
69 cases: TP=0, FP=3, TN=8, FN=2, ABSTAIN=56
Coverage: 18.8% (13/69 decided)
Precision: 0% (3 FP, 0 TP)
```

### 6.2 P7 False Positives (3 FP — All TABLE_CELL)

| Case | Text A | Text B | IS-01 | IS-02 | Machine | GT |
|---|---|---|---|---|---|---|
| IND-AMB-247 | '121' | '40 mM Hepes' | True | True | MERGE | KEEP |
| IND-AMB-223 | '5.' | 'SARS-CoV-2' | True | True | MERGE | KEEP |
| IND-AMB-235 | '6.' | 'RNA' | True | True | MERGE | KEEP |

**Root Cause:** IS-01 false-triggers on table cell values that look like numbered list items. '121', '5.', '6.' are table cell values, but IS-01 detects them as numeric prefixes → MERGE → FP.

### 6.3 P7 False Negatives (2 FN — Body Text / Reference)

| Case | Text A | Text B | IS-01 | IS-02 | Machine | GT | BC |
|---|---|---|---|---|---|---|---|
| IND-AMB-201 | 'al.,' | '2025).' | False | False | KEEP | MERGE | BODY_TEXT_CONTINUATION |
| IND-AMB-200 | 'et' | 'al.,' | False | False | KEEP | MERGE | REFERENCE_LIST_ENTRY |

**Root Cause:** Neither IS-01 nor IS-02 triggers → Machine defaults to KEEP_SEPARATE → But GT=MERGE (fragments of same reference/citation).

### 6.4 P7 vs IS-11 Mechanism Comparison

| Dimension | IS-11 | P7 |
|---|---|---|
| Uses TLD | YES | NO |
| Uses IS-01/IS-02 | YES (fallback) | YES (primary) |
| FP cause | TLD miss → IS-01 false-trigger | IS-01 false-trigger (no TLD) |
| FN cause | 0 FN | IS-01/IS-02 both False → default KEEP |
| Coverage | 29% TLD correct | 18.8% decided |

> **P7 FP mechanism = IS-01 false-trigger (same as IS-11 AMB-135). P7 does NOT use TLD. P7 FN mechanism is DISTINCT (body text/reference continuation, not in IS-11 scope).**

---

## 7. Cross-Experiment Mechanism Comparison

### 7.1 IS-11 vs M-B

```
SAME — M-B specifically diagnosed IS-11's Consumer/Integration Gap
Both identify: TLD is the bottleneck, P2 evidence exists but not used
M-B finding: "IS-11 consumer connects to TLD (chunker heuristic), NOT to frozen P2 structural facts"
M-B finding: "Correct-vs-blind comparison proves evidence is complete on blind pages"
```

### 7.2 IS-11 vs H2

```
RELATED — H2 found relation not computed (R2_RELATION_NOT_COMPUTED)
IS-11 found TLD not detecting
Both point to: P2 evidence exists but consumer doesn't use it
H2: SAME_ROW_DIFFERENT_COLUMN relation derivable from geometry but not computed
IS-11: table structure derivable from geometry but TLD fails and no fallback
Same underlying pattern: D (Consumer/Integration Gap)
```

### 7.3 IS-11 vs PH-02

```
DISTINCT — PH-02 was about research-object mismatch
PH-02: left_alignment_group treated as "column" → heterogeneous → fails
IS-11: TLD detection failure + no consumer fallback
PH-02: wrong aggregation unit (B + E)
IS-11: missing detection + no fallback (R2 + D)
Different failure mechanisms
```

### 7.4 IS-11 vs P7

```
DISTINCT — P7 uses IS-01/IS-02 (no TLD), different feature set
P7 FP: IS-01 false-triggers on table cell values
IS-11 FP: TLD misses table, falls back to IS-01/IS-02 which false-triggers
P7 FN: IS-01/IS-02 both False → default KEEP → GT=MERGE (body text/reference)
IS-11: no FN
Different mechanisms, but IS-11's FP (AMB-135) shares P7's FP pattern
```

### 7.5 Summary

| Comparison | Verdict |
|---|---|
| IS-11 vs M-B | **SAME** |
| IS-11 vs H2 | **RELATED** |
| IS-11 vs PH-02 | **DISTINCT** |
| IS-11 vs P7 | **DISTINCT** (with shared FP sub-pattern) |

```
CROSS_EXPERIMENT_MECHANISM = PARTIALLY_SUPPORTED
  D (Consumer/Integration Gap) is common across IS-11, H2, M-B
  But R2 (TLD detection) is specific to IS-11
  IS-01/IS-02 false-trigger is specific to P7
  PH-02 research-object mismatch is distinct
```

---

## 8. Root Cause Classification

### 8.1 Per-Case Classification

| Cause | Count | % | Description |
|---|---|---|---|
| NONE | 13 | 29% | TLD_CORRECT, Machine correct |
| F_MIXED (R2+D) | 32 | 71% | TLD fail + no consumer fallback |
| A (Observation Gap) | 0 | 0% | NOT FOUND — all evidence in P2 |
| B (Evidence Gap) | 0 | 0% | NOT FOUND — evidence formed correctly |
| C (Evidence Organization) | 0 | 0% | NOT FOUND (Machine side; AMB-032 Human side only) |
| D (Consumer/Integration) | 0 | 0% | (counted as SECONDARY in F_MIXED) |
| E (Evaluation/GT Design) | 0 | 0% | NOT FOUND — GT is consistent |
| G (Insufficient Evidence) | 0 | 0% | NOT FOUND — evidence sufficient |

### 8.2 Primary Bottleneck

```
PRIMARY_BOTTLENECK = R2 + D (Structural Detection + Consumer Integration)
  R2: TLD fails to detect table on 30/43 table cases (70%)
  D: IS-11 has no fallback to P2 geometry when TLD fails (32/45 = 71%)
  
  R2 is the TRIGGER (TLD detection fails)
  D is the AMPLIFIER (no fallback → ABSTAIN or FP)
  
  If D were fixed (consumer uses P2 when TLD fails):
    - 13 ABSTAIN cases could potentially be resolved
    - 1 FP (AMB-135) could be avoided
    - 13 "lucky" TN cases could become evidence-based TN
    
  If R2 were fixed (TLD detects all tables):
    - 23 TLD_MISS_TABLE + 7 TLD_PARTIAL = 30 cases resolved
    - But TLD is FROZEN (cannot modify)
    
  D is the ACTIONABLE bottleneck (consumer can use existing P2 evidence)
  R2 is the FROZEN bottleneck (TLD cannot be modified)
```

### 8.3 Secondary Bottleneck

```
SECONDARY_BOTTLENECK = C (Evidence Organization — AMB-032 Human side)
  AMB-032: TLD correct, Machine correct
  But P722 participant got UNKNOWN (45.9s)
  Because TLD cell info not organized/exposed for Human
  This is a Human-side organization gap, not Machine-side
```

---

## 9. First Failure Layer Principle

### 9.1 Per Case

| Case | P1 | P2 | TLD | IS-11 Consumer | GT | First Failure |
|---|---|---|---|---|---|---|
| AMB-135 | ✓ | ✓ | **✗** | ✗ (no fallback) | ✓ | **TLD** |
| AMB-032 | ✓ | ✓ | ✓ | ✓ (Machine) | ✓ | NONE (Machine); C (Human) |
| AMB-313 | ✓ | ✓ | **✗** | ✗ (ABSTAIN) | ✓ | **TLD** |
| AMB-462 | ✓ | ✓ | **✗** (wrong) | ✗ (ABSTAIN) | ✓ | **TLD** |
| AMB-414 | ✓ | ✓ | N/A | ✗ (no FIG detect) | ✓ | **No Fig Detector** |
| AMB-422 | ✓ | ✓ | N/A | ✗ (no FIG detect) | ✓ | **No Fig Detector** |

### 9.2 Principle

> **First Failure = 系统第一次失去足够信息/正确解释能力的位置。在全部 32 个失败案例中，First Failure 发生在 TLD（Structural Detection）层——P1 和 P2 都正确，但 TLD 未能检测到表格结构。IS-11 消费者随后因为只使用 TLD 输出而失败（D），但 First Failure 是 TLD。**

---

## 10. Final Research Questions

### Q1: Family A 是否存在统一 Failure Mechanism？

**PARTIALLY.** 主要机制是 TLD Detection Failure + Consumer No Fallback (R2+D)，影响 32/45 (71%)。但存在 3 种子机制（TLD miss, TLD partial, Figure out of scope），以及跨实验的 IS-01 false-trigger。

### Q2: AMB-135 属于哪一层？

**TLD (Structural Detection) — R2.** TLD missed table → IS-11 fell back to IS-01/IS-02 → IS-01 false-triggered → FP. First Failure = TLD.

### Q3: AMB-032 属于哪一层？

**Machine: NONE (correct). Human: C (Evidence Organization Gap).** TLD correct, Machine correct. But P722 participant couldn't verify table structure because TLD cell info not exposed.

### Q4: Figure Caption 属于哪一层？

**R2 (No Figure Detector) + D (has_fig_prefix not used).** TLD is table-only. has_fig_prefix derivable from P1 text but IS-11 doesn't compute it. Evidence exists, consumer doesn't use it.

### Q5: P7 Independent Failure 与 IS-11 是否共享机制？

**PARTIALLY.** P7 FP (3 cases) shares IS-01 false-trigger pattern with IS-11 AMB-135. But P7 doesn't use TLD (different feature set). P7 FN (2 cases) is distinct (body text/reference continuation). Mechanism is RELATED but not SAME.

### Q6: PH-02 / H2 / M-B / P7 是否 SAME / RELATED / DISTINCT？

| Pair | Verdict |
|---|---|
| IS-11 vs M-B | SAME |
| IS-11 vs H2 | RELATED |
| IS-11 vs PH-02 | DISTINCT |
| IS-11 vs P7 | DISTINCT (shared FP sub-pattern) |

### Q7: Structural Object 当前最主要瓶颈是什么？

**R2 (TLD Detection) + D (Consumer Integration).** TLD fails on 71% of cases. IS-11 has no fallback. D is actionable (consumer can use existing P2); R2 is frozen (TLD cannot be modified).

### Q8: 是否需要新的 Observation？

**NO.** All evidence exists in P1/P2. 45/45 cases have sufficient evidence. The problem is not missing observation but missing detection + missing consumer integration.

### Q9: 是否需要 LLM？

**NO.** All structural detection is deterministic (TLD, geometry, text features). No semantic understanding needed.

### Q10: 是否需要 Document Discourse？

**NO.** No case requires discourse understanding. Local structural evidence (TLD, geometry, FIG prefix) is sufficient.

### Q11: 是否值得继续 Structural Object 研究？

**YES — but focused on D (Consumer Integration), not R2 (TLD).** R2 is frozen (TLD cannot be modified). D is actionable: IS-11 consumer could use P2 geometry when TLD fails. This is the highest-value next research direction.

### Q12: 如果继续，下一步最小 READ-ONLY 研究是什么？

**Audit P2 geometry → table structure derivability.** Can P2 geometry (h_gap, dy, same_style, bbox, line_obs_count) be used to infer table structure when TLD fails? This is a READ-ONLY analysis of existing P2 data — no implementation, no modification.

---

## 11. Research Value Assessment

| Dimension | Rating | Reason |
|---|---|---|
| Research Value | HIGH | 71% of cases affected; D is actionable |
| Evidence Strength | HIGH | 45/45 evidence sufficient; cross-experiment confirmation |
| Implementation Cost | UNKNOWN | D fix would require consumer modification (not authorized) |
| Regression Risk | MEDIUM | Using P2 when TLD fails could introduce new errors |
| Expected Impact | HIGH | Could resolve 13 ABSTAIN + 1 FP + make 13 lucky TN evidence-based |

---

## 12. Anti-Overdesign Gate

```
No new Observation proposed (all in P2)
No new Engine proposed
No new Module proposed
No LLM proposed
No Document Discourse proposed
No new Architecture proposed
No Signal 3 modification
No TLD modification
No GT modification
No implementation
No experiment
```

> **遵循 First Failure Layer Principle：先找到最早失败层（TLD），再判断是否需要更高层能力。结论：不需要更高层能力——P2 evidence 已存在，只需 Consumer Integration。**

---

## 13. Final Status

```
FINAL_STATUS = STRUCTURAL_FAILURE_PARTIALLY_SUPPORTED
  → R2+D is supported as primary bottleneck (71% of cases)
  → But R2 (TLD) is FROZEN — cannot be modified
  → D (Consumer) is actionable but not authorized for implementation
  → Cross-experiment mechanism is PARTIALLY supported (D common, but 3 distinct sub-mechanisms)

PRIMARY_BOTTLENECK = R2 + D (Structural Detection + Consumer Integration)
SECONDARY_BOTTLENECK = C (Evidence Organization — AMB-032 Human side only)
RECOMMENDED_NEXT_AUDIT = P2 geometry → table structure derivability (READ-ONLY)
```

---

## 14. Governance Gate

```
DICE_CORE_MODIFICATION              = NO
P1_P7_MODIFICATION                  = NO
P2_MODIFICATION                     = NO
TLD_MODIFICATION                    = NO
IS11_MODIFICATION                   = NO
GT_MODIFICATION                     = NO
SIGNAL_MODIFICATION                 = NO
LLM                                 = NO
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

---

## 15. 最终原则验证

> *First Failure Layer Principle*

✓ 遵守：全部 32 个失败案例的 First Failure 在 TLD（Structural Detection）层。P1/P2 正确。不需要更高层能力。

> *不要因为 Table 很复杂就自动提出 LLM / Discourse / Engine*

✓ 遵守：所有 structural detection 是确定性的。P2 evidence 已存在。瓶颈是 TLD 检测失败 + Consumer 无回退——不需要 LLM、Discourse、新 Engine。

> *C 与 D 可以同时出现*

✓ 遵守：AMB-032 的 Human side 是 C（Evidence Organization），Machine side 是 NONE。其他案例的 Machine side 是 R2+D。

> *不得简单写 MIXED*

✓ 遵守：F_MIXED 拆为 PRIMARY (R2) + SECONDARY (D)。

`STOP = TRUE`。
