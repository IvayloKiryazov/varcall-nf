# Roadmap

A long, deliberately unfinished backlog so this repo grows with your learning. Items are
grouped into tiers. Each has **what**, **why it matters**, and **hints**. Check them off as
you go. Nothing here is "production pressure" - it's a learning ladder.

Legend: `[ ]` todo · `[x]` done · (E) plays to your engineering strength · (B) biology/stats
learning · (S) stretch.

---

## Tier 0 - already done (your starting baseline)

- [x] (E) Nextflow DSL2 pipeline: FASTQ -> QC -> align -> call -> stats -> MultiQC
- [x] (E) One pinned biocontainer per step (reproducible, no local installs)
- [x] (E) Self-contained deterministic test dataset with known SNPs
- [x] (E) Correctness check in CI (`bin/check_variants.py`) - asserts the biology, not just exit code
- [x] (E) Second caller (`freebayes`) selectable via `--caller`
- [x] (E) Execution observability + SLO tool (`bin/pipeline_metrics.py`)
- [x] (E) Reproducibility/drift comparator (`bin/compare_vcfs.py`) + determinism CI job
- [x] (E) Unit/integration tests (pytest) + linting (ruff) in CI

## Tier 1 - foundations to understand what you already have (B)

- [ ] (B) Open every output in `results/` and write one sentence per file explaining it.
- [ ] (B) Inspect a BAM: `samtools view results/alignments/sample1.sorted.bam | head`,
      then `samtools flagstat`. Understand what a SAM flag is.
- [ ] (B) Read the VCF by hand; map each line back to a SNP in `truth_snps.tsv`.
- [ ] (B) Run `--caller bcftools` and `--caller freebayes`, then compare with
      `bin/compare_vcfs.py`. Explain any differences in your own words.
- [ ] (B) Increase/decrease `--coverage` in the test-data generator and observe the effect on
      calls. Why does low coverage lose variants?

## Tier 2 - run it on real, public data (B, E)

- [ ] (B) Swap the toy reference for a small real one (e.g. *E. coli* K-12, ~4.6 Mb).
- [ ] (B) Pull a real small sample from **ENA/SRA** (e.g. an *E. coli* run) instead of
      simulated reads. Add a download step or document `wget`/`prefetch`.
- [ ] (E) Add an `nf-core/test-datasets`-style remote test profile (`-profile test_full`).
- [ ] (B) Add **adapter/quality trimming** (fastp or Trim Galore) before alignment; compare
      results with/without trimming.
- [ ] (S) Add a **downsampling** option and a mini experiment: calls vs coverage curve.

## Tier 3 - make the science better (B)

- [ ] (B) **Mark duplicates** (`samtools markdup` or Picard) and understand why PCR
      duplicates bias calls.
- [ ] (B) **Variant filtering** - add quality/depth filters (`bcftools filter`) and a
      documented rationale for thresholds.
- [ ] (B) **Left-align/normalize** variants (`bcftools norm`) so callers are comparable.
- [ ] (B) **Annotation** - add SnpEff or VEP to say what each variant *does* (gene, effect).
- [ ] (S) Add **GATK HaplotypeCaller** as a third `--caller` (learn BQSR + known-sites).
- [ ] (S) Add **DeepVariant** as a `--caller` and compare a deep-learning caller to the rest.
- [ ] (B) Three-way caller concordance report (bcftools vs freebayes vs GATK) using
      `compare_vcfs.py` extended to N-way.

## Tier 4 - a second assay: RNA-seq (B, S)

- [ ] (B) Add an RNA-seq path: **STAR** or **HISAT2** spliced alignment, or **Salmon**
      pseudo-alignment.
- [ ] (B) Produce a **gene-count matrix**; learn what normalization (TPM/CPM) means.
- [ ] (S) A tiny **differential-expression** step (DESeq2/edgeR in a Bioconductor container).
- [ ] (B) Learn and document what a **batch effect** is and how you'd detect/correct it.

## Tier 5 - engineering polish (E) - your wheelhouse, show it off

- [ ] (E) **nf-test** module + pipeline tests (scaffold in `tests/nf-test/`); wire into CI.
- [ ] (E) A **samplesheet validator** (schema + friendly errors) as a pre-flight step.
- [ ] (E) Multi-sample support end-to-end; a small **joint report** across samples.
- [ ] (E) `-profile conda` as an alternative to Docker; `-profile singularity` for HPC.
- [ ] (E) **Resume/caching** demo: document `-resume` and show a step being skipped.
- [ ] (E) Publish metrics to **Grafana/Prometheus** (or push a JSON to a gist) instead of the
      Markdown summary - reuse your SLO/telemetry experience.
- [ ] (E) Add **data-quality SLOs** (min mean coverage, max duplicate rate) that gate CI.
- [ ] (E) Trend metrics across CI runs to detect performance drift over time.
- [ ] (E) Container **digest pinning** (`@sha256:...`) for bit-for-bit reproducibility.
- [ ] (E) Add **DAG/architecture docs** auto-generated from the Nextflow DAG.

## Tier 6 - deployment & scale (S, E)

- [ ] (S) Run on a cloud batch backend (AWS Batch / Google Batch) via a Nextflow profile.
- [ ] (S) Cost/runtime comparison: local vs cloud for the same workload.
- [ ] (S) Package as an **nf-core-style** pipeline (lint with `nf-core lint`).

---

### How to work through this

1. Pick one item. Read the matching course section (see `docs/LEARNING_PATH.md`).
2. Implement it on a branch; open a PR to yourself.
3. In the PR description, explain the biology/stats **in your own words** (interview prep).
4. Keep CI green - correctness + reproducibility + quality gates should stay passing.
