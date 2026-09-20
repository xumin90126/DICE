# L5.10 Evidence Cue Boundary Audit — Design Only

## READ-ONLY Audit — No Implementation

**Date**: 2026-09-12
**Scope**: Evidence Cue boundary verification based on Human Pilot P01 + prior audits
**Authority**: L5 Human Validation
**Governance**: READ_ONLY=TRUE, all modifications=0, FROZEN_BASELINE=INTACT

---

## 0. Executive Summary

**Core Question**: Can existing structural evidence be safely transformed into Human-usable Evidence Cue without crossing Semantic Boundary?

**Answer**: YES. Evidence Cue is a **transformation/presentation layer**, not a new reasoning capability. It uses only frozen structural observations, introduces zero semantic interpretation, and requires no new Primitive, Contract, or Architecture.

**Final Gate**: PASS — Evidence Cue is identifiable, safe, and does not require any new system capability.

---

## 1. Research Questions

### Q1: Is Evidence Cue a presentation/transformation layer or a new reasoning capability?

**Answer**: Evidence Cue is a **transformation layer**.

Evidence Cue performs deterministic translation of existing L2 structural facts into Human-readable natural language. It does not:
- Infer new facts
- Combine evidence across documents
- Learn patterns
- Produce semantic labels
- Make decisions

It is equivalent to a `format()` function: `structural_fact → human_readable_string`.

The transformation is:
```
Input:  different_cell=True (L2 boolean, frozen TLD provenance)
Output: "A and B are in different structural positions" (natural language)
```

No reasoning occurs between input and output. The transformation is a fixed mapping table.

### Q2: Can Evidence Cue be generated only from frozen structural observations?

**Answer**: YES, for the primary cues. PARTIALLY for secondary cues.

**Primary cues (fully available from frozen sources)**:

| Cue Source | Frozen Provenance | Availability |
|---|---|---|
| TLD is_in_table | frozen TLD (022f5c21e872ad9e) + IS-11 harness | 21/21 |
| TLD different_cell | frozen TLD + IS-11 harness | 21/21 |
| RSC region_forms | frozen RSC (phase3.1 params) | 21/21 |
| P1 text_a / text_b | frozen P1 atomic observations | 21/21 |
| line_obs_count | frozen P1 + P2 geometry | 21/21 |
| line_spans (neighbors) | PyMuPDF extraction from frozen PDFs | 21/21 |

**Secondary cues (require trivial computation from frozen data)**:

| Cue Source | Computation | Availability |
|---|---|---|
| starts_with_FIG | `text_a.startswith("FIG.")` | computable, 2/21 match |
| ends_with_period | `text_a.rstrip().endswith(".")` | computable, 2/21 match |
| is_numeric | `re.match(r'^[\d.\-]+$', text_a)` | computable, 10/21 match |

These computations are **pattern matches on existing text**, not new observations. The text is already frozen in P1. The pattern match is a trivial deterministic function with no semantic model.

### Q3: Does Evidence Cue introduce any semantic interpretation?

**Answer**: NO, if safe translations are used.

**Semantic leakage audit** performed on 11 candidate cues. All safe outputs contain only:
- Structural facts (A: Structural fact)
- Human interpretation support (B: Human interpretation support)

None contain:
- Semantic conclusions (C: forbidden)

**Forbidden output check**: All 11 cues pass — no "should merge", "should separate", "same content unit", or "system recommends" in any safe output.

**Critical distinction**: The SAFE translation removes semantic connotations from field names:
- "different cell" → "different structural position" (removes "cell" which implies "separate")
- "is in table" → "within a multi-column aligned structure" (removes "table" which implies "data table")

The raw field names (different_cell, is_in_table) carry semantic connotations, but the safe translations do not. The translation is a **de-semanticization** operation, not a semantic interpretation.

### Q4: Does Evidence Cue reduce information entropy for Human while preserving authority boundary?

**Answer**: YES.

**Information entropy analysis**:

| Layer | Data Points (21 cases) | Useful % | Human Interpretation Cost |
|---|---|---|---|
| Layer 1 (current UI) | 315 (15 fields × 21) | 20% | HIGH — must filter 80% noise |
| Layer 2 (structural, not shown) | 84 (4 fields × 21) | 100% | MEDIUM — field names need interpretation |
| Layer 3 (Evidence Cue) | 84 (4 cues × 21) | 100% | LOW — natural language, zero noise |

**Entropy reduction**: 315 data points (20% useful) → 84 data points (100% useful)
- Information quantity: DECREASED
- Decision utility: INCREASED
- Authority boundary: PRESERVED (cues contain no judgment)

### Q5: Does Evidence Cue require new Primitive?

**Answer**: NO.

Evidence Cue requires:
- No Pattern Engine
- No Classifier
- No Semantic Model
- No New Capability
- No New Authority Level
- No New Primitive
- No New Contract
- No New Architecture

It requires only: a fixed translation table mapping L2 structural facts to natural-language strings, using already-frozen evidence.

---

## 2. Evidence Source Audit

### All Possible Evidence Cue Sources

| Source | Field | Available | Provenance | Cue Potential |
|---|---|---|---|---|
| **TLD** | is_in_table | 21/21 | frozen TLD (022f5c21e872ad9e) | HIGH |
| **TLD** | different_cell | 21/21 | frozen TLD + IS-11 harness | HIGH |
| **TLD** | same_cell | 21/21 | frozen TLD + IS-11 harness | MEDIUM (redundant with different_cell) |
| **TLD** | table_info (tables_detected, row/col_count) | 21/21 | frozen TLD | MEDIUM |
| **SCE** | different_local_partition | 11/21 | frozen SCE (phase3.1 params) | HIGH (when available) |
| **SCE** | same_structural_region | 11/21 | frozen SCE | MEDIUM |
| **SCE** | pairwise_same_y_band | 11/21 | frozen SCE | LOW (redundant with dy) |
| **RSC** | region_forms | 21/21 | frozen RSC (phase3.1 params) | HIGH |
| **RSC** | local_partitions_co_occurring | 21/21 | frozen RSC | MEDIUM |
| **P1** | text_a | 21/21 | frozen P1 atomic observation | HIGH (direct content) |
| **P1** | text_b | 21/21 | frozen P1 atomic observation | HIGH (direct content) |
| **P1** | bbox_a / bbox_b | 21/21 | frozen P1 | MEDIUM (position reference) |
| **P2** | h_gap | 21/21 | frozen P2 geometry | LOW (correct but not decision-relevant) |
| **P2** | dy | 21/21 | frozen P2 geometry | LOW (all same-line in pilot) |
| **P3** | same_style | 21/21 | frozen P3 style | LOW (never used by Human) |
| **P3** | style_sig_a / style_sig_b | 21/21 | frozen P3 | IRRELEVANT (not human-readable) |
| **LC** | line_spans | 21/21 | PyMuPDF from frozen PDFs | HIGH (neighbor context) |
| **LC** | left_neighbor | 17/21 | derived from line_spans | HIGH |
| **LC** | right_neighbor | 14/21 | derived from line_spans | HIGH |
| **TP** | starts_with_FIG | computable | trivial pattern match on P1 text | MEDIUM |
| **TP** | ends_with_period | computable | trivial pattern match on P1 text | MEDIUM |
| **TP** | is_numeric | computable | trivial pattern match on P1 text | MEDIUM |
| **TP** | b_starts_capital | computable | trivial pattern match on P1 text | LOW |

### Availability Summary

- **Fully available (21/21)**: 13 sources from frozen TLD/RSC/P1/P2/P3
- **Partially available (11/21)**: 2 sources from SCE (admitted cases only)
- **Trivially computable**: 4 text pattern sources from existing P1 text
- **Not available**: 0 — no source requires new observation

---

## 3. Semantic Leakage Audit

### Classification System

| Class | Description | Allowed? |
|---|---|---|
| A | Structural fact — verifiable, traceable, no semantic content | ✅ YES |
| B | Human interpretation support — presents facts in a way that helps Human infer, but does not infer | ✅ YES |
| C | Semantic conclusion — contains judgment, recommendation, or semantic label | ❌ FORBIDDEN |

### All Candidate Cues Classified

| Cue ID | Source | Safe Output | Class | Leakage Risk | Contains Judgment? |
|---|---|---|---|---|---|
| CUE-01 | TLD is_in_table | "within a detected multi-column aligned structure" | A | LOW (after translation) | NO |
| CUE-02 | TLD different_cell | "in different structural positions" | A | LOW (after translation) | NO |
| CUE-03 | SCE different_local_partition | "assigned to different x-position groups" | A | LOW (after translation) | NO |
| CUE-04 | RSC region_forms | "multi-column structure was/was not detected" | A | LOW | NO |
| CUE-05 | P1 text pattern | "Text A starts with 'FIG.'" | A | LOW (raw text fact) | NO |
| CUE-06 | P1 text pattern | "Text A ends with a period" | A | LOW | NO |
| CUE-07 | P1 text pattern | "Text A is a number" | A | LOW | NO |
| CUE-08 | line_obs_count | "There are N items on this line" | A | NONE | NO |
| CUE-09 | line_spans neighbors | "Text to the left of A: '...'" | A | NONE | NO |
| CUE-10 | TLD + line_obs_count | "Within multi-column structure; N items on line" | A+B | LOW | NO |
| CUE-11 | TLD=False + line_obs=2 | "No multi-column structure; 2 items on line" | A+B | LOW | NO |

### Forbidden Output Check

All 11 cues checked against forbidden phrases:
- "应该合并" / "should merge" → NOT FOUND ✅
- "应该分开" / "should separate" → NOT FOUND ✅
- "属于同一个语义单元" / "same content unit" → NOT FOUND ✅
- "这是同一句话" / "this is one sentence" → NOT FOUND ✅
- "系统认为" / "system recommends" → NOT FOUND ✅

**Result**: 11/11 cues pass. Zero semantic leakage in safe outputs.

### Critical Translation Rules

| Internal Field | ❌ Unsafe (raw field name) | ✅ Safe (translated) |
|---|---|---|
| is_in_table=True | "in a table" | "within a detected multi-column aligned structure" |
| is_in_table=False | "not in a table" | "no multi-column aligned structure detected" |
| different_cell=True | "in different cells" | "in different structural positions" |
| same_cell=True | "in the same cell" | "in the same structural position" |
| different_local_partition=True | "in different partitions" | "assigned to different x-position groups" |
| region_forms=False | "region not formed" | "no multi-column structure detected around A and B" |

The translation removes semantic nouns ("table", "cell", "partition") and replaces them with structural descriptions ("multi-column aligned structure", "structural position", "x-position group").

---

## 4. Human Cognitive Load Audit

### Current UI Fields (15 per case)

| Field | Human Used? | Burden Type | Value Class | Action |
|---|---|---|---|---|
| text_a | ✅ YES | reading | A. Directly Useful | **KEEP** |
| text_b | ✅ YES | reading | A. Directly Useful | **KEEP** |
| page_image | ✅ YES | visual | A. Directly Useful | **KEEP** |
| A/B highlight | ✅ YES | visual | A. Directly Useful | **KEEP** |
| line_spans | ✅ YES | reading | A. Directly Useful | **KEEP** |
| line_obs_count | ❌ NO (indirect) | numerical | B. Indirectly Useful | **KEEP** (distill as "N items on line") |
| doc_id | ❌ NO | reading | B. Indirectly Useful | **KEEP** (context) |
| page_number | ❌ NO | reading | B. Indirectly Useful | **KEEP** (context) |
| h_gap | ❌ NO | numerical interpretation | C. Low Utility | **REMOVE** |
| dy | ❌ NO | numerical interpretation | C. Low Utility | **REMOVE** |
| same_style | ❌ NO | boolean interpretation | C. Low Utility | **REMOVE** |
| width_a | ❌ NO | numerical interpretation | C. Low Utility | **REMOVE** |
| width_b | ❌ NO | numerical interpretation | C. Low Utility | **REMOVE** |
| style_sig_a | ❌ NO | string decoding | D. Potentially Misleading | **REMOVE** |
| style_sig_b | ❌ NO | string decoding | D. Potentially Misleading | **REMOVE** |

### Summary

- **KEEP (5 + 3 context)**: text_a, text_b, page_image, A/B highlight, line_spans, line_obs_count, doc_id, page_number
- **REMOVE (7)**: h_gap, dy, same_style, width_a, width_b, style_sig_a, style_sig_b
- **ADD (4 cues)**: structural position cue, multi-column structure cue, text pattern cue, neighbor context cue

### Cognitive Load Reduction

| Metric | Current | Proposed |
|---|---|---|
| Fields per case | 15 | 8 (5 kept + 3 added) |
| Numerical fields | 5 | 1 (line_obs_count, distilled) |
| Technical strings | 2 (style_sig) | 0 |
| Fields requiring interpretation | 12 | 2 (structural cues, already in natural language) |
| Noise ratio | 80% | 0% |

---

## 5. Three-Layer Comparison

### Representative Case: IS11-AMB-034 (A="21.59", B="5.71", GT=KEEP_SEPARATE)

**Layer 1: Raw Evidence (current UI)**
```
text_a = '21.59'
text_b = '5.71'
h_gap = 27.2pt
same_style = True
width_a = 20.2pt
width_b = 15.7pt
style_sig_a = 'NimbusRomNo9L-Regu|9.0|0|0|-|0|-'
line_obs_count = 3
```
→ Human burden: 8 fields, 5 numerical/technical, must filter noise
→ Decision utility: text + image useful; gap/style/width/sig NOT useful

**Layer 2: Structural Evidence (System has, not shown)**
```
is_in_table = True
different_cell = True
different_local_partition = True
region_forms = True
```
→ Human burden: 4 boolean fields, names need interpretation
→ Decision utility: HIGH — but field names carry semantic connotation

**Layer 3: Evidence Cue (proposed safe translation)**
```
"A and B are within a detected multi-column aligned structure"
"A and B are in different structural positions"
"There are 4 items on this line"
"Text to the left of A: 'PReLU-net [13]'"
```
→ Human burden: 4 short natural-language statements
→ Decision utility: HIGH — directly actionable
→ Semantic leakage: NONE

### Is Layer 3 Necessary?

**Layer 2 alone is insufficient** because:
1. Field names ("different_cell", "is_in_table") carry semantic connotations that create automation bias risk
2. Human must interpret boolean values into natural-language concepts (extra cognitive step)
3. No safe translation boundary exists — showing raw field names is unsafe

**Layer 3 is necessary** because:
1. It performs the critical de-semanticization translation
2. It reduces cognitive load (natural language vs boolean/numeric)
3. It establishes a clear boundary: "structural facts in Human-readable form, no semantic conclusions"
4. It is the minimum transformation that makes L2 evidence Human-safe

**Layer 3 is NOT a new reasoning layer** because:
1. The translation is a fixed mapping table (no inference)
2. The input is frozen L2 evidence (no new observation)
3. The output contains no semantic conclusion (no judgment)
4. The provenance is fully traceable (each cue maps to a specific frozen field)

---

## 6. Anti Over-Design Check

| Question | Answer |
|---|---|
| Does Evidence Cue require Pattern Engine? | **NO** |
| Does Evidence Cue require Classifier? | **NO** |
| Does Evidence Cue require Semantic Model? | **NO** |
| Does Evidence Cue require New Capability? | **NO** |
| Does Evidence Cue require New Authority Level? | **NO** |
| Does Evidence Cue require New Primitive? | **NO** |
| Does Evidence Cue require New Contract? | **NO** |
| Does Evidence Cue require New Architecture? | **NO** |
| Does Evidence Cue require L5.9? | **NO** |

**All answers are NO. No STOP condition triggered.**

Evidence Cue is a **transformation layer** that:
- Reads frozen L2 structural fields
- Applies a fixed translation table
- Outputs natural-language strings
- Contains no inference, no learning, no decision

---

## 7. Evidence Cue Specification (Design Only — NOT Implemented)

### Minimal Cue Set (4 cues per case)

| Cue # | Source | Safe Output Template | Availability |
|---|---|---|---|
| 1 | TLD is_in_table + RSC region_forms | "A and B are {within / not within} a detected multi-column aligned structure" | 21/21 |
| 2 | TLD different_cell | "A and B are in {different / the same} structural positions" | 21/21 |
| 3 | line_obs_count | "There are {N} text items on this line" | 21/21 |
| 4 | line_spans neighbors | "Text to the left of A: '{text}'" / "Text to the right of B: '{text}'" | 17+14/21 |

### Optional Cues (when pattern matches)

| Cue # | Source | Safe Output Template | Match Rate |
|---|---|---|---|
| 5 | P1 text pattern | "Text A starts with 'FIG.'" | 2/21 |
| 6 | P1 text pattern | "Text A ends with a period" | 2/21 |
| 7 | P1 text pattern | "Text A is a number" | 10/21 |

### Translation Table (Complete)

```python
# NOT IMPLEMENTED — design specification only

CUE_TRANSLATIONS = {
    # CUE-01: structural membership
    'is_in_table': {
        True:  'within a detected multi-column aligned structure',
        False: 'no multi-column aligned structure detected',
    },
    # CUE-02: positional relation
    'different_cell': {
        True:  'in different structural positions',
        False: 'in the same structural position',
    },
    # CUE-03: line context
    'line_obs_count': lambda n: f'There are {n} text items on this line',
    # CUE-04: neighbor context
    'left_neighbor':  lambda text: f'Text to the left of A: "{text}"',
    'right_neighbor': lambda text: f'Text to the right of B: "{text}"',
    # CUE-05/06/07: text patterns
    'starts_with_fig': 'Text A starts with "FIG."',
    'ends_with_period': 'Text A ends with a period',
    'is_numeric': 'Text A is a number',
}
```

This is a **fixed mapping table**. No inference. No learning. No semantic model.

---

## 8. Counter-Evidence (Preserved)

1. **A-phase 21/21 correct** — Human achieved perfect accuracy WITHOUT Evidence Cues. Page images compensated.
2. **Average 3.9s/item** — fast selection suggests current evidence was sufficient for P01.
3. **n=1** — cannot verify that Evidence Cue improves speed/accuracy/cognitive load.
4. **MERGE=2** — both captions; cannot verify cues generalize to other MERGE types.
5. **System≠GT=0** — cannot test automation bias risk of cues.
6. **conflict=0** — no contradictory evidence test.
7. **is_in_table=False appears in both MERGE and KEEP_SEPARATE** — TLD alone does not determine judgment (this is a feature: cue provides context without dictating answer).
8. **SCE fields only available for 11/21 cases** — partial availability limits cue coverage.

**These counter-evidence points do NOT invalidate the audit findings.** They limit the CONFIDENCE of the findings but do not contradict the structural analysis. The audit identifies what is POSSIBLE from existing evidence, not what is PROVEN to improve outcomes.

---

## 9. Final Gate

```
╔══════════════════════════════════════════════════════════╗
║              EVIDENCE CUE BOUNDARY GATE                   ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  Q1: Presentation layer, not reasoning capability?       ║
║      → YES ✅                                            ║
║                                                          ║
║  Q2: Generatable from frozen observations only?          ║
║      → YES (primary cues 21/21; secondary computable) ✅ ║
║                                                          ║
║  Q3: No semantic interpretation introduced?              ║
║      → YES (11/11 cues pass leakage check) ✅            ║
║                                                          ║
║  Q4: Reduces entropy, preserves authority?               ║
║      → YES (315→84 data points, 0% judgment content) ✅  ║
║                                                          ║
║  Q5: No new Primitive required?                          ║
║      → YES (no Primitive/Contract/Architecture) ✅       ║
║                                                          ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  GATE RESULT: PASS                                       ║
║                                                          ║
║  Evidence Cue is:                                        ║
║    = A TRANSFORMATION LAYER (not reasoning)              ║
║    = GENERATED FROM FROZEN EVIDENCE                      ║
║    = FREE OF SEMANTIC INTERPRETATION                     ║
║    = ENTROPY-REDUCING FOR HUMAN                          ║
║    = AUTHORITY-PRESERVING                                ║
║    = REQUIRING NO NEW PRIMITIVE                          ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

---

## 10. Governance

```
READ_ONLY = TRUE

CODE_MODIFICATION = 0
UI_MODIFICATION = 0
GT_MODIFICATION = 0
TLD_MODIFICATION = 0
ATOMIC_MODIFICATION = 0
IS11_DECISION_MODIFICATION = 0
AGGREGATION_MODIFICATION = 0
COMPRESSION_MODIFICATION = 0
L5.5_MODIFICATION = 0

NEW_PRIMITIVE = 0
NEW_CONTRACT = 0
NEW_ARCHITECTURE = 0
NEW_PATTERN_ENGINE = 0
PATTERN_REGISTRY = 0
PATTERN_MINER = 0
CLASSIFIER = 0
L5.9 = 0

PRODUCTION = FALSE
FROZEN_BASELINE = INTACT
HUMAN_DATA = REAL_PILOT_ONLY
NO_SIMULATION = TRUE
STOP = TRUE
```

### Pilot Limitations Preserved

```
Pilot = exploratory engineering evidence
n = 1
21 A cases
MERGE = 2
Conflict = 0
System ≠ GT = 0
```

### Evidence Classification

- This audit = **B-class** (engineering analysis, single pilot)
- Evidence Cue safety = **B-class** (structural analysis confirms no leakage, but not empirically tested with n>1)
- Evidence Cue utility = **C-class** (hypothesis — not verified that cues improve Human outcomes)
- Translation table = **B-class** (deterministic, traceable, but utility not empirically tested)
