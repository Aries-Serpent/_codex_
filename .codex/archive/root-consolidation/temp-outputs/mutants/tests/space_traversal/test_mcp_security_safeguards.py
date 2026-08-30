"""
Tests for MCP security safeguards detector.

Tests detection of security patterns like confirmation prompts, dry-run modes, sanitization, etc.
"""

import tempfile
from pathlib import Path

from scripts.space_traversal.detectors import mcp_security_safeguards


def test_detect_no_safeguards():
    """Test detection with no security safeguards."""
    file_index = {
        "files": [
            {"path": "src/app/main.py"},
            {"path": "src/app/utils.py"},
        ]
    }

    result = mcp_security_safeguards.detect(file_index)

    assert result["id"] == "mcp-security-safeguards", "Result must not be empty"
    assert result["found_patterns"] == [], "Result must not be empty"
    assert "confirm" in result["required_patterns"], "Result must not be empty"
    assert "dry_run" in result["required_patterns"], "Result must not be empty"


def test_detect_confirm_keyword():
    """Test detection of confirmation prompts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        py_file = Path(tmpdir) / "cli.py"
        py_file.write_text("""
def delete_resource(resource_id, confirm=False):
    if not confirm:
        logger.info("Please confirm deletion")
        return
    # Delete logic here
""")

        file_index = {"files": [{"path": str(py_file)}]}

        result = mcp_security_safeguards.detect(file_index)

        assert "confirm" in result["found_patterns"], "Result must not be empty"
        assert str(py_file) in result["evidence_files"], "Result must not be empty"


def test_detect_dry_run_keyword():
    """Test detection of dry-run mode."""
    with tempfile.TemporaryDirectory() as tmpdir:
        py_file = Path(tmpdir) / "deploy.py"
        py_file.write_text("""
def deploy(config, dry_run=False):
    if dry_run:
        logger.info("DRY RUN: Would deploy...")
        return
    # Actual deployment
""")

        file_index = {"files": [{"path": str(py_file)}]}

        result = mcp_security_safeguards.detect(file_index)

        assert "dry_run" in result["found_patterns"], "Result must not be empty"
        assert str(py_file) in result["evidence_files"], "Result must not be empty"


def test_detect_sanitize_keyword():
    """Test detection of sanitization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        py_file = Path(tmpdir) / "input.py"
        py_file.write_text("""
def process_input(data):
    # Sanitize user input
    sanitized = sanitize(data)
    return sanitized
""")

        file_index = {"files": [{"path": str(py_file)}]}

        result = mcp_security_safeguards.detect(file_index)

        assert "sanitize" in result["found_patterns"], "Result must not be empty"
        assert str(py_file) in result["evidence_files"], "Result must not be empty"


def test_detect_validation_keyword():
    """Test detection of validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        py_file = Path(tmpdir) / "validator.py"
        py_file.write_text("""
def validate_config(config):
    # Perform validation
    if not is_valid(config):
        raise ValueError("Invalid config")
""")

        file_index = {"files": [{"path": str(py_file)}]}

        result = mcp_security_safeguards.detect(file_index)

        assert "validation" in result["found_patterns"], "Result must not be empty"
        assert str(py_file) in result["evidence_files"], "Result must not be empty"


def test_detect_bounds_keyword():
    """Test detection of bounds checking."""
    with tempfile.TemporaryDirectory() as tmpdir:
        py_file = Path(tmpdir) / "array.py"
        py_file.write_text("""
def get_item(array, index):
    # Check bounds before access
    if index < 0 or index >= len(array):
        raise IndexError("Out of bounds")
    return array[index]
""")

        file_index = {"files": [{"path": str(py_file)}]}

        result = mcp_security_safeguards.detect(file_index)

        assert "bounds" in result["found_patterns"], "Result must not be empty"
        assert str(py_file) in result["evidence_files"], "Result must not be empty"


def test_detect_rollback_keyword():
    """Test detection of rollback capability."""
    with tempfile.TemporaryDirectory() as tmpdir:
        py_file = Path(tmpdir) / "transaction.py"
        py_file.write_text("""
def update_database(conn, data):
    try:
        conn.execute(data)
        conn.commit()
    except (AssertionError, ValueError, TypeError, RuntimeError):  # noqa: BLE001
        conn.rollback()
        raise
""")

        file_index = {"files": [{"path": str(py_file)}]}

        result = mcp_security_safeguards.detect(file_index)

        assert "rollback" in result["found_patterns"], "Result must not be empty"
        assert str(py_file) in result["evidence_files"], "Result must not be empty"


def test_detect_in_markdown():
    """Test detection of safeguards in markdown documentation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        md_file = Path(tmpdir) / "security.md"
        md_file.write_text("""
# Security Safeguards

Always use the `--confirm` flag for destructive operations.
Enable `--dry-run` mode to preview changes.
All inputs are sanitized before processing.
""")

        file_index = {"files": [{"path": str(md_file)}]}

        result = mcp_security_safeguards.detect(file_index)

        # Should find all three keywords in markdown
        assert "confirm" in result["found_patterns"], "Result must not be empty"
        assert "dry" in result["found_patterns"] or "dry_run" in result["found_patterns"], "Result must not be empty"
        assert "sanitize" in result["found_patterns"], "Result must not be empty"


def test_detect_multiple_safeguards():
    """Test detection of multiple safeguards in single file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        py_file = Path(tmpdir) / "secure_api.py"
        py_file.write_text("""
def secure_operation(data, confirm=False, dry_run=False):
    # Sanitize input
    data = sanitize(data)

    # Validate
    if not validate(data):
        return False

    # Check bounds
    if len(data) > MAX_SIZE:
        return False

    # Confirm before action
    if not confirm:
        return prompt_user()

    # Support dry-run
    if dry_run:
        return simulate(data)

    try:
        execute(data)
    except (AssertionError, ValueError, TypeError, RuntimeError):  # noqa: BLE001
        rollback()
""")

        file_index = {"files": [{"path": str(py_file)}]}

        result = mcp_security_safeguards.detect(file_index)

        # Should find all keywords
        assert "confirm" in result["found_patterns"], "Result must not be empty"
        assert "dry_run" in result["found_patterns"], "Result must not be empty"
        assert "sanitize" in result["found_patterns"], "Result must not be empty"
        assert "validation" in result["found_patterns"] or "validate" in result["found_patterns"]
        assert "bounds" in result["found_patterns"], "Result must not be empty"
        assert "rollback" in result["found_patterns"], "Result must not be empty"


def test_evidence_deduplication():
    """Test that evidence files are deduplicated."""
    with tempfile.TemporaryDirectory() as tmpdir:
        py_file = Path(tmpdir) / "app.py"
        py_file.write_text("""
confirm = True
dry_run = False
sanitize(data)
""")

        file_index = {"files": [{"path": str(py_file)}]}

        result = mcp_security_safeguards.detect(file_index)

        # File should appear only once even with multiple keywords
        assert len(result["evidence_files"]) == len(set(result["evidence_files"])), "Collection must not be empty"


def test_sorted_output():
    """Test that output lists are sorted."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = Path(tmpdir) / "z_file.py"
        file1.write_text("confirm = True")

        file2 = Path(tmpdir) / "a_file.py"
        file2.write_text("dry_run = False")

        file_index = {
            "files": [
                {"path": str(file1)},
                {"path": str(file2)},
            ]
        }

        result = mcp_security_safeguards.detect(file_index)

        # found_patterns should be sorted
        assert result["found_patterns"] == sorted(result["found_patterns"]), "Result must not be empty"
        # evidence_files should be sorted
        assert result["evidence_files"] == sorted(result["evidence_files"]), "Result must not be empty"


def test_docs_keywords_present():
    """Test that required docs_keywords are present."""
    file_index = {"files": []}

    result = mcp_security_safeguards.detect(file_index)

    assert "docs_keywords" in result, "Result must not be empty"
    expected_keywords = [
        "mcp",
        "security",
        "safeguards",
        "validation",
        "sanitization",
        "confirm",
        "dry-run",
        "defensive",
    ]
    for keyword in expected_keywords:
        assert keyword in result["docs_keywords"], "Result must not be empty"


def test_safeguards_metadata():
    """Test that safeguards metadata is present."""
    file_index = {"files": []}

    result = mcp_security_safeguards.detect(file_index)

    assert "meta" in result, "Result must not be empty"
    assert "safeguards" in result["meta"], "Result must not be empty"
    expected_safeguards = [
        "confirmation",
        "dry-run",
        "sanitization",
        "validation",
        "bounds-checking",
        "rollback",
    ]
    for safeguard in expected_safeguards:
        assert safeguard in result["meta"]["safeguards"], "Result must not be empty"


def test_detector_version():
    """Test that detector version is present."""
    file_index = {"files": []}

    result = mcp_security_safeguards.detect(file_index)

    assert "detector_version" in result["meta"], "Result must not be empty"
    assert result["meta"]["detector_version"] == "1.2", "Result must not be empty"


def test_category_mcp():
    """Test that category is set to MCP."""
    file_index = {"files": []}

    result = mcp_security_safeguards.detect(file_index)

    assert result["meta"]["category"] == "mcp", "Result must not be empty"


def test_non_python_non_md_ignored():
    """Test that non-Python/non-MD files are ignored."""
    file_index = {
        "files": [
            {"path": "data.json"},
            {"path": "config.yaml"},
            {"path": "image.png"},
        ]
    }

    result = mcp_security_safeguards.detect(file_index)

    # Should not process these files
    assert result["found_patterns"] == [], "Result must not be empty"
    assert result["evidence_files"] == [], "Result must not be empty"


def test_file_read_error_handling():
    """Test graceful handling of file read errors."""
    file_index = {
        "files": [
            {"path": "/nonexistent/file.py"},
        ]
    }

    # Should not crash on file read error
    result = mcp_security_safeguards.detect(file_index)

    assert result["id"] == "mcp-security-safeguards", "Result must not be empty"


def test_empty_file_index():
    """Test detection with empty file index."""
    file_index = {"files": []}

    result = mcp_security_safeguards.detect(file_index)

    assert result["id"] == "mcp-security-safeguards", "Result must not be empty"
    assert result["found_patterns"] == [], "Result must not be empty"
    assert result["evidence_files"] == [], "Result must not be empty"


def test_deterministic_output():
    """Test that detector produces deterministic output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        py_file = Path(tmpdir) / "app.py"
        py_file.write_text("confirm = True\ndry_run = False")

        file_index = {"files": [{"path": str(py_file)}]}

        # Run detection multiple times
        results = [mcp_security_safeguards.detect(file_index) for _ in range(3)]

        # All results should be identical
        for i in range(1, len(results)):
            assert results[i]["found_patterns"] == results[0]["found_patterns"], "Result must not be empty"
            assert results[i]["evidence_files"] == results[0]["evidence_files"], "Result must not be empty"
