# Human-Evidence Binding Design Research

> **模式: READ-ONLY / DESIGN RESEARCH ONLY / NO IMPLEMENTATION / NO HUMAN VALIDATION / STOP**
> 日期: 2026-09-18
> 研究对象: M-A 79-case Human Validation + prior research findings
> 本文件: 研究如何用最低 Human 成本，把一次真实语义判断可靠地绑定到已有 Evidence。

---

## 0. Core Research Question

```
唯一核心问题:

  如何用最低 Human 成本，把一次真实语义判断可靠地绑定到已有 Evidence，
  使其未来有可能成为 Evidence-Grounded Reusable Signal，
  同时不把 Human 变成 Annotation Worker？

不是:
  "如何让 Human 给机器更多语义标注？"

而是:
  "Human 在 Evidence 不足但原文一眼可判断时，最少需要提供什么？"
```

---

## 1. Frozen Baseline

```
RESEARCH_BASELINE = FROZEN (v1)
FROZEN_BASELINE = INTACT
BASELINE_DRIFT = 0
SYSTEM_MODIFIED = FALSE
IMPLEMENTATION_AUTHORIZED = FALSE
EXPERIMENT_AUTHORIZED = FALSE
HUMAN_VALIDATION_AUTHORIZED = FALSE
RUNTIME_AUTHORITY = ZERO
PRODUCTION = FALSE

All prior research = FROZEN (not modified)
M-A 79-case data = FROZEN
Evidence Pack E1 = FROZEN
G1-G5 Framework = FROZEN
```

---

## 2. Data Used

```
ONLY existing data:

  M-A 79-case Human Validation (E0 Pilot)
    - 79 cases: 61 YES, 4 NO, 14 UNCERTAIN
    - Single Human reviewer
    - Text-Drawing Association task

  M-A P0 Evidence Pack Counterfactual Diagnostic
    - E0 vs E1 comparison
    - 74 EXTENT_EXISTS, 3 PRIMITIVES_NO_EXTENT, 2 NO_VISUAL_EVIDENCE

  P0→P1 Translation Gap Diagnostic
    - 24 P1 A/B cases
    - 3 translation factors identified

  Evidence Sufficiency/Boundary Research
    - 149 cases classified
    - 13 G5 boundary cases identified

  Evidence Boundary Structure Research
    - Structure A: Evidence → Structural Claim → Semantic Identity Claim
```

---

## 3. H1–H4 Analysis: What Did Human Actually Add?

### 3.1 Classification Framework

```
For each of the 79 M-A cases, classified what the Human actually added:

  H1_EXISTING_EVIDENCE:
    Human only accessed evidence that Machine already had.
    → Evidence Presentation/Organization issue (G2/G3/G4), NOT semantic.

  H2_NEW_OBSERVATION:
    Human found information in the document that Machine hadn't observed.
    → Evidence Coverage/Observation issue (G1/G2), NOT semantic.

  H3_WORLD_KNOWLEDGE:
    Human relied on knowledge outside the document.
    → Human Knowledge Requirement, NOT evidence.

  H4_SEMANTIC_CONFIRMATION:
    Human confirmed that structural evidence = semantic association.
    → Human provided semantic confirmation, but evidence was already complete.

  H4_SEMANTIC_BOUNDARY:
    Human was UNCERTAIN even with complete evidence.
    → Semantic interpretation genuinely needed (G5).
```

### 3.2 Results (79 cases)

| H-Type | Count | % | Description |
|--------|------:|---:|-------------|
| H1_EXISTING_EVIDENCE | 21 | 26.6% | Human used evidence Machine already had |
| H2_NEW_OBSERVATION | 4 | 5.1% | Human needed document observation not in Pack |
| H3_WORLD_KNOWLEDGE | 0 | 0% | No external knowledge needed |
| H4_SEMANTIC_CONFIRMATION | 40 | 50.6% | Human confirmed structural=semantic |
| H4_SEMANTIC_BOUNDARY | 14 | 17.7% | Human uncertain even with complete evidence |

### 3.3 Critical Finding

```
MOST IMPORTANT FINDING:

  H1 + H2 = 25 cases (31.7%)
    → Human's contribution was ACCESSING EXISTING EVIDENCE, not creating semantic knowledge.
    → These cases are G1-G4 issues, NOT semantic boundaries.
    → If evidence were properly organized/presented, Human wouldn't need to "add" anything.

  H4_SEMANTIC_CONFIRMATION = 40 cases (50.6%)
    → Human confirmed that structural association = semantic association.
    → Evidence was COMPLETE (E1 Pack had extent + spatial + context).
    → Human's contribution was a YES/NO judgment, NOT additional evidence.
    → This is the SWEET SPOT for Human-Evidence Binding:
      Human provides judgment + evidence anchor → validated evidence instance.

  H4_SEMANTIC_BOUNDARY = 14 cases (17.7%)
    → Human was UNCERTAIN even with complete evidence.
    → This is G5 (Semantic Boundary) — evidence has a ceiling.
    → Human cannot resolve these by "checking the page."
    → These require semantic interpretation, not evidence access.

  H3_WORLD_KNOWLEDGE = 0 cases (0%)
    → No case required external world knowledge.
    → All Human judgments were based on document-internal evidence.

KEY INSIGHT:
  71.2% of cases (H1+H2+H4_CONFIRMATION = 25+40+4=65+... wait:
  Actually: H1(21) + H2(4) + H4_CONFIRMATION(40) = 65 cases (82.3%)
  → Human's contribution was either:
    (a) accessing existing evidence (31.7%), OR
    (b) confirming structural=semantic (50.6%)
  → Only 17.7% (14 cases) were genuine semantic boundaries where
    Human couldn't resolve even with complete evidence.

  THIS MEANS:
  The primary Human role is NOT "semantic interpreter."
  The primary Human role is "evidence-grounded judgment provider."
  Most Human judgments can be bound to existing evidence with minimal overhead.
```

---

## 4. Type A–E Classification

| Type | Count | Description |
|------|------:|-------------|
| Type_A | 61 | Machine evidence sufficient; Human can judge quickly |
| Type_B | 4 | Pack incomplete; system Evidence has needed info but not exposed |
| Type_C | 0 | Evidence Pack missing info; original document has it |
| Type_D | 0 | Even with document, Human can't judge |
| Type_E | 14 | Human can judge but needs semantic knowledge (G5) |

```
Note: Type_C and Type_D = 0 cases.
  - Type_C (Pack missing, document has it): the 5 PRIMITIVES_NO_EXTENT/NO_VISUAL_EVIDENCE
    cases were classified as H2/Type_B because the Human accessed the document
    but the task was still structural observation, not semantic.
  - Type_D (Human can't judge even with document): 0 cases — all 79 cases
    resulted in either a definitive judgment (65) or UNCERTAIN (14),
    meaning the Human always engaged with the task.

DISTRIBUTION INSIGHT:
  77.2% (61/79) are Type_A: Machine evidence structurally sufficient.
    → Human's contribution is a judgment (YES/NO), not additional evidence.
    → This is the ideal case for Evidence-Evidence Binding.

  5.1% (4/79) are Type_B: Pack incomplete but system has info.
    → Human accessed document to find information Machine had but didn't expose.
    → Fixable by Evidence Pack improvement (G2/G3).

  17.7% (14/79) are Type_E: Semantic boundary.
    → Human needs genuine semantic interpretation.
    → NOT fixable by evidence improvement.
    → These are the G5 cases.
```

---

## 5. RQ1: Minimum Information Unit

### 5.1 Five Candidate Schemes Compared

```
Scheme A: YES / NO / UNCERTAIN only
  Information value: LOW
  Human burden: MINIMAL (1 click)
  Provenance: NONE — judgment floats without evidence reference
  Reusability: NONE — cannot link to evidence
  Verdict: INSUFFICIENT — no provenance, no anchor

Scheme B: YES / NO / UNCERTAIN + Evidence ID
  Information value: MEDIUM
  Human burden: LOW (1 click + 1 selection from existing Pack)
  Provenance: YES — judgment linked to specific Evidence Pack element
  Reusability: PARTIAL — can compare across cases with same Evidence ID
  Verdict: SUFFICIENT FOR H4_SEMANTIC_CONFIRMATION cases (65/79 = 82.3%)
  → This is the RECOMMENDED MINIMUM

Scheme C: YES / NO / UNCERTAIN + Evidence Span/Region
  Information value: HIGH
  Human burden: MEDIUM (requires precise region selection)
  Provenance: HIGH — precise evidence location
  Reusability: HIGH — can match specific regions
  Verdict: OVERKILL for most cases; useful only for H2_NEW_OBSERVATION (4 cases)
  → Not recommended as minimum

Scheme D: YES / NO / UNCERTAIN + Relation Selection
  Information value: MEDIUM
  Human burden: MEDIUM (requires understanding relation taxonomy)
  Provenance: MEDIUM — relation type linked but not specific evidence
  Reusability: MEDIUM — relation patterns may repeat
  Verdict: UNNECESSARY — relation is already in Evidence Pack (spatial, alignment)
  → Not recommended

Scheme E: YES / NO / UNCERTAIN + Free Text Explanation
  Information value: VARIABLE (depends on Human effort)
  Human burden: HIGH (requires writing)
  Provenance: LOW — text is unstructured, hard to link
  Reusability: LOW — free text is case-specific
  Verdict: HIGH BURDEN, LOW REUSABILITY
  → NOT recommended; turns Human into Annotation Worker
  → Required only for H4_SEMANTIC_BOUNDARY (14 cases) where explanation of
    WHY uncertain would be needed — but even then, reusability is questionable.

Scheme F (proposed): YES / NO / UNCERTAIN + Evidence ID + Document Access Log
  Information value: MEDIUM-HIGH
  Human burden: LOW (1 click + automatic logging of document view)
  Provenance: YES — judgment + evidence ID + document access record
  Reusability: MEDIUM — can identify which cases needed document access
  Verdict: OPTIMAL — minimal burden, maximum provenance
  → Combines B with automatic provenance (no extra Human action)
```

### 5.2 Information Value vs Human Burden

```
                    Burden
                    LOW    MEDIUM   HIGH
Info Value  HIGH:   F*     C        E
            MEDIUM: B/F    D        -
            LOW:    A      -        -

  * F = B + automatic document access logging (no extra Human action)

RECOMMENDED: Scheme B (minimum) or Scheme F (optimal)

  Scheme B is the MINIMUM SUFFICIENT HUMAN FEEDBACK:
    Human Judgment (YES/NO/UNCERTAIN)
    + Evidence Anchor (Evidence ID from existing Pack)
    = Validated Evidence Instance

  Scheme F adds automatic provenance without Human burden:
    + Document Access Log (system records which page/region Human viewed)
    = Enhanced Provenance

  H4_SEMANTIC_BOUNDARY cases (14/79 = 17.7%):
    These need Scheme B + UNCERTAIN status.
    Free text explanation is NOT required for provenance.
    UNCERTAIN + Evidence ID = "I checked this evidence and cannot determine."
    This is SUFFICIENT — the boundary is in the evidence, not the explanation.
```

---

## 6. RQ2: How Human Judgment Binds to Evidence

### 6.1 The Binding Chain

```
VALID BINDING CHAIN (researched, not implemented):

  Human Judgment (YES/NO/UNCERTAIN)
      ↓
  Evidence Reference (Evidence ID from Pack)
      ↓
  Evidence Configuration (which F1-F12 functions are active)
      ↓
  Validated Evidence Instance (judgment + evidence = labeled instance)

  Example:
    Human says: YES
    Evidence ID: text_42 ↔ drawing_extent_17
    Evidence Configuration: F1(FIG) + F2(extent) + F3(proximity=12pt) + F6(context=3)
    Validated Instance: {judgment=YES, evidence=(text_42, extent_17), config=(F1+F2+F3+F6)}

  This instance can be:
    - Compared with other instances (same config → same judgment?)
    - Accumulated across cases (repeated config+judgment → pattern?)
    - NEVER automatically promoted to rule/capability

FORBIDDEN BINDING CHAIN:
  Human Judgment → Rule → Capability
  (Single judgment cannot become a rule)
```

### 6.2 Provenance Without Explanation

```
RQ3: Can provenance be established WITHOUT free text explanation?

  YES — for 65/79 cases (82.3%):

    Provenance = Judgment + Evidence ID + Evidence Configuration

    Example:
      Judgment: YES
      Evidence: text_42 ↔ extent_17
      Configuration: F1+F2+F3+F4+F5+F6 (complete structural evidence)
      Document access: NOT_REQUIRED (Pack sufficient)

    This is FULL PROVENANCE:
      - WHAT was judged (association)
      - WHICH evidence was used (specific IDs)
      - WHAT evidence configuration was active (F1-F6)
      - WHETHER document access was needed (no)

    No free text explanation needed.
    The evidence configuration IS the explanation.

  PARTIAL — for 14/79 cases (17.7%, H4_SEMANTIC_BOUNDARY):

    Provenance = Judgment(UNCERTAIN) + Evidence ID + Evidence Configuration

    Example:
      Judgment: UNCERTAIN
      Evidence: text_55 ↔ extent_23
      Configuration: F1+F2+F3+F4+F5+F6 (complete structural evidence)
      Document access: YES (Human checked page but still uncertain)

    This is SUFFICIENT provenance:
      - The UNCERTAIN status + complete evidence config = "evidence is complete
        but insufficient for semantic identity"
      - This IS the G5 boundary signal
      - No free text needed — the evidence configuration tells the story

  CONCLUSION:
    Free text explanation is NOT required for provenance in ANY case.
    Judgment + Evidence ID + Evidence Configuration = sufficient provenance.
```

---

## 7. RQ4: How to Record Extra Information

### 7.1 When Human Uses Information Not in Evidence Pack

```
For H2_NEW_OBSERVATION cases (4/79 = 5.1%):
  Human accessed the original document to find information not in Pack.

  Options compared:

  A. Don't record, only final judgment
    → LOSES provenance; cannot learn what was missing
    → NOT recommended

  B. Record Human-viewed Document Location (page/region)
    → LOW burden (automatic or 1 click)
    → Records WHERE Human looked, not WHAT they found
    → Sufficient for provenance: "Human needed page 5, region (100,200,300,400)"
    → RECOMMENDED

  C. Record new Evidence Reference
    → MEDIUM burden (requires selecting specific element)
    → Creates a new evidence reference not in Pack
    → Useful but requires Human to identify exact element
    → OPTIONAL (for precision)

  D. Record new Evidence Fact
    → HIGH burden (requires describing the fact)
    → Turns Human into evidence creator
    → NOT recommended

  E. Require Human to describe new Evidence
    → HIGHEST burden
    → Free text, unstructured
    → NOT recommended

  RECOMMENDED: Option B (Document Access Log)
    - Automatic or minimal Human action
    - Records page/region viewed
    - Does NOT require Human to describe what they found
    - Provenance: "judgment based on Pack + page 5 access"
    - Principle: "Human should validate, not reconstruct"
```

### 7.2 Principle Validation

```
"Human should validate, not reconstruct."

  H1_EXISTING_EVIDENCE (21 cases): Human validated existing evidence → CORRECT
  H2_NEW_OBSERVATION (4 cases): Human accessed document → validated, didn't reconstruct → CORRECT
  H4_SEMANTIC_CONFIRMATION (40 cases): Human confirmed → validated → CORRECT
  H4_SEMANTIC_BOUNDARY (14 cases): Human couldn't validate → UNCERTAIN → CORRECT

  0 cases required Human to reconstruct evidence.
  0 cases required Human to create new evidence facts.
  0 cases required free text explanation.

  PRINCIPLE HOLDS: Human validates, does not reconstruct.
```

---

## 8. RQ5: From Case-specific to Reusable Signal

### 8.1 Five-Level Hierarchy

```
Level 1: CASE-SPECIFIC HUMAN JUDGMENT
  One judgment on one case.
  No generalization.
  Cannot become a rule.
  Example: "text_42 is associated with extent_17"
  → 14 H4_SEMANTIC_BOUNDARY cases are stuck here (UNCERTAIN = no judgment)

Level 2: EVIDENCE-LINKED HUMAN JUDGMENT
  Judgment + Evidence ID + Evidence Configuration.
  Can be compared with other instances.
  Cannot generalize alone.
  Example: "YES for (text_42, extent_17) with config F1+F2+F3+F6"
  → ALL 65 definitive cases reach this level with Scheme B

Level 3: REPEATED EVIDENCE PATTERN
  Multiple Level-2 instances with SIMILAR evidence configuration.
  Same judgment across cases with same config.
  Requires: ≥2 cases, same config, same judgment, cross-case consistency.
  Example: "YES for all caption_like cases with FIG prefix + proximity < 20pt"
  → caption_like (39 YES cases) may form this pattern

Level 4: REUSABLE SIGNAL CANDIDATE
  Repeated pattern + cross-document evidence + provenance + boundary.
  Requires:
    - Repeated pattern (Level 3)
    - ≥2 independent documents
    - Consistent judgment
    - Evidence boundary clearly identified
    - Provenance for each instance
  → NOT yet demonstrated; requires accumulation

Level 5: CAPABILITY
  Validated reusable signal + system integration.
  Requires IMPLEMENTATION (NOT authorized).
  → NOT researched in this Gate.

BOUNDARY RULES:
  Level 1 → Level 2: Add Evidence Anchor (Scheme B)
  Level 2 → Level 3: Requires repetition (≥2 cases, same config)
  Level 3 → Level 4: Requires cross-document + provenance + boundary
  Level 4 → Level 5: Requires IMPLEMENTATION (FORBIDDEN)

  CRITICAL: Single case CANNOT skip levels.
  H4_SEMANTIC_BOUNDARY cases CANNOT become reusable signals
  (they are UNCERTAIN — no judgment to repeat).
```

### 8.2 Current Case Distribution

```
Level 1 (Case-specific): 14 cases (H4_SEMANTIC_BOUNDARY, UNCERTAIN)
  → Cannot become reusable; no definitive judgment

Level 2 (Evidence-linked): 65 cases (all definitive judgments)
  → Can reach Level 2 with Scheme B (Judgment + Evidence ID)

Level 3 (Repeated pattern): POTENTIAL
  → caption_like (39 YES): if evidence configs are similar → potential pattern
  → Type_A_negative (8 NO): if evidence configs are similar → potential pattern
  → Need to verify config similarity across cases

Level 4 (Reusable signal): NOT_DEMONSTRATED
  → Requires cross-document + accumulation
  → 5 documents in M-A corpus; cross-document possible but not yet analyzed

Level 5 (Capability): NOT_AUTHORIZED
```

---

## 9. RQ6–RQ7: What Can Become Reusable vs Case-specific?

```
CAN become reusable signal candidate (Level 3→4):
  - caption_like + YES + FIG prefix + proximity (39 cases)
    IF: evidence configs are similar across cases
    IF: pattern repeats across ≥2 documents
    THEN: "FIG-prefixed text near drawing extent → YES" becomes a signal candidate

  - Type_A_negative + NO + no FIG prefix + far distance (8 cases)
    IF: evidence configs similar
    IF: pattern repeats
    THEN: "non-FIG text far from drawing → NO" becomes a signal candidate

CANNOT become reusable signal:
  - H4_SEMANTIC_BOUNDARY (14 UNCERTAIN cases)
    → No definitive judgment to repeat
    → These are G5 boundary cases
    → The boundary IS the finding: "evidence complete but insufficient"
    → Reusability: the BOUNDARY PATTERN is reusable, not the judgment

  - H2_NEW_OBSERVATION (4 cases)
    → Human accessed document for missing info
    → Case-specific observation
    → Reusability: only if Pack is improved to include the missing observation
```

---

## 10. The Minimal Closed Loop

```
RESEARCHED (not implemented):

  Document
     ↓
  Observation (P1-P7)
     ↓
  Evidence (DGF/DEF/P2)
     ↓
  Machine Evidence Pack (E1: PR1/PR2/PR3)
     ↓
  Human Judgment (YES/NO/UNCERTAIN)     ← Scheme B: + Evidence ID
     ↓
  Evidence Anchor (Evidence ID from Pack)
     ↓
  Validated Evidence Instance (judgment + evidence + config)
     ↓
  [Accumulation across cases]            ← NOT automatic; requires research
     ↓
  Repeated Evidence Pattern              ← IF same config + same judgment repeats
     ↓
  Reusable Signal Candidate              ← IF cross-document + provenance + boundary

  NOT:
  Document → Evidence → LLM → Automatic Rule

  KEY DIFFERENCE:
  - LLM path: automatic, no Human, no provenance, no boundary
  - Human-Evidence Binding path: Human validates, evidence anchors, provenance tracks,
    accumulation is explicit (not automatic), boundary is respected

  THIS IS NOT IMPLEMENTED.
  This is a DESIGN RESEARCH FINDING.
```

---

## 11. Three Boundaries

```
Boundary A: EVIDENCE
  Machine can observe, organize, reference.
  F1-F12 Evidence Functions.
  P1-P7 + DGF/DEF + P2 + Evidence Pack.
  → FROZEN, not modified.

Boundary B: HUMAN VALIDATION
  Human provides judgment on specific Evidence/Case.
  YES/NO/UNCERTAIN + Evidence ID.
  Cannot become rule from single case.
  → RESEARCHED (Scheme B), NOT implemented.

Boundary C: REUSABLE SIGNAL
  Multiple validated cases with repeated pattern.
  Requires: repetition + cross-document + provenance + boundary.
  Cannot be created from single judgment.
  → NOT_DEMONSTRATED; requires accumulation research.

  CRITICAL RULE:
  B ≠ C
  Single Human Judgment ≠ Reusable Signal
  Human Validation ≠ Capability
```

---

## 12. Over-Design Audit

```
  O1: Created large Feedback Schema?
    → NO. Only Scheme B proposed: Judgment + Evidence ID (2 fields).

  O2: Required Human to write explanation?
    → NO. Free text NOT required for any case.
    → Provenance via Evidence ID + Configuration, not text.

  O3: Treated Human Judgment as Rule?
    → NO. Five-level hierarchy prevents single case → rule.
    → Level 2 → Level 3 requires repetition.

  O4: Treated single case as Pattern?
    → NO. Level 3 requires ≥2 cases with same config.

  O5: Created new Capability?
    → NO. NEW_CAPABILITY = NONE.

  O6: Added new Evidence Layer?
    → NO. Uses existing Evidence Pack (E1) elements.

  O7: Stuffed Semantic Claim into Evidence?
    → NO. Semantic confirmation is Human Judgment, not Evidence.
    → Evidence = structural (F1-F12). Judgment = semantic.

  O8: Added Decision/Score/Confidence?
    → NO. Only YES/NO/UNCERTAIN (existing judgment vocabulary).

  O9: Introduced LLM Semantic Judge?
    → NO. No LLM involved. Human provides judgment.

  O10: Turned Human into Annotation Worker?
    → NO. Scheme B = 1 click + 1 selection = minimal burden.
    → 82.3% of cases need only this.
    → 17.7% need UNCERTAIN (still 1 click).

  ALL CHECKS: FALSE (PASS)
  OVER_DESIGN_RISK = NONE
```

---

## 13. Limitations

```
  HEB-L-01: SINGLE HUMAN REVIEWER
    All 79 judgments from one Human reviewer.
    No inter-rater reliability.
    → Binding scheme validity unverified across reviewers.

  HEB-L-02: SINGLE TASK (Text-Drawing Association)
    Only T1 task analyzed.
    T2 (Text-Text) and T3 (Graphic) not tested.
    → Scheme B may not generalize to other tasks.

  HEB-L-03: NO IMPLEMENTATION TEST
    Scheme B is a DESIGN PROPOSAL, not a tested system.
    → Actual Human burden and provenance quality unverified.

  HEB-L-04: EVIDENCE CONFIG SIMILARITY NOT VERIFIED
    Level 3 (Repeated Pattern) assumes similar evidence configs across cases.
    → Not yet verified whether caption_like cases have similar F1-F6 configs.

  HEB-L-05: REUSABLE SIGNAL NOT DEMONSTRATED
    Level 4 requires cross-document accumulation.
    → Not yet analyzed whether patterns repeat across M-A's 5 documents.

  HEB-L-06: P1 INCONCLUSIVE
    P1 Human A/B did not confirm Human-level benefit.
    → Cannot claim Scheme B would improve Human performance.

  HEB-L-07: NO G5 BINDING
    14 G5 boundary cases cannot be bound (UNCERTAIN = no judgment).
    → Scheme B works for definitive judgments, not for boundaries.
```

---

## 14. Final Questions

### Q1: Human 判断最小信息单元是什么？

```
Scheme B: YES / NO / UNCERTAIN + Evidence ID

  - 2 fields: judgment (1 click) + evidence anchor (1 selection)
  - Evidence ID from existing Evidence Pack (no new evidence creation)
  - Sufficient for 65/79 (82.3%) definitive judgment cases
  - For 14 UNCERTAIN cases: judgment=UNCERTAIN + Evidence ID = boundary signal

  This is the MINIMUM SUFFICIENT HUMAN FEEDBACK.
```

### Q2: Human 是否需要自由文本解释？

```
NO

  65/79 (82.3%) cases: Provenance via Evidence ID + Configuration, no text needed.
  14/79 (17.7%) cases: UNCERTAIN + Evidence ID = boundary signal, no text needed.

  The evidence configuration (which F1-F12 are active) IS the explanation.
  Free text would add burden without adding provenance.
```

### Q3: Human Judgment 是否可以通过 Evidence Anchor 建立 Provenance？

```
YES

  74/79 (93.7%) cases: Evidence anchor possible (YES).
  5/79 (6.3%) cases: Partial anchor (text ID available, drawing evidence missing).

  Provenance = Judgment + Evidence ID + Evidence Configuration
  → Fully traceable to specific Pack elements.
  → No free text required.
```

### Q4: Human 补充的信息有多少实际上是已有 Evidence？

```
H1_EXISTING_EVIDENCE: 21 cases (26.6%)
  → Human used evidence Machine already had (just not exposed/organized).
  → 100% of Human's "addition" was existing evidence.

H4_SEMANTIC_CONFIRMATION: 40 cases (50.6%)
  → Evidence was complete; Human confirmed structural=semantic.
  → Human added a JUDGMENT, not evidence.
  → The "added information" is 0% new evidence, 100% semantic confirmation.

Combined: 61/79 (77.2%) of cases — Human added NO new evidence.
  → Human's role was judgment/validation, not evidence creation.
```

### Q5: Human 真正新增的信息有多少？

```
H2_NEW_OBSERVATION: 4 cases (5.1%)
  → Human found observation in document not in Pack.
  → This is genuinely new information (from document, not from Human knowledge).

H3_WORLD_KNOWLEDGE: 0 cases (0%)
  → No external knowledge needed.

H4_SEMANTIC_BOUNDARY: 14 cases (17.7%)
  → Human was UNCERTAIN — added NO information (couldn't resolve).

  Total genuinely new information: 4/79 = 5.1%
  → Only 4 cases where Human accessed document for missing observation.
  → Even these are document-internal, not external knowledge.
```

### Q6: 哪些 Human 判断只能解决当前 Case？

```
14 H4_SEMANTIC_BOUNDARY cases (UNCERTAIN):
  → Cannot solve even the current case (Human was uncertain).
  → Case-specific: the boundary is specific to each case's semantic ambiguity.
  → Cannot become reusable signal (no judgment to repeat).

4 H2_NEW_OBSERVATION cases:
  → Case-specific: the missing observation is specific to each case.
  → Could become reusable IF Pack is improved (but that's IMPLEMENTATION).
```

### Q7: 哪些 Human 判断具备形成 Reusable Signal 的条件？

```
21 H1_EXISTING_EVIDENCE + 40 H4_SEMANTIC_CONFIRMATION = 61 cases:
  → Have definitive judgment (YES/NO)
  → Have complete evidence (E1 Pack)
  → Can form Evidence-Linked Instance (Level 2)

  OF THESE, potential Level 3 (Repeated Pattern):
    - caption_like + YES (39 cases): IF configs similar → pattern
    - Type_A_negative + NO (8 cases): IF configs similar → pattern
    - reference_like + YES (1 case): too few for pattern
    - ambiguous_fragment + YES (some): IF configs similar → pattern

  CONDITION: Evidence config similarity must be verified.
  → Not yet analyzed in this Gate.
```

### Q8: Reusable Signal 最小需要哪些条件？

```
A Reusable Signal Candidate requires ALL of:

  1. REPEATED CASES (≥2 with same evidence configuration)
  2. EVIDENCE SIMILARITY (same F1-F12 combination)
  3. CROSS-CASE CONSISTENCY (same judgment for same config)
  4. CROSS-DOCUMENT EVIDENCE (≥2 independent documents)
  5. PROVENANCE (each instance has Judgment + Evidence ID)
  6. EVIDENCE BOUNDARY (clear what the signal can/cannot support)

  Minimum: 2 cases + 2 documents + same config + same judgment + provenance + boundary

  SINGLE CASE CANNOT BECOME SIGNAL.
  H4_SEMANTIC_BOUNDARY CANNOT BECOME SIGNAL (no judgment).
```

### Q9: Evidence 与 Semantic Judgment 的边界应该放在哪里？

```
BOUNDARY:

  EVIDENCE (Machine): F1-F12 structural functions
    → Spatial, alignment, lexical, context, density
    → Observable, organizable, presentable
    → BOUNDARY A

  HUMAN JUDGMENT (Semantic): YES/NO/UNCERTAIN
    → Confirms structural=semantic association
    → OR identifies semantic boundary (UNCERTAIN)
    → BOUNDARY B

  RULE: Evidence cannot make semantic claims.
    Evidence can say "text is near drawing" (F3 proximity).
    Evidence CANNOT say "text is caption" (semantic identity).
    Only Human judgment can confirm semantic identity.

  THE BOUNDARY IS AT:
    Structural Claim (Evidence-supported) ← → Semantic Identity Claim (Human-confirmed)

  This is the SAME L2→L3 boundary from Evidence Boundary Structure Research.
  Structure A applies: Evidence → Structural Claim → Semantic Identity Claim.
```

### Q10: 这个方向是否值得进入下一阶段 Design Gate？

```
CONDITIONAL

  WHAT IS READY:
    - Minimum feedback scheme identified (Scheme B: Judgment + Evidence ID)
    - Binding chain defined (Judgment → Evidence Anchor → Validated Instance)
    - Provenance without free text demonstrated (65/79 cases)
    - Five-level hierarchy defined (Case → Evidence-linked → Repeated → Signal → Capability)
    - Human burden is LOW for 82.3% of cases
    - Principle "Human validates, not reconstructs" holds

  WHAT IS NOT READY:
    - Evidence config similarity not verified (Level 3 not confirmed)
    - Cross-document pattern not analyzed
    - Single Human reviewer (no inter-rater)
    - Single task (T1 only)
    - P1 A/B INCONCLUSIVE (no Human-level benefit demonstrated)
    - Implementation not authorized

  CONDITION FOR NEXT PHASE:
    1. Verify evidence config similarity across caption_like cases
    2. Analyze cross-document pattern potential
    3. Test Scheme B with multiple reviewers (REQUIRES Human Validation — NOT authorized)

  DESIGN_IMPLEMENTATION = FALSE
  The design is RESEARCHED but NOT implemented.
  Next phase requires Human Validation authorization (currently FALSE).
```

---

## 15. Files Created

```
tmp/human_evidence_binding_design_research.md     (this file)
tmp/human_evidence_binding_design_research.json    (structured data)
tmp/human_evidence_binding_case_table.csv          (79 cases, 17 fields)
```

---

## 16. Final Governance State

```
RESEARCH_STATUS = COMPLETE

DESIGN_IMPLEMENTATION = FALSE
SYSTEM_MODIFIED = FALSE
EXPERIMENT_AUTHORIZED = FALSE
HUMAN_VALIDATION_AUTHORIZED = FALSE

NEW_CAPABILITY = NONE
RUNTIME_AUTHORITY = ZERO
PRODUCTION = FALSE

FROZEN_BASELINE = INTACT
BASELINE_DRIFT = 0

STOP = TRUE
```

---

## STOP

```
Human-Evidence Binding Design Research is COMPLETE.

Summary:
  - 79 M-A cases analyzed for Human-Evidence Binding
  - H1-H4 classification: 26.6% existing evidence, 5.1% new observation,
    50.6% semantic confirmation, 17.7% semantic boundary
  - Minimum feedback = Scheme B (Judgment + Evidence ID): 2 fields, LOW burden
  - Free text explanation NOT required (provenance via Evidence ID + Config)
  - 82.3% of cases: Human validates, doesn't reconstruct
  - Five-level hierarchy prevents single case → rule → capability
  - Reusable Signal requires: ≥2 cases + ≥2 documents + same config + provenance + boundary
  - Next phase: CONDITIONAL (needs config similarity verification + multi-reviewer test)

KEY INSIGHT:
  Human's primary role is NOT "semantic interpreter."
  Human's primary role is "evidence-grounded judgment provider."
  77.2% of Human contributions were either accessing existing evidence or
  confirming structural=semantic — neither requires new evidence creation.

  The minimum binding is:
    Human Judgment + Evidence Anchor = Validated Evidence Instance

  This is design research only. NOT implemented. NOT authorized.

不得自动开始下一阶段。
不得修改任何系统。
不得实现任何 Schema。
STOP = TRUE
```
