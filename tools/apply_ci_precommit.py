#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codex Orchestrator: pre-commit hooks, manual CI workflow, coverage gate, README badges.

Policy:
- DO NOT ACTIVATE ANY GitHub Actions Online files. All validations must run within the Codex environment.
- Workflows use only `workflow_dispatch`.

Creates/updates:
- .pre-commit-config.yaml
- .github/workflows/ci.yml (manual only) and .github/workflows/release.yml.disabled
- pyproject.toml or pytest.ini (coverage gate)
- README.md (badges with TODO repo slug)

Validations (local, best-effort): pre-commit, black/isort/flake8/mypy, pytest --cov with threshold.
"""

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
    rq = textwrap.dedent(
        f"""\
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
    sys.stderr.write(rq + "\n")


def upsert_yaml(path: Path, sentinel: str, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and sentinel in path.read_text(encoding="utf-8"):
        return
    if path.exists():
        new = path.read_text(encoding="utf-8")
        if not new.endswith("\n"):
            new += "\n"
        new += "\n" + content
        path.write_text(new, encoding="utf-8")
        log_change("edit", path, f"append guarded by {sentinel}", content)
    else:
        path.write_text(content, encoding="utf-8")
        log_change("create", path, f"create guarded by {sentinel}", content)


def ensure_precommit():
    path = REPO / ".pre-commit-config.yaml"
    sentinel = "# BEGIN: CODEX_PRECOMMIT"
    block = f"""{sentinel}
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 24.8.0
    hooks:
      - id: black
        args: ["--check"]

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--check-only", "--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 7.1.1
    hooks:
      - id: flake8
        args: ["--max-line-length=200", "--extend-ignore=E203"]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.1
    hooks:
      - id: mypy
        args: ["--ignore-missing-imports"]
# END: CODEX_PRECOMMIT
"""
    upsert_yaml(path, sentinel, block)


def ensure_ci_manual(cov_threshold: int):
    path = REPO / ".github" / "workflows" / "ci.yml"
    sentinel = "# BEGIN: CODEX_CI_MANUAL"
    block = f"""{sentinel}
name: CI (manual)
on:
  workflow_dispatch:
jobs:
  lint:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [ "3.9", "3.10", "3.11" ]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{{{ matrix.python-version }}}}
          cache: "pip"
      - run: pip install black isort flake8
      - run: black --version && isort --version && flake8 --version
      - run: black --check .
      - run: isort --check-only --profile black .
      - run: flake8 .

  type:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [ "3.9", "3.10", "3.11" ]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{{{ matrix.python-version }}}}
          cache: "pip"
      - run: pip install mypy
      - run: mypy --ignore-missing-imports .

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [ "3.9", "3.10", "3.11" ]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{{{ matrix.python-version }}}}
          cache: "pip"
      - run: pip install -e .[dev] pytest pytest-cov
      - run: pytest -q --maxfail=1 --cov=src --cov-report=xml --cov-fail-under={cov_threshold}
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: coverage-xml-${{{{ matrix.python-version }}}}
          path: coverage.xml
# END: CODEX_CI_MANUAL
"""
    upsert_yaml(path, sentinel, block)


def ensure_release_disabled():
    path = REPO / ".github" / "workflows" / "release.yml.disabled"
    sentinel = "# BEGIN: CODEX_RELEASE_DISABLED"
    block = f"""{sentinel}
# Release workflow is intentionally DISABLED. To enable, rename to release.yml and review triggers.
# on:
#   workflow_dispatch:
# jobs:
#   build-and-tag:
#     runs-on: ubuntu-latest
#     steps:
#       - uses: actions/checkout@v4
#       - uses: actions/setup-python@v5
#         with: {{ python-version: "3.11" }}
#       - run: echo "Build/tag steps here..."
# END: CODEX_RELEASE_DISABLED
"""
    upsert_yaml(path, sentinel, block)


def ensure_coverage_gate(threshold: int):
    pyproj = REPO / "pyproject.toml"
    sentinel = "# BEGIN: CODEX_PYTEST_COVERAGE"
    block = f"""{sentinel}
[tool.pytest.ini_options]
addopts = "--cov=src --cov-report=term-missing --cov-fail-under={threshold}"
# END: CODEX_PYTEST_COVERAGE
"""
    if pyproj.exists():
        text = pyproj.read_text(encoding="utf-8")
        if sentinel not in text:
            if not text.endswith("\n"):
                text += "\n"
            text += "\n" + block + "\n"
            pyproj.write_text(text, encoding="utf-8")
            log_change("edit", pyproj, "append pytest coverage gate", block)
    else:
        pytest_ini = REPO / "pytest.ini"
        if pytest_ini.exists() and sentinel in pytest_ini.read_text(encoding="utf-8"):
            return
        content = f"""{sentinel}
[pytest]
addopts = --cov=src --cov-report=term-missing --cov-fail-under={threshold}
# END: CODEX_PYTEST_COVERAGE
"""
        upsert_yaml(pytest_ini, sentinel, content)


def ensure_readme_badges():
    readme = REPO / "README.md"
    sentinel = "<!-- BEGIN: CODEX_BADGES -->"
    block = f"""{sentinel}
<!-- Replace OWNER/REPO with your repository slug -->
[![CI (manual)](https://img.shields.io/badge/CI-manual-blue)](#)
[![Coverage ≥ threshold](https://img.shields.io/badge/coverage-local--gate-successful-brightgreen)](#)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen)](#)
<!-- END: CODEX_BADGES -->
"""
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        if sentinel not in text:
            readme.write_text(block + "\n\n" + text, encoding="utf-8")
            log_change("edit", readme, "prepend manual badges", block)
    else:
        readme.write_text("# Project\n\n" + block + "\n", encoding="utf-8")
        log_change("create", readme, "create with badges", block)


def apply(cov_threshold: int):
    try:
        ensure_precommit()
        ensure_ci_manual(cov_threshold)
        ensure_release_disabled()
        ensure_coverage_gate(cov_threshold)
        ensure_readme_badges()
    except Exception as e:
        q5("3: Best-Effort Construction — write files", str(e), f"path={REPO}")


def validate(cov_threshold: int):
    steps = [
        ("pre-commit (all files)", ["pre-commit", "run", "--all-files"]),
        ("black --check .", ["black", "--check", "."]),
        (
            "isort --check-only --profile black .",
            ["isort", "--check-only", "--profile", "black", "."],
        ),
        (
            "flake8 apply_ci_precommit.py",
            [
                "flake8",
                "--max-line-length=200",
                "--extend-ignore=E203",
                "tools/apply_ci_precommit.py",
            ],
        ),
        (
            "mypy apply_ci_precommit.py",
            ["mypy", "--ignore-missing-imports", "tools/apply_ci_precommit.py"],
        ),
        (
            "pytest with coverage gate",
            [
                "pytest",
                "-q",
                "--maxfail=1",
                "--cov=src",
                f"--cov-fail-under={cov_threshold}",
            ],
        ),
    ]
    with RESULTS.open("a", encoding="utf-8") as fh:
        fh.write(f"\n# Validation {ts()}\n")
        for name, cmd in steps:
            fh.write(f"\n## {name}\n```\n")
            try:
                p = subprocess.run(cmd, capture_output=True, text=True)
                fh.write(p.stdout + p.stderr + f"\n(exit={p.returncode})\n")
            except Exception as e:
                fh.write(f"ERROR: {e}\n")
                q5("6: Finalization — validation", str(e), f"cmd={cmd}")
            fh.write("\n```\n")


def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--apply",
        action="store_true",
        help="create/augment pre-commit, ci (manual), coverage gate, badges",
    )
    ap.add_argument(
        "--validate", action="store_true", help="run local validations (no CI)"
    )
    ap.add_argument(
        "--cov-threshold",
        type=int,
        default=80,
        help="coverage threshold for local gate",
    )
    args = ap.parse_args()
    if args.apply:
        apply(args.cov_threshold)
    if args.validate:
        validate(args.cov_threshold)
    if not (args.apply or args.validate):
        print("Usage: --apply [--validate] [--cov-threshold N]")


if __name__ == "__main__":
    main()
