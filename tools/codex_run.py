#!/usr/bin/env python
"""Codex offline runner: audit -> pre-commit -> tests.
   Avoids network/CI, provides fallback when external CLI missing."""
from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Tuple, List

OK, WARN, FAIL = 0, 1, 2

def run(cmd: List[str], *, cwd: Path | None = None, timeout: int | None = None, env: dict | None = None, log: Path | None = None) -> Tuple[int, str]:
    proc = subprocess.Popen(cmd, cwd=str(cwd) if cwd else None,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            env=env or os.environ.copy(), text=True)
    try:
        out, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        out = f"[TIMEOUT] {' '.join(map(shlex.quote, cmd))} exceeded {timeout}s\n"
        rc = 124
    else:
        rc = proc.returncode
    if log:
        log.parent.mkdir(parents=True, exist_ok=True)
        with open(log, "a", encoding="utf-8") as fh:
            fh.write(out)
    return rc, out

def rewrite_readme_cli(readme: Path) -> Tuple[bool, str]:
    if not readme.exists():
        return False, "README not found; skipped"
    text = readme.read_text(encoding="utf-8", errors="ignore")
    new_text = re.sub(r"(^|\s)chatgpt-codex(\s+)", r"\1python tools/audit_builder.py\2", text)
    if new_text != text:
        readme.write_text(new_text, encoding="utf-8")
        return True, "normalized CLI references"
    return False, "no changes"

def run_audit(prompt: Path, artifacts: Path) -> Tuple[int, str]:
    artifacts.mkdir(parents=True, exist_ok=True)
    if Path("tools/audit_builder.py").exists():
        rc, out = run([sys.executable, "tools/audit_builder.py", "--prompt-file", str(prompt)], log=artifacts/"audit.log")
        if rc == 0:
            (artifacts/"audit.md").write_text(out, encoding="utf-8")
            return OK, "audit generated"
        return FAIL, "audit script failed"
    return WARN, "audit script missing"

def precommit_run(timeout: int, artifacts: Path, skip_hooks: str | None = None) -> Tuple[int, str]:
    env = os.environ.copy()
    if skip_hooks:
        env["SKIP"] = skip_hooks
    cmd = ["pre-commit", "run", "--all-files", "--verbose"]
    rc, _ = run(cmd, timeout=timeout, env=env, log=artifacts/"precommit.log")
    if rc == 124:
        return WARN, "pre-commit timed out"
    if rc != 0:
        run(["pre-commit", "clean"], env=env, log=artifacts/"precommit.log")
        rc2, _ = run(cmd, timeout=timeout, env=env, log=artifacts/"precommit.log")
        if rc2 != 0:
            return FAIL, "pre-commit failed"
    return OK, "pre-commit passed"

def has_pytest_cov() -> bool:
    rc, out = run(["pytest", "--version"])
    return "pytest-cov" in out

def run_tests(cov_target: str, cov_threshold: int, artifacts: Path) -> Tuple[int, str]:
    if has_pytest_cov():
        cmd = ["pytest", f"--cov={cov_target}", "--cov-report=term", f"--cov-fail-under={cov_threshold}"]
        rc, out = run(cmd, log=artifacts/"tests.log")
        if rc != 0:
            return FAIL, "tests or coverage failed"
        return OK, "tests with coverage passed"
    rc, _ = run(["pytest", "-q"], log=artifacts/"tests.log")
    if rc != 0:
        return FAIL, "tests failed"
    return WARN, "tests passed without coverage"

def append_changelog(msgs: List[str]) -> None:
    path = Path("CHANGELOG_codex.md")
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = [f"## {stamp} – Codex run"] + [f"- {m}" for m in msgs]
    previous = path.read_text(encoding="utf-8") if path.exists() else ""
    path.write_text((previous + ("\n" if previous else "") + "\n".join(entry) + "\n"), encoding="utf-8")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt-file", default="AUDIT_PROMPT.md")
    ap.add_argument("--readme", default="README.md")
    ap.add_argument("--artifacts", default="ARTIFACTS")
    ap.add_argument("--precommit-timeout", type=int, default=120)
    ap.add_argument("--skip-hooks", default=os.environ.get("SKIP"))
    ap.add_argument("--cov-target", default="src")
    ap.add_argument("--cov-threshold", type=int, default=70)
    args = ap.parse_args()

    artifacts = Path(args.artifacts)
    msgs: List[str] = []

    changed, note = rewrite_readme_cli(Path(args.readme))
    msgs.append(f"README rewrite: {note}")

    rc_audit, note = run_audit(Path(args.prompt_file), artifacts)
    msgs.append(f"Audit: {note}")

    rc_pc, note = precommit_run(args.precommit_timeout, artifacts, args.skip_hooks)
    msgs.append(f"pre-commit: {note}")

    rc_tests, note = run_tests(args.cov_target, args.cov_threshold, artifacts)
    msgs.append(f"tests: {note}")

    append_changelog(msgs)

    status = max(rc_audit, rc_pc, rc_tests)
    for m in msgs:
        print(m)
    return 0 if status == OK else (1 if status == WARN else 2)

if __name__ == "__main__":
    raise SystemExit(main())
