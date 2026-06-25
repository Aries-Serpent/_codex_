"""Regression tests for the runner URL parsing helper."""

from __future__ import annotations

import shlex
import subprocess
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _parse_owner_repo(url: str) -> tuple[str, str]:
    quoted_url = shlex.quote(url)
    script = textwrap.dedent(f"""
        source scripts/runner/common.sh
        parse_owner_repo {quoted_url}
        """).strip()
    completed = subprocess.run(
        ["bash", "-c", script],
        check=True,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    tokens = completed.stdout.strip().split()
    if not tokens:
        raise RuntimeError(
            f"Unexpected empty output: stderr={completed.stderr!r} script={script!r}"
        )
    if len(tokens) == 1:
        return tokens[0], ""
    return tokens[0], tokens[1]


def test_parse_https_repo_url() -> None:
    assert _parse_owner_repo("https://github.com/Aries-Serpent/_codex_") == (
        "Aries-Serpent",
        "_codex_",
    )


def test_parse_https_repo_with_git_suffix() -> None:
    assert _parse_owner_repo("https://github.com/Aries-Serpent/_codex_.git") == (
        "Aries-Serpent",
        "_codex_",
    )


def test_parse_ssh_repo_url() -> None:
    assert _parse_owner_repo("git@github.com:Aries-Serpent/_codex_.git") == (
        "Aries-Serpent",
        "_codex_",
    )


def test_parse_ssh_scheme_repo_url() -> None:
    assert _parse_owner_repo("ssh://git@github.com/Aries-Serpent/_codex_.git") == (
        "Aries-Serpent",
        "_codex_",
    )


def test_parse_owner_only_url() -> None:
    assert _parse_owner_repo("https://github.com/Aries-Serpent") == (
        "Aries-Serpent",
        "",
    )
