# Evidence Utility + Feedback-to-Future-Reuse 双闭环审计

**Date**: 2026-09-12
**Mode**: READ-ONLY / NO IMPLEMENTATION / NO NEW MODULE / FROZEN INTACT / STOP

---

## 1. Executive Summary

```
LOOP_A_EVIDENCE_UTILITY     = NOT_SUPPORTED (B2 slower, accuracy dropped, cue wrong on 2/8 H2)
LOOP_B_FEEDBACK_REUSE       = INSUFFICIENT (no future cases, signal has zero info gain)
SAME_BAND_SEPARATED_PAIR    = EVIDENCE REPRESENTATION, NOT LEARNING SIGNAL
CURRENT_LEARNING_LEVEL      = L2 (partial)
ITERATIVE_LEARNING          = NOT_SUPPORTED
IMPLEMENTATION_AUTHORIZED   = FALSE
STOP                        = TRUE
```

> **SAME_BAND_SEPARATED_PAIR 是一个安全的 Level-2 几何事实，但它对全部 45 个 GT 案例都为真——信息增量为零，无法区分 KEEP_SEPARATE 与 MERGE。P722 实验表明，提供 relation cue (B2) 反而使 Human 决策时间从 1.7s 增加到 5.9s，准确率从 100% 降到 93%，且在 2/8 H2 案例上 cue 方向错误。当前不存在 future/independent cases，无法测量 HRR。SAME_BAND_SEPARATED_PAIR 是 Evidence Representation，不是 Learning Signal。**

---

## 2. Research Question

> **SAME_BAND_SEPARATED_PAIR 是否真正提高 Human Evidence Utility？Human 的最小反馈是否能够产生 Evidence-grounded、可验证、可复用的 Signal？这个 Signal 是否能够在未来独立 Case 上减少 Human Review，同时保持质量与边界安全？**

---

## 3. Loop A: Evidence Utility Audit

### 3.1 实验条件

| Condition | 说明 | Cases | H2 Cases |
|---|---|---|---|
| A (no cue) | 无 cue，Human 看原始 evidence | 15 | 2 |
| B1 (cue) | 有 cue direction，无 relation | 10 | 7 |
| B2 (cue + relation) | 有 cue direction + relation evidence | 30 | 8 |

### 3.2 全案例比较

| Metric | A (no cue) | B1 (cue) | B2 (cue+rel) | Delta (B2-B1) |
|---|---|---|---|---|
| Case count | 15 | 10 | 30 | — |
| Avg decision_time | 2.2s | 1.7s | **5.9s** | **+4.2s** |
| Accuracy | 93% | **100%** | 93% | **-7%** |
| Overrides | 0 | 0 | 2 | +2 |
| Automation bias | 0 | 0 | 0 | 0 |
| Cue conflicts | N/A | 2 | 2 | 0 |

### 3.3 H2 案例比较

| Metric | A | B1 (cue) | B2 (cue+rel) | Delta (B2-B1) |
|---|---|---|---|---|
| H2 case count | 2 | 7 | 8 | — |
| Avg decision_time | 1.2s | 1.7s | **2.6s** | **+0.9s** |
| Correct | 2/2 (100%) | 7/7 (100%) | 8/8 (100%) | 0 |
| Overrides | 0 | 0 | **2** | **+2** |
| Cue conflicts | N/A | 2 | 2 | 0 |
| Cue wrong (vs GT) | N/A | N/A | **2/8** | — |

### 3.4 关键发现：B2 Cue 在 H2 案例上错误

| Case | Cue Direction | GT | Decision | Followed? | Override? | Correct? |
|---|---|---|---|---|---|---|
| AMB-462 | **MERGE** | KEEP_SEPARATE | KEEP_SEPARATE | NO | YES | YES |
| AMB-313 | **MERGE** | KEEP_SEPARATE | KEEP_SEPARATE | NO | YES | YES |

B2 的 cue 在 2/8 H2 案例上方向错误（cue=MERGE, GT=KEEP_SEPARATE）。Human 正确地 override 了错误 cue。

### 3.5 Evidence Utility 判定

```
EVIDENCE_UTILITY = NOT_SUPPORTED
```

| 指标 | 结果 | 说明 |
|---|---|---|
| Decision Time ↓ | **FAIL** | B2 (5.9s) >> B1 (1.7s)，relation 增加 4.2s |
| Evidence Reconstruction ↓ | **FAIL** | B2 expansion_count > B1 (0.47 vs 0.00) |
| Page Revisit ↓ | **FAIL** | B2 has page_revisit, B1 has 0 |
| Cognitive Burden ↓ | **FAIL** | B2 interaction_count > B1 (0.53 vs 0.00) |
| Decision Quality ≥ | **FAIL** | B2 (93%) < B1 (100%) |
| Boundary Quality ≥ | **PARTIAL** | H2 100% in both, but 2 cue conflicts |
| Automation Bias | **PASS** | 0 automation bias events, Human overrode wrong cue |

> **B2 (cue + relation) 不仅没有提高 Evidence Utility，反而增加了认知负荷、降低了准确率。Relation cue 在 2/8 H2 案例上方向错误，Human 不得不 override。**

---

## 4. Loop B: Feedback-to-Future-Reuse

### 4.1 Feedback Signal Decomposition

对 17 个 H2 案例的 Human feedback 进行分解：

| 问题 | 回答 |
|---|---|
| Q1: Machine already knows? | NO — TLD is_in_table=False for all H2 |
| Q2: Machine can derive from Evidence? | PARTIAL — SAME_BAND_SEPARATED_PAIR 可派生，但不够确定 KEEP_SEPARATE |
| Q3: Human supplied genuinely absent info? | YES — Human 识别 "Table N" 和 "different columns"（需要图像/结构检测） |
| Q4: Human wording (not signal)? | YES — rationale 中的 "Table 6", "#params column" 等是解释，不是 signal |

**可用的最小 feedback signal = KEEP_SEPARATE (binary)**

### 4.2 Signal Grounding Check

```
H2 case: same_y_band=True, h_gap>0
Level-2 Relation: SAME_BAND_SEPARATED_PAIR = TRUE
Human Feedback: KEEP_SEPARATE
```

**Grounding 问题**：

SAME_BAND_SEPARATED_PAIR 对**全部 45 个 GT 案例**都为 TRUE（17 H2 + 22 KS + 2 MERGE + 4 DISAGREE）。

如果将其作为 `→ KEEP_SEPARATE` signal：
- 43/45 correct (KEEP_SEPARATE + DISAGREE)
- **2/45 FALSE POSITIVE** (MERGE cases: AMB-414, AMB-422 — Figure captions)

```
SIGNAL_GROUNDING = NOT_SUPPORTED
```

Signal 不能安全 grounding 在 Level-2 evidence 上，因为 Level-2 relation 是 universal true（零信息增量）。

### 4.3 Information Gain Analysis

```
SAME_BAND_SEPARATED_PAIR:
  True for KEEP_SEPARATE cases: 39/39 (100%)
  True for MERGE cases: 2/2 (100%)
  True for DISAGREE cases: 4/4 (100%)
  → Information Gain = 0 (no discrimination)
```

> **SAME_BAND_SEPARATED_PAIR 是一个 universal fact——它对所有案例都为真，无法区分任何类别。它不是 Learning Signal，而是 Evidence Representation。**

### 4.4 Future Case Independence

| 维度 | 结果 |
|---|---|
| GT cases (discovery set) | 45 |
| P722 cases (test set) | 30 |
| P722 ⊂ GT? | YES |
| Future/independent cases | **0** |
| Cross-document future cases | **0** |
| Same-page leakage risk | N/A (no future cases) |

```
FUTURE_REUSE_EVIDENCE = INSUFFICIENT
```

### 4.5 HRR (Human Review Reduction)

```
B0 (without signal): Human reviews 45/45 = 100%
B1 (with signal):    Cannot calculate — no future cases

Hypothetical (if SAME_BAND_SEPARATED_PAIR → auto-KEEP_SEPARATE):
  Auto-correct: 43/45 (96%)
  Auto-WRONG: 2/45 (4%) — Figure captions
  Quality preservation: FAIL
```

```
HRR = INSUFFICIENT (no future cases to measure)
```

### 4.6 FRR (Feedback Reuse Ratio)

```
FRR = Independent Future Cases Correctly Covered / Human Feedback Instances Required
    = 0 / 17
    = 0 (no future cases)
```

---

## 5. Learning Signal Assessment

### 5.1 SAME_BAND_SEPARATED_PAIR 作为 Learning Signal 的条件检查

| 条件 | 满足？ | 说明 |
|---|---|---|
| 1. 有区分力 (true for some, false for others) | **NO** | 100% true, zero info gain |
| 2. Evidence-grounded (traceable to P2) | YES | same_y_band + h_gap |
| 3. Human-validated | N/A | Cannot validate universal fact |
| 4. Applicable to future cases | **NO** | No future cases |
| 5. Reduces future Human Review | **NO** | No HRR measurable |

### 5.2 关键区分

```
SAME_BAND_SEPARATED_PAIR = EVIDENCE REPRESENTATION
                         ≠ LEARNING SIGNAL
```

- Evidence Representation：描述已有 evidence 的结构关系（universal fact）
- Learning Signal：包含 Machine 之前不知道的信息，可减少未来 Human Review

SAME_BAND_SEPARATED_PAIR 是前者——它对所有案例都为真，不包含任何 Machine 可以"学习"的新信息。

---

## 6. Learning Level

| Level | Status | 说明 |
|---|---|---|
| L0 Storage | ✓ | Human feedback stored in GT |
| L1 Feedback Capture | ✓ | P722 captures decisions |
| L2 Candidate Discovery | **PARTIAL** | SAME_BAND_SEPARATED_PAIR discovered but zero info gain |
| L3 Evidence-grounded Candidate | ✗ | Signal cannot be safely grounded (false positive risk) |
| L4 Human-validated Reusable Signal | ✗ | No validation possible |
| L5 Future Case Reuse | ✗ | No future cases |
| L6 Measured HRR | ✗ | No HRR measurable |
| L7 Iterative Learning | ✗ | — |

```
CURRENT_LEARNING_LEVEL = L2 (partial)
```

---

## 7. Three Types of "Human Review Reduction"

| Type | 适用？ | 说明 |
|---|---|---|
| Type A: True Reuse | **NO** | No feedback → reusable knowledge → future cases → HRR |
| Type B: Evidence Compression | **PARTIAL** | B1 cue (1.7s) < A no-cue (2.2s) — some compression |
| Type C: Automation Bias | **NO** | 0 automation bias events, Human overrode wrong cue |

> **当前只观察到 Type B (Evidence Compression) 的弱信号。没有 Type A (True Reuse)。没有 Type C (Automation Bias)。**

---

## 8. Research Decision Matrix

| Dimension | Result | Evidence |
|---|---|---|
| Evidence Utility | **NOT_SUPPORTED** | B2 slower (5.9s vs 1.7s), accuracy dropped (93% vs 100%) |
| Feedback Grounding | **NOT_SUPPORTED** | Signal has zero info gain, 2/45 false positive |
| Signal Candidate | **PARTIAL** | SAME_BAND_SEPARATED_PAIR discovered but universal |
| Human Validation | **NOT_TESTED** | No validation mechanism for universal fact |
| Future Reuse | **INSUFFICIENT** | 0 future/independent cases |
| Human Review Reduction | **INSUFFICIENT** | No HRR measurable |
| Quality Preservation | **INSUFFICIENT** | 2/45 false positive if signal applied |
| Boundary Preservation | **INSUFFICIENT** | MERGE cases would be wrong |
| Automation Bias Safety | **SUPPORTED** | 0 automation bias, Human overrode wrong cue |
| Iterative Learning | **NOT_SUPPORTED** | L2 partial, missing L3-L7 |

---

## 9. Automation Bias Analysis

### 关键正面发现

```
AUTOMATION_BIAS = 0 (all conditions)
```

- B2 中 2/30 Human override 了错误的 cue → Human 没有盲目跟随 System
- 0 automation_bias_event 在所有条件中
- Human 在 AMB-462 和 AMB-313 上正确拒绝了 cue_direction=MERGE，选择了 KEEP_SEPARATE

### 但这不是 Evidence Utility 的证据

> **Automation Bias Safety 是安全指标，不是 Utility 指标。Human 没有 bias 不代表 relation cue 有用——只代表 Human 足够聪明不去盲从。**

---

## 10. B2 Cue 错误根因

### AMB-462 和 AMB-313 的特殊情况

这两个案例是 H2 中 TLD 检测到 1 个表格但 A/B 不在其中的案例（TLD_DETECTED_WRONG_TABLE_OR_PARTIAL）。

B2 的 cue 系统基于 TLD 输出：TLD 检测到表格但 A/B 不在表格内 → cue 认为 A/B 不是表格内容 → MERGE。

但实际上 A/B 确实在表格中（只是 TLD 检测的表格 bbox 不包含它们）→ GT=KEEP_SEPARATE。

> **B2 cue 错误根因：cue 依赖 TLD 输出，TLD 在这 2 个案例上检测到了错误的表格 bbox。这进一步证明了 Consumer/Integration Gap——IS-11 依赖 TLD 而非 P2。**

---

## 11. Anti-Overdesign Gate

| Gate | Required? | Evidence |
|---|---|---|
| Learning Engine | **NO** | No learning signal found |
| Feedback Engine | **NO** | Feedback captured but not reusable |
| Signal Engine | **NO** | Signal has zero info gain |
| Query Engine | **NO** | No minimal query needed |
| Pattern Engine | **NO** | No discriminating pattern |
| Relation Engine | **NO** | Relation is universal fact |
| Evidence Organization Layer | **NO** | Organization doesn't create info gain |
| New Observation | **NO** | Existing evidence sufficient (but universal) |
| LLM | **NO** | 0/45 cases need semantic interpretation |
| Modify P2/TLD/IS-11 | **NO** | Frozen, READ-ONLY |

**全部 NO。**

---

## 12. 三个核心问题回答

### Q1: SAME_BAND_SEPARATED_PAIR 是否真正提高 Human Evidence Utility？

**NO. NOT_SUPPORTED.**

P722 数据证明：
- B2 (cue + relation) avg time = 5.9s >> B1 (cue) avg time = 1.7s
- B2 accuracy = 93% < B1 accuracy = 100%
- B2 cue 在 2/8 H2 案例上方向错误
- B2 引入 2 次 override 和额外的 expansion/interaction

Relation cue 增加了认知负荷，没有提高准确率，且在某些案例上方向错误。

### Q2: Human 的最小反馈是否能够产生 Evidence-grounded、可验证、可复用的 Signal？

**NO. NOT_SUPPORTED.**

- Human feedback (KEEP_SEPARATE) 无法安全 grounding 在 SAME_BAND_SEPARATED_PAIR 上
- SAME_BAND_SEPARATED_PAIR 对 100% 案例为真 → 零信息增量 → 无区分力
- 如果用作 signal → 2/45 false positive (MERGE cases)
- Signal 不是 evidence-grounded（Level-2 太弱，Level-3 不安全）

### Q3: 这个 Signal 是否能够在未来独立 Case 上减少 Human Review，同时保持质量与边界安全？

**NO. INSUFFICIENT.**

- 0 个 future/independent cases
- HRR 无法测量
- 如果假设性应用 → 2/45 false positive → 质量不保持
- 边界不保持（MERGE cases 会被错误 SPLIT）

---

## 13. 最终研究路线

```
A = Evidence Utility Supported        → NO
B = Feedback Signal Candidate Supported → PARTIAL (candidate found but zero info gain)
C = Future Reuse Supported             → NO (no future cases)
D = Iterative Learning Supported       → NO
E = Evidence insufficient / collect more evidence → YES
F = Reject current hypothesis          → PARTIAL (SAME_BAND_SEPARATED_PAIR is safe geometry but not learning signal)
```

**最终选择：E (Evidence insufficient)**

当前数据不足以证明：
1. SAME_BAND_SEPARATED_PAIR 提高 Evidence Utility
2. Human feedback 可转化为可复用 Learning Signal
3. Future Case Reuse 可实现

需要收集更多证据（特别是 future/independent cases 和垂直连续性数据）才能继续评估。

---

## 14. 关键区分总结

```
Evidence Representation ≠ Learning Signal
Evidence Utility ≠ Learning
Feedback Capture ≠ Learning
Signal Candidate ≠ Reusable Knowledge
Reuse ≠ Generalization
Human Review Reduction ≠ Learning
```

SAME_BAND_SEPARATED_PAIR 是 **Evidence Representation**——它安全地描述了已有 P2 evidence 的几何关系，但它不包含 Machine 可以"学习"的新信息。它对所有案例都为真，没有区分力。

真正的 Learning Signal 需要满足：
1. 有区分力（true for some, false for others）
2. Evidence-grounded
3. Human-validated
4. Applicable to future cases
5. Measurably reduces Human Review

当前数据中不存在满足全部条件的 Signal。

---

## 15. Limitations

1. **P722 n=1 参与者**：Evidence Utility 评估基于单一参与者
2. **B2 仅 30 cases (8 H2)**：样本量不足以统计显著
3. **0 future cases**：完全无法评估 Future Reuse
4. **SAME_BAND_SEPARATED_PAIR universal true**：零信息增量是数据特性，不是方法问题
5. **垂直连续性不可测量**：如果 P5 (vertical continuity) 可测量，可能有区分力
6. **B2 cue 依赖 TLD**：cue 错误根因是 TLD 覆盖率不足，不是 relation 本身的问题
7. **4 文档**：泛化性无法评估
8. **无 Quality/Boundary preservation 测量**：无 future cases 无法测量

---

## 16. Governance Gate

```
DICE_CORE_MODIFICATION              = NO
P1_P7_MODIFICATION                  = NO
P2_MODIFICATION                     = NO
TLD_MODIFICATION                    = NO
IS11_MODIFICATION                   = NO
GT_MODIFICATION                     = NO
EXPERIMENT_MODIFICATION             = NO
NEW_MODULE                          = NO
NEW_ENGINE                          = NO
LLM                                 = NO
RUNTIME_CHANGE                      = NO
CAPABILITY_CHANGE                   = NO
FROZEN_BASELINE                     = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d)
IMPLEMENTATION_AUTHORIZED           = FALSE
FORMAL_LEARNING                     = FALSE
STOP                                = TRUE
```

---

## 17. 最终原则验证

> *Evidence Utility ≠ Learning*

✓ 遵守：B2 的 Evidence Utility 未被支持，且未被混淆为 Learning。

> *Feedback Capture ≠ Learning*

✓ 遵守：Human feedback 已被捕获 (P722)，但未被混淆为 Learning。

> *Signal Candidate ≠ Reusable Knowledge*

✓ 遵守：SAME_BAND_SEPARATED_PAIR 是 Candidate 但有零信息增量，未被混淆为 Reusable Knowledge。

> *Reuse ≠ Generalization*

✓ 遵守：无 Reuse（0 future cases），未被混淆为 Generalization。

> *Human Review Reduction ≠ Learning*

✓ 遵守：HRR 无法测量，未被混淆为 Learning。

`STOP = TRUE`。
