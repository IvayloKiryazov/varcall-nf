process GATK_GENOTYPE_GVCFS {
    tag "cohort"
    container 'quay.io/biocontainers/gatk4:4.5.0.0--py36hdfd78af_0@sha256:6cbaf094204d22734c04122933fa12eb208d6cc639ab6e4ae8af315381682847'
    publishDir "${params.outdir}/cohort", mode: 'copy'

    input:
    tuple path(combined), path(combined_tbi)
    path reference
    path fai
    path dict

    output:
    tuple path("cohort.vcf.gz"), path("cohort.vcf.gz.tbi"), emit: vcf

    script:
    """
    gatk GenotypeGVCFs -R ${reference} -V ${combined} -O cohort.vcf.gz
    """
}
