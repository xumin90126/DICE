# Data Policy

## Principle

This repository contains **only**:
- Synthetic data (DOC-ALPHA, DOC-BETA, synthetic test figures)
- Public-domain data (arXiv paper renders, open-source reference code)
- Research methodology and conclusions (aggregate metrics, not raw enterprise data)

## What is excluded

| Category | Reason |
|---|---|
| Enterprise PDFs | Company-origin; no public authorization |
| Extracted enterprise text | Derived from proprietary documents |
| Enterprise annotation data | Contains company-specific identifiers |
| Internal API scripts | Contain live credentials, cookies |
| Memory/development logs | Internal context, PII, secrets |
| Employee PII | Personal information |
| Internal screenshots | Identifiable internal systems |

## Synthetic Replacement Plan

For experiments that originally used enterprise data, synthetic replacements are planned (not yet generated):
- `synthetic_pdf`: Mock datasheets (DOC-ALPHA/BETA template)
- `synthetic_table`: Fictional annotation case tables
- `synthetic_sop`: Generic document-slicing SOP
- `synthetic_g1g2g3g4g5_case`: Synthetic boundary-generalization cases

## Verification

Every file in this repository has passed:
1. Category-level audit (A/B/C/D/E classification)
2. File-level manifest (source_path, classification, risks)
3. Public Tree Safety Check (automated secret/path/PII/company scan)
