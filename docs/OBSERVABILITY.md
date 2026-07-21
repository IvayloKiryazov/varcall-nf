# Observability & SLOs for a genomics pipeline

Many bioinformatics pipelines stop at "it produced a VCF." This project additionally treats
the pipeline as a measurable production system: per-step performance is captured and can be
gated against budgets.

## What's wired up

- **Nextflow trace** (`nextflow.config`, `trace { raw = true }`) records, per step:
  status, exit code, wall-clock runtime, %CPU, and peak memory (RSS/VMEM).
- **`bin/pipeline_metrics.py`** parses that trace into:
  - a Markdown table (printed to the CI job summary), and
  - a JSON summary (uploaded as an artifact),
  plus optional **SLO thresholds** (`--max-step-seconds`, `--max-rss-mib`, `--enforce`) that
  can *fail the build* when a step blows its budget.
- **Nextflow report / timeline / DAG** HTML are published under `results/pipeline_info/`.

## Try it

```bash
nextflow run . -profile docker,test --outdir results
python3 bin/pipeline_metrics.py --trace results/pipeline_info/trace.txt
# with budgets:
python3 bin/pipeline_metrics.py --trace results/pipeline_info/trace.txt \
    --max-step-seconds 120 --max-rss-mib 2048 --enforce
```

## Why this matters

- **Cost & scale**: genomics steps vary widely in runtime/memory; a per-step profile is how
  resources are right-sized and cloud cost is controlled.
- **Regressions**: an SLO gate catches "this step got 3x slower/heavier" the same way a
  service latency regression would be caught.
- **Transferability**: the same SLO/telemetry approach used for production services, applied to
  a scientific workflow.

## Planned extensions (see ROADMAP)

- Push metrics to a time-series store / Grafana instead of a Markdown table.
- Add **data-quality** SLOs (e.g. minimum mean coverage, maximum duplicate rate) alongside the
  runtime SLOs.
- Trend metrics across CI runs to detect drift over time.
