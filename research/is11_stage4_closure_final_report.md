# DICE Stage 4 Closure — Final Report

## 状态机

```
STAGE 4
    ↓
CLOSED
    ↓
FROZEN BASELINE
    ↓
INTACT
    ↓
NEXT INFORMATION SOURCE DECISION
    ↓
PENDING
```

```
IS-11
    ↓
EXPERIMENTALLY EVALUATED
    ↓
G7 = FAIL
G8 = PASS
    ↓
NO INTEGRATION
    ↓
NO P7.3
    ↓
NO PRODUCTION
```

```
FROZEN MODIFICATION
    ↓
NOT AUTHORIZED
```

---

## §1 — Frozen Baseline (READ-ONLY)

| 对象 | 状态 | Drift |
|------|------|-------|
| P1 (layout_analyzer.py, layout_rebuilder.py, table_line_detector.py) | ✅ FROZEN | 0 |
| P2 (3 files) | ✅ FROZEN | 0 |
| P3 (3 files) | ✅ FROZEN | 0 |
| P4 SpanConfig (5 values) | ✅ UNCHANGED | 0 |
| P4 Runner C1_SHA (3 files) | ✅ ALL MATCH | 0 |
| P5 (3 files) | ✅ FROZEN | 0 |
| P6 (3 files) | ✅ FROZEN | 0 |
| P7.1 (6 files) | ✅ FROZEN | 0 |
| P7.2 (8 files) | ✅ FROZEN | 0 |
| IS-01 definition | ✅ FROZEN (identical in Stage 4) | 0 |
| IS-02 definition | ✅ FROZEN (identical in Stage 4) | 0 |
| table_line_detector.py | ✅ MATCHES FROZEN HASH | 0 |
| CandidateSpan | ✅ FROZEN (via P1-P6 runner SHA) | 0 |
| DocumentSpan | ✅ FROZEN (via P1-P6 runner SHA) | 0 |
| Capability/Registry/Runtime | ✅ FROZEN (via P7.1/P7.2) | 0 |
| Frozen Capability Table | ✅ FROZEN (perception_dependency_matrix.json) | 0 |
| **TOTAL DRIFT** | | **0** |

```
P1-P6 drift = 0
P4 drift = 0
P7.1 drift = 0
P7.2 drift = 0
IS-01 drift = 0
IS-02 drift = 0
Frozen Runtime baseline drift = 0
```

**FROZEN BASELINE = INTACT ✅**

---

## §2 — Stage 4 Artifact Sealing

| 文件 | 大小 | SHA-256 |
|------|------|---------|
| `tmp/is11_machine_evaluation_results.json` | 63,889 bytes | 437aa665...33158 |
| `tmp/is11_machine_evaluation_metrics.json` | 5,472 bytes | e02ef77d...fb88e |
| `tmp/is11_machine_evaluation_report.md` | 9,762 bytes | ca27e236...ee21d3 |
| `tmp/is11_machine_evaluation_provenance.json` | 421 bytes | ee6e87c1...003ab4 |
| `tmp/is11_machine_evaluation_determinism.json` | 37 bytes | cb0bdb88...965725 |

**Cross-checks:**
- Results vs Metrics: 24/24 metrics match ✅
- G7: results=FAIL, metrics=FAIL ✅
- G8: results=PASS, metrics=PASS ✅
- Determinism: results=PASS, file=PASS ✅
- Case count: 45/45 ✅
- Provenance: p1_p6_modified=False, p4_modified=False ✅

```
Stage 4 = COMPLETE
Baseline A = COMPLETE
Baseline B = COMPLETE
Experimental C = COMPLETE
G7 = FAIL
G8 = PASS
Determinism = PASS
Frozen Baseline = INTACT
P7.3 = NOT AUTHORIZED
Production = FALSE
STOP = TRUE
```

---

## §3 — Key Experimental Facts

| 事实 | 值 | 确认 |
|------|-----|------|
| Primary cases | 45 | ✅ |
| Baseline B: FP | 1 | ✅ |
| Baseline B: Coverage | 42.2% | ✅ |
| Experimental C: FP | 1 | ✅ |
| Experimental C: Coverage | 60.0% | ✅ |
| ΔFP | 0 | ✅ |
| ΔCoverage | +17.8 pp | ✅ |
| G7 | FAIL | ✅ |
| G8 | PASS | ✅ |
| C vs B differences | 8 cases | ✅ |
| All 8: INSUFFICIENT_EVIDENCE → KEEP_SEPARATE | Yes | ✅ |
| All 8 GT correct | Yes | ✅ |
| Table context unavailable | 32/45 (71.1%) | ✅ |
| Determinism | PASS | ✅ |
| Cross-document stability | NOT_ESTABLISHED | ✅ |
| GT MERGE | 2 | ✅ |
| GT KEEP_SEPARATE | 43 | ✅ |

**ALL KEY FACTS: ✅ CONFIRMED**

---

## §4 — Conclusion Note (已证实 vs 尚未证实)

### 已证实

1. IS-11 在本次 45-case 实验中未降低 FP (G7=FAIL)
2. IS-11 没有造成 Recall 退化 (G8=PASS)
3. Coverage 从 42.2% 增至 60.0%
4. 8 个新增可判定案例均与 GT 一致
5. Determinism PASS
6. Cross-document FP-reduction stability NOT ESTABLISHED
7. 32/45 (71.1%) case 未获得 TABLE_CELL_CONTEXT
8. 2 个 MERGE GT 均在 unavailable 集合 (figure captions)
9. 唯一 FP case 在 unavailable 集合

### 尚未证实 (不可声称)

- 不可声称 "IS-11 无价值"
- 不可声称 "TABLE_CELL_CONTEXT 无效"
- 不可声称 "IS-11 能普遍提升 Coverage 17.8%"
- 不可声称 "table_line_detector 修复后一定有效"
- 不可声称 "IS-11 一定能够降低 FP"
- 不可对 Recall/Precision 统计稳定性做过度解释 (GT MERGE=2)

详见: `tmp/is11_stage4_closure_conclusion_note.md`

---

## §5 — 32/45 Table Unavailable 诊断

### 原因分布

| 原因 | Case 数 | 占比 |
|------|---------|------|
| TABLE_NOT_DETECTED | 25 | 78.1% |
| CANDIDATE_OUTSIDE_TABLE_BBOX | 7 | 21.9% |
| **Total** | **32** | **100%** |

### 按文档分布

| 文档 | Total | Unavailable | 占比 |
|------|-------|-------------|------|
| is11_resnet | 9 | 1 | 11% |
| is11_efficientnet | 18 | 16 | 89% |
| is11_med_001 | 8 | 8 | 100% |
| is11_cs_001 | 10 | 7 | 70% |

### 按页面分布

- efficientnet p5: 2, p6: 5, p7: 5, p8: 4 → TABLE_NOT_DETECTED (16 cases)
- med_001 p6: 1, p13: 1, p19: 3, p20: 2, p24: 1 → TABLE_NOT_DETECTED (8 cases)
- cs_001 p3: 7 → CANDIDATE_OUTSIDE_TABLE_BBOX (table detected but candidates outside)
- resnet p7: 1 → TABLE_NOT_DETECTED (1 case)

### GT 分布

| GT Label | Unavailable 中 | Available 中 |
|----------|---------------|-------------|
| MERGE | 2 | 0 |
| KEEP_SEPARATE | 30 | 13 |

### 内容类型 (32 unavailable)

| 类型 | 数量 |
|------|------|
| mixed (text + numeric) | 20 |
| numeric_pair | 7 |
| numeric_vs_text | 2 |
| figure_caption | 2 |
| text_pair | 1 |

### 信息可用性瓶颈

```
PRIMARY BOTTLENECK: TABLE_NOT_DETECTED (25/32 = 78%)
  → table_line_detector returned 0 tables on these pages
  → efficientnet p5-p8, med_001 p6/p13/p19/p20/p24, resnet p7

SECONDARY: CANDIDATE_OUTSIDE_TABLE_BBOX (7/32 = 22%)
  → table detected on page, but candidate bbox falls outside table region
  → all 7 in cs_001 p3 (candidates are in prose, not table)
```

**关键发现**:
- 2 个 MERGE GT case 都是 figure captions (med_001 p20, p24) → IS-11 在设计上无法覆盖
- 唯一 FP case (IS11-AMB-135) 在 unavailable 集合 → IS-11 无法纠正
- 瓶颈是 detector coverage，不是 cell membership resolution

---

## §6 — Frozen Modification Decision

| 问题 | 结论 |
|------|------|
| F1: Frozen 是当前研究瓶颈？ | **INCONCLUSIVE** |
| F2-A: 新 IS 实验 → 修改 Frozen？ | NO |
| F2-B: 增强 table perception → 修改 Frozen？ | YES (但污染已有实验) |
| F2-C: 修改 P1-P6 → 修改 Frozen？ | NO (无证据) |
| F2-D: 修改 P4 geometry → 修改 Frozen？ | NO (无证据) |
| F3: 当前有资格解冻 Frozen？ | **NOT AUTHORIZED** |

详见: `tmp/frozen_modification_decision_note.md`

---

## §7 — Next Information Source Decision (候选)

| Option | 研究问题 | 成本 | Frozen 修改 | 新 GT | 新 Corpus | 优先级 |
|--------|---------|------|------------|-------|-----------|--------|
| A | IS-11 在更强 table perception 下是否有价值？ | HIGH | 可能需要 | 必须 | 必须 | MEDIUM |
| B | 是否存在比 TABLE_CELL_CONTEXT 更稳定的结构信息？ | LOW-MEDIUM | 不需要 | 不需要 | 不需要 | **HIGH** |
| C | 为什么大量 case 无法达到 sufficient evidence？ | LOW | 不需要 | 不需要 | 不需要 | MEDIUM-HIGH |

**建议路径**: Option C (诊断) → Option B (新 IS) → [如有必要] Option A

详见: `tmp/next_information_source_decision.md`

---

## §8 — 最终状态

```
STAGE 4
    ↓
CLOSED
    ↓
FROZEN BASELINE = INTACT (0 drift)
    ↓
NEXT INFORMATION SOURCE DECISION = PENDING
    ↓
FROZEN MODIFICATION = NOT AUTHORIZED
    ↓
STOP = TRUE
WAIT FOR EXPLICIT AUTHORIZATION
```

```
IS-11
    ↓
EXPERIMENTALLY EVALUATED
    ↓
G7 = FAIL
G8 = PASS
    ↓
NO INTEGRATION
NO P7.3
NO PRODUCTION
```

```
IMPLEMENTATION = NOT AUTHORIZED
P7.3 = NOT AUTHORIZED
PRODUCTION = FALSE
FROZEN BASELINE = INTACT
STOP = TRUE
```

---

## 输出文件

| 文件 | 描述 |
|------|------|
| `tmp/is11_stage4_closure_conclusion_note.md` | READ-ONLY 结论 (已证实 vs 尚未证实) |
| `tmp/frozen_modification_decision_note.md` | Frozen 修改决策 (F1/F2/F3) |
| `tmp/next_information_source_decision.md` | 下一信息源候选研究问题 (Option A/B/C) |
| `tmp/is11_stage4_closure_final_report.md` | 本文件 (Stage 4 Closure 最终报告) |

---

## STOP

Stage 4 已封存。Frozen Baseline 完整 (0 drift)。32/45 table unavailable 已诊断。Frozen 修改 NOT AUTHORIZED。下一信息源决策 PENDING。

不修改任何代码。不重新运行实验。不进入 P7.3。不进入 Production。

**WAIT FOR EXPLICIT AUTHORIZATION.**
