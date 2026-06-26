"""Tests for AST plugin system."""

from codex.ast.plugins.loader import PluginLoader
from codex.ast.plugins.python_plugin import PythonPlugin


class TestPythonPlugin:
    """Test Python plugin implementation."""

    def test_plugin_metadata(self):
        """Test plugin provides valid metadata."""
        plugin = PythonPlugin()
        metadata = plugin.metadata

        assert metadata.name == "python", "Data must not be empty"
        assert metadata.version, "Data must not be empty"
        assert len(metadata.languages) > 0, "Collection must not be empty"
        assert len(metadata.file_extensions) > 0, "Collection must not be empty"

    def test_can_parse_python_file(self):
        """Test plugin recognizes Python files."""
        plugin = PythonPlugin()

        assert plugin.can_parse("test.py") is True, "Condition must be true"
        assert plugin.can_parse("module.pyw") is True, "Condition must be true"
        assert plugin.can_parse("data.json") is False, "Data must not be empty"

    def test_parse_python_code(self):
        """Test plugin can parse Python code."""
        plugin = PythonPlugin()

        code = "def hello():\n    return 'world'"
        node = plugin.parse(code, "test.py")

        assert node is not None, "node must be initialized"
        # Fix: NodeType enum needs .value to get string representation
        assert node.type.value in ["Module", "module"]

    def test_plugin_validation(self):
        """Test plugin validates successfully."""
        plugin = PythonPlugin()
        assert plugin.validate() is True, "Condition must be true"


class TestPluginLoader:
    """Test plugin loader functionality."""

    def test_discover_plugins(self):
        """Test plugin discovery."""
        loader = PluginLoader()
        loader.discover_plugins()

        plugins = loader.list_plugins()
        assert "ast_plugins" in plugins, "Condition must be true"
        assert "analysis_plugins" in plugins, "Condition must be true"

    def test_get_plugin_for_python_file(self):
        """Test getting plugin for Python file."""
        loader = PluginLoader()
        loader.discover_plugins()

        plugin = loader.get_plugin_for_file("test.py")
        assert plugin is not None, "plugin must be initialized"
        assert plugin.language == "python", "language is not valid"

    def test_get_plugin_by_language(self):
        """Test getting plugin by language name."""
        loader = PluginLoader()
        loader.discover_plugins()

        plugin = loader.get_plugin_by_language("python")
        assert plugin is not None, "plugin must be initialized"
        assert isinstance(plugin, PythonPlugin)

    def test_no_plugin_for_unknown_file(self):
        """Test no plugin returned for unknown file type."""
        loader = PluginLoader()
        loader.discover_plugins()

        plugin = loader.get_plugin_for_file("unknown.xyz")
        assert plugin is None, "plugin is not valid"
