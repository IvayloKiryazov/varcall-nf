process FASTQC {
    tag "${sample}"
    container 'quay.io/biocontainers/fastqc:0.12.1--hdfd78af_0'
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
