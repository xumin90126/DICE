# P7.1 Validation Report — StructureHypothesis Implementation

> Structure candidates from P1-P6 facts. No semantic final classification.

## Completion Checklist

- [x] StructureHypothesis schema (deterministic id, hypothesis_type, span_ids, region_ids, geometry, confidence, status=PROPOSED)
- [x] StructuralRelation schema (relation_type, source_id, target_id, supporting_fact_refs)
- [x] Supporting facts reference (not copy) P1-P6 observations
- [x] Full decision_trace per hypothesis (input, signals, decision, confidence)
- [x] Confidence = min(upstream, structural); no silent erase
- [x] Deterministic reproducibility
- [x] Semantic leakage scan = 0
- [x] Negative case failure count = 0
- [x] P1-P6 regression pass

## Metrics

- **total_hypotheses**: `175`
- **total_relations**: `367`
- **hypothesis_type_distribution**: `{'HEADING_CANDIDATE': 67, 'PARAGRAPH_GROUP_CANDIDATE': 28, 'SECTION_CANDIDATE': 67, 'LIST_CANDIDATE': 8, 'HEADER_CANDIDATE': 2, 'FOOTER_CANDIDATE': 2, 'MULTI_COLUMN_CONTINUATION_CANDIDATE': 1}`
- **relation_type_distribution**: `{'SHARES_REGION': 28, 'ADJACENT_TO': 172, 'PRECEDES': 67, 'VERTICAL_SEPARATION': 25, 'LEFT_ALIGNED_WITH': 13, 'REPEATS_ACROSS_PAGES': 8, 'CONTINUES_FROM': 1, 'STYLE_CONTRAST': 53}`
- **source_span_coverage**: `0.988`
- **source_region_coverage**: `0.931`
- **orphan_hypothesis_count**: `0`
- **duplicate_hypothesis_count**: `0`
- **provenance_completeness**: `1.0`
- **decision_trace_completeness**: `1.0`
- **confidence_distribution**: `{'LOW': 135, 'HIGH': 10, 'MEDIUM': 30}`
- **ambiguous_count**: `0`
- **unknown_count**: `0`
- **blocked_type_leaks**: `[]`
- **semantic_leakage_count**: `0`
- **semantic_leakage_details**: `[]`
- **negative_case_failure_count**: `0`
- **negative_case_failures**: `[]`
- **deterministic_reproducibility**: `True`
- **deterministic_rerun_details**: `[{'case': 'clear_heading', 'ok': True}, {'case': 'ambiguous_heading', 'ok': True}, {'case': 'paragraph_grouping', 'ok': True}, {'case': 'section_boundary', 'ok': True}, {'case': 'list_candidate', 'ok': True}]`
- **p1_p6_regression**: `True`
- **regression_details**: `{'p1_p6_code_unchanged': True, 'changed_files': [], 'frozen_730_md5': 'a10b368e', 'frozen_730_ok': True}`

## Synthetic Cases

| Case | Spans | Hypotheses | Relations | Types |
|---|---|---|---|---|
| clear_heading | 4 | 4 | 5 | {'HEADING_CANDIDATE': 1, 'PARAGRAPH_GROUP_CANDIDATE': 2, 'SECTION_CANDIDATE': 1} |
| ambiguous_heading | 4 | 1 | 4 | {'PARAGRAPH_GROUP_CANDIDATE': 1} |
| paragraph_grouping | 4 | 1 | 4 | {'PARAGRAPH_GROUP_CANDIDATE': 1} |
| section_boundary | 5 | 7 | 8 | {'HEADING_CANDIDATE': 2, 'PARAGRAPH_GROUP_CANDIDATE': 3, 'SECTION_CANDIDATE': 2} |
| list_candidate | 4 | 4 | 7 | {'HEADING_CANDIDATE': 1, 'PARAGRAPH_GROUP_CANDIDATE': 1, 'LIST_CANDIDATE': 1, 'SECTION_CANDIDATE': 1} |
| repeated_header | 4 | 8 | 10 | {'HEADING_CANDIDATE': 2, 'PARAGRAPH_GROUP_CANDIDATE': 2, 'SECTION_CANDIDATE': 2, 'HEADER_CANDIDATE': 2} |
| repeated_footer | 4 | 4 | 6 | {'PARAGRAPH_GROUP_CANDIDATE': 2, 'FOOTER_CANDIDATE': 2} |
| multicolumn_continuation | 6 | 3 | 7 | {'PARAGRAPH_GROUP_CANDIDATE': 2, 'MULTI_COLUMN_CONTINUATION_CANDIDATE': 1} |
| conflicting_style_geometry | 4 | 1 | 4 | {'PARAGRAPH_GROUP_CANDIDATE': 1} |
| low_confidence_upstream | 3 | 1 | 3 | {'PARAGRAPH_GROUP_CANDIDATE': 1} |
| single_page_top_no_header | 2 | 3 | 3 | {'HEADING_CANDIDATE': 1, 'PARAGRAPH_GROUP_CANDIDATE': 1, 'SECTION_CANDIDATE': 1} |

## Real Corpus

| Case | Spans | Hypotheses | Relations | Types |
|---|---|---|---|---|
| rm501_p2 | 44 | 49 | 86 | {'HEADING_CANDIDATE': 21, 'PARAGRAPH_GROUP_CANDIDATE': 4, 'LIST_CANDIDATE': 3, 'SECTION_CANDIDATE': 21} |
| dc201_p2 | 15 | 9 | 22 | {'HEADING_CANDIDATE': 3, 'PARAGRAPH_GROUP_CANDIDATE': 2, 'LIST_CANDIDATE': 1, 'SECTION_CANDIDATE': 3} |
| arxiv_single_p1 | 21 | 8 | 24 | {'HEADING_CANDIDATE': 3, 'PARAGRAPH_GROUP_CANDIDATE': 2, 'SECTION_CANDIDATE': 3} |
| arxiv_toc_p2 | 90 | 72 | 174 | {'HEADING_CANDIDATE': 33, 'PARAGRAPH_GROUP_CANDIDATE': 3, 'LIST_CANDIDATE': 3, 'SECTION_CANDIDATE': 33} |

## Semantic Leakage Scan

- ✅ No banned shortcuts found in engine source.

## Negative Cases

- ✅ `conflicting_style_geometry`: bold-only span produced 0 headings.
- ✅ `single_page_top_no_header`: single-page top region produced 0 headers.
- ✅ No TABLE/IMAGE/FORMULA/FLOWCHART types produced (blocked).

## Regression

- P1-P6 code unchanged: True
- Frozen 730 md5_8: a10b368e (expected a10b368e)
- all_pass: True

## Boundary Review

1. **P7.1 outputs ONLY StructureHypothesis (PROPOSED)**: ✅
2. **No Observation → Final Structure shortcut**: ✅
3. **No Single Signal → Structure shortcut**: ✅ (bold alone, top region alone both fail to produce candidates)
4. **P1-P6 unmodified**: ✅
5. **P7.1 does NOT write Evidence**: ✅
6. **No semantic leakage**: ✅
7. **Every hypothesis has provenance + decision_trace + supporting_facts + supporting_relations + confidence**: ✅
8. **P7.1 → Human Validation → Validated Structure boundary preserved**: ✅
9. **P7.2 / P7.3 still BLOCKED**: ✅

**P7.1 complete. STOP.**
