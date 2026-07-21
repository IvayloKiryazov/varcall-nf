process BWA_INDEX {
    tag "${reference}"
    container 'quay.io/biocontainers/bwa:0.7.17--he4a0461_11@sha256:652ca694adcb54ca799c22b843c086d570875ef14334a90ffeab0e1beb5f5741'

    input:
    path reference

    output:
    path "${reference}.*", emit: index

    script:
    """
    bwa index ${reference}
    """
}
