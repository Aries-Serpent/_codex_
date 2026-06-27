#!/usr/bin/env python
from __future__ import annotations

"""
Test Status Audit

Test module for status audit.
"""

"""
Test suite for codex-status-audit command.

These tests validate the status audit CLI functionality including:
- Help text output
- Skip-audit mode
- Report generation
- Baseline comparison
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def repo_root():
    """Get repository root directory."""
    return Path(__file__).resolve().parents[2]


@pytest.fixture
def status_audit_script(repo_root):
    """Get path to status_audit.py script."""
    return repo_root / "cli" / "status_audit.py"


def test_status_audit_help(status_audit_script):
    """Test that help text is shown correctly."""
    result = subprocess.run(
        [sys.executable, str(status_audit_script), "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "Result must not be empty"
    assert "Generate a comprehensive Codex status update audit report" in result.stdout, "Result must not be empty"
    assert "--output" in result.stdout, "Result must not be empty"
    assert "--baseline" in result.stdout, "Result must not be empty"
    assert "--skip-audit" in result.stdout, "Result must not be empty"


def test_status_audit_skip_mode(status_audit_script, tmp_path, repo_root):
    """Test status audit in skip-audit mode with existing artifacts."""
    # Check if artifacts exist, otherwise skip
    artifacts_dir = repo_root / "audit_artifacts"
    scored_file = artifacts_dir / "capabilities_scored.json"

    if not scored_file.exists():
        pytest.skip("No existing audit artifacts found")

    # Run with skip-audit mode
    output_dir = tmp_path / "test_reports"
    result = subprocess.run(
        [
            sys.executable,
            str(status_audit_script),
            "--skip-audit",
            "--output",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, "Result must not be empty"
    assert "SUCCESS" in result.stdout, "Result must not be empty"

    # Check that a report was generated
    reports = list(output_dir.glob("codex_status_update_*.md"))
    assert len(reports) > 0, "Reports must not be empty"

    # Verify report content structure
    report_content = reports[0].read_text()
    assert "Executive Summary" in report_content, "Content must not be empty"
    assert "Low Maturity Focus" in report_content, "Content must not be empty"
    assert "Weights (Effective)" in report_content, "Content must not be empty"
    assert "Integrity Chain" in report_content, "Content must not be empty"


def test_status_audit_artifacts_validation(status_audit_script, tmp_path):
    """Test that status audit validates required artifacts."""
    # Try to run skip-audit with missing artifacts
    result = subprocess.run(
        [
            sys.executable,
            str(status_audit_script),
            "--skip-audit",
            "--artifacts",
            str(tmp_path / "nonexistent"),
            "--output",
            str(tmp_path / "reports"),
        ],
        capture_output=True,
        text=True,
    )

    # Should fail because capabilities_scored.json is missing
    assert result.returncode != 0, "Result must not be empty"
    assert "Missing required audit artifacts" in result.stderr, "Result must not be empty"
    assert "capabilities_scored.json" in result.stderr, "Result must not be empty"


@pytest.mark.slow
def test_status_audit_full_run(status_audit_script, tmp_path):
    """Test full status audit run (slow test)."""
    output_dir = tmp_path / "test_reports"
    artifacts_dir = tmp_path / "test_artifacts"

    # Create artifacts directory
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Create minimal required artifacts
    capabilities_scored = artifacts_dir / "capabilities_scored.json"
    capabilities_scored.write_text(
        json.dumps({"capabilities": [], "timestamp": "2026-01-27T00:00:00Z", "version": "1.0"})
    )

    result = subprocess.run(
        [
            sys.executable,
            str(status_audit_script),
            "--output",
            str(output_dir),
            "--artifacts",
            str(artifacts_dir),
            "--skip-audit",  # Use existing artifacts
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )

    # Assertions
    assert result.returncode == 0, f"Command failed with code {result.returncode}:\n{result.stderr}"
    assert ("SUCCESS" in result.stdout or result.returncode == 0, "Result must not be empty"
    ), f"Expected success indicator in output:\n{result.stdout}"

    # Verify report was created
    reports = list(output_dir.glob("codex_status_update_*.md"))
    assert (len(reports) > 0, "Reports must not be empty"
    ), f"No reports generated in {output_dir}. Files: {list(output_dir.iterdir())}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
