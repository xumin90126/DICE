# M-A Pre-Experiment Gate Design

> **模式: DESIGN-ONLY / READ-ONLY / NO IMPLEMENTATION / NO EXPERIMENT / NO HUMAN VALIDATION / FROZEN INTACT / STOP**
> 日期: 2026-09-17
> 前置: `tmp/m_a_caption_association_design_research.md`（DESIGN_READY_WITH_CONDITIONS）
> 本文件: 把正式 Human Validation / Experiment 之前的设计条件全部明确化，判断 M-A 是否真正具备进入正式 Experiment 的条件。

---

## 1. Purpose

```
M-A 当前状态 = DESIGN_READY_WITH_CONDITIONS

本轮目标:
  把 G1–G9 九个 Gate 全部明确化，
  判断 M-A_EXPERIMENT_READY = YES / CONDITIONAL / NO

本轮不执行:
  ❌ Human Validation
  ❌ Experiment
  ❌ Implementation
  ❌ Threshold tuning
```

### 本轮发现的修正

```
在 G2 分析中发现，上一阶段报告的候选数量存在计数偏差:

  ORIGINAL (with P1 coarse+fine duplicates):
    126 candidates, 280 Type A, 9257 Type B

  DEDUPLICATED (coarse-level, position-unique):
    63 candidates, 154 Type A, 6330 Type B

  原因: P1 同时产出 coarse 和 fine 两级 atom，同一位置的文本
        被计为两个 atom（如 "FIG. 9:" coarse + "FIG." fine）。
        上一阶段的分析未做去重，导致计数翻倍。

  这一修正不改变任何研究结论的方向，但使候选集更精确。
  以下所有 Gate 设计均使用 DEDUPLICATED 数据。
```

---

## 2. Current M-A State

```
From m_a_caption_association_design_research.md:

  RESEARCH_OBJECT_DEFINED       = PASS
  EVIDENCE_BOUNDARY_DEFINED     = PASS
  HUMAN_VALIDATION_UNIT_DEFINED = PASS
  POSITIVE_SET_DESIGNABLE       = CONDITIONAL
  NEGATIVE_SET_DESIGNABLE       = PASS
  BOUNDARY_SET_DESIGNABLE       = CONDITIONAL
  EVALUATION_PROTOCOL_DESIGNABLE= CONDITIONAL
  IMPLEMENTATION_READY          = FAIL

  M-A_STATUS = DESIGN_READY_WITH_CONDITIONS

  H-MA HYPOTHESIS:
    Text-Drawing Spatial Association reduces candidate search space;
    final Caption Association remains semantic interpretation requiring Human validation.

Corrected data (deduplicated):
  63 caption candidates (was 126)
  154 Type A negatives (was 280)
  6330 Type B negatives (was 9257)
  5 PDFs, all with pattern
  3 core diagnostic cases (AMB-414, AMB-422, EXT-P28)
  7 multi-drawing boundary pages
```

---

## 3. G1 Spatial Rule Design

### 3.1 Distance

```
RULE_NAME: DISTANCE
EVIDENCE_SOURCE: text.bbox ↔ extent.bbox (consumer-computed vertical gap)
SEMANTIC_STATUS: Observation (pure geometric arithmetic, no semantic)
ROLE: SUPPORTING

EVIDENCE:
  Deduplicated caption_like candidates (n=41):
    Distance range: 2.5 – 55.2pt
    Distance median: 22.9pt
    83% below extent, 5% above, 12% inside (overlapping y-range)

PRE_REGISTRATION_REQUIREMENT: REQUIRED

  未来 Experiment 开始前必须冻结一个 distance rule。
  但本轮不得选择数值（禁止 threshold tuning）。

  Candidate range (observation-based, NOT pre-registered):
    Lower bound: ~2pt (text adjacent to extent)
    Upper bound: ~60pt (observed maximum for caption_like near extent)
    Median: ~23pt

  VALUE = TO_BE_PRE_REGISTERED
  禁止输出: best threshold / optimal threshold
```

### 3.2 Vertical Ordering

```
RULE_NAME: VERTICAL_ORDERING
EVIDENCE_SOURCE: text.bbox.y vs extent.bbox.y (consumer-computed)
SEMANTIC_STATUS: Observation (pure geometric)
ROLE: SUPPORTING

EVIDENCE:
  83% below, 5% above, 12% inside (overlapping y-range, deduplicated)

ANALYSIS:
  "below" is dominant (83%) but NOT universal (17% above or inside).
  87% ≠ threshold: 87% is an observation frequency, not a rule.
  87% ≠ ground truth: it is not validated by Human judgment.
  Cannot require "must be below" — would exclude 17% of candidates.

  Vertical ordering is DESCRIPTIVE (records position) + SUPPORTING (below is more likely).
  It is NOT NECESSARY (cannot be a hard requirement).

PRE_REGISTRATION_REQUIREMENT: NOT_REQUIRED_AS_RULE
  → Vertical ordering does NOT need to be a pre-registered rule.
  → It is a DESCRIPTIVE field in the Evidence Pack, not a gating criterion.
  → Future experiment may record it as a feature, but must not gate on it.
```

### 3.3 X-overlap

```
RULE_NAME: X_OVERLAP
EVIDENCE_SOURCE: text.bbox.x vs extent.bbox.x (consumer-computed)
SEMANTIC_STATUS: Observation (pure geometric)
ROLE: SUPPORTING

EVIDENCE:
  AMB-414: x_overlap=TRUE (text x=[85,125], extent x=[88,526])
  AMB-422: x_overlap=FALSE (text x=[85,129], extent x=[177,470])
  → Both are diagnostic cases, one overlaps, one does not.
  → x-overlap is NOT a necessary condition for diagnostic value.

CONCEPTUAL DISTINCTION (three concepts, must NOT be conflated):

  x-overlap:      text.x0 < extent.x1 AND text.x1 > extent.x0
                  → Boolean: do their x-ranges share any interval?

  x-alignment:    text.x0 ≈ extent.x0 (left edges align)
                  → Continuous: how close are the left edges?
                  → Different concept from overlap

  horizontal proximity: |text.x0 - extent.x0| or horizontal gap
                  → Distance metric: how far apart horizontally?
                  → Different concept from both above

  These three are NOT the same:
    - Text can x-overlap without x-aligning (text is narrower, inside extent x-range)
    - Text can x-align without x-overlapping (left edges match but text is above)
    - Text can be horizontally close without overlapping or aligning

PRE_REGISTRATION_REQUIREMENT: REQUIRED (as boolean x-overlap field)
  → x-overlap (boolean) should be recorded in Evidence Pack.
  → x-alignment and horizontal proximity are UNKNOWN — not enough data.
  → Must NOT use x-overlap as a gating criterion (AMB-422 disproves necessity).
  → VALUE = TO_BE_PRE_REGISTERED (whether to use as feature, not threshold)
```

### 3.4 Horizontal Alignment

```
RULE_NAME: HORIZONTAL_ALIGNMENT
EVIDENCE_SOURCE: text.bbox.x0 vs extent.bbox.x0 (consumer-computed)
SEMANTIC_STATUS: Observation (pure geometric)
ROLE: UNKNOWN

EVIDENCE:
  Some captions left-align with extent (med_001: text x0=85, extent x0=88)
  Some captions do not (resnet: text x0=308, extent x0 varies)
  Not enough systematic analysis to determine discriminative power.

PRE_REGISTRATION_REQUIREMENT: UNKNOWN
  → Cannot determine if this should be a rule.
  → If future experiment uses it, must pre-register BEFORE seeing results.
```

### 3.5 Multiple-Drawing Association

```
RULE_NAME: MULTIPLE_DRAWING_ASSOCIATION
EVIDENCE_SOURCE: count of extents near text (consumer-computed)
SEMANTIC_STATUS: Observation (count of geometric facts)
ROLE: NECESSARY (as a design consideration, not a threshold)

EVIDENCE:
  7 pages with 2+ extents, 4+ with 2+ FIG-prefix texts near different extents
  When text is near 2+ extents → association is AMBIGUOUS

PRE_REGISTRATION_REQUIREMENT: REQUIRED (as protocol rule)
  → Protocol must define: how to handle text near 2+ extents.
  → Rule: nearest-extent-by-distance as DEFAULT, but AMBIGUOUS cases
    (similar distances) → Boundary Set for Human Validation.
  → NO automatic winner selection.
  → This is a PROTOCOL rule, not a threshold.
```

### 3.6 G1 Summary

```
RULE              | ROLE       | PRE_REG_STATUS
DISTANCE          | SUPPORTING | REQUIRED (value TO_BE_PRE_REGISTERED)
VERTICAL_ORDERING | SUPPORTING | NOT_REQUIRED_AS_RULE (descriptive field)
X_OVERLAP         | SUPPORTING | REQUIRED (boolean field, not gating criterion)
H_ALIGNMENT       | UNKNOWN    | UNKNOWN
MULTI_DRAWING     | NECESSARY  | REQUIRED (protocol rule, no threshold)

DISTANCE_THRESHOLD_STATUS = REQUIRED
  → A distance rule must be pre-registered before experiment.
  → But value is TO_BE_PRE_REGISTERED (not selected this round).
  → Candidate range: 2.5–55.2pt (observation, NOT pre-registered value).
```

---

## 4. G2 P1 Atom Splitting Decision

### 4.1 Q1: Is P1 sufficient for FIG-prefix / reference-like / caption-like detection?

```
ANALYSIS (READ-ONLY, no P1 modification):

  P1 produces TWO levels of atoms for the same text:
    Coarse: "FIG. 9:" (single atom, contains full caption pattern)
    Fine:   "FIG." + "9:" (two atoms, fragments)

  At COARSE level:
    ✓ caption_like pattern (FIG.N: / Figure N.) IS detectable as single atom
      → 39 deduplicated caption-pattern atoms confirmed
    ✓ reference-like pattern (Fig. N) ... ) IS partially detectable
      → 1 deduplicated reference-pattern atom: "Fig. 3). When..."
    ✓ sub-figure label (Fig. 14a) IS detectable
      → 4 deduplicated sub-figure atoms confirmed

  At FINE level:
    ✗ "FIG." fragment alone is ambiguous (caption or reference)
    ✗ Cannot distinguish without surrounding atom context

  P2 same_y_band CAN reconstruct multi-atom context:
    ✓ Same_y concatenation of fine atoms reconstructs full caption text
    ✓ Same_y concatenation can detect reference-like wording ("see Fig. 1")
    ✓ This uses EXISTING P2 observation (no P1 modification needed)

CONCLUSION:
  P1 coarse-level atoms ARE sufficient for caption_like detection.
  The "P1 atom splitting limitation" identified in previous research
  was a COUNTING METHODOLOGY issue (counting both coarse and fine),
  NOT a Perception deficiency.

  P1 modification is NOT needed.
  The information IS present at coarse level.
  Reference-like detection is PARTIALLY available (lexical pattern at coarse level).
  Full reference detection CAN use P2 same_y reconstruction (no P1 change).
```

### 4.2 Q2: If insufficient, which failure taxonomy?

```
NOT APPLICABLE — P1 IS sufficient at coarse level.

  But for completeness, if we had treated it as a deficiency:
    It would be NOT A (Perception Missing) — P1 records the text.
    It would be NOT C (Evidence Representation Loss) — P1 has the information.
    It would be D (Evidence Organization Failure) — the issue was in
      how the analysis used the data (counting both levels), not in P1.

  The corrected classification:
    This is NOT a failure at all. P1 is correct.
    The previous research's "limitation" was an analysis methodology issue.
```

### 4.3 Q3: Is P1 modification required?

```
P1_MODIFICATION_REQUIRED = NOT_REQUIRED

  Evidence:
    1. P1 coarse atoms contain caption_like patterns (39 confirmed)
    2. P1 coarse atoms contain reference patterns (1 confirmed)
    3. P1 coarse atoms contain sub-figure labels (4 confirmed)
    4. P2 same_y_band can reconstruct multi-atom context (verified)
    5. No P1 change is needed for M-A to proceed

  The previous G6 condition ("P1 atom splitting limitation, DESIGN_DECISION_REQUIRED")
  is now RESOLVED:
    → It was not a P1 limitation.
    → It was a counting methodology issue (now corrected: 126 → 63).
    → P1 modification = NOT_REQUIRED.
```

### 4.4 G2 Gate Status

```
G2_P1_ATOM_SPLITTING = PASS (was CONDITIONAL)

  Previous: "P1 atom splitting limitation, DESIGN_DECISION_REQUIRED"
  Corrected: P1 is sufficient at coarse level; limitation was methodology, not P1.
  P1_MODIFICATION_REQUIRED = NOT_REQUIRED
  This gate is now CLEAR.
```

---

## 5. G3 Human Validation Design

### 5.1 Human Task Definition

```
HUMAN_TASK = ASSOCIATION_JUDGMENT

  Task: "Is this text associated with this drawing? (Yes / No / Uncertain)"

  NOT:
    ❌ CAPTION_CLASSIFICATION ("Is this a caption?")
    ❌ FIGURE_DETECTION ("Is this a figure?")
    ❌ MERGE_DECISION ("Should these merge?")
    ❌ FEATURE_SPECIFICATION ("What features indicate caption?")
    ❌ ALGORITHM_DESIGN ("How should the detector work?")
    ❌ REASON_EXPLANATION ("Why is this associated?")

  Human does NOT need to:
    ✗ Find the text (candidate is presented)
    ✗ Find the drawing (extent is presented)
    ✗ Reconstruct page structure (evidence is organized)
    ✗ Write reasons (just Yes/No/Uncertain)
    ✗ Specify detector/feature/algorithm

  Human DOES:
    ✓ See text content ("FIG. 9: Left:")
    ✓ See drawing extent (bbox + primitive_count + area)
    ✓ See spatial relationship (distance, x-overlap, below/above)
    ✓ See FIG-prefix lexical evidence (yes/no, pattern type)
    ✓ See adjacent text context (same_y members)
    ✓ Judge: associated / not associated / uncertain
```

### 5.2 Three-Option Judgment

```
  YES = associated (text is about/for this drawing)
  NO  = not associated (text is about something else)
  UNCERTAIN = cannot determine (boundary case → adjudication)

  Why UNCERTAIN (not just Yes/No):
    - Some cases are genuinely ambiguous (reference near drawing)
    - Forcing binary would create false ground truth
    - UNCERTAIN → routes to Boundary Set / Adjudication (G8)
    - Human is not punished for uncertainty
```

### 5.3 G3 Gate Status

```
G3_HUMAN_VALIDATION = PASS (design complete, execution NOT authorized)

  Design: ASSOCIATION_JUDGMENT (Yes/No/Uncertain)
  Evidence Pack: defined (§6)
  Human burden: minimal (one judgment per candidate, ~63 + ~100 negatives + ~15 boundary)
  Execution: NOT AUTHORIZED (requires separate authorization)
```

---

## 6. Human Evidence Pack Design

### 6.1 Information Requirements

```
For each candidate, Evidence Pack presents:

  1. Text content (P1)
     STATUS: REQUIRED
     - Full text of candidate atom (coarse level)
     - Example: "FIG. 9: Left: BIC values for models with different kernels."
     - If text is split: same_y concatenated full text

  2. Drawing extent (DRAWING_EXTENT_FACT)
     STATUS: REQUIRED
     - Extent bbox [x0, y0, x1, y1]
     - Primitive count (density signal)
     - Area (size signal)
     - NOT: PNG rendering (forbidden in Observation)
     - NOT: Figure identity (semantic, forbidden)

  3. Text bbox (P1)
     STATUS: REQUIRED
     - [x0, y0, x1, y1] of the candidate text

  4. Spatial relationship (consumer-computed)
     STATUS: REQUIRED
     - Distance: "34.5pt below extent"
     - X-overlap: "yes" / "no"
     - Vertical ordering: "below" / "above" / "inside"

  5. FIG-prefix lexical evidence (P1)
     STATUS: REQUIRED
     - FIG-prefix detected: yes/no
     - Pattern type: caption_like / reference_like / subfigure / ambiguous

  6. Adjacent text context (P2)
     STATUS: SUPPORTING
     - Same_y_band members (e.g., "FIG. 9:" + "Left:" + "Right:")
     - h_gap between members
     - Shows whether caption has continuation text

  7. Page context (P6 + multi-drawing)
     STATUS: OPTIONAL
     - Number of extents on page (for multi-drawing awareness)
     - Other FIG-prefix texts on page (for disambiguation)
     - P6 region type

  NOT included (anti-bias):
    ✗ caption = true (would tell Human the answer)
    ✗ association = true (would tell Human the answer)
    ✗ recommended answer (would bias judgment)
    ✗ confidence / score (forbidden)
    ✗ algorithm output (forbidden)
    ✗ Drawing PNG/image (visual recovery, forbidden in Observation)
```

### 6.2 Anti-Bias Verification

```
  Evidence Pack must NOT contain:
    ❌ Any semantic label (is_caption, is_figure, is_associated)
    ❌ Any score/confidence/recommendation
    ❌ Any algorithm output
    ❌ Any "expected answer" hint

  Evidence Pack MUST contain:
    ✓ Observable facts only (text, bbox, distance, overlap, prefix)
    ✓ Structural context (same_y, page extents)
    ✓ Nothing that pre-judges the association

  The Human sees EVIDENCE, not ANSWERS.
  The Human makes the JUDGMENT, not the system.
```

---

## 7. G4 Positive Set Design

### 7.1 Candidate vs Positive vs Negative vs Boundary

```
Definitions:

  CANDIDATE:
    Machine-identified text-drawing pair where:
      text has FIG-prefix + is near drawing extent
    → 63 deduplicated candidates
    → These are NOT positives — they are "worth validating"

  POSITIVE:
    Human-validated "associated" (Yes) from candidate set
    → Count: TO_BE_DETERMINED (requires Human Validation)
    → Estimated: ~39 caption-pattern atoms likely positive (but NOT confirmed)

  NEGATIVE:
    Human-validated "not associated" (No) from candidate set
    → Count: TO_BE_DETERMINED
    → Estimated: ~1 reference-pattern + some ambiguous fragments likely negative

  BOUNDARY:
    Human-validated "uncertain" from candidate set
    → Count: TO_BE_DETERMINED
    → Estimated: ~4 sub-figure labels + some ambiguous fragments

  KEY DISTINCTION:
    63 candidates ≠ 63 positives
    63 candidates → split into positive + negative + boundary BY Human Validation
```

### 7.2 How Human Validation produces Positive

```
Process (design only, not executed):

  1. Present 63 candidates to Human (one at a time, with Evidence Pack)
  2. Human judges: associated / not associated / uncertain
  3. Results:
     - "associated" → POSITIVE SET
     - "not associated" → NEGATIVE SET (from candidate)
     - "uncertain" → BOUNDARY SET

  This means:
    - Some candidates will become positives
    - Some candidates will become negatives (e.g., reference near drawing)
    - Some candidates will become boundary (e.g., sub-figure labels)

  The candidate set is the INPUT to validation, not the output.
```

### 7.3 G4 Gate Status

```
G4_POSITIVE_SET = CONDITIONAL

  Design: complete (candidate → positive via Human Validation)
  Data: 63 candidates available
  BUT: 0 validated (requires Human Validation execution)
  Execution: NOT AUTHORIZED

  CONDITIONAL because: positive set cannot be constructed without Human Validation.
  But the DESIGN is complete — the process is defined.
```

---

## 8. G5 Negative Set Design

### 8.1 Type A: FIG-prefix WITHOUT proximity

```
  Count: 154 deduplicated
  Definition: text has FIG-prefix, but is NOT within 60pt of any drawing extent
  Examples: "Figure 3 shows..." on text-only page, "see Fig. 1" in body text

  Can these serve as natural negatives?

    Evidence-level negative: YES
      → These texts have FIG-prefix but no spatial proximity to drawing
      → At Evidence Organization level, they are NOT caption_candidates
      → The organization rule (FIG-prefix + near extent) correctly excludes them

    Semantic ground truth negative: NOT_ESTABLISHED
      → We KNOW they are not caption_candidates (no proximity)
      → But we DON'T KNOW if they are "not associated with any drawing"
      → Some may reference a drawing on a DIFFERENT page (cross-page reference)
      → Some may reference a drawing that was filtered out (no extent)

  SEMANTIC_NEGATIVE_GROUND_TRUTH = NOT_ESTABLISHED
    → Type A negatives are Evidence-level negatives (organization correctly excludes them)
    → They are NOT automatically Semantic Ground Truth negatives
    → To use as GT negatives, Human Validation must confirm "not associated"
```

### 8.2 Type B: Proximity WITHOUT FIG-prefix

```
  Count: 6330 deduplicated
  Definition: text is within 60pt of drawing extent, but has NO FIG-prefix
  Examples: body text, table cells, equations, page numbers near drawings

  Can these serve as natural negatives?

    Evidence-level negative: YES
      → These texts are near drawing but lack FIG-prefix
      → At Evidence Organization level, they are NOT caption_candidates
      → The organization rule correctly excludes them

    Semantic ground truth negative: PARTIALLY_ESTABLISHED
      → Most are clearly NOT captions (table cells, equations, page numbers)
      → But: some MAY be captions without FIG-prefix (unconventional captioning)
      → Without FIG-prefix, they are unlikely captions but not impossible

  SEMANTIC_NEGATIVE_GROUND_TRUTH = NOT_ESTABLISHED (for Type B also)
    → Same reasoning: Evidence-level exclusion ≠ Semantic GT
```

### 8.3 G5 Gate Status

```
G5_NEGATIVE_SET = PASS (Evidence-level) / CONDITIONAL (Semantic GT)

  Evidence-level negatives: 154 + 6330 = 6484 available
    → Organization rule correctly excludes them → PASS

  Semantic GT negatives: NOT_ESTABLISHED
    → Requires Human Validation to confirm "not associated"
    → CONDITIONAL

  For experiment purposes:
    → Type A/B can be SAMPLED for Human Validation (to confirm they are negatives)
    → Subsample: ~50-80 cases (not all 6484)
    → If Human confirms "not associated" → they become validated negatives
```

---

## 9. G6 Boundary Set Design

### 9.1 Boundary Case Types

```
  1. Multiple drawings (text near 2+ extents)
     AVAILABLE: 7 pages identified
     → Text near multiple extents → which drawing is associated?
     → AMBIGUOUS when distances are similar
     → Count: 7 pages, ~4 with 2+ FIG-prefix near different extents

  2. Similar-distance drawings
     AVAILABLE: within the 7 multi-drawing pages
     → Need to check if any candidate has similar distances to 2 extents
     → If distance ratio < 1.5x → AMBIGUOUS
     → Count: TO_BE_CHECKED (design only, not executed)

  3. Partial x-overlap
     AVAILABLE: some candidates have partial x-overlap
     → Text x-range partially overlaps extent x-range
     → Not a clear "aligned" or "not aligned"
     → Count: present in data but not systematically categorized

  4. Text between drawings
     AVAILABLE: potentially in multi-drawing pages
     → Text at y between two extents, near both
     → Count: TO_BE_CHECKED

  5. FIG-prefix near multiple extents
     AVAILABLE: confirmed (4 pages with 2+ FIG-prefix near different extents)
     → Count: 4 pages

  6. Reference-like text near drawing
     AVAILABLE: 1 confirmed case ("Fig. 3). When..." near extent)
     → Count: 1 (may be more after full scan)
     → This is the caption-vs-reference boundary

  7. Footnote near drawing
     NOT_AVAILABLE_FROM_CURRENT_CORPUS
     → No footnote markers detected near drawing extents in current data
     → May exist but not systematically identified
     → Count: 0 confirmed

  8. Sub-figure labels
     AVAILABLE: 4 confirmed (Fig. 14a, 14b, 14c, 14d on arxiv_2402 p28)
     → These are labels for sub-figures within one drawing
     → Are they "associated with the drawing"? Likely yes, but ambiguous
     → Count: 4
```

### 9.2 Boundary Set Availability

```
  BOUNDARY_SET = PARTIALLY_AVAILABLE_FROM_CURRENT_CORPUS

    Available boundary types:
      ✓ Multiple drawings: 7 pages
      ✓ FIG-prefix near multiple extents: 4 pages
      ✓ Reference-like near drawing: 1 case
      ✓ Sub-figure labels: 4 cases
      ✓ Partial x-overlap: present (not categorized)

    NOT available:
      ✗ Footnote near drawing: 0 confirmed
      ✗ Text between drawings: not systematically checked

    Total confirmed boundary cases: ~16 (7 + 4 + 1 + 4)
    → Sufficient for initial Boundary Set design
    → Some types missing (footnote) — do NOT fabricate
```

### 9.3 G6 Gate Status

```
G6_BOUNDARY_SET = CONDITIONAL

  Design: complete (7 boundary types defined, availability checked)
  Data: ~16 confirmed boundary cases available
  BUT: some boundary types missing (footnote near drawing)
  AND: boundary cases require Human Validation to confirm

  CONDITIONAL because: boundary set is partially available, not fully comprehensive.
  But sufficient for initial experiment design.
```

---

## 10. G7 Sampling Frame

### 10.1 Stratified Sampling Design

```
POPULATION:
  All text atoms + drawing extents across 5 PDFs (95 pages)

SAMPLING FRAME (stratified):

  Stratum 1: Caption candidates (FIG-prefix + near extent)
    Count: 63 deduplicated
    Sampling: ALL (census, not sample) — 63 is manageable
    Purpose: validate as positive / negative / boundary

  Stratum 2: Type A negatives (FIG-prefix + NOT near extent)
    Count: 154 deduplicated
    Sampling: SUBSAMPLE (~30-40 cases)
    Purpose: confirm they are correctly excluded (validate as negative)
    Selection: random across 5 documents

  Stratum 3: Type B negatives (near extent + NO FIG-prefix)
    Count: 6330 deduplicated
    Sampling: SUBSAMPLE (~30-40 cases)
    Purpose: confirm they are correctly excluded (validate as negative)
    Selection: stratified by document + page region type

  Stratum 4: Multi-drawing boundary cases
    Count: 7 pages, ~16 boundary cases
    Sampling: ALL (census)
    Purpose: validate association ambiguity

  Stratum 5: Core diagnostic cases
    Count: 3 (AMB-414, AMB-422, EXT-P28)
    Sampling: ALL (census)
    Purpose: confirm diagnostic value with Human Validation

TOTAL VALIDATION BURDEN:
  63 + 35 + 35 + 16 + 3 = ~152 cases
  (manageable for Human Validation)
```

### 10.2 Anti-Bias Sampling Rules

```
  MUST avoid:
    ❌ Only sampling easiest FIG-prefix cases (would inflate positive rate)
    ❌ Only sampling med_001 (would lose cross-document independence)
    ❌ Only sampling known failure cases (would bias toward diagnostic)
    ❌ Only sampling positive candidates (would miss false positives)

  MUST include:
    ✓ All 63 candidates (census, no cherry-picking)
    ✓ Subsample from ALL 5 documents (cross-document)
    ✓ Negatives from both Type A and Type B (both exclusion mechanisms)
    ✓ Boundary cases (ambiguity testing)
    ✓ Core diagnostic cases (value confirmation)
```

### 10.3 G7 Gate Status

```
G7_SAMPLING_FRAME = PASS

  Design: complete (5 strata, census + subsample, anti-bias rules)
  Burden: ~152 cases (manageable)
  Execution: NOT AUTHORIZED
```

---

## 11. G8 Ground Truth

### 11.1 Ground Truth Levels

```
Three levels of truth:

  1. Machine Candidate (Evidence Organization output)
     → text has FIG-prefix + near extent → caption_candidate
     → This is NOT ground truth — it is a hypothesis

  2. Human Association Judgment (single Human)
     → "Is this text associated with this drawing? (Yes/No/Uncertain)"
     → This is PRIMARY ground truth (but single-judge)

  3. Adjudicated Ground Truth (multiple Humans, resolved)
     → If 2+ Humans agree → confirmed GT
     → If Humans disagree → adjudication process
     → This is FINAL ground truth
```

### 11.2 Disagreement Handling

```
  If two Humans disagree (one says Yes, other says No):

    → DO NOT automatically majority-vote
    → Route to ADJUDICATION:
      1. Present Evidence Pack to third Human (adjudicator)
      2. Adjudicator judges: Yes / No / Uncertain
      3. If adjudicator agrees with one → confirmed GT
      4. If adjudicator says Uncertain → BOUNDARY CASE
         → This case is genuinely ambiguous
         → Record as "semantic boundary" (failure type F)

    This ensures:
      - Disagreement is not hidden by majority vote
      - Genuinely ambiguous cases are preserved as boundary
      - The semantic boundary is respected, not forced
```

### 11.3 G8 Gate Status

```
G8_GROUND_TRUTH = PASS

  Design: complete (3 levels, disagreement → adjudication → boundary)
  No majority vote shortcut
  Semantic boundary respected
  Execution: NOT AUTHORIZED
```

---

## 12. G9 Acceptance Criteria

### 12.1 Metrics Design

```
  NOT using: accuracy / precision / recall alone
    → These require semantic ground truth (caption identity)
    → M-A validates ASSOCIATION, not CAPTION IDENTITY
    → Using accuracy would conflate Organization with Interpretation

  Using these metrics:

  1. Candidate-space reduction (Organization metric)
     → How much did FIG-prefix + proximity reduce the search space?
     → From 6330+154 = 6484 text-drawing pairs to 63 candidates
     → Reduction: 99.0%
     → This measures Organization value, NOT caption recognition accuracy
     → Already confirmed (does not need experiment)

  2. Association validity (validation metric)
     → Of 63 candidates, how many does Human validate as "associated"?
     → Expected: high (most caption_like are likely associated)
     → But: some may be references (not associated)
     → TO_BE_MEASURED (requires Human Validation)

  3. False positive rate (from negatives)
     → Of sampled negatives (Type A + Type B), how many does Human
       validate as "associated" (should be low)?
     → If high → organization rule is too permissive
     → TO_BE_MEASURED

  4. Boundary rate
     → Of all validated cases, what % is "uncertain"?
     → High boundary rate → semantic boundary is significant
     → Low boundary rate → organization is nearly sufficient
     → TO_BE_MEASURED

  5. Human agreement
     → If using 2+ Humans: what is the agreement rate?
     → High agreement → evidence is sufficient for Human judgment
     → Low agreement → cases are genuinely ambiguous (semantic boundary)
     → TO_BE_MEASURED

  6. Human review burden
     → How long does each judgment take?
     → How many cases can Human process per session?
     → Is the burden manageable (~152 cases)?
     → TO_BE_MEASURED

  7. Evidence sufficiency
     → Does the Evidence Pack contain enough information for Human to judge?
     → If Human frequently says "Uncertain" → evidence may be insufficient
     → If Human rarely says "Uncertain" → evidence is sufficient
     → TO_BE_MEASURED
```

### 12.2 What M-A Value Means

```
  M-A has value IF:
    ✓ Candidate-space reduction is high (99.0% — already confirmed)
    ✓ Association validity is high (most candidates are truly associated)
    ✓ False positive rate is low (few negatives are misclassified)
    ✓ Evidence sufficiency is high (Human can judge from Evidence Pack)
    ✓ Human review burden is manageable (~152 cases)

  M-A does NOT claim:
    ❌ Caption detection accuracy (that's Interpretation, not Organization)
    ❌ Caption recognition improvement (that's semantic, not structural)
    ❌ Document understanding improvement (that's Capability, not authorized)
```

### 12.3 G9 Gate Status

```
G9_ACCEPTANCE_CRITERIA = CONDITIONAL

  Design: complete (7 metrics defined, no accuracy/precision/recall alone)
  Metrics distinguish Organization value from Interpretation accuracy
  BUT: acceptance thresholds TO_BE_PRE_REGISTERED
    → Cannot define "what FPR is acceptable" without validation data
    → Cannot define "what association validity is sufficient" without results
    → These must be pre-registered AFTER pilot validation, BEFORE full experiment

  CONDITIONAL because: metric design is complete, but thresholds are not yet set.
```

---

## 13. Human Review Value Gate

### 13.1 HUMAN_REVIEW_VALUE Definition

```
  Question: Are the candidates Human sees more worth reviewing than before?

  BEFORE M-A (E0):
    → Human sees ALL text near drawing (9257/6330 texts per extent)
    → Human must manually find caption-like text
    → Review burden: extremely high (6330 texts to review per document)
    → Signal-to-noise: very low (most are body text, table cells)

  AFTER M-A (E1):
    → Human sees 63 candidates (FIG-prefix + near extent)
    → Review burden: manageable (63 + ~70 negatives + ~16 boundary = ~152)
    → Signal-to-noise: high (most candidates are caption-like)

  HUMAN_REVIEW_VALUE is NOT claimed as achieved.
  HUMAN_REVIEW_VALUE is DESIGNED to be measurable:

    High-value case proportion:
      → Of 63 candidates, how many does Human validate as "associated"?
      → High proportion → high-value candidates
      → TO_BE_MEASURED

    Semantic-boundary proportion:
      → Of 63 candidates, how many are "uncertain" (boundary)?
      → High proportion → semantic boundary is significant
      → Low proportion → organization is nearly sufficient
      → TO_BE_MEASURED

    Trivial-case proportion:
      → Of 63 candidates, how many are "obviously associated"?
      → High proportion → candidates are easy (less value per case)
      → Low proportion → candidates are non-trivial (more value per case)
      → TO_BE_MEASURED

    Human judgment burden:
      → Time per case, cases per session
      → TO_BE_MEASURED
```

### 13.2 What We Do NOT Claim

```
  ❌ Human Value has improved (no validation executed)
  ❌ Human labor has been reduced (no measurement)
  ❌ Caption detection works (not implemented)
  ❌ M-A improves accuracy (not measured)
  ❌ HVA-09 data is real (it is fictional/not-executed)

  We ONLY claim:
    ✓ The DESIGN for measuring Human Review Value is defined
    ✓ The candidate-space reduction is confirmed (99.0%)
    ✓ The validation burden is estimated (~152 cases)
    ✓ The metrics are designed (but not yet measured)
```

---

## 14. Failure Taxonomy Mapping

### 14.1 Existing Taxonomy

```
  A = Perception Missing
  B = Perception Incorrect
  C = Evidence Representation Loss
  D = Evidence Organization Failure
  E = Interpretation / Decision Logic Failure
  F = Genuine Semantic Boundary
  G = Unknown
```

### 14.2 M-A Candidate Failure Mapping

```
  If a Human cannot judge a candidate (says "Uncertain"):

    Possible causes:

    Cause 1: Evidence insufficient
      → Evidence Pack doesn't contain enough information
      → Human can't tell if text is associated with drawing
      → Failure type: D (Evidence Organization Failure)
      → "Organization didn't provide sufficient evidence for judgment"
      → OR: C (Evidence Representation Loss) if key evidence is missing

    Cause 2: Semantic boundary
      → Evidence is sufficient, but the case is genuinely ambiguous
      → "Figure 14a" — is a sub-figure label "associated with the drawing"?
      → Human can see the evidence but the concept is ambiguous
      → Failure type: F (Genuine Semantic Boundary)
      → "This is a legitimate semantic ambiguity, not an evidence failure"

    Cause 3: Perception failure
      → Drawing extent is wrong (aggregation error)
      → Text bbox is wrong (P1 extraction error)
      → Human sees incorrect evidence
      → Failure type: A (Perception Missing) or B (Perception Incorrect)
      → "The observation itself is wrong"

  DISTINCTION:
    Evidence insufficient (D/C): fixable by better organization/representation
    Semantic boundary (F): NOT fixable — it's a legitimate ambiguity
    Perception failure (A/B): fixable by fixing the observation layer

  M-A failure type routing:
    Human "Uncertain" → investigate cause:
      If evidence is incomplete → D or C
      If evidence is complete but ambiguous → F
      If evidence is wrong → A or B
      If cause unclear → G (Unknown)
```

### 14.3 Most Likely M-A Failure Categories

```
  PRIMARY: F (Genuine Semantic Boundary)
    → Caption vs reference, sub-figure labels, footnote vs caption
    → These are semantic ambiguities that evidence cannot resolve

  SECONDARY: D (Evidence Organization Failure)
    → If organization rule is too permissive (includes references)
    → If organization rule is too restrictive (excludes real captions)

  TERTIARY: A/B (Perception Missing/Incorrect)
    → If drawing extent aggregation is wrong
    → If P1 text extraction is incorrect
    → But: frozen baseline is verified, so this is unlikely

  LEAST LIKELY: E (Interpretation/Decision Logic Failure)
    → This would require a Hypothesis layer (not authorized)
    → M-A stops at Organization + Human Validation, no decision logic
```

---

## 15. Final Experiment Entry Gate

### 15.1 Gate Summary

```
G1 SPATIAL_RULES
  - Distance: SUPPORTING, value TO_BE_PRE_REGISTERED
  - Vertical ordering: SUPPORTING, descriptive only
  - X-overlap: SUPPORTING, boolean field
  - Horizontal alignment: UNKNOWN
  - Multiple-drawing: NECESSARY, protocol rule
  → CONDITIONAL (distance value not yet pre-registered)

G2 P1_ATOM_SPLITTING
  - P1 coarse atoms sufficient for caption_like detection
  - P1 modification NOT_REQUIRED
  - Previous "limitation" was counting methodology (now corrected)
  → PASS (upgraded from CONDITIONAL)

G3 HUMAN_VALIDATION
  - Task: ASSOCIATION_JUDGMENT (Yes/No/Uncertain)
  - Evidence Pack: defined with anti-bias
  - Execution: NOT AUTHORIZED
  → PASS (design complete)

G4 POSITIVE_SET
  - 63 candidates available
  - Positive = Human-validated "associated"
  - 0 validated (requires execution)
  → CONDITIONAL (design complete, data available, validation not executed)

G5 NEGATIVE_SET
  - Type A: 154, Type B: 6330
  - Evidence-level negatives: PASS
  - Semantic GT negatives: NOT_ESTABLISHED (requires validation)
  → PASS (Evidence-level) / CONDITIONAL (Semantic GT)

G6 BOUNDARY_SET
  - ~16 confirmed boundary cases (7 types)
  - Some types missing (footnote near drawing)
  → CONDITIONAL (partially available)

G7 SAMPLING_FRAME
  - 5 strata, ~152 cases, anti-bias rules
  → PASS

G8 GROUND_TRUTH
  - 3 levels (candidate → judgment → adjudicated)
  - Disagreement → adjudication → boundary (no majority vote)
  → PASS

G9 ACCEPTANCE_CRITERIA
  - 7 metrics defined (not accuracy/precision/recall alone)
  - Thresholds TO_BE_PRE_REGISTERED
  → CONDITIONAL (metrics designed, thresholds not set)
```

### 15.2 Gate Status Table

```
GATE                    | STATUS
G1 Spatial Rules        | CONDITIONAL
G2 P1 Atom Splitting    | PASS
G3 Human Validation     | PASS
G4 Positive Set         | CONDITIONAL
G5 Negative Set         | PASS (Evidence) / CONDITIONAL (GT)
G6 Boundary Set         | CONDITIONAL
G7 Sampling Frame       | PASS
G8 Ground Truth         | PASS
G9 Acceptance Criteria  | CONDITIONAL

PASS: 4 (G2, G3, G7, G8)
CONDITIONAL: 5 (G1, G4, G5-GT, G6, G9)
FAIL: 0
```

### 15.3 Experiment Readiness

```
M-A_EXPERIMENT_READY = CONDITIONAL

  PASS gates (4): G2, G3, G7, G8
    → These are fully designed and ready.
    → No remaining design work needed.

  CONDITIONAL gates (5): G1, G4, G5-GT, G6, G9
    → All have complete DESIGNS.
    → All are blocked on the SAME root cause:
      → Pre-registration of distance threshold (G1)
      → Human Validation execution (G4, G5-GT, G6, G9)

  FAIL gates: 0
    → No gate is fundamentally broken.
    → No gate requires redesign.

  DESIGN_READY ≠ EXPERIMENT_READY (confirmed):
    → Design IS ready (all 9 gates designed).
    → Experiment is CONDITIONAL (blocked on pre-registration + validation authorization).

  EXPERIMENT_READY ≠ IMPLEMENTATION_READY (confirmed):
    → Experiment can proceed with Human Validation (no code needed).
    → Implementation (detector/algorithm) is separate and NOT authorized.
```

---

## 16. Minimal Remaining Conditions

```
Only 3 conditions block experiment execution:

  1. Pre-register distance threshold (G1)
     → Must freeze a distance value BEFORE seeing validation results.
     → Candidate range: 2.5–55.2pt (observation-based).
     → Must NOT tune after seeing results (anti-p-hacking).
     → ACTION: User authorizes pre-registration; value is declared and frozen.
     → DOES NOT require implementation or code change.

  2. Human Validation authorization (G3 execution)
     → ~152 cases to be judged by Human(s).
     → Task: "Is this text associated with this drawing? (Yes/No/Uncertain)"
     → Evidence Pack is designed (no UI implementation needed — can be text-based).
     → ACTION: User authorizes Human Validation execution.

  3. Acceptance criteria pre-registration (G9)
     → Must define "what results would count as M-A having value?"
     → Blocked on G1 (distance threshold) + G3 (pilot validation data).
     → Can be done AFTER pilot validation, BEFORE full experiment.
     → ACTION: After pilot validation, pre-register acceptance thresholds.

NOTE:
  - G2 (P1 atom splitting) is RESOLVED → no longer a blocker.
  - G6 (boundary set) is partially available → sufficient for pilot.
  - G7 (sampling frame) is complete → ready to execute.
  - G8 (ground truth) is complete → ready to execute.

  The 3 conditions are SEQUENTIAL:
    1 → pre-register distance
    2 → execute Human Validation (using pre-registered distance)
    3 → pre-register acceptance criteria (using pilot results)

  None of these require:
    ❌ Code modification
    ❌ P1/P2/AO/TLD change
    ❌ Implementation of detector/algorithm
    ❌ LLM/classifier
    ❌ Capability/Runtime
```

---

## 17. Final Decision

```
M-A_EXPERIMENT_READY = CONDITIONAL

  The M-A Research Object is:
    ✓ Formally defined (Text-Drawing Association)
    ✓ Evidence-grounded (P1 + P2 + DRAWING_EXTENT_FACT + spatial)
    ✓ Boundary-clear (caption_candidate ≠ caption)
    ✓ Human-validation-ready (ASSOCIATION_JUDGMENT, Evidence Pack designed)
    ✓ Sampling-frame-ready (5 strata, ~152 cases, anti-bias)
    ✓ Ground-truth-ready (3 levels, adjudication, no majority vote)
    ✓ Metric-designed (7 metrics, not accuracy alone)
    ✓ Cross-document (5/5 PDFs, pattern confirmed)
    ✓ Corrected data (63 candidates, 154+6330 negatives, deduplicated)

  The 3 blocking conditions are:
    1. Distance threshold pre-registration (G1)
    2. Human Validation execution authorization (G3)
    3. Acceptance criteria pre-registration (G9, after pilot)

  These are AUTHORIZATION gates, not DESIGN gates.
  The DESIGN is complete.
  The NEXT STEP is user authorization, not more research.

  Recommendation:
    → Step 1: Authorize distance threshold pre-registration
    → Step 2: Authorize pilot Human Validation (~30-50 cases)
    → Step 3: Based on pilot, pre-register acceptance criteria
    → Step 4: Authorize full Human Validation (~152 cases)
    → Step 5: Analyze results

  Each step requires separate user authorization.
  No step is automatic.
```

### Sub-assessments

```
EXTENT_VALUE = ESSENTIAL (confirmed, unchanged)
CROSS_DOCUMENT_STATUS = DEMONSTRATED (5/5 PDFs, candidate level)
PURE_GEOMETRIC_ORGANIZATION = NOT_DEMONSTRATED (geometry alone insufficient)
SEMANTIC_BOUNDARY = IDENTIFIED (caption_candidate ≠ caption)
FIG_PREFIX_ROLE = CANDIDATE_SPACE_REDUCTION (Organization Support)

CORRECTED_COUNTS:
  CANDIDATE_COUNT = 63 (was 126, deduplicated)
  NEGATIVE_TYPE_A = 154 (was 280, deduplicated)
  NEGATIVE_TYPE_B = 6330 (was 9257, deduplicated)
  BOUNDARY_CASES = ~16 (7 types, partially available)
  VALIDATION_BURDEN = ~152 cases (manageable)

P1_MODIFICATION = NOT_REQUIRED (resolved)
  → P1 coarse atoms contain caption patterns
  → Previous "limitation" was counting methodology, not P1

DESIGN_READY ≠ EXPERIMENT_READY (confirmed)
EXPERIMENT_READY ≠ IMPLEMENTATION_READY (confirmed)
```

---

## 18. Governance Status

```text
M-A_PRE_EXPERIMENT_GATE_DESIGN = COMPLETE

M-A_EXPERIMENT_READY = CONDITIONAL

GATE STATUS:
  G1 Spatial Rules        = CONDITIONAL (distance value TO_BE_PRE_REGISTERED)
  G2 P1 Atom Splitting    = PASS (P1 NOT_REQUIRED, resolved)
  G3 Human Validation     = PASS (design complete, execution NOT authorized)
  G4 Positive Set         = CONDITIONAL (63 candidates, 0 validated)
  G5 Negative Set         = PASS (Evidence) / CONDITIONAL (Semantic GT)
  G6 Boundary Set         = CONDITIONAL (~16 cases, partially available)
  G7 Sampling Frame       = PASS (5 strata, ~152 cases)
  G8 Ground Truth         = PASS (3 levels, adjudication)
  G9 Acceptance Criteria  = CONDITIONAL (metrics designed, thresholds not set)

MINIMAL REMAINING CONDITIONS (3):
  1. Pre-register distance threshold (G1)
  2. Human Validation execution authorization (G3)
  3. Acceptance criteria pre-registration (G9, after pilot)

CORRECTED DATA (deduplicated):
  CANDIDATE_COUNT = 63 (was 126)
  NEGATIVE_TYPE_A = 154 (was 280)
  NEGATIVE_TYPE_B = 6330 (was 9257)
  BOUNDARY_CASES = ~16
  VALIDATION_BURDEN = ~152

KEY CORRECTIONS:
  - P1 atom splitting: NOT a limitation (was mischaracterized)
    P1 coarse atoms contain caption patterns; issue was counting methodology
  - P1_MODIFICATION_REQUIRED = NOT_REQUIRED (was DESIGN_DECISION_REQUIRED)
  - Candidate count: 63 (was 126, 50% duplicate inflation corrected)
  - Vertical ordering: 83% below (was 87%, corrected after dedup)

HUMAN_TASK = ASSOCIATION_JUDGMENT (Yes/No/Uncertain)
  NOT caption classification, NOT merge decision, NOT feature specification

EVIDENCE_PACK:
  REQUIRED: text content, extent bbox, text bbox, spatial relation, FIG-prefix
  SUPPORTING: adjacent text context (same_y)
  OPTIONAL: page context (multi-drawing, P6 region)
  FORBIDDEN: semantic labels, scores, recommendations, algorithm output

ACCEPTANCE METRICS (7):
  1. Candidate-space reduction (99.0% — confirmed)
  2. Association validity (TO_BE_MEASURED)
  3. False positive rate (TO_BE_MEASURED)
  4. Boundary rate (TO_BE_MEASURED)
  5. Human agreement (TO_BE_MEASURED)
  6. Human review burden (TO_BE_MEASURED)
  7. Evidence sufficiency (TO_BE_MEASURED)

FAILURE TAXONOMY:
  PRIMARY: F (Genuine Semantic Boundary)
  SECONDARY: D (Evidence Organization Failure)
  TERTIARY: A/B (Perception Missing/Incorrect)
  LEAST LIKELY: E (Interpretation/Decision Logic — not authorized)

AO_VISUAL_GEOMETRY = IMPLEMENTED (COMPLETE)
AO_VALUE_EXPERIMENT = COMPLETE (VALUE_PARTIALLY_SUPPORTED)
EVIDENCE_ORGANIZATION_DIAGNOSTIC = COMPLETE (PARTIALLY_TESTABLE)
EVIDENCE_ORGANIZATION_INDEPENDENCE = COMPLETE (CONDITIONAL)
M-A_DESIGN_RESEARCH = COMPLETE (DESIGN_READY_WITH_CONDITIONS)
M-A_PRE_EXPERIMENT_GATE_DESIGN = COMPLETE (EXPERIMENT_READY=CONDITIONAL)

FROZEN_BASELINE = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d, P1=74d23ec7)
P1_P6 = UNCHANGED
P7.1 = UNCHANGED
TLD = UNCHANGED
IS-11 = UNCHANGED (FROZEN, not modified)
IS-14 = UNCHANGED

CAPABILITY = UNCHANGED
RUNTIME_AUTHORITY = ZERO
PRODUCTION = FALSE

IMPLEMENTATION = NOT AUTHORIZED
EXPERIMENT = NOT AUTHORIZED
HUMAN_VALIDATION = NOT AUTHORIZED
HUMAN_FEEDBACK = NOT AUTHORIZED
L3 = NOT AUTHORIZED

STOP = TRUE
```

---

## Research Principle Adherence

- ✅ Used only existing evidence (5 PDFs, 63 deduplicated candidates, 154+6330 negatives)
- ✅ No new corpus creation
- ✅ No threshold values selected (all TO_BE_PRE_REGISTERED)
- ✅ No implementation
- ✅ No experiment execution
- ✅ No Human Validation execution
- ✅ Corrected candidate count (126 → 63, duplicate inflation identified and resolved)
- ✅ Corrected P1 atom splitting characterization (NOT a P1 limitation)
- ✅ P1 modification = NOT_REQUIRED (resolved)
- ✅ Strictly distinguished caption_candidate ≠ caption
- ✅ FIG-prefix = Organization Support (not Interpretation)
- ✅ Semantic boundary identified (not hidden)
- ✅ Human Validation unit is ASSOCIATION_JUDGMENT (not caption classification)
- ✅ Evidence Pack has anti-bias (no semantic labels, scores, recommendations)
- ✅ Ground truth has adjudication (no majority vote shortcut)
- ✅ Metrics distinguish Organization value from Interpretation accuracy
- ✅ HUMAN_REVIEW_VALUE designed but NOT claimed as achieved
- ✅ Did NOT claim caption detection works
- ✅ Did NOT claim accuracy improvement
- ✅ Did NOT claim Human Value improved
- ✅ Did NOT use HVA-09 fictional data
- ✅ Did NOT modify any code/AO/P1-P7/TLD/IS-11
- ✅ Frozen baseline intact
- ✅ DESIGN_READY ≠ EXPERIMENT_READY (confirmed)
- ✅ EXPERIMENT_READY ≠ IMPLEMENTATION_READY (confirmed)
- ✅ 3 minimal conditions identified (not entire history re-listed)

`STOP = TRUE`.
