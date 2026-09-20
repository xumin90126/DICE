# PH-02 Column-Membership Guard — GT Replay Experiment Report

> 授权: 本轮显式 EXPERIMENT EXECUTION AUTHORIZATION (仅 experiment-side replay)。
> 合约: `tmp/ph02_column_membership_experiment_contract.md` (预注册, 运行中零修改 —
> `parameter_grid_modified = false`)。
> 结果: **PH-02 = REJECTED** (预注册规则, 无补救, 无事后调参)。

---

## 1. Step 0 — Frozen Anchor Integrity Gate

期望哈希**全部从权威记录程序化读取** (layer_registry.json frozen_sources ×7 ·
P7.1 manifest ×N · P7.2 manifest ×N · GT SHA 从 is11_human_review_report.md 解析 ·
4 个语料 PDF SHA 从 sampling frame 记录), 逐位比较: **14/14 checks OK** → 实验继续。
(上一轮的 "transcription error" 已通过程序化读取根除。)

## 2. Baseline (先于 PH-02 建立, §五)

45 案例基线逐案保存 (`tmp/ph02_experiment/baseline.json`), 含 case_id / document_id /
page / baseline_prediction (B 与 C) / GT / is01_a / baseline_error_type:

| Baseline | decided | FP | correct-KEEP | abstain | E (decided∧≠GT) |
|----------|--------:|---:|-------------:|--------:|----------------:|
| baseline_b | 19 | 1 (IS11-AMB-135) | 18 | 26 | **1** |
| experimental_c | 27 | 1 (IS11-AMB-135) | 26 | 18 | **1** |

2 个 GT-MERGE 案例 (IS11-AMB-414/422) 两条 baseline 均 ABSTAIN — 既有未决错误,
按合约排除于 E 分母。

## 3. 执行概要

- 层只读构建: 4 docs × 18 unique pages; **45/45 anchors 经 bbox 精确定位**
  (tol 0.01→0.5pt 两级, 无 AMBIGUOUS/NO_MATCH);
- **15/15 参数组合 × 45 案例** 全矩阵记录 (`…results.json`, 468 KB, 15×45 case-level);
- 13 个 is01_a=true anchor 全部分析; GT-MERGE 双例单列核查 (§9)。

## 4. 核心发现 — Guard 为何未生效 (失败机制, 全部 OBSERVED)

对唯一已知 FP 的 anchor ('4' @ efficientnet p5, bbox 精确匹配):

```text
冻结 left_alignment_group (10 成员) 的数字邻居 (9):
  1@134.79  2@143.84  3@152.90  [4=anchor@161.95]  5@171.00
  6@180.06  7@189.11  8@198.16  9@207.22   1@263.39  ← 虚假邻居
dy = [9.05, 9.06, 9.05, 9.05, 9.06, 9.05, 9.05, 9.06, 56.17]
max/min ratio = 56.17 / 9.05 = 6.207  >  R_max 网格上限 3.0
```

行号列本身完美等距 (~9.05pt), 但冻结 x0-对齐组 (tolerance 2.0pt) **额外收录了一个
位于 56pt 之外的 x-对齐数字 '1'** (页面上另一结构中的数字, 恰好与该列左对齐)。
预注册的整集等距判据因此从不满足 → **guard 在全部 15 组参数下均不 fire → A = 0/1**。

显微镜阶段观察的 "1,2,3,5,6,7,8" 是真实子结构, 但合约把判据定义为"整集等距",
而冻结对齐组的成员超出了该子结构 — **合约的判据定义对该真实数据过于脆弱**。
这就是实验要给假设失败机会的意义 (§十八)。

## 5. 四项核心指标 (§八, 15 组全部一致)

| 指标 | baseline_b | experimental_c | 判定 |
|------|-----------|----------------|------|
| **A. Known FP Removal** | **0/1** | **0/1** | ❌ 全 15 组均为 0 |
| **B. Collateral Damage** | 0/18 | 0/26 | ✅ (但 A=0 下无意义) |
| **C. New False Positive** | 字面口径 **1/43** | 字面口径 **1/43** | ⚠️ 见下方口径披露 |
| **D. Net GT Improvement** | 0/1 | 0/1 | 无改善 |

**Metric C 口径披露 (诚实记录, 不影响判定)**: 合约字面定义
`C = |{GT=KEEP ∧ PH02=MERGE}|` 在 **A=0 时必然把未被修正的继承型 baseline FP 计入**
(该案例 PH02 判定 = 继承的 MERGE) → 字面 C = 1。派生描述性口径 (事后, 非预注册):
**新引入 MERGE** (PH02=MERGE ∧ baseline≠MERGE) = **0** (guard 结构上永不引入 MERGE)。
两种口径下 verdict 相同 — A=0 主导。

## 6. GT-MERGE 双例免疫 (§九, 单列核查)

| case_id | is01_a | 15/15 fires | geometry-only (忽略 is01_a 门) |
|---------|--------|-------------|-------------------------------|
| IS11-AMB-414 (med_001 p20) | false | **not_fires ×15** | not_fires ×15 |
| IS11-AMB-422 (med_001 p24) | false | **not_fires ×15** | not_fires ×15 |

`gt_merge_geometry_only_also_clean = true` — 图注 anchor 的冻结对齐组根本不含数字邻居,
免疫是结构性的 (比门禁更强)。

## 7. 13 个 is01_a Anchor 的 firing matrix (§十, descriptive only)

| anchor | doc/page | text_a | set | ratio | fired(任一组合) |
|--------|----------|--------|----:|------:|-----------------|
| IS11-AMB-467 | cs_001 p3 | '37.0' | 7 | 1.49 | **yes** |
| IS11-AMB-483 | cs_001 p3 | '23.5' | 8 | 23.48 | no |
| IS11-AMB-505 | cs_001 p3 | '61.4' | 7 | 1.49 | **yes** |
| IS11-AMB-514 | cs_001 p3 | '44.2' | 7 | 1.49 | **yes** |
| **IS11-AMB-135** | **efficientnet p5** | **'4'** | **10** | **6.21** | **no ← 目标 FP** |
| IS11-AMB-346 | efficientnet p9 | '83.95' | 4 | 1.46 | **yes** |
| IS11-AMB-350 | efficientnet p9 | '80.16' | 4 | 1.46 | **yes** |
| IS11-AMB-401/407/409 | med_001 p19 | '0.70'/'1.35'/'0.65' | 1 | — | no (轴刻度: 右对齐, 不入 left_alignment_group) |
| IS11-AMB-024 | resnet p6 | '28.54' | 9 | 2.01 | **yes** |
| IS11-AMB-034 | resnet p6 | '21.59' | 7 | 1.04 | **yes** |
| IS11-AMB-074 | resnet p8 | '41.5' | 2 | 1.00 | no (set<N) |

7/13 anchors 在部分组合下 fire — 全部为 GT=KEEP 的真实数值列 (fired-unchanged);
0 例造成预测改变。**这不是统计验证的特异性, 仅为描述性证据。**

## 8. Negative Case Analysis (§十一 — NEGATIVE_CASE_COVERAGE = LIMITED, 保持)

44 个 GT=KEEP 案例 (以 experimental_c 路线为例, 全 15 组一致):

| 桶 | 数量 |
|----|-----:|
| never fired | 37 |
| fired but unchanged | 7 (真实数值列, baseline 未 MERGE) |
| fired and changed | **0** (本应 changed 的唯一案例 = FP, 但未 fire) |
| caused collateral damage | **0** |

KEEP → MERGE: **0 例** (结构上不可能: guard 单向抑制)。

## 9. Document-level 分解 (§十二, 禁止只报 aggregate)

| Document | cases | baseline errors (B/C) | corrected | new errors | collateral | net GT change | anchors fired |
|----------|------:|----------------------|----------:|-----------:|-----------:|--------------:|--------------:|
| is11_resnet | 9 | 0 / 0 | 0 | 0 | 0 | 0 | 2/3 |
| is11_efficientnet | 18 | **1 / 1** | **0** | 0 | 0 | **0** | 2/3 |
| is11_med_001 | 8 | 0 / 0 | 0 | 0 | 0 | 0 | 0/3 |
| is11_cs_001 | 10 | 0 / 0 | 0 | 0 | 0 | 0 | 3/4 |

唯一需要修正的错误在 efficientnet, 但 guard 在该 anchor 上未生效 → net = 0 全线。
(不声称跨文档/跨语料任何泛化。)

## 10. Parameter Stability (§十三, 15 组矩阵摘要 — 完整逐组数据在 results JSON)

| N \ R_max | 2.0 | 2.5 | 3.0 |
|-----------|-----|-----|-----|
| 3 | A=0 | A=0 | A=0 |
| 4 | A=0 | A=0 | A=0 |
| 5 | A=0 | A=0 | A=0 |
| 6 | A=0 | A=0 | A=0 |
| 7 | A=0 | A=0 | A=0 |

(B=0, C-字面=1, C-新引入=0, GT-MERGE 免疫 = 全 15 组成立; 失败由 A 单一主导。)

**满足完整安全条件的 N 值 = 0/5** (合约要求 ≥3/5)。

## 11. VERDICT (按预注册规则, §十二/§十八)

```text
A = 0/1 (全 15 组)  →  规则 "REJECTED: A=0" 触发

PH-02 = REJECTED
```

无补规则、无定义修改、无重跑。接受失败。

## 12. 失败后可登记的候选 (descriptive, 本轮禁止实现/禁止运行)

- 仅作记录: FP anchor 的冻结对齐组内存在一个 **9 成员的最大连续等距段**
  (dy 全 ≈9.05pt)。任何 "最大等距连续段" 变体都是**不同的 hypothesis 定义**,
  属 post-hoc 观察产生的候选 (PH-02b), 依 §十四 禁止在本轮测试或包装为本轮结果。
  若未来要检验, 必须走新的预注册合约 (含负例集扩充), 且当前证据提示其风险:
  resnet p6 的 '28.54' (ratio 2.01, 整集口径已 fire) 显示等距段判据同样会 fire 于
  非行号数值列 — 特异性问题不会自动消失。

## 13. 统计解释边界 (§十五, 原文保留)

本实验**不**支持以下任何表述: "证明 PH-02 有效" · "普遍适用于 PDF" ·
"解决 table understanding" · "证明 column detection 泛化" · "production ready"。
合法表述仅限: **当前 replay corpus 与 PH-02 hypothesis (预注册整集等距形式) 不一致;
已知 FP 未被移除; 未观察到 collateral damage 与新引入 MERGE; Known FP denominator = 1,
statistical power extremely limited。**

## 14. 交付物

- `tmp/ph02_column_membership_experiment_report.md` (本报告)
- `tmp/ph02_column_membership_experiment_results.json` (468 KB, 完整 15×45 case-level
  + integrity + baseline + anchor analyses + 15 组指标 + 分类)
- `tmp/ph02_experiment/` (runner `run_ph02_replay.py` · `baseline.json` ·
  `anchor_analyses.json` · `runs_all_15.json` · `classification.json` · `experiment_master.json`)

---

## 最终 Gate (§十七)

```text
PH02_EXPERIMENT = COMPLETE
PH02_VERDICT = REJECTED (预注册规则: A=0/1 @ 全部 15 组; B=0; GT-MERGE 免疫 15/15)
PH02_IMPLEMENTATION = NOT AUTHORIZED
FROZEN_BASELINE = INTACT
GT_MODIFICATION = NONE
ATOMIC_OBSERVATION_MODIFICATION = NONE
PERCEPTION_PRODUCTION_MODIFICATION = NONE
PH03 = NOT AUTHORIZED
PH01 = NOT AUTHORIZED
PRODUCTION = FALSE
STOP = TRUE
```
