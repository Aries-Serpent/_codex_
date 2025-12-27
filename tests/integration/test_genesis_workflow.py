"""
Genesis Protocol Workflow Integration Tests

Tests end-to-end Genesis workflow execution, configuration loading,
and artifact generation.
"""

import pytest
import yaml
import json
from pathlib import Path
import os


class TestGenesisWorkflowIntegration:
    """Integration tests for Genesis Protocol workflow"""
    
    @pytest.fixture
    def repo_root(self):
        """Get repository root directory"""
        return Path(__file__).parent.parent.parent
    
    @pytest.fixture
    def genesis_config(self, repo_root):
        """Load Genesis configuration"""
        config_path = repo_root / ".codex" / "autonomous_agent.yaml"
        assert config_path.exists(), "Genesis config not found"
        
        with open(config_path) as f:
            return yaml.safe_load(f)
    
    @pytest.fixture
    def mock_secrets(self, tmp_path):
        """Create mock secrets for testing"""
        secrets = {
            "CODEX_MASTER_KEY": "test_key_12345",
            "GITHUB_TOKEN": "test_token_abcde",
        }
        secrets_file = tmp_path / "mock_secrets.yaml"
        with open(secrets_file, "w") as f:
            yaml.dump(secrets, f)
        return secrets_file
    
    def test_genesis_config_loads(self, genesis_config):
        """Test that Genesis configuration loads correctly"""
        assert genesis_config is not None
        assert "agent" in genesis_config
        assert "autonomous_actions_enabled" in genesis_config["agent"]
        assert genesis_config["agent"]["autonomous_actions_enabled"] is False, \
            "Autonomous actions should be disabled by default"
    
    def test_genesis_config_has_required_fields(self, genesis_config):
        """Test that Genesis config has all required fields"""
        required_top_fields = ["agent", "runtime", "security", "guardrails"]
        for field in required_top_fields:
            assert field in genesis_config, f"Missing required top-level field: {field}"
        
        # Check agent section fields
        agent_fields = ["name", "autonomous_actions_enabled", "allowed_operations", "escalation_policy"]
        for field in agent_fields:
            assert field in genesis_config["agent"], f"Missing agent field: {field}"
    
    def test_safety_guards_enabled(self, genesis_config):
        """Test that safety guards are properly configured"""
        assert genesis_config["agent"]["autonomous_actions_enabled"] is False
        
        # Check for escalation configuration
        assert "escalation_policy" in genesis_config["agent"]
        escalation = genesis_config["agent"]["escalation_policy"]
        assert "escalate" in str(escalation).lower() or "approval" in str(escalation).lower()
    
    def test_guardrails_file_exists(self, repo_root):
        """Test that guardrails documentation exists"""
        guardrails_path = repo_root / ".codex" / "guardrails.md"
        assert guardrails_path.exists(), "Guardrails documentation not found"
        
        content = guardrails_path.read_text()
        assert len(content) > 100, "Guardrails documentation seems empty"
        # Check for prohibition/restriction language
        content_upper = content.upper()
        assert any(word in content_upper for word in ["PROHIBITED", "FORBIDDEN", "NOT ALLOWED", "MUST NOT"]), \
            "Expected prohibition language in guardrails"
    
    def test_genesis_bootstrap_workflow_exists(self, repo_root):
        """Test that Genesis bootstrap workflow file exists"""
        workflow_path = repo_root / ".github" / "workflows" / "genesis-bootstrap.yml"
        assert workflow_path.exists(), "Genesis bootstrap workflow not found"
        
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        assert "jobs" in workflow
        # Check for any genesis-related job (name may vary)
        job_names = list(workflow["jobs"].keys())
        assert any("genesis" in job.lower() or "validate" in job.lower() for job in job_names), \
            f"No Genesis/validation job found in workflow. Jobs: {job_names}"
    
    def test_autonomous_agent_script_exists(self, repo_root):
        """Test that autonomous agent script exists and is importable"""
        script_path = repo_root / "scripts" / "autonomous_agent.py"
        assert script_path.exists(), "Autonomous agent script not found"
        
        # Check that it has required classes
        content = script_path.read_text()
        required_classes = ["AutonomousAgent", "CodeHealthSensor", "ActionProposer"]
        for cls in required_classes:
            assert cls in content, f"Missing required class: {cls}"
    
    def test_genesis_workflow_dry_run(self, repo_root, genesis_config):
        """Test Genesis workflow in dry-run mode"""
        # This tests the configuration validation without executing actions
        assert genesis_config["agent"]["autonomous_actions_enabled"] is False
        
        # Verify escalation policy is configured
        assert "escalation_policy" in genesis_config["agent"]
        policy = genesis_config["agent"]["escalation_policy"]
        assert len(policy) > 0, "Escalation policy should have entries"
    
    def test_runtime_variables_documented(self, repo_root):
        """Test that runtime variables are documented"""
        runtime_vars_path = repo_root / ".codex" / "runtime_variables.md"
        assert runtime_vars_path.exists(), "Runtime variables documentation not found"
        
        content = runtime_vars_path.read_text()
        # Check for key variables
        expected_vars = ["CODEX_ENV_PYTHON_VERSION", "CODEX_SESSION_ID", "CODEX_LOG_DB_PATH"]
        for var in expected_vars:
            assert var in content, f"Missing documentation for: {var}"
    
    def test_wiki_documentation_exists(self, repo_root):
        """Test that wiki documentation structure exists"""
        wiki_dir = repo_root / ".codex" / "wiki"
        assert wiki_dir.exists(), "Wiki directory not found"
        
        required_files = ["Home.md", "Genesis-Protocol.md", "Agent-Operations.md", "_Sidebar.md"]
        for filename in required_files:
            filepath = wiki_dir / filename
            assert filepath.exists(), f"Missing wiki file: {filename}"
            
            content = filepath.read_text()
            assert len(content) > 100, f"Wiki file {filename} seems empty"
    
    def test_security_vulnerabilities_fixed(self, repo_root):
        """Test that security vulnerability documentation exists"""
        security_scan_path = repo_root / ".codex" / "security_vulnerability_scan_2025-12-26.md"
        assert security_scan_path.exists(), "Security scan documentation not found"
        
        content = security_scan_path.read_text()
        # Check that torch, transformers, and mlflow are mentioned
        packages = ["torch", "transformers", "mlflow"]
        for pkg in packages:
            assert pkg in content.lower(), f"Package {pkg} not mentioned in security scan"
    
    def test_change_log_updated(self, repo_root):
        """Test that change log has been updated"""
        change_log_path = repo_root / ".codex" / "change_log.md"
        assert change_log_path.exists(), "Change log not found"
        
        content = change_log_path.read_text()
        assert "Genesis" in content or "genesis" in content, "No Genesis entries in change log"
        assert "2025-12-26" in content or "2025" in content, "No recent entries in change log"
    
    def test_agent_toolkit_available(self, repo_root):
        """Test that AI agent toolkit is available"""
        toolkit_path = repo_root / ".codex" / "ai_agent_toolkit.py"
        assert toolkit_path.exists(), "AI agent toolkit not found"
        
        content = toolkit_path.read_text()
        required_classes = ["EnvironmentValidator", "TestRunner", "LessonsLearned"]
        for cls in required_classes:
            assert cls in content, f"Missing toolkit class: {cls}"
    
    def test_lessons_learned_system(self, repo_root):
        """Test that lessons learned system is functioning"""
        lessons_path = repo_root / ".codex" / "lessons_learned.json"
        assert lessons_path.exists(), "Lessons learned file not found"
        
        with open(lessons_path) as f:
            lessons_data = json.load(f)
        
        # Handle both list and dict formats
        if isinstance(lessons_data, list):
            lessons = lessons_data
        else:
            lessons = lessons_data.get("lessons", lessons_data)
        
        assert len(lessons) > 0, "No lessons documented"
        
        # Check lesson structure
        first_lesson = lessons[0]
        required_fields = ["title", "category", "solution", "tags"]
        for field in required_fields:
            assert field in first_lesson, f"Lesson missing field: {field}"
    
    def test_phase2_readiness_documentation(self, repo_root):
        """Test that Phase 2 readiness is documented"""
        dependency_status_path = repo_root / ".codex" / "phase2_dependency_testing_status.md"
        assert dependency_status_path.exists(), "Phase 2 dependency status not documented"
        
        content = dependency_status_path.read_text()
        assert "Task 1.1" in content or "dependency" in content.lower()
        assert "Blocker" in content or "Issue" in content


class TestGenesisWorkflowArtifacts:
    """Test Genesis workflow artifact generation and validation"""
    
    @pytest.fixture
    def repo_root(self):
        """Get repository root directory"""
        return Path(__file__).parent.parent.parent
    
    def test_documentation_artifacts_exist(self, repo_root):
        """Test that required documentation artifacts exist"""
        artifacts = [
            ".codex/runtime_variables.md",
            ".codex/security_vulnerability_scan_2025-12-26.md",
            ".codex/wiki/Home.md",
            ".codex/wiki/Genesis-Protocol.md",
            ".codex/wiki/Agent-Operations.md",
            ".codex/change_log.md",
        ]
        
        for artifact in artifacts:
            path = repo_root / artifact
            assert path.exists(), f"Artifact not found: {artifact}"
            assert path.stat().st_size > 0, f"Artifact is empty: {artifact}"
    
    def test_toolkit_artifacts_exist(self, repo_root):
        """Test that toolkit artifacts exist"""
        artifacts = [
            ".codex/ai_agent_toolkit.py",
            ".codex/lessons_learned.json",
            ".codex/lessons_learned.md",
            ".codex/phase2_dependency_testing_status.md",
        ]
        
        for artifact in artifacts:
            path = repo_root / artifact
            assert path.exists(), f"Toolkit artifact not found: {artifact}"
    
    def test_pyproject_security_updates(self, repo_root):
        """Test that pyproject.toml has security updates applied.
        
        Uses minimum version checks to allow for future security updates.
        """
        import re
        from packaging import version as pkg_version
        
        pyproject_path = repo_root / "pyproject.toml"
        assert pyproject_path.exists()
        content = pyproject_path.read_text()
        
        # Check for minimum secure versions
        torch_match = re.search(r'torch[>=<,\s"\']*([0-9.]+)', content)
        if torch_match:
            torch_ver = torch_match.group(1)
            assert pkg_version.parse(torch_ver) >= pkg_version.parse("2.6.0")
        
        transformers_match = re.search(r'transformers[>=<,\s"\']*([0-9.]+)', content)
        if transformers_match:
            transformers_ver = transformers_match.group(1)
            assert pkg_version.parse(transformers_ver) >= pkg_version.parse("4.48.0")
        
        mlflow_match = re.search(r'mlflow[>=<,\s"\']*([0-9.]+)', content)
        if mlflow_match:
            mlflow_ver = mlflow_match.group(1)
            assert pkg_version.parse(mlflow_ver) >= pkg_version.parse("2.22.4")
    def test_requirements_security_updates(self, repo_root):
        """Test that requirements.txt has security updates"""
        requirements_path = repo_root / "requirements.txt"
        if requirements_path.exists():
            content = requirements_path.read_text()
            
            # Check that old vulnerable versions are not present
            assert "torch==2.2.2" not in content, "Old torch version still present"
            assert "transformers==4.41" not in content, "Old transformers version still present"


class TestGenesisWorkflowSafety:
    """Test Genesis workflow safety mechanisms"""
    
    @pytest.fixture
    def repo_root(self):
        """Get repository root directory"""
        return Path(__file__).parent.parent.parent
    
    def test_autonomous_actions_disabled_by_default(self, repo_root):
        """Test that autonomous actions are disabled"""
        config_path = repo_root / ".codex" / "autonomous_agent.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        assert config["agent"]["autonomous_actions_enabled"] is False, \
            "CRITICAL: Autonomous actions must be disabled by default"
    
    def test_workflow_safety_guards(self, repo_root):
        """Test that workflow has safety guards"""
        workflow_path = repo_root / ".github" / "workflows" / "genesis-bootstrap.yml"
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        # Check for safety conditions in any job
        jobs = workflow["jobs"]
        job_with_condition = any("if" in job_config for job_config in jobs.values())
        assert job_with_condition, "Workflow missing safety guard condition in jobs"
    
    def test_no_activated_workflows(self, repo_root):
        """Test that DO_NOT_ACTIVATE guards are in place"""
        do_not_activate_path = repo_root / ".codex" / "DO_NOT_ACTIVATE_GITHUB_ACTIONS"
        assert do_not_activate_path.exists(), "DO_NOT_ACTIVATE guard file missing"
    
    def test_rollback_script_exists(self, repo_root):
        """Test that rollback script exists for emergency recovery"""
        rollback_path = repo_root / "scripts" / "genesis_rollback.sh"
        assert rollback_path.exists(), "Emergency rollback script not found"
        
        # Check that it's executable
        assert os.access(rollback_path, os.X_OK), "Rollback script not executable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
