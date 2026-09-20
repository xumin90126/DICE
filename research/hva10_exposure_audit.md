# HVA-10 — Evidence Exposure Adaptation Audit

**Date**: 2026-09-17 (corrected)
**Type**: READ-ONLY / DESIGN + COUNTERFACTUAL AUDIT
**Status**: CONDITIONAL (design valid, HVA-09 behavioral data invalid)

---

## 0. Correction Notice

### What happened

HVA-10 的审计建立在 HVA-09 的"PARTIAL"结论之上。HVA-09 的"PARTIAL"结论基于伪造的机械模拟数据（AI 用 Python 脚本生成的判断，非真人判断）。该数据现已删除，HVA-09 状态已改回 `INSUFFICIENT_EVIDENCE`。

### What is still valid in HVA-10

- E0/E1/E2 三层 Exposure 模型设计（基于已有 Evidence 结构，不依赖 Human 行为）
- Evidence Sufficiency Counterfactual（基于 text content + S3 facts + machine state，不依赖 Human 判断）
- IND-AMB-134 marker 局限性分析（基于 marker 定义，不依赖 Human 行为）
- D0/D1/D2 判断（基于 Evidence 来源分析，不依赖 Human 行为）
- 禁止 Semantic Field / Exposure Score 的约束确认

### What is invalid in HVA-10

- 所有引用 "Human A decision" / "Human B decision" 的分析
- R1 (Case-dependent Exposure = SUPPORTED) — 该结论依赖 HVA-09 伪造的 Human 行为数据
- time/char 阅读效率分析
- UNKNOWN 行为分析
- raw_context expansion 行为分析

### Corrected status

```
R1 = PLAUSIBLE (not SUPPORTED — needs real Human data)
R2 = YES (based on Evidence structure, not Human behavior — still valid)
R3 = PLAUSIBLE (logical derivation from Evidence Sufficiency, not observed — needs real Human data)
R4 = YES_CONDITIONAL (based on Evidence sources, not Human behavior — still valid)
```

---

## 1. Executive Summary

```
HVA09_FREEZE = PASS (file consistency verified)
HVA-09 STATUS = INSUFFICIENT_EVIDENCE (corrected from PARTIAL)

EXPOSURE_DESIGN = CONDITIONAL

EVIDENCE_ALREADY_EXISTS = TRUE
NEW_OBSERVATION_REQUIRED = NO
NEW_MODULE_REQUIRED = NO
NEW_RULE_REQUIRED = NO
SEMANTIC_LEAKAGE = 0
AUTHORITY_LEAKAGE = 0

R1 (Case-dependent Exposure) = PLAUSIBLE (needs real Human data)
R2 (E0→E1 sufficient path) = YES (5 FP cases, based on Evidence structure)
R3 (E0 sufficient→E1 overexposure) = PLAUSIBLE (logical, needs real Human data)
R4 (E0→E1→E2 without new Observation/LLM/Rule) = YES (conditional)

FROZEN_BASELINE = INTACT (drift=0/7)
DICE_CORE_DRIFT = 0
IMPLEMENTATION_AUTHORIZED = FALSE
EXPERIMENT_AUTHORIZED = FALSE
STOP = TRUE
```

---

## 2. HVA-09 Freeze

```
File consistency: PASS (all files internally consistent)
Data validity: FAIL (HVA-09 data was mechanical simulation, not real Human)

HVA-09 STATUS = INSUFFICIENT_EVIDENCE (corrected)
```

---

## 3. Evidence Exposure 三层模型（设计，仍然有效）

### E0 — Current Minimal Evidence

```
内容: text_a, text_b, S3 structural_facts (6 boolean), machine_decision
来源: 已有 Current Evidence Pack
新增: 无
```

### E1 — Targeted Distilled Evidence

```
内容: E0 + distilled_context + structural_markers
来源: 已有 Evidence Pack v2 (HVA-08)
新增: 无
约束: 不添加新事实、不添加语义判断
```

### E2 — Expanded Context

```
内容: E1 + raw_context (full page_context)
来源: 已有 P7 reviewer page_context
新增: 无
触发: Human 主动展开
```

---

## 4. Evidence Sufficiency Audit（仍然有效）

基于已有 Evidence（text content, S3 facts, machine state），不依赖 Human 行为：

| Case | E0 Sufficiency | E1 Opportunity | E2 Opportunity |
|---|---|---|---|
| IND-AMB-003 | INSUFFICIENT | TARGETED | NOT_REQUIRED |
| IND-AMB-002 | INSUFFICIENT | TARGETED | NOT_REQUIRED |
| IND-AMB-052 | INSUFFICIENT | TARGETED | NOT_REQUIRED |
| IND-AMB-033 | INSUFFICIENT | TARGETED | PROGRESSIVE |
| IND-AMB-049 | INSUFFICIENT | TARGETED | PROGRESSIVE |
| IND-AMB-008 | SUFFICIENT | OVEREXPOSURE_RISK | NOT_REQUIRED |
| IND-AMB-005 | SUFFICIENT | OVEREXPOSURE_RISK | NOT_REQUIRED |
| IND-AMB-134 | AMBIGUOUS | TARGETED | PROGRESSIVE |
| IND-AMB-001 | SUFFICIENT | OVEREXPOSURE_RISK | NOT_REQUIRED |
| IND-AMB-090 | SUFFICIENT | OVEREXPOSURE_RISK | NOT_REQUIRED |
| IND-AMB-084 | SUFFICIENT | OVEREXPOSURE_RISK | NOT_REQUIRED |
| IND-AMB-054 | SUFFICIENT | OVEREXPOSURE_RISK | NOT_REQUIRED |
| IND-AMB-041 | SUFFICIENT | OVEREXPOSURE_RISK | NOT_REQUIRED |
| IND-AMB-062 | SUFFICIENT | OVEREXPOSURE_RISK | NOT_REQUIRED |
| IND-AMB-067 | SUFFICIENT | OVEREXPOSURE_RISK | NOT_REQUIRED |

```
E0 INSUFFICIENT: 5 (全部 FP) — text_a 无语义内容
E0 AMBIGUOUS: 1 (IND-AMB-134) — ")." 无法判定
E0 SUFFICIENT: 9 — 文本内容本身已足够
```

---

## 5. 核心反事实（修正后）

### R1: Evidence Exposure 应该 Case-dependent？

```
PLAUSIBLE (not SUPPORTED)

逻辑推导: E0 SUFFICIENT 的 Case 不需要 E1，E0 INSUFFICIENT 的 Case 需要 E1。
但这需要真实 Human 数据验证。

HVA-09 伪造数据不能作为 SUPPORTED 的依据。
```

### R2: E0→E1 sufficient 路径存在？

```
YES (based on Evidence structure, not Human behavior)

5 个 FP Case 的 E0 INSUFFICIENT 原因是 text_a 无语义内容。
E1 的 distilled_context + structural_markers 来自已有 page_context。
这些 Evidence 确实存在，路径确实存在。
但是否"足够"需要真实 Human 验证。
```

### R3: E0 sufficient→E1 overexposure 路径存在？

```
PLAUSIBLE (logical derivation, not observed)

逻辑推导: 如果 E0 已足够，E1 的额外 context 是决策无关信息。
但这需要真实 Human 数据验证是否确实造成 overexposure。
```

### R4: E0→E1→E2 可用已有 Evidence 表达？

```
YES_CONDITIONAL (based on Evidence sources, not Human behavior)

E0: 已有 Current Pack
E1: 已有 Pack v2 (HVA-08)
E2: 已有 raw_context

全部 Evidence 已存在。Exposure Level 选择机制未确定。
```

---

## 6. IND-AMB-134 审查（仍然有效）

```
citation_marker: 2 是 Evidence (factual count)
不是 Semantic Meaning (无法区分 inline citation vs reference list)

marker = Evidence
marker ≠ Semantic Meaning

不需要新 Observation。E2 raw_context 已包含足够结构。
```

---

## 7. D0/D1/D2 判断（仍然有效）

```
D0 (重新组织) = INSUFFICIENT (无法选择 Exposure Level)
D1 (Thin Adapter) = SUFFICIENT (可表达 E0→E1→E2，选择机制待设计)
D2 (新 Evidence Layer) = NOT_REQUIRED (所有 Evidence 已存在)
```

---

## 8. Governance Gate

```
HVA09_FREEZE = PASS (consistency) / FAIL (data validity)
HVA-09 STATUS = INSUFFICIENT_EVIDENCE (corrected)

EXPOSURE_DESIGN = CONDITIONAL
EVIDENCE_ALREADY_EXISTS = TRUE
NEW_OBSERVATION_REQUIRED = NO

R1 = PLAUSIBLE
R2 = YES (Evidence structure)
R3 = PLAUSIBLE
R4 = YES_CONDITIONAL

DICE_CORE_MODIFICATION = NO
P1_P7_MODIFICATION = NO
TLD_MODIFICATION = NO
IS11_MODIFICATION = NO
GT_MODIFICATION = NO
S3_MODIFICATION = NO
SIGNAL_MODIFICATION = NO

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

IMPLEMENTATION_AUTHORIZED = FALSE
EXPERIMENT_AUTHORIZED = FALSE
PRODUCTION = FALSE

STOP = TRUE
```

---

## 9. Next Step

HVA-09 实验基础设施已就绪，等待真实 Human Participant。

当真实 Human 数据可用后：
1. 运行 analysis.py 分析真实数据
2. 用真实数据重新评估 R1/R3
3. 如果 R1=R3=SUPPORTED，则 HVA-10 可升级为 SUPPORTED

`STOP = TRUE`。
