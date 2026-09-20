# PH-02 Failure Mechanism Review

> 性质: 对已完成且 REJECTED 的 PH-02 实验的失败机制分析与 Research-Object 重估。
> 本文档只 READ / ANALYZE / CLASSIFY / REPORT。零实现、零重跑、零调参、零文件修改
> (本文档与配套 JSON 除外)。分析中的补充事实均来自**只读层查询** (frozen artifacts)。

---

## 1. Executive Verdict

**PH-02 的失败根因是 Research-Object 层级错误**: 它把一个正确的 **Geometry Fact**
(冻结 `left_alignment_group` = "x0 距 anchor ≤2.0pt 的全部 atom") 直接当作了
**Structural Object** ("这一列") 来消费。该 group 被实测证明天然异构 — 在唯一 FP
案例中它同时包含表格行号列 (i,1..9 @ ~9.05pt) 与**正文句 "Table 1 shows…" 中的数字
token '1'@263.39**。整集等距判据检验的是 group 整体并不拥有的性质, 失败是结构性的,
不是阈值事故。

```text
WHOLE_GROUP_AS_RESEARCH_OBJECT = INVALID
CURRENT_RESEARCH_OBJECT       = UNRESOLVED (A=INVALID; B=REJECTED by specificity;
                                             C=surviving candidate, DESIGN ONLY)
NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE
NEXT_DECISION                 = B (design-only 新 hypothesis 合约, 前置条件已列明)
```

## 2. Frozen Experimental Facts (不可重新解释)

1. A = **0/1** — 触发预注册 `REJECTED: A=0`; 全 15 组参数一致。
2. B = 0 (0/18 与 0/26)。
3. C 双口径已披露: 字面继承型 C = 1/43 (A=0 时未修正的继承 FP 必然计入);
   派生口径 "新引入 MERGE" = 0。
4. D = 0/1。
5. 两个 GT-MERGE 案例 15/15 参数组合均未触发 (geometry-only 口径亦干净)。
6. 13 个 is01_a anchors 中 7 个在部分组合 fire, 全部 fired-unchanged。
7. 负例: never fired 37 / fired-unchanged 7 / fired-changed 0 / collateral 0。
8. 文档级 net improvement = 0 (4 docs 全部)。
9. 15 × 45 完整矩阵已落盘 (`tmp/ph02_column_membership_experiment_results.json`, 468 KB)。
10. 无 post-hoc tuning (`parameter_grid_modified = false`)。
11. Frozen baseline intact (Step 0 门禁 14/14, 程序化读哈希)。

**以上是正式的 REJECTED。不存在 "差一点成功"。**

## 3. Failure Mechanism

### 3.1 失败链 (全部 OBSERVED)

```text
FP anchor '4' (efficientnet p5, x0=320.35)
  ↓ 冻结 left_alignment_group (10 成员, |Δx0|≤2.0pt)
  ├─ 行号列子结构: i@122.0, 1,2,3,5,6,7,8,9 @ y=122–207, dy≈9.05pt, w≈3.77  ← 目标结构
  └─ '1'@y=263.39, w=8.00 — 所属整行: "ble 1 shows the architecture of EfﬁcientNet-B0. Its main"
     (正文句 "Table 1 shows…" 的数字 token; 右邻是散文, 非表格 cell)          ← 异构成员
  ↓ 整集 dy = [9.05 ×8, 56.17]
  ↓ max/min = 6.21 > R_max ∈ {2.0,2.5,3.0}
  ↓ 15/15 组合不 fire → A = 0/1 → REJECTED
```

### 3.2 失败分类 (§4.1 的回答)

| 类别 | 判定 | 证据 |
|------|------|------|
| **B. Research-object mismatch** | **✅ 主根因** | 把 "x0 对齐组" 当作 "column"; group 实测横跨 表格列 + 正文句 两个结构 (3.1) |
| **C. Aggregation-level mismatch** | **✅ 共因** | 整集聚合把异构成员一并纳入判据; 目标性质 (等距) 属于子结构而非整集 |
| **D. Predicate-design failure** | **✅ 表层形式** | 整集等距谓词在异构集上必然脆弱; 但它是 C 的结果, 非独立根因 |
| **E. Threshold sensitivity** | ✗ 非根因 | 失败在全部 15 组一致 (6.21 远超 3.0), 非刀锋阈值; 放宽阈值只会引回特异性失败 |
| **A. Observation insufficiency** | **✗ 不成立** | 所需全部事实 (对齐组、dy、宽度、右邻结构) 均在冻结输出中 — 缺的是正确的聚合单位, 不是测量 |
| **F. Specificity failure** | ⚠️ 次要面 | 7/13 anchors fire 于非行号数值列 (resnet '21.59' 值列 ratio=1.04 近完美等距) — 即使 A=1 也会暴露; 本轮它未直接触发 REJECTED (被 A=0 掩盖) |
| **F. Specificity failure** | ⚠️ 次要面 | 7/13 fire 于非行号数值列 (§6.3); 即使 A=1 也会暴露 |

### 3.3 为什么冻结证据正确而消费层级错误 (必答项)

`left_alignment_group` 的定义是**纯几何等价集**: "与 anchor 的 x0 距离 ≤2.0pt 的全部
atom"。它对以下事实**不做任何承诺**: (1) 成员的垂直范围无界 — '1'@263 与行号列末成员
'9'@207 相距 56pt; (2) x0 对齐是页面上**许多不同结构共享的属性** (栏起点、表格列边界、
正文行首)。因此 group 是一个**候选关系集合 (candidate relation set)**, 而非一个
**结构对象 (structural object)**。冻结几何没有错; 错的是把候选关系集合当作具有结构
同一性的对象来检验"整集等距"这种整体性质。

## 4. Geometry Fact vs Structural Evidence vs Research Object

| 层级 | 本例内容 | 状态 |
|------|---------|------|
| **Geometry Fact** | "\|x0('4') − x0(a)\| ≤ 2.0pt, a ∈ {i,1,2,3,5,6,7,8,9,'1'@263}" | 冻结 P2 输出, **正确** |
| **Structural Evidence** | "存在一个 9 成员、~9.05pt 等距、w≈3.77 的数字子序列" (需**选择子结构**才成立) | 可由冻结坐标推导, 但 PH-02 未做选择 |
| **Research Object** | "这是一个 row-number column" | **语义解释** — 需要连贯性 + 角色证据; PH-02 跳过了中间层直接断言 |

**层级错误 (明确写出)**: PH-02 把 Geometry/alignment group **直接提升**为
Column Membership Object。跳过的正是中间层: 子结构选择 (structural evidence)。
该跃迁在本语料上被一个反例证伪 — group 的第 10 个成员来自正文句。

## 5. Whole-Group Aggregation Analysis

1. **group 是否天然可能包含多个局部结构?** 是 — 实测三例: efficientnet p5 (行号列 +
   正文 token); resnet p6 '28.54' 组 (值列 9 成员, 内含 24pt 异常间隙, ratio 2.01);
   cs_001 p3 '37.0' 组 (值列 7 成员, dy 混合 10.9/16.1pt, ratio 1.49)。
2. **group 定义是否只保证几何接近而不保证结构同质?** 是 — 定义仅有 |Δx0|≤2.0pt,
   无垂直界、无结构约束、无成员同质性约束。
3. **group 是否可能包含多个 semantic/structural objects?** 是 — 行号列与正文数字
   同组即为实证; resnet '28.54' 组内部的 24pt 间隙同样提示组内跨结构。
4. **group-level predicate 是否天然不适合作为 column-membership 判据?**
   是 — 结论:

```text
WHOLE_GROUP_AS_RESEARCH_OBJECT = INVALID
```

理由 (两点, 独立成立): (i) **假阴性面** — 整体性质 (整集等距) 不是该聚合单位的性质,
异构成员一票否决, 目标子结构的存在无法被表达; (ii) **假阳性面** — 即使放宽至
R_max→∞, 整集口径仍会把同页所有 x0-对齐数字 (含完美等距的数值列, 如 resnet '21.59'
组 ratio=1.04) 判为同构 — 特异性不随阈值恢复。即: 该 research object 的失败
**与阈值无关**, 是对象选择错误。

## 6. Local-Equidistance Candidate Analysis

### 6.1 Why it is tempting

FP anchor 的对齐组内实测存在 9 成员最大等距连续段 (dy 全 ≈9.05, 断面数据见
results JSON)。把判据从"整集"改为"局部等距段"即可让该案例 fire — 这是显而易见的
"修复", 也是最危险的诱惑。

### 6.2 Why it is not yet valid

(1) "局部段"的长度下限、断面容差、多段并存时的选择规则全部未定义 — 每一个都是新的
自由度; (2) 它由本轮失败**反向导出** ("让 A 从 0 变 1"), 属于被禁止的
根据结果改假设再验证; (3) 最关键: 它**没有回答 research object 问题** — 局部等距段
仍然只是一个几何子结构, 不是"column", 更不是"row-number column"。

### 6.3 Specificity risk (实测, 非推测)

局部等距结构在语料中**大量存在于非行号结构**:

| 结构 | 实测 | 局部等距段判据行为 |
|------|------|-------------------|
| resnet p6 '21.59' 值列 | 7 成员, w=20.17, dy≈12.05pt, **ratio=1.04** (近完美) | 必然 fire — GT=KEEP, 结构上与行号列几乎不可区分 |
| cs_001 p3 '37.0' 值列 | 7 成员, w=17.44, ratio=1.49 | fire |
| resnet p6 '28.54' 值列 | 9 成员, ratio=2.01 | 宽容差下 fire |

结论: **local equidistance ≠ row-number-column specificity**。正确表述是:

```text
PH-02 failed
  → whole-group aggregation INVALID (本轮已证)
  → local-substructure 是候选 research object (未被证伪也未被证明)
  → 但 local equidistance 有已实测的特异性风险
  → 需要一个全新 hypothesis (对象 = C 类结构段 + 明确负例集)
  → NOT AUTHORIZED (本轮仅登记, 零实现零运行)
```

## 7. Existing Evidence Sufficiency Matrix

基于 frozen artifacts 的逐项判定 (第二列 = 能否**单独**区分 row-number column 与
其他 aligned numeric structure; 第三列 = 是否纯几何):

| Evidence | 已存在? | 单独区分力 | 只是 geometry? |
|----------|--------|-----------|----------------|
| x alignment | ✅ (frozen P2, tol=2.0pt) | AVAILABLE_BUT_INSUFFICIENT — 行号列/值列/正文数字共享该属性 | 是 |
| left_alignment_group | ✅ (frozen) | AVAILABLE_BUT_INSUFFICIENT — 异构 (行号列+正文 token 实测同组) | 是 |
| y spacing (dy) | ✅ (frozen center_y, hypothesis 侧可算) | AVAILABLE_BUT_INSUFFICIENT — '21.59' 值列 ratio 1.04 近完美等距 | 是 |
| local sequence (等距段) | ✅ 可推导 (非冻结输出) | AVAILABLE_BUT_INSUFFICIENT — §6.3 三例反证 | 是 |
| span geometry (宽度) | ✅ (frozen bbox) | AVAILABLE_BUT_INSUFFICIENT 单独不足; **组合线索真实存在**: 行号列 w≈3.77 均一窄 vs 值列 w=17-20 vs 正文 w=8 | 是 |
| region information | ✅ (P6 RegionFact, 层暴露) | AVAILABLE_BUT_INSUFFICIENT — 非语义分类, 只能说"同区域" | 是 |
| style evidence | ✅ (P3 / same_style 字段) | AVAILABLE_BUT_INSUFFICIENT — 表内同款字体, 无区分 | 是 |
| page context | ✅ (页级 atom 全集) | AVAILABLE_BUT_INSUFFICIENT — 可排页眉 (PH-03 域), 不给列角色 | 是 |
| neighboring structure (右邻) | ✅ (pairwise 可得) | AVAILABLE_BUT_INSUFFICIENT — 行号列右邻=表格 cell (x≈379), 正文 '1' 右邻=散文 — 差异真实存在, 区分力未证 | 是 |
| cross-column relationship | ✅ (pairwise/band 可得) | AVAILABLE_BUT_INSUFFICIENT — 行号列处于多列网格首列 (cs_001 p3 实测 3 个兄弟列), 但"首列性"仍未证为判别性 | 是 |
| **row-number 语义角色** | **NOT AVAILABLE** | 任何冻结输出都不直接表达"这是行号" — 且不应表达 (语义层禁令) | — |

**矩阵结论**: (a) 不存在 observation 缺口 — 全部判别线索都是既有冻结事实的**组合**问题;
(b) 也**不存在已证成的单一判别器** — 每条线索单独都不区分行号列与值列;
(c) "row-number" 语义角色在当前证据下 **NOT AVAILABLE** 且不应成为观测目标。

## 8. Research-Object Reassessment

| 候选 | 定义 | 所需 observable | 冻结证据支持? | 最大 FP 风险 | 可证伪实验? |
|------|------|----------------|---------------|--------------|------------|
| **A. Entire left_alignment_group** | PH-02 实际对象 | 对齐组 + 整集等距 | 支持 (存在) | 异构成员一票否决 (假阴性) + 值列同判 (假阳性) — **已被本轮实验双向证伪** | 已做 → REJECTED |
| **B. Local aligned numeric substructure** | 组内最大等距数字段 | 对齐组 + 局部 dy | 存在 | '21.59' 型近完美等距值列 (ratio 1.04) 必然同判 — 特异性风险已实测 | 可证伪但预期失败倾向明确 |
| **C. Structurally coherent candidate column segment** | 与相邻列呈网格关系、成员宽度/词法同质、垂直连贯的数字段 (几何级对象) | 对齐 + 宽度同质 + 邻列网格 + 垂直连贯 (全部既有事实的组合) | 存在 (组合级) | 判别准则未定义; 且正面案例覆盖 = **1** (全 GT 仅 1 个行号列实例) | 可设计, 但需先扩正面案例 |

```text
CURRENT_RESEARCH_OBJECT = UNRESOLVED
```

判定理由: A 已被证伪; B 被实测特异性证据压制; C 是唯一未被证伪的候选对象, 但其
"结构连贯"判据尚未定义、且 **GT 池内行号列正面实例 n=1** — 在正面案例扩充前,
任何以 C 为对象的新假设都无法获得有统计意义的验证。因此 research object 重估的
诚实终点是 UNRESOLVED + C 为领先候选, 而不是强行宣布 C 成立。

## 9. NEW_OBSERVATION_MEASUREMENT_REQUEST Assessment

```text
NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE
```

依据: §7 矩阵显示区分所需的全部原始事实 (对齐、dy、宽度、右邻、网格兄弟列) 均已在
冻结输出中; 缺口是 (a) hypothesis 侧的组合判据设计, (b) 正面/负例案例覆盖 — 两者都
不是 measurement 缺口。按 §8/§10 纪律 (五条件全不满足: 现有 P1-P6+层可表达、层闭集
足够、非查询问题之外还叠加了对象与覆盖问题), 提出新观测将被拒绝。观测层继续只提供
measurement, 不输出 "这是 row-number column"。

## 10. Generalizability Boundary

- **Observed mechanism (整集聚合无效性 / 对齐组异构性)**: SUPPORTED —
  在 3 个文档 (efficientnet p5, resnet p6, cs_001 p3) 的 anchors 上实测到
  group 异构/跨结构现象; 但全部在 4-doc pool 内。
- **Cross-corpus generalization**: NOT ESTABLISHED — 4 docs / 18 (doc,page) 设置 /
  TCC 集中 (3 docs/10 页) / med_001 过加权 1.86× (independence audit)。
- 纪律: **Frequency ≠ Mechanism ≠ Generalizability** — 机制层面的结论
  (整组对象无效) 不赋予任何跨语料推广; PH-02 的失败不得表述为
  "企业文档普遍存在 X"。

## 11. Recommended Next Decision (Q6)

**选择 B: 基于现有 evidence 设计新 hypothesis (DESIGN ONLY, IMPLEMENTATION NOT AUTHORIZED)**

证据依据: (i) observation 缺口不存在 (§9) → 排除 C; (ii) 机制根因是对象层错误且已有
明确候选对象 (C 类) → 非"无路可走", 不选 A (不继续); (iii) 但 B 的执行必须满足
三个前置条件 (写入未来合约, 缺一不批):
1. **负例集先行**: 把 '21.59' 型等距值列、cs_001 p3 值列、正文数字列为预注册负例;
2. **正面案例扩充**: 从 545-case universe 只读枚举 row-number-like 列实例,
   修复 n=1 正面覆盖问题 — 否则任何结果都只是 denominator-1 复刻;
3. **对象定义先行**: C 类"结构连贯列段"的判据 (宽度同质/网格位置/垂直连贯) 必须在
   合约中形式化并预注册, 禁止引用本轮失败结果反向调参。

## 12. Governance Gate

六问直答:

- **Q1 (为什么失败)**: 判据检验的对象 (整集对齐组) 不具备被判据所要求的性质;
  组实测异构 (行号列 + 正文 token), 整集等距必然被破坏 — 结构性失败, 非阈值事故。
- **Q2 (失败归属)**: Research-object problem (根因) + Aggregation problem (整组聚合)
  + Predicate problem (整集等距形式); **非** observation insufficiency。
- **Q3 (left_alignment_group 有没有错)**: **没有错** — 它如实报告 x0 对齐事实;
  错误发生在消费层级 (geometry fact → structural object 的越级提升)。
- **Q4 (真正的 research object)**: 几何级的 "structurally coherent candidate column
  segment" (C 类); "row-number column" 作为语义角色当前不可证伪 (正面覆盖 n=1,
  语义判据 NOT AVAILABLE), 不应作为直接对象。
- **Q5 (现有证据是否足够支持新最小假设)**: 足以**设计**与**证伪** (全部判别线索已在
  冻结输出中); 不足以**保证成功** (特异性风险已实测 + 正面案例覆盖不足) — 因此
  新假设必须以扩充案例集为前置。
- **Q6 (下一步)**: **B** — design-only 新 hypothesis 合约, 带三项前置条件; 不选 A
  (机制分析给出了可检验的修正路径), 不选 C (无 measurement 缺口)。

```text
╔══════════════════════════════════════════════════════════════════╗
║  PH02_EXPERIMENT = COMPLETE                                      ║
║  PH02_VERDICT = REJECTED                                         ║
║  PH02_FAILURE_REVIEW = COMPLETE                                  ║
║                                                                  ║
║  PH02_IMPLEMENTATION = NOT AUTHORIZED                            ║
║  PH02B = NOT AUTHORIZED                                          ║
║  GT_MODIFICATION = NONE                                          ║
║  ATOMIC_OBSERVATION_MODIFICATION = NONE                          ║
║  PERCEPTION_PRODUCTION_MODIFICATION = NONE                       ║
║  FROZEN_BASELINE = INTACT                                        ║
║  PRODUCTION = FALSE                                              ║
║                                                                  ║
║  NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE                      ║
║  NEW_HYPOTHESIS = PROPOSED (research object C, DESIGN ONLY —     ║
║                             表示研究设计候选, 不表示批准实施)      ║
║  STOP = TRUE                                                     ║
╚══════════════════════════════════════════════════════════════════╝
```
