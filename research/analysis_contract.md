# Formal Experiment Analysis Contract

**Version**: exp_v2_patched
**Date**: 2026-09-12
**Scope**: Analysis rules for the Formal Human Experiment (when it occurs)
**Status**: FROZEN — must not be modified after experiment data collection begins

---

## 1. Primary Question

> Does adding Evidence Cue to an information-reduced presentation (B1 → B2) reduce Human effort while preserving decision quality?

## 2. Primary Comparison

```
B1 vs B2
```

Secondary comparisons (for context, NOT primary):
- A vs B1 (Information Reduction effect)
- A vs B2 (Overall improvement)

## 3. Primary Population

### Inclusion Criteria

```
condition ∈ {B1, B2}
AND
Cue_available = TRUE  (case has ≥1 real Evidence-grounded Cue in B2)
AND
not_dry_run = TRUE    (participant_id does NOT start with "DRYRUN_")
AND
submission_complete = TRUE
```

### Exclusion Criteria

```
Cue_available = FALSE  (zero-cue cases: B1 == B2, no treatment contrast)
DRYRUN_*               (implementation verification, not scientific data)
technical_failure      (incomplete/missing submission)
```

### Zero-Cue Cases (7/30)

These cases are EXCLUDED from primary B1-vs-B2 analysis but RETAINED for:
- Exposure accounting
- Evidence availability reporting
- Secondary descriptive analysis
- Limitation reporting

### Do Not Over-filter

Primary filter is ONLY about Cue treatment existence. Do NOT additionally filter by:
- Case difficulty
- N/B/S/U type
- UNKNOWN responses
- Slow participants

Other variables are for stratification / sensitivity analysis, not exclusion.

## 4. Primary Effort Indicators

```
decision_time           (seconds, primary)
evidence_expansion_count (number of progressive-disclosure expansions)
revisit_count           (image interactions)
levels_viewed           (1 = main only, 2 = expanded)
interaction_count       (total UI interactions)
```

## 5. Quality Indicators

```
decision_correctness    (decision == GT)
boundary_correctness    (correct on B/U-type cases)
UNKNOWN_preservation    (UNKNOWN rate not artificially suppressed in B2)
```

### UNKNOWN Hard Constraint

```
If UNKNOWN(B2) < UNKNOWN(B1):
  → Must investigate: is it cue-induced over-certainty?
  → Check: did correctness also decrease?
  → If UNKNOWN↓ AND correctness↓: AUTOMATION_BIAS risk
  → Must NOT interpret UNKNOWN↓ as "better"
```

## 6. Safety Indicators

```
automation_bias         (WCAR, COR, EIR, CFR)
cue_over_reliance       (high CFR on conflict cases)
system_ne_gt_response   (behavior on AMB-313, AMB-462)
conflict_response       (case-level observation on 2 genuine conflict cases)
```

## 7. Automation Bias Reporting

### Genuine Conflict Cases

```
AMB-313: TLD false negative, Cue1 says "no structure", GT=KEEP_SEPARATE
AMB-462: TLD false negative, Cue1 says "no structure", GT=KEEP_SEPARATE
N = 2
```

### Reporting Rule

```
N = 2 → case-level exploratory report ONLY.

PROHIBITED:
  - significance tests on WCAR/COR
  - statistical generalization from n=2
  - "automation bias rate" overall inference
  - inferring Human behavior from 2 cases

REQUIRED:
  - Report each conflict case individually
  - Report: cue shown, human decision, evidence inspected, override, correct
  - Report AUTOMATION_BIAS_EVENT per case (TRUE/FALSE)
```

## 8. Tier Balance Reporting

Must report actual Tier-1/Tier-2 distribution per condition:

```
| Condition | Tier 1 | Tier 2 | Total |
|-----------|--------|--------|-------|
| A         | actual | actual | actual |
| B1        | actual | actual | actual |
| B2        | actual | actual | actual |
```

If imbalance exists → report as limitation. Do NOT attribute time difference to Cue if Tier imbalance is a plausible alternative.

## 9. Timing

### Definition (FROZEN)

```
case_open (loadCase completes, timer starts)
  → participant inspects evidence
  → participant clicks decision button (timer stops)
  → decision_time = (stop - start) / 1000 seconds
```

### Technical Latency

```
Image rendering: ~50-200ms for Tier-1 cases (base64 decode + browser render)
Tier-2 cases: no image → no render delay

This latency is INCLUDED in decision_time.
Do NOT subtract per-condition.
Report as limitation: Tier-1 timing may be inflated by render delay.
```

## 10. abstraction_burden

```
abstraction_burden = null (NOT_MEASURED)

PROHIBITED in analysis:
  - A HIGH proportion
  - B1 MEDIUM proportion
  - B2 LOW proportion
  - condition × abstraction_burden
  - Any cognitive burden conclusion from this field

This field is retained in schema for compatibility but must be null in all records.
```

## 11. Statistical Language

```
This is an exploratory pilot (n=15 minimum).

ALLOWED:
  - descriptive statistics (mean, median, distribution)
  - within-participant difference
  - effect size (if sample allows)
  - individual variability
  - per-case-type breakdown
  - "expected-direction reduction"

PROHIBITED:
  - "statistically significant"
  - "proven"
  - "generalizes"
  - "universally"
  - p-value as proof
```

## 12. Success Criteria

### PASS (ALL must hold)

```
Human Effort: B2 < B1 (expected-direction, cue-available cases)
Decision Quality: B2 ≥ B1 (correctness not lower)
Boundary Safety: UNKNOWN(B2) not artificially lower
Automation Bias: no AUTOMATION_BIAS_EVENT pattern
Evidence provenance: intact
```

### NOT Success

```
If time ↓ but quality ↓ → Distillation benefit NOT established.
If UNKNOWN↓ and correctness↓ → AUTOMATION_BIAS risk.
If only time↓ → insufficient; must check all criteria.
```

## 13. Learning Boundary

```
Even if experiment PASS:
  → Evidence Distillation has experimental support
  → NOT "DICE is learning"
  → NOT "Human feedback creates reusable knowledge"
  → NOT "Iterative Learning = TRUE"

This experiment does NOT test Feedback → Reusable Signal → Future Case Reuse.
ITERATIVE_LEARNING = INSUFFICIENT_EVIDENCE (regardless of outcome).
```

## 14. Participant Isolation

```
Participant A's results must NOT change Participant B's:
  - case assignment
  - cue content
  - GT
  - evidence
  - UI
  - condition

No real-time system updates from participant feedback.
Human feedback is append-only (recorded, not applied).
```

## 15. Data Boundary

```
DRYRUN_001 → implementation verification ONLY
  → Excluded from formal analysis
  → Never mixed with formal participant data

Formal participants: P001, P002, ...
  → Scientific analysis dataset
```
