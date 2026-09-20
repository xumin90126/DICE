# Phase 2 — IS-14 Controlled Experiment Design

> **DESIGN ONLY。不实现 IS-14。不修改任何系统文件。不运行评估实验。**
>
> 阶段: Phase 2 — IS-14 Controlled Experiment Design
> 前置: Phase 1 COMPLETE (LOOP_SUPPORTED, 附边界条件)
> 本阶段终点: IS-14 Hypothesis → Experiment Design → **STOP**

---

## 1. Executive Decision

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   FINAL DECISION:  DESIGN_READY                              ║
║   (附 3 项 pre-conditions，见 §20)                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

核心设计结论:

1. **Phase 1 的 4 个候选信息缺口不能合并为一个 IS。** 经逐一分析: TABLE_HEADER 缺口本质是 IS-11 的 detector 覆盖问题 (非新信息维度)；DIAGRAM_LIST_ITEM n=1 证据不足；broad DOCUMENT_STRUCTURE_ROLE 违反单一假设原则。**只有 figure/caption 域的缺口共享一个清晰、机器可观察的抽象。**

2. **最终 IS-14 假设 (从历史 broad 定义收窄)**:
   > **IS-14 = GRAPHIC_TEXT_CONTEXT** — 对不在检测到的表格区域内的 candidate pair，观察其是否处于图注 (caption) 文本单元或坐标轴刻度 (axis tick) 序列的图形文本上下文中。
   - OBS-A caption-label 文本模式 (已在真实语料验证: `FIG. 8/9/12:` 全部命中)
   - OBS-B caption-continuation 块邻接关系
   - OBS-C numeric tick-run 对齐 (已在真实语料验证: ≥5 成员等差数列, 均一字号)
   - OBS-D image-block 邻近 (**仅辅助信号** — 探测证明 vector figure 无 image block)

3. **与 IS-11 的边界按域划分，零重叠**: pair 在检测到的表格区域内 → IS-11 独占；pair 在图形/图注上下文 (非表格) → IS-14 独占；两者都不 → 无 IS-14 观察。

4. **本设计是第一个可能产生正确 MERGE 决策的机制** — 当前系统全部历史 TP=0 (Recall=0.0)，IS-11 与 §9.3 均无 MERGE-方向的结构信息源；IS-14 的 caption 规则直接对应 Phase 1 中全部 2 个 MERGE GT 的信息缺口。

5. **不重复 G7 错误**: Safety (ΔFP≤0, ΔFN≤0) 与 Utility (ΔCoverage>0 + 新增决策正确率) 严格分离；FP-reduction 不预设为 utility 目标。

**DESIGN_READY 的 3 项 pre-conditions** (进入 Phase 3 评估前必须满足，见 §20): G-C1 语料充足性 gate、caption-label 正则冻结、vector-figure 局限披露。

---

## 2. Phase 1 Evidence Reused

全部 READ-ONLY 引用，未重新计算:

| Phase 1 结论 | 本设计如何使用 |
|-------------|--------------|
| LOOP_SUPPORTED (n=1 转换, in-sample) | 闭环结构已验证 → 允许设计第 2 次受控转换；n=1 限制 → 本设计必须独立 corpus + 独立 GT |
| 45/45 决策引用 case-independent 结构概念 | 信息缺口的 taxonomy 来源 |
| 重复模式: TABLE_CELL_COLUMN(26), TABLE_HEADER(7), PROSE(4), FIGURE_AXIS_TICK(3), FIGURE_CAPTION(2), DIAGRAM(1) | §3-§4 逐类分析是否构成新 IS |
| M2 Tier A = 28.9% (现有 IS-11 observer 覆盖) | 表格域缺口的归属判断 |
| 2 个 MERGE GT 均为 figure caption、无任何 IS 覆盖 | IS-14 的 MERGE-方向价值依据 |
| 418 案例 (caption 内句子边界 → KEEP) | caption 语义细分: label+continuation ≠ body+body → 协议设计的关键约束 |
| 人工负担约束: 1-click, 无 reason 字段 | §12 评审设计 |
| FP case (IS11-AMB-135) 属表格域 | 不计入 IS-14 范围 (§8) |

同时引用: Stage 3 冻结 GT + adjudication rationales；Stage 4 sealed artifacts (B/C 决策 + IS-11 观察)；Stage 5 信息源决策；`is11_table_cell_context_experiment_design.md` §3.3 (IS-14 历史定义: DOCUMENT_STRUCTURE_ROLE, "比 IS-11 更广泛但更模糊")。

---

## 3. Information Gap Analysis

### 4.1-4.3 联合表: 逐缺口分析 (Human signal → Existing observable → Missing observable → 候选归属)

| # | Information Gap (Phase 1) | Human 到底告诉了系统什么 (4.1) | Existing Observable (4.2) | Missing Observable (4.3) | 候选归属 |
|---|--------------------------|------------------------------|--------------------------|-------------------------|---------|
| G1 | TABLE_CELL_COLUMN unavailable (19/26) | "两个数值在**同一表格行的不同列**/不同 cell" — 行列结构关系 | IS-01/IS-02 (文本模式); P4 geometry (gap/dy/style); IS-11 observer (表格检测, 覆盖 28.9%) | 更高覆盖的 table region/cell 检测 | **非 IS-14** → Perception 轨道 (Frozen 修改候选, 独立治理) |
| G2 | TABLE_HEADER (7; 3 已被 IS-11 解决, 4 unavailable) | "两个**列头**属于不同列" — 同 G1 的行列结构 | 同 G1 (3/7 已由 IS-11 different_cell 正确解决) | 同 G1 | **非 IS-14** (与 IS-11 信息重复, FAIL-3 风险) |
| G3 | FIGURE_CAPTION (2, 均 MERGE; 另 418 caption-prose KEEP) | 414/422: "同一图注的 **label+子描述/body** 构成一个连续单元" → MERGE；418: "图注 body 内**句子边界**" → KEEP | 无任何现有 IS 观察图注结构; P4 geometry 只有 gap/dy (414: 同行相邻, AMBIGUOUS) | **caption-label 文本模式** (FIG. N:) + **caption 块邻接关系** | **IS-14 ✓** |
| G4 | FIGURE_AXIS_TICK (3, KEEP) | "两个数值是**相邻的独立刻度标签**" — 不是同一标签 | 无任何现有 IS 观察刻度序列; IS-01 把 "0.70" 判为 number, IS-02 对 "0.75" 为 False → §9.3 ABSTAIN | **numeric tick-run 对齐观察** (等差数列 + 均一字号 + 行/列对齐) | **IS-14 ✓** |
| G5 | DIAGRAM_LIST_ITEM (1, KEEP) | "图示中两个**独立列表项**" | 无 | 图示元素检测 (最难, n=1) | **Deferred** (证据不足) |
| G6 | PROSE sentence boundary (4) | "句号结尾 + 大写开头 = 两个句子" | 信号本身 machine-observable (adjudicator 实际使用) | — | **非 IS-14**: IS-10 = HUMAN_OWNED 冻结, 重开不在授权范围 (仅记录) |

### 关键洞察 (4.3 的最终形式)

```
Existing Observable (P4 geometry + IS-01 + IS-02 + IS-11-as-run)
        +
New Observable (caption-label 模式 / caption 块邻接 / tick-run 对齐)
        ↓
Machine Decision (预注册协议消费 — 非 IS-14 本身裁决)
```

不是 `Existing Observable + another label`。IS-14 只提供**新的机器可观察变量**；决策映射是独立的预注册协议层 (与 Stage 4 IS-11 的 experimental_c_decision 同构，GT 冻结前锁定)。

---

## 4. Candidate IS-14 Information Sources (§3 重新分析，不预设)

对 Phase 1 候选逐一检验 "是否共享同一个可观测结构问题":

| 候选 | 机器可观察抽象 | 抽象是否与其它候选共享? |
|------|--------------|---------------------|
| FIGURE_CAPTION | 文本模式 (caption label) + 块邻接 | 独立抽象 (文本模式类) |
| FIGURE_AXIS_TICK | 几何对齐 (等差 numeric run) | 独立抽象 (几何序列类) — 但与 caption 同属 figure 域 |
| TABLE_HEADER | 表格行列结构 | **与 IS-11 同抽象** → 冗余 |
| DIAGRAM_LIST_ITEM | 图示元素分组 | 无可靠可观察抽象 (n=1) |

**结论**: caption 与 tick 虽然观察途径不同 (文本模式 vs 几何序列)，但回答**同一个结构问题** — "这两个片段在图形文本上下文中属于同一结构单元还是不同单元?" — 且域相同 (非表格的图形文本上下文)。二者可合并为**一个**信息源的两组观察组件；header/diagram 不能。

---

## 5. Rejected / Deferred Candidates

| 候选 | 决定 | 理由 (映射 FAIL 条件) |
|------|------|---------------------|
| Broad IS-14 = DOCUMENT_STRUCTURE_ROLE (table+figure+caption+body+heading+footnote+reference+equation 全角色分类器) | **REJECT** | 违反单一假设原则 (§9); 角色分类器接近 semantic decision (FAIL-4 风险); 观察组件过多难以归因 (FAIL-7) |
| IS-14 包含 TABLE_HEADER unavailable 缺口 | **REJECT** (从 IS-14 范围剔除) | 与 IS-11 信息重复 (FAIL-3); 4 个未解决 case 的根因是 frozen detector 覆盖 → 修改 detector = Frozen 修改 → 属 Perception 独立轨道 |
| IS-14 包含 TABLE_CELL_COLUMN unavailable (19 cases) | **REJECT** (同上) | 同上; IS-11 已在 13/45 可用时 13/13 正确 — 缺的是覆盖不是新信息 |
| DIAGRAM_LIST_ITEM observer | **DEFER** | n=1, 无可靠可观察抽象 (FAIL-1 风险); 若未来 corpus 中 diagram 案例增多可重新立项 |
| Sentence-boundary IS (period+capital) | **OUT OF SCOPE** | IS-10 = HUMAN_OWNED 冻结; 信号可观察性仅作记录，不立项 |

---

## 6. Final IS-14 Hypothesis

> **IS-14 = GRAPHIC_TEXT_CONTEXT**
>
> 对一个 candidate pair (text_a, text_b)，若其**不在任何检测到的表格区域内** (IS-11-as-run 域划分)，IS-14 观察该 pair 是否处于图形文本上下文，并区分两种结构单元关系:
>
> - **Caption 单元关系**: 其中一个片段是图注 label (预注册正则)，另一个片段位于同一 caption 文本块 (label 所在块或其直接连续块) → 二者属于**同一图注单元**。
> - **Tick 序列关系**: 两个片段均为纯数值，且各自属于一个**对齐的等差数值序列** (≥3 成员、行或列对齐、字号均一、间距近似恒定) → 二者属于**不同刻度单元**。
>
> IS-14 提供的是**机器可观察变量** (§7)，不是 MERGE/KEEP 裁决；裁决由预注册协议 (§14) 消费这些变量。

**假设来源链** (Human Feedback → Gap → Observable → Hypothesis):
69-case FP rationales (table) 与 Stage 3 KEEP/MERGE rationales (caption/tick) → Phase 1 taxonomy → 本设计收窄。历史名称 DOCUMENT_STRUCTURE_ROLE 被收窄为 GRAPHIC_TEXT_CONTEXT — 收窄决定记录于 §5。

**设计可行性探测** (READ-ONLY 页面数据检查，非实现):

| 探测 | 结果 |
|------|------|
| caption-label 正则 `^(FIG\|Fig\.?\|Figure)\s*\d+` | med_001 p19/p20/p24 的 'FIG. 8:', 'FIG. 9:', 'FIG. 12:' 全部命中 (span size=12.0, 正文 ~10) ✅ |
| tick-run 对齐 | med_001 p19: 20 个纯数值 span 组成 2 行 × 2 个等差序列 (17.9→18.7 Δ=0.2; 0.70→0.90 Δ=0.05; 1.25→1.45 Δ=0.05; 0.65→0.85 Δ=0.05), 字号均一 9.0, 行内 y 全等 ✅ |
| image-block 可用性 | med_001 仅 4/29 页有 image block; resnet_001 与 cs_001 **0/20 页**; efficientnet_001 1/11 页 → **vector figure 普遍存在** → OBS-D 降级为辅助信号 ⚠️ |

---

## 7. Machine-Observable Definition

全部观察从页面数据 (PyMuPDF text dict + 现有 candidate bbox) 机械推导，确定性、无语义判断、无人工输入:

| OBS | 名称 | 定义 (预注册) | 输入 | 输出 |
|-----|------|--------------|------|------|
| OBS-A | caption_label | 片段 span 文本匹配冻结正则集合 `^(FIG|Fig\.?|Figure)\s*\d+\s*[:.]?` (大小写不敏感; 正则集合在 GT 冻结前锁定，含已知变体列表) | span text | bool + matched text |
| OBS-B | caption_continuation | 另一片段中心位于 caption label 所在文本块内，或位于其**紧邻连续块** (同栏、块间距 ≤ 预注册阈值 14pt，沿用 P4 max_vertical_gap 语义一致性) | span bbox + page text blocks | bool + block ids |
| OBS-C | numeric_run | 两片段均为纯数值 (`^\d+(\.\d+)?$` 或带 % 的变体，预注册)；且各自属于某一对齐序列: 同 y-行 (y-center 差 ≤ 2pt) 或同 x-列 (x-center 差 ≤ 2pt) 上 ≥3 个纯数值 span、字号两两差 ≤ 0.5pt、相邻间距变异系数 ≤ 0.15 | 全页 numeric spans + bboxes + sizes | bool + run members + spacing |
| OBS-D | image_block_proximity (仅辅助) | 片段中心距任一 image block bbox ≤ 预注册 margin 20pt | page image blocks | bool (不参与协议门槛，仅随 trace 记录) |

**观察域前置条件**: pair 不在任何检测到的表格区域内 (IS-11-as-run 判定)。若在表格内 → IS-14 输出 `NOT_APPLICABLE(table_domain)`。

**不重复现有 observable 声明**: OBS-A/B/C 在 P1-P6、IS-01、IS-02、IS-11 中均不存在 (IS-01 是对 candidate 自身的 number 判定，OBS-C 是页面级序列对齐；IS-11 是表格线检测；P6 DENSE 是弱密度代理)。OBS-D 使用 PyMuPDF 原生 block 数据，非新 parser。

---

## 8. Boundary with IS-11

| 维度 | IS-11 (FROZEN, as-run) | IS-14 (HYPOTHESIS) |
|------|------------------------|--------------------|
| 域 | 检测到的表格区域 (table lines → region + cell grid) | 非表格的图形文本上下文 (caption / tick 序列) |
| 核心观察 | cell membership (same/different cell) | caption 单元归属 / tick 序列归属 |
| 数据来源 | table_line_detector (VLines) | 页面 text spans 模式 + 对齐几何 (+image block 辅助) |
| 决策方向 | different_cell→KEEP (8/8 已演示); same_cell→MERGE | caption 单元→MERGE (首次 MERGE 通路); tick 序列→KEEP |
| 优先级规则 | 表格域内**独占** | 仅在 IS-11 判 `NOT in table` 时观察 |

**域划分预注册**: 每个案例先运行 IS-11-as-run 域判定 (与 Stage 4 完全一致的调用与参数)；`in_table=True` → IS-14 = NOT_APPLICABLE；`in_table=False` → IS-14 观察。两 IS 永不同时对同一案例提供有效观察 → C−B 增量可完全归因于 IS-14 (FAIL-7 防护)。

**不能把 IS-11 未解决的问题塞进 IS-14**: 19 个 table-cell unavailable + 4 个 header unavailable 案例被显式排除在 IS-14 预期收益之外 (§5)，其归属为 Perception 轨道候选 (独立治理，未授权)。

---

## 9. Human Effort Budget

**评审负担: 与 Stage 3 相同或更低。**

| 项 | 设计 |
|----|------|
| Human 做什么 | 仅 1-click: MERGE / KEEP_SEPARATE (双盲 A/B + adjudication) |
| Human 不做什么 | ❌ 标注 cell/header/axis/caption/bbox ❌ 填写 reason ❌ 解释失败 ❌ 建 feature ❌ 写规则 ❌ 判断 detector 错误 (全部映射 Phase 2 §7 禁止清单) |
| 与 Stage 3 差异 | **不再要求 rationale 字段** (Stage 3 曾要求自由文本 rationale；本设计按 §12 禁止项取消强制 reason) |

**披露的 trade-off**: 取消 rationale 意味着新 corpus 的 GT 不携带 Stage 3 式的理由文本 → 未来 Phase-1 式人工理由分析在该 corpus 上不可重复。缓解: 机器侧观察 (IS-14 观察值 + IS-11 观察 + geometry) 全程留痕，缺口分析可基于机器观察 × 决策交叉进行 (Phase 1 §5 的主要方法本就不依赖 rationale)。

---

## 10. Automatic Inference Possibility

| 问题 | 回答 | 依据 |
|------|------|------|
| reason_category 是否需要人工提供? | **不需要** | IS-14 观察全部自动推导 (§7); Phase 1 已演示 43/45 rationale 可机器分类 |
| IS-14 观察是否需要人工逐例标注? | **不需要** | OBS-A/B/C/D 从页面数据机械推导 (Stage 4 IS-11 同模式: 13/45 案例零人工观察) |
| 观察与决策矛盾时是否需要人工? | 评估期不需要; 生产期 (未授权) 可作为 review-priority 信号 | 设计边界 |

---

## 11. Independent Corpus Design

**禁止复用**: Stage 1/3/4 的 4 个 PDF (resnet_001, efficientnet_001, med_001, cs_001) 与其 GT。不得因已知 MERGE=2/KEEP=43 反向挑选案例。

### Corpus 要求 (预注册)

| 项 | 要求 |
|----|------|
| PDF 数量 | 4–6 篇，**全新独立**，零 DICE 先前处理 (与 `tmp/` 下所有既有 manifest 的 SHA-256 交叉验证无重叠) |
| 领域 | ≥3 个新领域 (与 Stage 1 的 CV/NLP/物理/LLM 不重复)，**figure-heavy** (文档级判据: 平均每篇 ≥4 个 `FIG./Fig./Figure N.` 图注；文档级选择在案例级抽样之前，且对案例级 GT 盲) |
| 表格多样性 | ≥2 篇含无框线表格 (IS-11 对照域, 检验域划分不误伤) |
| Manifest | 文件名 + SHA-256 + 来源 + 页数; corpus 冻结后不可更换 |
| 抽样 seed | 固定整数，在 corpus manifest 冻结时一并记录 |

### Pipeline (与 Stage 1-3 同构)

```
Independent Corpus (SHA-256 frozen)
    ↓ P1-P6 (frozen, unmodified) — 纯几何 AMBIGUOUS 切片
Frozen Candidate Universe
    ↓ 预注册分层抽样 (仅几何维度: gap / w_b / line_obs; seed 固定)
Frozen Sampling Frame (n=54)
    ↓ 盲审双评审 + adjudication (label-only)
Frozen GT (Level-2)
    ↓ 之后才允许 IS-14 观察与评估
Baseline B vs Experimental C
```

**n=54 的理由**: 比 Stage 3 的 45 大 20%，在评审成本相近下提高少数类产出；抽样仍为几何盲分层。

**案例级 figure-context 命中率不预设、不用机器预筛** — 保持与 Stage 1-3 相同的 "抽样不含任何 IS 信息" 纪律 (避免把 IS-14 可用性烘焙进样本、夸大 ΔCoverage 的选择偏差)。

---

## 12. Human Review Design

| 项 | 设计 |
|----|------|
| 标签 | MERGE / KEEP_SEPARATE (仅二选一, 1-click) |
| 评审者 | 独立 Reviewer A + Reviewer B, 盲审 (仅见 case_id/page/text_a/text_b/page_context; 不见任何 IS/几何/机器信息) |
| 分歧处理 | 第三方 adjudication (仅可看 PDF 上下文, 不可看机器输出) |
| reason 字段 | **无** (§9) |
| GT 冻结时序 | **GT 冻结先于 IS-14 观察** (与 Stage 4 G2/G3 同纪律) |
| Provenance audit | 复用 `is11_provenance_audit.py` 模式: P1 抽样完整 / P2 文本未改 / P3 评审独立 / P4 机器泄漏 / P5 无事后选择 / P6 基线无漂移 |
| Integrity gate | 45→54 案例 0 missing / 0 extra / 0 duplicate |

---

## 13. Baseline B Definition

```
Baseline B = Geometry + IS-01 + IS-02 + IS-11 (frozen existing state)

  Geometry        : P4 frozen SpanConfig 判定的 AMBIGUOUS 状态 (Baseline A 在此全部 INSUFFICIENT_EVIDENCE)
  IS-01           : FROZEN ^\d+(\.\d+)*\.?$ OR ^[A-Z]\.\d+$ (未修改)
  IS-02           : FROZEN any-word->2-alpha-chars (未修改)
  §9.3 协议       : FROZEN (IS01∧IS02→MERGE; ¬IS01∧¬IS02→KEEP; else ABSTAIN)
  IS-11 as-run    : Stage 4 冻结的 experiment-only observer 行为
                    (域判定 + different_cell→KEEP / same_cell→MERGE / else 维持 §9.3)
```

IS-11 在 **B 与 C 两臂中完全相同** (冻结既有状态) — C−B 的全部差异只能来自 IS-14。

---

## 14. Experimental C Definition

```
Experimental C = Baseline B + IS-14 (HYPOTHESIS → experiment-only observer)

前置: IS-11 域判定 (as-run, 与 B 完全一致)
  in_table=True  → IS-14 = NOT_APPLICABLE → C 决策 = B 决策
  in_table=False → IS-14 观察 OBS-A/B/C(/D) → 预注册协议 R1/R2:

R1 (caption 单元 → MERGE):
  条件: OBS-A(a) ∧ OBS-B(b→a 的 caption 块)  [或对称: OBS-A(b) ∧ OBS-B(a→b)]
  动作: INSUFFICIENT_EVIDENCE → MERGE;  B=MERGE → MERGE (no-op)
  边界: **不覆盖 B=KEEP** (§9.3 已作出的正向 KEEP 判定不被 IS-14 推翻 — 保守方向;
        B=KEEP 要求 IS02_b=False, 与 caption-continuation 常见形态冲突小, 但保守优先)

R2 (tick 序列 → KEEP):
  条件: OBS-C(两片段同属各自对齐等差数值序列)
  动作: INSUFFICIENT_EVIDENCE → KEEP
  结构性保证: B=MERGE 要求 IS02_b=True (text_b 含 >2 alpha 词), 与 "text_b 纯数值"
  互斥 → R2 永不覆盖 B=MERGE (无新增 FP 通路, 协议级证明)

R3 (图形上下文但单元关系不确定): 维持 B 决策 (不强制判定)
```

**协议性质声明**: R1/R2 是 GT 冻结前锁定的**实验决策协议**，与 Stage 4 的 experimental_c_decision 同构；IS-14 本体 = §7 的观察变量集。协议映射是设计选择，预注册以免事后调参 (§13/§14 Phase 2 指令)。

**已观测案例的协议一致性自检** (设计期验证, 非评估):
- 414 ("FIG. 9:"+"Left:"): R1 命中 → MERGE ✓ (GT=MERGE)
- 422 ("FIG. 12:"+"Distribution..."): R1 命中 → MERGE ✓ (GT=MERGE)
- 418 (caption body+body): R1 不命中 (无 label) → 维持 ABSTAIN (GT=KEEP, 不伤害) ✓
- 401/407/409 (tick 对): R2 命中 → KEEP ✓ (GT=KEEP ×3)

---

## 15. Experiment Matrix

| Item | Baseline B | Experimental C |
| ---- | --------------------- | --------------------- |
| Geometry | YES (P4 FROZEN) | YES (P4 FROZEN) |
| IS-01 | FROZEN | FROZEN |
| IS-02 | FROZEN | FROZEN |
| IS-11 | FROZEN EXISTING STATE (as-run) | FROZEN EXISTING STATE (identical) |
| IS-14 | NO | HYPOTHESIS (experiment-only observer + R1/R2 预注册协议) |
| Human additional annotation | NO (label-only) | NO (label-only) |
| Frozen modification | NO | NO |

---

## 16. Failure Conditions (预注册)

| 条件 | 判定 | 动作 |
|------|------|------|
| FAIL-1 IS-14 无法形成独立 observable | OBS-A/B/C 定义无法机械落地或非确定 | **STOP** |
| FAIL-2 依赖复杂 Human annotation | 任何环节需要人工标注 cell/header/axis/caption/reason | **STOP** (Phase 1 §7/本设计 §9 已排除 → 不预期触发) |
| FAIL-3 与现有 IS 信息重复 | 发现 OBS 与 IS-01/02/11 或 P4 信号实质等价 | **REJECT / REDESIGN** |
| FAIL-4 越界成为 semantic decision | IS-14 被实现为直接输出 MERGE/KEEP 的语义分类器 | **REJECT** (本设计以 §7 观察集 + §14 协议分层规避) |
| FAIL-5 无法设计独立 corpus | 找不到满足 §11 要求的全新 figure-heavy PDF | **STOP** |
| FAIL-6 无法定义安全 gate | Safety 指标无法操作化 | **STOP** (本设计已定义 G-S1..S5 → 不预期触发) |
| FAIL-7 无法区分增量贡献 | 域划分失效 (IS-11/IS-14 对同一案例均有效观察) 或混淆表格域案例 | **REDESIGN** (域前置条件 + 归因审计防护) |

**评估期附加失败条件** (Phase 3 执行时): G-A1 可用性 < 60% → 观察者过弱, 停止评估记为负结果, **不得调参重跑**；G-S1/G-S2 任一 FAIL → IS-14 增量价值不成立，记录并 STOP。

---

## 17. Pre-Registered Gates (全部阈值此刻锁定，GT 之前)

### Safety (与 Utility 严格分离 — §14 教训)

| Gate | 定义 | 阈值 | 理由 |
|------|------|------|------|
| G-S1 | ΔFP (C−B) | **≤ 0** | IS-14 不得制造任何新错误 MERGE; R2 协议级无 FP 通路, R1 不覆盖 KEEP → 预期 0 |
| G-S2 | ΔFN (C−B) | **≤ 0** | 不得把真 MERGE 判成 KEEP (R1 只增 MERGE, R2 只作用于纯数值对) |
| G-S3 | Determinism | **0 mismatches** (双次运行 case 级决策+观察+trace 全等) | 同 Stage 4 G11 |
| G-S4 | Provenance | **PASS** (document SHA → case → span → observer 输入/输出 → 决策 → GT 比对全链; 无 GT 泄漏进 observer) | 同 Stage 3/4 audit 模式 |
| G-S5 | Frozen regression | **全部 SHA-256 不变** (P7.1/P7.2 manifests, span_config, IS-01/02 定义, table_line_detector, Stage 3/4 artifacts) | 实验前后双检 |

### Utility (由 IS-14 的信息角色定义 — 非 FP-reduction)

| Gate | 定义 | 阈值 | 理由 |
|------|------|------|------|
| G-C1 (评估前置) | 语料充足性 | 冻结样本中 **figure-context 案例 ≥15 且非图形对照案例 ≥20** | 无足够图形案例则 utility 无检验功效 → 停止, 不进入评估 |
| G-A1 (评估前置) | Observer 可用性 | IS-14 对 figure-context 案例给出**确定观察** (R1/R2 命中或明确 R3-不确定归类) 的比例 **≥60%** | Stage 4 教训: IS-11 可用性仅 28.9% 直接掏空检验; 60% 为有意义覆盖下限 |
| G-U1 (PRIMARY) | ΔCoverage (C−B) | **> 0** | IS-14 的角色 = 解析图形上下文弃权 (IS-11 已演示该类增量真实存在) |
| G-U2 | 新增决策正确率 | B=ABSTAIN→C=decided 的案例中 GT 正确率 **≥ 66.7%** (2/3) | 错误解析比弃权更危害 (safety-first 治理原则); 2/3 为最低可信线, 小样本下同时报告精确计数 |
| G-D1 | 跨文档稳定性 | ΔCoverage > 0 出现在 **≥2 个文档** | Stage 4 教训: 单文档改善不构成 stability |

**报告义务 (非 gate)**: ΔRecall / ΔPrecision 照实报告但标注统计不稳定 (少数类分母小); MERGE 方向正确数 (历史 TP=0 → 首次 TP 的出现本身是重要报告项)。

---

## 18. Determinism / Provenance / Regression Gates

见 §17 G-S3 / G-S4 / G-S5。补充执行规范:

- **Determinism**: C 条件完整跑两遍 (观察 + 决策 + trace 逐字段比对)；任何非确定来源 (dict 顺序、浮点合计) 必须在 observer 设计中显式排序/取整消除。
- **Provenance**: 每 case 记录 `pdf_sha256, page, candidate bbox/span ids, IS-11 域判定输出, OBS-A/B/C/D 原始输入与输出, R1/R2 触发与否, 最终决策, GT`；audit 脚本独立于 observer。
- **Regression**: 实验开始前 + 结束后各跑一次冻结清单 SHA 校验; 任何 drift → 全部结果作废。

---

## 19. Expected Information Gain

**基于现有冻结证据的预估 (非承诺)**:

| 项 | 估计 | 依据 |
|----|------|------|
| 图形上下文案例占新样本比例 | 未知 (corpus 依赖); med_001 先例: 该文档 8/8 抽中案例均为图形域 | 文档级 figure-heavy 选择提高命中, 案例级不干预 |
| 可解析案例 (R1/R2) | 在现有 45-case 证据上: 5/45 (11.1%) 命中 R1/R2 且全部 GT 正确 (2 MERGE + 3 KEEP); 418 类 (caption body) 不解析 (保守) | §14 自检 |
| MERGE 方向 | **首次为系统提供产生正确 MERGE 的结构通路** (历史 TP=0) | R1 对应全部 2 个 MERGE GT 缺口 |
| 跨文档泛化 | 待验 (G-D1); caption/tick 模式为跨领域常规排版, 先验合理但未证明 | — |
| 已知局限 | vector figure → OBS-D 弱; OBS-C 需防表格域误触发 (域前置 + 等差判据); caption 变体 (Fig. 5 / Figure 5 / 图 N?) → 正则集合冻结 + 非英文文献风险披露 | §6/§7/§16 |

**若 G-U1/G-U2 PASS**: IS-14 获得 empirical support (coverage 方向) → 才讨论下一信息源或 Perception 轨道; **不授权集成**。
**若 FAIL**: 按预注册失败记录 (如 R1 过严 → caption 变体漏检; R2 误触发 → 归因审计), 不调参重跑。

---

## 20. Experiment Readiness Decision

```
╔══════════════════════════════════════════════════════════════╗
║  DESIGN_READY                                                ║
║                                                              ║
║  IS-14 = GRAPHIC_TEXT_CONTEXT (HYPOTHESIS, 收窄自             ║
║          历史 DOCUMENT_STRUCTURE_ROLE)                        ║
║  观察集 = OBS-A/B/C (+OBS-D 辅助) — 全部机器可观察、确定性、     ║
║           与现有 IS 零重叠、零人工输入                          ║
║  边界   = 与 IS-11 按域划分, 案例级互斥, 增量可归因             ║
║  人工   = 1-click label-only, 双盲 + adjudication             ║
║  Frozen = 全程不修改 (实验前后 SHA 双检)                        ║
╚══════════════════════════════════════════════════════════════╝
```

**进入 Phase 3 (评估) 的 3 项 pre-conditions** (全部满足才可请求授权):

1. **G-C1 语料充足性达成**: 全新 figure-heavy 独立 corpus 冻结 (SHA-256 manifest) 且冻结样本含 ≥15 figure-context + ≥20 对照案例。若语料不可得 → FAIL-5 → STOP。
2. **caption-label 正则集合冻结**: 在 GT 收集前锁定变体列表 (FIG./Fig./Figure N + 冒号/句点变体; 非英文文献的覆盖范围显式声明或排除)。
3. **vector-figure 局限披露确认**: OBS-D 仅为辅助; 观察主力为文本模式 + 对齐几何 (已在 med_001 探测中验证可行)。

**Phase 2 交付物边界**: 本文档是唯一交付物。无 observer 代码、无 runner、无评估脚本、无 corpus 下载、无抽样执行。

---

## 19'. Safety Statement (final, verbatim)

```text
PHASE 2 = DESIGN ONLY
IS-14 = HYPOTHESIS ONLY
IS-14 IMPLEMENTATION = NOT AUTHORIZED

FROZEN BASELINE = INTACT
P7.3 = NOT AUTHORIZED
PRODUCTION = FALSE

NO CODE MODIFICATION
NO NEW IS IMPLEMENTATION
NO GT MODIFICATION
NO HUMAN COMPLEX ANNOTATION

STOP = TRUE
WAIT FOR EXPLICIT AUTHORIZATION
```

---

## 状态机

```
Phase 1 (LOOP_SUPPORTED)
    ↓
Phase 2: IS-14 Controlled Experiment Design
    ↓
DESIGN_READY (3 pre-conditions 记录在案)
    ↓
IS-14 = GRAPHIC_TEXT_CONTEXT / HYPOTHESIS ONLY
    ↓
Phase 3 (IS-14 Machine Evaluation) = NOT STARTED
    ↓
PENDING EXPLICIT AUTHORIZATION
    ↓
STOP = TRUE
```

> **Experiment first → Evidence second → Decision third → Implementation last.**
> 本设计未运行任何评估、未实现任何观察者、未触碰任何冻结文件。执行到设计报告生成立即 STOP。
