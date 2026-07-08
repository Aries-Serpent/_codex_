"""Configuration management for Codex.

Provides environment variable management and configuration utilities.
"""

from .env_vars import EnvironmentManager, env_manager

__all__ = ["EnvironmentManager", "env_manager"]
