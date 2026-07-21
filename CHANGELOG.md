# Changelog

## v0.2.0

Expanded into a "reproducible, tested, observable" learning pipeline.

- Second variant caller: `freebayes`, selectable via `--caller` (bcftools | freebayes).
- Observability: machine-readable Nextflow trace + `bin/pipeline_metrics.py` (per-step
  runtime/CPU/memory report with optional SLO gating) + DAG/timeline/report.
- Reproducibility: `bin/compare_vcfs.py` concordance/drift tool + a CI determinism job that
  runs the pipeline twice and asserts identical calls.
- Testing/quality: pytest suite for all Python tools + ruff linting, run as a CI job.
- CI expanded to three jobs: quality (lint+tests), pipeline correctness (caller matrix),
  reproducibility.
- Docs for learners: GLOSSARY, PIPELINE (design decisions), OBSERVABILITY, LEARNING_PATH
  (Coursera mapping), and a large tiered ROADMAP; CONTRIBUTING + nf-test scaffold.

## v0.1.0

Initial release.

- Nextflow DSL2 variant-calling pipeline: FastQC -> BWA-MEM -> samtools sort
  -> bcftools mpileup/call -> bcftools stats -> MultiQC.
- Self-contained tiny test dataset (20 kb reference, ~40x paired reads, 10 known SNPs)
  and a deterministic generator (`bin/generate_test_data.py`).
- Correctness check (`bin/check_variants.py`) that asserts the known SNPs are recovered.
- GitHub Actions CI that runs the full pipeline on the bundled data and validates the calls.
- One biocontainer per process (fully reproducible, no local tool installs).
