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
import functools
import json
import logging
import os
import shlex
import subprocess
import sys
import time
import traceback
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any

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
        return json.dumps(payload, ensure_ascii=False)


def init_json_logging(
    level_env: str = "CODEX_LOG_LEVEL", default_level: str = "INFO"
) -> logging.Logger:
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


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    rec = {"event.name": event}
    rec.update(fields)
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

    def __init__(self, *a, **k):
        self._logger = logging.getLogger("codex")
        super().__init__(*a, **k)

    def error(self, message: str) -> None:
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
) -> None:
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

    def __enter__(self):
        return self

    def __exit__(self, etype, evalue, etb):
        if etype is None:
            return False
        if isinstance(evalue, SystemExit):
            code = int(getattr(evalue, "code", 0) or 0)
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
            log = logger or logging.getLogger(target.__module__)
            try:
                result = target(*args, **kwargs)
            except BaseException as exc:  # pragma: no cover - exercised in tests
                if _is_successful_system_exit(exc):
                    log.info("exited successfully (SystemExit(0))")
                    return 0
                if isinstance(exc, SystemExit):
                    code = int(getattr(exc, "code", 1) or 1)
                    log.warning("SystemExit(%s) raised", code)
                    return code
                log.error("Unhandled exception", exc_info=exc)
                return 1

            if result is None:
                return 0
            try:
                return int(result)
            except Exception:
                return 0

        return _wrapped

    logger_obj = func if isinstance(func, logging.Logger) else logger
    return _CaptureExceptionsContext(logger=logger_obj, event=event)
