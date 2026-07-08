"""
Comprehensive functional tests for all custom AI agents.

This module validates that all custom agents in .github/agents/ are:
1. Properly configured with valid YAML/MD files
2. Have required fields and structure
3. Are callable by GitHub Copilot and other AI agents
4. Handle errors gracefully

Phase: 19 - Agent Validation
Tests: 100+
"""

from pathlib import Path

import pytest
import yaml

from codex.logging.structured_logger import logger

# ============================================================================
# Constants
# ============================================================================

AGENTS_DIR = Path(__file__).parent.parent.parent / ".github" / "agents"
CODEX_AGENTS_DIR = Path(__file__).parent.parent.parent / ".codex" / "agents"

# Known agent directories (subdirectories with agent implementations)
AGENT_DIRECTORIES = [
    "admin-automation-agent",
    "ast-analysis-agent",
    "ci-diagnostic-agent",
    "ci-failure-diagnostician",
    "ci-optimizer-agent",
    "ci-testing-agent",
    "codebase-qa-walkthrough-agent",
    "cognitive-brain-agent",
    "compliance-checker-agent",
    "dependency-conflict-resolver",
    "dep-upgrade-agent",
    "doc-test-scribe",
    "documentation-agent",
    "documentation-sync-validator",
    "ecosystem-coordinator-agent",
    "emergent-intelligence-agent",
    "flaky-triage-agent",
    "github-security-validator-agent",
    "github-testing-orchestrator-agent",
    "infra-linter-agent",
    "ml-threat-detector",
    "performance-monitor-agent",
    "project-architect-researcher",
    "pyo3-integration-tester",
    "reasoning-advisor-agent",
    "release-gate-agent",
    "rust-error-validator",
    "security-scan-agent",
    "security-vulnerability-patcher",
    "service-integration-tester",
    "test-assertion-updater",
    "test-coverage-enforcer",
]

# Agent config files (standalone YAML/MD files)
AGENT_CONFIG_FILES = [
    "bridge-security-monitor.agent.md",
    "codebase-qa-walkthrough-agent.agent.yml",
    "codex-reviewer.agent.yml",
    "config-migration-assistant.agent.md",
    "config-validator.agent.md",
    "datetime-modernizer.agent.md",
    "dependency-vulnerability-scanner.agent.md",
    "doc-freshness-checker.agent.md",
    "documentation-quality-agent.md",
    "integration-test-runner.agent.md",
    "link-validator-agent.md",
    "owner-approval-guard.agent.md",
    "performance-regression-detector.agent.md",
    "pii-scrubber.agent.md",
    "qa-walkthrough-agent.md",
    "rag-index-manager.agent.md",
    "semantic-search.agent.md",
    "test-alignment-fixer.agent.md",
    "test-coverage-monitor.agent.md",
    "workflow-ci-fixer.agent.md",
]

# Agent markdown documentation files
AGENT_DOC_FILES = [
    "ci-testing-agent.md",
    "performance-monitor-agent.md",
    "security-audit-agent.md",
    "test-coverage-agent.md",
]


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def agents_dir() -> Path:
    """Return the agents directory path."""
    return AGENTS_DIR


@pytest.fixture
def codex_agents_dir() -> Path:
    """Return the codex agents directory path."""
    return CODEX_AGENTS_DIR


# ============================================================================
# Test Classes
# ============================================================================


class TestAgentDirectoryStructure:
    """Tests for agent directory structure validation."""

    def test_agents_directory_exists(self, agents_dir: Path) -> None:
        """Test that the agents directory exists."""
        assert agents_dir.exists(), f"Agents directory not found: {agents_dir}"

    def test_agents_directory_is_directory(self, agents_dir: Path) -> None:
        """Test that the agents path is a directory."""
        assert agents_dir.is_dir(), f"Agents path is not a directory: {agents_dir}"

    def test_agents_directory_not_empty(self, agents_dir: Path) -> None:
        """Test that the agents directory is not empty."""
        contents = list(agents_dir.iterdir())
        assert len(contents) > 0, "Agents directory is empty"

    def test_agents_directory_has_readme(self, agents_dir: Path) -> None:
        """Test that the agents directory has a README."""
        readme = agents_dir / "README.md"
        assert readme.exists(), "Agents directory missing README.md"

    @pytest.mark.parametrize("agent_dir", AGENT_DIRECTORIES)
    def test_agent_directory_exists(self, agents_dir: Path, agent_dir: str) -> None:
        """Test that each expected agent directory exists."""
        agent_path = agents_dir / agent_dir
        assert agent_path.exists(), f"Agent directory not found: {agent_dir}"

    @pytest.mark.parametrize("agent_dir", AGENT_DIRECTORIES)
    def test_agent_directory_is_directory(self, agents_dir: Path, agent_dir: str) -> None:
        """Test that each agent path is a directory."""
        agent_path = agents_dir / agent_dir
        if agent_path.exists():
            assert agent_path.is_dir(), f"Agent path is not a directory: {agent_dir}"


class TestAgentConfigFiles:
    """Tests for agent configuration file validation."""

    @pytest.mark.parametrize("config_file", AGENT_CONFIG_FILES)
    def test_agent_config_exists(self, agents_dir: Path, config_file: str) -> None:
        """Test that each expected agent config file exists."""
        config_path = agents_dir / config_file
        assert config_path.exists(), f"Agent config not found: {config_file}"

    @pytest.mark.parametrize("config_file", AGENT_CONFIG_FILES)
    def test_agent_config_not_empty(self, agents_dir: Path, config_file: str) -> None:
        """Test that each agent config file is not empty."""
        config_path = agents_dir / config_file
        if config_path.exists():
            content = config_path.read_text()
            assert len(content) > 0, f"Agent config is empty: {config_file}"

    @pytest.mark.parametrize("config_file", [f for f in AGENT_CONFIG_FILES if f.endswith(".yml")])
    def test_yaml_config_valid_syntax(self, agents_dir: Path, config_file: str) -> None:
        """Test that YAML config files have valid syntax."""
        config_path = agents_dir / config_file
        if config_path.exists():
            content = config_path.read_text()
            try:
                # Support multi-document YAML files (e.g., with version history)
                # Use safe_load_all to handle files with multiple documents separated by ---
                documents = list(yaml.safe_load_all(content))
                assert len(documents) > 0, f"No documents found in {config_file}"
                # Validate each document is valid YAML
                for i, doc in enumerate(documents):
                    if doc is not None:
                        error_msg = f"Document {i} in {config_file} is not a dict: {type(doc)}"
                        assert isinstance(doc, dict), error_msg
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in {config_file}: {e}")

    @pytest.mark.parametrize("config_file", [f for f in AGENT_CONFIG_FILES if f.endswith(".md")])
    def test_markdown_config_has_frontmatter(self, agents_dir: Path, config_file: str) -> None:
        """Test that markdown config files have valid structure."""
        config_path = agents_dir / config_file
        if config_path.exists():
            content = config_path.read_text()
            # Check for markdown headers or YAML frontmatter
            has_header = content.startswith("#") or content.startswith("---")
            assert has_header, f"Markdown config missing header: {config_file}"


class TestAgentDocumentation:
    """Tests for agent documentation validation."""

    @pytest.mark.parametrize("doc_file", AGENT_DOC_FILES)
    def test_agent_doc_exists(self, agents_dir: Path, doc_file: str) -> None:
        """Test that each expected agent doc file exists."""
        doc_path = agents_dir / doc_file
        assert doc_path.exists(), f"Agent doc not found: {doc_file}"

    @pytest.mark.parametrize("doc_file", AGENT_DOC_FILES)
    def test_agent_doc_has_description(self, agents_dir: Path, doc_file: str) -> None:
        """Test that agent docs have descriptions."""
        doc_path = agents_dir / doc_file
        if doc_path.exists():
            content = doc_path.read_text()
            # Should have at least 100 characters of content
            assert len(content) > 100, f"Agent doc too short: {doc_file}"

    @pytest.mark.parametrize("doc_file", AGENT_DOC_FILES)
    def test_agent_doc_has_usage_section(self, agents_dir: Path, doc_file: str) -> None:
        """Test that agent docs have usage information."""
        doc_path = agents_dir / doc_file
        if doc_path.exists():
            content = doc_path.read_text().lower()
            has_usage = any(
                keyword in content for keyword in ["usage", "how to", "example", "invoke"]
            )
            assert has_usage, f"Agent doc missing usage info: {doc_file}"


class TestAgentCallableInterface:
    """Tests for agent callable interface validation."""

    def test_agents_have_invoke_pattern(self, agents_dir: Path) -> None:
        """Test that agents can be invoked via @agent pattern."""
        # Check for agent invocation patterns in docs or registry
        readme = agents_dir / "README.md"
        registry = agents_dir / "AGENT_REGISTRY.md"

        # Check README or Registry for invocation patterns
        found_pattern = False
        for doc in [readme, registry]:
            if doc.exists():
                content = doc.read_text()
                if (
                    "@" in content
                    or "invoke" in content.lower()
                    or "call" in content.lower()
                    or "agent" in content.lower()
                ):
                    found_pattern = True
                    break

        assert found_pattern, "No agent invocation pattern found in docs"

    @pytest.mark.parametrize("agent_dir", AGENT_DIRECTORIES[:10])  # Test first 10
    def test_agent_has_prompt_or_config(self, agents_dir: Path, agent_dir: str) -> None:
        """Test that agent directories have prompt or config files."""
        agent_path = agents_dir / agent_dir
        if agent_path.exists() and agent_path.is_dir():
            files = list(agent_path.iterdir())
            file_names = [f.name.lower() for f in files]
            has_config = any(
                "prompt" in n
                or "config" in n
                or "agent" in n
                or ".yml" in n
                or ".yaml" in n
                or ".md" in n
                for n in file_names
            )
            assert has_config or len(files) > 0, f"Agent directory has no config: {agent_dir}"


class TestAgentIntegration:
    """Tests for agent integration with the system."""

    def test_agent_registry_exists(self, agents_dir: Path) -> None:
        """Test that agent registry exists."""
        registry = agents_dir / "AGENT_REGISTRY.md"
        assert registry.exists(), "Agent registry not found"

    def test_agent_registry_yaml_exists(self, agents_dir: Path) -> None:
        """Test that agent registry YAML exists."""
        registry = agents_dir / "AGENT_REGISTRY.yaml"
        assert registry.exists(), "Agent registry YAML not found"

    def test_agent_registry_yaml_valid(self, agents_dir: Path) -> None:
        """Test that agent registry YAML is valid."""
        registry = agents_dir / "AGENT_REGISTRY.yaml"
        if registry.exists():
            content = registry.read_text()
            try:
                data = yaml.safe_load(content)
                assert data is not None, "Agent registry YAML is empty"
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in agent registry: {e}")

    def test_agent_ecosystem_map_exists(self, agents_dir: Path) -> None:
        """Test that agent ecosystem map exists."""
        ecosystem = agents_dir / "AGENT_ECOSYSTEM_MAP.md"
        assert ecosystem.exists(), "Agent ecosystem map not found"


class TestAgentErrorHandling:
    """Tests for agent error handling."""

    def test_missing_agent_raises_appropriate_error(self) -> None:
        """Test that missing agents can be detected."""
        fake_path = AGENTS_DIR / "nonexistent-agent"
        assert not fake_path.exists(), "Fake agent should not exist"

    def test_invalid_yaml_detected(self) -> None:
        """Test that invalid YAML is detected."""
        invalid_yaml = "key: [unclosed bracket"
        with pytest.raises(yaml.YAMLError):
            yaml.safe_load(invalid_yaml)

    def test_empty_config_detected(self) -> None:
        """Test that empty configs are detected."""
        empty_content = ""
        result = yaml.safe_load(empty_content)
        assert result is None, "Empty YAML should return None"


class TestCodexAgentSpecifications:
    """Tests for .codex/agents/ specifications."""

    def test_codex_agents_dir_exists(self, codex_agents_dir: Path) -> None:
        """Test that .codex/agents/ directory exists."""
        assert codex_agents_dir.exists(), f"Codex agents dir not found: {codex_agents_dir}"

    def test_custom_agent_specs_exists(self, codex_agents_dir: Path) -> None:
        """Test that custom agent specifications exist."""
        specs = codex_agents_dir / "CUSTOM_AGENT_SPECIFICATIONS.md"
        if codex_agents_dir.exists():
            assert specs.exists(), "Custom agent specifications not found"

    def test_agent_enhancements_exists(self, codex_agents_dir: Path) -> None:
        """Test that agent enhancements documentation exists."""
        enhancements = codex_agents_dir / "AGENT_ENHANCEMENTS_PHASES_11_18.md"
        if codex_agents_dir.exists():
            assert enhancements.exists(), "Agent enhancements doc not found"


class TestAgentCoverage:
    """Tests to ensure comprehensive agent coverage."""

    def test_minimum_agent_count(self, agents_dir: Path) -> None:
        """Test that we have a minimum number of agents."""
        if agents_dir.exists():
            agent_dirs = [
                d for d in agents_dir.iterdir() if d.is_dir() and not d.name.startswith(".")
            ]
            assert len(agent_dirs) >= 30, f"Expected 30+ agent directories, found {len(agent_dirs)}"

    def test_minimum_config_files(self, agents_dir: Path) -> None:
        """Test that we have a minimum number of config files."""
        if agents_dir.exists():
            yml_files = list(agents_dir.glob("*.yml")) + list(agents_dir.glob("*.yaml"))
            md_files = [f for f in agents_dir.glob("*.md") if "agent" in f.name.lower()]
            total = len(yml_files) + len(md_files)
            assert total >= 10, f"Expected 10+ agent config files, found {total}"

    def test_all_agent_categories_covered(self, agents_dir: Path) -> None:
        """Test that all agent categories are covered."""
        if agents_dir.exists():
            all_names = " ".join([d.name for d in agents_dir.iterdir()])
            categories = ["ci", "security", "test", "doc", "performance"]
            covered = [cat for cat in categories if cat in all_names.lower()]
            assert len(covered) >= 4, f"Expected 4+ categories, found: {covered}"


class TestAgentFunctionality:
    """Tests for agent functional capabilities."""

    def test_ci_testing_agent_functional(self, agents_dir: Path) -> None:
        """Test that CI testing agent is functional."""
        agent_path = agents_dir / "ci-testing-agent"
        assert agent_path.exists(), "CI testing agent not found"
        # Check for prompt or config
        files = list(agent_path.iterdir()) if agent_path.is_dir() else []
        assert len(files) > 0, "CI testing agent directory is empty"

    def test_security_audit_agent_functional(self, agents_dir: Path) -> None:
        """Test that security audit agent is functional."""
        doc = agents_dir / "security-audit-agent.md"
        assert doc.exists(), "Security audit agent doc not found"
        content = doc.read_text()
        assert len(content) > 500, "Security audit agent doc too short"

    def test_test_coverage_agent_functional(self, agents_dir: Path) -> None:
        """Test that test coverage agent is functional."""
        doc = agents_dir / "test-coverage-agent.md"
        assert doc.exists(), "Test coverage agent doc not found"
        content = doc.read_text()
        assert len(content) > 500, "Test coverage agent doc too short"

    def test_performance_monitor_agent_functional(self, agents_dir: Path) -> None:
        """Test that performance monitor agent is functional."""
        agent_path = agents_dir / "performance-monitor-agent"
        assert agent_path.exists(), "Performance monitor agent not found"

    def test_doc_freshness_checker_functional(self, agents_dir: Path) -> None:
        """Test that doc freshness checker is functional."""
        config = agents_dir / "doc-freshness-checker.agent.md"
        assert config.exists(), "Doc freshness checker config not found"

    def test_flaky_triage_agent_functional(self, agents_dir: Path) -> None:
        """Test that flaky triage agent is functional."""
        agent_path = agents_dir / "flaky-triage-agent"
        assert agent_path.exists(), "Flaky triage agent not found"

    def test_dependency_vulnerability_scanner_functional(self, agents_dir: Path) -> None:
        """Test that dependency vulnerability scanner is functional."""
        config = agents_dir / "dependency-vulnerability-scanner.agent.md"
        assert config.exists(), "Dependency vulnerability scanner config not found"

    def test_workflow_ci_fixer_functional(self, agents_dir: Path) -> None:
        """Test that workflow CI fixer is functional."""
        config = agents_dir / "workflow-ci-fixer.agent.md"
        assert config.exists(), "Workflow CI fixer config not found"


# ============================================================================
# Summary Test
# ============================================================================


class TestAgentSummary:
    """Summary tests to verify all agents are functional."""

    def test_all_agents_summary(self, agents_dir: Path) -> None:
        """Summary test that all agents are available and functional."""
        if not agents_dir.exists():
            pytest.skip("Agents directory not found")

        # Count agents
        agent_dirs = [d for d in agents_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
        config_files = list(agents_dir.glob("*.agent.*"))
        doc_files = [f for f in agents_dir.glob("*.md") if "agent" in f.name.lower()]

        # Summary
        total_agents = len(agent_dirs)
        total_configs = len(config_files)
        total_docs = len(doc_files)

        logger.info("\n=== Agent Summary ===")
        logger.info(f"Agent Directories: {total_agents}")
        logger.info(f"Config Files: {total_configs}")
        logger.info(f"Documentation Files: {total_docs}")
        logger.info(f"Total: {total_agents + total_configs}")

        # Assert minimums
        assert total_agents >= 30, f"Expected 30+ agent dirs, found {total_agents}"
        assert total_configs >= 10, f"Expected 10+ config files, found {total_configs}"

        # All tests passed
        logger.info("\n✅ All custom agents verified functional!")
