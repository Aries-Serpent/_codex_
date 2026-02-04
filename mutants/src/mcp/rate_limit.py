"""Deterministic token bucket rate limiter for MCP tests."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable
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


@dataclass
class _Bucket:
    tokens: float
    updated_at: float


class MCPRateLimiter:
    """Simple token-bucket rate limiter keyed by principal+tool."""

    def xǁMCPRateLimiterǁ__init____mutmut_orig(
        self,
        rate: float,
        capacity: int,
        *,
        seed: int | None = None,
        time_func: Callable[[], float] | None = None,
    ) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive")
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.rate = float(rate)
        self.capacity = float(capacity)
        self.seed = seed
        self._clock = time_func or time.monotonic
        self._buckets: dict[tuple[str, str], _Bucket] = {}

    def xǁMCPRateLimiterǁ__init____mutmut_1(
        self,
        rate: float,
        capacity: int,
        *,
        seed: int | None = None,
        time_func: Callable[[], float] | None = None,
    ) -> None:
        if rate < 0:
            raise ValueError("rate must be positive")
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.rate = float(rate)
        self.capacity = float(capacity)
        self.seed = seed
        self._clock = time_func or time.monotonic
        self._buckets: dict[tuple[str, str], _Bucket] = {}

    def xǁMCPRateLimiterǁ__init____mutmut_2(
        self,
        rate: float,
        capacity: int,
        *,
        seed: int | None = None,
        time_func: Callable[[], float] | None = None,
    ) -> None:
        if rate <= 1:
            raise ValueError("rate must be positive")
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.rate = float(rate)
        self.capacity = float(capacity)
        self.seed = seed
        self._clock = time_func or time.monotonic
        self._buckets: dict[tuple[str, str], _Bucket] = {}

    def xǁMCPRateLimiterǁ__init____mutmut_3(
        self,
        rate: float,
        capacity: int,
        *,
        seed: int | None = None,
        time_func: Callable[[], float] | None = None,
    ) -> None:
        if rate <= 0:
            raise ValueError(None)
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.rate = float(rate)
        self.capacity = float(capacity)
        self.seed = seed
        self._clock = time_func or time.monotonic
        self._buckets: dict[tuple[str, str], _Bucket] = {}

    def xǁMCPRateLimiterǁ__init____mutmut_4(
        self,
        rate: float,
        capacity: int,
        *,
        seed: int | None = None,
        time_func: Callable[[], float] | None = None,
    ) -> None:
        if rate <= 0:
            raise ValueError("XXrate must be positiveXX")
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.rate = float(rate)
        self.capacity = float(capacity)
        self.seed = seed
        self._clock = time_func or time.monotonic
        self._buckets: dict[tuple[str, str], _Bucket] = {}

    def xǁMCPRateLimiterǁ__init____mutmut_5(
        self,
        rate: float,
        capacity: int,
        *,
        seed: int | None = None,
        time_func: Callable[[], float] | None = None,
    ) -> None:
        if rate <= 0:
            raise ValueError("RATE MUST BE POSITIVE")
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.rate = float(rate)
        self.capacity = float(capacity)
        self.seed = seed
        self._clock = time_func or time.monotonic
        self._buckets: dict[tuple[str, str], _Bucket] = {}

    def xǁMCPRateLimiterǁ__init____mutmut_6(
        self,
        rate: float,
        capacity: int,
        *,
        seed: int | None = None,
        time_func: Callable[[], float] | None = None,
    ) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive")
        if capacity < 0:
            raise ValueError("capacity must be positive")

        self.rate = float(rate)
        self.capacity = float(capacity)
        self.seed = seed
        self._clock = time_func or time.monotonic
        self._buckets: dict[tuple[str, str], _Bucket] = {}

    def xǁMCPRateLimiterǁ__init____mutmut_7(
        self,
        rate: float,
        capacity: int,
        *,
        seed: int | None = None,
        time_func: Callable[[], float] | None = None,
    ) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive")
        if capacity <= 1:
            raise ValueError("capacity must be positive")

        self.rate = float(rate)
        self.capacity = float(capacity)
        self.seed = seed
        self._clock = time_func or time.monotonic
        self._buckets: dict[tuple[str, str], _Bucket] = {}

    def xǁMCPRateLimiterǁ__init____mutmut_8(
        self,
        rate: float,
        capacity: int,
        *,
        seed: int | None = None,
        time_func: Callable[[], float] | None = None,
    ) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive")
        if capacity <= 0:
            raise ValueError(None)

        self.rate = float(rate)
        self.capacity = float(capacity)
        self.seed = seed
        self._clock = time_func or time.monotonic
        self._buckets: dict[tuple[str, str], _Bucket] = {}

    def xǁMCPRateLimiterǁ__init____mutmut_9(
        self,
        rate: float,
        capacity: int,
        *,
        seed: int | None = None,
        time_func: Callable[[], float] | None = None,
    ) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive")
        if capacity <= 0:
            raise ValueError("XXcapacity must be positiveXX")

        self.rate = float(rate)
        self.capacity = float(capacity)
        self.seed = seed
        self._clock = time_func or time.monotonic
        self._buckets: dict[tuple[str, str], _Bucket] = {}

    def xǁMCPRateLimiterǁ__init____mutmut_10(
        self,
        rate: float,
        capacity: int,
        *,
        seed: int | None = None,
        time_func: Callable[[], float] | None = None,
    ) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive")
        if capacity <= 0:
            raise ValueError("CAPACITY MUST BE POSITIVE")

        self.rate = float(rate)
        self.capacity = float(capacity)
        self.seed = seed
        self._clock = time_func or time.monotonic
        self._buckets: dict[tuple[str, str], _Bucket] = {}

    def xǁMCPRateLimiterǁ__init____mutmut_11(
        self,
        rate: float,
        capacity: int,
        *,
        seed: int | None = None,
        time_func: Callable[[], float] | None = None,
    ) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive")
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.rate = None
        self.capacity = float(capacity)
        self.seed = seed
        self._clock = time_func or time.monotonic
        self._buckets: dict[tuple[str, str], _Bucket] = {}

    def xǁMCPRateLimiterǁ__init____mutmut_12(
        self,
        rate: float,
        capacity: int,
        *,
        seed: int | None = None,
        time_func: Callable[[], float] | None = None,
    ) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive")
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.rate = float(None)
        self.capacity = float(capacity)
        self.seed = seed
        self._clock = time_func or time.monotonic
        self._buckets: dict[tuple[str, str], _Bucket] = {}

    def xǁMCPRateLimiterǁ__init____mutmut_13(
        self,
        rate: float,
        capacity: int,
        *,
        seed: int | None = None,
        time_func: Callable[[], float] | None = None,
    ) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive")
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.rate = float(rate)
        self.capacity = None
        self.seed = seed
        self._clock = time_func or time.monotonic
        self._buckets: dict[tuple[str, str], _Bucket] = {}

    def xǁMCPRateLimiterǁ__init____mutmut_14(
        self,
        rate: float,
        capacity: int,
        *,
        seed: int | None = None,
        time_func: Callable[[], float] | None = None,
    ) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive")
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.rate = float(rate)
        self.capacity = float(None)
        self.seed = seed
        self._clock = time_func or time.monotonic
        self._buckets: dict[tuple[str, str], _Bucket] = {}

    def xǁMCPRateLimiterǁ__init____mutmut_15(
        self,
        rate: float,
        capacity: int,
        *,
        seed: int | None = None,
        time_func: Callable[[], float] | None = None,
    ) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive")
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.rate = float(rate)
        self.capacity = float(capacity)
        self.seed = None
        self._clock = time_func or time.monotonic
        self._buckets: dict[tuple[str, str], _Bucket] = {}

    def xǁMCPRateLimiterǁ__init____mutmut_16(
        self,
        rate: float,
        capacity: int,
        *,
        seed: int | None = None,
        time_func: Callable[[], float] | None = None,
    ) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive")
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.rate = float(rate)
        self.capacity = float(capacity)
        self.seed = seed
        self._clock = None
        self._buckets: dict[tuple[str, str], _Bucket] = {}

    def xǁMCPRateLimiterǁ__init____mutmut_17(
        self,
        rate: float,
        capacity: int,
        *,
        seed: int | None = None,
        time_func: Callable[[], float] | None = None,
    ) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive")
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.rate = float(rate)
        self.capacity = float(capacity)
        self.seed = seed
        self._clock = time_func and time.monotonic
        self._buckets: dict[tuple[str, str], _Bucket] = {}

    def xǁMCPRateLimiterǁ__init____mutmut_18(
        self,
        rate: float,
        capacity: int,
        *,
        seed: int | None = None,
        time_func: Callable[[], float] | None = None,
    ) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive")
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.rate = float(rate)
        self.capacity = float(capacity)
        self.seed = seed
        self._clock = time_func or time.monotonic
        self._buckets: dict[tuple[str, str], _Bucket] = None
    
    xǁMCPRateLimiterǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPRateLimiterǁ__init____mutmut_1': xǁMCPRateLimiterǁ__init____mutmut_1, 
        'xǁMCPRateLimiterǁ__init____mutmut_2': xǁMCPRateLimiterǁ__init____mutmut_2, 
        'xǁMCPRateLimiterǁ__init____mutmut_3': xǁMCPRateLimiterǁ__init____mutmut_3, 
        'xǁMCPRateLimiterǁ__init____mutmut_4': xǁMCPRateLimiterǁ__init____mutmut_4, 
        'xǁMCPRateLimiterǁ__init____mutmut_5': xǁMCPRateLimiterǁ__init____mutmut_5, 
        'xǁMCPRateLimiterǁ__init____mutmut_6': xǁMCPRateLimiterǁ__init____mutmut_6, 
        'xǁMCPRateLimiterǁ__init____mutmut_7': xǁMCPRateLimiterǁ__init____mutmut_7, 
        'xǁMCPRateLimiterǁ__init____mutmut_8': xǁMCPRateLimiterǁ__init____mutmut_8, 
        'xǁMCPRateLimiterǁ__init____mutmut_9': xǁMCPRateLimiterǁ__init____mutmut_9, 
        'xǁMCPRateLimiterǁ__init____mutmut_10': xǁMCPRateLimiterǁ__init____mutmut_10, 
        'xǁMCPRateLimiterǁ__init____mutmut_11': xǁMCPRateLimiterǁ__init____mutmut_11, 
        'xǁMCPRateLimiterǁ__init____mutmut_12': xǁMCPRateLimiterǁ__init____mutmut_12, 
        'xǁMCPRateLimiterǁ__init____mutmut_13': xǁMCPRateLimiterǁ__init____mutmut_13, 
        'xǁMCPRateLimiterǁ__init____mutmut_14': xǁMCPRateLimiterǁ__init____mutmut_14, 
        'xǁMCPRateLimiterǁ__init____mutmut_15': xǁMCPRateLimiterǁ__init____mutmut_15, 
        'xǁMCPRateLimiterǁ__init____mutmut_16': xǁMCPRateLimiterǁ__init____mutmut_16, 
        'xǁMCPRateLimiterǁ__init____mutmut_17': xǁMCPRateLimiterǁ__init____mutmut_17, 
        'xǁMCPRateLimiterǁ__init____mutmut_18': xǁMCPRateLimiterǁ__init____mutmut_18
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPRateLimiterǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁMCPRateLimiterǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁMCPRateLimiterǁ__init____mutmut_orig)
    xǁMCPRateLimiterǁ__init____mutmut_orig.__name__ = 'xǁMCPRateLimiterǁ__init__'

    def xǁMCPRateLimiterǁ_key__mutmut_orig(self, principal_id: str | None, tool_name: str | None) -> tuple[str, str]:
        return (principal_id or "*", tool_name or "*")

    def xǁMCPRateLimiterǁ_key__mutmut_1(self, principal_id: str | None, tool_name: str | None) -> tuple[str, str]:
        return (principal_id and "*", tool_name or "*")

    def xǁMCPRateLimiterǁ_key__mutmut_2(self, principal_id: str | None, tool_name: str | None) -> tuple[str, str]:
        return (principal_id or "XX*XX", tool_name or "*")

    def xǁMCPRateLimiterǁ_key__mutmut_3(self, principal_id: str | None, tool_name: str | None) -> tuple[str, str]:
        return (principal_id or "*", tool_name and "*")

    def xǁMCPRateLimiterǁ_key__mutmut_4(self, principal_id: str | None, tool_name: str | None) -> tuple[str, str]:
        return (principal_id or "*", tool_name or "XX*XX")
    
    xǁMCPRateLimiterǁ_key__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPRateLimiterǁ_key__mutmut_1': xǁMCPRateLimiterǁ_key__mutmut_1, 
        'xǁMCPRateLimiterǁ_key__mutmut_2': xǁMCPRateLimiterǁ_key__mutmut_2, 
        'xǁMCPRateLimiterǁ_key__mutmut_3': xǁMCPRateLimiterǁ_key__mutmut_3, 
        'xǁMCPRateLimiterǁ_key__mutmut_4': xǁMCPRateLimiterǁ_key__mutmut_4
    }
    
    def _key(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPRateLimiterǁ_key__mutmut_orig"), object.__getattribute__(self, "xǁMCPRateLimiterǁ_key__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _key.__signature__ = _mutmut_signature(xǁMCPRateLimiterǁ_key__mutmut_orig)
    xǁMCPRateLimiterǁ_key__mutmut_orig.__name__ = 'xǁMCPRateLimiterǁ_key'

    def xǁMCPRateLimiterǁ_refill__mutmut_orig(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=self.capacity, updated_at=now)
            self._buckets[key] = bucket
            return bucket

        elapsed = max(0.0, now - bucket.updated_at)
        if elapsed > 0:
            bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.rate)
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_1(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = None
        if bucket is None:
            bucket = _Bucket(tokens=self.capacity, updated_at=now)
            self._buckets[key] = bucket
            return bucket

        elapsed = max(0.0, now - bucket.updated_at)
        if elapsed > 0:
            bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.rate)
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_2(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(None)
        if bucket is None:
            bucket = _Bucket(tokens=self.capacity, updated_at=now)
            self._buckets[key] = bucket
            return bucket

        elapsed = max(0.0, now - bucket.updated_at)
        if elapsed > 0:
            bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.rate)
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_3(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is not None:
            bucket = _Bucket(tokens=self.capacity, updated_at=now)
            self._buckets[key] = bucket
            return bucket

        elapsed = max(0.0, now - bucket.updated_at)
        if elapsed > 0:
            bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.rate)
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_4(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = None
            self._buckets[key] = bucket
            return bucket

        elapsed = max(0.0, now - bucket.updated_at)
        if elapsed > 0:
            bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.rate)
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_5(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=None, updated_at=now)
            self._buckets[key] = bucket
            return bucket

        elapsed = max(0.0, now - bucket.updated_at)
        if elapsed > 0:
            bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.rate)
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_6(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=self.capacity, updated_at=None)
            self._buckets[key] = bucket
            return bucket

        elapsed = max(0.0, now - bucket.updated_at)
        if elapsed > 0:
            bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.rate)
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_7(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(updated_at=now)
            self._buckets[key] = bucket
            return bucket

        elapsed = max(0.0, now - bucket.updated_at)
        if elapsed > 0:
            bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.rate)
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_8(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=self.capacity, )
            self._buckets[key] = bucket
            return bucket

        elapsed = max(0.0, now - bucket.updated_at)
        if elapsed > 0:
            bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.rate)
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_9(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=self.capacity, updated_at=now)
            self._buckets[key] = None
            return bucket

        elapsed = max(0.0, now - bucket.updated_at)
        if elapsed > 0:
            bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.rate)
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_10(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=self.capacity, updated_at=now)
            self._buckets[key] = bucket
            return bucket

        elapsed = None
        if elapsed > 0:
            bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.rate)
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_11(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=self.capacity, updated_at=now)
            self._buckets[key] = bucket
            return bucket

        elapsed = max(None, now - bucket.updated_at)
        if elapsed > 0:
            bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.rate)
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_12(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=self.capacity, updated_at=now)
            self._buckets[key] = bucket
            return bucket

        elapsed = max(0.0, None)
        if elapsed > 0:
            bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.rate)
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_13(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=self.capacity, updated_at=now)
            self._buckets[key] = bucket
            return bucket

        elapsed = max(now - bucket.updated_at)
        if elapsed > 0:
            bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.rate)
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_14(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=self.capacity, updated_at=now)
            self._buckets[key] = bucket
            return bucket

        elapsed = max(0.0, )
        if elapsed > 0:
            bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.rate)
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_15(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=self.capacity, updated_at=now)
            self._buckets[key] = bucket
            return bucket

        elapsed = max(1.0, now - bucket.updated_at)
        if elapsed > 0:
            bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.rate)
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_16(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=self.capacity, updated_at=now)
            self._buckets[key] = bucket
            return bucket

        elapsed = max(0.0, now + bucket.updated_at)
        if elapsed > 0:
            bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.rate)
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_17(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=self.capacity, updated_at=now)
            self._buckets[key] = bucket
            return bucket

        elapsed = max(0.0, now - bucket.updated_at)
        if elapsed >= 0:
            bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.rate)
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_18(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=self.capacity, updated_at=now)
            self._buckets[key] = bucket
            return bucket

        elapsed = max(0.0, now - bucket.updated_at)
        if elapsed > 1:
            bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.rate)
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_19(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=self.capacity, updated_at=now)
            self._buckets[key] = bucket
            return bucket

        elapsed = max(0.0, now - bucket.updated_at)
        if elapsed > 0:
            bucket.tokens = None
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_20(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=self.capacity, updated_at=now)
            self._buckets[key] = bucket
            return bucket

        elapsed = max(0.0, now - bucket.updated_at)
        if elapsed > 0:
            bucket.tokens = min(None, bucket.tokens + elapsed * self.rate)
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_21(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=self.capacity, updated_at=now)
            self._buckets[key] = bucket
            return bucket

        elapsed = max(0.0, now - bucket.updated_at)
        if elapsed > 0:
            bucket.tokens = min(self.capacity, None)
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_22(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=self.capacity, updated_at=now)
            self._buckets[key] = bucket
            return bucket

        elapsed = max(0.0, now - bucket.updated_at)
        if elapsed > 0:
            bucket.tokens = min(bucket.tokens + elapsed * self.rate)
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_23(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=self.capacity, updated_at=now)
            self._buckets[key] = bucket
            return bucket

        elapsed = max(0.0, now - bucket.updated_at)
        if elapsed > 0:
            bucket.tokens = min(self.capacity, )
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_24(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=self.capacity, updated_at=now)
            self._buckets[key] = bucket
            return bucket

        elapsed = max(0.0, now - bucket.updated_at)
        if elapsed > 0:
            bucket.tokens = min(self.capacity, bucket.tokens - elapsed * self.rate)
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_25(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=self.capacity, updated_at=now)
            self._buckets[key] = bucket
            return bucket

        elapsed = max(0.0, now - bucket.updated_at)
        if elapsed > 0:
            bucket.tokens = min(self.capacity, bucket.tokens + elapsed / self.rate)
            bucket.updated_at = now
        return bucket

    def xǁMCPRateLimiterǁ_refill__mutmut_26(self, key: tuple[str, str], now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(tokens=self.capacity, updated_at=now)
            self._buckets[key] = bucket
            return bucket

        elapsed = max(0.0, now - bucket.updated_at)
        if elapsed > 0:
            bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.rate)
            bucket.updated_at = None
        return bucket
    
    xǁMCPRateLimiterǁ_refill__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPRateLimiterǁ_refill__mutmut_1': xǁMCPRateLimiterǁ_refill__mutmut_1, 
        'xǁMCPRateLimiterǁ_refill__mutmut_2': xǁMCPRateLimiterǁ_refill__mutmut_2, 
        'xǁMCPRateLimiterǁ_refill__mutmut_3': xǁMCPRateLimiterǁ_refill__mutmut_3, 
        'xǁMCPRateLimiterǁ_refill__mutmut_4': xǁMCPRateLimiterǁ_refill__mutmut_4, 
        'xǁMCPRateLimiterǁ_refill__mutmut_5': xǁMCPRateLimiterǁ_refill__mutmut_5, 
        'xǁMCPRateLimiterǁ_refill__mutmut_6': xǁMCPRateLimiterǁ_refill__mutmut_6, 
        'xǁMCPRateLimiterǁ_refill__mutmut_7': xǁMCPRateLimiterǁ_refill__mutmut_7, 
        'xǁMCPRateLimiterǁ_refill__mutmut_8': xǁMCPRateLimiterǁ_refill__mutmut_8, 
        'xǁMCPRateLimiterǁ_refill__mutmut_9': xǁMCPRateLimiterǁ_refill__mutmut_9, 
        'xǁMCPRateLimiterǁ_refill__mutmut_10': xǁMCPRateLimiterǁ_refill__mutmut_10, 
        'xǁMCPRateLimiterǁ_refill__mutmut_11': xǁMCPRateLimiterǁ_refill__mutmut_11, 
        'xǁMCPRateLimiterǁ_refill__mutmut_12': xǁMCPRateLimiterǁ_refill__mutmut_12, 
        'xǁMCPRateLimiterǁ_refill__mutmut_13': xǁMCPRateLimiterǁ_refill__mutmut_13, 
        'xǁMCPRateLimiterǁ_refill__mutmut_14': xǁMCPRateLimiterǁ_refill__mutmut_14, 
        'xǁMCPRateLimiterǁ_refill__mutmut_15': xǁMCPRateLimiterǁ_refill__mutmut_15, 
        'xǁMCPRateLimiterǁ_refill__mutmut_16': xǁMCPRateLimiterǁ_refill__mutmut_16, 
        'xǁMCPRateLimiterǁ_refill__mutmut_17': xǁMCPRateLimiterǁ_refill__mutmut_17, 
        'xǁMCPRateLimiterǁ_refill__mutmut_18': xǁMCPRateLimiterǁ_refill__mutmut_18, 
        'xǁMCPRateLimiterǁ_refill__mutmut_19': xǁMCPRateLimiterǁ_refill__mutmut_19, 
        'xǁMCPRateLimiterǁ_refill__mutmut_20': xǁMCPRateLimiterǁ_refill__mutmut_20, 
        'xǁMCPRateLimiterǁ_refill__mutmut_21': xǁMCPRateLimiterǁ_refill__mutmut_21, 
        'xǁMCPRateLimiterǁ_refill__mutmut_22': xǁMCPRateLimiterǁ_refill__mutmut_22, 
        'xǁMCPRateLimiterǁ_refill__mutmut_23': xǁMCPRateLimiterǁ_refill__mutmut_23, 
        'xǁMCPRateLimiterǁ_refill__mutmut_24': xǁMCPRateLimiterǁ_refill__mutmut_24, 
        'xǁMCPRateLimiterǁ_refill__mutmut_25': xǁMCPRateLimiterǁ_refill__mutmut_25, 
        'xǁMCPRateLimiterǁ_refill__mutmut_26': xǁMCPRateLimiterǁ_refill__mutmut_26
    }
    
    def _refill(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPRateLimiterǁ_refill__mutmut_orig"), object.__getattribute__(self, "xǁMCPRateLimiterǁ_refill__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _refill.__signature__ = _mutmut_signature(xǁMCPRateLimiterǁ_refill__mutmut_orig)
    xǁMCPRateLimiterǁ_refill__mutmut_orig.__name__ = 'xǁMCPRateLimiterǁ_refill'

    def xǁMCPRateLimiterǁallow__mutmut_orig(self, principal_id: str | None, tool_name: str | None) -> bool:
        """Return True if request is within the rate limit."""

        now = self._clock()
        key = self._key(principal_id, tool_name)
        bucket = self._refill(key, now)
        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return True
        return False

    def xǁMCPRateLimiterǁallow__mutmut_1(self, principal_id: str | None, tool_name: str | None) -> bool:
        """Return True if request is within the rate limit."""

        now = None
        key = self._key(principal_id, tool_name)
        bucket = self._refill(key, now)
        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return True
        return False

    def xǁMCPRateLimiterǁallow__mutmut_2(self, principal_id: str | None, tool_name: str | None) -> bool:
        """Return True if request is within the rate limit."""

        now = self._clock()
        key = None
        bucket = self._refill(key, now)
        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return True
        return False

    def xǁMCPRateLimiterǁallow__mutmut_3(self, principal_id: str | None, tool_name: str | None) -> bool:
        """Return True if request is within the rate limit."""

        now = self._clock()
        key = self._key(None, tool_name)
        bucket = self._refill(key, now)
        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return True
        return False

    def xǁMCPRateLimiterǁallow__mutmut_4(self, principal_id: str | None, tool_name: str | None) -> bool:
        """Return True if request is within the rate limit."""

        now = self._clock()
        key = self._key(principal_id, None)
        bucket = self._refill(key, now)
        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return True
        return False

    def xǁMCPRateLimiterǁallow__mutmut_5(self, principal_id: str | None, tool_name: str | None) -> bool:
        """Return True if request is within the rate limit."""

        now = self._clock()
        key = self._key(tool_name)
        bucket = self._refill(key, now)
        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return True
        return False

    def xǁMCPRateLimiterǁallow__mutmut_6(self, principal_id: str | None, tool_name: str | None) -> bool:
        """Return True if request is within the rate limit."""

        now = self._clock()
        key = self._key(principal_id, )
        bucket = self._refill(key, now)
        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return True
        return False

    def xǁMCPRateLimiterǁallow__mutmut_7(self, principal_id: str | None, tool_name: str | None) -> bool:
        """Return True if request is within the rate limit."""

        now = self._clock()
        key = self._key(principal_id, tool_name)
        bucket = None
        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return True
        return False

    def xǁMCPRateLimiterǁallow__mutmut_8(self, principal_id: str | None, tool_name: str | None) -> bool:
        """Return True if request is within the rate limit."""

        now = self._clock()
        key = self._key(principal_id, tool_name)
        bucket = self._refill(None, now)
        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return True
        return False

    def xǁMCPRateLimiterǁallow__mutmut_9(self, principal_id: str | None, tool_name: str | None) -> bool:
        """Return True if request is within the rate limit."""

        now = self._clock()
        key = self._key(principal_id, tool_name)
        bucket = self._refill(key, None)
        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return True
        return False

    def xǁMCPRateLimiterǁallow__mutmut_10(self, principal_id: str | None, tool_name: str | None) -> bool:
        """Return True if request is within the rate limit."""

        now = self._clock()
        key = self._key(principal_id, tool_name)
        bucket = self._refill(now)
        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return True
        return False

    def xǁMCPRateLimiterǁallow__mutmut_11(self, principal_id: str | None, tool_name: str | None) -> bool:
        """Return True if request is within the rate limit."""

        now = self._clock()
        key = self._key(principal_id, tool_name)
        bucket = self._refill(key, )
        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return True
        return False

    def xǁMCPRateLimiterǁallow__mutmut_12(self, principal_id: str | None, tool_name: str | None) -> bool:
        """Return True if request is within the rate limit."""

        now = self._clock()
        key = self._key(principal_id, tool_name)
        bucket = self._refill(key, now)
        if bucket.tokens > 1:
            bucket.tokens -= 1
            return True
        return False

    def xǁMCPRateLimiterǁallow__mutmut_13(self, principal_id: str | None, tool_name: str | None) -> bool:
        """Return True if request is within the rate limit."""

        now = self._clock()
        key = self._key(principal_id, tool_name)
        bucket = self._refill(key, now)
        if bucket.tokens >= 2:
            bucket.tokens -= 1
            return True
        return False

    def xǁMCPRateLimiterǁallow__mutmut_14(self, principal_id: str | None, tool_name: str | None) -> bool:
        """Return True if request is within the rate limit."""

        now = self._clock()
        key = self._key(principal_id, tool_name)
        bucket = self._refill(key, now)
        if bucket.tokens >= 1:
            bucket.tokens = 1
            return True
        return False

    def xǁMCPRateLimiterǁallow__mutmut_15(self, principal_id: str | None, tool_name: str | None) -> bool:
        """Return True if request is within the rate limit."""

        now = self._clock()
        key = self._key(principal_id, tool_name)
        bucket = self._refill(key, now)
        if bucket.tokens >= 1:
            bucket.tokens += 1
            return True
        return False

    def xǁMCPRateLimiterǁallow__mutmut_16(self, principal_id: str | None, tool_name: str | None) -> bool:
        """Return True if request is within the rate limit."""

        now = self._clock()
        key = self._key(principal_id, tool_name)
        bucket = self._refill(key, now)
        if bucket.tokens >= 1:
            bucket.tokens -= 2
            return True
        return False

    def xǁMCPRateLimiterǁallow__mutmut_17(self, principal_id: str | None, tool_name: str | None) -> bool:
        """Return True if request is within the rate limit."""

        now = self._clock()
        key = self._key(principal_id, tool_name)
        bucket = self._refill(key, now)
        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return False
        return False

    def xǁMCPRateLimiterǁallow__mutmut_18(self, principal_id: str | None, tool_name: str | None) -> bool:
        """Return True if request is within the rate limit."""

        now = self._clock()
        key = self._key(principal_id, tool_name)
        bucket = self._refill(key, now)
        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return True
        return True
    
    xǁMCPRateLimiterǁallow__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPRateLimiterǁallow__mutmut_1': xǁMCPRateLimiterǁallow__mutmut_1, 
        'xǁMCPRateLimiterǁallow__mutmut_2': xǁMCPRateLimiterǁallow__mutmut_2, 
        'xǁMCPRateLimiterǁallow__mutmut_3': xǁMCPRateLimiterǁallow__mutmut_3, 
        'xǁMCPRateLimiterǁallow__mutmut_4': xǁMCPRateLimiterǁallow__mutmut_4, 
        'xǁMCPRateLimiterǁallow__mutmut_5': xǁMCPRateLimiterǁallow__mutmut_5, 
        'xǁMCPRateLimiterǁallow__mutmut_6': xǁMCPRateLimiterǁallow__mutmut_6, 
        'xǁMCPRateLimiterǁallow__mutmut_7': xǁMCPRateLimiterǁallow__mutmut_7, 
        'xǁMCPRateLimiterǁallow__mutmut_8': xǁMCPRateLimiterǁallow__mutmut_8, 
        'xǁMCPRateLimiterǁallow__mutmut_9': xǁMCPRateLimiterǁallow__mutmut_9, 
        'xǁMCPRateLimiterǁallow__mutmut_10': xǁMCPRateLimiterǁallow__mutmut_10, 
        'xǁMCPRateLimiterǁallow__mutmut_11': xǁMCPRateLimiterǁallow__mutmut_11, 
        'xǁMCPRateLimiterǁallow__mutmut_12': xǁMCPRateLimiterǁallow__mutmut_12, 
        'xǁMCPRateLimiterǁallow__mutmut_13': xǁMCPRateLimiterǁallow__mutmut_13, 
        'xǁMCPRateLimiterǁallow__mutmut_14': xǁMCPRateLimiterǁallow__mutmut_14, 
        'xǁMCPRateLimiterǁallow__mutmut_15': xǁMCPRateLimiterǁallow__mutmut_15, 
        'xǁMCPRateLimiterǁallow__mutmut_16': xǁMCPRateLimiterǁallow__mutmut_16, 
        'xǁMCPRateLimiterǁallow__mutmut_17': xǁMCPRateLimiterǁallow__mutmut_17, 
        'xǁMCPRateLimiterǁallow__mutmut_18': xǁMCPRateLimiterǁallow__mutmut_18
    }
    
    def allow(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPRateLimiterǁallow__mutmut_orig"), object.__getattribute__(self, "xǁMCPRateLimiterǁallow__mutmut_mutants"), args, kwargs, self)
        return result 
    
    allow.__signature__ = _mutmut_signature(xǁMCPRateLimiterǁallow__mutmut_orig)
    xǁMCPRateLimiterǁallow__mutmut_orig.__name__ = 'xǁMCPRateLimiterǁallow'

    def xǁMCPRateLimiterǁreset__mutmut_orig(self, principal_id: str | None = None, tool_name: str | None = None) -> None:
        """Reset limiter state for a specific key or entirely."""

        if principal_id is None and tool_name is None:
            self._buckets.clear()
            return

        key = self._key(principal_id, tool_name)
        self._buckets.pop(key, None)

    def xǁMCPRateLimiterǁreset__mutmut_1(self, principal_id: str | None = None, tool_name: str | None = None) -> None:
        """Reset limiter state for a specific key or entirely."""

        if principal_id is None or tool_name is None:
            self._buckets.clear()
            return

        key = self._key(principal_id, tool_name)
        self._buckets.pop(key, None)

    def xǁMCPRateLimiterǁreset__mutmut_2(self, principal_id: str | None = None, tool_name: str | None = None) -> None:
        """Reset limiter state for a specific key or entirely."""

        if principal_id is not None and tool_name is None:
            self._buckets.clear()
            return

        key = self._key(principal_id, tool_name)
        self._buckets.pop(key, None)

    def xǁMCPRateLimiterǁreset__mutmut_3(self, principal_id: str | None = None, tool_name: str | None = None) -> None:
        """Reset limiter state for a specific key or entirely."""

        if principal_id is None and tool_name is not None:
            self._buckets.clear()
            return

        key = self._key(principal_id, tool_name)
        self._buckets.pop(key, None)

    def xǁMCPRateLimiterǁreset__mutmut_4(self, principal_id: str | None = None, tool_name: str | None = None) -> None:
        """Reset limiter state for a specific key or entirely."""

        if principal_id is None and tool_name is None:
            self._buckets.clear()
            return

        key = None
        self._buckets.pop(key, None)

    def xǁMCPRateLimiterǁreset__mutmut_5(self, principal_id: str | None = None, tool_name: str | None = None) -> None:
        """Reset limiter state for a specific key or entirely."""

        if principal_id is None and tool_name is None:
            self._buckets.clear()
            return

        key = self._key(None, tool_name)
        self._buckets.pop(key, None)

    def xǁMCPRateLimiterǁreset__mutmut_6(self, principal_id: str | None = None, tool_name: str | None = None) -> None:
        """Reset limiter state for a specific key or entirely."""

        if principal_id is None and tool_name is None:
            self._buckets.clear()
            return

        key = self._key(principal_id, None)
        self._buckets.pop(key, None)

    def xǁMCPRateLimiterǁreset__mutmut_7(self, principal_id: str | None = None, tool_name: str | None = None) -> None:
        """Reset limiter state for a specific key or entirely."""

        if principal_id is None and tool_name is None:
            self._buckets.clear()
            return

        key = self._key(tool_name)
        self._buckets.pop(key, None)

    def xǁMCPRateLimiterǁreset__mutmut_8(self, principal_id: str | None = None, tool_name: str | None = None) -> None:
        """Reset limiter state for a specific key or entirely."""

        if principal_id is None and tool_name is None:
            self._buckets.clear()
            return

        key = self._key(principal_id, )
        self._buckets.pop(key, None)

    def xǁMCPRateLimiterǁreset__mutmut_9(self, principal_id: str | None = None, tool_name: str | None = None) -> None:
        """Reset limiter state for a specific key or entirely."""

        if principal_id is None and tool_name is None:
            self._buckets.clear()
            return

        key = self._key(principal_id, tool_name)
        self._buckets.pop(None, None)

    def xǁMCPRateLimiterǁreset__mutmut_10(self, principal_id: str | None = None, tool_name: str | None = None) -> None:
        """Reset limiter state for a specific key or entirely."""

        if principal_id is None and tool_name is None:
            self._buckets.clear()
            return

        key = self._key(principal_id, tool_name)
        self._buckets.pop(None)

    def xǁMCPRateLimiterǁreset__mutmut_11(self, principal_id: str | None = None, tool_name: str | None = None) -> None:
        """Reset limiter state for a specific key or entirely."""

        if principal_id is None and tool_name is None:
            self._buckets.clear()
            return

        key = self._key(principal_id, tool_name)
        self._buckets.pop(key, )
    
    xǁMCPRateLimiterǁreset__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁMCPRateLimiterǁreset__mutmut_1': xǁMCPRateLimiterǁreset__mutmut_1, 
        'xǁMCPRateLimiterǁreset__mutmut_2': xǁMCPRateLimiterǁreset__mutmut_2, 
        'xǁMCPRateLimiterǁreset__mutmut_3': xǁMCPRateLimiterǁreset__mutmut_3, 
        'xǁMCPRateLimiterǁreset__mutmut_4': xǁMCPRateLimiterǁreset__mutmut_4, 
        'xǁMCPRateLimiterǁreset__mutmut_5': xǁMCPRateLimiterǁreset__mutmut_5, 
        'xǁMCPRateLimiterǁreset__mutmut_6': xǁMCPRateLimiterǁreset__mutmut_6, 
        'xǁMCPRateLimiterǁreset__mutmut_7': xǁMCPRateLimiterǁreset__mutmut_7, 
        'xǁMCPRateLimiterǁreset__mutmut_8': xǁMCPRateLimiterǁreset__mutmut_8, 
        'xǁMCPRateLimiterǁreset__mutmut_9': xǁMCPRateLimiterǁreset__mutmut_9, 
        'xǁMCPRateLimiterǁreset__mutmut_10': xǁMCPRateLimiterǁreset__mutmut_10, 
        'xǁMCPRateLimiterǁreset__mutmut_11': xǁMCPRateLimiterǁreset__mutmut_11
    }
    
    def reset(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁMCPRateLimiterǁreset__mutmut_orig"), object.__getattribute__(self, "xǁMCPRateLimiterǁreset__mutmut_mutants"), args, kwargs, self)
        return result 
    
    reset.__signature__ = _mutmut_signature(xǁMCPRateLimiterǁreset__mutmut_orig)
    xǁMCPRateLimiterǁreset__mutmut_orig.__name__ = 'xǁMCPRateLimiterǁreset'


__all__ = ["MCPRateLimiter"]
