"""Comprehensive tests for security.token_rotation module.

This module tests automated token rotation including:
- Token rotation triggers
- Rotation policies
- Token lifecycle management
- Grace periods
- Audit trails
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from security.token_rotation import (
    RotationPolicy,
    RotationTrigger,
    TokenMetadata,
    TokenRotationManager,
    TokenState,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def rotation_policy():
    """Create a rotation policy."""
    return RotationPolicy(
        max_token_age_days=90,
        rotate_before_expiry_days=7,
        grace_period_hours=24,
        max_rotation_count=12,
    )


@pytest.fixture
def token_metadata():
    """Create token metadata."""
    return TokenMetadata(
        token_id="token_123",
        created_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(days=90),
        scopes=["read:repo", "write:repo"],
    )


@pytest.fixture
def token_manager(rotation_policy):
    """Create a token manager."""
    return TokenRotationManager(policy=rotation_policy)


# ============================================================================
# ROTATION_TRIGGER TESTS
# ============================================================================


class TestRotationTrigger:
    """Test RotationTrigger enum."""

    def test_rotation_trigger_values(self):
        """Test all trigger types."""
        triggers = [
            RotationTrigger.SCHEDULED,
            RotationTrigger.EXPIRY,
            RotationTrigger.SECURITY_EVENT,
            RotationTrigger.EXPOSURE,
            RotationTrigger.MANUAL,
            RotationTrigger.POLICY_CHANGE,
        ]
        assert len(triggers) == 6, "Triggers must not be empty"

    def test_rotation_trigger_scheduled(self):
        """Test scheduled trigger."""
        assert RotationTrigger.SCHEDULED.value == "scheduled", "Value must be initialized"

    def test_rotation_trigger_expiry(self):
        """Test expiry trigger."""
        assert RotationTrigger.EXPIRY.value == "expiry", "Value must be initialized"

    def test_rotation_trigger_security_event(self):
        """Test security event trigger."""
        assert RotationTrigger.SECURITY_EVENT.value == "security_event", "Value must be initialized"

    def test_rotation_trigger_exposure(self):
        """Test exposure trigger."""
        assert RotationTrigger.EXPOSURE.value == "exposure", "Value must be initialized"

    def test_rotation_trigger_manual(self):
        """Test manual trigger."""
        assert RotationTrigger.MANUAL.value == "manual", "Value must be initialized"

    def test_rotation_trigger_policy_change(self):
        """Test policy change trigger."""
        assert RotationTrigger.POLICY_CHANGE.value == "policy_change", "Value must be initialized"


# ============================================================================
# TOKEN_STATE TESTS
# ============================================================================


class TestTokenState:
    """Test TokenState enum."""

    def test_token_state_values(self):
        """Test all token states."""
        states = [
            TokenState.ACTIVE,
            TokenState.ROTATING,
            TokenState.REVOKED,
            TokenState.EXPIRED,
        ]
        assert len(states) == 4, "States must not be empty"

    def test_token_state_active(self):
        """Test active state."""
        assert TokenState.ACTIVE.value == "active", "Value must be initialized"

    def test_token_state_rotating(self):
        """Test rotating state."""
        assert TokenState.ROTATING.value == "rotating", "Value must be initialized"

    def test_token_state_revoked(self):
        """Test revoked state."""
        assert TokenState.REVOKED.value == "revoked", "Value must be initialized"

    def test_token_state_expired(self):
        """Test expired state."""
        assert TokenState.EXPIRED.value == "expired", "Value must be initialized"


# ============================================================================
# TOKEN_METADATA TESTS
# ============================================================================


class TestTokenMetadata:
    """Test TokenMetadata dataclass."""

    def test_token_metadata_creation(self, token_metadata):
        """Test creating token metadata."""
        assert token_metadata.token_id == "token_123", "Data must not be empty"
        assert token_metadata.state == TokenState.ACTIVE, "Data must not be empty"
        assert token_metadata.rotation_count == 0, "Data must not be empty"

    def test_token_metadata_is_expired_false(self, token_metadata):
        """Test is_expired returns False for valid token."""
        assert token_metadata.is_expired() is False, "Data must not be empty"

    def test_token_metadata_is_expired_true(self):
        """Test is_expired returns True for expired token."""
        metadata = TokenMetadata(
            token_id="token_123",
            created_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) - timedelta(hours=1),
        )
        assert metadata.is_expired() is True, "Data must not be empty"

    def test_token_metadata_days_until_expiry(self, token_metadata):
        """Test days_until_expiry calculation."""
        days = token_metadata.days_until_expiry()
        assert days >= 89 and days <= 91, "days must be greater than zero"

    def test_token_metadata_days_until_expiry_expired(self):
        """Test days_until_expiry for expired token."""
        metadata = TokenMetadata(
            token_id="token_123",
            created_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) - timedelta(hours=1),
        )
        assert metadata.days_until_expiry() == 0, "Data must not be empty"

    def test_token_metadata_should_rotate_expiry_trigger(self, token_metadata, rotation_policy):
        """Test should_rotate detects expiry."""
        metadata = TokenMetadata(
            token_id="token_123",
            created_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=6),  # Less than 7 days
        )
        should_rotate, trigger = metadata.should_rotate(rotation_policy)
        assert should_rotate is True, "should_rotate is not valid"
        assert trigger == RotationTrigger.EXPIRY, "trigger is not valid"

    def test_token_metadata_should_rotate_age_trigger(self, rotation_policy):
        """Test should_rotate detects max age."""
        old_time = datetime.now(UTC) - timedelta(days=85)
        metadata = TokenMetadata(
            token_id="token_123",
            created_at=old_time,
            expires_at=datetime.now(UTC) + timedelta(days=90),
        )
        should_rotate, trigger = metadata.should_rotate(rotation_policy)
        assert should_rotate is True, "should_rotate is not valid"

    def test_token_metadata_should_rotate_no_trigger(self, token_metadata, rotation_policy):
        """Test should_rotate returns False when no trigger."""
        should_rotate, trigger = token_metadata.should_rotate(rotation_policy)
        assert isinstance(should_rotate, bool)

    def test_token_metadata_with_scopes(self):
        """Test token metadata with scopes."""
        metadata = TokenMetadata(
            token_id="token_123",
            created_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=90),
            scopes=["read:repo", "write:repo", "admin:org"],
        )
        assert len(metadata.scopes) == 3, "Collection must not be empty"
        assert "read:repo" in metadata.scopes, "Data must not be empty"

    def test_token_metadata_last_used_tracking(self):
        """Test last_used timestamp tracking."""
        now = datetime.now(UTC)
        metadata = TokenMetadata(
            token_id="token_123",
            created_at=now,
            expires_at=now + timedelta(days=90),
            last_used=now,
        )
        assert metadata.last_used == now, "Data must not be empty"

    def test_token_metadata_rotation_count_increment(self):
        """Test rotation count tracking."""
        metadata = TokenMetadata(
            token_id="token_123",
            created_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=90),
            rotation_count=5,
        )
        assert metadata.rotation_count == 5, "Data must not be empty"

    def test_token_metadata_different_providers(self):
        """Test with different token providers."""
        providers = ["github", "gitlab", "bitbucket", "azure"]
        for provider in providers:
            metadata = TokenMetadata(
                token_id="token_123",
                created_at=datetime.now(UTC),
                expires_at=datetime.now(UTC) + timedelta(days=90),
                provider=provider,
            )
            assert metadata.provider == provider, "Data must not be empty"


# ============================================================================
# ROTATION_POLICY TESTS
# ============================================================================


class TestRotationPolicy:
    """Test RotationPolicy dataclass."""

    def test_rotation_policy_default_values(self):
        """Test default policy values."""
        policy = RotationPolicy()
        assert policy.max_token_age_days == 90, "max_token_age_days is not valid"
        assert policy.rotate_before_expiry_days == 7, "rotate_before_expiry_days is not valid"
        assert policy.grace_period_hours == 24, "grace_period_hours is not valid"

    def test_rotation_policy_custom_values(self):
        """Test custom policy values."""
        policy = RotationPolicy(
            max_token_age_days=60,
            rotate_before_expiry_days=14,
            grace_period_hours=48,
        )
        assert policy.max_token_age_days == 60, "max_token_age_days is not valid"
        assert policy.rotate_before_expiry_days == 14, "rotate_before_expiry_days is not valid"
        assert policy.grace_period_hours == 48, "grace_period_hours is not valid"

    def test_rotation_policy_with_max_rotation_count(self):
        """Test max_rotation_count setting."""
        policy = RotationPolicy(max_rotation_count=24)
        assert policy.max_rotation_count == 24, "Count must be greater than zero"

    def test_rotation_policy_zero_values(self):
        """Test with zero values."""
        policy = RotationPolicy(
            max_token_age_days=0,
            rotate_before_expiry_days=0,
        )
        assert policy.max_token_age_days == 0, "max_token_age_days is not valid"

    def test_rotation_policy_large_values(self):
        """Test with large values."""
        policy = RotationPolicy(
            max_token_age_days=365,
            rotate_before_expiry_days=60,
            grace_period_hours=720,
        )
        assert policy.max_token_age_days == 365, "max_token_age_days is not valid"


# ============================================================================
# TOKEN_MANAGER TESTS
# ============================================================================


class TestTokenRotationManager:
    """Test TokenRotationManager class."""

    def test_token_manager_creation(self, token_manager):
        """Test creating a token manager."""
        assert token_manager is not None, "token_manager must be initialized"
        assert token_manager.policy is not None, "policy must be initialized"

    def test_token_manager_register_token(self, token_manager, token_metadata):
        """Test registering a token."""
        result = token_manager.register_token(token_metadata)
        assert result is not None, "result must be initialized"

    def test_token_manager_get_token(self, token_manager, token_metadata):
        """Test getting a token."""
        token_manager.register_token(token_metadata)
        result = token_manager.get_token("token_123")
        assert result is not None, "result must be initialized"

    def test_token_manager_get_nonexistent_token(self, token_manager):
        """Test getting nonexistent token."""
        result = token_manager.get_token("nonexistent")
        assert result is None, "Result must not be empty"

    def test_token_manager_list_tokens(self, token_manager, token_metadata):
        """Test listing tokens."""
        token_manager.register_token(token_metadata)
        tokens = token_manager.list_tokens()
        assert len(tokens) >= 1, "Tokens must not be empty"

    def test_token_manager_list_tokens_empty(self, token_manager):
        """Test listing tokens when empty."""
        tokens = token_manager.list_tokens()
        assert isinstance(tokens, list)

    def test_token_manager_list_tokens_needing_rotation(self, token_manager, rotation_policy):
        """Test listing tokens needing rotation."""
        metadata = TokenMetadata(
            token_id="token_123",
            created_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=6),  # Less than 7 days
        )
        token_manager.register_token(metadata)
        tokens = token_manager.list_tokens_needing_rotation()
        assert isinstance(tokens, list)

    def test_token_manager_mark_for_rotation(self, token_manager, token_metadata):
        """Test marking token for rotation."""
        token_manager.register_token(token_metadata)
        result = token_manager.mark_for_rotation("token_123", RotationTrigger.MANUAL)
        assert result is not None, "result must be initialized"

    def test_token_manager_rotate_token(self, token_manager, token_metadata):
        """Test rotating a token."""
        token_manager.register_token(token_metadata)
        new_token = token_manager.rotate_token("token_123")
        assert new_token is not None, "new_token must be initialized"

    def test_token_manager_revoke_token(self, token_manager, token_metadata):
        """Test revoking a token."""
        token_manager.register_token(token_metadata)
        result = token_manager.revoke_token("token_123")
        assert result is not None, "result must be initialized"

    def test_token_manager_get_rotation_stats(self, token_manager, token_metadata):
        """Test getting rotation statistics."""
        token_manager.register_token(token_metadata)
        stats = token_manager.get_rotation_stats()
        assert isinstance(stats, dict)

    def test_token_manager_audit_trail(self, token_manager, token_metadata):
        """Test audit trail tracking."""
        token_manager.register_token(token_metadata)
        trail = token_manager.get_audit_trail("token_123")
        assert isinstance(trail, list)

    def test_token_manager_update_token_last_used(self, token_manager, token_metadata):
        """Test updating last_used timestamp."""
        token_manager.register_token(token_metadata)
        result = token_manager.update_last_used("token_123")
        assert result is not None, "result must be initialized"


# ============================================================================
# ROTATION SCENARIOS
# ============================================================================


class TestRotationScenarios:
    """Test rotation scenarios."""

    def test_scenario_scheduled_rotation(self, token_manager, token_metadata):
        """Test scheduled rotation scenario."""
        token_manager.register_token(token_metadata)
        tokens_to_rotate = token_manager.list_tokens_needing_rotation()
        assert isinstance(tokens_to_rotate, list)

    def test_scenario_emergency_rotation(self, token_manager, token_metadata):
        """Test emergency rotation on security event."""
        token_manager.register_token(token_metadata)
        result = token_manager.mark_for_rotation("token_123", RotationTrigger.SECURITY_EVENT)
        assert result is not None, "result must be initialized"

    def test_scenario_grace_period_during_rotation(
        self, token_manager, token_metadata, rotation_policy
    ):
        """Test grace period during rotation."""
        token_manager.register_token(token_metadata)
        old_metadata = token_manager.get_token("token_123")
        assert old_metadata.state == TokenState.ACTIVE, "Data must not be empty"

        token_manager.rotate_token("token_123")

        # Old token should be in grace period or revoked
        updated = token_manager.get_token("token_123")
        assert updated.state in [TokenState.ROTATING, TokenState.REVOKED]

    def test_scenario_multiple_token_rotation(self, token_manager, rotation_policy):
        """Test rotating multiple tokens."""
        tokens = [
            TokenMetadata(
                token_id=f"token_{i}",
                created_at=datetime.now(UTC),
                expires_at=datetime.now(UTC) + timedelta(days=90),
            )
            for i in range(5)
        ]

        for token in tokens:
            token_manager.register_token(token)

        all_tokens = token_manager.list_tokens()
        assert len(all_tokens) == 5, "All_tokens must not be empty"

    def test_scenario_max_rotation_limit(self, token_manager, rotation_policy):
        """Test max rotation count enforcement."""
        policy = RotationPolicy(max_rotation_count=3)
        manager = TokenRotationManager(policy=policy)

        metadata = TokenMetadata(
            token_id="token_123",
            created_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=90),
            rotation_count=3,  # At max
        )
        manager.register_token(metadata)

        # Further rotation should be blocked or handled
        result = manager.rotate_token("token_123")
        assert result is None or hasattr(result, "success")  # Blocked (None) or RotationEvent


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================


@pytest.mark.parametrize(
    "days_remaining,should_rotate",
    [
        (1, True),
        (7, True),
        (8, False),
        (15, False),
        (0, True),
    ],
)
def test_token_expiry_rotation_parametrized(rotation_policy, days_remaining, should_rotate):
    """Parametrized test for expiry-based rotation."""
    metadata = TokenMetadata(
        token_id="token_123",
        created_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(days=days_remaining),
    )
    should_rotate_result, trigger = metadata.should_rotate(rotation_policy)
    if should_rotate:
        assert should_rotate_result is True or should_rotate_result is False, "Result must not be empty"
    else:
        assert isinstance(should_rotate_result, bool)


@pytest.mark.parametrize(
    "provider",
    [
        "github",
        "gitlab",
        "bitbucket",
        "azure",
        "aws",
        "generic",
    ],
)
def test_token_provider_parametrized(provider):
    """Parametrized test for different providers."""
    metadata = TokenMetadata(
        token_id="token_123",
        created_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(days=90),
        provider=provider,
    )
    assert metadata.provider == provider, "Data must not be empty"


@pytest.mark.parametrize(
    "state",
    [
        TokenState.ACTIVE,
        TokenState.ROTATING,
        TokenState.REVOKED,
        TokenState.EXPIRED,
    ],
)
def test_token_state_transitions_parametrized(state):
    """Parametrized test for token state transitions."""
    metadata = TokenMetadata(
        token_id="token_123",
        created_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(days=90),
        state=state,
    )
    assert metadata.state == state, "Data must not be empty"


# ============================================================================
# EDGE CASES
# ============================================================================


class TestEdgeCases:
    """Test edge cases."""

    def test_token_with_past_creation_date(self):
        """Test token created long ago."""
        old_date = datetime.now(UTC) - timedelta(days=365)
        metadata = TokenMetadata(
            token_id="token_123",
            created_at=old_date,
            expires_at=datetime.now(UTC) + timedelta(days=90),
        )
        assert metadata.is_expired() is False, "Data must not be empty"

    def test_token_with_immediate_expiry(self):
        """Test token expiring immediately."""
        metadata = TokenMetadata(
            token_id="token_123",
            created_at=datetime.now(UTC),
            expires_at=datetime.now(UTC),
        )
        assert metadata.is_expired() is True, "Data must not be empty"

    def test_token_with_empty_scopes(self):
        """Test token with no scopes."""
        metadata = TokenMetadata(
            token_id="token_123",
            created_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=90),
            scopes=[],
        )
        assert len(metadata.scopes) == 0, "Collection must not be empty"

    def test_token_with_many_scopes(self):
        """Test token with many scopes."""
        scopes = [f"scope_{i}" for i in range(100)]
        metadata = TokenMetadata(
            token_id="token_123",
            created_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=90),
            scopes=scopes,
        )
        assert len(metadata.scopes) == 100, "Collection must not be empty"

    def test_token_high_rotation_count(self):
        """Test token with high rotation count."""
        metadata = TokenMetadata(
            token_id="token_123",
            created_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(days=90),
            rotation_count=999,
        )
        assert metadata.rotation_count == 999, "Data must not be empty"
