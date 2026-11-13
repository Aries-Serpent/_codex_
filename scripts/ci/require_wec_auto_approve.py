#!/usr/bin/env python3
"""Require the wec:auto-approve label before an approval-capable workflow can act."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LABEL_NAME = "wec:auto-approve"
ONE_SESSION_LABEL_NAME = "wec:auto-approve-once"
DEFAULT_TTL_HOURS = 1
Request = Callable[..., tuple[int, Any]]


def _gh(method: str, path: str, token: str, body: dict[str, Any] | None = None) -> tuple[int, Any]:
    if __package__:
        from .approve_pending_runs import _gh as package_request

        return package_request(method, path, token, body)
    else:
        from approve_pending_runs import _gh as script_request

        return script_request(method, path, token, body)


def _parse_activation_time(value: Any) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        parsed = datetime.fromisoformat(value)
        return parsed.astimezone(timezone.utc) if parsed.tzinfo is not None else None
    except ValueError:
        return None


def label_valid(
    token: str,
    repo: str,
    pr_number: str | int,
    data: dict[str, Any],
    request: Request,
    *,
    ttl_hours: int = DEFAULT_TTL_HOURS,
) -> bool:
    """Bind a once grant to its latest GitHub label activation, never PR creation."""
    labels = data.get("labels")
    if not isinstance(labels, list) or not all(
        isinstance(label, dict) and isinstance(label.get("name"), str) for label in labels
    ):
        raise RuntimeError("Malformed approval labels")
    label_names = {label["name"] for label in labels}
    if LABEL_NAME in label_names:
        return True
    if ONE_SESSION_LABEL_NAME not in label_names:
        return False

    if type(ttl_hours) is not int or not 0 < ttl_hours <= DEFAULT_TTL_HOURS:
        return False
    if once_activation(token, repo, pr_number, request, ttl_hours=ttl_hours) is None:
        return False
    status, current = request("GET", f"/repos/{repo}/issues/{pr_number}", token)
    return status == 200 and isinstance(current, dict) and current.get("labels") == labels


def once_activation(
    token: str,
    repo: str,
    pr_number: str | int,
    request: Request,
    *,
    ttl_hours: int = DEFAULT_TTL_HOURS,
) -> dict[str, Any] | None:
    """Return the current verified activation, including its immutable event ID."""
    if type(ttl_hours) is not int or not 0 < ttl_hours <= DEFAULT_TTL_HOURS:
        return None
    latest: dict[str, Any] | None = None
    seen: set[int] = set()
    for page in range(1, 11):
        status, events = request(
            "GET", f"/repos/{repo}/issues/{pr_number}/events?per_page=100&page={page}", token
        )
        if status != 200 or not isinstance(events, list) or len(events) > 100:
            raise RuntimeError("Approval activation history unavailable")
        for event in events:
            if not isinstance(event, dict):
                raise RuntimeError("Malformed approval activation history")
            event_id = event.get("id")
            if type(event_id) is not int or event_id <= 0 or event_id in seen:
                raise RuntimeError("Invalid or repeated approval event identity")
            seen.add(event_id)
            if (
                event.get("event") in {"labeled", "unlabeled"}
                and (event.get("label") or {}).get("name") == ONE_SESSION_LABEL_NAME
                and (latest is None or event_id > latest["id"])
            ):
                latest = event
        if len(events) < 100:
            break
    else:
        raise RuntimeError("Approval activation inspection budget exhausted")
    if latest is None or latest["event"] != "labeled":
        return None
    actor = latest.get("actor")
    if not isinstance(actor, dict) or actor.get("type") != "User" or not actor.get("login"):
        return None
    activated = _parse_activation_time(latest.get("created_at"))
    if activated is None:
        return None
    age_hours = (datetime.now(timezone.utc) - activated).total_seconds() / 3600
    if not 0 <= age_hours <= ttl_hours:
        return None
    return latest


def has_wec_auto_approve(
    token: str, repo: str, pr_number: int, ttl_hours: int = DEFAULT_TTL_HOURS
) -> bool:
    status, data = _gh("GET", f"/repos/{repo}/issues/{pr_number}", token)
    if status != 200 or not isinstance(data, dict):
        raise RuntimeError("Approval label inspection unavailable")
    return label_valid(token, repo, pr_number, data, _gh, ttl_hours=ttl_hours)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pr-number", type=int, required=True, help="Pull request number to validate"
    )
    parser.add_argument(
        "--repo",
        default=os.environ.get("REPO") or os.environ.get("GITHUB_REPOSITORY", ""),
        help="Repository slug, e.g. owner/repo",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("GH_TOKEN")
        or os.environ.get("CODEX_MASTER_KEY")
        or os.environ.get("CODEX_BACKUP_KEY")
        or "",
        help="GitHub token",
    )
    args = parser.parse_args()

    def finish(code: int, rule: str) -> int:
        Path("approval-decision.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "decisions": [
                        {
                            "rule": rule,
                            "pr": args.pr_number,
                            "head_sha": os.environ.get("HEAD_SHA") or None,
                            "outcome": "authorized" if code == 0 else "denied",
                        }
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return code

    if not args.repo:
        print("::error::REPO is required to validate wec:auto-approve.")
        return finish(1, "missing-repository")
    if not args.token:
        print(
            "::notice::No GH_TOKEN/CODEX_MASTER_KEY provided; refusing to auto-approve without a token and label gate."
        )
        return finish(1, "missing-token")

    try:
        authorized = has_wec_auto_approve(args.token, args.repo, args.pr_number)
    except (OSError, ValueError, RuntimeError):
        print("::error::Approval label or activation evidence could not be verified.")
        return finish(1, "inspection-error")
    if authorized:
        print(f"✅ PR #{args.pr_number} has required label '{LABEL_NAME}'.")
        return finish(0, "label-present")

    print(
        f"::error::Approval denied for PR #{args.pr_number}: missing required label '{LABEL_NAME}'. "
        "Add the label to enable auto-approval."
    )
    return finish(1, "missing-or-expired-label")


if __name__ == "__main__":
    raise SystemExit(main())
