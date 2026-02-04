"""
Test Legacy Import Report

Test module for legacy import report.
"""

import csv
import subprocess
from pathlib import Path


def test_legacy_import_report_header_exists():
    repo_root = Path(__file__).resolve().parents[2]
    reports_dir = repo_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Run the analyzer
    script = repo_root / "scripts" / "remediation" / "analyze_legacy_usage.py"
    subprocess.run(["python", str(script)], check=True)

    csv_path = reports_dir / "legacy_import_usage.csv"
    assert csv_path.exists(), "legacy_import_usage.csv was not created"

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == ["module", "full_import", "file", "line"], "CSV header is incorrect"
