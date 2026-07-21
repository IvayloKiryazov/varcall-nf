#!/usr/bin/env python3
"""Data-quality gate based on ``samtools stats`` output.

Extends the "SLO" idea from runtime to *data quality*: assert the alignment meets a minimum
mapped-read fraction, and fail the build if it doesn't. A cheap guard against silently
processing bad data.
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stats", type=Path, help="samtools stats output file")
    parser.add_argument("--min-mapped-rate", type=float, default=0.90)
    args = parser.parse_args()

    metrics = parse_samtools_stats(args.stats)
    total = metrics.get("raw total sequences", 0.0)
    mapped = metrics.get("reads mapped", 0.0)
    rate = (mapped / total) if total else 0.0

    print(f"Total reads:  {int(total)}")
    print(f"Mapped reads: {int(mapped)}")
    print(f"Mapped rate:  {rate:.4f} (threshold {args.min_mapped_rate})")

    if rate < args.min_mapped_rate:
        print("RESULT: FAIL - mapped rate below threshold")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
