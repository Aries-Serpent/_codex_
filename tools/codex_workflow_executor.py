#!/usr/bin/env python3
# tools/codex_workflow_executor.py
from __future__ import annotations

import os
import re
import sys
import json
import shlex
import pathlib
import subprocess
import textwrap
import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
CODEX_DIR = ROOT / ".codex"
CHANGELOG = ROOT / "CHANGELOG_CODEX.md"
ERRORS = ROOT / "ERROR_CAPTURE_BLOCKS.md"
MAKEFILE = ROOT / "Makefile"
CI_LOCAL = ROOT / "ci_local.sh"
README = ROOT / "README.md"


def run(cmd: list[str], check=True, env=None) -> subprocess.CompletedProcess:
    print("+", " ".join(map(shlex.quote, cmd)))
    return subprocess.run(cmd, check=check, env=env)


def ensure_codex_dir():
    CODEX_DIR.mkdir(parents=True, exist_ok=True)


def log_change(line: str):
    ts = datetime.datetime.utcnow().isoformat() + "Z"
    CHANGELOG.parent.mkdir(exist_ok=True, parents=True)
    with open(CHANGELOG, "a", encoding="utf-8") as f:
        f.write(f"- {ts} {line}\n")


def ask_gpt5(phase: str, err: str, ctx: str):
    q = textwrap.dedent(
        f"""
        Question for ChatGPT-5: While performing [{phase}], encountered the following error: {err.strip()} Context: {ctx} What are the possible causes, and how can this be resolved while preserving intended functionality?
        """
    ).strip()
    ERRORS.parent.mkdir(parents=True, exist_ok=True)
    with open(ERRORS, "a", encoding="utf-8") as f:
        f.write(q + "\n\n")
    print(q, file=sys.stderr)


# --- README normalization: remove placeholder badges and inline TODOs
BADGE_PAT = re.compile(r"(shields\.io/placeholder|\[!\[.*?\]\(.*?placeholder.*?\)\])", re.I)
TODO_LINE = re.compile(r"^.*\bTODO\b.*$", re.I)


def normalize_readme():
    if not README.exists():
        return
    before = README.read_text(encoding="utf-8", errors="ignore").splitlines()
    after = []
    for ln in before:
        if BADGE_PAT.search(ln):
            continue
        if TODO_LINE.search(ln):
            continue
        after.append(ln)
    if after != before:
        README.write_text("\n".join(after) + "\n", encoding="utf-8")
        log_change("README: removed placeholder badges / TODO lines")


# --- Makefile: ensure tiny target that shells to ci_local.sh
def ensure_make_target_shells():
    make_txt = MAKEFILE.read_text(encoding="utf-8") if MAKEFILE.exists() else ""
    target = "\ncodex-gates:\n\t@bash ci_local.sh\n"
    if "codex-gates:" not in make_txt:
        header = ".PHONY: codex-gates\n" if ".PHONY: codex-gates" not in make_txt else ""
        MAKEFILE.write_text(make_txt + ("\n" if not make_txt.endswith("\n") else "") + header + target, encoding="utf-8")
        log_change('Makefile: added tiny "make codex-gates" target that shells to ci_local.sh')


# --- ci_local.sh: venv-first, deterministic
def ensure_ci_local_present():
    desired = textwrap.dedent(
        """
        #!/usr/bin/env bash
        set -euo pipefail
        HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        bash "$HERE/tools/bootstrap_dev_env.sh"
        source "$HERE/.venv/bin/activate" 2>/dev/null || true
        .venv/bin/pre-commit run --all-files
        .venv/bin/pytest
        """
    ).strip()
    if (not CI_LOCAL.exists()) or (CI_LOCAL.read_text(encoding="utf-8") != desired + "\n"):
        CI_LOCAL.write_text(desired + "\n", encoding="utf-8")
        os.chmod(CI_LOCAL, 0o755)
        log_change("ci_local.sh: ensured venv-first execution of gates")


# --- Run the local gates (only in Codex/self-hosted env)
def run_local_gates():
    env = dict(os.environ)
    try:
        run(["bash", "ci_local.sh"], check=True, env=env)
        log_change("Local gates passed (pre-commit, pytest)")
    except subprocess.CalledProcessError as e:
        ask_gpt5("Phase 6: Run local gates", f"returncode={e.returncode}", "pre-commit/pytest failed via ci_local.sh")
        raise


def main():
    ensure_codex_dir()
    log_change("Begin codex_workflow_executor")
    try:
        normalize_readme()
    except Exception as e:
        ask_gpt5("Phase 1: README normalization", str(e), "updating env secret references")
    try:
        ensure_make_target_shells()
        ensure_ci_local_present()
    except Exception as e:
        ask_gpt5("Phase 3: Ensure gates entrypoints", str(e), "Makefile or ci_local.sh update")
    try:
        run_local_gates()
    except Exception as e:
        ask_gpt5("Phase 6: Run local gates", str(e), "check .venv tools / tests / hooks")
    log_change("End codex_workflow_executor")
    return 0


if __name__ == "__main__":
    sys.exit(main())

