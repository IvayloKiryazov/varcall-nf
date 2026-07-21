process BCFTOOLS_CALL {
    tag "${sample}"
    container 'quay.io/biocontainers/bcftools:1.17--haef29d1_0@sha256:b70f139dda44b262fabf2fa8f5e0742bb811a3608c805c4304cb9a4d51194c6e'

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
