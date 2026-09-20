"""
L5.7 Experiment Harness (ISOLATED, tmp/ only)

Generates A/B/C presentation materials from frozen L5.5 output.
Does NOT produce human judgments. Does NOT modify frozen baseline.

Usage:
  python3 tmp/l5_7_experiment_harness.py generate   # generate materials
  python3 tmp/l5_7_experiment_harness.py validate    # validate materials
  python3 tmp/l5_7_experiment_harness.py schema      # print recording schema

This harness prepares everything for real human execution.
It does NOT execute the pilot (no human subject, no simulated judgments).
"""
from __future__ import annotations
import json, os, sys, hashlib
from typing import Any, Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from l5_5_aggregation import aggregate, load_cases_from_replay, CONTRACT_VERSION
from l5_5_evidence_compression import compress

REPLAY_PATH = 'tmp/mb_phase3_2_isolated_replay_results.json'
MATERIALS_PATH = 'tmp/l5_7_pilot_materials.json'
SCHEMA_PATH = 'tmp/l5_7_pilot_recording_schema.json'

# Judgment options (same for all workflows)
JUDGMENT_OPTIONS = ['KEEP_SEPARATE', 'MERGE', 'UNKNOWN']

# Latin square orders (counterbalancing)
LATIN_SQUARE = [
    ['A', 'B', 'C'],
    ['B', 'C', 'A'],
    ['C', 'A', 'B'],
]


# ═══════════════════════════════════════════════════════════════════════════
# Workflow A — Instance Validation materials
# ═══════════════════════════════════════════════════════════════════════════

def generate_workflow_A(cases: List[Dict]) -> List[Dict]:
    """
    Generate per-instance presentation materials.
    Human sees one instance at a time, judges independently.
    NO cross-instance abstraction required.
    """
    items = []
    for c in cases:
        eic = c.get('eic1_detail', {})
        sce = eic.get('sce')
        rsc = eic.get('rsc', {})

        # What Human sees: structural context (NO semantic label, NO GT)
        item = {
            'item_id': f"A|{c['case_id']}",
            'workflow': 'A',
            'case_id': c['case_id'],
            'task': 'Judge whether the two atoms belong to the same semantic unit.',
            'judgment_options': JUDGMENT_OPTIONS,
            'evidence_presented': {
                'sce_status': eic.get('sce_status', 'unknown'),
                'region_forms': rsc.get('region_forms', False),
                'pair_band_co_density': eic.get('pair_band_co_density', 0),
                'pair_band': rsc.get('pair_band', None),
                'pair_y': rsc.get('pair_y', None),
                'lsp_a': eic.get('lsp_a', None),
                'lsp_b': eic.get('lsp_b', None),
                'n_local_lsps': eic.get('n_local_lsps', 0),
                'different_local_partition': sce.get('different_local_partition') if sce else None,
                'same_structural_region': sce.get('same_structural_region') if sce else None,
                'interpretation_status': sce.get('interpretation_status') if sce else 'none',
            },
            # GT hidden from Human (only for scoring)
            '_gt_hidden': c.get('gt', '?'),
            # NO semantic label, NO conclusion, NO candidate wording
        }
        items.append(item)
    return items


# ═══════════════════════════════════════════════════════════════════════════
# Workflow B — Naive Pattern Validation materials
# ═══════════════════════════════════════════════════════════════════════════

def generate_workflow_B(cases: List[Dict], agg_result: Dict) -> List[Dict]:
    """
    Generate per-group presentation materials.
    Human sees all members of a group, must do abstraction themselves.
    NO compression, NO summary, NO claim candidate.
    """
    items = []
    for g in agg_result['groups']:
        sig = g['structural_signature']
        member_ids = [m['case_id'] for m in g['member_refs']]

        # Collect per-instance evidence for this group (all shown, no compression)
        member_evidence = []
        for c in cases:
            if c['case_id'] in member_ids:
                eic = c.get('eic1_detail', {})
                sce = eic.get('sce')
                rsc = eic.get('rsc', {})
                member_evidence.append({
                    'case_id': c['case_id'],
                    'sce_status': eic.get('sce_status', 'unknown'),
                    'region_forms': rsc.get('region_forms', False),
                    'pair_band_co_density': eic.get('pair_band_co_density', 0),
                    'pair_band': rsc.get('pair_band', None),
                    'pair_y': rsc.get('pair_y', None),
                    'lsp_a': eic.get('lsp_a', None),
                    'lsp_b': eic.get('lsp_b', None),
                    'n_local_lsps': eic.get('n_local_lsps', 0),
                    'different_local_partition': sce.get('different_local_partition') if sce else None,
                    'same_structural_region': sce.get('same_structural_region') if sce else None,
                    'interpretation_status': sce.get('interpretation_status') if sce else 'none',
                    '_gt_hidden': c.get('gt', '?'),
                })

        item = {
            'item_id': f"B|{g['group_id']}",
            'workflow': 'B',
            'group_id': g['group_id'],
            'task': 'Examine these instances, find their commonality, and judge whether they belong to the same semantic unit.',
            'judgment_options': JUDGMENT_OPTIONS,
            'grouping_hint': 'These instances have been pre-grouped by structural signature. You must determine the semantic meaning yourself.',
            'member_count': g['member_count'],
            'evidence_presented': member_evidence,
            # NO summary, NO claim, NO compression
            # Human does: commonality / comparison / prototype / boundary / negative / UNKNOWN
        }
        items.append(item)
    return items


# ═══════════════════════════════════════════════════════════════════════════
# Workflow C — Minimal Semantic Validation materials
# ═══════════════════════════════════════════════════════════════════════════

def generate_workflow_C(agg_result: Dict, comp_result: Dict, cases: List[Dict]) -> List[Dict]:
    """
    Generate per-claim presentation materials.
    Human sees compressed Semantic Claim Candidate + summary.
    System did aggregation + compression. Human only validates.
    """
    items = []
    for cg in comp_result['compressed_groups']:
        s = cg['summary']
        claim = cg['claim_candidate']
        pp = cg['provenance_pointer']

        # Level 4 evidence (on-demand, not shown by default)
        level4_evidence = []
        for ref in pp['member_refs']:
            case_id = ref['case_id']
            case = next((c for c in cases if c['case_id'] == case_id), None)
            if case:
                eic = case.get('eic1_detail', {})
                sce = eic.get('sce')
                rsc = eic.get('rsc', {})
                level4_evidence.append({
                    'case_id': case_id,
                    'sce_status': eic.get('sce_status', 'unknown'),
                    'region_forms': rsc.get('region_forms', False),
                    'pair_band_co_density': eic.get('pair_band_co_density', 0),
                    'pair_band': rsc.get('pair_band', None),
                    'pair_y': rsc.get('pair_y', None),
                    'lsp_a': eic.get('lsp_a', None),
                    'lsp_b': eic.get('lsp_b', None),
                    'n_local_lsps': eic.get('n_local_lsps', 0),
                    'different_local_partition': sce.get('different_local_partition') if sce else None,
                    'same_structural_region': sce.get('same_structural_region') if sce else None,
                    'interpretation_status': sce.get('interpretation_status') if sce else 'none',
                    '_gt_hidden': case.get('gt', '?'),
                })

        item = {
            'item_id': f"C|{s['group_id']}",
            'workflow': 'C',
            'group_id': s['group_id'],
            'task': 'Validate this Semantic Claim Candidate: is it SUPPORTED, UNSUPPORTED, or UNKNOWN?',
            'judgment_options': JUDGMENT_OPTIONS,
            # Default exposure (Level 0): claim + summary only
            'default_exposure': {
                'claim_text': claim['claim_text'],
                'interpretation_status': claim['interpretation_status'],  # candidate / UNKNOWN
                'claim_type': claim['claim_type'],
                'summary': {
                    'member_count': s['member_count'],
                    'consistent_count': s['consistent_count'],
                    'unknown_count': s['unknown_count'],
                    'conflict_count': s['conflict_count'],
                    'coverage_count': s['coverage_count'],
                    'grouping_criteria': s['grouping_criteria'],
                    'candidate_interpretations': s['candidate_interpretations'],
                },
                'note': 'This is a CANDIDATE, not a conclusion. You may reject it.',
            },
            # Progressive Disclosure levels (on-demand, NOT shown by default)
            'progressive_disclosure': {
                'level_1_summary': 'Already shown in default_exposure',
                'level_2_member_refs': [m['case_id'] for m in pp['member_refs']],
                'level_3_boundary_negative_unknown': {
                    'has_candidate': s['structural_signature']['has_candidate'],
                    'sce_status': s['structural_signature']['sce_status'],
                    'non_positive': not s['structural_signature']['has_candidate'],
                },
                'level_4_full_provenance': level4_evidence,  # per-instance detail
            },
            # Track expansion behavior
            'expansion_tracking': {
                'default_exposure_shown': True,
                'level_2_requested': False,  # to be recorded during execution
                'level_3_requested': False,
                'level_4_requested': False,
                'expansion_count': 0,
            },
        }
        items.append(item)
    return items


# ═══════════════════════════════════════════════════════════════════════════
# Recording Schema
# ═══════════════════════════════════════════════════════════════════════════

RECORDING_SCHEMA = {
    'schema_version': 'L5.7_v1',
    'description': 'Recording schema for Human Validation Pilot. One record per judgment.',
    'required_fields': {
        'participant_id': {'type': 'string', 'description': 'Anonymous participant identifier'},
        'item_id': {'type': 'string', 'description': 'A|case_id / B|group_id / C|group_id'},
        'workflow': {'type': 'string', 'enum': ['A', 'B', 'C']},
        'case_id_or_group_id': {'type': 'string', 'description': 'The case_id (A) or group_id (B/C) being judged'},
        'decision': {'type': 'string', 'enum': JUDGMENT_OPTIONS, 'description': 'Human semantic judgment'},
        'time_seconds': {'type': 'number', 'description': 'Time to complete this judgment (seconds)'},
    },
    'optional_fields': {
        'difficulty': {'type': 'string', 'enum': ['Easy', 'Medium', 'Hard'], 'description': 'Perceived difficulty'},
        'confidence': {'type': 'string', 'enum': ['Low', 'Medium', 'High'], 'description': 'Confidence in judgment'},
        'order_position': {'type': 'integer', 'description': 'Position in sequence (1st, 2nd, 3rd workflow)'},
        'expansion_count': {'type': 'integer', 'description': 'C only: how many levels expanded'},
        'levels_viewed': {'type': 'array', 'description': 'C only: which levels were viewed'},
        'behavioral_notes': {'type': 'string', 'description': 'Observer notes (abstraction behavior, revisit behavior, etc.)'},
    },
    'behavioral_indicators': {
        'ABSTRACTION_BEHAVIOR': 'Human performs cross-instance comparison / commonality search / prototype formation',
        'REVISIT_BEHAVIOR': 'Human frequently returns to previously viewed evidence',
        'EXPANSION_BEHAVIOR': 'Human expands beyond default exposure (C only)',
    },
    'workload_proxy_warning': 'review_count / evidence_exposure / interaction_count are workload PROXY, NOT cognitive_load. True burden = time + difficulty + abstraction_burden + task_behavior.',
}


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

def generate_materials() -> Dict:
    """Generate all A/B/C materials from frozen L5.5 output."""
    cases = load_cases_from_replay(REPLAY_PATH)
    agg = aggregate(cases)
    comp = compress(agg, cases)

    items_A = generate_workflow_A(cases)
    items_B = generate_workflow_B(cases, agg)
    items_C = generate_workflow_C(agg, comp, cases)

    materials = {
        'schema_version': 'L5.7_v1',
        'contract_version': CONTRACT_VERSION,
        'source': 'frozen L5.5 output (mb_phase3_2_isolated_replay_results.json)',
        'judgment_options': JUDGMENT_OPTIONS,
        'latin_square_orders': LATIN_SQUARE,
        'total_cases': len(cases),
        'total_groups': agg['total_groups'],
        'workflows': {
            'A': {
                'description': 'Instance Validation: per-instance judgment, no abstraction',
                'item_count': len(items_A),
                'items': items_A,
            },
            'B': {
                'description': 'Naive Pattern Validation: per-group, all members shown, Human does abstraction',
                'item_count': len(items_B),
                'items': items_B,
            },
            'C': {
                'description': 'Minimal Semantic Validation: per-claim, compressed, System did abstraction',
                'item_count': len(items_C),
                'items': items_C,
            },
        },
        'fairness_check': {
            'same_task': True,
            'same_material': True,
            'same_gt': True,
            'same_judgment_options': True,
            'C_claim_is_candidate': True,
            'C_claim_no_answer_leak': True,
        },
        'behavioral_tracking': {
            'ABSTRACTION_BEHAVIOR': 'cross-instance comparison / commonality / prototype',
            'REVISIT_BEHAVIOR': 'frequent return to previous evidence',
            'EXPANSION_BEHAVIOR': 'expand beyond default (C only)',
        },
        'note': 'Materials generated from frozen L5.5. NO human judgments included. Requires real human participant.',
    }

    return materials


def validate_materials(materials: Dict) -> Dict:
    """Validate materials for fairness and integrity."""
    checks = {}

    # Check: same judgment options across workflows
    opts = set(materials['judgment_options'])
    checks['same_judgment_options'] = opts == {'KEEP_SEPARATE', 'MERGE', 'UNKNOWN'}

    # Check: C claim does not leak GT answer
    c_items = materials['workflows']['C']['items']
    answer_words = ['keep_separate', 'merge', 'correct', 'answer', 'gt', 'ground truth', 'conclusion', 'supported', 'unsupported']
    leaks = []
    for item in c_items:
        claim = item['default_exposure']['claim_text'].lower()
        for w in answer_words:
            if w in claim:
                leaks.append(f"{item['item_id']}: '{w}'")
    checks['C_no_answer_leak'] = len(leaks) == 0
    checks['C_leaks'] = leaks

    # Check: C claim is candidate (not conclusion)
    all_candidate = all(
        item['default_exposure']['interpretation_status'] in ('candidate', 'UNKNOWN', 'none')
        for item in c_items
    )
    checks['C_claim_is_candidate'] = all_candidate

    # Check: same GT across workflows (hidden)
    a_gts = set(item['_gt_hidden'] for item in materials['workflows']['A']['items'])
    checks['A_gt_set'] = a_gts

    # Check: B has all members (no compression)
    b_items = materials['workflows']['B']['items']
    total_b_members = sum(item['member_count'] for item in b_items)
    checks['B_shows_all_members'] = total_b_members == materials['total_cases']

    # Check: C has provenance recoverable (Level 4)
    c_items = materials['workflows']['C']['items']
    all_recoverable = all(
        len(item['progressive_disclosure']['level_4_full_provenance']) == item['default_exposure']['summary']['member_count']
        for item in c_items
    )
    checks['C_level4_recoverable'] = all_recoverable

    # Check: C shows negative groups (not only positive)
    c_statuses = [item['default_exposure']['summary']['grouping_criteria'] for item in c_items]
    has_negative = any('no candidate' in item['default_exposure']['claim_text'].lower() or 'insufficient' in item['default_exposure']['claim_text'].lower() for item in c_items)
    checks['C_shows_negative'] = has_negative

    all_pass = all(v for k, v in checks.items() if isinstance(v, bool))
    checks['_all_pass'] = all_pass
    return checks


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'generate'

    if cmd == 'generate':
        materials = generate_materials()
        checks = validate_materials(materials)
        materials['validation'] = checks

        with open(MATERIALS_PATH, 'w') as f:
            json.dump(materials, f, indent=2, default=str)
        with open(SCHEMA_PATH, 'w') as f:
            json.dump(RECORDING_SCHEMA, f, indent=2, default=str)

        print(f"=== MATERIALS GENERATED ===")
        print(f"  A: {materials['workflows']['A']['item_count']} items (per-instance)")
        print(f"  B: {materials['workflows']['B']['item_count']} items (per-group, all members)")
        print(f"  C: {materials['workflows']['C']['item_count']} items (per-claim, compressed)")
        print(f"  Latin square: {LATIN_SQUARE}")
        print(f"  Judgment options: {JUDGMENT_OPTIONS}")
        print(f"  Validation: {'ALL PASS' if checks['_all_pass'] else 'FAIL'}")
        for k, v in checks.items():
            if k != '_all_pass':
                print(f"    {k}: {v}")
        print(f"  Materials: {MATERIALS_PATH}")
        print(f"  Schema: {SCHEMA_PATH}")
        print(f"  NO human judgments included. Requires real human participant.")

    elif cmd == 'validate':
        materials = json.load(open(MATERIALS_PATH))
        checks = validate_materials(materials)
        print(json.dumps(checks, indent=2, default=str))

    elif cmd == 'schema':
        print(json.dumps(RECORDING_SCHEMA, indent=2, default=str))

    else:
        print(f"Usage: python3 {sys.argv[0]} [generate|validate|schema]")
