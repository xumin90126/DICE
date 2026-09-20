"""Atomic Observation Layer v1 — Relations (closed set).

Contract (tmp/atomic_observation_implementation_contract.md section 4):
  - IN_REGION       relation_def = bbox_containment_v1 (registered exception:
                    center-point predicate over frozen coordinates)
  - GAP_SEQUENCE_v1 measurement identity (NOT a classifier):
        grouping  = frozen P2 same_y_band output (anchor U members, unique
                    frozensets) — zero grouping math in this layer
        gap       = frozen compute_pairwise(a, b).horizontal_distance verbatim
                    — zero gap math in this layer
        ordering  = sort_key_v1: (center_x asc, center_y asc, atom_id asc)
        thresholds= NONE (uniformity/CV/equispacing = hypothesis-side)

FORBIDDEN OUTPUTS (contract): is_uniform_run / is_tick_run / is_caption_group /
is_table_row / any is_* boolean, score, confidence, MERGE/KEEP/REJECT.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

_LAYER_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_LAYER_DIR, "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from perception.sandbox.geometry.geometry_engine import (  # noqa: E402  (frozen)
    compute_pairwise,
)
from perception.sandbox.geometry.geometry_config import (  # noqa: E402  (frozen)
    DEFAULT_CONFIG,
)

SCHEMA_VERSION = "1.0.0"
COORDINATE_SYSTEM = "pymupdf_page_1.26.x_y_down"

P2_ENGINE_SHA = "388e7939d334458e194dd4d805f6cafa0b975ce4f78d6b1137a965dd13d5554c"
P2_CONFIG_SHA = "7ef3629e5a9b819c59724b8e94a831d10a94e875c8b9534d750a7dcfa849196b"
GEOMETRY_SOURCE_FROZEN = (
    "frozen:geometry_engine.py@" + P2_ENGINE_SHA
    + "@cfg:geometry_config.py@" + P2_CONFIG_SHA
)
GEOMETRY_SOURCE_ARTIFACT = "p2_artifact:{sha}"

RELATION_DEF = "bbox_containment_v1"
MEASUREMENT_IDENTITY = "GAP_SEQUENCE_v1"


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ── IN_REGION (relation_def: bbox_containment_v1) ─────────────────────────

RELATION_DEF_DEFINITION = (
    "contained = (region.bbox[0] <= atom_center_x <= region.bbox[2]) and "
    "(region.bbox[1] <= atom_center_y <= region.bbox[3]); atom center = "
    "((bbox[0]+bbox[2])/2, (bbox[1]+bbox[3])/2) over frozen coordinates"
)


def relation_def_params_hash() -> str:
    """Identity of the registered containment definition."""
    return _sha(json.dumps(
        {"relation_def": RELATION_DEF, "definition": RELATION_DEF_DEFINITION,
         "version": "1.0.0"}, sort_keys=True, ensure_ascii=False))


def in_region(atom: Dict[str, Any], region_fact: Dict[str, Any]) -> Dict[str, Any]:
    """Pure geometric containment fact. No semantic predicate of any kind.

    atom: layer atom record (either kind) with bbox.
    region_fact: registered RegionFact record with bbox + region_id.
    """
    ab = atom["bbox"]
    rb = region_fact["bbox"]
    if ab is None or rb is None:
        contained = False
    else:
        cx = (ab[0] + ab[2]) / 2  # registered exception (contract 4.1)
        cy = (ab[1] + ab[3]) / 2
        contained = bool(rb[0] <= cx <= rb[2] and rb[1] <= cy <= rb[3])
    return {
        "atom_id": atom["atom_id"],
        "region_id": region_fact["region_id"],
        "contained": contained,
        "relation_def": RELATION_DEF,
        "params_hash": relation_def_params_hash(),
        "geometry_source": "layer:relation_def@" + RELATION_DEF
                           + " (coordinates: " + region_fact.get("geometry_source", "unknown") + ")",
        "document_id": atom["document_id"],
        "page_reference": atom["page_reference"],
    }


# ── GAP_SEQUENCE_v1 (measurement, not classifier) ─────────────────────────

def sort_key_v1(single: Dict[str, Any]) -> Tuple[float, float, str]:
    """Registered ordering: (center_x, center_y, atom_id). Deterministic."""
    return (single["center_x"], single["center_y"], single["observation_id"])


def _frozen_obs_dict(single: Dict[str, Any]) -> Dict[str, Any]:
    """Minimal P1-shape dict for the frozen compute_pairwise call.

    bbox / ids are FROZEN OUTPUT VALUES passed verbatim (no transformation).
    """
    return {
        "observation_id": single["observation_id"],
        "document_id": single["document_id"],
        "page_number": single["page_number"],
        "bbox": single["bbox"],
        "source_type": "span",
    }


def gap_sequence_params_hash(config_snapshot: Dict[str, Any]) -> str:
    """Measurement identity hash: frozen cfg snapshot + registered sort key."""
    return _sha(json.dumps(
        {"measurement_identity": MEASUREMENT_IDENTITY, "version": "1.0.0",
         "frozen_config_snapshot": config_snapshot,
         "sort_key_v1": ["center_x", "center_y", "observation_id"],
         "grouping": "frozen same_y_band anchor-neighborhood sets"},
        sort_keys=True, ensure_ascii=False))


def band_neighborhoods(singles: List[Dict[str, Any]]) -> List[Tuple[str, List[Dict[str, Any]]]]:
    """Consume frozen same_y_band output deterministically.

    frozen semantics (geometry_engine._populate_group_facts): for anchor A,
    same_y_band_members(A) = {B : |center_y(A) - center_y(B)| <= 3.0} (B != A).
    Group = ({A} U members(A)) as a frozenset anchored at A; unique sets only;
    bands ordered by their sorted member-id tuple (deterministic bookkeeping
    over frozen facts). Returns (anchor_atom_id, ordered_group) pairs.
    """
    by_id = {s["observation_id"]: s for s in singles}
    seen = set()
    groups: List[Tuple[str, List[Dict[str, Any]]]] = []
    for s in singles:
        anchor_id = s["observation_id"]
        members = frozenset([anchor_id] + list(s.get("same_y_band_members") or []))
        if members in seen:
            continue
        seen.add(members)
        group = [by_id[m] for m in sorted(members)]
        groups.append((anchor_id, group))
    groups.sort(key=lambda g: tuple(m["observation_id"] for m in g[1]))
    return groups


def gap_sequence_v1(singles: List[Dict[str, Any]],
                    document_id: str,
                    page_reference: int,
                    config_snapshot: Dict[str, Any],
                    artifact_sha: Optional[str] = None) -> Dict[str, Any]:
    """GAP_SEQUENCE_v1 — pure geometric measurement. Zero thresholds, zero classes.

    singles: full (non-truncated) P2 single_geometries for ONE page
             (must contain same_y_band_members + center_x/center_y + bbox).
    """
    ph = gap_sequence_params_hash(config_snapshot)
    if artifact_sha:
        geometry_source = GEOMETRY_SOURCE_ARTIFACT.format(sha=artifact_sha) + "+" + GEOMETRY_SOURCE_FROZEN
    else:
        geometry_source = GEOMETRY_SOURCE_FROZEN

    bands_out: List[Dict[str, Any]] = []
    for band_index, (anchor_id, group) in enumerate(band_neighborhoods(singles)):
        if len(group) < 2:
            continue  # a single atom has no gaps — nothing to measure
        ordered = sorted(group, key=sort_key_v1)
        gaps: List[Dict[str, Any]] = []
        for i in range(len(ordered) - 1):
            rel = compute_pairwise(_frozen_obs_dict(ordered[i]),
                                   _frozen_obs_dict(ordered[i + 1]),
                                   DEFAULT_CONFIG)
            gaps.append({
                "seq": i,
                "a_id": ordered[i]["observation_id"],
                "b_id": ordered[i + 1]["observation_id"],
                "gap": rel.horizontal_distance,  # frozen value, verbatim
            })
        bands_out.append({
            "band_id": f"band_{band_index:04d}",
            "anchor_atom_id": anchor_id,
            "member_atom_ids": [m["observation_id"] for m in ordered],
            "gaps": gaps,
        })
    return {
        "measurement_identity": MEASUREMENT_IDENTITY,
        "geometry_source": geometry_source,
        "document_id": document_id,
        "page_reference": page_reference,
        "params_hash": ph,
        "bands": bands_out,
    }


__all__ = ["in_region", "gap_sequence_v1", "band_neighborhoods",
           "relation_def_params_hash", "gap_sequence_params_hash",
           "RELATION_DEF", "MEASUREMENT_IDENTITY", "COORDINATE_SYSTEM",
           "SCHEMA_VERSION"]
