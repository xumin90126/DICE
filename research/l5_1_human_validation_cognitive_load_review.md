# L5.1 Human Validation Cognitive Load Review

> DESIGN-ONLY / READ-ONLY。不实施, 不实验, 不修改任何 frozen artifact / schema / code。
> RQ-L5.1: DICE 是否能通过 Evidence Aggregation + Evidence Compression 降低 Human Validation
> 的长期认知负担, 同时避免把 abstraction work 从 System 转嫁给 Human?

标注: [O] observed · [I] inferred · [H] hypothesis · [D] design · [EV] experimentally verified

---

## 0. 核心设计原则 (本阶段固定)

> **Human should validate, not reconstruct.**
> Human 应该负责验证语义, 而不是负责重建 Pattern。

> **DICE Pattern should compress evidence for humans, not transfer abstraction work to humans.**
> DICE 的 Pattern 应该为 Human 压缩证据, 而不是把抽象工作转嫁给 Human。

任何要求 Human 自己寻找共同点 / 比较大量实例 / 建立 Negative Set / 发现 Boundary / 判断实例归属
/ 构建 Scope / 重建 Pattern / 寻找冲突的设计 = 潜在 **Human Abstraction Burden**, 不得默认为合理。

---

## 1. 三种 Workflow 定义

### Workflow A — Instance Validation [D]
```
Observation 1 → Human 判断
Observation 2 → Human 判断
...
Observation N → Human 判断
```
单次简单, 重复高。= 当前 DICE 架构现状 (ValidationTask per-instance, review_interface 逐案) [O]。

### Workflow B — Naive Pattern Validation [D]
```
Many Instances → Pattern Candidate →
Human 阅读: Prototype + Boundary + Negative + UNKNOWN + Provenance + Scope + Boundary →
Human 自己理解 Pattern → Human Validation
```
减少 click/review count, 但单次 Cognitive Load 高。Human 承担 abstraction。

### Workflow C — Minimal Semantic Validation [D]
```
Many Observations → System Aggregation → System Structural Comparison →
System Evidence Compression → Pattern Candidate → Minimal Semantic Claim →
Human 只回答一个核心语义问题 → SUPPORTED / UNSUPPORTED / UNKNOWN
```
System 负责全部 abstraction; Human 只做 semantic authorization。

---

## 2. System vs Human 职责划分 (Workflow C 理想态)

| 任务 | Workflow A | Workflow B | Workflow C (理想) |
|---|---|---|---|
| aggregation | — | HUMAN (隐含) | **SYSTEM** |
| clustering / structural comparison | — | HUMAN | **SYSTEM** |
| provenance | SYSTEM | HUMAN 阅读 | **SYSTEM** |
| evidence summarization | — | HUMAN | **SYSTEM** |
| evidence compression | — | HUMAN | **SYSTEM** |
| candidate construction | — | HUMAN | **SYSTEM** |
| contradiction detection | — | HUMAN | **SYSTEM** |
| representative coverage | — | HUMAN | **SYSTEM** |
| boundary discovery | — | HUMAN | **SYSTEM** |
| negative discovery | — | HUMAN | **SYSTEM** |
| UNKNOWN discovery | — | HUMAN | **SYSTEM** |
| semantic interpretation | HUMAN | HUMAN | **HUMAN** |
| boundary adequacy confirmation | — | HUMAN | HUMAN (on-demand) |
| final authorization | HUMAN | HUMAN | **HUMAN** |

**关键**: Workflow C 把 abstraction 全部移到 System, Human 只剩 semantic judgment + final authorization。但这要求 System 具备 aggregation/compression 能力 — **当前架构不存在** (L5 review grep 0) [O]。

---

## 3. Human Cognitive Load Model (10 维)

| # | 维度 | 定义 | 为什么需要 | 可观测? | 当前状态 |
|---|---|---|---|---|---|
| C1 | review_count | Human 最终判断次数 | 直接影响 throughput | YES (可计) | 设计变量 |
| C2 | evidence_exposure | 默认阅读实例数 | 决定单次信息量 | YES (可计) | 设计变量 |
| C3 | evidence_switching | 实例间来回切换 | context switch cost | YES (可计 UI 事件) | 设计变量 |
| C4 | cross_instance_comparison | 自己比较多个实例 | abstraction 的核心成本 | PARTIAL (难直接测) | 设计变量 |
| C5 | abstraction_burden | 自己发现 commonality/boundary/negative/scope | 最重认知成本 | NO (需主观量表) | 设计变量 |
| C6 | decision_complexity | 一次判断考虑维度数 | 复杂判断易出错 | PARTIAL | 设计变量 |
| C7 | memory_load | 记住前例与后例比较 | working memory 有限 | NO (需 NASA-TLX 类) | 设计变量 |
| C8 | interaction_cost | clicks/expand/scroll/search/provenance-open | 物理操作成本 | YES (可计) | 设计变量 |
| C9 | error_risk | false approval/rejection/boundary-miss/negative-miss/overgeneralization | 认知负担的下游后果 | YES (对 held-out GT) | 未来实验 |
| C10 | fatigue | 长期吞吐量/质量下降 | 可持续性核心 | PARTIAL (duration 趋势) | 未来实验 |

**可观测**: C1/C2/C3/C8/C9 (客观可计); **半观测**: C4/C6/C10; **仅设计变量**: C5/C7 (需主观量表, 未来 human subject experiment)。

---

## 4. HVC 概念成本表达式 (非生产, 仅研究讨论)

```
HVC = α·review_count + β·evidence_exposure + γ·cross_instance_comparison
    + δ·abstraction_burden + ε·interaction_cost + ζ·decision_complexity
    + η·error_risk + θ·fatigue
```

- **不赋真实权重** (无 human subject data);
- **变量已定义** (§3);
- **可观测变量**: α(review_count) / β(evidence_exposure) / ε(interaction_cost) / η(error_risk) — 未来可实测;
- **设计变量**: δ(abstraction_burden) / γ(cross_instance_comparison) / ζ(decision_complexity) / θ(fatigue) — 需主观量表或 proxy;
- **未来验证**: A/B/C workflow 对比实验, 测 duration + error + NASA-TLX, 拟合 HVC。

**不伪造数值。**

---

## 5. Read-only Simulation (21 已有案例)

### 案例角色分布 [O, from phase3.2 results]

| 角色 | 案例 | 数量 | GT | off→on |
|---|---|---|---|---|
| positive target (FP fix) | AMB-135 | 1 | KEEP_SEPARATE | MERGE→KEEP_SEPARATE |
| direct recovered | 130/457/467/483/505/514 | 6 | KEEP_SEPARATE | INSUF→KEEP_SEPARATE |
| honest ABSTAIN | 313/462 | 2 | KEEP_SEPARATE | INSUF→INSUF (GT-consistent) |
| caption canary | 414/422 | 2 | MERGE | INSUF→INSUF (safety) |
| prose contamination | 519 | 1 | KEEP_SEPARATE | INSUF→INSUF |
| amb262 recovery | 262 | 1 | KEEP_SEPARATE | INSUF→KEEP_SEPARATE |
| controls correct | 005/024/034/074/346/350/522/530 | 8 | KEEP_SEPARATE | KEEP→KEEP |
| **合计** | | **21** | | |

### 5A. Workflow A (Instance) 模拟 [D, based on O cases]

- **阅读**: 每案 1 candidate (text + bbox + system reason);
- **判断**: ACCEPT/REJECT/NEED_REVIEW per instance;
- **次数**: 21;
- **evidence_exposure**: 21 (逐案);
- **cross_instance_comparison**: 0 (设计上独立) — 但 Human 若追求一致性会隐式比较 → 隐性 memory_load [I];
- **abstraction_burden**: 0;
- **推算 (概念, 非实测)**: 21 × ~5-15 sec = ~105-315 sec; 但一致性隐式比较增加隐性成本;
- **@10000**: 10000 × 5-15 sec = ~14-42 hr 纯判断; fatigue 必然; throughput 下降 [I]。

### 5B. Workflow B (Naive Pattern) 模拟 [D]

- System (隐含 Human) 需从 21 案形成 ~3-4 patterns:
  - P1: cell-context-different-cell (135 + 6 direct + 262 + 8 controls = 16 案)
  - P2: caption-safety-ABSTAIN (414/422)
  - P3: prose/value-column-ABSTAIN (519/034/074)
  - P4: structural-UNKNOWN (313/462)
- **每 pattern Human 阅读**: ~1 prototype + ~3-5 boundary + ~3-4 negative + ~2 UNKNOWN + provenance + scope ≈ **10-15 items**;
- **次数**: ~3-4 patterns;
- **evidence_exposure**: 3-4 × 10-15 ≈ **30-60 items** (高于 A 的 21!);
- **cross_instance_comparison**: HIGH — 必须比较 representative 才能理解 pattern;
- **abstraction_burden**: HIGH — 必须自己形成 pattern 心理模型、判断 boundary 是否充分、negative 是否覆盖;
- **memory_load**: HIGH — 须 hold pattern 结构同时评估各组件;
- **推算 (概念)**: 3-4 × ~3-8 min = ~9-32 min; 单次复杂度高;
- **@10000 → ~100-400 patterns**: pattern fatigue; 每次需 semantic reconstruction [I];
- **关键发现 [I]**: B 的 evidence_exposure (30-60) **可能高于** A (21) — validation count 下降但单次信息量上升; **这是 burden transfer 的直接证据**。

### 5C. Workflow C (Minimal Semantic) 模拟 [D]

- System 聚合 21 案 → ~3-4 semantic claims:
  - SC1: "16 个具有一致 co-structure 的 observation pair 支持不同-cell 解释" (summary: 16 consistent / 0 conflict / 0 UNKNOWN in this cluster)
  - SC2: "2 个 caption-band observation 不支持 cell 解释 (safety)" (summary: 2 / density=0)
  - SC3: "3 个 structural-UNKNOWN observation 证据不足" (summary: 3 / lag=0,1)
- **默认 Human 看到**: 1 semantic claim + summary (consistent/conflict/UNKNOWN count);
- **判断**: SUPPORTED / UNSUPPORTED / UNKNOWN (1 维);
- **次数**: ~3-4 claims;
- **evidence_exposure**: 3-4 (默认) — **远低于 A(21) 和 B(30-60)**;
- **cross_instance_comparison**: 0 (System 已做);
- **abstraction_burden**: 0 (System 已做) — **前提**: System aggregation 可信;
- **memory_load**: LOW;
- **on-demand**: 若 Human 疑问 → 展开 representative → boundary → negative → provenance;
- **推算 (概念)**: 3-4 × ~30-90 sec = ~2-6 min default; on-demand expansion 仅在可疑时;
- **@10000 → ~100-400 claims**: 每次简单 → 可持续 [I, H];
- **关键 [I]**: C 的默认 exposure (3-4) **最低**; 但依赖 System aggregation 质量 — 这是 burden transfer 的潜在入口 (见 §7)。

### 5D. 三 Workflow 模拟对比

| 维度 | A (Instance) | B (Naive Pattern) | C (Minimal Semantic) |
|---|---|---|---|
| review_count (21案) | 21 | 3-4 | 3-4 |
| evidence_exposure | 21 | **30-60** (最高!) | **3-4** (最低) |
| cross_instance_comparison | 0 (隐性) | HIGH | 0 |
| abstraction_burden | 0 | HIGH | 0 (前提: System 可信) |
| decision_complexity | LOW | HIGH | MEDIUM |
| memory_load | LOW-MED | HIGH | LOW |
| @10000 可持续 | NO (fatigue) | NO (pattern fatigue) | **可能** (H, 未验证) |

**结论 [I]**: B 不优于 A (exposure 更高); C 在设计层面最优, 但依赖未实现的 System 能力 + 未验证的 burden-transfer 假设。

---

## 6. Human Abstraction Burden Test

逐项判断 abstraction 由谁承担:

| abstraction 子任务 | A | B | C (理想) | 判定 |
|---|---|---|---|---|
| 发现 commonality | — | HUMAN | SYSTEM | B=burden |
| 发现 prototype | — | HUMAN | SYSTEM | B=burden |
| 发现 boundary | — | HUMAN | SYSTEM | B=burden |
| 发现 negative | — | HUMAN | SYSTEM | B=burden |
| 发现 UNKNOWN | — | HUMAN | SYSTEM | B=burden |
| 定义 scope | — | HUMAN | SHARED | B=burden; C=shared |
| 理解 provenance | — | HUMAN | SYSTEM | B=burden |
| 构建 pattern | — | HUMAN | SYSTEM | B=burden |
| 判断 semantic interpretation | HUMAN | HUMAN | HUMAN | 合理 |
| boundary adequacy confirmation | — | HUMAN | HUMAN(on-demand) | 合理 |
| final authorization | HUMAN | HUMAN | HUMAN | 合理 |

**判定 [I]**:
- **Workflow B**: Human 承担 8/10 abstraction 子任务 → **不成熟设计** (abstraction burden 未消除, 仅转移);
- **Workflow C**: System 承担 8/10; Human 仅 semantic interpretation + on-demand boundary confirmation + final authorization → **符合 "validate not reconstruct"**;
- **但 C 的 System 能力不存在** (grep 0) [O] → C 目前是 design hypothesis, 非可实现。

---

## 7. Burden Transfer Red-Team (§13, 最重要)

### 反例 1: "Pattern 减少 90% count, 但每次 10× 复杂"
- **对 B**: 成立 [I]。B 的 evidence_exposure (30-60) > A (21); 单次 decision_complexity HIGH;
  validation count 下降但 total cognitive cost 可能**上升**。**= Burden Transfer, 非 Reduction**。
- **对 C**: 不成立 (设计上) [D]。C 默认 exposure (3-4) < A; decision 1 维; abstraction=0。
  **但前提**: System aggregation 可信。

### 反例 2: "System 自动形成 Pattern, 但 Human 必须验证 System 是否正确形成"
- **这是 C 的核心风险 [I]**。若 Human 必须审计 System 的 pattern formation → burden transfer 回 Human。
- **缓解 (设计)** [D]:
  - System evidence summary 必须**诚实** (显示 conflict count / UNKNOWN count / coverage gap);
  - Human 通过 summary 即可检测可疑 pattern (如 "2 conflicts" → 自然触发 drill-down);
  - 验证是 **on-demand** (Progressive Disclosure), 非 mandatory;
  - provenance 全程可访问 (Level 4) — 但不默认展示。
- **残余风险 [I]**: 若 System 静默丢弃 negative 或误计 conflict, Human 无 summary-level 信号 → 需 full audit → burden transfer。缓解: System summary 必须 auditable + provenance 完整 + 可独立重算。
- **结论**: C 的 burden transfer 风险 **可被设计缓解但未实验验证** [H]。

### 明确记录
```
Workflow B = BURDEN TRANSFER (count↓, per-validation load↑, total may↑)
Workflow C = BURDEN REDUCTION (by design) IF System aggregation trustworthy + honest summary + on-demand audit
             residual risk: silent evidence suppression → mitigated by auditable summary + provenance
             STATUS: design hypothesis, NOT experimentally verified
```

---

## 8. Progressive Disclosure 设计 (DESIGN-ONLY)

### Level 0 — Minimal Claim (默认)
```
语义解释: [一句话 semantic claim]
系统证据摘要: N consistent / M conflict / K UNKNOWN
核心问题: 该证据是否支持这一解释?
[支持] [不支持] [证据不足]
```

### Level 1 — Evidence Summary (on-demand)
```
实例数量 / 结构一致性 / 冲突数量 / UNKNOWN 数量 / 证据覆盖范围
```

### Level 2 — Representative Evidence (on-demand)
```
System 选定的代表性实例 (prototype + boundary-edge)
```

### Level 3 — Boundary / Negative / UNKNOWN (on-demand)
```
System 发现的 boundary conditions / negative set / UNKNOWN cases
```

### Level 4 — Full Provenance (on-demand)
```
完整来源链: L2→LSP→RSC→EIC-1→instance
```

### 分析 [I]
- **默认 cognitive load**: Level 0 = 1 claim + summary → 极低;
- **降低负担**: YES (设计上) — Human 默认只见最小信息;
- **风险**: "系统隐藏重要证据" — 若 summary 不诚实 (漏 conflict/negative) → Human 误判;
- **缓解原则**: **Evidence visibility ≠ Evidence authority**
  - 不默认展示 ≠ 不存在;
  - 所有 Level 1-4 必须**可访问** (Human 主动展开);
  - summary 必须**诚实** (conflict/UNKNOWN count 不得隐瞒);
  - provenance 必须**完整可审计** (Level 4 always reachable);
- **残余风险**: Human 若从不展开 → 依赖 summary 诚实; 这是 System 信任问题, 非设计可完全消除 → 需 audit 机制 (未来)。

---

## 9. 长期运营模型 [I, H]

| 规模 | A (Instance) | B (Naive Pattern) | C (Minimal Semantic) |
|---|---|---|---|
| 10 | 简单可忍 | 不值得抽象 (pattern 覆盖低) | 简单, 但 System overhead 可能不划算 |
| 100 | 重复疲劳开始 | pattern fatigue 开始 | 可持续; on-demand 偶发 |
| 1000 | 高疲劳, throughput 下降 | 高 abstraction fatigue | 可持续 (H); System aggregation 必须可靠 |
| 10000 | 不可持续 (I) | 不可持续 (I) | **唯一可能可持续** (H, 未验证) |

**关键 [I]**: A/B 在 1000+ 不可持续; C 是唯一设计上可能可持续的, 但全部依赖未验证的 System aggregation/compression 能力。

---

## 10. Pattern 定义重新评估 (Model 1 vs Model 2)

### Model 1: Human validates Pattern
- Pattern = 验证对象;
- Human 必须理解 pattern 全貌 → abstraction burden (Workflow B);
- 风险: burden transfer。

### Model 2: Pattern organizes evidence; Human validates semantic claim
- Pattern = evidence organization / reuse layer (infrastructure, 非验证对象);
- Human validates Semantic Claim (Pattern 派生的最小语义陈述);
- Pattern 对 Human 透明 (System 内部);
- Human 不需要理解 pattern 结构, 只需判断 semantic claim 是否被证据支持。

### 反证尝试 [I]
- **反证 1**: "Human 不理解 pattern 则无法判断 claim" → 反驳: Human 判断的是 *claim 与 evidence summary 的关系*, 非 pattern 内部结构; summary (consistent/conflict/UNKNOWN) 已足够支撑判断; 若不足 → on-demand 展开;
- **反证 2**: "Pattern 若错则 claim 必错, Human 无法发现" → 反驳: summary 诚实时 conflict/UNKNOWN count 是信号; provenance 可审计; 但残余风险存在 (silent suppression) → 需 audit 机制;
- **反证 3**: "Semantic claim 太小, 无法覆盖 pattern 的边界" → 反驳: claim 可携带 scope; boundary adequacy 是 on-demand confirmation 而非 mandatory;

### 结论 [D]
**Model 2 更合理**。Pattern = evidence organization layer; Semantic Claim = validation unit。但 Model 2 依赖:
1. System aggregation/compression 能力 (不存在) [O];
2. 诚实 summary 机制 (未设计) [D];
3. on-demand audit (未实现) [D]。
**= design conclusion, 非 implementation decision。**

---

## 11. Human Validation 最小单位重新审查

比较 Instance / Pattern / Semantic Claim:

| 维度 | Instance | Pattern | Semantic Claim |
|---|---|---|---|
| 足够小? | YES | NO (太大) | YES (1 claim) |
| 可复用? | NO | YES (但复用=abstraction burden) | YES (claim 跨 instance, pattern 组织) |
| 可 falsify? | YES (对 GT) | PARTIAL (边界模糊) | YES (对 evidence summary + GT) |
| 可记录 provenance? | YES (per-instance) | PARTIAL | YES (pattern-level + instance refs) |
| 可产生 UNKNOWN? | YES (NEED_REVIEW) | PARTIAL | YES (explicit UNKNOWN) |
| 避免 semantic closure? | YES (per-instance 无 closure) | RISK (pattern 可能隐含 closure) | YES (claim 是 candidate, 非 fact) |
| 进入后续 pattern? | NO | = pattern 本身 | YES (validated claim → pattern) |
| 保持 capability registration 人控? | YES | RISK (pattern→auto-capability 诱惑) | YES (claim→candidate→human registration) |

**结论 [D]**: 最小 Human Validation Unit = **Semantic Claim**。Pattern = evidence organization / reuse layer (非验证对象)。这与 Model 2 一致。

---

## 12. Governance Boundary 检查

```
Observation → Evidence → Structural Interpretation → Semantic Interpretation Candidate
→ Human Validation (Semantic Claim) → Validated Pattern → Capability Candidate
→ Human-authored Declaration → Human Registration → Capability
```

- Pattern **无 runtime authority** (不 routing/selection/ranking/confidence/recommendation/execution);
- Semantic Claim validation **不自动** → Validated Pattern;
- Validated Pattern **不自动** → Capability Candidate;
- Capability Registration **Human Controlled** (FROZEN_CAPABILITY_TABLE 证明静态人控) [O];
- 新设计**不破坏** authority ladder — Semantic Claim 仍在 L4→L5 边界, 不越级 [D]。

---

## 13. 八个问题回答

### Q1: Pattern 是否真的降低 Human Cognitive Load?
**不自动** [I]。Naive Pattern (B) 可能**增加** per-validation load (exposure 30-60 > 21), = burden transfer。只有 Minimal Semantic Validation (C) + System compression + Progressive Disclosure 在设计上降低 load, 但**未实验验证** [H]。

### Q2: Naive Pattern Validation 是否存在明显 Human Abstraction Burden?
**YES** [I]。Human 承担 8/10 abstraction 子任务 (commonality/prototype/boundary/negative/UNKNOWN/scope/provenance/pattern-construction)。= "validate not reconstruct" 原则的违反。

### Q3: Minimal Semantic Validation 是否比 Naive Pattern 更合理?
**YES (设计层面)** [D]。System 承担 abstraction; Human 仅 semantic judgment; default exposure 最低。但依赖未实现的 System 能力 + 未验证的 burden-transfer 缓解。

### Q4: Representative/Boundary/Negative/UNKNOWN 是否应从 mandatory checklist 变成 system-managed evidence?
**YES** [D]。它们是 System 的 evidence support objects, 非 Human mandatory checklist。Human 默认见 summary; on-demand 展开。Evidence visibility ≠ Evidence authority。

### Q5: Progressive Disclosure 是否能降低默认认知负担?
**YES (设计上)** [D]。默认 Level 0 = 1 claim + summary → 极低。风险 = 隐藏重要证据 → 缓解 = 诚实 summary + 可访问 provenance + on-demand audit。残余风险 = silent suppression → 需 audit 机制 (未来)。

### Q6: Human Validation 最小单位?
**Semantic Claim** (非 Instance, 非 Pattern)。Pattern = evidence organization/reuse layer。Semantic Claim = Human 实际授权对象。

### Q7: 如何定义未来可测量的 Human Validation Cost?
可观测指标 [D]:
- review_count (判断次数);
- default_evidence_exposure (默认展示 item 数);
- interaction_cost (clicks/expands/scrolls/provenance-opens — UI 事件可计);
- decision_duration (start→submit);
- error_rate (对 held-out GT: false approval/rejection/boundary-miss);
- drill_down_rate (on-demand 展开频率 — 反映 summary 充分性);
- fatigue_trend (duration/error 随序号的退化曲线);
- NASA-TLX (主观认知负担量表 — C5/C7 proxy);
未来实验: A/B/C workflow × human subjects, 测上述指标, 拟合 HVC。**当前无 human subject data, 不伪造。**

### Q8: Pattern 是否仍值得继续研究?
**KEEP, 但 REDESIGN** [D]。
- REJECT? 否 — Pattern 作为 evidence organization/reuse layer 有价值 (Model 2);
- KEEP as-is? 否 — Naive Pattern (Model 1) = burden transfer, 不成熟;
- REDESIGN: Pattern 从 "验证对象" 重新定位为 "evidence organization layer"; validation unit = Semantic Claim; System 承担 abstraction; Progressive Disclosure; 诚实 summary + auditable provenance。
**不因之前认可 Pattern 就默认 KEEP — 本审查否定了 Model 1, 保留 Model 2 的 redesign 方向。**

---

## 14. 核心原则最终判断

> **DICE Pattern 的成功标准不是"让 Human 少看几个案例", 而是"让 Human 在更少、更简单、更明确的语义判断中获得足够的 Evidence, 同时不把 abstraction work 转嫁给 Human"。**

**成立 [D]**。记录为当前 Pattern/Human Validation 核心设计原则。

补充约束: "足够的 Evidence" = 诚实 summary + on-demand 可展开 + auditable provenance (非"默认展示全部")。abstraction work (commonality/boundary/negative/UNKNOWN/scope/provenance) 由 System 承担; Human 仅 semantic interpretation + final authorization。

---

## 15. Gate

```text
==================================================
L5.1 HUMAN VALIDATION COGNITIVE LOAD REVIEW
==================================================
STATUS: DESIGN-ONLY / READ-ONLY (no implementation, no experiment)

L5.1 STATUS = CONDITIONAL PASS
  (design analysis supports Model 2 / Workflow C direction;
   Naive Pattern B = burden transfer identified & rejected;
   Minimal Semantic C = burden reduction by design but unverified;
   System aggregation/compression capability absent in current architecture)

PATTERN_CONCEPT = KEEP + REDESIGN (Model 1→Model 2: pattern=evidence-org layer, not validation target)
HUMAN_VALIDATION_UNIT = Semantic Claim (not Instance, not Pattern)
HUMAN_ABSTRACTION_BURDEN = IDENTIFIED in Workflow B (8/10 tasks on Human); ELIMINATED by design in C (requires System capability)
PROGRESSIVE_DISCLOSURE = DESIGN PROPOSED (Level 0-4); reduces default load; residual risk=silent suppression
EVIDENCE_COMPRESSION = REQUIRED (System-side; capability absent; design only)
TOTAL_HUMAN_COST_MODEL = HVC defined (8 vars, no fake weights; observable: review_count/exposure/interaction/error; design: abstraction/memory/fatigue)
LONG_TERM_SUSTAINABILITY = C only potentially sustainable @10000 (H, unverified); A/B unsustainable @1000+
NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE (existing frozen Observation sufficient for pattern prerequisites; gap=aggregation/compression layer, not measurement)
IMPLEMENTATION_AUTHORIZATION = NOT AUTHORIZED
EXPERIMENT_AUTHORIZATION = NOT AUTHORIZED
FROZEN_BASELINE = INTACT
STOP = TRUE
==================================================
```

## 附: 设计原则记录 (本阶段固定)

1. Human should validate, not reconstruct;
2. Pattern compresses evidence for humans, not transfers abstraction to humans;
3. Validation unit = Semantic Claim; Pattern = evidence organization/reuse layer;
4. System承担 aggregation/compression/boundary/negative/UNKNOWN/provenance;
5. Human 承担 semantic interpretation + final authorization (on-demand boundary confirmation);
6. Evidence visibility ≠ Evidence authority (不默认展示 ≠ 不存在);
7. Progressive Disclosure (Level 0 default → Level 4 on-demand);
8. 诚实 summary (conflict/UNKNOWN count 不隐瞒) + auditable provenance;
9. Pattern 无 runtime authority; Capability Registration Human Controlled;
10. 成功标准 = 更少更简单的语义判断 + 足够证据 + abstraction 不转嫁。
