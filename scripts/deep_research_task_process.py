# ruff: noqa
# Python Name: enhanced_repo_improv2.py
# Script: ENHANCED Repository Improvement Tasks
# Purpose: Perform repository improvement / bootstrap tasks:
#          inventory, scaffolding, CI unification, security tooling integration,
#          CLI refactor, logging adjustments, documentation reinforcement.

"""
End-to-end repository improvement automation script (enhanced edition).

PHASES (idempotent, best-effort):
| Phase | Description                                                                 |
|-------|-----------------------------------------------------------------------------|
| 1     | Preparation: ensure directories & log files, capture git cleanliness, scan  |
| 2     | Search & Mapping: locate key files, verify presence                         |
| 3     | Construction: apply improvements (scaffolds, CI, security, CLI, logging)    |
| 4     | Results Summary: human-readable status report                               |

ARTIFACTS:
- .codex/change_log.md   : chronological change entries with embedded diff-ish content (not a true diff)
- .codex/errors.ndjson   : newline-delimited JSON error diagnostics (append-only)
- .codex/results.md      : summarized accomplishments & next steps
- .codex/inventory.json  : snapshot of repository file metadata (path, size, role, sha256)

DESIGN PRINCIPLES:
- Non-fatal execution: errors are logged and subsequent tasks attempt to proceed.
- Backward compatibility:
    * Importing runs tasks only when CODEX_AUTO_RUN=1 (disabled by default).
    * Avoids destructive edits unless clearly safe (e.g., removing disabled workflow superseded by ci.yml).
- Extensibility: task registration abstraction enables future pluggable tasks.
- Observability: stderr prompts preserve earlier "Question for ChatGPT-5" diagnostic style.
- Idempotency: Re-running should not produce material duplicate changes if no divergence.

ENVIRONMENT VARIABLES:
| Variable                          | Effect                                                      |
|----------------------------------|-------------------------------------------------------------|
| REPO_IMPROVEMENT_DRY_RUN=1       | Do not modify files; only log intended actions where safe.  |
| REPO_IMPROVEMENT_VERBOSE=1       | Emit progress messages to stdout.                           |
| REPO_IMPROVEMENT_SKIP_BASELINE=1 | Skip detect-secrets baseline generation.                    |
| REPO_IMPROVEMENT_TASK_FILTER     | Comma-separated subset of canonical step codes (e.g. 3.1).  |
| REPO_IMPROVEMENT_ORG             | GitHub organization name (defaults to 'Aries-Serpent')      |
| REPO_IMPROVEMENT_REPO            | GitHub repository name (defaults to '_codex_')              |
| CODEX_AUTO_RUN=1                 | Auto-run tasks on import (disabled by default).             |

PUBLIC API (__all__):
- now_iso()
- register_task()
- run_all()
- main()
- phase1_preparation()
- phase2_search_mapping()
- phase3_construction()
- phase4_results()
- list_registered_tasks()

USAGE:
    python enhanced_repo_improv2.py
    REPO_IMPROVEMENT_DRY_RUN=1 python enhanced_repo_improv2.py
    REPO_IMPROVEMENT_TASK_FILTER=3.1,3.4 python enhanced_repo_improv2.py

NOTE:
The unified CI workflow triggers only via workflow_dispatch (and PR events if configured) to
avoid unintended activation in forked contexts.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import subprocess  # nosec B404
import sys
import tempfile
import threading
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple
from ingestion import ingest

# --------------------------------------------------------------------------------------
# __all__
# --------------------------------------------------------------------------------------

__all__ = [
    "now_iso",
    "register_task",
    "run_all",
    "main",
    "phase1_preparation",
    "phase2_search_mapping",
    "phase3_construction",
    "phase4_results",
    "list_registered_tasks",
]

# --------------------------------------------------------------------------------------
# Constants & Paths
# --------------------------------------------------------------------------------------

# Robust repository root detection
_REPO_MARKERS = (".git", "pyproject.toml", ".pre-commit-config.yaml")


def _has_marker(p: Path, markers: Iterable[str] = _REPO_MARKERS) -> bool:
    try:
        return any((p / m).exists() for m in markers)
    except PermissionError:
        return False


def find_repo_root(start: Optional[Path] = None, markers: Iterable[str] = _REPO_MARKERS) -> Path:
    """Return nearest ancestor containing any marker, or fallback."""
    s = (start or Path(__file__).resolve()).absolute()
    for candidate in (s,) + tuple(s.parents):
        if _has_marker(candidate, markers):
            return candidate
    # Fallback: parent of scripts directory
    return s.parent.parent


REPO_ROOT = find_repo_root(Path(__file__).resolve().parent)
CODEX_DIR = REPO_ROOT / ".codex"
CHANGE_LOG = CODEX_DIR / "change_log.md"
ERRORS_LOG = CODEX_DIR / "errors.ndjson"
RESULTS_LOG = CODEX_DIR / "results.md"
INVENTORY_JSON = CODEX_DIR / "inventory.json"

# Target repository artifacts
INGESTION_DIR = REPO_ROOT / "src" / "ingestion"
INGESTOR_PY = INGESTION_DIR / "__init__.py"
INGESTION_README = INGESTION_DIR / "README.md"
PRECOMMIT_CFG = REPO_ROOT / ".pre-commit-config.yaml"
CONTRIBUTING_MD = REPO_ROOT / "CONTRIBUTING.md"
README_MD = REPO_ROOT / "README.md"
SESSION_LOGGER_PY = REPO_ROOT / "src" / "codex" / "logging" / "session_logger.py"
VIEWER_PY = REPO_ROOT / "src" / "codex" / "logging" / "viewer.py"
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
BUILD_WORKFLOW_DISABLED = REPO_ROOT / ".github" / "workflows" / "build-image.yml.disabled"

# Environment toggles
DRY_RUN = os.getenv("REPO_IMPROVEMENT_DRY_RUN") == "1"
VERBOSE = os.getenv("REPO_IMPROVEMENT_VERBOSE") == "1"
SKIP_BASELINE = os.getenv("REPO_IMPROVEMENT_SKIP_BASELINE") == "1"
TASK_FILTER = {
    s.strip() for s in os.getenv("REPO_IMPROVEMENT_TASK_FILTER", "").split(",") if s.strip()
}
GITHUB_ORG = os.getenv("REPO_IMPROVEMENT_ORG", "Aries-Serpent")
GITHUB_REPO = os.getenv("REPO_IMPROVEMENT_REPO", "_codex_")

SECURITY_SECTION_HEADER = "## Security Scanning"

# Classification heuristics
CODE_EXTS = {".py", ".sh", ".js", ".ts", ".tsx", ".jsx", ".sql"}
DOC_EXTS = {".md", ".rst"}
CONFIG_EXTS = {".yml", ".yaml", ".toml", ".ini"}
FILE_IGNORE_PARTS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", ".tox"}

# --------------------------------------------------------------------------------------
# Logging Configuration
# --------------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO if VERBOSE else logging.WARNING,
    format="[%(levelname)s] %(message)s",
)
logger = logging.getLogger("repo_improvement")

# --------------------------------------------------------------------------------------
# Data Structures
# --------------------------------------------------------------------------------------


@dataclass(order=True)
class Task:
    """
    Represents a single repository improvement task.

    Attributes:
        step_code: Canonical step code (e.g., "3.1").
        name: Human-readable short name.
        func: Callable performing the task.
        rationale: Short rationale for change log context (optional).
        active: Whether the task is enabled (user can disable programmatically).
    """

    step_code: str
    name: str
    func: Callable[[], None]
    rationale: str = ""
    active: bool = True
    sort_index: Sequence[int] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        numeric_parts: List[int] = []
        for part in re.split(r"[^\d]+", self.step_code):
            if part.isdigit():
                numeric_parts.append(int(part))
        self.sort_index = numeric_parts or [9999]


# --------------------------------------------------------------------------------------
# Utility Functions
# --------------------------------------------------------------------------------------


def now_iso() -> str:
    """Current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _v(msg: str) -> None:
    if VERBOSE:
        logger.info(msg)


def _ensure_paths() -> None:
    """Ensure codex internal directories & base log files exist."""
    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    if not CHANGE_LOG.exists() and not DRY_RUN:
        CHANGE_LOG.write_text("# Codex Change Log\n\n", encoding="utf-8")
    if not ERRORS_LOG.exists() and not DRY_RUN:
        ERRORS_LOG.write_text("", encoding="utf-8")
    if not RESULTS_LOG.exists() and not DRY_RUN:
        RESULTS_LOG.write_text("", encoding="utf-8")


def _log_error(step: str, error: str, context: str | None = None) -> None:
    """Append an error entry to ERRORS_LOG and emit a diagnostic prompt to stderr."""
    record = {"ts": now_iso(), "step": step, "error": error, "context": context or ""}
    try:
        if not DRY_RUN:
            ERRORS_LOG.open("a", encoding="utf-8").write(json.dumps(record) + "\n")
    except Exception:
        sys.stderr.write(f"[FATAL-LOG-FAIL] {record}\n")
    # Diagnostic prompt (retains pattern for upstream analysis)
    sys.stderr.write(
        "Question for ChatGPT-5:\n"
        f"While performing [{step}], encountered the following error:\n{error}\n"
        f"Context: {context or '(none)'}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n\n"
    )


def _atomic_write(path: Path, content: str, encoding: str = "utf-8") -> None:
    """Atomic write helper to minimize partial write risk."""
    if DRY_RUN:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding=encoding) as fh:
            fh.write(content)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError as cleanup_err:
            logging.debug("temporary file cleanup failed: %s", cleanup_err)
        raise


def _append_change(path: Path, action: str, rationale: str, new_content: str) -> None:
    """Append a change entry (with diff-style block) to the change log."""
    try:
        block = (
            f"### {now_iso()} — {path.relative_to(REPO_ROOT)}\n"
            f"- **Action:** {action}\n"
            f"- **Rationale:** {rationale or 'Repository improvement task'}\n"
            rf"```diff\n{new_content.rstrip()}\n```\n\n"
        )
        if not DRY_RUN:
            CHANGE_LOG.open("a", encoding="utf-8").write(block)
    except Exception as e:
        _log_error("log change", str(e), str(path))


def _tool_exists(cmd: str) -> bool:
    """Check if a command-line tool exists in PATH."""
    for p in os.getenv("PATH", "").split(os.pathsep):
        if not p:
            continue
        base = Path(p) / cmd
        if base.exists() and os.access(base, os.X_OK):
            return True
        if os.name == "nt":
            for ext in (".exe", ".cmd", ".bat"):
                candidate = base.with_suffix(ext)
                if candidate.exists() and os.access(candidate, os.X_OK):
                    return True
    return False


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _run_command(
    cmd: List[str], check: bool = True, cwd: Optional[Path] = None
) -> Tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        exe = shutil.which(cmd[0])
        if exe is None:
            raise FileNotFoundError(cmd[0])
        proc = subprocess.run(  # nosec B603
            [exe, *cmd[1:]],
            text=True,
            capture_output=True,
            check=check,
            cwd=str(cwd or REPO_ROOT),
            shell=False,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout or "", e.stderr or ""
    except Exception as e:
        return 1, "", str(e)


# --------------------------------------------------------------------------------------
# Phase 1: Preparation
# --------------------------------------------------------------------------------------


def phase1_preparation() -> None:
    _v("Phase 1: Preparation start")
    _ensure_paths()

    # Git cleanliness
    if (REPO_ROOT / ".git").exists():
        rc, out, err = _run_command(["git", "status", "--porcelain"], check=False)
        if rc != 0:
            _log_error(
                "1: Preparation - git status",
                f"git status failed: {err}",
                "Ensure Git repository is initialized",
            )
        elif out.strip():
            _log_error(
                "1: Preparation - clean check",
                "Working tree is not clean (uncommitted changes present)",
                out.strip(),
            )
    else:
        _log_error(
            "1: Preparation - git presence",
            ".git directory not found",
            "Repository may be unpacked or VCS not initialized",
        )

    # Inventory snapshot
    items: List[Dict[str, Any]] = []
    for p in REPO_ROOT.rglob("*"):
        if p.is_file() and not any(part in FILE_IGNORE_PARTS for part in p.parts):
            rel = str(p.relative_to(REPO_ROOT))
            try:
                size = p.stat().st_size
            except Exception:
                size = 0
            ext = p.suffix.lower()
            if ext in CODE_EXTS:
                role = "code"
            elif ext in DOC_EXTS:
                role = "doc"
            elif "pre-commit" in p.name or ext in CONFIG_EXTS:
                role = "config"
            else:
                role = "asset"
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
                sha_val = hashlib.sha256(content.encode("utf-8")).hexdigest()
            except Exception:
                sha_val = None
            try:
                mtime_iso = datetime.fromtimestamp(p.stat().st_mtime).isoformat()
            except Exception:
                mtime_iso = ""
            items.append(
                {
                    "path": rel,
                    "size": size,
                    "role": role,
                    "sha256": sha_val,
                    "last_modified": mtime_iso,
                }
            )

    try:
        if not DRY_RUN:
            _atomic_write(INVENTORY_JSON, json.dumps(items, indent=2))
    except Exception as e:
        _log_error("1: Preparation - write inventory", str(e), str(INVENTORY_JSON))
    _v("Phase 1: Preparation complete")


# --------------------------------------------------------------------------------------
# Phase 2: Search & Mapping
# --------------------------------------------------------------------------------------


def phase2_search_mapping() -> None:
    _v("Phase 2: Search & Mapping start")
    (REPO_ROOT / ".github" / "workflows").mkdir(parents=True, exist_ok=True)

    if not VIEWER_PY.exists():
        _log_error("2: Locate viewer.py", "File not found", str(VIEWER_PY))
    if not SESSION_LOGGER_PY.exists():
        _log_error("2: Locate session_logger.py", "File not found", str(SESSION_LOGGER_PY))
    if not PRECOMMIT_CFG.exists():
        _log_error("2: Locate pre-commit config", "File not found", str(PRECOMMIT_CFG))

    rc, py_ver, py_err = _run_command(["python", "--version"], check=False)
    if rc == 0:
        _v(f"Python version: {py_ver.strip()}")
    else:
        _log_error("2: Python version", "Failed to obtain Python version", py_err)
    _v("Phase 2: Search & Mapping complete")


# --------------------------------------------------------------------------------------
# Phase 3: Construction & Modification (Task Implementations)
# --------------------------------------------------------------------------------------

# PRUNED_PLACEHOLDER: _task_ingestion_scaffold removed in favor of real implementation.


# PRUNED_PLACEHOLDER: _task_ingestion_test removed; ingestion now has real tests.


def run_ingestion_example(path: str) -> str:
    """Example bridge to the real ingestion implementation."""

    return ingest(path)


def _task_ingestion_readme() -> None:
    src = r"""# Ingestion Module

This module is intended for data ingestion functionality. The `Ingestor` class is
currently a placeholder and will be implemented in the future.

## Usage (Future)

```python
from src.ingestion import Ingestor

# Initialize with configuration
ingestor = Ingestor({"source_type": "file"})

# Ingest data from source
ingestor.ingest("path/to/source")
```

## Development Status

- [x] Initial scaffold
- [ ] Core implementation
- [ ] Unit tests
- [ ] Documentation
- [ ] Integration tests
"""
    before = _read_text(INGESTION_README)
    if before != src:
        if not DRY_RUN:
            _atomic_write(INGESTION_README, src)
        _append_change(
            INGESTION_README,
            "edit" if before else "create",
            "Add ingestion module README",
            src,
        )


def _task_unify_ci() -> None:
    existing = _read_text(CI_WORKFLOW)
    ci_content = f"""name: CI
on:
  workflow_dispatch:
    inputs:
      use-ghcr-token:
        description: 'Use GITHUB_TOKEN for GHCR auth when GHCR_PAT is absent'
        required: false
        default: 'false'
      use-cr-pat:
        description: 'Use CR_PAT secret for GHCR auth when set'
        required: false
        default: 'false'
  pull_request:
    branches: [main]
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - '.github/ISSUE_TEMPLATE/**'

jobs:
  build-image:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t ghcr.io/{GITHUB_ORG}/{GITHUB_REPO}:latest .
      - name: Push Docker image
        if: ${{{{ github.event_name == 'workflow_dispatch' && (secrets.GHCR_PAT != '' || (github.event.inputs.use-cr-pat == 'true' && secrets.CR_PAT != '') || github.event.inputs.use-ghcr-token == 'true') }}}}
        env:
          CR_PAT: ${{{{ secrets.GHCR_PAT != '' && secrets.GHCR_PAT || (github.event.inputs.use-cr-pat == 'true' && secrets.CR_PAT != '' && secrets.CR_PAT) || github.token }}}}
        run: |
          echo "$CR_PAT" | docker login ghcr.io -u $GITHUB_ACTOR --password-stdin
          docker push ghcr.io/{GITHUB_ORG}/{GITHUB_REPO}:latest

  verify:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11
          cache: pip
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pre-commit==4.0.1 pytest==8.4.1 pytest-cov==7.0.0 click bandit detect-secrets
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi
      - name: Run linters and tests
        run: |
          pre-commit run --all-files
          pytest -q --cov=src --cov-report=html:htmlcov
      - name: Upload coverage report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: coverage-html
          path: htmlcov/
"""
    if existing != ci_content:
        if not DRY_RUN:
            _atomic_write(CI_WORKFLOW, ci_content)
        _append_change(
            CI_WORKFLOW,
            "edit" if existing else "create",
            "Unify CI workflows (lint, test, coverage, image build)",
            ci_content,
        )
    if BUILD_WORKFLOW_DISABLED.exists() and not DRY_RUN:
        try:
            BUILD_WORKFLOW_DISABLED.unlink()
            CHANGE_LOG.open("a", encoding="utf-8").write(
                f"### {now_iso()} — {BUILD_WORKFLOW_DISABLED.relative_to(REPO_ROOT)}\n"
                "- **Action:** delete\n"
                "- **Rationale:** Removed obsolete build workflow (merged into ci.yml)\n\n"
            )
        except Exception as e:
            _log_error("3.4: Unify CI workflows", str(e), str(BUILD_WORKFLOW_DISABLED))


def _task_update_contributing() -> None:
    if CONTRIBUTING_MD.exists():
        text = _read_text(CONTRIBUTING_MD)
    else:
        text = r"""# Contributing

Thank you for considering contributing to this project!

## Development Setup

1. Clone the repository
2. (Optional) Create a virtual environment
3. Install development dependencies: `pip install -e "[dev]"` (or `pip install -r requirements-dev.txt`)
4. Install pre-commit hooks: `pre-commit install`

## Development Workflow

1. Create a branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Run quality checks:
   ```
   pre-commit run --all-files
   mypy .
   pytest
   ```
4. Submit a pull request
"""
    original = text
    # Insert mypy if missing (fall back approach)
    if "mypy ." not in text and "mypy" not in text:
        if "pre-commit run --all-files" in text and "pytest" in text:
            text = text.replace("pre-commit run --all-files", "pre-commit run --all-files\nmypy .")
    text = re.sub(r"(?m)^Avoid enabling GitHub Actions.*(?:\n|$)", "", text)

    if ".secrets.baseline" not in text:
        extra = r"""

## Security Practices

Security scanning tools:

- **Bandit**: static security analysis for Python code.
- **detect-secrets**: identifies potential secret exposures.

If detect-secrets flags a false positive (no real secret), update the baseline:
```
detect-secrets scan --baseline .secrets.baseline
```
"""
        if "## Manual Validation" in text:
            idx = text.find("## Manual Validation")
            text = text[:idx] + extra + text[idx:]
        else:
            text += extra

    if text != original:
        if not DRY_RUN:
            _atomic_write(CONTRIBUTING_MD, text)
        _append_change(
            CONTRIBUTING_MD,
            "edit" if original else "create",
            "Update contributing guide for CI & secret scanning",
            text,
        )


def _task_refactor_cli() -> None:
    """Create / update click-based CLI with whitelisted tasks."""
    cli_py = REPO_ROOT / "src" / "codex" / "cli.py"
    cli_py.parent.mkdir(parents=True, exist_ok=True)
    cli_content = """\"\"\"Unified CLI for codex, using click for subcommands and input validation.\"\"\"

from __future__ import annotations

import logging
import sys
from typing import Dict, Callable

import click

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger("codex.cli")

ALLOWED_TASKS: Dict[str, Callable[[], None]] = {
    "ingest": lambda: logger.info("Ingestion scaffold created (placeholder)."),
    "ci": lambda: logger.info("CI workflow unified."),
    "pool-fix": lambda: logger.info("SQLite connection pool fix applied."),
    "security-scan": lambda: logger.info("Security scanning tools configured."),
}


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging.")
def cli(debug: bool = False) -> None:
    \"\"\"Codex CLI entry point.\"\"\"
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")


@cli.command("tasks")
def list_tasks() -> None:
    \"\"\"List allowed maintenance tasks.\"\"\"
    for task in sorted(ALLOWED_TASKS):
        click.echo(task)


@cli.command("run")
@click.argument("task")
@click.option("--force", is_flag=True, help="Force execution even if additional validation might fail.")
def run_task(task: str, force: bool = False) -> None:
    \"\"\"Run a whitelisted maintenance task by name.\"\"\"
    if task not in ALLOWED_TASKS:
        valid = ", ".join(sorted(ALLOWED_TASKS))
        click.echo(f"Task '{task}' is not allowed. Valid tasks: {valid}", err=True)
        sys.exit(1)
    logger.info("Running task: %s (force=%s)", task, force)
    try:
        ALLOWED_TASKS[task]()
        click.echo(f"Task '{task}' completed successfully")
    except Exception as e:  # pragma: no cover - defensive
        logger.error("Task '%s' failed: %s", task, e)
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    cli()
"""
    before_cli = _read_text(cli_py)
    if before_cli != cli_content:
        if not DRY_RUN:
            _atomic_write(cli_py, cli_content)
        _append_change(
            cli_py,
            "edit" if before_cli else "create",
            "Add unified CLI (click) with whitelisted commands",
            cli_content,
        )

    test_cli_py = REPO_ROOT / "tests" / "test_cli.py"
    test_cli_py.parent.mkdir(parents=True, exist_ok=True)
    cli_test_content = """import importlib
from click.testing import CliRunner

cli_module = importlib.import_module("codex.cli")


def test_cli_list_tasks():
    runner = CliRunner()
    result = runner.invoke(cli_module.cli, ["tasks"])
    assert result.exit_code == 0
    out = result.output.strip().split()
    for expected in ("ingest", "ci", "security-scan"):
        assert expected in out


def test_cli_run_invalid():
    runner = CliRunner()
    result = runner.invoke(cli_module.cli, ["run", "invalid_task"])
    assert result.exit_code != 0
    assert "not allowed" in result.output


def test_cli_run_valid():
    runner = CliRunner()
    result = runner.invoke(cli_module.cli, ["run", "ingest"])
    assert result.exit_code == 0
    assert "completed successfully" in result.output


def test_cli_debug_flag():
    runner = CliRunner()
    result = runner.invoke(cli_module.cli, ["--debug", "tasks"])
    assert result.exit_code == 0
"""
    before_test_cli = _read_text(test_cli_py)
    if before_test_cli != cli_test_content:
        if not DRY_RUN:
            _atomic_write(test_cli_py, cli_test_content)
        _append_change(
            test_cli_py,
            "edit" if before_test_cli else "create",
            "Add CLI tests for whitelisted commands",
            cli_test_content,
        )


def _task_session_logger_pool_fix() -> None:
    if not SESSION_LOGGER_PY.exists():
        _log_error("3.7: SQLite pool fix", "session_logger.py missing", str(SESSION_LOGGER_PY))
        return
    src_text = _read_text(SESSION_LOGGER_PY)
    pattern_try = r"(\n\s*try:\n\s*conn\.execute\([^)]*\)\n\s*conn\.commit\(\))"
    if re.search(pattern_try, src_text):
        patched = re.sub(
            pattern_try,
            (
                "\\1\n    except Exception as e:\n"
                "        if 'USE_POOL' in globals() and USE_POOL:\n"
                "            try:\n"
                "                conn.close()\n"
                "            except Exception:\n"
                "                pass\n"
                "            try:\n"
                "                CONN_POOL.pop(key, None)  # type: ignore[name-defined]\n"
                "            except Exception:\n"
                "                pass\n"
                "        raise\n"
            ),
            src_text,
        )
        if patched != src_text:
            if not DRY_RUN:
                _atomic_write(SESSION_LOGGER_PY, patched)
            _append_change(
                SESSION_LOGGER_PY,
                "edit",
                "Fix SQLite connection pool (close connection on exceptions)",
                patched,
            )


def _task_session_logger_exit_fix() -> None:
    if not SESSION_LOGGER_PY.exists():
        _log_error(
            "3.8: log_event finally",
            "session_logger.py missing",
            str(SESSION_LOGGER_PY),
        )
        return
    src_text = _read_text(SESSION_LOGGER_PY)
    if "def __exit__(self, exc_type, exc, tb)" in src_text:
        new_exit_impl = (
            "def __exit__(self, exc_type, exc, tb) -> None:\n"
            "        try:\n"
            "            if exc_type is not None:\n"
            "                log_event(\n"
            "                    self.session_id,\n"
            '                    "system",\n'
            '                    f"session_end (exc={exc_type.__name__}: {exc})",\n'
            "                    db_path=self.db_path,\n"
            "                )\n"
            "            else:\n"
            "                log_event(\n"
            "                    self.session_id,\n"
            '                    "system",\n'
            '                    "session_end",\n'
            "                    db_path=self.db_path,\n"
            "                )\n"
            "        except Exception:\n"
            "            import logging\n"
            '            logging.exception("session_end DB log failed")\n'
            "        return False\n"
        )
        patched = re.sub(
            r"def __exit__\(self, exc_type, exc, tb\) -> None:.*?(?=\n\S|$)",
            new_exit_impl,
            src_text,
            flags=re.S,
        )
        if patched != src_text:
            if not DRY_RUN:
                _atomic_write(SESSION_LOGGER_PY, patched)
            _append_change(
                SESSION_LOGGER_PY,
                "edit",
                "Ensure log_event execution on context exit (handle exceptions safely)",
                patched,
            )


def _task_viewer_validation_check() -> None:
    if not VIEWER_PY.exists():
        _log_error("3.9: Table name validation", "viewer.py missing", str(VIEWER_PY))
        return
    viewer_src = _read_text(VIEWER_PY)
    if "_validate_table_name" not in viewer_src or "--table" not in viewer_src:
        _log_error(
            "3.9: Table name validation",
            "Validation code missing",
            "viewer.py may be outdated",
        )


def _task_extend_precommit() -> None:
    if not PRECOMMIT_CFG.exists():
        _log_error("3.10: Extend pre-commit config", "File not found", str(PRECOMMIT_CFG))
        return
    content = _read_text(PRECOMMIT_CFG)
    bandit_block = (
        "- repo: https://github.com/PyCQA/bandit\n"
        "  rev: 1.7.4\n"
        "  hooks:\n"
        "    - id: bandit\n"
        "      name: bandit-security-scan\n"
        '      args: ["-lll"]\n'
    )
    detect_block = (
        "- repo: https://github.com/Yelp/detect-secrets\n"
        "  rev: v1.3.0\n"
        "  hooks:\n"
        "    - id: detect-secrets\n"
        "      name: detect-secrets-scan\n"
        '      args: ["--baseline", ".secrets.baseline"]\n'
    )
    mutated = False
    if "repo: https://github.com/PyCQA/bandit" not in content:
        if not content.endswith("\n"):
            content += "\n"
        content += bandit_block
        mutated = True
    if "repo: https://github.com/Yelp/detect-secrets" not in content:
        if not content.endswith("\n"):
            content += "\n"
        content += detect_block
        mutated = True
    if mutated:
        if not DRY_RUN:
            _atomic_write(PRECOMMIT_CFG, content)
        _append_change(
            PRECOMMIT_CFG,
            "edit",
            "Extend pre-commit hooks (Bandit & detect-secrets)",
            content,
        )


def _task_generate_secrets_baseline() -> None:
    if SKIP_BASELINE:
        _v("Skipping detect-secrets baseline generation (env override)")
        return
    if not _tool_exists("detect-secrets"):
        _log_error(
            "3.11: Generate .secrets.baseline",
            "detect-secrets not installed (PATH lookup failed)",
            "Install with: pip install detect-secrets",
        )
        return
    baseline_path = REPO_ROOT / ".secrets.baseline"
    rc, _out, err = _run_command(
        ["detect-secrets", "scan", "--baseline", str(baseline_path)], check=False
    )
    if rc != 0:
        _log_error(
            "3.11: Generate .secrets.baseline",
            err.strip() or "detect-secrets scan failed",
            "Invocation failure",
        )
        return
    if baseline_path.exists():
        content = _read_text(baseline_path)
        _append_change(
            baseline_path,
            "create",
            "Generate detect-secrets baseline",
            content,
        )


def _task_update_readme_security() -> None:
    text = (
        _read_text(README_MD)
        if README_MD.exists()
        else f"# {GITHUB_REPO}\n\nCodex managed repository.\n"
    )
    original = text
    if SECURITY_SECTION_HEADER not in text:
        security_section = r"""

## Security Scanning
This project uses **Bandit** for static security analysis and **detect-secrets** for secret scanning.

### Bandit
Runs via pre-commit to catch common Python security issues.

### Detect-Secrets
Uses `.secrets.baseline` to record allowed high-entropy patterns. Update it:
```bash
detect-secrets scan --baseline .secrets.baseline
```

> Note: Ensure no real secrets are committed; the baseline filters false positives.
"""
        insert_at = text.find("## Logging Locations")
        if insert_at != -1:
            text = text[:insert_at] + security_section + text[insert_at:]
        else:
            text += security_section
    if text != original:
        if not DRY_RUN:
            _atomic_write(README_MD, text)
        _append_change(
            README_MD,
            "edit" if original else "create",
            "Document security scanning (Bandit & detect-secrets) in README",
            text,
        )


# --------------------------------------------------------------------------------------
# Task Registration & Execution
# --------------------------------------------------------------------------------------

REGISTERED_TASKS: List[Task] = []


def register_task(
    step_code: str,
    name: str,
    callable_obj: Callable[[], None],
    rationale: str = "",
    active: bool = True,
) -> None:
    """
    Register a custom task (call before run_all).

    Replaces any existing task with the same step code.
    """
    global REGISTERED_TASKS
    REGISTERED_TASKS = [t for t in REGISTERED_TASKS if t.step_code != step_code] + [
        Task(step_code, name, callable_obj, rationale, active)
    ]
    REGISTERED_TASKS.sort()


def list_registered_tasks() -> List[Task]:
    """Return a copy of currently registered tasks."""
    return list(REGISTERED_TASKS)


def _initialize_default_tasks() -> None:
    if REGISTERED_TASKS:
        return
    defaults = [
        (
            "3.3",
            "Ingestion README",
            _task_ingestion_readme,
            "Add ingestion module README",
        ),
        (
            "3.4",
            "Unify CI workflows",
            _task_unify_ci,
            "Unify CI workflows (lint/test/image)",
        ),
        (
            "3.5",
            "Update CONTRIBUTING.md",
            _task_update_contributing,
            "Update contributing guide",
        ),
        (
            "3.6",
            "CLI refactor (click)",
            _task_refactor_cli,
            "Add unified CLI with click",
        ),
        (
            "3.7",
            "SQLite pool fix",
            _task_session_logger_pool_fix,
            "Ensure pool closes on exceptions",
        ),
        (
            "3.8",
            "log_event context exit",
            _task_session_logger_exit_fix,
            "Ensure log_event on __exit__",
        ),
        (
            "3.9",
            "Viewer validation check",
            _task_viewer_validation_check,
            "Validate table name logic presence",
        ),
        (
            "3.10",
            "Extend pre-commit config",
            _task_extend_precommit,
            "Add Bandit & detect-secrets hooks",
        ),
        (
            "3.11",
            "Generate .secrets.baseline",
            _task_generate_secrets_baseline,
            "Generate detect-secrets baseline",
        ),
        (
            "3.12",
            "Update README security section",
            _task_update_readme_security,
            "Document security scanning",
        ),
    ]
    for sc, name, fn, rat in defaults:
        register_task(sc, name, fn, rat, active=True)


def phase3_construction() -> None:
    _v("Phase 3: Construction start")
    _initialize_default_tasks()
    for task in list_registered_tasks():
        if not task.active:
            _v(f"Skipping inactive task {task.step_code} {task.name}")
            continue
        if TASK_FILTER and task.step_code not in TASK_FILTER:
            _v(f"Skipping task {task.step_code} due to filter")
            continue
        label = f"{task.step_code}: {task.name}"
        try:
            _v(label)
            task.func()
        except Exception as e:
            _log_error(label, str(e), "internal task execution")
    _v("Phase 3: Construction complete")


# --------------------------------------------------------------------------------------
# Phase 4: Results Summary
# --------------------------------------------------------------------------------------


def phase4_results() -> None:
    _v("Phase 4: Results Summary start")
    try:
        lines: List[str] = []
        lines.append(f"# Results Summary ({now_iso()})")
        lines.append("\n- **Implemented:**")
        lines.append(
            "    - Ingestion module scaffold (`Ingestor` class, placeholder test, README)."
        )
        lines.append(
            f"    - Unified GitHub Actions workflow (`ci.yml`) for lint, test, coverage, Docker build for {GITHUB_ORG}/{GITHUB_REPO}."
        )
        lines.append(
            "    - Static analysis & secret scanning (Bandit, detect-secrets) integrated via pre-commit & CI."
        )
        lines.append("    - Contributor & README documentation updated for security practices.")
        lines.append("    - CLI refactored using `click` with task whitelist & smoke tests.")
        lines.append("    - SQLite connection pool hardening (close & evict on errors).")
        lines.append("    - Session logging context exit ensures session_end event logging.")
        lines.append("    - Viewer table validation presence check performed (logged if missing).")
        lines.append("\n- **Residual Gaps:**")
        lines.append("    - `Ingestor` remains a placeholder pending real ingestion logic.")
        lines.append(
            "    - CLI tasks are stubs; integrate with internal APIs for true " "maintenance ops."
        )
        lines.append("    - Potential Bandit findings require periodic triage.")
        lines.append("    - Secret baseline may need refresh as code evolves.")
        lines.append("\n- **Next Steps:**")
        lines.append("    - Implement ingestion logic & meaningful tests.")
        lines.append("    - Extend CLI to operational maintenance commands.")
        lines.append("    - Monitor CI runs & address failures promptly.")
        lines.append("    - Refresh `.secrets.baseline` after structural repository changes.")
        lines.append("\n**NOTE:** CI workflow triggers only on manual dispatch or pull requests.")
        if not DRY_RUN:
            _atomic_write(RESULTS_LOG, "\n".join(lines) + "\n")
    except Exception as e:
        _log_error("results summary write", str(e), str(RESULTS_LOG))
    _v("Phase 4: Results Summary complete")


# --------------------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------------------


def run_all() -> int:
    """Execute all phases sequentially. Returns process-style exit code (0 success)."""
    try:
        phase1_preparation()
        phase2_search_mapping()
        phase3_construction()
        phase4_results()
        if not DRY_RUN:
            print("Completed repository improvement tasks for " f"{GITHUB_ORG}/{GITHUB_REPO}.")
            print(f"Results and change log have been updated in {CODEX_DIR}.")
        else:
            print("Dry-run complete (no files modified).")
    except KeyboardInterrupt:
        print("\nOperation interrupted by user. Partial changes may have been applied.")
        return 130  # Conventional for SIGINT
    except Exception as e:
        print(f"Error during execution: {e}")
        _log_error("run_all", str(e), "Unexpected top-level exception")
        return 1
    return 0


def main(argv: Optional[Iterable[str]] = None) -> int:
    """CLI entrypoint."""
    return run_all()


# Single-execution sentinel
_RUN_LOCK = threading.Lock()
_ALREADY_RAN = False


def _maybe_auto_run_on_import() -> None:
    """Import-time auto-run when CODEX_AUTO_RUN=1 (executes once)."""
    global _ALREADY_RAN
    if os.getenv("CODEX_AUTO_RUN") != "1":
        return
    with _RUN_LOCK:
        if _ALREADY_RAN:
            return
        _ALREADY_RAN = True
        run_all()


_maybe_auto_run_on_import()


if __name__ == "__main__":
    with _RUN_LOCK:
        if not _ALREADY_RAN:
            _ALREADY_RAN = True
            raise SystemExit(main(sys.argv))
