"""
Retries Module

This module provides functionality for retries.

Usage:
    from mcp.retries import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

# Minimal retry / backoff helper (exponential backoff with jitter)
import functools
import logging
logger = logging.getLogger(__name__)
import secrets
import time
from typing import Callable

_secure_random = secrets.SystemRandom()
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

def x_retry_on_exception__mutmut_orig(
    exceptions: tuple[type, ...] = (Exception,),
    tries: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 10.0,
    jitter: float = 0.1,
):
    def decorator(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    attempt += 1
                    if attempt >= tries:
                        raise
                    delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                    delay = delay * (1 + (_secure_random.random() * jitter))
                    time.sleep(delay)

        return wrapper

    return decorator

def x_retry_on_exception__mutmut_1(
    exceptions: tuple[type, ...] = (Exception,),
    tries: int = 4,
    base_delay: float = 0.5,
    max_delay: float = 10.0,
    jitter: float = 0.1,
):
    def decorator(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    attempt += 1
                    if attempt >= tries:
                        raise
                    delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                    delay = delay * (1 + (_secure_random.random() * jitter))
                    time.sleep(delay)

        return wrapper

    return decorator

def x_retry_on_exception__mutmut_2(
    exceptions: tuple[type, ...] = (Exception,),
    tries: int = 3,
    base_delay: float = 1.5,
    max_delay: float = 10.0,
    jitter: float = 0.1,
):
    def decorator(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    attempt += 1
                    if attempt >= tries:
                        raise
                    delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                    delay = delay * (1 + (_secure_random.random() * jitter))
                    time.sleep(delay)

        return wrapper

    return decorator

def x_retry_on_exception__mutmut_3(
    exceptions: tuple[type, ...] = (Exception,),
    tries: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 11.0,
    jitter: float = 0.1,
):
    def decorator(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    attempt += 1
                    if attempt >= tries:
                        raise
                    delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                    delay = delay * (1 + (_secure_random.random() * jitter))
                    time.sleep(delay)

        return wrapper

    return decorator

def x_retry_on_exception__mutmut_4(
    exceptions: tuple[type, ...] = (Exception,),
    tries: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 10.0,
    jitter: float = 1.1,
):
    def decorator(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    attempt += 1
                    if attempt >= tries:
                        raise
                    delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                    delay = delay * (1 + (_secure_random.random() * jitter))
                    time.sleep(delay)

        return wrapper

    return decorator

x_retry_on_exception__mutmut_mutants : ClassVar[MutantDict] = {
'x_retry_on_exception__mutmut_1': x_retry_on_exception__mutmut_1, 
    'x_retry_on_exception__mutmut_2': x_retry_on_exception__mutmut_2, 
    'x_retry_on_exception__mutmut_3': x_retry_on_exception__mutmut_3, 
    'x_retry_on_exception__mutmut_4': x_retry_on_exception__mutmut_4
}

def retry_on_exception(*args, **kwargs):
    result = _mutmut_trampoline(x_retry_on_exception__mutmut_orig, x_retry_on_exception__mutmut_mutants, args, kwargs)
    return result 

retry_on_exception.__signature__ = _mutmut_signature(x_retry_on_exception__mutmut_orig)
x_retry_on_exception__mutmut_orig.__name__ = 'x_retry_on_exception'
