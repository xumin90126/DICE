# Architecture

## DICE Capability OS

DICE is a **Capability Operating System** (not an Agent, not a Skill). It provides:

- **8-layer governance**: from evidence observation to capability promotion
- **22 frozen capabilities**: declarative extraction contracts (e.g., CAP-TEMP-RANGE, CAP-NAME-QTY-PAIR)
- **Human adjudication**: a YES/NO gate validates every assertion
- **Zero runtime authority**: the system recommends; humans decide

## Key Components

| Component | Role |
|---|---|
| Perception (P1-P7) | Atomic observation, geometry, style, region, reading order, structure |
| Evidence Store | Match evidence, observer, validator, proposal generator |
| Runtime | Execution, promotion, ranking adaptation, matching, comparison |
| Capability Registry | 22 declarative capability packages (contract + boundary + evidence) |
| Guardrails | G1 (numerical units), G2 (source attribution), G3 (critical missing values), G4 (format compliance) |
| Human Gate | YES/NO adjudication interface |

## Frozen Baseline

The 22-capability frozen baseline is **intact**. Capability definitions are declarative (PROPOSED status, empty evidence state). No capability has been promoted to ACTIVE without human approval.

> This document is a skeleton. Additional architecture details will be added as research is formalized.
