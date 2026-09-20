# Minimal Human Feedback Information Gain / Ambiguity Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY / NO IMPLEMENTATION / NO NEW MODULE / FROZEN INTACT / STOP

---

## 1. Executive Summary

```
MINIMAL_INFORMATIVE_FEEDBACK_STATUS = QUADRANT_B_EXISTS
PREVIOUS_PARADOX_DIAGNOSIS = CORRECTED
CURRENT_LEARNING_LEVEL = L3
```

> **上一阶段审计发现的"Stability-Novelty Paradox"是一个诊断错误。当按 Evidence State（而非 Feedback Text）分析时，60% 的案例属于 Type B（Machine 模糊，Human 解决），其中 10 个案例落在 Quadrant B（LOW burden + HIGH info gain）——这是理想的 Minimal Informative Feedback 区域。但 10/10 Quadrant B 案例的 HIGH info gain 源于 Machine LOGIC GAP（缺少数值检测逻辑），而非 Evidence Gap。真正的瓶颈是 Machine 在错误的案例上请求 Human。**

核心发现：

1. **Quadrant B 存在**：10 个案例同时满足 LOW burden + HIGH information gain + reviewer agreement。
2. **116 Confirmation 重新分析**：上一阶段判定 91% 为 LOW info gain 是错误的——按 Evidence State 分析，60% 是 HIDDEN_AMBIGUITY_RESOLUTION（Machine 模糊，Human 解决）。
3. **Stability-Novelty Paradox 被纠正**：悖论不是 minimal feedback 的结构性属性，而是诊断错误——上阶段分析了 Feedback Text 而非 Evidence State。
4. **H3 强支持**：Machine 应该只在模糊案例上请求 Human，而不是在所有案例上。Type A B2 时间（8.7s）> Type B B2 时间（3.1s）——Cue 在 Machine-decisive 案例上增加了认知负荷。
5. **H4 强支持**：Information Gain = f(Machine Uncertainty)。Type A = LOW gain, Type B = HIGH gain, Type C = LIMITED gain。
6. **推荐方向**：Machine-Requested Minimal Query（在模糊案例上请求最小区分性判断）。

---

## 2. Feedback Information Gain Classification

### Type A/B/C/D 分类

| Type | 描述 | Cases | Info Gain | Burden |
|---|---|---|---|---|
| A | Machine Already Knows (decisive + correct) | 17 (38%) | LOW | LOW |
| B | Machine Ambiguous, Human Resolves (agree) | 27 (60%) | HIGH | LOW/MEDIUM |
| C | Machine Ambiguous, Human Cannot Resolve (disagree) | 1 (2%) | LIMITED | HIGH |
| D | Human Resolves But High Burden | 0 (0%) | — | — |

### 关键纠正

上一阶段审计（基于 Feedback Text 分析）报告：
- 91% BOUNDARY_CONFIRMATION → LOW info gain

本阶段审计（基于 Evidence State 分析）发现：
- 38% TRUE_CONFIRMATION (Type A) → LOW info gain ✓
- 60% HIDDEN_AMBIGUITY_RESOLUTION (Type B) → **HIGH info gain** ← 被上阶段遗漏
- 2% UNRESOLVED_AMBIGUITY (Type C) → LIMITED info gain

**60% 的"确认"实际上是歧义解决**——上一阶段的分析方法（Feedback Text）无法区分这两种情况。

---

## 3. Human Burden Classification

| Burden Level | Cases | 说明 |
|---|---|---|
| LOW | 27 | Machine 有部分证据或 Human 可快速判断 |
| MEDIUM | 17 | Machine 无证据，Human 必须看图 |
| HIGH | 1 | 证据冲突，Human 审阅者分歧 |

### LOW Burden 细分

- 10 cases：Machine 有部分证据（numeric values），Human 可快速判断 → Quadrant B
- 17 cases：Machine 已decisive，Human 只确认 → Quadrant A

### MEDIUM Burden 细分

- 17 cases：Machine 无任何证据（TLD 未检测到表格，无 period/FIG）
- Human 必须查看页面图像来判断结构
- 这些是 IMAGE_GROUNDED 而非 EVIDENCE_GROUNDED

---

## 4. Information Gain × Human Burden Matrix

```
                 Information Gain
                 LOW       HIGH      LIMITED
              ┌────────┬────────┬────────┐
Burden LOW    │   17   │   10 ★ │    0   │
              ├────────┼────────┼────────┤
Burden MEDIUM │    0   │   17   │    0   │
              ├────────┼────────┼────────┤
Burden HIGH   │    0   │    0   │    1   │
              └────────┴────────┴────────┘
```

### Quadrant A (LOW burden + LOW gain): 17 cases
Machine 已decisive，Human 只确认。预期行为，不是问题。

### Quadrant B (LOW burden + HIGH gain): 10 cases ★
**理想的 Minimal Informative Feedback 区域**。Machine 模糊但 Human 可快速解决。

### Quadrant D (MEDIUM burden + HIGH gain): 17 cases
信息价值高，但 Human 需要看图。不完全符合"minimal"目标。

### Quadrant C (HIGH burden + LIMITED gain): 1 case
Evidence 冲突，Human 分歧。无法安全复用。

---

## 5. 116 Confirmation Re-analysis

### 方法纠正

上一阶段：分析 Feedback Text → 91% BOUNDARY_CONFIRMATION
本阶段：分析 Evidence State → 区分 Machine 是否已decisive

| 类别 | Cases | 说明 |
|---|---|---|
| TRUE_CONFIRMATION | 17 (38%) | Machine 已decisive，Human 确认 |
| HIDDEN_AMBIGUITY_RESOLUTION | 27 (60%) | Machine 模糊，Human 解决（被误认为"确认"） |
| UNRESOLVED_AMBIGUITY | 1 (2%) | Machine 模糊，Human 分歧 |

### 关键发现

> **60% 的"确认"实际上是歧义解决。**

上一阶段的 91% LOW info gain 结论是错误的，因为它基于 Feedback Text 而非 Evidence State。当 Human 说"KEEP_SEPARATE"时：
- 在 Type A 案例中：这是确认（LOW gain）
- 在 Type B 案例中：这是歧义解决（HIGH gain）

两种情况在 Feedback Text 层面无法区分，但在 Evidence State 层面可以。

---

## 6. High-Information Feedback Cases

### Quadrant B: 10 Cases (LOW Burden + HIGH Info Gain)

| Case | A | B | GT | Evidence | Alt Test |
|---|---|---|---|---|---|
| AMB-135 | '4' | 'MBConv6, k5x5' | SPLIT | no TLD, mixed type | MACHINE_COULD_RESOLVE_WITH_TYPE_LOGIC |
| AMB-321 | '8,144' | '8,041' | SPLIT | no TLD, both numeric | MACHINE_COULD_RESOLVE_WITH_NUMERIC_LOGIC |
| AMB-323 | '2,040' | '6,149' | SPLIT | no TLD, both numeric | MACHINE_COULD_RESOLVE_WITH_NUMERIC_LOGIC |
| AMB-401 | '0.70' | '0.75' | SPLIT | no TLD, both numeric | MACHINE_COULD_RESOLVE_WITH_NUMERIC_LOGIC |
| AMB-407 | '1.35' | '1.40' | SPLIT | no TLD, both numeric | MACHINE_COULD_RESOLVE_WITH_NUMERIC_LOGIC |
| AMB-409 | '0.65' | '0.70' | SPLIT | no TLD, both numeric | MACHINE_COULD_RESOLVE_WITH_NUMERIC_LOGIC |
| AMB-467 | '37.0' | '60.0' | SPLIT | no TLD, both numeric | MACHINE_COULD_RESOLVE_WITH_NUMERIC_LOGIC |
| AMB-483 | '23.5' | '38.5' | SPLIT | no TLD, both numeric | MACHINE_COULD_RESOLVE_WITH_NUMERIC_LOGIC |
| AMB-505 | '61.4' | '28.3' | SPLIT | no TLD, both numeric | MACHINE_COULD_RESOLVE_WITH_NUMERIC_LOGIC |
| AMB-514 | '44.2' | '63.5' | SPLIT | no TLD, both numeric | MACHINE_COULD_RESOLVE_WITH_NUMERIC_LOGIC |

### 关键特征

- 全部是 TLD 未检测到表格的页面上的数值对
- Human 可快速判断"不同数值 = 不同内容"
- Reviewer A/B 完全一致（10/10 agree）
- **但**：10/10 的 HIGH info gain 源于 Machine LOGIC GAP

---

## 7. Alternative Explanation Test

> 如果没有 Human Feedback，仅凭当前 Evidence，Machine 是否仍然能够合理得到同样结论？

### Quadrant B 结果

| 结果 | 数量 | 说明 |
|---|---|---|
| MACHINE_COULD_RESOLVE_WITH_NUMERIC_LOGIC | 9/10 | Machine 添加"两个不同数值"检测即可解决 |
| MACHINE_COULD_RESOLVE_WITH_TYPE_LOGIC | 1/10 | Machine 添加"数值 vs 文本"检测即可解决 |
| HUMAN_TRULY_NEEDED | 0/10 | 无 |

**关键发现**：10/10 Quadrant B 案例的 HIGH info gain 是**暂时的**——如果 Machine 添加简单的数值检测逻辑，这些案例会从 HIGH 降为 LOW。

### Quadrant D 结果

17 个 MEDIUM burden 案例是真正的 IMAGE_GROUNDED——TLD 未检测到表格，Machine 无任何证据，Human 必须看图。

---

## 8. Evidence Grounding

| Type | Evidence Grounding | 说明 |
|---|---|---|
| Type A (17) | EVIDENCE_GROUNDED | Machine 已有decisive evidence |
| Type B LOW (10) | EVIDENCE_POTENTIAL | Machine 有部分证据（numeric）但未使用 |
| Type B MEDIUM (17) | IMAGE_GROUNDED | Machine 无证据，Human 依赖图像 |
| Type C (1) | CONFLICT_GROUNDED | 证据冲突（TLD vs text pattern） |

### Grounding 链完整性

```
Type A: Evidence → Machine Decisive → Human Confirms
  → Grounding: COMPLETE (but LOW gain)

Type B LOW: Evidence (numeric) → Machine Ambiguous → Human Resolves
  → Grounding: PARTIAL (evidence exists but Machine logic gap)
  → If Machine logic improves → becomes Type A

Type B MEDIUM: No Evidence → Machine Ambiguous → Human Uses Image
  → Grounding: IMAGE_ONLY (not evidence-grounded)
  → Requires TLD coverage expansion to become evidence-grounded

Type C: Conflicting Evidence → Machine Ambiguous → Human Disagrees
  → Grounding: CONFLICT (cannot resolve with current evidence)
```

---

## 9. Minimal Query Test

> 如果系统主动向 Human 问一个更小的问题，是否可以获得同样的信息？

| Type | Minimal Query Possible? | 说明 |
|---|---|---|
| Type A | YES (but unnecessary) | Machine 已知，不需要问 |
| Type B LOW | **YES** | "[同一内容] [不同内容] [无法判断]" 即可 |
| Type B MEDIUM | YES (but needs image) | Human 仍需看图才能回答 |
| Type C | **NO** | Human 判断不稳定，无法可靠回答 |

### 结论

对于 Type B LOW（Quadrant B），最小查询 `[同一内容] [不同内容] [无法判断]` 足以获取高信息增量反馈。Human 不需要解释原因。

但对于 Type B MEDIUM，即使最小查询可以形式化，Human 仍需查看页面图像——这增加了认知负担。

---

## 10. Machine-Requested Feedback Analysis

### 概念

> Machine 检测到 Evidence Ambiguity 后，主动请求一个最小区分性判断。

### 当前状态

| Case Type | 当前 Human 负担 | 如果 Machine 只在模糊时请求 |
|---|---|---|
| Type A (17, 38%) | 100% (问所有) | 0% (不问) |
| Type B LOW (10, 22%) | 100% | 0% (如果 Machine 改进逻辑) / 100% (如果未改进) |
| Type B MEDIUM (17, 38%) | 100% | 100% (真正需要 Human) |
| Type C (1, 2%) | 100% | 100% (但预期 UNKNOWN) |

### 效率分析

```
当前: Human 审阅 100% 的案例
Machine-Requested (无逻辑改进): Human 审阅 62% (27 Type B + 1 Type C)
Machine-Requested (有逻辑改进): Human 审阅 40% (17 Type B MEDIUM + 1 Type C)
```

### P722 证据

| Type | B2 Avg Time | B2 Accuracy |
|---|---|---|
| Type A (Machine knows) | 8.7s | 87% |
| Type B (Human resolves) | 3.1s | 100% |

**Type A B2 比 Type B B2 更慢**——Cue 在 Machine-decisive 案例上增加了认知负荷而没有帮助。这证明：在 Machine 已知的案例上请求 Human 是浪费。

### 是否比 ACCEPT/SPLIT/MERGE 更好？

Machine-Requested Feedback 的优势：
- 减少 Human 负担（只在模糊时请求）
- 每次请求都有 HIGH info gain（因为只在模糊时请求）
- 可以用最小查询格式

但：
- 不需要新模块（可以是 research design）
- 不需要修改 UI（当前审计禁止）
- 只是研究方向建议

---

## 11. Stability–Novelty Paradox Re-analysis

### 上一阶段结论

> "Stable signals are redundant; novel signals are unstable."

### 本阶段纠正

**这个悖论是一个诊断错误。**

#### 错误根源

1. **分析了 Feedback Text 而非 Evidence State**：上一阶段将 91% 归类为 BOUNDARY_CONFIRMATION，但实际上 60% 是 HIDDEN_AMBIGUITY_RESOLUTION。
2. **LSC-02 被误分类**：LSC-02 (SENTENCE_BOUNDARY) 被当作"HIGH gain 但不稳定"的代表。但实际上 LSC-02 是 Type C（Machine 冲突），不是 Type B（Machine 模糊但 Human 解决）。
3. **未区分 Type A 和 Type B**：将 Type A 的"稳定+冗余"和 Type B 的"稳定+高增益"混在一起。

#### 正确分析

| Type | Gain | Stability | 是否矛盾？ |
|---|---|---|---|
| Type A (17) | LOW | STABLE | 否——预期行为 |
| Type B LOW (10) | HIGH | STABLE | 否——Quadrant B 存在！ |
| Type B MEDIUM (17) | HIGH | STABLE | 否——Human 一致 |
| Type C (1) | LIMITED | UNSTABLE | 否——边缘案例 |

**Type B（27 cases）同时具有 HIGH gain 和 STABLE**——这直接反驳了悖论。

### 纠正结论

> The Stability-Novelty Paradox is NOT a structural property of minimal feedback. It was a DIAGNOSIS ERROR caused by analyzing Feedback Text instead of Evidence State.

---

## 12. H1–H4 Hypothesis Assessment

### H1: Paradox is caused by data artifacts
**PARTIALLY SUPPORTED**

- GT imbalance (96% SPLIT) → ceiling effect ✓
- TLD coverage 41% → 15/27 Type B are image-dependent ✓
- BUT: 10/10 Quadrant B cases have Machine LOGIC GAP, not just data gap
- Data artifacts contribute, but Machine logic gap also plays a role

### H2: Minimal binary feedback inherently lacks information
**PARTIALLY SUPPORTED**

- LSC-02 shows binary feedback can't express semantic differences ✓
- BUT: 27/45 Type B cases show binary SPLIT IS sufficient to resolve Machine ambiguity
- Binary feedback is insufficient for CONFLICT cases (Type C), but sufficient for AMBIGUITY cases (Type B)

### H3: Problem is Machine asks on wrong cases
**STRONGLY SUPPORTED** ★

- 38% Type A: Machine knows → asking Human is WASTE
- 22% Quadrant B: Machine could know with logic → asking is UNNECESSARY
- P722 evidence: Type A B2 (8.7s) > Type B B2 (3.1s) → Cue adds load on Type A
- **This is the most important finding of this audit**

### H4: Info Gain = f(Machine Uncertainty)
**STRONGLY SUPPORTED** ★

- Type A (Machine decisive): LOW gain — universal pattern
- Type B (Machine ambiguous): HIGH gain — universal pattern
- Type C (Machine conflict): LIMITED gain — universal pattern
- No counterexamples in 45 cases
- **This is the key principle for Minimal Informative Feedback design**

---

## 13. Current Learning Level

```
CURRENT_LEARNING_LEVEL = L3
```

| Level | Status | 说明 |
|---|---|---|
| L0 Feedback Storage | ✓ | 172 instances |
| L1 Feedback Accumulation | ✓ | Multiple sources |
| L2 Evidence-linked Feedback | ✓ | Each linked to evidence state |
| L3 Candidate Discovery | ✓ | 5 candidates + Type A/B/C/D classification |
| L4 Human-validated Reusable Signal | ✗ | No future case test |
| L5 Future-case Reuse | ✗ | Not attempted |
| L6 Measured Effort Reduction | ✗ | Not measured |
| L7 Stable Iterative Learning | ✗ | No iteration |

**L3 未改变**。虽然本阶段发现了 Quadrant B 和纠正了悖论诊断，但没有进行 future case validation。

---

## 14. Recommended Next Research Route

### Q4 Answer: B (Machine-Requested Minimal Query)

**推荐方向：Machine-Requested Minimal Query**

理由：
1. **H3 强支持**：Machine 在 38% 的案例上不必要地请求 Human
2. **H4 强支持**：Info Gain = f(Machine Uncertainty) → 只在模糊时请求
3. **P722 证据**：Type A B2 (8.7s) > Type B B2 (3.1s) → 在已知案例上请求浪费
4. **Quadrant B 存在**：10 个案例证明 LOW burden + HIGH gain 可同时实现
5. **效率提升**：从 100% Human 审阅 → 40%（如果 Machine 改进逻辑）

### 具体建议（不实现，仅研究方向）

1. Machine 检测 Evidence Ambiguity（当前已有：machine_decisive 判断）
2. 只在 Machine ambiguous 时请求 Human
3. 请求格式：`[同一内容] [不同内容] [无法判断]`
4. Machine 不在 Type A 案例上请求（节省 38% Human effort）
5. 如果 Machine 添加 numeric detection logic，再节省 22%（Quadrant B）

### 不推荐

- ❌ Learning Engine / Pattern Engine / ML Training
- ❌ 新 DICE Core layer
- ❌ 修改 Frozen Baseline
- ❌ 修改 TLD
- ❌ 修改 UI（当前审计禁止）

---

## 15. Limitations

1. **n=1 P722 参与者**：跨参与者稳定性未验证
2. **4 文档**：语料多样性有限，TLD 覆盖率 41%
3. **Machine decisive 判断基于简化逻辑**：实际 Machine 可能有更复杂的判断路径
4. **Quadrant B 的 HIGH gain 是暂时的**：如果 Machine 逻辑改进，10/10 会降为 LOW gain
5. **Type B MEDIUM 案例是 IMAGE_GROUNDED**：无法在当前 Evidence 体系下解决
6. **无 future case test**：L4 未达到，无法验证复用性
7. **Machine-Requested Feedback 是概念性发现**：未实现，未验证

---

## 16. Governance Gate

```
DICE_CORE_MODIFICATION              = NO
P1_P7_MODIFICATION                  = NO
TLD_MODIFICATION                    = NO
ATOMIC_OBSERVATION_MODIFICATION     = NO
AGGREGATION_CHANGE                  = NO
COMPRESSION_CHANGE                  = NO
EVIDENCE_CUE_CHANGE                 = NO
SIGNAL_MODIFICATION                 = NO
UI_MODIFICATION                     = NO
NEW_OBJECT_IMPLEMENTATION           = NO
NEW_MODULE                          = NO
NEW_ENGINE                          = NO
RUNTIME_CHANGE                      = NO
ML_TRAINING                         = NO
LLM_TRAINING                        = NO
CAPABILITY_REGISTRATION_CHANGE      = NO
FROZEN_BASELINE                     = INTACT (drift=0/7)
FROZEN_EXPERIMENT                   = INTACT
FORMAL_EXPERIMENT                   = NOT_STARTED
STOP                                = TRUE
```

---

## 17. 最终结论

### Q1: Feedback 分布

| 象限 | Cases | 说明 |
|---|---|---|
| LOW burden + LOW gain | 17 (38%) | Type A: Machine 已知 |
| LOW burden + HIGH gain | 10 (22%) | **Quadrant B: 理想区域** |
| MEDIUM burden + HIGH gain | 17 (38%) | Type B MEDIUM: 需要图像 |
| HIGH burden + LIMITED gain | 1 (2%) | Type C: 无法解决 |

### Q2: Quadrant B 是否存在？

**YES — 10 cases observed.**

这些是 TLD 未检测到表格的页面上的数值对。Machine 模糊（NO_STRONG_EVIDENCE），但 Human 可快速判断"不同数值 = 不同内容"→ KEEP_SEPARATE。Reviewer A/B 完全一致。

但：10/10 的 HIGH gain 源于 Machine LOGIC GAP，是暂时的。

### Q3: 高信息增量为何产生？

1. **MACHINE_LOGIC_GAP (10 cases)**：Machine 缺少简单的数值检测逻辑
2. **TLD_COVERAGE_GAP (15 cases)**：TLD 未检测到表格，Machine 无证据
3. **EVIDENCE_CONFLICT (1 case)**：TLD false positive 导致冲突

### Q4: 下一步研究方向

**B. Machine-Requested Minimal Query**

> 不要让 Human 提供更多信息；要让 Human 在 Machine 最需要信息的地方提供最少的信息。

> The goal is not Minimal Feedback. The goal is Minimal Informative Feedback.

> Human should resolve Machine ambiguity, not reconstruct Machine understanding.

### 核心原则验证

> **Information Gain = f(Machine Uncertainty)**

- Type A (Machine decisive): LOW gain — 不要问 Human
- Type B (Machine ambiguous): HIGH gain — 在这里问 Human
- Type C (Machine conflict): LIMITED gain — 问但预期 UNKNOWN

`STOP = TRUE`。
