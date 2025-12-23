"""Tests for AST plugin system."""
import pytest
from pathlib import Path

from codex.ast.plugins import ASTPlugin, PluginMetadata
from codex.ast.plugins.loader import PluginLoader
from codex.ast.plugins.python_plugin import PythonPlugin


class TestPythonPlugin:
    """Test Python plugin implementation."""
    
    def test_plugin_metadata(self):
        """Test plugin provides valid metadata."""
        plugin = PythonPlugin()
        metadata = plugin.metadata
        
        assert metadata.name == "python"
        assert metadata.version
        assert len(metadata.languages) > 0
        assert len(metadata.file_extensions) > 0
    
    def test_can_parse_python_file(self):
        """Test plugin recognizes Python files."""
        plugin = PythonPlugin()
        
        assert plugin.can_parse("test.py") is True
        assert plugin.can_parse("module.pyw") is True
        assert plugin.can_parse("data.json") is False
    
    def test_parse_python_code(self):
        """Test plugin can parse Python code."""
        plugin = PythonPlugin()
        
        code = "def hello():\n    return 'world'"
        node = plugin.parse(code, "test.py")
        
        assert node is not None
        assert node.type in ["Module", "module"]
    
    def test_plugin_validation(self):
        """Test plugin validates successfully."""
        plugin = PythonPlugin()
        assert plugin.validate() is True


class TestPluginLoader:
    """Test plugin loader functionality."""
    
    def test_discover_plugins(self):
        """Test plugin discovery."""
        loader = PluginLoader()
        loader.discover_plugins()
        
        plugins = loader.list_plugins()
        assert 'ast_plugins' in plugins
        assert 'analysis_plugins' in plugins
    
    def test_get_plugin_for_python_file(self):
        """Test getting plugin for Python file."""
        loader = PluginLoader()
        loader.discover_plugins()
        
        plugin = loader.get_plugin_for_file("test.py")
        assert plugin is not None
        assert plugin.language == "python"
    
    def test_get_plugin_by_language(self):
        """Test getting plugin by language name."""
        loader = PluginLoader()
        loader.discover_plugins()
        
        plugin = loader.get_plugin_by_language("python")
        assert plugin is not None
        assert isinstance(plugin, PythonPlugin)
    
    def test_no_plugin_for_unknown_file(self):
        """Test no plugin returned for unknown file type."""
        loader = PluginLoader()
        loader.discover_plugins()
        
        plugin = loader.get_plugin_for_file("unknown.xyz")
        assert plugin is None
