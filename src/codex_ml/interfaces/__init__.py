# BEGIN: CODEX_IFACE_INIT
__all__ = [
    "TokenizerAdapter",
    "HFTokenizer",
    "RewardModel",
    "RLAgent",
    "register",
    "get",
    "load_component",
    "get_component",
    "apply_config",
]


def __getattr__(name: str):  # pragma: no cover - shim for optional deps
    if name in {"TokenizerAdapter", "HFTokenizer"}:
        from .tokenizer import HFTokenizer, TokenizerAdapter

        return {"TokenizerAdapter": TokenizerAdapter, "HFTokenizer": HFTokenizer}[name]
    if name in {"RewardModel"}:
        from .reward_model import RewardModel

        return RewardModel
    if name in {"RLAgent"}:
        from .rl import RLAgent

        return RLAgent
    if name in {"register", "get", "load_component", "get_component", "apply_config"}:
        from . import registry

        mapping = {
            "register": registry.register,
            "get": registry.get,
            "load_component": registry.load_component,
            "get_component": registry.get_component,
            "apply_config": registry.apply_config,
        }

        return mapping[name]
    raise AttributeError(name)


def __dir__() -> list[str]:  # pragma: no cover - introspection helper
    return sorted(__all__)


# END: CODEX_IFACE_INIT
