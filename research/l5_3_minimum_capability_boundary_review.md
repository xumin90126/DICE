# L5.3 Minimum System Abstraction Boundary Review

> DESIGN-ONLY / READ-ONLY。对 L5.2 Missing Capabilities 做 Capability Deletion Test,
> 找出 Workflow C 真正不可缺少的 System 能力边界。不实现 Pattern, 不实现 Pattern Engine。
>
> 核心原则: **Compress evidence, not meaning.** / **Human should validate, not reconstruct.**

标注: [O] observed · [I] inferred · [H] hypothesis · [D] design · [EV] experimentally verified

---

## 0. 前置: L5.2 的 7 项 minimum-required (待压缩基线)

L5.2 给出: `aggregation + compression + provenance-preserved + conflict-preserved + UNKNOWN-preserved + commonality(structural) + negative(structural); boundary deferrable`

L5.3 的任务: 对这 7 项 + L5.2 的 8 项 MISSING 逐项做 Deletion Test, 证明哪些是**真 primitive** (删除则 Workflow C 崩), 哪些是**派生/合并/视图/可延后**。

---

## 1. Methodology — Capability Deletion Test

**判定规则** [D]:
1. 假设删除该 capability;
2. 检查 Workflow C 是否仍成立 (Human 仅做 Semantic Claim 验证, 不做 abstraction);
3. 若不成立 → 具体破坏了哪项最小条件 → **PRIMITIVE**;
4. 若仍成立, 且可由其他 primitive 派生 → **DERIVED**;
5. 若仍成立, 但属 UI/视图呈现 → **VIEW**;
6. 若仍成立, 但属优化/非第一必须 → **DEFERRED**;
7. 若该 capability 实际是 Human 语义判断 → **HUMAN** (System 不得接管)。

**"成立"定义**: Human 默认只见 Level 0 (Semantic Claim + summary), 判断 SUPPORTED/UNSUPPORTED/UNKNOWN, 不自己 group/compare/find-commonality/find-negative/find-boundary/construct-pattern。

---

## 2. Capability Deletion Matrix (逐项)

### 2.1 Aggregation (group instances by structural signature)

| 维度 | 判定 |
|---|---|
| 删除后 Workflow C 成立? | **NO** |
| 失败模式 | 无 group → compression 无输入 → Human 手动 group 21 instances → **burden transfer** |
| 可派生? | NO (grouping 是入口操作, 无上游) |
| 输入 | frozen structural features (same_y_band/co_density/region_forms/partition_id/localization) [O, from frozen P2 + EIC-1] |
| 输出 | groups (instances sharing structural signature) |
| 需新 observation? | NO (frozen P2 + EIC-1 features 足够 [EV M-B audit]) |
| 涉及语义? | NO (structural signature only) |
| Authority | 0 (结构 grouping, 无语义) |
| Semantic closure 风险? | LOW (若 signature 含语义特征则越界; 缓解: signature=structural-only frozen features) |
| ranking/scoring/decision? | NO (grouping ≠ ranking) |
| 当前状态 | MISSING |
| **判定** | **PRIMITIVE — 不可删除** |

### 2.2 Evidence Compression (produce summary + Semantic Claim Candidate)

| 维度 | 判定 |
|---|---|
| 删除后 Workflow C 成立? | **NO** |
| 失败模式 | groups 存在但 Human 须读全部成员 → **burden transfer** (= Workflow B) |
| 可派生? | NO (compression 是 Human-exposure-降低的核心, 无替代) |
| 输入 | aggregation 输出 (groups) + per-instance EIC-1 candidate [O] + per-instance provenance [O] |
| 输出 | summary (consistent/conflict/UNKNOWN/coverage counts) + Semantic Claim Candidate (aggregated EIC-1, status=candidate) |
| 需新 observation? | NO |
| 涉及语义? | NO — compression 报告**已有** EIC-1 candidate interpretation [O], 不创建新语义; "Compress evidence, not meaning" |
| Authority | 0 (compression 只改组织/计数, 不改 authority; claim status=candidate 经 EIC-1 governed) |
| Semantic closure 风险? | LOW (若 summary 措辞隐含 conclusion 则越界; 缓解: 显式 status=candidate; 措辞=计数+结构描述) |
| ranking/scoring/decision? | NO (counts ≠ ranking; candidate ≠ conclusion) |
| 当前状态 | MISSING |
| **判定** | **PRIMITIVE — 不可删除** |

### 2.3 Provenance Preservation

| 维度 | 判定 |
|---|---|
| 删除后 Workflow C 成立? | 部分不成立 (Human 无法 audit → over-trust) |
| 可派生? | N/A — **已 EXISTS** [O] (ValidationRecord.provenance + StructuralRelation.provenance + EIC-1 case_ref + layer_registry sha) |
| 需新 capability? | NO (instance-level provenance 可在 Level 4 直接复用) |
| 涉及语义? | NO |
| Authority | 0 |
| 当前状态 | EXISTS (实例级); compression 需引用 (非新能力) |
| **判定** | **EXISTS — 复用, 非 minimum-set 新成员** |

### 2.4 Conflict Preservation

| 维度 | 判定 |
|---|---|
| 删除后 Workflow C 成立? | 不成立 (silent suppression → error_risk) |
| 可派生? | YES — conflict = EIC-1 coexistence `EVIDENCE_CONFLICT` [O, tmp adapter], per-instance; compression **必须**在 summary 中计 conflict_count |
| 需独立 capability? | NO — 是 compression 的**保真约束** (fidelity requirement), 非独立能力 |
| 输出 | conflict_count in summary (非 conflict 对象) |
| Authority | 0 (count, 不仲裁) |
| **判定** | **MERGED into Compression (fidelity constraint)** — 非独立 primitive |

### 2.5 UNKNOWN Preservation

| 维度 | 判定 |
|---|---|
| 删除后 Workflow C 成立? | 不成立 (false closure → error_risk) |
| 可派生? | YES — UNKNOWN = IS-11 `INSUFFICIENT_EVIDENCE` [O, frozen harness], per-instance; compression **必须**在 summary 中计 UNKNOWN_count |
| 需独立 capability? | NO — 是 compression 的**保真约束** |
| 输出 | UNKNOWN_count in summary |
| Authority | 0 (count, 不解释) |
| **判定** | **MERGED into Compression (fidelity constraint)** — 非独立 primitive |

### 2.6 Commonality Discovery

| 维度 | 判定 |
|---|---|
| 删除后 Workflow C 成立? | **YES** (若 aggregation 存在) |
| 理由 | commonality = aggregation 的 grouping criterion 显式陈述 ("16 instances share signature X"); 不需独立 discovery |
| 可派生? | YES — commonality = "这些 instance 共享的 structural signature" = aggregation 的 key |
| 需独立 capability? | NO — aggregation 输出 group 时自然携带 signature = commonality |
| 涉及语义? | NO (structural signature) |
| **判定** | **DERIVED from Aggregation** — 非独立 primitive |

### 2.7 Negative Set Discovery

| 维度 | 判定 |
|---|---|
| 删除后 Workflow C 成立? | **YES** (若 aggregation 存在) |
| 理由 | negatives = **其他 group** (不同 structural signature 的 instance); aggregation 分组后, 非-正例 group 自然可见; System **保留** (不删除) 非-正例 group, 但不**发现/标注** negative semantic role |
| 可派生? | YES — negative = "不在正例 group 的 instance, 属于其他 group"; aggregation 输出全部 group → negative 自然显现 |
| 需独立 capability? | NO — 但 compression **必须保留**非-正例 group (保真约束) |
| 涉及语义? | **CRITICAL**: 若 System 主动判定 "这是 negative (caption/value-column)" → **Semantic Closure** [I]; 缓解: System 只 group by structural signature, 不标 semantic role; "caption"/"value-column" 是 Human 验证后 label |
| Authority | 0 (grouping only; 不标 negative semantic role) |
| **判定** | **DERIVED from Aggregation + Compression-fidelity (preserve non-positive groups)** — 非独立 primitive; System 不得做 semantic negative-discovery |

### 2.8 Structural Comparison / Structural Signature

| 维度 | 判定 |
|---|---|
| 删除后 Workflow C 成立? | **YES** (若 aggregation 存在) |
| 理由 | structural signature = aggregation 的**输入/方法** (读 frozen P2 features 作 grouping key), 非独立能力 |
| 可派生? | YES — signature = {same_y_band, co_density, region_forms, partition_id, localization} 从 frozen P2/EIC-1 读取 [O] |
| 需新 observation? | NO [EV M-B audit] |
| **判定** | **INPUT to Aggregation (from frozen evidence)** — 非独立 primitive |

### 2.9 Summarization

| 维度 | 判定 |
|---|---|
| 删除后 Workflow C 成立? | NO — = compression 删除 |
| 可派生? | summarization = compression 的**输出格式** |
| **判定** | **MERGED into Compression** — 同一能力 |

### 2.10 Coverage Construction

| 维度 | 判定 |
|---|---|
| 删除后 Workflow C 成立? | **YES** (若 compression 存在) |
| 理由 | coverage = "N examined / M in group / K excluded / L UNKNOWN" = summary 中的计数 |
| 可派生? | YES — compression summary 自然含 coverage counts |
| **判定** | **DERIVED from Compression (summary count)** — 非独立 primitive |

### 2.11 Prototype Construction

| 维度 | 判定 |
|---|---|
| 删除后 Workflow C 成立? | **YES** (default Level 0 不需 prototype) |
| 理由 | Level 0 = claim + summary (counts); Human 判断 SUPPORTED/UNSUPPORTED/UNKNOWN 不需看具体 prototype; Level 2 (on-demand) 可显示 group 内任一 instance (不需智能选择) |
| 可派生? | PARTIAL — "first instance in group" 或 "random" 可作非智能 prototype; 智能选择 = 优化 |
| 需第一必须? | NO — 默认判断不依赖 prototype |
| 风险 | 智能prototype选择 = system bias 入口 (R2) |
| **判定** | **DEFERRED** — 非第一必须; 智能选择是优化, 非 primitive |

### 2.12 Boundary Discovery

| 维度 | 判定 |
|---|---|
| 删除后 Workflow C 成立? | **YES** (default Level 0) |
| 理由 | boundary = aggregation 的 grouping criteria ("signature X" 定义了 in/out); edge-case 选择 = 优化 |
| 可派生? | YES — grouping criteria = hard boundary; "co-structure≥3" → boundary=3 |
| 需第一必须? | NO — L5.2 已标 deferrable |
| 风险 | 智能 boundary-edge 选择 = system bias |
| **判定** | **DEFERRED** — grouping criteria = boundary; edge-case = 优化, 非 primitive |

### 2.13 Semantic Claim Candidate Construction

| 维度 | 判定 |
|---|---|
| 删除后 Workflow C 成立? | **NO** (无 claim → Human 验证什么?) |
| 可派生? | YES — claim = aggregation(group) + compression(count EIC-1 candidates in group) + 模板陈述 ("N instances with signature X have EIC-1 candidate Y"); **semantic content (Y) 来自已有 EIC-1 governed mapping** [O], 非新语义 |
| 需独立 capability? | NO — 是 compression 的**输出** (aggregated EIC-1 candidates, status=candidate) |
| 涉及语义? | **CRITICAL**: claim 含 semantic interpretation (Y); 但 Y 来自 EIC-1 (existing governed contract, status=candidate [O]), 非 compression 创建; compression 只**聚合报告** per-instance EIC-1 candidates → "Compress evidence, not meaning" |
| Authority | 0 (compression 报告 candidate, 不升 conclusion; Human ACCEPT 前无 authority) |
| Semantic closure 风险? | LOW (若 compression 创建新 Y → 越界; 缓解: Y 只来自 EIC-1 governed mapping, compression 不创建新 interpretation) |
| **判定** | **OUTPUT of Compression (aggregated existing EIC-1 candidates)** — 非独立 primitive; 依赖 EIC-1 governed mapping EXISTS |

### 2.14 Progressive Disclosure

| 维度 | 判定 |
|---|---|
| 需独立 System capability? | NO — 是 **UI/视图层** (Level 0-4 presentation); 数据来自 aggregation + compression + existing provenance |
| **判定** | **VIEW (UI), 非 System abstraction primitive** |

---

## 3. Minimum System Capability Set

```
Minimum System Capability Set = { Aggregation, Evidence Compression }
```

### 3.1 Aggregation (PRIMITIVE)

- **为什么不可删除**: 删除 → 无 group → compression 无输入 → Human 手动 group → burden transfer; Workflow C 崩;
- **删除失败模式**: Human 比较 21 instances, 自己找共同 signature, 自己 group → 8/10 abstraction 子任务回到 Human [I];
- **可派生?**: NO — grouping 是入口操作, 无上游 primitive;
- **已有代码支持?**: NO (grep 0 [O]); 但**输入已存在** (frozen P2 structural features + EIC-1 structural context [O, EV]);
- **当前**: MISSING;
- **实现前置**: 无新 observation (frozen features 足够 [EV]); 需 aggregation 层 (读 frozen features → group by signature);
- **Authority=0 保证**: signature = structural-only frozen features (same_y_band/co_density/region_forms/partition_id/localization); 不含 semantic labels; grouping ≠ ranking/selection/decision; 显式断言 forbidden fields (is_table/is_cell/...)。

### 3.2 Evidence Compression (PRIMITIVE)

- **为什么不可删除**: 删除 → groups 存在但 Human 读全部 → burden transfer (= Workflow B); Workflow C 崩;
- **删除失败模式**: Human 逐 instance 阅读 EIC-1 candidate + provenance → exposure=N → fatigue [I];
- **可派生?**: NO — compression 是 Human-exposure-降低的核心, 无替代;
- **已有代码支持?**: NO (grep 0 [O]); 但**输入已存在** (aggregation 输出 + per-instance EIC-1 candidate [O] + per-instance provenance [O] + per-instance INSUFFICIENT_EVIDENCE [O]);
- **当前**: MISSING;
- **实现前置**: aggregation (上游); EIC-1 governed mapping (EXISTS); 无新 observation;
- **Authority=0 保证**:
  - compression 报告**已有** EIC-1 candidate interpretation (status=candidate [O]), 不创建新语义;
  - summary = counts (consistent/conflict/UNKNOWN/coverage), 非 ranking/scoring;
  - Semantic Claim Candidate = aggregated per-instance EIC-1 candidates (模板陈述), 非 new interpretation;
  - 显式 status=candidate; Human ACCEPT 前无 authority;
  - "Compress evidence, not meaning" — 压缩证据 (counts + existing candidates), 不压缩/创建 meaning。

### 3.3 Compression Fidelity Constraints (非独立能力, 是 Compression 的硬约束)

| 约束 | 来源 | 为什么是约束而非能力 |
|---|---|---|
| conflict_count preserved | EIC-1 coexistence EVIDENCE_CONFLICT [O] | compression **必须**计 conflict_count (否则 silent suppression); 是保真要求, 非独立 conflict-capability |
| UNKNOWN_count preserved | IS-11 INSUFFICIENT_EVIDENCE [O] | compression **必须**计 UNKNOWN_count (否则 false closure); 是保真要求 |
| coverage_count preserved | aggregation group membership | compression **必须**含 N/M/K/L 计数 (否则 over-trust); 是保真要求 |
| provenance traceable | EXISTS [O] (instance-level) | compression **必须**引用 instance-level provenance (Level 4 可展开); 是保真要求, 非新 provenance-capability |
| non-positive groups preserved | aggregation output | compression **必须**保留非-正例 group (否则 negative 丢失 → overgeneralization); 是保真要求 |
| claim status=candidate | EIC-1 governed [O] | compression 输出**必须**标 candidate (否则 Semantic Closure); 是 authority 约束 |

---

## 4. Derived / Deferred / Merged / View / Human Capability Set

### 4.1 DERIVED (从 Aggregation 派生)
| Capability | 派生自 | 机制 |
|---|---|---|
| Commonality | Aggregation | grouping criterion 显式陈述 = commonality |
| Negative Set | Aggregation | 其他 group (不同 signature); System 保留不删除, 不标 semantic role |
| Structural Signature | Aggregation input | frozen P2/EIC-1 features 作 grouping key |
| Structural Comparison | Aggregation mechanism | 读 frozen pairwise + 检查 signature match |

### 4.2 MERGED into Compression (保真约束, 非独立能力)
| Capability | 合并入 | 机制 |
|---|---|---|
| Summarization | Compression | = compression 输出格式 |
| Conflict Preservation | Compression fidelity | conflict_count in summary |
| UNKNOWN Preservation | Compression fidelity | UNKNOWN_count in summary |
| Coverage | Compression fidelity | N/M/K/L counts in summary |
| Semantic Claim Candidate | Compression output | aggregated EIC-1 candidates (模板) |

### 4.3 DEFERRED (非第一必须, 优化)
| Capability | 理由 | 风险 |
|---|---|---|
| Prototype Construction | Level 0 default 不需; Level 2 on-demand 可用 "first/random" | 智能选择 = system bias (R2) |
| Boundary Discovery | grouping criteria = hard boundary; edge-case = 优化 | 智能 edge 选择 = bias |

### 4.4 VIEW (UI, 非 System abstraction)
| Capability | 理由 |
|---|---|
| Progressive Disclosure | Level 0-4 presentation; 数据来自 aggregation+compression+provenance |

### 4.5 EXISTS (复用, 非新)
| Capability | 状态 |
|---|---|
| Provenance | EXISTS (instance-level, Level 4 复用) |
| EIC-1 Governed Mapping | EXISTS (interpretation_status=candidate [O]) |
| IS-11 INSUFFICIENT_EVIDENCE | EXISTS (frozen harness [O]) |
| EIC-1 EVIDENCE_CONFLICT | EXISTS (tmp adapter, coexistence no-winner [O]) |

### 4.6 HUMAN (System 不得接管)
| Capability | 理由 |
|---|---|
| Semantic Interpretation | 语义 authority = Human; System 只产 Candidate (经 EIC-1 governed) |
| Semantic Claim Validation | Human 判断 SUPPORTED/UNSUPPORTED/UNKNOWN |
| Negative Semantic Role Labeling | "这是 caption/value-column" = Human 验证后 label; System 做 = Semantic Closure |
| Boundary Adequacy Judgment | Human on-demand 确认 |
| Final Authorization | Human ACCEPT 前 claim 无 authority |
| Capability Registration | Human Controlled (FROZEN_CAPABILITY_TABLE [O]) |

---

## 5. Minimality Proof (反证)

### 定理: Minimum Set = {Aggregation, Evidence Compression}

**证明 (删除任一 → Workflow C 崩)**:

**删 Aggregation**:
- 无 group → compression 无输入 → 21 instances 未分组;
- Human 须手动比较 21 instances, 找共同 structural signature, 自己 group;
- = 8/10 abstraction 子任务回到 Human (commonality/prototype/boundary/negative/UNKNOWN/scope/provenance/construction) [I];
- = burden transfer; Workflow C 退化为 Workflow B (或更差);
- **Workflow C 不成立。■**

**删 Evidence Compression**:
- groups 存在 (aggregation 输出), 但无 summary/claim;
- Human 须逐 instance 阅读 EIC-1 candidate + provenance → exposure=N (21);
- = burden transfer (= Workflow A within group); fatigue [I];
- Semantic Claim Candidate 无输出 → Human 验证什么? → 退化为 Human 自己从 instances 构造 claim;
- **Workflow C 不成立。■**

**两者皆在**:
- Aggregation groups → Compression summarizes → Human sees Level 0 (claim + counts) → judges;
- Human 不 group (System did), 不 compare (System did), 不 find commonality (in summary), 不 find negative (other groups visible), 不 find UNKNOWN (count in summary), 不 find conflict (count in summary), 不 construct prototype (not needed at L0), 不 find boundary (criteria stated);
- Human validates Semantic Claim → SUPPORTED/UNSUPPORTED/UNKNOWN;
- **Workflow C 成立, 无 burden transfer。■**

**最小性**: 2 个 primitive, 不可再删 (删任一 → 崩); 不可合并 (不同输入/输出/操作); 不可派生彼此 (aggregation=grouping, compression=summarizing, 独立变换)。

### L5.2 → L5.3 压缩

| | L5.2 minimum | L5.3 minimum |
|---|---|---|
| aggregation | ✓ primitive | ✓ primitive |
| compression | ✓ primitive | ✓ primitive |
| provenance | ✓ (独立列) | EXISTS (复用, 非新) |
| conflict-preserved | ✓ (独立列) | MERGED (compression fidelity) |
| UNKNOWN-preserved | ✓ (独立列) | MERGED (compression fidelity) |
| commonality | ✓ (独立列) | DERIVED (from aggregation) |
| negative | ✓ (独立列) | DERIVED (from aggregation) |
| **合计** | **7 项** | **2 primitive + 6 fidelity constraints** |

L5.3 通过 deletion test 将 7 项压缩为 **2 真正 primitive**, 其余为派生/合并/复用/约束。

---

## 6. System vs Human Abstraction Boundary

```
System (authority=0):
  Aggregation          — group by structural signature (frozen features)
  Evidence Compression — summarize counts + report existing EIC-1 candidates (status=candidate)
    ↓ fidelity constraints: conflict_count / UNKNOWN_count / coverage / provenance-ref / non-positive-groups / claim=candidate
  [输出: groups + summary + Semantic Claim Candidate]

Human (sole semantic authority):
  Semantic Interpretation    — "this structural config means cell-context"
  Semantic Claim Validation  — SUPPORTED / UNSUPPORTED / UNKNOWN
  Boundary Adequacy (on-demand) — "is this boundary sufficient?"
  Final Authorization        — ACCEPT (claim → validated knowledge)
  Negative Semantic Role     — "this group is caption (not table)"
  Capability Registration   — Human Controlled
```

**边界不变**: System = Structural Abstraction (L1/L2, authority=0); Human = Semantic Abstraction (L3, sole authority)。Minimum set 不越界。

---

## 7. Authority / Semantic Closure Risk Review

| Minimum Primitive | Authority | Closure 风险 | 缓解 |
|---|---|---|---|
| Aggregation | 0 | LOW (signature=structural frozen features; 若含语义→越界) | signature=structural-only; forbidden-field assertions |
| Evidence Compression | 0 | LOW (若创建新 interpretation→越界; 若 summary 隐含 conclusion→越界) | 报告**已有** EIC-1 candidate (不创建新); 显式 status=candidate; summary=counts+结构描述 |

**极端 B 检查 (System 太强)** [I]:
- System 形成 semantic pattern? → NO (只 group by structural signature);
- System 判 negative semantic role? → NO (只保留其他 group, 不标 "caption");
- System 自动 boundary? → NO (grouping criteria = boundary, 非 semantic boundary);
- System 自动 prototype? → DEFERRED (不智能选择);
- System 输出 semantic conclusion? → NO (输出 Candidate, status=candidate);
- **无 Semantic Closure。** ✓

**残余风险 [H]**: structural signature 本身可能隐含语义假设 (R4, L5.2); compression 措辞可能暗示 conclusion (R5); 需 audit (未来)。

---

## 8. Workflow C Burden-Transfer Check

### 极端 A (System 太弱) 检查 [I]
若 Minimum={Aggregation, Compression} 皆实现:
- Human 仍需找共同结构? → NO (aggregation 已 group, signature 在 summary);
- Human 仍需比较实例? → NO (aggregation 已比较);
- Human 仍需构造 prototype? → NO (default L0 不需; on-demand 可用 first/random);
- Human 仍需找 negative? → NO (其他 group 在 summary 可见);
- Human 仍需找 boundary? → NO (grouping criteria = boundary statement);
- Human 仍需判断 UNKNOWN? → NO (UNKNOWN_count 在 summary);
- Human 仍需重建 provenance? → NO (Level 4 可展开 existing provenance);
- **无 burden transfer。** ✓

### 极端 B (System 太强) 检查 [I]
- 见 §7: 无 Semantic Closure。✓

### 结论 [D]
Minimum={Aggregation, Compression} 在两个极端间正确定位: System 足够强 (消除 burden transfer) 但不过强 (无 semantic closure)。

---

## 9. Implementation Prerequisite List (DESIGN, 非授权)

| 前置 | 状态 | 说明 |
|---|---|---|
| Aggregation 输入 (frozen structural features) | EXISTS [O, EV] | same_y_band/co_density/region_forms/partition_id/localization from frozen P2 + EIC-1 |
| EIC-1 governed mapping (candidate interpretation) | EXISTS [O] | interpretation_status=candidate; 不创建新语义 |
| Per-instance provenance | EXISTS [O] | case_ref + frozen_p2 source + layer_registry sha |
| IS-11 INSUFFICIENT_EVIDENCE (UNKNOWN) | EXISTS [O] | frozen harness |
| EIC-1 EVIDENCE_CONFLICT | EXISTS [O] | tmp adapter coexistence (no winner) |
| Aggregation 层 (group by signature) | **MISSING** | 需新抽象层 (读 frozen → group); 非新 observation |
| Compression 层 (summarize + claim candidate) | **MISSING** | 需新抽象层 (读 groups+EIC-1 → summary+claim); 非新 observation |
| 新 Observation Measurement | **NONE** | frozen observation 足以表达全部 primitive 输入 [EV M-B audit] |

**NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE** — 2 个 primitive 的输入全部来自已有 frozen evidence; 缺口在抽象层 (aggregation + compression), 非测量层。

---

## 10. 21-Case Simulation (Minimum Set 验证)

```
Raw: 21 instances (135/130/457/467/483/505/514/313/462/414/422/519/262/005/024/034/074/346/350/522/530)

[Aggregation] group by structural signature:
  G1: {co-structure≥3, same_y_band, different_partition, localization≤150} → 16 cases
  G2: {caption band, density=0} → 2 cases
  G3: {partition-unresolvable (lag=0/1)} → 2 cases
  G4: {margin/prose signature} → 3 cases (519 + non-direct)

[Evidence Compression] per group:
  G1: summary="16 consistent, 0 conflict, 0 UNKNOWN; signature=co-structure≥3/same_y_band/diff-partition"
      claim="16 instances support different-cell interpretation (candidate)" [EIC-1 candidate aggregated]
  G2: summary="2 instances, density=0 (safety), 0 conflict, 0 UNKNOWN"
      claim="2 caption-band instances do not support cell interpretation (candidate)"
  G3: summary="2 instances, partition-unresolvable, UNKNOWN"
      claim="2 instances have insufficient evidence (UNKNOWN)"
  G4: summary="3 instances, margin/prose signature"
      claim="3 instances are non-positive (structural negative group)"

[Human Level 0]:
  G1 claim → SUPPORTED (GT-consistent: 16/16 KEEP_SEPARATE [O])
  G2 claim → SUPPORTED (GT: 414/422 MERGE=safety ABSTAIN [O])
  G3 claim → UNKNOWN (GT: 313/462 honest ABSTAIN [O])
  G4 claim → SUPPORTED (negative group confirmed)

Human burden: 4 judgments (not 21); default exposure: 4 claims + summaries (not 21 instances);
  0 grouping, 0 comparison, 0 commonality-finding, 0 negative-finding, 0 boundary-finding, 0 prototype-construction.
```

**验证 [D, based on O cases]**: Minimum={Aggregation, Compression} 足以支撑 21-case Workflow C; Human burden = 4 judgments vs 21; 无 abstraction work 转嫁。**但: GT-confirmed positive=1, pattern 泛化未验证 [O]; 此为设计模拟, 非实验。**

---

## 11. 最终判断

### 核心结论 [D]
Workflow C 真正不可缺少的 System 能力 = **2 个 primitive**: Aggregation + Evidence Compression。L5.2 的 7 项 minimum 中, 5 项为派生/合并/复用 (非独立 primitive)。Minimum set 足够强 (消除 burden transfer) 且不过强 (无 semantic closure), 输入全部来自已有 frozen evidence (无新 observation)。

### 成功标准达成
> "Workflow C 到底需要多强的 System, 才能让 Human 只做 Semantic Validation, 而不是被迫承担 Evidence Abstraction?"

**答案**: 需要 2 个 structural-authority-0 primitive (Aggregation + Compression), 输入来自 frozen evidence, 输出 = groups + summary + Semantic Claim Candidate (status=candidate)。Human 只做 Semantic Validation。不实现 Pattern Engine; 不需要 8 个模块; 不需要新 observation。

---

## 12. Gate

```text
==================================================
L5.3 MINIMUM SYSTEM ABSTRACTION BOUNDARY REVIEW
==================================================
STATUS: DESIGN-ONLY / READ-ONLY (no implementation, no experiment)

L5.3 STATUS = CONDITIONAL PASS
  (minimality proven: 2 primitives sufficient; 5 L5.2 items compressed to derived/merged/reused;
   deletion test: removing any primitive breaks Workflow C; no semantic closure; no new observation)

MINIMUM_SYSTEM_CAPABILITY_SET = { Aggregation, Evidence Compression }
  Aggregation: group by structural signature (frozen features); authority=0; MISSING
  Evidence Compression: summarize counts + report existing EIC-1 candidates (status=candidate); authority=0; MISSING
  + 6 Compression Fidelity Constraints (conflict_count/UNKNOWN_count/coverage/provenance-ref/non-positive-groups/claim=candidate)

DERIVED_FROM_AGGREGATION = { Commonality, Negative Set (preserve only), Structural Signature, Structural Comparison }
MERGED_INTO_COMPRESSION = { Summarization, Conflict Preservation, UNKNOWN Preservation, Coverage, Semantic Claim Candidate }
DEFERRED = { Prototype Construction, Boundary Discovery }
VIEW = { Progressive Disclosure (UI) }
EXISTS_REUSED = { Provenance, EIC-1 Governed Mapping, IS-11 INSUFFICIENT_EVIDENCE, EIC-1 EVIDENCE_CONFLICT }
HUMAN_ONLY = { Semantic Interpretation, Semantic Claim Validation, Negative Semantic Role, Boundary Adequacy, Final Authorization, Capability Registration }

NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE
  (2 primitives' inputs all from frozen evidence [EV M-B audit]; gap=abstraction layer, not measurement)

IMPLEMENTATION_AUTHORIZATION = NOT AUTHORIZED
EXPERIMENT_AUTHORIZATION = NOT AUTHORIZED
FROZEN_BASELINE = INTACT
STOP = TRUE
==================================================
```

## 附: L5.3 设计原则

1. **Minimum = 2 primitive** (Aggregation + Compression); 不建 Pattern Engine; 不需 8 模块;
2. **Compress evidence, not meaning** — compression 报告已有 EIC-1 candidate, 不创建新语义;
3. **Aggregation authority=0** — structural signature only (frozen features), 无 ranking/selection/decision;
4. **Compression authority=0** — counts + candidate report, 无 conclusion;
5. **6 fidelity constraints** 是 compression 硬约束 (非独立能力): conflict/UNKNOWN/coverage/provenance/non-positive/candidate-status;
6. **Negative = preserve other groups** (非 System semantic discovery; System 标 negative semantic role = Semantic Closure);
7. **Commonality = aggregation criterion stated** (非独立 discovery);
8. **Prototype/Boundary DEFERRED** (优化, 非 primitive; grouping criteria = boundary);
9. **Provenance/EIC-1/UNKNOWN/CONFLICT EXISTS** (复用, 非新);
10. **Human** = semantic interpretation + validation + authorization + negative-role + registration (sole authority);
11. **无新 observation** (frozen evidence 足够 [EV]);
12. **Minimality proven**: 删任一 primitive → Workflow C 崩 (burden transfer); 2 primitive 不可合并/派生彼此。
