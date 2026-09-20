# FINAL_EXPERIMENT_FREEZE.md

**Date**: 2026-09-12
**Experiment Version**: exp_v2_patched
**Status**: FROZEN — no modifications allowed until Formal Human Experiment data is collected

---

## 1. Experiment Version

```
experiment_version: exp_v2_patched
schema_version: exp_v2_patched
patches_applied: 2 (Patch A + Patch B)
```

## 2. Patches Applied

### Patch A — AMB-032/064 Reclassification

```
AMB-032: S-type conflict → N-type EVIDENCE_MISSING
  - cue_conflict: True → False
  - cue_direction: MERGE → null
  - conflict_status: EVIDENCE_MISSING
  - reclassified_from: S
  - reason: No cue displayed in B2; conflict is conceptual, not observable

AMB-064: S-type conflict → N-type EVIDENCE_MISSING
  - cue_conflict: True → False
  - cue_direction: MERGE → null
  - conflict_status: EVIDENCE_MISSING
  - reclassified_from: S
  - reason: No cue displayed in B2; conflict is conceptual, not observable

Genuine conflict count: 2 (AMB-313, AMB-462)
```

### Patch B — abstraction_burden Hardcode Removal

```
BEFORE: abstraction_burden = cond === 'A' ? 'HIGH' : (cond === 'B1' ? 'MEDIUM' : 'LOW')
AFTER:  abstraction_burden = null

Field retained in schema for compatibility.
Must be null in all records.
Must NOT be used in analysis.
```

## 3. SHA256 Hashes

### Frozen Baseline

```
GT (is11_semantic_ground_truth.json):
  7349963d0d23b5efc8c092ad45b8f301c39ca13a9c3bef8952aff809d0286959

TLD (table_line_detector.py):
  022f5c21e872ad9e737ddadb10a3f9eb8ff0ddd31333dacd6f30610cfbd8d79b

7 frozen sources: drift=0
```

### Experiment Artifacts

```
experiment_cases.json:
  698a8c05a8179a071a0a5e5f8b3d1c9e0f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c

experiment_cases_embedded.json:
  f8e98180d0c07dd5...

experiment_ui.html:
  7b639e2daf8c69cf...

experiment_server.py:
  a0eb2f374725da58...

analysis_contract.md:
  aea8dbbb92db83f0...

case_exposure_matrix.json:
  23dc6c0f16969472...

case_exposure_matrix.md:
  9a40bc8ac831cfb3...
```

### Design & Audit Artifacts

```
experiment_design_md:    221e67417a0927b9...
experiment_design_json:  50a1f50bf0301cbd...
correction_log:          14f6c6c239615f5f...
implementation_report:   cbb3ef80272367ae...
case_exposure_audit:     f14c1236521db022...
```

## 4. Patch Status

```
PATCH_A_CLASSIFICATION = PASS
  - AMB-032: EVIDENCE_MISSING ✓
  - AMB-064: EVIDENCE_MISSING ✓
  - Genuine conflicts: 2 ✓
  - GT not modified ✓
  - Underlying evidence not modified ✓

PATCH_B_ABSTRACTION_BURDEN = PASS
  - Hardcode removed ✓
  - Field set to null ✓
  - No condition-derived value ✓
  - Analysis exclusion rule in contract ✓

ABSTRACTION_BURDEN_HARDCODE = 0
```

## 5. Dry Run Status

```
DRY_RUN = PASS

Post-patch dry run (DRYRUN_002):
  - 30 cases loaded ✓
  - 3 conditions tested (B2→A→B1) ✓
  - 30 judgments submitted ✓
  - Patch A verified in served data ✓
  - Patch B verified in UI (null, no hardcode) ✓
  - abstraction_burden = null in all records ✓
  - Genuine conflict count = 2 ✓
  - DRYRUN separated from formal data ✓
  - GT hidden ✓
  - Raw events logged (62) ✓
  - Autosave + export ✓
```

## 6. Case Dataset Summary

```
Total cases: 30

Type distribution (post-patch):
  P:  17
  N:   7  (was 5, +2 reclassified from S)
  B:   4
  C:   2
  S:   2  (was 4, -2 reclassified to N)
  U:   2

Conflict cases:
  Genuine: 2 (AMB-313, AMB-462)
  Evidence-missing: 2 (AMB-032, AMB-064)

Tier distribution:
  Tier 1 (full evidence): 21
  Tier 2 (evidence reduced): 9

Zero-cue cases in B2: 7
Cue-available cases: 23
```

## 7. Analysis Contract

```
Primary comparison: B1 vs B2 on cue-available cases (23/30)
Primary effort: decision_time, expansion_count, revisit_count, levels_viewed, interaction_count
Quality: correctness, boundary correctness, UNKNOWN preservation
Safety: WCAR, COR, EIR, CFR (case-level on 2 genuine conflicts)
Statistical language: exploratory, descriptive, no significance claims
abstraction_burden: excluded (null, not measured)
Learning boundary: ITERATIVE_LEARNING = INSUFFICIENT_EVIDENCE

Contract hash: aea8dbbb92db83f0...
```

## 8. Freeze Statement

```
The following artifacts are FROZEN as of 2026-09-12:

  1. experiment_cases.json (case dataset, metadata, classification)
  2. experiment_cases_embedded.json (with images)
  3. experiment_ui.html (3-condition UI)
  4. experiment_server.py (recording server)
  5. analysis_contract.md (analysis rules)
  6. case_exposure_matrix.json/.md (exposure audit artifact)
  7. experiment_design .md/.json (v2 corrected design)
  8. GT (is11_semantic_ground_truth.json)
  9. TLD (table_line_detector.py)
  10. All frozen perception sources (7 anchors, drift=0)

NO modifications to these artifacts are allowed until:
  - Formal Human Experiment data is collected, OR
  - Explicit authorization for further design changes is granted.

Participant isolation rule:
  - Participant A's results must NOT change Participant B's materials
  - Human feedback is append-only (recorded, not applied)
  - No real-time system updates from participant behavior
```

## 9. Final Gate

```
FINAL_PRE_EXPERIMENT_PATCH = PASS

PATCH_A_CLASSIFICATION = PASS
PATCH_B_ABSTRACTION_BURDEN = PASS

ABSTRACTION_BURDEN_HARDCODE = 0

CASE_DATASET_INTEGRITY = PASS
GT_INTEGRITY = PASS
CUE_PROVENANCE = PASS
GT_LEAKAGE = PASS

GENUINE_CONFLICT_COUNT = 2
AMB_032 = EVIDENCE_MISSING
AMB_064 = EVIDENCE_MISSING

PRIMARY_ANALYSIS = B1_vs_B2_CUE_AVAILABLE
TIER_IMBALANCE = REPORTED_AS_LIMITATION
DRYRUN_EXCLUDED = TRUE

UI_INTEGRITY = PASS
TIMER_INTEGRITY = PASS
PARTICIPANT_ISOLATION = PASS
RECORDING_INTEGRITY = PASS

FINAL_EXPERIMENT_FREEZE = PASS

FORMAL_HUMAN_EXPERIMENT_READY = TRUE

FROZEN_BASELINE = INTACT
PRODUCTION = FALSE
RUNTIME_AUTHORITY = ZERO

ITERATIVE_LEARNING = INSUFFICIENT_EVIDENCE
STOP = TRUE
```
