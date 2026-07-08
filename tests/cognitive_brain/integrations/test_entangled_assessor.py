"""
Tests for EntangledComplianceSecurityAssessor.

Validates entangled agent coordination for compliance and security assessments.
"""

import pytest

from cognitive_brain.integrations.compliance_integration import (
    AuditResult,
    QuantumComplianceAssessor,
)
from cognitive_brain.integrations.entangled_assessor import (
    EntangledAssessmentResult,
    EntangledComplianceSecurityAssessor,
    MockSecurityScanner,
)
from cognitive_brain.models.quantum_metrics import QuantumMetricRepository
from cognitive_brain.quantum.coherence_monitor import CoherenceMonitor
from cognitive_brain.quantum.config import QuantumConfig
from cognitive_brain.quantum.entanglement import EntanglementManager
from cognitive_brain.quantum.superposition import SuperpositionEngine


@pytest.fixture
def config():
    """Quantum config with all features enabled."""
    config = QuantumConfig.from_env()
    config.quantum_mode = True
    config.quantum_superposition = True
    config.quantum_entanglement = True
    return config


@pytest.fixture
def repository():
    """In-memory repository for testing."""
    return QuantumMetricRepository(":memory:")


@pytest.fixture
def monitor(config, repository):
    """Coherence monitor."""
    return CoherenceMonitor(config, repository)


@pytest.fixture
def entanglement_mgr(config, monitor):
    """Entanglement manager."""
    return EntanglementManager(config, monitor)


@pytest.fixture
def engine(config, monitor):
    """Superposition engine."""
    return SuperpositionEngine(config, monitor)


@pytest.fixture
def compliance_assessor(config, engine, monitor, repository):
    """Quantum compliance assessor."""
    return QuantumComplianceAssessor(config, monitor, repository, enable_superposition=True)


@pytest.fixture
def entangled_assessor(entanglement_mgr, compliance_assessor):
    """Entangled compliance-security assessor."""
    return EntangledComplianceSecurityAssessor(
        compliance_assessor=compliance_assessor,
        security_scanner=MockSecurityScanner(),
        entanglement_mgr=entanglement_mgr,
    )


# --- Entanglement Setup Tests (3) ---


def test_setup_entanglement(entangled_assessor):
    """Test entanglement setup between compliance and security."""
    pair_id = entangled_assessor.setup_entanglement(correlation_strength=0.85)

    assert pair_id is not None, "pair_id must be initialized"
    assert isinstance(pair_id, str)
    assert len(pair_id) > 0, "Pair_id must not be empty"
    assert entangled_assessor.pair_id == pair_id, "pair_id is not valid"


def test_setup_with_custom_correlation(entangled_assessor):
    """Test setup with custom correlation strength."""
    pair_id = entangled_assessor.setup_entanglement(correlation_strength=0.90)

    assert pair_id is not None, "pair_id must be initialized"
    pair = entangled_assessor.entanglement.entangled_pairs[pair_id]
    assert pair.correlation_strength == 0.90, "correlation_strength is not valid"


def test_setup_entanglement_idempotent(entangled_assessor):
    """Test setup can be called multiple times (updates pair)."""
    entangled_assessor.setup_entanglement(0.85)  # Initial setup

    # Second call creates/updates
    pair_id_2 = entangled_assessor.setup_entanglement(0.90)

    # Should update the pair_id
    assert entangled_assessor.pair_id == pair_id_2, "pair_id is not valid"
    # IDs might be same if deterministic hashing produces same result
    assert isinstance(pair_id_2, str)


# --- Coordinated Assessment Tests (5) ---


def test_assess_with_entanglement_high_severity(entangled_assessor):
    """Test entangled assessment for high risk PII violation."""
    entangled_assessor.setup_entanglement(0.85)

    audit = AuditResult(
        audit_id="TEST-001",
        score=0.3,
        risk_level="high",
        remediation_cost=500.0,
        business_impact=0.8,
        violations=["PII exposure in user profile", "Missing encryption"],
    )

    result = entangled_assessor.assess_with_entanglement(audit)

    assert isinstance(result, EntangledAssessmentResult)
    assert result.compliance is not None, "compliance must be initialized"
    assert result.security is not None, "security must be initialized"
    assert result.pair_id == entangled_assessor.pair_id, "Result must not be empty"
    assert 0.0 <= result.correlation <= 1.0, "Result must not be empty"


def test_assess_without_setup_raises_error(entangled_assessor):
    """Test assessment without setup raises ValueError."""
    audit = AuditResult(
        audit_id="TEST-002",
        score=0.9,
        risk_level="low",
        remediation_cost=10.0,
        business_impact=0.3,
        violations=["Minor code quality issue"],
    )

    with pytest.raises(ValueError, match="Entanglement not set up"):
        entangled_assessor.assess_with_entanglement(audit)


def test_assess_updates_correlation(entangled_assessor):
    """Test assessment updates entanglement correlation."""
    entangled_assessor.setup_entanglement(0.85)

    audit = AuditResult(
        audit_id="TEST-003",
        score=0.2,
        risk_level="high",
        remediation_cost=1000.0,
        business_impact=0.9,
        violations=["Hardcoded secret key", "Missing authentication"],
    )

    # Perform assessment
    result = entangled_assessor.assess_with_entanglement(audit)

    # Check correlation was updated
    pair = entangled_assessor.entanglement.entangled_pairs[result.pair_id]
    assert len(pair.observed_states) >= 1, "Collection must not be empty"


def test_assess_multiple_audits(entangled_assessor):
    """Test multiple assessments build correlation history."""
    entangled_assessor.setup_entanglement(0.85)

    audits = [
        AuditResult(
            audit_id=f"TEST-{i:03d}",
            score=0.3,
            risk_level="high",
            remediation_cost=500.0,
            business_impact=0.8,
            violations=["PII exposure", f"Violation {i}"],
        )
        for i in range(5)
    ]

    results = [entangled_assessor.assess_with_entanglement(audit) for audit in audits]

    assert len(results) == 5, "Results must not be empty"
    assert all(isinstance(r, EntangledAssessmentResult) for r in results)

    # Correlation should be measurable after multiple observations
    final_correlation = results[-1].correlation
    assert 0.0 <= final_correlation <= 1.0, "0 is not valid"


def test_assess_tracks_total_count(entangled_assessor):
    """Test total assessment count is tracked."""
    entangled_assessor.setup_entanglement(0.85)

    assert entangled_assessor.total_assessments == 0, "total_assessments is not valid"

    for i in range(3):
        audit = AuditResult(
            audit_id=f"TEST-{i}",
            score=0.85,
            risk_level="low",
            remediation_cost=20.0,
            business_impact=0.4,
            violations=["Code quality issue"],
        )
        entangled_assessor.assess_with_entanglement(audit)

    assert entangled_assessor.total_assessments == 3, "total_assessments is not valid"


# --- Correlation Validation Tests (3) ---


def test_high_correlation_avoids_redundancy(entangled_assessor):
    """Test high correlation enables redundancy avoidance."""
    entangled_assessor.setup_entanglement(0.90)

    # Build high correlation history
    for i in range(10):
        audit = AuditResult(
            audit_id=f"TEST-{i}",
            score=0.3,
            risk_level="high",
            remediation_cost=500.0,
            business_impact=0.8,
            violations=["PII exposure", "Missing encryption"],
        )
        entangled_assessor.assess_with_entanglement(audit)

    # After building correlation, some redundancy should be avoided
    assert entangled_assessor.redundant_actions_avoided > 0, "redundant_actions_avoided must be greater than zero"


def test_correlation_above_threshold(entangled_assessor):
    """Test measured correlation meets target threshold."""
    entangled_assessor.setup_entanglement(0.85)

    # Assess several related violations
    for i in range(10):
        audit = AuditResult(
            audit_id=f"TEST-{i}",
            score=0.2,
            risk_level="high",
            remediation_cost=1000.0,
            business_impact=0.9,
            violations=["Hardcoded secret", "Missing authentication"],
        )
        result = entangled_assessor.assess_with_entanglement(audit)

    # Final correlation should be high for related violations
    final_correlation = result.correlation
    assert final_correlation > 0.6, "final_correlation must be greater than zero"


def test_get_redundancy_reduction(entangled_assessor):
    """Test redundancy reduction calculation."""
    entangled_assessor.setup_entanglement(0.85)

    # Initially zero
    assert entangled_assessor.get_redundancy_reduction() == 0.0, "entangled_assess is not valid"

    # After assessments, should have some reduction
    for i in range(20):
        audit = AuditResult(
            audit_id=f"TEST-{i}",
            score=0.3,
            risk_level="high",
            remediation_cost=500.0,
            business_impact=0.8,
            violations=["PII exposure", f"Violation {i}"],
        )
        entangled_assessor.assess_with_entanglement(audit)

    reduction = entangled_assessor.get_redundancy_reduction()
    assert 0.0 <= reduction <= 1.0, "0 is not valid"


# --- Error Handling Tests (4) ---


def test_assess_with_none_audit(entangled_assessor):
    """Test assessment with None audit raises error."""
    entangled_assessor.setup_entanglement(0.85)

    with pytest.raises(AttributeError):
        entangled_assessor.assess_with_entanglement(None)


def test_get_statistics_before_assessment(entangled_assessor):
    """Test get_statistics before any assessments."""
    entangled_assessor.setup_entanglement(0.85)

    stats = entangled_assessor.get_statistics()

    assert stats["total_assessments"] == 0, "Condition must be true"
    assert stats["redundant_actions_avoided"] == 0, "Condition must be true"
    assert stats["redundancy_reduction"] == 0.0, "Condition must be true"
    assert stats["pair_id"] == entangled_assessor.pair_id, "Condition must be true"


def test_get_statistics_after_assessments(entangled_assessor):
    """Test get_statistics after multiple assessments."""
    entangled_assessor.setup_entanglement(0.85)

    for i in range(10):
        audit = AuditResult(
            audit_id=f"TEST-{i}",
            score=0.7,
            risk_level="medium",
            remediation_cost=100.0,
            business_impact=0.5,
            violations=["Code quality issue", f"Issue {i}"],
        )
        entangled_assessor.assess_with_entanglement(audit)

    stats = entangled_assessor.get_statistics()

    assert stats["total_assessments"] == 10, "Condition must be true"
    assert stats["redundant_actions_avoided"] >= 0, "Value must be greater than zero"
    assert 0.0 <= stats["redundancy_reduction"] <= 1.0, "0 is not valid"
    assert stats["correlation"] >= 0.0, "Value must be greater than zero"


def test_mock_security_scanner(entangled_assessor):
    """Test MockSecurityScanner produces valid results."""
    scanner = MockSecurityScanner()

    audit_high = AuditResult(
        audit_id="TEST-001",
        score=0.2,
        risk_level="high",
        remediation_cost=1000.0,
        business_impact=0.9,
        violations=["Hardcoded secret key"],
    )
    result_high = scanner.scan_for_secrets(audit_high)

    assert "decision" in result_high, "Result must not be empty"
    assert "secrets_found" in result_high, "Result must not be empty"
    assert "confidence" in result_high, "Result must not be empty"
    assert result_high["decision"] in ["BLOCK", "MONITOR", "ALLOW"]

    audit_low = AuditResult(
        audit_id="TEST-002",
        score=0.9,
        risk_level="low",
        remediation_cost=10.0,
        business_impact=0.3,
        violations=["Code quality issue"],
    )
    result_low = scanner.scan_for_secrets(audit_low)

    assert result_low["decision"] == "ALLOW", "Result must not be empty"
