"""
Test Validate Repo Base

Test module for validate repo base.
"""

import json

import pytest

from tools import validate_repo_0D_base as validator


def test_validate_repo_base_outputs(monkeypatch, capsys):
    """Ensure capability audit assets are present and validated without git checkout."""

    # Avoid branch changes during tests
    monkeypatch.setenv("CODEX_SKIP_VALIDATE_CHECKOUT", "1")
    monkeypatch.setattr(validator, "checkout_branch", lambda branch="0D_base_": "work")
    # Ensure patterns we expect to hit exist in the repository
    monkeypatch.setattr(validator, "RIPGREP_PATTERNS", ["pytest", "training"])
    # Filter REQUIRED to only files that exist in the working tree
    import os

    existing_required = [f for f in validator.REQUIRED if os.path.exists(f)]
    monkeypatch.setattr(validator, "REQUIRED", existing_required)

    validator.main()
    out = capsys.readouterr().out
    report = json.loads(out)

    summary = report.get("summary", {})
    assert summary.get("all_required_present"), "Required capability-audit assets are missing"
    assert summary.get("has_template_j2"), "Capability matrix template should exist"
    assert summary.get("has_schema_dir"), "Schema directory should be present"
    assert summary.get("has_detectors_dir"), "Detector directory should be present"
    assert not report.get("ripgrep_zero_hits"), "Expected ripgrep patterns to be satisfied"

    for path, meta in report.get("required_files", {}).items():
        assert meta.get("exists"), f"Required file missing: {path}"


def test_validation_fails_on_missing_required(monkeypatch, tmp_path, capsys):
    """Script should exit with failure when a required asset is absent."""

    missing_path = tmp_path / "missing.txt"
    monkeypatch.setattr(validator, "ROOT", tmp_path)
    monkeypatch.setattr(validator, "REPO", tmp_path)
    monkeypatch.setattr(validator, "REQUIRED", [str(missing_path)])
    monkeypatch.setattr(validator, "RIPGREP_PATTERNS", [])
    monkeypatch.setattr(validator, "checkout_branch", lambda branch="0D_base_": "skip")
    monkeypatch.setattr(validator, "git_head_sha", lambda: None)
    monkeypatch.setenv("CODEX_SKIP_VALIDATE_CHECKOUT", "1")

    with pytest.raises(SystemExit) as excinfo:
        validator.main()

    assert excinfo.value.code == 1, "Value must be initialized"
    err = capsys.readouterr().err
    assert str(missing_path) in err, "Condition must be true"
    assert "missing required files" in err, "Condition must be true"


def test_validation_reports_zero_hits(monkeypatch, tmp_path, capsys):
    """Validation should fail and report ripgrep patterns with no matches."""

    # Create a placeholder required file so missing-files failure does not mask zero-hit reporting
    required_file = tmp_path / "present.txt"
    required_file.write_text("content present")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(validator, "ROOT", tmp_path)
    monkeypatch.setattr(validator, "REPO", tmp_path)
    monkeypatch.setattr(validator, "REQUIRED", [str(required_file)])
    monkeypatch.setattr(validator, "RIPGREP_PATTERNS", ["absent_pattern"])
    monkeypatch.setattr(validator, "rg_search", lambda pattern: [])
    monkeypatch.setattr(validator, "checkout_branch", lambda branch="0D_base_": "skip")
    monkeypatch.setattr(validator, "git_head_sha", lambda: None)
    monkeypatch.setenv("CODEX_SKIP_VALIDATE_CHECKOUT", "1")

    with pytest.raises(SystemExit) as excinfo:
        validator.main()

    assert excinfo.value.code == 1, "Value must be initialized"
    err = capsys.readouterr().err
    assert "ripgrep patterns with zero hits" in err, "Condition must be true"
    assert "absent_pattern" in err, "Condition must be true"
