# Changelog

## v0.1.0

Initial release.

- Nextflow DSL2 variant-calling pipeline: FastQC -> BWA-MEM alignment -> samtools sort
  -> bcftools mpileup/call -> bcftools stats -> MultiQC.
- Self-contained tiny test dataset (20 kb reference, ~40x paired reads, 10 known SNPs)
  and a deterministic generator (`bin/generate_test_data.py`).
- Correctness check (`bin/check_variants.py`) that asserts the known SNPs are recovered.
- GitHub Actions CI that runs the full pipeline on the bundled data and validates the calls.
- One biocontainer per process (fully reproducible, no local tool installs).
