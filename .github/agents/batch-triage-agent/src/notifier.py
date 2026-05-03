"""
Notifier - Stakeholder notification system

Handles notifications to Slack, email, and GitHub for batch triage results
and remediation actions.
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class NotificationChannel(Enum):
    """Notification channels."""

    SLACK = "slack"
    EMAIL = "email"
    GITHUB = "github"


class NotificationPriority(Enum):
    """Notification priority levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Notification:
    """A notification to be sent."""

    title: str
    message: str
    channel: NotificationChannel
    priority: NotificationPriority
    recipients: Optional[list[str]] = None
    metadata: Optional[dict[str, Any]] = None

    def __post_init__(self):
        if self.recipients is None:
            self.recipients = []
        if self.metadata is None:
            self.metadata = {}


class Notifier:
    """
    Sends notifications to various channels based on triage results.

    Capabilities:
    - Slack notifications
    - Email notifications
    - GitHub issue comments
    - Priority-based routing
    """

    def __init__(
        self,
        slack_webhook_url: Optional[str] = None,
        email_enabled: bool = False,
        github_enabled: bool = True,
        dry_run: bool = False,
    ):
        """
        Initialize notifier.

        Args:
            slack_webhook_url: Slack webhook URL
            email_enabled: Whether email notifications are enabled
            github_enabled: Whether GitHub notifications are enabled
            dry_run: If True, log notifications without sending
        """
        self.slack_webhook_url = slack_webhook_url or os.environ.get("SLACK_WEBHOOK_URL")
        self.email_enabled = email_enabled
        self.github_enabled = github_enabled
        self.dry_run = dry_run

        self.notifications_sent: list[Notification] = []

    def notify_batch_triage_complete(
        self,
        total_failures: int,
        groups: list[dict[str, Any]],
        metrics: dict[str, Any],
        report_url: Optional[str] = None,
    ) -> None:
        """
        Notify stakeholders that batch triage is complete.

        Args:
            total_failures: Total number of failures triaged
            groups: Triage groups
            metrics: Analysis metrics
            report_url: URL to full report
        """
        # Determine priority based on severity
        critical_count = sum(1 for g in groups if g.get("severity") == "critical")
        high_count = sum(1 for g in groups if g.get("severity") == "high")

        if critical_count > 0:
            priority = NotificationPriority.CRITICAL
        elif high_count > 0:
            priority = NotificationPriority.HIGH
        else:
            priority = NotificationPriority.MEDIUM

        # Build message
        message = self._build_triage_summary_message(
            total_failures, groups, metrics, report_url
        )

        # Send to appropriate channels based on priority
        if priority in [NotificationPriority.CRITICAL, NotificationPriority.HIGH]:
            # Send to Slack
            if self.slack_webhook_url:
                self._send_slack_notification(
                    title="🚨 Batch Triage Complete - Action Required",
                    message=message,
                    priority=priority,
                )

        # Always post to GitHub if enabled
        if self.github_enabled:
            self._send_github_notification(
                title="Batch Triage Complete",
                message=message,
                priority=priority,
            )

    def notify_remediation_available(
        self,
        actions: list[dict[str, Any]],
        auto_appliable: int,
        requires_approval: int,
    ) -> None:
        """
        Notify that remediations are available.

        Args:
            actions: List of remediation actions
            auto_appliable: Number of auto-appliable actions
            requires_approval: Number of actions requiring approval
        """
        message = f"""
📋 **Remediation Actions Available**

- **Auto-appliable**: {auto_appliable} actions
- **Requires approval**: {requires_approval} actions
- **Total actions**: {len(actions)}

Review and approve actions in the GitHub Actions workflow.
        """.strip()

        priority = NotificationPriority.HIGH if requires_approval > 0 else NotificationPriority.MEDIUM

        if self.slack_webhook_url:
            self._send_slack_notification(
                title="Remediation Actions Ready",
                message=message,
                priority=priority,
            )

    def notify_remediation_applied(
        self,
        action_id: str,
        description: str,
        success: bool,
        error: Optional[str] = None,
    ) -> None:
        """
        Notify that a remediation was applied.

        Args:
            action_id: Action ID
            description: Action description
            success: Whether application was successful
            error: Error message if failed
        """
        if success:
            message = f"✅ **Remediation Applied**: {description}"
            priority = NotificationPriority.LOW
        else:
            message = f"❌ **Remediation Failed**: {description}\nError: {error}"
            priority = NotificationPriority.HIGH

        if self.github_enabled:
            self._send_github_notification(
                title="Remediation Result",
                message=message,
                priority=priority,
            )

    def notify_escalation(
        self,
        reason: str,
        failures: list[dict[str, Any]],
        recommended_actions: list[str],
    ) -> None:
        """
        Escalate critical issues to engineering leads.

        Args:
            reason: Escalation reason
            failures: List of failures requiring escalation
            recommended_actions: Recommended next steps
        """
        message = f"""
🚨 **ESCALATION REQUIRED** 🚨

**Reason**: {reason}

**Affected Failures**: {len(failures)}

**Recommended Actions**:
{chr(10).join(f"- {action}" for action in recommended_actions)}

Immediate attention required from engineering leads.
        """.strip()

        # Send to multiple channels for critical escalations
        if self.slack_webhook_url:
            self._send_slack_notification(
                title="ESCALATION: Critical CI Failures",
                message=message,
                priority=NotificationPriority.CRITICAL,
            )

        if self.github_enabled:
            self._send_github_notification(
                title="Escalation Required",
                message=message,
                priority=NotificationPriority.CRITICAL,
            )

    def _build_triage_summary_message(
        self,
        total_failures: int,
        groups: list[dict[str, Any]],
        metrics: dict[str, Any],
        report_url: Optional[str] = None,
    ) -> str:
        """Build summary message for triage results."""
        # Count by severity
        severity_counts = {}
        for group in groups:
            severity = group.get("severity", "unknown")
            severity_counts[severity] = severity_counts.get(severity, 0) + group.get("failure_count", 0)

        severity_lines = []
        for severity in ["critical", "high", "medium", "low"]:
            count = severity_counts.get(severity, 0)
            if count > 0:
                emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(severity, "⚪")
                severity_lines.append(f"  {emoji} **{severity.upper()}**: {count}")

        message_parts = [
            f"**Total Failures**: {total_failures}",
            f"**Groups Identified**: {len(groups)}",
            "",
            "**By Severity**:",
        ]
        message_parts.extend(severity_lines)

        # Add metrics
        if metrics:
            message_parts.extend([
                "",
                "**Analysis Metrics**:",
                f"  - Average Confidence: {metrics.get('avg_confidence', 0):.2f}",
                f"  - High Confidence: {metrics.get('high_confidence_count', 0)}",
                f"  - Low Confidence: {metrics.get('low_confidence_count', 0)}",
            ])

        if report_url:
            message_parts.extend([
                "",
                f"**Full Report**: {report_url}",
            ])

        return "\n".join(message_parts)

    def _send_slack_notification(
        self,
        title: str,
        message: str,
        priority: NotificationPriority,
    ) -> None:
        """Send Slack notification."""
        if not self.slack_webhook_url:
            logger.warning("Slack webhook URL not configured - skipping notification")
            return

        if self.dry_run:
            logger.info(f"[DRY RUN] Would send Slack notification: {title}")
            return

        # Build Slack message
        color = {
            NotificationPriority.CRITICAL: "danger",
            NotificationPriority.HIGH: "warning",
            NotificationPriority.MEDIUM: "#439FE0",
            NotificationPriority.LOW: "good",
        }.get(priority, "#CCCCCC")

        payload = {
            "attachments": [{
                "color": color,
                "title": title,
                "text": message,
                "footer": "Batch Triage Agent",
            }]
        }

        try:
            import requests
            response = requests.post(
                self.slack_webhook_url,
                json=payload,
                timeout=10,
            )
            response.raise_for_status()

            notification = Notification(
                title=title,
                message=message,
                channel=NotificationChannel.SLACK,
                priority=priority,
            )
            self.notifications_sent.append(notification)

            logger.info(f"Sent Slack notification: {title}")
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")

    def _send_github_notification(
        self,
        title: str,
        message: str,
        priority: NotificationPriority,
    ) -> None:
        """Send GitHub notification (logged for now)."""
        if not self.github_enabled:
            return

        if self.dry_run:
            logger.info(f"[DRY RUN] Would send GitHub notification: {title}")
            return

        # For now, just log - actual GitHub comment would require issue number
        notification = Notification(
            title=title,
            message=message,
            channel=NotificationChannel.GITHUB,
            priority=priority,
        )
        self.notifications_sent.append(notification)

        logger.info(f"GitHub notification prepared: {title}")

    def get_statistics(self) -> dict[str, Any]:
        """
        Get notification statistics.

        Returns:
            Dictionary of statistics
        """
        by_channel = {}
        by_priority = {}

        for notif in self.notifications_sent:
            channel = notif.channel.value
            priority = notif.priority.value

            by_channel[channel] = by_channel.get(channel, 0) + 1
            by_priority[priority] = by_priority.get(priority, 0) + 1

        return {
            "total_sent": len(self.notifications_sent),
            "by_channel": by_channel,
            "by_priority": by_priority,
        }
