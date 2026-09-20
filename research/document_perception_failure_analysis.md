# DICE — Real Corpus Failure Analysis → Document Perception Improvement

> 角色: Senior System Engineer + Document Perception Research Engineer。
> 方法: **Atomic Observation Layer v1 作为显微镜** (只读查询, 零代码修改, 零冻结接触), 对真实
> 语料的真实切片失败进行定位、表征、表达性判定, 并提出最小 Perception Hypothesis。
> 证据标签: **OBSERVED** (artifact/显微镜实测) / **INFERRED** / **NOT ESTABLISHED / NOT YET QUANTIFIED**。

---

## A. Executive Summary

本分析不新增任何 observation / detector / schema。对 45 个真实人工裁决案例
(IS-11 GT, 4 篇真实 PDF)、Phase 1 重复失败模式表、P7.2 calibration records (33 条)、
Phase 3 incident log, 以及 4 次对失败原始页面的 Atomic Observation Layer 显微镜实测
(med_001 p20/p24, efficientnet_001 p5, 1602.03837 p6) 的综合结论:

1. **真实失败高度重复** [OBSERVED]: 45 个案例中 40 (88.9%) 落入 ≥3 case 的重复模式 —
   最大模式 TABLE_CELL_COLUMN n=26 (57.8%)。
2. **三大主簇** [INFERRED]:
   - **空间关联断裂** (caption 过切 — 唯一 MERGE 类 GT 缺口, 层实测 gap 10.5-18.1pt > P4 冻结阈值 8pt);
   - **表格区几何歧义** (cell 对 KEEP 误判 26 例 + 行号列过合并 FP 1 例 + 字距页眉伪表格行);
   - **列盲行推理** (P2 same_y_band 跨双栏混合 — 显微镜实测同一 band 同时含左栏正文与右栏表格)。
3. **全部高价值失败对现有 Observation 可表达 (YES/PARTIAL)** — 无一需要新增 measurement。
   判别性证据 (列对齐成员、同带几何、页顶位置、跨页重复) **已存在于冻结 P1/P2/P5/P7.1 事实中**,
   只是当前证据类从未查询。
4. **NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE**。

---

## B. Failure Inventory (Case Cards)

### CC-01 — Figure caption 过切 (Over-split) ×2

```text
CASE_ID: CC-01a / CC-01b
DOCUMENT_ID: is11_med_001 (2311.15207, sha ead90f6b… ✅ manifest 校验)
PAGE: 20 / 24
FAILURE_TYPE: F2 Over-split (+F5 non-text association)
OBSERVED_CHUNK: "FIG. 9:" 与 "Left:" 为两个互不关联的 candidate; "FIG. 12:" 与
                "Distribution of errors for predictions of entropy…" 同理
EXPECTED_STRUCTURE: 同一图注单元 (label + continuation 一体)
WHY_IT_IS_A_FAILURE: 人工 GT = MERGE (45 案例中唯一的 MERGE 类); 拆断后图注语境丢失,
                downstream evidence 失去 figure 说明主体
VISIBLE_DOCUMENT_EVIDENCE: p20 x=85.04 列首 "FIG. 9:" + x=143.46 "Left:" 同行;
                p24 x=85.04 "FIG. 12:" + x=139.12 长延续句 同行
CURRENT_P1_P6_FACTS: [OBSERVED 显微镜] 两案例均为同 y-band、h_gap=18.11pt (p20) /
                10.47pt (p24)、direction=LEFT_OF; 两者 label 均起始于列首 x=85.04
CURRENT_ATOMIC_OBSERVATIONS: TEXT_ATOM×2 (P1 span layer) + NON_TEXT_BLOCK×0
                (两页均无 image block → 图为矢量, documented limitation)
CURRENT_RELATIONS: 冻结 compute_pairwise: same_y_band=True, h_gap ∈ {18.11, 10.47}
                — 全部 > P4 SpanConfig 8.0 → 未被 P4 合并 → 进入 AMBIGUOUS
RESEARCH_OBJECT: caption label ↔ continuation ↔ graphic zone 的空间关联
EXPRESSIBLE_WITH_CURRENT_OBSERVATION: YES
IF_YES: TEXT_ATOM + 冻结 pairwise (same_y_band + h_gap ∈ (8,50]) + 列首对齐
        (x≈85.04, left_alignment_group) + NTB presence/absence + 页面区域位置 —
        判别结构完整存在, 无需新观测
IF_NO: —
DO_NOT_JUMP_TO: FigureCaptionObservation / is_caption 语义标签 / 新 detector
```

### CC-02 — 表格行号列过合并 (Over-merge, 机器 FP)

```text
CASE_ID: CC-02
DOCUMENT_ID: is11_efficientnet (1905.11946)
PAGE: 5
FAILURE_TYPE: F1 Over-merge (F6 table structure)
OBSERVED_CHUNK: IS-11 评估中 B/C 两条路线对 ("4", "MBConv6, k5x5") 均判 MERGE → FP
EXPECTED_STRUCTURE: KEEP_SEPARATE (GT) — "4" 是表格行号列成员, "MBConv6, k5x5" 是同行
                另一列的 cell, 二者是不同语义单元
WHY_IT_IS_A_FAILURE: IS-01("4" 纯数字)∧IS-02(>2 alpha) 双触发 → MERGE; 唯一机器 FP
VISIBLE_DOCUMENT_EVIDENCE: p5 表格区: 行号列 1,2,3,4,5,6,7,8 @ x≈320, 等距 ~9pt;
                行内容列 (MBConv6, k5x5 / depth: d = αφ …) @ x≈139-182 (左栏) 与 x≈354+ (表格)
CURRENT_P1_P6_FACTS: [OBSERVED 显微镜] '4' bbox=[320.35,158.18,324.12,165.72];
                frozen pairwise('4','MBConv6…') h_gap=30.02, v_gap=0, same_y_band=True
CURRENT_ATOMIC_OBSERVATIONS: TEXT_ATOM ×402 (page 5); NON_TEXT_BLOCK ×0 (矢量表格);
                **决定性事实: '4' 的冻结 left_alignment_group 含 1,2,3,5,6,7,8**
                (10 个成员, y=122…198, 等距 ~9pt — 完整纵向行号列) + same_x_band 16 成员
CURRENT_RELATIONS: same_y_band=True (行内), left_alignment_group (列成员),
                x_projection_overlap=16 — 全部冻结 P2 既有输出
RESEARCH_OBJECT: numeric atom 的"纵向数字列成员资格" vs "同行 cell 邻接"的区分
EXPRESSIBLE_WITH_CURRENT_OBSERVATION: YES
IF_YES: '4' 的列成员资格由冻结 left_alignment_group 完整表达 (7 个数字邻居等距对齐);
        'MBConv6, k5x5' 不在该列; 组合 = 已有 TEXT_ATOM + P2 对齐组 + pairwise —
        判别证据 100% 已存在, 只是 IS-11 证据类 (IS-01/IS-02/geometry) 从未查询它
IF_NO: —
DO_NOT_JUMP_TO: TableObservation / cell 语义标签
```

### CC-03 — 字距拉开页眉 → 伪表格行 (Header contamination)

```text
CASE_ID: CC-03
DOCUMENT_ID: PH3-ASTRO-001 (1602.03837, LIGO, APS 模板)
PAGE: 6 (顶部)
FAILURE_TYPE: F7 Header/footer contamination (→ 假阳性 table 结构)
OBSERVED_CHUNK: Phase 3 incident-2 [OBSERVED]: IS14-AMB-018/019 — 期刊页眉
                "P H Y S I C A L / R E V I E W" 被 line-based detector 判为 table 行
                (cells (0,0)/(0,1)); Phase 3 样本 30/54 in_table 含此类假阳性
EXPECTED_STRUCTURE: 页眉非正文, 不参与表格/正文结构
WHY_IT_IS_A_FAILURE: 页眉进入结构证据 → 污染 table 判定与正文 chunk
VISIBLE_DOCUMENT_EVIDENCE: [OBSERVED 显微镜] p6 顶部 y≈24: 'P H Y S I C A L'
                (x 210.2-275.1) / 'R E V I E W' (x 285.1-335.5) / 'L E T T E R S'
                (x 345.4-401.9) 三个 TEXT_ATOM 同 y-band; 同行还有 'PRL' '116,'
                '061102 (2016)' 'week ending' '12 FEBRUARY 2016'
CURRENT_P1_P6_FACTS: header atoms 位于页面顶部极窄带 (y 21.96-39.56);
                内容呈单字母+空格的 letter-spaced 形态; 此模式跨页重复 (APS 模板每页同位)
CURRENT_ATOMIC_OBSERVATIONS: TEXT_ATOM (P1) + 冻结 band/gap + 页面位置;
                (矢量页眉, NTB=0)
CURRENT_RELATIONS: same_y_band (header 行内) + 跨页重复 (P7.1 REPEATS_ACROSS_PAGES
                关系类型已存在于冻结结构层) + P6 PAGE_TOP_REGION 语义 (区域位置可表达)
RESEARCH_OBJECT: 页面顶部重复性短行的"页眉性"判别
EXPRESSIBLE_WITH_CURRENT_OBSERVATION: YES
IF_YES: 页顶 y 位置 (冻结坐标) + 同型跨页重复 (P2 跨页/P7.1 关系) + letter-spaced
        内容形态 (hypothesis 侧词法) — 判别三元组全部可表达
IF_NO: —
DO_NOT_JUMP_TO: HeaderObservation / 页眉 classifier
```

### CC-04 — same_y_band 跨栏混合 (列盲行推理)

```text
CASE_ID: CC-04
DOCUMENT_ID: is11_efficientnet p5 (与 CC-02 同页同 band)
PAGE: 5
FAILURE_TYPE: F3 Wrong reading order (风险面) / 空间推理列盲
OBSERVED_CHUNK: y≈161.95 的冻结 same_y_band 邻接集同时包含 左栏正文
                ('depth:','d','=','α','φ' @ x=139-182) 与 右栏表格 ('4' @322,
                'MBConv6, k5x5' @379, '56','×','56','40','2' @436-523)
EXPECTED_STRUCTURE: 双栏版式中, 同一水平带 ≠ 同一阅读行; 栏内序列才构成阅读行
WHY_IT_IS_A_FAILURE: 任何以 band 为"行"的推理会把两栏内容混入一个伪行
                (CC-02 的过合并正是在此混和方法下发生)
VISIBLE_DOCUMENT_EVIDENCE: [OBSERVED 显微镜] band 成员 x 呈双簇: 139-182 与 322-523
CURRENT_P1_P6_FACTS: P2 same_y_band (x 无关) + P5 列布局 (column groups, 冻结存在)
CURRENT_ATOMIC_OBSERVATIONS: TEXT_ATOM + P2 band + (P5 列事实, 经 RegionFact 通道可入层)
CURRENT_RELATIONS: band 成员的 x 双簇结构 — 由冻结 center_x 序列直接可判
RESEARCH_OBJECT: band 内列归属区分
EXPRESSIBLE_WITH_CURRENT_OBSERVATION: YES (P5 列组 / x 簇结构)
IF_NO: —
DO_NOT_JUMP_TO: ColumnObservation
```

### CC-05 — 无 IS 覆盖的角色类 (Phase 1 量化, 聚合级 Case Card)

```text
CASE_ID: CC-05 (聚合: 45 案例 + P7.2 calibration 33 条)
DOCUMENT_ID: is11_resnet(9) / is11_efficientnet(18) / is11_med_001(8) / is11_cs_001(10)
FAILURE_TYPE: F4 boundary / F6 / F5 混合 (按角色)
OBSERVED_CHUNK: [OBSERVED Phase 1] TABLE_CELL_COLUMN 26 (57.8%, 全 KEEP) ·
                TABLE_HEADER 7 (15.6%, KEEP) · PROSE_SENTENCE_PARAGRAPH 4 (KEEP) ·
                FIGURE_AXIS_TICK 3 (KEEP) · FIGURE_CAPTION 2 (MERGE) · DIAGRAM_LIST_ITEM 1;
                P7.2 calibration (33 条) 独立重复: TOC entry / reference marker /
                footnote / formula fragment
WHY_IT_IS_A_FAILURE: 这些角色的 boundary 判定目前依赖人工反复 (重复模式 = 系统性缺口)
EXPRESSIBLE_WITH_CURRENT_OBSERVATION:
  TABLE_CELL_COLUMN → YES (CC-02 同构: 对齐列成员 + band; IS-11 observer 已证 13/13 正确)
  TABLE_HEADER      → YES (表格首行位置 + 短文本 + 列对齐 — 已有事实组合)
  FIGURE_AXIS_TICK  → YES (GAP_SEQUENCE 等距 + 小字号 + 数字内容 hypothesis 侧)
  PROSE sentence    → PARTIAL (句读词法在 hypothesis 侧; IS-10=HUMAN_OWNED 冻结, 不重开)
  FIGURE_CAPTION    → YES (CC-01)
  DIAGRAM_LIST_ITEM → PARTIAL (diagram 区域判定依赖矢量检测 — documented limitation)
RESEARCH_OBJECT: 各角色对应的纯几何/内容可观测组合
DO_NOT_JUMP_TO: 语义 role observer
```

### CC-06 — Cross-page continuity

```text
CASE_ID: CC-06
FAILURE_TYPE: F8
状态: NOT YET QUANTIFIED — 当前 GT/case 库全部单页采样, 无跨页案例记录;
     不伪造频率。列为观察空白, 留待未来 corpus 扩展时判定。
```

---

## C. Failure Taxonomy (来自真实语料的聚类)

| Cluster | 包含 | 真实案例 | 机制 |
|---------|------|---------|------|
| **A. 空间关联断裂** | F2/F5 | CC-01 (×2), FIGURE_CAPTION 模式 | P4 冻结 8pt 合并阈值 < 真实图注 label↔continuation 间距 (10.5-18.1pt) → 该间距带 (8,50] 的关联对滞留 AMBIGUOUS 且无关联证据类 |
| **B. 表格区几何歧义** | F1/F6/F7 | CC-02 (FP), TABLE_CELL_COLUMN×26, TABLE_HEADER×7, CC-03 | 行/列/页眉在纯 band 几何下同构; 判别性结构 (对齐列、页顶位置、跨页重复) 存在但未被查询 |
| **C. 列盲行推理** | F3 | CC-04 | P2 same_y_band 与 P5 列结构未联合使用 → 伪行混合 |
| **D. 角色显著性无覆盖** | F4/F5 | FIGURE_AXIS_TICK×3, PROSE×4, DIAGRAM×1, P7.2 patterns | 角色判别所需观测存在, 但无证据类查询 (Phase 1 已量化) |
| **E. 跨页连续性** | F8 | CC-06 | 观察空白 (NOT YET QUANTIFIED) |

共同根因 [INFERRED]: **不是 observation 缺失, 而是"证据查询缺口"** — 冻结 P1-P6 已产出
判别性事实 (对齐组/band/位置/重复), 现有 evidence classes 只查询其中极小子集。

---

## D. Top 3–5 Priorities

| Rank | Failure | Frequency | Evidence Impact | Expressible | Candidate Fix (方向) | Priority |
|------|---------|----------:|----------------:|-------------|----------------------|----------|
| 1 | 表格 cell 对误判 (TABLE_CELL_COLUMN) | 26/45 (OBSERVED) | 高 — 最大重复模式, 直接决定 cell 级 evidence 边界 | YES | 查询对齐列成员 + band (PH-02 同构) | HIGH |
| 2 | Caption 空间关联断裂 (over-split) | 2/45 GT + Phase 3 prevalence 6.08% (OBSERVED) | 高 — 唯一 MERGE 缺口; 图注语境整体丢失 | YES | caption 关联证据类读已有观测 (PH-01) | HIGH |
| 3 | 页眉/页脚污染 (伪表格行) | incident 记录: 30/54 in_table 含 FP (OBSERVED); chunk 级 NOT YET QUANTIFIED | 高 — 系统性污染结构证据 | YES | 页顶位置+跨页重复+形态 三元组信号 (PH-03) | HIGH |
| 4 | 列盲 band 推理 | NOT YET QUANTIFIED (机制已实测) | 中-高 — 影响双栏文档全部行推理 | YES | band × P5 列组 联合查询 | MEDIUM |
| 5 | 跨页连续性 | NOT YET QUANTIFIED (观察空白) | 未知 | PARTIAL | 先补 corpus 案例再判定 | LOW (暂缓) |

优先理由: Rank 1-3 由真实人工裁决/事件记录背书 (非推测), 全部 EXPRESSIBLE=YES
(零新观测即可进入实验), 且候选修复全部**实验侧查询** — Frozen Baseline 零接触。

---

## E. Observation Expressibility Matrix

| Failure | Research Object | Existing Observation | Expressible? |
|---------|----------------|---------------------|--------------|
| CC-01 caption 过切 | label↔continuation↔graphic zone 关联 | TEXT_ATOM + frozen pairwise (same_y_band, h_gap) + 列首对齐 + NTB presence | **YES** |
| CC-02 行号列过合并 | numeric atom 的列成员资格 | left_alignment_group (7 数字邻居) + same_x_band + pairwise | **YES** |
| CC-03 页眉伪行 | 页顶重复短行的页眉性 | 页顶 y + 跨页重复 (P2/P7.1) + letter-spaced 词法 (hypothesis) | **YES** |
| CC-04 跨栏 band 混合 | band 内列归属 | P2 band + P5 column groups + center_x 簇 | **YES** |
| CC-05a TABLE_HEADER | 表格首行角色 | 位置 + 短文本 + 列对齐组合 | **YES** |
| CC-05b AXIS_TICK | 等距数字序列 | GAP_SEQUENCE + 小字号 + 数字词法 (hypothesis) | **YES** |
| CC-05c PROSE 句界 | 句读结构 | 词法信号 (hypothesis 侧); IS-10 冻结 HUMAN_OWNED | PARTIAL |
| CC-05d DIAGRAM | 图示区域 | 矢量检测不在任何 surface — documented limitation | PARTIAL |
| CC-06 跨页连续 | 跨页结构 | P2/P7.1 存在, 但无真实案例校准 | PARTIAL (证据空白) |

**结论: 高价值失败 (Rank 1-4) 全部 YES → 按 §7/§8 纪律, 不允许新增 observation。**

---

## F. Top Hypotheses (最小 Perception Hypotheses)

### PH-01 — Caption Association Evidence

```text
HYPOTHESIS_ID: PH-01
FAILURE: CC-01 (caption label 与 continuation 过切; 关联证据缺失)
RESEARCH_OBJECT: 同 y-band 内 label↔continuation↔graphic-zone 空间关联
OBSERVABLES_REQUIRED: TEXT_ATOM; frozen pairwise (same_y_band, h_gap); 
                      left_alignment (列首对齐); NON_TEXT_BLOCK_ATOM (presence);
                      页面位置
CURRENTLY_AVAILABLE: YES (全部为 v1 层 + 冻结 P1/P2 既有输出)
PROPOSED_PERCEPTION_CHANGE: 实验侧新增 caption-context 证据查询 (读取已有观测;
                      词法模式 "FIG N:" 留在 hypothesis 侧), 用于 candidate evidence —
                      不改 P4, 不改候选生成冻结路径
EXPECTED_EFFECT: 减少 fragmented evidence (图注主体与说明合并为正确关联单元);
                      Phase 3 已证该间距带 prevalence 6.08% (79/1299) — 影响面明确
NEGATIVE_CASE: 同带同行但语义无关的对 (如 "Table 3" 标签 + 表格首行) — 需
                      graphic-zone/位置区分, 预注册负例集
MEASUREMENT: 预注册案例集上的关联判定正确率 vs 人工 GT (未来授权后)
SUCCESS_CRITERION: 关联召回提升且负例 (无关对) 不误关联; 人审 1-click 不变
REGRESSION_RISK: 过度关联 (把无关同行对并入) — 由负例集 + 人审门把守
FROZEN_IMPACT: NONE (实验侧查询; P4/P1-P6 零修改)
IMPLEMENTATION_SCOPE: 实验侧 evidence-query 模块 (tmp/ 下), 需独立授权
```

### PH-02 — Column-Membership Guard (表格 cell 过合并防线)

```text
HYPOTHESIS_ID: PH-02
FAILURE: CC-02 (numeric text_a + alpha text_b 双触发 IS-01∧IS-02 → 误 MERGE)
RESEARCH_OBJECT: numeric atom 的纵向数字列成员资格 (行号列 vs 同行 cell)
OBSERVABLES_REQUIRED: TEXT_ATOM; left_alignment_group; same_x_band;
                      frozen pairwise; (等距性 = hypothesis 侧对 y 序列的计算)
CURRENTLY_AVAILABLE: YES — 显微镜实测: '4' 的 left_alignment_group 完整包含行号列
PROPOSED_PERCEPTION_CHANGE: 实验侧证据类: numeric text_a 若存在 ≥N 个等距对齐的
                      数字邻居 → 列成员信号 → 支持 KEEP (而非 MERGE)
EXPECTED_EFFECT: 消除 IS-11 机器评估唯一 FP (CC-02); 对 26 例 TABLE_CELL_COLUMN
                      KEEP 判定提供正向证据
NEGATIVE_CASE: 真正该 MERGE 的 numeric+alpha 对 (若存在) — GT 中 MERGE 类仅
                      caption 2 例, 无 numeric 案例 → 负例需预注册构造
MEASUREMENT: 45 案例 GT 重放 (未来授权后; 本轮 NOT RUN)
SUCCESS_CRITERION: FP→0 且 TP 不降; abstention 率不升
REGRESSION_RISK: 列信号误触发 (正文中的对齐数字列表) — 由负例集把守
FROZEN_IMPACT: NONE (证据类是实验侧; IS-01/IS-02/IS-11 冻结不回改)
IMPLEMENTATION_SCOPE: 实验侧; 需独立授权
```

### PH-03 — Page-Header Repetition Signal

```text
HYPOTHESIS_ID: PH-03
FAILURE: CC-03 (页眉进入表格/正文结构证据)
RESEARCH_OBJECT: 页面顶部重复短行的"页眉性"
OBSERVABLES_REQUIRED: TEXT_ATOM + 冻结 y 坐标 (页面顶部带); 跨页重复
                      (P2 跨页/P7.1 REPEATS_ACROSS_PAGES); letter-spaced 形态
                      (hypothesis 侧词法)
CURRENTLY_AVAILABLE: YES
PROPOSED_PERCEPTION_CHANGE: 实验侧信号: 页顶带 + 跨页同型重复 → header 信号 →
                      从 table/cell 证据中排除 (支持结构降噪, 不直接删内容)
EXPECTED_EFFECT: 消除 incident-2 类伪表格行 (30/54 样本含 FP 的主要来源之一);
                      减少正文 chunk 页眉污染 (F7)
NEGATIVE_CASE: 首页 masthead / 无页眉文档 / 页眉内含真实内容的版式 — 预注册负例
MEASUREMENT: incident 案例重放 + 负例集 (未来授权后)
SUCCESS_CRITERION: 伪表格行 → 0; 正文 chunk 页眉污染率下降; 无正文误伤
REGRESSION_RISK: 页顶真实内容 (标题/摘要首行) 被误判 — 位置阈值需预注册并经人审
FROZEN_IMPACT: NONE
IMPLEMENTATION_SCOPE: 实验侧; 需独立授权
```

---

## G. New Observation Requests

```text
NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE
```

依据: §E 矩阵中全部高价值失败 (Rank 1-4) EXPRESSIBLE=YES — 判别性证据已存在于冻结
P1/P2/P5/P7.1 事实与 v1 层闭集内。PARTIAL 项 (PROSE 词法 / DIAGRAM 矢量 / 跨页案例)
分别属于: hypothesis 侧词法 (不需层改动)、documented modality limitation、证据空白
(先补案例, 非补观测)。按原则 A 与 §8 五条件, 无一项满足新增门槛。

---

## H. Recommended Next Step (只推荐, 不执行)

1. **首选**: 授权 PH-02 (Column-Membership Guard) 的实验侧实现与 45 案例 GT 重放 —
   最小成本 (已有 GT、已有观测、单一查询谓词)、可证伪、直接消除已知 FP。
2. 次选: PH-01 (caption 关联) — 需先预注册负例集 (graphic-zone 区分), 成本中。
3. 平行准备: 为 Rank 4/5 补真实案例 (双栏 band 混合的 chunk 级量化、跨页连续性案例) —
   把 NOT YET QUANTIFIED 变成可判定的 inventory。
4. 全程保持: Candidate → Human Review → Validated Evidence 链不变 (§13);
   Perception 改善只作用于 candidate generation 证据, 绝不自动产生 validated evidence。

---

## 最终 Gate

```text
FAILURE_ANALYSIS_STATUS = COMPLETE
TOP_FAILURES_IDENTIFIED = 5 (clusters A-D + 观察空白 E)
TOP_PRIORITY_HYPOTHESES = 3 (PH-01 / PH-02 / PH-03, 全部实验侧、零冻结影响)
NEW_OBSERVATION_REQUIRED = NONE
FROZEN_BASELINE = INTACT
CODE_MODIFICATION = NONE (本轮仅只读显微镜查询; 7 个层文件未动)
IS11_EVALUATION = NOT_RUN
IS14_EVALUATION = NOT_RUN
P7.3 = NOT_AUTHORIZED
PRODUCTION = FALSE
NEXT_STEP_AUTHORIZATION = REQUIRED
STOP = TRUE
```
