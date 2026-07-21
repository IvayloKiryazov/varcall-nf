process SNPEFF {
    tag "${sample}"
    container 'quay.io/biocontainers/snpeff:5.1--hdfd78af_2@sha256:fe9947c05033dbca97de108732667e66cb1ab6e0860a3e507c4f907f5d7b4a9c'
    publishDir "${params.outdir}/annotated", mode: 'copy'

    input:
    tuple val(sample), path(vcf), path(tbi)

    output:
    tuple val(sample), path("${sample}.annotated.vcf"), emit: vcf

    script:
    """
    snpEff -dataDir \$PWD/snpeff_data ${params.snpeff_db} ${vcf} > ${sample}.annotated.vcf
    """
}
