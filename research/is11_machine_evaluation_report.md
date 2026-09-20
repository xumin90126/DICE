# IS-11 Stage 4: Machine Evaluation Report

## STAGE 4 — COMPLETE

| 字段 | 值 |
|------|-----|
| 阶段 | Stage 4 — IS-11 Machine Evaluation |
| 约束 | ONE NEW INFORMATION SOURCE (IS-11 only), no P1-P6 modification, no P7.3 |
| INTEGRITY PRE-GATE | ✅ PASS |
| BASELINE_A | COMPLETE |
| BASELINE_B | COMPLETE |
| EXPERIMENTAL_C | COMPLETE |
| G7 (FP Reduction) | ❌ FAIL |
| G8 (Recall/Coverage Safety) | ✅ PASS |
| CROSS_DOCUMENT_STABILITY | NOT_ESTABLISHED |
| DETERMINISM | ✅ PASS |
| FROZEN BASELINE | INTACT ✅ |
| IS-11 | EXPERIMENTALLY EVALUATED |
| P7.3 | NOT AUTHORIZED |
| STOP | TRUE |

---

## 1. Dataset

| 字段 | 值 |
|------|-----|
| Independent PDFs | 4 |
| Candidate Universe | 545 AMBIGUOUS cases |
| Sampling Frame | 45 cases (seed=20240909) |
| Semantic GT | 45 cases (FROZEN) |

## 2. GT Distribution

| Label | Count |
|-------|-------|
| MERGE | 2 |
| KEEP_SEPARATE | 43 |

---

## 3. Three Conditions

### Baseline A — Geometry Only

| 指标 | 值 |
|------|-----|
| TP | 0 |
| FP | 0 |
| FN | 0 |
| TN | 0 |
| ABSTAIN | 45 |
| Precision | 0.0 |
| Recall | 0.0 |
| Coverage | 0.0% |
| Abstention | 100% |

**说明**: 所有 45 个 case 都是 AMBIGUOUS 状态（几何无法判定），Baseline A 全部弃权。

### Baseline B — Geometry + IS-01 + IS-02

| 指标 | 值 |
|------|-----|
| TP | 0 |
| FP | 1 |
| FN | 0 |
| TN | 18 |
| ABSTAIN | 26 |
| Precision | 0.0 |
| Recall | 0.0 |
| Coverage | 42.2% |
| Abstention | 57.8% |

**说明**: 使用冻结 §9.3 协议 (IS-01_a ∧ IS-02_b → MERGE; ¬IS-01_a ∧ ¬IS-02_b → KEEP_SEPARATE; 否则 INSUFFICIENT_EVIDENCE)。

### Experimental C — Geometry + IS-01 + IS-02 + IS-11

| 指标 | 值 |
|------|-----|
| TP | 0 |
| FP | 1 |
| FN | 0 |
| TN | 26 |
| ABSTAIN | 18 |
| Precision | 0.0 |
| Recall | 0.0 |
| Coverage | 60.0% |
| Abstention | 40.0% |

**说明**: 在 Baseline B 基础上增加 IS-11 TABLE_CELL_CONTEXT 实验性观察。IS-11 通过 table_line_detector 检测表格区域和 cell membership，对检测到 different_cell 的 case 判 KEEP_SEPARATE，对 same_cell 的 case 判 MERGE。

---

## 4. Incremental Effect (C vs B)

| 指标 | Baseline B | Experimental C | Δ (C - B) |
|------|-----------|---------------|-----------|
| FP | 1 | 1 | **0** |
| Recall | 0.0 | 0.0 | **0.0** |
| Coverage | 42.2% | 60.0% | **+17.8%** |
| Precision | 0.0 | 0.0 | **0.0** |
| TN | 18 | 26 | **+8** |
| ABSTAIN | 26 | 18 | **-8** |

**核心发现**: IS-11 将 8 个 INSUFFICIENT_EVIDENCE case 正确解析为 KEEP_SEPARATE (GT 全部为 KEEP_SEPARATE)，覆盖率从 42.2% 提升到 60.0%。但 IS-11 **未能减少 FP**（ΔFP=0），因为唯一的 FP case (IS11-AMB-135) 不在检测到的表格区域内。

---

## 5. Pre-Registered Gates

### G7 — FP Reduction (PRIMARY)

| 字段 | 值 |
|------|-----|
| 预注册定义 | ΔFP < 0 |
| 实际值 | ΔFP = 0 |
| 结果 | **❌ FAIL** |

**原因**: FP_B=1, FP_C=1。IS-11 未减少 FP，因为唯一的 FP case (IS11-AMB-135: "4" / "MBConv6, k5x5") 在 EfficientNet p5 上，table_line_detector 未检测到该页面的表格（in_table=False），IS-11 无法提供 cell context 信息。

### G8 — Recall / Coverage Safety

| 字段 | 值 |
|------|-----|
| 预注册定义 | ΔRecall ≥ 0 AND ΔCoverage ≥ 0 |
| 实际值 | ΔRecall=0.0, ΔCoverage=+0.1778 |
| 结果 | **✅ PASS** |

---

## 6. Cross-Document Stability

| 文档 | n | GT MERGE | GT KEEP | B: FP | B: TN | B: ABSTAIN | C: FP | C: TN | C: ABSTAIN | ΔFP |
|------|---|---------|---------|-------|-------|------------|-------|-------|------------|-----|
| is11_resnet | 9 | 0 | 9 | 0 | 5 | 4 | 0 | 9 | 0 | 0 |
| is11_efficientnet | 18 | 0 | 18 | 1 | 12 | 5 | 1 | 14 | 3 | 0 |
| is11_med_001 | 8 | 2 | 6 | 0 | 0 | 8 | 0 | 0 | 8 | 0 |
| is11_cs_001 | 10 | 0 | 10 | 0 | 1 | 9 | 0 | 3 | 7 | 0 |

| 指标 | 值 |
|------|-----|
| Documents with FP reduction | 0/4 |
| Cross-document stability | **NOT_ESTABLISHED** |

**说明**: IS-11 在 0/4 文档中减少了 FP。覆盖率在 3/4 文档中有提升 (resnet: 4→0 abstain, efficientnet: 5→3, cs_001: 9→7)，但 med_001 无变化 (8→8 abstain)。med_001 的 2 个 MERGE GT case 都是 figure captions，不在表格区域，IS-11 无法提供帮助。

---

## 7. Determinism

| 指标 | 值 |
|------|-----|
| Run 1 vs Run 2 mismatches | 0 |
| Determinism | **✅ PASS** |

---

## 8. Case-Level Differences (C vs B)

共 **8 个 case** 在 C 和 B 之间存在决策差异，全部为 INSUFFICIENT_EVIDENCE → KEEP_SEPARATE：

| case_id | 文档 | B 决策 | C 决策 | GT | IS-11 in_table | IS-11 different_cell | 正确? |
|---------|------|--------|--------|-----|----------------|---------------------|-------|
| IS11-AMB-005 | resnet p1 | INSUFFICIENT_EVIDENCE | KEEP_SEPARATE | KEEP_SEPARATE | True | True | ✅ |
| IS11-AMB-024 | resnet p6 | INSUFFICIENT_EVIDENCE | KEEP_SEPARATE | KEEP_SEPARATE | True | True | ✅ |
| IS11-AMB-034 | resnet p6 | INSUFFICIENT_EVIDENCE | KEEP_SEPARATE | KEEP_SEPARATE | True | True | ✅ |
| IS11-AMB-074 | resnet p8 | INSUFFICIENT_EVIDENCE | KEEP_SEPARATE | KEEP_SEPARATE | True | True | ✅ |
| IS11-AMB-346 | efficientnet p9 | INSUFFICIENT_EVIDENCE | KEEP_SEPARATE | KEEP_SEPARATE | True | True | ✅ |
| IS11-AMB-350 | efficientnet p9 | INSUFFICIENT_EVIDENCE | KEEP_SEPARATE | KEEP_SEPARATE | True | True | ✅ |
| IS11-AMB-522 | cs_001 p4 | INSUFFICIENT_EVIDENCE | KEEP_SEPARATE | KEEP_SEPARATE | True | True | ✅ |
| IS11-AMB-530 | cs_001 p5 | INSUFFICIENT_EVIDENCE | KEEP_SEPARATE | KEEP_SEPARATE | True | True | ✅ |

**全部 8 个差异均为正确解析** (GT=KEEP_SEPARATE, C=KEEP_SEPARATE)。

---

## 9. Failure Analysis

### FP Cases (1)

| case_id | text_a | text_b | 文档 | IS-11 in_table | 原因 |
|---------|--------|--------|------|----------------|------|
| IS11-AMB-135 | "4" | "MBConv6, k5x5" | efficientnet p5 | False | table_line_detector 未检测到该页表格，IS-11 无法提供 cell context。IS-01_a=True ("4" 匹配数字模式) + IS-02_b=True ("MBConv6" 含 >2 alpha chars) → Baseline B 误判 MERGE。IS-11 因 table 未检测到无法纠正。 |

### FN Cases (0)

无 FN case。GT 中 2 个 MERGE case (IS11-AMB-414, IS11-AMB-422) 均为 figure captions (med_001)，不在表格区域，IS-11 和 Baseline B 均判 INSUFFICIENT_EVIDENCE (ABSTAIN)，不是 FN (machine ≠ MERGE 但 machine 也 ≠ KEEP_SEPARATE)。

### 未解析 ABSTAIN (18 cases in C)

- 10 个 med_001 case: table_line_detector 未检测到表格 (figure captions, axis labels, diagram items)
- 5 个 efficientnet case: table_line_detector 未检测到表格 (p5-p8 的表格)
- 3 个 cs_001 case: 候选 bbox 不在检测到的表格 cell 内

---

## 10. Frozen Baseline

| 检查项 | 结果 |
|--------|------|
| P7.1 drift | ✅ 0 |
| P7.2 drift | ✅ 0 |
| P4 SpanConfig | ✅ UNCHANGED |
| P1-P6 table_line_detector imports | ✅ 0 (仅 SHA hash 引用) |
| IS-11 in perception/ | ✅ NOT INTEGRATED |
| Semantic GT | ✅ FROZEN (45 cases, 2 MERGE, 43 KEEP_SEPARATE) |
| GT SHA-256 | 7349963d0d23b5efc8c092ad45b8f301c39ca13a9c3bef8952aff809d0286959 |

---

## 11. 研究结论

### Gate 结果

```
G7 (FP Reduction)   = FAIL  (ΔFP = 0, not < 0)
G8 (Recall/Coverage) = PASS  (ΔRecall = 0 ≥ 0, ΔCoverage = +0.1778 ≥ 0)
```

### 结论

> **IS-11 does not demonstrate the preregistered FP-reduction value.**

IS-11 (TABLE_CELL_CONTEXT) 在当前实验条件下：

1. **覆盖率提升**: ΔCoverage = +17.8% (42.2% → 60.0%)，正确解析了 8 个 ambiguous case
2. **无 FP 减少**: ΔFP = 0，唯一 FP case 不在检测到的表格区域
3. **无 Recall 提升**: ΔRecall = 0，GT 中 2 个 MERGE case 均为 figure captions (非表格区域)
4. **Cross-document stability NOT ESTABLISHED**: 0/4 文档减少 FP

### 失败原因分析

IS-11 的 FP 减少能力受限于：
- **table_line_detector 覆盖率不足**: 32/45 (71.1%) 的 case 未检测到表格区域
- **FP case 恰好在未检测到表格的页面**: IS11-AMB-135 (efficientnet p5) 的 table_line_detector 未检测到表格
- **MERGE GT case 不在表格区域**: 2 个 MERGE GT 均为 figure captions，IS-11 无法提供增量信息

### 根据 §23 研究结论规则

```
G7 = FAIL
→ IS-11 does not demonstrate the preregistered FP-reduction value
```

即使 G8 PASS (覆盖率安全)，**G7 FAIL 意味着 IS-11 未通过预注册的 PRIMARY gate**。

---

## 12. 最终状态

```
STAGE_4 = COMPLETE

BASELINE_A = COMPLETE
BASELINE_B = COMPLETE
EXPERIMENTAL_C = COMPLETE

G7 (FP Reduction) = FAIL
G8 (Recall/Coverage Safety) = PASS

CROSS_DOCUMENT_STABILITY = NOT_ESTABLISHED
DETERMINISM = PASS

FROZEN BASELINE = INTACT

IS-11 = EXPERIMENTALLY EVALUATED
IS-11 does not demonstrate the preregistered FP-reduction value

P7.3 = NOT AUTHORIZED
PRODUCTION = FALSE
RUNTIME = NOT AUTHORIZED
CAPABILITY REGISTRATION = NOT AUTHORIZED

NEXT AUTHORIZED ACTION = WAIT FOR EXPLICIT AUTHORIZATION

STOP = TRUE
```

---

## 输出文件

| 文件 | 路径 | 大小 |
|------|------|------|
| Machine Evaluation Results | `tmp/is11_machine_evaluation_results.json` | 63,889 bytes |
| Machine Evaluation Metrics | `tmp/is11_machine_evaluation_metrics.json` | 5,472 bytes |
| Machine Evaluation Report | `tmp/is11_machine_evaluation_report.md` | (this file) |
| Machine Evaluation Provenance | `tmp/is11_machine_evaluation_provenance.json` | — |
| Machine Evaluation Determinism | `tmp/is11_machine_evaluation_determinism.json` | — |
| Evaluation Script | `tmp/is11_machine_evaluation.py` | — |

---

## STOP

Stage 4 Machine Evaluation 完成。三个条件 (A/B/C) 全部运行完成。预注册 Gates 已评估。Frozen Baseline 完整。不进入 P7.3。不进入 Production。等待下一次授权。
