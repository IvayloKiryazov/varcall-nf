#!/usr/bin/env nextflow
nextflow.enable.dsl = 2

// GATK Best-Practices joint (cohort) germline genotyping:
//   per-sample HaplotypeCaller in GVCF mode -> CombineGVCFs -> GenotypeGVCFs
// This genotypes every sample at every cohort site, so private variants get confident
// reference (0/0) calls in the samples that lack them - the point of joint calling.
//   nextflow run cohort.nf -profile docker --outdir results_cohort

include { BWA_INDEX                } from './modules/local/bwa_index.nf'
include { SAMTOOLS_FAIDX           } from './modules/local/samtools_faidx.nf'
include { SAMTOOLS_DICT            } from './modules/local/samtools_dict.nf'
include { BWA_MEM                  } from './modules/local/bwa_mem.nf'
include { MARKDUP                  } from './modules/local/markdup.nf'
include { GATK_HAPLOTYPECALLER_GVCF } from './modules/local/gatk_haplotypecaller_gvcf.nf'
include { GATK_COMBINE_GVCFS       } from './modules/local/gatk_combine_gvcfs.nf'
include { GATK_GENOTYPE_GVCFS      } from './modules/local/gatk_genotype_gvcfs.nf'

// Own param names (not `input`/`reference`) so nextflow.config defaults don't override them.
params.cohort_input     = "${projectDir}/assets/samplesheet_cohort.csv"
params.cohort_reference = "${projectDir}/assets/cohort_test_data/reference/ref.fa"
params.outdir           = 'results_cohort'

workflow {
    ch_reference = Channel.value(file(params.cohort_reference, checkIfExists: true))

    BWA_INDEX(ch_reference)
    SAMTOOLS_FAIDX(ch_reference)
    SAMTOOLS_DICT(ch_reference)
    ch_index = BWA_INDEX.out.index.first()
    ch_fai   = SAMTOOLS_FAIDX.out.fai.first()
    ch_dict  = SAMTOOLS_DICT.out.dict.first()

    ch_reads = Channel
        .fromPath(params.cohort_input, checkIfExists: true)
        .splitCsv(header: true)
        .map { row -> tuple(row.sample, [file(row.fastq_1, checkIfExists: true),
                                         file(row.fastq_2, checkIfExists: true)]) }

    BWA_MEM(ch_reads, ch_reference, ch_index)
    MARKDUP(BWA_MEM.out.sam)
    GATK_HAPLOTYPECALLER_GVCF(MARKDUP.out.bam, ch_reference, ch_fai, ch_dict)

    // Gather every sample's GVCF (and its index) for joint genotyping.
    ch_gvcfs = GATK_HAPLOTYPECALLER_GVCF.out.gvcf.map { it[1] }.collect()
    ch_tbis  = GATK_HAPLOTYPECALLER_GVCF.out.gvcf.map { it[2] }.collect()

    GATK_COMBINE_GVCFS(ch_gvcfs, ch_tbis, ch_reference, ch_fai, ch_dict)
    GATK_GENOTYPE_GVCFS(GATK_COMBINE_GVCFS.out.combined, ch_reference, ch_fai, ch_dict)
}
