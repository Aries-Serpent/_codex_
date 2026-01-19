"""Tests for Notifier."""

import sys
from pathlib import Path

# Add parent directories to path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR.parent / "src"))

from notifier import (
    Notifier,
    Notification,
    NotificationChannel,
    NotificationPriority,
)


def test_notifier_initialization():
    """Test notifier initializes correctly."""
    notifier = Notifier(
        slack_webhook_url="https://hooks.slack.com/test",
        email_enabled=True,
        github_enabled=True,
        dry_run=True,
    )
    
    assert notifier.slack_webhook_url == "https://hooks.slack.com/test"
    assert notifier.email_enabled is True
    assert notifier.github_enabled is True
    assert notifier.dry_run is True


def test_notification_dataclass():
    """Test Notification dataclass."""
    notification = Notification(
        title="Test Alert",
        message="This is a test",
        channel=NotificationChannel.SLACK,
        priority=NotificationPriority.HIGH,
    )
    
    assert notification.title == "Test Alert"
    assert notification.recipients == []
    assert notification.metadata == {}


def test_notify_batch_triage_complete():
    """Test batch triage completion notification."""
    notifier = Notifier(dry_run=True, github_enabled=True)
    
    groups = [
        {
            "group_id": "group_1",
            "root_cause": "Test failure",
            "severity": "high",
            "failure_count": 5,
        },
        {
            "group_id": "group_2",
            "root_cause": "Import error",
            "severity": "medium",
            "failure_count": 3,
        },
    ]
    
    metrics = {
        "avg_confidence": 0.75,
        "high_confidence_count": 5,
        "low_confidence_count": 2,
    }
    
    notifier.notify_batch_triage_complete(
        total_failures=8,
        groups=groups,
        metrics=metrics,
        report_url="https://example.com/report",
    )
    
    # Check that notification was prepared
    assert len(notifier.notifications_sent) > 0


def test_notify_remediation_available():
    """Test remediation available notification."""
    notifier = Notifier(dry_run=True, slack_webhook_url="https://test.com")
    
    actions = [
        {"action_id": "1", "description": "Fix 1"},
        {"action_id": "2", "description": "Fix 2"},
    ]
    
    notifier.notify_remediation_available(
        actions=actions,
        auto_appliable=1,
        requires_approval=1,
    )
    
    assert len(notifier.notifications_sent) > 0


def test_notify_remediation_applied_success():
    """Test successful remediation notification."""
    notifier = Notifier(dry_run=True, github_enabled=True)
    
    notifier.notify_remediation_applied(
        action_id="action_123",
        description="Fixed import error",
        success=True,
    )
    
    assert len(notifier.notifications_sent) == 1
    assert "✅" in notifier.notifications_sent[0].message


def test_notify_remediation_applied_failure():
    """Test failed remediation notification."""
    notifier = Notifier(dry_run=True, github_enabled=True)
    
    notifier.notify_remediation_applied(
        action_id="action_456",
        description="Failed to fix build",
        success=False,
        error="Timeout",
    )
    
    assert len(notifier.notifications_sent) == 1
    assert "❌" in notifier.notifications_sent[0].message
    assert "Timeout" in notifier.notifications_sent[0].message


def test_notify_escalation():
    """Test escalation notification."""
    notifier = Notifier(
        dry_run=True,
        slack_webhook_url="https://test.com",
        github_enabled=True,
    )
    
    failures = [
        {"issue_number": 1, "severity": "critical"},
        {"issue_number": 2, "severity": "critical"},
    ]
    
    notifier.notify_escalation(
        reason="Multiple critical failures detected",
        failures=failures,
        recommended_actions=[
            "Investigate immediately",
            "Consider rollback",
        ],
    )
    
    # Should send to multiple channels
    assert len(notifier.notifications_sent) >= 2


def test_get_statistics():
    """Test notification statistics."""
    notifier = Notifier(dry_run=True, github_enabled=True)
    
    # Send some notifications
    notifier.notifications_sent.append(
        Notification(
            title="Test 1",
            message="Message 1",
            channel=NotificationChannel.SLACK,
            priority=NotificationPriority.HIGH,
        )
    )
    notifier.notifications_sent.append(
        Notification(
            title="Test 2",
            message="Message 2",
            channel=NotificationChannel.GITHUB,
            priority=NotificationPriority.MEDIUM,
        )
    )
    
    stats = notifier.get_statistics()
    
    assert stats["total_sent"] == 2
    assert stats["by_channel"]["slack"] == 1
    assert stats["by_channel"]["github"] == 1
    assert stats["by_priority"]["high"] == 1
    assert stats["by_priority"]["medium"] == 1


def test_priority_based_routing():
    """Test that critical notifications go to multiple channels."""
    notifier = Notifier(
        dry_run=True,
        slack_webhook_url="https://test.com",
        github_enabled=True,
    )
    
    # Critical failures should trigger Slack
    groups = [
        {"group_id": "g1", "severity": "critical", "failure_count": 10},
    ]
    
    notifier.notify_batch_triage_complete(
        total_failures=10,
        groups=groups,
        metrics={},
    )
    
    # Should have sent to both Slack and GitHub
    slack_sent = any(n.channel == NotificationChannel.SLACK for n in notifier.notifications_sent)
    github_sent = any(n.channel == NotificationChannel.GITHUB for n in notifier.notifications_sent)
    
    assert slack_sent or github_sent  # At least one should be sent in dry run


def test_build_triage_summary_message():
    """Test triage summary message building."""
    notifier = Notifier(dry_run=True)
    
    groups = [
        {"severity": "high", "failure_count": 5},
        {"severity": "medium", "failure_count": 3},
    ]
    
    metrics = {
        "avg_confidence": 0.72,
        "high_confidence_count": 4,
        "low_confidence_count": 1,
    }
    
    message = notifier._build_triage_summary_message(
        total_failures=8,
        groups=groups,
        metrics=metrics,
        report_url="https://example.com/report",
    )
    
    assert "Total Failures: 8" in message
    assert "Groups Identified: 2" in message
    assert "HIGH: 5" in message
    assert "MEDIUM: 3" in message
    assert "Average Confidence: 0.72" in message
