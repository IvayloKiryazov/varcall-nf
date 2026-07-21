process BCFTOOLS_CALL {
    tag "${sample}"
    container 'quay.io/biocontainers/bcftools:1.17--haef29d1_0'
    publishDir "${params.outdir}/variants", mode: 'copy'

    input:
    tuple val(sample), path(bam), path(bai)
    path reference
    path fai

    output:
    tuple val(sample), path("${sample}.vcf.gz"), path("${sample}.vcf.gz.tbi"), emit: vcf

    script:
    """
    bcftools mpileup -f ${reference} ${bam} \\
        | bcftools call -mv -Oz -o ${sample}.vcf.gz
    bcftools index -t ${sample}.vcf.gz
    """
}
