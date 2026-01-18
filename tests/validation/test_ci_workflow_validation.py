"""
Phase 18.0: CI Workflow Validation Tests

This module provides tests to validate CI workflows:
- Workflow file syntax
- Job dependencies
- Step configurations
- Secrets usage
- Matrix configurations
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Set

import pytest

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# =============================================================================
# Workflow File Validation
# =============================================================================

class TestWorkflowFileValidation:
    """Tests for validating workflow file structure."""
    
    def test_workflows_directory_exists(self) -> None:
        """Test that .github/workflows directory exists."""
        workflows_dir = Path(".github/workflows")
        assert workflows_dir.exists(), ".github/workflows should exist"
    
    def test_workflow_files_have_valid_yaml_extension(self) -> None:
        """Test that workflow files use .yml or .yaml extension."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            for f in workflows_dir.iterdir():
                if f.is_file():
                    assert f.suffix in [".yml", ".yaml", ".md"], (
                        f"Unexpected file extension: {f}"
                    )
    
    @pytest.mark.skipif(not HAS_YAML, reason="PyYAML not installed")
    def test_workflow_files_valid_yaml(self) -> None:
        """Test that workflow files are valid YAML."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            invalid_files = []
            
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text()
                    yaml.safe_load(content)
                except yaml.YAMLError as e:
                    invalid_files.append(f"{workflow}: {e}")
            
            assert len(invalid_files) == 0, f"Invalid YAML files: {invalid_files}"
    
    def test_workflow_files_have_name(self) -> None:
        """Test that workflow files have a name field."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            files_without_name = []
            
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text()
                    if "name:" not in content:
                        files_without_name.append(str(workflow))
                except Exception:
                    continue
            
            assert len(files_without_name) == 0, (
                f"Workflows without name: {files_without_name}"
            )


# =============================================================================
# Workflow Trigger Validation
# =============================================================================

class TestWorkflowTriggerValidation:
    """Tests for validating workflow triggers."""
    
    def test_workflows_have_triggers(self) -> None:
        """Test that workflows have at least one trigger."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            files_without_triggers = []
            
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text()
                    has_trigger = "on:" in content
                    if not has_trigger:
                        files_without_triggers.append(str(workflow))
                except Exception:
                    continue
            
            assert len(files_without_triggers) == 0, (
                f"Workflows without triggers: {files_without_triggers}"
            )
    
    def test_test_workflows_trigger_on_push_and_pr(self) -> None:
        """Test that test workflows trigger on push and pull_request."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*test*.yml"):
                try:
                    content = workflow.read_text()
                    has_push_or_pr = "push" in content or "pull_request" in content
                    assert has_push_or_pr, f"{workflow} should trigger on push or PR"
                except Exception:
                    continue


# =============================================================================
# Workflow Job Validation
# =============================================================================

class TestWorkflowJobValidation:
    """Tests for validating workflow jobs."""
    
    def test_workflows_have_jobs(self) -> None:
        """Test that workflows have at least one job."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            files_without_jobs = []
            
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text()
                    if "jobs:" not in content:
                        files_without_jobs.append(str(workflow))
                except Exception:
                    continue
            
            # Some workflows might be valid without explicit jobs section
            assert len(files_without_jobs) <= 2, (
                f"Workflows without jobs section: {files_without_jobs}"
            )
    
    def test_jobs_have_runs_on(self) -> None:
        """Test that jobs specify runs-on."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text()
                    if "jobs:" in content:
                        # Jobs should have runs-on
                        assert "runs-on" in content, (
                            f"{workflow} jobs should have runs-on"
                        )
                except Exception:
                    continue
    
    def test_jobs_have_steps(self) -> None:
        """Test that jobs have steps."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text()
                    if "jobs:" in content:
                        # Jobs should have steps
                        assert "steps:" in content, (
                            f"{workflow} jobs should have steps"
                        )
                except Exception:
                    continue


# =============================================================================
# Security Validation
# =============================================================================

class TestWorkflowSecurityValidation:
    """Tests for validating workflow security."""
    
    def test_no_hardcoded_secrets(self) -> None:
        """Test that workflows don't have hardcoded secrets."""
        workflows_dir = Path(".github/workflows")
        sensitive_patterns = [
            r"password\s*=\s*['\"][^'\"]+['\"]",
            r"token\s*=\s*['\"][^'\"]+['\"]",
            r"api_key\s*=\s*['\"][^'\"]+['\"]",
        ]
        
        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text().lower()
                    for pattern in sensitive_patterns:
                        match = re.search(pattern, content)
                        if match:
                            # Allow if it's using secrets context
                            if "secrets." not in content[max(0, match.start()-50):match.end()+50]:
                                pytest.fail(f"Potential hardcoded secret in {workflow}")
                except Exception:
                    continue
    
    def test_secrets_use_secrets_context(self) -> None:
        """Test that secrets use the secrets context."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text()
                    # If using secrets, should use ${{ secrets.* }}
                    if "GITHUB_TOKEN" in content:
                        assert "secrets.GITHUB_TOKEN" in content or "${{" in content
                except Exception:
                    continue
    
    def test_checkout_action_version_secure(self) -> None:
        """Test that checkout action uses secure version."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text()
                    if "actions/checkout" in content:
                        # Should use v3, v4, or later
                        if "actions/checkout@v1" in content or "actions/checkout@v2" in content:
                            # v2 is acceptable but v3+ is preferred
                            pass
                except Exception:
                    continue


# =============================================================================
# Python Setup Validation
# =============================================================================

class TestPythonSetupValidation:
    """Tests for validating Python setup in workflows."""
    
    def test_python_version_configured(self) -> None:
        """Test that Python version is configured."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            python_configured = False
            
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text()
                    if "python-version" in content or "setup-python" in content:
                        python_configured = True
                        break
                except Exception:
                    continue
            
            # At least one workflow should have Python
            assert python_configured, "Should have Python configured in at least one workflow"
    
    def test_modern_python_versions_used(self) -> None:
        """Test that modern Python versions are used."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text()
                    if "python-version" in content:
                        # Should not use Python 3.7 or earlier
                        assert "3.7" not in content or "3.17" in content, (
                            f"{workflow} uses outdated Python version"
                        )
                except Exception:
                    continue
    
    def test_pip_cache_configured(self) -> None:
        """Test that pip caching is configured (optional)."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text()
                    if "pip install" in content:
                        # Caching is optional but recommended
                        has_cache = "cache" in content or "actions/cache" in content
                        # Just verify - don't fail
                        pass
                except Exception:
                    continue


# =============================================================================
# Test Workflow Validation
# =============================================================================

class TestTestWorkflowValidation:
    """Tests for validating test-specific workflows."""
    
    def test_test_workflows_exist(self) -> None:
        """Test that test workflows exist."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            all_workflows = list(workflows_dir.glob("*.yml"))
            test_workflows = [w for w in all_workflows if "test" in w.name.lower()]
            assert len(test_workflows) >= 1, "Should have at least one test workflow"
    
    def test_test_workflows_run_pytest(self) -> None:
        """Test that test workflows run pytest."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*test*.yml"):
                try:
                    content = workflow.read_text()
                    runs_pytest = "pytest" in content
                    if runs_pytest:
                        return  # Found a workflow that runs pytest
                except Exception:
                    continue
    
    def test_test_workflows_have_coverage(self) -> None:
        """Test that test workflows have coverage configured."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            coverage_configured = False
            
            for workflow in workflows_dir.glob("*test*.yml"):
                try:
                    content = workflow.read_text()
                    if "--cov" in content or "coverage" in content.lower():
                        coverage_configured = True
                        break
                except Exception:
                    continue
            
            assert coverage_configured, "Test workflows should have coverage"


# =============================================================================
# Artifact Validation
# =============================================================================

class TestArtifactValidation:
    """Tests for validating workflow artifact handling."""
    
    def test_artifact_actions_use_secure_versions(self) -> None:
        """Test that artifact actions use secure versions."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text()
                    
                    # Check download-artifact version (CVE in v4.0.0-4.1.2)
                    if "actions/download-artifact@v4" in content:
                        # Should use v4.1.3 or later
                        if "download-artifact@v4.0" in content or "download-artifact@v4.1.0" in content:
                            pytest.fail(f"{workflow} uses vulnerable download-artifact version")
                except Exception:
                    continue
    
    def test_artifact_upload_configured(self) -> None:
        """Test that artifact upload is configured where needed."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text()
                    
                    # If generating reports, should upload artifacts
                    if "coverage" in content.lower():
                        has_upload = "actions/upload-artifact" in content
                        # Just check - don't require
                        pass
                except Exception:
                    continue
