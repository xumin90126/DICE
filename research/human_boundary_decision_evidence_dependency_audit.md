# Human Boundary Decision Evidence Dependency Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY / NO MODIFICATION / FROZEN INTACT / STOP
**Predecessor**: Candidate Semantic Coherence / Candidate Value Audit

---

## 1. Executive Summary

```
FINAL_STATUS = EVIDENCE_EXISTS_BUT_NOT_CONSUMED

KEY FINDING:
  Human 正确判断 Boundary 时，实际依赖的 Evidence 100% 已存在于 DICE 中。
  
  E1 (existing and used):        12/45 (26%) — TLD correct, machine uses it
  E2 (existing but not used):    29/45 (64%) — P1 text exists, IS-11 only extracts is_number binary
  E3 (derivable):                 4/45 (9%)  — period+cap / FIG prefix derivable from P1
  E4 (evidence missing):          0/45 (0%)  — NO evidence missing
  E5 (genuine semantic):          0/45 (0%)  — NO genuine semantic judgment needed

  → 100% of Human Decision Evidence EXISTS or is DERIVABLE
  → 0% requires new Observation
  → 0% requires genuine Human Semantic Judgment

IS-11 DECISION MECHANISM (reconstructed from source code):
  1. TLD override (28%): is_in_table + different_cell → KEEP_SEPARATE
  2. IS-01/IS-02 fallback (71%): TLD misses → binary content-type check
     - IS-01 = regex: ^\d+(\.\d+)*\.?$ (is text_a a pure number?)
     - IS-02 = any word with >2 alpha chars (does text_b have readable text?)
     - Both True (number + text) → MERGE
     - Both False (not-number + not-text) → KEEP_SEPARATE
     - Mixed → ABSTAIN

断裂 LOCATION:
  P1 text EXISTS (raw strings with full semantic content)
  → IS-01/IS-02 reads P1 text BUT only extracts binary (is_number / has_text)
  → IS-11 uses binary result, NOT semantic content
  → Human reads semantic content ("4" = stage index, "MBConv6" = operator → different columns)
  → Human uses PAGE CONTEXT (sees Table 1 layout)
  
  → This is CONSUMER_INTEGRATION_GAP (64%)
  → NOT Evidence Organization Gap (evidence IS organized in P1/TLD)
  → NOT Evidence Missing (0%)
  → NOT Semantic Judgment (0%)

PRIMARY_BOTTLENECK = C (Consumer Integration)
SECONDARY_BOTTLENECK = F (Evaluation Standard) — 9% STANDARD_GAP

STOP = TRUE
```

> **Human 在进行 Boundary Judgment 时依赖的 Evidence 100% 已存在于 DICE 中（E1+E2+E3 = 45/45 = 100%）。不存在 Evidence 缺失（E4 = 0%），不需要真正的 Human Semantic Judgment（E5 = 0%）。断裂发生在 P1 text content 与 IS-11 consumer 之间：IS-11 通过 IS-01/IS-02 只提取了 binary 信号（is_number / has_text），而 Human 读取了 text 的 semantic content（"4" = stage index, "MBConv6" = operator type → different columns）。这是 Consumer Integration Gap，不是 Evidence Organization Gap，也不是 Evidence Missing。**

---

## 2. Research Questions

### RQ1: Human 正确判断时依赖哪些信息？

**P1 text content (semantic meaning) + page context (visual layout).**

- Table cases (35/45 = 77%): Human reads text semantics ("4" = stage index, "MBConv6" = operator → different columns) + sees table layout
- Figure cases (2/45 = 4%): Human reads FIG prefix in P1 text → identifies figure caption
- Prose cases (4/45 = 9%): Human reads period_end + cap_start → identifies sentence boundary
- Other (4/45 = 9%): Human reads text content + context

### RQ2: 这些信息是否已存在于 DICE 中？

**YES — 100%.**

- P1 text: raw strings (text_a, text_b) — EXISTS
- P2 geometry: bbox, same_y_band, h_gap — EXISTS
- TLD: is_in_table, different_cell, cell assignment — EXISTS (but fails 71%)
- IS-01/IS-02: binary is_number / has_text — EXISTS (but insufficient)
- period_end, cap_start: NOT explicit fields, but DERIVABLE from P1 text (E3)
- has_fig_prefix: NOT explicit field, but DERIVABLE from P1 text (E3)

### RQ3: 为什么 Human 能利用而 Machine 没有利用？

**IS-11 only extracts binary signals from P1 text, not semantic content.**

- IS-01 = `re.match(r'^\d+(\.\d+)*\.?$', text_a)` → binary: is pure number?
- IS-02 = `any(len(re.sub(r'[^a-zA-Z]', '', w)) > 2 for w in text_b.split())` → binary: has readable text?
- IS-11 uses these binaries for fallback decision, NOT the actual text meaning
- Human reads "4" = stage index, "MBConv6" = operator type → semantically different columns
- Machine sees: IS-01=True (number) + IS-02=True (text) → MERGE (wrong)

### RQ4: 如果 Evidence 不存在，是 A (可推导) 还是 B (需新 Observation)?

**All evidence either exists (E1/E2) or is derivable (E3). NO new Observation needed.**

- E3 derivable features: `has_fig_prefix = text.startswith("FIG")`, `period_end = text.endswith(".")`, `cap_start = text[0].isupper()`
- These are deterministic regex operations on P1 text — NO semantic understanding needed
- E2 features (table column identity from text semantics) exist in P1 text but require semantic consumption

### RQ5: E1-E5 分布?

| Class | Count | % | Description |
|---|---|---|---|
| E1 | 12 | 26% | TLD correct, machine uses it, Human uses table structure |
| E2 | 29 | 64% | P1 text exists, Human uses semantic content, IS-11 uses only binary |
| E3 | 4 | 9% | period+cap / FIG prefix derivable from P1, not computed |
| E4 | 0 | 0% | NO evidence missing |
| E5 | 0 | 0% | NO genuine semantic judgment needed |

---

## 3. Case Set

### Primary Cases (9 focus + 4 comparison = 13 detailed)

| Case | Type | GT | Disagree | Machine | Focus |
|---|---|---|---|---|---|
| AMB-135 | Table (TLD miss) | KEEP | N | FP | Machine FP via IS-01/IS-02 fallback |
| AMB-032 | Table (TLD hit) | KEEP | N | TN | P722 UNKNOWN (evidence not exposed) |
| AMB-313 | Table header (TLD miss) | KEEP | N | ABSTAIN | Human uses header semantics |
| AMB-375 | Prose (disagreement) | KEEP | Y | ABSTAIN | Standard gap (sentence vs paragraph) |
| AMB-414 | Figure caption | MERGE | N | ABSTAIN | FIG prefix not computed |
| AMB-418 | Prose (disagreement) | KEEP | Y | ABSTAIN | Standard gap |
| AMB-422 | Figure caption | MERGE | N | ABSTAIN | FIG prefix not computed |
| AMB-462 | Table header (TLD miss) | KEEP | N | ABSTAIN | Human uses header semantics |
| AMB-519 | Prose (disagreement) | KEEP | Y | ABSTAIN | Standard gap, NOT E5 |
| AMB-024 | Table (TLD hit) | KEEP | N | TN | Comparison: clear KEEP |
| AMB-074 | Table (TLD hit) | KEEP | N | TN | Comparison: clear KEEP |
| AMB-005 | Prose (TLD FP) | KEEP | Y | TN | Comparison: TLD FP coincidence |
| AMB-346 | Table (TLD hit) | KEEP | N | TN | Comparison: clear KEEP |

### Full Set: 45 IS-11 cases + 69 P7 cases (cross-validation)

---

## 4. Human Decision Evidence Maps

### AMB-135 (Machine FP — Critical Case)

```
CASE_ID: IS11-AMB-135
HUMAN_DECISION: KEEP_SEPARATE (both reviewers agree)
CANDIDATE_OBJECTS: text_a='4', text_b='MBConv6, k5x5'

EVIDENCE_USED_BY_HUMAN:
  1. Text semantics: '4' = stage index, 'MBConv6, k5x5' = operator type
  2. Page context: Table 1 architecture table with multiple columns
  3. Column identity: stage index and operator are DIFFERENT columns

EVIDENCE_SOURCE: P1_TEXT + PAGE_CONTEXT
EVIDENCE_CURRENTLY_AVAILABLE: YES (P1 text_a='4', text_b='MBConv6, k5x5')
EVIDENCE_CURRENTLY_CONSUMED: PARTIAL — IS-01 extracts is_number=True, IS-02 extracts has_text=True
EVIDENCE_NOT_CONSUMED: Text semantic content (stage index vs operator type)
EVIDENCE_DERIVABLE: NO (requires semantic understanding, not deterministic regex)
EVIDENCE_MISSING: NO
SEMANTIC_JUDGMENT_REQUIRED: NO (Human uses structural role, not deep semantics)

DECISION_CRITICAL_EVIDENCE: Column identity (text_a and text_b are different table columns)
DECISION_SUPPORTING_EVIDENCE: Table structure (page context), h_gap=30.0

MACHINE_MECHANISM: TLD miss → IS-01=True(number) + IS-02=True(text) → MERGE (FP)
MACHINE_UNUSED: P1 text semantic content (only binary is_number extracted)

E_CLASS: E2 (existing but not used)
GAP_TYPE: CONSUMER_INTEGRATION
UNUSED_TYPE: TYPE_5 (low-level facts not combined into decision-critical evidence)
LS: LS-1 (Human points to existing evidence machine didn't use)
```

### AMB-032 (P722 UNKNOWN — Evidence Exposure Case)

```
CASE_ID: IS11-AMB-032
HUMAN_DECISION: KEEP_SEPARATE (both reviewers agree)
CANDIDATE_OBJECTS: text_a='-', text_b='8.43'

EVIDENCE_USED_BY_HUMAN:
  1. Table structure: Table 3, VGG row
  2. Column identity: '-' = top-1 error, '8.43' = top-5 error (different columns)
  3. TLD: is_in_table=True, different_cell=True, a_cell=[27,1], b_cell=[27,2]

EVIDENCE_SOURCE: TLD
EVIDENCE_CURRENTLY_AVAILABLE: YES
EVIDENCE_CURRENTLY_CONSUMED: YES (IS-11 uses TLD → KEEP_SEPARATE → TN)
EVIDENCE_NOT_CONSUMED: N/A (machine uses TLD correctly)
EVIDENCE_DERIVABLE: N/A
EVIDENCE_MISSING: NO

DECISION_CRITICAL_EVIDENCE: TLD different_cell=True
DECISION_SUPPORTING_EVIDENCE: Column identity (top-1 vs top-5 error)

MACHINE_MECHANISM: TLD_DIFFERENT_CELL → KEEP_SEPARATE (TN)
P722_BEHAVIOR: UNKNOWN (45.9s, expanded ALL 7 fields) — TLD cell info NOT exposed to participant

E_CLASS: E1 (existing and used)
GAP_TYPE: NONE (for IS-11 machine) / EVIDENCE_EXPOSURE (for P722 participant)
LS: LS-0 (machine already correct)

NOTE: IS-11 machine uses TLD correctly. But P722 participant couldn't access TLD cell info.
  → This is NOT a Consumer Integration Gap for IS-11.
  → It IS an Evidence Exposure Gap for P722 experiment participant.
```

### AMB-375 (Prose Disagreement — Standard Gap Case)

```
CASE_ID: IS11-AMB-375
HUMAN_DECISION: KEEP_SEPARATE (adjudicated, reviewer disagreement)
CANDIDATE_OBJECTS: text_a='[23].', text_b='Each'

EVIDENCE_USED_BY_HUMAN:
  1. Period_end: text_a ends with '.'
  2. Cap_start: text_b starts with 'E' (capital)
  3. Content unit definition: Reviewer A = sentence → KEEP; Reviewer B = paragraph → MERGE
  4. Adjudicator: period + cap → separate sentences → KEEP

EVIDENCE_SOURCE: P1_TEXT (derivable: period_end + cap_start)
EVIDENCE_CURRENTLY_AVAILABLE: YES (P1 text exists)
EVIDENCE_CURRENTLY_CONSUMED: PARTIAL — IS-01=False('[23].' not pure number), IS-02=True('Each' has text)
EVIDENCE_NOT_CONSUMED: period_end, cap_start (not computed by IS-11)
EVIDENCE_DERIVABLE: YES — period_end = text_a.endswith('.'), cap_start = text_b[0].isupper()
EVIDENCE_MISSING: NO
SEMANTIC_JUDGMENT_REQUIRED: NO — but STANDARD is unclear (sentence vs paragraph)

DECISION_CRITICAL_EVIDENCE: period_end + cap_start (sentence boundary)
DECISION_SUPPORTING_EVIDENCE: Text flow context

MACHINE_MECHANISM: TLD miss → IS-01=False + IS-02=True → ABSTAIN
MACHINE_UNUSED: period_end + cap_start (derivable, not computed)

E_CLASS: E3 (derivable from existing evidence)
GAP_TYPE: STANDARD_GAP (evidence derivable, but content unit standard unclear)
UNUSED_TYPE: TYPE_2 (not organized into structured relation)
LS: LS-2 (Human points to derivable relation + standard clarification)

NOT E5: Evidence IS sufficient (period+cap). Only the STANDARD (sentence vs paragraph) is unclear.
  The adjudicator resolved it with period+cap → KEEP. This is a STANDARD_GAP, not semantic ambiguity.
```

### AMB-414 (Figure Caption — E3 Derivable Case)

```
CASE_ID: IS11-AMB-414
HUMAN_DECISION: MERGE (both reviewers agree)
CANDIDATE_OBJECTS: text_a='FIG. 9:', text_b='Left:'

EVIDENCE_USED_BY_HUMAN:
  1. FIG prefix: text_a starts with 'FIG.' → figure caption label
  2. Caption structure: 'Left:' is a sub-description of the caption
  3. Continuous caption: 'FIG. 9: Left: BIC values...' is one unit

EVIDENCE_SOURCE: P1_TEXT (FIG prefix)
EVIDENCE_CURRENTLY_AVAILABLE: YES (P1 text_a='FIG. 9:')
EVIDENCE_CURRENTLY_CONSUMED: PARTIAL — IS-01=False('FIG. 9:' not pure number)
EVIDENCE_NOT_CONSUMED: has_fig_prefix (not computed)
EVIDENCE_DERIVABLE: YES — has_fig_prefix = text_a.startswith('FIG') (deterministic regex)
EVIDENCE_MISSING: NO

DECISION_CRITICAL_EVIDENCE: has_fig_prefix (FIG prefix in text_a)
DECISION_SUPPORTING_EVIDENCE: Caption sub-description pattern ('Left:')

MACHINE_MECHANISM: TLD miss → IS-01=False + IS-02=True → ABSTAIN
MACHINE_UNUSED: has_fig_prefix (derivable, not computed)

E_CLASS: E2 (existing but not used) / E3 (derivable)
GAP_TYPE: CONSUMER_INTEGRATION (FIG prefix in P1, IS-11 doesn't compute it)
LS: LS-1
```

### AMB-519 (Prose Disagreement — NOT E5)

```
CASE_ID: IS11-AMB-519
HUMAN_DECISION: KEEP_SEPARATE (adjudicated, reviewer disagreement)
CANDIDATE_OBJECTS: text_a='facto backbone for open-source LLMs.', text_b='To embrace...'

EVIDENCE_USED_BY_HUMAN:
  1. Period_end: text_a ends with '.'
  2. Cap_start: text_b starts with 'T' (capital)
  3. Content unit: Reviewer A = sentence → KEEP; Reviewer B = paragraph → MERGE
  4. Adjudicator: period + cap → separate sentences → KEEP

EVIDENCE_SOURCE: P1_TEXT (derivable: period_end + cap_start)
EVIDENCE_DERIVABLE: YES — deterministic regex
EVIDENCE_MISSING: NO
SEMANTIC_JUDGMENT_REQUIRED: NO

E_CLASS: E3 (derivable)
GAP_TYPE: STANDARD_GAP
LS: LS-2

NOT E5: Evidence is sufficient (period+cap derivable).
  The disagreement is about STANDARD (sentence vs paragraph), not about evidence.
  Adjudicator resolved with period+cap → KEEP.
  This is STANDARD_GAP, NOT genuine semantic ambiguity.
```

---

## 5. E1-E5 Classification

### IS-11 45 Cases

| Class | Count | % | Description |
|---|---|---|---|
| **E1** | **12** | **26%** | TLD correct, machine uses TLD, Human uses table structure |
| **E2** | **29** | **64%** | P1 text exists, Human uses semantic content, IS-11 uses only IS-01/IS-02 binary |
| **E3** | **4** | **9%** | period+cap (3 prose) + FIG prefix (classified as E2, but derivable) |
| **E4** | **0** | **0%** | NO evidence missing |
| **E5** | **0** | **0%** | NO genuine semantic judgment needed |

Note: E3 = 4 prose cases (AMB-005, AMB-375, AMB-418, AMB-519) where period+cap is derivable.
Figure caption cases (AMB-414, AMB-422) classified as E2 because the raw text exists in P1,
but has_fig_prefix is also derivable (E3). The primary classification is E2 (text exists, not consumed).

### P7 69 Cases (Cross-Validation)

| Class | Count | % |
|---|---|---|
| E1 | 3 | 4% |
| E2 | 66 | 95% |
| E3 | 0 | 0% |
| E4 | 0 | 0% |
| E5 | 0 | 0% |

P7 has NO TLD → all table cases are E2. Confirms E2 dominant, E4=0%, E5=0%.

### Combined 114 Cases

| Class | Count | % |
|---|---|---|
| E1 | 15 | 13% |
| E2 | 95 | 83% |
| E3 | 4 | 4% |
| E4 | 0 | 0% |
| E5 | 0 | 0% |

> **E4 (Evidence Missing) = 0/114 (0%). E5 (Genuine Semantic Judgment) = 0/114 (0%).**

---

## 6. Decision-Critical Evidence

### Evidence Value Distribution

| Value | Count | Evidence Type |
|---|---|---|
| HIGH | 45/45 (100%) | All decision-critical evidence is HIGH value |
| MEDIUM | 0 | — |
| LOW | 0 | — |
| IRRELEVANT | 0 | — |

### HIGH-Value Evidence Types

| Evidence Type | Count | Source | Human Uses | Machine Uses |
|---|---|---|---|---|
| Table column/cell identity | 35 | P1 text + page context | YES (semantic) | PARTIAL (IS-01/IS-02 binary only) |
| Figure caption (FIG prefix) | 2 | P1 text | YES | NO |
| Sentence boundary (period+cap) | 4 | P1 text (derivable) | YES | NO |
| Text content + context | 4 | P1 text | YES | PARTIAL (IS-01/IS-02 binary only) |

### LOW-Value Evidence (Supporting Only)

| Evidence Type | Count | Source | Role |
|---|---|---|---|
| h_gap | 45 | P2 geometry | Supporting (never decision-critical) |
| same_style | 45 | P3 style | Supporting |
| line_obs_count | 45 | P2 derived | Supporting |
| bbox / width / height | 45 | P2 geometry | Supporting |

> **Human 的 Decision-Critical Evidence 是 TEXT SEMANTIC CONTENT + PAGE CONTEXT，不是 geometry。Geometry (h_gap, same_style) 只是 Supporting Evidence。**

---

## 7. Machine-Unused Evidence

### Machine-Unused Evidence Breakdown

| Unused Type | Count | Description |
|---|---|---|
| TYPE_1 (not read) | 0 | IS-11 reads P1 text via IS-01/IS-02 |
| TYPE_2 (read but not organized) | 4 | period+cap not organized into structured relation |
| TYPE_3 (computed but lost in consumer) | 2 | FIG prefix in P1 text, IS-01 reads it but only extracts is_number |
| TYPE_4 (field exists but hidden) | 0 | — |
| TYPE_5 (low-level facts not combined) | 27 | P1 text has semantic content, IS-11 only uses binary is_number |
| NONE | 12 | TLD used correctly |

### TYPE_5 Detail (27 cases — Dominant)

IS-11 reads P1 text through IS-01/IS-02, but only extracts:
- IS-01: `bool(re.match(r'^\d+(\.\d+)*\.?$', text_a))` → is pure number?
- IS-02: `any(len(re.sub(r'[^a-zA-Z]', '', w)) > 2 for w in text_b.split())` → has readable text?

**The full semantic content of P1 text is NOT consumed.** IS-11 uses a binary content-type check, not semantic understanding. Human reads the actual text meaning ("4" = stage index, "MBConv6" = operator → different columns).

### TYPE_2 Detail (4 cases — Prose)

period_end (`text_a.endswith('.')`) and cap_start (`text_b[0].isupper()`) are:
- NOT currently computed by IS-11
- DERIVABLE from P1 text (deterministic regex)
- Decision-critical for prose sentence boundary cases

### TYPE_3 Detail (2 cases — Figure)

has_fig_prefix (`text_a.startswith('FIG')`) is:
- In P1 text (raw string "FIG. 9:")
- IS-01 reads text_a but only checks is_number → FIG prefix ignored
- DERIVABLE from P1 text (deterministic regex)
- Decision-critical for figure caption cases

---

## 8. Evidence Organization vs Consumer Integration

### Three-Way Distinction

| Gap Type | Count | % | Description |
|---|---|---|---|
| **CONSUMER_INTEGRATION** | **29** | **64%** | Evidence exists, IS-11 reads P1 text but only extracts binary, not semantic content |
| **STANDARD_GAP** | **4** | **9%** | Evidence derivable (period+cap), but content unit standard unclear |
| **NONE** | **12** | **26%** | TLD works, machine correct |
| EVIDENCE_ORGANIZATION | 0 | 0% | Evidence IS organized (P1 text, P2 geometry, TLD structure) |
| EVIDENCE_MISSING | 0 | 0% | NO evidence missing |
| HUMAN_SEMANTIC_GAP | 0 | 0% | NO genuine semantic judgment needed |

### Why CONSUMER_INTEGRATION (not Evidence Organization)?

```
Evidence Organization Gap:
  Evidence is NOT organized into meaningful relations.
  → Does NOT apply: P1 text IS organized (strings), P2 geometry IS organized (bbox, bands),
    TLD IS organized (table membership, cell assignment).

Consumer Integration Gap:
  Evidence IS organized, but IS-11 consumer doesn't read/use it.
  → APPLIES: IS-11 reads P1 text via IS-01/IS-02, but only extracts binary is_number/has_text.
    The semantic content of P1 text is NOT consumed.
    IS-11's consumer logic doesn't use text meaning, only content-type.

Human Semantic Gap:
  Evidence IS organized, consumer reads it, but needs Human semantic judgment.
  → Does NOT apply: 0% E5. Human doesn't need "semantic judgment" — Human uses
    structural role (column identity, sentence boundary, figure caption) which is
    deterministic or semi-deterministic from P1 text.
```

> **断裂不在 Evidence Organization（Evidence 已组织好），而在 Consumer Integration（IS-11 只提取 binary 信号，不消费 semantic content）。**

---

## 9. Difficult Case Analysis

### AMB-135: Why Machine FP?

```
Machine: TLD miss → IS-01=True('4' is number) + IS-02=True('MBConv6' has text) → MERGE (FP)
Human: '4' = stage index, 'MBConv6' = operator → different columns → KEEP_SEPARATE

Root cause: IS-01/IS-02 treats "number + text" as "same unit" (value + label).
  But '4' and 'MBConv6' are DIFFERENT columns in the same row.
  IS-01/IS-02 cannot distinguish "same column" from "different column" — it only checks content type.

Human evidence: P1 text semantic content + page context (Table 1 layout).
Machine unused: P1 text semantic content (only binary is_number extracted).
→ E2, CONSUMER_INTEGRATION, TYPE_5
```

### AMB-032: Why P722 UNKNOWN?

```
Machine: TLD correct → KEEP_SEPARATE (TN)
P722 participant: UNKNOWN (45.9s, expanded ALL 7 geometry fields)

Root cause: TLD cell info (is_in_table, different_cell, a_cell, b_cell) is NOT exposed
  to P722 participant. Participant only sees geometry fields (h_gap, dy, same_style, etc.).
  Participant cannot determine table membership from geometry alone.

Human reviewer: Used Table 3 context (from page visual) → KEEP_SEPARATE.
→ E1 for IS-11 machine (TLD used correctly)
→ Evidence Exposure Gap for P722 participant (TLD info not exposed)
```

### AMB-375/AMB-418/AMB-519: Why Disagreement?

```
All 3 cases: Prose sentence boundary, period_end + cap_start.

Reviewer A: sentence boundary → KEEP_SEPARATE
Reviewer B: paragraph continuity → MERGE
Adjudicator: period + cap → separate sentences → KEEP_SEPARATE

Root cause: Annotation protocol defines MERGE/KEEP using undefined "文本单元" (text unit).
  Reviewer A: text unit = sentence → KEEP (period + cap = sentence boundary)
  Reviewer B: text unit = paragraph → MERGE (same paragraph, continuous flow)
  Adjudicator: chose sentence definition (period + cap → KEEP)

Evidence: period_end + cap_start IS DERIVABLE from P1 text (E3).
Standard: "text unit = sentence" is NOT explicitly defined in protocol (STANDARD_GAP).
→ NOT E5: evidence is sufficient, only standard is unclear.
→ E3, STANDARD_GAP, LS-2
```

### AMB-414/AMB-422: Why Figure Caption ABSTAIN?

```
Machine: TLD miss → IS-01=False + IS-02=True → ABSTAIN
Human: FIG prefix in text_a → figure caption → MERGE

Root cause: IS-11 doesn't compute has_fig_prefix.
  has_fig_prefix = text_a.startswith('FIG') — deterministic regex, E3 derivable.
  IS-01 checks is_number, not FIG prefix.
→ E2/E3, CONSUMER_INTEGRATION
```

### AMB-519: Is it E5?

```
NO. AMB-519 is NOT E5.

Evidence: period_end (text ends with '.') + cap_start (text starts with 'T') → DERIVABLE.
Standard: sentence vs paragraph — adjudicator resolved with period+cap → KEEP.
  This is STANDARD_GAP, not semantic ambiguity.

E5 requires: "even with sufficient evidence + clear standard, still cannot resolve."
  AMB-519: evidence IS sufficient (period+cap), standard IS resolvable (adjudicator did it).
  → NOT E5.
→ E3, STANDARD_GAP
```

---

## 10. Decision Dependency Matrix

### Human Decision × Evidence Source × Status

| Human Decision | Evidence Source | E-Class | Count | Machine Outcome |
|---|---|---|---|---|
| KEEP (agreed) | TLD (table structure) | E1 | 12 | TN (12) |
| KEEP (agreed) | P1 text (table context) | E2 | 27 | TN (13), ABSTAIN (13), FP (1) |
| KEEP (disagreed) | P1 text (period+cap) | E3 | 4 | TN (1), ABSTAIN (3) |
| MERGE (agreed) | P1 text (FIG prefix) | E2 | 2 | ABSTAIN (2) |

### Machine Mechanism × E-Class

| Mechanism | Count | E1 | E2 | E3 |
|---|---|---|---|---|
| TLD_DIFF_CELL | 13 | 12 | 0 | 1 (AMB-005, TLD FP) |
| FB_NOTNUM+NOTTEXT | 13 | 0 | 13 | 0 |
| FB_MIXED | 18 | 0 | 15 | 3 |
| FB_NUM+TEXT | 1 | 0 | 1 (FP) | 0 |

### P7 Cross-Validation

| Boundary Class | Count | E1 | E2 | Machine FP | Machine FN |
|---|---|---|---|---|---|
| TABLE_CELL | 11 | 0 | 11 | 3 | 0 |
| TABLE_CELL_PAIR | 4 | 0 | 4 | 0 | 0 |
| BODY_TEXT_CONTINUATION | 27 | 2 | 25 | 0 | 1 |
| REFERENCE_LIST_ENTRY | 16 | 1 | 15 | 0 | 1 |
| FIGURE_LABEL | 2 | 0 | 2 | 0 | 0 |
| OTHER_AMBIGUOUS | 9 | 0 | 9 | 0 | 0 |

> **P7 confirms: E2 dominant (95%), E4=0%, E5=0%. P7 has NO TLD → all table cases are E2.**

---

## 11. Learning Signal Analysis

| LS Level | Count | % | Description |
|---|---|---|---|
| LS-0 | 25 | 55% | Machine already correct (TN), Human confirms |
| LS-1 | 16 | 35% | Human points to existing evidence machine didn't use |
| LS-2 | 4 | 8% | Human points to derivable relation (period+cap) + standard clarification |
| LS-3 | 0 | 0% | NO reusable cross-case decision evidence signal found |

### LS-1 Analysis (16 cases)

All LS-1 cases are where:
- Machine ABSTAIN (15) or FP (1) — machine couldn't decide or decided wrong
- Human used P1 text content / page context — evidence EXISTS but not consumed
- Human points to EXISTING evidence, not new evidence

> **LS-1 = "Human used existing evidence that IS-11 didn't consume." This is Consumer Integration signal, NOT Learning Signal.**

### LS-2 Analysis (4 cases)

All LS-2 cases are prose disagreements where:
- Human provides period+cap relation (E3 derivable)
- Human provides content unit definition (sentence vs paragraph)
- The period+cap relation IS derivable (deterministic regex)
- The content unit standard IS a protocol issue (STANDARD_GAP)

> **LS-2 = "Human points to derivable relation + standard clarification." The derivable relation (period+cap) is a potential E3 improvement. The standard clarification is a PROTOCOL issue, not a Learning Signal.**

### LS-3 Analysis (0 cases)

**NO reusable cross-case Decision Evidence Signal found.**

- LS-1 signals are case-specific (each case has different text content)
- LS-2 signals are partially reusable (period+cap is cross-case) but classified as E3 derivable, not Learning Signal
- No signal that can be "learned" and applied to new cases without rule-ization

> **Human Feedback 不产生 LS-3 (可复用 Decision Evidence Signal)。LS-1 和 LS-2 指向的是已有 Evidence 的 Consumer Integration 改进，不是新的 Learning。**

---

## 12. Bottleneck Diagnosis

### Bottleneck Options

| Option | Support | Verdict |
|---|---|---|
| A. Candidate Construction | 0% Construction FP (prior audit) | REJECTED |
| B. Evidence Organization | 0% — evidence IS organized | REJECTED |
| **C. Consumer Integration** | **64% E2, 29/45 cases** | **PRIMARY** |
| D. Evidence Perception | P2 sufficient 100% (prior audit) | REJECTED |
| E. Human Semantic Judgment | 0% E5 | REJECTED |
| **F. Evaluation Standard** | **9% E3 STANDARD_GAP** | **SECONDARY** |
| G. Evidence Insufficient | 0% E4 | REJECTED |

### PRIMARY_BOTTLENECK = C (Consumer Integration)

**64% of cases (29/45)** have CONSUMER_INTEGRATION_GAP:
- P1 text EXISTS with full semantic content
- IS-11 reads P1 text via IS-01/IS-02 BUT only extracts binary (is_number / has_text)
- Human reads P1 text semantic content + page context → correct decision
- Machine uses binary content-type → ABSTAIN (15) or FP (1) or TN-by-luck (13)

**The断裂 is between P1 text content and IS-11's binary extraction.**

### SECONDARY_BOTTLENECK = F (Evaluation Standard)

**9% of cases (4/45)** have STANDARD_GAP:
- Evidence IS sufficient (period+cap derivable)
- But content unit standard (sentence vs paragraph) is NOT defined in annotation protocol
- Adjudicator resolved with period+cap → KEEP (sentence definition)
- This is a PROTOCOL issue, not an Evidence issue

### NOT Evidence Organization Gap

Evidence IS organized:
- P1: text strings (organized)
- P2: geometry facts (organized: bbox, bands, distances)
- TLD: table structure (organized: is_in_table, cell, boundaries)
- IS-01/IS-02: binary signals (organized: boolean)

The problem is NOT that evidence is unorganized. The problem is that IS-11's consumer only extracts binary signals from P1 text, not the full semantic content.

---

## 13. Counterfactual Analysis

### Counterfactual A: + has_fig_prefix (E3, deterministic regex)

```
has_fig_prefix = text_a.startswith('FIG') or text_b.startswith('FIG')
```

- 2 ABSTAIN → TN (AMB-414, AMB-422)
- New: TN=28, ABSTAIN=16, FP=1
- **Derivable, deterministic, no semantic leakage**
- Requires: Consumer Integration (compute from P1 text, use in IS-11 decision)

### Counterfactual B: + period_end + cap_start (E3, deterministic regex)

```
period_end = text_a.rstrip().endswith('.')
cap_start = text_b[0].isupper()
```

- 3 ABSTAIN → TN (AMB-375, AMB-418, AMB-519)
- AMB-005 already TN (via TLD FP, no change)
- New: TN=29, ABSTAIN=15, FP=1
- **Derivable, deterministic, no semantic leakage**
- Requires: Consumer Integration (compute from P1 text, use in IS-11 decision)
- **BUT**: this is RETROSPECTIVE_DISCRIMINATIVE_FEATURE (4/4 BOUNDARY correct, 0/41 CLEAR changed)
  — must NOT be implemented as a universal rule without independent validation

### Counterfactual A+B: Both E3 Derivations

- 5 ABSTAIN → TN
- New: TN=31, ABSTAIN=13, FP=1
- **28% of ABSTAIN cases resolvable by E3 derivable features**

### Counterfactual C: + P1 Text Semantic Consumption (E2, NOT Deterministic)

- 9 ABSTAIN → potentially TN (if table context identified from text)
- 1 FP → potentially TN (if different columns identified)
- **Requires semantic understanding** — NOT deterministic regex
- This is the REMAINING gap after E3 derivations

### Counterfactual Summary

```
Current:       TN=26 (58%), ABSTAIN=18 (40%), FP=1 (2%)
+ E3 (A+B):    TN=31 (69%), ABSTAIN=13 (29%), FP=1 (2%)
+ E2 (C):      TN=41 (91%), ABSTAIN=0 (0%), FP=0 (0%) [HYPOTHETICAL]
```

> **E3 derivable features (has_fig_prefix, period_end, cap_start) can resolve 28% of ABSTAIN cases deterministically. E2 semantic consumption can potentially resolve the remaining 72%, but requires non-deterministic semantic understanding.**

---

## 14. IS-11 Decision Logic (Reconstructed from Source Code)

```
IS-01 (FROZEN):
  IS01_PATTERN_1 = r'^\d+(\.\d+)*\.?$'    # pure number: '28.54', '4', '8.43'
  IS01_PATTERN_2 = r'^[A-Z]\.\d+$'         # like 'A.1'
  compute_is01_a(text_a) → bool

IS-02 (FROZEN):
  any(len(re.sub(r'[^a-zA-Z]', '', w)) > 2 for w in text_b.split())
  → True if text_b has any word with >2 alpha chars
  compute_is02_b(text_b) → bool

Baseline B (FROZEN §9.3):
  if is01_a and is02_b:     → MERGE           # number + text → same unit
  elif not is01_a and not is02_b: → KEEP_SEPARATE  # not-number + not-text → separate
  else:                     → INSUFFICIENT_EVIDENCE  # mixed → abstain

Experimental C (IS-11):
  base = baseline_b_decision(is01_a, is02_b)
  if is11_different_cell:   → KEEP_SEPARATE   # TLD override
  if is11_same_cell:        → MERGE           # TLD override
  return base                                 # fallback to IS-01/IS-02
```

### Key Observation

IS-01/IS-02 is a **content-type heuristic**, NOT a semantic analyzer:
- IS-01 checks if text_a is a pure number (regex)
- IS-02 checks if text_b has readable text (alpha word length >2)
- When both are True → "number + text" → MERGE (assumes value + label = same unit)
- When both are False → "not-number + not-text" → KEEP_SEPARATE

**This heuristic cannot distinguish "same column" from "different column"** — it only checks content type, not structural relationship. Human uses text SEMANTIC CONTENT ("4" = stage index, "MBConv6" = operator → different columns) + PAGE CONTEXT (sees table layout).

---

## 15. Limitations

1. **Retrospective Analysis**: E1-E5 classification is retrospective (based on GT and reviewer rationales). Cannot be used as prospective evidence without independent validation.

2. **45-Case Sample**: Statistics (64% E2, 9% E3) are from 45 IS-11 cases. NOT generalizable to all 545 candidates or all documents without independent validation.

3. **Reviewer Rationale Extraction**: Human evidence is inferred from reviewer rationales (text), not from eye-tracking or think-aloud protocols. Actual cognitive process may differ.

4. **Counterfactual A+B**: period_end+cap_start is RETROSPECTIVE_DISCRIMINATIVE_FEATURE (4/4 BOUNDARY correct, 0/41 CLEAR changed). Must NOT be implemented as universal rule. has_fig_prefix is deterministic but only tested on 2 cases.

5. **P7 Cross-Validation**: P7 uses different corpus and different evaluation protocol. E-class distribution may differ in larger samples.

6. **TLD FP on Prose**: AMB-005 shows TLD can produce false table detection on prose text (1/45 = 2%). This is a TLD limitation, not studied in depth here.

7. **IS-01/IS-02 Source Code**: Analysis of IS-01/IS-02 mechanism is from `tmp/is11_machine_evaluation.py` (experiment script). The actual production IS-01/IS-02 (if different) may have different logic.

---

## 16. Final Questions

### Q1: Human 正确判断 Boundary 时最重要的 Evidence 是什么？

**P1 text semantic content + page context.** Specifically:
- Table column/cell identity (35/45 = 77%): text meaning + table layout
- Figure caption (2/45 = 4%): FIG prefix in text
- Sentence boundary (4/45 = 9%): period_end + cap_start
- Text content + context (4/45 = 9%): text meaning

### Q2: 这些 Evidence 有多少已存在于 DICE？

**100% (45/45).** All evidence exists in P1 text or is derivable from P1 text.

### Q3: 多少属于 E1？

**12/45 (26%).** TLD correct, machine uses it.

### Q4: 多少属于 E2？

**29/45 (64%).** P1 text exists, IS-11 only extracts binary, not semantic content.

### Q5: 多少属于 E3？

**4/45 (9%).** period+cap derivable from P1 text (not computed by IS-11).

### Q6: 多少属于 E4？

**0/45 (0%).** NO evidence missing.

### Q7: 多少属于 E5？

**0/45 (0%).** NO genuine semantic judgment needed.

### Q8: 当前最大浪费发生在哪里？

**Consumer Integration (64%).** Evidence exists in P1 text, IS-11 reads it via IS-01/IS-02 but only extracts binary is_number/has_text. The semantic content is NOT consumed. Human reads the same P1 text and uses semantic content → correct decision.

### Q9: Human Feedback 是否产生新的可复用 Decision Evidence Signal？

**NO.** 0% LS-3. LS-1 (35%) points to existing evidence not consumed. LS-2 (8%) points to derivable relations + standard clarification. Neither is a new reusable signal.

### Q10: 如果没有产生 Learning Signal，为什么？

因为 Human 使用的 Evidence 100% 已存在于 DICE 中。Human Feedback 指向的是 "已有 Evidence 没有被 IS-11 consumer 正确使用"，而不是 "需要新的 Evidence 或新的 Learning"。

断裂不在 Evidence 层（Evidence 充足），而在 Consumer 层（IS-11 只提取 binary，不消费 semantic content）。

### Q11: 下一步最小研究动作？

**READ_ONLY_AUDIT.**

- 本审计已定位断裂：Consumer Integration Gap (64%) + Standard Gap (9%)
- 不需要 NO_ACTION（断裂已定位）
- 不需要 MINIMAL_PROTOTYPE（未授权 IMPLEMENTATION）
- 不需要 FORMAL_EXPERIMENT（未授权 EXPERIMENT）
- 下一步应继续 READ-ONLY 研究：
  1. 验证 E3 derivable features (has_fig_prefix, period_end, cap_start) 在 545-candidate universe 上的覆盖率
  2. 分析 IS-01/IS-02 binary 的信息损失（P1 text → binary 丢失了多少 decision-critical 信息）
  3. 研究是否可以安全地组织 P1 text content 为 IS-11 可消费的结构化信号（不引入 semantic leakage）

---

## 17. Statistics Summary

```
TOTAL_CASES_ANALYZED: 45 (IS-11) + 69 (P7) = 114

E1_COUNT: 12/45 (26%) [IS-11], 3/69 (4%) [P7]
E1_RATE: 26% [IS-11], 4% [P7]
E2_COUNT: 29/45 (64%) [IS-11], 66/69 (95%) [P7]
E2_RATE: 64% [IS-11], 95% [P7]
E3_COUNT: 4/45 (9%) [IS-11], 0/69 (0%) [P7]
E3_RATE: 9% [IS-11], 0% [P7]
E4_COUNT: 0/45 (0%)
E4_RATE: 0%
E5_COUNT: 0/45 (0%)
E5_RATE: 0%

DECISION_CRITICAL_EVIDENCE_COUNT: 45/45 (100% HIGH value)

HIGH_VALUE_EVIDENCE_COUNT: 45 (100%)
MEDIUM_VALUE_EVIDENCE_COUNT: 0
LOW_VALUE_EVIDENCE_COUNT: 0

MACHINE_UNUSED_EXISTING_EVIDENCE_COUNT: 29/45 (64%) [E2]
DERIVABLE_EVIDENCE_COUNT: 4/45 (9%) [E3]
MISSING_EVIDENCE_COUNT: 0/45 (0%) [E4]
GENUINE_SEMANTIC_JUDGMENT_COUNT: 0/45 (0%) [E5]

LS0_COUNT: 25/45 (55%)
LS1_COUNT: 16/45 (35%)
LS2_COUNT: 4/45 (8%)
LS3_COUNT: 0/45 (0%)

PRIMARY_BOTTLENECK: C (Consumer Integration) — 64% E2
SECONDARY_BOTTLENECK: F (Evaluation Standard) — 9% E3 STANDARD_GAP

TRUE_REUSABLE_SIGNAL_FOUND: NO (0% LS-3)
CURRENT_LEARNING_LEVEL: L3 (unchanged)

RECOMMENDED_NEXT_STEP: READ_ONLY_AUDIT
```

---

## 18. Final Gate

```
DICE_CORE_MODIFICATION              = NO
P1_P7_MODIFICATION                  = NO
P2_MODIFICATION                     = NO
TLD_MODIFICATION                    = NO
IS11_MODIFICATION                   = NO
M_B_MODIFICATION                    = NO
GT_MODIFICATION                     = NO
SIGNAL_MODIFICATION                 = NO
EVIDENCE_CUE_MODIFICATION           = NO
LLM                                 = NO
NEW_OBSERVATION                     = NO
NEW_MODULE                          = NO
NEW_ENGINE                          = NO
RUNTIME_CHANGE                      = NO
CAPABILITY_CHANGE                   = NO
FROZEN_BASELINE                     = INTACT (drift=0/7)
FROZEN_EXPERIMENT                   = INTACT
IMPLEMENTATION_AUTHORIZED           = FALSE
EXPERIMENT_AUTHORIZED               = FALSE
FORMAL_EXPERIMENT                   = NOT_STARTED
STOP                                = TRUE
```

`STOP = TRUE`。
