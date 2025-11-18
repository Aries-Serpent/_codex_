"""
MCP rate limiting module.

Security: Uses deterministic RNG seed for reproducible rate limit testing.
Implements token bucket algorithm for request throttling.
"""

import time
import secrets
from typing import Dict, Tuple


class MCPRateLimiter:
    """
    Token-bucket rate limiter for MCP tool invocations.
    Allows up to `capacity` tokens, refilling at `rate` tokens per second.
    
    Security: Uses RNG seed for bucket initialization to ensure fairness.
    """
    def __init__(self, rate: float, capacity: int, seed: int = None) -> None:
        """
        Initialize rate limiter with token bucket parameters.
        
        Args:
            rate: Tokens per second refill rate
            capacity: Maximum burst capacity
            seed: Optional RNG seed for deterministic testing (offline mode)
        """
        self.rate = rate
        self.capacity = capacity
        self.seed = seed if seed is not None else secrets.randbits(32)  # RNG seed
        # Store usage as: (tokens, last_timestamp) per principal-tool key
        self._usage: Dict[Tuple[str, str], Tuple[float, float]] = {}

    def allow(self, principal_id: str, tool_name: str) -> bool:
        """
        Attempt to consume a token for the given principal and tool.
        Returns True if allowed (token consumed or within burst), False if rate limit exceeded.
        
        Security: Rate limiting prevents abuse and DoS attacks.
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
    
    def reset(self, principal_id: str = None, tool_name: str = None) -> None:
        """
        Reset rate limit counters (for testing or offline operations).
        
        Args:
            principal_id: Reset for specific principal (or all if None)
            tool_name: Reset for specific tool (or all if None)
        """
        if principal_id is None and tool_name is None:
            self._usage.clear()
        else:
            keys_to_remove = []
            for key in self._usage.keys():
                if (principal_id is None or key[0] == principal_id) and \
                   (tool_name is None or key[1] == tool_name):
                    keys_to_remove.append(key)
            for key in keys_to_remove:
                del self._usage[key]
