#!/usr/bin/env python3
"""
Codex Import Normalizer & Ruff Convergence Runner

- Splits comma-separated imports into one per line; alphabetizes names.
- Runs `ruff --fix` on target file, then re-runs `ruff` until exit code 0 (max loops).
- Ensures `.pre-commit-config.yaml` contains `ruff` and `ruff-format` hooks.
- Parses README for Ruff usage block and appends DO-NOT-ACTIVATE workflow statement.
- Writes change log, results, and research-question formatted errors.

USAGE:
  python tools/codex_import_normalizer.py --target codex_workflow.py
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple

# ---------------------------
# Helpers & logging
# ---------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
CODEX_DIR = REPO_ROOT / ".codex"
CHANGE_LOG = CODEX_DIR / "change_log.md"
ERRORS_LOG = CODEX_DIR / "errors.ndjson"
RESULTS_LOG = CODEX_DIR / "results.md"
INVENTORY_JSON = CODEX_DIR / "inventory.json"
PRECOMMIT = REPO_ROOT / ".pre-commit-config.yaml"
README = REPO_ROOT / "README.md"

RUFF_MAX_LOOPS = 5
DO_NOT_ACTIVATE = "DO NOT ACTIVATE ANY GitHub Actions files. ALL GitHub Action."

def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def ensure_dirs():
    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    if not CHANGE_LOG.exists():
        CHANGE_LOG.write_text("# Codex Change Log\n\n", encoding="utf-8")
    if not ERRORS_LOG.exists():
        ERRORS_LOG.write_text("", encoding="utf-8")
    if not RESULTS_LOG.exists():
        RESULTS_LOG.write_text("", encoding="utf-8")

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def append_results(block: str):
    with RESULTS_LOG.open("a", encoding="utf-8") as f:
        f.write(block.rstrip() + "\n\n")

def log_error(step: str, err: Exception | str, context: str = ""):
    msg = str(err)
    with ERRORS_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "ts": now_iso(), "step": step, "error": msg, "context": context
        }) + "\n")
    rq = (
        f"Question for ChatGPT-5 {now_iso()}:\n"
        f"While performing [{step}], encountered the following error:\n"
        f"{msg}\n"
        f"Context: {context}\n"
        f"What are the possible causes, and how can this be resolved while preserving intended functionality?"
    )
    append_results(rq)

def record_inventory(paths: List[Path]):
    items = []
    for p in paths:
        if not p.exists(): 
            continue
        try:
            text = p.read_text(encoding="utf-8")
            items.append({
                "path": str(p.relative_to(REPO_ROOT)),
                "sha256": sha256_text(text),
                "size": p.stat().st_size,
            })
        except Exception:
            pass
    INVENTORY_JSON.write_text(json.dumps(items, indent=2), encoding="utf-8")

def write_changelog(title: str, path: Path, before: str, after: str):
    # Keep compact diff-like block
    block = (
        f"### {now_iso()} — {path.relative_to(REPO_ROOT)}\n"
        f"- **Action:** edit\n"
        f"- **Rationale:** {title}\n"
        "```diff\n"
        f"{_compact_diff(before, after)}\n"
        "```\n\n"
    )
    with CHANGE_LOG.open("a", encoding="utf-8") as f:
        f.write(block)

def _compact_diff(before: str, after: str, context: int = 0) -> str:
    # Simple unified-like presentation; no external deps.
    import difflib
    return "".join(difflib.unified_diff(
        before.splitlines(True),
        after.splitlines(True),
        fromfile="before",
        tofile="after",
        n=context
    ))

# ---------------------------
# Import normalization
# ---------------------------
def split_and_alpha_imports(src_text: str) -> str:
    """
    Best-effort transform:
      - import a, b, c  -> three lines alphabetized
      - from X import a, b, c -> multiple 'from X import name' lines alphabetized
    Keeps imports within their scopes by operating line-wise, guarded by AST check.
    """
    try:
        ast.parse(src_text)  # sanity parse
    except SyntaxError as e:
        # If parse fails, bail out (do not mutate)
        raise RuntimeError(f"Syntax error pre-transform: {e}")

    lines = src_text.splitlines(keepends=True)
    out: List[str] = []
    for line in lines:
        stripped = line.lstrip()
        indent = line[: len(line) - len(stripped)]
        m1 = re.match(r"^(import)\s+(.+)$", stripped)
        m2 = re.match(r"^(from)\s+([A-Za-z0-9_\.]+)\s+import\s+(.+)$", stripped)
        if m1 and "," in m1.group(2):
            # import a, b, c as d
            parts = [p.strip() for p in m1.group(2).split(",")]
            # preserve aliases (`x as y`)
            names = sorted(parts, key=lambda s: s.split()[0])
            for n in names:
                out.append(f"{indent}import {n}\n")
        elif m2 and "," in m2.group(3):
            # from mod import a, b as c
            mod = m2.group(2)
            parts = [p.strip() for p in m2.group(3).split(",")]
            names = sorted(parts, key=lambda s: s.split()[0])
            for n in names:
                out.append(f"{indent}from {mod} import {n}\n")
        else:
            out.append(line)

    after = "".join(out)
    # Validate AST again
    try:
        ast.parse(after)
    except SyntaxError as e:
        # If unsafe, prefer original to avoid breaking
        raise RuntimeError(f"Syntax error post-transform: {e}")
    return after

# ---------------------------
# Ruff runners
# ---------------------------
def run_cmd(cmd: List[str]) -> Tuple[int, str]:
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = (p.stdout or "") + (p.stderr or "")
    return p.returncode, out

def ruff_fix_and_converge(target: Path) -> Tuple[int, List[str]]:
    logs = []
    code, out = run_cmd(["ruff", "check", "--fix", str(target)])
    logs.append(f"$ ruff check --fix {target}\n{out}")
    loops = 0
    while loops < RUFF_MAX_LOOPS:
        code, out = run_cmd(["ruff", "check", str(target)])
        logs.append(f"$ ruff check {target}\n{out}")
        if code == 0:
            break
        loops += 1
        # attempt another fix pass
        code2, out2 = run_cmd(["ruff", "check", "--fix", str(target)])
        logs.append(f"$ ruff check --fix {target}\n{out2}")
    return code, logs

# ---------------------------
# Pre-commit ruff hooks
# ---------------------------
_RUFF_BLOCK = """- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.5.0
  hooks:
    - id: ruff
      name: ruff
    - id: ruff-format
      name: ruff-format
"""

def ensure_ruff_hooks(yaml_text: str) -> str:
    # Idempotent insertion under 'repos:'; minimal YAML awareness
    if (" id: ruff\n" in yaml_text) and (" id: ruff-format\n" in yaml_text):
        return yaml_text  # already present
    if "repos:" not in yaml_text:
        # create minimal structure
        return "repos:\n" + _indent_block(_RUFF_BLOCK, 2) + ("\n" if not yaml_text.endswith("\n") else "") + yaml_text
    # Inject after 'repos:' line
    lines = yaml_text.splitlines(keepends=True)
    out = []
    injected = False
    for i, ln in enumerate(lines):
        out.append(ln)
        if not injected and ln.strip().startswith("repos:"):
            out.append(_indent_block(_RUFF_BLOCK, 2))
            injected = True
    if not injected:
        out.append("repos:\n")
        out.append(_indent_block(_RUFF_BLOCK, 2))
    return "".join(out)

def _indent_block(block: str, spaces: int) -> str:
    pad = " " * spaces
    return "".join(pad + ln if ln.strip() else ln for ln in block.splitlines(True))

# ---------------------------
# README edits
# ---------------------------
def update_readme(text: str) -> str:
    add_usage = "## Ruff Usage" not in text
    add_guard = DO_NOT_ACTIVATE not in text
    extra = []
    if add_usage:
        extra.append(
            "\n## Ruff Usage\n"
            "- Lint: `ruff .`\n"
            "- Auto-fix target: `ruff --fix codex_workflow.py`\n"
            "- Converge until clean: re-run `ruff` until exit code 0\n"
        )
    if add_guard:
        extra.append(f"\n> **{DO_NOT_ACTIVATE}**\n")
    return text + "".join(extra) if extra else text

# ---------------------------
# Main
# ---------------------------
def main():
    parser = argparse.ArgumentParser(description="Codex-ready import normalizer & ruff fixer")
    parser.add_argument("--target", required=True, help="Path to Python file to normalize imports (e.g., codex_workflow.py)")
    args = parser.parse_args()

    ensure_dirs()

    target = REPO_ROOT / args.target
    touched = [target, PRECOMMIT, README]
    record_inventory([p for p in touched if p.exists()])

    if not target.exists():
        log_error("2.1: Locate target file", "Target file not found", str(target))
        print("Target file not found:", target, file=sys.stderr)
        sys.exit(2)

    # Backup originals
    for p in [target, PRECOMMIT, README]:
        if p and p.exists():
            shutil.copy2(p, p.with_suffix(p.suffix + ".bak"))

    # Phase 3.1: normalize imports
    try:
        before = target.read_text(encoding="utf-8")
        after = split_and_alpha_imports(before)
        if after != before:
            target.write_text(after, encoding="utf-8")
            write_changelog("Split & alphabetize imports (one per line)", target, before, after)
        append_results(f"Normalized imports for {target.relative_to(REPO_ROOT)}")
    except Exception as e:
        log_error("3.1: Normalize imports", e, str(target))

    # Phase 3.2 & 3.3: ruff fix + converge
    try:
        code, logs = ruff_fix_and_converge(target)
        append_results("\n".join(logs))
        if code != 0:
            log_error("3.3: Re-run ruff until exit 0", f"Ruff did not converge to exit 0 (final code {code})", str(target))
    except Exception as e:
        log_error("3.2: Run ruff --fix", e, str(target))

    # Phase 3.4: ensure ruff hooks in pre-commit
    try:
        if PRECOMMIT.exists():
            pc_before = PRECOMMIT.read_text(encoding="utf-8")
        else:
            pc_before = "repos:\n"
        pc_after = ensure_ruff_hooks(pc_before)
        if pc_after != pc_before:
            PRECOMMIT.write_text(pc_after, encoding="utf-8")
            write_changelog("Ensure Ruff hooks (`ruff`, `ruff-format`) in pre-commit", PRECOMMIT, pc_before, pc_after)
        append_results("Verified/inserted Ruff hooks in .pre-commit-config.yaml")
    except Exception as e:
        log_error("3.4: Ensure Ruff pre-commit hooks", e, str(PRECOMMIT))

    # Phase 3.5: README edits (optional best-effort)
    try:
        if README.exists():
            rb = README.read_text(encoding="utf-8")
            ra = update_readme(rb)
            if ra != rb:
                README.write_text(ra, encoding="utf-8")
                write_changelog("README add Ruff usage & DO-NOT-ACTIVATE note", README, rb, ra)
            append_results("README checked/updated for Ruff usage & DO-NOT-ACTIVATE statement.")
    except Exception as e:
        log_error("3.5: README update", e, str(README))

    # Phase 6: finalization summary
    append_results(
        "Finalization Summary:\n"
        f"- Target: {target.relative_to(REPO_ROOT)}\n"
        f"- Ruff loops max: {RUFF_MAX_LOOPS}\n"
        "- Logs: see .codex/results.md and .codex/errors.ndjson\n"
        f"- NOTE: {DO_NOT_ACTIVATE}\n"
    )

if __name__ == "__main__":
    main()
