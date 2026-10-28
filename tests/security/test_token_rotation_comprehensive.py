"""Comprehensive tests for security.token_rotation module.

This module tests automated token rotation including:
- Token rotation triggers
- Rotation policies
- Token lifecycle management
- Grace periods
- Audit trails
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from itertools import count
from unittest.mock import Mock

import pytest

from security import token_rotation
from security.token_rotation import (
    RotationPolicy,
    RotationTrigger,
    TokenMetadata,
    TokenRotationManager,
    TokenState,
)

NOW = datetime(2026, 1, 15, 12, tzinfo=UTC)
OLD_TOKEN = "synthetic-old-token"
NEW_TOKEN = "synthetic-new-token"


@pytest.fixture(autouse=True)
def clock(monkeypatch):
    """Freeze both test and rotation clocks; advance explicitly without sleeping."""

    class Clock(datetime):
        current = NOW

        @classmethod
        def now(cls, tz=None):
            if tz is None:
                return cls.current.replace(tzinfo=None)
            return cls.current.astimezone(tz)

        @classmethod
        def advance(cls, delta):
            cls.current += delta

    monkeypatch.setattr(token_rotation, "datetime", Clock)
    monkeypatch.setitem(globals(), "datetime", Clock)
    event_ids = count(1)
    monkeypatch.setattr(
        token_rotation.secrets, "token_hex", lambda size: f"{next(event_ids):0{2 * size}x}"
    )
    return Clock


def token_hash(value):
    """Compute the documented truncated audit hash independently of the manager."""
    return hashlib.sha256(value.encode()).hexdigest()[:16]


def audit_records(manager):
    """Read the public JSONL audit artifact, not a nonexistent query API."""
    return [json.loads(line) for line in manager.audit_log_path.read_text().splitlines()]


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def rotation_policy():
    """Create a rotation policy."""
    return RotationPolicy(
        max_age_days=90,
        rotate_before_expiry_days=7,
        grace_period_hours=24,
        min_rotation_interval_hours=1,
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
def token_generator():
    """A deterministic, non-exhausting local generator; never a live provider."""
    return Mock(return_value=NEW_TOKEN)


@pytest.fixture
def token_manager(rotation_policy, token_generator, tmp_path):
    """Keep every audit write in a fresh temporary directory."""
    return TokenRotationManager(
        policy=rotation_policy,
        audit_log_path=tmp_path / "audit" / "rotation.jsonl",
        token_generator=token_generator,
    )


@pytest.fixture
def registered_token(token_manager, token_metadata):
    """Register through the supported value/expiry API, not a metadata argument."""
    return token_manager.register_token(
        token_id=token_metadata.token_id,
        token_value=OLD_TOKEN,
        expires_at=token_metadata.expires_at,
        scopes=token_metadata.scopes,
        provider=token_metadata.provider,
    )


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
        assert token_metadata.days_until_expiry() == 90

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
        old_time = datetime.now(UTC) - timedelta(days=90)
        metadata = TokenMetadata(
            token_id="token_123",
            created_at=old_time,
            expires_at=datetime.now(UTC) + timedelta(days=90),
        )
        should_rotate, trigger = metadata.should_rotate(rotation_policy)
        assert (should_rotate, trigger) == (True, RotationTrigger.SCHEDULED)

    def test_token_metadata_should_rotate_no_trigger(self, token_metadata, rotation_policy):
        """Test should_rotate returns False when no trigger."""
        assert token_metadata.should_rotate(rotation_policy) == (False, None)

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
        assert policy.to_dict() == {
            "max_age_days": 90,
            "rotate_before_expiry_days": 14,
            "grace_period_hours": 24,
            "auto_rotate_on_exposure": True,
            "auto_rotate_on_security_event": True,
            "min_rotation_interval_hours": 1,
        }

    def test_rotation_policy_custom_values(self):
        """Test custom policy values."""
        policy = RotationPolicy(
            max_age_days=60,
            rotate_before_expiry_days=14,
            grace_period_hours=48,
            auto_rotate_on_exposure=False,
            auto_rotate_on_security_event=False,
            min_rotation_interval_hours=2,
        )
        assert policy.to_dict() == {
            "max_age_days": 60,
            "rotate_before_expiry_days": 14,
            "grace_period_hours": 48,
            "auto_rotate_on_exposure": False,
            "auto_rotate_on_security_event": False,
            "min_rotation_interval_hours": 2,
        }

    def test_rotation_policy_with_min_rotation_interval(self):
        """The supported storm guard is a minimum interval, not a count cap."""
        policy = RotationPolicy(min_rotation_interval_hours=24)
        assert policy.min_rotation_interval_hours == 24
        assert policy.to_dict()["min_rotation_interval_hours"] == 24

    def test_rotation_policy_zero_values(self):
        """Test with zero values."""
        policy = RotationPolicy(
            max_age_days=0,
            rotate_before_expiry_days=0,
        )
        metadata = TokenMetadata("new", NOW, NOW + timedelta(days=90))
        assert policy.max_age_days == 0
        assert metadata.should_rotate(policy) == (True, RotationTrigger.SCHEDULED)

    def test_rotation_policy_large_values(self):
        """Test with large values."""
        policy = RotationPolicy(
            max_age_days=365,
            rotate_before_expiry_days=60,
            grace_period_hours=720,
        )
        metadata = TokenMetadata("young", NOW - timedelta(days=364), NOW + timedelta(days=90))
        assert policy.max_age_days == 365
        assert policy.grace_period_hours == 720
        assert metadata.should_rotate(policy) == (False, None)


# ============================================================================
# TOKEN_MANAGER TESTS
# ============================================================================


class TestTokenRotationManager:
    """Test TokenRotationManager class."""

    def test_token_manager_creation(
        self, token_manager, rotation_policy, token_generator, tmp_path
    ):
        """Test creating a token manager."""
        assert token_manager.policy is rotation_policy
        assert token_manager.token_generator is token_generator
        assert token_manager.tokens == {}
        assert token_manager.audit_log_path == tmp_path / "audit" / "rotation.jsonl"
        assert not token_manager.audit_log_path.exists()

    def test_token_manager_register_token(self, token_manager, token_metadata, registered_token):
        """Test registering a token."""
        assert registered_token == token_metadata
        assert token_manager.tokens == {"token_123": registered_token}
        assert registered_token.created_at == NOW
        assert not token_manager.audit_log_path.exists()

    def test_token_manager_get_token(self, token_manager, registered_token):
        """Registered metadata is exposed by the public tokens mapping."""
        assert token_manager.tokens["token_123"] is registered_token

    def test_token_manager_get_nonexistent_token(self, token_manager):
        """An unknown ID has neither metadata nor a pending rotation."""
        assert token_manager.tokens.get("nonexistent") is None
        assert token_manager.check_rotation_needed("nonexistent") == (False, None)

    def test_token_manager_list_tokens(self, token_manager, registered_token):
        """The schedule reports exact state and policy decisions."""
        assert token_manager.get_rotation_schedule() == [
            {
                "token_id": registered_token.token_id,
                "days_until_expiry": 90,
                "rotation_needed": False,
                "trigger": None,
                "state": "active",
                "rotation_count": 0,
            }
        ]

    def test_token_manager_list_tokens_empty(self, token_manager):
        """Test listing tokens when empty."""
        assert token_manager.get_rotation_schedule() == []

    def test_token_manager_list_tokens_needing_rotation(self, token_manager, registered_token):
        """Only the expiring token is due; the schedule is sorted by expiry."""
        expiring = token_manager.register_token(
            "expiring", "synthetic-expiring-token", NOW + timedelta(days=6)
        )
        assert token_manager.check_rotation_needed(expiring.token_id) == (
            True,
            RotationTrigger.EXPIRY,
        )
        assert token_manager.check_rotation_needed(registered_token.token_id) == (False, None)
        schedule = token_manager.get_rotation_schedule()
        assert [row["token_id"] for row in schedule] == ["expiring", "token_123"]
        assert [row["rotation_needed"] for row in schedule] == [True, False]
        assert [row["trigger"] for row in schedule] == ["expiry", None]

    def test_token_manager_manual_rotation(self, token_manager, registered_token, token_generator):
        """Explicit replacement values bypass generation and emit a success event."""
        event = token_manager.rotate_token(
            registered_token.token_id,
            RotationTrigger.MANUAL,
            OLD_TOKEN,
            new_token="synthetic-explicit-token",
            metadata={"reason": "planned replacement"},
        )
        assert event.success is True
        assert event.error_message is None
        assert event.trigger is RotationTrigger.MANUAL
        assert event.timestamp == NOW
        assert event.old_token_hash == token_hash(OLD_TOKEN)
        assert event.new_token_hash == token_hash("synthetic-explicit-token")
        assert event.metadata == {"reason": "planned replacement"}
        token_generator.assert_not_called()

    def test_token_manager_rotate_token(self, token_manager, registered_token, token_generator):
        """Generated replacement returns an event, not a raw token."""
        event = token_manager.rotate_token(
            registered_token.token_id, RotationTrigger.MANUAL, OLD_TOKEN
        )
        assert event.success is True
        assert event.token_id == registered_token.token_id
        assert event.old_token_hash == token_hash(OLD_TOKEN)
        assert event.new_token_hash == token_hash(NEW_TOKEN)
        assert event.old_token_hash != event.new_token_hash
        assert registered_token.rotation_count == 1
        assert registered_token.state is TokenState.ROTATING
        token_generator.assert_called_once_with()

    def test_token_manager_rotation_throttled(
        self, token_manager, registered_token, token_generator
    ):
        """An immediate repeat is rejected without generation or state/audit mutation."""
        first = token_manager.rotate_token(
            registered_token.token_id, RotationTrigger.MANUAL, OLD_TOKEN
        )
        audit_before = token_manager.audit_log_path.read_bytes()
        rejected = token_manager.rotate_token(
            registered_token.token_id, RotationTrigger.MANUAL, NEW_TOKEN
        )
        assert first.success is True
        assert rejected.success is False
        assert rejected.error_message == "Rotation throttled - minimum interval not met"
        assert rejected.old_token_hash == token_hash(NEW_TOKEN)
        assert rejected.new_token_hash == ""
        assert registered_token.rotation_count == 1
        assert registered_token.state is TokenState.ROTATING
        assert token_manager.audit_log_path.read_bytes() == audit_before
        token_generator.assert_called_once_with()

    def test_token_manager_schedule_after_rotation(self, token_manager, registered_token):
        """The public schedule reflects successful rotation state and count."""
        token_manager.rotate_token(registered_token.token_id, RotationTrigger.MANUAL, OLD_TOKEN)
        assert token_manager.get_rotation_schedule() == [
            {
                "token_id": registered_token.token_id,
                "days_until_expiry": 90,
                "rotation_needed": False,
                "trigger": None,
                "state": "rotating",
                "rotation_count": 1,
            }
        ]

    def test_token_manager_audit_trail(self, token_manager, registered_token):
        """The JSONL record contains event context and hashes, never raw values."""
        event = token_manager.rotate_token(
            registered_token.token_id,
            RotationTrigger.POLICY_CHANGE,
            OLD_TOKEN,
            metadata={"policy_version": 2},
        )
        assert audit_records(token_manager) == [
            {
                "event_id": event.event_id,
                "token_id": registered_token.token_id,
                "timestamp": NOW.isoformat(),
                "trigger": "policy_change",
                "old_token_hash": token_hash(OLD_TOKEN),
                "new_token_hash": token_hash(NEW_TOKEN),
                "success": True,
                "error_message": None,
                "metadata": {"policy_version": 2},
            }
        ]
        audit_text = token_manager.audit_log_path.read_text()
        assert OLD_TOKEN not in audit_text
        assert NEW_TOKEN not in audit_text

    def test_token_manager_rotation_preserves_metadata(self, token_manager, registered_token):
        """Rotation tracks lifecycle but does not invent vault/usage operations."""
        registered_token.last_used = NOW - timedelta(hours=2)
        token_manager.rotate_token(registered_token.token_id, RotationTrigger.MANUAL, OLD_TOKEN)
        assert registered_token.last_used == NOW - timedelta(hours=2)
        assert registered_token.scopes == ["read:repo", "write:repo"]
        assert registered_token.provider == "github"
        assert registered_token.created_at == NOW
        assert registered_token.expires_at == NOW + timedelta(days=90)


# ============================================================================
# ROTATION SCENARIOS
# ============================================================================


class TestRotationScenarios:
    """Test rotation scenarios."""

    def test_scenario_scheduled_rotation(self, token_manager, registered_token, clock):
        """Age-based scheduling produces the trigger consumed by rotation."""
        # Keep expiry well outside the window while crossing the age boundary.
        registered_token.expires_at = NOW + timedelta(days=180)
        clock.advance(timedelta(days=90))
        needed, trigger = token_manager.check_rotation_needed(registered_token.token_id)
        assert needed is True
        assert trigger is RotationTrigger.SCHEDULED
        event = token_manager.rotate_token(registered_token.token_id, trigger, OLD_TOKEN)
        assert event.success is True
        assert registered_token.rotation_count == 1
        assert registered_token.state is TokenState.ROTATING
        assert token_manager.check_rotation_needed(registered_token.token_id) == (False, None)

    @pytest.mark.parametrize("event_type", ["exposure", "breach", "compromise"])
    def test_scenario_emergency_rotation(self, token_manager, registered_token, event_type):
        """A targeted incident rotates only affected registered IDs."""
        unaffected = token_manager.register_token(
            "unaffected", "synthetic-unaffected-token", NOW + timedelta(days=90)
        )
        events = token_manager.handle_security_event(
            event_type,
            affected_token_ids=[registered_token.token_id, "unknown"],
            metadata={"incident_id": "local-test"},
        )
        assert len(events) == 1
        assert events[0].success is True
        assert events[0].trigger is RotationTrigger.SECURITY_EVENT
        assert events[0].token_id == registered_token.token_id
        assert events[0].metadata == {
            "security_event_type": event_type,
            "incident_id": "local-test",
        }
        assert registered_token.state is TokenState.ROTATING
        assert registered_token.rotation_count == 1
        assert unaffected.state is TokenState.ACTIVE
        assert unaffected.rotation_count == 0

    def test_scenario_grace_period_during_rotation(
        self, token_manager, registered_token, rotation_policy
    ):
        """Successful rotation enters ROTATING, the documented grace-period state.

        This metadata manager has no vault activation/revocation API. Do not
        equate a rotation event with provider-side revocation or secret storage.
        """
        assert rotation_policy.grace_period_hours == 24
        assert registered_token.state is TokenState.ACTIVE
        event = token_manager.rotate_token(
            registered_token.token_id, RotationTrigger.MANUAL, OLD_TOKEN
        )
        assert event.success is True
        assert token_manager.tokens[registered_token.token_id] is registered_token
        assert registered_token.state is TokenState.ROTATING

    def test_scenario_multiple_token_rotation(self, token_manager, token_generator):
        """A global incident rotates every token and appends one record per token."""
        for i in range(5):
            token_manager.register_token(
                f"token_{i}", f"synthetic-token-{i}", NOW + timedelta(days=90)
            )
        events = token_manager.handle_security_event("breach")
        assert [event.token_id for event in events] == [f"token_{i}" for i in range(5)]
        assert all(event.success is True for event in events)
        assert len({event.event_id for event in events}) == 5
        assert all(meta.state is TokenState.ROTATING for meta in token_manager.tokens.values())
        assert all(meta.rotation_count == 1 for meta in token_manager.tokens.values())
        assert [row["token_id"] for row in audit_records(token_manager)] == [
            f"token_{i}" for i in range(5)
        ]
        assert token_generator.call_count == 5

    def test_scenario_min_rotation_interval(self, token_manager, registered_token, clock):
        """Reject just before the minimum interval; accept exactly at the boundary."""
        first = token_manager.rotate_token(
            registered_token.token_id, RotationTrigger.MANUAL, OLD_TOKEN
        )
        clock.advance(timedelta(hours=1) - timedelta(microseconds=1))
        rejected = token_manager.rotate_token(
            registered_token.token_id, RotationTrigger.MANUAL, NEW_TOKEN
        )
        assert first.success is True
        assert rejected.success is False
        assert rejected.error_message == "Rotation throttled - minimum interval not met"
        assert registered_token.rotation_count == 1
        clock.advance(timedelta(microseconds=1))
        accepted = token_manager.rotate_token(
            registered_token.token_id,
            RotationTrigger.MANUAL,
            NEW_TOKEN,
            new_token="synthetic-next-token",
        )
        assert accepted.success is True
        assert accepted.error_message is None
        assert accepted.new_token_hash == token_hash("synthetic-next-token")
        assert registered_token.rotation_count == 2
        assert [row["timestamp"] for row in audit_records(token_manager)] == [
            NOW.isoformat(),
            (NOW + timedelta(hours=1)).isoformat(),
        ]

    @pytest.mark.parametrize(
        "event_type,policy_field",
        [
            ("exposure", "auto_rotate_on_exposure"),
            ("breach", "auto_rotate_on_security_event"),
            ("compromise", "auto_rotate_on_security_event"),
        ],
    )
    def test_scenario_auto_rotation_disabled(
        self, token_manager, registered_token, token_generator, event_type, policy_field
    ):
        """Policy opt-outs cause no rotation, generation, or audit write."""
        setattr(token_manager.policy, policy_field, False)
        assert token_manager.handle_security_event(event_type) == []
        assert registered_token.state is TokenState.ACTIVE
        assert registered_token.rotation_count == 0
        assert not token_manager.audit_log_path.exists()
        token_generator.assert_not_called()

    def test_scenario_unknown_affected_token(
        self, token_manager, registered_token, token_generator
    ):
        """An incident affecting only an unknown ID leaves registered tokens alone."""
        assert token_manager.handle_security_event("breach", ["unknown"]) == []
        assert registered_token.state is TokenState.ACTIVE
        assert registered_token.rotation_count == 0
        assert not token_manager.audit_log_path.exists()
        token_generator.assert_not_called()


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
    expected_trigger = RotationTrigger.EXPIRY if should_rotate else None
    assert metadata.should_rotate(rotation_policy) == (should_rotate, expected_trigger)


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
        """Test the first instant after expiry without relying on wall-clock drift."""
        metadata = TokenMetadata(
            token_id="token_123",
            created_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) - timedelta(microseconds=1),
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
