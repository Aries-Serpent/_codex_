#!/usr/bin/env python3
"""Shared GitHub write-capable helper for repo mutation workflows.

This module centralizes the write-vs-read decision so that workflows that post
comments, create discussions, dispatch workflows, or update repo variables run
through the same token selection policy instead of ad hoc inline fallbacks.

The repository contract is:
- read-only actions may use github.token
- write-capable actions must resolve through the canonical token chain
- variable/workflow/admin writes must prefer CODEX_MASTER_KEY or CODEX_BACKUP_KEY
- PR/issue comment posting may use GH_TOKEN when appropriate, but must be
  explicit and auditable
"""

from __future__ import annotations

import os
from typing import Any

from scripts.ci._token_resolver import get_token, get_token_scope, validate_token_scope

CANONICAL_WRITE_CHAIN = (
    "CODEX_MASTER_KEY",
    "CODEX_BACKUP_KEY",
    "GH_TOKEN",
    "GITHUB_TOKEN",
)

WRITE_OPERATIONS = {
    "repo_variable_write",
    "workflow_dispatch",
    "workflow_approval",
    "admin_write",
    "discussion_write",
    "issue_comment",
    "pr_comment",
    "discussion_comment",
}

ADMIN_WRITE_OPERATIONS = {
    "repo_variable_write",
    "workflow_dispatch",
    "workflow_approval",
    "admin_write",
}

COMMENT_OPERATIONS = {"pr_comment", "issue_comment", "discussion_comment"}
DISCUSSION_OPERATIONS = {"discussion_write", "discussion_comment"}


def _effective_token_chain(operation: str) -> tuple[str, ...]:
    """Return the allowable token sources for a given operation."""
    if operation in ADMIN_WRITE_OPERATIONS:
        return ("CODEX_MASTER_KEY", "CODEX_BACKUP_KEY")
    if operation in DISCUSSION_OPERATIONS:
        return CANONICAL_WRITE_CHAIN
    if operation in COMMENT_OPERATIONS:
        return CANONICAL_WRITE_CHAIN
    return CANONICAL_WRITE_CHAIN


def resolve_github_token(operation: str = "pr_comment") -> tuple[str, str]:
    """Resolve the correct token for a GitHub operation.

    Args:
        operation: A write/read capability name such as "pr_comment",
            "discussion_comment", "workflow_dispatch", or "repo_variable_write".

    Returns:
        A tuple of (token_value, token_source_name).

    Raises:
        ValueError: when the operation requires a stronger token than the current
            environment provides.
    """
    allowed = _effective_token_chain(operation)
    for env_name in allowed:
        candidate = os.environ.get(env_name, "").strip()
        if candidate:
            if operation in ADMIN_WRITE_OPERATIONS:
                is_valid, message = validate_token_scope(candidate, ["repo", "workflow", "actions:write"])
                if is_valid:
                    return candidate, env_name
                raise ValueError(
                    f"Operation '{operation}' requires a write-capable token; "
                    f"{env_name} is insufficient: {message}"
                )
            return candidate, env_name

    if operation in ADMIN_WRITE_OPERATIONS:
        raise ValueError(
            "No write-capable GitHub token is available. "
            "Set CODEX_MASTER_KEY or CODEX_BACKUP_KEY."
        )
    if os.environ.get("GITHUB_TOKEN"):
        return os.environ["GITHUB_TOKEN"], "GITHUB_TOKEN"
    raise ValueError(
        f"No token available for GitHub operation '{operation}'. "
        "Set CODEX_MASTER_KEY, CODEX_BACKUP_KEY, GH_TOKEN, or GITHUB_TOKEN."
    )


def build_auth_headers(token: str | None = None) -> dict[str, str]:
    """Return GitHub REST authorization headers for a given token."""
    token = token or resolve_github_token()[0]
    return {
        "Authorization": f"******",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
        "User-Agent": "codex-github-write-helper/1.0",
    }


def build_pr_comment_request(repo: str, issue_number: int, body: str) -> dict[str, Any]:
    """Return a canonical PR/issue comment payload for GitHub REST API calls."""
    return {
        "method": "POST",
        "path": f"/repos/{repo}/issues/{issue_number}/comments",
        "payload": {"body": body},
        "operation": "pr_comment",
    }


def build_discussion_comment_request(discussion_id: str, body: str) -> dict[str, Any]:
    """Return a canonical GraphQL discussion comment payload."""
    return {
        "operation": "discussion_comment",
        "graphql": {
            "query": """
mutation AddDiscussionComment($discussionId: ID!, $body: String!) {
  addDiscussionComment(input: {discussionId: $discussionId, body: $body}) {
    comment { id url body }
  }
}
""",
            "variables": {"discussionId": discussion_id, "body": body},
        },
    }


def build_workflow_dispatch_request(repo: str, workflow_id: str, ref: str, **inputs: Any) -> dict[str, Any]:
    """Return a canonical workflow-dispatch payload consistent with this repo."""
    payload = {"ref": ref, "inputs": inputs}
    return {
        "method": "POST",
        "path": f"/repos/{repo}/actions/workflows/{workflow_id}/dispatches",
        "payload": payload,
        "operation": "workflow_dispatch",
    }


def ensure_write_capability(operation: str, token: str | None = None) -> tuple[str, str]:
    """Validate that the selected token is acceptable for the operation."""
    if token is None:
        token, source = resolve_github_token(operation)
    else:
        source = os.environ.get("GH_TOKEN") if os.environ.get("GH_TOKEN") == token else None
        if source is None:
            source = os.environ.get("CODEX_MASTER_KEY") if os.environ.get("CODEX_MASTER_KEY") == token else None
        if source is None:
            source = os.environ.get("CODEX_BACKUP_KEY") if os.environ.get("CODEX_BACKUP_KEY") == token else None
        if source is None:
            source = os.environ.get("GITHUB_TOKEN") if os.environ.get("GITHUB_TOKEN") == token else None
        if source is None:
            source = "custom"

    if operation in ADMIN_WRITE_OPERATIONS and source not in {"CODEX_MASTER_KEY", "CODEX_BACKUP_KEY"}:
        raise ValueError(
            f"Operation '{operation}' requires CODEX_MASTER_KEY or CODEX_BACKUP_KEY; "
            f"got source '{source}'."
        )
    return token, source


__all__ = [
    "ADMIN_WRITE_OPERATIONS",
    "COMMENT_OPERATIONS",
    "CANONICAL_WRITE_CHAIN",
    "build_auth_headers",
    "build_discussion_comment_request",
    "build_pr_comment_request",
    "build_workflow_dispatch_request",
    "ensure_write_capability",
    "resolve_github_token",
]
