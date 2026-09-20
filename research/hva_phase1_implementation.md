# HVA Phase 1 Implementation Plan

**Date**: 2026-09-17
**Authorization**: HVA-05 READY, explicit user authorization granted
**Scope**: Phase 1 Minimal Prototype C

---

## 1. Implementation Scope

```
Components:
  1. FeedbackRecord — links Human decision to frozen evidence_snapshot
  2. Evidence Pack L0-L1 — structured evidence presentation
  3. S3 Evidence Signature — 6 boolean structural fingerprint
  4. SignalCandidate — groups cases with same signature

NOT included:
  - Counterexample Search (Phase 1.5)
  - Human Boundary Validation (Phase 2)
  - ValidatedSignal (Phase 2)
  - Future Case Replay (Phase 2)
```

## 2. Input Sources

| Source | File | Hash | Role |
|---|---|---|---|
| machine_eval | tmp/is11_machine_evaluation_results.json | 437aa665210ccd04 | Evidence Source of Truth |
| GT | tmp/is11_semantic_ground_truth.json | 7349963d0d23b5ef | Human Ground Truth + text_a/b for period/capital |
| L5 | tmp/l5_evidence_distillation_experiment/recording/experiment_results_live.json | (experiment record) | Human behavior (decision, evidence_viewed) |
| TLD | chunker/table_line_detector.py | 022f5c21e872ad9e | Frozen baseline verification |

## 3. Data Contracts

### FeedbackRecord
```json
{
  "record_id": "FR-{source}-{case_id}[-{condition}]",
  "case_id": "IS11-AMB-XXX",
  "source": "GT" | "L5",
  "human_id": "GT_REVIEWER" | "P722" | null,
  "human_decision": "KEEP_SEPARATE" | "MERGE" | "UNKNOWN",
  "evidence_snapshot": {
    "is_in_table": bool,
    "different_cell": bool,
    "is01_a": bool,
    "is02_b": bool,
    "text_a_ends_period": bool,
    "text_b_starts_capital": bool,
    "machine_decision": str,
    "document_id": str,
    "page": int
  },
  "evidence_viewed": null | {
    "levels_viewed": int,
    "fields_expanded": [str],
    "expansion_count": int,
    "decision_time_ms": int,
    "engagement_level": "SNAP" | "DEEP"
  },
  "provenance": {
    "machine_eval_hash": "437aa665210ccd04",
    "tld_hash": "022f5c21e872ad9e",
    "gt_hash": "7349963d0d23b5ef",
    "source": str,
    "experiment_condition": str | null,
    "timestamp": str
  },
  "conflict": bool,
  "adjudicated": bool
}
```

### Evidence Pack L0-L1
```json
{
  "case_id": "IS11-AMB-XXX",
  "L0": {
    "text_a": str,
    "text_b": str,
    "page": int,
    "document_id": str
  },
  "L1": {
    "tld_in_table": bool,
    "tld_different_cell": bool,
    "is01_number": bool,
    "is02_text": bool,
    "text_a_ends_period": bool,
    "text_b_starts_capital": bool,
    "machine_decision": str,
    "machine_decision_label": "Machine Decision (may be wrong): {decision}"
  }
}
```

### S3 Evidence Signature
```json
{
  "case_id": "IS11-AMB-XXX",
  "signature": {
    "is_in_table": bool,
    "different_cell": bool,
    "is01_a": bool,
    "is02_b": bool,
    "text_a_ends_period": bool,
    "text_b_starts_capital": bool
  },
  "signature_tuple": "(bool, bool, bool, bool, bool, bool)"
}
```

### SignalCandidate
```json
{
  "signal_id": "SC-{index}",
  "signature": dict,
  "source_cases": [str],
  "source_feedback_records": [str],
  "positive_cases": [str],
  "negative_cases": [str],
  "unknown_cases": [str],
  "conflict_cases": [str],
  "has_conflict": bool,
  "independence": {
    "independent_count": int,
    "total_count": int,
    "independence_ratio": float,
    "same_page_clusters": dict,
    "cross_document": bool,
    "document_count": int
  },
  "engagement_stats": {
    "snap_count": int,
    "deep_count": int,
    "no_interaction_count": int
  },
  "status": "DISCOVERED" | "REPEATED" | "INDEPENDENCE_VERIFIED" | "BOUNDARY_REVIEW_REQUIRED",
  "provenance": {
    "machine_eval_hash": str,
    "tld_hash": str,
    "gt_hash": str,
    "timestamp": str
  }
}
```

## 4. Frozen Hashes (Pre-Implementation)

```
TLD:      022f5c21e872ad9e
GT:       7349963d0d23b5ef
machine_eval: 437aa665210ccd04
```

## 5. Output Files

```
tmp/hva_phase1/
├── feedback_records.json
├── evidence_packs.json
├── evidence_signatures.json
├── signal_candidates.json
└── verification.json
```

## 6. Acceptance Criteria

1. Deterministic — same input → same output
2. Evidence Source = machine_eval
3. Snapshot can be reconstructed
4. Hash mismatch → SNAPSHOT_STALE
5. S3 fixed 6 fields
6. content_type does not exist
7. provenance complete
8. semantic_leakage = 0
9. authority_leakage = 0
10. Human Decision not modified by Machine
11. Single case does not form Reusable Candidate
12. Cross-document independence detectable
13. positive/negative/UNKNOWN/conflict not compressed
14. Frozen baseline drift = 0
15. DICE Core behavior byte-identical
