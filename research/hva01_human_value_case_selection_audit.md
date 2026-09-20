# HVA-01 Human Value-Aware Case Selection Audit

**Date**: 2026-09-16
**Mode**: READ-ONLY / AUDIT ONLY / NO IMPLEMENTATION / FROZEN INTACT / STOP
**Predecessors**: DCE-05/06/07, L5 Learning Signal Audit, Information Gain Audit, Feedback Reuse Audit, Next Direction Audit

---

## 1. Executive Summary

```
HVA-01 STATUS = CONDITIONAL

PRIMARY BOTTLENECK = L2 (Case Selection) + L3 (Evidence Distillation)
SECONDARY BOTTLENECK = L1 (Evidence/Perception — TLD, but NOT primary for human learning)

KEY FINDING:
  Current Case Selection optimizes for GEOMETRIC AMBIGUITY, not LEARNING VALUE.

  53% of 45 IS-11 cases are Type A (Machine-Decisive / Low Learning Value):
    Machine already correct, Human confirms in <3s, 0 evidence expansions.
    → Wasted human review effort.

  33% are Type D_LOW (Machine Uncertain / Human Resolves Quickly):
    Machine abstains, Human resolves as snap judgment (<5s, 0 expansions).
    → Feedback confirms what Human sees visually, no reusable signal extracted.

  Only 11% (5 cases) are Type E (Genuine Boundary):
    Adjudicated or UNKNOWN. But only 2/5 had high engagement (7 expansions).
    → True high learning value = 2/45 (4%).

  88% of content is TABLE-related (TABLE_NUMERIC + TABLE_TEXT).
  Only 7% PROSE, 4% FIGURE.
  → Severe content type bias. P7 has more diversity (27 BODY_TEXT, 16 REFERENCE).

TLD × LEARNING VALUE MATRIX:
  TLD failure does NOT systematically produce high learning value.
  83% of TLD failures (15/18 ABSTAIN) are resolved as snap judgments.
  Learning value comes from REVIEWER DISAGREEMENT (adjudicated), not TLD failure.
  TLD is an independent Evidence Quality Problem, NOT the human learning bottleneck.

L5 HUMAN BEHAVIOR EVIDENCE:
  69% of decisions made in <3 seconds (snap judgments)
  96% had NO evidence expansion
  96% viewed only 1 evidence level
  Only 2 cases (AMB-032, AMB-375) had high engagement → both UNKNOWN
  → Most human review produces BOUNDARY_CONFIRMATION, not new information.

COUNTERFACTUAL:
  If selection prioritized high learning value cases:
  - Human review could reduce from 45 to ~5-10 cases
  - But current "high gain" cases are temporary (Machine LOGIC GAP, per Info Gain Audit)
  - INSUFFICIENT EVIDENCE to claim true system improvement

NEXT_ROUTE = ROUTE E (MIXED)
  L2: Case Selection optimizes wrong metric
  L3: Evidence Distillation doesn't expose decision-relevant structure
  L1: TLD failure exists but is NOT the primary human learning bottleneck
  L4: Blocked downstream (ceiling effect, insufficient future cases)

STOP = TRUE
```

---

## 2. Data Sources

| Source | Count | Key Content |
|---|---|---|
| IS-11 GT (45 cases) | 45 | 43 KEEP_SEPARATE, 2 MERGE, 4 adjudicated |
| IS-11 Machine Eval | 45 | TN=26, ABSTAIN=18, FP=1, FN=0 |
| L5 Experiment (P722) | 55 judgments | Conditions A=15, B1=10, B2=30 |
| Pilot (P01) | 27 judgments | Workflows A=21, B=3, C=3 |
| P7 Evaluation | 69 cases | 6 boundary classes, 45 KS / 24 MERGE |
| Prior Audits | 9 files | DCE-05/06/07, Learning Signal, Info Gain, Feedback Reuse, Next Direction, Capability Boundary, Feedback Loop |

---

## 3. Case Class Distribution (45 IS-11 Cases)

| Class | Count | % | Description |
|---|---|---|---|
| Type_A | 24 | 53% | Machine decisive, Human snap judgment, no new info |
| Type_D_LOW | 15 | 33% | Machine uncertain, Human resolves quickly (snap) |
| Type_E | 5 | 11% | Genuine boundary (adjudicated or UNKNOWN) |
| Type_B | 1 | 2% | Machine error, Human corrects, case-specific |
| Type_C | 0 | 0% | Machine error + High reuse (NOT FOUND) |
| Type_D_HIGH | 0 | 0% | Machine uncertain + High reuse (NOT FOUND) |
| Type_F | 4 | 9% | Evidence/Perception failure (subset of above) |

**Key: 53% of human review is WASTED on cases where machine is already correct.**

---

## 4. L5 Human Behavior Evidence

### Decision Time and Engagement

| Metric | Value | Implication |
|---|---|---|
| Mean decision time | 4.1s | Snap judgments |
| <3s decisions | 69% | Most cases are trivially easy for humans |
| No evidence expansion | 96% | Humans don't examine evidence |
| Only 1 level viewed | 96% | Surface-level judgment only |
| High engagement (expansion ≥2) | 2/55 (4%) | Only AMB-032, AMB-375 |
| UNKNOWN outcomes | 2/55 (4%) | Only AMB-032, AMB-375 |
| Overrides | 2/55 (4%) | AMB-462, AMB-313 |

### Condition Comparison

| Condition | Count | Mean Time | Mean Exp | Correct | UNKNOWN |
|---|---|---|---|---|---|
| A (full evidence) | 15 | 2.2s | 0.0 | 14/15 (93%) | 0 |
| B1 (minimal) | 10 | 1.7s | 0.0 | 10/10 (100%) | 0 |
| B2 (distilled) | 30 | 5.9s | 0.5 | 28/30 (93%) | 2 |

**Critical finding: Condition A (full evidence) is FASTER than B2 (distilled evidence).**
This means the distilled evidence in B2 adds COGNITIVE LOAD without improving accuracy. The evidence presentation is not well designed for human decision-making.

---

## 5. Four-Layer Value Model

### L1 Evidence Value (Evidence exists and is correct?)

| Case Type | L1 Value | Evidence |
|---|---|---|
| Type_A (24 cases) | HIGH | P1/P2/TLD all working, machine decisive |
| Type_D_LOW (15 cases) | MEDIUM | P1/P2 exist, TLD fails or IS-11 fallback, evidence partial |
| Type_E (5 cases) | VARIABLE | Evidence exists but ambiguous (adjudicated) or complex (table structure) |
| Type_B (1 case, AMB-135) | LOW | TLD detection failure, evidence perception broken |

### L2 Human Review Value (Does human need to participate?)

| Case Type | L2 Value | Evidence |
|---|---|---|
| Type_A (24 cases) | LOW | Machine already correct, human confirms in <3s, no expansion |
| Type_D_LOW (15 cases) | LOW-MEDIUM | Human resolves quickly, but machine was uncertain |
| Type_E (5 cases) | MEDIUM-HIGH | Genuine boundary, human judgment matters |
| Type_B (1 case) | LOW | Human corrects easily (2.2s), but correction is case-specific |

### L3 Feedback Value (Does feedback contain new information?)

| Case Type | L3 Value | Evidence |
|---|---|---|
| Type_A (24 cases) | LOW | 91% BOUNDARY_CONFIRMATION (prior audit), no new info |
| Type_D_LOW (15 cases) | LOW-MEDIUM | Human resolves ambiguity, but 10/10 could be Machine logic gap (Info Gain Audit) |
| Type_E (5 cases) | MEDIUM-HIGH | Only 2/5 had high engagement; 3/5 were snap judgments despite adjudication |
| Type_B (1 case) | LOW | Correction is case-specific (TLD page-global contamination), no reusable signal |

### L4 Learning/Reuse Value (Can feedback improve future cases?)

| Case Type | L4 Value | Evidence |
|---|---|---|
| Type_A (24 cases) | LOW | Machine already has evidence, no improvement possible |
| Type_D_LOW (15 cases) | LOW | HIGH info gain is TEMPORARY (Machine LOGIC GAP, per Info Gain Audit) |
| Type_E (5 cases) | UNKNOWN | 2 high-engagement cases (032, 375) but both UNKNOWN — no stable signal |
| Type_B (1 case) | LOW | DCE-07 proved no safe fix, no reusable signal |
| All types | LOW | No candidate reached L4 (Learning Signal Audit), CS1 at R3 only (Feedback Reuse Audit) |

---

## 6. Case Value Profiles (Key Cases)

### AMB-135 (Type B — Machine Error / Low Reuse)

```
Case: AMB-135
Machine Output: MERGE (FP) — TLD page-global contamination
GT: KEEP_SEPARATE
Human Judgment: KEEP_SEPARATE (2.2s, 0 expansions — snap)

L1 Evidence Value: LOW (TLD detection failure)
L2 Human Review Value: LOW (human corrects trivially)
L3 Feedback Value: LOW (correction is case-specific, no reusable pattern)
L4 Learning Value: LOW (DCE-07 proved no safe fix)

Evidence → Human → Learning Trace:
  Machine: MERGE (wrong — TLD fails to detect table)
  → Human: sees "4" and "MBConv6" are different table columns → KEEP_SEPARATE
  → Feedback: KEEP_SEPARATE (confirms GT)
  → New information? NO — human uses page visual, not machine evidence
  → Evidence-grounded? NO — human uses visual inspection, not P1/P2/TLD
  → Repeated elsewhere? YES (AMB-262, AMB-313, AMB-462) but DCE-07 proved unsafe to fix
  → Reusable signal? NO — DCE-07 closed the locality route

Final: Type_B (Machine Error / Low Reuse). Human corrects but learning value is LOW.
```

### AMB-262 (Type D_LOW — Machine Uncertain / Low Reuse)

```
Case: AMB-262
Machine Output: ABSTAIN (TLD page-global contamination)
GT: KEEP_SEPARATE
Human Judgment: KEEP_SEPARATE (2.6s, 0 expansions — snap)

L1 Evidence Value: LOW (TLD detection failure)
L2 Human Review Value: LOW (human resolves trivially)
L3 Feedback Value: LOW (same as AMB-135 — case-specific TLD failure)
L4 Learning Value: LOW (DCE-07 closed locality route)

Final: Type_D_LOW. Machine uncertain, human resolves, but no reusable signal.
```

### AMB-032 (Type E — Genuine Boundary / High Engagement)

```
Case: AMB-032
Machine Output: KEEP_SEPARATE (TN — TLD correct)
GT: KEEP_SEPARATE
Human Judgment: UNKNOWN in B2 (45.9s, 7 expansions); KEEP_SEPARATE in A (1.8s, 0 expansions)

L1 Evidence Value: HIGH (TLD correct, evidence exists)
L2 Human Review Value: HIGH (human engaged deeply, 7 expansions, 45.9s)
L3 Feedback Value: MEDIUM (UNKNOWN in B2 — human couldn't resolve with distilled evidence)
  → But KEEP_SEPARATE in A — human could resolve with full evidence
  → Suggests evidence DISTILLATION (B2) is worse than full evidence (A)
L4 Learning Value: MEDIUM-HIGH (genuine boundary case, but UNKNOWN means no stable signal)

Evidence → Human → Learning Trace:
  Machine: KEEP_SEPARATE (correct — TLD detects table, different_cell)
  → Human B2: sees distilled evidence, expands 7 times, can't determine → UNKNOWN
  → Human A: sees full evidence, snap judgment → KEEP_SEPARATE
  → New information? YES — B2 evidence distillation FAILS to support human
  → Evidence-grounded? YES — TLD provides different_cell, but B2 doesn't expose it
  → Repeated elsewhere? UNKNOWN — only 1 such case
  → Reusable signal? POTENTIAL — "evidence distillation doesn't expose table structure"

Final: Type_E. Highest engagement case. Reveals evidence distillation gap (L3).
```

### AMB-375 (Type E — Genuine Boundary / High Engagement)

```
Case: AMB-375
Machine Output: ABSTAIN
GT: KEEP_SEPARATE (adjudicated — Reviewer A: KS, Reviewer B: MERGE)
Human Judgment: UNKNOWN in B2 (31.3s, 7 expansions); KEEP_SEPARATE in A (8.1s, 0 expansions)

L1 Evidence Value: MEDIUM (P1/P2 exist, IS-11 abstains, evidence partial)
L2 Human Review Value: HIGH (adjudicated + high engagement)
L3 Feedback Value: HIGH (reviewer disagreement + UNKNOWN = genuine boundary)
L4 Learning Value: MEDIUM (genuine boundary, but no stable signal extracted)

Evidence → Human → Learning Trace:
  Machine: ABSTAIN (IS-01=False, IS-02=False — "[23]." and "Each" both fail binary)
  → Reviewer A: KEEP_SEPARATE (citation + sentence start)
  → Reviewer B: MERGE (same sentence continuation)
  → Human B2: UNKNOWN (31.3s, 7 expansions — can't resolve)
  → Human A: KEEP_SEPARATE (8.1s, snap)
  → New information? YES — reviewer disagreement + UNKNOWN = genuine boundary
  → Evidence-grounded? PARTIAL — period + capital are detectable but insufficient
  → Repeated elsewhere? YES — AMB-005, AMB-418, AMB-519 are also adjudicated
  → Reusable signal? POTENTIAL — "when should system abstain" boundary

Final: Type_E. Genuine boundary. Learning value is in BOUNDARY DEFINITION, not correction.
```

### AMB-462 (Type D_LOW — Machine Uncertain / Low Reuse)

```
Case: AMB-462
Machine Output: ABSTAIN (TLD detects wrong table, target table text_ratio=0.163)
GT: KEEP_SEPARATE
Human Judgment: KEEP_SEPARATE (2.3s, 0 expansions — snap, override=True in B2)

L1 Evidence Value: LOW (TLD detects wrong table — Mechanism 2 failure)
L2 Human Review Value: LOW (human resolves trivially, even overrides cue)
L3 Feedback Value: LOW (override doesn't contain reusable signal)
L4 Learning Value: LOW (DCE-06 identified Mechanism 2, DCE-07 can't fix)

Final: Type_D_LOW. Human overrides machine cue, but correction is case-specific.
```

### AMB-008 (Negative Control — Not in IS-11 but analyzed in DCE-07)

```
Case: AMB-008 (resnet page 3 — PROSE with citations)
Machine Output: 0 tables (correctly rejected — align=0.410)
Not in IS-11 GT, but analyzed as negative control in DCE-07.

L1 Evidence Value: HIGH (P1/P2 exist, TLD correctly rejects)
L2 Human Review Value: LOW (not a boundary case — clear prose)
L3 Feedback Value: N/A (not in human review set)
L4 Learning Value: LOW (no boundary, no learning opportunity)

Note: This case type (prose with citations) is UNDERREPRESENTED in IS-11 (only 3 PROSE cases).
P7 has 27 BODY_TEXT_CONTINUATION cases — more diverse.
```

---

## 7. TLD × Learning Value Relationship Matrix

```
                 Human Learning Value
                 LOW       MEDIUM       HIGH
TLD Correct       24         1            1
(TN=26)          (Type_A)  (AMB-005     (AMB-032
                  snap      adj, snap    UNKNOWN,
                  judgments) but adj)    7 exp)

TLD Wrong         1          0            0
(FP=1)           (AMB-135
                  snap)

TLD Missing       15         0            3
(ABSTAIN=18)     (Type_D    -           (AMB-375,
                  LOW snap              AMB-418,
                  judgments)            AMB-519
                                        all adj)

TLD Ambiguous     0          0            0
```

### Key Findings:

1. **TLD Correct + Low Learning = 24/26 (92%)**: When TLD works, most cases are trivially easy for humans. No learning opportunity.

2. **TLD Missing + Low Learning = 15/18 (83%)**: When TLD fails, most cases are STILL trivially easy for humans. Human uses page visual, not TLD output. No learning opportunity.

3. **TLD Missing + High Learning = 3/18 (17%)**: The 3 high-learning cases (AMB-375, AMB-418, AMB-519) are ALL adjudicated. Their learning value comes from REVIEWER DISAGREEMENT, not from TLD failure.

4. **TLD Correct + High Learning = 1/26 (4%)**: AMB-032 is the only TLD-success case with high engagement. But the learning value is about EVIDENCE DISTILLATION (B2 condition fails to expose TLD info), not about TLD itself.

**CONCLUSION: TLD Failure does NOT systematically produce high Learning Value cases.**
- TLD is an independent Evidence Quality Problem (L1)
- Human Learning Value is driven by REVIEWER DISAGREEMENT and EVIDENCE DISTILLATION GAPS (L2/L3)
- TLD is NOT the primary human learning bottleneck

---

## 8. Selection Mechanism Analysis

### Current Pipeline

```
545 Candidates
  → Geometry Filter (same_y, close_x, h_gap)
  → Ambiguity Filter (IS-01/IS-02 mixed signals)
  → Sampling
  → 45 IS-11 Evaluation Cases
  → Human Review
```

### What Each Stage Optimizes

| Stage | Optimizes For | NOT Optimizing |
|---|---|---|
| Geometry Filter | Geometric proximity (same_y, close_x) | Content type diversity |
| Ambiguity Filter | Machine uncertainty (IS-01/IS-02 mixed) | Learning value |
| Sampling | Representative distribution | High-value case priority |
| Human Review | All selected cases equally | Expected improvement per judgment |

### What It Should Optimize (But Doesn't)

```
EXPECTED_SYSTEM_IMPROVEMENT_PER_HUMAN_JUDGMENT

  = P(Human feedback contains new information)
  × P(Information is evidence-grounded)
  × P(Information is reusable)
  × P(Future cases benefit)
```

Current selection maximizes the FIRST term partially (ambiguous cases → human resolves → "new information") but:
- 53% of selected cases have P(new info) ≈ 0 (Type A — machine already correct)
- 33% have P(new info) = HIGH but P(reusable) = LOW (temporary Machine LOGIC GAP)
- Only 4% have genuine boundary value

### Where Low-Value Cases Enter

```
Stage: Ambiguity Filter
  → Selects cases where IS-01/IS-02 give mixed signals
  → But 24/45 (53%) of these are actually Machine-Decisive (TN)
  → The ambiguity is in IS-01/IS-02 binary, not in the final decision
  → IS-11 experimental_c resolves most ambiguity via TLD override

Result: 53% of human review is spent confirming what machine already knows.
```

---

## 9. Content Type Bias

| Content Type | IS-11 Count | IS-11 % | P7 Count | P7 % |
|---|---|---|---|---|
| TABLE_NUMERIC | 20 | 44% | 11+4=15 | 22% |
| TABLE_TEXT | 20 | 44% | 0 | 0% |
| PROSE | 3 | 7% | 27 | 39% |
| FIGURE | 2 | 4% | 2 | 3% |
| REFERENCE | 0 | 0% | 16 | 23% |
| OTHER | 0 | 0% | 9 | 13% |

**IS-11 is 88% TABLE-focused. P7 is only 22% TABLE, with 39% PROSE and 23% REFERENCE.**

The IS-11 selection bias toward table content means:
- Human feedback is overwhelmingly about table cell boundaries
- No learning signal for prose continuation, reference list, figure caption boundaries
- P7 has more diverse boundary types but limited human review data

---

## 10. Feedback Reuse Findings (from Prior Audits)

### Learning Signal Audit Conclusions

```
Current Learning Level: L3 (Candidate Discovery)
  L0 Feedback Storage: ACHIEVED
  L1 Feedback Accumulation: ACHIEVED
  L2 Evidence-Linked Feedback: ACHIEVED
  L3 Candidate Discovery: ACHIEVED (5 candidates found)
  L4 Human-Validated Reusable Signal: NOT_ACHIEVED
  L5 Future Case Reuse: NOT_ACHIEVED
  L6 Measured Effort Reduction: NOT_ACHIEVED

91% of feedback is BOUNDARY_CONFIRMATION — Human mainly confirms Machine.
Only 9% contains new information (correction/new info).

Stability-Novelty Paradox:
  Stable signals are redundant (Machine already has evidence)
  Novel signals are unstable (Human reviewers disagree)
```

### Information Gain Audit Correction

```
60% of cases are Type B (Machine ambiguous, Human resolves) with HIGH info gain.
BUT: 10/10 Quadrant B cases could be resolved by Machine with BETTER LOGIC.
HIGH info gain is TEMPORARY — would drop to LOW if Machine adds numeric detection.

H3 STRONGLY SUPPORTED: Machine asks on wrong cases (38% Type A = waste)
H4 STRONGLY SUPPORTED: Info Gain = f(Machine Uncertainty)
```

### Feedback Reuse Audit Conclusions

```
CS1 reaches R3 (Repeated + Evidence-linked) — highest
CS2, CS3 reach R2 — repeated but weak
CS4 reaches R1 — one-off
None reaches R5 (Human-validated)

Learning Readiness:
  Feedback Capture: IMPLEMENTED
  Evidence Linkage: PARTIAL
  Signal Candidate Discovery: PARTIAL (manual, no automation)
  Human Validation: MISSING
  Reuse: MISSING
  Measured Improvement: MISSING
  Learning True: FALSE
```

---

## 11. 2D Matrix: Human Review Value × Learning Value

```
Human Review Value
    ↑
HIGH|  AMB-032 ★        AMB-375 ★
    |  (TLD correct,    (Adjudicated,
    |   B2 UNKNOWN,      B2 UNKNOWN,
    |   7 expansions)    7 expansions)
    |
MED |  AMB-418          AMB-005, AMB-519
    |  (Adjudicated,    (Adjudicated,
    |   7s, 0 exp)       snap judgments)
    |
LOW |  24 Type_A ★★★    15 Type_D_LOW ★★   1 Type_B
    |  (Machine correct, (Machine abstain,   (AMB-135
    |   snap judgments,   snap judgments)     FP, snap)
    |   0 expansions)
    +--------------------------------------→
         LOW              MEDIUM          HIGH
                 Learning Value
```

**★ = High-value cases (should be prioritized)**
**★★ = Medium-value cases (human resolves, but temporary gain)**
**★★★ = Low-value cases (wasted human review)**

### Current Selection Reality

```
45 cases selected:
  24 (53%) in LOW×LOW quadrant → WASTED
  15 (33%) in LOW×MEDIUM quadrant → TEMPORARY gain
  5 (11%) in MEDIUM/HIGH×MEDIUM/HIGH quadrant → GENUINE value
  1 (2%) in LOW×LOW (machine error) → case-specific

Human review effort: 100% spent on all 45
Effective learning value: ~11% of effort produces genuine value
```

---

## 12. Missed High-Value Cases

### Cases NOT in IS-11 but with Potential High Learning Value

1. **P7 BODY_TEXT_CONTINUATION (27 cases)**: Prose boundary cases. IS-11 has only 3 PROSE cases. P7 has 27. These could reveal learning signals for sentence/paragraph boundaries that IS-11 completely misses.

2. **P7 REFERENCE_LIST_ENTRY (16 cases)**: Reference list boundary cases. IS-11 has 0. These could reveal learning signals for citation format boundaries.

3. **P7 OTHER_AMBIGUOUS (9 cases)**: Cross-category boundary cases. IS-11 has 0. These could reveal learning signals for category-transition boundaries.

4. **P7 MERGE cases (24 cases)**: IS-11 has only 2 MERGE cases. P7 has 24. MERGE cases are harder and more likely to produce boundary learning signals.

5. **Cases with reviewer disagreement (4 in IS-11)**: AMB-005, AMB-375, AMB-418, AMB-519. These are the ONLY cases where human judgment is unstable → genuine boundary. But only 2/4 had high engagement in L5.

### Why They're Missed

```
Selection Filter: Geometry Filter → Ambiguity Filter
  → Optimizes for geometric proximity (same_y, close_x)
  → Table cells have same_y + close_x → selected
  → Prose continuation may NOT have close_x → filtered out
  → Reference entries may have different x positions → filtered out

Result: Selection bias toward TABLE content (88% of IS-11).
```

---

## 13. Counterfactual Selection Result

### Question: If selection prioritized "Potential High Learning Value" cases, would System Improvement Potential increase?

```
Counterfactual Selection:
  Instead of 45 cases (53% Type A, 33% Type D_LOW, 11% Type E):
  Select ~10-15 cases focused on:
    - All adjudicated cases (4 in IS-11)
    - All MERGE cases (2 in IS-11, 24 in P7)
    - Cross-category boundary cases (P7 OTHER_AMBIGUOUS)
    - Prose/Reference boundary cases (P7 BODY_TEXT, REFERENCE)
    - Cases where machine AND human are uncertain (UNKNOWN)

Expected outcomes:
  Human review effort: ↓ from 45 to ~10-15 (67-78% reduction)
  Feedback information gain per judgment: ↑ (each case is genuine boundary)
  Reusable signal potential: ↑ (more diverse boundary types)
  BUT:
    - Even "high gain" cases are temporary (Machine LOGIC GAP, per Info Gain Audit)
    - No candidate has reached L4 (Learning Signal Audit)
    - Ceiling effect: 96% KEEP_SEPARATE in IS-11
    - Insufficient future cases for reuse validation
    - Image confound: humans use page visual, not machine evidence

COUNTERFACTUAL_SELECTION_RESULT = INSUFFICIENT EVIDENCE

  SUPPORTED: Human review effort would decrease (fewer cases)
  SUPPORTED: Feedback information gain per judgment would increase
  NOT_SUPPORTED: True system improvement (no L4 achieved, no reuse validated)
  NOT_SUPPORTED: Human effort reduction (no HRR measurement)
  
  The counterfactual is PLAUSIBLE but UNPROVEN.
  Current data does not demonstrate that high-value selection would produce
  measurable system improvement, only that it would reduce wasted effort.
```

---

## 14. Ten Core Questions Answered

### Q1: 当前 Case Selection 实际在优化什么?

**Geometric Ambiguity (not Learning Value).**
The pipeline selects cases where text fragments are geometrically close (same_y, close_x) and IS-01/IS-02 give mixed signals. This correlates with Machine Uncertainty but NOT with Learning Value. 53% of selected cases are Machine-Decisive (Type A) where human review is wasted.

### Q2: 哪些 Case 对 Human 来说容易，但对 System 几乎没有 Learning Value?

**24 Type A cases (53%).** Machine correct (TN), human confirms in <3s, 0 evidence expansions. These are table cell pairs (e.g., "28.54" vs "10.02") where both machine and human trivially see they're different numbers in different cells.

### Q3: 哪些 Case 的 Human Feedback Information Gain 高?

**Only 2 cases had genuine high engagement: AMB-032 and AMB-375.** Both resulted in UNKNOWN (human couldn't resolve). Information Gain Audit identified 10 "Quadrant B" cases with HIGH info gain, but 10/10 are temporary (Machine LOGIC GAP — would be resolved by adding numeric detection logic).

### Q4: 哪些 Case 具有 Potential Reusable Signal?

**None have been validated.** Learning Signal Audit found 5 candidates (LSC-01 to LSC-05), 4/5 evidence-grounded but LOW info gain, 1/5 HIGH info gain but unstable. Feedback Reuse Audit found CS1 at R3 (highest), none at R5. No candidate reached L4 (Human-Validated Reusable Signal).

### Q5: 哪些 Case 是 Machine Error 但 Learning Value 低?

**AMB-135 (Type B).** Machine FP (MERGE instead of KEEP). Human corrects in 2.2s (snap). Error is case-specific (TLD page-global contamination on EfficientNet page 5). DCE-07 proved no safe fix. No reusable signal.

### Q6: 哪些 Case 是 Machine Error 且 Learning Value 高?

**NONE found.** The only Machine Error (AMB-135) has LOW learning value. TLD failures (AMB-262, AMB-313, AMB-462) are all Type D_LOW — human resolves as snap judgments. No Type C (Machine Error + High Reuse) exists in current data.

### Q7: 哪些 Case 是 Machine Uncertainty 但 Human 能提供高价值 Boundary?

**AMB-375 (adjudicated, UNKNOWN in B2, 7 expansions).** Reviewer disagreement (A: KS, B: MERGE). Human in B2 couldn't resolve (UNKNOWN). This is a genuine boundary case where "when should system abstain" learning value exists.

**AMB-032 (TLD correct, but UNKNOWN in B2, 7 expansions).** Machine correct but human in B2 couldn't resolve. Reveals evidence distillation gap — B2 doesn't expose TLD's different_cell info.

### Q8: TLD Failure 与 High Learning Value Case 到底是什么关系?

**TLD Failure does NOT systematically produce high Learning Value.**
- 83% of TLD failures (15/18 ABSTAIN) are resolved as snap judgments → LOW learning value
- The 3 high-learning TLD-failure cases (AMB-375, AMB-418, AMB-519) are ALL adjudicated → learning value comes from REVIEWER DISAGREEMENT, not TLD failure
- TLD is an independent Evidence Quality Problem (L1), NOT the human learning bottleneck

### Q9: 当前 Selection 是否漏掉了高 Learning Value Case?

**YES.**
- IS-11 is 88% TABLE content. P7 has 39% PROSE, 23% REFERENCE.
- IS-11 has 2 MERGE cases. P7 has 24 MERGE cases.
- IS-11 has 0 REFERENCE_LIST_ENTRY cases. P7 has 16.
- IS-11 has 0 OTHER_AMBIGUOUS cases. P7 has 9.
- These missing types could provide diverse boundary learning signals.

### Q10: 下一步最值得做什么，以及为什么?

**ROUTE E (MIXED) — L2 Case Selection + L3 Evidence Distillation.**
- L2: Redesign case selection to prioritize learning value over geometric ambiguity
- L3: Redesign evidence distillation to expose decision-relevant structure (AMB-032 shows B2 fails to expose TLD info)
- L1 (TLD): Important but NOT the primary human learning bottleneck — DCE-07 closed the locality route
- L4 (Feedback Reuse): Blocked downstream — ceiling effect, insufficient future cases

---

## 15. Anti-Overdesign Gate

```
NEW_OBSERVATION_NEEDED = NO
  P1/P2/TLD provide sufficient evidence. The issue is selection and distillation, not missing evidence.

NEW_MODULE_NEEDED = NO
  No new module needed. The issue is optimizing existing selection and evidence presentation.

NEW_ENGINE_NEEDED = NO
  No new processing pipeline needed.

LLM_NEEDED = NO
  The failure is in case selection and evidence distillation, not semantic understanding.

FORBIDDEN ESCALATIONS:
  ✗ Case Selection Problem → "Learning Engine" (NO)
  ✗ Evidence Distillation Problem → "Evidence Organization Engine" (NO)
  ✗ TLD Failure → "Document Understanding Engine" (NO)
  ✗ Feedback Reuse Problem → "Pattern Engine" (NO)
  ✗ Any problem → "LLM" (NO)
```

---

## 16. Learning Signal Gate

```
TRUE_REUSABLE_SIGNAL_FOUND = NO

  Current Learning Level: L3 (Candidate Discovery)
  No candidate reached L4 (Human-Validated Reusable Signal).
  CS1 at R3 (Repeated + Evidence-linked) — highest, but NOT validated.
  
  91% of feedback is BOUNDARY_CONFIRMATION (no new info).
  HIGH info gain cases are temporary (Machine LOGIC GAP).
  No future case reuse validated.
  No human effort reduction measured.
  
  This audit does NOT create new Learning Signals.
  This audit does NOT modify existing candidates.
```

---

## 17. Evidence Gaps

1. **P7 human review data incomplete**: P7 has 69 cases with diverse boundary types, but human labels are all UNKNOWN (not yet reviewed). Cannot assess learning value of P7 cases.

2. **Single participant (P01) pilot**: Only 27 judgments from 1 participant. Cannot assess cross-participant stability. Image confound: TRUE.

3. **L5 experiment limited**: 55 judgments from P722. Only 2 cases had high engagement. Cannot generalize engagement patterns.

4. **No future case validation**: No candidate has been tested on independent future cases. Cannot assess reuse potential.

5. **Ceiling effect**: 96% KEEP_SEPARATE in IS-11. No negative cases (same evidence → different feedback). Cannot learn boundaries.

6. **Content type bias**: IS-11 is 88% TABLE. Cannot assess learning value of prose/reference/figure boundary cases.

7. **No HRR measurement**: No experiment has measured Human Review Reduction. Cannot claim effort reduction.

---

## 18. Final Conclusion

```
HVA-01 STATUS = CONDITIONAL

PRIMARY BOTTLENECK = MIXED (L2 + L3)

  L2 (Case Selection): PRIMARY
    → Current selection optimizes geometric ambiguity, not learning value
    → 53% of cases are Type A (wasted human review)
    → 88% TABLE content bias, 0 REFERENCE, 0 OTHER_AMBIGUOUS
    → High-value cases (adjudicated, MERGE, diverse boundary types) are underrepresented

  L3 (Evidence Distillation): SECONDARY
    → L5 data: 96% no expansion, 96% only 1 level viewed
    → Condition A (full evidence) is FASTER than B2 (distilled) → distillation adds load
    → AMB-032: B2 UNKNOWN despite TLD having correct answer → distillation fails to expose structure

  L1 (Evidence/Perception — TLD): TERTIARY
    → TLD failure exists (DCE-06: 2 mechanisms) but is NOT the primary human learning bottleneck
    → 83% of TLD failures resolved as snap judgments
    → TLD failure ≠ high learning value
    → DCE-07 closed locality route

  L4 (Feedback Reuse): BLOCKED DOWNSTREAM
    → No candidate reached L4
    → Ceiling effect (96% KEEP_SEPARATE)
    → Insufficient future cases
    → No HRR measurement

CASE_SELECTION_CURRENT_OBJECTIVE = GEOMETRIC_AMBIGUITY (not LEARNING_VALUE)

LOW_VALUE_HUMAN_REVIEW = 24/45 (53%) Type A + 15/45 (33%) Type D_LOW = 87% low value

HIGH_VALUE_HUMAN_REVIEW = 5/45 (11%) Type E (but only 2/5 had high engagement)

HIGH_LEARNING_VALUE_CASES = AMB-032 (TLD correct, B2 UNKNOWN, evidence distillation gap), AMB-375 (adjudicated, B2 UNKNOWN, genuine boundary)

MISSED_HIGH_VALUE_CASES = P7 BODY_TEXT_CONTINUATION (27), P7 REFERENCE_LIST_ENTRY (16), P7 OTHER_AMBIGUOUS (9), P7 MERGE (24) — all underrepresented or absent in IS-11

TLD_RELATIONSHIP = INDEPENDENT — TLD failure does NOT systematically produce high learning value. TLD is an Evidence Quality Problem (L1), not the human learning bottleneck (L2/L3).

FEEDBACK_REUSE_STATUS = NOT_ACHIEVED — L3 (Candidate Discovery) only, no L4 (Human-Validated), no L5 (Reuse), no L6 (HRR)

COUNTERFACTUAL_SELECTION_RESULT = INSUFFICIENT EVIDENCE — plausible that high-value selection would reduce wasted effort, but no proof of true system improvement

NEXT_ROUTE = ROUTE E (MIXED)
  L2 contribution: Case Selection optimizes wrong metric (ambiguity ≠ learning value)
  L3 contribution: Evidence Distillation doesn't expose decision-relevant structure
  L1 contribution: TLD failure exists but is NOT primary for human learning
  L4 contribution: Blocked downstream

IMPLEMENTATION_AUTHORIZED = FALSE
EXPERIMENT_AUTHORIZED = FALSE
FROZEN_BASELINE = INTACT
PRODUCTION = FALSE

STOP = TRUE
```

---

## 19. Governance Gate

```
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

STOP                                = TRUE
```

`STOP = TRUE`。
