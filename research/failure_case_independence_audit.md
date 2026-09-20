# Failure Case Independence Audit

> 性质: FAILURE ANALYSIS 的独立性/抽样审计 (READ-ONLY)。不实现 perception, 不新增 observation,
> 不修改任何文件 (本文档除外)。上一轮结论 "40/45 = 88.9% 落入重复模式 → 真实文档感知失败高度重复"
> 在本轮被**重新审查**, 不被默认继承。
>
> 证据标签: **OBSERVED** (artifact 统计/只读复现) / **INFERRED** / **NOT ESTABLISHED / NOT COMPUTABLE**。
> 数据源: `tmp/is11_machine_evaluation_results.json` (45 cases) ·
> `tmp/is11_human_review_results.json` (rationales) · `tmp/is11_independent_sampling_frame.json`
> (抽样设计) · `tmp/is11_independent_candidate_universe.json` (universe 545) ·
> `tmp/is11_corpus_acquisition_report.md` (语料元数据)。

---

## 0. 方法与可复现性声明

Phase 1 的 per-case 语义类别映射未在 md 中逐案枚举 (仅发布聚合 26/7/4/3/2/1+2)。本审计按
Phase 1 记录的同一方法 (关键词分类 + adjudication 时取与 final label 一致的 reviewer rationale)
**只读复现** per-case 映射, 并与已发布分布对账:

| 类别 | 已发布 | 本审计复现 | 对账 |
|------|-------|-----------|------|
| TABLE_CELL_COLUMN | 26 | 28 | 发布的 2 例 OTHER 经 Phase 1 人工复核"实仍引用 Dataset/Train-Size 表列"(md §5 原文) — 复现 28 = 26 + 该 2 例 |
| TABLE_HEADER | 7 | 7 | ✅ 一致 |
| PROSE_SENTENCE_PARAGRAPH | 4 | 4 | ✅ |
| FIGURE_AXIS_TICK | 3 | 3 | ✅ |
| FIGURE_CAPTION | 2 | 2 | ✅ |
| DIAGRAM_LIST_ITEM | 1 | 1 | ✅ |
| OTHER | 2 | 0 | 一致 (被 Phase 1 人工归入表列) |

→ 映射可信, 用于独立性计算。涉及 26 的口径处**同时给出 26 (strict) 与 28 (replicated)**。

---

## A. Corpus Independence Audit

### A.1 Pool 级 (45 cases)

| 指标 | 值 |
|------|-----|
| total unique documents | **4** (resnet 9, efficientnet 18, med_001 8, cs_001 10) |
| total unique (document, page) | **18** |
| cases per page | max **8** (cs_001 p3), median 2.0; 分布: 8×1, 5×2, 4×1, 3×2, 2×5, 1×7 |
| **同一页 ≥3 cases 的页面** | 6 页 (cs_001p3=8, efficientnet p6=5, p7=5, p8=4, resnet p6=3, med_001 p19=3) — 同页多案例通常来自**同一表格/同一版式机制**, 相互强相关 |
| document HHI (unit=case, denom=45) | **0.281** → 有效文档数 1/HHI = **3.56** (名义 4) |
| FAMILY / template | **FAMILY = UNKNOWN** — 元数据只有 arxiv id 与主题域 (CS/Chemistry), 无 publisher-template 字段; 按 §B 纪律不从文件名/主题/视觉推断 |

### A.2 抽样权重检查 (case-level 过度加权?)

抽样设计 [OBSERVED]: 几何分层随机抽样 (seed 20240909), n=45, min_per_doc=8, universe=545。

| document | universe share | sample share | ratio | 判定 |
|----------|---------------|--------------|-------|------|
| is11_resnet | 118/545 = 0.217 | 9/45 = 0.200 | 0.92 | ≈ 比例 |
| is11_efficientnet | 253/545 = 0.464 | 18/45 = 0.400 | 0.86 | ≈ 比例 (略欠) |
| is11_med_001 | 52/545 = 0.095 | 8/45 = 0.178 | **1.86** | **过度加权 (min_per_doc 地板效应)** |
| is11_cs_001 | 122/545 = 0.224 | 10/45 = 0.222 | 0.99 | ≈ 比例 |

→ 抽样总体忠实于 universe 构成; 唯 med_001 被 min_per_doc 地板抬升 1.86× (影响 n=8 中约
3.7 例的期望份额)。**med_001 单文档集中的模式 (AXIS_TICK/CAPTION/DIAGRAM) 的频率解释必须
考虑此加权。** [OBSERVED]

### A.3 Per-pattern independence (核心表)

| Pattern | n (strict/replicated) | unique docs | unique pages | max/page | top1 doc (share) | top3 share | HHI (unit=case) | 有效文档数 |
|---------|----------------------|-------------|--------------|----------|------------------|-----------|-----------------|-----------|
| TABLE_CELL_COLUMN | 26 / 28 | **3** (of 4) | **10** | **5** | efficientnet 16 (57%/16·28) | 100% (仅 3 docs) | **0.421** | 2.37 |
| TABLE_HEADER | 7 | **3** (of 4) | 6 | 2 | cs_001 4 (57%) | 100% | 0.429 | 2.33 |
| PROSE_SENTENCE_PARAGRAPH | 4 | 3 (of 4) | 4 | 1 | med_001 2 (50%) | 100% | 0.375 | 2.67 |
| FIGURE_AXIS_TICK | 3 | **1** | **1** | 3 | med_001 3 (100%) | — | 1.000 | 1.00 |
| FIGURE_CAPTION | 2 | **1** | 2 | 1 | med_001 2 (100%) | — | 1.000 | 1.00 |
| DIAGRAM_LIST_ITEM | 1 | 1 | 1 | 1 | med_001 | — | 1.000 | 1.00 |

### A.4 TABLE_CELL_COLUMN = 26 专项回答 (§A 强制)

- **unique documents = 3 / 4** (resnet 7, efficientnet 16, cs_001 5; med_001 0)
- **unique pages = 10**; max 5 cases/页 (efficientnet p6 与 p7 各 5, cs_001 p3 5 —
  同一表格同一版式机制在同一页重复产生多个 candidate case)
- **family/template 集中?** FAMILY = UNKNOWN → **NOT COMPUTABLE**
- 结论口径: 26 ≠ 26 个独立失败; 独立失败设置 ≈ **10 个 (doc,page) 设置** (若同页同表视为一个机制实例);
  其中 3 页各贡献 5 例。document 基础 = 3 (pool 只有 4 docs, 无更多可采样)。

### A.5 其他模式专项

- **Caption (2)**: 1 doc × 2 pages (med_001 p20/p24) — 单文档。与 Phase 3 独立证据
  (prevalence 6.08%, 96.2% 集中于 GraphCast 单文档) **相互一致**: caption 关联失败在两个
  独立观测中均呈单文档集中 → 失败真实存在但 corpus 面窄 [OBSERVED×2 源]。
- **Page-header (CC-03)**: 45-case pool 中 **0 例**; 证据全部来自另一独立语料
  (PH3 corpus, incident-2 + 显微镜 p6) — 跨语料存在, 但 45-case 框架内频率 = 0 → 频率
  不可从 GT pool 估计 [NOT YET QUANTIFIED in GT frame]。
- **Column-blind band (CC-04)**: 机制实测于 efficientnet p5 (1 doc) — 单文档机制证据,
  无频率估计 [NOT YET QUANTIFIED]。
- **Role aggregation (CC-05)**: TABLE_HEADER 3 docs/6 pages, AXIS_TICK 1 doc/1 page,
  PROSE 3 docs/4 pages — 分化显著 (见 §E)。

---

## B. Document Family 判定

```text
FAMILY = UNKNOWN (全部 4 个文档)
```

现有 metadata (arxiv id, 主题域, 页数, sha) **不足以**可靠判定 publisher template /
source family。按 §B 纪律: 不从文件名、主题、视觉相似性推断。因此:
- family-level coverage / concentration = **NOT COMPUTABLE**;
- 本审计只报告 document-level 与 page-level 独立性。

---

## C. 两个层级的覆盖率重算 (§C)

Case-level coverage (denominator = 45, 明确):

| Pattern | case coverage |
|---------|---------------|
| TABLE_CELL_COLUMN | 26/45 = 57.8% (strict) / 28/45 = 62.2% (replicated) |
| TABLE_HEADER | 7/45 = 15.6% |
| PROSE | 4/45 = 8.9% |
| AXIS_TICK | 3/45 = 6.7% |
| CAPTION | 2/45 = 4.4% |
| DIAGRAM | 1/45 = 2.2% |

Document-level coverage (denominator = "unique documents in relevant observation frame"
= 45-case 框架的 4 docs, 明确可定义):

| Pattern | doc coverage | 判读 |
|---------|--------------|------|
| TABLE_CELL_COLUMN | 3/4 = 75% | 多文档, 但基数只有 4 |
| TABLE_HEADER | 3/4 = 75% | 同上 |
| PROSE | 3/4 = 75% | n=4 太小 |
| FIGURE_AXIS_TICK | 1/4 = 25% | 单文档 |
| FIGURE_CAPTION | 1/4 = 50% | 单文档 |
| Page-header | 0/4 (GT frame) — 相关框架是 PH3 语料 (5 docs, 1/5 = 20% 文档含该机制证据) | 跨框架, 分母不同已显式声明 |
| FAMILY-level | **NOT COMPUTABLE** | FAMILY = UNKNOWN |

**不使用任何其他更方便的 denominator。**

---

## D. Concentration Analysis (Top Failures)

| Pattern | top1 doc | top3 docs | max/page | median/page* | unique docs | HHI (unit=case) |
|---------|----------|-----------|----------|--------------|-------------|-----------------|
| TABLE_CELL_COLUMN | efficientnet 16 (57%) | 28/28 (100%, 仅 3 docs) | 5 | 2.5 (10 页中位数) | 3 | 0.421 |
| TABLE_HEADER | cs_001 4 (57%) | 7/7 (100%) | 2 | 1.0 (6 页) | 3 | 0.429 |
| FIGURE_AXIS_TICK | med_001 3 (100%) | — | 3 (同一图!) | 3 (1 页) | 1 | 1.000 |
| FIGURE_CAPTION | med_001 2 (100%) | — | 1 | 1 (2 页) | 1 | 1.000 |
| PROSE | med_001 2 (50%) | 4/4 | 1 | 1 (4 页) | 3 | 0.375 |

(*median cases per page among pages that have ≥1 case of the pattern)
HHI 的单位 (case) 与分母 (pattern 内 case 数) 已显式定义, 故报告; family-level HHI =
NOT COMPUTABLE。

**关键读数**: TCC 的 top1 文档贡献 57%, 且 top3 = 100% — 因为 pool 只有 4 docs。
TCC 在 10 个页面设置上出现 (3 docs), 其中 3 页各贡献 5 例 — **同一表格机制在同一页
重复产案是常态**, 案例数 ≠ 独立失败数。

---

## E. 40/45 = 88.9% 的重新分类 (§E)

对上一轮的总体口径 "40/45 落入重复模式 → 真实文档感知失败高度重复", 按模式拆分重判:

| Pattern | 分类 (§E 四选一) | 依据 |
|---------|-----------------|------|
| TABLE_CELL_COLUMN (26/28) | **DOCUMENT-CONCENTRATED** (多页多文档但文档基极小 + 页内强重复) | 3/4 docs, top1 57%, 10 pages, max 5/页, HHI 0.421; FAMILY=UNKNOWN 无法排除 template 效应 |
| TABLE_HEADER (7) | **DOCUMENT-CONCENTRATED** | 3/4 docs, top1 57%, HHI 0.429 |
| PROSE (4) | **INSUFFICIENT EVIDENCE** | n=4, 3 docs/4 pages — 独立性形态最好但样本量不足以判定 |
| FIGURE_AXIS_TICK (3) | **DOCUMENT-CONCENTRATED** (最强) | 1 doc × 1 page (同一张图!) — 完全不独立 |
| FIGURE_CAPTION (2) | **DOCUMENT-CONCENTRATED** | 1 doc × 2 pages; 与 Phase 3 独立证据方向一致但同样单文档集中 |
| Page-header / Column-blind | **INSUFFICIENT EVIDENCE** (GT frame 内 0 例; 机制证据来自另一语料单文档) | 频率不可估 |
| **总体 "88.9%"** | **INSUFFICIENT EVIDENCE (as a cross-document generality claim)** | 4 docs (有效 3.56), FAMILY=UNKNOWN, med_001 过加权 1.86×, 页内重复普遍 |

**修正后的合法陈述** [INFERRED]:
> 失败模式在 **4 文档 / 18 页设置** 的小语料内高度重复, 其中最大模式 (TCC) 达到 3 文档 /
> 10 页设置; 但 **"跨独立文档/跨 template 的普遍性" 在当前证据下不成立 (INSUFFICIENT
> EVIDENCE)** — 文档基数过小、family 未知、med_001 存在抽样加权、页内同表重复普遍。
> 上一轮 "真实文档感知失败高度重复" 的表述应**降格**为 "在同一 4 文档观察框架内重复"。

---

## F. 对 Priority 的影响 (§F — 不实现 PH-02)

| Rank | OLD (failure analysis) | NEW (after independence audit) | WHY |
|------|------------------------|-------------------------------|-----|
| 1 | TABLE_CELL_COLUMN — HIGH | **HIGH → MEDIUM-HIGH (下调)** | 26 cases 实为 3 docs / 10 页设置, top1 doc 57%, 同页同表重复普遍; "corpus-wide 最高频失败" 的说法不成立。但不下调出前列: (a) 3/4 docs 出现 = 机制非单表伪影; (b) 判别结构 (对齐列成员) 已显微镜实测 (CC-02); (c) PH-02 仍是成本最低的可证伪实验。下调的是**影响面声明**, 不是机制可信度。 |
| 2 | Caption 关联 — HIGH | **HIGH → MEDIUM (下调)** | 1 doc × 2 pages (45-case pool) + Phase 3 独立证据同为单文档集中 (96.2% GraphCast)。两个独立观测都指向"失败真实但语料面窄"。作为 perception 问题保留, 作为 corpus 级优先级下调。 |
| 3 | 页眉污染 — HIGH | **HIGH → MEDIUM-HIGH (相对上升)** | 唯一拥有**跨语料**证据的失败 (45-case pool 之外的 PH3 语料: incident-2 30/54 + 显微镜 p6 实测), 且机制 (页顶位置+跨页重复+形态) 与文档无关, 版式模板层面泛化性最合理。频率仍 NOT YET QUANTIFIED — 排序依据是机制泛化性而非 case 数。 |
| 4 | 列盲 band 推理 — MEDIUM | **MEDIUM → MEDIUM (维持)** | 机制单文档实测 (efficientnet p5), 无频率; 与 CC-02 同页同根因, 若做 PH-02 则顺带获得该机制的更多观测。不升不降。 |
| 5 | 跨页连续性 — LOW | **LOW (维持)** | 观察空白, 维持暂缓。 |

**汇总**: 原 Rank 1/2 的依据主要是 case 数量; 审计表明数量被 (a) 4-doc 小基数、(b) 页内同表
重复、(c) med_001 加权放大。修正后的优先序 = **PH-03 (页眉, 跨语料机制) ≈ PH-02 (TCC, 多页
多文档但集中) > PH-01 (caption, 单文档集中)**。PH-02 的实验价值 (GT 重放可证伪、零冻结
影响) 不变 — 变的是其结果可推广范围的预期声明。

---

## G. 审计边界声明

- 本审计只读; 未修改 Frozen Baseline / GT / Atomic Observation Layer / P1-P7 / parser /
  perception / IS-11·IS-14 evaluation; 未实现 PH-01/02/03; 未新增 observation 或 semantic schema。
- per-case 类别映射为只读复现并与发布分布对账 (26↔28 差异 = Phase 1 已人工确认的 2 例
  OTHER 漏检, 全文双口径披露)。
- FAMILY = UNKNOWN; family-level 一切统计 = NOT COMPUTABLE。
- med_001 抽样加权 1.86× 已披露; 涉及其集中模式的频率解释均须打折。

---

## 最终状态

```text
INDEPENDENCE_AUDIT = COMPLETE
FROZEN_BASELINE = INTACT
CODE_MODIFICATION = NONE
PERCEPTION_IMPLEMENTATION = NOT AUTHORIZED
PH-02 = NOT AUTHORIZED
STOP = TRUE
```
