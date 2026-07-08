"""Unit tests for Dynamics 365 SLA Policy models."""

from datetime import UTC, datetime, timedelta

import pytest

from codex.dynamics.model.sla import (
    SLAMetric,
    SLAPauseCondition,
    SLAPolicy,
    SLAPolicyRegistry,
)


class TestSLAPauseCondition:
    """Test SLAPauseCondition model."""

    def test_create_pause_condition(self):
        """Test creating a pause condition."""
        condition = SLAPauseCondition(
            field="status",
            operator="equals",
            value="paused",
        )
        assert condition.field == "status", "field is not valid"
        assert condition.operator == "equals", "operator is not valid"
        assert condition.value == "paused", "Value must be initialized"

    def test_evaluate_equals(self):
        """Test evaluating equals operator."""
        condition = SLAPauseCondition(
            field="status",
            operator="equals",
            value="paused",
        )

        assert condition.evaluate({"status": "paused"}) is True, "Condition must be true"
        assert condition.evaluate({"status": "active"}) is False, "Condition must be true"

    def test_evaluate_contains(self):
        """Test evaluating contains operator."""
        condition = SLAPauseCondition(
            field="tags",
            operator="contains",
            value="hold",
        )

        assert condition.evaluate({"tags": "on_hold"}) is True, "Condition must be true"
        assert condition.evaluate({"tags": "active"}) is False, "Condition must be true"


class TestSLAPolicy:
    """Test SLAPolicy model."""

    def test_create_policy(self):
        """Test creating an SLA policy."""
        policy = SLAPolicy(
            name="test_policy",
            metric=SLAMetric.FIRST_RESPONSE,
            target_minutes=60,
            effective_date=datetime.now(UTC).isoformat(),
        )
        assert policy.name == "test_policy", "name is not valid"
        assert policy.metric == SLAMetric.FIRST_RESPONSE, "Response must not be empty"
        assert policy.target_minutes == 60, "target_minutes is not valid"

    def test_policy_with_pause_conditions(self):
        """Test policy with pause conditions."""
        condition = SLAPauseCondition(
            field="status",
            operator="equals",
            value="paused",
        )

        policy = SLAPolicy(
            name="test_policy",
            metric=SLAMetric.RESOLUTION,
            target_minutes=480,
            pause_conditions=[condition],
            effective_date=datetime.now(UTC).isoformat(),
        )

        assert len(policy.pause_conditions) == 1, "Collection must not be empty"
        assert policy.is_paused({"status": "paused"}) is True, "Condition must be true"
        assert policy.is_paused({"status": "active"}) is False, "Condition must be true"

    def test_calculate_deadline(self):
        """Test SLA deadline calculation."""
        policy = SLAPolicy(
            name="test_policy",
            metric=SLAMetric.FIRST_RESPONSE,
            target_minutes=60,
            effective_date=datetime.now(UTC).isoformat(),
            business_hours_only=False,
        )

        start = datetime.now(UTC)
        deadline = policy.calculate_deadline(start)

        expected = start + timedelta(minutes=60)
        assert abs((deadline - expected).total_seconds()) < 1, "Condition must be true"

    def test_policy_diff(self):
        """Test diff method for policy comparison."""
        policy1 = SLAPolicy(
            name="test_policy",
            metric=SLAMetric.FIRST_RESPONSE,
            target_minutes=60,
            effective_date=datetime.now(UTC).isoformat(),
        )

        policy2 = SLAPolicy(
            name="test_policy",
            metric=SLAMetric.FIRST_RESPONSE,
            target_minutes=120,  # Changed
            effective_date=datetime.now(UTC).isoformat(),
        )

        patches = policy1.diff(policy2)
        assert len(patches) > 0, "Patches must not be empty"
        assert any(p["path"] == "/target_minutes" for p in patches), "Condition must be true"

    def test_to_d365_format(self):
        """Test conversion to D365 API format."""
        condition = SLAPauseCondition(
            field="status",
            operator="equals",
            value="paused",
        )

        policy = SLAPolicy(
            name="test_policy",
            metric=SLAMetric.FIRST_RESPONSE,
            target_minutes=60,
            pause_conditions=[condition],
            effective_date=datetime.now(UTC).isoformat(),
            business_hours_only=True,
        )

        d365_format = policy.to_d365_format()

        assert d365_format["name"] == "test_policy", "d365_f is not valid"
        assert d365_format["slametric"] == "first_response", "Response must not be empty"
        assert d365_format["successconditions"]["target_minutes"] == 60, "d365_f is not valid"
        assert len(d365_format["pauseconfiguration"]) == 1, "Collection must not be empty"


class TestSLAPolicyRegistry:
    """Test SLAPolicyRegistry model."""

    def test_create_registry(self):
        """Test creating a policy registry."""
        registry = SLAPolicyRegistry(
            policies=[],
            last_updated=datetime.now(UTC).isoformat(),
        )
        assert len(registry.policies) == 0, "Collection must not be empty"

    def test_add_policy(self):
        """Test adding a policy to registry."""
        registry = SLAPolicyRegistry(
            policies=[],
            last_updated=datetime.now(UTC).isoformat(),
        )

        policy = SLAPolicy(
            name="test_policy",
            metric=SLAMetric.FIRST_RESPONSE,
            target_minutes=60,
            effective_date=datetime.now(UTC).isoformat(),
        )

        registry.add_policy(policy)
        assert len(registry.policies) == 1, "Collection must not be empty"

    def test_get_policy(self):
        """Test retrieving a policy from registry."""
        policy = SLAPolicy(
            name="test_policy",
            metric=SLAMetric.FIRST_RESPONSE,
            target_minutes=60,
            version="1.0.0",
            effective_date=datetime.now(UTC).isoformat(),
        )

        registry = SLAPolicyRegistry(
            policies=[policy],
            last_updated=datetime.now(UTC).isoformat(),
        )

        retrieved = registry.get_policy("test_policy")
        assert retrieved is not None, "retrieved must be initialized"
        assert retrieved.name == "test_policy", "name is not valid"

        missing = registry.get_policy("nonexistent")
        assert missing is None, "missing is not valid"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
