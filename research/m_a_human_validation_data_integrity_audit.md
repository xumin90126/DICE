# M-A Human Validation Data Integrity Audit

> **模式: READ-ONLY DATA INTEGRITY AUDIT / NO MODIFICATION / FROZEN INTACT / STOP**
> 日期: 2026-09-17
> 前置: M-A Human Validation Pilot (79 cases, session sess_1789630659813_9qk3ods8)
> 本文件: 审计 Human Validation 原始数据的统计口径与完整性。

---

## 1. AUDIT PURPOSE

上一轮初步汇报存在计数不一致：

```
Reported: 61 YES + 4 NO + 15 UNCERTAIN = 80 (but 79 cases reported)
Reported type counts: 39 + 19 + 5 + 1 + 8 + 8 = 80 (but 79 cases reported)
```

本审计必须确定：统计摘要错误、Case Type 重叠、重复 Case、Revision 处理错误，还是原始数据存在其他问题。

---

## 2. RAW DATA INSPECTION

### Source File

```
tmp/m_a_human_review_pilot/data/human_session_1.json
  session_id: sess_1789630659813_9qk3ods8
  export_timestamp: 2026-09-17T08:01:23.038Z
  reported total_events: 80
  actual len(events): 80 (verified)
  event types: {judgment: 80} (no skip events)
```

### Raw Event Inspection

```
All 80 events are type=judgment.
No skip events.
No type=skip events.
Every event has: case_id, human_judgment, timestamp, review_order, session_id.
One event (index 46) has revision_of = non-null timestamp.
```

---

## 3. UNIQUE CASE UNIVERSE

```
TOTAL_UNIQUE_CASES = 79

Derived by: GROUP BY case_id on raw events

  Total review events (raw): 80
  Unique case_ids: 79
  Difference: 1 event (the revision)
```

### Duplicate Check

```
GROUP BY case_id:
  78 case_ids with exactly 1 event
  1 case_id with 2 events

  Multi-event case:
    case_id: arxiv_2402.18619_p28_152_82
    event 1: judgment=uncertain, revision_of=None, timestamp=2026-09-17T07:55:45.687Z
    event 2: judgment=yes, revision_of=2026-09-17T07:55:45.687Z, timestamp=2026-09-17T07:55:49.233Z

DUPLICATE_CASE_COUNT = 0
  → No accidental duplicates (same case_id shown twice without revision marker)
  → The 2-event case is a legitimate revision (revision_of field populated)

DUPLICATE_CASE_IDS = []
```

---

## 4. REVISION HANDLING

### Revision Case

```
CASE: arxiv_2402.18619_p28_152_82 (review_order=46)

  original judgment: uncertain
    timestamp: 2026-09-17T07:55:45.687Z
    revision_of: None

  final judgment: yes
    timestamp: 2026-09-17T07:55:49.233Z (3.5 seconds later)
    revision_of: 2026-09-17T07:55:45.687Z

  revision_count: 1
  included as: ONE UNIQUE CASE
  used in final statistics: YES (final judgment = yes)

REVISION CASES COUNT = 1
```

### Original vs Final Judgment Counts

```
Original judgments (all 79 cases, before revision):
  YES: 60
  NO: 4
  UNCERTAIN: 15
  SUM: 79 ✓

Final judgments (all 79 cases, after revision):
  YES: 61  (was 60, +1 from revision: uncertain→yes)
  NO: 4
  UNCERTAIN: 14  (was 15, -1 from revision)
  SUM: 79 ✓
```

---

## 5. COUNT CONSISTENCY

```
TOTAL_CASES = 79 (unique case_ids)
REVIEW_EVENTS = 80 (raw events, including 1 revision)
FINAL_JUDGMENTS = 79 (one per unique case)

YES (final): 61
NO (final): 4
UNCERTAIN (final): 14
SUM: 61 + 4 + 14 = 79

CONSISTENT = TRUE
  YES + NO + UNCERTAIN = TOTAL_UNIQUE_CASES = 79 ✓
```

---

## 6. 79 vs 80 ROOT CAUSE

```
COUNT_DISCREPANCY_ROOT_CAUSE = C (revision counted as extra event)

Explanation:
  The raw session log contains 80 events because case arxiv_2402.18619_p28_152_82
  was judged twice: first as UNCERTAIN, then revised to YES 3.5 seconds later.

  The previous summary counted all 80 events as separate judgments:
    61 YES + 4 NO + 15 UNCERTAIN = 80 (WRONG: counts original + revision)

  Correct counting uses FINAL judgment per unique case:
    61 YES + 4 NO + 14 UNCERTAIN = 79 (CORRECT)

  The revision moved one case from UNCERTAIN → YES:
    Original: 60 YES + 4 NO + 15 UNCERTAIN = 79
    Final:    61 YES + 4 NO + 14 UNCERTAIN = 79

  Previous summary error: counted 80 events instead of 79 unique cases.
  This is a summary arithmetic error, NOT a data integrity problem.
  The raw data is correct and complete.
```

### Secondary error: subfigure_label count

```
Previous summary reported subfigure_label = 5.
Corrected count: subfigure_label = 4.

Root cause: case arxiv_2402.18619_p28_152_82 (Fig. 14a) is a subfigure_label
  that was counted twice in the previous summary (once as original UNCERTAIN,
  once as revised YES), inflating subfigure_label from 4 to 5.

Corrected type counts:
  caption_like: 39 (unchanged)
  ambiguous_fragment: 19 (unchanged)
  subfigure_label: 4 (was 5, corrected)
  reference_like: 1 (unchanged)
  Type A negative: 8 (unchanged)
  Type B negative: 8 (unchanged)
  TOTAL: 39 + 19 + 4 + 1 + 8 + 8 = 79 ✓
```

---

## 7. CASE TYPE SYSTEM

### Mutual Exclusivity Check

```
TYPE_LABEL_SYSTEM = MUTUALLY_EXCLUSIVE

Each case is assigned exactly ONE primary type using this rule:
  1. If negative_type == 'type_a' → primary = 'Type A negative'
  2. If negative_type == 'type_b' → primary = 'Type B negative'
  3. Otherwise → primary = pattern_type (caption_like / ambiguous_fragment / subfigure_label / reference_like)

Overlap check:
  pattern_type and negative_type co-occur in the data, but:
  - For Type A/B cases, pattern_type is set to 'type_a_negative' / 'type_b_negative'
    (a label, not a pattern classification)
  - For candidate cases, negative_type is empty
  - The primary classification rule uses negative_type FIRST, then pattern_type
  - Therefore: NO case is assigned two primary types

OVERLAP_EXISTS = FALSE (in primary classification)
  → The 6 types are mutually exclusive strata
  → Sum of type counts = unique cases = 79 ✓
```

### Case Type Count Consistency

```
caption_like:        39
ambiguous_fragment:  19
subfigure_label:      4
reference_like:       1
Type A negative:      8
Type B negative:      8
SUM:                 79 = TOTAL_UNIQUE_CASES ✓

CASE_TYPE_COUNT_CONSISTENCY = PASS
```

---

## 8. CASE ID COVERAGE CHECK

```
Cases in session: 79
Cases in candidate data: 79
In session but NOT in candidate data: 0
In candidate data but NOT in session: 0

COVERAGE = 79/79 = 100%
  → Every candidate case was reviewed
  → No extra cases introduced
  → No missing cases
```

---

## 9. CROSS-TAB: Case Type × Final Human Judgment

```
Case Type              N    YES    NO   UNC
─────────────────────────────────────────────
caption_like          39     39     0     0
ambiguous_fragment    19     12     4     3
subfigure_label        4      4     0     0
reference_like         1      1     0     0
Type A negative        8      1     0     7
Type B negative        8      4     0     4
─────────────────────────────────────────────
TOTAL                 79     61     4    14

Each row is traceable to real case_ids (see §10).
```

### Row-by-row verification

```
caption_like (n=39): all 39 YES, 0 NO, 0 UNCERTAIN
  → 100% association confirmed

ambiguous_fragment (n=19): 12 YES, 4 NO, 3 UNCERTAIN
  → 63% YES, 21% NO, 16% UNCERTAIN
  → Most uncertain/NO cases are "Fig." standalone fragments

subfigure_label (n=4): all 4 YES, 0 NO, 0 UNCERTAIN
  → 100% association confirmed
  → (was 5 in previous summary; corrected to 4 after revision dedup)

reference_like (n=1): 1 YES, 0 NO, 0 UNCERTAIN
  → The single reference-like case ("Fig. 3). When...") was judged YES

Type A negative (n=8): 1 YES, 0 NO, 7 UNCERTAIN
  → 12% YES (false positive), 88% UNCERTAIN
  → Human did not reject any Type A as NO; mostly uncertain

Type B negative (n=8): 4 YES, 0 NO, 4 UNCERTAIN
  → 50% YES (false positive), 50% UNCERTAIN
  → Human did not reject any Type B as NO
```

---

## 10. PER-CASE AUDIT TABLE

```
(79 cases — full table in JSON)

Key fields per case:
  case_id, document_id, page_reference, case_type,
  original_judgment, final_judgment, revision_count, review_event_count

Revision case:
  arxiv_2402.18619_p28_152_82
    case_type: subfigure_label
    original_judgment: uncertain
    final_judgment: yes
    revision_count: 1
    review_event_count: 2

All other 78 cases:
    original_judgment = final_judgment
    revision_count: 0
    review_event_count: 1
```

---

## 11. CASE #46 REVISION DETAIL

```
CASE #46

  case_id: arxiv_2402.18619_p28_152_82
  document_id: arxiv_2402.18619
  page_reference: 28
  case_type: subfigure_label (Fig. 14a)
  text_content: "Fig. 14a"
  extent_bbox: [123.7, 77.2, 503.2, 178.3]
  spatial_distance: 0pt (inside extent)
  vertical_ordering: inside

  original judgment: uncertain
    timestamp: 2026-09-17T07:55:45.687Z

  final judgment: yes
    timestamp: 2026-09-17T07:55:49.233Z (3.5s later)
    revision_of: 2026-09-17T07:55:45.687Z

  revision count: 1
  included as: ONE UNIQUE CASE
  used in final statistics: YES (final judgment = yes)

  revision history preserved: YES (both events in session log)
  original judgment NOT deleted: YES (append-only confirmed)
```

---

## 12. CORRECTED ASSOCIATION VALIDITY

```
Definition:
  Association Validity = Human YES / Relevant Candidate Cases

Relevant Candidate Cases:
  = cases where FIG-prefix detected + near drawing extent
  = all non-negative cases
  = caption_like + ambiguous_fragment + subfigure_label + reference_like
  = 39 + 19 + 4 + 1 = 63

Human YES among candidates (final judgment):
  = 39 (caption_like) + 12 (ambiguous_fragment) + 4 (subfigure_label) + 1 (reference_like)
  = 56

Association Validity = 56 / 63 = 88.9%

Formula: YES / candidate_total
Numerator: 56
Denominator: 63

Previous summary reported: 56/64 = 88%
  → Denominator was 64 (wrong: counted 64 due to subfigure_label=5 instead of 4)
  → Corrected denominator: 63
  → Corrected value: 88.9% (essentially unchanged)
```

---

## 13. CORRECTED NEGATIVE CONTROL METRICS

```
Negative Control Cases:
  = Type A + Type B
  = 8 + 8 = 16

Human judgment distribution (final):

  Type A (FIG-prefix, NOT near extent):
    YES: 1 (12.5%)
    NO: 0 (0.0%)
    UNCERTAIN: 7 (87.5%)

  Type B (near extent, NO FIG-prefix):
    YES: 4 (50.0%)
    NO: 0 (0.0%)
    UNCERTAIN: 4 (50.0%)

  Combined:
    YES: 5 (31.2%)
    NO: 0 (0.0%)
    UNCERTAIN: 11 (68.8%)

False Positive Rate (primary formula):
  FPR = YES / neg_total = 5 / 16 = 31.2%
  (includes UNCERTAIN in denominator)

Alternative FPR (excluding UNCERTAIN):
  FPR_excl_unc = YES / (YES + NO) = 5 / (5 + 0) = 5 / 5 = 100.0%
  (excludes UNCERTAIN from denominator)
  → This means: among cases where Human made a definitive judgment (YES or NO),
    ALL 5 were YES (no negatives were rejected as NO)

Previous summary reported: FPR = 31%
  → Same value (31.2% vs 31%), denominator unchanged (16)
  → But FPR_excl_unc was not reported previously
```

---

## 14. CORRECTED BOUNDARY RATE

```
Definition (from m_a_pre_experiment_gate_design.md):
  Boundary Rate = UNCERTAIN / Unique Cases

UNCERTAIN (final judgment): 14
Unique Cases: 79

Boundary Rate = 14 / 79 = 17.7%

Previous summary reported: 15/80 = 19%
  → Numerator was 15 (wrong: counted original UNCERTAIN before revision)
  → Denominator was 80 (wrong: counted events instead of unique cases)
  → Corrected: 14/79 = 17.7%
```

---

## 15. LEAKAGE AUDIT

```
LEAKAGE_AUDIT = NOT_VERIFIED

  What can be verified from session data:
    ✓ Session log contains only: case_id, human_judgment, timestamp, review_order, session_id, revision_of
    ✓ No machine_answer field in session log
    ✓ No confidence/score/recommendation in session log
    ✓ No experiment result in session log
    ✓ No other case's Human answer in session log

  What CANNOT be verified from session data alone:
    ? Whether Human saw machine answers in the UI (not logged)
    ? Whether Human had prior knowledge of case types (not logged)
    ? Whether Human's browser displayed any external information (not logged)

  The UI was designed with anti-leakage (verified in UI Audit):
    ✓ No semantic labels in human-facing JSON
    ✓ No confidence/score/recommendation
    ✓ Neutral colors (no green=YES / red=NO)
    ✓ Internal metadata separated from human-facing data

  But the session log does not record what Human actually SAW on screen.
  Therefore: LEAKAGE_AUDIT = NOT_VERIFIED (design-level PASS, runtime-level NOT_VERIFIED)
```

---

## 16. ERROR SUMMARY

### Previous Summary Errors (all corrected)

```
ERROR 1: Judgment count = 80 instead of 79
  Root cause: revision event counted as separate judgment
  Correction: use FINAL judgment per unique case → 79

ERROR 2: UNCERTAIN = 15 instead of 14
  Root cause: original UNCERTAIN (case #46) counted alongside revised YES
  Correction: case #46 final = YES, so UNCERTAIN = 14

ERROR 3: subfigure_label = 5 instead of 4
  Root cause: case #46 (subfigure_label) counted twice
  Correction: 4 unique subfigure_label cases

ERROR 4: Boundary rate = 15/80 = 19% instead of 14/79 = 17.7%
  Root cause: wrong numerator (15) and denominator (80)
  Correction: 14/79 = 17.7%

ERROR 5: Candidate denominator = 64 instead of 63
  Root cause: subfigure_label inflated by 1
  Correction: 63 candidate cases

Values UNCHANGED by correction:
  YES (final): 61 (was 61 — correct in previous summary by coincidence)
  NO: 4 (unchanged)
  caption_like: 39 (unchanged)
  ambiguous_fragment: 19 (unchanged)
  Association Validity: ~89% (was 88%, negligible change)
  FPR: 31.2% (was 31%, negligible change)
```

---

## 17. DATA INTEGRITY CONFIRMATION

```
Raw session data: INTACT
  → 80 events, all type=judgment
  → 79 unique case_ids
  → 1 revision (legitimate, revision_of field populated)
  → 0 accidental duplicates
  → 0 skip events
  → 0 missing cases (79/79 coverage)

Case metadata: CONSISTENT
  → 79 cases in candidate data
  → 79 cases in session
  → 0 mismatch
  → Case types mutually exclusive (6 types, no overlap)
  → Type count sum = 79 = unique cases

Append-only: CONFIRMED
  → Revision case has both original and revised events
  → Original judgment NOT deleted
  → revision_of field links revised event to original

Human Judgment Modified: NO
  → No judgments were changed by this audit
  → Only statistical recalulation was performed

Human Validation Re-run: NO
  → No new Human judgments were collected
  → Existing 79 judgments used as-is
```

---

## 18. FINAL REPORT

```text
M-A HUMAN VALIDATION DATA INTEGRITY AUDIT

STATUS:
PASS

Unique Cases:
79

Review Events:
80

Final Judgments:
79

YES:
61

NO:
4

UNCERTAIN:
14

YES + NO + UNCERTAIN:
79

Count Consistency:
PASS

Duplicate Cases:
0

Revision Cases:
1 (case arxiv_2402.18619_p28_152_82: uncertain → yes)

Case Type System:
MUTUALLY_EXCLUSIVE

Case Type Count Consistency:
PASS (39 + 19 + 4 + 1 + 8 + 8 = 79)

79 vs 80 Root Cause:
C — revision counted as extra event.
Case arxiv_2402.18619_p28_152_82 has 2 events
(original uncertain + revision to yes).
Previous summary counted 80 events instead of 79 unique cases.
Secondary: subfigure_label miscounted as 5 instead of 4.

Association Validity:
56/63 = 88.9% (YES / candidate_total)
Previous: 56/64 = 88% (denominator off by 1)

Negative Control Metrics:
FPR = 5/16 = 31.2% (YES / neg_total, includes UNCERTAIN)
FPR_excl_unc = 5/5 = 100.0% (YES / (YES+NO), excludes UNCERTAIN)
Type A: 1 YES, 0 NO, 7 UNCERTAIN
Type B: 4 YES, 0 NO, 4 UNCERTAIN

Boundary Rate:
14/79 = 17.7% (UNCERTAIN / unique_cases)
Previous: 15/80 = 19% (wrong numerator and denominator)

Leakage Audit:
NOT_VERIFIED (design-level PASS, runtime-level not verifiable from session log)

Human Judgment Modified:
NO

Human Validation Re-run:
NO

M-A Algorithm Modified:
NO

P1 Modified:
NO

P2 Modified:
NO

P6 Modified:
NO

Frozen Baseline Drift:
0

Experiment Conclusion:
NOT YET ISSUED

STOP:
TRUE
```

---

## Governance Status

```text
M-A_HUMAN_VALIDATION_DATA_INTEGRITY_AUDIT = COMPLETE (PASS)

DATA INTEGRITY:
  Unique cases: 79
  Review events: 80 (includes 1 revision)
  Final judgments: 79
  Count consistency: PASS
  Duplicate cases: 0
  Revision cases: 1 (preserved, append-only)
  Case type: MUTUALLY_EXCLUSIVE, sum = 79
  Coverage: 79/79 = 100%

CORRECTED METRICS:
  YES: 61, NO: 4, UNCERTAIN: 14, SUM: 79 ✓
  Association Validity: 56/63 = 88.9%
  FPR: 5/16 = 31.2%
  Boundary Rate: 14/79 = 17.7%

ROOT CAUSE: revision counted as extra event (C)
  → Not a data integrity problem
  → Previous summary arithmetic error
  → Raw data is correct and complete

LEAKAGE AUDIT: NOT_VERIFIED (design PASS, runtime not logged)

FROZEN_BASELINE = INTACT (drift=0/4)
  P1: 74d23ec784d65782 (UNCHANGED)
  TLD: 022f5c21e872ad9e (UNCHANGED)
  GT: 7349963d0d23b5ef (UNCHANGED)
  layout_analyzer: 8f69f0d206b3e565 (UNCHANGED)

Human Judgment Modified: NO
M-A Algorithm Modified: NO
Experiment Conclusion: NOT YET ISSUED

STOP = TRUE
```

---

## Audit Principle Adherence

- ✅ Read raw session data (not previous summary)
- ✅ Built unique case universe from case_id GROUP BY
- ✅ Detected revision (1 case, 2 events)
- ✅ Used FINAL judgment for statistics
- ✅ Preserved original judgment (not deleted)
- ✅ Verified count consistency (79 = 61 + 4 + 14)
- ✅ Verified case type mutual exclusivity (6 types, no overlap)
- ✅ Verified type count sum = 79 = unique cases
- ✅ Cross-tab traceable to case_ids
- ✅ Reported root cause (C: revision counted as extra event)
- ✅ Corrected all 5 summary errors
- ✅ Reported formulas explicitly (numerator, denominator)
- ✅ Did NOT modify Human Judgment
- ✅ Did NOT modify Case Type labels
- ✅ Did NOT modify Candidate Set
- ✅ Did NOT modify M-A algorithm
- ✅ Did NOT modify P1/P2/P6/AO/TLD
- ✅ Did NOT re-run Human Validation
- ✅ Did NOT issue experiment conclusion
- ✅ Did NOT optimize algorithm based on results
- ✅ Frozen baseline intact (drift=0)
- ✅ STOP = TRUE

`STOP = TRUE`.
