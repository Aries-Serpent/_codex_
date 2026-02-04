"""
Centralized Configuration Loader

Single source of truth for all configuration loading across the codebase.
Consolidates conf/, config/, configs/, omegaconf/, and config_legacy/ into
a unified loading system with Hydra/OmegaConf support.

Part of Phase 3: Configuration Sprawl Resolution
"""
from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional
import warnings

logger = logging.getLogger(__name__)

# Determine repository root
REPO_ROOT = Path(__file__).resolve().parents[1]

# Configuration directory hierarchy (in priority order)
CONFIG_DIRS = {
    "primary": REPO_ROOT / "conf",  # Primary Hydra-based configs
    "configs": REPO_ROOT / "configs",  # Secondary application configs
    "deprecated_config": REPO_ROOT / "config",  # Deprecated
    "deprecated_legacy": REPO_ROOT / "config_legacy",  # Deprecated
    "deprecated_omegaconf": REPO_ROOT / "omegaconf",  # Deprecated
}

# Environment variable keys
ENV_VARS = {
    "CONFIG_DIR": "CODEX_CONFIG_DIR",
    "ENV": "CODEX_ENV",
    "DEBUG": "CODEX_DEBUG",
}
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


class ConfigLoader:
    """
    Centralized configuration loader.
    
    Loads configuration from conf/ directory (Hydra-based) as the single
    source of truth, with fallback support for configs/ directory.
    
    Deprecated directories (config/, config_legacy/, omegaconf/) are
    excluded by default and will log warnings if accessed.
    """
    
    def xǁConfigLoaderǁ__init____mutmut_orig(
        self,
        config_dir: Optional[Path] = None,
        allow_deprecated: bool = False,
        strict_mode: bool = False
    ):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Override default config directory
            allow_deprecated: Allow loading from deprecated directories
            strict_mode: Raise errors instead of warnings for deprecated access
        """
        self.config_dir = config_dir or CONFIG_DIRS["primary"]
        self.allow_deprecated = allow_deprecated
        self.strict_mode = strict_mode
        self._cache: Dict[str, Any] = {}
        
        # Ensure primary config directory exists
        if not self.config_dir.exists():
            logger.warning(f"Primary config directory not found: {self.config_dir}")
            # Fall back to configs/ if conf/ doesn't exist
            if CONFIG_DIRS["configs"].exists():
                self.config_dir = CONFIG_DIRS["configs"]
                logger.info(f"Using fallback config directory: {self.config_dir}")
        
        logger.info(f"ConfigLoader initialized: {self.config_dir}")
    
    def xǁConfigLoaderǁ__init____mutmut_1(
        self,
        config_dir: Optional[Path] = None,
        allow_deprecated: bool = True,
        strict_mode: bool = False
    ):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Override default config directory
            allow_deprecated: Allow loading from deprecated directories
            strict_mode: Raise errors instead of warnings for deprecated access
        """
        self.config_dir = config_dir or CONFIG_DIRS["primary"]
        self.allow_deprecated = allow_deprecated
        self.strict_mode = strict_mode
        self._cache: Dict[str, Any] = {}
        
        # Ensure primary config directory exists
        if not self.config_dir.exists():
            logger.warning(f"Primary config directory not found: {self.config_dir}")
            # Fall back to configs/ if conf/ doesn't exist
            if CONFIG_DIRS["configs"].exists():
                self.config_dir = CONFIG_DIRS["configs"]
                logger.info(f"Using fallback config directory: {self.config_dir}")
        
        logger.info(f"ConfigLoader initialized: {self.config_dir}")
    
    def xǁConfigLoaderǁ__init____mutmut_2(
        self,
        config_dir: Optional[Path] = None,
        allow_deprecated: bool = False,
        strict_mode: bool = True
    ):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Override default config directory
            allow_deprecated: Allow loading from deprecated directories
            strict_mode: Raise errors instead of warnings for deprecated access
        """
        self.config_dir = config_dir or CONFIG_DIRS["primary"]
        self.allow_deprecated = allow_deprecated
        self.strict_mode = strict_mode
        self._cache: Dict[str, Any] = {}
        
        # Ensure primary config directory exists
        if not self.config_dir.exists():
            logger.warning(f"Primary config directory not found: {self.config_dir}")
            # Fall back to configs/ if conf/ doesn't exist
            if CONFIG_DIRS["configs"].exists():
                self.config_dir = CONFIG_DIRS["configs"]
                logger.info(f"Using fallback config directory: {self.config_dir}")
        
        logger.info(f"ConfigLoader initialized: {self.config_dir}")
    
    def xǁConfigLoaderǁ__init____mutmut_3(
        self,
        config_dir: Optional[Path] = None,
        allow_deprecated: bool = False,
        strict_mode: bool = False
    ):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Override default config directory
            allow_deprecated: Allow loading from deprecated directories
            strict_mode: Raise errors instead of warnings for deprecated access
        """
        self.config_dir = None
        self.allow_deprecated = allow_deprecated
        self.strict_mode = strict_mode
        self._cache: Dict[str, Any] = {}
        
        # Ensure primary config directory exists
        if not self.config_dir.exists():
            logger.warning(f"Primary config directory not found: {self.config_dir}")
            # Fall back to configs/ if conf/ doesn't exist
            if CONFIG_DIRS["configs"].exists():
                self.config_dir = CONFIG_DIRS["configs"]
                logger.info(f"Using fallback config directory: {self.config_dir}")
        
        logger.info(f"ConfigLoader initialized: {self.config_dir}")
    
    def xǁConfigLoaderǁ__init____mutmut_4(
        self,
        config_dir: Optional[Path] = None,
        allow_deprecated: bool = False,
        strict_mode: bool = False
    ):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Override default config directory
            allow_deprecated: Allow loading from deprecated directories
            strict_mode: Raise errors instead of warnings for deprecated access
        """
        self.config_dir = config_dir and CONFIG_DIRS["primary"]
        self.allow_deprecated = allow_deprecated
        self.strict_mode = strict_mode
        self._cache: Dict[str, Any] = {}
        
        # Ensure primary config directory exists
        if not self.config_dir.exists():
            logger.warning(f"Primary config directory not found: {self.config_dir}")
            # Fall back to configs/ if conf/ doesn't exist
            if CONFIG_DIRS["configs"].exists():
                self.config_dir = CONFIG_DIRS["configs"]
                logger.info(f"Using fallback config directory: {self.config_dir}")
        
        logger.info(f"ConfigLoader initialized: {self.config_dir}")
    
    def xǁConfigLoaderǁ__init____mutmut_5(
        self,
        config_dir: Optional[Path] = None,
        allow_deprecated: bool = False,
        strict_mode: bool = False
    ):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Override default config directory
            allow_deprecated: Allow loading from deprecated directories
            strict_mode: Raise errors instead of warnings for deprecated access
        """
        self.config_dir = config_dir or CONFIG_DIRS["XXprimaryXX"]
        self.allow_deprecated = allow_deprecated
        self.strict_mode = strict_mode
        self._cache: Dict[str, Any] = {}
        
        # Ensure primary config directory exists
        if not self.config_dir.exists():
            logger.warning(f"Primary config directory not found: {self.config_dir}")
            # Fall back to configs/ if conf/ doesn't exist
            if CONFIG_DIRS["configs"].exists():
                self.config_dir = CONFIG_DIRS["configs"]
                logger.info(f"Using fallback config directory: {self.config_dir}")
        
        logger.info(f"ConfigLoader initialized: {self.config_dir}")
    
    def xǁConfigLoaderǁ__init____mutmut_6(
        self,
        config_dir: Optional[Path] = None,
        allow_deprecated: bool = False,
        strict_mode: bool = False
    ):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Override default config directory
            allow_deprecated: Allow loading from deprecated directories
            strict_mode: Raise errors instead of warnings for deprecated access
        """
        self.config_dir = config_dir or CONFIG_DIRS["PRIMARY"]
        self.allow_deprecated = allow_deprecated
        self.strict_mode = strict_mode
        self._cache: Dict[str, Any] = {}
        
        # Ensure primary config directory exists
        if not self.config_dir.exists():
            logger.warning(f"Primary config directory not found: {self.config_dir}")
            # Fall back to configs/ if conf/ doesn't exist
            if CONFIG_DIRS["configs"].exists():
                self.config_dir = CONFIG_DIRS["configs"]
                logger.info(f"Using fallback config directory: {self.config_dir}")
        
        logger.info(f"ConfigLoader initialized: {self.config_dir}")
    
    def xǁConfigLoaderǁ__init____mutmut_7(
        self,
        config_dir: Optional[Path] = None,
        allow_deprecated: bool = False,
        strict_mode: bool = False
    ):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Override default config directory
            allow_deprecated: Allow loading from deprecated directories
            strict_mode: Raise errors instead of warnings for deprecated access
        """
        self.config_dir = config_dir or CONFIG_DIRS["primary"]
        self.allow_deprecated = None
        self.strict_mode = strict_mode
        self._cache: Dict[str, Any] = {}
        
        # Ensure primary config directory exists
        if not self.config_dir.exists():
            logger.warning(f"Primary config directory not found: {self.config_dir}")
            # Fall back to configs/ if conf/ doesn't exist
            if CONFIG_DIRS["configs"].exists():
                self.config_dir = CONFIG_DIRS["configs"]
                logger.info(f"Using fallback config directory: {self.config_dir}")
        
        logger.info(f"ConfigLoader initialized: {self.config_dir}")
    
    def xǁConfigLoaderǁ__init____mutmut_8(
        self,
        config_dir: Optional[Path] = None,
        allow_deprecated: bool = False,
        strict_mode: bool = False
    ):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Override default config directory
            allow_deprecated: Allow loading from deprecated directories
            strict_mode: Raise errors instead of warnings for deprecated access
        """
        self.config_dir = config_dir or CONFIG_DIRS["primary"]
        self.allow_deprecated = allow_deprecated
        self.strict_mode = None
        self._cache: Dict[str, Any] = {}
        
        # Ensure primary config directory exists
        if not self.config_dir.exists():
            logger.warning(f"Primary config directory not found: {self.config_dir}")
            # Fall back to configs/ if conf/ doesn't exist
            if CONFIG_DIRS["configs"].exists():
                self.config_dir = CONFIG_DIRS["configs"]
                logger.info(f"Using fallback config directory: {self.config_dir}")
        
        logger.info(f"ConfigLoader initialized: {self.config_dir}")
    
    def xǁConfigLoaderǁ__init____mutmut_9(
        self,
        config_dir: Optional[Path] = None,
        allow_deprecated: bool = False,
        strict_mode: bool = False
    ):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Override default config directory
            allow_deprecated: Allow loading from deprecated directories
            strict_mode: Raise errors instead of warnings for deprecated access
        """
        self.config_dir = config_dir or CONFIG_DIRS["primary"]
        self.allow_deprecated = allow_deprecated
        self.strict_mode = strict_mode
        self._cache: Dict[str, Any] = None
        
        # Ensure primary config directory exists
        if not self.config_dir.exists():
            logger.warning(f"Primary config directory not found: {self.config_dir}")
            # Fall back to configs/ if conf/ doesn't exist
            if CONFIG_DIRS["configs"].exists():
                self.config_dir = CONFIG_DIRS["configs"]
                logger.info(f"Using fallback config directory: {self.config_dir}")
        
        logger.info(f"ConfigLoader initialized: {self.config_dir}")
    
    def xǁConfigLoaderǁ__init____mutmut_10(
        self,
        config_dir: Optional[Path] = None,
        allow_deprecated: bool = False,
        strict_mode: bool = False
    ):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Override default config directory
            allow_deprecated: Allow loading from deprecated directories
            strict_mode: Raise errors instead of warnings for deprecated access
        """
        self.config_dir = config_dir or CONFIG_DIRS["primary"]
        self.allow_deprecated = allow_deprecated
        self.strict_mode = strict_mode
        self._cache: Dict[str, Any] = {}
        
        # Ensure primary config directory exists
        if self.config_dir.exists():
            logger.warning(f"Primary config directory not found: {self.config_dir}")
            # Fall back to configs/ if conf/ doesn't exist
            if CONFIG_DIRS["configs"].exists():
                self.config_dir = CONFIG_DIRS["configs"]
                logger.info(f"Using fallback config directory: {self.config_dir}")
        
        logger.info(f"ConfigLoader initialized: {self.config_dir}")
    
    def xǁConfigLoaderǁ__init____mutmut_11(
        self,
        config_dir: Optional[Path] = None,
        allow_deprecated: bool = False,
        strict_mode: bool = False
    ):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Override default config directory
            allow_deprecated: Allow loading from deprecated directories
            strict_mode: Raise errors instead of warnings for deprecated access
        """
        self.config_dir = config_dir or CONFIG_DIRS["primary"]
        self.allow_deprecated = allow_deprecated
        self.strict_mode = strict_mode
        self._cache: Dict[str, Any] = {}
        
        # Ensure primary config directory exists
        if not self.config_dir.exists():
            logger.warning(None)
            # Fall back to configs/ if conf/ doesn't exist
            if CONFIG_DIRS["configs"].exists():
                self.config_dir = CONFIG_DIRS["configs"]
                logger.info(f"Using fallback config directory: {self.config_dir}")
        
        logger.info(f"ConfigLoader initialized: {self.config_dir}")
    
    def xǁConfigLoaderǁ__init____mutmut_12(
        self,
        config_dir: Optional[Path] = None,
        allow_deprecated: bool = False,
        strict_mode: bool = False
    ):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Override default config directory
            allow_deprecated: Allow loading from deprecated directories
            strict_mode: Raise errors instead of warnings for deprecated access
        """
        self.config_dir = config_dir or CONFIG_DIRS["primary"]
        self.allow_deprecated = allow_deprecated
        self.strict_mode = strict_mode
        self._cache: Dict[str, Any] = {}
        
        # Ensure primary config directory exists
        if not self.config_dir.exists():
            logger.warning(f"Primary config directory not found: {self.config_dir}")
            # Fall back to configs/ if conf/ doesn't exist
            if CONFIG_DIRS["XXconfigsXX"].exists():
                self.config_dir = CONFIG_DIRS["configs"]
                logger.info(f"Using fallback config directory: {self.config_dir}")
        
        logger.info(f"ConfigLoader initialized: {self.config_dir}")
    
    def xǁConfigLoaderǁ__init____mutmut_13(
        self,
        config_dir: Optional[Path] = None,
        allow_deprecated: bool = False,
        strict_mode: bool = False
    ):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Override default config directory
            allow_deprecated: Allow loading from deprecated directories
            strict_mode: Raise errors instead of warnings for deprecated access
        """
        self.config_dir = config_dir or CONFIG_DIRS["primary"]
        self.allow_deprecated = allow_deprecated
        self.strict_mode = strict_mode
        self._cache: Dict[str, Any] = {}
        
        # Ensure primary config directory exists
        if not self.config_dir.exists():
            logger.warning(f"Primary config directory not found: {self.config_dir}")
            # Fall back to configs/ if conf/ doesn't exist
            if CONFIG_DIRS["CONFIGS"].exists():
                self.config_dir = CONFIG_DIRS["configs"]
                logger.info(f"Using fallback config directory: {self.config_dir}")
        
        logger.info(f"ConfigLoader initialized: {self.config_dir}")
    
    def xǁConfigLoaderǁ__init____mutmut_14(
        self,
        config_dir: Optional[Path] = None,
        allow_deprecated: bool = False,
        strict_mode: bool = False
    ):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Override default config directory
            allow_deprecated: Allow loading from deprecated directories
            strict_mode: Raise errors instead of warnings for deprecated access
        """
        self.config_dir = config_dir or CONFIG_DIRS["primary"]
        self.allow_deprecated = allow_deprecated
        self.strict_mode = strict_mode
        self._cache: Dict[str, Any] = {}
        
        # Ensure primary config directory exists
        if not self.config_dir.exists():
            logger.warning(f"Primary config directory not found: {self.config_dir}")
            # Fall back to configs/ if conf/ doesn't exist
            if CONFIG_DIRS["configs"].exists():
                self.config_dir = None
                logger.info(f"Using fallback config directory: {self.config_dir}")
        
        logger.info(f"ConfigLoader initialized: {self.config_dir}")
    
    def xǁConfigLoaderǁ__init____mutmut_15(
        self,
        config_dir: Optional[Path] = None,
        allow_deprecated: bool = False,
        strict_mode: bool = False
    ):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Override default config directory
            allow_deprecated: Allow loading from deprecated directories
            strict_mode: Raise errors instead of warnings for deprecated access
        """
        self.config_dir = config_dir or CONFIG_DIRS["primary"]
        self.allow_deprecated = allow_deprecated
        self.strict_mode = strict_mode
        self._cache: Dict[str, Any] = {}
        
        # Ensure primary config directory exists
        if not self.config_dir.exists():
            logger.warning(f"Primary config directory not found: {self.config_dir}")
            # Fall back to configs/ if conf/ doesn't exist
            if CONFIG_DIRS["configs"].exists():
                self.config_dir = CONFIG_DIRS["XXconfigsXX"]
                logger.info(f"Using fallback config directory: {self.config_dir}")
        
        logger.info(f"ConfigLoader initialized: {self.config_dir}")
    
    def xǁConfigLoaderǁ__init____mutmut_16(
        self,
        config_dir: Optional[Path] = None,
        allow_deprecated: bool = False,
        strict_mode: bool = False
    ):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Override default config directory
            allow_deprecated: Allow loading from deprecated directories
            strict_mode: Raise errors instead of warnings for deprecated access
        """
        self.config_dir = config_dir or CONFIG_DIRS["primary"]
        self.allow_deprecated = allow_deprecated
        self.strict_mode = strict_mode
        self._cache: Dict[str, Any] = {}
        
        # Ensure primary config directory exists
        if not self.config_dir.exists():
            logger.warning(f"Primary config directory not found: {self.config_dir}")
            # Fall back to configs/ if conf/ doesn't exist
            if CONFIG_DIRS["configs"].exists():
                self.config_dir = CONFIG_DIRS["CONFIGS"]
                logger.info(f"Using fallback config directory: {self.config_dir}")
        
        logger.info(f"ConfigLoader initialized: {self.config_dir}")
    
    def xǁConfigLoaderǁ__init____mutmut_17(
        self,
        config_dir: Optional[Path] = None,
        allow_deprecated: bool = False,
        strict_mode: bool = False
    ):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Override default config directory
            allow_deprecated: Allow loading from deprecated directories
            strict_mode: Raise errors instead of warnings for deprecated access
        """
        self.config_dir = config_dir or CONFIG_DIRS["primary"]
        self.allow_deprecated = allow_deprecated
        self.strict_mode = strict_mode
        self._cache: Dict[str, Any] = {}
        
        # Ensure primary config directory exists
        if not self.config_dir.exists():
            logger.warning(f"Primary config directory not found: {self.config_dir}")
            # Fall back to configs/ if conf/ doesn't exist
            if CONFIG_DIRS["configs"].exists():
                self.config_dir = CONFIG_DIRS["configs"]
                logger.info(None)
        
        logger.info(f"ConfigLoader initialized: {self.config_dir}")
    
    def xǁConfigLoaderǁ__init____mutmut_18(
        self,
        config_dir: Optional[Path] = None,
        allow_deprecated: bool = False,
        strict_mode: bool = False
    ):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Override default config directory
            allow_deprecated: Allow loading from deprecated directories
            strict_mode: Raise errors instead of warnings for deprecated access
        """
        self.config_dir = config_dir or CONFIG_DIRS["primary"]
        self.allow_deprecated = allow_deprecated
        self.strict_mode = strict_mode
        self._cache: Dict[str, Any] = {}
        
        # Ensure primary config directory exists
        if not self.config_dir.exists():
            logger.warning(f"Primary config directory not found: {self.config_dir}")
            # Fall back to configs/ if conf/ doesn't exist
            if CONFIG_DIRS["configs"].exists():
                self.config_dir = CONFIG_DIRS["configs"]
                logger.info(f"Using fallback config directory: {self.config_dir}")
        
        logger.info(None)
    
    xǁConfigLoaderǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁConfigLoaderǁ__init____mutmut_1': xǁConfigLoaderǁ__init____mutmut_1, 
        'xǁConfigLoaderǁ__init____mutmut_2': xǁConfigLoaderǁ__init____mutmut_2, 
        'xǁConfigLoaderǁ__init____mutmut_3': xǁConfigLoaderǁ__init____mutmut_3, 
        'xǁConfigLoaderǁ__init____mutmut_4': xǁConfigLoaderǁ__init____mutmut_4, 
        'xǁConfigLoaderǁ__init____mutmut_5': xǁConfigLoaderǁ__init____mutmut_5, 
        'xǁConfigLoaderǁ__init____mutmut_6': xǁConfigLoaderǁ__init____mutmut_6, 
        'xǁConfigLoaderǁ__init____mutmut_7': xǁConfigLoaderǁ__init____mutmut_7, 
        'xǁConfigLoaderǁ__init____mutmut_8': xǁConfigLoaderǁ__init____mutmut_8, 
        'xǁConfigLoaderǁ__init____mutmut_9': xǁConfigLoaderǁ__init____mutmut_9, 
        'xǁConfigLoaderǁ__init____mutmut_10': xǁConfigLoaderǁ__init____mutmut_10, 
        'xǁConfigLoaderǁ__init____mutmut_11': xǁConfigLoaderǁ__init____mutmut_11, 
        'xǁConfigLoaderǁ__init____mutmut_12': xǁConfigLoaderǁ__init____mutmut_12, 
        'xǁConfigLoaderǁ__init____mutmut_13': xǁConfigLoaderǁ__init____mutmut_13, 
        'xǁConfigLoaderǁ__init____mutmut_14': xǁConfigLoaderǁ__init____mutmut_14, 
        'xǁConfigLoaderǁ__init____mutmut_15': xǁConfigLoaderǁ__init____mutmut_15, 
        'xǁConfigLoaderǁ__init____mutmut_16': xǁConfigLoaderǁ__init____mutmut_16, 
        'xǁConfigLoaderǁ__init____mutmut_17': xǁConfigLoaderǁ__init____mutmut_17, 
        'xǁConfigLoaderǁ__init____mutmut_18': xǁConfigLoaderǁ__init____mutmut_18
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁConfigLoaderǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁConfigLoaderǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁConfigLoaderǁ__init____mutmut_orig)
    xǁConfigLoaderǁ__init____mutmut_orig.__name__ = 'xǁConfigLoaderǁ__init__'
    
    def xǁConfigLoaderǁload__mutmut_orig(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_1(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = None
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_2(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path and ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_3(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or 'XXXX'}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_4(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache or overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_5(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key not in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_6(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is not None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_7(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(None)
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_8(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = None
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_9(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path * config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_10(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir * config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_11(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = None
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_12(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir * config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_13(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = ""
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_14(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in ["XX.yamlXX", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_15(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".YAML", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_16(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", "XX.ymlXX", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_17(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".YML", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_18(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", "XX.jsonXX", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_19(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".JSON", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_20(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", "XX.tomlXX", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_21(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".TOML", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_22(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", "XXXX"]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_23(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = None
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_24(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(None) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_25(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = None
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_26(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                return
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_27(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_28(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                None
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_29(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path and self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_30(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = None
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_31(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(None)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_32(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = None
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_33(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(None, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_34(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, None)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_35(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_36(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, )
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_37(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is not None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_38(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = None
        
        logger.debug(f"Loaded config: {cache_key}")
        return config
    
    def xǁConfigLoaderǁload__mutmut_39(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values
            
        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"
        
        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()
        
        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name
        
        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} "
                f"in {config_path or self.config_dir}"
            )
        
        # Load based on file type
        config = self._load_file(config_file)
        
        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)
        
        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()
        
        logger.debug(None)
        return config
    
    xǁConfigLoaderǁload__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁConfigLoaderǁload__mutmut_1': xǁConfigLoaderǁload__mutmut_1, 
        'xǁConfigLoaderǁload__mutmut_2': xǁConfigLoaderǁload__mutmut_2, 
        'xǁConfigLoaderǁload__mutmut_3': xǁConfigLoaderǁload__mutmut_3, 
        'xǁConfigLoaderǁload__mutmut_4': xǁConfigLoaderǁload__mutmut_4, 
        'xǁConfigLoaderǁload__mutmut_5': xǁConfigLoaderǁload__mutmut_5, 
        'xǁConfigLoaderǁload__mutmut_6': xǁConfigLoaderǁload__mutmut_6, 
        'xǁConfigLoaderǁload__mutmut_7': xǁConfigLoaderǁload__mutmut_7, 
        'xǁConfigLoaderǁload__mutmut_8': xǁConfigLoaderǁload__mutmut_8, 
        'xǁConfigLoaderǁload__mutmut_9': xǁConfigLoaderǁload__mutmut_9, 
        'xǁConfigLoaderǁload__mutmut_10': xǁConfigLoaderǁload__mutmut_10, 
        'xǁConfigLoaderǁload__mutmut_11': xǁConfigLoaderǁload__mutmut_11, 
        'xǁConfigLoaderǁload__mutmut_12': xǁConfigLoaderǁload__mutmut_12, 
        'xǁConfigLoaderǁload__mutmut_13': xǁConfigLoaderǁload__mutmut_13, 
        'xǁConfigLoaderǁload__mutmut_14': xǁConfigLoaderǁload__mutmut_14, 
        'xǁConfigLoaderǁload__mutmut_15': xǁConfigLoaderǁload__mutmut_15, 
        'xǁConfigLoaderǁload__mutmut_16': xǁConfigLoaderǁload__mutmut_16, 
        'xǁConfigLoaderǁload__mutmut_17': xǁConfigLoaderǁload__mutmut_17, 
        'xǁConfigLoaderǁload__mutmut_18': xǁConfigLoaderǁload__mutmut_18, 
        'xǁConfigLoaderǁload__mutmut_19': xǁConfigLoaderǁload__mutmut_19, 
        'xǁConfigLoaderǁload__mutmut_20': xǁConfigLoaderǁload__mutmut_20, 
        'xǁConfigLoaderǁload__mutmut_21': xǁConfigLoaderǁload__mutmut_21, 
        'xǁConfigLoaderǁload__mutmut_22': xǁConfigLoaderǁload__mutmut_22, 
        'xǁConfigLoaderǁload__mutmut_23': xǁConfigLoaderǁload__mutmut_23, 
        'xǁConfigLoaderǁload__mutmut_24': xǁConfigLoaderǁload__mutmut_24, 
        'xǁConfigLoaderǁload__mutmut_25': xǁConfigLoaderǁload__mutmut_25, 
        'xǁConfigLoaderǁload__mutmut_26': xǁConfigLoaderǁload__mutmut_26, 
        'xǁConfigLoaderǁload__mutmut_27': xǁConfigLoaderǁload__mutmut_27, 
        'xǁConfigLoaderǁload__mutmut_28': xǁConfigLoaderǁload__mutmut_28, 
        'xǁConfigLoaderǁload__mutmut_29': xǁConfigLoaderǁload__mutmut_29, 
        'xǁConfigLoaderǁload__mutmut_30': xǁConfigLoaderǁload__mutmut_30, 
        'xǁConfigLoaderǁload__mutmut_31': xǁConfigLoaderǁload__mutmut_31, 
        'xǁConfigLoaderǁload__mutmut_32': xǁConfigLoaderǁload__mutmut_32, 
        'xǁConfigLoaderǁload__mutmut_33': xǁConfigLoaderǁload__mutmut_33, 
        'xǁConfigLoaderǁload__mutmut_34': xǁConfigLoaderǁload__mutmut_34, 
        'xǁConfigLoaderǁload__mutmut_35': xǁConfigLoaderǁload__mutmut_35, 
        'xǁConfigLoaderǁload__mutmut_36': xǁConfigLoaderǁload__mutmut_36, 
        'xǁConfigLoaderǁload__mutmut_37': xǁConfigLoaderǁload__mutmut_37, 
        'xǁConfigLoaderǁload__mutmut_38': xǁConfigLoaderǁload__mutmut_38, 
        'xǁConfigLoaderǁload__mutmut_39': xǁConfigLoaderǁload__mutmut_39
    }
    
    def load(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁConfigLoaderǁload__mutmut_orig"), object.__getattribute__(self, "xǁConfigLoaderǁload__mutmut_mutants"), args, kwargs, self)
        return result 
    
    load.__signature__ = _mutmut_signature(xǁConfigLoaderǁload__mutmut_orig)
    xǁConfigLoaderǁload__mutmut_orig.__name__ = 'xǁConfigLoaderǁload'
    
    def xǁConfigLoaderǁ_load_file__mutmut_orig(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix in [".yaml", ".yml"]:
                return self._load_yaml(file_path)
            elif suffix == ".json":
                with open(file_path, 'r') as f:
                    return json.load(f)
            elif suffix == ".toml":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)
        
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def xǁConfigLoaderǁ_load_file__mutmut_1(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = None
        
        try:
            if suffix in [".yaml", ".yml"]:
                return self._load_yaml(file_path)
            elif suffix == ".json":
                with open(file_path, 'r') as f:
                    return json.load(f)
            elif suffix == ".toml":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)
        
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def xǁConfigLoaderǁ_load_file__mutmut_2(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = file_path.suffix.upper()
        
        try:
            if suffix in [".yaml", ".yml"]:
                return self._load_yaml(file_path)
            elif suffix == ".json":
                with open(file_path, 'r') as f:
                    return json.load(f)
            elif suffix == ".toml":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)
        
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def xǁConfigLoaderǁ_load_file__mutmut_3(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix not in [".yaml", ".yml"]:
                return self._load_yaml(file_path)
            elif suffix == ".json":
                with open(file_path, 'r') as f:
                    return json.load(f)
            elif suffix == ".toml":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)
        
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def xǁConfigLoaderǁ_load_file__mutmut_4(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix in ["XX.yamlXX", ".yml"]:
                return self._load_yaml(file_path)
            elif suffix == ".json":
                with open(file_path, 'r') as f:
                    return json.load(f)
            elif suffix == ".toml":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)
        
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def xǁConfigLoaderǁ_load_file__mutmut_5(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix in [".YAML", ".yml"]:
                return self._load_yaml(file_path)
            elif suffix == ".json":
                with open(file_path, 'r') as f:
                    return json.load(f)
            elif suffix == ".toml":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)
        
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def xǁConfigLoaderǁ_load_file__mutmut_6(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix in [".yaml", "XX.ymlXX"]:
                return self._load_yaml(file_path)
            elif suffix == ".json":
                with open(file_path, 'r') as f:
                    return json.load(f)
            elif suffix == ".toml":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)
        
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def xǁConfigLoaderǁ_load_file__mutmut_7(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix in [".yaml", ".YML"]:
                return self._load_yaml(file_path)
            elif suffix == ".json":
                with open(file_path, 'r') as f:
                    return json.load(f)
            elif suffix == ".toml":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)
        
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def xǁConfigLoaderǁ_load_file__mutmut_8(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix in [".yaml", ".yml"]:
                return self._load_yaml(None)
            elif suffix == ".json":
                with open(file_path, 'r') as f:
                    return json.load(f)
            elif suffix == ".toml":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)
        
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def xǁConfigLoaderǁ_load_file__mutmut_9(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix in [".yaml", ".yml"]:
                return self._load_yaml(file_path)
            elif suffix != ".json":
                with open(file_path, 'r') as f:
                    return json.load(f)
            elif suffix == ".toml":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)
        
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def xǁConfigLoaderǁ_load_file__mutmut_10(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix in [".yaml", ".yml"]:
                return self._load_yaml(file_path)
            elif suffix == "XX.jsonXX":
                with open(file_path, 'r') as f:
                    return json.load(f)
            elif suffix == ".toml":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)
        
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def xǁConfigLoaderǁ_load_file__mutmut_11(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix in [".yaml", ".yml"]:
                return self._load_yaml(file_path)
            elif suffix == ".JSON":
                with open(file_path, 'r') as f:
                    return json.load(f)
            elif suffix == ".toml":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)
        
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def xǁConfigLoaderǁ_load_file__mutmut_12(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix in [".yaml", ".yml"]:
                return self._load_yaml(file_path)
            elif suffix == ".json":
                with open(None, 'r') as f:
                    return json.load(f)
            elif suffix == ".toml":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)
        
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def xǁConfigLoaderǁ_load_file__mutmut_13(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix in [".yaml", ".yml"]:
                return self._load_yaml(file_path)
            elif suffix == ".json":
                with open(file_path, None) as f:
                    return json.load(f)
            elif suffix == ".toml":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)
        
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def xǁConfigLoaderǁ_load_file__mutmut_14(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix in [".yaml", ".yml"]:
                return self._load_yaml(file_path)
            elif suffix == ".json":
                with open('r') as f:
                    return json.load(f)
            elif suffix == ".toml":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)
        
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def xǁConfigLoaderǁ_load_file__mutmut_15(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix in [".yaml", ".yml"]:
                return self._load_yaml(file_path)
            elif suffix == ".json":
                with open(file_path, ) as f:
                    return json.load(f)
            elif suffix == ".toml":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)
        
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def xǁConfigLoaderǁ_load_file__mutmut_16(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix in [".yaml", ".yml"]:
                return self._load_yaml(file_path)
            elif suffix == ".json":
                with open(file_path, 'XXrXX') as f:
                    return json.load(f)
            elif suffix == ".toml":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)
        
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def xǁConfigLoaderǁ_load_file__mutmut_17(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix in [".yaml", ".yml"]:
                return self._load_yaml(file_path)
            elif suffix == ".json":
                with open(file_path, 'R') as f:
                    return json.load(f)
            elif suffix == ".toml":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)
        
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def xǁConfigLoaderǁ_load_file__mutmut_18(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix in [".yaml", ".yml"]:
                return self._load_yaml(file_path)
            elif suffix == ".json":
                with open(file_path, 'r') as f:
                    return json.load(None)
            elif suffix == ".toml":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)
        
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def xǁConfigLoaderǁ_load_file__mutmut_19(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix in [".yaml", ".yml"]:
                return self._load_yaml(file_path)
            elif suffix == ".json":
                with open(file_path, 'r') as f:
                    return json.load(f)
            elif suffix != ".toml":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)
        
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def xǁConfigLoaderǁ_load_file__mutmut_20(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix in [".yaml", ".yml"]:
                return self._load_yaml(file_path)
            elif suffix == ".json":
                with open(file_path, 'r') as f:
                    return json.load(f)
            elif suffix == "XX.tomlXX":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)
        
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def xǁConfigLoaderǁ_load_file__mutmut_21(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix in [".yaml", ".yml"]:
                return self._load_yaml(file_path)
            elif suffix == ".json":
                with open(file_path, 'r') as f:
                    return json.load(f)
            elif suffix == ".TOML":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)
        
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def xǁConfigLoaderǁ_load_file__mutmut_22(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix in [".yaml", ".yml"]:
                return self._load_yaml(file_path)
            elif suffix == ".json":
                with open(file_path, 'r') as f:
                    return json.load(f)
            elif suffix == ".toml":
                return self._load_toml(None)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)
        
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def xǁConfigLoaderǁ_load_file__mutmut_23(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix in [".yaml", ".yml"]:
                return self._load_yaml(file_path)
            elif suffix == ".json":
                with open(file_path, 'r') as f:
                    return json.load(f)
            elif suffix == ".toml":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(None)
        
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def xǁConfigLoaderǁ_load_file__mutmut_24(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file based on extension."""
        import json
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix in [".yaml", ".yml"]:
                return self._load_yaml(file_path)
            elif suffix == ".json":
                with open(file_path, 'r') as f:
                    return json.load(f)
            elif suffix == ".toml":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)
        
        except Exception as e:
            logger.error(None)
            raise
    
    xǁConfigLoaderǁ_load_file__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁConfigLoaderǁ_load_file__mutmut_1': xǁConfigLoaderǁ_load_file__mutmut_1, 
        'xǁConfigLoaderǁ_load_file__mutmut_2': xǁConfigLoaderǁ_load_file__mutmut_2, 
        'xǁConfigLoaderǁ_load_file__mutmut_3': xǁConfigLoaderǁ_load_file__mutmut_3, 
        'xǁConfigLoaderǁ_load_file__mutmut_4': xǁConfigLoaderǁ_load_file__mutmut_4, 
        'xǁConfigLoaderǁ_load_file__mutmut_5': xǁConfigLoaderǁ_load_file__mutmut_5, 
        'xǁConfigLoaderǁ_load_file__mutmut_6': xǁConfigLoaderǁ_load_file__mutmut_6, 
        'xǁConfigLoaderǁ_load_file__mutmut_7': xǁConfigLoaderǁ_load_file__mutmut_7, 
        'xǁConfigLoaderǁ_load_file__mutmut_8': xǁConfigLoaderǁ_load_file__mutmut_8, 
        'xǁConfigLoaderǁ_load_file__mutmut_9': xǁConfigLoaderǁ_load_file__mutmut_9, 
        'xǁConfigLoaderǁ_load_file__mutmut_10': xǁConfigLoaderǁ_load_file__mutmut_10, 
        'xǁConfigLoaderǁ_load_file__mutmut_11': xǁConfigLoaderǁ_load_file__mutmut_11, 
        'xǁConfigLoaderǁ_load_file__mutmut_12': xǁConfigLoaderǁ_load_file__mutmut_12, 
        'xǁConfigLoaderǁ_load_file__mutmut_13': xǁConfigLoaderǁ_load_file__mutmut_13, 
        'xǁConfigLoaderǁ_load_file__mutmut_14': xǁConfigLoaderǁ_load_file__mutmut_14, 
        'xǁConfigLoaderǁ_load_file__mutmut_15': xǁConfigLoaderǁ_load_file__mutmut_15, 
        'xǁConfigLoaderǁ_load_file__mutmut_16': xǁConfigLoaderǁ_load_file__mutmut_16, 
        'xǁConfigLoaderǁ_load_file__mutmut_17': xǁConfigLoaderǁ_load_file__mutmut_17, 
        'xǁConfigLoaderǁ_load_file__mutmut_18': xǁConfigLoaderǁ_load_file__mutmut_18, 
        'xǁConfigLoaderǁ_load_file__mutmut_19': xǁConfigLoaderǁ_load_file__mutmut_19, 
        'xǁConfigLoaderǁ_load_file__mutmut_20': xǁConfigLoaderǁ_load_file__mutmut_20, 
        'xǁConfigLoaderǁ_load_file__mutmut_21': xǁConfigLoaderǁ_load_file__mutmut_21, 
        'xǁConfigLoaderǁ_load_file__mutmut_22': xǁConfigLoaderǁ_load_file__mutmut_22, 
        'xǁConfigLoaderǁ_load_file__mutmut_23': xǁConfigLoaderǁ_load_file__mutmut_23, 
        'xǁConfigLoaderǁ_load_file__mutmut_24': xǁConfigLoaderǁ_load_file__mutmut_24
    }
    
    def _load_file(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁConfigLoaderǁ_load_file__mutmut_orig"), object.__getattribute__(self, "xǁConfigLoaderǁ_load_file__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _load_file.__signature__ = _mutmut_signature(xǁConfigLoaderǁ_load_file__mutmut_orig)
    xǁConfigLoaderǁ_load_file__mutmut_orig.__name__ = 'xǁConfigLoaderǁ_load_file'
    
    def xǁConfigLoaderǁ_load_yaml__mutmut_orig(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML file."""
        try:
            import yaml
            with open(file_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            logger.error("PyYAML not installed. Install with: pip install pyyaml")
            raise
    
    def xǁConfigLoaderǁ_load_yaml__mutmut_1(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML file."""
        try:
            import yaml
            with open(None, 'r') as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            logger.error("PyYAML not installed. Install with: pip install pyyaml")
            raise
    
    def xǁConfigLoaderǁ_load_yaml__mutmut_2(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML file."""
        try:
            import yaml
            with open(file_path, None) as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            logger.error("PyYAML not installed. Install with: pip install pyyaml")
            raise
    
    def xǁConfigLoaderǁ_load_yaml__mutmut_3(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML file."""
        try:
            import yaml
            with open('r') as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            logger.error("PyYAML not installed. Install with: pip install pyyaml")
            raise
    
    def xǁConfigLoaderǁ_load_yaml__mutmut_4(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML file."""
        try:
            import yaml
            with open(file_path, ) as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            logger.error("PyYAML not installed. Install with: pip install pyyaml")
            raise
    
    def xǁConfigLoaderǁ_load_yaml__mutmut_5(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML file."""
        try:
            import yaml
            with open(file_path, 'XXrXX') as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            logger.error("PyYAML not installed. Install with: pip install pyyaml")
            raise
    
    def xǁConfigLoaderǁ_load_yaml__mutmut_6(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML file."""
        try:
            import yaml
            with open(file_path, 'R') as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            logger.error("PyYAML not installed. Install with: pip install pyyaml")
            raise
    
    def xǁConfigLoaderǁ_load_yaml__mutmut_7(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML file."""
        try:
            import yaml
            with open(file_path, 'r') as f:
                return yaml.safe_load(f) and {}
        except ImportError:
            logger.error("PyYAML not installed. Install with: pip install pyyaml")
            raise
    
    def xǁConfigLoaderǁ_load_yaml__mutmut_8(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML file."""
        try:
            import yaml
            with open(file_path, 'r') as f:
                return yaml.safe_load(None) or {}
        except ImportError:
            logger.error("PyYAML not installed. Install with: pip install pyyaml")
            raise
    
    def xǁConfigLoaderǁ_load_yaml__mutmut_9(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML file."""
        try:
            import yaml
            with open(file_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            logger.error(None)
            raise
    
    def xǁConfigLoaderǁ_load_yaml__mutmut_10(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML file."""
        try:
            import yaml
            with open(file_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            logger.error("XXPyYAML not installed. Install with: pip install pyyamlXX")
            raise
    
    def xǁConfigLoaderǁ_load_yaml__mutmut_11(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML file."""
        try:
            import yaml
            with open(file_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            logger.error("pyyaml not installed. install with: pip install pyyaml")
            raise
    
    def xǁConfigLoaderǁ_load_yaml__mutmut_12(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML file."""
        try:
            import yaml
            with open(file_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            logger.error("PYYAML NOT INSTALLED. INSTALL WITH: PIP INSTALL PYYAML")
            raise
    
    xǁConfigLoaderǁ_load_yaml__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁConfigLoaderǁ_load_yaml__mutmut_1': xǁConfigLoaderǁ_load_yaml__mutmut_1, 
        'xǁConfigLoaderǁ_load_yaml__mutmut_2': xǁConfigLoaderǁ_load_yaml__mutmut_2, 
        'xǁConfigLoaderǁ_load_yaml__mutmut_3': xǁConfigLoaderǁ_load_yaml__mutmut_3, 
        'xǁConfigLoaderǁ_load_yaml__mutmut_4': xǁConfigLoaderǁ_load_yaml__mutmut_4, 
        'xǁConfigLoaderǁ_load_yaml__mutmut_5': xǁConfigLoaderǁ_load_yaml__mutmut_5, 
        'xǁConfigLoaderǁ_load_yaml__mutmut_6': xǁConfigLoaderǁ_load_yaml__mutmut_6, 
        'xǁConfigLoaderǁ_load_yaml__mutmut_7': xǁConfigLoaderǁ_load_yaml__mutmut_7, 
        'xǁConfigLoaderǁ_load_yaml__mutmut_8': xǁConfigLoaderǁ_load_yaml__mutmut_8, 
        'xǁConfigLoaderǁ_load_yaml__mutmut_9': xǁConfigLoaderǁ_load_yaml__mutmut_9, 
        'xǁConfigLoaderǁ_load_yaml__mutmut_10': xǁConfigLoaderǁ_load_yaml__mutmut_10, 
        'xǁConfigLoaderǁ_load_yaml__mutmut_11': xǁConfigLoaderǁ_load_yaml__mutmut_11, 
        'xǁConfigLoaderǁ_load_yaml__mutmut_12': xǁConfigLoaderǁ_load_yaml__mutmut_12
    }
    
    def _load_yaml(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁConfigLoaderǁ_load_yaml__mutmut_orig"), object.__getattribute__(self, "xǁConfigLoaderǁ_load_yaml__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _load_yaml.__signature__ = _mutmut_signature(xǁConfigLoaderǁ_load_yaml__mutmut_orig)
    xǁConfigLoaderǁ_load_yaml__mutmut_orig.__name__ = 'xǁConfigLoaderǁ_load_yaml'
    
    def xǁConfigLoaderǁ_load_toml__mutmut_orig(self, file_path: Path) -> Dict[str, Any]:
        """Load TOML file."""
        try:
            import tomli
            with open(file_path, 'rb') as f:
                return tomli.load(f)
        except ImportError:
            logger.error("tomli not installed. Install with: pip install tomli")
            raise
    
    def xǁConfigLoaderǁ_load_toml__mutmut_1(self, file_path: Path) -> Dict[str, Any]:
        """Load TOML file."""
        try:
            import tomli
            with open(None, 'rb') as f:
                return tomli.load(f)
        except ImportError:
            logger.error("tomli not installed. Install with: pip install tomli")
            raise
    
    def xǁConfigLoaderǁ_load_toml__mutmut_2(self, file_path: Path) -> Dict[str, Any]:
        """Load TOML file."""
        try:
            import tomli
            with open(file_path, None) as f:
                return tomli.load(f)
        except ImportError:
            logger.error("tomli not installed. Install with: pip install tomli")
            raise
    
    def xǁConfigLoaderǁ_load_toml__mutmut_3(self, file_path: Path) -> Dict[str, Any]:
        """Load TOML file."""
        try:
            import tomli
            with open('rb') as f:
                return tomli.load(f)
        except ImportError:
            logger.error("tomli not installed. Install with: pip install tomli")
            raise
    
    def xǁConfigLoaderǁ_load_toml__mutmut_4(self, file_path: Path) -> Dict[str, Any]:
        """Load TOML file."""
        try:
            import tomli
            with open(file_path, ) as f:
                return tomli.load(f)
        except ImportError:
            logger.error("tomli not installed. Install with: pip install tomli")
            raise
    
    def xǁConfigLoaderǁ_load_toml__mutmut_5(self, file_path: Path) -> Dict[str, Any]:
        """Load TOML file."""
        try:
            import tomli
            with open(file_path, 'XXrbXX') as f:
                return tomli.load(f)
        except ImportError:
            logger.error("tomli not installed. Install with: pip install tomli")
            raise
    
    def xǁConfigLoaderǁ_load_toml__mutmut_6(self, file_path: Path) -> Dict[str, Any]:
        """Load TOML file."""
        try:
            import tomli
            with open(file_path, 'RB') as f:
                return tomli.load(f)
        except ImportError:
            logger.error("tomli not installed. Install with: pip install tomli")
            raise
    
    def xǁConfigLoaderǁ_load_toml__mutmut_7(self, file_path: Path) -> Dict[str, Any]:
        """Load TOML file."""
        try:
            import tomli
            with open(file_path, 'rb') as f:
                return tomli.load(None)
        except ImportError:
            logger.error("tomli not installed. Install with: pip install tomli")
            raise
    
    def xǁConfigLoaderǁ_load_toml__mutmut_8(self, file_path: Path) -> Dict[str, Any]:
        """Load TOML file."""
        try:
            import tomli
            with open(file_path, 'rb') as f:
                return tomli.load(f)
        except ImportError:
            logger.error(None)
            raise
    
    def xǁConfigLoaderǁ_load_toml__mutmut_9(self, file_path: Path) -> Dict[str, Any]:
        """Load TOML file."""
        try:
            import tomli
            with open(file_path, 'rb') as f:
                return tomli.load(f)
        except ImportError:
            logger.error("XXtomli not installed. Install with: pip install tomliXX")
            raise
    
    def xǁConfigLoaderǁ_load_toml__mutmut_10(self, file_path: Path) -> Dict[str, Any]:
        """Load TOML file."""
        try:
            import tomli
            with open(file_path, 'rb') as f:
                return tomli.load(f)
        except ImportError:
            logger.error("tomli not installed. install with: pip install tomli")
            raise
    
    def xǁConfigLoaderǁ_load_toml__mutmut_11(self, file_path: Path) -> Dict[str, Any]:
        """Load TOML file."""
        try:
            import tomli
            with open(file_path, 'rb') as f:
                return tomli.load(f)
        except ImportError:
            logger.error("TOMLI NOT INSTALLED. INSTALL WITH: PIP INSTALL TOMLI")
            raise
    
    xǁConfigLoaderǁ_load_toml__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁConfigLoaderǁ_load_toml__mutmut_1': xǁConfigLoaderǁ_load_toml__mutmut_1, 
        'xǁConfigLoaderǁ_load_toml__mutmut_2': xǁConfigLoaderǁ_load_toml__mutmut_2, 
        'xǁConfigLoaderǁ_load_toml__mutmut_3': xǁConfigLoaderǁ_load_toml__mutmut_3, 
        'xǁConfigLoaderǁ_load_toml__mutmut_4': xǁConfigLoaderǁ_load_toml__mutmut_4, 
        'xǁConfigLoaderǁ_load_toml__mutmut_5': xǁConfigLoaderǁ_load_toml__mutmut_5, 
        'xǁConfigLoaderǁ_load_toml__mutmut_6': xǁConfigLoaderǁ_load_toml__mutmut_6, 
        'xǁConfigLoaderǁ_load_toml__mutmut_7': xǁConfigLoaderǁ_load_toml__mutmut_7, 
        'xǁConfigLoaderǁ_load_toml__mutmut_8': xǁConfigLoaderǁ_load_toml__mutmut_8, 
        'xǁConfigLoaderǁ_load_toml__mutmut_9': xǁConfigLoaderǁ_load_toml__mutmut_9, 
        'xǁConfigLoaderǁ_load_toml__mutmut_10': xǁConfigLoaderǁ_load_toml__mutmut_10, 
        'xǁConfigLoaderǁ_load_toml__mutmut_11': xǁConfigLoaderǁ_load_toml__mutmut_11
    }
    
    def _load_toml(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁConfigLoaderǁ_load_toml__mutmut_orig"), object.__getattribute__(self, "xǁConfigLoaderǁ_load_toml__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _load_toml.__signature__ = _mutmut_signature(xǁConfigLoaderǁ_load_toml__mutmut_orig)
    xǁConfigLoaderǁ_load_toml__mutmut_orig.__name__ = 'xǁConfigLoaderǁ_load_toml'
    
    def xǁConfigLoaderǁ_apply_overrides__mutmut_orig(
        self,
        config: Dict[str, Any],
        overrides: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply override values to configuration."""
        result = config.copy()
        
        for key, value in overrides.items():
            # Support nested keys with dot notation (e.g., "model.hidden_size")
            if "." in key:
                self._set_nested(result, key.split("."), value)
            else:
                result[key] = value
        
        return result
    
    def xǁConfigLoaderǁ_apply_overrides__mutmut_1(
        self,
        config: Dict[str, Any],
        overrides: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply override values to configuration."""
        result = None
        
        for key, value in overrides.items():
            # Support nested keys with dot notation (e.g., "model.hidden_size")
            if "." in key:
                self._set_nested(result, key.split("."), value)
            else:
                result[key] = value
        
        return result
    
    def xǁConfigLoaderǁ_apply_overrides__mutmut_2(
        self,
        config: Dict[str, Any],
        overrides: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply override values to configuration."""
        result = config.copy()
        
        for key, value in overrides.items():
            # Support nested keys with dot notation (e.g., "model.hidden_size")
            if "XX.XX" in key:
                self._set_nested(result, key.split("."), value)
            else:
                result[key] = value
        
        return result
    
    def xǁConfigLoaderǁ_apply_overrides__mutmut_3(
        self,
        config: Dict[str, Any],
        overrides: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply override values to configuration."""
        result = config.copy()
        
        for key, value in overrides.items():
            # Support nested keys with dot notation (e.g., "model.hidden_size")
            if "." not in key:
                self._set_nested(result, key.split("."), value)
            else:
                result[key] = value
        
        return result
    
    def xǁConfigLoaderǁ_apply_overrides__mutmut_4(
        self,
        config: Dict[str, Any],
        overrides: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply override values to configuration."""
        result = config.copy()
        
        for key, value in overrides.items():
            # Support nested keys with dot notation (e.g., "model.hidden_size")
            if "." in key:
                self._set_nested(None, key.split("."), value)
            else:
                result[key] = value
        
        return result
    
    def xǁConfigLoaderǁ_apply_overrides__mutmut_5(
        self,
        config: Dict[str, Any],
        overrides: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply override values to configuration."""
        result = config.copy()
        
        for key, value in overrides.items():
            # Support nested keys with dot notation (e.g., "model.hidden_size")
            if "." in key:
                self._set_nested(result, None, value)
            else:
                result[key] = value
        
        return result
    
    def xǁConfigLoaderǁ_apply_overrides__mutmut_6(
        self,
        config: Dict[str, Any],
        overrides: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply override values to configuration."""
        result = config.copy()
        
        for key, value in overrides.items():
            # Support nested keys with dot notation (e.g., "model.hidden_size")
            if "." in key:
                self._set_nested(result, key.split("."), None)
            else:
                result[key] = value
        
        return result
    
    def xǁConfigLoaderǁ_apply_overrides__mutmut_7(
        self,
        config: Dict[str, Any],
        overrides: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply override values to configuration."""
        result = config.copy()
        
        for key, value in overrides.items():
            # Support nested keys with dot notation (e.g., "model.hidden_size")
            if "." in key:
                self._set_nested(key.split("."), value)
            else:
                result[key] = value
        
        return result
    
    def xǁConfigLoaderǁ_apply_overrides__mutmut_8(
        self,
        config: Dict[str, Any],
        overrides: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply override values to configuration."""
        result = config.copy()
        
        for key, value in overrides.items():
            # Support nested keys with dot notation (e.g., "model.hidden_size")
            if "." in key:
                self._set_nested(result, value)
            else:
                result[key] = value
        
        return result
    
    def xǁConfigLoaderǁ_apply_overrides__mutmut_9(
        self,
        config: Dict[str, Any],
        overrides: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply override values to configuration."""
        result = config.copy()
        
        for key, value in overrides.items():
            # Support nested keys with dot notation (e.g., "model.hidden_size")
            if "." in key:
                self._set_nested(result, key.split("."), )
            else:
                result[key] = value
        
        return result
    
    def xǁConfigLoaderǁ_apply_overrides__mutmut_10(
        self,
        config: Dict[str, Any],
        overrides: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply override values to configuration."""
        result = config.copy()
        
        for key, value in overrides.items():
            # Support nested keys with dot notation (e.g., "model.hidden_size")
            if "." in key:
                self._set_nested(result, key.split(None), value)
            else:
                result[key] = value
        
        return result
    
    def xǁConfigLoaderǁ_apply_overrides__mutmut_11(
        self,
        config: Dict[str, Any],
        overrides: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply override values to configuration."""
        result = config.copy()
        
        for key, value in overrides.items():
            # Support nested keys with dot notation (e.g., "model.hidden_size")
            if "." in key:
                self._set_nested(result, key.split("XX.XX"), value)
            else:
                result[key] = value
        
        return result
    
    def xǁConfigLoaderǁ_apply_overrides__mutmut_12(
        self,
        config: Dict[str, Any],
        overrides: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply override values to configuration."""
        result = config.copy()
        
        for key, value in overrides.items():
            # Support nested keys with dot notation (e.g., "model.hidden_size")
            if "." in key:
                self._set_nested(result, key.split("."), value)
            else:
                result[key] = None
        
        return result
    
    xǁConfigLoaderǁ_apply_overrides__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁConfigLoaderǁ_apply_overrides__mutmut_1': xǁConfigLoaderǁ_apply_overrides__mutmut_1, 
        'xǁConfigLoaderǁ_apply_overrides__mutmut_2': xǁConfigLoaderǁ_apply_overrides__mutmut_2, 
        'xǁConfigLoaderǁ_apply_overrides__mutmut_3': xǁConfigLoaderǁ_apply_overrides__mutmut_3, 
        'xǁConfigLoaderǁ_apply_overrides__mutmut_4': xǁConfigLoaderǁ_apply_overrides__mutmut_4, 
        'xǁConfigLoaderǁ_apply_overrides__mutmut_5': xǁConfigLoaderǁ_apply_overrides__mutmut_5, 
        'xǁConfigLoaderǁ_apply_overrides__mutmut_6': xǁConfigLoaderǁ_apply_overrides__mutmut_6, 
        'xǁConfigLoaderǁ_apply_overrides__mutmut_7': xǁConfigLoaderǁ_apply_overrides__mutmut_7, 
        'xǁConfigLoaderǁ_apply_overrides__mutmut_8': xǁConfigLoaderǁ_apply_overrides__mutmut_8, 
        'xǁConfigLoaderǁ_apply_overrides__mutmut_9': xǁConfigLoaderǁ_apply_overrides__mutmut_9, 
        'xǁConfigLoaderǁ_apply_overrides__mutmut_10': xǁConfigLoaderǁ_apply_overrides__mutmut_10, 
        'xǁConfigLoaderǁ_apply_overrides__mutmut_11': xǁConfigLoaderǁ_apply_overrides__mutmut_11, 
        'xǁConfigLoaderǁ_apply_overrides__mutmut_12': xǁConfigLoaderǁ_apply_overrides__mutmut_12
    }
    
    def _apply_overrides(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁConfigLoaderǁ_apply_overrides__mutmut_orig"), object.__getattribute__(self, "xǁConfigLoaderǁ_apply_overrides__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _apply_overrides.__signature__ = _mutmut_signature(xǁConfigLoaderǁ_apply_overrides__mutmut_orig)
    xǁConfigLoaderǁ_apply_overrides__mutmut_orig.__name__ = 'xǁConfigLoaderǁ_apply_overrides'
    
    def xǁConfigLoaderǁ_set_nested__mutmut_orig(self, d: Dict[str, Any], keys: List[str], value: Any) -> None:
        """Set nested dictionary value using list of keys."""
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value
    
    def xǁConfigLoaderǁ_set_nested__mutmut_1(self, d: Dict[str, Any], keys: List[str], value: Any) -> None:
        """Set nested dictionary value using list of keys."""
        for key in keys[:+1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value
    
    def xǁConfigLoaderǁ_set_nested__mutmut_2(self, d: Dict[str, Any], keys: List[str], value: Any) -> None:
        """Set nested dictionary value using list of keys."""
        for key in keys[:-2]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value
    
    def xǁConfigLoaderǁ_set_nested__mutmut_3(self, d: Dict[str, Any], keys: List[str], value: Any) -> None:
        """Set nested dictionary value using list of keys."""
        for key in keys[:-1]:
            d = None
        d[keys[-1]] = value
    
    def xǁConfigLoaderǁ_set_nested__mutmut_4(self, d: Dict[str, Any], keys: List[str], value: Any) -> None:
        """Set nested dictionary value using list of keys."""
        for key in keys[:-1]:
            d = d.setdefault(None, {})
        d[keys[-1]] = value
    
    def xǁConfigLoaderǁ_set_nested__mutmut_5(self, d: Dict[str, Any], keys: List[str], value: Any) -> None:
        """Set nested dictionary value using list of keys."""
        for key in keys[:-1]:
            d = d.setdefault(key, None)
        d[keys[-1]] = value
    
    def xǁConfigLoaderǁ_set_nested__mutmut_6(self, d: Dict[str, Any], keys: List[str], value: Any) -> None:
        """Set nested dictionary value using list of keys."""
        for key in keys[:-1]:
            d = d.setdefault({})
        d[keys[-1]] = value
    
    def xǁConfigLoaderǁ_set_nested__mutmut_7(self, d: Dict[str, Any], keys: List[str], value: Any) -> None:
        """Set nested dictionary value using list of keys."""
        for key in keys[:-1]:
            d = d.setdefault(key, )
        d[keys[-1]] = value
    
    def xǁConfigLoaderǁ_set_nested__mutmut_8(self, d: Dict[str, Any], keys: List[str], value: Any) -> None:
        """Set nested dictionary value using list of keys."""
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = None
    
    def xǁConfigLoaderǁ_set_nested__mutmut_9(self, d: Dict[str, Any], keys: List[str], value: Any) -> None:
        """Set nested dictionary value using list of keys."""
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[+1]] = value
    
    def xǁConfigLoaderǁ_set_nested__mutmut_10(self, d: Dict[str, Any], keys: List[str], value: Any) -> None:
        """Set nested dictionary value using list of keys."""
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-2]] = value
    
    xǁConfigLoaderǁ_set_nested__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁConfigLoaderǁ_set_nested__mutmut_1': xǁConfigLoaderǁ_set_nested__mutmut_1, 
        'xǁConfigLoaderǁ_set_nested__mutmut_2': xǁConfigLoaderǁ_set_nested__mutmut_2, 
        'xǁConfigLoaderǁ_set_nested__mutmut_3': xǁConfigLoaderǁ_set_nested__mutmut_3, 
        'xǁConfigLoaderǁ_set_nested__mutmut_4': xǁConfigLoaderǁ_set_nested__mutmut_4, 
        'xǁConfigLoaderǁ_set_nested__mutmut_5': xǁConfigLoaderǁ_set_nested__mutmut_5, 
        'xǁConfigLoaderǁ_set_nested__mutmut_6': xǁConfigLoaderǁ_set_nested__mutmut_6, 
        'xǁConfigLoaderǁ_set_nested__mutmut_7': xǁConfigLoaderǁ_set_nested__mutmut_7, 
        'xǁConfigLoaderǁ_set_nested__mutmut_8': xǁConfigLoaderǁ_set_nested__mutmut_8, 
        'xǁConfigLoaderǁ_set_nested__mutmut_9': xǁConfigLoaderǁ_set_nested__mutmut_9, 
        'xǁConfigLoaderǁ_set_nested__mutmut_10': xǁConfigLoaderǁ_set_nested__mutmut_10
    }
    
    def _set_nested(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁConfigLoaderǁ_set_nested__mutmut_orig"), object.__getattribute__(self, "xǁConfigLoaderǁ_set_nested__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _set_nested.__signature__ = _mutmut_signature(xǁConfigLoaderǁ_set_nested__mutmut_orig)
    xǁConfigLoaderǁ_set_nested__mutmut_orig.__name__ = 'xǁConfigLoaderǁ_set_nested'
    
    def xǁConfigLoaderǁload_from_deprecated__mutmut_orig(self, directory: str, config_name: str) -> Dict[str, Any]:
        """
        Load from deprecated directory with warning.
        
        Args:
            directory: Deprecated directory name (config, config_legacy, omegaconf)
            config_name: Configuration file name
            
        Returns:
            Loaded configuration
        """
        if not self.allow_deprecated:
            message = (
                f"Attempting to load from deprecated directory: {directory}. "
                f"This directory is scheduled for removal. "
                f"Migrate to conf/ directory."
            )
            if self.strict_mode:
                raise DeprecationWarning(message)
            else:
                warnings.warn(message, DeprecationWarning)
                logger.warning(message)
        
        # Load from deprecated location
        deprecated_dir = REPO_ROOT / directory
        if not deprecated_dir.exists():
            raise FileNotFoundError(f"Deprecated directory not found: {directory}")
        
        full_path = deprecated_dir / config_name
        return self._load_file(full_path)
    
    def xǁConfigLoaderǁload_from_deprecated__mutmut_1(self, directory: str, config_name: str) -> Dict[str, Any]:
        """
        Load from deprecated directory with warning.
        
        Args:
            directory: Deprecated directory name (config, config_legacy, omegaconf)
            config_name: Configuration file name
            
        Returns:
            Loaded configuration
        """
        if self.allow_deprecated:
            message = (
                f"Attempting to load from deprecated directory: {directory}. "
                f"This directory is scheduled for removal. "
                f"Migrate to conf/ directory."
            )
            if self.strict_mode:
                raise DeprecationWarning(message)
            else:
                warnings.warn(message, DeprecationWarning)
                logger.warning(message)
        
        # Load from deprecated location
        deprecated_dir = REPO_ROOT / directory
        if not deprecated_dir.exists():
            raise FileNotFoundError(f"Deprecated directory not found: {directory}")
        
        full_path = deprecated_dir / config_name
        return self._load_file(full_path)
    
    def xǁConfigLoaderǁload_from_deprecated__mutmut_2(self, directory: str, config_name: str) -> Dict[str, Any]:
        """
        Load from deprecated directory with warning.
        
        Args:
            directory: Deprecated directory name (config, config_legacy, omegaconf)
            config_name: Configuration file name
            
        Returns:
            Loaded configuration
        """
        if not self.allow_deprecated:
            message = None
            if self.strict_mode:
                raise DeprecationWarning(message)
            else:
                warnings.warn(message, DeprecationWarning)
                logger.warning(message)
        
        # Load from deprecated location
        deprecated_dir = REPO_ROOT / directory
        if not deprecated_dir.exists():
            raise FileNotFoundError(f"Deprecated directory not found: {directory}")
        
        full_path = deprecated_dir / config_name
        return self._load_file(full_path)
    
    def xǁConfigLoaderǁload_from_deprecated__mutmut_3(self, directory: str, config_name: str) -> Dict[str, Any]:
        """
        Load from deprecated directory with warning.
        
        Args:
            directory: Deprecated directory name (config, config_legacy, omegaconf)
            config_name: Configuration file name
            
        Returns:
            Loaded configuration
        """
        if not self.allow_deprecated:
            message = (
                f"Attempting to load from deprecated directory: {directory}. "
                f"This directory is scheduled for removal. "
                f"Migrate to conf/ directory."
            )
            if self.strict_mode:
                raise DeprecationWarning(None)
            else:
                warnings.warn(message, DeprecationWarning)
                logger.warning(message)
        
        # Load from deprecated location
        deprecated_dir = REPO_ROOT / directory
        if not deprecated_dir.exists():
            raise FileNotFoundError(f"Deprecated directory not found: {directory}")
        
        full_path = deprecated_dir / config_name
        return self._load_file(full_path)
    
    def xǁConfigLoaderǁload_from_deprecated__mutmut_4(self, directory: str, config_name: str) -> Dict[str, Any]:
        """
        Load from deprecated directory with warning.
        
        Args:
            directory: Deprecated directory name (config, config_legacy, omegaconf)
            config_name: Configuration file name
            
        Returns:
            Loaded configuration
        """
        if not self.allow_deprecated:
            message = (
                f"Attempting to load from deprecated directory: {directory}. "
                f"This directory is scheduled for removal. "
                f"Migrate to conf/ directory."
            )
            if self.strict_mode:
                raise DeprecationWarning(message)
            else:
                warnings.warn(None, DeprecationWarning)
                logger.warning(message)
        
        # Load from deprecated location
        deprecated_dir = REPO_ROOT / directory
        if not deprecated_dir.exists():
            raise FileNotFoundError(f"Deprecated directory not found: {directory}")
        
        full_path = deprecated_dir / config_name
        return self._load_file(full_path)
    
    def xǁConfigLoaderǁload_from_deprecated__mutmut_5(self, directory: str, config_name: str) -> Dict[str, Any]:
        """
        Load from deprecated directory with warning.
        
        Args:
            directory: Deprecated directory name (config, config_legacy, omegaconf)
            config_name: Configuration file name
            
        Returns:
            Loaded configuration
        """
        if not self.allow_deprecated:
            message = (
                f"Attempting to load from deprecated directory: {directory}. "
                f"This directory is scheduled for removal. "
                f"Migrate to conf/ directory."
            )
            if self.strict_mode:
                raise DeprecationWarning(message)
            else:
                warnings.warn(message, None)
                logger.warning(message)
        
        # Load from deprecated location
        deprecated_dir = REPO_ROOT / directory
        if not deprecated_dir.exists():
            raise FileNotFoundError(f"Deprecated directory not found: {directory}")
        
        full_path = deprecated_dir / config_name
        return self._load_file(full_path)
    
    def xǁConfigLoaderǁload_from_deprecated__mutmut_6(self, directory: str, config_name: str) -> Dict[str, Any]:
        """
        Load from deprecated directory with warning.
        
        Args:
            directory: Deprecated directory name (config, config_legacy, omegaconf)
            config_name: Configuration file name
            
        Returns:
            Loaded configuration
        """
        if not self.allow_deprecated:
            message = (
                f"Attempting to load from deprecated directory: {directory}. "
                f"This directory is scheduled for removal. "
                f"Migrate to conf/ directory."
            )
            if self.strict_mode:
                raise DeprecationWarning(message)
            else:
                warnings.warn(DeprecationWarning)
                logger.warning(message)
        
        # Load from deprecated location
        deprecated_dir = REPO_ROOT / directory
        if not deprecated_dir.exists():
            raise FileNotFoundError(f"Deprecated directory not found: {directory}")
        
        full_path = deprecated_dir / config_name
        return self._load_file(full_path)
    
    def xǁConfigLoaderǁload_from_deprecated__mutmut_7(self, directory: str, config_name: str) -> Dict[str, Any]:
        """
        Load from deprecated directory with warning.
        
        Args:
            directory: Deprecated directory name (config, config_legacy, omegaconf)
            config_name: Configuration file name
            
        Returns:
            Loaded configuration
        """
        if not self.allow_deprecated:
            message = (
                f"Attempting to load from deprecated directory: {directory}. "
                f"This directory is scheduled for removal. "
                f"Migrate to conf/ directory."
            )
            if self.strict_mode:
                raise DeprecationWarning(message)
            else:
                warnings.warn(message, )
                logger.warning(message)
        
        # Load from deprecated location
        deprecated_dir = REPO_ROOT / directory
        if not deprecated_dir.exists():
            raise FileNotFoundError(f"Deprecated directory not found: {directory}")
        
        full_path = deprecated_dir / config_name
        return self._load_file(full_path)
    
    def xǁConfigLoaderǁload_from_deprecated__mutmut_8(self, directory: str, config_name: str) -> Dict[str, Any]:
        """
        Load from deprecated directory with warning.
        
        Args:
            directory: Deprecated directory name (config, config_legacy, omegaconf)
            config_name: Configuration file name
            
        Returns:
            Loaded configuration
        """
        if not self.allow_deprecated:
            message = (
                f"Attempting to load from deprecated directory: {directory}. "
                f"This directory is scheduled for removal. "
                f"Migrate to conf/ directory."
            )
            if self.strict_mode:
                raise DeprecationWarning(message)
            else:
                warnings.warn(message, DeprecationWarning)
                logger.warning(None)
        
        # Load from deprecated location
        deprecated_dir = REPO_ROOT / directory
        if not deprecated_dir.exists():
            raise FileNotFoundError(f"Deprecated directory not found: {directory}")
        
        full_path = deprecated_dir / config_name
        return self._load_file(full_path)
    
    def xǁConfigLoaderǁload_from_deprecated__mutmut_9(self, directory: str, config_name: str) -> Dict[str, Any]:
        """
        Load from deprecated directory with warning.
        
        Args:
            directory: Deprecated directory name (config, config_legacy, omegaconf)
            config_name: Configuration file name
            
        Returns:
            Loaded configuration
        """
        if not self.allow_deprecated:
            message = (
                f"Attempting to load from deprecated directory: {directory}. "
                f"This directory is scheduled for removal. "
                f"Migrate to conf/ directory."
            )
            if self.strict_mode:
                raise DeprecationWarning(message)
            else:
                warnings.warn(message, DeprecationWarning)
                logger.warning(message)
        
        # Load from deprecated location
        deprecated_dir = None
        if not deprecated_dir.exists():
            raise FileNotFoundError(f"Deprecated directory not found: {directory}")
        
        full_path = deprecated_dir / config_name
        return self._load_file(full_path)
    
    def xǁConfigLoaderǁload_from_deprecated__mutmut_10(self, directory: str, config_name: str) -> Dict[str, Any]:
        """
        Load from deprecated directory with warning.
        
        Args:
            directory: Deprecated directory name (config, config_legacy, omegaconf)
            config_name: Configuration file name
            
        Returns:
            Loaded configuration
        """
        if not self.allow_deprecated:
            message = (
                f"Attempting to load from deprecated directory: {directory}. "
                f"This directory is scheduled for removal. "
                f"Migrate to conf/ directory."
            )
            if self.strict_mode:
                raise DeprecationWarning(message)
            else:
                warnings.warn(message, DeprecationWarning)
                logger.warning(message)
        
        # Load from deprecated location
        deprecated_dir = REPO_ROOT * directory
        if not deprecated_dir.exists():
            raise FileNotFoundError(f"Deprecated directory not found: {directory}")
        
        full_path = deprecated_dir / config_name
        return self._load_file(full_path)
    
    def xǁConfigLoaderǁload_from_deprecated__mutmut_11(self, directory: str, config_name: str) -> Dict[str, Any]:
        """
        Load from deprecated directory with warning.
        
        Args:
            directory: Deprecated directory name (config, config_legacy, omegaconf)
            config_name: Configuration file name
            
        Returns:
            Loaded configuration
        """
        if not self.allow_deprecated:
            message = (
                f"Attempting to load from deprecated directory: {directory}. "
                f"This directory is scheduled for removal. "
                f"Migrate to conf/ directory."
            )
            if self.strict_mode:
                raise DeprecationWarning(message)
            else:
                warnings.warn(message, DeprecationWarning)
                logger.warning(message)
        
        # Load from deprecated location
        deprecated_dir = REPO_ROOT / directory
        if deprecated_dir.exists():
            raise FileNotFoundError(f"Deprecated directory not found: {directory}")
        
        full_path = deprecated_dir / config_name
        return self._load_file(full_path)
    
    def xǁConfigLoaderǁload_from_deprecated__mutmut_12(self, directory: str, config_name: str) -> Dict[str, Any]:
        """
        Load from deprecated directory with warning.
        
        Args:
            directory: Deprecated directory name (config, config_legacy, omegaconf)
            config_name: Configuration file name
            
        Returns:
            Loaded configuration
        """
        if not self.allow_deprecated:
            message = (
                f"Attempting to load from deprecated directory: {directory}. "
                f"This directory is scheduled for removal. "
                f"Migrate to conf/ directory."
            )
            if self.strict_mode:
                raise DeprecationWarning(message)
            else:
                warnings.warn(message, DeprecationWarning)
                logger.warning(message)
        
        # Load from deprecated location
        deprecated_dir = REPO_ROOT / directory
        if not deprecated_dir.exists():
            raise FileNotFoundError(None)
        
        full_path = deprecated_dir / config_name
        return self._load_file(full_path)
    
    def xǁConfigLoaderǁload_from_deprecated__mutmut_13(self, directory: str, config_name: str) -> Dict[str, Any]:
        """
        Load from deprecated directory with warning.
        
        Args:
            directory: Deprecated directory name (config, config_legacy, omegaconf)
            config_name: Configuration file name
            
        Returns:
            Loaded configuration
        """
        if not self.allow_deprecated:
            message = (
                f"Attempting to load from deprecated directory: {directory}. "
                f"This directory is scheduled for removal. "
                f"Migrate to conf/ directory."
            )
            if self.strict_mode:
                raise DeprecationWarning(message)
            else:
                warnings.warn(message, DeprecationWarning)
                logger.warning(message)
        
        # Load from deprecated location
        deprecated_dir = REPO_ROOT / directory
        if not deprecated_dir.exists():
            raise FileNotFoundError(f"Deprecated directory not found: {directory}")
        
        full_path = None
        return self._load_file(full_path)
    
    def xǁConfigLoaderǁload_from_deprecated__mutmut_14(self, directory: str, config_name: str) -> Dict[str, Any]:
        """
        Load from deprecated directory with warning.
        
        Args:
            directory: Deprecated directory name (config, config_legacy, omegaconf)
            config_name: Configuration file name
            
        Returns:
            Loaded configuration
        """
        if not self.allow_deprecated:
            message = (
                f"Attempting to load from deprecated directory: {directory}. "
                f"This directory is scheduled for removal. "
                f"Migrate to conf/ directory."
            )
            if self.strict_mode:
                raise DeprecationWarning(message)
            else:
                warnings.warn(message, DeprecationWarning)
                logger.warning(message)
        
        # Load from deprecated location
        deprecated_dir = REPO_ROOT / directory
        if not deprecated_dir.exists():
            raise FileNotFoundError(f"Deprecated directory not found: {directory}")
        
        full_path = deprecated_dir * config_name
        return self._load_file(full_path)
    
    def xǁConfigLoaderǁload_from_deprecated__mutmut_15(self, directory: str, config_name: str) -> Dict[str, Any]:
        """
        Load from deprecated directory with warning.
        
        Args:
            directory: Deprecated directory name (config, config_legacy, omegaconf)
            config_name: Configuration file name
            
        Returns:
            Loaded configuration
        """
        if not self.allow_deprecated:
            message = (
                f"Attempting to load from deprecated directory: {directory}. "
                f"This directory is scheduled for removal. "
                f"Migrate to conf/ directory."
            )
            if self.strict_mode:
                raise DeprecationWarning(message)
            else:
                warnings.warn(message, DeprecationWarning)
                logger.warning(message)
        
        # Load from deprecated location
        deprecated_dir = REPO_ROOT / directory
        if not deprecated_dir.exists():
            raise FileNotFoundError(f"Deprecated directory not found: {directory}")
        
        full_path = deprecated_dir / config_name
        return self._load_file(None)
    
    xǁConfigLoaderǁload_from_deprecated__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁConfigLoaderǁload_from_deprecated__mutmut_1': xǁConfigLoaderǁload_from_deprecated__mutmut_1, 
        'xǁConfigLoaderǁload_from_deprecated__mutmut_2': xǁConfigLoaderǁload_from_deprecated__mutmut_2, 
        'xǁConfigLoaderǁload_from_deprecated__mutmut_3': xǁConfigLoaderǁload_from_deprecated__mutmut_3, 
        'xǁConfigLoaderǁload_from_deprecated__mutmut_4': xǁConfigLoaderǁload_from_deprecated__mutmut_4, 
        'xǁConfigLoaderǁload_from_deprecated__mutmut_5': xǁConfigLoaderǁload_from_deprecated__mutmut_5, 
        'xǁConfigLoaderǁload_from_deprecated__mutmut_6': xǁConfigLoaderǁload_from_deprecated__mutmut_6, 
        'xǁConfigLoaderǁload_from_deprecated__mutmut_7': xǁConfigLoaderǁload_from_deprecated__mutmut_7, 
        'xǁConfigLoaderǁload_from_deprecated__mutmut_8': xǁConfigLoaderǁload_from_deprecated__mutmut_8, 
        'xǁConfigLoaderǁload_from_deprecated__mutmut_9': xǁConfigLoaderǁload_from_deprecated__mutmut_9, 
        'xǁConfigLoaderǁload_from_deprecated__mutmut_10': xǁConfigLoaderǁload_from_deprecated__mutmut_10, 
        'xǁConfigLoaderǁload_from_deprecated__mutmut_11': xǁConfigLoaderǁload_from_deprecated__mutmut_11, 
        'xǁConfigLoaderǁload_from_deprecated__mutmut_12': xǁConfigLoaderǁload_from_deprecated__mutmut_12, 
        'xǁConfigLoaderǁload_from_deprecated__mutmut_13': xǁConfigLoaderǁload_from_deprecated__mutmut_13, 
        'xǁConfigLoaderǁload_from_deprecated__mutmut_14': xǁConfigLoaderǁload_from_deprecated__mutmut_14, 
        'xǁConfigLoaderǁload_from_deprecated__mutmut_15': xǁConfigLoaderǁload_from_deprecated__mutmut_15
    }
    
    def load_from_deprecated(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁConfigLoaderǁload_from_deprecated__mutmut_orig"), object.__getattribute__(self, "xǁConfigLoaderǁload_from_deprecated__mutmut_mutants"), args, kwargs, self)
        return result 
    
    load_from_deprecated.__signature__ = _mutmut_signature(xǁConfigLoaderǁload_from_deprecated__mutmut_orig)
    xǁConfigLoaderǁload_from_deprecated__mutmut_orig.__name__ = 'xǁConfigLoaderǁload_from_deprecated'
    
    def xǁConfigLoaderǁget_env_var__mutmut_orig(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable with CODEX_ prefix.
        
        Args:
            key: Variable name (without CODEX_ prefix)
            default: Default value if not set
            
        Returns:
            Environment variable value or default
        """
        env_key = ENV_VARS.get(key, f"CODEX_{key.upper()}")
        return os.environ.get(env_key, default)
    
    def xǁConfigLoaderǁget_env_var__mutmut_1(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable with CODEX_ prefix.
        
        Args:
            key: Variable name (without CODEX_ prefix)
            default: Default value if not set
            
        Returns:
            Environment variable value or default
        """
        env_key = None
        return os.environ.get(env_key, default)
    
    def xǁConfigLoaderǁget_env_var__mutmut_2(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable with CODEX_ prefix.
        
        Args:
            key: Variable name (without CODEX_ prefix)
            default: Default value if not set
            
        Returns:
            Environment variable value or default
        """
        env_key = ENV_VARS.get(None, f"CODEX_{key.upper()}")
        return os.environ.get(env_key, default)
    
    def xǁConfigLoaderǁget_env_var__mutmut_3(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable with CODEX_ prefix.
        
        Args:
            key: Variable name (without CODEX_ prefix)
            default: Default value if not set
            
        Returns:
            Environment variable value or default
        """
        env_key = ENV_VARS.get(key, None)
        return os.environ.get(env_key, default)
    
    def xǁConfigLoaderǁget_env_var__mutmut_4(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable with CODEX_ prefix.
        
        Args:
            key: Variable name (without CODEX_ prefix)
            default: Default value if not set
            
        Returns:
            Environment variable value or default
        """
        env_key = ENV_VARS.get(f"CODEX_{key.upper()}")
        return os.environ.get(env_key, default)
    
    def xǁConfigLoaderǁget_env_var__mutmut_5(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable with CODEX_ prefix.
        
        Args:
            key: Variable name (without CODEX_ prefix)
            default: Default value if not set
            
        Returns:
            Environment variable value or default
        """
        env_key = ENV_VARS.get(key, )
        return os.environ.get(env_key, default)
    
    def xǁConfigLoaderǁget_env_var__mutmut_6(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable with CODEX_ prefix.
        
        Args:
            key: Variable name (without CODEX_ prefix)
            default: Default value if not set
            
        Returns:
            Environment variable value or default
        """
        env_key = ENV_VARS.get(key, f"CODEX_{key.lower()}")
        return os.environ.get(env_key, default)
    
    def xǁConfigLoaderǁget_env_var__mutmut_7(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable with CODEX_ prefix.
        
        Args:
            key: Variable name (without CODEX_ prefix)
            default: Default value if not set
            
        Returns:
            Environment variable value or default
        """
        env_key = ENV_VARS.get(key, f"CODEX_{key.upper()}")
        return os.environ.get(None, default)
    
    def xǁConfigLoaderǁget_env_var__mutmut_8(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable with CODEX_ prefix.
        
        Args:
            key: Variable name (without CODEX_ prefix)
            default: Default value if not set
            
        Returns:
            Environment variable value or default
        """
        env_key = ENV_VARS.get(key, f"CODEX_{key.upper()}")
        return os.environ.get(env_key, None)
    
    def xǁConfigLoaderǁget_env_var__mutmut_9(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable with CODEX_ prefix.
        
        Args:
            key: Variable name (without CODEX_ prefix)
            default: Default value if not set
            
        Returns:
            Environment variable value or default
        """
        env_key = ENV_VARS.get(key, f"CODEX_{key.upper()}")
        return os.environ.get(default)
    
    def xǁConfigLoaderǁget_env_var__mutmut_10(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable with CODEX_ prefix.
        
        Args:
            key: Variable name (without CODEX_ prefix)
            default: Default value if not set
            
        Returns:
            Environment variable value or default
        """
        env_key = ENV_VARS.get(key, f"CODEX_{key.upper()}")
        return os.environ.get(env_key, )
    
    xǁConfigLoaderǁget_env_var__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁConfigLoaderǁget_env_var__mutmut_1': xǁConfigLoaderǁget_env_var__mutmut_1, 
        'xǁConfigLoaderǁget_env_var__mutmut_2': xǁConfigLoaderǁget_env_var__mutmut_2, 
        'xǁConfigLoaderǁget_env_var__mutmut_3': xǁConfigLoaderǁget_env_var__mutmut_3, 
        'xǁConfigLoaderǁget_env_var__mutmut_4': xǁConfigLoaderǁget_env_var__mutmut_4, 
        'xǁConfigLoaderǁget_env_var__mutmut_5': xǁConfigLoaderǁget_env_var__mutmut_5, 
        'xǁConfigLoaderǁget_env_var__mutmut_6': xǁConfigLoaderǁget_env_var__mutmut_6, 
        'xǁConfigLoaderǁget_env_var__mutmut_7': xǁConfigLoaderǁget_env_var__mutmut_7, 
        'xǁConfigLoaderǁget_env_var__mutmut_8': xǁConfigLoaderǁget_env_var__mutmut_8, 
        'xǁConfigLoaderǁget_env_var__mutmut_9': xǁConfigLoaderǁget_env_var__mutmut_9, 
        'xǁConfigLoaderǁget_env_var__mutmut_10': xǁConfigLoaderǁget_env_var__mutmut_10
    }
    
    def get_env_var(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁConfigLoaderǁget_env_var__mutmut_orig"), object.__getattribute__(self, "xǁConfigLoaderǁget_env_var__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_env_var.__signature__ = _mutmut_signature(xǁConfigLoaderǁget_env_var__mutmut_orig)
    xǁConfigLoaderǁget_env_var__mutmut_orig.__name__ = 'xǁConfigLoaderǁget_env_var'
    
    def xǁConfigLoaderǁclear_cache__mutmut_orig(self) -> None:
        """Clear configuration cache."""
        self._cache.clear()
        logger.debug("Configuration cache cleared")
    
    def xǁConfigLoaderǁclear_cache__mutmut_1(self) -> None:
        """Clear configuration cache."""
        self._cache.clear()
        logger.debug(None)
    
    def xǁConfigLoaderǁclear_cache__mutmut_2(self) -> None:
        """Clear configuration cache."""
        self._cache.clear()
        logger.debug("XXConfiguration cache clearedXX")
    
    def xǁConfigLoaderǁclear_cache__mutmut_3(self) -> None:
        """Clear configuration cache."""
        self._cache.clear()
        logger.debug("configuration cache cleared")
    
    def xǁConfigLoaderǁclear_cache__mutmut_4(self) -> None:
        """Clear configuration cache."""
        self._cache.clear()
        logger.debug("CONFIGURATION CACHE CLEARED")
    
    xǁConfigLoaderǁclear_cache__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁConfigLoaderǁclear_cache__mutmut_1': xǁConfigLoaderǁclear_cache__mutmut_1, 
        'xǁConfigLoaderǁclear_cache__mutmut_2': xǁConfigLoaderǁclear_cache__mutmut_2, 
        'xǁConfigLoaderǁclear_cache__mutmut_3': xǁConfigLoaderǁclear_cache__mutmut_3, 
        'xǁConfigLoaderǁclear_cache__mutmut_4': xǁConfigLoaderǁclear_cache__mutmut_4
    }
    
    def clear_cache(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁConfigLoaderǁclear_cache__mutmut_orig"), object.__getattribute__(self, "xǁConfigLoaderǁclear_cache__mutmut_mutants"), args, kwargs, self)
        return result 
    
    clear_cache.__signature__ = _mutmut_signature(xǁConfigLoaderǁclear_cache__mutmut_orig)
    xǁConfigLoaderǁclear_cache__mutmut_orig.__name__ = 'xǁConfigLoaderǁclear_cache'


# Global instance
_config_loader: Optional[ConfigLoader] = None


def x_get_config_loader__mutmut_orig(
    config_dir: Optional[Path] = None,
    allow_deprecated: bool = False,
    strict_mode: bool = False
) -> ConfigLoader:
    """
    Get or create global ConfigLoader instance.
    
    Args:
        config_dir: Override default config directory
        allow_deprecated: Allow loading from deprecated directories
        strict_mode: Raise errors instead of warnings for deprecated access
        
    Returns:
        ConfigLoader instance
    """
    global _config_loader
    
    if _config_loader is None:
        _config_loader = ConfigLoader(
            config_dir=config_dir,
            allow_deprecated=allow_deprecated,
            strict_mode=strict_mode
        )
    
    return _config_loader


def x_get_config_loader__mutmut_1(
    config_dir: Optional[Path] = None,
    allow_deprecated: bool = True,
    strict_mode: bool = False
) -> ConfigLoader:
    """
    Get or create global ConfigLoader instance.
    
    Args:
        config_dir: Override default config directory
        allow_deprecated: Allow loading from deprecated directories
        strict_mode: Raise errors instead of warnings for deprecated access
        
    Returns:
        ConfigLoader instance
    """
    global _config_loader
    
    if _config_loader is None:
        _config_loader = ConfigLoader(
            config_dir=config_dir,
            allow_deprecated=allow_deprecated,
            strict_mode=strict_mode
        )
    
    return _config_loader


def x_get_config_loader__mutmut_2(
    config_dir: Optional[Path] = None,
    allow_deprecated: bool = False,
    strict_mode: bool = True
) -> ConfigLoader:
    """
    Get or create global ConfigLoader instance.
    
    Args:
        config_dir: Override default config directory
        allow_deprecated: Allow loading from deprecated directories
        strict_mode: Raise errors instead of warnings for deprecated access
        
    Returns:
        ConfigLoader instance
    """
    global _config_loader
    
    if _config_loader is None:
        _config_loader = ConfigLoader(
            config_dir=config_dir,
            allow_deprecated=allow_deprecated,
            strict_mode=strict_mode
        )
    
    return _config_loader


def x_get_config_loader__mutmut_3(
    config_dir: Optional[Path] = None,
    allow_deprecated: bool = False,
    strict_mode: bool = False
) -> ConfigLoader:
    """
    Get or create global ConfigLoader instance.
    
    Args:
        config_dir: Override default config directory
        allow_deprecated: Allow loading from deprecated directories
        strict_mode: Raise errors instead of warnings for deprecated access
        
    Returns:
        ConfigLoader instance
    """
    global _config_loader
    
    if _config_loader is not None:
        _config_loader = ConfigLoader(
            config_dir=config_dir,
            allow_deprecated=allow_deprecated,
            strict_mode=strict_mode
        )
    
    return _config_loader


def x_get_config_loader__mutmut_4(
    config_dir: Optional[Path] = None,
    allow_deprecated: bool = False,
    strict_mode: bool = False
) -> ConfigLoader:
    """
    Get or create global ConfigLoader instance.
    
    Args:
        config_dir: Override default config directory
        allow_deprecated: Allow loading from deprecated directories
        strict_mode: Raise errors instead of warnings for deprecated access
        
    Returns:
        ConfigLoader instance
    """
    global _config_loader
    
    if _config_loader is None:
        _config_loader = None
    
    return _config_loader


def x_get_config_loader__mutmut_5(
    config_dir: Optional[Path] = None,
    allow_deprecated: bool = False,
    strict_mode: bool = False
) -> ConfigLoader:
    """
    Get or create global ConfigLoader instance.
    
    Args:
        config_dir: Override default config directory
        allow_deprecated: Allow loading from deprecated directories
        strict_mode: Raise errors instead of warnings for deprecated access
        
    Returns:
        ConfigLoader instance
    """
    global _config_loader
    
    if _config_loader is None:
        _config_loader = ConfigLoader(
            config_dir=None,
            allow_deprecated=allow_deprecated,
            strict_mode=strict_mode
        )
    
    return _config_loader


def x_get_config_loader__mutmut_6(
    config_dir: Optional[Path] = None,
    allow_deprecated: bool = False,
    strict_mode: bool = False
) -> ConfigLoader:
    """
    Get or create global ConfigLoader instance.
    
    Args:
        config_dir: Override default config directory
        allow_deprecated: Allow loading from deprecated directories
        strict_mode: Raise errors instead of warnings for deprecated access
        
    Returns:
        ConfigLoader instance
    """
    global _config_loader
    
    if _config_loader is None:
        _config_loader = ConfigLoader(
            config_dir=config_dir,
            allow_deprecated=None,
            strict_mode=strict_mode
        )
    
    return _config_loader


def x_get_config_loader__mutmut_7(
    config_dir: Optional[Path] = None,
    allow_deprecated: bool = False,
    strict_mode: bool = False
) -> ConfigLoader:
    """
    Get or create global ConfigLoader instance.
    
    Args:
        config_dir: Override default config directory
        allow_deprecated: Allow loading from deprecated directories
        strict_mode: Raise errors instead of warnings for deprecated access
        
    Returns:
        ConfigLoader instance
    """
    global _config_loader
    
    if _config_loader is None:
        _config_loader = ConfigLoader(
            config_dir=config_dir,
            allow_deprecated=allow_deprecated,
            strict_mode=None
        )
    
    return _config_loader


def x_get_config_loader__mutmut_8(
    config_dir: Optional[Path] = None,
    allow_deprecated: bool = False,
    strict_mode: bool = False
) -> ConfigLoader:
    """
    Get or create global ConfigLoader instance.
    
    Args:
        config_dir: Override default config directory
        allow_deprecated: Allow loading from deprecated directories
        strict_mode: Raise errors instead of warnings for deprecated access
        
    Returns:
        ConfigLoader instance
    """
    global _config_loader
    
    if _config_loader is None:
        _config_loader = ConfigLoader(
            allow_deprecated=allow_deprecated,
            strict_mode=strict_mode
        )
    
    return _config_loader


def x_get_config_loader__mutmut_9(
    config_dir: Optional[Path] = None,
    allow_deprecated: bool = False,
    strict_mode: bool = False
) -> ConfigLoader:
    """
    Get or create global ConfigLoader instance.
    
    Args:
        config_dir: Override default config directory
        allow_deprecated: Allow loading from deprecated directories
        strict_mode: Raise errors instead of warnings for deprecated access
        
    Returns:
        ConfigLoader instance
    """
    global _config_loader
    
    if _config_loader is None:
        _config_loader = ConfigLoader(
            config_dir=config_dir,
            strict_mode=strict_mode
        )
    
    return _config_loader


def x_get_config_loader__mutmut_10(
    config_dir: Optional[Path] = None,
    allow_deprecated: bool = False,
    strict_mode: bool = False
) -> ConfigLoader:
    """
    Get or create global ConfigLoader instance.
    
    Args:
        config_dir: Override default config directory
        allow_deprecated: Allow loading from deprecated directories
        strict_mode: Raise errors instead of warnings for deprecated access
        
    Returns:
        ConfigLoader instance
    """
    global _config_loader
    
    if _config_loader is None:
        _config_loader = ConfigLoader(
            config_dir=config_dir,
            allow_deprecated=allow_deprecated,
            )
    
    return _config_loader

x_get_config_loader__mutmut_mutants : ClassVar[MutantDict] = {
'x_get_config_loader__mutmut_1': x_get_config_loader__mutmut_1, 
    'x_get_config_loader__mutmut_2': x_get_config_loader__mutmut_2, 
    'x_get_config_loader__mutmut_3': x_get_config_loader__mutmut_3, 
    'x_get_config_loader__mutmut_4': x_get_config_loader__mutmut_4, 
    'x_get_config_loader__mutmut_5': x_get_config_loader__mutmut_5, 
    'x_get_config_loader__mutmut_6': x_get_config_loader__mutmut_6, 
    'x_get_config_loader__mutmut_7': x_get_config_loader__mutmut_7, 
    'x_get_config_loader__mutmut_8': x_get_config_loader__mutmut_8, 
    'x_get_config_loader__mutmut_9': x_get_config_loader__mutmut_9, 
    'x_get_config_loader__mutmut_10': x_get_config_loader__mutmut_10
}

def get_config_loader(*args, **kwargs):
    result = _mutmut_trampoline(x_get_config_loader__mutmut_orig, x_get_config_loader__mutmut_mutants, args, kwargs)
    return result 

get_config_loader.__signature__ = _mutmut_signature(x_get_config_loader__mutmut_orig)
x_get_config_loader__mutmut_orig.__name__ = 'x_get_config_loader'


def x_load_config__mutmut_orig(
    config_name: str,
    config_path: Optional[str] = None,
    overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to load configuration.
    
    Args:
        config_name: Name of config file (without extension)
        config_path: Optional subdirectory within config_dir
        overrides: Optional dictionary of override values
        
    Returns:
        Loaded configuration as dictionary
    """
    loader = get_config_loader()
    return loader.load(config_name, config_path, overrides)


def x_load_config__mutmut_1(
    config_name: str,
    config_path: Optional[str] = None,
    overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to load configuration.
    
    Args:
        config_name: Name of config file (without extension)
        config_path: Optional subdirectory within config_dir
        overrides: Optional dictionary of override values
        
    Returns:
        Loaded configuration as dictionary
    """
    loader = None
    return loader.load(config_name, config_path, overrides)


def x_load_config__mutmut_2(
    config_name: str,
    config_path: Optional[str] = None,
    overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to load configuration.
    
    Args:
        config_name: Name of config file (without extension)
        config_path: Optional subdirectory within config_dir
        overrides: Optional dictionary of override values
        
    Returns:
        Loaded configuration as dictionary
    """
    loader = get_config_loader()
    return loader.load(None, config_path, overrides)


def x_load_config__mutmut_3(
    config_name: str,
    config_path: Optional[str] = None,
    overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to load configuration.
    
    Args:
        config_name: Name of config file (without extension)
        config_path: Optional subdirectory within config_dir
        overrides: Optional dictionary of override values
        
    Returns:
        Loaded configuration as dictionary
    """
    loader = get_config_loader()
    return loader.load(config_name, None, overrides)


def x_load_config__mutmut_4(
    config_name: str,
    config_path: Optional[str] = None,
    overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to load configuration.
    
    Args:
        config_name: Name of config file (without extension)
        config_path: Optional subdirectory within config_dir
        overrides: Optional dictionary of override values
        
    Returns:
        Loaded configuration as dictionary
    """
    loader = get_config_loader()
    return loader.load(config_name, config_path, None)


def x_load_config__mutmut_5(
    config_name: str,
    config_path: Optional[str] = None,
    overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to load configuration.
    
    Args:
        config_name: Name of config file (without extension)
        config_path: Optional subdirectory within config_dir
        overrides: Optional dictionary of override values
        
    Returns:
        Loaded configuration as dictionary
    """
    loader = get_config_loader()
    return loader.load(config_path, overrides)


def x_load_config__mutmut_6(
    config_name: str,
    config_path: Optional[str] = None,
    overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to load configuration.
    
    Args:
        config_name: Name of config file (without extension)
        config_path: Optional subdirectory within config_dir
        overrides: Optional dictionary of override values
        
    Returns:
        Loaded configuration as dictionary
    """
    loader = get_config_loader()
    return loader.load(config_name, overrides)


def x_load_config__mutmut_7(
    config_name: str,
    config_path: Optional[str] = None,
    overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to load configuration.
    
    Args:
        config_name: Name of config file (without extension)
        config_path: Optional subdirectory within config_dir
        overrides: Optional dictionary of override values
        
    Returns:
        Loaded configuration as dictionary
    """
    loader = get_config_loader()
    return loader.load(config_name, config_path, )

x_load_config__mutmut_mutants : ClassVar[MutantDict] = {
'x_load_config__mutmut_1': x_load_config__mutmut_1, 
    'x_load_config__mutmut_2': x_load_config__mutmut_2, 
    'x_load_config__mutmut_3': x_load_config__mutmut_3, 
    'x_load_config__mutmut_4': x_load_config__mutmut_4, 
    'x_load_config__mutmut_5': x_load_config__mutmut_5, 
    'x_load_config__mutmut_6': x_load_config__mutmut_6, 
    'x_load_config__mutmut_7': x_load_config__mutmut_7
}

def load_config(*args, **kwargs):
    result = _mutmut_trampoline(x_load_config__mutmut_orig, x_load_config__mutmut_mutants, args, kwargs)
    return result 

load_config.__signature__ = _mutmut_signature(x_load_config__mutmut_orig)
x_load_config__mutmut_orig.__name__ = 'x_load_config'


def x_reset_config_loader__mutmut_orig() -> None:
    """Reset global ConfigLoader instance."""
    global _config_loader
    _config_loader = None


def x_reset_config_loader__mutmut_1() -> None:
    """Reset global ConfigLoader instance."""
    global _config_loader
    _config_loader = ""

x_reset_config_loader__mutmut_mutants : ClassVar[MutantDict] = {
'x_reset_config_loader__mutmut_1': x_reset_config_loader__mutmut_1
}

def reset_config_loader(*args, **kwargs):
    result = _mutmut_trampoline(x_reset_config_loader__mutmut_orig, x_reset_config_loader__mutmut_mutants, args, kwargs)
    return result 

reset_config_loader.__signature__ = _mutmut_signature(x_reset_config_loader__mutmut_orig)
x_reset_config_loader__mutmut_orig.__name__ = 'x_reset_config_loader'


# Migration helpers

def x_detect_config_sprawl__mutmut_orig() -> Dict[str, List[str]]:
    """
    Detect configuration files across all directories.
    
    Returns:
        Dictionary mapping directory names to lists of config files
    """
    results = {}
    
    for name, path in CONFIG_DIRS.items():
        if not path.exists():
            continue
        
        configs = []
        for ext in ["*.yaml", "*.yml", "*.json", "*.toml"]:
            configs.extend([str(f.relative_to(path)) for f in path.rglob(ext)])
        
        if configs:
            results[name] = sorted(configs)
    
    return results


# Migration helpers

def x_detect_config_sprawl__mutmut_1() -> Dict[str, List[str]]:
    """
    Detect configuration files across all directories.
    
    Returns:
        Dictionary mapping directory names to lists of config files
    """
    results = None
    
    for name, path in CONFIG_DIRS.items():
        if not path.exists():
            continue
        
        configs = []
        for ext in ["*.yaml", "*.yml", "*.json", "*.toml"]:
            configs.extend([str(f.relative_to(path)) for f in path.rglob(ext)])
        
        if configs:
            results[name] = sorted(configs)
    
    return results


# Migration helpers

def x_detect_config_sprawl__mutmut_2() -> Dict[str, List[str]]:
    """
    Detect configuration files across all directories.
    
    Returns:
        Dictionary mapping directory names to lists of config files
    """
    results = {}
    
    for name, path in CONFIG_DIRS.items():
        if path.exists():
            continue
        
        configs = []
        for ext in ["*.yaml", "*.yml", "*.json", "*.toml"]:
            configs.extend([str(f.relative_to(path)) for f in path.rglob(ext)])
        
        if configs:
            results[name] = sorted(configs)
    
    return results


# Migration helpers

def x_detect_config_sprawl__mutmut_3() -> Dict[str, List[str]]:
    """
    Detect configuration files across all directories.
    
    Returns:
        Dictionary mapping directory names to lists of config files
    """
    results = {}
    
    for name, path in CONFIG_DIRS.items():
        if not path.exists():
            break
        
        configs = []
        for ext in ["*.yaml", "*.yml", "*.json", "*.toml"]:
            configs.extend([str(f.relative_to(path)) for f in path.rglob(ext)])
        
        if configs:
            results[name] = sorted(configs)
    
    return results


# Migration helpers

def x_detect_config_sprawl__mutmut_4() -> Dict[str, List[str]]:
    """
    Detect configuration files across all directories.
    
    Returns:
        Dictionary mapping directory names to lists of config files
    """
    results = {}
    
    for name, path in CONFIG_DIRS.items():
        if not path.exists():
            continue
        
        configs = None
        for ext in ["*.yaml", "*.yml", "*.json", "*.toml"]:
            configs.extend([str(f.relative_to(path)) for f in path.rglob(ext)])
        
        if configs:
            results[name] = sorted(configs)
    
    return results


# Migration helpers

def x_detect_config_sprawl__mutmut_5() -> Dict[str, List[str]]:
    """
    Detect configuration files across all directories.
    
    Returns:
        Dictionary mapping directory names to lists of config files
    """
    results = {}
    
    for name, path in CONFIG_DIRS.items():
        if not path.exists():
            continue
        
        configs = []
        for ext in ["XX*.yamlXX", "*.yml", "*.json", "*.toml"]:
            configs.extend([str(f.relative_to(path)) for f in path.rglob(ext)])
        
        if configs:
            results[name] = sorted(configs)
    
    return results


# Migration helpers

def x_detect_config_sprawl__mutmut_6() -> Dict[str, List[str]]:
    """
    Detect configuration files across all directories.
    
    Returns:
        Dictionary mapping directory names to lists of config files
    """
    results = {}
    
    for name, path in CONFIG_DIRS.items():
        if not path.exists():
            continue
        
        configs = []
        for ext in ["*.YAML", "*.yml", "*.json", "*.toml"]:
            configs.extend([str(f.relative_to(path)) for f in path.rglob(ext)])
        
        if configs:
            results[name] = sorted(configs)
    
    return results


# Migration helpers

def x_detect_config_sprawl__mutmut_7() -> Dict[str, List[str]]:
    """
    Detect configuration files across all directories.
    
    Returns:
        Dictionary mapping directory names to lists of config files
    """
    results = {}
    
    for name, path in CONFIG_DIRS.items():
        if not path.exists():
            continue
        
        configs = []
        for ext in ["*.yaml", "XX*.ymlXX", "*.json", "*.toml"]:
            configs.extend([str(f.relative_to(path)) for f in path.rglob(ext)])
        
        if configs:
            results[name] = sorted(configs)
    
    return results


# Migration helpers

def x_detect_config_sprawl__mutmut_8() -> Dict[str, List[str]]:
    """
    Detect configuration files across all directories.
    
    Returns:
        Dictionary mapping directory names to lists of config files
    """
    results = {}
    
    for name, path in CONFIG_DIRS.items():
        if not path.exists():
            continue
        
        configs = []
        for ext in ["*.yaml", "*.YML", "*.json", "*.toml"]:
            configs.extend([str(f.relative_to(path)) for f in path.rglob(ext)])
        
        if configs:
            results[name] = sorted(configs)
    
    return results


# Migration helpers

def x_detect_config_sprawl__mutmut_9() -> Dict[str, List[str]]:
    """
    Detect configuration files across all directories.
    
    Returns:
        Dictionary mapping directory names to lists of config files
    """
    results = {}
    
    for name, path in CONFIG_DIRS.items():
        if not path.exists():
            continue
        
        configs = []
        for ext in ["*.yaml", "*.yml", "XX*.jsonXX", "*.toml"]:
            configs.extend([str(f.relative_to(path)) for f in path.rglob(ext)])
        
        if configs:
            results[name] = sorted(configs)
    
    return results


# Migration helpers

def x_detect_config_sprawl__mutmut_10() -> Dict[str, List[str]]:
    """
    Detect configuration files across all directories.
    
    Returns:
        Dictionary mapping directory names to lists of config files
    """
    results = {}
    
    for name, path in CONFIG_DIRS.items():
        if not path.exists():
            continue
        
        configs = []
        for ext in ["*.yaml", "*.yml", "*.JSON", "*.toml"]:
            configs.extend([str(f.relative_to(path)) for f in path.rglob(ext)])
        
        if configs:
            results[name] = sorted(configs)
    
    return results


# Migration helpers

def x_detect_config_sprawl__mutmut_11() -> Dict[str, List[str]]:
    """
    Detect configuration files across all directories.
    
    Returns:
        Dictionary mapping directory names to lists of config files
    """
    results = {}
    
    for name, path in CONFIG_DIRS.items():
        if not path.exists():
            continue
        
        configs = []
        for ext in ["*.yaml", "*.yml", "*.json", "XX*.tomlXX"]:
            configs.extend([str(f.relative_to(path)) for f in path.rglob(ext)])
        
        if configs:
            results[name] = sorted(configs)
    
    return results


# Migration helpers

def x_detect_config_sprawl__mutmut_12() -> Dict[str, List[str]]:
    """
    Detect configuration files across all directories.
    
    Returns:
        Dictionary mapping directory names to lists of config files
    """
    results = {}
    
    for name, path in CONFIG_DIRS.items():
        if not path.exists():
            continue
        
        configs = []
        for ext in ["*.yaml", "*.yml", "*.json", "*.TOML"]:
            configs.extend([str(f.relative_to(path)) for f in path.rglob(ext)])
        
        if configs:
            results[name] = sorted(configs)
    
    return results


# Migration helpers

def x_detect_config_sprawl__mutmut_13() -> Dict[str, List[str]]:
    """
    Detect configuration files across all directories.
    
    Returns:
        Dictionary mapping directory names to lists of config files
    """
    results = {}
    
    for name, path in CONFIG_DIRS.items():
        if not path.exists():
            continue
        
        configs = []
        for ext in ["*.yaml", "*.yml", "*.json", "*.toml"]:
            configs.extend(None)
        
        if configs:
            results[name] = sorted(configs)
    
    return results


# Migration helpers

def x_detect_config_sprawl__mutmut_14() -> Dict[str, List[str]]:
    """
    Detect configuration files across all directories.
    
    Returns:
        Dictionary mapping directory names to lists of config files
    """
    results = {}
    
    for name, path in CONFIG_DIRS.items():
        if not path.exists():
            continue
        
        configs = []
        for ext in ["*.yaml", "*.yml", "*.json", "*.toml"]:
            configs.extend([str(None) for f in path.rglob(ext)])
        
        if configs:
            results[name] = sorted(configs)
    
    return results


# Migration helpers

def x_detect_config_sprawl__mutmut_15() -> Dict[str, List[str]]:
    """
    Detect configuration files across all directories.
    
    Returns:
        Dictionary mapping directory names to lists of config files
    """
    results = {}
    
    for name, path in CONFIG_DIRS.items():
        if not path.exists():
            continue
        
        configs = []
        for ext in ["*.yaml", "*.yml", "*.json", "*.toml"]:
            configs.extend([str(f.relative_to(None)) for f in path.rglob(ext)])
        
        if configs:
            results[name] = sorted(configs)
    
    return results


# Migration helpers

def x_detect_config_sprawl__mutmut_16() -> Dict[str, List[str]]:
    """
    Detect configuration files across all directories.
    
    Returns:
        Dictionary mapping directory names to lists of config files
    """
    results = {}
    
    for name, path in CONFIG_DIRS.items():
        if not path.exists():
            continue
        
        configs = []
        for ext in ["*.yaml", "*.yml", "*.json", "*.toml"]:
            configs.extend([str(f.relative_to(path)) for f in path.rglob(None)])
        
        if configs:
            results[name] = sorted(configs)
    
    return results


# Migration helpers

def x_detect_config_sprawl__mutmut_17() -> Dict[str, List[str]]:
    """
    Detect configuration files across all directories.
    
    Returns:
        Dictionary mapping directory names to lists of config files
    """
    results = {}
    
    for name, path in CONFIG_DIRS.items():
        if not path.exists():
            continue
        
        configs = []
        for ext in ["*.yaml", "*.yml", "*.json", "*.toml"]:
            configs.extend([str(f.relative_to(path)) for f in path.rglob(ext)])
        
        if configs:
            results[name] = None
    
    return results


# Migration helpers

def x_detect_config_sprawl__mutmut_18() -> Dict[str, List[str]]:
    """
    Detect configuration files across all directories.
    
    Returns:
        Dictionary mapping directory names to lists of config files
    """
    results = {}
    
    for name, path in CONFIG_DIRS.items():
        if not path.exists():
            continue
        
        configs = []
        for ext in ["*.yaml", "*.yml", "*.json", "*.toml"]:
            configs.extend([str(f.relative_to(path)) for f in path.rglob(ext)])
        
        if configs:
            results[name] = sorted(None)
    
    return results

x_detect_config_sprawl__mutmut_mutants : ClassVar[MutantDict] = {
'x_detect_config_sprawl__mutmut_1': x_detect_config_sprawl__mutmut_1, 
    'x_detect_config_sprawl__mutmut_2': x_detect_config_sprawl__mutmut_2, 
    'x_detect_config_sprawl__mutmut_3': x_detect_config_sprawl__mutmut_3, 
    'x_detect_config_sprawl__mutmut_4': x_detect_config_sprawl__mutmut_4, 
    'x_detect_config_sprawl__mutmut_5': x_detect_config_sprawl__mutmut_5, 
    'x_detect_config_sprawl__mutmut_6': x_detect_config_sprawl__mutmut_6, 
    'x_detect_config_sprawl__mutmut_7': x_detect_config_sprawl__mutmut_7, 
    'x_detect_config_sprawl__mutmut_8': x_detect_config_sprawl__mutmut_8, 
    'x_detect_config_sprawl__mutmut_9': x_detect_config_sprawl__mutmut_9, 
    'x_detect_config_sprawl__mutmut_10': x_detect_config_sprawl__mutmut_10, 
    'x_detect_config_sprawl__mutmut_11': x_detect_config_sprawl__mutmut_11, 
    'x_detect_config_sprawl__mutmut_12': x_detect_config_sprawl__mutmut_12, 
    'x_detect_config_sprawl__mutmut_13': x_detect_config_sprawl__mutmut_13, 
    'x_detect_config_sprawl__mutmut_14': x_detect_config_sprawl__mutmut_14, 
    'x_detect_config_sprawl__mutmut_15': x_detect_config_sprawl__mutmut_15, 
    'x_detect_config_sprawl__mutmut_16': x_detect_config_sprawl__mutmut_16, 
    'x_detect_config_sprawl__mutmut_17': x_detect_config_sprawl__mutmut_17, 
    'x_detect_config_sprawl__mutmut_18': x_detect_config_sprawl__mutmut_18
}

def detect_config_sprawl(*args, **kwargs):
    result = _mutmut_trampoline(x_detect_config_sprawl__mutmut_orig, x_detect_config_sprawl__mutmut_mutants, args, kwargs)
    return result 

detect_config_sprawl.__signature__ = _mutmut_signature(x_detect_config_sprawl__mutmut_orig)
x_detect_config_sprawl__mutmut_orig.__name__ = 'x_detect_config_sprawl'


def x_generate_migration_report__mutmut_orig() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_1() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = None
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_2() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = None
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_3() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["XX# Configuration Sprawl Analysis\nXX"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_4() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# configuration sprawl analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_5() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# CONFIGURATION SPRAWL ANALYSIS\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_6() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(None)
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_7() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime(None)}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_8() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('XX%Y-%m-%d %H:%M:%SXX')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_9() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%y-%m-%d %h:%m:%s')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_10() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%M-%D %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_11() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(None)
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_12() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("XX## Summary\nXX")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_13() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_14() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## SUMMARY\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_15() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = None
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_16() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(None)
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_17() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(None)
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_18() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(None)
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_19() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append(None)
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_20() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("XX## Directory Breakdown\nXX")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_21() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## directory breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_22() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## DIRECTORY BREAKDOWN\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_23() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = None
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_24() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "XX✅ PrimaryXX" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_25() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_26() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ PRIMARY" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_27() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name != "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_28() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "XXprimaryXX" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_29() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "PRIMARY" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_30() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "XX⚠️ DeprecatedXX" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_31() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_32() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ DEPRECATED" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_33() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "XXdeprecatedXX" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_34() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "DEPRECATED" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_35() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" not in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_36() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "XX🔄 SecondaryXX"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_37() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_38() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 SECONDARY"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_39() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(None)
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_40() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(None)
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_41() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(None)
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_42() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append(None)
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_43() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("XX\n**Files:**\nXX")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_44() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_45() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**FILES:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_46() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:11]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_47() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(None)
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_48() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) >= 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_49() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 11:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_50() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(None)
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_51() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) + 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_52() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 11} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_53() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append(None)
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_54() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("XX\n## Recommendations\nXX")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_55() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_56() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## RECOMMENDATIONS\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_57() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append(None)
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_58() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("XX1. Migrate all configs to `conf/` (primary)\nXX")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_59() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_60() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. MIGRATE ALL CONFIGS TO `CONF/` (PRIMARY)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_61() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append(None)
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_62() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("XX2. Use `configs/` for application-specific runtime configs\nXX")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_63() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_64() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. USE `CONFIGS/` FOR APPLICATION-SPECIFIC RUNTIME CONFIGS\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_65() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append(None)
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_66() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("XX3. Archive deprecated directories to `archive/removed/`\nXX")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_67() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_68() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. ARCHIVE DEPRECATED DIRECTORIES TO `ARCHIVE/REMOVED/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_69() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append(None)
    
    return "".join(report)


def x_generate_migration_report__mutmut_70() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("XX4. Update all import statements to use `load_config()`\nXX")
    
    return "".join(report)


def x_generate_migration_report__mutmut_71() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. update all import statements to use `load_config()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_72() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. UPDATE ALL IMPORT STATEMENTS TO USE `LOAD_CONFIG()`\n")
    
    return "".join(report)


def x_generate_migration_report__mutmut_73() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "".join(None)


def x_generate_migration_report__mutmut_74() -> str:
    """
    Generate report of configuration sprawl for migration planning.
    
    Returns:
        Markdown-formatted migration report
    """
    from datetime import datetime
    
    sprawl = detect_config_sprawl()
    
    report = ["# Configuration Sprawl Analysis\n"]
    report.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("## Summary\n")
    
    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")
    
    report.append("## Directory Breakdown\n")
    
    for name, files in sprawl.items():
        status = "✅ Primary" if name == "primary" else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")
        
        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")
    
    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")
    
    return "XXXX".join(report)

x_generate_migration_report__mutmut_mutants : ClassVar[MutantDict] = {
'x_generate_migration_report__mutmut_1': x_generate_migration_report__mutmut_1, 
    'x_generate_migration_report__mutmut_2': x_generate_migration_report__mutmut_2, 
    'x_generate_migration_report__mutmut_3': x_generate_migration_report__mutmut_3, 
    'x_generate_migration_report__mutmut_4': x_generate_migration_report__mutmut_4, 
    'x_generate_migration_report__mutmut_5': x_generate_migration_report__mutmut_5, 
    'x_generate_migration_report__mutmut_6': x_generate_migration_report__mutmut_6, 
    'x_generate_migration_report__mutmut_7': x_generate_migration_report__mutmut_7, 
    'x_generate_migration_report__mutmut_8': x_generate_migration_report__mutmut_8, 
    'x_generate_migration_report__mutmut_9': x_generate_migration_report__mutmut_9, 
    'x_generate_migration_report__mutmut_10': x_generate_migration_report__mutmut_10, 
    'x_generate_migration_report__mutmut_11': x_generate_migration_report__mutmut_11, 
    'x_generate_migration_report__mutmut_12': x_generate_migration_report__mutmut_12, 
    'x_generate_migration_report__mutmut_13': x_generate_migration_report__mutmut_13, 
    'x_generate_migration_report__mutmut_14': x_generate_migration_report__mutmut_14, 
    'x_generate_migration_report__mutmut_15': x_generate_migration_report__mutmut_15, 
    'x_generate_migration_report__mutmut_16': x_generate_migration_report__mutmut_16, 
    'x_generate_migration_report__mutmut_17': x_generate_migration_report__mutmut_17, 
    'x_generate_migration_report__mutmut_18': x_generate_migration_report__mutmut_18, 
    'x_generate_migration_report__mutmut_19': x_generate_migration_report__mutmut_19, 
    'x_generate_migration_report__mutmut_20': x_generate_migration_report__mutmut_20, 
    'x_generate_migration_report__mutmut_21': x_generate_migration_report__mutmut_21, 
    'x_generate_migration_report__mutmut_22': x_generate_migration_report__mutmut_22, 
    'x_generate_migration_report__mutmut_23': x_generate_migration_report__mutmut_23, 
    'x_generate_migration_report__mutmut_24': x_generate_migration_report__mutmut_24, 
    'x_generate_migration_report__mutmut_25': x_generate_migration_report__mutmut_25, 
    'x_generate_migration_report__mutmut_26': x_generate_migration_report__mutmut_26, 
    'x_generate_migration_report__mutmut_27': x_generate_migration_report__mutmut_27, 
    'x_generate_migration_report__mutmut_28': x_generate_migration_report__mutmut_28, 
    'x_generate_migration_report__mutmut_29': x_generate_migration_report__mutmut_29, 
    'x_generate_migration_report__mutmut_30': x_generate_migration_report__mutmut_30, 
    'x_generate_migration_report__mutmut_31': x_generate_migration_report__mutmut_31, 
    'x_generate_migration_report__mutmut_32': x_generate_migration_report__mutmut_32, 
    'x_generate_migration_report__mutmut_33': x_generate_migration_report__mutmut_33, 
    'x_generate_migration_report__mutmut_34': x_generate_migration_report__mutmut_34, 
    'x_generate_migration_report__mutmut_35': x_generate_migration_report__mutmut_35, 
    'x_generate_migration_report__mutmut_36': x_generate_migration_report__mutmut_36, 
    'x_generate_migration_report__mutmut_37': x_generate_migration_report__mutmut_37, 
    'x_generate_migration_report__mutmut_38': x_generate_migration_report__mutmut_38, 
    'x_generate_migration_report__mutmut_39': x_generate_migration_report__mutmut_39, 
    'x_generate_migration_report__mutmut_40': x_generate_migration_report__mutmut_40, 
    'x_generate_migration_report__mutmut_41': x_generate_migration_report__mutmut_41, 
    'x_generate_migration_report__mutmut_42': x_generate_migration_report__mutmut_42, 
    'x_generate_migration_report__mutmut_43': x_generate_migration_report__mutmut_43, 
    'x_generate_migration_report__mutmut_44': x_generate_migration_report__mutmut_44, 
    'x_generate_migration_report__mutmut_45': x_generate_migration_report__mutmut_45, 
    'x_generate_migration_report__mutmut_46': x_generate_migration_report__mutmut_46, 
    'x_generate_migration_report__mutmut_47': x_generate_migration_report__mutmut_47, 
    'x_generate_migration_report__mutmut_48': x_generate_migration_report__mutmut_48, 
    'x_generate_migration_report__mutmut_49': x_generate_migration_report__mutmut_49, 
    'x_generate_migration_report__mutmut_50': x_generate_migration_report__mutmut_50, 
    'x_generate_migration_report__mutmut_51': x_generate_migration_report__mutmut_51, 
    'x_generate_migration_report__mutmut_52': x_generate_migration_report__mutmut_52, 
    'x_generate_migration_report__mutmut_53': x_generate_migration_report__mutmut_53, 
    'x_generate_migration_report__mutmut_54': x_generate_migration_report__mutmut_54, 
    'x_generate_migration_report__mutmut_55': x_generate_migration_report__mutmut_55, 
    'x_generate_migration_report__mutmut_56': x_generate_migration_report__mutmut_56, 
    'x_generate_migration_report__mutmut_57': x_generate_migration_report__mutmut_57, 
    'x_generate_migration_report__mutmut_58': x_generate_migration_report__mutmut_58, 
    'x_generate_migration_report__mutmut_59': x_generate_migration_report__mutmut_59, 
    'x_generate_migration_report__mutmut_60': x_generate_migration_report__mutmut_60, 
    'x_generate_migration_report__mutmut_61': x_generate_migration_report__mutmut_61, 
    'x_generate_migration_report__mutmut_62': x_generate_migration_report__mutmut_62, 
    'x_generate_migration_report__mutmut_63': x_generate_migration_report__mutmut_63, 
    'x_generate_migration_report__mutmut_64': x_generate_migration_report__mutmut_64, 
    'x_generate_migration_report__mutmut_65': x_generate_migration_report__mutmut_65, 
    'x_generate_migration_report__mutmut_66': x_generate_migration_report__mutmut_66, 
    'x_generate_migration_report__mutmut_67': x_generate_migration_report__mutmut_67, 
    'x_generate_migration_report__mutmut_68': x_generate_migration_report__mutmut_68, 
    'x_generate_migration_report__mutmut_69': x_generate_migration_report__mutmut_69, 
    'x_generate_migration_report__mutmut_70': x_generate_migration_report__mutmut_70, 
    'x_generate_migration_report__mutmut_71': x_generate_migration_report__mutmut_71, 
    'x_generate_migration_report__mutmut_72': x_generate_migration_report__mutmut_72, 
    'x_generate_migration_report__mutmut_73': x_generate_migration_report__mutmut_73, 
    'x_generate_migration_report__mutmut_74': x_generate_migration_report__mutmut_74
}

def generate_migration_report(*args, **kwargs):
    result = _mutmut_trampoline(x_generate_migration_report__mutmut_orig, x_generate_migration_report__mutmut_mutants, args, kwargs)
    return result 

generate_migration_report.__signature__ = _mutmut_signature(x_generate_migration_report__mutmut_orig)
x_generate_migration_report__mutmut_orig.__name__ = 'x_generate_migration_report'


if __name__ == "__main__":
    # Generate migration report when run as script
    print(generate_migration_report())
