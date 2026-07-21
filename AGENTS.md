# Agent guide - varcall-nf

Guidance for AI coding agents (and humans) working in this repository. This is a public,
open-source **portfolio/learning** bioinformatics project: a reproducible, tested, observable
DNA variant-calling pipeline. There are no secrets here - keep it that way.

## What this repo is

A Nextflow (DSL2) pipeline that takes paired-end FASTQ to a filtered VCF plus a QC report, with
one pinned biocontainer per step, a self-contained test dataset, and CI that asserts the
results are biologically correct and reproducible.

## Repo map

- `main.nf` - workflow entry point; wires modules together.
- `modules/local/*.nf` - one process per file (FastQC, fastp, BWA, samtools, bcftools,
  freebayes, MultiQC). Each declares its own `container`.
- `nextflow.config` - params, profiles (docker/singularity/apptainer, test), and
  reporting/trace/observability config.
- `bin/*.py` - standalone Python tools (test-data generator, correctness/QC/reproducibility
  checks, samplesheet validator, metrics). All are unit-tested.
- `assets/test_data/` - the bundled tiny reference + reads + `truth_snps.tsv`.
- `tests/` - pytest suite (`test_tools.py`) and nf-test module tests (`nf-test/`).
- `docs/` - GLOSSARY, PIPELINE (design), OBSERVABILITY, LEARNING_PATH, ROADMAP, EXERCISES.
- `.github/workflows/ci.yml` - the CI gates.
- `.agents/skills/` - task recipes for extending the pipeline.

## The CI contract (keep all of these green)

1. **quality** - `ruff check bin tests`, `pytest`, and samplesheet validation.
2. **test** (matrix: bcftools, freebayes) - run the pipeline and assert known SNPs recovered
   (`bin/check_variants.py`) + alignment data-quality gate (`bin/check_qc.py`).
3. **reproducibility** - run the pipeline twice; assert identical calls (`bin/compare_vcfs.py`).
4. **nf-test** - Nextflow module tests.

Any change must keep these passing. If you add a step that changes outputs, update the checks.

## Conventions

- **One process per module file**, mirroring the existing siblings; always pin a `container`.
- Keep the per-sample channel contract consistent: reads are `tuple(sample, [r1, r2])`;
  BAMs are `tuple(sample, bam, bai)`; VCFs are `tuple(sample, vcf, tbi)`.
- The **final published VCF** is produced by `BCFTOOLS_FILTER` at `results/variants/<sample>.vcf.gz`.
- Python tools: standard library where possible; `argparse` CLIs; add a pytest test in
  `tests/test_tools.py`; keep `ruff` clean (config in `pyproject.toml`).
- Pin tool/container versions; prefer reproducibility over "latest".
- Do not add narrating comments or logging that wasn't asked for.

## How to extend

- New pipeline step -> follow `.agents/skills/add-pipeline-module/SKILL.md`.
- New variant caller -> follow `.agents/skills/add-variant-caller/SKILL.md`.
- Pick work from [`docs/ROADMAP.md`](docs/ROADMAP.md); each PR should include a short rationale.

## Safety

- This is a public repo. Never commit credentials, tokens, private data, or anything from
  another (e.g. employer) repository.
- Test data must remain small, synthetic, and license-clean.
- Container images come from public biocontainers only.

## Verifying locally

```bash
# Python tooling
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements-dev.txt
ruff check bin tests && pytest

# Pipeline (needs Nextflow + Docker)
nextflow run . -profile docker,test --outdir results
```
