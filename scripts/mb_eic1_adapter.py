"""
M-B EIC-1 Adapter — Local Structural Partition + Regional Structural Context + EIC-1.

DESIGN CONTRACT (Phase 2.2 / 3.1):
- LSP = structural object ONLY (membership/scope/relation/continuity/provenance).
- RSC = structural evidence ONLY (ceiling: "local structural co-organization", NOT "table region").
- EIC-1 = sole semantic gate; Cell Context Evidence = interpretation_status='candidate'.
- NO direct LSP->different_cell; mapping goes LSP->RSC->EIC-1->existing observation form.
- Frozen parameters (Phase 3.1, NOT tunable): P_MIN_MEMBERS=2, P_MIN_BANDS=3,
  P_LOCALIZATION=150pt, P_MIN_COSTRUCTURE_BAND_LOCAL=3, same_y_band (frozen P2).

This module is READ-ONLY over the frozen atomic observation store. It produces NO
decision, NO score, NO confidence. Forbidden-field assertions enforced.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'perception', 'atomic_observation'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import adapter as obs_adapter
from perception.sandbox.geometry.geometry_engine import compute_pairwise
from perception.sandbox.geometry.geometry_config import DEFAULT_CONFIG

# === FROZEN PARAMETERS (Phase 3.1) ===
P_MIN_MEMBERS = 2
P_MIN_BANDS = 3
P_LOCALIZATION = 150.0
P_MIN_COSTRUCTURE_BAND_LOCAL = 3
P4_BAND = 8.0  # frozen span threshold

FORBIDDEN = {'is_table','is_cell','is_row','is_column','is_header','is_row_number',
    'code_line','semantic_role','table_id','cell_id','score','confidence',
    'recommendation','merge_candidate','keep_candidate','decision','priority','winner'}

PARAMS_HASH = "phase3.1_frozen:Pmem2_Pband3_Ploc150_Pcostr3"

def _yb(y):
    return int(round(y / P4_BAND))

def _assert_clean(d, name):
    leak = set(d.keys()) & FORBIDDEN
    assert not leak, f"SEMANTIC LEAK in {name}: {leak}"

_store_cache = {}
def get_store(pdf_path, doc_id, page):
    key = (doc_id, page)
    if key not in _store_cache:
        _store_cache[key] = obs_adapter.build_case_b_store(pdf_path, doc_id, pages=[page])
    return _store_cache[key]

def find_atom_by_bbox(store, page, target_bbox):
    """Match case bbox to a single_geometry by center proximity."""
    pg = [p for p in store['pages'] if p['page_reference'] == page][0]
    S = pg['p2_full_bundle']['single_geometries']
    tcx = (target_bbox[0] + target_bbox[2]) / 2
    tcy = (target_bbox[1] + target_bbox[3]) / 2
    best, best_d = None, 1e9
    for s in S:
        cx, cy = s['center_x'], s['center_y']
        d = abs(cx - tcx) + abs(cy - tcy)
        if d < best_d:
            best_d = d; best = s
    return best, best_d, pg

def build_local_structural_partitions(pg):
    """LSP derivation. Structural only. Pure function over frozen store."""
    S = pg['p2_full_bundle']['single_geometries']
    seen = set(); lsps = []
    for s in S:
        gid = s.get('left_alignment_group') or []
        if not gid:
            continue
        k = tuple(sorted(gid))
        if k in seen:
            continue
        seen.add(k)
        mems = [x for x in S if x['observation_id'] in gid]
        n = len(mems)
        if n < P_MIN_MEMBERS:
            continue
        ys = [m['center_y'] for m in mems]
        xs = [m['bbox'][0] for m in mems]
        x1s = [m['bbox'][2] for m in mems]
        y1s = [m['bbox'][3] for m in mems]
        bands = set(_yb(y) for y in ys)
        if len(bands) < P_MIN_BANDS:
            continue
        y_ext = max(ys) - min(ys)
        lsp = {
            'partition_id': f"lsp|p{pg['page_reference']}|x{round(min(xs),1)}",
            'member_atom_ids': sorted([m['observation_id'] for m in mems]),
            'bbox_union': [round(min(xs),2), round(min(ys),2), round(max(x1s),2), round(max(y1s),2)],
            'axis': 'x0_left_alignment_group',
            'x0': round(min(xs), 2),
            'n_members': n,
            'n_bands': len(bands),
            'bands': sorted(bands),
            'y_min': round(min(ys),2), 'y_max': round(max(ys),2),
            'y_ext': round(y_ext,2),
            'is_local': y_ext <= P_LOCALIZATION,
            'source_surface': 'atomic_observation_layer.v1/p2_singles',
            'provenance': {'relation': 'left_alignment_group', 'source': 'frozen_p2',
                           'params_hash': PARAMS_HASH}
        }
        _assert_clean(lsp, 'LSP')
        lsps.append(lsp)
    return lsps

def build_regional_structural_context(lsps, pair_y):
    """RSC = regional structural context. Structural evidence only."""
    pair_band = _yb(pair_y)
    local_lsps = [l for l in lsps if l['is_local']]
    co_occurring = [l for l in local_lsps if pair_band in l['bands']]
    region_forms = len(co_occurring) >= P_MIN_COSTRUCTURE_BAND_LOCAL
    rsc = {
        'region_id': f"rsc|p|band{pair_band}",
        'pair_band': pair_band,
        'pair_y': round(pair_y, 2),
        'local_partitions_co_occurring': len(co_occurring),
        'region_forms': region_forms,
        'co_occurring_partition_ids': [l['partition_id'] for l in co_occurring],
        'ceiling_statement': 'local_structural_co_organization',
        'provenance': {'source': 'frozen_p2', 'params_hash': PARAMS_HASH}
    }
    _assert_clean(rsc, 'RSC')
    return rsc

def emit_structural_context_evidence(atom_a, atom_b, lsps, rsc):
    """EIC-1: produce Cell Context Evidence (interpretation_status=candidate).
    Preconditions: region_forms + same_y_band + both atoms partition-resolvable."""
    if not rsc['region_forms']:
        return None, 'region_not_formed'
    # same_y_band via frozen pairwise
    pr = compute_pairwise(atom_a, atom_b, DEFAULT_CONFIG)
    if not pr.same_y_band:
        return None, 'not_same_y_band'
    lsp_a = next((l for l in lsps if atom_a['observation_id'] in l['member_atom_ids']), None)
    lsp_b = next((l for l in lsps if atom_b['observation_id'] in l['member_atom_ids']), None)
    if lsp_a is None or lsp_b is None:
        return None, 'partition_unresolvable'
    same_partition = (lsp_a['partition_id'] == lsp_b['partition_id'])
    sce = {
        'case_ref': f"{atom_a['observation_id']}|{atom_b['observation_id']}",
        'atom_a_partition': lsp_a['partition_id'],
        'atom_b_partition': lsp_b['partition_id'],
        'same_structural_region': True,
        'different_local_partition': not same_partition,
        'same_local_partition': same_partition,
        'interpretation_status': 'candidate',
        'region_ref': rsc['region_id'],
        'pairwise_same_y_band': True,
        'provenance': {
            'lsp_a': lsp_a['partition_id'], 'lsp_b': lsp_b['partition_id'],
            'rsc': rsc['region_id'], 'source': 'eic1_v0',
            'params_hash': PARAMS_HASH,
            'chain': ['L2_geometry', 'LSP', 'RSC', 'EIC1']
        },
        'source': 'geometry_structural_context_adapter.v0'
    }
    _assert_clean(sce, 'SCE')
    return sce, 'admitted'

def eic1_map_to_observation(sce):
    """Map SCE -> existing is11_obs form (reuses existing state semantics)."""
    if sce is None:
        return None
    ti = {'source': 'eic1', 'interpretation_status': 'candidate',
          'region_ref': sce['region_ref'], 'provenance': sce['provenance']}
    if sce['same_structural_region'] and sce['different_local_partition']:
        return {'is_in_table': True, 'same_cell': False, 'different_cell': True, 'table_info': ti}
    if sce['same_structural_region'] and sce['same_local_partition']:
        return {'is_in_table': True, 'same_cell': True, 'different_cell': False, 'table_info': ti}
    return None

# === COEXISTENCE CONTRACT (no arbitration) ===
def compose_observations(tld_obs, eic1_obs):
    """Three-case coexistence. No winner, no preference, no fallback policy."""
    if eic1_obs is None:
        return tld_obs, 'tld_only_or_neither'
    tld_ctx = (tld_obs.get('is_in_table') or tld_obs.get('different_cell') or tld_obs.get('same_cell'))
    if not tld_ctx:
        return eic1_obs, 'eic1_single_source'
    # both present
    tld_dc, eic_dc = tld_obs.get('different_cell', False), eic1_obs.get('different_cell', False)
    tld_sc, eic_sc = tld_obs.get('same_cell', False), eic1_obs.get('same_cell', False)
    if tld_dc == eic_dc and tld_sc == eic_sc:
        merged = dict(tld_obs)
        ti = dict(tld_obs.get('table_info', {}))
        ti['sources'] = ['tld', 'eic1_agree']
        merged['table_info'] = ti
        return merged, 'agree'
    # CONFLICT -> EVIDENCE_CONFLICT (observable, no winner)
    return ({'is_in_table': False, 'same_cell': False, 'different_cell': False,
             'table_info': {'evidence_conflict': {'tld': {'different_cell': tld_dc, 'same_cell': tld_sc},
                                                  'eic1': {'different_cell': eic_dc, 'same_cell': eic_sc}},
                            'reason': 'evidence_conflict_no_admissible_composite'}}), 'evidence_conflict'
