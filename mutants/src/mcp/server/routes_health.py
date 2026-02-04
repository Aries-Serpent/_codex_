"""
Routes Health Module

This module provides functionality for routes health.

Usage:
    from server.routes_health import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .adapter_loader import load_adapter
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


def register_health_routes(app: FastAPI, adapter_loader_fn=load_adapter) -> None:
    @app.get("/health")
    async def health_root():
        adapter, adapter_path = adapter_loader_fn()
        try:
            adapter_status = adapter.health_check()
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            adapter_status = {"status": "degraded"}
        payload = {
            "service": "mcp-facade",
            "status": "ok",
            "adapter": adapter_path,
            "adapter_status": adapter_status,
        }
        return JSONResponse(content=payload)

    @app.get("/mcp/v1/health")
    async def mcp_health():
        adapter, adapter_path = adapter_loader_fn()
        try:
            adapter_status = adapter.health_check()
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            adapter_status = {"status": "degraded"}
        return JSONResponse(content={"status": "ok", "adapter": adapter_path, "adapter_status": adapter_status})
