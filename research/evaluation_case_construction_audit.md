# DICE Evaluation Case Construction Audit

**Date**: 2026-09-12
**Mode**: READ-ONLY, DESIGN-ONLY, AUDIT-ONLY
**Scope**: Audit current 45-case selection pipeline and define future Evaluation Case Construction principles
**Trigger**: P722 formal experiment revealed ceiling effect — 84% of cases are trivially separable table cells/headers

---

## A. Current State

### Candidate → Case Pipeline

```
4 PDFs / 60 pages
    ↓ P1-P6 (frozen perception layers)
9,397 same-Y coordinate text pairs
    ↓ Geometric ambiguity filter (h_gap 8-50pt, w_b ≥15pt, line_obs ≤15)
545 "ambiguous" candidates
    ↓ Stratified random sampling (by h_gap bin, w_b bin, line_obs bin, doc_id)
45 sampled cases
    ↓ Human GT (2 reviewers + adjudication)
45 GT-annotated cases (43 KEEP_SEPARATE, 2 MERGE)
```

### Selection Objective (Actual)

The sampling frame metadata explicitly states:

```json
"sampling_rule": "stratified random sampling (geometry-only stratification)",
"stratification_note": "ALL stratification dimensions are geometric.
  NO IS-11, IS-01, IS-02, text content, or human intuition used."
```

The candidate universe metadata confirms:

```json
"ambiguous_criteria": {
    "gap_min": 8.0,      // horizontal gap between text spans
    "gap_max": 50.0,
    "line_obs_max": 15,
    "wb_min": 15.0       // minimum width of text_b
}
```

### What Was Optimized

The pipeline optimizes for **geometric proximity** — pairs of text spans that are close together horizontally on the same line. This is appropriate for testing the geometric perception layer's ability to distinguish adjacent structural elements, but it does NOT optimize for semantic judgment difficulty.

---

## B. Failure Diagnosis

### Why Geometric Ambiguity ≠ Human Semantic Difficulty

**Root cause**: Tables contain many closely-spaced cells on the same line. The geometric filter (h_gap 8-50pt) therefore overwhelmingly selects table-adjacent pairs, not semantically ambiguous pairs.

### 545 Candidate Pool Distribution

| Family | Count | % | Typical Example |
|---|---|---|---|
| TABLE_CELL (both numeric) | 252 | 46% | `'28.54' / '10.02'` |
| TABLE_HEADER (short text) | 205 | 38% | `'Resolution' / '#Channels'` |
| PROSE (sentence fragments) | 66 | 12% | `'degrades rapidly.' / 'Unexpectedly,'` |
| FIGURE (caption/label) | 11 | 2% | `'FIG. 9:' / 'Left:'` |
| OTHER | 11 | 2% | — |

**84% of candidates are table-adjacent pairs** — geometrically close but semantically trivial.

### 45 Sampled Case Distribution

| Family | Count | GT | Evaluation Value |
|---|---|---|---|
| TABLE_CELL | 28 | all KEEP_SEPARATE | LOW |
| TABLE_HEADER | 7 | all KEEP_SEPARATE | LOW |
| AXIS_LABEL | 3 | all KEEP_SEPARATE | LOW |
| PROSE_SENTENCE | 4 | all KEEP_SEPARATE | MEDIUM |
| FIGURE_CAPTION | 2 | all MERGE | MEDIUM |
| OTHER | 1 | KEEP_SEPARATE | UNKNOWN |

### GT Distribution

```
KEEP_SEPARATE: 43/45 (96%)
MERGE:          2/45 (4%)
```

### SELECTION_OBJECTIVE_MISMATCH

The geometric ambiguity filter selects cases where the **system** has difficulty (close geometric proximity), not where the **Human** has difficulty (ambiguous semantic boundary). These are different problems:

- **System difficulty**: "Are these two adjacent spans in the same structural unit?" → needs geometry/detection
- **Human difficulty**: "Do these two text fragments belong to the same semantic unit?" → needs interpretation

For table cells like `'28.54' / '10.02'`, the system may struggle (they're close), but the Human finds it trivial (two different numbers in different columns = obviously separate).

---

## C. Evaluation Case Definition

### Candidate ≠ Evaluation Case

```
Observation  =  System-detected fact (text span exists at position X)
Candidate    =  System-flagged pair worth considering (geometric proximity met)
Evaluation Case =  Research-question-aligned experimental unit
```

An Evaluation Case must satisfy:
1. **Research question relevance**: The case must test something the research question asks
2. **Decision boundary proximity**: The correct answer must not be obvious to all participants
3. **Evidence sufficiency**: Enough evidence must exist for a Human to potentially reach the correct answer
4. **Plausible alternative**: At least one reasonable alternative interpretation exists
5. **Independence**: Not a near-duplicate of another case

### What Makes a Case "Evaluation-Valuable"

A case has HIGH evaluation value when:
- The structural evidence is **ambiguous or conflicting** (not trivially clear)
- A **plausible alternative interpretation** exists (someone could reasonably argue the opposite)
- The **Cue could plausibly help or mislead** (not irrelevant to the judgment)
- The **decision boundary** between MERGE and KEEP_SEPARATE is genuinely tested

---

## D. Case Quality Dimensions

### Qualitative Tiers (NO numerical weights)

| Dimension | HIGH | MEDIUM | LOW | UNKNOWN |
|---|---|---|---|---|
| **Case Validity** | GT adjudicated, provenance traceable | GT from single reviewer | No GT | — |
| **Case Relevance** | Tests research question directly | Tests related aspect | Trivially answerable | Unclear purpose |
| **Structural Ambiguity** | Multiple plausible interpretations | Some ambiguity, one dominant | Trivially clear | Insufficient evidence to assess |
| **Evidence Sufficiency** | Full evidence available | Partial evidence, enough to judge | Evidence missing or insufficient | Unknown |
| **Case Independence** | Unique document/page/setting | Same page, different content | Near-duplicate of another case | Not checked |
| **Plausible Alternative** | Strong alternative exists | Weak alternative exists | No alternative (obvious) | Unknown |

### Current 45-Case Assessment

| Dimension | HIGH | MEDIUM | LOW | UNKNOWN |
|---|---|---|---|---|
| Case Validity | 45 | 0 | 0 | 0 |
| Case Relevance | 0 | 6 | 38 | 1 |
| Structural Ambiguity | 0 | 11 | 34 | 0 |
| Evidence Sufficiency | 21 | 0 | 9 | 15 |
| Case Independence | 30 | 10 | 5 | 0 |
| Plausible Alternative | 0 | 11 | 34 | 0 |

**Assessment**: Case Validity is strong (all GT adjudicated), but Case Relevance and Structural Ambiguity are overwhelmingly LOW.

---

## E. Case Taxonomy

### Evaluation Coverage Labels (NOT runtime semantic classes)

| Label | Definition | Purpose |
|---|---|---|
| **P** (Positive) | Cue aligns with GT; straightforward case | Test baseline cue speedup |
| **N** (Negative) | Cue absent or irrelevant; case still requires judgment | Test cue doesn't induce errors |
| **B** (Boundary) | Evidence genuinely ambiguous; UNKNOWN acceptable | Test boundary safety |
| **C** (Conflict) | Cue direction ≠ GT (system evidence misleading) | Test override behavior |
| **S** (System≠GT) | System interpretation differs from GT | Test wrong-cue acceptance |
| **U** (UNKNOWN) | Evidence insufficient for definite answer | Test UNKNOWN preservation |

### Structural Family Labels

| Family | Definition | Typical GT |
|---|---|---|
| TABLE_CELL | Two values in different table columns | KEEP_SEPARATE (trivial) |
| TABLE_HEADER | Two column headers in same row | KEEP_SEPARATE (trivial) |
| AXIS_LABEL | Two adjacent axis tick values | KEEP_SEPARATE (trivial) |
| PROSE_SENTENCE | Sentence boundary in running text | KEEP_SEPARATE (ambiguous) |
| FIGURE_CAPTION | Caption label + caption body | MERGE (ambiguous) |
| LIST_ITEM | Two items in a list/diagram | KEEP_SEPARATE (variable) |
| OTHER | Does not fit above categories | Variable |

### Critical Distinction

These labels are **Evaluation Coverage labels** for research design, NOT runtime semantic classes. They must NOT become DICE runtime objects, capabilities, or decision rules.

---

## F. Coverage Matrix

### Current 45-Case Coverage

| Dimension | Covered? | Count | Gap |
|---|---|---|---|
| MERGE | ✗ minimal | 2 | Need more MERGE cases |
| KEEP_SEPARATE | ✓ over-represented | 43 | Excess trivial KEEP |
| UNKNOWN | ✗ absent | 0 | Need UNKNOWN-eligible cases |
| Boundary (genuine) | ✗ minimal | 6 | Need more boundary cases |
| Negative (cue-relevant) | ✗ absent | 0 | Need cue-misleading negatives |
| Conflict (genuine cue≠GT) | ✓ minimal | 2 | AMB-313, AMB-462 |
| Table structure | ✓ over-represented | 35 | Excess table cases |
| Figure/caption | ✗ minimal | 2 | Need more |
| Prose/sentence | ✗ minimal | 4 | Need more |
| Cross-column | ✓ | 35 | Over-represented |
| Caption parts | ✗ minimal | 2 | Need more |
| Spatial association | ✗ absent | 0 | Not tested |

### Target Coverage (Design Goal, NOT Implementation)

| Dimension | Target | Rationale |
|---|---|---|
| MERGE | 20-30% | Must test cue doesn't induce wrong KEEP |
| KEEP_SEPARATE | 30-40% | Must include non-trivial KEEP (not just table cells) |
| UNKNOWN | 10-15% | Must test UNKNOWN preservation |
| Boundary | 15-20% | Must test cue over-clarification risk |
| Conflict | 5-10% | Must test automation bias (WCAR/COR) |
| Table | 20-30% | Reduced from 78% — still represented but not dominant |
| Prose | 20-30% | Increased — genuine semantic ambiguity |
| Figure/caption | 10-15% | MERGE-relevant |
| Cross-document | 4+ docs | Diversity |

---

## G. Difficulty Discovery

### Structural Difficulty vs Human Difficulty

**Structural Difficulty** (observable from evidence):
- Competing structural interpretations exist
- Evidence conflict (TLD says one thing, text patterns suggest another)
- Missing evidence (no TLD, no image)
- Boundary proximity (case sits near MERGE/KEEP decision boundary)
- Multiple plausible structural partitions

**Human Difficulty** (only observable through behavior):
- Decision time
- Evidence expansion count
- Revisit count
- Reviewer disagreement
- UNKNOWN selection rate
- Cross-participant variation

### Critical Principle

> Case Construction can control **Structural Coverage**, but must NOT pre-assume **Human Difficulty** as a known fact.

Circular reasoning to avoid:
```
Human says difficult → label as difficult case → prove Human needs Cue
```

### Difficulty Discovery Loop (Conceptual Design Only)

```
Candidate Pool
    ↓
Structural Coverage Selection (ensure diversity of structural types)
    ↓
Pilot Cases (small initial set, diverse families)
    ↓
Human Behavior Observation (time, expansion, disagreement, UNKNOWN)
    ↓
Observed Difficulty Discovery (which cases were actually hard?)
    ↓
Future Evaluation Set Refinement (add similar cases, remove trivial ones)
```

This is **Evaluation Methodology**, NOT a Learning Engine or Feedback Engine.

---

## H. Evidence Availability

### Current Evidence Availability

| Evidence Type | Available | Missing | Impact |
|---|---|---|---|
| Page image | 30/30 (after fix) | 0 | Fixed in bug-fix v2 |
| TLD is_in_table | 21/30 | 9 | Tier-2 cases lack structural cue |
| TLD different_cell | 21/30 | 9 | Tier-2 cases lack position cue |
| Line spans | 28/30 | 2 | AMB-375/418 lack context |
| Text patterns | varies | — | Computed from P1 text |

### Principle

Evidence availability must be **explicitly recorded per case**. Evidence missing ≠ semantic difficulty — it's a separate dimension that affects Human effort independently.

Future Case Set must record:
```
image_available
TLD_available
Cue_available
structural_evidence_available
```

---

## I. Independence

### Current Independence Issues

| Issue | Finding |
|---|---|
| Document concentration | is11_efficientnet: 18/45 (40%) |
| Page concentration | is11_cs_001 page 3: 8/45 (18%) |
| Family concentration | TABLE_CELL+HEADER: 35/45 (78%) |
| Near-duplicate | Multiple cases from same table, same page |

### Principle

Case count ≠ independent observations. Future Case Set must report:
```
case_count
document_count
page_count
independent_settings (unique doc+page+family combinations)
near_duplicate_groups
```

---

## J. Development / Evaluation / Test Separation

### Risk of Same-Set Iteration

```
Discover failure → adjust system → test on same cases → "success" → false generalization
```

### Proposed Separation (Design Only)

| Set | Purpose | Usage |
|---|---|---|
| **Development Set** | Discover problems, tune Cue wording, debug UI | Can be iterated on |
| **Evaluation Set** | Formal experiment, pre-registered analysis | Frozen before experiment |
| **Independent Test** | Future validation on unseen cases | Not touched until needed |

### Current Status

No separation exists. The same 45 cases serve as both development and evaluation set. The current experiment's analysis contract was written AFTER the cases were seen, which creates potential for confirmation bias.

---

## K. Human Role

### What Human Should Do

| Task | Human | System |
|---|---|---|
| GT adjudication | ✓ | ✗ |
| Semantic validity check | ✓ | ✗ |
| Boundary interpretation | ✓ | ✗ |
| Case relevance judgment | ✓ | ✗ |
| Candidate enumeration | ✗ | ✓ |
| Coverage accounting | ✗ | ✓ |
| Duplication detection | ✗ | ✓ |
| Document/page diversity | ✗ | ✓ |
| Evidence availability check | ✗ | ✓ |
| Structural grouping | ✗ | ✓ |
| Sampling bookkeeping | ✗ | ✓ |

### Principle

> **Human should validate Cases, not reconstruct the entire Evaluation Set from raw candidates.**

System proposes candidate set → Human validates/rejects/adjusts → System does not pre-judge difficulty.

---

## L. System Role

### What System Should Do

1. **Enumerate candidates** from frozen perception output
2. **Group by structural family** (table, prose, figure, etc.)
3. **Check coverage gaps** (which families/conditions are missing?)
4. **Detect near-duplicates** (same page, same table, similar text)
5. **Report evidence availability** per candidate
6. **Propose a balanced candidate set** based on coverage goals
7. **NOT judge semantic difficulty** — that's Human's role

### What System Must NOT Do

- Decide "this case is hard" (Human difficulty is behavioral, not pre-computable)
- Select cases based on GT (that's leakage)
- Modify cases to fit coverage goals (that's fabrication)
- Create new runtime objects for case management

---

## M. Future Case Construction Pipeline

### Design Proposal (NOT Implementation)

```
Step 1: Candidate Pool (existing)
    - Frozen P1-P6 output
    - All same-Y pairs with geometric proximity
    - NO semantic filtering

Step 2: Structural Family Classification
    - System groups candidates by structural family
    - TABLE_CELL, TABLE_HEADER, PROSE, FIGURE, AXIS, LIST, OTHER
    - Based on evidence features (text content, TLD, position)
    - NOT based on GT

Step 3: Research-Question Filter
    - Filter out LOW evaluation value cases
    - Heuristic: exclude pure numeric table cell pairs (trivially separable)
    - Keep: prose boundaries, figure captions, ambiguous structures
    - Keep: cases with plausible alternative interpretation
    - NOT based on GT

Step 4: Coverage Filter
    - Ensure diversity: structural family × GT direction × evidence availability
    - Target distribution (not strict quota):
      - MERGE: 20-30%
      - KEEP_SEPARATE (non-trivial): 30-40%
      - UNKNOWN-eligible: 10-15%
      - Boundary: 15-20%
      - Conflict: 5-10%
    - NOT based on GT (GT assigned AFTER selection)

Step 5: Evidence Sufficiency Check
    - Verify each case has sufficient evidence for Human judgment
    - Record: image_available, TLD_available, Cue_available
    - Flag cases with missing evidence (may be useful for testing, but must be labeled)

Step 6: Diversity / Independence Check
    - No more than N cases from same page
    - No more than M cases from same table
    - Near-duplicate detection (text similarity, position proximity)
    - Cross-document distribution

Step 7: Pilot
    - Small initial set (10-15 cases)
    - Diverse families
    - Human behavior observation
    - NOT for final analysis — for difficulty discovery

Step 8: Human Difficulty Observation
    - Record: decision time, expansion, disagreement, UNKNOWN rate
    - Identify which cases were actually hard (behavioral evidence)
    - NOT pre-assumed difficulty labels

Step 9: Final Evaluation Set
    - Refined based on pilot observations
    - Frozen before formal experiment
    - Pre-registered analysis contract
    - Separate from development set
```

### Key Design Principles

1. **Structural coverage is controllable; Human difficulty is discovered**
2. **GT is assigned AFTER selection, not used FOR selection**
3. **No case fabrication — only filtering and grouping of real candidates**
4. **Pilot before formal — discover difficulty behaviorally**
5. **Development ≠ Evaluation — prevent same-set iteration**

---

## N. Anti-Overdesign Review

### Do We Need These?

| Proposed Module | Needed? | Rationale |
|---|---|---|
| Case Builder module | ✗ NO | Existing scripts + sampling frame sufficient; just needs better filter criteria |
| Difficulty Engine | ✗ NO | Human difficulty is behavioral, discovered through pilot, not pre-computed |
| Semantic Difficulty Classifier | ✗ NO | Structural family classification + plausible-alternative check is sufficient |
| Pattern Engine | ✗ NO | Not relevant to case construction |
| Learning Engine | ✗ NO | Case construction is evaluation methodology, not system learning |
| Feedback Engine | ✗ NO | Human feedback on case quality is manual review, not automated engine |
| Evaluation Runtime | ✗ NO | Existing experiment server is sufficient |

### What IS Needed (Minimal)

1. **Better filter criteria** for the existing sampling pipeline (exclude trivial table cells)
2. **Structural family classification** (can be done with existing P1/TLD output, no new module)
3. **Coverage accounting** (script-level, not runtime)
4. **Near-duplicate detection** (text similarity, script-level)
5. **Pilot-then-formal protocol** (methodology, not code)

All of these can be implemented as **scripts and metadata**, not as DICE runtime modules.

---

## O. Open Questions

| # | Question | Status |
|---|---|---|
| 1 | What structural features distinguish "trivially separable" from "genuinely ambiguous" table cases? | OPEN — needs analysis |
| 2 | How many genuinely ambiguous cases exist in the 545-candidate pool? | ESTIMATED: ~66 prose + 11 figure = ~77, but many may still be trivial |
| 3 | Should the corpus be expanded to include more MERGE-relevant structures? | OPEN — depends on research question scope |
| 4 | Is the 4-PDF corpus sufficient for generalization claims? | NO — exploratory only, needs acknowledgment |
| 5 | Can Human feedback on case quality inform future case selection without becoming a Learning Engine? | YES — as Evaluation Design Feedback, not runtime rule |
| 6 | Should UNKNOWN-eligible cases be constructed from evidence-poor cases or from genuinely ambiguous cases? | Prefer genuinely ambiguous (evidence-sufficient but interpretation-uncertain) |
| 7 | What is the minimum n for meaningful B1-vs-B2 comparison given case difficulty distribution? | Depends on effect size; with current 84% trivial cases, n would need to be very large |

---

## P. P722 Experiment Evidence

### Ceiling Effect Confirmed

| Condition | Accuracy | Avg Time | < 3s Decisions |
|---|---|---|---|
| A | 93% | 2.2s | 87% |
| B1 | 100% | 1.7s | 100% |
| B2 | 93% | 5.9s | 50% |

**Key findings**:
- B1: 100% accuracy, 100% under 3s → **CEILING EFFECT** (too easy)
- B2 slower than B1 (5.9s vs 1.7s) but this includes 2 UNKNOWN cases (45.9s, 31.3s) — likely Cue induced uncertainty, not efficiency
- B2: 2 UNKNOWN (7%) vs B1: 0 UNKNOWN → Cue may have introduced uncertainty on ambiguous cases
- 3 incorrect decisions in B2 → Cue may have misled on some cases

### Interpretation

The ceiling effect makes B1-vs-B2 comparison largely uninterpretable:
- When cases are trivially easy, Cue cannot reduce effort (already at floor)
- B2 being SLOWER may indicate Cue added processing load without benefit on easy cases
- The 2 UNKNOWN cases in B2 (AMB-032, AMB-375) are the only cases where Cue seemed to affect behavior

---

## Q. SELECTION_OBJECTIVE_MISMATCH — Detailed

### What the Geometric Filter Optimizes

```
h_gap 8-50pt → "these spans are geometrically close"
```

### What the Research Question Needs

```
"cases where Human semantic judgment is non-trivial"
```

### Why These Don't Align

| Geometric proximity | → | Table cells (trivially separable) |
|---|---|---|
| Geometric proximity | ≠ | Semantic ambiguity |

Tables have many closely-spaced cells → geometric filter selects mostly table pairs → most are trivially separable → ceiling effect.

### What Would Align

Cases where:
- Text fragments could plausibly belong to the same unit OR different units
- Structural evidence is ambiguous or conflicting
- A reasonable person could argue either direction
- The Cue could plausibly help OR mislead

These are NOT cases where two numbers sit in adjacent table columns.
