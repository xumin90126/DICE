#!/usr/bin/env python3
"""
DICE Potential Evaluation Candidate Set Construction
=====================================================

READ-ONLY research tooling script.
Reads 545 candidates from is11_independent_candidate_universe.json.
Applies structural classification, triviality filtering, coverage construction,
evidence availability check, and independence constraints.
Outputs a Potential Evaluation Candidate Set (NOT a final evaluation set).

DESIGN PRINCIPLES:
  - NO GT used for selection
  - NO Human difficulty (time, accuracy, disagreement) used for selection
  - NO experiment results used for selection
  - NO DICE Core modification
  - Deterministic and reproducible
  - Input file is NEVER modified (read-only)

PROVENANCE:
  Input:  tmp/is11_independent_candidate_universe.json (545 candidates)
  Output: tmp/potential_evaluation_case_set.json
  Date:   2026-09-12
"""

import json
import hashlib
import os
import re
from collections import defaultdict, Counter

# ============================================================
# CONFIGURATION
# ============================================================

INPUT_PATH = 'tmp/is11_independent_candidate_universe.json'
OUTPUT_PATH = 'tmp/potential_evaluation_case_set.json'
REPORT_PATH = 'tmp/potential_evaluation_case_construction.md'

# Independence constraints
MAX_PER_PAGE = 3          # ≤3 candidates per doc+page
MAX_PER_DOC_PCT = 0.35    # ≤35% from single document
CONTROL_RATIO = 0.10      # ~10% trivial cases kept as controls

# ============================================================
# STRUCTURAL CLASSIFICATION
# ============================================================

def is_numeric(text: str) -> bool:
    """Check if text is numeric (number, percentage, with M/B/x suffix)."""
    if not text or not text.strip():
        return False
    s = text.strip()
    # Remove common suffixes/prefixes
    s = re.sub(r'^[≤≥<>~]', '', s)
    s = s.replace('%', '').replace('M', '').replace('B', '').replace('x', '')
    s = s.replace(',', '').replace('(', '').replace(')', '').replace('-', '')
    s = s.replace('+', '').replace('×', '').replace('·', '').strip()
    if not s:
        return True  # was just a dash or symbol
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_axis_tick(text: str) -> bool:
    """Check if text looks like an axis tick label (0.xx, 1.xx, etc.)."""
    s = text.strip()
    return bool(re.match(r'^[0-9]\.[0-9]{1,2}$', s))


def is_short_capitalized(text: str) -> bool:
    """Check if text is a short capitalized header-like token."""
    s = text.strip()
    if len(s) > 25:
        return False
    if not s:
        return False
    # Check if starts with capital and is mostly alphabetic
    if not s[0].isupper():
        return False
    alpha_ratio = sum(1 for c in s if c.isalpha()) / max(len(s), 1)
    return alpha_ratio > 0.5


def ends_sentence(text: str) -> bool:
    """Check if text ends with sentence-ending punctuation."""
    s = text.strip()
    return s.endswith('.') or s.endswith('!') or s.endswith('?')


def ends_continuation(text: str) -> bool:
    """Check if text ends with continuation punctuation (suggesting same-unit)."""
    s = text.strip()
    return s.endswith(',') or s.endswith('(') or s.endswith(';') or s.endswith(':')


def contains_figure_marker(text: str) -> bool:
    """Check if text contains figure/caption markers."""
    s = text.upper()
    return 'FIG' in s or 'TABLE' in s and len(s) < 20


def classify_structure(candidate: dict) -> str:
    """
    Classify candidate into structural family.
    Uses ONLY deterministic structural features from candidate data.
    NO GT, NO human data.
    """
    ta = candidate.get('text_a', '').strip()
    tb = candidate.get('text_b', '').strip()
    
    a_num = is_numeric(ta)
    b_num = is_numeric(tb)
    a_axis = is_axis_tick(ta)
    b_axis = is_axis_tick(tb)
    
    # FIGURE_CAPTION: contains figure markers
    if contains_figure_marker(ta) or contains_figure_marker(tb):
        return 'FIGURE_CAPTION'
    
    # AXIS: both look like axis tick values
    if a_axis and b_axis:
        return 'AXIS'
    
    # TABLE_NUMERIC: both numeric, both short
    if a_num and b_num and len(ta) < 12 and len(tb) < 12:
        return 'TABLE_NUMERIC'
    
    # TABLE_HEADER: both short capitalized non-numeric
    if not a_num and not b_num:
        if is_short_capitalized(ta) and is_short_capitalized(tb):
            if len(ta) < 25 and len(tb) < 25:
                return 'TABLE_HEADER'
    
    # ROW_LABEL_VALUE: one numeric, one non-numeric, both short
    if a_num != b_num:
        if len(ta) < 35 and len(tb) < 35:
            return 'ROW_LABEL_VALUE'
    
    # PROSE: at least one text is long, or ends with sentence punctuation
    if len(ta) > 25 or len(tb) > 25:
        return 'PROSE'
    if ends_sentence(ta) or ends_continuation(ta):
        return 'PROSE'
    if ends_sentence(tb) or ends_continuation(tb):
        return 'PROSE'
    
    # Check if text looks like prose fragments
    if not a_num and not b_num and (len(ta) > 15 or len(tb) > 15):
        if ' ' in ta or ' ' in tb:
            return 'PROSE'
    
    return 'OTHER'


def classify_triviality(candidate: dict, family: str) -> str:
    """
    Classify triviality level based on structural features.
    This is NOT human difficulty — it's structural evaluation value.
    """
    ta = candidate.get('text_a', '').strip()
    tb = candidate.get('text_b', '').strip()
    a_num = is_numeric(ta)
    b_num = is_numeric(tb)
    
    # TRIVIAL_NUMERIC_PAIR: two numbers in different columns
    if family == 'TABLE_NUMERIC':
        return 'TRIVIAL_NUMERIC_PAIR'
    
    # TRIVIAL_HEADER_PAIR: two short headers in different columns
    if family == 'TABLE_HEADER':
        return 'TRIVIAL_HEADER_PAIR'
    
    # AXIS: trivially separable
    if family == 'AXIS':
        return 'TRIVIAL_AXIS_TICK'
    
    # Non-trivial table: ROW_LABEL_VALUE with potential ambiguity
    if family == 'ROW_LABEL_VALUE':
        # Check if there's a competing interpretation
        # "18 layers" / "27.94" — could be same-row (MERGE) or different-column (KEEP)
        if not a_num and b_num:
            # text label + number — potential row label + value
            return 'NONTRIVIAL_ROW_LABEL_VALUE'
        elif a_num and not b_num:
            return 'NONTRIVIAL_ROW_LABEL_VALUE'
        else:
            return 'NONTRIVIAL_ROW_LABEL_VALUE'
    
    # PROSE: potentially valuable
    if family == 'PROSE':
        if ends_sentence(ta) or ends_continuation(ta):
            return 'PROSE_BOUNDARY'
        return 'PROSE_FRAGMENT'
    
    # FIGURE_CAPTION: potentially valuable
    if family == 'FIGURE_CAPTION':
        return 'CAPTION_STRUCTURE'
    
    return 'UNCLASSIFIED'


# ============================================================
# EVALUATION OPPORTUNITY
# ============================================================

def assign_evaluation_opportunity(candidate: dict, family: str, 
                                   triviality: str) -> str:
    """
    Assign evaluation opportunity based on structural features.
    NOT human difficulty. NOT GT.
    """
    ta = candidate.get('text_a', '').strip()
    tb = candidate.get('text_b', '').strip()
    h_gap = candidate.get('h_gap', 0)
    line_obs = candidate.get('line_obs_count', 0)
    
    # LOW: trivial structures
    if triviality in ('TRIVIAL_NUMERIC_PAIR', 'TRIVIAL_HEADER_PAIR', 
                       'TRIVIAL_AXIS_TICK'):
        return 'LOW'
    
    # HIGH: prose boundary, figure caption — genuine structural ambiguity
    if family == 'PROSE' and triviality == 'PROSE_BOUNDARY':
        return 'HIGH'
    if family == 'FIGURE_CAPTION':
        return 'HIGH'
    
    # MEDIUM: row label + value (potential row vs column ambiguity)
    if family == 'ROW_LABEL_VALUE':
        # Check if there's a competing interpretation
        # Long label suggests it's a description, not just a column header
        label_text = ta if not is_numeric(ta) else tb
        if len(label_text) > 10:
            return 'MEDIUM'  # longer label → more context → potential ambiguity
        return 'MEDIUM'
    
    # MEDIUM: prose fragments without clear boundary
    if family == 'PROSE' and triviality == 'PROSE_FRAGMENT':
        return 'MEDIUM'
    
    # UNKNOWN: other
    return 'UNKNOWN'


def assign_potential_boundary(candidate: dict, family: str) -> bool:
    """
    Determine if candidate has potential boundary (competing interpretations).
    Based on structural features only. NOT GT.
    """
    ta = candidate.get('text_a', '').strip()
    tb = candidate.get('text_b', '').strip()
    
    # PROSE with sentence boundary: plausible MERGE (same paragraph flow)
    # vs plausible KEEP (separate sentences)
    if family == 'PROSE':
        if ends_sentence(ta) and tb and tb[0].isupper():
            return True  # sentence boundary — competing interpretations
        if ends_continuation(ta):
            return True  # continuation — competing interpretations
    
    # FIGURE_CAPTION: caption label + body — plausible MERGE (same caption)
    # vs plausible KEEP (different caption parts)
    if family == 'FIGURE_CAPTION':
        return True
    
    # ROW_LABEL_VALUE: label + value — plausible MERGE (same row description)
    # vs plausible KEEP (different columns)
    if family == 'ROW_LABEL_VALUE':
        return True
    
    return False


def assign_potential_conflict(candidate: dict) -> bool:
    """
    Determine if candidate has potential structural conflict.
    Based on evidence feature disagreement. NOT GT.
    """
    same_style = candidate.get('same_style', False)
    h_gap = candidate.get('h_gap', 0)
    dy = candidate.get('dy', 0)
    
    # Potential conflict: same style but large gap (style says "same",
    # but geometry says "different")
    if same_style and h_gap > 25:
        return True
    
    # Potential conflict: different style but small gap (geometry says "close",
    # but style says "different")
    if not same_style and h_gap < 15:
        return True
    
    return False


# ============================================================
# CUE RELEVANCE
# ============================================================

def assign_cue_relevance(candidate: dict, family: str, 
                          evaluation_opportunity: str) -> str:
    """
    Assign cue relevance based on evidence complexity.
    NOT cue effectiveness (that requires pilot).
    """
    line_obs = candidate.get('line_obs_count', 0)
    h_gap = candidate.get('h_gap', 0)
    same_style = candidate.get('same_style', False)
    
    # LOW: trivial cases — Cue unlikely to help
    if evaluation_opportunity == 'LOW':
        return 'LOW'
    
    # HIGH: complex evidence that's hard to read directly
    # Many observations on line → more context to parse
    # Large gap → more spatial reasoning needed
    if evaluation_opportunity == 'HIGH':
        if line_obs > 5 or h_gap > 20:
            return 'HIGH'
        return 'MEDIUM'
    
    # MEDIUM: some evidence complexity
    if evaluation_opportunity == 'MEDIUM':
        if line_obs > 5:
            return 'HIGH'
        return 'MEDIUM'
    
    return 'UNKNOWN'


# ============================================================
# EVIDENCE AVAILABILITY
# ============================================================

def check_evidence_availability(candidate: dict) -> dict:
    """
    Check evidence availability for each candidate.
    Based on what data exists in the candidate record.
    """
    pdf_path = candidate.get('pdf_path', '')
    
    # Image: PDF exists → image can be generated
    image_available = os.path.exists(pdf_path) if pdf_path else False
    
    # TLD: not computed at candidate generation time
    # (metadata states "table_line_detector.py was NOT called")
    tld_available = False  # not computed for candidates
    
    # Structural evidence: geometric features present
    has_geometry = all(k in candidate for k in 
                       ['bbox_a', 'bbox_b', 'h_gap', 'dy', 'w_a', 'w_b'])
    has_style = 'style_sig_a' in candidate and 'style_sig_b' in candidate
    structural_evidence = has_geometry and has_style
    
    # Cue: not computed for most candidates
    cue_available = False  # not computed at candidate level
    
    # Overall
    available = sum([image_available, tld_available, structural_evidence])
    if available >= 2:
        overall = 'PARTIAL'  # image + geometry, but no TLD/Cue
    elif available >= 1:
        overall = 'PARTIAL'
    else:
        overall = 'MISSING'
    
    return {
        'image_available': image_available,
        'tld_available': tld_available,
        'structural_evidence_available': structural_evidence,
        'cue_available': cue_available,
        'overall': overall,
    }


# ============================================================
# CEILING RISK (PRE-PILOT, STRUCTURAL)
# ============================================================

def assess_ceiling_risk(family: str, evaluation_opportunity: str,
                         triviality: str) -> str:
    """
    Assess structural ceiling risk.
    NOT observed human ceiling — pre-pilot structural estimate.
    """
    if triviality in ('TRIVIAL_NUMERIC_PAIR', 'TRIVIAL_HEADER_PAIR',
                       'TRIVIAL_AXIS_TICK'):
        return 'HIGH'  # obvious surface relation
    if evaluation_opportunity == 'LOW':
        return 'HIGH'
    if evaluation_opportunity == 'HIGH':
        return 'LOW'  # genuine ambiguity → low ceiling risk
    if evaluation_opportunity == 'MEDIUM':
        return 'MEDIUM'
    return 'UNKNOWN'


# ============================================================
# NEAR-DUPLICATE DETECTION
# ============================================================

def tokenize(text: str) -> set:
    """Simple word tokenization for similarity."""
    return set(re.findall(r'\w+', text.lower()))


def jaccard_similarity(set_a: set, set_b: set) -> float:
    """Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 1.0
    union = set_a | set_b
    if not union:
        return 0.0
    return len(set_a & set_b) / len(union)


def detect_near_duplicates(candidates: list) -> dict:
    """
    Detect near-duplicate candidates.
    Groups by doc+page, then checks text similarity and y-position.
    """
    # Group by doc+page
    by_page = defaultdict(list)
    for c in candidates:
        key = f"{c['doc_id']}_p{c['page']}"
        by_page[key].append(c)
    
    duplicate_groups = {}
    group_counter = 0
    
    for page_key, page_candidates in by_page.items():
        n = len(page_candidates)
        if n < 2:
            continue
        
        # Pre-compute token sets
        tokens = []
        for c in page_candidates:
            t_a = tokenize(c.get('text_a', ''))
            t_b = tokenize(c.get('text_b', ''))
            tokens.append(t_a | t_b)
        
        # Compare all pairs on same page
        for i in range(n):
            for j in range(i+1, n):
                ci = page_candidates[i]
                cj = page_candidates[j]
                
                # Check y-position proximity
                yi = ci.get('bbox_a', [0, 0])[1]
                yj = cj.get('bbox_a', [0, 0])[1]
                y_diff = abs(yi - yj)
                
                # Check text similarity
                sim = jaccard_similarity(tokens[i], tokens[j])
                
                if sim > 0.7 or (y_diff < 5 and sim > 0.5):
                    # Near-duplicate
                    cid_i = ci['case_id']
                    cid_j = cj['case_id']
                    
                    # Find or create group
                    found = False
                    for gid, members in duplicate_groups.items():
                        if cid_i in members or cid_j in members:
                            members.add(cid_i)
                            members.add(cid_j)
                            found = True
                            break
                    if not found:
                        group_counter += 1
                        duplicate_groups[f'dup_group_{group_counter}'] = {cid_i, cid_j}
    
    # Assign group IDs to candidates
    candidate_dup_group = {}
    for gid, members in duplicate_groups.items():
        for cid in members:
            candidate_dup_group[cid] = gid
    
    return candidate_dup_group, duplicate_groups


# ============================================================
# INDEPENDENCE GROUPING
# ============================================================

def assign_independence_groups(candidates: list) -> dict:
    """Assign independence group based on doc+page."""
    groups = {}
    page_counts = defaultdict(int)
    
    for c in candidates:
        key = f"{c['doc_id']}_p{c['page']}"
        groups[c['case_id']] = key
        page_counts[key] += 1
    
    return groups, dict(page_counts)


# ============================================================
# SELECTION LOGIC
# ============================================================

def select_potential_set(candidates: list, classifications: list,
                          independence_groups: dict, 
                          dup_groups: dict) -> tuple:
    """
    Select Potential Evaluation Candidate Set.
    
    Selection priority:
    1. Research-question alignment (HIGH > MEDIUM > UNKNOWN > LOW)
    2. Potential boundary / competing interpretation
    3. Cue relevance
    4. Evidence sufficiency
    5. Structural family coverage
    6. Document diversity
    7. Page diversity
    8. Near-duplicate reduction
    
    Keeps ~10% LOW cases as controls.
    Applies ≤3 per page independence constraint.
    """
    # Sort by priority (HIGH first, then MEDIUM, etc.)
    priority_order = {'HIGH': 0, 'MEDIUM': 1, 'UNKNOWN': 2, 'LOW': 3}
    
    indexed = []
    for i, c in enumerate(candidates):
        cls = classifications[i]
        indexed.append({
            'candidate': c,
            'classification': cls,
            'priority': priority_order.get(cls['evaluation_opportunity'], 4),
            'has_boundary': cls['potential_boundary'],
            'has_conflict': cls['potential_conflict'],
            'cue_relevance_val': {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2, 'UNKNOWN': 3}.get(cls['cue_relevance'], 4),
        })
    
    # Sort: priority → boundary → conflict → cue_relevance
    indexed.sort(key=lambda x: (
        x['priority'],
        not x['has_boundary'],
        not x['has_conflict'],
        x['cue_relevance_val'],
    ))
    
    # Select with independence constraints
    selected = []
    excluded = []
    page_selected_count = defaultdict(int)
    doc_selected_count = defaultdict(int)
    selected_dup_groups = set()
    
    # First pass: select HIGH and MEDIUM (non-trivial)
    for item in indexed:
        c = item['candidate']
        cls = item['classification']
        cid = c['case_id']
        page_key = independence_groups[cid]
        doc = c['doc_id']
        dup_group = dup_groups.get(cid)
        
        opp = cls['evaluation_opportunity']
        
        # Skip LOW for now (will add as controls later)
        if opp == 'LOW':
            excluded.append({
                'case_id': cid,
                'exclusion_reason': 'LOW_EVALUATION_VALUE',
                'structure_family': cls['structure_family'],
                'triviality': cls['triviality'],
            })
            continue
        
        # Independence check: ≤3 per page
        if page_selected_count[page_key] >= MAX_PER_PAGE:
            excluded.append({
                'case_id': cid,
                'exclusion_reason': 'PAGE_CONCENTRATION_LIMIT',
                'structure_family': cls['structure_family'],
                'triviality': cls['triviality'],
            })
            continue
        
        # Near-duplicate check: skip if group already has a representative
        if dup_group and dup_group in selected_dup_groups:
            excluded.append({
                'case_id': cid,
                'exclusion_reason': 'NEAR_DUPLICATE',
                'structure_family': cls['structure_family'],
                'triviality': cls['triviality'],
            })
            continue
        
        # Select
        selected.append(item)
        page_selected_count[page_key] += 1
        doc_selected_count[doc] += 1
        if dup_group:
            selected_dup_groups.add(dup_group)
    
    # Second pass: add control cases (LOW evaluation value, ~10%)
    target_controls = max(3, int(len(selected) * CONTROL_RATIO))
    controls_added = 0
    
    for item in indexed:
        if controls_added >= target_controls:
            break
        c = item['candidate']
        cls = item['classification']
        cid = c['case_id']
        page_key = independence_groups[cid]
        dup_group = dup_groups.get(cid)
        
        if cls['evaluation_opportunity'] != 'LOW':
            continue
        
        # Check independence
        if page_selected_count[page_key] >= MAX_PER_PAGE:
            continue
        if dup_group and dup_group in selected_dup_groups:
            continue
        
        # Remove from excluded, add to selected
        excluded = [e for e in excluded if e['case_id'] != cid]
        selected.append(item)
        page_selected_count[page_key] += 1
        doc_selected_count[c['doc_id']] += 1
        if dup_group:
            selected_dup_groups.add(dup_group)
        controls_added += 1
    
    # Document diversity check: flag if any doc > 35%
    total_selected = len(selected)
    doc_concentration = {}
    for doc, count in doc_selected_count.items():
        share = count / total_selected if total_selected > 0 else 0
        doc_concentration[doc] = {
            'count': count,
            'share': round(share, 3),
            'exceeds_limit': share > MAX_PER_DOC_PCT,
        }
    
    return selected, excluded, doc_concentration


# ============================================================
# MAIN
# ============================================================

def main():
    # === READ INPUT (READ-ONLY) ===
    print("=== DICE Potential Evaluation Candidate Set Construction ===\n")
    
    with open(INPUT_PATH, 'r') as f:
        input_data = json.load(f)
    
    candidates = input_data['ambiguous_cases']
    input_bytes = open(INPUT_PATH, 'rb').read()
    input_hash = hashlib.sha256(input_bytes).hexdigest()
    
    print(f"Input: {INPUT_PATH}")
    print(f"Candidate count: {len(candidates)}")
    print(f"Input SHA256: {input_hash[:32]}...")
    print(f"Input size: {len(input_bytes):,} bytes")
    
    assert len(candidates) == 545, f"Expected 545, got {len(candidates)}"
    
    # === CLASSIFY ALL 545 CANDIDATES ===
    print(f"\n--- Structural Classification ---")
    
    classifications = []
    for c in candidates:
        family = classify_structure(c)
        triviality = classify_triviality(c, family)
        eval_opp = assign_evaluation_opportunity(c, family, triviality)
        cue_rel = assign_cue_relevance(c, family, eval_opp)
        boundary = assign_potential_boundary(c, family)
        conflict = assign_potential_conflict(c)
        evidence = check_evidence_availability(c)
        ceiling = assess_ceiling_risk(family, eval_opp, triviality)
        
        classifications.append({
            'case_id': c['case_id'],
            'doc_id': c['doc_id'],
            'page': c['page'],
            'text_a': c['text_a'][:50],
            'text_b': c['text_b'][:50],
            'structure_family': family,
            'triviality': triviality,
            'evaluation_opportunity': eval_opp,
            'cue_relevance': cue_rel,
            'potential_boundary': boundary,
            'potential_conflict': conflict,
            'evidence_availability': evidence['overall'],
            'image_available': evidence['image_available'],
            'tld_available': evidence['tld_available'],
            'structural_evidence_available': evidence['structural_evidence_available'],
            'cue_available': evidence['cue_available'],
            'ceiling_risk': ceiling,
            'h_gap': c.get('h_gap', 0),
            'dy': c.get('dy', 0),
            'same_style': c.get('same_style', False),
            'line_obs_count': c.get('line_obs_count', 0),
        })
    
    # === STATISTICS ===
    print(f"\n--- Statistics ---")
    
    family_counts = Counter(c['structure_family'] for c in classifications)
    print(f"\nBy structure family:")
    for fam, cnt in sorted(family_counts.items(), key=lambda x: -x[1]):
        print(f"  {fam:25s} {cnt:4d} ({cnt/545*100:.0f}%)")
    
    opp_counts = Counter(c['evaluation_opportunity'] for c in classifications)
    print(f"\nBy evaluation opportunity:")
    for opp, cnt in sorted(opp_counts.items(), key=lambda x: -x[1]):
        print(f"  {opp:25s} {cnt:4d} ({cnt/545*100:.0f}%)")
    
    cue_counts = Counter(c['cue_relevance'] for c in classifications)
    print(f"\nBy cue relevance:")
    for cr, cnt in sorted(cue_counts.items(), key=lambda x: -x[1]):
        print(f"  {cr:25s} {cnt:4d} ({cnt/545*100:.0f}%)")
    
    evidence_counts = Counter(c['evidence_availability'] for c in classifications)
    print(f"\nBy evidence availability:")
    for ev, cnt in sorted(evidence_counts.items(), key=lambda x: -x[1]):
        print(f"  {ev:25s} {cnt:4d} ({cnt/545*100:.0f}%)")
    
    ceiling_counts = Counter(c['ceiling_risk'] for c in classifications)
    print(f"\nBy ceiling risk (pre-pilot, structural):")
    for cr, cnt in sorted(ceiling_counts.items(), key=lambda x: -x[1]):
        print(f"  {cr:25s} {cnt:4d} ({cnt/545*100:.0f}%)")
    
    boundary_count = sum(1 for c in classifications if c['potential_boundary'])
    conflict_count = sum(1 for c in classifications if c['potential_conflict'])
    print(f"\nPotential boundary: {boundary_count}/545")
    print(f"Potential conflict: {conflict_count}/545")
    
    # === NEAR-DUPLICATE DETECTION ===
    print(f"\n--- Near-Duplicate Detection ---")
    dup_groups_map, dup_groups = detect_near_duplicates(candidates)
    print(f"Near-duplicate groups: {len(dup_groups)}")
    print(f"Candidates in dup groups: {len(dup_groups_map)}")
    
    # === INDEPENDENCE GROUPING ===
    indep_groups, page_counts = assign_independence_groups(candidates)
    print(f"\n--- Independence ---")
    print(f"Unique doc+page: {len(page_counts)}")
    print(f"Pages with >10 candidates: {sum(1 for v in page_counts.values() if v > 10)}")
    
    # === SELECTION ===
    print(f"\n--- Selection ---")
    selected, excluded, doc_concentration = select_potential_set(
        candidates, classifications, indep_groups, dup_groups_map
    )
    
    print(f"Selected: {len(selected)}")
    print(f"Excluded: {len(excluded)}")
    print(f"Controls (LOW eval value kept): {sum(1 for s in selected if s['classification']['evaluation_opportunity'] == 'LOW')}")
    
    print(f"\nSelected by family:")
    sel_fam = Counter(s['classification']['structure_family'] for s in selected)
    for fam, cnt in sorted(sel_fam.items(), key=lambda x: -x[1]):
        print(f"  {fam:25s} {cnt:4d}")
    
    print(f"\nSelected by evaluation opportunity:")
    sel_opp = Counter(s['classification']['evaluation_opportunity'] for s in selected)
    for opp, cnt in sorted(sel_opp.items(), key=lambda x: -x[1]):
        print(f"  {opp:25s} {cnt:4d}")
    
    print(f"\nDocument concentration:")
    for doc, info in sorted(doc_concentration.items(), key=lambda x: -x[1]['count']):
        flag = ' ⚠️' if info['exceeds_limit'] else ''
        print(f"  {doc:25s} {info['count']:3d} ({info['share']*100:.0f}%){flag}")
    
    print(f"\nExcluded by reason:")
    exc_reasons = Counter(e['exclusion_reason'] for e in excluded)
    for reason, cnt in sorted(exc_reasons.items(), key=lambda x: -x[1]):
        print(f"  {reason:30s} {cnt:4d}")
    
    # === BUILD OUTPUT ===
    selected_list = []
    for s in selected:
        c = s['candidate']
        cls = s['classification']
        selected_list.append({
            'case_id': c['case_id'],
            'doc_id': c['doc_id'],
            'page': c['page'],
            'text_a': c['text_a'][:80],
            'text_b': c['text_b'][:80],
            'structure_family': cls['structure_family'],
            'triviality': cls['triviality'],
            'evaluation_opportunity': cls['evaluation_opportunity'],
            'cue_relevance': cls['cue_relevance'],
            'potential_boundary': cls['potential_boundary'],
            'potential_conflict': cls['potential_conflict'],
            'evidence_availability': cls['evidence_availability'],
            'image_available': cls['image_available'],
            'tld_available': cls['tld_available'],
            'structural_evidence_available': cls['structural_evidence_available'],
            'cue_available': cls['cue_available'],
            'ceiling_risk': cls['ceiling_risk'],
            'independence_group': indep_groups[c['case_id']],
            'near_duplicate_group': dup_groups_map.get(c['case_id'], None),
            'h_gap': cls['h_gap'],
            'dy': cls['dy'],
            'same_style': cls['same_style'],
            'line_obs_count': cls['line_obs_count'],
            'is_control': cls['evaluation_opportunity'] == 'LOW',
        })
    
    # Selection ledger (all 545)
    ledger = []
    for i, c in enumerate(candidates):
        cls = classifications[i]
        is_selected = any(s['candidate']['case_id'] == c['case_id'] for s in selected)
        exc = next((e for e in excluded if e['case_id'] == c['case_id']), None)
        ledger.append({
            'case_id': c['case_id'],
            'structure_family': cls['structure_family'],
            'evaluation_opportunity': cls['evaluation_opportunity'],
            'cue_relevance': cls['cue_relevance'],
            'potential_boundary': cls['potential_boundary'],
            'potential_conflict': cls['potential_conflict'],
            'evidence_availability': cls['evidence_availability'],
            'ceiling_risk': cls['ceiling_risk'],
            'independence_group': indep_groups[c['case_id']],
            'near_duplicate_group': dup_groups_map.get(c['case_id'], None),
            'selected': is_selected,
            'exclusion_reason': exc['exclusion_reason'] if exc else None,
            'is_control': is_selected and cls['evaluation_opportunity'] == 'LOW',
        })
    
    output = {
        'metadata': {
            'description': 'DICE Potential Evaluation Candidate Set',
            'type': 'RESEARCH TOOLING OUTPUT (not final evaluation set)',
            'construction_date': '2026-09-12',
            'input_file': INPUT_PATH,
            'input_candidate_count': len(candidates),
            'input_sha256': input_hash,
            'input_mutation': 0,
            'deterministic': True,
            'selection_principles': [
                'NO GT used for selection',
                'NO Human difficulty used for selection',
                'NO experiment results used for selection',
                'Structural classification only',
                'Research-question alignment filter',
                'Triviality / low-value exclusion (with control retention)',
                'Coverage construction',
                'Evidence availability recording',
                'Independence / diversity constraints',
                'Near-duplicate reduction',
            ],
            'independence_constraints': {
                'max_per_page': MAX_PER_PAGE,
                'max_per_doc_pct': MAX_PER_DOC_PCT,
                'control_ratio': CONTROL_RATIO,
            },
            'prohibited': [
                'GT-based selection',
                'Human difficulty assumption',
                'Experiment result leakage',
                'DICE Core modification',
                'Input file modification',
            ],
        },
        'statistics': {
            'total_candidates': len(candidates),
            'selected_count': len(selected),
            'excluded_count': len(excluded),
            'control_count': sum(1 for s in selected_list if s['is_control']),
            'by_structure_family': dict(family_counts),
            'by_evaluation_opportunity': dict(opp_counts),
            'by_cue_relevance': dict(cue_counts),
            'by_evidence_availability': dict(evidence_counts),
            'by_ceiling_risk': dict(ceiling_counts),
            'potential_boundary_count': boundary_count,
            'potential_conflict_count': conflict_count,
            'near_duplicate_groups': len(dup_groups),
            'unique_doc_page': len(page_counts),
            'selected_by_family': dict(sel_fam),
            'selected_by_opportunity': dict(sel_opp),
            'document_concentration': doc_concentration,
            'excluded_by_reason': dict(exc_reasons),
        },
        'selected_candidates': selected_list,
        'selection_ledger': ledger,
        'governance': {
            'IMPLEMENTATION_SCOPE': 'EVALUATION_RESEARCH_TOOLING_ONLY',
            'DICE_CORE_MODIFICATION': False,
            'FROZEN_BASELINE': 'INTACT',
            'FROZEN_EXPERIMENT': 'INTACT',
            'PRODUCTION': False,
            'RUNTIME_AUTHORITY': 'ZERO',
            'ITERATIVE_LEARNING': 'INSUFFICIENT_EVIDENCE',
            'FORMAL_HUMAN_EXPERIMENT': 'NOT_AUTHORIZED',
            'EVALUATION_SET_VALIDITY': 'NOT_YET_ESTABLISHED',
            'STOP': True,
        },
    }
    
    # Write output
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    output_hash = hashlib.sha256(open(OUTPUT_PATH, 'rb').read()).hexdigest()
    print(f"\n=== OUTPUT ===")
    print(f"Output: {OUTPUT_PATH}")
    print(f"Output SHA256: {output_hash[:32]}...")
    print(f"Output size: {os.path.getsize(OUTPUT_PATH):,} bytes")
    print(f"Selected: {len(selected)} candidates")
    
    # Verify input not modified
    input_hash_after = hashlib.sha256(open(INPUT_PATH, 'rb').read()).hexdigest()
    assert input_hash == input_hash_after, "INPUT WAS MODIFIED!"
    print(f"\nInput mutation check: PASS (hash unchanged)")
    
    return output


if __name__ == '__main__':
    main()
