#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codex Workflow: Safely patch `tests/test_session_logging.py` to replace
`except Exception: pass` near lines 60–68 with observable handling that
preserves skip semantics when hooks are unavailable.

Outputs:
  - ./.codex/change_log.md
  - ./.codex/errors.ndjson
  - ./.codex/results.md
Constraints:
  - DO NOT ACTIVATE ANY GitHub Actions files.
"""

import argparse
import dataclasses
import difflib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from typing import List, Optional, Tuple

REPO_ROOT = (
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    ).stdout.strip()
    or os.getcwd()
)

CODEX_DIR = os.path.join(REPO_ROOT, ".codex")
TARGET_REL = "tests/test_session_logging.py"
TARGET = os.path.join(REPO_ROOT, TARGET_REL)
FLAGS_ENV = os.path.join(CODEX_DIR, "flags.env")

os.makedirs(CODEX_DIR, exist_ok=True)

CHANGE_LOG = os.path.join(CODEX_DIR, "change_log.md")
ERRORS = os.path.join(CODEX_DIR, "errors.ndjson")
RESULTS = os.path.join(CODEX_DIR, "results.md")

# ---------- utilities ----------


def now_iso() -> str:
    return (
        datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    )


def read_text(p: str) -> str:
    with open(p, "r", encoding="utf-8") as f:
        return f.read()


def write_text(p: str, s: str) -> None:
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def append(path: str, text: str) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(text)


def run_ok(cmd: List[str]) -> Tuple[bool, str]:
    try:
        cp = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        return (cp.returncode == 0, cp.stdout)
    except Exception as e:
        return (False, f"{type(e).__name__}: {e}")


def log_error(step: str, desc: str, err: str, ctx: str) -> None:
    """Write ChatGPT-5 formatted question to console + ndjson."""
    block = (
        "Question for ChatGPT-5:\n"
        f"While performing [{step}: {desc}], encountered the following error:\n"
        f"{err}\n"
        f"Context: {ctx}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
    )
    print(block, file=sys.stderr)
    entry = {
        "ts": now_iso(),
        "step": step,
        "description": desc,
        "error": err,
        "context": ctx,
        "question_for_chatgpt5": block,
    }
    append(ERRORS, json.dumps(entry) + "\n")


def add_change(
    file_path: str, action: str, rationale: str, before: str, after: str
) -> None:
    diff = "\n".join(
        difflib.unified_diff(
            before.splitlines(),
            after.splitlines(),
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm="",
        )
    )
    append(
        CHANGE_LOG,
        f"\n## {now_iso()} — {action}\n"
        f"**File:** `{file_path}`\n"
        f"**Rationale:** {rationale}\n\n"
        f"```diff\n{diff}\n```\n",
    )


def ensure_import(module: str, src: str) -> Tuple[str, bool]:
    """Idempotently ensure `import module` exists; insert below top shebang/future/comments."""
    if re.search(rf"^\s*import\s+{re.escape(module)}\b", src, re.M):
        return src, False
    if re.search(rf"^\s*from\s+{re.escape(module)}\b", src, re.M):
        return src, False

    lines = src.splitlines()
    insert_idx = 0
    # Skip shebang, encoding, __future__, and initial comments/docstring header
    # Heuristic: insert after first non-empty, non-comment if early lines are headers
    for i, line in enumerate(lines[:50]):
        if i == 0 and line.startswith("#!"):
            insert_idx = i + 1
            continue
        if re.match(r"^#.*coding[:=]\s*utf-8", line, re.I):
            insert_idx = i + 1
            continue
        if re.match(r"^\s*from\s+__future__", line):
            insert_idx = i + 1
            continue
        if line.strip().startswith("#") or line.strip() == "":
            insert_idx = i + 1
            continue
        break

    new_lines = lines[:insert_idx] + [f"import {module}"] + lines[insert_idx:]
    return "\n".join(new_lines) + ("\n" if not src.endswith("\n") else ""), True


# ---------- patch logic ----------

EXC_PASS_PATTERN = re.compile(
    r"(^[ \t]*)except\s+Exception(?:\s+as\s+\w+)?\s*:\s*\n"
    r"([ \t]*)pass\b",
    flags=re.M,
)

REPLACEMENT_TEMPLATE = """{indent}except Exception as e:
{indent2}logging.exception("session logging hook raised: %s: %s", e.__class__.__name__, e)
{indent2}if isinstance(e, (ImportError, AttributeError, NotImplementedError)):
{indent2}    pytest.skip(f"Required session logging hook not available: {{e!r}}")
{indent2}pytest.fail(f"Session logging hook failed: {{e!r}}")"""


def patch_except_pass(
    src: str, prefer_range: Optional[Tuple[int, int]] = None
) -> Tuple[str, bool, str]:
    matches = list(EXC_PASS_PATTERN.finditer(src))
    if not matches:
        return src, False, "No `except Exception: pass` pattern found."

    chosen = None
    if prefer_range:
        start_l, end_l = prefer_range
        line_starts = [0]
        for m in re.finditer(r"\n", src):
            line_starts.append(m.end())

        def line_no(pos: int) -> int:
            ln = 1
            for i, st in enumerate(line_starts):
                if st > pos:
                    break
                ln = i + 1
            return ln

        for m in matches:
            ln = line_no(m.start())
            if start_l <= ln <= end_l:
                chosen = m
                break
    if chosen is None:
        chosen = matches[0]

    indent = chosen.group(1)
    indent2 = chosen.group(2) if chosen.group(2) else indent + "    "
    replacement = REPLACEMENT_TEMPLATE.format(indent=indent, indent2=indent2)
    new_src = src[: chosen.start()] + replacement + src[chosen.end() :]
    return new_src, True, "Patched `except Exception: pass` with logging + skip/fail."


# ---------- main workflow ----------


@dataclasses.dataclass
class Outcome:
    errors: List[str] = dataclasses.field(default_factory=list)
    changes: int = 0


def main() -> int:
    ok, out = run_ok(["git", "status", "--porcelain"])
    if not ok:
        log_error(
            "1.1", "Check clean working state", out, "git status --porcelain failed"
        )
    elif out.strip():
        log_error(
            "1.1",
            "Uncommitted changes present",
            out.strip(),
            "Proceeding best-effort per instructions",
        )

    append(FLAGS_ENV, "DO_NOT_ACTIVATE_GITHUB_ACTIONS=true\n")

    outcome = Outcome()

    for doc in ("README.md", "CONTRIBUTING.md"):
        p = os.path.join(REPO_ROOT, doc)
        if os.path.isfile(p):
            try:
                snap = os.path.join(CODEX_DIR, f"{doc}.snapshot.md")
                write_text(snap, read_text(p))
            except Exception as e:
                log_error("1.2", f"Snapshot {doc}", f"{type(e).__name__}: {e}", p)

    if not os.path.isfile(TARGET):
        log_error("2.2", "Locate test file", "File not found", TARGET)
        append(RESULTS, "Target test file not found; cannot patch.\n")
        append(RESULTS, "\n**DO NOT ACTIVATE ANY GitHub Actions files.**\n")
        return 1

    try:
        before = read_text(TARGET)
        after, imp_logging = ensure_import("logging", before)
        after, imp_pytest = ensure_import("pytest", after)

        patched, did_patch, msg = patch_except_pass(after, prefer_range=(60, 68))
        if not did_patch:
            patched, did_patch, msg = patch_except_pass(after, prefer_range=None)

        if did_patch:
            write_text(TARGET, patched)
            outcome.changes += 1
            rationale = (
                "Replace broad exception swallowing with observable handling; "
                "preserve skip semantics for missing hooks "
                "(ImportError/AttributeError/NotImplementedError) and otherwise fail."
            )
            add_change(TARGET_REL, "Patch except-pass", rationale, before, patched)
            if imp_logging or imp_pytest:
                add_change(
                    TARGET_REL,
                    "Ensure imports",
                    "Added missing imports for logging/pytest",
                    after,
                    patched,
                )
        else:
            log_error("3.2", "Patch except-pass", msg, TARGET)

    except Exception as e:
        log_error("3.2", "Apply patch", f"{type(e).__name__}: {e}", TARGET)

    ok, out = run_ok(
        [
            sys.executable,
            "-c",
            "import importlib, sys; importlib.import_module('pytest'); print('pytest-ok')",
        ]
    )
    if ok and "pytest-ok" in out:
        _ok, _out = run_ok(["pytest", "--collect-only", "-q"])
        if not _ok:
            log_error("3.4", "Pytest collection", _out, "pytest --collect-only -q")

    append(
        CHANGE_LOG,
        "\n## Pruning\nNo pruning performed; construction succeeded without duplication or unsafe paths.\n",
    )

    results = []
    if outcome.changes:
        results.append(
            f"- Patched `{TARGET_REL}` to replace `except Exception: pass` with logging + skip/fail."
        )
    else:
        results.append(f"- No patch applied to `{TARGET_REL}` (pattern not found).")
    results.append(
        "- Ensured `import logging` and `import pytest` presence (idempotent)."
    )
    results.append("- Recorded diffs in `.codex/change_log.md`.")
    results.append(
        "- Captured any errors in `.codex/errors.ndjson` (ChatGPT-5 format)."
    )
    results.append(
        "- Constraint observed: **DO NOT ACTIVATE ANY GitHub Actions files.**"
    )

    append(RESULTS, "# Results Summary\n" + "\n".join(results) + "\n")
    append(RESULTS, "\n**DO NOT ACTIVATE ANY GitHub Actions files.**\n")

    has_errors = os.path.isfile(ERRORS) and os.path.getsize(ERRORS) > 0
    return 1 if has_errors else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Codex workflow for session logging test patch."
    )
    _ = parser.parse_args()
    sys.exit(main())
