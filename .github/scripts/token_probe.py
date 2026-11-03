#!/usr/bin/env python3
"""Read-only health checks for the repository's configured GitHub credentials."""

from __future__ import annotations

import html
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from http.client import HTTPException
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

_REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_EXPIRY_WARNING_WINDOW = timedelta(hours=24)


class _RejectRedirectHandler(HTTPRedirectHandler):
    def redirect_request(
        self, req: Request, fp: Any, code: int, msg: str, headers: Any, newurl: str
    ) -> None:
        return None


@dataclass(frozen=True)
class ProbeResult:
    status: str
    usable_now: bool
    token_type: str
    scopes: str
    rate_remaining: str
    expires_at: str
    repository_permissions: str


def _token_type(token: str) -> str:
    for prefix, label in (
        ("github_pat_", "fine-grained-pat"),
        ("ghp_", "classic-pat"),
        ("gho_", "oauth-token"),
        ("ghs_", "github-app-installation"),
        ("ghu_", "github-app-user"),
    ):
        if token.startswith(prefix):
            return label
    return "unknown"


def _parse_expiration(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = re.sub(r"\s+UTC$", "+00:00", value.strip())
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = parsedate_to_datetime(normalized)
        except (TypeError, ValueError, OverflowError):
            return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _repository_permissions(payload: Any) -> str:
    if not isinstance(payload, dict):
        return "unknown"
    permissions = payload.get("permissions")
    if not isinstance(permissions, dict):
        return "not-reported"
    granted = sorted(key for key, value in permissions.items() if isinstance(value, bool) and value)
    return ", ".join(granted) or "none-reported"


def probe_token(
    token: str | None,
    repository: str,
    *,
    opener: Callable[..., Any] | None = None,
    now: datetime | None = None,
) -> ProbeResult:
    """Check repository read access; this does not verify downstream write rights."""
    if not token:
        return ProbeResult(
            "missing", False, "none", "not-reported", "unknown", "unknown", "unknown"
        )
    if not _REPO_PATTERN.fullmatch(repository) or any(
        component in {".", ".."} for component in repository.split("/")
    ):
        raise ValueError("GITHUB_REPOSITORY must be an owner/repository slug")

    request = Request(
        f"https://api.github.com/repos/{repository}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + token,
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    open_url = opener or build_opener(_RejectRedirectHandler()).open
    response = None
    status_code: int
    try:
        response = open_url(request, timeout=10)
        status_code = int(response.status)
        headers = response.headers
        body = response.read()
    except HTTPError as exc:
        status_code = int(exc.code)
        headers = exc.headers or {}
        body = b""
        response = exc
    except (HTTPException, URLError, TimeoutError, OSError, ValueError):
        return ProbeResult(
            "probe-error",
            False,
            _token_type(token),
            "not-reported",
            "unknown",
            "unknown",
            "unknown",
        )
    finally:
        if response is not None:
            response.close()

    rate_remaining = headers.get("X-RateLimit-Remaining", "unknown").strip()
    scopes = headers.get("X-OAuth-Scopes", "not-reported").strip() or "not-reported"
    expiration_header = headers.get("GitHub-Authentication-Token-Expiration")
    expiration = _parse_expiration(expiration_header)
    expires_at = expiration_header.strip() if expiration_header else "not-reported"
    permissions = "unknown"

    if status_code == 200:
        try:
            payload = json.loads(body) if body else {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            payload = None
        permissions = _repository_permissions(payload)
        if not isinstance(payload, dict):
            status, usable = "invalid-response", False
        elif rate_remaining == "0":
            status, usable = "rate-limited", False
        elif expiration is not None:
            current_time = now or datetime.now(timezone.utc)
            current_time = current_time.astimezone(timezone.utc)
            if expiration <= current_time:
                status, usable = "expired", False
            elif expiration - current_time <= _EXPIRY_WARNING_WINDOW:
                status, usable = "expiring-soon", True
            else:
                status, usable = "repository-readable", True
        else:
            status, usable = "repository-readable", True
    elif status_code == 401:
        status, usable = "unauthorized", False
    elif status_code == 403 and rate_remaining == "0":
        status, usable = "rate-limited", False
    elif status_code == 403:
        status, usable = "forbidden", False
    elif status_code == 404:
        status, usable = "not-found-or-inaccessible", False
    elif status_code == 429:
        status, usable = "rate-limited", False
    elif status_code >= 500:
        status, usable = "service-unavailable", False
    else:
        status, usable = "unexpected-http-status", False

    return ProbeResult(
        status,
        usable,
        _token_type(token),
        scopes,
        rate_remaining,
        expires_at,
        permissions,
    )


def _markdown_cell(value: str) -> str:
    sanitized = value.replace("\r", " ").replace("\n", " ")
    escaped = html.escape(sanitized, quote=False)
    for character in ("\\", "`", "|", "[", "]", "(", ")", "!", "*", "_", "#"):
        escaped = escaped.replace(character, f"\\{character}")
    return escaped


def render_summary(results: dict[str, ProbeResult], *, require_both: bool) -> tuple[str, bool]:
    master = results["CODEX_MASTER_KEY"]
    backup = results["CODEX_BACKUP_KEY"]
    passed = (
        master.usable_now and backup.usable_now
        if require_both
        else master.usable_now or backup.usable_now
    )
    rows = [
        "## GitHub credential probe",
        "",
        "> This probe verifies repository metadata read access only. It does not",
        "> verify write permissions or authorize downstream actions.",
        "",
        "| Credential | Probe status | Type hint | OAuth scopes | Rate remaining | Expiration | Repository permissions |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for name in ("CODEX_MASTER_KEY", "CODEX_BACKUP_KEY"):
        result = results[name]
        rows.append(
            "| "
            + " | ".join(
                _markdown_cell(value)
                for value in (
                    name,
                    result.status,
                    result.token_type,
                    result.scopes,
                    result.rate_remaining,
                    result.expires_at,
                    result.repository_permissions,
                )
            )
            + " |"
        )
    rows.extend(
        [
            "",
            f"**Required policy:** {'both configured keys' if require_both else 'at least one usable key'}",
            f"**Result:** {'PASS' if passed else 'FAIL'}",
        ]
    )
    return "\n".join(rows) + "\n", passed


def main() -> int:
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    require_both = os.environ.get("REQUIRE_BOTH_KEYS", "true").lower() == "true"
    results = {
        "CODEX_MASTER_KEY": probe_token(os.environ.get("CODEX_MASTER_KEY"), repository),
        "CODEX_BACKUP_KEY": probe_token(os.environ.get("CODEX_BACKUP_KEY"), repository),
    }
    summary, passed = render_summary(results, require_both=require_both)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with Path(summary_path).open("a", encoding="utf-8") as stream:
            stream.write(summary)
    else:
        sys.stdout.write(summary)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
