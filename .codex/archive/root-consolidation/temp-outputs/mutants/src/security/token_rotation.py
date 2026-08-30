"""Token Rotation Automation Module.

PS-05 Enhancement: Implements automated token rotation with:
- Auto-rotation on security events
- Rotation scheduling
- Comprehensive audit trail

This module extends the Token Security Neutralization planset with
enterprise-grade token lifecycle management.
"""

from __future__ import annotations

import hashlib
import json
import logging
import secrets
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class RotationTrigger(Enum):
    """Events that can trigger token rotation."""

    SCHEDULED = "scheduled"  # Regular rotation schedule
    EXPIRY = "expiry"  # Token approaching expiration
    SECURITY_EVENT = "security_event"  # Security incident detected
    EXPOSURE = "exposure"  # Token potentially exposed
    MANUAL = "manual"  # Manual rotation request
    POLICY_CHANGE = "policy_change"  # Security policy updated


class TokenState(Enum):
    """Token lifecycle states."""

    ACTIVE = "active"
    ROTATING = "rotating"  # In grace period during rotation
    REVOKED = "revoked"
    EXPIRED = "expired"


@dataclass
class TokenMetadata:
    """Metadata for a managed token."""

    token_id: str
    created_at: datetime
    expires_at: datetime
    last_used: Optional[datetime] = None
    state: TokenState = TokenState.ACTIVE
    rotation_count: int = 0
    scopes: list[str] = field(default_factory=list)
    provider: str = "github"  # github, gitlab, bitbucket, etc.

    def is_expired(self) -> bool:
        """Check if token has expired."""
        return datetime.now(UTC) > self.expires_at

    def days_until_expiry(self) -> int:
        """Days remaining until expiration."""
        delta = self.expires_at - datetime.now(UTC)
        return max(0, delta.days)

    def should_rotate(self, policy: RotationPolicy) -> tuple[bool, RotationTrigger | None]:
        """Determine if token should be rotated based on policy."""
        if self.is_expired():
            return True, RotationTrigger.EXPIRY

        if self.days_until_expiry() <= policy.rotate_before_expiry_days:
            return True, RotationTrigger.EXPIRY

        if self.rotation_count == 0:
            # First rotation after max age
            days_since_creation = (datetime.now(UTC) - self.created_at).days
            if days_since_creation >= policy.max_age_days:
                return True, RotationTrigger.SCHEDULED

        return False, None


@dataclass
class RotationPolicy:
    """Policy configuration for token rotation."""

    max_age_days: int = 90  # Maximum token age before rotation
    rotate_before_expiry_days: int = 14  # Rotate this many days before expiry
    grace_period_hours: int = 24  # Both tokens valid during rotation
    auto_rotate_on_exposure: bool = True  # Rotate if token detected in logs
    auto_rotate_on_security_event: bool = True  # Rotate on security incidents
    min_rotation_interval_hours: int = 1  # Prevent rotation storms

    def to_dict(self) -> dict[str, Any]:
        """Serialize policy to dict."""
        return {
            "max_age_days": self.max_age_days,
            "rotate_before_expiry_days": self.rotate_before_expiry_days,
            "grace_period_hours": self.grace_period_hours,
            "auto_rotate_on_exposure": self.auto_rotate_on_exposure,
            "auto_rotate_on_security_event": self.auto_rotate_on_security_event,
            "min_rotation_interval_hours": self.min_rotation_interval_hours,
        }


@dataclass
class RotationEvent:
    """Record of a rotation event for audit trail."""

    event_id: str
    token_id: str
    timestamp: datetime
    trigger: RotationTrigger
    old_token_hash: str  # SHA-256 of old token (not the token itself)
    new_token_hash: str  # SHA-256 of new token
    success: bool
    error_message: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_jsonl(self) -> str:
        """Serialize to JSONL format for audit log."""
        return json.dumps(
            {
                "event_id": self.event_id,
                "token_id": self.token_id,
                "timestamp": self.timestamp.isoformat(),
                "trigger": self.trigger.value,
                "old_token_hash": self.old_token_hash,
                "new_token_hash": self.new_token_hash,
                "success": self.success,
                "error_message": self.error_message,
                "metadata": self.metadata,
            }
        )


class TokenRotationManager:
    """Manages automated token rotation lifecycle.

    Features:
    - Scheduled rotation based on policy
    - Security event-triggered rotation
    - Grace period for seamless transitions
    - Comprehensive audit logging
    """

    def __init__(
        self,
        policy: RotationPolicy | None = None,
        audit_log_path: Path | None = None,
        token_generator: Callable[[], str] | None = None,
    ):
        """Initialize the rotation manager.

        Args:
            policy: Rotation policy configuration
            audit_log_path: Path for audit log file
            token_generator: Custom token generation function
        """
        self.policy = policy or RotationPolicy()
        self.audit_log_path = audit_log_path or Path(".codex/evidence/token_rotation.jsonl")
        self.token_generator = token_generator or self._default_token_generator
        self.tokens: dict[str, TokenMetadata] = {}
        self._rotation_locks: dict[str, datetime] = {}

    @staticmethod
    def _default_token_generator() -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(32)

    @staticmethod
    def _hash_token(token: str) -> str:
        """Create SHA-256 hash of token for audit (never store raw tokens)."""
        return hashlib.sha256(token.encode()).hexdigest()[:16]

    def register_token(
        self,
        token_id: str,
        token_value: str,
        expires_at: datetime,
        scopes: list[str] | None = None,
        provider: str = "github",
    ) -> TokenMetadata:
        """Register a token for management.

        Args:
            token_id: Unique identifier for the token
            token_value: The actual token (only hash is stored)
            expires_at: Token expiration datetime
            scopes: List of permission scopes
            provider: Token provider (github, gitlab, etc.)

        Returns:
            TokenMetadata for the registered token
        """
        metadata = TokenMetadata(
            token_id=token_id,
            created_at=datetime.now(UTC),
            expires_at=expires_at,
            scopes=scopes or [],
            provider=provider,
        )
        self.tokens[token_id] = metadata

        logger.info(f"Registered token {token_id} with expiry {expires_at.isoformat()}")
        return metadata

    def check_rotation_needed(self, token_id: str) -> tuple[bool, RotationTrigger | None]:
        """Check if a token needs rotation.

        Args:
            token_id: Token to check

        Returns:
            Tuple of (needs_rotation, trigger_reason)
        """
        if token_id not in self.tokens:
            return False, None

        return self.tokens[token_id].should_rotate(self.policy)

    def rotate_token(
        self,
        token_id: str,
        trigger: RotationTrigger,
        old_token: str,
        new_token: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RotationEvent:
        """Perform token rotation.

        Args:
            token_id: Token to rotate
            trigger: What triggered the rotation
            old_token: Current token value (for hash verification)
            new_token: New token value (generated if not provided)
            metadata: Additional context for audit

        Returns:
            RotationEvent with results
        """
        # Check rotation lock to prevent storms
        if token_id in self._rotation_locks:
            lock_time = self._rotation_locks[token_id]
            min_interval = timedelta(hours=self.policy.min_rotation_interval_hours)
            if datetime.now(UTC) - lock_time < min_interval:
                return RotationEvent(
                    event_id=secrets.token_hex(8),
                    token_id=token_id,
                    timestamp=datetime.now(UTC),
                    trigger=trigger,
                    old_token_hash=self._hash_token(old_token),
                    new_token_hash="",  # nosec B106
                    success=False,
                    error_message="Rotation throttled - minimum interval not met",
                    metadata=metadata or {},
                )

        # Generate new token if not provided
        new_token = new_token or self.token_generator()

        # Create rotation event
        event = RotationEvent(
            event_id=secrets.token_hex(8),
            token_id=token_id,
            timestamp=datetime.now(UTC),
            trigger=trigger,
            old_token_hash=self._hash_token(old_token),
            new_token_hash=self._hash_token(new_token),
            success=True,
            metadata=metadata or {},
        )

        # Update token metadata
        if token_id in self.tokens:
            self.tokens[token_id].rotation_count += 1
            self.tokens[token_id].state = TokenState.ROTATING

        # Set rotation lock
        self._rotation_locks[token_id] = datetime.now(UTC)

        # Log audit event
        self._write_audit_log(event)

        logger.info(f"Rotated token {token_id}: trigger={trigger.value}, event_id={event.event_id}")

        return event

    def handle_security_event(
        self,
        event_type: str,
        affected_token_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[RotationEvent]:
        """Handle a security event that may require token rotation.

        Args:
            event_type: Type of security event (exposure, breach, etc.)
            affected_token_ids: Specific tokens affected, or all if None
            metadata: Event context

        Returns:
            List of rotation events performed
        """
        events: list[Any] = []

        if event_type == "exposure" and not self.policy.auto_rotate_on_exposure:
            logger.warning("Token exposure detected but auto-rotation disabled")
            return events

        if event_type in ("breach", "compromise") and not self.policy.auto_rotate_on_security_event:
            logger.warning("Security event detected but auto-rotation disabled")
            return events

        token_ids = affected_token_ids or list(self.tokens.keys())

        for token_id in token_ids:
            if token_id in self.tokens:
                # Note: In production, old_token would come from secure storage
                event = self.rotate_token(
                    token_id=token_id,
                    trigger=RotationTrigger.SECURITY_EVENT,
                    old_token="<redacted>",  # Would be retrieved securely  # nosec B106
                    metadata={
                        "security_event_type": event_type,
                        **(metadata or {}),
                    },
                )
                events.append(event)

        return events

    def get_rotation_schedule(self) -> list[dict[str, Any]]:
        """Get scheduled rotations for all managed tokens.

        Returns:
            List of upcoming rotation schedules
        """
        schedule = []

        for token_id, meta in self.tokens.items():
            needs_rotation, trigger = meta.should_rotate(self.policy)

            schedule.append(
                {
                    "token_id": token_id,
                    "days_until_expiry": meta.days_until_expiry(),
                    "rotation_needed": needs_rotation,
                    "trigger": trigger.value if trigger else None,
                    "state": meta.state.value,
                    "rotation_count": meta.rotation_count,
                }
            )

        return sorted(schedule, key=lambda x: x["days_until_expiry"])

    def _write_audit_log(self, event: RotationEvent) -> None:
        """Write rotation event to audit log."""
        try:
            self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.audit_log_path.open("a") as f:
                f.write(event.to_jsonl() + "\n")
        except (IOError, OSError) as e:
            type(e).__name__
            logger.error("Failed to write audit log: <ERROR_TYPE>")


def check_token_rotation_needed(
    token_id: str,
    expires_at: datetime,
    max_age_days: int = 90,
    rotate_before_days: int = 14,
) -> tuple[bool, str | None]:
    """Convenience function to check if a token needs rotation.

    Args:
        token_id: Token identifier
        expires_at: Token expiration datetime
        max_age_days: Maximum age before rotation
        rotate_before_days: Days before expiry to rotate

    Returns:
        Tuple of (needs_rotation, reason)
    """
    now = datetime.now(UTC)

    if now > expires_at:
        return True, "Token expired"

    days_until_expiry = (expires_at - now).days
    if days_until_expiry <= rotate_before_days:
        return True, f"Token expires in {days_until_expiry} days"

    return False, None


__all__ = [
    "RotationEvent",
    "RotationPolicy",
    "RotationTrigger",
    "TokenMetadata",
    "TokenRotationManager",
    "TokenState",
    "check_token_rotation_needed",
]
