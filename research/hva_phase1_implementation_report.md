# HVA Phase 1 Implementation Report

**Date**: 2026-09-17
**Status**: PASS
**Scope**: Phase 1 Minimal Prototype C

---

## 1. Executive Summary

```
IMPLEMENTATION_STATUS = PASS
LEARNING_LEVEL = L3_CANDIDATE_DISCOVERY
FROZEN_BASELINE = INTACT (drift=0)
DICE_CORE_DRIFT = 0
SEMANTIC_LEAKAGE = 0
AUTHORITY_LEAKAGE = 0
STOP = TRUE
```

Phase 1 Minimal Prototype C has been implemented and all 15 acceptance criteria passed.

The implementation proves the core hypothesis: **Human Feedback can be linked to Evidence and grouped by structural similarity into Signal Candidates.**

### What Was Built

| Component | Count | Source |
|---|---|---|
| Evidence Packs (L0-L1) | 45 | machine_eval + GT |
| FeedbackRecords | 100 | 45 GT + 55 L5 |
| Evidence Signatures (S3) | 100 | from FeedbackRecords |
| SignalCandidates | 10 | grouped by S3 signature |

### Key Results

- 10 unique S3 signatures across 100 FeedbackRecords
- 8 SignalCandidates with ≥2 unique cases (reusable candidates)
- 2 SignalCandidates with single case (correctly marked SINGLE_CASE_NOT_CANDIDATE)
- 2 SignalCandidates with BOUNDARY_REVIEW_REQUIRED (conflict or negative cases detected)
- 6 SignalCandidates with INDEPENDENCE_VERIFIED
- Cross-document independence detected in 6/8 reusable candidates
- Same-page clustering detected (SC-04: resnet p6 has 2 cases, efficientnet p9 has 2 cases)

---

## 2. Implementation Scope

```
Built:
  ✓ FeedbackRecord — 100 records (45 GT + 55 L5)
  ✓ Evidence Pack L0-L1 — 45 packs
  ✓ S3 Evidence Signature — 6 boolean fields, no content_type
  ✓ SignalCandidate — 10 candidates with state machine

NOT built (out of scope):
  ✗ Counterexample Search (Phase 1.5)
  ✗ Human Boundary Validation (Phase 2)
  ✗ ValidatedSignal (Phase 2)
  ✗ Future Case Replay (Phase 2)
```

---

## 3. Input Sources

| Source | File | Hash | Role |
|---|---|---|---|
| machine_eval | is11_machine_evaluation_results.json | 437aa665210ccd04 | Evidence Source of Truth |
| GT | is11_semantic_ground_truth.json | 7349963d0d23b5ef | Human Ground Truth + text for period/capital |
| L5 | experiment_results_live.json | (experiment record) | Human behavior (decision, evidence_viewed) |
| TLD | table_line_detector.py | 022f5c21e872ad9e | Frozen baseline (verified unchanged) |

**L5 cues were NOT used as evidence source.** All evidence_snapshot fields come from machine_eval.

---

## 4. Data Contracts

### 4.1 FeedbackRecord

```
Fields:
  record_id: str — unique identifier
  case_id: str — IS-11 case ID
  source: "GT" | "L5" — feedback source
  human_id: str — "GT_REVIEWER" or L5 participant ID
  human_decision: "KEEP_SEPARATE" | "MERGE" | "UNKNOWN"
  evidence_snapshot: dict — frozen from machine_eval (9 fields)
  evidence_viewed: null (GT) | dict (L5: levels, fields, time, engagement)
  provenance: dict — machine_eval_hash + tld_hash + gt_hash + source + timestamp
  conflict: bool — reviewer disagreement
  adjudicated: bool — GT level 2 adjudicated

Evidence Snapshot (9 fields, all from machine_eval):
  is_in_table, different_cell, is01_a, is02_b,
  text_a_ends_period, text_b_starts_capital,
  machine_decision, document_id, page

NOT included (forbidden):
  rationale, rule, confidence, score, recommendation
```

### 4.2 Evidence Pack L0-L1

```
L0: text_a, text_b, page, document_id
L1: tld_in_table, tld_different_cell, is01_number, is02_text,
    text_a_ends_period, text_b_starts_capital,
    machine_decision, machine_decision_label

machine_decision_label format: "Machine Decision (may be wrong): {decision}"

Forbidden labels verified absent:
  Recommended, Suggested, Correct Answer, Should be, Likely Correct
```

### 4.3 S3 Evidence Signature

```
6 boolean fields:
  is_in_table, different_cell, is01_a, is02_b,
  text_a_ends_period, text_b_starts_capital

NOT included:
  content_type (64% ambiguous, not derivable — HVA-05)
  machine_decision (Machine Interpretation, not Evidence)
  h_gap, dy, etc. (P2 geometry, not in machine_eval — HVA-04 GAP-2)
```

### 4.4 SignalCandidate

```
Fields:
  signal_id, signature, source_cases, source_feedback_records
  positive_cases, negative_cases, unknown_cases, conflict_cases
  has_conflict, has_negative, majority_decision
  independence: independent_count, independence_ratio, same_page_clusters, cross_document
  engagement_stats: snap_count, deep_count, no_interaction_count
  status, provenance

Status state machine:
  SINGLE_CASE_NOT_CANDIDATE (1 unique case)
  DISCOVERED (1 record)
  REPEATED (≥2 records, <2 independent doc-page groups)
  INDEPENDENCE_VERIFIED (≥2 records, ≥2 independent groups, no conflict/negative)
  BOUNDARY_REVIEW_REQUIRED (has conflict or negative cases)

Forbidden fields verified absent:
  decision, selection, routing, ranking, score, confidence,
  recommendation, execution_plan, fallback, retry, override, correction,
  rule, auto_validated, validated, registered, active
```

---

## 5. SignalCandidate Results

### 5.1 Status Distribution

| Status | Count | Description |
|---|---|---|
| INDEPENDENCE_VERIFIED | 6 | ≥2 cases, ≥2 independent groups, no conflict |
| BOUNDARY_REVIEW_REQUIRED | 2 | Has conflict or negative cases |
| SINGLE_CASE_NOT_CANDIDATE | 2 | Only 1 unique case |

### 5.2 Key SignalCandidates

#### SC-04 (SIG-01: TABLE_NUMERIC_DIFF_CELL)

```
Signature: (True, True, True, False, False, False)
Cases: 5 (AMB-024, 034, 074, 346, 350)
All KEEP_SEPARATE, consistent
Status: INDEPENDENCE_VERIFIED
Independence: ratio=0.6, 3 independent groups
Same-page clusters: is11_resnet_p6=2, is11_efficientnet_p9=2
Cross-document: YES (3 documents)
→ HVA-02 finding confirmed: 5 cases but independence_ratio=0.6 (same-page clustering detected)
→ Correctly does NOT auto-validate (Phase 1 stops at INDEPENDENCE_VERIFIED)
```

#### SC-05 (SIG-02: SENTENCE_BOUNDARY_PERIOD_CAPITAL)

```
Signature: (False, False, False, True, True, True)
Cases: 3 (AMB-375, 418, 519)
All KEEP_SEPARATE (adjudicated), has_conflict=True
Status: BOUNDARY_REVIEW_REQUIRED
Conflict cases: AMB-375, 418, 519 (all adjudicated — reviewer disagreement)
Independence: ratio=1.0, 3 independent groups, 2 documents
→ HVA-02 finding confirmed: adjudicated cases correctly flagged as conflict
→ Correctly routed to BOUNDARY_REVIEW_REQUIRED (not auto-validated)
```

#### SC-02 (Figure Caption Conflict)

```
Signature: (False, False, False, True, False, True)
Cases: 6 (AMB-262, 380, 414, 422, 457, 462)
Positive: 4 KEEP_SEPARATE (AMB-262, 380, 457, 462)
Negative: 2 MERGE (AMB-414, 422 — figure captions)
Status: BOUNDARY_REVIEW_REQUIRED
→ Negative cases (MERGE) correctly detected
→ Same signature, different decisions → boundary review required
→ This is the conflict group HVA-05 identified: 4 KS + 2 MERGE
```

#### SC-01 (Largest Group — TLD Failure Cases)

```
Signature: (False, False, False, False, False, False)
Cases: 13 (all TLD-failure cases where is_in_table=False, is01_a=False, is02_b=False)
All KEEP_SEPARATE, consistent
Status: INDEPENDENCE_VERIFIED
Independence: ratio=0.31, 4 independent groups
Same-page clusters: multiple
→ Largest group — 13 cases with identical "no signal" signature
→ These are all TLD failure cases (DCE-06 Mechanism 1)
→ Correctly grouped but independence_ratio=0.31 (LOW_INDEPENDENCE)
```

### 5.3 SIG Mapping Validation

| HVA-02 Signal | S3 Signature | Maps to | Status | Correct? |
|---|---|---|---|---|
| SIG-01 (table numeric diff cell) | (T,T,T,F,F,F) | SC-04 | INDEPENDENCE_VERIFIED | ✓ |
| SIG-02 (period+capital) | (F,F,F,T,T,T) | SC-05 | BOUNDARY_REVIEW_REQUIRED | ✓ |
| SIG-07 (AMB-032 distillation) | (T,T,F,F,F,F) | SC-06 | INDEPENDENCE_VERIFIED | ✓ |
| SIG-08 (AMB-375 boundary) | = SIG-02 | SC-05 | BOUNDARY_REVIEW_REQUIRED | ✓ |

All 4 HVA-02 signals correctly mapped to SignalCandidates with appropriate statuses.

---

## 6. GAP-4 Verification (L5 vs machine_eval)

### AMB-032 Case

```
L5 experiment data:
  has_tld: False
  TLD cues: is_in_table=None, different_cell=None

machine_eval:
  is_in_table: True
  different_cell: True

FeedbackRecord.evidence_snapshot (from machine_eval):
  is_in_table: True ✓
  different_cell: True ✓

→ Evidence Pack L1 shows: tld_in_table=True, tld_different_cell=True
→ Human would see TLD evidence in L1 (fixes AMB-032 Evidence Distillation Gap)
→ GAP-4 resolution verified: machine_eval is source, not L5 cues
```

---

## 7. Acceptance Criteria Results

| # | Criterion | Result |
|---|---|---|
| 1 | Deterministic | PASS |
| 2 | Evidence Source = machine_eval | PASS |
| 3 | Snapshot reconstructable | PASS |
| 4 | Hash mismatch → SNAPSHOT_STALE | PASS |
| 5 | S3 fixed 6 fields | PASS |
| 6 | content_type does not exist | PASS |
| 7 | provenance complete | PASS |
| 8 | semantic_leakage = 0 | PASS |
| 9 | authority_leakage = 0 | PASS |
| 10 | Human Decision not modified | PASS |
| 11 | Single case not Reusable Candidate | PASS |
| 12 | Cross-document independence detectable | PASS |
| 13 | Categories not compressed | PASS |
| 14 | Frozen baseline drift = 0 | PASS |
| 15 | DICE Core byte-identical | PASS |

**ALL 15 CRITERIA PASSED.**

---

## 8. Output Files

```
tmp/hva_phase1/
├── implement.py                 (implementation script)
├── evidence_packs.json          (45 packs, 22.9KB)
├── feedback_records.json        (100 records, 90.6KB)
├── evidence_signatures.json     (100 signatures, 35.1KB)
├── signal_candidates.json       (10 candidates, 18.2KB)
└── verification.json            (acceptance criteria, 0.9KB)
```

---

## 9. What This Proves

```
PROVEN:
  ✓ Human Feedback can be linked to Evidence (FeedbackRecord with evidence_snapshot)
  ✓ Evidence can be organized for Human (Evidence Pack L0-L1)
  ✓ Structural fingerprint can be extracted (S3 Evidence Signature)
  ✓ Similar cases can be grouped (SignalCandidate with recurrence + independence)
  ✓ Conflict and negative cases are detected (BOUNDARY_REVIEW_REQUIRED)
  ✓ Same-page clustering is detected (independence_ratio)
  ✓ Single cases do not form Reusable Candidates
  ✓ Frozen baseline is intact (0 drift)
  ✓ No semantic leakage (0 violations)
  ✓ No authority leakage (0 violations)

NOT PROVEN (out of scope):
  ✗ Signal Validity (requires Human Boundary Validation — Phase 2)
  ✗ Future Case Reuse (requires Future Case Replay — Phase 2)
  ✗ Human Effort Reduction (requires HRR measurement — Phase 2)
  ✗ Learning Success (requires L4-L6 — Phase 2+)

LEARNING_LEVEL = L3_CANDIDATE_DISCOVERY
```

---

## 10. Governance Gate

```
IMPLEMENTATION_STATUS = PASS
LEARNING_LEVEL = L3_CANDIDATE_DISCOVERY
FROZEN_BASELINE = INTACT
DICE_CORE_DRIFT = 0
SEMANTIC_LEAKAGE = 0
AUTHORITY_LEAKAGE = 0

DICE_CORE_MODIFICATION = NO
P1_P7_MODIFICATION = NO
TLD_MODIFICATION = NO
IS11_MODIFICATION = NO
GT_MODIFICATION = NO
LLM = NO
NEW_OBSERVATION = NO
NEW_MODULE = NO
NEW_ENGINE = NO
RUNTIME_CHANGE = NO
CAPABILITY_CHANGE = NO

FROZEN_BASELINE = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d)
PRODUCTION = FALSE
STOP = TRUE
```

---

## 11. Next Steps (NOT Authorized)

```
Phase 1.5 (Counterexample Search):
  → Add cross-corpus search (IS-11 + P7)
  → Requires GAP-3 documentation (P7 lacks TLD fields)
  → NOT authorized yet

Phase 2 (Human Boundary Validation + Future Replay):
  → Requires Human Experiment authorization
  → Requires new corpus
  → NOT authorized yet

Phase 3 (Runtime Integration):
  → Only if Phase 2 proves Learning with measured HRR
  → NOT planned

STOP = TRUE. Do not proceed without explicit authorization.
```
