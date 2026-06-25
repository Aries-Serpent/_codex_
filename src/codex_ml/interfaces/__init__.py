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
    HFTokenizer = None
    HFTokenizerAdapter = None
    TokenizerAdapter = None
    WhitespaceTokenizer = None

try:
    from .reward_model import HeuristicRewardModel, RewardModel
except (ImportError, AttributeError):  # pragma: no cover - optional dependency guard
    RewardModel = None
    HeuristicRewardModel = None

try:
    from .rl import BanditRLAgent, RLAgent
except (ImportError, AttributeError):  # pragma: no cover - optional dependency guard
    RLAgent = None
    BanditRLAgent = None

from .registry import apply_config, get, get_component, load_component, register

try:
    from .peft_hooks import build_peft_config, enable_peft, load_adapter_for_inference
except (ImportError, AttributeError):  # pragma: no cover - optional dependency guard
    build_peft_config = None
    enable_peft = None
    load_adapter_for_inference = None

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
