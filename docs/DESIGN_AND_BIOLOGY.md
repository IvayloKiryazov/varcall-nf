# Design decisions & biology rationale

A deeper companion to [PIPELINE.md](PIPELINE.md). For each step it explains **the biological
question**, **why the step exists**, **why this tool/choice**, and **what can go wrong**. The
aim is that every design decision here is understandable and defensible on its own terms.
Terms are defined in [GLOSSARY.md](GLOSSARY.md).

---

## Part 1 - DNA variant calling

### The question
"Where does this sample's genome differ from a reference genome, and can we trust each
difference?" Those differences (variants) are the raw material for genetics: disease alleles,
strain typing, evolution, etc.

### 1. Read QC (FastQC)
- **Why:** sequencing is imperfect. Before drawing conclusions you check base quality, GC
  content, adapter contamination, and duplication. Garbage in, garbage out.
- **What can go wrong:** quality that collapses toward read ends, adapter read-through on short
  fragments, or unexpected GC (contamination). Ignoring these biases downstream calls.

### 2. Adapter/quality trimming (fastp)
- **Why:** adapters are synthetic sequence ligated during library prep; if the DNA fragment is
  shorter than the read, the read runs into the adapter. Aligning adapter bases causes
  mismatches and mis-mapping. Trimming also removes low-quality tails.
- **Choice:** fastp is fast, does adapter detection + quality trimming in one pass, and emits a
  QC report. **Trade-off:** over-aggressive trimming shortens reads and can reduce mappability;
  defaults are conservative.

### 3. Alignment (BWA-MEM) + reference indexing
- **Why:** to call variants you must know where each read came from on the reference. Alignment
  places reads and records mismatches (candidate variants).
- **Choice:** BWA-MEM is the standard for short-read **DNA**. It does *not* allow large gaps,
  which is correct for DNA but **wrong for RNA** (RNA reads span introns - hence a different
  aligner in Part 2). The reference is indexed once so alignment is fast.
- **Read groups (@RG):** tag reads with their sample/library/platform; callers use this to know
  which sample a read belongs to. Omitting it breaks GATK.
- **What can go wrong:** low mapping rate (wrong reference, contamination), or multi-mapping in
  repetitive regions (low MAPQ) producing false variants.

### 4. Duplicate marking (samtools markdup)
- **Why:** PCR amplification during library prep can copy the same original fragment many
  times. Those copies are not independent evidence, so if you count them you can *falsely* gain
  confidence in an error. Marking (not removing) lets callers ignore them.
- **Mechanics:** name-sort -> `fixmate` (fill in mate coordinates) -> coordinate-sort ->
  `markdup` (flag reads that share start/end as duplicates). bcftools mpileup then skips them.
- **What can go wrong:** optical/PCR duplicates inflate allele support; without marking, a
  sequencing error copied many times can look like a real heterozygous variant.

### 5. Coverage & alignment QC (mosdepth, samtools stats)
- **Why:** confidence in a variant scales with depth. Low mean coverage or low mapped-rate is a
  red flag that the whole callset is unreliable. This is where the pipeline's **data-quality
  gate** lives (a minimum mapped-rate and mean coverage).
- **Interpretation:** `mosdepth` mean coverage ~= average reads per base; `samtools stats`
  "reads mapped" / "raw total sequences" = mapped fraction.

### 6. Variant calling (bcftools / freebayes / gatk)
- **Why:** at each position, decide whether the pile of aligned bases represents a real variant
  or just sequencing noise, and infer the genotype.
- **The three callers (why offer a choice):**
  - **bcftools** (`mpileup | call`): pileup/likelihood based; fast, minimal, deterministic, no
    external resources. Great default and for reproducibility demos.
  - **freebayes:** haplotype-based Bayesian caller; considers combinations of nearby variants;
    a different model, useful to cross-check.
  - **GATK HaplotypeCaller:** local *de novo* re-assembly around active regions; the clinical
    standard, more sophisticated (and heavier). Needs a sequence dictionary.
- **Why it matters:** callers disagree at hard sites (indels, low complexity). The
  `caller_concordance.py` tool quantifies agreement - understanding *why* they differ is real
  bioinformatics.

### 7. Normalisation (bcftools norm)
- **Why:** the same indel can be written multiple ways (different position/representation).
  Normalisation left-aligns and standardises representation so variants are comparable across
  callers and against databases. For SNPs it's a no-op; for indels it's essential.

### 8. Filtering (bcftools filter)
- **Why:** callers emit low-confidence calls. Soft-filtering by quality (`QUAL`) and depth
  (`DP`) removes likely false positives. Thresholds are a **precision/recall trade-off**:
  stricter = fewer false positives but more missed true variants.
- **Honesty:** the default `QUAL<20 || INFO/DP<10` is a reasonable demo threshold, not a
  clinically validated one.

### 9. Annotation (custom SnpEff database)
- **Why:** a position + allele means little until you know *what it does* - which gene, and
  whether it changes a protein (missense/synonymous/nonsense), etc.
- **The subtle part:** SnpEff needs a database whose **contig names match the VCF**. Public
  prebuilt DBs often use different accessions (e.g. `U00096.3` vs `NC_000913.3`) than your
  reference, so annotation silently annotates nothing. This pipeline sidesteps that by
  **building a custom DB from the exact reference + its GFF**, guaranteeing matching contigs.

### Reading a VCF (what the columns mean)
`CHROM POS ID REF ALT QUAL FILTER INFO FORMAT <sample>`: position, reference vs alternate
allele, a quality score, filter status, site-level `INFO` (e.g. `DP` depth), and per-sample
`FORMAT` (e.g. `GT` genotype: `0/1` heterozygous, `1/1` homozygous-alt).

### Joint (cohort) genotyping - the industry-standard multi-sample workflow
Calling each sample independently and merging VCFs is weak: if sample B has no variant at a
site, an independent call simply omits it, so you can't tell "reference" from "not sequenced".
The **GATK Best-Practices** cohort workflow fixes this:
1. **HaplotypeCaller in GVCF mode** (`-ERC GVCF`) per sample - emits a record for *every*
   position (variant or not) with the evidence for the reference allele.
2. **CombineGVCFs** merges the per-sample GVCFs.
3. **GenotypeGVCFs** jointly genotypes all samples at all sites.
The payoff: at a variant private to sample A, sample B gets a confident `0/0` (reference) call
backed by its own read evidence, rather than a missing entry. This project demonstrates it in
`cohort.nf` and asserts the per-sample genotypes with `bin/check_cohort.py` (owner alt, others
`0/0`). Real cohorts scale this with GenomicsDBImport and add variant-quality recalibration
(VQSR) - natural next steps.

---

## Part 2 - RNA-seq quantification

### The question
"How much is each gene/transcript expressed?" Instead of *where does the sequence differ*, RNA
-seq asks *how much RNA of each type is present* - a proxy for gene activity.

### Why a different toolchain than DNA
- RNA is transcribed from genes and **spliced** (introns removed). A read can span an
  exon-exon junction, so a genome aligner like BWA-MEM (no large gaps) is wrong. Options:
  spliced genome aligners (STAR/HISAT2) or **transcriptome quantifiers**.
- **Choice here - Salmon (pseudo-alignment):** instead of full base-by-base alignment, Salmon
  matches reads to the *transcriptome* and models which transcript each read most likely came
  from. It's fast, accurate for quantification, and avoids the spliced-alignment complexity -
  ideal for a small, reproducible demo.

### The steps
1. **`salmon index`** builds a k-mer index of the transcriptome (the set of transcript
   sequences).
2. **`salmon quant`** assigns reads to transcripts (probabilistically, resolving reads that
   could come from several similar transcripts) and outputs `quant.sf` with **TPM** and
   estimated read counts per transcript.

### TPM (what the number means)
**Transcripts Per Million** normalises for two biases: transcript **length** (longer
transcripts collect more reads) and **sequencing depth** (bigger libraries have more reads).
TPMs sum to 1,000,000, so they express *relative* abundance and are comparable across samples.

### The correctness check
The bundled test data assigns each transcript a known expression weight and simulates reads in
proportion. `check_expression.py` asserts Salmon's TPM ordering matches the truth via
**Spearman rank correlation** - i.e. the pipeline recovers *which transcripts are more highly
expressed*, not just that it ran.

### What comes next (not yet built - see ROADMAP)
Real RNA-seq continues to a **count matrix** across samples and **differential expression**
(DESeq2/edgeR), where you must understand **normalisation** and **batch effects** (technical
variation, e.g. sequencing on different days, that can masquerade as biology and must be
modelled/corrected).

---

## Part 3 - why the engineering (briefly)
The engineering exists to make the science **trustworthy**:
- **Reproducibility** (digest-pinned containers, deterministic inputs, a determinism CI gate)
  means a result can be regenerated exactly - a precondition for science.
- **Correctness gates** (known SNPs recovered; expression ranking recovered; a golden-VCF
  snapshot) assert the *biology*, not just a zero exit code.
- **Data-quality SLOs** (mapped-rate, mean coverage) stop bad data from producing confident
  nonsense.
See [OBSERVABILITY.md](OBSERVABILITY.md) and [RELEASING.md](RELEASING.md).

---

## Concepts this project covers
A checklist of the ideas to be comfortable explaining: FASTQ/quality scores; adapters and why
we trim; alignment vs pseudo-alignment; MAPQ and multi-mapping; PCR duplicates and why we mark
them; coverage/depth and its effect on confidence; genotypes (het/hom); the caller model
differences (pileup vs haplotype vs reassembly); indel normalisation; precision/recall in
filtering; variant annotation and contig-name matching; TPM and expression normalisation;
splicing and why RNA needs different aligners; batch effects; and why reproducibility, testing,
and QC gates matter for trustworthy results.
