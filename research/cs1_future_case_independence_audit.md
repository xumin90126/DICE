# CS1 Future Case Independence Repair Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY / DATA INDEPENDENCE AUDIT
**Scope**: Repair Future Case Independence for CS1 Reuse Pilot

---

## A. Current Problem

### 为什么 Page Leakage = FULL 会削弱原实验

原设计有 20 个 Future Cases，全部与 31 个 Past Cases 在**相同页面**上：

```
Past CS1 Pages (14): 
  cs_001 p3,p4,p5 | efficientnet p5,p7,p9 | resnet p1,p2,p4,p5,p6,p8,p10,p11

Future Cases (20):
  ALL on these same 14 pages
```

Page Leakage = FULL 导致以下无法排除的混淆：

| 风险 | 说明 |
|---|---|
| Page-level repetition | Human 可能认出页面，回忆表格结构 |
| Same-table repetition | Future Case 可能来自 Past Case 的同一表格 |
| Local structural duplication | 同一页面的表格列对具有高度相似性 |
| Page-specific artifact | 页面布局特性可能使 TLD 检测更容易 |
| Same-layout memorization | Human 可能记住页面布局而非真正理解 Evidence |
| Same-region redundancy | 相邻 bbox 对可能共享局部上下文 |

因此，原设计无法证明 CS1 的**跨案例迁移能力**，只能证明**同页面重复识别**。

---

## B. Repaired Future Set

### 搜索范围

从 545 Candidate Pool 中搜索满足以下条件的 Future Case：

```
1. NOT in any past set (GT-45, GT-48, experiment set) — case leakage = NONE
2. NOT on any past CS1 page — page leakage = NONE
3. TLD is_in_table=True AND different_cell=True — CS1 evidence signature
4. NOT near-duplicate — no same-table, same-row, overlapping text
```

### 搜索结果

```
Total candidates on non-past pages:     190 (ALL structure families)
  - Table-family candidates:             148
  - All-family candidates:               190

TLD computed for ALL 190 candidates on 15 non-past pages:

Pages with TLD table detection:           2 (efficientnet p2, p4)
Pages without TLD table detection:       13

CS1-matched (is_in_table=True + different_cell=True):
  efficientnet p2:  3 cases (AMB-124, AMB-125, AMB-126)
  efficientnet p4:  0 cases (TLD detects table but candidates not within it)
  All other pages:  0 cases
  Novel doc (med_001): 0 cases (0 TLD table detections on any med_001 page)
```

### Near-Duplicate Check

3 个 CS1-matched cases 全部来自 efficientnet p2 的同一表格、同一行：

```
AMB-124: A='(b) width scaling'       B='(c) depth scaling'        cells [3,1]→[3,2]
AMB-125: A='(c) depth scaling'       B='(d) resolution scaling'   cells [3,2]→[3,3]
AMB-126: A='(d) resolution scaling'  B='(e) compound scaling'     cells [3,3]→[3,4]
```

文本重叠：
- AMB-124.B = AMB-125.A = "(c) depth scaling"
- AMB-125.B = AMB-126.A = "(d) resolution scaling"

分类：**NEAR_DUPLICATE**（同表、同行、相邻列、文本重叠）

去重后独立案例：**1**（如 AMB-124）

### Repaired Future Set

```
Future Case Count:           1
Future Document Count:       1 (is11_efficientnet)
Future Page Count:           1 (p2)
Cross-document count:        0
Cross-page same-doc count:   1
Same-page count:             0 (excluded)
```

---

## C. Independence

| 泄漏类型 | 状态 | 详情 |
|---|---|---|
| **Case Leakage** | ✅ NONE | AMB-124 不在任何 past set 中 |
| **Page Leakage** | ✅ NONE | efficientnet p2 不在 14 个 past CS1 页面中 |
| **Document Leakage** | ⚠️ PARTIAL | efficientnet 在 past docs 中 (Level C: same-doc, cross-page) |
| **Near-duplicate Leakage** | ✅ NONE (after dedup) | 去重后仅保留 1 个独立案例 |
| **Outcome Leakage** | ✅ NONE | 选择基于 evidence signature，未使用未来结果 |
| **GT Leakage** | ✅ NONE | Future Case 无 GT |

---

## D. Generalization Strength

### 量化

```
past_document_count:          3 (resnet, efficientnet, cs_001)
future_document_count:        1 (efficientnet)
overlap_document_count:       1 (efficientnet)
document_disjoint:            FALSE

past_page_count:             14
future_page_count:            1 (efficientnet p2)
overlap_page_count:           0
page_disjoint:                TRUE
```

### Independence Level

```
Level A (cross-doc + cross-page):  0 cases
Level B (cross-document):          0 cases
Level C (same-doc, cross-page):    1 case (after dedup)
Level D (same-page):               109 cases (EXCLUDED by rule)
```

### Generalization Strength

```
GENERALIZATION_STRENGTH = INSUFFICIENT
```

原因：
1. 仅 1 个独立 Future Case（需 ≥10）
2. 无 novel document（med_001 无 TLD 检测）
3. 仅 same-document cross-page（Level C），非 cross-document
4. 1 个案例无法统计测试 Reuse Coverage 或 Precision

---

## E. Reuse Readiness

```
REUSE_READINESS = NOT_READY
```

原因：
1. Future Case 数量不足（1 << 10）
2. 无 cross-document 泛化证据
3. 无法测量 Reuse Coverage（需要足够 Future Cases）
4. 无法测量 Reuse Precision（需要统计样本）
5. 无法区分 TRUE_REUSE vs EVIDENCE_HELPFULNESS（样本太小）

---

## F. Human Validation Readiness

```
HUMAN_VALIDATION_READY = FALSE
```

原因：Future Case Independence 不足，无法设计有效的 Reuse ON/OFF 对照实验。

即使 Human Validation（Phase 2）本身可以使用 31 个 Past Cases 进行（不依赖 Future Cases），但后续的 Reuse Test（Phase 3）需要独立 Future Cases，当前只有 1 个，无法执行。

---

## Root Cause Analysis

### 为什么 TLD 在非 past 页面上检测不到表格？

TLD (`table_line_detector.py`, frozen, SHA256 022f5c21) 的表格检测算法基于：
1. 提取文本 span 作为 VLine
2. 按行分组
3. 检测列对齐
4. 如果足够的列对齐，判定为表格

**所有非 past 页面都有足够的 VLine（≥6）**，满足 TLD 的最低前提条件。但 TLD 的列对齐检测算法只对特定页面布局有效：

| 页面类型 | TLD 检测 | VLine 数 | 说明 |
|---|---|---|---|
| Past pages (14) | ✅ 检测到表格 | 126-459 | TLD 识别列对齐 |
| efficientnet p2 | ✅ 检测到 2 个表格 | 199 | 唯一非 past 成功页面 |
| efficientnet p4 | ✅ 检测到 1 个表格 | 254 | 但候选不在表格内 |
| efficientnet p6 | ❌ 0 表格 | 459 | VLine 最多但 TLD 未检测 |
| med_001 所有页面 | ❌ 0 表格 | 43-203 | 无 novel document 可能 |
| resnet p7, p12 | ❌ 0 表格 | 179-230 | 同文档新页面但 TLD 失败 |
| cs_001 p1, p2 | ❌ 0 表格 | 126-151 | 同文档新页面但 TLD 失败 |

**根本原因**：TLD 的表格检测算法与候选构造管道（geometric filter h_gap 8-50pt + structural classification）使用不同的检测方法。构造管道基于几何间距识别候选，TLD 基于列对齐识别表格。两种方法的覆盖范围不同。

**这不是 bug** — 这是 frozen TLD 的已知限制。TLD 在冻结前只验证了特定页面布局。

### 数据流断裂图

```
545 Candidate Pool (geometric filter)
    ↓
148 table-family candidates on non-past pages
    ↓
TLD computation (frozen)
    ↓
0 CS1-matched cases (except 3 near-duplicates on efficientnet p2)
    ↓
FUTURE_CASE_INDEPENDENCE = INSUFFICIENT
```

---

## Counterfactual Check

对唯一的独立 Future Case (AMB-124)：

> 如果没有 CS1，Human 是否需要重新进行"是否属于不同表格列"的语义判断？

**回答：YES**

- AMB-124 的文本是 "(b) width scaling" / "(c) depth scaling"
- 这些是 EfficientNet 论文中的 scaling 维度名称
- Human 需要查看页面上下文才能判断它们是否在同一表格的不同列
- 如果 CS1 signal 已验证，Human 可以跳过"识别表格结构"的步骤
- 但：仅 1 个案例无法证明这一点在统计上成立

---

## Reuse Experiment Re-assessment

### 原设计 vs 修复后

| 维度 | 原设计 (20 cases) | 修复后 (1 case) |
|---|---|---|
| Future Case Count | 20 | 1 |
| Page Leakage | FULL (all same pages) | NONE |
| Document Leakage | PARTIAL (same 3 docs) | PARTIAL (same doc) |
| Independence Level | D (same-page) | C (same-doc, cross-page) |
| Generalization | MEDIUM (flawed) | INSUFFICIENT |
| HRR measurable | YES (but biased) | NO (n=1) |
| Reuse Coverage | 100% (but circular) | N/A (n=1) |
| Reuse Precision | Measurable (but biased) | N/A (n=1) |

### 结论

```
原设计: 有 20 个 Future Cases 但 Page Leakage = FULL → 结果不可信
修复后: Page Leakage = NONE 但仅 1 个 Future Case → 无法统计

两者都无法有效验证 CS1 的跨案例 Reuse 能力。
```

---

## Can Independence Be Repaired?

### 从现有 545 Pool 中修复？

```
NO — 已穷尽搜索
```

- 搜索了 ALL 190 candidates on 15 non-past pages
- TLD computed for ALL
- 仅 3 CS1-matched (all near-duplicates → 1 after dedup)
- med_001 (novel document) 有 0 TLD table detections

### 不允许的修复方式

```
❌ 修改 TLD (frozen, prohibited)
❌ 修改 Signal 定义 (prohibited)
❌ 修改 Evidence 定义 (prohibited)
❌ 使用 same-page cases (prohibited by Level D rule)
❌ 使用 near-duplicates (prohibited)
❌ 人工制造 Future Cases (prohibited)
❌ 扩大 Signal Scope (prohibited)
❌ 修改 Past Cases (prohibited)
❌ 新增文档/corpus (outside task scope)
```

### 唯一的合法路径（超出本任务范围）

```
1. 扩展 corpus — 新增含有 TLD 可检测表格的文档
   → 超出本任务范围（READ-ONLY AUDIT）
   → 需要新文档采集授权

2. 或：接受 Level D (same-page) cases，明确标记 GENERALIZATION_STRENGTH = LOW
   → 但任务规则禁止 same-page cases 作为正式 Future Case
```

---

## Final Answer

> **是否存在足够独立的 Future Cases，使我们能够第一次真正检验"过去 Human Feedback 是否能够迁移到新的 Case，并减少新的 Human Review"？**

```
NO — FUTURE_CASE_INDEPENDENCE = INSUFFICIENT
```

从 545 Candidate Pool 中穷尽搜索后：
- 仅找到 1 个独立的 Future Case（Level C: same-doc, cross-page）
- 远低于 ≥10 的最低要求
- 无 novel document（med_001 无 TLD 检测）
- 根本原因：frozen TLD 的表格检测覆盖范围有限，仅在 14 个 past 页面 + efficientnet p2 上有效

**当前 DICE 不具备足够独立的 Future Cases 来验证 CS1 的跨案例 Reuse 能力。**

---

## Governance Gate

```
DICE_CORE_MODIFICATION      = NO
NEW_MODULE                  = NO
NEW_ENGINE                  = NO
SIGNAL_MODIFICATION         = NO
TLD_MODIFICATION            = NO
EVIDENCE_CUE_MODIFICATION   = NO
RUNTIME_CHANGE              = NO
FROZEN_BASELINE             = INTACT
FROZEN_EXPERIMENT           = INTACT
FORMAL_EXPERIMENT           = NOT_STARTED
STOP                        = TRUE
```
