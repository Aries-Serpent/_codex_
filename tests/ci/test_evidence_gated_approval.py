"""Negative approval tests use offline REST fixtures, never credentials."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone

import pytest
import yaml

from scripts.ci import approve_pending_runs as approval
from scripts.ci import require_wec_auto_approve as label_gate
from scripts.ci import verify_owner_approval as owner_gate

SHA = "a" * 40


@pytest.fixture
def api(monkeypatch):
    monkeypatch.setenv("GITHUB_ACTOR", "maintainer-requester")
    monkeypatch.setenv("GITHUB_TRIGGERING_ACTOR", "maintainer-requester")
    pr = {
        "number": 1,
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


def test_only_trusted_workflow_run_approval_remains():
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
    assert "pull_request_target" in workflow["on"]
    assert "push" not in workflow["on"]
    assert "pull_request" not in workflow["on"]
    job = workflow["jobs"]["approve-original"]
    assert "endsWith(github.workflow_ref" in job["if"]
    checkout = next(
        step for step in job["steps"] if step.get("uses", "").startswith("actions/checkout@")
    )
    assert checkout["with"]["ref"] == "${{ github.workflow_sha }}"
    assert checkout["with"]["persist-credentials"] is False
    assert "environment" not in job
    assert job["permissions"]["contents"] == "read"


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


@pytest.mark.parametrize(
    "event_name", ["pull_request_target", "workflow_run", "issue_comment", "schedule"]
)
def test_automatic_inspection_is_not_self_approval(api, monkeypatch, event_name):
    _, run, identity, _ = api
    monkeypatch.setenv("GITHUB_EVENT_NAME", event_name)
    monkeypatch.setenv("GITHUB_ACTOR", "author")
    monkeypatch.setenv("GITHUB_TRIGGERING_ACTOR", "author")
    assert approval._authorize_run("", "o/r", "1", SHA, run) == "authorized"
    identity["login"] = "author"
    assert approval._authorize_run("", "o/r", "1", SHA, run) == "self-approval"


@pytest.mark.parametrize("event_name", ["pull_request_target", "workflow_run", "issue_comment"])
def test_trusted_event_resolves_exact_pr_head(api, monkeypatch, tmp_path, event_name):
    import json

    _, run, _, _ = api
    event = {
        "pull_request": {"number": 1, "head": {"sha": SHA}},
        "issue": {"number": 1, "pull_request": {"url": "fixture"}},
        "workflow_run": {"id": run["id"]},
    }
    # REST PR fixtures also carry their number.
    gh = approval._gh

    def numbered_pr(method, path, token, body=None):
        status, data = gh(method, path, token, body)
        if path == "/repos/o/r/pulls/1":
            data["number"] = 1
        return status, data

    monkeypatch.setattr(approval, "_gh", numbered_pr)
    path = tmp_path / "event.json"
    path.write_text(json.dumps(event))
    monkeypatch.setenv("GITHUB_EVENT_NAME", event_name)
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(path))
    assert approval._event_target("", "o/r") == ("1", SHA)


def test_workflow_event_rejects_ambiguous_association(api, monkeypatch, tmp_path):
    _, run, _, _ = api
    run["pull_requests"] = [{"number": 1}, {"number": 2}]
    path = tmp_path / "event.json"
    path.write_text('{"workflow_run": {"id": 7}}')
    monkeypatch.setenv("GITHUB_EVENT_NAME", "workflow_run")
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(path))
    with pytest.raises(RuntimeError, match="ambiguous"):
        approval._event_target("", "o/r")


def test_invalid_primary_pat_does_not_hide_valid_backup(monkeypatch):
    monkeypatch.delenv("GITHUB_APP_PRIVATE_KEY", raising=False)
    monkeypatch.setenv("CODEX_MASTER_KEY", "invalid-fixture")
    monkeypatch.setenv("CODEX_BACKUP_KEY", "valid-fixture")
    monkeypatch.setattr(
        approval,
        "_gh",
        lambda method, path, token: (
            (401, {})
            if token == "invalid-fixture"
            else (200, {"type": "User", "login": "independent-maintainer"})
        ),
    )
    assert approval._resolve_token() == ("valid-fixture", "CODEX_BACKUP_KEY")


@pytest.mark.parametrize(
    "case,expected",
    [
        ("fresh-old-pr", True),
        ("expired", False),
        ("future", False),
        ("revoked", False),
        ("missing", False),
        ("naive", False),
        ("bot", False),
        ("extended-ttl", False),
    ],
)
def test_once_grant_uses_verified_activation_not_pr_age(case, expected):
    labels = [{"name": "wec:auto-approve-once"}]
    pr = {"labels": labels, "created_at": "2020-01-01T00:00:00Z"}
    activation = {
        "id": 1,
        "event": "labeled",
        "label": {"name": "wec:auto-approve-once"},
        "actor": {"type": "User", "login": "maintainer"},
        "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
    }
    if case == "expired":
        activation["created_at"] = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    elif case == "future":
        activation["created_at"] = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    elif case == "naive":
        activation["created_at"] = "2026-11-13T00:00:00"
    elif case == "bot":
        activation["actor"]["type"] = "Bot"
    events = [] if case == "missing" else [activation]
    if case == "revoked":
        events.append({**activation, "id": 2, "event": "unlabeled"})

    def request(method, path, token):
        return (200, events) if "/events?" in path else (200, pr)

    assert (
        label_gate.label_valid(
            "", "o/r", 1, pr, request, ttl_hours=24 if case == "extended-ttl" else 1
        )
        is expected
    )


@pytest.mark.parametrize("case", ["denied", "truncated", "repeated"])
def test_once_activation_requires_complete_history(case):
    pr = {"labels": [{"name": "wec:auto-approve-once"}]}

    def request(method, path, token):
        if case == "denied":
            return 403, {}
        if case == "repeated":
            return 200, [{"id": 1}, {"id": 1}]
        return 200, [{"id": i} for i in range(1, 101)]

    with pytest.raises(RuntimeError):
        label_gate.label_valid("", "o/r", 1, pr, request)


@pytest.mark.parametrize(
    "case,error",
    [
        ("protected", None),
        ("missing-marker", "missing-or-invalid-environment-marker"),
        ("no-reviewers", "missing-independent-environment-review"),
        ("self-review", "missing-independent-environment-review"),
        ("bypass", "environment-allows-administrator-bypass"),
        ("unrestricted", "unrestricted-environment-deployment-branches"),
    ],
)
def test_owner_marker_never_substitutes_for_protection(case, error):
    environment = {
        "protection_rules": [
            {
                "type": "required_reviewers",
                "prevent_self_review": True,
                "reviewers": [{"type": "User", "reviewer": {"id": 1}}],
            }
        ],
        "can_admins_bypass": False,
        "deployment_branch_policy": {"protected_branches": True, "custom_branch_policies": False},
    }
    marker = "true"
    if case == "missing-marker":
        marker = ""
    elif case == "no-reviewers":
        environment["protection_rules"] = []
    elif case == "self-review":
        environment["protection_rules"][0]["prevent_self_review"] = False
    elif case == "bypass":
        environment["can_admins_bypass"] = True
    elif case == "unrestricted":
        environment["deployment_branch_policy"] = None
    assert owner_gate.protection_error(environment, marker) == error


@pytest.mark.parametrize(
    "reviewers",
    [
        [None],
        [{"type": "Unknown", "reviewer": {"id": 1}}],
        [{"type": "User", "reviewer": {"id": 0}}],
        [{"type": "Team", "reviewer": {"id": "1"}}],
        [{"type": "User", "reviewer": {"id": True}}],
        [{"type": "User", "reviewer": None}],
    ],
)
def test_owner_marker_rejects_malformed_or_unknown_reviewers(reviewers):
    environment = {
        "protection_rules": [
            {
                "type": "required_reviewers",
                "prevent_self_review": True,
                "reviewers": reviewers,
            }
        ],
        "can_admins_bypass": False,
        "deployment_branch_policy": {"protected_branches": True, "custom_branch_policies": False},
    }
    assert owner_gate.protection_error(environment, "true") == "invalid-environment-reviewer"


def test_environment_api_denial_is_not_approval(monkeypatch, capsys):
    monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
    monkeypatch.setenv("GITHUB_TOKEN", "fixture")
    monkeypatch.setenv("OWNER_APPROVAL_PROTECTED", "true")
    monkeypatch.setattr(owner_gate, "_gh", lambda *args: (403, {}))
    assert owner_gate.main() == 1
    assert "HTTP 403" in capsys.readouterr().out


@pytest.mark.parametrize(
    "event_name",
    ["pull_request_target", "workflow_run", "issue_comment", "schedule", "workflow_dispatch"],
)
def test_supported_trigger_runs_complete_independent_approval(
    api, monkeypatch, tmp_path, event_name
):
    import json

    pr, run, _, calls = api
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GITHUB_EVENT_NAME", event_name)
    monkeypatch.setenv("REPO", "o/r")
    monkeypatch.setenv("MAX_WAIT_SEC", "0")
    monkeypatch.setenv("DRY_RUN", "false")
    monkeypatch.delenv("HEAD_SHA", raising=False)
    monkeypatch.delenv("PR_NUMBER", raising=False)
    monkeypatch.delenv("APPROVAL_INTENT", raising=False)
    monkeypatch.delenv("TARGET_RUN_ID", raising=False)
    monkeypatch.setattr(approval, "_resolve_token", lambda: ("fixture", "fixture"))
    monkeypatch.setattr(approval, "_get_action_required_runs", lambda *args, **kwargs: [run])
    monkeypatch.setattr(approval, "_search_wec_labelled_prs", lambda *args: [("1", SHA)])
    event = {
        "pull_request": pr,
        "issue": {"number": 1, "pull_request": {"url": "fixture"}},
        "workflow_run": {"id": 7},
    }
    path = tmp_path / "event.json"
    path.write_text(json.dumps(event))
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(path))
    if event_name == "workflow_dispatch":
        monkeypatch.setenv("PR_NUMBER", "1")
    assert approval.main() == 0
    assert [(method, path) for method, path in calls if method != "GET"] == [
        ("POST", "/repos/o/r/actions/runs/7/approve")
    ]
    decision = json.loads((tmp_path / "approval-decision.json").read_text())["decisions"][0]
    assert decision["head_sha"] == SHA
    assert decision["outcome"] == "approved"


@pytest.mark.parametrize("status", [401, 403, 409, 422])
def test_platform_rejection_is_not_success(monkeypatch, status):
    monkeypatch.setattr(approval, "_gh", lambda *args: (status, {}))
    assert approval._approve_run("", "o/r", {"id": 7}) == "error"


@pytest.mark.parametrize("case", ["consume", "stale-head", "new-activation", "denied"])
def test_once_cleanup_binds_head_and_original_activation(monkeypatch, case):
    pr = {
        "state": "open",
        "head": {"sha": SHA},
        "labels": [{"name": "wec:auto-approve-once"}],
    }
    if case == "stale-head":
        pr["head"]["sha"] = "b" * 40
    calls = []

    def request(method, path, token):
        calls.append((method, path))
        return (403, {}) if method == "DELETE" and case == "denied" else (200, pr)

    monkeypatch.setattr(approval, "_gh", request)
    monkeypatch.setattr(approval, "label_valid", lambda *args: True)
    monkeypatch.setattr(
        approval.label_gate,
        "once_activation",
        lambda *args: {"id": 2 if case == "new-activation" else 1},
    )
    if case == "denied":
        with pytest.raises(RuntimeError, match="HTTP 403"):
            approval._consume_once_grant("", "o/r", "1", SHA, 1)
    else:
        approval._consume_once_grant("", "o/r", "1", SHA, 1)
    assert any(method == "DELETE" for method, _ in calls) is (case in {"consume", "denied"})


@pytest.mark.parametrize("case", ["completed", "old-session", "running", "other-pr"])
def test_once_cleanup_requires_verified_post_activation_session(monkeypatch, tmp_path, case):
    now = datetime.now(timezone.utc)
    session = {
        "name": "Copilot coding agent",
        "status": "completed",
        "head_sha": SHA,
        "pull_requests": [{"number": 1}],
        "run_started_at": now.isoformat(),
    }
    if case == "old-session":
        session["run_started_at"] = (now - timedelta(hours=2)).isoformat()
    elif case == "running":
        session["status"] = "in_progress"
    elif case == "other-pr":
        session["pull_requests"] = [{"number": 2}]
    path = tmp_path / "event.json"
    path.write_text('{"workflow_run": {"id": 8}}')
    monkeypatch.setenv("GITHUB_EVENT_NAME", "workflow_run")
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(path))
    monkeypatch.setattr(
        approval,
        "_gh",
        lambda method, path, token: (
            (200, session)
            if "/actions/runs/" in path
            else (200, {"labels": [{"name": "wec:auto-approve-once"}]})
        ),
    )
    monkeypatch.setattr(
        approval.label_gate,
        "once_activation",
        lambda *args: {"id": 1, "created_at": (now - timedelta(minutes=30)).isoformat()},
    )
    assert approval._completed_once_grant("", "o/r", "1", SHA) == (
        1 if case == "completed" else None
    )


def test_app_token_is_scoped_to_approval_repository_and_permissions(monkeypatch):
    import sys
    from types import SimpleNamespace

    monkeypatch.delenv("REPO", raising=False)
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    monkeypatch.setattr(approval, "_app_identity", None)
    monkeypatch.setitem(
        sys.modules, "jwt", SimpleNamespace(encode=lambda *args, **kwargs: "fixture")
    )
    calls = []

    def request(method, path, token, body=None):
        if path == "/app":
            return 200, {"id": 1, "slug": "codex-maintainer"}
        if path == "/app/installations/2":
            return 200, {"id": 2, "app_id": 1, "account": {"login": "o"}}
        calls.append((method, path, body))
        return 201, {
            "token": "scoped-fixture",
            "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
            "permissions": {
                "actions": "write",
                "pull_requests": "read",
                "issues": "write",
            },
        }

    monkeypatch.setattr(approval, "_gh", request)
    assert approval._mint_app_token("1", "fixture", "2", repo="o/r") == "scoped-fixture"
    assert calls == [
        (
            "POST",
            "/app/installations/2/access_tokens",
            {
                "repositories": ["r"],
                "permissions": {
                    "actions": "write",
                    "contents": "read",
                    "pull_requests": "read",
                    "issues": "write",
                },
            },
        ),
    ]


@pytest.fixture
def delegated_app(api, monkeypatch):
    import sys
    from types import SimpleNamespace

    _, run, _, _ = api
    monkeypatch.setattr(approval, "_app_identity", None)
    monkeypatch.setenv("REPO", "o/r")
    monkeypatch.setenv("GITHUB_APP_ID", "1")
    monkeypatch.setenv("GITHUB_APP_INSTALLATION_ID", "2")
    monkeypatch.setenv("GITHUB_APP_PRIVATE_KEY", "fixture")
    monkeypatch.setitem(
        sys.modules, "jwt", SimpleNamespace(encode=lambda *args, **kwargs: "jwt-fixture")
    )
    evidence = {
        "app": {"id": 1, "slug": "codex-maintainer"},
        "installation": {"id": 2, "app_id": 1, "account": {"login": "o"}},
        "token": {
            "token": "delegated-app-fixture",
            "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
            "permissions": {
                "actions": "write",
                "pull_requests": "read",
                "issues": "write",
            },
        },
        "review": {
            "user": {"login": "codex-maintainer[bot]", "type": "Bot"},
            "author_association": "NONE",
            "state": "APPROVED",
            "commit_id": SHA,
        },
    }
    original = approval._gh

    def request(method, path, token, body=None):
        if path == "/app":
            return 200, deepcopy(evidence["app"])
        if path == "/app/installations/2":
            return 200, deepcopy(evidence["installation"])
        if path == "/app/installations/2/access_tokens":
            return 201, deepcopy(evidence["token"])
        if "/reviews?" in path:
            return 200, [deepcopy(evidence["review"])]
        return original(method, path, token, body)

    monkeypatch.setattr(approval, "_gh", request)
    return evidence, run


def test_verified_agent_maintainer_needs_no_second_human(delegated_app, monkeypatch):
    _, run = delegated_app
    monkeypatch.setenv("GITHUB_ACTOR", "author")
    monkeypatch.setenv("GITHUB_TRIGGERING_ACTOR", "author")
    token, source = approval._resolve_token()
    assert source == "cognitive-brain-app"
    assert approval._authorize_run(token, "o/r", "1", SHA, run) == "authorized"
    assert "delegated-app-fixture" not in repr(approval._app_identity)


@pytest.mark.parametrize(
    "case", ["owner", "suspended", "app-id", "permissions", "issues-permission", "expiry"]
)
def test_agent_credentials_require_live_installation_evidence(delegated_app, case):
    evidence, _ = delegated_app
    if case == "owner":
        evidence["installation"]["account"]["login"] = "elsewhere"
    elif case == "suspended":
        evidence["installation"]["suspended_at"] = datetime.now(timezone.utc).isoformat()
    elif case == "app-id":
        evidence["app"]["id"] = 9
    elif case == "permissions":
        evidence["token"]["permissions"]["actions"] = "read"
    elif case == "issues-permission":
        evidence["token"]["permissions"]["issues"] = "read"
    else:
        evidence["token"]["expires_at"] = "2000-01-01T00:00:00Z"
    assert approval._mint_app_token("1", "fixture", "2") is None
    assert approval._app_identity is None


@pytest.mark.parametrize("case", ["stale", "other-bot", "withdrawn", "self"])
def test_delegated_review_preserves_independence_and_sha(delegated_app, case):
    evidence, run = delegated_app
    token, _ = approval._resolve_token()
    if case == "stale":
        evidence["review"]["commit_id"] = "b" * 40
    elif case == "other-bot":
        evidence["review"]["user"]["login"] = "unverified[bot]"
    elif case == "withdrawn":
        evidence["review"]["state"] = "DISMISSED"
    else:
        run["actor"]["login"] = "codex-maintainer[bot]"
    expected = "self-approval" if case == "self" else "missing-independent-current-review"
    assert approval._authorize_run(token, "o/r", "1", SHA, run) == expected


def test_expired_app_identity_does_not_authorize(delegated_app, monkeypatch):
    _, run = delegated_app
    token, _ = approval._resolve_token()
    monkeypatch.setattr(
        approval, "_app_identity", approval._AppIdentity(token, "codex-maintainer[bot]", 0)
    )
    assert approval._authorize_run(token, "o/r", "1", SHA, run) == "unknown-approver-identity"


def test_agent_approval_audit_preserves_real_bot_identity(delegated_app, monkeypatch):
    _, run = delegated_app
    monkeypatch.setenv("HEAD_SHA", SHA)
    monkeypatch.setenv("PR_NUMBER", "1")
    monkeypatch.setenv("GITHUB_EVENT_NAME", "workflow_dispatch")
    monkeypatch.setenv("CLEANUP_COPILOT_EYES", "false")
    monkeypatch.setenv("DRY_RUN", "false")
    monkeypatch.setattr(approval, "_get_action_required_runs", lambda *args, **kwargs: [run])
    decisions = []
    assert approval._run_decisions(decisions) == 0
    record = next(item for item in decisions if item.get("outcome") == "approved")
    assert record["approver"] == {"login": "codex-maintainer[bot]", "type": "Bot"}
    assert record["token_source"] == "cognitive-brain-app"
    assert record["head_sha"] == SHA
    assert record["credential_expires_at"] > datetime.now(timezone.utc).timestamp()
    assert "delegated-app-fixture" not in repr(decisions)


def test_malformed_success_response_is_not_permission_evidence(monkeypatch):
    from contextlib import nullcontext
    from types import SimpleNamespace

    response = SimpleNamespace(status=200, read=lambda limit: b"non-json-private-response")
    opener = SimpleNamespace(open=lambda *args, **kwargs: nullcontext(response))
    monkeypatch.setattr(approval.urllib.request, "build_opener", lambda *args: opener)
    status, payload = approval._gh("GET", "/user", "fixture")
    assert status == 502
    assert payload == {"error": "Invalid JSON from GitHub API"}
    assert "private-response" not in repr(payload)


def test_delegation_verification_precedes_any_untrusted_checkout():
    from pathlib import Path

    workflow = yaml.safe_load(
        (
            Path(__file__).resolve().parents[2] / ".github/workflows/agent-auth-delegation.yml"
        ).read_text()
    )
    activation = workflow["jobs"]["activate-delegation"]
    assert activation["environment"] == "owner-approval"
    assert "endsWith(github.workflow_ref" in activation["if"]
    checkout = activation["steps"][0]
    assert checkout["with"]["ref"] == "${{ github.workflow_sha }}"
    assert checkout["with"]["persist-credentials"] is False
    verification = activation["steps"][1]
    assert (
        verification["env"]["OWNER_APPROVAL_PROTECTED"] == "${{ secrets.OWNER_APPROVAL_PROTECTED }}"
    )
    assert "verify_owner_approval.py" in verification["run"]
    # The verifier reads environment protection with github.token (actions: read);
    # job-level permissions replace the workflow defaults, so preserve those too.
    assert activation["permissions"] == {
        "actions": "read",
        "contents": "write",
        "pull-requests": "write",
        "issues": "write",
    }
