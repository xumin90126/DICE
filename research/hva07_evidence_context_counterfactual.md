# HVA-07: Evidence Context Enrichment Counterfactual Audit

**Date**: 2026-09-17
**Mode**: READ-ONLY / AUDIT ONLY / NO IMPLEMENTATION
**Scope**: SC-05 FP/TP Counterfactual — Does existing page_context suffice if organized into Evidence Pack?

---

## 1. Executive Summary

```
HVA-07 STATUS = COMPLETE
EVIDENCE_CONTEXT_STATUS = PARTIALLY_SUPPORTED
PRIMARY_BOTTLENECK = EVIDENCE_ORGANIZATION_GAP (page_context exists, not composed)
SECONDARY_BOTTLENECK = SEMANTIC_BOUNDARY (author-name recognition, 2/5 FP)
NEW_OBSERVATION = NOT_REQUIRED
LLM_REQUIRED = NO
MINIMAL_ADAPTER_REQUIRED = NO (D1: better organization of existing data)
IMPLEMENTATION_AUTHORIZED = FALSE
FROZEN_BASELINE = INTACT
DICE_CORE_DRIFT = 0
STOP = TRUE
```

### Core Finding

page_context / neighboring context **已经存在于 P7 reviewer data 中**（13/13 cases, 1889-5569 chars）。如果将其组织进 Evidence Pack：

- **3/5 FP 可被 context 解释**（IND-AMB-003, 002, 052）—— reference list 结构 + bibliographic markers 足以区分
- **2/5 FP 仍需 Human semantic knowledge**（IND-AMB-033, 049）—— author-name recognition 超出确定性规则范围
- **3/3 TP 不受负面影响**—— context 确认 body text 判断，不产生新歧义

**这是 CASE B（Context 部分足够）。EVIDENCE_ORGANIZATION_GAP = SUPPORTED。**

---

## 2. Five FP Analysis

### FP-1: IND-AMB-003 (REFERENCE_LIST_ENTRY, GT=MERGE)

```
text_a: "."
text_b: "Philadelphia, PA: Society for"
Doc: ind_arxiv_2402, Page: 30
```

#### A — Current Evidence Pack

```
Human sees:
  L0: text_a=".", text_b="Philadelphia, PA: Society for", page=30, doc=ind_arxiv_2402
  L1: is01_a=False, is02_b=True, period=True, capital=True
  L1: machine_decision=INSUFFICIENT_EVIDENCE

Human CAN determine: period + capital → structural signal present
Human CANNOT determine: "." ends what? "Philadelphia, PA:" starts what?
  → "." could end a sentence, a citation, a title, an abbreviation
  → "Philadelphia, PA:" could start a new sentence, a publisher location, a section header
  → WITHOUT context: AMBIGUOUS
```

#### B — Context-Enriched (add page_context)

```
page_context shows: Reference list [12]-[31], each entry follows pattern:
  [N] Authors, "Title," Journal, vol. X, no. Y, Date. [Online]. Available: DOI

Specifically, [31] entry:
  "R. Glowinski, Variational Methods for the Numerical Solution of Nonlinear Elliptic Problems.
   Philadelphia, PA: Society for Industrial and Applied Mathematics, Nov 2015."

Human NOW sees:
  1. Page is a REFERENCE LIST (20+ entries with [N] markers)
  2. text_a "." ends the title "Nonlinear Elliptic Problems."
  3. text_b "Philadelphia, PA: Society for" is PUBLISHER LOCATION
  4. "Philadelphia, PA:" is a standard publisher location format
  5. This is WITHIN reference entry [31], not a sentence boundary

→ Human determines: MERGE (same reference entry continuation)
```

#### Classification: A_INSUFFICIENT_B_SUFFICIENT

```
page_context provides:
  - Reference list structure ([N] markers, 20+ entries) → SYSTEM-AVAILABLE
  - Entry pattern (Authors. Title. Publisher. Date.) → SYSTEM-AVAILABLE
  - "Philadelphia, PA:" as publisher location → recognizable from text pattern

Does Human need new semantic knowledge? MINIMAL
  - "Philadelphia, PA:" is a standard geographic format (not semantic inference)
  - Reference list structure is visible in raw text (no interpretation needed)

Does Human need new observation? NO
  - page_context already exists in P7 reviewer data

Does Human need LLM? NO
  - Deterministic text patterns suffice
```

---

### FP-2: IND-AMB-002 (REFERENCE_LIST_ENTRY, GT=MERGE)

```
text_a: "."
text_b: "Springer Berlin Heidelberg,"
Doc: ind_arxiv_2402, Page: 30 (same page as FP-1)
```

#### A — Current Evidence Pack

```
Same as FP-1: period + capital, but no context.
"." ends what? "Springer Berlin Heidelberg," starts what?
→ AMBIGUOUS
```

#### B — Context-Enriched

```
page_context shows same reference list. [30] entry:
  "C. Grossmann, H.-G. Roos, and M. Stynes, Numerical Treatment of Partial Differential Equations.
   Springer Berlin Heidelberg, Aug 2007."

Human NOW sees:
  1. Reference list (same as FP-1)
  2. text_a "." ends title "Partial Differential Equations."
  3. text_b "Springer Berlin Heidelberg," is PUBLISHER NAME
  4. "Springer" is a well-known academic publisher
  5. This is WITHIN reference entry [30]

→ Human determines: MERGE
```

#### Classification: A_INSUFFICIENT_B_SUFFICIENT

```
page_context provides:
  - Reference list structure → SYSTEM-AVAILABLE
  - "Springer Berlin Heidelberg," as publisher name → recognizable from text
    ("Springer" + city names is a standard publisher format)

Does Human need new semantic knowledge? MINIMAL
  - "Springer" as publisher is common knowledge but also inferable from pattern
    (Publisher + City format in reference list)

Does Human need new observation? NO
Does Human need LLM? NO
```

---

### FP-3: IND-AMB-052 (BODY_TEXT_CONTINUATION [MISLABELED], GT=MERGE)

```
text_a: "Guo, Jian Zhao, and Furao Shen."
text_b: "Image data aug-"
Doc: ind_arxiv_bio2, Page: 10
```

#### A — Current Evidence Pack

```
Human sees:
  text_a="Guo, Jian Zhao, and Furao Shen." (31 chars, 6 words)
  text_b="Image data aug-" (hyphenated, 14 chars)
  period=True, capital=True

Human CANNOT determine:
  - "Guo, Jian Zhao, and Furao Shen." → author names? sentence? list?
  - "Image data aug-" → paper title? sentence fragment? section header?
  - boundary_class=BODY_TEXT_CONTINUATION is MISLABELED (actual context = reference list)
→ AMBIGUOUS
```

#### B — Context-Enriched

```
page_context shows: Reference list [24]-[34], each entry follows pattern:
  [N] Author1, Author2, ... AuthorN. Title. Venue, pages, year.

Human NOW sees:
  1. Page is a REFERENCE LIST ([24]-[34] entries visible)
  2. text_a "Guo, Jian Zhao, and Furao Shen." matches AUTHOR NAME pattern
     (comma-separated capitalized names, "and" before last author)
  3. text_b "Image data aug-" is PAPER TITLE (hyphenated continuation)
  4. Pattern: "Authors. Title." within reference entry
  5. This is WITHIN a reference entry, not a sentence boundary

→ Human determines: MERGE
```

#### Classification: A_INSUFFICIENT_B_SUFFICIENT

```
page_context provides:
  - Reference list structure ([N] markers) → SYSTEM-AVAILABLE
  - Author-name pattern (comma-separated, "and" conjunction) → detectable from text
  - Title position (follows author names + period) → inferable from pattern

Does Human need new semantic knowledge? LOW
  - "Guo, Jian Zhao, and Furao Shen" is recognizable as author names from PATTERN
    (not from knowing these specific people)
  - The "LastName, FirstName, and LastName" pattern is a structural regularity

Does Human need new observation? NO
Does Human need LLM? NO
```

---

### FP-4: IND-AMB-033 (OTHER_AMBIGUOUS, GT=MERGE)

```
text_a: "Le."
text_b: "Randaugment:"
Doc: ind_arxiv_bio2, Page: 9
```

#### A — Current Evidence Pack

```
Human sees:
  text_a="Le." (3 chars, 1 word)
  text_b="Randaugment:" (13 chars, 1 word)
  period=True, capital=True

Human CANNOT determine:
  - "Le." → author surname? abbreviation? sentence fragment? French word?
  - "Randaugment:" → paper title? technical term? section header?
→ HIGHLY AMBIGUOUS
```

#### B — Context-Enriched

```
page_context shows:
  - "References" header visible
  - [1]-[8] entries visible, pattern: [N] Authors. Title. Venue. Year.
  - [8] entry: "Ekin D Cubuk, Barret Zoph, Dandelion Mane, Vijay Vasudevan, and Quoc V Le.
    Autoaugment: Learning augmentation strategies from data."

Human NOW sees:
  1. Page is a REFERENCE LIST ("References" header + [N] markers)
  2. text_a "Le." is in AUTHOR NAME position (after "and Quoc V")
  3. text_b "Randaugment:" is in TITLE position (follows author names + period)
  4. Pattern suggests within-entry continuation

BUT:
  5. "Le." is a 2-character token — could be:
     - Vietnamese surname (Human with Asian name knowledge)
     - French word ("le" = "the")
     - Abbreviation
  6. "Randaugment:" could be:
     - Paper title (if in reference list)
     - Technical term (if in body text)
  7. Context STRONGLY SUGGESTS reference list, but "Le." recognition
     as a surname requires SOME semantic/world knowledge

→ Human determines: MERGE (with higher confidence than A, but not fully deterministic)
```

#### Classification: A_INSUFFICIENT_B_PARTIAL

```
page_context provides:
  - Reference list structure ("References" header, [N] markers) → SYSTEM-AVAILABLE
  - Entry pattern → SYSTEM-AVAILABLE

BUT page_context CANNOT provide:
  - "Le." is a surname (not a word/abbreviation) → HUMAN SEMANTIC KNOWLEDGE
  - "Randaugment:" is a paper title → HUMAN SEMANTIC KNOWLEDGE
    (determinable from position in reference entry, but "Le." as name is the key)

Does Human need new semantic knowledge? YES (PARTIAL)
  - Reference list context is SYSTEM-AVAILABLE
  - But "Le." → surname recognition is HUMAN-ONLY SEMANTIC

Does Human need new observation? NO (the structural context exists)
Does Human need LLM? NO (but semantic recognition is needed)

THIS IS A GENUINE SEMANTIC BOUNDARY:
  The context REDUCES ambiguity (shows reference list) but does NOT ELIMINATE it
  ("Le." remains ambiguous without name recognition)
```

---

### FP-5: IND-AMB-049 (BODY_TEXT_CONTINUATION [MISLABELED], GT=MERGE)

```
text_a: "Levine."
text_b: "Bitrate-constrained dro:"
Doc: ind_arxiv_bio2, Page: 10 (same page as FP-3)
```

#### A — Current Evidence Pack

```
Human sees:
  text_a="Levine." (7 chars, 1 word)
  text_b="Bitrate-constrained dro:" (24 chars, hyphenated)
  period=True, capital=True

Human CANNOT determine:
  - "Levine." → author surname? sentence subject? person name?
  - "Bitrate-constrained dro:" → paper title? technical description?
→ AMBIGUOUS
```

#### B — Context-Enriched

```
page_context shows: Reference list [24]-[34] (same as FP-3)
  Pattern: [N] Authors. Title. Venue. Year.

Human NOW sees:
  1. Page is a REFERENCE LIST ([N] markers)
  2. "Levine." is in AUTHOR NAME position (single capitalized word + period)
  3. "Bitrate-constrained dro:" is in TITLE position
  4. Pattern: "Author. Title." within reference entry

BUT:
  5. "Levine." could be:
     - Surname (common, recognizable)
     - Sentence subject (if body text — but context shows reference list)
  6. "Bitrate-constrained dro:" could be:
     - Paper title (in reference list context)
     - Technical phrase (in body text — but context shows reference list)
  7. Context STRONGLY SUGGESTS reference list, "Levine." is more recognizable
     as a surname than "Le." (Levine is a common Western surname)

→ Human determines: MERGE (with higher confidence than A)
```

#### Classification: A_INSUFFICIENT_B_PARTIAL

```
page_context provides:
  - Reference list structure ([N] markers) → SYSTEM-AVAILABLE
  - Entry pattern → SYSTEM-AVAILABLE

page_context PARTIALLY provides:
  - "Levine." as surname → MORE RECOGNIZABLE than "Le." but still requires
    Human to recognize it as a name (not a common word)
  - "Bitrate-constrained" as title → inferable from position in reference entry

Does Human need new semantic knowledge? YES (MILD)
  - "Levine" is a recognizable surname to most literate Humans
  - But this is still semantic knowledge, not deterministic structure
  - The reference list context makes it HIGHLY LIKELY but not CERTAIN

Does Human need new observation? NO
Does Human need LLM? NO

THIS IS A MILD SEMANTIC BOUNDARY:
  Context + common name recognition → high confidence
  But not fully deterministic (unlike FP-003/002 where "Philadelphia, PA:" is unambiguous)
```

---

### FP Summary Table

| Case | text_a | text_b | A (Current) | B (Context-Enriched) | Context Source | Semantic Needed? |
|---|---|---|---|---|---|---|
| IND-AMB-003 | "." | "Philadelphia, PA:" | INSUFFICIENT | SUFFICIENT | page_context (ref list [12]-[31]) | MINIMAL |
| IND-AMB-002 | "." | "Springer Berlin Heidelberg," | INSUFFICIENT | SUFFICIENT | page_context (ref list [12]-[31]) | MINIMAL |
| IND-AMB-052 | "Guo, Jian Zhao, and Furao Shen." | "Image data aug-" | INSUFFICIENT | SUFFICIENT | page_context (ref list [24]-[34]) | LOW |
| IND-AMB-033 | "Le." | "Randaugment:" | INSUFFICIENT | PARTIAL | page_context (ref list [1]-[8]) | YES (name recognition) |
| IND-AMB-049 | "Levine." | "Bitrate-constrained dro:" | INSUFFICIENT | PARTIAL | page_context (ref list [24]-[34]) | MILD (name recognition) |

```
B_SUFFICIENT: 3/5 FP (003, 002, 052)
B_PARTIAL:    2/5 FP (033, 049)
B_STILL_INSUFFICIENT: 0/5 FP
A_SUFFICIENT: 0/5 FP
```

---

## 3. TP Safety Analysis

### TP-1: IND-AMB-008 (BODY_TEXT_CONTINUATION, GT=KEEP_SEPARATE)

```
text_a: "in improving out-of-distribution generalization."
text_b: "Our ap-"
```

#### A — Current Evidence Pack

```
Human sees:
  text_a (48 chars, 4 words — complete sentence ending)
  text_b "Our ap-" (hyphenated, starts new sentence)
  period=True, capital=True
  → Human determines: KEEP_SEPARATE (sentence boundary)
```

#### B — Context-Enriched

```
page_context shows: Body text paragraph about domain generalization methods.
  No [N] reference markers at sentence level (in-text citations [1], [26] exist but in body text)
  No "References" header
  Continuous prose about DANN, MMD, domain invariance

Human NOW sees:
  1. Body text context (not reference list)
  2. text_a is complete sentence about "out-of-distribution generalization"
  3. text_b "Our ap-" starts new sentence about their approach
  4. Context CONFIRMS: sentence boundary in body text

Does B add useful information? YES — confirms body text context
Does B create new ambiguity? NO — no reference markers, no conflicting structure
Does B increase cognitive load? MODERATE — 3045 chars of body text to read
Is B decision-relevant? YES — confirms not in reference list
```

#### TP Safety Assessment: SAFE

```
Context helps: CONFIRMS body text → sentence boundary → KEEP_SEPARATE
Context overwhelms: NO (body text is readable, no conflicting signals)
New ambiguity: NO
Over-reliance risk: LOW (context confirms existing judgment)
```

---

### TP-2: IND-AMB-005 (BODY_TEXT_CONTINUATION, GT=KEEP_SEPARATE)

```
text_a: "distribution."
text_b: "For the out-of-domain case, where the test"
```

#### A — Current Evidence Pack

```
Human sees:
  text_a="distribution." (13 chars, 1 word)
  text_b="For the out-of-domain case, where the test" (43 chars, 8 words)
  period=True, capital=True
  → Human determines: KEEP_SEPARATE (sentence boundary)
```

#### B — Context-Enriched

```
page_context shows: Paper Abstract section
  Title: "Domain Generalization by Rejecting Extreme Augmentations"
  Authors with email addresses
  "Abstract" header
  Body text about data augmentation

Human NOW sees:
  1. Abstract section (not reference list)
  2. text_a "distribution." ends sentence about data distribution
  3. text_b "For the out-of-domain case" starts new sentence
  4. Context CONFIRMS: sentence boundary in abstract

Does B add useful information? YES — confirms abstract/body text context
Does B create new ambiguity? NO
Does B increase cognitive load? MODERATE — 2495 chars
Is B decision-relevant? YES — confirms not in reference list
```

#### TP Safety Assessment: SAFE

```
Context helps: CONFIRMS abstract body text → sentence boundary → KEEP_SEPARATE
Context overwhelms: NO
New ambiguity: NO
Over-reliance risk: LOW
```

---

### TP-3: IND-AMB-134 (REFERENCE_LIST_ENTRY [MISLABELED], GT=KEEP_SEPARATE)

```
text_a: ")."
text_b: "Profiles"
```

#### A — Current Evidence Pack

```
Human sees:
  text_a=")." (2 chars)
  text_b="Profiles" (8 chars)
  period=True, capital=True
  boundary_class=REFERENCE_LIST_ENTRY (MISLABELED — actual context = body text with equations)

  → Without context: AMBIGUOUS (")." could end citation or equation)
  → Human might be misled by boundary_class label
```

#### B — Context-Enriched

```
page_context shows: Methods section body text with equations
  - R² formula
  - "coefficient of determination (R²)."
  - "Enhancer prediction" section
  - "Hi-C, ChIP-seq, ATAC-seq" data processing
  - URLs and data accession numbers (GSE228095, etc.)
  - "Profiles of the genomic data were plotted..."

Human NOW sees:
  1. Body text with equations (NOT a reference list)
  2. text_a ")." ends equation citation "(R²)."
  3. text_b "Profiles" starts new sentence/section about genomic profiles
  4. URLs and accession numbers exist but are inline data references, not bibliography
  5. Context CORRECTS the mislabeled boundary_class

Does B add useful information? YES — corrects mislabeling, confirms body text
Does B create new ambiguity? PARTIAL — URLs/accession numbers could superficially look reference-like
  BUT: overall structure is clearly methods section, not reference list
  Human can distinguish inline data references from bibliography entries
Does B increase cognitive load? MODERATE — 3073 chars with technical content
Is B decision-relevant? YES — critical for correcting boundary_class mislabel
```

#### TP Safety Assessment: SAFE (with note)

```
Context helps: CORRECTS mislabeled boundary_class → confirms body text → KEEP_SEPARATE
Context overwhelms: NO (technical content is dense but readable)
New ambiguity: MINOR (URLs/accession numbers look reference-like but context is clear)
Over-reliance risk: LOW

NOTE: This case demonstrates that context can CORRECT errors in existing annotations.
      boundary_class=REFERENCE_LIST_ENTRY was WRONG, context shows body text.
      This is an additional benefit of context enrichment.
```

---

### TP Summary Table

| Case | A Judgment | B Judgment | Context Helps? | Context Overwhelms? | New Ambiguity? | Decision-Relevant? |
|---|---|---|---|---|---|---|
| IND-AMB-008 | KEEP_SEPARATE | KEEP_SEPARATE (confirmed) | YES | NO | NO | YES |
| IND-AMB-005 | KEEP_SEPARATE | KEEP_SEPARATE (confirmed) | YES | NO | NO | YES |
| IND-AMB-134 | KEEP_SEPARATE | KEEP_SEPARATE (confirmed + corrected mislabel) | YES | NO | MINOR | YES (critical) |

```
TP Safety: 3/3 SAFE
  - Context confirms existing correct judgment for all 3 TP
  - Context corrects mislabeled boundary_class for TP-134
  - No context overwhelm
  - No new ambiguity that would change judgment
  - Context is decision-relevant (confirms body text vs reference list)
```

---

## 4. Evidence Matrix

| Evidence | Exists | Relevant | Sufficient | Safely Composable |
|---|---|---|---|---|
| E_page_context (neighboring text) | YES (P7 reviewer data, 13/13 cases) | YES | PARTIAL (3/5 FP + 3/3 TP) | YES (raw text, no semantic judgment) |
| E_citation_markers ([N] in text) | YES (in page_context text) | YES | PARTIAL (detects reference list) | YES (deterministic regex) |
| E_reference_header ("References" string) | YES (in page_context, 1/5 FP) | YES | PARTIAL (strong signal when present) | YES (string match) |
| E_bibliographic_markers (vol., pp., [Online], DOI) | YES (in page_context text) | YES | PARTIAL (confirms reference list) | YES (deterministic regex) |
| E_author_name_pattern (comma-separated names) | YES (in text_a for 2/5 FP) | YES | PARTIAL (catches "Guo, Jian Zhao" pattern) | PARTIAL (regex catches some, not "Le.") |
| E_publisher_pattern (City, State: Publisher) | YES (in text_b for 2/5 FP) | YES | YES (for those 2 cases) | YES (deterministic pattern) |
| E_period (S3 field) | YES (machine_eval) | YES | NO (necessary not sufficient) | YES (already in S3) |
| E_capital (S3 field) | YES (machine_eval) | YES | NO (necessary not sufficient) | YES (already in S3) |
| E_text_content (text_a, text_b) | YES (machine_eval) | YES | NO (necessary not sufficient) | YES (already in L0) |
| E_boundary_class | YES (P7 annotation) | NO | NO | NO (has labeling errors, 4/13 mislabeled) |
| E_geometry (bbox, width) | YES (P7 geometry_provenance) | NO | NO | YES (but not decision-relevant) |
| E_author_name_recognition | NO (not in any system) | YES (2/5 FP) | NO | NO (requires semantic knowledge) |

### Matrix Summary

```
EXISTS + RELEVANT + SUFFICIENT + SAFELY_COMPOSABLE:
  E_page_context, E_citation_markers, E_bibliographic_markers, E_publisher_pattern
  → 4 items: can be organized into Evidence Pack without new module

EXISTS + RELEVANT + PARTIALLY_SUFFICIENT + SAFELY_COMPOSABLE:
  E_reference_header, E_author_name_pattern
  → 2 items: useful but not always present/reliable

EXISTS + RELEVANT + NOT_SUFFICIENT + SAFELY_COMPOSABLE:
  E_period, E_capital, E_text_content
  → 3 items: already in S3, necessary but not sufficient

EXISTS + NOT_RELEVANT or NOT_SUFFICIENT + NOT_SAFELY_COMPOSABLE:
  E_boundary_class (labeling errors), E_geometry (not decision-relevant)
  → 2 items: should NOT be included

NOT_EXISTS:
  E_author_name_recognition
  → 1 item: requires semantic knowledge, NOT safely composable
```

---

## 5. Human Evidence Dependency

### Where does Human's "Reference context" come from?

```
For each FP, trace the evidence source:

FP-003 (".", "Philadelphia, PA:"):
  A. page_context → YES (shows [12]-[31] reference entries) → SYSTEM-AVAILABLE
  B. neighboring text → YES (20+ reference entries visible) → SYSTEM-AVAILABLE (in P7, not in Pack)
  C. page image → NOT USED (Human uses text)
  D. Human background knowledge → MINIMAL ("Philadelphia, PA:" is standard geographic format)
  E. Evidence Pack → DOES NOT HAVE context
  F. P7 fields not in Pack → page_context EXISTS in P7 reviewer data

  → PRIMARY SOURCE: SYSTEM-AVAILABLE (page_context)
  → SECONDARY: MINIMAL Human knowledge (geographic format recognition)

FP-002 (".", "Springer Berlin Heidelberg,"):
  A. page_context → YES (same reference list) → SYSTEM-AVAILABLE
  D. Human background knowledge → MINIMAL ("Springer" is recognizable publisher)
  → PRIMARY SOURCE: SYSTEM-AVAILABLE (page_context)

FP-052 ("Guo, Jian Zhao, and Furao Shen.", "Image data aug-"):
  A. page_context → YES (reference list [24]-[34]) → SYSTEM-AVAILABLE
  D. Human background knowledge → LOW (author-name pattern is structural, not semantic)
  → PRIMARY SOURCE: SYSTEM-AVAILABLE (page_context + text pattern)

FP-033 ("Le.", "Randaugment:"):
  A. page_context → YES ("References" header + [1]-[8]) → SYSTEM-AVAILABLE
  D. Human background knowledge → YES ("Le." is Vietnamese surname — semantic)
  → PRIMARY SOURCE: SYSTEM-AVAILABLE (page_context) + HUMAN SEMANTIC (name recognition)
  → WITHOUT semantic: context shows reference list but "Le." is still ambiguous

FP-049 ("Levine.", "Bitrate-constrained dro:"):
  A. page_context → YES (reference list [24]-[34]) → SYSTEM-AVAILABLE
  D. Human background knowledge → MILD ("Levine" is recognizable surname)
  → PRIMARY SOURCE: SYSTEM-AVAILABLE (page_context) + MILD HUMAN SEMANTIC
```

### Evidence Source Classification

```
SYSTEM-AVAILABLE EVIDENCE (exists in P7, can be organized into Pack):
  - page_context (neighboring text) → ALL 5 FP + ALL 3 TP
  - citation markers ([N] in text) → detectable from page_context
  - bibliographic markers (vol., pp., [Online]) → detectable from page_context
  - reference header ("References") → detectable from page_context
  - publisher patterns (City, State: Publisher) → detectable from text_b

HUMAN-ONLY SEMANTIC KNOWLEDGE (not in any system layer):
  - Author-name recognition ("Le." = surname) → 2/5 FP (033, 049)
  - Paper-title recognition ("Randaugment:" = title) → 1/5 FP (033)

BOUNDARY:
  - "Guo, Jian Zhao, and Furao Shen" → structural pattern (comma-separated, "and")
    → SYSTEM-AVAILABLE (regex can detect pattern, no semantic needed)
  - "Levine." → structural position (in reference list, after [N])
    → SYSTEM-AVAILABLE context + MILD semantic (name recognition)
  - "Le." → 2-char token, no structural pattern
    → HUMAN SEMANTIC (no deterministic rule can identify "Le." as surname)
```

---

## 6. Context Enrichment Counterfactual

### A vs B Comparison

| Dimension | A (Current Pack) | B (Context-Enriched) |
|---|---|---|
| FP distinguishable | 0/5 (all ambiguous) | 3/5 fully + 2/5 partially |
| TP safe | 3/3 correct | 3/3 correct (confirmed) |
| Cognitive load | LOW (5 items) | MODERATE (5 items + 2000-5000 chars context) |
| Decision-relevant info | period, capital, text | + reference structure, neighboring text, bibliographic markers |
| New ambiguity created | N/A | NO (for TP), REDUCED (for FP) |
| Semantic leakage | 0 | 0 (raw text only, no judgments) |
| Automation bias risk | LOW | LOW (context is evidence, not recommendation) |

### Does B truly add Decision-Relevant Evidence?

```
For FP:
  A: period + capital → ambiguous (could be sentence boundary or reference continuation)
  B: + page_context → reference list structure visible → disambiguates 3/5 FP

  The additional information is NOT just "more text to read."
  It is STRUCTURAL EVIDENCE that changes the decision:
    - [N] markers → reference list detected
    - Entry pattern → within-entry continuation identified
    - Publisher/author patterns → specific roles recognized

  → B adds DECISION-RELEVANT evidence for FP

For TP:
  A: period + capital → KEEP_SEPARATE (correct)
  B: + page_context → body text confirmed → KEEP_SEPARATE (confirmed)

  The additional information CONFIRMS but does not CHANGE the decision.
  It is relevant (confirms not in reference list) but not strictly necessary.

  → B adds CONFIRMATORY evidence for TP (not strictly necessary but not harmful)
```

### Cognitive Load Assessment

```
A: Human reads text_a + text_b + S3 fields → ~50-100 chars, <5 seconds
B: Human reads text_a + text_b + S3 fields + page_context → ~2000-5000 chars, 15-30 seconds

Is the additional reading justified?

  For FP: YES — without context, Human CANNOT distinguish (0/5)
           with context, Human CAN distinguish (3/5 fully + 2/5 partially)
           → 15-30 seconds additional reading for correct decision = justified

  For TP: PARTIAL — context confirms but doesn't change decision
           → 15-30 seconds additional reading for confirmation = not strictly necessary
           → But does not HARM (no new ambiguity, no wrong direction)

  Overall: Cognitive load increases but is JUSTIFIED by decision quality improvement
  → Context is NOT "just more reading" — it adds structural evidence
```

---

## 7. Semantic Boundary

### Can be explained by Evidence (SYSTEM-AVAILABLE):

```
1. Reference list detection (3/5 FP + 3/3 TP):
   - [N] citation markers in page_context → deterministic
   - "References" header → string match
   - vol./pp./[Online]/DOI patterns → regex
   - Entry pattern (Authors. Title. Publisher. Date.) → structural
   → EVIDENCE_ORGANIZATION_GAP: data exists, not composed

2. Publisher/location recognition (2/5 FP: 003, 002):
   - "Philadelphia, PA:" → geographic format pattern
   - "Springer Berlin Heidelberg," → publisher + city pattern
   → Deterministic from text_b content + reference context

3. Author-name pattern detection (1/5 FP: 052):
   - "Guo, Jian Zhao, and Furao Shen" → comma-separated + "and" pattern
   → Deterministic regex on text_a content
```

### Still belongs to Human Semantic Boundary:

```
1. Short surname recognition (2/5 FP: 033, 049):
   - "Le." → 2 chars, no structural pattern → requires world knowledge
   - "Levine." → 7 chars, recognizable but still semantic (not structural)
   → CANNOT be resolved by deterministic rules
   → "Le." could be: Vietnamese surname, French article, abbreviation
   → No regex or pattern can safely determine "Le." is a surname

2. Paper-title recognition (1/5 FP: 033):
   - "Randaugment:" → could be title, technical term, or section header
   - In reference list context: likely title
   - But determination requires understanding what "Randaugment" refers to
   → PARTIALLY resolvable by position in reference entry
   → But "Le." recognition is the prerequisite, which is semantic

BOUNDARY ASSESSMENT:
  3/5 FP: EXPLAINABLE by existing evidence (if organized)
  2/5 FP: HUMAN SEMANTIC BOUNDARY (cannot be resolved without semantic knowledge)
  → SEMANTIC_BOUNDARY = PARTIAL
```

---

## 8. Architecture Impact

### Classification: D1 — Existing Evidence + Better Evidence Organization

```
D1: Existing Evidence + better Evidence organization
  → page_context already exists in P7 reviewer data
  → P1 text extraction pipeline produces page text
  → No new Observation, Detector, or Module needed
  → Just include existing page_context in Evidence Pack L2

D2: Existing Evidence + minimal Context Adapter
  → NOT REQUIRED (page_context is already extracted and formatted)
  → IF future implementation considers cognitive load (filtering neighboring lines),
    a minimal adapter could help, but this is ORGANIZATION not new capability

D3: Existing Evidence insufficient → future observation request
  → NOT REQUIRED for 3/5 FP (evidence exists)
  → For 2/5 FP (semantic boundary): NOT an observation gap, it's a semantic gap
  → Do NOT propose new observation for author-name recognition
    (it's TYPE-F, not safely structurable)

SELECTED: D1

  The evidence EXISTS.
  The gap is ORGANIZATIONAL.
  page_context needs to be included in Evidence Pack.
  No new module, no new observation, no new engine.
```

### Semantic Leakage Check

```
Context enrichment adds ONLY:
  - page_context (raw text from page) → NO semantic judgment
  - neighboring text (surrounding lines) → NO semantic judgment

FORBIDDEN additions (verified NOT present):
  ✗ is_reference = true → NOT ADDED
  ✗ reference_detected → NOT ADDED
  ✗ author_detected → NOT ADDED
  ✗ recommended_merge → NOT ADDED
  ✗ boundary_class → NOT ADDED (has labeling errors, excluded)
  ✗ confidence → NOT ADDED
  ✗ score → NOT ADDED
  ✗ correct_answer → NOT ADDED

Legal structure:
  Existing Context (raw text) → Evidence Pack → Human
  (NOT: Context → Reference Detector → MERGE)

Semantic Leakage = 0
```

---

## 9. Evidence Dependency Chain

### For each FP:

```
FP-003 (".", "Philadelphia, PA:"):
  Raw Evidence: text_a=".", text_b="Philadelphia, PA:", page_context (ref list [12]-[31])
       ↓
  Existing Machine Evidence: is01_a=False, is02_b=True, period=True, capital=True
       ↓
  Context Evidence: [N] markers, reference entry pattern, "Philadelphia, PA:" format
    → SYSTEM HAS IT (page_context in P7)
    → SYSTEM HAS IT BUT NOT EXPOSED (not in Evidence Pack)
    → SYSTEM HAS IT BUT NOT COMPOSED (not organized into L2)
       ↓
  Human-perceived relation: "." ends title, "Philadelphia, PA:" is publisher location
    → Determinable from context + text pattern (MINIMAL semantic)
       ↓
  Human decision: MERGE

FP-033 ("Le.", "Randaugment:"):
  Raw Evidence: text_a="Le.", text_b="Randaugment:", page_context (ref list [1]-[8])
       ↓
  Existing Machine Evidence: is01_a=False, is02_b=True, period=True, capital=True
       ↓
  Context Evidence: "References" header, [N] markers
    → SYSTEM HAS IT (page_context in P7)
    → SYSTEM HAS IT BUT NOT EXPOSED (not in Evidence Pack)
       ↓
  Human-perceived relation: "Le." is author surname, "Randaugment:" is paper title
    → "Le." = surname → HUMAN SEMANTIC KNOWLEDGE
    → "Randaugment:" = title → inferable from position BUT requires "Le." recognition first
       ↓
  Human decision: MERGE (but requires semantic knowledge beyond system evidence)
```

### Chain Classification Summary

| Evidence Layer | Status | Count |
|---|---|---|
| SYSTEM HAS IT (in machine_eval) | Available | E1, E2, E3, E12 (S3 fields) |
| SYSTEM HAS IT BUT NOT EXPOSED (in P7, not in Pack) | page_context | ALL 13 cases |
| SYSTEM HAS IT BUT NOT COMPOSED (composable from existing) | citation markers, bib markers | Detectable from page_context |
| SYSTEM DOES NOT HAVE IT | author-name recognition | 2/5 FP (033, 049) |
| HUMAN SEMANTIC KNOWLEDGE | surname recognition, title recognition | 2/5 FP (033, 049) |

---

## 10. Minimum Evidence Human Needs

### For each FP (describing Evidence, NOT giving conclusions):

```
FP-003: Human needs:
  - A/B surrounding context (page_context showing reference entries [12]-[31])
  - A/B 前后文本 (neighboring reference entries with [N] markers)
  - 当前局部文本结构 (reference entry pattern: [N] Authors. Title. Publisher. Date.)
  → "Philadelphia, PA:" recognized as publisher location from format pattern

FP-002: Human needs:
  - Same as FP-003 (same page, same reference list)
  - "Springer Berlin Heidelberg," recognized as publisher name from pattern

FP-052: Human needs:
  - A/B surrounding context (page_context showing reference entries [24]-[34])
  - text_a pattern: comma-separated capitalized names with "and" → author-name structure
  - text_b position: follows author names + period → title position

FP-033: Human needs:
  - A/B surrounding context (page_context showing "References" + [1]-[8])
  - text_a "Le." → requires recognizing "Le" as a surname (HUMAN SEMANTIC)
  - text_b "Randaugment:" → position in reference entry suggests title

FP-049: Human needs:
  - A/B surrounding context (page_context showing reference entries [24]-[34])
  - text_a "Levine." → requires recognizing "Levine" as a surname (MILD HUMAN SEMANTIC)
  - text_b "Bitrate-constrained dro:" → position suggests title
```

---

## 11. Governance Gate

```
HVA-07 STATUS = COMPLETE
EVIDENCE_CONTEXT_STATUS = PARTIALLY_SUPPORTED
PRIMARY_BOTTLENECK = EVIDENCE_ORGANIZATION_GAP (page_context exists, not composed)
SECONDARY_BOTTLENECK = SEMANTIC_BOUNDARY (author-name recognition, 2/5 FP)
NEW_OBSERVATION = NOT_REQUIRED
LLM_REQUIRED = NO
MINIMAL_ADAPTER_REQUIRED = NO
ARCHITECTURE_IMPACT = D1 (Existing Evidence + better organization)

IMPLEMENTATION_AUTHORIZED = FALSE
EXPERIMENT_AUTHORIZED = FALSE
DICE_CORE_MODIFICATION = NO
P1_P7_MODIFICATION = NO
TLD_MODIFICATION = NO
IS11_MODIFICATION = NO
GT_MODIFICATION = NO
SIGNAL_MODIFICATION = NO
S3_MODIFICATION = NO
SC05_MODIFICATION = NO
VS05_MODIFICATION = NO
LLM = NO
NEW_OBSERVATION = NO
NEW_MODULE = NO
NEW_ENGINE = NO
NEW_RULE = NO
NEW_CLASSIFIER = NO
NEW_DETECTOR = NO
REFERENCE_DETECTOR = NO
RUNTIME_CHANGE = NO
CAPABILITY_CHANGE = NO
THRESHOLD_ADJUSTMENT = NO

SEMANTIC_LEAKAGE = 0
AUTHORITY_LEAKAGE = 0

FROZEN_BASELINE = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d)
PRODUCTION = FALSE
STOP = TRUE
```

---

## 12. 8-Sentence Final Answer

1. **page_context 已经存在于 P7 reviewer data 中**——13/13 cases 全部有 page_context（1889-5569 chars），包含 neighboring text、reference structure、bibliographic markers，但当前不在 Evidence Pack 中。

2. **3/5 FP 可被 context 完全解释**（IND-AMB-003, 002, 052）——page_context 显示 reference list 结构（[N] markers + entry pattern），text_b 中的 publisher/location/author-name patterns 可被确定性识别，不需要新的 semantic knowledge。

3. **2/5 FP 仍需 Human semantic knowledge**（IND-AMB-033, 049）——"Le." 和 "Levine." 的 surname recognition 超出确定性规则范围，page_context 显示 reference list 但无法确定性识别 2-char token 为人名。

4. **3/3 TP 不受负面影响**——context 确认 body text 判断（IND-AMB-008, 005），甚至纠正了 mislabeled boundary_class（IND-AMB-134），不产生新歧义，不增加过度依赖风险。

5. **EVIDENCE_CONTEXT_STATUS = PARTIALLY_SUPPORTED**——context 对 3/5 FP 充分，对 2/5 FP 部分充分，对 3/3 TP 安全，这是 CASE B（Context 部分足够）。

6. **Architecture Impact = D1**——page_context 是已有 Evidence（P7 reviewer data），只需要更好的 Evidence organization（加入 Evidence Pack L2），不需要新 Observation、新 Module、新 Engine、新 Adapter。

7. **Semantic Leakage = 0**——context enrichment 只添加 raw text（page_context），不添加 is_reference、reference_detected、author_detected、recommended_decision 等语义判断，合法结构是 Existing Context → Evidence Pack → Human。

8. **不试图消灭全部 Human Semantic Boundary**——2/5 FP 的 author-name recognition 是真实 Semantic Boundary，接受它存在，不为了消灭 boundary 而创建 Reference Detector 或 Rule，下一阶段只解决前 3 个 FP 的 Evidence Organization 问题。

`STOP = TRUE`。
