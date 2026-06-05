"""Slack webhook alert channel.

Sends alert events to a Slack incoming-webhook URL using only the standard
library (``urllib.request``).  No external dependencies are introduced.

Environment variables:
    CODEX_SLACK_WEBHOOK_URL: Webhook URL used when none is passed to the
        constructor.

Example::

    channel = SlackChannel()  # reads CODEX_SLACK_WEBHOOK_URL
    channel.send(AlertEvent(title="Training failed", message="...",
                            severity=AlertSeverity.CRITICAL))
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from typing import Any

from codex.alerting.base import AlertChannel, AlertEvent, AlertSeverity

logger = logging.getLogger(__name__)

# Slack attachment colour codes
_COLOUR_MAP: dict[AlertSeverity, str] = {
    AlertSeverity.INFO: "#36a64f",      # green
    AlertSeverity.WARNING: "#ffcc00",   # yellow
    AlertSeverity.ERROR: "#e01e5a",     # red
    AlertSeverity.CRITICAL: "#c0392b",  # dark red
}

_ENV_WEBHOOK = "CODEX_SLACK_WEBHOOK_URL"
_TIMEOUT = 10  # seconds


class SlackChannel(AlertChannel):
    """Deliver alerts to a Slack channel via an incoming webhook.

    Args:
        webhook_url: Full Slack webhook URL.  When *None* or empty the value
            of the ``CODEX_SLACK_WEBHOOK_URL`` environment variable is used.
    """

    def __init__(self, webhook_url: str | None = None) -> None:
        self._webhook_url: str = webhook_url or os.environ.get(_ENV_WEBHOOK, "")

    # ------------------------------------------------------------------
    def name(self) -> str:
        return "slack"

    # ------------------------------------------------------------------
    def send(self, event: AlertEvent) -> bool:
        """POST *event* to the configured Slack webhook.

        Returns:
            ``True`` on HTTP 200, ``False`` otherwise (logs a warning).
        """
        if not self._webhook_url:
            logger.warning(
                "SlackChannel: no webhook URL configured "
                "(set %s or pass webhook_url=...)",
                _ENV_WEBHOOK,
            )
            return False

        payload = self._build_payload(event)
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self._webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
                status = resp.getcode()
                if status != 200:
                    logger.warning(
                        "SlackChannel: unexpected HTTP %s from webhook", status
                    )
                    return False
            return True
        except urllib.error.URLError as exc:
            logger.warning("SlackChannel: failed to send alert — %s", exc)
            return False
        except Exception as exc:  # pragma: no cover — unexpected errors
            logger.warning("SlackChannel: unexpected error — %s", exc)
            return False

    # ------------------------------------------------------------------
    def _build_payload(self, event: AlertEvent) -> dict[str, Any]:
        colour = _COLOUR_MAP.get(event.severity, "#36a64f")
        fields: list[dict[str, Any]] = [
            {"title": "Severity", "value": event.severity.value, "short": True},
            {"title": "Timestamp", "value": event.timestamp or "—", "short": True},
        ]
        if event.run_id:
            fields.append({"title": "Run ID", "value": event.run_id, "short": True})
        if event.epoch:
            fields.append(
                {"title": "Epoch", "value": str(event.epoch), "short": True}
            )
        for key, value in event.metadata.items():
            fields.append({"title": key, "value": str(value), "short": True})

        return {
            "text": f"*{event.title}*",
            "attachments": [
                {
                    "color": colour,
                    "text": event.message,
                    "fields": fields,
                    "mrkdwn_in": ["text"],
                }
            ],
        }
