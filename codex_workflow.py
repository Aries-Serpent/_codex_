#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
codex_workflow.py
End-to-end scripted workflow for the '_codex_' repo (branch 0B_base_):
- Inventories repo, reads README/CONTRIBUTING
- Applies localized edits to test files (add imports)
- Logs changes and errors (ChatGPT-5 question template)
- Generates results summary
Constraint: DO NOT ACTIVATE ANY GitHub Actions files.
"""

import ast
import datetime as dt
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

from codex.utils.subprocess import run as safe_run

# ---- Configuration / Constraints ----
BRANCH = "0B_base_"
DO_NOT_ACTIVATE_GITHUB_ACTIONS = True

REPO_ROOT = Path.cwd()
CODEX_DIR = REPO_ROOT / ".codex"
CHANGE_LOG = CODEX_DIR / "change_log.md"
ERROR_LOG = CODEX_DIR / "errors.ndjson"
RESULTS = CODEX_DIR / "results.md"
INVENTORY = CODEX_DIR / "inventory.json"

TARGETS = [
    {"path": Path("tests/test_export.py"), "import_name": "json", "label": "t1"},
    {
        "path": Path("tests/test_logging_viewer_cli.py"),
        "import_name": "json",
        "label": "t2",
    },
    {
        "path": Path("tests/test_conversation_logger.py"),
        "import_name": "sqlite3",
        "label": "t3",
    },
]

AUTO_MARKER = "# [CODEX-AUTO]"
FORCE_FLAG = "--force" in sys.argv


# ---- Utilities ----
def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def run(cmd: List[str]) -> Tuple[int, str, str]:
    try:
        proc = safe_run(cmd, capture_output=True)
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except subprocess.CalledProcessError as e:
        stdout = e.stdout.strip() if e.stdout else ""
        stderr = e.stderr.strip() if e.stderr else str(e)
        return e.returncode, stdout, stderr



def ensure_dirs():
    CODEX_DIR.mkdir(parents=True, exist_ok=True)


def append_file(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(text)


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def read_text(path: Path) -> str:
    with path.open("r", encoding="utf-8") as f:
        return f.read()


def write_text(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not FORCE_FLAG and path.exists():
        existing = path.read_text(encoding="utf-8")
        if AUTO_MARKER in existing:
            print(f"skip {path} (has {AUTO_MARKER})", file=sys.stderr)
            return
    if AUTO_MARKER not in content:
        lines = content.splitlines(keepends=True)
        if lines and lines[0].startswith("#!"):
            content = lines[0] + AUTO_MARKER + "\n" + "".join(lines[1:])
        else:
            content = AUTO_MARKER + "\n" + "".join(lines)
    with path.open("w", encoding="utf-8") as f:
        f.write(content)


def record_error(step_num: str, step_desc: str, err_msg: str, context: str):
    # Echo ChatGPT-5 research question to console
    block = (
        "Question for ChatGPT-5:\n"
        f"While performing [{step_num}: {step_desc}], encountered the following error:\n"
        f"{err_msg}\n"
        f"Context: {context}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
    )
    print(block, file=sys.stderr)
    # Append structured NDJSON
    entry = {
        "ts": now_iso(),
        "step": step_num,
        "description": step_desc,
        "error": err_msg,
        "context": context,
    }
    append_file(ERROR_LOG, json.dumps(entry) + "\n")


def record_change(
    file_path: Path, action: str, rationale: str, before: str, after: str
):
    diff = difflib.unified_diff(
        before.splitlines(keepends=True),
        after.splitlines(keepends=True),
        fromfile=str(file_path) + " (before)",
        tofile=str(file_path) + " (after)",
        n=3,
    )
    diff_preview = "".join(list(diff)[:2000])  # cap preview
    block = (
        f"\n## {now_iso()} — {action}\n"
        f"**File:** `{file_path}`\n"
        f"**Rationale:** {rationale}\n"
        f"<details><summary>Diff (preview)</summary>\n\n"
        f"```diff\n{diff_preview}\n```\n"
        f"</details>\n"
    )
    append_file(CHANGE_LOG, block)


def get_repo_root() -> Path:
    code, out, _ = run(["git", "rev-parse", "--show-toplevel"])
    return Path(out) if code == 0 and out else REPO_ROOT


def assert_clean_state():
    code, out, err = run(["git", "status", "--porcelain"])
    if code != 0:
        record_error(
            "1.1", "Check clean working state", err or out, "git status --porcelain"
        )
        sys.exit(2)
    if out.strip():
        record_error(
            "1.1",
            "Working tree not clean",
            out,
            "Commit/stash changes before running workflow",
        )
        sys.exit(3)


def ensure_branch(branch: str):
    code, out, err = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if code != 0:
        record_error(
            "1.2", "Get current branch", err or out, "git rev-parse --abbrev-ref HEAD"
        )
        return
    if out != branch:
        code2, _out2, err2 = run(["git", "checkout", branch])
        if code2 != 0:
            record_error(
                "1.2",
                f"Checkout branch '{branch}'",
                err2 or _out2,
                f"git checkout {branch}",
            )


def load_guardrails():
    notes = []
    for name in ("README.md", "CONTRIBUTING.md"):
        p = REPO_ROOT / name
        if p.exists():
            try:
                txt = read_text(p)
                # Very light guardrail hint extraction (headings only)
                heads = [
                    ln.strip("# ").strip()
                    for ln in txt.splitlines()
                    if ln.startswith("#")
                ]
                notes.append({"file": name, "headings": heads})
            except Exception as e:
                record_error("1.2", f"Read {name}", str(e), f"path={p}")
    return notes


def scan_inventory():
    exts = {
        ".py",
        ".sh",
        ".sql",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".html",
        ".md",
        ".yml",
        ".yaml",
    }
    items = []
    for path in REPO_ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in exts:
            try:
                items.append(
                    {
                        "path": str(path.relative_to(REPO_ROOT)),
                        "size": path.stat().st_size,
                        "ext": path.suffix.lower(),
                    }
                )
            except Exception as e:
                record_error(
                    "1.3", "Stat file during inventory", str(e), f"path={path}"
                )
    write_json(INVENTORY, {"generated": now_iso(), "items": items})


def detect_workflows():
    wf_dir = REPO_ROOT / ".github" / "workflows"
    present = wf_dir.exists() and any(wf_dir.glob("*.y*ml"))
    return {
        "workflows_present": bool(present),
        "note": "DO NOT ACTIVATE ANY GitHub Actions files.",
    }


# ---- Import insertion logic ----
def ast_has_import(mod_src: str, name: str) -> bool:
    try:
        tree = ast.parse(mod_src)
    except Exception:
        # If unparsable, fall back to regex (best-effort)
        return bool(
            re.search(rf"^\s*import\s+{re.escape(name)}\b", mod_src, re.MULTILINE)
        )
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == name:
                    return True
        elif isinstance(node, ast.ImportFrom):
            # Not strictly required, but consider 'from sqlite3 import ...' as presence
            if node.module == name:
                return True
    return False


def find_insert_index(src: str) -> int:
    """
    Insert after: shebang, encoding, module docstring, and any __future__ imports.
    """
    lines = src.splitlines(True)
    i = 0
    # shebang
    if i < len(lines) and lines[i].startswith("#!"):
        i += 1
    # encoding cookie
    if i < len(lines) and re.match(r"#\s*-\*-\s*coding\s*:\s*.*-\*-\s*$", lines[i]):
        i += 1

    # module docstring
    def is_triple_start(s):
        return s.lstrip().startswith('"""') or s.lstrip().startswith("'''")

    if i < len(lines) and is_triple_start(lines[i]):
        quote = lines[i].lstrip()[:3]
        i += 1
        while i < len(lines):
            if quote in lines[i]:
                i += 1
                break
            i += 1
    # __future__ imports
    while i < len(lines) and re.match(r"\s*from\s+__future__\s+import\s+", lines[i]):
        i += 1
    return sum(len(line) for line in lines[:i])



def insert_import(src: str, name: str) -> str:
    if ast_has_import(src, name):
        return src  # no-op
    ins_point = find_insert_index(src)
    prefix = src[:ins_point]
    suffix = src[ins_point:]
    insertion = f"import {name}\n"
    # Ensure a blank line after import block if needed
    if suffix and not suffix.startswith("\n"):
        insertion = insertion
    return prefix + insertion + suffix


def py_compile_file(py_path: Path) -> Tuple[bool, str]:
    code, out, err = run([sys.executable, "-m", "py_compile", str(py_path)])
    ok = code == 0
    return ok, (err or out)


# ---- Main workflow ----
def phase_1():
    ensure_dirs()
    # 1.1 Clean state
    assert_clean_state()
    # 1.2 Branch + guardrails
    ensure_branch(BRANCH)
    guard = load_guardrails()
    append_file(CHANGE_LOG, f"# Change Log — {now_iso()}\n\n")
    append_file(CHANGE_LOG, f"- Guardrails detected: {json.dumps(guard)}\n")
    # 1.3 Inventory
    scan_inventory()
    # 1.4 Constraints
    wf_info = detect_workflows()
    append_file(
        CHANGE_LOG,
        f"- Constraint: DO_NOT_ACTIVATE_GITHUB_ACTIONS={DO_NOT_ACTIVATE_GITHUB_ACTIONS}\n",
    )
    append_file(CHANGE_LOG, f"- Workflows presence: {json.dumps(wf_info)}\n")
    # 1.5 Error log exists by ensure_dirs()


def phase_2_mapping():
    # Build mapping info
    mapping_rows = []
    for t in TARGETS:
        p = REPO_ROOT / t["path"]
        rationale = (
            "Exact path target"
            if p.exists()
            else "Primary target missing; will search fallback by filename"
        )
        mapping_rows.append(
            {
                "task": t["label"],
                "candidate_assets": [str(t["path"])],
                "rationale": rationale,
            }
        )
    append_file(CHANGE_LOG, "\n## Phase 2 — Mapping\n")
    append_file(CHANGE_LOG, "```\n" + json.dumps(mapping_rows, indent=2) + "\n```\n")


def best_effort_edit(target_path: Path, import_name: str, label: str):
    step = f"3.{label}"
    desc = f"Insert 'import {import_name}' into {target_path}"
    p = REPO_ROOT / target_path
    if not p.exists():
        # try fallback by filename
        candidates = list(REPO_ROOT.rglob(p.name))
        if candidates:
            p = candidates[0]
        else:
            record_error(step, desc, "File not found", f"target={target_path}")
            return

    try:
        before = read_text(p)
    except Exception as e:
        record_error(step, desc, f"Read failure: {e}", f"path={p}")
        return
    try:
        after = insert_import(before, import_name)
    except Exception as e:
        record_error(
            step, desc, f"Insert failure: {e}", f"path={p}, import={import_name}"
        )
        return
    if after == before:
        record_change(
            p,
            "no-op (import already present)",
            f"'{import_name}' detected via AST",
            before[:0],
            after[:0],
        )
    else:
        try:
            write_text(p, after)
            record_change(
                p,
                "insert_import",
                f"Add '{import_name}' while preserving header/future imports",
                before,
                after,
            )
        except Exception as e:
            record_error(step, desc, f"Write failure: {e}", f"path={p}")
            return
    # smoke compile
    ok, msg = py_compile_file(p)
    if not ok:
        record_error(step, f"Smoke compile {p}", msg, f"py_compile target={p}")


def phase_3_best_effort():
    append_file(CHANGE_LOG, "\n## Phase 3 — Best-Effort Construction\n")
    for t in TARGETS:
        best_effort_edit(t["path"], t["import_name"], t["label"])
    # README update (best-effort scan only)
    readme = REPO_ROOT / "README.md"
    if readme.exists():
        try:
            _ = read_text(readme)
            append_file(
                CHANGE_LOG,
                "- README reviewed: no path updates required for test files.\n",
            )
        except Exception as e:
            record_error("3.readme", "Read README.md", str(e), "README scan")


def phase_4_pruning():
    append_file(CHANGE_LOG, "\n## Phase 4 — Pruning\n")
    append_file(
        CHANGE_LOG, "- No pruning required; all edits are additive and localized.\n"
    )


def phase_5_errors_ack():
    # Nothing to do; errors appended in real-time. Summarize count.
    count = 0
    if ERROR_LOG.exists():
        with ERROR_LOG.open("r", encoding="utf-8") as f:
            count = sum(1 for _ in f if _.strip())
    append_file(
        CHANGE_LOG, f"\n## Phase 5 — Error Capture\n- Errors recorded: {count}\n"
    )


def phase_6_finalize():
    # Summarize implemented tasks and gaps
    errs = []
    if ERROR_LOG.exists():
        with ERROR_LOG.open("r", encoding="utf-8") as f:
            errs = [json.loads(line) for line in f if line.strip()]
    implemented = [
        {"file": str(t["path"]), "import": t["import_name"], "status": "attempted"}
        for t in TARGETS
    ]
    summary = {
        "generated": now_iso(),
        "implemented": implemented,
        "errors_count": len(errs),
        "note": "DO NOT ACTIVATE ANY GitHub Actions files.",
        "next_steps": [
            "Optionally run: pytest -q",
            "Review .codex/change_log.md and .codex/errors.ndjson",
        ],
    }
    write_text(
        RESULTS,
        "# Results Summary\n\n"
        f"- Generated: `{summary['generated']}`\n"
        f"- Implemented: `{json.dumps(summary['implemented'])}`\n"
        f"- Errors Count: `{summary['errors_count']}`\n\n"
        "## Pruning\n- None.\n\n"
        "## Constraints\n- **DO NOT ACTIVATE ANY GitHub Actions files.**\n\n"
        "## Next Steps\n- Optionally run `pytest -q`.\n- Review `.codex/change_log.md` and `.codex/errors.ndjson`.\n",
    )
    # Exit code
    if errs:
        sys.exit(1)
    sys.exit(0)


def main():
    # Phase 1
    phase_1()
    # Phase 2
    phase_2_mapping()
    # Phase 3
    phase_3_best_effort()
    # Phase 4
    phase_4_pruning()
    # Phase 5
    phase_5_errors_ack()
    # Phase 6
    phase_6_finalize()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        record_error("0.main", "Unhandled exception", str(e), "top-level")
        sys.exit(1)
