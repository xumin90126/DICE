"""
Independent Evaluation GT Assembly & Freeze
Combines Reviewer A/B results, computes agreement, adjudicates, freezes GT.
READ-ONLY: does not modify any frozen/production files.
Does NOT compute IS-01, IS-02, or any machine feature.
"""
import json, os, time, math
from collections import Counter, defaultdict

REVIEW_DIR = "tmp/perception/p7/independent_evaluation_human_review"

def load_reviewer_results(reviewer_id):
    """Load and combine results from batch files for a reviewer."""
    all_results = {}
    for batch_num in [1, 2]:
        # Try combined files first
        filepath = f"{REVIEW_DIR}/{reviewer_id}_results_batch_{batch_num*2-1}_{batch_num*2}.json"
        if not os.path.exists(filepath):
            # Try individual batch files
            for bn in [batch_num*2-1, batch_num*2]:
                fp = f"{REVIEW_DIR}/{reviewer_id}_results_batch_{bn}.json"
                if os.path.exists(fp):
                    with open(fp) as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        for r in data:
                            all_results[r["case_id"]] = r
                    elif isinstance(data, dict) and "results" in data:
                        for r in data["results"]:
                            all_results[r["case_id"]] = r
            continue
        
        with open(filepath) as f:
            data = json.load(f)
        
        if isinstance(data, list):
            for r in data:
                all_results[r["case_id"]] = r
        elif isinstance(data, dict) and "results" in data:
            for r in data["results"]:
                all_results[r["case_id"]] = r
        elif isinstance(data, dict):
            # Might be a single result or wrapper
            if "case_id" in data:
                all_results[data["case_id"]] = data
            else:
                for key, val in data.items():
                    if isinstance(val, list):
                        for r in val:
                            if isinstance(r, dict) and "case_id" in r:
                                all_results[r["case_id"]] = r
    
    return all_results


def load_all_reviewer_results(reviewer_id):
    """Try multiple file patterns to load reviewer results."""
    all_results = {}
    
    # Try all possible file patterns
    patterns = [
        f"{REVIEW_DIR}/{reviewer_id}_results_batch_1_2.json",
        f"{REVIEW_DIR}/{reviewer_id}_results_batch_3_4.json",
        f"{REVIEW_DIR}/{reviewer_id}_results.json",
        f"{REVIEW_DIR}/{reviewer_id}_batch_1_results.json",
        f"{REVIEW_DIR}/{reviewer_id}_batch_2_results.json",
        f"{REVIEW_DIR}/{reviewer_id}_batch_3_results.json",
        f"{REVIEW_DIR}/{reviewer_id}_batch_4_results.json",
    ]
    
    for filepath in patterns:
        if os.path.exists(filepath):
            with open(filepath) as f:
                data = json.load(f)
            
            if isinstance(data, list):
                for r in data:
                    if isinstance(r, dict) and "case_id" in r:
                        all_results[r["case_id"]] = r
            elif isinstance(data, dict):
                if "case_id" in data:
                    all_results[data["case_id"]] = data
                elif "results" in data:
                    for r in data["results"]:
                        if isinstance(r, dict) and "case_id" in r:
                            all_results[r["case_id"]] = r
                else:
                    for key, val in data.items():
                        if isinstance(val, list):
                            for r in val:
                                if isinstance(r, dict) and "case_id" in r:
                                    all_results[r["case_id"]] = r
    
    # Also scan directory for any files matching reviewer pattern
    if os.path.isdir(REVIEW_DIR):
        for fname in os.listdir(REVIEW_DIR):
            if fname.startswith(f"{reviewer_id}_") and fname.endswith(".json") and "results" in fname:
                filepath = os.path.join(REVIEW_DIR, fname)
                if filepath not in patterns:
                    with open(filepath) as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        for r in data:
                            if isinstance(r, dict) and "case_id" in r:
                                all_results[r["case_id"]] = r
                    elif isinstance(data, dict):
                        if "case_id" in data:
                            all_results[data["case_id"]] = data
                        elif "results" in data:
                            for r in data["results"]:
                                if isinstance(r, dict) and "case_id" in r:
                                    all_results[r["case_id"]] = r
    
    return all_results


def compute_cohens_kappa(decisions_a, decisions_b):
    """Compute Cohen's kappa for three-category agreement."""
    # Get common cases
    common = set(decisions_a.keys()) & set(decisions_b.keys())
    if not common:
        return 0.0, 0, {}
    
    categories = ["MERGE", "KEEP_SEPARATE", "CANNOT_DETERMINE"]
    
    # Build confusion matrix
    matrix = defaultdict(lambda: defaultdict(int))
    for cid in common:
        a = decisions_a[cid]
        b = decisions_b[cid]
        matrix[a][b] += 1
    
    n = len(common)
    
    # Observed agreement
    observed = sum(matrix[c][c] for c in categories) / n
    
    # Expected agreement
    a_marginal = {c: sum(matrix[c].values()) / n for c in categories}
    b_marginal = {c: sum(matrix[bc][c] for bc in categories) / n for c in categories}
    expected = sum(a_marginal[c] * b_marginal[c] for c in categories)
    
    if expected == 1.0:
        return 1.0, n, dict(matrix)
    
    kappa = (observed - expected) / (1 - expected)
    return kappa, n, {a: dict(b) for a, b in matrix.items()}


def main():
    print("=" * 100)
    print("INDEPENDENT EVALUATION GT ASSEMBLY & FREEZE")
    print("=" * 100)
    
    # Load reviewer results
    print("\n--- Loading Reviewer A results ---")
    reviewer_a = load_all_reviewer_results("reviewer_a")
    print(f"  Reviewer A: {len(reviewer_a)} cases loaded")
    
    print("\n--- Loading Reviewer B results ---")
    reviewer_b = load_all_reviewer_results("reviewer_b")
    print(f"  Reviewer B: {len(reviewer_b)} cases loaded")
    
    # Load sampling frame for case list
    with open("tmp/perception/p7/independent_evaluation_sampling_frame.json") as f:
        sf = json.load(f)
    all_case_ids = [c["case_id"] for c in sf["sampled_cases"]]
    print(f"\n  Total expected cases: {len(all_case_ids)}")
    
    # Check completeness
    missing_a = [cid for cid in all_case_ids if cid not in reviewer_a]
    missing_b = [cid for cid in all_case_ids if cid not in reviewer_b]
    print(f"  Missing from A: {len(missing_a)} {missing_a[:5]}")
    print(f"  Missing from B: {len(missing_b)} {missing_b[:5]}")
    
    if missing_a or missing_b:
        print("\n  ⚠️ INCOMPLETE - some cases missing")
    
    # Build decision maps
    decisions_a = {}
    decisions_b = {}
    
    for cid in all_case_ids:
        if cid in reviewer_a:
            dec = reviewer_a[cid].get("decision", "UNKNOWN")
            decisions_a[cid] = dec
        if cid in reviewer_b:
            dec = reviewer_b[cid].get("decision", "UNKNOWN")
            decisions_b[cid] = dec
    
    # Compute agreement
    common = set(decisions_a.keys()) & set(decisions_b.keys())
    print(f"\n--- Inter-Rater Agreement ---")
    print(f"  Common cases: {len(common)}")
    
    # Simple agreement
    agreements = sum(1 for cid in common if decisions_a[cid] == decisions_b[cid])
    agreement_rate = agreements / len(common) if common else 0
    print(f"  Simple agreement: {agreements}/{len(common)} = {agreement_rate:.1%}")
    
    # Cohen's kappa
    kappa, n, matrix = compute_cohens_kappa(decisions_a, decisions_b)
    print(f"  Cohen's kappa: {kappa:.3f}")
    
    # Interpretation
    if kappa >= 0.80:
        kappa_interp = "Strong agreement"
    elif kappa >= 0.60:
        kappa_interp = "Moderate agreement"
    else:
        kappa_interp = "Poor agreement"
    print(f"  Interpretation: {kappa_interp}")
    
    # Confusion matrix
    print(f"\n  Confusion matrix (A rows, B cols):")
    cats = ["MERGE", "KEEP_SEPARATE", "CANNOT_DETERMINE"]
    print(f"  {'':20s} {''.join(f'{c:>18s}' for c in cats)}")
    for a_cat in cats:
        row = [matrix.get(a_cat, {}).get(b_cat, 0) for b_cat in cats]
        print(f"  {a_cat:20s} {''.join(f'{r:>18d}' for r in row)}")
    
    # Decision distribution
    print(f"\n  Decision distribution:")
    print(f"    Reviewer A: {dict(Counter(decisions_a.values()))}")
    print(f"    Reviewer B: {dict(Counter(decisions_b.values()))}")
    
    # Identify agreements and disagreements
    agreed = []
    disagreements = []
    both_cannot = []
    
    for cid in common:
        a = decisions_a[cid]
        b = decisions_b[cid]
        
        if a == b:
            if a == "CANNOT_DETERMINE":
                both_cannot.append(cid)
            else:
                agreed.append(cid)
        else:
            disagreements.append(cid)
    
    print(f"\n  Agreed (MERGE/KEEP_SEPARATE): {len(agreed)}")
    print(f"  Both CANNOT_DETERMINE: {len(both_cannot)}")
    print(f"  Disagreements: {len(disagreements)}")
    
    if disagreements:
        print(f"\n  Disagreement details:")
        for cid in disagreements:
            print(f"    {cid}: A={decisions_a[cid]} B={decisions_b[cid]}")
    
    # === GENERATE SEMANTIC GT ===
    print(f"\n\n--- Generating Semantic GT ---")
    
    semantic_gt = {}
    gt_level = {}
    
    # Agreed cases → Level 2 GT (dual reviewer agreement)
    for cid in agreed:
        semantic_gt[cid] = decisions_a[cid]
        gt_level[cid] = "LEVEL_2_AGREED"
    
    # Both CANNOT_DETERMINE → UNRESOLVED
    for cid in both_cannot:
        semantic_gt[cid] = "UNRESOLVED"
        gt_level[cid] = "UNRESOLVED_BOTH_CANNOT"
    
    # Disagreements → need adjudication
    # For now, mark as PENDING_ADJUDICATION
    for cid in disagreements:
        semantic_gt[cid] = "PENDING_ADJUDICATION"
        gt_level[cid] = "PENDING_ADJUDICATION"
    
    print(f"  Level 2 GT (agreed): {len(agreed)}")
    print(f"  Unresolved (both CANNOT): {len(both_cannot)}")
    print(f"  Pending adjudication: {len(disagreements)}")
    print(f"  Total: {len(semantic_gt)}")
    
    # === ADJUDICATION (for disagreements) ===
    # Simple adjudication: if one says CANNOT and other says MERGE/SEPARATE,
    # use the non-CANNOT decision (single reviewer only, lower confidence)
    # If MERGE vs KEEP_SEPARATE, mark as UNRESOLVED (no adjudicator available)
    
    adjudicated = 0
    for cid in disagreements:
        a = decisions_a[cid]
        b = decisions_b[cid]
        
        if a == "CANNOT_DETERMINE" and b != "CANNOT_DETERMINE":
            # Use B's decision, mark as single-reviewer
            semantic_gt[cid] = b
            gt_level[cid] = "LEVEL_1_SINGLE_REVIEWER"
            adjudicated += 1
        elif b == "CANNOT_DETERMINE" and a != "CANNOT_DETERMINE":
            # Use A's decision, mark as single-reviewer
            semantic_gt[cid] = a
            gt_level[cid] = "LEVEL_1_SINGLE_REVIEWER"
            adjudicated += 1
        else:
            # MERGE vs KEEP_SEPARATE — true disagreement, no adjudicator
            semantic_gt[cid] = "UNRESOLVED"
            gt_level[cid] = "UNRESOLVED_DISAGREEMENT"
    
    print(f"\n  Adjudicated (single-reviewer): {adjudicated}")
    print(f"  Unresolved (disagreement): {sum(1 for v in gt_level.values() if v == 'UNRESOLVED_DISAGREEMENT')}")
    
    # === GT SUMMARY ===
    gt_summary = Counter(semantic_gt.values())
    level_summary = Counter(gt_level.values())
    
    print(f"\n--- Semantic GT Summary ---")
    print(f"  GT labels: {dict(gt_summary)}")
    print(f"  GT levels: {dict(level_summary)}")
    
    # Count usable GT (MERGE + KEEP_SEPARATE, excluding UNRESOLVED and PENDING)
    usable_gt = sum(1 for v in semantic_gt.values() if v in ["MERGE", "KEEP_SEPARATE"])
    unresolved = sum(1 for v in semantic_gt.values() if v == "UNRESOLVED")
    
    print(f"\n  Usable GT (MERGE/KEEP_SEPARATE): {usable_gt}")
    print(f"  Unresolved: {unresolved}")
    print(f"  Usable rate: {usable_gt}/{len(semantic_gt)} = {usable_gt/len(semantic_gt)*100:.1f}%")
    
    # === BUILD GT RECORDS ===
    gt_records = []
    for cid in all_case_ids:
        case_data = next(c for c in sf["sampled_cases"] if c["case_id"] == cid)
        
        record = {
            "case_id": cid,
            "document_id": case_data["doc_id"],
            "page": case_data["page"],
            "text_a": case_data["text_a"],
            "text_b": case_data["text_b"],
            "reviewer_a_decision": decisions_a.get(cid, "MISSING"),
            "reviewer_a_reason": reviewer_a.get(cid, {}).get("reason", ""),
            "reviewer_b_decision": decisions_b.get(cid, "MISSING"),
            "reviewer_b_reason": reviewer_b.get(cid, {}).get("reason", ""),
            "semantic_gt": semantic_gt.get(cid, "MISSING"),
            "gt_level": gt_level.get(cid, "MISSING"),
            "agreement_status": "AGREED" if cid in agreed else ("BOTH_CANNOT" if cid in both_cannot else "DISAGREEMENT"),
        }
        gt_records.append(record)
    
    # === FREEZE EVALUATION SET ===
    freeze_timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    
    evaluation_set = {
        "metadata": {
            "description": "Independent Evaluation Set with Semantic GT",
            "type": "FROZEN evaluation set",
            "creation_timestamp": freeze_timestamp,
            "freeze_status": "FROZEN",
            "freeze_timestamp": freeze_timestamp,
            "corpus": "4 INDEPENDENT PDFs (arxiv_2402, arxiv_bio2, qbio_genomics, qbio_rna)",
            "pipeline": "Frozen P1-P6 (no modification)",
            "sampling_seed": sf["metadata"]["sampling_seed"],
            "is01_is02_computed": False,
            "machine_prediction_computed": False,
            "note": "Semantic GT generated from blind dual-reviewer evaluation. "
                    "IS-01/IS-02 NOT computed. Machine prediction NOT computed. "
                    "GT is based on human semantic judgment, NOT geometry-based GT.",
        },
        "agreement_metrics": {
            "total_cases": len(all_case_ids),
            "common_cases": len(common),
            "simple_agreement": agreement_rate,
            "cohens_kappa": kappa,
            "kappa_interpretation": kappa_interp,
            "agreed": len(agreed),
            "both_cannot": len(both_cannot),
            "disagreements": len(disagreements),
            "adjudicated": adjudicated,
        },
        "gt_summary": {
            "total": len(semantic_gt),
            "usable_gt": usable_gt,
            "unresolved": unresolved,
            "by_label": dict(gt_summary),
            "by_level": dict(level_summary),
        },
        "reviewer_a_stats": {
            "total": len(reviewer_a),
            "decisions": dict(Counter(decisions_a.values())),
        },
        "reviewer_b_stats": {
            "total": len(reviewer_b),
            "decisions": dict(Counter(decisions_b.values())),
        },
        "gt_records": gt_records,
    }
    
    out_path = "tmp/perception/p7/independent_evaluation_semantic_gt.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(evaluation_set, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n=== EVALUATION SET FROZEN ===")
    print(f"  File: {out_path}")
    print(f"  Size: {os.path.getsize(out_path):,} bytes")
    print(f"  Freeze timestamp: {freeze_timestamp}")
    print(f"  EVALUATION_SET_FREEZE = TRUE")
    print(f"  IS-01/IS-02 computed: FALSE")
    print(f"  Machine prediction computed: FALSE")
    
    return evaluation_set


if __name__ == "__main__":
    main()
