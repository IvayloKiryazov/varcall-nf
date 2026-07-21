process BCFTOOLS_NORM {
    tag "${sample}"
    container 'quay.io/biocontainers/bcftools:1.17--haef29d1_0@sha256:b70f139dda44b262fabf2fa8f5e0742bb811a3608c805c4304cb9a4d51194c6e'

    input:
    tuple val(sample), path(vcf), path(tbi)
    path reference
    path fai

    output:
    tuple val(sample), path("${sample}.norm.vcf.gz"), path("${sample}.norm.vcf.gz.tbi"), emit: vcf

    script:
    """
    bcftools norm -f ${reference} ${vcf} -Oz -o ${sample}.norm.vcf.gz
    bcftools index -t ${sample}.norm.vcf.gz
    """
}
