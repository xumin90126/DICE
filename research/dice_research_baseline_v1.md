# DICE Research Baseline v1 — Phase 1 Formal Closure

> **模式: READ-ONLY / RESEARCH BASELINE FREEZE / NO IMPLEMENTATION / NO NEW EXPERIMENT / STOP**
> 日期: 2026-09-18
> 本文件: 对 DICE 第一阶段研究成果进行正式收口，建立可供后续研究使用的稳定 Research Baseline。

---

## 0. Purpose

```
本文件不是项目总结，不是论文草稿。

本文件是一个 RESEARCH BASELINE REGISTRY：
  - 记录当前已知什么
  - 记录当前未知什么
  - 记录冻结了什么
  - 记录下一步从哪里重新开启

完成后立即 STOP。
```

---

## 1. Baseline Version

```
BASELINE_VERSION = RESEARCH_BASELINE_V1
DATE = 2026-09-18
PHASE = PHASE_1_CLOSURE
RESEARCH_BASELINE = FROZEN
```

---

## 2. System State

```
SYSTEM_STATE:
  P1–P7:                      FROZEN
  Atomic Observation:          FROZEN
  DGF (Drawing Geometry Fact): FROZEN
  DEF (Drawing Extent Fact):   FROZEN
  M-A (Caption Association):   FROZEN
  Evidence Pack (E1):          FROZEN
  Capability Registry:         FROZEN
  Runtime governance:          FROZEN

FROZEN_HASHES (verified INTACT, drift=0):
  P1 (AtomicText):       74d23ec784d65782  INTACT ✓
  TLD:                   022f5c21e872ad9e  INTACT ✓
  GT:                    7349963d0d23b5ef  INTACT ✓
  layout_analyzer:       8f69f0d206b3e565  INTACT ✓
  DGF (drawing_geometry):f25a5ff41afa1bec  INTACT ✓
  DEF (drawing_extent):  cba9e583517f8967  INTACT ✓

  VERIFICATION_SOURCE:
    tmp/l5_5_implementation_baseline.json (expected=actual for P1, TLD, GT)
    tmp/m_a_evidence_pack_pre_implementation_resolution_gate.md (all 6 UNCHANGED)
    tmp/m_a_evidence_pack_implementation_report.md (all 6 ✓)

BASELINE_DRIFT = 0
```

---

## 3. Research State

```
RESEARCH_STATE:

  Research chain (completed):
    P1–P7
       ↓
    Atomic Observation
       ↓
    Vector Geometry Evidence (AO Visual Geometry Extension)
       ↓
    M-A Evidence Organization
       ↓
    Evidence Pack (E1: PR1/PR2/PR3, FROZEN)
       ↓
    G1–G5 Evidence Gap Framework
       ↓
    G1–G5 Cross-Document Validation (70 cases, 13 documents)
       ↓
    Evidence Sufficiency Analysis (149 cases)
       ↓
    Evidence Boundary Research (13 boundary candidates)

  Research artifacts (FROZEN):
    131 .md reports
    131 .json structured data files
    14 .csv case tables

  Key research outputs (canonical):
    tmp/human_evidence_requirement_research.md / .json / .csv
    tmp/g1_g5_cross_document_validation.md / .json / .csv (×3)
    tmp/evidence_sufficiency_boundary_research.md / .json / .csv (×3)
```

---

## 4. Frozen Artifacts

### 4.1 System Artifacts

| Artifact | SHA (short) | Status | File |
|----------|------------|--------|------|
| P1 AtomicText | 74d23ec784d65782 | INTACT | perception/p1/ |
| TLD | 022f5c21e872ad9e | INTACT | chunker/ |
| GT (Ground Truth) | 7349963d0d23b5ef | INTACT | tmp/is11_semantic_ground_truth.json |
| layout_analyzer | 8f69f0d206b3e565 | INTACT | chunker/layout_analyzer.py |
| DGF | f25a5ff41afa1bec | INTACT | perception/atomic_observation/drawing_geometry.py |
| DEF | cba9e583517f8967 | INTACT | perception/atomic_observation/drawing_extent.py |

### 4.2 Research Framework Artifacts

| Framework | Definition | Status | Source |
|-----------|-----------|--------|--------|
| G1 | OBSERVATION_COVERAGE_GAP | FROZEN | human_evidence_requirement_research.md |
| G2 | EVIDENCE_ORGANIZATION_GAP | FROZEN | human_evidence_requirement_research.md |
| G3 | EVIDENCE_PRESENTATION_GAP | FROZEN | human_evidence_requirement_research.md |
| G4 | CONSUMER_INTEGRATION_GAP | FROZEN | human_evidence_requirement_research.md |
| G5 | SEMANTIC_BOUNDARY | FROZEN | human_evidence_requirement_research.md |
| Evidence Sufficiency | SUFFICIENT/INSUFFICIENT/BOUNDARY/INDETERMINATE | FROZEN | evidence_sufficiency_boundary_research.md |
| Evidence Boundary | B1-B6 criteria + C1-C4 counterfactuals | FROZEN | evidence_sufficiency_boundary_research.md |
| Evidence Functions | F1-F12 (existing) + F13-F15 (derivable) | FROZEN | human_evidence_requirement_research.md |
| Minimum Sufficient Evidence | TARGET+REFERENCE+RELATION+CONTEXT (+conditional STATE) | FROZEN | human_evidence_requirement_research.md |

### 4.3 Research Data Artifacts

| Dataset | N | Cases | Status | Source File |
|---------|---|-------|--------|-------------|
| IS-11 Boundary Decision | 45 | 4 docs, GT-backed | FROZEN | is11_semantic_ground_truth.json |
| M-A Human Validation (E0) | 79 | 5 docs, single-rater | FROZEN | human_session_1.json |
| M-A Evidence Pack Counterfactual (P0) | 79 | E0 vs E1 comparison | FROZEN | m_a_evidence_pack_counterfactual_diagnostic.json |
| M-A Human A/B Pilot (P1) | 24 | 12 E0 + 12 E1 | FROZEN | ab_pilot_results.json |
| G1-G5 Cross-Document Validation | 70 | 13 docs, 23 problem types | FROZEN | g1_g5_case_classification.csv |
| Evidence Sufficiency/Boundary | 149 | Unified case universe | FROZEN | evidence_sufficiency_case_table.csv |
| P7 Independent Evaluation | 10 | 4 docs | FROZEN | Extracted from audit reports |
| Phase 3 IS-14 | 13 | 5 docs | FROZEN | phase3_is14_final_report.md |
| PH-02 Column Membership | 22 | 4 docs | FROZEN | ph02_failure_mechanism_review.json |

---

## 5. Findings (Three Levels)

### A. SUPPORTED

```
Current evidence is sufficient to support these conclusions:

S-01: G1-G5 can classify 100% of observed failure cases (70/70).
  Evidence: 70 cases from 13 documents, 23 problem types, 0 unclassified.
  Limitation: Academic papers only.

S-02: No new Gap Type (G6) is warranted.
  Evidence: 0 true new gap candidates; 27 borderline cases are all existing type boundaries.
  Limitation: Only academic papers tested.

S-03: Evidence Availability ≠ Evidence Sufficiency.
  Evidence: 55 cases have available evidence but are insufficient (G1-G3);
            13 have available but boundary (G5); only 65 have available AND sufficient (L5).
  Proof: G1-G5 hierarchy proves distinct layers; "exists" is only the first layer.

S-04: Evidence Boundary genuinely exists.
  Evidence: 13 cases pass all B1-B6 criteria and C1-C4 counterfactuals.
            9 CONFIRMED (more same-type evidence cannot resolve).
            4 CONDITIONAL (might resolve with page_context).
  Limitation: Single-researcher classification; no live counterfactual.

S-05: Cross-task convergence in Evidence Boundary mechanism.
  Evidence: 3 tasks show same pattern: structural evidence → semantic identity gap.
            Task 1: caption vs reference identity.
            Task 2: column type identity.
            Task 3: tick label identity.
  Limitation: Task 3 has 0 boundary cases (all G1/G2).

S-06: Evidence Boundary is distinguishable from G1-G5.
  Evidence: G1-G3=INSUFFICIENT, G4=INDETERMINATE, G5=BOUNDARY, L5=SUFFICIENT.
            Clean separation: 0 G1-G4 cases are boundary, 0 G5 cases are non-boundary.
  Conclusion: Evidence Boundary = G5 in the G1-G5 framework.

S-07: Evidence exists but is not consumed (G4) is a real pattern.
  Evidence: IS-11 consumer uses binary IS-01/IS-02 heuristic instead of structural P2 evidence.
            100% of decision-relevant evidence exists (Boundary audit); 64% not consumed.
            P1 A/B Pilot: new evidence usage NOT_OBSERVABLE.

S-08: TLD coverage failure is the dominant G2 pattern.
  Evidence: 32/45 IS-11 cases had TLD fail (71%); P2 geometry exists 45/45 (100%).
            Two mechanisms: page-global contamination + inherent low text ratio.
  Limitation: IS-11 specific; may not generalize.

S-09: P0 (Counterfactual) proved objective Evidence Pack improvement.
  Evidence: 27/79 cases improved (E1 > E0); 15/79 burden reduction; 0 regressions.
            Level-3 burden eliminated 8→0; 4 systematic gaps resolved.
  Status: OBJECTIVELY VERIFIED.

S-10: P1 (Human A/B) did NOT confirm Human-level benefit.
  Evidence: INCONCLUSIVE (N=24, 12 per arm); M3 worsened (+2); M6 unchanged (9→9);
            usage NOT_OBSERVABLE; MINOR changes invisible at N=12.
  Status: Honest negative result from sound pre-registered design.
```

### B. PARTIALLY_SUPPORTED

```
Current evidence partially supports these conclusions; limitations remain:

P-01: G1-G5 cross-domain generalization.
  Supported: 5 gap types in ≥3 documents, ≥2 document types.
  Not supported: All 13 documents are academic papers.
  → Non-academic documents NOT_TESTED.

P-02: Minimum Sufficient Evidence is object-independently definable.
  Supported: For structural claims: TARGET+REFERENCE+RELATION+CONTEXT (65 SUFFICIENT cases).
  Not supported: For semantic identity claims: no structural evidence is sufficient.
  → Boundary at L2 (structural) → L3 (semantic identity).

P-03: Evidence Boundary cross-document universality.
  Supported: 9 CONFIRMED boundary cases from 5 documents, 4 document types.
  Not supported: 4 CONDITIONAL cases; academic papers only; no inter-rater validation.
  → Universal claim requires broader validation.

P-04: G1-G5 framework sufficiency as Research Framework.
  Supported: 100% case coverage; cross-task stability; no new gap needed.
  Not supported: Academic-only corpus; 38.6% borderline cases; single researcher.
  → PARTIALLY_SUPPORTED (framework works, generalization limited).

P-05: Evidence Sufficiency classification is reliable.
  Supported: 149 cases classified; clean G1-G5 × Sufficiency matrix separation.
  Not supported: G4 (7 cases) INDETERMINATE; 16 INDETERMINATE total; no inter-rater.
  → Reliable for SUFFICIENT and INSUFFICIENT; less reliable for BOUNDARY and INDETERMINATE.
```

### C. NOT_DEMONSTRATED

```
Current evidence does NOT support these claims:

N-01: Machine can automatically detect Evidence Boundary.
  → All 13 boundary classifications are manual researcher analysis.
  → No automatic detection mechanism exists or is proposed.
  → Required semantic functions (CAPTION_IDENTITY, COLUMN_SEMANTIC_IDENTITY,
    AUTHOR_NAME_RECOGNITION) have no implementation path.

N-02: Evidence Boundary can be reliably quantified.
  → 4/13 boundary cases are CONDITIONAL (might resolve with context).
  → No quantitative boundary metric exists.
  → No inter-rater reliability test.

N-03: G1-G5 holds on non-academic documents.
  → 0 annual reports tested.
  → 0 technical reports tested.
  → 0 manuals tested.
  → 0 business documents tested.
  → All 149 cases are arXiv-style scientific papers.

N-04: Different Human reviewers produce consistent boundary judgments.
  → Single-researcher classification throughout.
  → M-A Pilot: single Human reviewer (inter-rater NOT_AVAILABLE).
  → IS-11: 2 reviewers, 4/45 disagreements (91.1% agreement, Kappa=0.464 moderate).
  → No multi-researcher boundary classification test.

N-05: Evidence Boundary Intelligence Module should be implemented.
  → Missing: non-academic validation, inter-rater reliability, automatic detection,
    semantic function implementation, G4 observability.
  → NOT_READY_FOR_IMPLEMENTATION.

N-06: P1 Human A/B benefit is confirmed.
  → INCONCLUSIVE (N=24, too small; MINOR changes dominant; usage NOT_OBSERVABLE).
  → Cannot claim Evidence Pack improvement produces Human-level benefit.

N-07: The distribution of G1-G5 is generalizable.
  → G2=35.7% is inflated by IS-11 TLD coverage problem.
  → G3=21.4% is inflated by M-A E0 Pack gaps.
  → Different corpus would produce different distribution.
  → Distribution is corpus-dependent, NOT universal.

N-08: Cross-page reference handling is solved.
  → 2 M-A cases (G1) have figure on another page.
  → 4 IS-11 cases are cross-page references.
  → No cross-page detection capability exists.
  → DESIGN_RESEARCH_REQUIRED, not implemented.
```

---

## 6. Known Limitations

```
LIMITATION_REGISTRY:

L-01: ACADEMIC-ONLY CORPUS
  All 149 cases are from arXiv-style scientific papers.
  Non-academic document types are NOT in the corpus.
  Impact: G1-G5 generalization to non-academic = NOT_DEMONSTRATED.

L-02: SINGLE-RESEARCHER CLASSIFICATION
  All G1-G5 and Sufficiency/Boundary classifications are by one researcher.
  No inter-rater reliability test was conducted.
  Impact: Classification reliability unverified.

L-03: SINGLE-HUMAN VALIDATION
  M-A Pilot: N_HUMANS=1 (single-rater).
  IS-11: 2 reviewers, Kappa=0.464 (moderate, below threshold).
  Impact: Human judgment reliability limited.

L-04: G4 NOT_OBSERVABLE
  Consumer behavior (IS-11 IS-01/IS-02) cannot be observed modifying its behavior.
  P1 A/B Pilot: no interaction logs (element visibility, time-per-element).
  Impact: 7 G4 cases INDETERMINATE; Evidence usage attribution impossible.

L-05: NO LIVE COUNTERFACTUAL
  C1-C4 counterfactuals are READ-ONLY reasoning, not live experiments.
  "Would reorganization solve it?" is answered by analysis, not by testing.
  Impact: Counterfactual conclusions are reasoned, not empirically verified.

L-06: P1 A/B PILOT UNDERPOWERED
  N=24 (12 per arm); 7/12 E1 cases had only MINOR changes.
  Cannot detect small effects; confounding (E1 arm had 2× historical UNCERTAIN).
  Impact: Human-level benefit NOT_DEMONSTRATED (INCONCLUSIVE).

L-07: NO NON-ENGLISH DOCUMENTS
  All documents are English-language arXiv papers.
  Impact: Cross-language generalization NOT_TESTED.

L-08: CORPUS BIAS IN DISTRIBUTION
  G2=35.7% inflated by IS-11 TLD coverage problem.
  G3=21.4% inflated by M-A E0 Pack gaps.
  Impact: Observed distribution NOT generalizable.

L-09: CONDITIONAL BOUNDARIES
  4/13 Evidence Boundary cases are CONDITIONAL.
  True boundary count may be 9-13 depending on context availability.
  Impact: Boundary count imprecise.

L-10: DOCUMENT DOMAIN CONCENTRATION
  IS-11: 4 documents (CS/Chemistry).
  M-A: 5 documents (all CS/arxiv).
  Phase 3: 5 documents (astrophysics/earth/bio/medical).
  P7: 4 documents (CS/biology).
  Impact: Limited domain diversity within academic papers.
```

---

## 7. Research Question Registry

File: `tmp/dice_research_question_registry_v1.csv`

| RQ_ID | Research Question | Status | Implementation Required |
|-------|------------------|--------|------------------------|
| RQ-01 | G1-G5 explains different Evidence Failure types? | PARTIALLY_SUPPORTED | FALSE |
| RQ-02 | Evidence Availability ≠ Evidence Sufficiency? | SUPPORTED | FALSE |
| RQ-03 | Evidence Boundary genuinely exists? | SUPPORTED | FALSE |
| RQ-04 | Evidence Boundary has cross-task commonality? | SUPPORTED | FALSE |
| RQ-05 | Machine can automatically detect Evidence Boundary? | NOT_DEMONSTRATED | FALSE |
| RQ-06 | G1-G5 generalizes to non-academic documents? | NOT_DEMONSTRATED | FALSE |
| RQ-07 | Should Evidence Boundary Intelligence be implemented? | NOT_READY_FOR_IMPLEMENTATION | FALSE |
| RQ-08 | Minimum Sufficient Evidence is object-independent? | PARTIALLY_SUPPORTED | FALSE |
| RQ-09 | Evidence Boundary distinguishable from G1-G5? | SUPPORTED | FALSE |
| RQ-10 | Should DICE be modified based on findings? | NOT_SUPPORTED | FALSE |

---

## 8. Next Research Gates

```
NEXT_RESEARCH_GATE_1:
  ID = DOMAIN_GENERALIZATION_GATE
  PURPOSE = Verify G1-G5 + Evidence Sufficiency + Evidence Boundary
            on non-academic documents (annual report, technical report,
            manual, business document, complex PDF)
  PRINCIPLE = Document Diversity ↑ (not N ↑)
  STATUS = REGISTERED (not started)
  IMPLEMENTATION_AUTHORIZED = FALSE
  EXPERIMENT_AUTHORIZED = FALSE

  FUTURE_PRINCIPLES:
    - Must NOT simply add more academic papers
    - Must prioritize document DOMAIN diversity
    - Must NOT create object-specific frameworks
    - Must use existing G1-G5 framework (FROZEN)
    - Must apply B1-B6 boundary criteria (FROZEN)
    - If framework fails → record as FRAMEWORK_LIMITATION, not auto-create G6

NEXT_RESEARCH_GATE_2:
  ID = EVIDENCE_BOUNDARY_STRUCTURE_GATE
  PURPOSE = Research whether Evidence Boundary can be represented as
            "Evidence → Supported Claim → Unsupported Stronger Claim" structure
  PRINCIPLE = Structural analysis only; NO detector, NO score, NO confidence
  STATUS = REGISTERED (not started)
  IMPLEMENTATION_AUTHORIZED = FALSE
  EXPERIMENT_AUTHORIZED = FALSE

  FUTURE_PRINCIPLES:
    - Must NOT implement boundary detector
    - Must NOT add score/confidence
    - Must NOT add runtime authority
    - Must NOT create automatic decision mechanism
    - Must remain READ-ONLY research

RESEARCH_BRAKE_MECHANISM:
  Any new failure case must pass through:
    1. G1-G5 Classification
    2. Evidence Sufficiency assessment
    3. Boundary check (B1-B6)
    4. Cross-case check (≥2 cases from different documents)
    5. Cross-document check
    6. Only then consider new research object

  If existing framework can explain → NO new capability.
  If only one case → NO new Gap Type.
  If only object difference → NO Object-specific Module.
  If only Evidence Pack issue → NO new theory.
```

---

## 9. Over-Design Audit

```
O1: NEW_MODULE = FALSE
  → No new system module created or proposed.

O2: NEW_FIELD = FALSE
  → No new fields added to any system component.

O3: NEW_DETECTOR = FALSE
  → No new detector created or proposed.

O4: NEW_CAPABILITY = FALSE
  → NEW_CAPABILITY = NONE.

O5: RUNTIME_CHANGE = FALSE
  → RUNTIME_AUTHORITY = ZERO. No runtime logic modified.

O6: HUMAN_REVIEW_CHANGE = FALSE
  → No Human Review protocol modified. HUMAN_VALIDATION_AUTHORIZED = FALSE.

O7: OBJECT_SPECIFIC_FRAMEWORK = FALSE
  → Framework is Task-based (T1/T2/T3), not object-based.
  → No Figure/Table/Caption-specific framework.

O8: G6_CREATED = FALSE
  → No G6 created. G1-G5 remains the framework.
  → 0 true new gap candidates identified.

ALL CHECKS: FALSE (PASS)
OVER_DESIGN_RISK = NONE
```

---

## 10. Forbidden Statements

```
The following statements are FORBIDDEN in any DICE research output:

  ✗ "DICE 已经解决 Evidence Boundary"
    → Evidence Boundary is IDENTIFIED, not SOLVED. 9 CONFIRMED + 4 CONDITIONAL.

  ✗ "DICE 可以自动判断 Evidence 是否足够"
    → No automatic detection mechanism exists. All classification is manual.

  ✗ "G1-G5 是普适理论"
    → G1-G5 is PARTIALLY_SUPPORTED. Academic papers only. Non-academic NOT_TESTED.

  ✗ "Evidence Boundary 已经可以自动检测"
    → NOT_DEMONSTRATED. No automatic detection exists.

  ✗ "G5 = 所有人类不确定性"
    → G5 = 13/149 = 8.7% of cases. 55 are INSUFFICIENT (G1-G3), not G5.
    → G5 is a SPECIFIC condition: evidence complete + semantic interpretation needed.

CORRECT STATEMENTS:
  ✓ "G1-G5 classified 100% of 70 observed failure cases from academic papers."
  ✓ "Evidence Boundary exists in 13 cases (9 CONFIRMED) within the current corpus."
  ✓ "Evidence Boundary = G5 in the G1-G5 framework."
  ✓ "Non-academic generalization is NOT_DEMONSTRATED."
  ✓ "Automatic boundary detection is NOT_DEMONSTRATED."
```

---

## 11. Final Questions

### Q1: 当前 DICE 第一阶段是否已经达到 Research Baseline Freeze 条件？

```
YES

  CONDITIONS MET:
    1. G1-G5 framework defined and validated (70/70 = 100%)
    2. Evidence Sufficiency analyzed (149 cases, 4-state classification)
    3. Evidence Boundary identified (13 candidates, 9 CONFIRMED)
    4. Cross-task convergence demonstrated (3 tasks, same mechanism)
    5. Frozen baseline verified INTACT (6 shas, drift=0)
    6. All research questions registered (RQ-01 to RQ-10)
    7. Known limitations documented (L-01 to L-10)
    8. Next research gates defined (2 gates, not started)
    9. Over-design audit passed (8 checks, all FALSE)
    10. No pending implementation/experiment/human validation

  The research has reached a stable state where:
    - What is known is clearly defined (SUPPORTED findings)
    - What is partially known is clearly bounded (PARTIALLY_SUPPORTED)
    - What is unknown is clearly listed (NOT_DEMONSTRATED)
    - The framework is FROZEN and ready for future validation
```

### Q2: 当前最重要的研究成果是什么？

```
The most important research achievement is NOT accuracy, NOT a module, NOT a capability.

It is the ESTABLISHMENT OF THE RELATIONSHIP:

  G1-G5 Evidence Gap Framework
    ↕ (maps to)
  Evidence Sufficiency (SUFFICIENT/INSUFFICIENT/BOUNDARY/INDETERMINATE)
    ↕ (maps to)
  Evidence Boundary (B1-B6 criteria, C1-C4 counterfactuals)

  Specifically:
    G1-G3 → INSUFFICIENT (evidence blocked before reaching Human)
    G4    → INDETERMINATE (consumer behavior unknown)
    G5    → BOUNDARY (evidence complete, semantic ceiling)
    L5    → SUFFICIENT (definitive judgment made)

  This means:
    - Evidence Boundary = G5 (they are the same thing)
    - The boundary is at L2 (structural claim) → L3 (semantic identity)
    - Structural evidence supports association/boundary/proximity claims
    - Semantic identity claims require interpretation beyond evidence
    - This pattern is STABLE across 3 tasks and 13 documents

  The framework tells us:
    WHERE the evidence breaks (G1-G5)
    WHETHER the Human can judge (Sufficiency)
    WHAT the evidence can support (Claim Level / Boundary)

  This is a Research Framework, not a system capability.
```

### Q3: 当前最大的未知是什么？

```
Three critical unknowns:

  UNKNOWN_1: NON-ACADEMIC GENERALIZATION (highest priority)
    All 149 cases are academic papers.
    G1-G5 + Evidence Boundary may or may not hold on:
      - Annual reports (complex tables, financial data)
      - Technical reports (diagrams, specifications)
      - Manuals (instructions, multi-column layouts)
      - Business documents (forms, mixed content)
    → DOMAIN_GENERALIZATION_GATE needed.

  UNKNOWN_2: HUMAN-INDEPENDENT VALIDATION
    All classifications are by one researcher.
    M-A Pilot: single Human reviewer.
    IS-11: 2 reviewers, Kappa=0.464 (moderate).
    Boundary classification reliability is UNVERIFIED across:
      - Different researchers
      - Different Human reviewers
      - Different annotation protocols
    → Inter-rater reliability test needed.

  UNKNOWN_3: BOUNDARY AUTOMATICITY
    No machine can detect Evidence Boundary automatically.
    All 13 boundary cases required manual B1-B6 analysis.
    Required semantic functions (CAPTION_IDENTITY etc.) have no implementation path.
    → EVIDENCE_BOUNDARY_STRUCTURE_GATE needed (research only, no implementation).
```

### Q4: 现在是否应该修改 DICE？

```
NO

  The research CONFIRMS the framework, not a deficiency requiring modification.

  Evidence:
    1. G1-G5 is stable (100% coverage, 0 new gap needed)
    2. Evidence Boundary = G5 (already in framework)
    3. Minimum Sufficient Evidence already in E1 Evidence Pack (FROZEN)
    4. Semantic boundary is a legitimate Human judgment boundary (not fixable)
    5. G1-G4 issues are KNOWN (TLD coverage, consumer integration) — fixing
       requires IMPLEMENTATION (not authorized)
    6. No new module/field/detector/capability warranted

  DICE must remain FROZEN.
  SYSTEM_MODIFIED = FALSE.
```

### Q5: 下一研究入口是什么？

```
NEXT_RESEARCH_GATE = DOMAIN_GENERALIZATION_GATE

  Purpose: Verify G1-G5 + Evidence Sufficiency + Evidence Boundary
           on non-academic documents.

  Principles:
    - Document Diversity ↑ (not N ↑)
    - Must NOT simply add more academic papers
    - Must use existing FROZEN framework
    - If framework fails → record as FRAMEWORK_LIMITATION

  STATUS = REGISTERED (not started)
  IMPLEMENTATION_AUTHORIZED = FALSE
  EXPERIMENT_AUTHORIZED = FALSE

  SECONDARY_GATE = EVIDENCE_BOUNDARY_STRUCTURE_GATE
  Purpose: Research whether Evidence Boundary can be structurally represented.
  STATUS = REGISTERED (not started)
  No detector, no score, no confidence, no runtime authority.

  IMPORTANT:
    These gates are REGISTERED for future reference.
    They are NOT authorized to start.
    STOP = TRUE after this baseline freeze.
```

---

## 12. Final Governance State

```
RESEARCH_BASELINE = FROZEN

SYSTEM_MODIFIED = FALSE

IMPLEMENTATION_AUTHORIZED = FALSE

EXPERIMENT_AUTHORIZED = FALSE

HUMAN_VALIDATION_AUTHORIZED = FALSE

FROZEN_BASELINE = INTACT

BASELINE_DRIFT = 0

NEW_CAPABILITY = NONE

RUNTIME_AUTHORITY = ZERO

PRODUCTION = FALSE

STOP = TRUE
```

---

## 13. Files Created

```
tmp/dice_research_baseline_v1.md         (this file)
tmp/dice_research_baseline_v1.json        (structured registry)
tmp/dice_research_question_registry_v1.csv (RQ-01 to RQ-10)
```

---

## 14. Research Artifact Index (Canonical Outputs)

| # | File | Research Phase | Key Content |
|---|------|---------------|-------------|
| 1 | ao_visual_geometry_contract_design.md | AO Extension | Visual geometry contract |
| 2 | ao_visual_geometry_value_experiment.md/.json | AO Extension | Value experiment |
| 3 | m_a_caption_association_design_research.md | M-A Design | Research Object definition |
| 4 | m_a_evidence_sufficiency_gap_diagnostic.md | M-A Diagnostic | 9-case gap diagnosis |
| 5 | m_a_human_validation_pilot_analysis.md/.json/.csv | M-A E0 Pilot | 79-case analysis |
| 6 | m_a_evidence_pack_counterfactual_diagnostic.md/.csv | P0 Counterfactual | E0 vs E1, 79 cases |
| 7 | m_a_evidence_pack_implementation_report.md/.json | E1 Implementation | PR1/PR2/PR3 |
| 8 | m_a_evidence_pack_pre_implementation_resolution_gate.md | E1 Gate | Pre-registration |
| 9 | m_a_human_ab_pilot_design_gate.md/.json | P1 Design | A/B design, M1-M6 |
| 10 | m_a_human_ab_pilot_result_analysis.md/.json/.csv | P1 Results | INCONCLUSIVE |
| 11 | m_a_p0_p1_translation_gap_diagnostic.md/.json/.csv | P0→P1 Gap | 3 translation factors |
| 12 | human_evidence_requirement_research.md/.json/.csv | Evidence Requirement | G1-G5, F1-F12, MSE |
| 13 | g1_g5_cross_document_validation.md/.json/.csv×3 | G1-G5 Validation | 70 cases, 13 docs |
| 14 | evidence_sufficiency_boundary_research.md/.json/.csv×3 | Sufficiency/Boundary | 149 cases, B1-B6 |
| 15 | dice_research_baseline_v1.md/.json/.csv | Baseline Freeze | This file |

---

## STOP

```
Research Baseline v1 is FROZEN.

下一步研究入口已登记 (DOMAIN_GENERALIZATION_GATE + EVIDENCE_BOUNDARY_STRUCTURE_GATE)
但未授权启动。

不得自动开始任何 Gate。
不得修改任何系统。
不得创建新模块/字段/检测器/能力。
不得增加 G6。
不得开始新 Human Experiment。

STOP = TRUE
```
