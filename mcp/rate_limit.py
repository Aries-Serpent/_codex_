"""Token bucket rate limiter with deterministic safeguards."""

from __future__ import annotations

import json
import os
import time
from typing import Dict, Tuple

from .safeguards import compute_secure_checksum, seeded_rng


class MCPRateLimiter:
    """Token-bucket rate limiter for MCP tool invocations."""

    def __init__(self, rate: float, capacity: int, seed: int | None = None) -> None:
        self.rate = rate
        self.capacity = capacity
        self._rng = seeded_rng(seed)
        self._usage: Dict[Tuple[str, str], Tuple[float, float]] = {}
        self._offline = os.environ.get("MCP_OFFLINE", "false").lower() in {"1", "true"}

    def allow(self, principal_id: str, tool_name: str) -> bool:
        key = (principal_id, tool_name)
        now = time.time()
        tokens, last_ts = self._usage.get(key, (self.capacity, now))
        elapsed = now - last_ts
        tokens = min(self.capacity, tokens + elapsed * self.rate + self._rng.random() * 1e-3)
        if tokens < 1:
            self._usage[key] = (tokens, now)
            return False
        self._usage[key] = (tokens - 1, now)
        return True

    def reset(self, principal_id: str | None = None, tool_name: str | None = None) -> None:
        if principal_id is None and tool_name is None:
            self._usage.clear()
            return
        keys_to_remove = []
        for key in self._usage.keys():
            if (principal_id is None or key[0] == principal_id) and (
                tool_name is None or key[1] == tool_name
            ):
                keys_to_remove.append(key)
        for key in keys_to_remove:
            del self._usage[key]

    def snapshot_state(self) -> Dict[str, str]:
        """Return a checksum-protected snapshot for offline persistence."""

        serialized_usage = {
            f"{principal}|{tool}": value
            for (principal, tool), value in self._usage.items()
        }
        payload = json.dumps({"usage": serialized_usage}, default=list, sort_keys=True)
        checksum = compute_secure_checksum(payload)
        return {"checksum": checksum, "offline": str(self._offline).lower(), "payload": payload}

    def restore_state(self, payload: str, checksum: str) -> None:
        """Restore rate limit state if checksum matches."""

        if compute_secure_checksum(payload) != checksum:
            return
        data = json.loads(payload)
        usage = {}
        for key, value in data.get("usage", {}).items():
            principal, tool = key.split("|", 1)
            usage[(principal, tool)] = tuple(value)
        self._usage = usage
