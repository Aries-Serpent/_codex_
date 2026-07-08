"""
Tests for monitor_run.py — Run Monitor & Cherry-Pick CLI

Covers PollSnapshot serialisation, state-file round-trip, run-ID resolution,
cherry_pick_delta path filtering, exit-code mapping, session timing (h/m/s/ns),
and the background-thread API.  No live GitHub API or network calls are made.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent.parent.parent / "scripts" / "ci"
sys.path.insert(0, str(SCRIPT_DIR))

try:
    import monitor_run as mr
    from monitor_run import (
        MonitorThread,
        PollSnapshot,
        _compute_elapsed,
        _exit_code,
        _read_state,
        _resolve_session_start,
        _write_state,
        cherry_pick_delta,
        cmd_list,
        poll_status,
        start_background_monitor,
    )
except ImportError:
    pytest.skip("monitor_run module not available", allow_module_level=True)


# ---------------------------------------------------------------------------
# PollSnapshot serialisation round-trip
# ---------------------------------------------------------------------------


class TestPollSnapshot:
    def test_to_dict_contains_all_fields(self):
        snap = PollSnapshot(
            run_id=1234,
            repo="owner/repo",
            polled_at="2026-03-17T23:00:00Z",
            status="in_progress",
            conclusion=None,
            head_sha="abc123",
            head_branch="main",
            html_url="https://github.com",
        )
        d = snap.to_dict()
        assert d["run_id"] == 1234, "Condition must be true"
        assert d["status"] == "in_progress", "Condition must be true"
        assert d["conclusion"] is None, "Condition must be true"
        assert d["completed"] is False, "Condition must be true"

    def test_from_dict_round_trip(self):
        snap = PollSnapshot(
            run_id=99,
            repo="a/b",
            polled_at="2026-03-17T23:00:00Z",
            status="completed",
            conclusion="success",
            head_sha="def456",
            head_branch="feat",
            html_url="https://x.com",
            cherry_picked=["file.py"],
            triage_passed=True,
            completed=True,
        )
        restored = PollSnapshot.from_dict(snap.to_dict())
        assert restored.run_id == 99, "run_id is not valid"
        assert restored.conclusion == "success", "conclusion is not valid"
        assert restored.cherry_picked == ["file.py"], "cherry_picked is not valid"
        assert restored.triage_passed is True, "triage_passed is not valid"
        assert restored.completed is True, "completed is not valid"

    def test_from_dict_ignores_unknown_keys(self):
        d = {
            "run_id": 1,
            "repo": "a/b",
            "polled_at": "t",
            "status": "completed",
            "conclusion": "success",
            "head_sha": "",
            "head_branch": "",
            "html_url": "",
            "unknown_future_field": "ignored",
        }
        snap = PollSnapshot.from_dict(d)
        assert snap.run_id == 1, "run_id is not valid"


# ---------------------------------------------------------------------------
# State-file read / write  (uses tmp_path)
# ---------------------------------------------------------------------------


class TestStateFile:
    def test_write_then_read(self, tmp_path, monkeypatch):
        monkeypatch.setattr(mr, "MONITOR_DIR", tmp_path / "monitor")
        snap = PollSnapshot(
            run_id=42,
            repo="x/y",
            polled_at="2026-03-17T23:00:00Z",
            status="in_progress",
            conclusion=None,
            head_sha="",
            head_branch="",
            html_url="",
        )
        _write_state(snap)
        restored = _read_state(42)
        assert restored.run_id == 42, "run_id must round-trip correctly"
        assert restored.status == "in_progress", "status must round-trip correctly"

    def test_read_nonexistent_returns_none(self, tmp_path, monkeypatch):
        monkeypatch.setattr(mr, "MONITOR_DIR", tmp_path / "monitor")
        assert _read_state(99999) is None, "Condition must be true"

    def test_poll_status_api(self, tmp_path, monkeypatch):
        monkeypatch.setattr(mr, "MONITOR_DIR", tmp_path / "monitor")
        assert poll_status(12345) is None, "Condition must be true"
        snap = PollSnapshot(
            run_id=12345,
            repo="x/y",
            polled_at="2026-03-17T23:00:00Z",
            status="completed",
            conclusion="success",
            head_sha="",
            head_branch="",
            html_url="",
            completed=True,
        )
        _write_state(snap)
        result = poll_status(12345)
        assert result.conclusion == "success", "conclusion must match the written snapshot"
        assert result.status == "completed", "status must match the written snapshot"


# ---------------------------------------------------------------------------
# Exit-code mapping
# ---------------------------------------------------------------------------


class TestExitCode:
    def test_success(self):
        snap = PollSnapshot(
            run_id=1,
            repo="a/b",
            polled_at="t",
            status="completed",
            conclusion="success",
            head_sha="",
            head_branch="",
            html_url="",
            completed=True,
        )
        assert _exit_code(snap) == 0, "Condition must be true"

    def test_failure(self):
        snap = PollSnapshot(
            run_id=1,
            repo="a/b",
            polled_at="t",
            status="completed",
            conclusion="failure",
            head_sha="",
            head_branch="",
            html_url="",
            completed=True,
        )
        assert _exit_code(snap) == 1, "Condition must be true"

    def test_timeout(self):
        snap = PollSnapshot(
            run_id=1,
            repo="a/b",
            polled_at="t",
            status="in_progress",
            conclusion=None,
            head_sha="",
            head_branch="",
            html_url="",
            error="Timeout after 90 minutes",
            completed=True,
        )
        assert _exit_code(snap) == 2, "Condition must be true"

    def test_api_error(self):
        snap = PollSnapshot(
            run_id=1,
            repo="a/b",
            polled_at="t",
            status="error",
            conclusion=None,
            head_sha="",
            head_branch="",
            html_url="",
            error="HTTP 404: ...",
            completed=True,
        )
        assert _exit_code(snap) == 3, "Condition must be true"

    def test_triage_failure(self):
        snap = PollSnapshot(
            run_id=1,
            repo="a/b",
            polled_at="t",
            status="completed",
            conclusion="success",
            head_sha="",
            head_branch="",
            html_url="",
            triage_passed=False,
            completed=True,
        )
        assert _exit_code(snap) == 4, "Condition must be true"

    def test_skipped_is_success(self):
        snap = PollSnapshot(
            run_id=1,
            repo="a/b",
            polled_at="t",
            status="completed",
            conclusion="skipped",
            head_sha="",
            head_branch="",
            html_url="",
            completed=True,
        )
        assert _exit_code(snap) == 0, "Condition must be true"


# ---------------------------------------------------------------------------
# cherry_pick_delta — path filtering
# ---------------------------------------------------------------------------


class TestCherryPickDelta:
    def test_skips_agent_auth_files(self, tmp_path, monkeypatch):
        """Files matching _SKIP_PATTERNS must never be checked out."""
        monkeypatch.setattr(mr, "REPO_ROOT", tmp_path)
        (tmp_path / ".git").mkdir()

        def fake_git(*args):
            if args[0] == "fetch":
                return ""
            if args[0] == "diff":
                return ".codex/agent_auth_session.json\nCODEX_MANIFEST.json\nREADME.md"
            if args[0] == "checkout":
                return ""
            return ""

        checked_out = []

        def capturing_git(*args):
            if args[0] == "checkout":
                checked_out.append(args[-1])
            return fake_git(*args)

        monkeypatch.setattr(mr, "_git", capturing_git)
        applied = cherry_pick_delta("main")
        assert ".codex/agent_auth_session.json" not in checked_out, "Condition must be true"
        assert "CODEX_MANIFEST.json" not in checked_out, "Condition must be true"
        assert "README.md" in checked_out, "Condition must be true"
        assert applied == ["README.md"], "applied is not valid"

    def test_empty_diff_returns_empty_list(self, tmp_path, monkeypatch):
        monkeypatch.setattr(mr, "REPO_ROOT", tmp_path)

        def fake_git(*args):
            if args[0] == "fetch":
                return ""
            return ""  # empty diff

        monkeypatch.setattr(mr, "_git", fake_git)
        assert cherry_pick_delta("main") == [], "Condition must be true"


# ---------------------------------------------------------------------------
# cmd_list — no monitors
# ---------------------------------------------------------------------------


class TestCmdList:
    def test_no_monitor_dir(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(mr, "MONITOR_DIR", tmp_path / "monitor_nonexistent")
        result = cmd_list()
        assert result == 0, "Result must not be empty"
        out = capsys.readouterr().out
        assert "No monitor" in out, "Condition must be true"

    def test_empty_monitor_dir(self, tmp_path, monkeypatch, capsys):
        monitor = tmp_path / "monitor"
        monitor.mkdir()
        monkeypatch.setattr(mr, "MONITOR_DIR", monitor)
        result = cmd_list()
        assert result == 0, "Result must not be empty"


# ---------------------------------------------------------------------------
# API: start_background_monitor returns MonitorThread
# ---------------------------------------------------------------------------


class TestStartBackgroundMonitor:
    def test_returns_thread(self, monkeypatch):
        """start_background_monitor must return a started MonitorThread."""

        # Patch _poll_loop so the thread exits immediately
        def instant_poll(*args, **kwargs):
            return PollSnapshot(
                run_id=1,
                repo="a/b",
                polled_at="t",
                status="completed",
                conclusion="success",
                head_sha="",
                head_branch="",
                html_url="",
                completed=True,
            )

        monkeypatch.setattr(mr, "_poll_loop", instant_poll)
        monkeypatch.setattr(mr, "_resolve_repo", lambda: "a/b")

        handle = start_background_monitor(run_id=1, repo="a/b")
        assert isinstance(handle, MonitorThread
        )  # start_background_monitor must return a MonitorThread
        handle.join(timeout=5)
        assert handle.result.conclusion == "success", "background monitor conclusion must be success"


# ---------------------------------------------------------------------------
# Session timing: _resolve_session_start + _compute_elapsed (h/m/s/ns)
# ---------------------------------------------------------------------------


class TestSessionTiming:
    def test_resolve_prefers_env_var(self, monkeypatch):
        """GITHUB_RUN_STARTED_AT env var takes priority over api_run_started_at."""
        monkeypatch.setenv("GITHUB_RUN_STARTED_AT", "2026-03-17T23:15:08Z")
        iso, ns = _resolve_session_start()
        assert iso == "2026-03-17T23:15:08Z", "iso is not valid"
        # ns must be a valid positive integer representing that timestamp
        assert ns > 0, "ns must be greater than zero"

    def test_resolve_cli_override_beats_env_var(self, monkeypatch):
        """cli_override takes highest priority — must override GITHUB_RUN_STARTED_AT."""
        monkeypatch.setenv("GITHUB_RUN_STARTED_AT", "2026-03-17T23:15:08Z")
        override_ts = "2026-01-01T00:00:00Z"
        iso, ns = _resolve_session_start(cli_override=override_ts)
        assert iso == override_ts, f"cli_override should beat GITHUB_RUN_STARTED_AT; got {iso!r}"
        assert ns > 0, "ns must be greater than zero"

    def test_resolve_uses_api_fallback(self, monkeypatch):
        """When env var absent, API run_started_at is used."""
        monkeypatch.delenv("GITHUB_RUN_STARTED_AT", raising=False)
        iso, ns = _resolve_session_start("2026-03-17T22:00:00+00:00")
        assert "2026-03-17" in iso, "in is not valid"
        assert ns > 0, "ns must be greater than zero"

    def test_resolve_fallback_to_now(self, monkeypatch):
        """When both env and api_ts absent, falls back to current time."""
        monkeypatch.delenv("GITHUB_RUN_STARTED_AT", raising=False)
        before_ns = time.time_ns()
        iso, ns = _resolve_session_start()
        after_ns = time.time_ns()
        assert before_ns <= ns <= after_ns, "before_ns is not valid"
        assert "2026" in iso or "202" in iso, "in is not valid"

    def test_compute_elapsed_sub_second(self):
        """Elapsed under 1 second produces '0s NNNNNNNNNns' format."""
        now_ns = time.time_ns()
        # Simulate start 500ms ago
        start_ns = now_ns - 500_000_000
        el_s, el_ns, human = _compute_elapsed(start_ns)
        assert el_s == 0, "el_s is not valid"
        assert 0 <= el_ns < 1_000_000_000, "0 is not valid"
        assert human.endswith("ns")
        assert len(human.split()[-1].rstrip("ns")) == 9, "Collection must not be empty"

    def test_compute_elapsed_minutes_seconds(self):
        """Elapsed 2m 7s produces 'Xm Ys NNNNNNNNNns' format."""
        # 2 min 7 sec = 127 seconds
        start_ns = time.time_ns() - 127_123_456_789
        el_s, _el_ns, human = _compute_elapsed(start_ns)
        assert el_s >= 127, "el_s must be greater than zero"
        assert "m" in human, "Condition must be true"
        assert "s" in human, "Condition must be true"
        parts = human.split()
        # Last part is nanoseconds
        assert parts[-1].endswith("ns"), "Condition must be true"
        ns_digits = parts[-1].rstrip("ns")
        assert len(ns_digits) == 9, "Ns_digits must not be empty"

    def test_compute_elapsed_hours(self):
        """Elapsed > 1h produces 'Xh Ym Zs NNNNNNNNNns' format."""
        # 1h 5m 3s = 3903 seconds
        start_ns = time.time_ns() - 3_903_000_000_000
        el_s, _el_ns, human = _compute_elapsed(start_ns)
        assert el_s >= 3903, "el_s must be greater than zero"
        assert human.startswith("1h") or int(human.split("h")[0]) >= 1, "Value must be greater than zero"

    def test_compute_elapsed_nanosecond_remainder_9_digits(self):
        """ns remainder is always zero-padded to exactly 9 digits."""
        # Start exactly 1s + 1ns ago → ns_rem should be 000000001
        start_ns = time.time_ns() - 1_000_000_001
        _, _el_ns, human = _compute_elapsed(start_ns)
        ns_part = human.split()[-1].rstrip("ns")
        assert len(ns_part) == 9, f"Expected 9-digit ns, got: {ns_part!r}"

    def test_snapshot_timing_fields_serialise(self):
        """session_started_ns and session_elapsed_ns survive to_dict/from_dict."""
        snap = PollSnapshot(
            run_id=1,
            repo="a/b",
            polled_at="t",
            status="completed",
            conclusion="success",
            head_sha="",
            head_branch="",
            html_url="",
            session_started_at="2026-03-17T23:15:08Z",
            session_started_ns=1742252108_000000000,
            current_dt="2026-03-17T23:48:22Z",
            session_elapsed_s=1994,
            session_elapsed_ns=123456789,
            session_elapsed_str="33m 14s 123456789ns",
            completed=True,
        )
        d = snap.to_dict()
        assert d["session_started_ns"] == 1742252108_000000000, "Condition must be true"
        assert d["session_elapsed_ns"] == 123456789, "Condition must be true"
        assert d["session_elapsed_str"] == "33m 14s 123456789ns", "Condition must be true"

        restored = PollSnapshot.from_dict(d)
        assert restored.session_started_ns == 1742252108_000000000, "session_started_ns is not valid"
        assert restored.session_elapsed_ns == 123456789, "session_elapsed_ns is not valid"
        assert restored.session_elapsed_str == "33m 14s 123456789ns", "session_elapsed_str is not valid"

    def test_poll_loop_stamps_timing(self, monkeypatch, tmp_path):
        """_poll_loop must stamp session_elapsed_str on the returned snapshot."""
        monkeypatch.setattr(mr, "MONITOR_DIR", tmp_path / "monitor")

        # Build a fake client that returns a completed run
        class FakeClient:
            def get_run(self, repo, run_id):
                snap = PollSnapshot(
                    run_id=run_id,
                    repo=repo,
                    polled_at=mr._now(),
                    status="completed",
                    conclusion="success",
                    head_sha="abc",
                    head_branch="main",
                    html_url="https://x",
                )
                snap._api_run_started_at = ""  # type: ignore[attr-defined]
                return snap

        monkeypatch.delenv("GITHUB_RUN_STARTED_AT", raising=False)
        start_ns = time.time_ns() - 65_000_000_000  # 65s ago

        result = mr._poll_loop(
            run_id=1,
            repo="a/b",
            client=FakeClient(),  # type: ignore[arg-type]
            interval=1,
            timeout=1,
            check_only=True,
            do_cherry=False,
            do_triage=False,
            session_started_at="",
            session_started_ns=start_ns,
        )

        assert result.session_elapsed_s >= 65, "session_elapsed_s must be greater than zero"
        assert result.session_elapsed_str != "", "Result must not be empty"
        assert "s" in result.session_elapsed_str, "Result must not be empty"
        assert result.session_elapsed_str.endswith("ns"), "Result must not be empty"
        assert result.current_dt != "", "Result must not be empty"
        assert result.session_started_ns == start_ns, "Result must not be empty"
