"""Environment variable management with validation and defaults.

Provides:
- Type-safe environment variable access
- Default value handling
- Validation for critical variables
- Logging of environment configuration
"""

from __future__ import annotations

import os
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, TypeVar

T = TypeVar("T")

# Accept "0"/"1" (legacy) and "true"/"false" (GitHub Actions repo-variable style).
# Validators use .lower() so "True", "TRUE", "yes", "YES" etc. are all accepted.
_BOOL_STR_TRUE = frozenset(("1", "true", "yes"))
_BOOL_STR_FALSE = frozenset(("0", "false", "no"))
_BOOL_STR_VALID = _BOOL_STR_TRUE | _BOOL_STR_FALSE


@dataclass
class EnvVarConfig:
    """Configuration for a single environment variable."""

    name: str
    default: Optional[str] = None
    validator: Optional[Callable[[str], bool]] = None
    required: bool = False
    description: str = ""


class EnvironmentManager:
    """Manage environment variables with validation and logging.

    Usage:
        env = EnvironmentManager()
        session_id = env.get_session_id()
        log_dir = env.get_log_dir()
    """

    # Define all CODEX_* environment variables
    ENV_VARS = {
        "CODEX_ENV_PYTHON_VERSION": EnvVarConfig(
            name="CODEX_ENV_PYTHON_VERSION",
            default="3.12",
            description="Python version for environment setup",
        ),
        "CODEX_ENV_NODE_VERSION": EnvVarConfig(
            name="CODEX_ENV_NODE_VERSION",
            default=None,
            description="Node.js version for environment setup",
        ),
        "CODEX_ENV_RUST_VERSION": EnvVarConfig(
            name="CODEX_ENV_RUST_VERSION",
            default=None,
            description="Rust version for environment setup",
        ),
        "CODEX_ENV_GO_VERSION": EnvVarConfig(
            name="CODEX_ENV_GO_VERSION",
            default=None,
            description="Go version for environment setup",
        ),
        "CODEX_ENV_SWIFT_VERSION": EnvVarConfig(
            name="CODEX_ENV_SWIFT_VERSION",
            default=None,
            description="Swift version for environment setup",
        ),
        "CODEX_SESSION_ID": EnvVarConfig(
            name="CODEX_SESSION_ID",
            default=None,  # Generated dynamically
            description="Session identifier (UUID recommended)",
        ),
        "CODEX_SESSION_LOG_DIR": EnvVarConfig(
            name="CODEX_SESSION_LOG_DIR",
            default=".codex/sessions",
            description="Directory for session log files",
        ),
        "CODEX_LOG_DB_PATH": EnvVarConfig(
            name="CODEX_LOG_DB_PATH",
            default=".codex/session_logs.db",
            description="Path to SQLite database for logs",
        ),
        "CODEX_DB_PATH": EnvVarConfig(
            name="CODEX_DB_PATH",
            default=".codex/session_logs.db",
            description="Alternative path to SQLite database",
        ),
        "CODEX_SQLITE_POOL": EnvVarConfig(
            name="CODEX_SQLITE_POOL",
            default="0",
            validator=lambda v: v.lower() in _BOOL_STR_VALID,
            description="Enable SQLite connection pooling (0=disabled, 1=enabled)",
        ),
        "CODEX_FORCE_CPU": EnvVarConfig(
            name="CODEX_FORCE_CPU",
            default="1",
            validator=lambda v: v.lower() in _BOOL_STR_VALID,
            description="Enforce CPU-only torch installation",
        ),
        "CODEX_CPU_MINIMAL": EnvVarConfig(
            name="CODEX_CPU_MINIMAL",
            default="0",
            validator=lambda v: v.lower() in _BOOL_STR_VALID,
            description="Slim ML augmentation (lean subset)",
        ),
        "CODEX_VENDOR_PURGE": EnvVarConfig(
            name="CODEX_VENDOR_PURGE",
            default="1",
            validator=lambda v: v.lower() in _BOOL_STR_VALID,
            description="Activate purge phase (uninstall vendor wheels)",
        ),
        "CODEX_ABORT_ON_GPU_PULL": EnvVarConfig(
            name="CODEX_ABORT_ON_GPU_PULL",
            default="0",
            validator=lambda v: v.lower() in _BOOL_STR_VALID,
            description="Hard fail if GPU wheels observed",
        ),
        "CODEX_DEPENDENCY_EVIDENCE_ENABLE": EnvVarConfig(
            name="CODEX_DEPENDENCY_EVIDENCE_ENABLE",
            default="1",
            validator=lambda v: v.lower() in _BOOL_STR_VALID,
            description="Record dependency operations",
        ),
        "CODEX_COLLECT_COVERAGE": EnvVarConfig(
            name="CODEX_COLLECT_COVERAGE",
            default="0",
            validator=lambda v: v.lower() in _BOOL_STR_VALID,
            description="Enable coverage collection in tests",
        ),
    }

    def __init__(self, lazy_validation: bool = False) -> None:
        """Initialize environment manager and optionally validate.

        Args:
            lazy_validation: If True, skip validation until first use (default: False)
        """
        self._session_id: Optional[str] = None
        self._validated: bool = False
        self._lazy_validation: bool = lazy_validation

        if not lazy_validation:
            self._validate_environment()

    def _ensure_validated(self) -> None:
        """Ensure environment has been validated (for lazy validation mode)."""
        if not self._validated:
            self._validate_environment()
            self._validated = True

    def validate(self) -> None:
        """Explicitly validate environment variables.

        Can be called multiple times safely (idempotent).
        Useful for explicit validation in scripts or applications.

        Raises:
            EnvironmentError: If validation fails

        Example:
            env = EnvironmentManager(lazy_validation=True)
            # ... later
            env.validate()  # Explicit validation
        """
        self._ensure_validated()

    def _validate_environment(self) -> None:
        """Validate required environment variables."""
        errors = []
        for var_name, config in self.ENV_VARS.items():
            value = os.getenv(var_name)

            if config.required and not value:
                errors.append(f"Required environment variable {var_name} not set")

            if value and config.validator and not config.validator(value):
                errors.append(f"Invalid value for {var_name}: {value}")

        if errors:
            raise OSError("\n".join(errors))

    def get(self, var_name: str, default: Optional[str] = None) -> str:
        """Get environment variable with fallback to configured default.

        Args:
            var_name: Environment variable name
            default: Override default (if not using configured default)

        Returns:
            Environment variable value or default
        """
        self._ensure_validated()
        config = self.ENV_VARS.get(var_name)
        fallback = default if default is not None else (config.default if config else None)
        value = os.getenv(var_name, fallback)
        # Return None as-is to preserve type distinction for optional variables
        return value if value is not None else ""

    def get_session_id(self) -> str:
        """Get or generate session ID.

        Returns:
            Session ID (from env or newly generated UUID)
        """
        if self._session_id:
            return self._session_id

        self._session_id = os.getenv("CODEX_SESSION_ID")
        if not self._session_id:
            self._session_id = str(uuid.uuid4())
            os.environ["CODEX_SESSION_ID"] = self._session_id

        return self._session_id

    def get_log_dir(self) -> Path:
        """Get session log directory (creates if not exists).

        Returns:
            Path to log directory
        """
        log_dir = Path(self.get("CODEX_SESSION_LOG_DIR"))
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir

    def get_db_path(self) -> Path:
        """Get SQLite database path.

        Returns:
            Path to session_logs.db
        """
        db_path_str = self.get("CODEX_LOG_DB_PATH") or self.get("CODEX_DB_PATH")
        db_path = Path(db_path_str)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return db_path

    def is_sqlite_pool_enabled(self) -> bool:
        """Check if SQLite connection pooling is enabled."""
        return self.get("CODEX_SQLITE_POOL").lower() in _BOOL_STR_TRUE

    def dump_config(self) -> dict[str, str]:
        """Dump current environment configuration.

        Returns:
            Dictionary of all CODEX_* variables and their values
        """
        return {var_name: self.get(var_name) for var_name in self.ENV_VARS}


# Global instance
env_manager = EnvironmentManager()
