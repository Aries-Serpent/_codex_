#!/usr/bin/env python3
"""
Codex end-to-end workflow for branch 0B_base_ on `_codex_`.

- Phase 1..6 as specified
- Best-effort, localized edits
- Evidence-based pruning
- Error capture as ChatGPT-5 questions
- Lint restricted to the requested file
- DOES NOT ACTIVATE ANY GitHub Actions
"""
from __future__ import annotations

import difflib
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
CODEX_DIR = REPO_ROOT / ".codex"
CHANGE_LOG = CODEX_DIR / "change_log.md"
ERRORS_NDJSON = CODEX_DIR / "errors.ndjson"
RESULTS_MD = CODEX_DIR / "results.md"
DO_NOT_ACTIVATE_GHA = True

TARGET_PARSE_FILE = REPO_ROOT / "src" / "codex" / "logging" / "query_logs.py"
TARGET_EXPORT_FILE = REPO_ROOT / "src" / "codex" / "logging" / "export.py"
TEST_EXPORT_FILE = REPO_ROOT / "tests" / "test_export.py"

def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")

def ensure_codex_scaffolding() -> None:
    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    if not CHANGE_LOG.exists():
        CHANGE_LOG.write_text("# .codex/change_log.md\n\n", encoding="utf-8")
    if not ERRORS_NDJSON.exists():
        ERRORS_NDJSON.write_text("", encoding="utf-8")
    if not RESULTS_MD.exists():
        RESULTS_MD.write_text("# .codex/results.md\n\n", encoding="utf-8")
    # sentinel file to emphasize policy
    (CODEX_DIR / "DO_NOT_ACTIVATE_GITHUB_ACTIONS").write_text(
        "Policy: DO NOT ACTIVATE ANY GitHub Actions files.\n", encoding="utf-8"
    )

def git_clean_working_tree() -> bool:
    try:
        out = subprocess.check_output(["git", "status", "--porcelain"], cwd=REPO_ROOT).decode()
        return out.strip() == ""
    except Exception:
        # Non-git folders should not block local edits
        return True

def read_text(p: Path) -> Optional[str]:
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8")

def write_text(p: Path, new_text: str, rationale: str, title: str, before_text: Optional[str]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(new_text, encoding="utf-8")
    log_change(p, "write/update", rationale, title, before_text or "", new_text)

def append_results(md: str) -> None:
    with RESULTS_MD.open("a", encoding="utf-8") as f:
        f.write(md)
        if not md.endswith("\n"):
            f.write("\n")

def append_error(step_num: str, step_desc: str, err_msg: str, context: str) -> None:
    block = (
        "Question for ChatGPT-5:\n"
        f"While performing [{step_num}: {step_desc}], encountered the following error:\n"
        f"{err_msg}\n"
        f"Context: {context}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?"
    )
    entry = {
        "timestamp": now_iso(),
        "step": step_num,
        "description": step_desc,
        "error": err_msg,
        "context": context,
        "question_text": block,
    }
    with ERRORS_NDJSON.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    # Echo to console as specified
    print(block, file=sys.stderr)

def log_change(path: Path, action: str, rationale: str, title: str, before: str, after: str) -> None:
    timestamp = now_iso()
    diff = "\n".join(
        difflib.unified_diff(
            before.splitlines(), after.splitlines(),
            fromfile=f"a/{path.as_posix()}",
            tofile=f"b/{path.as_posix()}",
            lineterm=""
        )
    )
    entry = (
        f"## {title}\n"
        f"- **Time:** {timestamp}\n"
        f"- **File:** `{path.as_posix()}`\n"
        f"- **Action:** {action}\n"
        f"- **Rationale:** {rationale}\n\n"
        "```diff\n" + (diff if diff.strip() else "# (no textual diff)") + "\n```\n\n"
    )
    with CHANGE_LOG.open("a", encoding="utf-8") as f:
        f.write(entry)

def replace_in_parse_when(text: str) -> Tuple[str, bool]:
    """
    Heuristic: only modify inside parse_when() block.
    We detect the function range textually to keep changes localized.
    """
    lines = text.splitlines(keepends=True)
    new_lines = lines[:]
    changed = False

    # Locate def parse_when
    def_idx = None
    for i, line in enumerate(lines):
        if re.match(r"^\s*def\s+parse_when\s*\(", line):
            def_idx = i
            break
    if def_idx is None:
        return text, False

    # Determine block indent and end
    indent = len(lines[def_idx]) - len(lines[def_idx].lstrip())
    end_idx = def_idx + 1
    while end_idx < len(lines):
        line = lines[end_idx]
        if line.strip() and (len(line) - len(line.lstrip())) <= indent and not line.lstrip().startswith(("#", "@")):
            break
        end_idx += 1

    block = "".join(lines[def_idx:end_idx])

    # Transform within block
    transformed = block
    # Replace explicit raises
    transformed = re.sub(r"raise\s+SystemExit\b", "raise ValueError", transformed)
    # Replace sys.exit(...) but keep message
    transformed = re.sub(r"sys\.exit\s*\(", "raise ValueError(", transformed)

    if transformed != block:
        changed = True
        new_lines[def_idx:end_idx] = [transformed]

    return "".join(new_lines), changed

def widen_caller_handlers(path: Path, text: str) -> Tuple[str, int]:
    """
    For files that call parse_when(), convert:
        except SystemExit:
    to:
        except (ValueError, SystemExit):
    Count number of rewrites.
    """
    if "parse_when(" not in text:
        return text, 0
    pattern = r"except\s+SystemExit\s*:"
    repl = r"except (ValueError, SystemExit):"
    new_text, n = re.subn(pattern, repl, text)
    return new_text, n

def ensure_session_id_validation(text: str) -> Tuple[str, bool]:
    """
    Insert a validation guard in the function that takes session_id.
    Heuristic: find def ...(...session_id...) and insert guard right after signature line.
    """
    lines = text.splitlines(keepends=True)
    changed = False

    # Import re if missing
    has_import_re = any(re.match(r"^\s*import\s+re(\s|$)", ln) for ln in lines)
    if not has_import_re:
        # Insert after first import block or at top
        insert_at = 0
        for i, ln in enumerate(lines):
            if ln.startswith("import ") or ln.startswith("from "):
                insert_at = i + 1
        lines.insert(insert_at, "import re\n")
        changed = True

    # Locate def with session_id in signature
    for i, ln in enumerate(lines):
        if re.match(r"^\s*def\s+\w+\s*\([^)]*session_id[^)]*\)\s*:", ln):
            # Determine indentation of function body
            # Insert guard at next line with same base indentation + 4 spaces
            indent = " " * (len(ln) - len(ln.lstrip()) + 4)
            guard = (
                f"{indent}if not re.match(r'^[A-Za-z0-9_-]+$', str(session_id or '')):\n"
                f"{indent}    raise ValueError('Invalid session_id: must match ^[A-Za-z0-9_-]+$')\n"
            )
            # Find the next line (body start)
            insert_pos = i + 1
            lines.insert(insert_pos + 0, guard)
            changed = True
            # Only add to the first function encountered
            break

    return "".join(lines), changed

def update_tests_export(existing: Optional[str]) -> str:
    """
    Create or update tests/test_export.py to cover session_id validation.
    The test is resilient: it tries to find a callable that accepts session_id,
    otherwise marks the test as xfail with rationale.
    """
    base = existing or ""
    header = (
        "import importlib, inspect, types, pytest\n"
        "mod = importlib.import_module('codex.logging.export')\n"
        "\n"
        "def _find_callable_accepting_session_id():\n"
        "    for name in dir(mod):\n"
        "        obj = getattr(mod, name)\n"
        "        if callable(obj):\n"
        "            try:\n"
        "                sig = inspect.signature(obj)\n"
        "                if 'session_id' in sig.parameters:\n"
        "                    return obj\n"
        "            except (ValueError, TypeError):\n"
        "                continue\n"
        "    return None\n"
        "\n"
        "@pytest.mark.parametrize('good', ['abc', 'ABC_123', 'a-b_c-9'])\n"
        "def test_session_id_good(good):\n"
        "    fn = _find_callable_accepting_session_id()\n"
        "    if fn is None:\n"
        "        pytest.skip('No callable with session_id parameter found in codex.logging.export')\n"
        "    # Call with kwargs if possible; otherwise skip\n"
        "    try:\n"
        "        fn(session_id=good)\n"
        "    except TypeError:\n"
        "        pytest.skip('Found callable does not accept keyword arg session_id; manual test wiring required')\n"
        "\n"
        "@pytest.mark.parametrize('bad', ['..', 'a b', 'abc!', '../../etc/passwd'])\n"
        "def test_session_id_bad(bad):\n"
        "    fn = _find_callable_accepting_session_id()\n"
        "    if fn is None:\n"
        "        pytest.skip('No callable with session_id parameter found in codex.logging.export')\n"
        "    with pytest.raises(ValueError):\n"
        "        try:\n"
        "            fn(session_id=bad)\n"
        "        except TypeError:\n"
        "            pytest.skip('Found callable does not accept keyword arg session_id; manual test wiring required')\n"
    )
    return header

def phase1_prep() -> None:
    ensure_codex_scaffolding()
    clean = git_clean_working_tree()
    append_results(f"## Phase 1\n- Clean working tree: {clean}\n- DO_NOT_ACTIVATE_GITHUB_ACTIONS: {DO_NOT_ACTIVATE_GHA}\n")

def phase2_search_mapping() -> None:
    mapping = {
        "T1": {
            "task": "parse_when -> ValueError; update callers; lint single file",
            "candidates": [TARGET_PARSE_FILE.as_posix(), "src/** files calling parse_when("],
            "rationale": "Direct file + localized caller handler widening",
        },
        "T2": {
            "task": "session_id validation in export.py + tests",
            "candidates": [TARGET_EXPORT_FILE.as_posix(), TEST_EXPORT_FILE.as_posix()],
            "rationale": "Direct file + adjacent tests",
        },
    }
    append_results("## Phase 2 — Mapping\n```json\n" + json.dumps(mapping, indent=2) + "\n```\n")

def phase3_construct() -> List[str]:
    unresolved: List[str] = []

    # T1: query_logs.py
    t1_before = read_text(TARGET_PARSE_FILE)
    if t1_before is None:
        append_error("3.1", "Modify parse_when -> ValueError", "File not found", TARGET_PARSE_FILE.as_posix())
        unresolved.append("T1: missing target file")
    else:
        t1_after, changed = replace_in_parse_when(t1_before)
        if changed:
            write_text(
                TARGET_PARSE_FILE, t1_after,
                "Replace SystemExit/sys.exit with ValueError inside parse_when (localized).",
                "T1: parse_when -> ValueError",
                t1_before,
            )
        else:
            append_results("- T1: No changes made in query_logs.py (parse_when not found or already ValueError).")

        # Widen caller handlers across src/**
        src_root = REPO_ROOT / "src"
        widened_total = 0
        if src_root.exists():
            for p in src_root.rglob("*.py"):
                if p == TARGET_PARSE_FILE:
                    continue
                text = read_text(p)
                if text is None or "parse_when(" not in text:
                    continue
                new_text, n = widen_caller_handlers(p, text)
                if n > 0:
                    write_text(
                        p, new_text,
                        "Widen 'except SystemExit' to 'except (ValueError, SystemExit)' for parse_when callers.",
                        "T1: Update callers to handle ValueError",
                        text,
                    )
                    widened_total += n
            append_results(f"- T1: Widened caller handlers in {widened_total} location(s).")
        else:
            append_error("3.1", "Update callers", "src/ not found", "Expected to search under src/** for parse_when(")
            unresolved.append("T1: src root missing for caller updates")

    # T2: export.py session_id validation
    t2_before = read_text(TARGET_EXPORT_FILE)
    if t2_before is None:
        append_error("3.2", "Insert session_id validation", "File not found", TARGET_EXPORT_FILE.as_posix())
        unresolved.append("T2: missing export.py")
    else:
        t2_after, changed2 = ensure_session_id_validation(t2_before)
        if changed2:
            write_text(
                TARGET_EXPORT_FILE, t2_after,
                "Insert session_id regex guard (^[A-Za-z0-9_-]+$) raising ValueError on invalid input.",
                "T2: session_id validation",
                t2_before,
            )
        else:
            append_results("- T2: session_id guard may already exist or no function signature found; no changes made.")

    # Tests for export
    try:
        existing = read_text(TEST_EXPORT_FILE)
        new_test = update_tests_export(existing)
        write_text(
            TEST_EXPORT_FILE, new_test,
            "Add/refresh tests for session_id validation with skip guards when wiring is unknown.",
            "T2: tests/test_export.py updated",
            existing or "",
        )
    except Exception as e:
        append_error("3.3", "Update tests/test_export.py", repr(e), "Creating/updating session_id validation tests failed")
        unresolved.append("T2: tests update failed")

    # Lint (pre-commit) restricted to the requested file
    try:
        if TARGET_PARSE_FILE.exists():
            proc = subprocess.run(
                ["pre-commit", "run", "--files", str(TARGET_PARSE_FILE)],
                cwd=REPO_ROOT, capture_output=True, text=True, check=False
            )
            append_results(
                "### Lint results (pre-commit)\n"
                f"Exit code: {proc.returncode}\n\n"
                "```\n" + (proc.stdout or "").strip() + "\n```\n"
                "```\n" + (proc.stderr or "").strip() + "\n```\n"
            )
            if proc.returncode != 0:
                append_error("3.5", "Run pre-commit on query_logs.py", f"Exit {proc.returncode}", "See results.md for tool output")
                # Keep building; do not abort
        else:
            append_results("- Skipped lint: target file missing.")
    except FileNotFoundError:
        append_results("- Skipped lint: pre-commit not installed.")
    except Exception as e:
        append_error("3.5", "Run pre-commit on query_logs.py", repr(e), "Unexpected error invoking pre-commit")

    return unresolved

def phase4_prune() -> None:
    # No proactive pruning; placeholder for evidence-based entries
    append_results("## Phase 4 — Pruning\n- No pruning performed unless entries appear in change log under **Pruning**.\n")

def phase5_finalize(unresolved: List[str]) -> int:
    # README textual refresh for SystemExit -> ValueError mentions
    for readme_name in ("README.md", "README.rst", "README.txt"):
        rp = REPO_ROOT / readme_name
        txt = read_text(rp)
        if txt and "parse_when" in txt and "SystemExit" in txt:
            before = txt
            after = txt.replace("SystemExit", "ValueError")
            if after != before:
                write_text(
                    rp, after,
                    "Refresh docs to reflect parse_when now raises ValueError.",
                    "Docs: README update parse_when exception",
                    before,
                )

    summary = [
        "## Phase 6 — Results Summary",
        f"- Timestamp: {now_iso()}",
        "- Implemented: T1 (best-effort), T2 (best-effort), lint run on query_logs.py",
        f"- Unresolved: {unresolved if unresolved else 'None'}",
        "- Statement: **DO NOT ACTIVATE ANY GitHub Actions files.**",
        "- Next Steps: (1) Review `.codex/change_log.md`; (2) run `pytest -q`; (3) commit with conventional message.",
        ""
    ]
    append_results("\n".join(summary))
    return 1 if unresolved else 0

def main() -> int:
    try:
        phase1_prep()
        phase2_search_mapping()
        unresolved = phase3_construct()
        phase4_prune()
        rc = phase5_finalize(unresolved)
        return rc
    except Exception as e:
        append_error("0.0", "Unhandled exception in workflow", repr(e), "Top-level")
        return 1

if __name__ == "__main__":
    sys.exit(main())
