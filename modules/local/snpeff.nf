process SNPEFF {
    tag "${sample}"
    container 'quay.io/biocontainers/snpeff:5.1--hdfd78af_2'
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
