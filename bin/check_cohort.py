#!/usr/bin/env python3
"""Validate a joint (cohort) VCF's per-sample genotypes.

For each sample, asserts that at *its* known private SNP positions it is genotyped with the
alternate allele, while the *other* samples are genotyped homozygous reference (0/0). That is
the defining behaviour of joint genotyping: every sample is genotyped at every cohort site.
"""
from __future__ import annotations

import argparse
import gzip
import sys
from pathlib import Path


def parse_truth(items: list[str]) -> dict[str, set[int]]:
    truth: dict[str, set[int]] = {}
    for item in items:
        name, path = item.split("=", 1)
        positions = set()
        for line in Path(path).read_text().splitlines()[1:]:
            positions.add(int(line.split("\t")[1]))
        truth[name] = positions
    return truth


def parse_cohort_vcf(path: Path) -> tuple[list[str], dict[int, dict[str, str]]]:
    """Return (sample_names, {pos: {sample: GT}})."""
    opener = gzip.open if str(path).endswith(".gz") else open
    samples: list[str] = []
    genotypes: dict[int, dict[str, str]] = {}
    with opener(path, "rt") as fh:
        for line in fh:
            if line.startswith("#CHROM"):
                samples = line.rstrip("\n").split("\t")[9:]
            elif not line.startswith("#"):
                f = line.rstrip("\n").split("\t")
                pos = int(f[1])
                gts = {}
                for name, col in zip(samples, f[9:]):
                    gts[name] = col.split(":")[0]
                genotypes[pos] = gts
    return samples, genotypes


def is_alt(gt: str) -> bool:
    return "1" in gt or any(c.isdigit() and c != "0" for c in gt.replace("|", "/").split("/"))


def is_ref(gt: str) -> bool:
    return gt in ("0/0", "0|0")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vcf", required=True, type=Path)
    parser.add_argument("--truth", action="append", required=True, metavar="NAME=PATH")
    args = parser.parse_args()

    truth = parse_truth(args.truth)
    samples, genotypes = parse_cohort_vcf(args.vcf)

    failures: list[str] = []
    for owner, positions in truth.items():
        if owner not in samples:
            failures.append(f"sample {owner} not in cohort VCF ({samples})")
            continue
        for pos in sorted(positions):
            gts = genotypes.get(pos)
            if gts is None:
                failures.append(f"{owner}: site {pos} missing from cohort VCF")
                continue
            if not is_alt(gts.get(owner, "./.")):
                failures.append(f"{owner}: not alt at own site {pos} (GT={gts.get(owner)})")
            for other in samples:
                if other != owner and not is_ref(gts.get(other, "./.")):
                    failures.append(
                        f"{other}: expected 0/0 at {owner}'s private site {pos}, "
                        f"got {gts.get(other)}"
                    )

    print(f"Samples: {samples}")
    print(f"Cohort sites: {len(genotypes)}")
    if failures:
        print("RESULT: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("RESULT: PASS - per-sample genotypes correct at all private sites")
    return 0


if __name__ == "__main__":
    sys.exit(main())
