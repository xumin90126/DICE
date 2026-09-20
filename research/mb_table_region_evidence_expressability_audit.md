# M-B Table Region Evidence Expressability Audit

> 角色: Senior System Engineer + Evidence Quality Researcher。性质: READ-ONLY /
> ANALYSIS-ONLY / EXPRESSABILITY AUDIT。零代码修改、零阈值、零 predicate、零实验、
> 零 GT 修改。唯一问题: **现有冻结 P2/P5 + Atomic Observation evidence 是否足以表达
> vector-table 的 region / row / column / cell-like partition — 从而改善 slicing?**

---

## 0. Gate 继承 (不变)

IMPLEMENTATION=NOT_AUTHORIZED · EXPERIMENT=NOT_AUTHORIZED · GT_MODIFICATION=NONE ·
ATOMIC_OBSERVATION_MODIFICATION=NONE · PERCEPTION_PRODUCTION_MODIFICATION=NONE ·
FROZEN_BASELINE=INTACT · PRODUCTION=FALSE · STOP=TRUE。

## 1. Research Question (RQ-MB)

> 在当前 frozen P2/P5 + Atomic Observation evidence 下, 是否已存在足够
> detector/source-backed geometric facts, 使我们在**不新增 observation measurement**
> 的前提下, 表达 vector-table 的 region / row / column / cell-like structure?

"表达" = 可审计、可重复、非语义化的几何事实推导; 不是猜 table、不是打分、不是
classifier、不是 LLM 看图。

## 2. Evidence Inventory (冻结面实测)

### 2.1 可用面 (OBSERVED, 逐字段核实)

| Evidence | 状态 | 来源/出处 |
|----------|------|-----------|
| TEXT_ATOM bbox/x0/x1/width/height/center_x/center_y | **AVAILABLE** | P1 (atomic_text.py, frozen) → adapter text_atoms |
| single_geometries: same_y_band_members / same_x_band_members | **AVAILABLE** | P2 compute_page_bundle (FULL universe, 无截断) |
| single_geometries: left/right/top/bottom/center_alignment_group | **AVAILABLE** | P2 singles (CC-02 已显微镜实测) |
| spatial_cluster_members / x_projection_overlap_count | **AVAILABLE** | P2 singles |
| frozen pairwise (same_y_band, h_gap, v_gap, direction, x_projection_overlap) | **AVAILABLE** | geometry_engine.compute_pairwise (frozen; 本审计实测调用) |
| y ordering / page-local neighborhood | **AVAILABLE** | bbox + pairwise |
| provenance (source_sha + params_hash + config_snapshot, 逐原子) | **AVAILABLE** | schema 强制 |
| RegionFact (注册检测器 bbox; 禁语义名) | **AVAILABLE** (Case A 面; 本审计对象页无注册 P6 artifact → NO_REGISTERED_ARTIFACT) | adapter.expose_region_facts_case_a |

### 2.2 缺席面 (documented, 非推断)

| Evidence | 状态 | 依据 |
|----------|------|------|
| 线条/矩形几何 (vector drawings) | **ABSENT** | atomic_observation_schema.json `known_limitations[0]`: "vector drawings (page.get_drawings) not covered — same surface limitation as frozen P1 block layer"; NTB 通道 = `get_text("dict")` blocks type≠0 = **仅 raster image blocks** (实测 eff p5/p6/p7/p9/resnet/cs/med 全部 NTB=0; 仅 eff p8 有 12 个 image block) |
| 矢量规则的 text-to-line 关系 | **ABSENT** | 同上 |

⇒ 本审计的 vector tables 按 §七 分类为 **Type C** (无 line/rectangle evidence 可用;
依赖 text alignment + row spacing + column spacing + local rectangular structure)。
PDF 中书tabs 规则线客观存在, 但在任何冻结面上不可见 — 这是 **documented surface
limitation**, 不是本轮新发现, 也不是本机制的承重项 (见 §7)。

## 3. 逐案冻结事实实测 (核心证据)

### 3.1 FP 案例 IS11-AMB-135 (eff p5) — 决定性事实

p5 上有**两个** '4' 原子; 机器评估对 (per CC-02 卡 h_gap=30.02) 为:

```text
a = '4' @ x0=320.35, y=161.95
    frozen left_alignment_group = 10 成员:
    ('i',122.0) ('1',134.8) ('2',143.8) ('3',152.9) ('4',161.95)
    ('5',171.0) ('6',180.1) ('7',189.1) ('8',198.2) ('9',207.2) ('1',263.4)*
    (*263.4 = PH-02 已知的 prose 污染成员)
b = 'MBConv6, k5x5' @ x0=354.14, y=161.95
    frozen left_alignment_group = 6 成员 (算子列, 全部 MBConv6 变体 @x0=354.14)
frozen pairwise(a,b): same_y_band=True, h_gap=30.02, v_gap=0.0, direction=LEFT_OF
```

**Level-2 读法 (全部由 Level-1 事实推导, 零语义)**: a 与 b 属于**不同 x0 对齐结构**
(320.35 vs 354.14, 各自有稳定成员列), 但处于**同一 y-band** (表行); 两列在重叠 y 区间
内**共结构** (见 3.2)。⇒ "same structural region + different local partition"
**完整可表达**。→ IS11-AMB-135 的 suppress 所需证据 (in-region ∧ different-partition)
在冻结事实中**已存在**。

### 3.2 p5 表区多列共结构 (audit-level 枚举, y=118-210)

**12 个 ≥3 成员 x0 列簇**: 行号列 n=10 @320.4 · 算子列 n=7 @354.1 ·
@428.5/432.0/436.3 n=3-6 · @439.7 n=10 ('×' 列) · @447.4 n=11 (resolution 序列) ·
@481.2 n=11 (channels) · @520.7 n=11 (resolution 个位)。多列平行 + same_y_band
交叉 = 行×列局部网格结构**可表达**。

### 3.3 盲页弃权案例 vs 已正确解析案例 (correct-vs-blind 反证, §十二)

| case | doc/page | C 结果 | a 原子冻结事实 | b 原子冻结事实 | pairwise |
|------|----------|--------|----------------|----------------|----------|
| AMB-135 (FP) | eff p5 | MERGE ❌ | lag=10 (行号列) | lag=6 (算子列) | same_band, h=30.02 |
| AMB-130 | eff p5 | ABSTAIN | 'Resolution' lag=3 band=4 | '#Channels' lag=2 band=4 | same_band, h=9.06 |
| AMB-313 | eff p8 | ABSTAIN | 'Test Size' **lag=0** band=3 | '#Classes' lag=1 band=3 | same_band, h=8.44 |
| AMB-262 | eff p7 | ABSTAIN | '41M' lag=8 band=12 | 'EfficientNet-' lag=17 band=12 | **same_y_band=False** (BELOW, v=17.6) |
| AMB-462 | cs p3 | ABSTAIN | 'WGe' lag=1 band=9 | 'Avg.' lag=8 band=9 | same_band, h=11.95 |
| AMB-467 | cs p3 | ABSTAIN | '37.0' **lag=6** band=9 | '60.0' **lag=8** band=9 | same_band, h=11.95 |
| AMB-483 | cs p3 | ABSTAIN | '23.5' lag=7 band=9 | '38.5' lag=6 band=9 | same_band, h=16.24 |
| AMB-505/514 | cs p3 | ABSTAIN | lag=8/6 band=9 | lag=7/8 band=9 | same_band |
| AMB-519 | cs p3 | ABSTAIN | 'facto…' **lag=24 band=1** | 'To embrace…' lag=2 band=1 | same_band (双栏正文!) |
| **AMB-346** | **eff p9** | **KEEP ✅** | '83.95' **lag=4 band=8** | '84.26' lag=4 band=8 | same_band, h=8.42 |
| **AMB-350** | **eff p9** | **KEEP ✅** | '80.16' lag=3 band=9 | '81.72' lag=3 band=9 | same_band, h=8.43 |
| **AMB-024** | **resnet p6** | **KEEP ✅** | '28.54' lag=8 band=2 | '10.02' lag=0 band=2 | same_band, h=24.98 |
| **AMB-034** | **resnet p6** | **KEEP ✅** | '21.59' lag=6 band=2 | '5.71' lag=9 band=2 | v=15.54 (不同带) |
| **AMB-005** | **resnet p1** | **KEEP ✅** | lag=30 band=2 | lag=2 band=2 | same_band (跨栏!) |
| **AMB-074** | **resnet p8** | **KEEP ✅** | '41.5' lag=1 band=8 | '21.2' lag=2 band=8 | same_band, h=45.64 |
| **AMB-522/530** | **cs p4/p5** | **KEEP ✅** | lag=2-4 band=3-7 | lag=1-4 band=3-7 | same_band |

**决定性对比结论 [OBSERVED]**: 已正确解析案例 (eff p9, resnet p1/6/8, cs p4/5) 与
盲区弃权案例 (cs p3 数值对, eff p5) 在 Level-1 冻结事实的**结构类完全相同** —
同为 "same_y_band + 两侧各有 ≥1 个有成员的对齐组"。**两组之间不存在 evidence 层面
的可观察差异**; 差异完全发生在 TLD 内部 (其输入是 `rebuild_page_lines` 文本视觉行 +
`_VALUE_RE` 实验室单位词法 + ≥3 片段/70% 列稳定等启发式 — 与观测层无关的
chunker 侧消费者)。⇒ M-B 的失效不在 evidence 不存在, 而在**无人查询它**。

### 3.4 逐案 M-B 可达性修正 (对 impact ranking 的双口径披露)

impact ranking 沿用 machine eval 报告 §9 的归因 ("5 eff + 3 cs"); 逐案 C 决策实测:
18 例 C 弃权 = **eff 3** (130 p5, 262 p7, 313 p8) + med 8 + **cs 7 (全 p3)**。按本审计
逐案事实重新划入 M-B 范围:

- **DIRECT (8)**: AMB-135 (FP, 同带不同列分区, suppress 证据在), AMB-130 (表头行, 弱列
  成员但同带+区域), AMB-313 (同上), AMB-457/462/467/483/505/514 中数值与表头对
  (lag 6-8 + band 9) — 即 **6 cs p3 案例全部 DIRECT**;
- **OUT of M-B scope (2)**: AMB-262 (same_y_band=**False**, 非同带对, cell-context
  路线不适用 → 属竖邻/其他机制), AMB-519 (双栏正文对, band=1, 无列结构 → CC-04
  列盲 band 机制, 非表格);
- med 8 例: 无表格页 (正确盲), 属 M-A (caption 2) / M-H / M-F 范围。

⇒ M-B DIRECT = **8 例** (含 FP), 比 impact ranking 的 6 估计更准确且更强。

## 4. 逐页分析表 (§六 — 12 页)

| Field | eff p5 | eff p6 | eff p7 | eff p8 | eff p9* | res p1* | res p6* | res p8* | cs p3 | cs p4* | cs p5* | med p20† |
|-------|--------|--------|--------|--------|---------|---------|---------|---------|-------|--------|--------|----------|
| known_failure | FP+abstain | no abstain | abstain(不同带) | abstain | no (control) | no | no | no | 7 abstains | no | no | caption(M-A) |
| frozen_geometry_available | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| bbox_available | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| x_structure_available | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| y_structure_available | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| horizontal_relation_available | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| vertical_relation_available | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| line_geometry_available | **no** | **no** | **no** | **no** | no | no | no | no | no | no | no | no |
| rectangle_geometry_available | **no** | **no** | **no** | **no** | no | no | no | no | no | no | no | no |
| text_geometry_relation | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| repeated_x_structure | **yes** (12 列簇) | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | no |
| repeated_y_structure | yes (bands) | yes | yes | yes | yes | yes | yes | yes | yes (band=9) | yes | yes | no |
| local_neighborhood | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| provenance | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| sufficient_for_region | **yes** | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | no (非表) |
| sufficient_for_row | **yes** | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | no |
| sufficient_for_column | **yes** | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | no |
| sufficient_for_cell_partition | **yes** (FP 对) | partial (无失败案例验证) | partial (AMB-262 非同带) | partial (表头 lag 0-1) | yes | yes | yes | yes | **yes** (6/7; 519 非表) | yes | yes | n/a |
| missing_measurement | 无 (参数待预注册) | 同左 | 同左 | 同左 | — | — | — | — | 同左 | — | — | — |

\* control (IS-11 已正确解析)。† 非 表格对照 (NTB=0, 无多列共结构 → 非表性可观察)。

## 5. 五个结构问题 (§八)

- **M-B1 Region Boundary**: yes — 区域 = 共结构列簇的成员 bbox 并集 (x-extent ×
  y-extent), 带逐原子 provenance; 是边界/范围 + 出处, 不是 score。
- **M-B2 Row Structure**: yes — same_y_band (冻结) + band 内成员序列; geometry-derived,
  deterministic, auditable。
- **M-B3 Column Structure**: yes — left_alignment_group / x0 簇 (冻结); 只表达
  structural column segment, 不命名 row_number_column。
- **M-B4 Cell Partition**: yes (FP 对实测) — same band ∩ 不同列组 = 不同局部分区;
  "same region + different partition" 完整可表达。表头行对 (lag 0-3) = partial
  (依赖 band + 区域上下文, 列成员弱)。
- **M-B5 Non-table Exclusion**: 差异**可观察** (不设计规则, 只判可观察性):
  - 双栏正文 margin 组 (lag=24-30, 实测 res p1/cs p3): band_n=1-2, 片段宽且宽度方差大
    → 与表列 (band 交叉多列 + 短 cell 片段) 可区分 — **可观察**; 但这正是 PH-02 的
    whole-group 陷阱所在 (见 §6), 必须以局部分区而非整组表达;
  - code line numbers (LLaMA p19/p22): 单列 + sib=0, 无平行列共结构 → **可观察**;
  - axis ticks: 单列堆 (sib 0-1) → **可观察**;
  - reference numbers: 单列 + 长散文右邻, 无第二稳定列 → **可观察**;
  - **TOC (最难)**: 3 个 x-zone (节号/标题+点列/页码) 共结构存在 → 点列 x-center 不稳 +
    标题片段宽度变异大, 差异仍可观察但**最接近混淆边界** — 记录为 hardest case,
    正式排除属实验侧预注册事项;
  - aligned numeric value columns (resnet p6 '21.59' 型): 与表列**同构** — Level 2
    **不区分** value column 与 row-index column (设计上就不区分; 角色语义在
    experiment/人工层)。

## 6. Research-Object Mismatch 检查 (§九) — 风险真实, 中间层可构造

**陷阱确认**: 整页左边距组 (lag=24-30) 在普通正文上同样存在 (实测 res p1 AMB-005
lag=30, cs p3 AMB-519 lag=24) — "frozen geometry group → 直接当 table" 会立刻把
正文当表格。这与 PH-02 的 whole-group 失败**同构**。

**自然中间层 (Level 2, 可由 Level-1 事实构造)**:

```text
Geometry Facts (bbox / x0 / center / band / alignment group / pairwise — 冻结)
        ↓  共结构: ≥2 个不同 x0 对齐结构 + 重叠 y 区间 + same_y_band 交叉
Structurally coherent local region (成员 bbox 并集 = boundary + provenance)
        ↓  局部化: band ∩ 列组 的交叠分区 (非整组!)
Cell-like local partition → cell-context 证据 (in-region ∧ same/different partition)
```

关键区别: 决策对象是**局部 (band ∩ column) 交叠分区**, 不是整个 alignment group —
'4' 的列成员资格只是分区归属事实, 不再充当 whole-group 研究对象。⇒ **不存在阻塞性
RESEARCH_OBJECT_GAP**; 中间层可构造, 但其聚合参数 (成组/成带/成区容差与最小成员数)
= **MISSING_PARAMETER, 属实验侧预注册, 不是新观测** (本审计不定值)。

## 7. 三种 Gap 的严格区分 (Q2 前置)

| Gap 类型 | 判定 | 依据 |
|----------|------|------|
| **Observation Gap** | 存在但**非承重** | vector drawings 不在任何冻结面 (documented limitation); 但 M-B 核心机制是 text-alignment 结构 (Type C), 已证可表达; 线几何属可选增强面, **不提出 request** |
| **Research-Object Gap** | 风险真实, **可构造** | whole-group 陷阱实测存在; 局部 (band∩column) 中间层可由冻结事实构造 → 非阻塞 |
| **Consumer/Integration Gap** | **PRIMARY (主失效点)** | IS-11 消费者接的是 TLD (chunker 启发式: 视觉行重建 + `_VALUE_RE` 实验室单位词法 + 片段数/列稳定阈值), **不是观测层**; 无任何消费者查询冻结 P2 结构事实; correct-vs-blind 对比证明盲页上证据**齐全且与已解析页同类** |

## 8. Evidence Sufficiency Matrix (§十三)

| Evidence | Correct Table (eff p9, res p1/6/8, cs p4/5) | Vector Blind Table (eff p5/p7/p8, cs p3) | Non-table Negative (med p20, LLaMA code, 2309 ref) |
|----------|---------------------------------------------|------------------------------------------|-----------------------------------------------------|
| bbox | AVAILABLE | AVAILABLE | AVAILABLE |
| x0/x1/center | AVAILABLE | AVAILABLE | AVAILABLE |
| y ordering | AVAILABLE | AVAILABLE | AVAILABLE |
| horizontal relation | AVAILABLE | AVAILABLE | AVAILABLE |
| vertical relation | AVAILABLE | AVAILABLE | AVAILABLE |
| repeated x | AVAILABLE (列簇) | **AVAILABLE (12 列簇 @p5; lag 6-8 @cs p3)** | AVAILABLE (但单列/margin: 无多列共结构) |
| repeated y | AVAILABLE (band) | AVAILABLE | PARTIAL (band_n=1-2) |
| line geometry | ABSENT (TLD 未用 drawings) | **ABSENT** | ABSENT |
| rectangle geometry | ABSENT | **ABSENT** | ABSENT |
| text-geometry relation | AVAILABLE | AVAILABLE | AVAILABLE |
| local neighborhood | AVAILABLE | AVAILABLE | AVAILABLE |
| provenance | AVAILABLE | AVAILABLE | AVAILABLE |

**读法**: Correct 与 Vector Blind 两列**无差异**; 差异只在 Non-table Negative 的
repeated-x/repeated-y 形态 (单列 vs 多列共结构) — 这正是 Level-2 可观察的排除信号。

## 9. 总判定 (§十一)

```text
M-B OVERALL VERDICT = EXPRESSIBLE
```

依据: (1) FP 对的 "same region + different partition" 证据在冻结事实中**实测完整**
(lag 10 成员列 + 对端 lag 6 成员列 + same_y_band + h_gap 30.02); (2) 盲页与已解析页
Level-1 事实**无类别差异** (correct-vs-blind 反证); (3) region/row/column/cell-partition
四个 Level-2 对象均可由 Level-1 事实确定性推导; (4) 唯一缺席 (line/rectangle geometry)
为 documented limitation 且非承重; (5) 缺的是聚合**参数** (预注册层) 与**消费者**
(integration 层), 不是观测。

诚实边界: 表头行对的 cell-partition = partial (列成员弱, 依赖 band+区域);
AMB-262 (不同带) 与 AMB-519 (正文) 不在 cell-context 范围; TOC 为最难混淆边界;
value column 与 row-index column 在 Level 2 **不可也不应区分**。

## 10. 系统工程问答 (§十四)

- **Q1 M-B 是否比 PH-02 更接近 root cause?** **YES** — PH-02 攻裁决谓词形态
  (whole-group 对象, 15 组预注册全败); M-B 定位到: 证据**已存在且与成功案例同类**,
  只是消费者 (IS-11→TLD) 从未查询观测层。root cause = integration, 不是 evidence
  短缺, 也不是判据形式。
- **Q2 Gap 类型**: 主 = **Consumer/Integration Gap**; 次 = Research-Object Gap
  (中间层可构造, 陷阱已识别且可避); Observation Gap 真实 (drawings) 但非承重。
- **Q3 最小下一步**: **DESIGN-ONLY** — "minimal Table Region Evidence construction"
  实验设计 (纸面): 用冻结 P2 事实构造局部 (band ∩ column) cell-partition 上下文,
  聚合参数预注册, 以 45-case GT 重放证伪, 以已解析 8/8 为对照回归集。不实现。
- **Q4 新观测?** **无 (NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE)** — 证据已足;
  get_drawings 线几何记录为可选未来面, 不在本机制的最小路径上 (ONE reason: Type C
  路线已闭合)。
- **Q5 直接 slicing 价值**: 把三段证据接起来 — (a) IS11-AMB-135: 其 suppress 所需的
  in-region ∧ different-partition 事实**已存在** (lag 10 列 × lag 6 列 × same_band);
  (b) 8 例 DIRECT 弃权/FP (135, 130, 313, 457, 462, 467, 483, 505, 514 中 8 例;
  262/519 明确划出范围) 可经同一证据路线变为有据决策; (c) 同一决策规则在已检测表格上
  **8/8 正确** (IS-11 实证) — 即把一个已被证明正确的 cell-context 规则的**输入**从
  TLD 盲区换为冻结结构事实: 预期 FP 1→0、C 弃权 18→~10、且已知通道正确率基线 8/8。

## 11. 最终 Gate (§十六)

```text
==================================================
M-B TABLE REGION EVIDENCE EXPRESSABILITY AUDIT
==================================================

RQ:
现有冻结 P2/P5 + Atomic Observation evidence 是否足以表达 vector-table 的
region / row / column / cell-like partition? — 是 (Level 1→2 全链实测闭合)

CASES:
IS11-AMB-135 (FP, 决定性) + AMB-130/313/457/462/467/483/505/514 (DIRECT 8)
+ controls AMB-005/024/034/074/346/350/522/530 (8/8 已正确)
+ 边界 AMB-262 (非同带, OUT) / AMB-519 (正文, OUT); 页: eff p5-p9, res p1/6/8,
cs p3/p4/p5, med p20 (非表对照) — 共 12 页

EXPRESSIBILITY:
EXPRESSIBLE (FP 对 "same region + different partition" 冻结事实实测完整;
correct-vs-blind 无 Level-1 差异; 表头行对 = partial; line/rectangle geometry
缺席为 documented limitation 且非承重)

RESEARCH_OBJECT:
whole-group 陷阱实测存在 (正文 lag 24-30); 自然中间层 = 局部 (band ∩ column)
分区, 可构造, 非阻塞; 聚合参数 = MISSING_PARAMETER (实验侧预注册, 不定值)

OBSERVATION_GAP:
无新增请求 (vector drawings 缺席为 documented, 非 Type C 路线承重项)
NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE

CONSUMER_GAP:
PRIMARY — IS-11 消费者接 TLD (chunker 词法启发式) 而非观测层;
无消费者查询冻结 P2 结构事实; 证据在盲页齐全且与已解析页同类

SLICING_IMPACT:
FP 1→0 (AMB-135 suppress 证据已在) + 8 例 DIRECT 有据决策 +
8/8 已证通道规则基线; C 弃权 18→~10 (估计, 待实验证伪)

OVERALL_VERDICT:
EXPRESSIBLE

NEXT_STEP:
DESIGN-ONLY: minimal Table Region Evidence construction experiment 设计
(预注册参数 + 45-case GT 重放证伪 + 8/8 对照) — 需下一阶段独立授权

IMPLEMENTATION:
NOT AUTHORIZED

EXPERIMENT:
NOT AUTHORIZED

GT:
UNCHANGED

ATOMIC_OBSERVATION:
UNCHANGED

PERCEPTION:
UNCHANGED

FROZEN_BASELINE:
INTACT

PRODUCTION:
FALSE

STOP:
TRUE
==================================================
```
