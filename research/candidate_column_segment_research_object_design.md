# Candidate-Column-Segment — Research Object Design (DESIGN ONLY)

> 阶段: NEW HYPOTHESIS = DESIGN ONLY; IMPLEMENTATION / EXPERIMENT = NOT AUTHORIZED。
> 上游: PH-02 REJECTED → failure mechanism review (whole-group object = INVALID,
> research object = UNRESOLVED, C 类 = 领先候选)。
> 本文档只 READ / ENUMERATE / ADJUDICATE / DESIGN / FORMALIZE / REPORT。零实现、零调参、
> 零重跑; 除本文档与配套 JSON 外未新增/修改任何文件。
> 枚举与裁决全部为 **MANUAL_RULE_ASSISTED, 非 GT** — 明确标注, 不冒充人工标注事实。

---

## 1. Research Question (重定义后)

> 在冻结 geometry / observation evidence 中, 能否识别一个具有内部结构一致性的
> **structurally coherent candidate column segment** (几何级结构单元), 并将其与
> "偶然 x 对齐的数字集合" 区分开?

注意: "row-number column" 是 semantic interpretation, **不是**本对象的目标输出 (§8)。
本阶段允许的合法结论包括 `CANDIDATE_RESEARCH_OBJECT = REJECTED` — 最终判定见 §9/§11。

## 2. 继承的冻结事实

PH02_EXPERIMENT = COMPLETE · PH02_VERDICT = REJECTED · PH02_FAILURE_REVIEW = COMPLETE ·
WHOLE_GROUP_AS_RESEARCH_OBJECT = INVALID · NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE ·
FROZEN_BASELINE = INTACT · 全部 NOT AUTHORIZED 状态继承不变。PH-02 的结果不做任何
重新调参、重新解释或修改。

---

## 3. 第一前置: Negative Structure Set (§四)

**枚举方法 (enumeration instrument, 非 hypothesis threshold)**: 在 545-universe 的
39 个 (doc,page) 设置上, 用冻结 P2 输出枚举数值 atom 的 x0 单链聚类
(|Δx0| ≤ 2.0pt = 冻结 alignment_tolerance), 取 ≥3 数值成员的簇 → **138 个簇**。
词法分类 (INT/DEC/NONNUM) 为 hypothesis 侧只读工具。规则辅助裁决 + 人工复核逐簇名单。

### 3.1 裁决分布 (138 簇, 4 docs / 38 pages)

| family | 簇数 | 语义(裁决性描述) | 与 row-number 的关系 |
|--------|-----:|------------------|----------------------|
| VALUE_COLUMN | 46 | 数值/百分比数据列 (decimal, w≈15-22) | **负例主力**: 对齐+近等距+网格嵌入, 但非行号 |
| AXIS_TICK | 19 | 图表 y 轴刻度列 (单调降序/倍频) | 负例: 对齐+近等距, 非行号 |
| DIGIT_GRID | 23 | 图示/矩阵数字网格 (w≤6) | 负例: 对齐+窄, 非行号 |
| MIXED_ARTIFACT | 38 | 跨结构混合簇 (含年代/正文数字, dy 断裂) | 负例: PH-02 失败机制的族级形态 |
| OTHER_INT_STRUCT | 11 | 其他整数结构 (重复计数等) | 负例 |
| **ROW_INDEX_LIKE** | **1** | 行号列 | **正例: 仅 1 个** |

### 3.2 负例代表记录 (每族)

```text
NEG-01  candidate_id: NEG-VAL-RESNET-P6-199.5
        document_id: is11_resnet  page: 6
        text_values: 21.59 21.99 21.84 21.53 20.74 19.87 19.38
        x: x0=199.5 (单链簇)   y: 310.4–383.1   spacing: dy≈12.05pt
        width: w=20.17 (7/7 一致)
        left_alignment_group: 同簇 (冻结口径)   local_context: 表格数据区
        right_neighbor_context: '5.71'@x254 等 (同表兄弟列, cell-like)
        region_context: 表格区域 (P6 可表达)
        GT_if_available: GT 池锚点 '21.59'/'5.71' 对 = KEEP_SEPARATE (人类裁决)
        manual_adjudication: VALUE_COLUMN (非行号)
        negative_reason: 近完美等距 + 对齐 + 数字, 但为数据值列 —
                         "局部高度等距 + numeric + x alignment ≠ row-number column"

NEG-02  NEG-VAL-CS001-P3-310.8: '37.0 35.1 38.5 …' ×7, w=17.44, ratio=1.49,
        grid_siblings=5 (同表 7 个平行值列 @x239-431) — 网格嵌入的纯值列族

NEG-03  NEG-TICK-MED-P19-96.9: '34 32 30 28 26 24 …' ×12 (双图平行刻度, sib=2),
        单调降序; NEG-TICK-MED-P14-142.0 '2.0 1.8 1.6 …' ratio=3.85 — 刻度族

NEG-04  NEG-GRID-RESNET-P5-363.5: '1 3 1 1 3 1 …' ×12, w=3.23 (架构图数字网格, sib=8)

NEG-05  NEG-MIX-EFF-P7-121.8: n=22, ratio=None (dy 断裂), 年代+表格混合 —
        与 PH-02 FP 的 prose-token 污染同族 (整簇不可作为单一结构对象)
```

完整 138 簇记录见配套 JSON (`clusters` 字段, 含 members/dy/width/right-neighbors/
family/adjudication)。**未修改任何 GT 以制造负例**; 涉 GT 的负例 (NEG-01 等) 直接引用
已有人类裁决 (KEEP_SEPARATE)。

---

## 4. 第二前置: 545-Universe 正例枚举 (§五)

在同样的 138 簇框架内按 "row-number / index-like" 裁决 (连续升序小整数 + 窄宽度 +
列形态)。结果:

| 指标 | 值 |
|------|-----|
| document_count (含正例结构) | **1** (is11_efficientnet) |
| page_count | **1** (p5) |
| unique_structural_settings | **1** (x0≈320.3, y≈122–207) |
| positive_candidate_count | **1** |
| GT_confirmed_count | **1** (IS11-AMB-135 的人类裁决 KEEP 锚定该列; 簇级标 GT_CONFIRMED) |
| MANUAL_CANDIDATE (额外) | **0** |
| UNCONFIRMED | **0** |

**唯一正例的形态**: `1 2 3 4 5 6 7 8 9` (升序连续整数, w≈3.77-4.19, dy≈9.05pt) +
1 个异构成员 ('1'@263.39, 正文句 token — PH-02 失败机制的实证)。近似但被排除的候选:
med p8 '0 1 2 3 4' (升序连续但 sib=0 孤立刻度列), eff p5 '1 1 2 2 3 3' (重复非连续),
resnet p5 '112 56 28 14 7 1' (架构参数)。

**结论: positive structural diversity = INSUFFICIENT (n=1 独立结构设置)。**
目标不是放大 n, 而是诚实回答"有多少" — 答案是 1。

---

## 5. 正负例结构对照 (§六)

| Feature | 正例 (row-index 列) | 负例: 值列 | 负例: 刻度列 | 负例: 数字网格 | 负例: 正文数字 | frozen evidence? |
|---------|--------------------|-----------|-------------|----------------|----------------|------------------|
| x alignment | ✓ (2.0pt) | ✓ | ✓ | ✓ | ✓ ('1'@263) | ✅ — **无区分力** (全家族共享) |
| y spacing | 等距 9.05pt | 近等距 (1.04-2.01) | 近等距/阶梯 | 等距 | 无规律 | ✅ — **无区分力** |
| width consistency | 均一窄 (3.77) | 均一宽 (15-22) | 窄 (2.3-10) | 窄 (≤6) | 8.0 | ✅ — 窄度部分区分值列; **不区分**刻度/网格 |
| local continuity | 连续 9 成员 | 连续 | 连续(可跨图重启) | 连续 | 断裂 | ✅ — 排除混合簇, 不排值列/刻度 |
| left/right neighbors | cell-like 短 token ('Conv3x3'@379, '224'@434) | cell-like | 图形区 | 图形区 | **长散文 span (213.6pt)** | ✅ (pairwise/bbox) — **对 prose 污染有区分力** |
| neighboring text type | 表格词法 (模型名/尺寸) | 数值 | 数字 | 数字 | 散文词序列 | ✅ 词法 = hypothesis 侧 |
| region relationship | 表格区 | 表格区 | 图形区 | 图形区 | 正文区 | ✅ P6 — 区分图形/正文 vs 表格, 粗粒度 |
| page context | 表页 | 表页 | 图页 | 图页 | 正文页 | ✅ |
| span structure | 单 token 窄 span | 单 token 宽 span | 单 token | 单 token | 单 token (但邻 span 巨长) | ✅ |
| **升序连续整数词法** | **✓ 1..9** | ✗ (小数) | **降序** (y 轴) | ✗ 重复/非连续 | ✗ | ✅ 词法 (hypothesis 侧) |
| **语义角色 "row-number"** | (人工裁决) | ✗ | ✗ | ✗ | ✗ | **NOT AVAILABLE** (且不应 available — §8) |

**诚实读法**: 单一特征没有任何一项能把正例从全部负例家族中分离; 组合特征
(窄 + 均宽 + 升序连续整数 + 网格嵌入 + 右邻 cell-like) 在**本语料的 1 个正例**上
成立, 但这恰恰只有 n=1 的验证力。对照表的用途是定义"必须测量什么", 不是证明判别力。

---

## 6. 三层定义 (§七 / §八)

**Level 1 — Geometry Fact** (全部冻结输出, 正确且不可更改):
x0 proximity (frozen 2.0pt) · center_y/bbox · horizontal_distance · alignment group 成员。

**Level 2 — Structural Evidence** (对冻结事实的 hypothesis 侧算术, 可复现):
多数值 atom 共享 x0 · 局部 y 间距有界 · 宽度一致 · 垂直连续 · 右邻 token 形态一致 ·
存在平行兄弟列。

**Level 3 — Research Object 候选**: 非循环定义 (M1-M5, 全部可观察/可证伪):

> **Candidate Column Segment** = 页面上数值 atom 的极大子集 S (|S| ≥ k), 满足:
> (M1) 成员两两 x0 距离在冻结 alignment tolerance 内;
> (M2) 垂直连续: 相邻 center_y 差 > 区分度下限, 且 max/min 差比 ≤ R;
> (M3) 宽度同质: max(w)/min(w) ≤ W;
> (M4) 网格嵌入: 同页存在 ≥1 个其他 ≥k 成员数值簇, y 范围与 S 重叠 ≥50%;
> (M5) 右邻连贯: S 成员的最近右邻 (S 外) 中, 长散文型 span (宽度巨大/词流)
>       占比 ≤ q。
>
> k, R, W, q = **TO BE PREREGISTERED** (§十一: 本阶段不设数值阈值; M1 沿用冻结 2.0pt)。

**每一判据的 WHY (§八 强制)**:
- M2: 排除 MIXED_ARTIFACT 族 (38 簇, dy 断裂/跨结构) — 实证: PH-02 FP 的污染成员
  制造 56.17pt 断面。**能区分**: 连贯段 vs 意外对齐混合。**不能**: 区分值列/刻度。
- M3: 排除宽度混层簇 ('112 27.94 28.54' 型)。**不能**: 值列宽度同样均质。
- M4: 排除孤立刻度堆 (med p8 '0 1 2 3 4' sib=0) — 网格嵌入是表格列与图形刻度的
  结构差异。**部分**: 有兄弟的刻度堆 (med p19 双图, sib=2) 仍会通过 → 已知残留风险。
- M5: 排除 prose-digit 污染 — 实测: 行号列右邻为 cell-like 短 token, 正文 '1' 右邻
  为 **213.6pt** 长散文 span (8.9× 于表格词法 span 量级)。**能区分**: 结构段 vs
  正文数字 — 直接封堵 PH-02 的失败机制。
- 明确承认: M1-M5 **没有任何一项** (或其组合) 被证明能区分 row-index 与值列 —
  这不是本对象的目标 (§8)。

**§八 "coherent ≠ equidistant" 直答**: 除了 y-spacing, coherence 还需
宽度同质 (M3) + 网格嵌入 (M4) + 右邻连贯 (M5) + 垂直连续 (M2); 其中 M2/M5 有本语料
实证支持, M3/M4 有方向性证据但判别力未证 — 全部列为"必须测量", 不预设有效。

---

## 7. 候选 Research Object 定义比较 (§十)

| | **C1** locally coherent aligned numeric segment | **C2** = C1 + neighbor/grid coherence (M1-M5) | **C3** = C2 + 升序连续整数词法 |
|---|---|---|---|
| Definition | M1+M2 (+M3) | M1-M5 全集 | M1-M5 + 成员为升序连续小整数 |
| Required observables | 对齐组+dy+宽度 | + 兄弟列 + 右邻宽度/词法 | + 词法序列 (hypothesis 侧) |
| Positive coverage | 1/1 (GT 段通过 M1-M3) | 1/1 (sib=1 ✓, 右邻 cell-like ✓) | 1/1 |
| Negative coverage | 差: 值列/刻度/网格大量通过 → "segment" 泛化到无用 | 中: 排除孤立刻度+prose 混合; **值列/有兄弟刻度仍为合法 segment (按定义正确!)** | 高: 排除值列/降序刻度; 残留: 升序连续刻度 (本语料未见, 未证) |
| Expected FP | 高 | 低 (对"结构段"目标) / 若误用于行号角色则高 | 低-中 |
| Expected FN | 低 | 低 | 中 (缺号>1 断裂) |
| Falsifiability | 可证伪 | 可证伪 | 可证伪 |
| Frozen evidence sufficiency | 足够 | 足够 | 足够 |
| 语义边界 (§十二) | 安全 | **安全 — 推荐锚定** | **漂移风险**: "升序连续整数"开始逼近 row-number 语义角色; 只能作为结构词法特征登记, 不得输出角色判定 |

**选择**: 以 **C2** 为 research object 设计锚 (它修正的是"什么是一个可判断的结构单元",
而非"什么是行号")。C3 降级为未来实验层的角色证据候选, 须独立负例检验。
**NONE OF THE ABOVE 不触发** — C2 形成可证伪定义。

## 8. 语义角色边界 (§十二)

最终假设形式 (设计立场, 非 detector):

```text
Frozen geometry facts
    ↓ [M1-M5 hypothesis-side 测量]
Candidate structural segment (geometry-level unit)
    ↓
Experiment-level / human adjudication (角色判定: row-number? value? tick?)
```

禁止形式: `is_row_number_column = true` 之类 observation 输出。observation layer 只提供
measurement; "row-number" 语义保留在 experiment/人工裁决层。

## 9. 是否需要新 observation (§十三)

```text
NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE
```

M1-M5 的全部输入 (x0/bbox/center_y/词法文本/兄弟簇/右邻 span) 均已在冻结 P1/P2 输出 +
层闭集内; 枚举实测亦全部由既有接口完成。无任何必要 observable 缺失。

## 10. 未来实验的 Falsification Logic (§十四 — 现在定义, 不执行)

若未来 C2 假设进入正式 preregistration + 实验, 以下任一结果 = **REJECTED**:
- **F1 (sensitivity fail)**: 预注册参数下, GT_CONFIRMED 正例段 (eff p5 行号列) 不满足
  M1-M5 之一 — 对象定义连唯一已知正例都无法容纳;
- **F2 (coherence 污染)**: MIXED_ARTIFACT 族 (38 簇) 或 prose-digit 案例 ('Table 1 shows…'
  型) 以超过预注册率的比例通过 M1-M5 — "coherence" 未封堵已知失败机制;
- **F3 (孤立刻度误纳)**: sib=0 的孤立刻度堆通过 M4 — 网格嵌入判据失效;
- **F4 (下游伤害)**: 任何 baseline-correct 判定因使用该对象而改变 (collateral > 0)。

注意: **值列/有兄弟刻度通过 M1-M5 不构成失败** — 它们本来就是合法的 structural
segment (对象定义如此); 把"segment"误读为"row-number"才是错误。
Acceptance thresholds: **TO BE PREREGISTERED**。

## 11. 八问直答 (§十五)

- **Q1**: 是 — C2 对象在聚合前先做子结构选择与连贯性检验, 修正了 whole-group 的
  聚合层级错误; 但它不解决语义角色问题 (也无此目标)。
- **Q2**: 解决 **Aggregation-level mismatch** 与 **Research-object mismatch** 的对象侧:
  geometry fact → structural evidence (选择+连贯) → structural object 的中间层首次被
  形式化 (M1-M5)。
- **Q3**: 对 "true structural segment vs accidental aligned values": **部分** — 实测上
  C2 能排除 prose 污染 (M5, 213.6pt 反证) 与混合簇 (M2) 与孤立刻度 (M4); 但值列/有兄弟
  刻度**本来就该**是 segment (它们不是"accidental") — C2 区分的是"结构段 vs 意外对齐",
  不是"行号 vs 非行号"。
- **Q4**: **能** — '21.59' 族以 VALUE_COLUMN 家族进入正式 negative set (其 GT 锚点
  KEEP_SEPARATE 为人类裁决); 连同刻度族/网格族/混合族共 137 簇。
- **Q5**: **否** — 545-universe 仅 **1 个**独立 row-index-like 结构设置 (GT 确认),
  document/page/setting/candidate/GT-confirmed = 1/1/1/1/1 → **INSUFFICIENT_COVERAGE**。
- **Q6**: 对**设计与证伪基建**: 足够 (M1-M5 全部可测, 负例集丰富); 对**验证**: 不足
  (正面 n=1, statistical power 与 PH-02 同病)。
- **Q7**: **NONE** — 无任何必要 observable 缺失 (§9)。
- **Q8**: **未具备** — preregistration 的三前置中 "正面案例扩充" 未解决 (本阶段只读
  枚举已证明 corpus 内无更多正例; 扩充需要新语料采集, 属新授权范围)。因此本设计以
  INSUFFICIENT_COVERAGE 状态封存, 不进入 preregistration。

## 12. 最终状态 (§十七)

```text
╔══════════════════════════════════════════════════════════════════╗
║  PH02 = REJECTED          PH02B = NOT AUTHORIZED                 ║
║  NEW_HYPOTHESIS = PROPOSED (C2 Candidate Column Segment,         ║
║                             DESIGN ONLY — 非批准实施)             ║
║  DESIGN_STATUS = INSUFFICIENT_COVERAGE                           ║
║  (正例独立结构设置 n=1; preregistration 前置未满足, NOT READY)     ║
║                                                                  ║
║  IMPLEMENTATION = NOT AUTHORIZED                                 ║
║  EXPERIMENT = NOT AUTHORIZED                                     ║
║  GT_MODIFICATION = NONE                                          ║
║  ATOMIC_OBSERVATION_MODIFICATION = NONE                          ║
║  PERCEPTION_PRODUCTION_MODIFICATION = NONE                       ║
║  FROZEN_BASELINE = INTACT                                        ║
║  NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE                      ║
║  PRODUCTION = FALSE                                              ║
║  STOP = TRUE                                                     ║
╚══════════════════════════════════════════════════════════════════╝
```

CANDIDATE_RESEARCH_OBJECT 判定: **未 REJECTED** (C2 形成可证伪非循环定义 M1-M5,
负例集 137 簇就位), 但 **DESIGN_STATUS = INSUFFICIENT_COVERAGE** — 在获得更多独立
正面结构设置之前, 任何基于该对象的实验都不具备最小验证力。
