# Phase 4 — Research Object Design: Atomic Observation Layer

> **DESIGN ONLY。** 不写代码、不修改任何现有文件、不运行实验、不收集 GT、不进入 Implementation。
> 本文档唯一任务: 把 "Research Object 应该是什么" 设计清楚。
>
> 证据标签: **OBSERVED** (代码/artifact 可查) / **INFERRED** (由证据推导) / **HYPOTHESIS** / **NOT ESTABLISHED**。
> 前置: Phase 3 Closure Diagnostic = MIXED_CAUSE (H3 研究对象表示错配为主因) / NEXT MAP ACTION = DESIGN_RESEARCH_OBJECT。

---

## 1. MAP 与当前架构读取结果 (READ-ONLY)

### 1.1 两层 MAP (复用 Phase 3 定位结论)

- 层 1: Perception Roadmap 阶段 0-6 — **阶段 1 "Atomic Observation Layer" 是本设计的既有 MAP 归属节点** [OBSERVED]
- 层 2: IS-Experiment 链 (Stage 0-5 → Phase 1-3) — Phase 3 = BLOCKED @ G-C1 [OBSERVED]

### 1.2 实际代码架构 (逐文件核实) [OBSERVED]

| 层 | 模块 | 产出物 | 语义纪律声明 |
|----|------|--------|-------------|
| P1 | `observations/atomic_text.py` | `AtomicTextObservation` (text, bbox, page, font_name/size/flags, source_index, reading_order_hint; **仅文本层** char/word/span/line/block) | 原子事实 |
| P2 | `geometry/` | `PairwiseGeometry` (width/height/center, **same_y_band_members, same_x_band_members, left/right/top/bottom/center_alignment_group, spatial_cluster_members**) + `PairwiseRelation` (horizontal/vertical_distance, overlap, direction) | 纯几何 |
| P3 | `style/` | `StyleObservation` + style_signature — 代码注释: **"No text/bbox/semantics"** | 纯样式事实 |
| P4 | `span/` (FROZEN SpanConfig) | `ExperimentalSpan` + `MergeDecision` trace (合并轨迹保留) | 几何合并 |
| P5 | (p5_runner) | 列布局 (geometric x-stripe 分组) | 几何 |
| P6 | `region/` | `RegionObservation`: PAGE_TOP / PAGE_BOTTOM / FULL_WIDTH / COLUMN / DENSE / SPARSE / UNKNOWN — 注释: **"NOT semantic classification"** | 几何区域 |
| P7.1 | `structure/` | `StructureHypothesis` (**仅 7 种候选**: HEADING/PARAGRAPH_GROUP/SECTION/LIST/HEADER/FOOTER/MULTI_COLUMN_CONTINUATION; 显式排除 TABLE/IMAGE/FORMULA; "never asserts is_\*=true") + `StructuralRelation` (**8 种**: STYLE_CONTRAST, VERTICAL_SEPARATION, ADJACENT_TO, LEFT_ALIGNED_WITH, PRECEDES, SHARES_REGION, CONTINUES_FROM, REPEATS_ACROSS_PAGES) — 反向追溯 Hypothesis→Relation→Span/Region→Observation | 候选, 非事实 |
| P7.2 | `validation/` | `ValidationTask/Record/ValidatedEvidence/AuditChain` (ACCEPT→Evidence) | 人工验证 |
| P7.3+ | — | **不存在** | NOT AUTHORIZED |

### 1.3 任务清单中**不存在于代码**的概念 [OBSERVED — 检索为空]

`DocumentSpan` (类)、`GenericBoundaryEvaluator`、`Evidence Admission` (作为代码)、
`Capability Registry / Capability Runtime / Runtime Authority`、`CapabilityCandidateObservation`、
`validation_memory.py` — 这些是治理/路线图层的**概念名称**， 无对应实现。
数据流终点如实为: **P7.2 ValidatedEvidence (终点)； Capability 未建 (P7.3 = NOT AUTHORIZED)。**

### 1.4 实际数据流 (以真实类名为准) [OBSERVED]

```text
Document (PDF)
  → P1  AtomicTextObservation          (原子: text+bbox+font+page; 仅文本)
  → P2  PairwiseGeometry/Relation      (相邻对几何 + 对齐组/同行带 — set 级!)
  → P3  StyleObservation               (确定性 style signature)
  → P4  ExperimentalSpan + MergeTrace  (FROZEN: gap≤8 同行同款合并)
  → P5  Column groups                  (几何列)
  → P6  RegionObservation              (几何区域: PAGE_TOP/COLUMN/DENSE/…)
  → P7.1 StructureHypothesis (7 类) + StructuralRelation (8 类)   [候选层]
  → P7.2 ValidationRecord → ValidatedEvidence (Human ACCEPT)      [验证层]
  → (Capability / Runtime: 未建 — P7.3 NOT AUTHORIZED)
```

**IS-实验轨道的 research object 现状**: IS-11/IS-14 的候选对由冻结管线从 **P1 原子**直接生成
(相邻、同行、未合并原子对)， IS observer 各自用 PyMuPDF **重新解析 PDF** 获取几何
(`is11_machine_evaluation.py` 与 `phase3_is14_observer.py` 各自独立实现页面解析 — 无共享观测层)。

---

## 2. Representation Loss 到底发生在哪里 (§一核心问题)

### 2.1 关键判别: P1/P2 的原子与关系**并未销毁** — 丢失的是"暴露与承载"

[OBSERVED] P1 原子与 P2 关系是确定性函数 (同一 PDF 重跑即重现)， 其 artifact 仍然存在。
因此本设计面对的不是 "重建已丢失的表示"， 而是:

> **(a) 下游只读 span、不读 atom (承载断层)； (b) 观测层对 IS 实验轨道没有查询接口 (暴露断层)；
> (c) 原子层缺 IMAGE 类； (d) 关系词汇缺 set 级规律函数； (e) 各 observer 重复实现几何。**

### 2.2 信息分类总表 (§一五问)

| 类别 | 内容 | 位置 |
|------|------|------|
| **CandidateSpan 之前已存在** | 原子 text/bbox/font/page/reading_order; 相邻对 h/v distance/overlap; 同行带; 五种对齐组; 空间簇; style signature; P6 几何区域 | P1/P2/P3/P6 [OBSERVED] |
| **被 P4 吸收** (span 层不再可分) | 碎片 (sub-span) 边界与碎片级 bbox; ≤8pt 碎片间距; 原子身份 (obs_id 组→单 span); 同行相邻关系 (对下游 span 读者而言) | P4 合并 [OBSERVED: MergeTrace 保留合并决策， 但下游消费者读 span 不读 trace] |
| **根本没有被保存** | **IMAGE 原子** (image block 不入 P1); **非相邻对关系** (P2 artifact 只存 reading-order 相邻对); **set 级规律关系** (等距序列/均匀 run/重复值 — P2 有对齐组但无 run/等距); caption/track 实验所需的观测无版本化持久层 | [OBSERVED 缺口] |
| **只能通过特定 detector 获得** | 表格区域 (table_line_detector, 冻结)； IS-14 的 caption/tick 查询 (各 observer 临时实现) | [OBSERVED] |
| **generic observable (可入原子层)** | text / bbox / page / font / 行列位置 / block 边界 / region membership (provenance 命名) / adjacency / distance / alignment / containment / repetition / image presence / table region (detector 输出的事实) / 几何关系 | §二清单 ✓ |
| **semantic interpretation (禁止入层)** | is_figure_caption / is_axis_label / should_merge / should_keep_separate / confidence / semantic_role / relevance / recommendation / decision | §二禁止清单 ✓ |

---

## 3. 最小可复用 Atomic Observation 的推导 (§三 — 先回答， 再 schema)

**推导链: 事实 → 可观测关系 → 可组合对象**

1. **事实层 (必须存在)**: 文档中存在"有位置的内容"。文本内容有位置 → TEXT 原子；
   图像块有位置 → IMAGE 原子。这是 PDF 几何层能确定性给出的全部原子事实。
2. **可观测关系层**: 任意原子集合之间的**确定性几何/集合函数** — 距离、共线、对齐、
   包含、邻接、等距、均匀 run、重复、区域归属。全部可从原子坐标机械计算， 无一词义。
3. **可组合对象层**: hypothesis = "对原子+关系的**查询谓词**"。Hypothesis 声明它需要哪些
   关系类型与原子类， 以自己的词法/统计规则解释查询结果 — **层本身不解释**。

**结论**: 最小可复用 Atomic Observation =

> **Atom (TEXT|IMAGE, 位置+内容+样式) + 闭集 Relation (确定性几何/集合函数, 参数显式版本化)**
> — 即 **"可查询的 P1-P6 事实暴露层 + 最小增量"**， 而非新发明表示。

关键佐证 [OBSERVED]: P2 已经有 same_y_band / 对齐组 / 空间簇 (set 级！)， P6 已经有几何区域，
P7.1 已经建立 "关系是事实、假设是候选" 的纪律。**设计的主要工作是"补缺口 + 立接口"， 不是"从零发明"。**

---

## 4. 三套候选 Abstraction (§四 — 不预设答案)

### Candidate A — "Expose Existing" (仅暴露既有 P1+P2 artifact, 零扩展)

1. 最小信息单元: `AtomicTextObservation` + `PairwiseRelation` (现成) [OBSERVED]
2. 能表达: 文本/位置/样式事实 + 相邻对几何 + 对齐组/同行带
3. 关系: pairwise + 已存 set 组 (对齐/带/簇)
4. 依赖 semantic label: 无
5. 依赖具体 detector: 无
6. 支持 IS-11: **部分** — 无 region fact 接口 (detector 输出不可查询)
7. 支持 IS-14: **部分** — 无 IMAGE 原子； 无等距 run 关系
8. 支持未知 hypothesis: **弱** — 只有"已持久化"的关系 (相邻对)， 非相邻/集合查询需各自重解析
9. 改变 CandidateSpan: 否
10. 侵入 Evidence Admission: 否
11. 侵入 Capability Runtime: 否

### Candidate B — "Atomic Observation Layer v2" (暴露层 + 最小增量) ★

1. 最小信息单元: **Atom** {atom_id, doc_id, page, kind∈{TEXT_ATOM, IMAGE_ATOM}, bbox,
   content(TEXT), style_signature(TEXT), source_provenance} — TEXT 原子 = P1 span 层原子
   (只读复用)； IMAGE 原子 = PyMuPDF image block (新增， 仅 presence+bbox)
2. 能表达: §2.2 全部 generic observable
3. 关系: **闭集 Relation 函数** — 既有 P2 pairwise/对齐组/带 + **新增 4 个 set 级函数**:
   `UNIFORM_RUN_MEMBERSHIP` (等距对齐 run), `EQUIPACED_SEQUENCE` (算术等距序列),
   `IDENTICAL_VALUE` (重复值), `IN_REGION` (region fact 归属; region fact 来自 P6 +
   冻结 detector 输出， **provenance 命名** 如 `table_line_detector@<sha>`, 不带语义标签)
4. 依赖 semantic label: **无** (region fact = "某冻结 detector 在参数 p 下输出的几何区域" 的事实)
5. 依赖具体 detector: 隔离 — detector 输出以 **RegionFact (provenance+params)** 形式**注入**，
   层核心不依赖任何 detector
6. 支持 IS-11: **是** — cell 关系 = TEXT 原子 + IN_REGION + SAME_LINE + ALIGNED_X 查询
7. 支持 IS-14: **是** — caption = 原子级碎片间隙查询 (P4 合并前原子仍在)； tick = UNIFORM_RUN;
   image presence = IMAGE_ATOM
8. 支持未知 hypothesis: **是** — 闭集原语 + hypothesis 自带词法/统计解释 (§6 压力测试)
9. 改变 CandidateSpan: **否** (并行层)
10. 侵入 Evidence Admission: **否** (该组件尚不存在； 层不写 P7.2)
11. 侵入 Capability Runtime: **否** (未建； 层无 decision/routing 能力)

### Candidate C — "Observation Graph / 全物化关系层"

1-3. 全图物化 (全对 O(n²) 边 + 跨层节点)
4-5. 无语义依赖 / 无 detector 依赖
6-8. 表达力最强 (三方案中最高)
9-11. 不改 CandidateSpan / 不侵入 Evidence / 不侵入 Runtime
**否决理由 [INFERRED]**: 物化成本与存储/版本复杂度高； 与 P7.1 的
Hypothesis-Relation 层职责重叠 (重复建设风险)； 大量关系对具体 hypothesis 无用 —
**违反最小主义 (抗过度设计)**。关系应为**按需确定性计算**， 而非全量物化。

**推荐: Candidate B (v2 暴露层)** — 在 A (不足) 与 C (过度) 之间的最小充分方案。

---

## 5. Representation Loss 复盘: IS-14 H3 三案例 (§五)

### 5.1 Caption — 损失的是"承载"， 不是"原子"

```text
"FIG." "9:" "Left:" "BIC" … (P1 原子, 各有 bbox)
   → P4 merge (gap≤8 同行同款) → 单一 ExperimentalSpan "FIG. 9: Left: BIC values…"
   → 候选轨道: 原子对不再作为候选存在 → 研究对象 (label/continuation 边界) 不可作为 case 呈现
```

| 问 | 答 |
|----|----|
| merge 前后机器仍拥有哪些 observable? | 合并 span 的**全文** (词序列仍在!)、总 bbox、style、P1 原子 artifact (未删)、P2 相邻关系 artifact [OBSERVED] |
| 哪些 observable 在 **span 承载层**永久丢失? | 碎片边界 (label 与 continuation 的分界 bbox)、碎片级 gap (2pt vs 7pt 的差异)、原子身份、作为**可查询候选**的地位 [OBSERVED] |
| 哪些在 **P1/P2 artifact 层**并未丢失? | 全部原子事实与相邻关系 — 只是**无接口查询** [OBSERVED] |

→ 结论 [INFERRED]: caption 的损失 = **暴露/承载断层 (Candidate B 的核心靶点)**，
不是原子表示的物理丢失。词法模式 ("FIG N:") 留在 hypothesis 侧 — 层只提供原子+间隙。

### 5.2 Axis Tick — observer limitation, 不是 representation limitation

```text
numeric text → P1 原子 (完整: text/bbox/size) → P2 (同行带/对齐组已有!)
→ AMBIGUOUS universe: 1885 对 eligible (大量进入!) → OBS-C center-CV≤0.15 仅 6.8% 通过
```

[OBSERVED] 原子与同行/对齐关系**全程存在**； 1885 对数值对成功进入候选 universe。
淘汰发生在 **OBS-C 的冻结判定准则** (中心距 CV) 与变宽数字几何的交互上。

> **按 §五要求明确区分**: 这是 **current observer limitation** (IS-14 observer 的冻结查询
> 谓词选择)， **不是 representation limitation** — 位置/宽度/字号信息完整存在， 任何确定性
> 查询变体 (如 edge-gap CV) 都可在不新增表示的情况下定义。
> Atomic Observation Layer 的价值在此案例 = **把几何查询从 observer 的临时重实现中解耦**
> (两个 observer 各自用 fitz 重解析页面的现状 [OBSERVED])， 使查询谓词成为 hypothesis 的
> 显式、可版本化声明 — 而**不是**让层预支任何特定谓词。

### 5.3 Raster Figure — 三分类判定

| 假设 | 判定 | 依据 |
|------|------|------|
| representation loss? | **否** | PDF 文本几何层如实反映了 "文本层无此内容"； DICE 没有丢弃任何已存在的信息 [INFERRED] |
| document perception limitation? | **部分** — 属于"该文档把文字栅格化"这一文件本身属性 | [INFERRED] |
| external modality limitation? | **是** (主判定) | 恢复需 OCR/视觉模态， 在几何层范围之外； 层的职责 = 以 IMAGE_ATOM 忠实记录 **presence** (可观测事实)， 显式声明 content 不可达 [OBSERVED: G-C3 披露] |

---

## 6. 最小 Schema (概念模型) 与 8 案例压力测试 (§六)

### 6.1 概念 Schema (草案 — 非实现)

```text
Atom            atom_id, doc_id, page, kind ∈ {TEXT_ATOM, IMAGE_ATOM},
                bbox[4], content (TEXT: span 文本; IMAGE: null),
                style_signature (TEXT only), source ("P1:span_layer@frozen" | "pymupdf:image_block")

RegionFact      region_id, source_detector ("P6:region_engine" | "table_line_detector@<sha>"),
                bbox, params_hash                      ← 事实: "某确定性过程在此输出了此区域"

Relation (闭集, 确定性函数, 参数显式):
  既有 (P2 复用):  PAIRWISE_GAP_X, PAIRWISE_GAP_Y, SAME_LINE, ALIGNED_X_CENTER,
                   ALIGNED_Y_CENTER, ADJACENT_READING_ORDER, CONTAINED_IN_BBOX
  新增 (v2 最小集): UNIFORM_RUN_MEMBERSHIP (等间距对齐 run, 参数: align_tol, cv_max, min_run),
                   EQUIPACED_SEQUENCE (算术等距, 参数: cv_max),
                   IDENTICAL_VALUE (重复值), IN_REGION (→RegionFact)
  每个 Relation: relation_type, subject_ids, value(s), params_hash, layer_version

禁止字段: is_caption / is_axis_tick / is_table_cell / role / decision / confidence /
          score / ranking / recommendation / execution_plan / fallback / retry /
          override / correction / permission — 任何形式
```

计算策略: **按需确定性计算** (lazy)， 非全量物化 (否决 Candidate C 的理由)。

### 6.2 压力测试: 同一组原语表达 8 种情况

| # | Hypothetical case | 所需原子 | 所需关系 | 词法/解释在哪 | 可表达? |
|---|-------------------|---------|---------|--------------|--------|
| 1 | table cell relationship | TEXT | IN_REGION(detector region) + SAME_LINE + ALIGNED_X_CENTER | hypothesis 判读 cell 归属 | ✅ |
| 2 | figure caption relationship | TEXT (P4 合并前原子仍可查) | PAIRWISE_GAP_X + SAME_LINE + ADJACENT_READING_ORDER | hypothesis 的 label 词法模式 | ✅ |
| 3 | axis tick relationship | TEXT | SAME_LINE/ALIGNED_Y_CENTER + UNIFORM_RUN_MEMBERSHIP (+EQUIPACED_SEQUENCE) | hypothesis 读数值序列 | ✅ |
| 4 | heading relationship | TEXT | PAGE_TOP RegionFact + style_signature 对比 (STYLE_CONTRAST 已在 P7.1) | hypothesis 判读 | ✅ |
| 5 | paragraph sentence boundary | TEXT | ADJACENT_READING_ORDER + content | **hypothesis 侧词法** (句读分析不入层) | ✅ |
| 6 | two-column layout | TEXT | COLUMN_REGION (P6) + ALIGNED_X 组 | hypothesis 判读 | ✅ |
| 7 | document title / section number | TEXT | PAGE_TOP + style + content | hypothesis 词法 (编号模式) | ✅ |
| 8 | image-contained text | IMAGE_ATOM | — (presence 可表达) | **content 不可达 — 外部模态， 显式声明边界** | ⚠️ presence ✅ / content ❌ (诚实边界， 非 schema 缺陷) |

**8/8 可表达** (case 8 内容级显式不可达)， **零新增语义字段， 零 schema 膨胀**。

---

## 7. 架构位置 (§八 — 按冻结边界做工程判断)

| 判据 | Option A: Doc→Atom→CandidateSpan | Option B: Doc→CandidateSpan→Atom | **Option C: 并行 (选定)** |
|------|----------------------------------|----------------------------------|--------------------------|
| information preservation | 最高 (但需改 P4 输入契约) | **差** — 若只标注候选， pre-merge 原子不进层； 若重推导则等于 C | **高** — 同源 P1 确定性重放 + IMAGE 原子 + 按需关系 |
| backward compatibility | **破坏** — P4/CandidateSpan 契约变更 | 兼容 | **完全兼容** — 冻结路径零接触 |
| frozen impact | **修改 Frozen = 禁止** | 无 (但诱导"候选标注层"歧路) | **无** |
| experiment isolation | 差 (观测层改动波及候选) | 中 (层随候选版本漂移) | **好** — 层驻留实验侧 (tmp/perception/atomic_observation/, roadmap 阶段 1 指定路径) |
| reuse | 高 (但以冻结风险为代价) | 中 (仅候选上下文可复用) | **高** — 任意 hypothesis 查询同一层 |
| implementation cost | 高 (含冻结变更审批) | 中 | 中 (P1 只读复用 + IMAGE 原子 + 4 个关系函数 + 查询接口) |
| semantic leakage risk | 中 (层进入决策上游， 压力增大) | 中 (候选语义回流) | **最低** — 层无决策路径可达 |

**选定: Option C (并行)** [INFERRED — 工程判断: 在 "CandidateSpan frozen contract 不可修改"
的硬边界下， A 直接违宪， B 造成表示断层与耦合， C 是唯一同时满足信息保全/冻结隔离/复用的位置]。
P1 的确定性 (同 PDF 重放同原子) 是 C 的正确性基础 [OBSERVED: P1 为确定性提取层]。

---

## 8. Human Feedback → Machine Improvement 对接点 (§九)

```text
Human Validation (P7.2, 1-click boundary judgment, 不变)
  → disagreement / boundary issue (既有 artifact 的只读分析, Phase 1 已验证可行)
  → machine-observable hypothesis (人只给语义判断; 缺口定位由机器交叉推导)
  → hypothesis DECLARED required observables (原子类 + 关系类型)
  → Atomic Observation Layer 查询 (确定性, 版本化)
  → controlled experiment (预注册协议 → GT → 评估)
```

Human **不**填写: reason_category / technical diagnosis / detector selection / feature selection。
Human **只**提供: 最终语义判断 / boundary judgment。 [Human Effort Budget = 1-click, 不变]
[OBSERVED 基础: Phase 1 已证明 reason 可由机器从已有 context 交叉推断 (≥95.6%)]

---

## 9. 未来 Experiment Contract (§十)

```text
Hypothesis (预注册)
  → declares: 所需 Atom kinds + Relation types + 自带词法/统计解释规则
  → observer (实验侧): 只读查询 Atomic Observation Layer
  → produces: experimental observation (纯信息 — 禁止 MERGE/KEEP/REJECT/score)
  → pre-registered decision protocol (独立层, GT 前冻结)
  → Human GT (1-click) → evaluation → gates → decision
```

**硬规则**:
1. Hypothesis **不得**修改 Atomic Observation (schema/relation 闭集/参数)。
2. 若 hypothesis 需要新关系类型 → **层版本升级** (v2→v3), 走治理审批， 且必须在 GT 冻结前完成 —
   严禁 seeing-results 后扩层。
3. Layer 不得输出任何 decision 词汇； observer 与 protocol 分层 (IS-11/IS-14 已实践的结构)。
4. 每次 hypothesis 声明与层版本 hash 一并写入实验 provenance。

---

## 10. 抗过度设计测试 (§十一)

| Test | 设计 | 结果 |
|------|------|------|
| **A. IS-14 Specificity** — 删除所有 figure/caption/axis 词汇后是否仍成立? | Schema 无任何此类词； 原语 = 原子+几何/集合关系 | **PASS** |
| **B. IS-11 Reuse** — 能否无需 TableCellObservation 表达 table context? | TEXT 原子 + IN_REGION(冻结 detector RegionFact) + SAME_LINE/ALIGNED_X — 无新类 | **PASS** |
| **C. Unknown Future Hypothesis** — 新 IS-XX 能否只读既有 observables? | 闭集原语覆盖 §6.2 八类； 词法在 hypothesis 侧； 只有真正的新几何关系才触发层版本升级 | **PASS** (带版本治理边界) |
| **D. Semantic Leakage** — 是否有字段偷偹表达"这是什么"? | kind=TEXT/IMAGE 是物理事实； RegionFact 以 detector provenance 命名 (非语义角色)； 无 is_*/score/role | **PASS** (RegionFact 命名规则为显式防线) |
| **E. Frozen Compatibility** — 实现是否必须改 Frozen? | 并行层 + P1 只读复用 + IMAGE 原子在实验侧提取 → **零 Frozen 修改**； 若未来晋升进主管线 → roadmap 阶段 5-6 promotion/unfreeze gates (**FUTURE PROMOTION REQUIRED** 标记于此， 本设计不提出任何冻结变更) | **PASS** |

---

## 11. DESIGN DECISION (§十二 12 项)

1. **是否值得建立**: **值得** — 但准确定义为 "把已建成 80% 的 P1-P6 事实层补齐暴露接口 + 4 个
   set 级关系 + IMAGE 原子"， 而非新建系统。直接依据: H3 主因 (caption 93.7% 吸收 / OBS-C
   判定与几何错配 / observer 重复解析) 全部指向 "可查询事实层缺位"。
2. **推荐 abstraction**: **Candidate B — Atomic Observation Layer v2 (暴露层 + 最小增量)**。
3. **为什么**: A 不足以支持 region/run 查询 (IS-11/IS-14 均半残)； C 过度物化且与 P7.1 职责重叠；
   B 是满足 §6.2 八案例的最小充分集， 且通过全部五项抗过度设计测试。
4. **最小 schema**: §6.1 (Atom + RegionFact + 闭集 Relation, lazy 计算， 参数版本化)。
5. **与 CandidateSpan 关系**: 并行 (Option C); CandidateSpan 完全不变； hypothesis 查询原子层
   获得 candidate-pair 之外的上下文。
6. **与 DocumentSpan 关系**: DocumentSpan 在代码中不存在 [OBSERVED] — 若未来引入， 应被定义为
   span/region/hypothesis 的文档级组织视图， 是原子层的**下游消费者**， 不得反向定义原子层。
7. **与 Evidence Admission 关系**: 该组件不存在 [OBSERVED]; ValidatedEvidence (P7.2) 是层外下游；
   层不写任何 validation/evidence 对象。
8. **与 Human Feedback Loop 关系**: §8 — 人 1-click; 层为 "机器找缺失 observable" 提供确定性查询面。
9. **IS-11 复用**: cell 关系 = 原子+region+对齐查询 (Test B); 冻结 IS-11 observer 本身不回改。
10. **IS-14 复用**: caption=原子级间隙查询； tick=UNIFORM_RUN (冻结 OBS-C 不回改， 其限制已被
    明确定性为 observer limitation); image presence=IMAGE_ATOM。
11. **未来未知 hypothesis**: §9 contract — 声明即可查询； 新关系类型走层版本治理。
12. **明确不能进入该 layer**: §6.1 禁止字段全表 + 一切 semantic interpretation (§2.2 末行) +
    decision/selection/routing/ranking/score/confidence/recommendation/execution_plan/
    fallback/retry/override/correction/capability registration/permission (§七清单) +
    词法模式 (正则属 hypothesis) + raster 文本恢复 (外部模态)。

### DESIGN STATUS

```text
╔══════════════════════════════════════════════════════════════╗
║  DESIGN STATUS = DESIGN_SUPPORTED_WITH_LIMITATIONS           ║
╚══════════════════════════════════════════════════════════════╝
```

**Limitations (诚实边界)**:
1. Raster 图内文字内容不可达 (外部模态) — 层只记录 IMAGE presence。
2. Relation 闭集 → 新关系类型需层版本治理 (防 hypothesis 私扩)。
3. P1 的 block 层跨 PyMuPDF 版本不稳定 [OBSERVED: roadmap 阶段 0 结论] → 层必须锚定
   word/span 层 (设计约束)。
4. 关系按需计算 → 复杂查询的确定性依赖参数版本化纪律 (params_hash 全程入 provenance)。
5. 层的实现 (未来) 需按 roadmap 阶段 1 批准启动； 本设计不授权任何实现。

---

## 12. MAP 状态 (§十三)

- **不创建新 MAP 节点。** 本设计的归属节点**已存在**: Perception Roadmap 阶段 1
  (Atomic Observation Layer) / 阶段 2 (Experimental Span Construction) [OBSERVED]。
- 相对 Phase 3 的 MAP GAP 报告更新: "post-BLOCK 诊断节点" 缺口已记录； 本设计落入**既有**
  阶段 1 节点， **无新 GAP**。一处记录性分歧: roadmap 阶段 1 原文提及语义性 RegionObservation
  (表格/图/正文…), 与 P6/P7.1 实践确立的反语义泄漏纪律不一致 — 本设计以 P6 几何区域分类 +
  provenance RegionFact 为准 (设计内裁定， 不修改 roadmap 文档)。

---

## 13. 最终安全声明

```text
PHASE 4 = DESIGN ONLY
RESEARCH OBJECT DESIGN = DESIGN_SUPPORTED_WITH_LIMITATIONS
IMPLEMENTATION = NOT AUTHORIZED
EVALUATION = NOT AUTHORIZED
GT = NOT AUTHORIZED
FROZEN MODIFICATION = NOT AUTHORIZED
P7.3 = NOT AUTHORIZED
PRODUCTION = FALSE
CAPABILITY REGISTRATION = NOT AUTHORIZED
RUNTIME INTEGRATION = NOT AUTHORIZED

NO CODE FILE CREATED
NO EXISTING CODE MODIFIED
NO NEW IS-14 EXPERIMENT
FROZEN BASELINE = INTACT

STOP = TRUE
WAIT FOR EXPLICIT AUTHORIZATION
```
