"""Feedback event dataclass for the codex_ml feedback loop."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _utcnow_iso() -> str:
    """Return the current UTC time as an ISO 8601 string (with ``Z`` suffix)."""
    return datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class FeedbackEvent:
    """Represents a single feedback signal captured by the feedback loop.

    Attributes:
        event_type: Category of the event (e.g. ``"alert"``, ``"drift"``,
            ``"metric"``, ``"user"``).
        source: Identifier of the component that produced the event
            (e.g. ``"prometheus_alertmanager"``, ``"data_drift_detector"``).
        payload: Arbitrary key/value data accompanying the event.
        score: Optional numeric quality/severity score.  Higher values are
            typically worse (severity) or better (quality) depending on
            ``event_type``; callers should document the convention.
        timestamp: ISO 8601 UTC timestamp string.  Auto-populated on
            construction when not supplied.
    """

    event_type: str
    source: str
    payload: dict[str, Any] = field(default_factory=dict)
    score: float | None = None
    timestamp: str = field(default_factory=_utcnow_iso)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable dict representation."""
        return {
            "event_type": self.event_type,
            "source": self.source,
            "payload": self.payload,
            "score": self.score,
            "timestamp": self.timestamp,
        }
