"""
GitHub Guru Agent — Issue Triage

Routes issues to the correct agent, suggests labels from the taxonomy,
and enforces label taxonomy compliance per .github/labels.yml.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

try:
    from .analyzers import IssueAnalysisResult, IssueAnalyzer
except ImportError:
    from analyzers import IssueAnalysisResult, IssueAnalyzer
try:
    from .github_client import GitHubAPIClient
except ImportError:
    from github_client import GitHubAPIClient

logger = logging.getLogger(__name__)


# --- Label taxonomy (mirrors .github/labels.yml) ---------------------------------

LABEL_TAXONOMY: dict[str, str] = {
    "bug": "d73a4a",
    "documentation": "0075ca",
    "enhancement": "a2eeef",
    "security": "e4e669",
    "performance": "fbca04",
    "ci/cd": "6f42c1",
    "test": "bfd4f2",
    "dependencies": "0366d6",
    "good first issue": "7057ff",
    "help wanted": "008672",
    "wontfix": "ffffff",
    "duplicate": "cfd3d7",
    "question": "d876e3",
    "P0-critical": "b60205",
    "P1-high": "d93f0b",
    "P2-medium": "fbca04",
    "P3-low": "0e8a16",
}

PRIORITY_LABELS = {
    "critical": "P0-critical",
    "high": "P1-high",
    "medium": "P2-medium",
    "low": "P3-low",
}


@dataclass
class TriageResult:
    """Result of issue triage."""

    issue_number: int
    analysis: IssueAnalysisResult
    labels_to_apply: list[str] = field(default_factory=list)
    priority_label: str = ""
    is_compliant: bool = True
    compliance_gaps: list[str] = field(default_factory=list)
    summary_md: str = ""


class IssueTriage:
    """
    Triages issues: resolves label taxonomy, applies priority labels,
    enforces compliance, and emits routing suggestions.

    SAFE_MODE: Only reads issue data; label application is advisory only
    (no write calls are issued).
    """

    def __init__(self, client: GitHubAPIClient):
        self.client = client
        self._analyzer = IssueAnalyzer(client)

    def triage(self, issue_number: int) -> TriageResult:
        """
        Perform full triage on an issue.

        Returns:
            TriageResult with labels, priority, compliance status.
        """
        analysis = self._analyzer.analyze(issue_number)

        # Map suggested labels to taxonomy
        labels_to_apply: list[str] = []
        compliance_gaps: list[str] = []

        for label in analysis.suggested_labels:
            if label in LABEL_TAXONOMY:
                labels_to_apply.append(label)
            else:
                compliance_gaps.append(f"Label '{label}' not in taxonomy")

        # Add priority label
        priority_label = PRIORITY_LABELS.get(analysis.suggested_priority, "P3-low")
        labels_to_apply.append(priority_label)

        is_compliant = len(compliance_gaps) == 0

        summary = (
            f"**Triage Report — Issue #{issue_number}**\n\n"
            f"{analysis.summary_md}\n\n"
            f"**Labels to apply**: {', '.join(f'`{lbl}`' for lbl in labels_to_apply) or '(none)'}\n"
            f"**Taxonomy compliance**: {'✅ Compliant' if is_compliant else '⚠️ Gaps found'}\n"
        )
        if compliance_gaps:
            summary += "**Compliance gaps**:\n" + "\n".join(f"- {g}" for g in compliance_gaps) + "\n"
        if analysis.routing_agent:
            summary += f"**Route to**: `{analysis.routing_agent}`\n"

        return TriageResult(
            issue_number=issue_number,
            analysis=analysis,
            labels_to_apply=labels_to_apply,
            priority_label=priority_label,
            is_compliant=is_compliant,
            compliance_gaps=compliance_gaps,
            summary_md=summary,
        )

    def check_label_compliance(self, repo_labels: list[str]) -> dict[str, Any]:
        """
        Check that all labels in the repository match the taxonomy.

        Args:
            repo_labels: List of label names from the GitHub API.

        Returns:
            Dict with 'compliant', 'extra', 'missing' lists.
        """
        taxonomy_set = set(LABEL_TAXONOMY.keys())
        repo_set = set(repo_labels)

        extra = sorted(repo_set - taxonomy_set)
        missing = sorted(taxonomy_set - repo_set)

        return {
            "compliant": len(extra) == 0 and len(missing) == 0,
            "extra_labels": extra,
            "missing_labels": missing,
            "compliance_score": max(
                0.0,
                100.0 * (1 - (len(extra) + len(missing)) / max(len(taxonomy_set), 1)),
            ),
        }
