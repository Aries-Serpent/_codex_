#!/usr/bin/env python
"""Tiny CLI wrapper for local _codex_ gates."""
import argparse
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(cmd: list[str]) -> int:
    print("$", " ".join(cmd))
    return subprocess.call(cmd)


def cmd_fences(_: argparse.Namespace) -> int:
    return run([sys.executable, os.path.join(REPO_ROOT, "tools", "validate_fences.py")])


def cmd_eval(args: argparse.Namespace) -> int:
    rules = args.rules or os.path.join(REPO_ROOT, "manifests", "codex_eval_rules.v3.json")
    inp = args.input or os.path.join(REPO_ROOT, "samples", "assistant_message_summary.sample.json")
    return run(
        [
            sys.executable,
            os.path.join(REPO_ROOT, "tools", "codex_evaluator.py"),
            "--rules",
            rules,
            "--input",
            inp,
        ]
    )


def cmd_gate(args: argparse.Namespace) -> int:
    rc = cmd_fences(args)
    if rc != 0:
        return rc
    return cmd_eval(args)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="codex-tools", description="Local gates for _codex_.")
    sub = p.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("fences", help="Run fence integrity checks")
    s1.set_defaults(func=cmd_fences)

    s2 = sub.add_parser("eval", help="Run Codex evaluator")
    s2.add_argument("--rules", default=None, help="Path to rules JSON")
    s2.add_argument("--input", default=None, help="Path to message or summary JSON")
    s2.set_defaults(func=cmd_eval)

    s3 = sub.add_parser("gate", help="Run both checks")
    s3.add_argument("--rules", default=None, help="Path to rules JSON")
    s3.add_argument("--input", default=None, help="Path to message or summary JSON")
    s3.set_defaults(func=cmd_gate)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
