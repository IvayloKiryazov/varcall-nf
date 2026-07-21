process MULTIQC {
    container 'quay.io/biocontainers/multiqc:1.19--pyhdfd78af_0@sha256:6487aad25c1d232abb98e7b23236606205ce39882a3de22b20e6d12b3d3e69af'
    publishDir "${params.outdir}/multiqc", mode: 'copy'

    input:
    path '*'

    output:
    path "multiqc_report.html", emit: report
    path "multiqc_data",        emit: data

    script:
    """
    multiqc --force .
    """
}
