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
import datetime as _dt
import subprocess
from pathlib import Path
from typing import Iterable

REPO = Path(__file__).resolve().parents[1]
QUESTIONS = REPO / "Codex_Questions.md"
CHANGELOG = REPO / "CHANGELOG_Codex.md"


def _append_questions(step: str, error: str) -> None:
    ts = _dt.datetime.utcnow().isoformat(timespec="seconds")
    block = (
        f"\nQuestion for ChatGPT-5 {ts}:\n"
        f"While performing {step}, encountered the following error:\n"
        f"{error}\n"
        "Context: automated task runner\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
    )
    QUESTIONS.write_text(QUESTIONS.read_text() + block, encoding="utf-8")


def _update_changelog(why: str, risk: str, rollback: str) -> None:
    entry = (
        f"\n## { _dt.date.today().isoformat() } Automated task\n\n"
        f"### WHY\n- {why}\n\n"
        f"### RISK\n- {risk}\n\n"
        f"### ROLLBACK\n- {rollback}\n"
    )
    CHANGELOG.write_text(CHANGELOG.read_text() + entry, encoding="utf-8")


def run_task(expr: str) -> int:
    """Run ``pytest`` with ``expr`` and return exit code."""
    try:
        subprocess.run(["pytest", "-q", expr], check=True)
        return 0
    except subprocess.CalledProcessError as exc:  # pragma: no cover - exercised in CI
        err = exc.stderr.decode() if exc.stderr else str(exc)
        _append_questions(expr, err)
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
    rc = 0
    for t in ns.tasks:
        rc |= run_task(t)
    if ns.changelog:
        _update_changelog(ns.changelog, ns.risk, ns.rollback)
    return rc


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
