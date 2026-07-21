process SAMTOOLS_STATS {
    tag "${sample}"
    container 'quay.io/biocontainers/samtools:1.17--h00cdaf9_0'
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
