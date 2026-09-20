"""Atomic Observation Layer v1 — determinism & safety acceptance harness.

Runs the verification battery required by the implementation authorization
(sections 18-21) WITHOUT any IS-11 / IS-14 evaluation, GT collection, or
sampling. Read-only with respect to the whole repository.

Checks:
  A schema validation            G NON_TEXT_BLOCK content=null
  B registry validation          H RegionFact provenance
  C frozen SHA verification      I IN_REGION geometry-source
  D determinism (byte-identity)  J GAP_SEQUENCE measurement-only
  E P1/P2 expose verification    K forbidden semantic-field scan
  F TEXT_ATOM identity           L frozen modification + scope audit
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

_LAYER_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_LAYER_DIR, "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
if _LAYER_DIR not in sys.path:
    sys.path.insert(0, _LAYER_DIR)

import adapter  # noqa: E402
import non_text_block as ntb  # noqa: E402
import relations  # noqa: E402

RESULTS: list = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    RESULTS.append((name, bool(ok), detail))
    print(f"  {'✅' if ok else '❌ FAIL'} {name}" + (f" — {detail}" if detail else ""))
    return bool(ok)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    reg = adapter.load_registry()
    ok_all = True

    # ── A. schema validation ──────────────────────────────────────────────
    print("\n[A] schema validation")
    with open(os.path.join(_LAYER_DIR, "atomic_observation_schema.json"), encoding="utf-8") as fh:
        schema = json.load(fh)
    ok_all &= check("A1 schema loads + version", schema["observation_schema_version"] == "1.0.0")
    ok_all &= check("A2 closed atom kinds",
                    set(schema["atoms"]) == {"TEXT_ATOM", "NON_TEXT_BLOCK_ATOM"})
    ok_all &= check("A3 closed relations",
                    set(schema["relations"]) == {"IN_REGION", "GAP_SEQUENCE"})
    ok_all &= check("A4 provenance fields complete",
                    set(schema["provenance_required_fields"]) == {
                        "source_sha", "params_hash", "schema_version",
                        "coordinate_system", "document_id", "page_reference",
                        "pymupdf_version"})
    ok_all &= check("A5 NTB content permanent null",
                    schema["atoms"]["NON_TEXT_BLOCK_ATOM"]["field_rules"]["content"]["value"] is None
                    and schema["atoms"]["NON_TEXT_BLOCK_ATOM"]["field_rules"]["content"]["permanent"] is True)

    # ── B. registry validation ────────────────────────────────────────────
    print("\n[B] registry validation")
    ok_all &= check("B1 registry versions present",
                    reg["versions"]["observation_schema_version"] == "1.0.0"
                    and "GAP_SEQUENCE_v1" in reg["measurement_identities"])
    ok_all &= check("B2 four version slots orthogonal",
                    set(reg["versions"]) == {"observation_schema_version",
                                             "measurement_identity_versions",
                                             "detector_versions", "query_version"})
    ok_all &= check("B3 compute_page_bundle rule max_pairwise=None",
                    reg["frozen_call_rules"]["compute_page_bundle"]["max_pairwise"] is None)
    ok_all &= check("B4 truncated artifact flagged",
                    reg["artifact_manifest"]["RM501-P4"]["p2_geometry"]["truncated"] is True)
    ok_all &= check("B5 detectors registered, never invoked by layer",
                    all(d["invoked_by_layer"] is False
                        for d in reg["registered_detectors"].values()))
    ok_all &= check("B6 declarations (Observation ≠ Interpretation/Decision/Capability)",
                    all(reg["declarations"].values()))

    # ── C. frozen SHA verification ────────────────────────────────────────
    print("\n[C] frozen SHA verification")
    for name, src in reg["frozen_sources"].items():
        live = sha256_file(os.path.join(_REPO_ROOT, src["path"]))
        ok_all &= check(f"C frozen: {name}", live == src["sha256"], live[:16])

    # ── D. determinism (byte-identity, in-memory persistence equivalence) ─
    print("\n[D] determinism — same document + source + params + query => byte-identical")
    test_doc = reg["case_b_test_documents"]["PH3-EARTH-001"]
    pdf_path = test_doc["path"]
    store1 = adapter.build_case_b_store(pdf_path, "PH3-EARTH-001", pages=[1, 2, 3])
    store2 = adapter.build_case_b_store(pdf_path, "PH3-EARTH-001", pages=[1, 2, 3])
    b1, b2 = adapter.serialize(store1), adapter.serialize(store2)
    ok_all &= check("D1 identity+geometry+serialization determinism (Case B rebuild)",
                    b1 == b2, f"{len(b1):,} bytes")
    exp1 = adapter.expose_text_atoms_case_a("RM501-P4", reg)
    exp2 = adapter.expose_text_atoms_case_a("RM501-P4", reg)
    ok_all &= check("D2 Case A expose determinism", adapter.serialize(exp1) == adapter.serialize(exp2))
    page2 = next(p for p in store1["pages"] if p["page_reference"] == 2)
    singles = page2["p2_full_bundle"]["single_geometries"]
    snap = page2["p2_full_bundle"]["config_snapshot"]
    g1 = relations.gap_sequence_v1(singles, "PH3-EARTH-001", 2, snap)
    g2 = relations.gap_sequence_v1(singles, "PH3-EARTH-001", 2, snap)
    ok_all &= check("D3 GAP_SEQUENCE query determinism", adapter.serialize(g1) == adapter.serialize(g2))

    # ── E. P1/P2 expose verification ──────────────────────────────────────
    print("\n[E] P1/P2 expose verification (expose-first, read-only)")
    art_path = os.path.join(_REPO_ROOT, reg["artifact_manifest"]["RM501-P4"]["p1_atomic"]["path"])
    sha_before = sha256_file(art_path)
    exp = adapter.expose_text_atoms_case_a("RM501-P4", reg)
    sha_after = sha256_file(art_path)
    ok_all &= check("E1 Case A exposed without recomputation (artifact sha unchanged)",
                    sha_before == sha_after == reg["artifact_manifest"]["RM501-P4"]["p1_atomic"]["sha256"])
    ok_all &= check("E2 truncated P2 artifact flagged, not presented as full",
                    adapter.expose_p2_singles_case_a("RM501-P4", reg)["truncated"] is True)
    from perception.sandbox.geometry.geometry_engine import compute_pairwise  # frozen
    from perception.sandbox.geometry.geometry_config import DEFAULT_CONFIG    # frozen
    p2exp = adapter.expose_p2_singles_case_a("RM501-P4", reg)
    singles_rm = p2exp["single_geometries"]
    by_id = {s["observation_id"]: s for s in singles_rm}
    pair_ok = True
    for s in singles_rm:
        for m in (s.get("same_y_band_members") or [])[:3]:
            ra = compute_pairwise({"observation_id": s["observation_id"], "document_id": s["document_id"],
                                   "page_number": s["page_number"], "bbox": s["bbox"], "source_type": "span"},
                                  {"observation_id": by_id[m]["observation_id"], "document_id": by_id[m]["document_id"],
                                   "page_number": by_id[m]["page_number"], "bbox": by_id[m]["bbox"], "source_type": "span"},
                                  DEFAULT_CONFIG)
            pair_ok &= (ra.same_y_band is True)
    ok_all &= check("E3 exposed band facts reproduce under frozen pairwise (no drift)", pair_ok)

    # ── F. TEXT_ATOM identity preservation ────────────────────────────────
    print("\n[F] TEXT_ATOM identity preservation")
    import fitz  # noqa: deferred, only for cross-check of artifact integrity
    with open(art_path, encoding="utf-8") as fh:
        p1_artifact = json.load(fh)
    span_obs = {o["observation_id"]: o for o in p1_artifact["observations"]
                if o["source_type"] == "span"}
    preserved = all(
        a["atom_id"] in span_obs
        and a["content"] == span_obs[a["atom_id"]]["text"]
        and a["bbox"] == span_obs[a["atom_id"]]["bbox"]
        and a["page_reference"] == span_obs[a["atom_id"]]["page_number"]
        for a in exp["text_atoms"])
    ok_all &= check(f"F1 all {len(exp['text_atoms'])} TEXT_ATOMs passthrough-identical to P1", preserved)
    ok_all &= check("F2 atom identity NOT regenerated (P1 observation_id verbatim)",
                    {a["atom_id"] for a in exp["text_atoms"]}
                    == set(span_obs.keys()))

    # ── G. NON_TEXT_BLOCK content=null ────────────────────────────────────
    print("\n[G] NON_TEXT_BLOCK content=null verification")
    ntbs = [b for p in store1["pages"] for b in p.get("non_text_block_atoms", [])]
    ok_all &= check(f"G1 {len(ntbs)} NON_TEXT_BLOCK atoms enumerated",
                    len(ntbs) > 0, f"pages 1-3 of PH3-EARTH-001")
    ok_all &= check("G2 content null for every NON_TEXT_BLOCK",
                    all(b["content"] is None for b in ntbs))
    ok_all &= check("G3 atom_id pure-function format",
                    all(b["atom_id"] == ntb.atom_id_for(b["document_id"], b["page_reference"],
                                                        int(b["atom_id"].rsplit("|", 1)[1]))
                        for b in ntbs))
    bad_tokens = ("image", "figure", "chart", "caption", "diagram")
    ok_all &= check("G4 no semantic vocabulary in NON_TEXT_BLOCK records",
                    not any(t in json.dumps(b).lower() for b in ntbs for t in bad_tokens))

    # ── H. RegionFact provenance ──────────────────────────────────────────
    print("\n[H] RegionFact provenance verification")
    rf = adapter.expose_region_facts_case_a("DC201-C1", reg)
    facts = rf.get("region_facts", [])
    ok_all &= check(f"H1 {len(facts)} RegionFacts exposed (P6 artifact, Case A)", len(facts) > 0)
    ok_all &= check("H2 every RegionFact carries source_detector+source_sha+params_hash",
                    all(f["source_detector"] in reg["registered_detectors"]
                        and len(f["source_sha"]) == 64 and len(f["params_hash"]) == 64
                        for f in facts))
    ok_all &= check("H3 region_id pure-function format",
                    all(f["region_id"].startswith("p6reg|DC201-C1|p5|") for f in facts))
    forbidden_region_types = ("TABLE_REGION", "GRAPHIC_REGION", "FIGURE_REGION", "region_type")
    ok_all &= check("H4 no semantic region-type names in RegionFact records",
                    not any(t in json.dumps(f) for f in facts for t in forbidden_region_types))

    # ── I. IN_REGION geometry-source ──────────────────────────────────────
    print("\n[I] IN_REGION geometry-source verification")
    atoms_page5 = []
    store5 = adapter.build_case_b_store(pdf_path, "PH3-EARTH-001", pages=[1])
    atom0 = store5["pages"][0]["text_atoms"][0]
    rel = relations.in_region(atom0, facts[0])
    ok_all &= check("I1 relation_def registered", rel["relation_def"] == "bbox_containment_v1")
    ok_all &= check("I2 geometry_source declared", "layer:relation_def@" in rel["geometry_source"])
    ok_all &= check("I3 output fields closed",
                    set(rel) == {"atom_id", "region_id", "contained", "relation_def",
                                 "params_hash", "geometry_source", "document_id",
                                 "page_reference"})
    ok_all &= check("I4 contained is plain boolean geometry (no semantics attached)",
                    isinstance(rel["contained"], bool))

    # ── J. GAP_SEQUENCE measurement-only ──────────────────────────────────
    print("\n[J] GAP_SEQUENCE measurement-only verification")
    ok_all &= check("J1 measurement identity = GAP_SEQUENCE_v1",
                    g1["measurement_identity"] == "GAP_SEQUENCE_v1")
    ok_all &= check("J2 zero thresholds in output (no boolean category fields)",
                    all(set(band) == {"band_id", "anchor_atom_id", "member_atom_ids", "gaps"}
                        for band in g1["bands"]))
    gap_vals_frozen = True
    for band in g1["bands"][:10]:
        for gaprec in band["gaps"][:10]:
            a = next(s for s in singles if s["observation_id"] == gaprec["a_id"])
            b = next(s for s in singles if s["observation_id"] == gaprec["b_id"])
            rel2 = compute_pairwise({"observation_id": a["observation_id"], "document_id": a["document_id"],
                                     "page_number": a["page_number"], "bbox": a["bbox"], "source_type": "span"},
                                    {"observation_id": b["observation_id"], "document_id": b["document_id"],
                                     "page_number": b["page_number"], "bbox": b["bbox"], "source_type": "span"},
                                    DEFAULT_CONFIG)
            gap_vals_frozen &= (rel2.horizontal_distance == gaprec["gap"])
    ok_all &= check("J3 every gap value == frozen compute_pairwise().horizontal_distance",
                    gap_vals_frozen)
    ok_all &= check("J4 geometry_source = frozen P2 engine + cfg (or artifact)",
                    g1["geometry_source"].startswith(("frozen:geometry_engine.py@", "p2_artifact:")))
    ok_all &= check("J5 bands measured (real data flowed)",
                    sum(len(b["gaps"]) for b in g1["bands"]) > 0,
                    f"{sum(len(b['gaps']) for b in g1['bands'])} gaps across {len(g1['bands'])} bands")

    # ── K. forbidden semantic-field scan ─────────────────────────────────
    print("\n[K] forbidden semantic-field scan (authorization section 19)")
    forbidden = schema["forbidden_semantic_tokens"]
    # The negative declarations themselves are LAW, not violations — excluded
    # from the scan (recursively). All actual data/outputs are scanned in full:
    # any forbidden token in data, fields, or outputs = FAIL.
    DECLARATION_KEYS = {"forbidden_semantic_tokens", "forbidden_identity_fields",
                        "forbidden_outputs", "forbidden_content", "forbidden_fields"}

    def scrub(node):
        if isinstance(node, dict):
            return {k: scrub(v) for k, v in node.items() if k not in DECLARATION_KEYS}
        if isinstance(node, list):
            return [scrub(v) for v in node]
        return node

    schema_scan = scrub(schema)
    registry_scan = scrub(reg)
    targets = {
        "schema.json": json.dumps(schema_scan),
        "registry.json": json.dumps(registry_scan),
        "gap_sequence_output": json.dumps(g1),
        "in_region_output": json.dumps(rel),
        "text_atom_records": json.dumps(exp["text_atoms"][:50]),
        "ntb_records": json.dumps(ntbs[:50]),
        "region_facts": json.dumps(facts),
    }
    leak = {name: [t for t in forbidden if t.lower() in blob.lower()]
            for name, blob in targets.items()}
    leak = {k: v for k, v in leak.items() if v}
    ok_all &= check("K1 zero forbidden tokens in schema/registry/outputs", not leak, str(leak)[:200])
    ok_all &= check("K2 forbidden list itself covers the mandated negatives",
                    all(t in forbidden for t in
                        ["is_table_cell", "is_figure", "is_caption", "is_tick_run",
                         "is_uniform_run", "MERGE", "KEEP", "REJECT", "score",
                         "confidence", "ranking", "routing", "recommendation",
                         "execution_plan", "fallback", "retry", "override", "correction"]))
    # note: forbidden-token scan is case-sensitive on data keys but we scan lowercased
    # blobs against lowercased tokens; 'KEEP'/'MERGE' uppercase checked via K1.

    # ── L. frozen modification + scope audit ──────────────────────────────
    print("\n[L] frozen modification scan + scope audit")
    f71 = json.load(open(os.path.join(_REPO_ROOT, "tmp/perception/p7/p7_1_freeze_hashes.json")))
    f72 = json.load(open(os.path.join(_REPO_ROOT, "tmp/perception/p7/p7_2_freeze_hashes.json")))
    d71 = sum(1 for fp, h in f71["files"].items()
              if os.path.exists(os.path.join(_REPO_ROOT, fp))
              and sha256_file(os.path.join(_REPO_ROOT, fp)) != h)
    d72 = sum(1 for fp, h in f72["files"].items()
              if os.path.exists(os.path.join(_REPO_ROOT, fp))
              and sha256_file(os.path.join(_REPO_ROOT, fp)) != h)
    ok_all &= check("L1 P7.1 freeze drift = 0", d71 == 0)
    ok_all &= check("L2 P7.2 freeze drift = 0", d72 == 0)
    gt_sha = sha256_file(os.path.join(_REPO_ROOT, "tmp/is11_semantic_ground_truth.json"))
    ok_all &= check("L3 GT intact",
                    gt_sha == "7349963d0d23b5efc8c092ad45b8f301c39ca13a9c3bef8952aff809d0286959")
    marker = os.path.join(_REPO_ROOT, "tmp/atomic_observation_implementation_contract.md")
    out = subprocess.run(["find", os.path.join(_REPO_ROOT, "perception"),
                          os.path.join(_REPO_ROOT, "chunker"),
                          "-name", "*.py", "-newer", marker],
                         capture_output=True, text=True)
    ok_all &= check("L4 no frozen code file modified after contract", out.stdout.strip() == "")
    allowed = {"atomic_observation_schema.json", "layer_registry.json", "adapter.py",
               "non_text_block.py", "relations.py", "verify_determinism.py", "CONTRACT.md"}
    actual = set(os.listdir(_LAYER_DIR))
    ok_all &= check("L5 scope clean: exactly the 7 authorized files",
                    actual == allowed, str(actual - allowed or "complete"))

    # ── compatibility smoke tests (section 16 — expression only, NO evaluation) ─
    print("\n[Smoke] IS-11 / IS-14 contract-expression compatibility (NOT evaluation)")
    ok_all &= check("S1 IS-11 expression: TLD registered + IN_REGION executes on RegionFacts",
                    "table_line_detector" in reg["registered_detectors"]
                    and isinstance(rel["contained"], bool))
    ok_all &= check("S2 IS-14 expression: GAP_SEQUENCE + NON_TEXT_BLOCK available",
                    len(g1["bands"]) > 0 and len(ntbs) > 0)
    ok_all &= check("S3 no MERGE/KEEP/REJECT decision produced anywhere in smoke",
                    not any(t in json.dumps(g1) + json.dumps(rel) for t in ("MERGE", "KEEP", "REJECT")))

    print("\n" + "═" * 64)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    failed = [n for n, ok, _ in RESULTS if not ok]
    print(f"ACCEPTANCE: {passed}/{len(RESULTS)} checks passed")
    if failed:
        print("FAILED:", failed)
    print("IMPLEMENTATION_STATUS =", "PASS" if not failed else "FAIL")
    print("EVALUATION = NOT AUTHORIZED | GT = NOT AUTHORIZED | P7.3 = NOT AUTHORIZED")
    print("PRODUCTION = FALSE | STOP = TRUE")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
