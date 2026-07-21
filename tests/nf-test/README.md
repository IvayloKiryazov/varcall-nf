# nf-test module tests

[nf-test](https://www.nf-test.com/) tests for the Nextflow processes, complementing the pytest
suite that covers the Python tools in `bin/`.

## Run locally

```bash
# needs Nextflow (Java 17+), Docker, and nf-test
curl -fsSL https://get.nf-test.com | bash && sudo mv nf-test /usr/local/bin/
nf-test test --profile docker
```

## Layout

- `modules/*.nf.test` - per-process tests (currently `SAMTOOLS_FAIDX`, `BWA_INDEX`).
- Configuration lives in `../../nf-test.config`.

## Extend

Generate a starting point for another module and add assertions:

```bash
nf-test generate process modules/local/bcftools_stats.nf
```

See `.agents/skills/add-pipeline-module/SKILL.md` for the full workflow.
