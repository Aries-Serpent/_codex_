#!/usr/bin/env python3
"""
github_var_writer.py — Systematic GitHub repository variable manager.

Reads a batch specification (JSON or CLI args) and creates/updates/deletes
repository variables via the GitHub Actions Variables REST API.

API docs:
  POST   /repos/{owner}/{repo}/actions/variables        — create
  PATCH  /repos/{owner}/{repo}/actions/variables/{name} — update
  DELETE /repos/{owner}/{repo}/actions/variables/{name} — delete
  GET    /repos/{owner}/{repo}/actions/variables        — list all

Required token scope:
  Fine-grained PAT with "Actions variables: write" — OR —
  Classic PAT with "repo" scope

Usage:
  # Apply a batch from a JSON file
  python scripts/ci/github_var_writer.py --batch .codex/pending_var_updates.json

  # Set a single variable
  python scripts/ci/github_var_writer.py --set MY_VAR=hello_world

  # Delete a variable
  python scripts/ci/github_var_writer.py --delete MY_VAR

  # List all variables (names + values)
  python scripts/ci/github_var_writer.py --list

  # Dry-run (print what would change, no API calls)
  python scripts/ci/github_var_writer.py --batch .codex/pending_var_updates.json --dry-run

Environment:
  CODEX_ADMIN_KEY    — PAT with variables:write (preferred)
  CODEX_MASTER_KEY   — fallback
  GITHUB_REPOSITORY  — defaults to Aries-Serpent/_codex_
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# ── Constants ────────────────────────────────────────────────────────────────

REPO = os.environ.get("GITHUB_REPOSITORY", "Aries-Serpent/_codex_")
BASE_URL = f"https://api.github.com/repos/{REPO}/actions/variables"
AUDIT_LOG = Path(".codex/evidence/var_write_audit.jsonl")

# Variables the agent is allowed to write autonomously (no extra approval).
# Extend this list to add new autonomous-writable variables.
ALLOWED_VAR_NAMES: set[str] = {
    "AUTONOMOUS_ACTIONS_ENABLED",
    "COGNITIVE_BRAIN_SESSION_NUMBER",
    "COGNITIVE_BRAIN_ALLOWED_ACTORS",
    "COPILOT_AGENT_AUTH_ENABLED",
    "AGENTIC_LOOP_ENABLED",
    "LAST_SESSION_ID",
    "LAST_AAIS_SCORE",
    "PHASE_11_STATUS",
    "WEBHOOK_RECEIVER_URL",
    "GITHUB_APP_ID",
    # Rate-limit cooldown variables (written by rate_limit_cooldown.py)
    "COPILOT_COOLDOWN_UNTIL_UTC",
    "COPILOT_RATE_LIMIT_HIT_COUNT",
    "COPILOT_LAST_SESSION_START_UTC",
    "COPILOT_SESSION_COOLDOWN_MINUTES",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _token() -> str:
    t = (
        os.environ.get("CODEX_ADMIN_KEY")
        or os.environ.get("CODEX_MASTER_KEY")
        or os.environ.get("CODEX_BACKUP_KEY", "")
    )
    if not t:
        print("ERROR: No auth token found. Set CODEX_ADMIN_KEY or CODEX_MASTER_KEY.", file=sys.stderr)
        sys.exit(1)
    return t


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_token()}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }


def _request(method: str, url: str, body: dict | None = None) -> tuple[int, dict]:
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    for k, v in _headers().items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors="replace")
        return e.code, {"error": msg}


def _audit(action: str, name: str, value: str | None, status: int, dry_run: bool) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "name": name,
        "value_len": len(value) if value else 0,
        "http_status": status,
        "dry_run": dry_run,
        "repo": REPO,
    }
    with AUDIT_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")


# ── Core operations ──────────────────────────────────────────────────────────

def list_vars() -> list[dict]:
    status, data = _request("GET", BASE_URL)
    if status != 200:
        print(f"ERROR listing variables: HTTP {status} — {data.get('error', '')}", file=sys.stderr)
        return []
    return data.get("variables", [])


def upsert_var(name: str, value: str, dry_run: bool = False, force: bool = False) -> bool:
    """Create or update a variable. Returns True on success."""
    if not force and name not in ALLOWED_VAR_NAMES:
        print(f"  BLOCKED  {name}  (not in ALLOWED_VAR_NAMES — pass --force to override)")
        return False

    if dry_run:
        print(f"  DRY-RUN  {name} = {value[:40]}{'...' if len(value) > 40 else ''}")
        return True

    # Try PATCH (update) first, fall back to POST (create)
    status, _resp = _request("PATCH", f"{BASE_URL}/{name}", {"value": value})
    if status == 404:
        status, _resp = _request("POST", BASE_URL, {"name": name, "value": value})

    ok = status in (201, 204)
    icon = "✅" if ok else "❌"
    print(f"  {icon}  {name} = {value[:40]}{'...' if len(value) > 40 else ''}  (HTTP {status})")
    _audit("upsert", name, value, status, dry_run)
    return ok


def delete_var(name: str, dry_run: bool = False, force: bool = False) -> bool:
    """Delete a variable. Returns True on success."""
    if not force and name not in ALLOWED_VAR_NAMES:
        print(f"  BLOCKED  {name}  (not in ALLOWED_VAR_NAMES — pass --force to override)")
        return False

    if dry_run:
        print(f"  DRY-RUN  DELETE {name}")
        return True

    status, _ = _request("DELETE", f"{BASE_URL}/{name}")
    ok = status == 204
    icon = "✅" if ok else "❌"
    print(f"  {icon}  DELETE {name}  (HTTP {status})")
    _audit("delete", name, None, status, dry_run)
    return ok


def apply_batch(batch_path: str, dry_run: bool = False, force: bool = False) -> int:
    """
    Apply a batch file. Supported formats:

    Simple dict  { "VAR_NAME": "value", ... }
    Operations   { "upsert": {"VAR": "val"}, "delete": ["VAR2"] }
    """
    path = Path(batch_path)
    if not path.exists():
        print(f"ERROR: Batch file not found: {batch_path}", file=sys.stderr)
        return 1

    data = json.loads(path.read_text())
    errors = 0

    # Detect format
    if "upsert" in data or "delete" in data:
        for name, value in (data.get("upsert") or {}).items():
            if not upsert_var(name, str(value), dry_run=dry_run, force=force):
                errors += 1
        for name in (data.get("delete") or []):
            if not delete_var(name, dry_run=dry_run, force=force):
                errors += 1
    else:
        # Simple dict: all keys are upserts
        for name, value in data.items():
            if not upsert_var(name, str(value), dry_run=dry_run, force=force):
                errors += 1

    return errors


# ── CLI ───────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Manage GitHub Actions repository variables via REST API."
    )
    parser.add_argument("--batch", metavar="FILE",
                        help="Apply a JSON batch file of variable upserts/deletes")
    parser.add_argument("--set", metavar="NAME=VALUE", dest="set_var",
                        help="Set a single variable")
    parser.add_argument("--delete", metavar="NAME", dest="delete_var",
                        help="Delete a single variable")
    parser.add_argument("--list", action="store_true",
                        help="List all repository variables")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would happen without making API calls")
    parser.add_argument("--force", action="store_true",
                        help="Bypass ALLOWED_VAR_NAMES check (use with caution)")
    args = parser.parse_args(argv)

    if args.list:
        variables = list_vars()
        if not variables:
            print("No variables found (or permission denied).")
            return 0
        print(f"{'NAME':<40} {'VALUE'}")
        print("-" * 70)
        for v in sorted(variables, key=lambda x: x["name"]):
            print(f"{v['name']:<40} {v.get('value', '')[:30]}")
        return 0

    if args.batch:
        print(f"Applying batch: {args.batch} (dry_run={args.dry_run})")
        return apply_batch(args.batch, dry_run=args.dry_run, force=args.force)

    if args.set_var:
        if "=" not in args.set_var:
            print("ERROR: --set requires NAME=VALUE format", file=sys.stderr)
            return 1
        name, _, value = args.set_var.partition("=")
        ok = upsert_var(name.strip(), value.strip(), dry_run=args.dry_run, force=args.force)
        return 0 if ok else 1

    if args.delete_var:
        ok = delete_var(args.delete_var.strip(), dry_run=args.dry_run, force=args.force)
        return 0 if ok else 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
