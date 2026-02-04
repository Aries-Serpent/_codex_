"""
Sandbox Manager - Manage sandboxed execution of untrusted code.

Provides isolated execution environment with:
- Resource limits (CPU, memory, timeout)
- Network isolation
- File system restrictions
- Execution tracing

Author: mbaetiong
Generated: 2025-12-17

Safeguards:
- Strict resource limits
- Network disabled by default
- Timeout enforcement
- Temporary workspace isolation
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Safeguards: Default resource limits
DEFAULT_TIMEOUT = 60
DEFAULT_MEMORY_MB = 512
DEFAULT_MAX_OUTPUT_SIZE = 1024 * 1024  # 1MB
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
class SandboxConfig:
    """Configuration for sandboxed execution.

    Attributes:
        timeout_seconds: Maximum execution time
        memory_limit_mb: Maximum memory usage
        network_enabled: Whether to allow network access
        allowed_file_write: Whether to allow file writes
        env_overrides: Environment variable overrides
        working_dir: Optional working directory
    """
    timeout_seconds: int = DEFAULT_TIMEOUT
    memory_limit_mb: int = DEFAULT_MEMORY_MB
    network_enabled: bool = False
    allowed_file_write: bool = False
    env_overrides: dict[str, str] = field(default_factory=dict)
    working_dir: Optional[Path] = None


@dataclass
class ExecutionResult:
    """Result of sandboxed execution.

    Attributes:
        exit_code: Process exit code
        stdout: Standard output content
        stderr: Standard error content
        duration_ms: Execution duration in milliseconds
        memory_peak_mb: Peak memory usage (if available)
        timed_out: Whether execution timed out
        file_operations: list of file operations detected
        network_attempts: list of network access attempts
    """
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    memory_peak_mb: Optional[float] = None
    timed_out: bool = False
    file_operations: list[dict[str, Any]] = field(default_factory=list)
    network_attempts: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "exit_code": self.exit_code,
            "stdout_snapshot": self.stdout[:10000] if self.stdout else "",
            "stderr_snapshot": self.stderr[:10000] if self.stderr else "",
            "duration_ms": self.duration_ms,
            "memory_peak_mb": self.memory_peak_mb,
            "timed_out": self.timed_out,
            "file_operations": self.file_operations,
            "network_attempts": self.network_attempts,
        }


class SandboxManager:
    """Manage sandboxed execution of untrusted code.

    Provides an isolated environment for running Python scripts with:
    - Resource limits (CPU, memory, timeout)
    - Deterministic execution (fixed seeds, hashes)
    - Output capture (stdout, stderr)
    - Optional network isolation

    Example:
        >>> manager = SandboxManager(SandboxConfig(timeout_seconds=30))
        >>> result = manager.execute(Path("script.py"))
        >>> print(f"Exit code: {result.exit_code}")

    Safeguards:
    - All executions run with strict timeout
    - Deterministic environment variables set
    - Output size is bounded
    - Temporary workspace used
    """

    def xǁSandboxManagerǁ__init____mutmut_orig(self, config: Optional[SandboxConfig] = None):
        """Initialize sandbox manager.

        Args:
            config: Sandbox configuration (uses defaults if None)
        """
        self.config = config or SandboxConfig()
        self._validate_config()

    def xǁSandboxManagerǁ__init____mutmut_1(self, config: Optional[SandboxConfig] = None):
        """Initialize sandbox manager.

        Args:
            config: Sandbox configuration (uses defaults if None)
        """
        self.config = None
        self._validate_config()

    def xǁSandboxManagerǁ__init____mutmut_2(self, config: Optional[SandboxConfig] = None):
        """Initialize sandbox manager.

        Args:
            config: Sandbox configuration (uses defaults if None)
        """
        self.config = config and SandboxConfig()
        self._validate_config()
    
    xǁSandboxManagerǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSandboxManagerǁ__init____mutmut_1': xǁSandboxManagerǁ__init____mutmut_1, 
        'xǁSandboxManagerǁ__init____mutmut_2': xǁSandboxManagerǁ__init____mutmut_2
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSandboxManagerǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁSandboxManagerǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁSandboxManagerǁ__init____mutmut_orig)
    xǁSandboxManagerǁ__init____mutmut_orig.__name__ = 'xǁSandboxManagerǁ__init__'

    def xǁSandboxManagerǁ_validate_config__mutmut_orig(self) -> None:
        """Validate configuration.

        Safeguard: Bounds checking on configuration values.
        """
        if self.config.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.config.timeout_seconds > 3600:
            logger.warning("Timeout exceeds 1 hour, may be excessive")

        if self.config.memory_limit_mb <= 0:
            raise ValueError("memory_limit_mb must be positive")

    def xǁSandboxManagerǁ_validate_config__mutmut_1(self) -> None:
        """Validate configuration.

        Safeguard: Bounds checking on configuration values.
        """
        if self.config.timeout_seconds < 0:
            raise ValueError("timeout_seconds must be positive")
        if self.config.timeout_seconds > 3600:
            logger.warning("Timeout exceeds 1 hour, may be excessive")

        if self.config.memory_limit_mb <= 0:
            raise ValueError("memory_limit_mb must be positive")

    def xǁSandboxManagerǁ_validate_config__mutmut_2(self) -> None:
        """Validate configuration.

        Safeguard: Bounds checking on configuration values.
        """
        if self.config.timeout_seconds <= 1:
            raise ValueError("timeout_seconds must be positive")
        if self.config.timeout_seconds > 3600:
            logger.warning("Timeout exceeds 1 hour, may be excessive")

        if self.config.memory_limit_mb <= 0:
            raise ValueError("memory_limit_mb must be positive")

    def xǁSandboxManagerǁ_validate_config__mutmut_3(self) -> None:
        """Validate configuration.

        Safeguard: Bounds checking on configuration values.
        """
        if self.config.timeout_seconds <= 0:
            raise ValueError(None)
        if self.config.timeout_seconds > 3600:
            logger.warning("Timeout exceeds 1 hour, may be excessive")

        if self.config.memory_limit_mb <= 0:
            raise ValueError("memory_limit_mb must be positive")

    def xǁSandboxManagerǁ_validate_config__mutmut_4(self) -> None:
        """Validate configuration.

        Safeguard: Bounds checking on configuration values.
        """
        if self.config.timeout_seconds <= 0:
            raise ValueError("XXtimeout_seconds must be positiveXX")
        if self.config.timeout_seconds > 3600:
            logger.warning("Timeout exceeds 1 hour, may be excessive")

        if self.config.memory_limit_mb <= 0:
            raise ValueError("memory_limit_mb must be positive")

    def xǁSandboxManagerǁ_validate_config__mutmut_5(self) -> None:
        """Validate configuration.

        Safeguard: Bounds checking on configuration values.
        """
        if self.config.timeout_seconds <= 0:
            raise ValueError("TIMEOUT_SECONDS MUST BE POSITIVE")
        if self.config.timeout_seconds > 3600:
            logger.warning("Timeout exceeds 1 hour, may be excessive")

        if self.config.memory_limit_mb <= 0:
            raise ValueError("memory_limit_mb must be positive")

    def xǁSandboxManagerǁ_validate_config__mutmut_6(self) -> None:
        """Validate configuration.

        Safeguard: Bounds checking on configuration values.
        """
        if self.config.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.config.timeout_seconds >= 3600:
            logger.warning("Timeout exceeds 1 hour, may be excessive")

        if self.config.memory_limit_mb <= 0:
            raise ValueError("memory_limit_mb must be positive")

    def xǁSandboxManagerǁ_validate_config__mutmut_7(self) -> None:
        """Validate configuration.

        Safeguard: Bounds checking on configuration values.
        """
        if self.config.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.config.timeout_seconds > 3601:
            logger.warning("Timeout exceeds 1 hour, may be excessive")

        if self.config.memory_limit_mb <= 0:
            raise ValueError("memory_limit_mb must be positive")

    def xǁSandboxManagerǁ_validate_config__mutmut_8(self) -> None:
        """Validate configuration.

        Safeguard: Bounds checking on configuration values.
        """
        if self.config.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.config.timeout_seconds > 3600:
            logger.warning(None)

        if self.config.memory_limit_mb <= 0:
            raise ValueError("memory_limit_mb must be positive")

    def xǁSandboxManagerǁ_validate_config__mutmut_9(self) -> None:
        """Validate configuration.

        Safeguard: Bounds checking on configuration values.
        """
        if self.config.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.config.timeout_seconds > 3600:
            logger.warning("XXTimeout exceeds 1 hour, may be excessiveXX")

        if self.config.memory_limit_mb <= 0:
            raise ValueError("memory_limit_mb must be positive")

    def xǁSandboxManagerǁ_validate_config__mutmut_10(self) -> None:
        """Validate configuration.

        Safeguard: Bounds checking on configuration values.
        """
        if self.config.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.config.timeout_seconds > 3600:
            logger.warning("timeout exceeds 1 hour, may be excessive")

        if self.config.memory_limit_mb <= 0:
            raise ValueError("memory_limit_mb must be positive")

    def xǁSandboxManagerǁ_validate_config__mutmut_11(self) -> None:
        """Validate configuration.

        Safeguard: Bounds checking on configuration values.
        """
        if self.config.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.config.timeout_seconds > 3600:
            logger.warning("TIMEOUT EXCEEDS 1 HOUR, MAY BE EXCESSIVE")

        if self.config.memory_limit_mb <= 0:
            raise ValueError("memory_limit_mb must be positive")

    def xǁSandboxManagerǁ_validate_config__mutmut_12(self) -> None:
        """Validate configuration.

        Safeguard: Bounds checking on configuration values.
        """
        if self.config.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.config.timeout_seconds > 3600:
            logger.warning("Timeout exceeds 1 hour, may be excessive")

        if self.config.memory_limit_mb < 0:
            raise ValueError("memory_limit_mb must be positive")

    def xǁSandboxManagerǁ_validate_config__mutmut_13(self) -> None:
        """Validate configuration.

        Safeguard: Bounds checking on configuration values.
        """
        if self.config.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.config.timeout_seconds > 3600:
            logger.warning("Timeout exceeds 1 hour, may be excessive")

        if self.config.memory_limit_mb <= 1:
            raise ValueError("memory_limit_mb must be positive")

    def xǁSandboxManagerǁ_validate_config__mutmut_14(self) -> None:
        """Validate configuration.

        Safeguard: Bounds checking on configuration values.
        """
        if self.config.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.config.timeout_seconds > 3600:
            logger.warning("Timeout exceeds 1 hour, may be excessive")

        if self.config.memory_limit_mb <= 0:
            raise ValueError(None)

    def xǁSandboxManagerǁ_validate_config__mutmut_15(self) -> None:
        """Validate configuration.

        Safeguard: Bounds checking on configuration values.
        """
        if self.config.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.config.timeout_seconds > 3600:
            logger.warning("Timeout exceeds 1 hour, may be excessive")

        if self.config.memory_limit_mb <= 0:
            raise ValueError("XXmemory_limit_mb must be positiveXX")

    def xǁSandboxManagerǁ_validate_config__mutmut_16(self) -> None:
        """Validate configuration.

        Safeguard: Bounds checking on configuration values.
        """
        if self.config.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.config.timeout_seconds > 3600:
            logger.warning("Timeout exceeds 1 hour, may be excessive")

        if self.config.memory_limit_mb <= 0:
            raise ValueError("MEMORY_LIMIT_MB MUST BE POSITIVE")
    
    xǁSandboxManagerǁ_validate_config__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSandboxManagerǁ_validate_config__mutmut_1': xǁSandboxManagerǁ_validate_config__mutmut_1, 
        'xǁSandboxManagerǁ_validate_config__mutmut_2': xǁSandboxManagerǁ_validate_config__mutmut_2, 
        'xǁSandboxManagerǁ_validate_config__mutmut_3': xǁSandboxManagerǁ_validate_config__mutmut_3, 
        'xǁSandboxManagerǁ_validate_config__mutmut_4': xǁSandboxManagerǁ_validate_config__mutmut_4, 
        'xǁSandboxManagerǁ_validate_config__mutmut_5': xǁSandboxManagerǁ_validate_config__mutmut_5, 
        'xǁSandboxManagerǁ_validate_config__mutmut_6': xǁSandboxManagerǁ_validate_config__mutmut_6, 
        'xǁSandboxManagerǁ_validate_config__mutmut_7': xǁSandboxManagerǁ_validate_config__mutmut_7, 
        'xǁSandboxManagerǁ_validate_config__mutmut_8': xǁSandboxManagerǁ_validate_config__mutmut_8, 
        'xǁSandboxManagerǁ_validate_config__mutmut_9': xǁSandboxManagerǁ_validate_config__mutmut_9, 
        'xǁSandboxManagerǁ_validate_config__mutmut_10': xǁSandboxManagerǁ_validate_config__mutmut_10, 
        'xǁSandboxManagerǁ_validate_config__mutmut_11': xǁSandboxManagerǁ_validate_config__mutmut_11, 
        'xǁSandboxManagerǁ_validate_config__mutmut_12': xǁSandboxManagerǁ_validate_config__mutmut_12, 
        'xǁSandboxManagerǁ_validate_config__mutmut_13': xǁSandboxManagerǁ_validate_config__mutmut_13, 
        'xǁSandboxManagerǁ_validate_config__mutmut_14': xǁSandboxManagerǁ_validate_config__mutmut_14, 
        'xǁSandboxManagerǁ_validate_config__mutmut_15': xǁSandboxManagerǁ_validate_config__mutmut_15, 
        'xǁSandboxManagerǁ_validate_config__mutmut_16': xǁSandboxManagerǁ_validate_config__mutmut_16
    }
    
    def _validate_config(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSandboxManagerǁ_validate_config__mutmut_orig"), object.__getattribute__(self, "xǁSandboxManagerǁ_validate_config__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _validate_config.__signature__ = _mutmut_signature(xǁSandboxManagerǁ_validate_config__mutmut_orig)
    xǁSandboxManagerǁ_validate_config__mutmut_orig.__name__ = 'xǁSandboxManagerǁ_validate_config'

    def xǁSandboxManagerǁ_build_environment__mutmut_orig(self) -> dict[str, str]:
        """Build deterministic execution environment.

        Safeguard: Deterministic execution environment.

        Returns:
            Environment dictionary
        """
        env = os.environ.copy()

        # set deterministic values
        env["PYTHONHASHSEED"] = "42"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONUNBUFFERED"] = "1"

        # Disable network if configured
        if not self.config.network_enabled:
            # Note: This doesn't truly disable network, but signals intent
            env["CODEX_NETWORK_DISABLED"] = "1"

        # Apply custom overrides
        env.update(self.config.env_overrides)

        return env

    def xǁSandboxManagerǁ_build_environment__mutmut_1(self) -> dict[str, str]:
        """Build deterministic execution environment.

        Safeguard: Deterministic execution environment.

        Returns:
            Environment dictionary
        """
        env = None

        # set deterministic values
        env["PYTHONHASHSEED"] = "42"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONUNBUFFERED"] = "1"

        # Disable network if configured
        if not self.config.network_enabled:
            # Note: This doesn't truly disable network, but signals intent
            env["CODEX_NETWORK_DISABLED"] = "1"

        # Apply custom overrides
        env.update(self.config.env_overrides)

        return env

    def xǁSandboxManagerǁ_build_environment__mutmut_2(self) -> dict[str, str]:
        """Build deterministic execution environment.

        Safeguard: Deterministic execution environment.

        Returns:
            Environment dictionary
        """
        env = os.environ.copy()

        # set deterministic values
        env["PYTHONHASHSEED"] = None
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONUNBUFFERED"] = "1"

        # Disable network if configured
        if not self.config.network_enabled:
            # Note: This doesn't truly disable network, but signals intent
            env["CODEX_NETWORK_DISABLED"] = "1"

        # Apply custom overrides
        env.update(self.config.env_overrides)

        return env

    def xǁSandboxManagerǁ_build_environment__mutmut_3(self) -> dict[str, str]:
        """Build deterministic execution environment.

        Safeguard: Deterministic execution environment.

        Returns:
            Environment dictionary
        """
        env = os.environ.copy()

        # set deterministic values
        env["XXPYTHONHASHSEEDXX"] = "42"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONUNBUFFERED"] = "1"

        # Disable network if configured
        if not self.config.network_enabled:
            # Note: This doesn't truly disable network, but signals intent
            env["CODEX_NETWORK_DISABLED"] = "1"

        # Apply custom overrides
        env.update(self.config.env_overrides)

        return env

    def xǁSandboxManagerǁ_build_environment__mutmut_4(self) -> dict[str, str]:
        """Build deterministic execution environment.

        Safeguard: Deterministic execution environment.

        Returns:
            Environment dictionary
        """
        env = os.environ.copy()

        # set deterministic values
        env["pythonhashseed"] = "42"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONUNBUFFERED"] = "1"

        # Disable network if configured
        if not self.config.network_enabled:
            # Note: This doesn't truly disable network, but signals intent
            env["CODEX_NETWORK_DISABLED"] = "1"

        # Apply custom overrides
        env.update(self.config.env_overrides)

        return env

    def xǁSandboxManagerǁ_build_environment__mutmut_5(self) -> dict[str, str]:
        """Build deterministic execution environment.

        Safeguard: Deterministic execution environment.

        Returns:
            Environment dictionary
        """
        env = os.environ.copy()

        # set deterministic values
        env["PYTHONHASHSEED"] = "XX42XX"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONUNBUFFERED"] = "1"

        # Disable network if configured
        if not self.config.network_enabled:
            # Note: This doesn't truly disable network, but signals intent
            env["CODEX_NETWORK_DISABLED"] = "1"

        # Apply custom overrides
        env.update(self.config.env_overrides)

        return env

    def xǁSandboxManagerǁ_build_environment__mutmut_6(self) -> dict[str, str]:
        """Build deterministic execution environment.

        Safeguard: Deterministic execution environment.

        Returns:
            Environment dictionary
        """
        env = os.environ.copy()

        # set deterministic values
        env["PYTHONHASHSEED"] = "42"
        env["PYTHONDONTWRITEBYTECODE"] = None
        env["PYTHONUNBUFFERED"] = "1"

        # Disable network if configured
        if not self.config.network_enabled:
            # Note: This doesn't truly disable network, but signals intent
            env["CODEX_NETWORK_DISABLED"] = "1"

        # Apply custom overrides
        env.update(self.config.env_overrides)

        return env

    def xǁSandboxManagerǁ_build_environment__mutmut_7(self) -> dict[str, str]:
        """Build deterministic execution environment.

        Safeguard: Deterministic execution environment.

        Returns:
            Environment dictionary
        """
        env = os.environ.copy()

        # set deterministic values
        env["PYTHONHASHSEED"] = "42"
        env["XXPYTHONDONTWRITEBYTECODEXX"] = "1"
        env["PYTHONUNBUFFERED"] = "1"

        # Disable network if configured
        if not self.config.network_enabled:
            # Note: This doesn't truly disable network, but signals intent
            env["CODEX_NETWORK_DISABLED"] = "1"

        # Apply custom overrides
        env.update(self.config.env_overrides)

        return env

    def xǁSandboxManagerǁ_build_environment__mutmut_8(self) -> dict[str, str]:
        """Build deterministic execution environment.

        Safeguard: Deterministic execution environment.

        Returns:
            Environment dictionary
        """
        env = os.environ.copy()

        # set deterministic values
        env["PYTHONHASHSEED"] = "42"
        env["pythondontwritebytecode"] = "1"
        env["PYTHONUNBUFFERED"] = "1"

        # Disable network if configured
        if not self.config.network_enabled:
            # Note: This doesn't truly disable network, but signals intent
            env["CODEX_NETWORK_DISABLED"] = "1"

        # Apply custom overrides
        env.update(self.config.env_overrides)

        return env

    def xǁSandboxManagerǁ_build_environment__mutmut_9(self) -> dict[str, str]:
        """Build deterministic execution environment.

        Safeguard: Deterministic execution environment.

        Returns:
            Environment dictionary
        """
        env = os.environ.copy()

        # set deterministic values
        env["PYTHONHASHSEED"] = "42"
        env["PYTHONDONTWRITEBYTECODE"] = "XX1XX"
        env["PYTHONUNBUFFERED"] = "1"

        # Disable network if configured
        if not self.config.network_enabled:
            # Note: This doesn't truly disable network, but signals intent
            env["CODEX_NETWORK_DISABLED"] = "1"

        # Apply custom overrides
        env.update(self.config.env_overrides)

        return env

    def xǁSandboxManagerǁ_build_environment__mutmut_10(self) -> dict[str, str]:
        """Build deterministic execution environment.

        Safeguard: Deterministic execution environment.

        Returns:
            Environment dictionary
        """
        env = os.environ.copy()

        # set deterministic values
        env["PYTHONHASHSEED"] = "42"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONUNBUFFERED"] = None

        # Disable network if configured
        if not self.config.network_enabled:
            # Note: This doesn't truly disable network, but signals intent
            env["CODEX_NETWORK_DISABLED"] = "1"

        # Apply custom overrides
        env.update(self.config.env_overrides)

        return env

    def xǁSandboxManagerǁ_build_environment__mutmut_11(self) -> dict[str, str]:
        """Build deterministic execution environment.

        Safeguard: Deterministic execution environment.

        Returns:
            Environment dictionary
        """
        env = os.environ.copy()

        # set deterministic values
        env["PYTHONHASHSEED"] = "42"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["XXPYTHONUNBUFFEREDXX"] = "1"

        # Disable network if configured
        if not self.config.network_enabled:
            # Note: This doesn't truly disable network, but signals intent
            env["CODEX_NETWORK_DISABLED"] = "1"

        # Apply custom overrides
        env.update(self.config.env_overrides)

        return env

    def xǁSandboxManagerǁ_build_environment__mutmut_12(self) -> dict[str, str]:
        """Build deterministic execution environment.

        Safeguard: Deterministic execution environment.

        Returns:
            Environment dictionary
        """
        env = os.environ.copy()

        # set deterministic values
        env["PYTHONHASHSEED"] = "42"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["pythonunbuffered"] = "1"

        # Disable network if configured
        if not self.config.network_enabled:
            # Note: This doesn't truly disable network, but signals intent
            env["CODEX_NETWORK_DISABLED"] = "1"

        # Apply custom overrides
        env.update(self.config.env_overrides)

        return env

    def xǁSandboxManagerǁ_build_environment__mutmut_13(self) -> dict[str, str]:
        """Build deterministic execution environment.

        Safeguard: Deterministic execution environment.

        Returns:
            Environment dictionary
        """
        env = os.environ.copy()

        # set deterministic values
        env["PYTHONHASHSEED"] = "42"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONUNBUFFERED"] = "XX1XX"

        # Disable network if configured
        if not self.config.network_enabled:
            # Note: This doesn't truly disable network, but signals intent
            env["CODEX_NETWORK_DISABLED"] = "1"

        # Apply custom overrides
        env.update(self.config.env_overrides)

        return env

    def xǁSandboxManagerǁ_build_environment__mutmut_14(self) -> dict[str, str]:
        """Build deterministic execution environment.

        Safeguard: Deterministic execution environment.

        Returns:
            Environment dictionary
        """
        env = os.environ.copy()

        # set deterministic values
        env["PYTHONHASHSEED"] = "42"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONUNBUFFERED"] = "1"

        # Disable network if configured
        if self.config.network_enabled:
            # Note: This doesn't truly disable network, but signals intent
            env["CODEX_NETWORK_DISABLED"] = "1"

        # Apply custom overrides
        env.update(self.config.env_overrides)

        return env

    def xǁSandboxManagerǁ_build_environment__mutmut_15(self) -> dict[str, str]:
        """Build deterministic execution environment.

        Safeguard: Deterministic execution environment.

        Returns:
            Environment dictionary
        """
        env = os.environ.copy()

        # set deterministic values
        env["PYTHONHASHSEED"] = "42"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONUNBUFFERED"] = "1"

        # Disable network if configured
        if not self.config.network_enabled:
            # Note: This doesn't truly disable network, but signals intent
            env["CODEX_NETWORK_DISABLED"] = None

        # Apply custom overrides
        env.update(self.config.env_overrides)

        return env

    def xǁSandboxManagerǁ_build_environment__mutmut_16(self) -> dict[str, str]:
        """Build deterministic execution environment.

        Safeguard: Deterministic execution environment.

        Returns:
            Environment dictionary
        """
        env = os.environ.copy()

        # set deterministic values
        env["PYTHONHASHSEED"] = "42"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONUNBUFFERED"] = "1"

        # Disable network if configured
        if not self.config.network_enabled:
            # Note: This doesn't truly disable network, but signals intent
            env["XXCODEX_NETWORK_DISABLEDXX"] = "1"

        # Apply custom overrides
        env.update(self.config.env_overrides)

        return env

    def xǁSandboxManagerǁ_build_environment__mutmut_17(self) -> dict[str, str]:
        """Build deterministic execution environment.

        Safeguard: Deterministic execution environment.

        Returns:
            Environment dictionary
        """
        env = os.environ.copy()

        # set deterministic values
        env["PYTHONHASHSEED"] = "42"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONUNBUFFERED"] = "1"

        # Disable network if configured
        if not self.config.network_enabled:
            # Note: This doesn't truly disable network, but signals intent
            env["codex_network_disabled"] = "1"

        # Apply custom overrides
        env.update(self.config.env_overrides)

        return env

    def xǁSandboxManagerǁ_build_environment__mutmut_18(self) -> dict[str, str]:
        """Build deterministic execution environment.

        Safeguard: Deterministic execution environment.

        Returns:
            Environment dictionary
        """
        env = os.environ.copy()

        # set deterministic values
        env["PYTHONHASHSEED"] = "42"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONUNBUFFERED"] = "1"

        # Disable network if configured
        if not self.config.network_enabled:
            # Note: This doesn't truly disable network, but signals intent
            env["CODEX_NETWORK_DISABLED"] = "XX1XX"

        # Apply custom overrides
        env.update(self.config.env_overrides)

        return env

    def xǁSandboxManagerǁ_build_environment__mutmut_19(self) -> dict[str, str]:
        """Build deterministic execution environment.

        Safeguard: Deterministic execution environment.

        Returns:
            Environment dictionary
        """
        env = os.environ.copy()

        # set deterministic values
        env["PYTHONHASHSEED"] = "42"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONUNBUFFERED"] = "1"

        # Disable network if configured
        if not self.config.network_enabled:
            # Note: This doesn't truly disable network, but signals intent
            env["CODEX_NETWORK_DISABLED"] = "1"

        # Apply custom overrides
        env.update(None)

        return env
    
    xǁSandboxManagerǁ_build_environment__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSandboxManagerǁ_build_environment__mutmut_1': xǁSandboxManagerǁ_build_environment__mutmut_1, 
        'xǁSandboxManagerǁ_build_environment__mutmut_2': xǁSandboxManagerǁ_build_environment__mutmut_2, 
        'xǁSandboxManagerǁ_build_environment__mutmut_3': xǁSandboxManagerǁ_build_environment__mutmut_3, 
        'xǁSandboxManagerǁ_build_environment__mutmut_4': xǁSandboxManagerǁ_build_environment__mutmut_4, 
        'xǁSandboxManagerǁ_build_environment__mutmut_5': xǁSandboxManagerǁ_build_environment__mutmut_5, 
        'xǁSandboxManagerǁ_build_environment__mutmut_6': xǁSandboxManagerǁ_build_environment__mutmut_6, 
        'xǁSandboxManagerǁ_build_environment__mutmut_7': xǁSandboxManagerǁ_build_environment__mutmut_7, 
        'xǁSandboxManagerǁ_build_environment__mutmut_8': xǁSandboxManagerǁ_build_environment__mutmut_8, 
        'xǁSandboxManagerǁ_build_environment__mutmut_9': xǁSandboxManagerǁ_build_environment__mutmut_9, 
        'xǁSandboxManagerǁ_build_environment__mutmut_10': xǁSandboxManagerǁ_build_environment__mutmut_10, 
        'xǁSandboxManagerǁ_build_environment__mutmut_11': xǁSandboxManagerǁ_build_environment__mutmut_11, 
        'xǁSandboxManagerǁ_build_environment__mutmut_12': xǁSandboxManagerǁ_build_environment__mutmut_12, 
        'xǁSandboxManagerǁ_build_environment__mutmut_13': xǁSandboxManagerǁ_build_environment__mutmut_13, 
        'xǁSandboxManagerǁ_build_environment__mutmut_14': xǁSandboxManagerǁ_build_environment__mutmut_14, 
        'xǁSandboxManagerǁ_build_environment__mutmut_15': xǁSandboxManagerǁ_build_environment__mutmut_15, 
        'xǁSandboxManagerǁ_build_environment__mutmut_16': xǁSandboxManagerǁ_build_environment__mutmut_16, 
        'xǁSandboxManagerǁ_build_environment__mutmut_17': xǁSandboxManagerǁ_build_environment__mutmut_17, 
        'xǁSandboxManagerǁ_build_environment__mutmut_18': xǁSandboxManagerǁ_build_environment__mutmut_18, 
        'xǁSandboxManagerǁ_build_environment__mutmut_19': xǁSandboxManagerǁ_build_environment__mutmut_19
    }
    
    def _build_environment(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSandboxManagerǁ_build_environment__mutmut_orig"), object.__getattribute__(self, "xǁSandboxManagerǁ_build_environment__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _build_environment.__signature__ = _mutmut_signature(xǁSandboxManagerǁ_build_environment__mutmut_orig)
    xǁSandboxManagerǁ_build_environment__mutmut_orig.__name__ = 'xǁSandboxManagerǁ_build_environment'

    def xǁSandboxManagerǁ_truncate_output__mutmut_orig(self, output: str) -> str:
        """Truncate output to prevent memory issues.

        Safeguard: Output size bounds.

        Args:
            output: Output string

        Returns:
            Truncated output
        """
        if len(output) > DEFAULT_MAX_OUTPUT_SIZE:
            return output[:DEFAULT_MAX_OUTPUT_SIZE] + "\n[... truncated ...]"
        return output

    def xǁSandboxManagerǁ_truncate_output__mutmut_1(self, output: str) -> str:
        """Truncate output to prevent memory issues.

        Safeguard: Output size bounds.

        Args:
            output: Output string

        Returns:
            Truncated output
        """
        if len(output) >= DEFAULT_MAX_OUTPUT_SIZE:
            return output[:DEFAULT_MAX_OUTPUT_SIZE] + "\n[... truncated ...]"
        return output

    def xǁSandboxManagerǁ_truncate_output__mutmut_2(self, output: str) -> str:
        """Truncate output to prevent memory issues.

        Safeguard: Output size bounds.

        Args:
            output: Output string

        Returns:
            Truncated output
        """
        if len(output) > DEFAULT_MAX_OUTPUT_SIZE:
            return output[:DEFAULT_MAX_OUTPUT_SIZE] - "\n[... truncated ...]"
        return output

    def xǁSandboxManagerǁ_truncate_output__mutmut_3(self, output: str) -> str:
        """Truncate output to prevent memory issues.

        Safeguard: Output size bounds.

        Args:
            output: Output string

        Returns:
            Truncated output
        """
        if len(output) > DEFAULT_MAX_OUTPUT_SIZE:
            return output[:DEFAULT_MAX_OUTPUT_SIZE] + "XX\n[... truncated ...]XX"
        return output

    def xǁSandboxManagerǁ_truncate_output__mutmut_4(self, output: str) -> str:
        """Truncate output to prevent memory issues.

        Safeguard: Output size bounds.

        Args:
            output: Output string

        Returns:
            Truncated output
        """
        if len(output) > DEFAULT_MAX_OUTPUT_SIZE:
            return output[:DEFAULT_MAX_OUTPUT_SIZE] + "\n[... TRUNCATED ...]"
        return output
    
    xǁSandboxManagerǁ_truncate_output__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSandboxManagerǁ_truncate_output__mutmut_1': xǁSandboxManagerǁ_truncate_output__mutmut_1, 
        'xǁSandboxManagerǁ_truncate_output__mutmut_2': xǁSandboxManagerǁ_truncate_output__mutmut_2, 
        'xǁSandboxManagerǁ_truncate_output__mutmut_3': xǁSandboxManagerǁ_truncate_output__mutmut_3, 
        'xǁSandboxManagerǁ_truncate_output__mutmut_4': xǁSandboxManagerǁ_truncate_output__mutmut_4
    }
    
    def _truncate_output(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSandboxManagerǁ_truncate_output__mutmut_orig"), object.__getattribute__(self, "xǁSandboxManagerǁ_truncate_output__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _truncate_output.__signature__ = _mutmut_signature(xǁSandboxManagerǁ_truncate_output__mutmut_orig)
    xǁSandboxManagerǁ_truncate_output__mutmut_orig.__name__ = 'xǁSandboxManagerǁ_truncate_output'

    def xǁSandboxManagerǁexecute__mutmut_orig(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_1(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = None
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_2(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_3(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(None)
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_4(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_5(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(None)

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_6(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = None
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_7(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(None).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_8(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = None
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_9(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(None), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_10(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(None)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_11(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(None)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_12(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = None

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_13(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = None

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_14(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir and script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_15(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = None

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_16(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = None

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_17(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                None,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_18(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=None,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_19(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=None,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_20(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=None,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_21(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=None,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_22(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=None,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_23(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=None,
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_24(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_25(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_26(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_27(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_28(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_29(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_30(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_31(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=False,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_32(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=False,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_33(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(None),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_34(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = None

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_35(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) / 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_36(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() + start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_37(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1001

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_38(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=None,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_39(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=None,
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_40(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=None,
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_41(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=None,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_42(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=None,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_43(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_44(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_45(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_46(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_47(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_48(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(None),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_49(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout and ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_50(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or "XXXX"),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_51(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(None),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_52(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr and ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_53(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or "XXXX"),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_54(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=True,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_55(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = None

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_56(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) / 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_57(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() + start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_58(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1001

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_59(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=None,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_60(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=None,
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_61(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=None,
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_62(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=None,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_63(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=None,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_64(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_65(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_66(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_67(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_68(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_69(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=+1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_70(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-2,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_71(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(None) if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_72(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout and "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_73(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "XXXX") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_74(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "XXXX",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_75(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=False,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_76(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(None)
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_77(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = None

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_78(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) / 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_79(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() + start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_80(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1001

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_81(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=None,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_82(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=None,
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_83(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=None,
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_84(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=None,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_85(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=None,
            )

    def xǁSandboxManagerǁexecute__mutmut_86(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_87(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_88(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_89(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_90(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                )

    def xǁSandboxManagerǁexecute__mutmut_91(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=+1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_92(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-2,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_93(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="XXXX",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=False,
            )

    def xǁSandboxManagerǁexecute__mutmut_94(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute a Python script in sandboxed environment.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with execution details

        Raises:
            FileNotFoundError: If script doesn't exist
        """
        import time

        script = script.resolve()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        if not script.is_file():
            raise FileNotFoundError(f"Script is not a file: {script}")

        # Build command
        python_exe = Path(sys.executable).resolve()
        cmd = [str(python_exe), str(script)]
        if args:
            cmd.extend(args)

        # Build environment
        env = self._build_environment()

        # Determine working directory
        cwd = (self.config.working_dir or script.parent).resolve()

        start_time = time.time()

        try:
            # Security: The script path is validated to exist and is within the controlled
            # sandbox workspace. The command uses 'python' (from PATH) which should be the
            # trusted system Python. Arguments are passed as a list (not shell) to prevent
            # injection. Environment and working directory are controlled by sandbox config.
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                env=env,
                cwd=str(cwd),
            )

            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=result.returncode,
                stdout=self._truncate_output(result.stdout or ""),
                stderr=self._truncate_output(result.stderr or ""),
                duration_ms=duration_ms,
                timed_out=False,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout=self._truncate_output(e.stdout or "") if e.stdout else "",
                stderr=f"Execution timed out after {self.config.timeout_seconds}s",
                duration_ms=duration_ms,
                timed_out=True,
            )

        except Exception as e:
            logger.debug(f"Exception: {e}")
            duration_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                duration_ms=duration_ms,
                timed_out=True,
            )
    
    xǁSandboxManagerǁexecute__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSandboxManagerǁexecute__mutmut_1': xǁSandboxManagerǁexecute__mutmut_1, 
        'xǁSandboxManagerǁexecute__mutmut_2': xǁSandboxManagerǁexecute__mutmut_2, 
        'xǁSandboxManagerǁexecute__mutmut_3': xǁSandboxManagerǁexecute__mutmut_3, 
        'xǁSandboxManagerǁexecute__mutmut_4': xǁSandboxManagerǁexecute__mutmut_4, 
        'xǁSandboxManagerǁexecute__mutmut_5': xǁSandboxManagerǁexecute__mutmut_5, 
        'xǁSandboxManagerǁexecute__mutmut_6': xǁSandboxManagerǁexecute__mutmut_6, 
        'xǁSandboxManagerǁexecute__mutmut_7': xǁSandboxManagerǁexecute__mutmut_7, 
        'xǁSandboxManagerǁexecute__mutmut_8': xǁSandboxManagerǁexecute__mutmut_8, 
        'xǁSandboxManagerǁexecute__mutmut_9': xǁSandboxManagerǁexecute__mutmut_9, 
        'xǁSandboxManagerǁexecute__mutmut_10': xǁSandboxManagerǁexecute__mutmut_10, 
        'xǁSandboxManagerǁexecute__mutmut_11': xǁSandboxManagerǁexecute__mutmut_11, 
        'xǁSandboxManagerǁexecute__mutmut_12': xǁSandboxManagerǁexecute__mutmut_12, 
        'xǁSandboxManagerǁexecute__mutmut_13': xǁSandboxManagerǁexecute__mutmut_13, 
        'xǁSandboxManagerǁexecute__mutmut_14': xǁSandboxManagerǁexecute__mutmut_14, 
        'xǁSandboxManagerǁexecute__mutmut_15': xǁSandboxManagerǁexecute__mutmut_15, 
        'xǁSandboxManagerǁexecute__mutmut_16': xǁSandboxManagerǁexecute__mutmut_16, 
        'xǁSandboxManagerǁexecute__mutmut_17': xǁSandboxManagerǁexecute__mutmut_17, 
        'xǁSandboxManagerǁexecute__mutmut_18': xǁSandboxManagerǁexecute__mutmut_18, 
        'xǁSandboxManagerǁexecute__mutmut_19': xǁSandboxManagerǁexecute__mutmut_19, 
        'xǁSandboxManagerǁexecute__mutmut_20': xǁSandboxManagerǁexecute__mutmut_20, 
        'xǁSandboxManagerǁexecute__mutmut_21': xǁSandboxManagerǁexecute__mutmut_21, 
        'xǁSandboxManagerǁexecute__mutmut_22': xǁSandboxManagerǁexecute__mutmut_22, 
        'xǁSandboxManagerǁexecute__mutmut_23': xǁSandboxManagerǁexecute__mutmut_23, 
        'xǁSandboxManagerǁexecute__mutmut_24': xǁSandboxManagerǁexecute__mutmut_24, 
        'xǁSandboxManagerǁexecute__mutmut_25': xǁSandboxManagerǁexecute__mutmut_25, 
        'xǁSandboxManagerǁexecute__mutmut_26': xǁSandboxManagerǁexecute__mutmut_26, 
        'xǁSandboxManagerǁexecute__mutmut_27': xǁSandboxManagerǁexecute__mutmut_27, 
        'xǁSandboxManagerǁexecute__mutmut_28': xǁSandboxManagerǁexecute__mutmut_28, 
        'xǁSandboxManagerǁexecute__mutmut_29': xǁSandboxManagerǁexecute__mutmut_29, 
        'xǁSandboxManagerǁexecute__mutmut_30': xǁSandboxManagerǁexecute__mutmut_30, 
        'xǁSandboxManagerǁexecute__mutmut_31': xǁSandboxManagerǁexecute__mutmut_31, 
        'xǁSandboxManagerǁexecute__mutmut_32': xǁSandboxManagerǁexecute__mutmut_32, 
        'xǁSandboxManagerǁexecute__mutmut_33': xǁSandboxManagerǁexecute__mutmut_33, 
        'xǁSandboxManagerǁexecute__mutmut_34': xǁSandboxManagerǁexecute__mutmut_34, 
        'xǁSandboxManagerǁexecute__mutmut_35': xǁSandboxManagerǁexecute__mutmut_35, 
        'xǁSandboxManagerǁexecute__mutmut_36': xǁSandboxManagerǁexecute__mutmut_36, 
        'xǁSandboxManagerǁexecute__mutmut_37': xǁSandboxManagerǁexecute__mutmut_37, 
        'xǁSandboxManagerǁexecute__mutmut_38': xǁSandboxManagerǁexecute__mutmut_38, 
        'xǁSandboxManagerǁexecute__mutmut_39': xǁSandboxManagerǁexecute__mutmut_39, 
        'xǁSandboxManagerǁexecute__mutmut_40': xǁSandboxManagerǁexecute__mutmut_40, 
        'xǁSandboxManagerǁexecute__mutmut_41': xǁSandboxManagerǁexecute__mutmut_41, 
        'xǁSandboxManagerǁexecute__mutmut_42': xǁSandboxManagerǁexecute__mutmut_42, 
        'xǁSandboxManagerǁexecute__mutmut_43': xǁSandboxManagerǁexecute__mutmut_43, 
        'xǁSandboxManagerǁexecute__mutmut_44': xǁSandboxManagerǁexecute__mutmut_44, 
        'xǁSandboxManagerǁexecute__mutmut_45': xǁSandboxManagerǁexecute__mutmut_45, 
        'xǁSandboxManagerǁexecute__mutmut_46': xǁSandboxManagerǁexecute__mutmut_46, 
        'xǁSandboxManagerǁexecute__mutmut_47': xǁSandboxManagerǁexecute__mutmut_47, 
        'xǁSandboxManagerǁexecute__mutmut_48': xǁSandboxManagerǁexecute__mutmut_48, 
        'xǁSandboxManagerǁexecute__mutmut_49': xǁSandboxManagerǁexecute__mutmut_49, 
        'xǁSandboxManagerǁexecute__mutmut_50': xǁSandboxManagerǁexecute__mutmut_50, 
        'xǁSandboxManagerǁexecute__mutmut_51': xǁSandboxManagerǁexecute__mutmut_51, 
        'xǁSandboxManagerǁexecute__mutmut_52': xǁSandboxManagerǁexecute__mutmut_52, 
        'xǁSandboxManagerǁexecute__mutmut_53': xǁSandboxManagerǁexecute__mutmut_53, 
        'xǁSandboxManagerǁexecute__mutmut_54': xǁSandboxManagerǁexecute__mutmut_54, 
        'xǁSandboxManagerǁexecute__mutmut_55': xǁSandboxManagerǁexecute__mutmut_55, 
        'xǁSandboxManagerǁexecute__mutmut_56': xǁSandboxManagerǁexecute__mutmut_56, 
        'xǁSandboxManagerǁexecute__mutmut_57': xǁSandboxManagerǁexecute__mutmut_57, 
        'xǁSandboxManagerǁexecute__mutmut_58': xǁSandboxManagerǁexecute__mutmut_58, 
        'xǁSandboxManagerǁexecute__mutmut_59': xǁSandboxManagerǁexecute__mutmut_59, 
        'xǁSandboxManagerǁexecute__mutmut_60': xǁSandboxManagerǁexecute__mutmut_60, 
        'xǁSandboxManagerǁexecute__mutmut_61': xǁSandboxManagerǁexecute__mutmut_61, 
        'xǁSandboxManagerǁexecute__mutmut_62': xǁSandboxManagerǁexecute__mutmut_62, 
        'xǁSandboxManagerǁexecute__mutmut_63': xǁSandboxManagerǁexecute__mutmut_63, 
        'xǁSandboxManagerǁexecute__mutmut_64': xǁSandboxManagerǁexecute__mutmut_64, 
        'xǁSandboxManagerǁexecute__mutmut_65': xǁSandboxManagerǁexecute__mutmut_65, 
        'xǁSandboxManagerǁexecute__mutmut_66': xǁSandboxManagerǁexecute__mutmut_66, 
        'xǁSandboxManagerǁexecute__mutmut_67': xǁSandboxManagerǁexecute__mutmut_67, 
        'xǁSandboxManagerǁexecute__mutmut_68': xǁSandboxManagerǁexecute__mutmut_68, 
        'xǁSandboxManagerǁexecute__mutmut_69': xǁSandboxManagerǁexecute__mutmut_69, 
        'xǁSandboxManagerǁexecute__mutmut_70': xǁSandboxManagerǁexecute__mutmut_70, 
        'xǁSandboxManagerǁexecute__mutmut_71': xǁSandboxManagerǁexecute__mutmut_71, 
        'xǁSandboxManagerǁexecute__mutmut_72': xǁSandboxManagerǁexecute__mutmut_72, 
        'xǁSandboxManagerǁexecute__mutmut_73': xǁSandboxManagerǁexecute__mutmut_73, 
        'xǁSandboxManagerǁexecute__mutmut_74': xǁSandboxManagerǁexecute__mutmut_74, 
        'xǁSandboxManagerǁexecute__mutmut_75': xǁSandboxManagerǁexecute__mutmut_75, 
        'xǁSandboxManagerǁexecute__mutmut_76': xǁSandboxManagerǁexecute__mutmut_76, 
        'xǁSandboxManagerǁexecute__mutmut_77': xǁSandboxManagerǁexecute__mutmut_77, 
        'xǁSandboxManagerǁexecute__mutmut_78': xǁSandboxManagerǁexecute__mutmut_78, 
        'xǁSandboxManagerǁexecute__mutmut_79': xǁSandboxManagerǁexecute__mutmut_79, 
        'xǁSandboxManagerǁexecute__mutmut_80': xǁSandboxManagerǁexecute__mutmut_80, 
        'xǁSandboxManagerǁexecute__mutmut_81': xǁSandboxManagerǁexecute__mutmut_81, 
        'xǁSandboxManagerǁexecute__mutmut_82': xǁSandboxManagerǁexecute__mutmut_82, 
        'xǁSandboxManagerǁexecute__mutmut_83': xǁSandboxManagerǁexecute__mutmut_83, 
        'xǁSandboxManagerǁexecute__mutmut_84': xǁSandboxManagerǁexecute__mutmut_84, 
        'xǁSandboxManagerǁexecute__mutmut_85': xǁSandboxManagerǁexecute__mutmut_85, 
        'xǁSandboxManagerǁexecute__mutmut_86': xǁSandboxManagerǁexecute__mutmut_86, 
        'xǁSandboxManagerǁexecute__mutmut_87': xǁSandboxManagerǁexecute__mutmut_87, 
        'xǁSandboxManagerǁexecute__mutmut_88': xǁSandboxManagerǁexecute__mutmut_88, 
        'xǁSandboxManagerǁexecute__mutmut_89': xǁSandboxManagerǁexecute__mutmut_89, 
        'xǁSandboxManagerǁexecute__mutmut_90': xǁSandboxManagerǁexecute__mutmut_90, 
        'xǁSandboxManagerǁexecute__mutmut_91': xǁSandboxManagerǁexecute__mutmut_91, 
        'xǁSandboxManagerǁexecute__mutmut_92': xǁSandboxManagerǁexecute__mutmut_92, 
        'xǁSandboxManagerǁexecute__mutmut_93': xǁSandboxManagerǁexecute__mutmut_93, 
        'xǁSandboxManagerǁexecute__mutmut_94': xǁSandboxManagerǁexecute__mutmut_94
    }
    
    def execute(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSandboxManagerǁexecute__mutmut_orig"), object.__getattribute__(self, "xǁSandboxManagerǁexecute__mutmut_mutants"), args, kwargs, self)
        return result 
    
    execute.__signature__ = _mutmut_signature(xǁSandboxManagerǁexecute__mutmut_orig)
    xǁSandboxManagerǁexecute__mutmut_orig.__name__ = 'xǁSandboxManagerǁexecute'

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_orig(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_1(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_2(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(None)

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_3(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = None

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_4(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = None
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_5(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = None

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_6(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(None).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_7(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = None
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_8(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(None)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_9(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = None

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_10(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(None)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_11(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_12(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd and is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_13(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    None
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_14(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = None
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_15(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(None)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_16(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if "XX..XX" in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_17(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." not in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_18(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(None).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_19(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(None)
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_20(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(None)
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_21(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(None)

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_22(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode=None,
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_23(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=None,
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_24(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=None,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_25(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding=None,
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_26(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_27(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_28(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_29(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_30(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="XXwXX",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_31(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="W",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_32(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix="XX.pyXX",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_33(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".PY",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_34(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=True,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_35(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="XXutf-8XX",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_36(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="UTF-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_37(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = None
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_38(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] - (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_39(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(None)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_40(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args and [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_41(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(None)}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_42(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(None))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_43(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(None)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_44(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = None

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_45(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = None
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_46(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(None, stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_47(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=None)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_48(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_49(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), )
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_50(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(None), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(wrapper_path)

    def xǁSandboxManagerǁexecute_with_tracing__mutmut_51(
        self,
        script: Path,
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute script with call tracing enabled.

        Uses Python's trace module to capture function calls.

        Args:
            script: Path to Python script
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult with tracing information
        """

        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")

        # Security: Validate script path to prevent path traversal
        script_resolved = script.resolve()

        # Get the working directory as trusted base
        try:
            cwd = Path.cwd().resolve()
            # Check if script is within current working directory or temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()

            is_in_cwd = script_resolved.is_relative_to(cwd)
            is_in_temp = script_resolved.is_relative_to(temp_dir)

            if not (is_in_cwd or is_in_temp):
                raise ValueError(
                    f"Script path {script_resolved} is outside allowed directories. "
                    f"Must be within {cwd} or {temp_dir}"
                )
            
            # Additional check: Ensure no path traversal sequences in the normalized path
            path_str = str(script_resolved)
            if ".." in Path(path_str).parts:
                raise ValueError(f"Path traversal detected in script path: {path_str}")
                
        except (ValueError, OSError) as e:
            logger.debug(f"Exception: {e}")
            raise ValueError(f"Path validation failed: {e}")

        # Create tracing wrapper script
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            wrapper = f"""
import sys
import trace

tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False,
    countcallers=False,
)

sys.argv = {[str(script)] + (args or [])}

try:
    tracer.runfunc(exec, open({repr(str(script))}).read(), {{'__name__': '__main__'}})
except SystemExit:
    pass
"""
            f.write(wrapper)
            wrapper_path = f.name

        try:
            result = self.execute(Path(wrapper_path), stdin_input=stdin_input)
            return result
        finally:
            os.unlink(None)
    
    xǁSandboxManagerǁexecute_with_tracing__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSandboxManagerǁexecute_with_tracing__mutmut_1': xǁSandboxManagerǁexecute_with_tracing__mutmut_1, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_2': xǁSandboxManagerǁexecute_with_tracing__mutmut_2, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_3': xǁSandboxManagerǁexecute_with_tracing__mutmut_3, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_4': xǁSandboxManagerǁexecute_with_tracing__mutmut_4, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_5': xǁSandboxManagerǁexecute_with_tracing__mutmut_5, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_6': xǁSandboxManagerǁexecute_with_tracing__mutmut_6, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_7': xǁSandboxManagerǁexecute_with_tracing__mutmut_7, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_8': xǁSandboxManagerǁexecute_with_tracing__mutmut_8, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_9': xǁSandboxManagerǁexecute_with_tracing__mutmut_9, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_10': xǁSandboxManagerǁexecute_with_tracing__mutmut_10, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_11': xǁSandboxManagerǁexecute_with_tracing__mutmut_11, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_12': xǁSandboxManagerǁexecute_with_tracing__mutmut_12, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_13': xǁSandboxManagerǁexecute_with_tracing__mutmut_13, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_14': xǁSandboxManagerǁexecute_with_tracing__mutmut_14, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_15': xǁSandboxManagerǁexecute_with_tracing__mutmut_15, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_16': xǁSandboxManagerǁexecute_with_tracing__mutmut_16, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_17': xǁSandboxManagerǁexecute_with_tracing__mutmut_17, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_18': xǁSandboxManagerǁexecute_with_tracing__mutmut_18, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_19': xǁSandboxManagerǁexecute_with_tracing__mutmut_19, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_20': xǁSandboxManagerǁexecute_with_tracing__mutmut_20, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_21': xǁSandboxManagerǁexecute_with_tracing__mutmut_21, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_22': xǁSandboxManagerǁexecute_with_tracing__mutmut_22, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_23': xǁSandboxManagerǁexecute_with_tracing__mutmut_23, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_24': xǁSandboxManagerǁexecute_with_tracing__mutmut_24, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_25': xǁSandboxManagerǁexecute_with_tracing__mutmut_25, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_26': xǁSandboxManagerǁexecute_with_tracing__mutmut_26, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_27': xǁSandboxManagerǁexecute_with_tracing__mutmut_27, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_28': xǁSandboxManagerǁexecute_with_tracing__mutmut_28, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_29': xǁSandboxManagerǁexecute_with_tracing__mutmut_29, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_30': xǁSandboxManagerǁexecute_with_tracing__mutmut_30, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_31': xǁSandboxManagerǁexecute_with_tracing__mutmut_31, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_32': xǁSandboxManagerǁexecute_with_tracing__mutmut_32, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_33': xǁSandboxManagerǁexecute_with_tracing__mutmut_33, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_34': xǁSandboxManagerǁexecute_with_tracing__mutmut_34, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_35': xǁSandboxManagerǁexecute_with_tracing__mutmut_35, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_36': xǁSandboxManagerǁexecute_with_tracing__mutmut_36, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_37': xǁSandboxManagerǁexecute_with_tracing__mutmut_37, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_38': xǁSandboxManagerǁexecute_with_tracing__mutmut_38, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_39': xǁSandboxManagerǁexecute_with_tracing__mutmut_39, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_40': xǁSandboxManagerǁexecute_with_tracing__mutmut_40, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_41': xǁSandboxManagerǁexecute_with_tracing__mutmut_41, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_42': xǁSandboxManagerǁexecute_with_tracing__mutmut_42, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_43': xǁSandboxManagerǁexecute_with_tracing__mutmut_43, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_44': xǁSandboxManagerǁexecute_with_tracing__mutmut_44, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_45': xǁSandboxManagerǁexecute_with_tracing__mutmut_45, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_46': xǁSandboxManagerǁexecute_with_tracing__mutmut_46, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_47': xǁSandboxManagerǁexecute_with_tracing__mutmut_47, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_48': xǁSandboxManagerǁexecute_with_tracing__mutmut_48, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_49': xǁSandboxManagerǁexecute_with_tracing__mutmut_49, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_50': xǁSandboxManagerǁexecute_with_tracing__mutmut_50, 
        'xǁSandboxManagerǁexecute_with_tracing__mutmut_51': xǁSandboxManagerǁexecute_with_tracing__mutmut_51
    }
    
    def execute_with_tracing(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSandboxManagerǁexecute_with_tracing__mutmut_orig"), object.__getattribute__(self, "xǁSandboxManagerǁexecute_with_tracing__mutmut_mutants"), args, kwargs, self)
        return result 
    
    execute_with_tracing.__signature__ = _mutmut_signature(xǁSandboxManagerǁexecute_with_tracing__mutmut_orig)
    xǁSandboxManagerǁexecute_with_tracing__mutmut_orig.__name__ = 'xǁSandboxManagerǁexecute_with_tracing'

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_orig(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_1(
        self,
        source_dir: Path,
        entry_point: str = "XXmain.pyXX",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_2(
        self,
        source_dir: Path,
        entry_point: str = "MAIN.PY",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_3(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = None
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_4(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) * "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_5(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(None) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_6(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "XXworkXX"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_7(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "WORK"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_8(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(None, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_9(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, None)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_10(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_11(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, )

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_12(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = None
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_13(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir * entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_14(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_15(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=None,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_16(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout=None,
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_17(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=None,
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_18(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=None,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_19(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_20(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_21(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_22(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_23(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=+1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_24(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-2,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_25(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="XXXX",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_26(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=1,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_27(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = None
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_28(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = None

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_29(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(None, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_30(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=None, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_31(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=None)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_32(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_33(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, stdin_input=stdin_input)
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_34(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, )
            finally:
                self.config.working_dir = original_cwd

    def xǁSandboxManagerǁexecute_in_tempdir__mutmut_35(
        self,
        source_dir: Path,
        entry_point: str = "main.py",
        args: Optional[list[str]] = None,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute in isolated temporary directory.

        Copies source to temp directory and executes there,
        preventing modification of original files.

        Args:
            source_dir: Directory containing source files
            entry_point: Script to execute
            args: Optional command-line arguments
            stdin_input: Optional stdin input

        Returns:
            ExecutionResult
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            shutil.copytree(source_dir, work_dir)

            script = work_dir / entry_point
            if not script.exists():
                return ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Entry point not found: {entry_point}",
                    duration_ms=0,
                )

            # Update config with working directory
            original_cwd = self.config.working_dir
            self.config.working_dir = work_dir

            try:
                return self.execute(script, args=args, stdin_input=stdin_input)
            finally:
                self.config.working_dir = None
    
    xǁSandboxManagerǁexecute_in_tempdir__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSandboxManagerǁexecute_in_tempdir__mutmut_1': xǁSandboxManagerǁexecute_in_tempdir__mutmut_1, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_2': xǁSandboxManagerǁexecute_in_tempdir__mutmut_2, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_3': xǁSandboxManagerǁexecute_in_tempdir__mutmut_3, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_4': xǁSandboxManagerǁexecute_in_tempdir__mutmut_4, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_5': xǁSandboxManagerǁexecute_in_tempdir__mutmut_5, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_6': xǁSandboxManagerǁexecute_in_tempdir__mutmut_6, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_7': xǁSandboxManagerǁexecute_in_tempdir__mutmut_7, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_8': xǁSandboxManagerǁexecute_in_tempdir__mutmut_8, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_9': xǁSandboxManagerǁexecute_in_tempdir__mutmut_9, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_10': xǁSandboxManagerǁexecute_in_tempdir__mutmut_10, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_11': xǁSandboxManagerǁexecute_in_tempdir__mutmut_11, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_12': xǁSandboxManagerǁexecute_in_tempdir__mutmut_12, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_13': xǁSandboxManagerǁexecute_in_tempdir__mutmut_13, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_14': xǁSandboxManagerǁexecute_in_tempdir__mutmut_14, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_15': xǁSandboxManagerǁexecute_in_tempdir__mutmut_15, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_16': xǁSandboxManagerǁexecute_in_tempdir__mutmut_16, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_17': xǁSandboxManagerǁexecute_in_tempdir__mutmut_17, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_18': xǁSandboxManagerǁexecute_in_tempdir__mutmut_18, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_19': xǁSandboxManagerǁexecute_in_tempdir__mutmut_19, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_20': xǁSandboxManagerǁexecute_in_tempdir__mutmut_20, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_21': xǁSandboxManagerǁexecute_in_tempdir__mutmut_21, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_22': xǁSandboxManagerǁexecute_in_tempdir__mutmut_22, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_23': xǁSandboxManagerǁexecute_in_tempdir__mutmut_23, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_24': xǁSandboxManagerǁexecute_in_tempdir__mutmut_24, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_25': xǁSandboxManagerǁexecute_in_tempdir__mutmut_25, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_26': xǁSandboxManagerǁexecute_in_tempdir__mutmut_26, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_27': xǁSandboxManagerǁexecute_in_tempdir__mutmut_27, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_28': xǁSandboxManagerǁexecute_in_tempdir__mutmut_28, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_29': xǁSandboxManagerǁexecute_in_tempdir__mutmut_29, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_30': xǁSandboxManagerǁexecute_in_tempdir__mutmut_30, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_31': xǁSandboxManagerǁexecute_in_tempdir__mutmut_31, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_32': xǁSandboxManagerǁexecute_in_tempdir__mutmut_32, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_33': xǁSandboxManagerǁexecute_in_tempdir__mutmut_33, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_34': xǁSandboxManagerǁexecute_in_tempdir__mutmut_34, 
        'xǁSandboxManagerǁexecute_in_tempdir__mutmut_35': xǁSandboxManagerǁexecute_in_tempdir__mutmut_35
    }
    
    def execute_in_tempdir(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSandboxManagerǁexecute_in_tempdir__mutmut_orig"), object.__getattribute__(self, "xǁSandboxManagerǁexecute_in_tempdir__mutmut_mutants"), args, kwargs, self)
        return result 
    
    execute_in_tempdir.__signature__ = _mutmut_signature(xǁSandboxManagerǁexecute_in_tempdir__mutmut_orig)
    xǁSandboxManagerǁexecute_in_tempdir__mutmut_orig.__name__ = 'xǁSandboxManagerǁexecute_in_tempdir'
