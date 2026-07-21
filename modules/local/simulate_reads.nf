process SIMULATE_READS {
    tag "${sample}"
    container 'python:3.11-slim'
    publishDir "${params.outdir}/simulated", mode: 'copy', pattern: '*.truth.tsv'

    input:
    tuple val(sample), path(reference)

    output:
    tuple val(sample), path("${sample}.sim_*.fastq.gz"), emit: reads
    path "${sample}.truth.tsv", emit: truth

    script:
    // procps (ps) is required by Nextflow for task metrics but absent from python:*-slim.
    """
    command -v ps >/dev/null 2>&1 || { apt-get update -qq && apt-get install -y -qq procps; }
    simulate_reads_from_reference.py \\
        --reference ${reference} --sample ${sample} --outdir . \\
        --region-length ${params.sim_region_length} \\
        --coverage ${params.sim_coverage} \\
        --num-snps ${params.sim_num_snps}
    """
}
