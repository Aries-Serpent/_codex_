#!/usr/bin/env python3
"""
stdlib-only JSON logging + argparse/subprocess helpers for Codex CLIs.

- Emits JSONL to stderr (one log event per line).
- Fields align with OTel Logs & Elastic ECS where practical:
  timestamp, log.level, log.logger, event.name, message,
  process.pid, thread.name, error.kind, error.message, error.stack,
  process.duration_ms, etc.
"""

from __future__ import annotations

import argparse
import contextvars
import functools
import json
import logging

logger = logging.getLogger(__name__)

import os  # noqa: E402
import shlex  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import traceback  # noqa: E402
import uuid  # noqa: E402
from collections.abc import Mapping, Sequence  # noqa: E402
from datetime import datetime, timezone  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

from codex_ml.logging.session_logger import DEFAULT_LOG_DIR, SessionLogger  # noqa: E402

_SESSION_ID_ENV = "CODEX_SESSION_ID"
_SESSION_LOG_DIR_ENV = "CODEX_SESSION_LOG_DIR"

_session_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "codex_session_id", default=None
)
_SESSION_LOGGER_DISABLED = object()
_session_logger_ctx: contextvars.ContextVar[SessionLogger | object | None] = contextvars.ContextVar(
    "codex_session_logger", default=None
)


def _session_log_dir() -> Path:
    raw = os.getenv(_SESSION_LOG_DIR_ENV)
    if raw:
        try:
            return Path(raw).expanduser()
        except (
            IOError,
            OSError,
            ModuleNotFoundError,
            ImportError,
        ):  # pragma: no cover - defensive fallback
            return DEFAULT_LOG_DIR
    return DEFAULT_LOG_DIR


def get_session_id() -> str:
    """Return the current context's session identifier, creating one if needed.

    A truthy cached identifier wins; otherwise CODEX_SESSION_ID is cached when
    set, or a new UUID string is generated. No logger/file is created and the
    environment is not modified. Later environment changes do not replace a
    truthy cached ID; use set_session_id to select another session explicitly.
    """
    session_id = _session_id_ctx.get()
    if session_id:
        return session_id
    env_value = os.getenv(_SESSION_ID_ENV)
    if env_value:
        _session_id_ctx.set(env_value)
        return env_value
    generated = str(uuid.uuid4())
    _session_id_ctx.set(generated)
    return generated


def set_session_id(session_id: str, *, log_dir: Path | str | None = None) -> str:
    """Select a context-local session and initialize its SessionLogger.

    Args:
        session_id: Identifier coerced to str and cached before logger creation.
            Use a safe filename component: it contributes to the session filename.
        log_dir: Optional directory, with ~ expanded; otherwise
            CODEX_SESSION_LOG_DIR or the SessionLogger default is used.

    Returns:
        String identifier. Logger-construction OSError is logged and disables
        session-file logging in this context rather than raising it.

    Creating a SessionLogger can create directories and prune old session files
    under its retention policy. Repeated calls replace the context's logger;
    they do not update CODEX_SESSION_ID or reconfigure Python log handlers.
    """
    resolved = str(session_id)
    _session_id_ctx.set(resolved)
    directory = Path(log_dir).expanduser() if log_dir is not None else _session_log_dir()
    try:
        _session_logger_ctx.set(SessionLogger(resolved, directory))
    except OSError as e:
        type(e).__name__
        logger.debug("OSError: <ERROR_TYPE>")
        logger.warning("OSError: <ERROR_TYPE>", exc_info=True)
        _session_logger_ctx.set(_SESSION_LOGGER_DISABLED)
    return resolved


def get_session_logger() -> SessionLogger:
    """Return the context's cached SessionLogger or lazily construct one.

    Uses get_session_id and the configured session log directory. Construction
    can create directories and prune old session files; the logger is cached.

    Raises:
        RuntimeError: If logging was disabled by a prior construction OSError,
            or construction now fails with OSError. The latter is chained and
            caches a disabled sentinel; set_session_id can retry initialization.
    """
    session_logger = _session_logger_ctx.get()
    if isinstance(session_logger, SessionLogger):
        return session_logger
    if session_logger is _SESSION_LOGGER_DISABLED:
        raise RuntimeError("Session logging unavailable")
    session_id = get_session_id()
    try:
        session_logger = SessionLogger(session_id, _session_log_dir())
    except OSError as exc:
        logging.getLogger(__name__).debug("OSError: %s", exc)
        _session_logger_ctx.set(_SESSION_LOGGER_DISABLED)
        raise RuntimeError("Session logging unavailable") from exc
    _session_logger_ctx.set(session_logger)
    return session_logger


def _json_safe(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, Mapping):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_json_safe(v) for v in value]
    return str(value)


def _prepare_session_payload(data: Mapping[str, Any]) -> dict[str, Any]:
    prepared: dict[str, Any] = {}
    for key, value in data.items():
        prepared[str(key)] = _json_safe(value)
    return prepared


# -----------------------
# JSON logging primitives
# -----------------------


def _utc_iso(ts: float | None = None) -> str:
    dt = datetime.fromtimestamp(ts if ts is not None else time.time(), tz=timezone.utc)
    return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")


class JsonFormatter(logging.Formatter):
    """Format standard logging records as a single Unicode JSON object.

    Dict messages overlay base timestamp/level/message fields. Eligible record
    extras, exception details, and a default context session.id are included.
    Values are not recursively sanitized or redacted: callers must provide
    JSON-serializable, non-sensitive payloads. Formatting needs only stdlib,
    although importing this module also imports the local SessionLogger.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Serialize record fields, exception information, and eligible extras.

        Args:
            record: LogRecord whose dict message may override base fields. Extras
                cannot replace fields already present in the payload.

        Returns:
            JSON string without a trailing newline, using ensure_ascii=False.
            Missing session.id is filled using get_session_id, not a file logger.

        Raises:
            TypeError: If a payload value is not JSON serializable.
            ValueError: If JSON serialization detects a circular container.
        """
        payload: dict[str, Any] = {
            "timestamp": _utc_iso(record.created),
            "log.level": record.levelname,
            "log.logger": record.name,
            "message": record.getMessage(),
            "process.pid": record.process,
            "thread.name": record.threadName,
        }
        if isinstance(record.msg, dict):
            payload.update(record.msg)
            if "message" not in payload:
                payload["message"] = record.getMessage()

        if record.exc_info:
            etype, evalue, etb = record.exc_info
            payload.setdefault("error.kind", getattr(etype, "__name__", str(etype)))
            payload.setdefault("error.message", str(evalue))
            payload.setdefault(
                "error.stack", "".join(traceback.format_exception(etype, evalue, etb))
            )

        # Include extras passed via logger.*(..., extra={...})
        for k, v in getattr(record, "__dict__", {}).items():
            if (
                k.startswith("_")
                or k in payload
                or k
                in (
                    "msg",
                    "args",
                    "levelname",
                    "levelno",
                    "pathname",
                    "filename",
                    "module",
                    "exc_info",
                    "exc_text",
                    "stack_info",
                    "lineno",
                    "funcName",
                    "created",
                    "msecs",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "processName",
                    "process",
                )
            ):
                continue
            payload[k] = v
        payload.setdefault("session.id", get_session_id())
        return json.dumps(payload, ensure_ascii=False)


def init_json_logging(
    level_env: str = "CODEX_LOG_LEVEL",
    default_level: str = "INFO",
    *,
    session_id: str | None = None,
    session_log_dir: Path | str | None = None,
) -> logging.Logger:
    """Replace root handlers with one stderr JSON handler and choose a session.

    Args:
        level_env: Environment variable containing the logging level name.
        default_level: Fallback level name; unrecognized names resolve to INFO.
        session_id: Truthy explicit ID, then CODEX_SESSION_ID, then the context ID.
        session_log_dir: Directory forwarded to set_session_id, which may create
            directories or prune session history through SessionLogger.

    Returns:
        Logger named codex, propagating to the newly configured root logger.

    Existing root handlers are removed, not closed. Calling again replaces the
    handler again. Failure to initialize session files via OSError is nonfatal.
    """
    resolved_session = session_id or os.environ.get(_SESSION_ID_ENV) or get_session_id()
    set_session_id(str(resolved_session), log_dir=session_log_dir)
    level_name = os.environ.get(level_env, default_level).upper()
    level = getattr(logging, level_name, logging.INFO)
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)
    h = logging.StreamHandler(stream=sys.stderr)
    h.setFormatter(JsonFormatter())
    root.addHandler(h)
    root.setLevel(level)
    return logging.getLogger("codex")


def log_event(logger: logging.Logger, event: str, **fields: Any) -> Any:
    """Emit a structured INFO record and best-effort session-file event.

    Args:
        logger: Python logger receiving the dict record through info.
        event: Session event type and default event.name in the record.
        **fields: Event fields; may override event.name and supply session.id.
            Keep values non-sensitive and JSON serializable for JsonFormatter.

    Returns:
        None, despite the permissive return annotation.

    The file copy converts unsupported values to strings and uses SessionLogger's
    redaction. The regular log record keeps original values and is not redacted
    here. ValueError, TypeError, and RuntimeError during session lookup/writing
    are suppressed; other errors, including session write OSError, propagate.
    """
    rec = {"event.name": event}
    rec.update(fields)
    rec.setdefault("session.id", get_session_id())
    try:
        session_logger = get_session_logger()
    except (ValueError, TypeError, RuntimeError):  # pragma: no cover - defensive
        pass
    else:
        try:
            session_logger.log_event(event, _prepare_session_payload(rec))
        except (ValueError, TypeError, RuntimeError):  # pragma: no cover - defensive
            logger.debug("Suppressed exception in handler", exc_info=True)
    logger.info(rec)


# -----------------------
# Subprocess instrumentation
# -----------------------


def _trim(s: str | None, limit: int = 16_384) -> tuple[str, bool]:
    if s is None:
        return ("", False)
    if len(s) <= limit:
        return (s, False)
    return (s[:limit] + f"\n[[truncated {len(s) - limit} chars]]", True)


def run_cmd(
    argv: Sequence[str],
    *,
    timeout: float | None = None,
    cwd: str | None = None,
    env: Mapping[str, str] | None = None,
    logger: logging.Logger | None = None,
) -> subprocess.CompletedProcess[str]:
    """
    Execute a command with capture and structured logging.
    Returns subprocess.CompletedProcess with text I/O (utf-8).
    """
    lg = logger or logging.getLogger("codex")
    t0 = time.monotonic()
    try:
        cp = subprocess.run(
            list(argv),
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            env=dict(os.environ, **(env or {})) if env else None,
            check=False,
        )
        dur_ms = int((time.monotonic() - t0) * 1000)
        out, out_trunc = _trim(cp.stdout)
        err, err_trunc = _trim(cp.stderr)
        log_event(
            lg,
            "subprocess.exec",
            cmd=shlex.join(map(str, argv)),
            cwd=cwd or "",
            exit_code=cp.returncode,
            process={"duration_ms": dur_ms},
            output={
                "stdout": out,
                "stderr": err,
                "truncated": {"stdout": out_trunc, "stderr": err_trunc},
            },
            timeout=timeout if timeout is not None else "",
        )
        return cp
    except subprocess.TimeoutExpired as e:
        dur_ms = int((time.monotonic() - t0) * 1000)
        log_event(
            lg,
            "subprocess.timeout",
            cmd=shlex.join(map(str, argv)),
            cwd=cwd or "",
            error={"kind": "TimeoutExpired", "message": str(e)},
            process={"duration_ms": dur_ms},
            timeout=timeout,
        )
        raise


# -----------------------
# Argparse integration
# -----------------------


class ArgparseJSONParser(argparse.ArgumentParser):
    """
    Parser that emits a structured log line on parse errors, then exits code 2.
    Mirrors argparse semantics (stderr + exit 2 on invalid args).
    """

    def __init__(self, *a, **k) -> None:
        self._logger = logging.getLogger("codex")
        super().__init__(*a, **k)

    def error(self, message: str) -> Any:
        """Log a cli.argparse_error event and terminate parsing with exit code 2.

        Args:
            message: Parser error text included in the event and stderr output.

        Raises:
            SystemExit: With code 2 after usage and error text are written to stderr,
                unless an earlier logging operation raises.

        No value is returned; logging uses this parser's codex logger and may
        lazily initialize session-file logging.
        """
        usage = self.format_usage().strip()
        log_event(
            self._logger,
            "cli.argparse_error",
            message=message,
            usage=usage,
            prog=self.prog,
        )
        self.exit(2, f"{usage}\nerror: {message}\n")


# -----------------------
# Exception capture helper
# -----------------------


def configure_cli_logging(
    level: int = logging.INFO,
    *,
    stream: Any | None = sys.stderr,
    quiet: bool = False,
) -> Any:
    """Configure a simple CLI logger (stderr by default)."""

    root = logging.getLogger()
    for handler in list(root.handlers):
        root.removeHandler(handler)
    handler = logging.StreamHandler(stream=stream)
    handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    root.addHandler(handler)
    root.setLevel(logging.WARNING if quiet else level)


def _is_successful_system_exit(exc: BaseException) -> bool:
    return isinstance(exc, SystemExit) and int(getattr(exc, "code", 0) or 0) == 0


class _CaptureExceptionsContext:
    """Context manager variant used by existing CLIs."""

    def __init__(self, logger: logging.Logger | None = None, event: str = "app.exception"):
        self.logger = logger or logging.getLogger("codex")
        self.event = event

    def __enter__(self) -> Any:
        return self

    def __exit__(self, etype, evalue, etb) -> Any:
        if etype is None:
            return False
        if isinstance(evalue, SystemExit):
            raw_code = getattr(evalue, "code", 0)
            try:
                code = int(raw_code or 0)
            except (TypeError, ValueError):
                # SystemExit.code can be a string message (e.g. from raise SystemExit("msg"))
                code = 1
            if code == 0:
                log_event(self.logger, "cli.exit", exit_status="success", code=code)
                return False
            log_event(
                self.logger,
                self.event,
                error={"kind": "SystemExit", "message": str(code)},
            )
            return False

        stack = "".join(traceback.format_exception(etype, evalue, etb))
        log_event(
            self.logger,
            self.event,
            error={
                "kind": getattr(etype, "__name__", str(etype)),
                "message": str(evalue),
                "stack": stack,
            },
        )
        return False

    def __call__(self, target: Any):
        return capture_exceptions(target, logger=self.logger, event=self.event)


def capture_exceptions(
    func: Any | None = None,
    *,
    logger: logging.Logger | None = None,
    event: str = "app.exception",
):
    """Decorator/context manager hybrid for consistent CLI exception handling."""

    if callable(func) and not isinstance(func, logging.Logger):
        target = func

        @functools.wraps(target)
        def _wrapped(*args: Any, **kwargs: Any) -> int:
            resolved_logger = logger or logging.getLogger(target.__module__)
            try:
                result = target(*args, **kwargs)
            except (  # noqa: BLE001
                Exception,
                SystemExit,
                KeyboardInterrupt,
            ) as exc:  # intentional: catch SystemExit/KeyboardInterrupt to log them
                if _is_successful_system_exit(exc):
                    resolved_logger.info("exited successfully (SystemExit(0))")
                    return 0
                if isinstance(exc, SystemExit):
                    code = int(getattr(exc, "code", 1) or 1)
                    resolved_logger.warning("SystemExit(%s) raised", code)
                    return code
                resolved_logger.error("Unhandled exception", exc_info=exc)
                return 1

            if result is None:
                resolved_logger.debug("Exception caught, returning", exc_info=True)
                return 0
            try:
                return int(result)
            except (ValueError, TypeError, RuntimeError):
                resolved_logger.warning("Exception occurred", exc_info=True)
                return 0

        return _wrapped

    logger_obj = func if isinstance(func, logging.Logger) else logger
    return _CaptureExceptionsContext(logger=logger_obj, event=event)
