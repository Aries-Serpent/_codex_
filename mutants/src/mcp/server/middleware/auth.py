"""
Auth Module

This module provides functionality for auth.

Usage:
    from middleware.auth import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import os

# Simple in-memory mapping for dev usage. Production should consult a secret manager.
DEV_KEYS: dict[str, dict] = {
    os.environ.get("DEV_API_KEY", "dev-key-1"): {"tenant": "dev-tenant", "scopes": ["read", "write"]},
}
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


class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """
    Dev-friendly API key / Bearer Token middleware.
    - Checks Authorization: Bearer <key> or X-API-Key header.
    - Injects request.state.principal = {"tenant": ..., "api_key": key, "scopes": [...]}.
    - Unknown keys: reject with 401 in dev to avoid accidental calls.
    """

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_orig(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_1(self, request: Request, call_next):
        api_key = ""
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_2(self, request: Request, call_next):
        api_key = None
        auth = None
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_3(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get(None)
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_4(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("XXauthorizationXX")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_5(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("AUTHORIZATION")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_6(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth or auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_7(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith(None):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_8(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.upper().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_9(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("XXbearer XX"):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_10(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("BEARER "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_11(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = None
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_12(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(None, 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_13(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", None)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_14(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_15(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", )[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_16(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.rsplit(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_17(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split("XX XX", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_18(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 2)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_19(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[2].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_20(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_21(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = None

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_22(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get(None)

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_23(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("XXx-api-keyXX")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_24(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("X-API-KEY")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_25(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = None
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_26(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(None)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_27(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key or principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_28(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is not None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_29(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response(None, status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_30(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=None)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_31(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response(status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_32(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", )

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_33(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("XXUnauthorizedXX", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_34(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_35(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("UNAUTHORIZED", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_36(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=402)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_37(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = None
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_38(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal and {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_39(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"XXtenantXX": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_40(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"TENANT": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_41(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "XXanonymousXX", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_42(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "ANONYMOUS", "api_key": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_43(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "XXapi_keyXX": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_44(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "API_KEY": api_key, "scopes": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_45(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "XXscopesXX": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_46(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "SCOPES": []}
        return await call_next(request)

    async def xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_47(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key)
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {"tenant": "anonymous", "api_key": api_key, "scopes": []}
        return await call_next(None)
    
    xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_1': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_1, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_2': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_2, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_3': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_3, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_4': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_4, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_5': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_5, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_6': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_6, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_7': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_7, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_8': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_8, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_9': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_9, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_10': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_10, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_11': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_11, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_12': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_12, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_13': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_13, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_14': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_14, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_15': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_15, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_16': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_16, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_17': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_17, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_18': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_18, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_19': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_19, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_20': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_20, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_21': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_21, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_22': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_22, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_23': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_23, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_24': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_24, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_25': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_25, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_26': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_26, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_27': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_27, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_28': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_28, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_29': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_29, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_30': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_30, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_31': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_31, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_32': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_32, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_33': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_33, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_34': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_34, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_35': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_35, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_36': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_36, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_37': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_37, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_38': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_38, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_39': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_39, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_40': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_40, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_41': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_41, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_42': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_42, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_43': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_43, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_44': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_44, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_45': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_45, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_46': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_46, 
        'xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_47': xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_47
    }
    
    def dispatch(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_orig"), object.__getattribute__(self, "xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_mutants"), args, kwargs, self)
        return result 
    
    dispatch.__signature__ = _mutmut_signature(xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_orig)
    xǁAPIKeyAuthMiddlewareǁdispatch__mutmut_orig.__name__ = 'xǁAPIKeyAuthMiddlewareǁdispatch'
