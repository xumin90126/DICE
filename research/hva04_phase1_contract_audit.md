# HVA-04 Phase 1 Minimal Prototype Contract Audit

**Date**: 2026-09-17
**Mode**: READ-ONLY CONTRACT AUDIT / NO CODE / NO IMPLEMENTATION / FROZEN INTACT / STOP
**Predecessors**: HVA-01, HVA-02, HVA-03

---

## 1. Executive Summary

```
HVA-04 STATUS = CONDITIONAL

  Phase 1 Prototype is NOT ready for implementation.
  4 CONTRACT GAPS identified that must be resolved before any code.

CONTRACT GAPS FOUND:
  GAP-1: content_type field does not exist in ANY data file (DERIVED only)
  GAP-2: P2 geometry fields (h_gap, dy, same_style, etc.) exist ONLY in L5
         experiment_cases, NOT in IS-11 machine evaluation
  GAP-3: P7 has NO TLD fields (is_in_table, different_cell) — cross-corpus
         Evidence Signature matching is PARTIAL only
  GAP-4: L5 experiment has_tld=False for 9/30 cases where machine_eval HAS
         TLD data → Evidence Pack must read from machine_eval, NOT L5 cues

MINIMAL_PROTOTYPE = C (FeedbackRecord + Evidence Pack + Evidence Signature + SignalCandidate)

  NOT D (which adds Counterexample Search).
  Counterexample Search is feasible but adds P7 cross-corpus complexity
  that is NOT needed to prove the core hypothesis.
  Core hypothesis = "Feedback can be linked to Evidence and grouped by
  structural similarity."
  This is proven by C. Counterexample Search is Phase 1.5.

P4_CONTRACT = GAP (content_type + P2 geometry source unresolved)
P6_CONTRACT = READY (all fields available from existing data)
P7_CONTRACT = GAP (Evidence Signature fields need scoping to available data)
COUNTEREXAMPLE_CONTRACT = GAP (P7 lacks TLD fields for full Signature match)

AUTHORITY_BOUNDARY = PASS
SEMANTIC_LEAKAGE = 0 (with one clarification needed on different_cell)

STOP = TRUE
```

---

## 2. Current Architecture Gap (Contract Perspective)

HVA-03 proposed 7 Parts. Phase 1 scope = P4 + P6 + P7 + Counterexample Search.

### What HVA-03 Specified vs What Data Actually Contains

| HVA-03 Field | HVA-03 Source | Actual Data Source | Status |
|---|---|---|---|
| text_a | P1 | GT (text_a) + machine_eval (text_a) + L5 (fields.text_a) | AVAILABLE |
| text_b | P1 | GT (text_b) + machine_eval (text_b) + L5 (fields.text_b) | AVAILABLE |
| page | P1 | machine_eval (page) + L5 (fields.page_number) | AVAILABLE |
| document_id | P1 | machine_eval (document_id) + L5 (fields.doc_id) | AVAILABLE |
| content_type | HVA-03 derived | **NOT IN ANY FILE** | **GAP-1** |
| is_in_table | TLD | machine_eval (is11_observation.is_in_table) | AVAILABLE (IS-11 only) |
| different_cell | TLD | machine_eval (is11_observation.different_cell) | AVAILABLE (IS-11 only) |
| is01_a | IS-01 | machine_eval (experimental_c.is01_a) + P7 (decision_evidence.is01_a) | AVAILABLE |
| is02_b | IS-02 | machine_eval (experimental_c.is02_b) + P7 (decision_evidence.is02_b) | AVAILABLE |
| machine_decision | IS-11 | machine_eval (experimental_c.decision) | AVAILABLE |
| machine_outcome | IS-11 | machine_eval (experimental_c.outcome) | AVAILABLE |
| h_gap | P2 | **L5 experiment_cases ONLY** | **GAP-2** |
| dy | P2 | **L5 experiment_cases ONLY** | **GAP-2** |
| same_style | P2 | **L5 experiment_cases ONLY** | **GAP-2** |
| width_a/b | P2 | **L5 experiment_cases ONLY** | **GAP-2** |
| style_sig_a/b | P2 | **L5 experiment_cases ONLY** | **GAP-2** |
| text_a_ends_period | P1 derived | Derivable from text_a (GT/machine_eval) | DERIVED — OK |
| text_b_starts_capital | P1 derived | Derivable from text_b (GT/machine_eval) | DERIVED — OK |
| reviewer_a_label | GT | GT (reviewer_a_label) | AVAILABLE |
| reviewer_b_label | GT | GT (reviewer_b_label) | AVAILABLE |
| final_label | GT | GT (final_label) | AVAILABLE |
| gt_level | GT | GT (gt_level) | AVAILABLE |
| adjudication_rationale | GT | GT (adjudication_rationale) | AVAILABLE |
| human_decision | L5 | L5 (decision) | AVAILABLE |
| decision_time_ms | L5 | L5 (decision_time_ms) | AVAILABLE |
| expansion_count | L5 | L5 (expansion_count) | AVAILABLE |
| levels_viewed | L5 | L5 (levels_viewed) | AVAILABLE |
| expanded_fields | L5 | L5 (expanded_fields) | AVAILABLE (4% non-null) |
| boundary_class | P7 | P7 (boundary_class) | AVAILABLE (P7 only) |
| semantic_gt | P7 | P7 (semantic_gt) | AVAILABLE (P7 only) |

### 4 Contract Gaps

```
GAP-1: content_type
  HVA-03 uses content_type (TABLE_NUMERIC / TABLE_TEXT / PROSE / FIGURE)
  in Evidence Pack L0 and Evidence Signature.
  content_type does NOT exist in GT, machine_eval, L5, or P7.
  It was manually derived in HVA-01 case profiles.
  RESOLUTION: Define derivation rule from existing fields:
    is_in_table=True + is01_a=True → TABLE_NUMERIC
    is_in_table=True + is01_a=False → TABLE_TEXT
    is_in_table=False + text_a_ends_period → PROSE
    text_a starts with "Fig" → FIGURE
  STATUS: DERIVABLE but rule must be documented, not assumed.

GAP-2: P2 geometry fields (h_gap, dy, same_style, width_a/b, style_sig_a/b)
  HVA-03 Evidence Pack L2 uses these fields.
  They exist ONLY in L5 experiment_cases (30 cases).
  They do NOT exist in IS-11 machine_eval (45 cases).
  15 IS-11 cases not in L5 have NO P2 geometry data.
  RESOLUTION OPTIONS:
    a) Read from L5 experiment_cases for 30 L5 cases; mark NOT_AVAILABLE for 15 others
    b) Recompute from P2 observation (requires P2 module access — Phase 1 should NOT couple to P2)
    c) Drop L2 from Phase 1 (L0-L1 only)
  RECOMMENDED: Option (c) — Drop L2 from Phase 1.

GAP-3: P7 lacks TLD fields
  P7 has 0/69 cases with is_in_table or different_cell.
  Counterexample Search across P7 can ONLY match on:
    is01_a, is02_b, text_a_ends_period, text_b_starts_capital
  It CANNOT match on is_in_table, different_cell.
  This means SIG-01 (different_cell-based) CANNOT be counterexample-searched on P7.
  Only SIG-02 (period+capital-based) CAN be counterexample-searched on P7.
  RESOLUTION: Document this limitation. Phase 1 Counterexample Search is PARTIAL.

GAP-4: L5 has_tld vs machine_eval TLD data inconsistency
  L5 experiment cases have has_tld=False for 9/30 cases.
  For these 9 cases, L5 cues show TLD is_in_table=None, different_cell=None.
  BUT machine_eval has TLD data for ALL 45 cases (including these 9).
  Example: AMB-032 — L5 has_tld=False, but machine_eval is_in_table=True, different_cell=True.
  RESOLUTION: Evidence Pack must read TLD data from machine_eval (is11_observation),
    NOT from L5 experiment_cases (cues). L5 cues are experiment presentation, not ground truth.
```

---

## 3. Audit P4 Evidence Pack

### 3.1 Input Field Audit

| Field | Source | Meaning | Authority Level | Required? |
|---|---|---|---|---|
| text_a | GT / machine_eval | Text fragment A | Evidence Fact (P1) | REQUIRED |
| text_b | GT / machine_eval | Text fragment B | Evidence Fact (P1) | REQUIRED |
| page | machine_eval | Page number | Evidence Fact (P1) | REQUIRED |
| document_id | machine_eval | Document ID | Evidence Fact (P1) | REQUIRED |
| content_type | DERIVED | Content classification | **Machine-derived** | REQUIRED (but GAP-1) |
| is_in_table | machine_eval is11_observation | TLD table detection | **Machine-derived (TLD)** | REQUIRED |
| different_cell | machine_eval is11_observation | TLD cell comparison | **Machine-derived (TLD)** | REQUIRED |
| is01_a | machine_eval experimental_c | IS-01 number detection | Machine-derived (IS-01) | REQUIRED |
| is02_b | machine_eval experimental_c | IS-02 text detection | Machine-derived (IS-02) | REQUIRED |
| machine_decision | machine_eval experimental_c | IS-11 decision | **Machine Interpretation** | REQUIRED |
| machine_outcome | machine_eval experimental_c | IS-11 outcome vs GT | **Machine Interpretation** | AUDIT_ONLY |
| text_a_ends_period | DERIVED from text_a | Period at end of A | Evidence Fact (derived) | REQUIRED |
| text_b_starts_capital | DERIVED from text_b | Capital at start of B | Evidence Fact (derived) | REQUIRED |
| h_gap | L5 experiment_cases | Horizontal gap | Evidence Fact (P2) | **NOT_REQUIRED (GAP-2)** |
| dy | L5 experiment_cases | Vertical offset | Evidence Fact (P2) | **NOT_REQUIRED (GAP-2)** |
| same_style | L5 experiment_cases | Style match | Evidence Fact (P2) | **NOT_REQUIRED (GAP-2)** |
| width_a/b | L5 experiment_cases | Text width | Evidence Fact (P2) | **NOT_REQUIRED (GAP-2)** |
| style_sig_a/b | L5 experiment_cases | Style signature | Evidence Fact (P2) | **NOT_REQUIRED (GAP-2)** |
| reviewer_a_label | GT | Reviewer A judgment | Human Judgment | AUDIT_ONLY |
| reviewer_b_label | GT | Reviewer B judgment | Human Judgment | AUDIT_ONLY |
| final_label | GT | Final GT label | Human Judgment | AUDIT_ONLY |
| gt_level | GT | GT confidence level | Metadata | AUDIT_ONLY |
| adjudication_rationale | GT | Adjudication reason | Human Judgment | AUDIT_ONLY |

### 3.2 Semantic Leakage Check

| Field | Classification | Leakage? | UI Display |
|---|---|---|---|
| text_a | Evidence Fact (P1) | NO | Raw text |
| text_b | Evidence Fact (P1) | NO | Raw text |
| is_in_table | **Machine-derived (TLD)** | NO (structural) | "TLD: In Table: YES" |
| different_cell | **Machine-derived (TLD)** | NO (structural) | "TLD: Different Cell: YES" |
| is01_a | Machine-derived (IS-01) | NO (structural) | "IS-01: Number: YES" |
| is02_b | Machine-derived (IS-02) | NO (structural) | "IS-02: Text: YES" |
| machine_decision | **Machine Interpretation** | **POTENTIAL** | Must show as "Machine Decision" NOT "Correct Answer" |
| machine_outcome | Machine Interpretation | **POTENTIAL** | AUDIT_ONLY — do NOT show to Human in L1 |
| text_a_ends_period | Evidence Fact (derived) | NO | "Ends with period: YES" |
| text_b_starts_capital | Evidence Fact (derived) | NO | "Starts with capital: YES" |
| content_type | **Machine-derived** | **POTENTIAL** | Must show as "Classified as" NOT "Is" |

**Semantic Leakage Assessment:**

```
different_cell = true
  Classification: B. Existing Machine Interpretation (TLD-derived structural fact)
  NOT A (pure geometry) — TLD applies detection algorithm to derive this
  NOT C (semantic judgment) — it's structural, not semantic
  
  UI must show: "TLD Detection: Different Cell = YES"
  NOT: "Correct Answer: Different Cell"
  NOT: "These are in different cells" (semantic claim)

machine_decision = KEEP_SEPARATE
  Classification: C. Machine Interpretation (IS-11 decision)
  This IS semantic leakage risk.
  UI must show: "Machine Decision: KEEP_SEPARATE"
  NOT: "Correct Answer: KEEP_SEPARATE"
  NOT: "Recommended: KEEP_SEPARATE"
  
  Phase 1 recommendation: Show machine_decision in L1 but clearly labeled as
  "Machine Decision (may be wrong)" not as guidance.

content_type = TABLE_NUMERIC
  Classification: B. Machine-derived (from is_in_table + is01_a)
  UI must show: "Classified as: TABLE_NUMERIC"
  NOT: "This is a table with numbers" (semantic claim)

SEMANTIC_LEAKAGE = 0 (with UI labeling requirements above)
```

### 3.3 Progressive Disclosure Audit

| Layer | Human Question | Fields | Expansion Trigger | Needed in Phase 1? |
|---|---|---|---|---|
| L0 | "What is this case?" | text_a, text_b, page, doc, content_type | Default visible | **YES** |
| L1 | "What evidence helps me decide?" | is_in_table, different_cell, is01_a, is02_b, ends_period, starts_capital, machine_decision, insufficiency | Default visible | **YES** |
| L2 | "What are the geometric details?" | h_gap, dy, same_style, width, style_sig | Human expands | **NO (GAP-2)** |
| L3 | "Are there contradictions?" | evidence_conflict, adjudicated, reviewer_disagreement | Human expands | **NO** |
| L4 | "Full audit trail" | raw TLD, raw P1, hashes | Audit only | **NO** |

**Phase 1 Decision: L0 + L1 only.**

```
Rationale:
  L2 requires P2 geometry fields that are NOT in machine_eval (GAP-2).
  L3 requires cross-case search (Counterexample Search — Phase 1.5).
  L4 is audit-only, not needed for prototype.
  
  L0 + L1 contains ALL decision-relevant evidence:
    - text_a, text_b (what are the fragments?)
    - is_in_table, different_cell (TLD structural result)
    - is01_a, is02_b (binary signal)
    - ends_period, starts_capital (sentence boundary indicator)
    - machine_decision (what machine decided)
    - insufficiency (is evidence incomplete?)
  
  This is sufficient to test the core hypothesis:
    "Can Human make a judgment with structured L0-L1 evidence
     that is faster and more accurate than raw field dump?"
```

---

## 4. Audit P6 FeedbackRecord

### 4.1 Minimal Field Contract

| Field | Type | Required? | Source | Rationale |
|---|---|---|---|---|
| record_id | str | REQUIRED | Generated | Unique identifier |
| case_id | str | REQUIRED | Input | Links to case |
| human_id | str | REQUIRED | Input | Links to human reviewer |
| human_decision | str | REQUIRED | Human input | KEEP_SEPARATE / MERGE / UNKNOWN |
| evidence_snapshot | dict | REQUIRED | Frozen from machine_eval | Evidence state at decision time |
| evidence_viewed | dict | REQUIRED | From interaction log | What human actually saw |
| provenance | dict | REQUIRED | From system | Audit trail |
| evidence_relations | list | **DERIVED** | Auto-extracted from snapshot | Structural relationships |
| human_rationale | str | **OPTIONAL** | Human input (if provided) | Not required, not depended on |
| experiment_condition | str | OPTIONAL | From experiment | A / B1 / B2 |

### 4.2 evidence_snapshot Minimal Fields

```python
evidence_snapshot = {
    # From machine_eval (is11_observation)
    "is_in_table": bool,
    "different_cell": bool,
    # From machine_eval (experimental_c)
    "is01_a": bool,
    "is02_b": bool,
    "machine_decision": str,
    # Derived from text_a/text_b
    "text_a_ends_period": bool,
    "text_b_starts_capital": bool,
    # From machine_eval (metadata)
    "document_id": str,
    "page": int,
    "content_type": str,  # DERIVED (GAP-1)
}
```

### 4.3 Does Human Need to Write Rationale?

```
NO.

L5 data shows: 96% of judgments had NO expansion, 91% of GT rationales are
formulaic ("different table columns"). Rationale is not a reliable signal source.

Human does NOT write rationale.
Machine constructs Signal Candidate from:
  Human Decision + Evidence Context (evidence_snapshot)

If rationale is provided (optional), it is recorded but NOT used for
Signal Candidate formation.
```

### 4.4 evidence_viewed Fields

```python
evidence_viewed = {
    "levels_viewed": [int],  # e.g. [0, 1]
    "fields_expanded": [str],  # from L5: expanded_fields (4% non-null)
    "decision_time_ms": int,  # from L5: decision_time_ms
    "expansion_count": int,  # from L5: expansion_count
}
```

### 4.5 FeedbackRecord Complete Contract

```python
FeedbackRecord = {
    "record_id": str,           # REQUIRED — generated
    "case_id": str,             # REQUIRED — from input
    "human_id": str,            # REQUIRED — from input
    "human_decision": str,      # REQUIRED — KEEP_SEPARATE / MERGE / UNKNOWN
    "evidence_snapshot": dict,  # REQUIRED — frozen from machine_eval
    "evidence_viewed": dict,    # REQUIRED — from interaction log
    "provenance": {
        "tld_hash": str,        # REQUIRED — "022f5c21e872ad9e"
        "gt_hash": str,         # REQUIRED — "7349963d0d23b5ef"
        "timestamp": str,       # REQUIRED — ISO format
        "experiment_condition": str,  # OPTIONAL — A / B1 / B2
    },
    "evidence_relations": list, # DERIVED — auto-extracted, not human input
    "human_rationale": str,     # OPTIONAL — not required, not depended on
    
    # FORBIDDEN:
    # rule, pattern, inference, conclusion
    # suggested_signal, signal_id
    # confidence, score, weight
}
```

**P6_CONTRACT = READY.** All required fields are available from existing data.

---

## 5. Audit Evidence Signature

### 5.1 What is Evidence Signature?

```
Evidence Signature = structural fingerprint of evidence combination
  = a dict of boolean/enum fields from evidence_snapshot

NOT:
  ❌ semantic label
  ❌ rule
  ❌ classification
  ❌ embedding similarity score
  ❌ confidence
  ❌ text content matching
```

### 5.2 Which Existing Fields Can Form Signature?

| Field | Type | Signature-eligible? | Available in IS-11? | Available in P7? |
|---|---|---|---|---|
| is_in_table | bool | YES | YES (machine_eval) | **NO** |
| different_cell | bool | YES | YES (machine_eval) | **NO** |
| is01_a | bool | YES | YES | YES |
| is02_b | bool | YES | YES | YES |
| text_a_ends_period | bool | YES | YES (derived) | YES (derived) |
| text_b_starts_capital | bool | YES | YES (derived) | YES (derived) |
| content_type | enum | YES | DERIVED (GAP-1) | DERIVED |
| machine_decision | enum | **NO** | YES | YES |
| h_gap | float | NO (continuous) | L5 only (GAP-2) | NO |

### 5.3 Signature = Evidence Representation or Semantic Interpretation?

```
Evidence Signature fields:
  is_in_table: bool — "TLD detected a table" — STRUCTURAL
  different_cell: bool — "TLD detected different cells" — STRUCTURAL
  is01_a: bool — "IS-01 regex matched number" — STRUCTURAL
  is02_b: bool — "IS-02 found alpha > 2 chars" — STRUCTURAL
  text_a_ends_period: bool — "text_a ends with '.'" — STRUCTURAL
  text_b_starts_capital: bool — "text_b starts with uppercase" — STRUCTURAL

ALL fields are structural facts (boolean), NOT semantic interpretations.

Does Signature cross Semantic Boundary?
  NO. Signature is a combination of structural boolean features.
  It does NOT interpret what the combination MEANS.
  It does NOT assign a semantic label.
  It does NOT produce a decision.

Example:
  Signature = {is_in_table:True, different_cell:True, is01_a:True}
  This is 3 structural facts. It does NOT say "this is a table with numbers
  that should be separated." That interpretation is Human's job.
```

### 5.4 Phase 1 Evidence Signature (Minimal)

```python
EvidenceSignature = {
    "is_in_table": bool,          # from machine_eval
    "different_cell": bool,       # from machine_eval
    "is01_a": bool,               # from machine_eval
    "is02_b": bool,               # from machine_eval
    "text_a_ends_period": bool,   # derived from text_a
    "text_b_starts_capital": bool, # derived from text_b
    "content_type": str,          # DERIVED (GAP-1)
}
```

**Note**: This signature has 7 fields. For P7 cross-corpus matching, only 5 fields are available (no is_in_table, different_cell). This is documented as a known limitation.

### 5.5 Signature Boundary Check

```
Does Evidence Signature cross Semantic Boundary?

Check 1: Does Signature contain semantic labels?
  NO. All fields are boolean or enum (structural).

Check 2: Does Signature produce decisions?
  NO. Signature is a fingerprint, not a classifier.

Check 3: Does Signature interpret evidence?
  NO. It records WHAT evidence exists, not WHAT IT MEANS.

Check 4: Could two semantically different cases have the same Signature?
  YES. Example: {is_in_table:False, is01_a:False, is02_b:True,
  text_a_ends_period:True, text_b_starts_capital:True}
  This signature matches both:
    - AMB-375 (sentence boundary → KEEP_SEPARATE)
    - P7 IND-AMB-049 (mid-sentence period → MERGE)
  Same signature, different semantic meaning.
  → Signature does NOT resolve semantic ambiguity.
  → That's correct: Human resolves it in Boundary Validation.

CONCLUSION: Evidence Signature does NOT cross Semantic Boundary.
```

---

## 6. Audit SignalCandidate

### 6.1 Minimal State Machine

```
DISCOVERED
  ↓ (≥2 FeedbackRecords with same Evidence Signature)
REPEATED
  ↓ (independence check passes: ≥2 independent doc-page groups)
INDEPENDENCE_VERIFIED
  ↓ (Counterexample Search executed — Phase 1.5)
COUNTEREXAMPLE_CHECKED
  ↓ (counterexamples found OR ceiling effect detected)
BOUNDARY_REVIEW_REQUIRED
  ↓ (Human Boundary Validation — Phase 2)
[VALIDATED / REJECTED / UNKNOWN]
  ↓ (Phase 2 only — NOT in Phase 1)
```

### 6.2 Phase 1 Allowed States

```
Phase 1 allows:
  DISCOVERED
  REPEATED
  INDEPENDENCE_VERIFIED
  COUNTEREXAMPLE_CHECKED (if Phase 1 includes Counterexample Search)
  BOUNDARY_REVIEW_REQUIRED

Phase 1 does NOT allow:
  AUTO_VALIDATED        ← FORBIDDEN
  VALIDATED             ← FORBIDDEN (requires Human Boundary Validation)
  REGISTERED            ← FORBIDDEN (requires registration)
  ACTIVE                ← FORBIDDEN (requires runtime)
  RETIRED               ← FORBIDDEN
```

### 6.3 SignalCandidate Phase 1 Contract

```python
SignalCandidate = {
    "signal_id": str,
    "evidence_signature": dict,      # from P7 Evidence Signature
    "source_cases": [str],           # case_ids
    "source_feedback_records": [str], # record_ids
    "human_decisions": [str],        # KEEP_SEPARATE / MERGE / UNKNOWN
    "decision_consistency": bool,    # all same decision?
    "has_conflict": bool,            # reviewer disagreement?
    "independence": {
        "independent_count": int,    # unique doc-page groups
        "total_count": int,
        "independence_ratio": float,
        "same_page_clusters": dict,  # {doc_page: count}
    },
    "recurrence": {
        "same_doc": int,
        "cross_doc": int,
    },
    "engagement_stats": {
        "snap_count": int,           # decision_time < 3000ms
        "deep_count": int,           # decision_time >= 3000ms
    },
    "status": str,  # DISCOVERED / REPEATED / INDEPENDENCE_VERIFIED / BOUNDARY_REVIEW_REQUIRED
    "counterexample_result": None,   # filled if Counterexample Search run
    
    # FORBIDDEN in Phase 1:
    # validated, registered, active, retired
    # rule, decision_function, confidence, score
}
```

### 6.4 Candidate ≠ Rule Check

```
SignalCandidate contains:
  - evidence_signature (structural facts)
  - source_cases (history)
  - human_decisions (what humans said)
  - independence (statistics)
  - status (state machine)

SignalCandidate does NOT contain:
  - rule (no IF-THEN)
  - decision_function (no f(x) → y)
  - confidence (no probability)
  - score (no ranking)
  - recommendation (no "should")
  - override (no authority)

Candidate = "Here are N cases with similar evidence and similar decisions."
Not = "When you see this evidence, decide this way."
```

---

## 7. Audit Counterexample Search

### 7.1 Search Input

```
Input: SignalCandidate (evidence_signature + human_decisions)
       + All records (IS-11 machine_eval + P7 machine_results)
```

### 7.2 Search Unit

```
Search Unit = Evidence Signature match

For each record in the search pool:
  1. Extract Evidence Signature from record
  2. Compare with target Signature
  3. If match: check if decision/GT differs

NOT:
  ❌ case (too granular, no structural comparison)
  ❌ document (too coarse)
  ❌ page (not independent)
  ❌ embedding similarity (requires model — NOT ALLOWED)

YES:
  ✓ evidence signature (structural boolean comparison)
```

### 7.3 Search Method

```
Method: Exact boolean match on Evidence Signature fields.

For IS-11 (45 cases):
  Signature fields available: is_in_table, different_cell, is01_a, is02_b,
  text_a_ends_period, text_b_starts_capital (6 fields)
  → Can match on ALL 6 fields.

For P7 (69 cases):
  Signature fields available: is01_a, is02_b, text_a_ends_period,
  text_b_starts_capital (4 fields only — NO is_in_table, different_cell)
  → Can match on 4 fields only.
  → PARTIAL match (GAP-3).

Does this need new model / LLM / embedding / detector?
  NO. It needs only boolean field comparison.
  All fields are already computed (is01_a, is02_b in P7 decision_evidence;
  text_a/text_b in P7 for period/capital derivation).

ALLOWED.
```

### 7.4 Search Output

```
Output: CounterexampleSearchResult = {
    "signal_id": str,
    "search_pool": "IS-11" | "IS-11+P7" | "IS-11+P7+Pilot",
    "matches_found": int,
    "counterexamples": [{
        "case_id": str,
        "document_id": str,
        "page": int,
        "evidence_signature": dict,
        "decision": str,          # human_decision or semantic_gt
        "decision_source": str,   # "HUMAN" or "GT"
        "signature_match_fields": [str],  # which fields matched
        "signature_missing_fields": [str], # which fields unavailable (e.g. is_in_table for P7)
    }],
    "unknown_matches": int,
    "ceiling_effect": bool,       # 0 counterexamples AND 0 unknowns
    "cross_document": bool,
    "search_completeness": "FULL" | "PARTIAL",  # PARTIAL if P7 missing TLD fields
}
```

### 7.5 Output Categories

```
POSITIVE: Same signature, same decision → supports signal
NEGATIVE: Same signature, different decision → counterexample
UNKNOWN: Same signature, decision=UNKNOWN → ambiguous
CONFLICT: Same signature, reviewer disagreement → boundary case
CEILING: 0 counterexamples AND 0 unknowns → cannot determine boundary
```

---

## 8. Ceiling Effect Audit

### 8.1 State Machine Enforcement

```
Question: Is "0 counterexamples = validated" truly prevented?

State machine:
  COUNTEREXAMPLE_CHECKED
    ↓
  if counterexamples_found > 0:
    → BOUNDARY_REVIEW_REQUIRED (counterexamples must be resolved)
  if counterexamples_found == 0 AND unknown_matches == 0:
    → CEILING_EFFECT
    → status = CEILING_EFFECT
    → MUST remain BOUNDARY_REVIEW_REQUIRED
    → CANNOT auto-promote to VALIDATED
  if counterexamples_found == 0 AND unknown_matches > 0:
    → PARTIAL_CEILING
    → status = BOUNDARY_REVIEW_REQUIRED
    → Human sees unknowns → likely UNKNOWN

Key: CEILING_EFFECT is a STATUS, not a promotion.
  It means "we cannot find counterexamples, but that doesn't mean they don't exist."
  It forces Human Boundary Review, where Human sees "0 counterexamples"
  and must decide:
    - APPLICABLE (risky — no counterexamples found, but ceiling effect)
    - UNKNOWN (safe — cannot determine)
    - NEEDS_SCOPING (attempts to bound)

In Phase 1: status stops at BOUNDARY_REVIEW_REQUIRED.
  No promotion possible. No VALIDATED state reachable.
```

### 8.2 Safest State for Ceiling

```
SAFEST_CEILING_STATE = INSUFFICIENT_EVIDENCE

  When ceiling_effect=True:
    status = INSUFFICIENT_EVIDENCE
    NOT VALIDATED
    NOT PROMOTED
    message = "0 counterexamples found. Cannot determine boundary.
               Insufficient evidence for validation."

  This is safer than CEILING_EFFECT because:
    - CEILING_EFFECT might imply "ceiling reached, signal works"
    - INSUFFICIENT_EVIDENCE clearly says "we don't know"
    - Prevents any misinterpretation as positive validation

  Phase 1 recommendation: Use INSUFFICIENT_EVIDENCE for ceiling cases.
```

---

## 9. Audit Case Selection Constraints

### 9.1 Constraint Classification

| Constraint | Value | Classification | Evidence |
|---|---|---|---|
| max_table_pct | 0.50 | **Design heuristic** | HVA-01: current 88% TABLE → 50% is a reduction target, not experimentally validated |
| min_prose_pct | 0.15 | **Design heuristic** | HVA-01: current 7% → 15% is a minimum for diversity, not validated |
| max_type_a_pct | 0.30 | **Design heuristic** | HVA-01: current 53% → 30% is a waste reduction target, not validated |
| min_merge_count | 2 | **Observed evidence** | HVA-02: IS-11 has 2 MERGE cases → minimum to maintain current level |

### 9.2 Recommendation

```
These constraints are NOT experimentally validated.
They are design heuristics based on HVA-01 observations.

DO NOT write them as hard rules.

Write as:
  "selection_constraint_candidate" or "sampling_guardrail"

And retain adjustability:
  constraints = {
    "max_table_pct": {"value": 0.50, "type": "guardrail", "adjustable": True,
                      "basis": "HVA-01 observed 88% TABLE bias"},
    "min_prose_pct": {"value": 0.15, "type": "guardrail", "adjustable": True,
                      "basis": "HVA-01 observed 7% PROSE underrepresentation"},
    "max_type_a_pct": {"value": 0.30, "type": "guardrail", "adjustable": True,
                       "basis": "HVA-01 observed 53% Type A waste"},
    "min_merge_count": {"value": 2, "type": "minimum", "adjustable": True,
                        "basis": "HVA-02 observed 2 MERGE in IS-11"},
  }
```

### 9.3 Case Selection Authority Check

```
Question: Does Case Selection produce new Selection Authority?

Case Selector CAN:
  - Choose which cases Human reviews
  - Apply guardrails for diversity
  - Prioritize by review value dimensions

Case Selector CANNOT:
  - Judge whether a case is correct
  - Decide the case answer
  - Decide whether a Signal is valid
  - Decide Runtime behavior

Proof: Case Selection ≠ Semantic Decision
  - Selection outputs SelectedCase (case_id + review_value + reason)
  - Selection does NOT output decision, label, or judgment
  - Selection only filters and prioritizes — it does not interpret
  - Human still makes all semantic decisions

Case Selection = SAMPLING (structural), not JUDGING (semantic).
→ NO new Selection Authority produced.
```

---

## 10. Audit Human Boundary

### 10.1 Human's Only Actions

```
1. Case Judgment
   [KEEP_SEPARATE] [MERGE] [UNKNOWN]

2. Signal Candidate Validation
   [SUPPORTED] [UNSUPPORTED] [UNKNOWN]

3. Boundary Validation
   [IN_SCOPE] [OUT_OF_SCOPE] [NEEDS_SCOPING] [UNKNOWN]
```

### 10.2 Machine Output Substitution Check

| Machine Output | Does it substitute Human Semantic Judgment? | Check |
|---|---|---|
| Evidence Pack L0-L1 | NO — presents facts, no recommendation | PASS |
| Evidence Signature | NO — structural fingerprint, no interpretation | PASS |
| SignalCandidate | NO — groups cases, no decision | PASS |
| Counterexample Search | NO — finds facts, no modification | PASS |
| machine_decision in L1 | **POTENTIAL** — shows Machine's decision | **CHECK** |
| content_type in L0 | **POTENTIAL** — classified by Machine | **CHECK** |

### 10.3 machine_decision and content_type Handling

```
machine_decision in Evidence Pack L1:
  Risk: Human might anchor on Machine's decision (automation bias).
  HVA-02 found: B2 cue WRONG on AMB-462/313, but Human overrode (safe).
  
  Phase 1 handling:
    - Show machine_decision in L1, clearly labeled "Machine Decision (may be wrong)"
    - Do NOT show as "Recommended" or "Suggested"
    - Do NOT show machine_outcome (TN/FP/etc.) — this reveals correctness, which biases Human
    
  This is NOT semantic substitution because:
    - Human can override (L5 data shows 2 overrides)
    - Human sees it as one data point, not as guidance
    - Evidence Pack presents it alongside other evidence, not as conclusion

content_type in Evidence Pack L0:
  Risk: Human might anchor on "TABLE_NUMERIC" classification.
  
  Phase 1 handling:
    - Show as "Classified as: TABLE_NUMERIC"
    - Do NOT show as "This is a table" (semantic claim)
    - Mark as machine-derived, not ground truth
    
  This is NOT semantic substitution because:
    - content_type is derived from structural fields (is_in_table + is01_a)
    - Human can see the underlying fields and disagree
    - It's a label for organization, not a judgment

CONCLUSION: NO Machine output substitutes Human Semantic Judgment.
  Human retains sole authority over KEEP/MERGE/UNKNOWN decisions.
```

---

## 11. Audit Failure Routing

| Failure | Detection | Route | Fallback? |
|---|---|---|---|
| Evidence Missing | P1 completeness check | Flag insufficiency → L1 shows "Insufficient" → Human UNKNOWN | NO guess |
| Case Selection uncertain | P3 guardrail violation | RESELECT with diversity | If pool lacks diversity → flag SELECTION_POOL_BIAS |
| Evidence Pack insufficient | Human expansion_count high | Human expands L1 → still insufficient → UNKNOWN | NO guess |
| Feedback insufficient | Human decision = UNKNOWN | Do not create Signal Candidate | NO signal |
| Signal unstable | has_conflict=True | → BOUNDARY_REVIEW_REQUIRED | NO auto-resolve |
| Counterexample found | Search returns NEGATIVE | → BOUNDARY_REVIEW_REQUIRED | NO auto-modify |
| No counterexample | Search returns CEILING | → INSUFFICIENT_EVIDENCE | NO auto-promote |
| Boundary unresolved | Human selects UNKNOWN | Signal stays CANDIDATE | NO auto-validate |
| Future case fails | Replay UNSUPPORTED | Signal → REVIEW (Phase 2) | NO auto-retire |

```
FORBIDDEN:
  fallback = guess (NO — system never guesses)
  retry = change decision (NO — system never changes Human decision)
  
ALL failure routes lead to either:
  - UNKNOWN (Human or system acknowledges inability)
  - BOUNDARY_REVIEW_REQUIRED (escalate to Human)
  - INSUFFICIENT_EVIDENCE (system acknowledges limitation)
  
NONE lead to:
  - Auto-decision
  - Auto-modification
  - Auto-promotion
  - Auto-rule
```

**FAILURE_ROUTING = COMPLETE.**

---

## 12. SIG Walk-Through with Phase 1 Data Structures

### SIG-01: TABLE_NUMERIC_DIFF_CELL → SPLIT

```
Step 1: FeedbackRecord
  9 cases, all with evidence_snapshot:
    is_in_table=True, different_cell=True, is01_a=True, is02_b=False
  All human_decision=KEEP_SEPARATE
  → CAN be recorded in FeedbackRecord ✓

Step 2: Evidence Signature
  Signature = {is_in_table:True, different_cell:True, is01_a:True, is02_b:False,
               text_a_ends_period:False, text_b_starts_capital:False, content_type:TABLE_NUMERIC}
  → CAN be extracted ✓
  content_type = TABLE_NUMERIC (DERIVED from is_in_table+is01_a — GAP-1 but derivable)

Step 3: SignalCandidate
  9 source_cases, all KEEP_SEPARATE, decision_consistency=True
  Independence: 5 on resnet page 6 → independent_count=3, ratio=0.33
  → CAN be formed ✓
  → Status: REPEATED, then INDEPENDENCE_VERIFIED (with LOW_INDEPENDENCE flag)

Step 4: Counterexample Search
  IS-11: 0 counterexamples (all 9 are the positive set)
  P7: CANNOT match on is_in_table/different_cell (GAP-3 — P7 has no TLD fields)
  → P7 match on is01_a=True, is02_b=False only (4-field match, not 6-field)
  → P7 cases with is01_a=True, is02_b=False: need to check
  
  CONTRACT GAP: P7 cannot do full Signature match for SIG-01.
  → Counterexample Search is PARTIAL for SIG-01.
  → status = COUNTEREXAMPLE_CHECKED with search_completeness=PARTIAL

Step 5: Final Phase 1 Status
  BOUNDARY_REVIEW_REQUIRED (with PARTIAL search completeness)
  → Cannot be promoted in Phase 1 ✓

CONTRACT GAP: P7 lacks TLD fields → SIG-01 counterexample search is PARTIAL.
```

### SIG-02: SENTENCE_BOUNDARY_PERIOD_CAPITAL → SPLIT

```
Step 1: FeedbackRecord
  4 IS-11 cases (adjudicated), all with evidence_snapshot:
    is_in_table=False, different_cell=False, is01_a=False, is02_b=True,
    text_a_ends_period=True, text_b_starts_capital=True
  human_decision: KEEP_SEPARATE (adjudicated)
  has_conflict=True (reviewer disagreement)
  → CAN be recorded ✓

Step 2: Evidence Signature
  Signature = {is_in_table:False, different_cell:False, is01_a=False, is02_b:True,
               text_a_ends_period:True, text_b_starts_capital:True, content_type:PROSE}
  → CAN be extracted ✓
  content_type = PROSE (DERIVED — GAP-1 but derivable)

Step 3: SignalCandidate
  4 source_cases, decision_consistency=True (at adjudicated level)
  has_conflict=True → status includes CONFLICT flag
  Independence: 3 docs → independent_count=3, ratio=0.75
  → CAN be formed ✓

Step 4: Counterexample Search
  IS-11: 0 counterexamples in IS-11 (only 4 cases have this signature)
  P7: CAN match on is01_a=False, is02_b=True, text_a_ends_period=True,
      text_b_starts_capital=True (4-field match — all available in P7)
  → P7: 15 matches found, 5 MERGE (counterexamples!)
  → search_completeness = FULL (all 4 match fields available in P7)
  → counterexamples_found = 5

Step 5: Final Phase 1 Status
  BOUNDARY_REVIEW_REQUIRED (with 5 counterexamples found)
  → Cannot be promoted ✓
  → HVA-03 architecture correctly blocks SIG-02 ✓

CONTRACT STATUS: SIG-02 walk-through completes without gaps ✓
  (P7 has all 4 needed fields: is01_a, is02_b, text, text)
```

### SIG-07: AMB-032 Evidence Distillation Gap

```
Step 1: FeedbackRecord
  AMB-032 B2: human_decision=UNKNOWN
  evidence_snapshot: is_in_table=True, different_cell=True (from machine_eval)
  
  CONTRACT NOTE: L5 has_tld=False, cues show TLD=None
  BUT machine_eval has TLD data.
  → FeedbackRecord reads from machine_eval (GAP-4 resolution)
  → evidence_snapshot correctly captures different_cell=True ✓

Step 2: Evidence Signature
  Signature = {is_in_table:True, different_cell:True, is01_a:False, is02_b:False,
               text_a_ends_period:False, text_b_starts_capital:False}
  
  Wait: is01_a=False (text_a="-" is not pure number per IS-01 regex)
  is02_b=False (text_b="8.43" has no alpha > 2)
  → Signature matches AMB-032 ✓

Step 3: SignalCandidate
  Only 1 case with UNKNOWN decision + this signature
  → Cannot form SignalCandidate (need ≥2 with same decision)
  → Routed to EVIDENCE_DISTILLATION_FEEDBACK (not Signal)
  
  Actually: AMB-032 A condition has human_decision=KEEP_SEPARATE
  → If we use A condition: 1 case with KEEP_SEPARATE + signature
  → Still only 1 case → cannot form Candidate
  
  But: other cases with same signature?
  → Check: is_in_table=True, different_cell=True, is01_a=False, is02_b=False
  → AMB-064 has different_cell=True, is_in_table=True (from machine_eval data)
  → Need to check is01_a/is02_b for AMB-064

Step 4: If ≥2 cases found with same signature:
  Counterexample Search → IS-11 only (P7 lacks TLD fields)
  → PARTIAL search
  
Step 5: Final Phase 1 Status
  If 1 case: NOT a SignalCandidate (one-off)
  If ≥2 cases: BOUNDARY_REVIEW_REQUIRED

CONTRACT STATUS: FeedbackRecord captures AMB-032 correctly ✓
  (reads from machine_eval, not L5 cues — resolves GAP-4)
```

### SIG-08: AMB-375 Genuine Boundary

```
Step 1: FeedbackRecord
  AMB-375: human_decision=KEEP_SEPARATE (adjudicated)
  evidence_snapshot: is_in_table=False, different_cell=False, is01_a=False, is02_b=True,
    text_a_ends_period=True, text_b_starts_capital=True
  has_conflict=True (Reviewer A: KS, Reviewer B: MERGE)
  → CAN be recorded ✓

Step 2: Evidence Signature
  Same as SIG-02: {is_in_table:False, is01_a:False, is02_b:True,
    text_a_ends_period:True, text_b_starts_capital:True}
  → SIG-08 and SIG-02 have SAME Evidence Signature
  → They are the SAME SignalCandidate (4 cases total: AMB-005/375/418/519)

Step 3: SignalCandidate
  Same as SIG-02: 4 cases, has_conflict=True
  → Status: BOUNDARY_REVIEW_REQUIRED

Step 4: Counterexample Search
  Same as SIG-02: 5 P7 counterexamples found
  → 33% FP rate

Step 5: Final Phase 1 Status
  BOUNDARY_REVIEW_REQUIRED (with 5 counterexamples)
  → Cannot be promoted ✓

CONTRACT STATUS: SIG-08 = SIG-02 (same signature, same candidate) ✓
  No additional gaps.
```

### Walk-Through Summary

| Signal | FeedbackRecord | Evidence Signature | SignalCandidate | Counterexample | Phase 1 Status | Contract Gap? |
|---|---|---|---|---|---|---|
| SIG-01 | ✓ | ✓ | ✓ | **PARTIAL** (P7 lacks TLD) | BOUNDARY_REVIEW_REQUIRED | GAP-3 |
| SIG-02 | ✓ | ✓ | ✓ | ✓ (FULL) | BOUNDARY_REVIEW_REQUIRED | NONE |
| SIG-07 | ✓ | ✓ | 1 case (no candidate) | N/A | One-off observation | NONE |
| SIG-08 | ✓ | ✓ (= SIG-02) | ✓ (= SIG-02) | ✓ (= SIG-02) | BOUNDARY_REVIEW_REQUIRED | NONE |

---

## 13. Minimal Data Flow Table

| Stage | Input | Process | Output | Human | Authority |
|---|---|---|---|---|---|
| Evidence Pack | machine_eval (is11_observation, experimental_c) + GT (text_a/b) | Organize into L0-L1 | EvidencePack | — | 0 (Machine) |
| Human Review | EvidencePack | Semantic judgment | FeedbackRecord | YES | Human |
| Signature | FeedbackRecord.evidence_snapshot | Structural extraction | EvidenceSignature | — | 0 (Machine) |
| Candidate | EvidenceSignatures (≥2 matching) | Recurrence + independence | SignalCandidate | — | 0 (Machine) |
| Counterexample | SignalCandidate + IS-11/P7 pool | Boolean signature match | CounterexampleSet | — | 0 (Machine) |
| Boundary | Candidate + Counterexamples | Semantic validation | BoundaryStatus | YES | Human |

```
Authority column:
  0 = Machine structural authority (aggregation, compression, comparison)
  Human = Human semantic authority (judgment, validation, boundary)

NO stage has mixed authority.
NO stage has Machine making semantic decisions.
```

---

## 14. Minimal Prototype Selection

### Options

```
A. FeedbackRecord + Evidence Pack
   → Proves: evidence can be organized and feedback can be captured
   → Missing: cannot group feedback → cannot test Signal formation
   → Too minimal: doesn't prove core hypothesis

B. FeedbackRecord + Evidence Pack + Evidence Signature
   → Proves: evidence can be organized, feedback captured, signature extracted
   → Missing: cannot group signatures → cannot test recurrence
   → Better but still incomplete

C. FeedbackRecord + Evidence Pack + Evidence Signature + SignalCandidate
   → Proves: FULL minimal loop from feedback to candidate formation
   → Can test: independence check, conflict detection, engagement stats
   → Missing: Counterexample Search (but candidates can be formed without it)
   → RECOMMENDED

D. + Counterexample Search
   → Proves: full loop including safety check
   → Adds: P7 cross-corpus complexity (GAP-3), more implementation
   → Risk: Counterexample Search adds scope without proving more of core hypothesis
   → DEFER to Phase 1.5
```

### Selection: C

```
MINIMAL_PROTOTYPE = C

Rationale:
  Core hypothesis = "Human feedback can be linked to Evidence and grouped
  by structural similarity into Signal Candidates."

  This hypothesis is proven by C:
    - FeedbackRecord links decision to evidence (P6)
    - Evidence Pack organizes evidence for human (P4)
    - Evidence Signature extracts structural fingerprint (P7 partial)
    - SignalCandidate groups similar feedback (P7)

  Counterexample Search (D) does NOT prove more of the core hypothesis.
  It proves a SAFETY mechanism. Safety is important but secondary to
  proving the loop works at all.

  Phase 1.5 can add Counterexample Search once Phase 1 proves the loop.
  
  Principle: "Choose the minimal closed loop that proves the core hypothesis,
  not the most feature-complete version."
```

---

## 15. Implementation Readiness Gate

```
HVA-04 STATUS = CONDITIONAL

P4_CONTRACT = GAP
  GAP-1: content_type not in any file (DERIVABLE — rule must be documented)
  GAP-2: P2 geometry fields not in machine_eval (RESOLVED: drop L2, use L0-L1 only)
  GAP-4: L5 has_tld inconsistency (RESOLVED: read from machine_eval, not L5 cues)

P6_CONTRACT = READY
  All required fields available from machine_eval + GT + L5 interaction log

P7_CONTRACT = GAP
  GAP-1: content_type in signature (DERIVABLE)
  GAP-3: P7 lacks TLD fields for cross-corpus match (DOCUMENTED limitation)
  Phase 1 scope: IS-11 only (no P7 cross-corpus needed for C)

COUNTEREXAMPLE_CONTRACT = GAP
  GAP-3: P7 lacks TLD fields → PARTIAL match for SIG-01
  DEFERRED to Phase 1.5 (not in minimal prototype C)

HUMAN_BOUNDARY = CLEAR
  Human does 3 things: Case Judgment, Signal Validation, Boundary Validation
  No Machine output substitutes Human semantic judgment

FAILURE_ROUTING = COMPLETE
  All failures route to UNKNOWN / BOUNDARY_REVIEW_REQUIRED / INSUFFICIENT_EVIDENCE
  No fallback = guess
  No retry = change decision

AUTHORITY_BOUNDARY = PASS
  Machine: structural (aggregation, compression, comparison)
  Human: semantic (judgment, validation, boundary)
  No authority leakage

SEMANTIC_LEAKAGE = 0
  different_cell = Machine-derived structural fact (NOT semantic judgment)
  machine_decision = Machine interpretation (UI must label "may be wrong")
  content_type = Machine-derived classification (UI must label "classified as")
  All 3 have UI labeling requirements to prevent leakage

MINIMAL_PROTOTYPE = C
  FeedbackRecord + Evidence Pack (L0-L1) + Evidence Signature + SignalCandidate

IMPLEMENTATION_BLOCKERS =
  1. GAP-1: content_type derivation rule must be documented before implementation
  2. GAP-4: Evidence Pack must read TLD from machine_eval (is11_observation),
     NOT from L5 experiment_cases (cues) — this is a data source decision
  3. Case Selection guardrails are design heuristics, not hard rules — must be
     labeled as "sampling_guardrail" not "hard_rule"

IMPLEMENTATION_AUTHORIZED = FALSE
EXPERIMENT_AUTHORIZED = FALSE

DICE_CORE_MODIFICATION = NO
TLD_MODIFICATION = NO
IS11_MODIFICATION = NO
P1_P7_MODIFICATION = NO
GT_MODIFICATION = NO

FROZEN_BASELINE = INTACT (drift=0/7, TLD=022f5c21, GT=7349963d)
PRODUCTION = FALSE
STOP = TRUE
```

---

## 16. Final Answer (10 Sentences)

1. **第一版 Prototype 做 4 件事**：FeedbackRecord（把 Human 判断和 machine_eval 的 evidence_snapshot 冻结关联）、Evidence Pack L0-L1（把 text_a/b + is_in_table + different_cell + is01/is02 + period/capital + machine_decision 组织为两层渐进展示）、Evidence Signature（从 evidence_snapshot 提取 7 个布尔/枚举结构特征作为指纹）、SignalCandidate（把 ≥2 个 Signature 相同的 FeedbackRecord 分组，执行 independence check 和 conflict detection）。

2. **只做这些因为核心假设是"Human feedback 能否被关联到 Evidence 并按结构相似性分组为 Signal Candidate"**——C 选项是证明这个假设的最小闭环，Counterexample Search 是安全机制而非核心假设验证，推迟到 Phase 1.5。

3. **Evidence Pack 输入**是 machine_eval 的 is11_observation（is_in_table, different_cell）和 experimental_c（is01_a, is02_b, decision）加 GT 的 text_a/b；**输出**是 L0（text_a/b, page, content_type）+ L1（is_in_table, different_cell, is01/is02, period/capital, machine_decision, insufficiency）两层结构化 JSON。

4. **FeedbackRecord 输入**是 Human 的 decision + Evidence Pack + 交互日志；**输出**是 record_id, case_id, human_decision, evidence_snapshot（冻结的 evidence 状态）, evidence_viewed（查看的层级和耗时）, provenance（hash 和时间戳）；Human 不需要写 rationale。

5. **Evidence Signature 输入**是 FeedbackRecord.evidence_snapshot；**输出**是 7 字段布尔/枚举 dict（is_in_table, different_cell, is01_a, is02_b, text_a_ends_period, text_b_starts_capital, content_type）；**SignalCandidate 输入**是 ≥2 个相同 Signature 的 FeedbackRecord；**输出**是 signal_id, source_cases, human_decisions, decision_consistency, has_conflict, independence, recurrence, status。

6. **Human 最终判断 3 件事**：Case Judgment（KEEP/MERGE/UNKNOWN）、Signal Validation（SUPPORTED/UNSUPPORTED/UNKNOWN）、Boundary Validation（IN_SCOPE/OUT_OF_SCOPE/NEEDS_SCOPING/UNKNOWN）——Phase 1 只涉及 Case Judgment，后两者是 Phase 2。

7. **Machine 最终做 4 件事**：Evidence 聚合为 Pack、从 Pack 提取 Evidence Signature、按 Signature 分组形成 SignalCandidate、执行 independence check 和 conflict detection——Machine 不做任何语义判断、不写 Rule、不决定 Signal 是否成立。

8. **绝对不能自动化的东西**：Signal 的 validation（必须 Human）、Signal 的 boundary 定义（必须 Human）、Signal 的 promotion（必须 Human Boundary Review）、ceiling effect 的 interpretation（0 反例 ≠ validated，必须 Human 判断）、任何从 Candidate 到 Rule 的转换（FORBIDDEN）。

9. **目前仍然没有解决的风险**：GAP-3（P7 缺 TLD 字段导致 SIG-01 类 Signal 的跨语料 counterexample search 只能 PARTIAL 匹配）和 Stability-Novelty Paradox（架构提供了 BOUNDING 机制但不保证 Human 能找到结构化 scope——SIG-02/08 的句子边界是语义问题，可能永久 UNKNOWN）。

10. **Phase 1 做完以后，进入 Phase 2 需要出现的证据**：所有 45 个 IS-11 case 生成 FeedbackRecord 且 evidence_snapshot 正确冻结了 machine_eval 状态；Evidence Signature 能正确区分 SIG-01（table numeric）和 SIG-02（period+capital）为不同 Signature；SignalCandidate 能检测 SIG-01 的 resnet page 6 independence 问题（ratio=0.33）；至少 1 个 SignalCandidate 达到 INDEPENDENCE_VERIFIED 状态且 has_conflict 被正确标记——此时才能证明管道机械可行，可以考虑 Phase 1.5（Counterexample Search）和 Phase 2（Human Boundary Validation）。

`STOP = TRUE`。
