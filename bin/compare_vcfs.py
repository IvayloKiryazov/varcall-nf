#!/usr/bin/env python3
"""Compare two VCFs for concordance - a reproducibility / drift check.

Two uses:
1. Determinism: run the pipeline twice and assert identical variant calls
   (``--require-identical``). Reproducibility is a known pain point in bioinformatics.
2. Method comparison: diff the calls from two callers (e.g. bcftools vs freebayes) to
   see where they agree and disagree.

Learning note: this mirrors a code-coverage/regression comparator - the same category of
tool applied to variant calls instead of code.
"""
from __future__ import annotations

import argparse
import gzip
import sys
from pathlib import Path


def read_sites(path: Path) -> set[tuple[str, int, str, str]]:
    opener = gzip.open if str(path).endswith(".gz") else open
    sites = set()
    with opener(path, "rt") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            fields = line.split("\t")
            chrom, pos, ref, alt = fields[0], int(fields[1]), fields[3], fields[4]
            sites.add((chrom, pos, ref, alt))
    return sites


def compare(a: set, b: set) -> dict:
    shared = a & b
    union = a | b
    return {
        "n_a": len(a),
        "n_b": len(b),
        "shared": len(shared),
        "only_in_a": sorted(a - b),
        "only_in_b": sorted(b - a),
        "concordance": (len(shared) / len(union)) if union else 1.0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vcf_a", type=Path)
    parser.add_argument("vcf_b", type=Path)
    parser.add_argument("--label-a", default="A")
    parser.add_argument("--label-b", default="B")
    parser.add_argument(
        "--require-identical",
        action="store_true",
        help="Exit non-zero unless the two call sets are identical.",
    )
    args = parser.parse_args()

    a = read_sites(args.vcf_a)
    b = read_sites(args.vcf_b)
    result = compare(a, b)

    print(f"{args.label_a}: {result['n_a']} variants")
    print(f"{args.label_b}: {result['n_b']} variants")
    print(f"Shared: {result['shared']}")
    print(f"Concordance (Jaccard): {result['concordance']:.4f}")

    for chrom, pos, ref, alt in result["only_in_a"]:
        print(f"  only in {args.label_a}: {chrom}:{pos} {ref}>{alt}")
    for chrom, pos, ref, alt in result["only_in_b"]:
        print(f"  only in {args.label_b}: {chrom}:{pos} {ref}>{alt}")

    identical = not result["only_in_a"] and not result["only_in_b"]
    if args.require_identical and not identical:
        print("RESULT: FAIL - call sets differ")
        return 1
    print(f"RESULT: {'IDENTICAL' if identical else 'DIFFERENT (not enforced)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
