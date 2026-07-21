# Roadmap

Planned enhancements for the pipeline, grouped by theme. The project intentionally keeps a
broad backlog spanning both engineering hardening and analysis capability. Each item notes
**what** it adds and **why** it matters.

Legend: `[x]` implemented · `[ ]` planned · (ENG) engineering/tooling · (BIO) analysis/science.

## Milestones

- **0.x (current)** - build breadth; each capability landed and green in CI.
- **1.0.0** - stability contract: real reads, multi-sample, digest-pinned reproducibility,
  nf-core-lint clean, stable documented params, first tagged release. Exit criteria and the
  full checklist live in [RELEASING.md](RELEASING.md).

---

## Implemented

- [x] (ENG) Nextflow DSL2 pipeline with one pinned biocontainer per step.
- [x] (ENG) Self-contained deterministic test dataset with known SNPs.
- [x] (ENG) Correctness gate in CI (`bin/check_variants.py`) - asserts recovered variants.
- [x] (ENG) Reproducibility gate (`bin/compare_vcfs.py`) - pipeline run twice, calls compared.
- [x] (ENG) Execution observability + SLO tooling (`bin/pipeline_metrics.py`).
- [x] (ENG) Unit/integration tests (pytest) + linting (ruff) in CI.
- [x] (ENG) Samplesheet pre-flight validation (`bin/validate_samplesheet.py`).
- [x] (ENG) Data-quality gate on alignment (`bin/check_qc.py`, mapped-rate threshold).
- [x] (ENG) Container-engine profiles: Docker, Singularity, Apptainer.
- [x] (BIO) Adapter/quality trimming (fastp).
- [x] (BIO) Duplicate marking (samtools markdup).
- [x] (BIO) Variant normalisation + soft filtering (bcftools norm / filter).
- [x] (BIO) Selectable variant caller (`--caller` bcftools | freebayes) with a caller matrix in CI.
- [x] (BIO) Aggregated QC reporting (FastQC + fastp + samtools stats + mosdepth + bcftools stats -> MultiQC).
- [x] (BIO) GATK HaplotypeCaller as a third `--caller` (with samtools dict).
- [x] (BIO) Coverage reporting (mosdepth) + mean-coverage data-quality gate.
- [x] (BIO) Run on a real reference (*E. coli* K-12) via `-profile test_full` (simulated reads).
- [x] (BIO) Variant annotation via SnpEff (`--annotate`, on the real-data path).
- [x] (ENG) Golden-VCF snapshot regression test in CI.
- [x] (ENG) Workflow linting (actionlint) in CI.
- [x] (ENG) On-demand integration workflow (`test_full.yml`) separate from gating CI.

## Analysis / science

- [ ] (BIO) Use real ENA/SRA reads (not simulated) on the real-data path.
- [ ] (BIO) Base-quality score recalibration (BQSR) for the GATK path.
- [ ] (BIO) VEP as an alternative annotator; compare to SnpEff.
- [ ] (BIO) DeepVariant as a `--caller`; compare a deep-learning caller to the rest.
- [x] (BIO) N-way caller concordance report (`bin/caller_concordance.py`).
- [ ] (BIO) Structural-variant calling (e.g. Manta/Delly) as an optional branch.
- [ ] (BIO) Coverage-vs-sensitivity mini-experiment (downsampling curve).

## Second assay: RNA-seq

- [ ] (BIO) RNA-seq path: STAR/HISAT2 spliced alignment or Salmon pseudo-alignment.
- [ ] (BIO) Gene-count matrix + normalisation (TPM/CPM).
- [ ] (BIO) Differential-expression step (DESeq2/edgeR in a Bioconductor container).
- [ ] (BIO) Batch-effect detection/correction and documentation.

## Engineering / reliability

- [ ] (ENG) nf-test module + pipeline tests wired into CI (scaffold in `tests/nf-test/`).
- [ ] (ENG) Multi-sample end-to-end support with a joint cross-sample report.
- [ ] (ENG) `conda` profile as an alternative to containers.
- [ ] (ENG) Container digest pinning (`@sha256:...`) for bit-for-bit reproducibility.
- [ ] (ENG) Data-quality SLOs beyond mapped-rate (mean coverage, duplicate rate).
- [ ] (ENG) Metrics export to Prometheus/Grafana instead of a Markdown summary.
- [ ] (ENG) Cross-run metric trending to detect performance drift.
- [ ] (ENG) `-resume`/caching demonstration and documentation.
- [ ] (ENG) Auto-generated architecture docs from the Nextflow DAG.

## Deployment / scale

- [ ] (ENG) Cloud batch executor profile (AWS Batch / Google Batch).
- [ ] (ENG) Cost/runtime comparison: local vs cloud for the same workload.
- [ ] (ENG) Package and lint as an nf-core-style pipeline (`nf-core lint`).
