# Evidence Relation Expressibility Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY / NO IMPLEMENTATION / NO NEW MODULE / FROZEN INTACT / STOP

---

## 1. Executive Summary

> **Human 真正需要的"关系性 Evidence"中，4/8 可以由现有 Evidence Facts 完全表达，2/8 部分表达，2/8 无法表达。无法表达的两个（Paragraph Membership 和 Caption Boundary）共享同一个缺失：TEXT_BLOCK/REGION 分割观察。但这个缺失不需要在本审计中解决——本审计只记录它。**

核心发现：

1. **TLD 已计算但丢弃了关键 Relation 数据**：TLD 输出 `table.headers`（列标题列表）和 `a_cell/b_cell`（行列位置），但 `compute_is11_observation()` 将其压缩为 `is_in_table` (bool) 和 `different_cell` (bool)，丢弃了 headers 和 cell position。这是 **Distillation Gap**，不是 Observation Gap。

2. **4 个 Relation 完全可表达**（RC1 Column Position, RC5 Cross-instance Alignment, RC6 Counterevidence, RC8 Local Neighborhood）——只需组织现有 Facts，不需要新 Observation。

3. **2 个 Relation 不可表达**（RC2 Paragraph Membership, RC3 Caption Boundary）——共享同一缺失：TEXT_BLOCK/REGION 分割。这是真正的 MISSING_OBSERVATION，但本审计不实现它。

4. **1 个候选不是 Relation**（RC4 Content Type）——它是 L4 Semantic Interpretation，不是 Evidence Relation。

5. **NO NEW MODULE**：Relation 不需要成为新系统对象。它可以作为 derived evidence representation 或 research metadata 存在，不需要持久化、不需要进入 Frozen Baseline、不需要进入 Runtime、不需要成为 API contract。

---

## 2. Research Question

> Human 真正需要的"关系性 Evidence"是否能够由 DICE 当前已经存在的 Evidence Facts 表达？如果能够，最小表达形式是什么？如果不能，究竟缺少什么最小信息？

回答：

- **能够表达**：4/8 完全可表达，2/8 部分可表达
- **最小表达形式**：组合现有 TLD 输出（headers + rows + cell position）和 line_spans，通过 deterministic comparison/grouping
- **不能表达的原因**：Paragraph Membership 和 Caption Boundary 共享同一缺失——TEXT_BLOCK/REGION 分割观察

---

## 3. Data Sources

| 来源 | 数量 | 用途 |
|---|---|---|
| Human Decision-Relevant Evidence Audit | 1 file | 6 missing evidence types, Evidence Value Matrix |
| Experiment Cases | 30 | Full Cue + fields + line_spans |
| P722 Judgments | 55 | A=15, B1=10, B2=30 |
| Reviewer Rationales | 90 | 2 reviewers × 45 cases |
| TLD Raw Output | 30 cases | headers, rows, a_cell, b_cell |
| Candidate Universe | 545 cases | bbox_a, bbox_b, geometric_state |
| Total | 780+ data points | — |

---

## 4. Relation Definition

只有满足以下全部 4 个条件的候选才允许进入 Relation 层：

### R1 — Multi-Evidence Dependency
必须至少依赖两个 Evidence Facts 或一个 Fact 与一个 Context。

### R2 — Relational Meaning
输出必须描述 Evidence 与 Evidence 之间的结构关系，而非简单复制某个字段。

### R3 — Traceability
任何 Relation 必须能回溯到 Input Evidence IDs → Original Evidence → Source/Provenance。

### R4 — No Semantic Closure
Relation 不能直接变成"这是不同表格列"、"这是同一段落"、"应该 KEEP_SEPARATE"。

**Relation Authority**:
```
AUTHORITY = 0
不能: MERGE / KEEP / REJECT / SELECT / ROUTE / RANK / SCORE / RECOMMEND / DECIDE / EXECUTE
```

---

## 5. Relation Candidate Inventory

| ID | Name | Human Evidence | Cases |
|---|---|---|---|
| RC1 | COLUMN_POSITION_RELATION | 70 TABLE_STRUCTURE + 57 NUMERIC_VALUE mentions | 22 |
| RC2 | PARAGRAPH_MEMBERSHIP_RELATION | 4 PARAGRAPH + 8 SENTENCE_BOUNDARY mentions; A/B disagreement | 4 |
| RC3 | CAPTION_CONTINUITY_RELATION | 13 FIGURE_CAPTION mentions | 2 |
| RC4 | CONTENT_TYPE_RELATION | 57 NUMERIC_VALUE + 14 TABLE_HEADER mentions | 13 |
| RC5 | CROSS_INSTANCE_ALIGNMENT_RELATION | Implied by 70 TABLE_STRUCTURE mentions | ALL table |
| RC6 | COUNTEREVIDENCE_RELATION | 2 P722 UNKNOWN decisions (uncertainty) | ALL |
| RC7 | BOUNDARY_INDICATOR_RELATION | 8 SENTENCE_BOUNDARY + TLD different_cell | 13 |
| RC8 | LOCAL_NEIGHBORHOOD_RELATION | 16 LOCAL_CONTEXT mentions | ALL |

---

## 6. Fact vs Relation Boundary

### 示例 A: `same_y_band = TRUE`
**FACT** — 这是原生 Geometry Observation（dy=0），不是 Relation。不得为 Cue 方便重新包装成 Relation。

### 示例 B: `different_cell = TRUE`
**FACT (derived from Relation)** — TLD 计算 `a_cell != b_cell` 得到 boolean。原始 Relation 数据（`a_cell=(row,col)`, `b_cell=(row,col)`）被压缩为 boolean。这是 **Distillation 压缩过度** 的证据。

### 示例 C: `A 与 B 分别属于两个稳定纵向结构`
**RELATION (L3)** — 可以由 TLD table.rows 的列提取组合得到。提取 A 所在列的所有 items 和 B 所在列的所有 items，形成两个纵向结构组。

---

## 7. Relation Expressibility Analysis

### 关键发现：TLD 已计算但丢弃的数据

```
TLD detect_tables_from_lines() 输出:
  table.headers: ['model', 'top-1 err.', 'top-5 err.', '64-d', '256-d', ...]
  table.rows: [[cell, cell, ...], [cell, cell, ...], ...]
  table.bbox: [x0, y0, x1, y1]

compute_is11_observation() 输出:
  is_in_table: bool           ← 从 a_cell is not None 派生
  different_cell: bool        ← 从 a_cell != b_cell 派生
  table_info.a_cell: (row, col)  ← 存在但未被 Cue 使用
  table_info.b_cell: (row, col)  ← 存在但未被 Cue 使用
  table_info.tables_detected: int

被丢弃的数据:
  table.headers → 未传递到 Cue 层
  table.rows → 未传递到 Cue 层
  a_cell (row, col) → 存在于 table_info 但未用于 Cue
  b_cell (row, col) → 存在于 table_info 但未用于 Cue
```

**结论**：Column Position Relation (RC1) 的全部输入数据已经由 TLD 计算，但在 `compute_is11_observation()` → Cue 的传递过程中被压缩为 boolean，丢弃了结构关系数据。

---

## 8. Minimal Fact → Relation Composition

### RC1 Column Position Relation (FULLY EXPRESSIBLE)

```
INPUT_FACTS:
  - text_a = '28.54' (P1 text observation)
  - text_b = '10.02' (P1 text observation)
  - TLD table.headers (TLD detect_tables_from_lines)
  - TLD table.rows (TLD detect_tables_from_lines)

DERIVATION:
  - search text_a in table.rows → (row=7, col=6)
  - search text_b in table.rows → (row=7, col=7)
  - header_a = table.headers[6] = 'top-1 err.'
  - header_b = table.headers[7] = 'top-5 err.'
  - same_row = (7 == 7) = True
  - same_column = (6 == 7) = False
  - column_distance = abs(6-7) = 1

OUTPUT (L2 Local Structural Relation):
  'A is in column 6 (header: top-1 err.), B is in column 7 (header: top-5 err.), same row, adjacent columns'

NEW_OBSERVATION_REQUIRED: NO
SEMANTIC_LEAKAGE: NO (states structural position, not 'different table columns → KEEP_SEPARATE')
```

### RC5 Cross-instance Alignment Relation (FULLY EXPRESSIBLE)

```
INPUT_FACTS:
  - TLD table.rows
  - a_cell (row, col) from TLD
  - b_cell (row, col) from TLD

DERIVATION:
  - column_items_A = [row[col_A] for row in table.rows if row[col_A] != '-']
  - column_items_B = [row[col_B] for row in table.rows if row[col_B] != '-']

OUTPUT (L3 Cross-instance Structural Relation):
  'A aligns vertically with [B6, 83.95, 84.04, 96.76, ...]; B aligns with [., B7, 84.26, ...]'

NEW_OBSERVATION_REQUIRED: NO
SEMANTIC_LEAKAGE: NO
PATTERN_BOUNDARY: DETECTED — approaches Pattern but stays within single table
```

### RC6 Counterevidence Relation (FULLY EXPRESSIBLE)

```
INPUT_FACTS:
  - TLD is_in_table (bool)
  - TLD different_cell (bool)
  - text_a ends with period (cue5)
  - text_b starts with capital (cue6)
  - text_a contains 'FIG' (cue7)

DERIVATION:
  - if is_in_table AND ends_period → TABLE_VS_SENTENCE conflict
  - if different_cell AND ends_period → CELL_VS_SENTENCE_BOUNDARY conflict
  - if is_in_table AND has_fig → TABLE_VS_FIGURE conflict

OUTPUT (L2 Local Structural Relation):
  'Evidence conflict: TABLE_VS_SENTENCE (TLD=table but text=sentence-like)'

NEW_OBSERVATION_REQUIRED: NO
SEMANTIC_LEAKAGE: NO (states conflict, not decision)
CASES: 3/30 (AMB-005, AMB-522, AMB-530)
```

### RC8 Local Neighborhood Relation (FULLY EXPRESSIBLE)

```
INPUT_FACTS:
  - line_spans (list of same-line items with x-positions)
  - bbox_a, bbox_b (positions)
  - line_obs_count

DERIVATION:
  - sort line_spans by x0
  - left_neighbor_A = item before A in sorted list
  - right_neighbor_B = item after B in sorted list

OUTPUT (L1 Pairwise Relation):
  'A has left neighbor "1. Introduction"; B has right neighbor (none)'

NEW_OBSERVATION_REQUIRED: NO
SEMANTIC_LEAKAGE: NO
CASES: 30/30 (all have line_spans)
```

### RC2 Paragraph Membership (NOT EXPRESSIBLE)

```
INPUT_FACTS AVAILABLE:
  - text_a, text_b (content)
  - bbox_a, bbox_b (position)
  - same_style (font match)
  - line_spans (same-line items)
  - dy (vertical distance)

MISSING:
  - Paragraph boundary detection (where does paragraph P start/end?)
  - Text block grouping (which lines belong to the same block?)
  - Reading order (is A before B in reading order?)

CONCLUSION: MISSING_OBSERVATION (text block / paragraph region detection)
No observation in P1-P6 or TLD computes paragraph or text block structure.
```

### RC3 Caption Boundary (PARTIALLY EXPRESSIBLE)

```
INPUT_FACTS AVAILABLE:
  - text_a contains 'FIG' (cue7) → FACT
  - bbox_a, bbox_b (position)
  - line_spans (same-line context)

MISSING:
  - Caption region detection (where does caption text block start/end?)
  - Same missing observation as RC2 (TEXT_BLOCK/REGION segmentation)

CONCLUSION: PARTIALLY EXPRESSIBLE (FIG marker available, boundary missing)
```

---

## 9. Relation Level Classification

| Candidate | Level | 说明 |
|---|---|---|
| RC1 Column Position | **L2** | Local Structural Relation (within one table) |
| RC2 Paragraph Membership | **L2** (desired) | Not expressible — missing observation |
| RC3 Caption Continuity | **L2** (desired) | Partially expressible |
| RC4 Content Type | **L4** | NOT Evidence Relation — Semantic Interpretation |
| RC5 Cross-instance Alignment | **L3** | Cross-instance Structural Relation (within one table) |
| RC6 Counterevidence | **L2** | Local Structural Relation (conflict between evidence types) |
| RC7 Boundary Indicator | **L1/L4** | L1 for individual facts, L4 for type classification |
| RC8 Local Neighborhood | **L1** | Pairwise Relation |

**L4 不属于 Evidence Relation**。RC4 (Content Type) 被排除。

---

## 10. Human Decision Relevance

| Relation | Human Need | Human Case Count | Evidence Traceability | Observed Human Reference |
|---|---|---|---|---|
| RC1 Column Position | HIGH | 22 | YES (TLD headers + rows) | 70 TABLE_STRUCTURE mentions |
| RC2 Paragraph Membership | HIGH | 4 | NO (missing observation) | 4 PARAGRAPH + A/B disagreement |
| RC3 Caption Continuity | MEDIUM | 2 | PARTIAL (FIG marker) | 13 FIGURE_CAPTION mentions |
| RC4 Content Type | HIGH | 13 | N/A (Interpretation) | 57 NUMERIC_VALUE mentions |
| RC5 Cross-instance Alignment | MEDIUM | ALL table | YES (TLD rows) | Implied by TABLE_STRUCTURE |
| RC6 Counterevidence | MEDIUM | ALL | YES (cue comparison) | 2 UNKNOWN decisions |
| RC7 Boundary Indicator | MEDIUM | 13 | PARTIAL | 8 SENTENCE_BOUNDARY |
| RC8 Local Neighborhood | MEDIUM | ALL | YES (line_spans) | 16 LOCAL_CONTEXT |

---

## 11. Relation Necessity

| Relation | Necessity | 理由 |
|---|---|---|
| RC1 Column Position | **NECESSARY** | 22 cases affected; TLD data exists but discarded |
| RC2 Paragraph Membership | **NECESSARY** | Caused A/B disagreement; but not expressible |
| RC3 Caption Continuity | **HELPFUL** | Only 2 cases; FIG marker already available |
| RC4 Content Type | **N/A** | Not Evidence Relation (L4) |
| RC5 Cross-instance Alignment | **HELPFUL** | Useful but approaches Pattern boundary |
| RC6 Counterevidence | **NECESSARY** | 3 cases with conflicts; safety-critical |
| RC7 Boundary Indicator | **HELPFUL** | Individual facts already exist as cues |
| RC8 Local Neighborhood | **HELPFUL** | line_spans already provide this |

**注意**："Human 使用过"不等于"Human 必须使用"。RC1 的 NECESSARY 基于 TLD 数据已存在但被丢弃这一事实，而非仅 Human 提及频率。

---

## 12. Six Priority Relation Audits

### R1 Column / Header Relation
Human 所说"不同列"需要：A/B x-position + alignment group + vertical continuity + header proximity。
**结果**：TLD 已计算 headers 和 cell position。Relation 可表达为 "A in col 6 (top-1 err.), B in col 7 (top-5 err.)"。
区分：Structural Relation = 位置关系；Semantic Interpretation = "这是两个表格列"。

### R2 Paragraph Membership
"同一段落"需要：text + geometry + reading order + region + neighbor relation。
**结果**：无法由现有 facts 组合得到。缺少 text block segmentation。
区分：Structural Relation = 同一文本块；Semantic Interpretation = "这是同一段落"。

### R3 Caption Boundary / Continuity
"同一 Figure Caption"需要：text continuity + reading order + caption-like structure + figure context。
**结果**：FIG pattern 可用（cue7），但 caption 边界缺少。
区分："caption" 本身已是 semantic label；FIG marker 是 fact。

### R4 Content Type
TABLE / FIGURE / CAPTION / PROSE / HEADER / AXIS 这些标签属于 Interpretation，不是 Relation。
**结果**：NOT_EVIDENCE_RELATION (L4)。

### R5 Cross-instance Pattern
A1↔A2↔A3 跨案例对齐。
**结果**：单表内可表达（L3）。跨表聚合 = Pattern = FORBIDDEN。
PATTERN_BOUNDARY_DETECTED = TRUE。

### R6 Counterevidence
Evidence supporting + Evidence contradicting。
**结果**：可通过比较多个 cue 得到（L2 conflict relation）。
不是 Evidence State，是 Evidence Relation（两个 evidence type 之间的冲突关系）。

---

## 13. Missing Information Analysis

| Relation | Missing Type | 说明 |
|---|---|---|
| RC1 Column Position | **NO_MISSING_INFORMATION** | Data exists, organization missing |
| RC2 Paragraph Membership | **MISSING_OBSERVATION** | Text block / paragraph region detection |
| RC3 Caption Boundary | **MISSING_OBSERVATION** | Same as RC2 — caption region detection |
| RC4 Content Type | **SEMANTIC_INTERPRETATION_REQUIRED** | Not an Evidence Relation |
| RC5 Cross-instance | **NO_MISSING_INFORMATION** | Data exists, organization missing |
| RC6 Counterevidence | **NO_MISSING_INFORMATION** | Comparing existing cues |
| RC7 Boundary Indicator | **PARTIAL** | Facts exist, type classification is interpretation |
| RC8 Local Neighborhood | **NO_MISSING_INFORMATION** | line_spans already available |

**关键区分**：如果 existing facts are sufficient but their organization is missing → `MISSING_RELATION_ORGANIZATION`（不是 `MISSING_OBSERVATION`）。

RC1, RC5, RC6, RC8 = `MISSING_RELATION_ORGANIZATION`（不是新观察，是组织现有数据）。
RC2, RC3 = `MISSING_OBSERVATION`（真正的缺失观察：text block segmentation）。

---

## 14. Relation vs Interpretation Boundary

| 层级 | 示例 | 性质 |
|---|---|---|
| L0 Raw Fact | text_a='28.54', dy=0 | 原始观察 |
| L1 Pairwise Relation | A 的左邻是 "1. Introduction" | 两个 fact 的关系 |
| L2 Local Structural Relation | A 在 col 6 (top-1 err.), B 在 col 7 (top-5 err.) | 局部结构关系 |
| L3 Cross-instance Structural Relation | A 的列包含 [B6, 83.95, 84.04, ...] | 跨实例结构关系 |
| L4 Semantic Interpretation | "这是不同表格列" / "应该 KEEP_SEPARATE" | **不属于 Evidence Relation** |

RC4 (Content Type) 是 L4，被排除。

---

## 15. Relation vs Pattern Boundary

RC5 (Cross-instance Alignment) 是最接近 Pattern 的候选：
- 单表内列提取 = L3 Relation ✅
- 跨表列模式聚合 = Pattern ❌ FORBIDDEN

```
PATTERN_BOUNDARY_DETECTED = TRUE
→ RC5 停留在 L3（单表内跨实例关系）
→ 不跨越到 Pattern（跨表聚合）
→ STOP: 不设计 Pattern Engine
```

---

## 16. Relation vs Rule/Decision Boundary

### Rule Leakage Audit

每个 Relation 都有潜在的 rule leakage 形式：

| Relation | Potential Rule | Leakage |
|---|---|---|
| RC1 | if different_columns: KEEP_SEPARATE | YES (if coded) |
| RC2 | if same_paragraph: MERGE | YES (if coded) |
| RC3 | if caption_continuity: MERGE | YES (if coded) |
| RC5 | if different_alignment: KEEP_SEPARATE | YES (if coded) |
| RC6 | if conflict: UNKNOWN | NO |
| RC8 | if neighbors_differ: KEEP_SEPARATE | YES (if coded) |

**关键**：Relation 本身不包含 rule。Rule leakage 只在有人写代码 `if relation → decision` 时发生。只要 `AUTHORITY=0`，无 leakage。

**Audit 结论**：当前 Relation 定义无 rule leakage。Relation 描述结构关系，不包含决策指令。

---

## 17. Relation Expressibility Matrix

| Relation Candidate | Human Need | Existing Facts Sufficient | Minimal Inputs | Level | Missing Information | Semantic Leakage | New Module |
|---|---|---|---|---|---|---|---|
| Column Position (RC1) | HIGH | YES (with organization) | text_a/b + TLD headers + TLD rows | L2 | NO_MISSING_INFORMATION | NO | NO |
| Paragraph Membership (RC2) | HIGH | NO | text + bbox + [MISSING: text block] | L2 | MISSING_OBSERVATION | N/A | NO |
| Caption Continuity (RC3) | MEDIUM | PARTIAL | FIG pattern + bbox + [MISSING: region] | L2 | MISSING_OBSERVATION | NO | NO |
| Content Type (RC4) | HIGH | N/A | N/A | L4 | SEMANTIC_INTERPRETATION | YES | NO |
| Cross-instance Alignment (RC5) | MEDIUM | YES (with organization) | TLD rows + bbox | L3 | NO_MISSING_INFORMATION | NO | NO |
| Counterevidence (RC6) | MEDIUM | YES | TLD bools + text patterns | L2 | NO_MISSING_INFORMATION | NO | NO |
| Boundary Indicator (RC7) | MEDIUM | PARTIAL | period + capital + diff_cell | L1/L4 | PARTIAL | PARTIAL | NO |
| Local Neighborhood (RC8) | MEDIUM | YES | line_spans + bbox | L1 | NO_MISSING_INFORMATION | NO | NO |

**汇总**：
- Fully Expressible: 4/8 (RC1, RC5, RC6, RC8)
- Partially Expressible: 2/8 (RC3, RC7)
- Not Expressible: 2/8 (RC2, RC3-boundary)
- Not Evidence Relation: 1/8 (RC4)

---

## 18. Anti-Overdesign Gate

```
NEW_OBSERVATION_REQUIRED = NO (for expressible relations)
  → RC1, RC5, RC6, RC8 need NO new observation
  → RC2, RC3 need text block segmentation, but this is DOCUMENTED not IMPLEMENTED

NEW_EVIDENCE_TYPE_REQUIRED = NO
  → All expressible relations use existing evidence types

NEW_RELATION_OBJECT_REQUIRED = NO
  → Relations can be derived evidence representations
  → No persistence required
  → No frozen baseline entry required

NEW_MODULE_REQUIRED = NO
  → Relations are deterministic compositions of existing facts
  → Can be expressed as research metadata

NEW_ENGINE_REQUIRED = NO
  → No learning, no pattern matching, no inference

FROZEN_BASELINE_CHANGE_REQUIRED = NO
  → Relations do not modify P1-P6, TLD, Aggregation, Compression, Cue

TLD_CHANGE_REQUIRED = NO
  → TLD already computes the needed data (headers, rows, cells)
  → The gap is in DOWNSTREAM organization, not TLD itself

UI_CHANGE_REQUIRED = NO
  → This audit does not modify UI
```

### Anti-Overdesign 判断

| 问题 | 回答 | 理由 |
|---|---|---|
| A. Relation 能否只是 derived evidence representation？ | YES | 可从现有 facts 确定性派生 |
| B. Relation 是否必须持久化？ | NO | 可即时计算 |
| C. Relation 是否必须进入 Frozen Baseline？ | NO | 不改变 frozen artifacts |
| D. Relation 是否必须进入 Runtime？ | NO | 不改变 runtime |
| E. Relation 是否必须成为 API contract？ | NO | 不是系统接口 |
| F. Relation 是否只是 Human Review presentation / research metadata？ | YES | 可作为研究元数据 |

**A/F 成立 → NO NEW MODULE, NO NEW CORE OBJECT**

---

## 19. Recommended Minimal Research Direction

> **Evidence Relation 不需要成为新的系统对象或模块。它是一个 Distillation/Organization 层面的概念：现有 TLD 输出已包含足够的关系数据（headers, rows, cell positions），但在传递到 Cue 层时被压缩为 boolean。**

最小方向（不实现，仅记录）：

1. **对于可表达的 4 个 Relation（RC1, RC5, RC6, RC8）**：问题不是缺少 Observation，而是 `compute_is11_observation()` → Cue 的传递过程中丢弃了结构数据。这是 **Distillation Gap**，不是 Architecture Gap。

2. **对于不可表达的 2 个 Relation（RC2, RC3）**：共享同一缺失——TEXT_BLOCK/REGION 分割。这是真正的 MISSING_OBSERVATION，但：
   - 仅影响 6/30 案例（4 sentence + 2 caption）
   - P722 B1（无 Cue）在这些案例上仍达 100% 准确率（image 足够）
   - 不值得为此新增 Observation 模块

3. **RC4 (Content Type) 不是 Relation**：它是 L4 Interpretation，不应强行纳入 Relation 层。

4. **RC5 接近 Pattern 边界**：PATTERN_BOUNDARY_DETECTED = TRUE，但停留在 L3。不设计 Pattern Engine。

---

## 20. Confidence / Limitations

### Confidence

| 发现 | 置信度 | 依据 |
|---|---|---|
| TLD 已计算 headers + cell positions | HIGH | 直接运行 TLD 验证 |
| RC1 完全可表达 | HIGH | AMB-024 实际验证：headers[6]='top-1 err.', headers[7]='top-5 err.' |
| RC2 不可表达 | HIGH | P1-P6 + TLD 无 text block segmentation |
| RC6 可表达 | HIGH | 3/30 案例检测到冲突 |
| Relation 不需要新模块 | MEDIUM-HIGH | 可作为 derived representation |
| TLD cell position 有误差 | MEDIUM | a_cell=(3,1) 但实际 '28.54' 在 row 7 col 6 |

### Limitations

- TLD cell position assignment 有误差（a_cell 不总是精确匹配实际位置）
- TLD 覆盖率 41%（10/30 案例有 cell data），非 TLD 页面无法表达 RC1/RC5
- n=1 参与者（P722），Human need 评估基于有限样本
- 无法验证 Relation 是否真的改善 Human 判断（禁止实验）
- RC2/RC3 的 MISSING_OBSERVATION 仅记录，不评估其实现成本

---

## 21. Governance Gate

```
DICE_CORE_MODIFICATION      = NO
P1_P6_MODIFICATION          = NO
ATOMIC_OBSERVATION_CHANGE   = NO
AGGREGATION_CHANGE          = NO
COMPRESSION_CHANGE          = NO
EVIDENCE_CUE_CHANGE         = NO
TLD_MODIFICATION            = NO
SIGNAL_MODIFICATION         = NO
UI_MODIFICATION             = NO
NEW_OBJECT_IMPLEMENTATION   = NO
NEW_MODULE                  = NO
NEW_ENGINE                  = NO
RUNTIME_CHANGE              = NO
ML_TRAINING                 = NO
FROZEN_BASELINE             = INTACT
FROZEN_EXPERIMENT           = INTACT
FORMAL_EXPERIMENT           = NOT_STARTED
CS1_REUSE                   = BLOCKED
HUMAN_VALIDATION            = BLOCKED
STOP                        = TRUE
```

---

## 22. 最终结论

### Q1: Evidence Relation 是否真实存在？

**PARTIALLY_SUPPORTED**

4/8 候选可由现有 Facts 表达（RC1, RC5, RC6, RC8），证明 Evidence Relation 层在结构上是成立的。但 2/8 不可表达（RC2, RC3），说明该层不完全覆盖 Human 需求。

### Q2: 最小 Relation 是什么？

不是 "一个 Relation Engine"。最小 Relation 是：
- **RC1**: `search text_a in TLD table.rows → (row, col) → headers[col]` → "A in column X (header: H)"
- **RC6**: `compare is_in_table vs ends_period` → "TABLE_VS_SENTENCE conflict"
- **RC8**: `sort line_spans by x0 → neighbors of A and B`

这些是 **deterministic composition of existing facts**，不需要新对象。

### Q3: 现有 Evidence 能否表达？

**PARTIALLY_EXPRESSIBLE**

- 4/8 完全可表达（RC1, RC5, RC6, RC8）
- 2/8 部分可表达（RC3, RC7）
- 2/8 不可表达（RC2, RC3-boundary）
- 1/8 不是 Relation（RC4 = L4）

### Q4: 如果不能表达，最小缺失信息是什么？

**TEXT_BLOCK/REGION 分割观察**。

RC2 (Paragraph Membership) 和 RC3 (Caption Boundary) 共享同一缺失：没有观察计算文本块/段落/图注的区域边界。这是唯一的真正 MISSING_OBSERVATION。

但这仅影响 6/30 案例，且 P722 B1 在这些案例上仍达 100% 准确率（image 足够）。不值得为此新增模块。

### Q5: Relation 是否需要进入 DICE Core？

**NO**

- Relation 可作为 derived evidence representation 存在
- 不需要持久化
- 不需要进入 Frozen Baseline
- 不需要进入 Runtime
- 不需要成为 API contract
- 可作为 Human Review presentation / research metadata

**NO NEW MODULE. NO NEW ENGINE.**

### 核心发现

Evidence Relation 中间层 **部分成立**：
- 可表达的部分（4/8）是 **Distillation Gap**（数据存在但被压缩为 boolean）
- 不可表达的部分（2/8）是 **Observation Gap**（text block segmentation 缺失）
- 但 Observation Gap 影响范围小（6/30），且 image 已足够补偿
- Relation 不需要新模块，只需要停止丢弃 TLD 已计算的数据

`STOP = TRUE`。
