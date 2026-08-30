"""Tests for scripts/ci/rate_limit_handler.py and push_conflict_resolver.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Ensure scripts/ci is on the path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "ci"))

import push_conflict_resolver as pcr
import rate_limit_handler as rlh

# ── rate_limit_handler tests ────────────────────────────────────────────────────


class TestIsRateLimitError:
    def test_detects_user_weekly_rate_limited_code(self):
        assert rlh.is_rate_limit_error({"code": "user_weekly_rate_limited"}), "Error should be raised or set"

    def test_detects_429_status(self):
        assert rlh.is_rate_limit_error({"status": "429"}), "Error should be raised or set"

    def test_detects_message_phrase(self):
        assert rlh.is_rate_limit_error({"message": "You've exceeded your weekly rate limit."}), "Error should be raised or set"

    def test_detects_text_phrase(self):
        assert rlh.is_rate_limit_error({"text": "reset in 6 hours 5 minutes"}), "Error should be raised or set"

    def test_rejects_unrelated_error(self):
        assert not rlh.is_rate_limit_error({"code": "not_found", "message": "repo missing"})

    def test_empty_payload_is_not_rate_limit(self):
        assert not rlh.is_rate_limit_error({}), "Error should be raised or set"


class TestExtractResetMinutes:
    def test_hours_and_minutes(self):
        minutes = rlh.extract_reset_minutes({"text": "reset in 6 hours 5 minutes"})
        assert minutes == 6 * 60 + 5, "minutes is not valid"

    def test_hours_only(self):
        minutes = rlh.extract_reset_minutes({"text": "reset in 2 hours"})
        assert minutes == 120, "minutes is not valid"

    def test_minutes_only(self):
        minutes = rlh.extract_reset_minutes({"text": "reset in 45 minutes"})
        assert minutes == 45, "minutes is not valid"

    def test_missing_returns_none(self):
        assert rlh.extract_reset_minutes({"text": "unknown error"}) is None, "Error should be raised or set"

    def test_searches_message_field_too(self):
        minutes = rlh.extract_reset_minutes({"message": "reset in 1 hour 30 minutes"})
        assert minutes == 90, "minutes is not valid"


class TestSaveCheckpoint:
    def test_creates_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(rlh, "CHECKPOINT_FILE", tmp_path / "cp.json")
        cp = rlh.save_checkpoint(
            pr_number=4389,
            error_data={"code": "user_weekly_rate_limited", "text": "reset in 6 hours 5 minutes"},
            completed=["Fix A"],
            in_progress=["Fix B"],
            pending=["Fix C", "Fix D"],
            session="S923",
        )
        assert (tmp_path / "cp.json").exists(), "Condition must be true"
        assert cp["pr_number"] == 4389, "Condition must be true"
        assert cp["session"] == "S923", "Condition must be true"
        assert cp["resolution"] == "pending", "Condition must be true"
        assert cp["tasks"]["completed"] == ["Fix A"], "Condition must be true"
        assert cp["tasks"]["in_progress"] == ["Fix B"], "Condition must be true"
        assert cp["tasks"]["pending"] == ["Fix C", "Fix D"]
        assert cp["rate_limit"]["reset_minutes"] == 365, "Condition must be true"

    def test_schema_version_present(self, tmp_path, monkeypatch):
        monkeypatch.setattr(rlh, "CHECKPOINT_FILE", tmp_path / "cp.json")
        cp = rlh.save_checkpoint(4389, {}, [], [], [])
        assert "schema_version" in cp, "Condition must be true"

    def test_push_conflict_risk_documented(self, tmp_path, monkeypatch):
        monkeypatch.setattr(rlh, "CHECKPOINT_FILE", tmp_path / "cp.json")
        cp = rlh.save_checkpoint(4389, {}, [], [], [])
        assert "push_conflict_risk" in cp, "Condition must be true"
        assert "resolver_script" in cp["push_conflict_risk"], "Condition must be true"


class TestLoadCheckpoint:
    def test_returns_none_when_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(rlh, "CHECKPOINT_FILE", tmp_path / "nonexistent.json")
        assert rlh.load_checkpoint() is None, "Condition must be true"

    def test_returns_dict_when_present(self, tmp_path, monkeypatch):
        cp_path = tmp_path / "cp.json"
        cp_path.write_text(json.dumps({"pr_number": 4389, "resolution": "pending"}))
        monkeypatch.setattr(rlh, "CHECKPOINT_FILE", cp_path)
        result = rlh.load_checkpoint()
        assert result["pr_number"] == 4389, "pr_number must round-trip from file"
        assert result["resolution"] == "pending", "resolution must round-trip from file"

    def test_returns_none_on_corrupt_json(self, tmp_path, monkeypatch):
        cp_path = tmp_path / "cp.json"
        cp_path.write_text("{bad json")
        monkeypatch.setattr(rlh, "CHECKPOINT_FILE", cp_path)
        assert rlh.load_checkpoint() is None, "Condition must be true"


class TestMarkCheckpointResolved:
    def test_marks_resolved(self, tmp_path, monkeypatch):
        cp_path = tmp_path / "cp.json"
        cp_path.write_text(json.dumps({"pr_number": 4389, "resolution": "pending"}))
        monkeypatch.setattr(rlh, "CHECKPOINT_FILE", cp_path)
        rlh.mark_checkpoint_resolved(session="S924")
        result = json.loads(cp_path.read_text())
        assert result["resolution"] == "resolved", "Result must not be empty"
        assert result["resolved_by_session"] == "S924", "Result must not be empty"
        assert "resolved_at" in result, "Result must not be empty"


class TestPostPrComment:
    def test_skips_when_no_token(self, tmp_path, monkeypatch):
        monkeypatch.setattr(rlh, "REPO", "")
        monkeypatch.setattr(rlh, "GH_TOKEN", "")
        cp = {"rate_limit": {}, "tasks": {}, "session": "S923"}
        result = rlh.post_pr_comment(4389, cp)
        assert result is False, "Result must not be empty"

    def test_posts_new_comment(self, monkeypatch):
        monkeypatch.setattr(rlh, "REPO", "Aries-Serpent/_codex_")
        monkeypatch.setattr(rlh, "GH_TOKEN", "fake-token")
        calls = []

        def fake_gh_api(method, path, body=None):
            calls.append((method, path))
            if method == "GET":
                return 200, []  # no existing comment
            return 201, {"id": 999}

        monkeypatch.setattr(rlh, "_gh_api", fake_gh_api)
        cp = {
            "rate_limit": {"request_id": "REQ-1", "retry_after_utc": "2026-05-10T10:00Z"},
            "tasks": {"completed": ["A"], "in_progress": ["B"], "pending": ["C"]},
            "session": "S923",
            "created_at": "2026-05-10T04:00:00Z",
        }
        result = rlh.post_pr_comment(4389, cp)
        assert result is True, "Result must not be empty"
        assert any("POST" in str(c) for c in calls), "Condition must be true"

    def test_updates_existing_comment(self, monkeypatch):
        monkeypatch.setattr(rlh, "REPO", "Aries-Serpent/_codex_")
        monkeypatch.setattr(rlh, "GH_TOKEN", "fake-token")

        def fake_gh_api(method, path, body=None):
            if method == "GET":
                return 200, [{"id": 42, "body": "<!-- codex-rate-limit-checkpoint -->"}]
            return 200, {}

        monkeypatch.setattr(rlh, "_gh_api", fake_gh_api)
        cp = {
            "rate_limit": {"request_id": "REQ-1", "retry_after_utc": "2026-05-10T10:00Z"},
            "tasks": {"completed": [], "in_progress": [], "pending": []},
            "session": "S923",
            "created_at": "2026-05-10T04:00:00Z",
        }
        result = rlh.post_pr_comment(4389, cp)
        assert result is True, "Result must not be empty"


# ── push_conflict_resolver tests ────────────────────────────────────────────────


class TestResolveKnownConflicts:
    def test_prefer_theirs_for_manifest(self, tmp_path, monkeypatch):
        manifest = tmp_path / "CODEX_MANIFEST.json"
        manifest.write_text("{}")
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            r = MagicMock()
            r.returncode = 0
            r.stdout = ""
            return r

        monkeypatch.setattr(pcr, "_run", fake_run)
        resolved, unresolved = pcr._resolve_known_conflicts(["CODEX_MANIFEST.json"])
        assert any("THEIRS:CODEX_MANIFEST.json" == r for r in resolved), "Condition must be true"
        assert not unresolved, "Condition must be true"

    def test_prefer_ours_for_secrets_baseline(self, monkeypatch):
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            r = MagicMock()
            r.returncode = 0
            r.stdout = ""
            return r

        monkeypatch.setattr(pcr, "_run", fake_run)
        resolved, unresolved = pcr._resolve_known_conflicts([".secrets.baseline"])
        assert any("OURS:.secrets.baseline" == r for r in resolved), "Condition must be true"
        assert not unresolved, "Condition must be true"

    def test_unknown_file_is_unresolved(self, monkeypatch):
        resolved, unresolved = pcr._resolve_known_conflicts(["src/my_module.py"])
        assert not resolved, "Condition must be true"
        assert "src/my_module.py" in unresolved, "Condition must be true"

    def test_dry_run_makes_no_calls(self, monkeypatch):
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            r = MagicMock()
            r.returncode = 0
            r.stdout = ""
            return r

        monkeypatch.setattr(pcr, "_run", fake_run)
        pcr._resolve_known_conflicts(["CODEX_MANIFEST.json"], dry_run=True)
        assert not calls, "Condition must be true"


class TestResolveUpToDate:
    """Test resolve() when branch is already up-to-date."""

    def test_no_op_when_up_to_date(self, monkeypatch):
        def fake_run(cmd, **kwargs):
            r = MagicMock()
            r.returncode = 0
            if "rev-list" in cmd:
                r.stdout = "0"
            elif "rev-parse" in cmd:
                r.stdout = "copilot/my-branch"
            else:
                r.stdout = ""
            return r

        monkeypatch.setattr(pcr, "_run", fake_run)
        result = pcr.resolve(branch="copilot/my-branch")
        assert result["success"] is True, "Result must not be empty"
        assert result["action"] == "no-op", "Result must not be empty"
        assert result["commits_behind"] == 0, "Result must not be empty"

    def test_fetch_failure_reported(self, monkeypatch):
        def fake_run(cmd, **kwargs):
            r = MagicMock()
            if "fetch" in cmd:
                r.returncode = 1
                r.stderr = "network error"
            else:
                r.returncode = 0
                r.stdout = ""
            return r

        monkeypatch.setattr(pcr, "_run", fake_run)
        result = pcr.resolve(branch="my-branch")
        assert result["success"] is False, "Result must not be empty"
        assert result["action"] == "fetch-failed", "Result must not be empty"

    def test_dry_run_reports_behind(self, monkeypatch):
        def fake_run(cmd, **kwargs):
            r = MagicMock()
            r.returncode = 0
            if "rev-list" in cmd:
                r.stdout = "3"
            elif "rev-parse" in cmd:
                r.stdout = "my-branch"
            else:
                r.stdout = ""
            return r

        monkeypatch.setattr(pcr, "_run", fake_run)
        result = pcr.resolve(branch="my-branch", dry_run=True)
        assert result["action"] == "dry-run", "Result must not be empty"
        assert result["commits_behind"] == 3, "Result must not be empty"
        assert result["success"] is False, "Result must not be empty"
