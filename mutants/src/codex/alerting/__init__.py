"""Training alerting package.

Provides a lightweight, zero-external-dependency alerting system for the
Codex training pipeline.

Key exports:

* :class:`TrainingAlertManager` — fan-out dispatcher; create via
  :meth:`~TrainingAlertManager.from_env` for zero-config usage.
* :class:`AlertChannel` — abstract base class for custom channels.
* :class:`AlertSeverity` — ``INFO | WARNING | ERROR | CRITICAL``.
* :class:`AlertEvent` — immutable event payload sent through channels.

Bundled channels:

* :class:`~codex.alerting.slack.SlackChannel` — Slack incoming webhook.
* :class:`~codex.alerting.email.EmailChannel` — SMTP email.

Example::

    from codex.alerting import TrainingAlertManager

    manager = TrainingAlertManager.from_env()
    try:
        run_training(...)
        manager.alert_training_complete(run_id="run-42", epochs=10, final_loss=0.15)
    except (ImportError, AttributeError) as exc:
        manager.alert_training_failure(exc, run_id="run-42", epoch=7)
        raise
"""

from codex.alerting.base import AlertChannel, AlertEvent, AlertSeverity
from codex.alerting.manager import TrainingAlertManager

__all__ = [
    "AlertChannel",
    "AlertEvent",
    "AlertSeverity",
    "TrainingAlertManager",
]
