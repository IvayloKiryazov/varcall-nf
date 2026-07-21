# Observability & SLOs for a genomics pipeline

Most bioinformatics repos stop at "it produced a VCF." This project treats the pipeline like
a production system you can measure - which is the differentiating angle if you come from a
CI/CD + SLO background.

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

## Why this matters (interview-ready framing)

- **Cost & scale**: genomics steps vary wildly in runtime/memory; knowing the per-step profile
  is how you right-size resources and control cloud cost.
- **Regressions**: an SLO gate catches "this step got 3x slower/heavier" the same way you'd
  catch a latency regression in a service.
- **Transferable skill**: this is exactly the SLO/telemetry work described on the CV, applied
  to a scientific workflow.

## Learning extensions (see ROADMAP)

- Push metrics to a time-series store / Grafana instead of a Markdown table.
- Add **data-quality** SLOs (e.g. minimum mean coverage, maximum duplicate rate) alongside the
  runtime SLOs.
- Trend metrics across CI runs to detect drift over time.
