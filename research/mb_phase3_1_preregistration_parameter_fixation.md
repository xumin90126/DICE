# M-B Phase 3.1 — Preregistration Parameter Fixation

> 性质: DESIGN-ONLY (参数定值, 非实施)。任务: 在实施前正式固定 EIC-1 的区域共组织
> 参数 (最后一批 MISSING_PARAMETER)。定值依据 = 冻结测量事实 (只读枚举, 与前序显微镜
> 同性质), **非**从"让 AMB-135 通过"反推。承重参数在 canary 边界侧, 不在目标侧。

---

## 1. 关键设计发现 — Localization Gap

测量揭示: **raw left_alignment_group 的共结构在每一页都很高** (med p20 caption 页 =
24 重叠分区; cs p3 = 125) — 正文 margin 组 (x0≈85/107, n=15-24, y_ext 293-393pt)
**污染每一页**。仅靠 left_alignment_group 共结构计数 **无法区分** 表格与 caption/正文。
→ EIC-1 区域推导 (Phase 2.2 §8 precondition 1) 若无**定位约束**, caption canary 必
FIRE → SAFETY FAILURE。

**修正**: LSP/区域推导增加 **localization 约束** — 只有 y_ext 有界的分区 (局部结构列)
计入共结构; page-wide margin 组 (y_ext 293-393pt) 被排除。这恰好是 PH-02 whole-group
陷阱的结构性复发点 — 定位约束阻止 LSP 退化成 page-wide 整组对象。LSP 定义不变 (仍
structural); **区域推导** 增 localization 子条件 (EIC-1 precondition 1 扩展, 非语义)。

## 2. 测量事实 (band-local co-structure density, 5 页)

方法: 对每页, 取 stable 分区 (P_min_mem≥2 ∧ P_min_bands≥3 ∧ y_ext≤BOUND), 按各 y-band
统计"在该 band 有成员的 local stable 分区数" = band-local density。

| 页 | 角色 | pair-band LOCAL density (≤100pt) | pair-band LOCAL density (≤150pt) | 页 max LOCAL |
|---|---|---:|---:|---:|
| eff p5 (y=162) | AMB-135 目标 | **19** | **30** | 20-31 |
| med p20 (y=347) | canary AMB-414 | **0** | **0** | 4-5 |
| med p24 (y=578) | canary AMB-422 | **0** | **0** | 0-1 |
| eff p9 | 正确控制 (表) | — | — | 26 |
| resnet p6 | 正确控制 (表) | — | — | 10 |
| cs p3 | DIRECT 目标 (表) | — | — | 17 |

分隔面: **目标/表格 = 10-30; canary = 0** (跨 100/150/200pt bound 全为 0)。
表格列 y_ext = 32-88pt; caption/margin y_ext = 293-393pt; **间隙 88-293pt** (193pt
裕度)。

## 3. 固定参数 (PREREGISTRATION — 实施前定值, 结果无关)

| 参数 | 值 | 依据 | 承重? |
|---|---|---|---|
| P_min_members | 2 | 表格分区 ≥4 成员; lag=0/1 噪声排除 | 否 (裕度大) |
| P_min_bands | 3 | 表格列 ≥4 带; caption 片段 1 带 | 中 |
| **P_localization** (分区 y_ext ≤) | **150pt** | 表格列 32-88pt; caption/margin 293-393pt; 150pt = 间隙中点 (裕度 62pt↓/143pt↑) | **是 (canary 边界)** |
| **P_min_costructure_band_local** | **3** | 表格 pair-band = 10-30; canary pair-band = 0; 阈值 3 在 0 与 10 的间隙中 | **是 (canary 边界)** |
| same_y_band (候选对) | True | frozen P2 pairwise (非新参数) | frozen |

## 4. Canary 安全性验证 (实测, 非假设)

```text
med p20 AMB-414 (pair y=346.5):
  bound=100pt: pair_band_local_density=0  → NO region → no context → abstain preserved ✓
  bound=150pt: pair_band_local_density=0  → SAFE ✓
  bound=200pt: pair_band_local_density=0  → SAFE ✓ (robust across [100,200]pt)
med p24 AMB-422 (pair y=577.7):
  bound=100/150/200pt: pair_band_local_density=0 → SAFE ✓ (all bounds)
eff p5 AMB-135 (pair y=161.95):
  bound=150pt: pair_band_local_density=30 ≥ 3 → region forms → context admissible ✓
```
canary pair-band 在全部 bound ∈ [100,200]pt 下 density=0 → P_localization 鲁棒。
目标 pair-band density=30 → 远超阈值 3 → AMB-135 无边界风险 (修复路径不依赖参数精调)。

## 5. EIC-1 Precondition 1 修正 (契约细化, 非语义变更)

Phase 2.2 §8 precondition 1 原文: "region 共组织可推导 (≥2 个可分辨 LSP + y-overlap
+ 跨带列稳定; 参数为预注册槽)"。

**修正后 (参数已定值)**:
> region 共组织可推导 ⇔ (a) ≥2 个可分辨 LSP (各 P_min_members≥2) ∧ (b) 各 LSP 跨带
> 稳定 (P_min_bands≥3) ∧ (c) **各 LSP 局部化 (y_ext ≤ P_localization=150pt)** ∧
> (d) 在候选对的 y-band, ≥P_min_costructure_band_local=3 个 local stable 分区共现 ∧
> (e) 候选对 same_y_band=True (frozen)。

不变项: LSP 仍 = structural object (零语义); localization 是纯几何 bound (空间范围),
非 table/cell 语义标签; EIC-1 仍 = 唯一语义闸门; 状态映射仍全复用既有约定。

## 6. 证伪条件

- canary pair-band LOCAL density ≥3 (任一 bound) → P_localization 或 P_costructure 失效
  → REPLAY FAIL (S2 hard gate);
- DIRECT 目标 pair-band LOCAL density <3 → context 不可得 (诚实, 逐例归因, 非失败);
- 正确控制决策变化 → F4 collateral → FAIL;
- P_localization 若在实施后发现表格列 y_ext > 150pt (大表) → 经治理修订 (非 ad hoc 调)。

## 7. 诚实披露

- cs p3 六对、eff p9/resnet p6 控制的**逐对** pair-band density 未逐一测 (仅测页 max
  + zone profile); 实施时 replay 会逐对验证 — 若某 DIRECT 对 density<3, 归为 honest
  unavailable (A2 通则已预注册);
- localization 约束是 Phase 2.2 后新增的契约细化 (precondition 1 扩展) — 但不改 LSP
  定义、不改状态映射、不改决策逻辑; 属 design review 范围内;
- AMB-135 修复**不依赖**任何参数精调 (pair density=30, 远超阈值 3) — 承重参数全在
  canary 边界侧, 与"让 FP 通过"无关。

## 8. Gate

```text
==================================================
M-B PHASE 3.1 — PREREGISTRATION PARAMETER FIXATION
==================================================
STATUS: COMPLETE (参数定值完毕; MISSING_PARAMETER = 0)
LOCALIZATION_GAP: 发现并修正 (raw alignment group page-contaminated;
  y_ext≤150pt localization 约束排除 margin 组; 防 PH-02 whole-group 复发)
CANARY_SAFETY: 实测验证 (pair-band density=0 跨 [100,200]pt; 目标=30)
PARAMETERS: P_min_mem=2, P_min_bands=3, P_localization=150pt,
  P_costructure_band_local=3, same_y_band=True(frozen)
EIC-1_PRECONDITION_1: 细化 (localization 子条件; 非语义变更)
FALSIFICATION: canary density≥3 => FAIL; DIRECT density<3 => honest unavailable
IMPLEMENTATION = NOT AUTHORIZED    REPLAY = NOT AUTHORIZED
GT_MODIFICATION = NONE    FROZEN_BASELINE = INTACT (drift 0, GT ✅, 层 7/7)
NEXT_STEP = 回到实施授权决策点 (参数已就绪; 是否授权实施 + isolated replay)
STOP = TRUE
==================================================
```
