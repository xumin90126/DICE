# DICE Evaluation Case Construction — Design Review

**Date**: 2026-09-12
**Mode**: READ-ONLY, DESIGN-ONLY, RESEARCH-METHODOLOGY REVIEW
**Predecessor**: `tmp/evaluation_case_construction_audit.md`
**Scope**: Define how to construct a valid Human Effort Reduction Evaluation Case Set from the existing Candidate Pool

---

## Part I — Core Questions Answered

### Q1: 为什么 h_gap 8–50pt 不能直接作为 Human Effort Case Selection criterion?

`h_gap` 衡量的是两个 span 之间的**水平几何距离**。这个变量对**感知层**有意义——它标记了"系统可能误判为同一结构单元的几何接近对"。

但对 **Human Effort Reduction** 研究而言，关键变量不是"几何上多近"，而是"语义上多难判断"。

**因果链断裂**：

```
h_gap 小 → 几何接近 → 系统可能误判
                    ↓
              但 Human 是否也难判断？→ 不一定
```

545 候选池的实际数据证实了这一点：

| 几何接近的原因 | 候选数 | Human 难度 |
|---|---|---|
| 表格同行不同列的数字 | 252 (46%) | ❌ 几乎无难度 |
| 表格同行不同列的列头 | 93 (17%) | ❌ 几乎无难度 |
| 表格行标签 + 相邻值 | 117 (21%) | ⚠️ 中等 |
| 正文句子边界 | 30 (6%) | ✅ 有真正难度 |
| 图注片段 | 11 (2%) | ✅ 有真正难度 |
| 其他 | 42 (8%) | ⚠️ 不定 |

**63% 的几何"模糊"候选实际上是表格内的平凡对**——因为表格天然有大量同行紧密排列的单元格。`h_gap` 筛选器被表格结构淹没，无法有效捕获语义模糊。

P722 实验证实：B1 条件 100% 准确率、100% 在 3 秒内完成。这意味着大量案例无论有无 Cue，Human 都能瞬时正确判断——天花板效应。

### Q2: 545 Candidate 中哪些类型值得重点保留?

**高评估价值类型**（应重点保留）：

| 类型 | 数量 | 理由 |
|---|---|---|
| **PROSE_SENTENCE_BOUNDARY** | 30 | 句子边界是 MERGE/KEEP_SEPARATE 的真实语义边界。"degrades rapidly." / "Unexpectedly," — 是同一段落连续文本流（MERGE 论点）还是两个独立句子（KEEP 论点）？存在合理的替代解释。 |
| **FIGURE_CAPTION_PARTS** | 11 | 图注标签 + 图注正文是结构模糊的经典案例。"FIG. 9:" / "Left:" — 是同一图注的不同部分（MERGE）还是独立的图注子标签（KEEP）？ |
| **ROW_LABEL_VALUE** (部分) | ~30 of 121 | 行标签 + 相邻数值有真正的结构模糊。"18 layers" / "27.94" — 是"18层模型的误差是27.94%"（MERGE，同一行的描述+值）还是"layers列"和"error列"的不同单元格（KEEP_SEPARATE）？但大部分 ROW_LABEL_VALUE 仍然是平凡的。 |
| **OTHER_AMBIGUOUS** | 42 | 包含列表项、层名比较等，需要逐一评估。 |

**中评估价值类型**（有条件保留）：

| 类型 | 数量 | 条件 |
|---|---|---|
| ROW_LABEL_VALUE (大部分) | ~91 of 121 | 仅当存在跨行表头、合并单元格或不规则对齐时才有价值。大部分是"标签列+值列"的标准表格结构，仍然平凡。 |

### Q3: 哪些类型应该被降低权重或排除?

**低评估价值类型**（应排除或大幅降低权重）：

| 类型 | 数量 | 理由 |
|---|---|---|
| **TRIVIAL_NUMERIC_PAIR** | 252 | 两个数字在不同列——如 `'28.54' / '10.02'`（top-1 error / top-5 error）。Human 一眼可判，不构成语义判断。 |
| **TRIVIAL_HEADER_PAIR** | 93 | 两个列头——如 `'Resolution' / '#Channels'`。不同列头，显然独立。 |

**关键原则**：排除的是"平凡关系"，不是"表格类型"。一个表格案例如果有合并表头、跨行标签、不规则对齐，仍可能具有高评估价值。

### Q4: 怎样避免未来再次出现 84% trivial cases?

**根因**：几何筛选器（`h_gap 8-50pt`）被表格结构淹没。表格天然有大量同行紧密排列的单元格，所以筛选器选中的大部分是表格内平凡对。

**解决方案**：在几何筛选之后、采样之前，增加**结构分类 + 低价值过滤**步骤：

```
Step 1: 几何筛选 (保留现有 h_gap filter)
    ↓ 产出 545 candidates
Step 2: 结构分类 (新增)
    → 将每个 candidate 分类为:
       TRIVIAL_NUMERIC_PAIR / TRIVIAL_HEADER_PAIR /
       PROSE_BOUNDARY / FIGURE_CAPTION / ROW_LABEL_VALUE / OTHER
Step 3: 低价值过滤 (新增)
    → 排除 TRIVIAL_NUMERIC_PAIR 和 TRIVIAL_HEADER_PAIR
    → 保留 PROSE_BOUNDARY / FIGURE_CAPTION / 部分 ROW_LABEL_VALUE
    → 产出 ~200 evaluation-valuable candidates
Step 4: 覆盖选择 (新增)
    → 从 200 中按覆盖目标选择
```

**分类方法**（无需新模块，脚本即可实现）：
- 两个 span 都是纯数字 + 长度 < 10 → TRIVIAL_NUMERIC_PAIR
- 两个 span 都以大写字母开头 + 长度 < 20 + 无空格 → TRIVIAL_HEADER_PAIR
- text_a 以句号/逗号/括号结尾 + 长度 > 20 → PROSE_BOUNDARY
- text_a 包含 "FIG" → FIGURE_CAPTION
- 一个是数字、一个是文本 + 长度 < 30 → ROW_LABEL_VALUE

### Q5: 怎样让 B1 vs B2 有真正可测的 effect opportunity?

B1 vs B2 的可测差异需要满足：**Cue 在该案例上有可能改变 Human 的认知或操作成本**。

当前问题：84% 案例太简单，B1 已经 100% 正确、100% <3s，Cue 无空间降低已经很低的成本。

**解决方案**：选择满足以下条件的案例（Evaluation Opportunity）：

1. **非瞬时可解**：Human 不能仅凭 text_a/text_b 表面形式在 <3s 内确定答案
2. **证据可访问性差异**：B1 中证据存在但需要展开/搜索才能理解；B2 Cue 能降低证据检索/解释成本
3. **判断质量非天花板**：B1 无 Cue 时准确率不应接近 100%，否则 Cue 无改善空间
4. **Cue 相关性**：Cue 内容与判断直接相关，不是无关信息

**Pilot 验证**：在正式实验前，用 10-15 个案例跑 Pilot，观察 B1 条件下的准确率和时间分布。如果 B1 准确率 >90% 或平均时间 <3s，说明案例仍然太简单，需要调整。

### Q6: 怎样测试 5 种 Cue 效果类型?

| 类型 | 定义 | 构造方法 | 预期 B1 vs B2 差异 |
|---|---|---|---|
| **Type 1 — Cue Informative** | B1 证据存在但不易理解；B2 Cue 降低检索/解释成本 | 选择证据字段多、需要展开才能看到关键信息的案例 | B2 比 B1 更快/更少展开，准确率相当 |
| **Type 2 — Cue Redundant** | Human 本来就能轻易理解 | 选择表面形式清晰的案例（少量，作为控制） | B1 ≈ B2，B2 可能略慢（额外阅读） |
| **Type 3 — Cue Misleading/Boundary** | Cue 看似有帮助但不能单独支持正确判断 | 选择 Cue 方向与 GT 一致但证据冲突的案例 | B2 可能更快但准确率下降，或 UNKNOWN 增加 |
| **Type 4 — Evidence Missing** | Cue 无法弥补底层证据缺失 | 选择 TLD 缺失或图像不清晰的案例 | B2 UNKNOWN 率应高于 B1（Cue 引入不确定） |
| **Type 5 — System ≠ GT** | System evidence/Cue 与 Human adjudication 不一致 | 选择 Cue direction ≠ GT direction 的案例 | B2 可能被误导，准确率低于 B1 |

**关键要求**：每种类型需要足够的案例（≥5）才能产生可统计的差异。当前 45 案例中 Type 1/2 过多，Type 3/4/5 几乎缺失。

### Q7: 怎样避免 GT / Pilot / Experiment leakage?

| 泄漏类型 | 风险 | 防范措施 |
|---|---|---|
| **GT leakage** | Case Builder 看到 GT 后选择有利于系统的案例 | GT 必须在案例选择**之后**分配。选择基于结构特征，不基于 GT。 |
| **Pilot feedback leakage** | Pilot 发现某案例"Cue 有效"后保留它用于正式实验 | Pilot 案例和正式实验案例**必须分离**。Pilot 案例不进入正式评估集。 |
| **Experiment result leakage** | 正式实验后发现某案例"支持假设"后重新分析 | 分析合同（analysis contract）必须在实验前预注册并冻结。 |
| **Cue output leakage** | Case Builder 看到 Cue 输出后选择"看起来有效"的案例 | Cue 计算在案例选择之后。案例选择基于候选的结构特征，不基于 Cue 内容。 |

**数据分离设计**：

```
Discovery Set (可迭代)
    → 发现问题，观察案例质量
    → 不用于最终分析
Pilot Set (可迭代)
    → 发现 Human difficulty
    → 不进入正式评估
Frozen Evaluation Set (冻结)
    → 预注册分析合同
    → 正式实验数据
Independent Holdout (冻结)
    → 不触碰直到需要独立验证
```

### Q8: 怎样控制 Ceiling / Floor?

**Ceiling 控制**：
- 目标：B1 无 Cue 时准确率 < 90%，平均时间 > 3s
- 方法：排除 TRIVIAL 类型案例；选择有 plausible alternative interpretation 的案例
- Pilot 验证：如果 B1 准确率 > 90% 或 <3s 占比 > 50%，说明案例集仍需调整

**Floor 控制**：
- 目标：B1 无 Cue 时准确率 > 50%（高于随机猜测），Human 能完成任务
- 方法：确保每个案例有足够的证据（image + TLD + text patterns）
- 记录 evidence_available，排除 evidence 完全缺失的案例

**目标区域**：

```
可判断 (accuracy > 50%)
    +
非瞬时 (time > 3s)
    +
证据可能有用 (Cue 有相关信息)
```

### Q9: 怎样控制 Case independence?

当前问题：
- is11_efficientnet_p6: 95 候选（一张大表）
- is11_cs_001_p3: 87 候选（一张大表）
- is11_efficientnet_p7: 72 候选（一张大表）

同一页表格产生的候选不是独立观察——它们共享相同的表格结构、列布局、行模式。

**独立审计要求**：

| 维度 | 限制 | 理由 |
|---|---|---|
| 同一 doc+page 的案例数 | ≤ 3 | 同一页的案例共享布局上下文 |
| 同一表格的案例数 | ≤ 2 | 同一表格的案例共享列结构 |
| 同一文档的案例数 | ≤ 30% | 避免文档特异性主导 |
| 近重复检测 | 文本相似度 > 0.8 的候选对标记为近重复 | 防止同一模式被多次计数 |

**报告要求**：
```
case_count = N
document_count = D
page_count = P
independent_settings = unique(doc, page, family) combinations
near_duplicate_groups = M
```

**实际数据**：prose + figure 候选共 41 个，来自 25 个不同页面，4 个文档。这些是池中最独立的子集。

### Q10: 最终最小 Case Construction Protocol

```
Input: Candidate Pool (545 candidates from frozen P1-P6)

Step 1: Research Question Definition
    → 明确: "Evidence Cue 是否降低 Human 认知/操作成本同时保持质量和边界安全"
    → 定义: 可测变量 = decision_time, accuracy, expansion_count, UNKNOWN_rate, override_rate

Step 2: Structural Candidate Classification
    → 分类每个 candidate 为:
       TRIVIAL_NUMERIC_PAIR / TRIVIAL_HEADER_PAIR /
       PROSE_BOUNDARY / FIGURE_CAPTION / ROW_LABEL_VALUE / OTHER
    → 方法: 基于文本内容 + 长度 + 数字检测 (脚本实现, 无需新模块)

Step 3: Low-value / Trivial Relation Exclusion
    → 排除: TRIVIAL_NUMERIC_PAIR (252) + TRIVIAL_HEADER_PAIR (93)
    → 保留: PROSE_BOUNDARY (30) + FIGURE_CAPTION (11) + 部分 ROW_LABEL_VALUE (~30) + OTHER (42)
    → 产出: ~113 evaluation-valuable candidates

Step 4: Coverage Selection
    → 目标分布 (非严格配额):
       MERGE-eligible: 20-30% (prose same-sentence, figure caption parts)
       KEEP_SEPARATE-eligible: 30-40% (prose boundary, trivial-but-kept)
       UNKNOWN-eligible: 10-15% (evidence-missing or genuinely ambiguous)
       Boundary: 15-20% (plausible alternative both directions)
       Conflict: 5-10% (cue direction ≠ likely GT)
    → 注意: GT 尚未分配, 此处基于结构特征估计

Step 5: Evidence Availability Check
    → 每个候选记录:
       image_available (Y/N)
       TLD_available (Y/N)
       structural_evidence_available (Y/N)
    → 排除: evidence 完全缺失的候选 (Floor risk)

Step 6: Diversity / Independence Check
    → 同一 doc+page: ≤ 3 cases
    → 同一文档: ≤ 30%
    → 近重复检测: 文本相似度 > 0.8 → 标记
    → 报告: case_count, document_count, page_count, independent_settings

Step 7: Potential Boundary / Conflict / UNKNOWN Coverage
    → Boundary: 选择有 plausible alternative 的案例 (plausible_merge AND plausible_keep)
    → Conflict: 选择 TLD evidence 与文本模式暗示不一致的案例
    → UNKNOWN: 选择 evidence 部分缺失的案例
    → 注意: 这些是 "potential", 非 GT

Step 8: Pilot (Discovery Set, ~10-15 cases)
    → 小规模 Human 实验
    → 观察: decision_time, accuracy, expansion, UNKNOWN
    → 目标: 发现 ceiling/floor, 发现 case quality 问题
    → NOT for final analysis

Step 9: Observe Human Difficulty
    → 从 Pilot 行为数据中发现:
       - 哪些案例太简单 (time < 3s, accuracy = 100%) → 替换
       - 哪些案例太难 (accuracy < 50%) → 检查 evidence 或标记 UNKNOWN-eligible
       - 哪些案例有分歧 (different participants chose differently) → 保留为 boundary
    → 这是 Behavioral Discovery, 非 Pre-assumed Difficulty

Step 10: Freeze Evaluation Set
    → 基于 Pilot 发现调整案例集
    → 预注册分析合同 (analysis contract)
    → 冻结案例集, 不再修改
    → 正式实验使用此集
    → Independent Holdout 保留不动
```

---

## Part II — Evaluation Opportunity Definition

### 概念

**Evaluation Opportunity** = 一个 Candidate 是否存在值得通过 Human Experiment 测量的研究空间。

### 判定条件 (全部满足 = HIGH evaluation opportunity)

| 条件 | 定义 | 检查方法 |
|---|---|---|
| A. Human has meaningful semantic decision | 不是纯数字/纯列头的平凡判断 | 文本内容分析 |
| B. Evidence can potentially help | 证据字段存在且与判断相关 | evidence_available 检查 |
| C. Cue could plausibly change accessibility | B1 中证据需要展开/搜索才能理解 | 字段数量 + progressive disclosure 设计 |
| D. Not trivially solvable from surface form | 不能仅凭 text_a/text_b 在 <3s 确定 | Pilot 行为验证 |
| E. Not impossible due to missing evidence | 有足够证据完成判断 | evidence sufficiency 检查 |

### 当前 545 候选的 Evaluation Opportunity 评估

| 评估 | 数量 | 占比 | 类型 |
|---|---|---|---|
| HIGH | ~41 | 8% | PROSE_BOUNDARY + FIGURE_CAPTION |
| MEDIUM | ~70 | 13% | 部分 ROW_LABEL_VALUE + OTHER |
| LOW | 345 | 63% | TRIVIAL_NUMERIC + TRIVIAL_HEADER |
| UNKNOWN | ~89 | 16% | 需要进一步分析 |

---

## Part III — Challenge Set vs Prevalence Set

### 定义

| 类型 | 目标 | 分布要求 |
|---|---|---|
| **Prevalence Set** | "现实中各种情况有多常见？" | 尊重自然分布 |
| **Challenge Set** | "系统在关键边界上能否支持 Human？" | 有意识增加 boundary/conflict/UNKNOWN |

### 当前实验应属于哪种?

**Challenge Set**。研究问题是"Evidence Cue 是否降低 Human Effort 同时保持质量和边界安全"——这需要**有意识地覆盖边界条件**，而非尊重自然分布。

自然分布（545 候选中 63% 是平凡表格对）会导致天花板效应，无法检验 Cue 效果。

### 但必须声明

> Challenge Set 的结果**不是 prevalence estimate**。不能从 Challenge Set 的错误率推断"系统在现实中的错误率"。Challenge Set 回答的是"在最需要支持的边界上，系统是否有效"。

---

## Part IV — MERGE/KEEP 不平衡分析

### 当前分布的危险

```
KEEP_SEPARATE = 43/45 (96%)
MERGE = 2/45 (4%)
```

| 风险 | 影响 |
|---|---|
| **Decision ceiling** | KEEP_SEPARATE 案例太多 → Human 倾向于默认 KEEP → MERGE 案例被错误地 KEEP |
| **Cue effect detectability** | 只有 2 个 MERGE 案例 → Cue 是否帮助正确识别 MERGE 无法统计 |
| **Automation bias detectability** | 如果 Cue 说"KEEP_SEPARATE"（与多数案例一致），Human 跟随 Cue 可能只是先验偏好，不是 Cue 效果 |
| **Boundary safety** | 无法测试"Cue 是否诱导错误 MERGE"——因为没有足够的 MERGE 案例来区分正确和错误 MERGE |

### 但不允许人为平衡

- ❌ 不修改 GT
- ❌ 不制造 MERGE 案例
- ❌ 不翻转 GT
- ❌ 不复制案例

### 解决方案

从 545 候选池中选择**结构上更可能是 MERGE 的候选**（prose same-sentence parts, figure caption parts），然后通过 GT adjudication 确定它们的真实标签。如果自然 GT 分布仍然是大部分 KEEP_SEPARATE，那么：

1. 接受这个分布，但确保有足够的 boundary 案例（plausible MERGE 但 GT = KEEP_SEPARATE）
2. 明确报告 GT 分布，在分析中控制先验偏好
3. 使用 within-subject 设计（每个参与者在 B1 和 B2 下看到相同案例），而非 between-subject 比较

---

## Part V — Matched Cases

### 是否需要 Matched Cases?

**是的，概念上有价值**。

Matched cases 可以控制"案例难度"这个混淆变量：

```
Case X: 相同结构模式, 不同语义上下文
    → 如果 B1 vs B2 差异在 X1 显著但在 X2 不显著
    → 说明差异来自语义上下文, 不是结构模式
```

例如：
- X1: `'degrades rapidly.' / 'Unexpectedly,'` (prose, sentence boundary, GT=KEEP)
- X2: `'0.1% (Fig. 6, right).' / 'Its test error is still fairly good'` (prose, sentence boundary, GT=KEEP)

两者都是"句号结尾 + 新句子开头"，但语义内容不同。如果 Cue 在 X1 有效但在 X2 无效，说明 Cue 效果依赖于语义内容而非结构模式。

### 但不立即实施

Matched case 构造需要：
1. 定义"匹配"标准（结构模式相似度）
2. 在候选池中搜索匹配对
3. 确保匹配对来自不同文档/页面

这可以作为未来 Pilot 后的精细化步骤，不需要在初始案例集中实现。

---

## Part VI — Pilot 的真正作用

### 重新定义

Pilot **不是**"先跑一遍实验看看结果"。

Pilot **是**"发现 Evaluation Case Quality"。

### Pilot 能发现什么

| 发现 | 行动 |
|---|---|
| Case too trivial (time < 3s, accuracy = 100%) | 替换为更难的候选 |
| Case too difficult (accuracy < 50%) | 检查 evidence 或标记 UNKNOWN-eligible |
| Case redundant (similar to another) | 合并或删除 |
| Case semantically meaningless | 删除 |
| Case evidence insufficient | 修复 evidence 或删除 |
| Case cue irrelevant | 标记为 Type 2 (Cue Redundant) |
| Case cue misleading | 标记为 Type 3 (Cue Misleading) |
| Case genuinely discriminative | 保留为正式案例 |

### Pilot ≠ System Optimization

```
Pilot → Case Quality Feedback → Evaluation Set Refinement

NOT:

Pilot → System Optimization → Same Cases → "Success"
```

---

## Part VII — Development / Evaluation / Holdout 分离

### 最小数据分离

| 层 | 目的 | 允许 | 禁止 |
|---|---|---|---|
| **Discovery** | 找候选, 观察质量 | 迭代, 调整 | 不用于最终分析 |
| **Pilot** | 发现 Human difficulty | 观察行为 | 不进入正式评估 |
| **Frozen Evaluation** | 正式实验 | 预注册分析 | 根据结果调整案例 |
| **Holdout** | 独立验证 | 不触碰 | 在熟悉案例上优化 |

### 防止 Same-Set Iteration

```
发现问题 → 调整系统 → 同一案例验证 → "成功" → FALSE GENERALIZATION
```

这是当前实验面临的风险：分析合同在案例选择之后编写，P722 数据在分析合同之后收集。虽然没有正式的"调整系统"步骤，但 UI 修复（progressive disclosure, image size）发生在 P722 数据收集过程中，可能影响数据一致性。

---

## Part VIII — Evidence Availability

### 每个案例必须记录

| 字段 | 含义 | 影响 |
|---|---|---|
| image_available | 页面图像是否可用 | Human 能否看到上下文 |
| TLD_available | table_line_detector 输出是否可用 | 结构证据是否存在 |
| structural_evidence_available | 综合结构证据 | 判断是否有足够信息 |
| cue_available | Evidence Cue 是否已计算 | B2 条件是否可执行 |

### 原则

> Evidence missing ≠ semantic difficulty

如果 evidence 缺失导致 Human 无法判断，那是 **Floor Effect**，不是"案例难"。必须分开记录和报告。

---

## Part IX — Human Feedback 如何进入 Case Construction

### 设计

```
Candidate → Evaluation Case → Human Pilot → Feedback → Case Quality Audit → Evaluation Set Refinement
```

### Feedback 类型

| Human 说 | 反馈类型 | 用途 |
|---|---|---|
| "这个案例不需要看 Cue" | Case-level: Cue Redundant | 标记为 Type 2 |
| "这个案例信息不足" | Case-level: Evidence Missing | 标记为 UNKNOWN-eligible 或修复 |
| "这个案例没有判断价值" | Case-level: Trivial | 从评估集移除 |
| "这个 Cue 对这种案例没帮助" | Pattern-level: Cue Ineffective | 未来 Cue 设计参考 |

### 边界

这些反馈是 **Evaluation Design Feedback**，不是 Runtime Rule：

- ✅ 用于改进未来评估集
- ✅ 用于标注案例类型
- ❌ 不自动变成系统规则
- ❌ 不成为 Learning Engine 输入

---

## Part X — Anti-Overdesign Gate

| 新增项 | 需要? | 理由 |
|---|---|---|
| Case Builder module | **NO** | 现有脚本 + 结构分类 + 覆盖选择足够 |
| Difficulty Engine | **NO** | Human difficulty 通过 Pilot 行为发现 |
| Semantic Difficulty Classifier | **NO** | 结构分类 + plausible-alternative 检查足够 |
| Pattern Engine | **NO** | 与案例构造无关 |
| Learning Engine | **NO** | Case Construction 是评估方法论, 非系统学习 |
| Feedback Engine | **NO** | Human feedback 手动审查, 非自动化 |
| Evaluation Runtime | **NO** | 现有实验服务器足够 |
| 新 primitive | **NO** | 无需新原子操作 |
| 新 authority-bearing object | **NO** | 评估案例无运行时权限 |

### 只需要的最小工具

1. **结构分类脚本** — 基于文本内容/长度/数字检测, Python 脚本, ~50 行
2. **覆盖统计脚本** — 按结构 family × GT × evidence 统计, ~30 行
3. **近重复检测脚本** — 文本相似度, ~20 行
4. **研究协议文档** — Case Construction Protocol, Pilot 设计, 分析合同模板

所有都是**脚本和文档**, 非 DICE 运行时模块。

---

## Part XI — Final Coverage Matrix

### 目标 Coverage Matrix (设计目标, 非实现)

| 维度 \ 结构 | TABLE | PROSE | FIGURE | OTHER | 总目标 |
|---|---|---|---|---|---|
| MERGE | 5-10% | 10-15% | 5-10% | 0-5% | 20-30% |
| KEEP_SEPARATE (non-trivial) | 10-15% | 10-15% | 0-5% | 5-10% | 30-40% |
| UNKNOWN | 0-5% | 5-10% | 0-5% | 0-5% | 10-15% |
| Boundary | 5-10% | 5-10% | 0-5% | 0-5% | 15-20% |
| Conflict | 0-5% | 0-5% | 0-5% | 0-5% | 5-10% |
| **总 TABLE** | **20-30%** | | | | (reduced from 78%) |
| **总 PROSE** | | **20-35%** | | | (increased from 9%) |
| **总 FIGURE** | | | **10-15%** | | (increased from 4%) |

### 当前 vs 目标

| 维度 | 当前 | 目标 | Gap |
|---|---|---|---|
| TABLE | 78% | 20-30% | ❌ 严重过度 |
| PROSE | 9% | 20-35% | ❌ 严重不足 |
| FIGURE | 4% | 10-15% | ❌ 不足 |
| MERGE | 4% | 20-30% | ❌ 严重不足 |
| Boundary | 13% | 15-20% | ⚠️ 接近但质量不足 |
| Conflict | 4% | 5-10% | ⚠️ 接近 |
| UNKNOWN | 0% | 10-15% | ❌ 完全缺失 |

---

## Part XII — 最终推荐 Pipeline

```
P1-P6 / Atomic Observation (FROZEN)
          ↓
     Candidate Pool (545, EXISTING)
          ↓
Structural Classification (NEW SCRIPT, ~50 lines)
          ↓
Research-question Alignment Filter (NEW PROTOCOL)
    → 排除 TRIVIAL_NUMERIC + TRIVIAL_HEADER
    → 保留 PROSE_BOUNDARY + FIGURE_CAPTION + 部分 ROW_LABEL_VALUE
    → 产出 ~113 evaluation-valuable candidates
          ↓
Triviality / Low-value Filter (NEW SCRIPT, ~30 lines)
    → 进一步排除 surface-trivial 案例
    → 产出 ~80-90 candidates
          ↓
Coverage Construction (NEW PROTOCOL)
    → 按目标分布选择
    → 确保 MERGE/KEEP/UNKNOWN/Boundary/Conflict 覆盖
          ↓
Evidence Sufficiency Check (NEW SCRIPT, ~20 lines)
    → 记录 image/TLD/structural evidence availability
    → 排除 evidence 完全缺失
          ↓
Diversity / Independence Check (NEW SCRIPT, ~20 lines)
    → 同页 ≤3, 同文档 ≤30%, 近重复检测
          ↓
       Pilot (Discovery Set, 10-15 cases)
          ↓
Observed Human Difficulty (BEHAVIORAL, NOT PRE-ASSUMED)
    → time, accuracy, expansion, UNKNOWN, disagreement
          ↓
Case Quality Refinement (MANUAL REVIEW)
    → 替换 trivial, 检查 floor, 标记 types
          ↓
 Frozen Evaluation Set (FREEZE + PRE-REGISTER)
          ↓
Formal Human Experiment
          ↓
Independent Holdout (UNTOUCHED)
```

---

## Part XIII — What is Known vs Hypothesized vs Requires Pilot

### Known (已确认)

1. 当前 45 案例有严重天花板效应 (P722: B1 100% accuracy, 100% <3s)
2. 几何筛选器 (h_gap 8-50pt) 被表格结构淹没 (63% trivial)
3. 545 候选中有 ~41 个高评估价值候选 (PROSE + FIGURE, 来自 25 个独立页面)
4. 当前 GT 分布 43:2 无法测试 MERGE boundary
5. Case Construction 的设计原则和 Pipeline 已定义

### Hypothesized (假设, 未验证)

1. ~113 个 evaluation-valuable 候选中约 30% 是 genuine boundary (≈34 cases)
2. 从 PROSE_BOUNDARY + FIGURE_CAPTION 中可以获得 ~20-30% MERGE 标签
3. Pilot 后 B1 准确率可降至 70-85% (移除天花板)
4. B1 vs B2 在 non-trivial 案例上可能有可测差异

### Requires Pilot Evidence (必须通过 Pilot 验证)

1. 哪些具体案例是 "non-trivial" (time > 3s)
2. B1 无 Cue 时的准确率分布
3. 哪些案例产生 reviewer/participant disagreement
4. Cue 在哪些案例上真正改变了行为
5. UNKNOWN 率是否足够支持边界安全分析
6. 113 个候选中多少是真正独立的 (near-duplicate 检测后)
