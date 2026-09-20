# DICE 83 Potential Evaluation Candidates — Human Construction Audit

**Date**: 2026-09-12
**Mode**: HUMAN CASE CONSTRUCTION AUDIT (READ-ONLY)
**Reviewer**: Single reviewer (AI-assisted, no independent second reviewer)
**Input**: `tmp/potential_evaluation_case_set.json` (83 candidates)

---

## 1. Summary

From 83 Potential Evaluation Candidates, human audit found:

| Metric | Count |
|---|---|
| Keep for Pilot (YES) | 54 |
| Exclude (NO) | 27 |
| Uncertain | 2 |
| HIGH case value | 27 |
| MEDIUM case value | 22 |
| LOW case value | 34 (includes 9 controls) |

**Potential Pilot Set = 54 candidates** (subject to further refinement)

**Single-reviewer limitation**: This audit was performed by one reviewer (AI-assisted). No independent second reviewer was available. Results should be treated as a first-pass filter, not as validated adjudication.

---

## 2. Audit Completeness

| Check | Status |
|---|---|
| Total candidates audited | 83/83 ✅ |
| All fields completed per case | ✅ |
| Prose family audited | 31/31 ✅ |
| Figure_Caption family audited | 11/11 ✅ |
| Row_Label_Value family audited | 32/32 ✅ |
| Table_Header + Other + Controls | 9/9 ✅ |

---

## 3. Results by Structure Family

| Family | Total | Keep=YES | Keep=NO | Keep=UNC | Keep Rate |
|---|---|---|---|---|---|
| PROSE | 31 | 20 | 9 | 2 | 65% |
| FIGURE_CAPTION | 11 | 11 | 0 | 0 | 100% |
| ROW_LABEL_VALUE | 32 | 15 | 17 | 0 | 47% |
| TABLE_HEADER | 4 | 4 | 0 | 0 | 100% (controls) |
| OTHER | 2 | 1 | 1 | 0 | 50% |
| TABLE_NUMERIC | 2 | 2 | 0 | 0 | 100% (controls) |
| AXIS | 1 | 1 | 0 | 0 | 100% (control) |

### Key Finding

- **FIGURE_CAPTION**: 100% keep rate — all 11 are genuine caption structure cases with HIGH value
- **PROSE**: 65% keep rate — 20 genuine sentence boundaries kept, 9 excluded (misclassified table headers, subfigure labels, trivial fragments)
- **ROW_LABEL_VALUE**: 47% keep rate — 15 genuine row-vs-column ambiguity kept, 17 excluded (trivial index+operator pairs, header+value pairs, near-duplicates)

---

## 4. Machine vs Human Discrepancy Analysis

### Overall Agreement

| Discrepancy Type | Count | Description |
|---|---|---|
| MATCH | 51 | Machine and human agreed |
| FALSE_MEDIUM | 21 | Machine=MEDIUM, Human=LOW |
| FALSE_HIGH | 5 | Machine=HIGH, Human=LOW |
| OVERESTIMATED | 5 | Machine=HIGH, Human=MEDIUM |
| MISSED_OPPORTUNITY | 1 | Machine=UNKNOWN, Human=MEDIUM |

**Agreement rate**: 51/83 = 61%

### Construction Heuristic Errors Found

#### Error 1: FALSE_HIGH — PROSE Misclassification (5 cases)

The structural classifier misclassified **table headers** as PROSE:

| Case | text_a | text_b | Actual Type |
|---|---|---|---|
| AMB-127 | "." | "As discussed in (" | Table cell fragment |
| AMB-419 | "." | "Our goal is to build" | Chart context fragment |
| AMB-142 | "Top-5 Acc." | "#Params" | TABLE_HEADER |
| AMB-236 | "Acc." | "#Param" | TABLE_HEADER |
| AMB-020 | "top-1 err." | "top-5 err." | TABLE_HEADER |

**Root cause**: The classifier checks for sentence-ending punctuation and text length, but table headers like "top-1 err." end with a period and exceed the length threshold, triggering PROSE classification.

**Fix (future, not this round)**: Check if the same line contains multiple short capitalized tokens (table header row pattern) before classifying as PROSE.

#### Error 2: FALSE_MEDIUM — ROW_LABEL_VALUE Trivial Pairs (21 cases)

Many ROW_LABEL_VALUE cases are trivially separable:

| Pattern | Example | Count | Why Trivial |
|---|---|---|---|
| Stage index + operator | "1" / "Conv3x3" | 3 | Obviously different columns |
| Scaling param + FLOPs | "=2)" / "14.7B" | 4 | Obviously different columns |
| Header + first value | "Val top1" / "77.11" | 2 | Header vs data, trivial |
| Ellipsis + matrix value | "…" / "-0.4765" | 2 | Not a real text pair |
| Model + dataset label | "ResNet-101" / "07+12" | 1 | Different columns |
| Model size + metric | "70B" / "16 (1.0x)" | 2 | Different columns |
| Row label + value | "LLaMA LLM" / "70B" | 1 | Different columns |
| Comma + conjunction | "," / "which" | 1 | Trivial fragment |
| Subfigure labels | "(b) width scaling" / "(c) depth scaling" | 3 | Obviously different labels |
| Table header row | "layer name output size" / "18-layer" | 1 | Header vs data |
| Param + model reversed | "85M" / "EfficientNet-B0" | 1 | Different columns |

**Root cause**: The classifier treats any numeric+text or text+numeric pair as ROW_LABEL_VALUE with MEDIUM value. But many such pairs are obviously in different table columns (stage index vs operator type, scaling parameter vs FLOPs count).

**Fix (future)**: Add checks for:
- Very short numeric A (single digit = stage index, not row label)
- Pattern like "=N)" (scaling parameter, not row label)
- Ellipsis as text (not a real span)
- Same-line context showing clear column separation

#### Error 3: Near-Duplicate Over-Selection

Several near-duplicate groups were selected:

| Group | Cases | Pattern |
|---|---|---|
| Stage index + operator | AMB-132, 133, 134 | "N" / "MBConv..." |
| Scaling + FLOPs | AMB-224, 226, 335, 337 | "=N)" / "XB" |
| Subfigure labels | AMB-124, 125, 126 | "(X) ... scaling" / "(Y) ... scaling" |
| Figure refs | AMB-389, 390 | "(Fig." / "N.X)" |
| Table rows | AMB-082, 084 | "baseline Faster R-CNN (...)" / "metric" |
| Method + error | AMB-041, 114, 117 | "Method [ref]" / "error_value" |
| Matrix ellipsis | AMB-430, 431 | "…" / "value" |
| Header + value | AMB-339, 347 | "header" / "first_value" |

**Root cause**: Near-duplicate detection used Jaccard word similarity, but these pairs have different text content (different numbers, different method names) so Jaccard is low. They're structural duplicates — same table, same row pattern, different data.

#### Error 4: FALSE_BOUNDARY (20 cases)

Machine flagged `potential_boundary=True` for 20 cases where human found no genuine boundary:

| Pattern | Count | Why No Boundary |
|---|---|---|
| Row label + value in different columns | 12 | Obviously different columns |
| Subfigure labels | 3 | Obviously different labels |
| Scaling + FLOPs | 3 | Obviously different columns |
| Other | 2 | — |

**Root cause**: The classifier flags `potential_boundary=True` for all ROW_LABEL_VALUE cases, assuming row-vs-column ambiguity. But many such pairs are clearly in different columns (visible from same-line context).

---

## 5. Construction Heuristic Validity Assessment

### What Works Well

1. **PROSE classification for sentence boundaries**: When correctly classified, PROSE cases have genuine MERGE/KEEP_SEPARATE ambiguity. 20/31 PROSE cases were correctly identified as valuable.
2. **FIGURE_CAPTION classification**: 100% accuracy — all 11 cases are genuine caption structure cases.
3. **Control case selection**: 9 control cases correctly identified as LOW value, retained for baseline.
4. **Independence constraints**: Page concentration limit (≤3/page) effectively reduced historical 8/page concentration.

### What Fails

1. **PROSE misclassification of table headers**: 5 cases where table headers ending with "." were classified as PROSE. **Fix**: Add table-header-row detection.
2. **ROW_LABEL_VALUE over-selection**: 17/32 ROW_LABEL_VALUE cases are trivially separable. **Fix**: Add structural context check (same-line word pattern).
3. **Near-duplicate detection insufficient**: Structural duplicates (same table, same pattern, different data) not caught by text similarity. **Fix**: Add structural pattern similarity (same-line layout, same table position).
4. **Potential boundary over-flagging**: 20 false boundary flags. **Fix**: Only flag boundary when same-line context shows genuine ambiguity, not for all ROW_LABEL_VALUE.

### CONSTRUCTION_HEURISTIC_VALIDITY = CONDITIONAL

The heuristic correctly identifies HIGH-value cases (PROSE boundaries, figure captions) but over-selects MEDIUM-value cases (ROW_LABEL_VALUE) and misclassifies some table headers as PROSE. With the identified fixes, the heuristic could achieve ~80% agreement with human audit.

---

## 6. Potential Pilot Set Composition

### 54 Candidates Recommended for Pilot

| Family | Count | Value |
|---|---|---|
| PROSE (sentence boundary) | 20 | HIGH — genuine MERGE/KEEP ambiguity |
| FIGURE_CAPTION | 11 | HIGH — caption structure ambiguity |
| ROW_LABEL_VALUE (genuine) | 12 | MEDIUM — row vs column ambiguity |
| Section headers | 3 | MEDIUM — number + title boundary |
| OTHER (figure labels) | 1 | MEDIUM |
| Controls (TABLE_NUMERIC/HEADER/AXIS) | 7 | LOW — baseline controls |

### Coverage Assessment

| Coverage Dimension | Covered? | Count |
|---|---|---|
| PROSE boundary | ✅ | 20 |
| FIGURE_CAPTION | ✅ | 11 |
| ROW vs COLUMN ambiguity | ✅ | 12 |
| Section header boundary | ✅ | 3 |
| Control (trivial) | ✅ | 7 |
| UNKNOWN-eligible | ⚠️ | 0 explicit, but some ROW_LABEL_VALUE may prove uncertain |
| Conflict | ⚠️ | 0 explicit, requires Cue computation to identify |
| System ≠ GT | ❌ | Requires GT adjudication first |

### What's Still Missing

1. **UNKNOWN-eligible cases**: No cases were explicitly identified as evidence-insufficient. This coverage gap may need to be filled by computing TLD and identifying cases where structural evidence is missing.
2. **Conflict cases**: Cannot be identified without Cue computation. The 30 "potential_conflict" cases from machine classification were mostly false positives.
3. **System ≠ GT cases**: Cannot be identified without GT adjudication.
4. **Cross-document diversity**: 54 cases from 4 documents — exploratory scale only.

---

## 7. Historical 45 vs Audited 54 Comparison

| Dimension | Historical 45 | Audited 54 |
|---|---|---|
| Trivial proportion | 84% | 13% (7 controls) |
| PROSE boundary | 4 | 20 |
| FIGURE_CAPTION | 2 | 11 |
| ROW vs COLUMN ambiguity | 0 | 12 |
| Ceiling risk HIGH | ~84% | 13% |
| Genuine boundary | ~6 | 35+ |
| Section header | 0 | 3 |

---

## 8. Key Recommendations (For Future Rounds)

1. **Fix PROSE misclassification**: Add table-header-row detection to prevent classifying "top-1 err." / "top-5 err." as PROSE.
2. **Fix ROW_LABEL_VALUE over-selection**: Add same-line context check — if the same line has clear column separation (multiple short tokens at regular intervals), classify as trivial.
3. **Improve near-duplicate detection**: Use structural pattern similarity (same table, same row position) in addition to text similarity.
4. **Compute TLD before Pilot**: TLD availability will enable conflict detection and UNKNOWN-eligible case identification.
5. **GT adjudication after selection**: GT must be assigned to the 54 candidates AFTER selection to prevent leakage.
6. **Pilot with 15-20 cases first**: Don't use all 54 at once. Start with a diverse subset to discover difficulty distribution.

---

## 9. Limitations

1. **Single reviewer**: No independent second reviewer. Agreement rates are against machine, not against another human.
2. **No page images used**: Audit was based on text content and same-line context extracted via PyMuPDF. Page images were available but not systematically reviewed for all 83 cases.
3. **No GT used**: Correct — GT was not used for selection. But this means we don't know the actual MERGE/KEEP distribution of the 54 recommended cases.
4. **AI-assisted review**: The reviewer is an AI, not a human domain expert. Judgments about "semantic judgment opportunity" are based on text structure analysis, not deep domain understanding.
5. **Near-duplicate detection may have missed cases**: Structural duplicates in tables may still exist in the 54 recommended cases.

---

## 10. Final Gate

```
CASE_COUNT = 83
HUMAN_AUDIT_COMPLETENESS = PASS
TRIVIALITY_AUDIT = PASS
SEMANTIC_OPPORTUNITY_AUDIT = PASS
EVIDENCE_SUFFICIENCY_AUDIT = PASS
BOUNDARY_AUDIT = PARTIAL (20 false boundary flags found)
CONFLICT_AUDIT = PARTIAL (cannot fully assess without Cue computation)
CUE_RELEVANCE_AUDIT = PASS
INDEPENDENCE_AUDIT = PARTIAL (structural near-duplicates may remain)
CONSTRUCTION_HEURISTIC_VALIDITY = CONDITIONAL
POTENTIAL_PILOT_SET = 54 cases
FINAL_EVALUATION_SET = NOT_ESTABLISHED
```

---

## 11. Governance

```
DICE_CORE_MODIFICATION = FALSE
P1_P7_MODIFICATION = FALSE
TLD_MODIFICATION = FALSE
ATOMIC_OBSERVATION_MODIFICATION = FALSE
FROZEN_BASELINE = INTACT
FROZEN_EXPERIMENT = INTACT
FORMAL_EXPERIMENT = NOT_AUTHORIZED
GT_MODIFICATION = FALSE
PRODUCTION = FALSE
RUNTIME_AUTHORITY = ZERO
ITERATIVE_LEARNING = INSUFFICIENT_EVIDENCE
STOP = TRUE
```
