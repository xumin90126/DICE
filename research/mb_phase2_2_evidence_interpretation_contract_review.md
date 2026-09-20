# M-B Phase 2.2 — Evidence Interpretation Contract Review

> 性质: DESIGN / CONTRACT REVIEW ONLY。零 frozen 代码修改、零 GT、零 TLD、零 IS-11
> decision logic 修改、零实验。RQ: 能否定义一个**最小、可审计、无语义越权的 Evidence
> Interpretation Contract**, 使 Frozen Geometry → LSP → Regional Structural Context →
> Cell Context Evidence → existing IS-11 observation contract, 而**不改变 existing
> IS-11 decision policy**? 重点不是"如何修 FP", 而是: 新结构证据如何获得语义解释,
> 语义解释的 authority 到底在哪一层产生。

---

## 1. STATUS

**M-B PHASE 2.2 = PASS / DESIGN-READY** (Gate A-O 全满足, 见 §19)。IMPLEMENTATION =
NOT AUTHORIZED; REPLAY = NOT AUTHORIZED; 下一阶段只能是 Phase 3 Isolated Replay
Design / Authorization Request; 本阶段不自行动。

## 2. OBJECTIVE

收敛 M-B 的 Evidence Interpretation Contract (EIC): 固定 Authority Gradient、封死
producer-side semantic upgrade、把 Phase 2.1 的 SEMANTIC_MAPPING_GAP 转化为一个显式、
可审计、可治理的契约 — 而非新增 decision policy。

## 3. FROZEN_BASELINE_STATUS

INTACT (anchors_drift=0, GT ✅ sha=7349963d…, layer registry 7/7)。本轮零修改。

## 4. AUTHORITY_GRADIENT (固定)

| 层 | 名称 | 内容 | 升级条件 |
|----|------|------|----------|
| L0 | Raw Document | PDF 字节 | — |
| L1 | Observation | "存在一个数字 4" | frozen P1 |
| L2 | Geometric Evidence | "4 的 bbox/x0/center/y/width = …"; pairwise; band | frozen P2, detector/source-backed |
| L3 | Structural Evidence | "4 与 1–9 形成局部垂直结构段" (LSP); 共现组织 (RSC) | frozen 事实上的**纯函数推导**, 零语义 |
| L4 | Semantic Interpretation | "该结构可能对应表格第一列 / 可能对应代码行号" | **必须有 EIC**; 无契约 = 只能停留为 Structural Evidence / Interpretation Candidate |
| L5 | Human Validated Knowledge | "人工确认: 这一类模式在定义边界内可解释为 row-index-like structure" | 人审发生在 **reusable pattern 级** + 边界/负例/记录 |
| L6 | Capability | 经 Human Validation + Registration 的知识转为可复用能力资产 | 仅自 L5 |

**固定规则**: L2/L3 不得自动获得 L4 authority; L4 不得自动获得 L5 authority; 只有
L5 形成 governed reusable knowledge; Interpretation Candidate 永不入 Runtime Authority。

## 5. NO_SEMANTIC_CLOSURE_RULE (正式写入契约)

**低层结构证据不得自动完成高层语义解释。** 禁止跃迁 (无 EIC 即非法):
bbox → table · alignment group → row-number column · vertical sequence → table row ·
local partition → different_cell · regional structure → table semantics ·
structural similarity → capability。
无契约时只能保留为 Structural Evidence / Interpretation Candidate, 不得升级为
Semantic Fact。本规则适用于包括 M-B 自身在内的**一切未来路径**。

## 6. LSP_CONTRACT (最小重定义)

LSP = Local Structural Partition = 基于冻结证据、局部空间范围内共享同一冻结结构关系
(对齐轴成员资格) 的 atom 集合的结构分区; 冻结 store 上的纯函数。

**只描述**: ① membership ② spatial scope (bbox 并集) ③ relation identity ④ local
continuity ⑤ provenance。
**禁止描述**: table / row / column / cell / header / row-number / code-line /
semantic role / KEEP-MERGE-REJECT / decision / confidence / score / recommendation。
**用词纪律**: "column" 若指语义对象即禁止; 仅允许 **"geometric column segment"**
(= structural object: 共享对齐关系的成员片段) — 与 **"semantic table column"**
(L4+, 需 EIC/L5) 严格区分。

**Q1 答**: LSP 的 semantic authority 止于**零** — 它只有结构描述权; 解释权从 L4
(EIC) 才开始。

## 7. REGIONAL_STRUCTURAL_CONTEXT_CONTRACT

RSC = 共现的局部结构对象的组织事实。**仍然完全属于 structural evidence** (Q2 答 = YES)。

**表达**: 哪些 LSP 共同出现 · 空间范围 (成员 bbox 并集) · 局部 partition 关系 ·
相邻结构关系 · vertical/horizontal continuity · provenance · source evidence refs。
**不宣称**: "table region"。**上限语句**: "该区域具有某种局部结构组织" —
**Regional Structural Context ≠ Table Semantics**。schema 无 table/cell 字段;
任何此类字段出现 = REJECT。

## 8. CELL_CONTEXT_EVIDENCE_CONTRACT — EIC-1 (核心语义闸门)

**Q3 答 (三者严格区分)**: Cell Context Evidence = **B: Semantic Interpretation**。
- 不是 A (structural evidence): "different cell" 在结构事实 (same_region ∧
  different_partition) 之上**增加了**解释内容;
- 不是 C (validated fact): 无 L5 人审;
- 是 B: 由 EIC-1 产出的、显式标注 `interpretation_status = candidate` 的解释。

**Q4 答 (authority 从哪里来)**: 三重来源, 缺一不可 — ① **EIC-1 文档本身**
(显式、可审计、确定性、经治理批准); ② 到 L2/L3 的完整溯源链; ③ 边界 = 在 L5
(pattern 级人审) 之前, 该解释只是 Interpretation Candidate, 仅存在于隔离实验上下文,
**无 runtime authority, 非 capability**。

**Q5 答 (为什么 IS-11 能消费)**: existing IS-11 observation contract 的证据形态
**本来就消费生产者解释** — TLD 的 cell 事实本身就是未验证的启发式解释 (bbox 包含 +
dist<30 近距回退 + 行列索引); 既有 8/8 正确即建立在 TLD 解释之上。EIC-1 产出的是
**同一形态、同一字段语义、同一状态约定**的解释 — 在既有契约的证据形态之内。
但纯 L3 结构布尔 (same_region/different_partition) **不在**既有契约形态内 →
**没有 EIC-1 就不可消费** — 这正是契约是闸门的含义。

**EIC-1 十要素**:

1. **Preconditions**: region 共组织可推导 (≥2 个可分辨 LSP + y-overlap + 跨带列稳定;
   参数为预注册槽, 不定值) ∧ 双方 atom 分区可解析 ∧ (TLD 无输出 或 与之相容)。
2. **Input Evidence**: L2/L3 冻结事实 + provenance (逐链)。
3. **Allowed Relations** → 既有字段语义映射 (全部复用既有状态约定):
   | 结构事实 | 既有 observation form |
   |---|---|
   | same_region ∧ different_partition (+preconditions) | {is_in_table: T, same_cell: F, different_cell: T} |
   | same_region ∧ same_partition (+preconditions) | {is_in_table: T, same_cell: T, different_cell: F} |
   | 分区/区域不可解析 | {F,F,F} + table_info.reason="interpretation_unavailable" (既有 "unknown" 约定) |
   | TLD 冲突 | {F,F,F} + table_info.evidence_conflict (见 §9) |
   注: 决策函数实测**只读** different_cell/same_cell (is_in_table 不门控); all-False
   的既有语义 = "cell membership unknown → base decision" (代码注释原文) — 状态复用,
   非新政策。
4. **Interpretation Scope**: cell-context 主张**仅限**被评估对 + 所在共组织区域;
   无全局 table 主张; 无 row/column 角色主张。
5. **Semantic Authority**: EIC-1 文档 (治理批准) + 溯源链; `interpretation_status =
   "candidate"` 直至 L5。
6. **Provenance**: L2→L3→EIC-1→observation form 全链逐记录 (source/artifact/input/
   trace 四元组)。
7. **Failure / Unknown State**: 分区不可解析 (实测例: AMB-313 'Test Size' lag=0) 或
   region 不可推导 → all-False + reason (既有约定, 不强解)。
8. **Conflict State**: 见 §9。
9. **Forbidden Inferences**: region → table · partition → cell (作为事实) · partition
   → row-number column · structural similarity → capability · confidence/score ·
   per-instance 语义标签。
10. **Human Validation Boundary**: L5 pattern 级 (见 §12); **负例集必须包含** caption/
    code/TOC/value-column — 这是 caption-vs-table 边界的正式治理位置。

## 9. TLD_GEOMETRY_CONFLICT_CONTRACT (Q7)

**原则**: Discovery ≠ Arbitration; Evidence Composition ≠ Decision Selection。

- 冲突首先成为 **observable evidence state + provenance**: `table_info.evidence_conflict
  = {tld_verdict, eic_verdict, refs}` + provenance log — 利用既有自由字段 table_info,
  不加决策输入字段。
- **EVIDENCE_CONFLICT ≠ winner**: 无 "相信 TLD / 相信 Geometry / 更强证据" 规则;
  冲突时**复合解释不可得** → 发射既有 all-False ("unknown") 状态 + 冲突记录。
  诚实披露: 这在消费侧行为上等价于回退基线 — 但它是**既有 unknown 状态语义的复用**
  (代码注释原文 "cell membership unknown → use base decision"), 不是新 fallback
  policy; 任何 source 都未被优先。现有代码**无**多源 fallback contract → 本阶段不创造
  一个; 该复合约定随 EIC-1 一并送治理批准。
- 本阶段**禁止**: conflict → 自动 winner / 自动基线选择 / retry / correction。

## 10. AMB135_WALKTHROUGH (逐层 authority 标注)

```text
L2 Geometry Evidence [frozen, source-backed]:
   '4'@320.35: lag=10 ('i','1'..'9','1'@263.4) · 'MBConv6,k5x5'@354.14: lag=6
   pairwise: same_y_band=T, h_gap=30.02, v_gap=0
L3 Structural Evidence [纯函数推导, 零语义]:
   LSP-a (10 成员对齐分区) · LSP-b (6 成员分区) — 不同 geometric column segment
   RSC-R: ≥2 分区共现 + y-overlap + 跨带列稳定 (p5 表区 12 列簇)
   结构事实: same_region(A,B,R)=T ∧ different_partition(A,B)=T
L4 [EIC-1: preconditions 满足 → 显式解释, scope=对+区域]:
   Cell Context Evidence (interpretation_status="candidate"):
   "A 与 B 处于同一结构组织区域的不同局部分区 — MAY be interpreted as
    different-cell-like context"
   → 既有 observation form: {is_in_table:T, same_cell:F, different_cell:T,
      table_info:{source:"eic-1", region_ref:R, provenance, interpretation_status:"candidate"}}
L4→consumer [零改动]: experimental_c_decision: different_cell → KEEP_SEPARATE
L5: 未发生 — 本主张在实验上下文内保持 candidate 状态, 无 runtime authority
```
每步责任: L2/L3 = evidence; EIC-1 = 唯一解释闸门 (preconditions/scope/provenance);
consumer = 既有决策。**全程无 "LSP → different_cell" 直连**。

## 11. CAPTION_SAFETY_CANARIES

```text
CAPTION_CANARY = MANDATORY SAFETY BOUNDARY
M-A-1 (AMB-414, med p20, GT=MERGE, baseline=abstain): band 含 'Left:'|'BIC values…'|
  'Right:'|'Learning' 4 个伪 cell 片段; 'FIG. 9:' lag=15 = 正文 margin 组
M-A-2 (AMB-422, med p24, GT=MERGE, baseline=abstain): 同构 ('FIG. 12:' lag=6 margin)
```
任何新 interpretation contract 导致 GT MERGE/ABSTAIN → KEEP = **SAFETY FAILURE**,
不得被其他 case 的 aggregate improvement 抵消。核心原则: **Geometry ≠ Table Semantics**。
EIC-1 在 L3 **不**区分 caption (诚实: 纯分区层面不可区分) — caption 边界的治理位置 =
L5 pattern 验证的**负例集** + canary 硬边界, 二者并存。

## 12. HUMAN_VALIDATION_BOUNDARY (Q8)

**最小 reusable abstraction unit = Interpretation Pattern**: "一类由规定结构条件约束的
local structural pattern 在定义边界内可解释为 X-like structure" — 附 applicability
boundary · negative examples · exceptions · provenance · validation record。

正例 (不是): "人工确认这个 PDF 第 5 页的 1–9 是表格第一列" (instance 级 = annotation
tool, 禁)。是: "人工确认满足 [EIC-1 preconditions 全集] 的局部结构 pattern 可解释为
row-index-like table structure, 边界 = …, 负例 = caption/code/TOC/value-column"。
证据不足形成 reusable interpretation 时 → **UNKNOWN / UNRESOLVED**, 不强行泛化。
Structural Evidence vs Interpretation Candidate vs Validated Knowledge vs Capability
四态严格分层; Interpretation Candidate ≠ Capability, 不得进入 Runtime Authority。

## 13. RED_TEAM_RESULTS (10 项主动攻击)

| # | 攻击 | 判定 | Guard |
|---|------|------|-------|
| 1 | LSP 偷偷变 table detector? | 拦截 | 单一冻结关系定义 + forbidden schema 字段 + 新关系=契约修订 |
| 2 | RSC 偷偷变 table region? | 拦截 | 上限语句 "局部结构组织" + schema 无 table 字段 |
| 3 | Cell Context 偷偷变 semantic fact? | 拦截 | `interpretation_status="candidate"` + 无 runtime authority + L5 门槛 |
| 4 | conflict 偷偷变 winner selection? | 拦截 | EVIDENCE_CONFLICT observable + 无优先规则 + 诚实披露行为等价性 |
| 5 | 为修 AMB-135 引入 M6/M7/M8? | 无 | 全部事实来自冻结 lag/band/pairwise; EIC preconditions = 解释准入条件 (预注册槽), 非 decision-producing 谓词 |
| 6 | caption 被误解释为 table? | 风险在, 双闸门 | canary 硬边界 (SAFETY FAILURE) + L5 负例集 |
| 7 | TOC 被误解释? | 同上 | TOC ∈ L5 负例集; 实验期 descriptive 观察 |
| 8 | code line number 被误解释为 row-number? | 同上 | 角色主张只在 L5 pattern 级; L3 无角色 |
| 9 | value column 被误解释为 row-number column? | 同上 | Level-2 不区分角色 (设计使然); 角色语义仅 L5 |
| 10 | Human Validation 退化成 instance annotation? | 拦截 | 验证对象 = pattern class + boundary + negatives + record; UNKNOWN 允许 |

## 14. MINIMALITY_REVIEW

不新增: vector detector / OCR / parser / table detector / predicate / threshold /
alignment heuristic / semantic classifier。新增物仅: ① EIC-1 契约文档 (治理对象);
② LSP/RSC 只读推导模块 (design-only, 参数预注册槽); ③ 生产者准入点 (potential
implementation, flag OFF 默认)。现有 frozen evidence 已足以表达全部 contract
prerequisite (M-B 审计已证: bbox/lag/band/pairwise/共现均在冻结面上)。

## 15. DECISION_POLICY_CHANGE_REQUIRED

**FALSE** — 理由: ① 决策函数 `experimental_c_decision` 零改动 (实测只读
different_cell/same_cell); ② 状态映射**复用既有字段语义与既有状态约定** (all-False =
既有 "unknown" 语义); ③ "partition→cell-context mapping" 由 **Evidence Interpretation
Contract** 承载 (evidence → 既有 observation form 的合法解释), 不是 decision policy
(证据 → KEEP/MERGE/ABSTAIN 的规则未动)。**严格证伪条件**: 若实现期发现既有形态无法
诚实承载该解释 (需改决策输入/优先级/新增决策字段) → 立即置
`DECISION_POLICY_CHANGE_REQUIRED = TRUE` 并停止 — 那意味着 M-B 不再是 minimal
consumer integration (MINIMAL_CONSUMER_INTEGRATION = FAILED)。

## 16. NEW_OBSERVATION_MEASUREMENT_REQUEST

**NONE** — 契约全部前置条件 (bbox/对齐组/band/pairwise/共现组织) 已在冻结面表达
(M-B Expressability Audit 实测); 无 observation insufficiency 证据, 不得申请。

## 17. IMPLEMENTATION_AUTHORIZATION

**NOT AUTHORIZED**。全部产出 = 契约文档 + 设计; 零 `.py` 修改。

## 18. REPLAY_AUTHORIZATION

**NOT AUTHORIZED**。Phase 3 前置 = EIC-1 经治理批准 + canary 边界生效 + 预注册参数
定值。Phase 3 只能是 Isolated Replay Design / Authorization Request (最小集: 1 FP +
2 canaries + 最高风险边界负例 + 选定 controls, 非全 corpus)。

## 19. Gate A-O 核对 (§19)

A ✓ LSP structural only · B ✓ RSC structural evidence only · C ✓ 无 LSP→different_cell
直连 (经 EIC-1) · D ✓ EIC-1 十要素齐备 · E ✓ 决策政策未动 · F ✓ 无 hidden arbitration
(冲突无 winner) · G ✓ conflict = evidence state + provenance (table_info + log) ·
H ✓ canaries = MANDATORY SAFETY BOUNDARY · I ✓ No Semantic Closure 成文 (§5) ·
J ✓ Human Validation 在 pattern 级 · K ✓ 无 M6/M7/M8 · L ✓ 零 frozen 修改 ·
M ✓ 零 GT 修改 · N ✓ 零实验 · O ✓ NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE。

## 20. GT_MODIFICATION / NEXT_STEP / STOP

GT_MODIFICATION = NONE。NEXT_STEP = **M-B Phase 3 — Isolated Replay Design /
Authorization Request** (仅设计/授权申请, 本阶段不进入)。STOP = TRUE。

## 21. Final Gate

```text
==================================================
M-B PHASE 2.2 — EVIDENCE INTERPRETATION CONTRACT REVIEW
==================================================
STATUS: PASS / DESIGN-READY (Gate A-O 全满足)
AUTHORITY_GRADIENT: L0-L6 固定; L2/L3 ↛ L4 自动; L4 ↛ L5 自动; L5→L6 唯一通路
NO_SEMANTIC_CLOSURE: 正式成文 (六类禁止跃迁)
LSP: structural only (authority 止于零语义)
RSC: structural evidence only (≠ Table Semantics)
CELL_CONTEXT_EVIDENCE: B — Semantic Interpretation (candidate 状态, 非事实非能力)
EIC-1: 十要素齐备; 状态映射全复用既有约定; 唯一语义闸门
CONFLICT: EVIDENCE_CONFLICT (observable + provenance); 无 winner/fallback 新政策
AMB-135: L2→L3→EIC-1→既有契约→KEEP (零决策改动; candidate 状态保持)
CANARIES: MANDATORY SAFETY BOUNDARY (flip = SAFETY FAILURE, 不可抵消)
HUMAN_VALIDATION: reusable pattern 级 + 负例集 (caption/code/TOC/value-column)
RED_TEAM: 10/10 拦截或双闸门
DECISION_POLICY_CHANGE_REQUIRED = FALSE (严格证伪条件已设)
NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE
IMPLEMENTATION = NOT AUTHORIZED    REPLAY = NOT AUTHORIZED
GT_MODIFICATION = NONE    FROZEN_BASELINE = INTACT
NEXT_STEP = M-B Phase 3 — Isolated Replay Design / Authorization Request
STOP = TRUE
==================================================
```
