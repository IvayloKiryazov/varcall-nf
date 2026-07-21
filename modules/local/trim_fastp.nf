process TRIM_FASTP {
    tag "${sample}"
    container 'quay.io/biocontainers/fastp:0.23.4--h5f740d0_0'
    publishDir "${params.outdir}/fastp", mode: 'copy', pattern: '*.{json,html}'

    input:
    tuple val(sample), path(reads)

    output:
    tuple val(sample), path("${sample}.trim_*.fastq.gz"), emit: reads
    path "${sample}.fastp.json", emit: json

    script:
    """
    fastp \\
        -i ${reads[0]} -I ${reads[1]} \\
        -o ${sample}.trim_1.fastq.gz -O ${sample}.trim_2.fastq.gz \\
        --thread ${task.cpus} \\
        -j ${sample}.fastp.json -h ${sample}.fastp.html
    """
}
