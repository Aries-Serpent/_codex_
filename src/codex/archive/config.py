"""Archive backend configuration loader with TOML/YAML/env var support."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

try:  # pragma: no cover - Python < 3.11 fallback
    import tomllib
except ImportError:  # pragma: no cover
    import tomli as tomllib  # type: ignore


@dataclass(frozen=True)
class BackendConfig:
    """Archive backend configuration."""

    type: Literal["sqlite", "postgres", "mariadb"] = "sqlite"
    url: str = "sqlite:///./.codex/archive.sqlite"


@dataclass(frozen=True)
class LoggingConfig:
    """Logging configuration."""

    level: Literal["debug", "info", "warn", "error"] = "info"
    format: Literal["json", "text"] = "json"
    file: str | None = None


@dataclass(frozen=True)
class RetryConfig:
    """Retry policy configuration."""

    enabled: bool = False
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 32.0
    backoff_factor: float = 2.0
    jitter: bool = True


@dataclass(frozen=True)
class BatchConfig:
    """Batch operations configuration."""

    max_concurrent: int = 5
    timeout_per_item: int = 300
    continue_on_error: bool = False


@dataclass(frozen=True)
class PerformanceConfig:
    """Performance tracking configuration."""

    enable_metrics: bool = True
    track_decompression: bool = True


@dataclass(frozen=True)
class ArchiveConfig:
    """Complete archive configuration."""

    backend: BackendConfig = field(default_factory=BackendConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    batch: BatchConfig = field(default_factory=BatchConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)

    @classmethod
    def from_env(cls) -> ArchiveConfig:
        """Load configuration from environment variables."""

        return cls(
            backend=BackendConfig(
                type=os.getenv("CODEX_ARCHIVE_BACKEND", "sqlite").lower(),
                url=os.getenv("CODEX_ARCHIVE_URL", "sqlite:///./.codex/archive.sqlite"),
            ),
            logging=LoggingConfig(
                level=os.getenv("CODEX_ARCHIVE_LOG_LEVEL", "info").lower(),
                format=os.getenv("CODEX_ARCHIVE_LOG_FORMAT", "json").lower(),
                file=os.getenv("CODEX_ARCHIVE_LOG_FILE"),
            ),
            retry=RetryConfig(
                enabled=os.getenv("CODEX_ARCHIVE_RETRY_ENABLED", "false").lower() == "true",
                max_attempts=int(os.getenv("CODEX_ARCHIVE_RETRY_MAX", "3")),
                initial_delay=float(os.getenv("CODEX_ARCHIVE_RETRY_INITIAL", "1.0")),
                max_delay=float(os.getenv("CODEX_ARCHIVE_RETRY_MAX_DELAY", "32.0")),
                backoff_factor=float(os.getenv("CODEX_ARCHIVE_RETRY_BACKOFF", "2.0")),
                jitter=os.getenv("CODEX_ARCHIVE_RETRY_JITTER", "true").lower() == "true",
            ),
            batch=BatchConfig(
                max_concurrent=int(os.getenv("CODEX_ARCHIVE_BATCH_CONCURRENT", "5")),
                timeout_per_item=int(os.getenv("CODEX_ARCHIVE_BATCH_TIMEOUT", "300")),
                continue_on_error=os.getenv("CODEX_ARCHIVE_BATCH_CONTINUE", "false").lower()
                == "true",
            ),
            performance=PerformanceConfig(
                enable_metrics=os.getenv("CODEX_ARCHIVE_PERF_ENABLED", "true").lower() == "true",
                track_decompression=os.getenv("CODEX_ARCHIVE_PERF_DECOMP", "true").lower()
                == "true",
            ),
        )

    @classmethod
    def from_file(cls, config_path: str | Path) -> ArchiveConfig:
        """Load configuration from TOML file."""

        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with path.open("rb") as handle:
            config_dict = tomllib.load(handle)

        return cls(
            backend=BackendConfig(**config_dict.get("backend", {})),
            logging=LoggingConfig(**config_dict.get("logging", {})),
            retry=RetryConfig(**config_dict.get("retry", {})),
            batch=BatchConfig(**config_dict.get("batch", {})),
            performance=PerformanceConfig(**config_dict.get("performance", {})),
        )

    @classmethod
    def load(cls, config_file: str | None = None) -> ArchiveConfig:
        """Load configuration with precedence: file → env → defaults."""

        if config_file:
            return cls.from_file(config_file)

        default_config = Path(".codex/archive.toml")
        if default_config.exists():
            return cls.from_file(default_config)

        return cls.from_env()

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""

        return {
            "backend": {
                "type": self.backend.type,
                "url": self.backend.url,
            },
            "logging": {
                "level": self.logging.level,
                "format": self.logging.format,
                "file": self.logging.file,
            },
            "retry": {
                "enabled": self.retry.enabled,
                "max_attempts": self.retry.max_attempts,
                "initial_delay": self.retry.initial_delay,
                "max_delay": self.retry.max_delay,
                "backoff_factor": self.retry.backoff_factor,
                "jitter": self.retry.jitter,
            },
            "batch": {
                "max_concurrent": self.batch.max_concurrent,
                "timeout_per_item": self.batch.timeout_per_item,
                "continue_on_error": self.batch.continue_on_error,
            },
            "performance": {
                "enable_metrics": self.performance.enable_metrics,
                "track_decompression": self.performance.track_decompression,
            },
        }

    def to_json(self) -> str:
        """Serialize configuration to JSON."""

        return json.dumps(self.to_dict(), indent=2, sort_keys=True)
