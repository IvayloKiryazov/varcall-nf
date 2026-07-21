process BCFTOOLS_CALL {
    tag "${sample}"
    container 'quay.io/biocontainers/bcftools:1.17--haef29d1_0'

    input:
    tuple val(sample), path(bam), path(bai)
    path reference
    path fai

    output:
    tuple val(sample), path("${sample}.raw.vcf.gz"), path("${sample}.raw.vcf.gz.tbi"), emit: vcf

    script:
    """
    bcftools mpileup -f ${reference} ${bam} \\
        | bcftools call -mv -Oz -o ${sample}.raw.vcf.gz
    bcftools index -t ${sample}.raw.vcf.gz
    """
}
