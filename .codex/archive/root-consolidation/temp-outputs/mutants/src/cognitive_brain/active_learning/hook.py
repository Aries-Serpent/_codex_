"""
Active Learning Hook for Continuous Compliance Improvement (Phase 4)

Staging-only hook that records uncertain compliance decisions for
human-expert review and future model fine-tuning.

Feature flag: CODEX_ACTIVE_LEARNING=true (default: false)
             CODEX_AL_UNCERTAINTY_THRESHOLD=0.70 (default)

Research basis: Brener 2021 — Active Learning achieved 30%+ false-positive
reduction via selective human annotation of uncertain predictions.

Design principle: This hook is write-only in staging. It records decisions
with low confidence / high uncertainty to a staging queue for human review.
It does NOT modify decisions — it only annotates them for learning.

API:
    hook = ActiveLearningHook()
    hook.record_if_uncertain(audit_result, assessment)
    queued = hook.get_queue()
    hook.clear_queue()
"""

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cognitive_brain.integrations.compliance_integration import (
        AuditResult,
        ComplianceAssessment,
    )


def _active_learning_enabled() -> bool:
    """Check CODEX_ACTIVE_LEARNING env flag (default: false)."""
    return os.getenv("CODEX_ACTIVE_LEARNING", "false").lower() in (
        "true",
        "1",
        "yes",
        "on",
    )


def _uncertainty_threshold() -> float:
    """Read configurable uncertainty threshold (default 0.70)."""
    try:
        return float(os.getenv("CODEX_AL_UNCERTAINTY_THRESHOLD", "0.70"))
    except ValueError:
        return 0.70


@dataclass
class UncertainSample:
    """
    A compliance decision queued for human expert review.

    Attributes:
        audit_id:      Identifier from the original AuditResult.
        timestamp:     ISO-8601 UTC timestamp when the sample was queued.
        decision:      The decision made by the model.
        confidence:    Model confidence (0.0–1.0).
        coherence:     Quantum coherence at decision time.
        uncertainty:   1.0 - confidence (higher = more uncertain).
        bias_flags:    Any bias flags raised during assessment.
        review_status: "pending" → "reviewed" → "accepted" | "rejected".
    """

    audit_id: str
    timestamp: str
    decision: str
    confidence: float
    coherence: float
    uncertainty: float
    bias_flags: list[str]
    review_status: str = "pending"


@dataclass
class ActiveLearningHook:
    """
    Staging hook that collects uncertain compliance decisions for human review.

    Records samples whose model confidence falls below the configurable
    ``CODEX_AL_UNCERTAINTY_THRESHOLD`` (default 0.70) so domain experts can
    annotate them.  The annotated samples can then be fed back into the
    scoring functions as additional ground-truth for future fine-tuning.

    This hook is a **no-op** unless ``CODEX_ACTIVE_LEARNING=true``.

    Example::

        hook = ActiveLearningHook()
        hook.record_if_uncertain(audit_result, assessment)

        # Later: review queued samples
        samples = hook.get_queue()
        print(f"{len(samples)} samples awaiting review")

        # Mark as reviewed
        hook.mark_reviewed("audit-001", accepted=True)
    """

    _queue: list[UncertainSample] = field(default_factory=list, init=False)
    query_budget_per_day: int = 50
    _daily_counts: dict[str, int] = field(default_factory=dict, init=False)

    def _enforce_query_budget(self) -> bool:
        """Enforce daily query budget. Returns False when budget exceeded."""
        today = datetime.now(timezone.utc).date().isoformat()
        count = self._daily_counts.get(today, 0)
        if count >= self.query_budget_per_day:
            import logging

            logging.getLogger(__name__).warning(
                "Active learning query budget (%d/day) exceeded",
                self.query_budget_per_day,
            )
            return False
        self._daily_counts[today] = count + 1
        return True

    def record_if_uncertain(
        self,
        audit: "AuditResult",
        assessment: "ComplianceAssessment",
    ) -> bool:
        """
        Queue the assessment for human review if confidence is below threshold.

        This is a no-op when:
        - ``CODEX_ACTIVE_LEARNING`` is not enabled.
        - Assessment confidence is ≥ ``CODEX_AL_UNCERTAINTY_THRESHOLD``.

        Args:
            audit:      The source AuditResult.
            assessment: The compliance decision and metrics.

        Returns:
            ``True`` if the sample was queued, ``False`` otherwise.
        """
        if not _active_learning_enabled():
            return False

        if not self._enforce_query_budget():
            return False

        threshold = _uncertainty_threshold()
        uncertainty = 1.0 - assessment.confidence

        if assessment.confidence >= threshold:
            return False  # Model is confident — no review needed

        sample = UncertainSample(
            audit_id=audit.audit_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            decision=assessment.decision.value,
            confidence=assessment.confidence,
            coherence=assessment.coherence,
            uncertainty=uncertainty,
            bias_flags=list(assessment.bias_flags),
        )
        self._queue.append(sample)
        return True

    def get_queue(
        self,
        status: str | None = None,
    ) -> list[UncertainSample]:
        """
        Return queued uncertain samples.

        Args:
            status: Filter by review_status ("pending", "reviewed",
                    "accepted", "rejected").  ``None`` returns all.

        Returns:
            List of ``UncertainSample`` objects.
        """
        if status is None:
            return list(self._queue)
        return [s for s in self._queue if s.review_status == status]

    def mark_reviewed(self, audit_id: str, accepted: bool) -> bool:
        """
        Mark a queued sample as reviewed.

        Args:
            audit_id: Audit identifier to mark.
            accepted: ``True`` if the model decision was correct;
                      ``False`` if the human expert disagrees.

        Returns:
            ``True`` if found and updated, ``False`` if not found.
        """
        for sample in self._queue:
            if sample.audit_id == audit_id and sample.review_status == "pending":
                sample.review_status = "accepted" if accepted else "rejected"
                return True
        return False

    def clear_queue(self) -> int:
        """
        Clear all reviewed samples from the queue.

        Returns:
            Number of samples removed.
        """
        before = len(self._queue)
        self._queue = [s for s in self._queue if s.review_status == "pending"]
        return before - len(self._queue)

    @property
    def pending_count(self) -> int:
        """Number of samples awaiting human review."""
        return sum(1 for s in self._queue if s.review_status == "pending")

    @property
    def total_count(self) -> int:
        """Total number of samples ever queued (including reviewed)."""
        return len(self._queue)
