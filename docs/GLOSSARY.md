# Glossary (plain language)

A quick reference for the biology terms used across this repository, aimed at readers with a
software background. Definitions are intentionally informal - approachable over exhaustive.

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

### Engineering terms, as applied here
- **Reproducibility** - re-running the pipeline gives the same results. Achieved via pinned
  tool versions (containers) and deterministic inputs. See `bin/compare_vcfs.py`.
- **Observability / SLO** - measuring runtime/CPU/memory per step and setting budgets. See
  `bin/pipeline_metrics.py` and [OBSERVABILITY.md](OBSERVABILITY.md).
- **Workflow manager (Nextflow)** - orchestrates the steps, handles parallelism, staging
  files between steps, containers, and resuming.

### Alleles, genotypes & ploidy
- **Allele** - one version of the sequence at a position (e.g. the `A` allele vs the `G`
  allele).
- **Reference vs alternate (REF/ALT)** - the allele in the reference vs the differing allele
  found in the sample.
- **Homozygous / heterozygous** - both chromosome copies carry the same allele (homo) vs two
  different alleles (het).
- **Ploidy** - how many copies of each chromosome an organism has (humans are diploid = 2).
- **Ts/Tv ratio** - transitions vs transversions; a quick sanity metric for a SNP call set.

### Alignment internals
- **CIGAR** - a compact string in SAM describing how a read aligns (matches, insertions,
  deletions, clips).
- **MAPQ** - mapping quality: how confident the aligner is about where a read went.
- **Insert size** - the length of the original DNA fragment between paired reads.
- **Pileup / mpileup** - stacking all reads over each position to see what bases they support;
  the basis of pileup-based calling.
- **PCR / optical duplicates** - artificial copies of the same fragment; marked so they don't
  falsely boost confidence in a variant.

### File formats & indexing
- **bgzip** - block-gzip compression that allows random access (used for `.vcf.gz`).
- **tabix / .tbi / .csi** - position indexes for bgzipped files so tools can seek quickly.
- **BED** - a simple format listing genomic regions (chrom, start, end); used to target
  analysis to specific intervals.
- **GFF / GTF** - annotation formats describing features (genes, exons) on a genome.
- **INFO / FORMAT (VCF)** - VCF columns: `INFO` holds site-level fields (e.g. depth `DP`);
  `FORMAT` holds per-sample fields (e.g. genotype `GT`).
- **Reference build / contig** - a specific version of a genome assembly; a `contig` is one
  named sequence within it (e.g. a chromosome).

### Processing concepts
- **Adapter trimming** - removing leftover sequencing-adapter bases from reads (fastp here).
- **Normalisation / left-alignment** - representing indels in a canonical position so callers
  can be compared (`bcftools norm`).
- **Filtering** - flagging/removing low-confidence calls by quality/depth (`bcftools filter`).
- **BQSR (base quality score recalibration)** - correcting systematic errors in per-base
  quality scores; a GATK best-practice step (roadmap).
- **Joint genotyping** - calling variants across many samples together for better accuracy
  (roadmap).
- **Annotation** - labelling variants with their likely biological effect and gene context
  (SnpEff/VEP; roadmap).

### RNA-seq terms (for the roadmap assay)
- **RNA-seq** - sequencing expressed RNA to measure gene activity (expression).
- **Spliced alignment** - RNA reads can skip introns, so aligners like STAR/HISAT2 handle gaps
  that DNA aligners don't.
- **Pseudo-alignment** - fast expression quantification (e.g. Salmon) without full alignment.
- **Counts / TPM / CPM** - ways of measuring/normalising how much each gene is expressed.
- **Differential expression** - finding genes whose expression differs between conditions
  (DESeq2/edgeR).
- **Batch effect** - unwanted technical variation (e.g. different sequencing runs) that can
  masquerade as biological signal and must be detected/corrected.

### Structural & larger variation
- **Indel** - insertion/deletion (already above); small-scale.
- **Structural variant (SV)** - larger rearrangements (large deletions, duplications,
  inversions, translocations); different callers (Manta/Delly) - roadmap.

### Ecosystem
- **biocontainer** - a community-maintained container image for a specific bioinformatics tool
  version; the basis of this pipeline's reproducibility.
- **nf-core** - a community collection of curated, standardised Nextflow pipelines and modules;
  the style this project mirrors.
- **nf-test** - the testing framework for Nextflow processes/workflows.
