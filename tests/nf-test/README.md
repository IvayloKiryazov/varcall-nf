# nf-test scaffold (planned - not yet wired into CI)

[nf-test](https://www.nf-test.com/) is the standard unit/integration testing framework for
Nextflow pipelines (used by nf-core). This directory is a placeholder for that roadmap item.

## Motivation

The Python tools in `bin/` are unit-tested with pytest, but the **Nextflow processes**
themselves are not yet. nf-test allows per-module assertions (e.g. "given this BAM, the caller
emits a VCF with N variants") without running the whole pipeline.

## Getting started

1. Install nf-test: `curl -fsSL https://get.nf-test.com | bash`
2. Initialise: `nf-test init`
3. Generate a test for a module, e.g. `nf-test generate process modules/local/bcftools_stats.nf`
4. Add assertions (see nf-core modules for examples) and run `nf-test test`.
5. Add an `nf-test` job to `.github/workflows/ci.yml`.

Test files use the `*.nf.test` suffix.
