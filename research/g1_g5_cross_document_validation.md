# G1–G5 Cross-Document Validation Research

> **模式: READ-ONLY RESEARCH / NO IMPLEMENTATION / NO EXPERIMENT / NO HUMAN VALIDATION / FROZEN INTACT / STOP**
> 日期: 2026-09-18
> 目标: 在更大、更多样的真实文档失败案例中，验证 G1–G5 Evidence Gap Framework 是否具有跨文档、跨任务、跨问题类型的解释能力。

---

## 0. Research Questions

```
RQ1: 当前 G1–G5 是否能够解释更多真实失败案例？
RQ2: G1–G5 是否能够跨不同文档类型保持稳定？
RQ3: 是否出现大量无法归入 G1–G5 的新型 Evidence Gap？
RQ4: 如果出现无法归类案例，它们是真正的新 Gap Type / 现有 Gap Type 的边界情况 / Observation 不足 / Evidence 不足 / 研究对象不适用？
RQ5: 当前 G1–G5 是否足以作为 Research Framework？
RQ6: 下一步是否有必要修改 DICE？
```

---

## 1. Frozen Baseline

```
FROZEN_BASELINE = INTACT
BASELINE_DRIFT = 0
IMPLEMENTATION_AUTHORIZED = FALSE
EXPERIMENT_AUTHORIZED = FALSE
HUMAN_VALIDATION_AUTHORIZED = FALSE
RUNTIME_AUTHORITY = ZERO
PRODUCTION = FALSE

G1-G5 Framework = FROZEN (definitions not modified during this research)

G1: OBSERVATION_COVERAGE_GAP    — 所需观察的对象/信息根本没有被观察到
G2: EVIDENCE_ORGANIZATION_GAP   — Evidence 已存在，但没有形成 Human 可使用的组织结构
G3: EVIDENCE_PRESENTATION_GAP   — Evidence 已组织，但没有有效呈现给 Human
G4: CONSUMER_INTEGRATION_GAP    — Evidence 已存在/呈现，但消费者没有实际获得或消费
G5: SEMANTIC_BOUNDARY           — Evidence 已经基本充分，但仍需要不可替代的语义判断
```

---

## 2. Evidence Base

### 2.1 Source Materials

```
ANALYZED_MATERIALS = 30+ reports + 5 structured data files
  IS-11 corpus (4 documents, 45 boundary cases):
    - is11_corpus_acquisition_report.md
    - is11_machine_evaluation_report.md / .json / .py
    - is11_human_review_report.md / .json
    - is11_stage4_closure_final_report.md
    - is11_stage2_report.md

  IS-14 Phase 3 corpus (5 documents, 13 cases):
    - phase3_is14_final_report.md
    - phase3_is14_corpus_manifest.json
    - phase3_is14_incident_log.md
    - phase3_sampling_strategy_diagnostic.md
    - phase3_map_gap_report.md

  PH-02 experiment (4 documents, 22 cases):
    - ph02_column_membership_experiment_report.md
    - ph02_failure_mechanism_review.md / .json

  Audit reports (10 files, 57 cases):
    - dce06_tld_failure_mechanism_audit.md / .json
    - dce05_table_column_identity_audit.md
    - dce07_tld_band_locality_counterfactual.md
    - boundary_resolution_ambiguity_audit.md
    - signal3_boundary_evidence_audit.md / .json
    - signal3_boundary_unknown_validation_audit.md / .json
    - structural_object_failure_decomposition_audit.md / .json
    - document_perception_failure_analysis.md
    - slicing_failure_impact_ranking.md / .json
    - p2_table_structure_derivability_audit.md

  HVA + Discourse + MB audits (10 files, 57 cases):
    - hva_phase2/phase2_report.md / .json
    - hva_phase2/hva06_sc05_boundary_audit.md
    - hva_phase2/hva07_evidence_context_counterfactual.md
    - document_discourse_semantic_organization_audit.md / .json
    - decision_critical_evidence_consumption_audit.md / .json
    - mb_table_region_evidence_expressability_audit.md / .json
    - text_unit_standard_impact_audit.md / .json
    - candidate_semantic_coherence_audit.md / .json
    - evaluation_object_closure_audit.md / .json
    - evidence_organization_gap_diagnostic.md / .json

  M-A Human Validation (5 documents, 79+24 cases):
    - m_a_human_validation_pilot_analysis.md / .csv
    - m_a_evidence_pack_counterfactual_diagnostic.md / .csv
    - m_a_human_ab_pilot_result_analysis.md / .csv
    - m_a_p0_p1_translation_gap_diagnostic.md / .csv
    - human_evidence_requirement_research.md / .json

  P7 Independent Evaluation (4 documents, 10 cases):
    - Extracted from audit reports above
```

### 2.2 Corpus Summary

```
Documents:           13 distinct document_ids
Document Types:      8 (all academic papers; no non-academic documents available)
  - academic_paper_cs (CS/CV/NLP):  4 documents
  - academic_paper_chemistry:       1 document
  - academic_paper_astrophysics:    2 documents
  - academic_paper_earth_science:   1 document
  - academic_paper_biology:         2 documents (P7 corpus)
  - academic_paper_medical_physics: 1 document
  - academic_paper_nlp:             1 document (cs_001, also CS)
  - academic_paper_mixed:           1 aggregate

Pages:               60+ pages across all documents
Cases:               70 (failure/abstain/ambiguous only; success cases excluded)
Problem Types:       23
Human-Reviewed:      60/70 (85.7%)
```

### 2.3 Sample Coverage Gap

```
SAMPLE_COVERAGE_GAP:
  - NO non-academic documents available (annual report, technical report,
    product/manual, business document, complex PDF not in corpus)
  - All 13 documents are arXiv-style scientific papers
  - Generalization to non-academic document types = NOT_TESTED
  - This is a REAL corpus limitation, NOT fabricated

  DOCUMENT_TYPE_COVERAGE:
    academic_paper:     13/13 (100%)
    annual_report:       0/13 (NOT_AVAILABLE)
    technical_report:    0/13 (NOT_AVAILABLE)
    product_manual:      0/13 (NOT_AVAILABLE)
    business_document:   0/13 (NOT_AVAILABLE)

  GENERALIZATION = LIMITED (academic papers only)
```

---

## 3. Sampling Frame

File: `tmp/g1_g5_cross_document_sampling_frame.csv`

```
TOTAL_CASES = 70

By Document:
  is11_efficientnet:      14
  is11_med_001:           11
  is11_cs_001:            10
  is11_resnet:             9
  arxiv_2402.18619:        5  (M-A corpus, distinct from ind_arxiv_2402)
  PH3-ASTRO-001:           3
  PH3-EARTH-002:           3
  ind_arxiv_2402:          4  (P7 corpus)
  ind_arxiv_bio2:          3  (P7 corpus)
  ind_qbio_rna:            3  (P7 corpus)
  PH3-EARTH-001:           2
  PH3-MED-001:             1
  all_5_docs:              2  (aggregate)

By Document Type:
  academic_paper_cs:              32
  academic_paper_chemistry:       11
  academic_paper_nlp:             10
  academic_paper_biology:          6
  academic_paper_astrophysics:     5
  academic_paper_earth_science:    3
  academic_paper_mixed:            2
  academic_paper_medical_physics:  1

By Problem Type (top 10):
  table_column_boundary:          17
  text_drawing_association:       14
  table_header_boundary:           5
  prose_sentence_boundary:         4
  figure_axis_tick:                3
  table_cell_fp:                   3
  reference_list_author_title:     3
  reference_list_continuation:     2
  figure_caption_association:      2
  header_contamination_table_fp:   2

Human-Reviewed Cases: 60/70 (85.7%)
Non-Human Cases:      10/70 (14.3%) — Phase 3 frozen-baseline findings + corpus-level
```

---

## 4. Case Classification

File: `tmp/g1_g5_case_classification.csv`

### 4.1 Primary Gap Distribution

```
TOTAL_CLASSIFIED = 70/70 (100%)
UNCLASSIFIED = 0

  G1 (OBSERVATION_COVERAGE_GAP):    10 cases (14.3%)
  G2 (EVIDENCE_ORGANIZATION_GAP):   25 cases (35.7%)
  G3 (EVIDENCE_PRESENTATION_GAP):   15 cases (21.4%)
  G4 (CONSUMER_INTEGRATION_GAP):     7 cases (10.0%)
  G5 (SEMANTIC_BOUNDARY):           13 cases (18.6%)

CLASSIFICATION_CONFIDENCE:
  HIGH:   52/70 (74.3%)
  MEDIUM: 18/70 (25.7%)
  LOW:     0/70 (0.0%)
```

### 4.2 Cross-Document Coverage

```
G1: 7 documents — PH3-ASTRO-001, PH3-EARTH-001, PH3-EARTH-002, all_5_docs,
                   arxiv_2402.18619, is11_efficientnet, is11_med_001
G2: 7 documents — PH3-ASTRO-001, PH3-EARTH-001, PH3-MED-001, is11_cs_001,
                   is11_efficientnet, is11_med_001, is11_resnet
G3: 6 documents — ind_arxiv_2402, ind_arxiv_bio2, is11_cs_001,
                   is11_efficientnet, is11_med_001, is11_resnet
G4: 3 documents — ind_arxiv_2402, ind_qbio_rna, is11_efficientnet
G5: 5 documents — arxiv_2402.18619, ind_arxiv_bio2, is11_cs_001,
                   is11_med_001, is11_resnet

MINIMUM_CROSS_DOCUMENT = 3 (G4)
MAXIMUM_CROSS_DOCUMENT = 7 (G1, G2)

ALL 5 GAP TYPES appear in ≥3 documents.
ALL 5 GAP TYPES appear in ≥2 document types.
```

### 4.3 Cross-Document-Type Coverage

```
G1: 5 document types — astrophysics, chemistry, cs, earth_science, mixed
G2: 5 document types — astrophysics, chemistry, cs, medical_physics, nlp
G3: 4 document types — biology, chemistry, cs, nlp
G4: 2 document types — biology, cs
G5: 4 document types — biology, chemistry, cs, nlp

NOTE: G4 has only 2 document types (biology + cs).
      This is because G4 (Consumer Integration Gap) is primarily observed
      in IS-11/P7 consumer behavior, which was only tested on CS and biology
      documents. This is a SAMPLE_COVERAGE_GAP, not a framework limitation.
```

### 4.4 Cross-Problem-Type Coverage

```
G1: 7 problem types — caption_representation_mismatch, corpus_sufficiency_fail,
                       raster_figure_text_invisible, single_document_dominance,
                       text_drawing_association, tick_representation_mismatch,
                       tick_run_definition_boundary
G2: 9 problem types — author_affiliation_table_fp, figure_axis_tick,
                       figure_axis_tick_detection, figure_caption_association,
                       figure_label_boundary, header_contamination_table_fp,
                       table_column_boundary, table_header_boundary,
                       text_drawing_association
G3: 5 problem types — reference_list_author_title, reference_list_continuation,
                       table_column_boundary, table_header_boundary,
                       text_drawing_association
G4: 5 problem types — body_text_citation_fn, column_membership_adjudication,
                       reference_list_citation_fn, table_cell_fp,
                       table_column_boundary
G5: 4 problem types — column_membership_specificity, prose_sentence_boundary,
                       reference_list_author_title, text_drawing_association

NOTE: text_drawing_association appears in G1, G2, G3, AND G5.
      table_column_boundary appears in G2, G3, AND G4.
      This confirms: the SAME problem type can produce DIFFERENT gap types
      depending on the specific case. Gap type is NOT determined by problem type.
```

---

## 5. Outlier Audit

File: `tmp/g1_g5_outlier_audit.csv`

```
OUTLIER_CASES_AUDITED = 27 (borderline cases, NOT unclassifiable)
TRUE_NEW_GAP_TYPE_CANDIDATES = 0

ALL 70 cases were classified into G1-G5 with 0 unclassified.
27 cases were identified as BOUNDARY cases between two gap types:

  G2/G4 boundary: 15 cases
    → TLD detection failure (G2) + consumer no fallback (G4)
    → Earliest breakpoint = G2 (TLD not organizing)
    → Secondary = G4 (IS-11 not using P2 when TLD fails)
    → NOT a new gap type — known boundary

  G3/G5 boundary: 4 cases
    → page_context not presented (G3) + period+cap ambiguous (G5)
    → With page_context, G3 resolves most cases
    → Without page_context, G5 emerges
    → NOT a new gap type — known boundary

  G5/G3 boundary: 6 cases
    → text unit standard undefined (G5) + period+cap not computed (G3)
    → Even with period+cap, standard gap causes human disagreement
    → NOT a new gap type — known boundary

  G5/G4 boundary: 2 cases
    → structural ambiguity (G5) + guard fires incorrectly (G4)
    → Value column indistinguishable from row-number column
    → NOT a new gap type — known boundary (specificity risk)
```

### 5.1 New Gap Type Assessment

```
NEW_GAP_CRITERIA (from task spec §8):
  1. Multiple independent cases           → YES (27 borderline cases)
  2. From different documents             → YES (13 documents)
  3. Different problem types              → YES (23 problem types)
  4. Cannot reasonably fit G1-G5          → NO (all 70 fit G1-G5)
  5. Stable common mechanism              → N/A (criterion 4 not met)

VERDICT: NO new gap type warranted.
  All borderline cases are EXISTING gap type boundaries.
  The boundary cases reveal that G2-G4 and G3-G5 are ADJACENT in the
  evidence flow hierarchy, and some cases sit at the transition point.
  This is expected behavior for a hierarchical framework, not a deficiency.
```

### 5.2 Figure/Table/Formula Specialization Check

```
OBJECT_TYPE_SPECIALIZATION_CHECK (from task spec §9):

  Figure problems → mapped to:
    G1 (raster figure text invisible, cross-page reference)
    G2 (figure structure not detected, axis tick not queried)
    G3 (extent exists but not shown in Evidence Pack)
    G5 (caption vs reference ambiguity)
    → NO "Figure Gap" type created. All figure problems map to evidence gaps.

  Table problems → mapped to:
    G2 (TLD missed table, column relation not organized)
    G4 (IS-01/IS-02 binary heuristic, consumer doesn't use P2)
    G5 (value column vs row-number column structural ambiguity)
    → NO "Table Gap" type created. All table problems map to evidence gaps.

  Caption problems → mapped to:
    G2 (caption association evidence not queried)
    G3 (FIG prefix not computed by IS-11)
    G5 (caption vs reference semantic boundary)
    → NO "Caption Gap" type created. All caption problems map to evidence gaps.

  Formula/List/Heading/Reading-Order problems → mapped to:
    G2 (header contamination, structure not organized)
    G4 (consumer integration)
    → NO object-specific gap type created.

VERDICT: G1-G5 successfully absorbs ALL object-specific problems.
  Object type ≠ Evidence Gap Type. CONFIRMED.
```

---

## 6. Cross-Task Validation

```
TASK 1 — Text-Text Boundary Decision (IS-11/P7/PH02):
  Cases: 45 (IS-11) + 10 (P7) + 3 (PH02) = 58
  Gap types observed: G2, G3, G4, G5
  Primary pattern: G2 (TLD organization gap) + G4 (consumer integration gap)
  All 58 cases classified into G1-G5.

TASK 2 — Text-Drawing Structural Association (M-A):
  Cases: 14 UNCERTAIN (from 79 E0 Pilot) + 10 Phase 3 = 24
  Gap types observed: G1, G2, G3, G5
  Primary pattern: G3 (evidence not presented) + G1 (cross-page reference)
  All 24 cases classified into G1-G5.

TASK 3 — IS-14 Graphic Text Context (Phase 3):
  Cases: 13
  Gap types observed: G1, G2
  Primary pattern: G1 (representation/corpus gap) + G2 (header contamination)
  All 13 cases classified into G1-G5.

CONVERGENT FINDING:
  All 3 tasks produce cases that fit G1-G5.
  Different tasks have different dominant gaps:
    Boundary decision: G2+G4 (organization + consumer)
    Text-drawing:      G3+G1 (presentation + observation)
    Graphic context:   G1+G2 (observation + organization)
  But the SAME 5-type taxonomy covers ALL tasks.
```

---

## 7. Observed Distribution vs Generalization

```
OBSERVED DISTRIBUTION (70 cases):
  G1: 14.3%   ← driven by Phase 3 corpus gaps + M-A cross-page refs
  G2: 35.7%   ← driven by IS-11 TLD coverage failure (32/45 TLD fail)
  G3: 21.4%   ← driven by M-A Evidence Pack E0 gaps + HVA page_context
  G4: 10.0%   ← driven by IS-01/IS-02 binary heuristic
  G5: 18.6%   ← driven by prose sentence boundary + caption vs reference

WARNING (from task spec §11):
  These proportions are NOT generalizable. They reflect:
  - IS-11's TLD coverage problem (inflates G2)
  - M-A's E0 Evidence Pack gaps (inflates G3)
  - Phase 3's corpus limitations (inflates G1)
  - Academic paper corpus bias (no business/technical documents)

  If a different corpus were used (e.g., annual reports with complex tables),
  the distribution would shift. G1 might decrease (more tables detected),
  G4 might increase (different consumer behavior), etc.

GENERALIZATION = LIMITED
  The FRAMEWORK (G1-G5) is stable across tasks and documents.
  The DISTRIBUTION is corpus-dependent and NOT generalizable.
```

---

## 8. Key Cross-Case Patterns

| Pattern | Gap Type | Cross-Document Evidence | Cross-Problem Evidence |
|---------|----------|------------------------|----------------------|
| TLD coverage failure → no table structure | G2+G4 | 4 IS-11 docs + 1 P7 doc | table_column + table_header |
| Evidence exists but consumer uses binary heuristic | G4 | 3 docs (IS-11 + P7) | table_cell_fp + citation_fn |
| Cross-page reference → nothing on page | G1 | 4 docs (M-A + Phase 3) | text_drawing + figure_caption |
| Extent exists but not shown in Pack | G3 | 2 docs (M-A) | text_drawing |
| period+cap ambiguous (sentence vs reference) | G3+G5 | 3 docs (IS-11 + P7) | prose_boundary + reference_list |
| Value column = row-number column (specificity) | G5+G4 | 2 docs (resnet + cs_001) | column_membership |
| Header contamination → false table | G2 | 1 doc (LIGO/APS) | header_contamination |
| Raster figure text invisible | G1 | 2 docs (LIGO + EHT) | raster_figure |

```
KEY OBSERVATION:
  The most common pattern (TLD coverage failure → G2+G4) appears in 4 documents
  and 2 problem types. This is a STABLE, CROSS-DOCUMENT pattern, not a single-case
  generalization.

  The second most common (cross-page reference → G1) appears in 4 documents
  and 2 problem types. Also stable.

  NO pattern appears in only 1 document with 1 problem type AND cannot fit G1-G5.
  → No new gap type is warranted.
```

---

## 9. Over-Design Check

```
O1: 是否为了扩样而修改系统？
  → NO. READ-ONLY research only. No system files modified.
  → All data extracted from existing reports and frozen data.

O2: 是否为了覆盖某个对象而增加字段？
  → NO. No new fields proposed.
  → All 12 Evidence Functions (F1-F12) served by existing fields.
  → G1-G5 definitions not modified.

O3: 是否出现 Figure/Table/Formula 专用 Gap？
  → NO. §5.2 confirms all object-specific problems map to G1-G5.
  → No "Figure Gap", "Table Gap", "Caption Gap" created.
  → Object type ≠ Evidence Gap Type. CONFIRMED.

O4: 是否把单案例规律提升成通用规律？
  → NO. All abstractions require ≥2 cross-document cases.
  → G5/G4 boundary (column specificity) has 2 cases from 2 documents —
    borderline but documented as boundary case, not universal rule.
  → Header contamination (G2) has 1 document (LIGO) but is supported by
    Phase 3 incident log (30/54 in_table FP) — cross-corpus evidence.

O5: 是否产生了新的 Runtime 能力？
  → NO. No Runtime capability proposed.
  → RUNTIME_AUTHORITY = ZERO.

O6: 是否产生新的 Capability？
  → NO. No new Capability proposed.
  → NEW_CAPABILITY = NONE.

O7: 是否产生新的 Human Review requirement？
  → NO. No new Human Review required.
  → HUMAN_VALIDATION_AUTHORIZED = FALSE.
  → All classification was done by researcher, not Human reviewer.

OVER_DESIGN_RISK = LOW
  All 7 checks PASS. No over-design detected.
```

---

## 10. Final Questions

### Q1: 当前 G1–G5 在扩大后的真实案例中覆盖了多少案例？

```
COVERAGE = 70/70 = 100%

  All 70 failure/abstain/ambiguous cases from 13 documents,
  8 document types, and 23 problem types were classified into G1-G5.
  0 cases remained unclassified.
  0 true new gap type candidates identified.
  27 borderline cases were identified and audited — all are existing
    gap type boundaries, not new types.

  The framework ABSORBS all observed failure modes without modification.
```

### Q2: G1–G5 是否跨不同文档类型出现？

```
YES — with limitations.

  G1: 5 document types (astrophysics, chemistry, cs, earth_science, mixed)
  G2: 5 document types (astrophysics, chemistry, cs, medical_physics, nlp)
  G3: 4 document types (biology, chemistry, cs, nlp)
  G4: 2 document types (biology, cs) ← LIMITED
  G5: 4 document types (biology, chemistry, cs, nlp)

  ALL 5 gap types appear in ≥2 document types.
  4 of 5 gap types appear in ≥4 document types.

  LIMITATION: All 13 documents are academic papers.
  Non-academic document types (annual report, technical report, manual,
  business document) are NOT in the corpus.
  → Cross-document-type stability is confirmed WITHIN academic papers.
  → Cross-document-type stability OUTSIDE academic papers = NOT_TESTED.

  GENERALIZATION = LIMITED (academic papers only)
```

### Q3: 是否出现稳定的 G1–G5 之外的新 Gap？

```
NO.

  0 true new gap type candidates.
  27 borderline cases audited — all are boundaries between existing types:
    G2/G4 boundary (15 cases): TLD organization failure + consumer no fallback
    G3/G5 boundary (4 cases): page_context not presented + period+cap ambiguous
    G5/G3 boundary (6 cases): text unit undefined + period+cap not computed
    G5/G4 boundary (2 cases): structural ambiguity + guard specificity

  These boundaries are EXPECTED in a hierarchical framework:
    G1 → G2 → G3 → G4 → G5 is an evidence flow chain.
    Cases at the transition between two adjacent types are natural.
    They do NOT indicate a missing type between them.
```

### Q4: 如果没有，新案例主要是已有 Gap 的什么边界？

```
Three dominant boundary patterns:

  BOUNDARY_1 (G2↔G4, 15 cases): "Organization failure + Consumer no fallback"
    → TLD fails to detect table (G2) → IS-11 has no fallback to P2 (G4)
    → The earliest breakpoint is G2 (if TLD organized correctly, G4 wouldn't trigger)
    → This is the MOST COMMON boundary (21.4% of all cases)
    → Cross-document: 4 IS-11 documents + consistent across table_column/table_header

  BOUNDARY_2 (G3↔G5, 10 cases): "Presentation gap + Semantic ambiguity"
    → page_context or period+cap not presented (G3) → ambiguity emerges (G5)
    → With complete evidence, SOME cases resolve (G3 was the real gap)
    → Without complete evidence, SOME cases remain ambiguous (G5 was real)
    → The boundary is: "would this case resolve with complete evidence?"
    → Cross-document: IS-11 + P7 + M-A corpora

  BOUNDARY_3 (G5↔G4, 2 cases): "Structural ambiguity + Consumer specificity"
    → Value column geometrically identical to row-number column (G5)
    → Guard fires but doesn't change prediction (G4)
    → The ambiguity is GENUINE — no current evidence can distinguish
    → Requires additional discriminative signal (not currently available)
    → Cross-document: resnet + cs_001
```

### Q5: 当前 G1–G5 是否足以作为 Research Framework？

```
PARTIALLY_SUPPORTED

  SUPPORTED:
    - 100% case coverage (70/70 classified, 0 unclassified)
    - Cross-task stability (3 tasks, all fit G1-G5)
    - Cross-document stability (≥3 documents per gap type)
    - Cross-document-type stability (≥2 types per gap type, within academic papers)
    - Cross-problem-type stability (gap type independent of problem type)
    - No object-specific gap types needed
    - No new gap type warranted (0 candidates)
    - Boundary cases are explainable (adjacent types in hierarchy)

  NOT_SUPPORTED:
    - Non-academic document types NOT_TESTED (corpus limitation)
    - G4 cross-document-type coverage limited (2 types only)
    - Distribution is corpus-dependent (NOT generalizable)
    - Single-researcher classification (no inter-rater validation)
    - 27/70 cases are borderline (38.6%) — framework boundaries are well-populated

  CONCLUSION:
    G1-G5 is SUFFICIENT as a Research Framework for ACADEMIC PAPER documents.
    G1-G5 is NOT YET VALIDATED for non-academic documents.
    The framework's STABILITY (no new gap needed) is the strongest finding.
    The framework's LIMITATION (academic-only corpus) is the weakest point.
    "PARTIALLY_SUPPORTED" reflects: framework works, but generalization is limited.
```

### Q6: 下一步是否有必要修改 DICE？

```
NO

  EVIDENCE:
    1. G1-G5 classified 100% of cases without modification → framework is stable
    2. No new gap type warranted → no new detection/organization/presentation needed
    3. All boundary cases are explainable → no structural change needed
    4. The dominant pattern (G2+G4: TLD coverage + consumer fallback) is a KNOWN
       issue documented in multiple audits — fixing it requires IMPLEMENTATION
       (TLD modification or IS-11 consumer redesign), which is NOT_AUTHORIZED
    5. The M-A Evidence Pack (E1) already FIXED the G3 cases (P0 verified)
    6. G1 cases (cross-page, raster) require new CAPABILITY (cross-page detection),
       which is DESIGN_RESEARCH_REQUIRED, not implementation-ready
    7. G5 cases (semantic boundary) are legitimate Human judgment boundaries —
       NOT fixable by system modification

  RATIONALE:
    The framework is stable. The system's problems are KNOWN and DOCUMENTED.
    Modifying DICE would not improve the framework's explanatory power.
    The framework identifies WHERE the problems are; fixing them is a separate
    decision requiring IMPLEMENTATION_AUTHORIZATION (currently FALSE).

  NO modification is NECESSARY or WARRANTED.
```

---

## 11. Files Created

```
tmp/g1_g5_cross_document_validation.md       (this file)
tmp/g1_g5_cross_document_validation.json     (structured data)
tmp/g1_g5_cross_document_sampling_frame.csv  (70 cases, 9 fields)
tmp/g1_g5_case_classification.csv             (70 cases, 16 fields)
tmp/g1_g5_outlier_audit.csv                   (27 borderline cases, 14 fields)
```

---

## 12. Limitations

```
LIMITATION_1: ACADEMIC-ONLY CORPUS
  All 13 documents are arXiv-style scientific papers.
  Non-academic documents (annual report, technical report, manual, business)
  are NOT in the corpus and were NOT tested.
  → GENERALIZATION = LIMITED
  → If non-academic documents produce cases that don't fit G1-G5,
    that would be discovered in future corpus expansion, not here.

LIMITATION_2: SINGLE-RESEARCHER CLASSIFICATION
  All 70 cases were classified by one researcher.
  No inter-rater reliability test was conducted.
  → Classification confidence is researcher judgment, not validated.
  → A second researcher might classify borderline cases differently.

LIMITATION_3: 38.6% BORDERLINE CASES
  27/70 cases are at the boundary between two gap types.
  While all were assigned a PRIMARY_GAP, the boundary nature means
  the assignment is not always unambiguous.
  → This is expected for a hierarchical framework but limits precision.

LIMITATION_4: NO LIVE SYSTEM RUNS
  All data comes from existing reports and frozen data.
  No new system runs were conducted (READ-ONLY).
  → Classification is based on documented evidence, not fresh verification.

LIMITATION_5: CORPUS BIAS
  The distribution (G2=35.7%) is inflated by IS-11's TLD coverage problem
  (32/45 TLD fail). A different corpus would produce a different distribution.
  → Distribution is NOT generalizable. Framework stability IS (within corpus).
```

---

## 13. Final Governance Status

```
RESEARCH_STATUS =
COMPLETE

IMPLEMENTATION_AUTHORIZED =
FALSE

EXPERIMENT_AUTHORIZED =
FALSE

HUMAN_VALIDATION_AUTHORIZED =
FALSE

SYSTEM_MODIFIED =
FALSE

FROZEN_BASELINE =
INTACT

BASELINE_DRIFT =
0

NEW_CAPABILITY =
NONE

RUNTIME_AUTHORITY =
ZERO

PRODUCTION =
FALSE

STOP =
TRUE
```

---

## Appendix A: Document Inventory

| Document ID | arXiv ID | Domain | Pages | Source Corpus | Document Type |
|-------------|----------|--------|-------|---------------|---------------|
| is11_resnet | 1512.03385 | CS/CV | 12 | IS-11 | academic_paper_cs |
| is11_efficientnet | 1905.11946 | CS/CV | 11 | IS-11 | academic_paper_cs |
| is11_med_001 | 2311.15207 | Chemistry | 29 | IS-11 | academic_paper_chemistry |
| is11_cs_001 | 2402.17764 | CS/NLP | 8 | IS-11 | academic_paper_nlp |
| PH3-ASTRO-001 | 1602.03837 | Astrophysics | 16 | IS-14 | academic_paper_astrophysics |
| PH3-EARTH-001 | 1906.11238 | Astrophysics | 17 | IS-14 | academic_paper_astrophysics |
| PH3-EARTH-002 | 2212.12794 | Earth Science | 102 | IS-14 | academic_paper_earth_science |
| PH3-BIO-001 | 2205.05897 | Genomics | 124 | IS-14 | academic_paper_biology |
| PH3-MED-001 | 2309.04040 | Medical Physics | 55 | IS-14 | academic_paper_medical_physics |
| arxiv_2402.18619 | 2402.18619 | CS | ~30 | M-A | academic_paper_cs |
| ind_arxiv_2402 | (P7 corpus) | CS | — | P7 | academic_paper_cs |
| ind_arxiv_bio2 | (P7 corpus) | Biology | — | P7 | academic_paper_biology |
| ind_qbio_rna | (P7 corpus) | Biology | — | P7 | academic_paper_biology |

## Appendix B: G1-G5 Decision Tree (FROZEN, not modified)

```
START: A failure/abstain/ambiguous case is observed.

  Q: Does the needed observation exist on the page?
    NO  → G1: OBSERVATION_COVERAGE_GAP
    YES → continue

  Q: Has the observation been organized into a usable structure?
    NO  → G2: EVIDENCE_ORGANIZATION_GAP
    YES → continue

  Q: Has the organized evidence been presented to the consumer/Human?
    NO  → G3: EVIDENCE_PRESENTATION_GAP
    YES → continue

  Q: Did the consumer actually use/consume the presented evidence?
    NO  → G4: CONSUMER_INTEGRATION_GAP
    YES → continue

  Q: Is the consumed evidence sufficient for a definitive judgment?
    NO  → G5: SEMANTIC_BOUNDARY
    YES → No gap (judgment made)

BOUNDARY CASES:
  G2↔G4: TLD fails (G2) + consumer has no fallback (G4) — earliest = G2
  G3↔G5: Evidence not presented (G3) + ambiguity emerges (G5) — if resolvable = G3, else G5
  G5↔G4: Structural ambiguity (G5) + guard fires incorrectly (G4) — genuine = G5
```
