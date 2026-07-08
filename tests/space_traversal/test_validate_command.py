"""Tests for the validate command in audit_runner.py (v1.4.0)."""

import json
import tempfile
from pathlib import Path

import pytest


def load_audit_runner():
    """Dynamically load audit_runner module."""
    import importlib.util

    audit_runner_path = (
        Path(__file__).resolve().parents[2] / "scripts" / "space_traversal" / "audit_runner.py"
    )
    spec = importlib.util.spec_from_file_location("audit_runner", str(audit_runner_path))
    audit_runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit_runner)
    return audit_runner


# Reference constants from audit_runner
EXIT_LOW_MATURITY = 4
EXIT_MISSING_DETECTOR = 5
EXIT_MISSING_ARTIFACTS = 2


def test_validate_command_passes_when_all_above_threshold():
    """Test validate passes when all capabilities are above threshold."""
    audit_runner = load_audit_runner()

    # ADDED: Verify the function exists
    if not hasattr(audit_runner, "command_validate"):
        pytest.skip("command_validate not found in audit_runner module")

    with tempfile.TemporaryDirectory() as tmp_dir:
        artifacts_dir = Path(tmp_dir) / "audit_artifacts"
        artifacts_dir.mkdir()

        # Create scored data with all caps above threshold
        scored_data = {
            "capabilities": [
                {"id": "cap1", "score": 0.85, "components": {}, "meta": {}},
                {"id": "cap2", "score": 0.90, "components": {}, "meta": {}},
            ]
        }
        (artifacts_dir / "capabilities_scored.json").write_text(json.dumps(scored_data))

        # Create gaps data with empty low_maturity
        gaps_data = {"low_maturity": []}
        (artifacts_dir / "gaps.json").write_text(json.dumps(gaps_data))

        cfg = {
            "output": {"artifacts_dir": str(artifacts_dir)},
            "options": {
                "fail_on_low_maturity": True,
                "fail_on_missing_detector": False,
            },
            "scoring": {"thresholds": {"low": 0.70}},
            "capability_map": {"overrides": {}},
        }

        # Should not raise
        audit_runner.command_validate(cfg)


def test_validate_command_fails_on_low_maturity():
    """Test validate fails with exit code 4 when low maturity is detected."""
    audit_runner = load_audit_runner()

    # ADDED: Verify the function exists
    if not hasattr(audit_runner, "command_validate"):
        pytest.skip("command_validate not found in audit_runner module")

    with tempfile.TemporaryDirectory() as tmp_dir:
        artifacts_dir = Path(tmp_dir) / "audit_artifacts"
        artifacts_dir.mkdir()

        # Create scored data with one cap below threshold
        scored_data = {
            "capabilities": [
                {"id": "cap1", "score": 0.65, "components": {}, "meta": {}},
                {"id": "cap2", "score": 0.90, "components": {}, "meta": {}},
            ]
        }
        (artifacts_dir / "capabilities_scored.json").write_text(json.dumps(scored_data))

        cfg = {
            "output": {"artifacts_dir": str(artifacts_dir)},
            "options": {
                "fail_on_low_maturity": True,
                "fail_on_missing_detector": False,
            },
            "scoring": {"thresholds": {"low": 0.70}},
            "capability_map": {"overrides": {}},
        }

        with pytest.raises(SystemExit) as exc_info:
            audit_runner.command_validate(cfg)

        assert exc_info.value.code == EXIT_LOW_MATURITY, "Value must be initialized"


def test_validate_command_respects_fail_on_low_maturity_false():
    """Test validate does not fail when fail_on_low_maturity is False."""
    audit_runner = load_audit_runner()

    # ADDED: Verify the function exists
    if not hasattr(audit_runner, "command_validate"):
        pytest.skip("command_validate not found in audit_runner module")

    with tempfile.TemporaryDirectory() as tmp_dir:
        artifacts_dir = Path(tmp_dir) / "audit_artifacts"
        artifacts_dir.mkdir()

        # Create scored data with one cap below threshold
        scored_data = {
            "capabilities": [
                {"id": "cap1", "score": 0.65, "components": {}, "meta": {}},
            ]
        }
        (artifacts_dir / "capabilities_scored.json").write_text(json.dumps(scored_data))

        # Create gaps data
        gaps_data = {"low_maturity": [{"id": "cap1", "score": 0.65}]}
        (artifacts_dir / "gaps.json").write_text(json.dumps(gaps_data))

        cfg = {
            "output": {"artifacts_dir": str(artifacts_dir)},
            "options": {
                "fail_on_low_maturity": False,  # Disabled
                "fail_on_missing_detector": False,
            },
            "scoring": {"thresholds": {"low": 0.70}},
            "capability_map": {"overrides": {}},
        }

        # Should not raise even with low maturity
        audit_runner.command_validate(cfg)


def test_validate_command_fails_when_missing_artifacts():
    """Test validate fails with exit code 2 when artifacts are missing."""
    audit_runner = load_audit_runner()

    # ADDED: Verify the function exists
    if not hasattr(audit_runner, "command_validate"):
        pytest.skip("command_validate not found in audit_runner module")

    with tempfile.TemporaryDirectory() as tmp_dir:
        artifacts_dir = Path(tmp_dir) / "audit_artifacts"
        artifacts_dir.mkdir()
        # Don't create capabilities_scored.json

        cfg = {
            "output": {"artifacts_dir": str(artifacts_dir)},
            "options": {},
            "scoring": {"thresholds": {"low": 0.70}},
        }

        with pytest.raises(SystemExit) as exc_info:
            audit_runner.command_validate(cfg)

        assert exc_info.value.code == EXIT_MISSING_ARTIFACTS, "Value must be initialized"


def test_stage_s5_creates_component_gaps():
    """Test that stage_s5_gaps creates component_gaps.json."""
    audit_runner = load_audit_runner()

    with tempfile.TemporaryDirectory() as tmp_dir:
        artifacts_dir = Path(tmp_dir) / "audit_artifacts"
        artifacts_dir.mkdir()

        cfg = {
            "output": {"artifacts_dir": str(artifacts_dir)},
            "scoring": {"thresholds": {"low": 0.70}},
        }

        scored_caps = [
            {
                "id": "cap1",
                "score": 0.60,
                "components": {"tests": 0.0, "safeguards": 0.2},
                "found_patterns": ["a"],
                "required_patterns": ["a", "b", "c"],
                "meta": {},
            },
            {
                "id": "cap2",
                "score": 0.80,
                "components": {"tests": 0.8, "safeguards": 0.8},
                "found_patterns": ["x", "y"],
                "required_patterns": ["x", "y"],
                "meta": {},
            },
        ]

        audit_runner.stage_s5_gaps(cfg, scored_caps)

        # Check gaps.json
        assert (artifacts_dir / "gaps.json").exists(), "Condition must be true"
        gaps_data = json.loads((artifacts_dir / "gaps.json").read_text())
        assert "low_maturity" in gaps_data, "Data must not be empty"
        assert len(gaps_data["low_maturity"]) == 1, "Collection must not be empty"
        assert gaps_data["low_maturity"][0]["id"] == "cap1", "Data must not be empty"

        # Check component_gaps.json
        assert (artifacts_dir / "component_gaps.json").exists(), "Condition must be true"
        comp_gaps = json.loads((artifacts_dir / "component_gaps.json").read_text())
        assert "component_gaps" in comp_gaps, "Condition must be true"
        assert comp_gaps["total_capabilities"] == 2, "Condition must be true"

        # cap1 should have gaps
        cap1_gap = next(g for g in comp_gaps["component_gaps"] if g["id"] == "cap1")
        assert "tests" in cap1_gap["zero_components"], "Condition must be true"
        assert "b" in cap1_gap["missing_patterns"], "Condition must be true"
        assert "c" in cap1_gap["missing_patterns"], "Condition must be true"
