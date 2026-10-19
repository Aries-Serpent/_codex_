"""Outcome measurement and calibrated pattern-confidence updates.

Confidence is updated *only* from an outcome traceable to the original
event (pattern ID + patch hash) and only after the merge produced a
measured post-merge signal. Unverified or pending outcomes never touch
the pattern store.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Optional

logger = logging.getLogger(__name__)

# Post-merge outcomes that are strong enough evidence to move confidence.
_MEASURED_OUTCOMES = frozenset({"success", "regression", "rollback"})

_OUTCOME_TO_FEEDBACK = {
    "success": "success",
    "regression": "failure",
    "rollback": "failure",
}


@dataclass(frozen=True, slots=True)
class ConfidenceUpdate:
    """Traceable record of a confidence change."""

    pattern_id: str
    event_id: str
    patch_hash: str
    outcome: str
    previous_rate: float
    new_rate: float
    alpha: float


class OutcomeTracker:
    """Link verified post-merge outcomes to pattern-confidence updates.

    Parameters
    ----------
    brain_interface:
        The agent brain interface exposing ``submit_learning`` and the
        pattern store (the existing EMA seam).
    outcome_source:
        Callable mapping an event ID to a measured post-merge outcome
        record (``{"outcome": ..., "merged": bool, ...}``). Injected so
        tests can replay recorded outcomes without network access.
    alpha:
        EMA smoothing factor used when reporting the expected update;
        the authoritative update happens inside the brain interface.
    """

    def __init__(
        self,
        brain_interface: Any,
        outcome_source: Callable[[str], Optional[Mapping[str, Any]]],
        *,
        alpha: float = 0.3,
    ) -> None:
        self.brain = brain_interface
        self.outcome_source = outcome_source
        self.alpha = alpha

    def process_outcome(
        self,
        *,
        event_id: str,
        pattern_id: str,
        patch_hash: str,
    ) -> Optional[ConfidenceUpdate]:
        """Update confidence from a verified outcome, or return None.

        Returns None (no update) when the outcome is missing, not merged,
        or not a measured terminal state — confidence must never move on
        unverified feedback.
        """

        record = self.outcome_source(event_id)
        if record is None:
            logger.info("No outcome recorded for event %s; skipping update", event_id)
            return None
        if not record.get("merged", False):
            logger.info("Event %s was not merged; skipping confidence update", event_id)
            return None

        outcome = str(record.get("outcome", "pending"))
        if outcome not in _MEASURED_OUTCOMES:
            logger.info("Outcome %r for event %s is not measured; skipping", outcome, event_id)
            return None

        previous_rate = self._current_rate(pattern_id)
        feedback = _OUTCOME_TO_FEEDBACK[outcome]
        applied = self.brain.submit_learning(
            pattern_id=pattern_id,
            outcome=feedback,
            context={"event_id": event_id, "patch_hash": patch_hash, "outcome": outcome},
            resolution_details=f"post-merge outcome={outcome} for event {event_id}",
        )
        if not applied:
            logger.warning("Pattern %s rejected the learning update", pattern_id)
            return None

        new_rate = self._current_rate(pattern_id)
        return ConfidenceUpdate(
            pattern_id=pattern_id,
            event_id=event_id,
            patch_hash=patch_hash,
            outcome=outcome,
            previous_rate=previous_rate,
            new_rate=new_rate,
            alpha=self.alpha,
        )

    def _current_rate(self, pattern_id: str) -> float:
        pattern = self.brain.get_pattern(pattern_id)
        if pattern is None:
            return 0.0
        return float(getattr(pattern, "success_rate", 0.0))
