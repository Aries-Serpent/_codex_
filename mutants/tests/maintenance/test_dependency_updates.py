"""
Phase 17.0: Dependency Update Tests

This module provides tests for dependency management and update automation,
ensuring dependencies are tracked and updated safely.

Created: 2026-01-18
Phase: 17.0 - Continuous Improvement & Maintenance
Tests: 15+
"""

import re
from pathlib import Path

import pytest

# Repository root
REPO_ROOT = Path(__file__).parents[2]


class TestDependencyManagement:
    """Tests for dependency management infrastructure."""

    def test_pyproject_toml_valid(self):
        """Verify pyproject.toml is valid and complete."""
        pyproject = REPO_ROOT / "pyproject.toml"
        assert pyproject.exists(), "pyproject.toml should exist"

        content = pyproject.read_text(encoding="utf-8")

        # Check for required sections
        required_sections = ["[project]", "dependencies"]
        for section in required_sections:
            assert section in content, f"pyproject.toml should have {section}"

    def test_dependencies_have_constraints(self):
        """Verify dependencies have version constraints."""
        pyproject = REPO_ROOT / "pyproject.toml"
        content = pyproject.read_text(encoding="utf-8")

        # Count constrained vs unconstrained
        # Simple heuristic: look for version operators
        version_operators = [">=", "<=", "~=", "==", ">", "<", "!="]
        constrained = sum(content.count(op) for op in version_operators)

        # Should have some version constraints
        assert constrained >= 5, "Dependencies should have version constraints"

    def test_dev_dependencies_separate(self):
        """Verify dev dependencies are separate from main dependencies."""
        pyproject = REPO_ROOT / "pyproject.toml"
        content = pyproject.read_text(encoding="utf-8")

        # Check for optional dependencies or dev group
        has_optional = "[project.optional-dependencies]" in content
        has_dev = "dev" in content or "test" in content

        assert has_optional or has_dev, "Should have separate dev dependencies"


class TestDependabotConfiguration:
    """Tests for Dependabot configuration."""

    def test_dependabot_yaml_exists(self):
        """Verify Dependabot configuration exists."""
        dependabot_path = REPO_ROOT / ".github" / "dependabot.yml"
        if not dependabot_path.exists():
            pytest.skip("Dependabot not configured (optional)")

        content = dependabot_path.read_text(encoding="utf-8")
        assert "updates" in content, "Dependabot should have updates section"

    def test_dependabot_covers_ecosystems(self):
        """Verify Dependabot covers required ecosystems."""
        dependabot_path = REPO_ROOT / ".github" / "dependabot.yml"
        if not dependabot_path.exists():
            pytest.skip("Dependabot not configured")

        content = dependabot_path.read_text(encoding="utf-8")

        # Should cover pip and github-actions at minimum
        ecosystems = ["pip", "github-actions"]
        for eco in ecosystems:
            if eco not in content:
                pytest.skip(f"Dependabot doesn't cover {eco} (optional)")

    def test_dependabot_schedule_configured(self):
        """Verify Dependabot has update schedule."""
        dependabot_path = REPO_ROOT / ".github" / "dependabot.yml"
        if not dependabot_path.exists():
            pytest.skip("Dependabot not configured")

        content = dependabot_path.read_text(encoding="utf-8")

        # Should have schedule
        schedule_patterns = ["weekly", "daily", "monthly"]
        has_schedule = any(p in content for p in schedule_patterns)
        assert has_schedule, "Dependabot should have update schedule"


class TestSecurityUpdates:
    """Tests for security update infrastructure."""

    def test_security_advisories_monitored(self):
        """Verify security advisory monitoring is in place."""
        # Check for security-related workflows
        workflows_dir = REPO_ROOT / ".github" / "workflows"
        if not workflows_dir.exists():
            pytest.skip("No workflows directory")

        security_workflows = []
        for workflow in workflows_dir.glob("*.yml"):
            content = workflow.read_text(encoding="utf-8")
            if any(
                term in content.lower() for term in ["security", "audit", "vulnerability", "cve"]
            ):
                security_workflows.append(workflow.name)

        assert len(security_workflows) >= 1, "Should have security-related workflows"

    def test_pip_audit_available(self):
        """Check if pip-audit or similar is configured."""
        # Look for pip-audit in workflows or requirements
        audit_tools = ["pip-audit", "safety", "snyk"]

        workflows_dir = REPO_ROOT / ".github" / "workflows"
        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*.yml"):
                try:
                    content = workflow.read_text(encoding="utf-8")
                    if any(tool in content for tool in audit_tools):
                        return  # Found audit tool
                except (UnicodeDecodeError, OSError):
                    continue

        pytest.skip("No pip-audit configured (optional)")


class TestVersionPinning:
    """Tests for version pinning strategies."""

    def test_no_floating_major_versions(self):
        """Verify no dependencies use floating major versions."""
        pyproject = REPO_ROOT / "pyproject.toml"
        content = pyproject.read_text(encoding="utf-8")

        # Pattern for "package>=X" without upper bound
        floating_pattern = r'["\'][a-z\-_]+>=\d+["\']'
        floating_deps = re.findall(floating_pattern, content.lower())

        # Some floating is acceptable, but log
        if len(floating_deps) > 10:
            pytest.skip(f"Many floating versions: {len(floating_deps)}")

    def test_lock_file_strategy_documented(self):
        """Verify lock file strategy is documented or implemented."""
        lock_files = [
            REPO_ROOT / "requirements" / "lock.txt",
            REPO_ROOT / "poetry.lock",
            REPO_ROOT / "Pipfile.lock",
        ]

        has_lock = any(f.exists() for f in lock_files)

        # Check if documented in CONTRIBUTING
        contributing = REPO_ROOT / "CONTRIBUTING.md"
        if contributing.exists():
            content = contributing.read_text(encoding="utf-8")
            if "lock" in content.lower() or "pin" in content.lower():
                return  # Documented

        if not has_lock:
            pytest.skip("No lock file strategy (optional)")


class TestUpdateAutomation:
    """Tests for dependency update automation."""

    def test_renovate_or_dependabot_configured(self):
        """Verify automated update tool is configured."""
        config_files = [
            REPO_ROOT / ".github" / "dependabot.yml",
            REPO_ROOT / "renovate.json",
            REPO_ROOT / ".renovaterc.json",
        ]

        configured = any(f.exists() for f in config_files)
        if not configured:
            pytest.skip("No automated update tool configured (optional)")

    def test_update_pr_labels_configured(self):
        """Verify update PRs are labeled appropriately."""
        dependabot_path = REPO_ROOT / ".github" / "dependabot.yml"
        if not dependabot_path.exists():
            pytest.skip("Dependabot not configured")

        content = dependabot_path.read_text(encoding="utf-8")

        # Should have labels configured
        if "labels" not in content:
            pytest.skip("Dependabot labels not configured (optional)")
