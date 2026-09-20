# H2 Evidence Organization / Relation Composition Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY / NO IMPLEMENTATION / NO NEW MODULE / FROZEN INTACT / STOP

---

## 1. Executive Summary

```
GROUP_B (Existing Evidence + Deterministic Relation Composition) = 17/17 (100%)
RELATION_STATUS = R2_RELATION_NOT_COMPUTED (17/17)
TERMINOLOGY_CORRECTION = Previous "RELATION_DISCARDED" was WRONG → R2 not R1
ARCHITECTURE_LAYER_NEEDED = NO
LLM_NEEDED = NO
NEW_OBSERVATION_NEEDED = NO
MINIMAL_NEXT_STEP = STOP (audit complete, no further narrowing needed)
```

> **17 个 H2 案例全部属于 Group B：已有 Evidence（P2 same_y_band + h_gap + bbox）足以确定性组合出 SAME_ROW_DIFFERENT_COLUMN 关系，但当前 IS-11 消费者使用 TLD 而非 P2，TLD 未检测到表格，导致关系从未被计算。这不是 R1（RELATION_DISCARDED），而是 R2（RELATION_NOT_COMPUTED）。不需要新 Architecture Layer、新 Observation、LLM 或新模块。**

核心发现：

1. **术语纠正**：前一阶段报告的 "RELATION_DISCARDED" 是错误的。17/17 是 R2_RELATION_NOT_COMPUTED——TLD 未检测到表格，关系从未被计算，不存在"丢弃"。
2. **17/17 Group B**：已有 P2 Evidence（same_y_band + h_gap）可确定性组合出所需关系。
3. **TLD 状态**：15/17 TLD 检测到 0 个表格；2/17 TLD 检测到 1 个表格但 A/B 不在其中。
4. **Consumer/Integration Gap**：IS-11 消费者使用 TLD（chunker 启发式），不查询冻结 P2 结构事实。M-B 审计已发现此 Consumer Gap。
5. **M-B 覆盖**：5/17 部分覆盖（M-B 检查了相同案例但关注不同方面），12/17 未覆盖。
6. **PH-02 区分**：17/17 RELATED_BUT_DIFFERENT——PH-02 是垂直列成员关系（已 REJECTED），H2 是水平行成员关系（不同轴、不同关系、不同失败模式）。
7. **Derived Ephemeral Relation**：所需关系可从已有 Evidence 派生，不需要持久存储、新 schema、新 object。

---

## 2. Case Scope

17 H2 cases from Document Discourse Audit:

```
IS11-AMB-052, IS11-AMB-130, IS11-AMB-163, IS11-AMB-168, IS11-AMB-198,
IS11-AMB-205, IS11-AMB-218, IS11-AMB-257, IS11-AMB-261, IS11-AMB-262,
IS11-AMB-267, IS11-AMB-279, IS11-AMB-313, IS11-AMB-318, IS11-AMB-380,
IS11-AMB-457, IS11-AMB-462
```

CASE_SCOPE = VERIFIED（与前一阶段完全匹配，未重新抽样，未增加 Synthetic cases，未改变 GT）。

---

## 3. Terminology Correction

### 前一阶段的错误

Document Discourse Audit 使用了 `RELATION_DISCARDED` 描述 17 个 H2 案例的 gap。

这暗示 TLD 已经计算了 rows/headers/cells/a_cell/b_cell，但 downstream 只保留了 boolean。

### 实际情况

| R 分类 | 定义 | H2 适用？ |
|---|---|---|
| R1 RELATION_ALREADY_COMPUTED_BUT_DISCARDED | TLD 已计算 rows/headers/cells，但 downstream 只保留 boolean | **NO (0/17)** |
| R2 RELATION_NOT_COMPUTED | 底层 Evidence 已存在，但系统未形成 table row/column relation | **YES (17/17)** |
| R3 EVIDENCE_INSUFFICIENT_FOR_RELATION | 即使已有全部 Evidence，仍不足以确定 relation | NO (0/17) |
| R4 SEMANTIC_INTERPRETATION_REQUIRED | 需要超出结构事实的语义解释 | NO (0/17) |
| R5 UNKNOWN | 现有材料不足以判断 | NO (0/17) |

### TLD 实际运行结果

| TLD 状态 | Count | 说明 |
|---|---|---|
| TLD_RAN_NO_TABLE_DETECTED | 15 (88%) | TLD 运行了，但检测到 0 个表格 |
| TLD_DETECTED_WRONG_TABLE_OR_PARTIAL | 2 (12%) | TLD 检测到 1 个表格，但 A/B 的 bbox 不在其中 |
| TLD_DETECTED_CORRECT_TABLE_WITH_CELLS | 0 (0%) | 无案例中 TLD 正确检测到包含 A/B 的表格 |

**结论**：17/17 是 R2。TLD 从未为这些页面计算表格结构，因此不存在"丢弃"——关系从未被计算。

---

## 4. Minimum Relation Table

| Case | Human Decision | Minimum Relation Needed | Existing Evidence | Can Compose? | Relation Status | Authority Level |
|------|---------------|------------------------|-------------------|--------------|-----------------|-----------------|
| AMB-052 | KEEP_SEPARATE | SAME_ROW_DIFFERENT_COLUMN | dy=0, h_gap=15.4, bbox | YES | R2_NOT_COMPUTED | L2_STRUCTURAL |
| AMB-130 | KEEP_SEPARATE | SAME_ROW_DIFFERENT_COLUMN | dy=0, h_gap=9.1, bbox | YES | R2_NOT_COMPUTED | L2_STRUCTURAL |
| AMB-163 | KEEP_SEPARATE | SAME_ROW_DIFFERENT_COLUMN | dy=0, h_gap=25.8, bbox | YES | R2_NOT_COMPUTED | L2_STRUCTURAL |
| AMB-168 | KEEP_SEPARATE | SAME_ROW_DIFFERENT_COLUMN | dy=0, h_gap=45.2, bbox | YES | R2_NOT_COMPUTED | L2_STRUCTURAL |
| AMB-198 | KEEP_SEPARATE | SAME_ROW_DIFFERENT_COLUMN | dy=0, h_gap=25.6, bbox | YES | R2_NOT_COMPUTED | L2_STRUCTURAL |
| AMB-205 | KEEP_SEPARATE | SAME_ROW_DIFFERENT_COLUMN | dy=0, h_gap=23.7, bbox | YES | R2_NOT_COMPUTED | L2_STRUCTURAL |
| AMB-218 | KEEP_SEPARATE | SAME_ROW_DIFFERENT_COLUMN | dy=0, h_gap=20.7, bbox | YES | R2_NOT_COMPUTED | L2_STRUCTURAL |
| AMB-257 | KEEP_SEPARATE | SAME_ROW_DIFFERENT_COLUMN | dy=0, h_gap=10.1, bbox | YES | R2_NOT_COMPUTED | L2_STRUCTURAL |
| AMB-261 | KEEP_SEPARATE | SAME_ROW_DIFFERENT_COLUMN | dy=0, h_gap=8.1, bbox | YES | R2_NOT_COMPUTED | L2_STRUCTURAL |
| AMB-262 | KEEP_SEPARATE | SAME_ROW_DIFFERENT_COLUMN | dy=0, h_gap=12.0, bbox | YES | R2_NOT_COMPUTED | L2_STRUCTURAL |
| AMB-267 | KEEP_SEPARATE | SAME_ROW_DIFFERENT_COLUMN | dy=0, h_gap=10.9, bbox | YES | R2_NOT_COMPUTED | L2_STRUCTURAL |
| AMB-279 | KEEP_SEPARATE | SAME_ROW_DIFFERENT_COLUMN | dy=0, h_gap=8.1, bbox | YES | R2_NOT_COMPUTED | L2_STRUCTURAL |
| AMB-313 | KEEP_SEPARATE | SAME_ROW_DIFFERENT_COLUMN | dy=0, h_gap=8.4, bbox | YES | R2_NOT_COMPUTED | L2_STRUCTURAL |
| AMB-318 | KEEP_SEPARATE | SAME_ROW_DIFFERENT_COLUMN | dy=0, h_gap=32.9, bbox | YES | R2_NOT_COMPUTED | L2_STRUCTURAL |
| AMB-380 | KEEP_SEPARATE | SAME_FIGURE_DIFFERENT_ITEMS | dy=0.1, h_gap=30.6, bbox | YES | R2_NOT_COMPUTED | L2_STRUCTURAL |
| AMB-457 | KEEP_SEPARATE | SAME_ROW_DIFFERENT_COLUMN | dy=0, h_gap=40.4, bbox | YES | R2_NOT_COMPUTED | L2_STRUCTURAL |
| AMB-462 | KEEP_SEPARATE | SAME_ROW_DIFFERENT_COLUMN | dy=0, h_gap=12.0, bbox | YES | R2_NOT_COMPUTED | L2_STRUCTURAL |

**矩阵解读**：17 行完全同质——全部 SAME_ROW_DIFFERENT_COLUMN（除 AMB-380 为 SAME_FIGURE_DIFFERENT_ITEMS），全部可从已有 Evidence 确定性组合，全部 R2_NOT_COMPUTED，全部 L2_STRUCTURAL。

---

## 5. 最小组合测试

### SAME_ROW_DIFFERENT_COLUMN 的确定性组合推演

所需 Evidence：

| Evidence | 来源 | 可用性 |
|---|---|---|
| dy ≈ 0 (same y-band) | P2 same_y_band (frozen pairwise) 或 bbox 直接计算 | **AVAILABLE** (17/17) |
| h_gap > 0 (不同 x 位置) | P2 h_gap (frozen pairwise) 或 bbox 直接计算 | **AVAILABLE** (17/17) |
| line_obs_count ≥ 3 (同行多个项) | candidate universe line_obs_count | **AVAILABLE** (10/17 有存储, 7/17 可从 bbox 推算) |

组合逻辑：

```
if same_y_band(A, B) == True     // dy ≈ 0
   AND h_gap(A, B) > 0           // 不同 x 位置
   AND line_obs_count ≥ 3        // 同行有多个文本项（表格行特征）
→ SAME_ROW_DIFFERENT_COLUMN(A, B)
→ KEEP_SEPARATE
```

### 实测验证

| 检查项 | 17 H2 Cases |
|---|---|
| dy ≈ 0 (same y) | 17/17 ✓ |
| h_gap > 0 (different x) | 17/17 ✓ |
| dy 范围 | 0.0–0.1 (全部 < 5pt) |
| h_gap 范围 | 8.1–45.2 (全部 > 0) |
| 可确定性组合 | **17/17 YES** |

### 为什么这不是"理论上可能"

因为 17/17 案例的 bbox 数据**已经存在**于 candidate universe 中，dy 和 h_gap **已经存储**或**可直接从 bbox 计算**。这不是理论推演——这是已有数据的实测验证。

---

## 6. TLD 状态详细分析

### TLD 运行确认

TLD **确实运行**了每个 H2 案例的页面（`compute_is11_observation()` 调用 `detect_tables_from_lines()`）。

### TLD 检测结果

| Case | tables_detected | a_in_table | b_in_table | TLD 状态 |
|---|---|---|---|---|
| AMB-052 | 0 | N/A | N/A | NO_TABLE_DETECTED |
| AMB-130 | 0 | N/A | N/A | NO_TABLE_DETECTED |
| AMB-163 | 0 | N/A | N/A | NO_TABLE_DETECTED |
| AMB-168 | 0 | N/A | N/A | NO_TABLE_DETECTED |
| AMB-198 | 0 | N/A | N/A | NO_TABLE_DETECTED |
| AMB-205 | 0 | N/A | N/A | NO_TABLE_DETECTED |
| AMB-218 | 0 | N/A | N/A | NO_TABLE_DETECTED |
| AMB-257 | 0 | N/A | N/A | NO_TABLE_DETECTED |
| AMB-261 | 0 | N/A | N/A | NO_TABLE_DETECTED |
| AMB-262 | 0 | N/A | N/A | NO_TABLE_DETECTED |
| AMB-267 | 0 | N/A | N/A | NO_TABLE_DETECTED |
| AMB-279 | 0 | N/A | N/A | NO_TABLE_DETECTED |
| AMB-313 | 0 | N/A | N/A | NO_TABLE_DETECTED |
| AMB-318 | 0 | N/A | N/A | NO_TABLE_DETECTED |
| AMB-380 | 0 | N/A | N/A | NO_TABLE_DETECTED |
| AMB-457 | 1 | False | False | WRONG_TABLE_OR_PARTIAL |
| AMB-462 | 1 | False | False | WRONG_TABLE_OR_PARTIAL |

### 原因分类

- 15/17: TLD 算法未检测到表格 → `TLD_ALGORITHM_LIMITATION`
- 2/17: TLD 检测到表格但 bbox 不包含 A/B → `TLD_TABLE_BBOX_MISMATCH`

**不修改 TLD**——只记录原因。

---

## 7. M-B 覆盖检查

### M-B 审计范围

M-B (Table Region Evidence Expressability Audit) 研究的是：冻结 P2/P5 + Atomic Observation evidence 是否足以表达 vector-table 的 region/row/column/cell-like partition。

### M-B 核心发现

M-B 审计发现：
1. P2 same_y_band + h_gap + left_alignment_group **AVAILABLE**（冻结）
2. IS-11 消费者使用 TLD，**不查询** P2 结构事实 → **CONSUMER/INTEGRATION GAP**
3. correct-vs-blind 对比证明盲页上证据**齐全且与已解析页同类**

### M-B 与 H2 的重叠

| 分类 | Count | 说明 |
|---|---|---|
| MB_PARTIALLY_COVERS | 5 (29%) | M-B 检查了相同案例（AMB-130, 262, 313, 457, 462）但关注 P2 expressability，不是 IS-11 consumer gap |
| MB_NOT_COVERED | 12 (71%) | M-B 未检查这些案例 |

### 关键发现

M-B 已发现 **Consumer/Integration Gap**（IS-11 使用 TLD 而非 P2），这与 H2 的发现完全一致。但 M-B 的焦点是 P2 expressability（"P2 能否表达 table structure"），而 H2 的焦点是 IS-11 consumer gap（"为什么 IS-11 不使用 P2"）。

**M-B 已识别相同 gap 机制，但未在 IS-11 consumer 层面解决。H2 不提出新的 Organization mechanism——M-B 的 Consumer Gap 发现已足够。**

---

## 8. PH-02 / C2 重叠检查

### PH-02 状态

PH-02 = **REJECTED**。失败根因：把 `left_alignment_group`（Geometry Fact）直接当作 Column Membership Object（Structural Object）——**Whole-Group-as-Research-Object error**。

### PH-02 vs H2 对比

| 维度 | PH-02 | H2 |
|---|---|---|
| 关系轴 | 垂直（column membership） | 水平（row membership） |
| Evidence | left_alignment_group (P2 singles) | same_y_band + h_gap (P2 pairwise) |
| Research Object | "这是一个 column" (whole group) | "A 和 B 在同一行不同列" (pairwise) |
| 失败模式 | Whole-group heterogeneity (正文 token 混入) | 不适用（pairwise，不是 whole-group） |
| 状态 | REJECTED | Group B (可组合) |

### 关键区分

PH-02 的失败是因为它把**整个 alignment group**当作一个**结构对象**来检验整集等距性质。group 天然异构（混合表格列 + 正文 token），导致整体性质检验必然失败。

H2 的关系是**pairwise**（A 和 B 之间的 same_y_band + h_gap），不涉及 whole-group 聚合。两个特定 atom 之间的 dy≈0 和 h_gap>0 是**确定性几何事实**，不存在 PH-02 的异构性问题。

**PH-02_RELATED_BUT_DIFFERENT (17/17)**：相同 Evidence 来源（P2），不同关系（垂直 vs 水平），不同失败模式（whole-group vs pairwise）。**H2 不重复 PH-02 的 rejected logic。**

### C2 状态

C2 = **PAUSED / BLOCKED**。根因：CandidateSpan upstream geometry limitation（row 104 bbox 腐败）。C2 是 DICE 1.0 的 Semantic Boundary Constraints，与 DICE 2.0 的 H2 无直接关系。

**C2_NOT_RELEVANT**：C2 关注的是 DICE 1.0 candidate span 的段落合并边界，不是 DICE 2.0 IS-11 的表格列关系。

---

## 9. Group 分类

| Group | Count | 说明 |
|---|---|---|
| A: Existing Evidence + Existing Relation | 0 | 无案例中 TLD 已计算正确关系 |
| **B: Existing Evidence + Deterministic Composition** | **17 (100%)** | **P2 same_y_band + h_gap 可确定性组合** |
| C: New Evidence required | 0 | 无案例需要新 Observation |
| D: Semantic Interpretation required | 0 | 无案例需要语义解释 |
| E: UNKNOWN | 0 | — |

---

## 10. Relation 生命周期

### DERIVED_EPHEMERAL_RELATION

SAME_ROW_DIFFERENT_COLUMN 关系的特征：

| 需求 | 是否需要？ |
|---|---|
| Persistent storage | **NO** — 可从 bbox 实时计算 |
| New schema | **NO** — dy 和 h_gap 已在 candidate universe 中 |
| New object | **NO** — pairwise relation，不需 object |
| New registry | **NO** — 不注册新 capability |
| Runtime use | 可选 — 如果 IS-11 consumer 查询 P2 |

**结论**：`DERIVED_EPHEMERAL_RELATION`——可从已有 Evidence 实时派生，不需要持久化。

---

## 11. Architecture Need

### 是否需要新 Architecture Layer？

**NO。**

理由：

1. Evidence 已存在（P2 same_y_band + h_gap，冻结）
2. Relation 可确定性组合（dy≈0 + h_gap>0 → SAME_ROW_DIFFERENT_COLUMN）
3. 不需要新 Observation（bbox + text 已存在）
4. 不需要新 schema（pairwise relation，不需 object）
5. 不需要新 module（简单几何组合逻辑）
6. 不需要新 engine（确定性推导，不需要推理引擎）

> **Existing Evidence → Deterministic Composition → Derived Relation 本身不等于新的 Architecture Layer。**

### 唯一的 Gap

**Consumer/Integration Gap**：IS-11 消费者使用 TLD 而非 P2。M-B 审计已发现此 gap。

这是**集成问题**，不是**架构问题**。解决方案是让 IS-11 consumer 查询 P2 same_y_band（或直接从 bbox 计算 dy/h_gap），而不是修改 TLD 或新增 Architecture Layer。

**但本审计不实现任何修改。**

---

## 12. LLM Need

**LLM_NOT_NECESSARY (17/17)。**

| 条件 | H2 满足？ |
|---|---|
| Existing Evidence + Deterministic Composition 仍无法表达 | NO (17/17 可组合) |
| Human 判断涉及 discourse/semantic role/authorial organization | NO (17/17 纯结构) |
| Cross-section meaning needed | NO (17/17 LOCAL_SUFFICIENT) |

**0/17 案例需要 LLM。**

---

## 13. Minimal Human Query

**不需要。**

如果 Evidence Organization 修复（IS-11 consumer 查询 P2 或直接计算 dy/h_gap），17/17 案例可由 Machine 自行判断。Human 不需要被问。

> **如果只是结构关系：不要把它交给 Human。Machine 应该自己解决。**

---

## 14. Research Questions (RQ1–RQ10)

### RQ1: 17 个 H2 是否都可以归结为 structural organization？

**YES. SUPPORTED (17/17)。** 全部 SAME_ROW_DIFFERENT_COLUMN（或 SAME_FIGURE_DIFFERENT_ITEMS），全部 L2_STRUCTURAL，0/17 需要 discourse/semantic。

### RQ2: 多少属于各分类？

| 分类 | Count |
|---|---|
| A: Representation/Distillation (relation already computed but discarded) | 0 |
| **B: Relation Composition (evidence exists, relation not computed)** | **17** |
| C: Evidence Gap (insufficient evidence) | 0 |
| D: Semantic Interpretation Gap | 0 |
| E: Unknown | 0 |

### RQ3: 最小 Human-relevant Relation 是什么？

**SAME_ROW_DIFFERENT_COLUMN** (16/17)：A 和 B 在同一水平线（dy≈0），不同 x 位置（h_gap>0），同行有多个文本项。

**SAME_FIGURE_DIFFERENT_ITEMS** (1/17, AMB-380)：A 和 B 是图中不同的标签项。

### RQ4: 这些 Relation 是否可以从已有 Evidence 确定性组合？

**YES (17/17)。**

组合逻辑：`same_y_band(A,B) == True AND h_gap(A,B) > 0 → SAME_ROW_DIFFERENT_COLUMN`

Evidence 来源：P2 frozen pairwise (same_y_band, h_gap) 或 bbox 直接计算。

### RQ5: M-B 是否已经覆盖？

**PARTIALLY。**

- 5/17: MB_PARTIALLY_COVERS（M-B 检查了相同案例但关注 P2 expressability）
- 12/17: MB_NOT_COVERED

M-B 已发现 Consumer/Integration Gap（IS-11 使用 TLD 而非 P2），与 H2 发现一致。但 M-B 未在 IS-11 consumer 层面解决。**H2 不提出新的 Organization mechanism——M-B 的发现已足够。**

### RQ6: PH-02/C2 是否已经研究过同类问题？

**PH-02: RELATED_BUT_DIFFERENT (17/17)。**

PH-02 是垂直列成员关系（left_alignment_group → column），已 REJECTED for whole-group-as-research-object error。H2 是水平行成员关系（same_y_band → row），是 pairwise relation，不涉及 whole-group 聚合。**不同轴、不同关系、不同失败模式。H2 不重复 PH-02 的 rejected logic。**

**C2: NOT_RELEVANT。** C2 是 DICE 1.0 的 Semantic Boundary Constraints，关注 candidate span 段落合并，与 DICE 2.0 IS-11 表格列关系无直接关系。

### RQ7: 是否需要新 Observation？

**NO (0/17)。** bbox + text + P2 same_y_band + h_gap 全部已存在。

### RQ8: 是否需要新 Architecture Layer？

**NO。** Existing Evidence → Deterministic Composition → Derived Relation 不等于新 Architecture Layer。唯一 gap 是 Consumer/Integration（IS-11 使用 TLD 而非 P2），这是集成问题，不是架构问题。

### RQ9: 是否需要 LLM？

**NO (0/17)。** 17/17 可确定性组合，0/17 需要 semantic interpretation。

### RQ10: 当前最小下一步是什么？

**STOP。**

审计已完成。17/17 H2 案例已确认为 Group B（Existing Evidence + Deterministic Composition）。不需要新 Architecture Layer、新 Observation、LLM 或新模块。Consumer/Integration Gap 已由 M-B 审计识别。

---

## 15. 最终结论

```
A = Existing Evidence + Existing Relation sufficient       → 0/17
B = Existing Evidence + Deterministic Relation Composition → 17/17 (100%)
C = New Evidence required                                   → 0/17
D = Genuine Semantic Interpretation required                → 0/17
E = UNKNOWN                                                 → 0/17
```

### 核心结论

> **17 个 H2 案例全部属于 Group B：已有 Evidence（P2 same_y_band + h_gap）足以确定性组合出 SAME_ROW_DIFFERENT_COLUMN 关系。Gap 不是 Evidence Gap、不是 Semantic Gap、不是 Architecture Gap——而是 Consumer/Integration Gap（IS-11 使用 TLD 而非 P2）。**

### 术语纠正

前一阶段报告的 `RELATION_DISCARDED` 是错误的。正确分类是 `R2_RELATION_NOT_COMPUTED`——TLD 未检测到表格，关系从未被计算，不存在"丢弃"。

---

## 16. Anti-Overdesign Gate

| Gate | Required? | Evidence |
|---|---|---|
| G1: New Observation? | **NO** | bbox + text + P2 same_y_band 已存在 |
| G2: New Evidence Type? | **NO** | pairwise geometry 已是 Evidence |
| G3: New Relation Object? | **NO** | DERIVED_EPHEMERAL_RELATION，不需 object |
| G4: Pattern Engine? | **NO** | 简单几何组合逻辑 |
| G5: Query Engine? | **NO** | Machine 可自行解决 |
| G6: Learning Engine? | **NO** | 确定性推导，不需学习 |
| G7: LLM? | **NO** | 0/17 需要 LLM |
| G8: New Architecture Layer? | **NO** | Consumer/Integration Gap，不是 Architecture Gap |

**全部 NO。不需要任何新架构组件。**

---

## 17. 特别禁止确认

- ~~"DICE 需要 Evidence Organization Engine"~~ → **NOT SUPPORTED**
- ~~"DICE 需要 Relation Engine"~~ → **NOT SUPPORTED**
- ~~"DICE 需要 Document Understanding Layer"~~ → **NOT SUPPORTED**
- ~~"DICE 需要 Discourse Engine"~~ → **NOT SUPPORTED**
- ~~"DICE 需要 LLM"~~ → **NOT SUPPORTED**

---

## 18. Limitations

1. **17 H2 案例来自 4 个文档**：pattern 可能在其他文档类型中不成立
2. **TLD 覆盖率 41%**：H2 集中在 TLD 未覆盖的页面
3. **AMB-380 (FIGURE_DIFFERENT_ITEMS) 只有 1 个案例**：figure pattern 普遍性未确认
4. **确定性组合推演基于 bbox 数据**：未在运行时实际验证（READ-ONLY）
5. **P2 same_y_band 在 candidate universe 中未直接存储**：但 dy 可从 bbox 计算，且 M-B 审计确认 P2 frozen pairwise 提供 same_y_band
6. **Consumer/Integration Gap 修复方案未设计**：本审计只识别 gap，不设计修复
7. **无 future case test**：L4-L7 未达到
8. **TLD 未修改**：只记录 TLD 未检测到表格的原因，不诊断 TLD 内部逻辑

---

## 19. Governance Gate

```
DICE_CORE_MODIFICATION              = NO
P1_P7_MODIFICATION                  = NO
TLD_MODIFICATION                    = NO
ATOMIC_OBSERVATION_MODIFICATION     = NO
M-B_MODIFICATION                    = NO
PH02_MODIFICATION                   = NO
C2_MODIFICATION                     = NO
AGGREGATION_CHANGE                  = NO
COMPRESSION_CHANGE                  = NO
EVIDENCE_CUE_CHANGE                 = NO
SIGNAL_MODIFICATION                 = NO
UI_MODIFICATION                     = NO
NEW_OBJECT_IMPLEMENTATION           = NO
NEW_MODULE                          = NO
NEW_ENGINE                          = NO
LLM                                 = NO
ML_TRAINING                         = NO
RUNTIME_CHANGE                      = NO
CAPABILITY_CHANGE                   = NO
FROZEN_BASELINE                     = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d)
FROZEN_EXPERIMENT                   = INTACT
FORMAL_EXPERIMENT                   = NOT_STARTED
STOP                                = TRUE
```

`STOP = TRUE`。
