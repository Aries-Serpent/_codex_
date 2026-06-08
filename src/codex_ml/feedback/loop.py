"""FeedbackLoop — high-level integration layer that ingests monitoring signals."""

from __future__ import annotations

from typing import Any

from codex_ml.feedback.collector import FeedbackCollector
from codex_ml.feedback.events import FeedbackEvent


class FeedbackLoop:
    """High-level feedback loop that bridges monitoring signals to the collector.

    The loop ingests alerts from the alerting stack and drift signals from the
    drift-detection subsystem, then exposes a single :meth:`should_adapt`
    decision predicate that downstream orchestrators (e.g. the OODA loop or
    the continuous-learning scheduler) can poll.

    Parameters
    ----------
    collector:
        Optionally supply a pre-configured :class:`~codex_ml.feedback.collector.FeedbackCollector`.
        If omitted, a default in-memory collector is created automatically.
    adapt_threshold:
        Number of ``"alert"`` events that must appear in the last
        *adapt_window* events to trigger :meth:`should_adapt`.  Default: 3.
    adapt_window:
        How many of the most recent events to inspect when evaluating
        :meth:`should_adapt`.  Default: 10.
    """

    def __init__(
        self,
        collector: FeedbackCollector | None = None,
        adapt_threshold: int = 3,
        adapt_window: int = 10,
    ) -> None:
        self._collector = collector or FeedbackCollector()
        self._adapt_threshold = adapt_threshold
        self._adapt_window = adapt_window

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def collector(self) -> FeedbackCollector:
        """The underlying :class:`~codex_ml.feedback.collector.FeedbackCollector`."""
        return self._collector

    # ------------------------------------------------------------------
    # Ingestion helpers
    # ------------------------------------------------------------------

    def on_alert(self, alert_event: Any) -> None:
        """Ingest a monitoring alert as a feedback event.

        Parameters
        ----------
        alert_event:
            Either a :class:`~codex_ml.feedback.events.FeedbackEvent` (passed
            through unchanged) or an arbitrary dict/object whose string
            representation is stored in the payload.  If the object exposes a
            ``severity`` attribute or key it is mapped to ``score``
            (``"critical"``→1.0, ``"warning"``→0.5, anything else→0.0).
        """
        if isinstance(alert_event, FeedbackEvent):
            self._collector.record(alert_event)
            return

        payload: dict[str, Any]
        if isinstance(alert_event, dict):
            payload = dict(alert_event)
        else:
            payload = {"raw": str(alert_event)}

        severity_str: str = str(
            payload.get("severity", getattr(alert_event, "severity", ""))
        ).lower()
        score = {"critical": 1.0, "warning": 0.5}.get(severity_str, 0.0)

        self._collector.record(
            FeedbackEvent(
                event_type="alert",
                source=str(payload.get("source", getattr(alert_event, "source", "alerting"))),
                payload=payload,
                score=score,
            )
        )

    def on_drift(self, drift_result: Any) -> None:
        """Ingest a drift-detection result as a feedback event.

        Parameters
        ----------
        drift_result:
            Either a :class:`~codex_ml.feedback.events.FeedbackEvent` (passed
            through unchanged) or a dict/object.  If the object exposes a
            ``drift_score`` attribute or key, it is used as the event score.
        """
        if isinstance(drift_result, FeedbackEvent):
            self._collector.record(drift_result)
            return

        payload: dict[str, Any]
        if isinstance(drift_result, dict):
            payload = dict(drift_result)
        else:
            payload = {"raw": str(drift_result)}

        score_val = payload.get("drift_score", getattr(drift_result, "drift_score", None))
        score: float | None = float(score_val) if score_val is not None else None

        self._collector.record(
            FeedbackEvent(
                event_type="drift",
                source=str(
                    payload.get("source", getattr(drift_result, "source", "drift_detector"))
                ),
                payload=payload,
                score=score,
            )
        )

    # ------------------------------------------------------------------
    # Decision predicate
    # ------------------------------------------------------------------

    def should_adapt(self) -> bool:
        """Return ``True`` if recent feedback indicates adaptation is needed.

        The heuristic counts ``"alert"`` events in the last
        :attr:`_adapt_window` events.  If the count exceeds
        :attr:`_adapt_threshold` the method returns ``True``.

        Returns
        -------
        bool
            ``True`` when adaptation is recommended.
        """
        recent = self._collector.get_recent(self._adapt_window)
        alert_count = sum(1 for ev in recent if ev.event_type == "alert")
        return alert_count > self._adapt_threshold
