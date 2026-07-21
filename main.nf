#!/usr/bin/env nextflow
nextflow.enable.dsl = 2

include { FASTQC          } from './modules/local/fastqc.nf'
include { BWA_INDEX       } from './modules/local/bwa_index.nf'
include { SAMTOOLS_FAIDX  } from './modules/local/samtools_faidx.nf'
include { BWA_MEM         } from './modules/local/bwa_mem.nf'
include { SAMTOOLS_SORT   } from './modules/local/samtools_sort.nf'
include { BCFTOOLS_CALL   } from './modules/local/bcftools_call.nf'
include { BCFTOOLS_STATS  } from './modules/local/bcftools_stats.nf'
include { MULTIQC         } from './modules/local/multiqc.nf'

workflow {

    // Parse the samplesheet into (sample, [fastq_1, fastq_2]) tuples.
    ch_reads = Channel
        .fromPath(params.input, checkIfExists: true)
        .splitCsv(header: true)
        .map { row -> tuple(row.sample, [file(row.fastq_1, checkIfExists: true),
                                         file(row.fastq_2, checkIfExists: true)]) }

    // The reference is a single file reused by several processes, so make it a value channel.
    ch_reference = Channel.value(file(params.reference, checkIfExists: true))

    FASTQC(ch_reads)
    BWA_INDEX(ch_reference)
    SAMTOOLS_FAIDX(ch_reference)

    BWA_MEM(ch_reads, ch_reference, BWA_INDEX.out.index.first())
    SAMTOOLS_SORT(BWA_MEM.out.sam)
    BCFTOOLS_CALL(SAMTOOLS_SORT.out.bam, ch_reference, SAMTOOLS_FAIDX.out.fai.first())
    BCFTOOLS_STATS(BCFTOOLS_CALL.out.vcf)

    // Aggregate QC (FastQC zips + bcftools stats) into a single MultiQC report.
    ch_reports = FASTQC.out.zip.map { it[1] }
        .mix(BCFTOOLS_STATS.out.stats)
        .collect()
    MULTIQC(ch_reports)
}

workflow.onComplete {
    log.info(workflow.success
        ? "Pipeline finished. Results in: ${params.outdir}"
        : "Pipeline failed. See the log above.")
}
