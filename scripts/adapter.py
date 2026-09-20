"""Atomic Observation Layer v1 — expose-first adapter.

Contract: tmp/atomic_observation_implementation_contract.md section 5.

  CASE A: registered artifact exists + sha verified -> expose verbatim,
          no recomputation, provenance = artifact sha, zero geometry transform.
  CASE B: no artifact -> ONLY whitelisted frozen functions
          (extract_pdf_observations / compute_page_bundle with max_pairwise=None),
          persisted as a layer artifact; next access = CASE A of the layer store.
  Truncated P2 artifacts (max_pairwise=2000) expose singles only, flagged
  `truncated: true`; GAP_SEQUENCE refuses them (never masquerade as full).

The layer NEVER: re-implements geometry, invokes detectors, arbitrates regions,
or emits decisions (MERGE/KEEP/REJECT/score/confidence/...).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from typing import Any, Dict, List, Optional

_LAYER_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_LAYER_DIR, "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from perception.sandbox.observations.atomic_text import (  # noqa: E402  (frozen whitelist)
    extract_pdf_observations,
    pymupdf_version,
)
from perception.sandbox.geometry.geometry_engine import (  # noqa: E402  (frozen whitelist)
    compute_page_bundle,
)
from perception.sandbox.geometry.geometry_config import (  # noqa: E402  (frozen whitelist)
    DEFAULT_CONFIG,
)

import non_text_block as ntb  # noqa: E402  (layer-local, sanctioned new surface)

SCHEMA_VERSION = "1.0.0"
COORDINATE_SYSTEM = "pymupdf_page_1.26.x_y_down"
P1_FROZEN_SHA = "74d23ec784d657825780b35627f1b766ad87bd4dd74d88bbe4d560941f3b724a"
TEXT_ATOM_KIND = "TEXT_ATOM"
SOURCE_SPAN = "span"


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha_obj(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def load_registry() -> Dict[str, Any]:
    with open(os.path.join(_LAYER_DIR, "layer_registry.json"), "r", encoding="utf-8") as fh:
        return json.load(fh)


def _page_provenance(source_sha: str, params_hash: str, document_id: str,
                     geometry_source: str) -> Dict[str, Any]:
    return {
        "source_sha": source_sha,
        "params_hash": params_hash,
        "schema_version": SCHEMA_VERSION,
        "coordinate_system": COORDINATE_SYSTEM,
        "document_id": document_id,
        "pymupdf_version": pymupdf_version(),
        "geometry_source": geometry_source,
    }


# ── CASE A: expose existing artifacts (read-only, verbatim) ───────────────

def expose_text_atoms_case_a(document_id: str,
                             registry: Optional[Dict[str, Any]] = None
                             ) -> Dict[str, Any]:
    """Expose TEXT_ATOMs from a registered P1 artifact. No recomputation."""
    reg = registry or load_registry()
    entry = reg["artifact_manifest"].get(document_id, {}).get("p1_atomic")
    if entry is None:
        return {"status": "NO_REGISTERED_ARTIFACT", "document_id": document_id}
    path = os.path.join(_REPO_ROOT, entry["path"])
    live_sha = _sha256_file(path)
    if live_sha != entry["sha256"]:
        return {"status": "ARTIFACT_SHA_MISMATCH", "expected": entry["sha256"],
                "live": live_sha, "document_id": document_id}
    with open(path, "r", encoding="utf-8") as fh:
        artifact = json.load(fh)
    atoms: List[Dict[str, Any]] = []
    for obs in artifact.get("observations", []):
        if obs.get("source_type") != SOURCE_SPAN:
            continue  # registered source filter (schema: TEXT_ATOM.source_filter)
        atoms.append({
            "atom_id": obs["observation_id"],          # P1 identity, verbatim
            "atom_kind": TEXT_ATOM_KIND,
            "document_id": obs["document_id"],         # verbatim
            "page_reference": obs["page_number"],      # verbatim
            "bbox": obs["bbox"],                       # verbatim
            "content": obs["text"],                    # verbatim
            "coordinate_system": COORDINATE_SYSTEM,
            "source_sha": live_sha,
            "params_hash": _sha_obj({"source_filter": SOURCE_SPAN}),
            "schema_version": SCHEMA_VERSION,
            "pymupdf_version": artifact.get("pymupdf_version", reg["pymupdf_version"]),
            "geometry_source": "p1_artifact:" + live_sha,
        })
    return {
        "status": "EXPOSED",
        "document_id": document_id,
        "covers_page": entry.get("covers_page"),
        "provenance": _page_provenance(live_sha, _sha_obj({"source_filter": SOURCE_SPAN}),
                                       document_id, "p1_artifact:" + live_sha),
        "text_atoms": atoms,
    }


def expose_p2_singles_case_a(document_id: str,
                             registry: Optional[Dict[str, Any]] = None
                             ) -> Dict[str, Any]:
    """Expose P2 single_geometries + band facts from a registered artifact.

    Truncated artifacts are exposed WITH truncated:true and are NOT eligible
    for GAP_SEQUENCE (relations.gap_sequence_v1 refuses them).
    """
    reg = registry or load_registry()
    entry = reg["artifact_manifest"].get(document_id, {}).get("p2_geometry")
    if entry is None:
        return {"status": "NO_REGISTERED_ARTIFACT", "document_id": document_id}
    path = os.path.join(_REPO_ROOT, entry["path"])
    live_sha = _sha256_file(path)
    if live_sha != entry["sha256"]:
        return {"status": "ARTIFACT_SHA_MISMATCH", "expected": entry["sha256"],
                "live": live_sha, "document_id": document_id}
    with open(path, "r", encoding="utf-8") as fh:
        artifact = json.load(fh)
    return {
        "status": "EXPOSED",
        "document_id": artifact["document_id"],
        "page_reference": artifact["page_number"],
        "truncated": bool(entry.get("truncated", False)),
        "max_pairwise": entry.get("max_pairwise"),
        "config_snapshot": artifact.get("config_snapshot"),
        "single_geometries": artifact.get("single_geometries", []),
        "provenance": _page_provenance(live_sha,
                                       _sha_obj(artifact.get("config_snapshot", {})),
                                       artifact["document_id"],
                                       "p2_artifact:" + live_sha),
    }


def expose_region_facts_case_a(document_id: str,
                               registry: Optional[Dict[str, Any]] = None
                               ) -> Dict[str, Any]:
    """Expose RegionFacts from a registered detector artifact (P6 regions).

    RegionFact carries ONLY: region_id (pure function), source_detector,
    source_sha (registered detector code sha), params_hash (sha over the
    artifact's recorded provenance block), bbox (verbatim), coordinate_system.
    P6 region_type / confidence / decision_trace are NOT copied (contract 3).
    """
    reg = registry or load_registry()
    entry = reg["artifact_manifest"].get(document_id, {}).get("p6_regions")
    if entry is None:
        return {"status": "NO_REGISTERED_ARTIFACT", "document_id": document_id}
    path = os.path.join(_REPO_ROOT, entry["path"])
    live_sha = _sha256_file(path)
    if live_sha != entry["sha256"]:
        return {"status": "ARTIFACT_SHA_MISMATCH", "expected": entry["sha256"],
                "live": live_sha, "document_id": document_id}
    with open(path, "r", encoding="utf-8") as fh:
        artifact = json.load(fh)
    detector = "p6_region_engine"
    det_entry = reg["registered_detectors"].get(detector)
    if det_entry is None:
        return {"status": "DETECTOR_NOT_REGISTERED", "detector": detector}
    payload = artifact.get("regions", {})
    region_records = payload.get("regions", []) if isinstance(payload, dict) else payload
    page_ref = payload.get("page_number") if isinstance(payload, dict) else artifact.get("page")
    params_hash = _sha_obj(payload.get("provenance", {}))
    facts: List[Dict[str, Any]] = []
    for seq, r in enumerate(sorted(region_records, key=lambda x: x["region_id"])):
        bbox = r.get("region_geometry", {}).get("bbox")
        facts.append({
            "region_id": f"p6reg|{document_id}|p{page_ref}|{seq:04d}",
            "source_detector": detector,
            "source_sha": det_entry["source_sha"],
            "params_hash": params_hash,
            "bbox": bbox,                             # detector output, verbatim
            "coordinate_system": COORDINATE_SYSTEM,
            "geometry_source": "p6_artifact:" + live_sha,
            "document_id": document_id,
            "page_reference": page_ref,
            "schema_version": SCHEMA_VERSION,
        })
    return {
        "status": "EXPOSED",
        "document_id": document_id,
        "covers_page": page_ref,
        "provenance": _page_provenance(live_sha, params_hash, document_id,
                                       "p6_artifact:" + live_sha),
        "region_facts": facts,
    }


# ── CASE B: frozen-function build (only when no registered artifact) ──────

def build_case_b_store(pdf_path: str,
                       document_id: str,
                       pages: Optional[List[int]] = None,
                       include_non_text_blocks: bool = True) -> Dict[str, Any]:
    """Build a layer store via whitelisted frozen functions ONLY.

    - extract_pdf_observations(layers=[span])  (frozen P1, registered params)
    - compute_page_bundle(..., max_pairwise=None)  (frozen P2, NO truncation)
    - non_text_block.enumerate_non_text_blocks  (the one sanctioned new surface)
    Deterministic: same pdf + same fitz version => byte-identical store.
    """
    reg = load_registry()
    obs = extract_pdf_observations(pdf_path, document_id, layers=[SOURCE_SPAN])
    obs_dicts = [o.to_dict() if hasattr(o, "to_dict") else dict(o.__dict__) for o in obs]

    atoms_by_page: Dict[int, List[Dict[str, Any]]] = {}
    for o in obs_dicts:
        atoms_by_page.setdefault(o["page_number"], []).append(o)

    page_refs = sorted(atoms_by_page) if pages is None else sorted(pages)
    ph_p1 = _sha_obj({"source_filter": SOURCE_SPAN,
                      "layers": [SOURCE_SPAN]})
    geometry_source_p1 = reg["geometry_sources"]["case_b_p1"]
    geometry_source_p2 = reg["geometry_sources"]["case_b_p2"]

    pages_out: List[Dict[str, Any]] = []
    for pno in page_refs:
        page_obs = atoms_by_page.get(pno, [])
        bundle = compute_page_bundle(page_obs, None, None, DEFAULT_CONFIG,
                                     max_pairwise=None)  # FULL universe, never truncated
        atoms: List[Dict[str, Any]] = []
        for o in page_obs:
            atoms.append({
                "atom_id": o["observation_id"],
                "atom_kind": TEXT_ATOM_KIND,
                "document_id": o["document_id"],
                "page_reference": o["page_number"],
                "bbox": o["bbox"],
                "content": o["text"],
                "coordinate_system": COORDINATE_SYSTEM,
                "source_sha": P1_FROZEN_SHA,
                "params_hash": ph_p1,
                "schema_version": SCHEMA_VERSION,
                "pymupdf_version": pymupdf_version(),
                "geometry_source": geometry_source_p1,
            })
        pages_out.append({
            "page_reference": pno,
            "text_atoms": atoms,
            "p2_full_bundle": {
                "truncated": False,
                "max_pairwise": None,
                "config_snapshot": bundle.config_snapshot,
                "single_geometries": bundle.single_geometries,
            },
            "provenance_p1": _page_provenance(P1_FROZEN_SHA, ph_p1, document_id,
                                              geometry_source_p1),
            "provenance_p2": _page_provenance(
                reg["frozen_sources"]["p2_engine"]["sha256"],
                _sha_obj(bundle.config_snapshot),
                document_id, geometry_source_p2),
        })

    store: Dict[str, Any] = {
        "layer": "atomic_observation",
        "observation_schema_version": SCHEMA_VERSION,
        "coordinate_system": COORDINATE_SYSTEM,
        "document_id": document_id,
        "build_source": "case_b_frozen_functions",
        "pymupdf_version": pymupdf_version(),
        "pages": pages_out,
    }
    if include_non_text_blocks:
        ntbs = ntb.enumerate_non_text_blocks(pdf_path, document_id, pages=page_refs)
        ntb_by_page: Dict[int, List[Dict[str, Any]]] = {}
        for rec in ntbs:
            ntb_by_page.setdefault(rec["page_reference"], []).append(rec)
        for p in pages_out:
            p["non_text_block_atoms"] = ntb_by_page.get(p["page_reference"], [])
    return store


# ── serialization (byte-deterministic) ────────────────────────────────────

def serialize(obj: Any) -> bytes:
    """Canonical serialization: fixed key order, UTF-8, compact separators."""
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


__all__ = ["load_registry", "expose_text_atoms_case_a", "expose_p2_singles_case_a",
           "expose_region_facts_case_a", "build_case_b_store", "serialize",
           "SCHEMA_VERSION", "COORDINATE_SYSTEM"]
