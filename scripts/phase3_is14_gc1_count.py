"""
Phase 3 — G-C1 Corpus Sufficiency Count (pre-evaluation gate).
Runs the FROZEN IS-14 observer over the FROZEN sample (n=54) and counts:
  - figure-context cases
  - control cases
Pre-registered counting definition (recorded here BEFORE the run):
  figure-context := NOT in_table AND ( (i) OBS-A match on either fragment
    OR (ii) either fragment inside a text block containing >=1 caption-label span,
            or inside a continuation block (<=14pt, same column, no new label) of such a block
    OR (iii) OBS-C numeric_tick_run true for BOTH fragments )
  control := NOT figure-context
The count output is used ONLY for the G-C1 go/no-go decision. It is never shown to
reviewers/adjudicators and never used to include/exclude cases (sample was already frozen).
"""
import sys, json
sys.path.insert(0, 'tmp')
from phase3_is14_observer import (observe_case, _get_page_data, _center, _point_in_rect,
                                  _block_of_point, CAPTION_RE, OBS_B_BLOCK_GAP_MAX)

def caption_block_membership(page_data, bbox):
    """Counting-rule (ii): fragment inside a caption-label block or its continuation block."""
    fc = _center(bbox)
    blk = _block_of_point(page_data, fc[0], fc[1])
    if blk is None:
        return False, None
    if any(CAPTION_RE.match(s["text"]) for s in blk["spans"]):
        return True, "inside_caption_block"
    # continuation of a caption block: vertical gap <=14, horizontal overlap, no new label inside
    for other in page_data["text_blocks"]:
        if other["block_index"] == blk["block_index"]:
            continue
        if not any(CAPTION_RE.match(s["text"]) for s in other["spans"]):
            continue
        lb, cbx = other["bbox"], blk["bbox"]
        gap_below = cbx[1] - lb[3]
        gap_above = lb[1] - cbx[3]
        gap = gap_below if gap_below >= 0 else (gap_above if gap_above >= 0 else -1.0)
        h_overlap = min(lb[2], cbx[2]) - max(lb[0], cbx[0])
        no_new_label = not any(CAPTION_RE.match(s["text"]) for s in blk["spans"])
        if gap >= 0 and gap <= OBS_B_BLOCK_GAP_MAX and h_overlap > 0 and no_new_label:
            return True, f"continuation_of_caption_block_{other['block_index']}"
    return False, None

def main():
    sf = json.load(open("tmp/phase3_is14_sampling_manifest.json"))
    cases = sf["sampled_cases"]

    results = []
    n_fig, n_ctrl, n_table_domain = 0, 0, 0
    fig_types = {"obs_a": 0, "caption_block": 0, "tick_run": 0}

    for c in cases:
        r = observe_case(c["pdf_path"], c["page"], c["bbox_a"], c["bbox_b"], c["text_a"], c["text_b"])
        in_table = r["is11_asrun_domain"]["is_in_table"]
        if in_table:
            n_table_domain += 1
            results.append({"case_id": c["case_id"], "doc_id": c["doc_id"], "page": c["page"],
                            "in_table": True, "figure_context": False, "reason": "table domain (IS-11)"})
            continue

        pd = _get_page_data(c["pdf_path"], c["page"])
        g = r["graphic_text_context"]
        oa_any = g["obs_a"]["fragment_a"]["caption_label_match"] or g["obs_a"]["fragment_b"]["caption_label_match"]
        oc_both = g["obs_c"]["fragment_a"]["numeric_tick_run"] and g["obs_c"]["fragment_b"]["numeric_tick_run"]
        mb_a, why_a = caption_block_membership(pd, c["bbox_a"])
        mb_b, why_b = caption_block_membership(pd, c["bbox_b"])

        is_fig = False
        reasons = []
        if oa_any:
            is_fig = True; reasons.append("obs_a"); fig_types["obs_a"] += 1
        if mb_a or mb_b:
            is_fig = True; reasons.append("caption_block:" + (why_a or "") + "|" + (why_b or "")); fig_types["caption_block"] += 1
        if oc_both:
            is_fig = True; reasons.append("tick_run"); fig_types["tick_run"] += 1

        if is_fig:
            n_fig += 1
        else:
            n_ctrl += 1
        results.append({"case_id": c["case_id"], "doc_id": c["doc_id"], "page": c["page"],
                        "in_table": False, "figure_context": is_fig,
                        "reasons": reasons, "text_a": c["text_a"][:40], "text_b": c["text_b"][:40]})

    # structure-type distribution
    by_doc_fig = {}
    by_doc_ctrl = {}
    for r in results:
        d = r["doc_id"]
        by_doc_fig.setdefault(d, 0); by_doc_ctrl.setdefault(d, 0)
        if r["figure_context"]:
            by_doc_fig[d] += 1
        else:
            by_doc_ctrl[d] += 1

    out = {
        "metadata": {
            "purpose": "G-C1 corpus sufficiency count (pre-evaluation gate)",
            "counting_definition_frozen_before_run": True,
            "definition": "figure-context := NOT in_table AND (OBS-A on either fragment OR caption-block membership (block contains caption-label or continuation block <=14pt same-column no-new-label) OR OBS-C both fragments); control := NOT figure-context",
            "firewall": "count used ONLY for G-C1 gate; never shown to reviewers; sample frozen before counting; no case included/excluded by this output",
        },
        "g_c1_counts": {
            "sample_size": len(results),
            "figure_context_cases": n_fig,
            "control_cases": n_ctrl,
            "table_domain_cases": n_table_domain,
            "required_figure_context": 15,
            "required_control": 20,
        },
        "figure_type_counts": fig_types,
        "by_document": {d: {"figure_context": by_doc_fig[d], "control": by_doc_ctrl[d]} for d in sorted(by_doc_fig)},
        "case_detail": results,
    }

    with open("tmp/phase3_is14_gc1_count.json", "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print("=" * 90)
    print("G-C1 CORPUS SUFFICIENCY COUNT")
    print("=" * 90)
    print(f"sample_size={len(results)}, figure_context={n_fig}, control={n_ctrl}, table_domain={n_table_domain}")
    print(f"figure types: {fig_types}")
    print("\nBy document:")
    for d in sorted(by_doc_fig):
        print(f"  {d}: figure={by_doc_fig[d]}, control={by_doc_ctrl[d]}")
    print(f"\nG-C1 requirement: figure_context >= 15 ({'PASS' if n_fig >= 15 else 'FAIL'}), control >= 20 ({'PASS' if n_ctrl >= 20 else 'FAIL'})")
    print(f"G-C1 = {'PASS' if n_fig >= 15 and n_ctrl >= 20 else 'FAIL'}")

if __name__ == "__main__":
    main()
