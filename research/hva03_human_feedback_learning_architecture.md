# HVA-03 Human Feedback Learning Loop System Architecture

**Date**: 2026-09-17
**Mode**: READ-ONLY ARCHITECTURE DESIGN / NO IMPLEMENTATION / RESEARCH PROTOTYPE / FROZEN INTACT / STOP
**Predecessors**: HVA-01, HVA-02, DCE-05/06/07, L5 Learning Signal Audit, Info Gain Audit, Feedback Reuse Audit, L5.3 Capability Boundary Review

---

## 1. Executive Summary

```
HVA-03 STATUS = CONDITIONAL

ARCHITECTURE_FEASIBILITY = MEDIUM

  This architecture is FEASIBLE as a thin research prototype.
  It is NOT feasible as a production runtime system at current evidence levels.

  Current Learning Level = L3 (Candidate Discovery)
  Target after Phase 1 = L3+ (Evidence-Linked Candidate)
  Target after Phase 2 = L4 (Human-Validated Signal) — ONLY if Phase 1 proves viable

KEY ARCHITECTURAL DECISIONS:

  1. The Stability-Novelty Paradox is NOT resolved by choosing stable OR novel.
     It is resolved by BOUNDING each signal to its applicable scope.
     → Counterexample Search + Human Boundary Validation

  2. Case Selection changes from GEOMETRIC_AMBIGUITY to REVIEW_VALUE.
     → 6 Value Dimensions + Selection Policy + Safety Constraints
     → NOT a black-box Learning Score

  3. Evidence Pack replaces raw evidence dump with 5-level Progressive Disclosure.
     → L1 must contain Decision-relevant Evidence (fixes AMB-032 distillation gap)

  4. FeedbackRecord links Human Decision to Evidence Snapshot.
     → Currently only saves decision, not what evidence human relied on

  5. SignalCandidate uses Evidence Signature (structural fingerprint), NOT keyword matching.
     → Prevents "keyword repetition = reusable signal" error

  6. Counterexample Search is MANDATORY before any Human Boundary Validation.
     → Prevents ceiling-effect overfitting (SIG-01/04/05)
     → Prevents corpus-specific false positives (SIG-02/06)

  7. ValidatedSignal contains NO decision/routing/score fields.
     → Authority Leakage Prevention

  8. Future Case Replay requires independent documents.
     → Prevents same-page/same-doc data leakage

PRIMARY_BOTTLENECK = Feedback Generalization (Stability-Novelty Paradox)
SECONDARY_BOTTLENECK = Future Validation (0 independent future cases)

STOP = TRUE
```

---

## 2. Current Architecture Gap

### What Exists

```
Current DICE Pipeline:
  Document → P1-P7 Observation → TLD → IS-01/IS-02 → IS-11 Decision → GT Comparison

Current Human Feedback Loop:
  IS-11 Decision → GT Reviewer Rationales → L5 Experiment → Pilot
  (Feedback is CAPTURED but NOT LINKED to evidence)
  (Feedback is STORED but NOT REUSED)
```

### What's Missing (from HVA-01/HVA-02)

| Gap | Evidence | Impact |
|---|---|---|
| Case Selection optimizes wrong metric | HVA-01: 53% Type A wasted, 88% TABLE bias | 87% of human review is low-value |
| Evidence not distilled for human | HVA-01: B2 slower than A (5.9s vs 2.2s), AMB-032 UNKNOWN in B2 | Human can't use existing evidence |
| Feedback not linked to evidence | HVA-02: only saves decision, not evidence refs | Can't trace what human relied on |
| No counterexample search | HVA-02: SIG-02 has 33% FP, discovered only by manual P7 check | Signals with FP get discovered too late |
| No boundary validation | HVA-02: SIG-08 is "CANDIDATE (unstable)" with no mechanism to bound it | Unstable signals either rejected or overclaimed |
| No future case replay | HVA-02: 0 independent future cases, R5=0, R6=0 | Can't prove reuse |
| Stability-Novelty Paradox | HVA-02: stable=redundant, novel=unstable | No signal is both stable AND novel |
| Ceiling effect | HVA-02: 96% KEEP_SEPARATE, 0 negatives | Can't learn boundaries |

### How This Architecture Addresses Each Gap

```
Gap: Case Selection wrong metric
  → P3 Case Selection: 6 Value Dimensions + Selection Policy

Gap: Evidence not distilled
  → P4 Evidence Pack: 5-level Progressive Disclosure

Gap: Feedback not linked
  → P6 FeedbackRecord: decision + evidence_refs + snapshot

Gap: No counterexample search
  → Counterexample Search: mandatory before Boundary Validation

Gap: No boundary validation
  → Human Boundary Validation: positive + counterexamples + UNKNOWN

Gap: No future replay
  → Future Case Replay: independent documents + data leakage prevention

Gap: Stability-Novelty Paradox
  → BOUNDING: each signal gets explicit applicable scope, not global rule

Gap: Ceiling effect
  → P3 Selection Policy: diversity constraint (require non-TABLE, MERGE, CONFLICT)
```

---

## 3. Target Architecture

```
                 DOCUMENT
                    ↓
              ┌─────────────┐
              │  P1 EVIDENCE  │  "Machine看到了什么？"
              └──────┬──────┘
                     ↓
              ┌─────────────┐
              │  P2 CANDIDATE │  "哪些Evidence组合值得分析？"
              └──────┬──────┘
                     ↓
              ┌──────────────────┐
              │  P3 CASE SELECTION │  "哪些Candidate值得Human看？" ← 修复HVA-01
              └──────┬───────────┘
                     ↓
              ┌──────────────────┐
              │  P4 EVIDENCE PACK  │  "Human如何快速获得关键信息？" ← 修复AMB-032
              └──────┬───────────┘
                     ↓
              ┌──────────────────┐
              │  P5 HUMAN REVIEW   │  "Human只做判断，不做分析"
              └──────┬───────────┘
                     ↓
              ┌──────────────────────────┐
              │  P6 FEEDBACK EVIDENCE LINKER │  "Human依赖了什么Evidence？" ← 新增
              └──────┬─────────────────────┘
                     ↓
              ┌──────────────────────────┐
              │  P7 SIGNAL CANDIDATE        │  "结构相似，不是关键词相似" ← 新增
              └──────┬─────────────────────┘
                     ↓
              ┌──────────────────────────┐
              │  COUNTEREXAMPLE SEARCH      │  "主动找反例" ← 新增
              └──────┬─────────────────────┘
                     ↓
              ┌──────────────────────────┐
              │  HUMAN BOUNDARY VALIDATION  │  "Signal适用到哪里？" ← 新增
              └──────┬─────────────────────┘
                     ↓
              ┌──────────────────┐
              │  VALIDATED SIGNAL  │  "有边界的知识，不是规则"
              └──────┬───────────┘
                     ↓
              ┌──────────────────────────┐
              │  FUTURE CASE REPLAY         │  "在新Case上是否成立？" ← 新增
              └──────┬─────────────────────┘
                     ↓
                REUSE / FAILURE
                     │
                     └────────→ FEEDBACK (↺ loop back to P6)
```

---

## 4. P1 Evidence

### 问题
> Machine 到底看到了什么？如果关键 Evidence 不存在，系统怎么阻止下游继续"猜"？

### 职责
Machine Evidence 的结构化记录与完整性声明。

### 输入
- Document pages (PDF/rendered images)
- P1-P7 Observation layer outputs (FROZEN, read-only)
- TLD output (FROZEN, sha256=022f5c21)

### 处理
```
For each candidate pair (text_a, text_b):
  1. Collect P1 evidence: text_a, text_b, bbox_a, bbox_b
  2. Collect P2 evidence: same_y_band, h_gap, x_positions, width
  3. Collect TLD evidence: is_in_table, different_cell, cell_coords
  4. Collect IS-01/IS-02: is_number, has_text
  5. Assess completeness:
     - Has P1 text? → YES/NO
     - Has P2 geometry? → YES/NO
     - Has TLD result? → YES/NO/NOT_APPLICABLE
     - Has IS-01/IS-02? → YES/NO
  6. Assess insufficiency:
     - If TLD=NOT_APPLICABLE AND content is PROSE → mark EVIDENCE_INSUFFICIENT_FOR_TABLE
     - If IS-01=False AND IS-02=False → mark BINARY_SIGNAL_ABSENT
```

### 输出
```python
EvidenceRecord = {
    "case_id": str,
    "document_id": str,
    "page": int,
    "text_a": str,
    "text_b": str,
    "p1_evidence": { "bbox_a": [...], "bbox_b": [...], "page_width": float },
    "p2_evidence": { "same_y_band": bool, "h_gap": float, "x_a": float, "x_b": float },
    "tld_evidence": { "is_in_table": bool, "different_cell": bool|None, "cell_a": [...], "cell_b": [...] },
    "is01": bool,
    "is02": bool,
    "completeness": {
        "has_p1": bool,
        "has_p2": bool,
        "has_tld": bool,
        "has_binary": bool,
    },
    "insufficiency_flags": [str],  # e.g. ["EVIDENCE_INSUFFICIENT_FOR_TABLE"]
    "provenance": {
        "tld_hash": "022f5c21e872ad9e",
        "p1_p7_version": str,
        "timestamp": str,
    }
}
```

### Human 介入
**无。** P1 Evidence 是纯 Machine 结构化记录。

### 风险
| Risk | Mitigation |
|---|---|
| Evidence 缺失 (TLD fails) | `insufficiency_flags` 标记 → 下游 P2 Candidate 必须 propagation |
| Evidence 过时 (frozen hash drift) | `provenance.tld_hash` 校验 → drift 则 BLOCK |
| Evidence 误导 (TLD FP) | 不在 P1 层解决 → 由 Counterexample Search 在 P7 层发现 |

### 失败路由
```
如果 completeness.has_tld = False AND insufficiency_flags 非空:
  → EvidenceRecord 仍输出，但标记 EVIDENCE_INSUFFICIENT
  → P2 Candidate 必须将此标记传入 Candidate.insufficiency_inherited
  → P3 Case Selection 看到 insufficiency → 提高 Review Value (可能揭示 Boundary)
  → P5 Human Review 看到 L1 Evidence Pack 显示 "Evidence Insufficient"
  → Human 可以选 UNKNOWN
```

### 验证
```
Evidence Accuracy (A层):
  Input: EvidenceRecord
  Metric: P1/P2/TLD output matches frozen baseline hash
  Failure: hash drift → BLOCK pipeline
  Safety: provenance hash check on every EvidenceRecord
```

---

## 5. P2 Candidate

### 问题
> 哪些 Evidence 组合值得进一步分析？

### 职责
从 EvidenceRecord 中提取值得进一步分析的 Evidence 组合，形成 Candidate。

### 输入
- EvidenceRecord (from P1)

### 处理
```
For each EvidenceRecord:
  1. Extract structural features:
     - content_type: TABLE_NUMERIC / TABLE_TEXT / PROSE / FIGURE / REFERENCE / OTHER
     - machine_state: DECISIVE (TN/TP) / UNCERTAIN (ABSTAIN) / ERROR (FP/FN)
     - evidence_conflict: TLD vs IS-01/IS-02 disagreement
     - boundary_class: from P7 classification if available
  2. Form Candidate:
     - Candidate does NOT contain any decision (KEEP/MERGE)
     - Candidate does NOT contain any rule
     - Candidate does NOT contain any score
     - Candidate only contains: evidence snapshot + structural features + insufficiency flags
  3. Tag candidate_type:
     - TYPE_A: machine_decisive (low review value)
     - TYPE_D: machine_uncertain (medium review value)
     - TYPE_E: boundary_potential (high review value)
     - TYPE_B: machine_error (review value depends on error type)
```

### 输出
```python
Candidate = {
    "candidate_id": str,
    "case_id": str,
    "evidence_ref": str,  # → EvidenceRecord.case_id
    "content_type": str,  # TABLE_NUMERIC / TABLE_TEXT / PROSE / FIGURE / REFERENCE / OTHER
    "machine_state": str,  # DECISIVE / UNCERTAIN / ERROR
    "evidence_conflict": bool,
    "insufficiency_inherited": [str],
    "candidate_type": str,  # TYPE_A / TYPE_D / TYPE_E / TYPE_B
    "structural_features": {
        "is_number_pair": bool,
        "has_text_pair": bool,
        "is_in_table": bool,
        "different_cell": bool|None,
        "same_y_band": bool,
        "text_a_ends_period": bool,
        "text_b_starts_capital": bool,
        "has_fig_prefix": bool,
    },
    # FORBIDDEN fields: decision, label, rule, score, confidence, recommendation
}
```

### 约束
```
Candidate ≠ Decision  (no KEEP/MERGE/UNKNOWN)
Candidate ≠ Rule      (no IF-THEN)
Candidate ≠ Capability (no runtime authority)
Candidate ≠ Score     (no ranking)
```

### Human 介入
**无。** Candidate 是纯 Machine 结构化提取。

### 风险
| Risk | Mitigation |
|---|---|
| Candidate 包含隐含语义结论 | structural_features 只含布尔/数值，不含 interpretation |
| Candidate 类型误判 | candidate_type 基于机器状态（客观），不基于语义判断 |
| Candidate 过多 | P3 Case Selection 负责过滤 |

### 失败路由
```
如果 evidence_conflict = True:
  → Candidate 标记 candidate_type = TYPE_E (boundary potential)
  → P3 Case Selection 提高 Review Value

如果 insufficiency_inherited 非空:
  → Candidate 标记 insufficiency
  → P3 Case Selection 看到 → 提高 Review Value
```

---

## 6. P3 Case Selection

### 问题
> 当前 Selection 优化几何模糊度（53% 浪费）。如何改为优化 Review Value？

### 职责
从 Candidate Pool 中选择值得 Human 审阅的 Case。

### 输入
- Candidate Pool (from P2)

### 处理

#### Step 1: Value Dimensions (6 dimensions, each 0-3)

```python
def compute_review_value(candidate):
    # D1: Machine Error Risk
    #    Machine likely wrong? (FP/FN history, TLD failure mechanism match)
    d1 = 0
    if candidate.machine_state == "ERROR": d1 = 3
    elif candidate.machine_state == "UNCERTAIN": d1 = 2
    elif candidate.machine_state == "DECISIVE": d1 = 0
    
    # D2: Evidence Uncertainty
    #    Evidence ambiguous? (conflict, insufficiency)
    d2 = 0
    if candidate.evidence_conflict: d2 += 2
    if candidate.insufficiency_inherited: d2 += 1
    
    # D3: Boundary Potential
    #    Could this reveal a boundary? (adjudication history, reviewer disagreement)
    d3 = 0
    if candidate.structural_features.text_a_ends_period and \
       candidate.structural_features.text_b_starts_capital: d3 = 2  # sentence boundary potential
    if candidate.content_type == "PROSE": d3 += 1
    if candidate.content_type == "REFERENCE": d3 += 1
    
    # D4: Feedback Value
    #    Will human feedback contain new info? (not just confirmation)
    d4 = 0
    if candidate.candidate_type == "TYPE_E": d4 = 3
    elif candidate.candidate_type == "TYPE_D": d4 = 1
    elif candidate.candidate_type == "TYPE_A": d4 = 0
    
    # D5: Reuse Potential
    #    Could this generalize? (cross-document structural pattern)
    d5 = 0
    if candidate.content_type in ["PROSE", "REFERENCE", "OTHER"]: d5 = 2  # underrepresented
    if candidate.machine_state == "UNCERTAIN": d5 += 1  # machine gap = reuse potential
    
    # D6: Coverage / Diversity
    #    Is this content type underrepresented in current batch?
    d6 = 0
    # (computed relative to already-selected batch)
    
    return {"D1": d1, "D2": d2, "D3": d3, "D4": d4, "D5": d5, "D6": d6}
```

**关键：这不是一个黑盒 Learning Score。** 每个维度有明确的证据来源和计算方法。

#### Step 2: Selection Policy

```python
def select_cases(candidate_pool, target_count=15):
    selected = []
    
    # Policy 1: MUST include all TYPE_E (boundary potential)
    type_e = [c for c in candidate_pool if c.candidate_type == "TYPE_E"]
    selected.extend(type_e)
    
    # Policy 2: MUST include all TYPE_B (machine error)
    type_b = [c for c in candidate_pool if c.candidate_type == "TYPE_B"]
    selected.extend(type_b)
    
    # Policy 3: Include TYPE_D with highest D2+D3 (uncertain + boundary)
    type_d = [c for c in candidate_pool if c.candidate_type == "TYPE_D"]
    type_d.sort(key=lambda c: compute_review_value(c)["D2"] + compute_review_value(c)["D3"], reverse=True)
    selected.extend(type_d[:target_count - len(selected)])
    
    # Policy 4: EXCLUDE most TYPE_A (machine decisive, low value)
    #   Only include if D6 (diversity) requires it
    remaining_slots = target_count - len(selected)
    if remaining_slots > 0:
        type_a = [c for c in candidate_pool if c.candidate_type == "TYPE_A"]
        # Select only for diversity coverage
        selected.extend(type_a[:remaining_slots])
    
    return selected
```

#### Step 3: Safety Constraints

```python
def validate_selection(selected):
    constraints = {
        "max_table_pct": 0.50,  # HVA-01: current 88% TABLE → cap at 50%
        "min_prose_pct": 0.15,  # HVA-01: current 7% → require at least 15%
        "min_merge_count": 2,   # HVA-02: only 2 MERGE → require at least 2
        "max_type_a_pct": 0.30, # HVA-01: current 53% Type A → cap at 30%
    }
    # If constraints violated → RESELECT with diversity priority
    return check_constraints(selected, constraints)
```

### 输出
```python
SelectedCase = {
    "case_id": str,
    "candidate_id": str,
    "review_value": {"D1": int, "D2": int, "D3": int, "D4": int, "D5": int, "D6": int},
    "selection_reason": str,  # e.g. "TYPE_E boundary potential + PROSE content"
    "evidence_pack_ref": str,  # → P4 Evidence Pack
}
```

### Human 介入
**无。** Case Selection 是 Machine 决策，但受 Safety Constraints 限制。

### 风险
| Risk | Mitigation |
|---|---|
| Selection 偏置 (TABLE overrepresentation) | Safety Constraints: max_table_pct=50%, min_prose_pct=15% |
| Type A 浪费 | Policy 4: EXCLUDE most Type A, only for diversity |
| 价值维度误判 | 6 dimensions 每个有明确 evidence source, 可审计 |
| 黑盒化 | 每个 SelectedCase 记录 selection_reason, 可追溯 |

### 失败路由
```
如果 Safety Constraints 违反:
  → RESELECT with diversity priority
  → 如果 Candidate Pool 不够 diverse (e.g. 0 PROSE cases):
    → flag SELECTION_POOL_BIAS
    → 输出 warning: "Pool lacks PROSE/REFERENCE content"
    → 不强制选择不存在的 Case
```

### 如何解决 HVA-01 的问题

```
HVA-01 发现: 53% Type A 浪费, 88% TABLE bias
HVA-03 解决:
  - Policy 4: EXCLUDE most Type A → Type A ≤ 30%
  - Safety Constraint: max_table_pct=50% → TABLE ≤ 50%
  - Safety Constraint: min_prose_pct=15% → PROSE ≥ 15%
  - D3 Boundary Potential: 优先选择 period+capital, PROSE, REFERENCE
  - D5 Reuse Potential: 优先选择 underrepresented content types
```

---

## 7. P4 Evidence Pack

### 问题
> Evidence 存在但 Human 看不到真正有价值的信息（AMB-032: B2 UNKNOWN despite TLD correct）。

### 职责
对已有 Evidence 进行结构化组织和 Progressive Disclosure。

### 输入
- EvidenceRecord (from P1)
- Candidate (from P2)
- SelectedCase (from P3)

### 处理

#### 5-Level Progressive Disclosure

```
Level 0 — Minimum Context (Human 必须先看到)
  - text_a (truncated to 60 chars)
  - text_b (truncated to 60 chars)
  - page_number
  - document_id
  - content_type (TABLE / PROSE / FIGURE / REFERENCE)
  → Human 可以立即知道"这是什么类型的Case"

Level 1 — Decision-Relevant Evidence (Human 用来做判断)
  - is_in_table: YES/NO
  - different_cell: YES/NO/UNKNOWN
  - is_number_pair: YES/NO
  - has_text_pair: YES/NO
  - text_a_ends_period: YES/NO
  - text_b_starts_capital: YES/NO
  - machine_decision: DECISIVE/UNCERTAIN/ERROR/ABSTAIN
  - insufficiency_flags: [str]
  → Human 看到决策关键信息，不需要从技术字段重建

Level 2 — Supporting Evidence (Human 需要深入时展开)
  - same_y_band: YES/NO
  - h_gap: float
  - x_a, x_b: float
  - width_a, width_b: float
  - style_sig_a, style_sig_b: str
  → 几何和样式细节

Level 3 — Counterevidence / Boundary Evidence
  - evidence_conflict: YES/NO (TLD vs IS-01/IS-02 disagreement)
  - similar_cases_with_different_gt: [case_id] (if any)
  - adjudication_history: YES/NO (was this case adjudicated?)
  - reviewer_disagreement: YES/NO
  → 告诉 Human "这里有矛盾/边界"

Level 4 — Raw Evidence / Provenance
  - Full bbox coordinates
  - Full TLD output (rows, bands, columns, text_ratio)
  - Full P1-P7 raw observation
  - TLD hash, GT hash, timestamp
  → 完整审计追踪
```

### 输出
```python
EvidencePack = {
    "case_id": str,
    "levels": {
        "L0": { "text_a": str, "text_b": str, "page": int, "doc": str, "content_type": str },
        "L1": { "is_in_table": bool, "different_cell": bool|None, "is_number_pair": bool,
                "has_text_pair": bool, "ends_period": bool, "starts_capital": bool,
                "machine_decision": str, "insufficiency": [str] },
        "L2": { "same_y_band": bool, "h_gap": float, "x_a": float, "x_b": float,
                "width_a": float, "width_b": float },
        "L3": { "evidence_conflict": bool, "similar_different_gt": [str],
                "adjudicated": bool, "reviewer_disagreement": bool },
        "L4": { "raw_tld": dict, "raw_p1": dict, "provenance": dict },
    },
    "default_level": 1,  # Human starts at L1
    # FORBIDDEN: recommendation, hint, cue_direction, suggested_answer
}
```

### 关键设计决策

```
1. L1 包含 different_cell (TLD 的关键输出)
   → 修复 AMB-032: B2 之前不暴露 different_cell → Human UNKNOWN
   → 现在 L1 直接显示 different_cell=YES → Human 可以快速判断

2. L3 包含 Counterevidence
   → Human 不再只看正例，也看到反例
   → 防止 confirmation bias

3. Evidence Pack 不包含任何 recommendation/cue/hint
   → 防止 automation bias (HVA-02: B2 cue WRONG on AMB-462/313)
   → Human 看到的是 Evidence，不是 Machine 的建议
```

### Human 介入
Human 与 Evidence Pack 交互：
- 默认看到 L0 + L1
- 可以展开 L2 (Supporting)
- 可以展开 L3 (Counterevidence) — **鼓励在边界 Case 中查看**
- 可以展开 L4 (Raw) — 仅用于审计

### 风险
| Risk | Mitigation |
|---|---|
| Evidence 太多 (L4 信息过载) | Progressive Disclosure: 默认 L1, 逐层展开 |
| Human 被 Machine 带偏 | L1 不含 recommendation/cue, 只含事实 |
| L1 遗漏关键信息 | L1 包含 different_cell + period/capital + machine_decision + insufficiency |
| Pack 设计偏置 | L3 强制包含 counterevidence |

### 失败路由
```
如果 L1 信息不足 (insufficiency_flags 非空):
  → L1 显示 "Evidence Insufficient" 警告
  → Human 看到 → 可以选 UNKNOWN
  → 不强制 Human 在证据不足时做判断

如果 L3 发现 evidence_conflict:
  → L3 高亮显示 conflict
  → 鼓励 Human 展开 L3
  → Human 看到 conflict → 可能选 UNKNOWN 或做 boundary judgment
```

### 如何解决 AMB-032 的问题

```
AMB-032 当前问题:
  B2 Evidence Pack 不暴露 TLD different_cell=True
  → Human B2: UNKNOWN (45.9s, 7 expansions)
  → Human A: KEEP_SEPARATE (1.8s, 0 expansions)

HVA-03 解决:
  L1 直接包含 different_cell=YES
  → Human 看到 L1 → 立即知道"不同单元格" → KEEP_SEPARATE
  → 不需要展开 7 个字段
  → 预期: 决策时间从 45.9s → <5s
```

---

## 8. P5 Human Review

### 问题
> Human 的职责必须严格限定。Human 不负责找 Evidence、整理 Evidence、找 Pattern。

### 职责
Human 只做 Case Judgment + Signal Validation + Boundary Validation + UNKNOWN。

### Human 不做

```
❌ 找 Evidence (Machine 负责 P1)
❌ 整理 Evidence (Machine 负责 P4 Evidence Pack)
❌ 找 Pattern (Machine 负责 P7 Signal Candidate)
❌ 写 Rule (FORBIDDEN)
❌ 写 Classifier (FORBIDDEN)
❌ 写 Prompt (FORBIDDEN)
❌ 写 Runtime Policy (FORBIDDEN)
```

### Human 只做

```
✓ Case Judgment: KEEP / MERGE / UNKNOWN
✓ Signal Candidate Validation: 成立 / 不成立 / 不确定
✓ Boundary Validation: 适用 / 不适用 / 需要限定 / UNKNOWN
✓ OUT_OF_SCOPE judgment
```

### UI / Interaction Contract

#### Case Review Interface

```
┌─────────────────────────────────────────────────────────────┐
│  Case Review: IS11-AMB-032                                    │
│  Document: is11_resnet, Page 6                                 │
│  Content Type: TABLE_NUMERIC                                   │
│                                                                │
│  ┌─── Level 0 ───────────────────────────────────────────┐   │
│  │ text_a: "-"                                           │   │
│  │ text_b: "8.43"                                        │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                                │
│  ┌─── Level 1 (Decision-Relevant) ───────────────────────┐   │
│  │ In Table: YES                                         │   │
│  │ Different Cell: YES                                   │   │
│  │ Number Pair: YES                                      │   │
│  │ Text Pair: NO                                         │   │
│  │ Machine Decision: DECISIVE (KEEP_SEPARATE)            │   │
│  │ Evidence Insufficient: NO                             │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                                │
│  [▶ Expand Level 2: Supporting Evidence]                      │
│  [▶ Expand Level 3: Counterevidence / Boundary]               │
│  [▶ Expand Level 4: Raw Evidence]                             │
│                                                                │
│  ┌─── Your Judgment ─────────────────────────────────────┐   │
│  │  [ KEEP_SEPARATE ]  [ MERGE ]  [ UNKNOWN ]            │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

#### Signal Candidate Validation Interface

```
┌─────────────────────────────────────────────────────────────┐
│  Signal Candidate: SIG-02                                      │
│  Name: Sentence Boundary (Period + Capital)                    │
│                                                                │
│  Evidence Signature:                                           │
│    text_a_ends_period = YES                                    │
│    text_b_starts_capital = YES                                 │
│    is_in_table = NO                                            │
│                                                                │
│  Positive Cases (4):                                           │
│    AMB-005: "degrades rapidly." / "Unexpectedly," → KS        │
│    AMB-375: "[23]." / "Each" → KS                              │
│    AMB-418: "left panel." / "The" → KS                         │
│    AMB-519: "open-source LLMs." / "To embrace" → KS            │
│                                                                │
│  Counterexamples Found (5):                                    │
│    IND-AMB-052: "Furao Shen" / "Image data aug-" → MERGE      │
│    IND-AMB-049: "Levine." / "Bitrate-constrained" → MERGE      │
│    IND-AMB-033: "Le." / "Randaugment:" → MERGE                 │
│    IND-AMB-003: "." / "Philadelphia, PA" → MERGE               │
│    IND-AMB-002: "." / "Springer Berlin" → MERGE                │
│                                                                │
│  ┌─── Your Validation ───────────────────────────────────┐   │
│  │  [ 成立 (Valid) ]                                     │   │
│  │  [ 不成立 (Invalid) ]                                 │   │
│  │  [ 不确定 (UNKNOWN) ]                                 │   │
│  │  [ 需要限定边界 (Needs Boundary) ]                    │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

#### Boundary Validation Interface

```
┌─────────────────────────────────────────────────────────────┐
│  Boundary Validation: SIG-02                                   │
│                                                                │
│  Positive: 4 cases (period+capital → KEEP_SEPARATE)            │
│  Counterexamples: 5 cases (period+capital → MERGE)             │
│                                                                │
│  Question: 这个Signal在什么条件下适用？                          │
│                                                                │
│  Positive pattern: sentence-ending period + new sentence       │
│  Counterexample pattern: mid-sentence period (abbreviations,   │
│    citations, reference entries) + continuation                 │
│                                                                │
│  ┌─── Your Boundary Judgment ────────────────────────────┐   │
│  │  [ 适用 (Applicable as-is) ]                          │   │
│  │  [ 不适用 (Not applicable) ]                          │   │
│  │  [ 需要限定 (Needs scoping) ]                         │   │
│  │    限定条件: ________________________________          │   │
│  │  [ UNKNOWN (Cannot determine) ]                       │   │
│  │  [ OUT_OF_SCOPE (Beyond review scope) ]               │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Human 何时看到原始 Evidence

| 场景 | 看什么 | 为什么 |
|---|---|---|
| 常规 Case Review | L0 + L1 | 快速判断，不需要原始数据 |
| 边界 Case (L3 conflict) | L0 + L1 + L3 | 需要看到 counterevidence |
| Signal Validation | Positive + Counterexamples | 需要对比判断 |
| Boundary Validation | Positive + Counterexamples + UNKNOWN | 需要定义适用范围 |
| 审计/争议 | L4 (Raw) | 完整 provenance 追溯 |

### 风险
| Risk | Mitigation |
|---|---|
| Human 被 Machine 带偏 | Evidence Pack 不含 recommendation/cue (修复 HVA-02: B2 cue WRONG) |
| Human 负担转移 | L1 默认展示，不需要 Human 从 12 个字段重建信息 |
| Human 越权 (写 Rule) | UI 只提供 4 个选项，不提供自由文本 Rule 输入 |
| Human 疲劳 | P3 Selection 减少 Type A → 减少无价值审阅 |

### 失败路由
```
如果 Human 选 UNKNOWN:
  → FeedbackRecord 记录 decision=UNKNOWN
  → 不形成 Signal Candidate (UNKNOWN 不产生 signal)
  → 如果多个 Human 在相同 Evidence Signature 上选 UNKNOWN:
    → 形成 ABSTENTION_BOUNDARY candidate (V4 Boundary Value)

如果 Human 选 OUT_OF_SCOPE:
  → Case 标记为 OUT_OF_SCOPE
  → 不进入 Signal Candidate 流程
  → 记录原因供未来 Case Selection 参考
```

---

## 9. P6 Feedback Evidence Linker

### 问题
> 当前只保存 decision=KEEP，不保存 Human 依赖了什么 Evidence。

### 职责
建立 Human Decision 与 Evidence Snapshot 的结构化关联。

### 输入
- Human Decision (from P5)
- EvidenceRecord (from P1)
- EvidencePack (from P4)
- Evidence levels actually viewed by Human (from P5 interaction log)

### 处理
```
1. Record which Evidence levels Human actually viewed
   (from interaction log: which levels were expanded)
2. Snapshot the Evidence state at decision time
   (freeze evidence values, not references — evidence may change if TLD updates)
3. Identify which evidence fields are "decision-relevant"
   (the fields present in L1 that Human saw)
4. Record evidence_relations:
   (structural relationships between evidence fields, e.g. "different_cell AND is_number → structural separation")
5. Link to provenance
   (TLD hash, GT hash, timestamp — for audit trail)
```

### 输出

```python
FeedbackRecord = {
    "record_id": str,
    "case_id": str,
    "human_id": str,
    "human_decision": str,  # KEEP_SEPARATE / MERGE / UNKNOWN / OUT_OF_SCOPE
    
    "evidence_refs": {
        "evidence_record_id": str,
        "evidence_pack_id": str,
    },
    
    "evidence_snapshot": {
        # Frozen copy of evidence values at decision time
        "is_in_table": bool,
        "different_cell": bool|None,
        "is_number_pair": bool,
        "has_text_pair": bool,
        "text_a_ends_period": bool,
        "text_b_starts_capital": bool,
        "same_y_band": bool,
        "content_type": str,
        "machine_state": str,
    },
    
    "evidence_viewed": {
        "levels_viewed": [int],  # e.g. [0, 1] or [0, 1, 3]
        "fields_expanded": [str],
        "decision_time_ms": int,
    },
    
    "evidence_relations": [
        # Structural relationships (NOT semantic interpretations)
        {"relation": "DIFFERENT_CELL_AND_NUMERIC", "fields": ["different_cell", "is_number_pair"]},
        {"relation": "SENTENCE_BOUNDARY_PATTERN", "fields": ["text_a_ends_period", "text_b_starts_capital"]},
    ],
    
    "provenance": {
        "tld_hash": str,
        "gt_hash": str,
        "timestamp": str,
        "experiment_condition": str,  # A / B1 / B2
    },
    
    # FORBIDDEN fields:
    # - rule, pattern, inference, conclusion
    # - suggested_signal, signal_id (signal formation is P7's job)
    # - confidence, score, weight
}
```

### 字段必要性判断

| 字段 | 必要？ | 理由 |
|---|---|---|
| human_decision | YES | 核心反馈 |
| evidence_snapshot | YES | 必须冻结决策时的 evidence 状态（TLD 可能更新） |
| evidence_viewed | YES | 知道 Human 看了什么，判断反馈质量 |
| evidence_relations | YES | P7 Signal Candidate 需要结构性关系来形成 Signature |
| provenance | YES | 审计追踪，防止 evidence drift |
| human_rationale | OPTIONAL | 如果有则记录，但不依赖（L5 实验 96% 无 rationale） |
| ~~rule~~ | NO | Human 不写 Rule |
| ~~confidence~~ | NO | 不评分 |
| ~~suggested_signal~~ | NO | Signal 由 P7 形成，不由 Human 建议 |

### Human 介入
Human 不直接创建 FeedbackRecord。FeedbackRecord 由系统在 Human 提交决策时自动生成。

### 风险
| Risk | Mitigation |
|---|---|
| Feedback 丢失 (未记录) | FeedbackRecord 自动生成，不依赖 Human 主动填写 |
| Evidence drift (TLD 更改后旧反馈失效) | evidence_snapshot 冻结决策时状态 + provenance hash |
| 关键关系遗漏 | evidence_relations 由 structural_features 自动提取 |
| Human rationale 依赖 | rationale 是 OPTIONAL，系统不依赖它形成 Signal |

### 失败路由
```
如果 Human 没有查看任何 Evidence (decision_time < 1s, 0 expansions):
  → FeedbackRecord 仍记录，但标记 engagement_level=SNAP
  → P7 Signal Candidate 形成时降低 weight (snap judgment 的 signal 可靠性低)
  
如果 evidence_snapshot 与当前 EvidenceRecord 不一致 (hash drift):
  → 标记 FEEDBACK_STALE
  → 不用于 Signal Candidate 形成
  → 记录供审计
```

---

## 10. P7 Signal Candidate

### 问题
> 如何从 FeedbackRecord 中形成 Signal Candidate，避免关键词匹配和 same-page 重复？

### 职责
从多个 FeedbackRecord 中提取结构相似的反馈，形成 Signal Candidate。

### 输入
- Multiple FeedbackRecords (from P6)

### 处理

#### Step 1: Evidence Signature 提取

```python
def extract_evidence_signature(feedback_record):
    """
    Evidence Signature = structural fingerprint of evidence combination
    NOT keyword matching, NOT text content
    """
    snap = feedback_record["evidence_snapshot"]
    
    signature = {
        "content_type": snap["content_type"],
        "is_in_table": snap["is_in_table"],
        "different_cell": snap["different_cell"],
        "is_number_pair": snap["is_number_pair"],
        "has_text_pair": snap["has_text_pair"],
        "text_a_ends_period": snap["text_a_ends_period"],
        "text_b_starts_capital": snap["text_b_starts_capital"],
        "same_y_band": snap["same_y_band"],
        "machine_state": snap["machine_state"],
    }
    return signature
```

**关键：Evidence Signature 是结构特征组合，不是文本内容。**
- ❌ "Human said 'table'" → 不是 Signature
- ✅ `{is_in_table: True, different_cell: True, is_number_pair: True}` → 是 Signature

#### Step 2: 结构相似性判断

```python
def are_structurally_similar(sig_a, sig_b):
    """
    Two cases are "structurally similar" if their Evidence Signatures match
    on ALL decision-relevant fields.
    """
    decision_fields = [
        "content_type", "is_in_table", "different_cell",
        "is_number_pair", "has_text_pair",
        "text_a_ends_period", "text_b_starts_capital",
    ]
    for field in decision_fields:
        if sig_a[field] != sig_b[field]:
            return False
    return True
```

#### Step 3: Independence Check (防止 same-page 重复)

```python
def check_independence(feedback_records):
    """
    HVA-02 发现: SIG-01 有 5 cases 在 resnet page 6 — 不是 5 个独立样本
    """
    groups = {}
    for fr in feedback_records:
        # Group by (document_id, page_number)
        key = (fr["document_id"], fr["page"])
        if key not in groups:
            groups[key] = []
        groups[key].append(fr)
    
    independent_count = len(groups)  # 每个文档-页面组合算 1 个独立观察
    total_count = len(feedback_records)
    
    return {
        "independent_count": independent_count,
        "total_count": total_count,
        "independence_ratio": independent_count / total_count if total_count > 0 else 0,
        "same_page_clusters": {str(k): len(v) for k, v in groups.items() if len(v) > 1},
    }
```

#### Step 4: Signal Candidate 形成

```python
def form_signal_candidate(feedback_records):
    signatures = [extract_evidence_signature(fr) for fr in feedback_records]
    
    # Check all signatures are similar
    if not all(are_structurally_similar(signatures[0], s) for s in signatures[1:]):
        return None  # Not all similar → cannot form candidate
    
    # Check decisions are consistent
    decisions = [fr["human_decision"] for fr in feedback_records]
    unique_decisions = set(decisions)
    
    # Check independence
    indep = check_independence(feedback_records)
    
    candidate = {
        "signal_id": generate_id(),
        "evidence_signature": signatures[0],
        "source_cases": [fr["case_id"] for fr in feedback_records],
        "human_decisions": decisions,
        "decision_consistency": len(unique_decisions) == 1,
        "has_conflict": len(unique_decisions) > 1,
        "independence": indep,
        "recurrence": {
            "same_page": indep["same_page_clusters"],
            "same_doc": count_unique_docs(feedback_records),
            "cross_doc": count_unique_docs(feedback_records),
        },
        "engagement_stats": {
            "snap_count": sum(1 for fr in feedback_records if fr["engagement_level"] == "SNAP"),
            "deep_count": sum(1 for fr in feedback_records if fr["engagement_level"] == "DEEP"),
        },
        "status": "CANDIDATE",
        # FORBIDDEN: rule, decision_function, confidence, score
    }
    
    return candidate
```

### 输出

```python
SignalCandidate = {
    "signal_id": str,
    "evidence_signature": dict,  # structural fingerprint
    "source_cases": [str],
    "source_feedback_records": [str],
    "human_decisions": [str],
    "decision_consistency": bool,
    "has_conflict": bool,
    "independence": {
        "independent_count": int,
        "total_count": int,
        "independence_ratio": float,
        "same_page_clusters": dict,
    },
    "recurrence": {
        "same_page": int,
        "same_doc": int,
        "cross_doc": int,
    },
    "engagement_stats": dict,
    "counterexample_search_result": None,  # filled by Counterexample Search
    "boundary_validation_result": None,     # filled by Human Boundary Validation
    "status": "CANDIDATE",  # CANDIDATE / REJECTED / BOUNDARY_DEFINED / VALIDATED
}
```

### 关键设计决策

```
1. Evidence Signature ≠ Keyword Matching
   → Signature 是结构特征组合 (is_in_table, different_cell, period, capital)
   → 不是文本内容匹配 ("Human said 'table'")

2. Independence Check 强制执行
   → HVA-02 发现: SIG-01 的 5 个 resnet page 6 cases 不是 5 个独立样本
   → independence_ratio < 0.5 → 标记 LOW_INDEPENDENCE
   → Signal Candidate 仍可形成，但标记独立性不足

3. Conflicting Cases 不被丢弃
   → has_conflict=True 时，Signal Candidate 仍形成
   → 但 status 标记为 CONFLICT
   → 必须进入 Boundary Review（不自动解决冲突）

4. UNKNOWN Decisions 不形成 Signal
   → 如果所有 Human 决策都是 UNKNOWN → 不形成 Signal Candidate
   → 但记录为 ABSTENTION_BOUNDARY observation (V4 Boundary Value)

5. Snap vs Deep Engagement 区分
   → snap_count > 70% → 标记 LOW_ENGAGEMENT
   → Signal 仍可形成，但可靠性标记降低
```

### 如何避免关键词假复用

```
HVA-02 禁止: "关键词重复 = Reusable Signal"
HVA-03 解决:
  - Evidence Signature 只包含结构特征 (bool/enum)，不包含文本
  - "Human said 'table' 3 times" → 不形成 Signal
  - "{is_in_table: True, different_cell: True} × 3 cases" → 形成 Signal
  - 文本内容不参与 Signature 计算
```

### 如何避免 same-page 重复被误认为 cross-document

```
HVA-02 发现: SIG-01 的 5 个 resnet page 6 cases
HVA-03 解决:
  - check_independence 按 (document_id, page) 分组
  - 5 cases on resnet page 6 → independent_count=1, total_count=5
  - independence_ratio=0.2 → LOW_INDEPENDENCE
  - Signal Candidate 仍形成但标记独立性不足
  - Counterexample Search 和 Boundary Validation 会看到此标记
```

### 风险
| Risk | Mitigation |
|---|---|
| 关键词假复用 | Evidence Signature 只含结构特征 |
| same-page 重复 | Independence Check (按 doc+page 分组) |
| Conflicting cases 被忽略 | has_conflict=True → 强制 Boundary Review |
| Snap judgments 形成弱 Signal | engagement_stats 标记 LOW_ENGAGEMENT |
| Ceiling effect (all positive) | Counterexample Search 主动找反例 |

### 失败路由
```
如果 independence_ratio < 0.3:
  → 标记 LOW_INDEPENDENCE
  → 不阻止 Candidate 形成，但 Boundary Validation 会看到标记

如果 has_conflict = True:
  → status = CONFLICT
  → MUST enter Boundary Review (不自动解决)

如果所有决策都是 UNKNOWN:
  → 不形成 Signal Candidate
  → 记录为 ABSTENTION_BOUNDARY observation
```

---

## 11. Counterexample Search

### 问题
> 任何 Signal Candidate 都不能直接升级。必须主动寻找反例。

### 职责
对每个 Signal Candidate，在全部 Case Pool 中搜索具有相似 Evidence Signature 但不同 Human Decision 的 Case。

### 输入
- SignalCandidate (from P7)
- All FeedbackRecords (full pool, not just positive cases)
- All EvidenceRecords (including cases not yet human-reviewed)

### 处理

```python
def search_counterexamples(signal_candidate, all_records):
    """
    Search for cases with similar Evidence Signature but different decision.
    """
    target_sig = signal_candidate["evidence_signature"]
    target_decision = signal_candidate["human_decisions"][0]  # assumed consistent
    
    counterexamples = []
    unknown_matches = []
    
    for record in all_records:
        sig = extract_evidence_signature(record)
        
        if are_structurally_similar(target_sig, sig):
            if record["human_decision"] != target_decision:
                if record["human_decision"] == "UNKNOWN":
                    unknown_matches.append(record)
                else:
                    counterexamples.append(record)
            # Also check GT (for cases not yet human-reviewed)
            elif record.get("gt_label") and record["gt_label"] != target_decision:
                counterexamples.append(record)
    
    # Also search in P7 (independent corpus)
    p7_counterexamples = search_p7_corpus(target_sig, target_decision)
    
    return {
        "counterexamples_found": len(counterexamples) + len(p7_counterexamples),
        "counterexamples": [r["case_id"] for r in counterexamples] + p7_counterexamples,
        "unknown_matches": len(unknown_matches),
        "unknown_case_ids": [r["case_id"] for r in unknown_matches],
        "ceiling_effect": len(counterexamples) == 0 and len(unknown_matches) == 0,
        "search_completeness": "FULL" if searched_all else "PARTIAL",
    }
```

### 搜索范围

```
1. Same IS-11 corpus (45 cases)
   → Search all 45 cases (not just positive ones)
   
2. P7 corpus (69 cases)
   → Search by Evidence Signature match
   → Use GT as proxy for Human Decision (if no human review)
   
3. Pilot data (27 cases)
   → Search by structural similarity
   
4. Future corpus (when available)
   → Search new documents
```

### 输出

```python
CounterexampleSearchResult = {
    "signal_id": str,
    "counterexamples_found": int,
    "counterexamples": [{
        "case_id": str,
        "document_id": str,
        "page": int,
        "evidence_signature": dict,
        "human_decision": str,  # or gt_label if no human review
        "decision_source": str,  # HUMAN / GT
    }],
    "unknown_matches": int,
    "ceiling_effect": bool,  # True if 0 counterexamples AND 0 unknowns
    "cross_document_counterexamples": bool,
    "search_completeness": str,
}
```

### 如果找到反例

```
Signal Candidate
  ↓
Counterexample Search finds 5 counterexamples (SIG-02: P7 MERGE cases)
  ↓
→ Signal Candidate status = HAS_COUNTEREXAMPLES
→ MUST enter Human Boundary Validation
→ NOT auto-rejected (counterexamples might define boundary, not invalidate)
→ NOT auto-modified (Machine cannot change Signal)
→ Human sees positive + counterexamples → determines boundary
```

### 如果未找到反例 (ceiling effect)

```
Signal Candidate
  ↓
Counterexample Search finds 0 counterexamples
  ↓
→ Signal Candidate status = CEILING_EFFECT
→ ceiling_effect = True
→ WARNING: "No counterexamples found — cannot determine boundary"
→ Still enters Human Boundary Validation
→ Human sees "0 counterexamples" → likely says UNKNOWN or "needs more data"
→ Signal does NOT auto-validate (absence of counterexamples ≠ proof of universality)
```

### 风险
| Risk | Mitigation |
|---|---|
| 搜索范围不足 | 搜索 IS-11 + P7 + Pilot + Future |
| GT 代替 Human Decision (P7) | 标记 decision_source=GT，区分 HUMAN vs GT |
| Ceiling effect 误判为 universal | ceiling_effect=True → 强制 WARNING，不 auto-validate |
| 反例被自动处理 | FORBIDDEN: Machine 不能修改 Signal → 必须进 Boundary Review |

### 失败路由
```
如果 search_completeness = PARTIAL (搜索范围不全):
  → 标记 SEARCH_INCOMPLETE
  → Boundary Validation 看到 → Human 可以选 UNKNOWN
  
如果 0 counterexamples AND 0 unknowns (ceiling):
  → 标记 CEILING_EFFECT
  → 不 auto-validate
  → Human 看到 "0 counterexamples" → 需要更多数据
```

---

## 12. Human Boundary Validation

### 问题
> Human 不应该重新审几十个 Case。Human 应该看到 Positive + Counterexamples + UNKNOWN，只回答"这个 Signal 适用到哪里？"

### 职责
Human 判断 Signal Candidate 的适用范围。

### 输入
- SignalCandidate (with counterexample search result)
- Positive cases (with Evidence Pack L0-L1)
- Counterexamples (with Evidence Pack L0-L1)
- UNKNOWN matches (if any)

### 处理

Human 看到以下信息：

```
1. Evidence Signature (structural pattern)
2. Positive cases (N cases, all same decision)
3. Counterexamples (M cases, different decision)
4. UNKNOWN matches (K cases, human couldn't resolve)
5. Independence report (same-page clusters, cross-doc count)
6. Engagement report (snap vs deep)
```

Human 只回答一个问题：

> **这个 Signal 在什么条件下适用？**

### Human 选项

```
[ 适用 (Applicable as-is) ]
  → Signal 适用于所有匹配 Evidence Signature 的 Case
  → 要求: 0 counterexamples AND 0 UNKNOWN
  → 如果有 counterexamples → 此选项 DISABLED

[ 不适用 (Not applicable) ]
  → Signal 不成立，拒绝
  → 适用于: counterexamples 证明 pattern 不 universal

[ 需要限定 (Needs scoping) ]
  → Signal 在限定条件下适用
  → Human 提供限定条件 (structural, not semantic)
  → 例如: "仅当 is_in_table=True AND different_cell=True 时适用"
  → NOT: "仅当语义上是表格数据时" (semantic = forbidden)

[ UNKNOWN (Cannot determine) ]
  → Human 无法判断
  → 适用于: reviewer disagreement, insufficient evidence, genuine ambiguity

[ OUT_OF_SCOPE (Beyond review scope) ]
  → 超出当前审阅范围
  → 适用于: 需要领域知识、需要更多数据
```

### 输出

```python
BoundaryValidationResult = {
    "signal_id": str,
    "human_id": str,
    "judgment": str,  # APPLICABLE / NOT_APPLICABLE / NEEDS_SCOPING / UNKNOWN / OUT_OF_SCOPE
    
    "scope_conditions": [str] | None,  # only if NEEDS_SCOPING
    # Structural conditions only, e.g. ["is_in_table=True", "different_cell=True"]
    # FORBIDDEN: semantic conditions, e.g. ["when content is about numbers"]
    
    "evidence_reviewed": {
        "positive_cases_viewed": int,
        "counterexamples_viewed": int,
        "unknowns_viewed": int,
        "levels_viewed": [int],
    },
    
    "rationale": str | None,  # optional, not required
    
    "validation_timestamp": str,
    # FORBIDDEN: confidence, score, weight, authority_level
}
```

### 什么情况必须 UNKNOWN

```
1. Reviewer disagreement on positive cases (SIG-02/08: 3/3 adjudicated)
   → Human sees that reviewers disagreed → likely UNKNOWN
   
2. Counterexamples have same Evidence Signature but different decision
   → Human cannot determine why → UNKNOWN
   
3. Insufficient evidence to distinguish positive from counterexamples
   → Human sees no structural difference → UNKNOWN
   
4. Ceiling effect (0 counterexamples)
   → Human cannot determine boundary → UNKNOWN or "needs more data"
```

### 什么情况 Signal 被拒绝

```
1. Human selects NOT_APPLICABLE
   → counterexamples prove pattern is not universal
   → Signal status = REJECTED
   
2. Counterexamples > 30% of matches (like SIG-02: 33% FP)
   → Human likely selects NOT_APPLICABLE or NEEDS_SCOPING
   → If NEEDS_SCOPING: scope must exclude counterexamples
```

### 什么情况 Signal 被限定边界

```
1. Human selects NEEDS_SCOPING
   → Human provides structural scope conditions
   → Signal becomes BOUNDARY_DEFINED
   → Future replay only applies within scope
   
Example (SIG-02 hypothetical):
   Original: period+capital → KEEP_SEPARATE
   Counterexamples: 5 P7 MERGE cases
   Human scoping: "仅当 is_in_table=False AND content_type=PROSE AND NOT reference_list"
   → Signal scoped to PROSE sentence boundaries only
   → Does NOT apply to REFERENCE_LIST_ENTRY
```

### 风险
| Risk | Mitigation |
|---|---|
| Human 写 semantic scope | UI 只允许 structural conditions (bool/enum)，不允许自由文本 Rule |
| Human 越权 (写 Rule) | UI 只提供 5 个选项，不提供 Rule 输入 |
| Human 疲劳 (太多 Case) | 只展示 Positive + Counterexamples + UNKNOWN，不展示全部 Case |
| Human 被 Machine 带偏 | Counterexample Search 结果是事实呈现，不含 recommendation |

### 失败路由
```
如果 Human 选 UNKNOWN:
  → Signal status = UNKNOWN (not rejected, not validated)
  → 需要更多数据或更多 Human 判断
  → 可以在未来重新提交 Boundary Validation

如果 Human 选 OUT_OF_SCOPE:
  → Signal status = DEFERRED
  → 不进入 Validated Signal
  → 记录供未来参考

如果多个 Human 判断不一致:
  → Signal status = CONFLICT
  → 不进入 Validated Signal
  → 需要 adjudication (类似 GT 的 adjudication 流程)
```

---

## 13. Validated Signal

### 问题
> 只有经过 Human Boundary Validation 后才能成为 Validated Signal。如何防止它偷偷变成 Rule？

### 职责
存储经过验证的 Signal，包含明确的适用边界和反例。

### 输入
- SignalCandidate (with status BOUNDARY_DEFINED or APPLICABLE)
- BoundaryValidationResult

### 输出

```python
ValidatedSignal = {
    "signal_id": str,
    "version": int,  # starts at 1, increments on revalidation
    
    "evidence_preconditions": {
        # Structural conditions that MUST be true for signal to apply
        "is_in_table": bool,
        "different_cell": bool,
        "content_type": str,
        # ... other structural fields from Evidence Signature
    },
    
    "positive_evidence": {
        "evidence_signature": dict,
        "source_cases": [str],
        "source_documents": [str],
        "human_decisions": [str],
    },
    
    "negative_evidence": {
        "counterexample_cases": [str],
        "counterexample_documents": [str],
        "counterexample_decisions": [str],
    },
    
    "boundary": {
        "scope_conditions": [str],  # structural only
        "exclusion_conditions": [str],  # structural only
        "unknown_conditions": [str],  # when signal cannot determine
    },
    
    "unknown_cases": [str],  # cases where signal returns UNKNOWN
    
    "conflict_cases": [str],  # cases with reviewer disagreement
    
    "provenance": {
        "validation_human_id": str,
        "validation_timestamp": str,
        "counterexample_search_result": dict,
        "boundary_validation_result": dict,
        "source_feedback_records": [str],
    },
    
    "validation_status": "VALIDATED",  # VALIDATED / SUPERSEDED / RETIRED
    
    "supersession": {
        "supersedes": str | None,  # previous signal_id if this replaces
        "superseded_by": str | None,  # future signal_id if replaced
    },
    
    # FORBIDDEN FIELDS (Authority Leakage Prevention):
    # decision, selection, routing, ranking, score, confidence,
    # recommendation, execution_plan, fallback, retry, override, correction
}
```

### Authority Leakage Check

| 字段 | 产生 Authority？ | 允许？ |
|---|---|---|
| evidence_preconditions | NO (structural facts) | YES |
| positive_evidence | NO (historical record) | YES |
| negative_evidence | NO (historical record) | YES |
| boundary.scope_conditions | NO (structural constraints) | YES |
| unknown_cases | NO (historical record) | YES |
| ~~decision~~ | YES (would become Rule) | **NO** |
| ~~selection~~ | YES (would become Router) | **NO** |
| ~~routing~~ | YES (would become Runtime) | **NO** |
| ~~score~~ | YES (would become Ranker) | **NO** |
| ~~confidence~~ | YES (would become Weight) | **NO** |
| ~~recommendation~~ | YES (would become Advice) | **NO** |
| ~~fallback~~ | YES (would become Policy) | **NO** |
| ~~override~~ | YES (would become Authority) | **NO** |

**关键：ValidatedSignal 是 KNOWLEDGE RECORD，不是 DECISION FUNCTION。**
- 它记录"在什么条件下，什么 Evidence 组合对应什么 Human 判断"
- 它不决定"系统应该怎么做"
- Future Case Replay 使用它来 CHECK，不是来 DECIDE

### 风险
| Risk | Mitigation |
|---|---|
| Signal 偷偷变成 Rule | FORBIDDEN fields check (no decision/routing/score) |
| Signal 过时 | version + supersession 机制 |
| Scope 条件包含语义 | scope_conditions 只允许 structural (bool/enum) |
| 未验证 Signal 被使用 | validation_status 必须为 VALIDATED |

### 失败路由
```
如果 ValidatedSignal 包含 FORBIDDEN field:
  → REJECT (schema validation fails)
  → Signal 不注册

如果 validation_status != VALIDATED:
  → 不可用于 Future Case Replay
  → 标记为 CANDIDATE 或 REJECTED
```

---

## 14. Future Case Replay

### 问题
> Validated Signal 不能直接宣布"Learning 成功"。必须在新 Case 上验证。

### 职责
在新未见 Case 上 replay Validated Signal，检查是否成立。

### 输入
- ValidatedSignal
- New unseen cases (from new documents, not in training set)

### 新 Case 如何获得

```
1. New documents (not in IS-11 or P7 corpus)
   → Must be from different document_ids
   → Must not share pages with training documents

2. Data leakage prevention:
   - Check document_id not in training set
   - Check page not in training set
   - Check text_a/text_b not exact match of training case
   - If any match → REJECT as "not unseen"

3. Independence guarantee:
   - New document → independent
   - Same document, different page → PARTIALLY independent
   - Same page → NOT independent (REJECT)
```

### 处理

```python
def replay_signal(validated_signal, new_case):
    """
    Apply ValidatedSignal to a new unseen case.
    Returns: SUPPORTED / UNSUPPORTED / UNKNOWN / OUT_OF_SCOPE
    """
    # Step 1: Check preconditions
    if not check_preconditions(validated_signal, new_case):
        return "OUT_OF_SCOPE"
    
    # Step 2: Check scope conditions
    if not check_scope(validated_signal["boundary"]["scope_conditions"], new_case):
        return "OUT_OF_SCOPE"
    
    # Step 3: Check exclusion conditions
    if check_exclusion(validated_signal["boundary"]["exclusion_conditions"], new_case):
        return "OUT_OF_SCOPE"
    
    # Step 4: Check if Evidence Signature matches
    new_sig = extract_evidence_signature(new_case)
    target_sig = validated_signal["positive_evidence"]["evidence_signature"]
    
    if are_structurally_similar(new_sig, target_sig):
        # Signature matches → signal predicts same decision as positive cases
        predicted_decision = validated_signal["positive_evidence"]["human_decisions"][0]
        return "SUPPORTED", predicted_decision
    else:
        # Check if matches counterexample signature
        for ce in validated_signal["negative_evidence"]["counterexample_cases"]:
            if are_structurally_similar(new_sig, extract_evidence_signature(ce)):
                return "UNSUPPORTED", None
        
        # Neither positive nor negative match
        return "UNKNOWN", None
```

### 输出

```python
ReplayResult = {
    "signal_id": str,
    "case_id": str,
    "result": str,  # SUPPORTED / UNSUPPORTED / UNKNOWN / OUT_OF_SCOPE
    "predicted_decision": str | None,
    "human_verified": bool,  # was human review done on this case?
    "human_decision": str | None,  # if human reviewed
    "match": bool | None,  # does signal prediction match human decision?
    "document_independence": {
        "is_new_document": bool,
        "is_new_page": bool,
        "training_set_overlap": bool,
    },
}
```

### 如何判断 Signal 是否真正复用

```
Replay Results Aggregation:
  SUPPORTED + Human matches → True Positive (signal works)
  SUPPORTED + Human differs → False Positive (signal fails)
  UNSUPPORTED + Human matches counterexample → True Negative (signal correctly excludes)
  UNKNOWN → Signal cannot determine (acceptable, not failure)
  OUT_OF_SCOPE → Signal correctly scopes (acceptable)

Learning Success requires:
  1. ≥ 5 independent new cases replayed
  2. True Positive Rate ≥ 80%
  3. False Positive Rate ≤ 10%
  4. ≥ 2 cross-document cases
  5. 0 boundary violations (no OUT_OF_SCOPE case should have been SUPPORTED)
```

### 风险
| Risk | Mitigation |
|---|---|
| 数据泄漏 (same doc/page) | document_independence check (reject if overlap) |
| 过拟合 (signal only works on training corpus) | Require cross-document replay |
| Signal 在新 Corpus 失效 | TLD coverage risk (DCE: TLD may fail on new docs) |
| Human Review 未下降 | Must measure HRR (Human Review Reduction) |

### 失败路由
```
如果 replay result = UNSUPPORTED (signal predicts wrong):
  → Signal prediction ≠ Human decision
  → Record as SIGNAL_FAILURE
  → Signal status → REVIEW (needs revalidation)
  → Does NOT auto-retire (Human must review failure)

如果 False Positive Rate > 10%:
  → Signal status → COMPROMISED
  → Must re-enter Boundary Validation
  → Human reviews failures → may scope, reject, or UNKNOWN

如果 0 new cases available:
  → Cannot replay
  → Signal remains VALIDATED but UNVERIFIED_ON_FUTURE
  → Cannot claim Learning Success (L5 not achieved)
```

---

## 15. Risk → System Mechanism Matrix

| Risk | System Part | Prevention | Detection | Human Boundary | Failure Route |
|---|---|---|---|---|---|
| Evidence 缺失 (TLD fails) | P1 Evidence | insufficiency_flags | completeness check | Human sees L1 "Insufficient" | UNKNOWN |
| Case 太简单 (Type A waste) | P3 Selection | Policy 4: EXCLUDE Type A | Review Value D4=0 → low priority | N/A | Not selected for review |
| Case Selection 偏置 (TABLE 88%) | P3 Selection | Safety Constraints: max_table=50%, min_prose=15% | Constraint validation | N/A | RESELECT with diversity |
| Evidence 太多 (信息过载) | P4 Evidence Pack | Progressive Disclosure L0-L4 | levels_viewed tracking | Human controls expansion | Default L1, expand on demand |
| Human 被 Machine 带偏 (automation bias) | P4+P5 | Evidence Pack 无 recommendation/cue | override tracking | Human can override | No cue = no bias source |
| Feedback 丢失 (未记录) | P6 Feedback Linker | Auto-generate FeedbackRecord | Record count check | N/A | Auto-generation on decision |
| 关键词假复用 | P7 Signal Candidate | Evidence Signature (structural, not text) | Signature format check | N/A | Reject text-based signature |
| 正例过拟合 (ceiling effect) | Counterexample Search | Mandatory search before validation | ceiling_effect=True flag | Human sees "0 counterexamples" | → UNKNOWN or "needs more data" |
| Signal 跨文档失效 | Future Replay | Cross-document independence check | Replay on new docs | Human verifies replay results | Signal → REVIEW → revalidation |
| Boundary 不明确 | Human Boundary Validation | Human must select scope/UNKNOWN | Conflict/UNKNOWN tracking | Human defines boundary | → UNKNOWN or NEEDS_SCOPING |
| 自动泛化错误 | Validated Signal | FORBIDDEN fields (no decision/routing) | Schema validation | N/A | Reject if FORBIDDEN field present |
| Human 负担转移 | P3+P4+P5 | Fewer cases (P3) + better Pack (P4) + simple UI (P5) | decision_time tracking | N/A | If time > 30s → flag HIGH_BURDEN |
| Authority Leakage | Validated Signal | FORBIDDEN fields check | Schema validation | Human retains semantic authority | Reject signal with authority fields |
| Same-page 重复误判 | P7 Signal Candidate | Independence Check (doc+page grouping) | independence_ratio tracking | Human sees independence report | Mark LOW_INDEPENDENCE |
| Conflicting cases 被忽略 | P7 Signal Candidate | has_conflict →强制 Boundary Review | Conflict detection | Human sees conflict | → Boundary Review (not auto-resolve) |
| TLD coverage on new corpus | Future Replay | TLD hash check | TLD output on new docs | Human sees TLD failure | → UNKNOWN (not signal failure) |
| Image confound | P5 Human Review | Image-free test condition | Condition tracking | N/A | Mark IMAGE_CONFOUND present |
| Reviewer disagreement | P7+Boundary | has_conflict flag | Adjudication history | Human sees disagreement | → UNKNOWN or NEEDS_SCOPING |

---

## 16. Accuracy Control Chain

### A. Evidence Accuracy

```
Input: EvidenceRecord (P1)
Metric: P1/P2/TLD output matches frozen baseline hash
Failure: hash drift → evidence is unreliable
Safety: BLOCK pipeline, require hash match
```

### B. Case Selection Quality

```
Input: SelectedCase list (P3)
Metric: 
  - Type A percentage ≤ 30% (HVA-01: was 53%)
  - TABLE percentage ≤ 50% (HVA-01: was 88%)
  - PROSE percentage ≥ 15% (HVA-01: was 7%)
  - MERGE count ≥ 2 (HVA-02: was 2)
Failure: constraints violated → low-quality selection
Safety: RESELECT with diversity priority
```

### C. Evidence Distillation Quality

```
Input: EvidencePack (P4) + Human interaction log (P5)
Metric:
  - L1 contains all decision-relevant fields
  - Mean decision time < 10s (HVA-01: B2 was 5.9s, A was 2.2s)
  - Expansion rate < 30% (HVA-01: was 96% no expansion → good)
  - UNKNOWN rate < 10% (HVA-01: was 4% → acceptable)
Failure: UNKNOWN rate > 20% → evidence not distilled well
Safety: Redesign L1 fields, add missing decision-relevant evidence
```

### D. Signal Quality

```
Input: SignalCandidate (P7)
Metric:
  - independence_ratio ≥ 0.5 (HVA-02: SIG-01 was 0.2 → LOW)
  - decision_consistency = True (or has_conflict flagged)
  - engagement: deep_count > 0 (not all snap)
  - cross_doc_count ≥ 2
Failure: independence_ratio < 0.3 → cannot validate
Safety: Mark LOW_INDEPENDENCE, require more independent cases
```

### E. Boundary Quality

```
Input: BoundaryValidationResult
Metric:
  - Counterexample search completed (not PARTIAL)
  - Human judgment is not UNKNOWN (or UNKNOWN is accepted with reason)
  - Scope conditions are structural (not semantic)
  - 0 unresolved conflicts
Failure: Human selects UNKNOWN → boundary undefined
Safety: Signal remains CANDIDATE, not VALIDATED
```

### F. Reuse Quality

```
Input: ReplayResult list
Metric:
  - ≥ 5 independent new cases replayed
  - True Positive Rate ≥ 80%
  - False Positive Rate ≤ 10%
  - ≥ 2 cross-document cases
  - 0 boundary violations
Failure: FP rate > 10% → signal compromised
Safety: Signal → REVIEW → revalidation or retirement
```

---

## 17. Human / Machine Authority Boundary

### Machine 可以做

```
✓ Evidence aggregation (P1: collect P1-P7, TLD, IS-01/IS-02)
✓ Evidence compression (P4: organize into 5-level Evidence Pack)
✓ Structural comparison (P7: Evidence Signature similarity)
✓ Candidate discovery (P7: group similar FeedbackRecords)
✓ Signal candidate discovery (P7: form SignalCandidate)
✓ Counterexample search (search for similar signature + different decision)
✓ Replay (apply ValidatedSignal to new cases, return SUPPORTED/UNSUPPORTED)
✓ Independence check (group by doc+page)
✓ Completeness check (verify evidence fields)
```

### Human 才能做

```
✓ Semantic validation (does this structural pattern make semantic sense?)
✓ Signal validation (is this candidate成立/不成立/不确定?)
✓ Boundary validation (where does this signal apply?)
✓ UNKNOWN judgment (when evidence is insufficient)
✓ Final registration (approve ValidatedSignal)
✓ OUT_OF_SCOPE judgment (when case is beyond system scope)
```

### Authority Leakage Check

```
检查: 有没有任何环节偷偷把 Human 判断自动升级成 Runtime Authority?

P1 Evidence: NO (pure machine observation)
P2 Candidate: NO (pure structural extraction)
P3 Selection: NO (machine selects cases, but doesn't make decisions)
P4 Evidence Pack: NO (presents evidence, no recommendation)
P5 Human Review: HUMAN AUTHORITY (decision is human's)
P6 Feedback Linker: NO (records human decision, doesn't act on it)
P7 Signal Candidate: NO (forms candidate, doesn't validate)
Counterexample Search: NO (finds facts, doesn't modify signal)
Human Boundary Validation: HUMAN AUTHORITY (boundary is human's)
Validated Signal: CHECK (knowledge record, NOT decision function)
  → FORBIDDEN fields prevent authority leakage
  → ValidatedSignal records "what was validated", not "what to do"
Future Replay: NO (checks signal, returns result, doesn't decide)

结论: NO AUTHORITY LEAKAGE.
  Machine 保留 structural authority (aggregation, compression, comparison).
  Human 保留 semantic authority (validation, boundary, registration).
  ValidatedSignal 是 knowledge record, 不是 runtime policy.
```

---

## 18. SIG-01 Analysis

### Current State
```
SIG-01: TABLE_NUMERIC_DIFF_CELL → SPLIT
R3 (cross-page recurrence)
Status: CANDIDATE
9 cases, 3 docs, but 5 on resnet page 6 (independence_ratio=0.33)
Info gain: LOW (BOUNDARY_CONFIRMATION — machine already has TLD evidence)
```

### Architecture Walk-Through

```
Step 1: P6 FeedbackRecord
  → 9 FeedbackRecords captured with evidence_snapshot
  → All show: is_in_table=True, different_cell=True, is_number_pair=True

Step 2: P7 Signal Candidate
  → Evidence Signature: {is_in_table:True, different_cell:True, is_number_pair:True}
  → 9 cases, all KEEP_SEPARATE → decision_consistency=True
  → Independence Check: 5 on resnet p6 → independent_count=3, ratio=0.33
  → Marked LOW_INDEPENDENCE
  → Engagement: 9/9 snap judgments → LOW_ENGAGEMENT

Step 3: Counterexample Search
  → Search IS-11 (45 cases): 0 counterexamples (all 9 are the positive set)
  → Search P7 (69 cases): 0 counterexamples with this exact signature
  → ceiling_effect=True
  → WARNING: "0 counterexamples — cannot determine boundary"

Step 4: Human Boundary Validation
  → Human sees: 9 positive + 0 counterexamples + LOW_INDEPENDENCE + LOW_ENGAGEMENT
  → Human likely selects: UNKNOWN ("cannot determine boundary without counterexamples")
  → OR: OUT_OF_SCOPE ("need more diverse data")

Step 5: Result
  → Signal does NOT reach VALIDATED status
  → Remains CANDIDATE with status UNKNOWN
  → Cannot enter Future Case Replay
```

### Why Architecture Prevents Wrong Upgrade

```
1. Independence Check prevents 5 same-page cases from being counted as 5 independent
2. Counterexample Search reveals ceiling effect (0 negatives)
3. Human Boundary Validation requires human judgment, not auto-validation
4. ceiling_effect=True → human likely says UNKNOWN
5. Signal remains CANDIDATE, not VALIDATED
→ SIG-01 does NOT wrongly upgrade to R5
```

---

## 19. SIG-02 Analysis

### Current State
```
SIG-02: SENTENCE_BOUNDARY_PERIOD_CAPITAL → SPLIT
R4 (cross-document, 7 docs)
Status: CANDIDATE (with counterexamples)
4 IS-11 positive + 15 P7 cases (10 KS, 5 MERGE = 33% FP)
Adjudicated: 4/4 (reviewer disagreement)
```

### Architecture Walk-Through

```
Step 1: P6 FeedbackRecord
  → 4 FeedbackRecords from adjudicated cases
  → evidence_snapshot: text_a_ends_period=True, text_b_starts_capital=True
  → has_conflict=True (Reviewer A: KS, Reviewer B: MERGE)

Step 2: P7 Signal Candidate
  → Evidence Signature: {text_a_ends_period:True, text_b_starts_capital:True, is_in_table:False}
  → 4 cases, decisions: KS, KS, KS, KS (adjudicated to KS)
  → decision_consistency=True (at adjudicated level)
  → has_conflict=True (reviewer disagreement at review level)
  → Status: CONFLICT (must enter Boundary Review)

Step 3: Counterexample Search
  → Search IS-11: 0 counterexamples (only 4 cases have this signature)
  → Search P7: 15 cases match signature
    → 10 KEEP_SEPARATE (positive)
    → 5 MERGE (COUNTEREXAMPLES!)
  → counterexamples_found=5
  → cross_document_counterexamples=True
  → ceiling_effect=False

Step 4: Human Boundary Validation
  → Human sees:
    - 4 positive (IS-11, adjudicated to KS)
    - 5 counterexamples (P7, MERGE)
    - has_conflict=True (reviewer disagreement)
    - 33% false positive rate
  → Human CANNOT select "适用 (Applicable)" → disabled (counterexamples exist)
  → Human options:
    a) "不适用 (Not applicable)" — 33% FP too high, pattern not universal
    b) "需要限定 (Needs scoping)" — try to find structural distinction
    c) "UNKNOWN (Cannot determine)" — cannot distinguish positive from counterexamples

  → Analysis: Positive cases (IS-11) and counterexamples (P7) have SAME Evidence Signature
    → No structural feature distinguishes them
    → Human likely selects UNKNOWN ("cannot determine structural boundary")
    → OR: attempts NEEDS_SCOPING but finds no structural scope condition
    → → falls back to UNKNOWN

Step 5: Result
  → Signal status = UNKNOWN (not validated, not rejected)
  → Cannot enter Future Case Replay
  → SIG-02 correctly blocked from wrong upgrade
```

### Why Architecture Prevents Wrong Upgrade

```
1. Counterexample Search PROACTIVELY finds P7 MERGE cases (before human validation)
2. Human sees counterexamples → cannot select "Applicable"
3. No structural feature distinguishes positive from counterexamples
4. Human selects UNKNOWN → signal not validated
5. 33% FP rate discovered and acted upon
→ SIG-02 does NOT upgrade to R5 despite R4 cross-document recurrence
```

### Contrast with Current System

```
Current system (HVA-02):
  → SIG-02 was discovered to have 33% FP only by MANUAL P7 check
  → No systematic mechanism to find counterexamples
  → Signal could have been wrongly upgraded if no one checked P7

HVA-03 architecture:
  → Counterexample Search is MANDATORY and AUTOMATIC
  → P7 cases are searched by default
  → 33% FP discovered before any human validation
  → Human Boundary Validation shows counterexamples
  → Signal correctly blocked
```

---

## 20. SIG-07 Analysis

### Current State
```
SIG-07: AMB-032 Evidence Distillation Gap
R1 (local only)
Status: NOT_REUSABLE
One-off: B2 doesn't expose TLD different_cell, Human UNKNOWN in B2
```

### Architecture Walk-Through

```
Step 1: P6 FeedbackRecord
  → AMB-032 FeedbackRecord captured:
    - human_decision (A): KEEP_SEPARATE
    - human_decision (B2): UNKNOWN
    - evidence_snapshot: is_in_table=True, different_cell=True
    - evidence_viewed (B2): levels_viewed=[0,2], 7 fields expanded

Step 2: P7 Signal Candidate
  → Only 1 case with this pattern (AMB-032 B2 UNKNOWN)
  → Cannot form Signal Candidate (need ≥ 2 structurally similar cases)
  → Marked as ONE_OFF_OBSERVATION

Step 3: Routing
  → NOT routed to Counterexample Search (not a Signal Candidate)
  → Routed to EVIDENCE_DISTILLATION_FEEDBACK
  → This is a SYSTEM PRESENTATION issue, not a FEEDBACK SIGNAL

Step 4: P4 Evidence Pack Redesign
  → AMB-032 reveals: B2 doesn't expose different_cell in L1
  → HVA-03 Evidence Pack L1 includes different_cell=YES
  → This FIXES the distillation gap
  → Future AMB-032-like cases: Human sees L1 → resolves in <5s

Step 5: Result
  → SIG-07 does NOT become a Signal Candidate
  → It becomes an Evidence Pack improvement input
  → Correctly classified as system presentation issue, not reusable signal
```

### Why Architecture Prevents Wrong Packaging

```
1. P7 requires ≥2 structurally similar cases → SIG-07 (1 case) cannot form Candidate
2. The observation (B2 UNKNOWN despite TLD correct) is a DISTILLATION GAP, not a SIGNAL
3. Architecture routes it to P4 Evidence Pack improvement, not P7 Signal Candidate
4. No risk of packaging a system presentation bug as "reusable knowledge"
→ SIG-07 correctly stays R1, NOT_REUSABLE
```

---

## 21. SIG-08 Analysis

### Current State
```
SIG-08: AMB-375 Genuine Boundary
R2 (repeated)
Status: CANDIDATE (unstable)
Adjudicated (Reviewer A: KS, Reviewer B: MERGE)
P7 has 5 counterexamples with same signature
```

### Architecture Walk-Through

```
Step 1: P6 FeedbackRecord
  → AMB-375 FeedbackRecord:
    - Reviewer A: KEEP_SEPARATE (sentence boundary)
    - Reviewer B: MERGE (paragraph flow)
    - Adjudicator: KEEP_SEPARATE (period+capital)
    - Human B2: UNKNOWN (31.3s, 7 expansions)
    - evidence_snapshot: text_a_ends_period=True, text_b_starts_capital=True

Step 2: P7 Signal Candidate
  → Evidence Signature: {text_a_ends_period:True, text_b_starts_capital:True, is_in_table:False}
  → Same as SIG-02 (4 cases total: AMB-005/375/418/519)
  → has_conflict=True (reviewer disagreement)
  → Status: CONFLICT

Step 3: Counterexample Search
  → Same as SIG-02: 5 P7 counterexamples found
  → 33% FP rate

Step 4: Human Boundary Validation
  → Human sees:
    - 4 positive (adjudicated to KS, but Reviewer B disagreed)
    - 5 counterexamples (P7 MERGE)
    - has_conflict=True
    - Reviewer B's rationale: "same paragraph/sentence flow"
    - Counterexample pattern: mid-sentence period (abbreviations, citations)
  → Human CANNOT select "Applicable" (counterexamples exist)
  → Human attempts NEEDS_SCOPING:
    - Can human find structural feature that separates positive from counterexamples?
    - Positive: text_a ends with sentence-ending period, text_b starts new sentence
    - Counterexample: text_a ends with period but NOT sentence-ending (abbreviation, citation)
    - BUT: this distinction is SEMANTIC (is the period sentence-ending or not?)
    - System cannot determine this structurally
    - Human cannot express this as structural scope condition
  → Human selects UNKNOWN ("cannot determine structural boundary")
  → OR: selects NEEDS_SCOPING with scope "is_in_table=False AND content_type=PROSE"
    → But P7 counterexamples are also PROSE → scope doesn't help
  → Falls back to UNKNOWN

Step 5: Result
  → Signal status = UNKNOWN
  → Genuine boundary acknowledged but cannot be structurally scoped
  → Signal does NOT become Validated Signal
  → Correctly classified as "genuine boundary but unstable"
```

### Why Architecture Prevents Wrong Upgrade

```
1. has_conflict=True → forced to Boundary Review
2. Counterexample Search finds 5 P7 MERGE cases
3. Human sees counterexamples → cannot select "Applicable"
4. No structural scope can separate positive from counterexamples
5. Human selects UNKNOWN → signal not validated
→ SIG-08 correctly remains CANDIDATE (unstable), NOT VALIDATED
```

### Why SIG-08 Needs Boundary Validation (Not Direct Rule)

```
Without Boundary Validation:
  → AMB-375 is "genuine boundary" → might be packaged as Rule
  → Rule: "period+capital → KEEP_SEPARATE"
  → This Rule has 33% FP on P7 → causes 5 wrong decisions
  → System makes errors

With Boundary Validation:
  → Counterexample Search reveals 5 FP
  → Human sees counterexamples → cannot validate as universal rule
  → Human selects UNKNOWN or attempts scoping
  → Signal remains CANDIDATE, NOT Rule
  → No wrong decisions made
→ Boundary Validation is ESSENTIAL for SIG-08
```

---

## 22. Failure Routes

### Complete Failure Route Map

```
                        ┌→ UNKNOWN (Human can't resolve)
                        │
Case → P1 Evidence ─────┼→ P2 Candidate → P3 Selection → P4 Pack → P5 Review
                        │    ↓                 ↓              ↓          ↓
                        │  insufficiency   constraints    L1 info    Human decision
                        │  propagated      validated      displayed   (KEEP/MERGE/UNKNOWN)
                        │                                               ↓
                        │                                    P6 FeedbackRecord
                        │                                               ↓
                        │                                    P7 Signal Candidate
                        │                                          ↓
                        │                              ┌── has_conflict? ──┐
                        │                              │ YES               │ NO
                        │                              ↓                   ↓
                        │                    forced Boundary Review   Counterexample Search
                        │                              │                   ↓
                        │                              │          ┌── counterexamples? ──┐
                        │                              │          │ YES (>0)             │ 0 (ceiling)
                        │                              │          ↓                      ↓
                        │                              │   Human Boundary       Human Boundary
                        │                              │   Validation            Validation
                        │                              │       ↓                      ↓
                        │                              │  ┌── judgment ──┐    ┌── judgment ──┐
                        │                              │  │              │    │              │
                        │                              │  APPLICABLE    │    UNKNOWN       │
                        │                              │  (0 counter)   │    ("need data") │
                        │                              │  → VALIDATED   │    → CANDIDATE   │
                        │                              │                │                   │
                        │                              │  NOT_APPLICABLE│    NOT_APPLICABLE│
                        │                              │  → REJECTED    │    → REJECTED    │
                        │                              │                │                   │
                        │                              │  NEEDS_SCOPING │                   │
                        │                              │  → BOUNDARY_   │                   │
                        │                              │    DEFINED     │                   │
                        │                              │    → VALIDATED │                   │
                        │                              │                │                   │
                        │                              │  UNKNOWN       │                   │
                        │                              │  → CANDIDATE   │                   │
                        │                              │    (unstable)  │                   │
                        │                              │                │                   │
                        │                              │  OUT_OF_SCOPE  │                   │
                        │                              │  → DEFERRED    │                   │
                        │                              └────────────────┘   └───────────────┘
                        │                                      ↓
                        │                              ValidatedSignal
                        │                                      ↓
                        │                              Future Case Replay
                        │                                      ↓
                        │                              ┌── replay result ──┐
                        │                              │                    │
                        │                          SUPPORTED            UNSUPPORTED
                        │                          + Human matches       + Human differs
                        │                          → True Positive       → False Positive
                        │                          → Signal works        → SIGNAL_FAILURE
                        │                                                 → REVIEW
                        │                                                 → revalidation
                        │
                        └→ OUT_OF_SCOPE (beyond system scope)
```

### Failure Categories

| Failure | Where Detected | Action | Human Involved? |
|---|---|---|---|
| Evidence missing | P1 | Flag insufficiency → propagate | No (auto) |
| Case too simple | P3 | Not selected | No (auto) |
| Selection bias | P3 | RESELECT | No (auto) |
| Evidence overload | P4/P5 | Track expansion, default L1 | No (auto) |
| Automation bias | P4/P5 | No cue in Pack | No (design) |
| Keyword false reuse | P7 | Reject text-based signature | No (auto) |
| Same-page repetition | P7 | Mark LOW_INDEPENDENCE | No (auto) |
| Ceiling effect | Counterexample | Flag, prevent auto-validation | Yes (Boundary) |
| Cross-doc failure | Future Replay | Signal → REVIEW | Yes (revalidation) |
| Boundary unclear | Human Boundary | → UNKNOWN | Yes (Human) |
| Authority leakage | Validated Signal | Schema validation rejects | No (auto) |
| Conflict unresolved | P7/Boundary | → UNKNOWN or CONFLICT | Yes (Human) |
| Signal compromised | Future Replay | FP > 10% → REVIEW | Yes (Human) |

---

## 23. Minimal Prototype Boundary

### What Phase 1 Prototype Includes

```
INCLUDED:
  ✓ P6 FeedbackRecord (capture decision + evidence link)
  ✓ P7 Signal Candidate (Evidence Signature + independence check)
  ✓ Counterexample Search (offline, on IS-11 + P7)
  ✓ P4 Evidence Pack L0-L1 (basic progressive disclosure)

NOT INCLUDED (Phase 2):
  ✗ P3 Case Selection redesign (requires new candidate pool)
  ✗ Human Boundary Validation UI (requires Human experiment)
  ✗ Validated Signal (requires Boundary Validation)
  ✗ Future Case Replay (requires new corpus)
```

### What Phase 1 Prototype Does NOT Do

```
✗ Does NOT modify DICE Core (P1-P7, TLD, IS-11)
✗ Does NOT create new Engine/Module/Runtime
✗ Does NOT run formal Human Experiment
✗ Does NOT validate any Signal
✗ Does NOT enter Runtime/Capability
✗ Does NOT use LLM
✗ Does NOT create Rules
```

### Phase 1 Success Criteria

```
1. FeedbackRecord can be generated for all 45 IS-11 cases
   → Each record links decision to evidence_snapshot
   → evidence_viewed tracks which levels human saw

2. Evidence Signature can be extracted from FeedbackRecord
   → Structural fingerprint (not text)
   → Correctly identifies similar cases

3. Signal Candidates can be formed from FeedbackRecords
   → Grouping by Evidence Signature
   → Independence check works (resnet p6 cluster detected)

4. Counterexample Search can run on IS-11 + P7
   → Finds SIG-02's 5 P7 counterexamples
   → Detects ceiling effect for SIG-01/04/05

5. Evidence Pack L0-L1 can be generated
   → L1 contains different_cell (fixes AMB-032)
   → Human can see decision-relevant evidence at first glance
```

### Phase 1 Does NOT Prove

```
✗ Does NOT prove Learning (no Validated Signal)
✗ Does NOT prove Reuse (no Future Replay)
✗ Does NOT prove HRR (no Human Review Reduction measurement)
✗ Does NOT prove Boundary (no Human Boundary Validation)
→ Phase 1 only proves the PIPELINE is mechanically viable
```

---

## 24. Final Architecture Judgment

### How Architecture Addresses Stability-Novelty Paradox

```
HVA-02 Finding:
  Stable signals are redundant (Machine has evidence → LOW info gain)
  Novel signals are unstable (Human reviewers disagree → no stable boundary)

HVA-03 Resolution:
  The paradox is NOT resolved by choosing stable OR novel.
  It is resolved by BOUNDING each signal to its applicable scope.

  For stable signals (SIG-01/04/05):
    → Counterexample Search finds ceiling effect (0 negatives)
    → Human Boundary Validation → UNKNOWN ("cannot determine boundary")
    → Signal stays CANDIDATE, correctly identified as redundant

  For novel signals (SIG-02/08):
    → Counterexample Search finds counterexamples (P7 FP)
    → Human Boundary Validation → UNKNOWN or NEEDS_SCOPING
    → If NEEDS_SCOPING: signal gets structural scope
    → If UNKNOWN: signal stays CANDIDATE, correctly identified as unstable

  Result: Neither stable nor novel signals are wrongly upgraded.
  Both are correctly classified and bounded.
```

### How Architecture Addresses HVA-01 Findings

```
HVA-01 Finding: 53% Type A waste, 88% TABLE bias
HVA-03 Resolution:
  P3 Case Selection:
    - Policy 4: EXCLUDE most Type A (cap at 30%)
    - Safety Constraints: max_table=50%, min_prose=15%
    - 6 Value Dimensions prioritize boundary/diversity/reuse

HVA-01 Finding: B2 slower than A, distillation adds load
HVA-03 Resolution:
  P4 Evidence Pack:
    - L1 contains decision-relevant evidence (different_cell, period, capital)
    - No cue/recommendation (prevents automation bias)
    - Progressive Disclosure (default L1, expand on demand)

HVA-01 Finding: Only 2/45 high-value cases
HVA-03 Resolution:
  P3 Selection: prioritize TYPE_E and diverse content
  → More high-value cases selected
  → Better use of human review effort
```

### How Architecture Addresses HVA-02 Findings

```
HVA-02 Finding: R5=0, R6=0, no reusable signal
HVA-03 Resolution:
  The architecture does NOT claim to achieve R5/R6.
  It provides the MECHANISM to attempt R5/R6:
    - P6-P7: link feedback to evidence, form candidates
    - Counterexample Search: prevent wrong upgrade
    - Human Boundary Validation: human-defined boundary
    - Future Replay: test on new cases

  But: success depends on DATA (more diverse cases, more participants, future corpus)
  Architecture cannot create data. It can only process what exists.

HVA-02 Finding: TLD is INDEPENDENT of feedback value
HVA-03 Resolution:
  Architecture does NOT focus on TLD.
  P1 Evidence captures TLD output as-is (frozen).
  TLD failure → insufficiency_flags → Human sees "Insufficient" → UNKNOWN.
  No attempt to fix TLD (DCE-07 closed route).
```

### Architecture Limitations

```
1. Cannot create data:
   → Needs more diverse cases (PROSE, REFERENCE, MERGE)
   → Needs more participants (n=1 currently)
   → Needs future corpus for replay
   → Architecture processes data, doesn't create it

2. Cannot resolve semantic boundaries:
   → SIG-02/08 boundary (sentence vs paragraph) is semantic
   → System can only express structural features
   → Human must resolve, but human may also say UNKNOWN
   → Some boundaries may be permanently UNKNOWN

3. Cannot prove Learning without future cases:
   → Future Replay requires new documents
   → No new documents available currently
   → Architecture is ready but data is not

4. Cannot measure HRR without experiment:
   → HRR measurement requires controlled experiment
   → Experiment is NOT AUTHORIZED
   → Architecture designs the measurement, doesn't execute it
```

---

## 25. Implementation Roadmap

### Phase 0: Architecture / Contract (NO CODE)

```
Duration: 1-2 days
Deliverables:
  1. FeedbackRecord schema (JSON Schema)
  2. SignalCandidate schema (JSON Schema)
  3. EvidencePack schema (JSON Schema)
  4. ValidatedSignal schema (JSON Schema)
  5. CounterexampleSearchResult schema
  6. BoundaryValidationResult schema
  7. ReplayResult schema

Constraints:
  - NO code implementation
  - NO runtime
  - NO DICE Core modification
  - Schema only

Success Criteria:
  - All schemas validated against HVA-01/HVA-02 data
  - SIG-01/02/07/08 walk-through completed on paper
  - FORBIDDEN fields check implemented in schema
```

### Phase 1: Minimal Prototype (OFFLINE ONLY)

```
Duration: 3-5 days
Deliverables:
  1. FeedbackRecord generator (reads existing GT + L5 data)
     → Generate FeedbackRecord for all 45 IS-11 cases
     → Generate FeedbackRecord for 55 L5 judgments
  
  2. Evidence Signature extractor
     → Extract structural fingerprint from FeedbackRecord
     → Group similar cases
  
  3. Signal Candidate former
     → Form candidates from grouped FeedbackRecords
     → Independence check (detect resnet p6 cluster)
  
  4. Counterexample Search (offline)
     → Search IS-11 + P7 for counterexamples
     → Reproduce SIG-02's 5 P7 FP discovery
  
  5. Evidence Pack L0-L1 generator
     → Generate Pack for 45 IS-11 cases
     → Verify L1 contains different_cell (AMB-032 fix)

Constraints:
  - OFFLINE only (no runtime, no UI)
  - NO DICE Core modification
  - NO Human Experiment
  - NO Signal Validation
  - NO Future Replay
  - All outputs are JSON files in tmp/

Success Criteria:
  1. All 45 IS-11 cases have FeedbackRecord
  2. Evidence Signature correctly groups similar cases
  3. Signal Candidates match HVA-02's 8 candidates
  4. Counterexample Search finds SIG-02's 5 P7 FP
  5. Evidence Pack L1 for AMB-032 shows different_cell=YES
  6. Independence check detects resnet p6 cluster (SIG-01)

Phase 1 Does NOT Prove:
  - Learning (no validation)
  - Reuse (no replay)
  - HRR (no experiment)
  - Boundary (no human validation)
  → Phase 1 only proves pipeline mechanical viability
```

### Phase 2: Human Validation + Future Replay (ONLY IF PHASE 1 SUCCEEDS)

```
Prerequisites:
  - Phase 1 success criteria ALL met
  - Human experiment authorization (NOT currently granted)
  - New corpus available (NOT currently available)

Duration: 2-4 weeks
Deliverables:
  1. Human Boundary Validation UI
     → Show Positive + Counterexamples + UNKNOWN
     → 5-option judgment (Applicable/Not/Scoping/UNKNOWN/OUT_OF_SCOPE)
  
  2. Validated Signal registration
     → Schema validation (FORBIDDEN fields check)
     → Version + supersession
  
  3. Future Case Replay
     → New document independence check
     → Replay on unseen cases
     → SUPPORTED/UNSUPPORTED/UNKNOWN/OUT_OF_SCOPE
  
  4. HRR Measurement
     → Compare human review count before/after signal application
     → Measure decision quality preservation

Constraints:
  - Requires Human Experiment authorization
  - Requires new corpus
  - NO Runtime integration
  - NO Capability registration
  - NO Production deployment
  - Still research prototype

Success Criteria:
  1. ≥ 1 Signal reaches VALIDATED status
  2. ≥ 5 independent future cases replayed
  3. True Positive Rate ≥ 80%
  4. False Positive Rate ≤ 10%
  5. HRR measured (even if not achieved)

Phase 2 Does NOT:
  - Enter Runtime
  - Enter Capability
  - Enter Production
  - Modify DICE Core
  → Phase 2 proves Learning (L4-L5) IF data supports it
```

### Phase 3+ (NOT PLANNED)

```
Phase 3: Runtime Integration
  → ONLY if Phase 2 proves Learning with measured HRR
  → NOT currently authorized
  → NOT currently feasible (no data)
  → DO NOT PLAN
```

---

## 26. Final Gate

```
HVA-03 STATUS = CONDITIONAL

ARCHITECTURE_FEASIBILITY = MEDIUM
  → Mechanically feasible (Phase 1 can be built)
  → Data-limited (Phase 2 blocked by lack of future corpus + experiment authorization)
  → Cannot prove Learning at current evidence levels

PRIMARY_BOTTLENECK = Feedback Generalization (Stability-Novelty Paradox)
  → Architecture provides BOUNDING mechanism, but cannot resolve semantic boundaries
  → SIG-02/08 boundary is semantic (sentence vs paragraph) → may be permanently UNKNOWN

SECONDARY_BOTTLENECK = Future Validation (0 independent future cases)
  → Architecture is ready for replay
  → But no new corpus available
  → Cannot prove R5/R6 without future cases

REUSABLE_SIGNAL_SUPPORTED = INSUFFICIENT_EVIDENCE
  → Architecture provides the mechanism
  → But current data (HVA-02) shows R5=0, R6=0
  → Architecture cannot create data

CURRENT_LEARNING_LEVEL = L3 (Candidate Discovery — unchanged)
  → Phase 1 target: L3+ (Evidence-Linked Candidate)
  → Phase 2 target: L4 (Human-Validated) — ONLY if Phase 1 succeeds AND data available

MINIMAL_PROTOTYPE = P6 FeedbackRecord + P7 SignalCandidate + Counterexample Search + P4 L0-L1
  → Phase 1 scope only
  → Offline, no runtime, no experiment

HUMAN_BOUNDARY = Human retains ALL semantic authority
  → Machine: aggregation, compression, structural comparison, search
  → Human: validation, boundary definition, UNKNOWN judgment, registration
  → NO authority leakage (ValidatedSignal has FORBIDDEN fields)

AUTOMATION_RISK = LOW
  → No auto-validation (Human Boundary required)
  → No auto-upgrade (Counterexample Search mandatory)
  → No auto-rule (FORBIDDEN fields)
  → No auto-runtime (research prototype only)

AUTHORITY_LEAKAGE_RISK = LOW
  → ValidatedSignal schema forbids decision/routing/score/confidence
  → Schema validation rejects authority fields
  → Human retains final registration authority

IMPLEMENTATION_REQUIRED = NOT_YET
  → Phase 0 (schema) can start immediately
  → Phase 1 (prototype) can start after Phase 0
  → Phase 2 requires authorization + data

IMPLEMENTATION_AUTHORIZED = FALSE
EXPERIMENT_AUTHORIZED = FALSE

DICE_CORE_MODIFICATION = NO
P1_P7_MODIFICATION = NO
TLD_MODIFICATION = NO
IS11_MODIFICATION = NO
M_B_MODIFICATION = NO
GT_MODIFICATION = NO
LLM = NO
NEW_OBSERVATION = NO
NEW_MODULE = NO
NEW_ENGINE = NO
RUNTIME_CHANGE = NO
CAPABILITY_CHANGE = NO

FROZEN_BASELINE = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d)
FROZEN_EXPERIMENT = INTACT
PRODUCTION = FALSE
STOP = TRUE
```

---

## 27. Final Answer (10 Sentences)

> **如果现在真的要把这个系统做出来，第一版到底应该做什么、绝对不能做什么、Human 到底负责什么、Machine 到底负责什么。**

1. 第一版只做 FeedbackRecord 捕获和 Evidence Pack L0-L1 重新设计——把 Human 的判断和它依赖的 Evidence 结构化地关联起来，让 Human 看第一层就能判断而不是从十几个技术字段重建信息。

2. 绝对不做任何自动规则生成、自动 Signal 升级、自动决策替换、自动 Runtime 集成——任何 Signal 必须经过 Counterexample Search 和 Human Boundary Validation 才能成为 ValidatedSignal。

3. Human 负责三件事：Case Judgment（KEEP/MERGE/UNKNOWN）、Signal Validation（成立/不成立/不确定）、Boundary Validation（适用/不适用/需要限定/UNKNOWN）——不负责找 Evidence、整理 Evidence、找 Pattern、写 Rule。

4. Machine 负责四件事：Evidence 聚合（P1）、Evidence 压缩为 Pack（P4）、结构性 Evidence Signature 提取和 Signal Candidate 形成（P7）、Counterexample 主动搜索——不做任何语义判断、不写 Rule、不决定 Runtime 行为。

5. Case Selection 必须从几何模糊度导向改为 Review Value 导向，用 6 个 Value Dimensions（Machine Error Risk / Evidence Uncertainty / Boundary Potential / Feedback Value / Reuse Potential / Coverage Diversity）加 Safety Constraints（TABLE≤50%、PROSE≥15%、Type A≤30%）替代当前 88% TABLE、53% 浪费的选择机制。

6. Evidence Pack 分 5 层渐进展示，L1 必须包含 different_cell + period/capital + machine_decision + insufficiency_flags，L3 必须包含 counterevidence——不包含任何 recommendation/cue/hint，防止 automation bias。

7. 任何 Signal Candidate 必须经过 Counterexample Search——发现反例后进入 Human Boundary Review，不得直接升级；ceiling effect（0 反例）也不能 auto-validate，因为"没有反例"不等于"普遍成立"。

8. Stability-Novelty Paradox 不通过选择稳定或新颖来解决，而是通过 BOUNDING——每个 Signal 限定结构化适用范围，超范围自动 OUT_OF_SCOPE；如果无法找到结构化 scope（如 SIG-02 的句子边界是语义问题），Signal 保持 UNKNOWN。

9. Learning 成功标准不是 Case 数量下降，而是 Validated Signal 在 ≥5 个独立新 Case 上成立（TPR≥80%、FPR≤10%）、跨文档验证、Decision Quality 不降、Human Review 真正下降——当前 R5=0、R6=0，架构提供了达成 R5/R6 的机制但不保证结果。

10. 当前 Learning Level = L3，Phase 1 目标是证明 Feedback→Evidence Link→Signal Candidate→Counterexample 链路机械可行（用 HVA-02 的 8 个已有 Candidate 验证），Phase 2 才考虑 Human Validation 和 Future Replay——但 Phase 2 需要新语料和实验授权，当前均不具备。

`STOP = TRUE`。
