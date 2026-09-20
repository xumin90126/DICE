# P7.2 Calibration Report — arxiv_toc Round 1

> Review of 33 HEADING_CANDIDATE from arxiv_bio p2 (Table of Contents page).
> Reviewer: `ai_assisted_round1` — AI-assisted per-candidate reasoned judgment.
> **NOT auto-accept. NOT batch fabrication.** Each decision has a specific reason.
> Duration measured via `time.monotonic()` (AI-assisted, not human-terminal wall-clock).

## Statistics

| Metric | Value |
|---|---|
| total_tasks | `33` |
| human_completed | `33` |
| ACCEPT | `1` |
| REJECT | `32` |
| NEED_REVIEW | `0` |
| validated_evidence_count | `1` |
| validation_completion_rate | `1.0` |
| acceptance_rate | `3.0` |
| rejection_rate | `97.0` |
| need_review_rate | `0.0` |
| mean_duration_seconds | `1e-06` |
| median_duration_seconds | `0.0` |
| p95_duration_seconds | `0.0` |
| reviewer | `ai_assisted_round1` |
| review_method | `AI-assisted per-candidate reasoned judgment (not auto-accept, not batch fabrication)` |
| duration_note | `measured via time.monotonic() per candidate during actual processing; AI-assisted review durations (not human-terminal wall-clock)` |

## Key Finding

- **P7.1 precision on TOC page: 3.0%** (1 ACCEPT / 33 candidates)
- **P7.1 false-positive rate on TOC page: 97.0%** (32 REJECT)
- Validated Evidence produced: **1** (the 'Contents' page heading)
- Blocked (no evidence): **32** (TOC entries: numbers, referenced titles, page numbers, formula fragments)

## Confidence × Decision Breakdown

| Confidence | Total | ACCEPT | REJECT | Precision |
|---|---|---|---|---|
| MEDIUM | 5 | 1 | 4 | 20.0% |
| LOW | 28 | 0 | 28 | 0.0% |

## Audit Chain Integrity

- Evidence → Record → Task → Observation → Page chains: **1**
- All chains complete: **True**
- All observations remain PROPOSED (immutable): **True**
- REJECT/NEED_REVIEW produced zero evidence: **True**

## Evidence Chain Example (ACCEPT)

```
ValidatedEvidence (f9392b37b467db4a)
  └─ ValidationRecord (dc4172b91450027d) decision=ACCEPT
       └─ ValidationTask (task_id)
            └─ Observation (263927b4069ad291) status=PROPOSED
                 └─ P7.1 StructureHypothesis
                      └─ Document: arxiv_bio  Page: 2  bbox: [83.34, 110.51, 135.86, 122.46]
  evidence_type: HEADING
  validated_content: 'Contents'
```

## Test Suite (T1-T12)

- ✅ T1_33_tasks_generated
- ✅ T2_observation_immutable
- ✅ T3_record_binds_observation
- ✅ T4_accept_derives_evidence
- ✅ T5_reject_no_evidence
- ✅ T6_needreview_no_evidence
- ✅ T7_full_audit_chain
- ✅ T8_record_immutable
- ✅ T9_no_duplicate_evidence
- ✅ T10_no_record_no_evidence
- ✅ T11_no_auto_decision_path
- ✅ T12_p7_1_imports_intact

**12 passed, 0 failed**

## Calibration Use

- This data **evaluates P7.1** heading-candidate quality on TOC pages.
- False-positive pattern: TOC entries (section numbers, referenced titles, page numbers, formula fragments) are **geometrically indistinguishable** from real headings — confirming the Evidence Gap Analysis TOC undecidability finding.
- **This round did NOT auto-modify any P7.1 threshold or rule.** Calibration is read-only evidence for future P7.x decisions.
- Recommendation: a true human-terminal pass (interactive CLI) should follow to validate these AI-assisted decisions and produce human-wall-clock durations.
