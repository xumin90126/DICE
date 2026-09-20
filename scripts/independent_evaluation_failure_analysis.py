"""
Independent Evaluation Failure Analysis & Next Information Source Decision
READ-ONLY / NO IMPLEMENTATION / NO POST-HOC TUNING

Analyzes the frozen Independent Machine-Resolvability Evaluation results.
Builds case-level failure matrix, outcome decomposition, and information source analysis.
Does NOT modify any frozen file. Does NOT execute new machine decisions.
"""
import json, os, re, time
from collections import Counter, defaultdict

P7 = "tmp/perception/p7"

def load_all_data():
    """Load all frozen data sources."""
    with open(f"{P7}/independent_machine_resolvability_results.json") as f:
        results = json.load(f)
    with open(f"{P7}/independent_evaluation_semantic_gt.json") as f:
        gt = json.load(f)
    with open(f"{P7}/independent_evaluation_sampling_frame.json") as f:
        sf = json.load(f)
    
    gt_lookup = {r["case_id"]: r for r in gt["gt_records"]}
    sf_lookup = {c["case_id"]: c for c in sf["sampled_cases"]}
    
    return results, gt_lookup, sf_lookup


def classify_outcome(machine_decision, semantic_gt, is01_a, is02_b):
    """
    Classify each case into outcome category.
    TP: machine MERGE + GT MERGE
    FP: machine MERGE + GT KEEP_SEPARATE
    TN: machine KEEP_SEPARATE + GT KEEP_SEPARATE
    FN: machine KEEP_SEPARATE + GT MERGE
    ABSTAIN: machine INSUFFICIENT_EVIDENCE
    """
    if machine_decision == "MERGE" and semantic_gt == "MERGE":
        return "TRUE_POSITIVE"
    elif machine_decision == "MERGE" and semantic_gt == "KEEP_SEPARATE":
        return "FALSE_POSITIVE"
    elif machine_decision == "KEEP_SEPARATE" and semantic_gt == "KEEP_SEPARATE":
        return "TRUE_NEGATIVE"
    elif machine_decision == "KEEP_SEPARATE" and semantic_gt == "MERGE":
        return "FALSE_NEGATIVE"
    elif machine_decision == "INSUFFICIENT_EVIDENCE":
        return "ABSTENTION"
    return "UNKNOWN"


def classify_abstention(case_id, semantic_gt, is01_a, is02_b, boundary_class, 
                         reviewer_a_reason, reviewer_b_reason, text_a, text_b):
    """
    Classify abstention into sub-categories based on evidence analysis.
    
    A. SUPPORTED_ABSTENTION — current frozen info source genuinely insufficient
    B. OVER_CONSERVATIVE — frozen info source theoretically sufficient but protocol abstained
    C. TARGET_CLASS_MISSING — would be target class (TOC) but absent in corpus
    D. OUT_OF_SCOPE — not target class, abstention expected
    E. INFORMATION_SOURCE_MISSING — needs new IS not currently in frozen spec
    F. DECISION_PROTOCOL_LIMITATION — current IS could resolve but protocol doesn't use them
    G. UNKNOWN — cannot confidently classify
    """
    # Analyze what information the human used
    reasons = (reviewer_a_reason + " " + reviewer_b_reason).lower()
    
    # Check if human used table/column context
    table_signals = any(kw in reasons for kw in [
        "table", "column", "row", "cell", "header", "different columns",
        "table 1", "table cell"
    ])
    
    # Check if human used reference/citation context
    ref_signals = any(kw in reasons for kw in [
        "reference", "citation", "author", "bibliograph", "ref [",
        "publisher", "et al", "reference list", "reference entry"
    ])
    
    # Check if human used sentence/paragraph context
    sentence_signals = any(kw in reasons for kw in [
        "sentence", "paragraph", "period", "new sentence", "continuous",
        "consecutive", "phrase", "license", "published"
    ])
    
    # Check if human used figure context
    figure_signals = any(kw in reasons for kw in [
        "figure", "sub-figure", "panel", "fig"
    ])
    
    # Check if human used heading/section context
    heading_signals = any(kw in reasons for kw in [
        "heading", "section", "title", "subtitle"
    ])
    
    # Determine what IS features are available
    # IS-01_a: number pattern on text_a
    # IS-02_b: readable title on text_b
    # IS-04: punctuation (text_a ends with period)
    # IS-05: capital start (text_b starts with capital)
    
    has_is01 = is01_a
    has_is02 = is02_b
    has_punctuation = text_a.strip().endswith(".") or text_a.strip().endswith("),") or text_a.strip().endswith(").")
    has_capital = len(text_b.strip()) > 0 and text_b.strip()[0].isupper() if text_b.strip() else False
    
    # Classify based on boundary class and signal analysis
    if boundary_class == "TABLE_CELL" or boundary_class == "TABLE_CELL_PAIR":
        if table_signals:
            return "E_INFORMATION_SOURCE_MISSING", "Human used table column/row context (IS-11/IS-12 proposed)"
        return "E_INFORMATION_SOURCE_MISSING", "Table structural context needed"
    
    if boundary_class == "REFERENCE_LIST_ENTRY":
        if ref_signals:
            # Human used reference structure — is this machine-observable?
            # Reference numbers [N] are detectable, but citation fragments ("et", "al.,") are not via IS-01/IS-02
            if has_is01 and not has_is02:
                return "F_DECISION_PROTOCOL_LIMITATION", "IS-01 detected number but IS-02 failed on citation text"
            elif not has_is01 and has_is02:
                return "E_INFORMATION_SOURCE_MISSING", "Reference structure context needed (IS-13 proposed)"
            else:
                return "E_INFORMATION_SOURCE_MISSING", "Citation fragment structure not detectable by current IS"
        return "E_INFORMATION_SOURCE_MISSING", "Reference structure context needed"
    
    if boundary_class == "BODY_TEXT_CONTINUATION":
        if sentence_signals:
            # Human used sentence boundary interpretation (IS-10, Category C - semantic)
            if has_punctuation and has_capital:
                return "E_INFORMATION_SOURCE_MISSING", "Sentence boundary signals exist (IS-04+IS-05) but IS-10 interpretation not in frozen spec"
            return "E_INFORMATION_SOURCE_MISSING", "Sentence/paragraph context needed"
        return "G_UNKNOWN", "Cannot determine information gap"
    
    if boundary_class == "FIGURE_LABEL":
        if figure_signals:
            return "D_OUT_OF_SCOPE", "Figure label pairs are not target class for IS-01+IS-02"
        return "D_OUT_OF_SCOPE", "Figure context not target class"
    
    if boundary_class == "OTHER_AMBIGUOUS":
        if heading_signals:
            return "C_TARGET_CLASS_MISSING", "Heading/section context suggests potential TOC-like case"
        return "G_UNKNOWN", "Cannot classify"
    
    return "G_UNKNOWN", "Unclassified abstention"


def analyze_human_info_sources(reasons_text, text_a, text_b, boundary_class):
    """
    Analyze which information sources the human reviewer used.
    Returns dict of IS usage.
    """
    reasons = reasons_text.lower()
    text_a_stripped = text_a.strip()
    text_b_stripped = text_b.strip()
    
    sources = {
        "IS-01_TEXT_NUMBER_PATTERN": False,
        "IS-02_TEXT_READABLE_TITLE": False,
        "IS-03_TEXT_SYMBOL_PATTERN": False,
        "IS-04_TEXT_PUNCTUATION": False,
        "IS-05_TEXT_CAPITAL_START": False,
        "IS-06_TEXT_APPENDIX_LETTER": False,
        "IS-07_VISUAL_TOC_CONTEXT": False,
        "IS-08_VISUAL_FORMULA_CONTEXT": False,
        "IS-09_VISUAL_BODY_CONTEXT": False,
        "IS-10_SENTENCE_BOUNDARY": False,
        "IS-11_TABLE_CELL_CONTEXT": False,  # PROPOSED
        "IS-12_ROW_COLUMN_POSITION": False,  # PROPOSED
        "IS-13_HEADER_RELATION": False,  # PROPOSED
        "IS-14_DOCUMENT_STRUCTURE_ROLE": False,  # PROPOSED
    }
    
    # IS-01: number pattern
    if re.match(r'^\d+(\.\d+)*\.?$', text_a_stripped) or re.match(r'^[A-Z]\.\d+$', text_a_stripped):
        if any(kw in reasons for kw in ["number", "reference number", "[", "case number", "edition"]):
            sources["IS-01_TEXT_NUMBER_PATTERN"] = True
    
    # IS-02: readable title
    if any(len(re.sub(r'[^a-zA-Z]', '', w)) > 2 for w in text_b.split()):
        if any(kw in reasons for kw in ["readable", "title", "word", "name", "author", "publisher"]):
            sources["IS-02_TEXT_READABLE_TITLE"] = True
    
    # IS-03: symbol pattern
    if any(kw in reasons for kw in ["symbol", "math", "formula", "cos", "sin", "parenthesis"]):
        sources["IS-03_TEXT_SYMBOL_PATTERN"] = True
    
    # IS-04: punctuation
    if text_a_stripped.endswith(".") or text_a_stripped.endswith("),"):
        if any(kw in reasons for kw in ["period", "sentence end", "ends", "punctuation"]):
            sources["IS-04_TEXT_PUNCTUATION"] = True
    
    # IS-05: capital start
    if text_b_stripped and text_b_stripped[0].isupper():
        if any(kw in reasons for kw in ["capital", "new sentence", "starts", "begins"]):
            sources["IS-05_TEXT_CAPITAL_START"] = True
    
    # IS-10: sentence boundary
    if any(kw in reasons for kw in ["sentence", "new sentence", "continuous", "consecutive", 
                                     "phrase", "paragraph", "split across"]):
        sources["IS-10_SENTENCE_BOUNDARY"] = True
    
    # IS-11/IS-12: table context
    if any(kw in reasons for kw in ["table", "column", "row", "cell", "header"]):
        sources["IS-11_TABLE_CELL_CONTEXT"] = True
        if any(kw in reasons for kw in ["different columns", "column", "row"]):
            sources["IS-12_ROW_COLUMN_POSITION"] = True
    
    # IS-13: header relation
    if any(kw in reasons for kw in ["header", "heading", "column header"]):
        sources["IS-13_HEADER_RELATION"] = True
    
    # IS-14: document structure role
    if any(kw in reasons for kw in ["reference list", "bibliography", "reference entry", 
                                     "section heading", "caption", "license"]):
        sources["IS-14_DOCUMENT_STRUCTURE_ROLE"] = True
    
    # IS-07/IS-08/IS-09: visual context (inferred from boundary class)
    if boundary_class == "BODY_TEXT_CONTINUATION":
        sources["IS-09_VISUAL_BODY_CONTEXT"] = True
    if "formula" in reasons or boundary_class == "FORMULA_LIKE":
        sources["IS-08_VISUAL_FORMULA_CONTEXT"] = True
    
    return sources


def assess_info_sufficiency(is01_a, is02_b, boundary_class, machine_decision, semantic_gt,
                             human_sources, text_a, text_b):
    """
    Assess whether current machine input is sufficient for correct decision.
    """
    # What machine currently has
    machine_has = {
        "IS-01_a": is01_a,
        "IS-02_b": is02_b,
    }
    
    # What human used beyond machine input
    human_extra = {k: v for k, v in human_sources.items() if v and k not in ["IS-01_TEXT_NUMBER_PATTERN", "IS-02_TEXT_READABLE_TITLE"]}
    
    if machine_decision == semantic_gt:
        # Correct decision — info was sufficient
        return "SUFFICIENT", "Machine had sufficient information", []
    
    if machine_decision == "INSUFFICIENT_EVIDENCE":
        # Abstention — was it necessary?
        if not human_extra:
            return "SUFFICIENT", "No additional human sources detected — abstention may be protocol limitation", ["protocol_conservatism"]
        
        missing = [k for k, v in human_extra.items() if v]
        # Check if missing sources are machine-observable
        machine_observable_missing = []
        semantic_missing = []
        for m in missing:
            if m.startswith("IS-1") and int(m.split("_")[0].split("-")[1]) <= 9:
                machine_observable_missing.append(m)
            elif m == "IS-10_SENTENCE_BOUNDARY":
                semantic_missing.append(m)
            elif m.startswith("IS-1") and int(m.split("_")[0].split("-")[1]) >= 11:
                machine_observable_missing.append(m)  # Proposed — theoretically observable
        
        if semantic_missing:
            return "INSUFFICIENT", "Requires semantic interpretation (Category C)", semantic_missing
        elif machine_observable_missing:
            return "PARTIALLY_SUFFICIENT", "Missing machine-observable sources", machine_observable_missing
        else:
            return "INSUFFICIENT", "Information gap cannot be characterized", missing
    
    if machine_decision != semantic_gt and machine_decision != "INSUFFICIENT_EVIDENCE":
        # Wrong decision (FP or FN)
        if not human_extra:
            return "SUFFICIENT", "Machine had same info as human but made wrong decision — protocol limitation", ["protocol_logic"]
        return "PARTIALLY_SUFFICIENT", "Machine made decision with partial info", [k for k, v in human_extra.items() if v]
    
    return "UNKNOWN", "Cannot assess", []


def build_failure_matrix():
    """Build the complete case-level failure matrix."""
    results, gt_lookup, sf_lookup = load_all_data()
    
    matrix = []
    
    for r in results["machine_results"]:
        case_id = r["case_id"]
        gt_rec = gt_lookup[case_id]
        sf_rec = sf_lookup[case_id]
        
        text_a = r["text_a"]
        text_b = r["text_b"]
        is01_a = r["is01_observation"]["is01_a"]
        is02_b = r["is02_observation"]["is02_b"]
        machine_decision = r["machine_decision"]
        semantic_gt = r["semantic_gt"]
        boundary_class = r["boundary_class"]
        
        # Classify outcome
        outcome = classify_outcome(machine_decision, semantic_gt, is01_a, is02_b)
        
        # Get human reasons
        reviewer_a_reason = gt_rec.get("reviewer_a_reason", "")
        reviewer_b_reason = gt_rec.get("reviewer_b_reason", "")
        combined_reasons = reviewer_a_reason + " " + reviewer_b_reason
        
        # Analyze human info sources
        human_sources = analyze_human_info_sources(combined_reasons, text_a, text_b, boundary_class)
        
        # Classify abstention sub-type if applicable
        abstention_subtype = None
        abstention_detail = None
        if outcome == "ABSTENTION":
            abstention_subtype, abstention_detail = classify_abstention(
                case_id, semantic_gt, is01_a, is02_b, boundary_class,
                reviewer_a_reason, reviewer_b_reason, text_a, text_b
            )
        
        # Assess information sufficiency
        sufficiency, sufficiency_detail, missing = assess_info_sufficiency(
            is01_a, is02_b, boundary_class, machine_decision, semantic_gt,
            human_sources, text_a, text_b
        )
        
        # Determine failure category
        if outcome == "TRUE_POSITIVE":
            failure_category = "NONE"
        elif outcome == "TRUE_NEGATIVE":
            failure_category = "NONE"
        elif outcome == "FALSE_POSITIVE":
            failure_category = "A_IS01_IS02_FP"
        elif outcome == "FALSE_NEGATIVE":
            failure_category = "C_FEATURE_COMBINATION_INSUFFICIENT"
        elif outcome == "ABSTENTION":
            failure_category = abstention_subtype or "D_INSUFFICIENT_EVIDENCE"
        else:
            failure_category = "UNKNOWN"
        
        # Determine if additional info could theoretically resolve
        could_resolve = "UNKNOWN"
        if missing:
            if any(m == "IS-10_SENTENCE_BOUNDARY" for m in missing):
                could_resolve = "PARTIALLY — requires semantic interpretation"
            elif any(m.startswith("IS-1") for m in missing if m != "IS-10_SENTENCE_BOUNDARY"):
                could_resolve = "YES — machine-observable source identified"
            else:
                could_resolve = "UNCLEAR"
        elif outcome in ["TRUE_POSITIVE", "TRUE_NEGATIVE"]:
            could_resolve = "N/A — correct decision"
        elif failure_category == "F_DECISION_PROTOCOL_LIMITATION":
            could_resolve = "YES — protocol could use existing info differently"
        
        # Confidence
        if outcome in ["TRUE_POSITIVE", "TRUE_NEGATIVE"]:
            confidence = "HIGH"
        elif outcome in ["FALSE_POSITIVE", "FALSE_NEGATIVE"]:
            confidence = "HIGH"
        elif abstention_subtype and abstention_subtype in ["D_OUT_OF_SCOPE", "E_INFORMATION_SOURCE_MISSING"]:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"
        
        record = {
            "case_id": case_id,
            "document_id": r["document_id"],
            "page": r["page"],
            "text_a": text_a,
            "text_b": text_b,
            "geometric_metadata": {
                "h_gap": sf_rec.get("h_gap"),
                "dy": sf_rec.get("dy"),
                "w_a": sf_rec.get("w_a"),
                "w_b": sf_rec.get("w_b"),
                "same_style": sf_rec.get("same_style"),
                "line_obs_count": sf_rec.get("line_obs_count"),
                "p4_decision": sf_rec.get("p4_decision"),
            },
            "boundary_class": boundary_class,
            "human_gt": semantic_gt,
            "human_reason_a": reviewer_a_reason,
            "human_reason_b": reviewer_b_reason,
            "is01_a": is01_a,
            "is02_b": is02_b,
            "machine_decision": machine_decision,
            "outcome": outcome,
            "failure_category": failure_category,
            "abstention_subtype": abstention_subtype,
            "abstention_detail": abstention_detail,
            "information_sufficiency": sufficiency,
            "sufficiency_detail": sufficiency_detail,
            "missing_information": missing,
            "human_info_sources_used": {k: v for k, v in human_sources.items() if v},
            "could_additional_info_resolve": could_resolve,
            "machine_observable_missing": [m for m in missing if m != "IS-10_SENTENCE_BOUNDARY"],
            "semantic_missing": [m for m in missing if m == "IS-10_SENTENCE_BOUNDARY"],
            "confidence": confidence,
            "notes": "",
        }
        matrix.append(record)
    
    return matrix


def main():
    print("=" * 100)
    print("INDEPENDENT EVALUATION FAILURE ANALYSIS")
    print("=" * 100)
    
    matrix = build_failure_matrix()
    
    # === OUTCOME DECOMPOSITION ===
    outcomes = Counter(r["outcome"] for r in matrix)
    print(f"\n--- Outcome Decomposition ---")
    for o in ["TRUE_POSITIVE", "FALSE_POSITIVE", "TRUE_NEGATIVE", "FALSE_NEGATIVE", "ABSTENTION"]:
        print(f"  {o}: {outcomes.get(o, 0)}")
    
    # === ABSTENTION SUB-TYPES ===
    abstentions = [r for r in matrix if r["outcome"] == "ABSTENTION"]
    abstention_types = Counter(r["abstention_subtype"] for r in abstentions)
    print(f"\n--- Abstention Sub-Types ({len(abstentions)} total) ---")
    for t, c in sorted(abstention_types.items(), key=lambda x: -x[1]):
        pct = c / len(abstentions) * 100
        print(f"  {t}: {c} ({pct:.1f}%)")
    
    # Correct vs Incorrect abstention
    correct_abstain = sum(1 for r in abstentions if r["abstention_subtype"] in 
                         ["D_OUT_OF_SCOPE", "E_INFORMATION_SOURCE_MISSING"])
    over_conservative = sum(1 for r in abstentions if r["abstention_subtype"] == "F_DECISION_PROTOCOL_LIMITATION")
    unknown_abstain = sum(1 for r in abstentions if r["abstention_subtype"] == "G_UNKNOWN")
    print(f"\n  Correct Abstention (genuine info gap): {correct_abstain}")
    print(f"  Over-Conservative (protocol limitation): {over_conservative}")
    print(f"  Unknown: {unknown_abstain}")
    
    # === FP ANALYSIS ===
    fps = [r for r in matrix if r["outcome"] == "FALSE_POSITIVE"]
    print(f"\n--- False Positive Analysis ({len(fps)}) ---")
    for fp in fps:
        print(f"  {fp['case_id']}: text_a='{fp['text_a']}', text_b='{fp['text_b']}'")
        print(f"    IS-01_a={fp['is01_a']}, IS-02_b={fp['is02_b']}, class={fp['boundary_class']}")
        print(f"    Human sources: {fp['human_info_sources_used']}")
        print(f"    Sufficiency: {fp['information_sufficiency']} — {fp['sufficiency_detail']}")
        print(f"    Missing: {fp['missing_information']}")
        print()
    
    # === FN ANALYSIS ===
    fns = [r for r in matrix if r["outcome"] == "FALSE_NEGATIVE"]
    print(f"\n--- False Negative Analysis ({len(fns)}) ---")
    for fn in fns:
        print(f"  {fn['case_id']}: text_a='{fn['text_a']}', text_b='{fn['text_b']}'")
        print(f"    IS-01_a={fn['is01_a']}, IS-02_b={fn['is02_b']}, class={fn['boundary_class']}")
        print(f"    Human sources: {fn['human_info_sources_used']}")
        print(f"    Sufficiency: {fn['information_sufficiency']} — {fn['sufficiency_detail']}")
        print(f"    Missing: {fn['missing_information']}")
        print()
    
    # === HUMAN INFO SOURCE MATRIX ===
    all_sources = Counter()
    for r in matrix:
        for k, v in r["human_info_sources_used"].items():
            if v:
                all_sources[k] += 1
    print(f"\n--- Human Information Source Usage (across 69 cases) ---")
    for src, count in sorted(all_sources.items(), key=lambda x: -x[1]):
        print(f"  {src}: {count} ({count/69*100:.1f}%)")
    
    # === INFO SUFFICIENCY ===
    sufficiency = Counter(r["information_sufficiency"] for r in matrix)
    print(f"\n--- Information Sufficiency ---")
    for s in ["SUFFICIENT", "PARTIALLY_SUFFICIENT", "INSUFFICIENT", "UNKNOWN"]:
        print(f"  {s}: {sufficiency.get(s, 0)}")
    
    # === DOCUMENT LEVEL ===
    print(f"\n--- Document-Level Breakdown ---")
    doc_stats = defaultdict(lambda: {"total": 0, "TP": 0, "FP": 0, "TN": 0, "FN": 0, "ABSTAIN": 0,
                                      "correct_abstain": 0, "over_conservative": 0, "unknown_abstain": 0,
                                      "gt_merge": 0, "gt_keep": 0})
    for r in matrix:
        doc = r["document_id"]
        doc_stats[doc]["total"] += 1
        if r["human_gt"] == "MERGE":
            doc_stats[doc]["gt_merge"] += 1
        else:
            doc_stats[doc]["gt_keep"] += 1
        if r["outcome"] == "TRUE_POSITIVE":
            doc_stats[doc]["TP"] += 1
        elif r["outcome"] == "FALSE_POSITIVE":
            doc_stats[doc]["FP"] += 1
        elif r["outcome"] == "TRUE_NEGATIVE":
            doc_stats[doc]["TN"] += 1
        elif r["outcome"] == "FALSE_NEGATIVE":
            doc_stats[doc]["FN"] += 1
        elif r["outcome"] == "ABSTENTION":
            doc_stats[doc]["ABSTAIN"] += 1
            if r["abstention_subtype"] in ["D_OUT_OF_SCOPE", "E_INFORMATION_SOURCE_MISSING"]:
                doc_stats[doc]["correct_abstain"] += 1
            elif r["abstention_subtype"] == "F_DECISION_PROTOCOL_LIMITATION":
                doc_stats[doc]["over_conservative"] += 1
            else:
                doc_stats[doc]["unknown_abstain"] += 1
    
    for doc in sorted(doc_stats.keys()):
        d = doc_stats[doc]
        print(f"  {doc}: total={d['total']}, GT_M={d['gt_merge']}, GT_KS={d['gt_keep']}, "
              f"TP={d['TP']}, FP={d['FP']}, TN={d['TN']}, FN={d['FN']}, ABSTAIN={d['ABSTAIN']} "
              f"(correct={d['correct_abstain']}, over-cons={d['over_conservative']}, unknown={d['unknown_abstain']})")
    
    # === BOUNDARY CLASS ===
    print(f"\n--- Boundary-Class Breakdown ---")
    bc_stats = defaultdict(lambda: {"total": 0, "TP": 0, "FP": 0, "TN": 0, "FN": 0, "ABSTAIN": 0,
                                     "correct_abstain": 0, "over_conservative": 0, "unknown_abstain": 0,
                                     "info_missing": 0, "out_of_scope": 0, "target_missing": 0})
    for r in matrix:
        bc = r["boundary_class"]
        bc_stats[bc]["total"] += 1
        if r["outcome"] == "ABSTENTION":
            bc_stats[bc]["ABSTAIN"] += 1
            st = r["abstention_subtype"]
            if st == "D_OUT_OF_SCOPE":
                bc_stats[bc]["out_of_scope"] += 1
                bc_stats[bc]["correct_abstain"] += 1
            elif st == "E_INFORMATION_SOURCE_MISSING":
                bc_stats[bc]["info_missing"] += 1
                bc_stats[bc]["correct_abstain"] += 1
            elif st == "F_DECISION_PROTOCOL_LIMITATION":
                bc_stats[bc]["over_conservative"] += 1
            elif st == "C_TARGET_CLASS_MISSING":
                bc_stats[bc]["target_missing"] += 1
            else:
                bc_stats[bc]["unknown_abstain"] += 1
        elif r["outcome"] == "TRUE_POSITIVE":
            bc_stats[bc]["TP"] += 1
        elif r["outcome"] == "FALSE_POSITIVE":
            bc_stats[bc]["FP"] += 1
        elif r["outcome"] == "TRUE_NEGATIVE":
            bc_stats[bc]["TN"] += 1
        elif r["outcome"] == "FALSE_NEGATIVE":
            bc_stats[bc]["FN"] += 1
    
    for bc in sorted(bc_stats.keys()):
        b = bc_stats[bc]
        print(f"  {bc}: total={b['total']}, TP={b['TP']}, FP={b['FP']}, TN={b['TN']}, FN={b['FN']}, "
              f"ABSTAIN={b['ABSTAIN']} (out_of_scope={b['out_of_scope']}, info_missing={b['info_missing']}, "
              f"over_cons={b['over_conservative']}, unknown={b['unknown_abstain']})")
    
    # === MISSING INFORMATION SOURCES ===
    all_missing = Counter()
    for r in matrix:
        for m in r["missing_information"]:
            all_missing[m] += 1
    print(f"\n--- Missing Information Sources (across all failure cases) ---")
    for src, count in sorted(all_missing.items(), key=lambda x: -x[1]):
        print(f"  {src}: {count}")
    
    # === SAVE FAILURE MATRIX JSON ===
    matrix_path = f"{P7}/independent_evaluation_failure_matrix.json"
    output = {
        "metadata": {
            "document": "Independent Evaluation Failure Matrix",
            "type": "READ-ONLY analysis matrix",
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S'),
            "immutable_baseline": {
                "evaluation_set": 69,
                "TP": 0, "FP": 3, "TN": 8, "FN": 2, "ABSTAIN": 56,
                "precision": 0.0, "recall": 0.0, "coverage": 0.188,
                "abstention_rate": 0.812, "boundary_shrinkage": 0.0,
            },
        },
        "outcome_summary": dict(outcomes),
        "abstention_summary": dict(abstention_types),
        "correct_abstention": correct_abstain,
        "over_conservative_abstention": over_conservative,
        "unknown_abstention": unknown_abstain,
        "human_info_source_usage": dict(all_sources),
        "info_sufficiency_summary": dict(sufficiency),
        "document_level": {k: dict(v) for k, v in doc_stats.items()},
        "boundary_class_level": {k: dict(v) for k, v in bc_stats.items()},
        "missing_info_sources": dict(all_missing),
        "case_records": matrix,
    }
    
    with open(matrix_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Failure matrix saved: {matrix_path} ({os.path.getsize(matrix_path):,} bytes)")
    
    return matrix, output


if __name__ == "__main__":
    matrix, output = main()
