# Human Review Reduction / Boundary Expansion Research

> **模式: READ-ONLY / RESEARCH ONLY / NO CODE / NO IMPLEMENTATION / NO NEW HUMAN VALIDATION / STOP**
> 日期: 2026-09-19
> Gate: HUMAN_REVIEW_REDUCTION_BOUNDARY_EXPANSION_RESEARCH
> 前置: Boundary Handoff Learning Research (COMPLETE, 4 patterns at B2)
> 本文件: 研究 Human Semantic Judgment 能否产生新的、可验证、可复用 Evidence，从而真正扩展 DICE 的自动化 Boundary，减少未来 Human Review。

---

## 0. Core Question

```
Human Semantic Judgment 能否产生新的、可验证、可复用 Evidence，
从而真正扩展 DICE 的自动化 Boundary，并在未来案例中减少 Human Review？

最终目标不是 "Human Review 更高效"。
最终目标是 "Human Review 是否可以随着 Evidence Learning 而逐步减少"。

成功标准只有一个：
Human Review ↓，而不是 Human Review 做得更舒服。
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
STOP = TRUE
```

---

## 2. Data Used

```
18 E4 genuine G5 cases (from Evidence Boundary Expansion Research)
  - 10 CAPTION_VS_REFERENCE
  - 4 TEXT_ROLE_AMBIGUITY
  - 2 AUTHOR_NAME_RECOGNITION
  - 2 COLUMN_SEMANTIC_TYPE

Boundary Handoff Learning Research (4 patterns, all at B2)
CE2 pair (decisive counterexample)
M-A 79-case Human Validation
Evidence Boundary Structure Research (13 G5 cases)
```

---

## 3. Human Contribution Classification (A–E)

### 3.1 Framework

```
A = ANSWER_ONLY: Human just gave yes/no (no evidence discovery)
B = NEW_EVIDENCE_CANDIDATE: Human found verifiable document evidence
C = EVIDENCE_RELATION_CANDIDATE: Human found new relation between existing evidence
D = EXTERNAL_KNOWLEDGE: Human used document-external knowledge
E = IRREDUCIBLE_SEMANTIC_JUDGMENT: No new evidence, just semantic understanding
```

### 3.2 Results (18 E4 cases)

| Contribution Type | Count | % | Description |
|-------------------|------:|---:|-------------|
| A_ANSWER_ONLY | 0 | 0% | No case was purely answer without reasoning |
| B_NEW_EVIDENCE_CANDIDATE | 2 | 11.1% | Column header/table title (P4) |
| C_EVIDENCE_RELATION_CANDIDATE | 2 | 11.1% | Page section context (P3) |
| D_EXTERNAL_KNOWLEDGE | 0 | 0% | No case was purely external knowledge |
| **E_IRREDUCIBLE_SEMANTIC_JUDGMENT** | **14** | **77.8%** | **No new evidence discovered** |

```
KEY FINDING:
  77.8% of G5 cases (14/18) are E_IRREDUCIBLE_SEMANTIC_JUDGMENT.
  → Human did NOT discover any new verifiable evidence.
  → Human used semantic understanding of existing evidence.
  → The text was already in local context (ctx=5).
  → Human's contribution was INTERPRETATION, not DISCOVERY.

  22.2% (4/18) have PARTIAL evidence candidates:
  → 2 cases (P4 COLUMN_TYPE): column header may help (B_NEW_EVIDENCE_CANDIDATE)
  → 2 cases (P3 AUTHOR_NAME): page section context may help (C_EVIDENCE_RELATION_CANDIDATE)
  → BUT: even these are CONDITIONAL and PARTIALLY machine-verifiable.

  0% (0/18) have SUPPORTED boundary expansion.
  → No case has evidence that fully resolves the boundary without Human.
```

---

## 4. Answer vs Evidence Distinction (Q1–Q2)

### 4.1 What Did Human Actually Contribute?

```
For each G5 case, analyzed whether Human's judgment was based on:

  (a) ANSWER: "This is a caption / reference / axis label / row number"
      → Pure semantic judgment, no new evidence.
      → Cannot be reused by machine.

  (b) NEW EVIDENCE: "The document says 'Fig. 3 shows...' / header says 'Accuracy'"
      → Document-internal evidence that Machine could re-observe.
      → Potentially reusable.

  (c) EVIDENCE RELATION: "This text is in the reference list section"
      → Relation between existing evidence items.
      → Potentially reusable.

  (d) EXTERNAL KNOWLEDGE: "Le. is a common Chinese surname"
      → Document-external knowledge.
      → Not reusable as DICE evidence.

  (e) IRREDUCIBLE SEMANTIC: "The text reads like it's describing the figure"
      → Semantic interpretation, not evidence.
      → Cannot be reused.
```

### 4.2 Detailed Analysis by Pattern

```
P1: CAPTION_VS_REFERENCE (10 cases) — E_IRREDUCIBLE
  Human's process:
    → Received: text + drawing extent + spatial relation + local context (ctx=5)
    → The text was ALREADY in the Evidence Pack.
    → Human READ the text and UNDERSTOOD its semantic role.
    → "This text says 'Fig. 3 shows the architecture...' → it's a caption"
    → "This text says 'as shown in Fig. 3b' → it's an in-text reference"

  Did Human discover NEW evidence?
    → NO. The text was already provided.
    → Human's contribution was SEMANTIC READING of existing text.
    → The "Fig. 3 shows" and "as shown in Fig. 3b" patterns were in ctx=5.
    → Human interpreted these patterns, didn't discover them.

  Is this Answer or Evidence?
    → ANSWER (semantic judgment based on existing evidence).
    → NOT new evidence.
    → Cannot be machine-verified without semantic understanding.

P2: TEXT_ROLE_AMBIGUITY (4 cases) — E_IRREDUCIBLE
  Human's process:
    → Received: short text ("scaling", "omit", "max", ", with") + drawing + spatial
    → Human determined: is this an axis label, annotation, or body text?
    → Required: understanding what the text MEANS in context of the figure.

  Did Human discover NEW evidence?
    → NO. Text and position were already provided.
    → Human's contribution was SEMANTIC ROLE DETERMINATION.
    → Cannot be machine-verified without understanding text's function.

P3: AUTHOR_NAME_RECOGNITION (2 cases) — C_EVIDENCE_RELATION_CANDIDATE (PARTIAL)
  Human's process:
    → Received: text pair with period+capital pattern.
    → Human determined: is "Le." a surname or sentence fragment?
    → POTENTIAL new evidence: page section (body text vs reference list).
    → This relation EXISTS in document structure but NOT in Evidence Pack.

  Did Human discover NEW evidence?
    → PARTIALLY YES: page section context is a new evidence relation.
    → BUT: author-name recognition ALSO requires external world knowledge.
    → Page section is machine-verifiable (C1=YES, C2=YES).
    → Author-name recognition is NOT machine-verifiable (C4=YES).
    → Even with page section, some cases remain G5 (need world knowledge).

P4: COLUMN_SEMANTIC_TYPE (2 cases) — B_NEW_EVIDENCE_CANDIDATE (PARTIAL)
  Human's process:
    → Received: numeric column with alignment evidence.
    → Human determined: are these row-numbers or data values?
    → POTENTIAL new evidence: column header or table title.
    → This may EXIST in document but NOT in Evidence Pack.

  Did Human discover NEW evidence?
    → PARTIALLY YES: column header is potential new evidence.
    → BUT: header may itself be ambiguous (e.g., "Index" could mean row-number or index value).
    → Even with header, some cases may remain G5 (need semantic understanding of what numbers mean).
    → Column header is machine-verifiable IF it exists (C1=PARTIAL, C2=YES).

CE2 PAIR (2 cases) — E_IRREDUCIBLE
  Human's process:
    → Received: IDENTICAL structural evidence (FIG+EXTENT+spatial+context).
    → Human READ the text content and made different judgments.
    → CE2-NO: text content indicates NOT a caption.
    → CE2-YES: text content indicates IS a caption.

  Did Human discover NEW evidence?
    → NO. ALL evidence was identical.
    → The difference was in SEMANTIC CONTENT of the text.
    → Human's contribution was semantic reading, not evidence discovery.
    → CE2 CONFIRMS: no new evidence can explain the judgment difference.
```

---

## 5. Machine Verifiability (Q3)

### 5.1 C1–C6 Check for New Evidence Candidates

```
For the 4 cases with evidence candidates (P3 + P4):

P3: PAGE_SECTION_CONTEXT (2 cases)
  C1 (exists in document?): YES — page structure exists in P1 output.
  C2 (expressible in existing Evidence?): YES — can be derived from page structure.
  C3 (needs new Observation?): NO — page structure already observed.
  C4 (depends on Human semantic interpretation?): PARTIAL — section classification is structural, but author-name is semantic.
  C5 (independently verifiable by second case?): YES — page section can be checked.
  C6 (cross-document recurrence?): CONDITIONAL — only 1 document tested.

  Classification: DERIVABLE_EVIDENCE (page section) + SEMANTIC_ONLY (author-name)
  → Page section is machine-verifiable.
  → Author-name recognition is NOT machine-verifiable (needs world knowledge).
  → PARTIAL: page section helps but doesn't fully resolve.

P4: COLUMN_HEADER (2 cases)
  C1 (exists in document?): PARTIAL — header may or may not exist for every table.
  C2 (expressible in existing Evidence?): YES — if header is extracted, it's text evidence.
  C3 (needs new Observation?): NO — header is text, already observed by P1.
  C4 (depends on Human semantic interpretation?): PARTIAL — header text may be ambiguous.
  C5 (independently verifiable?): YES — header text can be checked.
  C6 (cross-document recurrence?): YES — 2 documents tested.

  Classification: VERIFIABLE_EXISTING_EVIDENCE (if header exists) + SEMANTIC_ONLY (if header is ambiguous)
  → Column header is machine-verifiable IF it exists and is unambiguous.
  → But header may not exist or may be ambiguous.
  → PARTIAL: header helps but doesn't fully resolve.
```

### 5.2 Verifiability Distribution

| Verifiability | Count | % |
|--------------|------:|---:|
| NO (semantic interpretation) | 10 | 55.6% |
| NO (semantic role determination) | 4 | 22.2% |
| PARTIAL (page section + external) | 2 | 11.1% |
| PARTIAL (column header if exists) | 2 | 11.1% |
| YES (fully machine-verifiable) | 0 | 0% |

```
0/18 cases have FULLY machine-verifiable new evidence.
4/18 have PARTIALLY machine-verifiable candidates.
14/18 have NO machine-verifiable evidence (semantic only).

→ The vast majority (77.8%) of G5 cases have NO machine-verifiable new evidence.
→ Even the 4 PARTIAL cases cannot be fully resolved by machine.
→ The evidence candidates (page section, column header) help but don't eliminate G5.
```

---

## 6. Boundary Expansion Assessment (Q4–Q5)

### 6.1 Strict Criteria

```
BOUNDARY_EXPANSION_SUPPORTED requires ALL of:
  1. Human discovered Evidence
  2. Evidence is independently verifiable
  3. Evidence was not already available
  4. Evidence is reusable in another case
  5. Evidence can change future machine resolvability
```

### 6.2 Results

| Boundary Expansion | Count | % |
|---------------------|------:|---:|
| NOT_SUPPORTED | 14 | 77.8% |
| CONDITIONAL | 4 | 22.2% |
| SUPPORTED | 0 | 0% |

```
0/18 cases have SUPPORTED boundary expansion.
  → No case has evidence that fully resolves the boundary without Human.

4/18 cases are CONDITIONAL:
  → P3 (2 cases): page section may help partially (but author-name still needs Human).
  → P4 (2 cases): column header may help (but may not exist or be ambiguous).
  → Even these CONDITIONAL cases cannot fully resolve G5.

14/18 cases are NOT_SUPPORTED:
  → No new verifiable evidence discovered.
  → Human's contribution was irreducible semantic judgment.
  → G5 boundary remains.
```

### 6.3 Cross-Case Recurrence

```
For the 4 evidence candidates, checked cross-case recurrence:

  P3 (page section context): 2 cases, 1 document
    → Cross-case: YES (2 cases share same evidence need)
    → Cross-document: NO (only 1 document)
    → NOT sufficient for reusable pattern.

  P4 (column header): 2 cases, 2 documents
    → Cross-case: YES (2 cases share same evidence need)
    → Cross-document: YES (2 documents)
    → CONDITIONAL for reusable pattern (but only 2 cases).

  P1 (caption vs reference): 10 cases, 3 documents
    → Cross-case: YES, Cross-document: YES
    → BUT: E_IRREDUCIBLE — no new evidence to reuse.
    → Pattern is reusable for REQUIREMENT, not for EXPANSION.

  P2 (text role ambiguity): 4 cases, 3 documents
    → Cross-case: YES, Cross-document: YES
    → BUT: E_IRREDUCIBLE — no new evidence to reuse.
    → Pattern is reusable for REQUIREMENT, not for EXPANSION.

CONCLUSION:
  No evidence candidate has sufficient cross-case + cross-document + full verifiability
  to qualify as a Reusable Boundary Expansion Pattern.
```

---

## 7. CE2 Special Analysis (Q9)

### 7.1 The Questions

```
Q9.1: Did Human discover different New Evidence in the two CE2 cases?
  → NO. Both cases have E_IRREDUCIBLE_SEMANTIC_JUDGMENT.
  → Both: new_evidence_candidate = NONE.
  → Human did NOT discover any new evidence in either case.

Q9.2: If no new evidence, does different Judgment come from Semantic Content?
  → YES. The difference is in the text's semantic content.
  → CE2-NO: text content semantically indicates "not a caption" (e.g., in-text reference pattern).
  → CE2-YES: text content semantically indicates "is a caption" (e.g., descriptive pattern).
  → Both texts had IDENTICAL structural evidence (FIG+EXTENT+spatial+context).
  → The differentiator was the SEMANTIC MEANING of the text, not any new evidence.

Q9.3: If new evidence exists, is it machine-verifiable?
  → N/A. No new evidence was discovered.
  → The differentiator (semantic content) is NOT machine-verifiable.

Q9.4: Can new evidence explain why original evidence looked identical but was incomplete?
  → NO. The original evidence was NOT incomplete.
  → ALL structural evidence was complete and identical.
  → The "incompleteness" is not in evidence quantity but evidence TYPE:
    structural evidence cannot capture semantic content.
  → This IS the G5 boundary: structural evidence has a genuine ceiling.
```

### 7.2 CE2 Conclusion

```
CE2 DEFINITIVELY CONFIRMS:

  1. No new evidence was discovered in either case.
  2. Different judgments came from semantic content of the text.
  3. The semantic content is NOT machine-verifiable (requires semantic understanding).
  4. The original evidence was NOT incomplete — it was at its structural ceiling.
  5. G5 boundary CANNOT be expanded by evidence discovery.

  CE2 is the DECISIVE proof that:
  → G5 is a genuine semantic boundary, not an evidence deficiency.
  → Human's contribution at G5 is semantic judgment, not evidence discovery.
  → No amount of additional structural evidence can resolve the boundary.
  → Human Review CANNOT be reduced for these cases.
```

---

## 8. Review Reduction Level (Q6)

### 8.1 Level Distribution

| Level | Count | % | Description |
|-------|------:|---:|-------------|
| L0 (not reusable) | 14 | 77.8% | Human judgment not reusable; no evidence discovery |
| L1 (evidence found, insufficient) | 4 | 22.2% | Evidence discovered but insufficient for automatic resolution |
| L2 (potential reduction) | 0 | 0% | Evidence sufficient for future machine resolution |
| L3 (machine resolvable) | 0 | 0% | Machine can resolve without Human |

```
0/18 cases achieve L2 or L3.
  → No case has evidence sufficient to reduce Human Review.
  → Human Review CANNOT be reduced for any G5 case.

4/18 cases at L1:
  → Evidence candidates exist (page section, column header).
  → But insufficient for automatic resolution.
  → May improve Human Handoff (better evidence preparation).
  → But do NOT eliminate need for Human semantic judgment.

14/18 cases at L0:
  → No evidence discovery at all.
  → Human judgment is purely semantic.
  → Cannot be reused in any form.
  → Human Review is IRREDUCIBLE for these cases.
```

### 8.2 Human Review Reduction Assessment

```
POTENTIAL_HUMAN_REVIEW_REDUCTION = NO

  0/18 cases can achieve L2 (potential reduction).
  0/18 cases can achieve L3 (machine resolvable).

  The 4 L1 cases may improve Human Handoff (B2→B3 in boundary level terms):
  → DICE could prepare page section context or column header.
  → Human would have better evidence to work with.
  → But Human STILL must make the final semantic judgment.
  → This is Handoff Improvement, NOT Review Reduction.

  HUMAN_REVIEW_REDUCTION = NOT_SUPPORTED
  HUMAN_HANDOFF_IMPROVEMENT = CONDITIONAL (for 4/18 cases only)
```

---

## 9. Result Classification (Q10)

### 9.1 A/B/C Distribution

```
RESULT A (Human Answer — not reusable):
  14/18 (77.8%)
  → Human gave semantic judgment without discovering new evidence.
  → Cannot be reused by machine.
  → Human Review remains necessary.

RESULT B (Human Evidence Discovery — possibly reusable):
  4/18 (22.2%)
  → Human identified potential new evidence (page section, column header).
  → May improve future Human Handoff.
  → But insufficient for automatic resolution.
  → Cannot reduce Human Review.

RESULT C (Human Evidence Discovery → Future Machine Resolution):
  0/18 (0%)
  → No case has evidence that could make future cases machine-resolvable.
  → G5 boundary cannot be expanded to eliminate Human Review.

SUMMARY:
  A = 14 (77.8%) — Answer only, not reusable
  B = 4 (22.2%) — Evidence discovery, possibly reusable for Handoff
  C = 0 (0%) — No true Boundary Expansion
```

---

## 10. The Four-Layer Convergence

```
This research completes a four-layer convergence on the G5 boundary:

  Layer 1: Evidence Boundary Structure Research
    → 13 G5 cases: STRUCTURAL_EVIDENCE_NOT_SUFFICIENT.
    → Structural evidence has a ceiling.

  Layer 2: Evidence Configuration Family Research (CE2)
    → Identical structural evidence → different Human judgment.
    → EVIDENCE_FAMILY_CANNOT_DETERMINE_JUDGMENT = TRUE.

  Layer 3: Evidence Boundary Expansion Research
    → 18/29 E4: no structural evidence expansion can help.
    → 62.1% genuine G5.

  Layer 4: Human Review Reduction Research (this study)
    → 77.8% E_IRREDUCIBLE: Human discovered no new evidence.
    → 0% BOUNDARY_EXPANSION_SUPPORTED.
    → 0% POTENTIAL_HUMAN_REVIEW_REDUCTION.
    → CE2 confirms: no new evidence, different judgment = semantic content.

  FOUR-LAYER CONVERGENCE:
  All four independent research paths confirm:
  → G5 is a genuine, irreducible semantic boundary.
  → Structural evidence has a ceiling that cannot be crossed.
  → Human semantic judgment is irreducible.
  → Human Review cannot be reduced for G5 cases.
  → The boundary is a PROPERTY of the task, not a deficiency of the system.

  IMPLICATION:
  DICE should ACCEPT the G5 boundary.
  Human Review for G5 cases is PERMANENT, not reducible.
  The goal should be:
  → Efficient Human Handoff (B2 → B3: prepare better evidence for Human).
  → NOT Human Review Reduction (L2/L3: eliminate Human).
  → These are DIFFERENT goals:
    Handoff Improvement = make Human's job easier (CONDITIONAL, 4/18 cases).
    Review Reduction = eliminate Human's job (NOT_SUPPORTED, 0/18 cases).
```

---

## 11. Over-Design Audit

```
  O1: Human Answer → Rule? → NO
  O2: Human Answer → Label? → NO
  O3: New Semantic Detector? → NO
  O4: New Observation? → NO (identified need but didn't implement)
  O5: New Schema? → NO
  O6: New Evidence Field? → NO
  O7: One-Case-One-Patch? → NO (4 patterns, not 18 patches)
  O8: New Capability? → NO
  O9: New Runtime? → NO
  O10: Human Validation performed? → NO

  ALL CHECKS: FALSE
  OVER_DESIGN_AUDIT = PASS
```

---

## 12. Limitations

```
  HRR-L-01: SINGLE HUMAN REVIEWER
    All judgments from one reviewer.
    Evidence discovery may differ with other reviewers.

  HRR-L-02: NO IMPLEMENTATION TEST
    B_CANDIDATE and C_CANDIDATE are theoretical.
    Actual machine verifiability unverified.

  HRR-L-03: L1 CASES ARE PARTIAL
    Even the 4 L1 cases cannot fully resolve G5.
    Page section helps but author-name still needs world knowledge.
    Column header helps but may be ambiguous.

  HRR-L-04: NO HUMAN TIME DATA
    Cannot claim actual review time.
    "Review reduction" is structural analysis, not measurement.

  HRR-L-05: CE2 IS SINGLE INSTANCE
    CE2 is decisive but one pair.
    More pairs would strengthen the finding.

  HRR-L-06: SAME DOMAIN
    All cases from academic papers.
    Cross-domain review reduction untested.

  HRR-L-07: NO NEW HUMAN VALIDATION
    Cannot verify whether a different Human would discover different evidence.
    Evidence discovery is reviewer-specific.
```

---

## 13. Final Questions

### Q1: 18 个 G5 中，Human 贡献的主要是 Answer 还是 New Evidence？

```
ANSWER (Irreducible Semantic Judgment): 14/18 (77.8%)

  The MAJORITY of Human contributions are pure semantic judgments.
  Human did NOT discover new verifiable evidence in 77.8% of cases.
  Human READ existing evidence and INTERPRETED it semantically.
  This is Answer (semantic judgment), not Evidence (verifiable discovery).
```

### Q2: 有多少是真正 New Evidence？

```
4/18 (22.2%) — PARTIAL only.

  2 B_NEW_EVIDENCE_CANDIDATE (column header, P4).
  2 C_EVIDENCE_RELATION_CANDIDATE (page section, P3).

  These are PARTIAL:
  → Column header may not exist or may be ambiguous.
  → Page section helps but author-name needs world knowledge.
  → Neither fully resolves the boundary.
```

### Q3: 这些 New Evidence 有多少可机器验证？

```
0/18 FULLY machine-verifiable.
4/18 PARTIALLY machine-verifiable.

  P3: page section is machine-verifiable, but author-name is NOT.
  P4: column header is machine-verifiable IF it exists and is unambiguous.

  No new evidence candidate is FULLY machine-verifiable.
  Even the partial candidates cannot fully resolve G5.
```

### Q4: 有多少可以跨案例复用？

```
2/4 evidence candidates have cross-case recurrence:
  P3 (page section): 2 cases, 1 document — cross-case YES, cross-doc NO.
  P4 (column header): 2 cases, 2 documents — cross-case YES, cross-doc YES.

  BUT: both are PARTIAL and cannot fully resolve G5.
  Cross-case recurrence ≠ cross-case resolution.
```

### Q5: 有没有真正的 Boundary Expansion？

```
NO.

  BOUNDARY_EXPANSION_SUPPORTED: 0/18 (0%).
  BOUNDARY_EXPANSION_CONDITIONAL: 4/18 (22.2%).
  BOUNDARY_EXPANSION_NOT_SUPPORTED: 14/18 (77.8%).

  No case has evidence that fully expands the boundary.
  The 4 CONDITIONAL cases only partially help.
  G5 boundary remains for all 18 cases.
```

### Q6: 有没有 Potential Human Review Reduction？

```
NO.

  L0 (not reusable): 14/18 (77.8%).
  L1 (evidence found, insufficient): 4/18 (22.2%).
  L2 (potential reduction): 0/18 (0%).
  L3 (machine resolvable): 0/18 (0%).

  POTENTIAL_HUMAN_REVIEW_REDUCTION = NOT_SUPPORTED.
  HUMAN_HANDOFF_IMPROVEMENT = CONDITIONAL (4/18 cases only).
```

### Q7: 有没有一个 Case 可以从 Human Required 变成 Machine Resolvable？

```
NO.

  0/18 cases have evidence that could make future cases machine-resolvable.
  The 4 L1 cases have evidence candidates, but:
  → P3: page section + external knowledge (still needs Human).
  → P4: column header IF exists + IF unambiguous (still may need Human).
  → Neither achieves L2 or L3.

  No G5 case can transition from Human-Required to Machine-Resolvable.
```

### Q8: CE2 是否存在可验证的 New Evidence 差异？

```
NO.

  CE2-NO: E_IRREDUCIBLE_SEMANTIC_JUDGMENT, new_evidence = NONE.
  CE2-YES: E_IRREDUCIBLE_SEMANTIC_JUDGMENT, new_evidence = NONE.

  Both cases: NO new evidence discovered.
  Different judgments came from semantic content of the text.
  The semantic content is NOT machine-verifiable.
  Original evidence was NOT incomplete — it was at its structural ceiling.

  CE2 DEFINITIVELY CONFIRMS:
  → G5 cannot be expanded by evidence discovery.
  → Human's contribution is semantic judgment, not evidence.
  → Human Review is irreducible for these cases.
```

### Q9: Human Feedback 最终更接近 Answer Learning 还是 Evidence Learning？

```
ANSWER LEARNING — for 77.8% of G5 cases.

  14/18 cases: Human provided ANSWER (semantic judgment), not EVIDENCE.
  → This is closer to Answer Learning than Evidence Learning.
  → Answer Learning is FORBIDDEN (cannot learn Human's answer).
  → Therefore: 77.8% of G5 Human feedback CANNOT be safely used.

  4/18 cases: Human provided PARTIAL Evidence (B/C candidates).
  → This is closer to Evidence Learning.
  → But the evidence is PARTIAL and cannot fully resolve G5.
  → Evidence Learning is ALLOWED but INSUFFICIENT.

  OVERALL:
  Human Feedback at G5 is predominantly ANSWER, not EVIDENCE.
  → Answer Learning is forbidden.
  → Evidence Learning is insufficient.
  → Neither path can reduce Human Review.

  The correct interpretation:
  Human's feedback at G5 is SEMANTIC JUDGMENT (Answer).
  This judgment is irreducible.
  It cannot be converted to Evidence.
  It cannot be converted to Rule.
  It cannot be converted to Capability.
  → Human Review for G5 is PERMANENT.
```

### Q10: 下一阶段应该 STOP 还是 DESIGN_RESEARCH 还是 EXPERIMENT_DESIGN？

```
STOP.

  REASONING:
  1. 77.8% of G5 cases are IRREDUCIBLE — no evidence discovery.
  2. 0% have SUPPORTED boundary expansion.
  3. 0% have POTENTIAL_HUMAN_REVIEW_REDUCTION.
  4. CE2 definitively confirms: no new evidence, different judgment = semantic.
  5. Four-layer convergence: all research paths confirm G5 is irreducible.
  6. Human Feedback at G5 is predominantly ANSWER, not EVIDENCE.
  7. Answer Learning is FORBIDDEN.
  8. Evidence Learning is INSUFFICIENT (only 22.2% partial, 0% full).

  The G5 boundary is a PROPERTY of the task:
  → Structural evidence has a genuine ceiling.
  → Semantic identity cannot be determined from structure.
  → Human semantic judgment is irreducible.
  → Human Review for G5 is PERMANENT.

  WHAT WAS LEARNED (cumulative across all research):
  → G5 is genuine (4-layer convergence).
  → Human's contribution at G5 is semantic judgment (77.8% irreducible).
  → 4 Handoff Pattern Candidates exist (for REQUIREMENT, not ANSWER).
  → 4 evidence candidates exist (PARTIAL, cannot fully resolve).
  → Human Review cannot be reduced for G5.
  → Human Handoff can be CONDITIONALLY improved (4/18 cases, B2→B3).

  WHAT WOULD BE NEEDED TO CONTINUE:
  → Implement B3 evidence preparation (NOT authorized).
  → Multi-reviewer validation (NOT authorized).
  → Cross-domain testing (NOT authorized).
  → New Human Experiment (NOT authorized).

  NONE possible in READ-ONLY mode.
  → STOP.

  FINAL PRINCIPLE:
  The goal was "Human Review ↓".
  The finding is "Human Review = PERMANENT for G5".
  This is NOT a failure. It is a fundamental property.
  DICE should:
  → Automate G1-G4 (where evidence is sufficient).
  → Hand off G5 to Human (where evidence has ceiling).
  → Prepare evidence efficiently for Human (B2→B3, CONDITIONAL).
  → NOT attempt to eliminate Human at G5 (FORBIDDEN).
```

---

## 14. Files Created

```
tmp/human_review_reduction_research.md          (this file)
tmp/human_review_reduction_research.json         (structured data)
tmp/human_review_reduction_case_table.csv        (18 cases, 13 fields)
```

---

## 15. Final Governance State

```
RESEARCH_STATUS = COMPLETE

SYSTEM_MODIFIED = FALSE
IMPLEMENTATION_AUTHORIZED = FALSE
EXPERIMENT_AUTHORIZED = FALSE
HUMAN_VALIDATION_AUTHORIZED = FALSE

FROZEN_BASELINE = INTACT
BASELINE_DRIFT = 0

NEW_FIELD = NONE
NEW_SCHEMA = NONE
NEW_OBSERVATION = NONE
NEW_RULE = NONE
NEW_DETECTOR = NONE
NEW_SIGNAL = NONE
NEW_CAPABILITY = NONE

RUNTIME_AUTHORITY = ZERO
PRODUCTION = FALSE

STOP = TRUE
```

---

## STOP

```
Human Review Reduction / Boundary Expansion Research is COMPLETE.

SUMMARY:
  - 18 E4 genuine G5 cases analyzed for Human Review Reduction potential
  - Human Contribution: 77.8% IRREDUCIBLE_SEMANTIC_JUDGMENT, 22.2% PARTIAL evidence
  - BOUNDARY_EXPANSION_SUPPORTED: 0/18 (0%)
  - POTENTIAL_HUMAN_REVIEW_REDUCTION: 0/18 (0%)
  - L0 (not reusable): 14/18 (77.8%)
  - L1 (insufficient evidence): 4/18 (22.2%)
  - L2/L3 (reduction/resolution): 0/18 (0%)
  - CE2: NO new evidence, different judgment = semantic content
  - Human Feedback at G5: predominantly ANSWER, not EVIDENCE

FOUR-LAYER CONVERGENCE:
  Layer 1: STRUCTURAL_EVIDENCE_NOT_SUFFICIENT (13 G5 cases)
  Layer 2: EVIDENCE_FAMILY_CANNOT_DETERMINE_JUDGMENT (CE2)
  Layer 3: 62.1% genuine G5, no expansion possible
  Layer 4: 77.8% irreducible, 0% review reduction

FINAL FINDING:
  G5 is a genuine, irreducible semantic boundary.
  Human Review for G5 is PERMANENT, not reducible.
  Human Feedback at G5 is predominantly Answer, not Evidence.
  Answer Learning is FORBIDDEN.
  Evidence Learning is INSUFFICIENT.

  DICE should:
  → Automate G1-G4 (evidence sufficient).
  → Hand off G5 to Human (evidence ceiling).
  → Prepare evidence efficiently (B2→B3, CONDITIONAL, 4/18 cases).
  → NOT attempt to eliminate Human at G5.

  The goal "Human Review ↓" is NOT achievable for G5.
  The achievable goal is "Human Handoff Improvement" (CONDITIONAL).
  These are DIFFERENT goals.

  不得自动进入 Implementation。
  不得创建任何 Rule / Signal / Capability。
  不得把 Answer 当作 Evidence。
  不得把 Handoff Improvement 当作 Review Reduction。
  STOP = TRUE
```
