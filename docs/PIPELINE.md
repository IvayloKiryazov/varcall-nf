# Pipeline design & rationale

What each step does and why it is included. (Terms are defined in [GLOSSARY.md](GLOSSARY.md).)

## Flow

```
FASTQ (paired reads)
   ├─► FastQC ─────────────────────────────────────────────┐  (raw read QC)
   └─► fastp (trim) ─► BWA-MEM ─► markdup ─► sorted BAM ─────┤
Reference FASTA                                              │
   ├─► BWA index (feeds BWA-MEM)                             ├─► samtools stats ─┐
   └─► samtools faidx (feeds caller/normalise)              │                    │
sorted BAM + reference ─► caller ─► bcftools norm ─► bcftools filter ─► VCF      │
      (bcftools mpileup+call | freebayes)                    │                   ├─► MultiQC
                                                             └─► bcftools stats ─┘
```

## Steps

1. **FastQC** - quality report on the raw reads (adapter content, per-base quality, etc.).
2. **fastp** (`--trim`) - adapter/quality trimming; emits its own QC report for MultiQC.
3. **BWA index / samtools faidx** - prepare the reference for alignment and calling.
4. **BWA-MEM** - align read pairs to the reference; attaches a read group (`@RG`).
5. **markdup** (`--mark_duplicates`) - name-sort, fixmate, coordinate-sort, then mark PCR/optical
   duplicates so they don't inflate allele support. Falls back to a plain sort when disabled.
6. **samtools stats** - alignment metrics, consumed by the data-quality gate and MultiQC.
7. **Variant calling** (`--caller`): `bcftools` (pileup-based) or `freebayes` (haplotype-based).
8. **bcftools norm** - left-align and normalise variants so callers are comparable.
9. **bcftools filter** (`--filter_expr`) - soft-filter low-quality/low-depth calls; produces the
   final published VCF.
10. **bcftools stats** - summary of the final call set.
11. **MultiQC** - aggregates all QC into one HTML report.

## Rationale

- **BWA-MEM**: standard short-read DNA aligner; fast and well documented. (RNA-seq needs a
  spliced aligner such as STAR/HISAT2 - tracked in the roadmap.)
- **bcftools as default caller**: minimal and deterministic, and needs no external
  "known-sites" resource, which suits a small reproducible demo. **freebayes** is included to
  show that changing the scientific method is a first-class, testable configuration change.
- **normalise + soft filter**: makes call sets from different callers comparable and encodes
  quality thresholds explicitly rather than implicitly.
- **One container per process**: every tool version is pinned, which underpins reproducibility
  and the CI story.
- **DSL2 per-step modules**: mirrors production pipeline structure (e.g. nf-core), so the
  patterns are transferable.

## Deliberate simplifications

This is a demonstration pipeline, not a clinical one. Base-quality recalibration, joint
genotyping, and annotation are intentionally left as roadmap items. See [ROADMAP.md](ROADMAP.md).
