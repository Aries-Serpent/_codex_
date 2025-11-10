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
    
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["title"] == "codex_status_update"
    assert schema["type"] == "object"


def test_generator_runs_successfully():
    """Test that the generator runs without errors."""
    result = subprocess.run(
        [sys.executable, str(GENERATOR)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    
    assert result.returncode == 0, f"Generator failed: {result.stderr}"
    assert "Status update saved to" in result.stdout


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
    latest_report = reports[-1]
    
    with open(latest_report) as f:
        data = json.load(f)
    
    metadata = data["metadata"]
    
    assert "title" in metadata
    assert metadata["title"].startswith("📍 `_codex_` : Status Update")
    assert "timestamp_utc" in metadata
    assert "report_version" in metadata
    assert metadata["template_version"] == "v1.2"
    assert "git_context" in metadata
    assert "branch" in metadata["git_context"]
    assert "commit_sha" in metadata["git_context"]


def test_snapshot_has_capabilities():
    """Test that snapshot contains capabilities."""
    reports = sorted(STATUS_DIR.glob("_codex_status_update-*.json"))
    latest_report = reports[-1]
    
    with open(latest_report) as f:
        data = json.load(f)
    
    capabilities = data["snapshot"]["capabilities"]
    
    assert isinstance(capabilities, list)
    assert len(capabilities) > 0
    
    # Check first capability structure
    cap = capabilities[0]
    required_fields = [
        "name", "status", "artifacts", "gaps", "risks",
        "severity", "confidence", "patch_plan", "rollback"
    ]
    
    for field in required_fields:
        assert field in cap, f"Capability missing required field: {field}"
    
    # Check status is valid enum value
    assert cap["status"] in ["Implemented", "Partially Implemented", "Stubbed", "Missing"]


def test_repro_registry():
    """Test reproducibility registry structure."""
    reports = sorted(STATUS_DIR.glob("_codex_status_update-*.json"))
    latest_report = reports[-1]
    
    with open(latest_report) as f:
        data = json.load(f)
    
    repro = data["snapshot"]["repro"]
    
    assert "core_controls" in repro
    assert "registry" in repro
    assert isinstance(repro["registry"], list)
    assert len(repro["registry"]) > 0
    
    # Check first registry entry
    entry = repro["registry"][0]
    assert "id" in entry
    assert "category" in entry
    assert "control" in entry
    assert "status" in entry


@pytest.mark.skipif(
    not pytest.importorskip("jsonschema", reason="jsonschema not installed"),
    reason="jsonschema not available"
)
def test_report_validates_against_schema():
    """Test that the report validates against the JSON schema."""
    import jsonschema
    
    with open(SCHEMA) as f:
        schema = json.load(f)
    
    reports = sorted(STATUS_DIR.glob("_codex_status_update-*.json"))
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
        timeout=60,
    )
    
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    assert "Status update saved to" in result.stdout


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
