"""Stub numpy module for optional dependency gating."""

class _Random:
    @staticmethod
    def seed(seed):
        return None


random = _Random()
