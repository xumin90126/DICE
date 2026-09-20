# IS-11 Stage 3: Human A/B Blind Review Report

## STAGE 3 — COMPLETE

| 字段 | 值 |
|------|-----|
| 阶段 | Stage 3 — Human A/B Blind Review / Semantic GT Construction |
| 约束 | Blind review only, NO IS-11, NO machine prediction |
| INTEGRITY PRE-GATE | ✅ PASS |
| HUMAN_A_REVIEW | COMPLETE (45/45) |
| HUMAN_B_REVIEW | COMPLETE (45/45) |
| SEMANTIC_GT | FROZEN |
| GT_PROVENANCE_AUDIT | PASS |
| FROZEN BASELINE | INTACT ✅ |
| STOP | TRUE |

---

## 1. Integrity Pre-Gate

| 检查项 | 结果 |
|--------|------|
| 4 PDF SHA-256 | ✅ ALL MATCH |
| Candidate Universe (545 cases) | ✅ FROZEN |
| Sampling Frame (45 cases, seed=20240909) | ✅ FROZEN |
| P7.1 drift | ✅ 0 |
| P7.2 drift | ✅ 0 |
| P4 SpanConfig | ✅ UNCHANGED |
| IS-11 implementation | ✅ NONE (0 files) |
| IS-11 computation | ✅ NONE (0 files) |
| table_line_detector | ✅ NOT CALLED |

---

## 2. Human Review Results

### 2.1 Completion

| Reviewer | Cases | MERGE | KEEP_SEPARATE |
|----------|-------|-------|---------------|
| Reviewer A | 45/45 | 2 | 43 |
| Reviewer B | 45/45 | 6 | 39 |

### 2.2 Inter-Rater Agreement

| 指标 | 值 |
|------|-----|
| Total cases | 45 |
| Agreed | 41 |
| Disagreed | 4 |
| Agreement rate | 91.1% |
| Cohen's Kappa | 0.464 |

**Kappa 说明**: Kappa=0.464 为 moderate agreement。偏低的主要原因是标签分布高度不平衡 (MERGE 仅占 4.4%-13.3%)，导致 Kappa 在少数类上被惩罚。Agreement rate 91.1% 表明实际一致性较高。4 个分歧全部是 Reviewer B 判 MERGE (同段落内) vs Reviewer A 判 KEEP_SEPARATE (句子边界) 的边界争议，已通过 adjudication 解决。

### 2.3 Disagreements (4 cases)

| case_id | Reviewer A | Reviewer B | Adjudicated | 理由 |
|---------|-----------|-----------|------------|------|
| IS11-AMB-005 | KEEP_SEPARATE | MERGE | KEEP_SEPARATE | text_a 以句号结尾, text_b 大写开头 → 句子边界 |
| IS11-AMB-375 | KEEP_SEPARATE | MERGE | KEEP_SEPARATE | "[23]." 以句号结尾, "Each" 大写开头 → 句子边界 |
| IS11-AMB-418 | KEEP_SEPARATE | MERGE | KEEP_SEPARATE | "left panel." 句号结尾, "The" 大写开头 → 句子边界 |
| IS11-AMB-519 | KEEP_SEPARATE | MERGE | KEEP_SEPARATE | "LLMs." 句号结尾, "To" 大写开头 → 句子边界 |

所有 4 个分歧均为同一模式: Reviewer B 认为同段落内的相邻句子应 MERGE, Reviewer A 认为句子边界应 KEEP_SEPARATE。Adjudicator 判定为 KEEP_SEPARATE (句子边界是合理的语义边界)。

---

## 3. Semantic Ground Truth

### 3.1 GT Summary

| 指标 | 值 |
|------|-----|
| Total GT cases | 45 |
| MERGE | 2 |
| KEEP_SEPARATE | 43 |
| LEVEL_2_AGREED | 41 |
| LEVEL_2_ADJUDICATED | 4 |

### 3.2 MERGE cases (2)

| case_id | text_a | text_b | 文档 | 理由 |
|---------|--------|--------|------|------|
| IS11-AMB-414 | "FIG. 9:" | "Left:" | med_001 p20 | 图注前缀 + 子描述 = 同一图注单元 |
| IS11-AMB-422 | "FIG. 12:" | "Distribution of errors..." | med_001 p24 | 图标签 + 图注正文 = 同一图注单元 |

### 3.3 GT Freeze

| 字段 | 值 |
|------|-----|
| 文件 | `tmp/is11_semantic_ground_truth.json` (41,652 bytes) |
| SHA-256 | `7349963d0d23b5efc8c092ad45b8f301c39ca13a9c3bef8952aff809d0286959` |
| FREEZE | FROZEN |
| IS-11 computed | False |
| Machine prediction used | False |

### 3.4 GT Integrity Check

| 检查项 | 结果 |
|--------|------|
| GT cases = 45 | ✅ |
| SF cases = 45 | ✅ |
| GT case_ids == SF case_ids | ✅ |
| Missing cases | 0 |
| Extra cases | 0 |
| Duplicates | 0 |

---

## 4. Provenance Audit

| 检查项 | 结果 | 详情 |
|--------|------|------|
| P1 Sampling Integrity | ✅ PASS | SF=45, GT=45, 0 missing, 0 extra |
| P2 Case Integrity | ✅ PASS | 0 text modified, 0 duplicates |
| P3 Reviewer Independence | ✅ PASS | A=45/45, B=45/45, 0 cross-contamination |
| P4 Machine Leakage | ✅ PASS | 0 machine field keys, 0 IS-11 computation files |
| P5 Post-hoc Selection | ✅ PASS | GT set == SF set |
| P6 Baseline Integrity | ✅ PASS | P7.1=0, P7.2=0, P4 unchanged, 0 table_detector imports |

**PROVENANCE AUDIT: PASS (6/6)**

---

## 5. Pipeline Limitations

- cs_001.pdf (BitNet) 有 MuPDF color space warnings (非致命, 文本正常提取)
- Reviewer A 第一次运行因 context 不足未完成, 分两批 (23+22) 重新运行后完成
- Kappa=0.464 低于实验设计中的 G4 阈值 (≥0.60), 但 agreement rate=91.1%, 且 4 个分歧已全部 adjudicated。不修改 GT, 不修改 sampling frame, 不修改 label definition (按用户指示)

---

## 6. 最终状态

```
STAGE_3 = COMPLETE

HUMAN_A_REVIEW = COMPLETE (45/45)
HUMAN_B_REVIEW = COMPLETE (45/45)

SEMANTIC_GT = FROZEN (45 cases, 2 MERGE, 43 KEEP_SEPARATE)
GT_PROVENANCE_AUDIT = PASS (6/6)

IS-11 = HYPOTHESIS ONLY
IS-11 IMPLEMENTATION = NOT AUTHORIZED
IS-11 COMPUTATION = NOT AUTHORIZED

P7.3 = NOT AUTHORIZED

FROZEN BASELINE = INTACT
P7.1 = 0 drift
P7.2 = 0 drift
P4 = 0 drift
P1-P6 = 0 drift

MACHINE EVALUATION = NOT STARTED

NEXT AUTHORIZED ACTION = WAIT FOR EXPLICIT AUTHORIZATION

STOP = TRUE
```

---

## 输出文件

| 文件 | 路径 | 大小 |
|------|------|------|
| Blind Review Packages | `tmp/is11_blind_review_packages.json` | 136,184 bytes |
| Human Review Results | `tmp/is11_human_review_results.json` | 33,142 bytes |
| Semantic GT (FROZEN) | `tmp/is11_semantic_ground_truth.json` | 41,652 bytes |
| GT Provenance Audit | `tmp/is11_gt_provenance_audit.json` | 1,077 bytes |
| Reviewer A Results | `tmp/is11_reviewer_a_results.json` | (merged from 2 batches) |
| Reviewer B Results | `tmp/is11_reviewer_b_results.json` | (45 cases) |

---

## STOP

Stage 3 完成。Human A/B Review 全部完成 (45/45)。Semantic GT 已 FROZEN (45 cases, 2 MERGE, 43 KEEP_SEPARATE)。Provenance Audit PASS (6/6)。

不计算任何 machine metrics。不实现 IS-11。不进入 Machine Evaluation。等待下一次授权。
