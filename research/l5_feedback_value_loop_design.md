# Human Feedback Value Loop / Feedback Reusability Design

## READ-ONLY Design Audit — No Implementation

**Date**: 2026-09-12
**Scope**: Feedback lifecycle design based on Human Pilot P01 + L5.0–L5.10 audits
**Authority**: L5 Human Validation
**Governance**: READ_ONLY=TRUE, DESIGN_ONLY=TRUE, all modifications=0, FROZEN_BASELINE=INTACT

---

## 1. Executive Conclusion

**当前 DICE 是否已经具备 Human Feedback → Reuse → Iteration 的基础？**

**部分具备。** DICE 已具备反馈捕获（ValidationRecord）、证据溯源（frozen P1–P7 + TLD + SCE + RSC）、结构分组（Aggregation）、证据压缩（Compression）。但**反馈信号提取**（从自由文本中提取可复用信号）和**反馈复用机制**（将验证后的信号应用到未来案例）完全缺失。

**最大缺口**：FEEDBACK SIGNAL EXTRACTION — 人类语音反馈中包含可识别的可复用信号（"表格中的内容"、"不同列"、"句子边界"），但系统没有任何机制将这些信号从自由文本中提取、结构化、链接到证据、检测复发、或验证为可复用知识。

**最终建议**：DESIGN READY WITH EXPERIMENT BLOCKER

设计是完整的，概念边界是清晰的，但实现被以下实验条件阻塞：n>5 参与者、跨参与者信号复发验证、至少 1 次复用演示、自动化偏见测试。

---

## 2. Current-State Map

```
Human Review → Feedback → Reuse → Improvement
```

| Stage | Status | Evidence |
|---|---|---|
| Human Review | **IMPLEMENTED** | Pilot UI, 27 judgments, A/B/C workflows |
| Raw Feedback Capture | **IMPLEMENTED** | Recording Schema L5.7_v1, auto-save server |
| Evidence Linkage | **PARTIAL** | case_id→evidence link exists; feedback_text→evidence link missing |
| Feedback Signal Extraction | **MISSING** | Voice transcripts contain signals but not extracted |
| Signal Recurrence Detection | **MISSING** | No mechanism to find recurring signals across feedbacks |
| Reusable Candidate Construction | **MISSING** | No candidate generation from feedback signals |
| Human Validation of Candidates | **MISSING** | No validation workflow for extracted signals |
| Reuse Application | **MISSING** | No mechanism to apply validated signals to new cases |
| Reuse Outcome Measurement | **MISSING** | No measurement of effort reduction or quality impact |
| Feedback Recurrence / Correction | **MISSING** | No longitudinal tracking |

**Summary**: 2 IMPLEMENTED, 1 PARTIAL, 7 MISSING out of 10 stages.

---

## 3. Feedback Taxonomy

### What is Human Feedback in DICE?

Not all Human output is "Feedback." DICE must distinguish:

| Type | Description | Example from P01 | Reusable? |
|---|---|---|---|
| **Human Decision** | KEEP_SEPARATE / MERGE / UNKNOWN | A|IS11-AMB-034 → KEEP_SEPARATE | One-off (case-specific) |
| **Human Correction** | Disagreement with System candidate | (none in P01 — System≠GT=0) | High value (if occurs) |
| **Human Explanation** | Why this decision was made | "表格中同一行的不同列数据" | Potentially reusable |
| **Human Boundary Judgment** | "不确定" when evidence is insufficient | (none in P01 — 0 UNKNOWN) | Boundary signal |
| **Human Uncertainty** | UNKNOWN selection | (none in P01) | Negative evidence |
| **Human Voice Feedback** | Free-text/voice reasoning | 4 detailed transcripts | Contains reusable signals |
| **Human Evidence Relevance Feedback** | "which evidence helped" | (implicit in voice feedback) | Design feedback |
| **Human Semantic Interpretation** | "认可同一内容单元" | AMB-414/422 MERGE | Semantic (Human authority) |
| **One-off Case Judgment** | Decision without explanation | 21 A-phase fast judgments | Not reusable alone |

### Minimum Reusable Feedback Unit

A single KEEP_SEPARATE decision is **not** a reusable unit. It is a one-off judgment.

A **Potentially Reusable Signal** is a structured observation that links Human reasoning to Evidence:

```
Example reusable signal (NOT a rule, a CANDIDATE):
  Signal type: TABLE_DIFFERENT_COLUMNS
  Evidence basis: TLD is_in_table=True, different_cell=True
  Human observation: "表格中同一行的不同列数据"
  Human decision: KEEP_SEPARATE
  Source: P01/B|grp|885e943771cd
  Status: CANDIDATE (not validated, not rule)
```

This is NOT:
- A rule ("if is_in_table=True then KEEP_SEPARATE")
- A classifier
- An automatic decision

It IS:
- A candidate signal that MIGHT recur
- Linked to specific frozen evidence
- Traceable to a specific Human feedback
- Awaiting validation

---

## 4. Feedback Lifecycle (Minimal)

Each state must justify its existence:

### State 1: Raw Human Feedback
- **Why needed**: Human output must be captured
- **Solves**: Loss of Human judgment
- **Delete consequence**: No record of Human input
- **Independent object?**: NO — expressed by ValidationRecord (existing)
- **Status**: IMPLEMENTED

### State 2: Evidence-Linked Feedback
- **Why needed**: Feedback must connect to evidence it was based on
- **Solves**: Feedback becomes孤立 labels without evidence context
- **Delete consequence**: Cannot trace WHY Human decided
- **Independent object?**: NO — extension of ValidationRecord with evidence refs
- **Status**: PARTIAL (case_id link exists, evidence-field link missing)

### State 3: Interpretable Feedback Signal
- **Why needed**: Free text is not machine-processable; signals are
- **Solves**: "Stored but not searchable" problem
- **Delete consequence**: Feedback stays as unstructured text, cannot detect recurrence
- **Independent object?**: POTENTIALLY — a signal is a new concept (evidence-linked, structured)
- **BUT**: at n=1, can be expressed as manual annotation, not a system object
- **Status**: MISSING (concept identified, not implemented)

### State 4: Reusable Candidate
- **Why needed**: Recurring signals across multiple feedbacks indicate potential reusability
- **Solves**: "Feedback used once and forgotten" problem
- **Delete consequence**: Each feedback is processed independently, no accumulation
- **Independent object?**: POTENTIALLY — similar to Compression's claim_candidate but derived from Human feedback
- **BUT**: requires State 3 (signal extraction) to exist first
- **Status**: MISSING

### State 5: Human-Validated Reusable Signal
- **Why needed**: Candidates must be validated before reuse (authority boundary)
- **Solves**: Automation bias — unvalidated signals could mislead
- **Delete consequence**: Candidates used without validation → System authority violation
- **Independent object?**: NO — a validation status on the candidate
- **Status**: MISSING

### State 6: Reuse + Outcome
- **Why needed**: Must measure if reuse actually helps
- **Solves**: "Cannot prove learning" problem
- **Delete consequence**: Cannot distinguish learning from storage
- **Independent object?**: NO — outcome measurement on existing review records
- **Status**: MISSING

### States NOT Added (justified exclusion)

- **"Feedback Rule"**: NOT added — rules imply automatic application, violating authority boundary
- **"Feedback Pattern"**: NOT added — patterns require statistical significance (n>10), premature
- **"Learning State"**: NOT added — learning is an outcome measurement, not a state
- **"Feedback Cache"**: NOT added — caching is an implementation detail, not a design concept

---

## 5. Feedback Value Chain

```
Human Effort (time, cognitive load)
    ↓
Feedback (decision + voice/text explanation)
    ↓ input: Human judgment + reasoning
    ↓ output: ValidationRecord with feedback_text
    ↓ authority: Human (sole semantic authority)
    ↓ provenance: participant_id + case_id + timestamp
    ↓ failure mode: feedback not captured, or captured but not linked to evidence
    ↓ validation requirement: recording schema completeness
    ↓
Evidence Linkage (feedback → evidence fields)
    ↓ input: ValidationRecord + frozen evidence
    ↓ output: feedback with explicit evidence references
    ↓ authority: System (deterministic linkage)
    ↓ provenance: evidence field provenance (frozen TLD/SCE/RSC)
    ↓ failure mode: evidence not available, or feedback doesn't reference available evidence
    ↓ validation requirement: evidence-feedback traceability
    ↓
Signal Extraction (free text → structured signal)
    ↓ input: evidence-linked feedback
    ↓ output: candidate signal {type, evidence_basis, human_source, status=candidate}
    ↓ authority: System (extraction) + Human (signal validation)
    ↓ provenance: feedback source + evidence source
    ↓ failure mode: signal extraction error (false positive/negative)
    ↓ validation requirement: Human reviews extracted signals
    ↓
Signal Recurrence Detection (multiple feedbacks → recurring signal)
    ↓ input: multiple candidate signals
    ↓ output: recurring signal candidate {signal_type, occurrence_count, evidence_pattern}
    ↓ authority: System (deterministic aggregation)
    ↓ provenance: all feedback sources + all evidence sources
    ↓ failure mode: spurious recurrence (coincidence, not pattern)
    ↓ validation requirement: cross-participant verification
    ↓
Human Validation (candidate → validated reusable knowledge)
    ↓ input: recurring signal candidate
    ↓ output: validated signal {status=validated, scope, limitations}
    ↓ authority: Human (sole validation authority)
    ↓ provenance: validation record (who, when, what evidence)
    ↓ failure mode: Human validates incorrectly, or validates too broadly
    ↓ validation requirement: scope specification + limitation acknowledgment
    ↓
Reuse (validated signal → future cases)
    ↓ input: validated signal + new case evidence
    ↓ output: signal match {case_id, signal_id, match_quality}
    ↓ authority: System (deterministic matching) + Human (final judgment)
    ↓ provenance: validated signal provenance + new case evidence
    ↓ failure mode: signal applied outside scope, or evidence mismatch
    ↓ validation requirement: Human reviews signal match before judgment
    ↓
Future Outcome (reuse impact measurement)
    ↓ input: signal match + Human judgment on new case
    ↓ output: outcome {effort_delta, quality_delta, error_recurrence}
    ↓ authority: System (measurement) + Human (quality assessment)
    ↓ provenance: full chain traceable
    ↓ failure mode: measurement incomplete, or confounding variables
    ↓ validation requirement: baseline comparison
    ↓
Human Effort Reduction (loop closure)
    ↓ measured as: review_count_delta, review_time_delta, expansion_count_delta
    ↓ MUST be accompanied by: quality_maintained_or_improved
    ↓ MUST NOT be claimed without: baseline comparison + quality measurement
```

---

## 6. Reusability Boundary

### System CAN (automatically, deterministic):

| Operation | Existing Mechanism | New Needed? |
|---|---|---|
| Group cases by structural signature | Aggregation (frozen) | NO |
| Compress groups into summaries | Compression (frozen) | NO |
| Detect structural similarity between cases | Aggregation (structural_signature) | NO |
| Extract evidence fields per case | Sampling frame + replay | NO |
| Match new case to existing group | Aggregation signature matching | NO (concept exists) |
| Count feedback occurrences per group | (not implemented but trivial) | Process, not module |
| Present evidence cue to Human | L5.10 translation table | Process, not module |

### Human MUST (semantic authority):

| Operation | Why Human? |
|---|---|
| Semantic interpretation | System has no semantic capability |
| Boundary adequacy judgment | System cannot judge if evidence is sufficient |
| Scope acceptance for reusable signal | System cannot determine generalization scope |
| Final validation of reusable knowledge | Authority boundary: System authority=0 at L5 |
| Override of System proposal | Automation bias prevention |
| UNKNOWN selection when uncertain | System cannot determine Human uncertainty |

### Boundary Principle

```
System may propose reusable knowledge;
only Human validation can grant reusable semantic authority.
```

System does aggregation, extraction, matching, presentation.
Human does interpretation, validation, scope-setting, override.

---

## 7. Learning Definition

### When can we say Learning = TRUE?

**Learning = TRUE requires ALL of the following:**

1. **Feedback accumulated**: Multiple Human feedbacks exist for similar evidence patterns
2. **Signal extracted**: Reusable signals identified from feedbacks
3. **Signal validated**: Human validated the signal as reusable
4. **Signal applied**: Validated signal applied to NEW cases (not the original cases)
5. **Effort reduced**: Human review count or time DECREASED for new cases
6. **Quality maintained**: Decision accuracy did NOT decrease (false accept/reject not worse)
7. **Error recurrence reduced**: Same error type appears less frequently in new cases

### What is NOT Learning:

| State | What it is | What it is NOT |
|---|---|---|
| Feedback stored in database | Storage | NOT Learning |
| Multiple feedbacks retrieved by keyword | Retrieval | NOT Learning |
| Similar feedbacks grouped together | Aggregation | NOT Learning |
| Recurring signal identified | Candidate Discovery | NOT Learning (yet) |
| Signal validated by Human | Validation | NOT Learning (yet) |
| Validated signal shown for new case | Reuse Attempt | NOT Learning (yet) |
| **New case reviewed faster with same accuracy** | **Demonstrated Reuse** | **Learning = TRUE** |

### Critical Distinction

```
Storage ≠ Learning
Aggregation ≠ Learning
Retrieval ≠ Learning
Candidate Discovery ≠ Learning
Validation ≠ Learning
Reuse ≠ Learning
REUSE WITH MEASURED EFFORT REDUCTION + QUALITY MAINTENANCE = Learning
```

---

## 8. Feedback Maturity Model

| Level | Description | DICE Current Status |
|---|---|---|
| L0 | Human-only decision (no system support) | ✅ Passed (System provides evidence) |
| L1 | Feedback captured | ✅ **CURRENT** (ValidationRecord, auto-save) |
| L2 | Feedback evidence-linked | ⚠️ PARTIAL (case_id link, not evidence-field link) |
| L3 | Feedback aggregated / reusable candidate discovered | ❌ MISSING |
| L4 | Human validates reusable signal | ❌ MISSING |
| L5 | Validated knowledge reused across future cases | ❌ MISSING |
| L6 | Reuse reduces Human effort while maintaining quality | ❌ MISSING |
| L7 | Continuous closed-loop improvement | ❌ MISSING (future research) |

**DICE is at L1 (Feedback Captured), approaching L2 (Evidence-Linked).**

L2 requires: propagating TLD/text evidence into feedback records (design-ready per L5.10).
L3 requires: signal extraction mechanism (design identified, not implemented).
L4–L7 require: multi-participant experiments + longitudinal data.

---

## 9. Evaluation Metrics

All metrics are CONCEPTUAL unless marked VALIDATED.

| Metric | Type | Definition | Current Data |
|---|---|---|---|
| Human Effort Reduction | CONCEPTUAL | (baseline_review_time - reuse_review_time) / baseline_review_time | No baseline comparison data |
| Feedback Reuse Ratio | CONCEPTUAL | cases_covered_by_reuse / total_new_cases | No reuse mechanism |
| Generalization Scope | CONCEPTUAL | {same_doc, same_doc_family, cross_doc, cross_domain} | No reuse data |
| Decision Quality | CONCEPTUAL | accuracy_maintained OR improved after reuse | No reuse data |
| Error Recurrence Rate | CONCEPTUAL | same_error_type_count_batch2 / batch2_total | No batch 2 data |
| UNKNOWN Preservation | CONCEPTUAL | unknown_count not suppressed by reuse | No reuse data |
| Automation Bias Index | CONCEPTUAL | blind_accept_rate / total_reuse_matches | No reuse data, System≠GT=0 |
| Provenance Completeness | CONCEPTUAL | feedback→evidence→signal→validation chain traceable | Partially measurable (chain design exists) |
| Signal Extraction Precision | CONCEPTUAL | correct_signals / extracted_signals | No extraction mechanism |
| Signal Recurrence Rate | CONCEPTUAL | recurring_signals / total_extracted_signals | No extraction mechanism |

**All metrics are CONCEPTUAL. None are VALIDATED.** No experimental data exists to validate any metric. This is expected at L1 maturity.

---

## 10. Minimal Future Experiment (Design Only — NOT Implemented)

### Experiment Design: Feedback Reuse Validation Study

**Goal**: Prove that Human Feedback → Reuse → Effort Reduction + Quality Maintenance

**Design**:

```
Phase 1: Baseline (no reuse)
  - N=10 participants
  - 50 cases (diverse: tables, captions, prose, mixed)
  - Measure: review_time, review_count, accuracy, UNKNOWN, expansion_count
  - Capture: all feedback (decision + voice/text)

Phase 2: Signal Extraction (offline)
  - Extract signals from Phase 1 feedbacks
  - Link signals to evidence
  - Detect recurring signals
  - Present candidates to independent validators

Phase 3: Signal Validation
  - N=3 validators (different from Phase 1)
  - Validate candidate signals
  - Specify scope and limitations
  - Produce: validated reusable signals

Phase 4: Treatment (with reuse)
  - N=10 participants (different from Phase 1)
  - Same 50 cases + 50 NEW cases
  - For cases matching validated signals: show evidence cue + validated signal as context
  - For non-matching cases: show current evidence only
  - Measure: same metrics as Phase 1

Phase 5: Comparison
  - Compare Phase 1 (baseline) vs Phase 4 (treatment)
  - Metrics: review_time_delta, accuracy_delta, UNKNOWN_delta, error_recurrence
  - Learning = TRUE if: effort ↓ AND quality ↔/↑ AND error_recurrence ↓
```

**Critical Controls**:
- System≠GT test cases (at least 10): to test automation bias
- Conflict cases (at least 5): to test signal override behavior
- Cross-document cases (at least 20): to test generalization
- Signal shown as CANDIDATE (not conclusion): to preserve Human authority

**Prerequisites**:
- n>5 Phase 1 participants for signal extraction
- Diverse case corpus (not just tables)
- Evidence Cue implementation (L5.10 design-ready)
- Feedback signal extraction process (design identified)

---

## 11. Anti-Overdesign Gate

| Gate | Question | Answer | Justification |
|---|---|---|---|
| G1 | New Feedback object? | **NO** | ValidationRecord + feedback_text sufficient at L1 |
| G2 | New Signal object? | **NO** | Concept identified but n=1 insufficient; express as annotation |
| G3 | Pattern? | **NO** | Requires n>10 + cross-participant validation; premature |
| G4 | Learning Engine? | **NO** | End goal, not starting point; requires validated signals first |
| G5 | ML/LLM training? | **NO** | n=1, 21 cases far too small; authority boundary prohibits |
| G6 | What can existing objects express? | 7/12 concepts | See analysis below |
| G7 | Max gap without new modules? | **Signal Extraction** | Gap between stored feedback and reusable signal |
| G8 | Evidence for next level? | n>5 + recurrence + reuse demo + bias test | See prerequisites |

### G6: What Existing Objects Already Express

| Concept | Expressed By | Status |
|---|---|---|
| Human decided X for case Y | ValidationRecord | ✅ |
| Case Y has structural evidence Z | Sampling frame + replay | ✅ |
| Cases Y1-Y6 are structurally similar | Aggregation | ✅ |
| Group has N consistent, M unknown | Compression | ✅ |
| System proposes candidate C for group G | Compression (claim_candidate) | ✅ |
| Evidence cue E is safe to show | L5.10 audit | ✅ |
| Human feedback text exists | ValidationRecord (feedback_text) | ✅ |
| Human used evidence E to decide D | — | ❌ MISSING |
| Feedback signal S recurs across N cases | — | ❌ MISSING |
| Signal S validated as reusable | — | ❌ MISSING |
| Validated signal S applied to new case C | — | ❌ MISSING |
| Reuse of S reduced effort by X% | — | ❌ MISSING |

### G7: Maximum Gap Without New Modules

**FEEDBACK SIGNAL EXTRACTION** is the single largest gap.

Voice transcripts contain identifiable signals:
- "表格中的内容" → TABLE_CONTEXT
- "不同列" → DIFFERENT_COLUMNS
- "前一句话后半" → SENTENCE_BOUNDARY
- "认可同一内容单元" → CONTENT_CONTINUITY

But no mechanism exists to:
1. Extract these from free text
2. Link them to evidence fields
3. Detect recurrence
4. Present as candidates

**This gap does NOT require a new module.** It requires a PROCESS:
- Manual annotation (Human reads feedback, tags signals) — possible now
- Deterministic keyword match — trivial to implement
- LLM-assisted extraction with Human validation — future candidate

All three are processes, not modules. No new Primitive/Contract/Architecture needed.

### G8: Evidence Required for Next Level

To justify implementation, the following evidence must appear:

1. **Signal Identifiability** (partially met): L5.10 + P01 show signals are identifiable ✅
2. **Signal Recurrence** (not met): Need same signal from multiple participants
3. **Signal-Evidence Linkage** (partially met): L5.10 shows mapping exists ✅
4. **Reuse Feasibility** (not met): Need 1 demonstration of signal applied to new case
5. **Automation Bias Resistance** (not met): Need System≠GT test cases

**Bottom Line**: Need n>5 participants + cross-participant signal recurrence + 1 reuse demonstration + automation bias test.

---

## 12. Final Recommendation

### DESIGN READY WITH EXPERIMENT BLOCKER

**The design is complete:**
- Feedback taxonomy is defined (9 types, reusable vs one-off distinguished)
- Feedback lifecycle is minimal (6 states, each justified, no over-design)
- Feedback value chain is complete (input/output/authority/provenance/failure per stage)
- Reusability boundary is clear (System aggregates, Human validates)
- Learning definition is strict (7 conditions, all required)
- Maturity model places DICE at L1 (feedback captured)
- Anti-overdesign gate passes (G1–G5 all NO, G6–G8 analyzed)

**The implementation is blocked by:**
1. n=1 participant — cannot verify signal recurrence
2. 4 detailed feedbacks — insufficient for pattern detection
3. System≠GT=0 — cannot test automation bias
4. conflict=0 — cannot test signal override
5. No reuse mechanism — cannot demonstrate effort reduction
6. No baseline comparison — cannot measure improvement

**What does NOT block implementation:**
- Evidence Cue design (L5.10 PASS — safe translation exists)
- Evidence availability (frozen TLD/SCE/RSC all available)
- Aggregation/Compression (frozen, working)
- Authority boundary (clearly defined)
- Provenance (fully traceable)

### Next Steps (Require Explicit Authorization)

1. **Not now**: Implement signal extraction process
2. **Not now**: Run Phase 1 baseline experiment (n=10)
3. **Not now**: Implement evidence cue in UI
4. **Future**: After Phase 1 data → extract signals → validate → Phase 4 treatment
5. **Future**: After Phase 4 → measure Learning=TRUE

All steps require separate authorization. No autonomous implementation.

---

## 13. Governance

```
READ_ONLY = TRUE
DESIGN_ONLY = TRUE

CODE_MODIFICATION = 0
UI_MODIFICATION = 0
GT_MODIFICATION = 0
TLD_MODIFICATION = 0
ATOMIC_MODIFICATION = 0
IS11_DECISION_MODIFICATION = 0
AGGREGATION_MODIFICATION = 0
COMPRESSION_MODIFICATION = 0
L5.5_MODIFICATION = 0

NEW_PRIMITIVE = 0
NEW_CONTRACT = 0
NEW_ARCHITECTURE = 0
NEW_PATTERN_ENGINE = 0
PATTERN_REGISTRY = 0
PATTERN_MINER = 0
CLASSIFIER = 0
FEEDBACK_ENGINE = 0
LEARNING_ENGINE = 0
AUTO_TRAINING_PIPELINE = 0
AUTO_RULE_GENERATOR = 0
SEMANTIC_CLASSIFIER = 0
DECISION_POLICY = 0
RUNTIME_POLICY = 0
AUTOMATIC_CAPABILITY_REGISTRATION = 0

FUTURE_IMPLEMENTATION_CANDIDATES:
  - Feedback Signal Extraction Process (process, not module)
  - Evidence Cue UI Integration (after L5.10 authorization)
  - Reuse Matching Mechanism (after validated signals exist)
  - Outcome Measurement Framework (after reuse occurs)

PRODUCTION = FALSE
FROZEN_BASELINE = INTACT
HUMAN_DATA = REAL_PILOT_ONLY
NO_SIMULATION = TRUE
IMPLEMENTATION_AUTHORIZED = FALSE
STOP = TRUE
```

### Pilot Limitations Preserved

```
Pilot = exploratory engineering evidence
n = 1
21 A cases
MERGE = 2
Conflict = 0
System ≠ GT = 0
4 detailed voice feedbacks
```

### Evidence Classification

- This design = **B-class** (engineering design based on single pilot)
- Feedback signal identifiability = **B-class** (derived from P01 analysis)
- Learning definition = **C-class** (conceptual, not empirically validated)
- Maturity model positioning = **B-class** (based on implemented vs missing analysis)
- Reuse feasibility = **C-class** (hypothesis, requires experimental validation)
