process FASTQC {
    tag "${sample}"
    container 'quay.io/biocontainers/fastqc:0.12.1--hdfd78af_0@sha256:e194048df39c3145d9b4e0a14f4da20b59d59250465b6f2a9cb698445fd45900'
    publishDir "${params.outdir}/fastqc", mode: 'copy'

    input:
    tuple val(sample), path(reads)

    output:
    tuple val(sample), path("*.zip"),  emit: zip
    tuple val(sample), path("*.html"), emit: html

    script:
    """
    fastqc --threads ${task.cpus} ${reads}
    """
}
