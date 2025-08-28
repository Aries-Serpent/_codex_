#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone


def ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser("audit_builder")
    ap.add_argument("--prompt-file", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=Path(".codex/audit.md"))
    args = ap.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    prompt = args.prompt_file.read_text(encoding="utf-8")
    args.out.write_text(f"# Audit ({ts()})\n\nPrompt:\n\n```\n{prompt}\n```\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
