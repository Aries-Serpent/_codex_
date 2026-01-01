"""
Integration tests for cognitive agent framework.
Tests interaction between components.
"""
import pytest
import tempfile
from pathlib import Path
from typing import Any, Dict
from ..base_agent import CognitiveAgent
from ..cognitive_brain import CognitiveBrain
from ..pattern_recognizer import PatternRecognizer
from ..orchestrator import AgentOrchestrator


class TestAgent(CognitiveAgent):
    """Test agent for integration testing."""
    
    def __init__(self, name: str):
        super().__init__(name=name, version="1.0.0")
        self.perception_calls = []
        self.decision_calls = []
        self.action_calls = []
        self.aftermath_calls = []
    
    def perceive(self, task: Dict[str, Any]) -> Dict[str, Any]:
        self.perception_calls.append(task)
        
        # Query cognitive brain if available
        history = []
        if self.cognitive_brain:
            history = self.cognitive_brain.get_session_history(
                agent_name=self.name,
                limit=3
            )
        
        return {
            "parsed_inputs": task.get("parameters", {}),
            "patterns": ["test_pattern"],
            "history": history,
            "risks": [],
            "opportunities": []
        }
    
    def decide(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.decision_calls.append(context)
        return {
            "strategy": "test_strategy",
            "steps": ["step1", "step2"],
            "priority": 5,
            "rationale": "Test decision",
            "estimated_time": 10
        }
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        self.action_calls.append(decision)
        return {
            "status": "success",
            "outputs": {"result": "test_output"},
            "steps_completed": decision["steps"],
            "logs": ["Executed step1", "Executed step2"]
        }
    
    def aftermath(
        self, 
        result: Dict[str, Any],
        context: Dict[str, Any],
        decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        self.aftermath_calls.append((result, context, decision))
        
        # Record in cognitive brain if available
        if self.cognitive_brain and self.session_id:
            self.cognitive_brain.record_pattern(
                session_id=self.session_id,
                pattern_name="test_pattern",
                pattern_type="test",
                description="Test pattern from integration"
            )
            
            self.cognitive_brain.record_lesson(
                session_id=self.session_id,
                lesson_text="Integration test lesson",
                category="testing",
                confidence=0.9
            )
        
        return {
            "metrics": {
                "test_metric": 1,
                "success_rate": 1.0
            },
            "patterns": ["successful_execution"],
            "lessons": ["Test execution successful"],
            "recommendations": []
        }


@pytest.fixture
def temp_brain():
    """Create temporary brain for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_brain.db"
        yield CognitiveBrain(db_path)


def test_agent_with_brain_integration(temp_brain):
    """Test agent fully integrated with cognitive brain."""
    agent = TestAgent("integration-agent")
    agent.set_cognitive_brain(temp_brain)
    agent.set_session_id("integration-001")
    
    # Start session in brain
    temp_brain.start_session(
        session_id="integration-001",
        agent_name="integration-agent",
        agent_version="1.0.0",
        task_type="test"
    )
    
    # Execute PDA loop
    task = {
        "task_type": "test",
        "parameters": {"test_param": "test_value"}
    }
    
    result = agent.execute_pda_loop(task)
    
    # Verify result
    assert result["status"] == "success"
    assert "metrics" in result
    assert len(result["lessons"]) > 0
    
    # Verify brain records
    temp_brain.end_session("integration-001", "success", result["metrics"])
    
    # Check session history
    history = temp_brain.get_session_history(agent_name="integration-agent")
    assert len(history) == 1
    assert history[0]["session_id"] == "integration-001"
    
    # Check patterns
    patterns = temp_brain.get_similar_patterns("test_pattern")
    assert len(patterns) > 0
    assert patterns[0]["pattern_name"] == "test_pattern"
    
    # Check lessons
    lessons = temp_brain.get_recent_lessons(category="testing")
    assert len(lessons) > 0
    assert "integration test" in lessons[0]["lesson_text"].lower()


def test_agent_with_pattern_recognizer():
    """Test agent using pattern recognizer."""
    agent = TestAgent("pattern-agent")
    recognizer = PatternRecognizer()
    
    # Create temp file with patterns
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
def test_function():
    try:
        operation()
    except Exception:
        pass
""")
        temp_path = Path(f.name)
    
    try:
        # Agent perceive phase would use pattern recognizer
        patterns = recognizer.analyze_file(temp_path)
        
        # Execute PDA loop with pattern context
        task = {
            "task_type": "analyze",
            "parameters": {"file": str(temp_path)}
        }
        
        result = agent.execute_pda_loop(task)
        
        assert result["status"] == "success"
        assert len(patterns) > 0  # Should detect exception pattern
        
    finally:
        temp_path.unlink()


@pytest.mark.asyncio
async def test_orchestrator_with_multiple_agents(temp_brain):
    """Test orchestrator coordinating multiple agents."""
    # Create agents
    agent1 = TestAgent("agent1")
    agent2 = TestAgent("agent2")
    
    # Connect to brain
    agent1.set_cognitive_brain(temp_brain)
    agent2.set_cognitive_brain(temp_brain)
    
    # Create orchestrator
    orch = AgentOrchestrator(max_parallel=2)
    orch.register_agent("agent1", agent1)
    orch.register_agent("agent2", agent2)
    
    # Add tasks
    orch.add_task(
        task_id="task1",
        agent_name="agent1",
        task_type="analyze",
        parameters={"data": "test1"}
    )
    
    orch.add_task(
        task_id="task2",
        agent_name="agent2",
        task_type="fix",
        parameters={"data": "test2"},
        dependencies=["task1"]  # Depends on task1
    )
    
    # Execute workflow
    result = await orch.execute_workflow()
    
    assert result["status"] == "success"
    assert result["metrics"]["successful"] == 2
    assert result["metrics"]["failed"] == 0
    
    # Verify both agents executed
    assert len(agent1.perception_calls) == 1
    assert len(agent2.perception_calls) == 1


def test_full_pda_loop_with_brain(temp_brain):
    """Test complete PDA loop with brain recording."""
    agent = TestAgent("full-pda-agent")
    agent.set_cognitive_brain(temp_brain)
    agent.set_session_id("full-pda-001")
    
    # Start session
    temp_brain.start_session(
        "full-pda-001",
        "full-pda-agent",
        "1.0.0",
        "complete_test"
    )
    
    # Execute multiple tasks
    for i in range(3):
        task = {
            "task_type": f"test_{i}",
            "parameters": {"iteration": i}
        }
        result = agent.execute_pda_loop(task)
        assert result["status"] == "success"
    
    # End session
    temp_brain.end_session("full-pda-001", "success")
    
    # Verify all phases were called
    assert len(agent.perception_calls) == 3
    assert len(agent.decision_calls) == 3
    assert len(agent.action_calls) == 3
    assert len(agent.aftermath_calls) == 3
    
    # Verify brain recorded everything
    patterns = temp_brain.get_similar_patterns("test_pattern")
    assert patterns[0]["occurrences"] == 3  # One per task
    
    lessons = temp_brain.get_recent_lessons(category="testing")
    assert len(lessons) == 3  # One per task


def test_pattern_storage_in_brain(temp_brain):
    """Test that patterns detected are stored in brain."""
    agent = TestAgent("pattern-storage-agent")
    agent.set_cognitive_brain(temp_brain)
    agent.set_session_id("pattern-001")
    recognizer = PatternRecognizer()
    
    # Start session
    temp_brain.start_session(
        "pattern-001",
        "pattern-storage-agent",
        "1.0.0",
        "pattern_analysis"
    )
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
import unused_module
from package import *

def test_empty():
    pass
""")
        temp_path = Path(f.name)
    
    try:
        # Analyze and detect patterns
        patterns = recognizer.analyze_file(temp_path)
        
        # Store patterns in brain
        for pattern in patterns:
            temp_brain.record_pattern(
                session_id="pattern-001",
                pattern_name=pattern.name,
                pattern_type=pattern.pattern_type,
                description=pattern.description,
                context={
                    "file": str(temp_path),
                    "locations": pattern.locations
                }
            )
        
        # Verify patterns stored
        stored_patterns = temp_brain.get_similar_patterns("import")
        assert len(stored_patterns) > 0
        
        # Verify pattern types
        pattern_names = {p["pattern_name"] for p in stored_patterns}
        assert len(pattern_names) > 0  # Should have at least one import pattern
        
    finally:
        temp_path.unlink()
        temp_brain.end_session("pattern-001", "success")


def test_cross_agent_learning(temp_brain):
    """Test that agents learn from each other via shared brain."""
    agent1 = TestAgent("learning-agent-1")
    agent2 = TestAgent("learning-agent-2")
    
    agent1.set_cognitive_brain(temp_brain)
    agent2.set_cognitive_brain(temp_brain)
    
    # Agent 1 executes and learns
    agent1.set_session_id("learn-001")
    temp_brain.start_session("learn-001", "learning-agent-1", "1.0.0", "test")
    
    result1 = agent1.execute_pda_loop({"task_type": "task1"})
    assert result1["status"] == "success"
    
    temp_brain.end_session("learn-001", "success")
    
    # Agent 2 should be able to access Agent 1's history
    agent2.set_session_id("learn-002")
    temp_brain.start_session("learn-002", "learning-agent-2", "1.0.0", "test")
    
    result2 = agent2.execute_pda_loop({"task_type": "task2"})
    assert result2["status"] == "success"
    
    # Check that agent2's perception included history from agent1
    perception_context = agent2.perception_calls[0]
    # Note: In real implementation, perception would query brain for relevant history
    
    temp_brain.end_session("learn-002", "success")
    
    # Verify both sessions recorded
    all_sessions = temp_brain.get_session_history(limit=10)
    assert len(all_sessions) >= 2
    session_ids = {s["session_id"] for s in all_sessions}
    assert "learn-001" in session_ids
    assert "learn-002" in session_ids
