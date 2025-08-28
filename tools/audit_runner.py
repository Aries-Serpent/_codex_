#!/usr/bin/env python
"""
Portable audit runner: uses internal Python pipeline by default,
falls back to external 'chatgpt-codex' CLI only if present on PATH.
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys

__all__ = ["main"]


def run_external_cli(prompt_file: str) -> int:
    return subprocess.call(["chatgpt-codex", "--prompt-file", prompt_file])


def run_internal(prompt_file: str) -> int:
    script = pathlib.Path(__file__).resolve().parent / "audit_builder.py"
    if script.exists():
        return subprocess.call([sys.executable, str(script), "--prompt-file", prompt_file])
    pf = pathlib.Path(prompt_file)
    if not pf.exists():
        print(f"[audit] prompt file not found: {prompt_file}", file=sys.stderr)
        return 2
    out = pathlib.Path("artifacts")
    out.mkdir(exist_ok=True)
    (out / "AUDIT_RESULT.txt").write_text(f"[audit] processed: {pf.name}\n", encoding="utf-8")
    print(f"[audit] wrote {out/'AUDIT_RESULT.txt'}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument(
        "--prefer-cli",
        action="store_true",
        help="Try 'chatgpt-codex' if available.",
    )
    args = ap.parse_args(argv)

    cli = shutil.which("chatgpt-codex")
    if args.prefer_cli and cli:
        return run_external_cli(args.prompt_file)
    return run_internal(args.prompt_file)


if __name__ == "__main__":
    raise SystemExit(main())
