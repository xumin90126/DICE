# Phase 3 Closure — Sampling Strategy Diagnostic

> **READ-ONLY 诊断。** 不重新抽样、不增加 PDF、不改变 n=54、不改变 G-C1 ≥15 门槛、
> 不修改 caption regex / OBS-A/B/C/D / 任何 threshold、不提高 figure-context prevalence、
> 不收集 GT、不运行评估、不修改任何 Frozen 文件。
>
> 事实基线 (不得重新解释): Phase 3 = BLOCKED @ G-C1 FAIL (3/54 < 15); G-C2/G-C3 = PASS;
> 无 GT、无 Baseline B vs C、无 IS-14 evaluation result → **IS-14 不能标记 FAILED,
> 只能保持 HYPOTHESIS ONLY**。
>
> 证据标签: **OBSERVED** (本次测量/既有冻结 artifact) / **INFERRED** (由 OBSERVED 推导) /
> **HYPOTHESIS** / **NOT ESTABLISHED**。机器指标见 `tmp/phase3_sampling_strategy_metrics.json`。

---

## 1. 诊断问题

> G-C1 FAIL 到底说明当前实验 corpus 中 GRAPHIC_TEXT_CONTEXT 本身稀疏 (H1),
> 还是说明 sampling frame 与 IS-14 的研究对象不匹配 (H2),
> 还是说明研究对象在 candidate generation 阶段已被结构性排除 (H3)?

数据基线 (全部 OBSERVED, 来自冻结 artifact `phase3_is14_candidate_universe.json` +
本次只读全文扫描, 24.9s, page-cache 确定性):

| 基线量 | 值 |
|--------|-----|
| Universe AMBIGUOUS candidates | 1299 |
| 其中 table domain (IS-11 as-run 域判定) | 759 (58.4%) |
| 非表格 AMBIGUOUS | 540 |
| figure-context (域门控后: OBS-A ∨ caption-block ∨ OBS-C 双命中) | **79** |
| prevalence (universe) | **6.08%** |
| prevalence (非表格子集) | 14.63% |
| 冻结样本 (n=54) 中 figure-context | 3 |

---

## 2. H1 — Genuine Sparsity

**结论: 部分成立 (OBSERVED), 且高度集中。**

| 检查项 | 结果 (OBSERVED) |
|--------|----------------|
| 全部 1299 candidates 扫描 | 759 table domain / 540 非表格 |
| figure-context 可观察候选 (域门控) | **79** (tick 60, caption-block 16, OBS-A 3) |
| prevalence | 6.08% (universe) / 14.63% (非表格) |
| 按 document 分布 | **GraphCast 76 (96.2%) / ASTRO-001 3 / EHT·CAGI·MRI 0** |
| 按 page 分布 | 仅 14 页; top-3 页 (GraphCast p50/p36/p82) 占 74.7% |
| caption / tick 分布 | tick 为主 (60); caption 类 19 (16 域门控后) |
| 是否集中于少数 PDF | **是** — 单文档 96.2%, top-3 页 3/4 |
| 是否由 P4 几何合并吸收 | 见 H3 (是, caption 类尤其严重) |

判读 [INFERRED]: 在**当前 corpus 的版式构成**下, GRAPHIC_TEXT_CONTEXT 在 AMBIGUOUS
universe 中确实是低 prevalence 现象, 且非均匀 — 由单一文档的坐标轴标签版式主导。
但 "低 prevalence" 很大程度是**产物**而非**原因** (见 H3)。

---

## 3. H2 — Sampling Frame Mismatch

**结论: 不成立为主要原因 (OBSERVED 否证)。**

| 检查项 | 结果 |
|--------|------|
| 盲抽样保真度 | universe prevalence 6.08% × 54 = 期望 3.3; 实际 3; **保真比 0.91** (OBSERVED) |
| strata 是否额外稀释 | 否 — 几何盲抽样按 universe 比例命中; gap-bin 表示率: g2(12-20pt) 11.4%, g1 2.6%, g3 8.5%, g4 0.5% (OBSERVED); 抽样忠实反映 universe 构成 |
| AMBIGUOUS universe 天然偏向 | 是 (OBSERVED): table domain 58.4% + 正文邻接为主 — 但这是 universe 的构成问题 (H3/语料版式), 不是抽样规则问题 |
| targeted sampling frame 是否必要 | 见 §5 Route B — **机械上可行, 科学上不足以产生有效 G-D1 检验** (INFERRED) |

判读 [INFERRED]: 抽样没有额外稀释 — 它忠实地代表了一个本身就缺乏研究对象的 frame。
把原因归给 sampling frame 会导向错误修复 (targeted frame), 而 targeted frame 在本 corpus 上
**必须**接受 ≥80% 单文档 positive 才能凑满 15 (见 §5) — 修标不修本。

---

## 4. H3 — Research-object Mismatch

**结论: 强烈成立 (OBSERVED) — 这是主因。**

IS-14 的研究对象是 "非表格 graphic textual context"。测量该对象在 candidate generation
阶段的命运 (96 个 caption 页 + 全部数值行, 只读扫描):

### 4.1 Caption 类: 被 P4 几何合并结构性吸收

| caption 上下文相邻 pair 的 gap 分布 | 数量 | 占比 |
|-----------------------------------|------|------|
| gap ≤ 8pt → **P4 DETERMINISTIC_MERGE 吸收, 永不进入 AMBIGUOUS universe** | **1499** | **93.7%** |
| gap 8-50pt → AMBIGUOUS-eligible | 91 | 5.7% |
| gap > 50pt | 8 | 0.5% |

→ **约 94% 的 caption 上下文相邻 pair 在进入 AMBIGUOUS universe 之前就被冻结 P4 规则合并掉。**
这不是 IS-14 observer failure, 是 **research object 与 frozen candidate universe 之间的
representation mismatch** (任务 §二 H3 预期的情形, 明确成立)。

### 4.2 Tick 类: 进入 universe 但被冻结 OBS-C 定义排除

| 数值行相邻 pair (1326 个候选均匀行) | 数量 |
|-----------------------------------|------|
| overlap / 已合并 (P4) | 4245 |
| gap ≤ 8pt | 60 |
| gap 8-50pt (AMBIGUOUS-eligible) | 1885 |
| gap > 50pt | 1781 |
| eligible 中通过冻结 center-CV ≤ 0.15 | **仅 129 (6.8%)** |
| (仅诊断, 不调参): edge-gap CV ≤ 0.15 | 117 |

→ 数字轴标签大量进入 AMBIGUOUS universe (1885 对), 但**变宽数字** (如 '100/200/1000')
使中心距 CV 天然超过冻结的 0.15 — 冻结 OBS-C 定义与真实轴标签几何存在结构性错配。
edge-gap 诊断仅记录, **未也绝不**据此调参 (Phase 3 §28)。

### 4.3 Raster 图: 文本根本不存在

LIGO/EHT 图为 raster (80/37 image blocks): tick/标签文字在图像内, 无 text span →
该类图形上下文对任何文本 observer 不可见 (OBSERVED; G-C3 披露的延伸)。

### 4.4 判定

[INFERRED] H3 成立: 研究对象 (graphic textual context) 在 frozen candidate universe 中的
**表示率** ≈ 6% (universe) — 由 (a) P4 合并吸收 caption 类 93.7%, (b) OBS-C 中心距定义
排除 93% eligible 数值对, (c) raster 图零文本 三个机制共同造成。
**这不是 observer bug, 也不是假设被证伪, 而是研究对象与冻结候选表示之间的错配。**

---

## 5. 三假设对比结论与 Route 分析 (§三/§四)

### 5.1 严禁 "提高 prevalence" 作为目标

本诊断不产生任何 "继续找 figure-heavy PDF 直到 ≥15" 类建议 (结果驱动 sampling, 禁止)。
Route B 类 targeted frame 仅在满足完整预注册要件时才可提出 (见下)。

### 5.2 Route 量化 (维持自然随机抽样, §四第一问)

| 问题 | 回答 |
|------|------|
| 获得 ≥15 figure-context 需要多少 candidates? | 15 / 6.08% ≈ **247** (INFERRED; 为 n=54 的 4.6×) |
| 当前 prevalence 是否使成本不合理? | **是** — 5× 人工评审成本, 且集中度不变 (96% 单文档), top-3 页占 3/4 → 有效样本量远低于名义 n |
| 继续扩大普通随机 corpus 是否有科学价值? | **低** — 新增信息主要为同一 GraphCast 版式的重复; 跨文档泛化性不会改善 |

### 5.3 Route B (pre-registered targeted sampling) 可行性检验

| 要件 | 本 corpus 上的事实 |
|------|-------------------|
| positives 可用量 | 79 (够 15) — G-C1 字面上可满足 |
| 单文档占比 | 96.2% (76/79 GraphCast) |
| 防单文档主导的 per-doc cap | 需 cap=12 才能凑满 15 → **单文档占比 ≥80% 是下限** (INFERRED) |
| G-D1 (跨文档 ≥2) 可检验性 | 结构性薄弱: 第二文档最多 3 个 positive (n=3, 统计上不可靠) |
| 结论 [INFERRED] | targeted frame 只能产生 "GraphCast 版式专用" 的评估; 无法区分 IS-14 价值与 corpus artifact。**在冻结 OBS-C 定义不变的前提下, 本 corpus 不存在科学有效的 targeted frame。** |

(预注册要件清单 — 若未来 corpus 支持此路线: inclusion/exclusion criteria、frame、
deterministic selection rule、independent controls、独立文档、防污染、先注册后执行 — 全部记录,
本诊断不提出具体 frame, 因证据表明该路线当前无效。)

---

## 6. Route 决策矩阵 (§四 — 不提前选择, 按证据评分)

| 评价维度 | Route A 自然抽样 | Route B targeted frame | Route C DEFER | Route D 研究对象重设计 |
|----------|----------------|----------------------|---------------|----------------------|
| scientific validity | 低 (5× 成本换同类集中样本) | 低-中 (G-C1 字面过, G-D1 n=3 脆弱) | — (不作声称) | **高** (修因) |
| selection bias risk | 无 | 受预注册约束但 frame-conditional | 无 | 无 (表示层实验性变更 + promotion gates) |
| implementation cost | 中-高 (~247 例评审) | 低-中 (54 例评审) | **零** | 高 (设计 + 新观测层) |
| corpus cost | 高 (新 PDF) | **零** (复用) | 零 | 零/中 (现有 corpus 可复用) |
| expected information gain | 低 | 低-中 (仅 tick 子集; caption 类仍不可见) | 零 | **高** (解锁整个图形上下文类) |
| generalizability | 差 (单文档 96%) | 差 (≥80% 单文档) | — | **潜在高** (roadmap 阶段 5-6 promotion gates 把关) |
| frozen impact | 无 | 无 | 无 | **无** (若走实验性 Atomic Observation / Experimental Span 层; 任何冻结影响须经显式 unfreeze) |
| G-S1~G-S5 可检验性 | 可 | 可 | 不可 | 可 (重设计后) |
| 区分 IS-14 价值 vs corpus artifact 的能力 | 差 | **差** | — | **好** |

**矩阵结论 [INFERRED]**: A 与 B 在本 corpus 上均无法产生跨文档有效的 IS-14 评估;
C 是零成本止损; D 是唯一同时 (a) 针对主因 (H3 表示错配), (b) 不触碰 Frozen Baseline
(走实验性表示层), (c) 保留 IS-14 假设可检验性的路线。

---

## 7. Human Feedback → Machine Improvement 边界 (§五)

| 链环 | 状态 | 证据标签 |
|------|------|---------|
| Human Feedback (45-case rationales 引用 caption/axis 结构角色) | 完好 | OBSERVED (Phase 1 冻结 artifact) |
| → structural failure pattern (信息缺口: 无 IS 覆盖图形角色, 13/45) | 完好 | OBSERVED |
| → machine-observable hypothesis (IS-14 = GRAPHIC_TEXT_CONTEXT, Phase 2 冻结定义) | 完好 | OBSERVED |
| → controlled experiment (Phase 3) | **实例化失败于 pre-condition** | OBSERVED |
| → evidence-based decision | **无评估证据** — BLOCK ≠ 证伪 | OBSERVED |

**判定**: G-C1 BLOCK 的含义是 —

> **"已有反馈提出了合理 hypothesis, 但当前实验的候选表示 (candidate universe) 无法有效呈现
> 其研究对象, 因而无法有效测试它"** — 而 **不是** "human feedback 没有价值"。

二者不得混淆 [OBSERVED 边界 + INFERRED 判读]。LOOP_SUPPORTED 判定不受影响
(其证据 = IS-11 n=1 已完成的完整闭环, 与 IS-14 无关)。

**对闭环描述的一个精细化贡献** [INFERRED, 供未来 design 参考]:
在 "machine-observable hypothesis" 与 "controlled experiment" 之间应显式插入
**representation feasibility check** (研究对象在冻结候选表示中的可呈现率 ≥ 门槛) —
本次 BLOCK 的教训正是该检查此前不存在 (MAP GAP 的实质内容之一)。

---

## 8. FINAL DECISION GATE (§六)

### DIAGNOSTIC STATUS

```text
╔══════════════════════════════════════════════════════════════╗
║  DIAGNOSTIC STATUS = MIXED_CAUSE                             ║
║                                                              ║
║  H1 Genuine Sparsity        = 部分成立 (6.08% + 96% 单文档集中) ║
║  H2 Sampling Frame Mismatch = 否证 (抽样保真比 0.91)           ║
║  H3 Research-Object Mismatch = 成立 (主因:                     ║
║      caption 93.7% 被 P4 吸收; eligible 数值对 93% 被冻结       ║
║      OBS-C 中心距定义排除; raster 图零文本)                     ║
╚══════════════════════════════════════════════════════════════╝
```

(低 prevalence 是 H3 机制在当前 corpus 版式构成下的**产物**; 故为 MIXED 而非单一 H1。)

### NEXT MAP ACTION

```text
╔══════════════════════════════════════════════════════════════╗
║  NEXT MAP ACTION = DESIGN_RESEARCH_OBJECT                    ║
║  (DESIGN ONLY — 不实施)                                       ║
╚══════════════════════════════════════════════════════════════╝
```

依据: 主因为 H3 (表示错配); 修复表示的**唯一 MAP 内路径已存在** —
Perception Development Roadmap **阶段 1 (Atomic Observation Layer) / 阶段 2
(Experimental Span Construction)**, 其设计目标正是 "不依赖 CandidateSpan 的原子观测 +
实验性 span 构建", 天然适配 "caption/tick 邻接对在 P4 合并前作为独立观测保留" 的需求,
且全程不触碰 Frozen Baseline (任何晋升走阶段 5-6 promotion/unfreeze gates)。

**设计范围约束 (若获授权)**: 只产出设计文档 (research-object 定义 + representation
feasibility gate 预注册 + 与 IS-14 OBS-A/B/C 的衔接), 不写实现代码, 不改 Frozen,
不生成 GT, 不运行评估。若未获授权 → 默认状态为 **DEFER_IS14** (零成本, 假设保留在册)。

**本诊断明确排除的选项**: REDESIGN_SAMPLING_FRAME (针对被否证的 H2; 且本 corpus 上
任何 targeted frame 均无法避免 ≥80% 单文档 positive)、COLLECT_MORE_EVIDENCE
(诊断证据已充分)、NO_FURTHER_ACTION (与可行动的明确根因不符)。

---

## 9. Governance Boundary 确认 (§七)

```text
本次诊断全程 READ-ONLY:
  ✅ 未修改 P1-P6 / P4 SpanConfig / CandidateSpan / DocumentSpan
  ✅ 未修改 IS-01 / IS-02 / table_line_detector / P7.1 / P7.2 / GT
  ✅ 未修改 Capability Registry / Runtime / Runtime Authority / P7.3
  ✅ 未 re-sampling / 未 corpus substitution / 未 GT collection / 未 evaluation
  ✅ 未 threshold / regex / observer tuning
  ✅ 未 production / capability registration / runtime integration
  已发生动作 = repository 只读检索 + 既有 artifact 分析 + 统计 prevalence 分析
              + MAP positioning + sampling strategy 诊断 + 假设对比 + decision gate 设计
```

回归核验: Frozen Baseline = INTACT (Phase 3 已独立 SHA 验证, P7.1/P7.2 drift=0,
GT/Stage4/TLD/P4 哈希不变; 本诊断未引入任何新文件修改面)。

---

## 10. 最终状态

```text
PHASE 3 = BLOCKED (维持) | IS-14 = GRAPHIC_TEXT_CONTEXT / HYPOTHESIS ONLY (维持)
IS-14 FAILED = ❌ 不成立 (无评估, 不得标记 FAILED)
DIAGNOSTIC STATUS = MIXED_CAUSE (H1 部分 + H3 主因; H2 否证)
NEXT MAP ACTION = DESIGN_RESEARCH_OBJECT (design only; 未授权前默认 DEFER_IS14)
FROZEN BASELINE = INTACT | P7.3 = NOT AUTHORIZED | PRODUCTION = FALSE
STOP = TRUE | WAIT FOR EXPLICIT AUTHORIZATION
```
