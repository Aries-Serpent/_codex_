"""
Tests for Release Gate Agent - Gatekeeper Module (DECIDE Phase)

#AFTERMATH_PATTERN_IDENTIFIED: release_gate_testing_decide
"""

import pytest
from unittest.mock import Mock, patch
from agent.gatekeeper import ReleaseGatekeeper, ReleaseDecision, ReleaseAssessment


class TestReleaseDecision:
    """Test ReleaseDecision enum."""
    
    def test_release_decision_values(self):
        """Test ReleaseDecision enum has correct values."""
        assert ReleaseDecision.APPROVE.value == "approve"
        assert ReleaseDecision.APPROVE_WITH_MONITORING.value == "approve_with_monitoring"
        assert ReleaseDecision.BLOCK.value == "block"


class TestReleaseAssessment:
    """Test ReleaseAssessment dataclass."""
    
    def test_assessment_creation(self):
        """Test creating ReleaseAssessment with all fields."""
        assessment = ReleaseAssessment(
            decision=ReleaseDecision.APPROVE,
            risk_score=0.2,
            blockers=[],
            warnings=[],
            confidence=0.85,
            reasoning="Low risk, no issues",
            metadata={"test": "data"}
        )
        
        assert assessment.decision == ReleaseDecision.APPROVE
        assert assessment.risk_score == 0.2
        assert assessment.confidence == 0.85
        assert len(assessment.blockers) == 0


class TestReleaseGatekeeper:
    """Test ReleaseGatekeeper class."""
    
    @pytest.fixture
    def mock_brain(self):
        """Mock CognitiveBrain."""
        with patch('agent.gatekeeper.CognitiveBrain') as mock:
            yield mock
    
    @pytest.fixture
    def gatekeeper(self, mock_brain):
        """Create ReleaseGatekeeper instance with mocked brain."""
        return ReleaseGatekeeper()
    
    def test_gatekeeper_initialization(self, gatekeeper):
        """Test ReleaseGatekeeper initializes correctly."""
        assert gatekeeper.brain is not None
    
    def test_decide_all_pass(self, gatekeeper):
        """Test decide() with all validations passing."""
        validation_results = {
            "pass_rate": 1.0,
            "validations": [
                {"check_name": "CI/CD Status", "passed": True, "score": 1.0},
                {"check_name": "Test Coverage", "passed": True, "score": 1.0},
                {"check_name": "Security Scan", "passed": True, "score": 1.0},
            ]
        }
        
        with patch.object(gatekeeper.brain, 'query_patterns', return_value=[]):
            result = gatekeeper.decide(validation_results)
        
        assert result["decision"] == "approve"
        assert result["risk_score"] == 0.0
        assert len(result["blockers"]) == 0
        assert len(result["warnings"]) == 0
    
    def test_decide_ci_failure_blocks(self, gatekeeper):
        """Test decide() blocks release when CI fails."""
        validation_results = {
            "pass_rate": 0.83,
            "validations": [
                {"check_name": "CI/CD Status", "passed": False, "score": 0.0, "error_message": "Tests failed"},
                {"check_name": "Test Coverage", "passed": True, "score": 1.0},
                {"check_name": "Security Scan", "passed": True, "score": 1.0},
            ]
        }
        
        with patch.object(gatekeeper.brain, 'query_patterns', return_value=[]):
            result = gatekeeper.decide(validation_results)
        
        assert result["decision"] == "block"
        assert len(result["blockers"]) > 0
        assert "CI/CD Status" in result["blockers"][0]
    
    def test_decide_security_failure_blocks(self, gatekeeper):
        """Test decide() blocks release when security scan fails."""
        validation_results = {
            "pass_rate": 0.83,
            "validations": [
                {"check_name": "CI/CD Status", "passed": True, "score": 1.0},
                {"check_name": "Test Coverage", "passed": True, "score": 1.0},
                {"check_name": "Security Scan", "passed": False, "score": 0.0, "error_message": "Critical vuln"},
            ]
        }
        
        with patch.object(gatekeeper.brain, 'query_patterns', return_value=[]):
            result = gatekeeper.decide(validation_results)
        
        assert result["decision"] == "block"
        assert len(result["blockers"]) > 0
        assert "Security Scan" in result["blockers"][0]
    
    def test_decide_with_warnings(self, gatekeeper):
        """Test decide() approves with monitoring when warnings present."""
        validation_results = {
            "pass_rate": 0.83,
            "validations": [
                {"check_name": "CI/CD Status", "passed": True, "score": 1.0},
                {"check_name": "Test Coverage", "passed": True, "score": 1.0},
                {"check_name": "Documentation", "passed": False, "score": 0.67, "error_message": "Missing CHANGELOG"},
            ]
        }
        
        with patch.object(gatekeeper.brain, 'query_patterns', return_value=[]):
            result = gatekeeper.decide(validation_results)
        
        assert result["decision"] == "approve_with_monitoring"
        assert len(result["warnings"]) > 0
        assert len(result["blockers"]) == 0
    
    def test_calculate_release_risk_all_pass(self, gatekeeper):
        """Test risk calculation with all validations passing."""
        validation_results = {"pass_rate": 1.0, "validations": []}
        risk_score = gatekeeper._calculate_release_risk(validation_results)
        assert risk_score == 0.0
    
    def test_calculate_release_risk_all_fail(self, gatekeeper):
        """Test risk calculation with all validations failing."""
        validation_results = {
            "pass_rate": 0.0,
            "validations": [
                {"check_name": "CI/CD Status", "passed": False, "score": 0.0},
                {"check_name": "Security Scan", "passed": False, "score": 0.0},
            ]
        }
        risk_score = gatekeeper._calculate_release_risk(validation_results)
        assert risk_score >= 1.0  # Should be maxed at 1.0
    
    def test_query_historical_success_no_data(self, gatekeeper):
        """Test historical success query with no data."""
        with patch.object(gatekeeper.brain, 'query_patterns', return_value=[]):
            success_rate = gatekeeper._query_historical_success(0.5)
        assert success_rate == 0.7  # Default
    
    def test_query_historical_success_with_data(self, gatekeeper):
        """Test historical success query with existing patterns."""
        patterns = [
            {"risk_score": 0.4, "success": True},
            {"risk_score": 0.5, "success": True},
            {"risk_score": 0.6, "success": False},
        ]
        
        with patch.object(gatekeeper.brain, 'query_patterns', return_value=patterns):
            success_rate = gatekeeper._query_historical_success(0.5)
        
        assert success_rate == 2/3  # 2 successes out of 3
    
    def test_identify_blockers_critical_failures(self, gatekeeper):
        """Test blocker identification for critical failures."""
        validation_results = {
            "validations": [
                {"check_name": "CI/CD Status", "passed": False, "error_message": "Build failed"},
                {"check_name": "Security Scan", "passed": False, "error_message": "CVE detected"},
            ]
        }
        
        blockers = gatekeeper._identify_blockers(validation_results)
        assert len(blockers) == 2
    
    def test_identify_blockers_low_score(self, gatekeeper):
        """Test blocker identification for low scores."""
        validation_results = {
            "validations": [
                {"check_name": "Test Coverage", "passed": False, "score": 0.3},
            ]
        }
        
        blockers = gatekeeper._identify_blockers(validation_results)
        assert len(blockers) == 1
        assert "0.30" in blockers[0]
    
    def test_identify_warnings(self, gatekeeper):
        """Test warning identification for non-critical failures."""
        validation_results = {
            "validations": [
                {"check_name": "Documentation", "passed": False, "score": 0.67, "error_message": "Minor issue"},
            ]
        }
        
        warnings = gatekeeper._identify_warnings(validation_results)
        assert len(warnings) == 1
        assert "Documentation" in warnings[0]
    
    def test_make_decision_with_blockers(self, gatekeeper):
        """Test decision making with blockers present."""
        decision = gatekeeper._make_decision(0.5, ["Blocker 1"], [])
        assert decision == ReleaseDecision.BLOCK
    
    def test_make_decision_high_risk(self, gatekeeper):
        """Test decision making with high risk but no blockers."""
        decision = gatekeeper._make_decision(0.5, [], [])
        assert decision == ReleaseDecision.APPROVE_WITH_MONITORING
    
    def test_make_decision_with_warnings(self, gatekeeper):
        """Test decision making with warnings but low risk."""
        decision = gatekeeper._make_decision(0.1, [], ["Warning 1"])
        assert decision == ReleaseDecision.APPROVE_WITH_MONITORING
    
    def test_make_decision_approve(self, gatekeeper):
        """Test decision making approves clean release."""
        decision = gatekeeper._make_decision(0.1, [], [])
        assert decision == ReleaseDecision.APPROVE
    
    def test_calculate_confidence_high(self, gatekeeper):
        """Test confidence calculation with good conditions."""
        confidence = gatekeeper._calculate_confidence(0.1, 0.9, 0, 0)
        assert confidence > 0.8
    
    def test_calculate_confidence_low(self, gatekeeper):
        """Test confidence calculation with poor conditions."""
        confidence = gatekeeper._calculate_confidence(0.8, 0.5, 2, 3)
        assert confidence < 0.5
    
    def test_generate_reasoning_block(self, gatekeeper):
        """Test reasoning generation for blocked release."""
        reasoning = gatekeeper._generate_reasoning(
            ReleaseDecision.BLOCK, 0.8, ["Blocker 1", "Blocker 2"], []
        )
        assert "BLOCKED" in reasoning
        assert "2" in reasoning
    
    def test_generate_reasoning_approve_with_monitoring(self, gatekeeper):
        """Test reasoning generation for monitored release."""
        reasoning = gatekeeper._generate_reasoning(
            ReleaseDecision.APPROVE_WITH_MONITORING, 0.5, [], ["Warning 1"]
        )
        assert "APPROVED with monitoring" in reasoning
        assert "0.50" in reasoning
    
    def test_generate_reasoning_approve(self, gatekeeper):
        """Test reasoning generation for approved release."""
        reasoning = gatekeeper._generate_reasoning(
            ReleaseDecision.APPROVE, 0.1, [], []
        )
        assert "APPROVED" in reasoning
        assert "low risk" in reasoning
