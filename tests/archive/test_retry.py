from __future__ import annotations

from collections import deque

import pytest

from codex.archive.retry import RetryConfig, calculate_backoff, retry_with_backoff


def test_calculate_backoff_progression() -> None:
    cfg = RetryConfig(initial_delay=1.0, multiplier=2.0, max_delay=4.0, jitter=0.0)
    delays = [calculate_backoff(attempt, config=cfg) for attempt in range(1, 5)]
    assert delays == [1.0, 2.0, 4.0, 4.0]


def test_retry_eventually_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = deque([ConnectionError("boom"), ConnectionError("boom"), "ok"])
    slept: list[float] = []
    monkeypatch.setattr("codex.archive.retry.time.sleep", slept.append)

    @retry_with_backoff(RetryConfig(max_attempts=3, initial_delay=0, max_delay=0, jitter=0))
    def flaky() -> str:
        result = calls.popleft()
        if isinstance(result, Exception):
            raise result
        return result

    assert flaky() == "ok"
    assert slept  # ensure backoff triggered at least once


def test_retry_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    attempts = 0

    @retry_with_backoff(RetryConfig(enabled=False))
    def always_fail() -> None:
        nonlocal attempts
        attempts += 1
        raise ConnectionError("no retry")

    with pytest.raises(ConnectionError):
        always_fail()
    assert attempts == 1


def test_retry_does_not_swallow_non_transient(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("codex.archive.retry.time.sleep", lambda _: None)

    @retry_with_backoff(RetryConfig(max_attempts=2))
    def raises_value_error() -> None:
        raise ValueError("permanent failure")

    with pytest.raises(ValueError):
        raises_value_error()
