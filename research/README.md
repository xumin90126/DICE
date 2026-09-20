# M-A Human Review Pilot Interface

## Overview

This is a controlled Human Validation interface for M-A Text-Drawing Association research.
It presents real PDF page images with highlighted text and drawing regions, allowing a
Human to make minimal Association Judgments (YES / NO / UNCERTAIN) without needing to
reconstruct page structure or understand the algorithm.

## Quick Start

```bash
cd tmp/m_a_human_review_pilot
python3 -m http.server 8765 --bind 127.0.0.1
```

Then open: http://127.0.0.1:8765/

## Human Task

> "Is this text associated with the highlighted drawing region?"

- **YES**: text is associated with the drawing
- **NO**: text is not associated with the drawing
- **UNCERTAIN**: cannot determine (boundary case)

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Y / 1 | YES |
| N / 2 | NO |
| U / 3 | UNCERTAIN |
| ← → | Navigate cases |
| S | Skip case |
| F | Toggle Full/Focus view |
| +/− | Zoom in/out |
| 0 | Reset zoom |

## Case Data

- 63 deduplicated candidates (FIG-prefix + near drawing extent)
- 8 Type A negatives (FIG-prefix, NOT near extent)
- 8 Type B negatives (near extent, NO FIG-prefix)
- Total: 79 cases
- 5 documents (med_001, resnet, efficientnet, cs_001, arxiv_2402)
- 41 unique page images rendered at 150 DPI

## Session Data

- Judgments stored in browser localStorage (append-only)
- Revisions preserved (original + revision timestamp)
- Export button downloads full session log as JSON
- No automatic Ground Truth generation
- No experiment result computation

## File Structure

```
tmp/m_a_human_review_pilot/
├── index.html              # Main interface
├── assets/
│   ├── style.css           # Stylesheet
│   └── app.js              # Application logic
├── pages/                  # Rendered PDF page images (41 PNGs)
├── data/
│   ├── candidates.json     # Human-facing case data (no internal metadata)
│   ├── candidates_internal.json  # Internal metadata (audit only, not served)
│   └── audit_results.json  # UI + Cognitive Load audit results
├── generate_data.py        # Data generation script
└── README.md               # This file
```

## Anti-Bias Design

- No semantic labels (caption, figure, chart, diagram) in UI
- No machine confidence/score/recommendation
- Neutral colors: YES=blue, NO=amber, UNCERTAIN=gray
- Equal-weight buttons (no pre-selection, no default YES)
- Fixed case order (no adaptive sampling)
- Internal metadata separated from human-facing data
