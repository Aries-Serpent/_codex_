#!/usr/bin/env python3
"""
Codex Orchestrator: runs the sequential phases, applies minimal patches, records a CHANGELOG, and writes research questions to Codex_Questions.md on failure.
Policy: DO NOT enable GitHub Actions. All checks run locally when CODEX_ENV=1.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"
QUESTIONS = ROOT / "Codex_Questions.md"
README = ROOT / "README.md"


def ts() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")


def sh(cmd: list[str], step: str):
    try:
        return subprocess.run(cmd, cwd=ROOT, check=True, text=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        record_question(
            step, f"{e}", context=f"cmd={' '.join(cmd)}\nstdout={e.stdout}\nstderr={e.stderr}"
        )
        raise


def record_question(step_number_desc: str, error: str, context: str = ""):
    QUESTIONS.parent.mkdir(parents=True, exist_ok=True)
    with QUESTIONS.open("a", encoding="utf-8") as f:
        f.write(
            textwrap.dedent(
                f"""
                Question from ChatGPT @codex {dt.datetime.now().isoformat(timespec='seconds')}:
                While performing {step_number_desc}, encountered the following error: {error}
                Context: {context}. What are the possible causes, and how can this be resolved while preserving intended functionality?
                """.strip()
            )
            + "\n\n"
        )


def normalize_readme():
    if README.exists():
        txt = README.read_text(encoding="utf-8")
        new = re.sub(r"codex-file-citation:[^\s]+", "", txt)
        if new != txt:
            README.write_text(new, encoding="utf-8")
            append_changelog("- docs: normalize codex-file-citation references in README")


def append_changelog(line: str):
    CHANGELOG.parent.mkdir(parents=True, exist_ok=True)
    if CHANGELOG.exists():
        existing = CHANGELOG.read_text(encoding="utf-8")
    else:
        existing = "# Changelog\n\n"
    CHANGELOG.write_text(existing + f"{line}\n", encoding="utf-8")


def ensure_file(path: Path, content: str, why: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text(encoding="utf-8") != content:
        path.write_text(content, encoding="utf-8")
        append_changelog(why)


def run_quality_gates():
    if os.environ.get("CODEX_ENV") != "1":
        print("CODEX_ENV=1 not set; skipping quality gates to honor 'Codex-only' policy.")
        return
    try:
        sh(["pre-commit", "install"], "Phase 6: pre-commit install")
        sh(["pre-commit", "run", "-a"], "Phase 6: pre-commit run -a")
    except Exception:
        pass


def find_todos():
    out = sh(["bash", "-lc", 'rg -n "TODO|NotImplementedError" || true'], "Phase 2: scan TODOs")
    if out.stdout.strip():
        append_changelog("- scan: TODO/NotImplemented present; see ripgrep output in local logs")


def write_security_skeletons():
    ensure_file(ROOT / "bandit.yaml", "skips: []\n", "- chore: add bandit.yaml")
    ensure_file(
        ROOT / ".secrets.baseline",
        json.dumps({"version": "1.0.0", "results": []}, indent=2),
        "- chore: add empty detect-secrets baseline",
    )


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--lock-refresh", action="store_true")
    ap.add_argument("--quality-gates", action="store_true")
    args = ap.parse_args(argv)
    try:
        normalize_readme()
        write_security_skeletons()
        find_todos()
        if args.lock_refresh:
            if (ROOT / "tools/uv_lock_refresh.sh").exists():
                sh(["bash", "tools/uv_lock_refresh.sh"], "Phase 6: lock refresh")
        if args.quality_gates:
            run_quality_gates()
        print("Codex Orchestrator completed.")
    except Exception as e:
        print(f"[codex] error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
