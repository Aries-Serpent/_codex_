"""Unit tests for Dynamics 365 SLA Policy models."""

import pytest
from datetime import datetime, timedelta

from src.codex.dynamics.model.sla import (
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
        assert condition.field == "status"
        assert condition.operator == "equals"
        assert condition.value == "paused"
    
    def test_evaluate_equals(self):
        """Test evaluating equals operator."""
        condition = SLAPauseCondition(
            field="status",
            operator="equals",
            value="paused",
        )
        
        assert condition.evaluate({"status": "paused"}) is True
        assert condition.evaluate({"status": "active"}) is False
    
    def test_evaluate_contains(self):
        """Test evaluating contains operator."""
        condition = SLAPauseCondition(
            field="tags",
            operator="contains",
            value="hold",
        )
        
        assert condition.evaluate({"tags": "on_hold"}) is True
        assert condition.evaluate({"tags": "active"}) is False


class TestSLAPolicy:
    """Test SLAPolicy model."""
    
    def test_create_policy(self):
        """Test creating an SLA policy."""
        policy = SLAPolicy(
            name="test_policy",
            metric=SLAMetric.FIRST_RESPONSE,
            target_minutes=60,
            effective_date=datetime.now().isoformat(),
        )
        assert policy.name == "test_policy"
        assert policy.metric == SLAMetric.FIRST_RESPONSE
        assert policy.target_minutes == 60
    
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
            effective_date=datetime.now().isoformat(),
        )
        
        assert len(policy.pause_conditions) == 1
        assert policy.is_paused({"status": "paused"}) is True
        assert policy.is_paused({"status": "active"}) is False
    
    def test_calculate_deadline(self):
        """Test SLA deadline calculation."""
        policy = SLAPolicy(
            name="test_policy",
            metric=SLAMetric.FIRST_RESPONSE,
            target_minutes=60,
            effective_date=datetime.now().isoformat(),
            business_hours_only=False,
        )
        
        start = datetime.now()
        deadline = policy.calculate_deadline(start)
        
        expected = start + timedelta(minutes=60)
        assert abs((deadline - expected).total_seconds()) < 1
    
    def test_policy_diff(self):
        """Test diff method for policy comparison."""
        policy1 = SLAPolicy(
            name="test_policy",
            metric=SLAMetric.FIRST_RESPONSE,
            target_minutes=60,
            effective_date=datetime.now().isoformat(),
        )
        
        policy2 = SLAPolicy(
            name="test_policy",
            metric=SLAMetric.FIRST_RESPONSE,
            target_minutes=120,  # Changed
            effective_date=datetime.now().isoformat(),
        )
        
        patches = policy1.diff(policy2)
        assert len(patches) > 0
        assert any(p["path"] == "/target_minutes" for p in patches)
    
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
            effective_date=datetime.now().isoformat(),
            business_hours_only=True,
        )
        
        d365_format = policy.to_d365_format()
        
        assert d365_format["name"] == "test_policy"
        assert d365_format["slametric"] == "first_response"
        assert d365_format["successconditions"]["target_minutes"] == 60
        assert len(d365_format["pauseconfiguration"]) == 1


class TestSLAPolicyRegistry:
    """Test SLAPolicyRegistry model."""
    
    def test_create_registry(self):
        """Test creating a policy registry."""
        registry = SLAPolicyRegistry(
            policies=[],
            last_updated=datetime.now().isoformat(),
        )
        assert len(registry.policies) == 0
    
    def test_add_policy(self):
        """Test adding a policy to registry."""
        registry = SLAPolicyRegistry(
            policies=[],
            last_updated=datetime.now().isoformat(),
        )
        
        policy = SLAPolicy(
            name="test_policy",
            metric=SLAMetric.FIRST_RESPONSE,
            target_minutes=60,
            effective_date=datetime.now().isoformat(),
        )
        
        registry.add_policy(policy)
        assert len(registry.policies) == 1
    
    def test_get_policy(self):
        """Test retrieving a policy from registry."""
        policy = SLAPolicy(
            name="test_policy",
            metric=SLAMetric.FIRST_RESPONSE,
            target_minutes=60,
            version="1.0.0",
            effective_date=datetime.now().isoformat(),
        )
        
        registry = SLAPolicyRegistry(
            policies=[policy],
            last_updated=datetime.now().isoformat(),
        )
        
        retrieved = registry.get_policy("test_policy")
        assert retrieved is not None
        assert retrieved.name == "test_policy"
        
        missing = registry.get_policy("nonexistent")
        assert missing is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
