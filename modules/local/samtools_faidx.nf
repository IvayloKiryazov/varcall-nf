process SAMTOOLS_FAIDX {
    tag "${reference}"
    container 'quay.io/biocontainers/samtools:1.17--h00cdaf9_0@sha256:6f88956b747a67b2a39a3ff72c4de30e665239ee11db610624dd4298e30db1bf'

    input:
    path reference

    output:
    path "${reference}.fai", emit: fai

    script:
    """
    samtools faidx ${reference}
    """
}
