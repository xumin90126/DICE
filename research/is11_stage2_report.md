# IS-11 Stage 2: Independent Candidate Universe Construction Report

## STAGE 2 — COMPLETE

| 字段 | 值 |
|------|-----|
| 阶段 | Stage 2 — Independent Candidate Universe Construction |
| 约束 | Frozen P1-P6 only, NO IS-11, NO table_line_detector, NO P1-P6 modification |
| INTEGRITY PRE-GATE | ✅ PASS |
| Candidate Universe | FROZEN |
| Sampling Frame | FROZEN |
| FROZEN BASELINE | INTACT ✅ |
| STOP | TRUE |

---

## 1. Integrity Pre-Gate

| 检查项 | 结果 |
|--------|------|
| 4 PDF SHA-256 vs manifest | ✅ ALL MATCH |
| Frozen Baseline (P7.1) | ✅ 0 drift |
| Frozen Baseline (P7.2) | ✅ 0 drift |
| P4 SpanConfig | ✅ UNCHANGED (max_h_gap=8.0, max_v_gap=14.0, same_line_tol=3.0, cross_col=30.0, overlap=0.5) |
| P1-P6 code | ✅ UNCHANGED |
| IS-11 implementation | ✅ NONE (0 files) |
| table_line_detector integration | ✅ NOT CALLED (0 imports, only hash reference) |
| IS-01/IS-02 frozen | ✅ FROZEN |
| Corpus manifest frozen | ✅ PASS |

**INTEGRITY PRE-GATE: PASS**

---

## 2. 四个 PDF 的 P1-P6 Processing 状态

| PDF | 页数 | 观测总数 | 配对总数 | 同Y未合并 | 已合并 | AMBIGUOUS |
|-----|------|---------|---------|----------|--------|-----------|
| is11_resnet | 12 | 2,448 | 2,447 | 280 | 1,693 | 118 |
| is11_efficientnet | 11 | 3,153 | 3,152 | 533 | 1,936 | 253 |
| is11_med_001 | 29 | 2,793 | 2,792 | 144 | 2,123 | 52 |
| is11_cs_001 | 8 | 1,003 | 1,002 | 191 | 537 | 122 |
| **合计** | **60** | **9,397** | **9,393** | **1,148** | **6,289** | **545** |

**处理时间**: 2.9 秒

**Processing 状态**: 全部 60 页成功处理，无错误，无跳过 (0 页因观测不足跳过)。

---

## 3. Candidate Universe

### 3.1 总体

| 指标 | 值 |
|------|-----|
| 总 AMBIGUOUS 候选 | 545 |
| 候选定义 | Frozen AMBIGUOUS criteria: 8 < gap ≤ 50, same_style, line_obs ≤ 15, w_b ≥ 15 |
| 候选类型 | Pure geometric slice (无 IS-11, 无 IS-01/IS-02, 无 semantic label) |
| FREEZE | FROZEN |
| 文件 | `tmp/is11_independent_candidate_universe.json` (583,112 bytes) |

### 3.2 按文档分布

| 文档 | AMBIGUOUS | 占比 |
|------|-----------|------|
| is11_efficientnet | 253 | 46.4% |
| is11_cs_001 | 122 | 22.4% |
| is11_resnet | 118 | 21.7% |
| is11_med_001 | 52 | 9.5% |

### 3.3 几何分布

| Gap 区间 | 数量 |
|---------|------|
| 8-12pt | 179 |
| 12-20pt | 105 |
| 20-30pt | 174 |
| 30-50pt | 87 |

| w_b 区间 | 数量 |
|---------|------|
| 15-30pt | 398 |
| 30-60pt | 100 |
| 60-100pt | 22 |
| >100pt | 25 |

| line_obs 区间 | 数量 |
|--------------|------|
| 0-3 | 84 |
| 4-6 | 127 |
| 7-10 | 196 |
| 11-15 | 138 |

---

## 4. Sampling Frame

### 4.1 采样规则

- **方法**: Stratified random sampling
- **Seed**: 20240909 (固定, 记录)
- **分层维度** (全部几何, 无 IS-11):
  1. document_id (跨文档覆盖)
  2. h_gap bin (8-12, 12-20, 20-30, 30-50)
  3. w_b bin (15-30, 30-60, 60+)
  4. line_obs_count bin (0-3, 4-6, 7-10, 11-15)
- **目标**: 45 cases (超过 ≥30 最低要求)
- **最低每文档**: 8

### 4.2 采样结果

| 文档 | 采样数 | 占比 |
|------|--------|------|
| is11_efficientnet | 18 | 40.0% |
| is11_cs_001 | 10 | 22.2% |
| is11_resnet | 9 | 20.0% |
| is11_med_001 | 8 | 17.8% |
| **合计** | **45** | **100%** |

### 4.3 几何分布

| Gap 区间 | 数量 |
|---------|------|
| 8-12pt | 17 |
| 12-20pt | 7 |
| 20-30pt | 14 |
| 30-50pt | 7 |

| w_b 区间 | 数量 |
|---------|------|
| 15-30pt | 37 |
| 30-60pt | 5 |
| 60+ | 3 |

| line_obs 区间 | 数量 |
|--------------|------|
| 0-3 | 9 |
| 4-6 | 9 |
| 7-10 | 18 |
| 11-15 | 9 |

### 4.4 冻结

| 字段 | 值 |
|------|-----|
| 文件 | `tmp/is11_independent_sampling_frame.json` (48,454 bytes) |
| SHA-256 | `97980845b5bbd277b0b733aeb9891b42b7cd5317d33b4ebdfb33735373705b4d` |
| FREEZE | FROZEN |
| IS-11 computed | False |
| IS-01/IS-02 computed | False |
| Human GT collected | False |

---

## 5. Pipeline Limitations

**0 个 pipeline limitations 记录。**

全部 60 页成功通过 frozen P1-P6 处理，无 parsing failure、missing text、malformed coordinates 或 table-related layout issue。

注意: cs_001.pdf (BitNet) 有 MuPDF color space warnings (非致命, 文本可正常提取)。

---

## 6. 最终状态

```
STAGE_2 = COMPLETE

Candidate Universe = FROZEN (545 AMBIGUOUS cases)
Sampling Frame = FROZEN (45 sampled cases, seed=20240909)

IS-11 = HYPOTHESIS ONLY
IS-11 IMPLEMENTATION = NOT AUTHORIZED
IS-11 COMPUTATION = NOT AUTHORIZED
P7.3 = NOT AUTHORIZED

FROZEN BASELINE = INTACT (P7.1=0 drift, P7.2=0 drift)

NEXT AUTHORIZED ACTION = HUMAN REVIEW (awaiting human authorization)
STOP = TRUE
```

---

## 输出文件

| 文件 | 路径 | 大小 |
|------|------|------|
| Candidate Universe | `tmp/is11_independent_candidate_universe.json` | 583,112 bytes |
| Sampling Frame | `tmp/is11_independent_sampling_frame.json` | 48,454 bytes |
| Candidate Generation Script | `tmp/is11_generate_candidates.py` | (read-only, uses frozen P1-P6) |
| Sampling Frame Script | `tmp/is11_build_sampling_frame.py` | (read-only, geometry-only stratification) |

---

## STOP

Stage 2 完成。Candidate Universe 和 Sampling Frame 已冻结。不进行 Human Review。不实现 IS-11。不计算任何 machine metrics。等待下一次授权。
