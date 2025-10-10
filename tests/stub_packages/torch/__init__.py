"""Stub torch module for optional dependency gating."""

__all__ = []


def manual_seed(seed):
    return None


class _Cuda:
    @staticmethod
    def is_available():
        return False

    @staticmethod
    def manual_seed_all(seed):
        return None


class _Utils:
    pass


cuda = _Cuda()
utils = _Utils()
