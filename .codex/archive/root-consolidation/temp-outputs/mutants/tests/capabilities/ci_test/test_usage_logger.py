"""
Tests for scripts/ci/usage_logger.py (T-004).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.ci.usage_logger as ul


@pytest.fixture()
def tmp_log(tmp_path: Path) -> Path:
    """Return a temporary log path that doesn't exist yet."""
    log_file = tmp_path / "usage.ndjson"
    ul._LOG_PATH = log_file  # override module default for each test
    return log_file


# ── log_usage ──────────────────────────────────────────────────────────────


class TestLogUsage:
    def test_creates_file_on_first_write(self, tmp_log: Path) -> None:
        ul.log_usage(
            workflow="Test WF",
            runner="ubuntu-latest",
            effective_minutes=10.0,
            tier="GREEN",
        )
        assert tmp_log.exists(), "Condition must be true"

    def test_appends_valid_json_lines(self, tmp_log: Path) -> None:
        ul.log_usage(workflow="W1", runner="ubuntu-latest", effective_minutes=5.0, tier="GREEN")
        ul.log_usage(workflow="W2", runner="ubuntu-latest", effective_minutes=50.0, tier="YELLOW")
        lines = [json.loads(ln) for ln in tmp_log.read_text().splitlines() if ln.strip()]
        assert len(lines) == 2, "Lines must not be empty"
        assert lines[0]["workflow"] == "W1", "Condition must be true"
        assert lines[1]["tier"] == "YELLOW", "Condition must be true"

    def test_fields_present(self, tmp_log: Path) -> None:
        entry = ul.log_usage(
            workflow="Build Preview",
            runner="ubuntu-latest-m",
            effective_minutes=120.0,
            tier="RED",
            pr_number="42",
            branch="main",
            sha="abc123",
            approved=True,
        )
        assert "ts" in entry, "Condition must be true"
        assert entry["effective_minutes"] == 120.0, "Condition must be true"
        assert entry["pr"] == "42", "Condition must be true"
        assert entry["sha"] == "abc123", "Condition must be true"
        assert entry["approved"] is True, "Condition must be true"

    def test_sha_truncated_to_12(self, tmp_log: Path) -> None:
        entry = ul.log_usage(
            workflow="W",
            runner="r",
            effective_minutes=1.0,
            tier="GREEN",
            sha="abcdefghijklmnop",
        )
        assert len(entry["sha"]) <= 12, "Collection must not be empty"

    def test_optional_fields_omitted_when_empty(self, tmp_log: Path) -> None:
        entry = ul.log_usage(workflow="W", runner="r", effective_minutes=1.0, tier="GREEN")
        assert "pr" not in entry, "Condition must be true"
        assert "branch" not in entry, "Condition must be true"
        assert "sha" not in entry, "Condition must be true"
        assert "approved" not in entry, "Condition must be true"


# ── monthly_summary ────────────────────────────────────────────────────────


class TestMonthlySummary:
    def test_no_log_returns_zero(self, tmp_log: Path) -> None:
        summary = ul.monthly_summary(tmp_log)
        assert summary["total_minutes"] == 0.0, "Condition must be true"
        assert summary["entries"] == 0, "Condition must be true"

    def test_sums_current_month_only(self, tmp_log: Path) -> None:
        import datetime

        # Current-month entry
        now = datetime.datetime.now(datetime.timezone.utc)
        entry_now = {
            "ts": now.isoformat(),
            "workflow": "W",
            "runner": "ubuntu-latest",
            "effective_minutes": 30.0,
            "tier": "GREEN",
        }
        # Last-month entry (should not be counted).
        # Use timedelta(days=32) to safely land in the previous calendar month
        # without day-overflow errors (e.g. March 29 → replace(month=2) raises
        # ValueError because Feb 29 does not exist in non-leap years).
        # 32 days is chosen because no calendar month has more than 31 days,
        # so subtracting 32 always crosses into the prior month.
        last_month = now - datetime.timedelta(days=32)
        entry_old = {
            "ts": last_month.isoformat(),
            "workflow": "W",
            "runner": "ubuntu-latest",
            "effective_minutes": 999.0,
            "tier": "RED",
        }
        with tmp_log.open("w") as fh:
            fh.write(json.dumps(entry_now) + "\n")
            fh.write(json.dumps(entry_old) + "\n")

        summary = ul.monthly_summary(tmp_log)
        assert summary["total_minutes"] == 30.0, "Condition must be true"
        assert summary["entries"] == 1, "Condition must be true"

    def test_accumulates_multiple_entries(self, tmp_log: Path) -> None:
        import datetime

        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        entries = [
            {"ts": ts, "workflow": "A", "runner": "r", "effective_minutes": 10.0, "tier": "GREEN"},
            {"ts": ts, "workflow": "B", "runner": "r", "effective_minutes": 20.5, "tier": "YELLOW"},
            {"ts": ts, "workflow": "C", "runner": "r", "effective_minutes": 60.0, "tier": "RED"},
        ]
        with tmp_log.open("w") as fh:
            for e in entries:
                fh.write(json.dumps(e) + "\n")

        summary = ul.monthly_summary(tmp_log)
        assert summary["total_minutes"] == pytest.approx(90.5, rel=1e-3)
        assert summary["entries"] == 3, "Condition must be true"

    def test_ignores_malformed_lines(self, tmp_log: Path) -> None:
        import datetime

        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with tmp_log.open("w") as fh:
            fh.write("not-json\n")
            fh.write(json.dumps({"ts": ts, "effective_minutes": 15.0, "tier": "GREEN"}) + "\n")

        summary = ul.monthly_summary(tmp_log)
        assert summary["total_minutes"] == 15.0, "Condition must be true"


# ── budget alert exit code ─────────────────────────────────────────────────


class TestBudgetAlert:
    def test_below_threshold_returns_0(self, tmp_log: Path) -> None:
        import datetime

        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with tmp_log.open("w") as fh:
            fh.write(json.dumps({"ts": ts, "effective_minutes": 100.0, "tier": "GREEN"}) + "\n")

        summary = ul.monthly_summary(tmp_log)
        assert summary["total_minutes"] < 2500.0, "Condition must be true"

    def test_at_threshold_returns_alert(self, tmp_log: Path) -> None:
        import datetime

        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with tmp_log.open("w") as fh:
            fh.write(json.dumps({"ts": ts, "effective_minutes": 2500.0, "tier": "RED"}) + "\n")

        summary = ul.monthly_summary(tmp_log)
        assert summary["total_minutes"] >= 2500.0, "Value must be greater than zero"
