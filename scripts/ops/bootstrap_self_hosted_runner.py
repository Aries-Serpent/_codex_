#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import platform
import shlex
import subprocess
from pathlib import Path

from src.integrations.github_app_auth import mint_app_jwt, exchange_installation_token, create_runner_registration_token


def _assert_online_allowed():
    mode = os.getenv("CODEX_NET_MODE", "offline")
    allow = os.getenv("CODEX_ALLOWLIST_HOSTS", "")
    if mode != "online_allowlist" or "api.github.com" not in {h.strip() for h in allow.split(",") if h.strip()}:
        raise SystemExit("Online mode denied. Set CODEX_NET_MODE=online_allowlist and include api.github.com in CODEX_ALLOWLIST_HOSTS.")


def _download_url(version: str) -> str:
    os_name = "linux"
    arch = "x64" if platform.machine() in {"x86_64", "amd64"} else platform.machine()
    return f"https://github.com/actions/runner/releases/download/v{version}/actions-runner-{os_name}-{arch}-{version}.tar.gz"


def _exec(cmd: str, dry_run: bool) -> int:
    print(f"$ {cmd}")
    if dry_run:
        return 0
    return subprocess.call(cmd, shell=True)


def main():
    p = argparse.ArgumentParser(description="Bootstrap a self-hosted GitHub Actions runner on this host.")
    scope = p.add_mutually_exclusive_group(required=True)
    scope.add_argument("--repo", help="Repository name (requires --owner)")
    scope.add_argument("--org", help="Organization for org-level runner")
    p.add_argument("--owner", help="Repository owner (when using --repo)")
    p.add_argument("--labels", default="codex,linux,x64", help="Comma-separated labels for this runner")
    p.add_argument("--workdir", default=str(Path.home() / "actions-runner"), help="Runner home directory")
    p.add_argument("--runner-version", default=os.getenv("GITHUB_RUNNER_VERSION", "2.317.0"))
    p.add_argument("--dry-run", action="store_true", help="Print commands and plan; do not execute")
    p.add_argument("--no-service", action="store_true", help="Do not install/start the runner as a system service")
    args = p.parse_args()

    _assert_online_allowed()

    app_id = os.getenv("GITHUB_APP_ID")
    inst_id = os.getenv("GITHUB_APP_INSTALLATION_ID")
    if not app_id or not inst_id:
        raise SystemExit("Missing GITHUB_APP_ID or GITHUB_APP_INSTALLATION_ID.")

    print("Minting App JWT ...")
    app_jwt = mint_app_jwt(app_id)
    print("Exchanging Installation Access Token ...")
    installation_token, expires_at = exchange_installation_token(app_jwt, inst_id)
    print(f"[info] Installation token expires_at={expires_at}")

    print("Requesting Runner Registration Token ...")
    reg_token = create_runner_registration_token(
        installation_token, owner=args.owner if args.repo else "", repo=args.repo, org=args.org
    )

    runner_home = Path(args.workdir)
    runner_home.mkdir(parents=True, exist_ok=True)
    url = _download_url(args.runner_version)

    # Download & extract
    cmds = [
        f"cd {shlex.quote(str(runner_home))}",
        f"curl -fL {shlex.quote(url)} -o actions-runner.tar.gz",
        "tar xzf actions-runner.tar.gz",
    ]
    for c in cmds:
        rc = _exec(c, args.dry_run)
        if rc != 0:
            raise SystemExit(f"Command failed: {c}")

    # Configure runner
    config = "./config.sh "
    if args.repo:
        config += f"--url https://github.com/{args.owner}/{args.repo} "
    else:
        config += f"--url https://github.com/{args.org} "
    config += f"--token {shlex.quote(reg_token)} --labels {shlex.quote(args.labels)} --unattended --ephemeral"
    if _exec(config, args.dry_run) != 0:
        raise SystemExit("Runner config failed.")

    # Optionally install & start service
    if not args.no_service:
        if _exec("sudo ./svc.sh install", args.dry_run) != 0:
            raise SystemExit("Service install failed.")
        if _exec("sudo ./svc.sh start", args.dry_run) != 0:
            raise SystemExit("Service start failed.")

    print("Done. Verify runner status in GitHub Settings → Actions → Runners.")


if __name__ == "__main__":
    main()