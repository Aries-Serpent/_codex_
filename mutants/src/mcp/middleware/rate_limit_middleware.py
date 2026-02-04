"""
Rate Limit Middleware Module

This module provides functionality for rate limit middleware.

Usage:
    from middleware.rate_limit_middleware import ...

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
import time

# In-memory token-bucket per principal (scoped to process). Replace with Redis for multi-process.
_BUCKETS: dict[str, dict] = {}
DEFAULT_RATE = 5
BURST = 10
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


def x__get_bucket__mutmut_orig(principal: str, burst: int):
    b = _BUCKETS.setdefault(principal, {"tokens": burst, "last": time.time()})
    return b


def x__get_bucket__mutmut_1(principal: str, burst: int):
    b = None
    return b


def x__get_bucket__mutmut_2(principal: str, burst: int):
    b = _BUCKETS.setdefault(None, {"tokens": burst, "last": time.time()})
    return b


def x__get_bucket__mutmut_3(principal: str, burst: int):
    b = _BUCKETS.setdefault(principal, None)
    return b


def x__get_bucket__mutmut_4(principal: str, burst: int):
    b = _BUCKETS.setdefault({"tokens": burst, "last": time.time()})
    return b


def x__get_bucket__mutmut_5(principal: str, burst: int):
    b = _BUCKETS.setdefault(principal, )
    return b


def x__get_bucket__mutmut_6(principal: str, burst: int):
    b = _BUCKETS.setdefault(principal, {"XXtokensXX": burst, "last": time.time()})
    return b


def x__get_bucket__mutmut_7(principal: str, burst: int):
    b = _BUCKETS.setdefault(principal, {"TOKENS": burst, "last": time.time()})
    return b


def x__get_bucket__mutmut_8(principal: str, burst: int):
    b = _BUCKETS.setdefault(principal, {"tokens": burst, "XXlastXX": time.time()})
    return b


def x__get_bucket__mutmut_9(principal: str, burst: int):
    b = _BUCKETS.setdefault(principal, {"tokens": burst, "LAST": time.time()})
    return b

x__get_bucket__mutmut_mutants : ClassVar[MutantDict] = {
'x__get_bucket__mutmut_1': x__get_bucket__mutmut_1, 
    'x__get_bucket__mutmut_2': x__get_bucket__mutmut_2, 
    'x__get_bucket__mutmut_3': x__get_bucket__mutmut_3, 
    'x__get_bucket__mutmut_4': x__get_bucket__mutmut_4, 
    'x__get_bucket__mutmut_5': x__get_bucket__mutmut_5, 
    'x__get_bucket__mutmut_6': x__get_bucket__mutmut_6, 
    'x__get_bucket__mutmut_7': x__get_bucket__mutmut_7, 
    'x__get_bucket__mutmut_8': x__get_bucket__mutmut_8, 
    'x__get_bucket__mutmut_9': x__get_bucket__mutmut_9
}

def _get_bucket(*args, **kwargs):
    result = _mutmut_trampoline(x__get_bucket__mutmut_orig, x__get_bucket__mutmut_mutants, args, kwargs)
    return result 

_get_bucket.__signature__ = _mutmut_signature(x__get_bucket__mutmut_orig)
x__get_bucket__mutmut_orig.__name__ = 'x__get_bucket'


def clear_buckets() -> None:
    _BUCKETS.clear()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Very small in-memory rate limiter. Suitable for dev/testing only.
    - principal is taken from request.state.principal.api_key (fall back to 'anonymous')
    - Returns 429 when bucket empty.
    """

    def xǁRateLimitMiddlewareǁ__init____mutmut_orig(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("os").environ.get("RATE_LIMIT_RATE", str(DEFAULT_RATE))))
        if burst is None:
            burst = int(float(__import__("os").environ.get("RATE_LIMIT_BURST", str(BURST))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_1(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(None)
        if rate is None:
            rate = int(float(__import__("os").environ.get("RATE_LIMIT_RATE", str(DEFAULT_RATE))))
        if burst is None:
            burst = int(float(__import__("os").environ.get("RATE_LIMIT_BURST", str(BURST))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_2(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is not None:
            rate = int(float(__import__("os").environ.get("RATE_LIMIT_RATE", str(DEFAULT_RATE))))
        if burst is None:
            burst = int(float(__import__("os").environ.get("RATE_LIMIT_BURST", str(BURST))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_3(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = None
        if burst is None:
            burst = int(float(__import__("os").environ.get("RATE_LIMIT_BURST", str(BURST))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_4(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(None)
        if burst is None:
            burst = int(float(__import__("os").environ.get("RATE_LIMIT_BURST", str(BURST))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_5(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(None))
        if burst is None:
            burst = int(float(__import__("os").environ.get("RATE_LIMIT_BURST", str(BURST))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_6(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("os").environ.get(None, str(DEFAULT_RATE))))
        if burst is None:
            burst = int(float(__import__("os").environ.get("RATE_LIMIT_BURST", str(BURST))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_7(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("os").environ.get("RATE_LIMIT_RATE", None)))
        if burst is None:
            burst = int(float(__import__("os").environ.get("RATE_LIMIT_BURST", str(BURST))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_8(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("os").environ.get(str(DEFAULT_RATE))))
        if burst is None:
            burst = int(float(__import__("os").environ.get("RATE_LIMIT_BURST", str(BURST))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_9(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("os").environ.get("RATE_LIMIT_RATE", )))
        if burst is None:
            burst = int(float(__import__("os").environ.get("RATE_LIMIT_BURST", str(BURST))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_10(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__(None).environ.get("RATE_LIMIT_RATE", str(DEFAULT_RATE))))
        if burst is None:
            burst = int(float(__import__("os").environ.get("RATE_LIMIT_BURST", str(BURST))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_11(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("XXosXX").environ.get("RATE_LIMIT_RATE", str(DEFAULT_RATE))))
        if burst is None:
            burst = int(float(__import__("os").environ.get("RATE_LIMIT_BURST", str(BURST))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_12(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("OS").environ.get("RATE_LIMIT_RATE", str(DEFAULT_RATE))))
        if burst is None:
            burst = int(float(__import__("os").environ.get("RATE_LIMIT_BURST", str(BURST))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_13(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("os").environ.get("XXRATE_LIMIT_RATEXX", str(DEFAULT_RATE))))
        if burst is None:
            burst = int(float(__import__("os").environ.get("RATE_LIMIT_BURST", str(BURST))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_14(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("os").environ.get("rate_limit_rate", str(DEFAULT_RATE))))
        if burst is None:
            burst = int(float(__import__("os").environ.get("RATE_LIMIT_BURST", str(BURST))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_15(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("os").environ.get("RATE_LIMIT_RATE", str(None))))
        if burst is None:
            burst = int(float(__import__("os").environ.get("RATE_LIMIT_BURST", str(BURST))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_16(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("os").environ.get("RATE_LIMIT_RATE", str(DEFAULT_RATE))))
        if burst is not None:
            burst = int(float(__import__("os").environ.get("RATE_LIMIT_BURST", str(BURST))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_17(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("os").environ.get("RATE_LIMIT_RATE", str(DEFAULT_RATE))))
        if burst is None:
            burst = None
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_18(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("os").environ.get("RATE_LIMIT_RATE", str(DEFAULT_RATE))))
        if burst is None:
            burst = int(None)
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_19(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("os").environ.get("RATE_LIMIT_RATE", str(DEFAULT_RATE))))
        if burst is None:
            burst = int(float(None))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_20(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("os").environ.get("RATE_LIMIT_RATE", str(DEFAULT_RATE))))
        if burst is None:
            burst = int(float(__import__("os").environ.get(None, str(BURST))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_21(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("os").environ.get("RATE_LIMIT_RATE", str(DEFAULT_RATE))))
        if burst is None:
            burst = int(float(__import__("os").environ.get("RATE_LIMIT_BURST", None)))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_22(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("os").environ.get("RATE_LIMIT_RATE", str(DEFAULT_RATE))))
        if burst is None:
            burst = int(float(__import__("os").environ.get(str(BURST))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_23(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("os").environ.get("RATE_LIMIT_RATE", str(DEFAULT_RATE))))
        if burst is None:
            burst = int(float(__import__("os").environ.get("RATE_LIMIT_BURST", )))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_24(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("os").environ.get("RATE_LIMIT_RATE", str(DEFAULT_RATE))))
        if burst is None:
            burst = int(float(__import__(None).environ.get("RATE_LIMIT_BURST", str(BURST))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_25(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("os").environ.get("RATE_LIMIT_RATE", str(DEFAULT_RATE))))
        if burst is None:
            burst = int(float(__import__("XXosXX").environ.get("RATE_LIMIT_BURST", str(BURST))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_26(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("os").environ.get("RATE_LIMIT_RATE", str(DEFAULT_RATE))))
        if burst is None:
            burst = int(float(__import__("OS").environ.get("RATE_LIMIT_BURST", str(BURST))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_27(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("os").environ.get("RATE_LIMIT_RATE", str(DEFAULT_RATE))))
        if burst is None:
            burst = int(float(__import__("os").environ.get("XXRATE_LIMIT_BURSTXX", str(BURST))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_28(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("os").environ.get("RATE_LIMIT_RATE", str(DEFAULT_RATE))))
        if burst is None:
            burst = int(float(__import__("os").environ.get("rate_limit_burst", str(BURST))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_29(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("os").environ.get("RATE_LIMIT_RATE", str(DEFAULT_RATE))))
        if burst is None:
            burst = int(float(__import__("os").environ.get("RATE_LIMIT_BURST", str(None))))
        self.rate = rate
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_30(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("os").environ.get("RATE_LIMIT_RATE", str(DEFAULT_RATE))))
        if burst is None:
            burst = int(float(__import__("os").environ.get("RATE_LIMIT_BURST", str(BURST))))
        self.rate = None
        self.burst = burst

    def xǁRateLimitMiddlewareǁ__init____mutmut_31(self, app, rate: int | None = None, burst: int | None = None):
        super().__init__(app)
        if rate is None:
            rate = int(float(__import__("os").environ.get("RATE_LIMIT_RATE", str(DEFAULT_RATE))))
        if burst is None:
            burst = int(float(__import__("os").environ.get("RATE_LIMIT_BURST", str(BURST))))
        self.rate = rate
        self.burst = None
    
    xǁRateLimitMiddlewareǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRateLimitMiddlewareǁ__init____mutmut_1': xǁRateLimitMiddlewareǁ__init____mutmut_1, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_2': xǁRateLimitMiddlewareǁ__init____mutmut_2, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_3': xǁRateLimitMiddlewareǁ__init____mutmut_3, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_4': xǁRateLimitMiddlewareǁ__init____mutmut_4, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_5': xǁRateLimitMiddlewareǁ__init____mutmut_5, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_6': xǁRateLimitMiddlewareǁ__init____mutmut_6, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_7': xǁRateLimitMiddlewareǁ__init____mutmut_7, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_8': xǁRateLimitMiddlewareǁ__init____mutmut_8, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_9': xǁRateLimitMiddlewareǁ__init____mutmut_9, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_10': xǁRateLimitMiddlewareǁ__init____mutmut_10, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_11': xǁRateLimitMiddlewareǁ__init____mutmut_11, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_12': xǁRateLimitMiddlewareǁ__init____mutmut_12, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_13': xǁRateLimitMiddlewareǁ__init____mutmut_13, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_14': xǁRateLimitMiddlewareǁ__init____mutmut_14, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_15': xǁRateLimitMiddlewareǁ__init____mutmut_15, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_16': xǁRateLimitMiddlewareǁ__init____mutmut_16, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_17': xǁRateLimitMiddlewareǁ__init____mutmut_17, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_18': xǁRateLimitMiddlewareǁ__init____mutmut_18, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_19': xǁRateLimitMiddlewareǁ__init____mutmut_19, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_20': xǁRateLimitMiddlewareǁ__init____mutmut_20, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_21': xǁRateLimitMiddlewareǁ__init____mutmut_21, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_22': xǁRateLimitMiddlewareǁ__init____mutmut_22, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_23': xǁRateLimitMiddlewareǁ__init____mutmut_23, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_24': xǁRateLimitMiddlewareǁ__init____mutmut_24, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_25': xǁRateLimitMiddlewareǁ__init____mutmut_25, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_26': xǁRateLimitMiddlewareǁ__init____mutmut_26, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_27': xǁRateLimitMiddlewareǁ__init____mutmut_27, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_28': xǁRateLimitMiddlewareǁ__init____mutmut_28, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_29': xǁRateLimitMiddlewareǁ__init____mutmut_29, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_30': xǁRateLimitMiddlewareǁ__init____mutmut_30, 
        'xǁRateLimitMiddlewareǁ__init____mutmut_31': xǁRateLimitMiddlewareǁ__init____mutmut_31
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRateLimitMiddlewareǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁRateLimitMiddlewareǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁRateLimitMiddlewareǁ__init____mutmut_orig)
    xǁRateLimitMiddlewareǁ__init____mutmut_orig.__name__ = 'xǁRateLimitMiddlewareǁ__init__'

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_orig(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_1(self, request: Request, call_next):
        principal = None
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_2(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) and {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_3(self, request: Request, call_next):
        principal = getattr(None, "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_4(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), None, {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_5(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", None) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_6(self, request: Request, call_next):
        principal = getattr("principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_7(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_8(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", ) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_9(self, request: Request, call_next):
        principal = getattr(getattr(None, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_10(self, request: Request, call_next):
        principal = getattr(getattr(request, None, None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_11(self, request: Request, call_next):
        principal = getattr(getattr("state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_12(self, request: Request, call_next):
        principal = getattr(getattr(request, None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_13(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", ), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_14(self, request: Request, call_next):
        principal = getattr(getattr(request, "XXstateXX", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_15(self, request: Request, call_next):
        principal = getattr(getattr(request, "STATE", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_16(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "XXprincipalXX", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_17(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "PRINCIPAL", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_18(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = None
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_19(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") and "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_20(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get(None) or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_21(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("XXapi_keyXX") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_22(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("API_KEY") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_23(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "XXanonymousXX"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_24(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "ANONYMOUS"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_25(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = None
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_26(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(None, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_27(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, None)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_28(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_29(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, )
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_30(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = None
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_31(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = None
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_32(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now + bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_33(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["XXlastXX"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_34(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["LAST"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_35(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = None
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_36(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["XXtokensXX"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_37(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["TOKENS"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_38(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(None, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_39(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, None)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_40(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_41(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, )
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_42(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] - elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_43(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["XXtokensXX"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_44(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["TOKENS"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_45(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed / self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_46(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = None
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_47(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["XXlastXX"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_48(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["LAST"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_49(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["XXtokensXX"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_50(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["TOKENS"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_51(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] <= 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_52(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 2:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_53(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response(None, status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_54(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=None)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_55(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response(status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_56(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", )
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_57(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("XXRate limit exceededXX", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_58(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_59(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("RATE LIMIT EXCEEDED", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_60(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=430)
        bucket["tokens"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_61(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] = 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_62(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] += 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_63(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["XXtokensXX"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_64(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["TOKENS"] -= 1
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_65(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 2
        return await call_next(request)

    async def xǁRateLimitMiddlewareǁdispatch__mutmut_66(self, request: Request, call_next):
        principal = getattr(getattr(request, "state", None), "principal", {}) or {}
        key = principal.get("api_key") or "anonymous"
        bucket = _get_bucket(key, self.burst)
        now = time.time()
        elapsed = now - bucket["last"]
        bucket["tokens"] = min(self.burst, bucket["tokens"] + elapsed * self.rate)
        bucket["last"] = now
        if bucket["tokens"] < 1:
            return Response("Rate limit exceeded", status_code=429)
        bucket["tokens"] -= 1
        return await call_next(None)
    
    xǁRateLimitMiddlewareǁdispatch__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁRateLimitMiddlewareǁdispatch__mutmut_1': xǁRateLimitMiddlewareǁdispatch__mutmut_1, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_2': xǁRateLimitMiddlewareǁdispatch__mutmut_2, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_3': xǁRateLimitMiddlewareǁdispatch__mutmut_3, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_4': xǁRateLimitMiddlewareǁdispatch__mutmut_4, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_5': xǁRateLimitMiddlewareǁdispatch__mutmut_5, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_6': xǁRateLimitMiddlewareǁdispatch__mutmut_6, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_7': xǁRateLimitMiddlewareǁdispatch__mutmut_7, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_8': xǁRateLimitMiddlewareǁdispatch__mutmut_8, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_9': xǁRateLimitMiddlewareǁdispatch__mutmut_9, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_10': xǁRateLimitMiddlewareǁdispatch__mutmut_10, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_11': xǁRateLimitMiddlewareǁdispatch__mutmut_11, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_12': xǁRateLimitMiddlewareǁdispatch__mutmut_12, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_13': xǁRateLimitMiddlewareǁdispatch__mutmut_13, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_14': xǁRateLimitMiddlewareǁdispatch__mutmut_14, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_15': xǁRateLimitMiddlewareǁdispatch__mutmut_15, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_16': xǁRateLimitMiddlewareǁdispatch__mutmut_16, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_17': xǁRateLimitMiddlewareǁdispatch__mutmut_17, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_18': xǁRateLimitMiddlewareǁdispatch__mutmut_18, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_19': xǁRateLimitMiddlewareǁdispatch__mutmut_19, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_20': xǁRateLimitMiddlewareǁdispatch__mutmut_20, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_21': xǁRateLimitMiddlewareǁdispatch__mutmut_21, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_22': xǁRateLimitMiddlewareǁdispatch__mutmut_22, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_23': xǁRateLimitMiddlewareǁdispatch__mutmut_23, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_24': xǁRateLimitMiddlewareǁdispatch__mutmut_24, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_25': xǁRateLimitMiddlewareǁdispatch__mutmut_25, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_26': xǁRateLimitMiddlewareǁdispatch__mutmut_26, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_27': xǁRateLimitMiddlewareǁdispatch__mutmut_27, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_28': xǁRateLimitMiddlewareǁdispatch__mutmut_28, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_29': xǁRateLimitMiddlewareǁdispatch__mutmut_29, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_30': xǁRateLimitMiddlewareǁdispatch__mutmut_30, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_31': xǁRateLimitMiddlewareǁdispatch__mutmut_31, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_32': xǁRateLimitMiddlewareǁdispatch__mutmut_32, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_33': xǁRateLimitMiddlewareǁdispatch__mutmut_33, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_34': xǁRateLimitMiddlewareǁdispatch__mutmut_34, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_35': xǁRateLimitMiddlewareǁdispatch__mutmut_35, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_36': xǁRateLimitMiddlewareǁdispatch__mutmut_36, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_37': xǁRateLimitMiddlewareǁdispatch__mutmut_37, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_38': xǁRateLimitMiddlewareǁdispatch__mutmut_38, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_39': xǁRateLimitMiddlewareǁdispatch__mutmut_39, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_40': xǁRateLimitMiddlewareǁdispatch__mutmut_40, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_41': xǁRateLimitMiddlewareǁdispatch__mutmut_41, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_42': xǁRateLimitMiddlewareǁdispatch__mutmut_42, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_43': xǁRateLimitMiddlewareǁdispatch__mutmut_43, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_44': xǁRateLimitMiddlewareǁdispatch__mutmut_44, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_45': xǁRateLimitMiddlewareǁdispatch__mutmut_45, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_46': xǁRateLimitMiddlewareǁdispatch__mutmut_46, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_47': xǁRateLimitMiddlewareǁdispatch__mutmut_47, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_48': xǁRateLimitMiddlewareǁdispatch__mutmut_48, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_49': xǁRateLimitMiddlewareǁdispatch__mutmut_49, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_50': xǁRateLimitMiddlewareǁdispatch__mutmut_50, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_51': xǁRateLimitMiddlewareǁdispatch__mutmut_51, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_52': xǁRateLimitMiddlewareǁdispatch__mutmut_52, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_53': xǁRateLimitMiddlewareǁdispatch__mutmut_53, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_54': xǁRateLimitMiddlewareǁdispatch__mutmut_54, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_55': xǁRateLimitMiddlewareǁdispatch__mutmut_55, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_56': xǁRateLimitMiddlewareǁdispatch__mutmut_56, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_57': xǁRateLimitMiddlewareǁdispatch__mutmut_57, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_58': xǁRateLimitMiddlewareǁdispatch__mutmut_58, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_59': xǁRateLimitMiddlewareǁdispatch__mutmut_59, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_60': xǁRateLimitMiddlewareǁdispatch__mutmut_60, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_61': xǁRateLimitMiddlewareǁdispatch__mutmut_61, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_62': xǁRateLimitMiddlewareǁdispatch__mutmut_62, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_63': xǁRateLimitMiddlewareǁdispatch__mutmut_63, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_64': xǁRateLimitMiddlewareǁdispatch__mutmut_64, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_65': xǁRateLimitMiddlewareǁdispatch__mutmut_65, 
        'xǁRateLimitMiddlewareǁdispatch__mutmut_66': xǁRateLimitMiddlewareǁdispatch__mutmut_66
    }
    
    def dispatch(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁRateLimitMiddlewareǁdispatch__mutmut_orig"), object.__getattribute__(self, "xǁRateLimitMiddlewareǁdispatch__mutmut_mutants"), args, kwargs, self)
        return result 
    
    dispatch.__signature__ = _mutmut_signature(xǁRateLimitMiddlewareǁdispatch__mutmut_orig)
    xǁRateLimitMiddlewareǁdispatch__mutmut_orig.__name__ = 'xǁRateLimitMiddlewareǁdispatch'
