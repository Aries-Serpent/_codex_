"""
Tests for codex.mapping.models module.

This module contains tests for typed models for CSV-based mapping definitions.
"""

import pytest

# Skip all tests if pydantic is not available
pydantic = pytest.importorskip("pydantic")
ValidationError = pydantic.ValidationError


class TestRoutingPattern:
    """Tests for RoutingPattern model."""

    def test_basic_creation(self):
        """Test RoutingPattern basic creation."""
        from codex.mapping.models import RoutingPattern

        pattern = RoutingPattern(
            pattern_name="test_pattern",
            cdm_condition="condition_1",
            zd_destination_group="group_a",
            d365_queue="queue_1",
        )

        assert pattern.pattern_name == "test_pattern", "pattern_name is not valid"
        assert pattern.cdm_condition == "condition_1", "cdm_condition is not valid"
        assert pattern.zd_destination_group == "group_a", "zd_destination_group is not valid"
        assert pattern.d365_queue == "queue_1", "d365_queue is not valid"

    def test_from_dict(self):
        """Test RoutingPattern creation from dict."""
        from codex.mapping.models import RoutingPattern

        data = {
            "pattern_name": "pattern_1",
            "cdm_condition": "cond",
            "zd_destination_group": "group",
            "d365_queue": "queue",
        }

        pattern = RoutingPattern(**data)

        assert pattern.pattern_name == "pattern_1", "pattern_name is not valid"

    def test_extra_fields_forbidden(self):
        """Test extra fields are forbidden."""
        from codex.mapping.models import RoutingPattern

        with pytest.raises(ValidationError):
            RoutingPattern(
                pattern_name="test",
                cdm_condition="cond",
                zd_destination_group="group",
                d365_queue="queue",
                extra_field="not_allowed",
            )

    def test_missing_required_field(self):
        """Test missing required fields raise error."""
        from codex.mapping.models import RoutingPattern

        with pytest.raises(ValidationError):
            RoutingPattern(
                pattern_name="test",
                cdm_condition="cond",
                # Missing required fields
            )


class TestSlaParity:
    """Tests for SlaParity model."""

    def test_basic_creation(self):
        """Test SlaParity basic creation."""
        from codex.mapping.models import SlaParity

        sla = SlaParity(cdm_metric="response_time", zd_target_minutes=30, d365_target_minutes=45)

        assert sla.cdm_metric == "response_time", "Response must not be empty"
        assert sla.zd_target_minutes == 30, "zd_target_minutes is not valid"
        assert sla.d365_target_minutes == 45, "d365_target_minutes is not valid"

    def test_zero_minutes(self):
        """Test SlaParity with zero minutes."""
        from codex.mapping.models import SlaParity

        sla = SlaParity(cdm_metric="metric", zd_target_minutes=0, d365_target_minutes=0)

        assert sla.zd_target_minutes == 0, "zd_target_minutes is not valid"
        assert sla.d365_target_minutes == 0, "d365_target_minutes is not valid"

    def test_negative_minutes_rejected(self):
        """Test negative minutes are rejected."""
        from codex.mapping.models import SlaParity

        with pytest.raises(ValidationError):
            SlaParity(cdm_metric="metric", zd_target_minutes=-5, d365_target_minutes=10)

    def test_extra_fields_forbidden(self):
        """Test extra fields are forbidden."""
        from codex.mapping.models import SlaParity

        with pytest.raises(ValidationError):
            SlaParity(
                cdm_metric="metric",
                zd_target_minutes=10,
                d365_target_minutes=20,
                extra="not_allowed",
            )


class TestModuleExports:
    """Tests for module exports."""

    def test_all_exports(self):
        """Test __all__ exports."""
        from codex.mapping.models import __all__

        assert "RoutingPattern" in __all__, "Condition must be true"
        assert "SlaParity" in __all__, "Condition must be true"
