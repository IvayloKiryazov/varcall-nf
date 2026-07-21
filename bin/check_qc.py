#!/usr/bin/env python3
"""Data-quality gate for the alignment.

Extends the "SLO" idea from runtime to *data quality*: assert the alignment meets minimum
thresholds (mapped-read fraction from ``samtools stats`` and/or mean coverage from
``mosdepth``) and fail the build if it doesn't. A cheap guard against silently processing
bad data.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_samtools_stats(path: Path) -> dict[str, float]:
    metrics: dict[str, float] = {}
    for line in path.read_text().splitlines():
        if not line.startswith("SN\t"):
            continue
        _, key, value, *_ = line.split("\t")
        key = key.rstrip(":")
        try:
            metrics[key] = float(value)
        except ValueError:
            continue
    return metrics


def parse_mosdepth_mean(path: Path) -> float:
    """Return the genome-wide mean coverage from a mosdepth summary file."""
    for line in path.read_text().splitlines():
        fields = line.split("\t")
        if fields and fields[0] == "total":
            return float(fields[3])
    return 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stats", type=Path, help="samtools stats output file")
    parser.add_argument("--mosdepth-summary", type=Path, help="mosdepth summary file")
    parser.add_argument("--min-mapped-rate", type=float, default=0.90)
    parser.add_argument("--min-mean-coverage", type=float, default=0.0)
    args = parser.parse_args()

    failures: list[str] = []

    if args.stats:
        metrics = parse_samtools_stats(args.stats)
        total = metrics.get("raw total sequences", 0.0)
        mapped = metrics.get("reads mapped", 0.0)
        rate = (mapped / total) if total else 0.0
        print(f"Mapped rate:   {rate:.4f} (threshold {args.min_mapped_rate})")
        if rate < args.min_mapped_rate:
            failures.append("mapped rate below threshold")

    if args.mosdepth_summary:
        mean_cov = parse_mosdepth_mean(args.mosdepth_summary)
        print(f"Mean coverage: {mean_cov:.2f} (threshold {args.min_mean_coverage})")
        if mean_cov < args.min_mean_coverage:
            failures.append("mean coverage below threshold")

    if not args.stats and not args.mosdepth_summary:
        parser.error("provide --stats and/or --mosdepth-summary")

    if failures:
        print("RESULT: FAIL - " + "; ".join(failures))
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
