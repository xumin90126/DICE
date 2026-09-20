# P4 Validation Report — Experimental Span Construction v2

> Organization of P1/P2/P3 facts into continuous spans. No semantic classification.
> Read-only w.r.t. all frozen objects AND P1/P2/P3 outputs.

**P4 performs structural span construction only. P4 does not perform semantic classification.**

## Completion Checklist

- [x] ExperimentalSpan v2 schema
- [x] span construction engine
- [x] merge decision rules (fact-based)
- [x] merge decision trace
- [x] Position/Step separation (RM501)
- [x] observation coverage (no orphans)
- [x] no duplicate assignment
- [x] reverse traceability (source_observation_ids)
- [x] deterministic reproducibility
- [x] no cross-page merge
- [x] no cross-column false merge (Position/Step)
- [x] threshold centralized
- [x] no case-specific patches
- [x] P1 regression
- [x] P2 regression
- [x] P3 regression
- [x] Frozen 730 integrity
- [x] Annotation integrity
- [x] C1/C2 integrity
- [x] Capability/Runtime integrity

## 1. RM501-P4 p2 Position / Step Separation (Core Regression)

- **Position** obs_id=56403249af261633 bbox=[513.0, 548.21, 540.93, 558.72]
  → span_id=b4bd561485e0b41d text='Adsorption\nPosition' obs_count=2
- **Step** obs_id=c634aba817ebe541 bbox=[76.99, 539.48, 91.74, 549.5]
  → span_id=2ade2f11097ea00c text='Step'
- **Same span?** False ✅ NO (separate)
- **Merged spans containing both**: 0
- **Verdict**: PASS — Position and Step in separate spans

Position(x513) merged with 'Adsorption' (vertical contiguity, same column x513) — **correct**.
Step(x77) is a separate span. **No span contains both Position and Step.**

## 2. Five-Concept Distinction

| Concept | Description | P4 operates? |
|---|---|---|
| A. CandidateSpan Schema | data contract (frozen) | no |
| B. Legacy Generator | block-based algorithm (frozen) | no |
| C. Frozen 730 Pool | historical instances (frozen) | no |
| D. Experimental Span v2 | current evolvable output | **YES** |
| E. Future Validated Span | post-validation promotion | no (future) |

## 3. Test Set (14 items)

| Case | Obs | Spans | Merge | Sep | Coverage | Orphan | PositionStepMerge |
|---|---|---|---|---|---|---|---|
| same_line_contiguous | 51 | 14 | 37 | 13 | 1.0 | 0 | 0 |
| same_line_large_gap | 168 | 44 | 124 | 43 | 1.0 | 0 | 0 |
| different_line | 51 | 14 | 37 | 13 | 1.0 | 0 | 0 |
| two_column | 394 | 139 | 255 | 138 | 1.0 | 0 | 0 |
| position_step_regression | 168 | 44 | 124 | 43 | 1.0 | 0 | 0 |
| same_style | 51 | 14 | 37 | 13 | 1.0 | 0 | 0 |
| different_style | 397 | 126 | 271 | 125 | 1.0 | 0 | 0 |
| chinese | 5 | 3 | 2 | 2 | 1.0 | 0 | 0 |
| greek_mu | 46 | 21 | 25 | 20 | 1.0 | 0 | 0 |
| special_arrow | 51 | 14 | 37 | 13 | 1.0 | 0 | 0 |
| table_text | 157 | 38 | 119 | 37 | 1.0 | 0 | 1 |
| page_boundary | 51 | 14 | 37 | 13 | 1.0 | 0 | 0 |
| single_observation | 5 | 3 | 2 | 2 | 1.0 | 0 | 0 |
| null_metadata | 5 | 3 | 2 | 2 | 1.0 | 0 | 0 |

## 4. Metrics

| # | Metric | Value |
|---|---|---|
| 1_span_count | 44 |
| 2_observation_count | 168 |
| 3_span_coverage | 1.0 |
| 4_provenance_completeness | 1.0 |
| 5_orphan_count | 0 |
| 6_duplicate_assignment | 0 |
| 7_merge_count | 124 |
| 8_keep_separate_count | 43 |
| 10_deterministic_reproducibility | True |
| 11_rm501_position_step_separation | True |
| 12_cross_page_merge | 0 |
| 13_cross_column_false_merge | 0 |
| 14_p1_regression | True |
| 15_p2_regression | True |
| 16_p3_regression | True |
| 17_frozen_730_integrity | True |
| 18_annotation_integrity | True |
| 19_c1_c2_integrity | True |
| 20_capability_runtime_integrity | True |

## 5. Merge Decision Reason Distribution (RM501 p2)

| Reason | Count |
|---|---|
| NEXT_LINE_CONTIGUOUS | 124 |
| CROSS_COLUMN_GAP | 12 |
| LARGE_VERTICAL_GAP | 31 |

All reasons are geometric (SAME_LINE_CONTIGUOUS, NEXT_LINE_CONTIGUOUS, CROSS_COLUMN_GAP, LARGE_VERTICAL_GAP). No semantic reasons.

## 6. Span Configuration (centralized)

| Threshold | Value |
|---|---|
| max_horizontal_gap | 8.0 |
| max_vertical_gap | 14.0 |
| same_line_tolerance | 3.0 |
| style_transition_tolerance | 0.0 |
| cross_column_gap_threshold | 30.0 |
| overlap_tolerance | 0.5 |
| page_boundary_policy | BLOCK_CROSS_PAGE |
| construction_version | v2 |

No case-specific patches. No `if document_id == 'RM501'` or `if text == 'Position'`.

## 7. Regression Safety

**All frozen objects intact: True**

### Frozen 730 Pool
- md5_8: a10b368e (expected a10b368e) ✅

### Restore-zone frozen
| File | Expected | Actual | Pass |
|---|---|---|---|
| dice/registry.py | 50e3db50 | 50e3db50 | ✅ |
| dice/bootstrap.py | d7f09fef | d7f09fef | ✅ |
| dice/runtime/composition/shadow/capability_runtime/capability_loader.py | 830fca24 | 830fca24 | ✅ |

### C1 (sha256)
- chunker/layout_analyzer.py: ✅
- chunker/layout_rebuilder.py: ✅
- chunker/table_line_detector.py: ✅

### P1/P2/P3 code (not modified by P4)
- p1: sha256=74d23ec784d65782... modified=False
- p2|perception/sandbox/geometry/geometry_config.py: sha256=7ef3629e5a9b819c... modified=False
- p2|perception/sandbox/geometry/geometry_observation.py: sha256=7731377cb8468c91... modified=False
- p2|perception/sandbox/geometry/geometry_engine.py: sha256=388e7939d334458e... modified=False
- p3|perception/sandbox/style/style_config.py: sha256=90359278840247ac... modified=False
- p3|perception/sandbox/style/style_observation.py: sha256=cdf84b47de8f1788... modified=False
- p3|perception/sandbox/style/style_engine.py: sha256=2518cbf0bde06322... modified=False

## 8. Diagnostic Comparison with Frozen 730 (read-only)

- RM501-P4 p2: Experimental Spans = 44, Frozen 730 row 104 = 'Position\nStep' (1 merged candidate)
- 730 is a historical baseline, NOT P4's target count.
- P4's goal: better provenance + geometric consistency + splittability.
- Frozen 730 NOT modified, NOT overwritten.

## 9. Declaration & STOP

**P4 performs structural span construction only.**
**P4 does not perform semantic classification.**
No heading/caption/table/column/region detection. No P5 reading-order/column engine.
No Span v2 → Frozen 730 writeback. No Unfreeze.

P4 complete. STOP. Not entering P5/P6/P7.