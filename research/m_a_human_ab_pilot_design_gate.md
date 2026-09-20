# M-A Human A/B Evidence Sufficiency Pilot — Design Gate

> **DESIGN GATE / READ-ONLY / NO EXECUTION / STOP**
> 日期: 2026-09-18
> 前置: M-A Evidence Pack Counterfactual Diagnostic (EVIDENCE_PACK_IMPROVEMENT_SUPPORTED)
> 本文件: 设计 Human A/B Pilot，验证 E1 是否减少 Document Reconstruction Burden。

---

## 1. Design Status

```
DESIGN_STATUS = DESIGN_READY

  本设计完整覆盖：
    - 研究问题
    - E0/E1 定义
    - 采样框架
    - A/B 分配
    - 随机化规则
    - 盲化策略
    - 指标定义
    - 负担等级
    - Evidence Sufficiency 定义
    - Semantic Boundary 规则
    - Stop Rule
    - 预注册冻结

  未执行任何 Human Validation。
  未修改任何代码或数据。

EXPERIMENT_READY = TRUE
  （设计完整，可执行）

HUMAN_VALIDATION_AUTHORIZED = FALSE
  （授权须由用户下一步明确给出）
```

---

## 2. Research Question

```
RQ:
  相比旧 Evidence Pack (E0)，
  新 Evidence Pack (E1) 是否能够：

  1. 降低 Human 对原始 PDF 的重新阅读需求
  2. 降低 Document Reconstruction Burden
  3. 提高 Human 对 Evidence Sufficiency 的判断
  4. 减少由于 Evidence 不完整产生的 UNCERTAIN
  5. 在不增加语义结论的情况下，
     使 Text–Drawing Association 更容易被 Human 验证

  本实验不是：
    - Caption Detection Accuracy
    - Figure Detection Accuracy
    - Association Machine Accuracy
    - M-A Algorithm Accuracy
    - Semantic Classification
    - LLM Benchmark

  核心比较指标：
    E0 → E1 的 RECONSTRUCTION_BURDEN_CHANGE

  重点回答：
    E1 < E0 在 Human Reconstruction Burden 上？
```

---

## 3. E0 / E1 Definition

```
E0_DEFINITION:
  = 上一轮 Human Validation Pilot 实际使用的旧 Evidence Pack
  = ±3pt same_y threshold
  = Type A negatives: context_text='', context_atoms=[], extent_bbox=None
  = Type B negatives: context_text='', context_atoms=[]
  = No evidence_state field
  = 60pt used for BOTH candidate generation AND pack inclusion

E1_DEFINITION:
  = 当前已实施完成并通过 Implementation Verification 的新 Evidence Pack
  = ±5pt same_y threshold (PR1)
  = All cases: unified context collection (PR1 + G4)
  = Nearest extent always included (PR2)
  = 3-state evidence_state (PR3)
  = 60pt = candidate generation only (PR2)

E0/E1 CASE_ALIGNMENT:
  = 79 cases with identical CASE_IDs
  = Perfect alignment (verified: 79 = 79, 0 mismatches)

E0_RECOVERY_STATUS:
  = RECONSTRUCTED (original E0 data files overwritten by E1)
  = E0_RECONSTRUCTION_METHOD: OLD_LOGIC_RECONSTRUCTION
  = Reconstruction uses same frozen inputs (P1, DGF, DEF)
  = Same random seeds (42 for negative sampling, 123 for ordering)
  = Old logic precisely documented in diagnostic reports
  = E0_RECONSTRUCTION_BIAS_RISK: LOW
  = Verification: 16/16 negatives have empty context (expected)
  = Verification: 8/8 Type A have extent=None (expected)
  = Verification: evidence_state field absent (expected)

  NOTE:
    Original E0 data files (candidates.json, candidates_internal.json)
    were overwritten during E1 Implementation.
    No git history or backup exists.
    E0 was reconstructed by replicating the exact old generate_data.py logic.
    This is NOT a "simulated approximate E0" — it uses the same frozen
    inputs and documented logic. Case IDs match E1 perfectly.

E1_SOURCE:
  = tmp/m_a_human_review_pilot/data/candidates_internal.json (current)
  = Verified intact (sha16 verified, 3 runs byte-identical)
```

---

## 4. Sampling Frame

```
SAMPLING_FRAME:
  = 79 cases from M-A Human Validation Pilot
  = All case types: caption_like, ambiguous_fragment, subfigure_label,
    reference_like, Type A negative, Type B negative
  = All documents: is11_med_001, is11_resnet, is11_efficientnet,
    is11_cs_001, arxiv_2402.18619

STRATA (defined by E0 characteristics ONLY — NOT E1):

  S1_COMPLETE_YES (n=56):
    E0 Pack complete + E0 judgment YES
    Purpose: regression test (E1 should NOT regress)
    
  S3_COMPLETE_UNCERTAIN (n=3):
    E0 Pack complete + E0 judgment UNCERTAIN
    Purpose: semantic boundary test (E1 should NOT resolve if genuine boundary)
    
  S4_TYPE_A_NEGATIVE (n=8):
    Type A negative (FIG-prefix, not near extent)
    E0 Pack: INCOMPLETE (no extent, no context)
    E0 judgments: 7 UNCERTAIN, 1 YES
    Purpose: E1 improvement test (context + extent restored)
    
  S5_TYPE_B_NEGATIVE (n=8):
    Type B negative (near extent, no FIG-prefix)
    E0 Pack: PARTIAL (extent but no context)
    E0 judgments: 4 YES, 4 UNCERTAIN
    Purpose: E1 improvement test (context restored)
    
  S6_NO_JUDGMENT (n=4):
    E0 judgment NO
    Purpose: semantic leakage test (E1 should NOT change NO to YES)

  NOTE:
    S2 (incomplete Pack + UNCERTAIN, non-negative) is EMPTY because
    all incomplete-Pack UNCERTAIN cases are Type A/B negatives
    (already captured in S4/S5).

SAMPLE_SIZE:
  = 24 cases (12 per arm)

  Composition:
    S1_COMPLETE_YES:       8 (33%) — 4 per arm — regression test
    S3_COMPLETE_UNCERTAIN: 2 (8%)  — 1 per arm — semantic boundary
    S4_TYPE_A_NEGATIVE:    6 (25%) — 3 per arm — improvement test
    S5_TYPE_B_NEGATIVE:    4 (17%) — 2 per arm — improvement test
    S6_NO_JUDGMENT:        4 (17%) — 2 per arm — leakage test

  Balance:
    Not improvement-heavy: 33% regression + 17% leakage = 50% non-improvement
    Improvement test: 25% + 17% = 42%
    Semantic boundary: 8%
    
  This composition avoids:
    ✗ Only selecting E1-improved cases (42% improvement, 50% non-improvement)
    ✗ Only selecting UNCERTAIN (9/24 = 37.5% UNCERTAIN, 62.5% definitive)
    ✗ Only selecting negatives (10/24 = 42% negatives, 58% candidates)
    ✗ Only selecting one case type (6 types covered)
    ✗ Only selecting one document (5 documents covered)

INCLUSION_RULE:
  = Case must exist in BOTH E0 and E1 with identical CASE_ID
  = Case must belong to one of the 5 defined strata
  = Case must have a rendered page image available

EXCLUSION_RULE:
  = Case not in the 79-case Pilot set
  = Case with missing page image
  = S_OTHER stratum (not_reviewed or edge cases)

RANDOMIZATION_RULE:
  = PRE-REGISTERED, deterministic, seeded
  = Selection seed: 777 (per-stratum, using hash(stratum) for variation)
  = Allocation seed: 888 (per-stratum, using hash(stratum) for variation)
  = Presentation seed: 999 (global interleaving)
  
  Method:
    1. Within each stratum: sort by case_id (deterministic)
    2. Shuffle with per-stratum seed → take first N
    3. Shuffle selected with per-stratum seed → assign alternating A/B
    4. Global shuffle with seed 999 → presentation order (interleaved)
  
  This ensures:
    - Reproducible (same seeds → same selection)
    - No cherry-picking (mechanical randomization)
    - Balanced arms (stratified allocation)
    - Interleaved presentation (no arm clustering)

RANDOMIZATION_VERIFIED:
  Arm A (E0): 12 cases
    Strata: S1=4, S3=1, S4=3, S5=2, S6=2
    E0 judgments: YES=7, UNCERTAIN=3, NO=2
    Documents: 5 documents covered
    
  Arm B (E1): 12 cases
    Strata: S1=4, S3=1, S4=3, S5=2, S6=2
    E0 judgments: YES=4, UNCERTAIN=6, NO=2
    Documents: 5 documents covered

  NOTE: Arm B has more UNCERTAIN (6 vs 3) due to randomization.
  This is acceptable for a pilot — descriptive comparison only.
  No statistical significance claimed.
```

---

## 5. A/B Allocation

```
A_B_ALLOCATION:
  = Parallel case split with stratified randomization
  = Each case assigned to EITHER Arm A (E0) OR Arm B (E1)
  = Each case seen ONCE (no within-case repetition)
  
  Arm A (E0): 12 cases → Human sees OLD Evidence Pack
  Arm B (E1): 12 cases → Human sees NEW Evidence Pack

DESIGN_CHOICE_RATIONALE:
  
  Chosen: Parallel case split (NOT counterbalanced within-subject)
  
  Why NOT counterbalanced within-subject (A→B and B→A on same case):
    - Same Human seeing same case twice → SEVERE memory/carryover
    - Human remembers the case and prior judgment
    - Second viewing is biased by first viewing
    - For 24 cases, this would require 48 reviews with high carryover
  
  Why parallel case split:
    - Each case seen ONCE → ZERO carryover
    - Stratified randomization ensures balanced arms
    - Single Human reviews all 24 in interleaved random order
    - Human cannot tell which case is in which arm (no labels)
    - MINIMAL design that controls the primary threat (carryover)
  
  Trade-off:
    - Cannot directly compare E0 vs E1 for SAME case
    - Can compare AGGREGATE rates (e.g., E0 arm PDF reopen vs E1 arm)
    - Sufficient for pilot descriptive comparison
    - Acceptable for small pilot (not statistical power analysis)

CARRYOVER_ASSESSMENT:
  Primary carryover (same case, both Packs): ELIMINATED (parallel split)
  Secondary carryover (same Human did E0 Pilot before):
    - Risk: Human might remember some of the 79 E0 Pilot cases
    - Mitigation: cases reordered, Pack content differs for E1 cases
    - Mitigation: sufficient time gap recommended (≥1 week)
    - Residual risk: LOW (simple YES/NO/UNCERTAIN task, 79 cases hard to remember)
    - If different Human used: risk = ZERO
```

---

## 6. Blinding

```
BLINDING_STATUS = PARTIAL

  What IS blinded:
    ✓ Human does NOT see "E0" or "E1" labels
    ✓ Human does NOT see "OLD" or "NEW" labels
    ✓ Human does NOT see "A" or "B" labels
    ✓ Human does NOT see "IMPROVED" or "EXPERIMENTAL"
    ✓ Human does NOT know which version is "new" or "expected to be better"
    ✓ Human does NOT see case_type, stratum, or E0 judgment
    ✓ Human does NOT see GT, algorithm output, or expected answer
    ✓ Presentation order interleaves E0 and E1 cases randomly

  What is NOT blinded (intrinsic, unavoidable):
    ✗ Pack CONTENT differs between E0 and E1:
      - E1 has evidence_state field (E0 does not)
      - E1 has context for negatives (E0 does not)
      - E1 shows extent even when far (E0 shows "no drawing")
    - This is intrinsic to the design — you cannot hide that one Pack
      has more information than the other
    - Human MIGHT notice content differences across cases
    - But Human CANNOT determine which is "old" vs "new" without labels

  Why FULL blinding is NOT feasible:
    - The Packs differ in content by design (that's what we're testing)
    - Hiding content differences would defeat the experiment's purpose
    - The key blinding is: Human doesn't know which version is "new"
    
  Conclusion:
    PARTIAL blinding is the maximum achievable.
    The critical bias (knowing which is "improved") is controlled.
    Content visibility is intrinsic and acceptable.
```

---

## 7. Human Task

```
HUMAN_TASK:
  
  Core question (displayed for each case):
    "这个文本是否与这个图形关联？"
    ("Is this text associated with this drawing?")
  
  Allowed answers:
    YES
    NO
    UNCERTAIN

  Human role:
    MINIMAL SEMANTIC VALIDATOR
  
  Human does NOT:
    - Write reasons
    - Give confidence
    - Judge caption / figure / chart / semantic class
    - Specify algorithm
    - Modify Evidence
    - Choose threshold
    - See case type, GT, previous judgment, algorithm output

  Additional self-report questions (after each judgment):
    M2: "你是否需要打开原始 PDF 才能完成判断？" (YES/NO)
    M3: "你是否需要在 Evidence Pack 之外寻找额外上下文？" (YES/NO)
    M4: "你经历的 Document Reconstruction Burden 等级？" (0-4)
    M6: "当前 Evidence Pack 是否足以完成判断？" (SUFFICIENT/INSUFFICIENT/UNCERTAIN)
    
  UNCERTAIN follow-up (OPTIONAL, not forced):
    If Human selects UNCERTAIN for M1:
      Optional: "为什么不确定？" 
        A: Evidence 不足
        B: 语义本身模糊
        C: 其他 / 无法确定
      If Human skips: recorded as UNCERTAIN_UNCLASSIFIED
      Post-hoc analysis uses M4+M6 to classify

  Human does NOT:
    - Diagnose semantic boundary (that's post-hoc analysis)
    - Write complex reasoning
    - Rate cognitive load (no NASA-TLX)
```

---

## 8. Metrics

```
METRICS:

  M1: ASSOCIATION_JUDGMENT
    Values: YES / NO / UNCERTAIN
    Type: HUMAN JUDGMENT DISTRIBUTION (NOT machine accuracy)
    Note: YES rate is NOT accuracy. Negative YES is NOT false positive.

  M2: PDF_REOPEN_REQUIRED
    Values: YES / NO
    Definition: Human must open original PDF to complete judgment.
    Self-reported by Human after each case.

  M3: ADDITIONAL_DOCUMENT_SEARCH_REQUIRED
    Values: YES / NO
    Definition: Human must search beyond Evidence Pack for context.
    Self-reported by Human after each case.

  M4: HUMAN_RECONSTRUCTION_BURDEN
    Values: LEVEL 0 / LEVEL 1 / LEVEL 2 / LEVEL 3 / LEVEL 4
    Definition: (FROZEN — same as previous diagnostic, NOT redefined)
      LEVEL 0: Pack complete, no reconstruction needed
      LEVEL 1: Need local context (same_y line)
      LEVEL 2: Need multiple sentences / page content
      LEVEL 3: Must open PDF / understand page layout
      LEVEL 4: Pack cannot support judgment even after PDF
    Self-reported by Human, guided by M2 and M3.

  M5: TIME_TO_JUDGMENT
    Status: NOT_AVAILABLE
    Note: Current UI does not reliably record per-case timing.
    Do NOT fabricate time data. If UI is upgraded, M5 becomes available.

  M6: EVIDENCE_SUFFICIENCY
    Values: SUFFICIENT / INSUFFICIENT / UNCERTAIN
    Definition:
      SUFFICIENT = Human believes current Evidence Pack is sufficient
                  to complete Association Judgment.
      INSUFFICIENT = Human believes Pack lacks necessary Evidence.
      UNCERTAIN = Human cannot determine sufficiency.
    Note: Evidence Sufficiency ≠ Association Truth.
    Self-reported by Human after each case.

  PRIMARY_COMPARISON_METRIC:
    RECONSTRUCTION_BURDEN_CHANGE = E0_arm_burden vs E1_arm_burden
    
    Compared on:
      - PDF reopen rate (M2): E0_arm YES% vs E1_arm YES%
      - Additional search rate (M3): E0_arm YES% vs E1_arm YES%
      - Burden level distribution (M4): E0_arm levels vs E1_arm levels
      - UNCERTAIN distribution (M1): E0_arm UNCERTAIN% vs E1_arm UNCERTAIN%
      - Evidence sufficiency (M6): E0_arm SUFFICIENT% vs E1_arm SUFFICIENT%

    NOT a composite score. Descriptive comparison only.
```

---

## 9. Evidence Sufficiency Definition

```
EVIDENCE_SUFFICIENCY_DEFINITION:

  SUFFICIENT:
    Human believes the Evidence Pack contains enough information
    to make an Association Judgment (YES or NO).
    
    "Enough" means: the Pack provides the text, drawing, spatial relation,
    and context needed to assess whether the text refers to the drawing.
    
    SUFFICIENT does NOT mean:
      - The association is YES (Pack can be sufficient for a NO judgment)
      - The judgment is easy (Pack can be sufficient but judgment is hard)
      - No cognitive effort is needed

  INSUFFICIENT:
    Human believes the Evidence Pack lacks necessary information
    to make a confident judgment.
    
    "Lacks" means: missing text, missing drawing, missing context,
    or missing spatial relation that would be needed.

  UNCERTAIN:
    Human cannot determine whether the Pack is sufficient.
    Usually means: Pack seems complete but judgment is still unclear.

  CRITICAL DISTINCTION:
    Evidence Sufficiency ≠ Association Truth
    
    A Pack can be SUFFICIENT for a NO judgment
    (enough evidence to say "this text is NOT associated with this drawing").
    
    A Pack can be SUFFICIENT but the judgment is still UNCERTAIN
    (Pack has all evidence, but the semantic question is genuinely ambiguous).
    
    This distinction is essential for the Semantic Boundary audit.
```

---

## 10. Semantic Boundary Rule

```
SEMANTIC_BOUNDARY_RULE:

  If Human selects UNCERTAIN (M1), classify as follows:

  A. EVIDENCE_INSUFFICIENT:
    Condition: M6 = INSUFFICIENT
    Meaning: Pack did not provide enough evidence.
    This is NOT a semantic boundary — it's a Pack gap.
    
  B. POSSIBLE_SEMANTIC_BOUNDARY:
    Condition: M6 = SUFFICIENT AND M4 ≤ 1
    Meaning: Pack was sufficient and burden was low,
    but Human still could not determine association.
    This MAY be a genuine semantic interpretation boundary.
    
  C. NOT_DETERMINABLE:
    Condition: M6 = UNCERTAIN OR M4 ≥ 2
    Meaning: Cannot classify — either sufficiency unclear
    or burden too high to distinguish Pack gap from semantic boundary.

  CRITICAL RULE:
    UNCERTAIN alone does NOT mean semantic boundary.
    
    Only when:
      Evidence sufficient (M6=SUFFICIENT)
      AND burden low (M4≤1)
      AND Human still uncertain (M1=UNCERTAIN)
    
    Can we mark POSSIBLE_SEMANTIC_BOUNDARY.
    
    Otherwise: EVIDENCE_INSUFFICIENCY or NOT_DETERMINABLE.

  This rule ensures:
    - Pack gaps are NOT mislabeled as semantic boundaries
    - Only genuine ambiguity (with complete evidence) counts
    - Human is NOT asked to diagnose — classification is automatic
```

---

## 11. Stop Rule

```
STOP_RULE:

  The experiment MUST stop immediately if ANY of the following is detected:

  STOP-1: E1 Evidence Regression
    Any E1 field value is worse than E0 for the same case.
    Check: compare E0 and E1 fields for each case.
    Example: E0 has extent=set but E1 has extent=None (regression).

  STOP-2: E1 Modified Existing Human Data
    human_session_1.json is modified.
    Check: sha256 of human_session_1.json before and after.

  STOP-3: Frozen Baseline Drift > 0
    Any frozen file sha256 changes.
    Check: P1, TLD, GT, layout_analyzer, DGF, DEF.

  STOP-4: Semantic Leakage
    New semantic field appears in Evidence Pack.
    Forbidden fields: decision, prediction, classification, confidence,
    score, recommendation, ranking, semantic_label, caption, figure,
    is_caption, is_figure, association_score, machine_judgment.

  STOP-5: A/B Evidence Not Same Case
    Case IDs in Arm A and Arm B don't come from the same 79-case pool.
    Check: verify all 24 case_ids exist in both E0 and E1.

  STOP-6: E0/E1 Cannot Be Reliably Distinguished
    E0 and E1 Packs are identical for a case assigned to a specific arm.
    Check: verify E0 ≠ E1 for all cases where arm assignment expects
    a specific version.

  STOP-7: Human Data Contamination
    Human sees GT, previous judgment, case type, or algorithm output
    during the experiment.
    Check: UI inspection before experiment.

  If ANY stop condition is triggered:
    → Stop collecting Human Data immediately
    → Record which condition was triggered
    → Do NOT continue the experiment
    → Report to user for decision

  These checks are PRE-REGISTERED and FROZEN.
```

---

## 12. Pre-Registration Status

```
PRE_REGISTRATION_STATUS:

  The following are FROZEN before any Human Validation:

  1. Sampling Frame: 79 cases, 5 strata (S1, S3, S4, S5, S6) ✓ FROZEN
  2. Sampling Rule: stratified randomization, seed=777 ✓ FROZEN
  3. A/B Allocation: 12 per arm, seed=888 ✓ FROZEN
  4. Randomization: seed=999 for presentation order ✓ FROZEN
  5. Blinding: PARTIAL (no version labels, content visible) ✓ FROZEN
  6. Metrics: M1-M6 (M5=NOT_AVAILABLE) ✓ FROZEN
  7. Reconstruction Burden Definition: Level 0-4 (unchanged) ✓ FROZEN
  8. Evidence Sufficiency Definition: SUFFICIENT/INSUFFICIENT/UNCERTAIN ✓ FROZEN
  9. Stop Rule: 7 conditions (STOP-1 to STOP-7) ✓ FROZEN
  10. Semantic Boundary Rule: 3-class classification ✓ FROZEN
  11. PR1/PR2/PR3: ±5pt, 60pt candidate-gen-only, 3-state ✓ FROZEN
  12. Case selection: 24 cases (listed in sampling_frame.csv) ✓ FROZEN

  PROHIBITED after pre-registration:
    - Looking at partial Human results then modifying design
    - Adding/removing cases based on early results
    - Changing arm assignments
    - Redefining metrics or burden levels
    - Adjusting thresholds

  All design parameters are recorded in:
    - tmp/m_a_human_ab_pilot_design_gate.md (this file)
    - tmp/m_a_human_ab_pilot_design_gate.json
    - tmp/m_a_human_ab_pilot_sampling_frame.csv (79 cases, 24 selected)
```

---

## 13. Statistical Requirements

```
STATISTICAL_REQUIREMENTS:

  This is a SMALL PILOT, NOT formal statistical power analysis.

  PROHIBITED:
    - Calculating non-existent significance
    - Claiming "statistically significant"
    - Over-generalization
    - Cross-domain generalization claims

  ALLOWED:
    - Descriptive comparison
    - Example: "E0 arm PDF reopen rate = X%, E1 arm = Y%"
    - Example: "E0 arm Level 3 = N cases, E1 arm Level 3 = M cases"
    
  All comparisons labeled as: PILOT EVIDENCE (not conclusive)

  Sample size justification:
    24 cases (12 per arm) is sufficient for:
      - Descriptive rate comparison
      - Detecting LARGE effects (e.g., 0% vs 50% reopen rate)
      - Identifying patterns for future research
    
    NOT sufficient for:
      - Detecting small effects
      - Statistical significance testing
      - Generalization to other document domains
```

---

## 14. Human Burden Measurement Boundary

```
HUMAN_BURDEN_MEASUREMENT_BOUNDARY:

  This experiment measures:
    ✓ Document Reconstruction Burden (M2, M3, M4)
    ✓ Evidence Sufficiency (M6)
    ✓ Association Judgment distribution (M1)

  This experiment does NOT measure:
    ✗ Cognitive load (no NASA-TLX, no cognitive rating)
    ✗ Mental effort
    ✗ Fatigue
    ✗ Time (M5 = NOT_AVAILABLE)

  THEREFORE:
    - "100% completion" does NOT mean "low cognitive load"
    - "Burden decreased" refers ONLY to Document Reconstruction Burden
    - Cannot claim "cognitive load decreased" without cognitive measure
    - Can claim: "Document Reconstruction Burden decreased" (if data supports)

  This boundary is PRE-REGISTERED and MUST be respected in reporting.
```

---

## 15. Negative Control Audit (Design)

```
NEGATIVE_CONTROL_AUDIT:

  Type A negative (FIG-prefix, not near extent): 6 selected (3 per arm)
    E0 Pack: INCOMPLETE (no extent, no context)
    E1 Pack: context + extent (where DEF>0) or evidence_state distinction
    
    What to test:
      - E0 arm: Human likely needs PDF (burden Level 3)
      - E1 arm: Human should need less PDF (burden Level ≤ 2)
      - E1 arm: evidence_state should help Human understand
        "no extent" vs "primitives exist" vs "extent far away"

  Type B negative (near extent, no FIG-prefix): 4 selected (2 per arm)
    E0 Pack: PARTIAL (extent but no context)
    E1 Pack: extent + context
    
    What to test:
      - E0 arm: Human has drawing but no text context
      - E1 arm: Human has both drawing and text context
      - Burden should decrease (Level 1 → Level 0)

  HUMAN JUDGMENT DISTRIBUTION:
    - Reported as "Human judgment distribution" (NOT machine accuracy)
    - NOT reported as "FPR" or "accuracy"
    - Negative YES is "Human judged YES" (NOT "false positive")
    
  NOTE:
    E0 judgments for negatives were made under E0 (incomplete Pack).
    A/B Pilot judgments are INDEPENDENT (new session, new Pack version).
    Do NOT compare A/B Pilot judgments to E0 Pilot judgments directly.
    Compare WITHIN the A/B Pilot: Arm A vs Arm B.
```

---

## 16. Expected Outcomes (Hypotheses, NOT Pre-Determined Results)

```
HYPOTHESES (to be tested, NOT pre-determined):

  H1: E1 arm will have LOWER PDF reopen rate (M2) than E0 arm.
    Rationale: E1 provides context + extent for negatives.
    Expected: E0 arm M2=YES > E1 arm M2=YES.

  H2: E1 arm will have LOWER burden levels (M4) than E0 arm.
    Rationale: E1 eliminates Level 3 (must open PDF) for negatives.
    Expected: E0 arm Level 3 > E1 arm Level 3.

  H3: E1 arm will have HIGHER evidence sufficiency (M6=SUFFICIENT) than E0 arm.
    Rationale: E1 provides more complete Pack.
    Expected: E1 arm SUFFICIENT% > E0 arm SUFFICIENT%.

  H4: E1 arm will have FEWER UNCERTAIN due to evidence insufficiency.
    Rationale: E1 resolves Collection/Presentation/Organization gaps.
    Expected: E1 arm UNCERTAIN(EVIDENCE_INSUFFICIENT) < E0 arm.
    Note: UNCERTAIN(POSSIBLE_SEMANTIC_BOUNDARY) may NOT decrease.

  H5: E1 arm will NOT increase NO→YES leakage on S6 (NO judgment) cases.
    Rationale: E1 adds evidence, not semantic labels.
    Expected: S6 cases in E1 arm remain NO or become UNCERTAIN,
    NOT flip to YES.

  These hypotheses are NOT pre-determined results.
  The experiment tests them. Results may confirm or refute.
  ALL results are reported regardless of direction.
```

---

## 17. Cross-Case Pattern Analysis (Post-Hoc)

```
CROSS_CASE_PATTERN_ANALYSIS:

  After A/B Pilot completion, analyze patterns:

  PATTERN SEARCH:
    - Cases where E1 reduced burden (improvement pattern)
    - Cases where E1 did NOT reduce burden (no-improvement pattern)
    - Cases where E1 caused UNCERTAIN→definitive (resolution pattern)
    - Cases where E1 still has UNCERTAIN with SUFFICIENT (boundary pattern)

  These patterns are IDENTIFIED post-hoc, NOT pre-registered.
  They generate hypotheses for future research.
  They do NOT modify the current design or Pack.

  NO new semantic patterns will be created.
  Only Evidence Organization patterns (Collection/Presentation/Organization).
```

---

## 18. Implementation Requirements (For Experiment Execution)

```
IMPLEMENTATION_REQUIRED (if user authorizes HUMAN_VALIDATION):

  1. Render E0 Pack for Arm A cases:
     - Use reconstructed E0 data (/tmp/e0_reconstructed.json)
     - Generate E0 version of Pack display
     - E0 Pack fields: text, extent_bbox (may be None), spatial_distance,
       vertical_ordering, context_text (may be empty), NO evidence_state
     
  2. Render E1 Pack for Arm B cases:
     - Use current E1 data (candidates_internal.json)
     - E1 Pack fields: text, extent_bbox, spatial_distance,
       vertical_ordering, context_text, evidence_state
     
  3. UI Requirements:
     - Display Pack WITHOUT version labels (E0/E1/A/B/OLD/NEW)
     - Display page image with extent overlay (if extent exists)
     - Display Target Text, Drawing Extent, Spatial Relation, Context
     - For E1 cases: display evidence_state message
     - For E0 cases: display old binary message (no evidence_state)
     - Collect M1-M4, M6 (NOT M5)
     - Random presentation order (seed=999, pre-registered)
     - NO display of: GT, case_type, E0 judgment, algorithm output
     
  4. Session Recording:
     - Save to NEW session file (NOT human_session_1.json)
     - Record: case_id, arm, Pack version, M1-M4, M6, timestamp
     - Do NOT modify human_session_1.json
     
  5. Pre-Experiment Checks:
     - Verify frozen baseline (sha256)
     - Verify E0/E1 case alignment
     - Verify no semantic leakage
     - Verify stop conditions not triggered

  NOTE:
    These requirements are for FUTURE execution.
    They are NOT executed in this Design Gate.
    HUMAN_VALIDATION_AUTHORIZED = FALSE until user authorizes.
```

---

## 19. Final Gate

```
DESIGN_READY

  The design is complete:
    ✓ Research question defined
    ✓ E0/E1 defined with recovery status
    ✓ Sampling frame (79 cases, 5 strata)
    ✓ Sample size (24, 12 per arm)
    ✓ Stratified randomization (seeded, pre-registered)
    ✓ A/B allocation (parallel split, carryover controlled)
    ✓ Blinding (PARTIAL, justified)
    ✓ Human task (minimal semantic validator)
    ✓ Metrics (M1-M6, M5=NOT_AVAILABLE)
    ✓ Burden levels (Level 0-4, unchanged)
    ✓ Evidence sufficiency definition
    ✓ Semantic boundary rule
    ✓ Stop rule (7 conditions)
    ✓ Pre-registration (12 parameters frozen)
    ✓ Statistical requirements (pilot, descriptive only)
    ✓ Burden measurement boundary
    ✓ Negative control audit design
    ✓ Hypotheses (5, not pre-determined)
    ✓ Cross-case pattern analysis plan
    ✓ Implementation requirements (for future execution)

EXPERIMENT_READY = TRUE
  (design is complete and executable)

HUMAN_VALIDATION_AUTHORIZED = FALSE
  (authorization must come from user)

NO BLOCKERS identified.
```

---

## 20. Governance

```
IMPLEMENTATION_AUTHORIZED = FALSE (this task is DESIGN ONLY)
EXPERIMENT_AUTHORIZED = FALSE
HUMAN_VALIDATION_AUTHORIZED = FALSE
HUMAN_FEEDBACK = NOT_AUTHORIZED
L3 = NOT_AUTHORIZED
CAPABILITY = NOT_AUTHORIZED
RUNTIME = NOT_AUTHORIZED
RUNTIME_AUTHORITY = ZERO
PRODUCTION = FALSE

FROZEN_BASELINE = INTACT
FROZEN_BASELINE_DRIFT = 0
  P1: 74d23ec784d65782 (UNCHANGED)
  TLD: 022f5c21e872ad9e (UNCHANGED)
  GT: 7349963d0d23b5ef (UNCHANGED)
  layout_analyzer: 8f69f0d206b3e565 (UNCHANGED)
  DGF: f25a5ff41afa1bec (UNCHANGED)
  DEF: cba9e583517f8967 (UNCHANGED)

CODE = UNCHANGED (generate_data.py, app.js NOT modified in this task)
EVIDENCE_PACK = UNCHANGED (E0 and E1 NOT modified)
M_A_ALGORITHM = UNCHANGED
HUMAN_DATA = UNCHANGED (human_session_1.json NOT modified)
P1–P6 = UNCHANGED
P7.1 = UNCHANGED
DGF = UNCHANGED
DEF = UNCHANGED
TLD = UNCHANGED

PR1 SAME_Y = ±5pt (PRE_REGISTERED, FROZEN)
PR2 60pt = Candidate Generation Only (PRE_REGISTERED, FROZEN)
PR3 Evidence State = 3-State (PRE_REGISTERED, FROZEN)

STOP = TRUE
```

---

## 21. Core Principle Adherence

- ✅ Design verifies "Evidence Pack reduces Human reconstruction burden"
- ✅ Does NOT prove "new Pack is smarter/more accurate"
- ✅ Human validates, does NOT reconstruct
- ✅ Evidence Pack organizes Evidence, does NOT provide Judgment
- ✅ No semantic labels, scores, confidence, recommendations
- ✅ No accuracy optimization
- ✅ No LLM, embedding, classifier
- ✅ No Human Feedback, L3, Capability, Runtime
- ✅ Frozen baseline intact (drift=0)
- ✅ Pre-registration complete (12 parameters frozen)
- ✅ Stop rule defined (7 conditions)
- ✅ Blinding status honest (PARTIAL, justified)
- ✅ Statistical claims bounded (pilot, descriptive only)
- ✅ Burden measurement boundary respected (no cognitive load claims)
- ✅ No Human Validation executed
- ✅ No code/data modified

`STOP = TRUE`.
