from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.ci import copilot_agent_task as task


def safe_env(**overrides: str) -> dict[str, str]:
    env = {
        "AGENT_KILL_SWITCH": "0",
        "AUTONOMOUS_ACTIONS_ENABLED": "true",
        "COPILOT_AGENT_MAX_AUTONOMY_LEVEL": "D",
        "GITHUB_ACTOR": "mbaetiong",
        "CODEX_MASTER_KEY": "ghp_" + "a" * 36,
        "COPILOT_AGENT_TASK_TOKEN": "github_pat_" + "a" * 36,
    }
    env.update(overrides)
    return env


class FakeResponse:
    status = 200

    def __init__(self, payload: dict | list | str):
        self.payload = payload
        self.status = 200


class QueueTransport:
    def __init__(self, *responses: dict | list | tuple[int, dict]):
        self.responses = list(responses)
        self.calls: list[dict] = []

    def request(
        self,
        method: str,
        url: str,
        headers: dict,
        body: bytes | None = None,
        timeout: int = 30,
    ):
        self.calls.append(
            {
                "method": method,
                "url": url,
                "headers": dict(headers),
                "body": json.loads(body.decode("utf-8")) if body else None,
            }
        )
        if not self.responses:
            raise AssertionError("unexpected HTTP call")
        response = self.responses.pop(0)
        if isinstance(response, tuple):
            status, payload = response
            return task.HTTPResponse(status=status, payload=payload, headers={})
        return task.HTTPResponse(status=200, payload=response, headers={})


def test_launch_key_is_exactly_40_hex_chars() -> None:
    launch_key = task.generate_launch_key(
        "Fix tests",
        owner="Aries-Serpent",
        repo="_codex_",
        base_branch="main",
    )

    assert len(launch_key) == 40
    assert task.validate_launch_key(launch_key)
    assert task.validate_launch_key("x" * 40)


def test_create_payload_omits_empty_optional_fields() -> None:
    payload = task.build_create_payload(
        "Fix tests",
        base_branch="",
        head_branch="",
        launch_key="",
        issue_number=None,
        assignees=[],
        agent_assignment=None,
    )

    assert payload == {"prompt": "Fix tests"}


def test_create_payload_includes_only_non_empty_optional_fields() -> None:
    launch_key = "a" * 40
    payload = task.build_create_payload(
        "Fix tests",
        base_branch="main",
        head_branch="feature/tests",
        launch_key=launch_key,
        issue_number=42,
        assignees=["mbaetiong", "@copilot-swe-agent"],
        agent_assignment={"launch_key": launch_key},
    )

    assert payload["prompt"] == "Fix tests"
    assert payload["base_ref"] == "main"
    assert payload["head_ref"] == "feature/tests"
    assert payload["launch_key"] == launch_key
    assert payload["issue_number"] == 42
    assert payload["assignees"] == ["mbaetiong", "copilot-swe-agent"]
    assert payload["agent_assignment"] == {"launch_key": launch_key}


def test_branch_validation_rejects_direct_0d_base_launch() -> None:
    assert task.validate_branch_name("feature/tests")
    assert task.validate_branch_name("main")
    assert not task.validate_branch_name("feature..bad")
    assert not task.validate_branch_pair("0D_base_", "feature/tests")
    assert task.validate_branch_pair("0D_base_", "copilot/session-20261124-120000")
    assert task.validate_branch_pair("main", "0D_base_", promotion=True)


def test_custom_agent_slug_resolution_and_rejection() -> None:
    assert (
        task.resolve_custom_agent_slug("ci-failure-resolution-agent.agent.md")
        == "ci-failure-resolution-agent"
    )
    assert (
        task.resolve_custom_agent_slug("Security Alert Verification Agent")
        == "security-alert-verification-agent"
    )
    with pytest.raises(task.PolicyViolation):
        task.resolve_custom_agent_slug("unknown-agent")


def test_placeholder_and_installation_tokens_are_rejected() -> None:
    assert task.is_placeholder_credential("placeholder-token")
    assert task.is_placeholder_credential("")
    assert task.is_installation_token("ghs_123456789")

    valid, _reason = task.validate_credential("ghp_" + "a" * 36)
    assert valid
    assert not task.validate_credential("ghs_123456789")[0]
    assert not task.validate_credential("placeholder-token")[0]


def test_dedup_state_expires_after_24_hours(tmp_path: Path) -> None:
    dedup = task.DedupState(tmp_path / ".codex")
    launch_key = "a" * 40
    dedup.put(launch_key, {"task_id": "task-1", "created_at": "2026-11-23T00:00:00Z"})

    assert dedup.is_recent(launch_key, ttl_seconds=1.0) is False


def test_live_agent_task_probe_is_opt_in(tmp_path: Path) -> None:
    transport = QueueTransport({"tasks": []})
    client = task.CopilotAgentTaskClient(
        "Aries-Serpent",
        "_codex_",
        environ=safe_env(),
        transport=transport,
        repo_root=tmp_path,
        state_dir=tmp_path / ".codex",
    )

    probe = client.probe_agent_task_access()

    assert probe["passed"] is True
    assert probe["endpoint"] == "/agents/repos/Aries-Serpent/_codex_/tasks"


def test_preflight_passes_for_safe_d_tier_owner_and_budget(tmp_path: Path) -> None:
    client = task.CopilotAgentTaskClient(
        "Aries-Serpent",
        "_codex_",
        environ=safe_env(),
        repo_root=tmp_path,
        state_dir=tmp_path / ".codex",
    )

    result = client.preflight(
        "Fix tests",
        base_branch="main",
        head_branch="feature/tests",
        skip_budget=True,
    )

    assert result["allowed"] is True
    assert len(result["launch_key"]) == 40
    assert result["checks"]["owner_auth"]["passed"] is True
    assert result["checks"]["d_tier"]["passed"] is True


def test_preflight_rejects_kill_switch_and_wrong_owner(tmp_path: Path) -> None:
    client = task.CopilotAgentTaskClient(
        "Aries-Serpent",
        "_codex_",
        environ=safe_env(
            AGENT_KILL_SWITCH="1",
            GITHUB_ACTOR="someone-else",
        ),
        repo_root=tmp_path,
        state_dir=tmp_path / ".codex",
    )

    result = client.preflight("Fix tests", skip_budget=True)

    assert result["allowed"] is False
    assert result["checks"]["kill_switch"]["passed"] is False
    assert result["checks"]["owner_auth"]["passed"] is False


def test_create_is_mocked_deduplicated_and_writes_state(tmp_path: Path) -> None:
    transport = QueueTransport((201, {"id": "task-123", "status": "queued", "launch_key": ""}))
    client = task.CopilotAgentTaskClient(
        "Aries-Serpent",
        "_codex_",
        environ=safe_env(),
        transport=transport,
        repo_root=tmp_path,
        state_dir=tmp_path / ".codex",
    )

    first = client.create(
        "Fix tests",
        base_branch="main",
        head_branch="feature/tests",
        issue_number=42,
        assignees=["mbaetiong"],
        skip_budget=True,
    )

    second = client.create(
        "Fix tests",
        base_branch="main",
        head_branch="feature/tests",
        issue_number=42,
        assignees=["mbaetiong"],
        skip_budget=True,
    )

    assert first["deduplicated"] is False
    assert first["id"] == "task-123"
    assert second["deduplicated"] is True
    assert len(transport.calls) == 1

    call = transport.calls[0]
    assert call["method"] == "POST"
    assert call["url"] == "https://api.github.com/agents/repos/Aries-Serpent/_codex_/tasks"
    assert call["headers"]["X-GitHub-Api-Version"] == "2026-03-10"
    assert call["body"]["prompt"] == "Fix tests"
    assert call["body"]["issue_number"] == 42
    assert call["body"]["assignees"] == ["mbaetiong"]
    assert len(call["body"]["launch_key"]) == 40

    assert (tmp_path / ".codex" / "copilot_agent_task_dedup.json").is_file()
    assert (tmp_path / ".codex" / "copilot_agent_task_handoff.json").is_file()
    assert (tmp_path / ".codex" / "handoff_state.json").is_file()
    assert (tmp_path / ".codex" / "action_log.ndjson").is_file()


def test_assign_uses_issue_assignees_and_agent_assignment(tmp_path: Path) -> None:
    transport = QueueTransport(
        (200, {"id": 42, "state": "open", "assignees": ["copilot-swe-agent"]})
    )
    client = task.CopilotAgentTaskClient(
        "Aries-Serpent",
        "_codex_",
        environ=safe_env(),
        transport=transport,
        repo_root=tmp_path,
        state_dir=tmp_path / ".codex",
    )

    result = client.assign(
        42,
        ["copilot-swe-agent"],
        prompt="Fix issue 42",
        base_branch="main",
        skip_budget=True,
    )

    assert result["operation"] == "assign"
    assert len(transport.calls) == 1
    call = transport.calls[0]
    assert call["method"] == "POST"
    assert call["url"] == "https://api.github.com/repos/Aries-Serpent/_codex_/issues/42/assignees"
    assert call["body"]["assignees"] == ["copilot-swe-agent"]
    assert call["body"]["agent_assignment"]["issue_number"] == 42
    assert len(call["body"]["agent_assignment"]["launch_key"]) == 40


def test_view_list_continue_and_cancel_are_mocked(tmp_path: Path) -> None:
    transport = QueueTransport(
        {"id": "task-1", "status": "running"},
        {"tasks": [{"id": "task-1"}]},
        {"id": "task-1", "status": "continued"},
        {"id": "task-1", "status": "cancelled"},
    )
    client = task.CopilotAgentTaskClient(
        "Aries-Serpent",
        "_codex_",
        environ=safe_env(),
        transport=transport,
        repo_root=tmp_path,
        state_dir=tmp_path / ".codex",
    )

    view = client.view("task-1")
    listing = client.list(status="running", page=1, per_page=20)
    continuation = client.continue_task("task-1", "Keep going", skip_budget=True)
    cancellation = client.cancel("task-1", skip_budget=True)

    assert view["status"] == "running"
    assert listing["tasks"] == [{"id": "task-1"}]
    assert continuation["status"] == "continued"
    assert cancellation["status"] == "cancelled"
    assert transport.calls[1]["url"].endswith("/tasks?status=running&per_page=20")


def test_poll_stops_at_terminal_status(tmp_path: Path) -> None:
    transport = QueueTransport(
        {"id": "task-1", "status": "running"},
        {"id": "task-1", "status": "completed"},
    )
    client = task.CopilotAgentTaskClient(
        "Aries-Serpent",
        "_codex_",
        environ=safe_env(),
        transport=transport,
        repo_root=tmp_path,
        state_dir=tmp_path / ".codex",
        sleep=lambda _seconds: None,
        now=lambda: 100.0,
    )

    result = client.poll("task-1", timeout=30, interval=0)

    assert result["status"] == "completed"
    assert [item["status"] for item in result["observations"]] == ["running", "completed"]


def test_preflight_cli_outputs_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = task.main(
        [
            "--repo",
            "Aries-Serpent/_codex_",
            "--skip-budget",
            "preflight",
            "Fix tests",
            "--base",
            "main",
        ],
        environ=safe_env(),
        repo_root=tmp_path,
    )

    output = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert output["allowed"] is True
    assert output["operation"] == "preflight"


def test_preflight_rejects_direct_0d_base(tmp_path: Path) -> None:
    client = task.CopilotAgentTaskClient(
        "Aries-Serpent",
        "_codex_",
        environ=safe_env(),
        repo_root=tmp_path,
        state_dir=tmp_path / ".codex",
    )

    result = client.preflight(
        "Fix tests",
        base_branch="0D_base_",
        head_branch="feature/tests",
        skip_budget=True,
    )

    assert result["allowed"] is False
    assert any("0D_base_" in reason or "branches" in reason for reason in result["blocked_reasons"])
