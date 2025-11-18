import time
from typing import Dict, Tuple


class MCPRateLimiter:
    """
    Token-bucket rate limiter for MCP tool invocations.
    Allows up to `capacity` tokens, refilling at `rate` tokens per second.
    """
    def __init__(self, rate: float, capacity: int) -> None:
        self.rate = rate
        self.capacity = capacity
        # Store usage as: (tokens, last_timestamp) per principal-tool key
        self._usage: Dict[Tuple[str, str], Tuple[float, float]] = {}

    def allow(self, principal_id: str, tool_name: str) -> bool:
        """
        Attempt to consume a token for the given principal and tool.
        Returns True if allowed (token consumed or within burst), False if rate limit exceeded.
        """
        key = (principal_id, tool_name)
        now = time.time()
        tokens, last_ts = self._usage.get(key, (self.capacity, now))
        # Refill tokens since last timestamp
        elapsed = now - last_ts
        tokens = min(self.capacity, tokens + elapsed * self.rate)
        if tokens < 1:
            # Not enough tokens to allow the request
            self._usage[key] = (tokens, now)
            return False
        # Consume one token and allow
        self._usage[key] = (tokens - 1, now)
        return True
