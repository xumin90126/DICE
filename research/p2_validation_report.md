# P2 Validation Report — Geometry Observation Foundation

> Pure geometric facts over P1 AtomicTextObservation. No semantic classification.
> Read-only w.r.t. all frozen objects AND P1 outputs.

## Completion Checklist

- [x] GeometryObservation schema
- [x] bbox derived fields (width/height/center)
- [x] pairwise relation
- [x] distance
- [x] overlap
- [x] alignment
- [x] band facts
- [x] page-relative geometry
- [x] threshold centralized
- [x] provenance complete
- [x] RM501 Position/Step geometry verified
- [x] symmetry consistency
- [x] multi-document test
- [x] P1 regression
- [x] Frozen 730 unchanged
- [x] Annotation unchanged
- [x] C1/C2 unchanged
- [x] Capability/Runtime unchanged

## 1. RM501-P4 p2 Position / Step Geometry

- **Position** bbox=[513.0, 548.21, 540.93, 558.72] center_x=526.96
- **Step** bbox=[76.99, 539.48, 91.74, 549.5] center_x=84.36
- **Position relative to Step**: direction=RIGHT_OF, h_dist=421.26pt, v_dist=0.0pt
- **Step relative to Position**: direction=LEFT_OF
- **Symmetry verified**: True (RIGHT_OF <-> LEFT_OF)
- **Verdict**: PASS — Position(x513) and Step(x77) geometrically distinct, not merged

Position(x≈513) and Step(x≈77) remain **geometrically distinct** — h_dist=421pt, not merged. This proves P1+P2 correctly express their true spatial relationship.

## 2. Pairwise Relation Vocabulary

| Relation | Symmetric? | Inverse |
|---|---|---|
| LEFT_OF | no | RIGHT_OF |
| RIGHT_OF | no | LEFT_OF |
| ABOVE | no | BELOW |
| BELOW | no | ABOVE |
| OVERLAPPING | yes | OVERLAPPING |
| CONTAINED_BY | no | CONTAINS |
| CONTAINS | no | CONTAINED_BY |
| SAME_POSITION | yes | SAME_POSITION |

## 3. Test Set (11 items)

| Case | PDF | Page | Singles | Pairs | Notes |
|---|---|---|---|---|---|
| same_line_adjacent | C216-英文（单页）V26.1.pdf | 3 | 51 | 500 | target found: 1 |
| different_line | C216-英文（单页）V26.1.pdf | 3 | 51 | 500 |  |
| two_column | arxiv_bio.pdf | 3 | 394 | 500 |  |
| page_top_bottom | RM501-P4-英文（单页）V26.1.pdf | 1 | 46 | 500 |  |
| overlap_bbox | DC201-C1-英文（单页）V26.1.pdf | 5 | 157 | 500 |  |
| containment | DC201-C1-英文（单页）V26.1.pdf | 5 | 157 | 500 |  |
| table_adjacent_text | DC201-C1-英文（单页）V26.1.pdf | 5 | 157 | 500 | target found: 6 |
| chinese | C216-英文（单页）V26.1.pdf | 1 | 5 | 20 |  |
| greek_symbol | RM501-P4-英文（单页）V26.1.pdf | 1 | 46 | 500 | target found: 5 |
| special_symbol | C216-英文（单页）V26.1.pdf | 3 | 51 | 500 | target found: 1 |
| rm501_position_step | RM501-P4-英文（单页）V26.1.pdf | 2 | 168 | 500 | Position->Step: RIGHT_OF h=16.2 |

## 4. Metrics

| Metric | Value |
|---|---|
| 1_bbox_completeness | 1.0 |
| 2_geometry_completeness | 1.0 |
| 3_relation_consistency.total_relations | 2000 |
| 4_pairwise_symmetry_consistency.checked_pairs | 132 |
| 4_pairwise_symmetry_consistency.consistent | 132 |
| 4_pairwise_symmetry_consistency.symmetry_rate | 1.0 |
| 5_distance_correctness.position_step_h_dist | 421.26 |
| 5_distance_correctness.matches_relation_field | True |
| 5_distance_correctness.all_distances_nonneg | True |
| 6_overlap_correctness.iou_in_range | True |
| 6_overlap_correctness.overlap_area_nonneg | True |
| 7_unicode_observation_compatibility | True |
| 8_provenance_completeness | 1.0 |

**RM501 Position/Step**: PASS — Position(x513) and Step(x77) geometrically distinct, not merged

## 5. Threshold Configuration (centralized)

| Threshold | Value | Purpose |
|---|---|---|
| y_band_tolerance | 3.0 | same_y_band membership (y-center diff <= this) |
| x_band_tolerance | 3.0 | same_x_band membership (x-center diff <= this) |
| alignment_tolerance | 2.0 | edge aligned if coord diff <= this |
| overlap_tolerance | 0.5 | overlap below this treated as 0 (numeric noise) |
| horizontal_distance_threshold | 12.0 | reference x-gap fact (NOT a paragraph rule) |
| vertical_distance_threshold | 12.0 | reference y-gap fact (NOT a paragraph rule) |
| iou_tolerance | 0.001 | IoU below this treated as 0 |
| containment_ratio_threshold | 0.95 | B CONTAINED_BY A if >= this fraction of B inside A |

No thresholds hardcoded elsewhere — all in `GeometryConfig`.

## 6. Regression Safety

**All frozen objects intact: True**

### Restore-zone frozen (md5_8)

| File | Expected | Actual | Pass |
|---|---|---|---|
| dice/registry.py | 50e3db50 | 50e3db50 | ✅ |
| dice/bootstrap.py | d7f09fef | d7f09fef | ✅ |
| dice/runtime/composition/shadow/capability_runtime/capability_loader.py | 830fca24 | 830fca24 | ✅ |

### DICE 2.0 C1 (sha256)

- chunker/layout_analyzer.py: ✅
- chunker/layout_rebuilder.py: ✅
- chunker/table_line_detector.py: ✅

### Frozen 730 Pool

- exists: True, md5_8: a10b368e

### P1 code (not modified by P2)

- perception/sandbox/observations/atomic_text.py: sha256=74d23ec784d65782..., modified_by_p2=False

## 7. STOP

P2 complete. Not entering P3 Style. Not implementing Bold/Font-Size/Heading/
Multi-column/Span v2/Table/Image/Formula/Flowchart/Caption.
Geometry facts (x_projection, alignment_group, spatial_cluster) are available for a future Multi-column Layer to interpret as ColumnCandidate.