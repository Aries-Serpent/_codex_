#!/usr/bin/env python3
# tools/unify_logging_canonical.py
# Purpose: Make src/codex/logging canonical, wrap/retire legacy modules, normalize imports, and document everything.

import os, sys, re, json, subprocess, hashlib, datetime, shutil
from pathlib import Path
from typing import List, Tuple, Dict

# ---------------------------
# Config / Constraints
# ---------------------------
REPO_ROOT = Path(os.getcwd())
CODEX_DIR = REPO_ROOT / ".codex"
CHANGE_LOG = CODEX_DIR / "change_log.md"
ERRORS_NDJSON = CODEX_DIR / "errors.ndjson"
RESULTS_MD = CODEX_DIR / "results.md"

DO_NOT_ACTIVATE_GITHUB_ACTIONS = True
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".mypy_cache", ".ruff_cache", ".pytest_cache"}
if DO_NOT_ACTIVATE_GITHUB_ACTIONS:
    SKIP_DIRS |= {".github", ".github/workflows"}

CANONICAL_DIR = REPO_ROOT / "src" / "codex" / "logging"
LEGACY_WRAPPERS = {
    REPO_ROOT / "codex" / "logging" / "session_logger.py": "src.codex.logging.session_logger",
    REPO_ROOT / "codex" / "logging" / "session_query.py": "src.codex.logging.query_logs",  # maps "session_query" -> "query_logs"
}

# Patterns for import normalization
IMPORT_PATTERNS = [
    # from codex.logging.x import Y -> from src.codex.logging.x import Y
    (re.compile(r"\bfrom\s+codex\.logging(\b|\.)"), "from src.codex.logging\\1"),
    # import codex.logging.x -> import src.codex.logging.x
    (re.compile(r"\bimport\s+codex\.logging(\b|\.)"), "import src.codex.logging\\1"),
]
# CLI/module invocations in docs
DOC_PATTERNS = [
    (re.compile(r"\bpython(?:3)?\s+-m\s+codex\.logging\."), "python -m src.codex.logging."),
]

# ---------------------------
# Utilities
# ---------------------------

def now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def sh(cmd: List[str]) -> Tuple[int, str, str]:
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return p.returncode, out, err

def record_change(path: Path, action: str, rationale: str, before: str = "", after: str = "") -> None:
    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    CHANGE_LOG.touch(exist_ok=True)
    with CHANGE_LOG.open("a", encoding="utf-8") as f:
        f.write(f"\n### [{now_iso()}] {action}\n")
        f.write(f"- **File:** `{path.as_posix()}`\n- **Rationale:** {rationale}\n")
        if before or after:
            f.write("\n- **Before (hash/preview):**\n\n````\n")
            f.write(before[:4000])
            f.write("\n````\n- **After (hash/preview):**\n\n````\n")
            f.write(after[:4000])
            f.write("\n````\n")
        # Append git diff snippet if available
        rc, out, _ = sh(["git", "diff", "--", str(path)])
        if rc == 0 and out.strip():
            f.write("\n- **git diff snippet:**\n\n```diff\n")
            f.write(out[:8000])
            f.write("\n```\n")

def hash_preview(s: str) -> str:
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()[:12]
    preview = s.splitlines()[0] if s else ""
    return f"sha256:{h} :: {preview[:200]}"

def append_error(step: str, desc: str, message: str, context: str) -> None:
    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    ERRORS_NDJSON.touch(exist_ok=True)
    question_block = (
        "Question for ChatGPT-5:\n"
        f"While performing [{step}: {desc}], encountered the following error:\n"
        f"{message}\n"
        f"Context: {context}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
    )
    rec = {
        "ts": now_iso(),
        "step": step,
        "description": desc,
        "message": message,
        "context": context,
        "question_block": question_block,
    }
    with ERRORS_NDJSON.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    # Echo to console as required
    print(question_block, file=sys.stderr)

def ensure_clean_worktree() -> None:
    rc, out, err = sh(["git", "status", "--porcelain"])
    if rc != 0:
        append_error("1.1", "Verify clean worktree", err.strip() or out.strip(), "git status failed")
        sys.exit(1)
    if out.strip():
        append_error("1.1", "Verify clean worktree", "Working tree is not clean", out.strip())
        sys.exit(1)

def load_readmes() -> None:
    for p in [REPO_ROOT / "README.md", REPO_ROOT / "README_UPDATED.md"]:
        if p.exists():
            try:
                _ = p.read_text(encoding="utf-8")
            except Exception as e:
                append_error("1.2", f"Read {p.name}", str(e), str(p))

def build_inventory() -> List[Path]:
    collected = []
    for root, dirs, files in os.walk(REPO_ROOT):
        root_p = Path(root)
        # Skip unwanted dirs
        if any(seg in SKIP_DIRS for seg in root_p.parts):
            continue
        for fn in files:
            collected.append(root_p / fn)
    return collected

def write_header_logs() -> None:
    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    if not CHANGE_LOG.exists():
        CHANGE_LOG.write_text("# Change Log\n", encoding="utf-8")
    if not ERRORS_NDJSON.exists():
        ERRORS_NDJSON.write_text("", encoding="utf-8")

def make_wrapper(path: Path, target_module: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = (
        "# Auto-generated thin wrapper. DO NOT add side effects.\n"
        "# This module re-exports the canonical implementation.\n"
        f"from {target_module} import *  # noqa: F401,F403\n"
        "__all__ = [name for name in globals().keys() if not name.startswith('_')]\n"
    )
    before = ""
    if path.exists():
        try:
            before = hash_preview(path.read_text(encoding="utf-8"))
        except Exception:
            before = "<unreadable>"
    path.write_text(content, encoding="utf-8")
    after = hash_preview(content)
    record_change(path, "CREATE_WRAPPER" if not before else "REPLACE_WITH_WRAPPER",
                  f"Legacy -> canonical re-export ({target_module})", before, after)

def normalize_file_text(path: Path) -> Tuple[bool, str, str]:
    try:
        txt = path.read_text(encoding="utf-8")
    except Exception as e:
        append_error("3.3", f"Read file for normalization: {path}", str(e), str(path))
        return False, "", ""
    before = txt
    for pat, rep in IMPORT_PATTERNS:
        txt = re.sub(pat, rep, txt)
    # Docs/README tweaks
    for pat, rep in DOC_PATTERNS:
        txt = re.sub(pat, rep, txt)
    changed = txt != before
    if changed:
        try:
            path.write_text(txt, encoding="utf-8")
            record_change(path, "MODIFY_IMPORTS/DOCS",
                          "Normalize imports to src.codex.logging and CLI invocations",
                          hash_preview(before), hash_preview(txt))
        except Exception as e:
            append_error("3.3", f"Write normalized file: {path}", str(e), str(path))
            return False, before, before
    return changed, before, txt

def normalize_imports_across_repo(inventory: List[Path]) -> int:
    changes = 0
    for p in inventory:
        if p.suffix.lower() not in {".py", ".md", ".rst", ".txt", ".sh"}:
            continue
        if any(seg in SKIP_DIRS for seg in p.parts):
            continue
        chg, _, _ = normalize_file_text(p)
        if chg:
            changes += 1
    return changes

def smoke_checks() -> None:
    # Minimal import checks
    def try_import(mod: str, step: str):
        try:
            __import__(mod)
        except Exception as e:
            append_error(step, f"import {mod}", repr(e), f"Attempted to import {mod}")

    try_import("src.codex.logging", "3.4")
    # common submodules often referenced in README
    for sub in ("src.codex.logging.viewer", "src.codex.logging.query_logs", "src.codex.logging.export"):
        try_import(sub, "3.4")

def write_results_summary(changed_count: int, wrappers: Dict[str, str]) -> None:
    lines = []
    lines.append("# Results Summary")
    lines.append("")
    lines.append("## Implemented")
    lines.append(f"- Canonical package: `src/codex/logging/`")
    lines.append(f"- Wrappers created/replaced:")
    for k, v in wrappers.items():
        lines.append(f"  - `{Path(k).as_posix()}` → `from {v} import *`")
    lines.append(f"- Files normalized (imports/docs): {changed_count}")
    lines.append("")
    lines.append("## Prune Index")
    lines.append("- None removed in this pass (wrappers retained for back-compat).")
    lines.append("")
    lines.append("## Next Steps")
    lines.append("- After downstream consumers migrate to `src.codex.logging.*`, consider deleting legacy wrappers.")
    lines.append("")
    lines.append("## Important")
    lines.append("**DO NOT ACTIVATE ANY GitHub Actions files.**")
    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

def main() -> int:
    write_header_logs()

    # 1.1 Verify clean worktree
    ensure_clean_worktree()

    # 1.2 Read guardrails
    load_readmes()

    # 1.3 Inventory
    inventory = build_inventory()

    # Sanity: canonical dir present
    if not CANONICAL_DIR.exists():
        append_error("2.2", "Locate canonical src/codex/logging", "Canonical directory not found",
                     str(CANONICAL_DIR))
        # Stop — we cannot safely proceed
        return 1

    # 3.1/3.2 Create or replace wrappers for legacy modules
    effective_wrappers = {}
    for legacy_path, target_module in LEGACY_WRAPPERS.items():
        # Only create wrapper if target import appears plausible; otherwise record an error and skip creating a broken shim.
        # We'll attempt a speculative dynamic import after writing a temp file, but safer is to check existence of canonical .py
        target_hint = target_module.split(".")[-1] + ".py"
        expected = CANONICAL_DIR / target_hint
        if not expected.exists():
            # Not fatal for session_logger; many repos provide it. Log and continue (we may still normalize imports).
            append_error("3.2", f"Check canonical module: {target_module}",
                         "Expected canonical module file not found", f"Expected {expected}")
            # Do NOT create a shim if target cannot be located
            continue
        make_wrapper(legacy_path, target_module)
        effective_wrappers[str(legacy_path)] = target_module

    # 3.3 Normalize imports/docs across repository
    changed_count = normalize_imports_across_repo(inventory)

    # 3.4 Smoke checks
    smoke_checks()

    # 6.2 Results summary
    write_results_summary(changed_count, effective_wrappers)

    # 6.4 Exit policy
    if ERRORS_NDJSON.exists() and ERRORS_NDJSON.stat().st_size > 0:
        # If any lines exist with content, exit non-zero
        return 1
    return 0

if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
