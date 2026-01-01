"""
Tests for CognitiveAgent base class.
"""
import pytest
from pathlib import Path
from typing import Any, Dict
from ..base_agent import CognitiveAgent


class MockAgent(CognitiveAgent):
    """Mock agent for testing."""
    
    def perceive(self, task: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "parsed_inputs": task.get("parameters", {}),
            "patterns": ["test_pattern"],
            "risks": [],
            "opportunities": []
        }
    
    def decide(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "strategy": "test_strategy",
            "steps": ["step1", "step2"],
            "priority": 5,
            "rationale": "Test rationale",
            "estimated_time": 10
        }
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "outputs": {"result": "test"},
            "steps_completed": decision["steps"],
            "logs": ["Log 1", "Log 2"]
        }
    
    def aftermath(
        self, 
        result: Dict[str, Any],
        context: Dict[str, Any],
        decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "metrics": {"test_metric": 1},
            "patterns": ["aftermath_pattern"],
            "lessons": ["test_lesson"],
            "recommendations": []
        }


def test_cognitive_agent_initialization():
    """Test agent initialization."""
    agent = MockAgent(name="test-agent", version="1.0.0")
    
    assert agent.name == "test-agent"
    assert agent.version == "1.0.0"
    assert agent.workspace == Path.cwd()
    assert agent.session_id is None
    assert agent.cognitive_brain is None


def test_cognitive_agent_metadata():
    """Test agent metadata."""
    agent = MockAgent(name="test-agent", version="1.0.0")
    metadata = agent.get_metadata()
    
    assert metadata["name"] == "test-agent"
    assert metadata["version"] == "1.0.0"
    assert metadata["pda_loop_enabled"] is True
    assert metadata["aftermath_enabled"] is True
    assert metadata["cognitive_brain_connected"] is False


def test_execute_pda_loop_success():
    """Test successful PDA loop execution."""
    agent = MockAgent(name="test-agent", version="1.0.0")
    
    task = {
        "task_type": "test",
        "parameters": {"param1": "value1"}
    }
    
    result = agent.execute_pda_loop(task)
    
    assert result["status"] == "success"
    assert "metrics" in result
    assert "execution_time" in result["metrics"]
    assert result["lessons"] == ["test_lesson"]
    assert result["patterns"] == ["aftermath_pattern"]


def test_execute_pda_loop_error_handling():
    """Test PDA loop error handling."""
    
    class FailingAgent(CognitiveAgent):
        def perceive(self, task):
            raise ValueError("Test error")
        
        def decide(self, context):
            return {}
        
        def act(self, decision):
            return {}
        
        def aftermath(self, result, context, decision):
            return {"metrics": {}, "lessons": ["error_lesson"]}
    
    agent = FailingAgent(name="failing-agent", version="1.0.0")
    result = agent.execute_pda_loop({"task_type": "test"})
    
    assert result["status"] == "error"
    assert "error" in result
    assert result["error"] == "Test error"
    assert "execution_time" in result["metrics"]


def test_set_cognitive_brain():
    """Test setting cognitive brain."""
    agent = MockAgent(name="test-agent", version="1.0.0")
    
    class MockBrain:
        pass
    
    brain = MockBrain()
    agent.set_cognitive_brain(brain)
    
    assert agent.cognitive_brain is brain
    assert agent.get_metadata()["cognitive_brain_connected"] is True


def test_set_session_id():
    """Test setting session ID."""
    agent = MockAgent(name="test-agent", version="1.0.0")
    
    agent.set_session_id("session-123")
    assert agent.session_id == "session-123"
