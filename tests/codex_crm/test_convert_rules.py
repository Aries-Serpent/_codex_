"""Comprehensive tests for codex_crm.convert.rules module."""

from __future__ import annotations

import pytest


class TestConversionFidelity:
    """Tests for ConversionFidelity dataclass."""

    def test_conversion_fidelity_creation(self):
        """Test ConversionFidelity instantiation."""
        from codex_crm.convert.rules import ConversionFidelity

        fidelity = ConversionFidelity(logic=0.8, data=0.9, sla=1.0, score=0.87)
        assert fidelity.logic == 0.8, "logic is not valid"
        assert fidelity.data == 0.9, "Data must not be empty"
        assert fidelity.sla == 1.0, "sla is not valid"
        assert fidelity.score == 0.87, "score is not valid"

    def test_conversion_fidelity_frozen(self):
        """Test that ConversionFidelity is immutable."""
        from codex_crm.convert.rules import ConversionFidelity

        fidelity = ConversionFidelity(logic=0.5, data=0.5, sla=0.5, score=0.5)
        with pytest.raises(AttributeError):
            fidelity.logic = 1.0


class TestTriggerToD365:
    """Tests for trigger_to_d365 function."""

    def test_trigger_to_d365_basic(self):
        """Test basic trigger conversion."""
        from codex_crm.convert.rules import trigger_to_d365

        rule = {
            "if": {"field": "status", "value": "open"},
            "then": [{"action": "notify"}],
            "sla": "standard",
        }
        result = trigger_to_d365(rule)

        assert result["type"] == "realtime_workflow", "Result must not be empty"
        assert result["conditions"] == {"field": "status", "value": "open"}
        assert result["actions"] == [{"action": "notify"}], "Result must not be empty"
        assert result["sla"] == "standard", "Result must not be empty"

    def test_trigger_to_d365_empty(self):
        """Test trigger conversion with empty rule."""
        from codex_crm.convert.rules import trigger_to_d365

        result = trigger_to_d365({})
        assert result["type"] == "realtime_workflow", "Result must not be empty"
        assert result["conditions"] == {}, "Result must not be empty"
        assert result["actions"] == [], "Result must not be empty"
        assert result["sla"] is None, "Result must not be empty"


class TestAutomationToD365:
    """Tests for automation_to_d365 function."""

    def test_automation_to_d365_basic(self):
        """Test basic automation conversion."""
        from codex_crm.convert.rules import automation_to_d365

        rule = {"schedule": "daily", "then": [{"action": "cleanup"}], "sla": "background"}
        result = automation_to_d365(rule)

        assert result["type"] == "background_workflow", "Result must not be empty"
        assert result["schedule"] == "daily", "Result must not be empty"
        assert result["actions"] == [{"action": "cleanup"}], "Result must not be empty"
        assert result["sla"] == "background", "Result must not be empty"

    def test_automation_to_d365_empty(self):
        """Test automation conversion with empty rule."""
        from codex_crm.convert.rules import automation_to_d365

        result = automation_to_d365({})
        assert result["type"] == "background_workflow", "Result must not be empty"
        assert result["schedule"] is None, "Result must not be empty"
        assert result["actions"] == [], "Result must not be empty"


class TestComputeFidelity:
    """Tests for compute_fidelity function."""

    def test_compute_fidelity_perfect_match(self):
        """Test fidelity computation with perfect match."""
        from codex_crm.convert.rules import compute_fidelity

        source = {"if": {"x": 1}, "then": [{"a": 1}], "sla": "standard"}
        target = {"conditions": {"x": 1}, "actions": [{"a": 1}], "sla": "standard"}

        fidelity = compute_fidelity(source, target)
        assert fidelity.logic == 1.0, "logic is not valid"
        assert fidelity.data == 1.0, "Data must not be empty"
        assert fidelity.sla == 1.0, "sla is not valid"
        assert fidelity.score == 1.0, "score is not valid"

    def test_compute_fidelity_no_match(self):
        """Test fidelity computation with no match."""
        from codex_crm.convert.rules import compute_fidelity

        source = {"if": {"x": 1}, "then": [{"a": 1}], "sla": "standard"}
        target = {"conditions": {"y": 2}, "actions": [{"b": 2}], "sla": "fast"}

        fidelity = compute_fidelity(source, target)
        assert fidelity.logic == 0.0, "logic is not valid"
        assert fidelity.data == 0.0, "Data must not be empty"
        assert fidelity.sla == 0.0, "sla is not valid"
        assert fidelity.score == 0.0, "score is not valid"

    def test_compute_fidelity_partial_match(self):
        """Test fidelity computation with partial match."""
        from codex_crm.convert.rules import compute_fidelity

        source = {"if": {"x": 1}, "then": [{"a": 1}], "sla": "standard"}
        target = {"conditions": {"x": 1}, "actions": [{"b": 2}], "sla": "standard"}

        fidelity = compute_fidelity(source, target)
        assert fidelity.logic == 1.0, "logic is not valid"
        assert fidelity.data == 0.0, "Data must not be empty"
        assert fidelity.sla == 1.0, "sla is not valid"


class TestZdTriggerToD365:
    """Tests for zd_trigger_to_d365 function."""

    def test_zd_trigger_basic(self):
        """Test Zendesk trigger conversion."""
        from codex_crm.convert.rules import zd_trigger_to_d365

        rule = {"if": [{"field": "status"}], "then": [{"action": "route"}]}
        result = zd_trigger_to_d365(rule)

        assert result["type"] == "realtime_workflow", "Result must not be empty"
        assert result["when"] == "create_or_update", "Result must not be empty"
        assert result["if"] == [{"field": "status"}], "Result must not be empty"
        assert result["then"] == [{"action": "route"}], "Result must not be empty"


class TestZdAutomationToD365:
    """Tests for zd_automation_to_d365 function."""

    def test_zd_automation_basic(self):
        """Test Zendesk automation conversion."""
        from codex_crm.convert.rules import zd_automation_to_d365

        rule = {"schedule": "hourly", "if": [{"cond": 1}], "then": [{"action": "process"}]}
        result = zd_automation_to_d365(rule)

        assert result["type"] == "background_workflow", "Result must not be empty"
        assert result["schedule"] == "hourly", "Result must not be empty"
        assert result["if"] == [{"cond": 1}], "Result must not be empty"
        assert result["then"] == [{"action": "process"}], "Result must not be empty"


class TestFidelityScore:
    """Tests for fidelity_score function."""

    def test_fidelity_score_all_perfect(self):
        """Test fidelity score with all perfect inputs."""
        from codex_crm.convert.rules import fidelity_score

        score = fidelity_score(1.0, 1.0, 1.0)
        assert score == 1.0, "score is not valid"

    def test_fidelity_score_all_zero(self):
        """Test fidelity score with all zero inputs."""
        from codex_crm.convert.rules import fidelity_score

        score = fidelity_score(0.0, 0.0, 0.0)
        assert score == 0.0, "score is not valid"

    def test_fidelity_score_default_weights(self):
        """Test fidelity score with default weights (0.5, 0.3, 0.2)."""
        from codex_crm.convert.rules import fidelity_score

        # Only logic perfect
        score = fidelity_score(1.0, 0.0, 0.0)
        assert score == pytest.approx(0.5), "score is not valid"

        # Only data perfect
        score = fidelity_score(0.0, 1.0, 0.0)
        assert score == pytest.approx(0.3), "score is not valid"

        # Only SLA perfect
        score = fidelity_score(0.0, 0.0, 1.0)
        assert score == pytest.approx(0.2), "score is not valid"

    def test_fidelity_score_custom_weights(self):
        """Test fidelity score with custom weights."""
        from codex_crm.convert.rules import fidelity_score

        score = fidelity_score(1.0, 1.0, 1.0, weight_logic=1.0, weight_data=1.0, weight_sla=1.0)
        assert score == 1.0, "score is not valid"

    def test_fidelity_score_invalid_inputs(self):
        """Test fidelity score with invalid inputs."""
        from codex_crm.convert.rules import fidelity_score

        with pytest.raises(ValueError, match="within \\[0, 1\\]"):
            fidelity_score(-0.1, 0.5, 0.5)

        with pytest.raises(ValueError, match="within \\[0, 1\\]"):
            fidelity_score(0.5, 1.5, 0.5)

        with pytest.raises(ValueError, match="within \\[0, 1\\]"):
            fidelity_score(0.5, 0.5, -1.0)

    def test_fidelity_score_zero_weights(self):
        """Test fidelity score with zero weights raises error."""
        from codex_crm.convert.rules import fidelity_score

        with pytest.raises(ValueError, match="positive"):
            fidelity_score(0.5, 0.5, 0.5, weight_logic=0, weight_data=0, weight_sla=0)
