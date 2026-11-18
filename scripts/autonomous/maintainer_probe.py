"""Redacted capability and credential probe for the maintainer control plane."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CLI_API_URL = "http://127.0.0.1:8765"


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def command_available(name: str) -> bool:
    return shutil.which(name) is not None


def environment_presence(names: tuple[str, ...]) -> dict[str, bool]:
    return {name: bool(os.environ.get(name)) for name in names}


def sanitize_remote(value: str) -> str:
    """Return a log-safe remote containing no URL username or password."""
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme and parsed.hostname:
        host = parsed.hostname
        if parsed.port:
            host = f"{host}:{parsed.port}"
        return urllib.parse.urlunsplit((parsed.scheme, host, parsed.path, parsed.query, ""))
    if "@" in value and ":" in value:
        _, host_path = value.rsplit("@", 1)
        return host_path
    return value


def approved_api_origin(value: str) -> bool:
    """Allow loopback by default and explicitly approved HTTPS origins."""
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return False
    if parsed.hostname.lower() in {"localhost", "127.0.0.1", "::1"}:
        return parsed.username is None and parsed.password is None
    configured = os.environ.get("CODEX_ALLOWED_CLI_API_ORIGINS", "")
    approved = {origin.strip().rstrip("/") for origin in configured.split(",") if origin.strip()}
    return parsed.scheme == "https" and value.rstrip("/") in approved


def git_state() -> dict[str, Any]:
    def git(*args: str) -> str:
        result = subprocess.run(
            ["git", "--no-pager", *args],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    status = git("status", "--porcelain=v1")
    return {
        "branch": git("branch", "--show-current") or None,
        "head": git("rev-parse", "HEAD"),
        "dirty": bool(status),
        "remote_origin": sanitize_remote(git("remote", "get-url", "origin")) or None,
    }


def github_identity_probe() -> dict[str, Any]:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        return {"attempted": False, "credential_present": False, "http_status": None}

    request = urllib.request.Request(
        "https://api.github.com/user",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return {
                "attempted": True,
                "credential_present": True,
                "credential_source": (
                    "GITHUB_TOKEN" if os.environ.get("GITHUB_TOKEN") else "GH_TOKEN"
                ),
                "http_status": response.status,
                "authenticated_actor": payload.get("login"),
            }
    except urllib.error.HTTPError as exc:
        return {
            "attempted": True,
            "credential_present": True,
            "credential_source": "GITHUB_TOKEN" if os.environ.get("GITHUB_TOKEN") else "GH_TOKEN",
            "http_status": exc.code,
        }


def gh_probe() -> dict[str, Any]:
    if not command_available("gh"):
        return {"installed": False, "authenticated": None}

    result = subprocess.run(
        ["gh", "auth", "status"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return {
        "installed": True,
        "authenticated": result.returncode == 0,
        "exit_code": result.returncode,
    }


def public_repo_probe() -> dict[str, Any]:
    request = urllib.request.Request(
        "https://api.github.com/repos/Aries-Serpent/_codex_",
        headers={"Accept": "application/vnd.github+json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return {
                "http_status": response.status,
                "description": payload.get("description"),
                "default_branch": payload.get("default_branch"),
                "archived": payload.get("archived"),
            }
    except urllib.error.HTTPError as exc:
        return {"http_status": exc.code}


def cli_api_probe() -> dict[str, Any]:
    base_url = (
        os.environ.get("CODEX_CLI_API_URL")
        or os.environ.get("COPILOT_CLI_BASE_URL")
        or DEFAULT_CLI_API_URL
    ).rstrip("/")
    if not approved_api_origin(base_url):
        return {
            "reachable": False,
            "http_status": None,
            "base_url": base_url,
            "blocked_reason": "origin_not_approved",
        }
    try:
        with urllib.request.urlopen(f"{base_url}/api/health", timeout=2) as response:
            return {
                "reachable": True,
                "http_status": response.status,
                "base_url": base_url,
            }
    except Exception:
        return {"reachable": False, "http_status": None, "base_url": base_url}


def mcp_probe() -> dict[str, Any]:
    validator = ROOT / "scripts" / "validate_mcp.py"
    if not validator.exists():
        return {"documented": False, "probe_available": False}
    return {
        "documented": True,
        "probe_available": True,
        "host_exposed": False,
        "exposure_status": "not_verified_in_current_copilot_host",
    }


def vscode_extension_probe() -> dict[str, bool]:
    code = shutil.which("code")
    if not code:
        return {"code_cli_available": False}

    result = subprocess.run(
        [code, "--list-extensions"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    installed = set(result.stdout.splitlines()) if result.returncode == 0 else set()
    relevant = (
        "github.copilot",
        "github.copilot-chat",
        "github.vscode-pull-request-github",
        "github.vscode-github-actions",
        "ms-python.python",
        "ms-python.debugpy",
        "ms-playwright.playwright",
    )
    return {"code_cli_available": True, **{name: name in installed for name in relevant}}


def main() -> int:
    tool_names = (
        "git",
        "code",
        "gh",
        "curl",
        "node",
        "npm",
        "npx",
        "python3",
        "python3.12",
        "go",
        "cargo",
        "docker",
        "podman",
        "actionlint",
    )
    credential_names = (
        "GITHUB_TOKEN",
        "GH_TOKEN",
        "CODEX_MASTER_KEY",
        "CODEX_BACKUP_KEY",
        "CODEX_ADMIN_KEY",
        "AGENT_GITHUB_TOKEN",
    )

    report = {
        "timestamp": utc_timestamp(),
        "python": list(sys.version_info[:3]),
        "workspace": str(ROOT),
        "codespace": {
            "detected": bool(os.environ.get("CODESPACE_NAME")),
            "name": os.environ.get("CODESPACE_NAME"),
            "workspace_from_environment": os.environ.get("CODESPACE_VSCODE_FOLDER"),
            "name_is_runtime_evidence_only": True,
        },
        "git": git_state(),
        "tools": {name: command_available(name) for name in tool_names},
        "credentials": environment_presence(credential_names),
        "github_identity": github_identity_probe(),
        "gh": gh_probe(),
        "public_repository": public_repo_probe(),
        "cli_api": cli_api_probe(),
        "mcp": mcp_probe(),
        "vscode": vscode_extension_probe(),
        "workspace_files": {
            "venv": (ROOT / ".venv" / "bin" / "python").is_file(),
            "node_modules": (ROOT / "cognitive_app" / "node_modules").is_dir(),
            "playwright_package": (
                ROOT / "cognitive_app" / "node_modules" / "@playwright" / "test"
            ).is_dir(),
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
