#!/usr/bin/env python3
"""Generate a tiny, self-contained variant-calling test dataset for one sample.

Creates a small reference genome (deterministic from ``--ref-seed`` so it is identical across
samples), a "sample" genome derived from it with a set of known SNPs, and paired-end reads
simulated from the sample genome. Because the reads come from the mutated sample but are
aligned back to the unmutated reference, the pipeline should recover exactly the SNPs listed
in ``truth_<sample>.tsv``.

Run once per sample (varying ``--sample`` and ``--seed``) to build a multi-sample dataset that
shares a single reference.
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
    parser.add_argument("--sample", default="sample1")
    parser.add_argument("--contig", default="testchr")
    parser.add_argument("--ref-length", default=20000, type=int)
    parser.add_argument("--read-length", default=100, type=int)
    parser.add_argument("--fragment-length", default=300, type=int)
    parser.add_argument("--coverage", default=40, type=int)
    parser.add_argument("--num-snps", default=10, type=int)
    parser.add_argument("--seed", default=42, type=int, help="Seed for this sample's SNPs/reads.")
    parser.add_argument("--ref-seed", default=1, type=int, help="Seed for the shared reference.")
    args = parser.parse_args()

    # Reference is deterministic from --ref-seed, so every sample shares the same reference.
    reference = random_sequence(random.Random(args.ref_seed), args.ref_length)

    rng = random.Random(args.seed)
    sample = list(reference)
    margin = args.fragment_length
    spacing = (args.ref_length - 2 * margin) // (args.num_snps + 1)
    truth = []
    for i in range(1, args.num_snps + 1):
        pos = margin + i * spacing
        ref_base = reference[pos]
        alt_base = rng.choice([b for b in BASES if b != ref_base])
        sample[pos] = alt_base
        truth.append((args.contig, pos + 1, ref_base, alt_base))
    sample_seq = "".join(sample)

    num_fragments = args.coverage * args.ref_length // (2 * args.read_length)
    r1_records, r2_records = [], []
    qual = "I" * args.read_length
    max_start = args.ref_length - args.fragment_length
    for n in range(num_fragments):
        start = rng.randint(0, max_start)
        fragment = sample_seq[start : start + args.fragment_length]
        read_id = f"{args.sample}_read{n}"
        r1_records.append((f"{read_id}/1", fragment[: args.read_length], qual))
        r2_records.append((f"{read_id}/2", reverse_complement(fragment[-args.read_length :]), qual))

    outdir = args.outdir
    (outdir / "reference").mkdir(parents=True, exist_ok=True)
    (outdir / "reads").mkdir(parents=True, exist_ok=True)

    write_fasta(outdir / "reference" / "ref.fa", args.contig, "".join(reference))
    write_fastq_gz(outdir / "reads" / f"{args.sample}_R1.fastq.gz", r1_records)
    write_fastq_gz(outdir / "reads" / f"{args.sample}_R2.fastq.gz", r2_records)

    with (outdir / f"truth_{args.sample}.tsv").open("w") as fh:
        fh.write("contig\tposition\tref\talt\n")
        for contig, pos, ref_base, alt_base in truth:
            fh.write(f"{contig}\t{pos}\t{ref_base}\t{alt_base}\n")

    print(f"Sample: {args.sample} (seed {args.seed})")
    print(f"Reference: {args.ref_length} bp ({args.contig}, ref-seed {args.ref_seed})")
    print(f"Reads: {num_fragments} pairs @ ~{args.coverage}x; known SNPs: {len(truth)}")


if __name__ == "__main__":
    main()
