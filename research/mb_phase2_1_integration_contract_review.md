# M-B Phase 2.1 — Integration Contract & Semantic Boundary Review

> 性质: READ-ONLY / ANALYSIS-ONLY / DESIGN REVIEW ONLY。零代码/零 frozen/零 GT/零 TLD/
> 零 IS-11 决策逻辑修改。审查对象 = `tmp/mb_phase2_minimal_consumer_integration_design.md`。
> 核心问题: **M-B 接入 IS-11 时, 能否在不获得新语义/决策权的前提下让 IS-11 消费已有
> 几何结构证据?**

---

## 1. Executive Summary

审查结论: Phase 2 的**架构方向成立** (复用 IS-11 消费契约 + 薄 adapter + 零决策改动),
但**按原文书写存在 1 处语义泄漏**: 设计 walkthrough 让 adapter 产出
`{is_in_table, different_cell}` 形状的 is11_obs 兼容记录 — 经代码级核实, `different_cell`
在现有系统中**以"已检测表格"为前提** (TLD: table bbox 包含 → 行/列索引), 而
"co-structured region 内不同 LSP" **没有** table 判定前提 → 该映射不是既有契约, 是
**新的语义升级** (`SEMANTIC_MAPPING_GAP = TRUE`)。另外, 三案例共存规则 (agree/single/
conflict-abstain) 在现有系统中**不存在** (harness 只有单生产者) → 属 NEW DECISION
POLICY, 且 CONFLICT_CONTRACT_UNRESOLVED。canary 实测: caption 行在纯 Level-2 分区
层面与表格行**不可区分** (p20 band 有 4 个伪 cell 成员) → 风险实测为真。

**判定: CONDITIONAL_PASS** — 主体设计成立, 但必须先完成 3 项最小契约修正 (见 §13),
replay 在此之前 BLOCKED。

## 2. 8 Questions Review

- **Q1 (8 还是 9?)**: **9** (逐案对账见 §3; Phase 2 的 "8" 为算术笔误, 其自身列表即 9)。
- **Q2 (为何属 M-B?)**: 9 例全部 = Gap C (Consumer/Integration): 原子级事实已实测存在
  (same_band + 双侧分区结构), LSP 可构造, IS-11 未消费。无一需要新 detector/OCR/
  vector-line extraction (唯一 partial: AMB-313 的 'Test Size' lag=0, 分区推导可能失败)。
- **Q3 (LSP 是什么?)**: 正式契约见 §4 — Structural Object, 非语义对象; 通过 PH-02 复活
  检查 (非 M1-M5 合取)。
- **Q4 (LSP 能否直接产生 different_cell?)**: **不能** — 代码级证明见 §5:
  `SEMANTIC_MAPPING_GAP = TRUE`。
- **Q5 (TLD vs Geometry 解释权?)**: 都没有解释权; 但 Phase 2 的三案例规则是**新增决策
  策略** (非既有契约) → 必须显式契约化, 且 CONFLICT_CONTRACT_UNRESOLVED (§6)。
- **Q6 (caption canary failure path?)**: 实测确认, 全链见 §7 — 风险为真, flip 点 =
  IS-11 消费决策。
- **Q7 (semantic upgrade/leakage?)**: 发现 **1 处** (is11_obs 形状发射) → 修正后 0
  (§8)。
- **Q8 (OFF byte-identical?)**: 设计层 **PASS** (§9), 实现评审需复核 flag 包裹完整性。

## 3. M-B Canonical Case Reconciliation (Q1/Q2 — 逐案独立理由, 禁止总数反推)

| Case | Doc | Page | Failure | Why M-B (cell-context 路线) | Why not M-A/M-E/其他 | Include |
|------|-----|-----:|---------|------------------------------|----------------------|---------|
| AMB-135 | eff | 5 | FP-merge (IS-01∧IS-02) | same_band=T, h=30.02, 双侧分区 (lag 10 × lag 6), 12 列簇共结构 | 非 caption (GT=KEEP); band/分区结构在 → 非 M-E 观察缺失 | **YES** |
| AMB-130 | eff | 5 | abstain | 表头对 same_band=4, 分区 lag3/lag2 | 非 caption; 非 M-E (事实在) | **YES** (弱成员注记) |
| AMB-313 | eff | 8 | abstain | 表头对 same_band=3 | 非 caption/M-E | **YES** ⚠ 'Test Size' lag=0 → LSP 推导可能失败, recovery 不确定 (H2 逐例归因) |
| AMB-457 | cs | 3 | abstain | 表头对 lag8/lag3, band=9 | 同上 | **YES** |
| AMB-462 | cs | 3 | abstain | 'WGe' lag1 (弱) × 'Avg.' lag8, band=9 | 同上 | **YES** (弱成员注记) |
| AMB-467 | cs | 3 | abstain | '37.0' lag6 × '60.0' lag8, band=9 | 同上 | **YES** |
| AMB-483 | cs | 3 | abstain | lag7 × lag6, band=9 | 同上 | **YES** |
| AMB-505 | cs | 3 | abstain | lag8 × lag7, band=9 | 同上 | **YES** |
| AMB-514 | cs | 3 | abstain | lag6 × lag8, band=9 | 同上 | **YES** |
| AMB-262 | eff | 7 | abstain | — | **same_y_band=False** (BELOW, v=17.6): 非同带对, cell-context 路线不适用 (竖邻机制) | NO |
| AMB-519 | cs | 3 | abstain | — | 正文对 (band=1, margin 组 lag24): CC-04 列盲机制 | NO |

```text
M_B_DIRECT_CANONICAL_COUNT = 9
M_B_DIRECT_CANONICAL_CASES = [AMB-135, AMB-130, AMB-313, AMB-457, AMB-462, AMB-467, AMB-483, AMB-505, AMB-514]
RECONCILIATION_STATUS = PASS
```
Gap 分类: 9/9 = **C (Consumer/Integration)**; AMB-313 附 partial-derivation 注记;
无一滑入 A (Observation Gap) 或需要 vector-line/OCR。

## 4. LSP Formal Semantic Contract (Q3)

**定义**: LocalStructuralPartition 是基于 Frozen Geometry Evidence 构造的、局部空间
范围内共享同一冻结结构关系 (对齐轴成员资格) 的 atom 集合的结构分区; 携带 membership、
spatial scope (bbox 并集)、relation identity、continuity/adjacency 描述与 provenance,
由冻结 store 上的纯函数确定性构造。

**Q3.1**: LSP 是 **Structural Object** (非 Geometry Object — 它是推导的成员分组;
非 Semantic Object)。其 structural meaning 止于: **成员资格 + 空间范围 + 关系同一性 +
局部连续/邻接描述**。它不解释任何角色。

**禁止输出/声明** (缺席即合规): `is_table / is_cell / is_row / is_column / is_header /
is_row_number / table_id / cell_id / semantic_role / is_numeric_column / is_caption /
is_code` — 特别是 `is_row_number_column` 及任何等价物。

**PH-02 复活检查**: PASS — LSP ≠ `left_alignment_group + M1/M2/M3/M4/M5`。PH-02 的
对象是**整组**作为决策基底 + 多谓词连贯性合取 (15 组预注册全败); LSP 是**单关系分区
索引** (成员资格), 无阈值、无连贯性打分、无决策, 可复用可组合, 与 row-number 语义
无关。二者研究对象不同层。

## 5. LSP → Structural Context → IS-11 Mapping (Q4 — 代码级 mapping audit)

实测数据流 (现有系统, `tmp/is11_machine_evaluation.py`):

```text
TLD producer (现唯一):
  detect_tables_from_lines → tables[]
  is_in_table   = 候选 center ∈ 某 table bbox          (L140-170)
  cell          = (row_idx, col_idx) — table 内 vline 行×列索引, 近距回退 dist<30 (L172-235)
  different_cell = 双方有 cell 且不等; 或恰一方在表内   (L237-245)  ← 宽松析支, 已存在
consumer:
  experimental_c_decision: different_cell→KEEP; same_cell→MERGE; 否则 §9.3 基线 (L261-279)
```

**判定**: `different_cell` 的语义 = **"已检测表格内的不同 cell"** — 以 table 判定为
前提。Phase 2 walkthrough 的 `is11_obs 兼容记录 {is_in_table=T, different_cell=T}`
让 adapter 在**没有 table 判定**的情况下声明 cell 语义 = **生产者侧语义升级**。

```text
SEMANTIC_MAPPING_GAP = TRUE
```
(现有 IS-11 contract **未**规定任何"结构分区不等 → different_cell"的准入通道。)
**最小修正**: adapter 只发 `StructuralContextEvidence`; `different_partition →
cell-context` 的映射必须成为**显式的、单独评审授权的 IS-11 契约扩展** (NEW DECISION
POLICY — 见 §6/§13-C1)。该扩展是整个集成中唯一的语义闸门, 不得藏在 adapter 内。

## 6. TLD/Geometry Coexistence Contract (Q5/§10/§12)

- 三案例规则 (agree→admit / single→admit / conflict→abstain) 在现有系统**不存在**
  (harness 单生产者) → **Case B: NEW DECISION POLICY** — 不得冒充 evidence adapter 的一部分。
- **CONFLICT_CONTRACT_UNRESOLVED**: 谁发现冲突 (准入组合点) / 谁记录 (provenance log) /
  谁最终决策 (consumer 落回 §9.3 基线) — 现有系统无此契约; Phase 2 不得自行添加为
  "已有事实", 必须作为契约扩展的一部分被显式授权。**replay 前必须解决**。
- 无 arbitration authority: 无 priority/score/winner/override — 方向正确, 但须随契约
  扩展一起被评审, 而非默认生效。

## 7. M-A Caption Safety Canary Trace (Q6 — 升级为 MANDATORY SAFETY CANARIES)

实测冻结事实:

```text
med p20 (AMB-414, GT=MERGE, C=ABSTAIN):
  'FIG. 9:'@85.04  lag=15 (正文左边距组! lag_x=[85,87], y-ext=393pt) band=4
  'Left:'@143.46   lag=1  band=4
  band 4 成员 = ['Left:'@143.5, 'BIC values…'@178.6, 'Right:'@439.1, 'Learning'@482.0]
  → caption 行在 Level-2 呈 4 个"伪 cell"片段 — 与表格行不可区分
med p24 (AMB-422, GT=MERGE, C=ABSTAIN):
  'FIG. 12:'@85.04 lag=6 (margin 组, y-ext=612pt) band=1
  'Distribution of errors…'@139.12 lag=2 band=1
```

**Failure path**: ① caption label 与 continuation 起始 x0 不同 → 必然形成不同 LSP
(几乎所有同行对都如此 — 信号近内容无关); ② 不应解释为 table cell 的原因: caption
"列"是散文延续片段, 无跨带稳定列 (band 重数低, 'FIG. 9:' 的 lag 是散文 margin 组而非
表列) — 但这一区分在纯 Level-2 分区层面**不可得**; ③ adapter ON → different_partition
context 大概率产出; ④ → 消费契约 different_cell→KEEP; ⑤ **flip 发生在 IS-11 消费决策**
(abstain→KEEP, GT=MERGE → 错)。

| Canary | GT | Baseline | M-B predicted risk | Flip allowed? |
|--------|----|----------|--------------------|---------------|
| M-A-1 (AMB-414) | MERGE | abstain | KEEP risk (实测路径成立) | **NO** |
| M-A-2 (AMB-422) | MERGE | abstain | KEEP risk (同构) | **NO** |

任一 `MERGE/ABSTAIN → KEEP` = **M-B SAFETY FAILURE**, 不得被总体 accuracy 抵消。

## 8. Semantic Leakage Audit (Q7 — 逐层)

| Layer | Allowed | Forbidden | Phase 2 原文判定 |
|-------|---------|-----------|------------------|
| Geometry (frozen) | bbox/x/y/gap/alignment | table/cell 语义 | PASS |
| Atomic Observation | measured relation | decision | PASS |
| LSP | partition membership/scope/relation | row-number/table/cell 标签 | PASS |
| Structural Context Evidence | structural relation (same_region/different_partition) | confidence/score/is_in_table/different_cell | **FAIL — is11_obs 形状发射 = 1 处泄漏** |
| IS-11 | existing interpretation | new authority | PASS (决策函数未动) |

```text
SEMANTIC_LEAKAGE_COUNT (Phase 2 原文) = 1  →  BLOCKED
修正后 (adapter 只发 StructuralContextEvidence; 映射走显式契约扩展) = 0
```

## 9. OFF-Path Isolation Audit (Q8)

- OFF: adapter 不调用 → is11_obs 单源 (TLD) → 无新字段/无序变化/无序列化变化/无 GT/TLD/
  决策变化 → byte-identical。要求: flag gate 必须包裹**全部**新增路径 (实现评审复核点)。
- ON: 只增加 Frozen Geometry → LSP → Structural Context Evidence (只读推导), frozen
  artifacts 零改动。

```text
OFF_PATH_ISOLATION = PASS (design-level; 实现评审复核)
FROZEN_BASELINE_DRIFT = 0 (实测 anchors_drift=0)
ROLLBACK = FLAG_OFF
```

## 10. Architecture Classification (§16)

**Type B (New Research Object — LSP) + Type A 路径 (pure consumer integration)**:
证据存在 (审计已证), 需要构造的新中间对象 = LSP/Regional Context (仍非语义), 集成面 =
一个生产者插拔点。非 Type C (无新观测需求 — NEW_OBSERVATION_MEASUREMENT_REQUEST =
NONE 维持)。**Type D 风险在 Phase 2 原文中真实存在** (is11_obs 形状发射 = adapter 变
隐形 cell 解释器) — 本审查将其拦截并给出修正。

## 11. Red-Team Review (§19 — 防隐形 Table Detector)

patch-accumulation 结构性入口**存在**: 若未来向 LSP 推导中追加 M6/M7…("enough
conditions → table-like"), LSP 即变相 detector。Guardrails (纳入契约扩展的强制条款):
1. LSP 只能由**契约中枚举的冻结单关系**定义 (对齐成员资格等), 不得由"是否像 table"
   定义 — `LSP = locally coherent spatial partition`, 永非 `table-like cluster`;
2. 任何新关系/新谓词 = **契约修订 (governance gate)**, 不是 adapter 代码内变更;
3. forbidden-fields 在 schema 层强制 (缺席即合规, 出现即 REJECT);
4. 映射契约是**唯一**语义闸门 — 任何第二语义入口 = BLOCK。

## 12. Risks (汇总)

1. different_partition 信号近内容无关 (任何同带异 x0 对皆可得) → 无 table 门时泄漏面大
   — 这正是映射契约必须显式评审的原因;
2. caption canary 风险实测为真 (非假设);
3. TOC 类 3-zone 共结构 (审计已标最难混淆);
4. AMB-313 lag=0 → LSP 推导可能失败 (诚实预期);
5. 共存/冲突契约若实现时被简化为隐式规则 → authority 回归;
6. 参数槽 (region 成员数/容差) 预注册前不得定值。

## 13. Minimal Required Corrections (只记录, 不实施)

- **C1 (必须)**: 从 Design B 移除 `is11_obs` 形状发射; adapter 只产出
  `StructuralContextEvidence`。"Structural Context → IS-11 observation" 的映射
  (different_partition → cell-context 等价) 单独成文为 **IS-11 契约扩展 + NEW DECISION
  POLICY**, 显式评审授权后方可进入 replay。
- **C2 (必须)**: CONFLICT_CONTRACT 成文 (发现者=准入组合点 / 记录者=provenance log /
  决策者=consumer 基线回退), 与 C1 同批授权; 解决 CONFLICT_CONTRACT_UNRESOLVED。
- **C3 (必须)**: 层级显式化 — Geometry → LSP → **Regional Structural Context** → Cell
  Context → IS-11, 每个箭头一个具名映射契约; Phase 2 的 LSP→different_cell 直连删除。
- **C4 (必须)**: caption canaries 正式升级为 MANDATORY SAFETY CANARIES (flip = SAFETY
  FAILURE, 不可被总体指标抵消)。
- **C5 (记录)**: AMB-313 lag=0 推导失败可能性 + 弱成员案例 (130/462) 的诚实预期归因。
- **C6 (记录)**: Red-Team guardrails (§11) 写入契约扩展条款。

## 14. Final Gate (§23)

```text
PH02 = REJECTED
PH02B = NOT AUTHORIZED

M-B PHASE 2 = CONDITIONAL PASS (按 C1-C3 修正后成立)
M-B PHASE 2.1 = CONDITIONAL_PASS

M_B_DIRECT_CANONICAL_COUNT = 9        RECONCILIATION = PASS
LSP_SEMANTIC_STATUS = STRUCTURAL_OBJECT_NON_SEMANTIC (PH-02 复活检查 PASS)
LSP_TO_DIFFERENT_CELL_MAPPING = SEMANTIC_MAPPING_GAP = TRUE (代码级; 需显式契约扩展)
TLD_GEOMETRY_CONFLICT_CONTRACT = CONFLICT_CONTRACT_UNRESOLVED → 契约扩展中成文
CAPTION_CANARY_STATUS = MANDATORY_SAFETY_CANARIES (flip = SAFETY FAILURE; 风险实测为真)
SEMANTIC_LEAKAGE = 1 (Phase 2 原文) → 修正后 0; 修正前 replay BLOCKED
OFF_PATH_ISOLATION = PASS (design-level)
FROZEN_BASELINE_STATUS = INTACT (drift 0)
ARCHITECTURE_TYPE = Type B (LSP) + Type A 路径; Type D 风险已拦截
RUNTIME_AUTHORITY = ZERO

IMPLEMENTATION = NOT AUTHORIZED
EXPERIMENT = NOT AUTHORIZED
GT_MODIFICATION = NONE
ATOMIC_OBSERVATION_MODIFICATION = NONE
TLD_MODIFICATION = NONE
IS11_DECISION_MODIFICATION = NONE
PERCEPTION_PRODUCTION_MODIFICATION = NONE
FROZEN_BASELINE = INTACT
PRODUCTION = FALSE

NEXT_STEP = REDESIGN (C1-C3 最小契约修正, design-only)
           → 完成并授权后方可提请 M-B Phase 3 — Isolated Replay
             (最小集: 1 FP + 2 canaries + 最高风险边界负例 + 选定 controls)
STOP = TRUE
```
