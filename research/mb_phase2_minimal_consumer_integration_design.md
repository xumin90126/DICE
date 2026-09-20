# M-B Phase 2 — Minimal Consumer Integration Design

> 性质: **DESIGN-ONLY / READ-ONLY**。零代码、零 patch、零阈值、零实验执行、零 GT/TLD/
> 观测层修改。角色: Senior System Engineer + Evidence Quality / Slicing Architecture
> Reviewer。唯一问题 (RQ-MB2): 是否可以通过一个**最小 Consumer Integration**, 将已有
> frozen geometry-derived local structural partition 转化为 IS-11 可消费的 structural
> context, 覆盖 M-B DIRECT cases, 同时不改变既有正确行为?

---

## 1. Executive Summary

M-B Expressability Audit 已证明: (a) 盲页上冻结结构事实与已解析页**同类且齐全**;
(b) FP 对的 "same region + different partition" 证据在 Level-1 事实中完整; (c) root
cause = Consumer/Integration Gap (IS-11 的唯一证据生产者是 TLD — chunker 侧词法启发式)。

本设计的核心发现: **IS-11 的证据入口天然可插拔** — 消费者契约是
`compute_is11_observation(...) → {is_in_table, same_cell, different_cell, table_info}`,
决策函数 `experimental_c_decision` 只读这个 dict。TLD 只是该 dict 的**一个生产者**。
因此最小集成 = **一个薄 adapter (新, 隔离) 成为第二生产者 + 一个三案例共存契约**;
IS-11 决策逻辑、TLD、GT、观测层全部零改动。推荐 **Design B** (Structural Context
Adapter)。算术披露: 上一阶段审计 md 写 "DIRECT (8)" 但逐案枚举为 **9** (1 FP + 2 eff
+ 6 cs) — 本设计以逐案列表为准, 9 例全部纳入 scope (无挑选)。

## 2. Frozen Preconditions (不可重论)

M-B EXPRESSIBLE · PRIMARY_ROOT_CAUSE = CONSUMER/INTEGRATION GAP · SECONDARY =
RESEARCH-OBJECT GAP (local structural partition 可构造) · OBSERVATION_GAP = NONE for
minimal path · NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE · IMPLEMENTATION/EXPERIMENT
= NOT_AUTHORIZED · GT/层/PERCEPTION = UNCHANGED · FROZEN_BASELINE = INTACT。
IS-11 通道已证: 表格被识别时 cell-context 决策规则 **8/8 correct** — 故本设计**复用**
该消费契约, 不重新发明 cell reasoning。

## 3. Current Failure Surface

- **Known FP**: IS11-AMB-135 (eff p5) — "4"@320.35 (frozen lag=10: 'i','1'..'9' +
  污染成员 '1'@263.4) × "MBConv6, k5x5"@354.14 (frozen lag=6 算子列); pairwise
  same_y_band=True, h_gap=30.02 → 被 §9.3 基线规则 (IS-01∧IS-02) 误 MERGE。
- **M-B DIRECT = 9** (逐案修正, 双口径披露): AMB-135 (FP) + AMB-130 (eff p5 表头,
  lag 3/2 band 4) + AMB-313 (eff p8 表头, lag 0/1 band 3) + AMB-457/462/467/483/505/514
  (cs p3, lag 6-8 band 9)。OUT of scope: AMB-262 (same_y_band=False), AMB-519
  (正文对, band=1); med 8 例属 M-A/M-H/M-F。
- C 弃权总分布 (18) = eff 3 + med 8 + cs 7 — 仅上列 9 例在本设计 scope。

## 4. Research Question

**RQ-MB2**: 最小 Consumer Integration 能否把 frozen geometry-derived local structural
partition 转化为 IS-11 已有契约形状的 structural context — 覆盖 M-B DIRECT 9 例,
且 M3 collateral = 0?

## 5. Consumer Integration Boundary

```text
Observation Layer (FROZEN, 不动)
        ↓ read-only
Structural Evidence Layer (DESIGN-ONLY; 新, 隔离, 可 OFF)
  LocalStructuralPartition + StructuralContextEvidence (纯推导, 零语义)
        ↓
Consumer Adapter (POTENTIAL IMPLEMENTATION; 唯一接口点 = 证据生产者插拔 + 共存契约)
        ↓ is11_obs dict (契约形状不变)
IS-11 existing contract (experimental_c_decision 零改动) → KEEP/MERGE/ABSTAIN
```

## 6. Research Object Definition

**Geometry Fact** (frozen): bbox/x0/center/y/same_y_band/left_alignment_group/pairwise。
**Local Structural Partition** (derived, 本阶段研究对象): 一个 x0 对齐结构在其成员
y-extent 内的局部列分区 — 由 frozen left_alignment_group + 成员 bbox 并集确定性构造。
**Consumer Context**: same_structural_region ∧ different_local_partition (布尔事实 +
derivation trace)。**边界**: Partition/Context **不得**产生 decision/score/confidence/
recommendation/routing/ranking/fallback/correction/override — 只提供结构事实;
KEEP/MERGE/ABSTAIN 永远由现有 IS-11 契约决定。

## 7. Design A — Direct Evidence Injection

把 P2 singles/pairwise 原始记录直接塞给 IS-11 消费者, 由消费者自行推导分区。
- 优点: 无新对象。
- 缺点: 消费者内部逻辑增长 (推导混入决策层); provenance 在消费侧模糊; 无隔离边界
  (无法单独 OFF); 违反 "evidence 层不携带推导逻辑" 的分层; 回归面 = 整个消费者。
- 接口复杂度: 低门槛高耦合。**VERDICT: 不选** (把 complexity 推进 decision 层)。

## 8. Design B — Structural Context Adapter (推荐)

```text
Frozen store (read-only)
      ↓ 纯函数推导 (derivation procedures, 参数槽待预注册)
LocalStructuralPartition + StructuralContextEvidence
      ↓ 证据生产者插拔点 (与 TLD 并列的第二生产者)
Coexistence Contract (三案例规则, 无 arbitration)
      ↓ is11_obs 兼容记录
existing IS-11 consumer (零改动)
```
Adapter 只做: expose / package / preserve provenance / 按 frozen 语义 normalize。
不得: 语义标签、score、rank、decide、suppress、override TLD、改 GT。
- 优点: 决策层零改动; 推导可独立测试/回滚 (flag OFF = baseline); provenance 逐记录;
  与 PH-02 教训对齐 (决策对象 = 局部分区, 非整组)。
- 缺点: 新增 1 个模块 + 2 个对象 schema; 需要 1 个证据插拔点 (~20-30 行, gated)。

## 9. Design C — Parallel Evidence Channel (完整共存框架)

TLD channel + Geometry channel 并行 + source registry + 优先级/合并框架。
- 缺点: registry/优先级 = **authority creep** (§13 禁止); 新 schema 面大; 其有效内容
  (共存规则) 可以压缩为 B 内的三案例契约。
- **VERDICT: 不选** (超出最小性; 其合理内核并入 B)。

## 10. Design Comparison Matrix

| 维度 | A 注入 | **B 薄 Adapter** | C 并行框架 |
|------|--------|------------------|-----------|
| 新增对象 | 0 | 2 (Partition + ContextEvidence) | 2+registry |
| 新增接口 | 0 (逻辑进消费者) | **1 (生产者插拔点)** | 2 (插拔+registry) |
| 消费者逻辑改动 | 大 (推导入决策层) | **0 (决策函数不动)** | 0 |
| 语义/authority 泄漏风险 | 中 | **无** | 中 (优先级=authority) |
| 隔离/回滚 | 差 | **trivial (flag OFF)** | 中 |
| provenance | 模糊 | **逐记录** | 逐记录 |
| 最小性 | 假最小 | **最小** | 过重 |

## 11. Recommended Minimal Design

**Design B**, 含 C 的共存契约作为其准入规则。三案例规则 (§12):
- **Case 1** (TLD 有 + geometry 有, **一致**): cell-context 按该一致事实准入;
- **Case 1c** (两者**冲突**): 不做 winner — cell-context 字段置 null (不准入), 冲突
  事件写入 provenance log 供审计; 消费者落回 §9.3 基线 (INSUFFICIENT_EVIDENCE 路径)。
  这是**共存契约**, 不是仲裁 (无 score/优先级/可信度);
- **Case 2** (TLD 无 + geometry 有 — M-B target): geometry context 单源准入;
- 反向 (TLD 有 + geometry 无): TLD 单源准入 — 现状不变。
任一源单独说话时按该源准入; 冲突时诚实弃权。**零 authority**。

## 12. LocalStructuralPartition Schema (最小, 逐字段问责)

```json
{
  "partition_id": "{doc}|p{page}|lsp|{seq}",   // 纯函数 of member_atom_ids; 可重建
  "document_id": "...", "page_reference": N,
  "member_atom_ids": ["..."],                  // frozen P2 atom ids (verbatim)
  "bbox_union": [x0,y0,x1,y1],                 // derived: 成员 bbox 逐值并集
  "axis": "x0",                                // frozen 对齐关系名 (left_alignment_group)
  "source_surface": "atomic_observation_layer.v1/p2_singles",
  "source_shas": {"p1": "...", "p2": "..."},   // frozen 代码 sha (registry)
  "params_hash": "...",                        // frozen config snapshot hash
  "derivation_trace": {"relation": "left_alignment_group", "band_ref": "..."}
}
```
| 字段 | 来自 | frozen/derived | source-backed | deterministic | 语义? | 决策? | 污染风险 |
|------|------|----------------|---------------|---------------|-------|-------|----------|
| partition_id | 成员 id 集合 | derived(纯函数) | yes | yes | no | no | 无 |
| member_atom_ids | P2 store | frozen | yes | yes | no | no | 无 |
| bbox_union | 成员 bbox | derived(verbatim 并集) | yes | yes | no | no | 无 |
| axis/relation | P2 关系名 | frozen 语义 | yes | yes | no | no | 无 |
| source_shas/params_hash | layer_registry | frozen | yes | yes | no | no | 无 |
| derivation_trace | 本 adapter | derived | yes | yes | no | no | 无 |

**Forbidden fields (缺席即合规)**: is_table / is_row_number_column / is_cell /
merge_candidate / keep_candidate / confidence / score / priority / recommendation。
`StructuralContextEvidence` (对偶对象) = {case_ref, atom_a/atom_b → partition_id|null,
same_structural_region: bool|null, different_local_partition: bool|null, region_ref,
derivation_trace, source_shas, params_hash, source: "geometry_structural_context_adapter.v0"}
— 同样零语义零决策。**若 integration 需要语义字段才能完成 → 停止并报告
Research-Object/Consumer Contract Gap** (当前不需要 → 不触发)。

## 13. Provenance Model

每条 context 记录携带: source (adapter id+version) · source artifact (store 的
source_shas/params_hash — 冻结 registry 可验) · input identity (member_atom_ids +
case_ref) · derivation trace (relation/band_ref/region_ref + 推导过程哈希)。
determinism: adapter 为冻结 store 上的纯函数; 同输入 → byte-identical 输出
(与 verify_determinism 同标准); 冲突/弃权事件亦入 log (M6)。

## 14. TLD / Geometry Evidence Coexistence

TLD: 不修改、不退役、继续作为第一生产者 (其 13/45 覆盖 + 8/8 正确是既有事实)。
Geometry adapter: 第二生产者。准入契约 = §11 三案例规则。**禁止**: TLD wins /
Geometry wins / score wins / override。Consumer 按已有契约消费准入后的 cell-context;
两源冲突 → 无 cell-context (诚实弃权) + 审计日志。此契约下 TLD 权威既不扩大也不缩小。

## 15. IS11-AMB-135 Walkthrough (静态, 逐标注 evidence/decision 责任)

```text
"4"@320.35
   ↓ [EVIDENCE: 冻结 left_alignment_group=10 成员, bbox 并集, provenance]
LocalStructuralPartition LSP-a (行号列分区, x0≈320.4)
"MBConv6, k5x5"@354.14
   ↓ [EVIDENCE: 冻结 lag=6 成员 @354.14]
LocalStructuralPartition LSP-b (算子列分区)
pair ("4","MBConv6, k5x5")
   ↓ [EVIDENCE: 同一 co-structured region (p5 表区 12 列簇, y 重叠) — 推导]
   ↓ [EVIDENCE: LSP-a ≠ LSP-b → different_local_partition=True; same_structural_region=True]
StructuralContextEvidence {same_region=T, different_partition=T, trace, provenance}
   ↓ [ADMISSION: TLD 无输出 (p5 盲) + geometry 单源 → 准入 (Case 2)]
is11_obs 兼容记录 {is_in_table=T, same_cell=F, different_cell=T}
   ↓ [DECISION: experimental_c_decision — 零改动 — different_cell → KEEP_SEPARATE]
基线 MERGE (IS-01∧IS-02) 被既有契约覆盖 → 不再错误合并
```
每一步责任明确: ①③④⑤ = evidence; ⑥ = admission (契约规则); ⑦ = decision (现有
IS-11)。**若 LocalStructuralPartition 自身输出 KEEP/MERGE → 设计越界, 立即废弃** —
本设计中它不输出任何决策 (schema 无此字段)。

## 16. M-B DIRECT 9-case Scope (修正披露)

| # | case | doc/page | 上下文事实 |
|---|------|---------------------|------------|
| 1 | **AMB-135 (FP)** | eff p5 | lag 10 × lag 6, same_band, h=30.02 |
| 2 | AMB-130 | eff p5 | 表头对, lag 3/2, band 4 |
| 3 | AMB-313 | eff p8 | 表头对, lag 0/1, band 3 (列成员弱 → 上下文可能不足, 诚实预期) |
| 4-9 | AMB-457/462/467/483/505/514 | cs p3 | lag 6-8, band 9 |
OUT: AMB-262 (非同带) / AMB-519 (正文)。审计 md 的 "8" 为算术笔误, 逐案列表 = 9;
scope = 全部 9 例 (不因便利删减)。

## 17. Negative Boundary Analysis (§16 — 只判可观察性与作用面, 不设排除谓词)

| Boundary | 可能误触发原因 | 现有 evidence 能否区分 | 风险 |
|----------|----------------|------------------------|------|
| bibliography numbers | 对齐数字堆 | 可观察: 单列+长散文右邻, 区域内无第二分区 → same_region=F | 低 |
| TOC | 节号/标题/页码 3 x-zone 共结构 | **最难**: 共结构存在 → same_region 可为 T; 但点列 x-center 不稳+标题宽度变异可观察; 正式排除=实验侧预注册 | **中-高 (诚实标注)** |
| numbered list | 垂直数字堆 | 可观察: 无平行列共结构 | 低 |
| code line numbers | 连续整数列 | 可观察: sib=0, 无第二分区 | 低 |
| figure axis ticks | 重复数字几何 | 可观察: 单列堆 sib 0-1 | 低 |
| ordinary numeric values | 对齐值列 | Level-2 **同构不区分** (设计使然); 同分区对→same_partition→无 KEEP 支持; 误触发=给 KEEP 证据于 GT=KEEP 对 → 无害面 | 低 |
| prose (双栏) | 同带+跨栏分区 | margin 组 lag 24-30; same_region 可为 T+partition 不同 → 会给 KEEP 证据; in-frame GT=KEEP (005/519) 无害 | 中 |
| **caption (M-A 冲突!)** | label+continuation 同带不同 x | 会得 different_partition → KEEP 证据 → **可能翻转 2 例 GT=MERGE 弃权** | **高 — 必须作 canary** |

**关键设计发现 (诚实披露)**: 最小几何路线与 M-A (caption MERGE) 存在**已知碰撞面** —
med p20/p24 的 2 例 GT=MERGE 弃权若收到 different_partition 上下文会翻成 KEEP (错)。
处置: 列为 **M3 canary controls** (预测变化必须=0), 出现翻转 → PARTIAL/REJECT。
不在本设计添加排除谓词 (那会是新语义规则)。

## 18. Isolation / Rollback Boundary (§17)

- **OFF** (默认): adapter 不调用 → is11_obs 由 TLD 单源产生 → 与现状 byte-identical;
- **ON**: adapter 作为第二生产者接入插拔点; 作用于整个 replay (无 per-case 特判 —
  禁止 case-conditional 逻辑);
- baseline path 零改动 (决策函数/协议/TLD 不动); rollback = 关 flag (trivial);
  新模块物理隔离 (tmp/ 下独立文件, 未来如授权 → perception/sandbox/evidence 独立模块)。

## 19. Minimal Replay Experiment Design (§18 — 只设计, 不运行)

- **Positive/target (9)**: AMB-135 + 130,313,457,462,467,483,505,514;
- **Existing correct controls (8)**: 005,024,034,074,346,350,522,530 — 预测变化必须=0;
- **Canary controls (2)**: AMB-414/422 (caption, GT=MERGE 弃权) — 不得翻成 KEEP;
- **Negative boundary (in-frame)**: AMB-519 (正文), AMB-262 (不同带) — 不得产生错误
  决策变化; **out-of-frame 描述性观察** (无 GT, 只记录 context 是否产生): LLaMA p19/p22
  code lines, 2309 文献编号, 2212 p15 TOC;
- **全局**: 45-case 全量重跑 (OFF vs ON 逐案 diff), 附 determinism 双跑。
基建: 复用 tmp/ 既有 GT 重放 harness (run_ph02_replay 同框架), 新增 adapter 模块 +
插拔点。

## 20. Metrics (§19)

- **M1 Known FP suppression**: AMB-135: incorrect MERGE → not-incorrect-MERGE;
- **M2 M-B Direct recovery**: 9 例中 (a) 获得 admissible structural context 的数量 与
  (b) 最终 prediction 变化数量 — **分开统计** (evidence recovery ≠ decision change);
- **M3 Collateral**: 45 例中既有正确预测的变化数 (含 8 controls + 2 caption canaries)
  — 要求 **0**;
- **M4 Boundary leakage**: 负例上不正确 context 暴露数 — 要求 0;
- **M5 Determinism**: 同输入双跑 context 记录 byte-identical;
- **M6 Provenance completeness**: 每条 context: source/artifact/input/trace 四元组可追溯。

## 21. Success / Partial / Reject Criteria (§20 — 预先定义)

- **PASS**: M1 pass ∧ M3=0 ∧ M4=0 ∧ M5 pass ∧ M6 pass ∧ M-B DIRECT 出现可解释的
  evidence recovery (M2a>0 且变化方向与 GT 一致);
- **PARTIAL**: FP suppressed 但部分 DIRECT 无法恢复; 或 context recovered 但 downstream
  decision 不变 — 必须区分 **Evidence recovery failure** vs **Consumer decision failure**
  (后者指向契约缺口, 不是 evidence 失败);
- **REJECT**: 任一 correct case 翻转 / boundary leakage / semantic leakage /
  authority leakage / non-determinism / provenance failure。

## 22. Falsification Conditions (§21 — 假设, 不写死结果)

- **H1** (hypothesis): FP 对产出 same_region=T ∧ different_partition=T → 准入 → 既有
  契约给 KEEP。**Falsified if**: 分区推导无法在 p5 复现审计事实 / context 未准入。
- **H2**: ≥6/9 DIRECT 获得 admissible context。**Falsified if**: <6 (表头弱列成员案例
  预期不足属诚实预期, 但需逐例归因)。
- **H3**: controls 8/8 预测不变。**Falsified if**: 任一变化 (M3>0 → REJECT)。
- **H4**: caption canaries 2/2 不翻。**Falsified if**: 任一翻 KEEP (M3/M4 失败)。
- **H5**: 双跑 byte-identical。**Falsified if**: 任何差异。
- 预期观察 (非承诺): M1 pass / M2a ∈ [6,9] / M3=0 / M4=0。**禁止**提前写 "FP→0" 为
  结论 — 它只是 H1 的预期观察。

## 23. Risks (§12/§15/§17 汇总)

1. **M-A 碰撞** (最高): different_partition 上下文可能伤害 caption MERGE → canary 把守;
2. TOC 类共结构误给 context (in-frame 无此案例 → M4 描述性观察把守);
3. 表头弱列成员 → context 不足 (诚实预期, 逐例归因);
4. 共存契约本身成为隐性 policy (冲突→弃权是契约, 需在报告中可审计);
5. derived structure 被 downstream 误当语义 → schema 无语义字段 + forbidden 清单把守;
6. 参数槽 (成组/成带/成区容差) 若在实验前被临时定值 → 违反预注册纪律 (设计阶段不定值)。

## 24. Minimum Implementation Delta (§22/§24 — 只描述, 不执行)

**§22 直答**: 不修改 IS-11 **决策逻辑**能否接入? — **能**: 消费契约
(experimental_c_decision) 零改动, is11_obs dict 形状不变; 但 harness 的观察者包装
(compute_is11_observation) 目前硬编码 TLD 单源 — 零行改动不可能, **缺失接口 = 证据
生产者插拔点** (missing interface, 精确定位)。最小 delta:

| 层 | 动作 | 规模 | 状态 |
|----|------|------|------|
| Observation Layer | 零改动 (adapter 只读 store) | 0 | FROZEN |
| Structural Evidence Layer | 新模块: build_local_structural_partitions + emit_structural_context (纯函数) | ~100-150 行, tmp/ 独立文件 | DESIGN-ONLY |
| Consumer Adapter | compute_is11_observation 增加第二生产者调用 + 三案例准入 (flag 默认 OFF) | ~20-30 行, 1 个接口点 | POTENTIAL IMPLEMENTATION (需授权) |
| IS-11 契约 | experimental_c_decision / §9.3 协议 | 0 行 | UNCHANGED |
| TLD / GT / 观测层 schema | 零改动 | 0 | UNCHANGED |

**最小性证明**: 新对象 2 (均可由冻结事实纯函数重建) · 新接口 1 (插拔点) · 新逻辑 =
推导纯函数 + 三案例契约 (无 score/优先级) · 新语义假设 0 · 新阈值 0 (参数槽待预注册)
· 新 authority 0 (冲突→弃权) · 新 regression 面 = flag-gated 单通道, canary+controls
把守。任何更重方案 (detector/classifier/table schema/scoring) 均非必需 → 本设计即
最小。**若未来发现必须引入语义字段才能覆盖 DIRECT cases → 停止, 报告
Consumer Contract Gap, 不偷偷加**。

## 25. Governance Gate (§27)

```text
==================================================
M-B PHASE 2 — MINIMAL CONSUMER INTEGRATION DESIGN
==================================================

STATUS:
DESIGN-ONLY

ROOT_CAUSE:
CONSUMER / INTEGRATION GAP

SECONDARY:
RESEARCH-OBJECT GAP
→ LOCAL STRUCTURAL PARTITION CONSTRUCTIBLE

OBSERVATION_GAP:
NONE FOR MINIMAL PATH

M-B DIRECT:
9 (逐案修正披露: 1 FP + 2 eff + 6 cs; 审计 md "8" 为算术笔误)

KNOWN FP:
IS11-AMB-135

RECOMMENDED DESIGN:
Design B — Structural Context Adapter (第二生产者 + 三案例共存契约;
决策函数零改动)

RESEARCH_OBJECT:
LocalStructuralPartition (derived, 纯函数, 零语义, 零决策;
禁止字段清单缺席即合规)

MINIMUM_INTEGRATION:
1 插拔点 (~20-30 行, flag OFF 默认) + 1 隔离适配模块 (~100-150 行, tmp/)
+ 0 决策逻辑改动

TLD_RELATIONSHIP:
并行共存, 无仲裁; 冲突→cell-context 弃权+审计日志; TLD 权威不扩大不缩小

PROVENANCE:
source / source artifact (frozen shas+params_hash) / input identity /
derivation trace 四元组逐记录; determinism 双跑 byte-identical

ISOLATION:
OFF=baseline byte-identical; ON=全 replay 统一开启 (无 per-case 特判);
rollback=关 flag

EXPECTED_SLICING_IMPACT:
假设 (非承诺): H1 FP 对获得准入 context → 既有契约 KEEP;
H2 ≥6/9 DIRECT evidence recovery; H3 controls 8/8 不变;
H4 caption canaries 不翻; M3=0

PRIMARY_FALSIFICATION:
FP 对分区推导不可复现 / 任一 correct case 翻转 / caption canary 翻转 /
M4 leakage / non-determinism / provenance 缺失

IMPLEMENTATION:
NOT AUTHORIZED

EXPERIMENT:
NOT AUTHORIZED

GT:
UNCHANGED

ATOMIC_OBSERVATION:
UNCHANGED

PERCEPTION:
UNCHANGED

FROZEN_BASELINE:
INTACT

PRODUCTION:
FALSE

STOP:
TRUE
==================================================
```

## 26. Final Decision

推荐 **Design B** 为 MINIMAL VIABLE INTEGRATION DESIGN: 既有冻结证据 → 局部结构分区
(纯函数推导, 零语义) → 薄 adapter 以契约形状准入 (与 TLD 共存, 无仲裁) → 现有 IS-11
决策契约零改动。它直接作用于 IS11-AMB-135 的已证事实链, 覆盖 9 个 M-B DIRECT 案例,
隔离边界 trivial, 且把唯一的已知碰撞 (caption canary) 显式纳入证伪条件而非掩盖。
本阶段到此为止; 实验执行需下一阶段独立授权。
