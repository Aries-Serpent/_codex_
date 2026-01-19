"""Tests for BatchTriageAnalyzer."""

import sys
from pathlib import Path
import tempfile
import json

# Add parent directories to path
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(SCRIPT_DIR.parent / "src"))

from scripts.ci.batch_triage import FailureRecord, TriageGroup
from analyzer import BatchTriageAnalyzer


def test_analyzer_initialization():
    """Test analyzer initializes correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analyzer = BatchTriageAnalyzer(
            repo="test/repo",
            cognitive_brain_path=Path(tmpdir)
        )
        
        assert analyzer.repo == "test/repo"
        assert analyzer.cognitive_brain_path == Path(tmpdir)
        assert analyzer.patterns_dir.exists()


def test_analyze_with_confidence():
    """Test confidence scoring."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analyzer = BatchTriageAnalyzer(
            repo="test/repo",
            cognitive_brain_path=Path(tmpdir)
        )
        
        failure = FailureRecord(
            issue_number=123,
            issue_url="https://github.com/test/repo/issues/123",
            workflow_run_id="12345",
        )
        
        confidence = analyzer.analyze_with_confidence(failure)
        
        assert 0.0 <= confidence <= 1.0
        assert 123 in analyzer.confidence_scores


def test_enrich_with_historical_context():
    """Test historical context enrichment."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analyzer = BatchTriageAnalyzer(
            repo="test/repo",
            cognitive_brain_path=Path(tmpdir)
        )
        
        # Create a test pattern file
        pattern_file = analyzer.patterns_dir / "test_failure_pattern.json"
        pattern_data = {
            "timestamp": "2026-01-19T00:00:00",
            "root_cause": "Test failure",
            "resolution": "Fixed by updating assertions",
        }
        with open(pattern_file, 'w') as f:
            json.dump(pattern_data, f)
        
        failure = FailureRecord(
            issue_number=456,
            issue_url="https://github.com/test/repo/issues/456",
            workflow_run_id="67890",
            failure_type="test_failure",
        )
        
        context = analyzer.enrich_with_historical_context(failure)
        
        assert "total_occurrences" in context
        assert "similar_failures" in context
        assert context["total_occurrences"] == 1


def test_calculate_group_confidence():
    """Test group confidence calculation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analyzer = BatchTriageAnalyzer(
            repo="test/repo",
            cognitive_brain_path=Path(tmpdir)
        )
        
        # Add some failures with confidence scores
        failures = [
            FailureRecord(issue_number=1, issue_url="url1", workflow_run_id="1"),
            FailureRecord(issue_number=2, issue_url="url2", workflow_run_id="2"),
        ]
        analyzer.confidence_scores[1] = 0.8
        analyzer.confidence_scores[2] = 0.6
        
        group = TriageGroup(
            group_id="group_1",
            root_cause="Test failure",
            severity="medium",
            failure_count=2,
            failures=failures,
        )
        
        confidence = analyzer.calculate_group_confidence(group)
        
        assert confidence == 0.7  # Average of 0.8 and 0.6


def test_get_metrics():
    """Test metrics retrieval."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analyzer = BatchTriageAnalyzer(
            repo="test/repo",
            cognitive_brain_path=Path(tmpdir)
        )
        
        # Add some test data
        analyzer.failures = [
            FailureRecord(issue_number=1, issue_url="url1", workflow_run_id="1"),
            FailureRecord(issue_number=2, issue_url="url2", workflow_run_id="2"),
        ]
        analyzer.confidence_scores[1] = 0.9
        analyzer.confidence_scores[2] = 0.4
        
        metrics = analyzer.get_metrics()
        
        assert metrics["total_failures"] == 2
        assert metrics["avg_confidence"] == 0.65
        assert metrics["high_confidence_count"] == 1
        assert metrics["low_confidence_count"] == 1


def test_export_for_learning():
    """Test export for learning."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analyzer = BatchTriageAnalyzer(
            repo="test/repo",
            cognitive_brain_path=Path(tmpdir)
        )
        
        failure = FailureRecord(
            issue_number=789,
            issue_url="https://github.com/test/repo/issues/789",
            workflow_run_id="11111",
            failure_type="import_error",
            root_cause="Missing module",
            severity="medium",
        )
        analyzer.failures.append(failure)
        analyzer.confidence_scores[789] = 0.75
        
        export = analyzer.export_for_learning()
        
        assert "timestamp" in export
        assert "repository" in export
        assert len(export["failures"]) == 1
        assert export["failures"][0]["issue_number"] == 789
        assert export["failures"][0]["confidence"] == 0.75
