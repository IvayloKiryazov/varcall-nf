# Contributing / working notes

This is a personal **learning** project (not a commercial product). It's public so it can
double as a portfolio piece. Contributions/forks welcome, but the primary "contributor" is
future-me working through [docs/ROADMAP.md](docs/ROADMAP.md).

## Local setup

```bash
# Pipeline: needs Nextflow (Java 17+) and Docker
nextflow run . -profile docker,test --outdir results

# Python tooling: tests + linting
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
ruff check bin tests
pytest
```

## Conventions

- Keep every tool pinned to a container; never rely on host-installed bioinformatics tools.
- Every new pipeline feature should keep the three CI gates green: **correctness**
  (known SNPs recovered), **reproducibility** (determinism), **quality** (ruff + pytest).
- Prefer adding a small test over adding a comment.
- When you implement a roadmap item, write the biology explanation in your own words in the
  PR description (this is interview prep, not busywork).

## AI usage

AI-assisted implementation is used for boilerplate and syntax. Pipeline design and biological
interpretation are the author's own. See `docs/LEARNING_PATH.md` for the full stance.
