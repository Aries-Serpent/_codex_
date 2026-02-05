#!/usr/bin/env python3
"""Tests for Agent Integration module (Phase 1.2).

Tests the agent integration registry, core agent integration,
and brain integration section generation.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from codex.cognitive.agent_integration import (
    CORE_AGENTS,
    AgentCategory,
    AgentIntegrationRegistry,
    IntegratedAgent,
    get_brain_integration_section,
    integrate_agent,
    integrate_core_agents,
)


class TestIntegratedAgent:
    """Tests for IntegratedAgent dataclass."""

    def test_create_agent(self) -> None:
        """Test creating an IntegratedAgent."""
        agent = IntegratedAgent(
            agent_id="test-agent",
            category=AgentCategory.CI_CD,
        )
        assert agent.agent_id == "test-agent"
        assert agent.category == AgentCategory.CI_CD
        assert agent.patterns_accessed == 0
        assert agent.learnings_submitted == 0

    def test_agent_to_dict(self) -> None:
        """Test converting agent to dictionary."""
        agent = IntegratedAgent(
            agent_id="test-agent",
            category=AgentCategory.TESTING,
            capabilities=["pattern_query"],
        )
        data = agent.to_dict()
        assert data["agent_id"] == "test-agent"
        assert data["category"] == "testing"
        assert "pattern_query" in data["capabilities"]

    def test_agent_from_dict(self) -> None:
        """Test creating agent from dictionary."""
        data = {
            "agent_id": "test-agent",
            "category": "security",
            "capabilities": ["learning_feedback"],
            "patterns_accessed": 5,
            "learnings_submitted": 3,
        }
        agent = IntegratedAgent.from_dict(data)
        assert agent.agent_id == "test-agent"
        assert agent.category == AgentCategory.SECURITY
        assert agent.patterns_accessed == 5
        assert agent.learnings_submitted == 3

    def test_agent_roundtrip(self) -> None:
        """Test agent serialization roundtrip."""
        original = IntegratedAgent(
            agent_id="roundtrip-agent",
            category=AgentCategory.DOCUMENTATION,
            capabilities=["pattern_query", "session_state"],
        )
        data = original.to_dict()
        restored = IntegratedAgent.from_dict(data)
        assert restored.agent_id == original.agent_id
        assert restored.category == original.category
        assert restored.capabilities == original.capabilities


class TestAgentIntegrationRegistry:
    """Tests for AgentIntegrationRegistry."""

    def test_create_registry(self) -> None:
        """Test creating a registry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            registry = AgentIntegrationRegistry(manifest_path)
            assert registry.total_integrated == 0

    def test_register_agent(self) -> None:
        """Test registering an agent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            registry = AgentIntegrationRegistry(manifest_path)

            agent = registry.register(
                "test-agent",
                AgentCategory.CI_CD,
                ["pattern_query"],
            )
            assert agent.agent_id == "test-agent"
            assert registry.is_integrated("test-agent")
            assert registry.total_integrated == 1

    def test_get_agent(self) -> None:
        """Test getting an agent by ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            registry = AgentIntegrationRegistry(manifest_path)
            registry.register("test-agent", AgentCategory.TESTING)

            agent = registry.get("test-agent")
            assert agent is not None
            assert agent.agent_id == "test-agent"

            missing = registry.get("nonexistent")
            assert missing is None

    def test_list_by_category(self) -> None:
        """Test listing agents by category."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            registry = AgentIntegrationRegistry(manifest_path)

            registry.register("ci-agent-1", AgentCategory.CI_CD)
            registry.register("ci-agent-2", AgentCategory.CI_CD)
            registry.register("test-agent", AgentCategory.TESTING)

            ci_agents = registry.list_by_category(AgentCategory.CI_CD)
            assert len(ci_agents) == 2

            test_agents = registry.list_by_category(AgentCategory.TESTING)
            assert len(test_agents) == 1

    def test_list_all(self) -> None:
        """Test listing all agents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            registry = AgentIntegrationRegistry(manifest_path)

            registry.register("agent-1", AgentCategory.CI_CD)
            registry.register("agent-2", AgentCategory.TESTING)
            registry.register("agent-3", AgentCategory.SECURITY)

            all_agents = registry.list_all()
            assert len(all_agents) == 3

    def test_save_and_load(self) -> None:
        """Test saving and loading the manifest."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"

            # Create and save
            registry1 = AgentIntegrationRegistry(manifest_path)
            registry1.register("test-agent", AgentCategory.CI_CD, ["pattern_query"])
            registry1.save()

            # Load in new instance
            registry2 = AgentIntegrationRegistry(manifest_path)
            assert registry2.is_integrated("test-agent")
            agent = registry2.get("test-agent")
            assert agent is not None
            assert "pattern_query" in agent.capabilities

    def test_record_access(self) -> None:
        """Test recording pattern access."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            registry = AgentIntegrationRegistry(manifest_path)
            registry.register("test-agent", AgentCategory.CI_CD)

            assert registry.get("test-agent").patterns_accessed == 0
            registry.record_access("test-agent")
            assert registry.get("test-agent").patterns_accessed == 1
            registry.record_access("test-agent")
            assert registry.get("test-agent").patterns_accessed == 2

    def test_record_learning(self) -> None:
        """Test recording learning submission."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            registry = AgentIntegrationRegistry(manifest_path)
            registry.register("test-agent", AgentCategory.TESTING)

            assert registry.get("test-agent").learnings_submitted == 0
            registry.record_learning("test-agent")
            assert registry.get("test-agent").learnings_submitted == 1

    def test_get_stats(self) -> None:
        """Test getting integration statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            registry = AgentIntegrationRegistry(manifest_path)

            registry.register("ci-agent", AgentCategory.CI_CD)
            registry.register("test-agent", AgentCategory.TESTING)

            registry.record_access("ci-agent")
            registry.record_access("ci-agent")
            registry.record_learning("test-agent")

            stats = registry.get_stats()
            assert stats["total_agents"] == 2
            assert stats["by_category"]["ci_cd"] == 1
            assert stats["by_category"]["testing"] == 1
            assert stats["total_pattern_accesses"] == 2
            assert stats["total_learnings"] == 1

    def test_load_invalid_manifest(self) -> None:
        """Test loading an invalid manifest file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            manifest_path.write_text("invalid json")

            registry = AgentIntegrationRegistry(manifest_path)
            assert registry.total_integrated == 0


class TestIntegrateAgent:
    """Tests for integrate_agent function."""

    def test_integrate_with_string_category(self) -> None:
        """Test integrating with string category."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            agent = integrate_agent(
                "test-agent",
                category="ci_cd",
                manifest_path=manifest_path,
            )
            assert agent.agent_id == "test-agent"
            assert agent.category == AgentCategory.CI_CD

    def test_integrate_with_enum_category(self) -> None:
        """Test integrating with enum category."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            agent = integrate_agent(
                "test-agent",
                category=AgentCategory.SECURITY,
                manifest_path=manifest_path,
            )
            assert agent.category == AgentCategory.SECURITY

    def test_integrate_with_capabilities(self) -> None:
        """Test integrating with custom capabilities."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            agent = integrate_agent(
                "test-agent",
                capabilities=["custom_capability"],
                manifest_path=manifest_path,
            )
            assert "custom_capability" in agent.capabilities

    def test_integrate_saves_manifest(self) -> None:
        """Test that integration saves the manifest."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            integrate_agent("test-agent", manifest_path=manifest_path)

            assert manifest_path.exists()
            data = json.loads(manifest_path.read_text())
            assert "test-agent" in data["agents"]


class TestIntegrateCoreAgents:
    """Tests for integrate_core_agents function."""

    def test_integrate_core_agents(self) -> None:
        """Test integrating all core agents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            agents = integrate_core_agents(manifest_path)

            assert len(agents) == len(CORE_AGENTS)
            agent_ids = {a.agent_id for a in agents}
            assert agent_ids == set(CORE_AGENTS.keys())

    def test_core_agents_have_correct_categories(self) -> None:
        """Test that core agents have correct categories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            agents = integrate_core_agents(manifest_path)

            agent_map = {a.agent_id: a for a in agents}

            assert agent_map["ci-testing-agent"].category == AgentCategory.CI_CD
            assert agent_map["coverage-roadmap-agent"].category == AgentCategory.TESTING
            assert (
                agent_map["security-alert-verification-agent"].category
                == AgentCategory.SECURITY
            )

    def test_core_agents_have_category_capabilities(self) -> None:
        """Test that core agents have category-specific capabilities."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            agents = integrate_core_agents(manifest_path)

            agent_map = {a.agent_id: a for a in agents}

            # CI/CD agents should have ci_diagnosis
            assert "ci_diagnosis" in agent_map["ci-testing-agent"].capabilities

            # Testing agents should have coverage_tracking
            assert "coverage_tracking" in agent_map["coverage-roadmap-agent"].capabilities

            # Security agents should have vulnerability_analysis
            assert (
                "vulnerability_analysis"
                in agent_map["security-alert-verification-agent"].capabilities
            )


class TestGetBrainIntegrationSection:
    """Tests for get_brain_integration_section function."""

    def test_generates_markdown(self) -> None:
        """Test that function generates markdown."""
        section = get_brain_integration_section("test-agent", AgentCategory.CI_CD)
        assert "## 🧠 Cognitive Brain Integration" in section
        assert "test-agent" in section

    def test_includes_category(self) -> None:
        """Test that section includes category."""
        section = get_brain_integration_section("test-agent", AgentCategory.CI_CD)
        assert "ci_cd" in section

    def test_includes_correct_adapter(self) -> None:
        """Test that section includes correct adapter."""
        ci_section = get_brain_integration_section("ci-agent", AgentCategory.CI_CD)
        assert "CICDAdapter" in ci_section

        test_section = get_brain_integration_section("test-agent", AgentCategory.TESTING)
        assert "TestingAdapter" in test_section

        sec_section = get_brain_integration_section("sec-agent", AgentCategory.SECURITY)
        assert "SecurityAdapter" in sec_section

    def test_includes_usage_example(self) -> None:
        """Test that section includes usage example."""
        section = get_brain_integration_section("test-agent", AgentCategory.TESTING)
        assert "brain.query_patterns" in section
        assert "brain.submit_learning" in section
        assert "brain.check_alignment" in section

    def test_includes_integration_pattern(self) -> None:
        """Test that section includes integration pattern diagram."""
        section = get_brain_integration_section("test-agent", AgentCategory.CI_CD)
        assert "Query Brain for Relevant Patterns" in section
        assert "Submit Learning Feedback" in section

    def test_includes_documentation_links(self) -> None:
        """Test that section includes documentation links."""
        section = get_brain_integration_section("test-agent", AgentCategory.SECURITY)
        assert "AGENT_BRAIN_PROTOCOL.md" in section
        assert "pattern_learning_store.json" in section
        assert "brain_interface.py" in section


class TestCoreAgentsDefinition:
    """Tests for CORE_AGENTS constant."""

    def test_all_ci_cd_agents_defined(self) -> None:
        """Test that all CI/CD agents are defined."""
        ci_cd_agents = [
            "ci-testing-agent",
            "ci-log-retrieval-agent",
            "workflow-ci-fixer",
            "artifact-monitor-agent",
        ]
        for agent in ci_cd_agents:
            assert agent in CORE_AGENTS
            assert CORE_AGENTS[agent] == AgentCategory.CI_CD

    def test_all_testing_agents_defined(self) -> None:
        """Test that all testing agents are defined."""
        testing_agents = [
            "coverage-roadmap-agent",
            "test-alignment-fixer",
            "test-coverage-monitor",
        ]
        for agent in testing_agents:
            assert agent in CORE_AGENTS
            assert CORE_AGENTS[agent] == AgentCategory.TESTING

    def test_all_security_agents_defined(self) -> None:
        """Test that all security agents are defined."""
        security_agents = [
            "security-alert-verification-agent",
            "codeql-alert-resolution-agent",
        ]
        for agent in security_agents:
            assert agent in CORE_AGENTS
            assert CORE_AGENTS[agent] == AgentCategory.SECURITY

    def test_total_core_agents(self) -> None:
        """Test total number of core agents."""
        assert len(CORE_AGENTS) == 9


class TestAgentCategory:
    """Tests for AgentCategory enum."""

    def test_all_categories_exist(self) -> None:
        """Test all expected categories exist."""
        assert AgentCategory.CI_CD.value == "ci_cd"
        assert AgentCategory.TESTING.value == "testing"
        assert AgentCategory.SECURITY.value == "security"
        assert AgentCategory.DOCUMENTATION.value == "documentation"
        assert AgentCategory.RAG_ML.value == "rag_ml"
        assert AgentCategory.REPOSITORY.value == "repository"
        assert AgentCategory.OTHER.value == "other"

    def test_category_from_string(self) -> None:
        """Test creating category from string."""
        assert AgentCategory("ci_cd") == AgentCategory.CI_CD
        assert AgentCategory("testing") == AgentCategory.TESTING
        assert AgentCategory("security") == AgentCategory.SECURITY
