# Research Status

## Evidence Boundary Research

**Status: CONDITIONALLY_SUPPORTED**

The evidence boundary concept - the threshold between sufficient and insufficient evidence for a capability assertion - has been validated on a public arXiv corpus (IS-11 experiment, 45 cases). The boundary generalizes across document types but has not been validated on all document classes.

## G5 Boundary Generalization

**Status: CONDITIONALLY_SUPPORTED**

G5 (the highest boundary generalization grade) has been tested on arXiv-sourced cases. The generalization holds for structural features but has known failure modes on highly ambiguous text.

## Key Findings (from IS-11 Stage 4)

- FP = 1 (false positive rate is low)
- Recall = 0 (conservative - no false negatives)
- Coverage improved from 42.2% to 60.0% (+17.8 pp)
- All 8 newly-resolvable cases matched ground truth

## What is NOT implemented

- Automatic boundary detection (requires human specification)
- Automatic G5 detection (requires human review)
- Capability learning (capabilities are human-declared, not machine-learned)
- Capability expansion (future research direction)
- Production runtime (runtime authority = ZERO)

> This document summarizes publicly-safe research conclusions. Aggregate metrics are included; source corpus details are in the restricted archive.
