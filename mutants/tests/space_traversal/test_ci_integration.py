"""Tests for CI integration (v1.5.4)."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch


def test_detect_ci_environment_github():
    """Test GitHub Actions detection."""
    from scripts.space_traversal.ci_integration import detect_ci_environment

    env = {
        "GITHUB_ACTIONS": "true",
        "GITHUB_REPOSITORY": "owner/repo",
        "GITHUB_REF_NAME": "main",
        "GITHUB_SHA": "abc123",
        "GITHUB_RUN_ID": "12345",
    }

    with patch.dict(os.environ, env, clear=True):
        result = detect_ci_environment()

    assert result.ci == "github_actions", "Result must not be empty"
    assert result.repo == "owner/repo", "Result must not be empty"
    assert result.branch == "main", "Result must not be empty"
    assert result.commit == "abc123", "Result must not be empty"
    assert result.is_ci is True, "Result must not be empty"


def test_detect_ci_environment_gitlab():
    """Test GitLab CI detection."""
    from scripts.space_traversal.ci_integration import detect_ci_environment

    env = {
        "GITLAB_CI": "true",
        "CI_PROJECT_PATH": "group/project",
        "CI_COMMIT_REF_NAME": "feature",
        "CI_COMMIT_SHA": "def456",
        "CI_PIPELINE_ID": "98765",
    }

    with patch.dict(os.environ, env, clear=True):
        result = detect_ci_environment()

    assert result.ci == "gitlab_ci", "Result must not be empty"
    assert result.repo == "group/project", "Result must not be empty"
    assert result.branch == "feature", "Result must not be empty"


def test_detect_ci_environment_jenkins():
    """Test Jenkins detection."""
    from scripts.space_traversal.ci_integration import detect_ci_environment

    env = {
        "JENKINS_URL": "https://jenkins.example.com",
        "GIT_URL": "https://github.com/owner/repo.git",
        "GIT_BRANCH": "develop",
        "GIT_COMMIT": "xyz789",
        "BUILD_NUMBER": "42",
    }

    with patch.dict(os.environ, env, clear=True):
        result = detect_ci_environment()

    assert result.ci == "jenkins", "Result must not be empty"
    assert result.branch == "develop", "Result must not be empty"
    assert result.run_id == "42", "Result must not be empty"


def test_detect_ci_environment_none():
    """Test no CI environment detection."""
    from scripts.space_traversal.ci_integration import detect_ci_environment

    with patch.dict(os.environ, {}, clear=True):
        result = detect_ci_environment()

    assert result.ci is None, "Result must not be empty"
    assert result.is_ci is False, "Result must not be empty"


def test_ci_environment_is_pr():
    """Test PR detection in CI environment."""
    from scripts.space_traversal.ci_integration import detect_ci_environment

    env = {
        "GITHUB_ACTIONS": "true",
        "GITHUB_REPOSITORY": "owner/repo",
        "GITHUB_PR_NUMBER": "123",
    }

    with patch.dict(os.environ, env, clear=True):
        result = detect_ci_environment()

    assert result.is_pr is True, "Result must not be empty"
    assert result.pr_number == "123", "Result must not be empty"


def test_write_github_step_summary(tmp_path: Path):
    """Test GitHub Actions step summary writing."""
    from scripts.space_traversal.ci_integration import write_github_step_summary

    summary_file = tmp_path / "summary.md"

    capabilities = [
        {"id": "cap1", "score": 0.90},
        {"id": "cap2", "score": 0.75},
        {"id": "cap3", "score": 0.60},
    ]
    regressions = [
        {
            "capability_id": "cap3",
            "previous": 0.70,
            "current": 0.60,
            "delta": -0.10,
        }
    ]

    env = {"GITHUB_STEP_SUMMARY": str(summary_file)}

    with patch.dict(os.environ, env, clear=True):
        result = write_github_step_summary(0.75, capabilities, regressions)

    assert result is True, "Result must not be empty"
    assert summary_file.exists(), "Condition must be true"

    content = summary_file.read_text()
    assert "Audit Results" in content, "Result must not be empty"
    assert "Average Score" in content, "Content must not be empty"
    assert "0.75" in content, "Content must not be empty"
    assert "Regressions Detected" in content, "Content must not be empty"


def test_write_github_step_summary_no_env(tmp_path: Path):
    """Test step summary when not in GitHub Actions."""
    from scripts.space_traversal.ci_integration import write_github_step_summary

    with patch.dict(os.environ, {}, clear=True):
        result = write_github_step_summary(0.85, [], [])

    assert result is False, "Result must not be empty"


def test_set_github_output(tmp_path: Path):
    """Test GitHub Actions output variable setting."""
    from scripts.space_traversal.ci_integration import set_github_output

    output_file = tmp_path / "output.txt"

    env = {"GITHUB_OUTPUT": str(output_file)}

    with patch.dict(os.environ, env, clear=True):
        set_github_output("avg_score", "0.85")
        set_github_output("status", "pass")

    content = output_file.read_text()
    assert "avg_score=0.85" in content, "Content must not be empty"
    assert "status=pass" in content, "Content must not be empty"


def test_set_github_output_multiline(tmp_path: Path):
    """Test GitHub output with multiline value."""
    from scripts.space_traversal.ci_integration import set_github_output

    output_file = tmp_path / "output.txt"

    env = {"GITHUB_OUTPUT": str(output_file)}

    with patch.dict(os.environ, env, clear=True):
        set_github_output("report", "line1\nline2\nline3")

    content = output_file.read_text()
    assert "report<<" in content, "Content must not be empty"
    assert "line1" in content, "Content must not be empty"
    assert "line2" in content, "Content must not be empty"


def test_generate_pr_comment():
    """Test PR comment generation."""
    from scripts.space_traversal.ci_integration import generate_pr_comment

    capabilities = [
        {"id": "cap1", "score": 0.90},
        {"id": "cap2", "score": 0.75},
        {"id": "cap3", "score": 0.60},
    ]
    regressions = [
        {"capability_id": "cap3", "delta": -0.1, "severity": "high"},
    ]
    improvements = [
        {"capability_id": "cap1", "delta": 0.05},
    ]

    comment = generate_pr_comment(
        avg_score=0.75,
        capabilities=capabilities,
        regressions=regressions,
        improvements=improvements,
    )

    assert "Audit Pipeline Results" in comment, "Result must not be empty"
    assert "0.75" in comment, "Condition must be true"
    assert "Regressions" in comment, "Condition must be true"
    assert "cap3" in comment, "Condition must be true"
    assert "Improvements" in comment, "Condition must be true"
    assert "cap1" in comment, "Condition must be true"


def test_generate_pr_comment_no_regressions():
    """Test PR comment with no regressions."""
    from scripts.space_traversal.ci_integration import generate_pr_comment

    capabilities = [{"id": "cap1", "score": 0.90}]

    comment = generate_pr_comment(
        avg_score=0.90,
        capabilities=capabilities,
        regressions=[],
    )

    assert "✅" in comment, "Condition must be true"
    assert "Regressions" not in comment.split("Summary")[0], "Condition must be true"


def test_export_for_ci():
    """Test CI export format."""
    from scripts.space_traversal.ci_integration import export_for_ci

    capabilities = [
        {"id": "cap1", "score": 0.90},
        {"id": "cap2", "score": 0.75},
        {"id": "cap3", "score": 0.60},
    ]
    regressions = [
        {"capability_id": "cap3", "severity": "high"},
    ]

    result = export_for_ci(0.75, capabilities, regressions)

    assert result["avg_score"] == 0.75, "Result must not be empty"
    assert result["capability_count"] == 3, "Result must not be empty"
    assert result["regression_count"] == 1, "Result must not be empty"
    assert result["high_count"] == 1, "Result must not be empty"
    assert result["medium_count"] == 1, "Result must not be empty"
    assert result["low_count"] == 1, "Result must not be empty"
    assert result["has_regressions"] is True, "Result must not be empty"
    assert result["has_high_severity"] is True, "Result must not be empty"
    assert result["status"] == "warn", "Result must not be empty"


def test_detect_ci_environment_azure():
    """Test Azure Pipelines detection."""
    from scripts.space_traversal.ci_integration import detect_ci_environment

    env = {
        "TF_BUILD": "True",
        "BUILD_REPOSITORY_NAME": "my-repo",
        "BUILD_SOURCEBRANCHNAME": "main",
        "BUILD_SOURCEVERSION": "abc123",
    }

    with patch.dict(os.environ, env, clear=True):
        result = detect_ci_environment()

    assert result.ci == "azure_pipelines", "Result must not be empty"
    assert result.repo == "my-repo", "Result must not be empty"


def test_detect_ci_environment_circleci():
    """Test CircleCI detection."""
    from scripts.space_traversal.ci_integration import detect_ci_environment

    env = {
        "CIRCLECI": "true",
        "CIRCLE_PROJECT_REPONAME": "my-project",
        "CIRCLE_BRANCH": "feature",
        "CIRCLE_SHA1": "def456",
    }

    with patch.dict(os.environ, env, clear=True):
        result = detect_ci_environment()

    assert result.ci == "circleci", "Result must not be empty"
    assert result.repo == "my-project", "Result must not be empty"
