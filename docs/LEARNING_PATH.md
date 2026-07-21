# Background & references

This project pairs software-engineering practice (reproducibility, testing, CI/CD,
observability) with genomics analysis. This page lists the domain references it draws on and
records how the two areas map onto the codebase.

## Domain references

- **Genomic Data Science Specialization - Johns Hopkins** - command-line genomics (samtools,
  aligners), Python, Galaxy, Bioconductor, and biostatistics.
- **Bioinformatics Specialization - UC San Diego** - algorithmic foundations (assembly,
  alignment, sequence comparison).
- **Statistics with Python - University of Michigan** - statistical grounding for analysis.
- **EMBL-EBI On-demand Training** - Ensembl and sequence-analysis material.

## Concept-to-code map

| Concept | Where it appears in this repo |
|---|---|
| FASTQ, reads, quality scores | `docs/GLOSSARY.md`; FastQC / fastp reports under `results/` |
| Reference indexing | `modules/local/bwa_index.nf`, `samtools_faidx.nf` |
| Alignment | `modules/local/bwa_mem.nf`; BAMs under `results/alignments/` |
| Duplicate marking | `modules/local/markdup.nf` |
| Variant calling | `modules/local/bcftools_call.nf`, `freebayes.nf` (`--caller`) |
| Normalisation & filtering | `modules/local/bcftools_norm.nf`, `bcftools_filter.nf` |
| QC aggregation | `modules/local/multiqc.nf`; `results/multiqc/` |
| Caller comparison | `bin/compare_vcfs.py` |
| Observability / SLOs | `bin/pipeline_metrics.py`; `docs/OBSERVABILITY.md` |

## AI assistance policy

AI tools assist with boilerplate and unfamiliar syntax (Nextflow/Docker/CI configuration,
argparse scaffolding). Pipeline design decisions and biological interpretation are the
author's own. Each roadmap item is accompanied by a short rationale in its pull request
describing the analysis choices made.
