#!/usr/bin/env python3
"""Orchestrator to install safety filters & sandbox modules.
Creates files if missing and runs pytest on safety suite.
"""

from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CODEX = REPO / ".codex"
CODEX.mkdir(exist_ok=True)
CHANGE_LOG = CODEX / "change_log.md"
ERRORS = CODEX / "errors.ndjson"
RESULTS = CODEX / "results.md"


def ts() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def append(p: Path, text: str) -> None:
    p.write_text((p.read_text() if p.exists() else "") + text, encoding="utf-8")


def log_change(path: Path, rationale: str) -> None:
    append(
        CHANGE_LOG,
        f"## {ts()} — {path.relative_to(REPO)}\n- **Action:** upsert\n- **Rationale:** {rationale}\n\n",
    )


def upsert(path: Path, sentinel: str, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and sentinel in path.read_text(encoding="utf-8"):
        return
    path.write_text(content, encoding="utf-8")
    log_change(path, f"insert guarded by {sentinel}")


FILTERS = Path("src/codex_ml/safety/filters.py")
SANDBOX = Path("src/codex_ml/safety/sandbox.py")
INIT = Path("src/codex_ml/safety/__init__.py")
TEST = Path("tests/test_safety.py")
DOC = Path("documentation/safety_README.md")

# content strings are trimmed for brevity; they match repository files
FILTERS_CODE = Path(FILTERS).read_text(encoding="utf-8")
SANDBOX_CODE = Path(SANDBOX).read_text(encoding="utf-8")
INIT_CODE = Path(INIT).read_text(encoding="utf-8")
TEST_CODE = Path(TEST).read_text(encoding="utf-8")
DOC_CODE = Path(DOC).read_text(encoding="utf-8")

SENT_F = "# BEGIN: CODEX_SAFETY_FILTERS"
SENT_S = "# BEGIN: CODEX_SANDBOX"
SENT_I = "# BEGIN: CODEX_SAFETY_INIT"
SENT_T = "# BEGIN: CODEX_SAFETY_TESTS"
SENT_D = "<!-- BEGIN: CODEX_SAFETY_DOCS -->"


def apply() -> None:
    upsert(FILTERS, SENT_F, FILTERS_CODE)
    upsert(SANDBOX, SENT_S, SANDBOX_CODE)
    upsert(INIT, SENT_I, INIT_CODE)
    upsert(TEST, SENT_T, TEST_CODE)
    upsert(DOC, SENT_D, DOC_CODE)


def validate() -> None:
    append(RESULTS, f"\n# Validation {ts()}\n")
    cmd = ["pytest", "-q", "tests/test_safety.py"]
    append(RESULTS, f"\n## $ {' '.join(cmd)}\n```")
    p = subprocess.run(cmd, capture_output=True, text=True)
    append(RESULTS, p.stdout + p.stderr + f"\n(exit={p.returncode})\n```")


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()
    if args.apply:
        apply()
    if args.validate:
        validate()
    if not (args.apply or args.validate):
        print("Usage: --apply [--validate]")


if __name__ == "__main__":
    main()
