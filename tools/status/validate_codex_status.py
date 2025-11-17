#!/usr/bin/env python3
"""
Minimal, stdlib-only validator for `_codex_` status JSON against v1.1 schema shape.
Use --schema {v1.1,v1.2,dual}. In dual mode, validate v1.1 first, then v1.2 if provided.
"""
import argparse
import json
import pathlib
import sys

REQUIRED_TOP = [
    "metadata",
    "snapshot",
    "delta",
    "patches",
    "automation",
    "security",
    "questions",
    "decisions",
]


def _err(msg: str) -> None:
    print(f"[validate] ERROR: {msg}", file=sys.stderr)


def _ok(msg: str) -> None:
    print(f"[validate] OK: {msg}")


def validate_v11(report: dict) -> bool:
    ok = True
    for k in REQUIRED_TOP:
        if k not in report:
            _err(f"Missing top-level key: {k}")
            ok = False
    meta = report.get("metadata", {})
    if meta.get("template_version") != "v1.1":
        _err("metadata.template_version must be 'v1.1'")
        ok = False
    if "title" not in meta or not isinstance(meta["title"], str):
        _err("metadata.title missing or not string")
        ok = False
    return ok


def validate_v12(report: dict) -> bool:
    # Accept v1.2 as additive superset of v1.1 for now.
    ok = True
    for k in REQUIRED_TOP:
        if k not in report:
            _err(f"[v1.2] Missing top-level key: {k}")
            ok = False
    meta = report.get("metadata", {})
    if meta.get("template_version") != "v1.2":
        _err("[v1.2] metadata.template_version must be 'v1.2'")
        ok = False
    if "title" not in meta or not isinstance(meta["title"], str):
        _err("[v1.2] metadata.title missing or not string")
        ok = False
    return ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", choices=["v1.1", "v1.2", "dual"], default="v1.1")
    ap.add_argument("report_json", type=pathlib.Path)
    args = ap.parse_args()
    data = json.loads(args.report_json.read_text(encoding="utf-8"))
    if args.schema == "v1.1":
        return 0 if validate_v11(data) else 2
    if args.schema == "v1.2":
        return 0 if validate_v12(data) else 2
    # dual
    v11 = (
        validate_v11(data) if data.get("metadata", {}).get("template_version") == "v1.1" else False
    )
    v12 = (
        validate_v12(data) if data.get("metadata", {}).get("template_version") == "v1.2" else False
    )
    if v11 or v12:
        _ok("dual validation succeeded")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
