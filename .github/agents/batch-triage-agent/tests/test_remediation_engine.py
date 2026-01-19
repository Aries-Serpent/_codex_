"""Tests for RemediationEngine."""

import sys
import tempfile
from pathlib import Path

# Add parent directories to path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR.parent / "src"))

from remediation_engine import (
    RemediationEngine,
    RemediationAction,
    RiskLevel,
    RemediationType,
)


def test_remediation_engine_initialization():
    """Test remediation engine initializes correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = RemediationEngine(
            repo_root=Path(tmpdir),
            dry_run=True,
        )
        
        assert engine.repo_root == Path(tmpdir)
        assert engine.dry_run is True


def test_remediation_action_dataclass():
    """Test RemediationAction dataclass."""
    action = RemediationAction(
        action_id="test_action_1",
        remediation_type=RemediationType.CODE_FIX,
        risk_level=RiskLevel.MEDIUM,
        confidence=0.7,
        description="Fix test assertion",
    )
    
    assert action.action_id == "test_action_1"
    assert action.approval_required is True
    assert action.manual_steps == []


def test_generate_test_failure_remediations():
    """Test remediation generation for test failures."""
    engine = RemediationEngine(dry_run=True)
    
    actions = engine.generate_remediation(
        failure_type="test_failure",
        root_cause="Assertion failed: expected 5, got 3",
        detected_issues=[],
        suggested_actions=[],
        confidence=0.7,
    )
    
    assert len(actions) > 0
    assert any(a.remediation_type == RemediationType.CODE_FIX for a in actions)


def test_generate_import_error_remediations():
    """Test remediation generation for import errors."""
    engine = RemediationEngine(dry_run=True)
    
    actions = engine.generate_remediation(
        failure_type="import_error",
        root_cause="ModuleNotFoundError: No module named 'pytest'",
        detected_issues=[],
        suggested_actions=[],
        confidence=0.8,
    )
    
    assert len(actions) > 0
    assert any(a.remediation_type == RemediationType.DEPENDENCY_UPDATE for a in actions)
    assert any("pytest" in a.description for a in actions)


def test_generate_lint_error_remediations():
    """Test remediation generation for lint errors."""
    engine = RemediationEngine(dry_run=True)
    
    actions = engine.generate_remediation(
        failure_type="lint_error",
        root_cause="Lint errors found",
        detected_issues=[],
        suggested_actions=[],
        confidence=0.9,
    )
    
    assert len(actions) > 0
    assert any(a.remediation_type == RemediationType.CODE_FIX for a in actions)
    assert any("ruff" in a.automated_fix for a in actions if a.automated_fix)


def test_classify_risk():
    """Test risk classification."""
    engine = RemediationEngine(dry_run=True)
    
    # Low risk action
    low_risk = RemediationAction(
        action_id="low_1",
        remediation_type=RemediationType.RERUN,
        risk_level=RiskLevel.LOW,
        confidence=0.95,
        description="Rerun tests",
    )
    
    assert engine.classify_risk(low_risk) == RiskLevel.LOW
    
    # High risk action
    high_risk = RemediationAction(
        action_id="high_1",
        remediation_type=RemediationType.CODE_FIX,
        risk_level=RiskLevel.HIGH,
        confidence=0.4,
        description="Fix code",
    )
    
    assert engine.classify_risk(high_risk) == RiskLevel.HIGH


def test_filter_by_risk():
    """Test filtering actions by risk level."""
    engine = RemediationEngine(dry_run=True)
    
    # Add some actions
    engine.actions = [
        RemediationAction(
            action_id="low_1",
            remediation_type=RemediationType.RERUN,
            risk_level=RiskLevel.LOW,
            confidence=0.9,
            description="Low risk",
        ),
        RemediationAction(
            action_id="high_1",
            remediation_type=RemediationType.CODE_FIX,
            risk_level=RiskLevel.HIGH,
            confidence=0.5,
            description="High risk",
        ),
    ]
    
    low_risk_actions = engine.filter_by_risk(RiskLevel.LOW)
    
    assert len(low_risk_actions) == 1
    assert low_risk_actions[0].action_id == "low_1"


def test_apply_action_dry_run():
    """Test applying action in dry run mode."""
    engine = RemediationEngine(dry_run=True)
    
    action = RemediationAction(
        action_id="test_1",
        remediation_type=RemediationType.RERUN,
        risk_level=RiskLevel.LOW,
        confidence=0.95,
        description="Test action",
        automated_fix="echo 'test'",
    )
    action.approval_required = False
    
    result = engine.apply_action(action)
    
    assert result["success"] is True
    assert result["dry_run"] is True


def test_apply_action_requires_approval():
    """Test that action requiring approval is not auto-applied."""
    engine = RemediationEngine(dry_run=False)
    
    action = RemediationAction(
        action_id="test_2",
        remediation_type=RemediationType.CODE_FIX,
        risk_level=RiskLevel.HIGH,
        confidence=0.6,
        description="High risk action",
        automated_fix="echo 'dangerous'",
    )
    
    result = engine.apply_action(action)
    
    assert result["success"] is False
    assert "Approval required" in result["error"]


def test_generate_report():
    """Test generating remediation report."""
    engine = RemediationEngine(dry_run=True)
    
    # Add some actions
    engine.actions = [
        RemediationAction(
            action_id="low_1",
            remediation_type=RemediationType.RERUN,
            risk_level=RiskLevel.LOW,
            confidence=0.95,
            description="Low risk",
        ),
        RemediationAction(
            action_id="med_1",
            remediation_type=RemediationType.CONFIG_FIX,
            risk_level=RiskLevel.MEDIUM,
            confidence=0.7,
            description="Medium risk",
        ),
    ]
    engine.actions[0].approval_required = False
    
    report = engine.generate_report()
    
    assert report["total_actions"] == 2
    assert report["by_risk_level"]["low"] == 1
    assert report["by_risk_level"]["medium"] == 1
    assert report["auto_appliable"] == 1
    assert report["requires_approval"] == 1
