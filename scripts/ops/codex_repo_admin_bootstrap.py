"""
Codex Repo Admin Bootstrap
 - Standardize GitHub repo settings without enabling any workflows.
 - Idempotent; defaults are safe; dry-run by default.

Requires:
  CODEX_NET_MODE=online_allowlist
  CODEX_ALLOWLIST_HOSTS=api.github.com
  GITHUB_APP_ID, GITHUB_APP_INSTALLATION_ID, and App private key (see mint script).
"""

from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
from typing import Iterable, Mapping

from scripts.ops.codex_mint_tokens_per_run import (  # type: ignore
    _assert_online_allowed,
    _mint_app_jwt,
    TokenScope,
    GitHubSession,
    create_installation_access_token,
)

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "templates" / "github_repo_baseline"


def _default_repo_settings() -> dict:
    # Conservative, squash-only, delete merged branches, enable security knobs when available.
    return {
        "allow_squash_merge": True,
        "allow_merge_commit": False,
        "allow_rebase_merge": False,
        "delete_branch_on_merge": True,
        "allow_auto_merge": True,
        "squash_merge_commit_message": "PR_BODY",
        "squash_merge_commit_title": "PR_TITLE",
        "security_and_analysis": {
            "advanced_security": {"status": "enabled"},
            "secret_scanning": {"status": "enabled"},
            "secret_scanning_push_protection": {"status": "enabled"},
            # vulnerability alerts are separate, see _enable_repo_feature()
        },
    }


def _default_branch_protection() -> dict:
    # Minimal, safe protection for 'main' (no required status checks by default).
    return {
        "required_status_checks": None,  # or {"strict": False, "contexts": []}
        "enforce_admins": True,
        "required_pull_request_reviews": {
            "required_approvals": 1,
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": True,
        },
        "restrictions": None,
        "required_conversation_resolution": True,
        # Note: required signatures & linear history have separate endpoints; omitted by default.
    }


def _default_labels() -> list[dict]:
    return [
        {"name": "type:bug", "color": "d73a4a", "description": "Something isn't working"},
        {"name": "type:feature", "color": "a2eeef", "description": "New feature or request"},
        {"name": "type:docs", "color": "0075ca", "description": "Documentation updates"},
        {"name": "prio:high", "color": "b60205", "description": "High priority"},
        {"name": "good first issue", "color": "7057ff", "description": "Good for newcomers"},
    ]


def _plan_templates() -> dict[str, Path]:
    files: dict[str, Path] = {}
    for p in TEMPLATES.rglob("*"):
        if p.is_file():
            rel = p.relative_to(TEMPLATES)
            # map to repository path (.github/*)
            repo_path = Path(".github") / rel
            files[str(repo_path)] = p
    return files


def _put_json(
    session: GitHubSession, url: str, payload: Mapping[str, object], expected: int = 200
) -> dict:
    resp = session.request("PUT", url, json=payload)
    if resp.status_code != expected:
        raise SystemExit(f"PUT {url} failed: {resp.status_code} {resp.text}")
    return resp.json() if resp.text else {}


def _patch_json(
    session: GitHubSession, url: str, payload: Mapping[str, object], ok: set[int] = {200}
) -> dict:
    resp = session.request("PATCH", url, json=payload)
    if resp.status_code not in ok:
        raise SystemExit(f"PATCH {url} failed: {resp.status_code} {resp.text}")
    return resp.json() if resp.text else {}


def _enable_repo_feature(session: GitHubSession, owner: str, repo: str, feature: str) -> None:
    # vulnerability alerts on: PUT /repos/{owner}/{repo}/vulnerability-alerts
    url = f"/repos/{owner}/{repo}/{feature}"
    resp = session.put(url)
    if resp.status_code not in (204, 202):  # 202 for async enable on some hosts
        # Best-effort: ignore 404/403 if not available for the plan/org tier.
        if resp.status_code not in (403, 404):
            raise SystemExit(f"Enable {feature} failed: {resp.status_code} {resp.text}")


def apply_repo_settings(
    session: GitHubSession, owner: str, repo: str, settings: Mapping[str, object]
) -> dict:
    return _patch_json(session, f"/repos/{owner}/{repo}", settings)


def apply_branch_protection(
    session: GitHubSession, owner: str, repo: str, branch: str, rules: Mapping[str, object]
) -> dict:
    return _put_json(
        session, f"/repos/{owner}/{repo}/branches/{branch}/protection", rules, expected=200
    )


def ensure_labels(
    session: GitHubSession, owner: str, repo: str, labels: Iterable[Mapping[str, str]]
) -> dict:
    # Build a plan by diffing existing labels; create missing, update mismatched colors/descriptions.
    existing = session.get(f"/repos/{owner}/{repo}/labels").json()
    by_name = {l["name"].lower(): l for l in (existing or [])}
    plan: dict[str, list] = {"create": [], "update": []}
    for label in labels:
        name = label["name"]
        cur = by_name.get(name.lower())
        if not cur:
            plan["create"].append(label)
        else:
            needs = {}
            if cur.get("color", "").lower() != label["color"].lower():
                needs["color"] = label["color"]
            if (cur.get("description") or "") != label.get("description", ""):
                needs["description"] = label.get("description", "")
            if needs:
                plan["update"].append({"name": name, **needs})
    # Apply
    for lbl in plan["create"]:
        resp = session.post(f"/repos/{owner}/{repo}/labels", json=lbl)
        if resp.status_code not in (201, 200):
            raise SystemExit(f"Create label {lbl['name']} failed: {resp.status_code} {resp.text}")
    for upd in plan["update"]:
        name = upd.pop("name")
        resp = session.patch(f"/repos/{owner}/{repo}/labels/{name}", json=upd)
        if resp.status_code != 200:
            raise SystemExit(f"Update label {name} failed: {resp.status_code} {resp.text}")
    return plan


def ensure_repo_files(
    session: GitHubSession,
    owner: str,
    repo: str,
    files: dict[str, Path],
    branch: str,
    author: str,
) -> dict:
    # Uses "Create or update file contents" API; creates missing files only.
    plan = {"create": [], "skip": []}
    for repo_path, src in files.items():
        # stat if exists
        stat = session.get(f"/repos/{owner}/{repo}/contents/{repo_path}?ref={branch}")
        if stat.status_code == 200:
            plan["skip"].append(repo_path)
            continue
        if stat.status_code not in (404, 200):
            raise SystemExit(f"Probe {repo_path} failed: {stat.status_code} {stat.text}")
        content = base64.b64encode(src.read_bytes()).decode("ascii")
        payload = {
            "message": f"codex: bootstrap {repo_path}",
            "content": content,
            "branch": branch,
            "committer": {"name": author, "email": "codex@example"},
        }
        resp = session.put(f"/repos/{owner}/{repo}/contents/{repo_path}", json=payload)
        if resp.status_code not in (201, 200):
            raise SystemExit(f"Create {repo_path} failed: {resp.status_code} {resp.text}")
        plan["create"].append(repo_path)
    return plan


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Standardize GitHub repo settings (no workflows). Dry-run by default."
    )
    p.add_argument("--owner", required=True)
    p.add_argument("--repo", required=True)
    p.add_argument("--branch", default="main")
    p.add_argument(
        "--apply", action="store_true", help="Execute changes. Omit to just print the plan."
    )
    p.add_argument(
        "--with-templates",
        action="store_true",
        help="Also push CODEOWNERS + PR/Issue templates (.github).",
    )
    p.add_argument(
        "--codeowners", default="@Aries-Serpent/codex-admins", help="Default CODEOWNERS entry."
    )
    p.add_argument("--author", default="Codex Admin Bot", help="Commit author for hygiene files.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    owner, repo, branch = args.owner, args.repo, args.branch

    # Plan
    plan = {
        "repo_settings": _default_repo_settings(),
        "branch_protection": _default_branch_protection(),
        "labels": _default_labels(),
        "templates": list(_plan_templates().keys()) if args.with_templates else [],
        "target": {"owner": owner, "repo": repo, "branch": branch},
        "apply": bool(args.apply),
    }

    if not args.apply:
        print(json.dumps({"dry_run": True, "plan": plan}, indent=2, ensure_ascii=False))
        return 0

    _assert_online_allowed()
    app_id = os.getenv("GITHUB_APP_ID")
    inst_id = os.getenv("GITHUB_APP_INSTALLATION_ID")
    if not app_id or not inst_id:
        raise SystemExit("Missing GITHUB_APP_ID / GITHUB_APP_INSTALLATION_ID")

    # Mint JWT -> Installation token
    app_jwt = _mint_app_jwt(app_id)
    with GitHubSession(f"Bearer {app_jwt}") as app_session:
        token_data = create_installation_access_token(app_session, inst_id, TokenScope(tuple(), {}))
    installation_token = token_data.get("token", "")
    if not installation_token:
        raise SystemExit("No installation token minted.")

    # Apply via Installation token
    with GitHubSession(f"token {installation_token}") as gh:
        apply_repo_settings(gh, owner, repo, plan["repo_settings"])
        # Best-effort security toggles that require special endpoints
        _enable_repo_feature(gh, owner, repo, "vulnerability-alerts")
        apply_branch_protection(gh, owner, repo, branch, plan["branch_protection"])
        label_result = ensure_labels(gh, owner, repo, plan["labels"])
        file_result = {}
        if args.with_templates:
            # Prepare CODEOWNERS file dynamically if absent in template set.
            codeowners = TEMPLATES / "CODEOWNERS"
            if not codeowners.exists():
                codeowners.write_text(f"* {args.codeowners}\n", encoding="utf-8")
            file_result = ensure_repo_files(gh, owner, repo, _plan_templates(), branch, args.author)

    print(
        json.dumps(
            {"applied": True, "labels": label_result, "files": file_result},
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
