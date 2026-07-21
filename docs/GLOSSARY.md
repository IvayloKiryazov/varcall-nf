# Glossary (plain language)

If you're coming from software engineering and the biology words are new, start here. These
are intentionally informal - accuracy over jargon.

### Sequencing & data formats
- **DNA / genome** - the long string of letters A, C, G, T that encodes an organism. The
  "reference genome" is an agreed-upon representative version for a species.
- **Read** - one short fragment of sequence (here 100 letters) that a sequencing machine
  produced. A genome is reconstructed from millions of overlapping reads.
- **Paired-end reads** - the machine reads both ends of the same DNA fragment, giving two
  reads (`R1`, `R2`) a known distance apart. This extra info makes alignment more accurate.
- **FASTQ** - the text format for reads: for each read, an ID, the sequence, and a
  per-base quality score. Usually gzipped (`.fastq.gz`).
- **FASTA** - a simpler text format for sequences without qualities; used for the reference
  genome (`.fa`). A `.fai` file is just an index so tools can jump around it quickly.
- **Coverage / depth** - how many reads overlap a given position (e.g. "40x" means ~40
  reads cover each base on average). More coverage = more confidence in a call.

### Alignment
- **Alignment / mapping** - figuring out where each read came from in the reference genome.
- **BWA / BWA-MEM** - a popular aligner for DNA short reads. (STAR/HISAT2 are used for RNA.)
- **SAM / BAM** - the format storing alignments. SAM is text; BAM is the compressed binary
  version. We sort BAMs by position and index them (`.bai`) for fast access.
- **Read group (@RG)** - metadata tag saying which sample/library/platform a read came from;
  variant callers expect it.

### Variants
- **Variant** - a place where your sample's DNA differs from the reference.
- **SNP / SNV** - a single-letter difference (e.g. reference `A`, sample `G`). "SNP" implies
  it's a known/common one; "SNV" is the generic term.
- **Indel** - an insertion or deletion of one or more letters.
- **Variant calling** - the process of scanning alignments and deciding which differences
  are real variants (vs sequencing errors).
- **bcftools / freebayes / GATK / DeepVariant** - different variant callers, with different
  algorithms and trade-offs. This project ships bcftools and freebayes.
- **VCF** - the format listing called variants (position, ref allele, alt allele, quality,
  genotype...). Usually bgzipped (`.vcf.gz`) with a `.tbi` index.
- **Genotype (GT)** - whether the sample has the variant on one copy (heterozygous) or both
  copies (homozygous) of the chromosome.

### Quality & reporting
- **FastQC** - a tool that reports read quality metrics (per-base quality, GC content,
  adapter contamination...).
- **MultiQC** - aggregates many tool reports (FastQC, bcftools stats, ...) into one HTML page.
- **QC (quality control)** - checking the data/results are trustworthy before/while analyzing.

### Engineering terms you already know, applied here
- **Reproducibility** - re-running the pipeline gives the same results. Achieved via pinned
  tool versions (containers) and deterministic inputs. See `bin/compare_vcfs.py`.
- **Observability / SLO** - measuring runtime/CPU/memory per step and setting budgets. See
  `bin/pipeline_metrics.py` and [OBSERVABILITY.md](OBSERVABILITY.md).
- **Workflow manager (Nextflow)** - orchestrates the steps, handles parallelism, staging
  files between steps, containers, and resuming.
