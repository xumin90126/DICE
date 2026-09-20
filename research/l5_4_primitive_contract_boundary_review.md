# L5.4 Minimum Primitive Contract Boundary Review

> DESIGN-ONLY / READ-ONLY。为 Aggregation + Evidence Compression 建立最小、可证伪、不可越权的
> Primitive Contract。不实现代码, 不实现 Pattern, 不实现 Pattern Engine。
>
> 核心原则: **Compress evidence, not meaning.** / **Human should validate, not reconstruct.**

标注: [O] observed · [I] inferred · [H] hypothesis · [D] design · [EV] experimentally verified

---

## 0. 前置: L5.3 结论 (本阶段基线)

```
Minimum System Capability Set = { Aggregation, Evidence Compression }
  + 6 Compression Fidelity Constraints (conflict/UNKNOWN/coverage/provenance/non-positive/candidate)
```

L5.4 不再讨论"还需要什么能力"。只回答: **如果 System 只有这两个 primitive, 如何保证它们足以支持 Workflow C, 同时不演化成 Pattern Miner / Semantic Classifier / Decision Engine?**

---

## 1. Primitive A — Aggregation 最小定义

> **Aggregation = organize existing Evidence into explicitly structured groups according to declared structural relations, without assigning semantic roles.**

### 1.1 审查清单 [D]

| 问题 | 判定 | 理由 |
|---|---|---|
| 什么作为 grouping input? | frozen structural features only | same_y_band / co_density / region_forms / partition_id / localization [O, from frozen P2 + EIC-1] |
| 什么是合法 grouping relation? | structural signature equality (frozen features 的值匹配) | 非 semantic equivalence |
| group 最小输出? | {group_id, signature, member_instance_refs} | 不含 semantic label / prototype / representative / score |
| group 允许跨 document/page? | YES (structural signature 跨文档可比; 但 provenance 保留各自 source) | grouping 是结构关系, 非 document 约束 |
| group 可基于已有 frozen relations? | YES (StructuralRelation 8 types [O] + EIC-1 structural context [O] 作 signature 组件) | 复用 frozen, 不创建新关系 |
| group 允许引入 semantic label? | **NO** (FORBIDDEN) | semantic label = semantic role = Semantic Closure |
| group 允许自动判断"同一种语义"? | **NO** (FORBIDDEN) | Same Structure ≠ Same Meaning |
| group 允许自动选择 representative? | **NO** (FORBIDDEN at primitive level; DEFERRED per L5.3) | selection = ranking = authority >0 |
| group 允许 ranking/scoring? | **NO** (FORBIDDEN) | authority >0 |
| group 允许 recommendation? | **NO** (FORBIDDEN) | authority >0 |

### 1.2 核心区分 [D]

```
Structural Similarity ≠ Semantic Equivalence
Same Structure ≠ Same Meaning
```

**Aggregation 能否在不做 semantic inference 的情况下成立?** — **YES** [D]。
grouping key = frozen structural features 的值匹配 (deterministic, structural, 无语义推理)。
10 个实例结构相似但语义不同 → Aggregation 仍 group 它们 (by structure) → 不标 semantic role → 不越权 [I, R1]。

---

## 2. Primitive B — Evidence Compression 最小定义

> **Evidence Compression = reduce Human evidence exposure while preserving the ability to recover, inspect, and audit the underlying Evidence.**

### 2.1 审查清单 [D]

| 问题 | 判定 | 理由 |
|---|---|---|
| Compression 输入? | aggregation 输出 (groups) + per-instance EIC-1 candidate [O] + per-instance provenance [O] + per-instance INSUFFICIENT_EVIDENCE [O] | 全部 EXISTS [O] |
| Compression 输出? | summary (counts: consistent/conflict/UNKNOWN/coverage) + Semantic Claim Candidate (aggregated EIC-1 candidates, status=candidate) | 非 conclusion |
| 什么可以被压缩? | instance-level 细节 (bbox/text/per-instance trace) → counts + grouped candidate | exposure↓ |
| 什么绝对不能丢失? | F1-F7 (positive/negative/boundary/UNKNOWN/conflict/provenance/claim-traceable) | fidelity 硬约束 |
| summary 可包含 semantic language? | **ONLY** 来自已有 EIC-1 governed candidate 的 wording [O]; 不得创建新 semantic language | "Compress evidence, not meaning" |
| summary 可生成 Semantic Claim? | **Candidate only** (aggregated per-instance EIC-1 candidates, 模板陈述); 不得生成 conclusion | status=candidate [O] |
| summary 可自动判断 supported/unsupported? | **NO** (FORBIDDEN) | judgment = Human authority |
| summary 可隐藏 negative/UNKNOWN/conflict? | **NO** (FORBIDDEN — F2/F4/F5) | silent suppression |
| summary 可替 Human 判断 boundary? | **NO** (FORBIDDEN) | boundary judgment = Human |
| 必须支持 Level 4 provenance recovery? | **YES** (F6) | 可审计 |

### 2.2 核心区分 [D]

```
Evidence Compression ≠ Semantic Compression
```

**如果 summary 只有在自动完成 semantic interpretation 后才能生成, 则该 summary 不属于合法 System Compression。** [D]

合法 Compression: counts (deterministic from group membership) + aggregated existing EIC-1 candidate wording (governed, status=candidate)。
非法 Compression: System 自己推断 "这些实例都是表格行号" (new semantic interpretation)。

---

## 3. Primitive Contract Matrix

| Dimension | Aggregation | Evidence Compression |
|---|---|---|
| Input | frozen structural features (same_y_band/co_density/region_forms/partition_id/localization) [O] | aggregation output (groups) + per-instance EIC-1 candidate [O] + provenance [O] + INSUFFICIENT_EVIDENCE [O] |
| Output | groups: {group_id, signature, member_refs} | summary (counts) + Semantic Claim Candidate (aggregated EIC-1, status=candidate) |
| Operation | group by structural signature equality | count group members; aggregate existing EIC-1 candidates (template); preserve fidelity |
| Authority | **0** | **0** |
| Semantic Interpretation | **FORBIDDEN** | **FORBIDDEN** |
| Semantic Claim | 禁止生成最终结论 | 只能保留/组织 candidate (status=candidate [O]); 不得自主确认 |
| Ranking | FORBIDDEN | FORBIDDEN |
| Scoring | FORBIDDEN | FORBIDDEN |
| Selection | FORBIDDEN | FORBIDDEN |
| Recommendation | FORBIDDEN | FORBIDDEN |
| Decision | FORBIDDEN | FORBIDDEN |
| Provenance | 必须可追溯 (member_ref → instance → frozen source) | 必须保留 (Level 4 recoverable) |
| UNKNOWN | 不得消失 (partition-unresolvable 实例须入 group 或显式 UNKNOWN-group) | 必须保留 (UNKNOWN_count in summary) |
| Conflict | 不得消失 (EVIDENCE_CONFLICT 实例须显式标记) | 必须保留 (conflict_count in summary) |
| Negative Evidence | 不得 silent suppression (非-正例 group 须保留) | 必须可恢复 (non-positive group preserved) |
| Boundary Evidence | 不得伪造 (grouping criteria = declared structural, 非 inferred boundary) | 必须可恢复 (grouping criteria stated in summary) |
| Human Override | N/A (Aggregation 不产 judgment, 无需 override) | N/A (Compression 不产 judgment, 无需 override) |
| Runtime Authority | **0** | **0** |

---

## 4. Allowed / Forbidden Operation 边界

### 4.1 AGGREGATION_ALLOWED [D]
- read frozen structural features (same_y_band/co_density/region_forms/partition_id/localization);
- group instances by structural signature equality (deterministic value match);
- output group_id + signature + member_instance_refs;
- preserve per-instance provenance reference;
- explicitly mark partition-unresolvable instances (UNKNOWN-group);
- explicitly mark EVIDENCE_CONFLICT instances (conflict-tag within group);
- preserve non-positive groups (different signature groups retained);
- declare grouping criteria (signature definition = hard boundary statement).

### 4.2 AGGREGATION_FORBIDDEN [D]
- semantic clustering (group by meaning);
- semantic labeling (assign is_table/is_cell/is_row/caption/value-column/...);
- automatic pattern discovery (infer "this is a pattern");
- prototype semantic selection (choose "best" representative);
- negative semantic classification (label "this is negative");
- boundary semantic inference (infer semantic boundary);
- scope inference (infer applicability domain semantically);
- confidence score;
- ranking;
- best representative selection;
- decision / routing / recommendation;
- **任何 forbidden field** (is_table/is_cell/is_row/is_column/is_header/is_row_number/code_line/semantic_role/table_id/cell_id/score/confidence/recommendation/merge_candidate/keep_candidate/decision/priority/winner [O, EIC-1 FORBIDDEN set])。

### 4.3 COMPRESSION_ALLOWED [D]
- count group members (consistent/conflict/UNKNOWN/coverage);
- aggregate existing EIC-1 candidate wording (template: "N instances with signature X have EIC-1 candidate Y");
- preserve per-instance provenance reference (Level 4 recoverable);
- output summary with explicit counts;
- output Semantic Claim Candidate (status=candidate, aggregated);
- declare grouping criteria in summary;
- preserve non-positive groups (as separate claims or explicit negative-count);
- preserve UNKNOWN_count / conflict_count / coverage_count.

### 4.4 COMPRESSION_FORBIDDEN [D]
- semantic conclusion generation (output "these are table rows");
- semantic closure (close interpretation boundary);
- silent removal of contradictory evidence (hide conflict);
- silent removal of UNKNOWN (hide insufficient-evidence);
- silent removal of negative evidence (hide non-positive group);
- automatic boundary judgment (declare scope adequate/inadequate);
- automatic scope judgment (declare applicability);
- automatic support judgment (declare SUPPORTED/UNSUPPORTED);
- confidence score;
- ranking;
- recommendation;
- fallback / correction / override;
- runtime action (execute/route/select);
- **创建新 semantic interpretation** (Y not from EIC-1 governed mapping);
- **任何 forbidden field** (同 Aggregation FORBIDDEN set [O])。

### 4.5 关键区分 [D]
> **"不得丢失" ≠ "必须自动判断"**

- Negative Evidence: Compression **必须保留** (F2); 但 System **不得自动判断** "这是 Negative Example" (semantic role = Human);
- UNKNOWN: Compression **必须保留** (F4); 但 System **不得自动解释** UNKNOWN 的语义原因;
- Conflict: Compression **必须保留** (F5); 但 System **不得仲裁** (no winner [O]);
- Boundary: Compression **必须可恢复** (F3); 但 System **不得判断** boundary adequacy (Human on-demand)。

---

## 5. Semantic Claim Candidate 严格审查 (§5)

### 5.1 四问 [D]

1. **Aggregation 是否真能产生 claim candidate?** — **NO**。Aggregation 只 group (structural); 不产 claim。Claim 来自 EIC-1 governed mapping (per-instance candidate [O]);
2. **Compression 是否只压缩已有 EIC-1 candidate?** — **YES** [D]。Compression aggregate per-instance EIC-1 candidates (template), 不创建新 candidate;
3. **System 是否可能在没有 EIC-1 的情况下凭 structural similarity 自己创造 semantic claim?** — **若发生 = semantic leakage, FORBIDDEN** [D]。System 不得凭 "10 个结构相似" 自己推断 "它们是表格行号"。Structural similarity → grouping (allowed); Structural similarity → semantic claim (FORBIDDEN);
4. **System-generated semantic content 的本质?** — [D]:
   ```
   System-generated semantic content
   = recombination / organization of already governed candidate evidence (EIC-1)
   NOT = new semantic interpretation
   ```

### 5.2 区分 [D]
```
Template of Existing Candidate Claims (ALLOWED)
  = "N instances with signature X have EIC-1 candidate Y (status=candidate)"
  = aggregation + compression of governed candidates

New Semantic Interpretation (FORBIDDEN)
  = "N instances are table rows" (Y not from EIC-1)
  = semantic inference by System
```

**不能因为多个 candidate 相似, 就自动宣称"系统发现了一个 Pattern"。** [D]
- "发现 Pattern" (semantic) = Human 验证后;
- System 只 "grouped instances with shared signature + shared candidate" (structural + governed)。

---

## 6. Compression Fidelity Contract (正式化)

| ID | 约束 | 定义 | 来源 | 失败模式 |
|---|---|---|---|---|
| F1 | Positive Evidence Preservation | 正例 group 的 structural signature + member refs 保留 | aggregation output | 丢失 → claim 无支撑 |
| F2 | Negative Evidence Preservation | 非-正例 group 保留 (不 silent suppression) | aggregation output | 丢失 → overgeneralization |
| F3 | Boundary Evidence Preservation | grouping criteria (signature 定义) 在 summary 显式 | aggregation criteria | 丢失 → scope 不明 |
| F4 | UNKNOWN Preservation | UNKNOWN_count 显式 (partition-unresolvable 实例) | IS-11 INSUFFICIENT_EVIDENCE [O] | 丢失 → false closure |
| F5 | Conflict Preservation | conflict_count 显式 (EVIDENCE_CONFLICT 实例) | EIC-1 coexistence [O] | 丢失 → silent suppression |
| F6 | Provenance Recoverability | claim → instance → frozen source 全链可展开 (Level 4) | EIC-1 case_ref + frozen_p2 [O] | 丢失 → 不可审计 |
| F7 | Semantic Claim Traceability | claim candidate → per-instance EIC-1 candidate → EIC-1 governed mapping → frozen evidence 全链可追溯 | EIC-1 chain [O] | 丢失 → Human 无法验证 |

### F7 追溯链 [D]
```
Claim Candidate (aggregated)
    ↓ (Level 0)
Compressed Evidence (summary + counts)
    ↓ (Level 1)
Evidence Group (signature + member_refs)
    ↓ (Level 2/3)
Original Evidence (per-instance EIC-1 candidate + provenance)
    ↓ (Level 4)
Observation / Frozen Source (frozen P2 + atomic observation)
```
任何一级无法恢复 = **Compression Fidelity Failure** [D]。

---

## 7. Progressive Disclosure Contract (§7, 非实现)

### 7.1 原则 [D]
```
Hidden Evidence ≠ Absent Evidence
Compressed Evidence ≠ Less Authoritative Evidence
```

### 7.2 Recoverability 保证 [D]
- Human 可从 Level 0/1 回到 Level 4 (强制可访问);
- 若不能保证 recoverability → Compression Contract **不完整**;
- Level 4 = full provenance (per-instance case_ref + frozen source sha) [O, EXISTS];

### 7.3 风险审查 [I]
| 风险 | 机制 | 缓解 |
|---|---|---|
| Evidence Visibility 被误认为 Evidence Authority | "不展示" 被理解为 "不存在/不重要" | 显式标注: "N items hidden, expandable" |
| Compressed 被理解为 Less Authoritative | summary 被理解为 "简化=弱证据" | 显式标注: "compression preserves all evidence; Level 4 full" |
| Human 被迫相信 compression | 无 Level 4 入口 | 强制 Level 4 always reachable |

**判定 [D]**: Progressive Disclosure **纳入 Contract** (非独立能力); 作为 Compression 的 recoverability 约束 (F6)。不实现 UI。

---

## 8. Authority Gradient (§8)

```
Observation (L1/L2, frozen, source-backed)
    ↓ [System: read]
Evidence (L2/L3, frozen fact)
    ↓ [System: read]
Structural Abstraction (L3, Aggregation, authority=0)
    ↓ [System: group by signature]
Evidence Compression (L3→L4 boundary, Compression, authority=0)
    ↓ [System: aggregate existing candidates, status=candidate]
Semantic Claim Candidate (L4, governed by EIC-1, candidate not conclusion)
    ↓ [Human: semantic interpretation + validation] ← Human 重获 semantic authority
Validated Semantic Claim (L5, Human ACCEPT)
    ↓ [Human: registration decision] ← Human capability authority
Capability (L6, Human Controlled)
```

### 逐层回答 [D]
| 层 | System 能做? | System 不能做? |
|---|---|---|
| Observation→Evidence | read | create/modify |
| Evidence→Structural Abstraction | group by structural signature | semantic label/infer meaning |
| Structural Abstraction→Compression | count + aggregate existing candidates | create new interpretation/judge support |
| Compression→Claim Candidate | output candidate (status=candidate) | confirm/close/conclude |
| Claim Candidate→Human Validation | **N/A (Human)** | System 不得自动 validate |
| Human Validation→Capability | **N/A (Human)** | System 不得 auto-register |

### interpretation / validation / authorization 发生点 [D]
- **interpretation**: EIC-1 governed mapping (per-instance candidate, EXISTS [O]) — System 产 candidate, 不产 conclusion;
- **validation**: Human (SUPPORTED/UNSUPPORTED/UNKNOWN) — Human semantic authority;
- **capability authorization**: Human registration decision (FROZEN_CAPABILITY_TABLE [O]) — Human controlled.

### Boundary violation 检查 [D]
| 禁止 transition | 判定 |
|---|---|
| Aggregation → Semantic Interpretation | **FORBIDDEN** (structural only) |
| Compression → Semantic Interpretation | **FORBIDDEN** (aggregate existing candidate only) |
| Compression → Capability | **FORBIDDEN** (no auto-registration) |
| Aggregation → Decision | **FORBIDDEN** (no ranking/selection) |
| Compression → Decision | **FORBIDDEN** (no judgment/support-declaration) |

**无 boundary violation。** ✓

---

## 9. Semantic Closure Red-Team (§9, 8 攻击场景)

### R1: 10 实例结构相似但语义不同 → Aggregation 错误 group?
- **Aggregation 行为**: group by structural signature (10 实例同 signature → 同 group) [D];
- **是否越权?** **NO** — group 是结构关系, 不标 semantic role; "同结构 ≠ 同语义" 在 contract 中显式声明;
- **风险**: Human 若误读 group 为 semantic equivalence → 缓解: summary 显式标 "structural signature group, not semantic class" [D];
- **判定**: **SAFE by contract** (grouping ≠ semantic labeling)。

### R2: 9 支持 + 1 conflict → Compression 隐藏 conflict?
- **Compression 行为**: summary 必须含 conflict_count (F5) [D];
- **是否越权?** 若 conflict_count=0 而 Level 3 有 1 conflict → **F5 Failure** (silent suppression);
- **缓解**: F5 强制 conflict_count 显式; Level 3 可展开; summary-vs-Level3 consistency 可检测;
- **判定**: **F5 约束覆盖**; 残余风险 = System 不诚实计数 → 需 audit [H]。

### R3: 大量 UNKNOWN → Compression 只展示确定实例?
- **Compression 行为**: summary 必须含 UNKNOWN_count (F4) [D];
- **是否越权?** 若 UNKNOWN 被省略 → **F4 Failure** (false closure);
- **缓解**: F4 强制 UNKNOWN_count 显式; UNKNOWN-group 保留;
- **判定**: **F4 约束覆盖**; 残余风险同 R2 [H]。

### R4: Negative 远少于 Positive → silent suppression negative?
- **Compression 行为**: 非-正例 group 必须保留 (F2) [D];
- **是否越权?** 若 non-positive group 被删除 → **F2 Failure** (overgeneralization);
- **缓解**: F2 强制 non-positive group preserved; System **不得标** "这是 negative" (semantic role = Human);
- **判定**: **F2 约束覆盖**; "不得丢失 ≠ 必须自动判断" (System 保留非标 role) [D]。

### R5: 结构不同但语义相同 → Aggregation 不 group?
- **Aggregation 行为**: 不同 signature → 不同 group (structural) [D];
- **是否问题?** **NO** — 这是 semantic equivalence 问题, **System 不需解决**; 交给 Human (Human 可在 validation 中判定 "这两个 structural group 其实是同一语义");
- **判定**: **System 正确不做**; semantic equivalence = Human authority [D]。

### R6: caption/table/code/TOC 结构相似 → Aggregation 升级为 semantic role?
- **Aggregation 行为**: group by structural signature (可能同 group) [D];
- **是否越权?** 若 System 标 "这是 caption" → **Semantic Closure (FORBIDDEN)**;
- **缓解**: Aggregation FORBIDDEN semantic labeling; group 只含 signature + member_refs; "caption"/"table" label = Human 验证后;
- **判定**: **SAFE by contract** (grouping ≠ semantic role assignment)。

### R7: EIC-1 candidate wording 部分相似 → Compression 生成超出原 candidate 的新 claim?
- **Compression 行为**: aggregate existing EIC-1 candidates (template) [D];
- **是否越权?** 若 Compression 创建新 wording (Y not from EIC-1) → **semantic leakage (FORBIDDEN)**;
- **缓解**: Compression 只 recombine governed candidate wording; 不创建新 Y; F7 traceability 强制 claim → per-instance EIC-1 → governed mapping 可追溯;
- **判定**: **SAFE by contract** (F7 + "Compress evidence not meaning")。

### R8: 单实例极高 evidence volume → 支配 summary?
- **Compression 行为**: count group members (1 instance = 1 count, 非 volume-weighted) [D];
- **是否越权?** 若 count 按 evidence volume 加权 → **隐性 ranking (FORBIDDEN)**;
- **缓解**: count = instance count (1-per-instance), 非 evidence-volume-weighted; summary 显式标 "N instances" 非 "N evidence units";
- **判定**: **SAFE by contract** (count ≠ weighting)。

### Red-Team 总结 [I]
| 场景 | 风险 | Contract 覆盖 | 残余风险 |
|---|---|---|---|
| R1 | structural≠semantic 误读 | contract 显式声明 | LOW [H] |
| R2 | conflict 隐藏 | F5 | audit [H] |
| R3 | UNKNOWN 隐藏 | F4 | audit [H] |
| R4 | negative 隐藏 | F2 | audit [H] |
| R5 | semantic equivalence | System 正确不做 | NONE |
| R6 | semantic role 越权 | FORBIDDEN labeling | NONE |
| R7 | new claim 越权 | F7 + compress-not-mean | NONE |
| R8 | volume weighting | count≠weighting | NONE |

**8 场景全部 SAFE by contract**; 残余风险 = System 不诚实 (R2/R3/R4) → 需 audit 机制 (未来, 非本阶段)。

---

## 10. 不引入新 Capability (§10)

| 候选 | 判定 | 理由 |
|---|---|---|
| Representative Engine | **NOT primitive** (DEFERRED, L5.3) | L0 不需; 智能 = bias; first/random 可作 view |
| Boundary Engine | **NOT primitive** (DEFERRED, L5.3) | grouping criteria = boundary; edge = 优化 |
| Negative Detector | **NOT primitive** (DERIVED) | = 非-正例 group (preserve, 非 semantic discovery) |
| Conflict Engine | **NOT primitive** (MERGED) | = F5 constraint (conflict_count) |
| Coverage Engine | **NOT primitive** (MERGED) | = count in summary |
| Pattern Miner | **FORBIDDEN** | semantic pattern discovery = Human |
| Pattern Classifier | **FORBIDDEN** | semantic classification = Human |

**全部 = Derived View / Constraint / Metadata, 非 independent Capability。** 无新 primitive 通过 Deletion Test。Minimum Set 不变 = {Aggregation, Evidence Compression}。

---

## 11. 三个核心产物

### 产物 1: Minimum Primitive Contract

#### Aggregation
```
Aggregation MUST:
  - read frozen structural features only (same_y_band/co_density/region_forms/partition_id/localization)
  - group by structural signature equality (deterministic)
  - output {group_id, signature, member_instance_refs}
  - preserve per-instance provenance reference
  - explicitly mark UNKNOWN instances (partition-unresolvable)
  - explicitly mark CONFLICT instances (EVIDENCE_CONFLICT)
  - preserve non-positive groups (different signature)
  - declare grouping criteria (= hard boundary statement)
  - enforce forbidden-field assertions (is_table/is_cell/.../winner) [O, EIC-1 FORBIDDEN set]

Aggregation MAY:
  - group across document/page (structural signature is cross-document comparable)
  - use frozen StructuralRelation (8 types [O]) + EIC-1 structural context [O] as signature components
  - output UNKNOWN-group / conflict-tag as group metadata

Aggregation MUST NOT:
  - assign semantic labels (is_table/is_cell/is_row/caption/value-column/...)
  - infer semantic equivalence ("same structure = same meaning")
  - select representative / prototype (DEFERRED)
  - rank / score / recommend / decide / route
  - infer semantic boundary / scope
  - create new relations (only use frozen)
  - output any forbidden field
```

#### Evidence Compression
```
Compression MUST:
  - take aggregation output (groups) + per-instance EIC-1 candidate [O] + provenance [O] + INSUFFICIENT_EVIDENCE [O]
  - output summary (consistent_count/conflict_count/UNKNOWN_count/coverage_count)
  - output Semantic Claim Candidate (aggregated EIC-1 candidates, status=candidate [O], template)
  - preserve F1-F7 (positive/negative/boundary/UNKNOWN/conflict/provenance/claim-traceable)
  - declare grouping criteria in summary
  - support Level 4 provenance recovery (F6)
  - enforce forbidden-field assertions [O]

Compression MAY:
  - aggregate existing EIC-1 candidate wording (template: "N instances with signature X have candidate Y")
  - output non-positive group as separate claim or explicit negative-count
  - compress instance-level detail (bbox/text) into counts + grouped candidate

Compression MUST NOT:
  - create new semantic interpretation (Y not from EIC-1 governed mapping)
  - generate semantic conclusion ("these are table rows")
  - close semantic boundary
  - judge SUPPORTED/UNSUPPORTED (Human authority)
  - judge boundary adequacy (Human on-demand)
  - silently remove conflict/UNKNOWN/negative (F2/F4/F5)
  - score/rank/recommend/fallback/correct/override
  - execute runtime action
  - weight by evidence volume (count = instance count, 1-per-instance)
  - output any forbidden field
```

### 产物 2: Semantic Boundary Map

```
System Authority = 0 (Aggregation + Compression, structural only)
Human Semantic Authority = interpretation + validation + authorization (sole)
Capability Registration Authority = Human (FROZEN_CAPABILITY_TABLE [O])
Runtime Authority = 0

Allowed transitions:
  Observation → Evidence (read)
  Evidence → Structural Abstraction (group by signature)
  Structural Abstraction → Compression (count + aggregate candidate)
  Compression → Semantic Claim Candidate (status=candidate)
  Claim Candidate → Human Validation (Human)
  Human Validation → Capability (Human registration)

Forbidden transitions:
  Aggregation → Semantic Interpretation ✗
  Compression → Semantic Interpretation ✗
  Compression → Capability ✗
  Aggregation → Decision ✗
  Compression → Decision ✗
  Structural Similarity → Semantic Claim (without EIC-1) ✗
```

### 产物 3: Implementation Readiness Checklist (非授权, 仅 contract 推导)

| 前置 | 状态 | Contract 要求 |
|---|---|---|
| frozen structural features (signature input) | EXISTS [O, EV] | Aggregation MUST read |
| EIC-1 governed mapping (candidate) | EXISTS [O] | Compression MUST aggregate (not create) |
| per-instance provenance | EXISTS [O] | F6 recoverability |
| IS-11 INSUFFICIENT_EVIDENCE | EXISTS [O] | F4 UNKNOWN preservation |
| EIC-1 EVIDENCE_CONFLICT | EXISTS [O] | F5 conflict preservation |
| forbidden-field assertion mechanism | EXISTS [O, EIC-1 FORBIDDEN set] | both MUST enforce |
| Aggregation layer (group by signature) | MISSING | implement per contract |
| Compression layer (summary + claim candidate) | MISSING | implement per contract |
| Level 4 recovery path | EXISTS [O] (provenance) | F6 MUST support |
| 新 Observation | NONE | not needed [EV] |

**CONTRACT_STATUS = READY** (contract 完整、可证伪、authority=0 明确、fidelity 约束正式化、red-team 全覆盖)。
**但 IMPLEMENTATION_AUTHORIZATION = NOT AUTHORIZED** (下一阶段单独授权)。

---

## 12. 最终判断

### 核心结论 [D]
如果未来实现 Aggregation + Evidence Compression 按 L5.4 Contract, 则:
- **足以支撑 Workflow C** (L5.3 已证 2 primitive 不可删除);
- **不引入 Semantic Closure** (contract FORBIDDEN semantic labeling/conclusion/closure; red-team 8 场景全 SAFE);
- **不引入 Decision Authority** (FORBIDDEN ranking/scoring/selection/recommendation/decision);
- **不引入 Pattern Engine** (无 Pattern Miner/Classifier; Pattern = Human 验证后概念);
- **不引入 Human Burden Transfer** (System 承担 aggregation + compression; Human 仅 semantic validation);
- **Compression Fidelity 保证** (F1-F7 正式化; recoverability 强制; Level 4 always reachable);
- **Authority Gradient 不破坏** (无 forbidden transition)。

### 成功标准达成 [D]
> "如果未来实现 Aggregation + Evidence Compression, 那么可以在不引入 Semantic Closure、Decision Authority、Pattern Engine 或 Human Burden Transfer 的情况下, 为 Workflow C 提供其已经证明不可删除的最小 System 支撑。"

**成立。** Contract 完整覆盖; 无需增加模块; 问题不退回 Contract Boundary。

---

## 13. Gate

```text
==================================================
L5.4 MINIMUM PRIMITIVE CONTRACT BOUNDARY REVIEW
==================================================
STATUS: DESIGN-ONLY / READ-ONLY (no implementation, no experiment)

L5.4 STATUS = CONDITIONAL PASS
  (contract complete: MUST/MAY/MUST NOT for both primitives; F1-F7 fidelity formalized;
   authority=0 enforced; red-team 8 scenarios all SAFE by contract; no new capability needed;
   no semantic closure / no decision authority / no pattern engine / no burden transfer;
   implementation-ready by contract but NOT authorized)

AGGREGATION_CONTRACT = READY (MUST/MAY/MUST NOT defined; forbidden-field enforced; authority=0)
COMPRESSION_CONTRACT = READY (MUST/MAY/MUST NOT defined; F1-F7 fidelity; authority=0; compress-evidence-not-meaning)

SEMANTIC_CLOSURE_RISK = NONE by contract (FORBIDDEN labeling/conclusion/closure; red-team SAFE)
  residual = System dishonesty in counting (R2/R3/R4) -> needs audit [H, future]

AUTHORITY_BOUNDARY = System=0 (structural); Human=sole semantic; Capability=Human-controlled; Runtime=0
  no forbidden transition present

COMPRESSION_FIDELITY = F1-F7 formalized (positive/negative/boundary/UNKNOWN/conflict/provenance/claim-traceable)
  F7 traceability chain: Claim → Compressed → Group → Evidence → Observation (any break = Failure)

PROGRESSIVE_DISCLOSURE = CONTRACTED (not implemented; = F6 recoverability constraint)
  Hidden≠Absent; Compressed≠Less-Authoritative; Level 4 always reachable

NEW_CAPABILITY_REQUIRED = NO (all candidates = derived/constraint/view/forbidden; Minimum Set unchanged)
NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE

IMPLEMENTATION_AUTHORIZATION = NOT AUTHORIZED
EXPERIMENT_AUTHORIZATION = NOT AUTHORIZED

GT = INTACT
TLD = INTACT
ATOMIC_OBSERVATION = INTACT
IS11_DECISION = INTACT
PRODUCTION = FALSE
FROZEN_BASELINE = INTACT
STOP = TRUE
==================================================
```

## 附: L5.4 Contract 原则

1. **Aggregation**: group by structural signature only; no semantic label; no representative/ranking/decision;
2. **Compression**: count + aggregate existing EIC-1 candidate; no new interpretation; no conclusion/closure/judgment;
3. **Compress evidence, not meaning** — compression 报告 governed candidate, 不创建语义;
4. **"不得丢失" ≠ "必须自动判断"** — negative/UNKNOWN/conflict 保留但 System 不判 semantic role;
5. **Structural Similarity ≠ Semantic Equivalence** — grouping ≠ semantic class;
6. **Same Structure ≠ Same Meaning** — semantic equivalence = Human;
7. **F1-F7 硬约束** — positive/negative/boundary/UNKNOWN/conflict/provenance/claim-traceable;
8. **Hidden ≠ Absent; Compressed ≠ Less Authoritative** — Level 4 always reachable;
9. **Authority Gradient 不破坏** — 无 forbidden transition;
10. **不引入新 Capability** — Representative/Boundary/Negative/Conflict/Coverage = derived/constraint/view; Pattern Miner/Classifier = FORBIDDEN;
11. **forbidden-field assertions** — is_table/is_cell/.../score/confidence/winner [O, EIC-1 FORBIDDEN set] 强制;
12. **CONTRACT_STATUS = READY; IMPLEMENTATION = NOT AUTHORIZED** (下一阶段单独授权)。
