#!/usr/bin/env python3
"""Validate an input samplesheet before the pipeline runs.

A small pre-flight check that catches common mistakes (wrong columns, duplicate sample
names, missing FASTQ files) early with a clear error message instead of a mid-run failure.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REQUIRED_COLUMNS = ["sample", "fastq_1", "fastq_2"]


def validate(path: Path, check_files: bool) -> list[str]:
    errors: list[str] = []
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            return [f"{path} is empty"]
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            return [f"Missing required column(s): {', '.join(missing)}"]

        seen: set[str] = set()
        row_count = 0
        for i, row in enumerate(reader, start=2):  # header is line 1
            row_count += 1
            sample = (row.get("sample") or "").strip()
            if not sample:
                errors.append(f"line {i}: empty 'sample'")
            elif sample in seen:
                errors.append(f"line {i}: duplicate sample '{sample}'")
            else:
                seen.add(sample)

            for col in ("fastq_1", "fastq_2"):
                value = (row.get(col) or "").strip()
                if not value:
                    errors.append(f"line {i}: empty '{col}'")
                elif check_files and not Path(value).is_file():
                    errors.append(f"line {i}: {col} not found: {value}")

        if row_count == 0:
            errors.append("samplesheet has a header but no data rows")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("samplesheet", type=Path)
    parser.add_argument(
        "--check-files",
        action="store_true",
        help="Also verify that each referenced FASTQ file exists.",
    )
    args = parser.parse_args()

    errors = validate(args.samplesheet, args.check_files)
    if errors:
        print(f"Samplesheet INVALID ({len(errors)} problem(s)):")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"Samplesheet OK: {args.samplesheet}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
