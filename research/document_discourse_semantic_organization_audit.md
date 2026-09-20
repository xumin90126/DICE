# Document Discourse / Semantic Organization Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY / NO IMPLEMENTATION / NO NEW MODULE / FROZEN INTACT / STOP

---

## 1. Executive Summary

```
DOCUMENT_DISCOURSE_HYPOTHESIS     = NOT_SUPPORTED
EVIDENCE_ORGANIZATION_GAP         = PRIMARY (17/17 = 100%)
GENUINE_HUMAN_SEMANTIC_GAP        = NOT_SUPPORTED (0/17)
OBSERVATION_GAP                   = NOT_SUPPORTED (0/17)
LLM_ROLE                          = NOT_NECESSARY
MINIMAL_NEXT_STEP                 = Evidence Organization Audit
CURRENT_LEARNING_LEVEL            = L3
```

> **17 个 H2 案例全部是 EVIDENCE_ORGANIZATION_GAP，不是 Document Discourse / Semantic Gap。Human 利用的是表格列结构（同一行、不同列），这是纯结构信息，不是论述/语义信息。所有 17 个案例的 Evidence（bbox、text、line_spans）已经部分存在，但 TLD 未检测到表格，导致列关系未被组织。当前数据中不存在需要 Document Discourse 层的案例。**

核心发现：

1. **17/17 H2 案例是同一类问题**：两个对象在同一个表格/图的不同列/位置，TLD 未检测到表格结构。
2. **Human 利用的信息是结构性的**：表格列、同行位置、header 标识——不是论述/语义。
3. **Evidence 已部分存在**：bbox (x/y 位置)、text content、line_spans 全部可用；缺失的是表格结构关系的组合。
4. **17/17 LOCAL_SUFFICIENT**：Human 只需看局部页面区域，不需要 Global/Section context。
5. **17/17 NO discourse needed**：没有任何案例需要理解作者论述组织。
6. **17/17 LLM NOT_NECESSARY**：Evidence 存在，只是未组织——LLM 无法比空间对齐逻辑更好地解决组织 gap。
7. **TLD 覆盖率是根因**：7 个唯一页面上的表格未被 TLD 检测到。

---

## 2. Case Scope

### H2 Case List (17 cases)

来源：Machine-Requested Minimal Query Audit 中识别的 Type C (EVIDENCE_MISSING) 案例。

```
IS11-AMB-052, IS11-AMB-130, IS11-AMB-163, IS11-AMB-168, IS11-AMB-198,
IS11-AMB-205, IS11-AMB-218, IS11-AMB-257, IS11-AMB-261, IS11-AMB-262,
IS11-AMB-267, IS11-AMB-279, IS11-AMB-313, IS11-AMB-318, IS11-AMB-380,
IS11-AMB-457, IS11-AMB-462
```

- 文档分布：is11_efficientnet (13), is11_cs_001 (2), is11_resnet (1), is11_med_001 (1)
- 页面分布：7 个唯一页面
- GT：全部 KEEP_SEPARATE (17/17)
- Reviewer A/B 一致性：17/17 完全一致
- CASE_SCOPE = VERIFIED（与前一阶段审计完全匹配）

---

## 3. Case Matrix

| Case | Human Decision-Relevant Evidence | Existing? | Organization Gap? | Discourse? | Context Level | Gap Type | Minimal Query | LLM |
|------|----------------------------------|-----------|-------------------|------------|---------------|----------|---------------|-----|
| AMB-052 | Table 6, #params col vs error col | PARTIAL | RELATION_DISCARDED | NO | LOCAL | EVIDENCE_ORG_GAP | VALID | NO |
| AMB-130 | Table 1, Resolution vs #Channels headers | PARTIAL | RELATION_DISCARDED | NO | LOCAL | EVIDENCE_ORG_GAP | VALID | NO |
| AMB-163 | Table 2, Top-5 acc vs #Params | PARTIAL | RELATION_DISCARDED | NO | LOCAL | EVIDENCE_ORG_GAP | VALID | NO |
| AMB-168 | Table 2, param ratio vs #FLOPs | PARTIAL | RELATION_DISCARDED | NO | LOCAL | EVIDENCE_ORG_GAP | VALID | NO |
| AMB-198 | Table 2, Top-1 vs Top-5 acc | PARTIAL | RELATION_DISCARDED | NO | LOCAL | EVIDENCE_ORG_GAP | VALID | NO |
| AMB-205 | Table 2, Top-5 acc vs #Params | PARTIAL | RELATION_DISCARDED | NO | LOCAL | EVIDENCE_ORG_GAP | VALID | NO |
| AMB-218 | Table, #FLOPs vs Top-1 acc | PARTIAL | RELATION_DISCARDED | NO | LOCAL | EVIDENCE_ORG_GAP | VALID | NO |
| AMB-257 | Table 5, model name vs accuracy | PARTIAL | RELATION_DISCARDED | NO | LOCAL | EVIDENCE_ORG_GAP | VALID | NO |
| AMB-261 | Table 5, model name vs accuracy | PARTIAL | RELATION_DISCARDED | NO | LOCAL | EVIDENCE_ORG_GAP | VALID | NO |
| AMB-262 | Table 5, #Param vs Our Model name | PARTIAL | RELATION_DISCARDED | NO | LOCAL | EVIDENCE_ORG_GAP | VALID | NO |
| AMB-267 | Table 5, accuracy vs #Params | PARTIAL | RELATION_DISCARDED | NO | LOCAL | EVIDENCE_ORG_GAP | VALID | NO |
| AMB-279 | Table 5, model name vs accuracy | PARTIAL | RELATION_DISCARDED | NO | LOCAL | EVIDENCE_ORG_GAP | VALID | NO |
| AMB-313 | Table 6, Test Size vs #Classes headers | PARTIAL | RELATION_DISCARDED | NO | LOCAL | EVIDENCE_ORG_GAP | VALID | NO |
| AMB-318 | Table, dataset citation vs sample count | PARTIAL | RELATION_DISCARDED | NO | LOCAL | EVIDENCE_ORG_GAP | VALID | NO |
| AMB-380 | FIG. 4, RBF vs Matérn kernel labels | PARTIAL | RELATION_DISCARDED | NO | LOCAL | EVIDENCE_ORG_GAP | VALID | NO |
| AMB-457 | Table 2, Models vs Size headers | PARTIAL | RELATION_DISCARDED | NO | LOCAL | EVIDENCE_ORG_GAP | VALID | NO |
| AMB-462 | Table 2, WGe vs Avg. headers | PARTIAL | RELATION_DISCARDED | NO | LOCAL | EVIDENCE_ORG_GAP | VALID | NO |

**矩阵解读**：17 行完全同质——全部是 EVIDENCE_ORGANIZATION_GAP，全部 LOCAL_SUFFICIENT，全部 NO discourse，全部 MINIMAL_QUERY_VALID，全部 LLM=NO。

---

## 4. Human Reasoning Reconstruction

### 统一模式

所有 17 个 H2 案例的 Human 推理路径完全相同：

```
CASE
↓
Human Judgment: KEEP_SEPARATE
↓
Visible Evidence Used: Table/Figure structure (column/item membership)
↓
Implicit Relation Used: "A and B are in different columns/items of the same table/figure"
↓
Machine Currently Available? PARTIALLY (bbox + text exist)
↓
Machine Currently Organized? NO (TLD didn't detect table → relation discarded)
↓
Gap Type: EVIDENCE_ORGANIZATION_GAP
```

### Human Evidence Decomposition

| 类别 | 使用频率 | 说明 |
|---|---|---|
| A. Local Text | 17/17 | text content, numeric values, percentage, param suffix |
| B. Spatial Structure | 17/17 | same line (dy≈0), horizontal gap, alignment |
| C. Document Hierarchy | 16/17 | table context (Table N reference) |
| D. Cross-Object Relation | 17/17 | different columns / different items |
| E. Discourse / Authorial | 0/17 | **NONE** |

**关键发现**：Discourse / Authorial Organization 类别在 17 个案例中使用频率为 **0**。

### Reviewer Rationale 关键词频率

| 关键词 | 频率 | 说明 |
|---|---|---|
| "Table" | 16/17 | 表格引用 |
| "column" | 16/17 | 列引用 |
| "different columns" | 16/17 | 不同列 |
| "header" | 4/17 | 表头行 |
| "model name" | 4/17 | 模型名 |
| "accuracy" / "error" | 9/17 | 度量值 |
| "#Params" / "#FLOPs" | 7/17 | 参数/FLOPs |
| "FIG." | 1/17 | 图引用 (AMB-380) |

**所有 rationale 都是结构性的**（表格列、表头、位置），没有任何 rationale 提及论述理解、作者意图、段落关系。

---

## 5. Evidence → Relation → Discourse 三层矩阵

| Layer | Existing Capability | H2 Need | Status |
|-------|-------------------|---------|--------|
| **Evidence** | P1–P7: text, bbox, reading order, line_spans, fields (h_gap, dy, same_style) | text + bbox + spatial alignment | **PARTIALLY_AVAILABLE** — 所有原始 evidence 已存在 |
| **Relation** | TLD: table.headers, table.rows, a_cell, b_cell (when detected); compute_is11_observation() compresses to boolean | SAME_TABLE_ROW_DIFFERENT_COLUMN relation | **RELATION_DISCARDED** — TLD 未检测到表格，关系未被计算 |
| **Discourse** | 不存在 | 不需要 | **NOT_REQUIRED** — 0/17 案例需要论述理解 |

**矩阵解读**：

- Evidence 层：**已有**（bbox + text + line_spans）
- Relation 层：**缺失**（TLD 覆盖率不足，表格结构未被检测）
- Discourse 层：**不需要**（所有案例都是结构性的）

> **核心结论：Gap 在 Relation 层，不在 Discourse 层。不要把 Relation Gap 错误升级成 Discourse Gap。**

---

## 6. Structural vs Discourse 区分

### Structural Organization（17/17 案例使用）

```
Table exists on page
  ↓
Row contains multiple items at same y
  ↓
Each item in different x column
  ↓
Headers identify column meaning
  ↓
A and B are in different columns → KEEP_SEPARATE
```

这是**纯结构**——基于空间位置和表格布局。

### Discourse Organization（0/17 案例使用）

```
Paragraph A
  ↓ explains
Figure B
  ↓ described by
Caption C
  ↓ continued by
Paragraph D
```

这种论述关系在 17 个 H2 案例中**完全未出现**。

### 区分结论

> **H2 是 Structural Organization 问题，不是 Discourse Organization 问题。**

---

## 7. Context Level 分析

| Context Level | Cases | 说明 |
|---|---|---|
| LOCAL_SUFFICIENT | 17 (100%) | 只需看局部页面区域 |
| SECTION_REQUIRED | 0 | 无需 section context |
| GLOBAL_REQUIRED | 0 | 无需 global context |
| MULTI_LEVEL_REQUIRED | 0 | 无需多层级 |
| UNKNOWN | 0 | — |

**17/17 LOCAL_SUFFICIENT**——Human 只需要看到 A/B 所在的局部页面区域（表格/图），不需要理解文章整体结构、section 组织或论述流。

> **不需要引入 Document Discourse Layer。**

---

## 8. Gap Type 详细分析

### Q7 Gap Type 分布

| Gap Type | Count | 说明 |
|---|---|---|
| EVIDENCE_ORGANIZATION_GAP | 17 (100%) | Evidence 已部分存在，但关系未组织 |
| OBSERVATION_GAP | 0 | 无案例需要新 Observation |
| GENUINE_HUMAN_SEMANTIC_GAP | 0 | 无案例需要语义理解 |
| MACHINE_LOGIC_GAP | 0 | 无案例仅缺逻辑（前阶段的 H1 已分离） |
| UNKNOWN | 0 | — |

### EVIDENCE_ORGANIZATION_GAP 的具体含义

对于每个 H2 案例：

1. **已有 Evidence**：
   - `text_a`, `text_b`（文本内容）✓
   - `bbox_a`, `bbox_b`（空间位置）✓
   - `dy ≈ 0`（同一行）✓
   - `h_gap > 0`（水平间隔）✓
   - `line_spans`（同行其他文本项）✓ (10/17 有完整数据, 7/17 有 bbox 可推算)

2. **缺失 Organization**：
   - TLD 未检测到表格 → `is_in_table = False`
   - 表格列关系未计算 → `different_cell = False`
   - 表头未识别 → column identity unknown
   - `compute_is11_observation()` 压缩为 boolean，丢弃了 headers/rows/cell positions

3. **缺失的 Relation**：
   ```
   SAME_TABLE_ROW_DIFFERENT_COLUMN(A, B)
   ```
   定义：A 和 B 在同一水平线（same y），周围有多个其他文本项，构成 TLD 未检测到的表格行。

### 为什么不是 OBSERVATION_GAP？

bbox、text、line_spans **已经存在**于 candidate universe 和 experiment data 中。不是信息不存在，而是信息**未被组织成表格结构关系**。

### 为什么不是 GENUINE_HUMAN_SEMANTIC_GAP？

17/17 Reviewer A/B 完全一致——判断是稳定的、可重复的、基于结构的。不需要语义解释。

---

## 9. Document Discourse Pattern 搜索

### Pattern A-H 检查结果

| Pattern | 出现次数 | 说明 |
|---|---|---|
| A: Object ↔ Caption | 0 | 无案例 |
| B: Paragraph ↔ Figure | 0 | 无案例 |
| C: Paragraph ↔ Table | 0 | 无案例 |
| D: Heading ↔ Content Group | 0 | 无案例 |
| E: Previous ↔ Following Content | 0 | 无案例 |
| F: Local Object ↔ Global Section | 0 | 无案例 |
| G: Multiple Objects → One Semantic Unit | 0 | 无案例 |
| H: Spatially Close → Different Semantic Units | 17 | **但这是 TABLE_DIFFERENT_COLUMNS，不是 discourse** |

### 实际发现的 Pattern

| Structural Pattern | Count | 说明 |
|---|---|---|
| TABLE_DIFFERENT_COLUMNS | 15 (88%) | 同一表格行，不同列 |
| TABLE_COMPARISON_COLUMN_GROUP | 1 (6%) | 比较表中的不同列组 (AMB-262) |
| FIGURE_DIFFERENT_ITEMS | 1 (6%) | 图中不同标签项 (AMB-380) |

> **发现的 Pattern 全部是 Structural，不是 Discourse。**

Pattern H（"Spatially Close → Different Semantic Units"）表面上符合，但 Human 的判断依据是**表格列结构**（不同列 = 不同数据维度），不是"语义上属于不同内容单元"。这是空间/结构判断，不是语义判断。

---

## 10. Spatial Evidence Sufficiency Test

### bbox 数据验证

对 17 个 H2 案例检查 bbox 证据是否足以推断表格结构：

| 检查项 | 结果 | 说明 |
|---|---|---|
| bbox_a 存在 | 17/17 | 全部有 x/y 坐标 |
| bbox_b 存在 | 17/17 | 全部有 x/y 坐标 |
| dy ≈ 0 (same line) | 17/17 | 全部在同一水平线 |
| h_gap > 0 (horizontal separation) | 17/17 | 全部有水平间隔 |
| line_obs_count ≥ 3 (multiple items) | 10/17 | 10 个有完整 line_spans 数据 |
| neighbors exist | 0/17 | 7 个无 neighbors 数据 |

### 结论

> **17/17 案例的 bbox 数据显示 dy≈0（同一行）。这是检测表格行的关键空间证据，且已经存在于 Evidence 中。**

10/17 有完整的 line_spans 数据（同行多个文本项），足以检测表格行结构。
7/17 只有 bbox，但 dy≈0 仍然可从 bbox 直接计算。

**所有空间证据已存在，只是未被组织成表格结构关系。**

---

## 11. LLM Role Feasibility

### 四种 LLM 角色场景检查

| Scenario | H2 Cases | LLM Role |
|---|---|---|
| Case A: Evidence sufficient, organization gap | 17 | **NOT_NECESSARY** — 空间对齐逻辑可解决 |
| Case B: Evidence sufficient, cross-paragraph semantic relation | 0 | NOT_APPLICABLE |
| Case C: Evidence missing | 0 | NOT_APPLICABLE |
| Case D: Human judgment subjective | 0 | NOT_APPLICABLE |

### 结论

> **LLM 在 H2 解决中无必要角色。**

- Evidence 已存在（bbox + text）
- 缺失的是 Relation Composition（表格结构检测）
- LLM 无法比简单的空间对齐检查（dy≈0 + multiple items → table row）更好地解决组织 gap
- 引入 LLM 会增加不必要的复杂性和不可控性

### LLM 职责边界（如果未来需要）

如果未来出现真正需要论述理解的案例（当前数据中不存在），LLM 的职责必须严格限制为：

```
Evidence → LLM Hypothesis → Evidence Traceability → Human Minimal Validation
```

**不允许**：PDF → LLM → Truth / PDF → LLM → Capability / LLM → automatic slicing

---

## 12. Minimal Query 连接

### 对每个 H2 案例的 Minimal Query 测试

```
Question: "这两部分是否属于同一内容单元？"
Options:  [同一内容] [不同内容] [无法判断]
```

| 条件 | 17 H2 Cases |
|---|---|
| Q1: Human 不需理解 Machine 算法 | ✓ 17/17 |
| Q2: Human 不需 Pattern Mining | ✓ 17/17 |
| Q3: Human 不需长篇解释 | ✓ 17/17 |
| Q4: 答案能区分 ≥2 候选解释 | ✓ 17/17 |

### 结论

> **MINIMAL_QUERY_POTENTIALLY_VALID (17/17)**

但关键前提：Human 需要看到页面图像（IMAGE_GROUNDED）来识别表格结构。如果 Machine 已正确组织 Evidence（检测到表格），则 Human 甚至不需要被问——Machine 可以自行判断。

> **Minimal Query 对 H2 是 "fallback"，不是 "primary mechanism"。** 如果 Evidence Organization 修复，Query 不再需要。

---

## 13. 最小可学习单元

| Level | H2 适用？ | 说明 |
|---|---|---|
| L0 Case-specific correction | NO | 17 案例共享同一 pattern |
| L1 Local structural relation | YES | "same table row, different column" |
| L2 Repeated Evidence Organization | YES | 表格列检测 from spatial alignment |
| L3 Cross-document pattern | YES | pattern 出现在 4 个文档 |
| L4 Reusable semantic/discourse | NO | 不是 discourse |

**适当级别 = L2**：Repeated Evidence Organization（表格列检测的空间对齐 pattern）。

这是**结构 pattern**，不是 discourse pattern。学习目标是：

```
if dy ≈ 0 AND multiple items on same line AND regular x-spacing:
    → likely table row
    → items in different x positions = different columns
    → KEEP_SEPARATE
```

---

## 14. Anti-Overdesign Gate

| Gate | Required? | Evidence |
|---|---|---|
| G1: New Observation? | **NO** | bbox + text + line_spans 已存在 |
| G2: New Evidence Type? | **NO** | 空间位置已是 Evidence |
| G3: New Relation Object? | **POTENTIALLY_REQUIRED** | SAME_TABLE_ROW_DIFFERENT_COLUMN relation 需要表达（但不实现） |
| G4: Pattern Engine? | **NO** | 简单空间对齐逻辑足够 |
| G5: Query Engine? | **NO** | Minimal Query 是 fallback，不是 primary |
| G6: Learning Engine? | **NO** | L2 pattern 未验证 (L4 not reached) |
| G7: LLM? | **NO** | 0/17 案例需要 LLM |
| G8: Modify DICE Core? | **NO** | 只需 TLD 覆盖扩展（FROZEN，不修改） |

**G3 是唯一 POTENTIALLY_REQUIRED**——但仅作为审计记录，不实现。

---

## 15. Research Questions (RQ1–RQ10)

### RQ1: 17 个 H2 是否真的属于同一类问题？

**YES. SUPPORTED.**

17/17 案例具有完全相同的结构：
- Gap Type: EVIDENCE_ORGANIZATION_GAP (17/17)
- Structural Pattern: TABLE_DIFFERENT_COLUMNS or similar (17/17)
- Context Level: LOCAL_SUFFICIENT (17/17)
- Discourse Needed: NO (17/17)

### RQ2: Human 最常使用的 Decision-Relevant Evidence 是什么？

**表格列结构（TABLE_COLUMN_REFERENCE）。**

- Table reference: 16/17
- Column reference: 16/17
- 不同列: 16/17
- 图标签: 1/17

Human 的核心判断依据是："A 和 B 在表格/图的不同列/位置"。

### RQ3: 这些 Evidence 当前是否已经存在？

**PARTIALLY_AVAILABLE (17/17).**

- text content: ✓ 已存在
- bbox (x/y position): ✓ 已存在
- dy (same line): ✓ 可从 bbox 计算
- h_gap (horizontal separation): ✓ 可从 bbox 计算
- line_spans (同行其他项): ✓ 10/17 有完整数据
- table structure (TLD output): ✗ 未检测到

### RQ4: 主要缺失是什么？

**Organization / Relation。**

| 缺失类型 | Count |
|---|---|
| Observation | 0 |
| **Organization / Relation** | **17** |
| Logic | 0 |
| Semantic Interpretation | 0 |

Evidence 已存在，但表格结构关系未被组织。

### RQ5: H2 是否存在稳定重复的 Document Organization pattern？

**YES, but STRUCTURAL not DISCOURSE.**

- 重复 pattern: TABLE_DIFFERENT_COLUMNS (15/17) + variants (2/17)
- 稳定性: 17/17 Reviewer A/B 一致
- 跨文档: 4 个文档
- 但这是**结构 pattern**，不是**论述 pattern**

### RQ6: 这些 pattern 是 Structural 还是 Discourse？

**STRUCTURAL (17/17).**

所有 pattern 基于空间位置和表格布局，不涉及论述理解、作者意图或段落关系。

### RQ7: Human 是否需要 Global / Section context？

**NO. LOCAL_SUFFICIENT (17/17).**

Human 只需看局部页面区域（表格/图所在区域），不需要 Global 或 Section context。

### RQ8: 是否存在真正的 Persistent Human Semantic Judgment？

**NOT_SUPPORTED.**

- 0/17 案例需要语义判断
- 17/17 Reviewer A/B 一致 → 判断稳定且结构化
- 如果 TLD 覆盖扩展，17/17 可变为 Machine-Decisive
- 当前数据中不存在 persistent semantic judgment

### RQ9: LLM 在哪里有合理职责？

**NOWHERE in current H2 data.**

- 0/17 案例需要 LLM
- Evidence 已存在，只是未组织
- LLM 无法比空间对齐逻辑更好地解决组织 gap

### RQ10: 当前最小下一步到底是什么？

**Evidence Organization Audit.**

候选选择：

| 选项 | 选择？ | 理由 |
|---|---|---|
| STOP | — | 可选，但还有可研究的 Organization Gap |
| **Evidence Organization Audit** | **✓** | **核心发现：17/17 是 Organization Gap** |
| Relation Composition Prototype | — | 需先完成 Organization Audit |
| Document Organization Audit Extension | — | 不需要——无 discourse 信号 |
| LLM Feasibility Study | — | 不需要——0/17 案例 |
| Human Validation Study | — | 需先解决 Organization Gap |
| New Observation Request | — | 不需要——evidence 已存在 |

---

## 16. Final Verdict

```
DOCUMENT_DISCOURSE_HYPOTHESIS     = NOT_SUPPORTED
EVIDENCE_ORGANIZATION_GAP         = SUPPORTED (17/17 = 100%)
GENUINE_HUMAN_SEMANTIC_GAP        = NOT_SUPPORTED (0/17)
OBSERVATION_GAP                   = NOT_SUPPORTED (0/17)
LLM_ROLE_FEASIBILITY              = NOT_NECESSARY (0/17)
MINIMAL_QUERY_FEASIBILITY         = POTENTIALLY_VALID (17/17, but fallback only)
STRUCTURAL_PATTERN                = SUPPORTED (TABLE_DIFFERENT_COLUMNS, 17/17)
DISCOURSE_PATTERN                 = NOT_SUPPORTED (0/17)
```

### 证据等级

| 假设 | 证据等级 | 说明 |
|---|---|---|
| H1 Observation Gap | NOT_SUPPORTED | 0/17 — bbox + text 已存在 |
| H2 Evidence Organization Gap | **SUPPORTED** | 17/17 — evidence 存在但关系未组织 |
| H3 Genuine Human Semantic Gap | NOT_SUPPORTED | 0/17 — 全部结构化，reviewer 一致 |
| Document Discourse needed | NOT_SUPPORTED | 0/17 — 全部 LOCAL_SUFFICIENT |
| LLM needed | NOT_SUPPORTED | 0/17 — 组织 gap 不需 LLM |

### 核心原则验证

> *"H2 Human 到底看到了什么，而当前 DICE 没有表达什么？"*

**Human 看到了表格列结构。DICE 有 bbox 和 text，但没有组织成表格列关系。**

> *"这些判断是否反映了 Document Discourse / Semantic Organization 层面的信息缺失？"*

**NO. 这些判断反映的是 Evidence Organization层面的信息缺失，不是 Discourse / Semantic 层面。**

---

## 17. Limitations

1. **17 H2 案例全部来自 4 个文档**：pattern 可能在其他文档类型中不成立
2. **TLD 覆盖率 41%**：H2 集中在 TLD 未覆盖的页面，可能不代表所有 evidence organization gap
3. **AMB-380 (FIGURE_DIFFERENT_ITEMS) 只有 1 个案例**：图标签 pattern 的普遍性无法确认
4. **AMB-262 (COMPARISON_COLUMN_GROUP)**：虽然有 "Our Model vs Others" 语境，但 reviewer 仍基于表格结构判断——不能确认是否隐含 discourse
5. **无 future case test**：L4-L7 未达到
6. **Reviewer rationale 是事后解释**：可能不完全反映实时认知过程
7. **P722 只有 1 个参与者**：burden 评估样本有限
8. **本审计不检查 TLD 为什么未检测到这些表格**：TLD 是 FROZEN，只记录 gap 不诊断 TLD

---

## 18. Governance Gate

```
DICE_CORE_MODIFICATION              = NO
P1_P7_MODIFICATION                  = NO
TLD_MODIFICATION                    = NO
ATOMIC_OBSERVATION_MODIFICATION     = NO
AGGREGATION_CHANGE                  = NO
COMPRESSION_CHANGE                  = NO
EVIDENCE_CUE_CHANGE                 = NO
SIGNAL_MODIFICATION                 = NO
UI_MODIFICATION                     = NO
NEW_OBJECT_IMPLEMENTATION           = NO
NEW_MODULE                          = NO
NEW_ENGINE                          = NO
RUNTIME_CHANGE                      = NO
ML_TRAINING                         = NO
LLM_TRAINING                        = NO
CAPABILITY_REGISTRATION_CHANGE      = NO
FROZEN_BASELINE                     = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d)
FROZEN_EXPERIMENT                   = INTACT
FORMAL_EXPERIMENT                   = NOT_STARTED
STOP                                = TRUE
```

---

## 19. 七个最终汇报

### 1. 17 个 H2 到底是什么问题？

**17/17 是 EVIDENCE_ORGANIZATION_GAP**：两个对象在同一个表格/图的不同列/位置，bbox + text 已存在，但 TLD 未检测到表格结构，导致列关系未被组织。

### 2. Human 到底利用了什么信息？

**表格列结构**：Table reference (16/17), Column reference (16/17), 不同列 (16/17), 图标签 (1/17)。全部是结构性空间信息，不是论述/语义信息。

### 3. 这些信息 DICE 是否已有？

**PARTIALLY_AVAILABLE (17/17)**：text ✓, bbox ✓, dy ✓, h_gap ✓, line_spans ✓ (10/17)。缺失的是表格结构关系（TLD 未检测）。

### 4. 是否只是 Evidence Organization Gap？

**YES. SUPPORTED (17/17 = 100%)。** 不是 Observation Gap（evidence 已存在），不是 Semantic Gap（全部结构化），不是 Logic Gap（前阶段 H1 已分离）。

### 5. 是否真的出现 Document Discourse / Semantic Organization 信号？

**NO. NOT_SUPPORTED (0/17)。** 0 个案例需要 discourse 理解，0 个案例需要 section/global context，0 个案例需要语义解释。

### 6. LLM 是否值得进入下一阶段？

**NO. NOT_NECESSARY (0/17)。** Evidence 已存在，只需组织。LLM 无法比空间对齐逻辑更好地解决 organization gap。

### 7. 最小下一步是什么？

**Evidence Organization Audit**：研究如何将已存在的 bbox + text + line_spans 组织成表格列结构关系。不引入新模块、新 Observation、LLM 或 Discourse Layer。

`STOP = TRUE`。
