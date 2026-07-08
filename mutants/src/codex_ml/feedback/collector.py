"""FeedbackCollector — in-memory store with optional JSONL file sink."""

from __future__ import annotations

import collections
import json
import threading
from pathlib import Path
from typing import Any

from codex_ml.feedback.events import FeedbackEvent


class FeedbackCollector:
    """Thread-safe collector for :class:`~codex_ml.feedback.events.FeedbackEvent` objects.

    Parameters
    ----------
    max_memory:
        Maximum number of events to retain in the in-memory ring-buffer.
        Oldest events are dropped when the buffer is full.
    sink_path:
        If supplied, every recorded event is also appended as a JSON line to
        this file (JSONL format).  The parent directory must already exist or
        the first ``record()`` call will raise ``FileNotFoundError``.
    """

    def __init__(
        self,
        max_memory: int = 10_000,
        sink_path: str | Path | None = None,
    ) -> None:
        self._max_memory = max_memory
        self._buffer: collections.deque[FeedbackEvent] = collections.deque(maxlen=max_memory)
        self._sink_path: Path | None = Path(sink_path) if sink_path else None
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def record(self, event: FeedbackEvent) -> None:
        """Store *event* in memory (and optionally to the JSONL sink).

        Parameters
        ----------
        event:
            The :class:`~codex_ml.feedback.events.FeedbackEvent` to persist.
        """
        with self._lock:
            self._buffer.append(event)
            if self._sink_path is not None:
                with self._sink_path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(event.to_dict()) + "\n")

    def get_recent(self, n: int = 100) -> list[FeedbackEvent]:
        """Return the *n* most recent events, newest last.

        Parameters
        ----------
        n:
            Maximum number of events to return.  If fewer than *n* events have
            been recorded, all events are returned.
        """
        with self._lock:
            events = list(self._buffer)
        return events[-n:] if n < len(events) else events

    def aggregate(self) -> dict[str, Any]:
        """Compute summary statistics over all buffered events.

        Returns
        -------
        dict
            ``counts_by_type``
                Mapping of ``event_type`` → number of occurrences.
            ``avg_score``
                Mean of all non-``None`` ``score`` fields, or ``None`` when no
                scored events have been recorded.
            ``total``
                Total number of events currently in the buffer.
        """
        with self._lock:
            events = list(self._buffer)

        counts: dict[str, int] = {}
        scores: list[float] = []
        for ev in events:
            counts[ev.event_type] = counts.get(ev.event_type, 0) + 1
            if ev.score is not None:
                scores.append(ev.score)

        avg_score: float | None = sum(scores) / len(scores) if scores else None
        return {
            "counts_by_type": counts,
            "avg_score": avg_score,
            "total": len(events),
        }

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        with self._lock:
            return len(self._buffer)

    def __repr__(self) -> str:  # pragma: no cover
        return f"FeedbackCollector(size={len(self)}, max_memory={self._max_memory})"
