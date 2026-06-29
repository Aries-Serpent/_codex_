#!/usr/bin/env python3
"""
github_app_bootstrap.py — Bootstrap a GitHub App from CODEX_BACKUP_KEY.

Registers a GitHub App via the App Manifest API, configures its webhook,
saves credentials, and writes the App ID to GITHUB_APP_ID repository variable.

Flow:
  1. Generate an App manifest (name, permissions, events, webhook URL)
  2. POST to /app-manifests/{code}/conversions with a temporary OAuth code
     (obtained by directing the user/admin to the GitHub manifest flow URL)
  3. Save returned credentials (app_id, client_id, pem) to .codex/github_app/
  4. Update GITHUB_APP_ID repo variable via github_var_writer.py
  5. Optionally configure the webhook receiver URL

Since GitHub requires a browser-based OAuth step for app registration, this
script generates the manifest URL for step 1, and handles the conversion
(step 2) from the CLI once the admin provides the one-time code.

Usage:
  # Step 1 — Print the manifest redirect URL (open in browser as org owner)
  python scripts/ci/github_app_bootstrap.py --generate-manifest-url

  # Step 2 — Convert one-time code → App credentials
  python scripts/ci/github_app_bootstrap.py --convert-code ABC123XYZ

  # Show registered App info
  python scripts/ci/github_app_bootstrap.py --show

  # Re-configure webhook URL on existing app (requires JWT)
  python scripts/ci/github_app_bootstrap.py --update-webhook https://receiver.example.com/github

Environment:
  CODEX_BACKUP_KEY      — PAT used for registration (must have read:org + admin:org_hook)
  CODEX_ADMIN_KEY       — optional, used for variable writes
  GITHUB_REPOSITORY     — defaults to Aries-Serpent/_codex_
  WEBHOOK_RECEIVER_URL  — target URL for the app's webhook (optional, can be set later)

Output files:
  .codex/github_app/app_credentials.json  — app_id, client_id, html_url
  .codex/github_app/private_key.pem       — private key (NEVER COMMIT THIS FILE)

Security notes:
  - private_key.pem is automatically added to .gitignore
  - Never print the private key to stdout
  - CODEX_BACKUP_KEY is NOT logged

References:
  https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/registering-a-github-app-from-a-manifest
  https://docs.github.com/en/rest/apps/webhooks
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
from scripts.ci._token_resolver import get_token


# ── Constants ────────────────────────────────────────────────────────────────

REPO = os.environ.get("GITHUB_REPOSITORY", "Aries-Serpent/_codex_")
OWNER = REPO.split("/")[0]
APP_DIR = Path(".codex/github_app")
CREDENTIALS_FILE = APP_DIR / "app_credentials.json"
PRIVATE_KEY_FILE = APP_DIR / "private_key.pem"
GITIGNORE = Path(".gitignore")

# Default permissions for the Cognitive Brain agent app
APP_MANIFEST = {
    "name": "codex-cognitive-brain",
    "description": "Cognitive Brain autonomous agent for Aries-Serpent/_codex_",
    "url": f"https://github.com/{REPO}",
    "hook_attributes": {
        "url": os.environ.get("WEBHOOK_RECEIVER_URL", "https://placeholder.example.com/github-hook"),
        "active": True,
    },
    "redirect_url": f"https://github.com/{REPO}",
    "callback_urls": [f"https://github.com/{REPO}"],
    "public": False,
    "default_permissions": {
        "contents": "write",
        "issues": "write",
        "pull_requests": "write",
        "actions": "write",
        "metadata": "read",
        "administration": "read",
    },
    "default_events": [
        "push",
        "pull_request",
        "issue_comment",
        "pull_request_review_comment",
        "workflow_run",
        "issues",
        "check_run",
    ],
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _backup_token() -> str:
    t = get_token(required_elevated=True)[0] or os.environ.get("CODEX_ADMIN_KEY", "")
    if not t:
        print("ERROR: Set CODEX_BACKUP_KEY (needs admin:org_hook + read:org scopes).", file=sys.stderr)
        sys.exit(1)
    return t


def _ensure_gitignore_excludes_pem() -> None:
    """Make sure .codex/github_app/private_key.pem is never committed."""
    lines = GITIGNORE.read_text().splitlines() if GITIGNORE.exists() else []
    entry = ".codex/github_app/private_key.pem"
    if entry not in lines:
        with GITIGNORE.open("a") as f:
            f.write(f"\n# GitHub App private key — never commit\n{entry}\n")
        print(f"  ✅ Added {entry} to .gitignore")


def _save_credentials(data: dict) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    _ensure_gitignore_excludes_pem()

    # Separate private key from public credentials
    pem = data.pop("pem", None)
    if pem:
        PRIVATE_KEY_FILE.write_text(pem)
        PRIVATE_KEY_FILE.chmod(0o600)
        print(f"  ✅ Private key saved to {PRIVATE_KEY_FILE}  (mode 600, git-ignored)")

    creds = {
        "app_id": data.get("id"),
        "client_id": data.get("client_id"),
        "slug": data.get("slug"),
        "html_url": data.get("html_url"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "repo": REPO,
    }
    CREDENTIALS_FILE.write_text(json.dumps(creds, indent=2))
    print(f"  ✅ Credentials saved to {CREDENTIALS_FILE}")
    return creds


def _load_credentials() -> dict:
    if not CREDENTIALS_FILE.exists():
        print(f"ERROR: No credentials found at {CREDENTIALS_FILE}. Run --convert-code first.", file=sys.stderr)
        sys.exit(1)
    return json.loads(CREDENTIALS_FILE.read_text())


# ── Commands ──────────────────────────────────────────────────────────────────

def generate_manifest_url() -> None:
    """Print the URL the admin must open in a browser to register the app."""
    import urllib.parse

    manifest_json = json.dumps(APP_MANIFEST)
    encoded = urllib.parse.quote(manifest_json)
    url = f"https://github.com/organizations/{OWNER}/settings/apps/new?state=codex-bootstrap&manifest={encoded}"

    print("\n" + "=" * 70)
    print("STEP 1 — Open this URL as an org owner in your browser:")
    print("=" * 70)
    print(url)
    print("=" * 70)
    print("\nAfter clicking 'Create GitHub App', GitHub will redirect to:")
    print(f"  https://github.com/{REPO}?code=XXXXXXXXX&state=codex-bootstrap")
    print("\nCopy the `code=` value and run:")
    print("  python scripts/ci/github_app_bootstrap.py --convert-code <CODE>")
    print()


def convert_code(code: str) -> None:
    """Exchange a one-time manifest code for App credentials."""
    token = _backup_token()
    url = f"https://api.github.com/app-manifests/{code}/conversions"

    req = urllib.request.Request(url, data=b"{}", method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors="replace")
        print(f"ERROR: HTTP {e.code} — {msg}", file=sys.stderr)
        sys.exit(1)

    creds = _save_credentials(data)
    print("\n✅ GitHub App registered successfully!")
    print(f"   App ID   : {creds['app_id']}")
    print(f"   Slug     : {creds['slug']}")
    print(f"   URL      : {creds['html_url']}")

    # Write GITHUB_APP_ID to repo variables
    app_id = str(creds["app_id"]) if creds.get("app_id") else ""
    if app_id:
        print(f"\nWriting GITHUB_APP_ID={app_id} to repo variables ...")
        # Import and call github_var_writer directly
        scripts_dir = Path(__file__).parent
        sys.path.insert(0, str(scripts_dir))
        try:
            import github_var_writer as vw
            vw.upsert_var("GITHUB_APP_ID", app_id, force=True)
        except Exception as e:
            print(f"  ⚠️  Could not auto-write variable: {e}. Run manually:")
            print(f"     python scripts/ci/github_var_writer.py --set GITHUB_APP_ID={app_id} --force")


def update_webhook(receiver_url: str) -> None:
    """Update the app's webhook URL using JWT authentication."""
    if not PRIVATE_KEY_FILE.exists():
        print(f"ERROR: Private key not found at {PRIVATE_KEY_FILE}", file=sys.stderr)
        sys.exit(1)

    creds = _load_credentials()
    app_id = creds.get("app_id")
    if not app_id:
        print("ERROR: No app_id in credentials.", file=sys.stderr)
        sys.exit(1)

    # Attempt to generate JWT using PyJWT if available, else advise manual
    try:
        import importlib.util as _ilu
        if _ilu.find_spec("jwt") is None:
            raise ImportError("PyJWT not installed")
        import jwt as pyjwt  # type: ignore[import-not-found]
        pem = PRIVATE_KEY_FILE.read_text()
        now = int(datetime.now(timezone.utc).timestamp())
        payload = {"iat": now - 60, "exp": now + 600, "iss": app_id}
        token = pyjwt.encode(payload, pem, algorithm="RS256")
    except ImportError:
        print("⚠️  PyJWT not installed. Install with: pip install PyJWT cryptography")
        print("Then re-run this command.")
        return

    url = "https://api.github.com/app/hook/config"
    body = json.dumps({
        "url": receiver_url,
        "content_type": "json",
        "insecure_ssl": "0",
    }).encode()
    req = urllib.request.Request(url, data=body, method="PATCH")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.load(resp)
            print(f"✅ Webhook updated: {result.get('url', receiver_url)}")
    except urllib.error.HTTPError as e:
        print(f"ERROR: HTTP {e.code} — {e.read().decode(errors='replace')}", file=sys.stderr)


def show_app() -> None:
    """Print registered app info."""
    creds = _load_credentials()
    print("\n── GitHub App Credentials ──────────────────────────────────")
    for k, v in creds.items():
        print(f"  {k:<20} {v}")
    has_pem = PRIVATE_KEY_FILE.exists()
    print(f"  {'private_key.pem':<20} {'present ✅' if has_pem else 'MISSING ❌'}")
    print()


# ── CLI ───────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Bootstrap a GitHub App from CODEX_BACKUP_KEY."
    )
    parser.add_argument("--generate-manifest-url", action="store_true",
                        help="Print the browser URL to register the app (Step 1)")
    parser.add_argument("--convert-code", metavar="CODE",
                        help="Exchange one-time OAuth code for app credentials (Step 2)")
    parser.add_argument("--update-webhook", metavar="URL",
                        help="Update the app webhook URL (requires private key)")
    parser.add_argument("--show", action="store_true",
                        help="Show registered app credentials")
    args = parser.parse_args(argv)

    if args.generate_manifest_url:
        generate_manifest_url()
        return 0

    if args.convert_code:
        convert_code(args.convert_code)
        return 0

    if args.update_webhook:
        update_webhook(args.update_webhook)
        return 0

    if args.show:
        show_app()
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
