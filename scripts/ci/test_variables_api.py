#!/usr/bin/env python3
"""test_variables_api.py — Live end-to-end test for GitHub Variables API.

Tests creating, reading, updating, and deleting variables at:
  - Repository scope  (Aries-Serpent/_codex_)
  - Organization scope (Aries-Serpent)

Requires a PAT with `repo` scope (CODEX_MASTER_KEY or CODEX_BACKUP_KEY).
GITHUB_TOKEN (installation token) will fail with 403 — this is expected and documented.

Usage (GitHub Actions — called from test-variables-api.yml)
-----------------------------------------------------------
    python scripts/ci/test_variables_api.py

Usage (local — requires PAT exported as GH_TOKEN)
--------------------------------------------------
    GH_TOKEN=<your-pat> REPO=Aries-Serpent/_codex_ ORG=Aries-Serpent \
        python scripts/ci/test_variables_api.py

Exit codes
----------
    0  All tests passed
    1  One or more tests failed (see stdout for details)

References
----------
    REST API: https://docs.github.com/en/rest/actions/variables
    Full reference: docs/reference/GITHUB_VARIABLES_SECRETS_REFERENCE.md
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO = os.environ.get("REPO", "Aries-Serpent/_codex_")
ORG = os.environ.get("ORG", "Aries-Serpent")
GH_TOKEN = (
    os.environ.get("CODEX_MASTER_KEY")
    or os.environ.get("CODEX_BACKUP_KEY")
    or os.environ.get("GH_TOKEN")
    or os.environ.get("GITHUB_TOKEN", "")
)
GH_API = "https://api.github.com"
API_VERSION = "2026-03-10"

# Test variable names — timestamped to avoid conflicts with real variables.
_TS = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
REPO_VAR_NAME = f"CODEX_API_TEST_REPO_{_TS}"
ORG_VAR_NAME = f"CODEX_API_TEST_ORG_{_TS}"
REPO_VAR_VALUE_INITIAL = "repo_test_initial"
REPO_VAR_VALUE_UPDATED = "repo_test_updated"
ORG_VAR_VALUE_INITIAL = "org_test_initial"
ORG_VAR_VALUE_UPDATED = "org_test_updated"


# ---------------------------------------------------------------------------
# GitHub API helper
# ---------------------------------------------------------------------------

def _gh(
    method: str,
    path: str,
    body: dict | None = None,
) -> tuple[int, dict | str]:
    """Make a GitHub API request. Returns (status_code, response_body)."""
    url = f"{GH_API}{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GH_TOKEN}",
        "X-GitHub-Api-Version": API_VERSION,
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

_passed: list[str] = []
_failed: list[str] = []


def _assert(name: str, condition: bool, detail: str = "") -> bool:
    if condition:
        _passed.append(name)
        print(f"  ✅ PASS  {name}" + (f" — {detail}" if detail else ""))
    else:
        _failed.append(name)
        print(f"  ❌ FAIL  {name}" + (f" — {detail}" if detail else ""))
    return condition


# ---------------------------------------------------------------------------
# Repository Variable Tests
# ---------------------------------------------------------------------------

def test_repo_variables() -> None:
    print(f"\n{'='*60}")
    print(f"REPO VARIABLE TESTS — {REPO}")
    print(f"{'='*60}")

    # 1. LIST (before create — verify test var doesn't already exist)
    print("\n[1] LIST repo variables")
    status, resp = _gh("GET", f"/repos/{REPO}/actions/variables?per_page=100")
    _assert("list-repo-vars: HTTP 200", status == 200, f"got {status}")
    if status == 200:
        names = [v["name"] for v in resp.get("variables", [])]
        _assert("list-repo-vars: is list", isinstance(names, list), f"{len(names)} vars found")
        _assert(
            "list-repo-vars: test var absent",
            REPO_VAR_NAME not in names,
            f"{REPO_VAR_NAME} should not exist yet",
        )
        print(f"     Existing variables ({len(names)}): {', '.join(names[:5])}{'...' if len(names) > 5 else ''}")

    # 2. CREATE
    print(f"\n[2] CREATE repo variable: {REPO_VAR_NAME}={REPO_VAR_VALUE_INITIAL}")
    status, resp = _gh(
        "POST",
        f"/repos/{REPO}/actions/variables",
        {"name": REPO_VAR_NAME, "value": REPO_VAR_VALUE_INITIAL},
    )
    created = _assert("create-repo-var: HTTP 201", status == 201, f"got {status} — {resp}")
    if not created:
        print(f"     ⚠️  Cannot continue repo tests without successful create. Response: {resp}")
        return

    # 3. GET (verify value)
    print(f"\n[3] GET repo variable: {REPO_VAR_NAME}")
    status, resp = _gh("GET", f"/repos/{REPO}/actions/variables/{REPO_VAR_NAME}")
    _assert("get-repo-var: HTTP 200", status == 200, f"got {status}")
    _assert(
        "get-repo-var: value matches",
        resp.get("value") == REPO_VAR_VALUE_INITIAL,
        f"expected '{REPO_VAR_VALUE_INITIAL}', got '{resp.get('value')}'",
    )
    _assert("get-repo-var: name matches", resp.get("name") == REPO_VAR_NAME)
    print(f"     name={resp.get('name')}  value={resp.get('value')}  "
          f"created_at={resp.get('created_at')}")

    # 4. UPDATE (PATCH)
    print(f"\n[4] UPDATE repo variable: {REPO_VAR_NAME} → {REPO_VAR_VALUE_UPDATED}")
    status, resp = _gh(
        "PATCH",
        f"/repos/{REPO}/actions/variables/{REPO_VAR_NAME}",
        {"name": REPO_VAR_NAME, "value": REPO_VAR_VALUE_UPDATED},
    )
    _assert("update-repo-var: HTTP 204", status == 204, f"got {status} — {resp}")

    # 5. GET (verify updated value)
    print("\n[5] GET repo variable after update")
    status, resp = _gh("GET", f"/repos/{REPO}/actions/variables/{REPO_VAR_NAME}")
    _assert(
        "get-repo-var-after-update: value updated",
        resp.get("value") == REPO_VAR_VALUE_UPDATED,
        f"expected '{REPO_VAR_VALUE_UPDATED}', got '{resp.get('value')}'",
    )

    # 6. DELETE (cleanup)
    print(f"\n[6] DELETE repo variable: {REPO_VAR_NAME}")
    status, resp = _gh("DELETE", f"/repos/{REPO}/actions/variables/{REPO_VAR_NAME}")
    _assert("delete-repo-var: HTTP 204", status == 204, f"got {status} — {resp}")

    # 7. GET after delete (verify 404)
    print("\n[7] GET repo variable after delete (expect 404)")
    status, resp = _gh("GET", f"/repos/{REPO}/actions/variables/{REPO_VAR_NAME}")
    _assert("get-deleted-repo-var: HTTP 404", status == 404, f"got {status}")


# ---------------------------------------------------------------------------
# Organization Variable Tests
# ---------------------------------------------------------------------------

def test_org_variables() -> None:
    print(f"\n{'='*60}")
    print(f"ORG VARIABLE TESTS — {ORG}")
    print(f"{'='*60}")

    # 1. LIST
    print("\n[1] LIST org variables")
    status, resp = _gh("GET", f"/orgs/{ORG}/actions/variables?per_page=100")
    _assert("list-org-vars: HTTP 200", status == 200, f"got {status}")
    if status == 200:
        names = [v["name"] for v in resp.get("variables", [])]
        _assert("list-org-vars: is list", isinstance(names, list), f"{len(names)} vars found")
        print(f"     Existing org variables ({len(names)}): {', '.join(names[:5])}{'...' if len(names) > 5 else ''}")
    elif status == 403:
        print("     ⚠️  403: Token lacks admin:org scope — org variable tests require admin:org PAT.")
        print("     ℹ️  GITHUB_TOKEN and standard repo PATs cannot access org variables.")
        _assert("list-org-vars: scope-gate expected", True, "403 is correct for non-admin:org token")
        return
    else:
        print(f"     ⚠️  Unexpected {status} — skipping org tests")
        return

    # 2. CREATE
    print(f"\n[2] CREATE org variable: {ORG_VAR_NAME}={ORG_VAR_VALUE_INITIAL}")
    status, resp = _gh(
        "POST",
        f"/orgs/{ORG}/actions/variables",
        {
            "name": ORG_VAR_NAME,
            "value": ORG_VAR_VALUE_INITIAL,
            "visibility": "private",
        },
    )
    created = _assert("create-org-var: HTTP 201", status == 201, f"got {status} — {resp}")
    if not created:
        print(f"     ⚠️  Cannot continue org tests without successful create. Response: {resp}")
        return

    # 3. GET
    print(f"\n[3] GET org variable: {ORG_VAR_NAME}")
    status, resp = _gh("GET", f"/orgs/{ORG}/actions/variables/{ORG_VAR_NAME}")
    _assert("get-org-var: HTTP 200", status == 200, f"got {status}")
    _assert(
        "get-org-var: value matches",
        resp.get("value") == ORG_VAR_VALUE_INITIAL,
        f"expected '{ORG_VAR_VALUE_INITIAL}', got '{resp.get('value')}'",
    )
    print(f"     name={resp.get('name')}  value={resp.get('value')}  "
          f"visibility={resp.get('visibility')}")

    # 4. UPDATE
    print(f"\n[4] UPDATE org variable: {ORG_VAR_NAME} → {ORG_VAR_VALUE_UPDATED}")
    status, resp = _gh(
        "PATCH",
        f"/orgs/{ORG}/actions/variables/{ORG_VAR_NAME}",
        {
            "name": ORG_VAR_NAME,
            "value": ORG_VAR_VALUE_UPDATED,
            "visibility": "private",
        },
    )
    _assert("update-org-var: HTTP 204", status == 204, f"got {status} — {resp}")

    # 5. GET after update
    print("\n[5] GET org variable after update")
    status, resp = _gh("GET", f"/orgs/{ORG}/actions/variables/{ORG_VAR_NAME}")
    _assert(
        "get-org-var-after-update: value updated",
        resp.get("value") == ORG_VAR_VALUE_UPDATED,
        f"expected '{ORG_VAR_VALUE_UPDATED}', got '{resp.get('value')}'",
    )

    # 6. DELETE
    print(f"\n[6] DELETE org variable: {ORG_VAR_NAME}")
    status, resp = _gh("DELETE", f"/orgs/{ORG}/actions/variables/{ORG_VAR_NAME}")
    _assert("delete-org-var: HTTP 204", status == 204, f"got {status} — {resp}")

    # 7. Verify deleted
    print("\n[7] GET org variable after delete (expect 404)")
    status, resp = _gh("GET", f"/orgs/{ORG}/actions/variables/{ORG_VAR_NAME}")
    _assert("get-deleted-org-var: HTTP 404", status == 404, f"got {status}")


# ---------------------------------------------------------------------------
# Token validation
# ---------------------------------------------------------------------------

def test_token_info() -> None:
    print(f"\n{'='*60}")
    print("TOKEN VALIDATION")
    print(f"{'='*60}")

    if not GH_TOKEN:
        print("  ❌ No token found in CODEX_MASTER_KEY / CODEX_BACKUP_KEY / GH_TOKEN / GITHUB_TOKEN")
        _failed.append("token-present")
        return

    # Identify token type
    status, resp = _gh("GET", "/user")
    if status == 200:
        login = resp.get("login", "unknown")
        _assert("token: authenticated", True, f"logged in as {login}")
        print(f"     login={login}")
    else:
        _assert("token: authenticated", False, f"HTTP {status}")
        return

    # Check scopes via rate_limit endpoint headers
    url = f"{GH_API}/rate_limit"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GH_TOKEN}",
            "X-GitHub-Api-Version": API_VERSION,
        },
    )
    try:
        with urllib.request.urlopen(req) as resp_raw:
            scopes_header = resp_raw.headers.get("X-OAuth-Scopes", "")
            token_source = (
                "CODEX_MASTER_KEY" if os.environ.get("CODEX_MASTER_KEY")
                else "CODEX_BACKUP_KEY" if os.environ.get("CODEX_BACKUP_KEY")
                else "GH_TOKEN" if os.environ.get("GH_TOKEN")
                else "GITHUB_TOKEN"
            )
            print(f"     token_source={token_source}")
            print(f"     X-OAuth-Scopes={scopes_header or '(none — installation token)'}")
            has_repo_scope = "repo" in scopes_header.split(", ")
            has_admin_org = "admin:org" in scopes_header.split(", ")
            _assert(
                "token: has repo scope",
                has_repo_scope,
                "Required for repo variable CRUD. Use CODEX_MASTER_KEY or CODEX_BACKUP_KEY.",
            )
            _assert(
                "token: has admin:org scope",
                has_admin_org,
                "Required for org variable CRUD. Fine-grained PAT or classic PAT with admin:org.",
            )
    except urllib.error.HTTPError as e:
        _assert("token: rate-limit check", False, f"HTTP {e.code}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("GitHub Variables API — Live End-to-End Test")
    print(f"Repo:  {REPO}")
    print(f"Org:   {ORG}")
    print(f"Time:  {datetime.now(tz=timezone.utc).isoformat()}")
    print("=" * 60)

    test_token_info()
    test_repo_variables()
    test_org_variables()

    # Summary
    total = len(_passed) + len(_failed)
    print(f"\n{'='*60}")
    print(f"RESULTS: {len(_passed)}/{total} passed, {len(_failed)} failed")
    if _failed:
        print(f"FAILED tests: {', '.join(_failed)}")
    print("=" * 60)

    if _failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
