# Versioning & releases

## Versioning policy

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** - breaking changes to the CLI/params or output layout.
- **MINOR** - new, backwards-compatible capabilities (a new caller, step, or profile).
- **PATCH** - fixes that don't change the interface.

The pipeline version is set in `nextflow.config` (`manifest.version`) and mirrored in
`CHANGELOG.md`. During `0.x`, minor bumps may still adjust interfaces as the design settles;
from `1.0.0` onward the public interface is stable within a major version.

## Release checklist

1. Update `CHANGELOG.md` and `manifest.version` in `nextflow.config`.
2. Ensure all gating CI is green and the on-demand `test_full` run passes.
3. Tag the release and push: `git tag -a vX.Y.Z -m "vX.Y.Z" && git push origin vX.Y.Z`.
4. Create a GitHub Release from the tag with the changelog notes.

## Roadmap to v1.0

`0.x` builds breadth; `1.0.0` is a stability contract. Exit criteria for **v1.0.0**:

- [x] Core DNA path: trim -> dup-mark -> align -> multi-caller -> normalise -> filter -> QC.
- [x] Multiple callers (bcftools, freebayes, gatk) with a correctness matrix in CI.
- [x] Coverage + data-quality SLO gates; reproducibility (determinism) gate.
- [x] Golden-VCF snapshot regression; workflow linting; nf-test module tests.
- [x] On-demand real-reference run (`test_full`) verified in CI.
- [x] Real **ENA/SRA reads** on the real-data path (verified via `test_sra`).
- [x] **Multi-sample** support end-to-end with a joint (cross-sample) report.
- [x] **Annotation** (SnpEff) verified on the real-data path (custom DB from reference + GFF).
- [x] **Container digest pinning** (`@sha256:...`) for bit-for-bit reproducibility.
- [x] Release automation + **SBOM** attached to each GitHub Release.
- [x] CI linting (actionlint + ruff + pre-commit) and a documented parameter schema.
- [x] Stable, documented parameter set (`nextflow_schema.json`, kept in sync by a test).
- [ ] First tagged GitHub Release (this tag).

When every box is ticked and CI (gating + `test_full`) is green, cut **v1.0.0**.
