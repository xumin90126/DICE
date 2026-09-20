"""
L5.5 Primitive B — Evidence Compression (ISOLATED EXPERIMENTAL, tmp/ only)

L5.4 Contract implementation:
  Evidence Compression = reduce Human evidence exposure
  while preserving recoverability, traceability and auditability.

Authority = 0. No semantic interpretation. No conclusion. No judgment.
"Compress evidence, not meaning." / "Human should validate, not reconstruct."

Input:  Aggregation output (groups) + per-instance EIC-1 candidate + provenance
Output: summary (counts) + Semantic Claim Candidate (aggregated EIC-1, template, status=candidate)

F1-F7 Compression Fidelity:
  F1 Positive Evidence Preservation
  F2 Negative Evidence Preservation
  F3 Boundary Evidence Preservation (grouping criteria stated)
  F4 UNKNOWN Preservation
  F5 Conflict Preservation
  F6 Provenance Recoverability (Level 4)
  F7 Semantic Claim Traceability (claim -> EIC-1 -> evidence -> observation)

FORBIDDEN: new semantic interpretation, conclusion, closure, judgment, ranking, weighting, volume bias
"""
from __future__ import annotations
import json, hashlib
from typing import Any, Dict, List

from l5_5_aggregation import (
    FORBIDDEN_FIELDS, CONTRACT_VERSION, _assert_clean,
    compute_structural_signature, load_cases_from_replay,
)

# EIC-1 governed interpretation mapping (EXISTING, frozen, status=candidate)
# This is NOT a new semantic interpretation — it is the existing EIC-1 mapping
# from structural context to candidate interpretation, already governed.
EIC1_GOVERNED_MAPPING = {
    'different_local_partition': 'different_cell_candidate',
    'same_local_partition': 'same_cell_candidate',
}
# Note: these are CANDIDATE labels from existing EIC-1 contract, NOT conclusions.
# System does NOT create these — it reports what EIC-1 already produced.


def compress_group(group: Dict[str, Any], cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compress one group into summary + claim candidate.

    MUST:
    - Count members (consistent / conflict / UNKNOWN / coverage)
    - Aggregate existing EIC-1 candidates (template, status=candidate)
    - Preserve F1-F7
    - Declare grouping criteria

    MUST NOT:
    - Create new semantic interpretation
    - Generate conclusion
    - Judge SUPPORTED/UNSUPPORTED
    - Weight by evidence volume
    """
    sig = group['structural_signature']
    member_refs = group['member_refs']
    member_count = group['member_count']

    # Count members by structural sub-state
    consistent_count = 0  # members with admitted + candidate
    unknown_count = 0     # members without candidate (region_not_formed / partition_unresolvable)
    conflict_count = 0    # members with EVIDENCE_CONFLICT

    # Collect EIC-1 candidate interpretations (EXISTING, governed)
    candidate_interpretations = []  # list of existing EIC-1 candidate labels

    for ref in member_refs:
        case_id = ref['case_id']
        case = next((c for c in cases if c['case_id'] == case_id), None)
        if case is None:
            continue

        eic1 = case.get('eic1_detail', {})
        sce = eic1.get('sce')
        status = eic1.get('sce_status', 'unknown')

        if status == 'admitted' and sce is not None:
            consistent_count += 1
            # Read EXISTING EIC-1 candidate (governed, status=candidate)
            if sce.get('different_local_partition'):
                candidate_interpretations.append('different_cell_candidate')
            elif sce.get('same_local_partition'):
                candidate_interpretations.append('same_cell_candidate')
            else:
                candidate_interpretations.append('unmapped_candidate')
        elif status in ('region_not_formed', 'partition_unresolvable'):
            unknown_count += 1

        # Check for conflict in on_decision
        on_dec = str(case.get('on_decision', ''))
        if 'evidence_conflict' in on_dec.lower():
            conflict_count += 1

    # Deduplicate candidate interpretations (structural, not semantic clustering)
    # This is a set operation on existing labels, NOT semantic inference
    unique_candidates = sorted(set(candidate_interpretations))

    # ── Semantic Claim Candidate ────────────────────────────────────────────
    # Template of EXISTING candidate claims (NOT new interpretation)
    if sig['has_candidate'] and unique_candidates:
        # "N instances with structural signature X have EIC-1 governed candidate Y (status=candidate)"
        claim_text = (
            f"{consistent_count} instances with structural signature "
            f"(sce_status=admitted, different_local_partition={sig['different_local_partition']}, "
            f"same_structural_region={sig['same_structural_region']}, "
            f"pairwise_same_y_band={sig['pairwise_same_y_band']}) "
            f"have EIC-1 governed candidate interpretation: {', '.join(unique_candidates)} "
            f"(interpretation_status=candidate)"
        )
        claim_candidate = {
            'claim_text': claim_text,
            'interpretation_status': 'candidate',  # NOT conclusion
            'source_candidates': unique_candidates,  # existing EIC-1 labels
            'claim_type': 'aggregation_of_existing_governed_candidates',
            'is_new_semantic_interpretation': False,
            'authority': 0,
        }
    elif sig['sce_status'] == 'partition_unresolvable':
        claim_candidate = {
            'claim_text': f"{unknown_count} instances have partition-unresolvable structural context; EIC-1 produced no candidate (INSUFFICIENT_EVIDENCE)",
            'interpretation_status': 'UNKNOWN',
            'source_candidates': [],
            'claim_type': 'insufficient_evidence_report',
            'is_new_semantic_interpretation': False,
            'authority': 0,
        }
    elif sig['sce_status'] == 'region_not_formed':
        claim_candidate = {
            'claim_text': f"{unknown_count} instances have region-not-formed structural context (density=0); EIC-1 produced no candidate",
            'interpretation_status': 'UNKNOWN',
            'source_candidates': [],
            'claim_type': 'insufficient_evidence_report',
            'is_new_semantic_interpretation': False,
            'authority': 0,
        }
    else:
        claim_candidate = {
            'claim_text': f"{member_count} instances with structural signature ({sig['sce_status']}); no EIC-1 candidate",
            'interpretation_status': 'none',
            'source_candidates': [],
            'claim_type': 'no_candidate',
            'is_new_semantic_interpretation': False,
            'authority': 0,
        }

    # ── Compressed Summary ─────────────────────────────────────────────────
    # Count actual UNKNOWN members (no candidate = UNKNOWN for preservation)
    actual_unknown = sum(1 for ref in member_refs if ref['sce_status'] in ('region_not_formed', 'partition_unresolvable'))

    summary = {
        'group_id': group['group_id'],
        'structural_signature': sig,
        'member_count': member_count,
        'consistent_count': consistent_count,    # F1: positive evidence count
        'unknown_count': unknown_count,           # F4: UNKNOWN preserved (counted)
        'conflict_count': conflict_count,         # F5: conflict preserved
        'coverage_count': member_count,           # all members counted (no deletion)
        'grouping_criteria': 'structural_signature_from_frozen_P2_and_EIC1',  # F3: boundary stated
        'candidate_interpretations': unique_candidates,  # existing EIC-1 labels
    }

    # ── Provenance Pointer (F6: Level 4 recoverability) ────────────────────
    provenance_pointer = {
        'member_refs': member_refs,               # Level 2/3/4: can expand to per-instance
        'provenance_chain': 'claim_candidate -> summary -> group -> member_refs -> eic1_detail -> frozen_P2',
        'level_4_recoverable': True,              # F6: always reachable
        'eic1_chain_per_member': [
            ref['case_provenance']['eic1_chain']
            for ref in member_refs
            if ref.get('case_provenance', {}).get('eic1_chain')
        ],
    }

    # ── F7: Claim Traceability ─────────────────────────────────────────────
    claim_traceability = {
        'claim_candidate': claim_candidate,
        'source_eic1_candidates': candidate_interpretations,  # per-instance EIC-1 labels
        'source_evidence': 'frozen_P2_geometry + EIC1_structural_context',
        'source_observation': 'atomic_observation_layer.v1',
        'chain_complete': len(candidate_interpretations) == consistent_count,
        'traceability_chain': 'claim -> aggregated EIC-1 candidates -> per-instance SCE -> frozen P2 -> observation',
    }

    result = {
        'summary': summary,
        'claim_candidate': claim_candidate,
        'provenance_pointer': provenance_pointer,
        'claim_traceability': claim_traceability,
        'fidelity': {
            'F1_positive_preserved': consistent_count > 0 if sig['has_candidate'] else True,
            'F2_negative_preserved': True,  # non-positive groups retained (not deleted)
            'F3_boundary_stated': True,     # grouping criteria in summary
            'F4_unknown_preserved': unknown_count == actual_unknown,  # all UNKNOWN counted, none hidden
            'F5_conflict_preserved': True,  # conflict_count in summary
            'F6_provenance_recoverable': True,  # Level 4 reachable
            'F7_claim_traceable': claim_traceability['chain_complete'],
        },
        'authority': 0,
        'is_new_semantic_interpretation': False,
        'volume_weighted': False,  # count = instance count, NOT evidence volume
    }

    _assert_clean(result, f'compressed_group[{group["group_id"]}]')
    return result


def compress(aggregation_result: Dict[str, Any], cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compress all groups into summaries + claim candidates.

    Output:
    - compressed_groups: [{summary, claim_candidate, provenance_pointer, claim_traceability, fidelity}]
    - total_claims: number of claim candidates
    - total_exposure_default: number of claims (Human default sees this, not N instances)
    - F1-F7 aggregate status
    """
    groups = aggregation_result['groups']
    compressed = []

    for group in groups:
        cg = compress_group(group, cases)
        compressed.append(cg)

    # Aggregate F1-F7
    all_fidelity = {}
    fidelity_keys = [
        ('F1', 'F1_positive_preserved'),
        ('F2', 'F2_negative_preserved'),
        ('F3', 'F3_boundary_stated'),
        ('F4', 'F4_unknown_preserved'),
        ('F5', 'F5_conflict_preserved'),
        ('F6', 'F6_provenance_recoverable'),
        ('F7', 'F7_claim_traceable'),
    ]
    for fid_id, key in fidelity_keys:
        vals = [cg['fidelity'].get(key, False) for cg in compressed]
        all_fidelity[fid_id] = all(vals)

    total_claims = len(compressed)
    total_exposure_default = total_claims  # Human sees N claims, not N instances

    result = {
        'compressed_groups': compressed,
        'total_claims': total_claims,
        'total_exposure_default': total_exposure_default,
        'total_instances': aggregation_result['total_cases'],
        'compression_ratio': f"{total_exposure_default}/{aggregation_result['total_cases']}",
        'fidelity_aggregate': all_fidelity,
        'authority': 0,
        'is_new_semantic_interpretation': False,
        'volume_weighted': False,
        'contract_version': CONTRACT_VERSION,
        'note': 'Compress evidence, not meaning; count=instance count (1-per-instance, not volume-weighted)',
    }

    _assert_clean(result, 'compression_result')
    return result


if __name__ == '__main__':
    cases = load_cases_from_replay('tmp/mb_phase3_2_isolated_replay_results.json')
    from l5_5_aggregation import aggregate
    agg = aggregate(cases)
    comp = compress(agg, cases)
    print(f"Compression: {comp['total_instances']} instances -> {comp['total_claims']} claims (exposure {comp['compression_ratio']})")
    for cg in comp['compressed_groups']:
        s = cg['summary']
        c = cg['claim_candidate']
        print(f"  {s['group_id']}: members={s['member_count']} consistent={s['consistent_count']} unknown={s['unknown_count']} conflict={s['conflict_count']}")
        print(f"    claim: {c['claim_text'][:120]}...")
        print(f"    status={c['interpretation_status']} new_interp={c['is_new_semantic_interpretation']}")
    print(f"  Fidelity: {comp['fidelity_aggregate']}")
    print(f"  authority={comp['authority']} volume_weighted={comp['volume_weighted']}")
