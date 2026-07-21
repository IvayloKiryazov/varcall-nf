"""Unit / integration tests for the pipeline's Python helper tools.

These run without Nextflow or Docker: they exercise the scripts in ``bin/`` directly, so
CI can validate the tooling logic quickly and independently of the genomics stack.
"""
from __future__ import annotations

import gzip
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BIN = REPO_ROOT / "bin"


def run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(BIN / script), *args],
        capture_output=True,
        text=True,
    )


def write_vcf_gz(path: Path, records: list[tuple[str, int, str, str]]) -> None:
    with gzip.open(path, "wt") as fh:
        fh.write("##fileformat=VCFv4.2\n")
        fh.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")
        for chrom, pos, ref, alt in records:
            fh.write(f"{chrom}\t{pos}\t.\t{ref}\t{alt}\t60\t.\t.\n")


# --- generate_test_data.py ---------------------------------------------------

def test_generate_test_data_is_deterministic(tmp_path: Path) -> None:
    out1, out2 = tmp_path / "a", tmp_path / "b"
    for out in (out1, out2):
        result = run("generate_test_data.py", "--outdir", str(out), "--num-snps", "5")
        assert result.returncode == 0, result.stderr
    ref1 = (out1 / "reference" / "ref.fa").read_bytes()
    ref2 = (out2 / "reference" / "ref.fa").read_bytes()
    assert ref1 == ref2
    truth = (out1 / "truth_snps.tsv").read_text().splitlines()
    assert len(truth) == 1 + 5  # header + 5 SNPs


# --- check_variants.py -------------------------------------------------------

def test_check_variants_pass(tmp_path: Path) -> None:
    truth = tmp_path / "truth.tsv"
    truth.write_text("contig\tposition\tref\talt\nchr1\t100\tA\tG\nchr1\t200\tC\tT\n")
    vcf = tmp_path / "calls.vcf.gz"
    write_vcf_gz(vcf, [("chr1", 100, "A", "G"), ("chr1", 200, "C", "T")])
    result = run("check_variants.py", "--vcf", str(vcf), "--truth", str(truth))
    assert result.returncode == 0
    assert "PASS" in result.stdout


def test_check_variants_fail_on_missing(tmp_path: Path) -> None:
    truth = tmp_path / "truth.tsv"
    truth.write_text("contig\tposition\tref\talt\nchr1\t100\tA\tG\nchr1\t200\tC\tT\n")
    vcf = tmp_path / "calls.vcf.gz"
    write_vcf_gz(vcf, [("chr1", 100, "A", "G")])  # missing 200
    result = run("check_variants.py", "--vcf", str(vcf), "--truth", str(truth))
    assert result.returncode == 1
    assert "MISSING" in result.stdout


# --- compare_vcfs.py ---------------------------------------------------------

def test_compare_vcfs_identical(tmp_path: Path) -> None:
    records = [("chr1", 100, "A", "G"), ("chr1", 200, "C", "T")]
    a, b = tmp_path / "a.vcf.gz", tmp_path / "b.vcf.gz"
    write_vcf_gz(a, records)
    write_vcf_gz(b, records)
    result = run("compare_vcfs.py", str(a), str(b), "--require-identical")
    assert result.returncode == 0
    assert "IDENTICAL" in result.stdout


def test_compare_vcfs_different(tmp_path: Path) -> None:
    a, b = tmp_path / "a.vcf.gz", tmp_path / "b.vcf.gz"
    write_vcf_gz(a, [("chr1", 100, "A", "G")])
    write_vcf_gz(b, [("chr1", 100, "A", "G"), ("chr1", 300, "T", "C")])
    result = run("compare_vcfs.py", str(a), str(b), "--require-identical")
    assert result.returncode == 1
    assert "only in B" in result.stdout


# --- pipeline_metrics.py -----------------------------------------------------

def test_pipeline_metrics_report_and_slo(tmp_path: Path) -> None:
    trace = tmp_path / "trace.txt"
    # raw units: realtime in ms, memory in bytes
    trace.write_text(
        "task_id\tname\tstatus\texit\trealtime\t%cpu\tpeak_rss\tpeak_vmem\trchar\twchar\n"
        "1\tFASTQC (s1)\tCOMPLETED\t0\t5000\t95.0\t104857600\t209715200\t1000\t1000\n"
        "2\tBWA_MEM (s1)\tCOMPLETED\t0\t20000\t180.0\t524288000\t1048576000\t2000\t2000\n"
    )
    md = tmp_path / "metrics.md"
    js = tmp_path / "metrics.json"
    result = run(
        "pipeline_metrics.py",
        "--trace", str(trace),
        "--out-md", str(md),
        "--out-json", str(js),
    )
    assert result.returncode == 0
    assert "Pipeline metrics" in md.read_text()
    assert '"n_steps": 2' in js.read_text()

    # Enforce a tight SLO that BWA_MEM (20s) must breach.
    enforced = run(
        "pipeline_metrics.py",
        "--trace", str(trace),
        "--max-step-seconds", "10",
        "--enforce",
    )
    assert enforced.returncode == 1
    assert "SLO breaches" in enforced.stdout


# --- validate_samplesheet.py -------------------------------------------------

def test_validate_samplesheet_ok(tmp_path: Path) -> None:
    r1, r2 = tmp_path / "a_1.fq.gz", tmp_path / "a_2.fq.gz"
    r1.write_text("")
    r2.write_text("")
    sheet = tmp_path / "sheet.csv"
    sheet.write_text(f"sample,fastq_1,fastq_2\nsampleA,{r1},{r2}\n")
    result = run("validate_samplesheet.py", str(sheet), "--check-files")
    assert result.returncode == 0
    assert "OK" in result.stdout


def test_validate_samplesheet_duplicate_and_missing(tmp_path: Path) -> None:
    sheet = tmp_path / "sheet.csv"
    sheet.write_text(
        "sample,fastq_1,fastq_2\n"
        "s1,/no/such_1.fq.gz,/no/such_2.fq.gz\n"
        "s1,/no/other_1.fq.gz,/no/other_2.fq.gz\n"
    )
    result = run("validate_samplesheet.py", str(sheet), "--check-files")
    assert result.returncode == 1
    assert "duplicate sample" in result.stdout
    assert "not found" in result.stdout


def test_validate_samplesheet_missing_column(tmp_path: Path) -> None:
    sheet = tmp_path / "sheet.csv"
    sheet.write_text("sample,fastq_1\ns1,x_1.fq.gz\n")
    result = run("validate_samplesheet.py", str(sheet))
    assert result.returncode == 1
    assert "Missing required column" in result.stdout


# --- check_qc.py -------------------------------------------------------------

def test_check_qc_pass_and_fail(tmp_path: Path) -> None:
    stats = tmp_path / "s.txt"
    stats.write_text(
        "# comment\n"
        "SN\traw total sequences:\t1000\n"
        "SN\treads mapped:\t980\n"
    )
    ok = run("check_qc.py", str(stats), "--min-mapped-rate", "0.90")
    assert ok.returncode == 0
    assert "PASS" in ok.stdout

    bad = run("check_qc.py", str(stats), "--min-mapped-rate", "0.99")
    assert bad.returncode == 1
    assert "FAIL" in bad.stdout
