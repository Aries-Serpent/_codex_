"""Tests for webhooks (v1.5.4)."""

from __future__ import annotations

import json
import time
from unittest.mock import MagicMock, patch

import pytest


def test_audit_event_dataclass():
    """Test AuditEvent dataclass."""
    from dataclasses import asdict

    from scripts.space_traversal.webhooks import AuditEvent

    event = AuditEvent(
        event_type="audit_complete",
        repo_name="test-repo",
        timestamp=1234567890.0,
        avg_score=0.85,
        capability_count=18,
        regression_count=2,
        details={"high_count": 15, "low_count": 1},
    )

    data = asdict(event)
    assert data["event_type"] == "audit_complete", "Data must not be empty"
    assert data["repo_name"] == "test-repo", "Data must not be empty"
    assert data["avg_score"] == 0.85, "Data must not be empty"


def test_webhook_delivery_dataclass():
    """Test WebhookDelivery dataclass."""
    from scripts.space_traversal.webhooks import WebhookDelivery

    delivery = WebhookDelivery(
        url="https://example.com/webhook",
        event_type="audit_complete",
        status_code=200,
        success=True,
        error_message=None,
        timestamp=time.time(),
    )

    assert delivery.success is True, "success is not valid"
    assert delivery.status_code == 200, "status_code is not valid"


@patch("scripts.space_traversal.webhooks.urlopen")
def test_send_webhook_success(mock_urlopen):
    """Test successful webhook delivery."""
    from scripts.space_traversal.webhooks import AuditEvent, send_webhook

    # Mock successful response
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=False)
    mock_urlopen.return_value = mock_response

    event = AuditEvent(
        event_type="audit_complete",
        repo_name="test-repo",
        timestamp=time.time(),
        avg_score=0.85,
        capability_count=18,
        regression_count=0,
        details={},
    )

    result = send_webhook("https://example.com/webhook", event)

    assert result.success is True, "Result must not be empty"
    assert result.status_code == 200, "Result must not be empty"
    assert mock_urlopen.called, "Condition must be true"


@patch("scripts.space_traversal.webhooks.urlopen")
def test_send_webhook_with_secret(mock_urlopen):
    """Test webhook with HMAC signing."""
    from scripts.space_traversal.webhooks import AuditEvent, send_webhook

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=False)
    mock_urlopen.return_value = mock_response

    event = AuditEvent(
        event_type="audit_complete",
        repo_name="test-repo",
        timestamp=time.time(),
        avg_score=0.85,
        capability_count=18,
        regression_count=0,
        details={},
    )

    send_webhook("https://example.com/webhook", event, secret="test-secret")

    # Verify request was made with signature header
    call_args = mock_urlopen.call_args
    request = call_args[0][0]
    # Headers are stored with title case but accessed case-insensitively
    headers_lower = {k.lower(): v for k, v in request.headers.items()}
    assert "x-audit-signature" in headers_lower, "Condition must be true"


@patch("scripts.space_traversal.webhooks.urlopen")
def test_send_slack_notification(mock_urlopen):
    """Test Slack notification format."""
    from scripts.space_traversal.webhooks import AuditEvent, send_slack_notification

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=False)
    mock_urlopen.return_value = mock_response

    event = AuditEvent(
        event_type="audit_complete",
        repo_name="test-repo",
        timestamp=time.time(),
        avg_score=0.85,
        capability_count=18,
        regression_count=0,
        details={},
    )

    result = send_slack_notification("https://hooks.slack.com/test", event)

    assert result.success is True, "Result must not be empty"

    # Verify Slack payload format
    call_args = mock_urlopen.call_args
    request = call_args[0][0]
    payload = json.loads(request.data.decode())
    assert "attachments" in payload, "Condition must be true"
    assert payload["attachments"][0]["color"] == "good", "Condition must be true"


@patch("scripts.space_traversal.webhooks.urlopen")
def test_send_slack_notification_with_regressions(mock_urlopen):
    """Test Slack notification with regressions."""
    from scripts.space_traversal.webhooks import AuditEvent, send_slack_notification

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=False)
    mock_urlopen.return_value = mock_response

    event = AuditEvent(
        event_type="regression_detected",
        repo_name="test-repo",
        timestamp=time.time(),
        avg_score=0.75,
        capability_count=18,
        regression_count=3,
        details={},
    )

    result = send_slack_notification("https://hooks.slack.com/test", event)

    assert result.success is True, "Result must not be empty"
    call_args = mock_urlopen.call_args
    request = call_args[0][0]
    payload = json.loads(request.data.decode())
    assert payload["attachments"][0]["color"] == "warning", "Condition must be true"


@patch("scripts.space_traversal.webhooks.urlopen")
def test_send_teams_notification(mock_urlopen):
    """Test Teams notification format."""
    from scripts.space_traversal.webhooks import AuditEvent, send_teams_notification

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=False)
    mock_urlopen.return_value = mock_response

    event = AuditEvent(
        event_type="audit_complete",
        repo_name="test-repo",
        timestamp=time.time(),
        avg_score=0.85,
        capability_count=18,
        regression_count=0,
        details={},
    )

    result = send_teams_notification("https://teams.webhook.com/test", event)

    assert result.success is True, "Result must not be empty"

    call_args = mock_urlopen.call_args
    request = call_args[0][0]
    payload = json.loads(request.data.decode())
    assert payload["@type"] == "MessageCard", "Condition must be true"
    assert "Audit Complete" in payload["sections"][0]["activityTitle"], "Condition must be true"


def test_create_event_from_audit():
    """Test creating event from audit results."""
    from scripts.space_traversal.webhooks import create_event_from_audit

    capabilities = [
        {"id": "cap1", "score": 0.90},
        {"id": "cap2", "score": 0.85},  # At threshold for high
        {"id": "cap3", "score": 0.60},
    ]
    regressions = [
        {"capability_id": "cap3", "delta": -0.1},
    ]

    event = create_event_from_audit(
        capabilities=capabilities,
        regressions=regressions,
        repo_name="test-repo",
        event_type="audit_complete",
    )

    assert event.repo_name == "test-repo", "repo_name is not valid"
    assert event.capability_count == 3, "Count must be greater than zero"
    assert event.regression_count == 1, "Count must be greater than zero"
    assert event.avg_score == pytest.approx((0.90 + 0.85 + 0.60) / 3), "avg_score is not valid"
    assert event.details["high_count"] == 2, "Count must be greater than zero"
    assert event.details["low_count"] == 1, "Count must be greater than zero"
