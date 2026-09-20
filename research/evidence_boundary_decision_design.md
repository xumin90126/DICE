# Evidence Boundary Decision Design

> READ-ONLY 架构设计。不修改任何代码。不实施。不进入 P7.3。
> 吸收 P4 v3 Design 结论到 DICE 的 Evidence Boundary / Human-on-the-Boundary 原则中。

---

## 0. 背景与定位

### P4 v3 Design 结论回顾

P4 v3 Design (Gate = B. DESIGN-INCONCLUSIVE) 通过跨 8 文档审计证明：

- 纯 geometry/layout 可以**可靠识别**一部分 Text Unit Relation（gap≤8 → merge；gap>50 / different style / line_obs>15 → block）
- 纯 geometry/layout 可以**可靠阻断**一部分明显错误关系（cross-column, formula dense line, formula symbol）
- 但存在一部分 relation 在当前 observation 信息空间中**不可判定**（same_y + same_style + gap 8-50 + w_b 15-25 → TRUE merge 与 FALSE merge 几何同构）

### 本文档目标

将上述结论吸收为 DICE 的正式架构原则：**三态 Relation 模型 + Human-on-the-Boundary**。

本架构不修改 P4 / P7.1 / P7.2 的任何代码或冻结状态。它是对现有系统行为的**概念性重新解释**——为 Human Validation 提供理论依据，而非新增处理层。

---

## 一、三态 Text Unit Relation 模型

### 1.1 定义

| 状态 | 含义 | 几何证据 | 机器决定? | 人类介入? |
|---|---|---|---|---|
| `DETERMINISTIC_MERGE` | 有足够稳定的几何证据，可以确定两个 observation 属于同一 Text Unit | gap≤8 + same_y + same_style | ✅ 是 | ❌ 否 |
| `DETERMINISTIC_BLOCK` | 有足够稳定的几何证据，可以确定两个 observation 不应 merge | gap>50 (cross-column) OR different_style OR line_obs>15 OR w_b<15 (formula symbol) | ✅ 是 | ❌ 否 |
| `AMBIGUOUS` | 当前 observation 信息不足以可靠决定 merge/block | 8<gap≤50 + same_style + line_obs≤15 + w_b≥15（TRUE merge 与 FALSE merge 几何同构） | ❌ 否 | ✅ 是 |

### 1.2 实证基础

跨 8 文档审计（762 个 same-y observation pair）：

| 状态 | 对数 | 占比 | 处理方式 |
|---|---|---|---|
| DETERMINISTIC_MERGE (gap≤8) | 351 | 46.1% | P4 v2 自动合并（frozen） |
| DETERMINISTIC_BLOCK_CROSS (gap>50) | 84 | 11.0% | 自动阻断 |
| DETERMINISTIC_BLOCK_FONT (different style) | 84 | 11.0% | 自动阻断 |
| DETERMINISTIC_BLOCK_DENSE (line_obs>15) | 71 | 9.3% | 自动阻断 |
| DETERMINISTIC_BLOCK_NARROW (w_b<15) | 129 | 16.9% | 自动阻断 |
| **AMBIGUOUS** | **43** | **5.6%** | **Human Review** |
| **合计** | **762** | **100%** | |

**关键数据**：
- 94.4% 的 pair 可被机器确定性处理
- 5.6% 的 pair 进入 AMBIGUOUS → Human Review
- AMBIGUOUS 中 30 TRUE merge（69.8%）+ 13 FALSE merge（30.2%）
- 自动 merge 的 precision = 69.8% → **不足以作为 DETERMINISTIC_MERGE**

### 1.3 AMBIGUOUS 的文档分布

| 文档 | AMBIGUOUS 对数 | TRUE | FALSE |
|---|---|---|---|
| arxiv_toc | 22 | 22 | 0 |
| arxiv_2307 | 17 | 4 | 13 |
| arxiv_bio_body | 4 | 4 | 0 |
| RA101 | 0 | 0 | 0 |
| RM501-P4 | 0 | 0 | 0 |
| E804 | 0 | 0 | 0 |
| C216 | 0 | 0 | 0 |
| DC201 | 0 | 0 | 0 |

**设备手册（5 个）的 AMBIGUOUS = 0。** Human Review 完全由 uncertainty 驱动，而非 document volume 驱动。

---

## 二、能力分离

### 2.1 四层能力定义

| 层 | 职责 | 输入 | 输出 | 边界约束 |
|---|---|---|---|---|
| **P4** | Geometric text reconstruction / relation observation | P1 observation + P2 geometry + P3 style | Span（merged or separate） | 只用 geometry/layout；不读文本内容；frozen v2 |
| **P7.1** | StructureHypothesis observation | P4 span + P5 reading order + P6 region | StructureHypothesis (immutable, PROPOSED) | 只观察结构；不修改 span；frozen |
| **Human Validation** | 解决机器无法可靠决定的 semantic boundary | AMBIGUOUS relation + page image + geometric context | ValidationRecord (immutable, ACCEPT/REJECT/NEED_REVIEW) | 只处理 AMBIGUOUS；不重新 annotation；不修改 span |
| **Evidence** | 可验证结果的 derived layer | ValidationRecord (ACCEPT only) | ValidatedEvidence | 只从 ACCEPT 派生；不可被 runtime 覆盖 |

### 2.2 禁止的跨层行为

| 禁止行为 | 理由 |
|---|---|
| P7.1 合并 P4 未合并的 span | 违反 layer 职责——P7.1 是 observer，不是 reconstructor |
| Human Validation 直接修改原始 span | Span 是 immutable P4 输出——human 决定的是 relation，不是 span 本身 |
| Evidence 回写修改 P4/P7.1 | Evidence 是 derived layer——不可反向影响 source |
| Runtime 自动接受 AMBIGUOUS pair | Runtime authority = ZERO——AMBIGUOUS 必须经人类决定 |
| 下游模块偷偷修复 P4 fragmentation | Fragmentation 是 P4 的合法输出（保守策略）——不是 bug |

---

## 三、Decision Flow

```
Text Observation (P1, immutable)
         ↓
    Geometry (P2) + Style (P3)
         ↓
    P4 Span Construction (FROZEN v2)
    ┌─────────────────────────────────────┐
    │ gap≤8 + same_y + same_style         │ → DETERMINISTIC_MERGE → Span(merged)
    │ gap>50                              │ → DETERMINISTIC_BLOCK → Span(separate)
    │ different_style                     │ → DETERMINISTIC_BLOCK → Span(separate)
    │ (other gap≤8 conditions)            │ → DETERMINISTIC_MERGE/BLOCK per P4 rules
    │ 8<gap≤50 + same_y + same_style      │ → KEEP_SEPARATE (P4 conservative)
    └─────────────────────────────────────┘
         ↓
    P5 Reading Order → P6 Region → P7.1 StructureHypothesis (FROZEN)
    ┌─────────────────────────────────────┐
    │ Each span → StructureHypothesis      │
    │ hypothesis_type, confidence, signals │
    └─────────────────────────────────────┘
         ↓
    Relation Assessment (CONCEPTUAL, not a new code module)
    ┌──────────────────────────────────────────────────┐
    │ For each adjacent candidate pair:                │
    │                                                  │
    │ If P4 merged → DETERMINISTIC_MERGE (no review)   │
    │ If gap>50 → DETERMINISTIC_BLOCK (no review)      │
    │ If different_style → DETERMINISTIC_BLOCK         │
    │ If line_obs>15 → DETERMINISTIC_BLOCK (formula)   │
    │ If w_b<15 → DETERMINISTIC_BLOCK (symbol)         │
    │ If 8<gap≤50 + same_style + line≤15 + w_b≥15      │
    │   → AMBIGUOUS                                    │
    └──────────────────────────────────────────────────┘
         ↓
    ┌──────────────┬──────────────┐
    │              │              │
 DETERMINISTIC   DETERMINISTIC   AMBIGUOUS
    _MERGE         _BLOCK
    │              │              │
    ↓              ↓              ↓
 Automatic      Automatic    Human Boundary
 (no human)     (no human)       Review
    │              │              │
    │              │         ┌────┴────┐
    │              │         │         │
    │              │      ACCEPT     REJECT
    │              │         │         │
    ↓              ↓         ↓         ↓
 Evidence      No Evidence  Evidence  No Evidence
 (derived)     (derived)   (derived)  (derived)
```

### 3.1 哪些情况机器可以决定？

| 情况 | 决定 | 证据 |
|---|---|---|
| gap≤8 + same_y + same_style | MERGE | 351 对，P4 v2 已正确处理，跨 8 文档稳定 |
| gap>50 | BLOCK | 84 对，cross-column，100% 正确 |
| different_style | BLOCK | 84 对，structural boundary，100% 正确 |
| line_obs>15 | BLOCK | 71 对，formula dense line，100% 正确 |
| w_b<15 | BLOCK | 129 对，formula symbol，100% 正确 |

### 3.2 哪些情况机器只能 BLOCK？

P4 v2 当前对 8<gap≤50 的 same-y pair 执行 KEEP_SEPARATE。这实际上是保守 BLOCK——但它是**缺乏 merge 证据的 BLOCK**，不是**有 block 证据的 BLOCK**。

在概念上，这些 pair 应被重新解释为 AMBIGUOUS，而非 DETERMINISTIC_BLOCK。但 P4 是 frozen 的，所以 P4 的输出（KEEP_SEPARATE）不变——重新解释发生在 Relation Assessment 概念层。

### 3.3 哪些情况必须进入 Human Review？

**仅 AMBIGUOUS 状态的 pair 进入 Human Review。**

判定条件（全部满足）：
1. same_y (Δy≤3pt)
2. same_style (style_signature 一致)
3. 8 < gap ≤ 50pt
4. line_obs_count ≤ 15（不是 formula dense line）
5. w_b ≥ 15pt（不是 pure formula symbol）

这些 pair 的特征与 TRUE merge 几何同构，但 auto-merge precision 仅 69.8%——不足以确定性 merge。

### 3.4 Human Review 的输入是什么？

| 输入项 | 来源 | 说明 |
|---|---|---|
| Page image | P1 | 原始 PDF 页面渲染 |
| Candidate A bbox + text | P4 span → P7.1 hypothesis | 高亮框 A |
| Candidate B bbox + text | P4 span → P7.1 hypothesis | 高亮框 B |
| Geometric context | Relation Assessment | gap, Δy, same_style, line_obs_count, w_b |
| System suggestion | suggestion.py | "系统无法确定这两个候选是否属于同一文本单元" |
| Decision buttons | UI | ✓是同一文本单元 / ✕不是 / ?无法确定 |

### 3.5 Human 是否需要重新 annotation？

**否。** Human 只确认或拒绝系统提出的 boundary hypothesis。

系统提出："候选 A 和候选 B 可能属于同一文本单元（AMBIGUOUS）"

Human 决定：
- **ACCEPT**："是的，它们是同一个标题/文本单元" → Evidence 记录 merge
- **REJECT**："不是，它们是独立的" → 无 Evidence，保持 separate
- **NEED_REVIEW**："无法确定" → 升级或暂缓

Human 不重新画框、不重新标注文本、不修改 span。Human 只对**关系**做二元判断。

### 3.6 Human 是否只是确认系统提出的 boundary hypothesis？

**是。** 系统基于几何特征识别 AMBIGUOUS pair → 提出 boundary hypothesis → Human 确认/拒绝。

这不是开放式 annotation——而是**对系统 hypothesis 的验证**。与 P7.2 ValidationTask → ValidationRecord 的现有流程完全一致。

---

## 四、AMBIGUOUS 深度定义

### 4.1 AMBIGUOUS_TEXT_UNIT_RELATION

```
AMBIGUOUS_TEXT_UNIT_RELATION
```

**定义**：两个 geometrically adjacent observations，其 layout/style 特征与"同一文本单元"一致（same_y, same_style, gap in contested zone, non-formula-density），但当前 observation 信息空间中不存在能够可靠区分 TRUE merge 与 FALSE merge 的几何特征。

### 4.2 为什么产生

AMBIGUOUS 产生于 observation 信息空间的**固有局限性**，而非系统错误。

具体原因：
- TRUE merge（如 "1" + "Introduction"）和 FALSE merge（如 "ψ" + "[recall"）在以下特征上**完全同构**：
  - Δy ≈ 0pt（同一基线）
  - same_style（同一字体/字号/颜色）
  - gap 在 8-50pt 区间
  - line_obs_count ≤ 15（不是 formula dense line）
  - w_b ≥ 15pt（不是 pure symbol）
- 区分它们需要**文本内容理解**（"1" 是序号 vs "ψ" 是公式符号），而 P4 契约禁止文本内容分析

### 4.3 什么时候产生

| 条件 | 值 |
|---|---|
| Δy | ≤ 3pt |
| same_style | ✅ |
| gap | 8pt < gap ≤ 50pt |
| line_obs_count | ≤ 15 |
| w_b | ≥ 15pt |

当以上条件**全部满足**时，pair 进入 AMBIGUOUS。

### 4.4 为什么不能自动 merge

- Auto-merge precision = 69.8%（30 TRUE / 43 total）
- 13 个 FALSE merge 会被错误合并（公式碎片与正文过渡）
- 这会破坏公式结构（如 "ψ" + "[recall" 合并后变成无意义文本）

### 4.5 为什么也不能简单 block

- 30 个 TRUE merge 会被错误阻断（TOC 序号+标题、正文 section heading 保持碎片化）
- P7.1 会为每个碎片生成独立的 StructureHypothesis → heading candidate 碎片化
- 这正是当前 arxiv_toc p2 的问题（33 个 candidate → calibration_filter 压缩到 10 个）

### 4.6 如何进入 Human Validation

```
AMBIGUOUS pair
    ↓
ValidationTask (derived from Relation Assessment + P7.1 StructureHypothesis)
    ↓
Review Web UI presents:
    - Page image with both candidates highlighted
    - Geometric context (gap, Δy, style, line_obs)
    - System suggestion: "无法确定这两个候选是否属于同一文本单元"
    - Decision: ✓同一文本单元 / ✕不同 / ?无法确定
    ↓
Human decision → ValidationRecord (immutable)
```

### 4.7 Human 最终决定什么

Human 决定的是**两个 observation 之间的 relation**：

| Human decision | Relation 赋值 | 对 span 的影响 | 对 Evidence 的影响 |
|---|---|---|---|
| ACCEPT | SAME_TEXT_UNIT | 无（span 不变） | ValidatedEvidence 记录 "A 和 B 属于同一文本单元" |
| REJECT | DIFFERENT_TEXT_UNIT | 无（span 保持 separate） | 无 Evidence |
| NEED_REVIEW | UNKNOWN | 无 | 无 Evidence，标记为待定 |

**Human 不修改 span。** Span 是 P4 的 immutable 输出。Human 决定的是 relation——这是 Evidence 层的 derived 信息，不是 P4 层的修改。

### 4.8 决策后如何形成可追溯 provenance

```
Provenance chain (per AMBIGUOUS pair):

1. P1 Observation A (immutable, source_index, bbox, text)
2. P1 Observation B (immutable, source_index, bbox, text)
3. P4 MergeDecision (immutable, decision=KEEP_SEPARATE, reason="gap>8pt")
4. P4 Span A (immutable, from Observation A)
5. P4 Span B (immutable, from Observation B)
6. P7.1 StructureHypothesis A (immutable, PROPOSED)
7. P7.1 StructureHypothesis B (immutable, PROPOSED)
8. Relation Assessment: AMBIGUOUS (derived, with geometric evidence)
9. ValidationTask (derived, from AMBIGUOUS + Hypothesis A + Hypothesis B)
10. ValidationRecord (immutable, Human verdict: ACCEPT/REJECT/NEED_REVIEW)
11. ValidatedEvidence (derived, ACCEPT only: "A and B are SAME_TEXT_UNIT")
12. ValidationAuditChain (links 1-11, tamper-evident)
```

每一步都有明确的 producer、timestamp、和 immutable 标记。Audit chain 确保从 P1 observation 到最终 Evidence 的完整可追溯性。

### 4.9 AMBIGUOUS ≠ 什么

| AMBIGUOUS 不是 | 理由 |
|---|---|
| ❌ FAILED EXTRACTION | P1/P4 正确提取了所有 observation——extraction 成功 |
| ❌ BAD CANDIDATE | P7.1 正确生成了 StructureHypothesis——candidate 合法 |
| ❌ SYSTEM ERROR | 系统按设计运行——保守 KEEP_SEPARATE 是正确行为 |
| ❌ LOW QUALITY DATA | 数据质量正常——问题在信息空间局限性 |
| ✅ **AMBIGUOUS =** | "available evidence is insufficient for deterministic boundary decision" |

---

## 五、Human-on-the-Boundary 原则

### 5.1 核心原则

**Human review volume 应由 uncertainty 驱动，而非 document volume 驱动。**

```
Machine certainty spectrum:

High confidence ────────────────────── Uncertain ────── Clearly invalid
     │                                      │                  │
     ↓                                      ↓                  ↓
DETERMINISTIC_MERGE                    AMBIGUOUS          DETERMINISTIC_BLOCK
DETERMINISTIC_BLOCK                                       
     │                                      │                  │
     ↓                                      ↓                  ↓
Automatic handling                  Human review        Automatic block
(no human needed)               (uncertainty-driven)   (no human needed)
```

### 5.2 Human 只处理什么

| Human 处理 | 理由 |
|---|---|
| Ambiguous boundary | 几何证据不足以确定性决定 |
| Conflicting geometric signals | same_y + same_style 但 gap 在 contested zone |
| Novel layout | 新文档类型，未经 Human Validation 验证 |
| Low-confidence relation | P7.1 confidence=LOW 的 candidate pair |
| High-risk structure | heading fragmentation 影响下游理解 |

### 5.3 Human 不处理什么

| Human 不处理 | 理由 |
|---|---|
| DETERMINISTIC_MERGE pair | 机器已确定性合并，无需人类 |
| DETERMINISTIC_BLOCK pair | 机器已确定性阻断，无需人类 |
| 设备手册的全部 pair | 5 个设备手册 AMBIGUOUS=0，无需人类 |
| 正文段落内合并 | gap≤8 的正文 observation 已被 P4 自动合并 |
| 表格内部结构 | P6 region + P4 gap 规则已处理 |

### 5.4 Volume 估算

| 文档类型 | AMBIGUOUS pair 数 | Human review 需求 |
|---|---|---|
| arxiv TOC 页 | ~22 / page | 需要 |
| arxiv 正文页（含公式） | ~4-17 / page | 需要 |
| arxiv 正文页（无公式） | ~1-4 / page | 少量 |
| 设备手册 | 0 / page | **不需要** |
| **总计（8 文档样本）** | **43** | 可管理 |

**与当前 P7.2 对比**：
- 当前 P7.2 Round 1：校准后 10 个 candidate 需人工验证（arxiv_toc p2）
- AMBIGUOUS 方案：43 个 pair 需人工验证（跨 8 文档）
- 但设备手册从"需要验证所有 candidate"变成"零验证"——总体 human workload 降低

### 5.5 关于 Confidence Score 的说明

本架构**不引入 confidence score**。三态模型是离散的（DETERMINISTIC_MERGE / DETERMINISTIC_BLOCK / AMBIGUOUS），不是连续的 confidence 值。

理由：
- Confidence score 需要定义校准方法（如何将几何特征映射到 0-1 值？）
- Confidence threshold 需要跨文档验证（不同文档类型的 confidence 分布不同）
- 离散三态更确定性、更可解释、更易于 audit

如果未来需要 confidence score，它应作为 AMBIGUOUS 内部的优先级排序（哪些 AMBIGUOUS pair 先 review），而非作为 merge/block 的决策依据。

---

## 六、No LLM 原则

### 6.1 禁止项

| 禁止 | 理由 |
|---|---|
| LLM merge decision | 违反 deterministic 原则——LLM output 非确定 |
| Semantic text classification | 违反 geometry/layout only 原则 |
| Prompt-based heading recognition | 引入 LLM 的 semantic interpretation |
| LLM 自动批准 Evidence | LLM 不能成为 Evidence Authority |

### 6.2 LLM 的唯一允许角色

如果未来考虑 LLM，**只能作为 candidate suggestion / triage**：

| 允许 | 限制 |
|---|---|
| LLM 对 AMBIGUOUS pair 提供排序建议 | 不作为 merge/block 决定 |
| LLM 对 Human Review UI 提供展示排序 | 不影响 Evidence 派生 |
| LLM 对文档类型提供初步分类 | 不影响 P4/P7.1 决策 |

**LLM 永远不是 Evidence Authority。** Evidence 只从 Human ACCEPT 派生。

---

## 七、与 P7.2 Validation 的关系

### 7.1 P7.2 当前基础设施（FROZEN，不修改）

| 组件 | 状态 | 角色 |
|---|---|---|
| ValidationTask | FROZEN | 从 StructureHypothesis 派生 |
| ValidationRecord | FROZEN | Human verdict (ACCEPT/REJECT/NEED_REVIEW), immutable |
| ValidatedEvidence | FROZEN | 从 ACCEPT 派生 |
| ValidationAuditChain | FROZEN | 链接全链路 |
| calibration_filter.py | FROZEN (page-specific) | 实验性工具，非正式 pipeline |
| review_server.py | FROZEN | HTTP server, port 5072 |
| index.html | FROZEN | Web UI |
| suggestion.py | FROZEN | 系统建议生成 |

### 7.2 AMBIGUOUS 如何映射到 P7.2

AMBIGUOUS 是一个**概念性 relation 状态**，不需要新的代码模块。它映射到现有 P7.2 基础设施：

```
AMBIGUOUS relation (conceptual)
    ↓
StructureHypothesis A + StructureHypothesis B (P7.1, existing)
    ↓
ValidationTask (P7.2, existing — derived from hypothesis pair)
    ↓
Review Web UI (P7.2, existing — presents candidates to human)
    ↓
Human decision → ValidationRecord (P7.2, existing — immutable)
    ↓
ValidatedEvidence (P7.2, existing — ACCEPT only)
```

**不需要新的数据结构。** AMBIGUOUS 是对现有 P7.2 流程的**理论解释**——为什么某些 candidate pair 需要 human review：因为它们的 geometric relation 是 AMBIGUOUS，而非 DETERMINISTIC。

### 7.3 不变量保持

| 不变量 | 状态 |
|---|---|
| Observation immutable | ✅ 保持——P1/P4 输出不可变 |
| Human decision immutable | ✅ 保持——ValidationRecord 不可变 |
| Evidence 是 derived result | ✅ 保持——只从 ACCEPT 派生 |
| Runtime Authority = ZERO | ✅ 保持——runtime 不能覆盖 human decision |
| Capability Registration = Human Controlled | ✅ 保持——新文档类型需 human validation 后才获得 capability |

---

## 八、明确禁止项

| # | 禁止 | 理由 |
|---|---|---|
| 1 | 不修改 P4 v2 | P4 frozen，gap≤8 merge + gap>8 keep_separate 是当前确定性策略 |
| 2 | 不实施 P4 v3 | P4 v3 Gate = INCONCLUSIVE，irreducible FP 存在 |
| 3 | 不扩大 8pt threshold | precision 10-18%，误合并数学公式 |
| 4 | 不修改 calibration_filter | page-specific patch，不进入正式 pipeline |
| 5 | 不针对 arxiv_toc 写 special case | 不具备跨文档迁移性 |
| 6 | 不让 P7.1 修复 CandidateSpan | P7.1 是 observer，不是 reconstructor |
| 7 | 不让 Human Validation 直接修改原始 span | Span 是 immutable——human 决定 relation，不修改 span |
| 8 | 不让 LLM 成为 boundary authority | LLM 非确定，不能作为 Evidence Authority |
| 9 | 不把 ambiguous 自动判成 reject | 会错误阻断 30 个 TRUE merge |
| 10 | 不把 ambiguous 自动判成 accept | 会错误合并 13 个 FALSE merge |
| 11 | 不进入 P7.3 | 当前阶段是架构设计，不进入新阶段 |

---

## 九、架构验证（Q1-Q5）

### Q1. 三态是否足以表达当前发现的问题？

**是。**

三态模型完整覆盖了 762 个 same-y pair 的全部情况：
- DETERMINISTIC_MERGE (351, 46.1%)：P4 v2 已正确处理
- DETERMINISTIC_BLOCK (368, 48.3%)：5 种 block 模式，全部 100% precision
- AMBIGUOUS (43, 5.6%)：auto-merge precision 69.8%，不足以确定性 merge

不存在第四态。任何 pair 必属于三态之一。AMBIGUOUS 精确捕获了"几何证据不足"的 case——既不能 merge（30% false positive）也不能 block（70% false negative）。

### Q2. AMBIGUOUS 是否可以成为 DICE 中正式的一类"Evidence Boundary Uncertainty"？

**是。**

AMBIGUOUS 满足正式 Uncertainty 类型的所有条件：
1. **可实证**：43 个 pair 跨 8 文档被观测到，具有明确的几何特征边界
2. **可区分**：与 DETERMINISTIC_MERGE/BLOCK 有清晰的几何特征边界
3. **可处理**：通过 Human Validation 解决（现有 P7.2 基础设施支持）
4. **可追溯**：完整 provenance chain（P1→P4→P7.1→AMBIGUOUS→ValidationTask→Record→Evidence）
5. **非错误**：AMBIGUOUS ≠ error/bad candidate/system failure——是信息空间固有局限性
6. **不可自动解决**：69.8% precision 不足以自动 merge，30% false negative 不足以自动 block

### Q3. Human Validation 是否应该从"验证所有 Observation"演化成"验证机器无法确定的 Boundary"？

**是，且这是正确的演化方向。**

| 维度 | 当前模式 | 演化方向 |
|---|---|---|
| 驱动力 | Document volume（每个 candidate 都验证） | Uncertainty（只验证 AMBIGUOUS） |
| 设备手册 | 需验证所有 candidate | **零验证**（AMBIGUOUS=0） |
| arxiv TOC | 校准后 10 candidate | 22 AMBIGUOUS pair（更精确的 target） |
| 总 volume | 与 candidate 数成正比 | 与 uncertainty 数成正比（5.6% of pairs） |

演化路径：
1. 当前 P7.2 已支持 ValidationTask → Record → Evidence 流程
2. AMBIGUOUS 概念提供了**哪些 pair 需要 validation** 的理论依据
3. 未来实施时（NOT AUTHORIZED now），Relation Assessment 概念层可自动识别 AMBIGUOUS pair 并生成 ValidationTask
4. calibration_filter 的角色从"选 candidate"降级为"AMBIGUOUS pair 的 UI 展示辅助"

### Q4. 这种设计是否会破坏当前 P7.1/P7.2 的冻结边界？

**否。**

| 冻结边界 | 是否破坏 | 理由 |
|---|---|---|
| P7.1 StructureHypothesis schema | ❌ 不破坏 | AMBIGUOUS 不修改 hypothesis schema |
| P7.1 StructureEngine | ❌ 不破坏 | AMBIGUOUS 不修改 engine 逻辑 |
| P7.2 ValidationTask | ❌ 不破坏 | AMBIGUOUS 映射到现有 ValidationTask |
| P7.2 ValidationRecord | ❌ 不破坏 | Human decision 仍走现有 Record |
| P7.2 ValidatedEvidence | ❌ 不破坏 | Evidence 仍从 ACCEPT 派生 |
| P7.2 AuditChain | ❌ 不破坏 | 链路结构不变 |
| P4 SpanConfig | ❌ 不破坏 | P4 frozen v2 不变 |
| Frozen 730 | ❌ 不破坏 | Candidate presentation 不变 |
| CandidateSpan schema | ❌ 不破坏 | Span 是 immutable P4 输出 |

AMBIGUOUS 是**概念性重新解释**，不是代码修改。它解释了"为什么某些 pair 需要 Human Validation"，而非改变 P7.1/P7.2 的处理逻辑。

### Q5. 是否还需要继续研究 P4 v3？

**NO。**

如果没有新的 empirical evidence，不应继续研究 P4 v3。

理由：
1. P4 v3 Design 已证明：6 个 hard constraints 组合 → 0 false negative + ~13 irreducible false positive
2. Irreducible FP 的原因是**信息空间局限性**——公式碎片与 section heading 在几何上同构
3. 继续研究 P4 v3 需要新的 feature（如 text content analysis），但 P4 契约禁止文本内容分析
4. AMBIGUOUS 概念已正确接收了这个 limitation——将不可判定的 pair 路由到 Human Validation
5. 继续研究 P4 v3 而不引入新信息源 = 重复已完成的审计，不会产生新结论

**何时可以重新考虑 P4 v3？**
- 当新的 empirical evidence 出现时（如新的 geometric feature 被发现）
- 当 Human Validation 积累足够数据，证明 AMBIGUOUS pair 的某些子集可以确定性分类时
- 当文档类型扩展到新的 layout pattern，提供了新的区分信号时

在以上条件满足之前，P4 v3 研究暂停。P4 v2 保持 frozen。AMBIGUOUS → Human Validation 是当前的正确路径。

---

## 十、DESIGN STATUS

```
DESIGN STATUS  = READY

IMPLEMENTATION = NOT AUTHORIZED
P7.3           = NOT AUTHORIZED
P4 v3          = NOT AUTHORIZED (suspended pending new empirical evidence)
```

### READY 的理由

1. 三态模型完整覆盖问题空间（762 pair, 100%）
2. AMBIGUOUS 有坚实实证基础（43 pair, 跨 8 文档, 0 device manual）
3. 架构不破坏任何 frozen 边界（P4/P7.1/P7.2/Frozen 730 全部 UNCHANGED）
4. Human-on-the-Boundary 原则正确演化 Validation 方向（uncertainty-driven）
5. P4 v3 研究暂停有充分理由（irreducible FP = 信息空间局限性）
6. 现有 P7.2 基础设施完全支持 AMBIGUOUS 流程（无需新代码）

### NOT AUTHORIZED 的理由

1. 当前阶段是 READ-ONLY 架构设计
2. P4/P7.1/P7.2 全部 frozen
3. 实施 AMBIGUOUS 自动识别需要新代码（Relation Assessment 层），但本阶段禁止
4. Human Validation Infrastructure 演化需要独立批准

---

## 附录：与现有系统的映射关系

| 现有概念 | AMBIGUOUS 架构中的角色 | 变化 |
|---|---|---|
| P4 KEEP_SEPARATE (gap>8) | 重新解释为 AMBIGUOUS（部分）或 DETERMINISTIC_BLOCK（部分） | 概念性，无代码变化 |
| P7.1 StructureHypothesis | AMBIGUOUS pair 的两个 hypothesis 成为 ValidationTask 输入 | 无变化 |
| P7.2 ValidationTask | AMBIGUOUS pair 生成 ValidationTask | 无变化（已有流程） |
| P7.2 ValidationRecord | Human 对 AMBIGUOUS 的 ACCEPT/REJECT | 无变化（已有流程） |
| P7.2 ValidatedEvidence | 从 ACCEPT 派生 "A 和 B 是 SAME_TEXT_UNIT" | 无变化（已有流程） |
| calibration_filter | 降级为 page-specific UI 辅助工具 | 无变化（已暂停修改） |
| suggestion.py | 对 AMBIGUOUS pair 生成 "系统无法确定" 建议 | 无变化（已有 LOW confidence 逻辑） |

**结论：AMBIGUOUS 架构是现有系统的理论重新解释，不需要任何代码修改即可在概念层成立。实施需要独立批准。**

---

**STOP。READ-ONLY 架构设计完成。不实施。不修改任何代码。不进入 P7.3。等待下一步批准。**
