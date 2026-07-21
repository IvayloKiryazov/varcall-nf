process FREEBAYES {
    tag "${sample}"
    container 'quay.io/biocontainers/freebayes:1.3.6--hbfe0e7f_2'
    publishDir "${params.outdir}/variants", mode: 'copy'

    input:
    tuple val(sample), path(bam), path(bai)
    path reference
    path fai

    output:
    tuple val(sample), path("${sample}.vcf.gz"), path("${sample}.vcf.gz.tbi"), emit: vcf

    script:
    """
    freebayes -f ${reference} ${bam} > ${sample}.raw.vcf
    bgzip -c ${sample}.raw.vcf > ${sample}.vcf.gz
    tabix -p vcf ${sample}.vcf.gz
    """
}
