# Changelog

## v0.12.0

- Release workflow now generates and attaches an SPDX **SBOM**.
- Added `SECURITY.md` documenting the security posture (digest pinning, Trivy, SBOM, no secrets).

## v0.11.0

- Real-reads path: `-profile test_sra` streams a real E. coli run from ENA, downsampled with
  a new `SUBSAMPLE_READS` (seqtk) step (`--subsample N`); on-demand `test_sra.yml` workflow.

## v0.10.0

- CI: `pre-commit` hooks run as a CI job.
- CI: tag-triggered GitHub **Release** workflow (`release.yml`).
- CI: weekly + on-demand **Trivy** container vulnerability scan (`security-scan.yml`).

## v0.9.0

- Reproducibility: every container image is now pinned by `@sha256` digest.
- Reference handling generalised - gzipped/remote references are gunzipped via
  `PREPARE_REFERENCE`; samplesheet `fastq_*` entries may be local paths or URLs (enables
  real-data inputs). The default local-plain-FASTA path is unchanged.

## v0.8.0

- Developer ergonomics and repo polish: `Makefile`, `.pre-commit-config.yaml`, PR and issue
  templates, and `CITATION.cff`.
- Roadmap expanded with release/QA automation items (pre-commit CI, param schema, Trivy/SBOM,
  release automation, Zenodo DOI).

## v0.7.0

- Multi-sample support: the bundled dataset now has two samples (`sample1`, `sample2`) sharing
  one reference; CI asserts correctness and data-quality for every sample; MultiQC produces a
  joint report. `generate_test_data.py` gains `--sample`/`--ref-seed` (per-sample truth files).

## v0.6.0

- N-way caller concordance tool (`bin/caller_concordance.py`) + tests.
- Versioning policy and explicit path-to-v1.0 criteria (`docs/RELEASING.md`); milestones
  added to the roadmap.

## v0.5.0

More callers, coverage, real-data path, annotation, and QA automation.

- GATK HaplotypeCaller as `--caller gatk` (via samtools dict); added to the CI caller matrix.
- Coverage reporting with mosdepth -> MultiQC, plus a mean-coverage data-quality gate
  (`bin/check_qc.py` now handles samtools stats and/or mosdepth).
- On-demand real-data path: `-profile test_full` downloads the E. coli K-12 reference and
  simulates reads from it (`bin/simulate_reads_from_reference.py`, `PREPARE_REFERENCE`,
  `SIMULATE_READS`); manual `test_full.yml` workflow.
- Optional SnpEff annotation (`--annotate`).
- QA automation: golden-VCF snapshot regression test and actionlint workflow linting in CI.

## v0.4.0

Agentic-friendly tooling, expanded learning material, and Nextflow module tests.

- `AGENTS.md` guide + `.agents/skills/` (add-pipeline-module, add-variant-caller).
- nf-test module tests (`SAMTOOLS_FAIDX`, `BWA_INDEX`) + a dedicated CI job.
- Greatly expanded `docs/GLOSSARY.md` (alleles/genotypes, alignment internals, file formats,
  processing concepts, RNA-seq, structural variation, ecosystem).
- New `docs/EXERCISES.md` - progressive, hands-on study exercises.

## v0.3.0

Expanded analysis steps, more engineering gates, and public-facing documentation.

- Analysis: adapter/quality trimming (fastp), duplicate marking (samtools markdup), variant
  normalisation (bcftools norm) and soft filtering (bcftools filter); samtools stats added to
  the QC aggregation.
- Engineering: samplesheet pre-flight validation (`bin/validate_samplesheet.py`), alignment
  data-quality gate (`bin/check_qc.py`), and Singularity/Apptainer profiles.
- New params: `--trim`, `--mark_duplicates`, `--filter_expr`.
- CI: added samplesheet validation and a data-quality gate; expanded test coverage.
- Docs rewritten in a neutral, public-facing voice; roadmap reorganised by theme with a
  larger backlog.

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
