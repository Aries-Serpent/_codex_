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
import urllib.parse
import urllib.request
from typing import Any

from codex.alerting.base import AlertChannel, AlertEvent, AlertSeverity
from codex.resilience.retry import RetryExhausted, retry_with_backoff

logger = logging.getLogger(__name__)

# Slack attachment colour codes
_COLOUR_MAP: dict[AlertSeverity, str] = {
    AlertSeverity.INFO: "#36a64f",  # green
    AlertSeverity.WARNING: "#ffcc00",  # yellow
    AlertSeverity.ERROR: "#e01e5a",  # red
    AlertSeverity.CRITICAL: "#c0392b",  # dark red
}

_ENV_WEBHOOK = "CODEX_SLACK_WEBHOOK_URL"
_TIMEOUT = 10  # seconds
_ALLOWED_WEBHOOK_HOSTS = {"hooks.slack.com", "hooks.slack-gov.com"}
_ALLOWED_WEBHOOK_PATH_PREFIXES = ("/services/",)

# Retry configuration for webhook POSTs: up to 3 extra attempts with
# exponential backoff (1 s → 2 s → 4 s), capped at 30 s, retrying only
# on network / URL errors that are considered transient.
_retry_send = retry_with_backoff(
    max_retries=3,
    base_delay=1.0,
    max_delay=30.0,
    jitter=0.25,
    exceptions=(urllib.error.URLError,),
)


def _validated_webhook_url(raw_url: str) -> str:
    """Return a Slack webhook URL only when it matches the approved HTTPS hosts."""
    parsed = urllib.parse.urlparse(raw_url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("SlackChannel: webhook URL must use https and include a host")
    if parsed.username or parsed.password:
        raise ValueError("SlackChannel: webhook URL must not embed credentials")
    hostname = (parsed.hostname or "").lower()
    if hostname not in _ALLOWED_WEBHOOK_HOSTS:
        raise ValueError(
            f"SlackChannel: webhook URL host must be one of {sorted(_ALLOWED_WEBHOOK_HOSTS)!r}"
        )
    if parsed.params or parsed.query or parsed.fragment:
        raise ValueError(
            "SlackChannel: webhook URL must not include params, query strings, or fragments"
        )
    if not parsed.path.startswith(_ALLOWED_WEBHOOK_PATH_PREFIXES):
        raise ValueError(
            "SlackChannel: webhook URL path must start with one of "
            f"{_ALLOWED_WEBHOOK_PATH_PREFIXES!r}"
        )
    return urllib.parse.urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            "",
            "",
            "",
        )
    )


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

        The HTTP POST is wrapped with exponential backoff retry (up to 3
        extra attempts) for transient ``URLError`` failures.  Non-transient
        errors (e.g. ``ValueError`` from a malformed URL) are NOT retried and
        are caught as warnings.

        Returns:
            ``True`` on HTTP 200, ``False`` otherwise (logs a warning).
        """
        if not self._webhook_url:
            logger.warning(
                "SlackChannel: no webhook URL configured (set %s or pass webhook_url=...)",
                _ENV_WEBHOOK,
            )
            return False

        try:
            payload = self._build_payload(event)
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                _validated_webhook_url(self._webhook_url),
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            def _do_post() -> bool:
                with urllib.request.urlopen(  # nosec B310  # nosemgrep: semgrep.urllib-urlopen-dynamic -- webhook URL is allowlisted by _validated_webhook_url()
                    req, timeout=_TIMEOUT
                ) as resp:
                    status = resp.getcode()
                    if status != 200:
                        logger.warning("SlackChannel: unexpected HTTP %s from webhook", status)
                        return False
                return True

            return _retry_send(_do_post)()
        except RetryExhausted as exc:
            logger.warning("SlackChannel: all retry attempts exhausted — %s", exc.__cause__)
            return False
        except (ValueError, TypeError, RuntimeError) as exc:  # pragma: no cover — unexpected errors
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
            fields.append({"title": "Epoch", "value": str(event.epoch), "short": True})
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
