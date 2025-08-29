#!/usr/bin/env python3
"""Execute pytest tasks and capture failures.

This utility is intended for local workflows where tasks correspond to pytest
selections (e.g. ``tests/cli/test_cli_viewer.py``).  Each task is executed
sequentially; failing tasks append a question block to ``Codex_Questions.md``
so maintainers can follow up later.

Changelog entries can optionally be recorded via ``--changelog`` accompanied by
``--risk`` and ``--rollback`` messages.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Iterable

QUESTION_FILE = "Codex_Questions.md"
CHANGELOG = "CHANGELOG_Codex.md"


def ts() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime())


def append(path: Path, text: str) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    path.write_text(existing + text, encoding="utf-8")


def capture_error(step_no: str, desc: str, errmsg: str, context: str, project_root: Path) -> None:
    q = f"""Question for ChatGPT @codex {ts()}:
While performing [{step_no}:{desc}], encountered the following error:
{errmsg.strip()}
Context: {context.strip()}
What are the possible causes, and how can this be resolved while preserving intended functionality?

"""
    append(project_root / QUESTION_FILE, q)
    append(project_root / "codex_commit_comment.txt", f"{desc}: {errmsg}\n")


def gather_codex_questions(project_root: Path) -> str:
    path = project_root / QUESTION_FILE
    return path.read_text(encoding="utf-8") if path.exists() else ""


def build_commit_comment_body(project_root: Path) -> str:
    blocks = gather_codex_questions(project_root).strip()
    if not blocks:
        blocks = "No errors were captured by Codex during this iteration."
    header = f"Codex Iteration Error Report — {ts()}"
    return header + "\n\n" + blocks


def post_commit_comment(project_root: Path, body: str) -> tuple[bool, str]:
    token = (
        os.getenv("GH_PAT")
        or os.getenv("GITHUB_TOKEN")
        or os.getenv("CODEX_ENVIRONMENT_RUNNER")
        or os.getenv("_CODEX_BOT_RUNNER")
        or os.getenv("_CODEX_ACTION_RUNNER")
    )
    if not token:
        return False, "no token"
    repo = os.getenv("GITHUB_REPOSITORY", "")
    sha = os.getenv("GITHUB_SHA", "")
    if not repo or not sha:
        return False, "missing repo or sha"
    owner, repo_name = repo.split("/", 1)
    api = os.getenv("GITHUB_API_URL", "https://api.github.com")
    url = f"{api}/repos/{owner}/{repo_name}/commits/{sha}/comments"
    data = json.dumps({"body": body}).encode("utf-8")
    try:
        import urllib.request

        req = urllib.request.Request(
            url, data=data, headers={"Authorization": f"token {token}"}
        )
        with urllib.request.urlopen(req) as resp:  # pragma: no cover - network
            return 201 <= resp.getcode() < 300, "ok"
    except Exception as exc:  # pragma: no cover
        return False, str(exc)


def _update_changelog(project_root: Path, why: str, risk: str, rollback: str) -> None:
    entry = (
        f"\n## {time.strftime('%Y-%m-%d')} Automated task\n\n"
        f"### WHY\n- {why}\n\n"
        f"### RISK\n- {risk}\n\n"
        f"### ROLLBACK\n- {rollback}\n"
    )
    append(project_root / CHANGELOG, entry)


def run_task(expr: str, project_root: Path) -> int:
    """Run ``pytest`` with ``expr`` and return exit code."""
    try:
        subprocess.run(["pytest", "-q", expr], check=True)
        return 0
    except subprocess.CalledProcessError as exc:  # pragma: no cover
        err = exc.stderr.decode() if exc.stderr else str(exc)
        capture_error(expr, expr, err, "automated task runner", project_root)
        return exc.returncode


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run Codex tasks")
    ap.add_argument("tasks", nargs="*", help="Pytest paths or expressions")
    ap.add_argument("--changelog", help="Changelog WHY message")
    ap.add_argument("--risk", default="low", help="Changelog RISK entry")
    ap.add_argument(
        "--rollback",
        default="Revert this commit",
        help="Changelog ROLLBACK entry",
    )
    ns = ap.parse_args(list(argv) if argv is not None else None)
    project_root = Path(__file__).resolve().parents[1]
    rc = 0
    for t in ns.tasks:
        rc |= run_task(t, project_root)
    if ns.changelog:
        _update_changelog(project_root, ns.changelog, ns.risk, ns.rollback)
    if os.getenv("CODEX_POST_COMMIT_COMMENT"):
        body = build_commit_comment_body(project_root)
        post_commit_comment(project_root, body)
        (project_root / "codex_commit_comment.txt").write_text(body, encoding="utf-8")
    return rc


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
