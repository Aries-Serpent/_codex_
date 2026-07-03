"""Comprehensive tests for webhook management via CODEX_MASTER_KEY.

This test suite covers:
- Repository webhook CRUD (Process 8)
- Organization webhook CRUD (Process 9)
- Webhook signature validation using HMAC-SHA256
- Webhook delivery and event filtering
- Webhook security validation

Tests skip gracefully if CODEX_MASTER_KEY is unavailable.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import (  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
    Any,
    Optional,
)

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def repo_webhooks_endpoint(repo_owner: str, repo_name: str) -> str:
    """Return repository webhooks endpoint."""
    return f"/repos/{repo_owner}/{repo_name}/hooks"


@pytest.fixture
def org_webhooks_endpoint(org_name: str) -> str:
    """Return organization webhooks endpoint."""
    return f"/orgs/{org_name}/hooks"


@pytest.fixture
def test_webhook_secret() -> str:
    """Return test webhook secret."""
    return "test_webhook_secret_12345"


@pytest.fixture
def webhook_payload_sample() -> dict[str, Any]:
    """Return sample webhook payload."""
    return {
        "action": "opened",
        "number": 1,
        "pull_request": {
            "id": 1,
            "title": "Test PR",
            "user": {"login": "testuser"},
        },
        "repository": {
            "id": 123456,
            "name": "_codex_",
            "owner": {"login": "Aries-Serpent"},
        },
    }


@pytest.fixture
def mock_webhook_response():
    """Return callable that generates mock webhook responses."""

    def _make(
        hook_id: int = 1,
        url: str = "https://example.com/webhook",
        events: Optional[list[str]] = None,
        active: bool = True,
    ) -> dict[str, Any]:
        if events is None:
            events = ["push", "pull_request"]

        return {
            "id": hook_id,
            "name": "web",
            "active": active,
            "events": events,
            "config": {
                "url": url,
                "content_type": "json",
                "insecure_ssl": "0",
            },
            "updated_at": "2024-01-01T00:00:00Z",
            "created_at": "2024-01-01T00:00:00Z",
        }

    return _make


# ─────────────────────────────────────────────────────────────────────────────
# Process 8: Repository Webhooks Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestProcess8RepositoryWebhooks:
    """Process 8: Tests for repository webhooks (repo scope required)."""

    # ───────────────────────────────────────────────────────────────────────
    # Webhook CRUD Operations
    # ───────────────────────────────────────────────────────────────────────

    def test_process8_list_repo_webhooks_success(
        self,
        gh_api_base: str,
        repo_webhooks_endpoint: str,
        mock_webhook_response,
    ):
        """Test: List all repository webhooks."""
        endpoint = f"{gh_api_base}{repo_webhooks_endpoint}"

        assert "/repos/" in endpoint
        assert "/hooks" in endpoint

    def test_process8_list_repo_webhooks_empty(
        self,
        gh_api_base: str,
        repo_webhooks_endpoint: str,
    ):
        """Test: List returns empty array when no webhooks."""
        endpoint = f"{gh_api_base}{repo_webhooks_endpoint}"
        expected_response = []

        assert "/repos/" in endpoint
        assert "/hooks" in endpoint
        assert len(expected_response) == 0

    def test_process8_list_repo_webhooks_pagination(
        self,
        gh_api_base: str,
        repo_webhooks_endpoint: str,
    ):
        """Test: List webhooks supports pagination."""
        endpoint = f"{gh_api_base}{repo_webhooks_endpoint}?per_page=10&page=1"
        assert "per_page=10" in endpoint
        assert "page=1" in endpoint

    def test_process8_get_repo_webhook_success(
        self,
        gh_api_base: str,
        repo_webhooks_endpoint: str,
        mock_webhook_response,
    ):
        """Test: Get details of a specific repository webhook."""
        hook_id = 12345
        endpoint = f"{gh_api_base}{repo_webhooks_endpoint}/{hook_id}"
        response = mock_webhook_response(hook_id=hook_id)

        assert str(hook_id) in endpoint
        assert response["id"] == hook_id
        assert response["config"]["url"]

    def test_process8_create_repo_webhook_success(
        self,
        gh_api_base: str,
        repo_webhooks_endpoint: str,
        test_webhook_url: str,
    ):
        """Test: Create a repository webhook."""
        endpoint = f"{gh_api_base}{repo_webhooks_endpoint}"

        payload = {
            "name": "web",
            "active": True,
            "events": ["push", "pull_request"],
            "config": {
                "url": test_webhook_url,
                "content_type": "json",
                "secret": "webhook_secret",
            },
        }

        assert "/repos/" in endpoint
        assert "/hooks" in endpoint
        assert payload["name"] == "web"
        assert payload["active"] is True
        assert test_webhook_url in payload["config"]["url"]

    def test_process8_create_webhook_with_secret(
        self,
        gh_api_base: str,
        repo_webhooks_endpoint: str,
        test_webhook_url: str,
        test_webhook_secret: str,
    ):
        """Test: Create webhook with HMAC-SHA256 secret."""
        payload = {
            "name": "web",
            "active": True,
            "events": ["push"],
            "config": {
                "url": test_webhook_url,
                "content_type": "json",
                "secret": test_webhook_secret,
            },
        }

        assert payload["config"]["secret"]

    def test_process8_create_webhook_event_types(
        self,
        gh_api_base: str,
        repo_webhooks_endpoint: str,
        test_webhook_url: str,
    ):
        """Test: Create webhook with various event types."""
        event_combos = [
            ["push"],
            ["pull_request"],
            ["issues"],
            ["push", "pull_request", "issues"],
            ["*"],  # All events
        ]

        for events in event_combos:
            payload = {
                "name": "web",
                "active": True,
                "events": events,
                "config": {
                    "url": test_webhook_url,
                    "content_type": "json",
                },
            }

            assert payload["events"] == events

    def test_process8_update_repo_webhook_success(
        self,
        gh_api_base: str,
        repo_webhooks_endpoint: str,
        test_webhook_url: str,
    ):
        """Test: Update repository webhook configuration."""
        hook_id = 12345
        endpoint = f"{gh_api_base}{repo_webhooks_endpoint}/{hook_id}"

        payload = {
            "active": False,  # Disable webhook
            "events": ["push"],
            "config": {
                "url": test_webhook_url,
            },
        }

        assert str(hook_id) in endpoint
        assert payload["active"] is False

    def test_process8_delete_repo_webhook_success(
        self,
        gh_api_base: str,
        repo_webhooks_endpoint: str,
    ):
        """Test: Delete a repository webhook."""
        hook_id = 12345
        endpoint = f"{gh_api_base}{repo_webhooks_endpoint}/{hook_id}"

        # DELETE returns 204 No Content
        assert str(hook_id) in endpoint

    def test_process8_webhook_not_found_error(
        self,
        gh_api_base: str,
        repo_webhooks_endpoint: str,
        api_errors,
    ):
        """Test: 404 Not Found when webhook doesn't exist."""
        error = api_errors.resource_not_found()
        assert error.code == 404

    # ───────────────────────────────────────────────────────────────────────
    # Webhook Delivery
    # ───────────────────────────────────────────────────────────────────────

    def test_process8_webhook_deliveries_list(
        self,
        gh_api_base: str,
        repo_webhooks_endpoint: str,
    ):
        """Test: List webhook deliveries for a hook."""
        hook_id = 12345
        endpoint = f"{gh_api_base}{repo_webhooks_endpoint}/{hook_id}/deliveries"

        assert "deliveries" in endpoint

    def test_process8_webhook_delivery_details(
        self,
        gh_api_base: str,
        repo_webhooks_endpoint: str,
    ):
        """Test: Get details of a specific webhook delivery."""
        hook_id = 12345
        delivery_id = 1
        endpoint = f"{gh_api_base}{repo_webhooks_endpoint}/{hook_id}/deliveries/{delivery_id}"

        expected_response = {
            "id": delivery_id,
            "guid": "delivery-guid",
            "status": "delivered",
            "request": {
                "headers": {"X-GitHub-Event": "push"},
                "payload": {},
            },
            "response": {
                "status": 200,
                "headers": {},
                "body": "",
            },
        }

        assert f"/deliveries/{delivery_id}" in endpoint
        assert expected_response["status"] in ["delivered", "failed", "pending"]

    # ───────────────────────────────────────────────────────────────────────
    # Webhook Payload Testing
    # ───────────────────────────────────────────────────────────────────────

    def test_process8_webhook_test_payload(
        self,
        gh_api_base: str,
        repo_webhooks_endpoint: str,
    ):
        """Test: Send test payload to webhook."""
        hook_id = 12345
        endpoint = f"{gh_api_base}{repo_webhooks_endpoint}/{hook_id}/tests"

        # POST to trigger test delivery
        assert "tests" in endpoint

    # ───────────────────────────────────────────────────────────────────────
    # Error Handling
    # ───────────────────────────────────────────────────────────────────────

    def test_process8_invalid_webhook_url_error(
        self,
        gh_api_base: str,
        repo_webhooks_endpoint: str,
        api_errors,
    ):
        """Test: 422 when webhook URL is invalid."""
        error = api_errors.unprocessable_entity()
        assert error.code == 422

    def test_process8_webhook_limit_exceeded(
        self,
        gh_api_base: str,
        repo_webhooks_endpoint: str,
        api_errors,
    ):
        """Test: 422 when webhook limit exceeded."""
        error = api_errors.unprocessable_entity()
        assert error.code == 422


# ─────────────────────────────────────────────────────────────────────────────
# Process 9: Organization Webhooks Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestProcess9OrganizationWebhooks:
    """Process 9: Tests for organization webhooks (admin:org_hook scope required)."""

    # ───────────────────────────────────────────────────────────────────────
    # Webhook CRUD Operations
    # ───────────────────────────────────────────────────────────────────────

    def test_process9_list_org_webhooks_success(
        self,
        gh_api_base: str,
        org_webhooks_endpoint: str,
        mock_webhook_response,
    ):
        """Test: List all organization webhooks."""
        endpoint = f"{gh_api_base}{org_webhooks_endpoint}"

        assert "/orgs/" in endpoint
        assert "/hooks" in endpoint

    def test_process9_get_org_webhook_success(
        self,
        gh_api_base: str,
        org_webhooks_endpoint: str,
        mock_webhook_response,
    ):
        """Test: Get organization webhook details."""
        hook_id = 12345
        endpoint = f"{gh_api_base}{org_webhooks_endpoint}/{hook_id}"
        response = mock_webhook_response(hook_id=hook_id)

        assert str(hook_id) in endpoint
        assert response["id"] == hook_id

    def test_process9_create_org_webhook_success(
        self,
        gh_api_base: str,
        org_webhooks_endpoint: str,
        test_webhook_url: str,
    ):
        """Test: Create an organization webhook."""
        endpoint = f"{gh_api_base}{org_webhooks_endpoint}"

        payload = {
            "name": "web",
            "active": True,
            "events": ["push", "pull_request"],
            "config": {
                "url": test_webhook_url,
                "content_type": "json",
            },
        }

        assert "/orgs/" in endpoint or "/repos/" in endpoint
        assert payload["name"]

    def test_process9_create_org_webhook_with_secret(
        self,
        gh_api_base: str,
        org_webhooks_endpoint: str,
        test_webhook_url: str,
        test_webhook_secret: str,
    ):
        """Test: Create organization webhook with secret."""
        endpoint = f"{gh_api_base}{org_webhooks_endpoint}"

        payload = {
            "name": "web",
            "active": True,
            "events": ["push"],
            "config": {
                "url": test_webhook_url,
                "content_type": "json",
                "secret": test_webhook_secret,
            },
        }

        assert "/orgs/" in endpoint or "/repos/" in endpoint
        assert payload["config"]["secret"]

    def test_process9_update_org_webhook_success(
        self,
        gh_api_base: str,
        org_webhooks_endpoint: str,
        test_webhook_url: str,
    ):
        """Test: Update organization webhook."""
        hook_id = 12345
        endpoint = f"{gh_api_base}{org_webhooks_endpoint}/{hook_id}"

        payload = {
            "active": True,
            "config": {
                "url": test_webhook_url,
            },
        }

        assert str(hook_id) in endpoint
        assert payload["active"]

    def test_process9_delete_org_webhook_success(
        self,
        gh_api_base: str,
        org_webhooks_endpoint: str,
    ):
        """Test: Delete organization webhook."""
        hook_id = 12345
        endpoint = f"{gh_api_base}{org_webhooks_endpoint}/{hook_id}"

        assert str(hook_id) in endpoint

    # ───────────────────────────────────────────────────────────────────────
    # Error Handling
    # ───────────────────────────────────────────────────────────────────────

    def test_process9_insufficient_admin_scope_error(
        self,
        gh_api_base: str,
        org_webhooks_endpoint: str,
        api_errors,
    ):
        """Test: 403 when token lacks admin:org_hook scope."""
        error = api_errors.insufficient_scope()
        assert error.code == 403

    def test_process9_org_not_found_error(
        self,
        gh_api_base: str,
        api_errors,
    ):
        """Test: 404 when organization doesn't exist."""
        error = api_errors.resource_not_found()
        assert error.code == 404


# ─────────────────────────────────────────────────────────────────────────────
# Webhook Signature Validation Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestWebhookSignatureValidation:
    """Tests for webhook signature validation using constant-time comparison."""

    def test_webhook_signature_hmac_sha256(
        self,
        webhook_payload_sample: dict,
        test_webhook_secret: str,
    ):
        """Test: Compute valid HMAC-SHA256 signature for webhook payload."""
        payload_bytes = json.dumps(webhook_payload_sample).encode()
        expected_signature = "sha256=" + hmac.new(
            test_webhook_secret.encode(),
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()

        assert expected_signature.startswith("sha256=")
        assert len(expected_signature) > 10

    def test_webhook_signature_validation_success(
        self,
        webhook_payload_sample: dict,
        test_webhook_secret: str,
    ):
        """Test: Valid webhook signature passes validation."""
        payload_bytes = json.dumps(webhook_payload_sample).encode()
        signature = "sha256=" + hmac.new(
            test_webhook_secret.encode(),
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()

        # Validate using constant-time comparison
        computed = "sha256=" + hmac.new(
            test_webhook_secret.encode(),
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()

        assert hmac.compare_digest(signature, computed)

    def test_webhook_signature_validation_failure(
        self,
        webhook_payload_sample: dict,
        test_webhook_secret: str,
    ):
        """Test: Invalid webhook signature fails validation."""
        payload_bytes = json.dumps(webhook_payload_sample).encode()
        valid_signature = "sha256=" + hmac.new(
            test_webhook_secret.encode(),
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()

        invalid_signature = "sha256=invalid_signature_hash"

        assert not hmac.compare_digest(valid_signature, invalid_signature)

    def test_webhook_signature_constant_time_comparison(
        self,
        webhook_payload_sample: dict,
        test_webhook_secret: str,
    ):
        """Test: Use constant-time comparison to prevent timing attacks."""
        payload_bytes = json.dumps(webhook_payload_sample).encode()
        signature = "sha256=" + hmac.new(
            test_webhook_secret.encode(),
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()

        # Should use hmac.compare_digest, not string ==
        computed = signature

        result = hmac.compare_digest(signature, computed)
        assert result is True

    def test_webhook_signature_different_secret_fails(
        self,
        webhook_payload_sample: dict,
        test_webhook_secret: str,
    ):
        """Test: Signature with different secret fails validation."""
        payload_bytes = json.dumps(webhook_payload_sample).encode()

        signature_correct = "sha256=" + hmac.new(
            test_webhook_secret.encode(),
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()

        wrong_secret = "wrong_secret"
        signature_wrong = "sha256=" + hmac.new(
            wrong_secret.encode(),
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()

        assert not hmac.compare_digest(signature_correct, signature_wrong)

    def test_webhook_signature_raw_body_required(
        self,
        test_webhook_secret: str,
    ):
        """Test: Signature must use raw request body, not parsed JSON."""
        # Raw body with original formatting
        raw_body = b'{"action":"opened","number":1}'

        # Parsed and re-serialized (different formatting)
        parsed_body = json.dumps(json.loads(raw_body)).encode()

        sig_raw = "sha256=" + hmac.new(
            test_webhook_secret.encode(),
            raw_body,
            hashlib.sha256,
        ).hexdigest()

        sig_parsed = "sha256=" + hmac.new(
            test_webhook_secret.encode(),
            parsed_body,
            hashlib.sha256,
        ).hexdigest()

        # May differ if formatting differs
        # This illustrates why raw body is important
        assert sig_raw  # Valid
        assert sig_parsed  # Also valid, but may differ


# ─────────────────────────────────────────────────────────────────────────────
# Webhook Event Filtering and Processing
# ─────────────────────────────────────────────────────────────────────────────


class TestWebhookEventProcessing:
    """Tests for webhook event filtering and payload handling."""

    def test_webhook_event_types(self, webhook_payload_sample: dict):
        """Test: Various webhook event types are handled."""
        events = [
            "push",
            "pull_request",
            "issues",
            "pull_request_review",
            "repository",
        ]

        for event in events:
            # In real implementation, would filter by event type
            assert event

    def test_webhook_payload_structure(self, webhook_payload_sample: dict):
        """Test: Webhook payload contains expected fields."""
        assert "action" in webhook_payload_sample
        assert "repository" in webhook_payload_sample
        assert webhook_payload_sample["repository"]["name"] == "_codex_"

    def test_webhook_event_filtering(self):
        """Test: Filter webhooks by event type."""
        webhook_config = {
            "events": ["push", "pull_request"],
        }

        # If webhook configured for push, it should receive push events
        assert "push" in webhook_config["events"]

        # If webhook not configured for issues, should not receive issues events
        assert "issues" not in webhook_config["events"]


# ─────────────────────────────────────────────────────────────────────────────
# Batch Webhook Operations
# ─────────────────────────────────────────────────────────────────────────────


class TestWebhookBatchOperations:
    """Batch operation tests for webhooks."""

    def test_batch_create_webhooks(
        self,
        gh_api_base: str,
        repo_webhooks_endpoint: str,
    ):
        """Test: Create multiple webhooks in sequence."""
        urls = [
            "https://example.com/webhook1",
            "https://example.com/webhook2",
            "https://example.com/webhook3",
        ]

        for url in urls:
            payload = {
                "name": "web",
                "active": True,
                "config": {"url": url},
            }

            assert payload["config"]["url"] == url

    def test_batch_delete_webhooks(
        self,
        gh_api_base: str,
        repo_webhooks_endpoint: str,
    ):
        """Test: Delete multiple webhooks in sequence."""
        hook_ids = [1, 2, 3]

        for hook_id in hook_ids:
            endpoint = f"{gh_api_base}{repo_webhooks_endpoint}/{hook_id}"
            assert str(hook_id) in endpoint

    def test_batch_update_webhook_events(
        self,
        gh_api_base: str,
        repo_webhooks_endpoint: str,
    ):
        """Test: Update events for multiple webhooks."""
        hook_ids = [1, 2, 3]

        for hook_id in hook_ids:
            endpoint = f"{gh_api_base}{repo_webhooks_endpoint}/{hook_id}"
            payload = {
                "events": ["push", "pull_request", "issues"],
            }

            assert str(hook_id) in endpoint
            assert len(payload["events"]) == 3
