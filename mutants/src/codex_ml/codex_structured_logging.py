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
        except (IOError, OSError):  # pragma: no cover - defensive fallback
            return DEFAULT_LOG_DIR
    return DEFAULT_LOG_DIR


def get_session_id() -> str:
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
    def format(self, record: logging.LogRecord) -> str:
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
