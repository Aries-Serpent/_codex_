#!/usr/bin/env python3
"""Read-only exact-SHA merge gate for Copilot-managed pull requests.

This gate checks current-SHA AI review, required checks, branch freshness,
merge method, mergeability, and sub-PR/promotion readiness.  It only performs
GET requests; ``--execute`` runs the read-only gate and never merges or mutates
GitHub state.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Callable, Iterable, Mapping, Sequence

GITHUB_API = "https://api.github.com"
DEFAULT_REPO = "Aries-Serpent/_codex_"
MERGE_METHODS = frozenset({"merge", "squash", "rebase"})
DEFAULT_REQUIRED_CHECKS = (
    "premerge-triage-gate / triage-gate",
    "agentic-diff-guard / deterministic-diff-guard",
)
AI_LOGIN_PATTERN = re.compile(r"(copilot|github-copilot|coding-agent)", re.IGNORECASE)
SHA_PATTERN = re.compile(r"^[0-9a-fA-F]{7,40}$")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalize_sha(value: object) -> str:
    if not isinstance(value, str):
        return ""
    sha = value.strip().lower()
    return sha if re.fullmatch(r"^[0-9a-f]{40}$", sha) else ""


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _is_ai_login(login: object) -> bool:
    if not isinstance(login, str):
        return False
    return login.strip().lower() in {
        "github-copilot[bot]",
        "copilot-swe-agent[bot]",
        "cognitive-brain[bot]",
    }


def _review_commit_id(review: Mapping[str, Any]) -> str:
    commit_id = review.get("commit_id")
    if isinstance(commit_id, str):
        return commit_id
    commit = _mapping(review.get("commit"))
    commit_id = commit.get("oid")
    return commit_id if isinstance(commit_id, str) else ""


def _review_author(review: Mapping[str, Any]) -> str:
    user = _mapping(review.get("user"))
    login = user.get("login")
    if isinstance(login, str):
        return login
    author = _mapping(review.get("author"))
    login = author.get("login")
    return login if isinstance(login, str) else ""


def _pr_head_sha(pr: Mapping[str, Any]) -> str:
    head = _mapping(pr.get("head"))
    for key in ("sha", "oid", "headRefOid"):
        value = head.get(key) or pr.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _pr_head_ref(pr: Mapping[str, Any]) -> str:
    head = _mapping(pr.get("head"))
    for key in ("ref", "headRefName"):
        value = head.get(key) or pr.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _pr_head_owner(pr: Mapping[str, Any]) -> str:
    head = _mapping(pr.get("head"))
    repo = _mapping(head.get("repo"))
    full_name = repo.get("full_name")
    if isinstance(full_name, str) and "/" in full_name:
        return full_name.split("/", 1)[0]
    owner = _mapping(repo.get("owner"))
    login = owner.get("login")
    if isinstance(login, str):
        return login
    owner = _mapping(head.get("owner"))
    login = owner.get("login")
    return login if isinstance(login, str) else ""


def _pr_base_ref(pr: Mapping[str, Any]) -> str:
    base = _mapping(pr.get("base"))
    for key in ("ref", "baseRefName"):
        value = base.get(key) or pr.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def check_current_sha_ai_review(
    pr: Mapping[str, Any],
    reviews: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None,
    sha: str | None = None,
    unresolved_review_threads: int = 0,
) -> dict[str, Any]:
    """Require an APPROVED AI review bound to the exact pull-request SHA."""

    head_sha = _normalize_sha(sha) or _normalize_sha(_pr_head_sha(pr))
    if not head_sha:
        return {
            "pass": False,
            "approved": False,
            "head_sha": "",
            "reviewer": None,
            "reason": "current pull-request SHA unavailable",
        }

    if isinstance(reviews, Mapping):
        review_payload = reviews
        if "nodes" in review_payload:
            nodes = _mapping(review_payload["nodes"])
            raw_reviews = nodes.get("nodes", [])
        elif "reviews" in review_payload:
            raw_reviews = review_payload["reviews"]
        else:
            raw_reviews = []
    else:
        raw_reviews = reviews or []

    matching: list[dict[str, Any]] = []
    for item in raw_reviews:
        if not isinstance(item, Mapping):
            continue
        review_sha = _normalize_sha(_review_commit_id(item))
        login = _review_author(item)
        state = str(item.get("state") or "").strip().upper()
        if not review_sha:
            continue
        sha_matches = review_sha == head_sha
        if sha_matches and state == "APPROVED" and _is_ai_login(login):
            matching.append({"login": login, "commit_id": review_sha, "state": state})

    if type(unresolved_review_threads) is not int or unresolved_review_threads < 0:
        return {
            "pass": False,
            "approved": False,
            "head_sha": head_sha,
            "reviewer": None,
            "reason": "invalid unresolved review-thread count",
        }
    if unresolved_review_threads > 0:
        return {
            "pass": False,
            "approved": False,
            "head_sha": head_sha,
            "reviewer": None,
            "reason": f"unresolved review threads: {unresolved_review_threads}",
        }

    if not matching:
        return {
            "pass": False,
            "approved": False,
            "head_sha": head_sha,
            "reviewer": None,
            "reason": "no APPROVED AI review is bound to the current SHA",
        }

    reviewer = matching[-1]["login"]
    return {
        "pass": True,
        "approved": True,
        "head_sha": head_sha,
        "reviewer": reviewer,
        "reason": "exact-SHA AI approval found",
    }


def current_sha_ai_review_pass(
    pr: Mapping[str, Any],
    reviews: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None,
    sha: str | None = None,
) -> bool:
    return bool(check_current_sha_ai_review(pr, reviews, sha).get("pass"))


def _check_name(check: Mapping[str, Any]) -> str:
    for key in ("name", "context", "description", "job_name"):
        value = check.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _check_conclusion(check: Mapping[str, Any]) -> str:
    for key in ("conclusion", "result", "state", "status"):
        value = check.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().upper()
    return ""


def _normalize_rollup(check_rollup: object) -> list[Mapping[str, Any]]:
    if isinstance(check_rollup, Mapping):
        rollup = check_rollup
        for key in ("statusCheckRollup", "check_runs", "checks", "contexts"):
            value = rollup.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, Mapping)]
            if isinstance(value, Mapping):
                nodes = value.get("nodes")
                if isinstance(nodes, list):
                    return [item for item in nodes if isinstance(item, Mapping)]
        return []
    if isinstance(check_rollup, Sequence) and not isinstance(check_rollup, (str, bytes)):
        return [item for item in check_rollup if isinstance(item, Mapping)]
    return []


def _required_names(required_checks: object) -> list[str]:
    if isinstance(required_checks, str):
        return [required_checks] if required_checks.strip() else []
    if isinstance(required_checks, Mapping):
        return [str(name) for name in required_checks if isinstance(name, str) and name]
    if isinstance(required_checks, Sequence) and not isinstance(required_checks, (str, bytes)):
        names: list[str] = []
        for item in required_checks:
            if isinstance(item, str) and item:
                names.append(item)
            elif isinstance(item, Mapping):
                name = _check_name(item)
                if name:
                    names.append(name)
        return names
    return []


def check_required_checks(
    check_rollup: object,
    required_checks: object = None,
) -> dict[str, Any]:
    """Require every named check to be terminal success/neutral/skipped."""

    checks = _normalize_rollup(check_rollup)
    names = _required_names(required_checks)

    if isinstance(check_rollup, Mapping):
        required_contexts = check_rollup.get("required_contexts")
        if (
            not names
            and isinstance(required_contexts, Sequence)
            and not isinstance(required_contexts, (str, bytes))
        ):
            names = [str(name) for name in required_contexts]

    if not names and checks:
        names = [name for name in (_check_name(check) for check in checks) if name]
    if not names:
        return {
            "pass": False,
            "passed": 0,
            "pending": 0,
            "failed": 0,
            "missing": [],
            "reason": "required-check evidence unavailable",
        }

    by_name: dict[str, Mapping[str, Any]] = {}
    for check_item in checks:
        name = _check_name(check_item)
        if name:
            by_name[name.lower()] = check_item

    passed = 0
    pending = 0
    failed = 0
    missing: list[str] = []
    failures: list[str] = []

    for name in names:
        check: Mapping[str, Any] | None = by_name.get(name.lower())
        if check is None:
            for check_name, candidate in by_name.items():
                if name.lower() in check_name or check_name in name.lower():
                    check = candidate
                    break
        if check is None:
            missing.append(name)
            continue

        conclusion = _check_conclusion(check)
        status = str(check.get("status") or "").strip().upper()
        if conclusion in {"SUCCESS", "NEUTRAL", "SKIPPED", "PASS", "PASSED"}:
            passed += 1
        elif status in {
            "QUEUED",
            "IN_PROGRESS",
            "WAITING",
            "PENDING",
            "REQUESTED",
        } or conclusion in {
            "",
            "PENDING",
            "QUEUED",
        }:
            pending += 1
        else:
            failed += 1
            failures.append(name)

    ready = not missing and not pending and failed == 0
    reason = "all required checks pass" if ready else "required checks missing, pending, or failed"
    return {
        "pass": ready,
        "passed": passed,
        "pending": pending,
        "failed": failed,
        "missing": missing,
        "failures": failures,
        "required": names,
        "reason": reason,
    }


def required_checks_pass(check_rollup: object, required_checks: object = None) -> bool:
    return bool(check_required_checks(check_rollup, required_checks).get("pass"))


def check_branch_freshness(
    pr: Mapping[str, Any] | None = None,
    compare: Mapping[str, Any] | bool | str | None = None,
) -> dict[str, Any]:
    """Require evidence that the PR head is not behind or divergent."""

    pr = pr or {}
    if isinstance(compare, bool):
        return {
            "pass": compare,
            "behind_by": 0 if compare else None,
            "ahead_by": None,
            "status": "up-to-date" if compare else "unknown",
            "reason": "branch freshness supplied by caller" if compare else "branch is not fresh",
        }
    if isinstance(compare, str):
        status = compare.strip().lower()
        ready = status in {"identical", "ahead", "even", "clean", "up-to-date"}
        return {
            "pass": ready,
            "behind_by": 0 if ready else None,
            "ahead_by": None,
            "status": status,
            "reason": (
                "branch is fresh" if ready else f"branch freshness status is {status or 'unknown'}"
            ),
        }

    if isinstance(compare, Mapping):
        status = str(compare.get("status") or "").strip().lower()
        behind_by = compare.get("behind_by")
        ahead_by = compare.get("ahead_by")
        try:
            behind_count = int(behind_by) if behind_by is not None else None
        except (TypeError, ValueError):
            behind_count = None
        try:
            ahead_count = int(ahead_by) if ahead_by is not None else None
        except (TypeError, ValueError):
            ahead_count = None

        if status in {"behind", "diverged", "dirty", "unknown"}:
            ready = False
        elif behind_count is not None and behind_count > 0:
            ready = False
        else:
            ready = status in {"identical", "ahead", "even", "clean", "up-to-date"}
            if not ready and behind_count == 0:
                ready = status == ""

        return {
            "pass": ready,
            "behind_by": behind_count,
            "ahead_by": ahead_count,
            "status": status or "unknown",
            "reason": "branch is fresh" if ready else "branch is behind or freshness is unverified",
        }

    caller_status = pr.get("branch_status")
    if isinstance(caller_status, str):
        return check_branch_freshness(pr, caller_status)

    freshness = pr.get("branch_freshness")
    if freshness is None:
        pass
    elif isinstance(freshness, (bool, str, Mapping)):
        return check_branch_freshness(pr, freshness)

    return {
        "pass": False,
        "behind_by": None,
        "ahead_by": None,
        "status": "unknown",
        "reason": "branch freshness evidence unavailable",
    }


def branch_is_fresh(pr: Mapping[str, Any] | None = None, compare: object = None) -> bool:
    if compare is None or isinstance(compare, (Mapping, bool, str)):
        return bool(check_branch_freshness(pr, compare).get("pass"))
    return False


def validate_merge_method(
    method: str,
    repository: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate the selected merge method against the repo allowlist."""

    normalized = method.strip().lower() if isinstance(method, str) else ""
    if normalized not in MERGE_METHODS:
        return {
            "pass": False,
            "method": normalized,
            "reason": f"unsupported merge method: {normalized or 'empty'}",
        }

    repository = repository or {}
    capability_key = f"allow_{normalized}_merge"
    if capability_key in repository and repository[capability_key] is not True:
        return {
            "pass": False,
            "method": normalized,
            "reason": f"repository does not allow {normalized} merge",
        }

    return {"pass": True, "method": normalized, "reason": "merge method is allowed"}


def merge_method_pass(method: str, repository: Mapping[str, Any] | None = None) -> bool:
    return bool(validate_merge_method(method, repository).get("pass"))


def check_sub_pr_promotion_readiness(
    pr: Mapping[str, Any],
    mode: str | None = None,
) -> dict[str, Any]:
    """Require the repository's sub-PR or promotion branch contract."""

    head_ref = _pr_head_ref(pr)
    base_ref = _pr_base_ref(pr)
    normalized_mode = (mode or "").strip().lower().replace("-", "_")

    if not normalized_mode:
        if base_ref == "0D_base_" and head_ref.startswith(
            ("copilot/sub-pr-", "copilot/session-", "copilot/")
        ):
            normalized_mode = "sub_pr"
        elif base_ref == "main" and head_ref == "0D_base_":
            normalized_mode = "promotion"

    draft = pr.get("draft") is True
    head_owner = _pr_head_owner(pr)
    if head_owner and head_owner.lower() != "aries-serpent":
        return {
            "pass": False,
            "mode": normalized_mode or "unknown",
            "head": head_ref,
            "base": base_ref,
            "reason": f"fork head owner is not authorized: {head_owner}",
        }
    if draft:
        return {
            "pass": False,
            "mode": normalized_mode or "unknown",
            "head": head_ref,
            "base": base_ref,
            "reason": "draft pull requests are not promotion-ready",
        }

    if normalized_mode in {"sub_pr", "sub-pr", "subpr"}:
        ready = base_ref == "0D_base_" and head_ref.startswith(
            ("copilot/sub-pr-", "copilot/session-", "copilot/")
        )
        reason = (
            "sub-PR targets 0D_base_ with a Copilot branch"
            if ready
            else ("sub-PR requires base=0D_base_ and a copilot/ head branch")
        )
    elif normalized_mode in {"promotion", "promote"}:
        ready = base_ref == "main" and head_ref == "0D_base_"
        reason = (
            "promotion PR targets main from 0D_base_"
            if ready
            else ("promotion requires base=main and head=0D_base_")
        )
    else:
        ready = False
        reason = "readiness mode is unknown or branch contract does not match"

    return {
        "pass": ready,
        "mode": normalized_mode or "unknown",
        "head": head_ref,
        "base": base_ref,
        "reason": reason,
    }


def sub_pr_promotion_ready(pr: Mapping[str, Any], mode: str | None = None) -> bool:
    return bool(check_sub_pr_promotion_readiness(pr, mode).get("pass"))


def _mergeability_pass(pr: Mapping[str, Any]) -> dict[str, Any]:
    state = str(pr.get("state") or pr.get("reviewDecision") or "").strip().upper()
    mergeable = pr.get("mergeable")
    mergeable_state = (
        str(pr.get("mergeable_state") or pr.get("mergeStateStatus") or "").strip().upper()
    )

    if state and state not in {"OPEN", "MERGEABLE", ""}:
        return {
            "pass": False,
            "mergeable": mergeable,
            "mergeable_state": mergeable_state,
            "reason": f"pull request state is {state.lower()}",
        }

    if mergeable is False:
        return {
            "pass": False,
            "mergeable": mergeable,
            "mergeable_state": mergeable_state,
            "reason": "GitHub reports the pull request as unmergeable",
        }

    normalized_state = mergeable_state.lower()
    if normalized_state in {"dirty", "blocked", "unknown", "behind", "diverged"}:
        return {
            "pass": False,
            "mergeable": mergeable,
            "mergeable_state": mergeable_state,
            "reason": f"mergeable state is {normalized_state}",
        }

    if mergeable == "CONFLICTING" or mergeable == False:
        return {
            "pass": False,
            "mergeable": mergeable,
            "mergeable_state": mergeable_state,
            "reason": "mergeability evidence denies merge",
        }

    clean = (
        mergeable is True
        or mergeable == "MERGEABLE"
        or normalized_state in {"clean", "stable", "has_hooks"}
    )
    if not clean:
        return {
            "pass": False,
            "mergeable": mergeable,
            "mergeable_state": mergeable_state,
            "reason": "mergeability evidence is unavailable or not clean",
        }
    return {
        "pass": True,
        "mergeable": mergeable,
        "mergeable_state": mergeable_state,
        "reason": "pull request is mergeable",
    }


def evaluate_merge_gate(
    pr: Mapping[str, Any],
    reviews: Sequence[Mapping[str, Any]] | Mapping[str, Any] | None = None,
    check_rollup: object = None,
    compare: Mapping[str, Any] | bool | str | None = None,
    merge_method: str = "squash",
    mode: str | None = None,
    sha: str | None = None,
    required_checks: object = None,
    unresolved_review_threads: int = 0,
    repository: Mapping[str, Any] | None = None,
    execute: bool = False,
) -> dict[str, Any]:
    """Evaluate all merge gates without performing any GitHub mutation."""

    ai_review = check_current_sha_ai_review(pr, reviews, sha, unresolved_review_threads)
    required = check_required_checks(check_rollup, required_checks)
    freshness = check_branch_freshness(pr, compare)
    method = validate_merge_method(merge_method, repository)
    readiness = check_sub_pr_promotion_readiness(pr, mode)
    mergeability = _mergeability_pass(pr)

    checks = {
        "current_sha_ai_review": ai_review,
        "required_checks": required,
        "branch_freshness": freshness,
        "merge_method": method,
        "sub_pr_promotion_readiness": readiness,
        "mergeability": mergeability,
    }
    failures = [name for name, result in checks.items() if not result.get("pass")]
    ready = not failures
    head_sha = ai_review.get("head_sha") or _normalize_sha(_pr_head_sha(pr))

    return {
        "schema_version": 1,
        "ready": ready,
        "passed": ready,
        "blocked": not ready,
        "failures": failures,
        "blocked_reasons": [
            f"{name}: {checks[name].get('reason', 'gate failed')}" for name in failures
        ],
        "head_sha": head_sha,
        "merge_method": method,
        "current_sha_ai_review": ai_review,
        "ai_review": ai_review,
        "required_checks": required,
        "required_check": required,
        "branch_freshness": freshness,
        "sub_pr_promotion_readiness": readiness,
        "promotion_readiness": readiness,
        "mergeability": mergeability,
        "execute_requested": bool(execute),
        "mode": "execute-read-only" if execute else "read-only",
        "mutations_attempted": [],
        "checked_at": utc_now(),
    }


def run_merge_gate(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return evaluate_merge_gate(*args, **kwargs)


def _resolve_token(explicit: str | None = None) -> str:
    if explicit:
        return explicit.strip()
    for name in ("CODEX_MASTER_KEY", "CODEX_BACKUP_KEY", "GH_TOKEN", "GITHUB_TOKEN"):
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return ""


def _github_get(
    repo: str,
    path: str,
    token: str,
) -> object:
    """GET one GitHub API resource; this function has no mutation verbs."""

    if not token:
        raise RuntimeError("GitHub token unavailable; fail closed")
    url = path if path.startswith("https://") else f"{GITHUB_API}/{path.lstrip('/')}"
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != "api.github.com":
        raise RuntimeError("GitHub API URL validation failed")
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"GitHub API GET failed with HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"GitHub API GET failed: {type(exc).__name__}") from exc


class CopilotMergeGate:
    """Read-only evidence collector and evaluator for one pull request."""

    def __init__(
        self,
        repo: str = DEFAULT_REPO,
        pr: int | str | None = None,
        token: str | None = None,
        merge_method: str = "squash",
        mode: str | None = None,
        required_checks: Sequence[str] | None = None,
        execute: bool = False,
        http_get: Callable[[str, str, str], object] | None = None,
    ) -> None:
        if not isinstance(repo, str) or not re.fullmatch(r"[^/\s]+/[^/\s]+", repo):
            raise ValueError("repo must use owner/name format")
        if pr is None:
            raise ValueError("PR number is required")
        try:
            pr_number = int(pr)
        except (TypeError, ValueError) as exc:
            raise ValueError("PR number must be an integer") from exc
        if pr_number < 1:
            raise ValueError("PR number must be positive")
        self.repo = repo
        self.pr_number = pr_number
        self.token = _resolve_token(token)
        self.merge_method = merge_method
        self.mode = mode
        self.required_checks = list(required_checks or ())
        self.execute = bool(execute)
        self.http_get = http_get or _github_get

    def evaluate(self, sha: str | None = None) -> dict[str, Any]:
        if not self.token:
            return evaluate_merge_gate(
                {},
                reviews=[],
                check_rollup=None,
                merge_method=self.merge_method,
                mode=self.mode,
                sha=sha,
                required_checks=self.required_checks or None,
                execute=self.execute,
            )

        try:
            pr_payload = self.http_get(
                self.repo,
                f"repos/{self.repo}/pulls/{self.pr_number}",
                self.token,
            )
            if not isinstance(pr_payload, Mapping):
                raise RuntimeError("pull-request evidence is not a mapping")
            pr = dict(pr_payload)

            head_sha = sha or _pr_head_sha(pr)
            if not head_sha:
                return evaluate_merge_gate(
                    pr,
                    reviews=[],
                    check_rollup=None,
                    merge_method=self.merge_method,
                    mode=self.mode,
                    sha=sha,
                    required_checks=self.required_checks or None,
                    execute=self.execute,
                )

            reviews_payload = self.http_get(
                self.repo,
                f"repos/{self.repo}/pulls/{self.pr_number}/reviews?per_page=100",
                self.token,
            )
            reviews = reviews_payload if isinstance(reviews_payload, list) else []

            check_payload = self.http_get(
                self.repo,
                f"repos/{self.repo}/commits/{head_sha}/check-runs?per_page=100",
                self.token,
            )
            check_runs: list[Mapping[str, Any]] = []
            if isinstance(check_payload, Mapping):
                raw_check_runs = check_payload.get("check_runs")
                if isinstance(raw_check_runs, list):
                    check_runs = [item for item in raw_check_runs if isinstance(item, Mapping)]

            status_payload = self.http_get(
                self.repo,
                f"repos/{self.repo}/commits/{head_sha}/status",
                self.token,
            )
            status_checks: list[Mapping[str, Any]] = []
            if isinstance(status_payload, Mapping):
                raw_statuses = status_payload.get("statuses")
                if isinstance(raw_statuses, list):
                    status_checks = [item for item in raw_statuses if isinstance(item, Mapping)]

            normalized_status_checks: list[dict[str, Any]] = []
            for check in status_checks:
                normalized_status_checks.append(
                    {
                        "name": check.get("context"),
                        "status": check.get("status"),
                        "conclusion": check.get("state"),
                    }
                )

            check_rollup: list[Mapping[str, Any]] = list(check_runs)
            check_rollup.extend(normalized_status_checks)

            compare: Mapping[str, Any] | None = None
            base_ref = _pr_base_ref(pr)
            base_sha_payload = pr.get("base")
            base_sha = ""
            if isinstance(base_sha_payload, Mapping):
                base_sha = str(base_sha_payload.get("sha") or "")
            compare_ref = base_sha or base_ref
            if compare_ref:
                compare_payload = self.http_get(
                    self.repo,
                    f"repos/{self.repo}/compare/{urllib.parse.quote(str(compare_ref), safe='')}...{urllib.parse.quote(str(head_sha), safe='')}",
                    self.token,
                )
                if isinstance(compare_payload, Mapping):
                    compare = compare_payload

            required_checks = self.required_checks or None
            return evaluate_merge_gate(
                pr,
                reviews=reviews,
                check_rollup={"check_runs": check_rollup} if check_rollup else None,
                compare=compare,
                merge_method=self.merge_method,
                mode=self.mode,
                sha=head_sha,
                required_checks=required_checks,
                execute=self.execute,
            )
        except (RuntimeError, ValueError, KeyError) as exc:
            report = evaluate_merge_gate(
                {},
                reviews=[],
                check_rollup=None,
                merge_method=self.merge_method,
                mode=self.mode,
                sha=sha,
                required_checks=self.required_checks or None,
                execute=self.execute,
            )
            report["blocked_reasons"] = [f"evidence unavailable: {exc}"]
            report["failures"] = ["evidence_unavailable"]
            report["ready"] = False
            report["passed"] = False
            report["blocked"] = True
            return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=DEFAULT_REPO, help="owner/repo")
    parser.add_argument("--pr", "--pr-number", dest="pr", type=int, required=True)
    parser.add_argument("--sha", "--head-sha", dest="sha", default=None)
    parser.add_argument("--merge-method", choices=sorted(MERGE_METHODS), default="squash")
    parser.add_argument("--mode", choices=("sub_pr", "sub-pr", "promotion"), default=None)
    parser.add_argument("--required-check", action="append", default=[])
    parser.add_argument(
        "--execute", action="store_true", help="run read-only gate checks (does not merge)"
    )
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    parser.add_argument(
        "--token", default=None, help="explicit token; environment token resolution is preferred"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        gate = CopilotMergeGate(
            repo=args.repo,
            pr=args.pr,
            token=args.token,
            merge_method=args.merge_method,
            mode=args.mode,
            required_checks=args.required_check,
            execute=args.execute,
        )
        report = gate.evaluate(args.sha)
    except (ValueError, RuntimeError) as exc:
        report = {
            "ready": False,
            "passed": False,
            "blocked": True,
            "failures": ["gate_configuration_error"],
            "blocked_reasons": [str(exc)],
            "execute_requested": bool(getattr(args, "execute", False)),
            "mode": "execute-read-only" if getattr(args, "execute", False) else "read-only",
            "mutations_attempted": [],
            "checked_at": utc_now(),
        }

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("Copilot Merge Gate")
        print(f"Status: {'READY' if report['ready'] else 'BLOCKED'}")
        print(f"Mode: {report['mode']}")
        print(f"Mutations attempted: {len(report['mutations_attempted'])}")
        for reason in report.get("blocked_reasons", []):
            print(f"- {reason}")

    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
