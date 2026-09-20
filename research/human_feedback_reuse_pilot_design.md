# DICE Human Feedback Reuse Pilot — 最小闭环实验设计与准备

**Date**: 2026-09-12
**Mode**: READ-ONLY / EXPERIMENT DESIGN + PILOT PREPARATION
**DESIGN_ONLY**: TRUE
**EXPERIMENT_AUTHORIZATION**: NOT_GRANTED

---

## 1. Executive Verdict

> **CONDITIONAL — 当前存在一个足以进入 Human Feedback Reuse Pilot 的 Reusable Signal Candidate (CS1)，但尚未经过 Human Validation，尚未应用于 Future Cases，尚未测量 Human Review Reduction。**

CS1 (DIFFERENT_TABLE_COLUMNS) 满足进入 Pilot 的最低条件：
- ✅ 有 Evidence 支撑 (TLD is_in_table + different_cell)
- ✅ 有 Human Feedback (4 条自由文本 + 70 条 reviewer rationale)
- ✅ 有重复案例 (31 个 Past Cases，GT 全为 KEEP_SEPARATE)
- ✅ 跨文档 (3 个文档)
- ✅ 有 Future Cases (20 个未裁决案例，TLD 证据匹配)
- ✅ 不需要新增 Observation
- ✅ 不需要修改 Frozen Baseline
- ✅ Human 可以低成本验证

但存在限制：
- ⚠️ Future Cases 与 Past Cases 在相同页面 (page-level leakage risk)
- ⚠️ 无 novel document (med_001 无 TLD 匹配案例)
- ⚠️ 无 CONFLICT 案例 (signal boundary 未经验证)
- ⚠️ 无 UNKNOWN 案例 (TLD 从不产生 is_in_table=True + different_cell=False)
- ⚠️ n=1 参与者 (跨参与者稳定性未验证)

---

## 2. Selected Signal

### CS1: DIFFERENT_TABLE_COLUMNS

| 属性 | 值 |
|---|---|
| Signal ID | CS1-DIFFERENT_TABLE_COLUMNS |
| Evidence Signature | TLD is_in_table=True AND different_cell=True |
| Evidence Provenance | chunker/table_line_detector.py (frozen, SHA256 022f5c21) |
| Human Feedback | "同一个表格中的不同列的名称", "同一行的不同列数据" |
| Reviewer Rationales | 70/90 提及 "table columns" 或 "table cells" |
| Past Cases | 31 (全部 GT=KEEP_SEPARATE) |
| Past Documents | 3 (resnet, efficientnet, cs_001) |
| Past Pages | 14 |
| Validation Status | CANDIDATE (未验证) |

---

## 3. Why This Signal

### 为什么选择 CS1 而非 CS2/CS3/CS4

| 标准 | CS1 | CS2 (SENTENCE_BOUNDARY) | CS3 (FIGURE_CAPTION) | CS4 (SECTION_HEADER) |
|---|---|---|---|---|
| Evidence-backed | ✅ TLD | ✅ P1 text | ✅ P1 text | ✅ P1 text |
| Cases | 31 | 20 | 12 | 2 |
| Documents | 3 | 4 | 2 | 1 |
| Future Cases | 109 (selected 20) | ? | ? | 0 |
| Boundary expressible | ⚠️ PARTIAL | ⚠️ binary | ⚠️ FIG ambiguity | ❌ too few |
| Human feedback | ✅ explicit | ✅ explicit | ✅ explicit | ❌ none |
| Cross-document | ✅ 3 docs | ✅ 4 docs | ⚠️ 2 docs | ❌ 1 doc |
| Structural stability | ✅ HIGH (table structure) | ⚠️ MEDIUM (punctuation) | ⚠️ MEDIUM (FIG marker) | ❌ LOW |

**CS1 被选择的核心原因**：

1. **Evidence 是结构性的**（TLD 检测的表格位置），不是文本模式性的。结构证据比文本模式更稳定、更可重复。
2. **31 个 Past Cases 全部 GT=KEEP_SEPARATE**，证据与 GT 高度一致。
3. **109 个 Future Cases 有匹配的 TLD 证据**，可以实际测试复用。
4. **Human Feedback 明确提及**"不同表格列"，反馈与证据直接关联。
5. **跨文档**（3 个文档），虽然不是 novel document，但有多文档覆盖。

**其他候选暂不选择的原因**：
- CS2：虽然 100% evidence coverage，但 period+capital 是文本模式，结构稳定性低于 TLD。且 Future Cases 数量未验证。
- CS3：只有 2 个文档，FIG marker 有歧义（caption vs in-text reference），有明确 counter-evidence (AMB-063)。
- CS4：只有 2 个案例、1 个文档，不足以形成可验证 signal。

---

## 4. Signal Boundary

### 四层严格区分

#### A. Evidence (Machine-computed, frozen)

```
cue1 = TLD is_in_table (boolean, from frozen table_line_detector.py)
cue2 = TLD different_cell (boolean, from frozen table_line_detector.py)
```

#### B. Human Feedback (Human-expressed, stored)

```
"同一个表格中的不同列的名称"
"同一行的不同列数据"
"表格中的内容应该分开"
"表格内容没有语义完整性"
```

#### C. Reusable Signal Candidate (Experimental, not DICE schema)

```
Signal ID: CS1-DIFFERENT_TABLE_COLUMNS
Evidence Signature: is_in_table=True AND different_cell=True
Human Interpretation: "Text A and Text B occupy different structural positions within a detected multi-column table"
```

**禁止**：将此 Signal 转换为 `IF is_in_table=True AND different_cell=True THEN KEEP_SEPARATE`

#### D. Validated Reusable Signal (NOT YET EXISTING)

只有 Human 验证后才能产生。当前状态 = CANDIDATE。

### Boundary Definition

| Boundary | Condition | Evidence Count | Action |
|---|---|---|---|
| **SUPPORTED** | is_in_table=True AND different_cell=True | 31 past cases | Signal applicable — Human may skip repeated reconstruction |
| **UNSUPPORTED** | is_in_table=False | 32 cases | Signal does not apply — Human reviews from scratch |
| **UNKNOWN** | is_in_table=True AND different_cell=False | 0 cases | Cannot determine — HUMAN_REVIEW_REQUIRED |
| **OUT_OF_SCOPE** | Non-table families (PROSE, FIGURE_CAPTION, AXIS) | N/A | SIGNAL_NOT_APPLIED |
| **CONFLICT** | different_cell=True BUT Human adjudicates MERGE | 0 cases | EVIDENCE_CONFLICT + NO_AUTO_REUSE + HUMAN_REVIEW |

### CONFLICT 处理协议

```
IF different_cell=True AND Human GT=MERGE:
    → EVIDENCE_CONFLICT
    → NO_AUTO_REUSE
    → HUMAN_REVIEW
    → Signal does NOT win
    → Evidence does NOT win
    → Human judgment wins
```

**禁止**：
- Signal wins (自动覆盖 Human)
- Fallback (自动选择默认)
- Machine overrides Evidence

---

## 5. Past → Signal

### Past Cases (31)

| Source | Count | GT | Notes |
|---|---|---|---|
| GT-45 (frozen) | 16 | All KEEP_SEPARATE | Has TLD Cue from frozen experiment |
| GT-48 (session) | 15 | All KEEP_SEPARATE | TLD computed this session |
| Total | 31 | 31 KEEP_SEPARATE, 0 MERGE | 100% consistency |

### Human Feedback → Signal Construction

```
31 Past Cases
    ↓
TLD detects: is_in_table=True + different_cell=True
    ↓
Human Feedback: "不同表格列" (70/90 reviewer rationales)
    ↓
Recurring pattern identified (manual analysis)
    ↓
Signal Candidate constructed (CS1)
    ↓
Validation Status = CANDIDATE
    ↓
(AWAITING) Human Validation
```

### Human Validation Protocol (NOT YET EXECUTED)

```
Step 1: Present 10 past CS1 cases to Human
Step 2: For each case, Human sees:
    - Text A, Text B
    - Evidence: "TLD detected both in table, different cells"
    - Question: "Does this evidence structure indicate that A and B are in different structural positions within a table?"
Step 3: Human responds: VALIDATED / REJECTED / UNCERTAIN
Step 4: If ≥8/10 VALIDATED → Signal promoted to HUMAN_VALIDATED
Step 5: If <8/10 → Signal remains CANDIDATE, pilot blocked
```

---

## 6. Signal → Future

### Future Cases (20)

| Property | Value |
|---|---|
| Count | 20 |
| GT Status | NOT_ADJUDICATED (must be adjudicated AFTER experiment for quality measurement) |
| Documents | 3 (resnet=4, efficientnet=8, cs_001=8) |
| Pages | 5 |
| Structure Families | TABLE_HEADER=6, ROW_LABEL_VALUE=7, TABLE_NUMERIC=7 |
| TLD Evidence | All have is_in_table=True + different_cell=True |
| Case Independence | VERIFIED (0 case leakage) |
| Page Independence | FALSE (all on same pages as past) |
| Document Independence | FALSE (same 3 documents) |

### Future Case Selection Criteria

```
1. NOT in past set (case_id not in any GT-45, GT-48, or experiment set)
2. TLD is_in_table=True AND different_cell=True (evidence signature matches CS1)
3. Diversity: structure families (TABLE_HEADER, ROW_LABEL_VALUE, TABLE_NUMERIC)
4. Diversity: documents (3 documents represented)
5. Selected by evidence signature ONLY — NOT by expected outcome
```

### Future Case Examples (5 of 20)

| Case ID | Doc | Page | Family | Text A | Text B |
|---|---|---|---|---|---|
| AMB-002 | resnet | 1 | TABLE_HEADER | Xiangyu Zhang | Shaoqing Ren |
| AMB-340 | efficientnet | 9 | TABLE_NUMERIC | 77.11 | 79.13 |
| AMB-434 | cs_001 | 3 | TABLE_HEADER | Models | Size |
| AMB-436 | cs_001 | 3 | ROW_LABEL_VALUE | LLaMA LLM | 700M |
| AMB-067 | resnet | 8 | TABLE_HEADER | VOC 07 test | VOC 12 test |

### Signal Applicability per Future Case

```
For each Future Case:
    → Compute TLD (already done)
    → Check: is_in_table=True AND different_cell=True?
    → If YES: Signal APPLICABLE (REUSE_SUPPORTED)
    → If NO: Signal NOT APPLICABLE (REUSE_UNSUPPORTED)
    → If is_in_table=True AND different_cell=False: REUSE_UNKNOWN
    → If evidence conflicts with future GT: REUSE_CONFLICT
```

**All 20 Future Cases**: Signal APPLICABLE (REUSE_SUPPORTED) based on evidence signature.

But: **GT unknown** — Reuse Precision cannot be pre-determined.

---

## 7. Reuse OFF / Reuse ON

### Condition A — Reuse OFF

```
Future Case
    ↓
Evidence (text, geometry, style, image)
    ↓
Human Review (from scratch)
    ↓
Decision: KEEP_SEPARATE / MERGE / UNKNOWN
```

Measures:
- `human_review_required` = 20 (all cases reviewed)
- `decision_time` per case
- `decision` per case
- `correctness` (vs future GT, adjudicated after)
- `boundary` (did Human mark UNKNOWN when appropriate?)
- `unknown_count`

### Condition B — Reuse ON

```
Future Case
    ↓
Evidence (text, geometry, style, image)
    +
Validated Reusable Signal (CS1, if HUMAN_VALIDATED)
    ↓
Evidence Compatibility Check:
    → is_in_table=True AND different_cell=True? → REUSE_SUPPORTED
    → is_in_table=False? → REUSE_UNSUPPORTED
    → is_in_table=True AND diff_cell=False? → REUSE_UNKNOWN
    ↓
If REUSE_SUPPORTED:
    → Display: "Validated Signal: evidence indicates different table positions"
    → Display: supporting evidence + scope + boundary + provenance
    → Display: NOT "the answer is KEEP_SEPARATE"
    → Human can: ACCEPT (skip detailed review) / REJECT (review from scratch) / UNKNOWN (review with signal context)
    ↓
If REUSE_UNSUPPORTED:
    → Human reviews from scratch (same as Condition A)
    ↓
If REUSE_UNKNOWN:
    → Human reviews from scratch (same as Condition A)
```

Measures:
- `human_review_required` = 20 - accepted_reuse_count
- `signal_acceptance_count`
- `signal_rejection_count`
- `signal_unknown_count`
- `decision_time` per case
- `decision` per case
- `correctness` (vs future GT)
- `boundary_quality` (UNKNOWN preservation + CONFLICT detection)
- `error_propagation` (wrong reuse count)

### Anti-Automation-Bias Safeguards

```
1. Signal shown as "validated interpretation" NOT "correct answer"
2. Human can ACCEPT, REJECT, or mark UNKNOWN
3. Signal displays: evidence + scope + boundary + provenance
4. No auto-routing, no auto-decision, no auto-execute
5. Signal runtime authority = ZERO
6. Human override always available
```

---

## 8. Metrics

### Primary Metrics

| Metric | Formula | Target |
|---|---|---|
| HRR (Human Review Reduction) | (Review_OFF - Review_ON) / Review_OFF | > 0 (any reduction) |
| Reuse Coverage | Applicable future cases / Total future cases | 20/20 = 100% (all TLD-matched) |
| Reuse Precision | Correctly reused / Total reused | ≥ 90% |
| Decision Quality (ON) | Accuracy_ON vs GT | ≥ Accuracy_OFF |
| Decision Quality (OFF) | Accuracy_OFF vs GT | baseline |
| Boundary Quality | UNKNOWN_preserved_ON ≥ UNKNOWN_preserved_OFF | TRUE |
| Error Propagation | Wrong_reuse / Total_reuse | 0 (ideal), ≤ Error_OFF |

### Secondary Metrics

| Metric | Description |
|---|---|
| Signal Acceptance Rate | accepted_reuse / REUSE_SUPPORTED cases |
| Signal Rejection Rate | rejected_reuse / REUSE_SUPPORTED cases |
| UNKNOWN Preservation | UNKNOWN_ON ≥ UNKNOWN_OFF |
| CONFLICT Detection | If any CONFLICT case appears, was it detected? |
| Review Time Reduction | avg_time_OFF - avg_time_ON |
| FRR (Feedback Reuse Ratio) | future_cases_covered / feedback_instances (research metric only) |

### Result Classification

| Result Type | Condition | Classification |
|---|---|---|
| TRUE REUSE | Signal accepted + Human skips detailed review + Quality maintained | ✅ Learning |
| EVIDENCE HELPFULNESS | Human still reviews + faster decision + Quality maintained | ⚠️ Not Learning (C2) |
| UNSAFE AUTOMATION | Signal accepted + Quality decreased OR Boundary violated | ❌ Failure |

---

## 9. Circularity / Leakage Audit

| Leakage Type | Status | Evidence |
|---|---|---|
| **Case Leakage** | ✅ NONE | 0 future case_ids in past set (verified) |
| **Document Leakage** | ⚠️ PARTIAL | Same 3 documents in past and future (no novel document) |
| **Page Leakage** | ⚠️ FULL | All 20 future cases on same pages as past cases |
| **GT Leakage** | ✅ NONE | Future cases have no GT (must be adjudicated AFTER experiment) |
| **Outcome Leakage** | ✅ NONE | Future cases selected by evidence signature only, not by expected outcome |

### Risk Assessment

```
RISK = MEDIUM
```

- **Case-level independence**: VERIFIED — different case_ids, different text pairs, different bbox positions
- **Page-level familiarity risk**: Human might recognize the table/page and accept signal without careful checking
- **Mitigation**: Cases are different text pairs; Human sees different content; signal is labeled as "interpretation" not "answer"

### Generalization Strength

```
GENERALIZATION_STRENGTH = MEDIUM
```

- Cross-document: YES (3 documents)
- Cross-page: NO (same pages)
- Novel document: NO (med_001 has 0 TLD-matched cases)
- Cross-case: YES (different case_ids, different text pairs)

**Note**: This is the maximum generalization achievable with the current corpus. med_001 is primarily prose + figure captions, which don't trigger TLD table detection. Achieving novel-document generalization would require a new corpus with table structures — which is outside this experiment's scope.

---

## 10. Automation Bias Audit

### Risk Analysis

| Risk | Likelihood | Mitigation | Residual Risk |
|---|---|---|---|
| Blind acceptance | MEDIUM | Signal labeled as "interpretation", Human can REJECT | Human might still accept due to cognitive load |
| Over-generalization | LOW | Boundary explicitly defined (SUPPORTED/UNSUPPORTED/UNKNOWN/CONFLICT) | Future cases all match SUPPORTED, so boundary not tested |
| Boundary loss | LOW | UNKNOWN/CONFLICT protocol defined | No UNKNOWN/CONFLICT cases in corpus to test |
| Page familiarity bias | MEDIUM | Cases are different text pairs | Human might recognize table structure |

### Key Safety Principle

```
Reuse Signal ≠ Final Decision Authority

Signal can only say:
    "Evidence structure has been validated as indicating different table positions"

Signal CANNOT say:
    "The answer is KEEP_SEPARATE"
    "You should merge these"
    "This is correct"
    "Trust the machine"
```

---

## 11. Current Learning Level

| Level | Description | Status | Evidence |
|---|---|---|---|
| L0 | Human-only decision | ✅ PASSED | Historical state |
| L1 | Feedback captured | ✅ CURRENT | 4 free-text + 90 rationales + 93 GT rationales stored |
| L2 | Feedback evidence-linked | ✅ ACHIEVED (this task) | CS1: 31/31 cases TLD-linked, 100% evidence coverage |
| L3 | Reusable signal candidate | ✅ ACHIEVED (this task) | CS1 signal constructed with boundary definition |
| L4 | Human-validated signal | ❌ NOT YET | Validation protocol designed, NOT EXECUTED |
| L5 | Signal applied to future cases | ❌ NOT YET | 20 future cases prepared, Reuse ON/OFF designed |
| L6 | Measured review reduction | ❌ NOT YET | Metrics defined, NO measurement |

```
CURRENT_LEVEL = L3
```

**提升路径**：
- L3 → L4: Human validates CS1 signal (Phase 2, requires participant)
- L4 → L5: Validated signal applied to 20 future cases (Phase 3, requires participant)
- L5 → L6: Measure HRR, quality, boundary (Phase 4, requires GT adjudication)

**注意**: Level 提升基于实际完成，不基于设计完成。当前设计已完成到 L3，但 L4-L6 未执行。

---

## 12. Smallest Next Step

### 提议：授权一次小规模 Human Feedback Reuse Pilot

```
规模: 1 participant
     10 past cases (validation) + 20 future cases (reuse test)
     ~30 minutes total

前提条件:
    1. Human participant available
    2. GT adjudication protocol for 20 future cases (post-experiment)
    3. Experiment UI capable of showing signal context (Reuse ON condition)

不授权的内容:
    - 不自动应用 Signal
    - 不修改 DICE Core
    - 不修改 Frozen Baseline
    - 不修改 Runtime
    - 不建立 Signal Runtime Authority
```

### 如果授权，实验将测试

```
核心问题: 
    一次 Human 对 Evidence 的反馈，在经过 Human 验证后，
    是否能够安全地复用于新的 Case，并因此减少重复 Human Review？

具体测量:
    HRR = (20 - accepted_reuse_count) / 20
    Quality = accuracy_ON vs accuracy_OFF (vs future GT)
    Boundary = UNKNOWN_preservation + CONFLICT_detection
    Safety = error_propagation ≤ baseline
```

### 如果不授权

```
当前状态 = L3 (Reusable Signal Candidate)
等待条件成熟后再执行
```

---

## 13. Signal Representation (Experimental JSON)

实验性 JSON representation（非 DICE Core Schema）：

```json
{
  "signal_id": "CS1-DIFFERENT_TABLE_COLUMNS",
  "signal_version": "1.0-experimental",
  "signal_type": "evidence_grounded_interpretation",
  "not_a_rule": true,
  "not_a_decision_function": true,
  "runtime_authority": "ZERO",
  
  "evidence_signature": {
    "cue1_source": "TLD is_in_table",
    "cue1_value": true,
    "cue2_source": "TLD different_cell",
    "cue2_value": true
  },
  
  "human_interpretation": "Text A and Text B occupy different structural positions within a detected multi-column table",
  
  "scope": {
    "applicable_when": "TLD is_in_table=true AND different_cell=true",
    "structure_families": ["TABLE_NUMERIC", "ROW_LABEL_VALUE", "TABLE_HEADER"]
  },
  
  "boundary": {
    "SUPPORTED": "is_in_table=true AND different_cell=true (31 cases, all KEEP_SEPARATE)",
    "UNSUPPORTED": "is_in_table=false (32 cases, non-table)",
    "UNKNOWN": "is_in_table=true AND different_cell=false (0 cases)",
    "OUT_OF_SCOPE": "Non-table families (PROSE, FIGURE_CAPTION, AXIS)",
    "CONFLICT": "different_cell=true BUT GT=MERGE (0 cases) → EVIDENCE_CONFLICT + NO_AUTO_REUSE + HUMAN_REVIEW"
  },
  
  "validation_status": "CANDIDATE",
  "validation_allowed_values": ["CANDIDATE", "HUMAN_VALIDATED", "REJECTED"],
  "validation_forbidden_values": ["AUTO_APPROVED", "AUTO_EXECUTE", "AUTO_ROUTE", "AUTO_SELECT"]
}
```

---

## 14. Governance Gate

```
DICE_CORE_MODIFICATION      = NO
FROZEN_BASELINE             = INTACT
FROZEN_EXPERIMENT           = INTACT
NEW_MODULE                  = NO
NEW_ENGINE                  = NO
ML_TRAINING                 = NO
RUNTIME_CHANGE              = NO
SIGNAL_RUNTIME_AUTHORITY    = ZERO
EXPERIMENT_AUTHORIZATION    = NOT_GRANTED
STOP                        = TRUE
```

---

## 15. 最终回答

> **我们是否终于有一个可以验证：Human 的一次反馈能够帮助 Machine 处理未来 Case，并因此减少 Human 重复审阅的最小闭环？**

**是的，我们有一个 CONDITIONAL 的最小闭环设计。**

CS1 (DIFFERENT_TABLE_COLUMNS) 满足以下条件：
- 31 个 Past Cases 有 TLD 证据 + Human Feedback + GT
- 20 个 Future Cases 有匹配的 TLD 证据 + GT 未裁决
- Signal Boundary 定义完整 (SUPPORTED/UNSUPPORTED/UNKNOWN/OUT_OF_SCOPE/CONFLICT)
- Reuse ON/OFF 对照设计完成
- Metrics 定义完整 (HRR, Coverage, Precision, Quality, Boundary, Error)
- Circularity Audit 完成 (case-level clean, page-level risk documented)
- Automation Bias Audit 完成 (mitigations defined)

**但这个闭环尚未闭合。**

缺失的环节：
1. **Human Validation** (L3→L4): Human 需要验证 CS1 signal 是否适用于 evidence signature
2. **Reuse Execution** (L4→L5): Validated signal 需要应用于 20 future cases
3. **Measurement** (L5→L6): HRR 和 Quality 需要实际测量

**这 3 个环节需要 Human Participant + Experiment Authorization，当前均未获得。**

`STOP = TRUE`。
