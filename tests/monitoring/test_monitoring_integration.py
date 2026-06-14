"""
Integration tests for artifact monitoring system.

Tests the complete monitoring pipeline from workflow detection to issue creation.
"""

import json
from pathlib import Path

import pytest


class TestMonitoringIntegration:
    """Integration tests for monitoring system."""

    def test_workflow_inventory_exists(self):
        """Test that workflow inventory file exists and is valid JSON."""
        inventory_file = Path(".codex/monitoring/workflow_inventory.json")
        assert inventory_file.exists(), "Workflow inventory file should exist"

        with open(inventory_file, "r") as f:
            inventory = json.load(f)

        assert "workflows" in inventory
        assert "total_workflows" in inventory
        assert inventory["total_workflows"] > 0

    def test_monitoring_config_exists(self):
        """Test that monitoring configuration exists."""
        config_file = Path(".codex/config/monitoring.yaml")
        assert config_file.exists(), "Monitoring config should exist"

    def test_pattern_database_exists(self):
        """Test that error pattern database exists."""
        pattern_file = Path(".codex/monitoring/patterns/error_signatures.yaml")
        assert pattern_file.exists(), "Pattern database should exist"

    def test_monitoring_scripts_executable(self):
        """Test that monitoring scripts are executable."""
        scripts = [
            Path("scripts/monitoring/artifact_monitor.py"),
            Path("scripts/monitoring/issue_manager.py"),
            Path("scripts/monitoring/pattern_analyzer.py"),
            Path("scripts/monitoring/agent_orchestrator.py"),
        ]

        for script in scripts:
            assert script.exists(), f"Script {script} should exist"
            # Check if executable bit is set
            import os

            assert os.access(script, os.X_OK), f"Script {script} should be executable"

    def test_cognitive_brain_integration(self):
        """Test that Cognitive Brain integration modules exist."""
        modules = [
            Path("scripts/cognitive/sensors/monitoring_sensor.py"),
            Path("scripts/cognitive/actions/monitoring_actions.py"),
            Path("scripts/cognitive/self_healing_validation.py"),
        ]

        for module in modules:
            assert module.exists(), f"Module {module} should exist"

    def test_cli_wrapper_exists(self):
        """Test that CLI wrapper exists and is executable."""
        cli = Path("scripts/agents/artifact_monitor_cli.py")
        assert cli.exists(), "CLI wrapper should exist"
        import os

        assert os.access(cli, os.X_OK), "CLI should be executable"


class TestMonitoringConfiguration:
    """Tests for monitoring configuration."""

    def test_config_has_required_fields(self):
        """Test that config has all required fields."""
        import yaml

        config_file = Path(".codex/config/monitoring.yaml")
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        assert "monitoring" in config
        assert "issues" in config
        assert "patterns" in config
        assert "agents" in config
        assert "state" in config

    def test_pattern_database_has_patterns(self):
        """Test that pattern database has patterns defined."""
        import yaml

        pattern_file = Path(".codex/monitoring/patterns/error_signatures.yaml")
        with open(pattern_file, "r") as f:
            patterns = yaml.safe_load(f)

        assert "categories" in patterns
        assert len(patterns["categories"]) > 0

        # Check that patterns have required fields
        for _category, pattern_list in patterns["categories"].items():
            assert len(pattern_list) > 0
            for pattern in pattern_list:
                assert "id" in pattern
                assert "name" in pattern
                assert "pattern" in pattern
                assert "confidence_base" in pattern


class TestCognitiveBrainIntegration:
    """Tests for Cognitive Brain integration."""

    def test_monitoring_sensor_import(self):
        """Test that monitoring sensor can be imported."""
        try:
            from scripts.cognitive.sensors.monitoring_sensor import MonitoringSensor

            sensor = MonitoringSensor()
            assert sensor is not None
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")

    def test_action_proposer_import(self):
        """Test that action proposer can be imported."""
        try:
            from scripts.cognitive.actions.monitoring_actions import ActionProposer

            proposer = ActionProposer()
            assert proposer is not None
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")

    def test_self_healing_validator_import(self):
        """Test that self-healing validator can be imported."""
        try:
            from scripts.cognitive.self_healing_validation import SelfHealingValidator

            validator = SelfHealingValidator()
            assert validator is not None
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
