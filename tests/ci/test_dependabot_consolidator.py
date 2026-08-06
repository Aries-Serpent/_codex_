"""Tests for scripts/ci/dependabot_consolidator.py.

All external subprocess and HTTP calls are mocked so the tests run offline.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Generator
from unittest.mock import MagicMock, patch

import pytest

import scripts.ci.dependabot_consolidator as dc


@pytest.fixture
def token_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set a token so resolve_token does not exit."""
    monkeypatch.setenv("GH_TOKEN", "ghp_test_token")


@pytest.fixture
def mock_gh_auth() -> Generator[MagicMock, None, None]:
    """Mock gh auth status to succeed."""
    with patch("scripts.ci.dependabot_consolidator.verify_gh_auth") as m:
        yield m


@pytest.fixture
def mock_subprocess() -> Generator[MagicMock, None, None]:
    """Mock subprocess.run for git operations."""
    with patch("scripts.ci.dependabot_consolidator.subprocess.run") as m:
        yield m


@pytest.fixture
def mock_gh_api() -> Generator[MagicMock, None, None]:
    """Mock gh_api helper."""
    with patch("scripts.ci.dependabot_consolidator.gh_api") as m:
        m.return_value = {"number": 99}
        yield m


@pytest.fixture
def mock_paginated() -> Generator[MagicMock, None, None]:
    """Mock gh_api_paginated helper."""
    with patch("scripts.ci.dependabot_consolidator.gh_api_paginated") as m:
        yield m


@pytest.fixture
def mock_tempdir(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide a temporary directory that the consolidation git commands can use."""
    with patch(
        "scripts.ci.dependabot_consolidator.tempfile.TemporaryDirectory"
    ) as tmp:
        tmp.return_value.__enter__ = MagicMock(return_value=str(tmp_path))
        tmp.return_value.__exit__ = MagicMock(return_value=False)
        yield tmp_path


def make_pr(
    number: int,
    title: str,
    ref: str,
    login: str = "dependabot[bot]",
    labels: list[str] | None = None,
    merge_state_status: str = "CLEAN",
) -> dict[str, Any]:
    """Build a minimal PR dictionary."""
    return {
        "number": number,
        "title": title,
        "user": {"login": login},
        "head": {"ref": ref},
        "labels": [{"name": name} for name in (labels or [])],
        "merge_state_status": merge_state_status,
    }


def configure_subprocess_for_clean_merge(
    mock_run: MagicMock,
    tmp_path: Path,
) -> None:
    """Set subprocess.run return values for a successful clone/merge/push path."""
    def side_effect(
        cmd: list[str],
        **kwargs: Any,
    ) -> subprocess.CompletedProcess[str]:
        # Clone needs a git repo in tmp_path
        if cmd[1] == "clone":
            (tmp_path / ".git").mkdir(exist_ok=True)
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    mock_run.side_effect = side_effect


def test_no_prs_exits_cleanly(
    token_env: None,
    mock_gh_auth: MagicMock,
    mock_paginated: MagicMock,
) -> None:
    """Empty PR list returns 0."""
    mock_paginated.return_value = []
    args = ["--base-branch", "main", "--dry-run", "true"]
    assert dc.main(args) == 0


def test_single_pr_exits_cleanly(
    token_env: None,
    mock_gh_auth: MagicMock,
    mock_paginated: MagicMock,
) -> None:
    """Single Dependabot PR needs no consolidation."""
    mock_paginated.side_effect = [
        [make_pr(1, "Bump foo", "dependabot/foo")],  # pulls
        [],  # issues search for existing consolidation PR
    ]
    args = ["--base-branch", "main", "--dry-run", "true"]
    assert dc.main(args) == 0


def test_merge_clean_pr(
    token_env: None,
    mock_gh_auth: MagicMock,
    mock_paginated: MagicMock,
    mock_gh_api: MagicMock,
    mock_subprocess: MagicMock,
    mock_tempdir: Path,
) -> None:
    """Clean Dependabot branches are merged and a consolidation PR is created."""
    mock_paginated.side_effect = [
        [
            make_pr(1, "Bump foo", "dependabot/foo"),
            make_pr(2, "Bump bar", "dependabot/bar"),
        ],
        [],  # no existing consolidation issue
    ]
    configure_subprocess_for_clean_merge(mock_subprocess, mock_tempdir)
    mock_gh_api.return_value = {"number": 99}

    args = ["--base-branch", "main", "--dry-run", "false"]
    assert dc.main(args) == 0

    # PR creation call
    calls = mock_gh_api.call_args_list
    create_call = [
        c for c in calls if c.args[0] == "POST" and "/pulls" in c.args[1]
    ]
    assert create_call, "Expected PR creation call"
    payload = json.loads(create_call[0].args[3])
    assert payload["title"].startswith("chore(deps): consolidated dependency updates")
    assert payload["head"].startswith("dependabot/consolidated-")


def test_conflict_skipped_and_reported(
    token_env: None,
    mock_gh_auth: MagicMock,
    mock_paginated: MagicMock,
    mock_gh_api: MagicMock,
    mock_subprocess: MagicMock,
    mock_tempdir: Path,
) -> None:
    """A dirty merge is aborted, excluded, and reported."""
    mock_paginated.side_effect = [
        [
            make_pr(1, "Bump foo", "dependabot/foo"),
            make_pr(2, "Bump bar", "dependabot/bar"),
        ],
        [],
    ]

    def side_effect(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        if cmd[1] == "clone":
            (mock_tempdir / ".git").mkdir(exist_ok=True)
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
        # merge --no-ff for dependabot/bar conflicts
        if cmd[1] == "merge" and any("dependabot/bar" in str(x) for x in cmd):
            return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="merge conflict")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    mock_subprocess.side_effect = side_effect
    mock_gh_api.return_value = {"number": 99}

    assert dc.main(["--base-branch", "main"]) == 0

    create_call = [
        c for c in mock_gh_api.call_args_list
        if c.args[0] == "POST" and "/pulls" in c.args[1]
    ]
    payload = json.loads(create_call[0].args[3])
    body = payload["body"]
    assert "| #1 | Bump foo | merged cleanly |" in body
    assert "| #2 | Bump bar | merge conflict |" in body


def test_security_label_excluded(
    token_env: None,
    mock_gh_auth: MagicMock,
    mock_paginated: MagicMock,
    mock_gh_api: MagicMock,
    mock_subprocess: MagicMock,
    mock_tempdir: Path,
) -> None:
    """Security-labelled PRs are left out of the consolidation."""
    mock_paginated.side_effect = [
        [
            make_pr(1, "Bump safe", "dependabot/safe"),
            make_pr(2, "Bump security", "dependabot/security", labels=["security"]),
        ],
        [],
    ]
    configure_subprocess_for_clean_merge(mock_subprocess, mock_tempdir)
    mock_gh_api.return_value = {"number": 99}

    assert dc.main(["--base-branch", "main"]) == 0

    create_call = [
        c for c in mock_gh_api.call_args_list
        if c.args[0] == "POST" and "/pulls" in c.args[1]
    ]
    payload = json.loads(create_call[0].args[3])
    body = payload["body"]
    assert "security label" in body


def test_dry_run_no_push(
    token_env: None,
    mock_gh_auth: MagicMock,
    mock_paginated: MagicMock,
    mock_gh_api: MagicMock,
    mock_subprocess: MagicMock,
    mock_tempdir: Path,
) -> None:
    """Dry-run does not push branches or create/close PRs."""
    mock_paginated.side_effect = [
        [
            make_pr(1, "Bump foo", "dependabot/foo"),
            make_pr(2, "Bump bar", "dependabot/bar"),
        ],
        [],
    ]
    configure_subprocess_for_clean_merge(mock_subprocess, mock_tempdir)

    assert dc.main(["--base-branch", "main", "--dry-run", "true"]) == 0

    # No PR creation/update and no comments/close calls
    for call in mock_gh_api.call_args_list:
        assert not (call.args[0] == "POST" and "/pulls" in call.args[1])
        assert not (call.args[0] == "POST" and "/comments" in call.args[1])
    # No git push
    for call in mock_subprocess.call_args_list:
        if call.args and "git" in call.args[0][0]:
            assert "push" not in call.args[0], "Unexpected push in dry-run"


def test_existing_consolidation_pr_reused(
    token_env: None,
    mock_gh_auth: MagicMock,
    mock_paginated: MagicMock,
    mock_gh_api: MagicMock,
    mock_subprocess: MagicMock,
    mock_tempdir: Path,
) -> None:
    """When a consolidation PR already exists, its body is updated."""
    existing = {"number": 42, "title": "existing"}
    mock_paginated.side_effect = [
        [
            make_pr(1, "Bump foo", "dependabot/foo"),
            make_pr(2, "Bump bar", "dependabot/bar"),
        ],
        [{"number": 42, "pull_request": {}}],
    ]
    configure_subprocess_for_clean_merge(mock_subprocess, mock_tempdir)
    mock_gh_api.return_value = {"number": 42}

    assert dc.main(["--base-branch", "main"]) == 0

    update_call = [
        c for c in mock_gh_api.call_args_list
        if c.args[0] == "PATCH" and "/pulls/42" in c.args[1]
    ]
    assert update_call, "Expected existing PR update call"
