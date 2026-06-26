"""Tests for manifest determinism in Space Traversal Workflow v1.4.0."""

import json
from pathlib import Path

import scripts.space_traversal.audit_runner as audit_runner


def test_stage_s7_manifest_sorts_artifacts_and_reports_coverage(monkeypatch, tmp_path):
    """Test that manifest artifacts are sorted and coverage_stats is properly computed."""
    artifacts_dir = tmp_path / "audit_artifacts"
    artifacts_dir.mkdir()

    # Create unordered artifacts
    (artifacts_dir / "zeta.json").write_text("{}", encoding="utf-8")
    (artifacts_dir / "alpha.json").write_text("{}", encoding="utf-8")

    coverage_map = {
        "b.py": {"percent": 0.25, "covered_lines": [2]},
        "a.py": {"percent": 0.75, "covered_lines": [1, 2]},
    }
    coverage_path = artifacts_dir / "coverage_map.json"
    coverage_path.write_text(json.dumps(coverage_map), encoding="utf-8")

    template_path = (
        Path(__file__).resolve().parents[2] / "templates" / "audit" / "capability_matrix.md.j2"
    )
    cfg = {
        "weights": {
            "functionality": 0.2,
            "consistency": 0.2,
            "tests": 0.2,
            "safeguards": 0.2,
            "documentation": 0.2,
        },
        "output": {
            "artifacts_dir": str(artifacts_dir),
            "matrix_template": str(template_path),
        },
        "metrics_schema_version": "2.0.0",
    }

    # Keep manifest writes isolated from the repo root
    monkeypatch.setattr(audit_runner, "ROOT", tmp_path)

    manifest = audit_runner.stage_s7_manifest(cfg)

    # Verify artifacts are sorted by name
    artifact_names = [entry["name"] for entry in manifest["artifacts"]]
    assert artifact_names == sorted(artifact_names), "artifact_names is not valid"

    # Verify coverage stats are correctly computed
    expected_stats = {
        "total_files": 2,
        "min_percent": 0.25,
        "max_percent": 0.75,
        "avg_percent": 0.5,
    }
    assert manifest["coverage_stats"] == expected_stats, "Condition must be true"

    # Verify manifest is written to disk
    out_manifest = tmp_path / "audit_run_manifest.json"
    assert out_manifest.exists(), "Condition must be true"
    persisted = json.loads(out_manifest.read_text())
    assert persisted["coverage_stats"] == expected_stats, "Condition must be true"


def test_stage_s7_manifest_handles_empty_coverage(monkeypatch, tmp_path):
    """Test that manifest handles empty coverage_map correctly."""
    artifacts_dir = tmp_path / "audit_artifacts"
    artifacts_dir.mkdir()

    # Create empty coverage map
    coverage_map = {}
    coverage_path = artifacts_dir / "coverage_map.json"
    coverage_path.write_text(json.dumps(coverage_map), encoding="utf-8")

    template_path = (
        Path(__file__).resolve().parents[2] / "templates" / "audit" / "capability_matrix.md.j2"
    )
    cfg = {
        "weights": {
            "functionality": 0.2,
            "consistency": 0.2,
            "tests": 0.2,
            "safeguards": 0.2,
            "documentation": 0.2,
        },
        "output": {
            "artifacts_dir": str(artifacts_dir),
            "matrix_template": str(template_path),
        },
        "metrics_schema_version": "2.0.0",
    }

    monkeypatch.setattr(audit_runner, "ROOT", tmp_path)

    manifest = audit_runner.stage_s7_manifest(cfg)

    # With empty coverage, should have zero stats
    expected_stats = {
        "total_files": 0,
        "min_percent": 0.0,
        "max_percent": 0.0,
        "avg_percent": 0.0,
    }
    assert manifest["coverage_stats"] == expected_stats, "Condition must be true"


def test_stage_s7_manifest_no_coverage_file(monkeypatch, tmp_path):
    """Test that manifest works without coverage_map.json."""
    artifacts_dir = tmp_path / "audit_artifacts"
    artifacts_dir.mkdir()

    # Create only a simple artifact
    (artifacts_dir / "test.json").write_text("{}", encoding="utf-8")

    template_path = (
        Path(__file__).resolve().parents[2] / "templates" / "audit" / "capability_matrix.md.j2"
    )
    cfg = {
        "weights": {
            "functionality": 0.2,
            "consistency": 0.2,
            "tests": 0.2,
            "safeguards": 0.2,
            "documentation": 0.2,
        },
        "output": {
            "artifacts_dir": str(artifacts_dir),
            "matrix_template": str(template_path),
        },
        "metrics_schema_version": "2.0.0",
    }

    monkeypatch.setattr(audit_runner, "ROOT", tmp_path)

    manifest = audit_runner.stage_s7_manifest(cfg)

    # Without coverage_map.json, no coverage_stats should be present
    assert "coverage_stats" not in manifest, "Condition must be true"
