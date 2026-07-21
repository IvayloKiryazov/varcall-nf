process BCFTOOLS_NORM {
    tag "${sample}"
    container 'quay.io/biocontainers/bcftools:1.17--haef29d1_0'

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
