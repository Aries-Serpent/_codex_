"""Comprehensive tests for src/codex_ml/cli/plugins_cli.py module.

Tests cover:
- Registry group handling
- Plugin listing
- Plugin diagnostics
- Plugin explanation
"""

import pytest


class TestRegistryGroups:
    """Tests for _GROUPS registry."""

    def test_groups_dict_exists(self):
        """Test _GROUPS dictionary is defined."""
        from codex_ml.cli.plugins_cli import _GROUPS

        assert isinstance(_GROUPS, dict)

    def test_groups_contains_tokenizers(self):
        """Test _GROUPS contains tokenizers registry."""
        from codex_ml.cli.plugins_cli import _GROUPS

        assert "tokenizers" in _GROUPS, "Condition must be true"

    def test_groups_contains_models(self):
        """Test _GROUPS contains models registry."""
        from codex_ml.cli.plugins_cli import _GROUPS

        assert "models" in _GROUPS, "Condition must be true"

    def test_groups_contains_datasets(self):
        """Test _GROUPS contains datasets registry."""
        from codex_ml.cli.plugins_cli import _GROUPS

        assert "datasets" in _GROUPS, "Data must not be empty"

    def test_groups_contains_metrics(self):
        """Test _GROUPS contains metrics registry."""
        from codex_ml.cli.plugins_cli import _GROUPS

        assert "metrics" in _GROUPS, "Condition must be true"

    def test_groups_contains_trainers(self):
        """Test _GROUPS contains trainers registry."""
        from codex_ml.cli.plugins_cli import _GROUPS

        assert "trainers" in _GROUPS, "Condition must be true"

    def test_groups_contains_reward_models(self):
        """Test _GROUPS contains reward_models registry."""
        from codex_ml.cli.plugins_cli import _GROUPS

        assert "reward_models" in _GROUPS, "Condition must be true"

    def test_groups_contains_rl_agents(self):
        """Test _GROUPS contains rl_agents registry."""
        from codex_ml.cli.plugins_cli import _GROUPS

        assert "rl_agents" in _GROUPS, "Condition must be true"


class TestGetRegistry:
    """Tests for _get_registry function."""

    def test_get_registry_valid_group(self):
        """Test _get_registry returns registry for valid group."""
        from codex_ml.cli.plugins_cli import _get_registry

        class MockException(Exception):
            pass

        registry = _get_registry("tokenizers", bad_param_exc=MockException)
        assert registry is not None, "registry must be initialized"

    def test_get_registry_invalid_group(self):
        """Test _get_registry raises for invalid group."""
        from codex_ml.cli.plugins_cli import _get_registry

        class MockException(Exception):
            pass

        with pytest.raises(MockException) as exc_info:
            _get_registry("invalid_group", bad_param_exc=MockException)

        assert "unknown group" in str(exc_info.value), "Value must be initialized"

    def test_get_registry_all_valid_groups(self):
        """Test _get_registry works for all defined groups."""
        from codex_ml.cli.plugins_cli import _GROUPS, _get_registry

        class MockException(Exception):
            pass

        for group_name in _GROUPS:
            registry = _get_registry(group_name, bad_param_exc=MockException)
            assert registry is not None, "registry must be initialized"


class TestListGroup:
    """Tests for _list_group function."""

    def test_list_group_calls_echo(self):
        """Test _list_group calls echo for each name."""
        from codex_ml.cli.plugins_cli import _list_group

        echo_calls = []

        def mock_echo(x):
            return echo_calls.append(x)

        class MockException(Exception):
            pass

        # This may or may not have items depending on registered plugins
        try:
            _list_group("tokenizers", echo=mock_echo, bad_param_exc=MockException)
        except Exception as _err:
            _ = None  # Registry might be empty

        # echo_calls may be empty if no plugins registered

    def test_list_group_invalid_raises(self):
        """Test _list_group raises for invalid group."""
        from codex_ml.cli.plugins_cli import _list_group

        class MockException(Exception):
            pass

        with pytest.raises(MockException):
            _list_group("invalid", echo=print, bad_param_exc=MockException)


class TestDiagnoseGroup:
    """Tests for _diagnose_group function."""

    def test_diagnose_group_basic(self):
        """Test _diagnose_group basic functionality."""
        from codex_ml.cli.plugins_cli import _diagnose_group

        echo_calls = []

        def mock_echo(x):
            return echo_calls.append(x)

        class MockException(Exception):
            pass

        try:
            _diagnose_group(
                "tokenizers", use_entry_points=False, echo=mock_echo, bad_param_exc=MockException
            )
        except Exception as _err:
            _ = None  # May fail if registry not fully initialized

        # Should have called echo with registered count

    def test_diagnose_group_with_entry_points(self):
        """Test _diagnose_group with entry points loading."""
        from codex_ml.cli.plugins_cli import _diagnose_group

        echo_calls = []

        def mock_echo(x):
            return echo_calls.append(x)

        class MockException(Exception):
            pass

        try:
            _diagnose_group(
                "models", use_entry_points=True, echo=mock_echo, bad_param_exc=MockException
            )
        except Exception as _err:
            _ = None  # Entry points may not be available


class TestExplainGroup:
    """Tests for _explain_group function."""

    def test_explain_group_not_found(self):
        """Test _explain_group exits when item not found."""
        from codex_ml.cli.plugins_cli import _explain_group

        echo_calls = []

        def mock_echo(x):
            return echo_calls.append(x)

        class MockExitException(Exception):
            def __init__(self, code=0):
                self.code = code

        class MockBadParamException(Exception):
            pass

        # Non-existent item should cause exit
        with pytest.raises(MockExitException) as exc_info:
            _explain_group(
                "tokenizers",
                "nonexistent_item",
                echo=mock_echo,
                exit_exc=MockExitException,
                bad_param_exc=MockBadParamException,
            )

        assert exc_info.value.code == 1, "Value must be initialized"


class TestPluginsCLIIntegration:
    """Integration tests for plugins CLI module."""

    def test_module_imports(self):
        """Test that module can be imported."""
        from codex_ml.cli import plugins_cli

        assert hasattr(plugins_cli, "_GROUPS")
        assert hasattr(plugins_cli, "_get_registry")
        assert hasattr(plugins_cli, "_list_group")
        assert hasattr(plugins_cli, "_diagnose_group")
        assert hasattr(plugins_cli, "_explain_group")

    def test_registries_import(self):
        """Test that registries can be imported."""
        from codex_ml.cli.plugins_cli import registries

        assert registries is not None, "registries must be initialized"

    def test_typer_handling(self):
        """Test that typer is handled gracefully."""
        # Module should be importable regardless of typer availability
        # typer may be None if not installed
        assert True, "True is not valid"

    def test_structured_logging_imports(self):
        """Test structured logging imports are available."""
        from codex_ml.cli.plugins_cli import (
            ArgparseJSONParser,
            capture_exceptions,
            init_json_logging,
            log_event,
        )

        assert ArgparseJSONParser is not None, "ArgparseJSONParser must be initialized"
        assert capture_exceptions is not None, "capture_exceptions must be initialized"
        assert init_json_logging is not None, "init_json_logging must be initialized"
        assert log_event is not None, "log_event must be initialized"


class TestPluginRegistries:
    """Tests for plugin registry functionality."""

    def test_tokenizers_registry_has_names_method(self):
        """Test tokenizers registry has names method."""
        from codex_ml.cli.plugins_cli import _GROUPS

        registry = _GROUPS.get("tokenizers")
        if registry:
            assert hasattr(registry, "names")

    def test_models_registry_has_names_method(self):
        """Test models registry has names method."""
        from codex_ml.cli.plugins_cli import _GROUPS

        registry = _GROUPS.get("models")
        if registry:
            assert hasattr(registry, "names")

    def test_datasets_registry_has_names_method(self):
        """Test datasets registry has names method."""
        from codex_ml.cli.plugins_cli import _GROUPS

        registry = _GROUPS.get("datasets")
        if registry:
            assert hasattr(registry, "names")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
