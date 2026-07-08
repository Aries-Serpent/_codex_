"""Tests for fast_forward_safe_files.py — classify_files and build_plan logic."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

# The script lives in scripts/ci/ — add to path before importing
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts" / "ci"))

from fast_forward_safe_files import (  # pragma: allowlist secret
    _matches_any,
    classify_files,
)


class TestMatchesAny:
    def test_exact_match(self):
        assert _matches_any("CHANGELOG.md", ["CHANGELOG.md"])

    def test_glob_match(self):
        assert _matches_any(".github/workflows/ci.yml", [".github/workflows/*.yml"])

    def test_no_match(self):
        assert not _matches_any("src/codex/models.py", [".github/workflows/*.yml"])

    def test_basename_fallback(self):
        # Pattern "*.yml" should match even though path has directories
        assert _matches_any(".github/workflows/ci.yml", ["*.yml"])

    def test_deny_pattern(self):
        assert _matches_any(".github/workflows/deploy-prod.yml", [".github/workflows/deploy*.yml"])


class TestClassifyFiles:
    _config = {
        "allowlist": [
            ".github/workflows/*.yml",
            ".github/agents/*.md",
            "scripts/ci/*.py",
            "CHANGELOG.md",
        ],
        "denylist": [
            ".github/workflows/deploy*.yml",
            ".github/workflows/release*.yml",
        ],
    }

    def test_all_allowed(self):
        files = [
            ".github/workflows/proactive-ci-monitor.yml",
            "CHANGELOG.md",
        ]
        allowed, excluded, denied = classify_files(files, self._config)
        assert allowed == files, "allowed is not valid"
        assert excluded == [], "excluded is not valid"
        assert denied == [], "denied is not valid"

    def test_deny_overrides_allow(self):
        files = [".github/workflows/deploy-prod.yml"]
        allowed, _excluded, denied = classify_files(files, self._config)
        assert allowed == [], "allowed is not valid"
        assert denied == [".github/workflows/deploy-prod.yml"], "denied is not valid"

    def test_excluded_not_in_allowlist(self):
        files = ["src/codex/models.py", "tests/test_foo.py"]
        allowed, excluded, denied = classify_files(files, self._config)
        assert allowed == [], "allowed is not valid"
        assert set(excluded) == {"src/codex/models.py", "tests/test_foo.py"}
        assert denied == [], "denied is not valid"

    def test_force_files_bypasses_allowlist(self):
        # Explicitly requested files skip the allowlist check
        files = ["src/codex/models.py"]  # not in allowlist
        allowed, excluded, _denied = classify_files(files, self._config, force_files=files)
        assert allowed == ["src/codex/models.py"], "allowed is not valid"
        assert excluded == [], "excluded is not valid"

    def test_force_files_still_denied(self):
        # Even force_files cannot bypass the denylist
        files = [".github/workflows/release-v2.yml"]
        allowed, _excluded, denied = classify_files(files, self._config, force_files=files)
        assert allowed == [], "allowed is not valid"
        assert denied == [".github/workflows/release-v2.yml"], "denied is not valid"

    def test_mixed_batch(self):
        files = [
            ".github/workflows/ci.yml",  # allowed
            ".github/workflows/deploy.yml",  # denied (deploy* pattern)
            "src/codex/app.py",  # excluded
        ]
        allowed, excluded, denied = classify_files(files, self._config)
        assert allowed == [".github/workflows/ci.yml"], "allowed is not valid"
        assert excluded == ["src/codex/app.py"], "excluded is not valid"
        assert denied == [".github/workflows/deploy.yml"], "denied is not valid"

    def test_empty_input(self):
        allowed, excluded, denied = classify_files([], self._config)
        assert allowed == excluded == denied == [], "allowed is not valid"

    def test_empty_config(self):
        # With an empty allowlist, everything is excluded
        files = [".github/workflows/ci.yml"]
        allowed, excluded, _denied = classify_files(files, {})
        assert allowed == [], "allowed is not valid"
        assert excluded == files, "excluded is not valid"


class TestBuildPlanDryRun:
    """Integration test of build_plan() logic without real GitHub API calls."""

    def test_plan_structure(self):
        """build_plan returns a PromotionPlan with correct structure."""
        from fast_forward_safe_files import build_plan

        mock_pr = {
            "head": {"ref": "my-feature-branch", "sha": "abc123def456"},  # pragma: allowlist secret
        }
        mock_files = [
            ".github/workflows/proactive-ci-monitor.yml",
            "src/codex/models.py",
            ".github/workflows/deploy-prod.yml",
        ]

        with (
            patch("fast_forward_safe_files._get_pr", return_value=mock_pr),
            patch("fast_forward_safe_files._get_pr_files", return_value=mock_files),
        ):
            plan = build_plan("owner/repo", "fake-token", 42, "main", "create-pr", None)

        assert plan.pr_number == 42, "pr_number is not valid"
        assert plan.pr_branch == "my-feature-branch", "pr_branch is not valid"
        assert plan.source_sha == "abc123def456"  # pragma: allowlist secret
        assert plan.target_branch == "main", "target_branch is not valid"
        # Workflow is allowed, model is excluded, deploy is denied
        assert ".github/workflows/proactive-ci-monitor.yml" in plan.allowed, "Condition must be true"
        assert "src/codex/models.py" in plan.excluded, "Condition must be true"
        assert ".github/workflows/deploy-prod.yml" in plan.denied, "Condition must be true"

    def test_force_files_limits_scope(self):
        """When force_files given, only those files are considered."""
        from fast_forward_safe_files import build_plan

        mock_pr = {"head": {"ref": "branch", "sha": "aaa000"}}
        all_changed = [".github/workflows/ci.yml", "src/big_module.py", "README.md"]

        with (
            patch("fast_forward_safe_files._get_pr", return_value=mock_pr),
            patch("fast_forward_safe_files._get_pr_files", return_value=all_changed),
        ):
            plan = build_plan(
                "owner/repo",
                "fake-token",
                99,
                "main",
                "create-pr",
                force_files=[".github/workflows/ci.yml"],
            )

        # Only the explicitly requested file should appear
        assert plan.allowed == [".github/workflows/ci.yml"], "allowed is not valid"
        assert plan.excluded == [], "excluded is not valid"
        assert plan.denied == [], "denied is not valid"
