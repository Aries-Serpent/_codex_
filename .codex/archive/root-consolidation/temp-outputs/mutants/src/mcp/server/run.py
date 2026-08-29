"""
Run Module

This module provides functionality for run.

Usage:
    from server.run import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import argparse
import importlib
import logging
import os
import socket
import sys
import time
from typing import Optional

import uvicorn

logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument(
        "--port-fallbacks", type=int, default=3, help="Number of fallback ports to try"
    )
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help="Allow binding to 0.0.0.0 or :: (requires explicit opt-in).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    logger = logging.getLogger("mcp.server.run")

    diagnostics = args.diagnostics or os.environ.get("MCP_STARTUP_DIAGNOSTICS") == "1"
    if diagnostics:
        info_lines = [
            f"Python: {sys.version}",
            f"Executable: {sys.executable}",
            f"PID: {os.getpid()}",
            f"Host/Port: {args.host}:{args.port}",
            f"PYTHONPATH: {os.environ.get('PYTHONPATH', '')}",
            f"Uvicorn: {uvicorn.__version__}",
        ]
        for line in info_lines:
            logger.info(line)
            print(line, flush=True)

    allow_public = args.allow_public_bind or os.environ.get("MCP_ALLOW_PUBLIC_BIND") == "1"
    if _is_public_bind(args.host) and not allow_public:
        logger.error(
            "Refusing to bind to public interface %s without explicit opt-in. "
            "Use --allow-public-bind or set MCP_ALLOW_PUBLIC_BIND=1.",
            args.host,
        )
        raise SystemExit(2)

    host, port = _select_port(args.host, args.port, args.port_fallbacks, logger, diagnostics)
    start = time.time()
    app = importlib.import_module("src.mcp.server.facade_fastapi").APP
    elapsed = time.time() - start
    logger.info("Loaded APP in %.3fs", elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def _select_port(
    host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool
) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning(
                    "Port %s unavailable (%s). Falling back to %s.",
                    port,
                    reason,
                    candidate,
                )
                if diagnostics:
                    print(
                        f"Port {port} unavailable ({reason}). Falling back to {candidate}.",
                        flush=True,
                    )
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def _is_public_bind(host: str) -> bool:
    return host in {"0.0.0.0", "::"}  # nosec B104


def _check_bind(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        type(exc).__name__
        logger.debug("OSError: <ERROR_TYPE>")
        logger.debug("Exception caught, returning", exc_info=True)
        return False, str(exc)


if __name__ == "__main__":
    main()
