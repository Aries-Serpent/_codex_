# Minimal retry / backoff helper (exponential backoff with jitter)
import functools
import logging
logger = logging.getLogger(__name__)
import secrets
import time
from typing import Callable, Tuple

_secure_random = secrets.SystemRandom()

def retry_on_exception(
    exceptions: Tuple[type, ...] = (Exception,),
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
