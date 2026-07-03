#!/usr/bin/env python3
"""
_webhook_signature_validator.py — GitHub webhook payload signature validation.

Provides utilities for validating GitHub webhook signatures using HMAC-SHA256.

Key design principles
---------------------
Constant-Time Comparison:
    All signature comparisons use hmac.compare_digest() to prevent
    timing attacks that could reveal the secret length.

Signature Formats:
    GitHub uses X-Hub-Signature-256 header (sha256=...)
    Legacy X-Hub-Signature uses sha1=... (deprecated but supported)

Payload Handling:
    The raw request body (bytes) must be used, not the parsed JSON.
    The body must include the trailing newline/whitespace as sent by GitHub.

Usage
-----
    from _webhook_signature_validator import WebhookValidator

    validator = WebhookValidator(webhook_secret="my-secret")

    # Validate incoming webhook
    is_valid = validator.validate(
        payload=request.body,
        signature=request.headers.get("X-Hub-Signature-256")
    )

    if not is_valid:
        raise SecurityError("Invalid webhook signature")
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
from typing import Any

log = logging.getLogger(__name__)

# GitHub webhook constants
GITHUB_SIGNATURE_ALGORITHM = "sha256"
GITHUB_SIGNATURE_HEADER = "X-Hub-Signature-256"
GITHUB_SIGNATURE_HEADER_LEGACY = "X-Hub-Signature"


class WebhookValidator:
    """Validator for GitHub webhook signatures."""

    def __init__(self, webhook_secret: str):
        """
        Initialize validator with webhook secret.

        Args:
            webhook_secret: Secret configured in GitHub webhook settings
        """
        self.webhook_secret = webhook_secret

    def compute_signature(
        self,
        payload: bytes,
        algorithm: str = GITHUB_SIGNATURE_ALGORITHM,
    ) -> str:
        """
        Compute HMAC-SHA256 signature of webhook payload.

        Args:
            payload: Raw request body (bytes) from webhook
            algorithm: Algorithm name ('sha256' or 'sha1')

        Returns:
            Signature string (e.g., "sha256=abc123...")
        """
        if algorithm == "sha256":
            hash_obj = hmac.new(
                self.webhook_secret.encode("utf-8"),
                payload,
                hashlib.sha256,
            )
        elif algorithm == "sha1":
            hash_obj = hmac.new(
                self.webhook_secret.encode("utf-8"),
                payload,
                hashlib.sha1,
            )
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        return f"{algorithm}={hash_obj.hexdigest()}"

    def validate(
        self,
        payload: bytes,
        signature: str | None,
        algorithm: str = GITHUB_SIGNATURE_ALGORITHM,
    ) -> bool:
        """
        Validate webhook signature using constant-time comparison.

        Args:
            payload: Raw request body (bytes)
            signature: X-Hub-Signature-256 header value
            algorithm: Algorithm to use for validation

        Returns:
            True if signature is valid, False otherwise
        """
        if not signature:
            log.warning("Missing signature header")
            return False

        computed = self.compute_signature(payload, algorithm)

        # Constant-time comparison to prevent timing attacks
        is_valid = hmac.compare_digest(computed, signature)

        if not is_valid:
            log.warning(
                "Webhook signature mismatch (expected %s..., got %s...)",
                computed[:20],
                signature[:20],
            )

        return is_valid

    def parse_payload(self, payload: bytes) -> dict[str, Any]:
        """
        Parse webhook payload JSON.

        Args:
            payload: Raw request body (bytes)

        Returns:
            Parsed JSON as dict

        Raises:
            ValueError: If JSON is invalid
        """
        try:
            return json.loads(payload.decode("utf-8"))
        except Exception as err:
            raise ValueError(f"Failed to parse webhook payload: {err}") from err

    def validate_and_parse(
        self,
        payload: bytes,
        signature: str | None,
        algorithm: str = GITHUB_SIGNATURE_ALGORITHM,
    ) -> tuple[bool, dict[str, Any]]:
        """
        Validate signature and parse payload in one call.

        Args:
            payload: Raw request body (bytes)
            signature: X-Hub-Signature-256 header value
            algorithm: Algorithm to use

        Returns:
            Tuple of (is_valid, parsed_json)
        """
        is_valid = self.validate(payload, signature, algorithm)
        parsed = self.parse_payload(payload)
        return is_valid, parsed


class WebhookSignatureError(Exception):
    """Raised when webhook signature validation fails."""

    pass


def validate_webhook_signature(
    payload: bytes,
    signature: str | None,
    secret: str,
    algorithm: str = GITHUB_SIGNATURE_ALGORITHM,
) -> bool:
    """
    Standalone function to validate webhook signature.

    Args:
        payload: Raw request body (bytes)
        signature: X-Hub-Signature-256 header value
        secret: Webhook secret
        algorithm: Algorithm to use

    Returns:
        True if valid, False otherwise
    """
    validator = WebhookValidator(secret)
    return validator.validate(payload, signature, algorithm)


def validate_webhook_signature_strict(
    payload: bytes,
    signature: str | None,
    secret: str,
    algorithm: str = GITHUB_SIGNATURE_ALGORITHM,
) -> None:
    """
    Validate webhook signature and raise on failure.

    Args:
        payload: Raw request body (bytes)
        signature: X-Hub-Signature-256 header value
        secret: Webhook secret
        algorithm: Algorithm to use

    Raises:
        WebhookSignatureError: If signature is invalid
    """
    if not validate_webhook_signature(payload, signature, secret, algorithm):
        raise WebhookSignatureError("Invalid webhook signature")


# GitHub Webhook Event Types (for reference)
GITHUB_WEBHOOK_EVENTS = [
    "push",
    "pull_request",
    "pull_request_review",
    "pull_request_review_comment",
    "issues",
    "issue_comment",
    "create",
    "delete",
    "fork",
    "gollum",
    "page_build",
    "public",
    "release",
    "repository",
    "status",
    "watch",
    "workflow_run",
    "workflow_job",
    "check_run",
    "check_suite",
    "deployment",
    "deployment_status",
    "discussion",
    "discussion_comment",
    "label",
    "member",
    "milestone",
    "organization",
    "packages",
    "registry_package",
    "repository_dispatch",
    "branch_protection_rule",
    "merge_group",
]
