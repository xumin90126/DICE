# Machine-Requested Minimal Query Design & Feasibility Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY / NO IMPLEMENTATION / NO NEW MODULE / FROZEN INTACT / STOP

---

## 1. Executive Summary

```
MINIMAL_QUERY_FEASIBILITY = PARTIAL
GENUINE_PERSISTENT_MINIMAL_QUERY = NOT OBSERVED
CURRENT_LEARNING_LEVEL = L3
```

> **Machine-Requested Minimal Query 的概念在结构上成立（Machine 只在模糊时请求 Human），但在当前 45 个案例中，所有 LOW-burden + HIGH-gain 的 Query 都是 TEMPORARY（H1: Machine Logic Gap），一旦 Machine 添加简单的数值检测逻辑就会消失。唯一持续的 Human 需求（Type C, 17 cases）需要页面图像（MEDIUM burden, IMAGE_GROUNDED），不是真正的 "minimal" query。当前数据中不存在 LOW burden + HIGH gain + EVIDENCE grounded + PERSISTENT 的案例。**

核心发现：

1. **45 案例重新分类**：A (Machine-Decisive) = 17 (38%), B (Ambiguous-Resolvable) = 10 (22%), C (Evidence-Missing) = 17 (38%), D (Conflict-Unstable) = 1 (2%)。
2. **Quadrant B 全部是 H1 Temporary Machine Gap**：10/10 案例的 HIGH info gain 源于 Machine 缺少数值检测逻辑，不是真正的语义歧义。
3. **Type C 是主要持续需求**：17 个案例因 TLD 覆盖率不足而缺少 Evidence，Human 必须看图。Query 格式可行但需要 IMAGE → MEDIUM burden。
4. **Query 不增加 Information Gain**：Query 格式 vs 自由判断产生相同的信息——Query 的价值是过程一致性，不是学习价值。
5. **Learning Path 在 H2 和 H3 上断裂**：H2 无法形成 evidence-grounded signal（Machine 无证据可链接）；H3 的 Human 答案不稳定。
6. **最大可实现的 Human Effort Reduction = 60%**：需要 Machine 逻辑改进（消除 Type A+B），剩余 40% 持续需要 Human（Type C+D, IMAGE_GROUNDED）。

---

## 2. Machine-Requested Human Taxonomy

### Evidence State 分类（不使用 confidence/score）

| Evidence State | 说明 | Cases |
|---|---|---|
| EVIDENCE_SUFFICIENT | Machine Evidence 已足以支持稳定处理 | 17 (38%) |
| EVIDENCE_AMBIGUOUS | Machine 有部分 Evidence 但无法唯一确定 | 10 (22%) |
| EVIDENCE_MISSING | Machine 缺少关键 Evidence（TLD 未覆盖） | 17 (38%) |
| EVIDENCE_CONFLICT | Evidence 自身存在冲突 | 1 (2%) |

### Case Type 分类

| Type | Evidence State | Human Request | Cases |
|---|---|---|---|
| A: Machine-Decisive | EVIDENCE_SUFFICIENT | NO | 17 (38%) |
| B: Ambiguous / Human-Resolvable | EVIDENCE_AMBIGUOUS | YES (temporary) | 10 (22%) |
| C: Evidence-Missing | EVIDENCE_MISSING | YES (needs image) | 17 (38%) |
| D: Conflict / Human-Unstable | EVIDENCE_CONFLICT | UNKNOWN (unstable) | 1 (2%) |

---

## 3. 45-Case Reclassification

### Type A: Machine-Decisive (17 cases, 38%)

Machine 已有 TLD evidence (is_in_table + different_cell) 或 text pattern (period + capital) 或 FIG marker。

- 全部 GT = KEEP_SEPARATE (15) 或 MERGE (2, figure caption)
- Reviewer A/B 完全一致 (17/17)
- P722 B2 avg = 8.7s（Cue 在这些案例上增加了认知负荷）
- **Human Request = NO**

### Type B: Machine-Ambiguous / Human-Resolvable (10 cases, 22%)

Machine 有部分 Evidence（numeric values）但缺少组合逻辑。全部是 TLD 未检测到表格的页面上的数值对。

- 全部 GT = KEEP_SEPARATE
- Reviewer A/B 完全一致 (10/10)
- P722 B1 avg = 1.7s, B2 avg = 3.1s（B2 比 B1 慢——Cue 增加了负荷）
- **Human Request = YES (but temporary)**
- **Minimal Query = POSSIBLE**

### Type C: Machine-Evidence-Missing (17 cases, 38%)

Machine 无任何 Evidence（TLD 未检测到表格，无 period/FIG pattern）。Human 必须看图。

- 全部 GT = KEEP_SEPARATE
- Reviewer A/B 完全一致 (17/17)
- P722 avg = 2.0s, accuracy = 17/17 (100%)
- **Human Request = YES (needs image)**
- **Minimal Query = POSSIBLE but MEDIUM burden**

### Type D: Machine-Conflict / Human-Unstable (1 case, 2%)

TLD false positive (prose text assigned to table cell) + text pattern (period + capital) → Evidence Conflict。

- GT = KEEP_SEPARATE
- Reviewer A = KEEP_SEPARATE, B = MERGE (disagreement)
- P722 A = MERGE (wrong), B1 = KEEP_SEPARATE, B2 = KEEP_SEPARATE
- **Human Request = UNKNOWN (unstable)**

---

## 4. Quadrant B Deep Audit

### 10 个案例的 H1/H2/H3 分类

| H-Class | Count | 说明 |
|---|---|---|
| H1: Temporary Machine Gap | 10 | Machine 可通过简单逻辑解决 |
| H2: Evidence Interpretation Gap | 0 | — |
| H3: Genuine Human Semantic Judgment | 0 | — |

**全部 10 个 Quadrant B 案例都是 H1 Temporary Machine Gap。**

### 逐案分析

| Case | A | B | Machine Gap | Minimal Query | Lifetime |
|---|---|---|---|---|---|
| AMB-135 | '4' | 'MBConv6, k5x5' | type mismatch | "同一内容单元?" | TEMPORARY |
| AMB-321 | '8,144' | '8,041' | both numeric, different | "同一内容单元?" | TEMPORARY |
| AMB-323 | '2,040' | '6,149' | both numeric, different | "同一内容单元?" | TEMPORARY |
| AMB-401 | '0.70' | '0.75' | both numeric, different | "同一内容单元?" | TEMPORARY |
| AMB-407 | '1.35' | '1.40' | both numeric, different | "同一内容单元?" | TEMPORARY |
| AMB-409 | '0.65' | '0.70' | both numeric, different | "同一内容单元?" | TEMPORARY |
| AMB-467 | '37.0' | '60.0' | both numeric, different | "同一内容单元?" | TEMPORARY |
| AMB-483 | '23.5' | '38.5' | both numeric, different | "同一内容单元?" | TEMPORARY |
| AMB-505 | '61.4' | '28.3' | both numeric, different | "同一内容单元?" | TEMPORARY |
| AMB-514 | '44.2' | '63.5' | both numeric, different | "同一内容单元?" | TEMPORARY |

### Machine Fix（如果允许实现，但本审计禁止）

```
if both_numeric AND text_a != text_b:
    → likely different data points → KEEP_SEPARATE
```

这是一个**简单的数值比较逻辑**，不需要新 Observation、新模块或新 Evidence 类型。但本审计是 READ-ONLY，不实现。

### 关键结论

> **Quadrant B 的 HIGH info gain 不是来自"需要 Human 解决语义歧义"，而是来自 Machine 缺少简单的数值检测逻辑。**

如果 Machine 添加此逻辑：
- 10 个 Type B → 10 个 Type A (Machine-Decisive)
- Human Request 从 28/45 (62%) 降到 18/45 (40%)
- Quadrant B 消失

---

## 5. Temporary Machine Gap vs Genuine Human Judgment

| H-Class | Cases | Burden | Info Gain | Grounding | Lifetime | Learning Path |
|---|---|---|---|---|---|---|
| H1 Temporary | 10 | LOW | HIGH | EVIDENCE_POTENTIAL | TEMPORARY | 完整但缺 L4+L5 |
| H2 Interpretation Gap | 17 | MEDIUM | HIGH | IMAGE_GROUNDED | POTENTIALLY_REUSABLE | 断裂（无 evidence 可链接） |
| H3 Genuine Human | 1 | HIGH | LIMITED | CONFLICT_GROUNDED | PERSISTENT | 断裂（Human 不稳定） |
| N/A (Machine-Decisive) | 17 | LOW | LOW | EVIDENCE_GROUNDED | N/A | N/A |

### H1: Temporary Machine Gap (10 cases)

Machine 已有 Evidence（numeric values）但缺少组合逻辑。

- Learning Path: Machine Ambiguity → Query → Human SPLIT → Evidence+Answer → LSC → Validation → Future → Query disappears
- **Missing Links**: Human Validation (L4) + Future Case Test (L5)
- **Future**: If Machine learns numeric logic, query disappears

### H2: Evidence Interpretation Gap (17 cases)

Machine 无 Evidence（TLD 未覆盖）。Human 用图像解决。

- Learning Path: **BREAKS at "Evidence + Answer"** — Machine has no evidence to link the answer to
- Answer is IMAGE_GROUNDED, not EVIDENCE_GROUNDED
- **Cannot form evidence-grounded Learning Signal**
- **Missing Links**: Evidence Grounding + Human Validation + Future Case

### H3: Genuine Human Semantic Judgment (1 case)

Evidence Conflict (TLD false positive + text pattern)。Human 不稳定。

- Learning Path: **BREAKS at "Human Answer"** — Reviewer A/B disagree
- **Cannot form stable signal**
- **Missing Links**: Human Answer stability + everything else

---

## 6. Minimal Query Candidates

### 统一 Query 格式

所有 B/C/D 类型案例都可以使用同一个最小查询：

```
Question: "这两部分是否属于同一内容单元？"
Options:  [同一内容] [不同内容] [无法判断]
```

### Query 条件验证

| 条件 | H1 (10) | H2 (17) | H3 (1) |
|---|---|---|---|
| Q1: Human 不需理解 Machine 算法 | ✓ | ✓ | ✓ |
| Q2: Human 不需 Pattern Mining | ✓ | ✓ | ✓ |
| Q3: Human 不需长篇解释 | ✓ | ✓ (但需看图) | ✗ (判断不稳定) |
| Q4: 答案能区分 ≥2 候选解释 | ✓ | ✓ | ✗ (Human 自己不确定) |

### Query 可行性

| Type | Query Possible? | Burden | Info Gain | Grounding |
|---|---|---|---|---|
| H1 | YES | LOW | HIGH | EVIDENCE_POTENTIAL |
| H2 | YES (needs image) | MEDIUM | HIGH | IMAGE_GROUNDED |
| H3 | NO (unstable) | HIGH | LIMITED | CONFLICT |

---

## 7. Information Gain

| Type | Info Gain | 说明 |
|---|---|---|
| A (Machine-Decisive) | LOW | Machine 已知，Human 只确认 |
| B H1 (Temporary) | HIGH | Machine 模糊，Human 解决（但 temporary） |
| C H2 (Evidence Missing) | HIGH | Machine 无证据，Human 用图解决 |
| D H3 (Conflict) | LIMITED | Human 也不稳定 |

### Query vs Free Judgment

**Query 格式不增加 Information Gain。**

- Query 和自由判断产生**相同的答案**
- Query 的价值是**过程一致性**（相同问题、相同选项），不是信息量
- Query 的过程优势：一致性、降低认知开销、可扩展性
- 但这些是**过程优势**，不是**学习优势**

---

## 8. Human Burden

| Type | Burden | 原因 |
|---|---|---|
| A | LOW | Machine 已知，Human 只确认 |
| B H1 | LOW | Human 只需看文本（数值对），不需看图 |
| C H2 | MEDIUM | Human 必须看页面图像（无 Machine Evidence） |
| D H3 | HIGH | Evidence 冲突，Human 需深入理解上下文 |

### Burden 组成分析

| 因素 | H1 | H2 | H3 |
|---|---|---|---|
| 阅读范围 | 仅 text_a/b | text + page image | text + page + context |
| 上下文需求 | 无 | 需要（看表格结构） | 需要（看段落结构） |
| 跨实例比较 | 无 | 无 | 可能需要 |
| 语义抽象 | 无 | 低（识别表格列） | 高（判断段落成员） |
| 解释原因 | 无 | 无 | 需要（A/B 分歧原因） |

---

## 9. Evidence Grounding

| Type | Grounding | 可学习性 |
|---|---|---|
| A | EVIDENCE_GROUNDED | 已学习（Machine decisive） |
| B H1 | EVIDENCE_POTENTIAL | 可学习（Machine 添加逻辑后） |
| C H2 | IMAGE_GROUNDED | 不可学习（无 evidence 可链接） |
| D H3 | CONFLICT_GROUNDED | 不可学习（Human 不稳定） |

### H2 的关键问题

> Type C (H2) 的 17 个案例是 IMAGE_GROUNDED——Machine 无任何 Evidence 可链接 Human 答案。

即使 Human 答对 17/17，Machine 也无法从中学到任何 evidence-grounded signal，因为没有 evidence 可以关联。Learning Path 在 "Evidence + Answer" 步骤断裂。

---

## 10. Query Lifetime

| Lifetime | Cases | 说明 |
|---|---|---|
| TEMPORARY | 10 (H1) | Machine 逻辑改进后 query 消失 |
| POTENTIALLY_REUSABLE | 17 (H2) | 如果 TLD 扩展覆盖，部分可变为 Type A |
| PERSISTENT_HUMAN_JUDGMENT | 1 (H3) | 即使 Evidence 充分，仍需 Human 语义判断 |
| N/A | 17 (Type A) | 不需要 query |

### TEMPORARY 的含义

H1 的 10 个案例在 Machine 添加 `both_numeric + different_values → KEEP_SEPARATE` 逻辑后，全部变为 Type A。Query 不再需要。

但这不是"Learning"——这是"Logic Implementation"。Machine 不是从 Human Feedback 学习的，而是从 Logic Gap 分析中发现的。

### POTENTIALLY_REUSABLE 的含义

H2 的 17 个案例在 TLD 覆盖率扩展后，部分可能变为 Type A/B。但 TLD 是 FROZEN artifact，本审计不能修改。

### PERSISTENT 的含义

H3 的 1 个案例（AMB-005）即使有 paragraph context observation，仍可能需要 Human 判断——因为 Reviewer A/B 对"同段落 = MERGE"还是"不同句子 = SPLIT"存在根本分歧。

---

## 11. Future Learning Path

### H1 Learning Path（最完整但未完成）

```
Machine Ambiguity (numeric pairs, no TLD)
    ↓
Minimal Query: "同一内容单元?" [同一] [不同] [无法判断]
    ↓
Human Answer: SPLIT (10/10, reviewers agree)
    ↓
Evidence + Answer: both_numeric + different + SPLIT
    ↓ ✅
Repeated Cases: 10 cases, 4 docs, independent
    ↓ ✅
Learning Signal Candidate: LSC-04 (MIXED_NUMERIC_TEXT)
    ↓ ✅
Human Validation: NOT DONE ❌ (L4 not reached)
    ↓ ❌
Future Case: NOT TESTED ❌ (L5 not reached)
    ↓ ❌
Query no longer needed: THEORETICALLY YES (if Machine learns)
```

**缺失环节**: L4 (Human Validation) + L5 (Future Case Test)

### H2 Learning Path（断裂）

```
Machine Evidence Missing (TLD didn't detect table)
    ↓
Minimal Query: "同一内容单元?" (with image)
    ↓
Human Answer: SPLIT (17/17, reviewers agree)
    ↓
Evidence + Answer: no_machine_evidence + SPLIT
    ↓ ❌ BREAKS HERE — no evidence to link answer to
    → Cannot form evidence-grounded signal
    → Answer is IMAGE_GROUNDED
```

**断裂原因**: Machine 无 Evidence 可链接 Human 答案

### H3 Learning Path（断裂）

```
Machine Conflict (TLD false positive + text pattern)
    ↓
Minimal Query: "同一内容单元?"
    ↓ ❌ BREAKS HERE — Human answer unstable
    → Reviewer A = SPLIT, B = MERGE
    → Cannot form stable signal
```

**断裂原因**: Human 判断不稳定

---

## 12. H1/H2/H3 Assessment

### H1: Temporary Machine Gap
- **10 cases, ALL Quadrant B**
- Machine 可通过简单逻辑解决
- Query 是 temporary 的——会随 Machine 逻辑改进而消失
- **不是真正的 Learning 目标**——是 Logic Implementation 目标

### H2: Evidence Interpretation Gap
- **17 cases, Type C**
- Machine 无 Evidence，Human 用图像解决
- Query 可行但 MEDIUM burden（需看图）
- Learning Path 断裂——无 evidence 可链接
- **不是可学习的**——需要 TLD 覆盖扩展（FROZEN）

### H3: Genuine Human Semantic Judgment
- **1 case, Type D**
- Evidence Conflict + Human 不稳定
- Query 不可靠
- **是持续的 Human 需求**——但只有 1 个案例，不足以推广

### 整体评估

> **当前数据中不存在 "LOW burden + HIGH gain + EVIDENCE grounded + PERSISTENT" 的案例。**

- LOW burden + HIGH gain = H1 (10 cases) → TEMPORARY
- HIGH gain + PERSISTENT = H2 (17 cases) → MEDIUM burden + IMAGE_GROUNDED
- PERSISTENT + LOW burden = 不存在
- GENUINE H3 = 1 case → HIGH burden + LIMITED gain

---

## 13. Human Effort Reduction Implication

### 当前状态

```
Human reviews: 45/45 = 100%
```

### Machine-Requested Query 场景

| Scenario | Human Burden | Reduction | 说明 |
|---|---|---|---|
| 当前（无 Query） | 100% | 0% | Human 审阅所有案例 |
| Scenario 1: 只在模糊时请求 | 62% | 38% | Type A (17) 不请求 |
| Scenario 2: + Machine 逻辑 | 40% | 60% | Type A+B (27) 不请求 |
| Scenario 3: + TLD 扩展 | <40% | >60% | 部分 Type C → Type A (FROZEN) |

### 关键发现

> **最大可实现的 Human Effort Reduction = 60%**（需要 Machine 逻辑改进）

剩余 40%（Type C + D, 18 cases）持续需要 Human，且需要页面图像。

### Query vs 全面审阅

Machine-Requested Query 比全面审阅更接近 Effort Reduction，因为：
1. 消除了 Type A 的不必要审阅（38%）
2. 如果 Machine 逻辑改进，再消除 Type B（22%）
3. 对 Type C，Query 格式简化了判断（虽然仍需看图）

但：
- 这只是**过程效率**，不是**学习效率**
- Learning Path 在 H2 和 H3 上断裂
- 只有 H1 的 Learning Path 完整（但 temporary）

---

## 14. Current Learning Level

```
CURRENT_LEARNING_LEVEL = L3
```

| Level | Status |
|---|---|
| L0 Feedback Storage | ✓ |
| L1 Feedback Accumulation | ✓ |
| L2 Evidence-linked Feedback | ✓ |
| L3 Candidate Discovery | ✓ |
| L4 Human-validated Reusable Signal | ✗ |
| L5 Future-case Reuse | ✗ |
| L6 Measured Effort Reduction | ✗ |
| L7 Stable Iterative Learning | ✗ |

**L3 未改变。** 本审计发现了 Query 的可行性边界和 H1/H2/H3 分类，但没有进行 Human Validation 或 Future Case Test。

---

## 15. Limitations

1. **n=1 P722 参与者**：Query burden 评估基于有限样本
2. **4 文档**：TLD 覆盖率 41%，限制了 Type C 的分析
3. **H1 的 10 个案例全为数值对**：可能不具代表性——其他类型的 temporary gap 可能存在但未在数据中
4. **H3 只有 1 个案例**：无法判断 genuine human judgment 的普遍性
5. **Machine decisive 逻辑是简化的**：实际 Machine 可能有更复杂的判断路径
6. **Query 格式未经验证**：未在真实 Human 上测试最小查询的实际 burden
7. **TLD 是 FROZEN**：无法评估 TLD 扩展对 Type C 的影响
8. **无 future case test**：L4-L7 全部未达到

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

### Q1: 45 案例分类

| Type | Count | Evidence State |
|---|---|---|
| A: Machine-Decisive | 17 (38%) | EVIDENCE_SUFFICIENT |
| B: Ambiguous / Human-Resolvable | 10 (22%) | EVIDENCE_AMBIGUOUS |
| C: Evidence-Missing | 17 (38%) | EVIDENCE_MISSING |
| D: Conflict / Human-Unstable | 1 (2%) | EVIDENCE_CONFLICT |

### Q2: Quadrant B H1/H2/H3 分类

| H-Class | Count |
|---|---|
| H1 Temporary Machine Gap | 10 (100%) |
| H2 Evidence Interpretation Gap | 0 |
| H3 Genuine Human Semantic Judgment | 0 |

**全部 10 个 Quadrant B 案例是 H1 Temporary Machine Gap。**

### Q3: LOW burden + HIGH gain + EVIDENCE grounded 案例

**NOT OBSERVED.**

- LOW burden + HIGH gain = H1 (10 cases) → TEMPORARY (Machine Logic Gap)
- HIGH gain + EVIDENCE grounded = 不存在（H2 是 IMAGE_GROUNDED, H3 是 CONFLICT）

### Q4: 真正的 Minimal Query 是否存在？

**PARTIAL.**

- Query 格式可行：`"同一内容单元?" [同一] [不同] [无法判断]`
- 但所有 LOW-burden + HIGH-gain 的 query 都是 TEMPORARY
- 持续的 query 需要 IMAGE → MEDIUM burden → 不是真正的 "minimal"
- 真正的 persistent human judgment (H3) 只有 1 case 且不稳定

### Q5: Machine-Requested Query 是否比全面审阅更接近 Effort Reduction？

**YES, 但有上限。**

- 最大 Reduction = 60%（需要 Machine 逻辑改进）
- 剩余 40% 持续需要 Human（IMAGE_GROUNDED）
- Query 的价值是过程效率，不是学习效率
- Learning Path 只在 H1 上完整（但 temporary），H2/H3 断裂

### 核心原则验证

> **Machine should ask Human only when Evidence cannot resolve the ambiguity.**

✓ 支持：Type A (17) 不需要问，Type B/C/D (28) 需要问

> **Human should answer the smallest question that resolves that ambiguity.**

✓ 支持：`"同一内容单元?" [同一] [不同] [无法判断]` 足以解决 Type B/C 的歧义

> **The long-term goal is not to eliminate Human judgment blindly, but to make each Human answer teach the Machine something that can eventually reduce future Human requests.**

⚠ 部分支持：
- H1: Human answer CAN teach Machine (if L4+L5 reached)
- H2: Human answer CANNOT teach Machine (no evidence to link)
- H3: Human answer CANNOT teach Machine (unstable)

**当前只有 H1 (10 cases, temporary) 有完整的 learning path。H2 (17 cases) 和 H3 (1 case) 的 learning path 断裂。**

`STOP = TRUE`。
