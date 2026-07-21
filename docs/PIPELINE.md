# Pipeline design & decisions

This explains *what each step does* and *why it's there* - the part you should be able to
talk through in an interview. (Terms are defined in [GLOSSARY.md](GLOSSARY.md).)

## The flow

```
FASTQ (paired reads)
   │
   ├─► FastQC ─────────────────────────────┐   (read quality report)
   │                                         │
Reference FASTA                              │
   ├─► BWA index                            │
   ├─► samtools faidx                       │
   │                                         │
reads + index ─► BWA-MEM ─► samtools sort ─► BAM (sorted, indexed)
                                             │
BAM + reference ─► variant caller ──────────► VCF (.vcf.gz + .tbi)
   (bcftools mpileup+call  OR  freebayes)     │
                                             ├─► bcftools stats ─┐
                                             │                    ├─► MultiQC report
                                             └────────────────────┘
```

## Step-by-step

1. **FastQC** - quick quality report on the raw reads. In a real project you'd inspect this
   before trusting anything downstream (adapter contamination, quality drop-off, etc.).
2. **BWA index** - builds a searchable index of the reference so alignment is fast. Done once
   per reference.
3. **samtools faidx** - a lightweight `.fai` index of the reference FASTA; variant callers
   need it to random-access the reference.
4. **BWA-MEM** - aligns each read pair to the reference. We attach a read group (`@RG`) so the
   caller knows the sample. Output is SAM.
5. **samtools sort + index** - sorts alignments by genomic position and indexes them; nearly
   every downstream tool requires coordinate-sorted, indexed BAMs.
6. **Variant calling** (`--caller`):
   - **bcftools** (`mpileup | call -mv`) - pileup-based caller; fast and simple.
   - **freebayes** - haplotype-based Bayesian caller; different model, useful for comparison.
7. **bcftools stats** - summary numbers about the VCF (counts of SNPs/indels, Ts/Tv, ...).
8. **MultiQC** - rolls FastQC + bcftools stats into one shareable HTML report.

## Why these choices

- **BWA-MEM**: the de-facto standard for short-read DNA alignment; well documented and fast.
  *Learning task: understand why it isn't used for RNA-seq (spliced alignment) - see ROADMAP.*
- **bcftools as default caller**: minimal, deterministic, no reference "known-sites" needed,
  so it's ideal for a tiny reproducible demo. **freebayes** is included to show that swapping
  the scientific method is a first-class, testable change - not a rewrite.
- **One container per process**: every tool version is pinned to a biocontainer image. This is
  what makes the pipeline reproducible and is the backbone of the CI story.
- **Nextflow DSL2 with per-step modules**: mirrors how production pipelines (e.g. nf-core) are
  structured, so the patterns transfer to real jobs.

## Known simplifications (deliberate, documented)

This is a learning pipeline, not a clinical one. It intentionally skips several things a
production DNA pipeline would include - duplicate marking, base-quality recalibration,
variant filtering/annotation, joint genotyping. Each is a roadmap item so you can add it and
learn it. See [ROADMAP.md](ROADMAP.md).
