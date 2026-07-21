process BCFTOOLS_STATS {
    tag "${sample}"
    container 'quay.io/biocontainers/bcftools:1.17--haef29d1_0'
    publishDir "${params.outdir}/stats", mode: 'copy'

    input:
    tuple val(sample), path(vcf), path(tbi)

    output:
    path "${sample}.bcftools_stats.txt", emit: stats

    script:
    """
    bcftools stats ${vcf} > ${sample}.bcftools_stats.txt
    """
}
