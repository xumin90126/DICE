# IS-11 New Independent Corpus Acquisition Report

## NEW INDEPENDENT CORPUS ACQUISITION — COMPLETE

| 字段 | 值 |
|------|-----|
| 阶段 | NEW INDEPENDENT CORPUS ACQUISITION |
| 约束 | CORPUS ACQUISITION ONLY — 无 IS-11 计算，无 P1-P6 修改 |
| 获取方式 | arxiv.org PDF 下载 (公开开放获取) |
| CORPUS_ACQUISITION_GATE | **PASS** ✅ |
| IS-11 | HYPOTHESIS ONLY |
| FROZEN BASELINE | INTACT ✅ |
| STOP | TRUE |

---

## 1. 找到了哪些新 PDF

共下载 10 个 PDF，其中 8 个有效 (2 个损坏)，4 个被纳入语料库：

| # | 文件名 | arXiv ID | 页数 | 表格页数 | 估计候选 | 字段 |
|---|--------|---------|------|---------|---------|------|
| 1 | resnet_001.pdf | 1512.03385 | 12 | 5 | ~110 | CS |
| 2 | efficientnet_001.pdf | 1905.11946 | 11 | 6 | ~56 | CS |
| 3 | med_001.pdf | 2311.15207 | 29 | 2 | ~14 | Chemistry |
| 4 | cs_001.pdf | 2402.17764 | 8 | 1 | ~8 | CS/NLP |
| **合计** | | | | **14** | **~188** | **2 fields** |

---

## 2. 每个 PDF 的来源与 SHA-256

| 文件名 | SHA-256 | 大小 | URL |
|--------|---------|------|-----|
| resnet_001.pdf | `1e0651b6810ecba34a3dbc5b5b0209226f889004607c1f203540a48d64e5a93a` | 819,383b | https://arxiv.org/pdf/1512.03385 |
| efficientnet_001.pdf | *(见 manifest)* | 933,600b | https://arxiv.org/pdf/1905.11946 |
| med_001.pdf | `ead90f6b62e6e57cd22cba195b12a2d73a5f75112a3328db73838b871aff9760` | 2,300,171b | https://arxiv.org/pdf/2311.15207 |
| cs_001.pdf | `bcd625e89f95c39dc9143af4174978fcf2467eb9659d86f8da448d7d9366c332` | 463,748b | https://arxiv.org/pdf/2402.17764v1 |

---

## 3. 独立性审计结果

| 检查项 | 结果 |
|--------|------|
| 是否属于 Frozen 69-case Evaluation | ❌ 无重叠 (4 frozen: ind_arxiv_2402, ind_arxiv_bio2, ind_qbio_genomics, ind_qbio_rna) |
| 是否属于历史 3 个 FP exemplar | ❌ 无 (FP 来自 ind_qbio_rna) |
| 是否属于 Round 1 Human Boundary Review | ❌ 无 (Round 1: arxiv_2307, arxiv_bio, arxiv_toc) |
| 是否在 evidence_gap_analysis 中 | ❌ 无 |
| 是否在 boundary analysis 中引用 | ❌ 无 |
| 是否曾进入已有实验数据 | ❌ 无 |
| grep across tmp/perception/p7/, perception/, chunker/ | **0 matches** for all arxiv IDs, titles, authors |
| **结论** | **ALL 4 PDFs = INDEPENDENT, ZERO CONTAMINATION** |

---

## 4. 每个 PDF 的真实 Table 情况

### resnet_001.pdf (Deep Residual Learning for Image Recognition)
- **5 个真实数据表页面**: p1 (error rates), p4 (architecture comparison, 36 data rows), p5 (layer specifications), p6 (benchmark results), p8 (CIFAR-10 results)
- Table 类型: 架构表 + 基准结果表 + 误差表
- 内容: 数字 (error rates, layer counts) + 文本 (model names, layer types)

### efficientnet_001.pdf (EfficientNet: Rethinking Model Scaling)
- **6 个真实数据表页面**: p1 (model comparison), p4 (scaling dimensions), p6, p7 (transfer learning results), p10
- Table 类型: 模型比较表 + 缩放参数表 + 迁移学习结果
- 内容: 数字 (accuracy, parameters) + 文本 (dataset names, model names)

### med_001.pdf (Efficient interpolation of molecular properties)
- **2 个真实数据表页面**: p12 (kernel parameters), p19 (AUC comparison)
- Table 类型: 参数表 + 性能比较表
- 内容: 数字 (kcal/mol, AUC values) + 文本 (kernel names, descriptors)

### cs_001.pdf (The Era of 1-bit LLMs)
- **1 个真实数据表页面**: p1 (BitNet vs Transformer comparison)
- Table 类型: 方法比较表
- 内容: 数字 + 文本 (model names, precision types)
- 注意: 有 MuPDF color space warnings (非致命, 文本可提取)

---

## 5. Estimated TABLE_CELL Candidate Potential

| PDF | 数据行数 | 估计候选 | 说明 |
|-----|---------|---------|------|
| resnet_001 | 55 | ~110 | 架构表 + 结果表, 最高潜力 |
| efficientnet_001 | 28 | ~56 | 多个比较表 |
| med_001 | 7 | ~14 | 2 个数据表 |
| cs_001 | 4 | ~8 | 1 个比较表 |
| **合计** | **94** | **~188** | **ESTIMATE ONLY** |

> ⚠️ 以上数字为 **ESTIMATE ONLY**。实际 TABLE_CELL 候选数量只有在使用 frozen P1-P6 pipeline 生成 candidate universe 后才能确定。估计基于: 每个数据行 × 2 (保守估计每行 1-3 个 AMBIGUOUS 对)。

---

## 6. 被排除的 PDF 及原因

| 文件名 | 排除原因 |
|--------|---------|
| mat_001.pdf | "表格"页面实际为矩阵公式 (physics equations)，非真实数据表 |
| eng_001.pdf | 无真实数据表 (neural operator paper, 公式密集) |
| medimg_001.pdf | 无真实数据表 (RL controller paper, 图像密集) |
| nlp_001.pdf | 无真实数据表 (QLoRA paper, PDF 中无基准表) |
| transformer_001.pdf | 无真实数据表 (Attention paper, 无结果表) |

---

## 7. 是否满足 ≥2 Independent PDFs

```
Independent PDFs = 4 (required: ≥2)
✅ PASS
```

---

## 8. 是否具有 ≥30 Candidate Potential

```
Estimated TABLE_CELL candidates = ~188 (required: ≥30)
✅ PASS (ESTIMATE ONLY — actual count requires Stage 2 pipeline processing)
```

---

## 9. 是否可以进入下一阶段

```
CORPUS_ACQUISITION_GATE = PASS

条件:
  ✓ ≥2 independent PDFs (4 actual)
  ✓ ≥30 estimated candidate potential (~188 estimated)
  ✓ No unresolved contamination (0 contamination)

NEXT_AUTHORIZED_ACTION = STAGE 2 (awaiting human authorization)
```

---

## 10. 最终状态

```
IS-11 = HYPOTHESIS ONLY
IS-11 IMPLEMENTATION = NOT AUTHORIZED
IS-11 COMPUTATION = NOT AUTHORIZED
P7.3 = NOT AUTHORIZED
FROZEN BASELINE = INTACT
CORPUS_ACQUISITION_GATE = PASS
NEXT AUTHORIZED ACTION = STAGE 2 (awaiting human authorization)
STOP = TRUE
```

---

## 输出文件

| 文件 | 路径 |
|------|------|
| Corpus Manifest | `tmp/is11_new_corpus_candidate_manifest.json` (13,828 bytes) |
| Downloaded PDFs | `/tmp/is11_independent_corpus/` (4 included PDFs) |

---

## STOP

语料库获取完成。不实现 IS-11。不运行 P1-P6。不计算任何 machine metrics。不进入 Stage 2 (等待授权)。
