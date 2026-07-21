process BCFTOOLS_STATS {
    tag "${sample}"
    container 'quay.io/biocontainers/bcftools:1.17--haef29d1_0@sha256:b70f139dda44b262fabf2fa8f5e0742bb811a3608c805c4304cb9a4d51194c6e'
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
