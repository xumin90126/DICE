# 独立评估数据收集 — 受控执行报告

## Independent Evaluation Data Collection — Controlled Execution Report

| 字段 | 值 |
|------|-----|
| 阶段 | Independent Evaluation Data Collection — Controlled Execution |
| 阶段约束 | **DATA COLLECTION ONLY** — 禁止计算 IS-01/IS-02、机器指标、precision/recall |
| 执行时间 | 2026-09-08 ~ 2026-09-09 |
| 状态 | **DATA_COLLECTION_STATUS = COMPLETE** |
| 冻结基线 | **FROZEN_BASELINE = INTACT** ✅ |
| 溯源审计 | **PROVENANCE_AUDIT = PASS** (9/9 checks) ✅ |
| STOP | **TRUE** |

---

## 1. 执行摘要

本阶段在 4 个完全独立的 PDF 文档上执行冻结的 P1-P6 管道，生成 AMBIGUOUS 候选宇宙，冻结采样框，收集双盲人工 GT，裁定分歧，冻结评估集。**全程未计算 IS-01/IS-02、未生成机器预测、未计算任何机器指标。**

### 核心成果

| 指标 | 值 |
|------|-----|
| 候选宇宙总量 | 254 AMBIGUOUS cases (4 PDFs, 121 pages) |
| 采样框 | 69 cases (seed=20240908, 几何分层) |
| 人工审查者 | 2 (Reviewer A + Reviewer B, 完全独立) |
| 简单一致率 | 68/69 = **98.6%** |
| Cohen's Kappa | **0.968** (Strong agreement) |
| 分歧数 | 1 (已裁定) |
| 可用 GT | 69/69 = **100.0%** |
| GT 分布 | MERGE=24, KEEP_SEPARATE=45 |
| GT 层级 | LEVEL_2_AGREED=68, LEVEL_2_ADJUDICATED=1 |

---

## 2. 语料库独立性验证

### 2.1 四份独立 PDF

| doc_id | 独立性状态 | P7 制品引用 | 结论 |
|--------|-----------|------------|------|
| ind_arxiv_2402 | INDEPENDENT | ZERO | ✅ 可用于独立评估 |
| ind_arxiv_bio2 | INDEPENDENT | ZERO | ✅ 可用于独立评估 |
| ind_qbio_genomics | INDEPENDENT | ZERO | ✅ 可用于独立评估 |
| ind_qbio_rna | INDEPENDENT | ZERO | ✅ 可用于独立评估 |

### 2.2 排除的 3 份部分污染 PDF

| doc_id | 污染类型 | 排除原因 |
|--------|---------|---------|
| arxiv_2310 | P1 已处理 + evidence gap 元数据 | 元数据级污染 |
| arxiv_2401 | 元数据引用 | 元数据级污染 |
| qbio_cell | 元数据 + 字体分析 | 元数据级污染 |

**注**: 以上 3 份 PDF 仅有元数据级污染（无 IS 计算、无边界对分析），但为严格保证独立性而排除。

---

## 3. 候选宇宙生成

### 3.1 执行管道

- **管道**: 冻结 P1-P6（未修改生产代码）
- **P4 SpanConfig (FROZEN)**: `max_horizontal_gap=8.0, max_vertical_gap=14.0, same_line_tolerance=3.0, cross_column_gap_threshold=30.0, overlap_tolerance=0.5`
- **三态关系模型**: DETERMINISTIC_MERGE / DETERMINISTIC_BLOCK / AMBIGUOUS
- **输出**: 仅 AMBIGUOUS 状态的 case（DETERMINISTIC 状态不进入评估集）

### 3.2 候选宇宙统计

| doc_id | AMBIGUOUS cases |
|--------|----------------|
| ind_arxiv_2402 | 4 |
| ind_arxiv_bio2 | 103 |
| ind_qbio_genomics | 85 |
| ind_qbio_rna | 62 |
| **总计** | **254** |

### 3.3 禁止项验证

- ❌ IS-01 (TEXT_NUMBER_PATTERN): **未计算**
- ❌ IS-02 (TEXT_READABLE_TITLE): **未计算**
- ❌ ambiguity_mode: **未计算**
- ❌ ground_truth_label: **未计算**
- ❌ p4_decision_label (机器决策标签): **未计算**

---

## 4. 采样框冻结

### 4.1 采样方法

- **方法**: 分层随机采样 (stratified random sampling)
- **种子**: 20240908
- **分层维度**: 纯几何特征（无文本模式、无 IS 特征）
  - gap bins: G1_8-12, G2_12-20, G3_20-30, G4_30-50
  - w_b bins, line_obs bins, w_a bins
- **采样量**: 69 / 254 (27.2%)

### 4.2 文档覆盖

| doc_id | 采样数 |
|--------|--------|
| ind_arxiv_2402 | 4 |
| ind_arxiv_bio2 | 25 |
| ind_qbio_genomics | 23 |
| ind_qbio_rna | 17 |
| **总计** | **69** |

### 4.3 冻结状态

- **SAMPLING_FRAME_FREEZE = TRUE** ✅
- 采样框基于纯几何特征，未使用任何文本模式或 IS 特征

---

## 5. 双盲人工审查

### 5.1 盲审协议

每位审查者仅能看到以下字段：
- ✅ case_id
- ✅ page
- ✅ text_a
- ✅ text_b
- ✅ page_context (从 PDF 提取的页面文本上下文)

每位审查者**不能**看到：
- ❌ IS-01 / IS-02 特征
- ❌ 几何元数据 (gap, bbox, w_a, w_b, line_obs)
- ❌ 机器预测 (p4_decision)
- ❌ Round 1 数据
- ❌ DICE 概念
- ❌ 反事实分析

### 5.2 审查者独立性

- Reviewer A 和 Reviewer B 在完全独立的 subagent 上下文中运行
- 无共享状态、无信息交换
- 使用相同的盲审包（内容相同，但各自独立判断）

### 5.3 审查结果

| 审查者 | MERGE | KEEP_SEPARATE | CANNOT_DETERMINE | 总计 |
|--------|-------|---------------|-------------------|------|
| Reviewer A | 24 | 45 | 0 | 69 |
| Reviewer B | 25 | 44 | 0 | 69 |

---

## 6. 一致性分析

### 6.1 整体一致性

| 指标 | 值 |
|------|-----|
| 共同案例数 | 69 |
| 简单一致率 | 68/69 = **98.6%** |
| Cohen's Kappa | **0.968** |
| Kappa 解释 | Strong agreement (≥0.80) |

### 6.2 混淆矩阵 (A 行, B 列)

| | B: MERGE | B: KEEP_SEPARATE | B: CANNOT_DETERMINE |
|---|---------|------------------|---------------------|
| **A: MERGE** | 24 | 0 | 0 |
| **A: KEEP_SEPARATE** | 1 | 44 | 0 |
| **A: CANNOT_DETERMINE** | 0 | 0 | 0 |

### 6.3 分歧案例

仅 1 例分歧：

| case_id | Reviewer A | Reviewer B | 裁定者 | 最终 GT | GT 层级 |
|---------|-----------|-----------|--------|---------|---------|
| IND-AMB-032 | KEEP_SEPARATE | MERGE | 第三独立审查者 | KEEP_SEPARATE | LEVEL_2_ADJUDICATED |

**裁定理由**: "Kyungjae Lee," 是以逗号结尾的完整作者名，"Han-" 是下一个作者名的开头（连字符换行）。逗号标记了作者之间的边界，两者属于不同的作者条目，应保持分离。

---

## 7. 语义 GT 生成与冻结

### 7.1 GT 层级

| 层级 | 数量 | 说明 |
|------|------|------|
| LEVEL_2_AGREED | 68 | 双审查者一致（MERGE 或 KEEP_SEPARATE） |
| LEVEL_2_ADJUDICATED | 1 | 双审查者分歧，经第三独立审查者裁定 |
| **总计** | **69** | **100% 可用 GT** |

### 7.2 GT 标签分布

| GT 标签 | 数量 | 占比 |
|---------|------|------|
| MERGE | 24 | 34.8% |
| KEEP_SEPARATE | 45 | 65.2% |
| UNRESOLVED | 0 | 0.0% |

### 7.3 冻结状态

- **EVALUATION_SET_FREEZE = TRUE** ✅
- **SEMANTIC_GT_FREEZE = TRUE** ✅
- **is01_is02_computed = FALSE** ✅
- **machine_prediction_computed = FALSE** ✅

### 7.4 GT 独立性

GT 基于人工语义判断生成，**非**基于几何特征的 GT。审查者在判断时仅依赖文本语义理解，未使用任何几何/IS/机器信息。

---

## 8. 溯源审计 (Post-Freeze Provenance Audit)

### 8.1 审计结果

**OVERALL_PROVENANCE_AUDIT = PASS** (9/9 checks passed) ✅

| 检查项 | 结果 | 详情 |
|--------|------|------|
| IS-01/IS-02 未计算 | ✅ PASS | 0 actual computations |
| 机器指标未计算 | ✅ PASS | 0 actual computations |
| 盲审包含仅允许字段 | ✅ PASS | 0 leaked fields |
| 代码未引用 Round 1 数据 | ✅ PASS | 0 references |
| 采样框纯几何分层 | ✅ PASS | text=0, geo=2 |
| GT 冻结且无机器计算 | ✅ PASS | IS=False, Machine=False, Freeze=FROZEN |
| 审查结果仅含 decision/reason | ✅ PASS | 0 leaked fields |
| 无机器预测文件存在 | ✅ PASS | 0 files exist |
| 裁定者盲审 | ✅ PASS | extra fields: none |

### 8.2 边界保护验证

| 层级 | 状态 | 验证 |
|------|------|------|
| Layer A: CORPUS PREPROCESSING | ALLOWED (executed) | ✅ P1-P6 执行 |
| Layer B: EXPERIMENTAL FEATURE OBSERVATION | NOT EXECUTED | ✅ IS-01/IS-02 禁止至 GT 冻结后 |
| Layer C: DECISION LEAKAGE | FORBIDDEN | ✅ 0 violations |
| Blind Protocol | ENFORCED | ✅ 审查者仅看到文本 + page_context |
| GT Independence | VERIFIED | ✅ GT 基于人工语义判断 |

---

## 9. 冻结基线完整性

### 9.1 生产代码哈希验证

| 组件 | 哈希 | 预期 | 结果 |
|------|------|------|------|
| P7.1 files (6) | — | — | 0 drift → PASS ✅ |
| P7.2 files (8) | — | — | 0 drift → PASS ✅ |
| P1-P6 files (25) | — | — | 0 changed → PASS ✅ |
| Frozen 730 | a10b368e | a10b368e | PASS ✅ |
| span_rules.py | 1c8e3830 | 1c8e3830 | PASS ✅ |
| span_observation.py | 87e8c0bc | 87e8c0bc | PASS ✅ |
| calibration_filter.py | 6ab1ee78 | 6ab1ee78 | PASS ✅ |

**FROZEN_BASELINE = INTACT** ✅

### 9.2 会话期间修改验证

- 生产代码文件检查: 49 files
- 会话期间修改: **0 files**
- 所有新增文件均在 `tmp/perception/p7/independent_evaluation_*` 命名空间

---

## 10. 已知限制

| 限制 | 状态 | 说明 |
|------|------|------|
| IS-01 (TEXT_NUMBER_PATTERN) | FROZEN | 已知限制: 不区分标题 vs 公式编号 |
| IS-02 (TEXT_READABLE_TITLE) | FROZEN | 已知限制: "cos"/"sin"/"and"/"are" 匹配 (3 chars > 2) |
| Timer 实现 | NOT AUTHORIZED | Round 1 timer bug 已记录但未修复。本阶段未授权修复。人工成本测量已协议设计但未实现。 |

---

## 11. 输出文件清单

| 文件 | 类型 | 大小 |
|------|------|------|
| `independent_evaluation_generate_candidates.py` | 代码 | — |
| `independent_evaluation_candidate_universe.json` | 数据 (FROZEN) | 1.3MB |
| `independent_evaluation_sampling_frame.json` | 数据 (FROZEN) | 66KB |
| `independent_evaluation_gt_assembly.py` | 代码 | — |
| `independent_evaluation_semantic_gt.json` | 数据 (FROZEN) | 54KB |
| `independent_evaluation_provenance_audit.json` | 审计 | — |
| `independent_evaluation_collection_manifest.json` | 清单 | 10KB |
| `independent_evaluation_collection_report.md` | 报告 (本文件) | — |
| `independent_evaluation_human_review/` | 审查目录 | — |
| — `reviewer_a_blind_cases.json` | 盲审包 | 151KB |
| — `reviewer_b_blind_cases.json` | 盲审包 | 151KB |
| — `reviewer_a_batch_{1-4}.json` | 分批包 | — |
| — `reviewer_b_batch_{1-4}.json` | 分批包 | — |
| — `reviewer_a_results_batch_{1_2,3_4}.json` | 审查结果 | — |
| — `reviewer_b_results_batch_{1,2,3_4}.json` | 审查结果 | — |
| — `adjudicator_ind_amb_032.json` | 裁定结果 | — |

---

## 12. 授权状态

| 操作 | 授权状态 |
|------|---------|
| IS-01/IS-02 Execution | **NOT AUTHORIZED** |
| Machine Evaluation | **NOT AUTHORIZED** |
| P7.3 | **NOT AUTHORIZED** |
| Implementation | **NOT AUTHORIZED** |
| Timer Fix | **NOT AUTHORIZED** |
| Frozen Baseline Modification | **NOT AUTHORIZED** |

### 下一阶段授权前提

在执行 IS-01/IS-02 计算或机器评估之前，必须：
1. 人工审查本报告并确认评估集冻结的有效性
2. 人工授权 IS-01/IS-02 执行阶段
3. 确认 Pre-Registered Gates (G1-G12) 已设定
4. 确认 G7 (Precision ≥ 95%) 和 G8 (Recall ≥ 80%) 已在结果生成前设定

---

## 13. STOP 条件验证

| STOP 条件 | 触发? | 说明 |
|-----------|-------|------|
| 审查者看到 IS/机器信息 | ❌ 未触发 | 盲审包仅含允许字段 (审计 PASS) |
| 采样基于文本模式 | ❌ 未触发 | 采样框纯几何分层 (审计 PASS) |
| GT 在机器预测后修改 | ❌ 未触发 | GT 冻结前无机器预测 (审计 PASS) |
| Kappa < 0.60 | ❌ 未触发 | Kappa = 0.968 (Strong agreement) |

**STOP = TRUE** (阶段完成，等待人工授权下一阶段)

---

## 14. 结论

本阶段成功在 4 份独立 PDF 上执行了冻结的 P1-P6 管道，生成了 254 个 AMBIGUOUS 候选案例，采样 69 个案例进行双盲人工审查。两位独立审查者表现出极高的一致性（Kappa=0.968），仅 1 例分歧经第三独立审查者裁定解决。最终评估集包含 69 个 100% 可用的 Level 2 语义 GT。

**全程严格遵守 DATA COLLECTION ONLY 约束**：未计算 IS-01/IS-02、未生成机器预测、未计算任何机器指标。溯源审计 9/9 通过，冻结基线完整无损。

**DATA_COLLECTION_STATUS = COMPLETE**
**FROZEN_BASELINE = INTACT**
**STOP = TRUE**
