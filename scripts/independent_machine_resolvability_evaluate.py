"""
Independent Machine-Resolvability Evaluation
FROZEN OUT-OF-SAMPLE EVALUATION — NO RULE TUNING / NO IMPLEMENTATION

Executes frozen IS-01 / IS-02 experimental definitions on the frozen 69-case Evaluation Set.
Uses the frozen decision protocol from independent_machine_resolvability_experiment_design.md §9.3.

FROZEN IS-01 (TEXT_NUMBER_PATTERN):
    re.match(r'^\d+(\.\d+)*\.?$', text.strip()) OR re.match(r'^[A-Z]\.\d+$', text.strip())

FROZEN IS-02 (TEXT_READABLE_TITLE):
    any(len(re.sub(r'[^a-zA-Z]', '', w)) > 2 for w in text.split())

FROZEN DECISION PROTOCOL (§9.3):
    IS-01(text_a)==True  AND IS-02(text_b)==True  → MERGE
    IS-01(text_a)==False AND IS-02(text_b)==False → KEEP_SEPARATE
    Otherwise (mixed signals)                     → INSUFFICIENT_EVIDENCE

READ-ONLY: does not modify any frozen/production files.
"""
import json, re, os, hashlib, time, copy
from collections import Counter, defaultdict

P7 = "tmp/perception/p7"
GT_PATH = f"{P7}/independent_evaluation_semantic_gt.json"
SF_PATH = f"{P7}/independent_evaluation_sampling_frame.json"

# ======================================================================
# FROZEN FEATURE DEFINITIONS — DO NOT MODIFY
# ======================================================================

def is_01_text_number_pattern(text):
    """
    IS-01: TEXT_NUMBER_PATTERN (FROZEN)
    re.match(r'^\d+(\\.\\d+)*\\.?$', text.strip()) OR re.match(r'^[A-Z]\\.\\d+$', text.strip())
    """
    text_stripped = text.strip()
    pattern_1 = re.match(r'^\d+(\.\d+)*\.?$', text_stripped)
    pattern_2 = re.match(r'^[A-Z]\.\d+$', text_stripped)
    return bool(pattern_1 or pattern_2)


def is_02_text_readable_title(text):
    """
    IS-02: TEXT_READABLE_TITLE (FROZEN)
    any(len(re.sub(r'[^a-zA-Z]', '', w)) > 2 for w in text.split())
    """
    return any(len(re.sub(r'[^a-zA-Z]', '', w)) > 2 for w in text.split())


# ======================================================================
# FROZEN DECISION PROTOCOL — §9.3
# ======================================================================

def frozen_decision_protocol(is01_a, is02_b):
    """
    Frozen decision protocol from experiment design §9.3.
    Step 2: IS-01_a==True AND IS-02_b==True → MERGE
    Step 3: IS-01_a==False AND IS-02_b==False → KEEP_SEPARATE
    Step 4: Otherwise → INSUFFICIENT_EVIDENCE
    """
    if is01_a and is02_b:
        return "MERGE"
    elif (not is01_a) and (not is02_b):
        return "KEEP_SEPARATE"
    else:
        return "INSUFFICIENT_EVIDENCE"


# ======================================================================
# BOUNDARY CLASS CLASSIFICATION (heuristic, for analysis only)
# ======================================================================

def classify_boundary_class(text_a, text_b, page_context=""):
    """
    Classify boundary case for analysis purposes.
    This does NOT affect evaluation — it's only for reporting.
    """
    ta = text_a.strip()
    tb = text_b.strip()
    combined = (ta + " " + tb).lower()

    # Reference list entries
    if re.match(r'^\[\d+\]', ta) or re.match(r'^\[\d+\]', tb):
        return "REFERENCE_LIST_ENTRY"
    if ta == "." or ta == ")." or ta == ",":
        return "REFERENCE_LIST_ENTRY"

    # Table cells (detected by short numeric/text pairs in table context)
    if re.match(r'^[\d\.\-~, ]+$', ta) and len(ta) < 20:
        if re.match(r'^[\d\.\-~, ]+$', tb) and len(tb) < 20:
            return "TABLE_CELL_PAIR"
        return "TABLE_CELL"

    # Section headings with numbers
    if is_01_text_number_pattern(ta) and is_02_text_readable_title(tb):
        return "TOC_SECTION_NUMBER_TITLE"

    # Appendix letter titles
    if re.match(r'^[A-Z]$', ta) and is_02_text_readable_title(tb):
        return "APPENDIX_LETTER_TITLE"

    # Figure labels
    if re.match(r'^Fig', ta, re.I) or re.match(r'^Fig', tb, re.I):
        return "FIGURE_LABEL"

    # Author names / publisher info (reference list fragments)
    if any(kw in combined for kw in ['springer', 'press', 'university', 'philadelphia', 'new york',
                                      'et al', 'ieee', 'arxiv', 'proceedings', 'conference']):
        return "REFERENCE_LIST_ENTRY"

    # Body text continuation
    if len(ta) > 3 and len(tb) > 3:
        if not is_01_text_number_pattern(ta):
            return "BODY_TEXT_CONTINUATION"

    return "OTHER_AMBIGUOUS"


# ======================================================================
# MAIN EVALUATION
# ======================================================================

def run_evaluation(run_label="RUN_1"):
    """Run the frozen evaluation on all 69 cases."""
    print(f"\n{'='*100}")
    print(f"INDEPENDENT MACHINE-RESOLVABILITY EVALUATION — {run_label}")
    print(f"{'='*100}")

    # Load frozen inputs
    with open(GT_PATH) as f:
        gt_data = json.load(f)
    with open(SF_PATH) as f:
        sf_data = json.load(f)

    # Build lookup from sampling frame for geometry provenance
    sf_lookup = {c["case_id"]: c for c in sf_data["sampled_cases"]}

    # Process each case
    machine_results = []

    for record in gt_data["gt_records"]:
        case_id = record["case_id"]
        text_a = record["text_a"]
        text_b = record["text_b"]
        doc_id = record["document_id"]
        page = record["page"]
        semantic_gt = record["semantic_gt"]

        # Compute frozen features
        is01_a = is_01_text_number_pattern(text_a)
        is02_b = is_02_text_readable_title(text_b)

        # Also compute IS-01(text_b) and IS-02(text_a) for analysis (NOT used in decision)
        is01_b = is_01_text_number_pattern(text_b)
        is02_a = is_02_text_readable_title(text_a)

        # Apply frozen decision protocol
        machine_decision = frozen_decision_protocol(is01_a, is02_b)

        # Classify boundary class (for analysis only)
        boundary_class = classify_boundary_class(text_a, text_b)

        # Get geometry provenance from sampling frame
        sf_case = sf_lookup.get(case_id, {})

        result = {
            "case_id": case_id,
            "document_id": doc_id,
            "page": page,
            "text_a": text_a,
            "text_b": text_b,
            "geometry_provenance": {
                "bbox_a": sf_case.get("bbox_a"),
                "bbox_b": sf_case.get("bbox_b"),
                "w_a": sf_case.get("w_a"),
                "w_b": sf_case.get("w_b"),
                "h_gap": sf_case.get("h_gap"),
                "dy": sf_case.get("dy"),
                "same_style": sf_case.get("same_style"),
                "line_obs_count": sf_case.get("line_obs_count"),
                "p4_decision": sf_case.get("p4_decision"),
                "geometric_state": sf_case.get("geometric_state"),
            },
            "is01_observation": {
                "is01_a": is01_a,
                "is01_b": is01_b,
                "text_a_stripped": text_a.strip(),
            },
            "is02_observation": {
                "is02_a": is02_a,
                "is02_b": is02_b,
                "text_b_stripped": text_b.strip(),
            },
            "machine_decision": machine_decision,
            "semantic_gt": semantic_gt,
            "gt_level": record.get("gt_level", "UNKNOWN"),
            "agreement_status": record.get("agreement_status", "UNKNOWN"),
            "boundary_class": boundary_class,
            "decision_evidence": {
                "is01_a": is01_a,
                "is02_b": is02_b,
                "protocol_step": "STEP_2" if machine_decision == "MERGE"
                                else ("STEP_3" if machine_decision == "KEEP_SEPARATE" else "STEP_4"),
            },
            "experiment_version": "FROZEN_v1.0",
            "feature_spec_version": "IS-01_FROZEN / IS-02_FROZEN",
            "decision_protocol_version": "experiment_design_§9.3_FROZEN",
            "provenance": {
                "evaluation_set_source": "independent_evaluation_sampling_frame.json",
                "gt_source": "independent_evaluation_semantic_gt.json",
                "feature_source": "independent_machine_resolvability_experiment_design.md §6.2-6.3",
                "decision_protocol_source": "independent_machine_resolvability_experiment_design.md §9.3",
            },
        }
        machine_results.append(result)

    # === COMPUTE METRICS ===
    total = len(machine_results)

    # Confusion matrix
    tp = 0  # machine MERGE + GT MERGE
    fp = 0  # machine MERGE + GT KEEP_SEPARATE
    tn = 0  # machine KEEP_SEPARATE + GT KEEP_SEPARATE
    fn = 0  # machine KEEP_SEPARATE + GT MERGE
    abstain = 0  # machine INSUFFICIENT_EVIDENCE

    for r in machine_results:
        md = r["machine_decision"]
        gt = r["semantic_gt"]
        if md == "MERGE" and gt == "MERGE":
            tp += 1
        elif md == "MERGE" and gt == "KEEP_SEPARATE":
            fp += 1
        elif md == "KEEP_SEPARATE" and gt == "KEEP_SEPARATE":
            tn += 1
        elif md == "KEEP_SEPARATE" and gt == "MERGE":
            fn += 1
        elif md == "INSUFFICIENT_EVIDENCE":
            abstain += 1

    # Metrics
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / total if total > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    coverage = (total - abstain) / total if total > 0 else 0.0
    abstention_rate = abstain / total if total > 0 else 0.0

    # Boundary shrinkage
    baseline_ambiguous = total  # Level 1
    # Level 2: Potential — cases where IS-01_a=True (could be resolvable)
    potential_resolvable = sum(1 for r in machine_results if r["is01_observation"]["is01_a"])
    # Level 3: Actual machine-resolved — machine gave deterministic decision (not INSUFFICIENT_EVIDENCE)
    actual_machine_resolved = total - abstain
    # Level 4: Independently validated — machine decision matches GT AND gates pass
    # This requires G7 (precision>=0.95) AND G8 (recall>=0.80)
    g7_pass = precision >= 0.95
    g8_pass = recall >= 0.80
    independently_validated = (tp + tn) if (g7_pass and g8_pass) else 0
    # Actual boundary shrinkage rate
    actual_shrinkage_rate = independently_validated / baseline_ambiguous if baseline_ambiguous > 0 else 0.0

    # Potential resolution rate (Level 2 / Level 1)
    potential_resolution_rate = potential_resolvable / baseline_ambiguous if baseline_ambiguous > 0 else 0.0
    # Machine deterministic resolution rate (Level 3 / Level 1)
    machine_deterministic_resolution_rate = actual_machine_resolved / baseline_ambiguous if baseline_ambiguous > 0 else 0.0

    # === CROSS-DOCUMENT ANALYSIS ===
    doc_analysis = {}
    for r in machine_results:
        doc = r["document_id"]
        if doc not in doc_analysis:
            doc_analysis[doc] = {
                "total": 0, "gt_merge": 0, "gt_keep_separate": 0,
                "machine_merge": 0, "machine_keep_separate": 0, "machine_insufficient": 0,
                "tp": 0, "fp": 0, "tn": 0, "fn": 0, "abstain": 0,
            }
        d = doc_analysis[doc]
        d["total"] += 1
        if r["semantic_gt"] == "MERGE":
            d["gt_merge"] += 1
        else:
            d["gt_keep_separate"] += 1
        if r["machine_decision"] == "MERGE":
            d["machine_merge"] += 1
        elif r["machine_decision"] == "KEEP_SEPARATE":
            d["machine_keep_separate"] += 1
        else:
            d["machine_insufficient"] += 1

        if r["machine_decision"] == "MERGE" and r["semantic_gt"] == "MERGE":
            d["tp"] += 1
        elif r["machine_decision"] == "MERGE" and r["semantic_gt"] == "KEEP_SEPARATE":
            d["fp"] += 1
        elif r["machine_decision"] == "KEEP_SEPARATE" and r["semantic_gt"] == "KEEP_SEPARATE":
            d["tn"] += 1
        elif r["machine_decision"] == "KEEP_SEPARATE" and r["semantic_gt"] == "MERGE":
            d["fn"] += 1
        elif r["machine_decision"] == "INSUFFICIENT_EVIDENCE":
            d["abstain"] += 1

    for doc, d in doc_analysis.items():
        d["precision"] = d["tp"] / (d["tp"] + d["fp"]) if (d["tp"] + d["fp"]) > 0 else 0.0
        d["recall"] = d["tp"] / (d["tp"] + d["fn"]) if (d["tp"] + d["fn"]) > 0 else 0.0
        d["fpr"] = d["fp"] / (d["fp"] + d["tn"]) if (d["fp"] + d["tn"]) > 0 else 0.0
        d["abstention_rate"] = d["abstain"] / d["total"] if d["total"] > 0 else 0.0
        d["coverage"] = (d["total"] - d["abstain"]) / d["total"] if d["total"] > 0 else 0.0
        d["low_sample"] = d["total"] < 10

    # === BOUNDARY CLASS ANALYSIS ===
    class_analysis = {}
    for r in machine_results:
        bc = r["boundary_class"]
        if bc not in class_analysis:
            class_analysis[bc] = {
                "total": 0, "gt_merge": 0, "gt_keep_separate": 0,
                "machine_merge": 0, "machine_keep_separate": 0, "machine_insufficient": 0,
                "tp": 0, "fp": 0, "tn": 0, "fn": 0, "abstain": 0,
            }
        c = class_analysis[bc]
        c["total"] += 1
        if r["semantic_gt"] == "MERGE":
            c["gt_merge"] += 1
        else:
            c["gt_keep_separate"] += 1
        if r["machine_decision"] == "MERGE":
            c["machine_merge"] += 1
        elif r["machine_decision"] == "KEEP_SEPARATE":
            c["machine_keep_separate"] += 1
        else:
            c["machine_insufficient"] += 1
        if r["machine_decision"] == "MERGE" and r["semantic_gt"] == "MERGE":
            c["tp"] += 1
        elif r["machine_decision"] == "MERGE" and r["semantic_gt"] == "KEEP_SEPARATE":
            c["fp"] += 1
        elif r["machine_decision"] == "KEEP_SEPARATE" and r["semantic_gt"] == "KEEP_SEPARATE":
            c["tn"] += 1
        elif r["machine_decision"] == "KEEP_SEPARATE" and r["semantic_gt"] == "MERGE":
            c["fn"] += 1
        elif r["machine_decision"] == "INSUFFICIENT_EVIDENCE":
            c["abstain"] += 1

    for bc, c in class_analysis.items():
        c["precision"] = c["tp"] / (c["tp"] + c["fp"]) if (c["tp"] + c["fp"]) > 0 else 0.0
        c["recall"] = c["tp"] / (c["tp"] + c["fn"]) if (c["tp"] + c["fn"]) > 0 else 0.0

    # === FAILURE ANALYSIS ===
    failures = []
    for r in machine_results:
        md = r["machine_decision"]
        gt_val = r["semantic_gt"]
        is_error = False
        error_type = ""

        if md == "MERGE" and gt_val == "KEEP_SEPARATE":
            is_error = True
            error_type = "FALSE_POSITIVE"
        elif md == "KEEP_SEPARATE" and gt_val == "MERGE":
            is_error = True
            error_type = "FALSE_NEGATIVE"
        elif md == "INSUFFICIENT_EVIDENCE":
            is_error = True
            error_type = "ABSTENTION"

        if is_error:
            # Classify failure reason
            is01_a = r["is01_observation"]["is01_a"]
            is02_b = r["is02_observation"]["is02_b"]

            if error_type == "FALSE_POSITIVE":
                # IS-01_a=True + IS-02_b=True but GT=KEEP_SEPARATE
                if is01_a and is02_b:
                    failure_category = "A_IS01_IS02_FP"
                    failure_detail = "IS-01 matched number pattern + IS-02 matched readable token, but GT=KEEP_SEPARATE"
                else:
                    failure_category = "G_IMPLEMENTATION_DEFECT"
                    failure_detail = "Unexpected FP — decision protocol logic error"
            elif error_type == "FALSE_NEGATIVE":
                if not is01_a and not is02_b:
                    failure_category = "C_FEATURE_COMBINATION_INSUFFICIENT"
                    failure_detail = "Neither IS-01 nor IS-02 fired, machine=KEEP_SEPARATE, but GT=MERGE"
                else:
                    failure_category = "C_FEATURE_COMBINATION_INSUFFICIENT"
                    failure_detail = "Mixed signals → INSUFFICIENT_EVIDENCE but classified as FN"
            elif error_type == "ABSTENTION":
                if is01_a and not is02_b:
                    failure_category = "D_INSUFFICIENT_EVIDENCE"
                    failure_detail = "IS-01_a=True but IS-02_b=False → mixed → abstain"
                elif not is01_a and is02_b:
                    failure_category = "D_INSUFFICIENT_EVIDENCE"
                    failure_detail = "IS-01_a=False but IS-02_b=True → mixed → abstain"
                else:
                    failure_category = "D_INSUFFICIENT_EVIDENCE"
                    failure_detail = "Abstention for unknown reason"
            else:
                failure_category = "F_OUT_OF_SCOPE"
                failure_detail = "Unknown error type"

            failures.append({
                "case_id": r["case_id"],
                "document_id": r["document_id"],
                "page": r["page"],
                "text_a": r["text_a"],
                "text_b": r["text_b"],
                "is01_a": is01_a,
                "is02_b": is02_b,
                "machine_decision": md,
                "semantic_gt": gt_val,
                "error_type": error_type,
                "failure_category": failure_category,
                "failure_detail": failure_detail,
                "boundary_class": r["boundary_class"],
            })

    # === FALSE POSITIVE MODE ANALYSIS ===
    fp_cases = [f for f in failures if f["error_type"] == "FALSE_POSITIVE"]
    fp_mode_analysis = {
        "total_fp": len(fp_cases),
        "is02_loose_detection_fp": 0,
        "cases": [],
    }
    for fp_case in fp_cases:
        # Check if IS-02 loose detection is the cause
        text_b = fp_case["text_b"]
        words = text_b.split()
        short_words = [w for w in words if 0 < len(re.sub(r'[^a-zA-Z]', '', w)) <= 2]
        readable_words = [w for w in words if len(re.sub(r'[^a-zA-Z]', '', w)) > 2]

        fp_mode = {
            "case_id": fp_case["case_id"],
            "text_a": fp_case["text_a"],
            "text_b": fp_case["text_b"],
            "is01_a": fp_case["is01_a"],
            "is02_b": fp_case["is02_b"],
            "readable_words_in_b": readable_words,
            "boundary_class": fp_case["boundary_class"],
            "gt": "KEEP_SEPARATE",
            "analysis": f"IS-01 matched '{fp_case['text_a']}' as number; IS-02 matched readable words {readable_words} in '{fp_case['text_b']}'"
        }
        fp_mode_analysis["cases"].append(fp_mode)

        # Check for known IS-02 loose detection words
        loose_words = {"cos", "sin", "and", "are", "the", "for", "not", "but", "all", "any", "can", "had", "her",
                       "was", "one", "our", "out", "day", "get", "has", "him", "his", "how", "its", "let", "may",
                       "new", "now", "old", "see", "way", "who", "boy", "did", "end", "few", "got", "set", "top"}
        for rw in readable_words:
            if rw.lower() in loose_words:
                fp_mode_analysis["is02_loose_detection_fp"] += 1

    # === BUILD METRICS SUMMARY ===
    metrics = {
        "metadata": {
            "experiment": "Independent Machine-Resolvability Evaluation",
            "run_label": run_label,
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S'),
            "feature_spec": "FROZEN IS-01 / IS-02",
            "decision_protocol": "FROZEN §9.3",
        },
        "total_cases": total,
        "confusion_matrix": {
            "TP": tp,
            "FP": fp,
            "TN": tn,
            "FN": fn,
            "ABSTAIN": abstain,
        },
        "metrics": {
            "precision": round(precision, 6),
            "recall": round(recall, 6),
            "f1": round(f1, 6),
            "accuracy": round(accuracy, 6),
            "fpr": round(fpr, 6),
            "fnr": round(fnr, 6),
            "coverage": round(coverage, 6),
            "abstention_rate": round(abstention_rate, 6),
        },
        "gates": {
            "G7_precision_ge_95": g7_pass,
            "G7_precision_value": round(precision, 6),
            "G7_threshold": 0.95,
            "G8_recall_ge_80": g8_pass,
            "G8_recall_value": round(recall, 6),
            "G8_threshold": 0.80,
        },
        "boundary_shrinkage": {
            "level_1_baseline_ambiguous": baseline_ambiguous,
            "level_2_potential_resolvable": potential_resolvable,
            "level_3_actual_machine_resolved": actual_machine_resolved,
            "level_4_independently_validated": independently_validated,
            "potential_resolution_rate": round(potential_resolution_rate, 6),
            "machine_deterministic_resolution_rate": round(machine_deterministic_resolution_rate, 6),
            "actual_boundary_shrinkage_rate": round(actual_shrinkage_rate, 6),
            "gates_required_for_shrinkage": "G7_PASS AND G8_PASS",
            "gates_passed": g7_pass and g8_pass,
        },
        "cross_document_analysis": {k: v for k, v in doc_analysis.items()},
        "boundary_class_analysis": {k: v for k, v in class_analysis.items()},
        "failure_analysis": {
            "total_failures": len(failures),
            "false_positives": fp,
            "false_negatives": fn,
            "abstentions": abstain,
            "failure_categories": dict(Counter(f["failure_category"] for f in failures)),
            "failures": failures,
        },
        "false_positive_mode_analysis": fp_mode_analysis,
        "decision_distribution": {
            "machine_merge": sum(1 for r in machine_results if r["machine_decision"] == "MERGE"),
            "machine_keep_separate": sum(1 for r in machine_results if r["machine_decision"] == "KEEP_SEPARATE"),
            "machine_insufficient": sum(1 for r in machine_results if r["machine_decision"] == "INSUFFICIENT_EVIDENCE"),
            "gt_merge": sum(1 for r in machine_results if r["semantic_gt"] == "MERGE"),
            "gt_keep_separate": sum(1 for r in machine_results if r["semantic_gt"] == "KEEP_SEPARATE"),
        },
        "is_observation_summary": {
            "is01_a_true": sum(1 for r in machine_results if r["is01_observation"]["is01_a"]),
            "is01_a_false": sum(1 for r in machine_results if not r["is01_observation"]["is01_a"]),
            "is02_b_true": sum(1 for r in machine_results if r["is02_observation"]["is02_b"]),
            "is02_b_false": sum(1 for r in machine_results if not r["is02_observation"]["is02_b"]),
        },
    }

    # Print summary
    print(f"\n--- Evaluation Summary ({run_label}) ---")
    print(f"  Total cases: {total}")
    print(f"  Confusion Matrix: TP={tp}, FP={fp}, TN={tn}, FN={fn}, ABSTAIN={abstain}")
    print(f"  Precision: {precision:.6f} ({'PASS' if g7_pass else 'FAIL'} G7≥0.95)")
    print(f"  Recall: {recall:.6f} ({'PASS' if g8_pass else 'FAIL'} G8≥0.80)")
    print(f"  F1: {f1:.6f}")
    print(f"  Accuracy: {accuracy:.6f}")
    print(f"  FPR: {fpr:.6f}")
    print(f"  FNR: {fnr:.6f}")
    print(f"  Coverage: {coverage:.6f}")
    print(f"  Abstention Rate: {abstention_rate:.6f}")
    print(f"\n  Boundary Shrinkage:")
    print(f"    Level 1 (Baseline Ambiguous): {baseline_ambiguous}")
    print(f"    Level 2 (Potential Resolvable): {potential_resolvable} ({potential_resolution_rate:.1%})")
    print(f"    Level 3 (Actual Machine-Resolved): {actual_machine_resolved} ({machine_deterministic_resolution_rate:.1%})")
    print(f"    Level 4 (Independently Validated): {independently_validated} ({actual_shrinkage_rate:.1%})")
    print(f"    Gates passed (G7&G8): {g7_pass and g8_pass}")
    print(f"\n  Cross-Document:")
    for doc, d in doc_analysis.items():
        ls = " (LOW_SAMPLE)" if d["low_sample"] else ""
        print(f"    {doc}: total={d['total']}, TP={d['tp']}, FP={d['fp']}, TN={d['tn']}, FN={d['fn']}, ABSTAIN={d['abstain']}, "
              f"P={d['precision']:.3f}, R={d['recall']:.3f}{ls}")
    print(f"\n  Boundary Class:")
    for bc, c in class_analysis.items():
        print(f"    {bc}: total={c['total']}, TP={c['tp']}, FP={c['fp']}, TN={c['tn']}, FN={c['fn']}, ABSTAIN={c['abstain']}")
    print(f"\n  Failure Analysis:")
    print(f"    Total failures (FP+FN+Abstain): {len(failures)}")
    print(f"    Failure categories: {dict(Counter(f['failure_category'] for f in failures))}")
    if fp_cases:
        print(f"\n  FALSE POSITIVE Cases ({len(fp_cases)}):")
        for f in fp_cases:
            print(f"    {f['case_id']}: text_a='{f['text_a']}', text_b='{f['text_b']}', "
                  f"is01_a={f['is01_a']}, is02_b={f['is02_b']}, class={f['boundary_class']}")

    return machine_results, metrics


def compute_hashes():
    """Compute hashes of all frozen inputs for reproducibility."""
    def sha256(p):
        with open(p, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

    hashes = {
        "evaluation_set_hash": sha256(SF_PATH),
        "semantic_gt_hash": sha256(GT_PATH),
        "feature_spec_hash": "FROZEN in independent_machine_resolvability_experiment_design.md §6.2-6.3",
        "decision_protocol_version": "experiment_design_§9.3_FROZEN",
        "is01_definition": r"re.match(r'^\d+(\.\d+)*\.?$', text.strip()) OR re.match(r'^[A-Z]\.\d+$', text.strip())",
        "is02_definition": r"any(len(re.sub(r'[^a-zA-Z]', '', w)) > 2 for w in text.split())",
        "decision_protocol": "IS-01_a=True AND IS-02_b=True → MERGE; IS-01_a=False AND IS-02_b=False → KEEP_SEPARATE; Otherwise → INSUFFICIENT_EVIDENCE",
    }
    return hashes


def main():
    # === RUN 1 ===
    results_1, metrics_1 = run_evaluation("RUN_1")

    # === RUN 2 (determinism check) ===
    results_2, metrics_2 = run_evaluation("RUN_2")

    # === DETERMINISM CHECK ===
    print(f"\n{'='*100}")
    print(f"DETERMINISM CHECK: RUN_1 vs RUN_2")
    print(f"{'='*100}")

    deterministic = True
    mismatch_count = 0

    for r1, r2 in zip(results_1, results_2):
        if r1["machine_decision"] != r2["machine_decision"]:
            deterministic = False
            mismatch_count += 1
            print(f"  MISMATCH: {r1['case_id']}: R1={r1['machine_decision']}, R2={r2['machine_decision']}")

    # Also compare metrics
    metrics_match = (
        metrics_1["confusion_matrix"] == metrics_2["confusion_matrix"] and
        metrics_1["metrics"] == metrics_2["metrics"]
    )

    print(f"\n  Decision mismatches: {mismatch_count}")
    print(f"  Metrics match: {metrics_match}")
    print(f"  DETERMINISTIC = {'TRUE ✅' if deterministic and metrics_match else 'FALSE ❌'}")

    if not deterministic or not metrics_match:
        print(f"\n  ⚠️ DETERMINISM FAILURE — STOP")
        return None, None, None, deterministic

    # === SAVE OUTPUT FILES ===
    hashes = compute_hashes()

    # 1. Results JSON
    results_output = {
        "metadata": {
            "experiment": "Independent Machine-Resolvability Evaluation",
            "type": "FROZEN OUT-OF-SAMPLE EVALUATION",
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S'),
            "feature_spec_version": "IS-01_FROZEN / IS-02_FROZEN",
            "decision_protocol_version": "experiment_design_§9.3_FROZEN",
            "experiment_version": "FROZEN_v1.0",
            "deterministic": deterministic,
            "determinism_verified": True,
            "run_1_timestamp": metrics_1["metadata"]["timestamp"],
            "run_2_timestamp": metrics_2["metadata"]["timestamp"],
        },
        "frozen_inputs": hashes,
        "machine_results": results_1,  # Use Run 1 as canonical
    }

    results_path = f"{P7}/independent_machine_resolvability_results.json"
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results_output, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Results saved: {results_path} ({os.path.getsize(results_path):,} bytes)")

    # 2. Metrics JSON
    metrics_output = metrics_1  # Use Run 1 as canonical
    metrics_output["determinism_check"] = {
        "deterministic": deterministic,
        "mismatches": mismatch_count,
        "metrics_match": metrics_match,
    }
    metrics_output["experiment_hashes"] = hashes
    metrics_output["metadata"]["deterministic"] = deterministic

    metrics_path = f"{P7}/independent_machine_resolvability_metrics.json"
    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(metrics_output, f, ensure_ascii=False, indent=2)
    print(f"✅ Metrics saved: {metrics_path} ({os.path.getsize(metrics_path):,} bytes)")

    return results_1, metrics_1, hashes, deterministic


if __name__ == "__main__":
    main()
