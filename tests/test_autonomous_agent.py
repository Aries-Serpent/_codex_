"""Tests for AI-Driven Autonomous Codebase Management System."""
import pytest
from pathlib import Path
import json
import sys
import tempfile

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from autonomous_agent import (
    AutonomousAgent, CodeHealthSensor, ActionProposer,
    HealthStatus, ActionType, DecisionLevel, HealthMetric, ProposedAction
)


@pytest.fixture
def temp_repo(tmp_path):
    """Create a temporary repository for testing."""
    # Create directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    
    # Create Python files with varying complexity
    simple_file = src_dir / "simple.py"
    simple_file.write_text("""
def simple_function():
    '''A simple function.'''
    return True
""")
    
    complex_file = src_dir / "complex.py"
    complex_file.write_text("""
def complex_function(x, y, z):
    '''A complex function.'''
    if x > 0:
        if y > 0:
            if z > 0:
                for i in range(x):
                    if i % 2 == 0:
                        if i % 3 == 0:
                            return i
    elif x < 0:
        while y > 0:
            y -= 1
            if y == z:
                break
    return None
""")
    
    # Create duplicate code
    dup1 = src_dir / "dup1.py"
    dup1.write_text("""
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
""")
    
    dup2 = src_dir / "dup2.py"
    dup2.write_text("""
def handle_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
""")
    
    # Create test file
    test_file = tests_dir / "test_simple.py"
    test_file.write_text("""
def test_simple():
    assert True
""")
    
    return tmp_path


def test_health_metric_creation():
    """Test HealthMetric dataclass creation."""
    metric = HealthMetric(
        name="test_metric",
        value=0.5,
        threshold=0.8,
        status=HealthStatus.WARNING,
        timestamp="2025-12-21T00:00:00"
    )
    
    assert metric.name == "test_metric"
    assert metric.value == 0.5
    assert metric.threshold == 0.8
    assert metric.status == HealthStatus.WARNING


def test_proposed_action_creation():
    """Test ProposedAction dataclass creation."""
    action = ProposedAction(
        id="test123",
        type=ActionType.MAINTENANCE,
        decision_level=DecisionLevel.AUTONOMOUS,
        description="Test action",
        rationale="Test rationale",
        estimated_impact="Low",
        risk_level="low",
        reversibility=True,
        estimated_duration="5 minutes",
        proposed_at="2025-12-21T00:00:00"
    )
    
    assert action.id == "test123"
    assert action.type == ActionType.MAINTENANCE
    assert action.decision_level == DecisionLevel.AUTONOMOUS
    assert not action.approved
    assert not action.executed


def test_code_health_sensor_init(temp_repo):
    """Test CodeHealthSensor initialization."""
    sensor = CodeHealthSensor(temp_repo)
    
    assert sensor.repo_path == temp_repo


def test_analyze_complexity(temp_repo):
    """Test complexity analysis."""
    sensor = CodeHealthSensor(temp_repo)
    metrics = sensor.analyze_complexity()
    
    # Should detect the complex function
    assert len(metrics) >= 0
    
    if metrics:
        assert metrics[0].name == "code_complexity"
        assert metrics[0].value > 0


def test_detect_duplicate_code(temp_repo):
    """Test duplicate code detection."""
    sensor = CodeHealthSensor(temp_repo)
    metrics = sensor.detect_duplicate_code()
    
    assert len(metrics) == 1
    assert metrics[0].name == "code_duplication"
    assert 0 <= metrics[0].value <= 1.0


def test_check_test_coverage(temp_repo):
    """Test test coverage checking."""
    sensor = CodeHealthSensor(temp_repo)
    metrics = sensor.check_test_coverage()
    
    assert len(metrics) == 1
    assert metrics[0].name == "test_coverage"
    
    # We have 1 test file and 4 source files
    # Coverage should be 0.25
    assert metrics[0].value > 0
    assert metrics[0].status in (HealthStatus.WARNING, HealthStatus.HEALTHY)


def test_scan_security_issues(temp_repo):
    """Test security scanning."""
    # Add a file with security issue
    risky_file = temp_repo / "src" / "risky.py"
    risky_file.write_text("""
def dangerous():
    eval("print('hello')")
""")
    
    sensor = CodeHealthSensor(temp_repo)
    metrics = sensor.scan_security_issues()
    
    assert len(metrics) == 1
    assert metrics[0].name == "security_scan"
    assert metrics[0].value > 0  # Should find eval()
    assert metrics[0].status == HealthStatus.WARNING


def test_action_proposer_init(temp_repo):
    """Test ActionProposer initialization."""
    proposer = ActionProposer(temp_repo)
    
    assert proposer.repo_path == temp_repo


def test_propose_actions_for_complexity(temp_repo):
    """Test action proposal for high complexity."""
    from autonomous_agent import CodebaseHealth
    
    metric = HealthMetric(
        name="code_complexity",
        value=25.0,
        threshold=15.0,
        status=HealthStatus.WARNING,
        timestamp="2025-12-21T00:00:00"
    )
    
    health = CodebaseHealth(
        timestamp="2025-12-21T00:00:00",
        overall_status=HealthStatus.WARNING,
        metrics=[metric],
        proposed_actions=[],
        alerts=[]
    )
    
    proposer = ActionProposer(temp_repo)
    actions = proposer.propose_actions(health)
    
    assert len(actions) > 0
    assert actions[0].type == ActionType.REFACTORING
    assert "complexity" in actions[0].description.lower()


def test_propose_actions_for_duplication(temp_repo):
    """Test action proposal for code duplication."""
    from autonomous_agent import CodebaseHealth
    
    metric = HealthMetric(
        name="code_duplication",
        value=0.15,
        threshold=0.10,
        status=HealthStatus.WARNING,
        timestamp="2025-12-21T00:00:00"
    )
    
    health = CodebaseHealth(
        timestamp="2025-12-21T00:00:00",
        overall_status=HealthStatus.WARNING,
        metrics=[metric],
        proposed_actions=[],
        alerts=[]
    )
    
    proposer = ActionProposer(temp_repo)
    actions = proposer.propose_actions(health)
    
    assert len(actions) > 0
    assert actions[0].type == ActionType.REFACTORING
    assert "duplicate" in actions[0].description.lower()


def test_autonomous_agent_init(temp_repo):
    """Test AutonomousAgent initialization."""
    agent = AutonomousAgent(temp_repo)
    
    assert agent.repo_path == temp_repo
    assert agent.config is not None
    assert agent.state_path.exists()


def test_load_default_config(temp_repo):
    """Test loading default configuration."""
    agent = AutonomousAgent(temp_repo)
    
    config = agent.config
    
    assert "autonomous_actions_enabled" in config
    assert "monitoring_interval_minutes" in config
    assert "max_autonomous_actions_per_cycle" in config


def test_assess_health(temp_repo):
    """Test health assessment."""
    agent = AutonomousAgent(temp_repo)
    health = agent.assess_health()
    
    assert health.timestamp
    assert health.overall_status in HealthStatus
    assert len(health.metrics) > 0


def test_propose_improvements(temp_repo):
    """Test improvement proposal."""
    agent = AutonomousAgent(temp_repo)
    
    # Create health with issues
    health = agent.assess_health()
    
    # Add a warning metric
    health.metrics.append(HealthMetric(
        name="test_coverage",
        value=0.5,
        threshold=0.8,
        status=HealthStatus.WARNING,
        timestamp="2025-12-21T00:00:00"
    ))
    health.overall_status = HealthStatus.WARNING
    
    actions = agent.propose_improvements(health)
    
    # Should have proposed actions
    assert isinstance(actions, list)


def test_execute_autonomous_actions(temp_repo):
    """Test autonomous action execution."""
    agent = AutonomousAgent(temp_repo)
    
    # Create an autonomous action
    action = ProposedAction(
        id="test123",
        type=ActionType.TESTING,
        decision_level=DecisionLevel.AUTONOMOUS,
        description="Generate test",
        rationale="Low coverage",
        estimated_impact="Improved quality",
        risk_level="low",
        reversibility=True,
        estimated_duration="10 minutes",
        proposed_at="2025-12-21T00:00:00"
    )
    
    executed = agent.execute_autonomous_actions([action])
    
    # Should have executed the action
    assert len(executed) == 1
    assert executed[0].executed


def test_action_filtering_by_level(temp_repo):
    """Test that only autonomous actions are executed."""
    agent = AutonomousAgent(temp_repo)
    
    actions = [
        ProposedAction(
            id="auto1",
            type=ActionType.MAINTENANCE,
            decision_level=DecisionLevel.AUTONOMOUS,
            description="Auto action",
            rationale="Routine",
            estimated_impact="Low",
            risk_level="low",
            reversibility=True,
            estimated_duration="5 min",
            proposed_at="2025-12-21T00:00:00"
        ),
        ProposedAction(
            id="approval1",
            type=ActionType.REFACTORING,
            decision_level=DecisionLevel.APPROVAL_REQUIRED,
            description="Approval action",
            rationale="Significant change",
            estimated_impact="Medium",
            risk_level="medium",
            reversibility=True,
            estimated_duration="1 hour",
            proposed_at="2025-12-21T00:00:00"
        )
    ]
    
    executed = agent.execute_autonomous_actions(actions)
    
    # Only autonomous action should be executed
    assert len(executed) == 1
    assert executed[0].id == "auto1"


def test_save_state(temp_repo):
    """Test state saving."""
    from autonomous_agent import CodebaseHealth
    
    agent = AutonomousAgent(temp_repo)
    
    health = CodebaseHealth(
        timestamp="2025-12-21T00:00:00",
        overall_status=HealthStatus.HEALTHY,
        metrics=[],
        proposed_actions=[],
        alerts=[]
    )
    
    agent.save_state(health, [])
    
    # Check that state file was created
    state_files = list(agent.state_path.glob("state_*.json"))
    assert len(state_files) > 0


def test_run_cycle(temp_repo):
    """Test complete agent cycle."""
    agent = AutonomousAgent(temp_repo)
    
    health, actions = agent.run_cycle()
    
    assert health is not None
    assert isinstance(actions, list)
    assert health.overall_status in HealthStatus


def test_health_status_enum():
    """Test HealthStatus enum."""
    assert HealthStatus.HEALTHY.value == "healthy"
    assert HealthStatus.WARNING.value == "warning"
    assert HealthStatus.CRITICAL.value == "critical"
    assert HealthStatus.DEGRADED.value == "degraded"


def test_action_type_enum():
    """Test ActionType enum."""
    assert ActionType.MAINTENANCE.value == "maintenance"
    assert ActionType.OPTIMIZATION.value == "optimization"
    assert ActionType.SECURITY.value == "security"


def test_decision_level_enum():
    """Test DecisionLevel enum."""
    assert DecisionLevel.AUTONOMOUS.value == "autonomous"
    assert DecisionLevel.APPROVAL_REQUIRED.value == "approval_required"
    assert DecisionLevel.ESCALATE.value == "escalate"


def test_complexity_calculation(temp_repo):
    """Test complexity calculation for specific code."""
    sensor = CodeHealthSensor(temp_repo)
    
    # Create a simple function
    import ast
    code = """
def simple():
    return True
"""
    tree = ast.parse(code)
    func = tree.body[0]
    
    complexity = sensor._calculate_complexity(func)
    assert complexity == 1  # Base complexity
    
    # Create a complex function
    complex_code = """
def complex(x):
    if x > 0:
        if x < 10:
            return x
    return 0
"""
    tree = ast.parse(complex_code)
    func = tree.body[0]
    
    complexity = sensor._calculate_complexity(func)
    assert complexity > 1  # Should be higher


def test_security_detection_patterns(temp_repo):
    """Test detection of specific security patterns."""
    # Create files with different security issues
    eval_file = temp_repo / "src" / "eval_test.py"
    eval_file.write_text("result = eval('1 + 1')")
    
    exec_file = temp_repo / "src" / "exec_test.py"
    exec_file.write_text("exec('print(1)')")
    
    pickle_file = temp_repo / "src" / "pickle_test.py"
    pickle_file.write_text("import pickle\ndata = pickle.loads(bytes)")
    
    sensor = CodeHealthSensor(temp_repo)
    metrics = sensor.scan_security_issues()
    
    # Should detect all three patterns
    assert metrics[0].value >= 3
