process SNPEFF {
    tag "${sample}"
    container 'quay.io/biocontainers/snpeff:5.1--hdfd78af_2@sha256:fe9947c05033dbca97de108732667e66cb1ab6e0860a3e507c4f907f5d7b4a9c'
    publishDir "${params.outdir}/annotated", mode: 'copy'

    input:
    tuple val(sample), path(vcf), path(tbi)
    path reference
    path annotation

    output:
    tuple val(sample), path("${sample}.annotated.vcf"), emit: vcf
    path "snpEff_summary.html", optional: true

    script:
    // Build a custom SnpEff database from the reference + its annotation so contig names
    // match the called VCF by construction (avoids the usual DB/contig mismatch).
    """
    mkdir -p data/genome
    cp ${reference} data/genome/sequences.fa
    case "${annotation}" in
        *.gz) gunzip -c ${annotation} > data/genome/genes.gff ;;
        *)    cp ${annotation} data/genome/genes.gff ;;
    esac
    printf 'data.dir = ./data/\\ngenome.genome : custom\\n' > snpEff.config
    snpEff build -gff3 -noCheckCds -noCheckProtein -c snpEff.config -dataDir \$PWD/data genome
    snpEff -c snpEff.config -dataDir \$PWD/data genome ${vcf} > ${sample}.annotated.vcf
    """
}
