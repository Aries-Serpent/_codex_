"""Tests for ActiveLearningHook query budget enforcement (Phase 6 P2)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from cognitive_brain.active_learning.hook import ActiveLearningHook


def _make_audit(audit_id: str = "a1") -> MagicMock:
    m = MagicMock()
    m.audit_id = audit_id
    return m


def _make_assessment(confidence: float = 0.3) -> MagicMock:
    m = MagicMock()
    m.confidence = confidence
    m.decision = MagicMock()
    m.decision.value = "approve"
    m.coherence = 0.8
    m.bias_flags = []
    return m


@pytest.fixture(autouse=True)
def _enable_al(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CODEX_ACTIVE_LEARNING", "true")
    monkeypatch.setenv("CODEX_AL_UNCERTAINTY_THRESHOLD", "0.5")  # confidence<0.5 → queued


def test_query_budget_enforced(monkeypatch: pytest.MonkeyPatch) -> None:
    """Budget of N/day: only first N uncertain samples are queued."""
    hook = ActiveLearningHook(query_budget_per_day=3)

    results = [
        hook.record_if_uncertain(_make_audit(f"a{i}"), _make_assessment(confidence=0.1))
        for i in range(5)
    ]

    assert results[:3] == [True, True, True], "First 3 should be queued"
    assert results[3:] == [False, False], "Budget exceeded — should not queue"
    assert len(hook.get_queue()) == 3, "Collection must not be empty"


def test_budget_resets_across_days(monkeypatch: pytest.MonkeyPatch) -> None:
    """Simulate two different days — each day has its own budget."""
    from datetime import timezone

    hook = ActiveLearningHook(query_budget_per_day=2)

    # Day 1
    hook._daily_counts["2026-01-01"] = 2  # Simulate budget exhausted on day 1

    # Day 2 — fresh budget
    from datetime import datetime
    from unittest.mock import patch

    fixed_day2 = datetime(2026, 1, 2, 12, 0, 0, tzinfo=timezone.utc)
    with patch("cognitive_brain.active_learning.hook.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_day2
        result = hook.record_if_uncertain(_make_audit("day2-a1"), _make_assessment(0.1))

    assert result is True, "Day 2 budget should be fresh"


def test_budget_default_is_50() -> None:
    """Default budget is 50 per day."""
    hook = ActiveLearningHook()
    assert hook.query_budget_per_day == 50, "query_budget_per_day is not valid"


def test_budget_zero_blocks_all(monkeypatch: pytest.MonkeyPatch) -> None:
    """Budget of 0 blocks all queries."""
    hook = ActiveLearningHook(query_budget_per_day=0)
    result = hook.record_if_uncertain(_make_audit(), _make_assessment(confidence=0.1))
    assert result is False, "Result must not be empty"
    assert len(hook.get_queue()) == 0, "Collection must not be empty"
