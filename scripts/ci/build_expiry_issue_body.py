#!/usr/bin/env python3
"""Build the issue body for token-expiry-monitor.yml and print to stdout.

Reads URGENT_DETAILS env var (format: "TOKEN_NAME=days_left;TOKEN_NAME2=days_left2").
"""
from __future__ import annotations

import os
import sys


def main() -> None:
    details = os.environ.get("URGENT_DETAILS", "")
    rows: list[str] = []
    for item in details.split(";"):
        item = item.strip()
        if "=" not in item:
            continue
        name, days_str = item.split("=", 1)
        try:
            days_int = int(days_str.strip())
        except ValueError:
            continue
        status = "EXPIRED" if days_int < 0 else f"expires in {days_int}d"
        rows.append(f"| `{name.strip()}` | {status} |")

    table = "\n".join(rows) if rows else "| (see workflow log) | urgent |"

    body = "\n".join([
        "## PAT Expiry Alert",
        "",
        "One or more personal access tokens (PATs) are near expiry or have expired.",
        "",
        "| Token | Status |",
        "|-------|--------|",
        table,
        "",
        "**Rotation guide:** `docs/reference/ELEVATED_PRIVILEGES_TOKEN_REVIEW.md` §9 (7-step playbook)",
        "",
        "**Quick links:**",
        "- [CODEX_MASTER_KEY](https://github.com/organizations/Aries-Serpent/settings/secrets/actions/CODEX_MASTER_KEY)",
        "- [CODEX_BACKUP_KEY](https://github.com/organizations/Aries-Serpent/settings/secrets/actions/CODEX_BACKUP_KEY)",
        "",
        "_Auto-created by token-expiry-monitor.yml_",
    ])
    sys.stdout.write(body + "\n")


if __name__ == "__main__":
    main()
