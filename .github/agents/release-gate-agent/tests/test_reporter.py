"""
Tests for Release Gate Agent - Reporter Module (AFTERMATH Phase)

#AFTERMATH_PATTERN_IDENTIFIED: release_gate_testing_aftermath
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from agent.reporter import ReleaseReporter, ReleaseReport


class TestReleaseReport:
    """Test ReleaseReport dataclass."""
    
    def test_report_creation(self):
        """Test creating ReleaseReport with all fields."""
        timestamp = datetime.now()
        report = ReleaseReport(
            release_id="v1.0.0",
            outcome="success",
            risk_score=0.2,
            validation_pass_rate=0.95,
            blockers_count=0,
            warnings_count=1,
            duration_seconds=120.5,
            health_status="healthy",
            lessons_learned={"test": "lesson"},
            timestamp=timestamp,
            metadata={"url": "https://test"}
        )
        
        assert report.release_id == "v1.0.0"
        assert report.outcome == "success"
        assert report.risk_score == 0.2
        assert report.validation_pass_rate == 0.95
        assert report.duration_seconds == 120.5


class TestReleaseReporter:
    """Test ReleaseReporter class."""
    
    @pytest.fixture
    def mock_brain(self):
        """Mock CognitiveBrain."""
        with patch('agent.reporter.CognitiveBrain') as mock:
            yield mock
    
    @pytest.fixture
    def reporter(self, mock_brain):
        """Create ReleaseReporter instance with mocked brain."""
        return ReleaseReporter()
    
    def test_reporter_initialization(self, reporter):
        """Test ReleaseReporter initializes correctly."""
        assert reporter.brain is not None
    
    def test_generate_aftermath_report_success(self, reporter):
        """Test aftermath report generation for successful release."""
        validation_results = {
            "pass_rate": 1.0,
            "validations": [
                {"check_name": "CI/CD", "passed": True}
            ]
        }
        decision_result = {
            "risk_score": 0.1,
            "blockers": [],
            "warnings": [],
            "decision": "approve"
        }
        execution_result = {
            "status": "success",
            "health_status": "healthy",
            "duration_seconds": 100.0,
            "release_url": "https://github.com/test/releases/v1.0.0",
            "git_tag": "v1.0.0"
        }
        release_info = {"version": "v1.0.0"}
        
        with patch.object(reporter.brain, 'record_pattern') as mock_record:
            report = reporter.generate_aftermath_report(
                validation_results, decision_result, execution_result, release_info
            )
        
        assert report["outcome"] == "success"
        assert report["release_id"] == "v1.0.0"
        assert report["risk_score"] == 0.1
        assert report["validation_pass_rate"] == 1.0
        assert report["health_status"] == "healthy"
        mock_record.assert_called_once()
    
    def test_generate_aftermath_report_blocked(self, reporter):
        """Test aftermath report generation for blocked release."""
        validation_results = {
            "pass_rate": 0.5,
            "validations": []
        }
        decision_result = {
            "risk_score": 0.9,
            "blockers": ["CI failed"],
            "warnings": [],
            "decision": "block"
        }
        execution_result = {
            "status": "blocked",
            "health_status": "n/a",
            "duration_seconds": 5.0,
            "release_url": "",
            "git_tag": ""
        }
        release_info = {"version": "v1.0.0"}
        
        with patch.object(reporter.brain, 'record_pattern') as mock_record:
            report = reporter.generate_aftermath_report(
                validation_results, decision_result, execution_result, release_info
            )
        
        assert report["outcome"] == "blocked"
        assert report["blockers_count"] == 1
        mock_record.assert_called_once_with(
            pattern_type="release_outcome",
            success=False,
            metadata=pytest.ANY
        )
    
    def test_generate_aftermath_report_failed(self, reporter):
        """Test aftermath report generation for failed release."""
        validation_results = {
            "pass_rate": 0.9,
            "validations": []
        }
        decision_result = {
            "risk_score": 0.2,
            "blockers": [],
            "warnings": [],
            "decision": "approve"
        }
        execution_result = {
            "status": "failed",
            "health_status": "unhealthy",
            "duration_seconds": 150.0,
            "release_url": "",
            "git_tag": "v1.0.0"
        }
        release_info = {"version": "v1.0.0"}
        
        with patch.object(reporter.brain, 'record_pattern') as mock_record:
            report = reporter.generate_aftermath_report(
                validation_results, decision_result, execution_result, release_info
            )
        
        assert report["outcome"] == "failed"
        assert report["health_status"] == "unhealthy"
    
    def test_determine_outcome_success(self, reporter):
        """Test outcome determination for successful release."""
        execution_result = {
            "status": "success",
            "health_status": "healthy"
        }
        
        outcome = reporter._determine_outcome(execution_result)
        assert outcome == "success"
    
    def test_determine_outcome_blocked(self, reporter):
        """Test outcome determination for blocked release."""
        execution_result = {
            "status": "blocked",
            "health_status": "n/a"
        }
        
        outcome = reporter._determine_outcome(execution_result)
        assert outcome == "blocked"
    
    def test_determine_outcome_failed(self, reporter):
        """Test outcome determination for failed release."""
        execution_result = {
            "status": "failed",
            "health_status": "unhealthy"
        }
        
        outcome = reporter._determine_outcome(execution_result)
        assert outcome == "failed"
    
    def test_extract_lessons_validation_gaps(self, reporter):
        """Test lesson extraction identifies validation gaps."""
        validation_results = {
            "validations": [
                {"check_name": "CI/CD", "passed": False, "error_message": "Build failed"},
                {"check_name": "Coverage", "passed": False, "error_message": "Below 90%"}
            ]
        }
        decision_result = {"decision": "approve", "risk_score": 0.2}
        execution_result = {"status": "success", "health_status": "healthy"}
        
        lessons = reporter._extract_lessons(
            validation_results, decision_result, execution_result
        )
        
        assert "validation_gaps" in lessons
        assert len(lessons["validation_gaps"]) == 2
    
    def test_extract_lessons_decision_accuracy_block(self, reporter):
        """Test lesson extraction for correct block decision."""
        validation_results = {"validations": []}
        decision_result = {"decision": "block", "risk_score": 0.8}
        execution_result = {"status": "blocked", "health_status": "n/a"}
        
        lessons = reporter._extract_lessons(
            validation_results, decision_result, execution_result
        )
        
        assert "decision_accuracy" in lessons
        assert "Correctly blocked" in lessons["decision_accuracy"]
    
    def test_extract_lessons_decision_accuracy_approve(self, reporter):
        """Test lesson extraction for correct approve decision."""
        validation_results = {"validations": []}
        decision_result = {"decision": "approve", "risk_score": 0.1}
        execution_result = {"status": "success", "health_status": "healthy"}
        
        lessons = reporter._extract_lessons(
            validation_results, decision_result, execution_result
        )
        
        assert "decision_accuracy" in lessons
        assert "Correctly approved" in lessons["decision_accuracy"]
    
    def test_extract_lessons_risk_overcautious(self, reporter):
        """Test lesson extraction identifies over-cautious risk assessment."""
        validation_results = {"validations": []}
        decision_result = {"decision": "approve", "risk_score": 0.7}
        execution_result = {"status": "success", "health_status": "healthy"}
        
        lessons = reporter._extract_lessons(
            validation_results, decision_result, execution_result
        )
        
        assert "risk_calibration" in lessons
        assert "over-cautious" in lessons["risk_calibration"]
    
    def test_extract_lessons_risk_underestimated(self, reporter):
        """Test lesson extraction identifies under-estimated risk."""
        validation_results = {"validations": []}
        decision_result = {"decision": "approve", "risk_score": 0.2}
        execution_result = {"status": "failed", "health_status": "unhealthy"}
        
        lessons = reporter._extract_lessons(
            validation_results, decision_result, execution_result
        )
        
        assert "risk_calibration" in lessons
        assert "under-estimating" in lessons["risk_calibration"]
    
    def test_extract_lessons_performance(self, reporter):
        """Test lesson extraction identifies slow performance."""
        validation_results = {"validations": []}
        decision_result = {"decision": "approve", "risk_score": 0.1}
        execution_result = {
            "status": "success",
            "health_status": "healthy",
            "duration_seconds": 400.0  # Over 5 minutes
        }
        
        lessons = reporter._extract_lessons(
            validation_results, decision_result, execution_result
        )
        
        assert "performance" in lessons
        assert "400.0s" in lessons["performance"]
    
    def test_record_pattern_success(self, reporter):
        """Test pattern recording for successful release."""
        validation_results = {"pass_rate": 1.0}
        decision_result = {
            "risk_score": 0.1,
            "decision": "approve",
            "blockers": [],
            "warnings": []
        }
        execution_result = {
            "health_status": "healthy",
            "duration_seconds": 100.0
        }
        
        with patch.object(reporter.brain, 'record_pattern') as mock_record:
            reporter._record_pattern(
                validation_results, decision_result, execution_result, "success"
            )
        
        mock_record.assert_called_once()
        call_args = mock_record.call_args
        assert call_args[1]["pattern_type"] == "release_outcome"
        assert call_args[1]["success"] is True
        assert call_args[1]["metadata"]["risk_score"] == 0.1
    
    def test_record_pattern_handles_failure(self, reporter):
        """Test pattern recording handles brain failure gracefully."""
        validation_results = {"pass_rate": 1.0}
        decision_result = {"risk_score": 0.1, "decision": "approve", "blockers": [], "warnings": []}
        execution_result = {"health_status": "healthy", "duration_seconds": 100.0}
        
        with patch.object(reporter.brain, 'record_pattern', side_effect=Exception("Brain error")):
            # Should not raise exception
            reporter._record_pattern(
                validation_results, decision_result, execution_result, "success"
            )
