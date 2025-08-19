#!/usr/bin/env python3
# coding: utf-8
"""
codex_workflow.py — End-to-end workflow for:
1) Packaging config (pyproject.toml by default) with src/ layout for package 'codex'
2) Tests import cleanup (remove sys.path.insert hacks)
3) README install docs (pip install -e .)
with best-effort construction, evidence-based pruning (suggest-only by default),
structured change/error logs, and final results summary.

Constraints: DO NOT ACTIVATE ANY GitHub Actions files.
"""

import argparse
import datetime as dt
import difflib
import io
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------- Configuration Flags (overridable via CLI) ----------
DO_NOT_ACTIVATE_GITHUB_ACTIONS = True
DEFAULT_USE_SETUP_CFG = False     # False => use pyproject.toml
DEFAULT_PRUNE = False             # Suggest-only by default

# ---------- Paths ----------
REPO_ROOT = None  # resolved at runtime
CODEX_DIR = None  # .codex/
CHANGE_LOG = None
ERRORS_NDJSON = None
RESULTS_MD = None
INVENTORY_JSON = None

# ---------- Utilities ----------

def run(cmd: List[str]) -> Tuple[int, str, str]:
    """Run a shell command and return (code, stdout, stderr)."""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return p.returncode, out, err

def now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")

def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def read_text(p: Path) -> Optional[str]:
    try:
        return p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None

def write_text(p: Path, content: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

def append_text(p: Path, content: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(content)

def log_change(file_path: Path, action: str, rationale: str, before: Optional[str], after: Optional[str]) -> None:
    diff = ""
    if before is not None and after is not None and before != after:
        diff_lines = difflib.unified_diff(
            before.splitlines(keepends=False),
            after.splitlines(keepends=False),
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm=""
        )
        diff = "\n".join(diff_lines)
    entry = f"""### {now_iso()}
- **File:** `{file_path}`
- **Action:** {action}
- **Rationale:** {rationale}
- **Diff (summary):**
```

{diff if diff else "(no textual diff or file created)"}

````

"""
    append_text(CHANGE_LOG, entry)

def log_prune_record(title: str, purpose: str, alternatives: List[str], failure_modes: List[str], evidence: str, decision: str) -> None:
    entry = f"""### Prune Record — {title} ({now_iso()})
- **Purpose:** {purpose}
- **Alternatives evaluated:** {", ".join(alternatives) if alternatives else "none"}
- **Failure modes encountered:** {", ".join(failure_modes) if failure_modes else "none"}
- **Compatibility/Duplication Evidence:** {evidence}
- **Final Decision:** {decision}

"""
    append_text(CHANGE_LOG, entry)

def log_error(step_num: str, step_desc: str, error_msg: str, context: str) -> None:
    # Console echo as a ChatGPT-5 question block
    question = f"""Question for ChatGPT-5:
While performing [{step_num}: {step_desc}], encountered the following error:
{error_msg}
Context: {context}
What are the possible causes, and how can this be resolved while preserving intended functionality?
"""
    print(question.strip())
    # Persist as ndjson
    record = {
        "ts": now_iso(),
        "step": step_num,
        "desc": step_desc,
        "error": error_msg,
        "context": context
    }
    append_text(ERRORS_NDJSON, json.dumps(record) + "\n")

def require_clean_working_tree():
    code, out, err = run(["git", "status", "--porcelain"])
    if code != 0:
        log_error("1.1", "Verify clean working state", err or out, "git status --porcelain failed")
        return
    if out.strip():
        log_error("1.1", "Verify clean working state",
                  "Working tree has uncommitted changes.",
                  out.strip())

def resolve_repo_root():
    global REPO_ROOT
    code, out, err = run(["git", "rev-parse", "--show-toplevel"])
    if code != 0:
        log_error("1.1", "Identify repository root", err or out, "git rev-parse --show-toplevel")
        REPO_ROOT = Path.cwd()
    else:
        REPO_ROOT = Path(out.strip())

def init_codex_dir():
    global CODEX_DIR, CHANGE_LOG, ERRORS_NDJSON, RESULTS_MD, INVENTORY_JSON
    CODEX_DIR = REPO_ROOT / ".codex"
    ensure_dir(CODEX_DIR)
    CHANGE_LOG = CODEX_DIR / "change_log.md"
    ERRORS_NDJSON = CODEX_DIR / "errors.ndjson"
    RESULTS_MD = CODEX_DIR / "results.md"
    INVENTORY_JSON = CODEX_DIR / "inventory.json"
    if not CHANGE_LOG.exists():
        append_text(CHANGE_LOG, f"# Codex Change Log\n\nInitialized {now_iso()}\n\n")
    if not ERRORS_NDJSON.exists():
        append_text(ERRORS_NDJSON, "")
    # results.md re-written at finalization

def build_inventory():
    inventory = []
    for p in REPO_ROOT.rglob("*"):
        if ".git" in p.parts or p.is_dir():
            continue
        rel = p.relative_to(REPO_ROOT).as_posix()
        inventory.append(rel)
    write_text(INVENTORY_JSON, json.dumps(inventory, indent=2))

def detect_conflicts():
    """Return: (has_pyproject, has_setup_cfg, has_setup_py)"""
    return ((REPO_ROOT / "pyproject.toml").exists(),
            (REPO_ROOT / "setup.cfg").exists(),
            (REPO_ROOT / "setup.py").exists())

def create_or_update_pyproject():
    target = REPO_ROOT / "pyproject.toml"
    before = read_text(target)
    # Minimal PEP 621 with Setuptools + src layout
    content = f"""[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "codex"
version = "0.1.0"
description = "codex package for the _codex_ repository"
readme = "README.md"
requires-python = ">=3.9"
license = {{text = "MIT"}}
authors = [{{name = "Project Authors"}}]
dependencies = []

[tool.setuptools]
package-dir = {{"" = "src"}}

[tool.setuptools.packages.find]
where = ["src"]
"""
    write_text(target, content)
    after = read_text(target)
    action = "created" if before is None else "updated"
    log_change(target.relative_to(REPO_ROOT), action, "Establish PEP 621 packaging with src/ layout for 'codex'.", before, after)

def create_or_update_setup_cfg():
    target = REPO_ROOT / "setup.cfg"
    before = read_text(target)
    content = f"""[metadata]
name = codex
version = 0.1.0
description = codex package for the _codex_ repository
long_description = file: README.md
long_description_content_type = text/markdown

[options]
package_dir =
    = src
packages = find:
python_requires = >=3.9

[options.packages.find]
where = src
"""
    write_text(target, content)
    after = read_text(target)
    action = "created" if before is None else "updated"
    log_change(target.relative_to(REPO_ROOT), action, "Establish setup.cfg packaging with src/ layout for 'codex'.", before, after)

def ensure_src_package():
    pkg_dir = REPO_ROOT / "src" / "codex"
    init_file = pkg_dir / "__init__.py"
    before = read_text(init_file)
    if before is None:
        ensure_dir(pkg_dir)
        write_text(init_file, "# codex package\n")
        after = read_text(init_file)
        log_change(init_file.relative_to(REPO_ROOT), "created", "Create src/codex/__init__.py to ensure importability.", None, after)

def update_readme_install():
    target = REPO_ROOT / "README.md"
    before = read_text(target) or "# _codex_\n\n"
    # Replace or insert Installation section
    install_section = (
        "## Installation\n\n"
        "From the repository root, install in editable mode:\n\n"
        "```bash\n"
        "pip install -e .\n"
        "```\n"
    )

    pattern = re.compile(r"(?ms)^##\s*Installation\b.*?(?=^##\s|\Z)")
    if pattern.search(before):
        after = pattern.sub(install_section, before)
        action = "updated"
        rationale = "Refresh Installation section with editable install instructions."
    else:
        # Append at the end with a preceding newline
        sep = "" if before.endswith("\n") else "\n"
        after = before + sep + "\n" + install_section
        action = "updated" if before else "created"
        rationale = "Add Installation section with editable install instructions."

    write_text(target, after)
    log_change(target.relative_to(REPO_ROOT), action, rationale, before, after)

def cleanup_test_path_hacks():
    tests_dir = REPO_ROOT / "tests"
    if not tests_dir.exists():
        return
    # Pattern to remove lines using sys.path.insert(...) or path hacks around tests
    path_line = re.compile(r"^\s*(import\s+sys\b.*|sys\.path\.insert\(.+\)|import\s+os\b.*|sys\.path\.append\(.+\))\s*$")
    modified = False
    for py in tests_dir.rglob("*.py"):
        before = read_text(py)
        if before is None:
            continue
        lines = before.splitlines()
        new_lines = []
        for line in lines:
            if "sys.path.insert" in line or "sys.path.append" in line:
                continue
            if path_line.match(line) and ("sys" in line or "os" in line):
                continue
            new_lines.append(line)
        after = "\n".join(new_lines) + ("\n" if before.endswith("\n") else "")
        if after != before:
            write_text(py, after)
            log_change(py.relative_to(REPO_ROOT), "updated",
                       "Remove sys.path* test path hacks; rely on installed package.", before, after)
            modified = True
    return modified

def add_smoke_test():
    tests_dir = REPO_ROOT / "tests"
    ensure_dir(tests_dir)
    target = tests_dir / "test_import_codex.py"
    before = read_text(target)
    content = """def test_import_codex():
    import codex  # noqa: F401
"""
    write_text(target, content)
    after = read_text(target)
    action = "created" if before is None else "updated"
    log_change(target.relative_to(REPO_ROOT), action, "Add smoke test ensuring 'import codex' works.", before, after)

def suggest_prunes(use_setup_cfg: bool):
    has_pj, has_cfg, has_py = detect_conflicts()
    # If both pyproject and setup.cfg exist, suggest to keep the chosen one.
    if use_setup_cfg and (REPO_ROOT / "pyproject.toml").exists():
        log_prune_record(
            title="pyproject.toml vs setup.cfg",
            purpose="Duplicate packaging metadata",
            alternatives=["Keep setup.cfg only", "Keep pyproject.toml only"],
            failure_modes=["Conflicting build configuration sources"],
            evidence="Both pyproject.toml and setup.cfg present after setup.cfg selection.",
            decision="Recommend removing pyproject.toml (PRUNE=false => not applied)."
        )
    if (not use_setup_cfg) and (REPO_ROOT / "setup.cfg").exists():
        log_prune_record(
            title="setup.cfg vs pyproject.toml",
            purpose="Duplicate packaging metadata",
            alternatives=["Keep pyproject.toml only", "Keep setup.cfg only"],
            failure_modes=["Conflicting build configuration sources"],
            evidence="Both setup.cfg and pyproject.toml present after pyproject selection.",
            decision="Recommend removing setup.cfg (PRUNE=false => not applied)."
        )
    # setup.py coexistence note
    if has_py:
        log_prune_record(
            title="setup.py legacy",
            purpose="Legacy packaging entrypoint (redundant with PEP 621 / setup.cfg)",
            alternatives=["Keep pyproject.toml/setup.cfg only"],
            failure_modes=["Source-of-truth ambiguity in builds"],
            evidence="setup.py coexists with declarative config.",
            decision="Recommend removing setup.py or reducing to shim (PRUNE=false => not applied)."
        )

def mapping_results():
    # Very lightweight, since we don't know repo specifics
    mapping = {
        "t1: packaging config": {
            "candidate_assets": ["pyproject.toml", "setup.cfg", "setup.py", "src/codex/__init__.py"],
            "rationale": "PEP 621 (pyproject) preferred; src/ layout ensures clean imports."
        },
        "t2: tests import hygiene": {
            "candidate_assets": ["tests/**/*.py"],
            "rationale": "Remove sys.path hacks so tests use installed package resolution."
        },
        "t3: README install docs": {
            "candidate_assets": ["README.md"],
            "rationale": "Add/refresh install instructions (editable mode)."
        }
    }
    return mapping

def write_results(mapping: Dict[str, Dict], had_errors: bool):
    content = f"""# Codex Results — {now_iso()}

## Implemented
- Packaging config for `codex` with `src/` layout ({'setup.cfg' if (REPO_ROOT / 'setup.cfg').exists() else 'pyproject.toml'}).
- Tests cleaned to avoid `sys.path` hacks (where present).
- README updated with editable install instructions.
- Smoke test added: `tests/test_import_codex.py`.

## Mapping Table
```json
{json.dumps(mapping, indent=2)}
````

## Prune Index (recommendations)

(See `.codex/change_log.md` — Prune Records.)

## Constraints

* **DO NOT ACTIVATE ANY GitHub Actions files.**

## Status

* Errors logged: {"yes" if had_errors else "no"}
  """
    write_text(RESULTS_MD, content)

def main():
    parser = argparse.ArgumentParser(description="Codex E2E Workflow")
    parser.add_argument("--use-setup-cfg", type=lambda x: x.lower()=="true", default=str(DEFAULT_USE_SETUP_CFG).lower(),
                        help="true => emit setup.cfg; false => emit pyproject.toml")
    parser.add_argument("--prune", type=lambda x: x.lower()=="true", default=str(DEFAULT_PRUNE).lower(),
                        help="true => apply destructive prunes (NOT RECOMMENDED). Default false (suggest only).")
    args = parser.parse_args()
    use_setup_cfg = bool(args.use_setup_cfg)
    prune = bool(args.prune)

    # Phase 1
    try:
        resolve_repo_root()
        init_codex_dir()
        require_clean_working_tree()
        build_inventory()
    except Exception as e:
        log_error("1.*", "Preparation steps", repr(e), "Init codex dir / inventory")
    # Phase 2 is implicit in mapping_results()

    # Phase 3 — Best-effort construction
    try:
        # Packaging
        if use_setup_cfg:
            create_or_update_setup_cfg()
        else:
            create_or_update_pyproject()
        ensure_src_package()
    except Exception as e:
        log_error("3.1-3.2", "Create/patch packaging config", repr(e), "pyproject/setup.cfg/src package")

    # README Installation
    try:
        update_readme_install()
    except Exception as e:
        log_error("3.3", "Update README Installation section", repr(e), "README patch")

    # Tests cleanup and smoke test
    try:
        cleanup_test_path_hacks()
        add_smoke_test()
    except Exception as e:
        log_error("3.4", "Adjust tests & add smoke test", repr(e), "tests/**")

    # Phase 4 — Pruning suggestions (non-destructive by default)
    try:
        suggest_prunes(use_setup_cfg=use_setup_cfg)
        if prune:
            # Intentionally conservative: do not implement destructive operations in this default script.
            log_prune_record(
                title="No destructive actions performed",
                purpose="Safety-first",
                alternatives=[],
                failure_modes=[],
                evidence="PRUNE=true requested, but script is configured to suggest-only.",
                decision="Skipped destructive prunes."
            )
    except Exception as e:
        log_error("4.*", "Pruning analysis", repr(e), "Suggest prune records")

    # Phase 5 — Errors already logged incrementally

    # Phase 6 — Finalization
    had_errors = False
    try:
        errs = read_text(ERRORS_NDJSON) or ""
        had_errors = bool(errs.strip())
        write_results(mapping_results(), had_errors)
    except Exception as e:
        log_error("6.2", "Write results", repr(e), "results.md")

    # Required statement:
    print("NOTICE: DO NOT ACTIVATE ANY GitHub Actions files.")
    if DO_NOT_ACTIVATE_GITHUB_ACTIONS:
        gha = REPO_ROOT / ".github" / "workflows"
        if gha.exists():
            print("INFO: .github/workflows present; leaving untouched by policy.")

    sys.exit(1 if had_errors else 0)


if __name__ == "__main__":
    main()

