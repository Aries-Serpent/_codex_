"""Training alert manager.

The :class:`TrainingAlertManager` orchestrates delivery of alert events across
one or more :class:`~codex.alerting.base.AlertChannel` implementations.

Typical usage::

    manager = TrainingAlertManager.from_env()

    # On training failure:
    manager.alert_training_failure(exc, run_id="run-abc", epoch=5)

    # On training completion:
    manager.alert_training_complete(run_id="run-abc", epochs=10, final_loss=0.23)
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any

from codex.alerting.base import AlertChannel, AlertEvent, AlertSeverity

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class TrainingAlertManager:
    """Fan-out alert dispatcher for the training pipeline.

    Args:
        channels: List of :class:`~codex.alerting.base.AlertChannel` instances
            to deliver alerts through.
        min_severity: Events below this severity are silently discarded.
            Defaults to :attr:`~codex.alerting.base.AlertSeverity.ERROR`.
    """

    def __init__(
        self,
        channels: list[AlertChannel],
        min_severity: AlertSeverity = AlertSeverity.ERROR,
    ) -> None:
        self._channels = list(channels)
        self._min_severity = min_severity

    # ------------------------------------------------------------------
    @classmethod
    def from_env(cls) -> "TrainingAlertManager":
        """Auto-configure a :class:`TrainingAlertManager` from environment vars.

        Channels are added only when their required env vars are present:

        * **Slack** — ``CODEX_SLACK_WEBHOOK_URL``
        * **Email** — ``CODEX_ALERT_SMTP_HOST`` + ``CODEX_ALERT_TO``

        The minimum severity can be overridden via
        ``CODEX_ALERT_MIN_SEVERITY`` (one of ``info``, ``warning``, ``error``,
        ``critical``; default ``error``).
        """
        channels: list[AlertChannel] = []

        # Slack
        slack_url = os.environ.get("CODEX_SLACK_WEBHOOK_URL", "")
        if slack_url:
            from codex.alerting.slack import SlackChannel

            channels.append(SlackChannel(webhook_url=slack_url))
            logger.debug("TrainingAlertManager: Slack channel enabled")

        # Email
        smtp_host = os.environ.get("CODEX_ALERT_SMTP_HOST", "")
        alert_to = os.environ.get("CODEX_ALERT_TO", "")
        if smtp_host and alert_to:
            from codex.alerting.email import EmailChannel

            channels.append(EmailChannel.from_env())
            logger.debug("TrainingAlertManager: Email channel enabled")

        # Min severity
        raw_sev = os.environ.get("CODEX_ALERT_MIN_SEVERITY", "error").lower().strip()
        try:
            min_severity = AlertSeverity(raw_sev)
        except ValueError:
            logger.warning(
                "TrainingAlertManager: unknown CODEX_ALERT_MIN_SEVERITY=%r; defaulting to 'error'",
                raw_sev,
            )
            min_severity = AlertSeverity.ERROR

        return cls(channels=channels, min_severity=min_severity)

    # ------------------------------------------------------------------
    def alert(self, event: AlertEvent) -> dict[str, bool]:
        """Dispatch *event* to all registered channels (if severity qualifies).

        The event's ``timestamp`` field is auto-filled when empty before
        delivery.

        Returns:
            A mapping ``{channel_name: success_bool}`` for every channel that
            was attempted.  Channels skipped due to minimum-severity filtering
            are not included.
        """
        if event.severity < self._min_severity:
            logger.debug(
                "TrainingAlertManager: dropping %r event (below min_severity=%r)",
                event.severity.value,
                self._min_severity.value,
            )
            return {}

        event.fill_timestamp()
        results: dict[str, bool] = {}
        for channel in self._channels:
            try:
                ok = channel.send(event)
            except (ValueError, TypeError, RuntimeError) as exc:  # pragma: no cover — defensive
                logger.warning(
                    "TrainingAlertManager: channel %r raised unexpectedly — %s",
                    channel.name(),
                    exc,
                )
                ok = False
            results[channel.name()] = ok
        return results

    # ------------------------------------------------------------------
    def alert_training_failure(
        self,
        error: Exception,
        run_id: str = "",
        epoch: int = 0,
        **metadata: Any,
    ) -> dict[str, bool]:
        """Send a *CRITICAL* alert for an unhandled training exception.

        Args:
            error: The exception that caused the training to fail.
            run_id: Identifier for the training run.
            epoch: Epoch at which the failure occurred (0 = unknown).
            **metadata: Arbitrary key/value context attached to the event.

        Returns:
            ``{channel_name: success}`` mapping (see :meth:`alert`).
        """
        event = AlertEvent(
            title="Training run failed",
            message=f"{type(error).__name__}: {error}",
            severity=AlertSeverity.CRITICAL,
            run_id=run_id,
            epoch=epoch,
            metadata=dict(metadata),
        )
        return self.alert(event)

    # ------------------------------------------------------------------
    def alert_training_complete(
        self,
        run_id: str = "",
        epochs: int = 0,
        final_loss: float = 0.0,
        **metadata: Any,
    ) -> dict[str, bool]:
        """Send an *INFO* alert when training completes successfully.

        Args:
            run_id: Identifier for the training run.
            epochs: Total number of epochs completed.
            final_loss: Loss value at the final epoch.
            **metadata: Arbitrary key/value context attached to the event.

        Returns:
            ``{channel_name: success}`` mapping (see :meth:`alert`).
        """
        event = AlertEvent(
            title="Training run completed",
            message=(
                f"Training finished successfully — epochs={epochs}, final_loss={final_loss:.6f}"
            ),
            severity=AlertSeverity.INFO,
            run_id=run_id,
            epoch=epochs,
            metadata=dict(metadata),
        )
        return self.alert(event)
