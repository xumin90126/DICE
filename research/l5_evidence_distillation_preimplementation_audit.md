# Pre-Implementation Experimental Integrity Audit

## L5 Evidence Distillation → Human Effort Reduction Experiment

**Date**: 2026-09-12
**Scope**: Audit whether the experiment design has sufficient scientific integrity to enter implementation phase
**Mode**: READ-ONLY / DESIGN AUDIT ONLY
**Governance**: NO CODE, NO UI, NO DATA, NO GT, NO SCHEMA, NO EXPERIMENT EXECUTION

---

## 1. Executive Conclusion

### `CONDITIONAL PASS`

The experiment design has **strong foundational integrity** in:
- ✅ Research question scope (distillation, not learning)
- ✅ Evidence Cue boundary (all 7 cues: Semantic Authority = 0, no judgment leakage)
- ✅ Provenance (all cues traceable to frozen evidence, deterministic)
- ✅ Cognitive work decomposition (compressible vs non-compressible correctly identified)
- ✅ Learning effect control (matched-pairs + counterbalancing)

But has **3 blocking issues** that must be corrected before implementation:

1. **ATTRIBUTION CONFOUND** (HIGH): Current B = (A - 7 fields) + 4 cues. This confounds field deletion with cue addition. Cannot attribute time reduction to distillation vs deletion.

2. **AUTOMATION BIAS MEASUREMENT INVALID** (HIGH): Uses arbitrary "Override ≥ 50% = SAFE" threshold. No Wrong-Cue Acceptance Rate. Only 2 true cue-GT conflict cases (insufficient). 0 System≠GT cases.

3. **CASE CORPUS INCOMPLETE** (HIGH): 0 N-type cases, 0 System≠GT cases, 0 UNKNOWN baseline. Cannot test cue on confusing cases, cannot measure automation bias, cannot verify UNKNOWN preservation.

### `IMPLEMENTATION_READY = FALSE`

Until the 3 blocking issues are corrected.

### `IMPLEMENTATION_AUTHORIZED = FALSE` (regardless of readiness)

---

## 2. Information Equivalence Audit

### A → B Complete Mapping Table

| A Field | Class | Decision Relevance | B Representation | Status | Loss Risk | Justification |
|---|---|---|---|---|---|---|
| text_a | H | HIGH | field (kept) | RETAINED | NONE | Core text content |
| text_b | H | HIGH | field (kept) | RETAINED | NONE | Core text content |
| page_image | H | HIGH | field (kept) | RETAINED | NONE | Primary visual evidence |
| A/B_highlight | H | HIGH | field (kept) | RETAINED | NONE | Position markers |
| line_spans | H | HIGH | field (kept) | RETAINED | NONE | Neighbor context |
| line_obs_count | M | MEDIUM | field + Cue 3 | RE-EXPRESSED | NONE | Count distilled into natural language |
| h_gap | M | MEDIUM | Cue 2 (different_cell) | RE-EXPRESSED | LOW | Numeric gap → structural position cue; measures different aspect |
| doc_id | L | LOW | field (kept) | RETAINED | NONE | Context only |
| page_number | L | LOW | field (kept) | RETAINED | NONE | Context only |
| dy | L | LOW | none | LOST | NONE | All same-line (dy=0); no decision value |
| **same_style** | **M** | **MEDIUM** | **none** | **LOST** | **MEDIUM** | **Could support style-based reasoning; n=1 insufficient to prove unused** |
| width_a | L | LOW | none | LOST | NONE | Not referenced by Human |
| width_b | L | LOW | none | LOST | NONE | Not referenced by Human |
| style_sig_a | L | LOW | none | LOST | NONE | Technical string, not human-readable |
| style_sig_b | L | LOW | none | LOST | NONE | Technical string, not human-readable |

### Summary

| Status | Count |
|---|---|
| RETAINED | 7 |
| RE-EXPRESSED | 2 |
| LOST | 6 |

### Class H (Decision-Relevant) Loss Check

```
Class H fields: 5 (text_a, text_b, page_image, A/B_highlight, line_spans)
Class H LOST: 0
→ PASS: No decision-relevant information lost
```

### Class M (Supporting) Loss Check

```
Class M fields: 3 (line_obs_count, h_gap, same_style)
Class M RE-EXPRESSED: 2 (line_obs_count, h_gap)
Class M LOST: 1 (same_style)
→ ISSUE: same_style is Class M with MEDIUM loss risk
→ n=1 (P01) insufficient to prove same_style is universally unused
→ BLOCKING: must keep same_style in B or justify removal with >n=1 evidence
```

### Class L (Low-Value) Loss Check

```
Class L fields: 7
Class L LOST: 5 (dy, width_a, width_b, style_sig_a, style_sig_b)
Class L RETAINED: 2 (doc_id, page_number)
→ PASS: All LOST fields are low-value, provenance preserved in frozen evidence
```

---

## 3. Information Loss Assessment

| Loss Level | Count | Fields |
|---|---|---|
| HIGH | 0 | — |
| MEDIUM | 1 | same_style (Class M, could be decision-relevant for some participants) |
| LOW | 0 | — |
| NONE | 14 | All RETAINED + RE-EXPRESSED fields |

### Information Loss Hard Gate

```
Class H LOST: 0 → PASS
Class M LOST: 1 (same_style) → CONDITIONAL PASS (needs justification or retention)
Class L LOST: 5 → PASS (all low-value, provenance preserved)

OVERALL: CONDITIONAL PASS
  - No HIGH-risk loss
  - 1 MEDIUM-risk loss (same_style) requires correction
```

### Minimal Correction for same_style

**Option A** (recommended): Keep same_style in Condition B as optional/progressive disclosure field.
**Option B**: Add Condition B1 (deletion-only, no cues) to test if same_style removal affects accuracy.

---

## 4. Attribution Risk Audit

### Counterfactual C1: Deletion-Only

> If B only deletes 7 fields (no cues), would time still drop?

**Answer: LIKELY YES.** Removing 7 unused fields reduces visual scan time.

```
ATTRIBUTION_RISK = HIGH
```

Current design B = (A - 7 fields) + 4 cues confounds two changes. Cannot separate:
- Time↓ from less noise (field deletion)
- Time↓ from better distillation (cue addition)

### Counterfactual C2: All Fields + Cues

> If B keeps all 15 fields + adds 4 cues, would cue value show?

**Answer: UNCERTAIN.** Human may use cues to skip field scanning, or may ignore cues and scan all fields.

```
DISTILLATION_ATTRIBUTION = STRONGER (if cue used)
```

### Attribution Factor Assessment

| Factor | Current Control | Risk | Correction |
|---|---|---|---|
| A. Evidence Distillation (cue) | WEAK — confounded with deletion | **HIGH** | 3-condition design OR keep all fields in B |
| B. Information Deletion | NONE — no separate measurement | **HIGH** | Add B1 condition (deletion only) |
| C. UI Presentation | PARTIAL — fewer fields changes scanning | MEDIUM | Control layout between conditions |
| D. Learning Effect | GOOD — matched sets + counterbalancing | LOW | None needed |
| E. Automation Bias | WEAK — arbitrary threshold, insufficient cases | **HIGH** | Redesign measurement + add conflict cases |

### Recommended Correction: 3-Condition Design

```
Condition A:   15 fields + image (baseline)
Condition B1:  8 fields + image (deletion only, no cues)
Condition B2:  8 fields + 4 cues + image (deletion + cues)

Comparisons:
  A vs B1:  effect of field deletion (noise reduction)
  B1 vs B2: effect of cue addition (distillation)
  A vs B2:  combined effect
```

**Cost**: 3 conditions × n≥5 = n≥15 (50% more than current n≥10)

### Alternative: 2-Condition with All Fields

```
Condition A: 15 fields + image
Condition B: 15 fields + 4 cues + image (ALL fields kept + cues)

If B faster: cue provides value beyond existing fields
If B not faster: cue redundant
```

**Cost**: Same as current (n≥10), but tests only cue addition, not deletion.

### Verdict

```
ATTRIBUTION_VALIDITY = FAIL (current 2-condition design)
→ BLOCKING ISSUE #1
→ Must adopt 3-condition design OR 2-condition-with-all-fields design
```

---

## 5. Evidence Cue Boundary Audit

### Per-Cue Semantic Authority

| Cue | Underlying Evidence | Transformation | Semantic Authority | Judgment Leakage |
|---|---|---|---|---|
| Cue 1 (is_in_table) | frozen TLD | boolean → "within multi-column aligned structure" | 0 | PASS |
| Cue 2 (different_cell) | frozen TLD | boolean → "in different structural positions" | 0 | PASS |
| Cue 3 (line_obs_count) | P1 + P2 | integer → "N text items on this line" | 0 | PASS |
| Cue 4 (neighbors) | P1 + PyMuPDF | text → "Text to the left of A: '...'" | 0 | PASS |
| Cue 5 (ends_period) | P1 text | pattern → "Text A ends with a period" | 0 | PASS |
| Cue 6 (starts_capital) | P1 text | pattern → "Text B starts with a capital" | 0 | PASS |
| Cue 7 (starts_FIG) | P1 text | pattern → "Text A starts with 'FIG.'" | 0 | PASS |

### Verdict

```
All 7 cues: Semantic Authority = 0
All 7 cues: Judgment Leakage = PASS
No cue says KEEP/MERGE/should separate/should merge/system recommends
→ EVIDENCE_CUE_BOUNDARY = PASS
```

### Special Note: Cue 1 on TLD False-Negative Cases

Cue 1 on AMB-313/AMB-462 says "no multi-column structure detected" — this is **factually wrong** (TLD limitation). This is NOT semantic leakage (cue honestly reports TLD detection result). But it IS a potential automation bias source. Must be tested as Wrong-Cue Acceptance case.

---

## 6. Automation Bias Measurement Audit

### Current Design Problem

```
Override Rate ≥ 50% = SAFE
→ ARBITRARY threshold, no theoretical basis
→ Override Rate ≠ Automation Safety Proof
→ Only describes behavior, not safety
→ MUST BE REPLACED
```

### Required Redesign

| Metric | Definition | Purpose |
|---|---|---|
| **Wrong-Cue Acceptance Rate (WCAR)** | When Cue conflicts with GT, Human accepts wrong Cue direction / total conflict cases | Directly measures automation bias harm |
| **Correct Override Rate (COR)** | When Cue conflicts with GT, Human correctly overrides / total conflict cases | WCAR + COR = 1 (for decided cases) |
| **Evidence Inspection Rate (EIR)** | Human inspected underlying evidence before decision / total cases | Low EIR + high WCAR = automation bias pattern |
| **Cue-Following Rate (CFR)** | Human decision matches Cue-implied direction / total cases | High CFR on conflict cases = automation bias |

### Per-Conflict-Case Recording

| Case | Cue-GT Conflict | Human Followed Cue | Override | Correct | Evidence Inspected |
|---|---|---|---|---|---|
| AMB-313 | YES (Cue: no table, GT: KEEP_SEPARATE) | ? | ? | ? | ? |
| AMB-462 | YES (Cue: no table, GT: KEEP_SEPARATE) | ? | ? | ? | ? |
| AMB-414 | NO (Cue: FIG., GT: MERGE — cue correct) | ? | ? | ? | ? |
| AMB-422 | NO (Cue: FIG., GT: MERGE — cue correct) | ? | ? | ? | ? |

### Conflict Case Availability

```
True cue-GT conflict cases: 2 (AMB-313, AMB-462)
Non-conflict C-type cases: 2 (AMB-414, AMB-422 — cue correct)
System≠GT cases: 0

→ Only 2 true conflict cases → INSUFFICIENT for WCAR
→ Need ≥5 conflict cases for meaningful measurement
→ AUTOMATION_BIAS_TEST = INSUFFICIENT_CONFLICT_CASES
```

### Verdict

```
AUTOMATION_BIAS_MEASUREMENT = FAIL (current design)
→ BLOCKING ISSUE #2
→ Must: (1) replace threshold with WCAR/COR/EIR/CFR
        (2) add ≥3 more conflict cases (TLD false-negative or System≠GT)
        (3) no arbitrary safety threshold
```

### Minimum Automation Bias Safety Condition

```
A. Conflict cases must exist (≥5 recommended, minimum 3)
   Current: 2 → FAIL

B. Must observe if Human checked underlying evidence before decision
   Current: EIR not measured → FAIL

C. If Cue wrong + Human did not inspect evidence + Human accepted Cue
   → Record as AUTOMATION_BIAS_EVENT (not hidden)
   Current: no recording mechanism → FAIL
```

---

## 7. Statistical Language Discipline

### Current Design Issues

| Location | Problem | Correction |
|---|---|---|
| PASS criterion | "decision time significantly lower" | → "expected-direction reduction" |
| FAIL criterion | "No significant time difference" | → "no observable direction difference" |
| Override threshold | "≥ 50% = SAFE" | → Remove; report WCAR/COR individually |

### Corrected Language

```
PASS: "B shows expected-direction reduction in decision time compared to A"
PARTIAL: "B shows reduction on some case types but not others"
FAIL: "B shows no reduction or opposite direction"

Report: mean, median, distribution, within-participant difference,
        effect size (if sample allows), individual variability
NOT: p-value, significance, proven reduction

NO_STATISTICAL_GENERALIZATION at n=10 (exploratory pilot)
```

### Verdict

```
STATISTICAL_LANGUAGE = FAIL (current design uses "significantly")
→ BLOCKING ISSUE (minor, easy correction)
→ Must replace all "significant" with "expected-direction"
```

---

## 8. Case Integrity Audit

| Type | Current | Needed | Gap | Integrity |
|---|---|---|---|---|
| P (Positive) | 15 | 10 per set | Need 5 more for Set Y | PASS |
| N (Negative) | **0** | 5-8 | **CRITICAL: 0 available** | **FAIL** |
| B (Boundary) | 2 | 2-3 per set | Need 2-3 more | PARTIAL |
| C (Confounding) | 4 | 2 per set + System≠GT | Need System≠GT | PARTIAL |
| System≠GT | **0** | 3-5 | **CRITICAL: 0 available** | **FAIL** |

### AMB-313 / AMB-462 Special Check

- Correctly classified as C-type (confounding) ✅
- Cue 1 will say "no structure detected" (TLD false negative) ✅
- Human must override cue using visual evidence ✅
- BUT: only 2 such cases → insufficient for WCAR ❌

### AMB-414 / AMB-422 Special Check

- Classified as C-type but are NOT true cue-GT conflicts ⚠️
- Cue 7 ("starts with FIG.") is factually correct, supports MERGE direction
- Cannot test Wrong-Cue Acceptance (cue is right)
- Should be reclassified as P-type for MERGE (caption continuity positive)

### UNKNOWN Preservation

```
Current P01: 0 UNKNOWN selections
→ UNKNOWN preservation CANNOT be tested
→ Need boundary cases where evidence is genuinely ambiguous
→ UNKNOWN_PRESERVATION_TEST = NOT_TESTABLE with current cases
```

### Verdict

```
CASE_INTEGRITY = FAIL
→ BLOCKING ISSUE #3
→ Must: (1) add 5-8 N-type cases
        (2) add 3-5 System≠GT cases
        (3) add 2-3 boundary cases with genuine ambiguity
        (4) reclassify AMB-414/422 (not true conflicts)
```

---

## 9. UNKNOWN / Boundary Preservation

```
UNKNOWN_PRESERVATION = NOT_TESTABLE
  - 0 UNKNOWN in P01 baseline
  - No genuinely ambiguous cases in corpus
  - Cannot verify B doesn't suppress UNKNOWN
  - Must add boundary cases where UNKNOWN is the correct answer
```

### Boundary Preservation

```
BOUNDARY_PRESERVATION = PASS (design level)
  - Cue never says "should keep/separate"
  - Cue describes evidence, not conclusion
  - Human can always select UNKNOWN
  - BUT: cannot verify in practice without ambiguous cases
```

---

## 10. Provenance Audit

| Cue | Source | Traceable | Synthetic | Deterministic |
|---|---|---|---|---|
| Cue 1 | frozen TLD (022f5c21e872ad9e) | YES | NO | YES |
| Cue 2 | frozen TLD | YES | NO | YES |
| Cue 3 | P1 + P2 derived | YES | NO | YES |
| Cue 4 | PyMuPDF on frozen PDFs | YES | NO | YES |
| Cue 5 | P1 text pattern match | YES | NO | YES |
| Cue 6 | P1 text pattern match | YES | NO | YES |
| Cue 7 | P1 text pattern match | YES | NO | YES |

```
PROVENANCE = PASS
  - All cues traceable to frozen evidence
  - No synthetic evidence
  - No hidden detector
  - No new GT
  - All deterministic
```

---

## 11. Learning Effect Audit

```
LEARNING_EFFECT_CONTROL = PASS (with condition)

  - Matched-pairs design (Set X ≠ Set Y) ✅
  - Counterbalanced order (Group 1: A→B, Group 2: B→A) ✅
  - Same case not repeated for same participant ✅
  - Must measure within-session time trend ⚠️
  - Transfer learning risk: MEDIUM (similar structure)

  Condition: Must record and report within-session time trend.
  If trend significant: report as confound.
```

---

## 12. Implementation Readiness

### Blocking Issues Summary

| # | Issue | Severity | Correction |
|---|---|---|---|
| 1 | Attribution confound (deletion + cue confounded) | HIGH | 3-condition design OR keep all fields in B |
| 2 | Automation bias measurement invalid (arbitrary threshold, 2 conflict cases, 0 System≠GT) | HIGH | Replace with WCAR/COR/EIR/CFR + add ≥3 conflict cases |
| 3 | Case corpus incomplete (0 N-type, 0 System≠GT, 0 UNKNOWN baseline) | HIGH | Add N-type + System≠GT + ambiguous boundary cases |
| 4 | same_style LOST without sufficient justification | MEDIUM | Keep in B or add B1 condition |
| 5 | Statistical language uses "significant" | LOW | Replace with "expected-direction" |
| 6 | AMB-414/422 misclassified as conflict cases | LOW | Reclassify as P-type MERGE |

### Non-Blocking (PASS)

| Audit | Result |
|---|---|
| Research question scope | PASS (distillation, not learning) |
| Evidence Cue boundary | PASS (all 7 cues: authority=0, no leakage) |
| Provenance | PASS (all traceable, deterministic) |
| Cognitive work decomposition | PASS (compressible vs non-compressible correct) |
| Learning effect control | PASS (with within-session trend measurement) |
| Class H information loss | PASS (0 decision-relevant fields lost) |

### Final Assessment

```
IMPLEMENTATION_READY = FALSE

  3 HIGH-severity blocking issues must be corrected:
    1. Attribution confound → adopt 3-condition or all-fields design
    2. Automation bias measurement → redesign with WCAR + add conflict cases
    3. Case corpus → add N-type + System≠GT + ambiguous cases

  3 MEDIUM/LOW issues must be corrected:
    4. same_style → keep or justify
    5. Statistical language → replace "significant"
    6. AMB-414/422 → reclassify

  After corrections: re-audit before implementation.
```

### Corrected Success Criteria (Design Specification)

```
Primary Outcome:
  B shows expected-direction reduction in decision time compared to A
  (report: mean, median, distribution, within-participant difference, effect size)

Quality Guard:
  Decision quality (accuracy) B ≥ A
  Boundary quality B ≥ A
  UNKNOWN not artificially reduced (UNKNOWN_B ≥ UNKNOWN_A)
  No increased error propagation

Attribution Guard:
  B underlying evidence unchanged (no new observation)
  Information-equivalence audit PASS
  Cue semantic authority = 0
  Provenance preserved
  3-condition design separates deletion vs distillation effect

Automation Guard:
  Wrong-Cue Acceptance Rate reported (not thresholded)
  Correct Override Rate reported
  Evidence Inspection Rate reported
  Cue-Following Rate reported
  Per-conflict-case recording
  If conflict cases < 3: AUTOMATION_SAFETY = NOT_TESTED
  AUTOMATION_BIAS_EVENT recorded (not hidden)
```

---

## 13. Governance

```
READ_ONLY = TRUE
DESIGN_AUDIT_ONLY = TRUE

CODE_MODIFICATION = 0
UI_MODIFICATION = 0
DATA_MUTATION = 0
GT_MODIFICATION = 0
SCHEMA_MODIFICATION = 0
TLD_MODIFICATION = 0
ATOMIC_MODIFICATION = 0
AGGREGATION_MODIFICATION = 0
COMPRESSION_MODIFICATION = 0
CAPABILITY_REGISTRY_MODIFICATION = 0
RUNTIME_MODIFICATION = 0

NEW_PRIMITIVE = 0
NEW_CONTRACT = 0
NEW_ARCHITECTURE = 0
PATTERN_ENGINE = 0
FEEDBACK_ENGINE = 0
LEARNING_ENGINE = 0
SIGNAL_ENGINE = 0
SIGNAL_OBJECT = 0
ML_TRAINING = 0
LLM_FINE_TUNING = 0

NO_EXPERIMENT_EXECUTION = TRUE
NO_PARTICIPANT_RECRUITMENT = TRUE
FROZEN_BASELINE = INTACT
PRODUCTION = FALSE
RUNTIME_AUTHORITY = ZERO
CAPABILITY_REGISTRATION = HUMAN_CONTROLLED

IMPLEMENTATION_READY = FALSE
IMPLEMENTATION_AUTHORIZED = FALSE
ITERATIVE_LEARNING = INSUFFICIENT_EVIDENCE
STOP = TRUE
```

### Minimal Corrections (NOT Implemented — Design Specification Only)

| # | Correction | Type | Priority |
|---|---|---|---|
| 1 | Adopt 3-condition design (A / B1-deletion / B2-deletion+cue) OR 2-condition with all fields kept | Design change | HIGH |
| 2 | Replace Override threshold with WCAR/COR/EIR/CFR metrics | Design change | HIGH |
| 3 | Add ≥5 N-type + ≥3 System≠GT + ≥3 ambiguous boundary cases | Case preparation | HIGH |
| 4 | Keep same_style in B as progressive disclosure | Design change | MEDIUM |
| 5 | Replace all "significant" with "expected-direction" | Language correction | LOW |
| 6 | Reclassify AMB-414/422 as P-type MERGE (not conflict) | Classification correction | LOW |

### Evidence Classification

- This audit = **B-class** (engineering analysis based on real design + pilot data)
- Blocking issue severity = **B-class** (derived from systematic audit)
- Corrected success criteria = **B-class** (design specification)
- Automation bias redesign = **C-class** (conceptual, not empirically validated)

### Pilot Limitations Preserved

```
n = 1 (P01)
21 cases from 4 documents
0 N-type, 0 System≠GT, 0 conflict, 0 UNKNOWN
Image confound: YES
TLD false negatives: 2/21
NO_STATISTICAL_GENERALIZATION
```
