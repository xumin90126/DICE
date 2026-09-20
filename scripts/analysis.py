#!/usr/bin/env python3
"""
HVA-09 Analysis Script
Analyzes experiment results for M1-M6 metrics.
Designed to work with real Human data when available.
Currently produces INSUFFICIENT_EVIDENCE since no real Human Participant.
"""
import json
import os
import statistics
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(SCRIPT_DIR, 'experiment_results.json')
CASES_PATH = os.path.join(SCRIPT_DIR, 'experiment_cases.json')

def load_results():
    if not os.path.exists(RESULTS_PATH):
        return [], {}
    with open(RESULTS_PATH) as f:
        data = json.load(f)
    return data.get('results', []), data

def load_cases():
    with open(CASES_PATH) as f:
        return json.load(f)

def analyze(results, cases_data):
    """Run M1-M6 analysis on results."""
    
    if not results:
        return {
            'status': 'NO_RESULTS',
            'human_effect': 'INSUFFICIENT_EVIDENCE',
            'reason': 'No experiment results available',
        }
    
    # Check if these are real human results or dry-run
    # Dry-run results all have decision=UNKNOWN and decision_time_ms=3000
    is_dry_run = all(r['decision'] == 'UNKNOWN' and r['decision_time_ms'] == 3000 for r in results)
    
    if is_dry_run:
        return {
            'status': 'DRY_RUN_ONLY',
            'human_effect': 'INSUFFICIENT_EVIDENCE',
            'reason': 'Only dry-run data available. No real Human Participant.',
            'dry_run_results': len(results),
        }
    
    # Separate by condition
    a_results = [r for r in results if r['condition'] == 'A']
    b_results = [r for r in results if r['condition'] == 'B']
    
    analysis = {
        'total_results': len(results),
        'condition_a_count': len(a_results),
        'condition_b_count': len(b_results),
        'is_dry_run': False,
    }
    
    # M1: Decision Accuracy
    a_correct = sum(1 for r in a_results if r['decision'] == r['semantic_gt'])
    b_correct = sum(1 for r in b_results if r['decision'] == r['semantic_gt'])
    analysis['M1_decision_accuracy'] = {
        'A_accuracy': round(a_correct / len(a_results), 3) if a_results else None,
        'B_accuracy': round(b_correct / len(b_results), 3) if b_results else None,
        'A_correct': a_correct, 'A_total': len(a_results),
        'B_correct': b_correct, 'B_total': len(b_results),
    }
    
    # M2: Decision Time (median)
    a_times = [r['decision_time_ms'] for r in a_results]
    b_times = [r['decision_time_ms'] for r in b_results]
    analysis['M2_decision_time'] = {
        'A_median_ms': statistics.median(a_times) if a_times else None,
        'B_median_ms': statistics.median(b_times) if b_times else None,
        'A_mean_ms': round(statistics.mean(a_times), 1) if a_times else None,
        'B_mean_ms': round(statistics.mean(b_times), 1) if b_times else None,
    }
    
    # M3: Evidence Seeking
    a_expanded = sum(1 for r in a_results if r.get('raw_context_expanded'))
    b_expanded = sum(1 for r in b_results if r.get('raw_context_expanded'))
    a_exp_count = [r.get('evidence_expansion_count', 0) for r in a_results]
    b_exp_count = [r.get('evidence_expansion_count', 0) for r in b_results]
    analysis['M3_evidence_seeking'] = {
        'A_raw_expanded': a_expanded,
        'B_raw_expanded': b_expanded,
        'A_expansion_count_mean': round(statistics.mean(a_exp_count), 2) if a_exp_count else None,
        'B_expansion_count_mean': round(statistics.mean(b_exp_count), 2) if b_exp_count else None,
    }
    
    # M4: Decision Quality (by type)
    a_merge = [r for r in a_results if r['semantic_gt'] == 'MERGE']
    a_keep = [r for r in a_results if r['semantic_gt'] == 'KEEP_SEPARATE']
    b_merge = [r for r in b_results if r['semantic_gt'] == 'MERGE']
    b_keep = [r for r in b_results if r['semantic_gt'] == 'KEEP_SEPARATE']
    
    analysis['M4_decision_quality'] = {
        'A_merge_accuracy': round(sum(1 for r in a_merge if r['decision'] == 'MERGE') / len(a_merge), 3) if a_merge else None,
        'A_keep_accuracy': round(sum(1 for r in a_keep if r['decision'] == 'KEEP_SEPARATE') / len(a_keep), 3) if a_keep else None,
        'B_merge_accuracy': round(sum(1 for r in b_merge if r['decision'] == 'MERGE') / len(b_merge), 3) if b_merge else None,
        'B_keep_accuracy': round(sum(1 for r in b_keep if r['decision'] == 'KEEP_SEPARATE') / len(b_keep), 3) if b_keep else None,
        'A_unknown_count': sum(1 for r in a_results if r['decision'] == 'UNKNOWN'),
        'B_unknown_count': sum(1 for r in b_results if r['decision'] == 'UNKNOWN'),
    }
    
    # M5: Automation Bias
    # Focus on cases where Machine != GT
    a_machine_wrong = [r for r in a_results if not r.get('machine_agrees_with_gt', True)]
    b_machine_wrong = [r for r in b_results if not r.get('machine_agrees_with_gt', True)]
    
    a_followed_machine_when_wrong = sum(1 for r in a_machine_wrong if r['decision'] == r['machine_decision'])
    b_followed_machine_when_wrong = sum(1 for r in b_machine_wrong if r['decision'] == r['machine_decision'])
    
    analysis['M5_automation_bias'] = {
        'A_machine_wrong_cases': len(a_machine_wrong),
        'B_machine_wrong_cases': len(b_machine_wrong),
        'A_followed_machine_when_wrong': a_followed_machine_when_wrong,
        'B_followed_machine_when_wrong': b_followed_machine_when_wrong,
        'A_follow_rate': round(a_followed_machine_when_wrong / len(a_machine_wrong), 3) if a_machine_wrong else None,
        'B_follow_rate': round(b_followed_machine_when_wrong / len(b_machine_wrong), 3) if b_machine_wrong else None,
    }
    
    # M6: Evidence Exposure
    analysis['M6_evidence_exposure'] = {
        'A_avg_view_length': round(statistics.mean([r.get('view_length_a', 0) for r in a_results]), 1) if a_results else None,
        'B_avg_view_length': round(statistics.mean([r.get('view_length_b', 0) for r in b_results]), 1) if b_results else None,
        'B_avg_raw_context_length': round(statistics.mean([r.get('raw_context_length_b', 0) for r in b_results]), 1) if b_results else None,
        'B_avg_compression_ratio': round(statistics.mean([r.get('compression_ratio_b', 0) for r in b_results]), 3) if b_results else None,
    }
    
    # FP-specific analysis (5 SC-05 FP cases)
    fp_ids = ['IND-AMB-003', 'IND-AMB-002', 'IND-AMB-052', 'IND-AMB-033', 'IND-AMB-049']
    fp_a = [r for r in a_results if r['case_id'] in fp_ids]
    fp_b = [r for r in b_results if r['case_id'] in fp_ids]
    
    analysis['fp_specific'] = {
        'fp_in_A': len(fp_a),
        'fp_in_B': len(fp_b),
        'A_fp_correct': sum(1 for r in fp_a if r['decision'] == r['semantic_gt']),
        'B_fp_correct': sum(1 for r in fp_b if r['decision'] == r['semantic_gt']),
        'A_fp_expanded': sum(1 for r in fp_a if r.get('raw_context_expanded')),
        'B_fp_expanded': sum(1 for r in fp_b if r.get('raw_context_expanded')),
    }
    
    # Overall verdict
    accuracy_preserved = (analysis['M1_decision_accuracy']['B_accuracy'] is None or 
                         analysis['M1_decision_accuracy']['A_accuracy'] is None or
                         analysis['M1_decision_accuracy']['B_accuracy'] >= analysis['M1_decision_accuracy']['A_accuracy'])
    
    evidence_seeking_reduced = (analysis['M3_evidence_seeking']['B_raw_expanded'] <= analysis['M3_evidence_seeking']['A_raw_expanded'])
    
    time_not_increased = (analysis['M2_decision_time']['B_median_ms'] is None or 
                         analysis['M2_decision_time']['A_median_ms'] is None or
                         analysis['M2_decision_time']['B_median_ms'] <= analysis['M2_decision_time']['A_median_ms'] * 1.5)
    
    bias_not_increased = (analysis['M5_automation_bias']['B_follow_rate'] is None or 
                         analysis['M5_automation_bias']['A_follow_rate'] is None or
                         analysis['M5_automation_bias']['B_follow_rate'] <= analysis['M5_automation_bias']['A_follow_rate'])
    
    if accuracy_preserved and evidence_seeking_reduced and time_not_increased and bias_not_increased:
        analysis['verdict'] = 'SUPPORT'
    elif accuracy_preserved and evidence_seeking_reduced:
        analysis['verdict'] = 'PARTIAL'
    else:
        analysis['verdict'] = 'NOT_SUPPORTED'
    
    analysis['human_effect'] = 'SUPPORTED' if analysis['verdict'] == 'SUPPORT' else \
                               'PARTIAL' if analysis['verdict'] == 'PARTIAL' else 'NOT_SUPPORTED'
    
    return analysis

def main():
    results, raw = load_results()
    cases_data = load_cases()
    
    analysis = analyze(results, cases_data)
    
    output = {
        'analysis': analysis,
        'metadata': cases_data['metadata'],
        'result_count': len(results),
    }
    
    out_path = os.path.join(SCRIPT_DIR, 'analysis_output.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"=== HVA-09 Analysis ===")
    print(f"Results: {len(results)}")
    print(f"Status: {analysis.get('status', 'ANALYZED')}")
    print(f"Human Effect: {analysis.get('human_effect', 'UNKNOWN')}")
    
    if analysis.get('status') not in ('NO_RESULTS', 'DRY_RUN_ONLY'):
        for key in ['M1_decision_accuracy', 'M2_decision_time', 'M3_evidence_seeking',
                     'M4_decision_quality', 'M5_automation_bias', 'M6_evidence_exposure']:
            if key in analysis:
                print(f"\n{key}:")
                for k, v in analysis[key].items():
                    print(f"  {k}: {v}")
    
    print(f"\nVerdict: {analysis.get('verdict', 'N/A')}")

if __name__ == '__main__':
    main()
