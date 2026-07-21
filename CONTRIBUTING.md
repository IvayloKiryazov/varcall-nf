# Contributing

This is a portfolio project; the roadmap in [`docs/ROADMAP.md`](docs/ROADMAP.md) drives most
changes. Issues and pull requests are welcome.

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

- Every tool is pinned to a container; the pipeline does not rely on host-installed
  bioinformatics tools.
- New features should keep the CI gates green: **correctness** (known SNPs recovered),
  **reproducibility** (deterministic calls), **data quality** (alignment thresholds), and
  **quality** (ruff + pytest).
- Prefer adding a test over adding a comment.
- Pull requests that implement a roadmap item should include a short rationale for the
  analysis/design choices made.

## AI assistance

AI tools are used for boilerplate and unfamiliar syntax. Pipeline design and biological
interpretation are the author's own.
