"""Centralized configuration loader using Hydra Compose API.

This module provides utilities for loading and validating configuration files
using Hydra's composition API. It consolidates error handling and provides
structured error messages from conf/errors/defaults.yaml.

Key features:
- Hydra Compose API integration for dynamic config loading
- Structured error handling with YAML-based error definitions
- Schema validation support via Pydantic (optional)
- Fallback mechanisms for offline/testing environments
- Configuration override support

Usage:
    from codex.utils.config_loader import load_config, load_error_config
    
    # Load error configuration
    errors = load_error_config()
    
    # Load application configuration
    cfg = load_config(config_name="base", config_dir="conf")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Import with fallback support
try:
    from omegaconf import DictConfig, OmegaConf
    _OMEGACONF_AVAILABLE = True
except ImportError:
    logger.warning("OmegaConf not available, using dict fallback")
    DictConfig = dict  # type: ignore
    OmegaConf = None  # type: ignore
    _OMEGACONF_AVAILABLE = False

# Hydra imports with robust fallbacks
try:
    from hydra import compose, initialize_config_dir
    from hydra.errors import MissingConfigException as HydraMissingConfigException
    _HYDRA_AVAILABLE = True
except ImportError:
    logger.debug("Hydra not available, using fallback")
    compose = None  # type: ignore
    initialize_config_dir = None  # type: ignore
    HydraMissingConfigException = FileNotFoundError  # type: ignore
    _HYDRA_AVAILABLE = False

# Try to import from config_legacy as fallback
if not _HYDRA_AVAILABLE:
    try:
        from config_legacy.errors import MissingConfigException
    except ImportError:
        # Define our own if neither is available
        class MissingConfigException(FileNotFoundError):
            """Exception raised when a configuration file cannot be located."""
            def __init__(self, *, missing_cfg_file: str, message: str | None = None, **kwargs: Any) -> None:
                self.missing_cfg_file = missing_cfg_file
                resolved = message or f"Missing config file: {missing_cfg_file}"
                super().__init__(resolved)
                self.message = resolved
else:
    MissingConfigException = HydraMissingConfigException  # type: ignore
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


@dataclass
class ErrorConfig:
    """Structured error configuration."""
    code: str
    message: str
    severity: str
    resolution: str
    
    def format(self, **kwargs: Any) -> str:
        """Format error message with context."""
        return f"[{self.code}] {self.message.format(**kwargs)}"


class ConfigLoader:
    """Centralized configuration loader using Hydra Compose API."""
    
    def xǁConfigLoaderǁ__init____mutmut_orig(self, repo_root: Path | None = None) -> None:
        """Initialize the config loader.
        
        Args:
            repo_root: Root directory of the repository. If None, auto-detected.
        """
        self.repo_root = repo_root or self._find_repo_root()
        self.error_config: dict[str, Any] = {}
        self._load_error_config()
    
    def xǁConfigLoaderǁ__init____mutmut_1(self, repo_root: Path | None = None) -> None:
        """Initialize the config loader.
        
        Args:
            repo_root: Root directory of the repository. If None, auto-detected.
        """
        self.repo_root = None
        self.error_config: dict[str, Any] = {}
        self._load_error_config()
    
    def xǁConfigLoaderǁ__init____mutmut_2(self, repo_root: Path | None = None) -> None:
        """Initialize the config loader.
        
        Args:
            repo_root: Root directory of the repository. If None, auto-detected.
        """
        self.repo_root = repo_root and self._find_repo_root()
        self.error_config: dict[str, Any] = {}
        self._load_error_config()
    
    def xǁConfigLoaderǁ__init____mutmut_3(self, repo_root: Path | None = None) -> None:
        """Initialize the config loader.
        
        Args:
            repo_root: Root directory of the repository. If None, auto-detected.
        """
        self.repo_root = repo_root or self._find_repo_root()
        self.error_config: dict[str, Any] = None
        self._load_error_config()
    
    xǁConfigLoaderǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁConfigLoaderǁ__init____mutmut_1': xǁConfigLoaderǁ__init____mutmut_1, 
        'xǁConfigLoaderǁ__init____mutmut_2': xǁConfigLoaderǁ__init____mutmut_2, 
        'xǁConfigLoaderǁ__init____mutmut_3': xǁConfigLoaderǁ__init____mutmut_3
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁConfigLoaderǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁConfigLoaderǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁConfigLoaderǁ__init____mutmut_orig)
    xǁConfigLoaderǁ__init____mutmut_orig.__name__ = 'xǁConfigLoaderǁ__init__'
    
    @staticmethod
    def _find_repo_root() -> Path:
        """Find the repository root directory."""
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
                return parent
        # Fallback to parent of src
        return current.parents[3]
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_orig(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "conf" / "errors" / "defaults.yaml"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("r") as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PyYAML not available, using default error config")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_1(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = None
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("r") as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PyYAML not available, using default error config")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_2(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "conf" / "errors" * "defaults.yaml"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("r") as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PyYAML not available, using default error config")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_3(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "conf" * "errors" / "defaults.yaml"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("r") as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PyYAML not available, using default error config")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_4(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root * "conf" / "errors" / "defaults.yaml"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("r") as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PyYAML not available, using default error config")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_5(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "XXconfXX" / "errors" / "defaults.yaml"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("r") as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PyYAML not available, using default error config")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_6(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "CONF" / "errors" / "defaults.yaml"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("r") as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PyYAML not available, using default error config")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_7(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "conf" / "XXerrorsXX" / "defaults.yaml"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("r") as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PyYAML not available, using default error config")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_8(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "conf" / "ERRORS" / "defaults.yaml"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("r") as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PyYAML not available, using default error config")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_9(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "conf" / "errors" / "XXdefaults.yamlXX"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("r") as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PyYAML not available, using default error config")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_10(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "conf" / "errors" / "DEFAULTS.YAML"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("r") as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PyYAML not available, using default error config")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_11(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "conf" / "errors" / "defaults.yaml"
        if error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("r") as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PyYAML not available, using default error config")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_12(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "conf" / "errors" / "defaults.yaml"
        if not error_config_path.exists():
            logger.warning(None)
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("r") as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PyYAML not available, using default error config")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_13(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "conf" / "errors" / "defaults.yaml"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = None
            return
        
        try:
            import yaml
            with error_config_path.open("r") as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PyYAML not available, using default error config")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_14(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "conf" / "errors" / "defaults.yaml"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open(None) as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PyYAML not available, using default error config")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_15(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "conf" / "errors" / "defaults.yaml"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("XXrXX") as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PyYAML not available, using default error config")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_16(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "conf" / "errors" / "defaults.yaml"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("R") as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PyYAML not available, using default error config")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_17(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "conf" / "errors" / "defaults.yaml"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("r") as f:
                self.error_config = None
        except ImportError:
            logger.warning("PyYAML not available, using default error config")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_18(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "conf" / "errors" / "defaults.yaml"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("r") as f:
                self.error_config = yaml.safe_load(f) and {}
        except ImportError:
            logger.warning("PyYAML not available, using default error config")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_19(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "conf" / "errors" / "defaults.yaml"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("r") as f:
                self.error_config = yaml.safe_load(None) or {}
        except ImportError:
            logger.warning("PyYAML not available, using default error config")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_20(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "conf" / "errors" / "defaults.yaml"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("r") as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning(None)
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_21(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "conf" / "errors" / "defaults.yaml"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("r") as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("XXPyYAML not available, using default error configXX")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_22(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "conf" / "errors" / "defaults.yaml"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("r") as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("pyyaml not available, using default error config")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_23(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "conf" / "errors" / "defaults.yaml"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("r") as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PYYAML NOT AVAILABLE, USING DEFAULT ERROR CONFIG")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_24(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "conf" / "errors" / "defaults.yaml"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("r") as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PyYAML not available, using default error config")
            self.error_config = None
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_25(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "conf" / "errors" / "defaults.yaml"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("r") as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PyYAML not available, using default error config")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(None)
            self.error_config = self._get_default_error_config()
    
    def xǁConfigLoaderǁ_load_error_config__mutmut_26(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "conf" / "errors" / "defaults.yaml"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return
        
        try:
            import yaml
            with error_config_path.open("r") as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PyYAML not available, using default error config")
            self.error_config = self._get_default_error_config()
        except Exception as e:
            logger.warning(f"Failed to load error config: {e}")
            self.error_config = None
    
    xǁConfigLoaderǁ_load_error_config__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁConfigLoaderǁ_load_error_config__mutmut_1': xǁConfigLoaderǁ_load_error_config__mutmut_1, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_2': xǁConfigLoaderǁ_load_error_config__mutmut_2, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_3': xǁConfigLoaderǁ_load_error_config__mutmut_3, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_4': xǁConfigLoaderǁ_load_error_config__mutmut_4, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_5': xǁConfigLoaderǁ_load_error_config__mutmut_5, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_6': xǁConfigLoaderǁ_load_error_config__mutmut_6, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_7': xǁConfigLoaderǁ_load_error_config__mutmut_7, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_8': xǁConfigLoaderǁ_load_error_config__mutmut_8, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_9': xǁConfigLoaderǁ_load_error_config__mutmut_9, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_10': xǁConfigLoaderǁ_load_error_config__mutmut_10, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_11': xǁConfigLoaderǁ_load_error_config__mutmut_11, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_12': xǁConfigLoaderǁ_load_error_config__mutmut_12, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_13': xǁConfigLoaderǁ_load_error_config__mutmut_13, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_14': xǁConfigLoaderǁ_load_error_config__mutmut_14, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_15': xǁConfigLoaderǁ_load_error_config__mutmut_15, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_16': xǁConfigLoaderǁ_load_error_config__mutmut_16, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_17': xǁConfigLoaderǁ_load_error_config__mutmut_17, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_18': xǁConfigLoaderǁ_load_error_config__mutmut_18, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_19': xǁConfigLoaderǁ_load_error_config__mutmut_19, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_20': xǁConfigLoaderǁ_load_error_config__mutmut_20, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_21': xǁConfigLoaderǁ_load_error_config__mutmut_21, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_22': xǁConfigLoaderǁ_load_error_config__mutmut_22, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_23': xǁConfigLoaderǁ_load_error_config__mutmut_23, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_24': xǁConfigLoaderǁ_load_error_config__mutmut_24, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_25': xǁConfigLoaderǁ_load_error_config__mutmut_25, 
        'xǁConfigLoaderǁ_load_error_config__mutmut_26': xǁConfigLoaderǁ_load_error_config__mutmut_26
    }
    
    def _load_error_config(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁConfigLoaderǁ_load_error_config__mutmut_orig"), object.__getattribute__(self, "xǁConfigLoaderǁ_load_error_config__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _load_error_config.__signature__ = _mutmut_signature(xǁConfigLoaderǁ_load_error_config__mutmut_orig)
    xǁConfigLoaderǁ_load_error_config__mutmut_orig.__name__ = 'xǁConfigLoaderǁ_load_error_config'
    
    @staticmethod
    def _get_default_error_config() -> dict[str, Any]:
        """Get default error configuration when YAML loading fails."""
        return {
            "config_errors": {
                "missing_config": {
                    "code": "CONFIG_001",
                    "message": "Missing configuration file",
                    "severity": "error",
                    "resolution": "Ensure the configuration file exists"
                }
            },
            "defaults": {
                "log_errors": True,
                "raise_on_error": True,
                "fallback_enabled": True
            }
        }
    
    def xǁConfigLoaderǁget_error__mutmut_orig(self, category: str, error_key: str) -> ErrorConfig | None:
        """Get structured error configuration.
        
        Args:
            category: Error category (e.g., 'config_errors', 'hydra_errors')
            error_key: Specific error key within category
            
        Returns:
            ErrorConfig object or None if not found
        """
        errors = self.error_config.get(category, {})
        # Ensure errors is a dict before calling .get()
        if not isinstance(errors, dict):
            return None
        error_data = errors.get(error_key)
        if error_data and isinstance(error_data, dict):
            return ErrorConfig(**error_data)
        return None
    
    def xǁConfigLoaderǁget_error__mutmut_1(self, category: str, error_key: str) -> ErrorConfig | None:
        """Get structured error configuration.
        
        Args:
            category: Error category (e.g., 'config_errors', 'hydra_errors')
            error_key: Specific error key within category
            
        Returns:
            ErrorConfig object or None if not found
        """
        errors = None
        # Ensure errors is a dict before calling .get()
        if not isinstance(errors, dict):
            return None
        error_data = errors.get(error_key)
        if error_data and isinstance(error_data, dict):
            return ErrorConfig(**error_data)
        return None
    
    def xǁConfigLoaderǁget_error__mutmut_2(self, category: str, error_key: str) -> ErrorConfig | None:
        """Get structured error configuration.
        
        Args:
            category: Error category (e.g., 'config_errors', 'hydra_errors')
            error_key: Specific error key within category
            
        Returns:
            ErrorConfig object or None if not found
        """
        errors = self.error_config.get(None, {})
        # Ensure errors is a dict before calling .get()
        if not isinstance(errors, dict):
            return None
        error_data = errors.get(error_key)
        if error_data and isinstance(error_data, dict):
            return ErrorConfig(**error_data)
        return None
    
    def xǁConfigLoaderǁget_error__mutmut_3(self, category: str, error_key: str) -> ErrorConfig | None:
        """Get structured error configuration.
        
        Args:
            category: Error category (e.g., 'config_errors', 'hydra_errors')
            error_key: Specific error key within category
            
        Returns:
            ErrorConfig object or None if not found
        """
        errors = self.error_config.get(category, None)
        # Ensure errors is a dict before calling .get()
        if not isinstance(errors, dict):
            return None
        error_data = errors.get(error_key)
        if error_data and isinstance(error_data, dict):
            return ErrorConfig(**error_data)
        return None
    
    def xǁConfigLoaderǁget_error__mutmut_4(self, category: str, error_key: str) -> ErrorConfig | None:
        """Get structured error configuration.
        
        Args:
            category: Error category (e.g., 'config_errors', 'hydra_errors')
            error_key: Specific error key within category
            
        Returns:
            ErrorConfig object or None if not found
        """
        errors = self.error_config.get({})
        # Ensure errors is a dict before calling .get()
        if not isinstance(errors, dict):
            return None
        error_data = errors.get(error_key)
        if error_data and isinstance(error_data, dict):
            return ErrorConfig(**error_data)
        return None
    
    def xǁConfigLoaderǁget_error__mutmut_5(self, category: str, error_key: str) -> ErrorConfig | None:
        """Get structured error configuration.
        
        Args:
            category: Error category (e.g., 'config_errors', 'hydra_errors')
            error_key: Specific error key within category
            
        Returns:
            ErrorConfig object or None if not found
        """
        errors = self.error_config.get(category, )
        # Ensure errors is a dict before calling .get()
        if not isinstance(errors, dict):
            return None
        error_data = errors.get(error_key)
        if error_data and isinstance(error_data, dict):
            return ErrorConfig(**error_data)
        return None
    
    def xǁConfigLoaderǁget_error__mutmut_6(self, category: str, error_key: str) -> ErrorConfig | None:
        """Get structured error configuration.
        
        Args:
            category: Error category (e.g., 'config_errors', 'hydra_errors')
            error_key: Specific error key within category
            
        Returns:
            ErrorConfig object or None if not found
        """
        errors = self.error_config.get(category, {})
        # Ensure errors is a dict before calling .get()
        if isinstance(errors, dict):
            return None
        error_data = errors.get(error_key)
        if error_data and isinstance(error_data, dict):
            return ErrorConfig(**error_data)
        return None
    
    def xǁConfigLoaderǁget_error__mutmut_7(self, category: str, error_key: str) -> ErrorConfig | None:
        """Get structured error configuration.
        
        Args:
            category: Error category (e.g., 'config_errors', 'hydra_errors')
            error_key: Specific error key within category
            
        Returns:
            ErrorConfig object or None if not found
        """
        errors = self.error_config.get(category, {})
        # Ensure errors is a dict before calling .get()
        if not isinstance(errors, dict):
            return None
        error_data = None
        if error_data and isinstance(error_data, dict):
            return ErrorConfig(**error_data)
        return None
    
    def xǁConfigLoaderǁget_error__mutmut_8(self, category: str, error_key: str) -> ErrorConfig | None:
        """Get structured error configuration.
        
        Args:
            category: Error category (e.g., 'config_errors', 'hydra_errors')
            error_key: Specific error key within category
            
        Returns:
            ErrorConfig object or None if not found
        """
        errors = self.error_config.get(category, {})
        # Ensure errors is a dict before calling .get()
        if not isinstance(errors, dict):
            return None
        error_data = errors.get(None)
        if error_data and isinstance(error_data, dict):
            return ErrorConfig(**error_data)
        return None
    
    def xǁConfigLoaderǁget_error__mutmut_9(self, category: str, error_key: str) -> ErrorConfig | None:
        """Get structured error configuration.
        
        Args:
            category: Error category (e.g., 'config_errors', 'hydra_errors')
            error_key: Specific error key within category
            
        Returns:
            ErrorConfig object or None if not found
        """
        errors = self.error_config.get(category, {})
        # Ensure errors is a dict before calling .get()
        if not isinstance(errors, dict):
            return None
        error_data = errors.get(error_key)
        if error_data or isinstance(error_data, dict):
            return ErrorConfig(**error_data)
        return None
    
    xǁConfigLoaderǁget_error__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁConfigLoaderǁget_error__mutmut_1': xǁConfigLoaderǁget_error__mutmut_1, 
        'xǁConfigLoaderǁget_error__mutmut_2': xǁConfigLoaderǁget_error__mutmut_2, 
        'xǁConfigLoaderǁget_error__mutmut_3': xǁConfigLoaderǁget_error__mutmut_3, 
        'xǁConfigLoaderǁget_error__mutmut_4': xǁConfigLoaderǁget_error__mutmut_4, 
        'xǁConfigLoaderǁget_error__mutmut_5': xǁConfigLoaderǁget_error__mutmut_5, 
        'xǁConfigLoaderǁget_error__mutmut_6': xǁConfigLoaderǁget_error__mutmut_6, 
        'xǁConfigLoaderǁget_error__mutmut_7': xǁConfigLoaderǁget_error__mutmut_7, 
        'xǁConfigLoaderǁget_error__mutmut_8': xǁConfigLoaderǁget_error__mutmut_8, 
        'xǁConfigLoaderǁget_error__mutmut_9': xǁConfigLoaderǁget_error__mutmut_9
    }
    
    def get_error(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁConfigLoaderǁget_error__mutmut_orig"), object.__getattribute__(self, "xǁConfigLoaderǁget_error__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_error.__signature__ = _mutmut_signature(xǁConfigLoaderǁget_error__mutmut_orig)
    xǁConfigLoaderǁget_error__mutmut_orig.__name__ = 'xǁConfigLoaderǁget_error'
    
    def xǁConfigLoaderǁ_resolve_config_dir__mutmut_orig(self, config_dir: str | Path | None) -> Path:
        """Resolve config directory path with dual-path support.
        
        Args:
            config_dir: Config directory path (None, relative, or absolute)
            
        Returns:
            Resolved Path object
        """
        if config_dir is None:
            # Default to conf/ (Hydra convention), fallback to configs/
            primary = self.repo_root / "conf"
            if primary.exists():
                return primary
            return self.repo_root / "configs"
        elif not Path(config_dir).is_absolute():
            return self.repo_root / config_dir
        else:
            return Path(config_dir)
    
    def xǁConfigLoaderǁ_resolve_config_dir__mutmut_1(self, config_dir: str | Path | None) -> Path:
        """Resolve config directory path with dual-path support.
        
        Args:
            config_dir: Config directory path (None, relative, or absolute)
            
        Returns:
            Resolved Path object
        """
        if config_dir is not None:
            # Default to conf/ (Hydra convention), fallback to configs/
            primary = self.repo_root / "conf"
            if primary.exists():
                return primary
            return self.repo_root / "configs"
        elif not Path(config_dir).is_absolute():
            return self.repo_root / config_dir
        else:
            return Path(config_dir)
    
    def xǁConfigLoaderǁ_resolve_config_dir__mutmut_2(self, config_dir: str | Path | None) -> Path:
        """Resolve config directory path with dual-path support.
        
        Args:
            config_dir: Config directory path (None, relative, or absolute)
            
        Returns:
            Resolved Path object
        """
        if config_dir is None:
            # Default to conf/ (Hydra convention), fallback to configs/
            primary = None
            if primary.exists():
                return primary
            return self.repo_root / "configs"
        elif not Path(config_dir).is_absolute():
            return self.repo_root / config_dir
        else:
            return Path(config_dir)
    
    def xǁConfigLoaderǁ_resolve_config_dir__mutmut_3(self, config_dir: str | Path | None) -> Path:
        """Resolve config directory path with dual-path support.
        
        Args:
            config_dir: Config directory path (None, relative, or absolute)
            
        Returns:
            Resolved Path object
        """
        if config_dir is None:
            # Default to conf/ (Hydra convention), fallback to configs/
            primary = self.repo_root * "conf"
            if primary.exists():
                return primary
            return self.repo_root / "configs"
        elif not Path(config_dir).is_absolute():
            return self.repo_root / config_dir
        else:
            return Path(config_dir)
    
    def xǁConfigLoaderǁ_resolve_config_dir__mutmut_4(self, config_dir: str | Path | None) -> Path:
        """Resolve config directory path with dual-path support.
        
        Args:
            config_dir: Config directory path (None, relative, or absolute)
            
        Returns:
            Resolved Path object
        """
        if config_dir is None:
            # Default to conf/ (Hydra convention), fallback to configs/
            primary = self.repo_root / "XXconfXX"
            if primary.exists():
                return primary
            return self.repo_root / "configs"
        elif not Path(config_dir).is_absolute():
            return self.repo_root / config_dir
        else:
            return Path(config_dir)
    
    def xǁConfigLoaderǁ_resolve_config_dir__mutmut_5(self, config_dir: str | Path | None) -> Path:
        """Resolve config directory path with dual-path support.
        
        Args:
            config_dir: Config directory path (None, relative, or absolute)
            
        Returns:
            Resolved Path object
        """
        if config_dir is None:
            # Default to conf/ (Hydra convention), fallback to configs/
            primary = self.repo_root / "CONF"
            if primary.exists():
                return primary
            return self.repo_root / "configs"
        elif not Path(config_dir).is_absolute():
            return self.repo_root / config_dir
        else:
            return Path(config_dir)
    
    def xǁConfigLoaderǁ_resolve_config_dir__mutmut_6(self, config_dir: str | Path | None) -> Path:
        """Resolve config directory path with dual-path support.
        
        Args:
            config_dir: Config directory path (None, relative, or absolute)
            
        Returns:
            Resolved Path object
        """
        if config_dir is None:
            # Default to conf/ (Hydra convention), fallback to configs/
            primary = self.repo_root / "conf"
            if primary.exists():
                return primary
            return self.repo_root * "configs"
        elif not Path(config_dir).is_absolute():
            return self.repo_root / config_dir
        else:
            return Path(config_dir)
    
    def xǁConfigLoaderǁ_resolve_config_dir__mutmut_7(self, config_dir: str | Path | None) -> Path:
        """Resolve config directory path with dual-path support.
        
        Args:
            config_dir: Config directory path (None, relative, or absolute)
            
        Returns:
            Resolved Path object
        """
        if config_dir is None:
            # Default to conf/ (Hydra convention), fallback to configs/
            primary = self.repo_root / "conf"
            if primary.exists():
                return primary
            return self.repo_root / "XXconfigsXX"
        elif not Path(config_dir).is_absolute():
            return self.repo_root / config_dir
        else:
            return Path(config_dir)
    
    def xǁConfigLoaderǁ_resolve_config_dir__mutmut_8(self, config_dir: str | Path | None) -> Path:
        """Resolve config directory path with dual-path support.
        
        Args:
            config_dir: Config directory path (None, relative, or absolute)
            
        Returns:
            Resolved Path object
        """
        if config_dir is None:
            # Default to conf/ (Hydra convention), fallback to configs/
            primary = self.repo_root / "conf"
            if primary.exists():
                return primary
            return self.repo_root / "CONFIGS"
        elif not Path(config_dir).is_absolute():
            return self.repo_root / config_dir
        else:
            return Path(config_dir)
    
    def xǁConfigLoaderǁ_resolve_config_dir__mutmut_9(self, config_dir: str | Path | None) -> Path:
        """Resolve config directory path with dual-path support.
        
        Args:
            config_dir: Config directory path (None, relative, or absolute)
            
        Returns:
            Resolved Path object
        """
        if config_dir is None:
            # Default to conf/ (Hydra convention), fallback to configs/
            primary = self.repo_root / "conf"
            if primary.exists():
                return primary
            return self.repo_root / "configs"
        elif Path(config_dir).is_absolute():
            return self.repo_root / config_dir
        else:
            return Path(config_dir)
    
    def xǁConfigLoaderǁ_resolve_config_dir__mutmut_10(self, config_dir: str | Path | None) -> Path:
        """Resolve config directory path with dual-path support.
        
        Args:
            config_dir: Config directory path (None, relative, or absolute)
            
        Returns:
            Resolved Path object
        """
        if config_dir is None:
            # Default to conf/ (Hydra convention), fallback to configs/
            primary = self.repo_root / "conf"
            if primary.exists():
                return primary
            return self.repo_root / "configs"
        elif not Path(None).is_absolute():
            return self.repo_root / config_dir
        else:
            return Path(config_dir)
    
    def xǁConfigLoaderǁ_resolve_config_dir__mutmut_11(self, config_dir: str | Path | None) -> Path:
        """Resolve config directory path with dual-path support.
        
        Args:
            config_dir: Config directory path (None, relative, or absolute)
            
        Returns:
            Resolved Path object
        """
        if config_dir is None:
            # Default to conf/ (Hydra convention), fallback to configs/
            primary = self.repo_root / "conf"
            if primary.exists():
                return primary
            return self.repo_root / "configs"
        elif not Path(config_dir).is_absolute():
            return self.repo_root * config_dir
        else:
            return Path(config_dir)
    
    def xǁConfigLoaderǁ_resolve_config_dir__mutmut_12(self, config_dir: str | Path | None) -> Path:
        """Resolve config directory path with dual-path support.
        
        Args:
            config_dir: Config directory path (None, relative, or absolute)
            
        Returns:
            Resolved Path object
        """
        if config_dir is None:
            # Default to conf/ (Hydra convention), fallback to configs/
            primary = self.repo_root / "conf"
            if primary.exists():
                return primary
            return self.repo_root / "configs"
        elif not Path(config_dir).is_absolute():
            return self.repo_root / config_dir
        else:
            return Path(None)
    
    xǁConfigLoaderǁ_resolve_config_dir__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁConfigLoaderǁ_resolve_config_dir__mutmut_1': xǁConfigLoaderǁ_resolve_config_dir__mutmut_1, 
        'xǁConfigLoaderǁ_resolve_config_dir__mutmut_2': xǁConfigLoaderǁ_resolve_config_dir__mutmut_2, 
        'xǁConfigLoaderǁ_resolve_config_dir__mutmut_3': xǁConfigLoaderǁ_resolve_config_dir__mutmut_3, 
        'xǁConfigLoaderǁ_resolve_config_dir__mutmut_4': xǁConfigLoaderǁ_resolve_config_dir__mutmut_4, 
        'xǁConfigLoaderǁ_resolve_config_dir__mutmut_5': xǁConfigLoaderǁ_resolve_config_dir__mutmut_5, 
        'xǁConfigLoaderǁ_resolve_config_dir__mutmut_6': xǁConfigLoaderǁ_resolve_config_dir__mutmut_6, 
        'xǁConfigLoaderǁ_resolve_config_dir__mutmut_7': xǁConfigLoaderǁ_resolve_config_dir__mutmut_7, 
        'xǁConfigLoaderǁ_resolve_config_dir__mutmut_8': xǁConfigLoaderǁ_resolve_config_dir__mutmut_8, 
        'xǁConfigLoaderǁ_resolve_config_dir__mutmut_9': xǁConfigLoaderǁ_resolve_config_dir__mutmut_9, 
        'xǁConfigLoaderǁ_resolve_config_dir__mutmut_10': xǁConfigLoaderǁ_resolve_config_dir__mutmut_10, 
        'xǁConfigLoaderǁ_resolve_config_dir__mutmut_11': xǁConfigLoaderǁ_resolve_config_dir__mutmut_11, 
        'xǁConfigLoaderǁ_resolve_config_dir__mutmut_12': xǁConfigLoaderǁ_resolve_config_dir__mutmut_12
    }
    
    def _resolve_config_dir(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁConfigLoaderǁ_resolve_config_dir__mutmut_orig"), object.__getattribute__(self, "xǁConfigLoaderǁ_resolve_config_dir__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _resolve_config_dir.__signature__ = _mutmut_signature(xǁConfigLoaderǁ_resolve_config_dir__mutmut_orig)
    xǁConfigLoaderǁ_resolve_config_dir__mutmut_orig.__name__ = 'xǁConfigLoaderǁ_resolve_config_dir'
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_orig(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_1(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" and "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_2(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name != "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_3(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "XXconfXX" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_4(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "CONF" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_5(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "XXconfXX" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_6(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "CONF" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_7(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" not in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_8(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(None):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_9(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = None
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_10(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(None) if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_11(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root * "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_12(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "XXconfXX") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_13(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "CONF") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_14(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root * "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_15(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "XXconfXX") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_16(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "CONF") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_17(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") not in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_18(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(None)
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_19(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path("XX.XX")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_20(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = None
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_21(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf * f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_22(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" * relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_23(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root * "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_24(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "XXconfigsXX" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_25(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "CONFIGS" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_26(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf * f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_27(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" * relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_28(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" * "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_29(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root * "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_30(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "XXconfigsXX" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_31(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "CONFIGS" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_32(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "XXtrainingXX" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_33(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "TRAINING" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_34(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" * f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_35(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root * "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_36(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "XXconfigsXX" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_37(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "CONFIGS" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate
        
        return None
    
    def xǁConfigLoaderǁ_try_legacy_path__mutmut_38(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.
        
        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked
            
        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = primary_dir.relative_to(self.repo_root / "conf") if (self.repo_root / "conf") in primary_dir.parents else Path(".")
            
            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]
            
            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(None)
                    return candidate
        
        return None
    
    xǁConfigLoaderǁ_try_legacy_path__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁConfigLoaderǁ_try_legacy_path__mutmut_1': xǁConfigLoaderǁ_try_legacy_path__mutmut_1, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_2': xǁConfigLoaderǁ_try_legacy_path__mutmut_2, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_3': xǁConfigLoaderǁ_try_legacy_path__mutmut_3, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_4': xǁConfigLoaderǁ_try_legacy_path__mutmut_4, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_5': xǁConfigLoaderǁ_try_legacy_path__mutmut_5, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_6': xǁConfigLoaderǁ_try_legacy_path__mutmut_6, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_7': xǁConfigLoaderǁ_try_legacy_path__mutmut_7, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_8': xǁConfigLoaderǁ_try_legacy_path__mutmut_8, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_9': xǁConfigLoaderǁ_try_legacy_path__mutmut_9, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_10': xǁConfigLoaderǁ_try_legacy_path__mutmut_10, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_11': xǁConfigLoaderǁ_try_legacy_path__mutmut_11, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_12': xǁConfigLoaderǁ_try_legacy_path__mutmut_12, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_13': xǁConfigLoaderǁ_try_legacy_path__mutmut_13, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_14': xǁConfigLoaderǁ_try_legacy_path__mutmut_14, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_15': xǁConfigLoaderǁ_try_legacy_path__mutmut_15, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_16': xǁConfigLoaderǁ_try_legacy_path__mutmut_16, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_17': xǁConfigLoaderǁ_try_legacy_path__mutmut_17, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_18': xǁConfigLoaderǁ_try_legacy_path__mutmut_18, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_19': xǁConfigLoaderǁ_try_legacy_path__mutmut_19, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_20': xǁConfigLoaderǁ_try_legacy_path__mutmut_20, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_21': xǁConfigLoaderǁ_try_legacy_path__mutmut_21, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_22': xǁConfigLoaderǁ_try_legacy_path__mutmut_22, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_23': xǁConfigLoaderǁ_try_legacy_path__mutmut_23, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_24': xǁConfigLoaderǁ_try_legacy_path__mutmut_24, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_25': xǁConfigLoaderǁ_try_legacy_path__mutmut_25, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_26': xǁConfigLoaderǁ_try_legacy_path__mutmut_26, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_27': xǁConfigLoaderǁ_try_legacy_path__mutmut_27, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_28': xǁConfigLoaderǁ_try_legacy_path__mutmut_28, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_29': xǁConfigLoaderǁ_try_legacy_path__mutmut_29, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_30': xǁConfigLoaderǁ_try_legacy_path__mutmut_30, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_31': xǁConfigLoaderǁ_try_legacy_path__mutmut_31, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_32': xǁConfigLoaderǁ_try_legacy_path__mutmut_32, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_33': xǁConfigLoaderǁ_try_legacy_path__mutmut_33, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_34': xǁConfigLoaderǁ_try_legacy_path__mutmut_34, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_35': xǁConfigLoaderǁ_try_legacy_path__mutmut_35, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_36': xǁConfigLoaderǁ_try_legacy_path__mutmut_36, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_37': xǁConfigLoaderǁ_try_legacy_path__mutmut_37, 
        'xǁConfigLoaderǁ_try_legacy_path__mutmut_38': xǁConfigLoaderǁ_try_legacy_path__mutmut_38
    }
    
    def _try_legacy_path(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁConfigLoaderǁ_try_legacy_path__mutmut_orig"), object.__getattribute__(self, "xǁConfigLoaderǁ_try_legacy_path__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _try_legacy_path.__signature__ = _mutmut_signature(xǁConfigLoaderǁ_try_legacy_path__mutmut_orig)
    xǁConfigLoaderǁ_try_legacy_path__mutmut_orig.__name__ = 'xǁConfigLoaderǁ_try_legacy_path'
    
    def xǁConfigLoaderǁload_config__mutmut_orig(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_1(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = False
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_2(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = None
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_3(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides and []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_4(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = None
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_5(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(None)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_6(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = None
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_7(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir * f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_8(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() or allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_9(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_10(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = None
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_11(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(None, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_12(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, None)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_13(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_14(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, )
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_15(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(None)
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_16(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = None
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_17(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = None
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_18(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() or config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_19(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE or config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_20(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=None):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_21(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_22(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, ):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_23(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(None)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_24(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = None
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_25(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=None, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_26(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=None)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_27(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_28(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, )
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_29(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = None
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_30(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(None, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_31(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=None)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_32(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_33(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, )
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_34(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=False)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_35(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(None)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_36(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(None)
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_37(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_38(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open(None) as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_39(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("XXrXX") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_40(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("R") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_41(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = None
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_42(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) and {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_43(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(None) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_44(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = None
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_45(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(None, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_46(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, None)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_47(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_48(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, )
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_49(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE or OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_50(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(None)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_51(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error(None)
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_52(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("XXPyYAML required for config loadingXX")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_53(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("pyyaml required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_54(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PYYAML REQUIRED FOR CONFIG LOADING")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_55(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_56(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(None)
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_57(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_58(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_59(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = None
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_60(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error(None, "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_61(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", None)
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_62(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_63(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", )
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_64(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("XXconfig_errorsXX", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_65(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("CONFIG_ERRORS", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_66(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "XXmissing_configXX")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_67(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "MISSING_CONFIG")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_68(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = None
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_69(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=None,
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_70(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=None
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_71(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_72(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_73(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(None),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_74(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(None)
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_75(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE or OmegaConf:
            return OmegaConf.create({})
        return {}
    
    def xǁConfigLoaderǁload_config__mutmut_76(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found
            
        Returns:
            DictConfig (or dict if OmegaConf unavailable)
            
        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []
        
        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"
        
        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent
        
        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)
                
                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except Exception as e:
                logger.warning(f"Hydra compose failed: {e}")
                if not allow_fallback:
                    raise
        
        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml
                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}
                
                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)
                
                if _OMEGACONF_AVAILABLE and OmegaConf:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                if not allow_fallback:
                    raise
        
        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(
                missing_cfg_file=str(config_file),
                message=msg
            )
        
        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf:
            return OmegaConf.create(None)
        return {}
    
    xǁConfigLoaderǁload_config__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁConfigLoaderǁload_config__mutmut_1': xǁConfigLoaderǁload_config__mutmut_1, 
        'xǁConfigLoaderǁload_config__mutmut_2': xǁConfigLoaderǁload_config__mutmut_2, 
        'xǁConfigLoaderǁload_config__mutmut_3': xǁConfigLoaderǁload_config__mutmut_3, 
        'xǁConfigLoaderǁload_config__mutmut_4': xǁConfigLoaderǁload_config__mutmut_4, 
        'xǁConfigLoaderǁload_config__mutmut_5': xǁConfigLoaderǁload_config__mutmut_5, 
        'xǁConfigLoaderǁload_config__mutmut_6': xǁConfigLoaderǁload_config__mutmut_6, 
        'xǁConfigLoaderǁload_config__mutmut_7': xǁConfigLoaderǁload_config__mutmut_7, 
        'xǁConfigLoaderǁload_config__mutmut_8': xǁConfigLoaderǁload_config__mutmut_8, 
        'xǁConfigLoaderǁload_config__mutmut_9': xǁConfigLoaderǁload_config__mutmut_9, 
        'xǁConfigLoaderǁload_config__mutmut_10': xǁConfigLoaderǁload_config__mutmut_10, 
        'xǁConfigLoaderǁload_config__mutmut_11': xǁConfigLoaderǁload_config__mutmut_11, 
        'xǁConfigLoaderǁload_config__mutmut_12': xǁConfigLoaderǁload_config__mutmut_12, 
        'xǁConfigLoaderǁload_config__mutmut_13': xǁConfigLoaderǁload_config__mutmut_13, 
        'xǁConfigLoaderǁload_config__mutmut_14': xǁConfigLoaderǁload_config__mutmut_14, 
        'xǁConfigLoaderǁload_config__mutmut_15': xǁConfigLoaderǁload_config__mutmut_15, 
        'xǁConfigLoaderǁload_config__mutmut_16': xǁConfigLoaderǁload_config__mutmut_16, 
        'xǁConfigLoaderǁload_config__mutmut_17': xǁConfigLoaderǁload_config__mutmut_17, 
        'xǁConfigLoaderǁload_config__mutmut_18': xǁConfigLoaderǁload_config__mutmut_18, 
        'xǁConfigLoaderǁload_config__mutmut_19': xǁConfigLoaderǁload_config__mutmut_19, 
        'xǁConfigLoaderǁload_config__mutmut_20': xǁConfigLoaderǁload_config__mutmut_20, 
        'xǁConfigLoaderǁload_config__mutmut_21': xǁConfigLoaderǁload_config__mutmut_21, 
        'xǁConfigLoaderǁload_config__mutmut_22': xǁConfigLoaderǁload_config__mutmut_22, 
        'xǁConfigLoaderǁload_config__mutmut_23': xǁConfigLoaderǁload_config__mutmut_23, 
        'xǁConfigLoaderǁload_config__mutmut_24': xǁConfigLoaderǁload_config__mutmut_24, 
        'xǁConfigLoaderǁload_config__mutmut_25': xǁConfigLoaderǁload_config__mutmut_25, 
        'xǁConfigLoaderǁload_config__mutmut_26': xǁConfigLoaderǁload_config__mutmut_26, 
        'xǁConfigLoaderǁload_config__mutmut_27': xǁConfigLoaderǁload_config__mutmut_27, 
        'xǁConfigLoaderǁload_config__mutmut_28': xǁConfigLoaderǁload_config__mutmut_28, 
        'xǁConfigLoaderǁload_config__mutmut_29': xǁConfigLoaderǁload_config__mutmut_29, 
        'xǁConfigLoaderǁload_config__mutmut_30': xǁConfigLoaderǁload_config__mutmut_30, 
        'xǁConfigLoaderǁload_config__mutmut_31': xǁConfigLoaderǁload_config__mutmut_31, 
        'xǁConfigLoaderǁload_config__mutmut_32': xǁConfigLoaderǁload_config__mutmut_32, 
        'xǁConfigLoaderǁload_config__mutmut_33': xǁConfigLoaderǁload_config__mutmut_33, 
        'xǁConfigLoaderǁload_config__mutmut_34': xǁConfigLoaderǁload_config__mutmut_34, 
        'xǁConfigLoaderǁload_config__mutmut_35': xǁConfigLoaderǁload_config__mutmut_35, 
        'xǁConfigLoaderǁload_config__mutmut_36': xǁConfigLoaderǁload_config__mutmut_36, 
        'xǁConfigLoaderǁload_config__mutmut_37': xǁConfigLoaderǁload_config__mutmut_37, 
        'xǁConfigLoaderǁload_config__mutmut_38': xǁConfigLoaderǁload_config__mutmut_38, 
        'xǁConfigLoaderǁload_config__mutmut_39': xǁConfigLoaderǁload_config__mutmut_39, 
        'xǁConfigLoaderǁload_config__mutmut_40': xǁConfigLoaderǁload_config__mutmut_40, 
        'xǁConfigLoaderǁload_config__mutmut_41': xǁConfigLoaderǁload_config__mutmut_41, 
        'xǁConfigLoaderǁload_config__mutmut_42': xǁConfigLoaderǁload_config__mutmut_42, 
        'xǁConfigLoaderǁload_config__mutmut_43': xǁConfigLoaderǁload_config__mutmut_43, 
        'xǁConfigLoaderǁload_config__mutmut_44': xǁConfigLoaderǁload_config__mutmut_44, 
        'xǁConfigLoaderǁload_config__mutmut_45': xǁConfigLoaderǁload_config__mutmut_45, 
        'xǁConfigLoaderǁload_config__mutmut_46': xǁConfigLoaderǁload_config__mutmut_46, 
        'xǁConfigLoaderǁload_config__mutmut_47': xǁConfigLoaderǁload_config__mutmut_47, 
        'xǁConfigLoaderǁload_config__mutmut_48': xǁConfigLoaderǁload_config__mutmut_48, 
        'xǁConfigLoaderǁload_config__mutmut_49': xǁConfigLoaderǁload_config__mutmut_49, 
        'xǁConfigLoaderǁload_config__mutmut_50': xǁConfigLoaderǁload_config__mutmut_50, 
        'xǁConfigLoaderǁload_config__mutmut_51': xǁConfigLoaderǁload_config__mutmut_51, 
        'xǁConfigLoaderǁload_config__mutmut_52': xǁConfigLoaderǁload_config__mutmut_52, 
        'xǁConfigLoaderǁload_config__mutmut_53': xǁConfigLoaderǁload_config__mutmut_53, 
        'xǁConfigLoaderǁload_config__mutmut_54': xǁConfigLoaderǁload_config__mutmut_54, 
        'xǁConfigLoaderǁload_config__mutmut_55': xǁConfigLoaderǁload_config__mutmut_55, 
        'xǁConfigLoaderǁload_config__mutmut_56': xǁConfigLoaderǁload_config__mutmut_56, 
        'xǁConfigLoaderǁload_config__mutmut_57': xǁConfigLoaderǁload_config__mutmut_57, 
        'xǁConfigLoaderǁload_config__mutmut_58': xǁConfigLoaderǁload_config__mutmut_58, 
        'xǁConfigLoaderǁload_config__mutmut_59': xǁConfigLoaderǁload_config__mutmut_59, 
        'xǁConfigLoaderǁload_config__mutmut_60': xǁConfigLoaderǁload_config__mutmut_60, 
        'xǁConfigLoaderǁload_config__mutmut_61': xǁConfigLoaderǁload_config__mutmut_61, 
        'xǁConfigLoaderǁload_config__mutmut_62': xǁConfigLoaderǁload_config__mutmut_62, 
        'xǁConfigLoaderǁload_config__mutmut_63': xǁConfigLoaderǁload_config__mutmut_63, 
        'xǁConfigLoaderǁload_config__mutmut_64': xǁConfigLoaderǁload_config__mutmut_64, 
        'xǁConfigLoaderǁload_config__mutmut_65': xǁConfigLoaderǁload_config__mutmut_65, 
        'xǁConfigLoaderǁload_config__mutmut_66': xǁConfigLoaderǁload_config__mutmut_66, 
        'xǁConfigLoaderǁload_config__mutmut_67': xǁConfigLoaderǁload_config__mutmut_67, 
        'xǁConfigLoaderǁload_config__mutmut_68': xǁConfigLoaderǁload_config__mutmut_68, 
        'xǁConfigLoaderǁload_config__mutmut_69': xǁConfigLoaderǁload_config__mutmut_69, 
        'xǁConfigLoaderǁload_config__mutmut_70': xǁConfigLoaderǁload_config__mutmut_70, 
        'xǁConfigLoaderǁload_config__mutmut_71': xǁConfigLoaderǁload_config__mutmut_71, 
        'xǁConfigLoaderǁload_config__mutmut_72': xǁConfigLoaderǁload_config__mutmut_72, 
        'xǁConfigLoaderǁload_config__mutmut_73': xǁConfigLoaderǁload_config__mutmut_73, 
        'xǁConfigLoaderǁload_config__mutmut_74': xǁConfigLoaderǁload_config__mutmut_74, 
        'xǁConfigLoaderǁload_config__mutmut_75': xǁConfigLoaderǁload_config__mutmut_75, 
        'xǁConfigLoaderǁload_config__mutmut_76': xǁConfigLoaderǁload_config__mutmut_76
    }
    
    def load_config(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁConfigLoaderǁload_config__mutmut_orig"), object.__getattribute__(self, "xǁConfigLoaderǁload_config__mutmut_mutants"), args, kwargs, self)
        return result 
    
    load_config.__signature__ = _mutmut_signature(xǁConfigLoaderǁload_config__mutmut_orig)
    xǁConfigLoaderǁload_config__mutmut_orig.__name__ = 'xǁConfigLoaderǁload_config'
    
    @staticmethod
    def _apply_overrides(data: dict[str, Any], overrides: list[str]) -> dict[str, Any]:
        """Apply dotlist overrides to configuration dictionary.
        
        Args:
            data: Configuration dictionary
            overrides: List of override strings (e.g., ["key.subkey=value"])
            
        Returns:
            Modified configuration dictionary
        """
        for override in overrides:
            if "=" not in override:
                continue
            
            key_path, value_str = override.split("=", 1)
            keys = key_path.split(".")
            
            # Parse value
            try:
                import yaml
                value = yaml.safe_load(value_str)
            except Exception:
                value = value_str
            
            # Navigate and set value
            current = data
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            current[keys[-1]] = value
        
        return data


# Global loader instance
_global_loader: ConfigLoader | None = None


def x_get_loader__mutmut_orig() -> ConfigLoader:
    """Get or create global ConfigLoader instance."""
    global _global_loader
    if _global_loader is None:
        _global_loader = ConfigLoader()
    return _global_loader


def x_get_loader__mutmut_1() -> ConfigLoader:
    """Get or create global ConfigLoader instance."""
    global _global_loader
    if _global_loader is not None:
        _global_loader = ConfigLoader()
    return _global_loader


def x_get_loader__mutmut_2() -> ConfigLoader:
    """Get or create global ConfigLoader instance."""
    global _global_loader
    if _global_loader is None:
        _global_loader = None
    return _global_loader

x_get_loader__mutmut_mutants : ClassVar[MutantDict] = {
'x_get_loader__mutmut_1': x_get_loader__mutmut_1, 
    'x_get_loader__mutmut_2': x_get_loader__mutmut_2
}

def get_loader(*args, **kwargs):
    result = _mutmut_trampoline(x_get_loader__mutmut_orig, x_get_loader__mutmut_mutants, args, kwargs)
    return result 

get_loader.__signature__ = _mutmut_signature(x_get_loader__mutmut_orig)
x_get_loader__mutmut_orig.__name__ = 'x_get_loader'


def x_load_config__mutmut_orig(
    config_name: str,
    config_dir: str | Path | None = None,
    overrides: list[str] | None = None,
    allow_fallback: bool = True
) -> DictConfig | dict[str, Any]:
    """Load configuration using global loader.
    
    Args:
        config_name: Name of config file (without .yaml extension)
        config_dir: Directory containing config files
        overrides: List of config overrides
        allow_fallback: Whether to use fallback when config not found
        
    Returns:
        Configuration object
    """
    loader = get_loader()
    return loader.load_config(config_name, config_dir, overrides, allow_fallback)


def x_load_config__mutmut_1(
    config_name: str,
    config_dir: str | Path | None = None,
    overrides: list[str] | None = None,
    allow_fallback: bool = False
) -> DictConfig | dict[str, Any]:
    """Load configuration using global loader.
    
    Args:
        config_name: Name of config file (without .yaml extension)
        config_dir: Directory containing config files
        overrides: List of config overrides
        allow_fallback: Whether to use fallback when config not found
        
    Returns:
        Configuration object
    """
    loader = get_loader()
    return loader.load_config(config_name, config_dir, overrides, allow_fallback)


def x_load_config__mutmut_2(
    config_name: str,
    config_dir: str | Path | None = None,
    overrides: list[str] | None = None,
    allow_fallback: bool = True
) -> DictConfig | dict[str, Any]:
    """Load configuration using global loader.
    
    Args:
        config_name: Name of config file (without .yaml extension)
        config_dir: Directory containing config files
        overrides: List of config overrides
        allow_fallback: Whether to use fallback when config not found
        
    Returns:
        Configuration object
    """
    loader = None
    return loader.load_config(config_name, config_dir, overrides, allow_fallback)


def x_load_config__mutmut_3(
    config_name: str,
    config_dir: str | Path | None = None,
    overrides: list[str] | None = None,
    allow_fallback: bool = True
) -> DictConfig | dict[str, Any]:
    """Load configuration using global loader.
    
    Args:
        config_name: Name of config file (without .yaml extension)
        config_dir: Directory containing config files
        overrides: List of config overrides
        allow_fallback: Whether to use fallback when config not found
        
    Returns:
        Configuration object
    """
    loader = get_loader()
    return loader.load_config(None, config_dir, overrides, allow_fallback)


def x_load_config__mutmut_4(
    config_name: str,
    config_dir: str | Path | None = None,
    overrides: list[str] | None = None,
    allow_fallback: bool = True
) -> DictConfig | dict[str, Any]:
    """Load configuration using global loader.
    
    Args:
        config_name: Name of config file (without .yaml extension)
        config_dir: Directory containing config files
        overrides: List of config overrides
        allow_fallback: Whether to use fallback when config not found
        
    Returns:
        Configuration object
    """
    loader = get_loader()
    return loader.load_config(config_name, None, overrides, allow_fallback)


def x_load_config__mutmut_5(
    config_name: str,
    config_dir: str | Path | None = None,
    overrides: list[str] | None = None,
    allow_fallback: bool = True
) -> DictConfig | dict[str, Any]:
    """Load configuration using global loader.
    
    Args:
        config_name: Name of config file (without .yaml extension)
        config_dir: Directory containing config files
        overrides: List of config overrides
        allow_fallback: Whether to use fallback when config not found
        
    Returns:
        Configuration object
    """
    loader = get_loader()
    return loader.load_config(config_name, config_dir, None, allow_fallback)


def x_load_config__mutmut_6(
    config_name: str,
    config_dir: str | Path | None = None,
    overrides: list[str] | None = None,
    allow_fallback: bool = True
) -> DictConfig | dict[str, Any]:
    """Load configuration using global loader.
    
    Args:
        config_name: Name of config file (without .yaml extension)
        config_dir: Directory containing config files
        overrides: List of config overrides
        allow_fallback: Whether to use fallback when config not found
        
    Returns:
        Configuration object
    """
    loader = get_loader()
    return loader.load_config(config_name, config_dir, overrides, None)


def x_load_config__mutmut_7(
    config_name: str,
    config_dir: str | Path | None = None,
    overrides: list[str] | None = None,
    allow_fallback: bool = True
) -> DictConfig | dict[str, Any]:
    """Load configuration using global loader.
    
    Args:
        config_name: Name of config file (without .yaml extension)
        config_dir: Directory containing config files
        overrides: List of config overrides
        allow_fallback: Whether to use fallback when config not found
        
    Returns:
        Configuration object
    """
    loader = get_loader()
    return loader.load_config(config_dir, overrides, allow_fallback)


def x_load_config__mutmut_8(
    config_name: str,
    config_dir: str | Path | None = None,
    overrides: list[str] | None = None,
    allow_fallback: bool = True
) -> DictConfig | dict[str, Any]:
    """Load configuration using global loader.
    
    Args:
        config_name: Name of config file (without .yaml extension)
        config_dir: Directory containing config files
        overrides: List of config overrides
        allow_fallback: Whether to use fallback when config not found
        
    Returns:
        Configuration object
    """
    loader = get_loader()
    return loader.load_config(config_name, overrides, allow_fallback)


def x_load_config__mutmut_9(
    config_name: str,
    config_dir: str | Path | None = None,
    overrides: list[str] | None = None,
    allow_fallback: bool = True
) -> DictConfig | dict[str, Any]:
    """Load configuration using global loader.
    
    Args:
        config_name: Name of config file (without .yaml extension)
        config_dir: Directory containing config files
        overrides: List of config overrides
        allow_fallback: Whether to use fallback when config not found
        
    Returns:
        Configuration object
    """
    loader = get_loader()
    return loader.load_config(config_name, config_dir, allow_fallback)


def x_load_config__mutmut_10(
    config_name: str,
    config_dir: str | Path | None = None,
    overrides: list[str] | None = None,
    allow_fallback: bool = True
) -> DictConfig | dict[str, Any]:
    """Load configuration using global loader.
    
    Args:
        config_name: Name of config file (without .yaml extension)
        config_dir: Directory containing config files
        overrides: List of config overrides
        allow_fallback: Whether to use fallback when config not found
        
    Returns:
        Configuration object
    """
    loader = get_loader()
    return loader.load_config(config_name, config_dir, overrides, )

x_load_config__mutmut_mutants : ClassVar[MutantDict] = {
'x_load_config__mutmut_1': x_load_config__mutmut_1, 
    'x_load_config__mutmut_2': x_load_config__mutmut_2, 
    'x_load_config__mutmut_3': x_load_config__mutmut_3, 
    'x_load_config__mutmut_4': x_load_config__mutmut_4, 
    'x_load_config__mutmut_5': x_load_config__mutmut_5, 
    'x_load_config__mutmut_6': x_load_config__mutmut_6, 
    'x_load_config__mutmut_7': x_load_config__mutmut_7, 
    'x_load_config__mutmut_8': x_load_config__mutmut_8, 
    'x_load_config__mutmut_9': x_load_config__mutmut_9, 
    'x_load_config__mutmut_10': x_load_config__mutmut_10
}

def load_config(*args, **kwargs):
    result = _mutmut_trampoline(x_load_config__mutmut_orig, x_load_config__mutmut_mutants, args, kwargs)
    return result 

load_config.__signature__ = _mutmut_signature(x_load_config__mutmut_orig)
x_load_config__mutmut_orig.__name__ = 'x_load_config'


def x_load_error_config__mutmut_orig() -> dict[str, Any]:
    """Load error configuration.
    
    Returns:
        Error configuration dictionary
    """
    loader = get_loader()
    return loader.error_config


def x_load_error_config__mutmut_1() -> dict[str, Any]:
    """Load error configuration.
    
    Returns:
        Error configuration dictionary
    """
    loader = None
    return loader.error_config

x_load_error_config__mutmut_mutants : ClassVar[MutantDict] = {
'x_load_error_config__mutmut_1': x_load_error_config__mutmut_1
}

def load_error_config(*args, **kwargs):
    result = _mutmut_trampoline(x_load_error_config__mutmut_orig, x_load_error_config__mutmut_mutants, args, kwargs)
    return result 

load_error_config.__signature__ = _mutmut_signature(x_load_error_config__mutmut_orig)
x_load_error_config__mutmut_orig.__name__ = 'x_load_error_config'


__all__ = [
    "ConfigLoader",
    "ErrorConfig",
    "MissingConfigException",
    "load_config",
    "load_error_config",
    "get_loader",
]
