# HVA-05 Phase 1 Contract Gap Closure Audit

**Date**: 2026-09-17
**Mode**: READ-ONLY CONTRACT GAP CLOSURE / NO CODE / NO IMPLEMENTATION / FROZEN INTACT / STOP
**Predecessors**: HVA-03, HVA-04
**Scope**: GAP-1 (content_type) + GAP-4 (Evidence Source) + Guardrail Labeling ONLY

---

## 1. Executive Summary

```
HVA-05 STATUS = READY

GAP-1 = CLOSED → content_type REMOVED from Evidence Signature
GAP-4 = CLOSED → machine_eval is Evidence Source of Truth

KEY FINDINGS:

  GAP-1: content_type CANNOT be deterministically derived from machine_eval.
    HVA-04 proposed: is_in_table + is01_a → TABLE_NUMERIC
    TESTED on 45 cases: 29/45 (64%) → AMBIGUOUS (no rule matches)
    ROOT CAUSE: is_in_table is TLD detection result (can fail), not semantic classification.
      When TLD fails, is_in_table=False even for table content (AMB-135: "4" / "MBConv6").
      No machine_eval field can distinguish "table TLD missed" from "genuine non-table".
    CONCLUSION: content_type requires semantic classification → CANNOT enter Signature.
    REMEDIATION: S3 Signature (6 boolean fields) distinguishes all signals WITHOUT content_type.

  GAP-4: machine_eval is Evidence Source of Truth.
    17/30 L5 cases have TLD discrepancies with machine_eval.
    TWO discrepancy types:
      Type A (9 cases): L5 has_tld=False, TLD=None; machine_eval HAS TLD data.
        → L5 experiment didn't expose TLD to human (Evidence Distillation Gap)
      Type B (8 cases): L5 has_tld=True with different_cell=True; machine_eval has different_cell=False.
        → L5 used DIFFERENT TLD results than machine_eval (possible version mismatch)
    CONCLUSION: L5 cues are experiment UI presentation, NOT evidence ground truth.
    machine_eval has 45/45 complete data. L5 has 30/45 with 17 discrepancies.
    REMEDIATION: FeedbackRecord.evidence_snapshot reads from machine_eval exclusively.

  SIGNATURE_MINIMAL_VERSION = S3
    S3 = (is_in_table, different_cell, is01_a, is02_b, text_a_ends_period, text_b_starts_capital)
    6 boolean fields. Distinguishes SIG-01, SIG-02, SIG-07 without content_type.
    S1 (2 fields): TOO COARSE — cannot distinguish SIG-01 from SIG-02.
    S2 (4 fields): WORKS but less granular than S3.
    S3 (6 fields): WORKS, adds period+capital for sentence boundary detection.
    S4 (S3 + content_type): UNSAFE — content_type not derivable.

  SEMANTIC_LEAKAGE = 0
  AUTOMATION_BIAS_RISK = LOW (with UI labeling)
  AUTHORITY_BOUNDARY = PASS

STOP = TRUE
```

---

## 2. GAP-1: content_type Derivability Test

### 2.1 HVA-04 Proposed Derivation Rule

```
is_in_table=True + is01_a=True → TABLE_NUMERIC
is_in_table=True + is01_a=False → TABLE_TEXT
is_in_table=False + text_a_ends_period → PROSE
text_a starts with "Fig" → FIGURE
```

### 2.2 Test Result on ALL 45 IS-11 Cases

```
TABLE_NUMERIC: 5 cases (AMB-024/034/074/346/350) — all is_in_table=True, is01_a=True
TABLE_TEXT: 8 cases (AMB-005/032/064/101/102/440/522/530) — all is_in_table=True, is01_a=False
PROSE: 3 cases (AMB-375/418/519) — all is_in_table=False, ends_period=True
FIGURE: 0 cases — "Fig" prefix check fails (AMB-414 starts with "FIG. 9:", uppercase)
AMBIGUOUS: 29 cases (64%) — NO rule matches
```

### 2.3 Why 29 Cases Are AMBIGUOUS

```
Root Cause: is_in_table is TLD DETECTION RESULT, not semantic classification.

When TLD fails to detect a table (DCE-06: page-global contamination, Mechanism 1):
  → is_in_table=False even though content IS table data
  → Example: AMB-135 ("4" / "MBConv6") — clearly table content, but TLD didn't detect table
  → is_in_table=False, is01_a=True, ends_period=False → AMBIGUOUS

When content is non-table but doesn't end with period:
  → is_in_table=False, ends_period=False → AMBIGUOUS
  → Example: AMB-321 ("8,144" / "8,041") — table data TLD missed
  → Example: AMB-262 ("41M" / "EfficientNet-B5") — table data TLD missed

When content starts with "FIG." (uppercase):
  → text_a.startswith('Fig') fails (case-sensitive)
  → Example: AMB-414 ("FIG. 9:" / "Left:")

FUNDAMENTAL PROBLEM:
  is_in_table answers "Did TLD detect a table?" NOT "Is this table content?"
  These are DIFFERENT questions. TLD detection can fail (DCE-06 proved 2 mechanisms).
  No machine_eval field answers "Is this table content?" deterministically.
  → content_type requires semantic classification that machine_eval CANNOT provide.
```

### 2.4 Three Version Comparison

| Criterion | Version A (no content_type) | Version B (machine-derived) | Version C (HVA-01 manual) |
|---|---|---|---|
| Evidence Purity | HIGH — only machine_eval fields | MEDIUM — derived but 64% ambiguous | LOW — manual labels mixed in |
| Traceability | HIGH — all fields from machine_eval | MEDIUM — derivation rule documented | LOW — manual, not reproducible |
| Semantic Leakage | 0 | >0 — content_type IS semantic label | >0 — semantic label from human |
| Reproducibility | HIGH — deterministic | LOW — 64% ambiguous, rule incomplete | NONE — manual |
| Signal Separation | S3 distinguishes all signals | Cannot test (64% ambiguous) | Works but impure |
| Implementation Complexity | LOW — read existing fields | HIGH — derivation rule + ambiguity handling | MEDIUM — needs manual labels |
| **Verdict** | **SELECTED** | **REJECTED** | **REJECTED** |

### 2.5 content_type Removal Justification

```
content_type is NOT needed for Phase 1 because:

1. S3 Signature (without content_type) distinguishes all 4 signals:
   SIG-01: (True, True, True, False, False, False) — unique
   SIG-02: (False, False, False, True, True, True) — unique
   SIG-07: (True, True, False, False, False, False) — unique
   → No overlap between any signal groups.

2. content_type adds ZERO separation power:
   S3 already separates all signals. Adding content_type would not
   create new distinctions — it would only add a semantic label
   that is itself ambiguous (64% of cases).

3. content_type would introduce semantic contamination:
   If a manually-derived or ambiguous content_type enters the Signature,
   the Learning Loop starts with a semantic label mixed into Machine Evidence.
   This violates the principle: Signature = structural facts only.

4. content_type can be used as METADATA (not Signature field):
   In Evidence Pack L0, content_type can be shown to Human as
   "Classified as: TABLE_NUMERIC" (derived, labeled as machine-derived).
   But it does NOT enter Evidence Signature.
   → Human sees it as context, not as structural fingerprint.
```

### 2.6 GAP-1 Resolution

```
GAP-1 = CLOSED
CONTENT_TYPE = REMOVED (from Evidence Signature)
CONTENT_TYPE_SOURCE = N/A (not used in Signature)
CONTENT_TYPE_IS_MACHINE_EVIDENCE = NO (cannot be deterministically derived)

Note: content_type MAY be shown in Evidence Pack L0 as display metadata
(labeled "Machine-derived classification, may be inaccurate"),
but it does NOT enter Evidence Signature and does NOT affect SignalCandidate formation.
```

---

## 3. GAP-4: Evidence Source Hierarchy

### 3.1 Discrepancy Analysis

```
17/30 L5 cases (57%) have TLD discrepancies with machine_eval:

Type A — L5 missing TLD, machine_eval has it (9 cases):
  AMB-032: L5 TLD=None, machine_eval is_in_table=True, different_cell=True
  AMB-052: L5 TLD=None, machine_eval is_in_table=False, different_cell=False
  AMB-064: L5 TLD=None, machine_eval is_in_table=True, different_cell=True
  AMB-163: L5 TLD=None, machine_eval is_in_table=False, different_cell=False
  AMB-168: L5 TLD=None, machine_eval is_in_table=False, different_cell=False
  AMB-198: L5 TLD=None, machine_eval is_in_table=False, different_cell=False
  AMB-205: L5 TLD=None, machine_eval is_in_table=False, different_cell=False
  AMB-375: L5 TLD=None, machine_eval is_in_table=False, different_cell=False
  AMB-418: L5 TLD=None, machine_eval is_in_table=False, different_cell=False
  → L5 experiment didn't expose TLD to human for these cases.
  → This is the Evidence Distillation Gap (AMB-032 is the canonical example).

Type B — L5 has DIFFERENT TLD data than machine_eval (8 cases):
  AMB-130: L5 is_in_table=True, diff_cell=True; machine_eval is_in_table=False, diff_cell=False
  AMB-135: L5 is_in_table=True, diff_cell=True; machine_eval is_in_table=False, diff_cell=False
  AMB-262: L5 is_in_table=True, diff_cell=True; machine_eval is_in_table=False, diff_cell=False
  AMB-457: L5 is_in_table=True, diff_cell=True; machine_eval is_in_table=False, diff_cell=False
  AMB-467: L5 is_in_table=True, diff_cell=True; machine_eval is_in_table=False, diff_cell=False
  AMB-483: L5 is_in_table=True, diff_cell=True; machine_eval is_in_table=False, diff_cell=False
  AMB-505: L5 is_in_table=True, diff_cell=True; machine_eval is_in_table=False, diff_cell=False
  AMB-514: L5 is_in_table=True, diff_cell=True; machine_eval is_in_table=False, diff_cell=False
  → L5 used DIFFERENT TLD results than machine_eval.
  → These are ALL TLD failure cases (DCE-06 Mechanism 1: page-global contamination).
  → L5 experiment likely ran TLD with different configuration or different page rendering.
  → machine_eval is the FROZEN evaluation result (hash verified).
```

### 3.2 Evidence Source Hierarchy

```
SOURCE              | AUTHORITY              | ALLOWED USE                    | FORBIDDEN USE
--------------------|------------------------|--------------------------------|----------------------------------
machine_eval        | Machine Evidence       | Evidence Snapshot source       | NOT for Human judgment
(is11_observation,  | (frozen, hashed)       | Evidence Signature extraction  | NOT for Semantic decision
 experimental_c)    |                        | FeedbackRecord.evidence_snapshot| NOT modified by Phase 1
--------------------|------------------------|--------------------------------|----------------------------------
GT                  | Human Ground Truth     | Evaluation comparison          | NOT as Machine Evidence
(text_a/b, labels,  |                        | Adjudication history           | NOT in Evidence Signature
 rationales)        |                        | Audit trail                    | NOT shown to Human as "answer"
--------------------|------------------------|--------------------------------|----------------------------------
L5 experiment data  | Experiment Record      | Human behavior analysis        | NOT as Evidence Source of Truth
(decision, time,    | (interaction log)      | evidence_viewed tracking       | NOT for evidence_snapshot
 expanded_fields)   |                        | engagement stats               | NOT for TLD/is_in_table values
--------------------|------------------------|--------------------------------|----------------------------------
L5 cues             | Experiment UI          | NONE in Phase 1                | FORBIDDEN as Evidence
(has_tld, cue1-7)   | presentation           |                                | (17/30 discrepancies with machine_eval)
--------------------|------------------------|--------------------------------|----------------------------------
HVA-01 derived      | Audit Artifact         | Analysis context               | NOT as Machine Evidence
labels (content_type|                        | Report reference               | NOT in Evidence Signature
, case_class)       |                        |                                |
--------------------|------------------------|--------------------------------|----------------------------------
HVA-02 signal       | Audit Artifact         | Validation reference           | NOT as Runtime Signal
candidates          |                        | Cross-check                    | NOT auto-promoted
--------------------|------------------------|--------------------------------|----------------------------------
P1-P6, TLD          | Frozen Machine         | Read via machine_eval          | NOT directly accessed by Phase 1
                    | Observation            | (machine_eval captures output) | NOT modified
```

### 3.3 machine_eval as Evidence Source of Truth

```
JUSTIFICATION:

1. Completeness: 45/45 cases have is11_observation with is_in_table + different_cell.
   L5 has 30/45 with 17 discrepancies.

2. Frozen: machine_eval is the frozen IS-11 evaluation result.
   TLD hash (022f5c21) and GT hash (7349963d) verified in every record.

3. Consistency: machine_eval is11_observation is the output of the FROZEN TLD + IS-11 pipeline.
   L5 cues are experiment UI presentation, which used different TLD configuration
   (Type B discrepancies prove L5 TLD ≠ machine_eval TLD for 8 cases).

4. Authority: machine_eval is Machine Evidence (structural observation).
   L5 cues are Experiment Record (interaction log).
   GT is Human Ground Truth (judgment).
   These are DIFFERENT authority levels and must not be mixed.

EVIDENCE_SOURCE_OF_TRUTH = machine_eval (is11_machine_evaluation_results.json)
```

### 3.4 Evidence Snapshot Contract

```
FeedbackRecord.evidence_snapshot reads EXCLUSIVELY from machine_eval.

SNAPSHOT CONTRACT:
  Input: machine_eval.experimental_c.is11_observation + experimental_c.is01_a/is02_b/decision
         + GT.text_a/text_b (for period/capital derivation only)
  Transformation: Copy field values into frozen dict. Derive period/capital from text.
  Output: evidence_snapshot dict with frozen values
  Provenance: machine_eval file hash + TLD hash + GT hash + timestamp
  Authority: Machine Evidence (authority=0)
  Failure State: if machine_eval missing for case_id → SNAPSHOT_FAILED → FeedbackRecord not created

EVIDENCE_SNAPSHOT_CONTRACT = READY

Snapshot fields (final, from machine_eval):
  is_in_table: bool (from machine_eval is11_observation)
  different_cell: bool (from machine_eval is11_observation)
  is01_a: bool (from machine_eval experimental_c)
  is02_b: bool (from machine_eval experimental_c)
  machine_decision: str (from machine_eval experimental_c)
  text_a_ends_period: bool (derived from GT.text_a — deterministic regex)
  text_b_starts_capital: bool (derived from GT.text_b — deterministic check)
  document_id: str (from machine_eval)
  page: int (from machine_eval)

Provenance fields:
  machine_eval_hash: str (sha256 of is11_machine_evaluation_results.json, first 16 chars)
  tld_hash: str (022f5c21e872ad9e)
  gt_hash: str (7349963d0d23b5ef)
  snapshot_timestamp: str (ISO format)

RECONSTRUCTION GUARANTEE:
  If Human sees Evidence Pack on 2026-xx-xx and machine_eval changes later,
  FeedbackRecord.evidence_snapshot + provenance hashes allow EXACT reconstruction.
  If hashes don't match → SNAPSHOT_STALE → not used for SignalCandidate.
```

---

## 4. Per-Field Semantic Audit

| Field | Source | Type | Semantic Level | Provenance | Safe for Human Display? | Safe for Signature? | Safe for Learning? |
|---|---|---|---|---|---|---|---|
| is_in_table | machine_eval is11_observation | bool | Machine Evidence (TLD detection) | TLD (frozen) | YES (label: "TLD: In Table") | YES | YES |
| different_cell | machine_eval is11_observation | bool | Machine Evidence (TLD detection) | TLD (frozen) | YES (label: "TLD: Different Cell") | YES | YES |
| is01_a | machine_eval experimental_c | bool | Machine Evidence (IS-01 regex) | IS-01 (frozen) | YES (label: "IS-01: Number") | YES | YES |
| is02_b | machine_eval experimental_c | bool | Machine Evidence (IS-02 alpha check) | IS-02 (frozen) | YES (label: "IS-02: Text") | YES | YES |
| text_a_ends_period | Derived from GT.text_a | bool | Evidence Fact (deterministic regex) | GT text (frozen) | YES (label: "Ends with period") | YES | YES |
| text_b_starts_capital | Derived from GT.text_b | bool | Evidence Fact (deterministic check) | GT text (frozen) | YES (label: "Starts with capital") | YES | YES |
| machine_decision | machine_eval experimental_c | str | Machine Interpretation (IS-11 decision) | IS-11 (frozen) | YES (label: "Machine Decision (may be wrong)") | **NO** | NO |
| machine_outcome | machine_eval experimental_c | str | Machine Interpretation (vs GT) | IS-11 (frozen) | **NO** (reveals correctness) | NO | NO |
| content_type | DERIVED | str | **Cannot derive** (64% ambiguous) | N/A | Display only (labeled "may be inaccurate") | **NO** | NO |

**Key distinction:**
- is_in_table, different_cell, is01_a, is02_b, period, capital = **Machine Evidence** (structural facts, safe for Signature)
- machine_decision = **Machine Interpretation** (safe for Human display with label, NOT for Signature)
- machine_outcome = **Machine Interpretation** (NOT safe for Human display — reveals correctness)
- content_type = **Cannot derive** (NOT safe for Signature)

---

## 5. Guardrail Labeling

### 5.1 UI Labels for Evidence Pack L0-L1

| Field | UI Label | Rationale |
|---|---|---|
| is_in_table | "TLD Detection: In Table = YES/NO" | Machine-derived, labeled as TLD output |
| different_cell | "TLD Detection: Different Cell = YES/NO" | Machine-derived, labeled as TLD output |
| is01_a | "IS-01: Number = YES/NO" | Machine-derived, labeled as IS-01 output |
| is02_b | "IS-02: Text = YES/NO" | Machine-derived, labeled as IS-02 output |
| text_a_ends_period | "Text A ends with period: YES/NO" | Evidence Fact (deterministic) |
| text_b_starts_capital | "Text B starts with capital: YES/NO" | Evidence Fact (deterministic) |
| machine_decision | "Machine Decision (may be wrong): KEEP_SEPARATE" | Machine Interpretation, labeled "may be wrong" |
| machine_outcome | **NOT SHOWN** | Reveals correctness → automation bias |
| content_type | **NOT SHOWN in L1** (optional in L0 as "Classified as: X (may be inaccurate)") | 64% ambiguous → unreliable |

### 5.2 Automation Bias Risk Assessment

```
Question: Does the label itself produce automation bias?

Risk sources:
  1. machine_decision in L1 → Human might anchor on Machine's decision
     Mitigation: Label says "may be wrong" explicitly
     HVA-02 evidence: 2 overrides in L5 → Human CAN override (safe)
     Risk: LOW

  2. machine_outcome → NOT shown → NO risk
     Risk: NONE

  3. TLD fields (is_in_table, different_cell) → Human might treat as ground truth
     Mitigation: Label says "TLD Detection" (clearly machine-derived, not "correct answer")
     HVA-02 evidence: AMB-462/313 Human overrode TLD failure → Human CAN disagree
     Risk: LOW

  4. content_type → NOT in L1 → NO risk in Signature
     If shown in L0: labeled "may be inaccurate" → LOW risk
     Risk: LOW (display only, not in Signature)

OVERALL AUTOMATION_BIAS_RISK = LOW

  The key protection is:
  - NO "Recommended" or "Suggested" label anywhere
  - NO machine_outcome (correctness not revealed)
  - NO cue_direction (HVA-02: B2 cue was WRONG on 2 cases)
  - Human decision is always final (FeedbackRecord records Human's decision, not Machine's)
```

---

## 6. Evidence Signature — Final Selection

### 6.1 Version Comparison

```
S1: (is_in_table, different_cell) — 2 fields
  SIG-01 sig: (True, True)
  SIG-02 sig: (True, True) AND (False, False) — OVERLAP with SIG-01!
  SIG-07 sig: (True, True) — OVERLAP with SIG-01!
  → CANNOT distinguish signals. TOO COARSE.
  → REJECTED.

S2: (is_in_table, different_cell, is01_a, is02_b) — 4 fields
  SIG-01 sig: (True, True, True, False)
  SIG-02 sig: (False, False, False, True) AND (True, True, False, True)
  SIG-07 sig: (True, True, False, False)
  → CAN distinguish all signals. No overlap.
  → WORKS but doesn't include period/capital (needed for sentence boundary detection).
  → ACCEPTABLE but not optimal.

S3: (is_in_table, different_cell, is01_a, is02_b, text_a_ends_period, text_b_starts_capital) — 6 fields
  SIG-01 sig: (True, True, True, False, False, False)
  SIG-02 sig: (False, False, False, True, True, True) AND (True, True, False, True, True, True)
  SIG-07 sig: (True, True, False, False, False, False)
  → CAN distinguish all signals. No overlap.
  → Includes period+capital (needed for SIG-02 sentence boundary detection).
  → OPTIMAL.

S4: S3 + content_type — 7 fields
  → content_type CANNOT be derived (64% ambiguous).
  → UNSAFE.
  → REJECTED.
```

### 6.2 Selection: S3

```
SIGNATURE_MINIMAL_VERSION = S3

EvidenceSignature = {
    "is_in_table": bool,            # from machine_eval is11_observation
    "different_cell": bool,         # from machine_eval is11_observation
    "is01_a": bool,                 # from machine_eval experimental_c
    "is02_b": bool,                 # from machine_eval experimental_c
    "text_a_ends_period": bool,     # derived from GT.text_a (deterministic)
    "text_b_starts_capital": bool,  # derived from GT.text_b (deterministic)
}

Why S3 over S2:
  S3 includes text_a_ends_period and text_b_starts_capital.
  These are needed to detect SIG-02 (sentence boundary pattern).
  Without them, SIG-02 cases would have signature (False, False, False, True)
  which collides with other non-period, non-capital cases.
  With S3, SIG-02 has unique signature (False, False, False, True, True, True).
  
Why NOT S4:
  content_type cannot be deterministically derived (64% ambiguous).
  Adding an ambiguous semantic label to a structural fingerprint
  contaminates the Signature with non-deterministic data.
  S3 already distinguishes all signals → content_type adds ZERO value.

All 6 S3 fields are:
  - Boolean (structural, not semantic)
  - From machine_eval or deterministic derivation from GT text
  - Deterministic and reproducible
  - Provenance traceable (TLD hash, GT hash)
  - No human label
  - No semantic judgment
  - No frozen evidence modification
```

### 6.3 S3 Collision Analysis (All 45 Cases)

```
S3 produces 10 unique signatures across 45 cases.
8 groups have ≥2 cases (recurrence possible).
2 singletons.

Largest group: (False, False, False, False, False, False) — 13 cases
  All KEEP_SEPARATE, consistent.
  These are TLD-failure cases (table not detected).
  → Would form a SignalCandidate with 13 cases, independence check needed.

Conflict group: (False, False, False, True, False, True) — 6 cases
  4 KEEP_SEPARATE + 2 MERGE (AMB-414, AMB-422 — figure captions)
  → has_conflict=True → BOUNDARY_REVIEW_REQUIRED
  → System correctly identifies conflict without content_type.

Consistent groups: 7/8 groups have consistent GT labels.
  → Good signal formation potential.

Non-consistent group: 1/8 (the figure caption conflict group)
  → Correctly flagged as CONFLICT.
  → No content_type needed to detect conflict — S3 signature match + GT label difference suffices.
```

---

## 7. SIG Re-Validation Without content_type

### SIG-01 (TABLE_NUMERIC_DIFF_CELL)

```
S3 Signature: (True, True, True, False, False, False)
  5 cases: AMB-024/034/074/346/350
  All KEEP_SEPARATE, consistent.
  Independence: 3 docs, 5 cases (3 on resnet, 1 med, 1 cs) → ratio varies by page.

Without content_type:
  → Signature still unique. Still groups correctly. Still consistent.
  → content_type was USEFUL (for human display) but NOT NECESSARY (for signature).
  → REMOVED from Signature, optionally shown in L0 display.

VERDICT: content_type = USEFUL (display) but NOT NECESSARY (signature)
```

### SIG-02 (SENTENCE_BOUNDARY_PERIOD_CAPITAL)

```
S3 Signature: (False, False, False, True, True, True)
  3 cases: AMB-375/418/519
  All KEEP_SEPARATE (adjudicated), consistent at GT level.
  has_conflict=True (reviewer disagreement).

  Also: (True, True, False, True, True, True) for AMB-005
  → AMB-005 has is_in_table=True (TLD detected a table, but text is prose)
  → Different signature from AMB-375/418/519
  → AMB-005 forms a SEPARATE candidate from the other 3

Without content_type:
  → Signatures still unique. Still groups correctly.
  → content_type was REDUNDANT (S3 already separates by period+capital).

VERDICT: content_type = REDUNDANT
```

### SIG-07 (AMB-032 Evidence Distillation Gap)

```
S3 Signature: (True, True, False, False, False, False)
  1 case: AMB-032 (plus AMB-064/101/102/440 with same signature)
  → Actually 5 cases share this signature!
  → All KEEP_SEPARATE, consistent.
  → Could form a SignalCandidate (5 cases, consistent).

Without content_type:
  → Signature still unique. Still groups 5 cases.
  → content_type was REDUNDANT.

VERDICT: content_type = REDUNDANT
```

### SIG-08 (AMB-375 Genuine Boundary)

```
S3 Signature: same as SIG-02 (False, False, False, True, True, True)
  → SIG-08 = SIG-02 (same signature, same candidate).
  → content_type was REDUNDANT.

VERDICT: content_type = REDUNDANT
```

### Summary

| Signal | content_type necessity | S3 without content_type | Distinguishable? |
|---|---|---|---|
| SIG-01 | USEFUL (display only) | Unique signature | YES |
| SIG-02 | REDUNDANT | Unique signature | YES |
| SIG-07 | REDUNDANT | Unique signature | YES |
| SIG-08 | REDUNDANT | = SIG-02 | YES |

**content_type is NOT NECESSARY for any signal. S3 alone suffices.**

---

## 8. Failure Routing (Unchanged from HVA-04)

```
All HVA-04 failure routes remain valid:

  Evidence Missing → UNKNOWN
  Case Selection uncertain → retain/exclude
  Evidence Pack insufficient → Human expands → UNKNOWN
  Feedback insufficient → no Signal
  Signal unstable → BOUNDARY_REVIEW_REQUIRED
  Counterexample found → BOUNDARY_REVIEW_REQUIRED
  No counterexample → INSUFFICIENT_EVIDENCE
  Boundary unresolved → UNKNOWN
  Future case fails → Signal REVIEW

No new failure routes needed.
No fallback = guess.
No retry = change decision.
```

---

## 9. Final Gate

```
HVA-05 STATUS = READY

GAP-1 = CLOSED
  content_type CANNOT be deterministically derived (29/45 = 64% AMBIGUOUS)
  content_type REMOVED from Evidence Signature
  S3 (6 boolean fields) distinguishes all signals without content_type

GAP-4 = CLOSED
  machine_eval is Evidence Source of Truth (45/45 complete, frozen, hashed)
  L5 cues are experiment UI presentation (17/30 discrepancies with machine_eval)
  FeedbackRecord.evidence_snapshot reads exclusively from machine_eval

CONTENT_TYPE = REMOVED (from Signature; optional display-only in L0 with "may be inaccurate" label)
CONTENT_TYPE_SOURCE = N/A (not derivable from machine_eval)
CONTENT_TYPE_IS_MACHINE_EVIDENCE = NO

EVIDENCE_SOURCE_OF_TRUTH = machine_eval (is11_machine_evaluation_results.json)
EVIDENCE_SNAPSHOT_CONTRACT = READY

SIGNATURE_MINIMAL_VERSION = S3
  (is_in_table, different_cell, is01_a, is02_b, text_a_ends_period, text_b_starts_capital)

SEMANTIC_LEAKAGE = 0
  All 6 Signature fields are boolean structural facts
  machine_decision shown with "may be wrong" label
  machine_outcome NOT shown to Human
  content_type NOT in Signature

AUTOMATION_BIAS_RISK = LOW
  No "Recommended" or "Suggested" labels
  No cue_direction
  Human can override (proven in L5: 2 overrides)
  machine_outcome hidden (correctness not revealed)

AUTHORITY_BOUNDARY = PASS
  Machine: structural evidence aggregation + signature extraction
  Human: semantic judgment + signal validation + boundary validation
  No authority leakage

IMPLEMENTATION_AUTHORIZED = FALSE
EXPERIMENT_AUTHORIZED = FALSE

DICE_CORE_MODIFICATION = NO
P1_P7_MODIFICATION = NO
TLD_MODIFICATION = NO
IS11_MODIFICATION = NO
GT_MODIFICATION = NO

FROZEN_BASELINE = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d)
PRODUCTION = FALSE
STOP = TRUE
```

---

## 10. Final Answer (8 Sentences)

1. **content_type 不要**——测试证明 29/45 (64%) 的 case 无法从 machine_eval 确定性派生出 content_type，因为 is_in_table 是 TLD 检测结果（可能失败），不是语义分类，当 TLD 漏检表格时 is_in_table=False 但内容仍是表格数据，没有任何 machine_eval 字段能确定性地回答"这是表格内容吗"。

2. **不要不影响 Phase 1**——因为 S3 Signature（is_in_table, different_cell, is01_a, is02_b, text_a_ends_period, text_b_starts_capital）在不含 content_type 的情况下已经能完全区分 SIG-01/02/07/08 四个信号，4 个信号的 S3 签名零重叠，content_type 对信号分离的贡献为零。

3. **Phase 1 的 Evidence Source of Truth 是 machine_eval**（is11_machine_evaluation_results.json）——它有 45/45 完整数据、frozen hash 验证、TLD hash 追溯；L5 experiment data 的 cues 有 17/30 (57%) 与 machine_eval 不一致（9 个缺失 TLD 数据，8 个 TLD 数据不同），L5 cues 是实验 UI 展示层不是 Evidence Ground Truth。

4. **FeedbackRecord 通过 evidence_snapshot 冻结 Human 当时看到的 Evidence**——snapshot 直接从 machine_eval 的 is11_observation 和 experimental_c 复制字段值（6 个布尔字段 + machine_decision + document_id + page），附带 machine_eval 文件 hash + TLD hash + GT hash + 时间戳，如果后续 machine_eval 变化导致 hash 不匹配则标记 SNAPSHOT_STALE 不用于 SignalCandidate。

5. **最小 Signature 是 S3**——6 个布尔字段（is_in_table, different_cell, is01_a, is02_b, text_a_ends_period, text_b_starts_capital），全部来自 machine_eval 或从 GT.text_a/b 确定性派生，无人工标签、无语义判断、无 frozen 修改，在 45 个 case 上产生 10 个唯一签名，8 个分组有 ≥2 个 case（可形成 Candidate），1 个分组有 GT 冲突（正确标记为 CONFLICT）。

6. **HVA-04 的 GAP-1 和 GAP-4 已真正关闭**——GAP-1：content_type 从 Signature 中移除（无法确定性派生），S3 无需 content_type 即可区分所有信号；GAP-4：machine_eval 被确立为唯一 Evidence Source of Truth，L5 cues 不再作为 Evidence 来源，evidence_snapshot 合约已定义完整（字段 + provenance + 重建保证）。

7. **Guardrail labeling 已确定**——machine_decision 显示为"Machine Decision (may be wrong)"、machine_outcome 不显示（泄露正确性）、TLD 字段显示为"TLD Detection: ..."、content_type 不在 L1 显示（如在 L0 显示则标注"may be inaccurate"），无"Recommended"或"Suggested"标签，automation bias risk = LOW。

8. **下一步可以进入 Implementation Review**——所有 Implementation Blockers（GAP-1 content_type、GAP-4 evidence source、guardrail labeling）已关闭，Phase 1 Minimal Prototype C（FeedbackRecord + Evidence Pack L0-L1 + Evidence Signature S3 + SignalCandidate）的合约已完整定义，所有字段来源已确定，所有 authority boundary 已验证 PASS，可以开始审查实现方案（但仍 IMPLEMENTATION_AUTHORIZED = FALSE，需单独授权）。

`STOP = TRUE`。
