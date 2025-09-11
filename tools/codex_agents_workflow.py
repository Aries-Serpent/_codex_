#!/usr/bin/env python3
"""
Codex Agents Workflow: docs-only, idempotent updates for AGENTS.md & README.md
- Best-effort construction before pruning
- Evidence-based mapping
- Error capture in ChatGPT-5 research-question format
- DO NOT ACTIVATE ANY GitHub Actions files
"""

from __future__ import annotations

import json
import re
import subprocess  # nosec B404
import sys
import textwrap
from datetime import datetime
from pathlib import Path

# -------- Guardrails --------
DO_NOT_ACTIVATE_GITHUB_ACTIONS = True
WRITE_SCOPE_DOCS_ONLY = True

ROOT = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
)  # nosec B603,B607
CODEx_DIR = ROOT / ".codex"
CHANGE_LOG = CODEx_DIR / "change_log.md"
ERRORS_NDJSON = CODEx_DIR / "errors.ndjson"
RESULTS = CODEx_DIR / "results.md"

README = ROOT / "README.md"
AGENTS = ROOT / "docs" / "guides" / "AGENTS.md"
CONTRIB = ROOT / "CONTRIBUTING.md"
PRECOMMIT = ROOT / ".pre-commit-config.yaml"
PYTEST_INI = ROOT / "pytest.ini"
PYPROJECT = ROOT / "pyproject.toml"


def echo(s: str):
    sys.stdout.write(s + "\n")
    sys.stdout.flush()


def ensure_dirs():
    CODEx_DIR.mkdir(parents=True, exist_ok=True)


def git_clean_or_die():
    out = subprocess.run(
        ["git", "status", "--porcelain"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout  # nosec B603,B607
    if out.strip():
        die_step(
            step="1.1 Verify clean git state",
            err=f"Working tree not clean:\n{out}",
            ctx="Commit or stash changes before running this workflow.",
        )


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_if_changed(path: Path, new: str, rationale: str, header: str = "") -> bool:
    old = read(path)
    if old == new:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(new, encoding="utf-8")
    log_change(path, rationale, old, new, header=header)
    return True


def log_change(path: Path, rationale: str, before: str, after: str, header: str = ""):
    ensure_dirs()
    ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    snippet_before = "\n".join(before.splitlines()[:50])
    snippet_after = "\n".join(after.splitlines()[:50])
    entry = f"""
### {ts} — {path.as_posix()}
**Action:** {rationale}
{f"**Context:** {header}" if header else ""}

<details><summary>Before (first 50 lines)</summary>

```md
{snippet_before}
```

</details>

<details><summary>After (first 50 lines)</summary>

```md
{snippet_after}
```

</details>
"""
    with CHANGE_LOG.open("a", encoding="utf-8") as f:
        f.write(entry)


def die_step(step: str, err: str, ctx: str):
    """Record error in NDJSON + echo ChatGPT-5 research question; then exit non-zero."""
    ensure_dirs()
    obj = {
        "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "step": step,
        "error": err,
        "context": ctx,
    }
    with ERRORS_NDJSON.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj) + "\n")
    msg = f"""Question for ChatGPT-5:
While performing [{step}], encountered the following error:
{err}
Context: {ctx}
What are the possible causes, and how can this be resolved while preserving intended functionality?
"""
    echo(msg)
    sys.exit(2)


def parse_tools_from_precommit(text: str) -> list[str]:
    tools = set()
    for name in [
        "ruff",
        "black",
        "isort",
        "mypy",
        "pyright",
        "flake8",
        "bandit",
        "prettier",
        "eslint",
    ]:
        if re.search(rf"\b{name}\b", text, flags=re.I):
            tools.add(name)
    return sorted(tools)


def ensure_agents_md() -> bool:
    precommit_txt = read(PRECOMMIT)
    pytest_txt = read(PYTEST_INI)
    pyproject_txt = read(PYPROJECT)
    tools = parse_tools_from_precommit(precommit_txt)
    if "pytest" in pytest_txt or "pytest" in pyproject_txt.lower():
        tools = sorted(set(tools) | {"pytest"})
    if precommit_txt:
        tools = sorted(set(tools) | {"pre-commit"})

    required_sections = (
        textwrap.dedent(
            f"""
# AGENTS.md — Maintainers & Automation Guide

## Scope & Non-Goals
- **DO NOT ACTIVATE ANY GitHub Actions files.** This document is discoverable by automation and humans.
- Changes are restricted to documentation and `.codex/*` outputs.

## Logging Environment
- `CODEX_SESSION_ID`: unique session identifier (UUID/GUID).
- `CODEX_LOG_DB_PATH`: path to SQLite/NDJSON logs (default: `.codex/session_logs.db`).
- NDJSON session traces: `.codex/sessions/<SESSION_ID>.ndjson`
- Logs are retained for 30 days; purge older logs to satisfy enterprise retention policy.

## Required Tools
- Core: {", ".join(sorted(tools)) if tools else "pre-commit, pytest"}
- Install hooks:
  ```bash
  pip install pre-commit && pre-commit install
  pre-commit run --all-files
  ```
- Test locally:
  ```bash
  pytest -q
  ```

## Coding Standards (summary)
- Python: format with Black, lint with Ruff, imports with isort (if configured).
- Type checking: mypy/pyright as configured.
- Respect repository conventions noted in README and CONTRIBUTING (if present).

## CI Reference (read-only)
- Continuous Integration runs `pre-commit run --all-files` and `pytest` on PRs/commits.
- See the workflow definition under `.github/workflows/ci.yml` (do **not** modify or activate).
"""
        ).strip()
        + "\n"
    )

    if not AGENTS.exists():
        return write_if_changed(
            AGENTS,
            required_sections,
            "Create AGENTS.md with logging env vars, tools, and coding standards.",
        )
    else:
        cur = read(AGENTS)
        need = []
        if not re.search(r"Required Tools", cur, flags=re.I):
            need.append("tools")
        if not re.search(r"Coding Standards", cur, flags=re.I):
            need.append("standards")
        if not re.search(r"Logs are retained", cur):
            need.append("retention")
        if not need:
            return False
        merged = cur.rstrip() + "\n\n---\n\n" + required_sections
        return write_if_changed(
            AGENTS,
            merged,
            f"Augment AGENTS.md with missing sections: {', '.join(need)}.",
        )


def ensure_readme_refs() -> bool:
    txt = read(README)
    if not txt:
        base = (
            textwrap.dedent(
                """
# codex-universal

See [docs/guides/AGENTS.md](docs/guides/AGENTS.md) for environment variables, logging roles, testing expectations, and tool usage.
**DO NOT ACTIVATE ANY GitHub Actions files.**

## Continuous Integration (local parity)
Run locally before pushing:
```bash
pre-commit run --all-files
pytest -q
```
See the read-only workflow reference at `.github/workflows/ci.yml` (not activated by this script).

## Logging Locations
- SQLite DB: `.codex/session_logs.db`
- NDJSON sessions: `.codex/sessions/<SESSION_ID>.ndjson`
"""
            ).strip()
            + "\n"
        )
        return write_if_changed(
            README, base, "Create minimal README emphasizing AGENTS, CI, and logging."
        )

    changed = False
    if "docs/guides/AGENTS.md" not in txt:
        txt = (
            txt.rstrip()
            + "\n\nFor environment variables, logging roles, testing expectations, and tool usage, see [docs/guides/AGENTS.md](docs/guides/AGENTS.md).\n"
        )
        write_if_changed(README, txt, "Add discoverability link to AGENTS.md.")
        changed = True

    if "Continuous Integration (local parity)" not in txt:
        ci_block = textwrap.dedent(
            """
## Continuous Integration (local parity)
Run locally before pushing:
```bash
pre-commit run --all-files
pytest -q
```
See the read-only workflow reference at `.github/workflows/ci.yml` (not activated by this script).
"""
        ).strip()
        txt = txt.rstrip() + "\n\n" + ci_block + "\n"
        write_if_changed(README, txt, "Ensure CI local run instructions are present.")
        changed = True

    if "Logging Locations" not in txt:
        log_block = textwrap.dedent(
            """
## Logging Locations
- SQLite DB: `.codex/session_logs.db`
- NDJSON sessions: `.codex/sessions/<SESSION_ID>.ndjson`
"""
        ).strip()
        txt = txt.rstrip() + "\n\n" + log_block + "\n"
        write_if_changed(README, txt, "Ensure logging locations are documented.")
        changed = True

    return changed


def write_results(changes: list[str]):
    ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    body = f"""# Results — {ts}

## Implemented

* {"; ".join(changes) if changes else "No content changes required (already compliant)."}

## Residual Gaps

* None detected beyond docs scope.

## Pruning Index

* No pruning executed.

## Notes

* **DO NOT ACTIVATE ANY GitHub Actions files.**

"""
    write_if_changed(RESULTS, body, "Update results summary.")


def main():
    ensure_dirs()
    try:
        git_clean_or_die()
    except subprocess.CalledProcessError as e:
        die_step(
            "1.1 Verify clean git state",
            str(e),
            "git rev-parse/status failed; ensure this is a git repository.",
        )
        return

    changes = []
    try:
        if ensure_agents_md():
            changes.append("AGENTS.md updated")
        if ensure_readme_refs():
            changes.append("README.md updated")
        write_results(changes)
    except Exception as e:
        die_step(
            "3.x Best-effort construction",
            repr(e),
            "An exception occurred while editing docs.",
        )

    echo(
        "Completed. See .codex/change_log.md, .codex/results.md (and errors.ndjson if present)."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
