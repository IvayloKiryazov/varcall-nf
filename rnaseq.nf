#!/usr/bin/env nextflow
nextflow.enable.dsl = 2

// A second, minimal assay: RNA-seq transcript quantification with Salmon.
// Kept as a separate entry point so the stable DNA pipeline (main.nf) is untouched.
//   nextflow run rnaseq.nf -profile docker --outdir results_rna

include { SALMON_INDEX } from './modules/local/salmon_index.nf'
include { SALMON_QUANT } from './modules/local/salmon_quant.nf'

params.transcriptome = "${projectDir}/assets/rnaseq_test_data/transcriptome.fa"
params.reads         = "${projectDir}/assets/rnaseq_test_data/reads.fastq.gz"
params.rna_sample    = 'rna1'
params.outdir        = 'results_rna'

workflow {
    ch_transcriptome = Channel.value(file(params.transcriptome, checkIfExists: true))
    ch_reads = Channel.value(tuple(params.rna_sample, file(params.reads, checkIfExists: true)))

    SALMON_INDEX(ch_transcriptome)
    SALMON_QUANT(ch_reads, SALMON_INDEX.out.index.first())
}
