# M-B Phase 3 — Isolated Replay Design / Authorization Request

> 性质: DESIGN-ONLY。零实施、零代码修改、零 replay 运行、零 GT/threshold/predicate/
> policy 修改。本文件回答: **如果未来授权实施 EIC-1 + minimal consumer integration,
> 应如何在最小、隔离、可证伪的测试集合上验证 7 项关键性质** (FP 修复 / caption 安全 /
> 正确 KEEP 不破坏 / conflict 无 hidden arbitration / provenance 完整 / OFF byte-identical
> / decision policy 事实上不变)。

---

## 1. STATUS

**M-B PHASE 3 = DESIGN-READY**。IMPLEMENTATION = NOT AUTHORIZED; REPLAY = NOT
AUTHORIZED; 本文件是授权申请, 不是执行。

## 2. OBJECTIVE

见标题下引言 7 项。修复路径必须证明为: Geometry → LSP → RSC → EIC-1 → existing
observation contract → existing decision policy — **不是新增 decision rule**。

## 3. DESIGN_SCOPE

最小四类 (A/B/C/D) + 描述性边界观察; 决策度量行 21, 描述行 4; 全部取自既有冻结
corpus / GT (零新造 GT)。矩阵本节预固定, **结果无关, 不得事后增删**
(含"某 case 结果不好即删除" — 明确禁止)。

## 4. FROZEN_BASELINE

INTACT (anchors_drift=0, GT ✅, 层 7/7); TLD/IS-11 decision logic/观测层/GT 全部
INTACT; baseline 对照 = 存档 machine eval 逐案记录 (45-case)。

## 5. REPLAY_MATRIX (预固定)

图例: BASE = baseline 决策; EXP = expected integrated; 实测事实列引自 Phase 2/2.1
显微镜记录。

### A1 — Positive Repair Target (1)

| CASE_ID | DOC | PAGE | BASE | EXP | CASE_CLASS | WHY_INCLUDED | SAFETY_LEVEL |
|---|---|---|---|---|---|---|---|
| IS11-AMB-135 | efficientnet | p5 | MERGE (FP) | KEEP_SEPARATE (evidence state: EIC-1 admitted, candidate) | POSITIVE_REPAIR | 已证 lag10×lag6 + same_band 30.02 + 12 列簇共结构; FP 修复必须走契约链而非新规则 | HIGH (primary) |

### A2 — M-B DIRECT Recovery Targets (8, GT 全 = KEEP_SEPARATE)

| CASE_ID | DOC | PAGE | BASE | EXP | CASE_CLASS | WHY_INCLUDED | SAFETY_LEVEL |
|---|---|---|---|---|---|---|---|
| AMB-130 | efficientnet | p5 | ABSTAIN | KEEP_SEPARATE (context admitted) 或 ABSTAIN (honest unavailable); **禁 MERGE** | DIRECT_RECOVERY | 表头对 lag3/2 band4 | HIGH |
| AMB-313 | efficientnet | p8 | ABSTAIN | 同上 (⚠ 'Test Size' lag=0 → 不可得属诚实预期, 逐例归因) | DIRECT_RECOVERY (weak) | 表头对 lag0/1 band3 | HIGH |
| AMB-457 | cs_001 | p3 | ABSTAIN | 同 A2 通则 | DIRECT_RECOVERY | 'Models'/'Size' lag8/3 band9 | HIGH |
| AMB-462 | cs_001 | p3 | ABSTAIN | 同上 (lag1 弱成员注记) | DIRECT_RECOVERY | 'WGe'/'Avg.' lag1/8 band9 | HIGH |
| AMB-467 | cs_001 | p3 | ABSTAIN | 同上 | DIRECT_RECOVERY | '37.0'/'60.0' lag6/8 band9 | HIGH |
| AMB-483 | cs_001 | p3 | ABSTAIN | 同上 | DIRECT_RECOVERY | lag7/6 band9 | HIGH |
| AMB-505 | cs_001 | p3 | ABSTAIN | 同上 | DIRECT_RECOVERY | lag8/7 band9 | HIGH |
| AMB-514 | cs_001 | p3 | ABSTAIN | 同上 | DIRECT_RECOVERY | lag6/8 band9 | HIGH |

### B — Mandatory Safety Canaries (2, GT = MERGE)

| CASE_ID | DOC | PAGE | BASE | EXP | CASE_CLASS | WHY_INCLUDED | SAFETY_LEVEL |
|---|---|---|---|---|---|---|---|
| AMB-414 | med_001 | p20 | ABSTAIN | **ABSTAIN 不变** (context 不得翻转) | SAFETY_CANARY | band 含 4 伪 cell 片段 ('Left:'/'BIC values…'/'Right:'/'Learning'), 'FIG. 9:' lag=15=margin 组 | **CRITICAL (hard gate)** |
| AMB-422 | med_001 | p24 | ABSTAIN | **ABSTAIN 不变** | SAFETY_CANARY | 'FIG. 12:' lag=6 margin, 同构 | **CRITICAL (hard gate)** |

### C — Negative Controls (in-frame 2 + 描述性 4)

| CASE_ID | DOC | PAGE | BASE | EXP | CASE_CLASS | WHY_INCLUDED | SAFETY_LEVEL |
|---|---|---|---|---|---|---|---|
| AMB-519 | cs_001 | p3 | ABSTAIN | ABSTAIN 不变; 任何变化必须枚举+解释; GT 不一致 = F4 | NEG_PROSE_NUMERIC | 正文对 (band=1, margin lag24) — prose numeric token 边界 | MEDIUM |
| AMB-262 | efficientnet | p7 | ABSTAIN | ABSTAIN 不变 (same_y_band=F → context 应不可得) | NEG_DIFFERENT_BAND | 攻击 "非同带对误获 cell-context" 边界 | MEDIUM |
| (描述, 无 GT) LLaMA code-line seq | llama | p19/p22 | — | 仅记录 EIC-1 是否产出 context (期望: region 不可得 → no context) | NEG_CODE_LINE_NUMBER | 连续整数列边界攻击 | LOW |
| (描述, 无 GT) 2309 reference numbers | 2309.04040 | ref pages | — | 同上 | NEG_BIBLIOGRAPHY | 对齐数字堆边界 | LOW |
| (描述, 无 GT) 2212 p15 TOC | 2212.12794 | p15 | — | 同上 (最难混淆, 诚实记录) | NEG_TOC | 3-zone 共结构边界 | LOW |
| (描述, 无 GT) axis ticks | corpus 图页 | — | — | 同上; **in-frame 无此案例 = 如实标注, 不造 GT** | NEG_AXIS_TICK | 重复数字几何边界 | LOW |

### D — Existing Correct Controls (8, GT = KEEP_SEPARATE, 全部现状正确)

| CASE_ID | DOC | PAGE | BASE | EXP | CASE_CLASS | WHY_INCLUDED | SAFETY_LEVEL |
|---|---|---|---|---|---|---|---|
| AMB-005 | resnet | p1 | KEEP | **不变** | CORRECT_CONTROL + MIXED_ARTIFACT | 跨栏正文对 (margin lag30 × 右列) — prose/混合伪影边界攻击 | HIGH (collateral guard) |
| AMB-024 | resnet | p6 | KEEP | **不变** | CORRECT_CONTROL | 表内正确 cell-context 现状 | HIGH |
| AMB-034 | resnet | p6 | KEEP | **不变** | CORRECT_CONTROL + **VALUE_COLUMN_HIGH_RISK** | '21.59' lag6 — 攻击 value-column→row-number 误解释边界 | HIGH |
| AMB-074 | resnet | p8 | KEEP | **不变** | CORRECT_CONTROL | 表内正确现状 | HIGH |
| AMB-346 | efficientnet | p9 | KEEP | **不变** | CORRECT_CONTROL + CONFLICT_AGREEMENT_SITE | TLD 有输出页 → 验证 agree 路径 | HIGH |
| AMB-350 | efficientnet | p9 | KEEP | **不变** | 同上 | 同上 | HIGH |
| AMB-522 | cs_001 | p4 | KEEP | **不变** | CORRECT_CONTROL + CONFLICT_AGREEMENT_SITE | 同上 | HIGH |
| AMB-530 | cs_001 | p5 | KEEP | **不变** | 同上 | 同上 | HIGH |

矩阵合计: 决策度量 21 行 (1+8+2+2+8) + 描述 4 行。**本矩阵即冻结测试集。**

## 6. POSITIVE_TARGETS

A1 = S1 对象; A2 = S1 扩展 (recovery 计数分开统计: evidence recovery vs decision
change)。**禁止**为实现 AMB-135 反向修改研究对象/矩阵 (precommitted)。

## 7. SAFETY_CANARIES

S2 = **HARD SAFETY GATE**: 任一 canary MERGE/ABSTAIN → KEEP = SAFETY FAILURE →
REPLAY = FAIL, 即使 FP removal = 100%。canary 判定独立于 aggregate 指标, 单列报告。

## 8. NEGATIVE_CONTROLS

见 §5-C: VALUE_COLUMN (AMB-034 双角色) · AXIS_TICK (描述) · CODE_LINE_NUMBER
(LLaMA, 描述) · TOC (描述) · MIXED_ARTIFACT (AMB-005 双角色) · prose numeric
(AMB-519)。M4 计数: 不正确 context 暴露 = 0; 描述行只记 context 产生与否, 无决策度量。

## 9. CORRECT_CONTROLS

§5-D 8 例, 覆盖: normal prose (005) · numeric value column (034) · existing correct
table-context (024/074/346/350) · non-table structured numeric sequence (522/530 页
上下文 + 描述行)。S4: 预测变化 = 0 (任何变化 = F4 → FAIL)。

## 10. EIC-1 VALIDATION (语义边界检查, replay 内自动断言)

- 逐记录断言: `interpretation_status == "candidate"`; provenance 链 L2→LSP→RSC→EIC-1
  完整; schema 无 forbidden 字段 (table/row/column/cell/header/row-number/cell_id/
  table_id/score/confidence/...); preconditions 求值日志在案 (参数值 = 预注册定值);
- **静态断言**: L3 对象 (LSP/RSC) 输出中不得出现任何 L4 语义字段; EIC-1 输出只能是
  既有 observation form + table_info 注记;
- **禁止出现**: LSP→table/row/column/cell/different_cell; RSC→table region;
  Cell Context→validated fact (无 L5 记录时)。
- 注: Human Validation **不进入**本次 replay (§九) — 不模拟"人工确认某 case 是表";
  只验证 EIC-1 能在明确契约下生成可审计 Interpretation Candidate。

## 11. CONFLICT VALIDATION

- **agree 路径**: 346/350/522/530 (TLD 有输出页) — 双源一致时 context 准入且决策不变;
- **conflict 路径**: 预注册诚实预期 — in-frame 自然冲突案例可能不存在 (TLD 盲页正是
  EIC 目标页; TLD 有页其判定与 GT 一致)。若自然冲突不出现: **合成组合测试**
  (adapter 级单元检查: 输入 TLD 判定 + 相异 EIC 判定 → 断言输出 EVIDENCE_CONFLICT
  状态 + all-False + 无 preference 规则 + 冲突入 provenance)。合成测试仅测组合函数,
  不产生 corpus 决策。
- F10 判定: 冲突被 preference 解决 / 冲突未记录 / 出现 winner 字段 = FAIL。

## 12. DECISION_POLICY INVARIANCE (行为级验证, 非仅 diff)

1. **函数同一性**: ON 模式下决策函数源哈希 == OFF/存档版 (frozen copy 对照);
2. **行为等价**: 对每一条 EIC-1 **未**发射 context 的 case: ON 决策 == OFF 决策
   (逐案 diff = 0);
3. **输入组合唯一性**: ON 与 OFF 的全部差异必须可归约为 "is11_obs 内容由谁生产"
   (evidence input composition); 决策函数内**不得**出现新 if/else 分支 — 出现即
   MINIMAL_CONSUMER_INTEGRATION = FAILED (F2);
4. **公式化**: NEW EVIDENCE ≠ NEW DECISION POLICY — 新增的只是观察输入的组成方式。

## 13. OFF/ON ISOLATION

- **OFF**: adapter 不调用; 全 45-case 逐案记录与存档 baseline **byte-identical**
  (S9); 不影响无关 candidates/observations/registry/capability/runtime/GT;
- **ON**: 仅增加 EIC-1 消费整合通道 (第二生产者); flag 全局 (无 per-case 特判);
  影响面 = 明列 target evidence channel。

## 14. PROVENANCE CHECK

每条 Cell Context Evidence 四元组 (source / source artifact / input identity /
derivation trace) 完整可追溯 = S7 = 1.0; 缺任一 = F5。

## 15. DETERMINISM CHECK

ON 双跑: context 记录 + 决策 byte-identical = S8; 任何差异 = F6。

## 16. SUCCESS_CRITERIA (预定义)

| # | 标准 | 判定 |
|---|------|------|
| S1 | AMB-135 FP → corrected (经契约链) | 决策 = KEEP 且证据链完整 |
| S2 | caption canary 0 semantic flip | **HARD GATE** (违者 REPLAY=FAIL) |
| S3 | negative collateral = 0 | D 组 + 描述行零不当暴露 |
| S4 | existing correct controls unchanged | 8/8 决策不变 |
| S5 | semantic leakage = 0 | §10 断言全过 |
| S6 | decision policy modification = 0 | §12 四项全过 |
| S7 | provenance completeness = 1.0 | 四元组逐记录 |
| S8 | determinism = PASS | 双跑 byte-identical |
| S9 | OFF path = byte-identical | 45-case 对照存档 |
| S10 | frozen baseline drift = 0 | anchors/GT/层哈希复验 |

## 17. FAILURE_TAXONOMY

| # | 名称 | 判定条件 |
|---|------|----------|
| F1 | Semantic Leakage | L3 对象现 L4 字段 / L4 缺 candidate 标注 / 溯源缺 EIC-1 节点 |
| F2 | Decision Policy Change | 决策函数哈希变 / 行为等价破坏 / 函数内新分支 |
| F3 | Caption Safety Failure | 任一 canary → KEEP |
| F4 | Negative Collateral | D 组预测变化 / 非目标 case GT 不一致变化 |
| F5 | Provenance Failure | 四元组缺项 |
| F6 | Determinism Failure | 双跑差异 |
| F7 | OFF-path Drift | OFF ≠ 存档 baseline (非 byte-identical) |
| F8 | Integration Contract Failure | 准入点发射既有形态之外字段 / 组合层出现偏好 |
| F9 | EIC-1 Boundary Failure | 禁止推断出现 / 无 preconditions 即发射 / scope 越界 |
| F10 | Evidence Conflict Handling Failure | 冲突被偏好解决 / 未记录 / winner 字段 |

## 18. RED-TEAM (Patch Accumulation Precommitment)

**问**: 若 AMB-135 不通过, 是否会自然地添加 M6/M7/M8/M9? **答案必须是 NO — 预承诺**:
唯一允许的响应 = (a) 逐层归因 (precondition 未满足 / 参数定值不当 / 推导缺陷 /
consumer contract gap), (b) 经治理修订 EIC-1, (c) 宣告失败。**堆 predicate = 禁止**
(回到 Research Object / EIC, 不堆规则)。

## 19. SCIENTIFIC_CLAIM_BOUNDARY

GT-confirmed positive = 1。即使 REPLAY PASS, 只允许表述为: **"在当前冻结测试框架中,
验证了该 Consumer Integration 机制能够处理已识别的结构切片失败模式。"** 禁止声称:
解决 vector table recovery / 解决 table detection / 通用 row-number recognition /
跨文档泛化 / 方法普适。canary/负例结果同样只作边界记录, 不作泛化依据。

## 20. IMPLEMENTATION_AUTHORIZATION

**NOT AUTHORIZED** (本文件 = 设计 + 授权申请; 实施需下一阶段独立批准)。

## 21. REPLAY_AUTHORIZATION

**NOT AUTHORIZED**。批准前置: EIC-1 经治理批准 + canary 边界生效 + 预注册参数定值 +
OFF/ON 隔离实现评审通过。

## 22. NEXT_STEP

授权后执行本文件 §5 矩阵的 Isolated Replay (按 §16/§17 判定); 未授权则维持 STOP。

## 23. Final Gate

```text
==================================================
M-B PHASE 3 — ISOLATED REPLAY DESIGN / AUTHORIZATION REQUEST
==================================================
STATUS: DESIGN-READY
REPLAY_MATRIX: 冻结 (21 决策行 + 4 描述行; 结果无关, 不得增删)
POSITIVE: AMB-135 (primary) + 8 DIRECT (recovery 分开统计)
SAFETY: 2 canaries = HARD GATE (flip => FAIL, 不可抵消)
NEGATIVE: VALUE_COLUMN / AXIS_TICK / CODE_LINE_NUMBER / TOC / MIXED / PROSE
CONTROLS: 8 correct (S4 = 0 变化) + 4 conflict-agreement sites
EIC-1: candidate 状态 + 全链 provenance + 禁止推断断言
CONFLICT: agree 实测 + conflict 合成组合测试 (EVIDENCE_CONFLICT, 无 winner)
DECISION_POLICY_INVARIANCE: 行为级四项验证 (新证据 ≠ 新政策)
OFF/ON: OFF byte-identical; ON 仅 target channel
SUCCESS: S1-S10 (S2 hard gate)    FAILURE: F1-F10
RED_TEAM: patch accumulation precommitted FORBIDDEN
CLAIM_BOUNDARY: 框架内机制验证 (GT-confirmed positive = 1, 禁普适化)
IMPLEMENTATION = NOT AUTHORIZED
REPLAY = NOT AUTHORIZED
GT_MODIFICATION = NONE    FROZEN_BASELINE = INTACT
STOP = TRUE
==================================================
```
