# nf-test scaffold (roadmap item - not yet wired into CI)

[nf-test](https://www.nf-test.com/) is the standard unit/integration testing framework for
Nextflow pipelines (used by nf-core). This folder is a placeholder for that roadmap item so
you can learn it hands-on.

## Why add it

The Python tools in `bin/` are already unit-tested with pytest, but the **Nextflow processes
themselves** are not. nf-test lets you assert, per module, things like "given this BAM, the
caller emits a VCF with N variants" - without running the whole pipeline.

## Getting started (when you pick up this item)

1. Install nf-test: `curl -fsSL https://get.nf-test.com | bash`
2. Initialise: `nf-test init`
3. Generate a test for a module, e.g.:
   ```bash
   nf-test generate process modules/local/bcftools_stats.nf
   ```
4. Write assertions (see nf-core modules for examples), then run `nf-test test`.
5. Add an `nf-test` job to `.github/workflows/ci.yml`.

Example test file names live alongside as `*.nf.test`. Delete this README once the real
tests exist.
