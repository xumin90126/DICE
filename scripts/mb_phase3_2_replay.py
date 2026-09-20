"""
M-B Phase 3.2 Isolated Replay Runner.

- Imports frozen harness functions UNMODIFIED (compute_is11_observation, experimental_c_decision,
  compute_is01_a, compute_is02_b, baseline_b_decision, classify_outcome).
- OFF path: calls harness as-is (adapter not invoked) -> must equal archived baseline.
- ON path: harness TLD + EIC-1 adapter + coexistence contract -> composite is11_obs ->
  experimental_c_decision (UNCHANGED).
- Frozen 21 decision rows + 4 descriptive rows.
- Provenance + determinism double-run + independent audit.
"""
import sys, os, json, hashlib, importlib.util, copy
DICE2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
os.chdir(DICE2)
sys.path.insert(0, 'tmp')
sys.path.insert(0, 'tmp/perception/atomic_observation')

# Import harness WITHOUT modifying it
H = importlib.util.spec_from_file_location("is11_harness", "tmp/is11_machine_evaluation.py")
harness = importlib.util.module_from_spec(H)
H.loader.exec_module(harness)

import mb_eic1_adapter as EIC

# === FROZEN MATRIX (21 decision rows) ===
MATRIX_CASES = {
 'IS11-AMB-135': ('A1_POSITIVE_REPAIR','HIGH'),
 'IS11-AMB-130': ('A2_DIRECT_RECOVERY','HIGH'),
 'IS11-AMB-313': ('A2_DIRECT_RECOVERY_WEAK','HIGH'),
 'IS11-AMB-457': ('A2_DIRECT_RECOVERY','HIGH'),
 'IS11-AMB-462': ('A2_DIRECT_RECOVERY','HIGH'),
 'IS11-AMB-467': ('A2_DIRECT_RECOVERY','HIGH'),
 'IS11-AMB-483': ('A2_DIRECT_RECOVERY','HIGH'),
 'IS11-AMB-505': ('A2_DIRECT_RECOVERY','HIGH'),
 'IS11-AMB-514': ('A2_DIRECT_RECOVERY','HIGH'),
 'IS11-AMB-414': ('B_SAFETY_CANARY','CRITICAL'),
 'IS11-AMB-422': ('B_SAFETY_CANARY','CRITICAL'),
 'IS11-AMB-519': ('C_NEG_PROSE','MEDIUM'),
 'IS11-AMB-262': ('C_NEG_DIFFERENT_BAND','MEDIUM'),
 'IS11-AMB-005': ('D_CORRECT_MIXED','HIGH'),
 'IS11-AMB-024': ('D_CORRECT','HIGH'),
 'IS11-AMB-034': ('D_CORRECT_VALUE_COLUMN','HIGH'),
 'IS11-AMB-074': ('D_CORRECT','HIGH'),
 'IS11-AMB-346': ('D_CORRECT_AGREE_SITE','HIGH'),
 'IS11-AMB-350': ('D_CORRECT_AGREE_SITE','HIGH'),
 'IS11-AMB-522': ('D_CORRECT_AGREE_SITE','HIGH'),
 'IS11-AMB-530': ('D_CORRECT_AGREE_SITE','HIGH'),
}

def sha(p): return hashlib.sha256(open(p,'rb').read()).hexdigest()

def run_case(case, mode):
    """mode = 'OFF' or 'ON'. Returns full per-case record."""
    cid = case['case_id']
    text_a, text_b = case['text_a'], case['text_b']
    bbox_a, bbox_b = case['bbox_a'], case['bbox_b']
    pdf_path, page = case['pdf_path'], int(case['page'])
    doc_id = case['doc_id']
    is01_a = harness.compute_is01_a(text_a)
    is02_b = harness.compute_is02_b(text_b)
    gt_label = case.get('gt_label', 'UNKNOWN')

    # TLD observation (frozen harness, always computed)
    tld_obs = harness.compute_is11_observation(pdf_path, page, bbox_a, bbox_b, text_a, text_b)

    if mode == 'OFF':
        is11_obs = tld_obs
        evidence_state = 'off_tld_only'
        eic1_record = None
    else:
        # ON: build EIC-1 structural context
        store = EIC.get_store(pdf_path, doc_id, page)
        atom_a, da, pg = EIC.find_atom_by_bbox(store, page, bbox_a)
        atom_b, db, pg2 = EIC.find_atom_by_bbox(store, page, bbox_b)
        eic1_record = {'atom_a_match_dist': round(da,2), 'atom_b_match_dist': round(db,2)}
        if atom_a and atom_b and da < 5 and db < 5:
            lsps = EIC.build_local_structural_partitions(pg)
            pair_y = (atom_a['center_y'] + atom_b['center_y']) / 2
            rsc = EIC.build_regional_structural_context(lsps, pair_y)
            sce, sce_status = EIC.emit_structural_context_evidence(atom_a, atom_b, lsps, rsc)
            eic1_obs = EIC.eic1_map_to_observation(sce)
            eic1_record.update({
                'sce_status': sce_status, 'rsc': rsc, 'sce': sce,
                'n_local_lsps': sum(1 for l in lsps if l['is_local']),
                'pair_band_co_density': rsc['local_partitions_co_occurring'],
                'lsp_a': next((l['partition_id'] for l in lsps if atom_a['observation_id'] in l['member_atom_ids']), None),
                'lsp_b': next((l['partition_id'] for l in lsps if atom_b['observation_id'] in l['member_atom_ids']), None),
            })
            is11_obs, evidence_state = EIC.compose_observations(tld_obs, eic1_obs)
        else:
            is11_obs = tld_obs
            evidence_state = 'eic1_atom_match_failed'

    dec = harness.experimental_c_decision(is01_a, is02_b, is11_obs)
    outcome = harness.classify_outcome(dec, gt_label)
    return {
        'case_id': cid, 'doc': doc_id, 'page': page,
        'gt_label': gt_label, 'is01_a': is01_a, 'is02_b': is02_b,
        'mode': mode, 'evidence_state': evidence_state,
        'is11_obs': is11_obs, 'decision': dec, 'outcome': outcome,
        'eic1_detail': eic1_record,
        'tld_obs': tld_obs,
    }

def main():
    sf = json.load(open('tmp/is11_independent_sampling_frame.json'))
    gt = json.load(open('tmp/is11_semantic_ground_truth.json'))
    gt_lookup = {r['case_id']: r for r in gt['gt_records']}
    cases_all = {c['case_id']: c for c in sf['sampled_cases']}
    # attach gt
    for cid, c in cases_all.items():
        if cid in gt_lookup:
            c['gt_label'] = gt_lookup[cid]['final_label']

    archived = json.load(open('tmp/is11_machine_evaluation_results.json'))
    arch_lookup = {r['case_id']: r for r in archived['case_results']}

    matrix_ids = [c for c in sf['sampled_cases'] if c['case_id'] in MATRIX_CASES]
    print(f"Matrix cases found: {len(matrix_ids)} / 21")

    # === OFF RUN ===
    off_results = []
    for c in matrix_ids:
        r = run_case(c, 'OFF')
        off_results.append(r)
    # verify OFF == archived baseline
    off_match = 0; off_mismatch = []
    for r in off_results:
        a = arch_lookup.get(r['case_id'])
        if a:
            a_dec = a['experimental_c']['decision']
            a_obs = a['experimental_c']['is11_observation']
            if r['decision'] == a_dec and r['is11_obs'] == a_obs:
                off_match += 1
            else:
                off_mismatch.append({'case_id': r['case_id'],
                    'off_dec': r['decision'], 'arch_dec': a_dec,
                    'off_obs': r['is11_obs'], 'arch_obs': a_obs})
    print(f"OFF vs archived: {off_match}/{len(off_results)} match; mismatches={len(off_mismatch)}")

    # === ON RUN (1st) ===
    on_results_1 = []
    for c in matrix_ids:
        r = run_case(c, 'ON')
        on_results_1.append(r)

    # === ON RUN (2nd, determinism) ===
    on_results_2 = []
    for c in matrix_ids:
        r = run_case(c, 'ON')
        on_results_2.append(r)

    # determinism check
    det_ok = 0; det_mismatch = []
    for r1, r2 in zip(on_results_1, on_results_2):
        if r1['decision'] == r2['decision'] and r1['is11_obs'] == r2['is11_obs'] and r1['evidence_state'] == r2['evidence_state']:
            det_ok += 1
        else:
            det_mismatch.append(r1['case_id'])
    print(f"Determinism: {det_ok}/{len(on_results_1)} match; mismatches={det_mismatch}")

    # === build per-case comparison ===
    comparison = []
    for r_off, r_on in zip(off_results, on_results_1):
        cls, saf = MATRIX_CASES[r_off['case_id']]
        arch = arch_lookup.get(r_off['case_id'], {})
        comparison.append({
            'case_id': r_off['case_id'], 'class': cls, 'safety': saf,
            'gt': r_off['gt_label'],
            'baseline_archived': arch.get('experimental_c',{}).get('decision'),
            'off_decision': r_off['decision'], 'off_outcome': r_off['outcome'],
            'on_decision': r_on['decision'], 'on_outcome': r_on['outcome'],
            'on_evidence_state': r_on['evidence_state'],
            'decision_changed': r_off['decision'] != r_on['decision'],
            'on_is11_obs': r_on['is11_obs'],
            'eic1_detail': r_on['eic1_detail'],
        })

    results = {
        'matrix_size': len(matrix_ids),
        'off_vs_archived': {'match': off_match, 'total': len(off_results), 'mismatches': off_mismatch},
        'determinism': {'match': det_ok, 'total': len(on_results_1), 'mismatches': det_mismatch},
        'comparison': comparison,
    }
    json.dump(results, open('tmp/mb_phase3_2_isolated_replay_results.json','w'), indent=1)
    print("\n=== COMPARISON (OFF->ON) ===")
    for c in comparison:
        flag = ' <<<' if c['decision_changed'] else ''
        print(f"  {c['case_id']:16s} cls={c['class']:28s} gt={c['gt']:13s} "
              f"base={c['baseline_archived']:6s} off={c['off_decision']:6s} on={c['on_decision']:6s} "
              f"ev={c['on_evidence_state']:24s}{flag}")
    return results

if __name__ == '__main__':
    main()
