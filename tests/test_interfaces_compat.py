# BEGIN: CODEX_IFACE_TESTS
import importlib
import json
import os
from typing import Any, Mapping, Optional

import pytest
import yaml

from codex_ml.interfaces import RewardModel, RLAgent, TokenizerAdapter

# Configuration:
# Provide module paths via environment or a config file consumed elsewhere.
CFG_PATH = os.getenv("CODEX_INTERFACES_CFG", "configs/interfaces.yaml")
if os.path.exists(CFG_PATH):
    with open(CFG_PATH, "r", encoding="utf-8") as fh:
        _cfg = yaml.safe_load(fh) or {}
    _map = {
        "tokenizer": ("CODEX_TOKENIZER_PATH", "CODEX_TOKENIZER_KWARGS"),
        "reward_model": ("CODEX_REWARD_PATH", "CODEX_REWARD_KWARGS"),
        "rl_agent": ("CODEX_RL_PATH", "CODEX_RL_KWARGS"),
    }
    for k, (p_env, k_env) in _map.items():
        if k in _cfg:
            entry = _cfg[k]
            if isinstance(entry, str):
                os.environ.setdefault(p_env, entry)
            else:
                path = entry.get("path")
                kwargs = entry.get("kwargs")
                if path:
                    os.environ.setdefault(p_env, path)
                if kwargs:
                    os.environ.setdefault(k_env, json.dumps(kwargs))

TOK_PATH = os.getenv("CODEX_TOKENIZER_PATH")  # e.g., "yourpkg.tokenizers.hf:HFTokenizer"
RWD_PATH = os.getenv("CODEX_REWARD_PATH")  # e.g., "yourpkg.rewards.simple:SimpleReward"
RL_PATH = os.getenv("CODEX_RL_PATH")  # e.g., "yourpkg.rl.ppo:PPOAgent"


def _load(path: str) -> Any:
    mod, cls = path.split(":")
    m = importlib.import_module(mod)
    return getattr(m, cls)


def _kwargs(env: str) -> dict:
    data = os.getenv(env)
    return json.loads(data) if data else {}


TOK_KW = _kwargs("CODEX_TOKENIZER_KWARGS")
RWD_KW = _kwargs("CODEX_REWARD_KWARGS")
RL_KW = _kwargs("CODEX_RL_KWARGS")


@pytest.mark.skipif(TOK_PATH is None, reason="Tokenizer implementation not provided")
def test_tokenizer_adapter_contract():
    cls = _load(TOK_PATH)
    inst = cls(**TOK_KW)
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
    inst = cls(**RWD_KW)
    score = inst.evaluate("prompt", "completion")
    assert isinstance(score, float)
    metrics = inst.learn([("prompt", "completion", 1.0)])
    assert isinstance(metrics, dict)


@pytest.mark.skipif(RL_PATH is None, reason="RLAgent implementation not provided")
def test_rl_agent_contract(tmp_path):
    cls = _load(RL_PATH)
    inst = cls(**RL_KW)
    a = inst.act({"obs": 1})
    assert a is not None
    metrics = inst.update({"states": [], "actions": [], "rewards": []})
    assert isinstance(metrics, dict)
    p = tmp_path / "agent.bin"
    inst.save(str(p))
    assert p.exists()
    inst.load(str(p))


class _DummyRewardModel(RewardModel):
    def evaluate(self, prompt: str, completion: str, *, metadata: Optional[Any] = None) -> float:
        return 0.0

    def learn(self, data: Any) -> dict[str, float]:
        return {"loss": 0.0}


def test_reward_model_abc():
    rm = _DummyRewardModel()
    assert isinstance(rm.evaluate("p", "c"), float)
    assert isinstance(rm.learn([]), dict)


class _DummyRLAgent(RLAgent):
    def act(self, state: Any) -> Any:
        return 1

    def update(self, trajectory: Mapping[str, Any]) -> dict[str, float]:
        return {"loss": 0.0}

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("x")

    def load(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as fh:
            fh.read()


def test_rl_agent_abc(tmp_path):
    agent = _DummyRLAgent()
    assert agent.act({}) == 1
    assert isinstance(agent.update({}), dict)
    p = tmp_path / "agent.bin"
    agent.save(str(p))
    assert p.exists()
    agent.load(str(p))


# END: CODEX_IFACE_TESTS
