#!/usr/bin/env python3
"""Turn a Nextflow execution trace into an SLO-style metrics report.

Applies the "make it observable" idea from software engineering to a genomics pipeline:
parse the machine-readable trace (``trace.raw = true``) and report per-step runtime, CPU,
and peak memory, plus optional SLO thresholds that can gate CI.

Learning note: this is deliberately the part that plays to a CI/CD + SLO background. The
biology lives in the pipeline; this is about treating a scientific workflow as a
production system you can measure and set budgets for.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# In raw mode Nextflow writes realtime in milliseconds and memory in bytes.
MS_PER_SECOND = 1000
BYTES_PER_MIB = 1024 * 1024


def _to_int(value: str) -> int:
    return 0 if value in ("-", "") else int(float(value))


def _to_float(value: str) -> float:
    return 0.0 if value in ("-", "") else float(value)


def parse_trace(path: Path) -> list[dict]:
    lines = path.read_text().splitlines()
    if not lines:
        return []
    header = lines[0].split("\t")
    rows = []
    for line in lines[1:]:
        if not line.strip():
            continue
        cells = line.split("\t")
        row = dict(zip(header, cells))
        rows.append(
            {
                "name": row.get("name", "?"),
                "status": row.get("status", "?"),
                "exit": row.get("exit", "-"),
                "realtime_s": _to_int(row.get("realtime", "0")) / MS_PER_SECOND,
                "pct_cpu": _to_float(row.get("%cpu", "0")),
                "peak_rss_mib": _to_int(row.get("peak_rss", "0")) / BYTES_PER_MIB,
                "peak_vmem_mib": _to_int(row.get("peak_vmem", "0")) / BYTES_PER_MIB,
            }
        )
    return rows


def build_report(rows: list[dict]) -> dict:
    total_realtime = sum(r["realtime_s"] for r in rows)
    peak_rss = max((r["peak_rss_mib"] for r in rows), default=0.0)
    return {
        "steps": sorted(rows, key=lambda r: r["realtime_s"], reverse=True),
        "total_realtime_s": round(total_realtime, 2),
        "max_peak_rss_mib": round(peak_rss, 1),
        "n_steps": len(rows),
    }


def to_markdown(report: dict) -> str:
    lines = [
        "## Pipeline metrics (SLO view)",
        "",
        f"- Steps: **{report['n_steps']}**",
        f"- Total step runtime: **{report['total_realtime_s']} s**",
        f"- Peak RSS across steps: **{report['max_peak_rss_mib']} MiB**",
        "",
        "| Step | Status | Runtime (s) | %CPU | Peak RSS (MiB) |",
        "|---|---|---:|---:|---:|",
    ]
    for step in report["steps"]:
        lines.append(
            f"| {step['name']} | {step['status']} | {step['realtime_s']:.1f} "
            f"| {step['pct_cpu']:.0f} | {step['peak_rss_mib']:.1f} |"
        )
    return "\n".join(lines) + "\n"


def check_slos(report: dict, max_step_s: float | None, max_rss_mib: float | None) -> list[str]:
    breaches = []
    for step in report["steps"]:
        if max_step_s is not None and step["realtime_s"] > max_step_s:
            breaches.append(
                f"{step['name']} runtime {step['realtime_s']:.1f}s > {max_step_s}s"
            )
        if max_rss_mib is not None and step["peak_rss_mib"] > max_rss_mib:
            breaches.append(
                f"{step['name']} peak RSS {step['peak_rss_mib']:.1f}MiB > {max_rss_mib}MiB"
            )
    return breaches


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", required=True, type=Path)
    parser.add_argument("--out-md", type=Path)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--max-step-seconds", type=float, default=None)
    parser.add_argument("--max-rss-mib", type=float, default=None)
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="Exit non-zero if any SLO threshold is breached.",
    )
    args = parser.parse_args()

    rows = parse_trace(args.trace)
    report = build_report(rows)
    markdown = to_markdown(report)

    sys.stdout.write(markdown)
    if args.out_md:
        args.out_md.write_text(markdown)
    if args.out_json:
        args.out_json.write_text(json.dumps(report, indent=2))

    breaches = check_slos(report, args.max_step_seconds, args.max_rss_mib)
    if breaches:
        print("\nSLO breaches:")
        for breach in breaches:
            print(f"  - {breach}")
        if args.enforce:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
