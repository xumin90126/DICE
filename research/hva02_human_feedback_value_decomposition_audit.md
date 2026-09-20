# HVA-02 Human Feedback Value Decomposition & Reusability Audit

**Date**: 2026-09-17
**Mode**: READ-ONLY RESEARCH AUDIT / NO IMPLEMENTATION / FROZEN INTACT / STOP
**Predecessors**: HVA-01, DCE-05/06/07, L5 Learning Signal Audit, Info Gain Audit, Feedback Reuse Audit

---

## 1. Executive Summary

```
HVA-02 STATUS = INSUFFICIENT EVIDENCE

REUSABLE_SIGNAL = INSUFFICIENT EVIDENCE
  → No signal reached R5 (stable future-case reuse)
  → No signal reached R6 (measured HRR with quality preservation)
  → Highest: R4 (cross-document recurrence) for DCE-02, but with 33% false positives

HIGHEST_REUSE_LEVEL = R4 (with counterexamples — NOT validated)

BOUNDARY_SIGNAL = PARTIAL
  → 4 adjudicated cases reveal genuine boundary (period+capital vs paragraph flow)
  → But boundary is UNSTABLE (reviewer disagreement 3/3 in LSC-02)
  → P7 has 5 MERGE counterexamples → boundary not universal

PRIMARY_BOTTLENECK = MIXED (Feedback Generalization + Future Validation)
  → Feedback exists and is captured (L0-L2 achieved)
  → Candidates discovered (L3 achieved)
  → But candidates either have LOW info gain (redundant) or HIGH info gain (unstable)
  → No future-case validation possible (0 independent future cases)
  → Ceiling effect (96% KEEP_SEPARATE) prevents boundary learning

TLD_RELATIONSHIP = INDEPENDENT
  → High-value feedback does NOT concentrate on TLD failure
  → TLD failure cases (AMB-135/262/313/462) all produce snap judgments
  → Highest-value case (AMB-032) has TLD CORRECT — value is in evidence distillation
  → TLD is independent Evidence Quality problem, not human learning bottleneck

LEARNING_LEVEL = L3 (Candidate Discovery — unchanged)

KEY FINDING:
  Human Feedback has been CAPTURED but not REUSED.
  5 signal candidates exist (LSC-01 to LSC-05 / CS1-CS4).
  None reached L4 (Human-Validated Reusable Signal).
  The fundamental barrier is the STABILITY-NOVELTY PARADOX:
    - Stable signals are redundant (Machine already has evidence → LOW info gain)
    - Novel signals are unstable (Human reviewers disagree → no stable boundary)
  Additionally, the only signal with cross-document recurrence (DCE-02: period+capital)
  has 33% false positives on P7 → NOT generalizable.

  AMB-032 and AMB-375 are high-engagement cases but:
    - AMB-032: reveals L3 Evidence Distillation gap (B2 doesn't expose TLD info) — NOT a reusable signal
    - AMB-375: reveals genuine boundary (sentence vs paragraph) — but boundary is unstable

STOP = TRUE
```

---

## 2. Current Human Feedback Loop

```
Human Feedback Sources:
  1. GT Reviewer Rationales: 90 (45 cases × 2 reviewers) + 4 adjudicator rationales = 94
  2. L5 Experiment (P722): 55 judgments (A=15, B1=10, B2=30)
  3. Pilot (P01): 27 judgments (4 with free-text feedback)
  Total: 176 feedback instances

Feedback Taxonomy (from Learning Signal Audit):
  BOUNDARY_CONFIRMATION: 116 (91%) — Human confirms Machine existing evidence
  CONFLICT_SIGNAL: 4 (3%) — Reviewer disagreement
  HUMAN_ONLY_INFORMATION: 4 (3%) — Free-text feedback with novel info
  EVIDENCE_SUFFICIENCY_SIGNAL: 2 (2%) — Human signals evidence insufficiency
  BOUNDARY_CORRECTION: 1 (1%) — Human corrects Machine error

→ 91% of feedback is REDUNDANT CONFIRMATION.
→ Only 9% contains potentially new information.
→ Of the 9%, most is UNSTABLE (reviewer disagreement).
```

---

## 3. V1 Immediate Review Value

| Case Type | Count | V1 Value | Reason |
|---|---|---|---|
| Type A (Machine correct) | 24 | LOW | Machine already correct, human confirms in <3s |
| Type D_LOW (Machine abstain) | 15 | LOW-MEDIUM | Human resolves quickly, but machine was uncertain |
| Type E (Genuine boundary) | 5 | MEDIUM-HIGH | Human judgment matters, genuine ambiguity |
| Type B (Machine error) | 1 | LOW | Human corrects trivially (2.2s) |

**V1 Summary**: Only 5/45 cases (11%) have genuine Review Value where human judgment is necessary. 87% of cases could be resolved without human review.

---

## 4. V2 Feedback Information Gain

### F0-F4 Classification

| F-Type | Count | % | Description |
|---|---|---|---|
| F0 (answer only) | 55 | 59% | L5 judgments with no rationale, just KEEP/MERGE/UNKNOWN |
| F1 (case-specific) | 0 | 0% | No purely case-specific explanations found |
| F2 (confirms existing evidence) | 78 | 83% | Rationales confirm TLD/P1 evidence (table, column, cell, number) |
| F3 (reveals ignored relation) | 12 | 13% | Reveals period+capital sentence boundary (existing P1, system ignores) |
| F4 (exposes new requirement) | 4 | 4% | Adjudicated cases expose boundary (sentence vs paragraph) |

**Key**: F3 and F4 cases are the ONLY feedback with potential new information. All 4 F4 cases are the adjudicated cases (AMB-005/375/418/519), all sharing the SAME pattern: period_end + cap_start.

### Information Gain by Case

| Case | F-Type | Info Gain | Reason |
|---|---|---|---|
| AMB-032 | F2 | LOW (A) / HIGH (B2) | A: confirms TLD. B2: UNKNOWN reveals distillation gap |
| AMB-375 | F3/F4 | HIGH | Reviewer disagreement + UNKNOWN = genuine boundary |
| AMB-135 | F2 | LOW | Human corrects TLD FP, but uses page visual not system evidence |
| AMB-262 | F2 | LOW | Human resolves TLD abstain, snap judgment |
| AMB-313 | F2 | LOW | Human overrides cue, snap judgment |
| AMB-462 | F2 | LOW | Human overrides cue, snap judgment |
| AMB-005 | F3/F4 | HIGH | Adjudicated: period+capital vs paragraph flow |
| AMB-418 | F3/F4 | HIGH | Adjudicated: same pattern |
| AMB-519 | F3/F4 | HIGH | Adjudicated: same pattern |

---

## 5. V3 Reusable Signal Potential

### Signal Candidate Table

| signal_id | source_cases | feedback_type | value_type | evidence_grounded | evidence_source | new_information | interpretation_level | recurrence_same_page | recurrence_same_doc | recurrence_cross_doc | future_validation | reuse_level | current_status | reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SIG-01 (LSC-01/CS1) | 9 IS-11 + 17 total | F2 | Review/Reuse | YES | TLD (different_cell) | NO | L2 | 5 (resnet p6) | 3 docs | 3 docs | LOW (1 future case) | R3 | CANDIDATE | Stable but redundant (LOW info gain). Machine already has TLD evidence. Ceiling effect. |
| SIG-02 (LSC-02/CS2) | 4 IS-11 adjudicated | F3/F4 | Boundary | PARTIAL | P1 (text_a, text_b) | YES (boundary) | L3-L4 | 0 | 3 docs | 7 docs (IS-11+P7) | MEDIUM (15 P7 cases) | R4 | CANDIDATE (with counterexamples) | Cross-doc recurrence BUT 5/15 P7 FP. Boundary unstable (reviewer disagreement). |
| SIG-03 (LSC-03/CS3) | 2 IS-11 | F2 | Review | YES | P1 (fig prefix) | NO | L2 | 1 (med p20) | 1 doc | 1 doc | LOW | R2 | CANDIDATE | Stable but 1 doc only, LOW info gain. |
| SIG-04 (LSC-04) | 5 IS-11 | F2 | Review | YES | P1 (IS-01/IS-02) | NO | L2 | 0 | 4 docs | 4 docs | LOW | R3 | CANDIDATE | Stable but VERY LOW info gain (redundant). |
| SIG-05 (LSC-05) | 4 IS-11 | F2 | Review | YES | TLD (different_cell) | NO | L2 | 2 | 2 docs | 2 docs | LOW | R3 | CANDIDATE | Stable but redundant, ceiling effect. |
| SIG-06 (DCE-02 expanded) | 4 IS-11 + 15 P7 | F3/F4 | Boundary | YES | P1 (period+capital) | YES (boundary) | L3 | 0 | 3+4 docs | 7 docs | MEDIUM (15 P7) | R4 | NOT_REUSABLE | 33% FP on P7. Pattern is corpus-specific. |
| SIG-07 (AMB-032 distillation) | 1 IS-11 | F2→F4 | Distillation | YES | TLD (different_cell) | YES (distillation gap) | L3 | 0 | 1 doc | 1 doc | NONE | R1 | NOT_REUSABLE | One-off. Reveals B2 doesn't expose TLD info. Not a reusable signal. |
| SIG-08 (AMB-375 boundary) | 1 IS-11 | F4 | Boundary | PARTIAL | P1 (period+capital) | YES (boundary) | L4 | 0 | 1 doc | 3 docs | MEDIUM | R2 | CANDIDATE (unstable) | Genuine boundary but reviewer disagreement. Unstable. |

### Reuse Level Distribution

| Reuse Level | Count | Description |
|---|---|---|
| R0 (case-specific) | 0 | — |
| R1 (local reuse) | 1 | SIG-07 (AMB-032 distillation gap) |
| R2 (repeated) | 2 | SIG-03, SIG-08 |
| R3 (cross-page) | 3 | SIG-01, SIG-04, SIG-05 |
| R4 (cross-document) | 2 | SIG-02, SIG-06 (BUT with counterexamples) |
| R5 (stable future reuse) | 0 | NONE |
| R6 (measured HRR) | 0 | NONE |

**No signal reached R5 or R6. The highest is R4, but with 33% false positives.**

---

## 6. V4 Boundary Value

### Boundary Signal Analysis

| Boundary Type | Cases | Evidence | Stable? | Reusable? |
|---|---|---|---|---|
| Sentence vs Paragraph (period+capital) | 4 IS-11 + 15 P7 | P1 text | NO (reviewer disagreement 3/3, 5/15 P7 FP) | NO |
| Table cell vs Prose | 0 explicit | TLD | N/A | N/A |
| Figure caption vs Body text | 2 IS-11 | P1 (fig prefix) | YES (2/2) | PARTIAL (1 doc) |
| Evidence distillation boundary | 1 (AMB-032) | TLD+B2 | UNKNOWN (1 case) | NO (one-off) |

**Key**: The ONLY genuine boundary signal (sentence vs paragraph) is UNSTABLE. Reviewer A sees sentence boundary → KEEP_SEPARATE. Reviewer B sees paragraph flow → MERGE. Adjudicator resolves with period+capital rule, but P7 shows 33% of period+capital cases are actually MERGE.

### Abstention Boundary Value

```
AMB-032 (B2 UNKNOWN):
  Machine: TLD correct (different_cell=True)
  Human B2: UNKNOWN (45.9s, 7 expansions)
  → Boundary: "when evidence is distilled but not exposed, system should abstain"
  → But this is an Evidence Distillation gap, not a judgment boundary

AMB-375 (B2 UNKNOWN):
  Machine: ABSTAIN
  Human B2: UNKNOWN (31.3s, 7 expansions)
  → Boundary: "period+capital is insufficient for sentence boundary determination"
  → This IS a genuine abstention boundary
  → But it's UNSTABLE (Reviewer A: KS, Reviewer B: MERGE)
```

---

## 7. AMB-032 Analysis

### Evidence → Feedback → Signal Trace

```
Case: AMB-032
  text_a = "-", text_b = "8.43"
  GT: KEEP_SEPARATE (agreed, both reviewers)

Machine Evidence:
  P1: text_a="-", text_b="8.43"
  P2: bbox_a=[...], bbox_b=[...], same_y_band=True, h_gap=...
  TLD: table detected, A=[29,1], B=[29,2], different_cell=True
  IS-01: is01_a=True ("-" matches number regex)
  IS-02: is02_b=False ("8.43" has no alpha > 2)
  IS-11: different_cell → KEEP_SEPARATE (TN, correct)

Human Decision:
  Condition A (full evidence): KEEP_SEPARATE (1.8s, 0 expansions)
  Condition B2 (distilled): UNKNOWN (45.9s, 7 expansions)
    Expanded: h_gap, dy, same_style, width_a, width_b, style_sig_a, style_sig_b
    Did NOT inspect cue
    final_correct = False (UNKNOWN ≠ KEEP_SEPARATE)

Feedback Analysis:
  What did human provide? UNKNOWN in B2
  → Human could NOT resolve with distilled evidence
  → Human expanded 7 fields but still couldn't determine
  → In Condition A (full evidence), human resolved in 1.8s

  New information? YES — B2 evidence distillation FAILS to support human
  Evidence-grounded? YES — TLD has different_cell, but B2 doesn't expose it
  Repeated elsewhere? NO — only 1 such case (AMB-375 is similar but different mechanism)
  Cross-document? NO — 1 case, 1 document
  Future validation? NONE — no similar cases in P7

Four-way classification:
  A. New Evidence? NO — TLD already has different_cell
  B. New Interpretation? NO — human uses same evidence as TLD
  C. Better Evidence Distillation? YES — B2 doesn't expose TLD's different_cell
  D. New Reusable Knowledge? NO — one-off observation

Reuse Status:
  R1 (local reuse possible) — only for this case
  NOT a reusable signal. It's an Evidence Distillation Gap observation.

AMB-032 = L3 Evidence Distillation Value (NOT Reusable Signal)
```

---

## 8. AMB-375 Analysis

### Evidence → Feedback → Signal Trace

```
Case: AMB-375
  text_a = "[23].", text_b = "Each"
  GT: KEEP_SEPARATE (ADJUDICATED — Reviewer A: KS, Reviewer B: MERGE)

Machine Evidence:
  P1: text_a="[23].", text_b="Each"
  P2: bbox_a=[...], bbox_b=[...], same_y_band=True
  TLD: 0 tables (not table content)
  IS-01: is01_a=False ("[23]." not pure number)
  IS-02: is02_b=True ("Each" has alpha > 2)
  IS-11: is01=False, is02=True → mixed → ABSTAIN

Human Decision:
  Reviewer A: KEEP_SEPARATE — "[23]." ends sentence, "Each" begins next sentence
  Reviewer B: MERGE — same paragraph, citation ends sentence, "Each" begins next in same flow
  Adjudicator: period + capital → KEEP_SEPARATE
  
  Condition A: KEEP_SEPARATE (8.1s, 0 expansions)
  Condition B2: UNKNOWN (31.3s, 7 expansions) — couldn't resolve
    Also: KEEP_SEPARATE (3.5s, 0 expansions, cue_followed=True) — resolved with cue

Feedback Analysis:
  What did human provide? Reviewer DISAGREEMENT (A: KS, B: MERGE)
  → This reveals a GENUINE BOUNDARY: sentence boundary vs paragraph continuation
  → Both interpretations are valid:
    - "Sentence boundary" → different semantic units → KEEP_SEPARATE
    - "Paragraph flow" → same discourse unit → MERGE

  New information? YES — exposes boundary that Machine cannot resolve
  Evidence-grounded? PARTIAL — period+capital is detectable (P1) but INSUFFICIENT
    → P7 proves: 5/15 period+capital cases are MERGE (paragraph continuation)
    → Period+capital is NECESSARY but NOT SUFFICIENT for sentence boundary
  Repeated elsewhere? YES — AMB-005, AMB-418, AMB-519 (all adjudicated, same pattern)
  Cross-document? YES — 3 IS-11 docs + 4 P7 docs = 7 docs
  Future validation? MEDIUM — 15 P7 cases available, but 5 are counterexamples

Four-way classification:
  A. New Evidence? NO — period+capital already in P1
  B. New Interpretation? YES — "sentence boundary" interpretation vs "paragraph flow"
  C. Better Evidence Distillation? UNKNOWN — could help but boundary is unstable
  D. New Reusable Knowledge? NO — boundary is unstable (reviewer disagreement + P7 FP)

Reuse Status:
  R2 (repeated) — 4 IS-11 cases
  R4 (cross-document) — 7 docs, BUT 33% FP on P7
  NOT R5 — no stable future-case reuse (counterexamples exist)

AMB-375 = Boundary Value (genuine but UNSTABLE boundary, NOT reusable signal)
```

---

## 9. AMB-135 Counterexample

### Why Machine Error ≠ Reusable Signal

```
Case: AMB-135
  text_a = "4", text_b = "MBConv6, k5x5"
  GT: KEEP_SEPARATE (agreed)

Machine: MERGE (FP) — TLD page-global contamination (DCE-06 Mechanism 1)
  → TLD fails to detect table → no different_cell → fallback → is01+is02 → MERGE

Human: KEEP_SEPARATE (2.2s, 0 expansions — snap judgment)
  → Human sees page visual: "4" and "MBConv6" are in different table columns

Feedback Analysis:
  What did human provide? KEEP_SEPARATE (correct)
  New information? NO — human uses page visual, not system evidence
  Evidence-grounded? NO — human uses visual inspection, not P1/P2/TLD
  Repeated elsewhere? YES — AMB-262, AMB-313 (same TLD failure mechanism)
  Cross-document? YES — EfficientNet pages
  Future validation? LOW — DCE-07 proved no safe fix for TLD locality

WHY no reusable signal:
  1. Human correction is VISUAL, not evidence-based
     → Human sees table structure on page → corrects immediately
     → System doesn't have page visual → cannot learn from this correction
  2. TLD failure mechanism is IDENTIFIED (DCE-06) but UNFIXABLE (DCE-07)
     → The "signal" is "TLD should detect this table" — but DCE-07 proved no safe fix
     → Adding locality creates false positives on prose (AMB-008, AMB-042)
  3. Correction is case-specific (page-global contamination on specific page layouts)
     → No generalizable rule can be extracted
  4. The error would disappear if TLD detection improved
     → But TLD is FROZEN and DCE-07 closed the fix route

  A. New Evidence? NO
  B. New Interpretation? NO (human uses visual, not interpretation)
  C. Better Evidence Distillation? NO (TLD fails, not distillation)
  D. New Reusable Knowledge? NO (DCE-07 proved no safe fix)

AMB-135 = Type B (Machine Error / Low Reuse). Correction is case-specific and unfixable.
```

---

## 10. AMB-313 / AMB-462 Analysis

### Perception Failure vs Learning Opportunity

```
AMB-313:
  text_a = "Test Size", text_b = "#Classes"
  GT: KEEP_SEPARATE (agreed)
  Machine: ABSTAIN (TLD page-global contamination, Mechanism 1)
  Human: KEEP_SEPARATE (3.9s B2, 0 expansions, override=True)
    → Human overrides cue, snap judgment

  Classification: EVIDENCE PERCEPTION FAILURE (TLD Mechanism 1)
  → NOT a Feedback Learning Opportunity
  → Human uses page visual (sees table header row)
  → System doesn't have page visual → cannot learn
  → Same as AMB-135: case-specific, unfixable

AMB-462:
  text_a = "WGe", text_b = "Avg."
  GT: KEEP_SEPARATE (agreed)
  Machine: ABSTAIN (TLD Mechanism 2 — inherent low text_ratio)
  Human: KEEP_SEPARATE (2.3s B2, 0 expansions, override=True in one B2 instance)
    → Human overrides cue, snap judgment

  Classification: EVIDENCE PERCEPTION FAILURE (TLD Mechanism 2)
  → NOT a Feedback Learning Opportunity
  → Human uses page visual (sees benchmark table)
  → System doesn't have page visual → cannot learn
  → text_ratio=0.163 is inherent (numeric table) → DCE-07 can't fix

Both AMB-313 and AMB-462:
  → Evidence Perception Failure (L1)
  → NOT Feedback Learning Opportunity (L3/L4)
  → NOT Evaluation/Case Construction issue
  → Human correction is VISUAL, not evidence-based
  → No reusable signal can be extracted
```

---

## 11. Cross-Case Recurrence

### SIG-02 (Period+Capital Sentence Boundary) — Most Recurrent

| Corpus | Cases | KEEP_SEPARATE | MERGE | Adjudicated | Precision |
|---|---|---|---|---|---|
| IS-11 | 4 | 4 | 0 | 4 | 100% |
| P7 | 15 | 10 | 5 | 0 | 67% |
| Combined | 19 | 14 | 5 | 4 | 74% |

**Cross-document**: 7 documents (3 IS-11 + 4 P7)

**Independence**: 
- IS-11: 3 docs, 4 pages — INDEPENDENT
- P7: 4 docs, 15 cases — INDEPENDENT
- Total: 7 docs, 19 cases — INDEPENDENT

**BUT**: 5/15 P7 cases are MERGE (false positives for KEEP_SEPARATE rule)
→ Pattern is NOT universal
→ Period+capital is NECESSARY but NOT SUFFICIENT for sentence boundary

### Other Signals — Recurrence

| Signal | Same Page | Same Doc | Cross-Doc | Independent? |
|---|---|---|---|---|
| SIG-01 (table numeric diff_cell) | 5 (resnet p6) | 3 docs | 3 docs | PARTIAL (55% on one page) |
| SIG-03 (figure caption) | 1 (med p20) | 1 doc | 1 doc | NO |
| SIG-04 (mixed numeric text) | 0 | 4 docs | 4 docs | YES |
| SIG-05 (table diff_cell non-numeric) | 2 | 2 docs | 2 docs | YES |

**Warning**: SIG-01 has 5 cases on resnet page 6 — these are NOT 5 independent examples. They are 5 cells from the SAME table on the SAME page. Independence audit requires counting this as 1 independent observation.

---

## 12. Cross-Document Recurrence

| Signal | Documents | Truly Independent? | Counterexamples? |
|---|---|---|---|
| SIG-01 | 3 (resnet, efficientnet, med) | PARTIAL (55% on resnet p6) | NO (but ceiling effect) |
| SIG-02 | 7 (3 IS-11 + 4 P7) | YES | YES (5/15 P7 MERGE) |
| SIG-03 | 1 (med) | NO | NO |
| SIG-04 | 4 (resnet, efficientnet, med, cs) | YES | NO (but no negatives) |
| SIG-05 | 2 (resnet, efficientnet) | YES | NO (but ceiling effect) |

**Only SIG-02 has cross-document recurrence with counterexamples.**
**SIG-04 has cross-document recurrence but no counterexamples (ceiling effect — all KEEP_SEPARATE).**

---

## 13. Future Validation Availability

| Signal | Future Cases Available | Validation Feasibility | Counterexamples? |
|---|---|---|---|
| SIG-01 | 1 (P7 TABLE_CELL) | LOW | NO but ceiling |
| SIG-02 | 15 (P7 BODY_TEXT) | MEDIUM | YES (5 MERGE) |
| SIG-03 | 0 | NONE | NO |
| SIG-04 | 0 | NONE | NO |
| SIG-05 | 0 | NONE | NO |
| SIG-07 (distillation) | 0 | NONE | N/A |
| SIG-08 (boundary) | 15 (P7) | MEDIUM | YES (5 MERGE) |

**Key**: Only SIG-02/SIG-08 have meaningful future validation cases (15 P7). But 5/15 are counterexamples. No signal has future cases WITHOUT counterexamples.

---

## 14. TLD × Feedback Value

```
                 Feedback Value
                 LOW       MEDIUM       HIGH
TLD Correct       24         1            1
  (TN=26)        (Type A   (AMB-005    (AMB-032
                  snap)     adj, snap)   B2 UNKNOWN,
                                         7 exp, distillation gap)

TLD Wrong          1         0            0
  (FP=1)        (AMB-135
                  snap)

TLD Missing       12         0            3
  (ABSTAIN=18)   (Type D    -           (AMB-375/418/519
                  LOW snap              all adjudicated,
                  judgments)            HIGH boundary value)
                                         
                                         But: all 3 are period+capital
                                         pattern → same signal, not 3
                                         independent signals

TLD Missing + Override  3    0            0
  (AMB-313/462/519)  (snap)
```

**Key findings**:
1. HIGH feedback value does NOT concentrate on TLD failure
2. The highest-value case (AMB-032) has TLD CORRECT — value is in evidence distillation
3. TLD failure cases (AMB-135/262/313/462) all produce LOW-value snap judgments
4. The 3 HIGH-value TLD-missing cases (AMB-375/418/519) share the SAME signal (period+capital)
5. TLD is INDEPENDENT of feedback value

**CONCLUSION: TLD = Independent Evidence Quality Problem. NOT the human learning bottleneck.**

---

## 15. Case Selection × Feedback Value

### Content Type × Feedback Value

| Content Type | IS-11 Count | HIGH Value | MEDIUM Value | LOW Value |
|---|---|---|---|---|
| TABLE_NUMERIC | 20 | 0 | 0 | 20 |
| TABLE_TEXT | 20 | 1 (AMB-032) | 0 | 19 |
| PROSE | 3 | 3 (AMB-005/375/519) | 0 | 0 |
| FIGURE | 2 | 1 (AMB-418) | 0 | 1 |

**CRITICAL FINDING: 100% of HIGH-value cases are PROSE or non-table content.**
- 3/3 PROSE cases are HIGH value (all adjudicated)
- 1/2 FIGURE cases is HIGH value (adjudicated)
- Only 1/40 TABLE cases is HIGH value (AMB-032, and it's about distillation not table content)
- 0/20 TABLE_NUMERIC cases are HIGH value

**This means the current selection (88% TABLE) is systematically EXCLUDING the highest-value feedback type (PROSE/BOUNDARY).**

### P7 Content Type × Potential Value

| P7 Content Type | Count | Potential HIGH Value? | Reason |
|---|---|---|---|
| BODY_TEXT_CONTINUATION | 27 | YES | Sentence/paragraph boundaries — same as IS-11 adjudicated |
| REFERENCE_LIST_ENTRY | 16 | POSSIBLE | Citation format boundaries — not in IS-11 |
| OTHER_AMBIGUOUS | 9 | POSSIBLE | Cross-category boundaries — not in IS-11 |
| TABLE_CELL | 11 | LOW | Same as IS-11 TABLE (snap judgments) |
| MERGE cases | 24 | YES | Harder cases, more likely to produce boundaries |

**P7 has 27 BODY_TEXT + 16 REFERENCE + 9 OTHER = 52 potentially high-value cases that IS-11 completely misses.**

BUT: P7 human review data is incomplete (all labels UNKNOWN). Cannot confirm potential value without human review.

---

## 16. Four-Layer Value Decomposition Summary

| Value Layer | HIGH | MEDIUM | LOW | NONE |
|---|---|---|---|---|
| V1 Review Value | 5 (11%) | 0 | 39 (87%) | 1 (2%) |
| V2 Info Gain | 7 (16%) | 0 | 38 (84%) | 0 |
| V3 Reuse Potential | 0 | 2 (4%) | 6 (13%) | 37 (82%) |
| V4 Boundary Value | 1 (2%) | 3 (7%) | 0 | 41 (91%) |

**Key**: V1 and V2 have some HIGH cases, but V3 (Reuse) and V4 (Boundary) are overwhelmingly LOW/NONE. The gap between "Human can provide value" (V1/V2) and "Value can be reused" (V3/V4) is the core problem.

---

## 17. Failure / Missing Evidence

### Why No Reusable Signal Has Emerged

```
1. CEILING EFFECT (96% KEEP_SEPARATE)
   → All candidates are positive-only (0 negative cases)
   → Cannot learn boundaries (no counterexamples in IS-11)
   → P7 has counterexamples but no human review data

2. STABILITY-NOVELTY PARADOX
   → Stable signals (SIG-01/04/05) are REDUNDANT (Machine already has evidence)
   → Novel signals (SIG-02/08) are UNSTABLE (reviewer disagreement + P7 FP)
   → No signal is both stable AND novel

3. IMAGE CONFOUND
   → Human always sees page image in experiments
   → Human corrections often based on VISUAL inspection, not system evidence
   → Cannot distinguish "evidence-based feedback" from "visual-based feedback"
   → n=1 participant prevents cross-participant validation

4. NO FUTURE CASES
   → 0 independent future cases for most signals
   → Only SIG-02 has 15 P7 cases, but 5 are counterexamples
   → Cannot validate reuse without future cases

5. CONTENT TYPE BIAS
   → IS-11 is 88% TABLE → 0/40 TABLE cases have HIGH reuse value
   → 100% of HIGH-value cases are PROSE/FIGURE (non-table)
   → Selection systematically excludes high-value content types
```

---

## 18. Final Research Judgment

### Q1: 过去 Human Feedback 中有没有真正的 Reusable Signal?

**INSUFFICIENT EVIDENCE.**

- 5 signal candidates exist (LSC-01 to LSC-05)
- None reached R5 (stable future-case reuse) or R6 (measured HRR)
- Highest: R4 (SIG-02, cross-document recurrence) but with 33% false positives
- The only cross-document signal (period+capital) is NOT universal (P7 proves 33% FP)
- All other signals are either redundant (LOW info gain) or one-off

### Q2: 如果没有，是因为什么?

**MIXED — three factors combine:**

1. **Feedback itself has limited reuse value**: 91% is BOUNDARY_CONFIRMATION (redundant). Only 9% has new info, and most of that is unstable.

2. **System doesn't capture/express feedback correctly**: AMB-032 shows B2 distillation fails to expose TLD info. The system HAS evidence but doesn't DISTILL it for human use. This is an L3 (Evidence Distillation) gap.

3. **Not enough repeated cases**: IS-11 has only 4 adjudicated cases (all same pattern). P7 has 15 similar cases but no human review data. No independent future cases for validation.

### Q3: 当前最大瓶颈

**Ranked by evidence:**

1. **FEEDBACK_GENERALIZATION** (primary): Stability-Novelty Paradox. Stable signals redundant, novel signals unstable. No signal is both stable AND novel.

2. **FUTURE_VALIDATION** (secondary): 0 independent future cases for most signals. Only SIG-02 has P7 cases but with counterexamples.

3. **CASE_SELECTION** (tertiary): 88% TABLE bias excludes high-value PROSE/BOUNDARY content. 53% of selected cases are Type A (wasted).

4. **EVIDENCE_DISTILLATION** (tertiary): AMB-032 shows B2 fails to expose TLD info. But this is a presentation issue, not a feedback capture issue.

5. **FEEDBACK_CAPTURE** (not a bottleneck): Feedback IS captured (176 instances, L0-L2 achieved). The issue is what to DO with captured feedback.

### Q4: AMB-032 与 AMB-375 到底属于什么?

**AMB-032 = One-off useful feedback (NOT reusable signal)**
- Reveals L3 Evidence Distillation gap (B2 doesn't expose TLD different_cell)
- This is a SYSTEM PRESENTATION issue, not a FEEDBACK SIGNAL
- No cross-case recurrence, no future validation cases
- R1 (local reuse only)

**AMB-375 = Potential reusable signal (BUT unstable)**
- Reveals genuine boundary (sentence vs paragraph continuation)
- Cross-document recurrence (7 docs)
- BUT: reviewer disagreement (unstable) + 33% P7 FP (not universal)
- R2 (repeated) to R4 (cross-document) but NOT R5 (not stable)

### Q5: 如果存在 Potential Reusable Signal，下一步应该验证还是工程化?

**VALIDATION, not engineering.**

- No signal has reached R5 (stable future reuse)
- The only cross-document signal (SIG-02) has counterexamples
- Engineering a signal with 33% FP would introduce errors
- Next step: VALIDATE on P7 cases (15 available) with human review
- BUT: P7 human review data is incomplete (all UNKNOWN)
- AND: even if validated, the signal is corpus-specific (period+capital ≠ universal)

**Principle: Potential → Validation → Validated → Reuse → Engineering. Cannot skip steps.**

---

## 19. Next Route Recommendation

```
NEXT_ROUTE = ROUTE_E (MIXED)

  L2 (Case Selection): Redesign to include PROSE/BOUNDARY content (P7 BODY_TEXT, REFERENCE)
    → 100% of HIGH-value IS-11 cases are non-table
    → IS-11 excludes the highest-value content types
  
  L3 (Evidence Distillation): Redesign B2 to expose TLD structural info
    → AMB-032 proves B2 fails to expose different_cell
    → B2 is SLOWER than A (5.9s vs 2.2s) — adds load without benefit
  
  L4 (Feedback Generalization): Address Stability-Novelty Paradox
    → Need more DIVERSE cases (MERGE, CONFLICT, UNKNOWN)
    → Need more PARTICIPANTS (n=1 currently)
    → Need IMAGE-FREE test (separate visual from evidence)
  
  L1 (TLD/Evidence): Independent problem, NOT primary
    → DCE-07 closed locality route
    → TLD failure doesn't produce high-value feedback
  
  NOTE: This route does NOT authorize implementation.
  It identifies where future RESEARCH should focus.
```

---

## 20. Anti-Overdesign Gate

```
NEW_OBSERVATION_NEEDED = NO
  P1/P2/TLD provide sufficient evidence. Issue is generalization, not missing evidence.

NEW_MODULE_NEEDED = NO
  No new module would help. Issue is validation, not architecture.

NEW_ENGINE_NEEDED = NO
  No new engine needed.

LLM_NEEDED = NO
  Feedback generalization is a data/validation problem, not semantic understanding.

FORBIDDEN ESCALATIONS:
  ✗ Feedback Generalization → "Learning Engine" (NO)
  ✗ Stability-Novelty Paradox → "Pattern Engine" (NO)
  ✗ Evidence Distillation Gap → "Evidence Organization Engine" (NO)
  ✗ Boundary Instability → "LLM" (NO)
  ✗ Case Selection → "Intelligent Case Selector" (NO)
```

---

## 21. Governance Gate

```
HVA-02 STATUS = INSUFFICIENT EVIDENCE

REUSABLE_SIGNAL = INSUFFICIENT EVIDENCE
HIGHEST_REUSE_LEVEL = R4 (with counterexamples — NOT validated)
BOUNDARY_SIGNAL = PARTIAL
PRIMARY_BOTTLENECK = MIXED (Feedback Generalization + Future Validation)
TLD_RELATIONSHIP = INDEPENDENT
LEARNING_LEVEL = L3
ENGINEERING_REQUIRED = NO
EXPERIMENT_REQUIRED = NOT_YET

DICE_CORE_MODIFICATION              = NO
P1_P7_MODIFICATION                  = NO
P2_MODIFICATION                     = NO
TLD_MODIFICATION                    = NO
IS11_MODIFICATION                   = NO
M_B_MODIFICATION                    = NO
GT_MODIFICATION                     = NO
SIGNAL_MODIFICATION                 = NO
EVIDENCE_CUE_MODIFICATION           = NO

LLM                                 = NO
NEW_OBSERVATION                     = NO
NEW_MODULE                          = NO
NEW_ENGINE                          = NO

RUNTIME_CHANGE                      = NO
CAPABILITY_CHANGE                   = NO

FROZEN_BASELINE                     = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d)
FROZEN_EXPERIMENT                   = INTACT

IMPLEMENTATION_AUTHORIZED           = FALSE
EXPERIMENT_AUTHORIZED               = FALSE
FORMAL_EXPERIMENT                   = NOT_STARTED
PRODUCTION                          = FALSE

STOP                                = TRUE
```

---

## 22. Final Answer

> **我们现在有没有证据证明 Human Feedback 可以被 System 跨 Case 复用？**

**没有。**

- 没有 Signal 达到 R5（稳定未来 Case 复用）
- 没有 Signal 达到 R6（可测量的 HRR 且质量不降）
- 最高的 R4（跨文档复现）有 33% 假阳性
- 所有稳定 Signal 都是冗余的（机器已有证据）
- 所有新颖 Signal 都不稳定（人类评审分歧 + P7 反例）
- 0 个独立未来 Case 可用于验证（P7 有 Case 但无人类审阅数据）

**当前状态：5 个 Candidate 存在，但 0 个 Validated。Learning Level = L3（Candidate Discovery），不是 L4+（Validated Reusable Signal）。**

`STOP = TRUE`。
