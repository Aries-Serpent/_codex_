#!/usr/bin/env python3
"""
tools/codex_precommit_bootstrap.py

End-to-end bootstrap for pre-commit (ruff + black) on `_codex_` / branch `0B_base_`.

- Creates or updates:
  - .pre-commit-config.yaml
  - README.md (adds Pre-commit section if missing)
  - pyproject.toml (optional sections for Ruff/Black)
  - tests/test_precommit_config_exists.py (smoke)
  - .codex/change_log.md, .codex/errors.ndjson, .codex/results.md

- Logs summarized diffs to .codex/change_log.md
- Captures failures as "ChatGPT-5 research questions" in .codex/errors.ndjson
- DOES NOT and MUST NOT activate any GitHub Actions files.

Usage:
  python tools/codex_precommit_bootstrap.py [--force] [--dry-run]
"""

from __future__ import annotations

import difflib
import json
import re
import subprocess
import sys
import textwrap
from datetime import datetime
from pathlib import Path

REPO_BRANCH_EXPECTED = "0B_base_"
DO_NOT_ACTIVATE_GITHUB_ACTIONS = True
SAFE_WRITE_MODE = True

ROOT = Path.cwd()
CODEX_DIR = ROOT / ".codex"
CHANGE_LOG = CODEX_DIR / "change_log.md"
ERRORS_NDJSON = CODEX_DIR / "errors.ndjson"
RESULTS_MD = CODEX_DIR / "results.md"

PRECOMMIT_YAML = ROOT / ".pre-commit-config.yaml"
README = ROOT / "README.md"
PYPROJECT = ROOT / "pyproject.toml"
TEST_SMOKE = ROOT / "tests" / "test_precommit_config_exists.py"

R_RUFF_PRECOMMIT_REV = "v0.12.9"  # per official docs
R_BLACK_REV = "25.1.0"  # pin explicit version (avoid 'stable')
R_PCH_REV = "v6.0.0"  # pre-commit-hooks


def sh(cmd: list[str]) -> tuple[int, str, str]:
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return p.returncode, out.strip(), err.strip()


def log_change(path: Path, action: str, rationale: str, before: str, after: str):
    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    CHANGE_LOG.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    diff = ""
    if before is None:
        diff = f"*created* {path}"
    else:
        diff_lines = list(
            difflib.unified_diff(
                before.splitlines(),
                after.splitlines(),
                fromfile=f"{path} (before)",
                tofile=f"{path} (after)",
                lineterm="",
            )
        )
        diff = "\n".join(diff_lines[:200])  # avoid overlong logs
    with CHANGE_LOG.open("a", encoding="utf-8") as f:
        f.write(
            f"\n### {ts}\n- **File**: {path}\n- **Action**: {action}\n- "
            f"**Why**: {rationale}\n"
        )
        f.write("```diff\n" + (diff or "(no textual diff)") + "\n```\n")


def log_error(step_num_desc: str, error_message: str, context: str):
    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "step": step_num_desc,
        "error": error_message,
        "context": context,
    }
    with ERRORS_NDJSON.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    block = (
        "Question for ChatGPT-5:\n"
        f"While performing [{step_num_desc}], encountered the following error:\n"
        f"{error_message}\n"
        f"Context: {context}\n"
        "What are the possible causes, and how can this be resolved while preserving "
        "intended functionality?"
    )
    print(block, file=sys.stderr)


def safe_write(path: Path, content: str, rationale: str):
    before = path.read_text(encoding="utf-8") if path.exists() else None
    if SAFE_WRITE_MODE:
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(content, encoding="utf-8")
        tmp.replace(path)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    after = path.read_text(encoding="utf-8")
    log_change(
        path, "write" if before is not None else "create", rationale, before, after
    )


def ensure_repo_clean(force: bool):
    rc, out, err = sh(["git", "status", "--porcelain"])
    if rc != 0:
        log_error(
            "1.1: verify clean working state",
            err or out,
            "git status --porcelain failed",
        )
        return
    if out.strip() and not force:
        log_error(
            "1.1: verify clean working state",
            "Uncommitted changes present",
            "Run with --force to proceed despite a dirty tree.",
        )
        sys.exit(1)


def get_branch() -> str:
    rc, out, _ = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    return out if rc == 0 else ""


def inventory() -> str:
    items = []
    for p in sorted(ROOT.iterdir()):
        name = p.name + ("/" if p.is_dir() else "")
        items.append(name)
    return "\n".join(items)


def render_precommit_yaml(existing: str | None) -> str:
    base = (
        textwrap.dedent(f"""
    repos:
      - repo: https://github.com/astral-sh/ruff-pre-commit
        rev: {R_RUFF_PRECOMMIT_REV}
        hooks:
          - id: ruff-check
            args: [--fix]
          - id: ruff-format

      - repo: https://github.com/psf/black
        rev: {R_BLACK_REV}
        hooks:
          - id: black
            stages: [manual]   # keep manual to avoid double-formatting with ruff-format

      - repo: https://github.com/pre-commit/pre-commit-hooks
        rev: {R_PCH_REV}
        hooks:
          - id: trailing-whitespace
          - id: end-of-file-fixer
          - id: check-yaml
          - id: mixed-line-ending
    """).strip()
        + "\n"
    )
    if not existing:
        return base
    needed = []
    if "astral-sh/ruff-pre-commit" not in existing:
        needed.append(
            re.findall(
                r"(?s)- repo: https://github.com/astral-sh/ruff-pre-commit.*?"
                r"(?=\n\n- repo:|$)",
                base,
            )[0]
        )
    if "https://github.com/psf/black" not in existing:
        needed.append(
            re.findall(
                r"(?s)- repo: https://github.com/psf/black.*?"
                r"(?=\n\n- repo:|$)",
                base,
            )[0]
        )
    if "https://github.com/pre-commit/pre-commit-hooks" not in existing:
        needed.append(
            re.findall(
                r"(?s)- repo: https://github.com/pre-commit/pre-commit-hooks.*",
                base,
            )[0]
        )
    if not needed:
        return existing if existing.endswith("\n") else existing + "\n"
    return existing.rstrip() + "\n\n" + "\n\n".join(needed) + "\n"


def upsert_readme_section():
    txt = README.read_text(encoding="utf-8") if README.exists() else "# _codex_\n"
    section_title = "## Pre-commit (Ruff + Black)"
    if section_title in txt:
        return txt
    guide = textwrap.dedent(f"""
    {section_title}

    This repository uses [pre-commit](https://pre-commit.com) to run
    code-quality hooks locally.
    **DO NOT ACTIVATE ANY GitHub Actions files.**

    **Install once**
    ```bash
    pipx install pre-commit || pip install --user pre-commit
    pre-commit install
    pre-commit autoupdate
    ```

    **Run on all files**
    ```bash
    pre-commit run --all-files
    ```

    **Run on specific files**
    ```bash
    pre-commit run --files path/to/file1.py path/to/file2.py
    ```

    **Optional — run Black manually (kept as manual stage)**
    ```bash
    pre-commit run --hook-stage manual black --all-files
    ```
    """).strip()
    return txt.rstrip() + "\n\n" + guide + "\n"


def upsert_pyproject():
    base = ""
    if PYPROJECT.exists():
        base = PYPROJECT.read_text(encoding="utf-8")
    parts = []
    has_ruff = re.search(r"(?m)^\[tool\.ruff\]", base) is not None
    has_black = re.search(r"(?m)^\[tool\.black\]", base) is not None

    if not has_ruff:
        parts.append(
            textwrap.dedent("""
        [tool.ruff]
        line-length = 88
        target-version = "py312"

        [tool.ruff.lint]
        select = ["E", "F", "I"]
        """).strip()
        )
    if not has_black:
        parts.append(
            textwrap.dedent("""
        [tool.black]
        line-length = 88
        target-version = ["py312"]
        """).strip()
        )

    if not parts:
        return base
    if base.strip():
        return base.rstrip() + "\n\n" + "\n\n".join(parts) + "\n"
    return "\n\n".join(parts) + "\n"


def ensure_smoke_test():
    content = (
        textwrap.dedent(
            """
        import pathlib

        def test_precommit_config_exists():
            root = pathlib.Path(__file__).resolve().parents[1]
            assert (root / ".pre-commit-config.yaml").exists(), (
                ".pre-commit-config.yaml should exist at repo root"
            )
        """
        ).strip()
        + "\n"
    )
    return content


def main():
    force = "--force" in sys.argv
    dry = "--dry-run" in sys.argv

    try:
        ensure_repo_clean(force=force)
    except Exception as e:
        log_error(
            "1.1: verify clean working state",
            repr(e),
            "exception during cleanliness check",
        )

    cur_branch = get_branch()
    if cur_branch and cur_branch != REPO_BRANCH_EXPECTED:
        log_error(
            "1.1: branch check",
            f"Current branch is '{cur_branch}', expected '{REPO_BRANCH_EXPECTED}'",
            "Proceeding anyway; this is informational.",
        )

    inv = inventory()
    print("Repository inventory (top-level):\n" + inv)

    try:
        existing = (
            PRECOMMIT_YAML.read_text(encoding="utf-8")
            if PRECOMMIT_YAML.exists()
            else None
        )
        rendered = render_precommit_yaml(existing)
        if not dry:
            safe_write(
                PRECOMMIT_YAML,
                rendered,
                "Add/merge pre-commit hooks: ruff-check, ruff-format, "
                "black(manual), hygiene hooks",
            )
    except Exception as e:
        log_error("3.2: write .pre-commit-config.yaml", repr(e), "render/merge failure")

    try:
        new_readme = upsert_readme_section()
        if not dry:
            safe_write(README, new_readme, "Document pre-commit usage & warnings")
    except Exception as e:
        log_error("3.3: update README.md", repr(e), "upsert Pre-commit section")

    try:
        updated = upsert_pyproject()
        if updated:
            if not dry:
                safe_write(
                    PYPROJECT,
                    updated,
                    "Add/update Ruff/Black sections in pyproject.toml",
                )
    except Exception as e:
        log_error("3.3: update pyproject.toml", repr(e), "upsert Ruff/Black sections")

    try:
        if not dry:
            TEST_SMOKE.parent.mkdir(parents=True, exist_ok=True)
            safe_write(
                TEST_SMOKE,
                ensure_smoke_test(),
                "Add smoke test for .pre-commit-config.yaml presence",
            )
    except Exception as e:
        log_error(
            "3.4: create smoke test", repr(e), "tests/test_precommit_config_exists.py"
        )

    try:
        results = (
            textwrap.dedent(
                f"""
                # Results Summary

                - Implemented:
                  - .pre-commit-config.yaml (ruff-check, ruff-format,
                    black on manual stage, hygiene hooks)
                  - README.md: Pre-commit section appended (install, run, manual black)
                  - pyproject.toml: [tool.ruff], [tool.black] sections (if missing)
                  - tests/test_precommit_config_exists.py (smoke test)

                - Constraints:
                  - DO NOT ACTIVATE ANY GitHub Actions files.

                - Inventory (top-level):
                ```
                {inv}
                ```

                - Next Steps:
                  - Install: `pipx install pre-commit` or
                    `pip install --user pre-commit`
                  - Run: `pre-commit install`
                  - Then: `pre-commit run --all-files`
                  - For manual Black:
                    `pre-commit run --hook-stage manual black --all-files`
                """
            ).strip()
            + "\n"
        )
        if not dry:
            safe_write(RESULTS_MD, results, "Document results & next steps")
    except Exception as e:
        log_error("6.2: write .codex/results.md", repr(e), "final summary")

    unresolved = ERRORS_NDJSON.exists() and ERRORS_NDJSON.stat().st_size > 0
    if unresolved:
        print(
            "Unresolved errors were captured in .codex/errors.ndjson", file=sys.stderr
        )
        sys.exit(1)
    print("Success. Pre-commit configuration bootstrapped.")
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_error("0.0: unhandled exception", repr(e), "top-level failure")
        sys.exit(1)
