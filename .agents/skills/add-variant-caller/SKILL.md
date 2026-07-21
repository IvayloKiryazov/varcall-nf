---
name: add-variant-caller
description: Add a new variant caller option to varcall-nf (e.g. GATK HaplotypeCaller, DeepVariant) selectable via --caller, converging on the shared raw-VCF contract so normalisation, filtering, stats and CI work unchanged. Use when extending the caller matrix.
---

# Add a variant caller

The pipeline selects a caller with `--caller`. Callers converge on a shared contract so the
downstream steps (normalise -> filter -> stats) and the CI checks stay the same.

## Contract

A caller module takes `tuple(sample, bam, bai)` plus the reference and its `.fai`, and emits:

```
tuple val(sample), path("${sample}.raw.vcf.gz"), path("${sample}.raw.vcf.gz.tbi"), emit: vcf
```

It must output a **bgzipped, tabix-indexed** raw VCF and should **not** `publishDir` (the final
published VCF is produced later by `BCFTOOLS_FILTER`).

## Steps

1. Create `modules/local/<caller>.nf` mirroring `bcftools_call.nf` / `freebayes.nf`. Pin the
   caller's biocontainer; ensure it can bgzip+tabix (or route the raw VCF through a compress step).
2. In `main.nf`, add an `else if (params.caller == '<caller>')` branch that calls it and sets
   `ch_raw_vcf`.
3. Add `<caller>` to the CI caller matrix in `.github/workflows/ci.yml` so correctness is checked.
4. Verify on the bundled data (via Docker) that it recovers the 10 known SNPs; confirm they
   survive `--filter_expr`.
5. Document the caller in `README.md` and `docs/PIPELINE.md`; note it in `CHANGELOG.md`.

## Notes

- Some callers (GATK) need extra inputs (sequence dictionary, known-sites, BQSR). Add those as
  their own small steps/params rather than overloading the caller module.
- Different callers report QUAL on different scales - sanity-check that `--filter_expr` is
  appropriate, or make the threshold caller-aware.
