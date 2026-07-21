process PREPARE_REFERENCE {
    tag "${reference}"
    container 'ubuntu:22.04'

    input:
    path reference

    output:
    path "reference.fa", emit: fasta

    script:
    """
    case "${reference}" in
        *.gz) gunzip -c ${reference} > reference.fa ;;
        *)    cp ${reference} reference.fa ;;
    esac
    """
}
