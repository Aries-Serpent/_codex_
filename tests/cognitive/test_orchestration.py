"""Tests for orchestration integration module.

Phase 1.4 of Long-term Cognitive Brain Planset.
Tests for BrainAwareOrchestrator, orchestration patterns, and agent coordination.
"""

from __future__ import annotations

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from codex.cognitive.orchestration import (
    ORCHESTRATING_AGENTS,
    BrainAwareOrchestrator,
    OrchestrationDecision,
    OrchestrationPattern,
    OrchestrationResult,
    create_orchestrator,
    get_orchestrating_agent_count,
    get_orchestrating_agents,
    integrate_orchestrating_agents,
)

# ============================================================================
# Test Data Fixtures
# ============================================================================


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_patterns():
    """Sample pattern store data."""
    return {
        "patterns": [
            {
                "id": "TFR-001",
                "name": "Test failure resolution",
                "category": "testing",
                "keywords": ["pytest", "test", "failure", "error"],
                "symptoms": ["test collection error", "assertion failed"],
                "success_rate": 0.95,
            },
            {
                "id": "CIF-001",
                "name": "CI failure resolution",
                "category": "ci_cd",
                "keywords": ["ci", "pipeline", "workflow", "build"],
                "symptoms": ["workflow failed", "build error"],
                "success_rate": 0.88,
            },
            {
                "id": "SEC-001",
                "name": "Security issue resolution",
                "category": "security",
                "keywords": ["security", "vulnerability", "codeql"],
                "symptoms": ["security alert", "vulnerability detected"],
                "success_rate": 0.92,
            },
        ]
    }


@pytest.fixture
def sample_manifest():
    """Sample agent integration manifest."""
    return {
        "metadata": {
            "last_updated": "2026-02-05T12:00:00Z",
            "total_agents": 18,
        },
        "agents": {
            "ci-testing-agent": {
                "category": "ci_cd",
                "capability": "ci_diagnosis",
            },
            "test-coverage-monitor": {
                "category": "testing",
                "capability": "coverage_tracking",
            },
            "security-alert-verification-agent": {
                "category": "security",
                "capability": "alert_triage",
            },
        },
    }


@pytest.fixture
def setup_test_files(temp_dir, sample_patterns, sample_manifest):
    """Set up test pattern store and manifest files."""
    pattern_path = temp_dir / "pattern_learning_store.json"
    manifest_path = temp_dir / "agent_integration_manifest.json"

    with open(pattern_path, "w") as f:
        json.dump(sample_patterns, f)

    with open(manifest_path, "w") as f:
        json.dump(sample_manifest, f)

    return pattern_path, manifest_path


# ============================================================================
# OrchestrationPattern Tests
# ============================================================================


class TestOrchestrationPattern:
    """Tests for OrchestrationPattern enum."""

    def test_pattern_values(self):
        """Test pattern enum values."""
        assert OrchestrationPattern.SEQUENTIAL_CHAIN.value == "sequential_chain", "Value must be initialized"
        assert OrchestrationPattern.PARALLEL_FAN_OUT.value == "parallel_fan_out", "Value must be initialized"
        assert OrchestrationPattern.CONDITIONAL_ROUTING.value == "conditional_routing", "Value must be initialized"
        assert OrchestrationPattern.HIERARCHICAL_DELEGATION.value == "hierarchical", "Value must be initialized"

    def test_all_patterns_defined(self):
        """Test all 4 patterns are defined."""
        assert len(OrchestrationPattern) == 4, "Orchestrationpattern must not be empty"


# ============================================================================
# OrchestrationDecision Tests
# ============================================================================


class TestOrchestrationDecision:
    """Tests for OrchestrationDecision dataclass."""

    def test_decision_creation(self):
        """Test creating an orchestration decision."""
        decision = OrchestrationDecision(
            selected_agents=["agent-1", "agent-2"],
            pattern=OrchestrationPattern.SEQUENTIAL_CHAIN,
            confidence=0.85,
            reasoning="Selected based on pattern match",
        )

        assert decision.selected_agents == ["agent-1", "agent-2"]
        assert decision.pattern == OrchestrationPattern.SEQUENTIAL_CHAIN, "pattern is not valid"
        assert decision.confidence == 0.85, "confidence is not valid"
        assert "pattern match" in decision.reasoning, "Condition must be true"

    def test_decision_with_pattern_matches(self):
        """Test decision with pattern matches."""
        decision = OrchestrationDecision(
            selected_agents=["agent-1"],
            pattern=OrchestrationPattern.CONDITIONAL_ROUTING,
            confidence=0.9,
            reasoning="Based on TFR-001",
            pattern_matches=["TFR-001", "CIF-001"],
        )

        assert decision.pattern_matches == ["TFR-001", "CIF-001"]

    def test_decision_timestamp(self):
        """Test decision has timestamp."""
        decision = OrchestrationDecision(
            selected_agents=[],
            pattern=OrchestrationPattern.PARALLEL_FAN_OUT,
            confidence=0.5,
            reasoning="Default",
        )

        assert decision.timestamp is not None, "timestamp must be initialized"
        # Should be ISO format
        datetime.fromisoformat(decision.timestamp.replace("Z", "+00:00"))


# ============================================================================
# OrchestrationResult Tests
# ============================================================================


class TestOrchestrationResult:
    """Tests for OrchestrationResult dataclass."""

    def test_result_creation(self):
        """Test creating an orchestration result."""
        result = OrchestrationResult(
            orchestrator_id="artifact-monitor-agent",
            agents_executed=["agent-1", "agent-2"],
            pattern_used=OrchestrationPattern.HIERARCHICAL_DELEGATION,
            success=True,
        )

        assert result.orchestrator_id == "artifact-monitor-agent", "Result must not be empty"
        assert len(result.agents_executed) == 2, "Collection must not be empty"
        assert result.success is True, "Result must not be empty"

    def test_result_with_learnings(self):
        """Test result with learnings."""
        result = OrchestrationResult(
            orchestrator_id="coverage-roadmap-agent",
            agents_executed=["agent-1"],
            pattern_used=OrchestrationPattern.SEQUENTIAL_CHAIN,
            success=True,
            learnings=[{"step": 1, "agent": "agent-1"}],
        )

        assert len(result.learnings) == 1, "Collection must not be empty"


# ============================================================================
# ORCHESTRATING_AGENTS Tests
# ============================================================================


class TestOrchestratingAgents:
    """Tests for ORCHESTRATING_AGENTS constant."""

    def test_agent_count(self):
        """Test 11 orchestrating agents are defined."""
        assert len(ORCHESTRATING_AGENTS) == 11, "Orchestrating_agents must not be empty"

    def test_all_agents_have_pattern(self):
        """Test all agents have orchestration pattern."""
        for agent_id, config in ORCHESTRATING_AGENTS.items():
            assert "pattern" in config, f"{agent_id} missing pattern"
            assert isinstance(config["pattern"], OrchestrationPattern
            ), f"{agent_id} pattern is not OrchestrationPattern"

    def test_all_agents_have_capability(self):
        """Test all agents have capability."""
        for agent_id, config in ORCHESTRATING_AGENTS.items():
            assert "capability" in config, f"{agent_id} missing capability"
            assert config["capability"], f"{agent_id} capability is empty"

    def test_all_agents_have_delegates(self):
        """Test all agents have delegates_to list."""
        for agent_id, config in ORCHESTRATING_AGENTS.items():
            assert "delegates_to" in config, f"{agent_id} missing delegates_to"
            assert isinstance(config["delegates_to"], list), f"{agent_id} delegates_to is not list"

    def test_expected_agents_present(self):
        """Test expected orchestrating agents are present."""
        expected = [
            "artifact-monitor-agent",
            "coverage-roadmap-agent",
            "repository-hygiene-agent",
            "integration-test-runner",
            "rag-module-management-agent",
            "reference-updater-agent",
            "root-organizer-agent",
            "tokenization-coverage-agent",
            "workflow-management-agent",
            "code-analysis-agent",
            "codex-reviewer-agent",
        ]

        for agent_id in expected:
            assert agent_id in ORCHESTRATING_AGENTS, f"{agent_id} not found"


# ============================================================================
# BrainAwareOrchestrator Tests
# ============================================================================


class TestBrainAwareOrchestrator:
    """Tests for BrainAwareOrchestrator class."""

    def test_orchestrator_creation(self, setup_test_files):
        """Test creating an orchestrator."""
        pattern_path, manifest_path = setup_test_files

        orchestrator = BrainAwareOrchestrator(
            orchestrator_id="artifact-monitor-agent",
            pattern_store_path=pattern_path,
            manifest_path=manifest_path,
        )

        assert orchestrator.orchestrator_id == "artifact-monitor-agent", "orchestrator_id is not valid"
        assert orchestrator.pattern == OrchestrationPattern.HIERARCHICAL_DELEGATION, "pattern is not valid"
        assert orchestrator.capability == "pattern_routing", "capability is not valid"

    def test_invalid_orchestrator_raises(self, temp_dir):
        """Test invalid orchestrator ID raises error."""
        with pytest.raises(ValueError, match="Unknown orchestrator"):
            BrainAwareOrchestrator(
                orchestrator_id="invalid-agent",
                pattern_store_path=temp_dir / "patterns.json",
            )

    def test_query_patterns(self, setup_test_files):
        """Test querying patterns."""
        pattern_path, manifest_path = setup_test_files

        orchestrator = BrainAwareOrchestrator(
            orchestrator_id="artifact-monitor-agent",
            pattern_store_path=pattern_path,
            manifest_path=manifest_path,
        )

        patterns = orchestrator.query_patterns("pytest error")
        assert len(patterns) >= 1, "Patterns must not be empty"
        assert patterns[0]["id"] == "TFR-001", "Condition must be true"

    def test_query_patterns_no_match(self, setup_test_files):
        """Test querying patterns with no match."""
        pattern_path, manifest_path = setup_test_files

        orchestrator = BrainAwareOrchestrator(
            orchestrator_id="artifact-monitor-agent",
            pattern_store_path=pattern_path,
            manifest_path=manifest_path,
        )

        patterns = orchestrator.query_patterns("completely unrelated query")
        assert len(patterns) == 0, "Patterns must not be empty"

    def test_recommend_agents(self, setup_test_files):
        """Test recommending agents."""
        pattern_path, manifest_path = setup_test_files

        orchestrator = BrainAwareOrchestrator(
            orchestrator_id="artifact-monitor-agent",
            pattern_store_path=pattern_path,
            manifest_path=manifest_path,
        )

        agents = orchestrator.recommend_agents("pytest failure")
        assert len(agents) > 0, "Agents must not be empty"
        # Should include delegates
        for delegate in orchestrator.delegates_to:
            assert delegate in agents, "Condition must be true"

    def test_make_routing_decision(self, setup_test_files):
        """Test making routing decision."""
        pattern_path, manifest_path = setup_test_files

        orchestrator = BrainAwareOrchestrator(
            orchestrator_id="coverage-roadmap-agent",
            pattern_store_path=pattern_path,
            manifest_path=manifest_path,
        )

        decision = orchestrator.make_routing_decision("test failure")
        assert isinstance(decision, OrchestrationDecision)
        assert len(decision.selected_agents) > 0, "Collection must not be empty"
        assert decision.confidence > 0, "confidence must be greater than zero"

    def test_routing_decision_with_pattern_match(self, setup_test_files):
        """Test routing decision includes pattern matches."""
        pattern_path, manifest_path = setup_test_files

        orchestrator = BrainAwareOrchestrator(
            orchestrator_id="artifact-monitor-agent",
            pattern_store_path=pattern_path,
            manifest_path=manifest_path,
        )

        decision = orchestrator.make_routing_decision("pytest error in tests")
        assert len(decision.pattern_matches) > 0, "Collection must not be empty"
        assert decision.confidence >= 0.9, "confidence must be greater than zero"


class TestSequentialChainExecution:
    """Tests for sequential chain execution."""

    def test_sequential_chain_success(self, setup_test_files):
        """Test successful sequential chain execution."""
        pattern_path, manifest_path = setup_test_files

        orchestrator = BrainAwareOrchestrator(
            orchestrator_id="coverage-roadmap-agent",
            pattern_store_path=pattern_path,
            manifest_path=manifest_path,
        )

        result = orchestrator.execute_sequential_chain(
            ["agent-1", "agent-2", "agent-3"],
            task_fn=lambda _: True,
        )

        assert result.success is True, "Result must not be empty"
        assert len(result.agents_executed) == 3, "Collection must not be empty"
        assert result.pattern_used == OrchestrationPattern.SEQUENTIAL_CHAIN, "Result must not be empty"

    def test_sequential_chain_failure_stops(self, setup_test_files):
        """Test sequential chain stops on failure."""
        pattern_path, manifest_path = setup_test_files

        orchestrator = BrainAwareOrchestrator(
            orchestrator_id="reference-updater-agent",
            pattern_store_path=pattern_path,
            manifest_path=manifest_path,
        )

        def fail_on_second(agent_id: str) -> bool:
            return agent_id != "agent-2"

        result = orchestrator.execute_sequential_chain(
            ["agent-1", "agent-2", "agent-3"],
            task_fn=fail_on_second,
        )

        assert result.success is False, "Result must not be empty"
        assert len(result.agents_executed) == 2, "Collection must not be empty"


class TestParallelFanOutExecution:
    """Tests for parallel fan-out execution."""

    def test_parallel_fan_out_all_success(self, setup_test_files):
        """Test parallel fan-out with all success."""
        pattern_path, manifest_path = setup_test_files

        orchestrator = BrainAwareOrchestrator(
            orchestrator_id="integration-test-runner",
            pattern_store_path=pattern_path,
            manifest_path=manifest_path,
        )

        result = orchestrator.execute_parallel_fan_out(
            ["agent-1", "agent-2", "agent-3"],
            task_fn=lambda _: True,
        )

        assert result.success is True, "Result must not be empty"
        assert len(result.agents_executed) == 3, "Collection must not be empty"
        assert result.pattern_used == OrchestrationPattern.PARALLEL_FAN_OUT, "Result must not be empty"

    def test_parallel_fan_out_partial_failure(self, setup_test_files):
        """Test parallel fan-out with partial failure."""
        pattern_path, manifest_path = setup_test_files

        orchestrator = BrainAwareOrchestrator(
            orchestrator_id="code-analysis-agent",
            pattern_store_path=pattern_path,
            manifest_path=manifest_path,
        )

        def fail_on_second(agent_id: str) -> bool:
            return agent_id != "agent-2"

        result = orchestrator.execute_parallel_fan_out(
            ["agent-1", "agent-2", "agent-3"],
            task_fn=fail_on_second,
        )

        assert result.success is False, "Result must not be empty"
        assert len(result.agents_executed) == 3, "Collection must not be empty"


class TestConditionalRoutingExecution:
    """Tests for conditional routing execution."""

    def test_conditional_routing(self, setup_test_files):
        """Test conditional routing based on pattern."""
        pattern_path, manifest_path = setup_test_files

        orchestrator = BrainAwareOrchestrator(
            orchestrator_id="codex-reviewer-agent",
            pattern_store_path=pattern_path,
            manifest_path=manifest_path,
        )

        agents_map = {
            "testing": ["test-agent-1", "test-agent-2"],
            "security": ["security-agent-1"],
            "default": ["default-agent"],
        }

        result = orchestrator.execute_conditional_routing(
            condition="pytest test failure",
            agents_map=agents_map,
        )

        assert result.pattern_used == OrchestrationPattern.CONDITIONAL_ROUTING, "Result must not be empty"
        # Should have routed to testing agents
        assert len(result.learnings) > 0, "Collection must not be empty"

    def test_conditional_routing_default(self, setup_test_files):
        """Test conditional routing falls back to default."""
        pattern_path, manifest_path = setup_test_files

        orchestrator = BrainAwareOrchestrator(
            orchestrator_id="codex-reviewer-agent",
            pattern_store_path=pattern_path,
            manifest_path=manifest_path,
        )

        agents_map = {
            "unknown_category": ["agent-1"],
            "default": ["default-agent"],
        }

        result = orchestrator.execute_conditional_routing(
            condition="completely unrelated condition",
            agents_map=agents_map,
        )

        # Should use default route
        assert result.pattern_used == OrchestrationPattern.CONDITIONAL_ROUTING, "Result must not be empty"


class TestLearningAggregation:
    """Tests for learning aggregation."""

    def test_aggregate_learnings(self, setup_test_files):
        """Test aggregating learnings from multiple results."""
        pattern_path, manifest_path = setup_test_files

        orchestrator = BrainAwareOrchestrator(
            orchestrator_id="artifact-monitor-agent",
            pattern_store_path=pattern_path,
            manifest_path=manifest_path,
        )

        results = [
            OrchestrationResult(
                orchestrator_id="artifact-monitor-agent",
                agents_executed=["a1", "a2"],
                pattern_used=OrchestrationPattern.HIERARCHICAL_DELEGATION,
                success=True,
            ),
            OrchestrationResult(
                orchestrator_id="artifact-monitor-agent",
                agents_executed=["a3"],
                pattern_used=OrchestrationPattern.SEQUENTIAL_CHAIN,
                success=True,
            ),
            OrchestrationResult(
                orchestrator_id="artifact-monitor-agent",
                agents_executed=["a4", "a5", "a6"],
                pattern_used=OrchestrationPattern.HIERARCHICAL_DELEGATION,
                success=False,
            ),
        ]

        summary = orchestrator.aggregate_learnings(results)

        assert summary["total_orchestrations"] == 3, "Condition must be true"
        assert summary["total_agents_executed"] == 6, "Condition must be true"
        assert summary["successful_orchestrations"] == 2, "Condition must be true"
        assert summary["success_rate"] == pytest.approx(2 / 3)
        assert "hierarchical" in summary["patterns_used"], "Condition must be true"
        assert "sequential_chain" in summary["patterns_used"], "Condition must be true"


# ============================================================================
# Module Function Tests
# ============================================================================


class TestModuleFunctions:
    """Tests for module-level functions."""

    def test_get_orchestrating_agents(self):
        """Test get_orchestrating_agents returns copy."""
        agents = get_orchestrating_agents()
        assert len(agents) == 11, "Agents must not be empty"

        # Should be a copy
        agents["new-agent"] = {}
        assert "new-agent" not in ORCHESTRATING_AGENTS, "Condition must be true"

    def test_get_orchestrating_agent_count(self):
        """Test get_orchestrating_agent_count."""
        assert get_orchestrating_agent_count() == 11, "Count must be greater than zero"

    def test_integrate_orchestrating_agents(self, temp_dir):
        """Test integrating orchestrating agents."""
        manifest_path = temp_dir / "manifest.json"

        # Create initial manifest
        initial = {
            "agents": {
                "existing-agent": {"category": "core"},
            },
        }
        with open(manifest_path, "w") as f:
            json.dump(initial, f)

        integrated = integrate_orchestrating_agents(manifest_path)

        assert len(integrated) == 11, "Integrated must not be empty"
        assert "artifact-monitor-agent" in integrated, "Condition must be true"

        # Verify manifest was updated
        with open(manifest_path) as f:
            manifest = json.load(f)

        assert "artifact-monitor-agent" in manifest["agents"], "Condition must be true"
        assert manifest["metadata"]["orchestrating_agents"] == 11, "Data must not be empty"

    def test_create_orchestrator(self, setup_test_files):
        """Test create_orchestrator helper."""
        with (
            patch(
                "codex.cognitive.orchestration.DEFAULT_PATTERN_STORE",
                setup_test_files[0],
            ),
            patch(
                "codex.cognitive.orchestration.DEFAULT_MANIFEST",
                setup_test_files[1],
            ),
        ):
            orchestrator = create_orchestrator("artifact-monitor-agent")
            assert orchestrator.orchestrator_id == "artifact-monitor-agent", "orchestrator_id is not valid"


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_pattern_store(self, temp_dir):
        """Test with empty pattern store."""
        pattern_path = temp_dir / "patterns.json"
        manifest_path = temp_dir / "manifest.json"

        with open(pattern_path, "w") as f:
            json.dump({"patterns": []}, f)

        with open(manifest_path, "w") as f:
            json.dump({"agents": {}}, f)

        orchestrator = BrainAwareOrchestrator(
            orchestrator_id="artifact-monitor-agent",
            pattern_store_path=pattern_path,
            manifest_path=manifest_path,
        )

        patterns = orchestrator.query_patterns("anything")
        assert patterns == [], "patterns is not valid"

    def test_missing_pattern_store(self, temp_dir):
        """Test with missing pattern store file."""
        pattern_path = temp_dir / "nonexistent.json"
        manifest_path = temp_dir / "manifest.json"

        with open(manifest_path, "w") as f:
            json.dump({"agents": {}}, f)

        orchestrator = BrainAwareOrchestrator(
            orchestrator_id="artifact-monitor-agent",
            pattern_store_path=pattern_path,
            manifest_path=manifest_path,
        )

        # Should not raise, just have empty patterns
        assert orchestrator._patterns == [], "_patterns is not valid"

    def test_malformed_json_handling(self, temp_dir):
        """Test handling of malformed JSON files."""
        pattern_path = temp_dir / "patterns.json"
        manifest_path = temp_dir / "manifest.json"

        with open(pattern_path, "w") as f:
            f.write("not valid json")

        with open(manifest_path, "w") as f:
            json.dump({"agents": {}}, f)

        orchestrator = BrainAwareOrchestrator(
            orchestrator_id="artifact-monitor-agent",
            pattern_store_path=pattern_path,
            manifest_path=manifest_path,
        )

        # Should not raise, just have empty patterns
        assert orchestrator._patterns == [], "_patterns is not valid"

    def test_sequential_chain_no_task_fn(self, setup_test_files):
        """Test sequential chain without task function."""
        pattern_path, manifest_path = setup_test_files

        orchestrator = BrainAwareOrchestrator(
            orchestrator_id="coverage-roadmap-agent",
            pattern_store_path=pattern_path,
            manifest_path=manifest_path,
        )

        result = orchestrator.execute_sequential_chain(
            ["agent-1", "agent-2"],
        )

        assert result.success is True, "Result must not be empty"
        assert len(result.agents_executed) == 2, "Collection must not be empty"
