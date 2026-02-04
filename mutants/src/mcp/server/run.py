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
import logging
import os
import socket
import sys
from typing import Optional

import importlib
import time

import uvicorn
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


def x_main__mutmut_orig() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_1() -> None:
    parser = None
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_2() -> None:
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_3() -> None:
    parser = argparse.ArgumentParser(description="XXRun MCP FastAPI serverXX")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_4() -> None:
    parser = argparse.ArgumentParser(description="run mcp fastapi server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_5() -> None:
    parser = argparse.ArgumentParser(description="RUN MCP FASTAPI SERVER")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_6() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        None,
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_7() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=None,
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_8() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help=None,
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_9() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_10() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_11() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_12() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "XX--hostXX",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_13() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--HOST",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_14() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get(None, "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_15() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", None),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_16() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_17() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", ),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_18() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("XXMCP_SERVER_HOSTXX", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_19() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("mcp_server_host", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_20() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "XX127.0.0.1XX"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_21() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="XXHost interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).XX",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_22() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="host interface to bind (default: 127.0.0.1 or mcp_server_host).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_23() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="HOST INTERFACE TO BIND (DEFAULT: 127.0.0.1 OR MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_24() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument(None, type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_25() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=None, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_26() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_27() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument(type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_28() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_29() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, )
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_30() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("XX--portXX", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_31() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--PORT", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_32() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8081)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_33() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument(None, default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_34() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default=None)
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_35() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument(default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_36() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", )
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_37() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("XX--log-levelXX", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_38() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--LOG-LEVEL", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_39() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="XXinfoXX")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_40() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_41() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument(None, type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_42() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=None, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_43() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=None, help="Number of fallback ports to try")
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


def x_main__mutmut_44() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help=None)
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


def x_main__mutmut_45() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument(type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_46() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_47() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, help="Number of fallback ports to try")
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


def x_main__mutmut_48() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, )
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


def x_main__mutmut_49() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("XX--port-fallbacksXX", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_50() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--PORT-FALLBACKS", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_51() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=4, help="Number of fallback ports to try")
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


def x_main__mutmut_52() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="XXNumber of fallback ports to tryXX")
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


def x_main__mutmut_53() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="number of fallback ports to try")
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


def x_main__mutmut_54() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="NUMBER OF FALLBACK PORTS TO TRY")
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


def x_main__mutmut_55() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument(None, action="store_true", help="Enable startup diagnostics")
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


def x_main__mutmut_56() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action=None, help="Enable startup diagnostics")
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


def x_main__mutmut_57() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help=None)
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


def x_main__mutmut_58() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument(action="store_true", help="Enable startup diagnostics")
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


def x_main__mutmut_59() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", help="Enable startup diagnostics")
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


def x_main__mutmut_60() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", )
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


def x_main__mutmut_61() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("XX--diagnosticsXX", action="store_true", help="Enable startup diagnostics")
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


def x_main__mutmut_62() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--DIAGNOSTICS", action="store_true", help="Enable startup diagnostics")
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


def x_main__mutmut_63() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="XXstore_trueXX", help="Enable startup diagnostics")
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


def x_main__mutmut_64() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="STORE_TRUE", help="Enable startup diagnostics")
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


def x_main__mutmut_65() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="XXEnable startup diagnosticsXX")
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


def x_main__mutmut_66() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="enable startup diagnostics")
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


def x_main__mutmut_67() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="ENABLE STARTUP DIAGNOSTICS")
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


def x_main__mutmut_68() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        None,
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


def x_main__mutmut_69() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action=None,
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


def x_main__mutmut_70() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help=None,
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


def x_main__mutmut_71() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
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


def x_main__mutmut_72() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
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


def x_main__mutmut_73() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
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


def x_main__mutmut_74() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "XX--allow-public-bindXX",
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


def x_main__mutmut_75() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--ALLOW-PUBLIC-BIND",
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


def x_main__mutmut_76() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="XXstore_trueXX",
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


def x_main__mutmut_77() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="STORE_TRUE",
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


def x_main__mutmut_78() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help="XXAllow binding to 0.0.0.0 or :: (requires explicit opt-in).XX",
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


def x_main__mutmut_79() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help="allow binding to 0.0.0.0 or :: (requires explicit opt-in).",
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


def x_main__mutmut_80() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help="ALLOW BINDING TO 0.0.0.0 OR :: (REQUIRES EXPLICIT OPT-IN).",
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


def x_main__mutmut_81() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help="Allow binding to 0.0.0.0 or :: (requires explicit opt-in).",
    )
    args = None

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


def x_main__mutmut_82() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help="Allow binding to 0.0.0.0 or :: (requires explicit opt-in).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=None)
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


def x_main__mutmut_83() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help="Allow binding to 0.0.0.0 or :: (requires explicit opt-in).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=getattr(None, args.log_level.upper(), logging.INFO))
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


def x_main__mutmut_84() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help="Allow binding to 0.0.0.0 or :: (requires explicit opt-in).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, None, logging.INFO))
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


def x_main__mutmut_85() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help="Allow binding to 0.0.0.0 or :: (requires explicit opt-in).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), None))
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


def x_main__mutmut_86() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help="Allow binding to 0.0.0.0 or :: (requires explicit opt-in).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=getattr(args.log_level.upper(), logging.INFO))
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


def x_main__mutmut_87() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help="Allow binding to 0.0.0.0 or :: (requires explicit opt-in).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, logging.INFO))
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


def x_main__mutmut_88() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help="Allow binding to 0.0.0.0 or :: (requires explicit opt-in).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), ))
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


def x_main__mutmut_89() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help="Allow binding to 0.0.0.0 or :: (requires explicit opt-in).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.lower(), logging.INFO))
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


def x_main__mutmut_90() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help="Allow binding to 0.0.0.0 or :: (requires explicit opt-in).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    logger = None

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


def x_main__mutmut_91() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help="Allow binding to 0.0.0.0 or :: (requires explicit opt-in).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    logger = logging.getLogger(None)

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


def x_main__mutmut_92() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help="Allow binding to 0.0.0.0 or :: (requires explicit opt-in).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    logger = logging.getLogger("XXmcp.server.runXX")

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


def x_main__mutmut_93() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help="Allow binding to 0.0.0.0 or :: (requires explicit opt-in).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    logger = logging.getLogger("MCP.SERVER.RUN")

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


def x_main__mutmut_94() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help="Allow binding to 0.0.0.0 or :: (requires explicit opt-in).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    logger = logging.getLogger("mcp.server.run")

    diagnostics = None
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


def x_main__mutmut_95() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help="Allow binding to 0.0.0.0 or :: (requires explicit opt-in).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    logger = logging.getLogger("mcp.server.run")

    diagnostics = args.diagnostics and os.environ.get("MCP_STARTUP_DIAGNOSTICS") == "1"
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


def x_main__mutmut_96() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help="Allow binding to 0.0.0.0 or :: (requires explicit opt-in).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    logger = logging.getLogger("mcp.server.run")

    diagnostics = args.diagnostics or os.environ.get(None) == "1"
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


def x_main__mutmut_97() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help="Allow binding to 0.0.0.0 or :: (requires explicit opt-in).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    logger = logging.getLogger("mcp.server.run")

    diagnostics = args.diagnostics or os.environ.get("XXMCP_STARTUP_DIAGNOSTICSXX") == "1"
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


def x_main__mutmut_98() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help="Allow binding to 0.0.0.0 or :: (requires explicit opt-in).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    logger = logging.getLogger("mcp.server.run")

    diagnostics = args.diagnostics or os.environ.get("mcp_startup_diagnostics") == "1"
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


def x_main__mutmut_99() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help="Allow binding to 0.0.0.0 or :: (requires explicit opt-in).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    logger = logging.getLogger("mcp.server.run")

    diagnostics = args.diagnostics or os.environ.get("MCP_STARTUP_DIAGNOSTICS") != "1"
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


def x_main__mutmut_100() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
    parser.add_argument("--diagnostics", action="store_true", help="Enable startup diagnostics")
    parser.add_argument(
        "--allow-public-bind",
        action="store_true",
        help="Allow binding to 0.0.0.0 or :: (requires explicit opt-in).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    logger = logging.getLogger("mcp.server.run")

    diagnostics = args.diagnostics or os.environ.get("MCP_STARTUP_DIAGNOSTICS") == "XX1XX"
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


def x_main__mutmut_101() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
        info_lines = None
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


def x_main__mutmut_102() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
            f"PYTHONPATH: {os.environ.get(None, '')}",
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


def x_main__mutmut_103() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
            f"PYTHONPATH: {os.environ.get('PYTHONPATH', None)}",
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


def x_main__mutmut_104() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
            f"PYTHONPATH: {os.environ.get('')}",
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


def x_main__mutmut_105() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
            f"PYTHONPATH: {os.environ.get('PYTHONPATH', )}",
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


def x_main__mutmut_106() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
            f"PYTHONPATH: {os.environ.get('XXPYTHONPATHXX', '')}",
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


def x_main__mutmut_107() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
            f"PYTHONPATH: {os.environ.get('pythonpath', '')}",
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


def x_main__mutmut_108() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
            f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'XXXX')}",
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


def x_main__mutmut_109() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
            logger.info(None)
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


def x_main__mutmut_110() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
            print(None, flush=True)

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


def x_main__mutmut_111() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
            print(line, flush=None)

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


def x_main__mutmut_112() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
            print(flush=True)

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


def x_main__mutmut_113() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
            print(line, )

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


def x_main__mutmut_114() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
            print(line, flush=False)

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


def x_main__mutmut_115() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    allow_public = None
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


def x_main__mutmut_116() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    allow_public = args.allow_public_bind and os.environ.get("MCP_ALLOW_PUBLIC_BIND") == "1"
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


def x_main__mutmut_117() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    allow_public = args.allow_public_bind or os.environ.get(None) == "1"
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


def x_main__mutmut_118() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    allow_public = args.allow_public_bind or os.environ.get("XXMCP_ALLOW_PUBLIC_BINDXX") == "1"
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


def x_main__mutmut_119() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    allow_public = args.allow_public_bind or os.environ.get("mcp_allow_public_bind") == "1"
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


def x_main__mutmut_120() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    allow_public = args.allow_public_bind or os.environ.get("MCP_ALLOW_PUBLIC_BIND") != "1"
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


def x_main__mutmut_121() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    allow_public = args.allow_public_bind or os.environ.get("MCP_ALLOW_PUBLIC_BIND") == "XX1XX"
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


def x_main__mutmut_122() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    if _is_public_bind(args.host) or not allow_public:
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


def x_main__mutmut_123() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    if _is_public_bind(None) and not allow_public:
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


def x_main__mutmut_124() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    if _is_public_bind(args.host) and allow_public:
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


def x_main__mutmut_125() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
            None,
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


def x_main__mutmut_126() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
            None,
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


def x_main__mutmut_127() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_128() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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


def x_main__mutmut_129() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
            "XXRefusing to bind to public interface %s without explicit opt-in. XX"
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


def x_main__mutmut_130() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
            "refusing to bind to public interface %s without explicit opt-in. "
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


def x_main__mutmut_131() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
            "REFUSING TO BIND TO PUBLIC INTERFACE %S WITHOUT EXPLICIT OPT-IN. "
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


def x_main__mutmut_132() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
            "XXUse --allow-public-bind or set MCP_ALLOW_PUBLIC_BIND=1.XX",
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


def x_main__mutmut_133() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
            "use --allow-public-bind or set mcp_allow_public_bind=1.",
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


def x_main__mutmut_134() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
            "USE --ALLOW-PUBLIC-BIND OR SET MCP_ALLOW_PUBLIC_BIND=1.",
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


def x_main__mutmut_135() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
        raise SystemExit(None)

    host, port = _select_port(args.host, args.port, args.port_fallbacks, logger, diagnostics)
    start = time.time()
    app = importlib.import_module("src.mcp.server.facade_fastapi").APP
    elapsed = time.time() - start
    logger.info("Loaded APP in %.3fs", elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_136() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
        raise SystemExit(3)

    host, port = _select_port(args.host, args.port, args.port_fallbacks, logger, diagnostics)
    start = time.time()
    app = importlib.import_module("src.mcp.server.facade_fastapi").APP
    elapsed = time.time() - start
    logger.info("Loaded APP in %.3fs", elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_137() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    host, port = None
    start = time.time()
    app = importlib.import_module("src.mcp.server.facade_fastapi").APP
    elapsed = time.time() - start
    logger.info("Loaded APP in %.3fs", elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_138() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    host, port = _select_port(None, args.port, args.port_fallbacks, logger, diagnostics)
    start = time.time()
    app = importlib.import_module("src.mcp.server.facade_fastapi").APP
    elapsed = time.time() - start
    logger.info("Loaded APP in %.3fs", elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_139() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    host, port = _select_port(args.host, None, args.port_fallbacks, logger, diagnostics)
    start = time.time()
    app = importlib.import_module("src.mcp.server.facade_fastapi").APP
    elapsed = time.time() - start
    logger.info("Loaded APP in %.3fs", elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_140() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    host, port = _select_port(args.host, args.port, None, logger, diagnostics)
    start = time.time()
    app = importlib.import_module("src.mcp.server.facade_fastapi").APP
    elapsed = time.time() - start
    logger.info("Loaded APP in %.3fs", elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_141() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    host, port = _select_port(args.host, args.port, args.port_fallbacks, None, diagnostics)
    start = time.time()
    app = importlib.import_module("src.mcp.server.facade_fastapi").APP
    elapsed = time.time() - start
    logger.info("Loaded APP in %.3fs", elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_142() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    host, port = _select_port(args.host, args.port, args.port_fallbacks, logger, None)
    start = time.time()
    app = importlib.import_module("src.mcp.server.facade_fastapi").APP
    elapsed = time.time() - start
    logger.info("Loaded APP in %.3fs", elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_143() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    host, port = _select_port(args.port, args.port_fallbacks, logger, diagnostics)
    start = time.time()
    app = importlib.import_module("src.mcp.server.facade_fastapi").APP
    elapsed = time.time() - start
    logger.info("Loaded APP in %.3fs", elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_144() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    host, port = _select_port(args.host, args.port_fallbacks, logger, diagnostics)
    start = time.time()
    app = importlib.import_module("src.mcp.server.facade_fastapi").APP
    elapsed = time.time() - start
    logger.info("Loaded APP in %.3fs", elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_145() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    host, port = _select_port(args.host, args.port, logger, diagnostics)
    start = time.time()
    app = importlib.import_module("src.mcp.server.facade_fastapi").APP
    elapsed = time.time() - start
    logger.info("Loaded APP in %.3fs", elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_146() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    host, port = _select_port(args.host, args.port, args.port_fallbacks, diagnostics)
    start = time.time()
    app = importlib.import_module("src.mcp.server.facade_fastapi").APP
    elapsed = time.time() - start
    logger.info("Loaded APP in %.3fs", elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_147() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    host, port = _select_port(args.host, args.port, args.port_fallbacks, logger, )
    start = time.time()
    app = importlib.import_module("src.mcp.server.facade_fastapi").APP
    elapsed = time.time() - start
    logger.info("Loaded APP in %.3fs", elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_148() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    start = None
    app = importlib.import_module("src.mcp.server.facade_fastapi").APP
    elapsed = time.time() - start
    logger.info("Loaded APP in %.3fs", elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_149() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    app = None
    elapsed = time.time() - start
    logger.info("Loaded APP in %.3fs", elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_150() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    app = importlib.import_module(None).APP
    elapsed = time.time() - start
    logger.info("Loaded APP in %.3fs", elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_151() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    app = importlib.import_module("XXsrc.mcp.server.facade_fastapiXX").APP
    elapsed = time.time() - start
    logger.info("Loaded APP in %.3fs", elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_152() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    app = importlib.import_module("SRC.MCP.SERVER.FACADE_FASTAPI").APP
    elapsed = time.time() - start
    logger.info("Loaded APP in %.3fs", elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_153() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    elapsed = None
    logger.info("Loaded APP in %.3fs", elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_154() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    elapsed = time.time() + start
    logger.info("Loaded APP in %.3fs", elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_155() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    logger.info(None, elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_156() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    logger.info("Loaded APP in %.3fs", None)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_157() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    logger.info(elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_158() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    logger.info("Loaded APP in %.3fs", )
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_159() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    logger.info("XXLoaded APP in %.3fsXX", elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_160() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    logger.info("loaded app in %.3fs", elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_161() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    logger.info("LOADED APP IN %.3FS", elapsed)
    if diagnostics:
        print(f"Loaded APP in {elapsed:.3f}s", flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_162() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
        print(None, flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_163() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
        print(f"Loaded APP in {elapsed:.3f}s", flush=None)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_164() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
        print(flush=True)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_165() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
        print(f"Loaded APP in {elapsed:.3f}s", )
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_166() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
        print(f"Loaded APP in {elapsed:.3f}s", flush=False)
    logger.info("Starting MCP server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_167() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    logger.info(None, host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_168() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    logger.info("Starting MCP server on %s:%s", None, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_169() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    logger.info("Starting MCP server on %s:%s", host, None)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_170() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    logger.info(host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_171() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    logger.info("Starting MCP server on %s:%s", port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_172() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    logger.info("Starting MCP server on %s:%s", host, )

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_173() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    logger.info("XXStarting MCP server on %s:%sXX", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_174() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    logger.info("starting mcp server on %s:%s", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_175() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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
    logger.info("STARTING MCP SERVER ON %S:%S", host, port)

    uvicorn.run(app, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_176() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    uvicorn.run(None, host=host, port=port, log_level=args.log_level)


def x_main__mutmut_177() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    uvicorn.run(app, host=None, port=port, log_level=args.log_level)


def x_main__mutmut_178() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    uvicorn.run(app, host=host, port=None, log_level=args.log_level)


def x_main__mutmut_179() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    uvicorn.run(app, host=host, port=port, log_level=None)


def x_main__mutmut_180() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    uvicorn.run(host=host, port=port, log_level=args.log_level)


def x_main__mutmut_181() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    uvicorn.run(app, port=port, log_level=args.log_level)


def x_main__mutmut_182() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    uvicorn.run(app, host=host, log_level=args.log_level)


def x_main__mutmut_183() -> None:
    parser = argparse.ArgumentParser(description="Run MCP FastAPI server")
    parser.add_argument(
        "--host",
        default=os.environ.get("MCP_SERVER_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1 or MCP_SERVER_HOST).",
    )
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log-level", default="info")
    parser.add_argument("--port-fallbacks", type=int, default=3, help="Number of fallback ports to try")
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

    uvicorn.run(app, host=host, port=port, )

x_main__mutmut_mutants : ClassVar[MutantDict] = {
'x_main__mutmut_1': x_main__mutmut_1, 
    'x_main__mutmut_2': x_main__mutmut_2, 
    'x_main__mutmut_3': x_main__mutmut_3, 
    'x_main__mutmut_4': x_main__mutmut_4, 
    'x_main__mutmut_5': x_main__mutmut_5, 
    'x_main__mutmut_6': x_main__mutmut_6, 
    'x_main__mutmut_7': x_main__mutmut_7, 
    'x_main__mutmut_8': x_main__mutmut_8, 
    'x_main__mutmut_9': x_main__mutmut_9, 
    'x_main__mutmut_10': x_main__mutmut_10, 
    'x_main__mutmut_11': x_main__mutmut_11, 
    'x_main__mutmut_12': x_main__mutmut_12, 
    'x_main__mutmut_13': x_main__mutmut_13, 
    'x_main__mutmut_14': x_main__mutmut_14, 
    'x_main__mutmut_15': x_main__mutmut_15, 
    'x_main__mutmut_16': x_main__mutmut_16, 
    'x_main__mutmut_17': x_main__mutmut_17, 
    'x_main__mutmut_18': x_main__mutmut_18, 
    'x_main__mutmut_19': x_main__mutmut_19, 
    'x_main__mutmut_20': x_main__mutmut_20, 
    'x_main__mutmut_21': x_main__mutmut_21, 
    'x_main__mutmut_22': x_main__mutmut_22, 
    'x_main__mutmut_23': x_main__mutmut_23, 
    'x_main__mutmut_24': x_main__mutmut_24, 
    'x_main__mutmut_25': x_main__mutmut_25, 
    'x_main__mutmut_26': x_main__mutmut_26, 
    'x_main__mutmut_27': x_main__mutmut_27, 
    'x_main__mutmut_28': x_main__mutmut_28, 
    'x_main__mutmut_29': x_main__mutmut_29, 
    'x_main__mutmut_30': x_main__mutmut_30, 
    'x_main__mutmut_31': x_main__mutmut_31, 
    'x_main__mutmut_32': x_main__mutmut_32, 
    'x_main__mutmut_33': x_main__mutmut_33, 
    'x_main__mutmut_34': x_main__mutmut_34, 
    'x_main__mutmut_35': x_main__mutmut_35, 
    'x_main__mutmut_36': x_main__mutmut_36, 
    'x_main__mutmut_37': x_main__mutmut_37, 
    'x_main__mutmut_38': x_main__mutmut_38, 
    'x_main__mutmut_39': x_main__mutmut_39, 
    'x_main__mutmut_40': x_main__mutmut_40, 
    'x_main__mutmut_41': x_main__mutmut_41, 
    'x_main__mutmut_42': x_main__mutmut_42, 
    'x_main__mutmut_43': x_main__mutmut_43, 
    'x_main__mutmut_44': x_main__mutmut_44, 
    'x_main__mutmut_45': x_main__mutmut_45, 
    'x_main__mutmut_46': x_main__mutmut_46, 
    'x_main__mutmut_47': x_main__mutmut_47, 
    'x_main__mutmut_48': x_main__mutmut_48, 
    'x_main__mutmut_49': x_main__mutmut_49, 
    'x_main__mutmut_50': x_main__mutmut_50, 
    'x_main__mutmut_51': x_main__mutmut_51, 
    'x_main__mutmut_52': x_main__mutmut_52, 
    'x_main__mutmut_53': x_main__mutmut_53, 
    'x_main__mutmut_54': x_main__mutmut_54, 
    'x_main__mutmut_55': x_main__mutmut_55, 
    'x_main__mutmut_56': x_main__mutmut_56, 
    'x_main__mutmut_57': x_main__mutmut_57, 
    'x_main__mutmut_58': x_main__mutmut_58, 
    'x_main__mutmut_59': x_main__mutmut_59, 
    'x_main__mutmut_60': x_main__mutmut_60, 
    'x_main__mutmut_61': x_main__mutmut_61, 
    'x_main__mutmut_62': x_main__mutmut_62, 
    'x_main__mutmut_63': x_main__mutmut_63, 
    'x_main__mutmut_64': x_main__mutmut_64, 
    'x_main__mutmut_65': x_main__mutmut_65, 
    'x_main__mutmut_66': x_main__mutmut_66, 
    'x_main__mutmut_67': x_main__mutmut_67, 
    'x_main__mutmut_68': x_main__mutmut_68, 
    'x_main__mutmut_69': x_main__mutmut_69, 
    'x_main__mutmut_70': x_main__mutmut_70, 
    'x_main__mutmut_71': x_main__mutmut_71, 
    'x_main__mutmut_72': x_main__mutmut_72, 
    'x_main__mutmut_73': x_main__mutmut_73, 
    'x_main__mutmut_74': x_main__mutmut_74, 
    'x_main__mutmut_75': x_main__mutmut_75, 
    'x_main__mutmut_76': x_main__mutmut_76, 
    'x_main__mutmut_77': x_main__mutmut_77, 
    'x_main__mutmut_78': x_main__mutmut_78, 
    'x_main__mutmut_79': x_main__mutmut_79, 
    'x_main__mutmut_80': x_main__mutmut_80, 
    'x_main__mutmut_81': x_main__mutmut_81, 
    'x_main__mutmut_82': x_main__mutmut_82, 
    'x_main__mutmut_83': x_main__mutmut_83, 
    'x_main__mutmut_84': x_main__mutmut_84, 
    'x_main__mutmut_85': x_main__mutmut_85, 
    'x_main__mutmut_86': x_main__mutmut_86, 
    'x_main__mutmut_87': x_main__mutmut_87, 
    'x_main__mutmut_88': x_main__mutmut_88, 
    'x_main__mutmut_89': x_main__mutmut_89, 
    'x_main__mutmut_90': x_main__mutmut_90, 
    'x_main__mutmut_91': x_main__mutmut_91, 
    'x_main__mutmut_92': x_main__mutmut_92, 
    'x_main__mutmut_93': x_main__mutmut_93, 
    'x_main__mutmut_94': x_main__mutmut_94, 
    'x_main__mutmut_95': x_main__mutmut_95, 
    'x_main__mutmut_96': x_main__mutmut_96, 
    'x_main__mutmut_97': x_main__mutmut_97, 
    'x_main__mutmut_98': x_main__mutmut_98, 
    'x_main__mutmut_99': x_main__mutmut_99, 
    'x_main__mutmut_100': x_main__mutmut_100, 
    'x_main__mutmut_101': x_main__mutmut_101, 
    'x_main__mutmut_102': x_main__mutmut_102, 
    'x_main__mutmut_103': x_main__mutmut_103, 
    'x_main__mutmut_104': x_main__mutmut_104, 
    'x_main__mutmut_105': x_main__mutmut_105, 
    'x_main__mutmut_106': x_main__mutmut_106, 
    'x_main__mutmut_107': x_main__mutmut_107, 
    'x_main__mutmut_108': x_main__mutmut_108, 
    'x_main__mutmut_109': x_main__mutmut_109, 
    'x_main__mutmut_110': x_main__mutmut_110, 
    'x_main__mutmut_111': x_main__mutmut_111, 
    'x_main__mutmut_112': x_main__mutmut_112, 
    'x_main__mutmut_113': x_main__mutmut_113, 
    'x_main__mutmut_114': x_main__mutmut_114, 
    'x_main__mutmut_115': x_main__mutmut_115, 
    'x_main__mutmut_116': x_main__mutmut_116, 
    'x_main__mutmut_117': x_main__mutmut_117, 
    'x_main__mutmut_118': x_main__mutmut_118, 
    'x_main__mutmut_119': x_main__mutmut_119, 
    'x_main__mutmut_120': x_main__mutmut_120, 
    'x_main__mutmut_121': x_main__mutmut_121, 
    'x_main__mutmut_122': x_main__mutmut_122, 
    'x_main__mutmut_123': x_main__mutmut_123, 
    'x_main__mutmut_124': x_main__mutmut_124, 
    'x_main__mutmut_125': x_main__mutmut_125, 
    'x_main__mutmut_126': x_main__mutmut_126, 
    'x_main__mutmut_127': x_main__mutmut_127, 
    'x_main__mutmut_128': x_main__mutmut_128, 
    'x_main__mutmut_129': x_main__mutmut_129, 
    'x_main__mutmut_130': x_main__mutmut_130, 
    'x_main__mutmut_131': x_main__mutmut_131, 
    'x_main__mutmut_132': x_main__mutmut_132, 
    'x_main__mutmut_133': x_main__mutmut_133, 
    'x_main__mutmut_134': x_main__mutmut_134, 
    'x_main__mutmut_135': x_main__mutmut_135, 
    'x_main__mutmut_136': x_main__mutmut_136, 
    'x_main__mutmut_137': x_main__mutmut_137, 
    'x_main__mutmut_138': x_main__mutmut_138, 
    'x_main__mutmut_139': x_main__mutmut_139, 
    'x_main__mutmut_140': x_main__mutmut_140, 
    'x_main__mutmut_141': x_main__mutmut_141, 
    'x_main__mutmut_142': x_main__mutmut_142, 
    'x_main__mutmut_143': x_main__mutmut_143, 
    'x_main__mutmut_144': x_main__mutmut_144, 
    'x_main__mutmut_145': x_main__mutmut_145, 
    'x_main__mutmut_146': x_main__mutmut_146, 
    'x_main__mutmut_147': x_main__mutmut_147, 
    'x_main__mutmut_148': x_main__mutmut_148, 
    'x_main__mutmut_149': x_main__mutmut_149, 
    'x_main__mutmut_150': x_main__mutmut_150, 
    'x_main__mutmut_151': x_main__mutmut_151, 
    'x_main__mutmut_152': x_main__mutmut_152, 
    'x_main__mutmut_153': x_main__mutmut_153, 
    'x_main__mutmut_154': x_main__mutmut_154, 
    'x_main__mutmut_155': x_main__mutmut_155, 
    'x_main__mutmut_156': x_main__mutmut_156, 
    'x_main__mutmut_157': x_main__mutmut_157, 
    'x_main__mutmut_158': x_main__mutmut_158, 
    'x_main__mutmut_159': x_main__mutmut_159, 
    'x_main__mutmut_160': x_main__mutmut_160, 
    'x_main__mutmut_161': x_main__mutmut_161, 
    'x_main__mutmut_162': x_main__mutmut_162, 
    'x_main__mutmut_163': x_main__mutmut_163, 
    'x_main__mutmut_164': x_main__mutmut_164, 
    'x_main__mutmut_165': x_main__mutmut_165, 
    'x_main__mutmut_166': x_main__mutmut_166, 
    'x_main__mutmut_167': x_main__mutmut_167, 
    'x_main__mutmut_168': x_main__mutmut_168, 
    'x_main__mutmut_169': x_main__mutmut_169, 
    'x_main__mutmut_170': x_main__mutmut_170, 
    'x_main__mutmut_171': x_main__mutmut_171, 
    'x_main__mutmut_172': x_main__mutmut_172, 
    'x_main__mutmut_173': x_main__mutmut_173, 
    'x_main__mutmut_174': x_main__mutmut_174, 
    'x_main__mutmut_175': x_main__mutmut_175, 
    'x_main__mutmut_176': x_main__mutmut_176, 
    'x_main__mutmut_177': x_main__mutmut_177, 
    'x_main__mutmut_178': x_main__mutmut_178, 
    'x_main__mutmut_179': x_main__mutmut_179, 
    'x_main__mutmut_180': x_main__mutmut_180, 
    'x_main__mutmut_181': x_main__mutmut_181, 
    'x_main__mutmut_182': x_main__mutmut_182, 
    'x_main__mutmut_183': x_main__mutmut_183
}

def main(*args, **kwargs):
    result = _mutmut_trampoline(x_main__mutmut_orig, x_main__mutmut_mutants, args, kwargs)
    return result 

main.__signature__ = _mutmut_signature(x_main__mutmut_orig)
x_main__mutmut_orig.__name__ = 'x_main'


def x__select_port__mutmut_orig(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_1(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = None
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_2(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(None, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_3(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, None)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_4(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_5(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, )
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_6(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(1, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_7(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(None):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_8(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts - 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_9(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 2):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_10(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = None
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_11(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port - offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_12(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = None
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_13(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(None, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_14(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, None)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_15(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_16(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, )
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_17(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning(None, port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_18(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", None, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_19(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, None, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_20(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, None)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_21(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning(port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_22(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_23(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_24(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, )
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_25(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("XXPort %s unavailable (%s). Falling back to %s.XX", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_26(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("port %s unavailable (%s). falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_27(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("PORT %S UNAVAILABLE (%S). FALLING BACK TO %S.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_28(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(None, flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_29(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=None)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_30(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_31(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", )
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_32(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=False)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_33(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning(None, candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_34(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", None, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_35(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, None, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_36(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, None)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_37(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning(candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_38(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_39(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_40(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, )
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_41(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("XXPort %s unavailable on host %s (%s).XX", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_42(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_43(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("PORT %S UNAVAILABLE ON HOST %S (%S).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=True)
    return host, port


def x__select_port__mutmut_44(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(None, flush=True)
    return host, port


def x__select_port__mutmut_45(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=None)
    return host, port


def x__select_port__mutmut_46(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(flush=True)
    return host, port


def x__select_port__mutmut_47(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", )
    return host, port


def x__select_port__mutmut_48(host: str, port: int, fallbacks: int, logger: logging.Logger, diagnostics: bool) -> tuple[str, int]:
    attempts = max(0, fallbacks)
    for offset in range(attempts + 1):
        candidate = port + offset
        ok, reason = _check_bind(host, candidate)
        if ok:
            if offset:
                logger.warning("Port %s unavailable (%s). Falling back to %s.", port, reason, candidate)
                if diagnostics:
                    print(f"Port {port} unavailable ({reason}). Falling back to {candidate}.", flush=True)
            return host, candidate
        logger.warning("Port %s unavailable on host %s (%s).", candidate, host, reason)
        if diagnostics:
            print(f"Port {candidate} unavailable on host {host} ({reason}).", flush=False)
    return host, port

x__select_port__mutmut_mutants : ClassVar[MutantDict] = {
'x__select_port__mutmut_1': x__select_port__mutmut_1, 
    'x__select_port__mutmut_2': x__select_port__mutmut_2, 
    'x__select_port__mutmut_3': x__select_port__mutmut_3, 
    'x__select_port__mutmut_4': x__select_port__mutmut_4, 
    'x__select_port__mutmut_5': x__select_port__mutmut_5, 
    'x__select_port__mutmut_6': x__select_port__mutmut_6, 
    'x__select_port__mutmut_7': x__select_port__mutmut_7, 
    'x__select_port__mutmut_8': x__select_port__mutmut_8, 
    'x__select_port__mutmut_9': x__select_port__mutmut_9, 
    'x__select_port__mutmut_10': x__select_port__mutmut_10, 
    'x__select_port__mutmut_11': x__select_port__mutmut_11, 
    'x__select_port__mutmut_12': x__select_port__mutmut_12, 
    'x__select_port__mutmut_13': x__select_port__mutmut_13, 
    'x__select_port__mutmut_14': x__select_port__mutmut_14, 
    'x__select_port__mutmut_15': x__select_port__mutmut_15, 
    'x__select_port__mutmut_16': x__select_port__mutmut_16, 
    'x__select_port__mutmut_17': x__select_port__mutmut_17, 
    'x__select_port__mutmut_18': x__select_port__mutmut_18, 
    'x__select_port__mutmut_19': x__select_port__mutmut_19, 
    'x__select_port__mutmut_20': x__select_port__mutmut_20, 
    'x__select_port__mutmut_21': x__select_port__mutmut_21, 
    'x__select_port__mutmut_22': x__select_port__mutmut_22, 
    'x__select_port__mutmut_23': x__select_port__mutmut_23, 
    'x__select_port__mutmut_24': x__select_port__mutmut_24, 
    'x__select_port__mutmut_25': x__select_port__mutmut_25, 
    'x__select_port__mutmut_26': x__select_port__mutmut_26, 
    'x__select_port__mutmut_27': x__select_port__mutmut_27, 
    'x__select_port__mutmut_28': x__select_port__mutmut_28, 
    'x__select_port__mutmut_29': x__select_port__mutmut_29, 
    'x__select_port__mutmut_30': x__select_port__mutmut_30, 
    'x__select_port__mutmut_31': x__select_port__mutmut_31, 
    'x__select_port__mutmut_32': x__select_port__mutmut_32, 
    'x__select_port__mutmut_33': x__select_port__mutmut_33, 
    'x__select_port__mutmut_34': x__select_port__mutmut_34, 
    'x__select_port__mutmut_35': x__select_port__mutmut_35, 
    'x__select_port__mutmut_36': x__select_port__mutmut_36, 
    'x__select_port__mutmut_37': x__select_port__mutmut_37, 
    'x__select_port__mutmut_38': x__select_port__mutmut_38, 
    'x__select_port__mutmut_39': x__select_port__mutmut_39, 
    'x__select_port__mutmut_40': x__select_port__mutmut_40, 
    'x__select_port__mutmut_41': x__select_port__mutmut_41, 
    'x__select_port__mutmut_42': x__select_port__mutmut_42, 
    'x__select_port__mutmut_43': x__select_port__mutmut_43, 
    'x__select_port__mutmut_44': x__select_port__mutmut_44, 
    'x__select_port__mutmut_45': x__select_port__mutmut_45, 
    'x__select_port__mutmut_46': x__select_port__mutmut_46, 
    'x__select_port__mutmut_47': x__select_port__mutmut_47, 
    'x__select_port__mutmut_48': x__select_port__mutmut_48
}

def _select_port(*args, **kwargs):
    result = _mutmut_trampoline(x__select_port__mutmut_orig, x__select_port__mutmut_mutants, args, kwargs)
    return result 

_select_port.__signature__ = _mutmut_signature(x__select_port__mutmut_orig)
x__select_port__mutmut_orig.__name__ = 'x__select_port'


def x__is_public_bind__mutmut_orig(host: str) -> bool:
    return host in {"0.0.0.0", "::"}


def x__is_public_bind__mutmut_1(host: str) -> bool:
    return host not in {"0.0.0.0", "::"}


def x__is_public_bind__mutmut_2(host: str) -> bool:
    return host in {"XX0.0.0.0XX", "::"}


def x__is_public_bind__mutmut_3(host: str) -> bool:
    return host in {"0.0.0.0", "XX::XX"}

x__is_public_bind__mutmut_mutants : ClassVar[MutantDict] = {
'x__is_public_bind__mutmut_1': x__is_public_bind__mutmut_1, 
    'x__is_public_bind__mutmut_2': x__is_public_bind__mutmut_2, 
    'x__is_public_bind__mutmut_3': x__is_public_bind__mutmut_3
}

def _is_public_bind(*args, **kwargs):
    result = _mutmut_trampoline(x__is_public_bind__mutmut_orig, x__is_public_bind__mutmut_mutants, args, kwargs)
    return result 

_is_public_bind.__signature__ = _mutmut_signature(x__is_public_bind__mutmut_orig)
x__is_public_bind__mutmut_orig.__name__ = 'x__is_public_bind'


def x__check_bind__mutmut_orig(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug("Exception caught, returning", exc_info=True)
        return False, str(exc)


def x__check_bind__mutmut_1(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = None
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug("Exception caught, returning", exc_info=True)
        return False, str(exc)


def x__check_bind__mutmut_2(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(None, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug("Exception caught, returning", exc_info=True)
        return False, str(exc)


def x__check_bind__mutmut_3(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.AF_INET, None)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug("Exception caught, returning", exc_info=True)
        return False, str(exc)


def x__check_bind__mutmut_4(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug("Exception caught, returning", exc_info=True)
        return False, str(exc)


def x__check_bind__mutmut_5(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.AF_INET, )
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug("Exception caught, returning", exc_info=True)
        return False, str(exc)


def x__check_bind__mutmut_6(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(None, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug("Exception caught, returning", exc_info=True)
        return False, str(exc)


def x__check_bind__mutmut_7(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, None, 1)
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug("Exception caught, returning", exc_info=True)
        return False, str(exc)


def x__check_bind__mutmut_8(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, None)
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug("Exception caught, returning", exc_info=True)
        return False, str(exc)


def x__check_bind__mutmut_9(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug("Exception caught, returning", exc_info=True)
        return False, str(exc)


def x__check_bind__mutmut_10(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, 1)
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug("Exception caught, returning", exc_info=True)
        return False, str(exc)


def x__check_bind__mutmut_11(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, )
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug("Exception caught, returning", exc_info=True)
        return False, str(exc)


def x__check_bind__mutmut_12(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 2)
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug("Exception caught, returning", exc_info=True)
        return False, str(exc)


def x__check_bind__mutmut_13(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(None)
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug("Exception caught, returning", exc_info=True)
        return False, str(exc)


def x__check_bind__mutmut_14(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.close()
        return False, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug("Exception caught, returning", exc_info=True)
        return False, str(exc)


def x__check_bind__mutmut_15(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(None)
        logger.debug("Exception caught, returning", exc_info=True)
        return False, str(exc)


def x__check_bind__mutmut_16(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug(None, exc_info=True)
        return False, str(exc)


def x__check_bind__mutmut_17(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug("Exception caught, returning", exc_info=None)
        return False, str(exc)


def x__check_bind__mutmut_18(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug(exc_info=True)
        return False, str(exc)


def x__check_bind__mutmut_19(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug("Exception caught, returning", )
        return False, str(exc)


def x__check_bind__mutmut_20(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug("XXException caught, returningXX", exc_info=True)
        return False, str(exc)


def x__check_bind__mutmut_21(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug("exception caught, returning", exc_info=True)
        return False, str(exc)


def x__check_bind__mutmut_22(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug("EXCEPTION CAUGHT, RETURNING", exc_info=True)
        return False, str(exc)


def x__check_bind__mutmut_23(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug("Exception caught, returning", exc_info=False)
        return False, str(exc)


def x__check_bind__mutmut_24(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug("Exception caught, returning", exc_info=True)
        return True, str(exc)


def x__check_bind__mutmut_25(host: str, port: int) -> tuple[bool, Optional[str]]:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.close()
        return True, None
    except OSError as exc:
        logger.debug(f"OSError: {exc}")
        logger.debug("Exception caught, returning", exc_info=True)
        return False, str(None)

x__check_bind__mutmut_mutants : ClassVar[MutantDict] = {
'x__check_bind__mutmut_1': x__check_bind__mutmut_1, 
    'x__check_bind__mutmut_2': x__check_bind__mutmut_2, 
    'x__check_bind__mutmut_3': x__check_bind__mutmut_3, 
    'x__check_bind__mutmut_4': x__check_bind__mutmut_4, 
    'x__check_bind__mutmut_5': x__check_bind__mutmut_5, 
    'x__check_bind__mutmut_6': x__check_bind__mutmut_6, 
    'x__check_bind__mutmut_7': x__check_bind__mutmut_7, 
    'x__check_bind__mutmut_8': x__check_bind__mutmut_8, 
    'x__check_bind__mutmut_9': x__check_bind__mutmut_9, 
    'x__check_bind__mutmut_10': x__check_bind__mutmut_10, 
    'x__check_bind__mutmut_11': x__check_bind__mutmut_11, 
    'x__check_bind__mutmut_12': x__check_bind__mutmut_12, 
    'x__check_bind__mutmut_13': x__check_bind__mutmut_13, 
    'x__check_bind__mutmut_14': x__check_bind__mutmut_14, 
    'x__check_bind__mutmut_15': x__check_bind__mutmut_15, 
    'x__check_bind__mutmut_16': x__check_bind__mutmut_16, 
    'x__check_bind__mutmut_17': x__check_bind__mutmut_17, 
    'x__check_bind__mutmut_18': x__check_bind__mutmut_18, 
    'x__check_bind__mutmut_19': x__check_bind__mutmut_19, 
    'x__check_bind__mutmut_20': x__check_bind__mutmut_20, 
    'x__check_bind__mutmut_21': x__check_bind__mutmut_21, 
    'x__check_bind__mutmut_22': x__check_bind__mutmut_22, 
    'x__check_bind__mutmut_23': x__check_bind__mutmut_23, 
    'x__check_bind__mutmut_24': x__check_bind__mutmut_24, 
    'x__check_bind__mutmut_25': x__check_bind__mutmut_25
}

def _check_bind(*args, **kwargs):
    result = _mutmut_trampoline(x__check_bind__mutmut_orig, x__check_bind__mutmut_mutants, args, kwargs)
    return result 

_check_bind.__signature__ = _mutmut_signature(x__check_bind__mutmut_orig)
x__check_bind__mutmut_orig.__name__ = 'x__check_bind'


if __name__ == "__main__":
    main()
