# M-B Phase 3.2 — Implementation + Isolated Replay Report

> PRE-REGISTERED · CONTROLLED · FALSIFIABLE · ISOLATED EXPERIMENT. 结果告诉我们设计
> 哪里成立/不成立; 代码没有追着结果跑。

## 1. STATUS

**M-B PHASE 3 = REPLAY PASS** (S1-S10 全 PASS, S2 HARD GATE PASS, F1-F10 = 0)。

## 2. Implementation Delta (实际执行)

| 层 | 文件 | 动作 | 行数 | 状态 |
|---|---|---|---|---|
| Observation Layer | (frozen) | 零改动 | 0 | FROZEN ✓ |
| Structural Evidence | `tmp/mb_eic1_adapter.py` | 新建: LSP+RSC+EIC-1+coexistence | ~180 | ISOLATED ✓ |
| Consumer Adapter | `tmp/mb_phase3_2_replay.py` | 新建: OFF/ON runner, 导入 harness 未改 | ~150 | ISOLATED ✓ |
| IS-11 decision logic | `tmp/is11_machine_evaluation.py` | **零改动** (hash 验证) | 0 | UNCHANGED ✓ |
| TLD / GT / 观测层 | (frozen) | 零改动 | 0 | UNCHANGED ✓ |

**关键**: harness 文件**从未被编辑** — replay runner 用 `importlib` 导入其函数;
`experimental_c_decision` / `compute_is11_observation` 原样调用。

## 3. Baseline Integrity (S10)

```
harness sha:    pre=b41494020b49 post=b41494020b49  MATCH ✓
TLD sha:        pre=022f5c21e872 post=022f5c21e872  MATCH ✓
GT sha:         pre=7349963d0d23 post=7349963d0d23  MATCH ✓
anchors drift:  0/7  ✓
FROZEN_BASELINE = INTACT
```

## 4. OFF Path Isolation (S9)

- OFF decisions vs archived baseline: **21/21 byte-identical** ✓
- OFF is11_observation: 21/21 match after tuple/list normalization
- 8 "mismatches" 调查: 全部是 **tuple-vs-list 序列化伪影** (harness 返回 `(row_idx,col_idx)`
  tuple; 存档 JSON 序列化为 list `[row_idx,col_idx]`)。归一化后 **0 真实差异**。
  决策相关字段 (is_in_table/same_cell/different_cell) 全部一致。
- **S9 = PASS** (adapter OFF 时不调用; OFF = 纯 harness 原样)

## 5. ON Path — Frozen Matrix Results (21 决策行)

### Evidence State 分布
- `tld_only_or_neither`: 10 (EIC-1 未发射 — region 未形成/非同带/分区不可解, 诚实)
- `eic1_single_source`: 8 (EIC-1 发射, TLD 静默 — M-B 目标案例)
- `agree`: 3 (TLD+EIC-1 双源一致: 034, 346, 350)
- `evidence_conflict`: 0 (无自然冲突 — 如 Phase 3 §11 预测)

### A1 — Positive Repair (S1)
| Case | off | on | gt | path |
|---|---|---|---|---|
| AMB-135 | MERGE (FP) | **KEEP_SEPARATE** | KEEP_SEPARATE | Geometry→LSP→RSC→EIC-1→既有契约→既有决策 ✓ |

**S1 = PASS** — FP 经完整契约链修复, 非新 decision rule。

### A2 — DIRECT Recovery (8)
| Case | off | on | gt | ev | result |
|---|---|---|---|---|---|
| 130 | ABSTAIN | KEEP | KEEP | eic1_single | recovered ✓ |
| 313 | ABSTAIN | ABSTAIN | KEEP | tld_only | honest unavailable (lag=0, 预期) ✓ |
| 457 | ABSTAIN | KEEP | KEEP | eic1_single | recovered ✓ |
| 462 | ABSTAIN | ABSTAIN | KEEP | tld_only | honest unavailable (lag=1 弱, 预期) ✓ |
| 467 | ABSTAIN | KEEP | KEEP | eic1_single | recovered ✓ |
| 483 | ABSTAIN | KEEP | KEEP | eic1_single | recovered ✓ |
| 505 | ABSTAIN | KEEP | KEEP | eic1_single | recovered ✓ |
| 514 | ABSTAIN | KEEP | KEEP | eic1_single | recovered ✓ |

6/8 recovered (GT-consistent); 2/8 honest ABSTAIN; **0 MERGE** ✓

### B — Safety Canaries (S2 HARD GATE)
| Case | off | on | gt | flip? |
|---|---|---|---|---|
| AMB-414 | ABSTAIN | ABSTAIN | MERGE | **NO** ✓ |
| AMB-422 | ABSTAIN | ABSTAIN | MERGE | **NO** ✓ |

**S2 = PASS** (0 flips; localization 约束生效 — canary pair-band density=0)

### C — Negative Controls
| Case | off | on | gt | ev | result |
|---|---|---|---|---|---|
| AMB-519 (prose) | ABSTAIN | ABSTAIN | KEEP | tld_only | unchanged ✓ |
| AMB-262 | ABSTAIN | KEEP_SEPARATE | KEEP_SEPARATE | eic1_single | GT-consistent recovery (见 §8 披露) |

### D — Correct Controls (S4)
| 005 | 024 | 034 | 074 | 346 | 350 | 522 | 530 |
|---|---|---|---|---|---|---|---|
| KEEP✓ | KEEP✓ | KEEP✓(agree) | KEEP✓ | KEEP✓(agree) | KEEP✓(agree) | KEEP✓ | KEEP✓ |

**S4 = PASS** (8/8 unchanged)

### Descriptive Boundary (4 行, 无 GT)
arXiv 1910.10683 p1(abstract)/p14(references): region_forms=False (co_density=1-2 < 3)
→ EIC-1 正确不发射 context ✓。LLaMA code-line / 2212 TOC / axis-tick 专用 PDF 不在
可用语料; 边界覆盖由 in-frame 负例 (519 prose / 034 value-column / 005 mixed) + arXiv
描述性提供。

## 6. S1-S10 Adjudication

| # | 标准 | 判定 | 证据 |
|---|------|------|------|
| S1 | AMB-135 corrected | **PASS** | MERGE→KEEP via eic1_single_source, 契约链完整 |
| S2 | canary 0 flips | **PASS (HARD GATE)** | 414/422 both ABSTAIN unchanged |
| S3 | negative collateral = 0 | **PASS** | 0 GT-inconsistent changes; 519 unchanged; 262 GT-consistent |
| S4 | correct controls unchanged | **PASS** | 8/8 unchanged |
| S5 | semantic leakage = 0 | **PASS** | 11 admitted records, all candidate, 0 forbidden fields |
| S6 | decision policy change = 0 | **PASS** | harness hash unchanged + behavioral 10/10 + 0 new branches |
| S7 | provenance = 1.0 | **PASS** | 11/11 quadruple complete |
| S8 | determinism = PASS | **PASS** | 21/21 double-run byte-identical |
| S9 | OFF byte-identical | **PASS** | 21/21 decisions; 8 "mismatches" = tuple/list artifacts |
| S10 | frozen drift = 0 | **PASS** | anchors 0/7, GT/TLD/harness hashes match |

## 7. F1-F10 Adjudication

| # | 名称 | 判定 |
|---|------|------|
| F1 Semantic Leakage | **0** |
| F2 Decision Policy Change | **0** |
| F3 Caption Safety Failure | **0** |
| F4 Negative Collateral | **0** |
| F5 Provenance Failure | **0** |
| F6 Determinism Failure | **0** |
| F7 OFF-path Drift | **0** (8 "mismatches" = serialization artifacts, not drift) |
| F8 Integration Contract Failure | **0** |
| F9 EIC-1 Boundary Failure | **0** |
| F10 Conflict Handling Failure | **0** (0 conflicts occurred; contract untested by natural cases — 见 §8) |

## 8. Honest Disclosures

1. **AMB-262 分类修正**: Phase 2/3 标 "different_band" (基于早期 atom 测量 same_y_band=False);
   实际 sampling-frame 案例对为同带+不同 x0 分区 (lsp x187.4 vs x213.1, co_density=41) →
   EIC-1 正确发射 → KEEP_SEPARATE (GT-consistent)。早期测量针对的是不同 atom 对;
   replay 用实际案例对纠正了分类。**非失败** — 实验揭示了分类误差。
2. **OFF "mismatches"**: 8/21 is11_observation 看似不匹配存档; 调查确认全部是
   tuple-vs-list 序列化伪影 (harness 返回 tuple, 存档 JSON 为 list)。归一化后 0 真实差异;
   决策 21/21 byte-identical。S9 PASS。
3. **Conflict 路径未被自然案例测试**: 0 evidence_conflict 发生 (TLD 盲页 = EIC 目标;
   TLD 活跃页 = agree)。冲突契约 (EVIDENCE_CONFLICT→all-False) 未被自然案例行使 —
   如 Phase 3 §11 预测, 需合成单元测试验证。**诚实覆盖缺口, 非失败**。
4. **AMB-313/462 honest ABSTAIN**: lag=0/1 分区不可解 → ABSTAIN 保留 (Phase 3 预期)。
5. **Descriptive 行**: LLaMA/2212/axis 专用 PDF 不在可用语料; in-frame 负例 + arXiv
   描述性提供边界覆盖。

## 9. Independent Audit (§21 — 非 runner 自报)

- file diff: harness/TLD/GT/anchors 全部 hash 不变 ✓
- decision function hash: b41494020b49 不变 ✓
- semantic leakage: 0 (admitted 11 records, 全 candidate, 0 forbidden) ✓
- safety canaries: 414/422 0 flip ✓
- decision invariance: behavioral 10/10 (EIC-1 inactive → ON==OFF) ✓
- provenance: 11/11 ✓
- determinism: 21/21 ✓
- OFF: 21/21 decisions byte-identical ✓
- **independent audit = PASS (与 runner 自报一致)**

## 10. Scientific Claim Boundary

GT-confirmed positive = 1。本次 PASS 只支持表述:

> **"在当前冻结测试框架中, 验证了该 minimal Consumer Integration 能够处理已识别的
> 结构切片失败模式。"**

禁止声称: 通用 vector table recovery / table detection / row-number recognition /
跨文档泛化 / 普适方法 / production readiness。mechanism validation ≠ generalization proof。

## 11. Final Gate

```text
==================================================
M-B PHASE 3.2 — IMPLEMENTATION + ISOLATED REPLAY
==================================================
STATUS: REPLAY PASS

S1-S10: ALL PASS (S2 HARD GATE PASS)
F1-F10: 0
DECISION_FUNCTION: UNCHANGED (hash verified)
OFF_PATH: byte-identical (21/21; 8 "mismatches" = tuple/list artifacts)
FROZEN_BASELINE: INTACT (drift 0, GT/TLD/harness hashes match)
PROVENANCE: 11/11 complete (1.0)
DETERMINISM: 21/21

EVIDENCE_STATES: tld_only=10, eic1_single=8, agree=3, conflict=0
RECOVERY: AMB-135 FP fixed + 6/8 DIRECT recovered + 2 honest ABSTAIN
CANARIES: 0 flips    CONTROLS: 8/8 unchanged    NEGATIVES: 0 damage

IMPLEMENTATION = EXECUTED (isolated, flag-gated, non-production)
ISOLATED_REPLAY = EXECUTED (frozen 21-row matrix)
GT_MODIFICATION = NONE
ATOMIC_OBSERVATION_MODIFICATION = NONE
TLD_MODIFICATION = NONE
IS11_DECISION_MODIFICATION = NONE
PERCEPTION_PRODUCTION_MODIFICATION = NONE
FROZEN_BASELINE = INTACT
PRODUCTION = FALSE

CLAIM: 框架内机制验证 (GT-confirmed positive = 1; 禁普适化)
NEXT_STEP = (需人类决策; 不自行进入)
STOP = TRUE
==================================================
```
