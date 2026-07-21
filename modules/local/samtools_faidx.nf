process SAMTOOLS_FAIDX {
    tag "${reference}"
    container 'quay.io/biocontainers/samtools:1.17--h00cdaf9_0'

    input:
    path reference

    output:
    path "${reference}.fai", emit: fai

    script:
    """
    samtools faidx ${reference}
    """
}
