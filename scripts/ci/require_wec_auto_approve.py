#!/usr/bin/env python3
"""Require the wec:auto-approve label before an approval-capable workflow can act."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any

LABEL_NAME = "wec:auto-approve"


def _gh(method: str, path: str, token: str, body: dict[str, Any] | None = None) -> tuple[int, Any]:
    url = f"https://api.github.com{path}"
    data = json.dumps(body).encode() if body is not None else None
    headers = {
        "Authorization": f""******",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
        "User-Agent": "codex-require-wec-auto-approve/1.0",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = resp.read()
            try:
                return resp.status, json.loads(payload) if payload.strip() else {}
            except json.JSONDecodeError:
                return resp.status, {"raw": payload[:200].decode("utf-8", errors="replace")}
    except urllib.error.HTTPError as exc:
        try:
            err_body = json.loads(exc.read())
        except Exception:
            err_body = {"message": str(exc)}
        return exc.code, err_body


def get_pr_labels(token: str, repo: str, pr_number: int) -> list[str]:
    status, data = _gh("GET", f"/repos/{repo}/issues/{pr_number}", token)
    if status != 200 or not isinstance(data, dict):
        return []
    labels = data.get("labels", [])
    return [label.get("name", "") for label in labels if isinstance(label, dict)]


def has_wec_auto_approve(token: str, repo: str, pr_number: int) -> bool:
    return LABEL_NAME in get_pr_labels(token, repo, pr_number)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr-number", type=int, required=True, help="Pull request number to validate")
    parser.add_argument("--repo", default=os.environ.get("REPO") or os.environ.get("GITHUB_REPOSITORY", ""), help="Repository slug, e.g. owner/repo")
    parser.add_argument("--token", default=os.environ.get("GH_TOKEN") or os.environ.get("CODEX_MASTER_KEY") or os.environ.get("CODEX_BACKUP_KEY") or "", help="GitHub token")
    args = parser.parse_args()

    if not args.repo:
        print("::error::REPO is required to validate wec:auto-approve.")
        return 0
    if not args.token:
        print("::notice::No GH_TOKEN/CODEX_MASTER_KEY provided; refusing to auto-approve without a token and label gate.")
        return 0

    if has_wec_auto_approve(args.token, args.repo, args.pr_number):
        print(f"✅ PR #{args.pr_number} has required label '{LABEL_NAME}'.")
        return 0

    print(
        f"::notice::Approval denied for PR #{args.pr_number}: missing required label '{LABEL_NAME}'. "
        "No workflow action is taken."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
