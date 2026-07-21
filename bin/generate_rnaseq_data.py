#!/usr/bin/env python3
"""Generate a tiny, self-contained RNA-seq test dataset.

Creates a small "transcriptome" (a handful of transcripts) where each transcript is assigned a
known expression level, then simulates single-end reads in proportion to those levels. Because
the reads are drawn proportionally, a quantifier (Salmon) should estimate higher TPM for the
highly expressed transcripts - which is what ``check_expression.py`` asserts.

Deterministic (fixed seed) so the committed data and expected ranking never drift.
"""
from __future__ import annotations

import argparse
import gzip
import random
from pathlib import Path

BASES = "ACGT"


def random_sequence(rng: random.Random, length: int) -> str:
    return "".join(rng.choice(BASES) for _ in range(length))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", default="assets/rnaseq_test_data", type=Path)
    parser.add_argument("--num-transcripts", default=6, type=int)
    parser.add_argument("--transcript-length", default=1000, type=int)
    parser.add_argument("--read-length", default=75, type=int)
    parser.add_argument("--total-reads", default=30000, type=int)
    parser.add_argument("--seed", default=42, type=int)
    args = parser.parse_args()

    rng = random.Random(args.seed)

    # Expression weights: a clear gradient so ranking is unambiguous (16x down to 1x).
    weights = [2 ** (args.num_transcripts - 1 - i) for i in range(args.num_transcripts)]
    total_weight = sum(weights)

    transcripts = {
        f"tx{i+1}": random_sequence(rng, args.transcript_length)
        for i in range(args.num_transcripts)
    }
    names = list(transcripts)

    args.outdir.mkdir(parents=True, exist_ok=True)
    with (args.outdir / "transcriptome.fa").open("w") as fh:
        for name, seq in transcripts.items():
            fh.write(f">{name}\n")
            for j in range(0, len(seq), 60):
                fh.write(seq[j : j + 60] + "\n")

    qual = "I" * args.read_length
    max_start = args.transcript_length - args.read_length
    with gzip.open(args.outdir / "reads.fastq.gz", "wt") as fh:
        for n in range(args.total_reads):
            tx = rng.choices(names, weights=weights, k=1)[0]
            start = rng.randint(0, max_start)
            read = transcripts[tx][start : start + args.read_length]
            fh.write(f"@read{n}_{tx}\n{read}\n+\n{qual}\n")

    with (args.outdir / "truth_expression.tsv").open("w") as fh:
        fh.write("transcript\tweight\texpected_fraction\n")
        for name, w in zip(names, weights):
            fh.write(f"{name}\t{w}\t{w / total_weight:.4f}\n")

    print(f"Transcripts: {args.num_transcripts} x {args.transcript_length} bp")
    print(f"Reads: {args.total_reads} single-end @ {args.read_length} bp")
    print(f"Expression weights: {dict(zip(names, weights))}")


if __name__ == "__main__":
    main()
