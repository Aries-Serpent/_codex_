"""Negative approval tests use offline REST fixtures, never credentials."""

from copy import deepcopy

import pytest
import yaml

from scripts.ci import approve_pending_runs as approval

SHA = "a" * 40


@pytest.fixture
def api(monkeypatch):
    monkeypatch.setenv("GITHUB_ACTOR", "maintainer-requester")
    monkeypatch.setenv("GITHUB_TRIGGERING_ACTOR", "maintainer-requester")
    pr = {
        "state": "open",
        "head": {"sha": SHA},
        "user": {"login": "author"},
        "labels": [{"name": "wec:auto-approve"}],
    }
    run = {
        "id": 7,
        "head_sha": SHA,
        "conclusion": "action_required",
        "actor": {"login": "author"},
        "triggering_actor": {"login": "author"},
        "pull_requests": [{"number": 1}],
    }
    identity = {"login": "independent-maintainer", "type": "User"}
    responses = {"/user": identity, "/repos/o/r/pulls/1": pr, "/repos/o/r/actions/runs/7": run}
    responses["/repos/o/r/pulls/1/reviews?per_page=100&page=1"] = [
        {
            "user": {"login": "reviewer", "type": "User"},
            "author_association": "MEMBER",
            "state": "APPROVED",
            "commit_id": SHA,
        }
    ]
    calls = []

    def gh(method, path, token, body=None):
        calls.append((method, path))
        if method == "POST":
            return 204, {}
        return (200, deepcopy(responses[path])) if path in responses else (403, {})

    monkeypatch.setattr(approval, "_gh", gh)
    return pr, run, identity, calls


def test_independent_current_labelled_run_authorized(api):
    _, run, _, calls = api
    assert approval._authorize_run("", "o/r", "1", SHA, run) == "authorized"
    assert all(method == "GET" for method, _ in calls)


def test_label_alone_does_not_establish_review(api, monkeypatch):
    _, run, _, _ = api
    gh = approval._gh

    def no_reviews(method, path, token, body=None):
        if "/reviews?" in path:
            return 200, []
        return gh(method, path, token, body)

    monkeypatch.setattr(approval, "_gh", no_reviews)
    assert approval._authorize_run("", "o/r", "1", SHA, run) == "missing-independent-current-review"


@pytest.mark.parametrize("case", ["stale", "self", "bot", "outside", "withdrawn"])
def test_review_evidence_must_be_current_and_independent(api, monkeypatch, case):
    _, run, _, _ = api
    gh = approval._gh

    def reviews(method, path, token, body=None):
        status, data = gh(method, path, token, body)
        if "/reviews?" in path:
            if case == "stale":
                data[0]["commit_id"] = "b" * 40
            elif case == "self":
                data[0]["user"]["login"] = "author"
            elif case == "bot":
                data[0]["user"]["type"] = "Bot"
            elif case == "outside":
                data[0]["author_association"] = "NONE"
            else:
                data.append({**data[0], "state": "CHANGES_REQUESTED"})
        return status, data

    monkeypatch.setattr(approval, "_gh", reviews)
    assert approval._authorize_run("", "o/r", "1", SHA, run) == "missing-independent-current-review"


@pytest.mark.parametrize(
    "case,expected",
    [
        ("no-label", "missing-or-expired-label"),
        ("stale-pr", "stale-head-sha"),
        ("stale-run", "stale-head-sha"),
        ("self", "self-approval"),
        ("bot", "unknown-approver-identity"),
        ("closed", "stale-head-sha"),
    ],
)
def test_negative_authorization(api, case, expected):
    pr, run, identity, calls = api
    if case == "no-label":
        pr["labels"] = []
    elif case == "stale-pr":
        pr["head"]["sha"] = "b" * 40
    elif case == "stale-run":
        run["head_sha"] = "b" * 40
    elif case == "self":
        identity["login"] = "author"
    elif case == "bot":
        identity["type"] = "Bot"
    else:
        pr["state"] = "closed"
    assert approval._authorize_run("", "o/r", "1", SHA, run) == expected
    assert all(method == "GET" for method, _ in calls)


def test_no_rerun_fallback(monkeypatch):
    calls = []
    monkeypatch.setattr(
        approval, "_gh", lambda method, path, token: calls.append(path) or (403, {})
    )
    assert approval._approve_run("", "o/r", {"id": 7}) == "error"
    assert calls == ["/repos/o/r/actions/runs/7/approve"]


def test_author_rerunning_approver_is_denied(api, monkeypatch):
    _, run, _, _ = api
    monkeypatch.setenv("GITHUB_TRIGGERING_ACTOR", "author")
    assert approval._authorize_run("", "o/r", "1", SHA, run) == "self-approval"


@pytest.mark.parametrize(
    "associations", [None, [], [{"number": 2}], [{"number": 1}, {"number": 2}]]
)
def test_pr_association_must_be_unambiguous(api, associations):
    _, run, _, _ = api
    run["pull_requests"] = associations
    assert (
        approval._authorize_run("", "o/r", "1", SHA, run) == "unknown-or-mismatched-pr-association"
    )


def test_explicit_denial_precedes_token_resolution(monkeypatch):
    monkeypatch.setenv("APPROVAL_INTENT", "force_deny")
    monkeypatch.setattr(approval, "_resolve_token", lambda: pytest.fail("must not resolve tokens"))
    decisions = []
    assert approval._run_decisions(decisions) == 1
    assert decisions[0]["rule"] == "explicit-denial"


def test_missing_pr_denied_and_recorded(monkeypatch, tmp_path):
    import json

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("REPO", "o/r")
    monkeypatch.setenv("HEAD_SHA", SHA)
    monkeypatch.delenv("PR_NUMBER", raising=False)
    monkeypatch.setattr(
        approval, "_resolve_token", lambda: pytest.fail("must deny before token resolution")
    )
    assert approval.main() == 1
    assert (
        json.loads((tmp_path / "approval-decision.json").read_text())["decisions"][0]["rule"]
        == "missing-pr"
    )


def test_legacy_workflow_bypasses_unreachable():
    from pathlib import Path

    workflow = yaml.safe_load(
        (
            Path(__file__).resolve().parents[2] / ".github/workflows/auto-approve-workflows.yml"
        ).read_text()
    )
    for job in workflow["jobs"].values():
        for step in job.get("steps", []):
            source = step.get("run", "") + step.get("with", {}).get("script", "")
            if (
                "gh run approve" in source
                or "approveWorkflowRun" in source
                or "git push" in source
                or "gh label create" in source
            ):
                assert step.get("if") == "${{ false }}"
    push = workflow["jobs"]["approve-on-push"]
    approve = next(
        step for step in push["steps"] if step["name"] == "Approve pending runs (if PR found)"
    )
    assert "exit 0" not in approve["run"]
    assert "approval_source == ''" in workflow["jobs"]["approve-original"]["if"]
    for job_id in ("approve-on-push", "evaluate-approval", "execute-approval", "approve-original"):
        checkout = next(
            step
            for step in workflow["jobs"][job_id]["steps"]
            if step.get("uses", "").startswith("actions/checkout@")
        )
        assert checkout["with"]["ref"] == "${{ github.event.repository.default_branch }}"


def test_preliminary_inspection_failure_is_recorded(monkeypatch, tmp_path):
    import json
    import sys
    from scripts.ci import require_wec_auto_approve as gate

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys, "argv", ["gate", "--pr-number", "1", "--repo", "o/r", "--token", "fixture"]
    )

    def unavailable(*args):
        raise OSError("fixture network unavailable")

    monkeypatch.setattr(gate, "has_wec_auto_approve", unavailable)
    assert gate.main() == 1
    assert (
        json.loads((tmp_path / "approval-decision.json").read_text())["decisions"][0]["rule"]
        == "inspection-error"
    )
