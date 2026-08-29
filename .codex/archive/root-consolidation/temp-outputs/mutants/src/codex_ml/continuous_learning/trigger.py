"""Retraining trigger descriptor for the continuous learning pipeline.

A ``RetrainingTrigger`` is created whenever drift scores exceed configured
thresholds.  It is a plain dataclass — fully serialisable, no external
dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

__all__ = ["RetrainingTrigger"]


@dataclass
class RetrainingTrigger:
    """Descriptor produced when the pipeline decides retraining is needed.

    Attributes:
        reason: Human-readable explanation of why retraining was triggered
            (e.g. ``"data_drift_psi"`` or ``"model_drift_js"``).
        drift_score: The drift score that exceeded the threshold.
        timestamp: UTC datetime at which the trigger was created.
        config_snapshot: Snapshot of the pipeline configuration at trigger
            time (arbitrary key-value pairs).
    """

    reason: str
    drift_score: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    config_snapshot: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialise the trigger to a plain dictionary."""
        return {
            "reason": self.reason,
            "drift_score": self.drift_score,
            "timestamp": self.timestamp.isoformat(),
            "config_snapshot": dict(self.config_snapshot),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RetrainingTrigger":
        """Deserialise a trigger from a dictionary produced by :meth:`to_dict`."""
        ts_raw = data.get("timestamp")
        ts = datetime.fromisoformat(ts_raw) if ts_raw else datetime.now(UTC)
        return cls(
            reason=data["reason"],
            drift_score=float(data["drift_score"]),
            timestamp=ts,
            config_snapshot=dict(data.get("config_snapshot", {})),
        )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"RetrainingTrigger(reason={self.reason!r}, "
            f"drift_score={self.drift_score:.4f}, "
            f"timestamp={self.timestamp.isoformat()!r})"
        )
