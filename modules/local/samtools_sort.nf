process SAMTOOLS_SORT {
    tag "${sample}"
    container 'quay.io/biocontainers/samtools:1.17--h00cdaf9_0'
    publishDir "${params.outdir}/alignments", mode: 'copy'

    input:
    tuple val(sample), path(sam)

    output:
    tuple val(sample), path("${sample}.sorted.bam"), path("${sample}.sorted.bam.bai"), emit: bam

    script:
    """
    samtools sort -@ ${task.cpus} -o ${sample}.sorted.bam ${sam}
    samtools index ${sample}.sorted.bam
    """
}
