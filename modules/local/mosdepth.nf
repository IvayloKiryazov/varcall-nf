process MOSDEPTH {
    tag "${sample}"
    container 'quay.io/biocontainers/mosdepth:0.3.6--hd299d5a_0'
    publishDir "${params.outdir}/coverage", mode: 'copy'

    input:
    tuple val(sample), path(bam), path(bai)

    output:
    path "${sample}.mosdepth.summary.txt",     emit: summary
    path "${sample}.mosdepth.global.dist.txt", emit: dist

    script:
    """
    mosdepth -n --fast-mode ${sample} ${bam}
    """
}
