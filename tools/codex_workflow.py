#!/usr/bin/env python3
# tools/codex_workflow.py
# End-to-end orchestrator for the `_codex_` repo task on branch `0B_base_`.
# Performs best-effort construction, controlled pruning, error capture, and finalization.
# IMPORTANT: DO NOT ACTIVATE ANY GitHub Actions files.

import argparse
import dataclasses
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

DO_NOT_ACTIVATE_GITHUB_ACTIONS = True
REPO_REL_TARGET = Path("scripts/apply_session_logging_workflow.py")  # primary asset


# -------------------- Utilities --------------------


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def run(cmd: List[str], cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    try:
        p = subprocess.Popen(
            cmd,
            cwd=str(cwd) if cwd else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        out, err = p.communicate()
        return p.returncode, out, err
    except FileNotFoundError as e:
        return 127, "", str(e)


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def read_text(p: Path) -> Optional[str]:
    try:
        return p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def write_text(p: Path, content: str, apply: bool):
    if not apply:
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def append_text(p: Path, content: str, apply: bool):
    if not apply:
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(content)


def unified_diff(old: str, new: str, path: str) -> str:
    return "".join(
        difflib.unified_diff(
            old.splitlines(keepends=True),
            new.splitlines(keepends=True),
            fromfile=f"a/{path}",
            tofile=f"b/{path}",
            lineterm="",
        )
    )


def is_git_repo(root: Path) -> bool:
    code, out, _ = run(["git", "rev-parse", "--is-inside-work-tree"], cwd=root)
    return code == 0 and out.strip() == "true"


def git_clean_status(root: Path) -> str:
    code, out, err = run(["git", "status", "--porcelain"], cwd=root)
    if code != 0:
        return f"(non-git or error: {err.strip()})"
    return out.strip() or "(clean)"


# -------------------- Logging --------------------

ROOT = Path.cwd()
CODEX_DIR = ROOT / ".codex"
CHANGE_LOG = CODEX_DIR / "change_log.md"
ERRORS_LOG = CODEX_DIR / "errors.ndjson"
RESULTS_MD = CODEX_DIR / "results.md"


@dataclasses.dataclass
class ChangeEntry:
    file: str
    action: str
    rationale: str
    diff: str


def log_change(entry: ChangeEntry, apply: bool):
    header = f"\n### {entry.action}: `{entry.file}`\n"
    body = (
        f"- When: {now_iso()}\n- Rationale: {entry.rationale}\n\n<details><summary>Diff</summary>\n\n```diff\n{entry.diff}\n```\n\n</details>\n"
    )
    append_text(CHANGE_LOG, header + body, apply)


def log_error(step_number: str, step_desc: str, error_message: str, context: str, apply: bool):
    # Echo in required ChatGPT-5 format
    msg = (
        "Question for ChatGPT-5:\n"
        f"While performing [{step_number}: {step_desc}], encountered the following error:\n"
        f"{error_message}\n"
        f"Context: {context}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
    )
    sys.stderr.write(msg + "\n")
    # Append NDJSON
    record = {
        "ts": now_iso(),
        "step": step_number,
        "description": step_desc,
        "error": error_message,
        "context": context,
    }
    append_text(ERRORS_LOG, json.dumps(record) + "\n", apply)


# -------------------- Phase 1: Preparation --------------------


def phase1_preparation(apply: bool):
    ensure_dir(CODEX_DIR)
    # Initialize change log with header if empty
    if not CHANGE_LOG.exists() and apply:
        CHANGE_LOG.write_text(f"# Codex Change Log\nInitialized: {now_iso()}\n", encoding="utf-8")
    if not ERRORS_LOG.exists() and apply:
        ERRORS_LOG.write_text("", encoding="utf-8")

    # Identify repo root & clean state
    repo_flag = is_git_repo(ROOT)
    status_str = git_clean_status(ROOT)
    # Inventory
    exts = (".py", ".sh", ".sql", ".js", ".ts", ".html", ".md")
    inventory = []
    for p in ROOT.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts and ".git" not in p.parts and ".venv" not in p.parts:
            rel = p.relative_to(ROOT).as_posix()
            role = "code" if p.suffix.lower() in (".py", ".sh", ".sql", ".js", ".ts") else "doc"
            inventory.append({"path": rel, "role": role})
    inv_md = [
        "# Inventory (lightweight)",
        f"_Generated: {now_iso()}_\n",
        f"- Git repo: {repo_flag}",
        f"- Working state: {status_str}\n",
        "## Files",
    ]
    inv_md += [f"- `{i['path']}` ({i['role']})" for i in sorted(inventory, key=lambda x: x["path"])]
    append_text(RESULTS_MD, "\n".join(inv_md) + "\n", apply)


# -------------------- Phase 2 & 3: Mapping + Construction --------------------


EXCEPT_PATTERN = re.compile(
    r"(?P<indent>^[ \t]*)except\s+FileNotFoundError(?:\s+as\s+\w+)?\s*:\s*\n(?P<body>(?:[ \t]*#.*\n|[ \t]*[^\S\r\n]*\n|[ \t]*pass[ \t]*\n|[ \t]*\.\.\.[ \t]*\n)+)",
    re.MULTILINE,
)


def ensure_import_sys(src: str) -> str:
    # Inject 'import sys' if not present (and respect typical top-of-file import block).
    if re.search(r"^\s*import\s+sys\b", src, flags=re.MULTILINE):
        return src
    # Insert after shebang/encoding/comments/import block
    lines = src.splitlines()
    insert_idx = 0
    while insert_idx < len(lines) and (
        lines[insert_idx].startswith("#!")
        or lines[insert_idx].startswith("# -*- coding:")
        or lines[insert_idx].strip().startswith("#")
        or lines[insert_idx].strip() == ""
    ):
        insert_idx += 1
    while insert_idx < len(lines) and re.match(r"^\s*(from\s+\S+\s+import|import\s+\S+)", lines[insert_idx]):
        insert_idx += 1
    lines.insert(insert_idx, "import sys")
    return "\n".join(lines) + ("\n" if src.endswith("\n") else "")


def replace_bare_except(src: str) -> Tuple[str, int]:
    """
    Replace 'except FileNotFoundError: pass/...' with a warning + sys.exit(2).
    Returns (new_src, replacements_count).
    """

    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        indent = m.group("indent")
        new_block = (
            f"{indent}except FileNotFoundError as e:\n"
            f"{indent}    sys.stderr.write(\n"
            f'{indent}        "WARNING: Git is required for this operation. Please install Git (https://git-scm.com/) and ensure this script is run inside a Git repository. Details: {{}}\\n".format(str(e))\n'
            f"{indent}    )\n"
            f"{indent}    sys.exit(2)\n"
        )
        count += 1
        return new_block

    new_src = EXCEPT_PATTERN.sub(repl, src)
    return new_src, count


def phase2_3_construct(apply: bool, errors: List[str]):
    step = "2-3"
    target = ROOT / REPO_REL_TARGET
    original = read_text(target)
    if original is None:
        log_error(
            step,
            "Locate target file",
            f"File not found: {REPO_REL_TARGET}",
            "Ensure scripts/apply_session_logging_workflow.py exists on branch 0B_base_.",
            apply,
        )
        errors.append("missing-target")
        return

    transformed = ensure_import_sys(original)
    transformed, n_repl = replace_bare_except(transformed)

    if n_repl == 0:
        log_error(
            step,
            "Pattern replace",
            "No 'except FileNotFoundError: pass' (or '...') pattern found.",
            "The block may differ in indentation/content or lines have shifted; verify lines 40–46.",
            apply,
        )

    if transformed != original:
        diff = unified_diff(original, transformed, REPO_REL_TARGET.as_posix())
        rationale = (
            "Replace bare 'except FileNotFoundError' with actionable warning and graceful exit; inject 'import sys' if absent; localized, minimal-risk change."
        )
        if apply:
            backup = target.with_suffix(target.suffix + ".bak")
            shutil.copyfile(target, backup)
            write_text(target, transformed, apply=True)
        log_change(
            ChangeEntry(
                file=str(REPO_REL_TARGET),
                action="Modify",
                rationale=rationale,
                diff=diff,
            ),
            apply,
        )
    else:
        append_text(
            RESULTS_MD,
            f"\nNo changes applied to `{REPO_REL_TARGET}` (content already compliant or pattern not found).\n",
            apply,
        )

    after_content = transformed
    ok_msg = bool(
        re.search(r"WARNING: Git is required for this operation", after_content)
    ) and ("sys.exit(2)" in after_content)
    if not ok_msg:
        log_error(
            "3.4",
            "Smoke check",
            "Post-change content missing WARNING message or sys.exit(2).",
            "Verify replacement and imports were injected correctly.",
            apply,
        )


# -------------------- Phase 6: Finalization --------------------


def finalize(apply: bool, had_errors: bool):
    summary = [
        "\n# Results Summary",
        f"- Timestamp: {now_iso()}",
        "- Implemented: Replace bare FileNotFoundError handler with warning + exit(2); ensured 'import sys'.",
        "- Residual gaps: See `.codex/errors.ndjson` entries (if any).",
        "- Prune index: None.",
        "- Next steps: Review script runtime paths; consider README prerequisites section if missing.",
        "\n**DO NOT ACTIVATE ANY GitHub Actions files.**\n",
    ]
    append_text(RESULTS_MD, "\n".join(summary) + "\n", apply)
    if had_errors:
        sys.exit(1)
    sys.exit(0)


# -------------------- Main --------------------


def main():
    parser = argparse.ArgumentParser(description="Codex workflow orchestrator")
    parser.add_argument(
        "--yes", action="store_true", help="Apply changes (consent). Otherwise dry-run."
    )
    args = parser.parse_args()

    user_consent = args.yes or (os.getenv("CODEX_USER_CONSENT") == "1")
    apply = bool(user_consent)

    phase1_preparation(apply=apply)

    errors: List[str] = []
    if DO_NOT_ACTIVATE_GITHUB_ACTIONS:
        append_text(RESULTS_MD, "\nConstraint: DO_NOT_ACTIVATE_GITHUB_ACTIONS = true\n", apply)

    try:
        phase2_3_construct(apply=apply, errors=errors)
    except Exception as e:
        log_error(
            "2-3",
            "Construct & replace",
            repr(e),
            "Unexpected exception during transformation.",
            apply,
        )
        errors.append("construct-exception")

    had_errors = len(errors) > 0
    finalize(apply=apply, had_errors=had_errors)


if __name__ == "__main__":
    main()

