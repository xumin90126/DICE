# HVA Phase 2 Plan — Signal Validation & Unseen Case Replay

**Date**: 2026-09-17
**Scope**: SC-05 Human Boundary Validation → ValidatedSignal → Unseen Case Replay

---

## 1. Research Question

> 一个由 Human Feedback 形成的 SignalCandidate，经过 Human Validation 后，是否能够在真正的 Unseen Case 上复用？

## 2. Target Candidate: SC-05

```
Signal ID: SC-05
Signature: (is_in_table=False, different_cell=False, is01_a=False, is02_b=True,
            text_a_ends_period=True, text_b_starts_capital=True)
Pattern: text_a ends with period + text_b starts with capital + not numeric + has text

Source Cases (3, all adjudicated):
  IS11-AMB-375: "[23]." / "Each" → KEEP_SEPARATE (Reviewer A: KS, B: MERGE)
  IS11-AMB-418: "left panel." / "The" → KEEP_SEPARATE (Reviewer A: KS, B: MERGE)
  IS11-AMB-519: "open-source LLMs." / "To embrace" → KEEP_SEPARATE (Reviewer A: KS, B: MERGE)

Status: BOUNDARY_REVIEW_REQUIRED (has_conflict=True, all 3 adjudicated)
Independence: ratio=1.0, 2 documents (is11_cs_001, is11_med_001)
```

## 3. Human Boundary Validation Design

### Human sees:
```
Positive cases (3): All KEEP_SEPARATE (adjudicated)
  - All have reviewer disagreement (A: KS, B: MERGE)
  - Adjudicator resolved: period + capital → KEEP_SEPARATE

Conflict: 3/3 cases have reviewer disagreement

Counterexamples: NONE in IS-11 (ceiling effect within IS-11)
```

### Human question:
> "period + capital pattern 是否足以支持 KEEP_SEPARATE 信号？"

### Human options:
- SUPPORTED: Pattern sufficient → proceed to replay
- UNSUPPORTED: Pattern insufficient → signal fails
- UNKNOWN: Cannot determine → signal stays UNKNOWN
- OUT_OF_SCOPE: Beyond review scope

### Simulated Human Validation (based on existing adjudication data):

Since all 3 source cases were already adjudicated by a human adjudicator who ruled
"period + capital → KEEP_SEPARATE", we use the adjudicator's decision as the
Human Boundary Validation result.

**HOWEVER**: The adjudicator's decision was made WITHOUT seeing counterexamples
from P7. The replay will reveal whether this decision holds on unseen data.

Validation result: SUPPORTED (with boundary note: "adjudicated without counterexamples")

## 4. Unseen Case Replay Design

### Unseen Cases: P7 (13 cases matching 4-field signature)

```
Match criteria: is01_a=False, is02_b=True, text_a_ends_period=True, text_b_starts_capital=True
(P7 lacks is_in_table/different_cell — GAP-3, PARTIAL 4-field match)

Truly unseen:
  - 0 case_id overlap with IS-11
  - 0 document overlap with IS-11
  - 4 new documents: ind_arxiv_2402, ind_arxiv_bio2, ind_qbio_genomics, ind_qbio_rna

GT distribution: 8 KEEP_SEPARATE, 5 MERGE (38% negative!)
Boundary classes: BODY_TEXT_CONTINUATION(6), REFERENCE_LIST_ENTRY(6), OTHER_AMBIGUOUS(1)
```

### Replay Process:

```
For each unseen P7 case:
  1. Extract S3 signature (4 available fields)
  2. Match against SC-05 signature
  3. If match: signal predicts KEEP_SEPARATE (majority decision from source)
  4. Compare signal prediction with P7 GT
  5. Classify: TRUE_POSITIVE / FALSE_POSITIVE / TRUE_NEGATIVE / UNKNOWN
```

### Replay Output:
```
SIGNAL_MATCH: Signature matches → signal predicts KEEP_SEPARATE
SIGNAL_NOT_MATCH: Signature doesn't match → OUT_OF_SCOPE
SIGNAL_UNRESOLVED: Cannot determine (partial match only)
```

### Baseline vs Signal-assisted Comparison:

```
Baseline: Human reviews unseen case with Evidence Pack L0-L1 only
Signal-assisted: Human reviews unseen case with Evidence Pack + Signal preconditions

Metrics:
  1. decision_time
  2. expansion_count
  3. levels_viewed
  4. human_decision
  5. correctness
  6. signal_match
  7. signal_failure
  8. human_override

NOTE: Phase 2 does NOT run a new Human Experiment.
We use existing P7 GT as proxy for Human decision.
HRR measurement requires a future authorized experiment.
```

## 5. Data Structures

### ValidatedSignal
### ReplayCase
### ReplayResult

(defined in implementation)

## 6. Stop Conditions

```
STOP if:
  - Unseen Case count < 5 → INSUFFICIENT_COVERAGE
  - Signal FP rate > 30% → Signal compromised
  - Conflict cannot be explained → UNKNOWN
  - Signal depends on source-specific artifact → FAILURE

DO NOT:
  - Modify Signal to improve results
  - Modify GT to let Signal pass
  - Expand Signal definition
  - Add fields to Signature
```

## 7. Frozen Hashes

```
TLD:          022f5c21e872ad9e
GT:           7349963d0d23b5ef
machine_eval: 437aa665210ccd04
```
