# L5 Human Validation Readiness Review

> DESIGN / ARCHITECTURE REVIEW ONLY。零实施、零实验、零 schema 修改、零代码修改。
> RQ: DICE 的 Human Validation 能否验证"可复用的 Interpretation Pattern / Capability
> Boundary", 而不是退化为 instance-by-instance annotation?

---

## 1. Current Architecture Inventory (只读)

### 1.1 实际对象 = 实例级 (instance-level)

| 组件 | 文件 | 验证对象 | 粒度 |
|---|---|---|---|
| StructureHypothesis (P7.1) | `structure_hypothesis.py` | hypothesis_id = hash(document\|page\|type\|source_ids) | **per-document per-page per-observation** |
| ValidationTask (P7.2) | `validation_models.py` | task_id = hash(document\|page\|observation_id) | **per-instance** |
| ValidationRecord | `validation_models.py` | verdict (ACCEPT/REJECT/NEED_REVIEW) on ONE task | **per-instance, immutable** |
| ValidatedEvidence | `validation_models.py` | derived from Observation + ACCEPT + Record | **per-instance derived** |
| FROZEN_CAPABILITY_TABLE | `assets/frozen_capabilities.py` | 22 static DICE 1.0 capabilities; L3_SKILL_ROUTES = "Human 指定的静态映射, 非自动学习" | **static human-authored, NOT derived from validation** |
| review_interface | `review_interface.py` | "CONFIRMATION interface, not free annotation"; Human sees 1 candidate → Accept/Reject/Need Review | **per-candidate confirmation** |

### 1.2 关键发现

1. **当前 Human Validation 的实际对象 = 单个 StructureHypothesis (per-document per-page)** — 实例级, 非 pattern 级;
2. **ValidationRecord 能保存**: verdict + reason + notes + timestamp + duration + reviewer_id + revision_status + supersedes + provenance — **无 pattern 字段、无 negative-set、无 boundary、无 scope**;
3. **CapabilityCandidateObservation / DocumentSpan / interpretation_pattern / reusable_pattern / pattern_validation**: **grep 全代码库 = 0 命中** — 这些概念在当前架构中**不存在**;
4. **reusable pattern 的表达能力 = 不存在** (无 schema、无对象、无流程);
5. **Human Review UI 实际要求 instance-level labeling**: review_interface 明文 "present one candidate for Human review (index/total)" — 逐案确认, 非 pattern 抽象;
6. **instance-level bias 发生位置**: ValidationTask 的 key 构造 (`document|page|observation_id`) + review_interface 的逐案呈现循环 — 结构性实例级, 非偶然;
7. **TABLE/TABLE_CELL 在 P7.1 被 BLOCKED** (`structure_config.py`: "waits for Table Cell Geometry observation") — M-B 的 cell-context interpretation candidate 在冻结 P7.1/P7.2 架构中**无对应 hypothesis type**; EIC-1 的 SCE 是 tmp/ 实验产物, 无架构归宿。

## 2. Authority Ladder (三概念严格区分)

```text
Observation (L1/L2: "存在一个数字 4", bbox/x0/y — frozen, source-backed)
    ↓
Evidence (L2/L3: pairwise same_y_band, alignment group — frozen fact)
    ↓
Structural Interpretation (L3: LSP/RSC — derived, non-semantic)
    ↓
Semantic Interpretation (L4: EIC-1 Cell Context Evidence — candidate, governed)
    ↓
Human Validation (L5: ??? — 当前 = instance verdict; 设计目标 = pattern validation)
    ↓
Capability (L6: FROZEN_CAPABILITY_TABLE — static human-authored, NOT auto-derived)
```

**原则**: Higher semantic authority requires stronger evidence + stronger validation。L4 不得自动获 L5; L5 不得自动获 L6。

## 3. 候选对象评估 (A-E, 不预设答案)

| 维度 | A Document Instance | B Evidence Instance | C Interpretation Candidate | D Interpretation Pattern | E Capability Boundary |
|---|---|---|---|---|---|
| Reusability | LOW | LOW | LOW-MEDIUM | **HIGH** | HIGHEST |
| Human burden | HIGH (scales with corpus) | HIGH | HIGH | **LOW (1 validation → many)** | LOW |
| Evidence provenance | per-instance | per-instance | per-instance + chain | **pattern-level + instance refs** | pattern + capability ref |
| Falsifiability | LOW (1 instance) | LOW | MEDIUM | **HIGH (negative set)** | HIGH |
| Negative evidence support | NONE | NONE | weak | **structured negative set** | structured |
| Boundary expressibility | NONE | NONE | weak | **explicit scope/boundary** | explicit |
| Risk of semantic overreach | LOW | LOW | MEDIUM | MEDIUM (manageable) | HIGH (premature) |
| Compatibility with current DICE | YES (current) | YES | PARTIAL (tmp only) | **NO (schema absent)** | NO |
| Cross-document reuse | NO | NO | weak | **YES (designed for)** | YES |

### 为什么其他不足

- **A/B (instance)**: 纯实例标注 = §7 反模式 1 (Human Validation → instance labeling); 无复用; human burden 随语料线性增长; 无法跨文档; 不支持 negative set/boundary — **当前架构现状, 即问题本身**;
- **C (interpretation candidate)**: 仍实例绑定 (per-pair/per-region); 验证每个 candidate = 带解释链的实例标注; 比 A/B 多了 chain 但无复用机制; EIC-1 的 SCE 是实例级产物 (`case_ref = atom_a|atom_b`);
- **E (capability boundary)**: 是 D 的下游; 无 D 无法跳到 E; capability registration 是独立人控步骤 (FROZEN_CAPABILITY_TABLE 证明); 过早抽象 = semantic overreach 风险。

**D (Interpretation Pattern) = 当前最有证据支持的候选** — 但明确是 **DESIGN CONCLUSION, 非 implementation decision**。

## 4. Pattern Validation 最小组成 (设计审查, 非 schema)

一个 Interpretation Pattern 至少需要 (分析, 不自动成 schema):

1. **Positive structural conditions**: EIC-1 preconditions (≥2 local stable LSPs + same_y_band + co-structure density≥3 + localization≤150pt) — *已存在 (Phase 3.1 冻结)*;
2. **Negative examples**: caption/code-line/TOC/value-column/page-margin — *已存在 (M-B audit + Phase 3.2 canary/prose)*;
3. **Boundary conditions**: scope = vector-table pages in frozen corpus; spatial bounds (localization); exclusion bounds (margin y_ext) — *部分已有*;
4. **Evidence provenance**: L2→LSP→RSC→EIC-1 chain — *已存在 (Phase 3.2 11/11)*;
5. **Interpretation statement**: "this structural configuration may be interpreted as cell-context candidate" — *已存在 (EIC-1, candidate status)*;
6. **Scope**: applicability domain — *需定义*;
7. **UNKNOWN/insufficient condition**: lag=0/1 partition unresolvable → ABSTAIN — *已存在 (313/462 honest ABSTAIN)*;
8. **Human decision**: ACCEPT/REJECT/UNKNOWN on the PATTERN (not instance) — *需设计*;
9. **ValidationRecord**: pattern-level (not task-level) — *需设计*;
10. **Reuse condition**: when can the pattern apply to new instances — *需定义*。

**关键**: 成分 (1/2/4/5/7) 已从 M-B 研究中获得; 成分 (3/6/8/9/10) 需设计 — 这就是 CONDITIONAL READY 的含义。

## 5. 真实案例可行性审查 (分析, 不成规则)

**问**: 一个 Human 能否验证一个 reusable pattern 覆盖多个 instance?

**分析例** (不得变成 semantic rule): "在满足 [EIC-1 preconditions 全集] + 排除 [caption/code/TOC/value-column/margin negative set] + 处于 [vector-table boundary] 内时, 该 structural configuration 可被解释为 cell-context candidate。"

- 覆盖正例: AMB-135 + 6 DIRECT recovered (130/457/467/483/505/514) + 8 controls = **15 instances, 1 pattern**;
- 负例集: AMB-414/422 (caption), AMB-519 (prose), AMB-034 (value-column) = pattern 的 negative set;
- UNKNOWN: AMB-313/462 (lag=0/1) = pattern 的 insufficient-evidence condition;
- AMB-262: 同带不同分区 → pattern 覆盖 (GT-consistent recovery)。

**可行性**: YES — 一个 pattern 可覆盖 ~15 instances; human burden = 1 validation vs 15 instance labels。**但**: GT-confirmed positive=1, positive diversity 仍不足 → pattern 的**泛化性未验证** (仅框架内)。这是分析例, 不是 rule。

## 6. 反模式审查 (§7)

| # | 风险 | 当前架构 | 判定 |
|---|------|----------|------|
| 1 | Human Validation → instance labeling | ValidationTask per-instance + review_interface 逐案 | **PRESENT** |
| 2 | Human Validation → rule authoring | review = Accept/Reject, 非 rule writing | not present |
| 3 | Human Validation → hidden if/else | validation = governance, 不入 code | not present |
| 4 | Human Validation → runtime authority | ValidatedEvidence = derived reference, 非 executable | not present |
| 5 | Human Validation → automatic capability registration | FROZEN_CAPABILITY_TABLE static, 非自动 | not present |
| 6 | Positive example only | ValidationRecord 无 negative-set 字段 | **RISK PRESENT** |
| 7 | No negative evidence | 同上 — 无 structured negative set | **RISK PRESENT** |
| 8 | No boundary | ValidationRecord 无 scope/boundary 字段 | **RISK PRESENT** |
| 9 | No UNKNOWN state | NEED_REVIEW 存在但 per-instance, 非 pattern-level UNKNOWN | PARTIALLY PRESENT |
| 10 | Validation → executable behavior | ValidatedEvidence 非 runtime | not present |

**RISK = PRESENT (4 项: 1/6/7/8)** — 记录, 不修复。

## 7. Human Burden Conceptual Model

```text
Many Instances → Repeated Evidence Pattern → One Human Validation → Reusable Pattern → Many New Instances
```

- **一次验证覆盖多 instance 当**: instances 共享同一 structural configuration (同 EIC-1 preconditions) — pattern 抽象掉 instance 差异;
- **不能当**: instances 结构不同 (caption vs table vs code) — 各需独立 pattern 或 UNKNOWN;
- **保留 UNKNOWN 当**: evidence 不足以形成 pattern (positive diversity=1 → 无法抽象);
- **不值得抽象当**: pattern 仅覆盖 1 instance (无复用收益) — GT-confirmed positive=1 意味当前多数 pattern 尚不值得抽象。

## 8. Pattern Overgeneralization 防护 (architecture-level, 非 schema)

| 机制 | 作用 | 当前状态 |
|---|---|---|
| Scope | 限定 applicability domain | 需定义 |
| Boundary | 空间/结构界 | 部分有 (localization) |
| Negative Set | 强制排除 | 成分有, 无 schema |
| Provenance | 溯源 | 已有 (EIC-1 chain) |
| Validation Context | 哪些 instance 被见/语料 | 需定义 |
| Version | pattern 版本 | 需定义 |
| Supersession | 新 pattern 取代旧 | 需定义 |
| Revalidation Trigger | 语料扩展/参数变/新负例 → 重验 | 需定义 |

## 9. Pattern Validation ≠ Capability Registration

```text
Pattern Validation → Validated Knowledge / Interpretation → Capability Candidate → Human Controlled Registration → Capability
```

- **Human Validation ≠ automatic Capability Registration**;
- FROZEN_CAPABILITY_TABLE = DICE 1.0 静态人控路由, **非** pattern validation 产物;
- 新 capability 需: pattern validated → capability candidate proposed → human registration decision → capability table entry (governed, 非自动);
- Capability Registration remains **Human Controlled**。

## 10. 论文价值评估

| # | 问题 | NOVELTY | EVIDENCE STRENGTH | CURRENT SUPPORT | MISSING EVIDENCE | OVERCLAIM RISK |
|---|------|---------|-------------------|-----------------|------------------|----------------|
| 1 | Human Validation as reusable pattern validation | HIGH | MEDIUM (ingredients exist) | PARTIAL (M-B) | no pattern schema/instance validated | MEDIUM |
| 2 | Evidence → Interpretation boundary | HIGH | HIGH (EIC-1 code-level) | STRONG (Phase 2.1/2.2) | L5 not occurred | LOW |
| 3 | No Semantic Closure | HIGH | HIGH (formalized) | STRONG | — | LOW |
| 4 | Evidence Quality + Error Containment | HIGH | HIGH (S1-S10) | STRONG (Phase 3.2) | — | LOW |
| 5 | Honest ABSTAIN | MEDIUM-HIGH | HIGH (313/462) | STRONG | — | LOW |
| 6 | Negative evidence as validation input | HIGH | MEDIUM (negatives cataloged) | PARTIAL | no pattern-level negative schema | MEDIUM |
| 7 | Research-object revision | HIGH | HIGH (PH-02→C2→LSP) | STRONG | — | LOW |
| 8 | Consumer Integration vs Observation Gap | HIGH | HIGH (M-B audit + replay) | STRONG | — | LOW |

## 11. 三个最终判断

### A. L5 DESIGN READINESS = **CONDITIONAL READY**

理由: pattern 的**成分** (positive conditions / negative set / provenance / UNKNOWN / interpretation statement) 已从 M-B 研究中获得; 但 pattern **对象/schema/抽象层/流程**在当前架构中**不存在** (grep 0 命中); ValidationTask 结构性实例级; 4 项反模式风险 PRESENT (1/6/7/8); TABLE/TABLE_CELL 在 P7.1 BLOCKED (EIC-1 candidate 无架构归宿)。需设计工作后方可进入任何 L5 validation。

### B. Human Validation 最小研究对象 = **Interpretation Pattern (Candidate D)**

当前最有证据支持 (成分已备 + 可行性分析通过 + 复用收益高 + human burden 低)。**明确 = DESIGN CONCLUSION, 非 implementation decision**。Pattern 需携带 10 项组成 (§4), 其中 5 项已有、5 项需设计。不跳到 E (capability boundary) — 过早。

### C. 是否需要新 Observation Measurement? **NO**

现有 frozen Observation (P1/P2 geometry + Atomic Observation) 足以表达全部 pattern prerequisite (M-B Expressability Audit + Phase 3.2 已证)。Gap 不在 observation, 在 pattern 抽象层 + human validation 流程。**NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE**。

## 12. Gate

```text
==================================================
L5 HUMAN VALIDATION READINESS REVIEW
==================================================
STATUS: DESIGN / ARCHITECTURE REVIEW ONLY

CURRENT_ARCHITECTURE:
  Validation object = instance-level (ValidationTask per document/page/observation)
  reusable-pattern abstraction = ABSENT (grep 0)
  FROZEN_CAPABILITY_TABLE = static human-authored (NOT auto-derived)
  TABLE/TABLE_CELL = BLOCKED in P7.1 (EIC-1 candidate has no architecture home)

AUTHORITY_LADDER: Observation → Evidence → Structural → Semantic → Human Validation → Capability
  (higher authority requires stronger evidence + stronger validation)

RECOMMENDED_OBJECT: Interpretation Pattern (Candidate D) — DESIGN CONCLUSION, not implementation
  ingredients 5/10 ready (positive conditions / negative set / provenance / UNKNOWN / interpretation)
  ingredients 5/10 need design (scope / boundary / human-decision / pattern-ValidationRecord / reuse)

ANTI_PATTERN_RISKS: 4 PRESENT (instance-labeling / no-negative-set / no-boundary / positive-only)
  (recorded, NOT fixed)

L5_DESIGN_READINESS = CONDITIONAL READY
NEW_OBSERVATION_MEASUREMENT_REQUEST = NONE
PATTERN_VALIDATION != CAPABILITY_REGISTRATION (Human Controlled)

IMPLEMENTATION = NOT AUTHORIZED
EXPERIMENT = NOT AUTHORIZED
GT = UNCHANGED    TLD = UNCHANGED    ATOMIC_OBSERVATION = UNCHANGED
IS11_DECISION = UNCHANGED    FROZEN_BASELINE = INTACT
PRODUCTION = FALSE
STOP = TRUE
==================================================
```
