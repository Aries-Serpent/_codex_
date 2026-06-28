"""Base classes for the training alerting system.

Defines the AlertSeverity enum, AlertEvent dataclass and the abstract
AlertChannel protocol that concrete notifier implementations must satisfy.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class AlertSeverity(StrEnum):
    """Severity levels for alert events, ordered from least to most severe."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

    def __le__(self, other: "AlertSeverity") -> bool:  # type: ignore[override]
        _order = list(AlertSeverity)
        return _order.index(self) <= _order.index(other)

    def __lt__(self, other: "AlertSeverity") -> bool:  # type: ignore[override]
        _order = list(AlertSeverity)
        return _order.index(self) < _order.index(other)

    def __ge__(self, other: "AlertSeverity") -> bool:  # type: ignore[override]
        _order = list(AlertSeverity)
        return _order.index(self) >= _order.index(other)

    def __gt__(self, other: "AlertSeverity") -> bool:  # type: ignore[override]
        _order = list(AlertSeverity)
        return _order.index(self) > _order.index(other)


@dataclass
class AlertEvent:
    """Represents a single alert event emitted by the training pipeline.

    Args:
        title: Short summary of the event (used as subject/headline).
        message: Detailed human-readable description of the event.
        severity: How severe the event is.
        run_id: Identifier for the training run that produced this event.
        epoch: Training epoch at which the event occurred (0 = not applicable).
        metadata: Arbitrary key/value pairs attached to the event.
        timestamp: ISO-8601 UTC string; auto-filled by the manager when empty.
    """

    title: str
    message: str
    severity: AlertSeverity
    run_id: str = ""
    epoch: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""

    def fill_timestamp(self) -> None:
        """Set *timestamp* to the current UTC time if it is not already set."""
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class AlertChannel(ABC):
    """Abstract base class for alert delivery channels.

    Concrete implementations (e.g. :class:`~codex.alerting.slack.SlackChannel`,
    :class:`~codex.alerting.email.EmailChannel`) must override both
    :meth:`send` and :meth:`name`.
    """

    @abstractmethod
    def send(self, event: AlertEvent) -> bool:
        """Deliver *event* through this channel.

        Returns:
            ``True`` on success, ``False`` on failure.  Implementations must
            **not** raise — they should log a warning and return ``False``.
        """

    @abstractmethod
    def name(self) -> str:
        """Return a stable, human-readable identifier for this channel."""
