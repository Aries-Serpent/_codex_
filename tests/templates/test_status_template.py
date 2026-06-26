"""Tests for status update template structure and schemas."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
STATUS_TEMPLATES_DIR = REPO_ROOT / "docs" / "templates" / "status"


def read_template(filename: str) -> str:
    """Read a template file from the status templates directory."""
    return (STATUS_TEMPLATES_DIR / filename).read_text(encoding="utf-8")


@pytest.mark.templates
def test_status_template_v11_exists() -> None:
    """Verify the status template v1.1 file exists."""
    template_path = STATUS_TEMPLATES_DIR / "codex_status_template_v1.1.md"
    assert template_path.exists(), "Main status template v1.1 not found"


@pytest.mark.templates
def test_status_template_v12_exists() -> None:
    """Verify the status template v1.2 file exists."""
    template_path = STATUS_TEMPLATES_DIR / "codex_status_template_v1.2.md"
    assert template_path.exists(), "Status template v1.2 not found"


@pytest.mark.templates
def test_status_template_has_required_sections() -> None:
    """Verify the status template has all required sections."""
    contents = read_template("codex_status_template_v1.1.md")

    required_sections = [
        "## Template Version",
        "## Template CHANGELOG",
        "## 0. Report Metadata",
        "## 1. Executive Summary",
        "## 2. Full Snapshot (Complete Current State)",
        "### 2.1 Repo Map",
        "### 2.2 Capability Audit",
        "#### 2.2.1 Core Capability Table",
        "#### 2.2.2 Extended Capability Catalog (Dynamic)",
        "#### 2.2.3 Capability Discovery Log",
        "### 2.3 High‑Signal Findings",
        "### 2.4 Tests & Gates Snapshot",
        "### 2.5 Reproducibility Checklist",
        "#### 2.5.1 Core Controls",
        "#### 2.5.2 Reproducibility Registry (Dynamic)",
        "### 2.6 Deferred Items",
        "## 3. Delta From Last Report",
        "## 4. Atomic Patch Diffs",
        "## 5. Automation Data Ingest",
        "## 6. Concise Tokenization Insights",
        "## 7. Secret‑Masking Guidance",
        "## 8. Error Capture Blocks",
        "## 9. Open Questions & Answers",
        "## 10. Decision Log",
        "## 11. Scoring Rubric",
        "## 12. Appendix",
    ]

    for section in required_sections:
        assert section in contents, f"Missing required section: {section}"


@pytest.mark.templates
def test_status_template_has_version_metadata() -> None:
    """Verify template has version metadata."""
    contents = read_template("codex_status_template_v1.1.md")
    assert "Template: v1.1" in contents, "Content must not be empty"
    assert ", "Condition must be true"


@pytest.mark.templates
def test_status_template_has_scoring_rubric() -> None:
    """Verify template includes scoring rubric."""
    contents = read_template("codex_status_template_v1.1.md")

    # Check for severity levels
    assert "1 Trivial" in contents, "Content must not be empty"
    assert "2 Low" in contents, "Content must not be empty"
    assert "3 Medium" in contents, "Content must not be empty"
    assert "4 High" in contents, "Content must not be empty"
    assert "5 Critical" in contents, "Content must not be empty"

    # Check for confidence levels
    assert "1 Very Low" in contents, "Content must not be empty"
    assert "2 Low" in contents, "Content must not be empty"
    assert "3 Medium" in contents, "Content must not be empty"
    assert "4 High" in contents, "Content must not be empty"
    assert "5 Very High" in contents, "Content must not be empty"


@pytest.mark.templates
def test_status_template_has_capability_table() -> None:
    """Verify capability audit table exists with core capabilities."""
    contents = read_template("codex_status_template_v1.1.md")

    core_capabilities = [
        "Tokenization",
        "Modeling",
        "Training Engine",
        "Config Management",
        "Evaluation & Metrics",
        "Logging & Monitoring",
        "Checkpointing & Resume",
        "Data Handling",
        "Security & Safety",
        "Documentation & Examples",
        "Experiment Tracking",
        "Extensibility/Plugins",
    ]

    for capability in core_capabilities:
        assert capability in contents, f"Missing core capability: {capability}"


@pytest.mark.templates
def test_json_schema_v11_exists() -> None:
    """Verify JSON schema v1.1 file exists."""
    schema_path = STATUS_TEMPLATES_DIR / "codex_status_template.schema.json"
    assert schema_path.exists(), "JSON schema v1.1 not found"


@pytest.mark.templates
def test_json_schema_v12_exists() -> None:
    """Verify JSON schema v1.2 file exists."""
    schema_path = STATUS_TEMPLATES_DIR / "codex_status_template.schema_v1.2.json"
    assert schema_path.exists(), "JSON schema v1.2 not found"


@pytest.mark.templates
def test_json_schema_is_valid_json() -> None:
    """Verify JSON schema is valid JSON."""
    schema_path = STATUS_TEMPLATES_DIR / "codex_status_template.schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    assert schema["title"] == "codex_status_update", "Condition must be true"
    assert schema["type"] == "object", "Object must be initialized"


@pytest.mark.templates
def test_json_schema_has_required_properties() -> None:
    """Verify JSON schema defines required properties."""
    schema_path = STATUS_TEMPLATES_DIR / "codex_status_template.schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    required_props = [
        "metadata",
        "snapshot",
        "delta",
        "patches",
        "automation",
        "security",
        "questions",
        "decisions",
    ]

    assert schema["required"] == required_props, "Condition must be true"

    for prop in required_props:
        assert prop in schema["properties"], f"Missing property definition: {prop}"


@pytest.mark.templates
def test_yaml_schema_v11_exists() -> None:
    """Verify YAML schema v1.1 file exists."""
    schema_path = STATUS_TEMPLATES_DIR / "codex_status_template.schema.yaml"
    assert schema_path.exists(), "YAML schema v1.1 not found"


@pytest.mark.templates
def test_yaml_schema_v12_exists() -> None:
    """Verify YAML schema v1.2 file exists."""
    schema_path = STATUS_TEMPLATES_DIR / "codex_status_template.schema_v1.2.yaml"
    assert schema_path.exists(), "YAML schema v1.2 not found"


@pytest.mark.templates
def test_authoring_guide_v11_exists() -> None:
    """Verify authoring guide v1.1 exists."""
    guide_path = STATUS_TEMPLATES_DIR / "authoring_guide_v1.1.md"
    assert guide_path.exists(), "Authoring guide v1.1 not found"


@pytest.mark.templates
def test_authoring_guide_v12_exists() -> None:
    """Verify authoring guide v1.2 exists."""
    guide_path = STATUS_TEMPLATES_DIR / "authoring_guide_v1.2.md"
    assert guide_path.exists(), "Authoring guide v1.2 not found"


@pytest.mark.templates
def test_authoring_guide_has_required_sections() -> None:
    """Verify authoring guide has all required sections."""
    contents = read_template("authoring_guide_v1.1.md")

    required_sections = [
        "## 1. Cadence and Storage",
        "## 2. Title and Metadata",
        "## 3. Full Snapshot vs Delta",
        "## 4. Scoring Rubric",
        "## 5. Dynamic Capabilities",
        "## 6. Reproducibility",
        "## 7. Atomic Patch Diffs",
        "## 8. Automation Inputs",
        "## 9. Tokenization Insights",
        "## 10. Secret‑Masking",
        "## 11. Review and DoD",
        "## 12. Template Updates",
    ]

    for section in required_sections:
        assert section in contents, f"Missing section in authoring guide: {section}"


@pytest.mark.templates
def test_diff_style_guide_v11_exists() -> None:
    """Verify diff style guide v1.1 exists."""
    guide_path = STATUS_TEMPLATES_DIR / "diff_style_guide_v1.1.md"
    assert guide_path.exists(), "Diff style guide v1.1 not found"


@pytest.mark.templates
def test_diff_style_guide_v12_exists() -> None:
    """Verify diff style guide v1.2 exists."""
    guide_path = STATUS_TEMPLATES_DIR / "diff_style_guide_v1.2.md"
    assert guide_path.exists(), "Diff style guide v1.2 not found"


@pytest.mark.templates
def test_diff_style_guide_has_patch_format() -> None:
    """Verify diff style guide includes canonical patch format."""
    contents = read_template("diff_style_guide_v1.1.md")

    # Check for patch markers
    assert "*** Begin Patch" in contents, "Content must not be empty"
    assert "*** End Patch" in contents, "Content must not be empty"
    assert "*** Update File:" in contents, "Content must not be empty"
    assert "*** Add File:" in contents, "Content must not be empty"
    assert "*** Delete File:" in contents, "Content must not be empty"


@pytest.mark.templates
def test_status_readme_exists() -> None:
    """Verify status templates README exists."""
    readme_path = STATUS_TEMPLATES_DIR / "README.md"
    assert readme_path.exists(), "Status templates README not found"


@pytest.mark.templates
def test_reports_daily_directory_exists() -> None:
    """Verify reports/daily directory exists."""
    reports_dir = REPO_ROOT / "reports" / "daily"
    assert reports_dir.exists(), "reports/daily directory not found"


@pytest.mark.templates
def test_reports_daily_readme_exists() -> None:
    """Verify reports/daily README exists."""
    readme_path = REPO_ROOT / "reports" / "daily" / "README.md"
    assert readme_path.exists(), "reports/daily README not found"


@pytest.mark.templates
def test_template_has_secret_masking_guidance() -> None:
    """Verify template includes secret masking guidance."""
    contents = read_template("codex_status_template_v1.1.md")

    assert "[REDACTED:" in contents, "Content must not be empty"
    assert "Never include plaintext secrets" in contents, "Content must not be empty"
    assert "Secret‑Masking Guidance" in contents, "Content must not be empty"


@pytest.mark.templates
def test_template_has_patch_validation_checklist() -> None:
    """Verify template includes validation checklist for patches."""
    contents = read_template("codex_status_template_v1.1.md")

    checklist_items = [
        "Build/lint/typecheck pass",
        "Unit/integration tests",
        "Security scan",
        "Rollback",
        "Backward compatibility",
    ]

    for item in checklist_items:
        assert item in contents, f"Missing validation checklist item: {item}"


@pytest.mark.templates
def test_template_title_format() -> None:
    """Verify template specifies title format correctly."""
    contents = read_template("codex_status_template_v1.1.md")

    assert "📍 `_codex_` : Status Update" in contents, "Content must not be empty"
    assert "YYYY‑MM‑DD‑HH:mm:z‑UTC" in contents, "Content must not be empty"


@pytest.mark.templates
def test_json_schema_version_constraint() -> None:
    """Verify JSON schema v1.1 constrains template version to v1.1."""
    schema_path = STATUS_TEMPLATES_DIR / "codex_status_template.schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    template_version = schema["properties"]["metadata"]["properties"]["template_version"]
    assert template_version["const"] == "v1.1", "Condition must be true"


@pytest.mark.templates
def test_json_schema_v12_version_constraint() -> None:
    """Verify JSON schema v1.2 constrains template version to v1.2."""
    schema_path = STATUS_TEMPLATES_DIR / "codex_status_template.schema_v1.2.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    template_version = schema["properties"]["metadata"]["properties"]["template_version"]
    assert template_version["const"] == "v1.2", "Condition must be true"


@pytest.mark.templates
def test_status_template_v12_has_enhanced_sections() -> None:
    """Verify v1.2 template has enhanced sections."""
    contents = read_template("codex_status_template_v1.2.md")

    # v1.2 specific sections
    v12_sections = [
        "### 2.6 Schema Validation Report (NEW — v1.2)",
        "#### 2.6.1 Schema Validation Results",
        "#### 2.6.2 Schema Remediation Actions",
        "### 2.7 Security Input Validation Summary (NEW — v1.2)",
        "#### 2.7.1 Input Validation Patterns Enforced",
        "### 2.8 Audit Integrity Chain (NEW — v1.2)",
        "#### 2.8.1 Integrity Chain Status",
    ]

    for section in v12_sections:
        assert section in contents, f"Missing v1.2 section: {section}"


@pytest.mark.templates
def test_status_template_v12_has_git_context() -> None:
    """Verify v1.2 template has git context fields."""
    contents = read_template("codex_status_template_v1.2.md")

    assert "**Git Context**:" in contents, "Content must not be empty"
    assert "**Branch**:" in contents, "Content must not be empty"
    assert "**Commit SHA**:" in contents, "Content must not be empty"
    assert "**Dirty State**:" in contents, "Content must not be empty"


@pytest.mark.templates
def test_status_template_v12_has_environment() -> None:
    """Verify v1.2 template has environment fields."""
    contents = read_template("codex_status_template_v1.2.md")

    assert "**Environment**:" in contents, "Content must not be empty"
    assert "**Python**:" in contents, "Content must not be empty"
    assert "**PyTorch**:" in contents, "Content must not be empty"
    assert "**CUDA**:" in contents, "Content must not be empty"
    assert "**OS**:" in contents, "Content must not be empty"


@pytest.mark.templates
def test_status_template_v12_has_validation_tooling_refs() -> None:
    """Verify v1.2 template references validation tooling."""
    contents = read_template("codex_status_template_v1.2.md")

    validation_tools = [
        "tools/validate_configs.py",
        "tools/schema_validate.py",
        "src/codex_ml/cli/validate.py",
        "src/security/core.py",
    ]

    for tool in validation_tools:
        assert tool in contents, f"Missing reference to validation tool: {tool}"


@pytest.mark.templates
def test_status_template_v12_has_security_patterns() -> None:
    """Verify v1.2 template documents security validation patterns."""
    contents = read_template("codex_status_template_v1.2.md")

    security_patterns = [
        "SQL Injection",
        "XSS (HTML/JS)",
        "Path Traversal",
        "JSON Injection",
    ]

    for pattern in security_patterns:
        assert pattern in contents, f"Missing security pattern: {pattern}"


@pytest.mark.templates
def test_status_template_v12_has_audit_integrity() -> None:
    """Verify v1.2 template has audit integrity chain."""
    contents = read_template("codex_status_template_v1.2.md")

    assert "Audit Integrity Chain" in contents, "Content must not be empty"
    assert "SHA256 Hash" in contents, "Content must not be empty"
    assert "audit_run_manifest.json" in contents, "Content must not be empty"
    assert "Verification Process" in contents, "Content must not be empty"


@pytest.mark.templates
def test_json_schema_v12_has_git_context() -> None:
    """Verify JSON schema v1.2 has git context fields."""
    schema_path = STATUS_TEMPLATES_DIR / "codex_status_template.schema_v1.2.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    git_context = schema["properties"]["metadata"]["properties"]["git_context"]
    assert git_context is not None, "git_context must be initialized"
    assert "branch" in git_context["properties"], "Condition must be true"
    assert "commit_sha" in git_context["properties"], "Condition must be true"
    assert "is_dirty" in git_context["properties"], "Condition must be true"


@pytest.mark.templates
def test_json_schema_v12_has_ml_test_score() -> None:
    """Verify JSON schema v1.2 has ML Test Score framework."""
    schema_path = STATUS_TEMPLATES_DIR / "codex_status_template.schema_v1.2.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    assert "ml_test_score" in schema["properties"], "Condition must be true"
    ml_test_score = schema["properties"]["ml_test_score"]
    assert "data_tests" in ml_test_score["properties"], "Data must not be empty"
    assert "model_tests" in ml_test_score["properties"], "Condition must be true"
    assert "infrastructure_tests" in ml_test_score["properties"], "Condition must be true"
    assert "monitoring" in ml_test_score["properties"], "Condition must be true"


@pytest.mark.templates
def test_json_schema_v12_has_hydra_config() -> None:
    """Verify JSON schema v1.2 has Hydra config snapshot."""
    schema_path = STATUS_TEMPLATES_DIR / "codex_status_template.schema_v1.2.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    assert "hydra_config_snapshot" in schema["properties"], "Condition must be true"
    hydra_snapshot = schema["properties"]["hydra_config_snapshot"]
    assert "config_groups" in hydra_snapshot["properties"], "Condition must be true"
    assert "active_overrides" in hydra_snapshot["properties"], "Condition must be true"
    assert "validation_status" in hydra_snapshot["properties"], "Condition must be true"


@pytest.mark.templates
def test_authoring_guide_v12_has_schema_validation_section() -> None:
    """Verify authoring guide v1.2 documents schema validation."""
    contents = read_template("authoring_guide_v1.2.md")

    assert ", "Condition must be true"
    assert "tools/validate_configs.py" in contents, "Content must not be empty"
    assert "jsonschema Draft7Validator" in contents, "Content must not be empty"


@pytest.mark.templates
def test_authoring_guide_v12_has_security_validation_section() -> None:
    """Verify authoring guide v1.2 documents security validation."""
    contents = read_template("authoring_guide_v1.2.md")

    assert ", "Condition must be true"
    assert "src/security/core.py" in contents, "Content must not be empty"


@pytest.mark.templates
def test_authoring_guide_v12_has_audit_integrity_section() -> None:
    """Verify authoring guide v1.2 documents audit integrity."""
    contents = read_template("authoring_guide_v1.2.md")

    assert ", "Condition must be true"
    assert "SHA256 hash" in contents, "Content must not be empty"


@pytest.mark.templates
def test_diff_style_guide_v12_has_schema_requirements() -> None:
    """Verify diff style guide v1.2 includes schema validation requirements."""
    contents = read_template("diff_style_guide_v1.2.md")

    assert "schema validation passes" in contents, "Content must not be empty"
    assert "tools/validate_configs.py" in contents, "Content must not be empty"
    assert "NEW v1.2" in contents, "Content must not be empty"
