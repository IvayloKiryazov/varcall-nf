#!/usr/bin/env python3
"""N-way concordance across variant call sets.

Given several VCFs (e.g. from bcftools, freebayes, gatk), report how much they agree: how
many variants are shared by all callers, a pairwise Jaccard matrix, and how many are unique to
each caller. Useful for understanding where callers disagree - a common analysis step.
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
            f = line.split("\t")
            sites.add((f[0], int(f[1]), f[3], f[4]))
    return sites


def jaccard(a: set, b: set) -> float:
    union = a | b
    return (len(a & b) / len(union)) if union else 1.0


def parse_inputs(items: list[str]) -> dict[str, Path]:
    parsed: dict[str, Path] = {}
    for item in items:
        if "=" not in item:
            raise SystemExit(f"--vcf expects NAME=PATH, got: {item}")
        name, path = item.split("=", 1)
        parsed[name] = Path(path)
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--vcf",
        action="append",
        required=True,
        metavar="NAME=PATH",
        help="A named VCF, e.g. --vcf bcftools=a.vcf.gz (repeatable).",
    )
    parser.add_argument("--out-md", type=Path)
    args = parser.parse_args()

    inputs = parse_inputs(args.vcf)
    if len(inputs) < 2:
        parser.error("provide at least two --vcf entries")

    sites = {name: read_sites(path) for name, path in inputs.items()}
    names = list(sites)
    shared_all = set.intersection(*sites.values())
    union_all = set.union(*sites.values())

    lines = ["## Caller concordance", ""]
    lines.append(f"- Callers: {', '.join(names)}")
    lines.append(f"- Variants in union: {len(union_all)}")
    lines.append(f"- Shared by all: {len(shared_all)}")
    lines.append("")
    lines.append("| caller | total | unique |")
    lines.append("|---|---:|---:|")
    for name in names:
        others = set.union(*(sites[o] for o in names if o != name))
        unique = sites[name] - others
        lines.append(f"| {name} | {len(sites[name])} | {len(unique)} |")
    lines.append("")
    lines.append("Pairwise Jaccard:")
    lines.append("")
    lines.append("| | " + " | ".join(names) + " |")
    lines.append("|" + "---|" * (len(names) + 1))
    for a in names:
        row = [a] + [f"{jaccard(sites[a], sites[b]):.3f}" for b in names]
        lines.append("| " + " | ".join(row) + " |")

    report = "\n".join(lines) + "\n"
    sys.stdout.write(report)
    if args.out_md:
        args.out_md.write_text(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
