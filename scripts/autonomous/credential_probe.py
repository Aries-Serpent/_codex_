"""Redacted GitHub credential and operation-permission probe."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.autonomous.github_permission_matrix import azimuth_write_plan  # noqa: E402

API_ROOT = "https://api.github.com"
REPOSITORY = "Aries-Serpent/_codex_"
TOKEN_SOURCES = (
    "CODEX_MASTER_KEY",
    "CODEX_BACKUP_KEY",
    "GH_TOKEN",
    "GITHUB_TOKEN",
)
READ_PROBES = {
    "repository": f"/repos/{REPOSITORY}",
    "pull_requests": f"/repos/{REPOSITORY}/pulls?state=all&per_page=1",
    "actions_runs": f"/repos/{REPOSITORY}/actions/runs?per_page=1",
    "checks": f"/repos/{REPOSITORY}/commits/main/check-runs?per_page=1",
    "releases": f"/repos/{REPOSITORY}/releases?per_page=1",
    "deployments": f"/repos/{REPOSITORY}/deployments?per_page=1",
    "code_scanning": f"/repos/{REPOSITORY}/code-scanning/alerts?per_page=1",
    "secret_scanning": f"/repos/{REPOSITORY}/secret-scanning/alerts?per_page=1",
}


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def request_json(
    path: str,
    token: str,
    *,
    method: str = "GET",
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(
        f"{API_ROOT}{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            headers = {key.lower(): value for key, value in response.headers.items()}
            payload = json.loads(response.read().decode("utf-8"))
            return {
                "status": response.status,
                "oauth_scopes": headers.get("x-oauth-scopes"),
                "accepted_oauth_scopes": headers.get("x-accepted-oauth-scopes"),
                "rate_limit_remaining": headers.get("x-ratelimit-remaining"),
                "payload": payload,
            }
    except urllib.error.HTTPError as exc:
        headers = {key.lower(): value for key, value in exc.headers.items()}
        return {
            "status": exc.code,
            "oauth_scopes": headers.get("x-oauth-scopes"),
            "accepted_oauth_scopes": headers.get("x-accepted-oauth-scopes"),
            "rate_limit_remaining": headers.get("x-ratelimit-remaining"),
            "message": exc.read().decode("utf-8", errors="replace")[:240],
        }


def safe_contents_write_probe(token: str) -> dict[str, Any]:
    """Create an unreferenced blob that cannot alter repository-visible refs."""
    marker = f"codex-azimuth-write-probe-{utc_timestamp()}"
    result = request_json(
        f"/repos/{REPOSITORY}/git/blobs",
        token,
        method="POST",
        body={"content": marker, "encoding": "utf-8"},
    )
    payload = result.get("payload")
    return {
        "status": result.get("status"),
        "write_verified": result.get("status") == 201,
        "blob_sha": payload.get("sha") if isinstance(payload, dict) else None,
        "visible_ref_changed": False,
        "denial": result.get("message") if result.get("status") != 201 else None,
        "marker_in_report": False,
    }


def probe_source(source: str, token: str, *, live_safe_probes: bool = False) -> dict[str, Any]:
    identity = request_json("/user", token)
    probe_results: dict[str, dict[str, Any]] = {}
    repository_permissions: dict[str, Any] | None = None
    for operation, path in READ_PROBES.items():
        result = request_json(path, token)
        payload = result.pop("payload", None)
        if operation == "repository" and isinstance(payload, dict):
            repository_permissions = payload.get("permissions")
        probe_results[operation] = {
            "status": result.get("status"),
            "read_verified": result.get("status") == 200,
            "oauth_scopes": result.get("oauth_scopes"),
            "accepted_oauth_scopes": result.get("accepted_oauth_scopes"),
            "rate_limit_remaining": result.get("rate_limit_remaining"),
            "denial": result.get("message") if result.get("status") != 200 else None,
        }

    identity_payload = identity.get("payload")
    live_safe_writes = None
    if live_safe_probes and identity.get("status") == 200:
        live_safe_writes = {"contents": safe_contents_write_probe(token)}
    return {
        "source": source,
        "configured": True,
        "identity_status": identity.get("status"),
        "actor": identity_payload.get("login") if isinstance(identity_payload, dict) else None,
        "repository_permissions": repository_permissions,
        "reads": probe_results,
        "write_verified": False,
        "write_verification": "deferred_to_authorized_task_scoped_reversible_operation",
        "azimuth_writes": azimuth_write_plan(),
        "live_safe_writes": live_safe_writes,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe GitHub credentials and permissions")
    parser.add_argument(
        "--live-safe-probes",
        action="store_true",
        help="Run only reversible no-ref live write probes (currently Contents blob)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    seen_tokens: dict[str, list[str]] = {}
    credentials: list[dict[str, Any]] = []
    for source in TOKEN_SOURCES:
        token = os.environ.get(source, "").strip()
        if not token:
            credentials.append({"source": source, "configured": False})
            continue
        if token in seen_tokens:
            seen_tokens[token].append(source)
            credentials.append(
                {
                    "source": source,
                    "configured": True,
                    "deduplicated_as": seen_tokens[token][0],
                    "write_verified": False,
                }
            )
            continue
        seen_tokens[token] = [source]
        credentials.append(probe_source(source, token, live_safe_probes=args.live_safe_probes))

    report = {
        "timestamp": utc_timestamp(),
        "repository": REPOSITORY,
        "credential_sources": credentials,
        "github_app": {
            "id_present": bool(os.environ.get("_GITHUB_APP_ID") or os.environ.get("GITHUB_APP_ID")),
            "private_key_present": bool(
                os.environ.get("_GITHUB_APP_PRIVATE_KEY")
                or os.environ.get("GITHUB_APP_PRIVATE_KEY_PEM")
            ),
            "installation_id_present": bool(
                os.environ.get("_GITHUB_APP_INSTALLATION_ID")
                or os.environ.get("GITHUB_APP_INSTALLATION_ID")
            ),
            "probe_status": "requires_authenticated_installation_adapter",
            "write_verified": False,
        },
        "secret_values_included": False,
        "azimuth_write_objective": {
            "scope": "operation-level write verification for all GitHub permission families",
            "live_write_enabled": args.live_safe_probes,
            "method": "rubber_duck_preflight -> adversarial_denial -> reversible_live_probe -> reconcile_rollback",
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
