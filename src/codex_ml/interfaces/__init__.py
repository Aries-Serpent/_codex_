# BEGIN: CODEX_IFACE_INIT
__all__ = [
    "TokenizerAdapter",
    "HFTokenizer",
    "WhitespaceTokenizer",
    "RewardModel",
    "HeuristicRewardModel",
    "RLAgent",
    "BanditRLAgent",
    "register",
    "get",
    "load_component",
    "get_component",
    "apply_config",
]


def __getattr__(name: str):  # pragma: no cover - shim for optional deps
    if name in {"TokenizerAdapter", "HFTokenizer", "WhitespaceTokenizer"}:
        from .tokenizer import HFTokenizer, TokenizerAdapter, WhitespaceTokenizer

        return {
            "TokenizerAdapter": TokenizerAdapter,
            "HFTokenizer": HFTokenizer,
            "WhitespaceTokenizer": WhitespaceTokenizer,
        }[name]
    if name in {"RewardModel", "HeuristicRewardModel"}:
        from .reward_model import HeuristicRewardModel, RewardModel

        return {"RewardModel": RewardModel, "HeuristicRewardModel": HeuristicRewardModel}[name]
    if name in {"RLAgent", "BanditRLAgent"}:
        from .rl import BanditRLAgent, RLAgent

        return {"RLAgent": RLAgent, "BanditRLAgent": BanditRLAgent}[name]
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
