# P5 Validation Report — Reading Order & Multi-column Geometry Foundation

> Geometric reading-order interpretation of P4 spans. No semantic classification.
> Read-only w.r.t. all frozen objects AND P1/P2/P3/P4 outputs.

**P5 performs geometric reading-order construction. P5 does not perform semantic classification.**

## Completion Checklist

- [x] ReadingOrderObservation schema
- [x] Column geometry (x-projection/density/gaps)
- [x] Reading order engine (column-major)
- [x] Reading order decision trace
- [x] RM501 Position/Step separation
- [x] DC201 reading order
- [x] Cross-column ordering (A1A2A3B1B2B3)
- [x] No cross-page ordering
- [x] No orphan spans
- [x] No duplicate assignment
- [x] Deterministic reproducibility
- [x] Ambiguity handling (LOW/UNKNOWN)
- [x] No hardcoded 2-column assumption
- [x] No semantic header/footer
- [x] P1/P2/P3/P4 regression
- [x] Frozen 730 integrity
- [x] Annotation integrity
- [x] C1/C2 integrity
- [x] Capability/Runtime integrity

## 1. RM501-P4 p2 — Position / Step Reading Order

- **Position** span_id=b4bd561485e0b41d reading_index=27 column=col_0 bbox=[508.05, 539.4, 545.88, 558.72]
- **Step** span_id=2ade2f11097ea00c reading_index=15 column=col_0 bbox=[76.99, 539.48, 91.74, 549.5]
- **Gap in reading order**: 12 spans between them
- **Adjacent?** False ✅ NOT adjacent
- **Same column?** True
- **Verdict**: PASS — Position and Step NOT adjacent in reading order

Position(x508) and Step(x77) are table headers at the same y≈539.5 but in DIFFERENT x positions. They are 12 reading-order positions apart, NOT adjacent — no Position→Step continuity error.

## 2. DC201-p5 Reading Order

- spans=38 columns=1 confidence=HIGH
- coverage=1.0 orphan=0
- Single-column instruction page; reading order top→bottom, left→right within line (▲ special symbol preserved as separate span).

## 3. Column Geometry (bbox vertical projection)

Column detection uses the vertical coverage profile of span BBOXES. A column gap = vertical white stripe (zero bbox coverage) wider than column_gap_threshold. Tiny groups (< min_column_span_count) are margin elements (page numbers), merged into nearest column.

## 4. Test Set

| Case | Type | Spans | Columns | Confidence | Coverage | Orphan | Order |
|---|---|---|---|---|---|---|---|
| single_column_real | real | 14 | 1 | HIGH | 1.0 | 0 | - |
| rm501_p2 | real | 44 | 1 | HIGH | 1.0 | 0 | - |
| dc201_p5 | real | 38 | 1 | HIGH | 1.0 | 0 | - |
| table_text | real | 38 | 1 | HIGH | 1.0 | 0 | - |
| chinese_greek_symbol | real | 44 | 1 | HIGH | 1.0 | 0 | - |
| sparse_page | real | 3 | 1 | HIGH | 1.0 | 0 | - |
| arxiv_mixed | real | 139 | 1 | HIGH | 1.0 | 0 | - |
| arxiv_toc | real | 90 | 2 | HIGH | 1.0 | 0 | - |
| two_column_clean | synth | 6 | 2 | HIGH | 1.0 | 0 | ✅ |
| three_column | synth | 9 | 3 | HIGH | 1.0 | 0 | ✅ |
| uneven_two_column | synth | 6 | 2 | HIGH | 1.0 | 0 | ✅ |
| single_column | synth | 4 | 1 | HIGH | 1.0 | 0 | ✅ |
| top_region_two_column | synth | 5 | 2 | HIGH | 1.0 | 0 | ✅ |
| row_aligned_toc | synth | 8 | 2 | HIGH | 1.0 | 0 | N/A (ambiguous) |
| overlapping_ambiguous | synth | 3 | 1 | LOW | 1.0 | 0 | N/A (ambiguous) |

## 5. Metrics

| # | Metric | Value |
|---|---|---|
| 1_total_pages | 15 |
| 2_total_spans | 451 |
| 3_reading_order_coverage | 1.0 |
| 4_orphan_spans | 0 |
| 5_duplicate_order_assignment | 0 |
| 6_reading_order_index_completeness | 1.0 |
| 7_deterministic_reproducibility | True |
| 8_column_candidate_count | 22 |
| 9_single_column_count | 9 |
| 10_multi_column_count | 6 |
| 11_ambiguous_count | 2 |
| 12_low_confidence_count | 1 |
| 13_cross_column_ordering_violations | 0 |
| 14_cross_page_ordering_violations | 0 |
| 15_rm501_regression | True |
| 16_dc201_regression | True |
| 17_provenance_completeness | 1.0 |
| 18_decision_trace_completeness | 1.0 |

## 6. Reading Order Configuration (centralized)

| Threshold | Value |
|---|---|
| column_gap_threshold | 25.0 |
| column_density_threshold | 2 |
| column_x_bin_size | 5.0 |
| top_region_ratio | 0.2 |
| bottom_region_ratio | 0.2 |
| full_width_ratio | 0.6 |
| column_x_tolerance | 12.0 |
| min_column_span_count | 3 |
| vertical_order_tolerance | 1.0 |
| large_vertical_gap | 30.0 |
| overlap_tolerance | 0.5 |
| confidence_threshold_high | 0.75 |
| confidence_threshold_medium | 0.5 |
| ambiguous_column_overlap_ratio | 0.4 |
| row_alignment_threshold | 0.6 |
| overlap_ambiguity_threshold | 0.6 |
| construction_version | v1 |

No document-specific thresholds. No `if document_id == 'RM501'` / `if text == 'Position'` / `if text == 'Step'`.

## 7. Regression Safety

**All frozen objects intact: True**

### Frozen 730 Pool
- md5_8: a10b368e (expected a10b368e) ✅

### Restore-zone frozen (md5_8)
| File | Expected | Actual | Pass |
|---|---|---|---|
| dice/registry.py | 50e3db50 | 50e3db50 | ✅ |
| dice/bootstrap.py | d7f09fef | d7f09fef | ✅ |
| dice/runtime/composition/shadow/capability_runtime/capability_loader.py | 830fca24 | 830fca24 | ✅ |

### C1 (sha256)
- chunker/layout_analyzer.py: ✅
- chunker/layout_rebuilder.py: ✅
- chunker/table_line_detector.py: ✅

### P1/P2/P3/P4 code (not modified by P5)
- p1|perception/sandbox/observations/atomic_text.py: sha256=74d23ec784d65782... modified=False
- p2|perception/sandbox/geometry/geometry_config.py: sha256=7ef3629e5a9b819c... modified=False
- p2|perception/sandbox/geometry/geometry_observation.py: sha256=7731377cb8468c91... modified=False
- p2|perception/sandbox/geometry/geometry_engine.py: sha256=388e7939d334458e... modified=False
- p3|perception/sandbox/style/style_config.py: sha256=90359278840247ac... modified=False
- p3|perception/sandbox/style/style_observation.py: sha256=cdf84b47de8f1788... modified=False
- p3|perception/sandbox/style/style_engine.py: sha256=2518cbf0bde06322... modified=False
- p4|perception/sandbox/span/span_config.py: sha256=55b9a23850398acc... modified=False
- p4|perception/sandbox/span/span_observation.py: sha256=87e8c0bca1b2dcc4... modified=False
- p4|perception/sandbox/span/span_rules.py: sha256=1c8e38300e9de981... modified=False
- p4|perception/sandbox/span/span_engine.py: sha256=41e9636a63d97110... modified=False

## 8. Declaration & STOP

**P5 performs geometric reading-order construction.**
**P5 does not perform semantic classification.**
No heading/caption/table/image/formula/flowchart detection. No P6 region / P7 structure.
P5 does not modify spans (read-only input). No column semantic interpretation.

P5 complete. STOP. Not entering P6/P7.