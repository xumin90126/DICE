# M-A Human Review Interface Implementation Report

> **模式: INTERFACE IMPLEMENTATION / FROZEN INTACT / STOP**
> 日期: 2026-09-17
> 前置: `tmp/m_a_pre_experiment_gate_design.md`（M-A_EXPERIMENT_READY=CONDITIONAL）
> 本文件: M-A Human Validation Pilot Interface 建设报告。

---

## 1. IMPLEMENTATION_STATUS

```
M-A_HUMAN_REVIEW_INTERFACE = READY
```

### Deliverables

```
tmp/m_a_human_review_pilot/
├── index.html                    # Main interface (self-contained)
├── assets/
│   ├── style.css                 # Neutral-color stylesheet
│   └── app.js                    # Application logic (session, zoom, overlays)
├── pages/                        # 41 rendered PDF page images (150 DPI PNG)
├── data/
│   ├── candidates.json           # Human-facing case data (79 cases, no internal metadata)
│   ├── candidates_internal.json  # Internal metadata (audit only)
│   └── audit_results.json        # UI + Cognitive Load audit results
├── generate_data.py              # Data generation script
└── README.md                     # Usage guide
```

### Case Data Summary

```
Total cases: 79
  Candidates (FIG-prefix + near extent): 63 (deduplicated)
  Type A negatives (FIG-prefix, NOT near): 8 (sampled from 154)
  Type B negatives (near, NO FIG-prefix): 8 (sampled from 6330)

Documents: 5 (med_001, resnet, efficientnet, cs_001, arxiv_2402)
Page images: 41 unique (rendered at 150 DPI)
Render resolution: 1241-1275 × 1650-1754 px
```

---

## 2. UI_AUDIT

```
20-point checklist (§三十二):

A. Target text visible:              PASS (all 79 cases have text_bbox)
B. Target drawing visible:           PASS (71 with extent, 8 Type A by design)
C. Full page visible:                PASS (41 unique page images, all valid PNG)
D. Focused view:                     PASS (Focus View tab + scrollToFocus)
E. Bbox correct:                     PASS (all 79 cases within image bounds)
F. No answer leakage:                PASS (no confidence/score/recommend in JSON)
G. No semantic label leakage:        PASS (no caption/figure/chart in metadata)
H. No machine confidence:            PASS (no confidence field in UI or data)
I. No recommendation:                PASS (no recommended_answer field)
J. No automatic GT:                  PASS (app.js records judgment only, no GT)
K. No P1 modification:               PASS (P1 sha=74d23ec784d65782, unchanged)
L. No frozen baseline drift:         PASS (drift=0/4)
M. Deduplicated candidate frame:     PASS (63 candidates, not 126)
N. Multi-drawing handling:           PASS (each case = single text-drawing pair)
O. Human data append-only:           PASS (sessionLog.push, no overwrite)
P. Cognitive-load design audit:      PASS (see §3)
Q. Zoom support:                     PASS (zoom in/out/reset/fit + keyboard)
R. YES/NO/UNCERTAIN:                 PASS (3 equal-weight buttons)
S. Text context:                     PASS (adjacent text shown when available)
T. No semantic visual bias:          PASS (blue/amber/gray, no green=YES)

SUMMARY: 19 PASS, 0 FAIL, 19 total
```

---

## 3. COGNITIVE_LOAD_AUDIT

```
10-point checklist (§三十三):

1. Human needs to find target?           NO  (highlighted with dashed/solid boxes)
2. Human needs to understand bbox?        NO  (visual overlay, no raw coordinates)
3. Human needs to understand distance?    NO  (descriptive: "text is Xpt below")
4. Human needs to understand primitive?   NO  (not in UI)
5. Human needs to understand FIG-prefix?  NO  (text shown as-is, no detection label)
6. Human needs to read entire page?       NO  (Focus View auto-scrolls + Full Page)
7. Human can directly see Text+Drawing?   YES (highlighted on real page image)
8. Human can complete Yes/No/Uncertain?   YES (3 equal buttons + keyboard shortcuts)
9. UI has answer-suggesting elements?     NO  (neutral colors, equal weight)
10. UI requires extra explanation?        NO  (no reason field, no annotation)

SUMMARY:
  1-6 = NO: 6/6 ✓
  7-8 = YES: 2/2 ✓
  9-10 = NO: 2/2 ✓
  → DESIGN AUDIT: PASS

NOTE: Real cognitive burden requires Human Pilot data to confirm.
This is a design audit, not a validated measurement.
```

---

## 4. EVIDENCE_LEAKAGE_AUDIT

```
Anti-leakage checks:

1. Answer leakage (machine answer shown to Human):
   STATUS: 0 detected
   - No 'confidence' field in human-facing JSON
   - No 'score' field
   - No 'recommended_answer' field
   - No 'machine_decision' field
   - App.js does not render any of these fields

2. Semantic label leakage (caption/figure/chart shown to Human):
   STATUS: 0 detected
   - 'pattern_type' field (caption_like, reference_like, etc.) stripped from
     human-facing candidates.json
   - Internal metadata saved separately in candidates_internal.json
   - App.js does not access pattern_type, negative_type, extent_primitive_count,
     extent_area, or x_overlap fields
   - Only text_content, extent existence, spatial distance, and context are shown

3. Machine-answer leakage (algorithm output visible):
   STATUS: 0 detected
   - No algorithm output in UI
   - No candidate score
   - No probability
   - No classification result

4. Context leakage (context contains answer hints):
   STATUS: 0 detected
   - Context text is raw same_y-band text from P1 (actual document text)
   - No system-added annotations or hints
   - Context is "what Human would see if reading the page"

5. Internal metadata separation:
   Human-facing JSON (candidates.json) contains ONLY:
     - case_id, document_id, page_reference, review_order
     - text_content, text_bbox, extent_bbox
     - spatial_distance, vertical_ordering
     - context_text
     - page_image, page_image_width, page_image_height, page_scale

   Internal JSON (candidates_internal.json) contains ADDITIONAL:
     - pattern_type (caption_like, reference_like, etc.)
     - negative_type (type_a, type_b)
     - extent_primitive_count, extent_area
     - x_overlap
     (NOT served to UI, NOT in app.js)
```

---

## 5. BOUNDING_BOX_AUDIT

```
All 79 cases verified:

  Text bbox:
    - All text_bbox values are non-null
    - All text_bbox coordinates convert to pixel coordinates within image bounds
    - Text bbox uses P1 coarse-level atom bbox (wider, contains full pattern)

  Drawing extent bbox:
    - 71/79 cases have extent_bbox (from DRAWING_EXTENT_FACT)
    - 8/79 cases have extent_bbox=null (Type A negatives — by design, no drawing nearby)
    - All extent_bbox coordinates convert to pixel coordinates within image bounds

  Coordinate conversion:
    - PDF points → pixels: multiply by scale (150/72 = 2.083)
    - SVG overlay uses same coordinate space as page image
    - No manual bbox adjustment (raw P1/DRAWING_EXTENT_FACT bboxes used)

  Visual rendering:
    - Target Text: dashed blue rectangle (#4a90d9), 2px stroke
    - Target Drawing: solid amber rectangle (#d99f4a), 2px stroke, 4% fill
    - Labels: "Text" (blue) and "Drawing Region" (amber) above each box
    - Neither color implies YES or NO (neutral, non-semantic)
```

---

## 6. FROZEN_BASELINE_STATUS

```
FROZEN_BASELINE = INTACT (drift=0/4)

  P1 (atomic_text.py):       sha=74d23ec784d65782  (UNCHANGED)
  TLD (table_line_detector): sha=022f5c21e872ad9e  (UNCHANGED)
  GT (is11_semantic_gt):     sha=7349963d0d23b5ef  (UNCHANGED)
  layout_analyzer:           sha=8f69f0d206b3e565  (UNCHANGED)

  AO implementation (UNCHANGED):
    drawing_geometry.py:     sha=f25a5ff41afa1bec
    drawing_extent.py:       sha=cba9e583517f8967

  No code files modified.
  No frozen artifacts modified.
  Only new files created (UI + data + page images).
```

---

## 7. P1_MODIFICATION_STATUS

```
P1 modified: NO

  P1 was READ-ONLY throughout this task.
  extract_page_observations() called to read text atoms.
  No writes to P1 source or any perception layer.
  P1 sha verified: 74d23ec784d65782 (unchanged).
```

---

## 8. M-A_ALGORITHM_MODIFICATION_STATUS

```
M-A algorithm modified: NO

  No M-A algorithm exists (not implemented, not authorized).
  This task only built a review UI — no detector, no classifier,
  no association logic, no threshold tuning.
  DRAWING_EXTENT_FACT and DRAWING_GEOMETRY_FACT were READ-ONLY.
```

---

## 9. HUMAN_VALIDATION_EXECUTION_STATUS

```
Human Validation executed: NO

  The interface is READY but not yet used for actual Human judgment.
  No Human has reviewed any case.
  No session data contains real judgments.
  localStorage is empty (no judgments recorded).

  Human Validation requires explicit user authorization:
  "开始 M-A Human Validation Pilot"
```

---

## 10. Interface Design Summary

### Core Principle

```
Human should validate, not reconstruct.
Compress evidence, not meaning.
```

### What Human Sees

```
1. Real PDF page image (150 DPI, full page)
2. Target Text highlighted (dashed blue box)
3. Target Drawing highlighted (solid amber box)
4. Focus View (auto-scrolls to text + drawing region)
5. Evidence Panel:
   - Target Text content
   - Drawing region (marked on page)
   - Spatial relationship (descriptive: "Xpt below")
   - Adjacent text context (when available)
6. Question: "Is this text associated with the highlighted drawing region?"
7. Three buttons: YES / NO / UNCERTAIN (equal weight)
```

### What Human Does NOT See

```
❌ Machine answer / recommendation
❌ Semantic labels (caption, figure, chart)
❌ Confidence / score / probability
❌ Algorithm state / candidate generation logic
❌ Distance threshold / x-overlap / primitive count
❌ FIG-prefix detection result
❌ Pattern type classification
❌ Negative type classification
```

### Session Data Structure

```
Each judgment record (append-only):
{
  type: "judgment",
  case_id: "is11_med_001_p20_85_340",
  document_id: "is11_med_001",
  page_reference: 20,
  human_judgment: "yes" | "no" | "uncertain",
  timestamp: "2026-09-17T...",
  review_order: 1,
  session_id: "sess_...",
  revision_of: null | "previous_timestamp"
}

Skip records:
{
  type: "skip",
  case_id: "...",
  timestamp: "...",
  ...
}

NOT included:
  ❌ ground_truth (no automatic GT)
  ❌ human_score
  ❌ machine_agreement_score
  ❌ recommended_answer
```

---

## 11. Final Reporting Format

```
M-A HUMAN REVIEW INTERFACE IMPLEMENTATION

STATUS:
READY

Real PDF rendering:
PASS

Target Text highlighting:
PASS

Target Drawing highlighting:
PASS

Focused View:
PASS

Human Task:
YES / NO / UNCERTAIN

Answer leakage:
0 / detected

Semantic leakage:
0 / detected

Machine-answer leakage:
0 / detected

Cognitive-load design audit:
PASS

P1 modified:
NO

Frozen baseline drift:
0

M-A algorithm modified:
NO

Human Validation executed:
NO

Ground Truth generated:
NO

M-A Experiment executed:
NO

STOP:
TRUE
```

---

## 12. Distinction Clarification

```
INTERFACE READY
≠ HUMAN VALIDATION COMPLETE
≠ M-A EXPERIMENT COMPLETE
≠ M-A ACCEPTED

This task achieved:
  M-A_HUMAN_REVIEW_INTERFACE = READY

This task did NOT achieve:
  ❌ M-A proven
  ❌ M-A effective
  ❌ Human review value proven
  ❌ Caption recognition improved
  ❌ Document recognition improved

These require future real Human Experiment with validated evidence.
```

---

## 13. Governance Status

```text
M-A_HUMAN_REVIEW_INTERFACE = READY

Interface: READY (19/19 UI audit PASS, 10/10 cognitive load PASS)
Human Validation: NOT EXECUTED (requires user authorization)
Ground Truth: NOT GENERATED (requires adjudication process)
M-A Experiment: NOT EXECUTED (requires validation + acceptance criteria)

FROZEN_BASELINE = INTACT (drift=0/4)
P1 = UNCHANGED (sha=74d23ec784d65782)
TLD = UNCHANGED (sha=022f5c21e872ad9e)
GT = UNCHANGED (sha=7349963d0d23b5ef)
layout_analyzer = UNCHANGED (sha=8f69f0d206b3e565)
AO = UNCHANGED (drawing_geometry + drawing_extent)

CAPABILITY = UNCHANGED
RUNTIME_AUTHORITY = ZERO
PRODUCTION = FALSE

IMPLEMENTATION = NOT AUTHORIZED (M-A algorithm)
EXPERIMENT = NOT AUTHORIZED
HUMAN_VALIDATION = NOT AUTHORIZED (execution)
HUMAN_FEEDBACK = NOT AUTHORIZED
L3 = NOT AUTHORIZED

New files created:
  tmp/m_a_human_review_pilot/ (index.html, CSS, JS, 41 PNGs, 2 JSONs, README, generate_data.py)
  tmp/m_a_human_review_interface_report.md (this file)

Modified files: 0

STOP = TRUE
```

---

## Research Principle Adherence

- ✅ Real PDF page rendering (41 pages at 150 DPI)
- ✅ Target Text + Target Drawing highlighted on real page images
- ✅ Full Page + Focus View both available
- ✅ Zoom support (in/out/reset/fit + keyboard)
- ✅ YES/NO/UNCERTAIN with equal-weight buttons
- ✅ No answer leakage (0 detected)
- ✅ No semantic label leakage (0 detected, internal metadata separated)
- ✅ No machine recommendation (0 detected)
- ✅ No automatic GT generation
- ✅ No P1 modification (sha verified)
- ✅ No DICE core modification
- ✅ Deduplicated candidate frame preserved (63, not 126)
- ✅ Multi-drawing handling (each case = single pair)
- ✅ Human data append-only (push, not overwrite)
- ✅ Cognitive-load design audit PASS (6/6 NO, 2/2 YES, 2/2 NO)
- ✅ Frozen baseline drift = 0
- ✅ Did NOT execute Human Validation
- ✅ Did NOT generate Ground Truth
- ✅ Did NOT execute M-A Experiment
- ✅ Did NOT claim M-A proven or effective
- ✅ Did NOT claim Human Value improved
- ✅ STOP = TRUE

`STOP = TRUE`.
