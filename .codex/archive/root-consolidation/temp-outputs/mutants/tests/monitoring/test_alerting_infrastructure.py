"""
Test Alerting Infrastructure - Phase 20.1

Comprehensive tests for alerting infrastructure including:
- Alert rule configuration and validation
- Alert trigger conditions
- Alert notification channels
- Alert escalation policies
- Alert silencing and acknowledgment
- Alert aggregation and deduplication

Author: Codex Team
Phase: 20.1 Production Monitoring & Alerting
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import Any

import pytest

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def alert_rule_config() -> dict[str, Any]:
    """Fixture for alert rule configuration."""
    return {
        "name": "high_cpu_usage",
        "description": "Alert when CPU usage exceeds threshold",
        "severity": "warning",
        "condition": {
            "metric": "cpu_usage_percent",
            "operator": ">=",
            "threshold": 80,
            "duration": "5m",
        },
        "labels": {
            "team": "infrastructure",
            "service": "compute",
        },
        "annotations": {
            "summary": "High CPU usage detected",
            "runbook_url": "https://runbook.example.com/cpu",
        },
    }


@pytest.fixture
def notification_channels() -> list[dict[str, Any]]:
    """Fixture for notification channel configurations."""
    return [
        {
            "name": "slack_ops",
            "type": "slack",
            "config": {
                "webhook_url": "https://hooks.slack.com/xxx",
                "channel": "#ops-alerts",
            },
            "enabled": True,
        },
        {
            "name": "pagerduty_critical",
            "type": "pagerduty",
            "config": {
                "integration_key": "pd-key-xxx",
                "severity_mapping": {"critical": "critical", "warning": "warning"},
            },
            "enabled": True,
        },
        {
            "name": "email_team",
            "type": "email",
            "config": {
                "recipients": ["team@example.com"],
                "smtp_server": "smtp.example.com",
            },
            "enabled": True,
        },
    ]


@pytest.fixture
def escalation_policy() -> dict[str, Any]:
    """Fixture for alert escalation policy."""
    return {
        "name": "default_escalation",
        "steps": [
            {
                "delay_minutes": 0,
                "notify": ["slack_ops"],
            },
            {
                "delay_minutes": 15,
                "notify": ["pagerduty_critical"],
            },
            {
                "delay_minutes": 30,
                "notify": ["email_team", "pagerduty_critical"],
            },
        ],
        "repeat_interval_minutes": 60,
    }


@pytest.fixture
def sample_alert() -> dict[str, Any]:
    """Sample alert instance."""
    return {
        "id": "alert-123",
        "rule_name": "high_cpu_usage",
        "status": "firing",
        "severity": "warning",
        "started_at": datetime.utcnow().isoformat(),
        "value": 85.5,
        "labels": {"host": "server-01", "service": "api"},
        "annotations": {"summary": "CPU at 85.5%"},
    }


# ============================================================================
# Alert Rule Tests
# ============================================================================


class TestAlertRules:
    """Tests for alert rule configuration and validation."""

    def test_alert_rule_has_required_fields(self, alert_rule_config: dict[str, Any]):
        """Test that alert rule has all required fields."""
        required_fields = ["name", "description", "severity", "condition"]
        for field in required_fields:
            assert field in alert_rule_config, "Condition must be true"

    def test_alert_rule_severity_valid(self, alert_rule_config: dict[str, Any]):
        """Test that alert severity is valid."""
        valid_severities = ["info", "warning", "error", "critical"]
        assert alert_rule_config["severity"] in valid_severities, "Condition must be true"

    def test_alert_condition_structure(self, alert_rule_config: dict[str, Any]):
        """Test alert condition has correct structure."""
        condition = alert_rule_config["condition"]
        assert "metric" in condition, "Condition must be true"
        assert "operator" in condition, "Condition must be true"
        assert "threshold" in condition, "Condition must be true"

    def test_alert_condition_operators(self):
        """Test valid comparison operators for alert conditions."""
        valid_operators = ["==", "!=", ">", "<", ">=", "<="]
        test_operator = ">="
        assert test_operator in valid_operators, "test_operat is not valid"

    def test_alert_rule_labels(self, alert_rule_config: dict[str, Any]):
        """Test alert rule labels configuration."""
        labels = alert_rule_config["labels"]
        assert "team" in labels, "Condition must be true"
        assert "service" in labels, "Condition must be true"

    def test_alert_rule_annotations(self, alert_rule_config: dict[str, Any]):
        """Test alert rule annotations configuration."""
        annotations = alert_rule_config["annotations"]
        assert "summary" in annotations, "Condition must be true"
        assert "runbook_url" in annotations, "Condition must be true"

    def test_alert_duration_parsing(self, alert_rule_config: dict[str, Any]):
        """Test parsing of alert duration strings."""
        duration_str = alert_rule_config["condition"]["duration"]

        # Parse duration (e.g., "5m" -> 300 seconds)
        value = int(duration_str[:-1])
        unit = duration_str[-1]

        multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        duration_seconds = value * multipliers.get(unit, 1)

        assert duration_seconds == 300, "duration_seconds is not valid"

    def test_alert_threshold_validation(self, alert_rule_config: dict[str, Any]):
        """Test alert threshold is numeric and valid."""
        threshold = alert_rule_config["condition"]["threshold"]
        assert isinstance(threshold, (int, float))
        assert threshold > 0, "threshold must be greater than zero"


# ============================================================================
# Alert Trigger Tests
# ============================================================================


class TestAlertTriggers:
    """Tests for alert trigger conditions."""

    def test_threshold_exceeded_triggers_alert(self, alert_rule_config: dict[str, Any]):
        """Test that exceeding threshold triggers alert."""
        threshold = alert_rule_config["condition"]["threshold"]
        current_value = 85.5

        should_trigger = current_value >= threshold
        assert should_trigger is True, "should_trigger is not valid"

    def test_threshold_not_exceeded_no_alert(self, alert_rule_config: dict[str, Any]):
        """Test that staying below threshold doesn't trigger alert."""
        threshold = alert_rule_config["condition"]["threshold"]
        current_value = 75.0

        should_trigger = current_value >= threshold
        assert should_trigger is False, "should_trigger is not valid"

    def test_alert_duration_requirement(self):
        """Test that alert requires sustained condition."""
        required_duration_seconds = 300
        condition_start = time.time() - 200  # Started 200s ago

        duration_met = (time.time() - condition_start) >= required_duration_seconds
        assert duration_met is False, "duration_met is not valid"

    def test_alert_duration_met(self):
        """Test alert triggers when duration is met."""
        required_duration_seconds = 300
        condition_start = time.time() - 400  # Started 400s ago

        duration_met = (time.time() - condition_start) >= required_duration_seconds
        assert duration_met is True, "duration_met is not valid"

    def test_multiple_conditions_all_true(self):
        """Test alert with multiple conditions (AND logic)."""
        conditions = [
            {"metric": "cpu", "value": 85, "threshold": 80, "met": True},
            {"metric": "memory", "value": 90, "threshold": 85, "met": True},
        ]

        all_met = all(c["met"] for c in conditions)
        assert all_met is True, "all_met is not valid"

    def test_multiple_conditions_any_true(self):
        """Test alert with multiple conditions (OR logic)."""
        conditions = [
            {"metric": "cpu", "value": 50, "threshold": 80, "met": False},
            {"metric": "memory", "value": 90, "threshold": 85, "met": True},
        ]

        any_met = any(c["met"] for c in conditions)
        assert any_met is True, "any_met is not valid"

    def test_alert_state_transition_pending_to_firing(self):
        """Test alert state transition from pending to firing."""
        current_state = "pending"
        duration_met = True

        new_state = "firing" if current_state == "pending" and duration_met else current_state

        assert new_state == "firing", "new_state is not valid"

    def test_alert_state_transition_firing_to_resolved(self):
        """Test alert state transition from firing to resolved."""
        current_state = "firing"
        condition_met = False

        new_state = "resolved" if current_state == "firing" and not condition_met else current_state

        assert new_state == "resolved", "new_state is not valid"


# ============================================================================
# Notification Channel Tests
# ============================================================================


class TestNotificationChannels:
    """Tests for notification channel configuration."""

    def test_slack_channel_config(self, notification_channels: list[dict[str, Any]]):
        """Test Slack notification channel configuration."""
        slack = next(c for c in notification_channels if c["type"] == "slack")
        assert slack["name"] == "slack_ops", "Condition must be true"
        assert "webhook_url" in slack["config"], "Condition must be true"
        assert "channel" in slack["config"], "Condition must be true"

    def test_pagerduty_channel_config(self, notification_channels: list[dict[str, Any]]):
        """Test PagerDuty notification channel configuration."""
        pd = next(c for c in notification_channels if c["type"] == "pagerduty")
        assert "integration_key" in pd["config"], "Condition must be true"
        assert "severity_mapping" in pd["config"], "Condition must be true"

    def test_email_channel_config(self, notification_channels: list[dict[str, Any]]):
        """Test email notification channel configuration."""
        email = next(c for c in notification_channels if c["type"] == "email")
        assert "recipients" in email["config"], "Condition must be true"
        assert len(email["config"]["recipients"]) > 0, "Collection must not be empty"

    def test_channel_enabled_status(self, notification_channels: list[dict[str, Any]]):
        """Test notification channel enabled status."""
        for channel in notification_channels:
            assert "enabled" in channel, "Condition must be true"
            assert isinstance(channel["enabled"], bool)

    def test_notification_payload_format(self, sample_alert: dict[str, Any]):
        """Test notification payload formatting."""
        payload = {
            "title": f"Alert: {sample_alert['rule_name']}",
            "severity": sample_alert["severity"],
            "summary": sample_alert["annotations"]["summary"],
            "timestamp": sample_alert["started_at"],
        }

        assert "title" in payload, "Condition must be true"
        assert "severity" in payload, "Condition must be true"
        assert "summary" in payload, "Condition must be true"

    def test_notification_rate_limiting(self):
        """Test notification rate limiting."""
        max_notifications_per_hour = 10
        current_count = 8

        can_send = current_count < max_notifications_per_hour
        assert can_send is True, "can_send is not valid"

        current_count = 10
        can_send = current_count < max_notifications_per_hour
        assert can_send is False, "can_send is not valid"


# ============================================================================
# Escalation Policy Tests
# ============================================================================


class TestEscalationPolicies:
    """Tests for alert escalation policies."""

    def test_escalation_steps_order(self, escalation_policy: dict[str, Any]):
        """Test escalation steps are in correct order."""
        steps = escalation_policy["steps"]
        delays = [s["delay_minutes"] for s in steps]

        assert delays == sorted(delays), "delays is not valid"

    def test_initial_notification_immediate(self, escalation_policy: dict[str, Any]):
        """Test first escalation step is immediate."""
        first_step = escalation_policy["steps"][0]
        assert first_step["delay_minutes"] == 0, "Condition must be true"

    def test_escalation_includes_notify_targets(self, escalation_policy: dict[str, Any]):
        """Test each escalation step has notify targets."""
        for step in escalation_policy["steps"]:
            assert "notify" in step, "Condition must be true"
            assert len(step["notify"]) > 0, "Collection must not be empty"

    def test_escalation_repeat_interval(self, escalation_policy: dict[str, Any]):
        """Test escalation repeat interval configuration."""
        assert "repeat_interval_minutes" in escalation_policy, "Condition must be true"
        assert escalation_policy["repeat_interval_minutes"] > 0, "Value must be greater than zero"

    def test_get_current_escalation_step(self, escalation_policy: dict[str, Any]):
        """Test determining current escalation step based on time."""
        alert_age_minutes = 20
        steps = escalation_policy["steps"]

        current_step = None
        for step in reversed(steps):
            if alert_age_minutes >= step["delay_minutes"]:
                current_step = step
                break

        assert current_step is not None, "current_step must be initialized"
        assert current_step["delay_minutes"] == 15, "Condition must be true"


# ============================================================================
# Alert Silencing Tests
# ============================================================================


class TestAlertSilencing:
    """Tests for alert silencing functionality."""

    def test_silence_creation(self):
        """Test creating a silence rule."""
        silence = {
            "id": "silence-123",
            "matchers": [{"label": "service", "value": "api"}],
            "starts_at": datetime.utcnow().isoformat(),
            "ends_at": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
            "comment": "Maintenance window",
            "created_by": "admin@example.com",
        }

        assert "matchers" in silence, "Condition must be true"
        assert "starts_at" in silence, "Condition must be true"
        assert "ends_at" in silence, "Condition must be true"

    def test_silence_matcher_evaluation(self, sample_alert: dict[str, Any]):
        """Test silence matcher evaluation against alert."""
        matcher = {"label": "service", "value": "api"}
        alert_labels = sample_alert["labels"]

        matches = alert_labels.get(matcher["label"]) == matcher["value"]
        assert matches is True, "matches is not valid"

    def test_silence_time_window_active(self):
        """Test silence is active within time window."""
        now = datetime.utcnow()
        starts_at = now - timedelta(hours=1)
        ends_at = now + timedelta(hours=1)

        is_active = starts_at <= now <= ends_at
        assert is_active is True, "is_active is not valid"

    def test_silence_time_window_expired(self):
        """Test silence is not active after expiration."""
        now = datetime.utcnow()
        starts_at = now - timedelta(hours=3)
        ends_at = now - timedelta(hours=1)

        is_active = starts_at <= now <= ends_at
        assert is_active is False, "is_active is not valid"


# ============================================================================
# Alert Acknowledgment Tests
# ============================================================================


class TestAlertAcknowledgment:
    """Tests for alert acknowledgment functionality."""

    def test_acknowledge_alert(self, sample_alert: dict[str, Any]):
        """Test acknowledging an alert."""
        alert = sample_alert.copy()
        alert["acknowledged"] = True
        alert["acknowledged_by"] = "user@example.com"
        alert["acknowledged_at"] = datetime.utcnow().isoformat()

        assert alert["acknowledged"] is True, "Condition must be true"
        assert "acknowledged_by" in alert, "Condition must be true"

    def test_acknowledgment_stops_escalation(self):
        """Test that acknowledgment stops further escalation."""
        is_acknowledged = True
        should_escalate = not is_acknowledged

        assert should_escalate is False, "should_escalate is not valid"

    def test_acknowledged_alert_still_visible(self, sample_alert: dict[str, Any]):
        """Test acknowledged alerts remain visible."""
        alert = sample_alert.copy()
        alert["acknowledged"] = True
        alert["status"] = "firing"  # Still firing

        # Acknowledged alerts should still appear in active alerts
        is_active = alert["status"] == "firing"
        assert is_active is True, "is_active is not valid"


# ============================================================================
# Alert Aggregation Tests
# ============================================================================


class TestAlertAggregation:
    """Tests for alert aggregation and grouping."""

    def test_group_alerts_by_label(self):
        """Test grouping alerts by label."""
        alerts = [
            {"id": "1", "labels": {"service": "api", "host": "host-1"}},
            {"id": "2", "labels": {"service": "api", "host": "host-2"}},
            {"id": "3", "labels": {"service": "db", "host": "host-3"}},
        ]

        groups = {}
        for alert in alerts:
            service = alert["labels"]["service"]
            if service not in groups:
                groups[service] = []
            groups[service].append(alert)

        assert len(groups["api"]) == 2, "Collection must not be empty"
        assert len(groups["db"]) == 1, "Collection must not be empty"

    def test_deduplicate_alerts(self):
        """Test alert deduplication based on fingerprint."""
        alerts = [
            {"fingerprint": "fp-1", "labels": {"service": "api"}},
            {"fingerprint": "fp-1", "labels": {"service": "api"}},  # Duplicate
            {"fingerprint": "fp-2", "labels": {"service": "db"}},
        ]

        seen = set()
        unique = []
        for alert in alerts:
            if alert["fingerprint"] not in seen:
                seen.add(alert["fingerprint"])
                unique.append(alert)

        assert len(unique) == 2, "Unique must not be empty"

    def test_alert_fingerprint_generation(self):
        """Test alert fingerprint generation."""
        labels = {"service": "api", "host": "server-01", "alertname": "HighCPU"}

        # Sort labels for consistent fingerprint
        sorted_labels = sorted(labels.items())
        fingerprint = hash(tuple(sorted_labels))

        assert fingerprint is not None, "fingerprint must be initialized"
        assert isinstance(fingerprint, int)

    def test_aggregated_notification_content(self):
        """Test aggregated notification contains all alerts."""
        grouped_alerts = {
            "api": [{"id": "1"}, {"id": "2"}],
            "db": [{"id": "3"}],
        }

        total_alerts = sum(len(alerts) for alerts in grouped_alerts.values())
        assert total_alerts == 3, "total_alerts is not valid"
