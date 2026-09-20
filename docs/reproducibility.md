# Reproducibility

## Overview

This repository is designed to be reproducible using **only public and synthetic data**. No enterprise data is required.

## Synthetic Corpus

The repository includes synthetic mock documents (DOC-ALPHA, DOC-BETA) generated with MuPDF. These serve as layout-structure demonstrations and can be used to test the perception pipeline.

## Public arXiv Corpus

Several experiments (IS-11, M-A, HVA, PH-02) use publicly available arXiv papers as the test corpus. If you wish to reproduce these experiments:

1. Download the referenced arXiv PDFs (verify each paper's license for redistribution).
2. Run the experiment scripts in `scripts/`.
3. Compare results with the reports in `research/`.

## What cannot be reproduced from this repository alone

- Experiments that originally used enterprise documents (DICE 2.0 generalization, Phase 52.1 human feedback). For these, **synthetic replacement data** is planned for a future phase. The research conclusions (aggregate metrics, methodology) are published; the source corpus is not.

> See docs/data-policy.md for details on what is and is not included.
