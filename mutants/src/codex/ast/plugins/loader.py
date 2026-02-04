"""
Plugin discovery and loading system.
"""

import importlib
import importlib.util
import logging
from pathlib import Path
from typing import Optional

from . import AnalysisPlugin, ASTPlugin

logger = logging.getLogger(__name__)
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


class PluginLoader:
    """
    Discovers and loads AST plugins.

    Searches for plugins in:
    1. Built-in plugins (codex.ast.plugins.*)
    2. External plugins (installed packages)
    3. Local plugin directory
    """

    def xǁPluginLoaderǁ__init____mutmut_orig(self):
        """Initialize plugin loader."""
        self._ast_plugins: dict[str, ASTPlugin] = {}
        self._analysis_plugins: dict[str, AnalysisPlugin] = {}
        self._loaded = False

    def xǁPluginLoaderǁ__init____mutmut_1(self):
        """Initialize plugin loader."""
        self._ast_plugins: dict[str, ASTPlugin] = None
        self._analysis_plugins: dict[str, AnalysisPlugin] = {}
        self._loaded = False

    def xǁPluginLoaderǁ__init____mutmut_2(self):
        """Initialize plugin loader."""
        self._ast_plugins: dict[str, ASTPlugin] = {}
        self._analysis_plugins: dict[str, AnalysisPlugin] = None
        self._loaded = False

    def xǁPluginLoaderǁ__init____mutmut_3(self):
        """Initialize plugin loader."""
        self._ast_plugins: dict[str, ASTPlugin] = {}
        self._analysis_plugins: dict[str, AnalysisPlugin] = {}
        self._loaded = None

    def xǁPluginLoaderǁ__init____mutmut_4(self):
        """Initialize plugin loader."""
        self._ast_plugins: dict[str, ASTPlugin] = {}
        self._analysis_plugins: dict[str, AnalysisPlugin] = {}
        self._loaded = True
    
    xǁPluginLoaderǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPluginLoaderǁ__init____mutmut_1': xǁPluginLoaderǁ__init____mutmut_1, 
        'xǁPluginLoaderǁ__init____mutmut_2': xǁPluginLoaderǁ__init____mutmut_2, 
        'xǁPluginLoaderǁ__init____mutmut_3': xǁPluginLoaderǁ__init____mutmut_3, 
        'xǁPluginLoaderǁ__init____mutmut_4': xǁPluginLoaderǁ__init____mutmut_4
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPluginLoaderǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁPluginLoaderǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁPluginLoaderǁ__init____mutmut_orig)
    xǁPluginLoaderǁ__init____mutmut_orig.__name__ = 'xǁPluginLoaderǁ__init__'

    def xǁPluginLoaderǁdiscover_plugins__mutmut_orig(self):
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

    def xǁPluginLoaderǁdiscover_plugins__mutmut_1(self):
        """Discover all available plugins."""
        if self._loaded:
            return

        # Load built-in plugins
        self._load_builtin_plugins()

        # Load external plugins
        self._load_external_plugins()

        self._loaded = None
        logger.info(
            f"Loaded {len(self._ast_plugins)} AST plugins, "
            f"{len(self._analysis_plugins)} analysis plugins"
        )

    def xǁPluginLoaderǁdiscover_plugins__mutmut_2(self):
        """Discover all available plugins."""
        if self._loaded:
            return

        # Load built-in plugins
        self._load_builtin_plugins()

        # Load external plugins
        self._load_external_plugins()

        self._loaded = False
        logger.info(
            f"Loaded {len(self._ast_plugins)} AST plugins, "
            f"{len(self._analysis_plugins)} analysis plugins"
        )

    def xǁPluginLoaderǁdiscover_plugins__mutmut_3(self):
        """Discover all available plugins."""
        if self._loaded:
            return

        # Load built-in plugins
        self._load_builtin_plugins()

        # Load external plugins
        self._load_external_plugins()

        self._loaded = True
        logger.info(
            None
        )
    
    xǁPluginLoaderǁdiscover_plugins__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPluginLoaderǁdiscover_plugins__mutmut_1': xǁPluginLoaderǁdiscover_plugins__mutmut_1, 
        'xǁPluginLoaderǁdiscover_plugins__mutmut_2': xǁPluginLoaderǁdiscover_plugins__mutmut_2, 
        'xǁPluginLoaderǁdiscover_plugins__mutmut_3': xǁPluginLoaderǁdiscover_plugins__mutmut_3
    }
    
    def discover_plugins(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPluginLoaderǁdiscover_plugins__mutmut_orig"), object.__getattribute__(self, "xǁPluginLoaderǁdiscover_plugins__mutmut_mutants"), args, kwargs, self)
        return result 
    
    discover_plugins.__signature__ = _mutmut_signature(xǁPluginLoaderǁdiscover_plugins__mutmut_orig)
    xǁPluginLoaderǁdiscover_plugins__mutmut_orig.__name__ = 'xǁPluginLoaderǁdiscover_plugins'

    def xǁPluginLoaderǁ_load_builtin_plugins__mutmut_orig(self):
        """Load built-in plugins from codex.ast.plugins package."""
        builtin_dir = Path(__file__).parent

        for plugin_file in builtin_dir.glob("*_plugin.py"):
            module_name = plugin_file.stem
            try:
                module = importlib.import_module(f"codex.ast.plugins.{module_name}")
                self._register_from_module(module)
            except Exception as e:
                logger.warning(f"Failed to load plugin {module_name}: {e}")

    def xǁPluginLoaderǁ_load_builtin_plugins__mutmut_1(self):
        """Load built-in plugins from codex.ast.plugins package."""
        builtin_dir = None

        for plugin_file in builtin_dir.glob("*_plugin.py"):
            module_name = plugin_file.stem
            try:
                module = importlib.import_module(f"codex.ast.plugins.{module_name}")
                self._register_from_module(module)
            except Exception as e:
                logger.warning(f"Failed to load plugin {module_name}: {e}")

    def xǁPluginLoaderǁ_load_builtin_plugins__mutmut_2(self):
        """Load built-in plugins from codex.ast.plugins package."""
        builtin_dir = Path(None).parent

        for plugin_file in builtin_dir.glob("*_plugin.py"):
            module_name = plugin_file.stem
            try:
                module = importlib.import_module(f"codex.ast.plugins.{module_name}")
                self._register_from_module(module)
            except Exception as e:
                logger.warning(f"Failed to load plugin {module_name}: {e}")

    def xǁPluginLoaderǁ_load_builtin_plugins__mutmut_3(self):
        """Load built-in plugins from codex.ast.plugins package."""
        builtin_dir = Path(__file__).parent

        for plugin_file in builtin_dir.glob(None):
            module_name = plugin_file.stem
            try:
                module = importlib.import_module(f"codex.ast.plugins.{module_name}")
                self._register_from_module(module)
            except Exception as e:
                logger.warning(f"Failed to load plugin {module_name}: {e}")

    def xǁPluginLoaderǁ_load_builtin_plugins__mutmut_4(self):
        """Load built-in plugins from codex.ast.plugins package."""
        builtin_dir = Path(__file__).parent

        for plugin_file in builtin_dir.glob("XX*_plugin.pyXX"):
            module_name = plugin_file.stem
            try:
                module = importlib.import_module(f"codex.ast.plugins.{module_name}")
                self._register_from_module(module)
            except Exception as e:
                logger.warning(f"Failed to load plugin {module_name}: {e}")

    def xǁPluginLoaderǁ_load_builtin_plugins__mutmut_5(self):
        """Load built-in plugins from codex.ast.plugins package."""
        builtin_dir = Path(__file__).parent

        for plugin_file in builtin_dir.glob("*_PLUGIN.PY"):
            module_name = plugin_file.stem
            try:
                module = importlib.import_module(f"codex.ast.plugins.{module_name}")
                self._register_from_module(module)
            except Exception as e:
                logger.warning(f"Failed to load plugin {module_name}: {e}")

    def xǁPluginLoaderǁ_load_builtin_plugins__mutmut_6(self):
        """Load built-in plugins from codex.ast.plugins package."""
        builtin_dir = Path(__file__).parent

        for plugin_file in builtin_dir.glob("*_plugin.py"):
            module_name = None
            try:
                module = importlib.import_module(f"codex.ast.plugins.{module_name}")
                self._register_from_module(module)
            except Exception as e:
                logger.warning(f"Failed to load plugin {module_name}: {e}")

    def xǁPluginLoaderǁ_load_builtin_plugins__mutmut_7(self):
        """Load built-in plugins from codex.ast.plugins package."""
        builtin_dir = Path(__file__).parent

        for plugin_file in builtin_dir.glob("*_plugin.py"):
            module_name = plugin_file.stem
            try:
                module = None
                self._register_from_module(module)
            except Exception as e:
                logger.warning(f"Failed to load plugin {module_name}: {e}")

    def xǁPluginLoaderǁ_load_builtin_plugins__mutmut_8(self):
        """Load built-in plugins from codex.ast.plugins package."""
        builtin_dir = Path(__file__).parent

        for plugin_file in builtin_dir.glob("*_plugin.py"):
            module_name = plugin_file.stem
            try:
                module = importlib.import_module(None)
                self._register_from_module(module)
            except Exception as e:
                logger.warning(f"Failed to load plugin {module_name}: {e}")

    def xǁPluginLoaderǁ_load_builtin_plugins__mutmut_9(self):
        """Load built-in plugins from codex.ast.plugins package."""
        builtin_dir = Path(__file__).parent

        for plugin_file in builtin_dir.glob("*_plugin.py"):
            module_name = plugin_file.stem
            try:
                module = importlib.import_module(f"codex.ast.plugins.{module_name}")
                self._register_from_module(None)
            except Exception as e:
                logger.warning(f"Failed to load plugin {module_name}: {e}")

    def xǁPluginLoaderǁ_load_builtin_plugins__mutmut_10(self):
        """Load built-in plugins from codex.ast.plugins package."""
        builtin_dir = Path(__file__).parent

        for plugin_file in builtin_dir.glob("*_plugin.py"):
            module_name = plugin_file.stem
            try:
                module = importlib.import_module(f"codex.ast.plugins.{module_name}")
                self._register_from_module(module)
            except Exception as e:
                logger.warning(None)
    
    xǁPluginLoaderǁ_load_builtin_plugins__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPluginLoaderǁ_load_builtin_plugins__mutmut_1': xǁPluginLoaderǁ_load_builtin_plugins__mutmut_1, 
        'xǁPluginLoaderǁ_load_builtin_plugins__mutmut_2': xǁPluginLoaderǁ_load_builtin_plugins__mutmut_2, 
        'xǁPluginLoaderǁ_load_builtin_plugins__mutmut_3': xǁPluginLoaderǁ_load_builtin_plugins__mutmut_3, 
        'xǁPluginLoaderǁ_load_builtin_plugins__mutmut_4': xǁPluginLoaderǁ_load_builtin_plugins__mutmut_4, 
        'xǁPluginLoaderǁ_load_builtin_plugins__mutmut_5': xǁPluginLoaderǁ_load_builtin_plugins__mutmut_5, 
        'xǁPluginLoaderǁ_load_builtin_plugins__mutmut_6': xǁPluginLoaderǁ_load_builtin_plugins__mutmut_6, 
        'xǁPluginLoaderǁ_load_builtin_plugins__mutmut_7': xǁPluginLoaderǁ_load_builtin_plugins__mutmut_7, 
        'xǁPluginLoaderǁ_load_builtin_plugins__mutmut_8': xǁPluginLoaderǁ_load_builtin_plugins__mutmut_8, 
        'xǁPluginLoaderǁ_load_builtin_plugins__mutmut_9': xǁPluginLoaderǁ_load_builtin_plugins__mutmut_9, 
        'xǁPluginLoaderǁ_load_builtin_plugins__mutmut_10': xǁPluginLoaderǁ_load_builtin_plugins__mutmut_10
    }
    
    def _load_builtin_plugins(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPluginLoaderǁ_load_builtin_plugins__mutmut_orig"), object.__getattribute__(self, "xǁPluginLoaderǁ_load_builtin_plugins__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _load_builtin_plugins.__signature__ = _mutmut_signature(xǁPluginLoaderǁ_load_builtin_plugins__mutmut_orig)
    xǁPluginLoaderǁ_load_builtin_plugins__mutmut_orig.__name__ = 'xǁPluginLoaderǁ_load_builtin_plugins'

    def xǁPluginLoaderǁ_load_external_plugins__mutmut_orig(self):
        """Load plugins from installed packages."""
        # Look for packages with 'codex_ast_plugin_' prefix
        try:
            import pkgutil

            # Only search in known plugin paths, not all of sys.path
            plugin_prefix = "codex_ast_plugin_"
            for finder, name, ispkg in pkgutil.iter_modules():
                if name.startswith(plugin_prefix):
                    try:
                        module = importlib.import_module(name)
                        self._register_from_module(module)
                        logger.info(f"Loaded external plugin: {name}")
                    except ImportError as ie:
                        logger.debug(f"Failed to import external plugin {name}: {ie}")
                    except Exception as e:
                        logger.warning(f"Failed to load external plugin {name}: {e}", exc_info=True)
        except Exception as e:
            logger.debug(f"External plugin discovery failed: {e}")

    def xǁPluginLoaderǁ_load_external_plugins__mutmut_1(self):
        """Load plugins from installed packages."""
        # Look for packages with 'codex_ast_plugin_' prefix
        try:
            import pkgutil

            # Only search in known plugin paths, not all of sys.path
            plugin_prefix = None
            for finder, name, ispkg in pkgutil.iter_modules():
                if name.startswith(plugin_prefix):
                    try:
                        module = importlib.import_module(name)
                        self._register_from_module(module)
                        logger.info(f"Loaded external plugin: {name}")
                    except ImportError as ie:
                        logger.debug(f"Failed to import external plugin {name}: {ie}")
                    except Exception as e:
                        logger.warning(f"Failed to load external plugin {name}: {e}", exc_info=True)
        except Exception as e:
            logger.debug(f"External plugin discovery failed: {e}")

    def xǁPluginLoaderǁ_load_external_plugins__mutmut_2(self):
        """Load plugins from installed packages."""
        # Look for packages with 'codex_ast_plugin_' prefix
        try:
            import pkgutil

            # Only search in known plugin paths, not all of sys.path
            plugin_prefix = "XXcodex_ast_plugin_XX"
            for finder, name, ispkg in pkgutil.iter_modules():
                if name.startswith(plugin_prefix):
                    try:
                        module = importlib.import_module(name)
                        self._register_from_module(module)
                        logger.info(f"Loaded external plugin: {name}")
                    except ImportError as ie:
                        logger.debug(f"Failed to import external plugin {name}: {ie}")
                    except Exception as e:
                        logger.warning(f"Failed to load external plugin {name}: {e}", exc_info=True)
        except Exception as e:
            logger.debug(f"External plugin discovery failed: {e}")

    def xǁPluginLoaderǁ_load_external_plugins__mutmut_3(self):
        """Load plugins from installed packages."""
        # Look for packages with 'codex_ast_plugin_' prefix
        try:
            import pkgutil

            # Only search in known plugin paths, not all of sys.path
            plugin_prefix = "CODEX_AST_PLUGIN_"
            for finder, name, ispkg in pkgutil.iter_modules():
                if name.startswith(plugin_prefix):
                    try:
                        module = importlib.import_module(name)
                        self._register_from_module(module)
                        logger.info(f"Loaded external plugin: {name}")
                    except ImportError as ie:
                        logger.debug(f"Failed to import external plugin {name}: {ie}")
                    except Exception as e:
                        logger.warning(f"Failed to load external plugin {name}: {e}", exc_info=True)
        except Exception as e:
            logger.debug(f"External plugin discovery failed: {e}")

    def xǁPluginLoaderǁ_load_external_plugins__mutmut_4(self):
        """Load plugins from installed packages."""
        # Look for packages with 'codex_ast_plugin_' prefix
        try:
            import pkgutil

            # Only search in known plugin paths, not all of sys.path
            plugin_prefix = "codex_ast_plugin_"
            for finder, name, ispkg in pkgutil.iter_modules():
                if name.startswith(None):
                    try:
                        module = importlib.import_module(name)
                        self._register_from_module(module)
                        logger.info(f"Loaded external plugin: {name}")
                    except ImportError as ie:
                        logger.debug(f"Failed to import external plugin {name}: {ie}")
                    except Exception as e:
                        logger.warning(f"Failed to load external plugin {name}: {e}", exc_info=True)
        except Exception as e:
            logger.debug(f"External plugin discovery failed: {e}")

    def xǁPluginLoaderǁ_load_external_plugins__mutmut_5(self):
        """Load plugins from installed packages."""
        # Look for packages with 'codex_ast_plugin_' prefix
        try:
            import pkgutil

            # Only search in known plugin paths, not all of sys.path
            plugin_prefix = "codex_ast_plugin_"
            for finder, name, ispkg in pkgutil.iter_modules():
                if name.startswith(plugin_prefix):
                    try:
                        module = None
                        self._register_from_module(module)
                        logger.info(f"Loaded external plugin: {name}")
                    except ImportError as ie:
                        logger.debug(f"Failed to import external plugin {name}: {ie}")
                    except Exception as e:
                        logger.warning(f"Failed to load external plugin {name}: {e}", exc_info=True)
        except Exception as e:
            logger.debug(f"External plugin discovery failed: {e}")

    def xǁPluginLoaderǁ_load_external_plugins__mutmut_6(self):
        """Load plugins from installed packages."""
        # Look for packages with 'codex_ast_plugin_' prefix
        try:
            import pkgutil

            # Only search in known plugin paths, not all of sys.path
            plugin_prefix = "codex_ast_plugin_"
            for finder, name, ispkg in pkgutil.iter_modules():
                if name.startswith(plugin_prefix):
                    try:
                        module = importlib.import_module(None)
                        self._register_from_module(module)
                        logger.info(f"Loaded external plugin: {name}")
                    except ImportError as ie:
                        logger.debug(f"Failed to import external plugin {name}: {ie}")
                    except Exception as e:
                        logger.warning(f"Failed to load external plugin {name}: {e}", exc_info=True)
        except Exception as e:
            logger.debug(f"External plugin discovery failed: {e}")

    def xǁPluginLoaderǁ_load_external_plugins__mutmut_7(self):
        """Load plugins from installed packages."""
        # Look for packages with 'codex_ast_plugin_' prefix
        try:
            import pkgutil

            # Only search in known plugin paths, not all of sys.path
            plugin_prefix = "codex_ast_plugin_"
            for finder, name, ispkg in pkgutil.iter_modules():
                if name.startswith(plugin_prefix):
                    try:
                        module = importlib.import_module(name)
                        self._register_from_module(None)
                        logger.info(f"Loaded external plugin: {name}")
                    except ImportError as ie:
                        logger.debug(f"Failed to import external plugin {name}: {ie}")
                    except Exception as e:
                        logger.warning(f"Failed to load external plugin {name}: {e}", exc_info=True)
        except Exception as e:
            logger.debug(f"External plugin discovery failed: {e}")

    def xǁPluginLoaderǁ_load_external_plugins__mutmut_8(self):
        """Load plugins from installed packages."""
        # Look for packages with 'codex_ast_plugin_' prefix
        try:
            import pkgutil

            # Only search in known plugin paths, not all of sys.path
            plugin_prefix = "codex_ast_plugin_"
            for finder, name, ispkg in pkgutil.iter_modules():
                if name.startswith(plugin_prefix):
                    try:
                        module = importlib.import_module(name)
                        self._register_from_module(module)
                        logger.info(None)
                    except ImportError as ie:
                        logger.debug(f"Failed to import external plugin {name}: {ie}")
                    except Exception as e:
                        logger.warning(f"Failed to load external plugin {name}: {e}", exc_info=True)
        except Exception as e:
            logger.debug(f"External plugin discovery failed: {e}")

    def xǁPluginLoaderǁ_load_external_plugins__mutmut_9(self):
        """Load plugins from installed packages."""
        # Look for packages with 'codex_ast_plugin_' prefix
        try:
            import pkgutil

            # Only search in known plugin paths, not all of sys.path
            plugin_prefix = "codex_ast_plugin_"
            for finder, name, ispkg in pkgutil.iter_modules():
                if name.startswith(plugin_prefix):
                    try:
                        module = importlib.import_module(name)
                        self._register_from_module(module)
                        logger.info(f"Loaded external plugin: {name}")
                    except ImportError as ie:
                        logger.debug(None)
                    except Exception as e:
                        logger.warning(f"Failed to load external plugin {name}: {e}", exc_info=True)
        except Exception as e:
            logger.debug(f"External plugin discovery failed: {e}")

    def xǁPluginLoaderǁ_load_external_plugins__mutmut_10(self):
        """Load plugins from installed packages."""
        # Look for packages with 'codex_ast_plugin_' prefix
        try:
            import pkgutil

            # Only search in known plugin paths, not all of sys.path
            plugin_prefix = "codex_ast_plugin_"
            for finder, name, ispkg in pkgutil.iter_modules():
                if name.startswith(plugin_prefix):
                    try:
                        module = importlib.import_module(name)
                        self._register_from_module(module)
                        logger.info(f"Loaded external plugin: {name}")
                    except ImportError as ie:
                        logger.debug(f"Failed to import external plugin {name}: {ie}")
                    except Exception as e:
                        logger.warning(None, exc_info=True)
        except Exception as e:
            logger.debug(f"External plugin discovery failed: {e}")

    def xǁPluginLoaderǁ_load_external_plugins__mutmut_11(self):
        """Load plugins from installed packages."""
        # Look for packages with 'codex_ast_plugin_' prefix
        try:
            import pkgutil

            # Only search in known plugin paths, not all of sys.path
            plugin_prefix = "codex_ast_plugin_"
            for finder, name, ispkg in pkgutil.iter_modules():
                if name.startswith(plugin_prefix):
                    try:
                        module = importlib.import_module(name)
                        self._register_from_module(module)
                        logger.info(f"Loaded external plugin: {name}")
                    except ImportError as ie:
                        logger.debug(f"Failed to import external plugin {name}: {ie}")
                    except Exception as e:
                        logger.warning(f"Failed to load external plugin {name}: {e}", exc_info=None)
        except Exception as e:
            logger.debug(f"External plugin discovery failed: {e}")

    def xǁPluginLoaderǁ_load_external_plugins__mutmut_12(self):
        """Load plugins from installed packages."""
        # Look for packages with 'codex_ast_plugin_' prefix
        try:
            import pkgutil

            # Only search in known plugin paths, not all of sys.path
            plugin_prefix = "codex_ast_plugin_"
            for finder, name, ispkg in pkgutil.iter_modules():
                if name.startswith(plugin_prefix):
                    try:
                        module = importlib.import_module(name)
                        self._register_from_module(module)
                        logger.info(f"Loaded external plugin: {name}")
                    except ImportError as ie:
                        logger.debug(f"Failed to import external plugin {name}: {ie}")
                    except Exception as e:
                        logger.warning(exc_info=True)
        except Exception as e:
            logger.debug(f"External plugin discovery failed: {e}")

    def xǁPluginLoaderǁ_load_external_plugins__mutmut_13(self):
        """Load plugins from installed packages."""
        # Look for packages with 'codex_ast_plugin_' prefix
        try:
            import pkgutil

            # Only search in known plugin paths, not all of sys.path
            plugin_prefix = "codex_ast_plugin_"
            for finder, name, ispkg in pkgutil.iter_modules():
                if name.startswith(plugin_prefix):
                    try:
                        module = importlib.import_module(name)
                        self._register_from_module(module)
                        logger.info(f"Loaded external plugin: {name}")
                    except ImportError as ie:
                        logger.debug(f"Failed to import external plugin {name}: {ie}")
                    except Exception as e:
                        logger.warning(f"Failed to load external plugin {name}: {e}", )
        except Exception as e:
            logger.debug(f"External plugin discovery failed: {e}")

    def xǁPluginLoaderǁ_load_external_plugins__mutmut_14(self):
        """Load plugins from installed packages."""
        # Look for packages with 'codex_ast_plugin_' prefix
        try:
            import pkgutil

            # Only search in known plugin paths, not all of sys.path
            plugin_prefix = "codex_ast_plugin_"
            for finder, name, ispkg in pkgutil.iter_modules():
                if name.startswith(plugin_prefix):
                    try:
                        module = importlib.import_module(name)
                        self._register_from_module(module)
                        logger.info(f"Loaded external plugin: {name}")
                    except ImportError as ie:
                        logger.debug(f"Failed to import external plugin {name}: {ie}")
                    except Exception as e:
                        logger.warning(f"Failed to load external plugin {name}: {e}", exc_info=False)
        except Exception as e:
            logger.debug(f"External plugin discovery failed: {e}")

    def xǁPluginLoaderǁ_load_external_plugins__mutmut_15(self):
        """Load plugins from installed packages."""
        # Look for packages with 'codex_ast_plugin_' prefix
        try:
            import pkgutil

            # Only search in known plugin paths, not all of sys.path
            plugin_prefix = "codex_ast_plugin_"
            for finder, name, ispkg in pkgutil.iter_modules():
                if name.startswith(plugin_prefix):
                    try:
                        module = importlib.import_module(name)
                        self._register_from_module(module)
                        logger.info(f"Loaded external plugin: {name}")
                    except ImportError as ie:
                        logger.debug(f"Failed to import external plugin {name}: {ie}")
                    except Exception as e:
                        logger.warning(f"Failed to load external plugin {name}: {e}", exc_info=True)
        except Exception as e:
            logger.debug(None)
    
    xǁPluginLoaderǁ_load_external_plugins__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPluginLoaderǁ_load_external_plugins__mutmut_1': xǁPluginLoaderǁ_load_external_plugins__mutmut_1, 
        'xǁPluginLoaderǁ_load_external_plugins__mutmut_2': xǁPluginLoaderǁ_load_external_plugins__mutmut_2, 
        'xǁPluginLoaderǁ_load_external_plugins__mutmut_3': xǁPluginLoaderǁ_load_external_plugins__mutmut_3, 
        'xǁPluginLoaderǁ_load_external_plugins__mutmut_4': xǁPluginLoaderǁ_load_external_plugins__mutmut_4, 
        'xǁPluginLoaderǁ_load_external_plugins__mutmut_5': xǁPluginLoaderǁ_load_external_plugins__mutmut_5, 
        'xǁPluginLoaderǁ_load_external_plugins__mutmut_6': xǁPluginLoaderǁ_load_external_plugins__mutmut_6, 
        'xǁPluginLoaderǁ_load_external_plugins__mutmut_7': xǁPluginLoaderǁ_load_external_plugins__mutmut_7, 
        'xǁPluginLoaderǁ_load_external_plugins__mutmut_8': xǁPluginLoaderǁ_load_external_plugins__mutmut_8, 
        'xǁPluginLoaderǁ_load_external_plugins__mutmut_9': xǁPluginLoaderǁ_load_external_plugins__mutmut_9, 
        'xǁPluginLoaderǁ_load_external_plugins__mutmut_10': xǁPluginLoaderǁ_load_external_plugins__mutmut_10, 
        'xǁPluginLoaderǁ_load_external_plugins__mutmut_11': xǁPluginLoaderǁ_load_external_plugins__mutmut_11, 
        'xǁPluginLoaderǁ_load_external_plugins__mutmut_12': xǁPluginLoaderǁ_load_external_plugins__mutmut_12, 
        'xǁPluginLoaderǁ_load_external_plugins__mutmut_13': xǁPluginLoaderǁ_load_external_plugins__mutmut_13, 
        'xǁPluginLoaderǁ_load_external_plugins__mutmut_14': xǁPluginLoaderǁ_load_external_plugins__mutmut_14, 
        'xǁPluginLoaderǁ_load_external_plugins__mutmut_15': xǁPluginLoaderǁ_load_external_plugins__mutmut_15
    }
    
    def _load_external_plugins(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPluginLoaderǁ_load_external_plugins__mutmut_orig"), object.__getattribute__(self, "xǁPluginLoaderǁ_load_external_plugins__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _load_external_plugins.__signature__ = _mutmut_signature(xǁPluginLoaderǁ_load_external_plugins__mutmut_orig)
    xǁPluginLoaderǁ_load_external_plugins__mutmut_orig.__name__ = 'xǁPluginLoaderǁ_load_external_plugins'

    def xǁPluginLoaderǁ_register_from_module__mutmut_orig(self, module):
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

    def xǁPluginLoaderǁ_register_from_module__mutmut_1(self, module):
        """Register plugins from a module."""
        for attr_name in dir(None):
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

    def xǁPluginLoaderǁ_register_from_module__mutmut_2(self, module):
        """Register plugins from a module."""
        for attr_name in dir(module):
            attr = None

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

    def xǁPluginLoaderǁ_register_from_module__mutmut_3(self, module):
        """Register plugins from a module."""
        for attr_name in dir(module):
            attr = getattr(None, attr_name)

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

    def xǁPluginLoaderǁ_register_from_module__mutmut_4(self, module):
        """Register plugins from a module."""
        for attr_name in dir(module):
            attr = getattr(module, None)

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

    def xǁPluginLoaderǁ_register_from_module__mutmut_5(self, module):
        """Register plugins from a module."""
        for attr_name in dir(module):
            attr = getattr(attr_name)

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

    def xǁPluginLoaderǁ_register_from_module__mutmut_6(self, module):
        """Register plugins from a module."""
        for attr_name in dir(module):
            attr = getattr(module, )

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

    def xǁPluginLoaderǁ_register_from_module__mutmut_7(self, module):
        """Register plugins from a module."""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            # Check if it's a plugin class
            if isinstance(attr, type):
                if issubclass(attr, ASTPlugin) or attr is not ASTPlugin:
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

    def xǁPluginLoaderǁ_register_from_module__mutmut_8(self, module):
        """Register plugins from a module."""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            # Check if it's a plugin class
            if isinstance(attr, type):
                if issubclass(None, ASTPlugin) and attr is not ASTPlugin:
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

    def xǁPluginLoaderǁ_register_from_module__mutmut_9(self, module):
        """Register plugins from a module."""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            # Check if it's a plugin class
            if isinstance(attr, type):
                if issubclass(attr, None) and attr is not ASTPlugin:
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

    def xǁPluginLoaderǁ_register_from_module__mutmut_10(self, module):
        """Register plugins from a module."""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            # Check if it's a plugin class
            if isinstance(attr, type):
                if issubclass(ASTPlugin) and attr is not ASTPlugin:
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

    def xǁPluginLoaderǁ_register_from_module__mutmut_11(self, module):
        """Register plugins from a module."""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            # Check if it's a plugin class
            if isinstance(attr, type):
                if issubclass(attr, ) and attr is not ASTPlugin:
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

    def xǁPluginLoaderǁ_register_from_module__mutmut_12(self, module):
        """Register plugins from a module."""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            # Check if it's a plugin class
            if isinstance(attr, type):
                if issubclass(attr, ASTPlugin) and attr is ASTPlugin:
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

    def xǁPluginLoaderǁ_register_from_module__mutmut_13(self, module):
        """Register plugins from a module."""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            # Check if it's a plugin class
            if isinstance(attr, type):
                if issubclass(attr, ASTPlugin) and attr is not ASTPlugin:
                    try:
                        plugin_instance = None
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

    def xǁPluginLoaderǁ_register_from_module__mutmut_14(self, module):
        """Register plugins from a module."""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            # Check if it's a plugin class
            if isinstance(attr, type):
                if issubclass(attr, ASTPlugin) and attr is not ASTPlugin:
                    try:
                        plugin_instance = attr()
                        if plugin_instance.validate():
                            self._ast_plugins[plugin_instance.language] = None
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

    def xǁPluginLoaderǁ_register_from_module__mutmut_15(self, module):
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
                            logger.info(None)
                    except Exception as e:
                        logger.warning(f"Failed to instantiate plugin {attr_name}: {e}")

                elif issubclass(attr, AnalysisPlugin) and attr is not AnalysisPlugin:
                    try:
                        plugin_instance = attr()
                        self._analysis_plugins[plugin_instance.name] = plugin_instance
                        logger.info(f"Registered analysis plugin: {plugin_instance.name}")
                    except Exception as e:
                        logger.warning(f"Failed to instantiate analysis plugin {attr_name}: {e}")

    def xǁPluginLoaderǁ_register_from_module__mutmut_16(self, module):
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
                        logger.warning(None)

                elif issubclass(attr, AnalysisPlugin) and attr is not AnalysisPlugin:
                    try:
                        plugin_instance = attr()
                        self._analysis_plugins[plugin_instance.name] = plugin_instance
                        logger.info(f"Registered analysis plugin: {plugin_instance.name}")
                    except Exception as e:
                        logger.warning(f"Failed to instantiate analysis plugin {attr_name}: {e}")

    def xǁPluginLoaderǁ_register_from_module__mutmut_17(self, module):
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

                elif issubclass(attr, AnalysisPlugin) or attr is not AnalysisPlugin:
                    try:
                        plugin_instance = attr()
                        self._analysis_plugins[plugin_instance.name] = plugin_instance
                        logger.info(f"Registered analysis plugin: {plugin_instance.name}")
                    except Exception as e:
                        logger.warning(f"Failed to instantiate analysis plugin {attr_name}: {e}")

    def xǁPluginLoaderǁ_register_from_module__mutmut_18(self, module):
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

                elif issubclass(None, AnalysisPlugin) and attr is not AnalysisPlugin:
                    try:
                        plugin_instance = attr()
                        self._analysis_plugins[plugin_instance.name] = plugin_instance
                        logger.info(f"Registered analysis plugin: {plugin_instance.name}")
                    except Exception as e:
                        logger.warning(f"Failed to instantiate analysis plugin {attr_name}: {e}")

    def xǁPluginLoaderǁ_register_from_module__mutmut_19(self, module):
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

                elif issubclass(attr, None) and attr is not AnalysisPlugin:
                    try:
                        plugin_instance = attr()
                        self._analysis_plugins[plugin_instance.name] = plugin_instance
                        logger.info(f"Registered analysis plugin: {plugin_instance.name}")
                    except Exception as e:
                        logger.warning(f"Failed to instantiate analysis plugin {attr_name}: {e}")

    def xǁPluginLoaderǁ_register_from_module__mutmut_20(self, module):
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

                elif issubclass(AnalysisPlugin) and attr is not AnalysisPlugin:
                    try:
                        plugin_instance = attr()
                        self._analysis_plugins[plugin_instance.name] = plugin_instance
                        logger.info(f"Registered analysis plugin: {plugin_instance.name}")
                    except Exception as e:
                        logger.warning(f"Failed to instantiate analysis plugin {attr_name}: {e}")

    def xǁPluginLoaderǁ_register_from_module__mutmut_21(self, module):
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

                elif issubclass(attr, ) and attr is not AnalysisPlugin:
                    try:
                        plugin_instance = attr()
                        self._analysis_plugins[plugin_instance.name] = plugin_instance
                        logger.info(f"Registered analysis plugin: {plugin_instance.name}")
                    except Exception as e:
                        logger.warning(f"Failed to instantiate analysis plugin {attr_name}: {e}")

    def xǁPluginLoaderǁ_register_from_module__mutmut_22(self, module):
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

                elif issubclass(attr, AnalysisPlugin) and attr is AnalysisPlugin:
                    try:
                        plugin_instance = attr()
                        self._analysis_plugins[plugin_instance.name] = plugin_instance
                        logger.info(f"Registered analysis plugin: {plugin_instance.name}")
                    except Exception as e:
                        logger.warning(f"Failed to instantiate analysis plugin {attr_name}: {e}")

    def xǁPluginLoaderǁ_register_from_module__mutmut_23(self, module):
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
                        plugin_instance = None
                        self._analysis_plugins[plugin_instance.name] = plugin_instance
                        logger.info(f"Registered analysis plugin: {plugin_instance.name}")
                    except Exception as e:
                        logger.warning(f"Failed to instantiate analysis plugin {attr_name}: {e}")

    def xǁPluginLoaderǁ_register_from_module__mutmut_24(self, module):
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
                        self._analysis_plugins[plugin_instance.name] = None
                        logger.info(f"Registered analysis plugin: {plugin_instance.name}")
                    except Exception as e:
                        logger.warning(f"Failed to instantiate analysis plugin {attr_name}: {e}")

    def xǁPluginLoaderǁ_register_from_module__mutmut_25(self, module):
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
                        logger.info(None)
                    except Exception as e:
                        logger.warning(f"Failed to instantiate analysis plugin {attr_name}: {e}")

    def xǁPluginLoaderǁ_register_from_module__mutmut_26(self, module):
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
                        logger.warning(None)
    
    xǁPluginLoaderǁ_register_from_module__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPluginLoaderǁ_register_from_module__mutmut_1': xǁPluginLoaderǁ_register_from_module__mutmut_1, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_2': xǁPluginLoaderǁ_register_from_module__mutmut_2, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_3': xǁPluginLoaderǁ_register_from_module__mutmut_3, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_4': xǁPluginLoaderǁ_register_from_module__mutmut_4, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_5': xǁPluginLoaderǁ_register_from_module__mutmut_5, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_6': xǁPluginLoaderǁ_register_from_module__mutmut_6, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_7': xǁPluginLoaderǁ_register_from_module__mutmut_7, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_8': xǁPluginLoaderǁ_register_from_module__mutmut_8, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_9': xǁPluginLoaderǁ_register_from_module__mutmut_9, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_10': xǁPluginLoaderǁ_register_from_module__mutmut_10, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_11': xǁPluginLoaderǁ_register_from_module__mutmut_11, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_12': xǁPluginLoaderǁ_register_from_module__mutmut_12, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_13': xǁPluginLoaderǁ_register_from_module__mutmut_13, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_14': xǁPluginLoaderǁ_register_from_module__mutmut_14, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_15': xǁPluginLoaderǁ_register_from_module__mutmut_15, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_16': xǁPluginLoaderǁ_register_from_module__mutmut_16, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_17': xǁPluginLoaderǁ_register_from_module__mutmut_17, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_18': xǁPluginLoaderǁ_register_from_module__mutmut_18, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_19': xǁPluginLoaderǁ_register_from_module__mutmut_19, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_20': xǁPluginLoaderǁ_register_from_module__mutmut_20, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_21': xǁPluginLoaderǁ_register_from_module__mutmut_21, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_22': xǁPluginLoaderǁ_register_from_module__mutmut_22, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_23': xǁPluginLoaderǁ_register_from_module__mutmut_23, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_24': xǁPluginLoaderǁ_register_from_module__mutmut_24, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_25': xǁPluginLoaderǁ_register_from_module__mutmut_25, 
        'xǁPluginLoaderǁ_register_from_module__mutmut_26': xǁPluginLoaderǁ_register_from_module__mutmut_26
    }
    
    def _register_from_module(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPluginLoaderǁ_register_from_module__mutmut_orig"), object.__getattribute__(self, "xǁPluginLoaderǁ_register_from_module__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _register_from_module.__signature__ = _mutmut_signature(xǁPluginLoaderǁ_register_from_module__mutmut_orig)
    xǁPluginLoaderǁ_register_from_module__mutmut_orig.__name__ = 'xǁPluginLoaderǁ_register_from_module'

    def xǁPluginLoaderǁget_plugin_for_file__mutmut_orig(self, file_path: str) -> Optional[ASTPlugin]:
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

    def xǁPluginLoaderǁget_plugin_for_file__mutmut_1(self, file_path: str) -> Optional[ASTPlugin]:
        """
        Get appropriate plugin for a file.

        Args:
            file_path: Path to file

        Returns:
            Plugin instance or None
        """
        if self._loaded:
            self.discover_plugins()

        for plugin in self._ast_plugins.values():
            if plugin.can_parse(file_path):
                return plugin

        return None

    def xǁPluginLoaderǁget_plugin_for_file__mutmut_2(self, file_path: str) -> Optional[ASTPlugin]:
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
            if plugin.can_parse(None):
                return plugin

        return None
    
    xǁPluginLoaderǁget_plugin_for_file__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPluginLoaderǁget_plugin_for_file__mutmut_1': xǁPluginLoaderǁget_plugin_for_file__mutmut_1, 
        'xǁPluginLoaderǁget_plugin_for_file__mutmut_2': xǁPluginLoaderǁget_plugin_for_file__mutmut_2
    }
    
    def get_plugin_for_file(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPluginLoaderǁget_plugin_for_file__mutmut_orig"), object.__getattribute__(self, "xǁPluginLoaderǁget_plugin_for_file__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_plugin_for_file.__signature__ = _mutmut_signature(xǁPluginLoaderǁget_plugin_for_file__mutmut_orig)
    xǁPluginLoaderǁget_plugin_for_file__mutmut_orig.__name__ = 'xǁPluginLoaderǁget_plugin_for_file'

    def xǁPluginLoaderǁget_plugin_by_language__mutmut_orig(self, language: str) -> Optional[ASTPlugin]:
        """Get plugin by language name."""
        if not self._loaded:
            self.discover_plugins()

        return self._ast_plugins.get(language)

    def xǁPluginLoaderǁget_plugin_by_language__mutmut_1(self, language: str) -> Optional[ASTPlugin]:
        """Get plugin by language name."""
        if self._loaded:
            self.discover_plugins()

        return self._ast_plugins.get(language)

    def xǁPluginLoaderǁget_plugin_by_language__mutmut_2(self, language: str) -> Optional[ASTPlugin]:
        """Get plugin by language name."""
        if not self._loaded:
            self.discover_plugins()

        return self._ast_plugins.get(None)
    
    xǁPluginLoaderǁget_plugin_by_language__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPluginLoaderǁget_plugin_by_language__mutmut_1': xǁPluginLoaderǁget_plugin_by_language__mutmut_1, 
        'xǁPluginLoaderǁget_plugin_by_language__mutmut_2': xǁPluginLoaderǁget_plugin_by_language__mutmut_2
    }
    
    def get_plugin_by_language(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPluginLoaderǁget_plugin_by_language__mutmut_orig"), object.__getattribute__(self, "xǁPluginLoaderǁget_plugin_by_language__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_plugin_by_language.__signature__ = _mutmut_signature(xǁPluginLoaderǁget_plugin_by_language__mutmut_orig)
    xǁPluginLoaderǁget_plugin_by_language__mutmut_orig.__name__ = 'xǁPluginLoaderǁget_plugin_by_language'

    def xǁPluginLoaderǁget_analysis_plugin__mutmut_orig(self, name: str) -> Optional[AnalysisPlugin]:
        """Get analysis plugin by name."""
        if not self._loaded:
            self.discover_plugins()

        return self._analysis_plugins.get(name)

    def xǁPluginLoaderǁget_analysis_plugin__mutmut_1(self, name: str) -> Optional[AnalysisPlugin]:
        """Get analysis plugin by name."""
        if self._loaded:
            self.discover_plugins()

        return self._analysis_plugins.get(name)

    def xǁPluginLoaderǁget_analysis_plugin__mutmut_2(self, name: str) -> Optional[AnalysisPlugin]:
        """Get analysis plugin by name."""
        if not self._loaded:
            self.discover_plugins()

        return self._analysis_plugins.get(None)
    
    xǁPluginLoaderǁget_analysis_plugin__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPluginLoaderǁget_analysis_plugin__mutmut_1': xǁPluginLoaderǁget_analysis_plugin__mutmut_1, 
        'xǁPluginLoaderǁget_analysis_plugin__mutmut_2': xǁPluginLoaderǁget_analysis_plugin__mutmut_2
    }
    
    def get_analysis_plugin(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPluginLoaderǁget_analysis_plugin__mutmut_orig"), object.__getattribute__(self, "xǁPluginLoaderǁget_analysis_plugin__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_analysis_plugin.__signature__ = _mutmut_signature(xǁPluginLoaderǁget_analysis_plugin__mutmut_orig)
    xǁPluginLoaderǁget_analysis_plugin__mutmut_orig.__name__ = 'xǁPluginLoaderǁget_analysis_plugin'

    def xǁPluginLoaderǁlist_plugins__mutmut_orig(self) -> dict[str, list[str]]:
        """list all registered plugins."""
        if not self._loaded:
            self.discover_plugins()

        return {
            "ast_plugins": list(self._ast_plugins.keys()),
            "analysis_plugins": list(self._analysis_plugins.keys()),
        }

    def xǁPluginLoaderǁlist_plugins__mutmut_1(self) -> dict[str, list[str]]:
        """list all registered plugins."""
        if self._loaded:
            self.discover_plugins()

        return {
            "ast_plugins": list(self._ast_plugins.keys()),
            "analysis_plugins": list(self._analysis_plugins.keys()),
        }

    def xǁPluginLoaderǁlist_plugins__mutmut_2(self) -> dict[str, list[str]]:
        """list all registered plugins."""
        if not self._loaded:
            self.discover_plugins()

        return {
            "XXast_pluginsXX": list(self._ast_plugins.keys()),
            "analysis_plugins": list(self._analysis_plugins.keys()),
        }

    def xǁPluginLoaderǁlist_plugins__mutmut_3(self) -> dict[str, list[str]]:
        """list all registered plugins."""
        if not self._loaded:
            self.discover_plugins()

        return {
            "AST_PLUGINS": list(self._ast_plugins.keys()),
            "analysis_plugins": list(self._analysis_plugins.keys()),
        }

    def xǁPluginLoaderǁlist_plugins__mutmut_4(self) -> dict[str, list[str]]:
        """list all registered plugins."""
        if not self._loaded:
            self.discover_plugins()

        return {
            "ast_plugins": list(None),
            "analysis_plugins": list(self._analysis_plugins.keys()),
        }

    def xǁPluginLoaderǁlist_plugins__mutmut_5(self) -> dict[str, list[str]]:
        """list all registered plugins."""
        if not self._loaded:
            self.discover_plugins()

        return {
            "ast_plugins": list(self._ast_plugins.keys()),
            "XXanalysis_pluginsXX": list(self._analysis_plugins.keys()),
        }

    def xǁPluginLoaderǁlist_plugins__mutmut_6(self) -> dict[str, list[str]]:
        """list all registered plugins."""
        if not self._loaded:
            self.discover_plugins()

        return {
            "ast_plugins": list(self._ast_plugins.keys()),
            "ANALYSIS_PLUGINS": list(self._analysis_plugins.keys()),
        }

    def xǁPluginLoaderǁlist_plugins__mutmut_7(self) -> dict[str, list[str]]:
        """list all registered plugins."""
        if not self._loaded:
            self.discover_plugins()

        return {
            "ast_plugins": list(self._ast_plugins.keys()),
            "analysis_plugins": list(None),
        }
    
    xǁPluginLoaderǁlist_plugins__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁPluginLoaderǁlist_plugins__mutmut_1': xǁPluginLoaderǁlist_plugins__mutmut_1, 
        'xǁPluginLoaderǁlist_plugins__mutmut_2': xǁPluginLoaderǁlist_plugins__mutmut_2, 
        'xǁPluginLoaderǁlist_plugins__mutmut_3': xǁPluginLoaderǁlist_plugins__mutmut_3, 
        'xǁPluginLoaderǁlist_plugins__mutmut_4': xǁPluginLoaderǁlist_plugins__mutmut_4, 
        'xǁPluginLoaderǁlist_plugins__mutmut_5': xǁPluginLoaderǁlist_plugins__mutmut_5, 
        'xǁPluginLoaderǁlist_plugins__mutmut_6': xǁPluginLoaderǁlist_plugins__mutmut_6, 
        'xǁPluginLoaderǁlist_plugins__mutmut_7': xǁPluginLoaderǁlist_plugins__mutmut_7
    }
    
    def list_plugins(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁPluginLoaderǁlist_plugins__mutmut_orig"), object.__getattribute__(self, "xǁPluginLoaderǁlist_plugins__mutmut_mutants"), args, kwargs, self)
        return result 
    
    list_plugins.__signature__ = _mutmut_signature(xǁPluginLoaderǁlist_plugins__mutmut_orig)
    xǁPluginLoaderǁlist_plugins__mutmut_orig.__name__ = 'xǁPluginLoaderǁlist_plugins'


# Singleton instance
_loader = PluginLoader()


def get_loader() -> PluginLoader:
    """Get the global plugin loader instance."""
    return _loader
