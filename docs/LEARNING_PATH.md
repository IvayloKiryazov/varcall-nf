# Learning path

This project is a **learning vehicle**, not a product. The idea: pair a course with this repo
and turn each concept into a commit. You bring the engineering rigor (CI, tests, containers,
observability); the courses fill in the biology and stats.

## Suggested courses (Coursera unless noted)

1. **Genomic Data Science Specialization - Johns Hopkins** - most job-aligned: command-line
   genomics (samtools, bowtie/BWA), Python, Galaxy, Bioconductor, and biostatistics.
2. **Bioinformatics Specialization - UC San Diego (Pevzner)** - algorithmic foundations
   (assembly, alignment, sequence comparison); very CS-friendly.
3. **Statistics with Python - University of Michigan** (or JHU biostatistics) - close the
   stats gap; this is the most common weak spot for engineers pivoting in.
4. Free + Europe-relevant: **EMBL-EBI On-demand Training** (Ensembl, sequence analysis).

## Map: concept -> what to do in this repo

| Once you've learned... | Do this here |
|---|---|
| FASTQ, reads, quality scores | Read `docs/GLOSSARY.md`; open the FastQC report in `results/fastqc/` |
| Reference genomes, indexing | Understand `BWA_INDEX` / `SAMTOOLS_FAIDX`; try a real reference |
| Alignment (BWA-MEM) | Read `modules/local/bwa_mem.nf`; inspect a BAM with `samtools view` |
| SAM/BAM, sorting, flags | Explore `results/alignments/`; run `samtools flagstat` |
| Variant calling | Compare `--caller bcftools` vs `--caller freebayes` with `bin/compare_vcfs.py` |
| VCF format, genotypes | Open `results/variants/*.vcf.gz`; read `bcftools stats` output |
| QC aggregation | Open the MultiQC report in `results/multiqc/` |
| RNA-seq | Do the RNA-seq roadmap item (STAR/Salmon + counts) |
| Annotation, filtering | Do the SnpEff/VEP and filtering roadmap items |

## How to use AI honestly while learning

Being transparent about AI assistance is normal in 2026 and expected. The rule of thumb:

- **Fine to lean on AI**: Nextflow/Docker/CI boilerplate, argparse scaffolding, syntax you
  haven't learned yet (R/Bioconductor, etc.).
- **Do NOT outsource the understanding**: *why* BWA over another aligner, *what* a batch
  effect is and why you'd correct for it, *what* the caller is actually doing. That's the exact
  gap you're closing - if you can't explain a design choice in an interview, it hurts you.
- **State it plainly**: "AI-assisted implementation; pipeline design and biological
  interpretation are my own." Nobody blinks at that; not being able to explain a decision is
  what kills credibility.

For each roadmap item, write a short note in your own words (in the PR description or a
`docs/notes/` file) explaining the biology - that's your interview prep.
