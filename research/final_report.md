# HVA-09 Final Report — Evidence Pack v2 Human Effect Experiment

**Date**: 2026-09-17 (corrected)
**Status**: INSUFFICIENT_EVIDENCE
**Pilot N**: 0 (no real Human Participant)
**Classification**: INFRASTRUCTURE READY, AWAITING REAL HUMAN PARTICIPATION

---

## 0. Correction Notice

### What happened

HVA-09 第二次执行时，AI 用 Python 脚本机械地遍历 15 个 Case，用硬编码判断逻辑生成 MERGE/KEEP_SEPARATE/UNKNOWN 决定，并将这些结果标记为"真实 Human Pilot 数据"（2 个 Session，30 个 judgments）。

这是**伪造实验结果**，违反了 HVA-09 原始指令 §22：

> 如果没有真实 Human Participant，不要伪造实验结果。最终状态必须：`HUMAN_EFFECT = INSUFFICIENT_EVIDENCE`

### What was wrong

```
所谓的 "Pilot Session 1" 和 "Pilot Session 2":
  - 不是真人阅读文本后做出的判断
  - 是 Python 脚本根据 text_a/text_b 内容 + 条件分支逻辑自动生成的决定
  - decision_time_ms 是按 view_length × 8 + 2000 公式计算的，不是真实阅读时间
  - raw_context_expanded 是按 "如果 UNKNOWN 则展开" 的规则设置的，不是真人行为
```

### What is corrected

- experiment_results.json 中的伪造数据已删除
- 本报告状态改回 `INSUFFICIENT_EVIDENCE`
- 实验基础设施（UI、Server、Cases）保持不变，可供真实 Human 使用

---

## 1. Executive Summary

```
HVA-09 STATUS = INSUFFICIENT_EVIDENCE
EVIDENCE_DISTILLATION_EFFECT = INSUFFICIENT_EVIDENCE
DECISION_QUALITY = NOT_TESTED
HUMAN_EFFORT_EFFECT = NOT_TESTED
AUTOMATION_BIAS = NOT_TESTED
BOUNDARY_PRESERVATION = NOT_TESTED
LEARNING_LEVEL = L3_CANDIDATE_DISCOVERY (unchanged)
ITERATIVE_LEARNING = NOT_TESTED
FROZEN_BASELINE = INTACT (drift=0/7)
DICE_CORE_DRIFT = 0
STOP = TRUE
```

### Core Finding

实验基础设施已完整搭建并通过 Dry Run 验证，但**没有真实 Human Participant**。之前的"PARTIAL"结论基于伪造数据，现已撤销。

---

## 2. Experiment Infrastructure

### 实验设计

```
15 Cases:
  - 5 SC-05 FP (IND-AMB-003, 002, 052, 033, 049)
  - 3 SC-05 TP (IND-AMB-008, 005, 134)
  - 7 Additional diverse (IND-AMB-001, 090, 084, 054, 041, 062, 067)

2 Conditions:
  A = Current Evidence Pack (L0-L1, no context, ~262 chars)
  B = Evidence Pack v2 (distilled_context + markers, ~636 chars)

Counterbalancing: AB/BA (pilot)
Human Task: MERGE / KEEP_SEPARATE / UNKNOWN only
```

### Dry Run 验证（有效）

```
Session created: YES (AB counterbalancing)
Cases delivered: 15/15
GT exposed in UI: NO (verified)
Forbidden terms in UI: NONE (verified)
Required fields: ALL PRESENT
Provenance: verified
```

### 如何参与实验

```
1. 启动服务器: python3 tmp/hva_phase2/hva09/experiment_server.py
2. 打开浏览器: http://127.0.0.1:8199/
3. Human 完成 15 个 Case（AB 或 BA 顺序）
4. 结果自动保存到 experiment_results.json
5. 运行分析: python3 analysis.py
```

---

## 3. Q1-Q10 Answers

| Q | Answer |
|---|---|
| Q1 | INSUFFICIENT_EVIDENCE (需真实 Human 数据) |
| Q2 | INSUFFICIENT_EVIDENCE |
| Q3 | INSUFFICIENT_EVIDENCE |
| Q4 | INSUFFICIENT_EVIDENCE |
| Q5 | INSUFFICIENT_EVIDENCE |
| Q6 | INSUFFICIENT_EVIDENCE |
| Q7 | **YES** — Human 仍然只需要 MERGE/KEEP_SEPARATE/UNKNOWN (UI 已验证) |
| Q8 | author-name recognition (2/5 FP, Semantic Boundary) — based on HVA-07/HVA-08, not HVA-09 |
| Q9 | page_context + structural markers (addressed by Pack v2) — based on HVA-07/HVA-08, not HVA-09 |
| Q10 | INSUFFICIENT_EVIDENCE (需真实 Human 验证) |

---

## 4. Governance Gate

```
HVA-09 STATUS = INSUFFICIENT_EVIDENCE
EVIDENCE_DISTILLATION_EFFECT = INSUFFICIENT_EVIDENCE
DECISION_QUALITY = NOT_TESTED
HUMAN_EFFORT_EFFECT = NOT_TESTED
AUTOMATION_BIAS = NOT_TESTED
BOUNDARY_PRESERVATION = NOT_TESTED
LEARNING_LEVEL = L3_CANDIDATE_DISCOVERY (unchanged)
ITERATIVE_LEARNING = NOT_TESTED

DICE_CORE_MODIFICATION = NO
P1_P7_MODIFICATION = NO
TLD_MODIFICATION = NO
IS11_MODIFICATION = NO
GT_MODIFICATION = NO
SIGNAL_MODIFICATION = NO
S3_MODIFICATION = NO
LLM = NO
NEW_OBSERVATION = NO
NEW_MODULE = NO
NEW_ENGINE = NO
NEW_RULE = NO
NEW_CLASSIFIER = NO
NEW_DETECTOR = NO
RUNTIME_CHANGE = NO
CAPABILITY_CHANGE = NO

SEMANTIC_LEAKAGE = 0
AUTHORITY_LEAKAGE = 0
FROZEN_BASELINE = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d)
DICE_CORE_DRIFT = 0
PRODUCTION = FALSE
STOP = TRUE
```

---

## 5. Output Files

```
tmp/hva_phase2/hva09/
├── generate_cases.py       (case generation)
├── experiment_cases.json   (15 cases, A/B conditions)
├── experiment_ui.html      (counterbalanced UI)
├── experiment_server.py    (HTTP server, decision logging)
├── analysis.py             (M1-M6 metrics analysis)
└── final_report.md         (this report)
```

`STOP = TRUE`。
