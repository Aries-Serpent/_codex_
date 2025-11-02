# BEGIN: CODEX_IFACE_INIT
__all__ = [
    "TokenizerAdapter",
    "HFTokenizer",
    "HFTokenizerAdapter",
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
    "build_peft_config",
    "enable_peft",
    "load_adapter_for_inference",
]


def __getattr__(name: str):  # pragma: no cover - shim for optional deps
    if name in {"TokenizerAdapter", "HFTokenizer", "HFTokenizerAdapter", "WhitespaceTokenizer"}:
        from .tokenizer import (
            HFTokenizer,
            HFTokenizerAdapter,
            TokenizerAdapter,
            WhitespaceTokenizer,
        )

        return {
            "TokenizerAdapter": TokenizerAdapter,
            "HFTokenizer": HFTokenizer,
            "HFTokenizerAdapter": HFTokenizerAdapter,
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
    if name in {"build_peft_config", "enable_peft", "load_adapter_for_inference"}:
        from .peft_hooks import build_peft_config, enable_peft, load_adapter_for_inference

        mapping = {
            "build_peft_config": build_peft_config,
            "enable_peft": enable_peft,
            "load_adapter_for_inference": load_adapter_for_inference,
        }

        return mapping[name]
    raise AttributeError(name)


def __dir__() -> list[str]:  # pragma: no cover - introspection helper
    return sorted(__all__)


# END: CODEX_IFACE_INIT
