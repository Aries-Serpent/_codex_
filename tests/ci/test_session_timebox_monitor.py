from __future__ import annotations

from datetime import datetime, timedelta, timezone

from scripts.ci.session_timebox_monitor import build_prompt, get_sleep_interval, monitor


def test_build_prompt_uses_actual_deadline_and_remaining_budget() -> None:
    started_at = datetime(2026, 10, 8, 5, 0, tzinfo=timezone.utc)
    deadline = datetime(2026, 10, 8, 5, 20, tzinfo=timezone.utc)
    remaining = timedelta(minutes=5)

    prompt = build_prompt(
        "feature/demo",
        "owner/repo",
        started_at,
        deadline,
        remaining,
        "git status --short --branch",
    )

    assert "**Planned deadline:** 2026-10-08T05:20:00Z" in prompt
    assert "**Remaining before limit:** 0:05:00" in prompt


def test_get_sleep_interval_caps_sleep_at_warning_boundary() -> None:
    now = datetime(2026, 10, 8, 5, 0, tzinfo=timezone.utc)
    deadline = datetime(2026, 10, 8, 5, 2, tzinfo=timezone.utc)
    warning_trigger = timedelta(minutes=1)

    sleep_for = get_sleep_interval(now, deadline, warning_trigger, 180, warned=False)

    assert sleep_for == timedelta(minutes=1)


def test_monitor_uses_actual_remaining_time_when_warning_triggers(monkeypatch) -> None:
    times = iter(
        [
            datetime(2026, 10, 8, 5, 0, 0, tzinfo=timezone.utc),
            datetime(2026, 10, 8, 5, 1, 30, tzinfo=timezone.utc),
            datetime(2026, 10, 8, 5, 2, 0, tzinfo=timezone.utc),
        ]
    )
    captured: dict[str, object] = {}

    def fake_utc_now() -> datetime:
        try:
            return next(times)
        except StopIteration:
            return datetime(2026, 10, 8, 5, 2, 0, tzinfo=timezone.utc)

    def fake_warn_and_prepare(started_at, deadline, remaining, warning_window_minutes, prompt_path) -> None:
        captured["deadline"] = deadline
        captured["remaining"] = remaining
        captured["warning_window_minutes"] = warning_window_minutes

    monkeypatch.setattr("scripts.ci.session_timebox_monitor.utc_now", fake_utc_now)
    monkeypatch.setattr("scripts.ci.session_timebox_monitor.warn_and_prepare", fake_warn_and_prepare)
    monkeypatch.setattr("scripts.ci.session_timebox_monitor.time.sleep", lambda _seconds: None)

    result = monitor(2, 1, 180, __import__("pathlib").Path(".codex/continuation_prompt.md"), once=False)

    assert result == 0
    assert captured["deadline"] == datetime(2026, 10, 8, 5, 2, tzinfo=timezone.utc)
    assert captured["remaining"] == timedelta(minutes=0, seconds=30)
    assert captured["warning_window_minutes"] == 1
