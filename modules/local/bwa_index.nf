process BWA_INDEX {
    tag "${reference}"
    container 'quay.io/biocontainers/bwa:0.7.17--he4a0461_11'

    input:
    path reference

    output:
    path "${reference}.*", emit: index

    script:
    """
    bwa index ${reference}
    """
}
