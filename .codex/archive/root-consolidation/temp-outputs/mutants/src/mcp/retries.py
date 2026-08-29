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
import secrets
import time
from collections.abc import Callable

logger = logging.getLogger(__name__)
_secure_random = secrets.SystemRandom()


def retry_on_exception(
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
