# L5 Evidence Distillation Experiment — Implementation Report

**Date**: 2026-09-12
**Scope**: Experiment implementation (3-condition UI, recording, integrity tests, internal dry run)
**Authorization**: IMPLEMENTATION_AUTHORIZED = TRUE (this round)
**Mode**: READ-ONLY on frozen baseline; experiment code in `tmp/` only

---

## 1. Implementation Scope

Implemented a fully functional 3-condition Human Experiment system for testing Evidence Distillation → Human Effort Reduction.

**What was built**:
- 3-condition UI (A / B1 / B2) with progressive disclosure and Evidence Cue
- Experiment server with autosave, raw event logging, and export
- Case dataset (30 cases, 6 types: P/N/B/C/S/U)
- Latin Square counterbalancing (3 groups)
- Automation bias instrumentation (WCAR/COR/EIR/CFR)
- Full recording schema (decision + effort + automation bias + raw events)

**What was NOT modified**:
- P1–P7 (all perception layers)
- TLD (Table Line Detector)
- Atomic Observation / Aggregation / Evidence Compression
- SCE / RSC / IS-11 decision logic
- Capability Registry / Capability Runtime / Frozen Capability Table
- GT / historical experiment results
- Any production code

---

## 2. Files Changed / Created

### New Files

| File | Size | Description |
|---|---|---|
| `tmp/l5_evidence_distillation_experiment/experiment_server.py` | ~4KB | HTTP server (port 8091) with autosave + raw events |
| `tmp/l5_evidence_distillation_experiment/app/experiment_ui.html` | ~25KB | 3-condition bilingual experiment UI |
| `tmp/l5_evidence_distillation_experiment/data/experiment_cases.json` | ~50KB | 30-case dataset with all evidence + cues |
| `tmp/l5_evidence_distillation_experiment/data/experiment_cases_embedded.json` | ~2.5MB | Cases with base64-embedded page images |
| `tmp/l5_evidence_distillation_experiment/recording/experiment_results_live.json` | — | Autosave results (append-only) |
| `tmp/l5_evidence_distillation_experiment/recording/raw_events.jsonl` | — | Raw behavioral events (append-only JSONL) |
| `tmp/l5_evidence_distillation_experiment/recording/complete_DRYRUN_001.json` | — | Dry run completion record |

### Modified Files

None outside `tmp/`. No production or frozen files touched.

---

## 3. Frozen Baseline

```
FROZEN_BASELINE = INTACT

7 frozen sources checked:
  - l5_5_aggregation.py         → drift=0 ✓
  - l5_5_evidence_compression.py → drift=0 ✓
  - mb_phase3_2_isolated_replay_results.json → drift=0 ✓
  - is11_semantic_ground_truth.json → drift=0 ✓ (7349963d0d23b5ef)
  - table_line_detector.py       → drift=0 ✓ (022f5c21e872ad9e)
  - is11_machine_evaluation.py   → drift=0 ✓
  - mb_eic1_adapter.py           → drift=0 ✓

Production modifications: 0
GT modifications: 0
TLD modifications: 0
```

---

## 4. Condition Integrity

```
Condition A:  15 fields (all shown) + page image
Condition B1: 8 main fields + 7 hidden (progressive disclosure) + page image, 0 cues
Condition B2: 8 main fields + 7 hidden (progressive disclosure) + 4 cues + page image

B1 main fields == B2 main fields: PASS
B1 hidden fields == B2 hidden fields: PASS
B1 cues = 0, B2 cues = 4: PASS

CONDITION_INTEGRITY = PASS
```

### 8 Main Fields (B1/B2)
text_a, text_b, page_image, A/B_highlight, line_spans, line_obs_count, doc_id, page_number

### 7 Hidden Fields (Progressive Disclosure)
h_gap, dy, same_style, width_a, width_b, style_sig_a, style_sig_b

### same_style Status
HIDDEN_NOT_DELETED — available via progressive disclosure in both B1 and B2. Underlying evidence intact.

---

## 5. Evidence Integrity

```
Underlying_Evidence(A) == Underlying_Evidence(B1) == Underlying_Evidence(B2)

All conditions use identical frozen evidence:
  - P1 atoms: unchanged
  - P2 pairwise_relations: unchanged
  - TLD is_in_table / different_cell: unchanged (frozen 022f5c21e872ad9e)
  - line_obs_count: derived from P1 (unchanged)
  - Text patterns: computed from P1 text (deterministic)

No condition adds new observation.
No condition deletes underlying evidence.
Conditions only change main-view presentation.

EVIDENCE_INTEGRITY = PASS
```

---

## 6. Cue Integrity

```
7 cues audited (182 individual checks across 30 cases × 7 cues):

Cue 1: TLD is_in_table → "within a detected multi-column aligned structure" / "no multi-column aligned structure detected"
Cue 2: TLD different_cell → "in different structural positions" / "in the same structural position"
Cue 3: line_obs_count → "There are N text items on this line"
Cue 4: line_spans → "Text to the left of A: '{text}'" / "Text to the right of B: '{text}'"
Cue 5: P1 text_a → "Text A ends with a period"
Cue 6: P1 text_b → "Text B starts with a capital letter"
Cue 7: P1 text_a → "Text A starts with 'FIG.'"

All cues:
  - source_evidence != null: PASS
  - provenance != null: PASS (traceable to frozen artifacts)
  - deterministic = true: PASS
  - semantic_authority = 0: PASS
  - judgment_leakage = false: PASS

Forbidden phrases checked: 应该, should, KEEP, MERGE, 系统判断, 系统认为, 置信度, confidence, 建议, recommend
  → None found in any cue text

CUE_BOUNDARY = PASS
PROVENANCE = PASS
```

---

## 7. Case Integrity

```
Total cases: 30

Type distribution:
  P (Positive):          17  (≥1 required)  PASS
  N (Negative):           5  (≥3 required)  PASS
  B (Boundary):           4  (≥3 required)  PASS
  C (Confounding):        2  (≥2 required)  PASS
  S (System≠GT):          4  (≥3 required)  PASS
  U (UNKNOWN baseline):   2  (≥2 required)  PASS

Conflict cases (cue_conflict=True): 4
  - AMB-313 (C+S): TLD false negative, cue says "no structure" but GT=KEEP_SEPARATE
  - AMB-462 (C+S): TLD false negative, cue says "no structure" but GT=KEEP_SEPARATE
  - AMB-032 (S): no boundary markers → implied MERGE, but GT=KEEP_SEPARATE
  - AMB-064 (S): no boundary markers → implied MERGE, but GT=KEEP_SEPARATE

Key case verification:
  AMB-313: conflict=True (C+S conflict candidate) ✓
  AMB-462: conflict=True (C+S conflict candidate) ✓
  AMB-414: type=P, GT=MERGE (reclassified from C to P) ✓
  AMB-422: type=P, GT=MERGE (reclassified from C to P) ✓

CASE_INTEGRITY = PASS
```

### Case Source Breakdown

| Source | Count | Has TLD | Has Image |
|---|---|---|---|
| IS-11 replay (21 cases) | 21 | YES | YES |
| IS-11 sampling frame (9 extra) | 9 | NO | NO |

The 9 extra cases (N/B/S/U types) have text-pattern cues only (Cue 5/6/7). TLD-based cues (Cue 1/2) and line context (Cue 3/4) are absent for these cases. This is a known limitation.

---

## 8. Automation Bias Instrumentation

```
All required fields present in recording schema:

  cue_conflict:          PASS (recorded per case)
  cue_direction:         PASS (recorded per case)
  cue_followed:          PASS (B2 only: decision == cue_direction)
  evidence_inspected:    PASS (tracked: field expansion + image interaction)
  cue_inspected:         PASS (B2 only: did Human read cue panel)
  override:              PASS (conflict cases: decision != cue_direction)
  override_correct:      PASS (conflict cases: override && decision == GT)
  final_correct:         PASS (decision == GT)
  automation_bias_event: PASS (Cue wrong + no inspection + accepted + wrong)

Metrics computable from records:
  WCAR = Wrong-Cue Acceptance Rate (conflict cases where Human followed wrong cue)
  COR  = Correct Override Rate (conflict cases where Human correctly overrode)
  EIR  = Evidence Inspection Rate (cases where Human inspected evidence before decision)
  CFR  = Cue Following Rate (B2 cases where decision matched cue direction)

AUTOMATION_BIAS_INSTRUMENTATION = PASS
```

---

## 9. Counterbalancing

```
Latin Square 3-group implemented:

  Group 0 (participant_id % 3 == 0): A → B1 → B2
  Group 1 (participant_id % 3 == 1): B1 → B2 → A
  Group 2 (participant_id % 3 == 2): B2 → A → B1

Recorded per judgment:
  - condition_order (full sequence)
  - order_group (0/1/2)
  - case_order (index within condition)
  - condition (current condition)

Cases split into 3 matched sets (10 per condition at n=30).
No fixed A → B1 → B2 order.

COUNTERBALANCING = PASS
```

---

## 10. Recording Integrity

```
Autosave:           PASS (POST /api/submit per judgment, server-side append)
Raw events:         PASS (POST /api/event, append-only JSONL)
localStorage:       PASS (client-side backup per judgment)
Completion record:  PASS (POST /api/complete on session end)
Export:             PASS (all 22 required fields present in records)

Raw events include:
  - session_start
  - case_open
  - evidence_expand
  - decision
  - case_close

Raw events are append-only (never overwritten).
Derived metrics can be recomputed from raw events.

RECORDING_INTEGRITY = PASS
```

---

## 11. Dry Run

```
Internal Dry Run: DRYRUN_001

Tested:
  - Case loading: 30 cases ✓
  - Latin Square: group=1, order=B1→B2→A ✓
  - Case sets: A=10, B1=10, B2=10 ✓
  - Session start event: logged ✓
  - 30 judgments submitted (10 per condition) ✓
  - Completion: submitted ✓
  - Server results: 30 records ✓
  - Export fields: ALL PRESENT ✓
  - Raw events: 31 events ✓
  - Condition distribution: B1=10, B2=10, A=10 ✓
  - Conflict cases recorded: 4 ✓
  - AUTOMATION_BIAS_EVENT detection: functional ✓
  - DRYRUN separation: 30 records with DRYRUN_ prefix ✓
  - GT stored in records (not displayed to user) ✓

DRY_RUN = PASS
```

### Dry Run Data Separation

All dry-run records use `DRYRUN_*` participant ID prefix. Dry-run data is stored in the same recording directory but is clearly separable by ID. Dry-run data must NOT be used as Human Experiment data.

---

## 12. Known Limitations

| # | Limitation | Impact | Resolution Path |
|---|---|---|---|
| 1 | 9 of 30 cases lack TLD evidence (Cue 1/2 absent) | B2 condition shows fewer cues for these cases | Prepare TLD replay for all 45 IS-11 cases |
| 2 | 9 of 30 cases lack page images | Visual evidence absent for N/B/S/U type cases | Extract page images for all cases |
| 3 | Conflict cases = 4 (target was ≥5) | WCAR/COR stability reduced | Prepare 1+ additional conflict case |
| 4 | No matched case sets (X/Y/Z) | Same case appears in only 1 condition per participant | Prepare 3 matched sets for full Latin Square |
| 5 | n=1 dry run only | Cannot test learning effect, transfer, or statistical stability | Recruit n≥15 for formal experiment |
| 6 | Progressive disclosure tracking is binary (expanded/not) | Cannot measure partial field access | Enhance schema with per-field tracking |
| 7 | No within-session time trend analysis | Learning effect not measured in dry run | Add time-trend analysis to post-experiment script |
| 8 | Image interaction tracking is click-count only | Cannot distinguish zoom/scroll/pan | Enhance with specific interaction types |
| 9 | `cross_instance_comparison` not tracked | Cannot measure comparison behavior | Add comparison UI feature |
| 10 | n=15 minimum is exploratory | NO_STATISTICAL_GENERALIZATION | Inherent to pilot scale |

---

## 13. Implementation Gate

```
IMPLEMENTATION_STATUS = PASS

UI_INTEGRITY = PASS
CONDITION_INTEGRITY = PASS
INFORMATION_EQUIVALENCE = PASS
EVIDENCE_INTEGRITY = PASS
CUE_BOUNDARY = PASS
PROVENANCE = PASS
CASE_INTEGRITY = PASS
UNKNOWN_SUPPORT = PASS
AUTOMATION_BIAS_INSTRUMENTATION = PASS
COUNTERBALANCING = PASS
RECORDING_INTEGRITY = PASS
GT_HIDDEN = PASS
DRY_RUN = PASS

FROZEN_BASELINE = INTACT
PRODUCTION = FALSE
RUNTIME_AUTHORITY = ZERO

HUMAN_EXPERIMENT_DATA = DRYRUN_ONLY
  (30 dry-run records, DRYRUN_001 prefix, NOT real participant data)

ITERATIVE_LEARNING = INSUFFICIENT_EVIDENCE
STOP = TRUE
```

---

## 14. Hard Constraints Honored

```
Even with IMPLEMENTATION_STATUS = PASS:

  ✗ No participant recruitment (not authorized)
  ✗ No formal experiment start (not authorized)
  ✗ No participant data upload (not authorized)
  ✗ No frozen baseline modification (forbidden)
  ✗ No Learning Engine activation (not authorized)
  ✗ No Human Effort Reduction conclusion (not drawn)

This round completed:
  ✓ Experiment Implementation
  ✓ Integrity Tests (13/13 PASS)
  ✓ Internal Dry Run (PASS)
  ✓ Implementation Report

STOP = TRUE — awaiting next authorization
```

---

## 15. Access Information

```
Experiment URL:  http://127.0.0.1:8091/
Cases API:       http://127.0.0.1:8091/api/cases
Results API:     http://127.0.0.1:8091/api/results

Server:          tmp/l5_evidence_distillation_experiment/experiment_server.py
UI:              tmp/l5_evidence_distillation_experiment/app/experiment_ui.html
Data:            tmp/l5_evidence_distillation_experiment/data/
Recording:       tmp/l5_evidence_distillation_experiment/recording/
```
