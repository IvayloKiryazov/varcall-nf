process BWA_MEM {
    tag "${sample}"
    container 'quay.io/biocontainers/bwa:0.7.17--he4a0461_11@sha256:652ca694adcb54ca799c22b843c086d570875ef14334a90ffeab0e1beb5f5741'

    input:
    tuple val(sample), path(reads)
    path reference
    path index

    output:
    tuple val(sample), path("${sample}.sam"), emit: sam

    script:
    def read_group = "@RG\\tID:${sample}\\tSM:${sample}\\tPL:ILLUMINA"
    """
    bwa mem -t ${task.cpus} -R '${read_group}' ${reference} ${reads[0]} ${reads[1]} > ${sample}.sam
    """
}
