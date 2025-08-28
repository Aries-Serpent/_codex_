#!/usr/bin/env python
"""
End-to-end Codex workflow:
- README parsing + reference cleanup
- File search & light adaptation attempt (placeholder)
- Run audit, pre-commit, tests
- Collect errors as ChatGPT-5 questions
NOTE: Does NOT enable any GitHub Actions.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
import time

__all__ = ["main"]

ROOT = pathlib.Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)


def run(
    cmd: list[str], capture: bool = False, env: dict[str, str] | None = None
) -> tuple[int, str]:
    try:
        if capture:
            out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT, env=env)
            return 0, out
        ret = subprocess.call(cmd, env=env)
        return ret, ""
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output
    except FileNotFoundError as e:
        return 127, str(e)


def parse_readme() -> None:
    readme = ROOT / "README.md"
    if not readme.exists():
        return
    txt = readme.read_text(encoding="utf-8", errors="ignore")
    txt2 = re.sub(
        r"https?://raw\.githubusercontent\.com/\S+", "[[REQUIRES-OFFLINE-ALTERNATIVE]]", txt
    )
    if txt2 != txt:
        (ART / "README.cleaned.md").write_text(txt2, encoding="utf-8")


def light_file_search() -> None:
    srcs = list(ROOT.rglob("*.py"))
    (ART / "FILE_LIST.json").write_text(
        json.dumps([str(s.relative_to(ROOT)) for s in srcs], indent=2)
    )


def error_capture(phase_step: str, err: str, ctx: str) -> None:
    ts = time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime())
    block = (
        f"Question for ChatGPT-5 {ts}:\n"
        f"While performing {phase_step}, encountered the following error:\n"
        f"{err.strip()}\n"
        f"Context: {ctx}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
    )
    log = ART / "ERRORS.log"
    with log.open("a", encoding="utf-8") as f:
        f.write(block + "\n")
    print(block, file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--prefer-cli", action="store_true", help="prefer external chatgpt-codex if present"
    )
    args = ap.parse_args(argv)

    try:
        parse_readme()
        light_file_search()

        rc, out = run(
            ["python", "tools/audit_runner.py", "--prompt-file", "AUDIT_PROMPT.md"]
            + (["--prefer-cli"] if args.prefer_cli else [])
        )
        if rc != 0:
            error_capture("STEP 1 (audit)", out or "non-zero exit", "Running portable audit runner")

        rc, out = run(["python", "tools/run_precommit.py"])
        if rc != 0:
            error_capture(
                "STEP 2 (pre-commit)",
                out or "non-zero exit",
                "Verbose run with timeout and cache-clean",
            )

        rc, out = run(["python", "tools/run_tests.py"])
        if rc != 0:
            error_capture("STEP 3 (tests)", out or "non-zero exit", "pytest with optional coverage")
        return 0
    except Exception as e:  # pragma: no cover - safety net
        error_capture("WORKFLOW (unexpected)", repr(e), "codex_workflow guard")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
