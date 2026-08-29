"""codex_ml.feedback — Feedback loop integration package.

Exported symbols
----------------
FeedbackCollector
    Thread-safe in-memory (+ optional JSONL-sink) collector for feedback events.
FeedbackEvent
    Dataclass representing a single captured feedback signal.
FeedbackLoop
    High-level loop that ingests monitoring alerts and drift signals and
    exposes a :meth:`~FeedbackLoop.should_adapt` decision predicate.
"""

from __future__ import annotations

from codex_ml.feedback.collector import FeedbackCollector
from codex_ml.feedback.events import FeedbackEvent
from codex_ml.feedback.loop import FeedbackLoop

__all__ = [
    "FeedbackCollector",
    "FeedbackEvent",
    "FeedbackLoop",
]
