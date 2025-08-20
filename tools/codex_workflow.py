#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
_codex_ / 0B_base_ — End-to-End Workflow Executor
- Best-effort construction before pruning
- Pre-commit local pytest hook, mypy files include tests/
- Coverage script creation + README Testing docs
- Error capture as ChatGPT-5 research questions
- No GitHub Actions activation

Run from repo root: python3 tools/codex_workflow.py
"""

import os, sys, re, json, stat, difflib, subprocess, shutil
from datetime import datetime
from pathlib import Path

# ---------- Utilities ----------

def repo_root() -> Path:
    try:
        out = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
        return Path(out)
    except Exception as e:
        print_q5(step="1.1: Identify repo root",
                 err=str(e),
                 ctx="Ensure this script runs inside a Git repository.")
        sys.exit(2)

def git_clean(root: Path) -> bool:
    try:
        out = subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True)
        return out.strip() == ""
    except Exception as e:
        log_error(step="1.1", desc="Check git clean state", err=str(e), ctx="git status --porcelain failed")
        return False

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""

def write_text(p: Path, content: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

def chmod_x(p: Path):
    m = p.stat().st_mode
    p.chmod(m | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

def run_cmd(cmd, cwd, step_desc):
    try:
        proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError as e:
        log_error(step="3.4", desc=f"Run {' '.join(cmd)}", err=str(e),
                  ctx=f"{step_desc} (Is '{cmd[0]}' installed?)")
        return 127, "", str(e)
    except Exception as e:
        log_error(step="3.4", desc=f"Run {' '.join(cmd)}", err=str(e),
                  ctx=step_desc)
        return 1, "", str(e)

# ---------- Logging ----------

CODEx = None
CHANGE_LOG = None
ERRORS = None
RESULTS = None
INVENTORY = None
ERROR_COUNT = 0

def init_logs(root: Path):
    global CODEx, CHANGE_LOG, ERRORS, RESULTS, INVENTORY
    CODEx = root / ".codex"
    ensure_dir(CODEx)
    CHANGE_LOG = CODEx / "change_log.md"
    ERRORS = CODEx / "errors.ndjson"
    RESULTS = CODEx / "results.md"
    INVENTORY = CODEx / "inventory.json"
    for p in (CHANGE_LOG, ERRORS, RESULTS):
        if not p.exists():
            write_text(p, "")

def now_iso():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def append_change(file: Path, action: str, rationale: str, before: str, after: str):
    hdr = f"### {now_iso()} — {file}\n- **Action:** {action}\n- **Rationale:** {rationale}\n"
    diff = "\n".join(difflib.unified_diff(
        before.splitlines(), after.splitlines(),
        fromfile=f"{file} (before)", tofile=f"{file} (after)", lineterm=""
    ))
    write_text(CHANGE_LOG, read_text(CHANGE_LOG) + hdr + "```diff\n" + diff + "\n```\n\n")

def log_error(step: str, desc: str, err: str, ctx: str):
    global ERROR_COUNT
    ERROR_COUNT += 1
    rec = {
        "ts": now_iso(),
        "step": step,
        "description": desc,
        "error": err,
        "context": ctx
    }
    with ERRORS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print_q5(step=f"{step}: {desc}", err=err, ctx=ctx)

def print_q5(step: str, err: str, ctx: str):
    msg = (
        "Question for ChatGPT-5:\n"
        f"While performing [{step}], encountered the following error:\n"
        f"{err}\n"
        f"Context: {ctx}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
    )
    sys.stderr.write(msg + "\n")

# ---------- Phase 1: Prep ----------

def build_inventory(root: Path):
    items = []
    for p in root.rglob("*"):
        if p.is_file() and ".git" not in p.parts and ".venv" not in p.parts and p.name != "codex_workflow.py":
            role = "code" if p.suffix in {".py",".sh",".js",".ts",".tsx",".jsx",".sql"} else \
                   "doc" if p.suffix.lower() in {".md",".rst"} else \
                   "config" if "pre-commit" in p.name or p.suffix in {".yml",".yaml",".toml",".ini"} else \
                   "asset"
            items.append({"path": str(p.relative_to(root)), "ext": p.suffix, "role": role})
    write_text(INVENTORY, json.dumps(items, indent=2))

# ---------- Phase 2/3: Construction ----------

PRE_COMMIT_HEADER = "# --- Added/ensured by codex_workflow.py ---"

LOCAL_PYTEST_BLOCK = """\
- repo: local
  hooks:
    - id: local-pytest
      name: local-pytest
      entry: pytest -q
      language: system
      pass_filenames: false
"""

MIRRORS_MYPY_BLOCK = """\
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.10.0  # pin or adjust as appropriate
  hooks:
    - id: mypy
      additional_dependencies: []
      files: '^(src|tests)/'
"""

def ensure_precommit_config(root: Path) -> Path:
    cfg = root / ".pre-commit-config.yaml"
    if not cfg.exists():
        before = ""
        content = f"{PRE_COMMIT_HEADER}\nrepos:\n{indent_block(LOCAL_PYTEST_BLOCK, 2)}\n{indent_block(MIRRORS_MYPY_BLOCK, 2)}"
        write_text(cfg, content)
        append_change(cfg, "create", "Initialize minimal pre-commit config with local pytest and mypy hooks", before, content)
        return cfg

    before = read_text(cfg)
    content = before

    if "repos:" not in content:
        content = f"{content.rstrip()}\nrepos:\n"

    # Ensure local repo block
    if "repo: local" not in content:
        content = f"{content.rstrip()}\n{indent_block(LOCAL_PYTEST_BLOCK, 0)}"
    else:
        # Ensure local-pytest exists
        if "id: local-pytest" not in content:
            # Append the hook under existing local repo; simple heuristic append near end
            content = f"{content.rstrip()}\n  # ensure local pytest hook\n  hooks:\n    - id: local-pytest\n      name: local-pytest\n      entry: pytest -q\n      language: system\n      pass_filenames: false\n"

    # Ensure mypy block exists
    if "id: mypy" not in content:
        content = f"{content.rstrip()}\n{indent_block(MIRRORS_MYPY_BLOCK, 0)}"

    if content != before:
        write_text(cfg, content)
        append_change(cfg, "update", "Ensure repos: local pytest hook and mypy hook exist", before, content)

    return cfg

def ensure_mypy_files_include_tests(root: Path, cfg: Path):
    before = read_text(cfg)
    content = before

    # Find mypy hook and adjust files:
    # Pattern: a 'hooks' item with '- id: mypy' and an optional 'files:' immediately below or within that block.
    # Strategy: If a 'files:' for mypy exists but lacks 'tests', widen to ^(src|tests)/
    if "id: mypy" not in content:
        # Already ensured earlier; if still missing, log and return
        log_error(step="3.2", desc="Ensure mypy hook exists", err="mypy hook not found after ensure_precommit_config",
                  ctx=str(cfg))
        return

    # Update existing files: line
    def repl_files(match: re.Match) -> str:
        block = match.group(0)
        if re.search(r"^\s*files\s*:\s*['"]\^\(.*\)['"]", block, re.M):
            block2 = re.sub(r"^\s*files\s*:\s*['"]\^\((.*?)\)/['"]",
                            lambda m: f"      files: '^(src|tests)/'",
                            block, flags=re.M)
            return block2
        elif re.search(r"^\s*files\s*:\s*['\"][^'\"]+['\"]", block, re.M):
            # Any other files: pattern → replace with ^(src|tests)/
            block2 = re.sub(r"^\s*files\s*:\s*['\"][^'\"]+['\"]",
                            "      files: '^(src|tests)/'", block, flags=re.M)
            return block2
        else:
            # Insert files beneath id: mypy
            lines = block.splitlines()
            for i, line in enumerate(lines):
                if re.search(r"id:\s*mypy", line):
                    insert_at = i + 1
                    lines.insert(insert_at, "      files: '^(src|tests)/'")
                    break
            return "\n".join(lines)

    new_content = re.sub(
        r"(?ms)(^\s*-+\s*id:\s*mypy\b.*?(?=^\s*-+\s*id:|\Z))",
        repl_files,
        content
    )

    if new_content != before:
        write_text(cfg, new_content)
        append_change(cfg, "update", "Include tests/ in mypy files pattern", before, new_content)

def indent_block(block: str, spaces: int) -> str:
    pad = " " * spaces
    return "\n".join(pad + line if line.strip() else line for line in block.splitlines())

def ensure_scripts_and_coverage(root: Path):
    scripts = root / "scripts"
    ensure_dir(scripts)
    sh = scripts / "run_coverage.sh"
    before = read_text(sh)
    content = """#!/usr/bin/env bash
set -euo pipefail
# Coverage runner generated by codex_workflow.py
pytest --cov=src --cov-report=term-missing "$@"
"""
    if before != content:
        write_text(sh, content)
        chmod_x(sh)
        append_change(sh, "create" if not before else "update",
                      "Provide coverage runner for pytest coverage over src/",
                      before, content)

def update_readme_testing(root: Path):
    readme = root / "README.md"
    before = read_text(readme)
    testing_block = """
## Testing

### Quick checks
- Run pre-commit on config changes:
  ```bash
  pre-commit run --files .pre-commit-config.yaml
```

- Run pytest with coverage:

  ```bash
  scripts/run_coverage.sh
  ```

> **Note:** DO NOT ACTIVATE ANY GitHub Actions files. This repository intentionally avoids enabling `.github/workflows/*` in this workflow.
"""
    if "## Testing" in before:
        # Replace existing Testing section heuristically
        new = re.sub(r"(?ms)^## Testing\b.*?(?=^##|\Z)", testing_block + "\n", before)
    else:
        new = before.rstrip() + "\n\n" + testing_block + "\n"
    if new != before:
        write_text(readme, new)
        append_change(readme, "update", "Document coverage script and pre-commit usage; reiterate no GitHub Actions activation", before, new)

# ---------- Phase 3.4: Smoke run pre-commit ----------

def run_precommit_on_config(root: Path):
    step_desc = "Run pre-commit for .pre-commit-config.yaml"
    rc, out, err = run_cmd(["pre-commit", "run", "--files", ".pre-commit-config.yaml"], cwd=root, step_desc=step_desc)
    # Record output in results (informational)
    with RESULTS.open("a", encoding="utf-8") as f:
        f.write(f"### {now_iso()} pre-commit output\n`\n{out}\n`\n")
        if rc != 0:
            f.write(f"\n**pre-commit exit code:** {rc}\n`\n{err}\n`\n")
    return rc

# ---------- Phase 6: Results ----------

def write_results_summary(root: Path):
    content = []
    content.append(f"# Codex Results — {now_iso()}\n")
    content.append("## Implemented\n- Ensured `.pre-commit-config.yaml` includes a **local pytest** hook.\n- Ensured **mypy** hook includes `tests/` in `files`.\n- Created `scripts/run_coverage.sh` and made it executable.\n- Updated `README.md` Testing section with usage instructions.\n")
    content.append("## Residual Gaps\n- `pre-commit` and `pytest` must be installed in the environment.\n- Pin versions of hooks as needed for your org’s policy.\n")
    content.append("## Pruning\n- No assets pruned.\n")
    content.append("## Next Steps\n- Run `pre-commit install` (if not already) to enable local hooks.\n- Optionally add CI (but **DO NOT ACTIVATE ANY GitHub Actions files** in this workflow).\n")
    content.append("\n**DO NOT ACTIVATE ANY GitHub Actions files.**\n")
    write_text(RESULTS, "\n".join(content))

# ---------- Main ----------

def main():
    root = repo_root()
    init_logs(root)

    # Phase 1: Clean check
    if not git_clean(root):
        log_error(step="1.1", desc="Working tree not clean",
                  err="Uncommitted changes present",
                  ctx="Commit or stash changes before running this workflow.")
        # Continue (best-effort) but will exit non-zero at end

    # Phase 1.2/1.3: Read guardrails & inventory
    build_inventory(root)

    # Phase 2/3: Construct
    cfg = ensure_precommit_config(root)
    ensure_mypy_files_include_tests(root, cfg)
    ensure_scripts_and_coverage(root)
    update_readme_testing(root)

    # Phase 3.4: pre-commit smoke (best-effort)
    run_precommit_on_config(root)

    # Phase 6: Results
    write_results_summary(root)

    # Exit status
    if ERROR_COUNT > 0:
        sys.stderr.write(f"\nCompleted with {ERROR_COUNT} recorded error(s).\n")
        sys.exit(1)
    print("\nCompleted successfully with no recorded errors.")
    sys.exit(0)

if __name__ == "__main__":
    main()
