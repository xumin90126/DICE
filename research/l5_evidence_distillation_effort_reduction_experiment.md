# DICE Evidence Distillation → Human Effort Reduction

## Minimal Evidence Cue Experiment Design — Corrected v2

**Date**: 2026-09-12 (corrected)
**Scope**: Design minimal experiment to test whether Evidence Cue reduces Human effort without reducing decision quality or increasing automation/authority risk
**Governance**: READ_ONLY=TRUE, DESIGN_ONLY=TRUE, FROZEN_BASELINE=INTACT, IMPLEMENTATION_AUTHORIZED=FALSE
**Correction basis**: `tmp/l5_evidence_distillation_preimplementation_audit.md` — 3 HIGH blocking issues resolved

---

## 1. Research Question

> **Can better distillation of already-existing evidence reduce Human effort without reducing decision quality or increasing automation / authority risk?**

### What This Experiment Is NOT

- NOT a Learning Experiment (no Feedback → Reuse → Iteration)
- NOT a Signal Extraction Experiment (no automated signal mining)
- NOT a Pattern Engine Test (no pattern detection)
- NOT a Future-Case Reuse Test (no cross-round application)

### What This Experiment IS

A single-round, **three-condition** comparison separating Information Reduction from Evidence Distillation:
- **Condition A**: Full evidence presentation (15 fields + page image)
- **Condition B1**: Reduced evidence (8 fields + page image, no cues)
- **Condition B2**: Reduced evidence + Evidence Cue (8 fields + 4 cues + page image)

All three conditions use the **same underlying evidence**. No condition adds new facts. Changes are **presentation/distillation** only.

---

## 2. Current Baseline

### What Human Currently Sees (Condition A)

| Evidence | Exposed? | Human Used? (P01) |
|---|---|---|
| text_a | YES | YES |
| text_b | YES | YES |
| page_image | YES | YES |
| A/B highlight | YES | YES |
| line_spans | YES | YES |
| h_gap (numeric) | YES | NO (unused) |
| dy (numeric) | YES | NO (unused) |
| same_style (boolean) | YES | NO (unused) |
| width_a (numeric) | YES | NO (unused) |
| width_b (numeric) | YES | NO (unused) |
| style_sig_a (string) | YES | NO (unused, misleading) |
| style_sig_b (string) | YES | NO (unused, misleading) |
| line_obs_count | YES | INDIRECTLY |
| doc_id | YES | INDIRECTLY |
| page_number | YES | INDIRECTLY |

### What Exists But Is NOT Exposed

| Evidence | Available? | Why Not Shown? |
|---|---|---|
| TLD is_in_table | 21/21 (frozen) | Not in UI |
| TLD different_cell | 21/21 (frozen) | Not in UI |
| SCE different_local_partition | 11/21 (frozen) | Not in UI |
| RSC region_forms | 21/21 (frozen) | Not in UI |
| Text patterns (ends_with_period, starts_with_FIG) | Computable | Not computed |

### P01 Baseline Metrics

| Metric | Value |
|---|---|
| Decision time (A-phase) | avg 3.9s/case |
| Decision accuracy | 21/21 (100%) |
| UNKNOWN rate | 0% |
| Evidence expansion (C-phase) | avg 1 level |
| Fields used | 5/15 (33%) |
| Noise ratio | 80% (12 unused fields) |

---

## 3. Three-Condition Design

### Condition A — Full Evidence Baseline

```
A = 15 original fields + page image
```

Purpose: Current Human Validation complete evidence presentation baseline.

### Condition B1 — Reduced Evidence / No Cue

```
B1 = 8 fields + page image (no cues)
```

- Removes low-value fields from main view
- Does NOT add any Evidence Cue
- Underlying evidence unchanged
- Page image unchanged
- Hidden fields available via Progressive Disclosure

Purpose: Isolate and measure **Information Reduction Effect** — does reducing noise alone reduce Human effort?

### Condition B2 — Reduced Evidence + Evidence Cue

```
B2 = 8 fields + 4 Evidence Cue + page image
```

- Same field set as B1
- Only addition: Evidence Cues
- Cues derived entirely from existing evidence
- No new underlying evidence

Purpose: Isolate and measure **Evidence Distillation Effect** — does adding cues provide incremental value beyond field reduction?

### Critical Constraint

> **B2 cannot obtain facts that A or B1 do not have.**

All three conditions share identical underlying evidence. Only presentation differs.

---

## 4. Attribution Logic

### Primary Comparison: B1 vs B2

```
B1 vs B2
```

Both have identical field sets. The only difference is Evidence Cue. This is the **cleanest test of Evidence Distillation**.

### Secondary Comparison 1: A vs B1

```
A vs B1
```

Measures **Information Reduction Effect** — does removing low-value fields reduce effort?

### Secondary Comparison 2: A vs B2

```
A vs B2
```

Measures **Overall Presentation Improvement** — does the complete distillation package improve Human experience vs original?

### Interpretation Matrix

| Pattern | Conclusion |
|---|---|
| A > B1, B1 ≈ B2 | Mainly Information Reduction; Cue adds no incremental value |
| A > B1, B1 > B2 | Both Information Reduction AND Evidence Distillation contribute |
| A ≈ B1, B1 > B2 | **Most valuable**: Cue provides value that field reduction alone cannot |
| B2 faster but quality↓ or UNKNOWN↓ or WCAR↑ | NOT success — automation bias or quality degradation |

### Strict Distinction

```
Information Reduction (A → B1)
≠
Evidence Distillation (B1 → B2)
```

Only B1 → B2 is the core Evidence Distillation comparison.

---

## 5. Information Equivalence Audit (Corrected)

### A → B1 → B2 Complete Mapping

| A Field | Class | A | B1 | B2 | Information Status | Loss Risk |
|---|---|---|---|---|---|---|
| text_a | H | shown | shown | shown | RETAINED | NONE |
| text_b | H | shown | shown | shown | RETAINED | NONE |
| page_image | H | shown | shown | shown | RETAINED | NONE |
| A/B highlight | H | shown | shown | shown | RETAINED | NONE |
| line_spans | H | shown | shown | shown | RETAINED | NONE |
| line_obs_count | M | shown | shown | shown + Cue 3 | RE-EXPRESSED | NONE |
| h_gap | M | shown | hidden (progressive) | hidden + Cue 2 | RE-EXPRESSED | LOW |
| same_style | M | shown | **HIDDEN_NOT_DELETED** | **HIDDEN_NOT_DELETED** | HIDDEN (progressive disclosure) | MEDIUM→LOW |
| doc_id | L | shown | shown | shown | RETAINED | NONE |
| page_number | L | shown | shown | shown | RETAINED | NONE |
| dy | L | shown | hidden (progressive) | hidden (progressive) | HIDDEN (progressive disclosure) | NONE |
| width_a | L | shown | hidden (progressive) | hidden (progressive) | HIDDEN (progressive disclosure) | NONE |
| width_b | L | shown | hidden (progressive) | hidden (progressive) | HIDDEN (progressive disclosure) | NONE |
| style_sig_a | L | shown | hidden (progressive) | hidden (progressive) | HIDDEN (progressive disclosure) | NONE |
| style_sig_b | L | shown | hidden (progressive) | hidden (progressive) | HIDDEN (progressive disclosure) | NONE |

### Field Status Definitions

| Status | Meaning |
|---|---|
| RETAINED | Field shown in main view, identical across all conditions |
| RE-EXPRESSED | Original evidence compressed into Cue; underlying evidence traceable |
| HIDDEN_NOT_DELETED | Field hidden from main view but available via Progressive Disclosure; underlying evidence intact |

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
Class M HIDDEN_NOT_DELETED: 1 (same_style)
Class M LOST: 0
→ PASS: same_style preserved via Progressive Disclosure
```

### Class L (Low-Value) Loss Check

```
Class L fields: 7
Class L RETAINED: 2 (doc_id, page_number)
Class L HIDDEN_NOT_DELETED: 5 (dy, width_a, width_b, style_sig_a, style_sig_b)
Class L LOST: 0
→ PASS: All hidden, none deleted, provenance preserved
```

### Evidence Equality Guarantee (Corrected)

```
Underlying_Evidence(A) == Underlying_Evidence(B1) == Underlying_Evidence(B2)

A:  15 fields + page image
B1: 8 fields (main) + 7 hidden (progressive) + page image
B2: 8 fields (main) + 7 hidden (progressive) + 4 cues + page image

No condition adds new observation.
No condition changes P1/P2/P6/TLD/SCE/RSC.
No condition deletes underlying evidence.
Conditions only change main-view presentation.
```

### same_style Correction

```
same_style: HIDDEN_NOT_DELETED (not REMOVED)

  B1 main view: hidden
  B1 progressive disclosure: available
  B2 main view: hidden
  B2 progressive disclosure: available

  Underlying evidence: intact (frozen P3)
  Provenance: preserved
  If participant needs style info: can expand progressive disclosure panel
```

---

## 6. Evidence Cue Boundary

### Cue Definition

```
Cue = Evidence-derived presentation
Cue ≠ Judgment
Cue ≠ Rule
Cue ≠ Decision
Cue ≠ Recommendation
Cue ≠ Confidence
Cue ≠ Score
```

### Safe Cue Set (from L5.10, 7 cues — up to 4 shown per case)

| Cue # | Source | Safe Output | Semantic Leap Risk |
|---|---|---|---|
| 1 | TLD is_in_table | "within a detected multi-column aligned structure" / "no multi-column aligned structure detected" | LOW |
| 2 | TLD different_cell | "in different structural positions" / "in the same structural position" | LOW |
| 3 | line_obs_count | "There are N text items on this line" | NONE |
| 4 | line_spans neighbors | "Text to the left of A: '{text}'" | NONE |
| 5 | P1 text pattern | "Text A ends with a period" | LOW |
| 6 | P1 text pattern | "Text B starts with a capital letter" | LOW |
| 7 | P1 text pattern | "Text A starts with 'FIG.'" | LOW |

### Per-Cue Semantic Authority

| Cue | Underlying Evidence | Transformation | Semantic Authority | Judgment Leakage |
|---|---|---|---|---|
| Cue 1 | frozen TLD | boolean → natural language | 0 | PASS |
| Cue 2 | frozen TLD | boolean → natural language | 0 | PASS |
| Cue 3 | P1 + P2 | integer → natural language | 0 | PASS |
| Cue 4 | P1 + PyMuPDF | text → quotation | 0 | PASS |
| Cue 5 | P1 text | pattern match → fact | 0 | PASS |
| Cue 6 | P1 text | pattern match → fact | 0 | PASS |
| Cue 7 | P1 text | pattern match → fact | 0 | PASS |

### Forbidden Outputs (Leakage Check)

| ❌ Forbidden | ✅ Safe Alternative |
|---|---|
| "应该分开" (should separate) | "in different structural positions" |
| "属于不同表格列" (different table columns) | "in different structural positions" |
| "这是同一句话" (same sentence) | "Text A ends with a period" |
| "系统判断为 KEEP" | (no system judgment allowed) |
| "置信度 95%" | (no confidence score allowed) |

### Cue Boundary Verdict

```
All 7 cues: Semantic Authority = 0
All 7 cues: Judgment Leakage = PASS
→ EVIDENCE_CUE_BOUNDARY = PASS
```

---

## 7. Condition Field Sets

### Condition A (15 fields + image)

```
Main view: text_a, text_b, page_image, A/B_highlight, line_spans,
           h_gap, dy, same_style, width_a, width_b, style_sig_a, style_sig_b,
           line_obs_count, doc_id, page_number
Cues: none
```

### Condition B1 (8 fields + image, no cues)

```
Main view: text_a, text_b, page_image, A/B_highlight, line_spans,
           line_obs_count, doc_id, page_number
Progressive disclosure: h_gap, dy, same_style, width_a, width_b, style_sig_a, style_sig_b
Cues: none
```

### Condition B2 (8 fields + 4 cues + image)

```
Main view: text_a, text_b, page_image, A/B_highlight, line_spans,
           line_obs_count, doc_id, page_number
Cues (up to 4): Cue 1 (multi-column structure), Cue 2 (structural position),
                Cue 3 (line item count), Cue 4 (text pattern when matched)
Progressive disclosure: h_gap, dy, same_style, width_a, width_b, style_sig_a, style_sig_b
```

---

## 8. Experiment Hypotheses

### H1 — Information Reduction

```
B1 may require less Human effort than A.
```

### H2 — Evidence Distillation (Primary)

```
B2 may require less Human effort than B1.
AND
Decision Quality(B2) ≥ Decision Quality(B1)
```

### H3 — Boundary Safety

```
UNKNOWN(B2) should not be artificially lower than UNKNOWN(B1) or UNKNOWN(A).
If UNKNOWN decreases, must verify it is not due to cue-induced over-certainty.
```

### H4 — Automation Bias

```
In cue-conflict cases, Human should be able to:
  - inspect underlying evidence
  - override cue when necessary
  - make correct decision despite misleading cue

No preset Override threshold.
Report: WCAR, COR, EIR, CFR, individual variation, case-level errors.
```

---

## 9. Case Selection (Corrected)

### Five Case Types

| Type | Description | Purpose | Current | Needed | Total Target |
|---|---|---|---|---|---|
| **P** | Positive — clear structural evidence | Test cue speedup on obvious cases | 13 (was 15, AMB-414/422 reclassified) | +5 for Set Y | 18 |
| **N** | Negative — similar appearance, different judgment | Test cue doesn't induce errors on confusing cases | 0 | **+5-8** | 5-8 |
| **B** | Boundary — evidence ambiguous, UNKNOWN acceptable | Test UNKNOWN preservation | 2 | **+3** | 5 |
| **C** | Confounding — cue could mislead (TLD false negative) | Test override behavior | 2 (AMB-313, AMB-462) | +2 for Set Y | 4 |
| **S** | System≠GT — cue direction ≠ GT | Test Wrong-Cue Acceptance | 0 | **+3-5** | 3-5 |
| **U** | UNKNOWN baseline — genuinely ambiguous | Establish UNKNOWN rate baseline | 0 | **+2** | 2 |

**Note**: Types may overlap (a case can be both C and S). Not all categories are mutually exclusive.

### AMB-414 / AMB-422 Reclassification

```
AMB-414: reclassified as P-type MERGE (was C-type)
  - Cue 7 ("starts with FIG.") is factually correct
  - GT = MERGE → cue supports correct direction
  - NOT a cue-conflict case
  - Tests normal MERGE / figure-caption interpretation

AMB-422: reclassified as P-type MERGE (was C-type)
  - Same as AMB-414
  - NOT a cue-conflict case
```

### AMB-313 / AMB-462 Verification

```
AMB-313:
  TLD is_in_table = False (TLD false negative)
  Cue 1 output: "no multi-column aligned structure detected"
  GT reviewer: "two different column headers in Table 6"
  Human-correct interpretation: KEEP_SEPARATE (table columns)
  → TRUE cue-GT conflict: Cue says no structure, but table exists
  → Classified as C-type + S-type (System≠Human)

AMB-462:
  TLD is_in_table = False (TLD false negative)
  Cue 1 output: "no multi-column aligned structure detected"
  GT reviewer: "two adjacent column headers in Table 2"
  Human-correct interpretation: KEEP_SEPARATE (table columns)
  → TRUE cue-GT conflict: Cue says no structure, but table exists
  → Classified as C-type + S-type (System≠Human)
```

### Required New Cases (NOT yet prepared)

| Type | Count | Source | Status |
|---|---|---|---|
| N (Negative) | 5-8 | New IS-11 extraction or other documents | NOT PREPARED |
| B (Boundary) | 3 | Genuinely ambiguous structure cases | NOT PREPARED |
| S (System≠GT) | 3-5 | Cases where cue direction ≠ GT | NOT PREPARED |
| U (UNKNOWN baseline) | 2 | Cases where evidence insufficient for definite answer | NOT PREPARED |
| P (for Set Y) | 5 | Matched table column cases from new docs | NOT PREPARED |
| C (for Set Y) | 2 | TLD edge cases from new docs | NOT PREPARED |
| **Total new** | **20-25** | | **NOT PREPARED** |

### Cue-Conflict Case Chain

Each conflict case must have complete chain:

```
Underlying Evidence → Evidence Cue → GT → Human-correct interpretation
```

| Case | Underlying Evidence | Cue Output | GT | Conflict Type |
|---|---|---|---|---|
| AMB-313 | TLD is_in_table=False | "no multi-column structure detected" | KEEP_SEPARATE | Cue≠GT (TLD false negative) |
| AMB-462 | TLD is_in_table=False | "no multi-column structure detected" | KEEP_SEPARATE | Cue≠GT (TLD false negative) |
| New S-type 1-3 | (to be prepared) | (cue direction) | (opposite GT) | Cue≠GT |
| New S-type 4-5 | (to be prepared) | (cue direction) | (opposite GT) | Cue≠GT |

**Minimum conflict cases for WCAR**: 5 (2 existing + 3 new)

---

## 10. Automation Bias Measurement (Corrected)

### Removed: Arbitrary Threshold

```
DELETED: "Override Rate ≥ 50% = SAFE"
DELETED: Any preset safety threshold
```

### Adopted: Four Behavioral Metrics

| Metric | Definition | Purpose |
|---|---|---|
| **WCAR** (Wrong-Cue Acceptance Rate) | When Cue≠GT, Human accepts wrong Cue direction / total conflict cases | Directly measures automation bias harm |
| **COR** (Correct Override Rate) | When Cue≠GT, Human correctly overrides / total conflict cases | Measures independent verification |
| **EIR** (Evidence Inspection Rate) | Human inspected underlying evidence/image before decision / total cases | Low EIR + high WCAR = automation bias pattern |
| **CFR** (Cue-Following Rate) | Human decision matches Cue-implied direction / total cases | High CFR on conflict cases = automation bias |

### Per-Conflict-Case Recording

| Case | Cue-GT Conflict | Human Followed Cue | Override | Correct | Evidence Inspected | AUTOMATION_BIAS_EVENT |
|---|---|---|---|---|---|---|
| AMB-313 | YES | ? | ? | ? | ? | ? |
| AMB-462 | YES | ? | ? | ? | ? | ? |
| New S-1 | YES | ? | ? | ? | ? | ? |
| New S-2 | YES | ? | ? | ? | ? | ? |
| New S-3 | YES | ? | ? | ? | ? | ? |

### AUTOMATION_BIAS_EVENT Definition

```
AUTOMATION_BIAS_EVENT = TRUE when:
  Cue ≠ GT (wrong cue)
  AND Human did NOT inspect underlying evidence
  AND Human accepted Cue direction
  AND Human decision ≠ GT (wrong decision)

This MUST be recorded, NOT hidden.
```

### Minimum Automation Bias Safety Condition

```
A. Conflict cases must exist (≥5 recommended, minimum 3)
   Current: 2 existing + 3 new = 5 → PASS (after case preparation)

B. Must observe if Human checked underlying evidence before decision
   EIR measured per case → PASS (after schema implementation)

C. AUTOMATION_BIAS_EVENT recorded when:
   Cue wrong + Human did not inspect + Human accepted Cue
   → MUST be recorded, NOT hidden → PASS (after schema implementation)
```

### Reporting (No Threshold)

```
Report descriptively:
  - WCAR (raw count + rate)
  - COR (raw count + rate)
  - EIR (raw count + rate)
  - CFR (raw count + rate, split by conflict vs non-conflict)
  - Individual variation (per participant)
  - Case-level errors (which cases, what went wrong)

DO NOT:
  - Set "WCAR < X% = SAFE"
  - Set "Override ≥ X% = SAFE"
  - Claim "automation bias not present" without case-level evidence
```

---

## 11. UNKNOWN Preservation (Corrected)

### UNKNOWN Baseline Requirement

```
Current P01: 0 UNKNOWN selections
→ Cannot test UNKNOWN preservation without baseline
→ MUST add ≥2 genuinely ambiguous cases (U-type)

U-type cases must satisfy:
  - Current evidence is insufficient for definite Human judgment
  - Both KEEP_SEPARATE and MERGE are plausible
  - GT may be adjudicated as UNKNOWN or contested
  - NOT artificially manufactured ambiguity
```

### UNKNOWN Hard Constraint

```
If UNKNOWN(B1) < UNKNOWN(A):
  → Must explain: is it because fewer fields = less uncertainty?
  → Check: did accuracy also decrease?

If UNKNOWN(B2) < UNKNOWN(B1):
  → Must explain: is it because Cue made Human over-certain?
  → CRITICAL CHECK: Cue clarity↑ + Human uncertainty↓ + correctness↓
  → If this pattern appears: AUTOMATION_BIAS risk
  → Must NOT interpret UNKNOWN↓ as "better"
```

---

## 12. Participant / Counterbalancing Design

### Design: 3-Condition with Latin Square

```
3 conditions: A, B1, B2
3 case sets: X, Y, Z (matched, different cases)

Latin Square:
  Group 1 (n≥5): A on X → B1 on Y → B2 on Z
  Group 2 (n≥5): A on Y → B1 on Z → B2 on X
  Group 3 (n≥5): A on Z → B1 on X → B2 on Y
```

### Set Composition (per set)

| Type | Count |
|---|---|
| P | 6 |
| N | 2 |
| B | 2 |
| C | 1-2 |
| S | 1-2 |
| U | 1 |
| **Total per set** | **13-16** |

### Learning Effect Control

| Risk | Mitigation |
|---|---|
| Same case seen 3 times | **Set X ≠ Y ≠ Z** — no case appears in multiple sets for same participant |
| Condition order effect | Latin Square counterbalancing (3 groups, 3 orders) |
| Transfer learning | Measure within-session time trend; report if significant |
| Fatigue | Mandatory breaks between conditions; randomize case order within condition |

### LEARNING_EFFECT_RISK

```
PARTIALLY CONTROLLED
  - Same case not repeated across conditions ✅
  - Latin Square counterbalancing ✅
  - Must measure within-session time trend ⚠️
  - Transfer learning risk: MEDIUM
```

### Participant Requirements

| Parameter | Minimum | Recommended |
|---|---|---|
| n per group | 5 | 7 |
| Total n | 15 | 21 |
| Prior exposure | None (different from P01) | None |
| Expertise | Mixed | Mixed |

---

## 13. Measurement Plan

### Primary Outcome

| Metric | Condition Comparison |
|---|---|
| **Decision Time** | B1 vs B2 (primary), A vs B1 (secondary), A vs B2 (secondary) |

### Secondary Outcomes

| Metric | Type |
|---|---|
| Evidence Expansion Count | Effort |
| Levels Viewed | Engagement |
| Screenshot/Page Revisit | Process |
| Cross-instance Comparison Count | Cognitive Process |
| Abstraction Burden | Cognitive Load |
| Interaction Count | Engagement |

### Safety / Quality Metrics

| Metric | Type |
|---|---|
| Correctness | Quality |
| Boundary Correctness | Quality |
| UNKNOWN Rate | Boundary Safety |
| WCAR | Automation Bias |
| COR | Automation Bias |
| EIR | Automation Bias |
| CFR | Automation Bias |
| Cue Inspection (did Human read cue?) | Process |
| AUTOMATION_BIAS_EVENT | Safety |

### Recording Schema Extension

| Field | Type | Description |
|---|---|---|
| condition | string | "A" / "B1" / "B2" |
| set_id | string | "X" / "Y" / "Z" |
| case_type | string | "P" / "N" / "B" / "C" / "S" / "U" |
| cue_shown | array | cues presented (B2 only) |
| cue_inspected | boolean | did Human expand/read cue panel |
| decision_time_ms | integer | milliseconds |
| field_expansion_count | integer | total field/cue expansions |
| progressive_disclosure_used | boolean | did Human access hidden fields |
| progressive_disclosure_fields | array | which hidden fields were accessed |
| image_interactions | integer | zoom/scroll/pan count |
| evidence_inspected | boolean | did Human inspect evidence before decision |
| cue_followed | boolean | did Human decision match cue direction |
| automation_bias_event | boolean | AUTOMATION_BIAS_EVENT flag |

**Note**: Schema extension is design specification. Implementation requires authorization.

---

## 14. Cognitive Work Decomposition

### Human Judgment Process (6 Steps)

| Step | Description | Compressible? | Current Cost | Cue Effect |
|---|---|---|---|---|
| 1. Look | Visual scan of page image | YES | 0.5-2s | Pre-labels structure |
| 2. Find relevant evidence | Identify which fields matter | YES | 2-5s | Eliminates noise (B1) + cues guide attention (B2) |
| 3. Understand raw evidence | Interpret h_gap, style_sig | YES | 1-3s | Cues translate to natural language (B2 only) |
| 4. Compare low-level evidence | Compare A/B positions | PARTIAL | 1-2s | Pre-computes positional comparison (B2 only) |
| 5. Construct interpretation | Form hypothesis | **NO** | 1-3s | Supports but does not replace |
| 6. Make judgment | KEEP/MERGE/UNKNOWN | **NO** | 0.5-1s | Must not influence |

### Compressible vs Non-Compressible

```
Compressible (Steps 1-4):     ~4.5-12s total
  B1 reduces: Steps 1-2 (less noise to scan)
  B2 reduces: Steps 1-4 (cues translate + guide)

NOT Compressible (Steps 5-6): ~1.5-4s total
  Must remain Human authority in all conditions
```

### Burden Transfer Check

```
True Compression (success):
  System distills evidence → Human faster understanding

Burden Transfer (failure):
  System outputs complex structure → Human must re-interpret

Check: Does B2 reduce Human reasoning load (Steps 1-4)?
  OR does B2 add new interpretation burden (cues need explanation)?
  → Cue language must be self-explanatory (natural language, no technical terms)
  → If Human must interpret cue → burden transfer, not compression
```

---

## 15. Statistical Language (Corrected)

### Removed

```
DELETED: "significantly lower" (implies statistical significance)
DELETED: "No significant time difference"
DELETED: Any pre-data significance claim
```

### Corrected Language

```
Primary outcome: "B2 shows expected-direction reduction in decision time compared to B1"

Report:
  - mean, median, distribution
  - within-participant difference
  - effect size (if sample allows)
  - individual variability
  - per-case-type breakdown

DO NOT report:
  - p-value as proof
  - "statistically significant"
  - "proven reduction"

NO_STATISTICAL_GENERALIZATION at n=15 (exploratory pilot)
```

---

## 16. Success / Partial / Fail Criteria (Corrected)

### PASS (ALL must hold)

| Criterion | Measurement |
|---|---|
| Human Effort: B2 < B1 (expected-direction) | Decision time comparison |
| Human Effort: B1 ≤ A (expected-direction) | Decision time comparison |
| Decision Quality: B2 ≥ B1 ≥ A | Accuracy not lower |
| Boundary Safety: UNKNOWN(B2) not artificially lower | UNKNOWN rate comparison + correctness check |
| Automation Bias: WCAR reported, no AUTOMATION_BIAS_EVENT pattern | Case-level analysis |
| Underlying Evidence unchanged | No new observation in any condition |
| Cue contains no semantic judgment | Leakage check pass |
| Attribution valid | B1 vs B2 isolates distillation effect |

### PARTIAL_PASS (any one)

| Criterion | Condition |
|---|---|
| B2 < B1 but B1 ≈ A | Distillation helps, but field reduction doesn't |
| B1 < A but B1 ≈ B2 | Field reduction helps, but cue doesn't add value |
| P-type improved but N/B/S-type not | Cue helps easy cases only |
| WCAR > 0 but no systematic AUTOMATION_BIAS_EVENT | Some wrong-cue acceptance but not pattern |

### FAIL (any one)

| Criterion | Condition |
|---|---|
| B2 faster but Quality(B2) < Quality(B1) | Accuracy degraded |
| AUTOMATION_BIAS_EVENT pattern (Cue wrong + no inspection + accepted) | Systematic rubber-stamping |
| Cue contains semantic judgment | Leakage check fail |
| Cue requires new observation | Scope violation |
| B2 ≈ B1 (no distillation effect) | Cue provides no incremental value |
| UNKNOWN(B2) < UNKNOWN(B1) AND correctness(B2) < correctness(B1) | Over-certainty harm |

---

## 17. Attribution Factor Assessment (Corrected)

| Factor | Control | Risk | How Measured |
|---|---|---|---|
| A. Evidence Distillation (cue) | **STRONG** — B1 vs B2 isolates cue | LOW | B1 vs B2 comparison |
| B. Information Deletion | **STRONG** — A vs B1 isolates deletion | LOW | A vs B1 comparison |
| C. UI Presentation | **PARTIAL** — layout differs between A and B1/B2 | MEDIUM | Visual layout control |
| D. Learning Effect | **GOOD** — Latin Square + matched sets | LOW | Within-session trend |
| E. Automation Bias | **GOOD** — WCAR/COR/EIR/CFR + conflict cases | LOW | Case-level analysis |

---

## 18. Threats to Validity

| Threat | Type | Mitigation | Residual Risk |
|---|---|---|---|
| Learning effect | Internal validity | Latin Square + matched sets | MEDIUM (transfer learning) |
| n too small | Statistical power | n=15 minimum; exploratory only | HIGH (NO_STATISTICAL_GENERALIZATION) |
| Image confound | Construct validity | All conditions have image | HIGH (cue may be image-redundant) |
| TLD false negatives | External validity | C-type + S-type conflict cases test override | MEDIUM |
| Case corpus bias | External validity | Need 20-25 new cases | HIGH (limited diversity until prepared) |
| Progressive disclosure confound | Construct validity | Track progressive_disclosure_used | LOW |

---

## 19. Expected Interpretation

### Most Likely Outcome: PARTIAL_PASS

**Expected**: B1 < A (field reduction helps), B2 ≤ B1 (cue provides marginal additional benefit).

**Reasoning**:
- B1 removes 7 unused fields → less scanning time
- B2 adds cues → may help on P-type (confirm structure) but may not help on B/S-type (cue ambiguous or wrong)
- C-type (TLD false negative): cue may SLOW DOWN (Human must resolve cue-image conflict)

### Per-Type Expected Effect

| Type | B1 vs A | B2 vs B1 | Risk |
|---|---|---|---|
| P | ↓ (less noise) | ↓ (cue confirms structure) | LOW |
| N | ↓ (less noise) | ? (cue may or may not help) | MEDIUM |
| B | ↓ (less noise) | ↔ or ↑ (cue may not resolve ambiguity) | MEDIUM |
| C | ↓ (less noise) | ↑ (cue contradicts image → longer) | HIGH (tests override) |
| S | ↓ (less noise) | ↑ (cue wrong → longer if Human checks) | HIGH (tests WCAR) |
| U | ↓ (less noise) | ↔ (cue doesn't resolve genuine ambiguity) | MEDIUM |

---

## 20. Four Research Questions

### Q1: Evidence Cue 是否真的降低了 Human 当前操作成本？

**Expected**: YES on P-type (B2 < B1), MIXED on B/C/S-type.

### Q2: 降低的是哪一种成本？

**Expected**: Primarily Step 2 (Find) and Step 3 (Understand).
**NOT expected**: Step 5 (Interpret) or Step 6 (Judge) — if these decrease, indicates automation bias.

### Q3: 这种降低是否以质量/安全为代价？

Must verify: accuracy ≥, UNKNOWN ≥, WCAR reported, no AUTOMATION_BIAS_EVENT pattern.

### Q4: 如果成功，下一步是否值得研究 Feedback 复用？

If PASS: YES — Evidence Cue as carrier for validated signals.
If FAIL: Diagnose cue design vs evidence non-compressibility.

---

## 21. Learning Boundary

```
This experiment tests:
  Evidence Distillation → Human Effort Reduction

It does NOT test:
  Iterative Learning
  Feedback Reuse
  Future-Case Application

ITERATIVE_LEARNING = INSUFFICIENT_EVIDENCE
  (remains unchanged regardless of experiment outcome)
```

### Stage Progression

```
Stage 1 (THIS EXPERIMENT):
  Evidence Distillation → Human Effort Reduction

Stage 2 (FUTURE):
  Human Feedback → Reusable Signal

Stage 3 (FUTURE):
  Human Validation → Reuse

Stage 4 (FUTURE):
  Future Cases → Human Effort Reduction

Only after Stage 4:
  Iterative Learning discussion
```

---

## 22. Provenance Audit

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

## 23. Design Status

### Prerequisites for Implementation

| Prerequisite | Status |
|---|---|
| 3-condition design (A / B1 / B2) | ✅ DONE (this correction) |
| Information equivalence audit | ✅ DONE (A→B1→B2 mapping) |
| same_style HIDDEN_NOT_DELETED | ✅ DONE |
| Automation bias redesign (WCAR/COR/EIR/CFR) | ✅ DONE |
| Statistical language corrected | ✅ DONE |
| AMB-414/422 reclassified | ✅ DONE |
| Cognitive work decomposition | ✅ DONE |
| Latin Square counterbalancing | ✅ DONE |
| Success/fail criteria corrected | ✅ DONE |
| **New cases (N/B/S/U + Set Y/Z)** | ❌ NOT PREPARED |
| **Participants (n≥15)** | ❌ NOT RECRUITED |
| **UI for 3 conditions** | ❌ NOT IMPLEMENTED |
| **Recording schema extension** | ❌ NOT IMPLEMENTED |
| **GT for new cases** | ❌ NOT ADJUDICATED |

### DESIGN_STATUS

```
DESIGN_STATUS = READY

Design is complete, internally consistent, and all 3 HIGH blocking issues resolved.
Implementation is blocked by PREPARATION only (cases, participants, UI, schema, GT).
All design-level issues are resolved.
```

---

## 24. Governance

```
READ_ONLY = TRUE
DESIGN_ONLY = TRUE

CODE_MODIFICATION = 0
UI_MODIFICATION = 0
DATA_MUTATION = 0
GT_MODIFICATION = 0
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
ML_TRAINING = 0
LLM_FINE_TUNING = 0

IMPLEMENTATION_REQUIRED = TRUE (for experiment execution)
IMPLEMENTATION_AUTHORIZED = FALSE

FROZEN_BASELINE = INTACT
PRODUCTION = FALSE
RUNTIME_AUTHORITY = ZERO
CAPABILITY_REGISTRATION = HUMAN_CONTROLLED

ITERATIVE_LEARNING = INSUFFICIENT_EVIDENCE
STOP = TRUE
```

### Evidence Classification

- This corrected design = **B-class** (engineering design based on audit corrections)
- Expected distillation benefit = **C-class** (hypothesis, not empirically tested)
- Expected automation bias risk = **C-class** (not tested, conceptual)
- Attribution validity = **B-class** (3-condition design provides clean isolation)
- Automation bias measurement = **B-class** (WCAR/COR/EIR/CFR are observable)

### Pilot Limitations Preserved

```
n = 1 (P01)
21 cases from 4 documents
0 N-type, 0 System≠GT, 0 conflict, 0 UNKNOWN (before correction)
Image confound: YES
TLD false negatives: 2/21
NO_STATISTICAL_GENERALIZATION at minimum n=15
```
