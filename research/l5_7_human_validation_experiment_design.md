# L5.7 Human Validation Experiment — Design + Feasibility + Material Audit

> DESIGN ONLY. 不招募 Human, 不执行实验, 不修改 production code。
> L5 Architecture = CLOSED (L5.6)。本阶段不重新打开 L5 Architecture。

标注: [O] observed · [I] inferred · [H] hypothesis · [D] design · [EV] experimentally verified

---

## 0. 继承状态 [O]

```
L5.6 STATUS = CONDITIONAL PASS
OVER_DESIGN_RISK = LOW
CIRCULAR_REASONING = LIMITED
L5_ARCHITECTURE_STATUS = CLOSED
NEXT_STEP = HUMAN_VALIDATION_EXPERIMENT
L5.3_CLAIM = Workflow C scoped minimum (B, not universal)
L5.5_EVIDENCE_LEVEL = ENGINEERING_PROXY (3/21, not human-subject)
```

**本阶段不新增 Primitive / Contract / Pattern Object / Architecture。**

---

## 1. Research Question

> **RQ-L5.7**: Compared with Instance Validation (A) and Naive Pattern Validation (B),
> does Evidence Aggregation + Evidence Compression + Semantic Claim Validation (C)
> reduce Human cognitive burden while preserving or improving validation quality?

### 1.1 RQ 可否被最小 Human Experiment 回答? [I]

**YES, with material limitations (§3)。** RQ 需要比较 A/B/C 的 cost + quality, 最小实验结构可回答。但当前 21-case 材料存在 GT imbalance 和 automation-bias-coverage 不足 (§3), 实验范围受限。

---

## 2. Material Audit [O/EV]

### 2.1 材料清单 [O]

| 材料类 | 数量 | 来源 |
|---|---|---|
| Total cases | 21 | `mb_phase3_2_isolated_replay_results.json` (frozen) |
| Groups (L5.5) | 3 | admitted=11, region_not_formed=6, partition_unresolvable=4 |
| Positive (admitted+candidate) | 11 | IS11-AMB-034/130/135/262/346/350/457/467/483/505/514 |
| Negative (region_not_formed) | 6 | IS11-AMB-005/313/414/422/519/530 |
| UNKNOWN (partition_unresolvable) | 4 | IS11-AMB-024/074/462/522 |
| Conflict | 0 | (natural conflict coverage=0, carry-forward disclosure) |
| GT KEEP_SEPARATE | 19 | 90.5% |
| GT MERGE | 2 | 9.5% (AMB-414, AMB-422) |

### 2.2 五类必要材料检查 [O]

| 必要材料 | 存在? | 数量 | 评估 |
|---|---|---|---|
| Positive | YES | 11 | 充足 (admitted + candidate) |
| Negative | YES | 6 | 充足 (region_not_formed, density=0) |
| UNKNOWN | YES | 4 | 充足 (partition_unresolvable) |
| Boundary | PARTIAL | 2 | 有限 (MERGE cases = boundary-positive, 全在 region_not_formed group) |
| Conflict | **NO** | 0 | **缺失** (natural conflict coverage=0) |

### 2.3 GT Balance [O]

```
KEEP_SEPARATE: 19 (90.5%)
MERGE: 2 (9.5%)
```

**SEVERELY IMBALANCED。** 19:2 = 无法做 quality 统计检验 (MERGE cases 太少, false-rejection 风险只能观测 2 例)。

### 2.4 Automation Bias Material [O]

```
System candidate (different_cell_candidate) 出现: 11 cases (全 admitted)
其中 GT=KEEP_SEPARATE: 11 (100%)
其中 GT=MERGE: 0 (0%)
System candidate ≠ GT 的 case: 0
```

**AUTOMATION_BIAS_COVERAGE = LIMITED。** 所有 System candidate 与 GT 一致。无 System 误导 case。Human 无法被测试"因 System claim 而错误接受"的场景。

原因: System 只在 admitted (structural evidence 充分) 时产生 candidate, 而 admitted cases 全是 KEEP_SEPARATE (结构上确实不同); MERGE cases (结构上相同) 落入 region_not_formed (无 structural region), System 正确地不产生 candidate。

**这不是 System 的错误** — System 行为是 structurally correct 的 (不同结构 = 不同 cell candidate; 相同结构 = 无 region = no candidate)。但**实验材料不足以测试 automation bias**。

### 2.5 21 cases 是否够做 pilot? [I]

**YES, 作为 PILOT / EXPLORATORY。**

- n=21 足够做 within-subject pilot (每个 participant 做 A/B/C 三条件);
- 但不足以做 confirmatory statistical inference (GT imbalance 19:2);
- 必须标记 `PILOT / EXPLORATORY`, 不得写成 confirmatory evidence。

### 2.6 Material Limitation 汇总 [O]

| 限制 | 影响 | 是否阻塞实验? |
|---|---|---|
| GT imbalance (19:2) | Quality 统计检验不可行; MERGE false-rejection 只能观测 2 例 | NO (pilot 仍可做) |
| Conflict = 0 | 无法测试 conflict preservation 的 Human 判断质量 | NO (F5 已在 L5.5 EV; Human 不需判断 conflict) |
| Automation bias coverage = LIMITED | 无法测试"System 误导 → Human 错误接受" | **PARTIAL** (可记录为 limitation) |
| Positive 全 KEEP_SEPARATE | C 的 claim 全是 "different_cell_candidate", 全正确; 无法测试 C 的 false-acceptance | **PARTIAL** (可记录为 limitation) |
| Cross-document = NO | 全部来自同一 corpus (DICE IS-11 sampling frame) | NO (scope 限定) |

---

## 3. EXPERIMENT_MATERIAL_LIMITATION [O]

```
EXPERIMENT_MATERIAL_LIMITATION:
  1. GT imbalance: KEEP_SEPARATE=19, MERGE=2 → quality 统计不可行, pilot only
  2. Conflict coverage: 0 → conflict-preservation Human judgment 不可测
  3. Automation bias coverage: LIMITED → 0 System≠GT cases; 
     System candidate 全正确; 无法测试 Human 因 System claim 而错误接受
  4. Positive scope: 全 KEEP_SEPARATE → C false-acceptance 不可测
  5. Cross-document: NO → 泛化不可声称
  6. n=21 → pilot/exploratory only, 非 confirmatory
```

**不扩大 Pattern / 增加 Primitive / 修改系统来弥补。** 只记录 limitation 并提出最小数据补充方案 (§10)。

---

## 4. 三个 Workflow 定义 [D]

### Workflow A — Instance Validation

```
Human 看到:
  Evidence Instance (per case)
  + structural context (EIC-1 detail: sce_status, region_forms, partition info)
  + validation task: "这两个 atom 是否属于同一 semantic unit? → KEEP_SEPARATE / MERGE / UNKNOWN"

Human 对每个 instance 独立判断。
  Judgments: 21 (per case)
  Evidence exposure: 21 instances
  Abstraction burden: 0 (Human 不需 group/compare)
  Cognitive cost: 21 × (read + decide)
```

### Workflow B — Naive Pattern Validation

```
Human 看到:
  3 groups (by sce_status, pre-grouped, 无 compression)
  + 每个 group 的全部 member instances (无 summary, 无 claim)
  
Human 自己承担:
  commonality discovery (这些 instance 有什么共同结构?)
  comparison (instance 间差异?)
  prototype formation (这个 group 代表什么?)
  boundary reasoning (group 边界在哪?)
  negative identification (为什么这些不是 candidate?)
  UNKNOWN reasoning (为什么这些 partition unresolvable?)

  Judgments: 3 (per group, group-level KEEP_SEPARATE/MERGE/UNKNOWN)
  Evidence exposure: 21 instances (全部, 但 grouped)
  Abstraction burden: HIGH (Human 做 grouping + pattern understanding)
  Cognitive cost: 3 judgments + 21 instance reading + abstraction work
```

**B 的检测目标**: Validation Count 21→3, 但 abstraction burden 是否上升? (burden transfer 检测)

### Workflow C — Minimal Semantic Validation

```
Human 看到:
  3 Semantic Claim Candidates (L5.5 compressed output)
  + summary (counts: consistent/unknown/conflict/coverage)
  + grouping criteria (structural signature)
  + provenance pointer (Level 4 recoverable on demand)

Human 只负责:
  claim validation (这个 candidate 是否 SUPPORTED / UNSUPPORTED / UNKNOWN?)
  boundary adequacy (grouping criteria 是否 sufficient?)
  UNKNOWN judgment
  final semantic decision

  Judgments: 3 (per claim)
  Evidence exposure: 3 claims (default) / 21 instances (Level 4 on demand)
  Abstraction burden: 0 (System did grouping + compression)
  Cognitive cost: 3 × (read claim + validate)
```

**C 的检测目标**: Validation Count 21→3, abstraction burden=0, quality 是否保持?

### 三个概念严格区分 [D]

| 概念 | A | B | C |
|---|---|---|---|
| Validation Count | 21 | 3 | 3 |
| Evidence Exposure | 21 | 21 | 3 (default) / 21 (on demand) |
| Abstraction Burden | 0 | HIGH | 0 |
| Cognitive Cost | 21×(read+decide) | 3 judgments + abstraction | 3×(read claim+validate) |

**核心逻辑错误防护**: 不得从 21→3 直接推出 cognitive load ↓。必须实测 cost + burden。

---

## 5. 实验变量 (最小化) [D]

### 5.1 Primary Outcome

| 变量 | 测量 | A | B | C |
|---|---|---|---|---|
| **Cognitive Cost** | completion time (per workflow) | 21×t_inst | t_group + t_abstraction | 3×t_claim |
| **Evidence Exposure** | instances reviewed (count) | 21 | 21 | 3 (default) + N (on-demand expansion) |
| **Validation Quality** | correctness vs GT | 21 judgments vs GT | 3 judgments vs GT | 3 judgments vs GT |

### 5.2 Validation Quality 细分 [D]

| 子指标 | 定义 | 材料限制 |
|---|---|---|
| Correctness | judgment == GT | 21 cases (19 KS + 2 MERGE) |
| False Acceptance | Human says KEEP_SEPARATE but GT=MERGE | 2 MERGE cases only |
| False Rejection | Human says MERGE but GT=KEEP_SEPARATE | 19 KS cases |
| UNKNOWN handling | Human says UNKNOWN when evidence insufficient | 4 partition_unresolvable + 6 region_not_formed |

### 5.3 Secondary Outcome (optional, 非必需)

| 变量 | 测量 | 必需? |
|---|---|---|
| Perceived difficulty | 5-point Likert per workflow | NO (secondary) |
| Confidence | 5-point Likert per judgment | NO (secondary) |
| Error detection | Human 是否发现 System 误判 | NO (automation bias coverage LIMITED) |

**不为了"看起来全面"增加指标。** Secondary 仅在 pilot 中顺便收集, 不作 primary claim。

---

## 6. Burden Transfer 检测 [D]

### 6.1 检测逻辑

```
A vs C:
  if (C.count < A.count) AND (C.quality >= A.quality) AND (C.time < A.time):
      → C 优于 A (cost↓, quality preserved)
  if (C.count < A.count) AND (C.quality < A.quality):
      → C 牺牲质量换效率 (FAIL C2)
      
B vs C:
  if (B.count == C.count == 3) AND (B.time > C.time) AND (B.quality <= C.quality):
      → C 优于 B (same count, less burden, quality preserved)
  if (B.count == C.count == 3) AND (B.abstraction_burden > C.abstraction_burden):
      → burden transfer detected in B (B 把 abstraction 转给 Human)
```

### 6.2 Burden Transfer 信号

```
SIGNAL_POSITIVE (burden transfer confirmed):
  B.count == C.count (both 3)
  BUT B.time > C.time (B 更慢)
  AND/OR B.perceived_difficulty > C.perceived_difficulty
  
SIGNAL_NEGATIVE (no burden transfer):
  B.time ≈ C.time AND B.difficulty ≈ C.difficulty
  → Naive pattern 与 compressed pattern 负担相同
```

### 6.3 Automation Bias 检测 (LIMITED) [D]

```
因 AUTOMATION_BIAS_COVERAGE = LIMITED (0 System≠GT cases):

检测: 
  C 中 Human 是否 100% 接受 System claim?
  if Human accepts 100% AND GT = 100% consistent:
      → 无法区分 "Human 独立验证后同意" vs "Human 因 System claim 而盲目接受"
      → AUTOMATION_BIAS_RESULT = INCONCLUSIVE (记录为 limitation)
```

---

## 7. UNKNOWN 处理 [D]

### 7.1 UNKNOWN 必须是合法结果

```
Human judgment options per task:
  KEEP_SEPARATE  (atoms 属于不同 semantic unit)
  MERGE           (atoms 属于同一 semantic unit)
  UNKNOWN         (evidence 不足以判断)
```

### 7.2 UNKNOWN 正确性判定

| Group | GT | Correct UNKNOWN? |
|---|---|---|
| partition_unresolvable (4) | KEEP_SEPARATE | UNKNOWN = acceptable (evidence insufficient, Human 不强行判断); KEEP_SEPARATE = also correct (if Human recovers via Level 4) |
| region_not_formed (6) | 4 KEEP_SEPARATE + 2 MERGE | UNKNOWN = acceptable for MERGE cases (evidence insufficient); KEEP_SEPARATE = correct for 4 KS; MERGE = correct for 2 MERGE |

### 7.3 Over-compression Risk 检测 [D]

```
C 中 System 对 region_not_formed group 的 claim = "6 instances, no candidate, UNKNOWN"
检测: Human 是否因 "no candidate" 而全部判 UNKNOWN?
  if Human 全 UNKNOWN for region_not_formed:
      → 但其中 2 个 GT=MERGE, 4 个 GT=KEEP_SEPARATE
      → 全 UNKNOWN = correctness 下降 (正确答案是 4 KS + 2 MERGE)
      → 可能是 over-compression (Human 依赖 System "no candidate" 而不自行检查)
```

**这是 C 的关键风险检测点。**

---

## 8. Negative Evidence 保留 [D]

### 8.1 C 必须展示 negative

```
C 展示:
  Group 1 (admitted, 11 members): claim = "different_cell_candidate (candidate)"
  Group 2 (region_not_formed, 6 members): claim = "no candidate (UNKNOWN)"
  Group 3 (partition_unresolvable, 4 members): claim = "INSUFFICIENT_EVIDENCE (UNKNOWN)"
```

Group 2 + 3 = negative evidence (无 candidate)。**C 不得只展示 Group 1。**

### 8.2 Provenance 可恢复 [D]

```
C 中 Human 可 on-demand 展开 Level 4:
  per-instance EIC-1 detail (structural context, partition info, density)
  → Human 可检查 individual case 的 structural evidence
  → 检测: Human 是否实际使用 Level 4? (记录 expansion count)
```

---

## 9. 实验结构 (最小) [D]

### 9.1 Design

```
Within-subject, each participant does A → B → C (or counterbalanced order)
  Conditions: 3 (A, B, C)
  Materials: 21 cases (same set, different presentation per condition)
  Task: semantic validation (KEEP_SEPARATE / MERGE / UNKNOWN)
  
Participant count: pilot (n=3-5, exploratory)
  → 不做 confirmatory statistical inference
  → 标记 PILOT / EXPLORATORY
```

### 9.2 Order / Learning Effect 处理 [D]

```
Counterbalancing: Latin square (3 conditions × 3 orders)
  Order 1: A → B → C
  Order 2: B → C → A
  Order 3: C → A → B

Learning effect: same 21 cases seen 3 times (once per condition)
  → Mitigation: counterbalancing + record order
  → Limitation: same material repeated; record as LIMITATION
  → 不增加新材料 (不扩大 Pattern/Primitive)
```

### 9.3 不增加的 [D]

- NO between-subject design (pilot 太少, within-subject 更 efficient)
- NO complex ANOVA (n=3-5, non-parametric descriptive only)
- NO causal inference (pilot, 非 confirmatory)
- NO blinding (System claim 是 C 的组成部分, 不能隐藏)

---

## 10. 最小数据补充方案 (如材料不足) [D]

### 10.1 当前材料是否需要补充? [I]

**YES, for limited scope:**

| 需补充 | 原因 | 最小方案 |
|---|---|---|
| System≠GT cases (automation bias) | 0 cases; 无法测试 Human 因 System 误导而错误接受 | 从 DICE corpus 补充 3-5 cases: structural similarity high but GT=MERGE (System 可能误产 candidate); 或人为构造 structural-admitted-but-GT-merge case |
| Conflict cases | 0 cases; 无法测试 conflict preservation 的 Human 判断 | 从 corpus 补充 2-3 cases: two evidence sources disagree (EIC-1 says candidate, another source says no) |
| GT balance | 19:2 严重不平衡 | 补充 5-8 MERGE cases (使 balance 达到 ~15:7) |

### 10.2 补充方案限制 [D]

```
DATA_SUPPLEMENT_PLAN:
  scope: 从 DICE IS-11 sampling frame 或同 corpus 补充
  target: +5-8 MERGE cases, +2-3 conflict cases, +3-5 System≠GT cases
  method: same EIC-1 pipeline (frozen), same GT annotation process
  NOT allowed: 修改 EIC-1 / GT / TLD / production code
  NOT allowed: 为补充数据而修改 System architecture
  
  status: PROPOSED (需单独授权; 本阶段不执行)
```

### 10.3 不补充也能做 pilot 吗? [I]

**YES, 但 scope 严重受限:**

- 可做 A/B/C cost 比较 (cognitive cost, evidence exposure);
- 可做 quality 描述 (correctness 描述性统计, 非推断);
- **不可做**: automation bias 测试, false-acceptance 测试, conflict preservation Human 判断;
- 标记: `PILOT_WITH_LIMITED_SCOPE`。

---

## 11. 最小成功标准 [D]

### C1 Cognitive Cost
```
C.time < A.time (C 更快)
OR C.time ≈ A.time (not materially higher)
```

### C2 Quality
```
C.correctness >= A.correctness (C 不牺牲质量)
  注: 因 GT imbalance, 用 descriptive comparison, 非 statistical test
```

### C3 Burden Transfer
```
C: count=3, abstraction_burden=0
B: count=3, abstraction_burden=HIGH
→ C.abstraction_burden < B.abstraction_burden (C 不转嫁 burden)
→ if B.time > C.time AND B.difficulty > C.difficulty: burden transfer in B confirmed
```

### C4 Evidence Integrity
```
C 中:
  UNKNOWN preserved (Group 2,3 展示)
  negative preserved (Group 2,3 = no candidate)
  conflict preserved (conflict_count field in summary; 当前=0, 记录)
  provenance recoverable (Level 4 on-demand, 记录 expansion count)
```

---

## 12. Authority Boundary (实验期间) [D]

```
System:
  aggregation = 0 authority
  compression = 0 authority
  semantic claim = candidate (NOT conclusion)

Human:
  semantic validation = authority (SUPPORTED / UNSUPPORTED / UNKNOWN)

Capability:
  human-controlled (实验不自动产生 Capability)

Runtime:
  0 authority
```

实验不改变 Authority Boundary。C 的 claim 是 candidate, Human 可拒绝。

---

## 13. Experiment Artifact Boundary [D]

```
允许:
  tmp/l5_7_experiment_harness.py   (read-only adapter, calls L5.5 frozen)
  tmp/l5_7_material_set.json       (21 cases + presentation per workflow)
  tmp/l5_7_experiment_protocol.md  (this design)
  tmp/l5_7_*.json/md               (results, NOT yet executed)

不得:
  修改 L5.5 aggregation/compression (frozen)
  修改 GT / TLD / Atomic Observation / IS-11 decision
  修改 production code / schema / Capability Registry / Runtime
  写入生产架构
```

---

## 14. Anti-Overdesign Final Audit [I]

### 14.1 九个问题

| # | 问题 | 回答 |
|---|---|---|
| 1 | 本实验是否真的需要 A/B/C 三组? | **YES** — RQ 需比较 Instance vs Naive-Pattern vs Compressed-Claim; 少于 3 组无法回答 RQ |
| 2 | 是否存在可删除的指标? | Secondary (perceived difficulty, confidence) 可删; Primary (cost, quality, burden) 不可删 |
| 3 | 是否存在可删除的实验条件? | NO — 3 conditions 是回答 RQ 的最小集 |
| 4 | 是否为理论完整性增加变量? | NO — 所有变量直接服务于 RQ |
| 5 | 是否新增 System Primitive? | **NO** — 直接使用 L5.5 {Aggregation, Compression} |
| 6 | 是否新增 Contract? | **NO** — L5.4 Contract 仍适用 |
| 7 | 是否重新打开 Pattern Architecture? | **NO** — Pattern = compression+reuse layer (closed) |
| 8 | 是否存在 experiment-design recursion? | **NO** — 设计直接服务 RQ, 未因"潜在风险"增加设计层 |
| 9 | 是否存在"为排除风险而不断增加设计"趋势? | **NO** — limitations 记录而非设计消除 (§3, §10) |

### 14.2 Minimality 判定

```
EXPERIMENT_DESIGN_MINIMALITY = PASS
  (3 conditions = RQ minimum; 3 primary outcomes = RQ minimum;
   no new architecture; no new contract; no recursion;
   limitations recorded not designed-away)
```

---

## 15. 二十四个问题回答

### Q1: RQ-L5.7 是否可被最小 Human Experiment 回答?
**YES, with material limitations。** A/B/C 最小结构可回答 cost+quality+burden; 但 automation bias / false-acceptance / conflict 测试受材料限制 (§3)。[I]

### Q2: A/B/C 三个 Workflow 是否足够?
**YES。** 3 conditions 是回答 RQ 的最小集。少于 3 无法比较。[D]

### Q3: 当前 21 cases 是否可用于 pilot?
**YES, as PILOT / EXPLORATORY。** n=21 足够 within-subject pilot; 但 GT imbalance (19:2) 使 quality 统计不可行。[I]

### Q4: 是否需要新增数据?
**YES, for limited scope。** 需补充 MERGE cases (GT balance) + conflict cases + System≠GT cases (automation bias)。最小方案见 §10。但 pilot 可先做 (limited scope)。[D]

### Q5: 最小 outcome set?
**{Cognitive Cost (time), Validation Quality (correctness), Burden Transfer (B vs C burden)}。** Secondary = {difficulty, confidence} (optional)。[D]

### Q6: 如何检测 burden transfer?
B vs C: same count (3), compare time + perceived difficulty。B.time > C.time + B.difficulty > C.difficulty → burden transfer in B confirmed。[D]

### Q7: 如何检测 validation quality degradation?
C.correctness vs A.correctness (descriptive, 非 statistical)。C.correctness < A.correctness → quality degradation (FAIL C2)。重点关注 region_not_formed group (over-compression risk, §7.3)。[D]

### Q8: 如何处理 UNKNOWN?
UNKNOWN 是合法 judgment。partition_unresolvable + region_not_formed groups 的 UNKNOWN = acceptable。检测 over-compression: Human 是否因 "no candidate" 而全 UNKNOWN (§7.3)。[D]

### Q9: 如何处理 negative evidence?
C 必须展示 Group 2 (region_not_formed) + Group 3 (partition_unresolvable) = negative。不得只展示 Group 1 (admitted)。Level 4 on-demand 可恢复 per-instance evidence。[D]

### Q10: 如何处理 automation bias?
**AUTOMATION_BIAS_COVERAGE = LIMITED。** 0 System≠GT cases。检测: C 中 Human 是否 100% 接受 System claim; 若是, 结果 = INCONCLUSIVE (无法区分独立验证 vs 盲目接受)。记录为 limitation (§3)。需补充数据 (§10)。[O+D]

### Q11: 当前设计是否已足够?
**YES, for pilot with limited scope。** 设计可回答 cost + quality (descriptive) + burden transfer。不能回答 automation bias / false-acceptance / conflict (material limited)。[I]

### Q12: 是否新增 System Architecture?
**NO。** 直接使用 L5.5 {Aggregation, Compression}。不新增 Primitive / Contract / Pattern Object。[O]

### Q13: 是否出现 experiment over-design?
**NO。** 3 conditions = minimum; 3 outcomes = minimum; no new architecture; limitations recorded not designed-away。EXPERIMENT_DESIGN_MINIMALITY = PASS。[I]

### Q14: 是否应停止设计并申请实验授权?
**YES。** 设计已足够回答 RQ (with limitations)。应停止设计, 申请 pilot 实验授权 (limited scope) 或先补充数据再申请 (full scope)。[D]

---

## 16. Next-Step Decision [D]

### 两条路径

```
PATH 1 (PILOT NOW, LIMITED SCOPE):
  → 使用当前 21 cases 做 pilot
  → 回答: cost + quality (descriptive) + burden transfer
  → 不回答: automation bias, false-acceptance, conflict
  → 标记: PILOT / EXPLORATORY / LIMITED_SCOPE
  → 需授权: HUMAN EXPERIMENT AUTHORIZATION (pilot)

PATH 2 (SUPPLEMENT DATA FIRST, THEN FULL EXPERIMENT):
  → 补充 +5-8 MERGE + 2-3 conflict + 3-5 System≠GT cases
  → 然后做 full experiment (automation bias + false-acceptance + conflict)
  → 需授权: DATA SUPPLEMENT + HUMAN EXPERIMENT AUTHORIZATION
```

### 推荐 [I]

**PATH 1 (PILOT NOW)。** 理由:
1. 当前材料可回答 RQ 的核心 (cost + burden transfer);
2. Pilot 结果可指导 data supplement 的具体需求 (哪些 limitation 最 critical);
3. 不等待 data supplement (可能耗时; pilot 先行更 efficient);
4. 诚实标记 PILOT / LIMITED_SCOPE, 不过度声称。

---

## 17. Gate

```text
==================================================
L5.7 HUMAN VALIDATION EXPERIMENT DESIGN
==================================================
STATUS = DESIGN-READY (design complete; no execution; no recruitment)

EXPERIMENT_DESIGN_MINIMALITY = PASS
  (3 conditions = RQ minimum; 3 primary outcomes = RQ minimum;
   no new architecture; no new contract; no recursion;
   limitations recorded not designed-away)

L5 ARCHITECTURE = CLOSED (not reopened)
NEW_PRIMITIVE = 0
NEW_CONTRACT = 0
NEW_DESIGN = 0 (experiment design only, not architecture design)

RQ-L5.7 = ANSWERABLE (with material limitations)
  core (cost + burden transfer): YES
  automation bias: LIMITED (0 System≠GT cases)
  false-acceptance: LIMITED (0 System≠GT cases)
  conflict: LIMITED (0 conflict cases)
  quality statistical inference: LIMITED (GT imbalance 19:2)

MATERIAL_AUDIT:
  positive: 11 (sufficient)
  negative: 6 (sufficient)
  UNKNOWN: 4 (sufficient)
  boundary: 2 MERGE (limited)
  conflict: 0 (missing)
  automation_bias_material: 0 System≠GT (LIMITED)
  GT_balance: 19:2 (SEVERELY IMBALANCED)

EXPERIMENT_MATERIAL_LIMITATION = RECORDED (§3)
  not designed-away; not architecture-expanded

EXPERIMENT_STRUCTURE:
  within-subject, 3 conditions (A/B/C), 21 cases, counterbalanced Latin square
  pilot n=3-5, exploratory, non-confirmatory
  primary: {cognitive cost, validation quality, burden transfer}
  secondary: {perceived difficulty, confidence} (optional)

SUCCESS_CRITERIA:
  C1: C.time < A.time (or not materially higher)
  C2: C.correctness >= A.correctness (descriptive)
  C3: C.abstraction_burden < B.abstraction_burden
  C4: UNKNOWN/negative/conflict/provenance preserved in C

AUTHORITY_BOUNDARY: preserved (System=0, Human=authority, claim=candidate)

RECOMMENDED_PATH = PATH 1 (PILOT NOW, LIMITED SCOPE)
  → use current 21 cases
  → answer cost + burden transfer + descriptive quality
  → mark PILOT / EXPLORATORY / LIMITED_SCOPE
  → data supplement deferred (informed by pilot results)

NEXT =
    HUMAN EXPERIMENT AUTHORIZATION REQUEST (PILOT, LIMITED SCOPE)
    (requires separate authorization; not executed in this phase)

IMPLEMENTATION_AUTHORIZATION = NOT AUTHORIZED (production)
EXPERIMENT_AUTHORIZATION = NOT AUTHORIZED (requires separate human-subject authorization)
DATA_SUPPLEMENT_AUTHORIZATION = NOT AUTHORIZED (requires separate)
PRODUCTION = FALSE
FROZEN_BASELINE = INTACT
STOP = TRUE
==================================================
```

## 附: 实验设计事实

1. **3 conditions** (A/B/C) = RQ 最小集;
2. **21 cases** = pilot material (within-subject, each participant does all 3);
3. **3 groups** (L5.5) = C 的 claim 数 (exposure 3 vs 21);
4. **Primary outcomes** = {cost, quality, burden transfer} (3, minimum);
5. **Secondary outcomes** = {difficulty, confidence} (optional, 不作 primary claim);
6. **UNKNOWN** = 合法 judgment (不强迫分类);
7. **Negative** = Group 2+3 必须展示 (不只 positive);
8. **Automation bias** = LIMITED (0 System≠GT; 记录为 limitation);
9. **GT imbalance** = 19:2 (pilot only, 非 confirmatory);
10. **No new architecture** (L5.5 frozen, direct use);
11. **No new contract** (L5.4 applicable);
12. **Limitations recorded** (not designed-away);
13. **PATH 1 recommended** (pilot now, supplement later informed by pilot);
14. **Design stopped** (sufficient for RQ; no L5.7.1/7.2/7.3);
15. **Not executed** (design + audit + authorization request only)。
