# P3 Validation Report — Style Observation Foundation

> Pure style facts from P1 AtomicTextObservation. No semantic classification.
> Read-only w.r.t. all frozen objects AND P1/P2 outputs.

**P3 does not perform semantic classification.**

## Completion Checklist

- [x] StyleObservation schema
- [x] font fact completeness
- [x] font size correctness
- [x] flag decoding consistency
- [x] bold correctness
- [x] italic correctness (if corpus)
- [x] underline correctness (null where unavailable)
- [x] style_signature determinism
- [x] style comparison symmetry
- [x] provenance completeness
- [x] Unicode compatibility
- [x] missing metadata robustness
- [x] P1 regression
- [x] P2 regression
- [x] Frozen 730 integrity
- [x] Annotation integrity
- [x] C1/C2 integrity
- [x] Capability/Runtime integrity

## 1. RM501-P4 p2 Position / Step Style

- **Position**: font='Arial-BoldMT' family='Arial' size=7.3 bold=True italic=False sig='Arial|7.3|1|0|-|0|-'
- **Step**: font='Arial-BoldMT' family='Arial' size=7.0 bold=True italic=False sig='Arial|7.0|1|0|-|0|-'
- **Comparison**: same_font=True same_size=False same_bold=True same_sig=False size_delta=0.3 diff=size_diff
- **Verdict**: PASS — Position and Step styles separately preserved

Position(size=7.3) and Step(size=7.0) styles **separately preserved** — same font, same bold, but different size (delta=0.3pt). Not merged.

## 2. Flag Bit Definitions (empirically verified)

| Bit | Value | Meaning | Verification |
|---|---|---|---|
| 0 | 1 | superscript | CMR8/CMR7 (TeX small-sized) |
| 1 | 2 | italic | Arial-ItalicMT(2), CMMI10(6) |
| 2 | 4 | serifed | Times-Roman(4), CMR10(4) |
| 3 | 8 | monospaced | SFTT1095(12) |
| 4 | 16 | bold | Arial-BoldMT(16), PalatinoLinotype-Bold(20) |
| - | - | underline | null — not encoded in PyMuPDF 1.26.5 span flags |
| - | - | subscript | null — not reliably encoded |

**bold/italic authoritative source = flags bits, NOT font-name guessing.**
Font-name cross-validation recorded in provenance (non-authoritative).

## 3. Test Set (15 items)

| Case | PDF | Page | Total | Bold | Italic | Sup | Distinct sigs |
|---|---|---|---|---|---|---|---|
| rm501_p2 | RM501-P4-英文（单页）V26.1.pdf | 2 | 168 | 34 | 0 | 0 | 6 |
| dc201_p5 | DC201-C1-英文（单页）V26.1.pdf | 5 | 157 | 31 | 0 | 0 | 7 |
| normal_body | C216-英文（单页）V26.1.pdf | 3 | 51 | 10 | 1 | 0 | 8 |
| different_sizes | RM501-P4-英文（单页）V26.1.pdf | 1 | 46 | 15 | 0 | 0 | 6 |
| bold_text | RM501-P4-英文（单页）V26.1.pdf | 2 | 168 | 34 | 0 | 0 | 6 |
| italic_text | arxiv_bio.pdf | 1 | 131 | 11 | 77 | 47 | 27 |
| different_fonts | arxiv_bio.pdf | 3 | 394 | 3 | 197 | 92 | 27 |
| chinese | C216-英文（单页）V26.1.pdf | 1 | 5 | 5 | 0 | 0 | 3 |
| greek_mu | RM501-P4-英文（单页）V26.1.pdf | 1 | 46 | 15 | 0 | 0 | 6 |
| special_arrow | C216-英文（单页）V26.1.pdf | 3 | 51 | 10 | 1 | 0 | 8 |
| table_text | DC201-C1-英文（单页）V26.1.pdf | 5 | 157 | 31 | 0 | 0 | 7 |
| same_style_multi | C216-英文（单页）V26.1.pdf | 3 | 51 | 10 | 1 | 0 | 8 |
| superscript | arxiv_bio.pdf | 5 | 397 | 11 | 197 | 99 | 19 |
| unknown_flags | arxiv_bio.pdf | 3 | 394 | 3 | 197 | 92 | 27 |
| missing_metadata | C216-英文（单页）V26.1.pdf | 1 | 5 | 5 | 0 | 0 | 3 |

## 4. Metrics

| # | Metric | Value |
|---|---|---|
| 1_total_observations | 168 |
| 2_style_completeness | 1.0 |
| 3_font_completeness | 1.0 |
| 4_font_size_completeness | 1.0 |
| 5_bold_completeness | 1.0 |
| 6_provenance_rate | 1.0 |
| 7_style_signature_determinism | True |
| 8_style_comparison_consistency | True |
| 9_unicode_verification | True |
| 10_missing_metadata_handling | True |
| 11_rm501_position_step.verdict | PASS — Position and Step styles separately preserved |
| 11_rm501_position_step.position_sig | Arial|7.3|1|0|-|0|- |
| 11_rm501_position_step.step_sig | Arial|7.0|1|0|-|0|- |
| 11_rm501_position_step.same_signature | False |
| 11_rm501_position_step.size_delta | 0.3 |

## 5. Style Signature Format

`family|size|bold|italic|underline|superscript|subscript` (null = `-`)

- Deterministic: same style facts → same signature (verified)
- No text content, no bbox, no semantics, no CandidateSpan ID
- Example: `Arial|7.3|1|0|-|0|-` (Arial bold 7.3pt)

## 6. Threshold Configuration

| Threshold | Value |
|---|---|
| font_size_equality_tolerance | 0.15 |
| font_size_normalization_decimals | 1 |
| cross_validate_font_name | True |

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

### P1 code (not modified by P3)
- perception/sandbox/observations/atomic_text.py: sha256=74d23ec784d65782...

### P2 code (not modified by P3)
- perception/sandbox/geometry/geometry_config.py: sha256=7ef3629e5a9b819c...
- perception/sandbox/geometry/geometry_observation.py: sha256=7731377cb8468c91...
- perception/sandbox/geometry/geometry_engine.py: sha256=388e7939d334458e...

## 8. Declaration

**P3 does not perform semantic classification.**
P3 produces only style facts (font/size/flags/bold/italic/superscript/signature/comparison).
No is_heading, is_title, is_body, is_caption, heading_level, region_type, column_id.
bold/italic from flags bits (authoritative), not font-name/size/position heuristics.

## 9. STOP

P3 complete. Not entering P4 Span v2 / Multi-column / Heading / Caption / 
Region / Table / Image / Formula / Flowchart detection.