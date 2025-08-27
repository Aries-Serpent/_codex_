from typing import Callable, Dict

_REG: Dict[str, Callable[..., None]] = {}

def register(name: str):
    def deco(fn: Callable[..., None]):
        _REG[name] = fn
        return fn
    return deco

def run(name: str, **kwargs):
    fn = _REG.get(name)
    if not fn:
        raise KeyError(f"step not found: {name}")
    return fn(**kwargs)

def names() -> list[str]:
    return sorted(_REG.keys())
