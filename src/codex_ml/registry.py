from typing import Callable, Dict

_REG: Dict[str, Callable] = {}


def register(name: str):
    def deco(fn: Callable):
        _REG[name] = fn
        return fn

    return deco


def get(name: str) -> Callable:
    return _REG[name]
