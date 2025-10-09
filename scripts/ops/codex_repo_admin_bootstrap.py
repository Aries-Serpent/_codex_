#!/usr/bin/env python3
"""Harden a GitHub repository without touching workflows."""

from __future__ import annotations

import argparse
import base64
import importlib.util
import json
import os
import sys
import types
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, MutableMapping, Optional, Sequence, Tuple
from urllib.parse import quote as _url_quote

from src.integrations.github_app_auth import assert_online_allowlisted, build_auth_header_from_env

_requests_spec = importlib.util.find_spec("requests")
if _requests_spec is None:

    def _missing(*args, **kwargs):  # type: ignore[unused-arg]
        raise RuntimeError(
            "requests library not available; install requests to enable network calls"
        )

    requests = types.SimpleNamespace(  # type: ignore[assignment]
        request=_missing,
        post=_missing,
        get=_missing,
        put=_missing,
        patch=_missing,
        Session=lambda: types.SimpleNamespace(request=_missing, close=lambda: None),
        utils=types.SimpleNamespace(quote=_url_quote),
    )
else:  # pragma: no cover - exercised in integration
    import requests  # type: ignore


API_VERSION = os.getenv("GITHUB_API_VERSION", "2022-11-28")
DEFAULT_API_BASE = os.getenv("GITHUB_API_BASE", "https://api.github.com")
USER_AGENT = "codex-ops-repo-admin-bootstrap/2.0"


def _mask(secret: str, keep: int = 4) -> str:
    if not secret:
        return "<empty>"
    s = secret.strip()
    if len(s) <= keep:
        return "*" * len(s)
    return f"{'*' * (len(s) - keep)}{s[-keep:]}"


@dataclass
class GitHubSession:
    """Small wrapper around :mod:`requests` with default headers."""

    auth_header: str
    api_base: str = DEFAULT_API_BASE

    def __post_init__(self) -> None:
        if not self.auth_header:
            raise ValueError("auth_header is required")
        if not self.auth_header.lower().startswith(("token ", "bearer ", "basic ")):
            self.auth_header = f"token {self.auth_header}"
        session_factory = getattr(requests, "Session", None)
        self._session = session_factory() if callable(session_factory) else None

    def __enter__(self) -> "GitHubSession":  # pragma: no cover - trivial
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - trivial
        self.close()

    def close(self) -> None:
        if self._session and hasattr(self._session, "close"):
            self._session.close()

    # Methods that tests can patch
    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, object] | None = None,
        json_body: Mapping[str, object] | None = None,
        data: object | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: float = 15,
    ):
        url = self._url(path)
        hdrs = self._headers(headers)
        if self._session is not None:
            return self._session.request(
                method,
                url,
                params=params,
                json=json_body,
                data=data,
                headers=hdrs,
                timeout=timeout,
            )
        return requests.request(
            method,
            url,
            params=params,
            json=json_body,
            data=data,
            headers=hdrs,
            timeout=timeout,
        )

    def _headers(self, extra: Mapping[str, str] | None = None) -> Mapping[str, str]:
        base = {
            "Authorization": self.auth_header,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": USER_AGENT,
        }
        if extra:
            merged = dict(base)
            merged.update(extra)
            return merged
        return base

    def _url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return f"{self.api_base.rstrip('/')}/{path.lstrip('/')}"

    def get(self, path: str, *, params: Mapping[str, object] | None = None, timeout: float = 15):
        return self._request("GET", path, params=params, timeout=timeout)

    def put(
        self,
        path: str,
        *,
        json: Mapping[str, object] | None = None,
        data: object | None = None,
        timeout: float = 15,
    ):
        return self._request("PUT", path, json_body=json, data=data, timeout=timeout)

    def post(
        self,
        path: str,
        *,
        json: Mapping[str, object] | None = None,
        data: object | None = None,
        timeout: float = 15,
    ):
        return self._request("POST", path, json_body=json, data=data, timeout=timeout)

    def patch(
        self,
        path: str,
        *,
        json: Mapping[str, object] | None = None,
        data: object | None = None,
        timeout: float = 15,
    ):
        return self._request("PATCH", path, json_body=json, data=data, timeout=timeout)


def _default_repo_settings(preset: str = "default") -> Dict[str, object]:
    squash_only = preset in {"default", "strict"}
    allow_auto_merge = True if preset == "default" else False
    return {
        "allow_squash_merge": squash_only,
        "allow_merge_commit": not squash_only and preset != "strict",
        "allow_rebase_merge": False if preset != "relaxed" else True,
        "delete_branch_on_merge": True,
        "allow_auto_merge": allow_auto_merge,
        "squash_merge_commit_message": "PR_BODY",
        "squash_merge_commit_title": "PR_TITLE",
        # Best-effort features (eligible plans only)
        "security_and_analysis": {
            "advanced_security": {"status": "enabled"},
            "secret_scanning": {"status": "enabled"},
            "secret_scanning_push_protection": {"status": "enabled"},
        },
    }


def _branch_protection_template(
    branch: str,
    required_approvals: int,
    status_checks: Sequence[str],
) -> Dict[str, object]:
    return {
        "branch": branch,
        "required_status_checks": {
            "strict": True,
            "contexts": list(status_checks),
        },
        "enforce_admins": True,
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": True,
            "required_approving_review_count": max(required_approvals, 0),
            "require_last_push_approval": True,
        },
        "restrictions": None,
        "required_linear_history": True,
        "allow_force_pushes": False,
        "allow_deletions": False,
        "block_creations": True,
        "required_conversation_resolution": True,
        "lock_branch": False,
        "allow_fork_syncing": False,
    }


def plan_labels(
    owner: str, repo: str, labels: Sequence[Mapping[str, Any]]
) -> List[Tuple[str, Dict[str, Any]]]:
    ops: List[Tuple[str, Dict[str, Any]]] = []
    for label in labels:
        name = label["name"]
        payload = {
            "name": name,
            "color": label.get("color", "ededed").lstrip("#"),
            "description": label.get("description", ""),
        }
        ops.append(("upsert", payload))
    return ops


def apply_repo_settings(
    session: GitHubSession, owner: str, repo: str, payload: Mapping[str, Any]
) -> None:
    resp = session.patch(f"/repos/{owner}/{repo}", json=payload)
    if resp.status_code // 100 != 2:
        if resp.status_code in (403, 404):
            raise SystemExit(f"Repo settings update forbidden: {resp.status_code} {resp.text}")
        raise SystemExit(f"Repo settings update failed: {resp.status_code} {resp.text}")


def enable_vulnerability_alerts(session: GitHubSession, owner: str, repo: str) -> str:
    resp = session.put(f"/repos/{owner}/{repo}/vulnerability-alerts")
    if resp.status_code in (204, 202):
        return "enabled"
    if resp.status_code in (403, 404):
        return "skipped"
    raise SystemExit(f"Enable vulnerability-alerts failed: {resp.status_code} {resp.text}")


def set_automated_security_fixes(
    session: GitHubSession, owner: str, repo: str, enable: bool
) -> str:
    path = f"/repos/{owner}/{repo}/automated-security-fixes"
    resp = session.put(path) if enable else session._request("DELETE", path)
    if resp.status_code in (204, 202):
        return "enabled" if enable else "disabled"
    if resp.status_code in (403, 404):
        return "skipped"
    raise SystemExit(
        f"{'Enable' if enable else 'Disable'} automated-security-fixes failed: {resp.status_code} {resp.text}"
    )


def get_default_branch(session: GitHubSession, owner: str, repo: str) -> str:
    resp = session.get(f"/repos/{owner}/{repo}")
    if resp.status_code != 200:
        alt = session._request("GET", f"/repos/{owner}")
        if alt.status_code == 200:
            resp = alt
        else:
            raise SystemExit(f"Get repository failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data.get("default_branch") or "main"


def apply_branch_protection(
    session: GitHubSession,
    owner: str,
    repo: str,
    branch: str,
    config: Mapping[str, Any],
) -> None:
    payload = dict(config)
    payload.pop("branch", None)
    resp = session.put(f"/repos/{owner}/{repo}/branches/{branch}/protection", json=payload)
    if resp.status_code // 100 != 2:
        raise SystemExit(f"Branch protection failed: {resp.status_code} {resp.text}")


def _list_labels(
    session: GitHubSession, owner: str, repo: str
) -> MutableMapping[str, Mapping[str, Any]]:
    resp = session.get(f"/repos/{owner}/{repo}/labels")
    if resp.status_code == 200:
        return {item["name"].lower(): item for item in resp.json()}
    if resp.status_code // 100 == 2:
        return {}
    if resp.status_code in (403, 404):
        return {}
    raise SystemExit(f"List labels failed: {resp.status_code} {resp.text}")


def ensure_labels(
    session: GitHubSession,
    owner: str,
    repo: str,
    labels: Sequence[Mapping[str, Any]],
) -> List[Mapping[str, object]]:
    existing = _list_labels(session, owner, repo)
    results: List[Mapping[str, object]] = []
    for label in labels:
        name = label["name"]
        payload = {
            "name": name,
            "color": label.get("color", "ededed").lstrip("#"),
            "description": label.get("description", ""),
        }
        if name.lower() in existing:
            resp = session.patch(
                f"/repos/{owner}/{repo}/labels/{_url_quote(name, safe='')}",
                json={"new_name": name, **payload},
            )
            if resp.status_code // 100 != 2:
                raise SystemExit(f"Update label {name} failed: {resp.status_code} {resp.text}")
            results.append({"name": name, "status": "updated"})
        else:
            resp = session.post(f"/repos/{owner}/{repo}/labels", json=payload)
            if resp.status_code // 100 != 2:
                raise SystemExit(f"Create label {name} failed: {resp.status_code} {resp.text}")
            results.append({"name": name, "status": "created"})
    return results


def ensure_files(
    session: GitHubSession,
    owner: str,
    repo: str,
    files: Sequence[Mapping[str, Any]],
    *,
    branch: str,
    author: str,
) -> List[Mapping[str, object]]:
    results: List[Mapping[str, object]] = []
    for file in files:
        path = file["path"]
        message = file.get("message", f"chore: ensure {path} present")
        content = file["content"]
        url = f"/repos/{owner}/{repo}/contents/{path}"
        resp = session.get(url, params={"ref": branch})
        sha: Optional[str]
        if resp.status_code == 200:
            sha = resp.json().get("sha")
        elif resp.status_code == 404:
            sha = None
        else:
            raise SystemExit(f"Fetch contents {path} failed: {resp.status_code} {resp.text}")
        body: Dict[str, Any] = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
            "branch": branch,
            "committer": {"name": author, "email": "ops@codex.local"},
        }
        if sha:
            body["sha"] = sha
        resp = session.put(url, json=body)
        if resp.status_code not in (200, 201):
            raise SystemExit(f"Upsert contents {path} failed: {resp.status_code} {resp.text}")
        results.append({"path": path, "status": "updated" if sha else "created"})
    return results


def _load_labels(path: Optional[Path]) -> List[Mapping[str, Any]]:
    if path and path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []


def _load_codeowners(path: Optional[Path]) -> List[Mapping[str, Any]]:
    if path and path.exists():
        return [
            {
                "path": ".github/CODEOWNERS",
                "message": "chore: ensure CODEOWNERS present",
                "content": path.read_text(encoding="utf-8"),
            }
        ]
    return []


def _build_plan(args: argparse.Namespace) -> Dict[str, Any]:
    branch = args.branch or "main"
    labels = _load_labels(args.labels_json)
    files = _load_codeowners(args.codeowners)
    plan: Dict[str, Any] = {
        "target": {"owner": args.owner, "repo": args.repo, "branch": branch},
        "preset": args.preset,
        "repo_settings": _default_repo_settings(args.preset),
        "branch_protection": _branch_protection_template(
            branch, args.required_approvals, args.status_check
        ),
        "labels": labels,
        "files": files,
    }
    return plan


def _assert_online_allowed() -> None:
    assert_online_allowlisted()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Standardize GitHub repo settings (no workflows). Dry-run by default."
    )
    parser.add_argument("--owner", required=True, help="Repository owner/org")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--branch", help="Protected branch (if omitted, detect from repo default)")
    parser.add_argument(
        "--detect-default-branch",
        action="store_true",
        help="Auto-detect default branch via REST API",
    )
    parser.add_argument(
        "--preset",
        default="default",
        choices=["default", "strict", "relaxed"],
        help="Policy preset toggling merge behavior and auto-merge",
    )
    parser.add_argument(
        "--required-approvals",
        type=int,
        default=1,
        help="Required PR approvals (branch protection)",
    )
    parser.add_argument(
        "--status-check",
        action="append",
        default=[],
        help="Required status check context (repeatable)",
    )
    parser.add_argument(
        "--labels-json",
        type=Path,
        help="Path to labels.json (optional)",
    )
    parser.add_argument(
        "--codeowners",
        type=Path,
        help="Path to CODEOWNERS template (optional)",
    )
    parser.add_argument(
        "--author",
        default="Codex Admin Bot",
        help="Commit author for hygiene files",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Execute changes (omit to print plan only)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose logs (masked token tails + status)",
    )
    parser.add_argument(
        "--dependabot-updates",
        action="store_true",
        help="Enable Dependabot security updates (best-effort)",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    plan = _build_plan(args)
    if not args.apply:
        print(json.dumps({"dry_run": True, "plan": plan}, indent=2, ensure_ascii=False))
        return 0

    _assert_online_allowed()
    auth_header = build_auth_header_from_env()
    if args.verbose:
        print(f"[auth] Using header: {_mask(auth_header)}", file=sys.stderr)

    with GitHubSession(auth_header=auth_header) as gh:
        branch = args.branch
        if args.detect_default_branch and not branch:
            branch = get_default_branch(gh, args.owner, args.repo)
        branch = branch or plan["target"]["branch"]
        plan["target"]["branch"] = branch
        plan["branch_protection"]["branch"] = branch
        if args.verbose:
            print(f"[info] target branch: {branch}", file=sys.stderr)

        apply_repo_settings(gh, args.owner, args.repo, plan["repo_settings"])

        va_state = enable_vulnerability_alerts(gh, args.owner, args.repo)
        dep_state = "skipped"
        if args.dependabot_updates:
            dep_state = set_automated_security_fixes(gh, args.owner, args.repo, enable=True)

        apply_branch_protection(
            gh,
            args.owner,
            args.repo,
            branch,
            plan["branch_protection"],
        )

        labels_result = ensure_labels(gh, args.owner, args.repo, plan["labels"])
        files_result = ensure_files(
            gh,
            args.owner,
            args.repo,
            plan["files"],
            branch=branch,
            author=args.author,
        )

    result = {
        "applied": True,
        "vulnerability_alerts": va_state,
        "dependabot_security_updates": dep_state,
        "labels": labels_result,
        "files": files_result,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nAborted by user.", file=sys.stderr)
        sys.exit(130)
