# Exercises

A progressive set of exercises for learning genomics data analysis using this pipeline as a
sandbox. They pair with [`docs/ROADMAP.md`](ROADMAP.md) and [`docs/GLOSSARY.md`](GLOSSARY.md).
Each exercise lists a goal, hints, and how to check the result.

## Level 1 - read the outputs

1. **Tour the results.** Run `nextflow run . -profile docker,test --outdir results` and open
   every file under `results/`. Write one sentence per file describing what it is.
2. **Inspect an alignment.** `samtools view results/alignments/*.bam | head` and
   `samtools flagstat results/alignments/*.bam`. Identify how many reads mapped and what a SAM
   flag encodes.
3. **Read the VCF.** Open `results/variants/sample1.vcf.gz` and map each variant line back to a
   row in `assets/test_data/truth_snps.tsv`.
4. **Read the QC report.** Open `results/multiqc/multiqc_report.html`. Note what FastQC, fastp,
   samtools stats, and bcftools stats each contribute.

## Level 2 - change inputs and observe

5. **Coverage vs sensitivity.** Regenerate the test data at lower depth:
   `python3 bin/generate_test_data.py --coverage 8`. Re-run and see whether all SNPs are still
   recovered. Explain why low coverage loses calls.
6. **Toggle steps.** Run with `--trim false` and `--mark_duplicates false`. Compare metrics and
   call sets. What changed and why?
7. **Caller comparison.** Run both `--caller bcftools` and `--caller freebayes`, then
   `python3 bin/compare_vcfs.py <a> <b>`. Explain any differences.

## Level 3 - real data

8. **Real reference.** Swap in the *E. coli* K-12 genome and re-run. What breaks, what needs
   more resources?
9. **Real reads.** Download a small *E. coli* run from ENA/SRA and run it through. Compare its
   FastQC to the synthetic data.
10. **Filtering thresholds.** Tune `--filter_expr` and justify your thresholds from the QUAL/DP
    distributions in the VCF.

## Level 4 - extend the pipeline (engineering)

11. **Add a step.** Follow `.agents/skills/add-pipeline-module/SKILL.md` to add a coverage
    report (e.g. `samtools depth` / `mosdepth`) and surface it in MultiQC.
12. **Add a caller.** Follow `.agents/skills/add-variant-caller/SKILL.md` to add GATK
    HaplotypeCaller behind `--caller gatk`.
13. **Add nf-test.** Write nf-test cases for another module and add them to CI.
14. **Data-quality SLOs.** Extend `bin/check_qc.py` with a mean-coverage and duplicate-rate
    gate.

## Level 5 - a second assay

15. **RNA-seq.** Build an alternative entry that does STAR/Salmon -> counts, and produce a gene
    count matrix. Learn what normalisation (TPM/CPM) means and why.
16. **Differential expression.** Add a small DESeq2/edgeR step on a toy count matrix and
    interpret the output.

For each exercise, capture a short written explanation of the biology/stats involved - that
record is as valuable as the code.
