"""
Security module for MSP Gateway
Handles authentication, authorization, policy enforcement, and redaction
"""

import logging
import re
from hashlib import pbkdf2_hmac, sha256
from pathlib import Path
from typing import Optional

import yaml

from src.utils.log_sanitizer import sanitize_log_input

from .config import settings

logger = logging.getLogger(__name__)

_API_KEY_HASH_PREFIX = "pbkdf2_sha256$"
_API_KEY_HASH_ITERATIONS = 200_000


def _api_key_pepper_bytes() -> bytes:
    return settings.api_key_pepper.encode("utf-8")


def legacy_hash_api_key(api_key: str) -> str:
    """Return the legacy SHA-256 API-key hash for compatibility lookups.

    Note: This function uses SHA-256 for backward compatibility with existing
    stored hashes. New hashes should use hash_api_key() which uses PBKDF2.
    This is intentionally weak for legacy support only.
    """
    # Security: intentional SHA-256 for backward-compat lookup of existing stored hashes only.
    # New hashes always use hash_api_key() (PBKDF2). Legacy hashes are migrated to PBKDF2
    # on first use via TenantRegistry.get_tenant_by_api_key(). See tenant_context.py.
    # nosec: B303,B324 - legacy support for existing hashes
    # nosemgrep: python.lang.security.insecure-hash-algorithm-md5.insecure-hash-algorithm-md5
    # intentional legacy SHA-256; PBKDF2 migration happens on first use in TenantRegistry
    # see services/msp_gateway/middleware/tenant_context.py
    return sha256(api_key.encode("utf-8")).hexdigest()  # nosec  # pragma: allowlist secret


def candidate_api_key_hashes(api_key: str) -> tuple[str, str]:
    """Return current and legacy hash representations for *api_key*."""
    return (hash_api_key(api_key), legacy_hash_api_key(api_key))


def hash_api_key(api_key: str) -> str:
    """Return a stable KDF-derived hash for API-key storage and lookup."""
    derived = pbkdf2_hmac(
        "sha256",
        api_key.encode("utf-8"),
        _api_key_pepper_bytes(),
        _API_KEY_HASH_ITERATIONS,
    ).hex()
    return f"{_API_KEY_HASH_PREFIX}{derived}"


class PolicyEnforcer:
    """Enforces security policies from safelist and denylist"""

    def __init__(self, policy_dir: Optional[str] = None):
        self.policy_dir = Path(policy_dir or settings.policy_dir)
        self._load_policies()

    def _load_policies(self):
        """Load safelist and denylist policies"""
        try:
            safelist_path = self.policy_dir / "safelist.yaml"
            denylist_path = self.policy_dir / "denylist.yaml"

            if safelist_path.exists():
                with open(safelist_path, "r") as f:
                    self.safelist = yaml.safe_load(f) or {}
            else:
                logger.warning("Safelist not found at %s, using empty policy", safelist_path)
                self.safelist = {}

            if denylist_path.exists():
                with open(denylist_path, "r") as f:
                    self.denylist = yaml.safe_load(f) or {}
            else:
                logger.warning("Denylist not found at %s, using empty policy", denylist_path)
                self.denylist = {}

            logger.info("Policies loaded successfully")
        except Exception as e:
            logger.error("Error loading policies: %s", type(e).__name__)
            self.safelist = {}
            self.denylist = {}

    def check_blocked_patterns(self, text: str) -> Optional[str]:
        """Check if text contains blocked patterns

        Returns:
            Error message if blocked pattern found, None otherwise
        """
        blocked_patterns = self.denylist.get("blocked_prompt_patterns", [])
        for pattern in blocked_patterns:
            if pattern.lower() in text.lower():
                return f"Blocked pattern detected: {pattern}"
        return None

    def check_blocked_actions(self, action: str) -> bool:
        """Check if action is blocked

        Returns:
            True if action is blocked, False otherwise
        """
        blocked_actions = self.denylist.get("blocked_actions", [])
        return action in blocked_actions

    def redact_sensitive_content(self, text: str) -> tuple[str, list[str]]:
        """Redact sensitive information from text

        Returns:
            Tuple of (redacted_text, list of redaction types applied)
        """
        if not settings.redaction_enabled:
            return text, []

        redacted = text
        redactions_applied = []

        # Apply regex-based redactions
        redaction_patterns = self.denylist.get("redaction_patterns", [])
        for pattern_config in redaction_patterns:
            pattern = pattern_config.get("pattern")
            replacement = pattern_config.get("replacement", "[REDACTED]")
            if pattern:
                matches = re.findall(pattern, redacted)
                if matches:
                    redacted = re.sub(pattern, replacement, redacted)
                    redactions_applied.append(replacement)

        # Redact sensitive terms (but avoid redacting already-redacted placeholders)
        sensitive_terms = self.denylist.get("sensitive_terms", [])
        for term in sensitive_terms:
            if term.lower() in redacted.lower():
                # Case-insensitive replacement, but not inside brackets []
                # Use negative lookbehind and lookahead to avoid matching inside [REDACTED] markers
                pattern = r'(?<!\[)' + re.escape(term) + r'(?![^\[]*\])'
                redacted = re.sub(pattern, "[REDACTED]", redacted, flags=re.IGNORECASE)
                redactions_applied.append(f"term:{term}")

        return redacted, redactions_applied


class AuthManager:
    """Handles authentication and authorization"""

    def __init__(self):
        self.api_keys: dict[str, str] = {}  # api_key_hash -> tenant_id mapping

    def register_api_key(self, api_key: str, tenant_id: str):
        """Register an API key for a tenant"""
        self.register_api_key_hash(hash_api_key(api_key), tenant_id)

    def register_api_key_hash(self, api_key_hash: str, tenant_id: str):
        """Register a pre-hashed API key for a tenant."""
        self.api_keys[api_key_hash] = tenant_id

    def verify_api_key(self, api_key: str) -> Optional[str]:
        """Verify API key and return tenant_id

        Returns:
            tenant_id if valid, None otherwise
        """
        for api_key_hash in candidate_api_key_hashes(api_key):
            tenant_id = self.api_keys.get(api_key_hash)
            if tenant_id is not None:
                return tenant_id
        return None

    def revoke_api_key(self, api_key: str):
        """Revoke an API key"""
        for api_key_hash in candidate_api_key_hashes(api_key):
            self.revoke_api_key_hash(api_key_hash)

    def revoke_api_key_hash(self, api_key_hash: str):
        """Revoke a pre-hashed API key."""
        self.api_keys.pop(api_key_hash, None)


class OfflineGuard:
    """Enforces offline-only operation"""

    @staticmethod
    def check_network_access() -> bool:
        """Check if network access is attempted

        Returns:
            True if network access is blocked, False if allowed
        """
        return settings.offline

    @staticmethod
    def block_external_call(call_type: str):
        """Block external calls in offline mode

        Raises:
            RuntimeError if offline mode is enabled
        """
        if settings.offline:
            raise RuntimeError(
                f"External call '{call_type}' blocked in offline mode. "
                "Set MSP_OFFLINE=False to allow network access."
            )


# Global instances
policy_enforcer = PolicyEnforcer()
auth_manager = AuthManager()
offline_guard = OfflineGuard()


def validate_prompt(prompt: str, tenant_id: str) -> tuple[bool, Optional[str]]:
    """Validate a prompt against security policies

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check for blocked patterns
    error = policy_enforcer.check_blocked_patterns(prompt)
    if error:
        logger.warning(  # nosec: tenant_id and error are sanitized via sanitize_log_input  # pragma: allowlist secret
            "Blocked prompt for tenant %s: %s",
            sanitize_log_input(tenant_id),
            sanitize_log_input(error),
        )
        return False, error

    # Check prompt length (basic validation)
    if len(prompt) > 10000:  # Max prompt length
        return False, "Prompt exceeds maximum length"

    return True, None


def redact_content(text: str, tenant_id: str) -> tuple[str, list[str]]:
    """Redact sensitive content from text

    Returns:
        Tuple of (redacted_text, list of redactions applied)
    """
    redacted, redactions = policy_enforcer.redact_sensitive_content(text)
    if redactions:
        logger.info(  # nosec: tenant_id and redactions are sanitized via sanitize_log_input  # pragma: allowlist secret
            "Applied redactions for tenant %s: %s",
            sanitize_log_input(tenant_id),
            sanitize_log_input(str(redactions)),
        )
    return redacted, redactions
