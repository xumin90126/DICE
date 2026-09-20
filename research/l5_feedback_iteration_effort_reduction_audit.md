# DICE Human Feedback → System Iteration → Human Effort Reduction

## Experiment Design & Evidence Audit — READ-ONLY / DESIGN-ONLY

**Date**: 2026-09-12
**Scope**: Audit whether Human Feedback can produce measurable future Human Effort Reduction without sacrificing quality or boundary safety
**Governance**: READ_ONLY=TRUE, DESIGN_ONLY=TRUE, FROZEN_BASELINE=INTACT, IMPLEMENTATION_AUTHORIZED=FALSE

---

## 1. Executive Conclusion

### 核心问题回答

> **DICE 是否已经存在"Human Feedback → System Iteration → Future Human Effort Reduction"的可验证闭环？**

**NO — 闭环不存在。**

当前 DICE 处于 **Storage + Manual Candidate Discovery** 阶段。Feedback 被保存，候选信号被人工识别，但：
- 没有验证工作流
- 没有复用机制
- 没有新案例测试
- 没有效果测量

### 最重要发现：Distillation Gap ≠ Learning Gap

反事实分析揭示了一个关键区分：

**CS1（DIFFERENT_TABLE_COLUMNS）的证据已经存在于系统中**（TLD is_in_table / different_cell）。Human feedback 的价值不是"教系统新知识"，而是"验证现有证据对 Human 判断是相关的"。

```
Human Feedback 的真实价值 = Evidence Relevance Validation
                      ≠ Knowledge Generation
```

因此，通往 Human Effort Reduction 的最短路径不是 Learning Engine，而是 **Evidence Cue 实现**（L5.10 已设计完成）——将已有证据安全地蒸馏给 Human。

### ITERATIVE_LEARNING = INSUFFICIENT EVIDENCE

---

## 2. Current-State Map

### 当前 Human Loop（实际状态）

```
Document → Evidence → Evidence Distillation → Candidate → Human Minimal Feedback → ValidationRecord
                                                                          ↓
                                                                    [STOP — stored but not reused]
```

### 目标闭环

```
Document → Evidence → Evidence Distillation → Candidate → Human Feedback
                                                              ↓
                                              Evidence-grounded Reusable Signal
                                                              ↓
                                              Human Validation
                                                              ↓
                                              Validated Reusable Knowledge
                                                              ↓
                                              System Iteration
                                                              ↓
                                              Future Similar Cases
                                                              ↓
                                              Human Effort Reduction
                                                              ↓
                                              Quality / Error Containment Check
                                                              ↓
                                              New Feedback ↺
```

### 现状 vs 目标逐段对比

| 闭环段 | 当前状态 | 证据 |
|---|---|---|
| Document → Evidence | **IMPLEMENTED** | P1–P7 frozen, TLD/SCE/RSC |
| Evidence → Distillation | **PARTIAL** | 15 fields shown, ~3 used; L5.10 design-ready but not implemented |
| Distillation → Candidate | **IMPLEMENTED** | Aggregation + Compression (frozen) |
| Candidate → Human Feedback | **IMPLEMENTED** | Pilot UI, 27 judgments |
| Feedback → ValidationRecord | **IMPLEMENTED** | Auto-save, schema L5.7_v1 |
| Feedback → Reusable Signal | **MISSING** | No extraction mechanism (manual audit only) |
| Signal → Human Validation | **MISSING** | No validation workflow |
| Validation → Reusable Knowledge | **MISSING** | No validated signals exist |
| Knowledge → System Iteration | **MISSING** | No observable system change from feedback |
| Iteration → Future Cases | **MISSING** | No reuse mechanism |
| Future Cases → Effort Reduction | **MISSING** | No measurement |
| Effort Reduction → Quality Check | **MISSING** | No baseline comparison |
| Quality Check → New Feedback | **MISSING** | No closed loop |

**已实现: 5/14 段。缺失: 9/14 段。**

---

## 3. Four-State Distinction

| 状态 | DICE 当前位置 | 证据 |
|---|---|---|
| A. Feedback Storage | **YES** | 27 judgments in pilot_results_live.json |
| B. Feedback Aggregation | **YES** | Structural grouping (Aggregation), B/C phase group judgments |
| C. Reusable Signal Candidate | **YES (manual)** | CS1–CS4 identified in audit, NOT by system |
| D. Actual Iterative Learning | **NO** | No validation, no reuse, no measurement |

**当前 DICE = A + B + C（人工发现）。D 未达到。**

---

## 4. Human Effort Reduction (HER) Definition

### 概念指标

```
HER = 1 - H_after / H_before

H = f(review_count, decision_time, evidence_exposure, expansion_count, abstraction_burden, interaction_cost)
```

### HER 单独不能证明 Learning

必须同时满足：

| 条件 | 公式 | 当前可测？ |
|---|---|---|
| Effort Reduction | HER > 0 | NO (no Round 2) |
| Quality Preservation | Quality_after ≥ Quality_before | NO (no baseline) |
| Error Containment | Error_after ≤ Error_before | NO (no Round 2) |
| Boundary Safety | UNKNOWN preserved, override available, no automation bias | NO (not tested) |

### 当前 HER 值

**NOT MEASURABLE** — 没有 Round 2 数据，没有 baseline，没有迭代后的系统状态。

---

## 5. Evaluation Dimensions

| 维度 | 指标 | 当前数据 | 类型 |
|---|---|---|---|
| **Human Effort** | review_count | 27 (Round 1 only) | CONCEPTUAL for HER |
| | decision_time | avg 3.9s A-phase, 11–133s B/C | CONCEPTUAL for HER |
| | evidence_exposure | 15 fields/case | MEASURABLE |
| | expansion_count | 1 (C-phase) | MEASURABLE |
| | abstraction_burden | 12/15 fields unused | MEASURABLE |
| **Decision Quality** | correct_decision | 21/21 A-phase correct | VALIDATED (Round 1) |
| | false_positive | 0 | VALIDATED (Round 1) |
| | false_negative | 0 | VALIDATED (Round 1) |
| | UNKNOWN_reasonable | 0 UNKNOWN (not tested) | NOT TESTED |
| **Evidence Quality** | evidence_sufficiency | 21/21 cases have TLD evidence | VALIDATED |
| | evidence_relevance | 12/15 fields unused by Human | VALIDATED |
| | evidence_distillation | TLD not propagated to Human | VALIDATED (gap) |
| | provenance | frozen, traceable | VALIDATED |
| **Error Recurrence** | round1_errors | 0 (P01 perfect) | VALIDATED |
| | round2_errors | N/A | NOT TESTABLE |
| | error_recurrence_rate | N/A | NOT TESTABLE |
| **Reuse** | feedback_reuse_ratio | N/A | CONCEPTUAL |
| | reuse_coverage | N/A | CONCEPTUAL |
| **Automation Bias** | blind_accept_rate | N/A | CONCEPTUAL |
| | override_rate | N/A | CONCEPTUAL |
| | automation_bias_index | N/A | CONCEPTUAL |

---

## 6. Minimal Experiment Design: Round 1 → Round 2

### Round 1: Feedback Generation（使用已有数据）

**已有**：
- 27 judgments (P01)
- 4 voice feedbacks
- CS1 (R3), CS2 (R2), CS3 (R2), CS4 (R1)

**Round 1 补充需求**（未执行）：
- n≥3 participants on same 21 cases
- Image-free condition (evidence cues only, no page image)
- Diverse cases: +5–8 MERGE, +2–3 conflict, +3–5 System≠GT

### Round 1 → Reusable Candidate

| Candidate | Evidence Link | Validation Status | Future Applicability | Expected HER |
|---|---|---|---|---|
| CS1 DIFFERENT_TABLE_COLUMNS | TLD 15/17 | CANDIDATE (R3) | HIGH — 17/21 cases, 3 docs | MEDIUM (cue reduces interpretation time) |
| CS2 SENTENCE_BOUNDARY | Text pattern 2/2 | CANDIDATE (R2) | LOW — only 2 cases | LOW |
| CS3 FIGURE_CAPTION_CONTINUITY | Text pattern 2/2 | CANDIDATE (R2) | LOW — only 2 cases, 1 doc | LOW |
| CS4 CATEGORY_HETEROGENEITY | Boundary observation | ONE-OFF (R1) | N/A (boundary, not decision) | NONE (increases awareness, not reduces effort) |

### Round 2: Unseen Future Cases

**要求**：
- 新 Case（不与 Round 1 重复）
- 同类结构（table columns, sentence boundaries, captions）
- 跨 document / page
- 包含 positive（信号匹配且 GT 一致）+ negative（信号匹配但 GT 不同）+ boundary（信号模糊）
- 不暴露 GT
- 不告诉 Human 正确答案

### Baseline vs Iterated

| 条件 | 描述 |
|---|---|
| **B0 (Baseline)** | 原始 DICE：15 fields + page image，无 Evidence Cue，无 validated signal |
| **B1 (Iterated)** | DICE + L5.10 Evidence Cue（safe translation）+ validated signal as context |

### 比较矩阵

| 指标 | B0 (Baseline) | B1 (Iterated) | 类型 |
|---|---|---|---|
| Human Review Count | 100% | 100% (all cases still reviewed) | Type A not expected |
| Human Decision Time | baseline | expected ↓ | Type B (compression) |
| Evidence Exposure | 15 fields | 8 fields | Type B |
| Expansion Count | baseline | expected ↓ | Type B |
| Abstraction Burden | HIGH (12 unused) | LOW (0 unused) | Type B |
| Decision Quality | baseline | expected ≥ | must verify |
| UNKNOWN Preservation | baseline | must verify ≥ | must verify |
| Error Rate | baseline | must verify ≤ | must verify |
| Error Recurrence | baseline | must verify ≤ | must verify |
| Reuse Coverage | 0% | depends on signal match | Type A if genuine |

### 关键预期

**最可能观察到的是 Type B（Evidence Compression）**，不是 Type A（Genuine Reuse）。

原因：CS1 的证据已经存在于系统中。Evidence Cue 实现后，Human 不需要从 15 个字段中自己发现 "这是表格的不同列"——系统直接告诉他。这是蒸馏，不是学习。

**Type A（Genuine Reuse）只有在以下条件才可能**：
- Human 在 Round 1 发现了系统不知道的新证据模式
- 该模式被验证后应用到新案例
- 新案例中系统自动检测该模式并提示

当前 CS1–CS4 都不满足：所有证据模式都已被系统检测（TLD）或可简单计算（text pattern）。

---

## 7. Counterfactual Analysis

### 核心问题

> **如果没有这次 Human Feedback，下一轮 Human 是否仍然必须重复进行同样的判断？**

| Candidate | 回答 | 原因 |
|---|---|---|
| CS1 | **YES — 仍需重复** | 证据在系统中但未蒸馏给 Human；未来 Human 看到同样的原始数据，重新推导 |
| CS2 | **YES — 仍需重复** | text pattern 可计算但未计算；未来 Human 自己读文本判断 |
| CS3 | **YES — 仍需重复** | 同 CS2 |
| CS4 | **YES — 但性质不同** | 这是边界意识，不影响工作量但影响安全 |

### 关键发现

**所有候选信号的反事实回答都是 YES。** Feedback 未产生系统级复用。

但原因不是"系统没有学习"，而是"系统没有蒸馏已有证据"。

```
问题根源: Evidence Distillation Gap (L5.10 已设计)
      ≠ Learning Gap (不需要 Learning Engine)
```

---

## 8. System Iteration Definition

### Human Feedback 后系统可发生的可观察变化

| 变化 | 机制 | 需要新模块？ | 是 Learning？ | 当前状态 |
|---|---|---|---|---|
| Evidence Cue Presentation | L5.10 safe translation table | NO | NO (distillation) | DESIGN_READY |
| Text Pattern Computation | trivial pattern match | NO | NO (distillation) | DESIGN_IDENTIFIED |
| Field Selection (cognitive load) | remove 7 low-value fields | NO | NO (distillation) | DESIGN_IDENTIFIED |
| Signal Validation | Human reviews candidates | NO (process) | NO (validation) | MISSING |
| Signal Application to New Cases | match + present as context | NO (process) | POTENTIALLY (if F1-F10 met) | MISSING |

### 什么不是 System Iteration

- 修改规则 → FORBIDDEN (no rule engine)
- 修改分类器 → FORBIDDEN (no classifier)
- 修改模型 → FORBIDDEN (no ML)
- 修改 Runtime → FORBIDDEN (runtime authority=0)
- 静默决策 → FORBIDDEN (authority transfer)

### DESIGN GAP

**唯一真正的 Design Gap**：从 Validated Signal 到 New Case Application 的匹配机制。

但这不需要新模块——它是一个**过程**：
1. 提取 validated signal 的 evidence pattern（如 is_in_table=True AND different_cell=True）
2. 对新案例运行相同的 frozen 证据检测
3. 如果匹配，呈现 validated signal 作为 context cue
4. Human 独立判断

步骤 1–3 都是已有能力的组合，不需要新 Primitive/Contract/Architecture。

---

## 9. Review Reduction Type Classification

| Type | 名称 | 描述 | 是成功？ | 是 Learning？ | DICE 可达成？ |
|---|---|---|---|---|---|
| A | Genuine Reuse | Review↓ 因 validated knowledge 处理重复结构 | YES | YES | 需 validation + reuse + new cases |
| B | Evidence Compression | Review time↓ 因 evidence 更好蒸馏 | PARTIAL | NO | **最直接路径** (L5.10) |
| C | Automation Bias | Review↓ 因 Human 信任系统不检查 | NO (danger) | NO | 必须预防 |
| D | Case Removal | Review↓ 因困难案例被排除 | NO | NO | 不适用 |
| E | Authority Transfer | Review↓ 因系统静默决策 | NO (governance failure) | NO | 禁止 |

### DICE 当前最可能实现的

**Type B (Evidence Compression)** 是最直接、最安全、不需要新模块的路径。

通过 L5.10 Evidence Cue 实现：
- Human 看到安全翻译后的结构事实
- 减少从 15 个原始字段中筛选相关信息的时间
- 减少抽象负担（不需要自己发现 "这是表格"）

**但 Type B 不是 Learning。** 它是 Distillation。

**Type A (Genuine Reuse)** 需要：
1. Evidence Cue 实现（Type B 基础）
2. 多参与者验证信号复发
3. 信号被 Human 验证为可复用
4. 验证后的信号应用到新案例
5. 测量到 effort reduction + quality maintained

这是一个多阶段过程，当前只完成了第 0 步（候选识别）。

---

## 10. Automation Bias Check Design

### 实验条件

| 条件 | 描述 |
|---|---|
| **Condition A (Blind)** | Evidence only — 无 System suggestion |
| **Condition B (Assisted)** | Evidence + System-derived candidate cue（不是答案） |

### 安全 vs 危险

| 呈现方式 | 类型 | 安全？ |
|---|---|---|
| "A 和 B 在不同结构位置" | CUE | ✅ SAFE |
| "A 和 B 应该分开" | ANSWER | ❌ FORBIDDEN |

### 测量

```
Automation Bias Index (ABI) = blind_accept_rate / total_assisted_cases

ABI > 0.7 → DANGER (rubber-stamping)
ABI < 0.3 → SAFE (independent verification)
Target: ABI < 0.5 with System≠GT cases
```

### System≠GT 测试案例

必须包含 cue 暗示一个方向但 GT 是另一个方向的案例：
- 如果 Human 盲目跟随 cue → 在 System≠GT 案例上出错 → ABI 高
- 如果 Human 独立验证 → 在 System≠GT 案例上正确 → ABI 低

---

## 11. Error Learning / Amplification Check

### 错误传播路径

```
Human Error (Round 1)
    ↓
Wrong Feedback stored
    ↓
[IF automated extraction without validation]
    ↓
Wrong Signal extracted
    ↓
Applied to N future cases
    ↓
N Errors (Error Amplification Loop)
```

### 错误遏制要求

| 要求 | 当前状态 |
|---|---|
| 无自动信号提取 | ✅ (no extraction mechanism) |
| 无信号应用无 scope | ✅ (no application mechanism) |
| 无静默系统决策 | ✅ (authority=0 at L5) |
| 每个复用信号可溯源 | NOT TESTABLE (no reused signals) |
| Human 可随时 override / UNKNOWN | ✅ (UI supports UNKNOWN) |
| System≠GT 测试案例 | ❌ (0 in current pilot) |
| Conflict 测试案例 | ❌ (0 in current pilot) |
| Supersede 机制 | ❌ (not designed) |

### 当前风险评估

**当前风险 = LOW**，因为没有任何自动化提取或应用机制。所有候选都是人工发现。

**如果实现自动化提取，风险 = HIGH**，除非同时实现独立 Human Validation。

---

## 12. F1–F10 Maturity Conditions

| 条件 | 描述 | 当前状态 |
|---|---|---|
| F1 | Feedback captured | ✅ PASS |
| F2 | Evidence-linked | ⚠️ PARTIAL (case_id link, not evidence-field link) |
| F3 | Reusable candidate identified | ⚠️ PARTIAL (manual, CS1 at R3) |
| F4 | Human validated | ❌ FAIL (no validation workflow) |
| F5 | Applied to unseen future cases | ❌ FAIL (no reuse) |
| F6 | Human effort reduced | ❌ FAIL (no measurement) |
| F7 | Decision/evidence quality maintained | ❌ FAIL (no Round 2) |
| F8 | Error recurrence not increased | ❌ FAIL (no Round 2) |
| F9 | Boundary / UNKNOWN preserved | ❌ FAIL (not tested) |
| F10 | Provenance traceable | ⚠️ PARTIAL (feedback provenance yes, signal→validation chain no) |

### ITERATIVE_LEARNING = FALSE

F1 PASS, F2–F3 PARTIAL, F4–F9 FAIL, F10 PARTIAL → 不满足 "全部同时满足" 条件。

---

## 13. Maturity Model

| Level | Description | DICE Status |
|---|---|---|
| L0 | Human-only decision | ✅ PASSED |
| L1 | Feedback Captured | ✅ **CURRENT** |
| L2 | Evidence-linked Feedback | ⚠️ PARTIAL (design-ready via L5.10) |
| L3 | Reusable Candidate | ⚠️ PARTIAL (manual, CS1=R3) |
| L4 | Human Validated Reusable Knowledge | ❌ MISSING |
| L5 | Future-case Reuse | ❌ MISSING |
| L6 | Measured Human Effort Reduction | ❌ MISSING |
| L7 | Repeated Iterative Improvement | ❌ MISSING |

**DICE 在 L1，接近 L2/L3 但未达到 L4。**

---

## 14. Research Hypotheses

| Hypothesis | 描述 | 当前证据 | 状态 |
|---|---|---|---|
| H1 Reuse | Human feedback can generate evidence-grounded reusable candidate | CS1 at R3, TLD supports 15/17 | PARTIALLY SUPPORTED (n=1, image confound) |
| H2 Iteration | Validated reusable feedback can improve handling of unseen future similar cases | NO (no validation, no Round 2) | NOT TESTED |
| H3 Effort Reduction | After validated reuse, Human effort on future similar cases decreases | NO (no measurement) | NOT TESTED |
| H4 Quality Preservation | Effort reduction does not reduce decision quality | NO (no Round 2) | NOT TESTED |
| H5 Error Containment | Feedback reuse does not amplify Human errors | NO (no reuse, no error test) | NOT TESTED |
| H6 Boundary Preservation | UNKNOWN/negative/boundary cases remain protected | NO (0 UNKNOWN, 0 conflict, 0 System≠GT) | NOT TESTED |
| H7 Non-Automation | Observed effort reduction is not merely automation bias | NO (no assisted condition tested) | NOT TESTED |

**7 个假设中：1 个 PARTIALLY SUPPORTED，6 个 NOT TESTED。**

---

## 15. Final Gate

```
╔══════════════════════════════════════════════════════════════╗
║           ITERATIVE LEARNING DECISION GATE                   ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  FEEDBACK_CAPTURE        = PASS                              ║
║  EVIDENCE_LINKAGE        = PARTIAL                           ║
║  REUSABLE_SIGNAL         = PARTIAL                           ║
║  HUMAN_VALIDATION        = FAIL                              ║
║  FUTURE_CASE_REUSE       = FAIL                              ║
║  SYSTEM_ITERATION        = FAIL                              ║
║  HUMAN_EFFORT_REDUCTION  = FAIL                              ║
║  QUALITY_PRESERVATION    = FAIL                              ║
║  ERROR_CONTAINMENT       = FAIL                              ║
║  BOUNDARY_PRESERVATION   = FAIL                              ║
║  AUTOMATION_BIAS_CONTROL = FAIL                              ║
║                                                              ║
║  ITERATIVE_LEARNING      = INSUFFICIENT_EVIDENCE             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

### Gate 字段

```
FEEDBACK_CAPTURE = PASS
EVIDENCE_LINKAGE = PARTIAL
REUSABLE_SIGNAL = PARTIAL
HUMAN_VALIDATION = FAIL
FUTURE_CASE_REUSE = FAIL
SYSTEM_ITERATION = FAIL
HUMAN_EFFORT_REDUCTION = FAIL
QUALITY_PRESERVATION = FAIL
ERROR_CONTAINMENT = FAIL
BOUNDARY_PRESERVATION = FAIL
AUTOMATION_BIAS_CONTROL = FAIL
ITERATIVE_LEARNING = INSUFFICIENT_EVIDENCE
```

---

## 16. Current State / Target State / Gap / Evidence

### CURRENT STATE
```
L1 Feedback Captured
  - 27 judgments stored
  - 4 voice feedbacks
  - CS1 (R3), CS2 (R2), CS3 (R2), CS4 (R1)
  - No validation, no reuse, no measurement
  - Storage + Manual Candidate Discovery
```

### TARGET STATE
```
L6 Measured Human Effort Reduction
  - Validated reusable knowledge applied to new cases
  - HER > 0 measured
  - Quality maintained
  - Error recurrence not increased
  - Boundary preserved
  - No automation bias
```

### GAP
```
9/14 closed-loop segments MISSING
  - Feedback → Reusable Signal (extraction process)
  - Signal → Validation (validation workflow)
  - Validation → Knowledge (no validated signals)
  - Knowledge → Iteration (no observable system change)
  - Iteration → Future Cases (no reuse mechanism)
  - Future Cases → Effort Reduction (no measurement)
  - Effort Reduction → Quality Check (no baseline)
  - Quality Check → New Feedback (no closed loop)
  - Boundary Preservation (not tested)
```

### EXISTING EVIDENCE
```
1. CS1 DIFFERENT_TABLE_COLUMNS at R3 (strongest candidate)
2. TLD is_in_table/different_cell available 21/21 (frozen)
3. L5.10 Evidence Cue design PASS (safe translation exists)
4. Aggregation + Compression frozen and working
5. P01 100% A-phase accuracy (Human can judge correctly)
6. 4 voice feedbacks contain reusable signals (manually identified)
7. 3 documents, cross-document CS1 recurrence
```

### MISSING EVIDENCE
```
1. Cross-participant signal recurrence (n=1)
2. Image-free condition (image confound unresolved)
3. Validated reusable signals (no validation workflow)
4. Round 2 unseen cases (no new corpus)
5. Baseline comparison (no B0 vs B1)
6. System≠GT test cases (0)
7. Conflict test cases (0)
8. UNKNOWN preservation test (0 UNKNOWN)
9. Automation bias measurement (no assisted condition)
10. Error recurrence measurement (no Round 2)
11. TLD false negative resolution (AMB-313, AMB-462)
```

### MINIMUM EXPERIMENT
```
Phase 0: Implement L5.10 Evidence Cue (Type B — distillation, not learning)
  - Safe translation table
  - Remove 7 low-value fields
  - Add 4 evidence cues
  - NOT a Learning Engine, NOT a Signal Engine

Phase 1: Baseline (B0)
  - n≥5 participants
  - 50 cases (21 original + 29 new, diverse)
  - Measure: time, accuracy, UNKNOWN, expansion, effort
  - Capture: all feedback

Phase 2: Signal Extraction + Validation
  - Extract candidates from Phase 1 feedbacks
  - n≥3 independent validators
  - Validate/reject candidates with scope + boundary

Phase 3: Iterated (B1)
  - n≥5 different participants
  - Same 50 cases + 50 NEW unseen cases
  - B1: Evidence Cue + validated signal as context (NOT answer)
  - Include ≥10 System≠GT cases
  - Include ≥5 conflict cases

Phase 4: Comparison
  - B0 vs B1 on all metrics
  - ABI measurement
  - HER calculation
  - Quality/error/boundary checks

Phase 5: Decision
  - If HER > 0 AND quality ≥ AND error ≤ AND boundary preserved AND ABI < 0.5:
    → ITERATIVE_LEARNING = TRUE
  - Else:
    → ITERATIVE_LEARNING = FALSE or INSUFFICIENT
```

### EXPECTED OBSERVABLES
```
Most likely: Type B (Evidence Compression)
  - Decision time ↓ (faster evidence interpretation)
  - Evidence exposure ↓ (8 fields vs 15)
  - Abstraction burden ↓ (0 unused vs 12)
  - Review count = SAME (all cases still reviewed)
  - Quality = SAME or ↑ (better evidence, not less judgment)

Possibly: Type A (Genuine Reuse) on subset
  - For cases matching validated CS1 signal
  - Decision time ↓ MORE than non-matching cases
  - But ONLY if Human independently validates (not rubber-stamps)

Must verify: Type C (Automation Bias) NOT occurring
  - ABI < 0.5 on System≠GT cases
  - Override rate > 0 on conflict cases
  - UNKNOWN rate ≥ baseline
```

### DECISION GATE
```
ITERATIVE_LEARNING = TRUE requires:
  F1-F10 ALL PASS
  H1-H7 ALL SUPPORTED (not just partially)
  ABI < 0.5
  HER > 0
  Quality_after ≥ Quality_before
  Error_after ≤ Error_before

Current: ITERATIVE_LEARNING = INSUFFICIENT_EVIDENCE
  F1 PASS, F2-F3 PARTIAL, F4-F9 FAIL, F10 PARTIAL
  H1 PARTIAL, H2-H7 NOT TESTED
  ABI NOT MEASURED
  HER NOT MEASURABLE
```

---

## 17. Critical Reflection

### 我们是在减少 Human 工作，还是只是把 Human 的工作隐藏起来？

**当前：既没有减少，也没有隐藏。** Feedback 被保存但完全未被使用。Human 在 Round 2 仍需重复全部工作。

**如果实现 Evidence Cue（Type B）：** 减少了 evidence interpretation 时间，但 Human 仍需做全部决策。这是真正的减少（distillation），不是隐藏。

**如果实现 Signal Reuse（Type A）：** 必须确保 Human 独立验证，不是 rubber-stamp。否则就是隐藏（Type C/E）。

### 我们是在让系统真正迭代，还是只是在保存 Human 的历史判断？

**当前：只是在保存。** ValidationRecord 存储了 27 个判断，但系统行为没有任何变化。

**通往真正迭代的最短路径**：
1. 实现 L5.10 Evidence Cue → Type B（distillation，不是 learning）
2. 多参与者验证 CS1 复发 → R4
3. Human 验证 CS1 为可复用 → R5
4. 应用到新案例 + 测量 → R6
5. 如果 HER > 0 + quality maintained → Learning = TRUE

### 最重要的一句话

> **Human Feedback 的首要价值不是教系统新知识，而是验证哪些已有证据对 Human 判断是相关的。通往 Human Effort Reduction 的最短路径是 Evidence Distillation（L5.10），不是 Learning Engine。**

---

## 18. Governance

```
READ_ONLY = TRUE
DESIGN_ONLY = TRUE

CODE_MODIFICATION = 0
UI_MODIFICATION = 0
DATA_MUTATION = 0
GT_MODIFICATION = 0
TLD_MODIFICATION = 0
ATOMIC_MODIFICATION = 0
AGGREGATION_MODIFICATION = 0
COMPRESSION_MODIFICATION = 0
VALIDATION_RECORD_MODIFICATION = 0
CAPABILITY_REGISTRY_MODIFICATION = 0
RUNTIME_MODIFICATION = 0

NEW_PRIMITIVE = 0
NEW_CONTRACT = 0
NEW_ARCHITECTURE = 0
PATTERN_ENGINE = 0
FEEDBACK_ENGINE = 0
LEARNING_ENGINE = 0
SIGNAL_ENGINE = 0
ML_TRAINING = 0
LLM_FINE_TUNING = 0

FUTURE_CANDIDATES:
  - Evidence Cue Implementation (L5.10 design-ready, Type B path)
  - Signal Validation Workflow (after n>3 + cross-participant recurrence)
  - Signal Reuse Mechanism (after R5 validated signals)
  - Outcome Measurement Framework (after R6 reuse)

IMPLEMENTATION_REQUIRED = TRUE (for Phase 0–5 experiment)
IMPLEMENTATION_AUTHORIZED = FALSE

FROZEN_BASELINE = INTACT
PRODUCTION = FALSE
RUNTIME_AUTHORITY = ZERO
CAPABILITY_REGISTRATION = HUMAN_CONTROLLED
STOP = TRUE
```

### Evidence Classification

- This audit = **B-class** (engineering analysis based on real pilot + prior audits)
- CS1 reusable candidate = **B-class** (R3, derived from real feedback)
- HER feasibility = **C-class** (conceptual, not measured)
- Iterative Learning = **C-class** (INSUFFICIENT_EVIDENCE, not testable)
- Evidence Cue as HER path = **B-class** (L5.10 PASS, design-ready, Type B expected)
- Automation bias risk = **C-class** (not tested, conceptual)

### Pilot Limitations Preserved

```
n = 1
27 judgments, 4 voice feedbacks
MERGE = 2, UNKNOWN = 0, conflict = 0, System≠GT = 0
Image confound: YES
TLD false negatives: 2/21
No Round 2, no baseline, no measurement
```
