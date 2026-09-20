# PH-02 Column-Membership Guard — Experiment Contract

> 本文档只定义实验, 不实现任何东西。IMPLEMENTATION = NOT AUTHORIZED。
> 上游: `tmp/document_perception_failure_analysis.md` (CC-02) ·
> `tmp/failure_case_independence_audit.md` (独立性修正: 26 cases = 3 docs/10 页, 非跨文档普遍) ·
> `tmp/atomic_observation_implementation_contract.md` (层 v1, 冻结)。
> 证据标签: **OBSERVED** (artifact/显微镜实测) / **CONTRACT** (本文件定义) / **INFERRED**。

---

## 1. Research Question

> **已有 frozen geometry evidence (P2 `left_alignment_group` 等) 是否足以作为
> column-membership signal, 在 45-case GT replay 中移除已知 false positive
> (IS11-AMB-135: "4"+"MBConv6, k5x5" 被误 MERGE), 同时不伤害任何原本正确的判定?**

这不是"增加新观察对象"的问题 (独立性审计已确认现有观测充分), 而是
"已有证据 + 一个 hypothesis 侧判别谓词能否修复已知错误且无副作用"的问题。

## 2. Hypothesis (正式)

**PH-02 Column-Membership Guard** [CONTRACT]:

> 若某候选对的 text_a 为数字, 且该 atom 与 ≥N 个具有稳定 x 对齐关系的数字邻居构成
> 等距纵向列模式 (column-membership pattern), 则该 pattern 构成"两 fragment 属于
> 表格不同列/不同结构单元"的支持证据, 应**抑制** baseline 的 MERGE 判定 (改为 KEEP_SEPARATE)。

性质声明:
- EXPERIMENT-SIDE HYPOTHESIS — 不是 Observation Schema / Runtime Rule / Capability /
  Frozen Geometry 定义 / semantic label;
- **单向抑制器**: 只能把 MERGE 改为 KEEP_SEPARATE, 永不引入新的 MERGE;
- 显微镜依据 [OBSERVED]: FP 案例 '4' 的冻结 `left_alignment_group` 精确包含
  1,2,3,5,6,7,8 (同 x≈320, 等距 ~9pt) — 判别结构已存在于冻结 P2 输出。

## 3. Scope (研究对象选择 — §十二, 不模糊)

**选择研究对象 A: "row-number-like numeric column 的误判修复"** — guard 仅作用于
baseline 已判 MERGE 的候选对 (作用集), 不对全部文本做列检测。

拒绝研究对象 B ("任何具有 column-membership geometry 的文本"): B 需要系统性负例覆盖,
而当前 corpus 无预留负例集 (NEGATIVE_CASE_COVERAGE = LIMITED, 见 §9) — 选择 B 将迫使
结论超出证据。**防泛化条款**: 本实验禁止产生 "column-membership guard 对所有 PDF 有效"
类表述; guard 的 "列性" 信号本身不区分 行号列/数据列/刻度列 (见 §9/§13), 其安全性
完全来自 "只作用于 baseline-MERGE 候选" 这一有界用法。

## 4. Existing Evidence (全部 OBSERVED)

| 证据 | 内容 |
|------|------|
| 已知 FP | IS11-AMB-135 (efficientnet p5): text_a='4' (IS-01 ✓), text_b='MBConv6, k5x5' (IS-02 ✓) → baseline B 与 C 均判 MERGE; GT=KEEP_SEPARATE。**45 案例中唯一的机器 FP, 也是唯一的 MERGE 判定** |
| 判别几何 | '4' 的冻结 `left_alignment_group` = 10 成员; 数字成员 1,2,3,5,6,7,8 @ x≈320, center_y 等距 ~9pt (122.0→198.2) |
| GT-MERGE 免疫 | 2 个 GT-MERGE 案例 (caption) text_a='FIG. 9:'/'FIG. 12:' → is01_a=False → guard 结构性不可能作用于它们 |
| 触发面 | is01_a=true: 13 案例 (resnet 3 / efficientnet 3 / med_001 3 / cs_001 4); is01_a∧is02_b 双真: 仅 1 (即该 FP) |
| baseline 记录 | B: fp=1, tn=18, abstain=26; C: fp=1, tn=26, abstain=18 (冻结 artifact `is11_machine_evaluation_results.json`) |
| 独立性警示 | pool=4 docs; TCC 26 例 = 3 docs/10 页设置; med_001 过加权 1.86× — 本实验结论仅限 replay corpus (§11) |

## 5. Operational Definition (数学/操作化形式 — §四)

**全部量定义在冻结输出之上; 无一需要新观测。**

| 项 | 定义 |
|----|------|
| **Candidate pair** | 45-case GT pool 中的 (text_a, text_b) 候选 (冻结 artifact 记录, 含 is01_a/is02_b 字段 — 直接采用, 不重算) |
| **Anchor** | 候选对的 text_a atom (其 P1 span-layer atom, 经层 Case A/B 暴露); 仅当 `is01_a == true` 时进入分析 |
| **Neighbor** | 同页 atom 满足: (i) 属于 anchor 的冻结 `left_alignment_group` (P2 冻结输出); (ii) `content` 匹配 NUMERIC_RE_v1 (hypothesis 词法, 见下); (iii) atom_id ≠ anchor |
| **对齐 (alignment)** | **沿用冻结定义, 不重定义**: `left_alignment` = \|x0_a − x0_b\| ≤ alignment_tolerance = **2.0pt** (frozen GeometryConfig) — 即 `left_alignment_group` 的既有成员资格 |
| **等距 (spacing regularity)** | S = {anchor} ∪ neighbors 按 center_y 升序排序; dy_i = cy_{i+1} − cy_i; 要求所有 dy_i > DISTINCTNESS_FLOOR (0.5pt, hypothesis 参数, 排除同行重叠); **regularity = max(dy)/min(dy) ≤ R_max** (比值判据, 相对而非绝对; 绝对行距不作判据) |
| **绝对/相对** | 距离判据全部相对化 (比值); 行距绝对值因版式而异, 不设绝对阈值 |
| **缺号处理** | **值连续性不被检查** (故意的: 值域等差 = 内容解读, 已被架构挑战否决)。1,2,3,5,6,7,8 → dy 全 ≈9pt, ratio≈1.0 ✓。真实缺行 (几何上跳一行) → 单个 dy ≈2× → ratio≈2.0 → 在 R_max∈{2.5,3.0} 下通过, R_max=2.0 下拒绝 — 此敏感性进入参数网格讨论, 不预设 |
| **NUMERIC_RE_v1** (hypothesis 词法, 固定版本) | `^[+-]?\d[\d.,]*\s*%?$` (对 content.strip() 全匹配; '4' ✓, '28.54' ✓, '93.9%' ✓, '0.46M' ✗ — M 后缀视为非纯数字, 从严) |
| **Column-membership fires** | \|S\| ≥ N ∧ 全 dy > 0.5pt ∧ max(dy)/min(dy) ≤ R_max |
| **Guard 判定规则** | IF baseline decision = MERGE ∧ fires → PH02 prediction = **KEEP_SEPARATE**; ELSE prediction = baseline decision (逐字继承, 含 ABSTAIN) |

## 6. Parameter Grid (§五 — 定义待测空间, 不寻优)

**FROZEN 参数 (读取, 不重定义)**:

| 参数 | 值 | 来源 |
|------|-----|------|
| alignment_tolerance | 2.0pt | frozen `geometry_config.py@7ef3629e…` |
| left_alignment_group 定义 | frozen `compute_pairwise` | frozen `geometry_engine.py@388e7939…` |
| y_band / bbox / center | frozen P2 输出 | 同上 (层只读暴露) |

**HYPOTHESIS 参数 (本合约版本化 v1, 与 frozen 严格分离)**:

| 参数 | 网格 | 说明 |
|------|------|------|
| N (最少列成员数, 含 anchor) | **{3, 4, 5, 6, 7}** | 已知案例 S=8 — N 不写死; N=7 为最严档 |
| R_max (等距比值上限) | **{2.0, 2.5, 3.0}** | 2.0 不容忍缺行; 2.5/3.0 容忍单缺行 |
| DISTINCTNESS_FLOOR | 0.5pt (固定) | 仅排除 dy=0 退化 |
| NUMERIC_RE | v1 (固定) | 见 §5; 版本化, 变更 = 合约版本升级 |

网格规模 = 5 × 3 = **15 组参数组合**, 全部预注册; **本阶段不运行、不寻优**;
若未来运行, 报告须给出全部 15 组结果 (不允许只报告最优组)。

## 7. GT Replay Protocol (§六)

**输入 (全部冻结, 只读)**: `is11_machine_evaluation_results.json` (45 案例的 baseline_b /
experimental_c 逐案判定) + `is11_semantic_ground_truth.json` (GT, SHA 锚定) + Atomic
Observation Layer 只读查询 (Case A artifact / Case B 冻结函数, `max_pairwise=None`)。

**Replay = 纯函数**: `ph02_prediction(case_record, layer_observations, params) → prediction`。
确定性: 同输入 → 同输出 (层确定性已验收 53/53)。不重跑冻结 evaluator — baseline 判定
逐字采用冻结记录。

**逐案记录 schema** (45 行, 每参数组合一套):

```text
case_id | document_id | page | baseline_prediction (B 与 C 各一列)
| is01_a | is02_b | anchor_atom_id | aligned_numeric_neighbors (ids + contents)
| set_size | dy_sequence | max_min_ratio | fired (true/false)
| PH02_prediction | GT | changed (true/false)
| change_type ∈ {NONE, MERGE→KEEP, KEEP→MERGE, ABSTAIN→*, *→ABSTAIN}
```

**作用集与观测集分离**:
- **Action set** (prediction 可能改变) = {baseline decision = MERGE} = **1 案例** [OBSERVED];
- **Firing-pattern set** (guard 求值但预测不变) = 全部 45 案例 (重点: 13 个 is01_a=true
  anchor 的 firing 行为 + 2 个 GT-MERGE 案例的免疫验证)。

## 8. Positive Cases

- **正例集 = 作用集本身** (全部 baseline-MERGE 判定, 无挑选空间): n=1 (IS11-AMB-135, B 与 C 各一次)。
- 预期行为 [预注册, 非结果]: '4' 的 S = {1,2,3,4,5,6,7,8}, |S|=8, dy≈9pt 均匀, ratio≈1.0 →
  全部 15 组参数下 fires → PH02 = KEEP_SEPARATE = GT ✓。
- **禁止**为扩大正例集而事后纳入 "看起来像行号列" 的其他案例 (§九原则)。

## 9. Negative Cases

**NEGATIVE_CASE_COVERAGE = LIMITED** (如实声明; 无预留对抗语料)。

池内负例 (44 个 GT=KEEP 案例, 全部进入 firing-pattern 分析, 重点):

| 负例类 | 池内实例 | 预期 |
|--------|---------|------|
| 数值表格相邻 cell (同列数据值) | '82.9%'+'96.2%' (efficientnet p6), '8,144'+'8,041' 等 | guard 可能 fires (真实列) — 无害: baseline 未 MERGE; 记录为 "fires-on-true-column" 数据点 |
| 行号列 FP 自身 | CC-02 | fires → 修正 (这是正例) |
| 正文普通数字 / 句内数值 | PROSE 类 4 例 | 多数不 fires (无对齐列) — fires 与否均记录 |
| 单个数字 / 无足够邻居 | 若干 (N 门槛处理) | 不 fires |
| 数字密集但无稳定 x 对齐 | 表格密集页 (cs_001 p3: 8 案例/页) | 不 fires 或 fires — 逐案记录 |
| **GT-MERGE 对 (必须不fires)** | 'FIG. 9:'/'FIG. 12:' ×2 | **is01_a=False → 结构性免疫; 若任何参数组下 fires = 实现错误** |

**缺失的负例覆盖** (诚实清单): 非表格文档的正文数字列、多栏正文行号引用、假性等距装饰点线、
跨栏数字列。这些在 pool 中不存在 → 结论边界相应受限 (§12)。

## 10. Metrics (§七 — numerator/denominator 显式)

| 指标 | 定义 | 分母状态 |
|------|------|---------|
| **A. Known FP Removal** | \|{c: baseline=MERGE ∧ GT=KEEP ∧ PH02=KEEP}\| / \|{c: baseline=MERGE ∧ GT=KEEP}\| | 分母 = **1** [OBSERVED]; 若为 0 则 NOT COMPUTABLE (实际非 0) |
| **B. Collateral Damage** | \|{c: baseline 正确 ∧ PH02 ≠ baseline ∧ PH02 相对 GT 变错}\| / \|{c: baseline 正确}\| | 分母 = B 路线 19 decided-correct, C 路线 26 (OBSERVED); 结构上应为 0 (单向抑制), 仍须计算验证 |
| **C. New False Positive** | \|{c: GT=KEEP ∧ PH02=MERGE}\| / \|{c: GT=KEEP}\| (=43) | 结构上应为 0 (guard 永不输出 MERGE), 仍须计算验证 |
| **D. Net GT Improvement** | (E_baseline − E_ph02) / E_baseline, 其中 E = \|{c: 非 ABSTAIN 判定 ∧ 判定 ≠ GT}\| | E_baseline(B) = 1, E_baseline(C) = 1 [OBSERVED]; 2 个 GT-MERGE 的 baseline-ABSTAIN 属**既有未决错误**, 不计入 E 也不计入改善 (分母显式排除, 不藏不凑) |
| **S. Signal specificity (描述性)** | 每参数组合下: firing 数 / 13 个 is01_a=true anchor; 及 GT-MERGE 对 firing 数 (须 = 0) | 描述性, 不进 PASS 判定 |

**禁止**: 只报告 A 而不报告 B/C/D; 使用任何未在本节声明的分母。

## 11. Document-level Analysis (§八 — 禁止只报 aggregate)

逐文档表 (4 行, 每参数组合):

```text
document | cases | is01_a anchors | baseline errors | PH02 corrected
| collateral damage | new errors | net change | firing count
```

预注册分析问题: PH-02 的修正 **(1) 单文档特例? (2) 多文档重复机制? (3) 某类文档机制?**
预期形态 [由 §4 事实推断, 非结果]: 修正集中于 efficientnet (FP 所在); 其余 3 文档
0 修正/0 伤害; firing 分布跨 4 文档 (3/3/3/4 anchors)。
**无论结果如何, 禁止声称跨语料泛化** (§11 边界 + 独立性审计: 4-doc pool, FAMILY=UNKNOWN)。

## 12. Success / Failure Criteria (§十 — 事先定义, 不可事后移动)

```text
SUPPORTED            当且仅当: A = 1/1 ∧ B = 0 ∧ C = 0
                     ∧ GT-MERGE 两案例在全部 15 组参数下均不 fires (免疫验证)
                     ∧ 结果对参数稳健: ≥3/5 个 N 值下 (任一 R_max) A=B=C=0 成立
                     ∧ 45 行逐案记录 + 4 文档分解完整产出

PARTIALLY_SUPPORTED  A = 1/1 ∧ B = 0 ∧ C = 0, 但仅 1–2 个 N 值下成立 (刀锋参数) —
                     机制存在但阈值敏感; 或 A = 1/1 仅在 B 路线成立而 C 路线不可用

REJECTED             A = 0 (任何参数组合下 FP 未被移除) 或 B > 0 或 C > 0 (任何伤害)
                     — 特别地: 若 B > 0, 即使 A = 1/1, 仍为 REJECTED
```

**统计力声明 [CONTRACT, 不可删除]**: A 的分母 = 1。因此 **SUPPORTED 的含义是
"在唯一可用的已知 FP 上与假设一致且无任何副作用"**, 不是效应量的统计证明。
任何后续表述必须携带此限定。

## 13. Known Limitations

1. **FP 分母 = 1** — 无统计力; 本实验是机制验证, 不是效果量估计。
2. **NEGATIVE_CASE_COVERAGE = LIMITED** — 池内负例仅 44 个 GT-KEEP 案例, 无对抗性预留集。
3. **4-doc pool + med_001 过加权 1.86×** (独立性审计) — 任何频率/推广表述被禁止。
4. guard 信号 = "列性" 检测, 不区分 行号列/数据列/刻度列 — 安全性完全来自 §3 的有界用法 A;
   若未来有人将其用于 B 用途, 本合约的结论**不**覆盖。
5. 语料全部为矢量图形页 (NTB=0) — 图像型表格/图未覆盖。
6. dy 比值判据对 "多行连续缺失" 的行为未在池内出现 — 留待负例扩充。
7. NUMERIC_RE_v1 从严设计 ('0.46M' 类带单位数字不算纯数字) — 该选择的边界效应进入
   firing 记录, 不在实验中调整。

## 14. Frozen Boundary

| 类别 | 内容 |
|------|------|
| **只读** | GT (SHA 锚定) · `is11_machine_evaluation_results.json` · 层 v1 (7 文件) · P1-P7 冻结代码与 artifact · candidate universe / sampling frame |
| **FROZEN 参数 (读取, 不重定义)** | alignment_tolerance=2.0 · y_band_tolerance=3.0 · `left_alignment_group` 定义 · P2 全部输出 |
| **HYPOTHESIS 参数 (本合约 v1)** | N ∈ {3,4,5,6,7} · R_max ∈ {2.0,2.5,3.0} · DISTINCTNESS_FLOOR=0.5pt · NUMERIC_RE_v1 · sort/比较规则 |
| **禁止** | 新 Observation Measurement · 新 semantic schema · 修改层/冻结/parser/perception · Runtime/Capability/Production · 为结果调参 · 为通过 verifier 修改 verifier |
| **实现位 (未来, 需独立授权)** | 实验侧 replay 脚本 (tmp/ 下), 复用层只读查询; 位置与验收方式沿用层实现授权模式 |

## 15. Implementation Authorization Status

```text
IMPLEMENTATION (PH-02 replay) = NOT AUTHORIZED (本合约 READY 后另行授权)
GT_MODIFICATION = NOT AUTHORIZED
ATOMIC_OBSERVATION_MODIFICATION = NONE
PERCEPTION_CODE_MODIFICATION = NONE
PH-01 = NOT AUTHORIZED
PH-03 = NOT AUTHORIZED
PRODUCTION = FALSE
```

---

## 最终 Gate

可操作化检查: anchor/neighbor/对齐/等距/缺号/参数分离/逐案记录/四指标分子分母/
四文档分解/预注册判定规则 — **全部已严格定义, 无缺失证据项**。

```text
╔══════════════════════════════════════════════════════════════╗
║  PH02_CONTRACT = READY                                       ║
║  (READY ≠ 授权运行; replay 执行需下一次显式授权)               ║
╚══════════════════════════════════════════════════════════════╝

IMPLEMENTATION = NOT AUTHORIZED
GT_MODIFICATION = NOT AUTHORIZED
FROZEN_BASELINE = INTACT
ATOMIC_OBSERVATION_MODIFICATION = NONE
PERCEPTION_CODE_MODIFICATION = NONE
PH03 = NOT AUTHORIZED
PH01 = NOT AUTHORIZED
PRODUCTION = FALSE
STOP = TRUE
```
