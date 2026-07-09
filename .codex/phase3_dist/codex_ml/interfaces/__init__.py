"""
  Init   Module

This module provides functionality for   init  .

Usage:
    from interfaces.__init__ import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

# BEGIN: CODEX_IFACE_INIT
try:
    from .tokenizer import (
        HFTokenizer,
        HFTokenizerAdapter,
        TokenizerAdapter,
        WhitespaceTokenizer,
    )
except (ImportError, AttributeError):  # pragma: no cover - optional dependency guard
    HFTokenizer = None  # type: ignore[misc,assignment]
    HFTokenizerAdapter = None
    TokenizerAdapter = None  # type: ignore[misc,assignment]
    WhitespaceTokenizer = None  # type: ignore[misc,assignment]

try:
    from .reward_model import HeuristicRewardModel, RewardModel
except (ImportError, AttributeError):  # pragma: no cover - optional dependency guard
    RewardModel = None  # type: ignore[misc,assignment]
    HeuristicRewardModel = None  # type: ignore[misc,assignment]

try:
    from .rl import BanditRLAgent, RLAgent
except (ImportError, AttributeError):  # pragma: no cover - optional dependency guard
    RLAgent = None  # type: ignore[misc,assignment]
    BanditRLAgent = None  # type: ignore[misc,assignment]

from .registry import apply_config, get, get_component, load_component, register

try:
    from .peft_hooks import build_peft_config, enable_peft, load_adapter_for_inference
except (ImportError, AttributeError):  # pragma: no cover - optional dependency guard
    build_peft_config = None  # type: ignore[assignment]
    enable_peft = None  # type: ignore[assignment]
    load_adapter_for_inference = None  # type: ignore[assignment]

__all__ = [
    "BanditRLAgent",
    "HFTokenizer",
    "HFTokenizerAdapter",
    "HeuristicRewardModel",
    "RLAgent",
    "RewardModel",
    "TokenizerAdapter",
    "WhitespaceTokenizer",
    "apply_config",
    "build_peft_config",
    "enable_peft",
    "get",
    "get_component",
    "load_adapter_for_inference",
    "load_component",
    "register",
]


def __dir__() -> list[str]:  # pragma: no cover - introspection helper
    return sorted(__all__)


# END: CODEX_IFACE_INIT
