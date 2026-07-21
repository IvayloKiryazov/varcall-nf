process BCFTOOLS_FILTER {
    tag "${sample}"
    container 'quay.io/biocontainers/bcftools:1.17--haef29d1_0@sha256:b70f139dda44b262fabf2fa8f5e0742bb811a3608c805c4304cb9a4d51194c6e'
    publishDir "${params.outdir}/variants", mode: 'copy'

    input:
    tuple val(sample), path(vcf), path(tbi)

    output:
    tuple val(sample), path("${sample}.vcf.gz"), path("${sample}.vcf.gz.tbi"), emit: vcf

    script:
    """
    bcftools filter -e '${params.filter_expr}' ${vcf} -Oz -o ${sample}.vcf.gz
    bcftools index -t ${sample}.vcf.gz
    """
}
