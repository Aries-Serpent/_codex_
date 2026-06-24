#!/usr/bin/env python3
"""
Phase 8.2: Label Automation & Slack Notifications

Handles GitHub label creation/updates and Slack notifications for classified issues.
"""

import json
import os
from dataclasses import asdict
from typing import Optional

import requests

from phase_8_2_issue_classifier import ClassificationResult, IssueClassifier


class GitHubLabelManager:
    """Manages GitHub labels for issue triage."""

    def __init__(self, token: Optional[str] = None):
        """
        Initialize the GitHub label manager.

        Args:
            token: GitHub API token (uses GITHUB_TOKEN env var if not provided)
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"******",
            "Accept": "application/vnd.github.v3+json",
        }

    def create_labels(
        self, owner: str, repo: str, labels: list[dict]
    ) -> list[dict]:
        """
        Create labels in a GitHub repository.

        Args:
            owner: Repository owner
            repo: Repository name
            labels: List of label dicts with name, color, description

        Returns:
            List of created label dicts
        """
        created = []
        for label in labels:
            url = f"{self.base_url}/repos/{owner}/{repo}/labels"
            data = {
                "name": label["name"],
                "color": label["color"],
                "description": label.get("description", ""),
            }
            try:
                response = requests.post(
                    url, json=data, headers=self.headers, timeout=10
                )
                if response.status_code in [201, 422]:  # 422 = already exists
                    created.append(label)
                else:
                    print(
                        f"Error creating label {label['name']}: {response.status_code}"
                    )
            except Exception as e:
                print(f"Error creating label {label['name']}: {e}")
        return created

    def apply_labels(
        self, owner: str, repo: str, issue_number: int, labels: list[str]
    ) -> bool:
        """
        Apply labels to a GitHub issue.

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number
            labels: List of label names to apply

        Returns:
            True if successful, False otherwise
        """
        url = (
            f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/labels"
        )
        try:
            response = requests.post(
                url, json=labels, headers=self.headers, timeout=10
            )
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Error applying labels to issue {issue_number}: {e}")
            return False

    def get_issue_labels(
        self, owner: str, repo: str, issue_number: int
    ) -> list[str]:
        """
        Get current labels on an issue.

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number

        Returns:
            List of label names
        """
        url = (
            f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/labels"
        )
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return [label["name"] for label in response.json()]
        except Exception as e:
            print(f"Error getting labels for issue {issue_number}: {e}")
        return []


class SlackNotifier:
    """Sends Slack notifications for triage events."""

    def __init__(self, webhook_url: Optional[str] = None):
        """
        Initialize Slack notifier.

        Args:
            webhook_url: Slack webhook URL (uses SLACK_WEBHOOK_URL env var if not provided)
        """
        self.webhook_url = webhook_url or os.environ.get("SLACK_WEBHOOK_URL")

    def send_issue_alert(
        self,
        classification: ClassificationResult,
        issue_url: str,
        channel: Optional[str] = None,
        mention_users: Optional[list[str]] = None,
    ) -> bool:
        """
        Send Slack alert for classified issue.

        Args:
            classification: ClassificationResult
            issue_url: GitHub issue URL
            channel: Slack channel (optional, overrides webhook channel)
            mention_users: List of users to mention

        Returns:
            True if successful
        """
        if not self.webhook_url:
            print("Warning: SLACK_WEBHOOK_URL not configured")
            return False

        mention_users = mention_users or []

        # Build message
        mention_str = " ".join(mention_users) if mention_users else ""
        color_map = {
            "P0": "#ff0000",  # Red
            "P1": "#ff6600",  # Orange
            "P2": "#ffaa00",  # Yellow
            "P3": "#ffdd00",  # Light yellow
            "P4": "#cccccc",  # Gray
        }

        payload = {
            "channel": channel,
            "attachments": [
                {
                    "color": color_map.get(classification.severity, "#cccccc"),
                    "title": f"Issue #{classification.issue_number}: {classification.issue_title}",
                    "title_link": issue_url,
                    "fields": [
                        {
                            "title": "Severity",
                            "value": f"{classification.severity} ({classification.confidence:.0%} confidence)",
                            "short": True,
                        },
                        {
                            "title": "Category",
                            "value": classification.category,
                            "short": True,
                        },
                        {
                            "title": "Routing",
                            "value": classification.routing_target,
                            "short": True,
                        },
                        {"title": "Assignee", "value": classification.suggested_assignee or "Unassigned", "short": True},
                        {
                            "title": "Reasoning",
                            "value": classification.reasoning,
                            "short": False,
                        },
                    ],
                    "footer": "Phase 8.2 Auto-Triage",
                    "ts": int(
                        __import__("time").time()
                    ),  # Current timestamp
                }
            ],
        }

        if mention_str:
            payload["text"] = f"{mention_str} New issue alert"

        try:
            response = requests.post(
                self.webhook_url, json=payload, timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending Slack notification: {e}")
            return False

    def send_metrics_report(
        self,
        metrics: dict,
        channel: Optional[str] = None,
    ) -> bool:
        """
        Send periodic metrics report to Slack.

        Args:
            metrics: Dictionary of metrics
            channel: Slack channel

        Returns:
            True if successful
        """
        if not self.webhook_url:
            return False

        fields = []
        for key, value in metrics.items():
            fields.append({
                "title": key,
                "value": str(value),
                "short": True,
            })

        payload = {
            "channel": channel,
            "attachments": [
                {
                    "color": "#0366d6",
                    "title": "Phase 8.2 Triage Metrics",
                    "fields": fields,
                    "footer": "Phase 8.2 Auto-Triage",
                    "ts": int(__import__("time").time()),
                }
            ],
        }

        try:
            response = requests.post(
                self.webhook_url, json=payload, timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending metrics report: {e}")
            return False


class TriageAutomation:
    """Main automation orchestrator."""

    def __init__(
        self,
        github_token: Optional[str] = None,
        slack_webhook: Optional[str] = None,
    ):
        """
        Initialize automation.

        Args:
            github_token: GitHub API token
            slack_webhook: Slack webhook URL
        """
        self.classifier = IssueClassifier()
        self.label_manager = GitHubLabelManager(github_token)
        self.slack = SlackNotifier(slack_webhook)

    def process_issue(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        title: str,
        body: str,
        issue_url: str,
        existing_labels: Optional[list[str]] = None,
    ) -> ClassificationResult:
        """
        Process and triage a GitHub issue end-to-end.

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number
            title: Issue title
            body: Issue body
            issue_url: Issue URL
            existing_labels: Current labels

        Returns:
            ClassificationResult
        """
        existing_labels = existing_labels or []

        # Classify issue
        classification = self.classifier.classify_issue(
            issue_number=issue_number,
            title=title,
            body=body,
            labels=existing_labels,
        )

        # Apply labels
        if classification.suggested_labels:
            self.label_manager.apply_labels(
                owner,
                repo,
                issue_number,
                classification.suggested_labels,
            )

        # Send Slack alert if needed
        if classification.slack_alert:
            routing_rule = self._get_routing_rule(classification.severity)
            if routing_rule:
                self.slack.send_issue_alert(
                    classification,
                    issue_url,
                    channel=routing_rule.get("slack_channel"),
                    mention_users=routing_rule.get("mention_users", []),
                )

        return classification

    def _get_routing_rule(self, severity: str) -> Optional[dict]:
        """Get routing rule for severity level."""
        # Load routing rules
        try:
            rules_path = ".codex/PHASE_8_2_ROUTING_RULES.json"
            with open(rules_path) as f:
                rules = json.load(f)
                return rules.get("severity_routing", {}).get(severity)
        except Exception as e:
            print(f"Error loading routing rules: {e}")
        return None


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: phase_8_2_label_automation.py <command> [args]")
        print("  create-labels <owner> <repo>")
        print("  process-issue <owner> <repo> <issue_number> <title> <body>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "create-labels":
        owner, repo = sys.argv[2], sys.argv[3]
        manager = GitHubLabelManager()

        # Load labels from routing rules
        try:
            with open(".codex/PHASE_8_2_ROUTING_RULES.json") as f:
                rules = json.load(f)
                all_labels = (
                    rules.get("github_labels", {}).get("severity", [])
                    + rules.get("github_labels", {}).get("category", [])
                    + rules.get("github_labels", {}).get("metadata", [])
                )
                manager.create_labels(owner, repo, all_labels)
                print(f"Created {len(all_labels)} labels in {owner}/{repo}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif command == "process-issue":
        owner, repo, issue_num, title, body = (
            sys.argv[2],
            sys.argv[3],
            int(sys.argv[4]),
            sys.argv[5],
            sys.argv[6],
        )
        automation = TriageAutomation()
        result = automation.process_issue(
            owner,
            repo,
            issue_num,
            title,
            body,
            f"https://github.com/{owner}/{repo}/issues/{issue_num}",
        )
        print(json.dumps(asdict(result), indent=2))

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)
