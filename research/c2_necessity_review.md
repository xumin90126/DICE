# C2 Necessity Review + Positive Coverage Audit

> 阶段: READ / AUDIT / COMPARE / ABLATE-CONCEPTUALLY / ENUMERATE / REPORT。
> 零实现、零实验、零调参、零 GT/冻结修改; 除本文档与配套 JSON 外未新增/修改文件。
> 上游: `candidate_column_segment_research_object_design.md` (C2 = M1-M5, k/R/W/q 待预注册)
> · `ph02_failure_mechanism_review.md` · `failure_case_independence_audit.md`。

---

## 1. 固定状态 (继承, 不变)

PH02 = REJECTED · PH02B = NOT AUTHORIZED · NEW_HYPOTHESIS = PROPOSED ·
DESIGN_STATUS = INSUFFICIENT_COVERAGE · IMPLEMENTATION/EXPERIMENT = NOT AUTHORIZED ·
GT/层/production 修改 = NONE · FROZEN_BASELINE = INTACT · NEW_OBSERVATION = NONE · STOP = TRUE。

C2 定义 (审查对象, 本轮不修改): M1 alignment + M2 vertical continuity + M3 width
homogeneity + M4 grid embedding + M5 right-neighbor coherence; k, R, W, q = TO BE
PREREGISTERED。

## 2. M1–M5 逐项必要性审查

### M1 Alignment

1. **定义性条件** — "column segment" 概念内含 x 方向对齐; 无 M1 则对象不成立 (非辅助证据)。
2. 无 M1: 不成其为 aligned segment — 对象坍缩为"数字集合"。
3. 解决 FP: 任意数字聚集; 定义 FN 面: **右对齐/居中列** (轴刻度典型右对齐) 不入
   left_alignment_group — 本语料刻度簇因等宽而恰有相同 x0 才被枚举捕获, 这是偶然而非保证。
4. 是 — 直接继承冻结 P2 (|Δx0| ≤ 2.0pt), 零新增语义。**预注册决策点**: 对齐参照
   (x0 / center / x1) 必须在 preregistration 中显式选择, 当前定义默认 x0 是未声明的选择。

**Status: NECESSARY_CANDIDATE** · DESIGN_ORIGIN = FROZEN_EVIDENCE_DERIVED

### M2 Vertical Continuity

1. 代表的是**几何连贯** (成员位置连续), 不是语义连贯 — 定义已明确排除值连续
   (PH-02 合约即如此), 无偷换。
2. 排除 MIXED_ARTIFACT 族 (38 簇, dy 断裂/跨结构) — 唯一能排除该族的判据
   (实测: 38 簇 ratio=None 或 >10)。
3. **真实误伤风险**: 分节表格 (节间自然大间隙)、跨页延续、稀疏行距布局会被
   max/min 比值判据切断 — 正例本身未触发 (1..9 完整), 但 n=1 无法估计该风险频率。
4. continuity = **geometry continuity** (dy 序列性质), 非数字序列连续性, 亦非语义连续性
   — 边界干净。

**Status: NECESSARY_CANDIDATE** (附 FN 风险披露) · DESIGN_ORIGIN = MECHANISM_DERIVED
(异构成员机制, 38 簇族级复现, 非单一案例)

### M3 Width Homogeneity

1. 可能区分的理由: 意外对齐常混合不同字宽 token (prose 数字 vs 表格数字);
   排版列倾向等宽。
2. **真实正例宽度天然变化的情况**: 数字位数不同的列 ('7' vs '112' 型) — 本语料
   eff p5 resolution 列 (w_mean 9.64) 即混合位宽; 若按 x0 聚类则隐含等宽, 按其他参照
   则不然 — M3 与 M1 的参照选择耦合, 未被审视。
3. **VALUE_COLUMN 高度同质**: 实测 resnet p6 两簇 w=20.17 (7-9/9 成员完全一致) —
   M3 对"正例 vs 值列"**零区分力**。
4. 混合宽度簇 (如 '112 27.94 28.54', ratio 31.23) 已被 M2 排除 — 抽样检查未发现
   "dy 均匀但宽度异质"的簇实例。

**Status: POSSIBLY_REDUNDANT** (在 M2+M5 在场时无已证独立排除面; 建议降级为辅助
诊断量, 不作为定义性判据) · DESIGN_ORIGIN = NEGATIVE-DRIVEN (弱)

### M4 Grid Embedding

1. 当前可观察事实: "同页存在 ≥1 个其他 ≥3 成员数值簇, y 范围重叠 ≥50%" —
   纯几何共现关系, 可由冻结输出直接计算。
2. **不是隐藏语义分类器** — 判据不引用 "table" 概念; 但其**动机**是"表格多列"这一
   结构直觉, 动机与可观察量之间有距离, 必须由实验检验填补。
3. 部分是 — 直接诱因是负例中的孤立刻度堆 (med p8 '0 1 2 3 4', sib=0)。
4. **VALUE_COLUMN 普遍满足** grid embedding (cs p3 sib=5, eff p9 sib=7) —
   M4 对"正例 vs 值列"无区分力 (与 M3 同病)。
5. 若移除: sib=0 孤立堆重新入场 (med p8 型; M2 无法排除 — 其 ratio=1.0)。
6. 独立机制证据: **不足** — 反例: med p19 双图平行刻度 (sib=2) 通过 M4 却仍是刻度;
   正例仅 sib=1。M4 的"唯一排除面"真实存在, 但其充分性与必要性均未证。

**Status: USEFUL_BUT_NOT_PROVEN** · DESIGN_ORIGIN = NEGATIVE-DRIVEN

### M5 Right-Neighbor Coherence (重点)

**本轮新增实测 (族级抽查, instrument: 右邻为 >100pt 长 alpha span 的成员占比)**:

| family | 抽样簇 | mean long-alpha rate | 含长散文右邻的簇 |
|--------|-------:|---------------------:|------------------|
| ROW_INDEX_LIKE (GT, 全 10 成员) | 1 | **0.100** | 1 (即其自身污染成员) |
| VALUE_COLUMN | 8 | 0.062 | 1 |
| AXIS_TICK | 8 | 0.000 | 0 |
| DIGIT_GRID | 8 | 0.000 | 0 |
| MIXED_ARTIFACT | 8 | **0.175** | 2 |

四问直答:

1. **是否只在修复 PH-02 那一个 case?** 起源是; 但机制论证独立成立 (表格列成员毗邻
   有界结构 atom, 正文数字毗邻延绵词流), 且族级方向获弱佐证 (MIXED 0.175 最高,
   干净表族 0.0)。
2. 不知道 PH-02 FP 能否独立推出? 能 (上述结构论证), 但**不会被赋予当前这种
   簇级分数形式** — 形式是 case 后见的。
3. 测量的是什么: 邻居 span 宽度 + 词法 + 局部结构关系 — **未做语义 table 分类**
   (无 "is cell" 判定), 语义泄漏低但解释层存在。
4. VALUE_COLUMN 的右邻与行号列类似吗: **是** (cell-like: '60.0'@348 等) — M5 对
   "正例 vs 值列"无区分力 (设计上就不承担此职)。
5. FP/FN 风险: FN 实证 — 含长文本单元格的表 (VALUE 抽样 0.062 ≠ 0) 会被误伤;
   **致命缺陷: 簇级形式下, GT 正例自身 long-alpha rate = 0.1 (其污染成员), 任何
   q < 0.1 都会拒绝唯一正例** — M5 现形式与唯一已知正例不相容。

**M5_STATUS = UNRESOLVED** (起源 CASE_MOTIVATED; 方向获弱族级佐证; 簇级形式存在
与正例不相容的规范缺陷 → 需要**成员级重构**: 先剪除长散文邻接成员, 再对剩余子集
重测 M1-M4 连贯性 — 此为设计修正建议, 本轮不实施) · DESIGN_ORIGIN = CASE_MOTIVATED

## 3. Ablation Matrix (§五 — 概念/数据层面, 未运行 C2)

| Component | Intended role | Evidence supporting necessity | Known counterexample | Risk if removed | Risk if retained | Status |
|-----------|--------------|-------------------------------|----------------------|-----------------|------------------|--------|
| M1 | 定义性对齐条件 | 概念必要; 冻结 2.0pt 直接继承 | 右对齐列 (FN 面, 未在本语料成簇) | 对象坍缩 | 覆盖偏 x0 参照 | NECESSARY_CANDIDATE |
| M2 | 几何连贯 | 38 MIXED 簇全被其排除 (唯一排除面) | 分节/跨页/稀疏表 (FN 风险未量化) | MIXED 族全部入场 | FN 于真实分节结构 | NECESSARY_CANDIDATE |
| M3 | 宽度同质 | 无独立已证排除面 (混合宽度簇已被 M2 排除) | resnet p6 值列 w=20.17 完全同质 (零区分) | 疑似无新增 FP | FN 于混位数列; 假象必要性 | **POSSIBLY_REDUNDANT** |
| M4 | 网格嵌入 | 唯一排除 sib=0 孤立堆的判据 (med p8) | med p19 双图刻度 sib=2 仍通过 (不充分); 单列表 (FN) | 孤立堆重新入场 | 单列表/稀疏图误伤 | USEFUL_BUT_NOT_PROVEN |
| M5 | 右邻连贯 | 族级弱佐证 (0.175 vs 0.0-0.062); 机制论证独立 | **GT 正例自身 0.1 > q** (簇级形式自斥) | prose 污染重新入场 | **拒绝唯一正例** (现形式); 误伤长文本单元格 | **UNRESOLVED** |

**PROVEN 不出现** — 无正式实验, 与 §五 纪律一致。

## 4. Patch-Accumulation 检查 (§六)

| Component | DESIGN_ORIGIN |
|-----------|---------------|
| M1 | FROZEN_EVIDENCE_DERIVED |
| M2 | MECHANISM_DERIVED |
| M3 | NEGATIVE-DRIVEN |
| M4 | NEGATIVE-DRIVEN |
| M5 | CASE_MOTIVATED |

**判定: patch-accumulation 风险真实存在** — 5 个判据中 3 个 (M3/M4/M5) 的来源是
"看负例/看失败案例后加规则", 仅 M1/M2 有对象定义或机制层面的独立根基。缓解因素:
阈值尚未设定 (无 tuning 发生), 且每个 M 都有可观察定义; 但**特征集本身**是在看过
负例后选定的 — 选择偏差必须披露。审查结论 (§七/§十五): M3 应降级, M5 需成员级重构,
重构方向 = **C2′ = M1 + M2 + M4 (定义性) + M5′ (成员级诊断, 非簇级判据)** — 更简单、
语义泄漏更低、过拟合面更小。此为设计修正建议, 本轮不实施、不运行。

## 5. Research-Object 合理性重检 (§七)

| 维度 | C1 (对齐簇) | C2 (M1-M5) | C3′ (简化: M1+M2+M4 + M5′诊断) |
|------|------------|------------|-------------------------------|
| Complexity | 最低 | 高 (5 判据, 3 个弱根基) | 中 (3 定义性 + 1 诊断) |
| Observability | 全可观察 | 全可观察 | 全可观察 |
| Falsifiability | 可 (但判别力≈0: 万物皆 segment) | 可, 但 M5 现形式自斥正例 | 可 |
| Generalizability | 差 | 未证 (n=1) | 同左, 结构更可能迁移 |
| Semantic leakage risk | 低 | 低-中 (M5 解释层) | 更低 |
| Overfitting risk | 低 (但无用) | **中-高 (3/5 弱根基)** | 降低 |

**判定**:

```text
C2 = REQUIRES_REDESIGN
```

依据: 非"明显过拟合"单一致命, 而是 (a) M3 POSSIBLY_REDUNDANT + (b) M5 簇级形式与
唯一正例不相容 (规范缺陷) 两项合计构成必须重设计的证据。重设计方向已明确
(C2′), 且不依赖任何新观测。C2 不是 UNDER-SPECIFIED (M1-M5 均有可观察定义),
不是单纯 OVERFIT-RISK (M1/M2 根基扎实), 不是 TOO COMPLEX (判据数量本身不是问题,
根基才是)。

## 6. Positive Coverage Audit 继续 (§八/§九)

补充只读扫描 (≥2 成员 INT 升序连续簇全扫 + 11 OTHER_INT_STRUCT / 19 AXIS_TICK 人工
复核), 不放宽任何裁决标准:

| candidate | doc/page | values | n | 裁决 | 理由 |
|-----------|----------|--------|---|------|------|
| eff p5 x0≈320.3 | eff p5 | 1..9 (+prose '1') | 10 | **GT_CONFIRMED** | IS11-AMB-135 人类裁决锚定 |
| eff p5 x0=163.2 | eff p5 (同页!) | [2,3] | 2 | REJECTED | n<k; 同页非独立设置 |
| med p8 x0=516.3 | med p8 | [0,1,2,3,4] | 5 | REJECTED | 孤立刻度 (sib=0), 非列结构 |
| med p13 [1,2] / med p17 [4,5] | med | 各 n=2 | 2 | REJECTED | n<k |
| cs p1 [-1,0] / [2,3]; cs p2 [1,2]; cs p3 [2,3] | cs | 各 n=2 | 2 | REJECTED | n<k; 矩阵/图形值上下文 |

**独立设置纪律**: eff p5 x0=163.2 与 GT 正例同页 — 即使通过判据也不构成独立设置。

最终覆盖:

| 指标 | 值 |
|------|-----|
| document_count | **1** |
| page_count | **1** |
| unique_structural_settings | **1** |
| GT_confirmed_positive | **1** |
| manual_candidates | **0** |
| rejected_candidates | **8** |

```text
POSITIVE_COVERAGE = INSUFFICIENT
PREREGISTRATION = NOT READY
EXPERIMENT = NOT AUTHORIZED
```

不通过降低标准解决。(§十一 分支"发现新 GT-confirmed positive"未触发 — 无需更新
对象边界; 唯一说明: 即便未来发现, 同文档/同页/同版式重复不计入独立设置。)

## 7. 八问直答 (§十三)

- **Q1**: 机制驱动 = M1 (定义性/冻结), M2 (异构机制, 38 簇复现); case-driven = M5
  (起源); negative-driven = M3, M4。
- **Q2**: **存在** — 3/5 判据源于负例/单案例; 已通过 DESIGN_ORIGIN 全量披露;
  缓解 = 阈值未设 + 可观察定义, 但特征集选择偏差不可消除, 只能由 redesign 与
  独立语料检验消化。
- **Q3**: 意图上比 C1 合理 (C1 判别力≈0); 但**按现规范** C2 含缺陷 (M5 自斥正例),
  其合理内核 = M1+M2+M4。
- **Q4**: 是, 适度过复杂 — 5 判据中 1 个冗余 (M3) + 1 个需重构 (M5);
  简化为 C2′ (3 定义性 + 1 诊断) 后复杂度问题消除。
- **Q5**: 部分 — 有唯一排除面 (孤立堆) 与可观察定义, 但仅有 negative-driven 论证,
  且已观察到不充分反例 (双图刻度) 与 FN 面 (单列表) → 独立结构性理由**未确立**。
- **Q6**: M5 = 起源 case-motivated, 机制论证独立, 族级佐证**弱** (0.175 vs 0.062
  分离不锐), 且簇级形式被唯一正例证伪 → **UNRESOLVED, 不是 PH-02-specific repair
  但也不是 GENERAL_STRUCTURAL_EVIDENCE**; 需成员级重构后重审。
- **Q7**: **是** — n=1 不变; 8 个补充候选全部 REJECTED (理由记录在案)。
- **Q8**: **否** — 双重阻塞: (a) C2 REQUIRES_REDESIGN (M3 降级 + M5 成员级重构);
  (b) POSITIVE_COVERAGE = INSUFFICIENT。即使完成 (a), (b) 仍独立阻塞。

## 8. 下一步 (§十)

当前最合理的下一步是 **corpus discovery / corpus expansion** (获取含多样表格版式的
新文档, 产生独立 row-index-like 结构设置), 而**不是**继续设计更多 predicate。
C2′ 重设计是纸面工作, 可与语料扩充并行, 但在任何独立正例到位前, 二者都不进入
preregistration。

---

## Governance Gate (§十五)

```text
PH02 = REJECTED
PH02B = NOT AUTHORIZED

C2_DESIGN = REVIEWED
C2 = REQUIRES_REDESIGN (M3 降级 POSSIBLY_REDUNDANT; M5 簇级形式自斥唯一正例 → 成员级重构)
DESIGN_STATUS = INSUFFICIENT_COVERAGE
PREREGISTRATION = NOT READY (阻塞: redesign × coverage 双重)

IMPLEMENTATION = NOT AUTHORIZED
EXPERIMENT = NOT AUTHORIZED
GT_MODIFICATION = NONE
ATOMIC_OBSERVATION_MODIFICATION = NONE
PERCEPTION_PRODUCTION_MODIFICATION = NONE
FROZEN_BASELINE = INTACT
NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE
PRODUCTION = FALSE
STOP = TRUE
```
