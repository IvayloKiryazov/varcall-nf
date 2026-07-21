#!/usr/bin/env nextflow
nextflow.enable.dsl = 2

include { PREPARE_REFERENCE } from './modules/local/prepare_reference.nf'
include { SIMULATE_READS    } from './modules/local/simulate_reads.nf'
include { FASTQC          } from './modules/local/fastqc.nf'
include { TRIM_FASTP      } from './modules/local/trim_fastp.nf'
include { BWA_INDEX       } from './modules/local/bwa_index.nf'
include { SAMTOOLS_FAIDX  } from './modules/local/samtools_faidx.nf'
include { BWA_MEM         } from './modules/local/bwa_mem.nf'
include { SAMTOOLS_SORT   } from './modules/local/samtools_sort.nf'
include { MARKDUP         } from './modules/local/markdup.nf'
include { SAMTOOLS_STATS  } from './modules/local/samtools_stats.nf'
include { MOSDEPTH        } from './modules/local/mosdepth.nf'
include { SAMTOOLS_DICT   } from './modules/local/samtools_dict.nf'
include { BCFTOOLS_CALL   } from './modules/local/bcftools_call.nf'
include { FREEBAYES       } from './modules/local/freebayes.nf'
include { GATK_HAPLOTYPECALLER } from './modules/local/gatk_haplotypecaller.nf'
include { BCFTOOLS_NORM   } from './modules/local/bcftools_norm.nf'
include { BCFTOOLS_FILTER } from './modules/local/bcftools_filter.nf'
include { BCFTOOLS_STATS  } from './modules/local/bcftools_stats.nf'
include { SNPEFF          } from './modules/local/snpeff.nf'
include { MULTIQC         } from './modules/local/multiqc.nf'

workflow {

    // Reads + reference: either simulate from a (possibly remote/gzipped) reference
    // (--simulate_reads, used by -profile test_full), or read a local samplesheet.
    if (params.simulate_reads) {
        PREPARE_REFERENCE(Channel.value(file(params.reference, checkIfExists: true)))
        ch_reference = PREPARE_REFERENCE.out.fasta.first()
        SIMULATE_READS(ch_reference.map { ref -> tuple(params.sample_id, ref) })
        ch_reads = SIMULATE_READS.out.reads
    }
    else {
        ch_reads = Channel
            .fromPath(params.input, checkIfExists: true)
            .splitCsv(header: true)
            .map { row -> tuple(row.sample, [file(row.fastq_1, checkIfExists: true),
                                             file(row.fastq_2, checkIfExists: true)]) }
        ch_reference = Channel.value(file(params.reference, checkIfExists: true))
    }

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
    MOSDEPTH(ch_bam)

    // Variant calling: pick the caller with --caller (bcftools | freebayes | gatk).
    if (params.caller == 'bcftools') {
        BCFTOOLS_CALL(ch_bam, ch_reference, ch_fai)
        ch_raw_vcf = BCFTOOLS_CALL.out.vcf
    }
    else if (params.caller == 'freebayes') {
        FREEBAYES(ch_bam, ch_reference, ch_fai)
        ch_raw_vcf = FREEBAYES.out.vcf
    }
    else if (params.caller == 'gatk') {
        SAMTOOLS_DICT(ch_reference)
        GATK_HAPLOTYPECALLER(ch_bam, ch_reference, ch_fai, SAMTOOLS_DICT.out.dict.first())
        ch_raw_vcf = GATK_HAPLOTYPECALLER.out.vcf
    }
    else {
        error "Unknown --caller '${params.caller}'. Supported: 'bcftools', 'freebayes', 'gatk'."
    }

    // Normalise then filter to produce the final published VCF.
    BCFTOOLS_NORM(ch_raw_vcf, ch_reference, ch_fai)
    BCFTOOLS_FILTER(BCFTOOLS_NORM.out.vcf)
    ch_vcf = BCFTOOLS_FILTER.out.vcf

    BCFTOOLS_STATS(ch_vcf)

    // Optional functional annotation (needs a matching snpeff_db; used on real-data runs).
    if (params.annotate) {
        SNPEFF(ch_vcf)
    }

    // Aggregate QC (FastQC + fastp + samtools stats + mosdepth + bcftools stats) into MultiQC.
    ch_reports = FASTQC.out.zip.map { it[1] }
        .mix(ch_fastp_qc)
        .mix(SAMTOOLS_STATS.out.stats)
        .mix(MOSDEPTH.out.summary)
        .mix(MOSDEPTH.out.dist)
        .mix(BCFTOOLS_STATS.out.stats)
        .collect()
    MULTIQC(ch_reports)
}
