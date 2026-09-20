# Minimal Pre-Implementation Correction Log

## L5 Evidence Distillation → Human Effort Reduction Experiment

**Date**: 2026-09-12
**Basis**: `tmp/l5_evidence_distillation_preimplementation_audit.md`
**Action**: Apply minimal corrections to resolve 3 HIGH blocking issues + 3 MEDIUM/LOW issues
**Mode**: READ-ONLY + DESIGN CORRECTION ONLY

---

## Correction 1: Three-Condition Design (Resolves Attribution Confound)

### Audit Issue

**BLOCKING ISSUE #1 (HIGH)**: Original design B = (A - 7 fields) + 4 cues confounded Information Deletion with Evidence Distillation. Could not attribute time reduction to cue vs field removal.

### Original Design

```
Condition A: 15 fields + image
Condition B: 8 fields + 4 cues + image
```

### Correction

```
Condition A:  15 fields + image (full baseline)
Condition B1: 8 fields + image (reduced, no cues — isolates Information Reduction)
Condition B2: 8 fields + 4 cues + image (reduced + cues — isolates Evidence Distillation)
```

### Scientific Rationale

B1 and B2 share identical field sets. The only difference is Evidence Cue. This provides clean causal isolation:
- A → B1: measures Information Reduction effect
- B1 → B2: measures Evidence Distillation effect (PRIMARY)
- A → B2: measures combined effect

Without B1, any time reduction in B could be from field deletion OR cue addition — unattributable.

### Attribution Impact

```
BEFORE: Attribution validity = FAIL (confounded)
AFTER:  Attribution validity = PASS (B1 vs B2 isolates distillation)
```

### Automation-Bias Impact

No direct impact on automation bias measurement, but cleaner attribution helps interpret whether cue-related behavior changes are from cue presence or field absence.

### Case-Set Changes

Requires 3 matched case sets (X, Y, Z) instead of 2 (X, Y). 50% more cases needed per participant.

### Remaining Limitations

- n increases from 10 to 15 minimum (3 groups × 5)
- More complex counterbalancing (Latin Square vs simple AB/BA)
- Transfer learning risk remains MEDIUM

---

## Correction 2: same_style HIDDEN_NOT_DELETED (Resolves Class M Loss)

### Audit Issue

**NON-BLOCKING ISSUE #4 (MEDIUM)**: same_style (Class M, MEDIUM loss risk) was LOST in original Condition B. n=1 (P01) insufficient to prove it is universally unused by all participants.

### Original Design

```
same_style: REMOVED from Condition B
```

### Correction

```
same_style: HIDDEN_NOT_DELETED
  B1 main view: hidden
  B1 progressive disclosure: available
  B2 main view: hidden
  B2 progressive disclosure: available
  Underlying evidence: intact (frozen P3)
```

### Scientific Rationale

- same_style is Class M (supporting evidence) — could be decision-relevant for some participants
- n=1 cannot prove it is universally unused
- Progressive Disclosure preserves information access without adding main-view noise
- If participant needs style info, they can expand the progressive disclosure panel
- Tracking `progressive_disclosure_used` and `progressive_disclosure_fields` records if style was accessed

### Attribution Impact

Ensures no information is truly lost. If B2 is faster than B1, it cannot be because same_style was deleted (it wasn't — it was hidden in both).

### Automation-Bias Impact

None.

### Case-Set Changes

None.

### Remaining Limitations

- Progressive disclosure adds a small UI complexity
- Must track which hidden fields were accessed (schema extension)
- If many participants access same_style via progressive disclosure, it should be reconsidered for main view

---

## Correction 3: Automation Bias Redesign (Resolves Invalid Measurement)

### Audit Issue

**BLOCKING ISSUE #2 (HIGH)**: Original design used arbitrary "Override ≥ 50% = SAFE" threshold. Only 2 true cue-GT conflict cases (insufficient). 0 System≠GT cases. Could not meaningfully measure automation bias.

### Original Design

```
Override Rate ≥ 50% = SAFE
Override Rate 20-50% = CONCERN
Override Rate < 20% = DANGER
```

### Correction

```
DELETED: Override ≥ 50% = SAFE
DELETED: Any preset safety threshold

ADOPTED: Four descriptive behavioral metrics

WCAR (Wrong-Cue Acceptance Rate):
  When Cue≠GT, Human accepts wrong Cue direction / total conflict cases

COR (Correct Override Rate):
  When Cue≠GT, Human correctly overrides / total conflict cases

EIR (Evidence Inspection Rate):
  Human inspected underlying evidence before decision / total cases

CFR (Cue-Following Rate):
  Human decision matches Cue-implied direction / total cases

AUTOMATION_BIAS_EVENT:
  TRUE when: Cue≠GT + Human did NOT inspect evidence + Human accepted Cue + Human decision≠GT
  MUST be recorded, NOT hidden
```

### Scientific Rationale

- Override Rate is a behavior indicator, not a safety proof
- Arbitrary thresholds (50%) have no theoretical basis for exploratory pilot
- WCAR directly measures harm: did Human accept a wrong cue?
- EIR distinguishes "informed acceptance" from "blind acceptance"
- Per-case recording enables case-level error analysis
- No threshold means: report what happened, don't pre-define "safe"

### Attribution Impact

Cleaner: if B2 has high WCAR, it means cue specifically caused wrong decisions (not field reduction, since B1 has no cue).

### Automation-Bias Impact

```
BEFORE: AUTOMATION_BIAS_MEASUREMENT = FAIL (arbitrary threshold, 2 cases)
AFTER:  AUTOMATION_BIAS_MEASUREMENT = PASS (WCAR/COR/EIR/CFR + 5 conflict cases after preparation)
```

### Case-Set Changes

- Must add ≥3 new cue-conflict / System≠GT cases (total ≥5)
- AMB-414/422 reclassified (NOT conflicts — cue is correct)
- AMB-313/462 verified as TRUE conflicts (Cue 1 "no structure" vs GT KEEP_SEPARATE)

### Remaining Limitations

- 5 conflict cases is still small for WCAR stability
- EIR depends on schema implementation (tracking evidence inspection)
- Individual variation may be large with n=15

---

## Correction 4: Case Composition (Resolves Incomplete Corpus)

### Audit Issue

**BLOCKING ISSUE #3 (HIGH)**: 0 N-type cases, 0 System≠GT cases, 0 UNKNOWN baseline. Cannot test cue on confusing cases, cannot measure automation bias, cannot verify UNKNOWN preservation.

### Original Design

```
P: 15, N: 0, B: 2, C: 4 (2 true conflicts), S: 0, U: 0
```

### Correction

```
P: 13 (AMB-414/422 reclassified to P-type MERGE) + 5 new = 18
N: 0 + 5-8 new = 5-8
B: 2 + 3 new = 5
C: 2 (AMB-313/462, true conflicts) + 2 new = 4
S: 0 + 3-5 new = 3-5
U: 0 + 2 new = 2

Total new cases needed: 20-25
```

### Scientific Rationale

- **N-type**: Without negative cases, cannot test if cue INDUCES errors on confusing cases
- **S-type (System≠GT)**: Without cue-GT conflict cases, cannot measure WCAR
- **U-type**: Without UNKNOWN baseline, cannot verify B doesn't suppress uncertainty
- **AMB-414/422 reclassification**: These are NOT cue-conflict cases (cue "starts with FIG." is correct, GT=MERGE). Classifying them as conflicts would inflate WCAR denominator with non-conflict cases.

### Attribution Impact

Complete case composition ensures all aspects of cue effect are tested: speedup (P), error induction (N), boundary preservation (B/U), automation bias (C/S).

### Automation-Bias Impact

With ≥5 true conflict cases, WCAR becomes meaningfully measurable.

### Case-Set Changes

20-25 new cases must be prepared from new documents, with GT adjudication. This is the largest preparation effort.

### Remaining Limitations

- New cases not yet prepared
- GT adjudication required for all new cases
- Case diversity depends on document availability

---

## Correction 5: Statistical Language (Resolves Premature Claims)

### Audit Issue

**NON-BLOCKING ISSUE #5 (LOW)**: Original design used "significantly lower" implying statistical significance. At n=10 (now n=15), cannot claim significance.

### Original Design

```
PASS: "decision time significantly lower in B vs A"
FAIL: "No significant time difference"
```

### Correction

```
PASS: "B2 shows expected-direction reduction in decision time compared to B1"
FAIL: "B2 shows no observable direction difference from B1"

Report: mean, median, distribution, within-participant difference, effect size, individual variability
DO NOT: p-value as proof, "statistically significant", "proven reduction"

NO_STATISTICAL_GENERALIZATION at n=15 (exploratory pilot)
```

### Scientific Rationale

- Exploratory pilot cannot pre-claim significance
- "Expected-direction" is a hypothesis, not a conclusion
- Actual significance requires n≥30 per condition and pre-registered analysis plan

### Remaining Limitations

- n=15 remains exploratory; results indicate direction, not proof
- Effect size may be unstable with small sample

---

## Correction 6: AMB-414/422 Reclassification + Latin Square

### Audit Issue

**NON-BLOCKING ISSUE #6 (LOW)**: AMB-414/422 misclassified as C-type conflict cases. Also, 3-condition design requires Latin Square counterbalancing.

### Original Design

```
AMB-414: C-type (confounding)
AMB-422: C-type (confounding)
Counterbalancing: 2-group AB/BA
```

### Correction

```
AMB-414: P-type MERGE (cue correct, not conflict)
AMB-422: P-type MERGE (cue correct, not conflict)
Counterbalancing: 3-group Latin Square (A/B1/B2 × X/Y/Z)
```

### Scientific Rationale

- AMB-414/422: Cue 7 ("starts with FIG.") is factually correct and supports GT=MERGE. These are NOT cue-conflict cases. Including them as conflicts would dilute WCAR measurement.
- Latin Square: 3 conditions require 3×3 counterbalancing to control order effects across all condition sequences.

### Remaining Limitations

- Latin Square requires 3 matched case sets (more case preparation)
- 3 groups × n≥5 = n≥15 minimum

---

## Correction Summary

| # | Issue | Severity | Correction | Status |
|---|---|---|---|---|
| 1 | Attribution confound | HIGH | 3-condition design (A / B1 / B2) | ✅ RESOLVED |
| 2 | same_style LOST | MEDIUM | HIDDEN_NOT_DELETED (progressive disclosure) | ✅ RESOLVED |
| 3 | Automation bias invalid | HIGH | WCAR/COR/EIR/CFR, no threshold | ✅ RESOLVED |
| 4 | Case corpus incomplete | HIGH | Add N/B/S/U cases, reclassify AMB-414/422 | ✅ RESOLVED (design) |
| 5 | Statistical language | LOW | "expected-direction" not "significant" | ✅ RESOLVED |
| 6 | AMB-414/422 + counterbalancing | LOW | Reclassify + Latin Square | ✅ RESOLVED |

### All 6 corrections applied to design documents. None implemented in code/UI/data.

---

## Remaining Limitations (After Corrections)

| Limitation | Type | Resolution Path |
|---|---|---|
| New cases not prepared (20-25) | Preparation | Requires case extraction + GT adjudication |
| Participants not recruited (n≥15) | Preparation | Requires recruitment authorization |
| UI for 3 conditions not implemented | Implementation | Requires UI development authorization |
| Recording schema not implemented | Implementation | Requires schema development authorization |
| GT for new cases not adjudicated | Preparation | Requires GT adjudication authorization |
| n=15 is exploratory, not generalizable | Statistical | Inherent to pilot scale; report as exploratory |
| Image confound persists | Construct | All conditions have image; cue may be image-redundant |
| TLD false negatives (2 cases) | External | C-type + S-type cases test override behavior |

---

## Governance

```
READ_ONLY = TRUE
DESIGN_CORRECTION_ONLY = TRUE

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

FILES_MODIFIED:
  - tmp/l5_evidence_distillation_effort_reduction_experiment.md (updated to v2_corrected)
  - tmp/l5_evidence_distillation_effort_reduction_experiment.json (updated to v2_corrected)

FILES_CREATED:
  - tmp/l5_evidence_distillation_minimal_correction_log.md (this file)

FROZEN_BASELINE = INTACT
PRODUCTION = FALSE
RUNTIME_AUTHORITY = ZERO
ITERATIVE_LEARNING = INSUFFICIENT_EVIDENCE
STOP = TRUE
```
