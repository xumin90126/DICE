# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this repository, please report it privately. Do not open a public issue.

## Data Safety

This repository is built from a read-only audit of a private research environment. Every file included in this public tree has passed:

1. **Classification audit** (DICE_PUBLIC_RELEASE_AUDIT_v1)
2. **File-level manifest** (DICE_PUBLIC_RELEASE_MANIFEST_v1)
3. **Public Tree Safety Check** (automated scan for secrets, internal paths, company data, PII)

### What is excluded

- API keys, tokens, session cookies, passwords, credentials
- Enterprise PDFs, SOPs, internal documents
- Employee PII (names, phones, emails, photos)
- Internal URLs, IPs, filesystem paths
- Memory logs, development logs
- Any file with company-specific identifiers

If you believe any restricted content has been inadvertently included, please report it immediately for removal.

## Scope

This is a **research** repository. It is not a production system. The runtime has **ZERO authority** - it cannot make decisions, execute actions, or modify state autonomously.
