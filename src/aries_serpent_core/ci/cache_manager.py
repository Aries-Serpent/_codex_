"""
Unified Cache Management System for GitHub Actions and Local Development.

This module provides comprehensive cache management capabilities across the repository:
- Centralized cache key generation
- Cache coordination across workflows
- Cache validation and health monitoring
- Automatic cleanup and optimization
- Dependency tracking and consistency

Usage:
    from codex.ci.cache_manager import CacheManager, CacheType

    # In GitHub Actions
    manager = CacheManager()
    cache_key = manager.generate_cache_key(
        cache_type=CacheType.PIP,
        workflow_name="pr-checks",
        extra_identifiers={"job": "test"}
    )

    # For cache validation
    health = manager.validate_cache_health()
    logger.info(f"Cache health: {health}")
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from codex.logging.structured_logger import logger
from codex.utils.path_utils import windows_safe_timestamp


class CacheType(Enum):
    """Standard cache types used across the repository."""

    PIP = "pip"
    NOX = "nox"
    UV = "uv"
    GH_CLI = "gh"
    HUGGINGFACE = "huggingface"
    TRANSFORMERS = "transformers"
    PRE_COMMIT = "pre-commit"
    MYPY = "mypy"
    PYTEST = "pytest"
    DOCKER_BUILDX = "docker-buildx"
    YARN = "yarn"
    CARGO = "cargo"
    AGENT_VENV = "agent-venv"  # L6b — lean Copilot agent virtualenv (.venv_agent)
    BRAIN_DB = "brain-db"  # L6c — Cognitive Brain SQLite DB
    CUSTOM = "custom"


@dataclass
class CacheConfig:
    """Configuration for a specific cache."""

    cache_type: CacheType
    paths: list[str]
    key_components: list[str]
    restore_keys: list[str] = field(default_factory=list)
    max_size_mb: Optional[int] = None
    ttl_days: Optional[int] = None

    def to_github_actions(self) -> dict[str, Any]:
        """Convert to GitHub Actions cache format."""
        return {
            "path": "\n".join(self.paths),
            "key": self.key_components[0] if self.key_components else "",
            "restore-keys": "\n".join(self.restore_keys) if self.restore_keys else "",
        }


@dataclass
class CacheHealth:
    """Health status of cache system."""

    total_size_gb: float
    total_caches: int
    cache_hit_rate: Optional[float] = None
    oldest_cache_days: Optional[int] = None
    unused_caches: int = 0
    is_critical: bool = False
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class CacheManager:
    """Unified cache management system for the repository."""

    CACHE_PATHS = {
        CacheType.PIP: ["~/.cache/pip"],
        CacheType.NOX: ["~/.cache/nox", ".nox"],
        CacheType.UV: ["~/.cache/uv"],
        CacheType.GH_CLI: ["~/.cache/gh"],
        CacheType.HUGGINGFACE: ["~/.cache/huggingface"],
        CacheType.TRANSFORMERS: ["~/.cache/transformers"],
        CacheType.PRE_COMMIT: ["~/.cache/pre-commit"],
        CacheType.MYPY: [".mypy_cache"],
        CacheType.PYTEST: [".pytest_cache"],
        CacheType.DOCKER_BUILDX: ["~/.docker/buildx-cache"],
        CacheType.YARN: ["~/.yarn/cache", "~/.npm"],
        CacheType.CARGO: ["~/.cargo/registry", "~/.cargo/git", "target"],
        CacheType.AGENT_VENV: [".venv_agent"],
        CacheType.BRAIN_DB: [".codex/brain.db", ".codex/brain/"],
    }

    DEPENDENCY_FILES = {
        CacheType.PIP: [
            "requirements.txt",
            "requirements-dev.txt",
            "requirements-test.txt",
            "pyproject.toml",
            "setup.py",
            "setup.cfg",
        ],
        CacheType.NOX: ["noxfile.py", "pyproject.toml"],
        CacheType.PRE_COMMIT: [".pre-commit-config.yaml"],
        CacheType.YARN: ["package.json", "yarn.lock", "package-lock.json"],
        CacheType.CARGO: ["Cargo.toml", "Cargo.lock"],
    }

    def __init__(
        self,
        repo_root: Optional[Path] = None,
        github_context: Optional[dict[str, Any]] = None,
    ):
        """Initialize cache manager."""
        self.repo_root = repo_root or self._detect_repo_root()
        self.github_context = github_context or self._load_github_context()

        # Parse CI environment variable strictly
        self.is_ci = self._is_ci_environment()

    @staticmethod
    def _is_ci_environment() -> bool:
        """Return True when current environment indicates CI execution."""
        ci_raw = os.environ.get("CI", "").strip().lower()
        return ci_raw in {"1", "true", "yes", "on"}

    def _detect_repo_root(self) -> Path:
        """Detect repository root directory."""
        if "GITHUB_WORKSPACE" in os.environ:
            return Path(os.environ["GITHUB_WORKSPACE"])

        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent

        return Path.cwd()

    def _load_github_context(self) -> dict[str, Any]:
        """Load GitHub Actions context from environment."""
        return {
            "runner_os": os.environ.get("RUNNER_OS", platform.system()),
            "runner_arch": os.environ.get("RUNNER_ARCH", platform.machine()),
            "workflow": os.environ.get("GITHUB_WORKFLOW", "unknown"),
            "job": os.environ.get("GITHUB_JOB", "unknown"),
            "ref": os.environ.get("GITHUB_REF", "unknown"),
            "sha": os.environ.get("GITHUB_SHA", "unknown"),
        }

    def generate_cache_key(
        self,
        cache_type: CacheType,
        workflow_name: Optional[str] = None,
        extra_identifiers: Optional[dict[str, str]] = None,
        include_timestamp: bool = False,
    ) -> str:
        """Generate consistent cache key."""
        components = []

        components.append(self.github_context["runner_os"])

        if workflow_name:
            components.append(workflow_name)
        elif self.github_context["workflow"] != "unknown":
            components.append(self.github_context["workflow"])

        if extra_identifiers:
            for key in sorted(extra_identifiers.keys()):
                components.append(f"{key}-{extra_identifiers[key]}")

        components.append(cache_type.value)

        dep_hash = self._hash_dependencies(cache_type)
        if dep_hash:
            components.append(dep_hash)

        if include_timestamp:
            timestamp = windows_safe_timestamp(fmt="compact")
            components.append(timestamp)

        return "-".join(components)

    def generate_restore_keys(
        self,
        cache_key: str,
        fallback_levels: int = 2,
    ) -> list[str]:
        """Generate restore keys for cache fallback."""
        parts = cache_key.split("-")
        restore_keys = []

        for i in range(1, min(fallback_levels + 1, len(parts))):
            restore_key = "-".join(parts[:-i]) + "-"
            restore_keys.append(restore_key)

        return restore_keys

    def _hash_dependencies(self, cache_type: CacheType) -> str:
        """Hash dependency files for cache key."""
        files = self.DEPENDENCY_FILES.get(cache_type, [])
        if not files:
            return ""

        hasher = hashlib.sha256()

        for file_pattern in files:
            if "*" in file_pattern:
                matches = list(self.repo_root.glob(file_pattern))
            else:
                matches = [self.repo_root / file_pattern]

            for file_path in sorted(matches):
                if file_path.exists() and file_path.is_file():
                    hasher.update(file_path.read_bytes())

        return hasher.hexdigest()[:12]

    def create_cache_config(
        self,
        cache_type: CacheType,
        workflow_name: Optional[str] = None,
        extra_identifiers: Optional[dict[str, str]] = None,
        additional_paths: Optional[list[str]] = None,
    ) -> CacheConfig:
        """Create complete cache configuration."""
        cache_key = self.generate_cache_key(
            cache_type,
            workflow_name=workflow_name,
            extra_identifiers=extra_identifiers,
        )

        restore_keys = self.generate_restore_keys(cache_key)

        paths = self.CACHE_PATHS.get(cache_type, []).copy()
        if additional_paths:
            paths.extend(additional_paths)

        return CacheConfig(
            cache_type=cache_type,
            paths=paths,
            key_components=[cache_key],
            restore_keys=restore_keys,
        )

    def validate_cache_health(
        self,
        size_threshold_gb: float = 8.0,
        age_threshold_days: int = 30,
    ) -> CacheHealth:
        """Validate cache health and generate recommendations."""
        health = CacheHealth(total_size_gb=0.0, total_caches=0)

        if self.is_ci and self._is_gh_cli_available():
            try:
                result = subprocess.run(
                    ["gh", "cache", "list", "--json", "key,sizeInBytes,createdAt"],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=30,
                )

                caches = json.loads(result.stdout)
                total_bytes = sum(c.get("sizeInBytes", 0) for c in caches)
                health.total_size_gb = total_bytes / (1024**3)
                health.total_caches = len(caches)

                if caches:
                    oldest = min(
                        datetime.fromisoformat(c["createdAt"].replace("Z", "+00:00"))
                        for c in caches
                    )
                    health.oldest_cache_days = (datetime.now(oldest.tzinfo) - oldest).days

            except (
                subprocess.CalledProcessError,
                json.JSONDecodeError,
                KeyError,
                subprocess.TimeoutExpired,
            ):
                # Swallow errors when gh CLI is unavailable or times out
                # Health metrics will remain at default values (0)
                logger.debug("Suppressed exception in handler", exc_info=True)
        if health.total_size_gb > size_threshold_gb:
            health.is_critical = True
            health.warnings.append(
                f"Cache size ({health.total_size_gb:.2f} GB) exceeds threshold ({size_threshold_gb} GB)"  # noqa: E501
            )
            health.recommendations.append("Run cache cleanup to free space")

        if health.oldest_cache_days and health.oldest_cache_days > age_threshold_days:
            health.warnings.append(
                f"Oldest cache is {health.oldest_cache_days} days old (threshold: {age_threshold_days})"  # noqa: E501
            )
            health.recommendations.append("Clean up old caches")

        return health

    def _is_gh_cli_available(self) -> bool:
        """Check if GitHub CLI is available."""
        try:
            subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            return True
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            return False


def main() -> None:
    """CLI interface for cache management."""
    import argparse

    parser = argparse.ArgumentParser(description="Cache Management CLI")
    parser.add_argument(
        "command",
        choices=["validate", "generate-key", "health"],
        help="Command to execute",
    )
    parser.add_argument("--cache-type", help="Cache type")
    parser.add_argument("--workflow", help="Workflow name")

    args = parser.parse_args()

    manager = CacheManager()

    if args.command == "validate":
        health = manager.validate_cache_health()
        logger.info(f"Cache Health: {'CRITICAL' if health.is_critical else 'HEALTHY'}")
        logger.info(f"Total Size: {health.total_size_gb:.2f} GB")
        logger.info(f"Total Caches: {health.total_caches}")
        sys.exit(1 if health.is_critical else 0)

    elif args.command == "generate-key":
        if not args.cache_type:
            logger.error("Error: --cache-type required")
            sys.exit(1)

        cache_type = CacheType(args.cache_type)
        key = manager.generate_cache_key(cache_type, workflow_name=args.workflow)
        logger.info(key)

    elif args.command == "health":
        health = manager.validate_cache_health()
        logger.info(f"Cache Health: {'CRITICAL' if health.is_critical else 'HEALTHY'}")
        logger.info(f"Total Size: {health.total_size_gb:.2f} GB")
        logger.info(f"Total Caches: {health.total_caches}")
        for warning in health.warnings:
            logger.info(f"Warning: {warning}")
        for rec in health.recommendations:
            logger.info(f"Recommendation: {rec}")


if __name__ == "__main__":
    main()
