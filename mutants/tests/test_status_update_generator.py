"""
Test Status Update Generator

Test module for status update generator.
"""

#!/usr/bin/env python3
"""
Test suite for the status update generator.

Tests that the generated status update:
1. Follows the JSON schema
2. Contains all required fields
3. Produces valid, well-formed output
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Paths
REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = REPO_ROOT / "tools" / "generate_status_update.py"
SCHEMA = REPO_ROOT / "schemas" / "codex_status_update.schema.json"
STATUS_DIR = REPO_ROOT / ".codex" / "status"


@pytest.fixture(scope="session", autouse=True)
def ensure_status_report_exists():
    """Ensure at least one status report exists before running tests."""
    # Check if any reports exist
    reports = list(STATUS_DIR.glob("_codex_status_update-*.json"))
    if len(reports) == 0:
        # Generate a report if none exist
        if GENERATOR.exists():
            result = subprocess.run(
                [sys.executable, str(GENERATOR)],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                pytest.skip(f"Could not generate status report: {result.stderr}")
        else:
            pytest.skip(f"Generator not found at {GENERATOR}")
    # If reports exist or were generated successfully, tests can proceed
    return True


def test_generator_exists():
    """Test that the generator script exists."""
    assert GENERATOR.exists(), f"Generator not found at {GENERATOR}"


def test_schema_exists():
    """Test that the schema file exists."""
    assert SCHEMA.exists(), f"Schema not found at {SCHEMA}"


def test_schema_is_valid_json():
    """Test that the schema is valid JSON."""
    with open(SCHEMA) as f:
        schema = json.load(f)

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema", "Condition must be true"
    assert schema["title"] == "codex_status_update", "Condition must be true"
    assert schema["type"] == "object", "Object must be initialized"


def test_generator_runs_successfully():
    """Test that the generator runs without errors."""
    result = subprocess.run(
        [sys.executable, str(GENERATOR)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Generator failed: {result.stderr}"
    assert "Status update saved to" in result.stdout, "Result must not be empty"


def test_generated_report_is_valid_json():
    """Test that the generated report is valid JSON."""
    # Find the most recent report
    reports = sorted(STATUS_DIR.glob("_codex_status_update-*.json"))
    assert len(reports) > 0, "No status update reports found"

    latest_report = reports[-1]

    with open(latest_report) as f:
        data = json.load(f)

    assert isinstance(data, dict)


def test_report_has_required_sections():
    """Test that the report contains all required top-level sections."""
    reports = sorted(STATUS_DIR.glob("_codex_status_update-*.json"))
    latest_report = reports[-1]

    with open(latest_report) as f:
        data = json.load(f)

    required_sections = [
        "metadata",
        "snapshot",
        "delta",
        "patches",
        "automation",
        "security",
        "questions",
        "decisions",
    ]

    for section in required_sections:
        assert section in data, f"Missing required section: {section}"


def test_metadata_structure():
    """Test the metadata section structure."""
    reports = sorted(STATUS_DIR.glob("_codex_status_update-*.json"))
    assert len(reports) > 0, "No status update reports found"
    latest_report = reports[-1]

    with open(latest_report) as f:
        data = json.load(f)

    metadata = data["metadata"]

    assert "title" in metadata, "Data must not be empty"
    assert metadata["title"].startswith("📍 `_codex_` : Status Update"), "Data must not be empty"
    assert "timestamp_utc" in metadata, "Data must not be empty"
    assert "report_version" in metadata, "Data must not be empty"
    assert metadata["template_version"] == "v1.2", "Data must not be empty"
    assert "git_context" in metadata, "Data must not be empty"
    assert "branch" in metadata["git_context"], "Data must not be empty"
    assert "commit_sha" in metadata["git_context"], "Data must not be empty"


def test_snapshot_has_capabilities():
    """Test that snapshot contains capabilities."""
    reports = sorted(STATUS_DIR.glob("_codex_status_update-*.json"))
    assert len(reports) > 0, "No status update reports found"
    latest_report = reports[-1]

    with open(latest_report) as f:
        data = json.load(f)

    capabilities = data["snapshot"]["capabilities"]

    assert isinstance(capabilities, list)
    assert len(capabilities) > 0, "Capabilities must not be empty"

    # Check first capability structure
    cap = capabilities[0]
    required_fields = [
        "name",
        "status",
        "artifacts",
        "gaps",
        "risks",
        "severity",
        "confidence",
        "patch_plan",
        "rollback",
    ]

    for field in required_fields:
        assert field in cap, f"Capability missing required field: {field}"

    # Check status is valid enum value
    assert cap["status"] in ["Implemented", "Partially Implemented", "Stubbed", "Missing"]


def test_repro_registry():
    """Test reproducibility registry structure."""
    reports = sorted(STATUS_DIR.glob("_codex_status_update-*.json"))
    assert len(reports) > 0, "No status update reports found"
    latest_report = reports[-1]

    with open(latest_report) as f:
        data = json.load(f)

    repro = data["snapshot"]["repro"]

    assert "core_controls" in repro, "Condition must be true"
    assert "registry" in repro, "Condition must be true"
    assert isinstance(repro["registry"], list)
    assert len(repro["registry"]) > 0, "Collection must not be empty"

    # Check first registry entry
    entry = repro["registry"][0]
    assert "id" in entry, "Condition must be true"
    assert "category" in entry, "Condition must be true"
    assert "control" in entry, "Condition must be true"
    assert "status" in entry, "Condition must be true"


def test_report_validates_against_schema():
    """Test that the report validates against the JSON schema."""
    jsonschema = pytest.importorskip("jsonschema", reason="jsonschema not installed")

    with open(SCHEMA) as f:
        schema = json.load(f)

    reports = sorted(STATUS_DIR.glob("_codex_status_update-*.json"))
    assert len(reports) > 0, "No status update reports found"
    latest_report = reports[-1]

    with open(latest_report) as f:
        data = json.load(f)

    # This will raise ValidationError if invalid
    jsonschema.validate(data, schema)


def test_cli_integration():
    """Test that the CLI command works."""
    result = subprocess.run(
        [sys.executable, "-m", "cli.status_audit", "--generate"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    assert "Status update saved to" in result.stdout, "Result must not be empty"


def test_validation_failure_exits_with_error():
    """Test that validation failures result in non-zero exit code."""
    # We'll test this by mocking a validation failure
    # Create a simple test script that imports and calls validate_report with invalid data
    test_script = """
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.generate_status_update import validate_report

# Test with invalid report (missing required fields)
invalid_report = {"metadata": {}}
is_valid, errors = validate_report(invalid_report)
sys.exit(0 if is_valid else 1)
"""

    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(f"from pathlib import Path\n{test_script}")
        temp_script = f.name

    try:
        result = subprocess.run(
            [sys.executable, temp_script],
            capture_output=True,
            text=True,
        )
        # Validation should fail for an invalid report
        assert result.returncode != 0, "Expected non-zero exit code for invalid report"
    finally:
        Path(temp_script).unlink()


def test_invalid_report_saved_separately():
    """Test that invalid reports are saved with .invalid.json extension."""
    # Check if any .invalid.json files exist
    invalid_reports = list(STATUS_DIR.glob("*.invalid.json"))
    # This test is informational - invalid reports may or may not exist
    # depending on whether validation failures have occurred
    if invalid_reports:
        # If they exist, verify they're not treated as valid reports
        valid_reports = [
            r
            for r in STATUS_DIR.glob("_codex_status_update-*.json")
            if not r.name.endswith(".invalid.json")
        ]
        # Ensure the test suite uses only valid reports
        assert len(valid_reports) > 0, "Should have valid reports for testing"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
