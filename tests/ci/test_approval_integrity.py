"""Offline inventory and transition integrity checks; registries are synthetic."""

import json
from copy import deepcopy
from urllib.parse import parse_qs, urlsplit

import pytest
import yaml

from scripts.ci import approve_pending_runs as approval
from scripts.cognitive import d_capable_promotion as promotion

SHA = "a" * 40
AGENT = {
    "id": "fixture",
    "autonomy_model": "E",
    "maturity": "production",
    "violations_30d": 0,
    "handoff_protocol": "structured",
    "capability_tags": ["analysis", "testing", "evidence"],
    "description": "Synthetic fixture",
}


def first_page(path):
    return parse_qs(urlsplit(path).query).get("page") == ["1"]


@pytest.fixture
def offline(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    for key in (
        "HEAD_SHA",
        "PR_NUMBER",
        "TARGET_RUN_ID",
        "APPROVAL_INTENT",
        "GITHUB_OUTPUT",
    ):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("REPO", "o/r")
    monkeypatch.setenv("GITHUB_EVENT_NAME", "schedule")
    monkeypatch.setenv("MAX_WAIT_SEC", "0")
    monkeypatch.setenv("DRY_RUN", "false")
    monkeypatch.setattr(approval, "_resolve_token", lambda: ("fixture", "mock"))
    calls = []

    def install(response):
        def gh(method, path, token, body=None):
            calls.append((method, path))
            assert method == "GET", "Inventory failure must not mutate GitHub"
            return response(path)

        monkeypatch.setattr(approval, "_gh", gh)

    return install, calls


@pytest.mark.parametrize(
    "status,payload",
    [
        (403, {"message": "Forbidden"}),
        (200, {}),
        (200, {"items": [], "total_count": 1, "incomplete_results": False}),
        (200, {"items": [], "total_count": 0, "incomplete_results": True}),
        (200, {"items": [], "total_count": 0}),
        (200, {"items": {}, "total_count": 0, "incomplete_results": False}),
        (200, {"items": [], "total_count": False, "incomplete_results": False}),
        (200, {"items": [], "total_count": 1001, "incomplete_results": False}),
        (200, {"items": [None], "total_count": 1, "incomplete_results": False}),
        (200, {"items": [{}], "total_count": 1, "incomplete_results": False}),
    ],
)
def test_search_failure_is_not_empty_success(offline, status, payload):
    install, _ = offline
    install(lambda path: (status, payload))
    assert approval.main() == 1
    assert json.loads(open("approval-decision.json").read())["decisions"][-1] == {
        "rule": "inspection-error",
        "pr": None,
        "head_sha": None,
        "outcome": "denied",
    }


def test_complete_empty_search_is_legitimate_success(offline):
    install, calls = offline
    install(lambda path: (200, {"items": [], "total_count": 0, "incomplete_results": False}))
    assert approval.main() == 0
    assert len(calls) == 2
    assert json.loads(open("approval-decision.json").read())["decisions"][0]["rule"] == (
        "no-authorized-targets"
    )


def test_complete_search_pagination_retains_all_targets(offline):
    install, _ = offline
    items = [{"number": number} for number in range(1, 102)]

    def response(path):
        if path.startswith("/search/"):
            query = parse_qs(urlsplit(path).query)["q"][0]
            if query.endswith("label:wec:auto-approve-once"):
                return 200, {"items": [], "total_count": 0, "incomplete_results": False}
            return 200, {
                "items": items[:100] if first_page(path) else items[100:],
                "total_count": 101,
                "incomplete_results": False,
            }
        return 200, {
            "number": int(path.rsplit("/", 1)[-1]),
            "state": "open",
            "head": {"sha": SHA},
            "labels": [{"name": "wec:auto-approve"}],
        }

    install(response)
    assert approval._search_wec_labelled_prs("fixture", "o/r") == [
        (str(number), SHA) for number in range(1, 102)
    ]


@pytest.mark.parametrize("failure", ["denied", "short", "repeated", "changed"])
def test_search_pagination_cannot_return_partial_results(offline, failure):
    install, _ = offline
    first = [{"number": number} for number in range(1, 101)]

    def response(path):
        if first_page(path):
            return 200, {"items": first, "total_count": 101, "incomplete_results": False}
        if failure == "denied":
            return 403, {}
        items = [] if failure == "short" else [{"number": 1 if failure == "repeated" else 101}]
        return 200, {
            "items": items,
            "total_count": 102 if failure == "changed" else 101,
            "incomplete_results": False,
        }

    install(response)
    assert approval.main() == 1


@pytest.mark.parametrize("payload", [{}, {"head": {}}, {"head": {"sha": SHA}, "labels": None}])
def test_discovered_pr_inspection_must_be_complete(offline, payload):
    install, _ = offline

    def response(path):
        if path.startswith("/search/"):
            return 200, {"items": [{"number": 1}], "total_count": 1, "incomplete_results": False}
        return 200, payload

    install(response)
    assert approval.main() == 1


@pytest.mark.parametrize(
    "status,payload",
    [
        (403, {}),
        (200, {}),
        (200, {"workflow_runs": [], "total_count": 1}),
        (200, {"workflow_runs": None, "total_count": 0}),
        (200, {"workflow_runs": [{}], "total_count": 1}),
    ],
)
def test_run_inventory_failure_is_denied(offline, monkeypatch, status, payload):
    install, _ = offline
    monkeypatch.setenv("PR_NUMBER", "1")
    monkeypatch.setenv("HEAD_SHA", SHA)

    def response(path):
        if path == "/repos/o/r/pulls/1":
            return 200, {"labels": [{"name": "wec:auto-approve"}]}
        return status, payload

    install(response)
    assert approval.main() == 1


@pytest.mark.parametrize("failure", ["denied", "short", "repeated", "changed"])
def test_run_pagination_must_finish_before_approval(offline, monkeypatch, failure):
    install, _ = offline
    monkeypatch.setenv("PR_NUMBER", "1")
    monkeypatch.setenv("HEAD_SHA", SHA)
    first = [{"id": number, "head_sha": SHA} for number in range(1, 101)]

    def response(path):
        if path == "/repos/o/r/pulls/1":
            return 200, {"labels": [{"name": "wec:auto-approve"}]}
        if first_page(path):
            return 200, {"workflow_runs": first, "total_count": 101}
        if failure == "denied":
            return 403, {}
        runs = (
            []
            if failure == "short"
            else [{"id": 1 if failure == "repeated" else 101, "head_sha": SHA}]
        )
        return 200, {"workflow_runs": runs, "total_count": 102 if failure == "changed" else 101}

    install(response)
    assert approval.main() == 1


@pytest.mark.parametrize("dry_run,deny", [(True, False), (False, True), (True, True)])
def test_denied_and_dry_paths_preserve_once_labels(offline, monkeypatch, dry_run, deny):
    install, _ = offline
    monkeypatch.setenv("PR_NUMBER", "1")
    monkeypatch.setenv("HEAD_SHA", SHA)
    monkeypatch.setenv("DRY_RUN", str(dry_run).lower())
    monkeypatch.setenv("GITHUB_ACTOR", "requester")
    monkeypatch.setenv("GITHUB_TRIGGERING_ACTOR", "requester")
    pr = {
        "state": "open",
        "head": {"sha": SHA},
        "user": {"login": "author"},
        "labels": [{"name": "wec:auto-approve-once"}],
        "created_at": approval.datetime.now(approval.timezone.utc).isoformat(),
    }
    run = {
        "id": 7,
        "head_sha": SHA,
        "conclusion": "action_required",
        "actor": {"login": "author"},
        "triggering_actor": {"login": "author"},
        "pull_requests": [{"number": 1}],
    }

    def response(path):
        if path == "/user":
            return 200, {"login": "independent-maintainer", "type": "User"}
        if path == "/repos/o/r/pulls/1":
            return 200, deepcopy(pr)
        if path == "/repos/o/r/actions/runs/7":
            return 200, deepcopy(run)
        if "/reviews?" in path:
            return 200, (
                []
                if deny
                else [
                    {
                        "user": {"login": "reviewer", "type": "User"},
                        "author_association": "MEMBER",
                        "state": "APPROVED",
                        "commit_id": SHA,
                    }
                ]
            )
        return 200, {"workflow_runs": [deepcopy(run)], "total_count": 1}

    install(response)
    assert approval.main() == (1 if deny else 0)
    assert pr["labels"] == [{"name": "wec:auto-approve-once"}]


def test_complete_empty_run_inventory_is_success(offline, monkeypatch):
    install, _ = offline
    monkeypatch.setenv("PR_NUMBER", "1")
    monkeypatch.setenv("HEAD_SHA", SHA)
    install(
        lambda path: (
            (200, {"labels": [{"name": "wec:auto-approve"}]})
            if path == "/repos/o/r/pulls/1"
            else (200, {"workflow_runs": [], "total_count": 0})
        )
    )
    assert approval.main() == 0
    assert json.loads(open("approval-decision.json").read())["decisions"][0]["rule"] == (
        "no-pending-runs"
    )


def test_complete_run_pagination_preserves_all_identities(offline):
    install, _ = offline
    runs = [{"id": number, "head_sha": SHA} for number in range(1, 102)]
    install(
        lambda path: (
            200,
            {"workflow_runs": runs[:100] if first_page(path) else runs[100:], "total_count": 101},
        )
    )
    assert approval._get_action_required_runs("fixture", "o/r", SHA) == runs


@pytest.mark.parametrize("status,payload", [(403, {}), (200, [None]), (200, [{}])])
def test_open_pr_inventory_does_not_hide_failure(offline, status, payload):
    install, _ = offline
    install(lambda path: (status, payload))
    with pytest.raises(RuntimeError):
        approval._get_open_pr_shas("fixture", "o/r")


def test_complete_empty_open_pr_inventory_is_valid(offline):
    install, _ = offline
    install(lambda path: (200, []))
    assert approval._get_open_pr_shas("fixture", "o/r") == []


def test_reaction_cleanup_dry_run_is_read_only(offline):
    install, _ = offline
    install(
        lambda path: (
            (200, [{"id": 1}])
            if "/comments?" in path
            else (200, [{"id": 2, "content": "eyes", "user": {"login": "Copilot"}}])
        )
    )
    assert approval._cleanup_copilot_eyes_reactions("fixture", "o/r", "1", dry_run=True) == (1, 0)


@pytest.mark.parametrize("apply", [False, True])
def test_duplicate_mixed_eligibility_denied_before_any_mutation(tmp_path, monkeypatch, apply):
    monkeypatch.chdir(tmp_path)
    data = {"agents": [deepcopy(AGENT), {**AGENT, "violations_30d": 1}]}
    registry = tmp_path / "fixture.yaml"
    registry.write_text(yaml.safe_dump(data))
    before = registry.read_bytes()
    monkeypatch.setattr(promotion, "save_registry", lambda *args: pytest.fail("must not save"))
    assert promotion.run(registry, apply) == 1
    assert registry.read_bytes() == before
    assert not (tmp_path / ".codex").exists()


@pytest.mark.parametrize(
    "agents",
    [
        None,
        {},
        [None],
        [{}],
        [{"id": ""}],
        [{"id": 1}],
        [{"id": " fixture "}],
        [{"id": "fixture name"}],
        [{"id": "Fixture"}],
        [{"id": "fixture_name"}],
        [{"id": "ab"}],
        [{"id": "a" * 65}],
        [AGENT, AGENT],
    ],
)
def test_public_writer_rejects_ambiguous_schema_before_write(tmp_path, agents):
    registry = tmp_path / "fixture.yaml"
    registry.write_text(yaml.safe_dump({"agents": [AGENT]}))
    before = registry.read_bytes()
    with pytest.raises(ValueError):
        promotion.save_registry({"agents": agents}, registry)
    assert registry.read_bytes() == before


def test_public_writer_also_rejects_duplicate_source_registry(tmp_path):
    registry = tmp_path / "fixture.yaml"
    registry.write_text(yaml.safe_dump({"agents": [AGENT, AGENT]}))
    before = registry.read_bytes()
    with pytest.raises(ValueError, match="unique"):
        promotion.save_registry({"agents": [AGENT]}, registry)
    assert registry.read_bytes() == before


def test_unique_mixed_eligibility_promotes_only_eligible_agent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GITHUB_OUTPUT", raising=False)
    registry = tmp_path / "fixture.yaml"
    registry.write_text(
        yaml.safe_dump(
            {
                "last_updated": "old",
                "agents": [AGENT, {**AGENT, "id": "blocked", "violations_30d": 1}],
            }
        )
    )
    assert promotion.run(registry, True) == 0
    agents = yaml.safe_load(registry.read_text())["agents"]
    assert [agent["autonomy_model"] for agent in agents] == ["D_CAPABLE", "E"]
