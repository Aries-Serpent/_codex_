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
from typing import Iterable, Optional, Tuple, Union

# Repository root (two levels up from this file)
REPO = Path(__file__).resolve().parents[1]

# Output files (relative to project root)
QUESTION_FILE = "Codex_Questions.md"
CHANGELOG = "CHANGELOG_Codex.md"
COMMIT_COMMENT_FILE = "codex_commit_comment.txt"


def ts() -> str:
    """Timestamp (local) for human-readable logs."""
    return time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime())


def append(path: Path, text: str) -> None:
    """Append text to a file, creating parent directories if needed."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            existing = path.read_text(encoding="utf-8", errors="replace")
        else:
            existing = ""
        path.write_text(existing + text, encoding="utf-8")
    except Exception:
        # Best-effort append; swallow errors but do not crash the runner.
        try:
            # attempt a simple write fallback
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        except Exception:
            # give up silently; caller should still return non-zero to indicate failure
            pass


def capture_error(
    step_no: str,
    desc: str,
    errmsg: str,
    context: str,
    project_root: Union[Path, str] = REPO,
) -> None:
    """Record a standardized question block and an entry in the commit comment file."""
    project_root = Path(project_root)
    q = (
        f"Question for ChatGPT @codex {ts()}:\n"
        f"While performing [{step_no}:{desc}], encountered the following error:\n"
        f"{errmsg.strip()}\n"
        f"Context: {context.strip()}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n\n"
    )
    append(project_root / QUESTION_FILE, q)
    append(project_root / COMMIT_COMMENT_FILE, f"{desc}: {errmsg.strip()}\n")


def gather_codex_questions(project_root: Union[Path, str] = REPO) -> str:
    """Return the contents of the questions file (if present)."""
    project_root = Path(project_root)
    path = project_root / QUESTION_FILE
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def build_commit_comment_body(project_root: Union[Path, str] = REPO) -> str:
    """Compose the body for a commit comment from collected question blocks."""
    blocks = gather_codex_questions(project_root).strip()
    if not blocks:
        blocks = "No errors were captured by Codex during this iteration."
    header = f"Codex Iteration Error Report — {ts()}"
    return header + "\n\n" + blocks


def post_commit_comment(project_root: Union[Path, str] = REPO, body: str = "") -> Tuple[bool, str]:
    """
    Optionally post a commit comment to GitHub.

    Requires:
      - environment token in one of GH_PAT, GITHUB_TOKEN, CODEX_ENVIRONMENT_RUNNER, _CODEX_BOT_RUNNER, _CODEX_ACTION_RUNNER
      - environment GITHUB_REPOSITORY and GITHUB_SHA (typical in Actions)
    Returns (success: bool, message: str)
    """
    token = (
        os.getenv("GH_PAT")
        or os.getenv("GITHUB_TOKEN")
        or os.getenv("CODEX_ENVIRONMENT_RUNNER")
        or os.getenv("_CODEX_BOT_RUNNER")
        or os.getenv("_CODEX_ACTION_RUNNER")
    )
    if not token:
        return False, "no-token"

    repo_env = os.getenv("GITHUB_REPOSITORY", "")
    sha = os.getenv("GITHUB_SHA", "")
    if not repo_env or not sha:
        return False, "missing-repo-or-sha"

    try:
        owner, repo_name = repo_env.split("/", 1)
    except Exception:
        return False, "invalid-repo-format"

    api = os.getenv("GITHUB_API_URL", "https://api.github.com")
    url = f"{api}/repos/{owner}/{repo_name}/commits/{sha}/comments"
    data = json.dumps({"body": body}).encode("utf-8")

    try:
        import urllib.request

        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
                "User-Agent": "codex-runner",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:  # pragma: no cover - network
            code = resp.getcode()
            return (201 <= code < 300), f"http-{code}"
    except Exception as exc:  # pragma: no cover - network
        return False, str(exc)


def _update_changelog(project_root: Union[Path, str], why: str, risk: str, rollback: str) -> None:
    """Append a standardized changelog entry under project_root/CHANGELOG."""
    project_root = Path(project_root)
    entry = (
        f"\n## {time.strftime('%Y-%m-%d')} Automated task\n\n"
        f"### WHY\n- {why}\n\n"
        f"### RISK\n- {risk}\n\n"
        f"### ROLLBACK\n- {rollback}\n"
    )
    append(project_root / CHANGELOG, entry)


def _normalize_run_task_args(args: tuple) -> Tuple[str, Path]:
    """
    Support multiple historical signatures for run_task:
      - run_task(step_no: int, expr: str, project_root: Path)
      - run_task(expr: str, project_root: Path)
      - run_task(expr: str) -> uses REPO as project_root
    Returns (expr, project_root)
    """
    if len(args) == 3:
        # (step_no, expr, project_root)
        _, expr, project_root = args
        return str(expr), Path(project_root)
    if len(args) == 2:
        # (expr, project_root)
        expr, project_root = args
        return str(expr), Path(project_root)
    if len(args) == 1:
        expr = args[0]
        return str(expr), REPO
    raise TypeError("Unsupported run_task signature")


def run_task(*args) -> int:
    """Run ``pytest -q <expr>`` and record failures.

    Flexible signature to preserve backward compatibility with older call sites.
    Returns the subprocess return code (0 on success).
    """
    try:
        expr, project_root = _normalize_run_task_args(args)
    except TypeError:
        # If the caller passed unexpected args, bubble up a non-zero code
        return 2

    try:
        proc = subprocess.run(
            ["pytest", "-q", expr],
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:
        # Failed to invoke pytest itself
        capture_error("invoke", expr, str(exc), "pytest invocation", project_root)
        return 2

    if proc.returncode == 0:
        return 0

    # Compose an error message including stdout/stderr snippets
    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    err_msg = "\n".join(s for s in (out, err) if s)

    if not err_msg:
        err_msg = f"pytest exited with code {proc.returncode}"

    # Step identifier: try to glean a helpful label
    step_label = expr
    capture_error(step_label, expr, err_msg, "pytest", project_root)
    return proc.returncode if isinstance(proc.returncode, int) else 1


def main(argv: Optional[Iterable[str]] = None) -> int:
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

    # Run tasks sequentially
    for t in ns.tasks:
        rc |= run_task(t, project_root)

    # Optional changelog entry
    if ns.changelog:
        try:
            _update_changelog(project_root, ns.changelog, ns.risk, ns.rollback)
        except Exception:
            # record but don't crash
            capture_error(
                "changelog",
                "update changelog",
                "failed to write changelog",
                "changelog",
                project_root,
            )

    # Optional post to GitHub commit comments (only if environment variables set)
    if os.getenv("CODEX_POST_COMMIT_COMMENT"):
        try:
            body = build_commit_comment_body(project_root)
            success, msg = post_commit_comment(project_root, body)
            # Always write the commit comment file locally for traceability
            append(project_root / COMMIT_COMMENT_FILE, body + f"\n# post_status: {success} {msg}\n")
        except Exception as exc:
            capture_error(
                "post_comment", "post commit comment", str(exc), "post_commit_comment", project_root
            )

    return int(rc)


if __name__ == "__main__":  # pragma: no cover - invoked as script
    raise SystemExit(main())
