"""Exercise approval authority using the real shell guard."""

import json
import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GUARD = REPO_ROOT / "scripts/ci/owner_approval_guard.sh"


@pytest.mark.parametrize(
    ("approval_env", "expected_code", "expected_source"),
    [
        ({}, 2, "env-missing"),
        ({"OWNER_APPROVED_UNTIL": "invalid"}, 2, "env-until-invalid"),
        ({"OWNER_APPROVED_UNTIL": "2000-01-01T00:00:00Z"}, 2, "env-until-expired"),
        (
            {"OWNER_APPROVED_UNTIL": "invalid", "OWNER_APPROVED_DURATION": "2h"},
            2,
            "env-until-invalid",
        ),
        (
            {"OWNER_APPROVED_UNTIL": "2000-01-01T00:00:00Z", "OWNER_APPROVED_DURATION": "2h"},
            2,
            "env-until-expired",
        ),
        ({"OWNER_APPROVED_UNTIL": "2100-01-01T00:00:00Z"}, 0, "env-until"),
        ({"OWNER_APPROVED_DURATION": "invalid"}, 2, "env-duration-invalid"),
        ({"OWNER_APPROVED_DURATION": "2h"}, 0, "env-duration"),
        (
            {
                "COPILOT_AGENT_AUTH_ENABLED": "true",
                "COPILOT_AGENT_AUTH_BYPASS_TOOLS": "security-scans, docker-build-push",
            },
            0,
            "env-agent-auth",
        ),
        (
            {
                "COPILOT_AGENT_AUTH_ENABLED": "true",
                "COPILOT_AGENT_AUTH_BYPASS_TOOLS": "security-scans",
            },
            2,
            "env-missing",
        ),
    ],
)
@pytest.mark.parametrize("token_override", [False, True])
def test_guard_never_trusts_worktree_approval(
    tmp_path: Path,
    approval_env: dict[str, str],
    expected_code: int,
    expected_source: str,
    token_override: bool,
) -> None:
    codex = tmp_path / ".codex"
    codex.mkdir()
    session = codex / "agent_auth_session.json"
    session.write_text(
        json.dumps({"expires_at": 4102444800, "bypass_tools": "", "pr_number": "5765"})
    )
    github = tmp_path / ".github"
    github.mkdir()
    (github / "OWNER_APPROVAL.yml").write_text(
        "enabled: true\nmode: until\nuntil: 2100-01-01T00:00:00Z\n" "cost_workflows:\n  - all\n"
    )
    env = {
        "PATH": os.environ["PATH"],
        "TOOL_KEY": "docker-build-push",
        "GITHUB_ACTIONS": "true",
        **approval_env,
    }
    if token_override:
        alternate = tmp_path / "alternate-session.json"
        alternate.write_text(session.read_text())
        env["CODEX_SESSION_TOKEN_FILE"] = str(alternate)
    result = subprocess.run(
        ["bash", str(GUARD)], cwd=tmp_path, env=env, capture_output=True, text=True, timeout=10
    )
    assert result.returncode == expected_code, result.stdout + result.stderr
    evidence = json.loads((codex / "evidence/owner_approval.jsonl").read_text().splitlines()[-1])
    assert evidence["source"] == expected_source
    assert evidence["decision"] == ("approved" if expected_code == 0 else "denied")


def test_committed_session_is_evidence_only() -> None:
    session = json.loads((REPO_ROOT / ".codex/agent_auth_session.json").read_text())
    assert session["expires_at"] == 0
    assert "does not authorize" in session["note"]
