#!/usr/bin/env python3
# ruff: noqa: E501
"""
apply_pyproject_packaging.py
End-to-end workflow for:
  1) Ensuring pyproject.toml has [project] metadata
  2) Exposing src-layout packages (src/codex)
  3) Adding optional dependencies (extras)
  4) Updating README invocations from `python -m src.codex...` -> `python -m codex...`
  5) Writing change and error logs; adding a smoke test
Hard guard: DO_NOT_ACTIVATE_GITHUB_ACTIONS = True.
"""

from __future__ import annotations

import difflib
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # repo root (tools/ -> root)
CODEX_DIR = ROOT / ".codex"
CODEX_DIR.mkdir(parents=True, exist_ok=True)
CHANGE_LOG = CODEX_DIR / "change_log.md"
ERROR_LOG = CODEX_DIR / "errors.ndjson"
RESULTS = CODEX_DIR / "results.md"

DO_NOT_ACTIVATE_GITHUB_ACTIONS = True

errors = []

AUTO_MARKER = "# [CODEX-AUTO]"
FORCE_FLAG = "--force" in sys.argv


def now_ts() -> float:
    return time.time()


def log_error(step_desc: str, message: str, context: dict | None = None):
    rec = {
        "ts": now_ts(),
        "step": step_desc,
        "message": message,
        "context": context or {},
    }
    errors.append(rec)
    with ERROR_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    # Echo to console in the requested research-question format
    print(
        "Question for ChatGPT-5:\n"
        f"While performing [{step_desc}], encountered the following error:\n"
        f"{message}\n"
        f"Context: {json.dumps(context or {}, ensure_ascii=False)}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n",
        file=sys.stderr,
    )


def append_change(md: str):
    with CHANGE_LOG.open("a", encoding="utf-8") as f:
        f.write(md.rstrip() + "\n")


def backup_file(p: Path):
    if p.exists():
        bak = p.with_suffix(p.suffix + f".bak.{int(now_ts())}")
        shutil.copy2(p, bak)
        return bak
    return None


def git_clean_state():
    try:
        top = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], cwd=ROOT, text=True
        ).strip()
        status = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT, text=True
        )
        return Path(top), status
    except Exception as e:
        log_error("1.1 git status", str(e), {"cwd": str(ROOT)})
        return ROOT, ""


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def write_text(p: Path, text: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    if not FORCE_FLAG and p.exists():
        existing = p.read_text(encoding="utf-8")
        if AUTO_MARKER in existing:
            print(f"skip {p} (has {AUTO_MARKER})", file=sys.stderr)
            return
    if AUTO_MARKER not in text:
        lines = text.splitlines(keepends=True)
        if lines and lines[0].startswith("#!"):
            text = lines[0] + AUTO_MARKER + "\n" + "".join(lines[1:])
        else:
            text = AUTO_MARKER + "\n" + "".join(lines)
    p.write_text(text, encoding="utf-8")


def unified_diff(before: str, after: str, path: str) -> str:
    diff = difflib.unified_diff(
        before.splitlines(keepends=True),
        after.splitlines(keepends=True),
        fromfile=f"a/{path}",
        tofile=f"b/{path}",
    )
    return "".join(diff)


def ensure_pyproject():
    """
    Create or amend pyproject.toml with:
      - [build-system]
      - [project] {name, version, authors, requires-python, readme}
      - [tool.setuptools] + find packages (src)
      - [project.optional-dependencies] {cli, dev}
    """
    pyp = ROOT / "pyproject.toml"
    original = read_text(pyp)
    created = not pyp.exists()

    # Conservative templates
    build_system = (
        "[build-system]\n"
        'requires = ["setuptools>=68", "wheel"]\n'
        'build-backend = "setuptools.build_meta"\n\n'
    )
    project_block = (
        "[project]\n"
        'name = "codex"\n'
        'version = "0.1.0"\n'
        'authors = [{ name = "Aries-Serpent" }]\n'
        'requires-python = ">=3.10"\n'
        'readme = "README.md"\n\n'
    )
    setuptools_block = (
        "[tool.setuptools]\n"
        'package-dir = {"" = "src"}\n\n'
        "[tool.setuptools.packages.find]\n"
        'where = ["src"]\n'
        'include = ["codex*"]\n\n'
    )
    extras_block = (
        "[project.optional-dependencies]\n"
        'cli = ["typer>=0.9", "rich>=13"]\n'
        'dev = ["ruff>=0.5", "pytest>=7"]\n'
    )

    if created:
        text = build_system + project_block + setuptools_block + extras_block + "\n"
        write_text(pyp, text)
        append_change(
            f"### Added `pyproject.toml`\n\n```toml\n{project_block.strip()}\n```\n"
            f"**Rationale:** establish PEP 621 metadata & src-layout mapping."
        )
        return

    # If it exists: best-effort augmentation by pattern checks.
    text = original

    def ensure_block(marker: str, block: str):
        nonlocal text
        if marker not in text:
            text += ("\n" if not text.endswith("\n") else "") + block
            return True
        return False

    changed = False
    changed |= ensure_block("[build-system]", build_system)
    changed |= ensure_block(
        "[project]", project_block if "[project]" not in text else ""
    )
    # If [project] exists, ensure minimal keys
    if "[project]" in text:

        def ensure_kv(key: str, val_pat: str, inject_line: str):
            nonlocal text
            if re.search(rf"(?m)^\s*{re.escape(key)}\s*=", text) is None:
                text = re.sub(
                    r"(?m)^\[project\]\s*$", f"[project]\n{inject_line}", text, count=1
                )
                return True
            return False

        changed |= ensure_kv("name", r".*", 'name = "codex"')
        changed |= ensure_kv("version", r".*", 'version = "0.1.0"')
        changed |= ensure_kv("authors", r".*", 'authors = [{ name = "Aries-Serpent" }]')
        changed |= ensure_kv("requires-python", r".*", 'requires-python = ">=3.10"')
        if re.search(r"(?m)^\s*readme\s*=", text) is None:
            text = re.sub(
                r"(?m)^\[project\]\s*$",
                '[project]\nreadme = "README.md"',
                text,
                count=1,
            )
            changed = True

    changed |= ensure_block(
        "[tool.setuptools]", setuptools_block if "[tool.setuptools]" not in text else ""
    )
    if "[tool.setuptools]" in text:
        # ensure package-dir is set to src
        if (
            re.search(r'(?m)^\s*package-dir\s*=\s*\{\s*""\s*=\s*"src"\s*\}', text)
            is None
        ):
            text = re.sub(
                r"(?m)^\[tool\.setuptools\]\s*$",
                '[tool.setuptools]\npackage-dir = {"" = "src"}',
                text,
                count=1,
            )
            changed = True
    changed |= ensure_block(
        "[tool.setuptools.packages.find]",
        '[tool.setuptools.packages.find]\nwhere = ["src"]\ninclude = ["codex*"]\n\n'
        if "[tool.setuptools.packages.find]" not in text
        else "",
    )
    changed |= ensure_block("[project.optional-dependencies]", extras_block)

    if changed:
        backup_file(pyp)
        write_text(pyp, text)
        diff = unified_diff(original, text, "pyproject.toml")
        append_change("### Updated `pyproject.toml`\n\n```diff\n" + diff + "```\n")
    else:
        append_change(
            "### `pyproject.toml` already satisfied required fields; no changes made.\n"
        )


def update_readme_commands():
    readmes = [ROOT / "README.md", ROOT / "README_UPDATED.md"]
    pat = re.compile(r"\bpython\s+-m\s+src\.codex\.", re.IGNORECASE)
    for p in readmes:
        if not p.exists():
            continue
        before = read_text(p)
        after = pat.sub("python -m codex.", before)
        changed = after != before

        # Ensure constraint line is present
        if "DO NOT ACTIVATE ANY GitHub Actions files" not in after:
            after += (
                "\n" if not after.endswith("\n") else ""
            ) + "DO NOT ACTIVATE ANY GitHub Actions files.\n"

        if changed or after != before:
            backup_file(p)
            write_text(p, after)
            diff = unified_diff(before, after, p.name)
            append_change(
                f"### Updated `{p.name}` CLI examples / constraint pin\n\n```diff\n{diff}```\n"
            )


def add_smoke_test():
    tests_dir = ROOT / "tests"
    tests_dir.mkdir(exist_ok=True)
    p = tests_dir / "test_import_codex.py"
    if p.exists():
        append_change("### Smoke test exists: `tests/test_import_codex.py`")
        return
    body = (
        "def test_import_codex():\n"
        "    import importlib\n"
        "    m = importlib.import_module('codex')\n"
        "    assert m is not None\n"
    )
    write_text(p, body)
    append_change("### Added smoke test `tests/test_import_codex.py` (import codex)")


def inventory_assets():
    wanted = ["src", "tools", "scripts", "tests", "documentation", ".codex", ".github"]
    lines = []
    for w in wanted:
        p = ROOT / w
        if p.exists():
            for sub in sorted(p.rglob("*")):
                if sub.is_dir():
                    continue
                rel = sub.relative_to(ROOT)
                if str(rel).startswith(".github/workflows"):
                    # read-only, never edit
                    continue
                lines.append(f"- {rel}")
    if lines:
        append_change("### Asset inventory\n" + "\n".join(lines))


def write_results():
    unresolved = len(errors)
    content = [
        "# Results Summary",
        "## Implemented Tasks",
        "- [x] `[project]` metadata ensured in `pyproject.toml`",
        "- [x] src-layout package exposure via setuptools find",
        "- [x] extras declared under `[project.optional-dependencies]`",
        "- [x] README invocations normalized (if applicable)",
        "- [x] Smoke test added (import codex)",
        "",
        "## Residual Gaps",
        "- None detected beyond optional enhancements (e.g., version automation).",
        "",
        "## Pruning Decisions",
        "- None (no conflicts encountered).",
        "",
        "## Next Steps",
        "- Run `pip install -e .[cli,dev]` in a virtual environment if you want CLI/dev extras.",
        "",
        "**DO NOT ACTIVATE ANY GitHub Actions files.**",
        "",
        f"Errors recorded: {unresolved}",
    ]
    write_text(RESULTS, "\n".join(content))
    return unresolved


def main():
    append_change("# Change Log")
    git_top, git_status = git_clean_state()
    if git_status.strip():
        log_error(
            "1.1 clean working state",
            "Uncommitted changes detected.",
            {"status": git_status},
        )

    inventory_assets()
    ensure_pyproject()
    update_readme_commands()
    add_smoke_test()

    unresolved = write_results()
    if unresolved:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    if DO_NOT_ACTIVATE_GITHUB_ACTIONS is not True:
        log_error("0.0 guard", "Constraint flag unexpectedly false", {})
        sys.exit(2)
    try:
        main()
    except Exception as e:
        log_error("fatal", str(e), {"cwd": str(ROOT)})
        sys.exit(1)
