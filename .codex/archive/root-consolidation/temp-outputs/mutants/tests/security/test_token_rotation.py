"""Tests for Token Rotation Automation module.

PS-05 Enhancement: Tests for automated token rotation with:
- Policy-based rotation scheduling
- Security event handling
- Audit trail verification
"""

import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

from security.token_rotation import (
    RotationEvent,
    RotationPolicy,
    RotationTrigger,
    TokenMetadata,
    TokenRotationManager,
    TokenState,
    check_token_rotation_needed,
)


class TestRotationPolicy:
    """Test RotationPolicy configuration."""

    def test_default_policy(self):
        """Test default policy values."""
        policy = RotationPolicy()
        assert policy.max_age_days == 90, "max_age_days is not valid"
        assert policy.rotate_before_expiry_days == 14, "rotate_before_expiry_days is not valid"
        assert policy.grace_period_hours == 24, "grace_period_hours is not valid"
        assert policy.auto_rotate_on_exposure is True, "auto_rotate_on_exposure is not valid"
        assert policy.auto_rotate_on_security_event is True, "auto_rotate_on_security_event is not valid"

    def test_custom_policy(self):
        """Test custom policy configuration."""
        policy = RotationPolicy(
            max_age_days=30,
            rotate_before_expiry_days=7,
            auto_rotate_on_exposure=False,
        )
        assert policy.max_age_days == 30, "max_age_days is not valid"
        assert policy.rotate_before_expiry_days == 7, "rotate_before_expiry_days is not valid"
        assert policy.auto_rotate_on_exposure is False, "auto_rotate_on_exposure is not valid"

    def test_policy_serialization(self):
        """Test policy to_dict method."""
        policy = RotationPolicy()
        policy_dict = policy.to_dict()
        assert "max_age_days" in policy_dict, "Condition must be true"
        assert "rotate_before_expiry_days" in policy_dict, "Condition must be true"
        assert policy_dict["max_age_days"] == 90, "Condition must be true"


class TestTokenMetadata:
    """Test TokenMetadata model."""

    def test_create_metadata(self):
        """Test creating token metadata."""
        expires = datetime.now(UTC) + timedelta(days=30)
        meta = TokenMetadata(
            token_id="test-token-1",
            created_at=datetime.now(UTC),
            expires_at=expires,
            scopes=["repo:read", "workflow:write"],
        )
        assert meta.token_id == "test-token-1", "token_id is not valid"
        assert meta.state == TokenState.ACTIVE, "state is not valid"
        assert meta.rotation_count == 0, "Count must be greater than zero"

    def test_is_expired_false(self):
        """Test token is not expired."""
        meta = TokenMetadata(
            token_id="test",
            created_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=30),
        )
        assert meta.is_expired() is False, "Condition must be true"

    def test_is_expired_true(self):
        """Test token is expired."""
        meta = TokenMetadata(
            token_id="test",
            created_at=datetime.now(UTC) - timedelta(days=100),
            expires_at=datetime.now(UTC) - timedelta(days=1),
        )
        assert meta.is_expired() is True, "Condition must be true"

    def test_days_until_expiry(self):
        """Test days until expiry calculation."""
        meta = TokenMetadata(
            token_id="test",
            created_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=15),
        )
        days = meta.days_until_expiry()
        assert 14 <= days <= 15, "14 is not valid"

    def test_should_rotate_expiring(self):
        """Test should_rotate for token nearing expiry."""
        policy = RotationPolicy(rotate_before_expiry_days=14)
        meta = TokenMetadata(
            token_id="test",
            created_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=10),
        )
        should_rotate, trigger = meta.should_rotate(policy)
        assert should_rotate is True, "should_rotate is not valid"
        assert trigger == RotationTrigger.EXPIRY, "trigger is not valid"

    def test_should_not_rotate(self):
        """Test should_rotate for healthy token."""
        policy = RotationPolicy()
        meta = TokenMetadata(
            token_id="test",
            created_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=60),
        )
        should_rotate, trigger = meta.should_rotate(policy)
        assert should_rotate is False, "should_rotate is not valid"
        assert trigger is None, "trigger is not valid"


class TestTokenRotationManager:
    """Test TokenRotationManager."""

    def test_register_token(self):
        """Test registering a token."""
        manager = TokenRotationManager()
        expires = datetime.now(UTC) + timedelta(days=90)

        meta = manager.register_token(
            token_id="github-token-1",
            token_value="ghp_xxxxx",
            expires_at=expires,
            scopes=["repo"],
            provider="github",
        )

        assert meta.token_id == "github-token-1", "token_id is not valid"
        assert meta.provider == "github", "provider is not valid"
        assert "github-token-1" in manager.tokens, "Condition must be true"

    def test_check_rotation_needed(self):
        """Test checking if rotation is needed."""
        manager = TokenRotationManager()

        # Register expiring token
        expires = datetime.now(UTC) + timedelta(days=5)
        manager.register_token("test-token", "xxx", expires)

        needs_rotation, trigger = manager.check_rotation_needed("test-token")
        assert needs_rotation is True, "needs_rotation is not valid"
        assert trigger == RotationTrigger.EXPIRY, "trigger is not valid"

    def test_rotate_token(self):
        """Test token rotation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit_path = Path(tmpdir) / "token_rotation.jsonl"
            manager = TokenRotationManager(audit_log_path=audit_path)

            # Register token
            expires = datetime.now(UTC) + timedelta(days=90)
            manager.register_token("test-token", "old-token-value", expires)

            # Rotate
            event = manager.rotate_token(
                token_id="test-token",
                trigger=RotationTrigger.MANUAL,
                old_token="old-token-value",
                metadata={"reason": "test"},
            )

            assert event.success is True, "success is not valid"
            assert event.trigger == RotationTrigger.MANUAL, "trigger is not valid"
            assert len(event.old_token_hash) == 16, "Collection must not be empty"
            assert len(event.new_token_hash) == 16, "Collection must not be empty"
            assert event.old_token_hash != event.new_token_hash, "old_token_hash is not valid"

            # Check audit log
            assert audit_path.exists(), "Condition must be true"

    def test_rotation_throttling(self):
        """Test rotation throttling prevents storms."""
        manager = TokenRotationManager(policy=RotationPolicy(min_rotation_interval_hours=1))

        expires = datetime.now(UTC) + timedelta(days=90)
        manager.register_token("test-token", "token-value", expires)

        # First rotation succeeds
        event1 = manager.rotate_token(
            "test-token",
            RotationTrigger.MANUAL,
            "token-value",
        )
        assert event1.success is True, "success is not valid"

        # Second rotation should be throttled
        event2 = manager.rotate_token(
            "test-token",
            RotationTrigger.MANUAL,
            "token-value",
        )
        assert event2.success is False, "success is not valid"
        assert "throttled" in event2.error_message.lower(), "Error should be raised or set"

    def test_get_rotation_schedule(self):
        """Test getting rotation schedule."""
        manager = TokenRotationManager()

        # Register tokens with different expiries
        manager.register_token(
            "token-1",
            "xxx",
            datetime.now(UTC) + timedelta(days=10),
        )
        manager.register_token(
            "token-2",
            "yyy",
            datetime.now(UTC) + timedelta(days=60),
        )

        schedule = manager.get_rotation_schedule()

        assert len(schedule) == 2, "Schedule must not be empty"
        # Should be sorted by days until expiry
        assert schedule[0]["token_id"] == "token-1", "Condition must be true"
        assert schedule[0]["rotation_needed"] is True, "Condition must be true"


class TestSecurityEventHandling:
    """Test security event triggered rotation."""

    def test_handle_exposure_event(self):
        """Test handling token exposure event."""
        manager = TokenRotationManager()

        manager.register_token(
            "exposed-token",
            "xxx",
            datetime.now(UTC) + timedelta(days=90),
        )

        events = manager.handle_security_event(
            event_type="exposure",
            affected_token_ids=["exposed-token"],
            metadata={"source": "secret-scanning"},
        )

        assert len(events) == 1, "Events must not be empty"
        assert events[0].trigger == RotationTrigger.SECURITY_EVENT, "trigger is not valid"

    def test_disabled_auto_rotation(self):
        """Test that disabled auto-rotation is respected."""
        manager = TokenRotationManager(policy=RotationPolicy(auto_rotate_on_exposure=False))

        manager.register_token(
            "token",
            "xxx",
            datetime.now(UTC) + timedelta(days=90),
        )

        events = manager.handle_security_event("exposure")
        assert len(events) == 0, "Events must not be empty"


class TestConvenienceFunctions:
    """Test standalone convenience functions."""

    def test_check_token_rotation_needed_expired(self):
        """Test check for expired token."""
        needs_rotation, reason = check_token_rotation_needed(
            token_id="test",
            expires_at=datetime.now(UTC) - timedelta(days=1),
        )
        assert needs_rotation is True, "needs_rotation is not valid"
        assert "expired" in reason.lower(), "Condition must be true"

    def test_check_token_rotation_needed_soon(self):
        """Test check for token expiring soon."""
        needs_rotation, reason = check_token_rotation_needed(
            token_id="test",
            expires_at=datetime.now(UTC) + timedelta(days=5),
            rotate_before_days=14,
        )
        assert needs_rotation is True, "needs_rotation is not valid"
        assert "expires in" in reason.lower(), "Condition must be true"

    def test_check_token_rotation_needed_healthy(self):
        """Test check for healthy token."""
        needs_rotation, reason = check_token_rotation_needed(
            token_id="test",
            expires_at=datetime.now(UTC) + timedelta(days=60),
        )
        assert needs_rotation is False, "needs_rotation is not valid"
        assert reason is None, "reason is not valid"


class TestRotationEvent:
    """Test RotationEvent serialization."""

    def test_to_jsonl(self):
        """Test JSONL serialization."""
        event = RotationEvent(
            event_id="evt-123",
            token_id="test-token",
            timestamp=datetime.now(UTC),
            trigger=RotationTrigger.SCHEDULED,
            old_token_hash="abc123",
            new_token_hash="def456",
            success=True,
        )

        jsonl = event.to_jsonl()
        assert "evt-123" in jsonl, "Condition must be true"
        assert "scheduled" in jsonl, "Condition must be true"
        assert "abc123" in jsonl, "Condition must be true"
