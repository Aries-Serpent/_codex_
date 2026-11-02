"""Offline evidence and side-effect boundaries for the proactive monitor."""

from __future__ import annotations

import importlib.util
import sys
import urllib.error
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/ci/proactive_ci_monitor.py"
spec = importlib.util.spec_from_file_location("proactive_ci_monitor_integrity", SCRIPT)
assert spec is not None and spec.loader is not None
monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor)


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def denied(*args, **kwargs):
        pytest.fail("Real network access is forbidden in monitor fixtures")

    monkeypatch.setattr(monitor.urllib.request, "urlopen", denied)
    monkeypatch.setattr(monitor, "_CI_HEALTH_AVAILABLE", False)


def snapshot(status="passed", *, complete=True, name="lint"):
    return {"complete": complete, "checks": [{"name": name, "status": status}]}


@pytest.mark.parametrize("iterations", [0, -1, True, 1.5, "2"])
def test_positive_iterations_required(iterations):
    with pytest.raises(ValueError, match="positive integer"):
        monitor.monitor_until_converged(snapshot, max_iterations=iterations)


@pytest.mark.parametrize("status", ["missing", "info", "unknown", "failure", "queued"])
def test_nonpositive_evidence_never_converges(status):
    result = monitor.monitor_until_converged(
        lambda: snapshot(status), max_iterations=2, required_checks=["lint"]
    )
    assert not result["converged"]
    assert result["exit_code"] != 0
    assert result["iterations"] == 2


def test_missing_required_check_never_converges():
    result = monitor.monitor_until_converged(snapshot, required_checks=["lint", "tests"])
    assert not result["converged"]


@pytest.mark.parametrize("data", [{"complete": True, "checks": []}, snapshot(complete=False)])
def test_empty_or_incomplete_not_green(data):
    result = monitor.monitor_until_converged(lambda: data)
    assert not result["converged"]
    assert result["exit_code"] == 1


def test_reader_only_bounded_convergence(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Read-only convergence must not call GitHub or post comments")

    monkeypatch.setattr(monitor, "_gh", forbidden)
    monkeypatch.setattr(monitor, "_post_rescue_comment", forbidden)
    states = iter([snapshot("info"), snapshot("passed")])
    result = monitor.monitor_until_converged(
        lambda: next(states), max_iterations=3, required_checks=["lint"]
    )
    assert result["converged"]
    assert result["iterations"] == 2
    assert result["exit_code"] == 0
    assert result["read_only"]
    assert result["pending_integrations"] == ["maintained-health", "evolution", "local-fixer"]


def test_reader_denial_is_explicit_nonzero():
    def reader():
        raise urllib.error.HTTPError("fixture", 403, "Forbidden", {}, None)

    result = monitor.monitor_until_converged(reader, max_iterations=3)
    assert result["exit_code"] == 1
    assert result["iterations"] == 1
    assert result["errors"] == ["Reader failed: HTTP 403"]


@pytest.fixture
def api(monkeypatch):
    pr = {"number": 7, "head": {"sha": "abcdef1234567890"}}
    run = {"id": 12, "name": "ModuleNotFoundError", "conclusion": "failure"}
    requests = []

    def reader(path, token, method="GET", body=None):
        requests.append((path, method))
        if method == "POST":
            return {"id": 10}
        if "/pulls?" in path:
            return [pr]
        if "/jobs?" in path:
            return {"jobs": []}
        if "/actions/runs?" in path:
            return {"workflow_runs": [run], "total_count": 1}
        if "/comments?" in path:
            return []
        raise AssertionError(path)

    monkeypatch.setattr(monitor, "_gh", reader)
    return reader, requests


def test_dry_run_counts_plans_not_posts(api):
    _, requests = api
    result = monitor.scan("fixture/repo", "fixture", True, 24)
    assert result["complete"]
    assert result["escalated"] == 0
    assert result["planned"] == 1
    assert result["details"][0]["action"] == "dry-run"
    assert all(method == "GET" for _, method in requests)


@pytest.mark.parametrize("post_fails", [False, True])
def test_only_successful_post_counts_as_escalated(api, monkeypatch, post_fails):
    reader, _ = api

    def replacement(path, token, method="GET", body=None):
        if method == "POST" and post_fails:
            raise urllib.error.HTTPError("fixture", 403, "Forbidden", {}, None)
        return reader(path, token, method, body)

    monkeypatch.setattr(monitor, "_gh", replacement)
    result = monitor.scan("fixture/repo", "fixture", False, 24)
    assert result["escalated"] == int(not post_fails)
    assert result["complete"] is not post_fails
    assert result["details"][0]["action"] == ("post-failed" if post_fails else "escalated")


@pytest.mark.parametrize("denied_endpoint", ["/pulls", "/actions/runs?", "/jobs?", "/comments?"])
def test_denied_reads_are_incomplete_and_do_not_post(api, monkeypatch, denied_endpoint):
    reader, requests = api

    def replacement(path, token, method="GET", body=None):
        if denied_endpoint in path:
            raise urllib.error.HTTPError("fixture", 403, "Forbidden", {}, None)
        return reader(path, token, method, body)

    monkeypatch.setattr(monitor, "_gh", replacement)
    result = monitor.scan("fixture/repo", "fixture", False, 24)
    assert not result["complete"]
    assert result["exit_code"] == 1
    assert result["errors"]
    assert "HTTP 403" in result["errors"][0]
    assert result["escalated"] == 0
    assert all(method == "GET" for _, method in requests)


def test_comments_second_page_prevents_duplicate(monkeypatch):
    paths = []

    def reader(path, token):
        paths.append(path)
        if path.endswith("page=1"):
            return [{"body": "unrelated"} for _ in range(100)]
        return [{"body": "<!-- proactive-ci-monitor:abcdef123456:12 -->"}]

    monkeypatch.setattr(monitor, "_gh", reader)
    assert monitor._existing_rescue_comment("fixture/repo", 7, "abcdef123456", 12, "fixture")
    assert len(paths) == 2


def test_workflow_run_pagination(monkeypatch):
    def reader(path, token):
        if path.endswith("page=1"):
            return {"workflow_runs": [{"id": i} for i in range(50)], "total_count": 51}
        return {"workflow_runs": [{"id": 50}], "total_count": 51}

    monkeypatch.setattr(monitor, "_gh", reader)
    assert len(monitor._latest_runs_for_sha("fixture/repo", "sha", "fixture")) == 51


@pytest.mark.parametrize(
    "response",
    [{"workflow_runs": [], "total_count": 2}, {"workflow_runs": None}],
)
def test_incomplete_pagination_rejected(monkeypatch, response):
    monkeypatch.setattr(monitor, "_gh", lambda *args: response)
    with pytest.raises(ValueError):
        monitor._latest_runs_for_sha("fixture/repo", "sha", "fixture")


def test_denial_on_later_page_is_not_partial_success(api, monkeypatch):
    reader, requests = api

    def replacement(path, token, method="GET", body=None):
        if "/actions/runs?" in path:
            if path.endswith("page=2"):
                raise urllib.error.HTTPError("fixture", 403, "Forbidden", {}, None)
            return {"workflow_runs": [{"id": i} for i in range(50)], "total_count": 51}
        return reader(path, token, method, body)

    monkeypatch.setattr(monitor, "_gh", replacement)
    result = monitor.scan("fixture/repo", "fixture", False, 24)
    assert not result["complete"]
    assert result["exit_code"] == 1
    assert result["errors"] == ["PR #7 runs: HTTP 403"]
    assert all(method == "GET" for _, method in requests)


def test_pagination_budget_exhaustion_is_explicit(monkeypatch):
    monkeypatch.setattr(monitor, "_gh", lambda *args: [{"body": ""}] * 100)
    with pytest.raises(ValueError, match="Pagination limit reached"):
        monitor._existing_rescue_comment("fixture/repo", 7, "sha", 12, "fixture")


def test_target_pr_denied_read_is_incomplete(api, monkeypatch):
    def denied(*args, **kwargs):
        raise urllib.error.HTTPError("fixture", 403, "Forbidden", {}, None)

    monkeypatch.setattr(monitor, "_gh", denied)
    result = monitor.scan("fixture/repo", "fixture", True, 24, target_pr=7)
    assert not result["complete"]
    assert result["exit_code"] == 1
    assert result["errors"] == ["PR #7: HTTP 403"]


def test_cli_incomplete_scan_nonzero(api, monkeypatch, capsys):
    monkeypatch.setattr(
        monitor,
        "_list_open_prs",
        lambda *args: (_ for _ in ()).throw(ValueError("Incomplete pagination")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["monitor", "--repo", "fixture/repo", "--token", "fixture", "--dry-run"],
    )
    assert monitor.main() == 1
    assert '"complete": false' in capsys.readouterr().out
