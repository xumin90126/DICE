"""
L5.5 Primitive A — Aggregation (ISOLATED EXPERIMENTAL, tmp/ only)

L5.4 Contract implementation:
  Aggregation = organize existing Evidence into explicitly structured groups
  according to declared structural relations, without assigning semantic roles.

Authority = 0. No semantic interpretation. No ranking. No decision.
"Compress evidence, not meaning." / "Human should validate, not reconstruct."

Input:  frozen EIC-1 structural context (from mb_phase3_2_isolated_replay_results.json)
Output: groups {group_id, structural_signature, member_refs, provenance}
        + UNKNOWN preserved + CONFLICT preserved + non-positive groups preserved

FORBIDDEN fields (enforced via assertion):
  is_table, is_cell, is_row, is_column, is_header, is_row_number,
  code_line, semantic_role, table_id, cell_id, score, confidence,
  recommendation, merge_candidate, keep_candidate, decision, priority, winner
"""
from __future__ import annotations
import json, hashlib, os
from typing import Any, Dict, List, Tuple

# ── Contract constants ──────────────────────────────────────────────────────
CONTRACT_VERSION = "L5.4_v1"
FORBIDDEN_FIELDS = frozenset({
    'is_table','is_cell','is_row','is_column','is_header','is_row_number',
    'code_line','semantic_role','table_id','cell_id','score','confidence',
    'recommendation','merge_candidate','keep_candidate','decision','priority','winner',
    'selection','ranking','fallback','retry','override','correction','route',
    'execution_plan','semantic_pattern','pattern_id','pattern_type',
})

# Structural signature components (ALL from frozen P2 + EIC-1, zero semantic)
SIGNATURE_COMPONENTS = [
    'sce_status',           # admitted / region_not_formed / partition_unresolvable
    'region_forms',         # bool (frozen P2 co-structure threshold)
    'different_local_partition',  # bool (from SCE, structural)
    'same_structural_region',     # bool (from SCE, structural)
    'pairwise_same_y_band',       # bool (from frozen P2)
    'has_candidate',              # bool (EIC-1 interpretation_status=candidate exists)
]


def _assert_clean(obj: Any, name: str, path: str = "") -> None:
    """Recursively assert no forbidden field exists in output."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in FORBIDDEN_FIELDS:
                raise AssertionError(f"FORBIDDEN FIELD LEAKAGE: '{k}' in {name} at {path}")
            _assert_clean(v, name, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _assert_clean(v, name, f"{path}[{i}]")


def compute_structural_signature(eic1_detail: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute structural signature from frozen EIC-1 features.
    NO semantic inference. Deterministic. Structural-only.

    Signature = frozen structural features that determine grouping.
    Same signature => same group. This is structural similarity, NOT semantic equivalence.
    """
    status = eic1_detail.get('sce_status', 'unknown')
    rsc = eic1_detail.get('rsc', {})
    sce = eic1_detail.get('sce')
    region_forms = rsc.get('region_forms', False)

    if status == 'admitted' and sce is not None:
        # SCE exists — read structural fields only (all frozen, all governed)
        sig = {
            'sce_status': 'admitted',
            'region_forms': True,
            'different_local_partition': sce.get('different_local_partition', False),
            'same_structural_region': sce.get('same_structural_region', False),
            'pairwise_same_y_band': sce.get('pairwise_same_y_band', False),
            'has_candidate': True,  # interpretation_status='candidate' exists in SCE
        }
    elif status == 'region_not_formed':
        sig = {
            'sce_status': 'region_not_formed',
            'region_forms': False,
            'different_local_partition': False,
            'same_structural_region': False,
            'pairwise_same_y_band': False,
            'has_candidate': False,
        }
    elif status == 'partition_unresolvable':
        sig = {
            'sce_status': 'partition_unresolvable',
            'region_forms': True,  # region formed but partition not resolvable
            'different_local_partition': False,
            'same_structural_region': False,
            'pairwise_same_y_band': False,
            'has_candidate': False,
        }
    else:
        sig = {
            'sce_status': status,
            'region_forms': region_forms,
            'different_local_partition': False,
            'same_structural_region': False,
            'pairwise_same_y_band': False,
            'has_candidate': False,
        }

    _assert_clean(sig, 'structural_signature')
    return sig


def _sig_key(sig: Dict[str, Any]) -> str:
    """Deterministic key from signature (for grouping)."""
    return json.dumps(sig, sort_keys=True)


def _group_id(sig: Dict[str, Any]) -> str:
    """Deterministic group_id from signature."""
    raw = json.dumps(sig, sort_keys=True)
    return f"grp|{hashlib.sha1(raw.encode()).hexdigest()[:12]}"


def aggregate(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate cases into groups by structural signature.

    Input: list of case dicts (each with case_id, eic1_detail, gt, off_decision, on_decision)
    Output: {
        groups: [{group_id, structural_signature, member_refs, member_count, provenance}],
        grouping_criteria: "structural signature from frozen P2 + EIC-1",
        unknown_count, conflict_count, non_positive_group_count,
        total_cases, total_groups,
        contract_version, authority: 0
    }

    Guarantees:
    - Deterministic (same input => same output, byte-identical)
    - No semantic labels
    - UNKNOWN preserved (partition_unresolvable + region_not_formed groups retained)
    - CONFLICT preserved (if any EVIDENCE_CONFLICT in input, retained)
    - Non-positive groups preserved (all groups retained, no deletion)
    - Per-member provenance preserved
    - Input not modified
    """
    groups_map: Dict[str, Dict[str, Any]] = {}
    unknown_count = 0
    conflict_count = 0

    for case in cases:
        case_id = case.get('case_id', '?')
        eic1_detail = case.get('eic1_detail', {})
        sce = eic1_detail.get('sce')

        sig = compute_structural_signature(eic1_detail)
        key = _sig_key(sig)
        gid = _group_id(sig)

        if key not in groups_map:
            groups_map[key] = {
                'group_id': gid,
                'structural_signature': sig,
                'member_refs': [],
                'provenance': {
                    'grouping_criteria': 'structural_signature_from_frozen_P2_and_EIC1',
                    'contract_version': CONTRACT_VERSION,
                    'authority': 0,
                    'semantic_interpretation': 'FORBIDDEN',
                },
            }

        # Member reference (provenance preserved)
        member_ref = {
            'case_id': case_id,
            'sce_status': eic1_detail.get('sce_status', 'unknown'),
            'has_sce': sce is not None,
            'case_provenance': {
                'eic1_chain': sce.get('provenance', {}) if sce else {},
                'source': sce.get('source', 'none') if sce else 'none',
            },
        }
        _assert_clean(member_ref, f'member_ref[{case_id}]')
        groups_map[key]['member_refs'].append(member_ref)

        # Count UNKNOWN (partition_unresolvable or region_not_formed = no candidate)
        if sig['sce_status'] in ('partition_unresolvable', 'region_not_formed'):
            unknown_count += 1

        # Count CONFLICT (if on_decision has evidence_conflict)
        on_decision = case.get('on_decision', '')
        if 'evidence_conflict' in str(case.get('on_decision', '')).lower():
            conflict_count += 1

    groups = list(groups_map.values())
    for g in groups:
        g['member_count'] = len(g['member_refs'])
        _assert_clean(g, f'group[{g["group_id"]}]')

    # Non-positive groups = groups without candidate (sce_status != admitted)
    non_positive = sum(1 for g in groups if not g['structural_signature']['has_candidate'])

    result = {
        'groups': groups,
        'grouping_criteria': 'structural_signature_from_frozen_P2_and_EIC1',
        'signature_components': SIGNATURE_COMPONENTS,
        'total_cases': len(cases),
        'total_groups': len(groups),
        'unknown_count': unknown_count,
        'conflict_count': conflict_count,
        'non_positive_group_count': non_positive,
        'contract_version': CONTRACT_VERSION,
        'authority': 0,
        'semantic_interpretation': 'FORBIDDEN',
        'note': 'Structural Similarity != Semantic Equivalence; Same Structure != Same Meaning',
    }

    _assert_clean(result, 'aggregation_result')
    return result


def load_cases_from_replay(replay_path: str) -> List[Dict[str, Any]]:
    """Load 21 cases from frozen replay results (read-only)."""
    data = json.load(open(replay_path))
    comp = data.get('comparison', [])
    cases = []
    for c in comp:
        cases.append({
            'case_id': c.get('case_id', '?'),
            'gt': c.get('gt', '?'),
            'off_decision': c.get('off_decision', '?'),
            'on_decision': c.get('on_decision', '?'),
            'eic1_detail': c.get('eic1_detail', {}),
        })
    return cases


if __name__ == '__main__':
    cases = load_cases_from_replay('tmp/mb_phase3_2_isolated_replay_results.json')
    result = aggregate(cases)
    print(f"Aggregation: {result['total_cases']} cases -> {result['total_groups']} groups")
    for g in result['groups']:
        sig = g['structural_signature']
        print(f"  {g['group_id']}: status={sig['sce_status']} candidate={sig['has_candidate']} members={g['member_count']}")
    print(f"  unknown_count={result['unknown_count']} conflict_count={result['conflict_count']} non_positive={result['non_positive_group_count']}")
    print(f"  authority={result['authority']} semantic_interpretation={result['semantic_interpretation']}")
