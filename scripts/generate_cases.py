#!/usr/bin/env python3
"""
HVA-09: Generate experiment_cases.json
Builds A and B condition case sets from P7 data + Evidence Pack v2.
"""
import json, hashlib, os, re
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PHASE2_DIR = os.path.dirname(SCRIPT_DIR)
TMP = os.path.dirname(PHASE2_DIR)
BASE = os.path.dirname(TMP)

def sha256_16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]

def sha256_full(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def derive_ends_period(ta):
    return bool(ta) and ta.rstrip().endswith('.')

def derive_starts_capital(tb):
    return bool(tb) and tb[0].isupper()

MARKER_PATTERNS = {
    'citation_marker': re.compile(r'\[\d+\]'),
    'references_header': re.compile(r'^\s*References\s*$', re.MULTILINE | re.IGNORECASE),
    'volume_marker': re.compile(r'vol\.', re.IGNORECASE),
    'pages_marker': re.compile(r'pp\.', re.IGNORECASE),
    'online_marker': re.compile(r'\[Online\]'),
    'doi_marker': re.compile(r'doi\.org|doi:', re.IGNORECASE),
    'arxiv_marker': re.compile(r'arXiv', re.IGNORECASE),
    'available_marker': re.compile(r'Available:', re.IGNORECASE),
    'publisher_city_marker': re.compile(r'[A-Z][a-z]+,\s+[A-Z]{2}:'),
}

def extract_markers(text):
    return {name: len(p.findall(text)) for name, p in MARKER_PATTERNS.items()}

def clean_line(line):
    clean = line
    if clean.startswith('>>>'):
        clean = clean[3:]
    clean = clean.replace('[TEXT A]', '').replace('[TEXT B]', '')
    return clean.strip()

def distill_context(page_context, text_a, text_b, window_before=3, window_after=4):
    if not page_context or not page_context.strip():
        return {'available': False, 'context_text': '', 'human_view': '', 'compression_ratio': 0, 'raw_length': 0, 'distilled_length': 0}
    
    lines = page_context.split('\n')
    total = len(lines)
    
    b_idx = None
    for i, line in enumerate(lines):
        clean = clean_line(line)
        if text_b in clean:
            b_idx = i
            break
    if b_idx is None:
        for i, line in enumerate(lines):
            if '[TEXT B]' in line:
                b_idx = i
                break
    if b_idx is None:
        b_idx = max(0, total // 2)
    
    a_idx = None
    for i in range(b_idx, max(b_idx - 10, -1), -1):
        clean = clean_line(lines[i])
        if text_a in clean:
            a_idx = i
            break
    if a_idx is None:
        for i in range(b_idx, max(b_idx - 10, -1), -1):
            if '[TEXT A]' in lines[i]:
                a_idx = i
                break
    if a_idx is None:
        a_idx = max(0, b_idx - 1)
    
    win_start = max(0, min(a_idx, b_idx) - window_before)
    win_end = min(total, max(a_idx, b_idx) + window_after)
    
    parts = []
    for i in range(win_start, win_end):
        clean = clean_line(lines[i])
        prefix = ''
        if i == a_idx:
            prefix = '[A] '
        elif i == b_idx:
            prefix = '[B] '
        if clean:
            parts.append(f"{prefix}{clean}")
    
    context_text = '\n'.join(parts)
    return {
        'available': True,
        'context_text': context_text,
        'human_view': context_text,
        'compression_ratio': round(len(context_text) / max(len(page_context), 1), 3),
        'raw_length': len(page_context),
        'distilled_length': len(context_text),
        'window_start': win_start,
        'window_end': win_end,
    }

# Verify frozen baseline
tld_hash = sha256_16(os.path.join(BASE, 'chunker', 'table_line_detector.py'))
gt_hash = sha256_16(os.path.join(TMP, 'is11_semantic_ground_truth.json'))
me_hash = sha256_16(os.path.join(TMP, 'is11_machine_evaluation_results.json'))
reg = json.load(open(os.path.join(TMP, 'perception', 'atomic_observation', 'layer_registry.json')))
drift = sum(1 for k, v in reg['frozen_sources'].items() if sha256_full(v['path']) != v['sha256'])
assert drift == 0 and tld_hash == '022f5c21e872ad9e' and gt_hash == '7349963d0d23b5ef'

# Load data
p7m = json.load(open(os.path.join(TMP, 'perception', 'p7', 'independent_machine_resolvability_results.json')))
p7m_map = {c['case_id']: c for c in p7m['machine_results']}
p7r = json.load(open(os.path.join(TMP, 'perception', 'p7', 'independent_evaluation_human_review', 'reviewer_a_blind_cases.json')))
p7r_map = {c['case_id']: c for c in p7r.get('cases', [])}

# 15 experiment cases
CASE_IDS = [
    # SC-05 FP (5)
    'IND-AMB-003', 'IND-AMB-002', 'IND-AMB-052', 'IND-AMB-033', 'IND-AMB-049',
    # SC-05 TP (3)
    'IND-AMB-008', 'IND-AMB-005', 'IND-AMB-134',
    # Additional diverse (7)
    'IND-AMB-001', 'IND-AMB-090', 'IND-AMB-084', 'IND-AMB-054', 'IND-AMB-041',
    'IND-AMB-062', 'IND-AMB-067',
]

TIMESTAMP = datetime.now(timezone.utc).isoformat()

cases = []
for cid in CASE_IDS:
    mc = p7m_map[cid]
    rc = p7r_map.get(cid, {})
    ta = mc.get('text_a', '')
    tb = mc.get('text_b', '')
    de = mc.get('decision_evidence', {})
    pc = str(rc.get('page_context', '') or '')
    
    ends_period = derive_ends_period(ta)
    starts_capital = derive_starts_capital(tb)
    
    # S3 structural facts
    sf = {
        'tld_in_table': None,
        'tld_different_cell': None,
        'is01_a': de.get('is01_a'),
        'is02_b': de.get('is02_b'),
        'text_a_ends_period': ends_period,
        'text_b_starts_capital': starts_capital,
    }
    
    machine_decision = mc.get('machine_decision', 'UNKNOWN')
    machine_state = {
        'machine_decision': machine_decision,
        'label': f"Machine Decision (may be wrong): {machine_decision}",
    }
    
    # Distilled context
    distilled = distill_context(pc, ta, tb)
    
    # Structural markers (from distilled or raw)
    marker_source = 'distilled_context' if distilled['available'] else 'raw_page_context'
    markers = extract_markers(distilled['context_text'] if distilled['available'] else pc)
    markers_found = {k: v for k, v in markers.items() if v > 0}
    
    # --- Condition A: Current Evidence Pack (L0-L1 only) ---
    a_view_lines = [
        "=== Text A ===",
        ta,
        "",
        "=== Text B ===",
        tb,
        "",
        "=== Structural Facts ===",
        f"IS-01 (Number): {'YES' if sf['is01_a'] else 'NO'}",
        f"IS-02 (Text): {'YES' if sf['is02_b'] else 'NO'}",
        f"Text A ends with period: {'YES' if ends_period else 'NO'}",
        f"Text B starts with capital: {'YES' if starts_capital else 'NO'}",
        "",
        "=== Machine State ===",
        f"Machine Decision (may be wrong): {machine_decision}",
    ]
    a_view = '\n'.join(a_view_lines)
    
    # --- Condition B: Evidence Pack v2 ---
    b_view_lines = [
        "=== Text A ===",
        ta,
        "",
        "=== Text B ===",
        tb,
        "",
    ]
    if distilled['available']:
        b_view_lines.extend([
            "=== Relevant Context ===",
            distilled['human_view'],
            "",
        ])
    if markers_found:
        b_view_lines.extend([
            "=== Structural Markers (in context) ===",
        ])
        for name, count in markers_found.items():
            b_view_lines.append(f"  {name}: {count}")
        b_view_lines.append("")
    b_view_lines.extend([
        "=== Structural Facts ===",
        f"IS-01 (Number): {'YES' if sf['is01_a'] else 'NO'}",
        f"IS-02 (Text): {'YES' if sf['is02_b'] else 'NO'}",
        f"Text A ends with period: {'YES' if ends_period else 'NO'}",
        f"Text B starts with capital: {'YES' if starts_capital else 'NO'}",
        "",
        "=== Machine State ===",
        f"Machine Decision (may be wrong): {machine_decision}",
    ])
    b_view = '\n'.join(b_view_lines)
    
    case = {
        'case_id': cid,
        'document_id': mc.get('document_id', ''),
        'page': mc.get('page', 0),
        'text_a': ta,
        'text_b': tb,
        'semantic_gt': mc.get('semantic_gt', ''),
        'boundary_class': mc.get('boundary_class', ''),
        'machine_decision': machine_decision,
        'machine_agrees_with_gt': (machine_decision == mc.get('semantic_gt', '')),
        
        # Condition A
        'condition_a': {
            'view': a_view,
            'view_length': len(a_view),
            'has_context': False,
            'has_markers': False,
            'visible_fields': 6,
        },
        
        # Condition B
        'condition_b': {
            'view': b_view,
            'view_length': len(b_view),
            'has_context': distilled['available'],
            'has_markers': len(markers_found) > 0,
            'markers': markers_found,
            'markers_source': marker_source,
            'distilled_context': distilled,
            'raw_context': pc,
            'raw_context_length': len(pc),
            'visible_fields': 6 + (1 if distilled['available'] else 0) + (1 if markers_found else 0),
            'compression_ratio': distilled['compression_ratio'],
        },
        
        'provenance': {
            'machine_eval_hash': me_hash,
            'tld_hash': tld_hash,
            'gt_hash': gt_hash,
            'timestamp': TIMESTAMP,
        },
    }
    cases.append(case)

# Output
output = {
    'metadata': {
        'experiment': 'HVA-09 Evidence Pack v2 Human Effect Experiment',
        'date': TIMESTAMP,
        'total_cases': len(cases),
        'conditions': ['A (Current Pack)', 'B (Evidence Pack v2)'],
        'human_task': 'MERGE / KEEP_SEPARATE / UNKNOWN',
        'counterbalancing': 'AB/BA (pilot)',
        'status': 'PILOT / EXPLORATORY',
        'frozen_baseline': {
            'tld_hash': tld_hash,
            'gt_hash': gt_hash,
            'machine_eval_hash': me_hash,
            'drift': f'{drift}/7 INTACT',
        },
    },
    'cases': cases,
}

out_path = os.path.join(SCRIPT_DIR, 'experiment_cases.json')
with open(out_path, 'w') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"=== experiment_cases.json ===")
print(f"  Path: {out_path}")
print(f"  Size: {os.path.getsize(out_path):,} bytes")
print(f"  Cases: {len(cases)}")
print(f"\nCase summary:")
for c in cases:
    a_len = c['condition_a']['view_length']
    b_len = c['condition_b']['view_length']
    ctx = 'Y' if c['condition_b']['has_context'] else 'N'
    mk = len(c['condition_b'].get('markers', {}))
    print(f"  {c['case_id']}: gt={c['semantic_gt']:>12}, A={a_len:>4}ch, B={b_len:>4}ch, ctx={ctx}, markers={mk}")

print(f"\nFrozen baseline: drift={drift}/7 INTACT")
