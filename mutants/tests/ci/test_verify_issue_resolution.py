"""
tests/ci/test_verify_issue_resolution.py
═════════════════════════════════════════

Unit tests for scripts/ci/verify_issue_resolution.py.

All GitHub API calls are mocked — no live network required.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# ── Load the module under test ────────────────────────────────────────────────

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "ci" / "verify_issue_resolution.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("verify_issue_resolution", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    # Register before exec so @dataclass can resolve the module dict
    sys.modules["verify_issue_resolution"] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


vir = _load_module()
Status = vir.Status


# ── Helpers ───────────────────────────────────────────────────────────────────


def _fake_issue(
    *, state: str = "open", title: str = "Bug report", labels: list[str] | None = None
) -> dict:
    return {
        "number": 3951,
        "title": title,
        "state": state,
        "state_reason": "completed" if state == "closed" else None,
        "body": "Some issue body text",
        "labels": [{"name": lb} for lb in (labels or [])],
        "html_url": "https://github.com/Aries-Serpent/_codex_/issues/3951",
    }


def _fake_pr(
    *,
    merged: bool = False,
    state: str = "open",
    mergeable_state: str = "clean",
    title: str = "Fix: something",
    sha: str = "abc123def456",  # pragma: allowlist secret
) -> dict:
    return {
        "number": 3954,
        "title": title,
        "state": state,
        "merged": merged,
        "merged_at": "2026-04-13T00:00:00Z" if merged else None,
        "mergeable_state": mergeable_state,
        "head": {"sha": sha},
        "html_url": "https://github.com/Aries-Serpent/_codex_/pull/3954",
    }


def _fake_run(*, status: str = "completed", conclusion: str = "success") -> dict:
    return {
        "id": 12345,
        "name": "Validation Pipeline",
        "display_title": "PR push",
        "status": status,
        "conclusion": conclusion,
        "html_url": "https://github.com/Aries-Serpent/_codex_/actions/runs/12345",
    }


# ── URL parsing ───────────────────────────────────────────────────────────────


def test_parse_issue_url():
    owner, repo, kind, num = vir.parse_url("https://github.com/Aries-Serpent/_codex_/issues/3951")
    assert owner == "Aries-Serpent", "owner is not valid"
    assert repo == "_codex_", "repo is not valid"
    assert kind == "issue", "kind is not valid"
    assert num == "3951", "num is not valid"


def test_parse_pr_url():
    _owner, _repo, kind, num = vir.parse_url("https://github.com/Aries-Serpent/_codex_/pull/3954")
    assert kind == "pr", "kind is not valid"
    assert num == "3954", "num is not valid"


def test_parse_run_url():
    _owner, _repo, kind, num = vir.parse_url(
        "https://github.com/Aries-Serpent/_codex_/actions/runs/99999"
    )
    assert kind == "run", "kind is not valid"
    assert num == "99999", "num is not valid"


def test_parse_invalid_url_raises():
    with pytest.raises(ValueError):
        vir.parse_url("https://example.com/something")


def test_build_url_issue():
    url = vir.build_url("Aries-Serpent", "_codex_", "issue", 3951)
    assert url == "https://github.com/Aries-Serpent/_codex_/issues/3951", "url is not valid"


# ── Issue verifier ────────────────────────────────────────────────────────────


def test_verify_issue_closed():
    with patch.object(vir, "_api_safe") as mock_api:
        mock_api.side_effect = [
            _fake_issue(state="closed"),  # get issue
            [],  # events
        ]
        result = vir.verify_issue("Aries-Serpent", "_codex_", 3951, token=None)

    assert result.status == Status.RESOLVED, "Result must not be empty"
    assert "closed" in result.reason.lower(), "Result must not be empty"
    assert result.resolved is True, "Result must not be empty"


def test_verify_issue_open_no_fix():
    with (
        patch.object(vir, "_api_safe") as mock_api,
        patch.object(vir, "_paginated", return_value=[]),
    ):
        mock_api.return_value = _fake_issue(state="open")
        result = vir.verify_issue("Aries-Serpent", "_codex_", 3951, token=None)

    assert result.status == Status.UNRESOLVED, "Result must not be empty"
    assert result.resolved is False, "Result must not be empty"


def test_verify_issue_open_with_merged_linked_pr():
    events = [
        {
            "event": "cross-referenced",
            "source": {
                "issue": {
                    "state": "closed",
                    "html_url": "https://github.com/Aries-Serpent/_codex_/pull/3954",
                    "pull_request": {"merged_at": "2026-04-10T00:00:00Z"},
                }
            },
        }
    ]
    with (
        patch.object(vir, "_api_safe", return_value=_fake_issue(state="open")),
        patch.object(vir, "_paginated", return_value=events),
    ):
        result = vir.verify_issue("Aries-Serpent", "_codex_", 3951, token=None)

    assert result.status == Status.RESOLVED, "Result must not be empty"
    assert "merged pr" in result.reason.lower(), "Result must not be empty"


def test_verify_issue_api_error_returns_unknown():
    with patch.object(vir, "_api_safe", return_value=None):
        result = vir.verify_issue("Aries-Serpent", "_codex_", 9999, token=None)

    assert result.status == Status.UNKNOWN, "Result must not be empty"


# ── PR verifier ───────────────────────────────────────────────────────────────


def test_verify_pr_merged():
    with (
        patch.object(vir, "_api_safe", return_value=_fake_pr(merged=True)),
        patch.object(vir, "_check_required_ci", return_value=None),
    ):
        result = vir.verify_pr("Aries-Serpent", "_codex_", 3954, token=None)

    assert result.status == Status.RESOLVED, "Result must not be empty"
    assert result.resolved is True, "Result must not be empty"


def test_verify_pr_conflict():
    with patch.object(vir, "_api_safe", return_value=_fake_pr(mergeable_state="dirty")):
        result = vir.verify_pr("Aries-Serpent", "_codex_", 3954, token=None)

    assert result.status == Status.CONFLICTED, "Result must not be empty"
    assert result.resolved is False, "Result must not be empty"


def test_verify_pr_blocked_by_ci():
    ci_summary = {
        "total": 5,
        "passed": 3,
        "failed": 2,
        "pending": 0,
        "skipped": 0,
        "all_pass": False,
        "any_fail": True,
        "any_pending": False,
        "details": ["  ❌ validate.yml — failure"],
    }
    with patch.object(vir, "_api_safe", return_value=_fake_pr()):
        with patch.object(vir, "_check_required_ci", return_value=ci_summary):
            result = vir.verify_pr("Aries-Serpent", "_codex_", 3954, token=None)

    assert result.status == Status.BLOCKED, "Result must not be empty"
    assert result.resolved is False, "Result must not be empty"


def test_verify_pr_clean_all_pass():
    ci_summary = {
        "total": 5,
        "passed": 5,
        "failed": 0,
        "pending": 0,
        "skipped": 0,
        "all_pass": True,
        "any_fail": False,
        "any_pending": False,
        "details": [],
    }
    with patch.object(vir, "_api_safe", return_value=_fake_pr(mergeable_state="clean")):
        with patch.object(vir, "_check_required_ci", return_value=ci_summary):
            result = vir.verify_pr("Aries-Serpent", "_codex_", 3954, token=None)

    assert result.status == Status.READY, "Result must not be empty"
    assert result.resolved is True, "Result must not be empty"


def test_verify_pr_pending_ci():
    ci_summary = {
        "total": 5,
        "passed": 3,
        "failed": 0,
        "pending": 2,
        "skipped": 0,
        "all_pass": False,
        "any_fail": False,
        "any_pending": True,
        "details": ["  ⏳ validate.yml — in_progress"],
    }
    with patch.object(vir, "_api_safe", return_value=_fake_pr()):
        with patch.object(vir, "_check_required_ci", return_value=ci_summary):
            result = vir.verify_pr("Aries-Serpent", "_codex_", 3954, token=None)

    assert result.status == Status.IN_PROGRESS, "Result must not be empty"
    assert result.resolved is False, "Result must not be empty"


# ── Workflow run verifier ─────────────────────────────────────────────────────


def test_verify_run_success():
    with patch.object(vir, "_api_safe", return_value=_fake_run(conclusion="success")):
        result = vir.verify_run("Aries-Serpent", "_codex_", 12345, token=None)

    assert result.status == Status.RESOLVED, "Result must not be empty"
    assert result.resolved is True, "Result must not be empty"


def test_verify_run_failure():
    with patch.object(vir, "_api_safe", return_value=_fake_run(conclusion="failure")):
        result = vir.verify_run("Aries-Serpent", "_codex_", 12345, token=None)

    assert result.status == Status.UNRESOLVED, "Result must not be empty"
    assert result.resolved is False, "Result must not be empty"


def test_verify_run_in_progress():
    with patch.object(
        vir, "_api_safe", return_value=_fake_run(status="in_progress", conclusion="")
    ):
        result = vir.verify_run("Aries-Serpent", "_codex_", 12345, token=None)

    assert result.status == Status.IN_PROGRESS, "Result must not be empty"
    assert result.resolved is False, "Result must not be empty"


def test_verify_run_action_required():
    with patch.object(vir, "_api_safe", return_value=_fake_run(conclusion="action_required")):
        result = vir.verify_run("Aries-Serpent", "_codex_", 12345, token=None)

    assert result.status == Status.BLOCKED, "Result must not be empty"


# ── verify_all integration ────────────────────────────────────────────────────


def test_verify_all_mixed_urls():
    issue_data = _fake_issue(state="closed")
    pr_data = _fake_pr(merged=True)

    with (
        patch.object(vir, "_api_safe") as mock_api,
        patch.object(vir, "_paginated", return_value=[]),
    ):
        mock_api.side_effect = [
            issue_data,  # issue fetch
            pr_data,  # PR fetch
        ]
        results = vir.verify_all(
            [
                "https://github.com/Aries-Serpent/_codex_/issues/3951",
                "https://github.com/Aries-Serpent/_codex_/pull/3954",
            ]
        )

    assert len(results) == 2, "Results must not be empty"
    assert all(r.resolved for r in results), "Result must not be empty"


def test_verify_all_invalid_url_returns_unknown():
    results = vir.verify_all(["https://example.com/not-github"])
    assert len(results) == 1, "Results must not be empty"
    assert results[0].status == Status.UNKNOWN, "Result must not be empty"


# ── Output formatters ─────────────────────────────────────────────────────────


def test_format_text_all_resolved():
    results = [
        vir.VerificationResult(
            url="https://github.com/Aries-Serpent/_codex_/issues/3951",
            kind="issue",
            number=3951,
            title="Bug: CI failure",
            status=Status.RESOLVED,
            reason="Issue is closed (completed)",
        )
    ]
    text = vir.format_text(results)
    assert "RESOLVED" in text, "Condition must be true"
    assert "ALL RESOLVED" in text, "Condition must be true"


def test_format_text_unresolved():
    results = [
        vir.VerificationResult(
            url="https://github.com/Aries-Serpent/_codex_/issues/3951",
            kind="issue",
            number=3951,
            title="Bug: open",
            status=Status.UNRESOLVED,
            reason="Issue is open",
        )
    ]
    text = vir.format_text(results)
    assert "UNRESOLVED" in text, "Condition must be true"


def test_format_markdown_contains_table():
    results = [
        vir.VerificationResult(
            url="https://github.com/Aries-Serpent/_codex_/issues/3951",
            kind="issue",
            number=3951,
            title="Test issue",
            status=Status.RESOLVED,
            reason="Closed",
        )
    ]
    md = vir.format_markdown(results)
    assert "|" in md, "Condition must be true"
    assert "RESOLVED" in md, "Condition must be true"
    assert "All issues verified resolved" in md, "All is not valid"


# ── VerificationResult serialisation ─────────────────────────────────────────


def test_result_to_dict_roundtrip():
    r = vir.VerificationResult(
        url="https://github.com/Aries-Serpent/_codex_/issues/3951",
        kind="issue",
        number=3951,
        title="My issue",
        status=Status.RESOLVED,
        reason="closed",
        details=["detail1"],
    )
    d = r.to_dict()
    assert d["resolved"] is True, "Condition must be true"
    assert d["status"] == "RESOLVED", "Condition must be true"
    assert d["kind"] == "issue", "Condition must be true"
    # Roundtrip through JSON
    assert json.loads(json.dumps(d))["number"] == 3951, "Condition must be true"


# ── CLI tests ─────────────────────────────────────────────────────────────────


def test_cli_no_args_exits_nonzero():
    with pytest.raises(SystemExit) as exc_info:
        vir.main([])
    assert exc_info.value.code != 0, "Value must be initialized"


def test_cli_resolved_issue_exits_0():
    with (
        patch.object(vir, "_api_safe", return_value=_fake_issue(state="closed")),
        patch.object(vir, "_paginated", return_value=[]),
    ):
        rc = vir.main(
            [
                "--issues",
                "3951",
                "--repo",
                "Aries-Serpent/_codex_",
            ]
        )
    assert rc == 0, "rc is not valid"


def test_cli_unresolved_issue_exits_1():
    with (
        patch.object(vir, "_api_safe", return_value=_fake_issue(state="open")),
        patch.object(vir, "_paginated", return_value=[]),
    ):
        rc = vir.main(
            [
                "--issues",
                "9999",
                "--repo",
                "Aries-Serpent/_codex_",
            ]
        )
    assert rc == 1, "rc is not valid"


def test_cli_json_output(capsys):
    with (
        patch.object(vir, "_api_safe", return_value=_fake_issue(state="closed")),
        patch.object(vir, "_paginated", return_value=[]),
    ):
        rc = vir.main(
            [
                "--issues",
                "3951",
                "--repo",
                "Aries-Serpent/_codex_",
                "--json",
            ]
        )
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)
    assert data[0]["resolved"] is True, "Data must not be empty"
    assert rc == 0, "rc is not valid"


def test_cli_allow_in_progress():
    """--allow-in-progress should make IN_PROGRESS count as resolved."""
    run_data = _fake_run(status="in_progress", conclusion="")
    with patch.object(vir, "_api_safe", return_value=run_data):
        rc = vir.main(
            [
                "--runs",
                "12345",
                "--repo",
                "Aries-Serpent/_codex_",
                "--allow-in-progress",
            ]
        )
    assert rc == 0, "rc is not valid"
