#!/usr/bin/env python3
"""codex_exec.py

Lightweight automation driver for this repository.

Usage
-----
    python tools/codex_exec.py            # run in SAFE_MODE (default)
    SAFE_MODE=0 python tools/codex_exec.py  # allow edits across the repo

Phases
------
1. Detect repository root.
2. Initialize `.codex/` scaffolding (`change_log.md`, `errors.ndjson`, `results.md`).
3. Apply placeholder edits for ingestion, chat, and SQLite modules and run
   `ruff --fix` if available.
4. Generate placeholder tests.
5. Update README with a results summary.
6. Append overall results to `.codex/results.md`.

Every modification is logged to `.codex/change_log.md` and any exception is
recorded as a JSON line in `.codex/errors.ndjson`.

The command respects `SAFE_MODE` (enabled by default) and aborts early if
`.codex/DO_NOT_ACTIVATE_GITHUB_ACTIONS` exists. No network or secret access is
performed.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

# Hard guard to prevent CI activation.
DO_NOT_ACTIVATE_GITHUB_ACTIONS = True

# SAFE_MODE defaults to on; set SAFE_MODE=0 to allow broader edits.
SAFE_MODE = os.environ.get("SAFE_MODE", "1") not in {"0", "false", "False"}


def timestamp() -> str:
    """Return an ISO-8601 timestamp in UTC."""

    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def find_repo_root(start: Optional[Path] = None) -> Path:
    """Locate the repository root by walking upward for a `.git` directory."""

    p = (start or Path.cwd()).resolve()
    for _ in range(20):
        if (p / ".git").exists():
            return p
        if p.parent == p:
            break
        p = p.parent
    raise RuntimeError("Unable to locate repository root")


def log_change(change_log: Path, message: str) -> None:
    """Append a markdown-formatted change entry."""

    with change_log.open("a", encoding="utf-8") as f:
        f.write(f"### {timestamp()} — {message}\n")


def log_error(errors: Path, phase: str, err: BaseException) -> None:
    """Record an error as a JSON object."""

    rec = {"ts": timestamp(), "phase": phase, "error": str(err)}
    with errors.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def init_codex(root: Path) -> dict[str, Path]:
    """Ensure `.codex/` scaffolding exists and return key paths."""

    codex = root / ".codex"
    codex.mkdir(exist_ok=True)

    change_log = codex / "change_log.md"
    if not change_log.exists():
        change_log.write_text("# Codex change log\n")

    paths = {
        "codex": codex,
        "change_log": change_log,
        "errors": codex / "errors.ndjson",
        "results": codex / "results.md",
    }

    if not paths["errors"].exists():
        paths["errors"].write_text("")
        log_change(change_log, "Initialized .codex/errors.ndjson")
    if not paths["results"].exists():
        paths["results"].write_text("# Results\n")
        log_change(change_log, "Initialized .codex/results.md")

    return paths


def _append_marker(root: Path, path: Path, change_log: Path, errors: Path) -> None:
    """Append a marker comment to *path* or create the file if missing."""

    marker = "# touched by codex_exec"
    rel = path.relative_to(root)
    try:
        if path.exists():
            content = path.read_text(encoding="utf-8")
            if marker not in content:
                if not content.endswith("\n"):
                    content += "\n"
                path.write_text(content + marker + "\n", encoding="utf-8")
                log_change(change_log, f"Updated {rel}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(marker + "\n", encoding="utf-8")
            log_change(change_log, f"Created {rel}")
    except Exception as exc:  # noqa: BLE001
        log_error(errors, f"edit {rel}", exc)


def apply_edits(root: Path, change_log: Path, errors: Path) -> str:
    """Touch key source files or log skips when in SAFE_MODE."""

    targets = [
        root / "src" / "ingestion" / "__init__.py",
        root / "src" / "codex" / "chat.py",
        root / "src" / "codex" / "db" / "sqlite_patch.py",
    ]

    if SAFE_MODE:
        for p in targets:
            rel = p.relative_to(root)
            log_change(change_log, f"SAFE_MODE: skipped edit {rel}")
        return "edits skipped (SAFE_MODE)"

    for p in targets:
        _append_marker(root, p, change_log, errors)
    return "applied placeholder edits"


def run_ruff_fix(root: Path, change_log: Path, errors: Path) -> str:
    """Run `ruff --fix` when available and safe to do so."""

    if SAFE_MODE:
        log_change(change_log, "SAFE_MODE: ruff --fix skipped")
        return "ruff --fix skipped (SAFE_MODE)"
    if shutil.which("ruff") is None:
        log_change(change_log, "ruff not found; skipping lint fixes")
        return "ruff not available"
    try:
        result = subprocess.run(
            ["ruff", "--fix", str(root)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            log_error(errors, "ruff --fix", RuntimeError(result.stderr.strip()))
            return "ruff --fix failed"
        log_change(change_log, "Executed `ruff --fix`")
        return "ruff --fix applied"
    except Exception as exc:  # noqa: BLE001
        log_error(errors, "ruff --fix", exc)
        return "ruff --fix failed"


def generate_tests(root: Path, change_log: Path, errors: Path) -> str:
    """Create a placeholder test file if possible."""

    tests_dir = root / "tests"
    target = tests_dir / "test_codex_exec_placeholder.py"

    if SAFE_MODE:
        log_change(change_log, "SAFE_MODE: skipped test generation")
        return "test generation skipped (SAFE_MODE)"
    if not tests_dir.exists():
        log_change(change_log, "No tests directory; skipping generation")
        return "no tests directory"
    try:
        if not target.exists():
            target.write_text(
                "def test_codex_exec_placeholder():\n    assert True\n",
                encoding="utf-8",
            )
            log_change(change_log, f"Created {target.relative_to(root)}")
            return "generated placeholder test"
        return "placeholder test already present"
    except Exception as exc:  # noqa: BLE001
        log_error(errors, "generate tests", exc)
        return "test generation failed"


def update_readme(root: Path, change_log: Path, errors: Path, results: Path) -> str:
    """Insert a results summary section in the repository README."""

    readme = root / "README.md"
    if not readme.exists():
        log_change(change_log, "README.md missing; nothing to update")
        return "README missing"
    if SAFE_MODE:
        log_change(change_log, "SAFE_MODE: README update skipped")
        return "README update skipped (SAFE_MODE)"
    try:
        content = readme.read_text(encoding="utf-8")
        marker = "\n## Codex Results\n"
        summary = results.read_text(encoding="utf-8").strip()
        if marker not in content:
            content += marker + "\n"
        content = content.split(marker)[0] + marker + "\n" + summary + "\n"
        readme.write_text(content, encoding="utf-8")
        log_change(change_log, "Updated README with results summary")
        return "README updated"
    except Exception as exc:  # noqa: BLE001
        log_error(errors, "update README", exc)
        return "README update failed"


def write_results(results: Path, change_log: Path, lines: Iterable[str]) -> None:
    """Append a run summary to the results file."""

    with results.open("a", encoding="utf-8") as f:
        f.write("\n## Run\n")
        for line in lines:
            f.write(f"- {line}\n")
    log_change(change_log, "Appended run summary to results.md")


def main() -> int:
    try:
        root = find_repo_root()
    except Exception as exc:  # noqa: BLE001
        print("Could not locate repository root:", exc)
        return 2

    paths = init_codex(root)
    change_log = paths["change_log"]
    errors = paths["errors"]
    results = paths["results"]

    guard = paths["codex"] / "DO_NOT_ACTIVATE_GITHUB_ACTIONS"
    if guard.exists():
        log_change(
            change_log,
            "Guardrail present: DO_NOT_ACTIVATE_GITHUB_ACTIONS; exiting",
        )
        write_results(results, change_log, ["Skipped: DO_NOT_ACTIVATE_GITHUB_ACTIONS"])
        return 0

    summary: list[str] = []
    summary.append(apply_edits(root, change_log, errors))
    summary.append(run_ruff_fix(root, change_log, errors))
    summary.append(generate_tests(root, change_log, errors))
    summary.append(update_readme(root, change_log, errors, results))
    write_results(results, change_log, summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
