#!/usr/bin/env python3
"""Generate a tiny, self-contained variant-calling test dataset.

Creates a small reference genome, a "sample" genome derived from it with a set of
known SNPs, and paired-end reads simulated from the sample genome. Because the reads
come from the mutated sample but are aligned back to the unmutated reference, the
pipeline should recover exactly the SNPs listed in ``truth_snps.tsv``.

Deterministic (fixed seed) so the committed data and the expected variants never drift.
"""
from __future__ import annotations

import argparse
import gzip
import random
from pathlib import Path

BASES = "ACGT"


def random_sequence(rng: random.Random, length: int) -> list[str]:
    return [rng.choice(BASES) for _ in range(length)]


def reverse_complement(seq: str) -> str:
    comp = {"A": "T", "T": "A", "C": "G", "G": "C", "N": "N"}
    return "".join(comp[b] for b in reversed(seq))


def write_fasta(path: Path, name: str, sequence: str, width: int = 60) -> None:
    with path.open("w") as fh:
        fh.write(f">{name}\n")
        for i in range(0, len(sequence), width):
            fh.write(sequence[i : i + width] + "\n")


def write_fastq_gz(path: Path, records: list[tuple[str, str, str]]) -> None:
    with gzip.open(path, "wt") as fh:
        for read_id, seq, qual in records:
            fh.write(f"@{read_id}\n{seq}\n+\n{qual}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", default="assets/test_data", type=Path)
    parser.add_argument("--contig", default="testchr")
    parser.add_argument("--ref-length", default=20000, type=int)
    parser.add_argument("--read-length", default=100, type=int)
    parser.add_argument("--fragment-length", default=300, type=int)
    parser.add_argument("--coverage", default=40, type=int)
    parser.add_argument("--num-snps", default=10, type=int)
    parser.add_argument("--seed", default=42, type=int)
    args = parser.parse_args()

    rng = random.Random(args.seed)

    reference = random_sequence(rng, args.ref_length)
    sample = list(reference)

    # Introduce evenly spaced SNPs into the sample genome, away from the edges.
    margin = args.fragment_length
    spacing = (args.ref_length - 2 * margin) // (args.num_snps + 1)
    truth = []
    for i in range(1, args.num_snps + 1):
        pos = margin + i * spacing
        ref_base = reference[pos]
        alt_base = rng.choice([b for b in BASES if b != ref_base])
        sample[pos] = alt_base
        # 1-based position to match VCF/`truth_snps.tsv` convention.
        truth.append((args.contig, pos + 1, ref_base, alt_base))

    sample_seq = "".join(sample)

    num_fragments = args.coverage * args.ref_length // (2 * args.read_length)
    r1_records, r2_records = [], []
    qual = "I" * args.read_length  # Phred 40 across the board.
    max_start = args.ref_length - args.fragment_length
    for n in range(num_fragments):
        start = rng.randint(0, max_start)
        fragment = sample_seq[start : start + args.fragment_length]
        r1 = fragment[: args.read_length]
        r2 = reverse_complement(fragment[-args.read_length :])
        read_id = f"read{n}"
        r1_records.append((f"{read_id}/1", r1, qual))
        r2_records.append((f"{read_id}/2", r2, qual))

    outdir = args.outdir
    (outdir / "reference").mkdir(parents=True, exist_ok=True)
    (outdir / "reads").mkdir(parents=True, exist_ok=True)

    write_fasta(outdir / "reference" / "ref.fa", args.contig, "".join(reference))
    write_fastq_gz(outdir / "reads" / "sample1_R1.fastq.gz", r1_records)
    write_fastq_gz(outdir / "reads" / "sample1_R2.fastq.gz", r2_records)

    with (outdir / "truth_snps.tsv").open("w") as fh:
        fh.write("contig\tposition\tref\talt\n")
        for contig, pos, ref_base, alt_base in truth:
            fh.write(f"{contig}\t{pos}\t{ref_base}\t{alt_base}\n")

    print(f"Reference: {args.ref_length} bp ({args.contig})")
    print(f"Reads: {num_fragments} pairs @ ~{args.coverage}x, {args.read_length} bp")
    print(f"Known SNPs: {len(truth)} -> {outdir / 'truth_snps.tsv'}")


if __name__ == "__main__":
    main()
