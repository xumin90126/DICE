# Text Unit Standard Definition Impact Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY / NO MODIFICATION / COUNTERFACTUAL ANALYSIS ONLY / FROZEN INTACT / STOP

---

## 1. Executive Summary

```
STANDARD_GAP_SUPPORTED = YES (for prose sentence boundary cases, 4/4 disagreements resolved)

STANDARD-B (Sentence Boundary):
  Triggers: 4/45 (9%) — only prose sentence boundary cases
  Disagreements resolved: 4/4 (100%)
  CLEAR cases changed: 0/45 (0%)
  MERGE false positives: 0/2 (0%)
  NO_PREDICTION: 41/45 (91%) — table/figure/mixed cases not covered

KEY FINDING:
  Sentence Boundary ≠ Content Unit Boundary ≠ Evidence Boundary
  IS-11 mixes multiple boundary types in one 45-case pool:
    - Table values (21, 47%) — column boundary, no disagreement
    - Table headers (7, 16%) — column boundary, no disagreement
    - Prose sentences (4, 9%) — sentence boundary, ALL disagreements
    - Figure captions (2, 4%) — caption boundary, no disagreement
    - Mixed (11, 24%) — various, 1 disagreement (prose-like)

  STANDARD-B resolves ALL disagreements but covers only 9% of cases
  → It is a PARTIAL standard, not a universal boundary standard
  → Table and figure cases have NO standard gap (reviewers already agree)

FINAL_STATUS = STANDARD_GAP_PARTIALLY_SUPPORTED
  → Standard gap exists but only for prose sentence cases
  → Other boundary types are already clear (no disagreement)

PERSISTENT_SEMANTIC_AMBIGUITY = NOT_FOUND
LLM_NEEDED = NO
DOCUMENT_DISCOURSE_NEEDED = NO
STOP = TRUE
```

> **STANDARD-B（Sentence Boundary Standard）解决了全部 4 个 reviewer 分歧——它们都是 prose sentence boundary 案例（period + capital → KEEP_SEPARATE）。但 STANDARD-B 只覆盖 4/45 (9%) 的案例，不触及 table values (47%)、table headers (16%)、figure captions (4%) 和 mixed (24%) 案例。IS-11 的 45-case pool 混合了多种不同的 boundary 类型——Sentence Boundary、Table Column Boundary、Figure Caption Boundary——每种需要不同的 "content unit" 定义。Standard gap 仅存在于 prose sentence 案例；table 和 figure 案例无标准歧义（reviewer 已一致）。STANDARD-B 不是 universal boundary standard。**

---

## 2. Research Question

> 如果从一开始就明确 "Text Unit = Sentence"，当前 45 个 Case 中哪些 disagreement 会消失？STANDARD-B 是否会误伤其他案例？

---

## 3. Two Standards Compared

### STANDARD-A (Current)

```
MERGE = 两个片段属于同一文本单元
KEEP_SEPARATE = 两个片段不属于同一文本单元
Problem: "文本单元" (text unit) is UNDEFINED
```

### STANDARD-B (Counterfactual — Sentence Boundary)

```
Text Unit = Sentence
IF text_a ends with sentence-ending punctuation (.) AND text_b starts with uppercase
THEN: different sentence units → KEEP_SEPARATE
NOTE: This is a RESEARCH counterfactual only. Not written to GT. Not implemented.
```

---

## 4. Full 45-Case Counterfactual Analysis

### 4.1 Results Summary

| Metric | STANDARD-A (Current) | STANDARD-B (Sentence) |
|---|---|---|
| Total cases | 45 | 45 |
| Rule triggers | N/A (Human judgment) | 4 (9%) |
| Disagreements | 4 | **0 (all resolved)** |
| CLEAR cases changed | N/A | **0** |
| MERGE false positives | N/A | **0** |
| NO_PREDICTION | N/A | 41 (91%) |
| GT distribution | KEEP=43, MERGE=2 | KEEP=4 (triggered), NO_PRED=41 |

### 4.2 Q1: Do All 4 Disagreements Become KEEP_SEPARATE?

**YES — all 4 resolved:**

| Case | period_end | cap_start | SB | CF_GT | Final GT | Resolved? |
|---|---|---|---|---|---|---|
| AMB-005 | Y | Y | Y | KEEP_SEPARATE | KEEP_SEPARATE | **YES** |
| AMB-375 | Y | Y | Y | KEEP_SEPARATE | KEEP_SEPARATE | **YES** |
| AMB-418 | Y | Y | Y | KEEP_SEPARATE | KEEP_SEPARATE | **YES** |
| AMB-519 | Y | Y | Y | KEEP_SEPARATE | KEEP_SEPARATE | **YES** |

### 4.3 Q2: Does STANDARD-B Change Any CLEAR Cases?

**NO — 0/45 changed.**

STANDARD-B only triggers on 4 cases (all disagreements). The other 41 cases get NO_PREDICTION — STANDARD-B doesn't touch them.

### 4.4 Q3: Does STANDARD-B Affect MERGE Cases?

**NO — 0/2 false positives.**

| Case | GT | text_a | period_end | SB | CF_GT | False Positive? |
|---|---|---|---|---|---|---|
| AMB-414 | MERGE | 'FIG. 9:' | **False** (ends with ':') | False | NO_PREDICTION | **NO** |
| AMB-422 | MERGE | 'FIG. 12:' | **False** (ends with ':') | False | NO_PREDICTION | **NO** |

> **Figure labels end with ':', not '.' — STANDARD-B's period check correctly excludes them.**

---

## 5. Figure Caption Analysis

### 5.1 AMB-414 and AMB-422 Under STANDARD-B

| Feature | AMB-414 | AMB-422 |
|---|---|---|
| text_a | 'FIG. 9:' | 'FIG. 12:' |
| text_a ends with | ':' (colon) | ':' (colon) |
| period_end | **False** | **False** |
| cap_start | True ('Left:') | True ('Distribution...') |
| sentence_boundary | **False** | **False** |
| STANDARD-B triggers | **NO** | **NO** |
| GT | MERGE | MERGE |
| False positive | **NO** | **NO** |

### 5.2 Why STANDARD-B Doesn't Conflict

> **Figure labels use ':' as separator (e.g., 'FIG. 9:'), not '.' as sentence-ending punctuation. STANDARD-B's `endswith('.')` check correctly excludes figure labels. Sentence Boundary Standard does NOT误伤 Figure Caption cases.**

### 5.3 But: Sentence Boundary ≠ Caption Boundary

STANDARD-B doesn't trigger on figure captions, but it also doesn't **resolve** them. Figure caption boundary requires a different definition:
- `has_fig_prefix → MERGE` (label + caption body = same content unit)

> **Sentence Boundary Standard ≠ Universal Boundary Standard. STANDARD-B handles prose sentences; figure captions need a separate boundary definition.**

---

## 6. Three Boundary Types — Conceptual Distinction

### 6.1 Definitions

| Boundary Type | Definition | Key Evidence | Coverage |
|---|---|---|---|
| **Sentence Boundary** | Two spans belong to different sentences | period_end + cap_start | 4/45 (9%) |
| **Table Column Boundary** | Two spans are in different table columns | TLD is_in_table + different_cell | 28/45 (62%) |
| **Figure Caption Boundary** | Label + caption body = same caption | has_fig_prefix | 2/45 (4%) |

### 6.2 Hierarchy?

```
Sentence Boundary → Content Unit Boundary → Evidence Boundary
```

- **Sentence Boundary**: Are these different sentences? (prose-specific)
- **Content Unit Boundary**: Are these different content units? (type-specific: sentence, table cell, caption)
- **Evidence Boundary**: Should these be separate evidence units? (application-specific)

> **三者不等同。Sentence Boundary 是 Content Unit Boundary 的一个子类型。Table Column 和 Figure Caption 是其他子类型。IS-11 混合了所有三种。**

### 6.3 Disagreement Distribution

| Boundary Type | Cases | Disagreements | Standard Gap? |
|---|---|---|---|
| Sentence Boundary (prose) | 4 | **4 (100%)** | **YES** |
| Table Column Boundary | 28 | 0 (0%) | NO (reviewers agree) |
| Figure Caption Boundary | 2 | 0 (0%) | NO (reviewers agree) |
| Mixed | 11 | 0 (0%, AMB-375 is prose-like) | NO |

> **ALL disagreements are in Sentence Boundary cases. Table and Figure cases have NO standard gap.**

---

## 7. IS-11 Research Object Analysis

### 7.1 What Is IS-11 Actually Testing?

IS-11 candidate universe criteria (geometric): `gap 8-50, same_style, line_obs ≤ 15, w_b ≥ 15`

These criteria select **geometrically ambiguous same-y pairs** — but the resulting pool mixes:

| Type | Count | What's Being Tested | Boundary Type |
|---|---|---|---|
| Table values | 21 (47%) | Different table columns? | Column Boundary |
| Table headers | 7 (16%) | Different table columns? | Column Boundary |
| Prose sentences | 4 (9%) | Different sentences? | Sentence Boundary |
| Figure captions | 2 (4%) | Label + caption? | Caption Boundary |
| Mixed | 11 (24%) | Various | Various |

### 7.2 The Core Problem

> **IS-11 mixes multiple boundary types in one pool but uses a single undefined "text unit" standard. This creates standard ambiguity ONLY for prose sentence cases — the other types have implicit but clear standards (reviewers agree).**

### 7.3 Option Analysis

| Option | Description | Matches IS-11? |
|---|---|---|
| 1. Sentence Segmentation | Only sentence boundaries | NO (only 4/45 are prose) |
| 2. Content Unit Segmentation | Various content units | **YES (mixed types)** |
| 3. Evidence Boundary Construction | Evidence-level boundaries | PARTIAL |
| 4. Structural Object Segmentation | Table/Figure/Prose objects | **YES (mixed structural types)** |

> **IS-11 is testing Option 2/4: Content Unit / Structural Object Segmentation with mixed types. The single "text unit" standard is insufficient because different types need different definitions.**

---

## 8. GT Balance Comparison

| Metric | Current (STANDARD-A) | Counterfactual (STANDARD-B) |
|---|---|---|
| KEEP_SEPARATE | 43 | 4 (triggered) + 39 (NO_PRED, current KEEP) |
| MERGE | 2 | 0 (triggered) + 2 (NO_PRED, current MERGE) |
| Disagreements | 4 | **0** |
| Total | 45 | 45 |

> **GT balance does NOT change — STANDARD-B doesn't modify any GT label. It only resolves the 4 disagreements (which were already adjudicated to KEEP_SEPARATE). STANDARD-B confirms the adjudicator's decisions.**

---

## 9. Human Disagreement Re-examination

### For Each Disagreement Case:

| Case | If Standard = Sentence? | If Standard = Content Unit? | If Standard = Evidence Unit? |
|---|---|---|---|
| AMB-005 | No judgment needed (period+cap → KEEP) | Still needs judgment (sentence vs paragraph) | Still needs judgment |
| AMB-375 | No judgment needed (period+cap → KEEP) | Still needs judgment | Still needs judgment |
| AMB-418 | No judgment needed (period+cap → KEEP) | Still needs judgment | Still needs judgment |
| AMB-519 | No judgment needed (period+cap → KEEP) | Still needs judgment | Still needs judgment |

> **If Standard = Sentence (STANDARD-B): Human judgment NOT needed for these 4 cases — deterministic rule suffices.**
> **If Standard = Content Unit (undefined): Human judgment still needed — disagreement persists.**
> **The key is: DICE needs to decide which boundary type it's measuring.**

---

## 10. AMB-032 — Preserved as EVIDENCE_ORGANIZATION_GAP

```
AMB-032:
  Type: Table value ('-' / '8.43')
  Reviewers: AGREED (both KEEP_SEPARATE)
  GT: KEEP_SEPARATE (no disagreement)
  P722 B2: UNKNOWN (45.9s)
  TLD: is_in_table=True (correct)
  period+cap: False (no sentence boundary)
  STANDARD-B: NO_PREDICTION (doesn't trigger)
  
  Root cause: EVIDENCE_ORGANIZATION_GAP
  - TLD detected table correctly
  - But P722 participant couldn't verify table structure from geometry fields
  - Table structure not organized for participant
  - NOT Standard Gap (reviewers agreed)
  - NOT Semantic Ambiguity (deterministic resolution exists)
```

> **AMB-032 remains EVIDENCE_ORGANIZATION_GAP. STANDARD-B does not address it (no sentence boundary). This case needs table structure evidence organization, not standard clarification.**

---

## 11. Signal 3 Status

```
SIGNAL_3_STATUS = RETAIN_AS_L3_CANDIDATE
```

Signal 3 (line_obs ≥ 3 AND NOT fig → KEEP_SEPARATE):
- 38/38 CLEAR cases correct
- BOUNDARY_OVERCOMMIT on 4 disagreement cases
- Not upgraded, not closed

Adjudicator rule (period+cap → KEEP_SEPARATE):
- RETROSPECTIVE_DISCRIMINATIVE_FEATURE
- Not upgraded to L4/L5/RULE/PRODUCTION
- Requires future independent data validation

---

## 12. Final Research Questions

### Q1: Text Unit 是否必须定义？

**YES — 至少对 prose sentence boundary 案例必须定义。** 当前 "文本单元" 未定义导致 4 个分歧。定义后分歧消失。

### Q2: 如果定义，最小合理定义是什么？

**对 prose: Text Unit = Sentence (delimited by period + capital).** 这是 adjudicator 已使用的规则。

但这不是 universal definition——table 和 figure 需要不同的 content unit 定义。

### Q3: Sentence Standard 是否足以支持当前研究目标？

**NO — 不足以支持全部目标。** STANDARD-B 只覆盖 4/45 (9%)。IS-11 混合了多种 boundary 类型。Sentence Standard 只解决 prose 部分。

### Q4: Sentence Standard 是否会误伤 Figure Caption / Content Unit cases？

**NO — 不会误伤。** Figure labels end with ':' not '.' → STANDARD-B correctly excludes them. 0/2 false positives on MERGE cases.

### Q5: 当前 Boundary Research 的真正 Evaluation Object 是什么？

**Mixed: Content Unit / Structural Object Segmentation.** IS-11 pool 包含 table columns (62%)、prose sentences (9%)、figure captions (4%)、mixed (24%)。不是单一的 Sentence Segmentation。

### Q6: 当前 Human disagreement 中有多少确实由 Standard Gap 解释？

**4/4 (100%).** 全部 4 个分歧都是 prose sentence boundary 案例，由 STANDARD_GAP 解释。

### Q7: 还有多少无法由 Standard Gap 解释？

**0 个 disagreement.** 所有分歧都由 Standard Gap 解释。

但 AMB-032 (UNKNOWN) 不由 Standard Gap 解释——它是 EVIDENCE_ORGANIZATION_GAP（1 个 case，不是 disagreement）。

### Q8: AMB-032 的 Evidence Organization Gap 是否仍成立？

**YES — 仍成立。** AMB-032 不是 disagreement（reviewer 一致）。它的 UNKNOWN 来自 P722 参与者无法从几何字段验证 table structure。TLD 正确但 evidence 未组织。Standard Gap 不适用于此 case。

### Q9: 是否仍有任何证据支持 Persistent Semantic Ambiguity？

**NO — NOT_FOUND.** 所有 4 个分歧在标准明确后消失。Adjudicator 用确定性规则解决。无案例满足 "evidence + standard + organization 全部充分但 Human 仍分歧" 的条件。

### Q10: 是否需要 LLM？

**NO.** 所有 resolution 通过确定性字符串检查（period, capital）完成。

### Q11: 是否需要 Document Discourse Structure？

**NO.** 无案例需要 discourse 理解。局部文本特征足够。

---

## 13. Final Status

```
FINAL_STATUS = STANDARD_GAP_PARTIALLY_SUPPORTED
```

**PARTIALLY_SUPPORTED** 因为：
- Standard Gap 解释了 ALL 4 disagreements (100%)
- STANDARD-B resolves all disagreements with 0 false positives
- BUT STANDARD-B is partial (9% coverage)
- IS-11 mixes multiple boundary types
- Table and figure cases have no standard gap (but need different definitions)
- AMB-032 is EVIDENCE_ORGANIZATION_GAP (not standard gap)

---

## 14. Key Conceptual Finding

```
Sentence Boundary ≠ Content Unit Boundary ≠ Evidence Boundary

IS-11 mixes:
  - Sentence Boundary (prose, 4 cases, ALL disagreements)
  - Table Column Boundary (28 cases, 0 disagreements)
  - Figure Caption Boundary (2 cases, 0 disagreements)

Standard Gap exists ONLY for Sentence Boundary cases.
Table and Figure cases have implicit but clear standards.
```

> **当前 Human disagreement 的一部分来自 Evaluation Standard 不明确（prose sentence cases），而不是 Human 无法完成语义判断。但这并不意味着所有 Boundary Resolution 都可以 deterministic——table 和 figure 案例需要不同的 boundary 定义，且 TLD 有 coverage gap。**

---

## 15. Anti-Overdesign Gate

```
DICE_CORE_MODIFICATION              = NO
P1_P7_MODIFICATION                  = NO
P2_MODIFICATION                     = NO
TLD_MODIFICATION                    = NO
IS11_MODIFICATION                   = NO
GT_MODIFICATION                     = NO
SIGNAL_MODIFICATION                 = NO
LLM                                 = NO
NEW_MODULE                          = NO
NEW_ENGINE                          = NO
NEW_OBSERVATION                     = NO
NEW_ARCHITECTURE_NEEDED             = NO
RUNTIME_CHANGE                      = NO
FROZEN_BASELINE_DRIFT               = 0/7
IMPLEMENTATION_AUTHORIZED           = FALSE
EXPERIMENT_AUTHORIZED               = FALSE
STOP                                = TRUE
```

---

## 16. Governance Gate

```
DICE_CORE_MODIFICATION              = NO
P1_P7_MODIFICATION                  = NO
P2_MODIFICATION                     = NO
TLD_MODIFICATION                    = NO
IS11_MODIFICATION                   = NO
GT_MODIFICATION                     = NO
SIGNAL_MODIFICATION                 = NO
LLM                                 = NO
NEW_MODULE                          = NO
NEW_ENGINE                          = NO
RUNTIME_CHANGE                      = NO
CAPABILITY_CHANGE                   = NO
FROZEN_BASELINE                     = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d)
FROZEN_EXPERIMENT                   = INTACT
IMPLEMENTATION_AUTHORIZED           = FALSE
EXPERIMENT_AUTHORIZED               = FALSE
FORMAL_EXPERIMENT                   = NOT_STARTED
STOP                                = TRUE
```

---

## 17. 最终原则验证

> *不能只报告 4 个 disagreement。必须重新分析全部 45 cases。*

✓ 遵守：对全部 45 cases 进行了 counterfactual analysis。

> *Sentence Boundary Standard ≠ Universal Boundary Standard*

✓ 明确写出：STANDARD-B 只覆盖 9%，不是 universal standard。三种 boundary type 被区分。

> *不要为了获得更漂亮的分布而修改 GT。*

✓ 遵守：0 GT labels changed。Counterfactual 仅用于分析。

> *AMB-032 必须继续作为 EVIDENCE_ORGANIZATION_GAP*

✓ 遵守：AMB-032 单独保留为 EVIDENCE_ORGANIZATION_GAP，未归入 Standard Gap。

> *不得过度外推：所有 Boundary Resolution 都可以 deterministic*

✓ 遵守：明确指出 table 和 figure 案例需要不同定义，TLD 有 coverage gap，不所有 resolution 都 deterministic。

`STOP = TRUE`。
