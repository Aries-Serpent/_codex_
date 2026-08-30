#!/usr/bin/env python3
"""
Tests for OODA Loop Executor - Phase 10.3

Target: > 95% code coverage
Test Categories:
- Phase execution (observe, orient, decide, act)
- State management & transitions
- Concurrency & isolation
- Graceful degradation
- Error handling & recovery
- Performance constraints
- Metrics collection
"""

import asyncio
import time
from datetime import datetime

import pytest

from scripts.cognitive.ooda_loop_executor import (
    ActionResult,
    ContextData,
    ContextProvider,
    DegradationLevel,
    ObservationData,
    OODAExecutor,
    OODAPhase,
    RiskLevel,
    StateProvider,
)


class MockStateProvider(StateProvider):
    """Mock state provider for testing."""
    
    def __init__(self, fail_on_call: str = None):
        self.fail_on_call = fail_on_call
        self.call_count = {}
    
    def get_repo_state(self):
        self._track_call("get_repo_state")
        if self.fail_on_call == "get_repo_state":
            raise Exception("Simulated repo state failure")
        return {
            "branch": "main",
            "uncommitted_changes": 0,
            "recent_commits": ["abc123", "def456"],
            "test_status": "passing",
        }
    
    def get_agent_state(self):
        self._track_call("get_agent_state")
        return {
            "health": 0.95,
            "queue_depth": 3,
            "performance": {
                "avg_latency_ms": 150.0,
                "success_rate": 0.92,
                "throughput": 10,
            },
        }
    
    def get_environment_state(self):
        self._track_call("get_environment_state")
        return {
            "ci_health": 0.85,
            "resource_utilization": {
                "cpu": 0.45,
                "memory": 0.62,
                "disk": 0.30,
            },
        }
    
    def get_task_context(self, task_id: str):
        self._track_call(f"get_task_context:{task_id}")
        return {
            "id": task_id,
            "priority": "P1",
            "dependencies": ["task_000"],
        }
    
    def _track_call(self, method_name: str):
        self.call_count[method_name] = self.call_count.get(method_name, 0) + 1


class MockContextProvider(ContextProvider):
    """Mock context provider for testing."""
    
    def __init__(self, degradation_level: DegradationLevel = DegradationLevel.FULL_CONTEXT):
        self.degradation_level = degradation_level
        self.call_count = {}
    
    async def get_patterns(self, observation, top_k=5):
        self._track_call("get_patterns")
        if self.degradation_level == DegradationLevel.NO_CONTEXT:
            return []
        return [
            {
                "pattern_id": "pat_001",
                "name": "CI Self-Healing Pattern",
                "similarity": 0.92,
                "success_rate": 0.88,
                "conditions": {"task_type": "ci_fix", "priority": "P1"},
                "tags": ["ci_self_healing", "automated"],
            }
        ]
    
    async def get_sessions(self, task_type, limit=3):
        self._track_call("get_sessions")
        if self.degradation_level in [DegradationLevel.NO_CONTEXT, DegradationLevel.PATTERN_ONLY]:
            return []
        return [
            {
                "session_id": "sess_001",
                "timestamp": datetime.now().isoformat(),
                "task_type": task_type,
                "success": True,
                "duration_ms": 250,
                "decisions": [{"decision_id": "dec_001", "strategy": "pattern_follow", "outcome": "success"}],
            }
        ]
    
    async def get_external_context(self):
        self._track_call("get_external_context")
        return {
            "advisory_issues": [],
            "repo_variables": {"CODEX_CI_FAILURE_RATE": "15.3:medium"},
            "ci_health": 0.85,
        }
    
    def _track_call(self, method_name: str):
        self.call_count[method_name] = self.call_count.get(method_name, 0) + 1


# ============================================================================
# Phase Execution Tests
# ============================================================================

@pytest.mark.asyncio
async def test_observe_phase_collects_state():
    """Test that OBSERVE phase collects complete state."""
    executor = OODAExecutor(state_provider=MockStateProvider())
    
    observation = await executor._observe("task_001", "ci_fix")
    
    assert observation is not None
    assert observation.repo_state is not None
    assert observation.task is not None
    assert observation.agent_state is not None
    assert observation.environment is not None
    assert observation.task["type"] == "ci_fix"
    assert len(observation.repo_state) > 0


@pytest.mark.asyncio
async def test_observe_phase_timing():
    """Test that OBSERVE phase completes within SLA."""
    executor = OODAExecutor(state_provider=MockStateProvider())
    
    start_time = time.time()
    observation = await executor._observe("task_001", "ci_fix")
    elapsed_ms = (time.time() - start_time) * 1000
    
    # Should complete much faster than 50ms target (mock implementation)
    assert elapsed_ms < 50, f"OBSERVE phase took {elapsed_ms:.1f}ms (target < 50ms)"


@pytest.mark.asyncio
async def test_orient_phase_with_full_context():
    """Test ORIENT phase with full context available."""
    executor = OODAExecutor(
        state_provider=MockStateProvider(),
        context_provider=MockContextProvider(DegradationLevel.FULL_CONTEXT),
    )
    
    observation = await executor._observe("task_001", "ci_fix")
    orientation = await executor._orient(observation)
    
    assert orientation is not None
    assert orientation.context.degradation_level == DegradationLevel.FULL_CONTEXT
    assert len(orientation.context.patterns) > 0
    assert len(orientation.context.sessions) > 0
    assert orientation.confidence > 0


@pytest.mark.asyncio
async def test_orient_phase_with_pattern_only_context():
    """Test ORIENT phase with pattern-only context."""
    executor = OODAExecutor(
        state_provider=MockStateProvider(),
        context_provider=MockContextProvider(DegradationLevel.PATTERN_ONLY),
    )
    
    observation = await executor._observe("task_001", "ci_fix")
    orientation = await executor._orient(observation)
    
    assert orientation.context.degradation_level == DegradationLevel.PATTERN_ONLY
    assert len(orientation.context.patterns) > 0
    assert len(orientation.context.sessions) == 0


@pytest.mark.asyncio
async def test_orient_phase_with_no_context():
    """Test ORIENT phase with no context (emergency mode)."""
    executor = OODAExecutor(
        state_provider=MockStateProvider(),
        context_provider=MockContextProvider(DegradationLevel.NO_CONTEXT),
    )
    
    observation = await executor._observe("task_001", "ci_fix")
    orientation = await executor._orient(observation)
    
    assert orientation.context.degradation_level == DegradationLevel.NO_CONTEXT
    assert len(orientation.context.patterns) == 0
    assert len(orientation.context.sessions) == 0


@pytest.mark.asyncio
async def test_decide_phase_selects_strategy():
    """Test DECIDE phase selects appropriate strategy."""
    executor = OODAExecutor(state_provider=MockStateProvider())
    
    observation = await executor._observe("task_001", "ci_fix")
    orientation = await executor._orient(observation)
    decision = await executor._decide(orientation, "P1")
    
    assert decision is not None
    assert len(decision.strategies) > 0
    assert decision.selected_strategy is not None
    assert decision.confidence_score >= 0.0
    assert decision.success_probability >= 0.0


@pytest.mark.asyncio
async def test_decide_phase_respects_degradation_level():
    """Test DECIDE phase generates appropriate strategies based on context."""
    # Full context
    executor_full = OODAExecutor(
        state_provider=MockStateProvider(),
        context_provider=MockContextProvider(DegradationLevel.FULL_CONTEXT),
    )
    obs_full = await executor_full._observe("task_001", "ci_fix")
    orient_full = await executor_full._orient(obs_full)
    decision_full = await executor_full._decide(orient_full, "P1")
    
    # No context
    executor_none = OODAExecutor(
        state_provider=MockStateProvider(),
        context_provider=MockContextProvider(DegradationLevel.NO_CONTEXT),
    )
    obs_none = await executor_none._observe("task_001", "ci_fix")
    orient_none = await executor_none._orient(obs_none)
    decision_none = await executor_none._decide(orient_none, "P1")
    
    # Full context should have more strategy options
    assert len(decision_full.strategies) >= len(decision_none.strategies)


@pytest.mark.asyncio
async def test_act_phase_executes_and_returns_result():
    """Test ACT phase executes strategy and returns result."""
    executor = OODAExecutor(state_provider=MockStateProvider())
    
    observation = await executor._observe("task_001", "ci_fix")
    orientation = await executor._orient(observation)
    decision = await executor._decide(orientation, "P1")
    result = await executor._act(decision)
    
    assert result is not None
    assert result.status in ["success", "partial", "failure"]
    assert result.execution_time_ms >= 0
    assert isinstance(result.metrics, dict)


# ============================================================================
# State Management Tests
# ============================================================================

@pytest.mark.asyncio
async def test_execute_cycle_complete_flow():
    """Test complete OODA cycle execution."""
    executor = OODAExecutor(state_provider=MockStateProvider())
    
    state = await executor.execute_cycle("task_001", "ci_fix", "P1")
    
    assert state.cycle_id is not None
    assert state.observation is not None
    assert state.orientation is not None
    assert state.decision is not None
    assert state.action_result is not None
    assert state.phase == OODAPhase.FEEDBACK
    assert "observe_ms" in state.metrics
    assert "orient_ms" in state.metrics
    assert "decide_ms" in state.metrics
    assert "act_ms" in state.metrics


@pytest.mark.asyncio
async def test_execute_cycle_timing_sla():
    """Test that complete cycle meets < 200ms SLA."""
    executor = OODAExecutor(state_provider=MockStateProvider())
    
    start_time = time.time()
    state = await executor.execute_cycle("task_001", "ci_fix", "P1")
    total_ms = (time.time() - start_time) * 1000
    
    # Mock implementation should complete much faster, but SLA is < 200ms
    assert total_ms < 200, f"Complete cycle took {total_ms:.1f}ms (target < 200ms)"


@pytest.mark.asyncio
async def test_ooda_state_to_dict():
    """Test OODAState serialization to dictionary."""
    executor = OODAExecutor(state_provider=MockStateProvider())
    
    state = await executor.execute_cycle("task_001", "ci_fix", "P1")
    state_dict = state.to_dict()
    
    assert state_dict["cycle_id"] is not None
    assert state_dict["phase"] == "feedback"
    assert state_dict["observation"] is not None
    assert state_dict["orientation"] is not None
    assert state_dict["decision"] is not None
    assert state_dict["action_result"] is not None
    assert "metrics" in state_dict


# ============================================================================
# Concurrency Tests
# ============================================================================

@pytest.mark.asyncio
async def test_concurrent_cycles_respect_limit():
    """Test that concurrent OODA cycles respect max_concurrent_loops limit."""
    executor = OODAExecutor(
        state_provider=MockStateProvider(),
        max_concurrent_loops=10,
    )
    
    # Launch 20 cycles
    tasks = [
        executor.execute_cycle(f"task_{i:03d}", "ci_fix", "P1")
        for i in range(20)
    ]
    
    results = await asyncio.gather(*tasks)
    
    assert len(results) == 20
    assert all(r.action_result is not None for r in results)


@pytest.mark.asyncio
async def test_concurrent_cycles_isolation():
    """Test that concurrent cycles have isolated state."""
    executor = OODAExecutor(state_provider=MockStateProvider())
    
    # Launch 5 concurrent cycles
    tasks = [
        executor.execute_cycle(f"task_{i:03d}", "ci_fix", "P1")
        for i in range(5)
    ]
    
    results = await asyncio.gather(*tasks)
    
    # Each should have unique cycle_id
    cycle_ids = [r.cycle_id for r in results]
    assert len(cycle_ids) == len(set(cycle_ids)), "Cycle IDs should be unique"


@pytest.mark.asyncio
async def test_metrics_aggregation_across_cycles():
    """Test that metrics are correctly aggregated across multiple cycles."""
    executor = OODAExecutor(state_provider=MockStateProvider())
    
    # Execute 5 cycles
    for i in range(5):
        await executor.execute_cycle(f"task_{i:03d}", "ci_fix", "P1")
    
    metrics = executor.get_metrics()
    
    assert metrics["total_cycles"] == 5
    assert metrics["successful_cycles"] > 0
    assert "observe_p50_ms" in metrics
    assert "observe_p99_ms" in metrics
    assert metrics["active_cycles"] == 0  # All should be completed


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.asyncio
async def test_ooda_handles_state_provider_failure():
    """Test graceful handling of state provider failures."""
    executor = OODAExecutor(state_provider=MockStateProvider(fail_on_call="get_agent_state"))
    
    # Should not crash, but handle error
    state = await executor.execute_cycle("task_001", "ci_fix", "P1")
    
    assert state.action_result.status == "failure"
    assert len(state.action_result.errors) > 0


@pytest.mark.asyncio
async def test_ooda_handles_missing_strategy():
    """Test graceful handling when no strategy can be selected."""
    executor = OODAExecutor(state_provider=MockStateProvider())
    
    # This should still complete even if strategy selection has issues
    state = await executor.execute_cycle("task_001", "unknown_type", "P1")
    
    assert state.action_result is not None


@pytest.mark.asyncio
async def test_ooda_handles_context_provider_timeout():
    """Test graceful degradation when context provider times out."""
    
    class SlowContextProvider(ContextProvider):
        async def get_patterns(self, observation, top_k=5):
            await asyncio.sleep(1)  # Will timeout
            return []
        
        async def get_sessions(self, task_type, limit=3):
            return []
        
        async def get_external_context(self):
            return {}
    
    executor = OODAExecutor(
        state_provider=MockStateProvider(),
        context_provider=SlowContextProvider(),
    )
    
    state = await executor.execute_cycle("task_001", "ci_fix", "P1")
    
    # Should complete despite timeout (with degraded context)
    assert state.action_result is not None
    assert state.phase == OODAPhase.FEEDBACK


# ============================================================================
# Degradation Mode Tests
# ============================================================================

@pytest.mark.asyncio
async def test_degradation_to_pattern_only():
    """Test degradation to pattern-only mode."""
    
    class PartialContextProvider(ContextProvider):
        async def get_patterns(self, observation, top_k=5):
            return [{"pattern_id": "pat_001", "name": "Test", "similarity": 0.9, "success_rate": 0.8}]
        
        async def get_sessions(self, task_type, limit=3):
            raise Exception("Sessions unavailable")
        
        async def get_external_context(self):
            return {}
    
    executor = OODAExecutor(
        state_provider=MockStateProvider(),
        context_provider=PartialContextProvider(),
    )
    
    state = await executor.execute_cycle("task_001", "ci_fix", "P1")
    
    assert state.orientation is not None
    assert state.orientation.context.degradation_level == DegradationLevel.PATTERN_ONLY


@pytest.mark.asyncio
async def test_degradation_to_no_context():
    """Test degradation to no-context mode."""
    
    class FailingContextProvider(ContextProvider):
        async def get_patterns(self, observation, top_k=5):
            raise Exception("Patterns unavailable")
        
        async def get_sessions(self, task_type, limit=3):
            raise Exception("Sessions unavailable")
        
        async def get_external_context(self):
            raise Exception("External data unavailable")
    
    executor = OODAExecutor(
        state_provider=MockStateProvider(),
        context_provider=FailingContextProvider(),
    )
    
    state = await executor.execute_cycle("task_001", "ci_fix", "P1")
    
    assert state.orientation is not None
    assert state.orientation.context.degradation_level == DegradationLevel.NO_CONTEXT


@pytest.mark.asyncio
async def test_degradation_without_context_provider():
    """Test that executor works without context provider (no-context mode)."""
    executor = OODAExecutor(state_provider=MockStateProvider(), context_provider=None)
    
    state = await executor.execute_cycle("task_001", "ci_fix", "P1")
    
    assert state.orientation is not None
    assert state.orientation.context.degradation_level == DegradationLevel.NO_CONTEXT
    assert state.action_result is not None


# ============================================================================
# Risk and Confidence Tests
# ============================================================================

@pytest.mark.asyncio
async def test_confidence_scoring():
    """Test confidence scoring based on context quality."""
    executor = OODAExecutor(
        state_provider=MockStateProvider(),
        context_provider=MockContextProvider(DegradationLevel.FULL_CONTEXT),
    )
    
    state = await executor.execute_cycle("task_001", "ci_fix", "P1")
    
    # Should have reasonable confidence with full context
    assert state.orientation.confidence >= 0.0
    assert state.orientation.confidence <= 1.0


@pytest.mark.asyncio
async def test_risk_level_assessment():
    """Test risk level is correctly assessed."""
    executor = OODAExecutor(state_provider=MockStateProvider())
    
    state = await executor.execute_cycle("task_001", "ci_fix", "P1")
    
    assert state.orientation.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH]


# ============================================================================
# Data Structure Tests
# ============================================================================

def test_observation_data_serialization():
    """Test ObservationData to_dict()."""
    obs = ObservationData(
        timestamp=datetime.now(),
        repo_state={"branch": "main"},
        task={"id": "task_001", "type": "ci_fix"},
        agent_state={"health": 0.9},
        environment={"cpu": 0.5},
    )
    
    obs_dict = obs.to_dict()
    
    assert "timestamp" in obs_dict
    assert obs_dict["repo_state"]["branch"] == "main"


def test_context_data_serialization():
    """Test ContextData to_dict()."""
    context = ContextData(
        patterns=[{"pattern_id": "pat_001", "name": "Test"}],
        sessions=[],
        degradation_level=DegradationLevel.FULL_CONTEXT,
    )
    
    context_dict = context.to_dict()
    
    assert len(context_dict["patterns"]) == 1
    assert context_dict["degradation_level"] == "full_context"


def test_action_result_serialization():
    """Test ActionResult to_dict()."""
    result = ActionResult(
        status="success",
        output={"step": 1},
        execution_time_ms=150.5,
    )
    
    result_dict = result.to_dict()
    
    assert result_dict["status"] == "success"
    assert result_dict["execution_time_ms"] == 150.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
