# BEGIN: CODEX_APPLY_DATA_LOADERS
"""Orchestrator for creating data loader utilities and running validations."""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CODEX = REPO / ".codex"
CODEX.mkdir(parents=True, exist_ok=True)
CHANGE_LOG = CODEX / "change_log.md"
ERRORS = CODEX / "errors.ndjson"
RESULTS = CODEX / "results.md"


def ts() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def log_change(action: str, path: Path, why: str, preview: str = "") -> None:
    if not CHANGE_LOG.exists() or CHANGE_LOG.stat().st_size == 0:
        CHANGE_LOG.write_text("# Codex Change Log\n", encoding="utf-8")
    with CHANGE_LOG.open("a", encoding="utf-8") as fh:
        fh.write(
            f"## {ts()} — {path.relative_to(REPO)}\n- **Action:** {action}\n- **Rationale:** {why}\n"
        )
        if preview:
            fh.write("```text\n" + preview[:4000] + "\n```\n")
        fh.write("\n")


def q5(step: str, err: str, ctx: str) -> None:
    msg = textwrap.dedent(
        f"""
        Question for ChatGPT-5 {ts()}:
        While performing [{step}], encountered the following error:
        {err}
        Context: {ctx}
        What are the possible causes, and how can this be resolved while preserving intended functionality?
        """
    )
    with ERRORS.open("a", encoding="utf-8") as fh:
        fh.write(
            json.dumps({"ts": ts(), "step": step, "error": err, "context": ctx}) + "\n"
        )
    sys.stderr.write(msg + "\n")


def upsert(path: Path, content: str, sentinel: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if sentinel in existing:
            return
        new = (
            existing
            + ("\n\n" if existing and not existing.endswith("\n") else "")
            + content
        )
        path.write_text(new, encoding="utf-8")
        log_change("edit", path, f"insert guarded by {sentinel}", content[:4000])
    else:
        path.write_text(content, encoding="utf-8")
        log_change("create", path, f"insert guarded by {sentinel}", content[:4000])


# File templates (identical to those committed)
LOADERS_SENTINEL = "# BEGIN: CODEX_DATA_LOADERS"
with open(REPO / "src/codex_ml/data/loaders.py", "r", encoding="utf-8") as fh:
    LOADERS_CODE = fh.read()
CLI_SENTINEL = "# BEGIN: CODEX_DATA_CLI"
with open(REPO / "src/codex_ml/data/cli.py", "r", encoding="utf-8") as fh:
    CLI_CODE = fh.read()
TEST_SENTINEL = "# BEGIN: CODEX_DATA_TESTS"
with open(REPO / "tests/test_loaders.py", "r", encoding="utf-8") as fh:
    TEST_CODE = fh.read()


def apply() -> None:
    try:
        upsert(REPO / "src/codex_ml/data/loaders.py", LOADERS_CODE, LOADERS_SENTINEL)
        upsert(REPO / "src/codex_ml/data/cli.py", CLI_CODE, CLI_SENTINEL)
        upsert(REPO / "tests/test_loaders.py", TEST_CODE, TEST_SENTINEL)
    except Exception as e:  # pragma: no cover
        q5("3: Best-Effort Construction — write files", str(e), f"path={REPO}")


def validate() -> None:
    with RESULTS.open("a", encoding="utf-8") as fh:
        fh.write(f"\n# Validation {ts()}\n")
        name, cmd = (
            "PyTest (loaders subset)",
            ["pytest", "-q", "-k", "loaders", "--maxfail=1"],
        )
        fh.write(f"\n## {name}\n```\n")
        try:
            p = subprocess.run(cmd, capture_output=True, text=True)
            fh.write(p.stdout + p.stderr + f"\n(exit={p.returncode})\n")
        except Exception as e:  # pragma: no cover
            fh.write(f"ERROR: {e}\n")
            q5("6: Finalization — validation", str(e), f"cmd={cmd}")
        fh.write("\n```\n")


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--apply", action="store_true", help="create/augment loaders, cli, tests"
    )
    ap.add_argument(
        "--validate", action="store_true", help="run local validations (pytest subset)"
    )
    args = ap.parse_args()
    if args.apply:
        apply()
    if args.validate:
        validate()
    if not (args.apply or args.validate):
        print("Usage: --apply [--validate]")


if __name__ == "__main__":
    main()
# END: CODEX_APPLY_DATA_LOADERS
