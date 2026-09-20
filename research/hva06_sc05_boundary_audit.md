# HVA-06: SC-05 Boundary & Evidence Sufficiency Audit

**Date**: 2026-09-17
**Mode**: READ-ONLY AUDIT
**Scope**: SC-05 / VS-05 TP/FP Boundary Analysis
**Predecessor**: HVA Phase 2 (REUSE_DEMONSTRATED_BUT_INSUFFICIENT)

---

## 1. Research Questions

```
RQ1: Human 为什么能够区分 SC-05 的 TP 与 FP？
RQ2: Human 用于区分 TP / FP 的 Evidence，是否已经存在于当前 DICE Evidence 层？
RQ3: 如果 Evidence 已存在，问题是 Evidence Missing / Organization Gap / Signal Boundary Gap？
RQ4: SC-05 是否应该继续作为 Reusable Signal？
```

---

## 2. TP/FP Case Analysis

### 2.1 IS-11 Source Cases (3, all body text sentence boundaries)

| Case | text_a | text_b | Context | Adjudication |
|---|---|---|---|---|
| IS11-AMB-375 | "[23]." | "Each" | Body text, citation ends sentence | "sentence-ending punctuation + capital = separate sentences" |
| IS11-AMB-418 | "...left panel." | "The" | Figure caption, sentence ends | "sentence-ending punctuation + capital = separate sentences" |
| IS11-AMB-519 | "...open-source LLMs." | "To embrace" | Body text, sentence ends | "sentence-ending punctuation + capital = separate sentences" |

**Critical Finding**: All 3 IS-11 source cases are body text / figure caption sentence boundaries. None are in reference lists. The signal was validated on a BODY_TEXT-biased sample.

### 2.2 P7 TP Cases (8 — KEEP_SEPARATE, correct prediction)

#### TP-1: IND-AMB-005 (BODY_TEXT_CONTINUATION)
```
text_a: "distribution."
text_b: "For the out-of-domain case, where the test"
Context: Abstract, body text. "distribution." ends sentence about data distribution.
         "For the out-of-domain case" starts new sentence about test scenario.
Human evidence: text_a is complete sentence ending, text_b is grammatically new sentence.
```

#### TP-2: IND-AMB-008 (BODY_TEXT_CONTINUATION)
```
text_a: "in improving out-of-distribution generalization."
text_b: "Our ap-"
Context: Body text about domain generalization methods.
         Full sentence ends, "Our ap-" (hyphenated) starts new sentence about their approach.
Human evidence: text_a is full sentence (48 chars, 4 words), text_b starts new sentence.
```

#### TP-3: IND-AMB-134 (REFERENCE_LIST_ENTRY, but actually body text)
```
text_a: ")."
text_b: "Profiles"
Context: Body text with equations. ")." ends equation citation (R²).
         "Profiles" starts new paragraph about genomic profiles.
Human evidence: ")." ends a mathematical expression, "Profiles" starts new section.
         Boundary_class=REFERENCE_LIST_ENTRY is MISLABELED — context is body text.
```

### 2.3 P7 FP Cases (5 — MERGE, wrong prediction)

#### FP-1: IND-AMB-003 (REFERENCE_LIST_ENTRY)
```
text_a: "."
text_b: "Philadelphia, PA: Society for"
Context: Page 30, reference list. [12]-[16] visible in page_context.
         "." ends previous reference element, "Philadelphia, PA:" is publisher location
         continuing the SAME reference entry.
Human evidence: Recognizes reference list structure (page_context shows [N] markers,
         vol., pp., [Online] patterns). "Philadelphia, PA:" is publisher location,
         not a new sentence.
```

#### FP-2: IND-AMB-002 (REFERENCE_LIST_ENTRY)
```
text_a: "."
text_b: "Springer Berlin Heidelberg,"
Context: Same page as FP-1 (page 30). Reference list.
         "." ends title element, "Springer Berlin Heidelberg," is publisher name
         continuing the SAME reference entry.
Human evidence: Recognizes reference list structure. "Springer Berlin Heidelberg,"
         is publisher name, not a new sentence.
```

#### FP-3: IND-AMB-052 (BODY_TEXT_CONTINUATION, but actually reference list)
```
text_a: "Guo, Jian Zhao, and Furao Shen."
text_b: "Image data aug-"
Context: Page 10. page_context shows reference list [24]-[30].
         "Guo, Jian Zhao, and Furao Shen." = author names.
         "Image data aug-" = paper title (hyphenated continuation).
         Boundary_class=BODY_TEXT_CONTINUATION is MISLABELED — context is reference list.
Human evidence: Recognizes "LastName, FirstName, and LastName" author name pattern.
         "Image data aug-" is paper title, not new sentence.
```

#### FP-4: IND-AMB-033 (OTHER_AMBIGUOUS)
```
text_a: "Le."
text_b: "Randaugment:"
Context: Page 9. page_context shows "References" header + [1]-[5] entries.
         "Le." = author last name (Vietnamese surname).
         "Randaugment:" = paper title.
Human evidence: "Le." is recognized as author name (short, capitalized, in reference list).
         "Randaugment:" is paper title. These are parts of the SAME reference entry.
```

#### FP-5: IND-AMB-049 (BODY_TEXT_CONTINUATION, but actually reference list)
```
text_a: "Levine."
text_b: "Bitrate-constrained dro:"
Context: Page 10. page_context shows reference list [24]-[30].
         "Levine." = author last name.
         "Bitrate-constrained dro:" = paper title.
         Boundary_class=BODY_TEXT_CONTINUATION is MISLABELED — context is reference list.
Human evidence: "Levine." is author name. "Bitrate-constrained" is paper title.
```

### 2.4 Cross-Case Pattern Summary

```
TP pattern: period ends a COMPLETE sentence/unit
            → text_b starts a genuinely NEW sentence/unit
            → Body text: sentence boundary
            → Reference list: entry boundary (between [N] markers)

FP pattern: period ends a PART of a reference entry
            → text_b CONTINUES the same reference entry
            → Author name → title (3/5 FP)
            → Title element → publisher info (2/5 FP)

DISTINGUISHING FACTOR:
  TP: text_a and text_b belong to DIFFERENT semantic units
  FP: text_a and text_b belong to the SAME semantic unit (reference entry)
```

### 2.5 Boundary Class Mislabeling Discovery

```
3 of 5 FP cases have MISLABELED boundary_class:
  IND-AMB-052: labeled BODY_TEXT_CONTINUATION, actual context = reference list
  IND-AMB-049: labeled BODY_TEXT_CONTINUATION, actual context = reference list
  IND-AMB-033: labeled OTHER_AMBIGUOUS, actual context = reference list

1 of 8 TP cases has MISLABELED boundary_class:
  IND-AMB-134: labeled REFERENCE_LIST_ENTRY, actual context = body text with equations

→ boundary_class is a HUMAN ANNOTATION, not machine-computed.
→ It has labeling errors.
→ It CANNOT be used as reliable machine evidence.
```

---

## 3. Evidence Dependency Matrix

| ID | Evidence | OBSERVED | INFERRED | NECESSARY | SUFFICIENT | Source |
|---|---|---|---|---|---|---|
| E1 | period (text_a_ends_period) | Yes (S3) | - | Yes | No | TYPE-A: machine_eval/GT |
| E2 | capital (text_b_starts_capital) | Yes (S3) | - | Yes | No | TYPE-A: machine_eval/GT |
| E3 | text_a / text_b content | Yes | - | Yes | No | TYPE-A: machine_eval/GT |
| E4 | sentence continuity | No | Partially (grammar) | Yes | No | TYPE-F: Semantic |
| E5 | reference-like structure | Partially (P7 page_context) | Yes (from page_context) | Yes | No | TYPE-B: P7 reviewer data |
| E6 | author-name continuation | No | Partially (regex) | Yes (3/5 FP) | No | TYPE-F: Semantic |
| E7 | bibliographic markers | Partially (in text) | Yes (regex on text) | Partially | No | TYPE-D: Composable |
| E8 | neighboring text | Partially (P7 page_context) | No | Yes | No | TYPE-B: P7 reviewer data |
| E9 | document/page context | Partially (doc_id, page) | No | Yes | No | TYPE-B: Partial |
| E10 | structural geometry | Yes (P7 geometry_provenance) | - | No | No | TYPE-B: P7 machine |
| E11 | content-type | No | No (64% ambiguous) | Yes | No | TYPE-E: Not available |
| E12 | IS-01/IS-02/TLD | Yes (S3) | - | Yes (baseline) | No | TYPE-A: machine_eval |

### Evidence Status Summary

```
TYPE-A (machine_eval exists):     E1, E2, E3, E12 → 4 items, all in S3, all NECESSARY but NOT SUFFICIENT
TYPE-B (P1-P7 exists):            E5, E8, E9, E10 → 4 items, exists in P7 but NOT in machine_eval
TYPE-C (TLD exists):              None relevant (all cases is_in_table=False)
TYPE-D (Composable from existing): E7 → 1 item, could be composed from text_a/text_b with regex
TYPE-E (Not in system):           E11 → 1 item, content_type not derivable (HVA-05)
TYPE-F (Semantic, not safe):      E4, E6 → 2 items, requires semantic knowledge

NECESSARY but NOT in Evidence Pack: E4, E5, E6, E8
NECESSARY and in Evidence Pack:    E1, E2, E3, E12
```

---

## 4. Human Decision Dependency

### 4.1 TP Cases — What Human Actually Uses

```
TP (KEEP_SEPARATE): Human determines text_a and text_b are DIFFERENT semantic units.

Evidence used:
  1. text_a ends with period (E1) — OBSERVED, TYPE-A
  2. text_b starts with capital (E2) — OBSERVED, TYPE-A
  3. text_a is a complete sentence/phrase (E3) — OBSERVED, TYPE-A
  4. text_b is grammatically a new sentence (E4) — NOT OBSERVED, TYPE-F
  5. Neighboring text shows body text context (E8) — NOT in machine_eval, TYPE-B

Example (IND-AMB-008):
  Human reads: "in improving out-of-distribution generalization." / "Our ap-"
  Human sees: text_a is full sentence (48 chars), text_b starts new sentence
  Human uses: E1 + E2 + E3 (length/content) + E4 (grammar) + E8 (body text context)
  → KEEP_SEPARATE
```

### 4.2 FP Cases — What Human Actually Uses

```
FP (MERGE): Human determines text_a and text_b are PARTS of the SAME reference entry.

Evidence used:
  1. text_a ends with period (E1) — OBSERVED, TYPE-A
  2. text_b starts with capital (E2) — OBSERVED, TYPE-A
  3. Neighboring text shows reference list (E5, E8) — NOT in machine_eval, TYPE-B
  4. text_a is author name or reference element (E6) — NOT OBSERVED, TYPE-F
  5. text_b is title/publisher/location (E6, E7) — Partially OBSERVED in text, TYPE-D/F
  6. Bibliographic markers in context (E7) — NOT extracted, TYPE-D

Example (IND-AMB-033):
  Human reads: "Le." / "Randaugment:"
  Human sees: page_context has "References" header + [1]-[5] entries
  Human recognizes: "Le." is author surname, "Randaugment:" is paper title
  Human uses: E5 (reference structure) + E6 (author-name recognition) + E8 (neighboring text)
  → MERGE (same reference entry)
```

### 4.3 The Critical Gap

```
S3 Signature provides: E1 + E2 + E3 + E12 (period, capital, text, IS-01/IS-02)
Human additionally needs: E4 + E5 + E6 + E8 (continuity, reference structure, author-name, neighboring text)

The S3 Signature captures the NECESSARY condition (period + capital)
but MISSES the DISCRIMINATING evidence (context + reference structure + author-name).
```

---

## 5. Evidence Source Classification

| Evidence | TYPE | Location | In Evidence Pack? | Composable? |
|---|---|---|---|---|
| E1 period | A | machine_eval/GT | Yes (S3) | - |
| E2 capital | A | machine_eval/GT | Yes (S3) | - |
| E3 text content | A | machine_eval/GT | Yes (L0) | - |
| E4 sentence continuity | F | Human semantic | No | No (requires grammar) |
| E5 reference structure | B/D | P7 page_context | No | Yes (from page_context with regex) |
| E6 author-name | F | Human semantic | No | Partially (regex catches some, not all) |
| E7 bibliographic markers | D | In text_a/text_b | No | Yes (regex on text) |
| E8 neighboring text | B | P7 page_context | No | No (needs page text extraction) |
| E9 doc/page context | B | machine_eval | Partial (doc_id, page) | No (section type missing) |
| E10 geometry | B | P7 geometry | No | No |
| E11 content-type | E | Not available | No | No (HVA-05: 64% ambiguous) |
| E12 IS-01/IS-02/TLD | A | machine_eval | Yes (S3) | - |

---

## 6. Primary Bottleneck

### PRIMARY: CASE-B (Evidence Organization Gap)

```
The most critical missing evidence is E8 (neighboring text / page_context).

page_context EXISTS in P7 reviewer data (all 13 cases have it, 1889-5569 chars each).
page_context does NOT exist in machine_eval.
page_context does NOT exist in Evidence Pack.

If page_context were available in Evidence Pack:
  → E5 (reference structure) could be composed with deterministic rules
    (check for [N] citation markers, "References" header, vol./pp./[Online] patterns)
  → E7 (bibliographic markers) could be composed with regex on text_a/text_b
    (check for "vol.", "pp.", "[Online]", "Available:", DOI patterns)
  → E8 (neighboring text) would be directly available

With these, ~3/5 FP could be caught:
  - IND-AMB-003: "Philadelphia, PA:" in reference list → publisher location (E5+E7)
  - IND-AMB-002: "Springer Berlin Heidelberg," in reference list → publisher name (E5+E7)
  - IND-AMB-052: "Guo, Jian Zhao, and Furao Shen." → author pattern (E6, partially regex)

This is NOT an Observation Gap (the data exists).
This is NOT a Semantic Boundary (deterministic rules can catch some FP).
This IS an Evidence Organization Gap (data exists but is not composed into Evidence Pack).
```

### SECONDARY: CASE-D (Semantic Boundary)

```
Even with page_context, 2/5 FP would remain hard to catch:

  - IND-AMB-033: "Le." / "Randaugment:"
    "Le." is a Vietnamese surname. Regex cannot reliably identify this as an author name.
    "Randaugment:" could be a title or a sentence. Requires semantic knowledge.
    → TYPE-F: Human uses world knowledge (name recognition)

  - IND-AMB-049: "Levine." / "Bitrate-constrained dro:"
    "Levine." could be author name or sentence subject. Ambiguous without context.
    "Bitrate-constrained" is a technical term, could be title or sentence.
    → TYPE-F: Human uses semantic understanding

These cases represent a genuine Semantic Boundary.
period + capital CANNOT distinguish author-name from sentence-subject
without semantic knowledge that is not safely structurable.

→ Accept this as a BOUNDARY, do not force Learning.
```

---

## 7. SC-05 Boundary Diagnosis

### 7.1 Signal Boundary Analysis

```
SC-05 (period + capital → KEEP_SEPARATE):

  NECESSARY condition: YES
    All KEEP_SEPARATE cases have period + capital.
    period + capital is a necessary structural precondition.

  SUFFICIENT condition: NO
    5/13 unseen cases with period + capital are MERGE.
    The pattern also matches reference continuation.

  BOUNDARY type: CONTEXT-DEPENDENT
    In body text: period + capital → KEEP_SEPARATE (high precision)
    In reference list: period + capital → AMBIGUOUS (could be entry boundary or within-entry)

  IS-11 bias: BODY_TEXT
    All 3 source cases are body text / figure caption.
    No reference list cases in source.
    → Signal was validated without seeing reference list counterexamples.
```

### 7.2 FP Root Cause

```
5 FP cases share ONE structural cause:

  period + capital is ambiguous between:
    (a) sentence boundary → KEEP_SEPARATE (Signal prediction)
    (b) within-reference continuation → MERGE (GT)

  The ambiguity is NOT random.
  It has a STRUCTURAL explanation:
    - Author name ends with period, title starts with capital → MERGE
    - Title element ends with period, publisher starts with capital → MERGE
    - Sentence ends with period, new sentence starts with capital → KEEP_SEPARATE

  The signal CANNOT distinguish (a) from (b) because S3 Signature
  does not include context evidence (E5, E8).
```

### 7.3 IS-11 Source Bias

```
IS-11 source cases (3):
  IS11-AMB-375: body text (medical paper, page 6)
  IS11-AMB-418: figure caption (medical paper, page 20)
  IS11-AMB-519: body text (CS paper, page 3)

All 3 are sentence boundaries in continuous text flow.
None are in reference lists.
None involve author-name → title transitions.

→ The adjudicator's validation was correct FOR THE SAMPLE,
   but the sample was biased toward body text.
→ The signal was not tested against reference list continuation patterns.
→ This is a SAMPLING BIAS, not a Signal error.
```

---

## 8. Evidence Sufficiency

### 8.1 Can Existing Evidence Stably Distinguish TP from FP?

```
Body text vs reference list:
  AVAILABLE: YES (if page_context is included)
  METHOD: Check page_context for [N] markers, "References" header, vol./pp. patterns
  RELIABILITY: HIGH (deterministic, no semantic knowledge needed)
  STATUS: EVIDENCE_NOT_COMPOSED (page_context exists in P7 but not in Evidence Pack)

Within reference list (entry boundary vs within-entry continuation):
  AVAILABLE: PARTIALLY
  METHOD: Check for [N] citation marker at start of text_b line → entry boundary
          Check for author-name pattern in text_a → within-entry continuation
  RELIABILITY: MEDIUM
    - [N] marker detection: HIGH (deterministic regex)
    - Author-name detection: LOW (regex catches "LastName, FirstName" but not "Le.")
  STATUS: MIXED
    - [N] detection: EVIDENCE_NOT_COMPOSED (deterministic, could be done)
    - Author-name detection: SEMANTIC_BOUNDARY (requires world knowledge)

Sentence continuity (body text):
  AVAILABLE: NO
  METHOD: Grammar analysis, semantic understanding
  RELIABILITY: N/A
  STATUS: SEMANTIC_BOUNDARY (TYPE-F)
```

### 8.2 BOUNDARY_EVIDENCE_AVAILABLE

```
BOUNDARY_EVIDENCE_AVAILABLE = PARTIALLY TRUE

  Body text vs reference list distinction:
    AVAILABLE = TRUE (via page_context, TYPE-B → TYPE-D composable)
    But NOT currently in Evidence Pack → EVIDENCE_NOT_COMPOSED

  Within-reference distinction (author-name vs sentence):
    AVAILABLE = PARTIALLY
    [N] marker detection: AVAILABLE (TYPE-D)
    Author-name recognition: NOT AVAILABLE (TYPE-F, semantic)

  Overall:
    If page_context is added to Evidence Pack:
      ~3/5 FP catchable with deterministic rules
      ~2/5 FP remain as Semantic Boundary
    → BOUNDARY_EVIDENCE_AVAILABLE = PARTIALLY TRUE
```

---

## 9. Observation Gap Assessment

### 9.1 NEW_OBSERVATION_MEASUREMENT_REQUEST?

```
Do we need a new Observation Layer?

  E8 (neighboring text / page_context):
    EXISTS in P1 text extraction pipeline (page text is extracted)
    EXISTS in P7 reviewer data (page_context field)
    NOT in machine_eval (not passed through)
    → NOT a new observation. This is Evidence Organization.

  E5 (reference structure detection):
    Could be composed from page_context with deterministic rules
    → NOT a new observation. This is Evidence Composition (TYPE-D).

  E7 (bibliographic marker detection):
    Could be composed from text_a/text_b with regex
    → NOT a new observation. This is Evidence Composition (TYPE-D).

  E6 (author-name recognition):
    Requires semantic knowledge (world knowledge about names)
    → This WOULD need a new observation/detector, BUT:
      - It's TYPE-F (semantic), not safely structurable
      - Do NOT propose a new detector for this
      - Accept as Semantic Boundary

CONCLUSION:
  NEW_OBSERVATION_MEASUREMENT_REQUEST = NOT REQUIRED

  The evidence EXISTS but is NOT ORGANIZED.
  This is an Evidence Organization Gap (CASE-B), not an Observation Gap (CASE-C).

  No new Observation, Detector, or Engine should be proposed.
```

### 9.2 Minimum Evidence Measurement Request (if authorized in future)

```
IF authorized:
  Request: page_context (neighboring text) in Evidence Pack
  Method: Extract from P1 text extraction output (already exists in pipeline)
  Scope: L2 Evidence Pack level (L0-L1 unchanged)
  Determinism: Fully deterministic (text extraction is frozen)
  Risk: LOW (no semantic judgment, no new module)

  This is NOT a new Observation.
  This is Evidence Organization (composing existing pipeline output into Evidence Pack).

  NOT requested in this audit. Only documented.
```

---

## 10. Reference / Author-Name Continuation Special Check

### 10.1 What Evidence Describes Reference Structure?

```
For 5 FP cases, check if current system can describe:

  Author names:       NOT AVAILABLE (no module detects author-name patterns)
  Titles:             NOT AVAILABLE (no module detects paper titles)
  Publication info:   NOT AVAILABLE (no module detects publisher/location)
  Page numbers:       NOT AVAILABLE (in reference, not in Evidence)
  DOI:                NOT AVAILABLE (in text, but not extracted as evidence)
  Citation marker:    NOT AVAILABLE ([N] in text, but not extracted as evidence)
  Neighboring text:   AVAILABLE in P7 page_context, NOT in machine_eval
  Text continuity:    NOT AVAILABLE (no module analyzes text flow)
  Bibliography structure: NOT AVAILABLE (no module detects reference list structure)
```

### 10.2 Classification

```
For each missing evidence:

  Neighboring text (E8):
    EXISTS in P7 page_context → EVIDENCE_NOT_COMPOSED
    (exists but not organized into Evidence Pack)

  Bibliographic markers (E7: [N], vol., pp., [Online], DOI):
    EXISTS in text_a/text_b → EVIDENCE_NOT_COMPOSED
    (could be extracted with regex, but no module does this)

  Reference structure (E5):
    EXISTS in page_context → EVIDENCE_NOT_COMPOSED
    (could be detected from page_context with deterministic rules)

  Author-name recognition (E6):
    NOT EXISTS in any system → SEMANTIC_BOUNDARY
    (requires world knowledge, not safely structurable)

  Paper title recognition:
    NOT EXISTS in any system → SEMANTIC_BOUNDARY
    (requires understanding of reference format + title patterns)
```

---

## 11. Reusable Signal Status

### 11.1 SC-05 Classification

```
SC-05 status: BOUNDARY_ONLY

  The signal identifies a genuine boundary:
    period + capital is a NECESSARY condition for KEEP_SEPARATE.

  But the signal is NOT SUFFICIENT:
    38.5% FP on unseen cases.
    Cannot distinguish sentence boundary from reference continuation.

  The signal should NOT continue as a Reusable Signal (as-is).
  The signal should NOT be STOPPED entirely (the boundary is real).
  The signal should NOT be MODIFIED (forbidden by audit constraints).

  Status: BOUNDARY_ONLY
    → Records the boundary exists.
    → Records the FP cause (Evidence Organization Gap + Semantic Boundary).
    → Does NOT auto-narrow.
    → Does NOT auto-stop.
    → Future narrowing requires explicit authorization + new Evidence composition.
```

### 11.2 Do NOT Form "REFERENCE → MERGE" Rule

```
EXPLICITLY FORBIDDEN:
  The 5 FP cases show reference continuation → MERGE.
  This does NOT justify creating a rule "reference_list → MERGE".

  Reasons:
  1. boundary_class has labeling errors (3/5 FP mislabeled).
  2. Reference list also contains TP cases (entry boundaries → KEEP_SEPARATE).
  3. "reference_list → MERGE" would be a NEW RULE, not a Signal.
  4. The evidence for "is this a reference list?" is NOT in machine_eval.
  5. Human "knowing it's a reference" is semantic knowledge (TYPE-F).

  → Do NOT create REFERENCE → MERGE rule.
  → Record as Human Semantic Boundary.
```

---

## 12. Recommended Next Route

```
Route A (Evidence Organization — IF authorized):
  1. Add page_context to Evidence Pack L2
     (source: P1 text extraction output, already exists in pipeline)
  2. Compose reference structure detection from page_context
     (deterministic: check [N] markers, "References" header, vol./pp. patterns)
  3. Compose bibliographic marker extraction from text_a/text_b
     (deterministic: regex for vol., pp., [Online], DOI)
  4. Re-run SC-05 replay with enriched Evidence Pack
  5. Expected improvement: ~3/5 FP catchable, FP rate drops from 38.5% to ~15%
  6. BUT: 2/5 FP remain as Semantic Boundary (author-name recognition)

  Status: NOT authorized. Only documented.

Route B (Accept Semantic Boundary):
  1. Accept that period + capital has a context-dependent boundary
  2. Record SC-05 as BOUNDARY_ONLY
  3. Do NOT attempt to narrow further
  4. Focus on other candidates (SC-04) or new signal discovery
  5. Accept L4 as the learning level ceiling for this signal

  Status: RECOMMENDED (safe, honest, no overreach).

Route C (SC-04 investigation — IF authorized):
  1. SC-04 (table numeric diff cell) has no conflict in IS-11
  2. 7 P7 matches, all KEEP_SEPARATE
  3. May have different boundary characteristics
  4. But independence_ratio=0.6 (same-page clustering)

  Status: NOT authorized. Only documented.
```

---

## 13. Learning Level

```
LEARNING_LEVEL = L4_CANDIDATE_VALIDATION (UNCHANGED)

  This audit does NOT improve Learning Level.
  This audit only updates:
    - SIGNAL_BOUNDARY_STATUS: BOUNDARY_ONLY
    - EVIDENCE_SUFFICIENCY_STATUS: PARTIALLY_SUFFICIENT
    - REUSE_DIAGNOSIS: REUSE_DEMONSTRATED_BUT_CONTEXT_DEPENDENT

  L5 (Reliable Reuse) requires:
    - FP rate < 30% (currently 38.5%)
    - OR Evidence Organization improvement (not authorized)
    - OR accepting Semantic Boundary (Route B)

  Without authorization for Route A, L5 is NOT achievable for SC-05.
```

---

## 14. Governance Gate

```
AUDIT_STATUS = COMPLETE
SIGNAL_BOUNDARY_STATUS = BOUNDARY_ONLY
EVIDENCE_SUFFICIENCY_STATUS = PARTIALLY_SUFFICIENT
REUSE_DIAGNOSIS = REUSE_DEMONSTRATED_BUT_CONTEXT_DEPENDENT
PRIMARY_BOTTLENECK = CASE_B_EVIDENCE_ORGANIZATION_GAP
SECONDARY_BOTTLENECK = CASE_D_SEMANTIC_BOUNDARY
BOUNDARY_EVIDENCE_AVAILABLE = PARTIALLY_TRUE
NEW_OBSERVATION_REQUIRED = NO

IMPLEMENTATION_AUTHORIZED = FALSE
EXPERIMENT_AUTHORIZED = FALSE
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
RUNTIME_CHANGE = NO
CAPABILITY_CHANGE = NO
RULE_CREATION = NO (no "REFERENCE → MERGE" rule)
THRESHOLD_ADJUSTMENT = NO (no FP threshold fitting)

FROZEN_BASELINE = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d)
PRODUCTION = FALSE
STOP = TRUE
```

---

## 15. 8-Sentence Final Answer

1. **Human 区分 TP/FP 的核心证据是上下文**——Human 通过 neighboring text（page_context）判断当前是在 body text 还是 reference list，S3 Signature 只包含 period + capital 但不包含上下文。

2. **IS-11 source cases 存在 BODY_TEXT bias**——3 个 source cases 全部是 body text / figure caption 的句子边界，没有 reference list 续行 case，导致 Signal 在 biased sample 上验证通过。

3. **5 个 FP 的根因是 within-reference continuation**——author name → title（3/5）和 title element → publisher info（2/5），period + capital 在参考文献条目内续行中同样出现。

4. **Primary Bottleneck = CASE-B (Evidence Organization Gap)**——page_context（neighboring text）在 P7 reviewer data 中存在但在 machine_eval 和 Evidence Pack 中不存在，这是 Evidence Organization 问题不是 Observation Gap。

5. **Secondary Bottleneck = CASE-D (Semantic Boundary)**——即使有 page_context，author-name recognition（"Le." 是姓氏还是句子片段）仍需要语义知识，无法安全结构化。

6. **BOUNDARY_EVIDENCE_AVAILABLE = PARTIALLY TRUE**——body text vs reference list 的区分可用 page_context + 确定性规则实现（~3/5 FP 可捕获），但 within-reference 的 author-name 识别是 Semantic Boundary（~2/5 FP 不可捕获）。

7. **SC-05 status = BOUNDARY_ONLY**——period + capital 是 KEEP_SEPARATE 的必要条件但非充分条件，Signal 不应作为 Reusable Signal 继续使用，但 boundary 是真实的，不应 STOP，不应 MODIFY。

8. **禁止创建 "REFERENCE → MERGE" 规则**——boundary_class 有标注错误（3/5 FP 被错误标注为 BODY_TEXT），reference list 中也有 TP case（entry boundary），Human "知道是参考文献" 是 semantic knowledge（TYPE-F），不能形成 Reusable Signal。

`STOP = TRUE`。
