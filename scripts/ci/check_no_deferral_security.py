#!/usr/bin/env python3
"""Enforce strict no-deferral security governance.

Rules:
- No deferral language is allowed in security status or PR artifacts.
- Every unresolved finding must be associated with an explicit owner and reason.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _ensure_owner_reason(block: str, label: str) -> list[str]:
    errors: list[str] = []
    if not re.search(r"\*\*Owner\*\*:\s*.+", block, re.IGNORECASE):
        errors.append(f"{label}: missing required '**Owner**:' classification")
    if not re.search(
        r"\*\*(?:Reason|Reason for Exception)\*\*:\s*.+",
        block,
        re.IGNORECASE,
    ):
        errors.append(f"{label}: missing required 'Reason' classification")
    return errors


def validate_exceptions(path: Path) -> list[str]:
    text = _read_text(path)
    errors: list[str] = []
    if "**Owner**:" not in text or "**Reason**:" not in text:
        errors.append(
            f"{path}: security exception policy requires explicit '**Owner**:' and '**Reason**:' fields"
        )

    blocks = re.split(r"(?=^###\s+)", text, flags=re.MULTILINE)
    for block in blocks:
        if "Exception ID:" not in block:
            continue
        status_match = re.search(r"\*\*Status\*\*:\s*(ACTIVE|OPEN|UNRESOLVED|PENDING)", block, re.IGNORECASE)
        if status_match:
            errors.extend(_ensure_owner_reason(block, f"{path}:{block.splitlines()[0].strip()}"))
    return errors


def validate_matrix(path: Path) -> list[str]:
    text = _read_text(path).lower()
    required_phrase = "all unresolved findings must list an owner and reason before merge"
    if required_phrase not in text:
        return [
            f"{path}: matrix must state that all unresolved findings must list an owner and reason before merge"
        ]
    return []


def _scan_for_out_of_scope_language(target: str | None) -> list[str]:
    if target is None:
        return []
    text = target.lower()
    patterns = [
        "out of scope",
        "outside the scope",
        "not related to this pr",
        "pre-existing issue",
        "will address in a future pr",
        "defer this to a future",
        "deferred to a later session",
        "not my responsibility",
    ]
    hits = [p for p in patterns if p in text]
    if hits:
        return [f"Deferral/out-of-scope language detected: {hits[0]}"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Enforce no-deferral security policy")
    parser.add_argument(
        "--paths",
        nargs="*",
        default=[
            "docs/security/security-exceptions.md",
            "docs/security-open-findings-matrix.md",
        ],
        help="Paths to validate",
    )
    parser.add_argument("--text", help="Optional raw text to scan for deferral language")
    args = parser.parse_args()

    errors: list[str] = []

    if args.text is not None:
        errors.extend(_scan_for_out_of_scope_language(args.text))

    for raw_path in args.paths:
        path = Path(raw_path)
        if not path.exists():
            errors.append(f"Missing required security policy file: {path}")
            continue
        if path.name == "security-exceptions.md":
            errors.extend(validate_exceptions(path))
        elif path.name == "security-open-findings-matrix.md":
            errors.extend(validate_matrix(path))

    if errors:
        print("Strict no-deferral security gate failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print("Strict no-deferral security gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
