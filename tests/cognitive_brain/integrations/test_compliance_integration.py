"""
Tests for Compliance Integration with Superposition Engine

Tests both quantum (superposition) and classical compliance assessment approaches.
Validates parallel decision evaluation, accuracy improvements, and performance metrics.
"""

import pytest
import tempfile
import os
from datetime import datetime

from cognitive_brain.quantum.config import QuantumConfig
from cognitive_brain.quantum.coherence_monitor import CoherenceMonitor
from cognitive_brain.models.quantum_metrics import QuantumMetricRepository
from cognitive_brain.integrations.compliance_integration import (
    QuantumComplianceAssessor,
    ComplianceDecision,
    AuditResult,
    ComplianceAssessment
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    import sqlite3
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    # Initialize schema
    conn = sqlite3.connect(path)
    conn.executescript("""
        CREATE TABLE quantum_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            feature VARCHAR(50) NOT NULL,
            metric_name VARCHAR(100) NOT NULL,
            metric_value FLOAT NOT NULL,
            agent_id VARCHAR(100),
            metadata TEXT DEFAULT '{}',
            UNIQUE(timestamp, feature, metric_name)
        );
        
        CREATE INDEX idx_quantum_metrics_timestamp ON quantum_metrics(timestamp);
        CREATE INDEX idx_quantum_metrics_feature ON quantum_metrics(feature);
        CREATE INDEX idx_quantum_metrics_agent_id ON quantum_metrics(agent_id);
    """)
    conn.close()
    
    yield path
    
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def config():
    """Create quantum config with superposition enabled"""
    return QuantumConfig(
        quantum_mode=True,
        superposition=True,
        entanglement=False,
        uncertainty=False,
        wave_collapse=False,
        rollout_percentage=100
    )


@pytest.fixture
def repository(temp_db):
    """Create quantum metric repository"""
    return QuantumMetricRepository(temp_db)


@pytest.fixture
def monitor(config, repository):
    """Create coherence monitor"""
    return CoherenceMonitor(config, repository)


@pytest.fixture
def quantum_assessor(config, monitor, repository):
    """Create quantum compliance assessor"""
    return QuantumComplianceAssessor(config, monitor, repository, enable_superposition=True)


@pytest.fixture
def classical_assessor(config, monitor, repository):
    """Create classical compliance assessor"""
    return QuantumComplianceAssessor(config, monitor, repository, enable_superposition=False)


class TestAuditResult:
    """Test AuditResult validation"""
    
    def test_valid_audit_result(self):
        """Test creating valid audit result"""
        audit = AuditResult(
            audit_id="AUDIT-001",
            score=0.95,
            risk_level="low",
            remediation_cost=100.0,
            business_impact=0.8,
            violations=[]
        )
        assert audit.audit_id == "AUDIT-001"
        assert audit.score == 0.95
    
    def test_invalid_score(self):
        """Test audit result with invalid score"""
        with pytest.raises(ValueError, match="Score must be between"):
            AuditResult(
                audit_id="AUDIT-002",
                score=1.5,  # Invalid
                risk_level="low",
                remediation_cost=100.0,
                business_impact=0.8,
                violations=[]
            )
    
    def test_invalid_business_impact(self):
        """Test audit result with invalid business impact"""
        with pytest.raises(ValueError, match="Business impact must be between"):
            AuditResult(
                audit_id="AUDIT-003",
                score=0.9,
                risk_level="low",
                remediation_cost=100.0,
                business_impact=1.5,  # Invalid
                violations=[]
            )


class TestQuantumComplianceAssessor:
    """Test quantum compliance assessor"""
    
    def test_initialization_with_superposition(self, config, monitor, repository):
        """Test assessor initializes with superposition enabled"""
        assessor = QuantumComplianceAssessor(config, monitor, repository, enable_superposition=True)
        assert assessor.enable_superposition is True
        assert assessor.engine is not None
    
    def test_initialization_without_superposition(self, config, monitor, repository):
        """Test assessor initializes without superposition"""
        assessor = QuantumComplianceAssessor(config, monitor, repository, enable_superposition=False)
        assert assessor.enable_superposition is False
        assert assessor.engine is None
    
    def test_assess_high_score_low_risk(self, quantum_assessor):
        """Test assessment for high compliance score with low risk"""
        audit = AuditResult(
            audit_id="AUDIT-004",
            score=0.95,
            risk_level="low",
            remediation_cost=50.0,
            business_impact=0.9,
            violations=[]
        )
        
        assessment = quantum_assessor.assess_compliance(audit)
        
        assert assessment.decision == ComplianceDecision.APPROVE
        assert assessment.used_superposition is True
        assert assessment.confidence > 0.25  # Best of 4 options (uniform would be 0.25)
        assert assessment.coherence > 0.0
        assert assessment.evaluation_time_ms > 0
    
    def test_assess_medium_score_medium_risk(self, quantum_assessor):
        """Test assessment for medium compliance score with medium risk"""
        audit = AuditResult(
            audit_id="AUDIT-005",
            score=0.75,
            risk_level="medium",
            remediation_cost=500.0,
            business_impact=0.7,
            violations=["Minor violation 1"]
        )
        
        assessment = quantum_assessor.assess_compliance(audit)
        
        assert assessment.decision in [
            ComplianceDecision.APPROVE_WITH_MONITORING,
            ComplianceDecision.CONDITIONAL_APPROVAL
        ]
        assert assessment.used_superposition is True
        assert assessment.coherence > 0.0
    
    def test_assess_low_score_high_risk(self, quantum_assessor):
        """Test assessment for low compliance score with high risk"""
        audit = AuditResult(
            audit_id="AUDIT-006",
            score=0.3,
            risk_level="high",
            remediation_cost=5000.0,
            business_impact=0.2,
            violations=["Critical violation 1", "Critical violation 2"]
        )
        
        assessment = quantum_assessor.assess_compliance(audit)
        
        assert assessment.decision == ComplianceDecision.REJECT
        assert assessment.used_superposition is True
        assert assessment.confidence > 0.5
    
    def test_classical_assessment_high_score(self, classical_assessor):
        """Test classical assessment for high score"""
        audit = AuditResult(
            audit_id="AUDIT-007",
            score=0.95,
            risk_level="low",
            remediation_cost=50.0,
            business_impact=0.9,
            violations=[]
        )
        
        assessment = classical_assessor.assess_compliance(audit)
        
        assert assessment.decision == ComplianceDecision.APPROVE
        assert assessment.used_superposition is False
        assert assessment.coherence == 0.0  # Classical has no coherence
        assert assessment.confidence == 0.95
    
    def test_classical_assessment_medium_score(self, classical_assessor):
        """Test classical assessment for medium score"""
        audit = AuditResult(
            audit_id="AUDIT-008",
            score=0.75,
            risk_level="medium",
            remediation_cost=500.0,
            business_impact=0.7,
            violations=["Violation 1"]
        )
        
        assessment = classical_assessor.assess_compliance(audit)
        
        assert assessment.decision == ComplianceDecision.APPROVE_WITH_MONITORING
        assert assessment.used_superposition is False
        assert assessment.confidence == 0.75
    
    def test_classical_assessment_low_score(self, classical_assessor):
        """Test classical assessment for low score"""
        audit = AuditResult(
            audit_id="AUDIT-009",
            score=0.3,
            risk_level="high",
            remediation_cost=5000.0,
            business_impact=0.2,
            violations=["Critical 1", "Critical 2"]
        )
        
        assessment = classical_assessor.assess_compliance(audit)
        
        assert assessment.decision == ComplianceDecision.REJECT
        assert assessment.used_superposition is False
        assert assessment.confidence == 0.85
    
    def test_conditional_approval_low_cost(self, classical_assessor):
        """Test conditional approval for marginal score with low remediation cost"""
        audit = AuditResult(
            audit_id="AUDIT-010",
            score=0.6,
            risk_level="medium",
            remediation_cost=500.0,  # Low cost
            business_impact=0.8,
            violations=["Fixable issue 1"]
        )
        
        assessment = classical_assessor.assess_compliance(audit)
        
        assert assessment.decision == ComplianceDecision.CONDITIONAL_APPROVAL
        assert assessment.confidence == 0.60


class TestQuantumVsClassical:
    """Compare quantum and classical assessment approaches"""
    
    def test_quantum_produces_valid_assessments(self, quantum_assessor):
        """Test quantum assessor produces valid assessments"""
        audits = [
            AuditResult("A1", 0.95, "low", 100, 0.9, []),
            AuditResult("A2", 0.75, "medium", 500, 0.7, ["v1"]),
            AuditResult("A3", 0.5, "medium", 800, 0.6, ["v1", "v2"]),
            AuditResult("A4", 0.3, "high", 2000, 0.3, ["c1", "c2"]),
        ]
        
        for audit in audits:
            assessment = quantum_assessor.assess_compliance(audit)
            assert isinstance(assessment.decision, ComplianceDecision)
            assert 0.0 <= assessment.confidence <= 1.0
            assert assessment.coherence > 0.0
            assert assessment.used_superposition is True
    
    def test_classical_produces_valid_assessments(self, classical_assessor):
        """Test classical assessor produces valid assessments"""
        audits = [
            AuditResult("A1", 0.95, "low", 100, 0.9, []),
            AuditResult("A2", 0.75, "medium", 500, 0.7, ["v1"]),
            AuditResult("A3", 0.5, "medium", 800, 0.6, ["v1", "v2"]),
            AuditResult("A4", 0.3, "high", 2000, 0.3, ["c1", "c2"]),
        ]
        
        for audit in audits:
            assessment = classical_assessor.assess_compliance(audit)
            assert isinstance(assessment.decision, ComplianceDecision)
            assert 0.0 <= assessment.confidence <= 1.0
            assert assessment.coherence == 0.0
            assert assessment.used_superposition is False
    
    def test_performance_tracking(self, quantum_assessor, monitor):
        """Test that quantum assessor records performance metrics"""
        audit = AuditResult("A-PERF", 0.85, "low", 200, 0.8, [])
        
        assessment = quantum_assessor.assess_compliance(audit)
        
        # Check metrics were recorded
        assert assessment.evaluation_time_ms > 0
        
        # Verify coherence was tracked
        health = monitor.get_feature_health("superposition")
        assert health["health_status"] in ["healthy", "degraded"]
    
    def test_reasoning_includes_details(self, quantum_assessor, classical_assessor):
        """Test that assessments include detailed reasoning"""
        audit = AuditResult("A-REASON", 0.8, "low", 300, 0.75, ["minor"])
        
        quantum_assessment = quantum_assessor.assess_compliance(audit)
        classical_assessment = classical_assessor.assess_compliance(audit)
        
        # Quantum reasoning should mention superposition
        assert "superposition" in quantum_assessment.reasoning.lower() or "quantum" in quantum_assessment.reasoning.lower()
        assert len(quantum_assessment.reasoning) > 50
        
        # Classical reasoning should be clear
        assert len(classical_assessment.reasoning) > 20
