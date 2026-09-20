# L5.7 Pilot Harness — Execution Preparation Report

> ISOLATED EXPERIMENTAL (tmp/ only)。Harness 构建 + 材料生成 + 记录 schema 定义。
> **不包含任何 Human 判断数据。** 不模拟 Human 行为。不产生合成结果。
> 为真实 Human 参与者做好一切执行准备。

标注: [O] observed · [D] design · [EV] experimentally verified (code-level)

---

## 1. 本轮完成的工作

| 项 | 状态 | 说明 |
|---|---|---|
| Experiment harness | ✅ COMPLETE | `tmp/l5_7_experiment_harness.py` (19.9 KB) |
| A/B/C presentation materials | ✅ COMPLETE | `tmp/l5_7_pilot_materials.json` (50.7 KB) |
| Recording schema | ✅ COMPLETE | `tmp/l5_7_pilot_recording_schema.json` (2.3 KB) |
| Material validation | ✅ ALL PASS | 7 fairness/integrity checks |
| Frozen baseline | ✅ INTACT | drift=0, 0 production mods |
| Human judgments | ❌ NOT INCLUDED | Requires real human participant |

---

## 2. Harness 功能 [EV]

### 2.1 `tmp/l5_7_experiment_harness.py`

```
generate  → 从 frozen L5.5 输出生成 A/B/C 材料
validate  → 验证材料公平性 + 完整性
schema    → 打印记录 schema
```

- 读取 frozen `mb_phase3_2_isolated_replay_results.json` (read-only)
- 调用 frozen L5.5 `aggregate()` + `compress()` (未修改)
- 生成 3 个 workflow 的 presentation materials
- **不产生任何 judgment / decision / time 数据**

### 2.2 材料结构 [O]

| Workflow | Items | Human sees | Abstraction burden |
|---|---|---|---|
| A | 21 | per-instance: structural context (sce_status, region_forms, density, partition info) | 0 (independent judgment) |
| B | 3 | per-group: all member instances (no compression, no summary, no claim) | HIGH (Human does commonality/comparison/prototype) |
| C | 3 | per-claim: compressed Semantic Claim Candidate + summary + progressive disclosure | 0 (System did abstraction) |

### 2.3 记录 Schema [D]

**必需字段:**
```
participant_id, item_id, workflow, case_id_or_group_id, decision, time_seconds
```

**可选字段:**
```
difficulty (Easy/Medium/Hard), confidence (Low/Medium/High),
order_position, expansion_count (C only), levels_viewed (C only), behavioral_notes
```

**行为指标:**
```
ABSTRACTION_BEHAVIOR  → cross-instance comparison / commonality / prototype
REVISIT_BEHAVIOR       → frequent return to previous evidence
EXPANSION_BEHAVIOR     → expand beyond default exposure (C only)
```

**Workload proxy 警告:**
```
review_count / evidence_exposure / interaction_count = workload PROXY, NOT cognitive_load
True burden = time + difficulty + abstraction_burden + task_behavior
```

---

## 3. Material Validation [EV]

| 检查项 | 结果 |
|---|---|
| same_judgment_options (A/B/C 一致) | ✅ {KEEP_SEPARATE, MERGE, UNKNOWN} |
| C_no_answer_leak | ✅ (0 leaks; no keep_separate/merge/correct/answer/gt/conclusion) |
| C_claim_is_candidate | ✅ (interpretation_status = candidate/UNKNOWN, 非 conclusion) |
| A_gt_set | ✅ {MERGE, KEEP_SEPARATE} (GT hidden from Human) |
| B_shows_all_members | ✅ (21 total = all cases, no compression) |
| C_level4_recoverable | ✅ (per-instance detail available on-demand) |
| C_shows_negative | ✅ (2 negative groups + 1 positive group) |

**ALL 7 CHECKS PASS。**

---

## 4. A/B/C 公平性 [EV]

| 公平性维度 | A | B | C |
|---|---|---|---|
| Task | 判断 atom pair 是否同一 semantic unit | 同左 | 验证 Semantic Claim Candidate |
| Judgment options | KEEP_SEPARATE / MERGE / UNKNOWN | 同左 | 同左 |
| Material | 21 frozen cases | 21 frozen cases (grouped) | 21 frozen cases (compressed) |
| GT | hidden (scoring only) | hidden | hidden |
| Semantic label | NONE | NONE | NONE (claim = candidate) |
| Answer leak | NONE | NONE | NONE (0 leak words) |
| System conclusion | NONE | NONE | NONE (candidate, not conclusion) |

---

## 5. Progressive Disclosure (C) [D]

```
Level 0 (default): Claim Candidate + Summary (counts + grouping criteria)
  ↓ Human requests more
Level 1: Summary detail (already in default)
  ↓
Level 2: Member refs (case_id list)
  ↓
Level 3: Boundary / Negative / UNKNOWN (has_candidate, sce_status, non_positive)
  ↓
Level 4: Full Provenance (per-instance EIC-1 detail: structural context)
```

**记录: `expansion_count` + `levels_viewed` (C only)**

核心观察: 如果 C default exposure = 3 但 Human 频繁展开到 Level 4 (actual exposure ≈ 21), 说明 Compression 技术上成立但 Human 认为压缩信息不足。

---

## 6. 行为观察维度 [D]

### 6.1 Information Load
- default evidence shown (A=21, B=21, C=3)
- expanded evidence (C: track expansion_count)
- full provenance viewed (C: track level_4_requested)

### 6.2 Choice Load
- A/B/C 都只有 3 options (KEEP_SEPARATE / MERGE / UNKNOWN)
- 不增加选项

### 6.3 Reasoning Load (核心观察)
- ABSTRACTION_BEHAVIOR: Human 是否做跨实例比较 / 找共同点 / 归纳 / 找边界 / 找反例
- 预期: A=low, B=high, C=low
- 若 C 出现 ABSTRACTION_BEHAVIOR → OBSERVED_BURDEN_TRANSFER = TRUE

### 6.4 Memory Load
- REVISIT_BEHAVIOR: Human 是否频繁回看以前内容
- 预期: A=high (21 instances), B=medium (3 groups but 21 members), C=low (3 claims)

---

## 7. 关键观察: N_instances → N_claims → Human Work [D]

```
N_instances = 21
    ↓ Aggregation
N_groups = 3
    ↓ Compression
N_claims = 3
    ↓ Human validation
N_human_judgments = 3 (C) vs 21 (A) vs 3 (B)

Key question: N_claims → Human Work 是否真正降低?
  - If C.time < A.time AND C.abstraction = 0 AND C.quality ≥ A.quality → C 有效
  - If C.time ≈ A.time OR C.abstraction > 0 → burden transfer
```

---

## 8. 规模化观察 (pilot-level, 非证明) [D]

```
N_instances = 21 → N_groups = 3 → N_claims = 3 → N_judgments = 3

If N_instances = 1000:
  - A: 1000 judgments (linear)
  - B: ~N_groups judgments + 1000 instance reading (Human burden = high)
  - C: ~N_claims judgments (if compression holds)

Pilot 不能证明 1000 可扩展, 但可观察:
  N_instances → N_claims 是否有实际压缩效果
  N_claims → Human Work 是否仍存在高认知成本
```

---

## 9. 允许 C 失败 [D]

```
If real human results show:
  C judgment count ↓ BUT
  Human reasoning ↑ OR
  Human evidence exposure ↑ OR
  Human uncertainty ↑ OR
  Human quality ↓

→ Must record: C DID NOT REDUCE HUMAN COGNITIVE BURDEN
→ Must NOT modify Aggregation/Compression/UI/Claim wording to "fix" C
→ Must report as observed failure (potential future research question)
```

---

## 10. 结果分析四层面 [D]

| Layer | 内容 | 当前材料限制 |
|---|---|---|
| 1 Operational | judgment_count, time, interaction_count, evidence_exposure | 可测 |
| 2 Cognitive Behavior | abstraction behavior, revisit, expansion, difficulty | 可观察 |
| 3 Validation Quality | correctness vs GT, false acceptance/rejection, UNKNOWN usage | GT 19:2 → 谨慎 |
| 4 Reusability Potential | instance → group → claim → boundary | 不可声称 generalization |

---

## 11. 执行前还需要的 (NOT in this phase) [D]

| 项 | 状态 | 说明 |
|---|---|---|
| Human participants (n=3-5) | NOT RECRUITED | 需 Human Experiment Authorization |
| Experiment UI / interface | NOT BUILT | 需单独实现 (可基于 materials JSON) |
| Consent form / ethics | NOT DONE | 需 IRB 或等价审查 |
| Result recording tool | NOT BUILT | 可基于 recording schema JSON 实现 |
| Pilot execution | NOT DONE | 本轮不执行 |

---

## 12. 边界 [O]

```
PRODUCTION = FALSE
PRODUCTION_MODIFICATIONS = 0
FROZEN_BASELINE = INTACT (drift=0)
L5.5 NOT MODIFIED (frozen, direct use)
GT / TLD / Atomic Observation / IS-11 / Capability Registry / Runtime = NOT MODIFIED

NEW_PRIMITIVE = 0
NEW_CONTRACT = 0
NEW_ARCHITECTURE = 0
NEW_DESIGN = 0 (harness = infrastructure, not architecture design)

NO HUMAN JUDGMENTS PRODUCED
NO SIMULATED RESULTS
NO FABRICATED EVIDENCE
```

---

## 13. Gate

```text
==================================================
L5.7 PILOT HARNESS — EXECUTION PREPARATION
==================================================
STATUS = HARNESS-READY (materials + schema complete; no execution; no human data)

HARNESS = COMPLETE (tmp/l5_7_experiment_harness.py)
MATERIALS = COMPLETE (A=21, B=3, C=3; all validation PASS)
RECORDING_SCHEMA = COMPLETE (required + optional + behavioral indicators)
MATERIAL_VALIDATION = ALL 7 CHECKS PASS

FROZEN_BASELINE = INTACT (drift=0)
PRODUCTION_MODIFICATIONS = 0
L5.5_NOT_MODIFIED = True

NO_HUMAN_JUDGMENTS = True
NO_SIMULATED_RESULTS = True
NO_FABRICATED_EVIDENCE = True

L5_ARCHITECTURE = CLOSED
NEW_PRIMITIVE = 0
NEW_CONTRACT = 0
NEW_DESIGN = 0

EXPERIMENT_AUTHORIZATION = NOT AUTHORIZED
  (requires: human participants + UI + consent + ethics approval)

NEXT =
    HUMAN EXPERIMENT AUTHORIZATION
    → Recruit participants (n=3-5 pilot)
    → Build experiment UI (based on materials JSON)
    → Obtain consent / ethics approval
    → Execute A/B/C with real humans
    → Record decisions + time + behavior
    → Analyze 4 layers (operational / cognitive / quality / reusability)
    → Report real human evidence (A-class)

IMPLEMENTATION_AUTHORIZATION = NOT AUTHORIZED
PRODUCTION = FALSE
FROZEN_BASELINE = INTACT
STOP = TRUE
==================================================
```

## 附: 交付物

| 文件 | 大小 | 内容 |
|---|---|---|
| `tmp/l5_7_experiment_harness.py` | 19.9 KB | Harness: generate/validate/schema |
| `tmp/l5_7_pilot_materials.json` | 50.7 KB | A/B/C presentation materials (21+3+3 items) |
| `tmp/l5_7_pilot_recording_schema.json` | 2.3 KB | Recording schema + behavioral indicators |

**无 Human 判断数据。无模拟结果。无伪造证据。** 为真实 Human 执行做好一切准备。需 Human Experiment Authorization 后方可执行。
