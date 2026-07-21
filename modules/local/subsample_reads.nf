process SUBSAMPLE_READS {
    tag "${sample}"
    container 'quay.io/biocontainers/seqtk:1.4--he4a0461_1@sha256:24a4a7ebb63af178822c166befb4fcafc77d1b6754fe52fb085f0835cc274496'

    input:
    tuple val(sample), path(reads)
    val n_pairs

    output:
    tuple val(sample), path("${sample}.sub_*.fastq.gz"), emit: reads

    script:
    // Same seed for both mates keeps pairs in sync.
    """
    seqtk sample -s100 ${reads[0]} ${n_pairs} | gzip > ${sample}.sub_1.fastq.gz
    seqtk sample -s100 ${reads[1]} ${n_pairs} | gzip > ${sample}.sub_2.fastq.gz
    """
}
