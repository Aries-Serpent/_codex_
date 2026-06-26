"""
Tests for status_reporting detector (v1.4.0)
"""

from scripts.space_traversal.detectors.status_reporting import detect


def test_status_reporting_detector_basic():
    """Test basic status reporting detection."""
    file_index = {
        "files": [
            {"path": "scripts/status/codex_status.py", "ext": ".py"},
            {"path": "scripts/audit/audit_report.py", "ext": ".py"},
            {"path": "src/reporting/status_update.py", "ext": ".py"},
        ]
    }

    result = detect(file_index)

    assert result["id"] == "status-reporting", "Result must not be empty"
    assert len(result["evidence_files"]) > 0, "Collection must not be empty"
    assert "status" in result["found_patterns"] or "report" in result["found_patterns"], "Result must not be empty"
    assert result["required_patterns"] == ["status", "report", "audit"]
    assert result["meta"]["layer"] == "operations", "Result must not be empty"


def test_status_reporting_detector_no_evidence():
    """Test status reporting detector with no evidence."""
    file_index = {"files": [{"path": "src/utils/helper.py", "ext": ".py"}]}

    result = detect(file_index)

    assert result["id"] == "status-reporting", "Result must not be empty"
    assert len(result["evidence_files"]) == 0, "Collection must not be empty"
    assert len(result["found_patterns"]) == 0, "Collection must not be empty"


def test_status_reporting_detector_audit_patterns():
    """Test status reporting detector with audit patterns."""
    file_index = {
        "files": [
            {"path": "scripts/audit/audit_runner.py", "ext": ".py"},
            {"path": "templates/audit/report.md.j2", "ext": ".j2"},
        ]
    }

    result = detect(file_index)

    assert result["id"] == "status-reporting", "Result must not be empty"
    assert "audit" in result["found_patterns"], "Result must not be empty"
    assert "report" in result["found_patterns"], "Result must not be empty"
    assert len(result["evidence_files"]) > 0, "Collection must not be empty"


def test_status_reporting_detector_sorted_output():
    """Test that detector returns sorted results."""
    file_index = {
        "files": [
            {"path": "z_status.py", "ext": ".py"},
            {"path": "a_audit.py", "ext": ".py"},
            {"path": "m_report.py", "ext": ".py"},
        ]
    }

    result = detect(file_index)

    # Check that evidence files are sorted
    assert result["evidence_files"] == sorted(result["evidence_files"]), "Result must not be empty"
    # Check that found patterns are sorted
    assert result["found_patterns"] == sorted(result["found_patterns"]), "Result must not be empty"
