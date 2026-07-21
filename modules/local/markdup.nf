process MARKDUP {
    tag "${sample}"
    container 'quay.io/biocontainers/samtools:1.17--h00cdaf9_0@sha256:6f88956b747a67b2a39a3ff72c4de30e665239ee11db610624dd4298e30db1bf'
    publishDir "${params.outdir}/alignments", mode: 'copy'

    input:
    tuple val(sample), path(sam)

    output:
    tuple val(sample), path("${sample}.markdup.bam"), path("${sample}.markdup.bam.bai"), emit: bam

    script:
    """
    samtools sort -n -@ ${task.cpus} -O bam -o name_sorted.bam ${sam}
    samtools fixmate -m name_sorted.bam fixmate.bam
    samtools sort -@ ${task.cpus} -o coord_sorted.bam fixmate.bam
    samtools markdup coord_sorted.bam ${sample}.markdup.bam
    samtools index ${sample}.markdup.bam
    """
}
