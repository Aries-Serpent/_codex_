"""GitHub App implementation for reviewer bot."""

from __future__ import annotations

import hmac
import hashlib
import os
from datetime import datetime, timedelta
from typing import Any, Dict
import logging

import jwt
import requests
from flask import Flask, jsonify, request

logger = logging.getLogger(__name__)


class CodexReviewerApp:
    """GitHub App for PR review."""

    def __init__(self) -> None:
        self.app_id = os.environ.get("CODEX_APP_ID", "")
        self.private_key = os.environ.get("CODEX_PRIVATE_KEY", "")
        self.webhook_secret = os.environ.get("CODEX_WEBHOOK_SECRET", "")
        self.app = Flask(__name__)
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Setup webhook routes."""

        @self.app.route("/webhook", methods=["POST"])
        def webhook() -> Any:
            if not self._verify_signature(request):
                return jsonify({"error": "Invalid signature"}), 401

            event = request.headers.get("X-GitHub-Event", "")
            payload = request.get_json(silent=True) or {}

            if event == "pull_request":
                result = self._handle_pr_event(payload)
            elif event == "pull_request_review":
                result = self._handle_review_event(payload)
            elif event == "issue_comment":
                result = self._handle_comment_event(payload)
            else:
                result = {"status": "ignored", "event": event}

            return jsonify(result)

        @self.app.route("/health", methods=["GET"])
        def health() -> Any:
            return jsonify({"status": "healthy", "app_id": self.app_id})

    def _verify_signature(self, req: Any) -> bool:
        """Verify webhook signature."""
        signature = req.headers.get("X-Hub-Signature-256")
        if not signature or not self.webhook_secret:
            return False

        expected = "sha256=" + hmac.new(
            self.webhook_secret.encode(),
            req.data,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(signature, expected)

    def _handle_pr_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pull request events."""
        action = payload.get("action")
        pr = payload.get("pull_request", {})

        if action in {"opened", "synchronize"}:
            logger.info(f"PR event: {action} for PR #{pr.get('number', 0)}")
            return {
                "status": "review_queued",
                "pr": pr.get("number", 0),
            }

        return {"status": "ignored", "action": action}

    def _handle_review_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pull request review events."""
        logger.info("Review event received")
        return {"status": "review_event_received"}

    def _handle_comment_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle issue comment events."""
        logger.info("Comment event received")
        return {"status": "comment_event_received"}

    def _generate_jwt(self) -> str:
        """Generate JWT for app authentication."""
        now = datetime.utcnow()
        payload = {
            "iat": now,
            "exp": now + timedelta(minutes=10),
            "iss": self.app_id,
        }

        return jwt.encode(payload, self.private_key, algorithm="RS256")

    def _get_installation_token(self, installation_id: int) -> str:
        """Get installation access token."""
        jwt_token = self._generate_jwt()

        response = requests.post(
            f"https://api.github.com/app/installations/{installation_id}/access_tokens",
            headers={
                "Authorization": f"Bearer {jwt_token}",
                "Accept": "application/vnd.github.v3+json",
            },
            timeout=10,
        )

        response.raise_for_status()
        return response.json().get("token", "")
