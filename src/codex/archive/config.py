"""Configuration helpers for the archive command surface."""

from __future__ import annotations

import os
import typing as _t
from dataclasses import asdict, dataclass, field
from pathlib import Path

if _t.TYPE_CHECKING:  # pragma: no cover - typing helpers
    from .backend import ArchiveConfig as _ArchiveConfig
    from .retry import RetryConfig as _RetryConfig
else:  # pragma: no cover - runtime fallback for type hints
    _ArchiveConfig = _t.Any  # type: ignore[assignment]
    _RetryConfig = _t.Any  # type: ignore[assignment]

try:  # pragma: no cover - Python 3.11+
    import tomllib as _toml
except ModuleNotFoundError:  # pragma: no cover - fallback for <3.11
    import tomli as _toml  # type: ignore


_T = _t.TypeVar("_T")
_ENV_BOOL_TRUE = {"1", "true", "yes", "on", "enabled"}
_ENV_BOOL_FALSE = {"0", "false", "no", "off", "disabled"}
_SUPPORTED_BACKENDS = {"sqlite", "postgres", "mariadb"}


def _coerce_bool(value: object, *, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, int | float):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in _ENV_BOOL_TRUE:
            return True
        if lowered in _ENV_BOOL_FALSE:
            return False
    return default


def _coerce_int(value: object, *, default: int) -> int:
    if isinstance(value, bool):  # pragma: no branch - bool is int subclass
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return default
    return default


def _coerce_float(value: object, *, default: float) -> float:
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return default
    return default


def _load_toml(path: Path) -> dict[str, _t.Any]:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file does not exist: {path}")
    with path.open("rb") as handle:
        data = _toml.load(handle)
    if not isinstance(data, dict):  # pragma: no cover - defensive
        raise ValueError("TOML configuration must yield a table at the root level")
    return data


@dataclass(frozen=True)
class BackendConfig:
    """Backend connection information."""

    backend: str = "sqlite"
    url: str = "sqlite:///./.codex/archive.sqlite"

    def __post_init__(self) -> None:  # pragma: no cover - exercised indirectly
        object.__setattr__(self, "backend", self.backend.lower())
        if self.backend not in _SUPPORTED_BACKENDS:
            raise ValueError(f"Unsupported archive backend: {self.backend}")
        if not self.url:
            raise ValueError("Archive URL must be provided")

    @classmethod
    def from_dict(cls, payload: dict[str, _t.Any]) -> BackendConfig:
        backend = payload.get("backend", cls.backend)
        url = payload.get("url", cls.url)
        return cls(backend=backend, url=url)

    @classmethod
    def from_env(cls, env: dict[str, str]) -> BackendConfig:
        backend = env.get("CODEX_ARCHIVE_BACKEND")
        url = env.get("CODEX_ARCHIVE_URL")
        payload = {}
        if backend:
            payload["backend"] = backend
        if url:
            payload["url"] = url
            if not backend:
                from .backend import infer_backend

                payload["backend"] = infer_backend(url)
        return cls.from_dict(payload)

    def to_archive_config(self) -> _ArchiveConfig:
        from .backend import ArchiveConfig

        return ArchiveConfig(url=self.url, backend=self.backend)


@dataclass(frozen=True)
class LoggingConfig:
    """Logging configuration for archive commands."""

    level: str = "info"
    format: str = "text"
    evidence_file: Path | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "level", self.level.lower())
        object.__setattr__(self, "format", self.format.lower())
        if self.format not in {"text", "json"}:
            raise ValueError("Logging format must be either 'text' or 'json'")

    @classmethod
    def from_dict(cls, payload: dict[str, _t.Any]) -> LoggingConfig:
        return cls(
            level=payload.get("level", cls.level),
            format=payload.get("format", cls.format),
            evidence_file=Path(payload["evidence_file"]) if payload.get("evidence_file") else None,
        )

    @classmethod
    def from_env(cls, env: dict[str, str]) -> LoggingConfig:
        payload: dict[str, _t.Any] = {}
        if env.get("CODEX_ARCHIVE_LOG_LEVEL"):
            payload["level"] = env["CODEX_ARCHIVE_LOG_LEVEL"]
        if env.get("CODEX_ARCHIVE_LOG_FORMAT"):
            payload["format"] = env["CODEX_ARCHIVE_LOG_FORMAT"]
        if env.get("CODEX_ARCHIVE_LOG_EVIDENCE"):
            payload["evidence_file"] = env["CODEX_ARCHIVE_LOG_EVIDENCE"]
        return cls.from_dict(payload)


@dataclass(frozen=True)
class RetrySettings:
    """Retry parameters for batch operations."""

    enabled: bool = True
    max_attempts: int = 5
    initial_delay: float = 1.0
    max_delay: float = 32.0
    multiplier: float = 2.0
    jitter: float = 0.1
    seed: int | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, _t.Any]) -> RetrySettings:
        return cls(
            enabled=_coerce_bool(payload.get("enabled"), default=cls.enabled),
            max_attempts=_coerce_int(payload.get("max_attempts"), default=cls.max_attempts),
            initial_delay=_coerce_float(payload.get("initial_delay"), default=cls.initial_delay),
            max_delay=_coerce_float(payload.get("max_delay"), default=cls.max_delay),
            multiplier=_coerce_float(payload.get("multiplier"), default=cls.multiplier),
            jitter=_coerce_float(payload.get("jitter"), default=cls.jitter),
            seed=(
                _coerce_int(payload.get("seed"), default=0)
                if payload.get("seed") is not None
                else None
            ),
        )

    @classmethod
    def from_env(cls, env: dict[str, str]) -> RetrySettings:
        payload: dict[str, _t.Any] = {}
        if env.get("CODEX_ARCHIVE_RETRY_ENABLED"):
            payload["enabled"] = env["CODEX_ARCHIVE_RETRY_ENABLED"]
        if env.get("CODEX_ARCHIVE_RETRY_ATTEMPTS"):
            payload["max_attempts"] = env["CODEX_ARCHIVE_RETRY_ATTEMPTS"]
        if env.get("CODEX_ARCHIVE_RETRY_INITIAL"):
            payload["initial_delay"] = env["CODEX_ARCHIVE_RETRY_INITIAL"]
        if env.get("CODEX_ARCHIVE_RETRY_MAX"):
            payload["max_delay"] = env["CODEX_ARCHIVE_RETRY_MAX"]
        if env.get("CODEX_ARCHIVE_RETRY_MULTIPLIER"):
            payload["multiplier"] = env["CODEX_ARCHIVE_RETRY_MULTIPLIER"]
        if env.get("CODEX_ARCHIVE_RETRY_JITTER"):
            payload["jitter"] = env["CODEX_ARCHIVE_RETRY_JITTER"]
        if env.get("CODEX_ARCHIVE_RETRY_SEED"):
            payload["seed"] = env["CODEX_ARCHIVE_RETRY_SEED"]
        return cls.from_dict(payload)

    def to_retry_config(self) -> _RetryConfig:
        from .retry import RetryConfig

        return RetryConfig(
            enabled=self.enabled,
            max_attempts=self.max_attempts,
            initial_delay=self.initial_delay,
            max_delay=self.max_delay,
            multiplier=self.multiplier,
            jitter=self.jitter,
            seed=self.seed,
        )


@dataclass(frozen=True)
class BatchConfig:
    """Batch execution parameters."""

    concurrent: int = 4
    progress_interval: int = 10
    results_path: Path | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, _t.Any]) -> BatchConfig:
        return cls(
            concurrent=max(1, _coerce_int(payload.get("concurrent"), default=cls.concurrent)),
            progress_interval=max(
                1, _coerce_int(payload.get("progress_interval"), default=cls.progress_interval)
            ),
            results_path=Path(payload["results_path"]) if payload.get("results_path") else None,
        )

    @classmethod
    def from_env(cls, env: dict[str, str]) -> BatchConfig:
        payload: dict[str, _t.Any] = {}
        if env.get("CODEX_ARCHIVE_BATCH_CONCURRENT"):
            payload["concurrent"] = env["CODEX_ARCHIVE_BATCH_CONCURRENT"]
        if env.get("CODEX_ARCHIVE_BATCH_PROGRESS"):
            payload["progress_interval"] = env["CODEX_ARCHIVE_BATCH_PROGRESS"]
        if env.get("CODEX_ARCHIVE_BATCH_RESULTS"):
            payload["results_path"] = env["CODEX_ARCHIVE_BATCH_RESULTS"]
        return cls.from_dict(payload)


@dataclass(frozen=True)
class PerformanceConfig:
    """Performance instrumentation toggles."""

    enabled: bool = True
    emit_to_evidence: bool = True

    @classmethod
    def from_dict(cls, payload: dict[str, _t.Any]) -> PerformanceConfig:
        return cls(
            enabled=_coerce_bool(payload.get("enabled"), default=cls.enabled),
            emit_to_evidence=_coerce_bool(
                payload.get("emit_to_evidence"), default=cls.emit_to_evidence
            ),
        )

    @classmethod
    def from_env(cls, env: dict[str, str]) -> PerformanceConfig:
        payload: dict[str, _t.Any] = {}
        if env.get("CODEX_ARCHIVE_PERF_ENABLED"):
            payload["enabled"] = env["CODEX_ARCHIVE_PERF_ENABLED"]
        if env.get("CODEX_ARCHIVE_PERF_EVIDENCE"):
            payload["emit_to_evidence"] = env["CODEX_ARCHIVE_PERF_EVIDENCE"]
        return cls.from_dict(payload)


@dataclass(frozen=True)
class ArchiveAppConfig:
    """Top level configuration loaded for CLI commands."""

    backend: BackendConfig = field(default_factory=BackendConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    retry: RetrySettings = field(default_factory=RetrySettings)
    batch: BatchConfig = field(default_factory=BatchConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)

    @classmethod
    def from_dict(cls, payload: dict[str, _t.Any]) -> ArchiveAppConfig:
        return cls(
            backend=BackendConfig.from_dict(payload.get("backend", {})),
            logging=LoggingConfig.from_dict(payload.get("logging", {})),
            retry=RetrySettings.from_dict(payload.get("retry", {})),
            batch=BatchConfig.from_dict(payload.get("batch", {})),
            performance=PerformanceConfig.from_dict(payload.get("performance", {})),
        )

    @classmethod
    def from_env(cls, env: dict[str, str]) -> ArchiveAppConfig:
        return cls(
            backend=BackendConfig.from_env(env),
            logging=LoggingConfig.from_env(env),
            retry=RetrySettings.from_env(env),
            batch=BatchConfig.from_env(env),
            performance=PerformanceConfig.from_env(env),
        )

    @classmethod
    def from_file(cls, path: Path) -> ArchiveAppConfig:
        data = _load_toml(path)
        return cls.from_dict(data)

    @classmethod
    def load(
        cls,
        *,
        config_file: Path | str | None = None,
        env: _t.Mapping[str, str] | None = None,
    ) -> ArchiveAppConfig:
        runtime_env = dict(os.environ)
        if env is not None:
            runtime_env.update(env)

        file_override = config_file or runtime_env.get("CODEX_ARCHIVE_CONFIG")
        base_config = cls()
        if file_override:
            base_config = cls.from_file(Path(file_override))

        env_config = cls.from_env(runtime_env)

        return cls(
            backend=_merge(base_config.backend, env_config.backend),
            logging=_merge(base_config.logging, env_config.logging),
            retry=_merge(base_config.retry, env_config.retry),
            batch=_merge(base_config.batch, env_config.batch),
            performance=_merge(base_config.performance, env_config.performance),
        )

    def to_backend_config(self) -> _ArchiveConfig:
        return self.backend.to_archive_config()

    def to_dict(self) -> dict[str, _t.Any]:
        return {
            "backend": asdict(self.backend),
            "logging": _serialize_logging(self.logging),
            "retry": asdict(self.retry),
            "batch": _serialize_batch(self.batch),
            "performance": asdict(self.performance),
        }


def _merge(current: _T, override: _T) -> _T:
    if current == override:
        return current
    cls = type(current)
    defaults = asdict(cls())
    payload = asdict(current)
    for key, value in asdict(override).items():
        default_value = defaults.get(key)
        if value == default_value:
            continue
        payload[key] = value
    return cls(**payload)


def _serialize_logging(config: LoggingConfig) -> dict[str, _t.Any]:
    payload = asdict(config)
    if config.evidence_file is not None:
        payload["evidence_file"] = str(config.evidence_file)
    return payload


def _serialize_batch(config: BatchConfig) -> dict[str, _t.Any]:
    payload = asdict(config)
    if config.results_path is not None:
        payload["results_path"] = str(config.results_path)
    return payload
