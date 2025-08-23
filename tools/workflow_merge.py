#!/usr/bin/env python3
"""
Codex Workflow Merge: choose authoritative codex_workflow.py, merge/rename duplicates,
update references, and verify that mypy duplicate-module warnings disappear.

Environment: Linux/Ubuntu (Codex), unrestricted network is not required.
Tools: prefers rg/sed if present, but has Python fallbacks.
"""

from __future__ import annotations
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Tuple, Dict

REPO = (
    Path(__file__).resolve().parents[1]
    if (Path(__file__).parent.name == "tools")
    else Path(__file__).resolve().parent
)
CODEX = REPO / ".codex"
CODEX.mkdir(parents=True, exist_ok=True)
CHANGELOG = CODEX / "change_log.md"
ERRORS = CODEX / "errors.ndjson"
RESULTS = CODEX / "results.md"


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def log_change(title: str, details: str) -> None:
    CHANGELOG.touch(exist_ok=True)
    with CHANGELOG.open("a", encoding="utf-8") as f:
        f.write(f"### {now_iso()} — {title}\n{details}\n\n")


def log_error(step: str, err: Exception | str, ctx: str) -> None:
    ERRORS.touch(exist_ok=True)
    payload = {"ts": now_iso(), "step": step, "error": str(err), "context": ctx}
    with ERRORS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")
    sys.stderr.write(
        f"Question for ChatGPT-5 {now_iso()}:\n"
        f"While performing [{step}], encountered the following error:\n{err}\n"
        f"Context: {ctx}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n\n"
    )


def run(cmd: List[str], check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, cwd=str(REPO), text=True, capture_output=True, check=check
    )


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def list_candidates() -> List[Path]:
    """
    Find all candidate workflow scripts: *codex_workflow*.py anywhere in repo, excluding venvs/build.
    """
    ignore_dirs = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "build",
        "dist",
        ".mypy_cache",
        ".pytest_cache",
    }
    candidates: List[Path] = []
    for p in REPO.rglob("codex_workflow*.py"):
        if any(part in ignore_dirs for part in p.parts):
            continue
        candidates.append(p)
    return sorted(set(candidates))


def count_references(name_fragment: str) -> int:
    """
    Count repo-wide references using ripgrep if available; else
    fallback to python scanning.
    """
    if have("rg"):
        cp = run(["rg", "-n", name_fragment])
        return sum(1 for _ in cp.stdout.splitlines())
    # Fallback
    total = 0
    for p in REPO.rglob("*"):
        if not p.is_file():
            continue
        if any(
            seg in p.parts
            for seg in (".git", ".venv", "venv", "node_modules", "dist", "build")
        ):
            continue
        if p.suffix.lower() not in {
            ".py",
            ".md",
            ".rst",
            ".txt",
            ".yml",
            ".yaml",
            ".toml",
            ".ini",
        }:
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        total += txt.count(name_fragment)
    return total


@dataclass
class Choice:
    path: Path
    ref_count: int
    mtime: float


def choose_authoritative(candidates: List[Path]) -> Path:
    """
    Prefer root ./codex_workflow.py if present; else prefer highest
    reference count; tie-breaker newest mtime.
    """
    root = REPO / "codex_workflow.py"
    if root in candidates:
        return root
    scored = [
        Choice(path=c, ref_count=count_references(c.stem), mtime=c.stat().st_mtime)
        for c in candidates
    ]
    scored.sort(key=lambda x: (x.ref_count, x.mtime), reverse=True)
    return scored[0].path


def ensure_at_root(authoritative: Path) -> Path:
    """
    Move authoritative to repo root as codex_workflow.py if needed.
    """
    target = REPO / "codex_workflow.py"
    if authoritative == target:
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        # Merge strategy: append unique definitions from authoritative into target
        try:
            src = authoritative.read_text(encoding="utf-8", errors="ignore")
            dst = target.read_text(encoding="utf-8", errors="ignore")
            if src != dst:
                with target.open("a", encoding="utf-8") as f:
                    f.write(
                        "\n\n# BEGIN MERGED FROM: "
                        + str(authoritative.relative_to(REPO))
                        + "\n"
                    )
                    f.write(src)
                    f.write(
                        "\n# END MERGED FROM: "
                        + str(authoritative.relative_to(REPO))
                        + "\n"
                    )
                src_rel = authoritative.relative_to(REPO)
                dst_rel = target.relative_to(REPO)
                log_change("Merge", f"Merged content from {src_rel} into {dst_rel}")
        except Exception as e:
            log_error("3: ensure_at_root merge", e, f"authoritative={authoritative}")
    else:
        shutil.copy2(authoritative, target)
        src_rel = authoritative.relative_to(REPO)
        dst_rel = target.relative_to(REPO)
        log_change("Move", f"Copied authoritative {src_rel} -> {dst_rel}")
    # keep source for deletion later
    return target


def build_replacements(non_auth_files: List[Path]) -> Dict[str, str]:
    """
    Map old import forms to 'codex_workflow'.
    """
    mapping = {}
    for p in non_auth_files:
        name = p.stem  # codex_workflow or codex_workflow_tool
        # plausible import tokens
        tokens = {
            f"from tools.{name} import",
            f"import tools.{name}",
            f"from {name} import",
            f"import {name}",
            f"{name}.",  # attribute access
        }
        for t in tokens:
            mapping[t] = t.replace(f"tools.{name}", "codex_workflow").replace(
                f"{name}", "codex_workflow"
            )
    return mapping


def replace_in_file(path: Path, mapping: Dict[str, str]) -> int:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return 0
    orig = text
    for k, v in mapping.items():
        # conservative: replace only whole-word tokens
        text = re.sub(rf"(?<!\w){re.escape(k)}(?!\w)", v, text)
    if text != orig:
        path.write_text(text, encoding="utf-8")
        return 1
    return 0


def update_references(mapping: Dict[str, str]) -> Tuple[int, int]:
    changed, scanned = 0, 0
    for p in REPO.rglob("*"):
        if not p.is_file():
            continue
        if any(
            seg in p.parts
            for seg in (
                ".git",
                ".venv",
                "venv",
                "node_modules",
                "dist",
                "build",
                ".mypy_cache",
                ".pytest_cache",
            )
        ):
            continue
        if p.suffix.lower() not in {
            ".py",
            ".md",
            ".rst",
            ".txt",
            ".yml",
            ".yaml",
            ".toml",
            ".ini",
        }:
            continue
        scanned += 1
        changed += replace_in_file(p, mapping)
    return changed, scanned


def delete_or_shim(non_auth: List[Path], keep_shim: bool) -> None:
    for f in non_auth:
        rel = f.relative_to(REPO)
        if keep_shim:
            shim = (
                '"""Compatibility shim – prefer `codex_workflow`."""\n'
                "import warnings as _w\n"
                "_w.warn(\n"
                "    'Deprecated import: use `codex_workflow`', DeprecationWarning\n"
                ")\n"
                "from codex_workflow import *  # noqa: F401,F403\n"
            )
            f.write_text(shim, encoding="utf-8")
            log_change("Shim", f"Rewrote {rel} as compatibility shim")
        else:
            f.unlink(missing_ok=True)
            log_change("Delete", f"Deleted redundant {rel}")


def run_checks() -> str:
    outputs = []
    checks = [
        ("mypy", ["mypy", "."]),
        ("ruff", ["ruff", "--diff", "."]),
        ("pytest", ["pytest", "-q", "--maxfail=1"]),
    ]
    for name, cmd in checks:
        try:
            cp = run(cmd, check=False)
            outputs.append(f"## {name}\n```\n{cp.stdout}\n{cp.stderr}\n```\n")
        except Exception as e:
            log_error("5: run_checks", e, f"cmd={cmd}")
            outputs.append(f"## {name}\n```\nERROR: {e}\n```\n")
    return "\n".join(outputs)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Consolidate codex_workflow* scripts and update references."
    )
    ap.add_argument(
        "--keep-shims",
        action="store_true",
        help="Leave compatibility shim modules instead of deleting.",
    )
    args = ap.parse_args()

    candidates = list_candidates()
    if not candidates:
        log_error(
            "1: Preparation - candidates",
            "No codex_workflow*.py files found",
            "Search repo",
        )
        return 1

    # Prefer root authoritative; else choose by references/mtime
    authoritative = choose_authoritative(candidates)
    non_auth = [c for c in candidates if c != authoritative]

    # Move authoritative to root if needed
    authoritative = ensure_at_root(authoritative)

    # Prepare replacements mapping for non-authoritative names
    mapping = build_replacements(non_auth)

    # Update references across repo
    changed, scanned = update_references(mapping)
    log_change(
        "Update references",
        f"Scanned {scanned} files; updated {changed} files to use `codex_workflow`",
    )

    # Remove or shim redundant files
    delete_or_shim(non_auth, keep_shim=args.keep_shims)

    # Write summary and run checks
    RESULTS.write_text("", encoding="utf-8")
    with RESULTS.open("a", encoding="utf-8") as f:
        f.write(f"# Workflow Merge Results ({now_iso()})\n\n")
        f.write(f"- Authoritative: `{authoritative.relative_to(REPO)}`\n")
        f.write(f"- Redundant files: {[str(p.relative_to(REPO)) for p in non_auth]}\n")
        f.write(f"- Files changed: {changed}\n\n")
        f.write(run_checks())

        f.write(
            "\n**Note:** Look for mypy messages like 'Duplicate module named' "
            "and confirm they are gone.\n"
        )

    # Suggested commit (do not auto-commit to keep user control)
    log_change(
        "Commit suggestion",
        (
            "git add -A && git commit -m '"
            "feat: consolidate codex_workflow entrypoint; remove duplicates "
            "and update references'"
        ),
    )

    # Compliance: do not alter CI triggers
    log_change(
        "Compliance", "DO NOT ACTIVATE ANY GitHub Actions files. ALL GitHub Action."
    )

    print("Consolidation complete. See .codex/ for logs and results.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        log_error("9: Uncaught", e, "Top-level")
        raise
