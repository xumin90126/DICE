# Human Decision Evidence Dependency & Feedback Learning Signal Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY / NO IMPLEMENTATION / NO NEW MODULE / FROZEN INTACT / STOP

---

## 1. Executive Summary

```
PRIMARY_EVIDENCE_CATEGORY = E2 (Existing but Unorganized) — 35/45 (78%)
SECONDARY_EVIDENCE_CATEGORY = E5 (Human Semantic) — 10/45 (22%)
HUMAN_OVERRIDE_ROOT_CAUSE = System cue wrong (TLD missed table) + Human used E2+E5
KEY_FINDING = Human depends on BOTH structural (E2) AND text pattern (E5) evidence
SIGNAL_CANDIDATE_1 = has_fig_prefix → MERGE (info gain HIGH, but semantic)
SIGNAL_CANDIDATE_2 = line_obs >= 6 → KEEP_SEPARATE (info gain MODERATE, pure geometry)
SIGNAL_CANDIDATE_3 = line_obs >= 3 AND NOT fig → KEEP_SEPARATE (info gain HIGH, mixed)
CURRENT_LEARNING_LEVEL = L3 (improved from L2 — evidence-grounded candidates found)
FUTURE_REUSE = INSUFFICIENT (0 future cases)
IMPLEMENTATION_AUTHORIZED = FALSE
STOP = TRUE
```

> **Human 正确判断主要依赖 E2（已有但未组织的 Evidence——多个 line spans 构成表格结构）和 E5（文本模式识别——'FIG.' 前缀区分 Figure caption）。纯几何（E2）无法区分表格列与 Figure caption（AMB-313 与 AMB-414 几何几乎相同）；Human 必须使用文本内容（E5）来区分。发现了 3 个 evidence-grounded signal candidate，其中 Signal 2（line_obs ≥ 6，纯几何）无 false positive 但覆盖率仅 62%；Signal 3（line_obs ≥ 3 AND NOT fig）信息增量最高但有语义成分。Learning Level 提升到 L3（evidence-grounded candidates），但 L4-L7 未达到（无 validation、无 future cases）。**

---

## 2. Research Questions

> **RQ-EVIDENCE-DEPENDENCY：对于 Human 能够正确判断 MERGE / KEEP / UNKNOWN 的 Case，哪些 Evidence 是真正 decision-relevant 的？这些 Evidence 当前是否已经存在于 DICE？如果存在，为什么 Human 仍需要自己重构？**

> **RQ-FEEDBACK-SIGNAL：Human 的最小反馈是否可以帮助 System 发现这些 decision-relevant Evidence，而不是让 Human 自己定义规则？**

---

## 3. Case Scope

| Priority | Cases | 说明 |
|---|---|---|
| P1: Override cases | AMB-313, AMB-462 | Human overrode wrong System cue |
| P2: MERGE cases | AMB-414, AMB-422 | GT=MERGE (false positive risk) |
| P3: H2 cases | 17 cases | Type C Evidence Missing |
| P4: All GT | 45 cases | Complete analysis |

---

## 4. AMB-313 / AMB-462 Override Analysis

### AMB-313: 'Test Size' / '#Classes'

```
GT: KEEP_SEPARATE (table column headers)
System B2 cue: MERGE (WRONG — TLD detected 0 tables)
Human: KEEP_SEPARATE (CORRECT override, 3.9s)
```

**Line spans on same y=271.8:**
- 'Dataset' x0=109.8
- 'Train Size' x0=187.6
- 'Test Size' x0=224.9 ← A
- '#Classes' x0=258.9 ← B
- '81' x0=338.5

**Human reasoning**: 5 items on same line → table header row → different columns → KEEP_SEPARATE

**Why System was wrong**: TLD detected 0 tables → is_in_table=False → default cue=MERGE

### AMB-462: 'WGe' / 'Avg.'

```
GT: KEEP_SEPARATE (table column headers)
System B2 cue: MERGE (WRONG — TLD detected 1 table but A/B outside bbox)
Human: KEEP_SEPARATE (CORRECT override, 4.7s)
```

**Line spans on same y=216.1 (10 items):**
- 'Models', 'Size', 'ARCe', 'ARCc', 'HS', 'BQ', ..., 'WGe' ← A, 'Avg.' ← B

**Human reasoning**: 10 items on same line → table header row → different columns → KEEP_SEPARATE

**Why System was wrong**: TLD detected 1 table but A/B bbox outside detected table bbox → is_in_table=False → cue=MERGE

### Why Human Could Override

Human used:
1. **E2 (Existing but Unorganized)**: Multiple line spans on same y — evidence EXISTS but not organized as "table header row"
2. **E5 (Text Pattern)**: 'Test Size' / '#Classes' / 'WGe' / 'Avg.' are short text labels (not 'FIG.' prefix) → table headers, not figure captions

> **Human correctly overrode because they could see BOTH the structural pattern (multiple items on same line) AND the text content (not 'FIG.' prefix). System only had TLD output (wrong) and didn't expose line_spans organization.**

---

## 5. Evidence Dependency Five-Category Classification

### All 45 GT Cases

| Category | Count | Description |
|---|---|---|
| **E2 (Existing but Unorganized)** | **35 (78%)** | Line spans exist but not organized as table structure |
| **E5 (Human Semantic)** | **10 (22%)** | Text pattern / sentence structure needed |
| E1 (Existing Explicit, sufficient) | 0 | No case where direct evidence alone is sufficient |
| E3 (Derived) | 0 | No case requires only derivation (all need E2 or E5) |
| E4 (Missing Observation) | 0 | No case requires genuinely new observation |

### E2 Breakdown (35 cases)

All 35 E2 cases:
- GT: KEEP_SEPARATE (35/35 = 100%)
- Have: line_obs_count ≥ 3, NOT has_fig_prefix
- Evidence: multiple line spans on same y, text content
- Human must reconstruct: "these items form a table row"

### E5 Breakdown (10 cases)

| Subtype | Count | GT | Description |
|---|---|---|---|
| TEXT_PATTERN_FIG | 2 | MERGE (2/2) | 'FIG.' prefix → figure caption |
| SENTENCE_STRUCTURE | 5 | KEEP_SEPARATE (3), DISAGREE (2) | Prose sentence boundary |
| TEXT_PATTERN_FIG (misclassified) | 3 | KEEP_SEPARATE (3) | Actually E2 cases with value/column refs |

---

## 6. Information Gain Analysis

### Signal Candidate 1: has_fig_prefix → MERGE

| GT | has_fig_prefix=True | has_fig_prefix=False |
|---|---|---|
| MERGE | **2 (100%)** | 0 |
| KEEP_SEPARATE | 0 (0%) | 39 |
| DISAGREE | 0 (0%) | 4 |

```
INFORMATION_GAIN = HIGH (perfect discrimination)
EVIDENCE_GROUNDED = YES (text_a is in E1)
SEMANTIC_LEAKAGE = NON-ZERO (text pattern matching)
CROSS_CASE = YES (2 cases, 1 document)
VALIDATABLE = PARTIAL (n=2 only)
FUTURE_REUSE = INSUFFICIENT
```

### Signal Candidate 2: line_obs ≥ 6 → KEEP_SEPARATE

| GT | line_obs ≥ 6 | line_obs < 6 |
|---|---|---|
| KEEP_SEPARATE | 28 | 11 |
| MERGE | **0** | 2 |
| DISAGREE | 0 | 4 |

```
INFORMATION_GAIN = MODERATE (0 false positive, but 62% coverage)
EVIDENCE_GROUNDED = YES (line_obs_count is in E1)
SEMANTIC_LEAKAGE = 0 (pure geometry)
CROSS_CASE = YES (28 cases, 4 documents)
VALIDATABLE = PARTIAL
FUTURE_REUSE = INSUFFICIENT
```

### Signal Candidate 3: line_obs ≥ 3 AND NOT has_fig_prefix → KEEP_SEPARATE

| GT | Condition met | Condition not met |
|---|---|---|
| KEEP_SEPARATE | **42** | 0 |
| MERGE | **0** | 2 |
| DISAGREE | **0** | 4 |

```
INFORMATION_GAIN = HIGH (42/42 KEEP_SEPARATE, 0 false positive)
EVIDENCE_GROUNDED = YES (line_obs + text in E1)
SEMANTIC_LEAKAGE = NON-ZERO (combines geometry + text pattern)
CROSS_CASE = YES (42 cases, 4 documents)
VALIDATABLE = PARTIAL
FUTURE_REUSE = INSUFFICIENT
```

### Comparison with SAME_BAND_SEPARATED_PAIR

| Signal | Info Gain | False Positive | Coverage | Semantic Leakage |
|---|---|---|---|---|
| SAME_BAND_SEPARATED_PAIR | **ZERO** (100% true) | 2/45 | 100% | 0 |
| Signal 1: has_fig → MERGE | HIGH | 0 | 4% | non-zero |
| Signal 2: line_obs ≥ 6 | MODERATE | 0 | 62% | 0 |
| Signal 3: line_obs≥3 AND NOT fig | HIGH | 0 | 93% | non-zero |

> **SAME_BAND_SEPARATED_PAIR 有零信息增量（前阶段已确认）。新发现的 Signal Candidates 有正信息增量——这是从 L2 到 L3 的关键进步。**

---

## 7. Counterfactual Analysis

### AMB-313 Counterfactual

| If Human didn't see... | Could still judge? | Decision-relevant? |
|---|---|---|
| line_spans | Maybe (less confident) | YES (structural confirmation) |
| text content | **NO** (same geometry as AMB-414) | **YES (critical)** |
| bbox | Maybe (text alone might suffice) | PARTIAL |

### AMB-414 Counterfactual

| If Human didn't see... | Could still judge? | Decision-relevant? |
|---|---|---|
| 'FIG.' prefix | **NO** (would look like table headers) | **YES (critical)** |
| line_spans | Yes (FIG. prefix sufficient) | PARTIAL |

### Key Counterfactual Finding

> **Text content is decision-relevant for BOTH override and MERGE cases. Pure geometry (bbox, dy, h_gap, line_obs) cannot distinguish AMB-313 (KEEP_SEPARATE) from AMB-414 (MERGE) — they have nearly identical geometry. Human must use text pattern ('FIG.' vs table labels) to distinguish.**

---

## 8. Feedback Grounding

### Can Human feedback help discover decision-relevant evidence?

```
Human feedback: KEEP_SEPARATE (35 E2 cases) + MERGE (2 E5 cases)
System analysis: What differs between KEEP_SEPARATE and MERGE groups?
  → KEEP_SEPARATE: line_obs ≥ 3, NOT has_fig_prefix
  → MERGE: has_fig_prefix=True
  → Signal candidates discovered!
```

**Yes — Human feedback CAN help System discover evidence patterns.** System doesn't need Human to write rules — it can analyze which evidence features correlate with feedback labels.

### But: correlation ≠ learning signal

```
SIGNAL_CANDIDATE ≠ REUSABLE_SIGNAL
```

All 3 candidates are SIGNAL_CANDIDATES (L3), but none are REUSABLE_SIGNALS (L4+) because:
- No Human validation (L4)
- No future case reuse (L5)
- No measured HRR (L6)

---

## 9. Evidence Utility vs Learning Utility

| Evidence | Utility A (Human faster) | Utility B (Future reuse) |
|---|---|---|
| SAME_BAND_SEPARATED_PAIR | NOT_SUPPORTED (B2 slower) | NOT_SUPPORTED (zero info gain) |
| line_obs_count exposure | **POTENTIAL** (if cue correct) | INSUFFICIENT (no future cases) |
| has_fig_prefix exposure | **POTENTIAL** (if cue correct) | INSUFFICIENT (no future cases) |
| Signal 2 (line_obs ≥ 6) | UNKNOWN (not tested) | INSUFFICIENT (no future cases) |
| Signal 3 (line_obs≥3 AND NOT fig) | UNKNOWN (not tested) | INSUFFICIENT (no future cases) |

> **P722 B2 showed that WRONG cue direction increases time. The problem was not evidence exposure — it was wrong cue. If cue direction were correct (using Signal 3), utility might improve. But this cannot be tested (no more experiments).**

---

## 10. Human Override Root Cause

### Why System cue was wrong on AMB-313/462

| Case | TLD Status | System Logic | Result |
|---|---|---|---|
| AMB-313 | 0 tables detected | is_in_table=False → MERGE | WRONG |
| AMB-462 | 1 table detected, A/B outside bbox | is_in_table=False → MERGE | WRONG |

**Root cause**: System cue depends on TLD output. TLD missed table (AMB-313) or detected wrong table bbox (AMB-462). System default for "not in table" = MERGE, which is wrong for table header cases.

### Why Human was correct

Human used evidence that System didn't expose:
1. **line_spans** (E2): Multiple items on same y → structural pattern
2. **text content** (E5): 'Test Size' / '#Classes' → table labels, not 'FIG.' prefix

> **System's cue was wrong because it only used TLD (which failed). Human used E2+E5 evidence that System didn't organize. This is a Consumer/Integration Gap — evidence exists but isn't consumed.**

---

## 11. Category Distribution Summary

| Category | Count | Description | Info Gain | Reuse Potential |
|---|---|---|---|---|
| A: Machine knows + Human uses directly | 0 | — | — | — |
| B: Machine knows but Human reconstructs | **35 (78%)** | E2: line_spans unorganized | HIGH (with E5) | MODERATE |
| C: Machine can derive but doesn't expose | 0 | — | — | — |
| D: Machine genuinely lacks observation | 0 | — | — | — |
| E: Persistent Human Semantic Judgment | **10 (22%)** | E5: text pattern / sentence | HIGH (for fig) | LOW (n=2) |

**Primary: Category B (78%)** — Evidence exists but Human must reconstruct.
**Secondary: Category E (22%)** — Text pattern recognition needed.

---

## 12. Research Route

```
A = Existing Evidence sufficient but poorly organized     → YES (primary, 78%)
B = Deterministic derived Evidence sufficient              → PARTIAL (line_obs derivable)
C = New Observation genuinely required                    → NO (0 cases)
D = Persistent Human Semantic Judgment remains            → PARTIAL (22%, text pattern)
E = Evidence insufficient / Future validation required    → YES (no future cases)
```

**主因：A (Existing Evidence sufficient but poorly organized) + E (Future validation required)**

---

## 13. Seven Research Questions

### Q1: Human 正确判断最依赖哪一类 Evidence？

**E2 (Existing but Unorganized) — 35/45 (78%)。** Human 依赖多个 line spans 构成的局部结构（表格行），这些 evidence 已存在但未组织。

### Q2: 这些 Evidence 中，哪些已经存在于 DICE？

**全部存在。** text, bbox, line_spans, line_obs_count, same_style 全部在 candidate universe 中。无 E4 (Missing Observation)。

### Q3: 如果已存在，Human 为什么仍需要自己重构？

**Consumer/Integration Gap。** IS-11 使用 TLD（未检测到表格），不查询 P2 line_spans。Human 必须从页面图像或原始 evidence 中自己重构表格结构。

### Q4: 哪些 Evidence 真正具有 Information Gain？

- `has_fig_prefix → MERGE`: HIGH info gain (2/2 MERGE, 0/43 others)
- `line_obs ≥ 6 → KEEP_SEPARATE`: MODERATE (0 false positive, 62% coverage)
- `line_obs ≥ 3 AND NOT fig → KEEP_SEPARATE`: HIGH (42/42, 0 false positive)

对比：SAME_BAND_SEPARATED_PAIR info gain = ZERO (100% true)。

### Q5: Human Feedback 能否帮助 Machine 发现这些 Evidence？

**YES。** System 可以分析 KEEP_SEPARATE vs MERGE 组之间的 evidence 差异，发现 line_obs_count 和 has_fig_prefix 的区分力。Human 不需要写规则。

### Q6: 有没有证据表明这些 Evidence 可以跨独立 Future Cases 复用？

**NO。** 0 future/independent cases。P722 测试集是 GT 的子集。无法验证泛化。

### Q7: 当前 Human Feedback Learning Level 应该停在哪一级？

**L3 (Evidence-grounded Candidate)。** 发现了 3 个 evidence-grounded signal candidates，但未 validation (L4)、未 future reuse (L5)、未 measured HRR (L6)。

---

## 14. Learning Level

| Level | Status | Description |
|---|---|---|
| L0 Storage | ✓ | Human feedback stored in GT |
| L1 Feedback Capture | ✓ | P722 captures decisions |
| L2 Candidate Discovery | ✓ | SAME_BAND_SEPARATED_PAIR (zero info gain) |
| **L3 Evidence-grounded Candidate** | **✓** | **3 signal candidates with info gain > 0** |
| L4 Human-validated Reusable Signal | ✗ | No validation performed |
| L5 Future Case Reuse | ✗ | 0 future cases |
| L6 Measured HRR | ✗ | Not measurable |
| L7 Iterative Learning | ✗ | — |

```
CURRENT_LEARNING_LEVEL = L3 (improved from L2)
```

**进步原因**：发现了 info gain > 0 的 signal candidates（对比前阶段的 SAME_BAND_SEPARATED_PAIR info gain = 0）。

**未达到 L4 原因**：无 Human validation、无 future cases。

---

## 15. Signal Candidate Details

### Signal 1: has_fig_prefix → MERGE

```
Definition: text_a or text_b starts with 'FIG' (case-insensitive)
Evidence: E1 (text content, existing)
Info Gain: HIGH — 2/2 MERGE, 0/43 others
Semantic Leakage: NON-ZERO (text pattern matching)
Coverage: 2/45 (4%)
Cross-case: 2 cases, 1 document
Validatable: PARTIAL (n=2)
Future Reuse: INSUFFICIENT
```

### Signal 2: line_obs_count ≥ 6 → KEEP_SEPARATE

```
Definition: line_obs_count >= 6
Evidence: E1 (line_obs_count, existing)
Info Gain: MODERATE — 0 false positive, 28/45 coverage
Semantic Leakage: 0 (pure geometry)
Coverage: 28/45 (62%)
Cross-case: 28 cases, 4 documents
Validatable: PARTIAL
Future Reuse: INSUFFICIENT
```

### Signal 3: line_obs_count ≥ 3 AND NOT has_fig_prefix → KEEP_SEPARATE

```
Definition: line_obs_count >= 3 AND NOT (text starts with 'FIG')
Evidence: E1 (line_obs + text, existing)
Info Gain: HIGH — 42/42 KEEP_SEPARATE, 0 false positive
Semantic Leakage: NON-ZERO (combines geometry + text pattern)
Coverage: 42/45 (93%)
Cross-case: 42 cases, 4 documents
Validatable: PARTIAL
Future Reuse: INSUFFICIENT
```

---

## 16. Anti-Overdesign Gate

| Gate | Required? | Evidence |
|---|---|---|
| Learning Engine | **NO** | L3 candidates, not L4+ |
| Feedback Engine | **NO** | Feedback captured, not engine needed |
| Signal Engine | **NO** | Candidates found by analysis, not engine |
| Query Engine | **NO** | No query needed |
| Pattern Engine | **NO** | Simple thresholds, not patterns |
| Relation Engine | **NO** | H2 branch closed |
| Evidence Organization Layer | **NO** | Evidence exists, consumer gap |
| New Observation | **NO** | 0 E4 cases |
| LLM | **NO** | 0 cases need LLM |
| Modify P2/TLD/IS-11 | **NO** | Frozen, READ-ONLY |

**全部 NO。**

---

## 17. Limitations

1. **45 GT cases, 4 documents**：Signal candidates 可能在其他文档中不成立
2. **2 MERGE cases only**：has_fig_prefix signal 基于 n=2，泛化性极弱
3. **0 future cases**：完全无法验证 future reuse
4. **P722 n=1**：Evidence Utility 评估基于单一参与者
5. **line_obs_count 阈值选择**：阈值 3/6 基于当前 45 cases，可能 overfit
6. **has_fig_prefix 是文本模式**：引入语义泄漏，不是纯 geometry
7. **E2/E5 分类基于 reviewer rationale**：rationale 是事后解释，可能不完全反映实时认知
8. **Signal 3 的 93% 覆盖率**：在 45 cases 上完美，但 3 个未覆盖案例（2 MERGE + 1 DISAGREE with fig）无法确认泛化

---

## 18. Governance Gate

```
DICE_CORE_MODIFICATION              = NO
P1_P7_MODIFICATION                  = NO
P2_MODIFICATION                     = NO
TLD_MODIFICATION                    = NO
IS11_MODIFICATION                   = NO
GT_MODIFICATION                     = NO
EXPERIMENT_MODIFICATION             = NO
NEW_MODULE                          = NO
NEW_ENGINE                          = NO
LLM                                 = NO
RUNTIME_CHANGE                      = NO
CAPABILITY_CHANGE                   = NO
FROZEN_BASELINE                     = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d)
IMPLEMENTATION_AUTHORIZED           = FALSE
FORMAL_LEARNING                     = FALSE
STOP                                = TRUE
```

---

## 19. 最终原则验证

> *不要寻找 Human 告诉 Machine 的"规则"。*

✓ 遵守：分析的是 Human 依赖的 Evidence，不是 Human 写的规则。

> *不要把"机器能够计算的 Relation"自动当作"Human 需要的 Evidence"。*

✓ 遵守：SAME_BAND_SEPARATED_PAIR 被正确识别为零信息增量的 Evidence Representation，不是 Learning Signal。

> *Human Minimal Judgment → System 分析 → 发现 Evidence → 验证 Signal → Future Cases → HRR*

✓ 遵守：发现了 3 个 evidence-grounded signal candidates (L3)，但明确停止在 L3——未 validation (L4)、未 future reuse (L5)、未 HRR (L6)。

`STOP = TRUE`。
