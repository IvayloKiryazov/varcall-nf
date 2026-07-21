process SALMON_QUANT {
    tag "${sample}"
    container 'quay.io/biocontainers/salmon:1.10.2--hecfa306_0@sha256:6a5078f0a868bcc07f0b687fe099d564b6bf129b7912623ab781a8ed1354cfdf'
    publishDir "${params.outdir}/salmon", mode: 'copy'

    input:
    tuple val(sample), path(reads)
    path index

    output:
    tuple val(sample), path("${sample}"), emit: quant
    path "${sample}/quant.sf",            emit: sf

    script:
    """
    salmon quant -i ${index} -l A -r ${reads} -o ${sample} \\
        --validateMappings --threads ${task.cpus}
    """
}
