# Security policy

This is an open-source learning/portfolio project, not production clinical software.

## Reporting

If you find a security issue (e.g. a vulnerable dependency or an unsafe default), please open a
GitHub issue, or use GitHub's private "Report a vulnerability" flow for anything sensitive.

## What's in place

- Every container image is pinned by `@sha256` digest (see the modules).
- A weekly + on-demand **Trivy** scan (`.github/workflows/security-scan.yml`) checks the pinned
  images for HIGH/CRITICAL vulnerabilities.
- An **SBOM** (SPDX) is generated and attached to each tagged release.
- No secrets or credentials are stored in this repository; test data is small and synthetic,
  and real-data runs stream public data from ENA/NCBI.
