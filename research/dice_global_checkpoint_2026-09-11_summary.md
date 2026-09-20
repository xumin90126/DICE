# DICE Global Checkpoint Summary — 2026-09-11

> 入口摘要。开启新研究阶段时先读本文件。

## 一句话状态

DICE 当前处于 **STABLE CHECKPOINT**。M-B minimal Consumer Integration 实验线已正式关闭
(PASS); PH-02 (REJECTED) 与 C2 (INSUFFICIENT) 已关闭; 冻结基线完整; 无进行中实验;
production = FALSE; 不自行进入下一阶段。

## 关闭的研究线

| 线 | 状态 |
|---|---|
| PH-02 (whole-group column-membership predicate) | REJECTED (15/15 A=0) |
| C2 (candidate-column-segment) | REQUIRES_REDESIGN / NOT IMPLEMENTED (coverage=1) |
| M-B (minimal Consumer Integration) | **CLOSED / PASS** (Phase 3.2 S1-S10 PASS, F1-F10=0) |

## 冻结基线 (INTACT, drift=0)

- 7 frozen anchors (P1/P2×4/P4/P6/TLD) — 全部 sha 匹配;
- GT sha = 7349963d0d23b5ef; IS-11 harness sha = b41494020b491b92;
- Atomic Observation Layer 7 sources 完整;
- 全程未修改 GT / TLD / Atomic Observation / IS-11 decision / production code。

## M-B 关闭的科学含义 (不是什么)

**是**: 当前冻结测试框架下, M-B minimal Consumer Integration 的预注册机制验证已完成
并通过验收; 实验线关闭, 不继续扩张。

**不是**: table detection 已解决 / row-number recognition 已解决 / M-B 所有 coverage gap
已解决 / generalization 已证明 / production ready。

- GT-confirmed positive = 1
- natural conflict coverage = 0
- generalization = NOT VERIFIED
- production = FALSE

## 实验产物隔离 (PASS)

- `tmp/mb_eic1_adapter.py` + `tmp/mb_phase3_2_replay.py` 仅在 tmp/;
- 不被任何 production module import (grep 0 命中);
- adapter 只读 frozen store (无 mutation); replay 用 importlib 导入 harness 未改;
- 不形成新 production dependency。

## 开放问题 (只列, 不执行; evidence 不足标 INSUFFICIENT)

| 问题 | Evidence | 价值 | 就绪? |
|---|---|---|---|
| conflict 契约自然案例覆盖=0 | PARTIAL | MEDIUM | design-ready, NOT authorized |
| L5 Human Validation 未发生 | INSUFFICIENT | HIGH | NOT READY |
| 跨文档泛化 | INSUFFICIENT (positive=1) | HIGH但不可操作 | NOT READY |
| AMB-313/462 alternative relations | PARTIAL | LOW-MEDIUM | design-only |

**不自行选择下一研究问题。**

## 关键资产入口

- 完整因果链: `tmp/mb_case_study.md`
- 证据总目录: `tmp/dice_engineering_evidence_index.md`
- 论文素材库 (9 类型): `tmp/dice_paper_materials.md`
- 研究时间线 (12 Phase): `tmp/dice_research_timeline.md`
- 差异修正日志 (D1-D7): `tmp/dice_evidence_discrepancy_log.md`
- 资产清单 (10 类): `tmp/dice_research_asset_inventory.md`
- 完整 checkpoint: `tmp/dice_global_checkpoint_2026-09-11.md` + `.json`

## Governance

```text
M-B = CLOSED / PASS    CURRENT EXPERIMENT = NONE
NEW EXPERIMENTS/PARAMETERS/PREDICATES = 0
GT/TLD/ATOMIC_OBSERVATION/IS11_DECISION/PRODUCTION_CODE = ALL UNCHANGED
EXPERIMENTAL_ARTIFACT_ISOLATION = PASS    FROZEN_BASELINE = INTACT
PRODUCTION = FALSE    GENERALIZATION = NOT VERIFIED    GT_POSITIVE = 1
CURRENT_STATE = STABLE CHECKPOINT    STOP = TRUE
```
