process SAMTOOLS_STATS {
    tag "${sample}"
    container 'quay.io/biocontainers/samtools:1.17--h00cdaf9_0@sha256:6f88956b747a67b2a39a3ff72c4de30e665239ee11db610624dd4298e30db1bf'
    publishDir "${params.outdir}/stats", mode: 'copy'

    input:
    tuple val(sample), path(bam), path(bai)

    output:
    path "${sample}.samtools_stats.txt", emit: stats

    script:
    """
    samtools stats ${bam} > ${sample}.samtools_stats.txt
    """
}
