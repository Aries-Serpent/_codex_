"""Tests for CI integration (v1.5.4)."""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest


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

    assert result.ci == "github_actions"
    assert result.repo == "owner/repo"
    assert result.branch == "main"
    assert result.commit == "abc123"
    assert result.is_ci is True


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

    assert result.ci == "gitlab_ci"
    assert result.repo == "group/project"
    assert result.branch == "feature"


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

    assert result.ci == "jenkins"
    assert result.branch == "develop"
    assert result.run_id == "42"


def test_detect_ci_environment_none():
    """Test no CI environment detection."""
    from scripts.space_traversal.ci_integration import detect_ci_environment

    with patch.dict(os.environ, {}, clear=True):
        result = detect_ci_environment()

    assert result.ci is None
    assert result.is_ci is False


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

    assert result.is_pr is True
    assert result.pr_number == "123"


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

    assert result is True
    assert summary_file.exists()

    content = summary_file.read_text()
    assert "Audit Results" in content
    assert "Average Score" in content
    assert "0.75" in content
    assert "Regressions Detected" in content


def test_write_github_step_summary_no_env(tmp_path: Path):
    """Test step summary when not in GitHub Actions."""
    from scripts.space_traversal.ci_integration import write_github_step_summary

    with patch.dict(os.environ, {}, clear=True):
        result = write_github_step_summary(0.85, [], [])

    assert result is False


def test_set_github_output(tmp_path: Path):
    """Test GitHub Actions output variable setting."""
    from scripts.space_traversal.ci_integration import set_github_output

    output_file = tmp_path / "output.txt"

    env = {"GITHUB_OUTPUT": str(output_file)}

    with patch.dict(os.environ, env, clear=True):
        set_github_output("avg_score", "0.85")
        set_github_output("status", "pass")

    content = output_file.read_text()
    assert "avg_score=0.85" in content
    assert "status=pass" in content


def test_set_github_output_multiline(tmp_path: Path):
    """Test GitHub output with multiline value."""
    from scripts.space_traversal.ci_integration import set_github_output

    output_file = tmp_path / "output.txt"

    env = {"GITHUB_OUTPUT": str(output_file)}

    with patch.dict(os.environ, env, clear=True):
        set_github_output("report", "line1\nline2\nline3")

    content = output_file.read_text()
    assert "report<<" in content
    assert "line1" in content
    assert "line2" in content


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

    assert "Audit Pipeline Results" in comment
    assert "0.75" in comment
    assert "Regressions" in comment
    assert "cap3" in comment
    assert "Improvements" in comment
    assert "cap1" in comment


def test_generate_pr_comment_no_regressions():
    """Test PR comment with no regressions."""
    from scripts.space_traversal.ci_integration import generate_pr_comment

    capabilities = [{"id": "cap1", "score": 0.90}]

    comment = generate_pr_comment(
        avg_score=0.90,
        capabilities=capabilities,
        regressions=[],
    )

    assert "✅" in comment
    assert "Regressions" not in comment.split("Summary")[0]  # Not in main section


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

    assert result["avg_score"] == 0.75
    assert result["capability_count"] == 3
    assert result["regression_count"] == 1
    assert result["high_count"] == 1
    assert result["medium_count"] == 1
    assert result["low_count"] == 1
    assert result["has_regressions"] is True
    assert result["has_high_severity"] is True
    assert result["status"] == "warn"


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

    assert result.ci == "azure_pipelines"
    assert result.repo == "my-repo"


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

    assert result.ci == "circleci"
    assert result.repo == "my-project"
