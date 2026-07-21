process FREEBAYES {
    tag "${sample}"
    container 'quay.io/biocontainers/freebayes:1.3.6--hbfe0e7f_2'

    input:
    tuple val(sample), path(bam), path(bai)
    path reference
    path fai

    output:
    tuple val(sample), path("${sample}.raw.vcf.gz"), path("${sample}.raw.vcf.gz.tbi"), emit: vcf

    script:
    """
    freebayes -f ${reference} ${bam} > ${sample}.freebayes.vcf
    bgzip -c ${sample}.freebayes.vcf > ${sample}.raw.vcf.gz
    tabix -p vcf ${sample}.raw.vcf.gz
    """
}
