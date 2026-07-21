process GATK_HAPLOTYPECALLER {
    tag "${sample}"
    container 'quay.io/biocontainers/gatk4:4.5.0.0--py36hdfd78af_0'

    input:
    tuple val(sample), path(bam), path(bai)
    path reference
    path fai
    path dict

    output:
    tuple val(sample), path("${sample}.raw.vcf.gz"), path("${sample}.raw.vcf.gz.tbi"), emit: vcf

    script:
    """
    gatk HaplotypeCaller -R ${reference} -I ${bam} -O ${sample}.raw.vcf.gz
    """
}
