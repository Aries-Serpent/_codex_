"""Tests for entry-point plugin system."""
import pytest
from unittest.mock import Mock, patch
from packaging import version

from codex_ml.plugins.entry_points import (
    PluginInfo,
    PluginValidator,
    EntryPointPluginRegistry,
    discover_plugins,
)


class TestPluginInfo:
    """Test PluginInfo dataclass."""
    
    def test_create_plugin_info(self):
        """Test creating plugin info."""
        info = PluginInfo(
            name="test_plugin",
            entry_point_group="codex_ml.plugins",
            entry_point_name="test_plugin",
            module_name="test.plugin",
            version="1.0.0",
        )
        
        assert info.name == "test_plugin"
        assert info.version == "1.0.0"
        assert info.loaded is False
        assert info.error is None


class TestPluginValidator:
    """Test PluginValidator class."""
    
    def test_validator_creation(self):
        """Test validator creation."""
        validator = PluginValidator(codex_version="1.0.0")
        assert validator.codex_version == "1.0.0"
    
    def test_validate_compatible_version(self):
        """Test validation with compatible version."""
        validator = PluginValidator(codex_version="2.0.0")
        
        plugin_info = PluginInfo(
            name="test",
            entry_point_group="test",
            entry_point_name="test",
            module_name="test",
            required_codex_version="1.0.0",
        )
        
        is_valid, error = validator.validate_plugin(plugin_info)
        assert is_valid is True
        assert error is None
    
    def test_validate_incompatible_version(self):
        """Test validation with incompatible version."""
        validator = PluginValidator(codex_version="1.0.0")
        
        plugin_info = PluginInfo(
            name="test",
            entry_point_group="test",
            entry_point_name="test",
            module_name="test",
            required_codex_version="2.0.0",
        )
        
        is_valid, error = validator.validate_plugin(plugin_info)
        assert is_valid is False
        assert "requires codex_ml" in error
    
    def test_validate_missing_dependency(self):
        """Test validation with missing dependency."""
        validator = PluginValidator()
        
        plugin_info = PluginInfo(
            name="test",
            entry_point_group="test",
            entry_point_name="test",
            module_name="test",
            dependencies=["nonexistent_package>=1.0.0"],
        )
        
        is_valid, error = validator.validate_plugin(plugin_info)
        assert is_valid is False
        assert "Missing dependency" in error


class TestEntryPointPluginRegistry:
    """Test EntryPointPluginRegistry class."""
    
    def test_registry_creation(self):
        """Test registry creation."""
        registry = EntryPointPluginRegistry()
        assert registry is not None
        assert registry.validator is not None
    
    def test_default_groups(self):
        """Test default entry point groups."""
        registry = EntryPointPluginRegistry()
        assert "codex_ml.plugins" in registry.DEFAULT_GROUPS
        assert "codex_ml.tokenizers" in registry.DEFAULT_GROUPS
        assert "codex_ml.models" in registry.DEFAULT_GROUPS
    
    def test_list_plugins_empty(self):
        """Test listing plugins when none are discovered."""
        registry = EntryPointPluginRegistry()
        plugins = registry.list_plugins()
        assert isinstance(plugins, dict)
    
    def test_get_plugin_not_found(self):
        """Test getting non-existent plugin."""
        registry = EntryPointPluginRegistry()
        plugin = registry.get_plugin("test_group", "nonexistent")
        assert plugin is None
    
    def test_get_plugin_info_not_found(self):
        """Test getting info for non-existent plugin."""
        registry = EntryPointPluginRegistry()
        info = registry.get_plugin_info("test_group", "nonexistent")
        assert info is None


class TestPluginDiscovery:
    """Test plugin discovery functionality."""
    
    def test_discover_plugins_callable(self):
        """Test that discover_plugins function is callable."""
        assert callable(discover_plugins)
    
    @patch('importlib.metadata.entry_points')
    def test_discover_empty_group(self, mock_entry_points):
        """Test discovering plugins from empty group."""
        # Mock empty entry points
        mock_eps = Mock()
        mock_eps.select = Mock(return_value=[])
        mock_entry_points.return_value = mock_eps
        
        registry = EntryPointPluginRegistry()
        discovered = registry.discover_plugins(groups=["test_group"])
        
        assert "test_group" in discovered
        assert len(discovered["test_group"]) == 0


class TestPluginManagementScript:
    """Test plugin management script."""
    
    def test_script_exists(self):
        """Test that management script exists."""
        from pathlib import Path
        script_path = Path("scripts/manage_plugins.py")
        assert script_path.exists()
        assert script_path.is_file()
    
    def test_script_help(self):
        """Test script help output."""
        import subprocess
        result = subprocess.run(
            ["python", "scripts/manage_plugins.py", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "Plugin Management CLI" in result.stdout
    
    def test_script_list_command(self):
        """Test list command."""
        import subprocess
        result = subprocess.run(
            ["python", "scripts/manage_plugins.py", "list"],
            capture_output=True,
            text=True
        )
        # Command should run without error
        assert result.returncode == 0


@pytest.mark.integration
class TestRealPluginDiscovery:
    """Integration tests with real entry points."""
    
    def test_discover_codex_ml_plugins(self):
        """Test discovering actual codex_ml plugins."""
        import importlib.metadata
        
        try:
            eps = importlib.metadata.entry_points()
            # Just verify we can call entry_points
            assert eps is not None
        except Exception:
            pytest.skip("Entry points not available")
