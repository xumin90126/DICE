# L5 Evidence Distillation Boundary Audit

## READ-ONLY Audit — No Implementation, No Architecture, No UI Changes

**Date**: 2026-09-12
**Scope**: Based on Evidence Relevance/Distillation Audit + Human Pilot P01
**Authority**: L5 Human Validation
**Evidence Class**: B (engineering analysis, single pilot, n=1)
**Governance**: READ_ONLY=TRUE, all modifications=0, FROZEN_BASELINE=INTACT

---

## 0. Executive Summary

**Core Question**: Can the System, using only existing Frozen Evidence, construct Human-understandable, Decision-Relevant Evidence Cues that do NOT contain final Judgment?

**Answer**: YES, for 3 of 5 Human Evidence types. PARTIALLY for the remaining 2. The minimum safe boundary is Boundary 2 (Decision-Relevant Evidence Cue), which translates L2 structural facts into Human-actionable language without crossing into L4 semantic interpretation.

**Single Conclusion**: **B. DISTILLATION GAP IS REAL AND MINIMAL CUE IS IDENTIFIABLE**

---

## 1. Research Question

**RQ-ED1**: For Human's actual judgment dependencies in the Pilot, can the System construct "Human-understandable, Decision-Relevant, but non-Judgmental" Evidence Cues using only existing Frozen Evidence?

The desired pipeline is:
```
Evidence → Evidence Cue → Human Judgment
```
NOT:
```
Evidence → System Judgment → Human
```

---

## 2. Four-Layer Classification

All System fields were classified into strict layers:

### Layer Classification Results

| Field | L1 Raw | L2 Structural | L3 Cue | L4 Interpretation | Leakage Risk |
|---|---|---|---|---|---|
| text_a / text_b | ✅ | | | | NONE |
| bbox_a / bbox_b | ✅ | | | | NONE |
| page_image | ✅ | | | | NONE |
| line_spans | ✅ | | | | NONE |
| h_gap | | ✅ | | | NONE (low utility) |
| dy | | ✅ | | | NONE |
| same_style | | ✅ | | | LOW |
| line_obs_count | | ✅ | | | NONE |
| width_a / width_b | ✅ | | | | NONE (irrelevant) |
| style_sig | ✅ | | | | NONE (irrelevant) |
| **is_in_table** | | ✅ | | | **MEDIUM** — "table" is semantic concept |
| **same_cell** | | ✅ | | | **HIGH** — "same cell" implies "should merge" |
| **different_cell** | | ✅ | | | **HIGH** — "different cell" implies "should separate" |
| **different_local_partition** | | ✅ | | | **MEDIUM** — "partition" implies separation |
| same_structural_region | | ✅ | | | LOW |
| region_forms | | ✅ | | | LOW |
| starts_with_FIG (not yet computed) | ✅ | | | | MEDIUM — "FIG." implies caption |
| ends_with_period (not yet computed) | ✅ | | | | LOW |
| is_numeric (not yet computed) | ✅ | | | | LOW |
| left_neighbor_text | ✅ | | | | NONE |
| items_on_line | | ✅ | | | NONE |

### Critical Finding: TLD Fields are L2 Structural but Named with Semantic Connotations

The TLD computes:
1. `is_in_table` = atom center falls within a detected multi-column aligned structure bbox
2. `same_cell` = A and B have the same (row_idx, col_idx) within the detected structure
3. `different_cell` = A and B have different (row_idx, col_idx)

These are **purely structural operations** (point-in-rect, x-position clustering). The detection algorithm uses:
- y-alignment for row grouping
- x-gap ≥ 12pt for column detection
- ≥ 3 consecutive multi-column rows for table confirmation
- Column stability validation (≥ 70% alignment)

**No semantic interpretation occurs in TLD.** However, the FIELD NAMES ("table", "cell") carry semantic connotations that could create automation bias if shown directly to Human.

### Safe Translation Required

| Internal Field | Unsafe (leakage) | Safe Cue (L3) |
|---|---|---|
| is_in_table=True | "A and B are in a table" | "A and B are within a detected multi-column aligned structure" |
| different_cell=True | "A and B are in different cells" | "A and B are in different structural positions within the aligned structure" |
| same_cell=True | "A and B are in the same cell" | "A and B are in the same structural position" |
| different_local_partition=True | "A and B are in different partitions" | "A and B are assigned to different x-position groups" |

The safe translation preserves the structural fact while removing the semantic implication. Human still decides whether "different structural positions" means "should be separate."

---

## 3. Five Human Evidence Types — Detailed Analysis

### Type 1: Table Membership

| Question | Answer |
|---|---|
| Human cue | "表格中的内容" (table content) — mentioned 4 times |
| System has raw evidence? | **YES** — TLD: detect_tables_from_lines() → table bbox → point_in_rect |
| System layer | L2 Structural (multi-column aligned structure detection) |
| Can combine without semantic interpretation? | **YES** — table detection is purely structural |
| Missing layer | NONE — L2 exists, just not propagated to Human |
| Minimal safe cue | "A and B are within a detected multi-column aligned structure" |
| Unsafe version | "A and B are in a table" (implies semantic 'table') |
| Leakage risk | MEDIUM — "table" carries semantic connotation |
| Automation bias risk | MEDIUM — "in table" might imply "should be separate" |
| Traceability | FULL — TLD provenance with frozen params (min_rows=3, col_gap=12.0) |

### Type 2: Column Distinction

| Question | Answer |
|---|---|
| Human cue | "不同列" (different columns) — mentioned 3 times |
| System has raw evidence? | **YES** — TLD: (row_idx, col_idx) per atom → different_cell; SCE: different_local_partition |
| System layer | L2 Structural (x-position grouping) |
| Can combine without semantic interpretation? | **YES** — column assignment is positional |
| Missing layer | NONE — L2 exists |
| Minimal safe cue | "A and B are in different structural positions within the aligned structure" |
| Unsafe version | "A and B are in different cells" (implies "should be separate") |
| Leakage risk | **HIGH** — "different cell" directly implies separation |
| Automation bias risk | **HIGH** — Human might read as "system says separate" |
| Traceability | FULL — TLD + SCE provenance |

### Type 3: Sentence Boundary

| Question | Answer |
|---|---|
| Human cue | "前一句话后半+后一句话前半" — mentioned 2 times |
| System has raw evidence? | **PARTIALLY** — P1 has text content; punctuation is checkable but not currently computed |
| System layer | L1 Raw (text pattern) — "sentence boundary" itself is L3/L4 |
| Can combine without semantic interpretation? | **PARTIALLY** — can detect "A ends with period" (L1); cannot claim "A ends a sentence" (L4) |
| Missing layer | L3 — no distillation from "ends with period" to decision-relevant cue |
| Minimal safe cue | "Text A ends with a period. Text B starts with a capital letter." (L1 facts) |
| Unsafe version | "A ends a sentence and B starts a new one" (L4 discourse interpretation) |
| Leakage risk | LOW for L1 facts; HIGH for L3 interpretation |
| Traceability | PARTIAL — P1 has text; punctuation check not currently computed |

### Type 4: Caption Continuity

| Question | Answer |
|---|---|
| Human cue | "认可同一内容单元" (implicit for FIG. cases) — mentioned 2 times |
| System has raw evidence? | **PARTIALLY** — P1 has text; "FIG." prefix is matchable; line_obs_count available |
| System layer | L1 Raw (text pattern) + L2 Structural (item count) |
| Can combine without semantic interpretation? | **PARTIALLY** — can detect "starts with FIG." (L1); cannot claim "is a caption" (L4) |
| Missing layer | L3 — no distillation from "starts with FIG." + "2 items on line" to cue |
| Minimal safe cue | "Text A starts with 'FIG.' Only 2 items on this line." (L1+L2 facts) |
| Unsafe version | "A is a figure caption and B is its description" (L4 interpretation) |
| Leakage risk | MEDIUM — "FIG." is strong semantic signal |
| Traceability | PARTIAL — P1 has text; pattern match not computed; line_obs_count available |

### Type 5: Content Type Diversity

| Question | Answer |
|---|---|
| Human cue | "有的是数据有的是object对象" — mentioned 1 time |
| System has raw evidence? | **YES** — P1 text; is_numeric check is trivial |
| System layer | L1 Raw (text pattern) |
| Can combine without semantic interpretation? | **YES** — "is numeric" is a raw fact |
| Missing layer | L3 — no distillation from "numeric vs text" to cue |
| Minimal safe cue | "Text A is a number. Text B contains letters." (L1 facts) |
| Unsafe version | "A is a data value and B is a label" (L4 interpretation) |
| Leakage risk | LOW |
| Traceability | PARTIAL — P1 has text; is_numeric not currently computed |

### Summary

| Type | System Has Raw? | Can Construct Without Semantic? | Missing Layer | Status |
|---|---|---|---|---|
| Table membership | YES | YES | NONE (not propagated) | DISTILLATION_GAP |
| Column distinction | YES | YES (with safe translation) | NONE (not propagated) | DISTILLATION_GAP |
| Sentence boundary | PARTIALLY | PARTIALLY | L3 (punctuation not computed) | DISTILLATION_GAP + minor OBSERVATION_GAP |
| Caption continuity | PARTIALLY | PARTIALLY | L3 (pattern not computed) | DISTILLATION_GAP + minor OBSERVATION_GAP |
| Content type diversity | YES | YES | L3 (is_numeric not computed) | DISTILLATION_GAP |

---

## 4. TLD Field Audit

### is_in_table

| Aspect | Finding |
|---|---|
| Semantic source | detect_tables_from_lines() — purely structural (y-alignment + x-gap + column stability) |
| Frozen provenance | YES — TLD is frozen (hash 022f5c21e872ad9e), params frozen (min_rows=3, col_gap=12.0) |
| Layer | L2 Structural |
| If shown directly | MEDIUM automation bias risk — "in table" implies "should be separate" |
| Safe downgrade | "within a detected multi-column aligned structure" — removes "table" connotation |
| Traceability after downgrade | FULL — can trace back to detect_tables_from_lines() + point_in_rect |

### different_cell

| Aspect | Finding |
|---|---|
| Semantic source | (row_idx, col_idx) comparison after row/column grouping — purely positional |
| Frozen provenance | YES — computed by IS-11 harness using frozen TLD |
| Layer | L2 Structural |
| If shown directly | **HIGH** automation bias risk — "different cell" implies "should be separate" |
| Safe downgrade | "in different structural positions" — removes "cell" connotation |
| Traceability after downgrade | FULL — can trace back to (row_idx, col_idx) assignment |

### same_cell

| Aspect | Finding |
|---|---|
| Semantic source | Same as different_cell but equality check |
| Frozen provenance | YES |
| Layer | L2 Structural |
| If shown directly | **HIGH** automation bias risk — "same cell" implies "should merge" |
| Safe downgrade | "in the same structural position" |
| Traceability | FULL |

### Critical Observation: is_in_table=False Does NOT Determine Judgment

| Case | is_in_table | GT | Content |
|---|---|---|---|
| AMB-313 | False | KEEP_SEPARATE | Column header |
| AMB-414 | False | MERGE | Caption |
| AMB-519 | False | KEEP_SEPARATE | Prose boundary |

**This is GOOD**: TLD's `is_in_table` alone does not dictate the judgment. Human still needs text content + visual context to decide. The cue provides structural context but does NOT make the decision.

This means: showing the distilled cue ("within multi-column aligned structure: NO") would NOT automatically lead Human to the correct answer. Human must still interpret what "not in a structure" means for this specific case (caption? prose? header?).

---

## 5. Why h_gap=27.2pt Produces No Human Feedback

### Evidence Relevance Research Question

A correct geometric fact exists and is shown, but Human never referenced it. Why?

**Five reasons**:

1. **Information Form Mismatch**: h_gap is a NUMERIC VALUE; Human judgment operates on CATEGORICAL/RELATIONAL concepts. The numeric value requires an additional cognitive step that is not natural for semantic judgment.

2. **Decision Relevance Gap**: The number is correct but not decision-relevant. Human needs the RELATIONSHIP ("different columns"), not the distance.

3. **Comparison Without Reference**: 27.2pt means nothing without context. Human has no reference frame for point distances.

4. **Redundancy with Visual Evidence**: The page image already shows the spatial relationship. h_gap is a redundant encoding in a less useful form.

5. **Cognitive Cost of Irrelevant Information**: Human must process the number, determine it's not useful, then ignore it. With 12 such fields, this accumulates.

**Classification**: This is a RELEVANCE_GAP — the information is present, understandable, but not useful for the decision. NOT an Observation Gap (the measurement is correct) and NOT a Presentation Gap (the number is clearly displayed).

---

## 6. Information Abundance as Cognitive Load

### Current State

- 15 fields shown per case
- ~3 fields actually used by Human (text, page image, line context)
- 12 fields never referenced in any feedback

### Analysis

Information Abundance is NOT simply "too many fields." The core issue is:

> **Human must first SELECT which fields to attend to before they can use any field.**

This selection is itself cognitive work. With 15 fields:
- Human must evaluate each field's relevance (15 decisions)
- Then attend to the relevant ones (~3)
- Then ignore the rest (~12)

If the 12 unused fields were replaced with 3 high-value distilled cues:
- Total information: 6 fields (down from 15)
- All fields decision-relevant
- Selection cost: near zero
- Decision utility: higher

**Verdict**: Information Abundance is a RELEVANCE problem. The issue is not "too much information" but "wrong information shown, right information missing." Reducing quantity without improving relevance would not solve the problem.

**BUT**: This cannot be confirmed as a general principle from n=1. P01 achieved 3.9s/item, suggesting fast selection. Other participants might struggle more.

---

## 7. B/C Phase Analysis

### B-Phase: Structural Group ≠ Semantic Group

**Finding**: grp|16bfcb76b820 contains 6 cases with `sce_status=region_not_formed` but 3 different semantic categories.

**System grouping**: Correct at structural level — all 6 lack structural region.

**What grouping misses**: TLD data varies within the group:
- Sub-group 1 (is_in_table=True, different_cell=True): AMB-005, AMB-530 → table content
- Sub-group 2 (is_in_table=False, 2 items on line): AMB-414, AMB-422 → caption
- Sub-group 3 (is_in_table=False, 3+ items): AMB-313, AMB-519 → headers/prose

**Minimum Human-facing exposure**: Show per-case TLD status within the group — "2 within multi-column structure, 2 not (isolated pair), 2 not (multi-item line)". This is structural, safe, and reveals heterogeneity.

**Attribution**: NOT Aggregation error (grouping is structurally correct). IS Distillation Gap (TLD data not propagated to group representation).

### C-Phase: "6 instances: undetermined"

**Technical correctness**: ✅ The group IS heterogeneous, so "undetermined" is accurate.

**Human utility**: ❌ Low — Human needs to know WHAT is undetermined and WHY.

**Attribution analysis**:
- A. Compression Loss? — NO. No information lost; "undetermined" is correct.
- B. Relevance Loss? — PARTIALLY. Label is relevant but not actionable.
- C. Missing Heterogeneity Exposure? — YES. Group has 3 sub-categories not exposed.
- D. Semantic Interpretation Gap? — NO. System doesn't attempt interpretation.
- E. Mixed? — YES: B + C.

**Root cause**: Compression receives group-level structural signature, NOT per-case TLD data. TLD data exists at L2 but is not propagated through the pipeline to L4 Compression.

**Attribution**: Distillation Gap (pipeline propagation), NOT Compression contract violation (Compression operates correctly on its input).

---

## 8. Distillation Boundary Definition

### Boundary Hierarchy

| Boundary | Description | Contains Judgment? | Automation Bias Risk |
|---|---|---|---|
| 0 | Raw Evidence (text, bbox, font) | NO | NONE |
| 1 | Structural Evidence (h_gap, same_y, TLD detection) | NO | NONE |
| **2** | **Decision-Relevant Evidence Cue (safe translation)** | **NO** | **LOW** |
| 3 | Semantic Interpretation Candidate ("appears to be caption") | YES (candidate) | HIGH |
| 4 | Human Judgment (KEEP_SEPARATE / MERGE) | YES (final) | FORBIDDEN |

### DICE Current State

- **Internal processing**: Boundary 3 (EIC-1 produces semantic candidates)
- **C-phase Compression**: Boundary 3 (claim candidates)
- **Pilot UI**: Boundary 1 (subset of L2 structural facts)
- **Gap**: Boundary 1 → Boundary 2 distillation is missing

### Proposed Safe Boundary: Boundary 2

**Rationale**:
- Boundary 0: too much cognitive load
- Boundary 1: correct but not actionable ("h_gap=27.2pt" is correct but useless)
- **Boundary 2**: actionable but not judgmental ("different structural positions" helps without dictating)
- Boundary 3: risks automation bias ("appears to be caption" steers Human)
- Boundary 4: forbidden (Human's job)

### Is "Evidence Cue" a Stable Intermediate Layer?

**Evidence for YES**:
- Human feedback shows consistent use of cue-level concepts
- These concepts are derivable from L2 without L4 interpretation
- Translation is deterministic and traceable
- Cue does not contain judgment

**Evidence for UNCERTAIN**:
- Boundary between "cue" and "interpretation" is not always clear
- "A starts with FIG." is L1; "A is a caption prefix" is L3/L4 — where does one become the other?
- n=1 — cannot verify boundary stability across participants
- System≠GT=0 — cannot test automation bias risk of cues

**Verdict**: Evidence Cue is a **potentially stable** intermediate layer. It is more than a presentation trick (requires structural analysis + safe translation) but less than a new architecture (uses existing L2 evidence). Its boundary stability is **NOT YET VERIFIED** and requires multi-participant testing.

**This audit does NOT propose implementing Evidence Cue as a new layer. It only identifies that the conceptual boundary exists.**

---

## 9. Evidence Cue Mapping Table (Representative Cases)

| Case | Human Decision | Human-Explicit Evidence | Human-Observed Cue | Current System Evidence | Potential Distilled Cue | Cue Source | Cue Type | Leakage Risk | Human Utility | Traceability | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AMB-034 | KEEP_SEPARATE | (B-phase: "表格数据") | Two numbers in table row | text, image, gap=27.2pt, same_style | "Within multi-column structure; different structural positions" | TLD | STRUCTURAL_FACT | MEDIUM (if "table" used) / LOW (if "structure" used) | HIGH | FULL | IDENTIFIABLE |
| AMB-414 | MERGE | (B-phase: "认可同一内容单元") | "FIG." prefix; only 2 items | text, image, gap=18.1pt, same_style | "Not within multi-column structure; 2 items on line; A starts with 'FIG.'" | TLD + P1 text + line_obs | STRUCTURAL_FACT + CONTEXTUAL_EVIDENCE | LOW | HIGH | PARTIAL | IDENTIFIABLE |
| AMB-005 | KEEP_SEPARATE | "前一句话后半+后一句话前半" | A ends with period; B starts capital | text, image, gap=10pt, same_style | "A ends with period; B starts with capital letter; within multi-column structure" | P1 text pattern + TLD | CONTEXTUAL_EVIDENCE + STRUCTURAL_FACT | LOW | HIGH | PARTIAL | IDENTIFIABLE (requires punctuation check) |
| AMB-530 | KEEP_SEPARATE | "同一张表格的不同列的名称" | Column headers; 6+ items in row | text, image, gap=12.3pt, same_style | "Within multi-column structure; different structural positions; 8 items on line" | TLD + line_obs | STRUCTURAL_FACT | MEDIUM / LOW | HIGH | FULL | IDENTIFIABLE |
| AMB-313 | KEEP_SEPARATE | "表格中不同列的名称" | Column headers | text, image, gap=8.4pt, same_style | "Not within multi-column structure; 5 items on line; A='Test Size', B='#Classes'" | TLD + P1 text + line_obs | STRUCTURAL_FACT + CONTEXTUAL_EVIDENCE | LOW | MEDIUM | FULL | IDENTIFIABLE |
| AMB-519 | KEEP_SEPARATE | "一句话后半+下一句前半" | A ends with period; only 2 items | text, image, gap=8.6pt | "Not within multi-column structure; 2 items on line; A ends with period" | TLD + P1 text + line_obs | NEGATIVE_EVIDENCE (not in structure) + CONTEXTUAL_EVIDENCE | LOW | HIGH | PARTIAL | IDENTIFIABLE |

### Cue Type Distribution

| Cue Type | Count | Description |
|---|---|---|
| STRUCTURAL_FACT | 21/21 | TLD/SCE structural position facts |
| CONTEXTUAL_EVIDENCE | 21/21 | Text content, neighbor text, punctuation |
| RELATIONAL_EVIDENCE | 15/21 | "different structural positions" (requires both A and B positions) |
| NEGATIVE_EVIDENCE | 6/21 | "NOT within multi-column structure" (absence of structure) |
| HETEROGENEITY_EVIDENCE | 1 group (B/C) | Group contains mixed structural contexts |
| UNKNOWN_EVIDENCE | 0/21 | No case lacks identifiable cues |
| POTENTIAL_SEMANTIC_INTERPRETATION | 0/21 | No cue requires semantic interpretation to construct |

---

## 10. Final Single Conclusion

### B. DISTILLATION GAP IS REAL AND MINIMAL CUE IS IDENTIFIABLE

### PRIMARY_GAP: DISTILLATION_GAP

The System already possesses the L2 structural evidence (TLD: is_in_table, different_cell; SCE: different_local_partition; P1: text content) needed to construct Decision-Relevant Evidence Cues. These cues can be constructed via safe translation (Boundary 2) without crossing into semantic interpretation (Boundary 3).

The gap is: L2 evidence exists → L3 cue not constructed → Human receives only L1/L2 subset (h_gap, same_style) that is correct but low-utility.

### SECONDARY_GAP: RELEVANCE_GAP

The UI presents 12 low-value fields (h_gap numeric, same_style, width, style_sig) that Human never referenced. These are correct but not decision-relevant. Information abundance creates selection cost.

### EVIDENCE

1. All 21 cases have TLD evidence (is_in_table, different_cell) that was not propagated to Human
2. Human's 4 voice feedbacks consistently reference cue-level concepts ("table", "column", "caption", "sentence") — all derivable from L2 without L4 interpretation
3. Safe translations exist for all high-leakage fields (different_cell → "different structural positions")
4. TLD alone does NOT determine judgment (is_in_table=False for both MERGE and KEEP_SEPARATE cases) — cue doesn't dictate answer
5. MERGE vs KEEP_SEPARATE distinguishing signal (is_in_table + item count + text pattern) is fully derivable from existing evidence

### COUNTEREVIDENCE

1. Human achieved 21/21 = 100% accuracy WITHOUT distilled cues — page images compensated
2. Average judgment time 3.9s — fast selection suggests current evidence was sufficient for P01
3. n=1 — cannot verify cue boundary stability across participants
4. MERGE=2 — both captions; cannot verify cue generalizes to other MERGE types
5. System≠GT=0, conflict=0 — cannot test automation bias risk of cues
6. is_in_table=False appears in both MERGE and KEEP_SEPARATE — TLD alone insufficient (but this is a feature, not a bug: it means the cue doesn't dictate the judgment)
7. 3 of 5 Human Evidence types (sentence boundary, caption, content type) require L1 pattern computation not currently performed — minor OBSERVATION_GAP for these

### CONFIDENCE

**MEDIUM** (for DISTILLATION_GAP as primary)

- 21/21 cases show distillation gap — systematic
- Safe translations are identifiable for all high-risk fields
- TLD provenance is frozen and traceable
- BUT: n=1, cannot verify cue utility or automation bias risk empirically
- BUT: 3/5 types require minor computation not yet done (punctuation, FIG. pattern, is_numeric)

**MEDIUM-LOW** (for Evidence Cue as stable boundary)

- Conceptual boundary is identifiable
- Safe translations exist
- BUT: boundary between "cue" and "interpretation" is not always sharp
- BUT: no empirical verification of boundary stability
- BUT: cannot test with System≠GT cases (automation bias risk unknown)

---

## 11. What This Audit Does NOT Claim

- Does NOT claim Evidence Cue should be implemented (that requires separate authorization)
- Does NOT claim Evidence Cue would improve accuracy (accuracy was already 100%)
- Does NOT claim Evidence Cue would reduce cognitive load (n=1, not verified)
- Does NOT claim TLD fields are safe to show directly (they require safe translation)
- Does NOT propose a new Primitive, Contract, or Architecture
- Does NOT propose L5.9
- Does NOT claim the current UI is broken (it achieved 100% accuracy)
- Does NOT claim LLM understanding is insufficient (no evidence for or against)

---

## 12. Minimal Direction (Observational, NOT Prescriptive)

If future work is authorized to address this gap, the observable direction would be:

1. **Propagate TLD structural facts** (is_in_table, different_cell) from L2 to the Human-facing layer
2. **Apply safe translation**: "table" → "multi-column aligned structure"; "cell" → "structural position"
3. **Compute trivial L1 patterns**: ends_with_period, starts_with_FIG, is_numeric
4. **Remove or de-emphasize low-value fields**: h_gap numeric, style_sig, width
5. **Expose group heterogeneity in B/C**: show per-case TLD status within structural groups

But this is **observational only**. No implementation is proposed. The boundary stability requires multi-participant verification with System≠GT test cases.

---

## 13. Answer to the Core Question

> "System 当前是否已经可以在不产生 Semantic Judgment 的情况下，把已有 Evidence 提炼成 Human 真正需要的最小 Evidence Cue？"

**YES, for 2 of 5 types (table membership, column distinction)** — L2 structural evidence exists and safe translations are identifiable. No new computation needed.

**PARTIALLY, for 3 of 5 types (sentence boundary, caption, content type)** — L1 raw data exists but trivial pattern computations (punctuation check, FIG. prefix match, is_numeric) are not currently performed. These are minor OBSERVATION_GAPs (the data exists, the computation is trivial, but it's not done).

> "如果可以，最小安全边界在哪里？"

**Boundary 2: Decision-Relevant Evidence Cue**

The System can safely translate L2 structural facts into Human-actionable language (e.g., "different structural positions" instead of "different cells") without crossing into semantic interpretation. The cue provides context for Human judgment without dictating the answer.

**BUT**: This boundary's stability is NOT YET VERIFIED. It requires:
- Multi-participant testing (n > 1)
- System≠GT test cases (to test automation bias)
- Conflict cases (to test cue behavior under contradictory evidence)

Until these are available, Boundary 2 remains a **hypothesis**, not a verified result.

---

## 14. Governance

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
is_in_table=False does NOT independently determine KEEP/MERGE
```

### Evidence Classification

- This audit = **B-class** (engineering analysis based on single pilot)
- Evidence Cue identifiability = **B-class** (derived from analysis, not independently verified)
- Boundary 2 stability = **C-class** (unverified hypothesis — requires multi-participant testing)
- TLD safe translations = **B-class** (provenance is frozen/traceable, but utility not empirically tested)
