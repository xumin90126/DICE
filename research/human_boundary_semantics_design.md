# Human Boundary Semantics Design

> READ-ONLY DESIGN ONLY。不修改任何 frozen/production/source 文件。不实施。不进入 P7.3。

---

## Executive Summary

```
Round 1 Evidence Status:
  Sample: 20/43 AMBIGUOUS
  Completion: 20/20
  Raw GT Accuracy: 19/20 = 95.0%
  GT Disputed: AMB-026 (geometry-based GT vs semantic judgment)
  Adversarial Resolution: PASS (AMB-018, AMB-040)
  Human Cost: INVALID (duration_ms broken)
  Information Gain: SUPPORTED (limited to tested cases)

Human-on-the-Boundary:
  PROMISING / EMPIRICALLY SUPPORTED FOR INITIAL FEASIBILITY
  NOT GENERALIZED
  NOT FULLY VALIDATED
  NOT COST-VALIDATED

Implementation: NOT AUTHORIZED
P7.3: NOT AUTHORIZED
Frozen: INTACT
```

本阶段唯一目标：把 Human 从"人工处理 ambiguity 的人"重新定义为"产生 Boundary Evidence、帮助系统判断哪些边界可以机器化、哪些边界必须由 Human 保持"的 Evidence Source。

---

## 一、Round 1 Evidence Status

### 1.1 冻结的实验事实

| 维度 | 值 | 状态 |
|---|---|---|
| AMBIGUOUS pool | 43 | FROZEN |
| Human sample | 20/43 | FROZEN |
| Documents | 3 (arxiv_toc, arxiv_2307, arxiv_bio_body) | FROZEN |
| Modes | 4 | FROZEN |
| MERGE | 13 | FROZEN |
| KEEP_SEPARATE | 7 | FROZEN |
| CANNOT_DETERMINE | 0 | FROZEN |
| Raw GT Accuracy | 19/20 = 95.0% | FROZEN (official) |
| Excluding AMB-026 | 19/19 = 100.0% | AUXILIARY ONLY |
| Alternative semantic | 20/20 = 100.0% | HYPOTHETICAL / NOT OFFICIAL |
| AMB-026 | GT_DISPUTED | FROZEN (not modified) |
| Adversarial AMB-018 | MERGE ✅ | FROZEN |
| Adversarial AMB-040 | KEEP_SEPARATE ✅ | FROZEN |
| Duration | INVALID | FROZEN (bug documented, not fixed) |
| Information Gain | SUPPORTED (limited) | FROZEN |
| Reviewer | single (reviewer_1) | FROZEN |
| Inter-reviewer agreement | NOT MEASURED | FROZEN |

### 1.2 不修改的承诺

- 不修改 Round 1 数据
- 不修改 AMB-026 GT
- 不修复 timer
- 不扩大 sample
- 不重跑 experiment

---

## 二、核心问题：Human 到底在决定什么？

### 2.1 问题陈述

Round 1 证明了 Human 可以处理 AMBIGUOUS boundary。但"Human 做对了"不等于"我们知道 Human 做的是什么"。

需要区分三种不同的 boundary：

| Boundary 类型 | 决定什么 | 信息源 | 当前机器可做? |
|---|---|---|---|
| A. Geometry Boundary | 两个 geometric span 是否应该合并？ | gap, Δy, font, style, line_obs | P4 v2 可以（gap≤8 merge, gap>8 separate） |
| B. Semantic Text-Unit Boundary | 两个 span 是否属于同一有意义文本单元？ | 文本内容、句法、语义 | ❌ P4 契约禁止文本内容分析 |
| C. Document-Structure Boundary | span 属于什么结构角色（heading/body/table/formula）？ | 页面布局、视觉模式、区域类型 | P6 region 部分可做，但不完整 |

### 2.2 Round 1 的三种 Boundary Type

基于 20 个 case 的信息源分析：

#### Type 1: GEOMETRY_APPROXIMABLE (13 cases)

| 特征 | 说明 |
|---|---|
| Case | AMB-001~021, 023, 025, 027, 028, 034, 043 |
| Mode | TOC_SECTION_NUMBER_TITLE (12) + APPENDIX_LETTER_TITLE (1) |
| Human 信息源 | NUMBER_PATTERN + READABLE_TEXT_B + PAGE_CONTEXT |
| Human 判断 | 全部 MERGE ✅ |
| 本质 | "1" + "Introduction" — 序号+标题。P4 几何上能识别 gap/dy/font 相似，但无法区分序号 vs 公式符号 |

**关键洞察**：这 13 个 case 的 boundary 判断**理论上可以被几何近似**（如果 P4 调高 threshold 并加入 guard），但 P4 当前无法区分"序号+标题"和"公式符号+公式符号"——因为区分需要**识别 text_a 是数字编号还是数学符号**，这是语义信息。

Human 通过阅读 text_a（"1" = 数字编号）和 text_b（"Introduction" = 可读标题词）来判断它们构成 section heading。这利用了：
- 文本内容的可读性（"Introduction" 是英文单词 vs "ψ" 是符号）
- 编号模式识别（"1", "2.1", "B.1" 是编号模式）
- 页面上下文（TOC 页的布局模式）

#### Type 2: VISUAL_CONTEXT (6 cases)

| 特征 | 说明 |
|---|---|
| Case | AMB-029, 030, 032, 037, 040, 041 |
| Mode | FORMULA_FRAGMENT_WIDE |
| Human 信息源 | SYMBOL_PATTERN + FORMULA_PAGE_CONTEXT |
| Human 判断 | 全部 KEEP_SEPARATE ✅ |
| 本质 | "ψ" + "ψψ", "( )" + "cos(" — 公式碎片。Human 从公式页面上下文识别这些是公式符号，不应合并 |

**关键洞察**：这 6 个 case 的 boundary 判断需要**页面级视觉上下文**——Human 看到这是公式密集的页面行，识别符号是公式的一部分。P4 的 line_obs_count > 15 可以部分捕获这个信号（formula dense line），但对于 line_obs ≤ 15 的公式碎片（如 AMB-040, line_obs=8），几何特征不足以区分。

Human 通过页面视觉上下文（公式排版模式、符号密集度、非文字字符）来判断。这利用了：
- 页面级视觉模式（公式行 vs 标题行的视觉差异）
- 符号识别（非文字字符 = 数学符号）
- 上下文密度（周围 observation 的密集程度）

#### Type 3: PURE_SEMANTIC (1 case)

| 特征 | 说明 |
|---|---|
| Case | AMB-026 |
| Mode | BODY_TEXT_CONTINUATION |
| Human 信息源 | READABLE_TEXT_A + READABLE_TEXT_B + PUNCTUATION_BOUNDARY + SENTENCE_START_B |
| Human 判断 | KEEP_SEPARATE |
| GT | SHOULD_MERGE (DISPUTED) |
| 本质 | "transition form factor of primary interest to us." + "Its normalization is" — 两个不同句子片段在同一行 |

**关键洞察**：这个 case 暴露了最深层的问题。Human 通过**阅读文本内容的句法结构**来判断：
- text_a 以句号 "." 结尾 → 前一句的结束
- text_b 以 "Its" 开头（大写 + 代词）→ 新句子的主语
- 两者在同一行但属于不同句子 → 不应合并

这是**纯语义判断**——没有任何几何特征能区分"同行连续文本"和"同行不同句子"。P4 的 geometry-only contract 无法表达这个判断。P7.1 的 StructureHypothesis 也不处理句法分析。

### 2.3 三种 Boundary 不可混为一谈

| 混淆 | 后果 |
|---|---|
| A = B（Geometry = Semantic） | 错误假设"调 threshold 就能解决 fragmentation"——但公式碎片与标题在几何上同构 |
| B = C（Semantic = Structure） | 错误假设"识别 heading 就能判断 merge"——但 AMB-026 是 body text 句子边界，不涉及 heading |
| A = C（Geometry = Structure） | 错误假设"P4 能识别结构角色"——但 P4 只做 span reconstruction，不做 structure classification |

---

## 三、Geometry vs Semantic vs Structure Boundary

### Layer 1: GEOMETRIC_BOUNDARY

| 属性 | 值 |
|---|---|
| 定义 | 两个 geometric observation/span 是否在物理位置上属于同一连续文本区域 |
| 输入信息 | bbox, gap, Δy, font_family, font_size, style_signature, line_obs_count |
| 输出 | MERGE (same geometric region) / SEPARATE (different geometric region) |
| Authority | P4 (machine, frozen v2) |
| 自动决定? | ✅ 是（DETERMINISTIC_MERGE: gap≤8; DETERMINISTIC_BLOCK: gap>50 / diff_style / dense / narrow） |
| Human 作用 | ❌ 无（DETERMINISTIC 范围内不需要 Human） |
| AMBIGUOUS 处理 | ❌ P4 保持 KEEP_SEPARATE（保守），不自动 merge |
| 与 P4 关系 | P4 是此层的唯一 authority |
| 与 P7.1 关系 | P7.1 接收 P4 的 span 作为输入，不修改 |
| 与 P7.2 关系 | P7.2 不处理此层 |

**关键约束**：P4 只负责几何重建，不承担语义解释。P4 的 KEEP_SEPARATE 是"缺乏 merge 证据"的保守行为，不是"有 block 证据"的确定行为。AMBIGUOUS pair 的几何特征不足以确定性决定。

### Layer 2: SEMANTIC_TEXT_UNIT_BOUNDARY

| 属性 | 值 |
|---|---|
| 定义 | 两个 span 是否属于同一个有意义的文本单元（句子、短语、标题文本） |
| 输入信息 | text content, 句法结构, 标点, 语义连续性 + Layer 1 几何特征 |
| 输出 | SAME_TEXT_UNIT / DIFFERENT_TEXT_UNIT / CANNOT_DETERMINE |
| Authority | Human (via P7.2 Validation) |
| 自动决定? | ❌ 否（P4 契约禁止文本内容分析；P7.1 不做句法分析） |
| Human 作用 | ✅ 是（Human 阅读文本，判断语义连续性） |
| 与 P4 关系 | P4 不参与此层——P4 的几何 span 是输入，不是决策者 |
| 与 P7.1 关系 | P7.1 的 StructureHypothesis 基于 P4 span，但不判断 span 间的语义关系 |
| 与 P7.2 关系 | P7.2 是此层的执行通道——ValidationTask → ValidationRecord → Evidence |

**关键约束**：此层的判断**需要阅读文本内容**。P4 的 geometry-only contract 禁止此操作。Human 是此层的唯一 authority。

**AMB-026 的位置**：AMB-026 属于此层——"transition form factor of primary interest to us." 和 "Its normalization is" 的语义关系只有阅读文本才能判断。GT ontology 用几何特征（width+length）近似语义关系，在 body text 场景下产生 mismatch。

### Layer 3: DOCUMENT_STRUCTURE_BOUNDARY

| 属性 | 值 |
|---|---|
| 定义 | span 属于什么文档结构角色（heading / body / table / formula / caption / column / procedure） |
| 输入信息 | 页面布局, 视觉模式, 区域类型 (P6), reading order (P5) + Layer 1 几何特征 + Layer 2 语义特征 |
| 输出 | HEADING / BODY / TABLE_CELL / FORMULA / CAPTION / FOOTER / UNKNOWN |
| Authority | P7.1 (StructureHypothesis, machine) + Human (Validation) |
| 自动决定? | 部分——P7.1 可以 PROPOSE 结构角色，但需要 Human 验证 |
| Human 作用 | ✅ 验证 P7.1 的结构 hypothesis（ACCEPT/REJECT/NEED_REVIEW） |
| 与 P4 关系 | P4 提供 span 作为输入 |
| 与 P7.1 关系 | P7.1 是此层的主要 machine authority |
| 与 P7.2 关系 | P7.2 验证 P7.1 的 hypothesis |

**关键约束**：此层的判断需要**页面级视觉上下文**。P6 region 可以部分提供，但公式行 vs 标题行的区分需要更丰富的视觉模式识别。

**FORMULA_FRAGMENT_WIDE 的位置**：6 个公式碎片 case 跨越 Layer 2 和 Layer 3——Human 既利用了符号识别（Layer 2 语义），又利用了公式页面上下文（Layer 3 结构）。

### 三层关系图

```
Layer 1: GEOMETRIC_BOUNDARY (P4, machine)
    │
    │  P4 produces spans (merged or separate)
    │  AMBIGUOUS pairs remain KEEP_SEPARATE
    │
    ▼
Layer 2: SEMANTIC_TEXT_UNIT_BOUNDARY (Human, via P7.2)
    │
    │  Human reads text content
    │  Determines if two spans are same text unit
    │  Produces Boundary Evidence
    │
    ▼
Layer 3: DOCUMENT_STRUCTURE_BOUNDARY (P7.1 + Human)
    │
    │  P7.1 proposes structure role
    │  Human validates
    │  Produces StructureHypothesis evidence
    │
    ▼
  Evidence (derived from Human ACCEPT)
```

---

## 四、AMB-026 Ontology Mismatch

### 4.1 Mismatch 本质

| 维度 | GT ontology | 目标语义定义 |
|---|---|---|
| 判断依据 | 几何特征 (w_a≥25 AND w_b≥25 AND len≥10) | 语义关系（是否同一文本单元） |
| AMB-026 判断 | SHOULD_MERGE | SHOULD_NOT_MERGE |
| 适用场景 | 纯几何 pipeline 的粗分类 | 语义层面的 text unit boundary |
| 错误类型 | False positive（几何近似过宽） | N/A（语义定义是 ground truth） |

### 4.2 为什么产生 Mismatch

GT ontology 用几何特征来**近似**语义关系。这个近似在以下场景有效：
- TOC_SECTION_NUMBER_TITLE：序号+标题 → 几何特征（narrow + wide + same_y）与语义关系一致
- FORMULA_FRAGMENT_WIDE：公式碎片 → 几何特征（narrow + narrow + dense line）与语义关系一致

但在 BODY_TEXT_CONTINUATION 场景失效：
- 两个宽文本片段在同一行 → 几何特征（wide + wide + same_y）暗示"连续"
- 但语义上可能是两个不同句子 → "Its normalization is" 是新句子的开始

### 4.3 Mismatch 的深层含义

AMB-026 暴露的不是"GT 标错了"，而是**几何信息空间的结构性局限**：

> 当两个文本片段在同一行、宽度相似、字体相同时，几何特征无法区分"连续文本"和"不同句子"。这个区分需要**句法分析**（标点、句子结构），而句法分析属于 Layer 2 (SEMANTIC_TEXT_UNIT_BOUNDARY)，不属于 Layer 1 (GEOMETRIC_BOUNDARY)。

### 4.4 不修改 GT

GT_DISPUTED 保留为 audit finding。不修改 GT 的理由：
1. GT 是实验产物，修改它会污染实验的完整性
2. GT dispute 本身是有价值的发现——它证明了 geometry-based GT 的局限性
3. 正确的做法是在未来实验中使用语义专家标注作为 GT，而不是修改当前几何 GT

---

## 五、Human Boundary Evidence Model

### 5.1 概念模型

```
Human Decision (MERGE / KEEP_SEPARATE / CANNOT_DETERMINE)
    ↓
Boundary Observation (Human 观察到的 boundary 特征)
    ↓
Boundary Evidence (可追溯的 derived result)
```

### 5.2 Human Decision 的语义

| Decision | 语义 | Evidence 产出 | 对 P4 的影响 |
|---|---|---|---|
| MERGE | Human 判断两个 span 属于同一文本单元 | ValidatedEvidence: "A and B are SAME_TEXT_UNIT" | ❌ 无（不修改 P4 span） |
| KEEP_SEPARATE | Human 判断两个 span 不属于同一文本单元 | 无 Evidence（记录为 REJECT） | ❌ 无（P4 已 KEEP_SEPARATE） |
| CANNOT_DETERMINE | Human 在当前可见证据下也无法确定 | 无 Evidence（记录为 NEED_REVIEW） | ❌ 无（保持 P4 默认） |

### 5.3 CANNOT_DETERMINE ≠ 系统失败

CANNOT_DETERMINE 表示：

> "在当前 Human 可见证据下，也不足以确定 boundary。"

这不是错误，而是**真实的认知不确定性**。可能的原因：
- 页面上下文不足（图片分辨率、裁剪范围）
- 文本本身存在歧义（模糊的边界 case）
- Human 需要更多信息（如更多页面上下文、文档全文）

CANNOT_DETERMINE 的价值：
- 标记"即使 Human 也无法解决的 case" → 这些是**永久 Human-owned Boundary** 的候选
- 提供系统改进信号（哪些 case 需要 new information source）

### 5.4 Human Decision ≠ Machine Rule

**禁止**将单个 Human decision 直接转换为 machine rule：

```
❌ 禁止路径：
Human MERGE on "1"→"Introduction"
→ "gap 10pt should merge"
→ P4 threshold = 12pt
→ 自动 merge all gap≤12pt pairs
```

**正确的路径**：

```
✅ 正确路径：
Human Decisions (multiple, independent)
→ Evidence aggregation (pattern across cases)
→ Generalization test (cross-document)
→ Independent validation (second reviewer)
→ only then candidate machine boundary
→ Gate review
→ if passed: candidate machine boundary
→ if not passed: KEEP HUMAN BOUNDARY
```

### 5.5 Boundary Evidence 的不可逆性

| 属性 | 约束 |
|---|---|
| Human Decision | immutable (ValidationRecord) |
| Boundary Evidence | immutable (ValidatedEvidence, derived from ACCEPT) |
| Evidence → Machine Rule | ❌ 不可自动转换（需 Gate 审查） |
| Machine Rule → Evidence 回写 | ❌ 禁止（Evidence 是 derived layer） |

---

## 六、Human-on-the-Boundary Architecture

### 6.1 Human 的角色重新定义

| 旧定义 | 新定义 |
|---|---|
| "人工处理 ambiguity 的人" | "产生 Boundary Evidence 的 Evidence Source" |
| 目标：处理所有 AMBIGUOUS case | 目标：为系统提供 boundary 判断证据，帮助系统学习哪些边界可以机器化 |
| 终点：所有 case 处理完 | 终点：积累足够证据，判断每个 ambiguity mode 的 machine-resolvability |

### 6.2 架构原则

1. **Human 不替 P4 调 threshold**——Human 判断的是语义关系，不是几何参数
2. **Human 不修改 span**——Span 是 P4 的 immutable 输出
3. **Human 产生 Evidence**——Human decision → ValidationRecord → ValidatedEvidence
4. **Evidence 不自动成为 rule**——需经过 Generalization Gate
5. **Human workload 由 uncertainty 驱动**——不是 document volume 驱动

### 6.3 三层 Authority 分配

| Layer | Machine Authority | Human Authority | Evidence Authority |
|---|---|---|---|
| Layer 1 (Geometric) | ✅ P4 (DETERMINISTIC) | ❌ (AMBIGUOUS 不在此层解决) | ❌ |
| Layer 2 (Semantic) | ❌ (P4 禁止文本分析) | ✅ (Human via P7.2) | ✅ (from ACCEPT) |
| Layer 3 (Structure) | ✅ P7.1 (PROPOSE) | ✅ (Human validates) | ✅ (from ACCEPT) |

---

## 七、Boundary Shrinkage

### 7.1 核心概念

```
BOUNDARY_SHRINKAGE
```

**定义**：随着 Human Evidence 积累，某些 ambiguity 类型从"需要 Human 判断"逐渐变为"机器可以确定性判断"的过程。

### 7.2 相关指标

| 指标 | 定义 | 用途 |
|---|---|---|
| Human Review Rate | 需 Human 审查的 case 数 / 总 AMBIGUOUS case 数 | 衡量当前 Human 负担 |
| Boundary Resolution Rate | Human 做出确定性判断（MERGE/KEEP_SEPARATE）的 case 数 / 总 Human case 数 | 衡量 Human 能力 |
| Boundary Persistence Rate | 上一轮 AMBIGUOUS 中本轮仍 AMBIGUOUS 的比例 | 衡量 shrinkage 速度 |
| Boundary Regression Rate | 上一轮 DETERMINISTIC 中本轮变为 AMBIGUOUS 的比例 | 衡量稳定性 |
| Boundary Expansion Rate | 新文档/新版式产生的新 AMBIGUOUS 类型比例 | 衡量新 ambiguity 来源 |

### 7.3 Shrinkage 路径

```
AMBIGUOUS (needs Human)
    ↓
Human Evidence accumulation (multiple independent cases)
    ↓
Pattern analysis (consistent Human decisions across documents)
    ↓
Generalization test (can machine replicate Human judgment?)
    ↓
┌───────────────────┬───────────────────┐
│                   │                   │
Machine-resolvable │  Human-owned      │
Boundary            │  Boundary         │
(shrinkage occurred)│ (permanent)       │
                    │                   │
└───────────────────┴───────────────────┘
```

### 7.4 Shrinkage 的条件

某一类 ambiguity 可以 shrink（变为 machine-resolvable）的条件：
1. **充分独立案例**：足够多的独立 Human decision（≥20 per mode）
2. **跨文档一致**：Human decision 在不同文档上一致
3. **可识别的几何特征**：存在稳定的几何特征组合能复现 Human judgment
4. **低 false-positive**：机器复现的 false-positive rate < 5%
5. **对抗性鲁棒**：在 adversarial case 上正确

**不满足以上条件 → KEEP HUMAN BOUNDARY。**

### 7.5 不要求所有 Human case 最终都被机器自动化

某些 ambiguity 可能**永久 Human-owned**：

| 类型 | 是否可能 shrink? | 理由 |
|---|---|---|
| TOC_SECTION_NUMBER_TITLE | ⚠️ 可能 | 如果找到稳定的几何 guard（如 number pattern + w_b≥25 + line_obs≤10），可能 shrink |
| FORMULA_FRAGMENT_WIDE | ⚠️ 部分可能 | line_obs>15 的公式行已 DETERMINISTIC_BLOCK；line_obs≤15 的需要视觉上下文 |
| APPENDIX_LETTER_TITLE | ⚠️ 可能 | 与 TOC_SECTION_NUMBER_TITLE 类似 |
| BODY_TEXT_CONTINUATION | ❌ 永久 Human-owned | 需要句法分析，P4 契约禁止 |

---

## 八、Human Workload Growth Risk

### 8.1 风险

```
Document volume ↑
→ ambiguous cases ↑
→ Human workload ↑
→ system becomes human-dependent
```

如果 Human Review Rate 与 document volume 成线性关系，系统将不可扩展。

### 8.2 不会无限增长的架构原则

**原则：Human workload 不应仅仅因为 corpus size 增长而线性增长。**

实现方式：

| 策略 | 说明 |
|---|---|
| Boundary Shrinkage | 已验证的 ambiguity 类型从 Human 移到 machine |
| Document-type capability | 同类型文档的 AMBIGUOUS pattern 一致 → 验证一次，后续同类文档自动处理 |
| AMBIGUOUS 去重 | 相同 ambiguity pattern（同 gap/w_b/line_obs/mode）只 review 一次 |
| Human-owned Boundary 隔离 | 永久 Human-owned 的 ambiguity 类型固定化，不随文档增长 |

### 8.3 四类 Ambiguity 的处理策略

| 类型 | 处理策略 | Workload 趋势 |
|---|---|---|
| 已验证可 machine-resolve | shrink 到 machine | → 0（一次性验证成本） |
| 永久 Human-owned | 固化为 Human Boundary | → 常量（每文档少量 case） |
| 可通过 new information source 消除 | 引入新 feature（如句法分析）→ 从 AMBIGUOUS 移除 | → 0（开发成本一次性） |
| 不可消除 ambiguity | 接受为系统 limitation | → 常量 |

### 8.4 Workload Growth 公式（概念性）

```
Human Workload(N) = Σ(mode_i) × (new_document_types + unverified_ambiguity_count)

where:
  N = corpus size
  mode_i = each ambiguity mode
  new_document_types = 新文档类型数（有限，收敛）
  unverified_ambiguity_count = 未 shrink 的 ambiguity 数（递减）
```

随着 shrinkage 和 document-type capability 积累，Human Workload 趋向常量，而非线性增长。

---

## 九、Machine Boundary Promotion Gate

### 9.1 Gate 设计

一个 Human case 不能因为"Human 做对了"就成为 machine rule。需要经过以下 Gate：

| Gate | 条件 | 说明 |
|---|---|---|
| G1 — Sufficient independent cases | ≥ 20 independent Human decisions per ambiguity mode | 统计显著性最低要求 |
| G2 — Cross-document generalization | Human decision 在 ≥ 3 个不同文档上一致 | 跨文档迁移性 |
| G3 — Low false-positive rate | 机器复现的 FP rate < 5% | 安全性 |
| G4 — Stable feature relationship | 存在稳定的几何特征组合能复现 Human judgment | 可机器化 |
| G5 — Adversarial robustness | 在已知 adversarial case 上正确 | 鲁棒性 |
| G6 — Independent human agreement | ≥ 2 reviewer，agreement ≥ 80% | 可重复性 |
| G7 — No known semantic counterexample | 没有已知的语义反例 | 完备性 |
| G8 — Regression pass | 在全部已有文档上不产生 regression | 不破坏现有 |
| G9 — Authority / provenance preserved | Evidence chain 完整，authority 清晰 | 可审计 |

### 9.2 Gate 不通过的处理

如果 Gate 不通过：

```
KEEP HUMAN BOUNDARY
```

不继续硬编码。不调 threshold。不增加 heuristic。

### 9.3 当前 Round 1 的 Gate 状态

| Gate | 状态 | 说明 |
|---|---|---|
| G1 | ❌ 不满足 | TOC_NUM_TITLE=12, FORMULA_WIDE=6, APPENDIX=1, BODY_CONT=1 — 均不足 20 |
| G2 | ⚠️ 部分 | TOC_NUM_TITLE 跨 3 文档；FORMULA_WIDE 仅 arxiv_2307；BODY_CONT 仅 1 |
| G3 | ❌ 未测试 | 机器复现未执行（P4 v3 不实施） |
| G4 | ⚠️ 部分 | P4 v3 design 识别了候选特征，但 irreducible FP 存在 |
| G5 | ✅ 满足 | AMB-018, AMB-040 adversarial 正确 |
| G6 | ❌ 不满足 | 单 reviewer，无 inter-reviewer agreement |
| G7 | ❌ 不满足 | AMB-026 是已知 semantic counterexample（GT dispute） |
| G8 | ❌ 未测试 | 无 regression test |
| G9 | ✅ 满足 | Provenance chain 完整 |

**结论：9 个 Gate 中 2 个满足，3 个部分满足，4 个不满足。当前不允许任何 Machine Boundary Promotion。**

---

## 十、Human-owned Boundary

### 10.1 定义

```
Human-owned Boundary
```

**定义**：某类 boundary 判断**永久需要 Human authority**，因为其信息需求超出机器当前和可预见的信息空间。

### 10.2 候选 Human-owned Boundary

| Boundary 类型 | Human-owned? | 理由 |
|---|---|---|
| BODY_TEXT_CONTINUATION (sentence boundary) | ✅ 很可能永久 Human-owned | 需要句法分析，P4 契约禁止；P7.1 不做句法 |
| FORMULA vs HEADING (visual context, line_obs≤15) | ⚠️ 可能 Human-owned | 需要页面级视觉模式识别，P4 几何特征不足 |
| TOC_SECTION_NUMBER_TITLE | ❌ 可能 machine-resolvable | 几何特征 + text pattern 可能可组合（需 Gate 验证） |

### 10.3 Human-owned Boundary 的管理

| 原则 | 说明 |
|---|---|
| 固定化 | 每个文档的 Human-owned Boundary 数量固定，不随文档增长 |
| 去重 | 相同 pattern 的 Human-owned Boundary 只 review 一次 |
| Capability 隔离 | Human-owned Boundary 不影响 DETERMINISTIC case 的自动处理 |
| Evidence 保留 | Human decision 产生 Evidence，可用于未来 Generalization 测试 |

---

## 十一、Round 1 的 Open Questions

| # | 问题 | 当前状态 | 需要什么 |
|---|---|---|---|
| 1 | TOC_NUM_TITLE 能否 shrink? | P4 v3 design 有候选特征，但有 irreducible FP | 更多独立 case + inter-reviewer agreement |
| 2 | FORMULA_WIDE (line_obs≤15) 能否 shrink? | 不确定——需要视觉上下文 | 新 information source（如 page region type） |
| 3 | BODY_CONT 是否永久 Human-owned? | 很可能——需要句法分析 | 确认 P4 契约不会扩展到句法分析 |
| 4 | Human Cost 是否可接受? | INVALID（duration broken） | Timer fix + 重新测量 |
| 5 | Inter-reviewer agreement? | NOT MEASURED | 第二 reviewer |
| 6 | 剩余 23 AMBIGUOUS case 的表现? | 未测试 | 扩大 sample（但 NOT AUTHORIZED now） |
| 7 | 设备手册是否真的零 AMBIGUOUS? | 5 个文档 AMBIGUOUS=0 | 更多设备手册验证 |
| 8 | GT ontology 是否需要重新定义? | AMB-026 暴露 mismatch | 语义专家标注（非几何 GT） |

---

## 十二、Authorization Status

```
Round 1 Experiment:     FROZEN
Human Boundary Semantics: DESIGN READY (READ-ONLY)

Human-on-the-Boundary:
  PROMISING / EMPIRICALLY SUPPORTED FOR INITIAL FEASIBILITY
  NOT GENERALIZED
  NOT FULLY VALIDATED
  NOT COST-VALIDATED

Machine Boundary Promotion Gate:
  NOT PASSED (2/9 gates satisfied)
  → No Human Decision may be converted to machine rule

Implementation:         NOT AUTHORIZED
P7.3:                   NOT AUTHORIZED
P4 v3:                  NOT AUTHORIZED (suspended)
Timer Fix:              NOT AUTHORIZED (design only)
GT Modification:        NOT AUTHORIZED (GT_DISPUTED preserved)
Sample Expansion:       NOT AUTHORIZED
Frozen Baseline:        INTACT
```

---

## 十三、核心结论

### Human 的价值不是"替 P4 调 threshold"

Human 的价值是**提供当前机器信息源无法提供的 boundary evidence**：

| Human 提供的信息 | 机器是否有? | 属于哪层? |
|---|---|---|
| 文本内容可读性（"Introduction" 是词 vs "ψ" 是符号） | ❌ P4 禁止文本分析 | Layer 2 |
| 句法结构（句号 = 句子结束，大写 = 新句开始） | ❌ P4/P7.1 不做句法 | Layer 2 |
| 页面级视觉模式（TOC 页 vs 公式页的布局差异） | ⚠️ P6 region 部分可做 | Layer 3 |
| 编号模式识别（"1", "2.1", "B.1" 是编号） | ❌ 需要文本 pattern 分析 | Layer 2+3 |

### Human Decision 不是 Machine Rule

Human 正确判断 20 个 case ≠ "这些 case 可以自动 machine-merge"。

从 Human Decision 到 Machine Rule 需要：
1. Evidence aggregation（多独立 case 的 pattern）
2. Generalization test（跨文档验证）
3. Gate review（9 个 Gate 全通过）
4. 当前 0 个 ambiguity mode 通过 Gate

### Human Workload 不会无限增长

通过 Boundary Shrinkage + Document-type capability + Human-owned Boundary 固定化，Human workload 趋向常量。

### AMB-026 的价值

AMB-026 不是"实验失败"——它是**最有价值的发现**。它证明了：
1. Geometry-based GT 在 body text 场景下有结构性局限
2. 某些 boundary 判断需要纯语义信息（句法分析）
3. 这些 boundary 是 Human-owned 的候选

---

## STOP

```
DESIGN STATUS = READY (READ-ONLY design, not implementation)

Human-on-the-Boundary:
  PROMISING / EMPIRICALLY SUPPORTED FOR INITIAL FEASIBILITY
  NOT GENERALIZED / NOT FULLY VALIDATED / NOT COST-VALIDATED

Implementation = NOT AUTHORIZED
P7.3 = NOT AUTHORIZED
Frozen = INTACT
```

**不进入下一阶段。不修改任何代码。不修改任何实验数据。等待下一步批准。**
