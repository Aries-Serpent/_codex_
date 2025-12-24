#!/usr/bin/env python3
"""
Webhook notifications for audit events.

Provides webhook delivery for audit pipeline events.

Features:
- Generic webhook delivery with HMAC signing
- Slack-formatted notifications
- Delivery retry with exponential backoff
- Event type support (audit_complete, regression_detected, etc.)

Example:
    from scripts.space_traversal.webhooks import send_webhook, AuditEvent

    event = AuditEvent(
        event_type="audit_complete",
        repo_name="my-repo",
        timestamp=time.time(),
        avg_score=0.85,
        capability_count=18,
        regression_count=0,
        details={}
    )
    success = send_webhook("https://hooks.example.com/audit", event)
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from dataclasses import asdict, dataclass
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

__all__ = [
    "AuditEvent",
    "send_webhook",
    "send_slack_notification",
    "send_teams_notification",
    "WebhookDelivery",
]

logger = logging.getLogger(__name__)


@dataclass
class AuditEvent:
    """Audit event for webhook delivery."""

    event_type: str  # "audit_complete", "regression_detected", "threshold_crossed"
    repo_name: str
    timestamp: float
    avg_score: float
    capability_count: int
    regression_count: int
    details: dict[str, Any]


@dataclass
class WebhookDelivery:
    """Record of webhook delivery attempt."""

    url: str
    event_type: str
    status_code: Optional[int]
    success: bool
    error_message: Optional[str]
    timestamp: float


def send_webhook(
    url: str,
    event: AuditEvent,
    secret: Optional[str] = None,
    timeout: int = 10,
    max_retries: int = 3,
) -> WebhookDelivery:
    """
    Send webhook notification.

    Args:
        url: Webhook endpoint URL
        event: AuditEvent to send
        secret: Optional HMAC secret for signing
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts

    Returns:
        WebhookDelivery record
    """
    payload = json.dumps(asdict(event)).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "AuditPipeline/1.5.4",
        "X-Audit-Event": event.event_type,
    }

    if secret:
        signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        headers["X-Audit-Signature"] = f"sha256={signature}"

    for attempt in range(max_retries):
        try:
            req = Request(url, data=payload, headers=headers, method="POST")
            with urlopen(req, timeout=timeout) as resp:
                return WebhookDelivery(
                    url=url,
                    event_type=event.event_type,
                    status_code=resp.status,
                    success=resp.status in (200, 201, 202, 204),
                    error_message=None,
                    timestamp=time.time(),
                )
        except HTTPError as e:
            logger.debug(f"HTTPError: {e}")
            logger.warning(f"Webhook HTTP error (attempt {attempt + 1}): {e.code}")
            if attempt == max_retries - 1:
                return WebhookDelivery(
                    url=url,
                    event_type=event.event_type,
                    status_code=e.code,
                    success=False,
                    error_message=str(e),
                    timestamp=time.time(),
                )
        except URLError as e:
            logger.debug(f"URLError: {e}")
            logger.warning(f"Webhook URL error (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                return WebhookDelivery(
                    url=url,
                    event_type=event.event_type,
                    status_code=None,
                    success=False,
                    error_message=str(e),
                    timestamp=time.time(),
                )
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.warning(f"Webhook error (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                return WebhookDelivery(
                    url=url,
                    event_type=event.event_type,
                    status_code=None,
                    success=False,
                    error_message=str(e),
                    timestamp=time.time(),
                )

        # Exponential backoff
        time.sleep(2**attempt)

    # Should not reach here, but return failure just in case
    return WebhookDelivery(
        url=url,
        event_type=event.event_type,
        status_code=None,
        success=False,
        error_message="Max retries exceeded",
        timestamp=time.time(),
    )


def send_slack_notification(
    webhook_url: str,
    event: AuditEvent,
    channel: Optional[str] = None,
) -> WebhookDelivery:
    """
    Send Slack-formatted notification.

    Args:
        webhook_url: Slack webhook URL
        event: AuditEvent to send
        channel: Optional channel override

    Returns:
        WebhookDelivery record
    """
    emoji = "✅" if event.regression_count == 0 else "⚠️"
    color = "good" if event.regression_count == 0 else "warning"

    if event.avg_score < 0.70:
        color = "danger"
        emoji = "🔴"

    payload: dict[str, Any] = {
        "attachments": [
            {
                "color": color,
                "title": f"{emoji} Audit Complete: {event.repo_name}",
                "fields": [
                    {
                        "title": "Average Score",
                        "value": f"{event.avg_score:.3f}",
                        "short": True,
                    },
                    {
                        "title": "Capabilities",
                        "value": str(event.capability_count),
                        "short": True,
                    },
                    {
                        "title": "Regressions",
                        "value": str(event.regression_count),
                        "short": True,
                    },
                    {"title": "Event", "value": event.event_type, "short": True},
                ],
                "footer": "Audit Pipeline v1.5.4",
                "ts": int(event.timestamp),
            }
        ]
    }

    if channel:
        payload["channel"] = channel

    try:
        req = Request(
            webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(req, timeout=10) as resp:
            return WebhookDelivery(
                url=webhook_url,
                event_type=event.event_type,
                status_code=resp.status,
                success=resp.status == 200,
                error_message=None,
                timestamp=time.time(),
            )
    except (URLError, HTTPError) as e:
        logger.debug(f"Exception: {e}")
        logger.warning(f"Slack notification failed: {e}")
        return WebhookDelivery(
            url=webhook_url,
            event_type=event.event_type,
            status_code=getattr(e, "code", None),
            success=False,
            error_message=str(e),
            timestamp=time.time(),
        )


def send_teams_notification(
    webhook_url: str,
    event: AuditEvent,
) -> WebhookDelivery:
    """
    Send Microsoft Teams notification.

    Args:
        webhook_url: Teams webhook URL
        event: AuditEvent to send

    Returns:
        WebhookDelivery record
    """
    color = "00FF00" if event.regression_count == 0 else "FFA500"
    if event.avg_score < 0.70:
        color = "FF0000"

    payload = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": color,
        "summary": f"Audit Complete: {event.repo_name}",
        "sections": [
            {
                "activityTitle": f"🔍 Audit Complete: {event.repo_name}",
                "facts": [
                    {"name": "Average Score", "value": f"{event.avg_score:.3f}"},
                    {"name": "Capabilities", "value": str(event.capability_count)},
                    {"name": "Regressions", "value": str(event.regression_count)},
                    {"name": "Event Type", "value": event.event_type},
                ],
                "markdown": True,
            }
        ],
    }

    try:
        req = Request(
            webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(req, timeout=10) as resp:
            return WebhookDelivery(
                url=webhook_url,
                event_type=event.event_type,
                status_code=resp.status,
                success=resp.status == 200,
                error_message=None,
                timestamp=time.time(),
            )
    except (URLError, HTTPError) as e:
        logger.debug(f"Exception: {e}")
        logger.warning(f"Teams notification failed: {e}")
        return WebhookDelivery(
            url=webhook_url,
            event_type=event.event_type,
            status_code=getattr(e, "code", None),
            success=False,
            error_message=str(e),
            timestamp=time.time(),
        )


def create_event_from_audit(
    capabilities: list[dict],
    regressions: list[dict],
    repo_name: str,
    event_type: str = "audit_complete",
) -> AuditEvent:
    """
    Create AuditEvent from audit results.

    Args:
        capabilities: List of capability dictionaries
        regressions: List of regression dictionaries
        repo_name: Repository name
        event_type: Type of event

    Returns:
        AuditEvent instance
    """
    scores = [c.get("score", 0) for c in capabilities]
    avg_score = sum(scores) / len(scores) if scores else 0

    return AuditEvent(
        event_type=event_type,
        repo_name=repo_name,
        timestamp=time.time(),
        avg_score=avg_score,
        capability_count=len(capabilities),
        regression_count=len(regressions),
        details={
            "high_count": sum(1 for s in scores if s >= 0.85),
            "low_count": sum(1 for s in scores if s < 0.70),
            "regression_ids": [r.get("capability_id") for r in regressions],
        },
    )
