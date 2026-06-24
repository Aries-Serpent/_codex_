#!/usr/bin/env python3
"""Tests for Agent Integration module (Phases 1.2 and 1.3).

Tests the agent integration registry, core agent integration,
extended agent integration, and brain integration section generation.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from codex.cognitive.agent_integration import (
    ALL_INTEGRATED_AGENTS,
    CORE_AGENTS,
    EXTENDED_AGENTS,
    AgentCategory,
    AgentIntegrationRegistry,
    IntegratedAgent,
    get_brain_integration_section,
    get_extended_agent_count,
    get_total_agent_count,
    integrate_agent,
    integrate_all_agents,
    integrate_core_agents,
    integrate_extended_agents,
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
            assert agent_map["security-alert-verification-agent"].category == AgentCategory.SECURITY

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


# ============================================================================
# Phase 1.3: Extended Agent Integration Tests
# ============================================================================


class TestExtendedAgentsDefinition:
    """Tests for EXTENDED_AGENTS constant (Phase 1.3)."""

    def test_all_documentation_agents_defined(self) -> None:
        """Test that all documentation agents are defined."""
        doc_agents = [
            "documentation-consolidator",
            "link-validator-agent",
            "doc-freshness-checker",
        ]
        for agent in doc_agents:
            assert agent in EXTENDED_AGENTS
            assert EXTENDED_AGENTS[agent] == AgentCategory.DOCUMENTATION

    def test_all_rag_ml_agents_defined(self) -> None:
        """Test that all RAG/ML agents are defined."""
        rag_ml_agents = [
            "rag-index-manager",
            "meta-tensor-validator",
            "rag-meta-tensor-regression-agent",
        ]
        for agent in rag_ml_agents:
            assert agent in EXTENDED_AGENTS
            assert EXTENDED_AGENTS[agent] == AgentCategory.RAG_ML

    def test_all_repository_agents_defined(self) -> None:
        """Test that all repository agents are defined."""
        repo_agents = [
            "repository-hygiene-agent",
            "root-organizer-agent",
            "reference-updater-agent",
        ]
        for agent in repo_agents:
            assert agent in EXTENDED_AGENTS
            assert EXTENDED_AGENTS[agent] == AgentCategory.REPOSITORY

    def test_total_extended_agents(self) -> None:
        """Test total number of extended agents."""
        assert len(EXTENDED_AGENTS) == 9

    def test_get_extended_agent_count(self) -> None:
        """Test get_extended_agent_count function."""
        assert get_extended_agent_count() == 9


class TestAllIntegratedAgents:
    """Tests for ALL_INTEGRATED_AGENTS constant."""

    def test_all_agents_combined(self) -> None:
        """Test that all agents are combined correctly."""
        assert len(ALL_INTEGRATED_AGENTS) == len(CORE_AGENTS) + len(EXTENDED_AGENTS)

    def test_core_agents_in_all(self) -> None:
        """Test that all core agents are in ALL_INTEGRATED_AGENTS."""
        for agent_id in CORE_AGENTS:
            assert agent_id in ALL_INTEGRATED_AGENTS

    def test_extended_agents_in_all(self) -> None:
        """Test that all extended agents are in ALL_INTEGRATED_AGENTS."""
        for agent_id in EXTENDED_AGENTS:
            assert agent_id in ALL_INTEGRATED_AGENTS

    def test_get_total_agent_count(self) -> None:
        """Test get_total_agent_count function."""
        assert get_total_agent_count() == 18


class TestIntegrateExtendedAgents:
    """Tests for integrate_extended_agents function."""

    def test_integrates_all_extended_agents(self) -> None:
        """Test that all extended agents are integrated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            agents = integrate_extended_agents(manifest_path)
            assert len(agents) == 9

    def test_documentation_agents_have_doc_analysis(self) -> None:
        """Test documentation agents have doc_analysis capability."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            agents = integrate_extended_agents(manifest_path)
            doc_agents = [a for a in agents if a.category == AgentCategory.DOCUMENTATION]
            for agent in doc_agents:
                assert "doc_analysis" in agent.capabilities

    def test_rag_ml_agents_have_ml_operations(self) -> None:
        """Test RAG/ML agents have ml_operations capability."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            agents = integrate_extended_agents(manifest_path)
            rag_agents = [a for a in agents if a.category == AgentCategory.RAG_ML]
            for agent in rag_agents:
                assert "ml_operations" in agent.capabilities

    def test_repository_agents_have_repo_management(self) -> None:
        """Test repository agents have repo_management capability."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            agents = integrate_extended_agents(manifest_path)
            repo_agents = [a for a in agents if a.category == AgentCategory.REPOSITORY]
            for agent in repo_agents:
                assert "repo_management" in agent.capabilities

    def test_saves_manifest(self) -> None:
        """Test that manifest is saved after integration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            integrate_extended_agents(manifest_path)
            assert manifest_path.exists()
            data = json.loads(manifest_path.read_text())
            assert data["total_agents"] == 9

    def test_all_agents_have_base_capabilities(self) -> None:
        """Test all extended agents have base capabilities."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            agents = integrate_extended_agents(manifest_path)
            for agent in agents:
                assert "pattern_query" in agent.capabilities
                assert "learning_feedback" in agent.capabilities
                assert "session_state" in agent.capabilities


class TestIntegrateAllAgents:
    """Tests for integrate_all_agents function."""

    def test_integrates_all_agents(self) -> None:
        """Test that all agents (core + extended) are integrated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            agents = integrate_all_agents(manifest_path)
            assert len(agents) == 18

    def test_includes_all_categories(self) -> None:
        """Test that all categories are represented."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            agents = integrate_all_agents(manifest_path)
            categories = {a.category for a in agents}
            assert AgentCategory.CI_CD in categories
            assert AgentCategory.TESTING in categories
            assert AgentCategory.SECURITY in categories
            assert AgentCategory.DOCUMENTATION in categories
            assert AgentCategory.RAG_ML in categories
            assert AgentCategory.REPOSITORY in categories

    def test_category_counts(self) -> None:
        """Test that category counts are correct."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            agents = integrate_all_agents(manifest_path)
            by_category = {}
            for agent in agents:
                cat = agent.category.value
                by_category[cat] = by_category.get(cat, 0) + 1
            assert by_category["ci_cd"] == 4
            assert by_category["testing"] == 3
            assert by_category["security"] == 2
            assert by_category["documentation"] == 3
            assert by_category["rag_ml"] == 3
            assert by_category["repository"] == 3

    def test_saves_manifest_with_all(self) -> None:
        """Test that manifest is saved with all agents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            integrate_all_agents(manifest_path)
            data = json.loads(manifest_path.read_text())
            assert data["total_agents"] == 18


class TestExtendedAgentAdapters:
    """Tests for extended agent adapters in brain integration section."""

    def test_docs_adapter(self) -> None:
        """Test DocsAdapter for documentation agents."""
        section = get_brain_integration_section(
            "documentation-consolidator", AgentCategory.DOCUMENTATION
        )
        assert "DocsAdapter" in section

    def test_rag_ml_adapter(self) -> None:
        """Test RAGMLAdapter for RAG/ML agents."""
        section = get_brain_integration_section("rag-index-manager", AgentCategory.RAG_ML)
        assert "RAGMLAdapter" in section

    def test_repo_adapter(self) -> None:
        """Test RepoAdapter for repository agents."""
        section = get_brain_integration_section(
            "repository-hygiene-agent", AgentCategory.REPOSITORY
        )
        assert "RepoAdapter" in section


class TestRegistryWithExtendedAgents:
    """Tests for registry behavior with extended agents."""

    def test_list_by_category_documentation(self) -> None:
        """Test listing agents by documentation category."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            integrate_extended_agents(manifest_path)
            registry = AgentIntegrationRegistry(manifest_path)
            doc_agents = registry.list_by_category(AgentCategory.DOCUMENTATION)
            assert len(doc_agents) == 3

    def test_list_by_category_rag_ml(self) -> None:
        """Test listing agents by RAG/ML category."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            integrate_extended_agents(manifest_path)
            registry = AgentIntegrationRegistry(manifest_path)
            rag_agents = registry.list_by_category(AgentCategory.RAG_ML)
            assert len(rag_agents) == 3

    def test_list_by_category_repository(self) -> None:
        """Test listing agents by repository category."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            integrate_extended_agents(manifest_path)
            registry = AgentIntegrationRegistry(manifest_path)
            repo_agents = registry.list_by_category(AgentCategory.REPOSITORY)
            assert len(repo_agents) == 3

    def test_stats_with_all_agents(self) -> None:
        """Test stats with all agents integrated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            integrate_all_agents(manifest_path)
            registry = AgentIntegrationRegistry(manifest_path)
            stats = registry.get_stats()
            assert stats["total_agents"] == 18
            assert "documentation" in stats["by_category"]
            assert "rag_ml" in stats["by_category"]
            assert "repository" in stats["by_category"]

    def test_is_integrated_extended_agent(self) -> None:
        """Test is_integrated for extended agents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "manifest.json"
            integrate_extended_agents(manifest_path)
            registry = AgentIntegrationRegistry(manifest_path)
            assert registry.is_integrated("documentation-consolidator")
            assert registry.is_integrated("rag-index-manager")
            assert registry.is_integrated("repository-hygiene-agent")
            assert not registry.is_integrated("unknown-agent")
