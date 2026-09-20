# L5.2 Evidence Compression Feasibility Review

> DESIGN-ONLY / READ-ONLY。不实施, 不实验, 不修改任何 frozen artifact / schema / code。
> RQ-L5.2: DICE 是否能在不引入新语义权威、不发生 Semantic Closure 的前提下, 由 System 自动
> 完成 Evidence Aggregation / Structural Comparison / Evidence Compression / Coverage Construction /
> Conflict+UNKNOWN Preservation, 使 Human 仅验证一个最小 Semantic Claim?

标注: [O] observed · [I] inferred · [H] hypothesis · [D] design · [EV] experimentally verified

---

## 0. 前置原则 (L5.1 固定, 本阶段继承)

> Human should validate, not reconstruct.
> DICE Pattern should compress evidence for humans, not transfer abstraction work to humans.

L5.2 核心追问: **不是"架构逻辑是否合理", 而是"现有 DICE 能力是否真的足以支撑"。** 不因 L5.1 认可 Model 2 就默认 L5.2 成立。

---

## 1. System Work vs Human Work Allocation Matrix

| Task | System | Human | Current DICE Support | Authority Risk | Status |
|---|---|---|---|---|---|
| aggregation | YES | — | MISSING (无跨实例聚合; StructuralRelation 实例级; region_engine 页内聚类非跨实例) | LOW (结构聚合无语义) | **MISSING** |
| structural comparison | YES | — | PARTIAL (pairwise geometry frozen P2; 但无跨实例结构比较; 无 commonality) | LOW | **PARTIAL** |
| commonality discovery | YES | — | MISSING (grep 0; 无 common_structure/repeated_pattern) | LOW-MED (commonality≠语义, 但若系统自己断言"同一pattern"越界) | **MISSING** |
| prototype construction | YES | — | MISSING | MED (prototype 选择=system bias 入口) | **MISSING** |
| boundary discovery | YES | — | MISSING (localization 有空间边界, 但无 pattern boundary) | MED | **MISSING** |
| negative discovery | YES | — | MISSING (负例 cataloged 在文档, 非 system 自动发现) | MED (negative 启发式→semantic closure 风险) | **MISSING** |
| UNKNOWN discovery | YES | — | PARTIAL (IS-11 INSUFFICIENT_EVIDENCE 实例级; P6 UNKNOWN_REGION; 但无跨实例 UNKNOWN 聚合) | LOW (UNKNOWN 是拒答, 无语义越权) | **PARTIAL** |
| evidence summarization | YES | — | MISSING (grep 0; 无 evidence_summary) | LOW-MED (摘要措辞可能隐含语义) | **MISSING** |
| evidence compression | YES | — | MISSING | MED (压缩=选择=潜在 silent suppression) | **MISSING** |
| contradiction detection | YES | — | PARTIAL (EIC-1 coexistence conflict=临时实验产物; 架构内无 conflict 对象) | LOW (conflict 保留≠仲裁) | **PARTIAL** |
| provenance preservation | YES | — | EXISTS (ValidationRecord.provenance + StructuralRelation.provenance + layer_registry frozen sha + audit_chain) | LOW | **EXISTS** |
| coverage construction | YES | — | MISSING | MED (覆盖率选择=system bias) | **MISSING** |
| semantic interpretation | — | YES | — (Human authority; System 不得自动) | — | HUMAN |
| semantic claim validation | — | YES | MISSING (无 Semantic Claim 对象/流程; 当前=instance verdict) | — | HUMAN (对象缺失) |
| semantic authorization | — | YES | EXISTS (FROZEN_CAPABILITY_TABLE 人控; validation ACCEPT) | — | HUMAN |

**总结 [O]**: 15 项中 — EXISTS=2 (provenance, human authorization), PARTIAL=3 (structural comparison/UNKNOWN/conflict 实例级), **MISSING=8** (aggregation/commonality/prototype/boundary/negative/summarization/compression/coverage), HUMAN-only=3。**Workflow C 的 System 侧 8/12 核心能力 MISSING。**

---

## 2. 当前 DICE 能力只读核查 (§5)

### 2.1 已有 (EXISTS) [O]

| 能力 | 位置 | 性质 | 局限 |
|---|---|---|---|
| pairwise geometry | frozen P2 (geometry_engine) | 实例对几何事实 | 非跨实例聚合 |
| StructuralRelation (8 types) | structure_relation.py | 实例对结构关系 (LEFT_ALIGNED_WITH / ADJACENT_TO / PRECEDES / SHARES_REGION / CONTINUES_FROM / REPEATS_ACROSS_PAGES / VERTICAL_SEPARATION / STYLE_CONTRAST) | **per doc/page/src/tgt**, 无跨实例 grouping |
| region clustering | region_engine.py | 页内 span 聚类 (density/sparse) | 页内, 非跨实例 |
| provenance | ValidationRecord.provenance + audit_chain + layer_registry sha | 实例级追溯 | 无 pattern 级追溯 |
| UNKNOWN | IS-11 INSUFFICIENT_EVIDENCE + P6 UNKNOWN_REGION + CONFIDENCE_UNKNOWN | 实例级拒答 | 无跨实例 UNKNOWN 聚合 |
| conflict (临时) | mb_eic1_adapter compose (EVIDENCE_CONFLICT, no winner) | 实验产物, **非架构** | 未进架构 |
| validation memory | validation_records.json (33 records: 1 ACCEPT/32 REJECT) | 实例 verdict 历史 | 无 pattern 抽象 |

### 2.2 关键发现: 名字类似 ≠ 能力已存在 [O]

- `REPEATS_ACROSS_PAGES` 听似"pattern", 实际 = **实例对关系** (header/footer 是否跨页重复), 非 reusable pattern 抽象;
- `region clustering` = 页内 span 分组, 非跨实例 evidence aggregation;
- `audit_chain` = 单 evidence 的反向追溯, 非多实例压缩后的合并追溯;
- `UNKNOWN_REGION` = 单 region 无法判定, 非跨实例 UNKNOWN discovery;
- **不存在**: aggregation / commonality / common_structure / repeated_pattern / evidence_summary / compress / coverage / prototype / boundary_discovery / negative_discovery (grep 全 0) [O]。

### 2.3 现有 validation 的实际形态 [O]

33 条 validation_records: 全实例级 (validation_id/task_id/observation_id), verdict=ACCEPT/REJECT/NEED_REVIEW, 无 pattern_id / negative_set / boundary / scope 字段。= Workflow A 现状。

---

## 3. Evidence Compression 定义 (§6)

**不是**: "15 实例 → 一句话摘要" (过度压缩 = silent suppression)。

**是**: High Compression + High Fidelity。

### Compression Gain (降低)
- Human evidence exposure (默认阅读 item 数);
- Human interaction (clicks/expands);
- Cross-instance comparison (由 System 做)。

### Compression Fidelity (必须保留)
- positive evidence (支持 claim 的结构事实);
- contradiction (冲突, 不得隐藏);
- UNKNOWN (证据不足, 不得强制归并);
- boundary evidence (边界条件);
- negative evidence 可追溯性 (负例不得删除);
- provenance (全部压缩后证据可回溯原始 source)。

**研究目标 [D]**: 非 Maximum Compression, 而是 **High Compression + High Fidelity**。

---

## 4. Compression Fidelity 设计指标 (§7, 仅研究, 非生产)

| 指标 | 定义 | 风险 |
|---|---|---|
| positive_preserved | 压缩后 positive 结构事实仍可恢复 | 丢失→claim 无支撑 |
| negative_preserved | 负例仍可追溯 | 丢失→overgeneralization |
| boundary_preserved | 边界条件仍可审查 | 丢失→scope 膨胀 |
| UNKNOWN_preserved | 证据不足案例仍显式 | 丢失→false closure |
| conflict_preserved | 冲突仍 observable | 丢失→silent suppression |
| provenance_preserved | 压缩→原始 source 可回溯 | 丢失→不可审计 |
| semantic_claim_traceable | claim → 支撑证据链可展开 | 丢失→Human 无法验证 |

### 关键问题回答 [D]
1. **什么叫"关键证据"?** = 支撑/反驳/限定 claim 的证据 (positive/negative/boundary/UNKNOWN/conflict); **非**全部实例 (实例可压缩, 关键证据不可);
2. **谁定义?** = System 提议 (基于 structural role), Human 确认 (boundary adequacy); System 不得单方面定义"关键"并据此删除其他;
3. **是否允许 System 自己决定?** = System 可提议 (candidate), 不可最终决定 (无 authority); Human 可推翻;
4. **semantic authority 风险?** = 若 System 用 semantic heuristic 选关键证据 → Semantic Closure; 缓解: System 只用 structural role (positive/negative/boundary 是结构判定, 非语义判定);
5. **Human 是否可展开原始证据?** = YES (Level 4 Progressive Disclosure, 强制可访问);
6. **是否存在 silent suppression?** = 残余风险 [I]; 缓解: summary 必须含 conflict/UNKNOWN count (诚实), provenance 全保留, 可独立重算。

---

## 5. Progressive Disclosure 安全审查 (§8)

| Level | 内容 | 默认展示 | 风险 |
|---|---|---|---|
| 0 | Minimal Semantic Claim + summary (consistent/conflict/UNKNOWN count) | YES | summary 不诚实→误导 |
| 1 | Evidence Summary (instance count/consistency/coverage) | on-demand | — |
| 2 | Representative Evidence (prototype + boundary-edge) | on-demand | prototype bias (R2) |
| 3 | Boundary/Negative/UNKNOWN | on-demand | 若 Human 不展开→依赖 summary |
| 4 | Full Provenance | on-demand | — |

### 优点 [D]
- 默认 exposure 低 (Level 0);
- interaction 低;
- cross-instance comparison 低 (System 已做)。

### 风险 [I]
- **silent suppression**: System 隐藏 conflict/negative → Human 误批准;
- **system-selected evidence bias**: prototype 不代表真正 boundary;
- **important negative hidden**: 负例未在 summary 显式 count;
- **conflict hidden**: conflict count 必须显式, 不得省略;
- **Human over-trust summary**: 长期后默认相信 (automation bias, R6)。

### 核心原则 [D]
> **Evidence visibility ≠ Evidence authority。不默认展示 ≠ 可以删除。**

被压缩/隐藏的证据必须: expand + trace + audit。Level 4 必须 always reachable。

**安全判定 [I]**: Progressive Disclosure **设计上**安全 IF summary 诚实 + provenance 全保留 + Level 4 可访问 + 可独立重算。残余风险 (silent suppression / automation bias) **未实验验证** [H]。

---

## 6. Semantic Authority Boundary (§9)

### System 可以 (authority = structural, 非语义) [D]
- 发现结构 (LSP/RSC);
- 聚合证据 (group by structural signature);
- 比较结构 (pairwise/density);
- 压缩证据 (summarize counts);
- 指出冲突 (EVIDENCE_CONFLICT, no winner);
- 指出 UNKNOWN (INSUFFICIENT_EVIDENCE);
- 构建 Candidate (Semantic Claim **Candidate**, 非 conclusion)。

### System 不可以 (未经 Human) [D]
- 完成语义解释;
- 自动关闭语义边界;
- 自动判定"表格"/"行号列"/"能力";
- 自动升级 Capability。

### 硬约束 [D]
> **Compression Layer authority = 0。** 它只改变证据组织方式, 不改变证据语义 authority。

```
Evidence → Compression → Semantic Claim CANDIDATE (非 Conclusion)
                                   ↓
                            Human Validation
                                   ↓
                          Validated Semantic Claim
```

---

## 7. Design Simulation — System 如何压缩 (§10-11, 用 21 已有案例)

### 模拟流程 (21 案例)

```
Raw Instances (21: 135/130/457/467/483/505/514/313/462/414/422/519/262/005/024/034/074/346/350/522/530)
↓
Step 1: Aggregation (group by structural signature)
  - System 读每案的 LSP/RSC/EIC-1 结构特征 (same_y_band / co_density / region_forms / partition / localization)
  - 聚类: {co-structure≥3, same_y_band, different_partition, localization≤150} → Group G1 (16 cases: 135+6direct+262+8controls)
  - {caption band, density=0} → Group G2 (414/422)
  - {lag=0/1, partition unresolvable} → Group G3 (313/462)
  - {prose/value-column margin} → Group G4 (519/034/074)
↓
Step 2: Structural Comparison (within group)
  - G1: 16 案共享 co-structure signature → commonality candidate
  - G2: 2 案 density=0 → safety signature
  - G3: 2 案 unresolvable → UNKNOWN signature
  - G4: margin/prose → negative signature
↓
Step 3: Common Structure + Contradictions + UNKNOWN
  - common: G1 的 co-structure signature
  - contradiction: 0 (evidence_conflict=0 in replay [O])
  - UNKNOWN: G3 (2 cases)
↓
Step 4: Compressed Evidence
  - G1: "16 instances share co-structure signature (density≥3, same_y_band, different_partition); 0 conflicts; 0 UNKNOWN in group"
  - G2: "2 instances: caption band, density=0 (safety)"
  - G3: "2 instances: partition unresolvable (UNKNOWN)"
  - G4: "3 instances: margin/prose (negative)"
↓
Step 5: Semantic Claim Candidate
  - SC1: "16 structurally consistent observations support different-cell interpretation (candidate)"
  - SC2: "2 caption-band observations do not support cell interpretation (safety)"
  - SC3: "2 observations have insufficient evidence (UNKNOWN)"
  - SC4: "3 margin/prose observations are negative"
↓
Human: SUPPORTED / UNSUPPORTED / UNKNOWN per claim
```

### 每步能力核查 [O-based]

| Step | 当前能否 | 缺口 |
|---|---|---|
| 1 Aggregation | **NO** | 无跨实例 grouping; StructuralRelation 实例对; region_engine 页内; 需新 aggregation 层 |
| 2 Structural Comparison | PARTIAL | pairwise geometry frozen (实例对); 无跨实例 signature 比较; 需 structural signature 抽象 |
| 3 Commonality + Contradiction + UNKNOWN | PARTIAL | UNKNOWN 实例级 EXISTS; conflict 临时产物; commonality MISSING |
| 4 Compression | **NO** | 无 summarization/compression 对象 |
| 5 Semantic Claim Candidate | **NO** | 无 Semantic Claim 对象; EIC-1 是 Cell Context Evidence (interpretation), 非 Semantic Claim Candidate (validation unit) |

### 缺口分类 [I]
- Step 1-2: **Pattern abstraction gap** (跨实例 grouping + structural signature) — 非 observation gap (frozen 观测够), 非 consumer gap (M-B 已证 consumer 可复用); 是**新抽象层**;
- Step 3: UNKNOWN/conflict 部分有 (实例级), 需**跨实例聚合**;
- Step 4-5: **完全 MISSING** — 压缩对象 + Semantic Claim 对象均不存在;
- **不引入语义权威**: Step 1-4 全 structural (group/signature/count), Step 5 是 **Candidate** (非 conclusion) → authority=0 [D];
- **不需要新 observation**: 现有 frozen P1/P2 + Atomic Observation 足以产生 structural signature [EV, M-B audit]; gap 在抽象层, 非测量。

---

## 8. System Abstraction Capability Test (§12)

| 能力 | 当前 | 判定 |
|---|---|---|
| Commonality Discovery | grep 0; StructuralRelation 实例对非共性 | **MISSING** |
| Prototype Construction | 无 | **MISSING** |
| Boundary Discovery | localization 有空间边界; 无 pattern boundary | **MISSING** |
| Negative Discovery | 负例 cataloged 在文档 (人工); 非 system 自动 | **MISSING** |
| UNKNOWN Discovery | 实例级 EXISTS; 跨实例聚合 MISSING | **PARTIAL** |
| Conflict Detection | 临时 EIC-1 coexistence; 架构无 conflict 对象 | **PARTIAL** |
| Evidence Compression | grep 0 | **MISSING** |
| Coverage Construction | 无 | **MISSING** |
| Provenance Preservation | 实例级 EXISTS; 压缩后合并追溯 MISSING | **PARTIAL** |

**9 项: MISSING=6, PARTIAL=3, SUPPORTED=0。**

### Workflow C 是否仍可成立? [I]
**不能立即成立**。6/9 核心能力 MISSING → Workflow C 目前是 **design hypothesis**, 非可实现。System 侧能力缺失 = 把 abstraction work 转嫁给 Human 的风险 (若强行用 Human 补) = **HUMAN_ABSTRACTION_BURDEN**。需先建 System abstraction 层 (aggregation + signature + compression + claim candidate) 才能成立。

---

## 9. Burden Transfer Red-Team (§13)

### R1: System "15 一致" 但隐藏 2 反例 → Human 误批准?
**风险 = PRESENT [I]**。若 summary 不显式 conflict/negative count → silent suppression → Human 误批准。
**缓解 [D]**: summary 强制含 conflict_count / negative_count / UNKNOWN_count (诚实); provenance 全保留; Level 3 可展开 negative。**残余风险未验证** [H]。

### R2: System prototype 不代表真正 boundary → Human 被误导?
**风险 = PRESENT [I]**。prototype 选择 = system bias 入口。
**缓解 [D]**: prototype 必须配 boundary-edge case (System 选最接近边界的实例, 非最典型); Human 可展开 Level 2 审查; boundary adequacy = Human on-demand confirmation。**残余风险**: 若 System 误选 → Human 不展开则不发现 [H]。

### R3: System 压缩但 Human 不知"为什么这 15 个/还有哪些/为何同组" → System Over-trust?
**风险 = PRESENT [I]**。
**缓解 [D]**: summary 必须含 grouping rationale (structural signature, 非语义); coverage count (N included / M excluded / K conflict); Level 1 展示 grouping criteria; provenance 可展开。**残余**: Human 若不问则不知 [H]。

### R4: System negative discovery 用 semantic heuristic → Semantic Closure?
**风险 = PRESENT [I, critical]**。若 System 用"这是 caption"→semantic 判定选 negative = Semantic Closure。
**缓解 [D]**: negative discovery 只用 **structural signature** (density=0, margin y_ext, single-column sib=0), 非语义标签; "caption"/"value-column" 是 Human 验证后的 label, 非 System 判定。**残余**: structural signature 本身可能隐含语义假设 [H] → 需 audit。

### R5: Semantic Claim Candidate vs Conclusion 边界?
**边界 [D]**: Candidate = `interpretation_status="candidate"` (EIC-1 已有此字段 [O]); Conclusion = 经 Human ACCEPT。System 只产 Candidate, 不产 Conclusion。**风险**: 若 compression 隐含 conclusion (措辞/选择) → 越界。**缓解**: Candidate 显式标 status; Human ACCEPT 前无 authority。

### R6: 1000 次 summary 后 Human 默认相信 → automation bias?
**风险 = PRESENT [I, long-term]**。Progressive Disclosure 的 default-low 会被习惯化 → Human 不展开 → over-trust。
**缓解 [D]**: (1) 定期 audit (抽样强制展开); (2) summary 不诚实时 system 责任 (可检测: conflict_count 与 Level 3 实际负例数不符 → alarm); (3) 关键 claim (高影响) 强制展开 boundary; **残余**: 无法完全消除习惯化 [H] → 需 human subject 实验。

### Red-Team 总结 [I]
6 个反例全部 **风险 PRESENT**; 全部有**设计缓解**; 全部有**残余风险未验证**。Workflow C 的 burden reduction **设计上可行但未经实证**, 且依赖 6 个 MISSING 能力的实现 + 4 类缓解机制的有效性。

---

## 10. Pattern 重新定义 (§14)

| 候选定义 | 评估 | 判定 |
|---|---|---|
| Human Validation Object | L5.1 已否定 (Model 1 = burden transfer) | REJECT |
| Evidence Organization Layer | 合理但不够 (无 compression) | 不充分 |
| Evidence Compression + Reuse Layer | 最准确: 组织 + 压缩 + 复用, 透明于 Human | **KEEP** |

**Pattern = Evidence Compression + Reuse Layer** [D]。它组织证据、压缩证据、使 Semantic Claim 可复用; 对 Human 透明 (非验证对象); 无 runtime authority。但这定义**依赖未实现的 System 能力** (6/9 MISSING) → Pattern 概念 KEEP, 但当前**不可实现**, 需 System abstraction 层。

---

## 11. Semantic Claim 反证 (§15)

| 维度 | 评估 | 判定 |
|---|---|---|
| 足够小? | 1 claim + summary, 1 维判断 | YES |
| 足够明确? | claim 携带 structural signature + scope | YES (需 scope 定义) |
| 可 falsify? | 对 evidence summary + held-out GT | YES |
| 产生 UNKNOWN? | 显式 UNKNOWN (证据不足) | YES |
| 绑定 provenance? | claim → 支撑证据链 (Level 4) | YES (需实现) |
| 保留 boundary? | claim 携 scope; boundary on-demand | YES (需实现) |
| 导致 Human 重读大量 evidence? | 默认 NO (summary); on-demand YES | 设计上 NO |
| 被 Pattern reuse? | validated claim → pattern reuse | YES |
| 进入 Capability Candidate? | claim → candidate → human registration | YES |
| 保持 Human Controlled Registration? | registration 非 automatic | YES |

**反证结果 [D]**: Semantic Claim **仍适合**作为最小 Human Validation Unit。10/10 维度通过 (其中 4 项需实现才生效)。不因反证而推翻。

---

## 12. Structural Abstraction vs Semantic Abstraction (§16)

| 层 | System 可做? | 理由 |
|---|---|---|
| Structural Abstraction (group/signature/compare/count) | **YES** [D] | 结构事实, authority=0, 无语义越权 |
| Semantic Abstraction (pattern=语义类/scope=语义边界/conclusion) | **NO** [D] | 语义 authority 经 Human |

**划分 [D]**:
- System: "这 15 个实例存在这些共同**结构** (co-structure≥3, same_y_band, different_partition)" — 允许;
- System: "所以它们属于某个**语义** Pattern (表格行号)" — **禁止** (Semantic Closure);
- Human: 判断 "这些结构是否支持该语义解释" — 允许。

---

## 13. 最小可行 System Abstraction (§17)

为使 Human 只验证 Semantic Claim, System **最少**必须承担 [D]:

```
Minimum System Responsibilities =
  Aggregation (group by structural signature)
+ Evidence Compression (summarize: consistent/conflict/UNKNOWN counts)
+ Provenance Preservation (claim → source 可回溯)
+ Conflict Preservation (conflict 不得隐藏)
+ UNKNOWN Preservation (UNKNOWN 不得强制归并)
```

### commonality/boundary/negative discovery 是否第一阶段必须? [I]
- **commonality**: **必须** (无共性无法 group → 无 compression) — 但 = structural signature (非语义);
- **boundary**: **可延后** (第一阶段可不含 pattern boundary; Human 在 Level 2 审查 prototype 即可; boundary discovery 是优化非必须);
- **negative**: **必须** (无 negative → overgeneralization 风险) — 但 = structural signature 负例 (density=0/margin), 非语义标签。

**最小集 = aggregation + compression + provenance + conflict + UNKNOWN + commonality(structural) + negative(structural)**。boundary 可延后。**不过度设计。**

---

## 14. 三层能力模型 (§18)

| 层 | 内容 | 自动化? | 当前 |
|---|---|---|---|
| L1 Evidence Organization | group/aggregate/link/provenance | System (structural) | provenance EXISTS; group/aggregate MISSING |
| L2 Evidence Compression | summarize/compress/preserve contradiction/preserve UNKNOWN/progressive disclosure | System (structural) | 全 MISSING (progressive disclosure 设计 only) |
| L3 Semantic Abstraction | semantic pattern/semantic claim/scope/boundary | **Human** (System 只产 Candidate) | Semantic Claim 对象 MISSING; Human authorization EXISTS |

**结论 [D]**: L1/L2 = System 自动 (结构, authority=0); L3 = Human (语义, authority)。L1/L2 当前大部分 MISSING; L3 对象缺失但 authority 边界清晰。

---

## 15. Evidence Compression 对 HVC 的影响 (§19)

| HVC 变量 | Compression 影响 | 机制 |
|---|---|---|
| review_count | ↓ | N instance → M claims (M≪N) |
| evidence_exposure | ↓ | default Level 0 (summary) |
| cross_instance_comparison | ↓ | System 已做 |
| interaction_cost | ↓ | 默认少展开 |
| decision_complexity | ↓ | 1 维判断 (SUPPORTED/UNSUPPORTED/UNKNOWN) |
| fatigue | ↓ | 单次简单 + 复用 |
| **error_risk** | **不得 ↑** | 若 ↑ = 虚假 HVC 降低 (evidence hiding/over-compression) |

**禁止 [D]**: 通过 evidence hiding / semantic over-compression 获得 review_count↓ 但 error_risk↑ 的虚假 HVC 降低。Compression Fidelity 是硬约束。

---

## 16. 证据等级汇总

| 结论 | 等级 |
|---|---|
| 当前 8/12 System 能力 MISSING | [O] (grep + 代码核查) |
| Workflow C 设计上降低 HVC | [D] |
| burden transfer 风险 6 项 PRESENT | [I] |
| 缓解机制有效 | [H] (未实验) |
| 现有 frozen observation 足够 | [EV] (M-B audit) |
| Semantic Claim 适合 validation unit | [D] |
| Pattern = compression+reuse layer | [D] |
| 长期可持续 @10000 | [H] (未验证) |
| compression fidelity 可定义 | [D] |
| progressive disclosure 安全 | [D] + 残余风险 [H] |

**无任何 [E] (无 human subject experiment)。不把 design 写成 experimentally verified。**

---

## 17. 十个问题回答

### Q1: 现有 DICE 是否已具备 Aggregation/Comparison/Compression/Coverage/Conflict/UNKNOWN?
- Aggregation: **MISSING** [O]
- Structural Comparison: **PARTIAL** (pairwise 实例对; 无跨实例) [O]
- Evidence Compression: **MISSING** [O]
- Coverage Construction: **MISSING** [O]
- Conflict Preservation: **PARTIAL** (EIC-1 临时产物; 架构无) [O]
- UNKNOWN Preservation: **PARTIAL** (实例级 EXISTS; 跨实例聚合 MISSING) [O]
**6 项: 0 EXISTS, 3 PARTIAL, 3 MISSING。不足以支撑 Workflow C。**

### Q2: Workflow C 最大工程缺口?
**跨实例 Evidence Aggregation + Structural Signature 层** (L1 Evidence Organization) [I]。无此层, compression/coverage/commonality 全无基础。这不是 observation gap (frozen 观测够 [EV]), 非 consumer gap (M-B 已证 [EV]), 是**新抽象层**。

### Q3: Workflow C 最大治理风险?
**Silent Suppression + Automation Bias** [I]。System 压缩时隐藏 conflict/negative → Human 误批准 (R1); 长期默认相信 summary (R6)。缓解 = 诚实 summary + auditable provenance + 强制可展开 + 抽样 audit; **残余风险未验证** [H]。

### Q4: Compression Fidelity 如何定义?
关键证据 (positive/negative/boundary/UNKNOWN/conflict/provenance) 在压缩后仍可恢复/追溯/审查 [D]。System 提议关键证据 (structural role), Human 确认 (boundary adequacy); System 不得单方面删除; semantic heuristic 选关键 = Semantic Closure 禁止。

### Q5: Progressive Disclosure 是否安全?
**设计上安全 IF**: summary 诚实 + provenance 全保留 + Level 4 可访问 + 可独立重算 [D]。**残余风险**: silent suppression + automation bias, **未实验验证** [H]。Evidence visibility ≠ Evidence authority。

### Q6: System 可承担到哪一级 abstraction?
**Structural Abstraction (L1/L2)** — group/signature/compare/count, authority=0 [D]。**Semantic Abstraction (L3)** — 保留 Human; System 只产 Candidate [D]。

### Q7: Human 最终应只做什么?
**Semantic interpretation validation + final authorization** (SUPPORTED/UNSUPPORTED/UNKNOWN) [D]。boundary adequacy on-demand confirmation; scope acceptance (若需)。不重建 pattern / 不比较实例 / 不建 negative / 不发现 boundary。

### Q8: Semantic Claim 是否仍适合?
**YES** [D]。10/10 维度通过 (4 需实现)。反证未推翻。

### Q9: Pattern 最终应该是什么?
**Evidence Compression + Reuse Layer** [D]。组织+压缩+复用, 透明于 Human, 无 runtime authority。概念 KEEP, 但当前不可实现 (依赖 6 MISSING 能力)。

### Q10: @100/1000/10000/100000 理论可持续性?
- 100: A 可忍, C 设计可行 [D];
- 1000: A 疲劳, C 设计可持续 [H];
- 10000: A 不可持续, C **理论上**可持续 [H];
- 100000: C 理论上可持续 (若 System 可信 + audit 机制), 但**完全未验证** [H]。
"理论上可持续" ≠ "已实证可持续"。需 human subject 实验。

---

## 18. 核心原则最终判断

> **"DICE Pattern 的核心价值不是替 Human 做语义判断, 而是替 Human 完成证据组织、压缩和比较, 使 Human 可以在更低 Cognitive Load 下完成最小的 Semantic Validation。"**

**成立 [D]**。记录为 L5.2 核心设计原则。

补充约束 [D]:
1. Pattern = compression+reuse layer, 非 semantic authority;
2. System 承担 structural abstraction (L1/L2), authority=0;
3. Human 承担 semantic abstraction (L3), 唯一 authority;
4. Compression Fidelity 硬约束 (关键证据可恢复/追溯/审查);
5. Evidence visibility ≠ authority (不展示≠删除, Level 4 always reachable);
6. 残余风险 (silent suppression/automation bias) 未验证 → 需 audit + human subject 实验;
7. 当前 6/9 System 能力 MISSING → Pattern 概念 KEEP 但**不可立即实现**。

---

## 19. Gate

```text
==================================================
L5.2 EVIDENCE COMPRESSION FEASIBILITY REVIEW
==================================================
STATUS: DESIGN-ONLY / READ-ONLY (no implementation, no experiment)

L5.2 STATUS = CONDITIONAL PASS
  (design direction sound: Pattern=compression+reuse layer, System=structural abstraction,
   Human=semantic validation; BUT 6/9 System capabilities MISSING, Workflow C not implementable now;
   burden transfer risks 6 PRESENT with design mitigations but unverified residuals)

PATTERN_ROLE = Evidence Compression + Reuse Layer (transparent to Human, no runtime authority)
HUMAN_VALIDATION_UNIT = Semantic Claim (confirmed, 10/10 dimensions pass; 4 need implementation)
SYSTEM_ABSTRACTION_LEVEL = Structural Abstraction only (L1/L2, authority=0); Semantic Abstraction = Human
EVIDENCE_COMPRESSION_STATUS = MISSING (no aggregation/compression/summary object; design only)
COMPRESSION_FIDELITY_STATUS = DEFINED (7 indicators; System-proposes/Human-confirms; residual risk unverified)
PROGRESSIVE_DISCLOSURE_STATUS = DESIGN PROPOSED (Level 0-4); safe by design IF honest summary+provenance+audit; residual risk unverified
HUMAN_ABSTRACTION_BURDEN = ELIMINATED by design in C (IF System capability built); currently would transfer to Human if forced
BURDEN_TRANSFER_RISK = 6 RED-TEAM CASES PRESENT (R1-R6); mitigations designed; residuals unverified
SEMANTIC_AUTHORITY_RISK = Compression Layer authority=0 (by design); residual = structural signature may hide semantic assumption (R4); needs audit
CURRENT_SYSTEM_CAPABILITY = EXISTS=2 (provenance, human-auth); PARTIAL=3 (pairwise-comparison, UNKNOWN-instance, conflict-temporary); MISSING=8
MINIMUM_REQUIRED_SYSTEM_CAPABILITY = aggregation + compression + provenance-preserved + conflict-preserved + UNKNOWN-preserved + commonality(structural) + negative(structural); boundary deferrable
NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE (frozen observation sufficient; gap=abstraction layer, not measurement)
IMPLEMENTATION_AUTHORIZATION = NOT AUTHORIZED
EXPERIMENT_AUTHORIZATION = NOT AUTHORIZED
FROZEN_BASELINE = INTACT
STOP = TRUE
==================================================
```

## 附: L5.2 设计原则记录

1. Pattern = Evidence Compression + Reuse Layer (非 validation object, 非 semantic authority);
2. System 承担 Structural Abstraction (L1 Evidence Organization + L2 Evidence Compression), authority=0;
3. Human 承担 Semantic Abstraction (L3), 唯一 semantic authority;
4. Compression Layer authority = 0 (只改组织, 不改语义);
5. Compression Fidelity 硬约束 (positive/negative/boundary/UNKNOWN/conflict/provenance 可恢复);
6. System 提议关键证据 (structural role), Human 确认 (boundary adequacy); System 不得单方面删除;
7. Evidence visibility ≠ authority (不展示≠删除; Level 4 always reachable);
8. Progressive Disclosure (Level 0 default minimal → Level 4 on-demand full);
9. 诚实 summary (conflict/UNKNOWN count 不隐瞒) + auditable provenance + 可独立重算;
10. 残余风险 (silent suppression/automation bias/structural-signature-hides-semantic) 未验证 → 需 audit + human subject 实验;
11. Semantic Claim = validation unit (candidate, 非 conclusion; Human ACCEPT 前无 authority);
12. Pattern 概念 KEEP 但当前 6/9 System 能力 MISSING → 不可立即实现。
