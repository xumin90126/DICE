# Human Evidence Requirement / Minimum Sufficient Evidence Research

> **模式: READ-ONLY RESEARCH / NO MODIFICATION / NO IMPLEMENTATION / NO EXPERIMENT / FROZEN INTACT / STOP**
> 日期: 2026-09-18
> 前置: M-A Caption Association Design Research, Evidence Sufficiency Gap Diagnostic, Human Validation Pilot Analysis, Evidence Pack Counterfactual Diagnostic (P0), Human A/B Pilot (P1), P0→P1 Translation Gap Diagnostic, Human Boundary Decision Evidence Dependency Audit, Human Decision Evidence Dependency Audit
> 本文件: 跨任务、跨对象、跨案例识别可复用的 Evidence Gap 抽象。非案例特定设计。非 Figure/Table/Formula 特定方案。

---

## 0. Research Question

> **当 Human 需要验证一个文档中的具体关系、归属、边界或语义判断时，究竟需要哪些最小证据，才能在不重新阅读整份文档的情况下完成判断？**

本研究的范围严格限定为：

```
IN_SCOPE:
  - 识别跨任务可复用的 Evidence Gap 抽象类型
  - 识别每个 Evidence Gap 类型对应的 Evidence Function
  - 确定 Minimum Sufficient Evidence 的结构边界
  - 区分 Evidence Exists / Evidence Organized / Evidence Presented / Evidence Consumed / Evidence Sufficient

OUT_OF_SCOPE:
  - 案例特定字段设计（已在 Evidence Pack Implementation Report 中完成）
  - Figure/Table/Formula 特定解决方案
  - 新检测器/规则/阈值/模块/LLM 提案
  - 任何代码/数据/算法修改
  - 任何 Human Validation 重跑
```

---

## 1. Evidence Base

```
ANALYZED_MATERIALS:
  Reports (14, all READ-ONLY):
    - m_a_caption_association_design_research.md          (Research Object definition)
    - m_a_evidence_sufficiency_gap_diagnostic.md           (9-case gap diagnosis)
    - m_a_human_validation_pilot_analysis.md               (79-case E0 Pilot)
    - m_a_evidence_pack_counterfactual_diagnostic.md/.csv  (79-case E0→E1, P0)
    - m_a_evidence_pack_implementation_report.md/.json     (E1 implementation)
    - m_a_evidence_pack_pre_implementation_resolution_gate.md (PR1/PR2/PR3)
    - m_a_human_ab_pilot_design_gate.md/.json              (P1 design)
    - m_a_human_ab_pilot_result_analysis.md/.json/.csv     (P1 results, N=24)
    - m_a_p0_p1_translation_gap_diagnostic.md/.json/.csv   (P0→P1 gap)
    - human_decision_evidence_dependency_audit.md/.json    (45-case boundary audit)
    - human_boundary_decision_evidence_dependency_audit.md/.json (45-case boundary)

  Case data:
    - 79 M-A Human Validation Pilot cases (E0, single-rater)
    - 79 M-A Evidence Pack Counterfactual cases (E0 vs E1)
    - 24 M-A Human A/B Pilot cases (P1, 12 E0 + 12 E1)
    - 45 Text Boundary Decision cases (Boundary audit, separate task)

  Human tasks covered:
    - T1: Text-Drawing Structural Association Judgment (M-A, 79+24 cases)
    - T2: Text-Text Boundary Decision (merge/keep-separate, 45 cases)

  Documents: 5 arxiv-style scientific papers (is11_med_001, is11_resnet,
              is11_efficientnet, is11_cs_001, arxiv_2402.18619)

  Governance:
    FROZEN_BASELINE = INTACT (drift=0, shas verified)
    IMPLEMENTATION_AUTHORIZED = FALSE
    EXPERIMENT_AUTHORIZED = FALSE
    HUMAN_VALIDATION_AUTHORIZED = FALSE
    RUNTIME_AUTHORITY = ZERO
    PRODUCTION = FALSE
    STOP = TRUE
```

---

## 2. Cross-Task Findings Summary

### 2.1 Two Human Tasks Analyzed

```
TASK 1 — Text-Drawing Structural Association Judgment (M-A):
  Question: "Is this text associated with this drawing? (YES/NO/UNCERTAIN)"
  N = 79 (E0 Pilot) + 24 (P1 A/B)
  Human sees: text content + drawing extent + spatial relation + same_y context
  Judgment: YES=61, NO=4, UNCERTAIN=14 (E0 Pilot)

TASK 2 — Text-Text Boundary Decision (Boundary):
  Question: "Should these two text atoms be merged or kept separate?"
  N = 45
  Human sees: text_a + text_b + same_y context + table structure
  Judgment: MERGE / KEEP_SEPARATE / UNKNOWN
  System cue exists (IS-11/TLD), Human can override
```

### 2.2 Dominant Cross-Task Pattern

```
CROSS_TASK_FINDING_1 — Evidence Exists but Not Used:
  M-A (P0 counterfactual):
    4/9 UNCERTAIN = evidence sufficient but not presented to Human (44%)
    Primary bottleneck = EVIDENCE_PACK_COMPLETENESS (not observation)
    0/9 = evidence missing (nothing to observe) ← only 2/9 true observation gap

  Boundary (audit):
    100% of decision-relevant evidence EXISTS in DICE (E4=0%)
    64% = existing but not consumed by IS-11 (Consumer Integration Gap)
    0% = evidence missing
    0% = genuine semantic judgment needed

  CONVERGENT FINDING:
    Both tasks show the SAME dominant pattern:
    Evidence EXISTS in the system but is NOT reaching the Human/consumer
    in a usable form. The gap is NOT "missing observation" — it is
    "existing evidence not organized/presented/consumed."

CROSS_TASK_FINDING_2 — Semantic Boundary is the Minority:
  M-A: 5/14 UNCERTAIN = POSSIBLE semantic boundary (36%), 0 CONFIRMED
  Boundary: 0/45 = genuine semantic judgment (E5=0%)
  CONVERGENT: Semantic boundary EXISTS but is NOT the primary blocker.
  Most uncertainty is reducible by evidence improvement, not semantic resolution.

CROSS_TASK_FINDING_3 — Observation Coverage Gap is Rare but Unfixable:
  M-A: 2/9 UNCERTAIN = true observation gap (DGF=0, nothing on page) (22%)
  Boundary: 0/45 = evidence missing (E4=0%)
  CONVERGENT: True "nothing to observe" is rare. When it occurs,
  no amount of Pack/aggregation/organization can fix it.
  Requires new detection capability (cross-page reference handling).
```

---

## Q1. What abstract Human task types exist (not object-specific)?

### Table 1: Human Task Abstraction

| Task ID | Abstract Task Type | Question Form | Evidence Needed | Observed In | N | Key Property |
|---------|-------------------|---------------|-----------------|-------------|---|--------------|
| T1 | STRUCTURAL_ASSOCIATION_JUDGMENT | "Is X associated with Y?" | Target object + reference object + spatial relation + context | M-A (text-drawing) | 79+24 | Binary structural judgment; does NOT require semantic identity ("is it a caption?") |
| T2 | BOUNDARY_DECISION | "Should A and B be merged or separated?" | Both objects + same_y context + structural context (table/column) | Boundary (text-text) | 45 | Merge/separate; requires structural role understanding |
| T3 | DISAMBIGUATION_JUDGMENT | "Which of N candidates is X associated with?" | Target + multiple candidates + pairwise relations | M-A multi-drawing (7 pages) | ~7 | Ambiguous when distances similar; nearest-heuristic default |
| T4 | ROLE_DISAMBIGUATION_JUDGMENT | "What is the semantic role of X?" | Target + context + lexical pattern | M-A caption-vs-reference, label-vs-body | 5 | SEMANTIC boundary — cannot resolve from geometry alone |
| T5 | *(REJECTED)* CAPTION_IDENTITY | "Is this text a Caption?" | — | — | — | Too semantic; requires concept definition; rejected in design research |
| T6 | *(REJECTED)* KEEP_REJECT | "Keep or reject algorithm output?" | — | — | — | Too algorithmic; Human validates evidence, not algorithm decisions |

```
ABSTRACTION_LEVEL:
  T1 + T2 = STRUCTURAL tasks (geometric + lexical evidence sufficient)
  T3 = MULTI-CANDIDATE extension of T1 (needs pairwise comparison)
  T4 = SEMANTIC task (evidence may be sufficient but interpretation needed)
  T5, T6 = REJECTED (too semantic or too algorithmic)

KEY INSIGHT:
  The Human's task is always a JUDGMENT on a RELATION (association,
  boundary, disambiguation), NOT an IDENTIFICATION (what is this object?).
  Evidence serves the relation judgment; it does NOT determine object identity.
  Object identity (caption? reference? label?) is a SEMANTIC INTERPRETATION
  that may remain uncertain even with complete evidence (T4 / Semantic Boundary).
```

---

## Q2. What Evidence Gap types recur across tasks, cases, and objects?

### Table 2: Evidence Gap Abstract (Cross-Task, Cross-Case)

| Gap ID | Gap Type | Definition | Root Cause | Fixable by Pack? | Cross-Task Evidence | Case Count |
|--------|----------|-----------|------------|-----------------|-------------------|------------|
| G1 | OBSERVATION_COVERAGE_GAP | Nothing to observe on the page (DGF=0, no drawing, no raster) | Figure is on another page; pure text page | NO — requires cross-page detection | M-A: 2/9 UNCERTAIN; Boundary: 0/45 | 2 |
| G2 | EVIDENCE_ORGANIZATION_GAP | Primitives exist (DGF>0) but no usable aggregate formed (DEF=0); OR distinct states conflated into one | Aggregation parameters filter out valid primitives; OR state model too coarse | PARTIAL — aggregation parameter tuning (DESIGN_RESEARCH_REQUIRED); state model fixable | M-A: 3/9 UNCERTAIN (2 correctly excluded, 1 possible true gap) + 8 conflated-state cases | 4+8 |
| G3 | EVIDENCE_PRESENTATION_GAP | Evidence exists and is organized, but NOT presented to the Human | Pack generation logic excludes cases; context hardcoded empty; threshold dual-use | YES — Pack redesign (DONE in E1) | M-A: 4/9 UNCERTAIN (extent false-None + context empty); Boundary: 64% Consumer Integration | 4+16 |
| G4 | CONSUMER_INTEGRATION_GAP | Evidence exists, organized, and presented, but consumer (algorithm OR Human) does not use it | Consumer extracts binary signal from rich content; OR Human doesn't view presented evidence | NO (algorithm) / NOT_OBSERVABLE (Human) | Boundary: IS-11 reads P1 text but extracts only is_number/has_text (64%); M-A P1: new evidence usage NOT_OBSERVABLE | 29+? |
| G5 | SEMANTIC_BOUNDARY | Evidence is complete and consumed, but judgment remains uncertain due to genuine semantic ambiguity | Caption vs reference; label vs body text; structural role undeterminable from geometry | NO — this is a legitimate Human judgment boundary, not an evidence gap | M-A: 5/14 UNCERTAIN POSSIBLE (0 CONFIRMED); Boundary: 0/45 | 5 |

```
HIERARCHY (evidence flow):
  Observation (G1) → Organization (G2) → Presentation (G3) → Consumption (G4) → Semantic (G5)

  G1 blocks all downstream: if nothing is observed, nothing can be organized.
  G2 blocks G3: if not organized, cannot be presented.
  G3 blocks G4: if not presented, cannot be consumed.
  G4 blocks G5: if not consumed, semantic sufficiency cannot be assessed.
  G5 is the terminal: evidence is complete but interpretation is needed.

OBSERVED FREQUENCY (M-A 14 UNCERTAIN):
  G1 (Observation):      2 cases (14%)  — unfixable by Pack
  G2 (Organization):     3 cases (21%)  — partially fixable
  G3 (Presentation):     4 cases (29%)  — FIXED in E1 (P0 proved)
  G4 (Consumption):      NOT_OBSERVABLE — cannot quantify
  G5 (Semantic):         5 cases (36%)  — POSSIBLE, 0 CONFIRMED

  PRIMARY_BOTTLENECK = G3 (Presentation) — the most fixable gap
  SECONDARY = G1 (Observation) — the least fixable gap
  TERTIARY = G5 (Semantic) — legitimate, not a "gap" to fix

CROSS-TASK CONVERGENCE:
  M-A:  G1=14%, G2=21%, G3=29%, G5=36% (of UNCERTAIN)
  Boundary: G1=0%, G2=0%, G3=0%, G4=64%, G5=0% (of all 45)
    → Boundary task's gap is CONSUMPTION (G4), not Presentation (G3)
    → Different tasks have different dominant gaps
    → But the SAME 5-type taxonomy covers both
```

### Candidate Gap Type Evaluation

| Candidate (from spec) | Supported? | Maps to | Reason |
|----------------------|-----------|---------|--------|
| Identity | NO (not a gap) | → G5 (Semantic) | "What is this?" is semantic interpretation, not evidence gap. Evidence can reconstruct text but not determine identity. |
| Relation | YES (overlaps) | → G3 (Presentation) | Spatial relation is a core evidence function. Gap = relation not computed/presented. Overlaps with Spatial. |
| Reference | PARTIAL | → G1 (Observation) | Cross-page reference = specific manifestation of observation coverage gap. Not a separate type. |
| Context | YES | → G3 (Presentation) | Same_y context is a core evidence function. Gap = context not collected/presented. |
| Spatial | YES (overlaps) | → G3 (Presentation) | Spatial evidence (distance, ordering, overlap). Overlaps with Relation — merge as SPATIAL_RELATION. |
| Reading-Order | NO | — | P5 ReadingOrder exists but was NOT a bottleneck in any observed case. Not a demonstrated gap type. |
| Boundary | NO (not a gap) | — | "Boundary" is a Human TASK (T2), not an Evidence Gap. Boundary task gaps are G3/G4. |
| Evidence Organization | YES | → G2 | Supported as a distinct gap type. |
| Evidence Presentation | YES | → G3 | Supported as a distinct gap type. PRIMARY bottleneck. |
| Evidence State | NO (not a gap) | → G2 (function) | 3-state model is an Evidence FUNCTION (observation coverage disambiguation), not a gap type. Serves G2. |
| Semantic Interpretation | YES | → G5 | Supported as the terminal gap type. MINORITY of uncertainty. |

```
CONSOLIDATION:
  11 candidate types → 5 gap types (G1-G5)
  4 rejected as "not a gap type" (Identity, Reading-Order, Boundary, Evidence State)
  2 merged (Relation + Spatial → SPATIAL_RELATION function within G3)
  1 collapsed (Reference → manifestation of G1)

  NET: 5 cross-task, cross-object reusable Evidence Gap abstractions.
```

---

## Q3. What Evidence Functions serve each gap type?

### Table 3: Evidence Function vs Field

| Function ID | Evidence Function | Served by (current field) | Gap Addressed | Observed Cases | Status |
|------------|-------------------|--------------------------|---------------|----------------|--------|
| F1 | LEXICAL_DISCRIMINATION | text content, FIG-prefix pattern | Candidate generation (pre-gap) | 79 (all) | EXISTS (P1) |
| F2 | SPATIAL_REFERENCE_TARGET | drawing extent bbox (DEF) | G1, G2 (presence/absence) | 72/79 have extent | EXISTS (DEF) |
| F3 | PROXIMITY_SIGNAL | text-extent distance | G3 (if not presented) | 72/79 computed | EXISTS (consumer-computed) |
| F4 | POSITIONAL_CONTEXT | vertical ordering (above/below/inside) | G3 (if not presented) | 72/79 computed | EXISTS (consumer-computed) |
| F5 | ALIGNMENT_SIGNAL | x-overlap | G3 (if not presented) | 72/79 computed | EXISTS (consumer-computed) |
| F6 | TEXT_RECONSTRUCTION | same_y context (P2 same_y_band, ±5pt) | G3 (context collection) | 79/79 (E1); 63/79 (E0) | EXISTS (P2); FIXED in E1 (±5pt) |
| F7 | DRAWING_DENSITY_SIGNAL | primitive_count, area | G2 (extent quality) | 72/79 | EXISTS (DGF/DEF) |
| F8 | CAPTION_CONTINUATION | adjacent text, h_gap between same-y members | G3 (context completeness) | Partial | EXISTS (P2 h_gap) |
| F9 | MULTI_DRAWING_DISAMBIGUATION | number of extents on page, other FIG texts | G3 (multi-candidate) | 7 pages | DERIVABLE (not stored) |
| F10 | REGION_CONTEXT | P6 region type (COLUMN/DENSE/SPARSE) | G3 (page context) | All pages | EXISTS (P6) |
| F11 | OBSERVATION_COVERAGE_DISAMBIGUATION | evidence_state 3-state model | G2 (state conflation) | 79/79 (E1) | FIXED in E1 (PR3) |
| F12 | NEGATIVE_CONTROL | Type A (FIG+far) + Type B (near+no-FIG) negatives | Validation (pre-gap) | 16 negatives | EXISTS (case design) |

```
FUNCTION-TO-FIELD DISTINCTION (critical):
  Evidence Function = WHAT the evidence does (abstract role)
  Evidence Field = HOW the evidence is stored (concrete data)

  One Function may be served by multiple Fields:
    F3 (Proximity) ← distance_pt (consumer-computed from bbox arithmetic)
    F6 (Text Reconstruction) ← same_y_context (P2 same_y_band ±5pt)

  One Field may serve multiple Functions:
    DEF extent bbox → F2 (reference target) + F3 (distance source) + F5 (overlap source)

  FORBIDDEN CONFLATION:
    "Add a new field" ≠ "add a new capability" ≠ "add a new function"
    A new FUNCTION may be needed; a new FIELD may not be (existing field may serve it)
    This research identifies FUNCTIONS, not fields. Field design = implementation (NOT authorized).
```

---

## Q4. What is the Minimum Sufficient Evidence structure?

### Table 4: Minimum Sufficient Evidence Structure

| Component | Evidence Function Served | Required? | Conditional? | Not Required? | Observed Justification |
|-----------|------------------------|-----------|---------------|---------------|----------------------|
| TARGET_TEXT | F1 (lexical) | REQUIRED | — | — | 79/79 cases: text is the judgment target |
| NEAREST_DRAWING_EXTENT | F2 (reference target) | REQUIRED (always, even if >60pt) | — | All-page extents | P0 Pattern A: false-None extent caused 3+ UNCERTAIN; E1 fix = always include nearest |
| SPATIAL_RELATION (distance + ordering + overlap) | F3, F4, F5 | REQUIRED | — | — | 72/79: spatial relation is core to association judgment |
| SAME_Y_CONTEXT (±5pt) | F6 (text reconstruction) | REQUIRED | — | Sentence/paragraph/cross-page context | P0 Pattern B: empty context caused 2 UNCERTAIN; ±3pt caused 1 total context loss |
| EVIDENCE_STATE (3-state) | F11 (coverage disambiguation) | — | CONDITIONAL (non-EXTENT_EXISTS only) | — | P0 Pattern C: conflated state misled Human for 8 cases |

```
MINIMUM_SUFFICIENT_EVIDENCE_SCHEMA (pre-registered, FROZEN):
  REQUIRED:
    TARGET_TEXT
    NEAREST_DRAWING_EXTENT     (always, regardless of distance)
    SPATIAL_RELATION           (distance + vertical ordering + x-overlap)
    SAME_Y_CONTEXT             (±5pt, unified for all case types)

  CONDITIONAL:
    EVIDENCE_STATE             (only when state ≠ EXTENT_EXISTS)

  NOT_REQUIRED:
    all-page extents
    sentence/paragraph context
    cross-page context
    reading order sequence
    region classification
    primitive-level detail

  EVIDENCE_COMPRESSION_BOUNDARY:
    ENDS at: same_y context + nearest extent + spatial relation
    BEYOND this = Document Reconstruction (Human should NOT need to do)

  PACK_REMAINS_NON_SEMANTIC = TRUE
    Pack provides OBSERVATION + ORGANIZATION + PRESENTATION
    Pack does NOT provide INTERPRETATION
    "Evidence Sufficient" ≠ "Association True"
```

### Sufficiency vs Association Truth (critical distinction)

```
Evidence Sufficient = Human has enough information to make A judgment (YES or NO)
  → A Pack can be SUFFICIENT for a NO judgment
  → A Pack can be SUFFICIENT while judgment is UNCERTAIN (genuine semantic boundary)
  → SUFFICIENT does NOT mean: association is YES, judgment is easy, no cognitive effort

Evidence Exists = the raw observation is present in the system
  → Does NOT mean it is organized (G2)
  → Does NOT mean it is presented (G3)
  → Does NOT mean it is consumed (G4)
  → Does NOT mean it is sufficient (may be G5)

THE 5-STATE SUFFICIENCY LADDER:
  L0: Evidence does not exist (G1)
  L1: Evidence exists but not organized (G2)
  L2: Evidence organized but not presented (G3)
  L3: Evidence presented but not consumed (G4)
  L4: Evidence consumed but not sufficient (G5 — semantic boundary)
  L5: Evidence consumed and sufficient → judgment made

  M-A E0 Pilot: 65/79 reached L5 (definitive judgment); 14 at L0-L4
  M-A E1 (P0):  74/79 reached L3+ (evidence presented); 5 at L0-L1 (genuine gaps)
  Boundary:     45/45 evidence at L1+ (exists); 29/45 stuck at L2-L3 (not consumed by IS-11)
```

---

## Q5. Which evidence gaps are unfixable by Pack design?

```
UNFIXABLE_BY_PACK (require new capability):

  G1 — OBSERVATION_COVERAGE_GAP:
    Cause: figure is on another page; page is pure text
    Fix requires: cross-page reference resolution (new detection capability)
    Cases: 2 (is11_med_001_p18, arxiv_2402.18619_p11)
    Status: DESIGN_RESEARCH_REQUIRED (not implementation)

  G2 (partial) — AGGREGATION_PARAMETER_GAP:
    Cause: 233 primitives exist but no extent formed (is11_efficientnet_p2)
    Fix requires: aggregation parameter investigation (possible threshold tuning)
    Cases: 1 (possible true gap; 2 others correctly excluded)
    Status: DESIGN_RESEARCH_REQUIRED

  G4 — CONSUMER_INTEGRATION_GAP:
    Cause: consumer (IS-11) extracts binary signal from rich P1 text
    Fix requires: consumer redesign (IS-11 IS-01/IS-02 logic change)
    Cases: 29/45 boundary cases
    Status: NOT_AUTHORIZED (consumer modification = implementation)

  G5 — SEMANTIC_BOUNDARY:
    Cause: genuine semantic ambiguity (caption vs reference; label vs body)
    Fix: NONE — this is a legitimate Human judgment boundary
    Cases: 5 POSSIBLE (0 CONFIRMED)
    Status: NOT_A_GAP_TO_FIX (route to Human Validation, accepted)

FIXABLE_BY_PACK (already addressed in E1):

  G3 — EVIDENCE_PRESENTATION_GAP:
    Sub-type 3a (extent false-None): FIXED — always include nearest extent (PR2)
    Sub-type 3b (context empty for negatives): FIXED — unified pipeline (PR1)
    Sub-type 3c (±3pt too narrow): FIXED — ±5pt (PR1)
    Cases: 4/9 UNCERTAIN resolved; 27/79 improved; 0 regressions
    Status: E1_IMPLEMENTED (P0 verified); FROZEN

  G2 (state conflation):
    FIXED — 3-state evidence_state model (PR3)
    Cases: 8 conflated-state cases resolved
    Status: E1_IMPLEMENTED (P0 verified); FROZEN
```

---

## Q6. What is the relationship between Evidence Sufficiency and Human behavior?

```
From P1 A/B Pilot (N=24):

  FINDING_1 — Evidence Sufficient ≠ No Search:
    7/9 E1 M3=YES (searched) cases had M6=SUFFICIENT
    Human reports Pack is sufficient BUT still searches for more context
    M3 (search) and M6 (sufficiency) measure DIFFERENT constructs
    → Sufficiency is a belief state; search is a behavior; they are DECOUPLED

  FINDING_2 — Evidence Improved ≠ Human Benefit Observed:
    P0: 27/79 cases objectively improved (E1 > E0)
    P1: 9/12 E1 cases = "improvement without observable benefit"
    Only 1/12 showed clear benefit signal
    → Objective content improvement does NOT guarantee Human-level signal
    → At N=12, MINOR changes (7/12) are invisible

  FINDING_3 — Evidence Usage NOT_OBSERVABLE:
    No interaction logs (element visibility, time-per-element, scroll)
    Cannot determine if Human actually viewed new evidence_state
    Cannot attribute judgment outcome to new evidence
    → Benefit claims are FORBIDDEN without usage observability

  FINDING_4 — Genuine Evidence Gaps Remain Unfixable:
    2/12 E1 cases = Type A PRIMITIVES_NO_EXTENT (DEF=0)
    M4=L4, M6=uncertain — Pack cannot fix (page lacks drawing evidence)
    → These are G1/G2 gaps, not G3 — correctly identified as unfixable

  IMPLICATION FOR EVIDENCE REQUIREMENT RESEARCH:
    "Minimum Sufficient Evidence" is an OBJECTIVE property of the Pack
    (can be verified by P0 counterfactual: does the Pack contain the
    required components?).

    "Human-perceived sufficiency" is a SUBJECTIVE state that depends on:
    - whether the Human views the evidence (G4 — not observable)
    - whether the evidence is relevant to the specific judgment
    - the Human's interpretation of "sufficient" vs "search"
    - case difficulty (confounding)

    The research can establish OBJECTIVE minimum sufficiency (Pack structure).
    It CANNOT establish HUMAN-PERCEIVED sufficiency without:
    - interaction logs (G4 observability)
    - larger N (power for MINOR changes)
    - construct-validity validation (M3 ≠ M6)
```

---

## OVER-DESIGN CHECK

```
This section checks for over-design risks in the research conclusions.

CHECK_1 — Per-object system design (Figure/Table/Formula-specific)?
  STATUS: CLEAN
  All 5 gap types (G1-G5) are object-agnostic.
  No gap type references "figure", "table", "formula", "caption" specifically.
  Evidence Functions (F1-F12) are abstract (lexical, spatial, contextual).
  The taxonomy applies to ANY document relation judgment task.

CHECK_2 — Field = Capability confusion?
  STATUS: CLEAN
  Table 3 explicitly distinguishes Function (abstract role) from Field (concrete data).
  No new field is proposed. Existing fields are mapped to functions.
  "Add a new function" ≠ "add a new field" is stated.
  Field design = implementation (NOT authorized).

CHECK_3 — Distance = Relation confusion?
  STATUS: CLEAN
  F3 (Proximity) is labeled as SUPPORTING signal, not a rule.
  "Closer → tends YES" is explicitly marked "descriptive, NOT a rule."
  No threshold derived from distance distribution.
  Distance serves the spatial relation FUNCTION; it does NOT define association.
  PR2 (60pt) is pre-registered as candidate-generation-only, NOT a semantic threshold.

CHECK_4 — Evidence Exists = Sufficient confusion?
  STATUS: CLEAN
  The 5-state sufficiency ladder (L0-L5) explicitly separates:
    Exists (L1+) → Organized (L2+) → Presented (L3+) → Consumed (L4+) → Sufficient (L5)
  "Evidence Sufficient ≠ Association True" is stated.
  Boundary audit finding (100% exists, 64% not consumed) is cited as proof.

CHECK_5 — Single-case generalization?
  STATUS: CLEAN
  G2 aggregation gap (is11_efficientnet_p2, 233 primitives) is labeled
  DESIGN_RESEARCH_REQUIRED, NOT generalized to a rule.
  No threshold or rule derived from a single case.
  Case-specific observations are marked with case_ids; abstractions require
  cross-case evidence (minimum 2 cases from different documents).

CHECK_6 — Unimplemented proposals?
  STATUS: CLEAN
  No new detector, rule, threshold, module, LLM, or capability proposed.
  G1 fix (cross-page) = DESIGN_RESEARCH_REQUIRED (not a proposal).
  G2 fix (aggregation) = DESIGN_RESEARCH_REQUIRED (not a proposal).
  G4 fix (consumer) = NOT_AUTHORIZED (stated as finding, not proposal).
  All E1 fixes (PR1/PR2/PR3) are ALREADY IMPLEMENTED and FROZEN.

CHECK_7 — Research hypothesis written as system requirement?
  STATUS: CLEAN
  "Minimum Sufficient Evidence" is defined as an OBJECTIVE Pack property
  (verifiable by counterfactual), NOT a system requirement.
  No statement of the form "the system MUST do X."
  All findings are framed as "observed in data" with case evidence.
  Governance: IMPLEMENTATION_AUTHORIZED = FALSE throughout.

OVER_DESIGN_RISK = LOW
  The research identifies abstractions and functions, not implementations.
  The 5 gap types are observational (what was observed), not prescriptive
  (what the system should do). The Minimum Sufficient Evidence schema is
  pre-registered and FROZEN (not a new proposal).
```

---

## 5 Final Questions

### FQ1: Is a universal Human Evidence Requirement proven?

```
STATUS = PARTIALLY_SUPPORTED

  SUPPORTED (objective):
    - 5-type Evidence Gap taxonomy (G1-G5) is cross-task validated
      (covers both M-A association and Boundary decision)
    - Minimum Sufficient Evidence schema (TARGET_TEXT + NEAREST_DRAWING_EXTENT
      + SPATIAL_RELATION + SAME_Y_CONTEXT + EVIDENCE_STATE) is pre-registered,
      implemented (E1), and P0-verified (27/79 improved, 0 regressions)
    - 12 Evidence Functions (F1-F12) are abstracted from observed field purposes
    - Dominant pattern (evidence exists but not presented/consumed) is convergent
      across 2 independent tasks

  NOT_SUPPORTED (Human-level):
    - P1 A/B Pilot did NOT confirm Human-level benefit (INCONCLUSIVE)
    - Evidence usage NOT_OBSERVABLE (no interaction logs)
    - N=24 too small for MINOR changes (7/12 invisible)
    - Single Human reviewer (inter-rater reliability NOT_AVAILABLE)
    - Construct validity not established (M3 ≠ M6)
    - 5 documents only (scientific papers; generalization NOT_DEMONSTRATED)

  CONCLUSION:
    The OBJECTIVE evidence requirement (what the Pack must contain) is
    PARTIALLY_SUPPORTED by P0 counterfactual evidence.
    The SUBJECTIVE evidence requirement (what the Human perceives as sufficient)
    is NOT_DEMONSTRATED by P1 (INCONCLUSIVE).
    A universal claim requires: (1) interaction logs, (2) larger N,
    (3) multi-document-type, (4) multi-human.
```

### FQ2: What is the safest abstraction?

```
SAFEST_ABSTRACTION = The 5-type Evidence Gap hierarchy (G1-G5):

  G1: OBSERVATION_COVERAGE_GAP    (nothing to observe)
  G2: EVIDENCE_ORGANIZATION_GAP   (exists but not organized)
  G3: EVIDENCE_PRESENTATION_GAP   (organized but not presented)
  G4: CONSUMER_INTEGRATION_GAP    (presented but not consumed)
  G5: SEMANTIC_BOUNDARY           (consumed but not sufficient)

  WHY safest:
    - Cross-task validated (2 tasks, 148+ cases)
    - Object-agnostic (no Figure/Table/Formula specificity)
    - Observational (derived from data, not prescriptive)
    - Non-semantic (describes evidence flow, not interpretation)
    - Hierarchical (clear dependency chain, diagnostic utility)
    - Each gap type has a clear fixability status
    - Does NOT require new fields/detectors/rules to define

  SECONDARY (supporting): The 5-state Sufficiency Ladder (L0-L5)
    Distinguishes Exists / Organized / Presented / Consumed / Sufficient
    Prevents the most dangerous conflation: "evidence exists" = "sufficient"
```

### FQ3: Is system modification needed now?

```
SYSTEM_MODIFICATION_NEEDED_NOW = FALSE

  RATIONALE:
    - E1 Evidence Pack is ALREADY IMPLEMENTED and FROZEN (PR1/PR2/PR3)
    - P0 verified objective improvement (27/79, 0 regressions)
    - P1 did NOT confirm Human-level benefit (INCONCLUSIVE)
    - No new field/detector/rule/threshold/module is justified by current evidence
    - G1 (cross-page) = DESIGN_RESEARCH_REQUIRED (not implementation-ready)
    - G2 (aggregation) = DESIGN_RESEARCH_REQUIRED (1 possible case, insufficient)
    - G4 (consumer) = NOT_AUTHORIZED (IS-11 modification = implementation)
    - G5 (semantic) = NOT_A_GAP_TO_FIX (legitimate Human boundary)
    - IMPLEMENTATION_AUTHORIZED = FALSE
    - EXPERIMENT_AUTHORIZED = FALSE
    - HUMAN_VALIDATION_AUTHORIZED = FALSE
    - FROZEN_BASELINE = INTACT

  The system is in a stable, frozen state. The research identifies
  what is known and what is unknown. No modification is warranted
  until the unknowns (G4 observability, P1 confirmation, G1/G2 research)
  are resolved.
```

### FQ4: Are new specific fields needed?

```
NEW_SPECIFIC_FIELDS_NEEDED = FALSE

  RATIONALE:
    - All 12 Evidence Functions (F1-F12) are served by EXISTING fields:
      P1 text, P2 same_y_band, P5 ReadingOrder, P6 RegionObservation,
      DGF, DEF, consumer-computed spatial relation
    - E1 added evidence_state (3-state) — ALREADY IMPLEMENTED, FROZEN
    - E1 unified same_y context (±5pt) — ALREADY IMPLEMENTED, FROZEN
    - E1 always-includes nearest extent — ALREADY IMPLEMENTED, FROZEN
    - No NEW field is identified as needed by the gap analysis
    - G1 (cross-page) would need a new CAPABILITY (not a field) — DESIGN_RESEARCH_REQUIRED
    - G4 (consumer) would need consumer LOGIC change (not a field) — NOT_AUTHORIZED

  The research confirms that existing observation surfaces (P1/P2/P5/P6/DGF/DEF)
  are SUFFICIENT to serve all identified Evidence Functions. The gaps are in
  organization/presentation/consumption, NOT in missing fields.
```

### FQ5: What is the next minimal research action?

```
NEXT_RESEARCH_ACTION = ONE READ-ONLY action:

  "Audit G4 (Consumer Integration Gap) observability: determine whether
  the M-A review UI can be instrumented (READ-ONLY design analysis only)
  to record which Evidence Pack elements a Human views, without modifying
  any production system, frozen baseline, or existing data.

  Specifically: catalog what interaction signals are technically capturable
  (element visibility, scroll position, time-per-element, click events) in
  the current UI architecture, and whether capturing them would require
  code modification (implementation) or can be derived from existing logs.

  This is a READ-ONLY design-feasibility audit. No implementation.
  No experiment. No Human Validation. Output = a feasibility report."

  WHY this action:
    - G4 (Consumption) is the ONLY gap type that is NOT_OBSERVABLE
    - Without G4 observability, no future experiment can attribute
      Human judgment to evidence usage
    - P1 failed partly because G4 was not observable (Lesson 5)
    - This is the minimal prerequisite for any future evidence-requirement
      experiment — it does NOT itself test anything
    - It is purely diagnostic (what CAN we observe?) not prescriptive

  ALTERNATIVE = NO_NEXT_ACTION_JUSTIFIED
    If the team judges that G4 observability audit is itself premature
    (given P1 INCONCLUSIVE and STOP=TRUE), then NO_NEXT_ACTION_JUSTIFIED
    is the equally valid conclusion. The research has identified what is
    known and what is unknown; stopping here is defensible.

  RECOMMENDED = NO_NEXT_ACTION_JUSTIFIED
    Given: P1 INCONCLUSIVE, IMPLEMENTATION_AUTHORIZED=FALSE,
    EXPERIMENT_AUTHORIZED=FALSE, HUMAN_VALIDATION_AUTHORIZED=FALSE,
    STOP=TRUE, FROZEN_BASELINE=INTACT — the safest action is to STOP
    and not initiate new research until governance status changes.
    The G4 observability audit is documented as a known prerequisite
    for FUTURE research, not an action to take now.
```

---

## Table 5: Future Problem Handling Principles

| Principle ID | Principle | Rationale | Derived From | Applies To |
|-------------|-----------|-----------|--------------|------------|
| P1 | Separate "Evidence Exists" from "Evidence Sufficient" | 100% of boundary evidence exists; 64% not consumed. Exists ≠ sufficient. | Boundary audit, P0 counterfactual | All gap assessment |
| P2 | Separate "Pack Content" from "Human Benefit" | P0 improved content (27/79); P1 didn't confirm benefit. Content ≠ benefit. | P0→P1 translation gap | All Human validation design |
| P3 | Separate "Evidence Sufficient" from "Association True" | SUFFICIENT can lead to NO; SUFFICIENT can lead to UNCERTAIN. | Design gate pre-registration | All judgment analysis |
| P4 | Separate "Search" from "Insufficiency" | 7/9 M3=YES had M6=SUFFICIENT. Search ≠ insufficiency. | P1 A/B results | All metric design |
| P5 | Classify UNCERTAIN before interpreting | 3-class UNCERTAIN (Evidence Insufficient / Possible Semantic Boundary / Not Determinable) prevents misreading. | Design gate, P1 results | All UNCERTAIN analysis |
| P6 | Require convergent evidence for benefit claims | No single metric suffices; require M2/M3/M4/M6 convergence. | P1 design gate | All benefit claims |
| P7 | Separate fixable gaps from unfixable | G3 (Presentation) fixable; G1 (Observation) unfixable by Pack. | Gap diagnostic, P0 | All gap resolution |
| P8 | Pre-register thresholds before use | ±5pt, 60pt, 3-state were pre-registered. Prevents post-hoc tuning. | PR1/PR2/PR3 gate | All parameter use |
| P9 | Instrument usage before claiming benefit | G4 NOT_OBSERVABLE blocked P1. Usage logs are prerequisite. | P1 Lesson 5 | All future experiments |
| P10 | Stop when evidence is exhausted | P1 INCONCLUSIVE + STOP=TRUE is the honest result. Don't force SUPPORTED. | P1 governance | All research conclusion |

---

## Cross-Case Gap Pattern Summary

| Pattern | Gap Type | Cross-Case Evidence | Fixability |
|---------|----------|-------------------|------------|
| Extent false-None (Type A, 60pt dual-use) | G3 | 3 cases across 3 documents | FIXED (E1 PR2) |
| Context empty for negatives (hardcoded) | G3 | 16 cases (8 Type A + 8 Type B) | FIXED (E1 unified pipeline) |
| ±3pt too narrow (baseline variation) | G3 | 17 cases (16 neg + 11 cand) | FIXED (E1 PR1 ±5pt) |
| State conflation (binary → 3-state) | G2 | 8 cases (3 PRI_NO_EXT + 3 EXT + 2 NO_VIS) | FIXED (E1 PR3) |
| Cross-page reference (figure elsewhere) | G1 | 4 cases across 4 documents | UNFIXABLE (needs cross-page) |
| Aggregation miss (233 primitives, no extent) | G2 | 1 case (efficientnet p2) | DESIGN_RESEARCH_REQUIRED |
| "Fig." fragment ambiguity (caption vs ref) | G5 | 3 cases across 2 documents | NOT_A_GAP (semantic boundary) |
| Non-FIG text role ambiguity (label vs body) | G5 | 2 cases across 1 document | NOT_A_GAP (semantic boundary) |
| Consumer binary extraction (IS-11) | G4 | 29/45 boundary cases | NOT_AUTHORED (consumer change) |
| Improvement without benefit (MINOR changes) | G4 | 9/12 P1 E1 cases | NOT_OBSERVABLE (no usage logs) |

---

## Governance Verification

```
FROZEN_BASELINE:
  P1 (AtomicText)       sha=74d23ec784d65782  INTACT
  TLD                   sha=022f5c21e872ad9e  INTACT
  GT                    sha=7349963d0d23b5ef  INTACT
  layout_analyzer       sha=8f69f0d206b3e565  INTACT
  DGF                   sha=f25a5ff41afa1bec  INTACT
  DEF                   sha=cba9e583517f8967  INTACT
  DRIFT = 0

DATA:
  human_session_1.json        UNCHANGED (79 cases, MUST NOT MODIFY)
  candidates_internal.json    UNCHANGED (79 cases, E1 Evidence Pack)
  ab_pilot_results.json       UNCHANGED (24 cases, P1 results)
  e0_reconstructed.json       UNCHANGED (persistent copy)

RESEARCH_MODE:
  READ_ONLY = TRUE
  FILES_MODIFIED = 0 (existing)
  FILES_CREATED = 3 (new research outputs only):
    - tmp/human_evidence_requirement_research.md (this file)
    - tmp/human_evidence_requirement_research.json
    - tmp/human_evidence_requirement_case_table.csv

NO:
  - code modification
  - data modification
  - algorithm modification
  - Evidence Pack modification
  - Human Judgment modification
  - Frozen Baseline modification
  - new detector/rule/threshold/module/LLM/Capability/Runtime
  - implementation
  - experiment
  - Human Validation
```

---

## Conclusion

```
HUMAN_EVIDENCE_REQUIREMENT_STATUS = PARTIALLY_SUPPORTED
  → Objective Pack structure supported by P0 counterfactual
  → Human-perceived sufficiency NOT_DEMONSTRATED by P1 (INCONCLUSIVE)
  → Universal claim requires interaction logs + larger N + multi-document + multi-human

PRIMARY_ABSTRACTION = 5-TYPE_EVIDENCE_GAP_HIERARCHY (G1-G5)
  G1: OBSERVATION_COVERAGE_GAP (nothing to observe)
  G2: EVIDENCE_ORGANIZATION_GAP (exists but not organized)
  G3: EVIDENCE_PRESENTATION_GAP (organized but not presented)
  G4: CONSUMER_INTEGRATION_GAP (presented but not consumed)
  G5: SEMANTIC_BOUNDARY (consumed but not sufficient)

SECONDARY_ABSTRACTIONS =
  12_EVIDENCE_FUNCTIONS (F1-F12, abstract roles served by existing fields)
  5-STATE_SUFFICIENCY_LADDER (L0-L5: Exists→Organized→Presented→Consumed→Sufficient)
  MINIMUM_SUFFICIENT_EVIDENCE_SCHEMA (TARGET_TEXT + NEAREST_DRAWING_EXTENT
    + SPATIAL_RELATION + SAME_Y_CONTEXT + conditional EVIDENCE_STATE)

CASE_SPECIFIC_PATCH_RISK = LOW
  → 5 gap types are object-agnostic and cross-task validated
  → No Figure/Table/Formula-specific solution proposed
  → No single-case generalization (all abstractions require ≥2 cross-document cases)
  → OVER-DESIGN CHECK: 7 checks, all CLEAN

MINIMUM_SUFFICIENT_EVIDENCE_STATUS = OBJECTIVELY_VERIFIED (P0), HUMAN_UNVERIFIED (P1)
  → P0: 27/79 improved, 0 regressions, Level-3 burden 8→0
  → P1: INCONCLUSIVE (N=24, usage NOT_OBSERVABLE, MINOR changes invisible)
  → Schema is pre-registered, implemented (E1), and FROZEN

SYSTEM_MODIFICATION_NEEDED_NOW = FALSE
  → E1 already implemented and frozen
  → No new field/detector/rule/threshold justified
  → G1/G2 = DESIGN_RESEARCH_REQUIRED (not implementation-ready)
  → G4 = NOT_AUTHORIZED (consumer change)
  → G5 = NOT_A_GAP_TO_FIX (legitimate boundary)

NEW_HUMAN_VALIDATION_NEEDED_NOW = FALSE
  → P1 INCONCLUSIVE but does NOT justify new validation
  → G4 observability prerequisite not met (no interaction logs)
  → Construct validity not established (M3 ≠ M6)
  → HUMAN_VALIDATION_AUTHORIZED = FALSE

NEXT_RESEARCH_ACTION = NO_NEXT_ACTION_JUSTIFIED
  → Given STOP=TRUE and all authorization flags FALSE
  → G4 observability audit documented as known prerequisite for FUTURE research
  → Not an action to take now

IMPLEMENTATION_AUTHORIZED = FALSE
EXPERIMENT_AUTHORIZED = FALSE
HUMAN_VALIDATION_AUTHORIZED = FALSE
FROZEN_BASELINE = INTACT
STOP = TRUE
```

---

## Appendix A: Source Material Index

| # | File | Type | Cases | Key Contribution |
|---|------|------|-------|-----------------|
| 1 | m_a_caption_association_design_research.md | Design Research | — | Research Object, Task types, Evidence Functions |
| 2 | m_a_evidence_sufficiency_gap_diagnostic.md | Gap Diagnostic | 9 | 3-layer diagnosis (Observation/Organization/Semantic) |
| 3 | m_a_human_validation_pilot_analysis.md | Pilot Analysis | 79 | Case types, judgment distribution, UNCERTAIN classification |
| 4 | m_a_evidence_pack_counterfactual_diagnostic.md/.csv | Counterfactual (P0) | 79 | E0→E1 comparison, 4 gap patterns, burden reduction |
| 5 | m_a_evidence_pack_implementation_report.md/.json | Implementation | 79 | PR1/PR2/PR3, E1 Evidence Pack schema |
| 6 | m_a_evidence_pack_pre_implementation_resolution_gate.md | Gate | — | Pre-registration of PR1/PR2/PR3 |
| 7 | m_a_human_ab_pilot_design_gate.md/.json | Design Gate | 24 | P1 A/B design, metrics M1-M6, stop conditions |
| 8 | m_a_human_ab_pilot_result_analysis.md/.json/.csv | Result Analysis | 24 | P1 results, INCONCLUSIVE, 4-type E1 outcome |
| 9 | m_a_p0_p1_translation_gap_diagnostic.md/.json/.csv | Gap Diagnostic | 24 | 3 translation factors, construct mismatch |
| 10 | human_decision_evidence_dependency_audit.md/.json | Audit | 45 | E2=78% existing-but-unorganized, 3 signal candidates |
| 11 | human_boundary_decision_evidence_dependency_audit.md/.json | Audit | 45 | 100% evidence exists, 64% Consumer Integration Gap |
| 12 | m_a_human_validation_pilot_case_analysis.csv | Case Data | 79 | Per-case judgment, type, spatial evidence |
| 13 | m_a_human_ab_pilot_sampling_frame.csv | Sampling | 79 | 24 selected, arm/stratum/p0-change |
| 14 | m_a_p0_p1_translation_gap_case_table.csv | Case Data | 24 | Per-case P0 change type, P1 metrics |

## Appendix B: Evidence Gap Type Decision Tree

```
START: Human cannot make a definitive judgment (UNCERTAIN)

  Q: Does the target observation exist on the page?
    NO  → G1: OBSERVATION_COVERAGE_GAP (nothing to observe)
          → Fix: cross-page detection (DESIGN_RESEARCH_REQUIRED)
    YES → continue

  Q: Has the observation been organized into a usable aggregate?
    NO  → G2: EVIDENCE_ORGANIZATION_GAP (primitives exist, no extent)
          → Fix: aggregation parameter investigation (DESIGN_RESEARCH_REQUIRED)
    YES → continue

  Q: Has the organized evidence been presented in the Pack?
    NO  → G3: EVIDENCE_PRESENTATION_GAP (exists but not shown)
          → Fix: Pack redesign (DONE in E1, FROZEN)
    YES → continue

  Q: Did the consumer (algorithm/Human) use the presented evidence?
    NO  → G4: CONSUMER_INTEGRATION_GAP (presented but not consumed)
          → Fix: consumer redesign / UI instrumentation (NOT_AUTHORIZED)
    YES → continue

  Q: Is the consumed evidence sufficient for a definitive judgment?
    NO  → G5: SEMANTIC_BOUNDARY (consumed but not sufficient)
          → Fix: NONE — legitimate Human judgment boundary
    YES → L5: Judgment made (exit)

DECISION_TREE_STATUS = OBSERVATIONAL (diagnostic tool, not a system rule)
  → This tree describes how to DIAGNOSE an existing UNCERTAIN case.
  → It does NOT prescribe system behavior.
  → It does NOT require implementation.
```
