# BEGIN: CODEX_IFACE_TESTS
import importlib
import os
from typing import Any

import pytest

from codex_ml.interfaces import TokenizerAdapter

# Configuration:
# Provide module paths via environment or a config file consumed elsewhere.
TOK_PATH = os.getenv(
    "CODEX_TOKENIZER_PATH"
)  # e.g., "yourpkg.tokenizers.hf:HFTokenizer"
RWD_PATH = os.getenv("CODEX_REWARD_PATH")  # e.g., "yourpkg.rewards.simple:SimpleReward"
RL_PATH = os.getenv("CODEX_RL_PATH")  # e.g., "yourpkg.rl.ppo:PPOAgent"


def _load(path: str) -> Any:
    mod, cls = path.split(":")
    m = importlib.import_module(mod)
    return getattr(m, cls)


@pytest.mark.skipif(TOK_PATH is None, reason="Tokenizer implementation not provided")
def test_tokenizer_adapter_contract():
    cls = _load(TOK_PATH)
    inst = cls()  # TODO: supply kwargs if needed
    assert isinstance(inst, TokenizerAdapter)
    ids = inst.encode("hello")
    assert isinstance(ids, list) and all(isinstance(i, int) for i in ids)
    txt = inst.decode(ids)
    assert isinstance(txt, str)
    assert isinstance(inst.vocab_size(), int)
    assert isinstance(inst.pad_id(), int)
    assert isinstance(inst.eos_id(), int)


@pytest.mark.skipif(RWD_PATH is None, reason="RewardModel implementation not provided")
def test_reward_model_contract():
    cls = _load(RWD_PATH)
    inst = cls()  # TODO: supply kwargs if needed
    score = inst.score("prompt", "completion")
    assert isinstance(score, float)


@pytest.mark.skipif(RL_PATH is None, reason="RLAgent implementation not provided")
def test_rl_agent_contract(tmp_path):
    cls = _load(RL_PATH)
    inst = cls()  # TODO: supply kwargs if needed
    a = inst.select_action({"obs": 1})
    assert a is not None
    metrics = inst.update({"states": [], "actions": [], "rewards": []})
    assert isinstance(metrics, dict)
    p = tmp_path / "agent.bin"
    inst.save(str(p))
    assert p.exists()
    inst.load(str(p))


# --- Codex prompts (for future completion) ---
# TODO[Codex]: If your implementations require constructor arguments, update tests to pass minimal viable config.
# TODO[Codex]: Wire a config reader to set CODEX_*_PATH from configs/interfaces.yaml during pytest collection.
# END: CODEX_IFACE_TESTS
