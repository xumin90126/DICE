# HVA Phase 2 Report — Signal Validation & Unseen Case Replay

**Date**: 2026-09-17
**Status**: COMPLETE
**Scope**: SC-05 Human Boundary Validation → ValidatedSignal → Unseen Case Replay

---

## 1. Executive Summary

```
LEARNING_LEVEL         = L4_CANDIDATE_VALIDATION
REUSE_DEMONSTRATED     = TRUE
HUMAN_EFFORT_REDUCTION = NOT_FEASIBLE
ITERATIVE_LEARNING     = INSUFFICIENT_EVIDENCE
FINAL_STATUS           = REUSE_DEMONSTRATED_BUT_INSUFFICIENT
STOP                   = TRUE
```

Phase 2 回答了核心研究问题：**一个由 Human Feedback 形成的 SignalCandidate，经过 Human Validation 后，是否能够在真正的 Unseen Case 上复用？**

### 回答

**能复用，但不可靠。**

- Signal 在 13 个 Unseen Cases 上匹配成功（跨 4 个新文档）
- 但 FP rate = 38.5%（5 个错误预测）
- Signal 无法区分"句子边界"和"引用内续行"
- Human Effort Reduction 不可行（FP 太高，Human 仍需逐个验证）

### 这是诚实的研究结果

Signal 没有失败——它成功匹配了 Unseen Cases。但 Signal 也不够可靠——38.5% FP 意味着它不能被信任为自动决策。Conflict 有结构性原因（period + capital 的语义歧义），不是随机错误。

---

## 2. SC-05 Signal Profile

```
Signal ID: SC-05
Pattern: text_a ends with period + text_b starts with capital + not numeric + has text
S3 Signature: (is_in_table=False, different_cell=False, is01_a=False, is02_b=True,
               text_a_ends_period=True, text_b_starts_capital=True)

Source Cases (3, all adjudicated):
  IS11-AMB-375: "[23]." / "Each" → KEEP_SEPARATE (A: KS, B: MERGE)
  IS11-AMB-418: "kernels illustrated" / "The" → KEEP_SEPARATE (A: KS, B: MERGE)
  IS11-AMB-519: "open-source LLMs." / "To embrace" → KEEP_SEPARATE (A: KS, B: MERGE)

Conflict: 3/3 (all adjudicated — Reviewer disagreement)
Independence: ratio=1.0, 2 documents
Majority Decision: KEEP_SEPARATE
```

---

## 3. Human Boundary Validation

### Human 看到的 Evidence

```
Positive cases (3): All KEEP_SEPARATE (adjudicated)
Conflict cases (3): All have reviewer disagreement (A: KS, B: MERGE)
Negative cases: 0 in IS-11 (ceiling effect)
Counterexamples: NOT available in IS-11
```

### Validation Result: SUPPORTED

```
Basis: IS-11 adjudicator resolved all 3 conflict cases as KEEP_SEPARATE.
       Adjudicator saw period + capital pattern and ruled KEEP_SEPARATE.

Limitation: Adjudicator did NOT see P7 counterexamples.
            Validation made WITHOUT counterexample evidence.
            Replay will test if this holds.
```

### ValidatedSignal (VS-05)

```
signal_id: VS-05
source_signal_candidate: SC-05
validated_by_human: True
validation_result: SUPPORTED
evidence_preconditions: is01_a=False, is02_b=True, period=True, capital=True
predicted_decision: KEEP_SEPARATE
positive_cases: 3, negative_cases: 0, conflict_cases: 3

Forbidden fields verified absent:
  decision, selection, routing, ranking, score, confidence,
  recommendation, execution_plan, fallback, retry, override, correction
```

---

## 4. Unseen Case Identification

### Match Criteria

```
SC-05 S3 signature has 6 fields.
P7 has 4 of 6 fields (lacks is_in_table, different_cell — GAP-3).
Match on 4 available fields: is01_a=False, is02_b=True, period=True, capital=True
```

### Unseen Cases Found: 13

```
Total P7 cases: 69
Matching 4-field signature: 13
Case_id overlap with IS-11: 0 (truly unseen)
Document overlap with IS-11: 0 (truly unseen)

GT distribution: 8 KEEP_SEPARATE, 5 MERGE (38% negative!)
Boundary classes: REFERENCE_LIST_ENTRY(6), BODY_TEXT_CONTINUATION(6), OTHER_AMBIGUOUS(1)
Documents: 4 (ind_arxiv_2402, ind_arxiv_bio2, ind_qbio_genomics, ind_qbio_rna)
All 4 documents are NEW (0 overlap with IS-11)

Coverage: positive=8, negative=5, boundary=3 types
Coverage check: PASS (≥5 unseen cases)
```

---

## 5. Replay Results

### Outcome Distribution

| Outcome | Count | Description |
|---|---|---|
| TRUE_POSITIVE | 8 | Signal KS, GT KS (correct) |
| FALSE_POSITIVE | 5 | Signal KS, GT MERGE (wrong) |
| Total | 13 | All SIGNAL_MATCH |

```
Precision: 8/13 = 61.5%
FP rate: 5/13 = 38.5%
```

### Boundary Class × Outcome

| Boundary Class | TP | FP | Total |
|---|---|---|---|
| BODY_TEXT_CONTINUATION | 4 | 2 | 6 |
| REFERENCE_LIST_ENTRY | 4 | 2 | 6 |
| OTHER_AMBIGUOUS | 0 | 1 | 1 |

### Document × Outcome

| Document | TP | FP | Total |
|---|---|---|---|
| ind_arxiv_2402 | 1 | 2 | 3 |
| ind_arxiv_bio2 | 5 | 3 | 8 |
| ind_qbio_genomics | 1 | 0 | 1 |
| ind_qbio_rna | 1 | 0 | 1 |

---

## 6. FALSE POSITIVE Analysis

### 5 FP Cases

| Case | text_a | text_b | BC | GT | Root Cause |
|---|---|---|---|---|---|
| IND-AMB-003 | "." | "Philadelphia, PA:" | REF | MERGE | Citation continuation |
| IND-AMB-002 | "." | "Springer Berlin" | REF | MERGE | Citation continuation |
| IND-AMB-052 | "Furao Shen." | "Image data aug-" | BODY | MERGE | Author→title continuation |
| IND-AMB-033 | "Le." | "Randaugment:" | OTHER | MERGE | Author→title continuation |
| IND-AMB-049 | "Levine." | "Bitrate-constrained" | BODY | MERGE | Author→title continuation |

### Pattern Analysis

```
所有 5 个 FP 共享同一结构性原因：
  period + capital 在以下两种语义中歧义：
    (a) 句子边界 → KEEP_SEPARATE (Signal 预测)
    (b) 引用/作者名内续行 → MERGE (GT 实际)

Signal 无法区分 (a) 和 (b)，因为 S3 Signature 不包含：
  - 上下文类型（是否在参考文献列表中）
  - text_a 的语义角色（是句子还是作者名/引用）
  - text_b 的语义角色（是新句子还是引用续行）

→ period + capital 是 KEEP_SEPARATE 的必要条件，但不是充分条件
```

---

## 7. Human Effort Reduction Analysis

### Baseline vs Signal-assisted

```
Baseline (P7 machine):
  All 13 cases: INSUFFICIENT_EVIDENCE
  Human effort: must review all 13 from scratch
  Machine provides: no prediction

Signal-assisted:
  All 13 cases: SIGNAL_MATCH (predicts KEEP_SEPARATE)
  FP rate: 38.5%
  Precision: 61.5%

HRR Analysis:
  If Human trusts Signal blindly: 5 errors (38.5%) → UNACCEPTABLE
  If Human verifies each match: no effort reduction (must check all 13)
  → Signal adds cognitive overhead (verify signal + make decision)

HRR Conclusion: NOT_FEASIBLE
  FP rate 38.5% > 30% threshold
  Signal DOES NOT reduce Human effort
  Signal may INCREASE cognitive overhead
```

---

## 8. Conflict Explanation

### IS-11 Source Conflict (3/3 cases)

```
All 3 cases: Reviewer A=KEEP_SEPARATE, B=MERGE
Adjudicator: KEEP_SEPARATE

Root: 'period + capital' looks like sentence boundary (A's view)
      but could also be reference/list continuation (B's view)
```

### P7 Replay Conflict (5 FP cases)

```
All 5 FP: Signal predicted KS, GT says MERGE
Root: Same pattern, different semantic context
  - REFERENCE_LIST_ENTRY: period ends citation, capital starts next word in same entry
  - BODY_TEXT_CONTINUATION: period ends author name, capital starts paper title
  - OTHER_AMBIGUOUS: period ends abbreviation, capital starts related term
```

### Conflict IS Explained

```
The signal's conflict is NOT random — it has a STRUCTURAL cause.

period + capital is ambiguous between:
  (a) sentence boundary → KEEP_SEPARATE
  (b) within-reference/author continuation → MERGE

The signal CANNOT distinguish (a) from (b) without additional context.
→ This is a BOUNDARY, not a FAILURE.
→ The signal correctly identifies a structural ambiguity.
```

---

## 9. Learning Level Assessment

```
L3 (Candidate Discovery): ACHIEVED (Phase 1)
  → Human Feedback → FeedbackRecord → S3 Signature → SignalCandidate

L4 (Candidate Validation): ACHIEVED (Phase 2)
  → Human validated SC-05 (adjudication)
  → ValidatedSignal created (VS-05)
  → Unseen Case Replay executed (13 cases, 4 documents)

L5 (Reliable Reuse): NOT ACHIEVED
  → REUSE_DEMONSTRATED = TRUE (signal matches unseen cases)
  → But FP rate 38.5% → signal NOT reliable
  → HRR NOT feasible

ITERATIVE_LEARNING: INSUFFICIENT_EVIDENCE
  → Reuse demonstrated but unreliable
  → HRR not feasible
  → Signal needs boundary refinement or rejection
```

---

## 10. Key Research Findings

### Finding 1: Signal CAN Match Unseen Cases

```
13 unseen cases matched across 4 new documents.
0 case_id overlap, 0 document overlap.
→ Signal is NOT source-specific. It generalizes structurally.
```

### Finding 2: Signal is NOT Reliable

```
38.5% FP rate.
5 out of 13 predictions wrong.
→ Signal matches too broadly — catches both KS and MERGE cases.
```

### Finding 3: Conflict has Structural Cause

```
period + capital is ambiguous between:
  (a) sentence boundary (KEEP_SEPARATE)
  (b) reference/author continuation (MERGE)

IS-11 source cases were all (a) — ceiling effect.
P7 unseen cases include (b) — revealing the boundary.
→ Adjudicator's validation was correct for IS-11 but insufficient for general use.
```

### Finding 4: HRR NOT Feasible

```
Signal does not reduce Human effort:
  - FP too high → Human must verify each case
  - Signal adds cognitive overhead
  - No automation benefit
```

### Finding 5: HVA-02 Prediction Confirmed

```
HVA-02 predicted SIG-02 (period+capital) has 33% FP on P7.
Phase 2 measured: 38.5% FP (5/13).
→ HVA-02's retrospective analysis was accurate.
→ The 33% FP was NOT a measurement artifact — it's a real boundary.
```

---

## 11. What This Proves

### PROVEN

```
✓ Human Feedback can form SignalCandidates (Phase 1)
✓ SignalCandidate can be Human-validated (Phase 2)
✓ ValidatedSignal can match Unseen Cases (Phase 2)
✓ Signal generalizes across documents (4 new documents)
✓ Conflict has structural explanation (period+capital ambiguity)
✓ FP rate is measurable and consistent (HVA-02: 33%, Phase 2: 38.5%)
✓ The mechanism works end-to-end: Feedback → Signal → Replay
```

### NOT PROVEN

```
✗ Signal reliability (FP 38.5% > 30% threshold)
✗ Human Effort Reduction (FP too high)
✗ Iterative Learning (reuse demonstrated but insufficient)
✗ L5 (Reliable Reuse)
```

### The Honest Conclusion

```
The Learning Mechanism works (L3→L4).
Signal can be discovered, validated, and replayed.
But this particular Signal (SC-05/VS-05) is insufficient for reliable reuse.

This is NOT a failure of the mechanism.
This is a BOUNDARY of the Signal.
The mechanism correctly identified this boundary.
```

---

## 12. Output Files

```
tmp/hva_phase2/
├── phase2_plan.md              (研究计划, 4.6KB)
├── implement.py                (实现脚本, 17.1KB)
├── validated_signals.json      (ValidatedSignal VS-05, 2.0KB)
└── replay_results.json         (13 ReplayResults, 16.2KB)

tmp/hva_phase2/phase2_report.md   (本报告)
tmp/hva_phase2/phase2_report.json  (报告JSON)
```

---

## 13. Stop Conditions

```
STOP CONDITIONS CHECK:
  FP rate > 30%:                 YES (38.5%) → STOP SIGNAL
  Unseen Case count < 5:         NO (13 cases)
  Candidate cannot cross doc:    NO (4 new documents)
  Signal depends on source:      NO (generalizes)
  Conflict cannot be explained:  NO (structural cause found)
  Human Validation unstable:     NO (adjudication consistent)

→ Signal STOPPED due to FP rate > 30%
→ Do NOT modify signal to improve results
→ Do NOT expand signal definition
→ Do NOT add fields to Signature
→ Record as INSUFFICIENT_EVIDENCE for reliable reuse
```

---

## 14. Next Steps (NOT Authorized)

```
If authorized in future:
  1. Test SC-04 (SIG-01: table numeric diff cell)
     → No conflict in IS-11, 7 P7 matches, all KEEP_SEPARATE
     → May have different FP characteristics
     → But independence_ratio=0.6 (same-page clustering)

  2. Boundary refinement research
     → Investigate additional context signals (not in S3)
     → But this requires new Evidence sources → Phase 3+
     → CANNOT modify S3 Signature

  3. New corpus collection
     → More unseen cases for better coverage
     → Requires Human Experiment authorization

NOT authorized:
  - Modify Signal/GT/TLD/IS-11/P1-P7
  - Run new Human Experiment
  - Enter Phase 3
  - Register Capability
```

---

## 15. Governance Gate

```
LEARNING_LEVEL         = L4_CANDIDATE_VALIDATION
REUSE_DEMONSTRATED     = TRUE
HUMAN_EFFORT_REDUCTION = NOT_FEASIBLE
ITERATIVE_LEARNING     = INSUFFICIENT_EVIDENCE
FINAL_STATUS           = REUSE_DEMONSTRATED_BUT_INSUFFICIENT

DICE_CORE_MODIFICATION = NO
P1_P7_MODIFICATION     = NO
TLD_MODIFICATION       = NO
IS11_MODIFICATION      = NO
GT_MODIFICATION        = NO
LLM                    = NO
NEW_OBSERVATION        = NO
NEW_MODULE             = NO
NEW_ENGINE             = NO
RUNTIME_CHANGE         = NO
CAPABILITY_CHANGE      = NO
SIGNAL_MODIFICATION    = NO (signal stopped, not modified)

FROZEN_BASELINE        = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d)
PRODUCTION             = FALSE
STOP                   = TRUE
```

---

## 16. 8-Sentence Final Answer

1. **SC-05（period+capital→KEEP_SEPARATE）经过 Human Boundary Validation 获得 SUPPORTED**——3 个 IS-11 source cases 全部由 adjudicator 判定为 KEEP_SEPARATE，但 adjudicator 在判定时未看到 P7 counterexamples。

2. **13 个 Unseen Cases 从 P7 中找到**——4 个全新文档，0 case_id 重叠，0 document 重叠，GT 分布为 8 KEEP_SEPARATE + 5 MERGE（38% negative）。

3. **Replay 结果：8 TRUE_POSITIVE + 5 FALSE_POSITIVE**——Signal 成功匹配 13 个 Unseen Cases，但 FP rate = 38.5%，precision = 61.5%。

4. **5 个 FP 的根因是结构性歧义**——period+capital 在"句子边界"（KEEP_SEPARATE）和"引用/作者名内续行"（MERGE）之间歧义，Signal 无法区分这两种语义。

5. **REUSE_DEMONSTRATED = TRUE**——Signal 确实能在 Unseen Cases 上复用，跨 4 个新文档，不是 source-specific。

6. **HUMAN_EFFORT_REDUCTION = NOT_FEASIBLE**——FP rate 38.5% > 30%，Human 必须逐个验证，Signal 不减少工作量反而增加认知负担。

7. **ITERATIVE_LEARNING = INSUFFICIENT_EVIDENCE**——复用已证明但不可靠，Signal 被 STOP（不修改，不扩展，记录为 INSUFFICIENT_EVIDENCE）。

8. **Learning Level = L4_CANDIDATE_VALIDATION**——机制端到端工作（Feedback→Signal→Replay），但 VS-05 这个特定 Signal 不够可靠，L5（Reliable Reuse）未达到。

`STOP = TRUE`。不自行进入下一阶段。
