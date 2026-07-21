process GATK_COMBINE_GVCFS {
    tag "cohort"
    container 'quay.io/biocontainers/gatk4:4.5.0.0--py36hdfd78af_0@sha256:6cbaf094204d22734c04122933fa12eb208d6cc639ab6e4ae8af315381682847'

    input:
    path gvcfs
    path tbis
    path reference
    path fai
    path dict

    output:
    tuple path("combined.g.vcf.gz"), path("combined.g.vcf.gz.tbi"), emit: combined

    script:
    def variants = gvcfs.collect { "-V ${it}" }.join(' ')
    """
    gatk CombineGVCFs -R ${reference} ${variants} -O combined.g.vcf.gz
    """
}
