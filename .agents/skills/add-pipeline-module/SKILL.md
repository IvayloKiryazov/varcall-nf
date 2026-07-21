---
name: add-pipeline-module
description: Add a new process/step to the varcall-nf Nextflow pipeline (a new module under modules/local, wired into main.nf, containerised, and covered by tests) while keeping all CI gates green. Use when adding a QC, alignment, post-processing, or reporting step.
---

# Add a pipeline module

Recipe for adding a new step to `varcall-nf` the same way the existing ones are built.

## 1. Create the module

Copy an existing sibling in `modules/local/` that has the closest input/output shape (e.g.
`samtools_stats.nf` for a BAM-in/report-out step). Each module must:

- declare `process NAME { ... }` with a `tag`,
- pin a public **biocontainer** via `container '...'`,
- `publishDir "${params.outdir}/<subdir>"` if it emits user-facing output,
- keep the channel contract: reads `tuple(sample, [r1, r2])`, BAM `tuple(sample, bam, bai)`,
  VCF `tuple(sample, vcf, tbi)`,
- put results on named `emit:` outputs.

## 2. Wire it into `main.nf`

- `include { NAME } from './modules/local/name.nf'` at the top.
- Call it in the `workflow {}` block, feeding it the right upstream channel.
- If it is optional, gate it on a new `params.<flag>` with an `if/else` (see `params.trim` and
  `params.mark_duplicates` for the pattern), and default the flag in `nextflow.config`.
- If it produces QC, `.mix()` it into `ch_reports` so MultiQC picks it up.

## 3. Verify the tool command first (recommended)

Before trusting Nextflow, run the raw command through the container with Docker on the bundled
test data to confirm it works and produces the expected output.

## 4. Add tests

- If it emits a file from simple inputs, add an nf-test under `tests/nf-test/modules/`.
- If it ships a companion Python tool in `bin/`, add a pytest case in `tests/test_tools.py`.

## 5. Keep CI green

Run `ruff check bin tests && pytest` locally, and confirm the pipeline still recovers the known
SNPs. Update `bin/check_variants.py` / `bin/check_qc.py` expectations only if outputs
legitimately change. Note the change in `CHANGELOG.md` and, if relevant, `docs/PIPELINE.md`.
