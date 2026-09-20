# IS-11 TABLE_CELL_CONTEXT
# Independent Machine-Observability Experiment Design

## READ-ONLY / DESIGN ONLY / NO IMPLEMENTATION

| 字段 | 值 |
|------|-----|
| 实验名称 | IS-11 TABLE_CELL_CONTEXT Independent Machine-Observability Experiment |
| 类型 | 实验设计 (DESIGN ONLY) |
| 前置条件 | Independent Machine-Resolvability Evaluation (COMPLETE) + Failure Analysis (COMPLETE) |
| 约束 | READ-ONLY — 不实现 IS-11，不运行 IS-11，不修改任何 frozen 文件 |
| DESIGN STATUS | READY |
| IS-11 状态 | HYPOTHESIS ONLY |
| IMPLEMENTATION | NOT AUTHORIZED |
| STOP | TRUE |

---

## 1. Research Question

**不研究**: "IS-11 能不能让 accuracy 变高？"

**研究**: "TABLE_CELL_CONTEXT 是否是一种独立、稳定、machine-observable 的 Information Source，能够补充当前 IS-01 + IS-02，并帮助判断：'number + readable text' 究竟是 semantic text-unit continuation，还是 structurally separate table content？"

**研究对象**: INFORMATION SUFFICIENCY，不是 RULE PERFORMANCE。

**核心假设**: IS-01+IS-02 在 TABLE_CELL 场景下产生 FP，是因为缺少 table 结构信息源——而非 IS-01/IS-02 本身的 pattern matching 错误。

---

## 2. Historical Evidence

### 2.1 Frozen Evaluation Results (IMMUTABLE)

| 指标 | 值 |
|------|-----|
| Evaluation Set | 69 cases (FROZEN) |
| TP | 0 |
| FP | 3 (全部 TABLE_CELL) |
| FN | 2 |
| TN | 8 |
| ABSTAIN | 56 |
| Precision | 0.000 |
| Recall | 0.000 |
| Coverage | 18.8% |

### 2.2 Failure Analysis Conclusions

- 3/3 FP 的根因: **Information Source Gap** — 缺少 IS-11 (TABLE_CELL_CONTEXT)
- 2/2 FN 的根因: **Semantic Irreducibility** — 需要 IS-10 (Category C, HUMAN_OWNED)
- 38/56 abstention 为正确保守 (genuine info gap)
- 0/56 过度保守
- TOC-specific hypothesis: UNTESTED (0 target cases)
- General boundary decision: NOT_SUPPORTED

### 2.3 TABLE_CELL 在 Candidate Universe 中的频率

| 文档 | TABLE_CELL | 总 AMBIGUOUS | 占比 |
|------|-----------|-------------|------|
| ind_qbio_rna | 34 | 62 | 54.8% |
| ind_qbio_genomics | 6 | 85 | 7.1% |
| ind_arxiv_bio2 | 0 | 103 | 0% |
| ind_arxiv_2402 | 0 | 4 | 0% |
| **总计** | **40** | **254** | **15.7%** |

**TABLE_CELL 不是偶然现象** — 它在表格密集的生物学论文中占 15.7%，是系统性的 boundary class。

---

## 3. IS-11 Definition

### 3.1 IS-11 作为 Information Source（非 Rule）

IS-11 = TABLE_CELL_CONTEXT

**不是**: "加一个 table detector"

**是**: "Human decision appears to rely on table structural context, which is not represented in current decision input."

### 3.2 候选信息维度

IS-11 可能需要观察以下信息组件：

| # | 组件 | 定义 | 优先级 |
|---|------|------|--------|
| C1 | table_region | 候选对是否位于 table 区域内 | HIGH |
| C2 | cell_membership | text_a 和 text_b 是否属于同一 cell | **CRITICAL** |
| C3 | row_position | text_a 和 text_b 是否在同一行 | MEDIUM |
| C4 | column_position | text_a 和 text_b 是否在同一列 | HIGH |
| C5 | cell_boundary | 各自 cell 的 bounding box | MEDIUM |
| C6 | table_header_relation | 列头与 cell 的对应关系 | LOW |
| C7 | neighboring_cells | 相邻 cell 的内容 | LOW |
| C8 | row_column_alignment | 跨行列对齐稳定性 | MEDIUM |
| C9 | table_body_membership | 是否在 body vs header vs caption | LOW |

**注意**: 这些只是 candidate information sources。不假定全部有效。C2 (cell_membership) 是核心——它直接区分"同一 cell 内的编号+标题"(TOC heading)与"不同 cell 的数字+描述"(table row)。

### 3.3 IS-11 与 IS-12 / IS-14 的边界

| IS | 定义 | 与 IS-11 的关系 |
|----|------|----------------|
| IS-11 | TABLE_CELL_CONTEXT | "这是否是 table 语境" |
| IS-12 | ROW_COLUMN_POSITION | "在 table 中的行列位置" — IS-11 的子组件 |
| IS-14 | DOCUMENT_STRUCTURE_ROLE | "文档结构角色 (reference/caption/table)" — 比 IS-11 更粗粒度 |

**IS-11 vs IS-12**: IS-11 回答"是否在 table 中"，IS-12 回答"在 table 中的哪个位置"。第一实验仅测试 IS-11。

**IS-11 vs IS-14**: IS-11 是 IS-14 的一个特例 (table 是 document structure role 之一)。IS-14 更广泛但更模糊。

---

## 4. Information Availability

### 4.1 P1-P6 现有证据检查

| 组件 | P1-P6 中可用? | 来源 | 状态 |
|------|-------------|------|------|
| table_region | ❌ | P6 DENSE_REGION 是弱代理 (也匹配密集正文) | PARTIALLY_AVAILABLE |
| cell_membership | ❌ | 无 | NOT_AVAILABLE |
| cell_boundary | ❌ | 无 (table_line_detector.py 有但未集成) | NOT_AVAILABLE |
| row_position | ❌ | dy=0.0 可用但非 row-specific | NOT_AVAILABLE |
| column_position | ⚠️ | bbox x-coordinates 可用但未聚类 | PARTIALLY_AVAILABLE |
| table_header_relation | ❌ | 无 | NOT_AVAILABLE |
| table_body_membership | ❌ | 无 | NOT_AVAILABLE |
| neighboring_cells | ❌ | 无 | NOT_AVAILABLE |
| row_column_alignment | ⚠️ | x-coordinates 可用但未分析 | PARTIALLY_AVAILABLE |

**总结**: 9 个信息组件中，0 个在 P1-P6 中完全可用，3 个部分可用 (raw coordinates)，6 个完全不可用。

### 4.2 table_line_detector.py — 存在但未集成

| 维度 | 状态 |
|------|------|
| 文件位置 | `chunker/table_line_detector.py` |
| 功能 | detect_tables_from_lines(): 表格检测 + 行列聚类 + cell grid + header |
| P1-P6 集成 | ❌ 未集成 — 仅作为依赖 hash 被跟踪 |
| P6 table labels | ❌ P6 明确禁止 table/image/figure 标签 (geometric only) |
| P6 Region Types | PAGE_TOP, PAGE_BOTTOM, FULL_WIDTH, COLUMN, DENSE, SPARSE, UNKNOWN |

**关键发现**: IS-11 evidence EXISTS in the codebase (table_line_detector.py) but is NOT accessible through P1-P6 pipeline。

### 4.3 "Information exists" vs "Information is machine-accessible"

| 维度 | Human 可观察? | P1-P6 机器可访问? | 差距 |
|------|-------------|-----------------|------|
| Table region | ✅ (视觉) | ❌ (DENSE 是弱代理) | 需要 table region detection |
| Cell membership | ✅ (视觉) | ❌ | 需要 cell boundary detection |
| Column position | ✅ (视觉) | ⚠️ (raw x-coords only) | 需要 column clustering |
| Header relation | ✅ (视觉) | ❌ | 需要 header detection |

**结论**: Human 能从 PDF 视觉上观察 table 结构，但 P1-P6 不提供机器可用的 table 证据。table_line_detector.py 存在但未集成——这是 INTEGRATION GAP，不是 CAPABILITY GAP。

---

## 5. Historical FP Analysis (3 Exemplars)

### 5.1 IND-AMB-247: "121" + "40 mM Hepes"

| 维度 | 值 |
|------|-----|
| Human reason A | "'121' is a numeric value (molecular weight) and '40 mM Hepes' begins the RNA folding buffer description — they are in different columns of the same table row" |
| Human reason B | "'121' is a numeric value (RNA length in nt) and '40 mM Hepes' begins the RNA folding buffer; they are separate cells in different table columns" |
| Human IS used | IS-11 (TABLE_CELL_CONTEXT), IS-12 (ROW_COLUMN_POSITION) |

**Human 依赖分析**:
- ✅ table region: 明确提到 "table"
- ✅ cell membership: 明确提到 "separate cells", "different columns"
- ✅ column position: 明确区分 "molecular weight" 列 vs "buffer" 列
- ❌ header relation: 未显式引用列头名称
- ❌ neighboring cells: 未显式引用相邻 cell

**IS-11 是否能解释此 FP?**: YES — 如果 IS-11 检测到 text_a 和 text_b 在不同 cell (不同列)，协议可以将 MERGE 降级为 KEEP_SEPARATE 或 INSUFFICIENT_EVIDENCE。

### 5.2 IND-AMB-223: "5." + "SARS-CoV-2"

| 维度 | 值 |
|------|-----|
| Human reason | "'5.' is the case study number and 'SARS-CoV-2' is the RNA specimen name — they occupy separate columns ('Case study' vs 'RNA Specimen') in the table" |
| Human IS used | IS-01, IS-02, IS-11, IS-12 |

**Human 依赖分析**:
- ✅ table region: 明确提到 "table"
- ✅ cell membership: 明确提到 "separate columns"
- ✅ column position: 明确引用列头 "Case study" vs "RNA Specimen"
- ⚠️ header relation: 隐式引用了列头

**IS-11 是否能解释此 FP?**: YES — 同上，cell membership 检测可区分。

### 5.3 IND-AMB-235: "6." + "RNA"

| 维度 | 值 |
|------|-----|
| Human reason | "'6.' is a case study number and 'RNA' begins the RNA specimen name — they occupy separate columns ('Case study' vs 'RNA Specimen') in the table" |
| Human IS used | IS-01, IS-02, IS-05, IS-11, IS-12 |

**Human 依赖分析**:
- ✅ table region: 明确提到 "table"
- ✅ cell membership: 明确提到 "separate columns"
- ✅ column position: 引用列头

**IS-11 是否能解释此 FP?**: YES — 同上。

### 5.4 FP 共同模式

3/3 FP 中 Human 全部依赖:
1. Table region 识别 (IS-11 C1)
2. Cell membership 判断 (IS-11 C2) — **核心**
3. Column position 区分 (IS-12，IS-11 子组件)

**支持 IS-11 information hypothesis**: TABLE_CELL_CONTEXT 是 Human 做出正确 KEEP_SEPARATE 决策的关键信息源。

**但不能断言 IS-11 一定有效**: 仅 3 个 exemplar，不足以证明 IS-11 在更大样本上稳定有效。

---

## 6. IS-11 与 FN / Abstention 的关系

### 6.1 IS-11 是否能帮助 FN?

2 个 FN (IND-AMB-200, IND-AMB-201) 是引用片段 ("et"/"al.,", "al.,"/"2025)."), 不是 TABLE_CELL。

**IS-11 对 FN 无直接帮助** — FN 的根因是 IS-10 (Category C, HUMAN_OWNED)，不是 table context。

### 6.2 IS-11 是否能帮助 abstention?

56 个 abstention 中:
- 25 个涉及 TABLE_CELL context (IS-11 相关) — IS-11 可能帮助
- 21 个涉及 sentence/paragraph context (IS-10 相关) — IS-11 无帮助
- 10 个其他

**IS-11 可能帮助 25/56 = 44.6% 的 abstention** — 但仅限 TABLE_CELL 类别。

---

## 7. Independent Data Requirement

### 7.1 当前数据状况

| 数据 | 状态 | 可用于 IS-11? |
|------|------|-------------|
| Frozen 69-case Evaluation Set | FROZEN | ❌ 不可作为 development set (contamination) |
| 4 independent PDFs (已用) | 已用于 IS-01/IS-02 评估 | ❌ 不可再用于 IS-11 development (评估集已冻结) |
| 3 partially-contaminated PDFs | metadata contamination | ⚠️ CONDITIONALLY USABLE |
| 新外部 PDFs | 未获取 | ✅ BEST OPTION |

### 7.2 3 个 Partially-Contaminated PDFs 的条件可用性

| PDF | 污染类型 | IS-11 污染? | 可用? |
|-----|---------|-----------|------|
| arxiv_2310 | P1 processed + evidence gap metadata | ❌ 无 IS-11 计算 | ⚠️ CONDITIONAL |
| arxiv_2401 | metadata only | ❌ 无 IS-11 计算 | ⚠️ CONDITIONAL |
| qbio_cell | metadata + fonts | ❌ 无 IS-11 计算 | ⚠️ CONDITIONAL |

**条件**: 这 3 个 PDF 的污染仅限于 metadata 级别 (evidence gap analysis 中提到过文件大小/页数/图片数)，从未计算 IS-11 或分析 TABLE_CELL boundary pairs。如果用于 IS-11 实验，需要:
1. 在实验前记录 provenance (metadata contamination acknowledged)
2. 不从这 3 个 PDF 的 GT 反推 IS-11 definition
3. 与新外部 PDF 的结果分开报告

### 7.3 样本量需求

| 需求 | 值 | 理由 |
|------|-----|------|
| TABLE_CELL cases (minimum) | ≥30 | 统计功效 (当前 3 FP / 11 sampled 不足) |
| Documents with tables | ≥2 | Cross-document generalization |
| Table styles | ≥2 (border + borderless) | Style diversity |
| Non-TABLE_CELL cases | ≥20 | Control (IS-11 不应损害非 table 场景) |

### 7.4 当前不存在真正独立的 IS-11 evaluation data

**INDEPENDENT IS-11 EVALUATION DATA = NOT AVAILABLE**

需要:
1. 获取新的含表格 PDF (最佳选择)
2. 或条件性使用 3 个 partially-contaminated PDFs (次优)
3. 不可以从 frozen 69-case set 拆分 (contamination)

---

## 8. Baselines

### 8.1 三条件设计

| 条件 | 特征 | 目的 |
|------|------|------|
| Baseline A | Geometry only (P4 DETERMINISTIC + AMBIGUOUS) | 建立 floor — 无 IS 特征时表现 |
| Baseline B | Geometry + IS-01 + IS-02 (frozen §9.3) | 建立 IS-01/IS-02 baseline |
| Experimental C | Geometry + IS-01 + IS-02 + IS-11 | 测量 IS-11 增量价值 |

### 8.2 为什么需要 Baseline A

如果只有 Baseline B vs Experimental C，无法知道改善来自 IS-11 还是其他因素。Baseline A 提供 "零 IS" floor。

### 8.3 ONE NEW IS AT A TIME

第一实验**仅加入 IS-11**。不同时加入:
- IS-12 (ROW_COLUMN_POSITION) — IS-11 子组件，待 IS-11 验证后单独测试
- IS-14 (DOCUMENT_STRUCTURE_ROLE) — 更广泛，defer
- IS-10 (SENTENCE_BOUNDARY) — HUMAN_OWNED，永不实现

---

## 9. Sampling Strategy

### 9.1 分层维度

| 维度 | 分层 | 理由 |
|------|------|------|
| Boundary class | TABLE_CELL vs NON-TABLE_CELL | 确保 TABLE_CELL 充足 |
| Table style | bordered vs borderless | 跨样式泛化 |
| IS-01+IS-02 match | True+True vs others | 聚焦 FP 高风险区 |
| Geometry (gap, w_b) | 同 IS-01/IS-02 实验分层 | 可比性 |

### 9.2 采样比例

| 类别 | 目标采样 | 理由 |
|------|---------|------|
| TABLE_CELL (IS-01+IS-02 match) | ≥15 | 高 FP 风险区 |
| TABLE_CELL (IS-01+IS-02 non-match) | ≥15 | IS-11 对 abstention 的影响 |
| NON-TABLE_CELL (control) | ≥20 | IS-11 不应损害非 table 场景 |
| **总计** | **≥50** | 统计功效 |

---

## 10. Blind Human GT

### 10.1 协议

与 IS-01/IS-02 实验完全相同的盲审协议:
- Reviewer A + Reviewer B (独立)
- 仅看: case_id, page, text_a, text_b, page_context
- 不看: IS-11, IS-01, IS-02, geometry, machine prediction, Round 1
- Adjudication for disagreements (第三独立审查者)

### 10.2 GT 冻结时序

```
Stage D: Blind GT Collection → GT FROZEN
Stage E: Evaluation Set Freeze
Stage F: Baseline A+B Machine Evaluation (after GT freeze)
Stage G: IS-11 Observation (after GT freeze, IS-11 spec frozen)
Stage H: Decision Comparison
```

**GT 必须在 IS-11 observation 之前冻结。**

---

## 11. Incremental Information Gain Metrics

| 指标 | 公式 | 目标 |
|------|------|------|
| ΔPrecision | P(C) - P(B) | ≥ 0 (不降级) |
| ΔRecall | R(C) - R(B) | ≥ 0 (不降级) |
| ΔCoverage | Cov(C) - Cov(B) | ≥ 0 (更多确定决策) |
| ΔAbstention | Abstain(C) - Abstain(B) | ≤ 0 (更少 abstention, 但需正确) |
| ΔFPR | FPR(C) - FPR(B) | < 0 (**FP reduction — PRIMARY**) |
| ΔFNR | FNR(C) - FNR(B) | ≤ 0 (无新 FN) |
| ΔShrinkage | Shrink(C) - Shrink(B) | > 0 (新 validated shrinkage) |
| FP Reduction | FP(B) - FP(C) | > 0 (IS-11 减少 TABLE_CELL FP) |
| Validated Shrinkage | Validated(C) / total | > 0 |

---

## 12. Cross-Document Generalization

### 12.1 必须检查的维度

| 维度 | 值 |
|------|-----|
| Document family | ≥2 (e.g., biology + CS) |
| Table style | bordered + borderless |
| Table layout | single-column + multi-column |
| Table content | numeric-heavy + text-heavy |
| Header structure | simple + multi-row/merged |

### 12.2 报告要求

每个文档单独报告: case count, TP, FP, TN, FN, ABSTAIN, precision, recall, FPR, abstention。

如果某文档样本太少 (<10), 标记 LOW_SAMPLE。

---

## 13. IS-11 Failure Modes (Design)

| # | 失败模式 | 描述 | 风险等级 |
|---|---------|------|---------|
| F1 | False table detection | DENSE_REGION 误判为 table | MEDIUM |
| F2 | Missing table region | borderless table 未检出 | HIGH |
| F3 | Cell boundary unavailable | table_line_detector 无法提取 cell grid | MEDIUM |
| F4 | Row/column ambiguity | x-coordinate clustering 不稳定 | LOW |
| F5 | Header/body confusion | header 被当作 body cell | LOW |
| F6 | Cross-cell text fragmentation | 一个 semantic unit 跨越多个 cell | MEDIUM |
| F7 | Table-like but non-table | 视觉类似 table 但实际是 list/figure | MEDIUM |
| F8 | Table context insufficient | 知道是 table 但仍无法判断 semantic boundary | HIGH |
| F9 | Different semantic units in same cell | 同一 cell 内有多个语义单元 | LOW |
| F10 | Same semantic unit across cells | 一个语义单元跨越多个 cell (merged cells) | MEDIUM |

**注意**: 这些是设计阶段预判的 failure mode，不预设全部出现。

---

## 14. Pre-Registered Gates

| Gate | 条件 | 阈值 | 设定时间 |
|------|------|------|---------|
| G1 | Independent Data | ≥30 TABLE_CELL from independent PDFs | 实验前 |
| G2 | IS-11 Spec Freeze | IS-11 定义在 GT 前冻结 | FROZEN |
| G3 | No Leakage | Provenance audit | PASS |
| G4 | Semantic GT Validity | Level 2, kappa ≥ 0.60 | kappa ≥ 0.60 |
| G5 | Cross-Document Coverage | ≥2 docs with tables | ≥2 |
| G6 | Incremental Precision | ΔPrecision > 0 on TABLE_CELL | > 0 |
| G7 | FP Reduction | ΔFP < 0 on TABLE_CELL | < 0 |
| G8 | Recall/Coverage Safety | ΔRecall ≥ 0 AND ΔCoverage ≥ 0 | ≥ 0 |
| G9 | Abstention Safety | 0 new FP from former abstain | 0 |
| G10 | Boundary Shrinkage | ΔShrinkage > 0 | > 0 |
| G11 | Determinism | Run 1 = Run 2 | 0 mismatches |
| G12 | Provenance | Full chain documented | PASS |

---

## 15. Success Criteria

IS-11 成功**不是** "减少了 abstention 就叫成功"。至少要求:

1. 不会显著增加 false positive (ΔFPR < 0)
2. 能够减少一部分 correct/necessary abstention (ΔCoverage > 0)
3. 增量 information gain 可以在 independent data 上复现
4. 跨 document 有稳定表现 (G5 PASS)
5. provenance 完整 (G12 PASS)
6. deterministic (G11 PASS)
7. **FP Reduction > 0** (G7 PASS — PRIMARY)

---

## 16. Failure Criteria

以下任一情况 → IS-11 MACHINE-RESOLVABILITY NOT DEMONSTRATED:

- FP 增加 (ΔFPR > 0)
- 没有 validated shrinkage (ΔShrinkage = 0)
- 只在单文档有效 (G5 FAIL)
- 只能解决 development cases (G3 FAIL — leakage)
- feature 无法稳定提取 (G11 FAIL — non-deterministic)
- 仍高度依赖 semantic interpretation (IS-11 退化为 Category C)
- GT 不可靠 (G4 FAIL)
- provenance 不可证明 (G12 FAIL)

---

## 17. Next Experiment (Beyond IS-11)

如果 IS-11 实验完成:

| 结果 | 下一步 |
|------|--------|
| IS-11 有效 (G7+G8 PASS) | 测试 IS-12 (ROW_COLUMN_POSITION) 增量 |
| IS-11 部分有效 | 分析 F8 (table context insufficient) — 可能需要 IS-14 |
| IS-11 无效 | 转为 HUMAN_OWNED 或重新评估 TABLE_CELL boundary class |
| IS-11 无法稳定提取 | DEFER — 等待更好的 table detection 技术 |

---

## 18. Limitations

| # | 限制 | 影响 |
|---|------|------|
| L1 | 3 个 FP exemplar 样本量极小 | 不能从 3 个例子断言 IS-11 一定有效 |
| L2 | table_line_detector.py 未在独立语料上测试 | 机器可观测性为理论推断 |
| L3 | 当前无独立 IS-11 evaluation data | 需要新 PDF 或条件性使用 partially-contaminated PDFs |
| L4 | IS-11 定义尚未冻结 | 候选维度 (C1-C9) 需要在实验前确定子集 |
| L5 | TABLE_CELL 仅在 qbio 文档中存在 | 跨文档泛化可能受限 |
| L6 | IS-11 可能退化为 Category C | 如果 table context 仍需 semantic interpretation |

---

## 19. Final Decision — 12 Questions

**Q1: IS-11 到底是什么 Information Source?**
TABLE_CELL_CONTEXT — 观察 text pair 是否位于 table 区域内，以及是否属于同一/不同 cell。核心组件是 cell_membership (C2)。

**Q2: 当前系统是否已经拥有足够的 IS-11 evidence?**
**NO** — 9 个信息组件中 0 个完全可用，6 个完全不可用。table_line_detector.py 存在但未集成到 P1-P6。这是 INTEGRATION GAP + CAPABILITY GAP。

**Q3: Human 为什么依赖 IS-11?**
3/3 FP 中 Human 全部引用 "table"、"different columns"、"separate cells" — table 结构是 Human 区分 "编号+标题" 与 "表格数字+描述" 的关键信息。

**Q4: IS-11 是否可能解释 3 个 TABLE_CELL FP?**
**YES** — 如果 IS-11 检测到 text_a 和 text_b 在不同 cell，协议可将 MERGE 降级。但仅基于 3 个 exemplar，不能断言一定有效。

**Q5: IS-11 是否可能帮助解释 FN / abstention?**
- FN: **NO** — FN 是引用片段，需要 IS-10 (Category C)
- Abstention: **PARTIALLY** — 25/56 abstention 涉及 TABLE_CELL，IS-11 可能帮助

**Q6: IS-11 与 IS-12 / IS-14 的边界在哪里?**
- IS-11 = "是否在 table 语境" (coarse)
- IS-12 = "table 中的行列位置" (fine, IS-11 子组件)
- IS-14 = "文档结构角色" (broader, IS-11 是其特例)

**Q7: IS-11 是否可能独立 machine-observable?**
**PARTIALLY YES** — table_line_detector.py 提供了 table region + cell grid 检测能力。但:
- 未在独立评估语料上测试
- borderless table 检测可能失败 (F2)
- cell_membership 仍可能不足以判断 semantic boundary (F8)

**Q8: 当前是否存在真正 independent IS-11 evaluation data?**
**NO** — Frozen 69-case set 不可用 (contamination)。需要新 PDF 或条件性使用 partially-contaminated PDFs。

**Q9: 如何防止 IS-11 experiment contamination?**
1. IS-11 定义在 GT 收集前冻结
2. GT 在 IS-11 observation 前冻结
3. 不从 69-case GT 反推 IS-11 definition
4. 新 PDF 必须独立 (零 P7 引用)
5. Provenance audit (同 IS-01/IS-02 实验的 9-point audit)

**Q10: 什么结果才足以证明 IS-11 有增量价值?**
- G7 (FP Reduction) PASS: ΔFP < 0 on TABLE_CELL
- G8 (Recall/Coverage Safety) PASS: ΔRecall ≥ 0 AND ΔCoverage ≥ 0
- G5 (Cross-Document) PASS: ≥2 docs
- G11 (Determinism) PASS
- 增量效果在 independent data 上复现

**Q11: 什么结果意味着 IS-11 应该被放弃或转为 Human-owned?**
- FP 增加 (IS-11 制造新 FP)
- 只在单文档有效
- feature 无法稳定提取 (non-deterministic)
- IS-11 退化为 Category C (需要 semantic interpretation)
- F8 (table context insufficient) 普遍出现

**Q12: 下一阶段应该 BUILD / DESIGN EXPERIMENT / MORE DATA / HUMAN-OWNED / STOP?**
- **MORE DATA** — 当前无独立 IS-11 evaluation data，需先获取含表格 PDF
- **DESIGN EXPERIMENT** — 实验设计已完成 (本文档)
- **NOT BUILD** — IS-11 定义尚未冻结，需先确定 C1-C9 子集
- **NOT HUMAN_OWNED** — IS-11 理论上 machine-observable (不同于 IS-10)
- **STOP** — 本阶段设计完成，不进入实现

---

## 20. No Pre-Assumption of Effectiveness

**特别声明**: 不因为 "3 个 FP 全部 TABLE_CELL" 就断言 "IS-11 肯定能解决"。

**正确表述**: "TABLE_CELL_CONTEXT 是当前最值得验证的新增 Information Source hypothesis。"

3 个 FP exemplar 支持 IS-11 的 information hypothesis，但:
- 3 个样本不足以证明稳定性
- IS-11 可能存在 F8 (table context insufficient)
- table_line_detector.py 未在独立语料上测试
- 需要独立实验验证

---

## 21. Final Status

```
DESIGN_STATUS = READY
IS-11 = HYPOTHESIS ONLY
IMPLEMENTATION = NOT AUTHORIZED
P7.3 = NOT AUTHORIZED
P4 = FROZEN
IS-01 = FROZEN
IS-02 = FROZEN
69-CASE EVALUATION = FROZEN
SEMANTIC GT = FROZEN
FROZEN BASELINE = INTACT
STOP = TRUE
```

---

## STOP

设计完成。不实现 IS-11。不运行 IS-11。不修改实验。不修改规则。不进入 P7.3。

**输出**:
- IS-11 Experiment Design (本文档)
- IS-11 Information Availability Matrix (`is11_table_cell_context_information_matrix.json`)
- IS-11 Experiment Matrix (`is11_table_cell_context_experiment_matrix.json`)
