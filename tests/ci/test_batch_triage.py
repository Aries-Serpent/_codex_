"""
Tests for Batch CI Failure Triage Tool

Tests the batch triage functionality without requiring GitHub API access.
"""

import json
import pytest
from pathlib import Path
import sys

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).resolve().parent.parent.parent / "scripts" / "ci"
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from batch_triage import (
        FailureRecord,
        TriageGroup,
        BatchTriageEngine
    )
except ImportError:
    pytest.skip("batch_triage module not available", allow_module_level=True)


def test_failure_record_creation():
    """Test FailureRecord creation and serialization"""
    failure = FailureRecord(
        issue_number=2905,
        issue_url="https://github.com/Aries-Serpent/_codex_/issues/2905",
        workflow_run_id="21145572518",
        analysis_run_id="21145604149"
    )
    
    assert failure.issue_number == 2905
    assert failure.workflow_run_id == "21145572518"
    
    # Test serialization
    data = failure.to_dict()
    assert data['issue_number'] == 2905
    assert data['workflow_run_id'] == "21145572518"


def test_triage_group_creation():
    """Test TriageGroup creation and serialization"""
    failures = [
        FailureRecord(
            issue_number=2905,
            issue_url="https://github.com/Aries-Serpent/_codex_/issues/2905",
            workflow_run_id="21145572518"
        ),
        FailureRecord(
            issue_number=2906,
            issue_url="https://github.com/Aries-Serpent/_codex_/issues/2906",
            workflow_run_id="21145592938"
        )
    ]
    
    group = TriageGroup(
        group_id="group_1",
        root_cause="Test failure",
        severity="high",
        failure_count=2,
        failures=failures,
        common_patterns=["pattern1", "pattern2"],
        remediation_suggestions=["suggestion1", "suggestion2"]
    )
    
    assert group.failure_count == 2
    assert len(group.failures) == 2
    assert group.severity == "high"
    
    # Test serialization
    data = group.to_dict()
    assert data['failure_count'] == 2
    assert len(data['failures']) == 2


def test_batch_triage_engine_initialization():
    """Test BatchTriageEngine initialization"""
    engine = BatchTriageEngine(repo="Aries-Serpent/_codex_")
    
    assert engine.owner == "Aries-Serpent"
    assert engine.repo_name == "_codex_"
    assert engine.failures == []
    assert engine.groups == []


def test_extract_run_id():
    """Test workflow run ID extraction from URLs"""
    engine = BatchTriageEngine()
    
    url1 = "https://github.com/Aries-Serpent/_codex_/actions/runs/21145572518"
    assert engine._extract_run_id(url1) == "21145572518"
    
    url2 = "https://github.com/owner/repo/actions/runs/123456789"
    assert engine._extract_run_id(url2) == "123456789"
    
    assert engine._extract_run_id("") is None
    assert engine._extract_run_id("invalid") is None


def test_classify_failure_type():
    """Test failure type classification from logs"""
    engine = BatchTriageEngine()
    
    # Test failure
    logs1 = "FAILED tests/test_example.py::test_function"
    assert engine._classify_failure_type(logs1) == "test_failure"
    
    # Import error
    logs2 = "ModuleNotFoundError: No module named 'pytest'"
    assert engine._classify_failure_type(logs2) == "import_error"
    
    # Syntax error
    logs3 = "SyntaxError: invalid syntax"
    assert engine._classify_failure_type(logs3) == "syntax_error"
    
    # Build failure
    logs4 = "Build failed: error in compilation"
    assert engine._classify_failure_type(logs4) == "build_failure"
    
    # Unknown
    logs5 = "Some other error"
    assert engine._classify_failure_type(logs5) == "unknown"


def test_extract_root_cause():
    """Test root cause extraction from logs"""
    engine = BatchTriageEngine()
    
    # Test failure
    logs1 = "FAILED tests/test_example.py::test_function - AssertionError"
    root_cause1 = engine._extract_root_cause(logs1)
    assert "test_function" in root_cause1
    
    # Module not found
    logs2 = "ModuleNotFoundError: No module named 'pytest-timeout'"
    root_cause2 = engine._extract_root_cause(logs2)
    assert "pytest-timeout" in root_cause2
    
    # Unknown
    logs3 = "Random error message"
    root_cause3 = engine._extract_root_cause(logs3)
    assert "Unknown root cause" in root_cause3


def test_grouping_by_root_cause():
    """Test grouping failures by root cause"""
    engine = BatchTriageEngine()
    
    # Add failures with different root causes
    failure1 = FailureRecord(
        issue_number=2905,
        issue_url="https://github.com/Aries-Serpent/_codex_/issues/2905",
        workflow_run_id="21145572518",
        root_cause="Missing module: pytest",
        severity="high"
    )
    failure2 = FailureRecord(
        issue_number=2906,
        issue_url="https://github.com/Aries-Serpent/_codex_/issues/2906",
        workflow_run_id="21145592938",
        root_cause="Missing module: pytest",
        severity="high"
    )
    failure3 = FailureRecord(
        issue_number=2907,
        issue_url="https://github.com/Aries-Serpent/_codex_/issues/2907",
        workflow_run_id="21145583258",
        root_cause="Test failure: test_example",
        severity="medium"
    )
    
    engine.failures = [failure1, failure2, failure3]
    
    # Group by root cause
    engine.group_failures(strategy='root_cause')
    
    assert len(engine.groups) == 2
    
    # Check first group (should have 2 failures with same root cause)
    group1 = next(g for g in engine.groups if g.failure_count == 2)
    assert group1.failure_count == 2
    assert "pytest" in group1.root_cause
    
    # Check second group (should have 1 failure)
    group2 = next(g for g in engine.groups if g.failure_count == 1)
    assert group2.failure_count == 1
    assert "test_example" in group2.root_cause


def test_grouping_by_severity():
    """Test grouping failures by severity"""
    engine = BatchTriageEngine()
    
    # Add failures with different severities
    failure1 = FailureRecord(
        issue_number=2905,
        issue_url="https://github.com/Aries-Serpent/_codex_/issues/2905",
        workflow_run_id="21145572518",
        severity="high"
    )
    failure2 = FailureRecord(
        issue_number=2906,
        issue_url="https://github.com/Aries-Serpent/_codex_/issues/2906",
        workflow_run_id="21145592938",
        severity="high"
    )
    failure3 = FailureRecord(
        issue_number=2907,
        issue_url="https://github.com/Aries-Serpent/_codex_/issues/2907",
        workflow_run_id="21145583258",
        severity="medium"
    )
    
    engine.failures = [failure1, failure2, failure3]
    
    # Group by severity
    engine.group_failures(strategy='severity')
    
    assert len(engine.groups) == 2
    
    # Check high severity group
    high_group = next(g for g in engine.groups if g.severity == "high")
    assert high_group.failure_count == 2
    
    # Check medium severity group
    medium_group = next(g for g in engine.groups if g.severity == "medium")
    assert medium_group.failure_count == 1


def test_markdown_report_generation():
    """Test markdown report generation"""
    engine = BatchTriageEngine()
    
    # Add sample failures
    failure = FailureRecord(
        issue_number=2905,
        issue_url="https://github.com/Aries-Serpent/_codex_/issues/2905",
        workflow_run_id="21145572518",
        root_cause="Test failure",
        severity="high"
    )
    engine.failures = [failure]
    
    # Group failures
    engine.group_failures(strategy='root_cause')
    
    # Generate report
    report = engine.generate_markdown_report()
    
    assert "# Batch CI Failure Triage Report" in report
    assert "**Total Failures:** 1" in report
    assert "**Groups Identified:** 1" in report
    assert "#2905" in report
    assert "Test failure" in report


def test_json_report_generation():
    """Test JSON report generation"""
    engine = BatchTriageEngine()
    
    # Add sample failures
    failure = FailureRecord(
        issue_number=2905,
        issue_url="https://github.com/Aries-Serpent/_codex_/issues/2905",
        workflow_run_id="21145572518",
        root_cause="Test failure",
        severity="high"
    )
    engine.failures = [failure]
    
    # Group failures
    engine.group_failures(strategy='root_cause')
    
    # Generate report
    report_json = engine.generate_json_report()
    report = json.loads(report_json)
    
    assert report['total_failures'] == 1
    assert report['total_groups'] == 1
    assert len(report['failures']) == 1
    assert len(report['groups']) == 1
    assert report['failures'][0]['issue_number'] == 2905


def test_csv_loading(tmp_path):
    """Test loading failures from CSV file"""
    engine = BatchTriageEngine()
    
    # Create temporary CSV file
    csv_file = tmp_path / "test_failures.csv"
    csv_content = """Issue #,Issue URL,Failed Workflow Run,Self-Healing Analysis Run
2905,https://github.com/Aries-Serpent/_codex_/issues/2905,https://github.com/Aries-Serpent/_codex_/actions/runs/21145572518,https://github.com/Aries-Serpent/_codex_/actions/runs/21145604149
2906,https://github.com/Aries-Serpent/_codex_/issues/2906,https://github.com/Aries-Serpent/_codex_/actions/runs/21145592938,https://github.com/Aries-Serpent/_codex_/actions/runs/21145617654
"""
    csv_file.write_text(csv_content)
    
    # Load from CSV
    engine.load_from_csv(csv_file)
    
    assert len(engine.failures) == 2
    assert engine.failures[0].issue_number == 2905
    assert engine.failures[0].workflow_run_id == "21145572518"
    assert engine.failures[1].issue_number == 2906
    assert engine.failures[1].workflow_run_id == "21145592938"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
