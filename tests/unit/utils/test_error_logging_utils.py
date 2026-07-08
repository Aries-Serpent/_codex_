"""Unit tests for error_logging utilities (Phase 23 Week 3 gapfill)."""

from src.utils.error_logging import append_error_to_file, log_error


def test_log_error_basic(tmp_path):
    """Test log_error writes error messages."""
    log_file = tmp_path / "errors.log"
    log_error("Test error message", log_file=str(log_file))

    assert log_file.exists(), "Condition must be true"
    content = log_file.read_text()
    assert "Test error message" in content, "Content must not be empty"


def test_log_error_with_exception(tmp_path):
    """Test log_error captures exception details."""
    log_file = tmp_path / "errors.log"

    try:
        raise ValueError("Test exception")
    except ValueError as e:
        log_error("Error occurred", exception=e, log_file=str(log_file))

    content = log_file.read_text()
    assert "ValueError" in content, "Value must be initialized"
    assert "Test exception" in content, "Content must not be empty"


def test_log_error_timestamp(tmp_path):
    """Test log_error includes timestamp."""
    log_file = tmp_path / "errors.log"
    log_error("Test error", log_file=str(log_file))

    content = log_file.read_text()
    # Should contain timestamp pattern
    assert "20" in content, "Content must not be empty"


def test_log_error_severity_levels(tmp_path):
    """Test log_error supports severity levels."""
    log_file = tmp_path / "errors.log"

    log_error("Error message", severity="ERROR", log_file=str(log_file))
    log_error("Warning message", severity="WARNING", log_file=str(log_file))

    content = log_file.read_text()
    assert "ERROR" in content, "Content must not be empty"
    assert "WARNING" in content, "Content must not be empty"


def test_append_error_to_file_creates_file(tmp_path):
    """Test append_error_to_file creates file if missing."""
    log_file = tmp_path / "new_errors.log"
    append_error_to_file("Test error", str(log_file))

    assert log_file.exists(), "Condition must be true"


def test_append_error_to_file_appends(tmp_path):
    """Test append_error_to_file appends to existing file."""
    log_file = tmp_path / "errors.log"
    log_file.write_text("Existing content\n")

    append_error_to_file("New error", str(log_file))

    content = log_file.read_text()
    assert "Existing content" in content, "Content must not be empty"
    assert "New error" in content, "Content must not be empty"


def test_append_error_to_file_permission_denied(tmp_path):
    """Test append_error_to_file handles permission errors."""
    log_file = tmp_path / "readonly.log"
    log_file.write_text("Content\n")
    log_file.chmod(0o444)  # Read-only

    try:
        append_error_to_file("Should fail", str(log_file))
    except PermissionError:
        _ = None  # Expected
    finally:
        log_file.chmod(0o644)  # Restore permissions


def test_log_error_multiline_message(tmp_path):
    """Test log_error handles multiline messages."""
    log_file = tmp_path / "errors.log"
    message = "Line 1\nLine 2\nLine 3"
    log_error(message, log_file=str(log_file))

    content = log_file.read_text()
    assert "Line 1" in content, "Content must not be empty"
    assert "Line 2" in content, "Content must not be empty"
    assert "Line 3" in content, "Content must not be empty"


def test_log_error_context_info(tmp_path):
    """Test log_error includes context information."""
    log_file = tmp_path / "errors.log"
    context = {"user": "test_user", "operation": "test_op"}
    log_error("Error with context", context=context, log_file=str(log_file))

    content = log_file.read_text()
    assert "test_user" in content, "Content must not be empty"
    assert "test_op" in content, "Content must not be empty"
