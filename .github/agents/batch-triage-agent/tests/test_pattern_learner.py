"""Tests for PatternLearner."""

import sys
import json
import tempfile
from pathlib import Path

# Add parent directories to path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR.parent / "src"))

from pattern_learner import PatternLearner, FailurePattern


def test_pattern_learner_initialization():
    """Test pattern learner initializes correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        learner = PatternLearner(
            kb_path=Path(tmpdir),
            pattern_expiry_days=90,
            min_occurrences=3,
        )
        
        assert learner.kb_path == Path(tmpdir)
        assert learner.pattern_expiry_days == 90
        assert learner.min_occurrences == 3
        assert learner.patterns_dir.exists()


def test_failure_pattern_dataclass():
    """Test FailurePattern dataclass."""
    pattern = FailurePattern(
        pattern_id="test_pattern_1",
        failure_type="test_failure",
        root_cause="Assertion failed",
        common_symptoms=["Expected 5, got 3"],
    )
    
    assert pattern.pattern_id == "test_pattern_1"
    assert pattern.occurrences == 1
    assert pattern.first_seen != ""
    assert pattern.success_rate == 0.0


def test_record_triage_outcome():
    """Test recording triage outcomes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        learner = PatternLearner(kb_path=Path(tmpdir))
        
        failures = [
            {
                "issue_number": 1,
                "failure_type": "test_failure",
                "root_cause": "Test failed",
                "detected_issues": [{"description": "Assertion error"}],
            }
        ]
        
        learner.record_triage_outcome(
            batch_id="batch_001",
            failures=failures,
        )
        
        # Check file was created
        outcome_files = list(learner.patterns_dir.glob("batch_batch_001_*.json"))
        assert len(outcome_files) == 1


def test_pattern_extraction():
    """Test pattern extraction from batch."""
    with tempfile.TemporaryDirectory() as tmpdir:
        learner = PatternLearner(kb_path=Path(tmpdir))
        
        failures = [
            {
                "failure_type": "import_error",
                "root_cause": "Module not found",
                "detected_issues": [{"description": "ModuleNotFoundError: foo"}],
            },
            {
                "failure_type": "import_error",
                "root_cause": "Module not found",
                "detected_issues": [{"description": "ModuleNotFoundError: bar"}],
            },
        ]
        
        patterns = learner._extract_patterns_from_batch(failures)
        
        assert len(patterns) == 1
        assert patterns[0]["failure_type"] == "import_error"
        assert patterns[0]["occurrences"] == 2


def test_track_remediation_outcome():
    """Test tracking remediation outcomes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        learner = PatternLearner(kb_path=Path(tmpdir))
        
        # Create a pattern
        pattern_id = learner._generate_pattern_id("test_failure", "Test failed")
        learner._update_or_create_pattern({
            "pattern_id": pattern_id,
            "failure_type": "test_failure",
            "root_cause": "Test failed",
            "common_symptoms": [],
            "occurrences": 1,
        })
        
        # Track remediation
        learner.track_remediation_outcome(
            remediation_id="rem_001",
            pattern_id=pattern_id,
            success=True,
            resolution_time_hours=2.5,
        )
        
        # Check JSONL file exists
        assert learner.remediations_db.exists()
        
        # Verify pattern success rate updated
        pattern = learner.patterns[pattern_id]
        assert pattern.success_rate == 1.0


def test_get_pattern():
    """Test retrieving patterns."""
    with tempfile.TemporaryDirectory() as tmpdir:
        learner = PatternLearner(kb_path=Path(tmpdir))
        
        # Create a pattern
        learner._update_or_create_pattern({
            "pattern_id": learner._generate_pattern_id("lint_error", "Missing semicolon"),
            "failure_type": "lint_error",
            "root_cause": "Missing semicolon",
            "common_symptoms": ["Syntax error"],
            "occurrences": 5,
        })
        
        pattern = learner.get_pattern("lint_error", "Missing semicolon")
        
        assert pattern is not None
        assert pattern.failure_type == "lint_error"
        assert pattern.occurrences == 5


def test_get_best_remediation():
    """Test getting best remediation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        learner = PatternLearner(kb_path=Path(tmpdir))
        
        # Create pattern with recommendations
        pattern_id = learner._generate_pattern_id("build_failure", "Dependency conflict")
        pattern = FailurePattern(
            pattern_id=pattern_id,
            failure_type="build_failure",
            root_cause="Dependency conflict",
            common_symptoms=[],
            success_rate=0.85,
            recommended_actions=["Update dependencies", "Clear cache"],
        )
        learner.patterns[pattern_id] = pattern
        
        remediation = learner.get_best_remediation("build_failure", "Dependency conflict")
        
        assert remediation is not None
        assert remediation["success_rate"] == 0.85
        assert remediation["confidence"] == "high"


def test_cleanup_expired_patterns():
    """Test cleanup of expired patterns."""
    with tempfile.TemporaryDirectory() as tmpdir:
        learner = PatternLearner(kb_path=Path(tmpdir), pattern_expiry_days=0)
        
        # Create an old pattern
        from datetime import datetime, timedelta
        old_date = (datetime.now() - timedelta(days=1)).isoformat()
        
        pattern = FailurePattern(
            pattern_id="old_pattern",
            failure_type="test_failure",
            root_cause="Old failure",
            common_symptoms=[],
            last_seen=old_date,
        )
        learner.patterns["old_pattern"] = pattern
        
        # Save to disk
        pattern_file = learner.patterns_dir / "old_pattern.json"
        with open(pattern_file, 'w') as f:
            json.dump(pattern.to_dict(), f)
        
        # Cleanup
        removed = learner.cleanup_expired_patterns()
        
        assert removed == 1
        assert "old_pattern" not in learner.patterns


def test_get_statistics():
    """Test statistics retrieval."""
    with tempfile.TemporaryDirectory() as tmpdir:
        learner = PatternLearner(kb_path=Path(tmpdir), min_occurrences=2)
        
        # Add patterns
        learner.patterns["p1"] = FailurePattern(
            pattern_id="p1",
            failure_type="test_failure",
            root_cause="Test 1",
            common_symptoms=[],
            occurrences=3,
            success_rate=0.8,
        )
        learner.patterns["p2"] = FailurePattern(
            pattern_id="p2",
            failure_type="import_error",
            root_cause="Import 1",
            common_symptoms=[],
            occurrences=1,
            success_rate=0.5,
        )
        
        stats = learner.get_statistics()
        
        assert stats["total_patterns"] == 2
        assert stats["stable_patterns"] == 1  # Only p1 has >= 2 occurrences
        assert stats["high_success_patterns"] == 1  # Only p1 has >= 0.7 success rate
