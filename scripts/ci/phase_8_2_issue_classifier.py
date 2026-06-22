#!/usr/bin/env python3
"""
Phase 8.2: Issue Classifier Engine

Main classification engine integrating severity scoring and GitHub API.
Handles issue processing, classification, and routing metadata.
"""

import json
import sys
from dataclasses import asdict, dataclass
from typing import Optional

from phase_8_2_severity_scorer import Category, SeverityScore, SeverityScorer


@dataclass
class ClassificationResult:
    """Complete classification result for an issue."""

    issue_number: int
    issue_title: str
    severity: str  # P0-P4
    category: str
    confidence: float
    reasoning: str
    suggested_labels: list[str]
    suggested_assignee: Optional[str]
    keywords_matched: list[str]
    routing_target: str
    slack_alert: bool


class IssueClassifier:
    """Main issue classification engine."""

    def __init__(self, routing_rules: Optional[dict] = None):
        """
        Initialize the classifier.

        Args:
            routing_rules: Optional routing configuration (dict)
        """
        self.scorer = SeverityScorer()
        self.routing_rules = routing_rules or {}

    def classify_issue(
        self,
        issue_number: int,
        title: str,
        body: str,
        labels: Optional[list[str]] = None,
        assignees: Optional[list[str]] = None,
    ) -> ClassificationResult:
        """
        Classify a GitHub issue.

        Args:
            issue_number: GitHub issue number
            title: Issue title
            body: Issue body/description
            labels: Current GitHub labels
            assignees: Current assignees

        Returns:
            ClassificationResult with all classification data
        """
        labels = labels or []

        # Score severity and category
        score: SeverityScore = self.scorer.score(title, body, labels)

        # Generate suggested labels
        suggested_labels = self._generate_labels(score, labels)

        # Determine routing
        routing_target = self._get_routing_target(score)
        suggested_assignee = self._get_suggested_assignee(score, routing_target)

        # Decide if Slack alert needed
        slack_alert = score.severity.value in ["P0", "P1"]

        return ClassificationResult(
            issue_number=issue_number,
            issue_title=title,
            severity=score.severity.value,
            category=score.category.value,
            confidence=score.confidence,
            reasoning=score.reasoning,
            suggested_labels=suggested_labels,
            suggested_assignee=suggested_assignee,
            keywords_matched=score.keywords_matched,
            routing_target=routing_target,
            slack_alert=slack_alert,
        )

    def _generate_labels(self, score: SeverityScore, current_labels: list[str]) -> list[str]:
        """Generate suggested GitHub labels."""
        labels = []

        # Add severity label
        severity_label = f"severity-{score.severity.value}"
        if severity_label not in current_labels:
            labels.append(severity_label)

        # Add category label
        category_label = f"category-{score.category.value.replace(' ', '-').lower()}"
        if category_label not in current_labels:
            labels.append(category_label)

        # Add additional context labels
        if "security" in score.category.value.lower():
            labels.append("security-alert")
        if score.severity.value == "P0":
            labels.append("critical")
        if "performance" in score.category.value.lower():
            labels.append("performance")

        return [l for l in labels if l not in current_labels]

    def _get_routing_target(self, score: SeverityScore) -> str:
        """Determine routing target based on severity and category."""
        severity = score.severity.value

        # Use routing rules if provided
        if self.routing_rules:
            rule_key = f"{severity}:{score.category.value}"
            if rule_key in self.routing_rules:
                return self.routing_rules[rule_key].get("target", "maintainers")

        # Default routing by severity
        routing_map = {
            "P0": "emergency-team",
            "P1": "urgent-maintainers",
            "P2": "standard-maintainers",
            "P3": "backlog",
            "P4": "community",
        }

        return routing_map.get(severity, "maintainers")

    def _get_suggested_assignee(
        self, score: SeverityScore, routing_target: str
    ) -> Optional[str]:
        """Suggest an assignee based on routing target and category."""
        # Map categories to expertise/team
        if "Security" in score.category.value:
            return "security-team"
        if "Infrastructure" in score.category.value:
            return "devops-team"
        if "Documentation" in score.category.value:
            return "docs-team"
        if "Testing" in score.category.value:
            return "qa-team"

        # Default assignees by severity
        if score.severity.value == "P0":
            return "on-call-team"
        elif score.severity.value == "P1":
            return "urgent-maintainers"

        return None

    def classify_from_json(self, issue_json: str) -> ClassificationResult:
        """
        Classify an issue from JSON data (GitHub API format).

        Args:
            issue_json: JSON string with issue data

        Returns:
            ClassificationResult
        """
        data = json.loads(issue_json)
        return self.classify_issue(
            issue_number=data.get("number", 0),
            title=data.get("title", ""),
            body=data.get("body", ""),
            labels=[label.get("name", "") for label in data.get("labels", [])],
            assignees=[
                user.get("login", "") for user in data.get("assignees", [])
            ],
        )


def main():
    """CLI entry point for issue classification."""
    if len(sys.argv) < 2:
        print("Usage: phase_8_2_issue_classifier.py <issue_json>")
        print("  or: phase_8_2_issue_classifier.py --test")
        sys.exit(1)

    if sys.argv[1] == "--test":
        # Run test cases
        test_issues = [
            {
                "number": 1,
                "title": "Production database is down",
                "body": "Users cannot access the platform. Outage started 5 min ago.",
                "labels": [],
                "assignees": [],
            },
            {
                "number": 2,
                "title": "Security vulnerability in auth module",
                "body": "Found XSS vulnerability in login form. Critical security breach.",
                "labels": [],
                "assignees": [],
            },
            {
                "number": 3,
                "title": "Fix typo in README",
                "body": "Found 'teh' instead of 'the' on line 42.",
                "labels": [],
                "assignees": [],
            },
        ]

        classifier = IssueClassifier()
        for issue in test_issues:
            result = classifier.classify_issue(
                issue_number=issue["number"],
                title=issue["title"],
                body=issue["body"],
                labels=[l.get("name", "") for l in issue.get("labels", [])],
            )
            print(f"\n{'=' * 60}")
            print(f"Issue #{result.issue_number}: {result.issue_title}")
            print(f"Severity: {result.severity} (confidence: {result.confidence:.2f})")
            print(f"Category: {result.category}")
            print(f"Routing: {result.routing_target}")
            print(f"Labels: {', '.join(result.suggested_labels)}")
            print(f"Reasoning: {result.reasoning}")
            print(f"Slack Alert: {result.slack_alert}")
        sys.exit(0)

    # Classify from JSON input
    try:
        issue_json = sys.argv[1]
        classifier = IssueClassifier()
        result = classifier.classify_from_json(issue_json)
        print(json.dumps(asdict(result), indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
