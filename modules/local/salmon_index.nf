process SALMON_INDEX {
    tag "${transcriptome}"
    container 'quay.io/biocontainers/salmon:1.10.2--hecfa306_0@sha256:6a5078f0a868bcc07f0b687fe099d564b6bf129b7912623ab781a8ed1354cfdf'

    input:
    path transcriptome

    output:
    path "salmon_index", emit: index

    script:
    """
    salmon index -t ${transcriptome} -i salmon_index -k 31
    """
}
