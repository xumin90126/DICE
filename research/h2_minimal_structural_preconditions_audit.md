# H2 Minimal Structural Preconditions Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY / NO IMPLEMENTATION / NO NEW MODULE / FROZEN INTACT / STOP

---

## 1. Executive Summary

```
H2_MINIMAL_PRECONDITION_VERDICT = SAFE_STRUCTURAL_RELATION_BUT_NOT_COLUMN_INTERPRETATION
SAFE_LEVEL_2_RELATION = SAME_BAND_SEPARATED_PAIR
UNSAFE_LEVEL_3_INTERPRETATION = SAME_ROW_DIFFERENT_COLUMN
ARCHITECTURE_LAYER_NEEDED = NO
NEW_OBSERVATION_NEEDED = NO
LLM_NEEDED = NO
PH02_RESEARCH_OBJECT_RISK = LOW
SEMANTIC_LEAKAGE = 0 (for Level-2 relation)
AUTHORITY = 0
IMPLEMENTATION_AUTHORIZED = FALSE
STOP = TRUE
```

> **`same_y_band + h_gap > 0` 可以安全形成 Level-2 Local Structural Relation `SAME_BAND_SEPARATED_PAIR`——这是一个确定性、局部、pairwise、authority=0 的几何事实组合，对所有 45 个 GT 案例都为真，无语义泄漏。但不能安全升级为 Level-3 `SAME_ROW_DIFFERENT_COLUMN`，因为 2/2 MERGE 案例（Figure caption: 'FIG. N:' + caption text）同样满足 `same_y_band + h_gap > 0`，但 GT=MERGE。仅凭几何无法区分表格不同列与 Figure caption——区分需要文本模式匹配（'FIG.' 检测，引入语义泄漏）或垂直连续性（当前数据不可测量）。**

---

## 2. Research Question

> **RQ-H2-PRECONDITION：什么最小的、非语义的、可验证的结构前提，能够使局部 P2 Geometry Evidence 安全地形成一个 Local Structural Relation，并避免把普通水平相邻对象误解释成"不同表格列"？**

**回答**：最小安全前提是 `same_y_band(A,B) == True AND h_gap(A,B) > 0`，形成 `SAME_BAND_SEPARATED_PAIR`。但这只能表达"两个对象在同一水平带且有水平间隔"——**不能**表达"它们在不同表格列"。

---

## 3. Input Scope

### Positive Set (17 H2 cases)

全部来自前序审计确认的 H2 case list。逐 case 保留 document_id, page, text, bbox, dy, h_gap, x0/x1, width, line_obs_count, same_style, TLD evidence。

### Negative/Control Set

从 45 个 GT 案例中提取所有具有 `same_y_band=True AND h_gap>0` 的非 H2 案例：

| 类型 | Count | 说明 |
|---|---|---|
| H2_POSITIVE | 17 | H2 正例（table different columns） |
| SAME_LINE_CONTROL | 22 | 非 H2 KEEP_SEPARATE（TLD 检测到表格的同行不同列） |
| MERGE_GT | 2 | **GT=MERGE**（Figure caption: 'FIG. N:' + text） |
| DISAGREE | 4 | Reviewer A/B 分歧（prose 同行） |

**总计 45 个 GT 案例，其中 45/45 满足 `same_y_band + h_gap > 0`。**

---

## 4. Precondition Matrix

| Precondition | H2 (17) | MERGE (2) | DISAGREE (4) | KS Control (22) | Classification |
|---|---|---|---|---|---|
| P1: same_y_band | 17/17 | 2/2 | 4/4 | 22/22 | NECESSARY_CANDIDATE (but not sufficient) |
| P2: h_gap > 0 | 17/17 | 2/2 | 4/4 | 22/22 | NECESSARY_CANDIDATE (but not sufficient) |
| P3: x0(A) < x0(B) | 17/17 | 2/2 | — | — | SUPPORTING (doesn't distinguish) |
| P4: line_obs ≥ 3 | 17/17 | 1/2 | 3/4 | — | DOES NOT DISTINGUISH |
| P5: vertical continuity | YES (tables) | NO (captions) | — | — | UNKNOWN (not measurable) |
| P6: width consistency | varies | varies | — | — | REDUNDANT |
| P7: local density | 17/17 | 1/2 | 3/4 | — | DOES NOT DISTINGUISH |
| P8: bounded local context | YES (pairwise) | YES | YES | YES | NECESSARY_CANDIDATE |
| P9: local repetition | YES (tables) | NO (captions) | — | — | UNKNOWN (not measurable) |
| P10: TLD evidence | 0/17 | 0/2 | — | — | NOT_SUPPORTED |

### Key Finding

**P1 + P2 (same_y_band + h_gap) 是必要的，但不能区分 H2（KEEP_SEPARATE）与 MERGE（GT=MERGE）。**

- MERGE AMB-414 ('FIG. 9:' / 'Left:'): same_y=YES, h_gap=18.1, line_obs=5, same_style=YES → **全部 geometry preconditions PASS，但 GT=MERGE**
- MERGE AMB-422 ('FIG. 12:' / 'Distribution of...'): same_y=YES, h_gap=10.5, line_obs=2 → most PASS

**P5 (vertical continuity) 和 P9 (local repetition) 可能有区分力，但当前数据无法测量。**

---

## 5. False Positive Analysis

### Rule Trigger Test

```
If rule = (same_y_band AND h_gap > 0 → SAME_ROW_DIFFERENT_COLUMN → KEEP_SEPARATE):
```

| Set | Count | Trigger? | Correct? |
|---|---|---|---|
| H2 positive (GT=KEEP_SEPARATE) | 17 | 17/17 YES | ✓ CORRECT |
| MERGE (GT=MERGE) | 2 | 2/2 YES | ✗ **FALSE POSITIVE** |
| DISAGREE | 4 | 4/4 YES | ⚠ UNCERTAIN |
| KS control (GT=KEEP_SEPARATE) | 22 | 22/22 YES | ✓ CORRECT |

### False Positive Cases

| Case | Text A | Text B | GT | dy | h_gap | line_obs | Issue |
|---|---|---|---|---|---|---|---|
| AMB-414 | 'FIG. 9:' | 'Left:' | MERGE | 0.0 | 18.1 | 5 | Figure caption — should MERGE |
| AMB-422 | 'FIG. 12:' | 'Distribution of errors...' | MERGE | 0.0 | 10.5 | 2 | Figure caption — should MERGE |

### Root Cause

Figure caption 的结构是 `FIG. N: <caption text>`——label 和 text 在同一行，有水平间隔。这在几何上与表格不同列**完全相同**（same_y + h_gap + multiple items）。区分它们的唯一方式是：

1. **文本模式匹配**（检测 'FIG.' 前缀）→ 引入语义泄漏
2. **垂直连续性**（表格有多行，caption 只有一行）→ 当前数据不可测量
3. **TLD 表格检测** → H2 案例中 TLD 未检测到表格

**三种方式都不是纯 Level-2 Geometry Fact。**

---

## 6. PH-02 Comparison

| 维度 | PH-02 | H2 |
|---|---|---|
| 目标关系 | 垂直列成员关系（column membership） | 水平行成员关系（row/column separation） |
| Evidence | left_alignment_group（whole-page P2 singles） | same_y_band + h_gap（pairwise P2） |
| Research Object | "这是一个 column"（whole group as object） | "A 和 B 在同一水平带有间隔"（pairwise fact） |
| 失败模式 | Whole-group contamination（prose token 混入 alignment group） | 不适用（pairwise，不涉及 whole-group） |
| 状态 | REJECTED | Group B (Level-2 safe, Level-3 unsafe) |

### PH-02 Failure Reused?

```
PH02_FAILURE_REUSED = NO
```

H2 使用 **pairwise** local evidence（same_y_band(A,B), h_gap(A,B)），不使用 whole-page alignment group。PH-02 的失败根因（whole-group-as-research-object error）在 H2 中**不适用**。

但 H2 面临一个**不同的**问题：Level-2 几何事实无法区分表格列与 Figure caption。这不是 PH-02 的 whole-group contamination——这是 **geometry ambiguity**（多种文档结构共享相同几何特征）。

---

## 7. M-B Comparison

| 维度 | M-B | H2 |
|---|---|---|
| 研究焦点 | P2 Evidence 是否能表达 table region/row/column | P2 Evidence 能安全形成什么 Local Structural Relation |
| 核心发现 | Consumer/Integration Gap（IS-11 用 TLD 不用 P2） | Level-2 safe, Level-3 unsafe |
| M-B coverage | 5/17 H2 cases examined | — |
| Relation formed | M-B 证明 P2 可表达 table structure | H2 证明只能安全到 SAME_BAND_SEPARATED_PAIR |

### M-B 覆盖？

M-B 证明了 P2 **可以表达** table region structure（expressability）。但 M-B 没有检验 **false positive risk**——即 same_y_band + h_gap 是否会误触发在 Figure caption 上。

H2 审计补充了 M-B 的缺失：**P2 expressability ≠ P2 safe interpretation**。P2 可以表达几何事实，但不能安全地将其解释为"表格列"。

```
MB_FULLY_COVERED = NO
MB_PARTIALLY_COVERS = YES (expressability proven, false positive risk not checked)
NEW_MECHANISM_NEEDED = NO (same P2 evidence, deeper safety analysis)
```

---

## 8. Semantic Leakage Audit

### Level-2: SAME_BAND_SEPARATED_PAIR

| 检查项 | 结果 |
|---|---|
| 包含 'table'? | NO |
| 包含 'cell'? | NO |
| 包含 'column'? | NO |
| 包含 'row_number'? | NO |
| 包含 'caption'? | NO |
| 包含 'paragraph'? | NO |
| 包含 'header'/'footer'? | NO |
| 包含 'meaning'/'role'/'intent'? | NO |

```
SEMANTIC_INTERPRETATION = FALSE
SEMANTIC_LEAKAGE = 0
```

### Level-3: SAME_ROW_DIFFERENT_COLUMN

| 检查项 | 结果 |
|---|---|
| 包含 'column'? | **YES** |
| 包含 'row'? | **YES** |

```
SEMANTIC_INTERPRETATION = TRUE
SEMANTIC_LEAKAGE = non-zero
```

`SAME_ROW_DIFFERENT_COLUMN` 包含 "row" 和 "column"——这些是 **Structural Interpretation** 概念，不是纯 Geometry Fact。要安全使用，必须证明存在足够结构前提区分表格列与其他同行结构。当前数据**无法证明**。

---

## 9. Authority Audit

### Level-2: SAME_BAND_SEPARATED_PAIR

| 检查项 | 结果 |
|---|---|
| 产生 decision? | NO |
| 产生 selection? | NO |
| 产生 routing? | NO |
| 产生 ranking? | NO |
| 产生 score? | NO |
| 产生 confidence? | NO |
| 产生 recommendation? | NO |
| 产生 execution_plan? | NO |
| 产生 fallback? | NO |
| 产生 override? | NO |
| 产生 correction? | NO |

```
AUTHORITY = 0
```

`SAME_BAND_SEPARATED_PAIR` 只陈述几何事实，不做任何决策。

---

## 10. Generalization Audit

| 维度 | 结果 |
|---|---|
| H2 positive coverage | 17/17 (100%) |
| Negative coverage (MERGE) | 2/2 false positive risk |
| Control coverage (KS non-H2) | 22/22 correct |
| DISAGREE coverage | 4/4 uncertain |
| False-positive candidates | 2 (Figure captions) |
| Document diversity | 4 documents |
| Page diversity | 7 pages (H2), more for controls |

### Generalization Status

```
GENERALIZATION_STATUS = INSUFFICIENT_EVIDENCE
```

- 45 个 GT 案例中 2/2 MERGE 案例是 false positive
- 4 个 DISAGREE 案例的 Human 判断不稳定
- 仅 4 个文档，无法评估其他文档类型中的 false positive 率
- Figure caption pattern 可能在其他文档中更常见

**不能宣称 Level-3 `SAME_ROW_DIFFERENT_COLUMN` 可以泛化。**

---

## 11. Minimal Safe Relation

### SAFE: SAME_BAND_SEPARATED_PAIR (Level 2)

```
Definition: same_y_band(A, B) == True AND h_gap(A, B) > 0
```

- **Deterministic**: YES — 从 bbox 直接计算
- **Local**: YES — pairwise，不使用 whole-page group
- **Evidence-grounded**: YES — 来自 P2 frozen pairwise
- **Authority = 0**: YES — 只陈述事实，不做决策
- **Semantic leakage**: 0 — 不包含 table/cell/column/row/caption
- **Provenance-preserving**: YES — 从 frozen bbox 派生

### UNSAFE: SAME_ROW_DIFFERENT_COLUMN (Level 3)

```
Cannot be safely derived from Level-2 alone.
```

- 2/2 MERGE cases 是 false positive
- 区分需要 text pattern（语义泄漏）或 vertical continuity（不可测量）
- **不得自动升级到这一层**

---

## 12. Relation Candidates Evaluation

| Candidate | Level | Safe? | Semantic Leakage | Authority | Verdict |
|---|---|---|---|---|---|
| SAME_BAND_SEPARATED_PAIR | L2 | YES | 0 | 0 | **SAFE** |
| HORIZONTALLY_SEPARATED_PAIR | L2 | YES | 0 | 0 | SAFE (same as above) |
| LEFT_RIGHT_ORDERED_PAIR | L2 | YES | 0 | 0 | SAFE (adds x0 ordering) |
| LOCAL_ROW_SEPARATION | L3 | NO | non-zero | 0+ | UNSAFE |
| SAME_ROW_DIFFERENT_COLUMN | L3 | NO | non-zero | 0+ | UNSAFE |
| TABLE_DIFFERENT_COLUMN | L4 | NO | high | 0+ | FORBIDDEN |

---

## 13. Final Decision

```
H2_MINIMAL_PRECONDITION_VERDICT = SAFE_STRUCTURAL_RELATION_BUT_NOT_COLUMN_INTERPRETATION
```

### 可以安全形成的 Relation

```
SAME_BAND_SEPARATED_PAIR
  = same_y_band(A, B) == True AND h_gap(A, B) > 0
  = Level 2 Local Structural Relation
  = deterministic, local, pairwise, authority=0
  = NO semantic leakage
```

### 不能安全升级的 Interpretation

```
SAME_ROW_DIFFERENT_COLUMN
  = Cannot be derived from Level-2 alone
  = 2/2 MERGE cases are false positive
  = Requires text pattern or vertical continuity (not pure geometry)
  = Level 3 Structural Interpretation
```

---

## 14. Architecture / Observation / LLM Need

```
ARCHITECTURE_LAYER_NEEDED = NO
NEW_OBSERVATION_NEEDED = NO
LLM_NEEDED = NO
TLD_CHANGE_NEEDED = NO
IS11_CHANGE_NEEDED = NO
```

SAME_BAND_SEPARATED_PAIR 是 **DERIVED_EPHEMERAL_RELATION**——可从已有 P2 Evidence 实时派生，不需要：
- Persistent storage
- New schema
- New object
- New registry
- New module
- New engine
- New architecture layer

---

## 15. Implementation Candidate (NOT AUTHORIZED)

如果未来需要使用 SAME_BAND_SEPARATED_PAIR：

```
Frozen Evidence (P2 same_y_band + h_gap)
  → Minimal Structural Preconditions (same_y_band=True AND h_gap>0)
  → Local Structural Relation (SAME_BAND_SEPARATED_PAIR)
  → existing consumer (if integrated)
```

但：
- Local Structural Relation 是 **derived evidence representation**，不是新的 architecture layer
- **IMPLEMENTATION_AUTHORIZED = FALSE**
- 本审计不实现任何代码

---

## 16. Five Final Questions

### Q1: `same_y_band + h_gap > 0` 是否足以形成安全 Relation？

**YES for Level-2 (SAME_BAND_SEPARATED_PAIR)。NO for Level-3 (SAME_ROW_DIFFERENT_COLUMN)。**

几何事实"同一水平带 + 存在水平间隔"是安全的。但将其解释为"不同表格列"是不安全的——2/2 MERGE 案例（Figure caption）证明了几何无法区分。

### Q2: 如果不足，还需要什么最小结构前提？

**Vertical continuity (P5) 或 Local repetition (P9)**——即证明 A/B 所在的行结构在多个相邻 y-band 中重复出现（表格多行）。但这两种前提**当前数据不可测量**（没有 adjacent row evidence）。

如果未来可以测量 vertical continuity，则可能安全升级到 Level-3。但当前只能停留在 Level-2。

### Q3: 这个 Relation 是哪一级？

```
SAME_BAND_SEPARATED_PAIR = Level 2 (Local Structural Relation)
```

不是 Level 1（Geometry Fact）——因为它是对两个 geometry facts 的组合。
不是 Level 3（Structural Interpretation）——因为它不包含 table/column/row 语义。
不是 Level 4（Semantic Interpretation）——它不做语义判断。

### Q4: 这个问题到底属于哪一个 Gap？

```
Consumer/Integration Gap
```

- 不是 Observation Gap（bbox + P2 same_y_band 已存在）
- 不是 Research-Object Gap（pairwise relation 避免了 PH-02 的 whole-group error）
- 是 Consumer/Integration Gap（IS-11 使用 TLD 而非 P2，M-B 审计已发现）

同时存在一个 **Interpretation Safety Gap**：Level-2 几何事实可以安全形成，但 Level-3 解释不能安全升级——这不是 Evidence Gap 或 Architecture Gap，而是 **Safety Boundary**。

### Q5: 下一步应该做什么？

```
STOP
```

- 不 IMPLEMENT（Level-2 relation 已定义但未授权实现）
- 不 DESIGN FURTHER（Level-3 的 vertical continuity 需要新数据，但本审计禁止新 Observation）
- 不 COLLECT MORE EVIDENCE（本审计 READ-ONLY，不增加 GT）
- **STOP**——审计完成，结论明确

---

## 17. Limitations

1. **仅 45 个 GT 案例**：2/45 MERGE 案例是 false positive，但样本量不足以估计泛化 false positive 率
2. **仅 4 个文档**：Figure caption pattern 可能在其他文档中更常见
3. **Vertical continuity 不可测量**：当前数据没有 adjacent row evidence，无法验证 P5/P9 的区分力
4. **545 个候选中 528 个无 GT**：大量 same_y + h_gap 案例未被 Human 标注，可能存在未发现的 false positive pattern
5. **MERGE 案例仅 2 个**：Figure caption false positive 的普遍性无法确认
6. **DISAGREE 案例 4 个**：prose 同行案例的 Human 判断不稳定，几何关系是否安全取决于如何使用
7. **TLD 是 FROZEN**：不修改 TLD，只记录其未检测到 H2 表格
8. **Level-2 relation 未运行时验证**：本审计是 READ-ONLY 推演，未在运行时测试

---

## 18. Governance Gate

```
DICE_CORE_MODIFICATION              = NO
P1_P7_MODIFICATION                  = NO
P2_MODIFICATION                     = NO
TLD_MODIFICATION                    = NO
IS11_MODIFICATION                   = NO
GT_MODIFICATION                     = NO
EXPERIMENT_MODIFICATION             = NO
NEW_MODULE                          = NO
NEW_ENGINE                          = NO
LLM                                 = NO
RUNTIME_CHANGE                      = NO
CAPABILITY_CHANGE                   = NO
FROZEN_BASELINE                     = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d)
IMPLEMENTATION_AUTHORIZED           = FALSE
STOP                                = TRUE
```

---

## 19. 核心原则验证

> *"本审计不是为了证明我们已经找到一个规则，而是为了证明：在什么最小条件下，一个局部 Geometry Relation 才可以被安全地表达。"*

**回答**：最小安全条件是 `same_y_band=True AND h_gap>0`，形成 `SAME_BAND_SEPARATED_PAIR`。此条件对所有 45 个 GT 案例为真，无 false geometry，无语义泄漏，authority=0。

> *"如果只能证明"同一水平带 + 存在水平间隔"，就只停留在这个层级，不得为了帮助 IS-11 而强行把它解释成"不同表格列"。"*

**遵守**：本审计停留在 `SAME_BAND_SEPARATED_PAIR`（Level 2），不升级到 `SAME_ROW_DIFFERENT_COLUMN`（Level 3）。2/2 MERGE false positive 证明升级不安全。

> *"先确定 Research Object，再确定 Relation，再决定是否实现。不要反过来。"*

**遵守**：先确定 Research Object（pairwise geometry fact），再确定 Relation（SAME_BAND_SEPARATED_PAIR），再决定不实现（IMPLEMENTATION_AUTHORIZED=FALSE）。

`STOP = TRUE`。
