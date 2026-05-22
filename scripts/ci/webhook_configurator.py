#!/usr/bin/env python3
"""
webhook_configurator.py — Programmatic GitHub repository webhook manager.

Creates, updates, lists, and deletes repository webhooks via the GitHub REST API.
Stores webhook state in .codex/webhook_registry.json for idempotent re-runs.

API docs:
  POST   /repos/{owner}/{repo}/hooks          — create
  PATCH  /repos/{owner}/{repo}/hooks/{id}     — update
  DELETE /repos/{owner}/{repo}/hooks/{id}     — delete
  GET    /repos/{owner}/{repo}/hooks          — list all

Required token scope:
  Fine-grained PAT with "Webhooks: write" — OR — Classic PAT with "admin:repo_hook"

Usage:
  # Apply declarative config (idempotent)
  python scripts/ci/webhook_configurator.py --apply .codex/webhook_config.json

  # List current webhooks
  python scripts/ci/webhook_configurator.py --list

  # Delete a webhook by ID
  python scripts/ci/webhook_configurator.py --delete 123456

  # Dry-run (show what would change)
  python scripts/ci/webhook_configurator.py --apply .codex/webhook_config.json --dry-run

Environment:
  CODEX_ADMIN_KEY        — Fine-grained PAT with "Webhooks: write" (preferred)
  CODEX_MASTER_KEY       — Classic PAT with "admin:repo_hook" (fallback)
  GITHUB_REPOSITORY      — defaults to Aries-Serpent/_codex_
  WEBHOOK_RECEIVER_URL   — override placeholder URL in config entries whose URL
                           contains "your-cognitive-brain-server.com" or is the
                           PLACEHOLDER_URL sentinel. Set this repo variable once
                           the Cognitive Brain API server is deployed, then run
                           @agent-infra apply-webhooks to activate the hooks.

Webhook config file format (.codex/webhook_config.json):
  {
    "webhooks": [
      {
        "name": "copilot-agent-trigger",
        "url": "https://your-receiver.example.com/github-webhook",
        "secret_env": "WEBHOOK_SECRET",
        "events": ["push", "pull_request", "issue_comment", "workflow_run"],
        "active": true,
        "content_type": "json"
      }
    ]
  }
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
from urllib.parse import urlparse

# ── Constants ────────────────────────────────────────────────────────────────

REPO = os.environ.get("GITHUB_REPOSITORY", "Aries-Serpent/_codex_")
BASE_URL = f"https://api.github.com/repos/{REPO}/hooks"
REGISTRY = Path(".codex/webhook_registry.json")
AUDIT_LOG = Path(".codex/evidence/webhook_audit.jsonl")

# Sentinel in webhook_config.json indicating the real URL has not been set yet.
# When WEBHOOK_RECEIVER_URL env var is set it replaces all entries that still
# carry this placeholder value.
PLACEHOLDER_URL = "https://api.your-cognitive-brain-server.com/webhook/github"

# The full set of webhook events the cognitive brain agents care about
AGENTIC_EVENTS: list[str] = [
    "push",
    "pull_request",
    "issue_comment",
    "pull_request_review_comment",
    "workflow_run",
    "repository_dispatch",
    "check_run",
    "check_suite",
]


# ── Helpers ──────────────────────────────────────────────────────────────────

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
        return e.code, {"error": e.read().decode(errors="replace")}


def _audit(action: str, hook_id: int | None, name: str, status: int, dry_run: bool) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "hook_id": hook_id,
        "name": name,
        "http_status": status,
        "dry_run": dry_run,
        "repo": REPO,
    }
    with AUDIT_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def _load_registry() -> dict:
    if REGISTRY.exists():
        return json.loads(REGISTRY.read_text())
    return {}


def _save_registry(data: dict) -> None:
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY.write_text(json.dumps(data, indent=2))


# ── Core operations ──────────────────────────────────────────────────────────

def list_hooks() -> list[dict]:
    status, data = _request("GET", BASE_URL)
    if status != 200:
        print(f"ERROR listing webhooks: HTTP {status} — {data.get('error', '')}", file=sys.stderr)
        return []
    return data if isinstance(data, list) else []


def create_hook(
    url: str,
    events: list[str],
    secret: str | None = None,
    active: bool = True,
    content_type: str = "json",
    dry_run: bool = False,
) -> dict | None:
    body: dict = {
        "name": "web",
        "active": active,
        "events": events,
        "config": {
            "url": url,
            "content_type": content_type,
            "insecure_ssl": "0",
        },
    }
    if secret:
        body["config"]["secret"] = secret

    if dry_run:
        print(f"  DRY-RUN  CREATE webhook → {url}  events={events}")
        return None

    status, resp = _request("POST", BASE_URL, body)
    ok = status == 201
    icon = "✅" if ok else "❌"
    hook_id = resp.get("id")
    print(f"  {icon}  CREATE {url}  id={hook_id}  (HTTP {status})")
    _audit("create", hook_id, url, status, dry_run)
    return resp if ok else None


def update_hook(
    hook_id: int,
    url: str,
    events: list[str],
    secret: str | None = None,
    active: bool = True,
    content_type: str = "json",
    dry_run: bool = False,
) -> bool:
    body: dict = {
        "active": active,
        "events": events,
        "config": {
            "url": url,
            "content_type": content_type,
            "insecure_ssl": "0",
        },
    }
    if secret:
        body["config"]["secret"] = secret

    if dry_run:
        print(f"  DRY-RUN  UPDATE webhook id={hook_id} → {url}  events={events}")
        return True

    status, _ = _request("PATCH", f"{BASE_URL}/{hook_id}", body)
    ok = status == 200
    icon = "✅" if ok else "❌"
    print(f"  {icon}  UPDATE id={hook_id} → {url}  (HTTP {status})")
    _audit("update", hook_id, url, status, dry_run)
    return ok


def delete_hook(hook_id: int, dry_run: bool = False) -> bool:
    if dry_run:
        print(f"  DRY-RUN  DELETE webhook id={hook_id}")
        return True

    status, _ = _request("DELETE", f"{BASE_URL}/{hook_id}")
    ok = status == 204
    icon = "✅" if ok else "❌"
    print(f"  {icon}  DELETE id={hook_id}  (HTTP {status})")
    _audit("delete", hook_id, "", status, dry_run)
    return ok


def apply_config(config_path: str, dry_run: bool = False) -> int:
    """
    Apply a declarative webhook config file. Idempotent:
    - If a webhook with matching URL already exists → update it
    - If it doesn't exist → create it
    """
    path = Path(config_path)
    if not path.exists():
        print(f"ERROR: Config file not found: {config_path}", file=sys.stderr)
        return 1

    config = json.loads(path.read_text())
    desired = config.get("webhooks", [])

    # If WEBHOOK_RECEIVER_URL is set in the environment, replace placeholder
    # URLs so the operator can drive apply-webhooks entirely via a repo variable
    # without editing webhook_config.json directly.
    receiver_url_override = os.environ.get("WEBHOOK_RECEIVER_URL", "").strip()
    if receiver_url_override:
        for wh in desired:
            existing_url = wh.get("url", "")
            try:
                existing_host = (urlparse(existing_url).hostname or "").lower()
            except (TypeError, ValueError):
                existing_host = ""
            # CodeQL py/incomplete-url-substring-sanitization: match hostname
            # exactly (or its subdomains) rather than a substring of the URL.
            is_placeholder_host = (
                existing_host == "your-cognitive-brain-server.com"
                or existing_host.endswith(".your-cognitive-brain-server.com")
            )
            if existing_url == PLACEHOLDER_URL or is_placeholder_host:
                print(f"  ↳ Overriding placeholder URL with WEBHOOK_RECEIVER_URL for '{wh.get('name', wh['url'])}'")
                wh["url"] = receiver_url_override

    existing = {h["config"]["url"]: h for h in list_hooks() if h.get("config", {}).get("url")}
    registry = _load_registry()
    errors = 0

    for wh in desired:
        receiver_url = wh["url"]
        events = wh.get("events", AGENTIC_EVENTS)
        active = wh.get("active", True)
        ctype = wh.get("content_type", "json")
        secret_env = wh.get("secret_env", "")
        secret = os.environ.get(secret_env) if secret_env else None
        name = wh.get("name", receiver_url)

        if receiver_url in existing:
            hook_id = existing[receiver_url]["id"]
            print(f"Updating webhook '{name}' (id={hook_id}) ...")
            ok = update_hook(hook_id, receiver_url, events, secret=secret,
                             active=active, content_type=ctype, dry_run=dry_run)
        else:
            print(f"Creating webhook '{name}' ...")
            result = create_hook(receiver_url, events, secret=secret,
                                 active=active, content_type=ctype, dry_run=dry_run)
            ok = result is not None or dry_run
            if result:
                registry[name] = {"id": result["id"], "url": receiver_url, "ts": datetime.now(timezone.utc).isoformat()}

        if not ok:
            errors += 1

    if not dry_run:
        _save_registry(registry)

    return errors


# ── CLI ───────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Manage GitHub repository webhooks via REST API."
    )
    parser.add_argument("--apply", metavar="CONFIG_FILE",
                        help="Declaratively apply a webhook config (idempotent)")
    parser.add_argument("--list", action="store_true",
                        help="List all current webhooks")
    parser.add_argument("--delete", metavar="HOOK_ID", type=int,
                        help="Delete a webhook by numeric ID")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print changes without making API calls")
    args = parser.parse_args(argv)

    if args.list:
        hooks = list_hooks()
        if not hooks:
            print("No webhooks found (or permission denied).")
            return 0
        print(f"{'ID':<12} {'ACTIVE':<8} {'URL'}")
        print("-" * 80)
        for h in hooks:
            url = h.get("config", {}).get("url", "?")
            active = "yes" if h.get("active") else "no"
            print(f"{h['id']:<12} {active:<8} {url}")
        return 0

    if args.delete:
        ok = delete_hook(args.delete, dry_run=args.dry_run)
        return 0 if ok else 1

    if args.apply:
        return apply_config(args.apply, dry_run=args.dry_run)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
