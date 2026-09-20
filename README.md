# DICE — Evidence Intelligence Research

> **This repository is an ongoing research project.** It is not production-ready, not fully autonomous, and not a general-purpose system.

## What is DICE?

DICE (Document Intelligence Capability Engineering) is a research framework for transforming enterprise document information into trustworthy, reusable capabilities through an evidence-based, human-adjudicated governance pipeline.

Core concepts:
- **Evidence Boundary**: The boundary between sufficient and insufficient evidence for a capability assertion.
- **Capability Registry**: A declarative, frozen set of 22 extraction capabilities (e.g., temperature range, name-quantity pair, table cell segmentation).
- **Human Adjudication**: A human gate (YES/NO) validates every capability assertion before promotion.
- **Guardrails**: Deterministic assertions (G1-G4) that check numerical units, source attribution, critical missing values, and format compliance.

## Research Status

| Research Question | Status |
|---|---|
| Evidence Boundary | CONDITIONALLY_SUPPORTED |
| G5 Boundary | CONDITIONALLY_SUPPORTED |
| G5 Boundary Generalization | CONDITIONALLY_SUPPORTED |
| Automatic Boundary Detection | NOT_IMPLEMENTED |
| Automatic G5 Detection | NOT_IMPLEMENTED |
| Capability Learning | NOT_IMPLEMENTED |
| Capability Expansion | FUTURE_RESEARCH |
| Production Runtime | DISABLED |
| Runtime Authority | ZERO |

## Repository Structure

```
dice-public/
├── docs/              # Methodology, architecture, reproducibility, data policy
├── research/          # Research methodology, experiments, conclusions
├── src/               # Core code (dice package, perception, chunker, guardrails)
├── capabilities/      # 22 frozen capability declarations (declarative JSON)
├── assets/            # Frozen capability table, audit trace
├── tests/             # Test scripts
├── examples/          # Synthetic mock documents + public academic renders
├── scripts/           # Reproducibility scripts
└── .github/           # Issue templates, workflow skeletons
```

## Data Policy

This repository contains **only synthetic and public-domain data**. No enterprise data, proprietary documents, or personally identifiable information is included. See SECURITY.md and docs/data-policy.md.

## License

See LICENSE.

## Citation

See CITATION.cff.
