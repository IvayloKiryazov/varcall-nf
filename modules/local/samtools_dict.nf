process SAMTOOLS_DICT {
    tag "${reference}"
    container 'quay.io/biocontainers/samtools:1.17--h00cdaf9_0'

    input:
    path reference

    output:
    path "${reference.baseName}.dict", emit: dict

    script:
    """
    samtools dict ${reference} -o ${reference.baseName}.dict
    """
}
