#!/usr/bin/env nextflow
nextflow.enable.dsl = 2

include { FASTQC          } from './modules/local/fastqc.nf'
include { TRIM_FASTP      } from './modules/local/trim_fastp.nf'
include { BWA_INDEX       } from './modules/local/bwa_index.nf'
include { SAMTOOLS_FAIDX  } from './modules/local/samtools_faidx.nf'
include { BWA_MEM         } from './modules/local/bwa_mem.nf'
include { SAMTOOLS_SORT   } from './modules/local/samtools_sort.nf'
include { MARKDUP         } from './modules/local/markdup.nf'
include { SAMTOOLS_STATS  } from './modules/local/samtools_stats.nf'
include { BCFTOOLS_CALL   } from './modules/local/bcftools_call.nf'
include { FREEBAYES       } from './modules/local/freebayes.nf'
include { BCFTOOLS_NORM   } from './modules/local/bcftools_norm.nf'
include { BCFTOOLS_FILTER } from './modules/local/bcftools_filter.nf'
include { BCFTOOLS_STATS  } from './modules/local/bcftools_stats.nf'
include { MULTIQC         } from './modules/local/multiqc.nf'

workflow {

    // Parse the samplesheet into (sample, [fastq_1, fastq_2]) tuples.
    ch_reads = Channel
        .fromPath(params.input, checkIfExists: true)
        .splitCsv(header: true)
        .map { row -> tuple(row.sample, [file(row.fastq_1, checkIfExists: true),
                                         file(row.fastq_2, checkIfExists: true)]) }

    // The reference is reused by several processes, so make derived indices value channels.
    ch_reference = Channel.value(file(params.reference, checkIfExists: true))

    FASTQC(ch_reads)
    BWA_INDEX(ch_reference)
    SAMTOOLS_FAIDX(ch_reference)
    ch_index = BWA_INDEX.out.index.first()
    ch_fai   = SAMTOOLS_FAIDX.out.fai.first()

    // Optional adapter/quality trimming.
    if (params.trim) {
        TRIM_FASTP(ch_reads)
        ch_align_reads = TRIM_FASTP.out.reads
        ch_fastp_qc    = TRIM_FASTP.out.json
    }
    else {
        ch_align_reads = ch_reads
        ch_fastp_qc    = Channel.empty()
    }

    BWA_MEM(ch_align_reads, ch_reference, ch_index)

    // Optional duplicate marking (recommended for real data).
    if (params.mark_duplicates) {
        MARKDUP(BWA_MEM.out.sam)
        ch_bam = MARKDUP.out.bam
    }
    else {
        SAMTOOLS_SORT(BWA_MEM.out.sam)
        ch_bam = SAMTOOLS_SORT.out.bam
    }

    SAMTOOLS_STATS(ch_bam)

    // Variant calling: pick the caller with --caller (bcftools | freebayes).
    if (params.caller == 'bcftools') {
        BCFTOOLS_CALL(ch_bam, ch_reference, ch_fai)
        ch_raw_vcf = BCFTOOLS_CALL.out.vcf
    }
    else if (params.caller == 'freebayes') {
        FREEBAYES(ch_bam, ch_reference, ch_fai)
        ch_raw_vcf = FREEBAYES.out.vcf
    }
    else {
        error "Unknown --caller '${params.caller}'. Supported: 'bcftools', 'freebayes'."
    }

    // Normalise then filter to produce the final published VCF.
    BCFTOOLS_NORM(ch_raw_vcf, ch_reference, ch_fai)
    BCFTOOLS_FILTER(BCFTOOLS_NORM.out.vcf)
    ch_vcf = BCFTOOLS_FILTER.out.vcf

    BCFTOOLS_STATS(ch_vcf)

    // Aggregate QC (FastQC + fastp + samtools stats + bcftools stats) into one MultiQC report.
    ch_reports = FASTQC.out.zip.map { it[1] }
        .mix(ch_fastp_qc)
        .mix(SAMTOOLS_STATS.out.stats)
        .mix(BCFTOOLS_STATS.out.stats)
        .collect()
    MULTIQC(ch_reports)
}
