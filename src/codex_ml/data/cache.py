# BEGIN: CODEX_DATA_CACHE
from __future__ import annotations

import time


class SimpleCache:
    def __init__(self, ttl_s: int = 3600, max_items: int = 1000):
        self.ttl, self.max = ttl_s, max_items
        self._d = {}

    def get(self, k):
        v = self._d.get(k)
        if not v:
            return None
        val, t = v
        if time.time() - t > self.ttl:
            self._d.pop(k, None)
            return None
        return val

    def set(self, k, val):
        # Guard against zero-capacity caches and eviction edge cases.
        if self.max is not None and self.max <= 0:
            return

        if self.max is not None and len(self._d) >= self.max:
            if not self._d:
                return
            self._d.pop(next(iter(self._d)))
        self._d[k] = (val, time.time())


# END: CODEX_DATA_CACHE
