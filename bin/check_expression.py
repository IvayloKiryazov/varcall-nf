#!/usr/bin/env python3
"""Validate that Salmon recovered the known expression ranking.

Compares the estimated TPM in a Salmon ``quant.sf`` against the truth expression weights and
asserts the two orderings agree (Spearman rank correlation above a threshold). This is the
RNA-seq analogue of the DNA correctness check: it asserts the result is right, not just that
the tool ran.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def read_quant_tpm(path: Path) -> dict[str, float]:
    tpm: dict[str, float] = {}
    lines = path.read_text().splitlines()
    for line in lines[1:]:  # skip header: Name Length EffectiveLength TPM NumReads
        f = line.split("\t")
        tpm[f[0]] = float(f[3])
    return tpm


def read_truth(path: Path) -> dict[str, float]:
    truth: dict[str, float] = {}
    lines = path.read_text().splitlines()
    for line in lines[1:]:
        f = line.split("\t")
        truth[f[0]] = float(f[1])
    return truth


def ranks(values: list[float]) -> list[float]:
    """Average ranks (ties averaged)."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    result = [0.0] * len(values)
    i = 0
    while i < len(values):
        j = i
        while j + 1 < len(values) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            result[order[k]] = avg
        i = j + 1
    return result


def spearman(a: list[float], b: list[float]) -> float:
    ra, rb = ranks(a), ranks(b)
    n = len(a)
    d2 = sum((x - y) ** 2 for x, y in zip(ra, rb))
    return 1 - (6 * d2) / (n * (n * n - 1))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quant", required=True, type=Path)
    parser.add_argument("--truth", required=True, type=Path)
    parser.add_argument("--min-spearman", type=float, default=0.9)
    args = parser.parse_args()

    tpm = read_quant_tpm(args.quant)
    truth = read_truth(args.truth)
    names = [n for n in truth if n in tpm]
    if len(names) < 2:
        print("Not enough overlapping transcripts to compare")
        return 1

    rho = spearman([truth[n] for n in names], [tpm[n] for n in names])
    print(f"Transcripts compared: {len(names)}")
    print(f"Spearman(weight, TPM): {rho:.4f} (threshold {args.min_spearman})")
    for n in sorted(names, key=lambda x: truth[x], reverse=True):
        print(f"  {n}: weight={truth[n]:.0f} TPM={tpm[n]:.1f}")

    if rho < args.min_spearman:
        print("RESULT: FAIL - expression ranking not recovered")
        return 1
    print("RESULT: PASS - expression ranking recovered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
