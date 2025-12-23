"""
Plugin discovery and loading system.
"""
import importlib
import importlib.util
from pathlib import Path
from typing import List, Dict, Type, Optional
import logging

from . import ASTPlugin, AnalysisPlugin

logger = logging.getLogger(__name__)


class PluginLoader:
    """
    Discovers and loads AST plugins.
    
    Searches for plugins in:
    1. Built-in plugins (codex.ast.plugins.*)
    2. External plugins (installed packages)
    3. Local plugin directory
    """
    
    def __init__(self):
        """Initialize plugin loader."""
        self._ast_plugins: Dict[str, ASTPlugin] = {}
        self._analysis_plugins: Dict[str, AnalysisPlugin] = {}
        self._loaded = False
    
    def discover_plugins(self):
        """Discover all available plugins."""
        if self._loaded:
            return
        
        # Load built-in plugins
        self._load_builtin_plugins()
        
        # Load external plugins
        self._load_external_plugins()
        
        self._loaded = True
        logger.info(
            f"Loaded {len(self._ast_plugins)} AST plugins, "
            f"{len(self._analysis_plugins)} analysis plugins"
        )
    
    def _load_builtin_plugins(self):
        """Load built-in plugins from codex.ast.plugins package."""
        builtin_dir = Path(__file__).parent
        
        for plugin_file in builtin_dir.glob("*_plugin.py"):
            module_name = plugin_file.stem
            try:
                module = importlib.import_module(
                    f"codex.ast.plugins.{module_name}"
                )
                self._register_from_module(module)
            except Exception as e:
                logger.warning(f"Failed to load plugin {module_name}: {e}")
    
    def _load_external_plugins(self):
        """Load plugins from installed packages."""
        # Look for packages with 'codex_ast_plugin_' prefix
        try:
            import pkgutil
            for finder, name, ispkg in pkgutil.iter_modules():
                if name.startswith('codex_ast_plugin_'):
                    try:
                        module = importlib.import_module(name)
                        self._register_from_module(module)
                    except Exception as e:
                        logger.warning(f"Failed to load external plugin {name}: {e}")
        except Exception as e:
            logger.debug(f"External plugin discovery failed: {e}")
    
    def _register_from_module(self, module):
        """Register plugins from a module."""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            
            # Check if it's a plugin class
            if isinstance(attr, type):
                if issubclass(attr, ASTPlugin) and attr is not ASTPlugin:
                    try:
                        plugin_instance = attr()
                        if plugin_instance.validate():
                            self._ast_plugins[plugin_instance.language] = plugin_instance
                            logger.info(f"Registered AST plugin: {plugin_instance.language}")
                    except Exception as e:
                        logger.warning(f"Failed to instantiate plugin {attr_name}: {e}")
                
                elif issubclass(attr, AnalysisPlugin) and attr is not AnalysisPlugin:
                    try:
                        plugin_instance = attr()
                        self._analysis_plugins[plugin_instance.name] = plugin_instance
                        logger.info(f"Registered analysis plugin: {plugin_instance.name}")
                    except Exception as e:
                        logger.warning(f"Failed to instantiate analysis plugin {attr_name}: {e}")
    
    def get_plugin_for_file(self, file_path: str) -> Optional[ASTPlugin]:
        """
        Get appropriate plugin for a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Plugin instance or None
        """
        if not self._loaded:
            self.discover_plugins()
        
        for plugin in self._ast_plugins.values():
            if plugin.can_parse(file_path):
                return plugin
        
        return None
    
    def get_plugin_by_language(self, language: str) -> Optional[ASTPlugin]:
        """Get plugin by language name."""
        if not self._loaded:
            self.discover_plugins()
        
        return self._ast_plugins.get(language)
    
    def get_analysis_plugin(self, name: str) -> Optional[AnalysisPlugin]:
        """Get analysis plugin by name."""
        if not self._loaded:
            self.discover_plugins()
        
        return self._analysis_plugins.get(name)
    
    def list_plugins(self) -> Dict[str, List[str]]:
        """List all registered plugins."""
        if not self._loaded:
            self.discover_plugins()
        
        return {
            'ast_plugins': list(self._ast_plugins.keys()),
            'analysis_plugins': list(self._analysis_plugins.keys())
        }


# Singleton instance
_loader = PluginLoader()


def get_loader() -> PluginLoader:
    """Get the global plugin loader instance."""
    return _loader
