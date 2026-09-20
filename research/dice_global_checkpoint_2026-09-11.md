# DICE Global Research Checkpoint — 2026-09-11

> 纯审计 / 状态固化 / 研究资产整理。M-B 实验线正式关闭。不开展新实验, 不设计新扩展。

## A. SYSTEM POSITIONING

```text
DICE = Capability Layer (governed operationalization of validated knowledge)

Document → Evidence → Human Validation → Capability → Transfer / Runtime

RAG = retrieval
DICE = governed operationalization of validated knowledge
```

DICE 不是 table detector / OCR / parser / classifier。DICE 是把经人审验证的知识
转化为可治理、可追溯、可回退的能力资产的操作化层。

## B. GOVERNANCE

- **Runtime Authority = ZERO** (低层证据不自动获得决策权; 解释权经 EIC-1 契约 + L5 人审)
- **Capability Registration = Human Controlled** (L5 reusable pattern 级, 非 instance annotation)
- **Production = FALSE**
- **Frozen Baseline = INTACT**

## C. CURRENT FROZEN STATE

| 冻结项 | 哈希 (前16) | 状态 |
|---|---|---|
| P1 extract (atomic_text) | (registry) | drift=0 |
| P2 engine (geometry_engine) | (registry) | drift=0 |
| P2 config (geometry_config) | (registry) | drift=0 |
| P2 shape (geometry_observation) | (registry) | drift=0 |
| P4 span config | (registry) | drift=0 |
| P6 region engine | (registry) | drift=0 |
| TLD (table_line_detector) | 022f5c21e872ad9e | drift=0 |
| GT (is11_semantic_ground_truth) | 7349963d0d23b5ef | drift=0 |
| IS-11 harness (is11_machine_evaluation) | b41494020b491b92 | drift=0 |
| Atomic Observation Layer | 7 frozen sources / layer_registry | drift=0 |
| **anchors_drift total** | **0/7** | **INTACT** |

registered_detectors: p6_region_engine, table_line_detector (均 invoked_by_layer=False)。

## D. CLOSED RESEARCH LINES

| 线 | 最终状态 | 关闭理由 |
|---|---|---|
| PH-02 (column-membership predicate) | **REJECTED** | 15/15 A=0; whole-group research object 结构上无法承担 column-membership 语义; 无补救 |
| C2 (candidate-column-segment) | **REQUIRES_REDESIGN / NOT IMPLEMENTED** | POSITIVE_COVERAGE=INSUFFICIENT; positive diversity=1; 双重阻塞 (redesign × coverage) |
| M-B (minimal Consumer Integration) | **CLOSED / PASS** | Phase 3.2 REPLAY_PASS; S1-S10 ALL PASS; F1-F10=0; 预注册机制验证完成 |

**不自动重开**。禁止 M-B Phase 4 / M-B-1 / M6/M7/M8/M9 / 新 predicate / 新 threshold tuning /
新 replay expansion (除非未来另行明确授权)。

## E. CURRENT OPEN RESEARCH QUESTIONS (只列, 不执行)

| # | 开放问题 | Evidence Sufficiency | Research Value | Risk | Experiment Readiness |
|---|---------|----------------------|----------------|------|---------------------|
| OQ1 | conflict 契约自然案例覆盖 = 0 (合成单元测试未运行) | PARTIAL (合成设计完成, 自然案例未行使) | MEDIUM | LOW | design-ready, NOT authorized |
| OQ2 | L5 Human Validation (reusable pattern 级) 未发生 | INSUFFICIENT (无 L5 验证; interpretation 仍 candidate) | HIGH | MEDIUM (解释权未最终落地) | NOT READY (需 pattern 抽象工作) |
| OQ3 | 跨文档泛化 | INSUFFICIENT (GT positive=1) | HIGH but NOT actionable (无更多正例) | HIGH (over-claim risk) | NOT READY |
| OQ4 | AMB-313/462 分区推导 (alternative frozen relations) | PARTIAL (lag=0/1 已知 left_alignment_group 不足) | LOW-MEDIUM | LOW | design-only |

**原则**: 现有 evidence 不足时标记 INSUFFICIENT EVIDENCE, 不自行提出新 rule。
**CURRENT STATE = STABLE CHECKPOINT** — 不自行选择下一研究问题。

## F. CURRENT EXPERIMENTAL ARTIFACTS

| file | purpose | status | production dependency | allowed usage |
|---|---|---|---|---|
| tmp/mb_eic1_adapter.py | EIC-1 LSP+RSC+SCE 推导 (read-only over frozen store) | experimental, isolated | **NONE** (不被任何 production module import) | 隔离实验复现 only |
| tmp/mb_phase3_2_replay.py | OFF/ON replay runner (importlib 导入 harness 未改) | experimental, isolated | **NONE** (只写 tmp/ 结果) | 隔离实验复现 only |
| tmp/mb_phase3_2_*.json | replay 结果/baseline/report | experimental data | NONE | 审计参考 only |
| tmp/mb_phase3_1_*.md/json | 参数定值记录 | design record | NONE | 参考 only |
| tmp/mb_phase3_*design.md/json | Phase 3 冻结矩阵设计 | design record | NONE | 参考 only |
| tmp/mb_phase2*/2.1*/2.2* | 契约/审查设计 | design record | NONE | 参考 only |
| tmp/mb_case_study / dice_* (7 文件) | 证据沉淀/论文素材 | documentation | NONE | 参考 only |

**EXPERIMENTAL_ARTIFACT_ISOLATION = PASS**:
- 实验代码仅在 tmp/; 不被 perception/ chunker/ production import (grep 验证 0 命中);
- adapter 只读 frozen store (无 mutation); replay 用 importlib 导入 harness 未改文件;
- 实验代码唯一写操作 = tmp/mb_phase3_2_isolated_replay_results.json;
- 不改变 frozen runtime / harness / IS-11 decision / GT / TLD / Atomic Observation / capability registration;
- 不形成新 production dependency。

## G. SCIENTIFIC CLAIM BOUNDARY

- **mechanism validation ≠ generalization** (M-B Phase 3.2 = 框架内机制验证, 非泛化证明);
- **GT-confirmed positive = 1** (全程);
- **natural conflict coverage = 0** (冲突契约未被自然案例行使);
- **production readiness = FALSE**;
- **generalization = NOT VERIFIED**;
- 允许表述: "在当前冻结测试框架中, 验证了该 minimal Consumer Integration 能够处理已识别的
  结构切片失败模式。"
- 禁止表述: 通用 vector table recovery / table detection / row-number recognition /
  跨文档泛化 / 普适方法 / production readiness。

## H. RESEARCH INTEGRITY

- **failure preservation**: PH-02 REJECTED / C2 INSUFFICIENT / Phase 2.1 CONDITIONAL_PASS /
  honest ABSTAIN (313/462) 全部存档, 未因最终 PASS 删除;
- **discrepancy log**: 7 条 (D1-D7) 在 `tmp/dice_evidence_discrepancy_log.md`, OLD→AUDIT→
  CORRECTED→REASON→TIMING, 不覆盖历史;
- **historical correction**: DIRECT 6→8→9; eff/cs 5+3→3+7; AMB-262 分类; OFF 伪 mismatch;
  AMB-135 '4' identity; 组枚举口径; FP 3→1 — 全部双值保留;
- **evidence provenance**: EIC-1 11/11 records 四元组完整 (source/artifact/input/trace);
  frozen source sha 逐项可验;
- **experiment reproducibility**: determinism 21/21 双跑 byte-identical; frozen baseline
  drift=0; OFF byte-identical — 实验可独立复现。

## Final Governance Gate

```text
==================================================
DICE GLOBAL RESEARCH CHECKPOINT — 2026-09-11
==================================================
M-B = CLOSED / PASS
CURRENT EXPERIMENT = NONE
NEW EXPERIMENTS = 0    NEW PARAMETERS = 0    NEW PREDICATES = 0

GT_MODIFIED = FALSE    TLD_MODIFIED = FALSE
ATOMIC_OBSERVATION_MODIFIED = FALSE    IS11_DECISION_MODIFIED = FALSE
PRODUCTION_CODE_MODIFIED = FALSE

EXPERIMENTAL_ARTIFACT_ISOLATION = PASS
FROZEN_BASELINE = INTACT (anchors_drift 0, GT/TLD/harness sha 全匹配)
PRODUCTION = FALSE

GENERALIZATION = NOT VERIFIED
GT_POSITIVE = 1
NATURAL_CONFLICT_COVERAGE = 0

CURRENT_STATE = STABLE CHECKPOINT
STOP = TRUE
==================================================
```
