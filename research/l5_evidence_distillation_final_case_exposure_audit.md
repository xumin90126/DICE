# L5 Evidence Distillation — Final Case Exposure Integrity Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY, AUDIT ONLY
**Scope**: Audit whether 30-case dataset and exposure design support fair A/B1/B2 Human Experiment
**Audited artifacts**: `tmp/l5_evidence_distillation_experiment/data/experiment_cases.json`, `app/experiment_ui.html`, `experiment_server.py`

---

## 1. Executive Conclusion

```
CASE_EXPOSURE_AUDIT = CONDITIONAL
```

The experiment CAN proceed as a formal Human Experiment, but with mandatory limitations and reporting constraints. The primary B1-vs-B2 causal comparison is NOT broken, but it is diluted by 7/30 zero-cue cases and confounded by unstratified random case splitting.

**Core question answered**: Can A/B1/B2 differences be attributed to presentation/Evidence Distillation rather than case composition?

**Answer**: PARTIALLY YES — for cue-available cases (23/30), the B1-vs-B2 comparison is clean. For 7/30 zero-cue cases, B1 and B2 are identical (no cue difference), so they contribute noise but not bias. The main risk is unstratified random splitting causing uneven Tier-1/Tier-2 distribution across conditions.

---

## 2. Case Identity

| Check | Result |
|---|---|
| Unique case_id | PASS (30 unique IDs, 0 duplicates) |
| Stable document/page | PASS (4 documents, page=0 for all; stable mapping) |
| Stable underlying evidence | PASS (21 from frozen replay, 9 from frozen sampling frame) |
| GT consistency | PASS (all 30 cases have GT from frozen is11_semantic_ground_truth.json) |
| Near-duplicate text pairs | PASS (0 near-duplicates found) |

```
CASE_IDENTITY = PASS
```

---

## 3. Three-Condition Exposure

### Design

Each participant sees 30 cases split into 3 non-overlapping sets of 10:
- 10 cases in Condition A
- 10 cases in Condition B1
- 10 cases in Condition B2

Each case appears in exactly ONE condition per participant (no same-case repetition within participant). Across participants, the same case CAN appear in different conditions (between-participant comparison).

### Cross-Condition Exposure Capability

| Question | Answer |
|---|---|
| Can each case appear in A? | YES |
| Can each case appear in B1? | YES |
| Can each case appear in B2? | YES |
| Is exposure guaranteed balanced? | NO (random shuffle, no stratification) |
| Same case seen 3× by same participant? | NO (avoids memory effect) |

### Case Splitting Mechanism

```javascript
// Current implementation (experiment_ui.html, line 281-291):
const shuffled = [...CASES];  // random Fisher-Yates shuffle
const third = Math.ceil(shuffled.length/3);
conditionCaseLists = {
  A: shuffled.slice(0, third),      // cases 1-10
  B1: shuffled.slice(third, third*2), // cases 11-20
  B2: shuffled.slice(third*2)         // cases 21-30
};
```

**Issue**: Random shuffle does NOT guarantee balanced Tier-1/Tier-2 distribution. Simulation (1000 runs) shows:
- Tier-2 per condition: min=0, max=8, mean=3.0
- One condition could get 0 evidence-poor cases while another gets 6+

```
CASE_MATCHING = PASS (between-participant, cross-condition possible)
```

**Note**: CASE_MATCHING passes because cases CAN appear in all conditions. The balancing issue is classified under INFORMATION_AVAILABILITY_BALANCE.

---

## 4. Case Difficulty Balance

### Two-Tier Evidence Structure

| Tier | Count | TLD | Image | Cues in B2 | Types |
|---|---|---|---|---|---|
| T1 (Full Evidence) | 21 | ✓ | ✓ | 4-7 | P=17, B=2, C=2, S=2 |
| T2 (Evidence Reduced) | 9 | ✗ | ✗ | 0-2 | N=5, B=2, U=2, S=2 |

### Type Distribution Across Tiers

| Type | Tier 1 | Tier 2 | Total |
|---|---|---|---|
| P | 17 | 0 | 17 |
| N | 0 | 5 | 5 |
| B | 2 | 2 | 4 |
| C | 2 | 0 | 2 |
| S | 2 | 2 | 4 |
| U | 0 | 2 | 2 |

### Difficulty Imbalance Risk

- All N-type cases (5) are in Tier 2 (no TLD, no image, zero cues)
- All U-type cases (2) are in Tier 2
- 2/4 S-type cases are in Tier 2 (and have zero cues → not genuine conflicts)
- All C-type cases (2) are in Tier 1

If Tier-2 cases are unevenly distributed across conditions, one condition becomes systematically different in:
- Image availability
- TLD evidence availability
- Cue availability (for B2)
- Case type mix

```
CASE_DIFFICULTY_BALANCE = LIMITATION
```

**Minimal correction proposed (NOT implemented)**: Replace random shuffle with stratified randomization — ensure each condition receives ~3 Tier-2 and ~7 Tier-1 cases, with balanced type distribution.

---

## 5. Image Availability

### Per-Case Image Status

| Case | Image | Reason | Type | Tier |
|---|---|---|---|---|
| 21 replay cases | ✓ | Annotated images available | P/B/C/S | T1 |
| 9 extra cases | ✗ | No replay → no annotated image | N/B/U/S | T2 |

### Image Missing Hard Rule Check

For all 9 image-missing cases: A, B1, and B2 ALL lack the image. No condition shows an image for these cases.

```
Image consistency across conditions: PASS (same per case)
Image availability balance across conditions: LIMITATION (random, not stratified)
```

**Verdict**: Image-missing cases can be RETAINED because all 3 conditions are equally image-missing for those cases. They do NOT create a within-case condition confound. However, if image-missing cases are unevenly distributed across conditions, between-condition comparison is affected.

```
IMAGE_AVAILABILITY = LIMITATION
```

---

## 6. TLD Availability

### Per-Case TLD Status

| Case | TLD | Cue1 | Cue2 | Reason |
|---|---|---|---|---|
| 21 replay cases | ✓ | ✓ | ✓ (16/21) | Frozen TLD replay available |
| 9 extra cases | ✗ | ✗ | ✗ | No replay → no TLD evidence |

### TLD Missing Case Exposure

For all 9 TLD-missing cases: A, B1, and B2 ALL lack TLD evidence. No condition synthesizes TLD cues for these cases.

```
TLD consistency across conditions: PASS (same per case)
TLD availability balance across conditions: LIMITATION (random, not stratified)
```

**Cue generation integrity**: Cues are NOT generated for cases lacking TLD evidence. Cue1/Cue2 show `null` for these cases. No synthetic cues created.

```
TLD_AVAILABILITY = LIMITATION
```

---

## 7. Cue Availability

### B2 Cue Count Per Case

| Cue Count | Cases | Implication |
|---|---|---|
| 0 cues | 7 | B1 == B2 (no presentation difference) |
| 2 cues | 2 | B2 shows text-pattern cues only |
| 4 cues | 8 | B2 shows TLD + line cues |
| 5 cues | 8 | B2 shows TLD + line + text cues |
| 6 cues | 5 | B2 shows full cue set |

### Zero-Cue Cases (Critical Finding)

7 cases have ZERO cues displayed in B2:
- IS11-AMB-052 (N): `'0.46M' / '7.51'`
- IS11-AMB-163 (N): `'93.9%' / '34M'`
- IS11-AMB-168 (N): `'3.0x' / '5.7B'`
- IS11-AMB-198 (N): `'82.9%' / '96.2%'`
- IS11-AMB-205 (N): `'96.5%' / '155M'`
- IS11-AMB-032 (S): `'-' / '8.43'`
- IS11-AMB-064 (S): `'training data' / '07+12'`

For these cases: B2 cue panel displays "本案例无可用证据提示" (no cues available). B1 and B2 are presentationally identical.

**Impact on B1-vs-B2 comparison**: These 7 cases add noise but NOT bias. If assigned to B2, they reduce the effective cue-exposure sample. If assigned to B1, they're harmless (B1 has no cues anyway).

**Minimal correction proposed (NOT implemented)**: Analysis-stage filter — report B1-vs-B2 comparison separately for:
- Cue-available cases (23/30): genuine distillation comparison
- Zero-cue cases (7/30): no-difference baseline

```
CUE_AVAILABILITY = LIMITATION (7/30 zero-cue, dilutes but does not bias)
```

---

## 8. Conflict Cases

### Conflict Case Audit

| Case | Type | TLD | Image | Cues in B2 | Conflict Class | Genuine? |
|---|---|---|---|---|---|---|
| AMB-313 | C,S | ✓ | ✓ | 4 (cue1,cue3,cue4L,cue4R) | GENUINE_CUE_CONFLICT | YES |
| AMB-462 | C,S | ✓ | ✓ | 4 (cue1,cue3,cue4L,cue6) | GENUINE_CUE_CONFLICT | YES |
| AMB-032 | S | ✗ | ✗ | 0 | EVIDENCE_MISSING_NOT_CONFLICT | NO |
| AMB-064 | S | ✗ | ✗ | 0 | EVIDENCE_MISSING_NOT_CONFLICT | NO |

### AMB-313 Detail (Genuine Conflict)

```
Underlying Evidence: TLD is_in_table=False (frozen TLD false negative)
Generated Cue: Cue1 = "no multi-column aligned structure detected"
GT: KEEP_SEPARATE (reviewer: "two different column headers in Table 6")
Conflict: Cue says "no structure" but table structure exists → cue misleads toward MERGE
Cue displayed in B2: YES (cue1 text visible to participant)
WCAR/COR measurable: YES
```

### AMB-462 Detail (Genuine Conflict)

```
Underlying Evidence: TLD is_in_table=False (frozen TLD false negative)
Generated Cue: Cue1 = "no multi-column aligned structure detected"
GT: KEEP_SEPARATE (reviewer: "two adjacent column headers in Table 2")
Conflict: Cue says "no structure" but table structure exists → cue misleads toward MERGE
Cue displayed in B2: YES (cue1 text visible to participant)
WCAR/COR measurable: YES
```

### AMB-032 Detail (NOT Genuine Conflict)

```
Underlying Evidence: No TLD (no replay), text_a='-', text_b='8.43'
Generated Cue: NONE (zero cues available)
"Conflict" classification: cue_direction=MERGE (based on ABSENCE of boundary markers)
  → This is a CONCEPTUAL inference, not an observable cue
GT: KEEP_SEPARATE
Cue displayed in B2: NO (cue panel shows "no cues available")
WCAR/COR measurable: NO (no cue to accept/reject)
→ RECLASSIFICATION: EVIDENCE_MISSING, not GENUINE_CUE_CONFLICT
```

### AMB-064 Detail (NOT Genuine Conflict)

```
Underlying Evidence: No TLD, text_a='training data', text_b='07+12'
Generated Cue: NONE (zero cues available)
"Conflict" classification: cue_direction=MERGE (absence of boundary markers)
GT: KEEP_SEPARATE
Cue displayed in B2: NO
WCAR/COR measurable: NO
→ RECLASSIFICATION: EVIDENCE_MISSING, not GENUINE_CUE_CONFLICT
```

### AMB-414 / AMB-422

```
AMB-414: type=P, GT=MERGE, cue_direction=MERGE → NO conflict (cue correct) ✓
AMB-422: type=P, GT=MERGE, cue_direction=MERGE → NO conflict (cue correct) ✓
Both remain P-type MERGE (not reclassified to conflict) ✓
```

```
CONFLICT_CASE_INTEGRITY = FAIL
  Genuine cue conflicts: 2 (AMB-313, AMB-462)
  Fake conflicts (no cue displayed): 2 (AMB-032, AMB-064)
  WCAR/COR measurable on: 2 cases only
```

**Note**: CONFLICT_CASE_INTEGRITY is NOT a hard gate. It does not block FORMAL_HUMAN_EXPERIMENT_READY. But it must be reported as a limitation.

---

## 9. UNKNOWN

### U-Type Cases

| Case | Type | Tier | TLD | Image | Cues in B2 | GT |
|---|---|---|---|---|---|---|
| AMB-375 | B,U | T2 | ✗ | ✗ | 2 (cue5,cue6) | KEEP_SEPARATE (reviewer disagreement: A=KEEP, B=MERGE) |
| AMB-418 | B,U | T2 | ✗ | ✗ | 2 (cue5,cue6) | KEEP_SEPARATE (reviewer disagreement: A=KEEP, B=MERGE) |

### UNKNOWN Exposure

- Both U-type cases are in Tier 2 (no TLD, no image)
- Both have reviewer disagreement (genuinely ambiguous)
- Both have 2 text-pattern cues in B2 (cue5: ends with period, cue6: starts with capital)
- UNKNOWN option available in all 3 conditions
- UNKNOWN hard constraint defined: if UNKNOWN(B2) < UNKNOWN(B1), must investigate over-certainty

### UNKNOWN Balance

Both U-type cases are in Tier 2. With random splitting:
- Probability both in same condition: ~33%
- Expected per condition: ~0.67
- Some conditions may have 0 UNKNOWN exposure

```
UNKNOWN_EXPOSURE = LIMITATION
  - 2 U-type cases (minimum met)
  - Both in Tier 2 (reduced evidence)
  - Random distribution → some conditions may have 0 UNKNOWN cases
  - UNKNOWN preservation can only be tested if U-type cases land in B2
```

---

## 10. Boundary Cases

### B-Type Cases

| Case | Type | Tier | Cues in B2 | Ambiguity Source |
|---|---|---|---|---|
| AMB-005 | B | T1 | 6 | Sentence boundary (ends period, starts capital) |
| AMB-519 | B | T1 | 4 | Sentence boundary |
| AMB-375 | B,U | T2 | 2 | Reviewer disagreement |
| AMB-418 | B,U | T2 | 2 | Reviewer disagreement |

### Boundary Case Assessment

- 4 B-type cases (minimum 3 met)
- 2 in Tier 1 (full evidence, 4-6 cues): can test cue over-clarification
- 2 in Tier 2 (reduced evidence, 2 cues): can test UNKNOWN preservation
- AMB-375/418 have genuine reviewer disagreement → genuinely ambiguous
- Cue 5 ("ends with period") + Cue 6 ("starts with capital") could over-clarify → tests boundary safety

```
BOUNDARY_CASE_INTEGRITY = PASS
```

---

## 11. Negative Cases

### N-Type Cases

| Case | Type | Tier | Cues in B2 | text_a | text_b |
|---|---|---|---|---|---|
| AMB-052 | N | T2 | 0 | '0.46M' | '7.51' |
| AMB-163 | N | T2 | 0 | '93.9%' | '34M' |
| AMB-168 | N | T2 | 0 | '3.0x' | '5.7B' |
| AMB-198 | N | T2 | 0 | '82.9%' | '96.2%' |
| AMB-205 | N | T2 | 0 | '96.5%' | '155M' |

### Negative Case Assessment

- 5 N-type cases (minimum 3 met)
- ALL in Tier 2 with ZERO cues in B2
- All are numeric pairs (similar appearance, different judgment = KEEP_SEPARATE)
- These test whether cue ABSENCE causes errors (but since B1==B2 for these, they test noise, not cue effect)
- **Limitation**: N-type cases cannot test "cue induces error on confusing cases" because they have no cues

```
NEGATIVE_CASE_INTEGRITY = LIMITATION
  - 5 N-type cases (count: PASS)
  - ALL have zero cues → cannot test cue-induced errors on negatives
  - Only test baseline difficulty without cue influence
```

---

## 12. System≠GT

### S-Type Cases

| Case | Type | Tier | Cues in B2 | cue_direction | GT | Genuine? |
|---|---|---|---|---|---|---|
| AMB-313 | C,S | T1 | 4 | MERGE | KEEP_SEPARATE | YES (TLD false negative) |
| AMB-462 | C,S | T1 | 4 | MERGE | KEEP_SEPARATE | YES (TLD false negative) |
| AMB-032 | S | T2 | 0 | MERGE | KEEP_SEPARATE | NO (no cue displayed) |
| AMB-064 | S | T2 | 0 | MERGE | KEEP_SEPARATE | NO (no cue displayed) |

### System≠GT Assessment

- 4 S-type cases (minimum 3 met by count)
- But only 2 are GENUINE System≠GT (AMB-313, AMB-462)
- AMB-032/064: "cue_direction=MERGE" is conceptual (absence of markers), not an actual displayed cue
- No GT was modified to create S-type cases
- No cue was artificially generated to conflict with GT

```
SYSTEM_GT_INTEGRITY = PARTIAL
  - Count: 4 (≥3: PASS)
  - Genuine: 2 (AMB-313, AMB-462)
  - Fake: 2 (AMB-032, AMB-064 — no cue displayed, not observable)
  - No GT modification: PASS
  - No artificial conflict creation: PASS
```

---

## 13. Latin Square

### Design

```
Group 0 (participant_id % 3 == 0): A → B1 → B2
Group 1 (participant_id % 3 == 1): B1 → B2 → A
Group 2 (participant_id % 3 == 2): B2 → A → B1
```

### Verification

| Check | Result |
|---|---|
| Each condition in each position | PASS (A appears in position 1/2/3 across groups) |
| Participant group balanced | PASS (modulo 3 assignment) |
| Case exposure vs condition order | Independent (case split is random, condition order is Latin Square) |
| No fixed A→B1→B2 | PASS (3 different orders) |

```
LATIN_SQUARE = PASS
```

---

## 14. Learning Effect

### Risk Assessment

| Factor | Risk | Mitigation |
|---|---|---|
| Same case 3× by same participant | NONE | Cases split into non-overlapping sets (1 condition per participant) |
| Condition order effect | LOW | Latin Square counterbalancing |
| Transfer learning | MEDIUM | Must measure within-session time trend |
| Fatigue | MEDIUM | Mandatory breaks between conditions (UI shows transition screen) |

### Within-Session Time Trend

Not currently measured in analysis. The recording schema captures `case_order` (index within condition) and `condition_order`, enabling post-hoc time trend analysis.

```
LEARNING_EFFECT_CONTROL = PASS (Latin Square + no same-case repetition)
  Residual risk: MEDIUM (transfer learning, must measure in analysis)
```

---

## 15. Same-Case Repetition

```
Same participant sees same case multiple times: NO
  - 30 cases split into 3 non-overlapping sets of 10
  - Each case appears in exactly 1 condition per participant
  - No memory effect from repeated exposure

SAME_CASE_REPETITION = PASS
```

---

## 16. Timing Integrity

### Timing Definition

```javascript
caseStartTime = Date.now();  // set at END of loadCase(), after all content rendered
decisionTime = (endTime - caseStartTime) / 1000;  // same formula for all conditions
```

### Timing Consistency Across Conditions

| Check | Result |
|---|---|
| Timer start point | Same (end of loadCase) for A/B1/B2 |
| Timer end point | Same (submitDecision click) for A/B1/B2 |
| Formula | Same ((endTime - caseStartTime) / 1000) |
| Technical latency excluded? | NO (image render delay not excluded) |

### Timing Latency Issue

- `caseStartTime` is set AFTER `innerHTML` assignment for image
- BUT: base64 image decode/render may still be in progress when timer starts
- Tier-1 cases (with 2.5MB embedded images): ~50-200ms render delay
- Tier-2 cases (no image): no render delay
- If Tier-1/Tier-2 split is uneven across conditions → timing confound

```
TIMING_INTEGRITY = PASS (same logic for all conditions)
  Limitation: image render delay (~50-200ms) not excluded from decision_time
  Impact: inflates decision_time for Tier-1 cases vs Tier-2 cases
  If Tier-1/Tier-2 balanced across conditions → effect cancels out
  If unbalanced → systematic timing confound
```

### abstraction_burden Confound

```javascript
abstraction_burden: cond === 'A' ? 'HIGH' : (cond === 'B1' ? 'MEDIUM' : 'LOW')
```

**CRITICAL**: `abstraction_burden` is HARDCODED by condition, not measured. This pre-assumes B2 is less burdensome than B1, which is the hypothesis being tested. This field must NOT be used in analysis.

---

## 17. Presentation-only Principle

### Verified Differences

| Difference | A | B1 | B2 | Allowed? |
|---|---|---|---|---|
| Main fields shown | 15 | 8 | 8 | YES (presentation reduction) |
| Hidden fields (progressive) | 0 | 7 | 7 | YES (progressive disclosure) |
| Evidence Cues | 0 | 0 | 4 | YES (cue addition) |
| Page image | Same | Same | Same | YES |
| Decision options | 3 | 3 | 3 | YES |
| Submit behavior | Same | Same | Same | YES |
| Autosave | Same | Same | Same | YES |
| Timing mechanism | Same | Same | Same | YES |

### Forbidden Differences Check

| Check | Result |
|---|---|
| Different image per condition | PASS (same image) |
| Different evidence per condition | PASS (same underlying evidence) |
| Different GT per condition | PASS (same GT, hidden) |
| Different case per condition | PASS (same case set, different presentation) |
| Different decision options | PASS (MERGE/KEEP_SEPARATE/UNKNOWN in all) |
| Different interaction semantics | PASS (same expand/click/submit) |
| Auto-select/default decision | PASS (no auto-selection) |
| Highlighted "correct" option | PASS (no highlighting) |

```
PRESENTATION_ONLY = PASS
```

---

## 18. GT Leakage

### Cue Generation Pipeline

```
Evidence (frozen TLD/P1/line_spans) → deterministic transformation → Cue text
```

### GT-to-Cue Check

| Check | Result |
|---|---|
| GT in cue text | PASS (0 occurrences across 30 cases × 7 cues = 210 checks) |
| Human expected answer in cue | PASS (no "should", "recommend", "system thinks") |
| Cue derived from GT | PASS (cues derived from frozen evidence only) |
| Cue uses GT label | PASS (cue_direction is derived from evidence patterns, not GT) |

**Note on cue_direction**: For AMB-313/462, `cue_direction=MERGE` is derived from TLD `is_in_table=False` (cue says "no structure" → implies same flow → MERGE). This is evidence-derived, not GT-derived. The GT happens to be KEEP_SEPARATE, creating the conflict. This is correct — the cue is evidence-based, and the conflict with GT is a genuine system limitation (TLD false negative).

For AMB-032/064, `cue_direction=MERGE` is derived from absence of boundary markers (no period, no capital). This is also evidence-derived. However, no cue is actually DISPLAYED for these cases, so the "conflict" is not observable.

```
GT_LEAKAGE = PASS
```

---

## 19. Decision Option Integrity

```
All 3 conditions (A/B1/B2) use identical decision options:
  - MERGE (合并)
  - KEEP_SEPARATE (分开)
  - UNKNOWN (不确定)

No condition adds/removes/reorders options.
No condition changes button placement or styling per condition.
No condition auto-selects a default.

DECISION_OPTION_INTEGRITY = PASS
```

---

## 20. Remaining Limitations

| # | Limitation | Severity | Impact on B1-vs-B2 | Required Reporting |
|---|---|---|---|---|
| 1 | 7/30 cases have zero cues in B2 | HIGH | Dilutes B1-vs-B2 comparison (B1==B2 for these) | Report B1-vs-B2 filtered to cue-available cases (23/30) |
| 2 | Unstratified random case splitting | HIGH | May cause uneven Tier-1/Tier-2 across conditions | Report Tier distribution per condition; use stratified splitting if possible |
| 3 | Only 2 genuine conflict cases | HIGH | WCAR/COR measured on 2 cases only (low stability) | Report WCAR/COR as case-level, not rate-level |
| 4 | AMB-032/064 misclassified as conflicts | MEDIUM | Inflates conflict count; WCAR denominator wrong | Reclassify as EVIDENCE_MISSING; exclude from WCAR |
| 5 | abstraction_burden hardcoded by condition | MEDIUM | Pre-assumes hypothesis result | Exclude from analysis; replace with null |
| 6 | Image render delay (~50-200ms) | LOW | Inflates Tier-1 timing | Acknowledge; consider preloading |
| 7 | All N/U cases in Tier 2 | MEDIUM | Cannot test cue effect on negatives | Report as subgroup limitation |
| 8 | No matched case sets (X/Y/Z) | MEDIUM | Between-participant only (lower power) | Acknowledge; use within-participant analysis where possible |
| 9 | 9/30 cases lack page image | LOW | Visual evidence absent | Report as subgroup |
| 10 | n=15 exploratory | INHERENT | NO_STATISTICAL_GENERALIZATION | Report as exploratory pilot |

---

## 21. Minimal Corrections Proposed (NOT Implemented)

Per audit mode (READ-ONLY, AUDIT ONLY), these corrections are PROPOSED only:

### Correction A: Reclassify AMB-032/064

```
AMB-032: S-type conflict → EVIDENCE_MISSING (no cue displayed)
AMB-064: S-type conflict → EVIDENCE_MISSING (no cue displayed)
Genuine conflict cases: 2 (AMB-313, AMB-462)
```

### Correction B: Remove hardcoded abstraction_burden

```
Replace: abstraction_burden = cond === 'A' ? 'HIGH' : ...
With: abstraction_burden = null (not measured)
```

### Correction C: Stratified case splitting

```
Replace random shuffle with:
  1. Separate Tier-1 (21) and Tier-2 (9) cases
  2. Randomly assign ~7 Tier-1 + ~3 Tier-2 to each condition
  3. Ensure type balance (P/N/B/C/S/U distributed across conditions)
```

### Correction D: Analysis-stage filtering

```
B1-vs-B2 primary comparison:
  - Filter to cue-available cases (23/30) only
  - Report zero-cue cases (7/30) as "no-difference" subgroup

WCAR/COR:
  - Compute on genuine conflict cases only (2 cases)
  - Report as case-level observations, not rates
```

---

## 22. Hard Gate Summary

| Hard Gate | Result | Notes |
|---|---|---|
| CASE_IDENTITY | PASS | 30 unique IDs, stable mapping |
| CASE_MATCHING | PASS | Between-participant, cross-condition possible |
| INFORMATION_AVAILABILITY_BALANCE | LIMITATION | Random (not stratified); expected balanced, high variance |
| GT_INTEGRITY | PASS | All GT from frozen source, unmodified |
| CUE_PROVENANCE | PASS | All cues traceable to frozen evidence |
| GT_LEAKAGE | PASS | No GT in cue text or pipeline |
| DECISION_OPTION_INTEGRITY | PASS | Same 3 options in all conditions |
| TIMING_INTEGRITY | PASS | Same timing logic; minor latency caveat |

**No hard gate FAILs.** INFORMATION_AVAILABILITY_BALANCE is classified as LIMITATION (not FAIL) because:
- Per-case evidence availability is consistent across conditions (same case = same evidence in A/B1/B2)
- The issue is between-condition case assignment balance, which is random (not systematic)
- Expected value is balanced (3 Tier-2 per condition)
- Can be addressed through stratified splitting (Correction C) or analysis-stage reporting

---

## 23. Final Audit Gate

```
CASE_EXPOSURE_AUDIT = CONDITIONAL

CASE_IDENTITY = PASS
CASE_MATCHING = PASS
CASE_DIFFICULTY_BALANCE = LIMITATION
IMAGE_AVAILABILITY = LIMITATION
TLD_AVAILABILITY = LIMITATION
CUE_AVAILABILITY = LIMITATION
CONFLICT_CASE_INTEGRITY = FAIL (2/4 not genuine)
UNKNOWN_EXPOSURE = LIMITATION
BOUNDARY_CASE_INTEGRITY = PASS
NEGATIVE_CASE_INTEGRITY = LIMITATION
SYSTEM_GT_INTEGRITY = PARTIAL
LATIN_SQUARE = PASS
LEARNING_EFFECT_CONTROL = PASS
TIMING_INTEGRITY = PASS
DECISION_OPTION_INTEGRITY = PASS
PRESENTATION_ONLY = PASS
GT_LEAKAGE = PASS

FORMAL_HUMAN_EXPERIMENT_READY = TRUE
  (with mandatory limitations and reporting constraints)

FROZEN_BASELINE = INTACT
PRODUCTION = FALSE
RUNTIME_AUTHORITY = ZERO

ITERATIVE_LEARNING = INSUFFICIENT_EVIDENCE
STOP = TRUE
```

### CONDITIONAL PASS Rationale

The experiment CAN proceed because:

1. **All hard gates PASS** (no FAIL on any blocking item)
2. **B1-vs-B2 causal comparison is NOT broken** — for cue-available cases (23/30), the comparison is clean
3. **Zero-cue cases (7/30) add noise, not bias** — B1==B2 for these, so they don't confound the direction
4. **GT leakage = PASS** — no contamination of cue by GT
5. **Presentation-only = PASS** — only presentation differs across conditions

### Mandatory Reporting Constraints

If the formal experiment proceeds:

1. **B1-vs-B2 analysis must filter to cue-available cases (23/30)** — report zero-cue cases separately
2. **WCAR/COR must be reported on 2 genuine conflict cases only** — not 4
3. **AMB-032/064 must be reclassified as EVIDENCE_MISSING** — not conflict
4. **abstraction_burden field must be excluded from analysis** — hardcoded, not measured
5. **Tier-1/Tier-2 distribution per condition must be reported** — check for imbalance
6. **Image render delay must be acknowledged** — may inflate Tier-1 timing
7. **All results are exploratory** — NO_STATISTICAL_GENERALIZATION at n=15

### Minimal Corrections Recommended (require separate authorization)

- Correction A: Reclassify AMB-032/064
- Correction B: Remove hardcoded abstraction_burden
- Correction C: Stratified case splitting
- Correction D: Analysis-stage filtering protocol

These corrections are PROPOSED only. Implementation requires separate authorization.
