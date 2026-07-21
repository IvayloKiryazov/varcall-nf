#!/usr/bin/env python3
"""Simulate paired-end reads from an existing reference FASTA.

Lets the pipeline run on a real reference genome (e.g. E. coli) without needing to host large
real read files: a region of the reference is copied, seeded with known SNPs, and sequenced
in silico. Deterministic given a seed, so results are reproducible.
"""
from __future__ import annotations

import argparse
import gzip
import random
from pathlib import Path

BASES = "ACGT"


def read_first_contig(path: Path) -> tuple[str, str]:
    name = "contig"
    seq: list[str] = []
    started = False
    for line in path.read_text().splitlines():
        if line.startswith(">"):
            if started:
                break
            name = line[1:].split()[0]
            started = True
        elif started:
            seq.append(line.strip())
    return name, "".join(seq).upper()


def reverse_complement(seq: str) -> str:
    comp = {"A": "T", "T": "A", "C": "G", "G": "C", "N": "N"}
    return "".join(comp.get(b, "N") for b in reversed(seq))


def write_fastq_gz(path: Path, records: list[tuple[str, str, str]]) -> None:
    with gzip.open(path, "wt") as fh:
        for read_id, seq, qual in records:
            fh.write(f"@{read_id}\n{seq}\n+\n{qual}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--sample", default="sim")
    parser.add_argument("--outdir", default=".", type=Path)
    parser.add_argument("--region-length", default=100000, type=int)
    parser.add_argument("--read-length", default=100, type=int)
    parser.add_argument("--fragment-length", default=300, type=int)
    parser.add_argument("--coverage", default=40, type=int)
    parser.add_argument("--num-snps", default=20, type=int)
    parser.add_argument("--seed", default=42, type=int)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    contig, full = read_first_contig(args.reference)

    # Keep only A/C/G/T so introduced SNPs are well defined; cap to region length.
    clean = "".join(b for b in full if b in BASES)
    region = clean[: args.region_length]
    if len(region) < 2 * args.fragment_length:
        raise SystemExit(f"Reference region too short ({len(region)} bp)")

    sample = list(region)
    margin = args.fragment_length
    spacing = (len(region) - 2 * margin) // (args.num_snps + 1)
    truth = []
    for i in range(1, args.num_snps + 1):
        pos = margin + i * spacing
        ref_base = region[pos]
        alt_base = rng.choice([b for b in BASES if b != ref_base])
        sample[pos] = alt_base
        truth.append((contig, pos + 1, ref_base, alt_base))
    sample_seq = "".join(sample)

    n_fragments = args.coverage * len(region) // (2 * args.read_length)
    qual = "I" * args.read_length
    r1, r2 = [], []
    max_start = len(region) - args.fragment_length
    for n in range(n_fragments):
        start = rng.randint(0, max_start)
        frag = sample_seq[start : start + args.fragment_length]
        r1.append((f"read{n}/1", frag[: args.read_length], qual))
        r2.append((f"read{n}/2", reverse_complement(frag[-args.read_length :]), qual))

    outdir = args.outdir
    outdir.mkdir(parents=True, exist_ok=True)
    write_fastq_gz(outdir / f"{args.sample}.sim_1.fastq.gz", r1)
    write_fastq_gz(outdir / f"{args.sample}.sim_2.fastq.gz", r2)
    with (outdir / f"{args.sample}.truth.tsv").open("w") as fh:
        fh.write("contig\tposition\tref\talt\n")
        for c, pos, ref_base, alt_base in truth:
            fh.write(f"{c}\t{pos}\t{ref_base}\t{alt_base}\n")

    print(f"Contig: {contig} (used {len(region)} bp)")
    print(f"Reads: {n_fragments} pairs @ ~{args.coverage}x; SNPs: {len(truth)}")


if __name__ == "__main__":
    main()
