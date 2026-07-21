#!/usr/bin/env python3
"""Validate that the pipeline recovered the known SNPs from the test dataset.

Compares the called VCF against ``truth_snps.tsv``. Exits non-zero if any truth SNP is
missing or has the wrong ALT allele, which is what lets CI assert the pipeline is
scientifically correct, not just that it ran.
"""
from __future__ import annotations

import argparse
import gzip
import sys
from pathlib import Path


def read_truth(path: Path) -> dict[int, tuple[str, str]]:
    truth: dict[int, tuple[str, str]] = {}
    with path.open() as fh:
        next(fh)  # header
        for line in fh:
            _contig, pos, ref, alt = line.rstrip("\n").split("\t")
            truth[int(pos)] = (ref, alt)
    return truth


def read_called_snvs(path: Path) -> dict[int, tuple[str, str]]:
    opener = gzip.open if path.suffix == ".gz" else open
    called: dict[int, tuple[str, str]] = {}
    with opener(path, "rt") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            fields = line.split("\t")
            pos, ref, alt = int(fields[1]), fields[3], fields[4]
            if len(ref) == 1 and len(alt) == 1:  # SNVs only
                called[pos] = (ref, alt)
    return called


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vcf", required=True, type=Path)
    parser.add_argument("--truth", required=True, type=Path)
    args = parser.parse_args()

    truth = read_truth(args.truth)
    called = read_called_snvs(args.vcf)

    missing, wrong = [], []
    for pos, (ref, alt) in sorted(truth.items()):
        if pos not in called:
            missing.append((pos, ref, alt))
        elif called[pos] != (ref, alt):
            wrong.append((pos, (ref, alt), called[pos]))

    found = len(truth) - len(missing) - len(wrong)
    print(f"Truth SNPs:     {len(truth)}")
    print(f"Correctly called: {found}")
    print(f"Total SNVs in VCF: {len(called)}")

    for pos, ref, alt in missing:
        print(f"  MISSING  {pos} {ref}>{alt}")
    for pos, expected, got in wrong:
        print(f"  WRONG    {pos} expected {expected[0]}>{expected[1]}, got {got[0]}>{got[1]}")

    if missing or wrong:
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS - all known SNPs recovered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
