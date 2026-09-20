# Boundary Resolution Ambiguity Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY / NO MODIFICATION / FROZEN INTACT / STOP

---

## 1. Executive Summary

```
ROOT_CAUSE_PRIMARY     = A. STANDARD_GAP (4/5 boundary cases, 80%)
ROOT_CAUSE_SECONDARY   = B. EVIDENCE_ORGANIZATION_GAP (1/5, AMB-032)
PERSISTENT_SEMANTIC_AMBIGUITY = NOT_FOUND

KEY DISCOVERY:
  ALL 4 reviewer disagreement cases share IDENTICAL adjudication rationale:
    "Text_a ends with sentence-ending punctuation and text_b starts with
     capital — likely separate sentences."
  
  → The adjudicator used period_end + cap_start (a DETERMINISTIC, E3 feature)
    to resolve ALL 4 disagreements → KEEP_SEPARATE
  → The disagreement was NOT about semantic interpretation
  → The disagreement was about STANDARD: "text unit" was undefined
    - Reviewer A: text unit = sentence → KEEP_SEPARATE
    - Reviewer B: text unit = paragraph → MERGE
    - Adjudicator: text unit = sentence (period+cap → KEEP_SEPARATE)

COUNTERFACTUAL:
  If annotation protocol had defined "text unit = sentence (period+capital delimited)",
  ALL 4 disagreements would disappear → NOT persistent semantic ambiguity

ADJUDICATOR RULE (period+cap → KEEP_SEPARATE):
  - 100% consistent with final GT on all 4 triggering cases
  - 0 false positives on 45 cases
  - DETERMINISTIC (derivable from P1 text)
  - HUMAN-VALIDATED (applied by expert adjudicator)
  - STRONGER than Signal 3 (RESOLVES boundary, not just detects)

FINAL_STATUS           = PARTIALLY_SUPPORTED
L3_SIGNAL_CANDIDATE    = YES (adjudicator rule is evidence-grounded + human-validated)
L4_CANDIDATE_READY     = FALSE (n=4, no future cases, rule not in Signal 3)
STOP                   = TRUE
```

> **Human 在 Boundary Resolution 上的不稳定主要来自 STANDARD_GAP（80%）——标注协议未定义 "文本单元"（text unit），导致 Reviewer A 理解为 "句子"，Reviewer B 理解为 "段落"。 adjudicator 使用确定性特征（period_end + cap_start）解决了全部 4 个分歧，选择了 "句子 = 文本单元" 的标准。这不是 Persistent Semantic Ambiguity——如果标准明确，分歧消失。AMB-032 的 UNKNOWN 来自 EVIDENCE_ORGANIZATION_GAP——TLD 正确检测了表格，但 P722 参与者无法从展示的几何特征验证表格结构。未发现任何案例满足 Persistent Semantic Ambiguity 的条件。**

---

## 2. Research Question

> 在 Boundary Detection 已经成立的情况下，Human 为什么仍然无法稳定决定 KEEP_SEPARATE / MERGE？

---

## 3. Cases Analyzed

| Case | Type | GT | Reviewer A | Reviewer B | Final | P722 B2 |
|---|---|---|---|---|---|---|
| AMB-005 | Disagreement | KEEP | KEEP | MERGE | KEEP | KEEP (3.4s) |
| AMB-375 | Disagreement | KEEP | KEEP | MERGE | KEEP | UNKNOWN (31.3s) |
| AMB-418 | Disagreement | KEEP | KEEP | MERGE | KEEP | KEEP (12.2s) |
| AMB-519 | Disagreement | KEEP | KEEP | MERGE | KEEP | KEEP (2.0s) |
| AMB-032 | UNKNOWN | KEEP | KEEP | KEEP | KEEP | UNKNOWN (45.9s) |

Plus comparison with 38 CLEARLY_SUPPORTED and 2 CLEARLY_UNSUPPORTED cases.

---

## 4. Boundary Detection Status

```
BOUNDARY_DETECTION = ESTABLISHED (from previous audit)
  period_end + cap_start: 4/4 BOUNDARY, 0/38 CLEAR, 0/2 UNSUPPORTED, 0/1 UNKNOWN
  Derivable from P1 text (E3)
  Not in Signal 3 (cannot modify)
```

---

## 5. Boundary Resolution Status

### 5.1 The Core Question

> 当 Boundary 被识别后（period+cap=True），Human 能否稳定决定 KEEP vs MERGE？

### 5.2 Answer

**NO — but NOT because of semantic ambiguity.**

The instability comes from **STANDARD_GAP**: the annotation protocol defines:

```
MERGE — 两个片段属于同一文本单元
KEEP_SEPARATE — 两个片段不属于同一文本单元
```

But **"文本单元" (text unit) is NOT defined**. This creates two interpretations:
- Reviewer A: text unit = sentence → period+cap = different sentences → KEEP_SEPARATE
- Reviewer B: text unit = paragraph → same paragraph = same unit → MERGE

### 5.3 Adjudicator Resolution

ALL 4 disagreement cases have **IDENTICAL** adjudication rationale:

> "Text_a ends with sentence-ending punctuation and text_b starts with capital — likely separate sentences."

The adjudicator:
1. Used period_end + cap_start (deterministic E3 feature)
2. Chose "sentence = text unit" standard
3. Resolved ALL 4 cases to KEEP_SEPARATE
4. Applied the SAME rule consistently

---

## 6. AMB-024 vs AMB-375 Comparison

### 6.1 Evidence Table

| Feature | AMB-024 (CLEAR) | AMB-375 (BOUNDARY) | In Signal 3? | Distinguishes? |
|---|---|---|---|---|
| text_a | '28.54' | '[23].' | NO | YES (content) |
| text_b | '10.02' | 'Each' | NO | YES (content) |
| line_obs | 3 | 3 | YES | NO (same) |
| has_fig | False | False | YES | NO (same) |
| period_end | **False** | **True** | NO | **YES** |
| cap_start | **False** | **True** | NO | **YES** |
| TLD is_in_table | True | False | NO | YES |
| h_gap | 25.0 | 9.7 | NO | Partially |
| reviewer A | KEEP | KEEP | — | Same |
| reviewer B | KEEP | **MERGE** | — | **DIFFERENT** |
| adjudication | N/A (agreed) | period+cap → KEEP | — | — |

### 6.2 What Machine Lacks

Machine lacks **period_end + cap_start** — a deterministic feature derivable from P1 text. This feature:
- Perfectly distinguishes CLEAR (0/38) from BOUNDARY (4/4)
- Was used by the adjudicator to resolve ALL disagreements
- Is NOT in Signal 3 (cannot modify)

### 6.3 Why Human Can Distinguish

- AMB-024: Human sees numeric values → table cells → KEEP (no ambiguity)
- AMB-375: Human sees '[23].' (citation ending sentence) + 'Each' (new sentence) → sentence boundary → but is "same paragraph" → KEEP or MERGE? → STANDARD ambiguity

> **The difference is NOT that Human uses "higher-level semantic understanding". The difference is that Human sees text content (period, capital) that Signal 3 doesn't check. Once the standard is clarified (sentence = text unit), the decision is deterministic.**

---

## 7. Reviewer Disagreement Source Analysis

### Q1: Two reviewers saw the same Evidence?

**YES.** Both reviewers saw the same text, same geometry, same page context. Both explicitly mention "sentence boundary" and "same paragraph" in their rationales.

### Q2: Used different standards?

**YES — this is the root cause.**
- Reviewer A: "text unit = sentence" → different sentences → KEEP_SEPARATE
- Reviewer B: "text unit = paragraph" → same paragraph → MERGE

### Q3: Different evidence sources (page image vs text)?

**NO.** Both reviewers reference text content and paragraph context. No evidence of different modalities.

### Q4: Evidence exists but not explicitly shown?

**YES — partially.** period_end and cap_start exist in P1 text but are not computed/exposed as features. However, both reviewers explicitly noted them in rationales.

### Q5: Evidence can be deterministically composed?

**YES.** period_end = text_a.endswith('.'), cap_start = text_b[0].isupper() — trivial string checks.

### Q6: Boundary Cue explains disagreement?

**YES.** period+cap=True is the boundary cue. When present, the "sentence vs paragraph" standard ambiguity triggers.

### Q7: If same complete Evidence given, disagreement still possible?

**YES — but only because the STANDARD is ambiguous, not because of semantic ambiguity.** If the standard defined "text unit = sentence", disagreement would disappear.

### Q8: What type of disagreement?

**STANDARD_AMBIGUITY** — the annotation protocol doesn't define "text unit". This is NOT:
- random noise (pattern is consistent: all 4 cases have same structure)
- case ambiguity (the cases are clear sentence-boundary cases)
- annotation ambiguity (both reviewers understood the task)
- evidence ambiguity (both saw the same evidence)
- persistent semantic ambiguity (standard clarification resolves it)

---

## 8. Human Effort vs Information Gain

| Case | P722 Time | Evidence Inspected | Expanded Fields | Decision | Info Gain |
|---|---|---|---|---|---|
| AMB-005 | 3.4s | No | None | KEEP | Low effort, correct |
| AMB-375 | 31.3s | Yes | ALL 7 fields | **UNKNOWN** | High effort, uncertain |
| AMB-418 | 12.2s | No | None | KEEP | Medium effort, correct |
| AMB-519 | 2.0s | No | None | KEEP | Low effort, correct |
| AMB-032 | 45.9s | Yes | ALL 7 fields | **UNKNOWN** | High effort, uncertain |

### Pattern

- **Low effort + correct**: AMB-005, 519 — participant followed cue or made quick judgment
- **High effort + uncertain**: AMB-375, 032 — participant expanded ALL fields, spent 31-46s, still UNKNOWN

### Key Insight

> **High effort cases (AMB-375, 032) involved Evidence Reconstruction — participant had to reconstruct context from geometry fields. The geometry fields (h_gap, dy, same_style, width, style_sig) don't directly convey "sentence boundary" or "table structure". Participant needed text content + context, but only got geometry.**

---

## 9. "Human Semantic Gap" Re-examination

### 9.1 The Hypothesis

Previous audits classified the 4 boundary cases as PERSISTENT_HUMAN_SEMANTIC_BOUNDARY. This audit re-examines that classification.

### 9.2 Evidence Against Persistent Semantic Ambiguity

1. **Adjudicator resolved ALL 4 with a deterministic rule** (period+cap → KEEP_SEPARATE)
2. **Adjudicator's rule is consistent** across all 4 cases (identical rationale)
3. **Both reviewers agree on facts** (period, capital, same paragraph) — they disagree on standard
4. **If standard clarified, disagreement disappears** (counterfactual test passed)
5. **The resolving feature is E3 (derivable)** — not E5 (semantic)

### 9.3 Evidence For STANDARD_GAP

1. Protocol defines MERGE/KEEP_SEPARATE using "文本单元" (text unit) — undefined term
2. Reviewer A: text unit = sentence; Reviewer B: text unit = paragraph
3. Adjudicator: text unit = sentence (clarified the standard)
4. All 4 cases have identical structure (sentence boundary within paragraph)

### 9.4 Conclusion

```
PERSISTENT_SEMANTIC_AMBIGUITY = NOT_FOUND
```

> **The 4 disagreement cases are STANDARD_GAP, not PERSISTENT_SEMANTIC_AMBIGUITY. The adjudicator resolved them with a deterministic feature (period+cap). If the annotation standard had defined "text unit = sentence", no disagreement would have occurred.**

---

## 10. Cause Distribution

| Cause | Count | Cases | Description |
|---|---|---|---|
| **A. STANDARD_GAP** | **4 (80%)** | AMB-005, 375, 418, 519 | "Text unit" undefined; sentence vs paragraph interpretation |
| **B. EVIDENCE_ORGANIZATION_GAP** | **1 (20%)** | AMB-032 | TLD correct but table structure not organized for participant |
| C. EVIDENCE_MISSING | 0 | — | No case requires genuinely missing observation |
| D. PERSISTENT_SEMANTIC_AMBIGUITY | 0 | — | No case where evidence+standard+organization sufficient but Human still disagrees |
| UNKNOWN | 0 | — | — |

---

## 11. Adjudicator Rule Assessment

### 11.1 The Rule

```
IF period_end=True AND cap_start=True THEN KEEP_SEPARATE
```

### 11.2 Properties

| Property | Value |
|---|---|
| Deterministic | YES (trivial string checks on P1 text) |
| Evidence-grounded | YES (period and capital in P1 text, E3) |
| Consistent | YES (same rationale for all 4 cases) |
| Human-validated | YES (applied by expert adjudicator) |
| Coverage | 4/45 cases (9%) — only triggers on sentence-boundary cases |
| False positive | 0/45 (0%) |
| Resolves boundary | YES (not just detects — gives KEEP_SEPARATE) |
| In Signal 3 | NO (cannot modify) |

### 11.3 Comparison with Signal 3

| Aspect | Signal 3 | Adjudicator Rule |
|---|---|---|
| Features | line_obs ≥ 3, NOT fig | period_end, cap_start |
| Coverage | 42/45 (93%) | 4/45 (9%) |
| False positive | 0 | 0 |
| Boundary handling | OVERCOMMIT (no UNKNOWN) | RESOLVES (KEEP_SEPARATE) |
| Human-validated | NO | YES (adjudicator) |
| Status | L3 Candidate | RETROSPECTIVE_DISCRIMINATIVE_FEATURE |

### 11.4 Can This Be a Learning Signal?

**YES — as L3_SIGNAL_CANDIDATE:**
- Evidence-grounded (E3, derivable from P1)
- Human-validated (adjudicator applied it)
- Info gain > 0 (resolves disagreements)
- Cross-case (4 cases, 3 documents)
- Consistent (identical rationale)

**NO — as L4_REUSABLE_SIGNAL:**
- n=4 (too few)
- No future cases
- Not in Signal 3 (cannot implement)
- No measured HRR

---

## 12. Does Human Need Higher-Level Semantic Understanding?

### Q3: Human 是否真的需要"更高层语义理解"？

**NO.**

The 4 disagreement cases were resolved by a **deterministic string check** (period + capital). The adjudicator did NOT use "higher-level semantic understanding" — they used a simple structural feature that exists in P1 text.

### Q4: Human 是否需要 Document Discourse Structure？

**NO.**

No case required understanding document discourse (paragraph function, heading hierarchy, section structure). The adjudicator's rule uses only local text features (period, capital).

### Q5: Human 是否需要 LLM？

**NO.**

All boundary resolution can be achieved with deterministic string checks. No case requires natural language understanding beyond "does text end with period?" and "does next text start with capital?".

---

## 13. What Is Actually Missing?

| Component | Missing? | Detail |
|---|---|---|
| Observation | **NO** | All evidence in P1 text |
| Evidence Organization | **PARTIAL** | period+cap not computed; table structure not organized for AMB-032 |
| Evidence Interpretation | **NO** | No interpretation needed beyond string checks |
| Human Semantic Judgment | **NO** | Adjudicator resolved with deterministic rule |
| **Evaluation Standard** | **YES** | "Text unit" undefined in annotation protocol |

> **当前主要缺失的是 Evaluation Standard——标注协议未定义 "文本单元"。其次是 Evidence Organization——period+cap 未计算，table structure 未为参与者组织。**

---

## 14. Minimal Human Question

### The Question

> "这两部分是否属于同一个内容单元？"

### Answer Space

- MERGE
- KEEP_SEPARATE
- UNKNOWN

### Is This Sufficient?

**YES — the question is sufficient.** The problem is NOT the question or the answer space. The problem is that **"内容单元" (content unit) is undefined**, causing different interpretations.

If the standard clarified:
- "content unit = sentence (delimited by period + capital)"
Then the question becomes unambiguous and the answer is deterministic.

> **缺少的不是更多按钮或更复杂的问题，而是 Evaluation Standard 的明确定义。**

---

## 15. Learning Signal Candidates

### Adjudicator Rule: period_end + cap_start → KEEP_SEPARATE

```
L3_SIGNAL_CANDIDATE = YES
  - Evidence-grounded: E3 (derivable from P1 text)
  - Human-validated: adjudicator applied it
  - Info gain > 0: resolves 4/4 disagreements
  - Cross-case: 4 cases, 3 documents
  - Consistent: identical rationale
  - 0 false positive on 45 cases

L4_REUSABLE_SIGNAL = NO
  - n=4 (too few)
  - No future cases
  - Not in Signal 3 (cannot implement)
  - No measured HRR
```

### Signal 3 (existing)

```
L3_SIGNAL_CANDIDATE = YES (retained)
  - 38/38 CLEAR cases correct
  - But BOUNDARY_OVERCOMMIT (no UNKNOWN output)
  - Retained as L3, not upgraded
```

---

## 16. Final Output Matrix

| Dimension | Result |
|---|---|
| Boundary Detection | ESTABLISHED (period+cap, 4/4 vs 0/38) |
| Boundary Resolution | PARTIALLY_SUPPORTED (adjudicator rule works, but standard unclear) |
| STANDARD_GAP | 4/5 (80%) |
| EVIDENCE_ORGANIZATION_GAP | 1/5 (20%) |
| EVIDENCE_MISSING | 0 |
| PERSISTENT_SEMANTIC_AMBIGUITY | NOT_FOUND |
| Document Discourse Needed | NO |
| LLM Needed | NO |
| New Observation Needed | NO |
| New Architecture Needed | NO |
| L3 Signal Candidate | YES (adjudicator rule) |
| L4 Candidate Ready | NO (n=4, no future cases) |

---

## 17. Final Research Questions

### Q1: Boundary Detection 和 Boundary Resolution 的真正边界在哪里？

**Boundary Detection** = 识别 period+cap=True（确定性，E3，可派生）。
**Boundary Resolution** = 决定 KEEP/MERGE。当前需要标准明确（"text unit = sentence"）。一旦标准明确，resolution 也是确定性的。

### Q2: AMB-005/375/418/032 的 disagreement 主要来自什么？

**STANDARD_GAP (4/4)**。标注协议未定义 "文本单元"。Reviewer A = sentence，Reviewer B = paragraph。Adjudicator 用 period+cap 解决。

**EVIDENCE_ORGANIZATION_GAP (AMB-032)**。TLD 正确但 table structure 未为参与者组织。

### Q3: Human 是否真的需要"更高层语义理解"？

**NO。** Adjudicator 用确定性字符串检查（period + capital）解决了全部分歧。

### Q4: Human 是否需要 Document Discourse Structure？

**NO。** 无案例需要 discourse 理解。局部文本特征（period, capital）足够。

### Q5: Human 是否需要 LLM？

**NO。** 所有 resolution 可通过确定性字符串检查完成。

### Q6: 当前缺的是什么？

**主要：Evaluation Standard**（"文本单元" 未定义）。
**次要：Evidence Organization**（period+cap 未计算；table structure 未组织）。

### Q7: 是否存在真正的 Persistent Human Semantic Judgment？

**NO。** 未发现任何案例满足条件（evidence + standard + organization 全部充分但 Human 仍分歧）。所有分歧在标准明确后消失。

### Q8: 是否存在可验证的 L3 Learning Signal Candidate？

**YES。** Adjudicator rule（period+cap → KEEP_SEPARATE）是 evidence-grounded + human-validated + info gain > 0。但 n=4，无 future cases，不能升级 L4。

### Q9: 下一步应该？

**C. 增加 Evaluation / GT 标准**（主要）——明确 "text unit" 定义。
**B. 增加最小 Deterministic Derivation**（次要）——计算 period+cap。
**E. 扩展独立 Corpus**（未来）——验证 adjudicator rule 泛化性。

---

## 18. Final Status

```
FINAL_STATUS = PARTIALLY_SUPPORTED
```

**PARTIALLY_SUPPORTED** 因为：
- Boundary Detection 已建立（period+cap, 确定性）
- Boundary Resolution 有 adjudicator rule（human-validated, deterministic）
- 但 STANDARD 未明确（导致初始分歧）
- 且 rule 未在 Signal 3 中（不能实现）
- 且 n=4, 无 future cases（不能升级 L4）

---

## 19. Next Research Route

```
PRIMARY: C. 增加 Evaluation / GT 标准
  → 明确 "text unit" 定义（sentence vs paragraph）
  → 这是最高优先级——解决标准模糊性

SECONDARY: B. 增加最小 Deterministic Derivation  
  → 计算 period_end + cap_start（retrospective discriminative feature）
  → 但不修改 Signal 3，不实现

TERTIARY: E. 扩展独立 Corpus
  → 在 future independent cases 上验证 adjudicator rule
  → Level B (different document), ≥10 cases
  → 仅在标准明确后进行
```

---

## 20. Anti-Overdesign Gate

```
DICE_CORE_MODIFICATION              = NO
P1_P7_MODIFICATION                  = NO
P2_MODIFICATION                     = NO
TLD_MODIFICATION                    = NO
IS11_MODIFICATION                   = NO
GT_MODIFICATION                     = NO
EXPERIMENT_MODIFICATION             = NO
SIGNAL_MODIFICATION                 = NO
NEW_MODULE                          = NO
NEW_ENGINE                          = NO
NEW_OBSERVATION                     = NO
NEW_LLM_PIPELINE                    = NO
RUNTIME_CHANGE                      = NO
CAPABILITY_CHANGE                   = NO
FROZEN_BASELINE_DRIFT               = 0/7
IMPLEMENTATION_AUTHORIZED           = FALSE
EXPERIMENT_AUTHORIZED               = FALSE
FORMAL_LEARNING                     = FALSE
STOP                                = TRUE
```

---

## 21. Governance Gate

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
FROZEN_EXPERIMENT                   = INTACT
IMPLEMENTATION_AUTHORIZED           = FALSE
FORMAL_EXPERIMENT                   = NOT_STARTED
STOP                                = TRUE
```

---

## 22. 最终原则验证

> *Reviewer disagreement ≠ Persistent Human Semantic Gap*

✓ 遵守：4 个 disagreement 被分类为 STANDARD_GAP，不是 PERSISTENT_SEMANTIC_AMBIGUITY。Adjudicator 用确定性规则解决。

> *不要把 Human Semantic Gap 轻易判成 E5*

✓ 遵守：检查了所有 E1-E4 可能性。发现 standard 未定义（A）和 evidence 未组织（B）。未发现任何案例满足 E5 的 6 项条件。

> *Human 所谓的"语义判断"，是否其实只是 Machine 没有把局部上下文组织好？*

✓ 回答：**YES — 主要是 standard 未定义 + evidence 未组织**。Adjudicator 用 period+cap（E3, derivable）解决了全部分歧。不需要 "更高层语义理解"。

`STOP = TRUE`。
