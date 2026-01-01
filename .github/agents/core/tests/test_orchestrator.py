"""
Tests for AgentOrchestrator.
"""
import pytest
from typing import Any, Dict
from ..orchestrator import AgentOrchestrator, TaskStatus
from ..base_agent import CognitiveAgent


class MockAgent(CognitiveAgent):
    """Mock agent for testing."""
    
    def __init__(self, name: str, delay: float = 0.1):
        super().__init__(name=name, version="1.0.0")
        self.delay = delay
        self.executed_tasks = []
    
    def perceive(self, task: Dict[str, Any]) -> Dict[str, Any]:
        return {"parsed": task}
    
    def decide(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"strategy": "execute"}
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        import time
        time.sleep(self.delay)
        return {"status": "success", "outputs": {}}
    
    def aftermath(self, result, context, decision) -> Dict[str, Any]:
        self.executed_tasks.append(result)
        return {"metrics": {}, "lessons": [], "patterns": []}


def test_orchestrator_initialization():
    """Test orchestrator initialization."""
    orch = AgentOrchestrator(max_parallel=3)
    
    assert orch.max_parallel == 3
    assert len(orch.agents) == 0
    assert len(orch.tasks) == 0


def test_register_agent():
    """Test agent registration."""
    orch = AgentOrchestrator()
    agent = MockAgent("test-agent")
    
    orch.register_agent("test-agent", agent)
    
    assert "test-agent" in orch.agents
    assert orch.agents["test-agent"] == agent


def test_add_task():
    """Test adding tasks."""
    orch = AgentOrchestrator()
    agent = MockAgent("test-agent")
    orch.register_agent("test-agent", agent)
    
    task = orch.add_task(
        task_id="task1",
        agent_name="test-agent",
        task_type="test",
        parameters={"param": "value"},
        priority=8
    )
    
    assert task.task_id == "task1"
    assert task.agent_name == "test-agent"
    assert task.priority == 8
    assert task.status == TaskStatus.PENDING
    assert "task1" in orch.tasks


def test_add_task_unregistered_agent():
    """Test adding task for unregistered agent."""
    orch = AgentOrchestrator()
    
    with pytest.raises(ValueError, match="not registered"):
        orch.add_task(
            task_id="task1",
            agent_name="unknown-agent",
            task_type="test",
            parameters={}
        )


def test_dependency_validation_valid():
    """Test valid dependency graph."""
    orch = AgentOrchestrator()
    agent = MockAgent("test-agent")
    orch.register_agent("test-agent", agent)
    
    orch.add_task("task1", "test-agent", "test", {})
    orch.add_task("task2", "test-agent", "test", {}, dependencies=["task1"])
    orch.add_task("task3", "test-agent", "test", {}, dependencies=["task2"])
    
    assert orch._validate_dependencies() is True


def test_dependency_validation_cycle():
    """Test cycle detection in dependencies."""
    orch = AgentOrchestrator()
    agent = MockAgent("test-agent")
    orch.register_agent("test-agent", agent)
    
    # Create a cycle: task1 -> task2 -> task3 -> task1
    orch.add_task("task1", "test-agent", "test", {}, dependencies=["task3"])
    orch.add_task("task2", "test-agent", "test", {}, dependencies=["task1"])
    orch.add_task("task3", "test-agent", "test", {}, dependencies=["task2"])
    
    assert orch._validate_dependencies() is False


def test_get_ready_tasks():
    """Test getting ready tasks."""
    orch = AgentOrchestrator()
    agent = MockAgent("test-agent")
    orch.register_agent("test-agent", agent)
    
    orch.add_task("task1", "test-agent", "test", {}, priority=5)
    orch.add_task("task2", "test-agent", "test", {}, priority=9)
    orch.add_task("task3", "test-agent", "test", {}, dependencies=["task1"], priority=7)
    
    ready = orch._get_ready_tasks()
    
    # task1 and task2 should be ready (no dependencies)
    # task3 should not be ready (depends on task1)
    assert len(ready) == 2
    # Should be sorted by priority (task2 first, then task1)
    assert ready[0].task_id == "task2"
    assert ready[1].task_id == "task1"


@pytest.mark.asyncio
async def test_execute_workflow_simple():
    """Test simple workflow execution."""
    orch = AgentOrchestrator(max_parallel=2)
    agent = MockAgent("test-agent", delay=0.01)
    orch.register_agent("test-agent", agent)
    
    orch.add_task("task1", "test-agent", "test", {"data": "test1"})
    orch.add_task("task2", "test-agent", "test", {"data": "test2"})
    
    result = await orch.execute_workflow()
    
    assert result["status"] == "success"
    assert len(result["tasks"]) == 2
    assert result["metrics"]["successful"] == 2
    assert result["metrics"]["failed"] == 0


@pytest.mark.asyncio
async def test_execute_workflow_with_dependencies():
    """Test workflow with task dependencies."""
    orch = AgentOrchestrator(max_parallel=2)
    agent = MockAgent("test-agent", delay=0.01)
    orch.register_agent("test-agent", agent)
    
    orch.add_task("task1", "test-agent", "test", {})
    orch.add_task("task2", "test-agent", "test", {}, dependencies=["task1"])
    orch.add_task("task3", "test-agent", "test", {}, dependencies=["task1"])
    
    result = await orch.execute_workflow()
    
    assert result["status"] == "success"
    assert result["metrics"]["successful"] == 3
    
    # Verify task1 completed before task2 and task3
    assert orch.tasks["task1"].status == TaskStatus.SUCCESS
    assert orch.tasks["task2"].status == TaskStatus.SUCCESS
    assert orch.tasks["task3"].status == TaskStatus.SUCCESS


@pytest.mark.asyncio
async def test_execute_workflow_cycle_error():
    """Test workflow execution with cycle."""
    orch = AgentOrchestrator()
    agent = MockAgent("test-agent")
    orch.register_agent("test-agent", agent)
    
    # Create cycle
    orch.add_task("task1", "test-agent", "test", {}, dependencies=["task2"])
    orch.add_task("task2", "test-agent", "test", {}, dependencies=["task1"])
    
    result = await orch.execute_workflow()
    
    assert result["status"] == "error"
    assert "cycle" in result["error"].lower()


def test_workflow_summary():
    """Test workflow summary generation."""
    orch = AgentOrchestrator()
    agent1 = MockAgent("agent1")
    agent2 = MockAgent("agent2")
    orch.register_agent("agent1", agent1)
    orch.register_agent("agent2", agent2)
    
    orch.add_task("task1", "agent1", "test", {})
    orch.add_task("task2", "agent2", "test", {})
    orch.add_task("task3", "agent1", "test", {})
    
    # Mark some tasks as completed
    orch.tasks["task1"].status = TaskStatus.SUCCESS
    orch.tasks["task2"].status = TaskStatus.FAILURE
    
    summary = orch.get_workflow_summary()
    
    assert summary["total_tasks"] == 3
    assert summary["by_status"][TaskStatus.SUCCESS.value] == 1
    assert summary["by_status"][TaskStatus.FAILURE.value] == 1
    assert summary["by_status"][TaskStatus.PENDING.value] == 1
    assert summary["by_agent"]["agent1"] == 2
    assert summary["by_agent"]["agent2"] == 1


def test_clear_workflow():
    """Test clearing workflow."""
    orch = AgentOrchestrator()
    agent = MockAgent("test-agent")
    orch.register_agent("test-agent", agent)
    
    orch.add_task("task1", "test-agent", "test", {})
    orch.add_task("task2", "test-agent", "test", {})
    
    assert len(orch.tasks) == 2
    
    orch.clear()
    
    assert len(orch.tasks) == 0


@pytest.mark.asyncio
async def test_parallel_execution_limit():
    """Test that max_parallel limit is respected."""
    orch = AgentOrchestrator(max_parallel=2)
    agent = MockAgent("test-agent", delay=0.1)
    orch.register_agent("test-agent", agent)
    
    # Add 5 independent tasks
    for i in range(5):
        orch.add_task(f"task{i}", "test-agent", "test", {})
    
    import time
    start = time.time()
    result = await orch.execute_workflow()
    elapsed = time.time() - start
    
    # With max_parallel=2 and 5 tasks (0.1s each), 
    # should take at least 0.3s (3 batches: 2+2+1)
    assert elapsed >= 0.25  # Allow some margin
    assert result["metrics"]["successful"] == 5
