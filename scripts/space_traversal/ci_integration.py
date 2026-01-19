#!/usr/bin/env python3
"""
Ci Integration

Purpose:
    [To be documented - Ci Integration]

Usage:
    python scripts/space_traversal/ci_integration.py [options]
    
    Examples:
    $ python scripts/space_traversal/ci_integration.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""


from __future__ import annotations

"""
CI/CD integration helpers for v1.5.4

Provides utilities for integrating audit pipeline with various CI systems.

Features:
- CI environment detection (GitHub Actions, GitLab CI, Jenkins)
- GitHub Actions step summary generation
- Output variable helpers
- PR comment generation

Example:
    from scripts.space_traversal.ci_integration import (
        detect_ci_environment,
        write_github_step_summary,
    )

    env = detect_ci_environment()
    if env["ci"] == "github_actions":
        write_github_step_summary(avg_score, capabilities, regressions)
"""

import os
from typing import Any, Optional

__all__ = [
    "detect_ci_environment",
    "write_github_step_summary",
    "set_github_output",
    "generate_pr_comment",
    "CIEnvironment",
]

# Maximum number of regressions to display in summary tables
MAX_REGRESSIONS_DISPLAY = 10


class CIEnvironment:
    """CI environment information."""

    def __init__(self, data: dict[str, Optional[str]]):
        self.ci = data.get("ci")
        self.repo = data.get("repo")
        self.branch = data.get("branch")
        self.commit = data.get("commit")
        self.pr_number = data.get("pr_number")
        self.run_id = data.get("run_id")
        self.run_url = data.get("run_url")
        self._data = data

    def __getitem__(self, key: str) -> Optional[str]:
        return self._data.get(key)

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return self._data.get(key, default)

    @property
    def is_ci(self) -> bool:
        return self.ci is not None

    @property
    def is_pr(self) -> bool:
        return self.pr_number is not None


def detect_ci_environment() -> CIEnvironment:
    """
    Detect CI environment and extract metadata.

    Supports:
    - GitHub Actions
    - GitLab CI
    - Jenkins
    - Azure Pipelines
    - CircleCI

    Returns:
        CIEnvironment with detected values
    """
    env = os.environ

    # GitHub Actions
    if env.get("GITHUB_ACTIONS") == "true":
        return CIEnvironment(
            {
                "ci": "github_actions",
                "repo": env.get("GITHUB_REPOSITORY"),
                "branch": env.get("GITHUB_REF_NAME"),
                "commit": env.get("GITHUB_SHA"),
                "pr_number": env.get("GITHUB_PR_NUMBER"),
                "run_id": env.get("GITHUB_RUN_ID"),
                "run_url": (
                    f"https://github.com/{env.get('GITHUB_REPOSITORY')}"
                    f"/actions/runs/{env.get('GITHUB_RUN_ID')}"
                ),
                "actor": env.get("GITHUB_ACTOR"),
                "event_name": env.get("GITHUB_EVENT_NAME"),
            }
        )

    # GitLab CI
    if env.get("GITLAB_CI") == "true":
        return CIEnvironment(
            {
                "ci": "gitlab_ci",
                "repo": env.get("CI_PROJECT_PATH"),
                "branch": env.get("CI_COMMIT_REF_NAME"),
                "commit": env.get("CI_COMMIT_SHA"),
                "mr_iid": env.get("CI_MERGE_REQUEST_IID"),
                "pr_number": env.get("CI_MERGE_REQUEST_IID"),
                "pipeline_id": env.get("CI_PIPELINE_ID"),
                "run_id": env.get("CI_PIPELINE_ID"),
                "run_url": env.get("CI_PIPELINE_URL"),
            }
        )

    # Jenkins
    if env.get("JENKINS_URL"):
        return CIEnvironment(
            {
                "ci": "jenkins",
                "repo": env.get("GIT_URL"),
                "branch": env.get("GIT_BRANCH"),
                "commit": env.get("GIT_COMMIT"),
                "build_number": env.get("BUILD_NUMBER"),
                "run_id": env.get("BUILD_NUMBER"),
                "run_url": env.get("BUILD_URL"),
                "pr_number": env.get("CHANGE_ID"),
            }
        )

    # Azure Pipelines
    if env.get("TF_BUILD") == "True":
        return CIEnvironment(
            {
                "ci": "azure_pipelines",
                "repo": env.get("BUILD_REPOSITORY_NAME"),
                "branch": env.get("BUILD_SOURCEBRANCHNAME"),
                "commit": env.get("BUILD_SOURCEVERSION"),
                "run_id": env.get("BUILD_BUILDID"),
                "run_url": env.get("SYSTEM_TEAMFOUNDATIONCOLLECTIONURI"),
                "pr_number": env.get("SYSTEM_PULLREQUEST_PULLREQUESTNUMBER"),
            }
        )

    # CircleCI
    if env.get("CIRCLECI") == "true":
        return CIEnvironment(
            {
                "ci": "circleci",
                "repo": env.get("CIRCLE_PROJECT_REPONAME"),
                "branch": env.get("CIRCLE_BRANCH"),
                "commit": env.get("CIRCLE_SHA1"),
                "run_id": env.get("CIRCLE_BUILD_NUM"),
                "run_url": env.get("CIRCLE_BUILD_URL"),
                "pr_number": env.get("CIRCLE_PR_NUMBER"),
            }
        )

    return CIEnvironment({"ci": None})


def write_github_step_summary(
    avg_score: float,
    capabilities: list[dict],
    regressions: list[dict],
    title: str = "Audit Results",
) -> bool:
    """
    Write GitHub Actions step summary.

    Args:
        avg_score: Average capability score
        capabilities: List of capability dictionaries
        regressions: List of regression dictionaries
        title: Summary title

    Returns:
        True if summary was written, False otherwise
    """
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return False

    with open(summary_path, "a", encoding="utf-8") as f:
        f.write(f"## 🔍 {title}\n\n")

        # Summary badges
        status = "✅" if not regressions else "⚠️"
        f.write(f"**Status:** {status} | ")
        f.write(f"**Average Score:** {avg_score:.3f} | ")
        f.write(f"**Capabilities:** {len(capabilities)} | ")
        f.write(f"**Regressions:** {len(regressions)}\n\n")

        # Score distribution
        high = sum(1 for c in capabilities if c.get("score", 0) >= 0.85)
        medium = sum(1 for c in capabilities if 0.70 <= c.get("score", 0) < 0.85)
        low = sum(1 for c in capabilities if c.get("score", 0) < 0.70)

        f.write("### Score Distribution\n\n")
        f.write(f"- 🟢 High (≥0.85): {high}\n")
        f.write(f"- 🟡 Medium (0.70-0.85): {medium}\n")
        f.write(f"- 🔴 Low (<0.70): {low}\n\n")

        # Regressions
        if regressions:
            f.write("### ⚠️ Regressions Detected\n\n")
            f.write("| Capability | Previous | Current | Δ |\n")
            f.write("|------------|----------|---------|---|\n")
            for r in regressions[:10]:  # Limit to 10
                prev = r.get("previous", r.get("previous_avg", 0))
                curr = r.get("current", r.get("current_score", 0))
                delta = r.get("delta", 0)
                f.write(f"| {r.get('capability_id', 'unknown')} | {prev:.3f} | ")
                f.write(f"{curr:.3f} | {delta:+.3f} |\n")
            if len(regressions) > MAX_REGRESSIONS_DISPLAY:
                f.write(
                    f"\n*... and {len(regressions) - MAX_REGRESSIONS_DISPLAY} more regressions*\n"
                )

    return True


def set_github_output(name: str, value: str) -> bool:
    """
    Set GitHub Actions output variable.

    Args:
        name: Output variable name
        value: Output value

    Returns:
        True if output was set, False otherwise
    """
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as f:
            # Handle multi-line values
            if "\n" in value:
                import uuid

                delimiter = str(uuid.uuid4())
                f.write(f"{name}<<{delimiter}\n{value}\n{delimiter}\n")
            else:
                f.write(f"{name}={value}\n")
        return True
    return False


def set_github_env(name: str, value: str) -> bool:
    """
    Set GitHub Actions environment variable.

    Args:
        name: Environment variable name
        value: Environment value

    Returns:
        True if env was set, False otherwise
    """
    env_path = os.environ.get("GITHUB_ENV")
    if env_path:
        with open(env_path, "a", encoding="utf-8") as f:
            if "\n" in value:
                import uuid

                delimiter = str(uuid.uuid4())
                f.write(f"{name}<<{delimiter}\n{value}\n{delimiter}\n")
            else:
                f.write(f"{name}={value}\n")
        return True
    return False


def generate_pr_comment(
    avg_score: float,
    capabilities: list[dict],
    regressions: list[dict],
    improvements: list[dict] | None = None,
    compare_to: str = "baseline",
) -> str:
    """
    Generate PR comment markdown.

    Args:
        avg_score: Average capability score
        capabilities: List of capability dictionaries
        regressions: List of regression dictionaries
        improvements: Optional list of improvements
        compare_to: What the comparison is against

    Returns:
        Markdown string for PR comment
    """
    lines = [
        "## 🔍 Audit Pipeline Results",
        "",
    ]

    # Summary section
    status_emoji = "✅" if not regressions else "⚠️"
    if avg_score < 0.70:
        status_emoji = "🔴"

    lines.extend(
        [
            f"**Status:** {status_emoji}",
            f"**Average Score:** {avg_score:.3f}",
            f"**Compared to:** {compare_to}",
            "",
        ]
    )

    # Quick stats
    high = sum(1 for c in capabilities if c.get("score", 0) >= 0.85)
    low = sum(1 for c in capabilities if c.get("score", 0) < 0.70)

    lines.extend(
        [
            "### Summary",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Capabilities | {len(capabilities)} |",
            f"| High scores (≥0.85) | {high} |",
            f"| Low scores (<0.70) | {low} |",
            f"| Regressions | {len(regressions)} |",
            "",
        ]
    )

    # Regressions section
    if regressions:
        lines.extend(
            [
                "### ⚠️ Regressions",
                "",
                "| Capability | Change | Severity |",
                "|------------|--------|----------|",
            ]
        )
        for r in regressions[:5]:
            delta = r.get("delta", 0)
            severity = r.get("severity", "medium")
            severity_emoji = "🔴" if severity == "high" else "🟡"
            lines.append(
                f"| {r.get('capability_id', 'unknown')} | {delta:+.3f} | {severity_emoji} {severity} |"
            )
        if len(regressions) > 5:
            lines.append(f"\n*... and {len(regressions) - 5} more*")
        lines.append("")

    # Improvements section
    if improvements:
        lines.extend(
            [
                "### ✅ Improvements",
                "",
                "| Capability | Change |",
                "|------------|--------|",
            ]
        )
        for imp in improvements[:5]:
            delta = imp.get("delta", 0)
            lines.append(f"| {imp.get('capability_id', 'unknown')} | {delta:+.3f} |")
        lines.append("")

    lines.extend(
        [
            "---",
            "*Generated by Audit Pipeline v1.5.4*",
        ]
    )

    return "\n".join(lines)


def export_for_ci(
    avg_score: float,
    capabilities: list[dict],
    regressions: list[dict],
) -> dict[str, Any]:
    """
    Export audit results in CI-friendly format.

    Args:
        avg_score: Average capability score
        capabilities: List of capability dictionaries
        regressions: List of regression dictionaries

    Returns:
        Dictionary suitable for CI output
    """
    return {
        "avg_score": round(avg_score, 6),
        "capability_count": len(capabilities),
        "regression_count": len(regressions),
        "high_count": sum(1 for c in capabilities if c.get("score", 0) >= 0.85),
        "medium_count": sum(1 for c in capabilities if 0.70 <= c.get("score", 0) < 0.85),
        "low_count": sum(1 for c in capabilities if c.get("score", 0) < 0.70),
        "has_regressions": len(regressions) > 0,
        "has_high_severity": any(r.get("severity") == "high" for r in regressions),
        "regression_ids": [r.get("capability_id") for r in regressions],
        "status": "pass" if not regressions else "warn",
    }
