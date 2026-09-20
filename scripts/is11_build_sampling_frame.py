"""
IS-11 Independent Sampling Frame Construction
READ-ONLY: stratified random sampling from frozen candidate universe.
Uses ONLY geometric features for stratification (no IS-11, no IS-01/IS-02, no human intuition).
Sampling seed is fixed and recorded.
"""
import json, os, time, random, hashlib
from collections import Counter, defaultdict

def main():
    print("=" * 100)
    print("IS-11 INDEPENDENT SAMPLING FRAME CONSTRUCTION")
    print("=" * 100)

    # Load frozen candidate universe
    with open("tmp/is11_independent_candidate_universe.json") as f:
        universe = json.load(f)

    candidates = universe["ambiguous_cases"]
    print(f"\nTotal AMBIGUOUS candidates: {len(candidates)}")

    # === SAMPLING RULE (pre-registered, geometry-only) ===
    # Stratification dimensions (ALL geometric, NO IS-11, NO text content):
    # 1. document_id (ensure cross-document coverage)
    # 2. h_gap bin (geometric density)
    # 3. w_b bin (text width)
    # 4. line_obs_count bin (line density)
    #
    # Target: ≥40 cases (exceeds ≥30 minimum), proportional to document distribution
    # but with minimum 8 per document to ensure cross-document coverage

    SAMPLING_SEED = 20240909
    TARGET_SAMPLE = 45  # ≥30 minimum + buffer for potential exclusions
    MIN_PER_DOC = 8     # ensure cross-document coverage

    # Define geometric strata
    def gap_bin(gap):
        if gap <= 12: return "g1_8_12"
        elif gap <= 20: return "g2_12_20"
        elif gap <= 30: return "g3_20_30"
        else: return "g4_30_50"

    def wb_bin(wb):
        if wb < 30: return "w1_15_30"
        elif wb < 60: return "w2_30_60"
        else: return "w3_60plus"

    def lo_bin(lo):
        if lo <= 3: return "l1_0_3"
        elif lo <= 6: return "l2_4_6"
        elif lo <= 10: return "l3_7_10"
        else: return "l4_11_15"

    # Build strata
    for c in candidates:
        c["_stratum"] = f"{c['doc_id']}|{gap_bin(c['h_gap'])}|{wb_bin(c['w_b'])}|{lo_bin(c['line_obs_count'])}"

    # Document distribution
    doc_counts = Counter(c["doc_id"] for c in candidates)
    print(f"\n--- Document Distribution ---")
    for doc, count in sorted(doc_counts.items()):
        print(f"  {doc}: {count}")

    # Proportional allocation with minimum per document
    total = len(candidates)
    doc_allocations = {}
    for doc, count in doc_counts.items():
        proportional = int(TARGET_SAMPLE * count / total)
        doc_allocations[doc] = max(MIN_PER_DOC, proportional)

    # Adjust if total exceeds TARGET_SAMPLE
    while sum(doc_allocations.values()) > TARGET_SAMPLE:
        # Reduce from largest allocation
        max_doc = max(doc_allocations, key=doc_allocations.get)
        if doc_allocations[max_doc] > MIN_PER_DOC:
            doc_allocations[max_doc] -= 1
        else:
            break

    print(f"\n--- Sampling Allocations (seed={SAMPLING_SEED}) ---")
    for doc in sorted(doc_allocations.keys()):
        print(f"  {doc}: {doc_allocations[doc]}")
    print(f"  Total target: {sum(doc_allocations.values())}")

    # Stratified random sampling within each document
    random.seed(SAMPLING_SEED)

    sampled = []
    for doc_id, n_sample in doc_allocations.items():
        doc_candidates = [c for c in candidates if c["doc_id"] == doc_id]

        # Sub-stratify by gap_bin for diversity within document
        gap_strata = defaultdict(list)
        for c in doc_candidates:
            gap_strata[gap_bin(c["h_gap"])].append(c)

        # Allocate samples across gap strata proportionally
        n_doc = len(doc_candidates)
        doc_sampled = []

        for stratum, stratum_cases in gap_strata.items():
            n_stratum = max(1, int(n_sample * len(stratum_cases) / n_doc))
            n_stratum = min(n_stratum, len(stratum_cases))
            # Sort by case_id for deterministic ordering before random selection
            stratum_cases.sort(key=lambda c: c["case_id"])
            selected = random.sample(stratum_cases, n_stratum)
            doc_sampled.extend(selected)

        # If under-allocated, fill from remaining
        if len(doc_sampled) < n_sample:
            remaining = [c for c in doc_candidates if c not in doc_sampled]
            n_extra = min(n_sample - len(doc_sampled), len(remaining))
            remaining.sort(key=lambda c: c["case_id"])
            doc_sampled.extend(random.sample(remaining, n_extra))

        # If over-allocated, trim
        if len(doc_sampled) > n_sample:
            doc_sampled.sort(key=lambda c: c["case_id"])
            doc_sampled = doc_sampled[:n_sample]

        sampled.extend(doc_sampled)
        print(f"  {doc_id}: sampled {len(doc_sampled)} / {len(doc_candidates)}")

    # Sort final sample by case_id
    sampled.sort(key=lambda c: c["case_id"])

    # Remove internal stratum field
    for c in sampled:
        c.pop("_stratum", None)

    print(f"\n--- Final Sample: {len(sampled)} cases ---")

    # Verify distribution
    print(f"\n--- Sample Document Distribution ---")
    sample_doc_counts = Counter(c["doc_id"] for c in sampled)
    for doc, count in sorted(sample_doc_counts.items()):
        print(f"  {doc}: {count}")

    print(f"\n--- Sample Gap Distribution ---")
    sample_gap = Counter()
    for c in sampled:
        sample_gap[gap_bin(c["h_gap"])] += 1
    for bucket, count in sorted(sample_gap.items()):
        print(f"  {bucket}: {count}")

    print(f"\n--- Sample w_b Distribution ---")
    sample_wb = Counter()
    for c in sampled:
        sample_wb[wb_bin(c["w_b"])] += 1
    for bucket, count in sorted(sample_wb.items()):
        print(f"  {bucket}: {count}")

    print(f"\n--- Sample line_obs Distribution ---")
    sample_lo = Counter()
    for c in sampled:
        sample_lo[lo_bin(c["line_obs_count"])] += 1
    for bucket, count in sorted(sample_lo.items()):
        print(f"  {bucket}: {count}")

    # Page distribution
    print(f"\n--- Sample Page Distribution ---")
    sample_pages = Counter((c["doc_id"], c["page"]) for c in sampled)
    for (doc, page), count in sorted(sample_pages.items()):
        print(f"  {doc} page {page}: {count}")

    # === SAVE SAMPLING FRAME ===
    output = {
        "metadata": {
            "description": "IS-11 Independent Sampling Frame",
            "type": "READ-ONLY sampling frame (Stage 2)",
            "creation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "sampling_rule": "stratified random sampling (geometry-only stratification)",
            "sampling_seed": SAMPLING_SEED,
            "target_sample_size": TARGET_SAMPLE,
            "minimum_per_document": MIN_PER_DOC,
            "stratification_dimensions": [
                "document_id (cross-document coverage)",
                "h_gap bin (geometric density: 8-12, 12-20, 20-30, 30-50)",
                "w_b bin (text width: 15-30, 30-60, 60+)",
                "line_obs_count bin (line density: 0-3, 4-6, 7-10, 11-15)",
            ],
            "stratification_note": "ALL stratification dimensions are geometric. NO IS-11, IS-01, IS-02, text content, or human intuition used.",
            "source_universe": "tmp/is11_independent_candidate_universe.json",
            "source_universe_size": len(candidates),
            "is11_computed": False,
            "is01_is02_computed": False,
            "human_gt_collected": False,
        },
        "summary": {
            "total_sampled": len(sampled),
            "by_document": dict(sample_doc_counts),
            "by_gap_bin": dict(sample_gap),
            "by_wb_bin": dict(sample_wb),
            "by_lo_bin": dict(sample_lo),
        },
        "sampled_cases": sampled,
    }

    out_path = "tmp/is11_independent_sampling_frame.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Sampling frame saved: {out_path}")
    print(f"   Size: {os.path.getsize(out_path):,} bytes")

    # Verify freeze
    sf_sha = hashlib.sha256(open(out_path, 'rb').read()).hexdigest()
    print(f"   SHA-256: {sf_sha}")
    print(f"\n   FREEZE STATUS: FROZEN")

    return sampled


if __name__ == "__main__":
    main()
