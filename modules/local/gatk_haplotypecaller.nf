process GATK_HAPLOTYPECALLER {
    tag "${sample}"
    container 'quay.io/biocontainers/gatk4:4.5.0.0--py36hdfd78af_0@sha256:6cbaf094204d22734c04122933fa12eb208d6cc639ab6e4ae8af315381682847'

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
