#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codex Orchestrator: Extensibility ABCs (TokenizerAdapter, RewardModel, RLAgent),
compatibility tests, optional entry-point stubs, and docs.

Creates/updates:
- codex_ml/interfaces/{tokenizer.py,reward_model.py,rl.py,__init__.py}
- tests/test_interfaces_compat.py
- configs/interfaces.example.yaml
- docs/architecture/interfaces.md
- (optional) appends commented entry-point groups to pyproject.toml

Validations (local only):
- mypy codex_ml/interfaces
- pytest -k interfaces (skipped portions allowed)

Policy:
- DO NOT ACTIVATE ANY GitHub Actions Online files. ALL GitHub Actions such as pre-commit, validation, etc MUST EXPLICITLY RUN WITHIN THE CODEX ENVIRONMENT.
"""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CODEX = REPO / ".codex"
CODEX.mkdir(parents=True, exist_ok=True)
CHANGE_LOG = CODEX / "change_log.md"
ERRORS = CODEX / "errors.ndjson"
RESULTS = CODEX / "results.md"


def ts() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def log_change(action: str, path: Path, why: str, preview: str = "") -> None:
    if not CHANGE_LOG.exists() or CHANGE_LOG.stat().st_size == 0:
        CHANGE_LOG.write_text("# Codex Change Log\n", encoding="utf-8")
    with CHANGE_LOG.open("a", encoding="utf-8") as fh:
        fh.write(
            f"## {ts()} — {path.relative_to(REPO)}\n- **Action:** {action}\n- **Rationale:** {why}\n"
        )
        if preview:
            fh.write("```text\n" + preview[:4000] + "\n```\n")
        fh.write("\n")


def q5(step: str, err: str, ctx: str) -> None:
    rq = textwrap.dedent(
        f"""\
    Question for ChatGPT-5 {ts()}:
    While performing [{step}], encountered the following error:
    {err}
    Context: {ctx}
    What are the possible causes, and how can this be resolved while preserving intended functionality?
    """
    )
    with ERRORS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": ts(), "step": step, "error": err, "context": ctx}) + "\n")
    sys.stderr.write(rq + "\n")


def upsert(path: Path, content: str, sentinel: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and sentinel in path.read_text(encoding="utf-8", errors="ignore"):
        return
    path.write_text(content, encoding="utf-8")
    log_change("upsert", path, f"insert guarded by {sentinel}", content)


# ---------------- Interfaces ----------------
S_TOKEN = "# BEGIN: CODEX_IFACE_TOKENIZER"
TOKENIZER = f"""{S_TOKEN}
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Iterable, Optional

class TokenizerAdapter(ABC):
    \"\"\"Abstract adapter for tokenization backends.

    Implementations must provide deterministic encode/decode for reproducibility and
    expose key ids for padding and EOS handling.
    \"\"\"

    @abstractmethod
    def encode(self, text: str, *, add_special_tokens: bool = True) -> List[int]:
        \"\"\"Encode a single string into token ids.\"\"\"
        raise NotImplementedError

    def batch_encode(self, texts: Iterable[str], *, add_special_tokens: bool = True) -> List[List[int]]:
        \"\"\"Optional batch encode; default maps to encode().\"\"\"
        return [self.encode(t, add_special_tokens=add_special_tokens) for t in texts]

    @abstractmethod
    def decode(self, ids: Iterable[int], *, skip_special_tokens: bool = True) -> str:
        \"\"\"Decode token ids into a string.\"\"\"
        raise NotImplementedError

    @abstractmethod
    def vocab_size(self) -> int:
        \"\"\"Return size of vocabulary.\"\"\"
        raise NotImplementedError

    @abstractmethod
    def pad_id(self) -> int:
        \"\"\"Return padding token id.\"\"\"
        raise NotImplementedError

    @abstractmethod
    def eos_id(self) -> int:
        \"\"\"Return end-of-sequence token id.\"\"\"
        raise NotImplementedError
# END: CODEX_IFACE_TOKENIZER
"""

S_REWARD = "# BEGIN: CODEX_IFACE_REWARD"
REWARD = f"""{S_REWARD}
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional

class RewardModel(ABC):
    \"\"\"Abstract reward model producing a scalar evaluation for (prompt, completion).\"\"\"

    @abstractmethod
    def evaluate(self, prompt: str, completion: str, *, metadata: Optional[Mapping[str, Any]] = None) -> float:
        \"\"\"Return a scalar reward (higher is better).\"\"\"
        raise NotImplementedError

    def batch_evaluate(self, pairs: list[tuple[str, str]], *, metadatas: Optional[list[Optional[Mapping[str, Any]]]] = None) -> list[float]:
        \"\"\"Optional batch evaluation; default maps to evaluate().\"\"\"
        res: list[float] = []
        for i, (p, c) in enumerate(pairs):
            md = metadatas[i] if metadatas and i < len(metadatas) else None
            res.append(self.evaluate(p, c, metadata=md))
        return res

    @abstractmethod
    def learn(self, data: Any) -> dict[str, float]:
        \"\"\"Update model parameters from data and return training metrics.\"\"\"
        raise NotImplementedError
# END: CODEX_IFACE_REWARD
"""

S_RL = "# BEGIN: CODEX_IFACE_RL"
RL = f"""{S_RL}
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Mapping

class RLAgent(ABC):
    \"\"\"Abstract RL agent for text generation or other environments.\"\"\"

    @abstractmethod
    def act(self, state: Any) -> Any:
        \"\"\"Choose an action for the given state.\"\"\"
        raise NotImplementedError

    @abstractmethod
    def update(self, trajectory: Mapping[str, Any]) -> dict[str, float]:
        \"\"\"Update agent from a trajectory and return metrics (e.g., loss).\"\"\"
        raise NotImplementedError

    @abstractmethod
    def save(self, path: str) -> None:
        \"\"\"Persist agent state.\"\"\"
        raise NotImplementedError

    @abstractmethod
    def load(self, path: str) -> None:
        \"\"\"Restore agent state.\"\"\"
        raise NotImplementedError
# END: CODEX_IFACE_RL
"""

S_INIT = "# BEGIN: CODEX_IFACE_INIT"
INIT = f"""{S_INIT}
from .tokenizer import TokenizerAdapter
from .reward_model import RewardModel
from .rl import RLAgent

__all__ = ["TokenizerAdapter", "RewardModel", "RLAgent"]
# END: CODEX_IFACE_INIT
"""

# ---------------- Tests ----------------
S_TESTS = "# BEGIN: CODEX_IFACE_TESTS"
TESTS = (
    S_TESTS
    + """
import importlib, json, os, types, pytest, yaml
from typing import Any, Mapping, Optional
from codex_ml.interfaces import TokenizerAdapter, RewardModel, RLAgent

# Configuration:
# Provide module paths via environment or a config file consumed elsewhere.
CFG_PATH = os.getenv("CODEX_INTERFACES_CFG", "configs/interfaces.yaml")
if os.path.exists(CFG_PATH):
    with open(CFG_PATH, "r", encoding="utf-8") as fh:
        _cfg = yaml.safe_load(fh) or {{}}
    _map = {{
        "tokenizer": ("CODEX_TOKENIZER_PATH", "CODEX_TOKENIZER_KWARGS"),
        "reward_model": ("CODEX_REWARD_PATH", "CODEX_REWARD_KWARGS"),
        "rl_agent": ("CODEX_RL_PATH", "CODEX_RL_KWARGS"),
    }}
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

TOK_PATH = os.getenv("CODEX_TOKENIZER_PATH")   # e.g., "yourpkg.tokenizers.hf:HFTokenizer"
RWD_PATH = os.getenv("CODEX_REWARD_PATH")      # e.g., "yourpkg.rewards.simple:SimpleReward"
RL_PATH  = os.getenv("CODEX_RL_PATH")          # e.g., "yourpkg.rl.ppo:PPOAgent"

def _load(path: str) -> Any:
    mod, cls = path.split(":")
    m = importlib.import_module(mod)
    return getattr(m, cls)

def _kwargs(env: str) -> dict:
    data = os.getenv(env)
    return json.loads(data) if data else {{}}

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
    a = inst.act({{"obs": 1}})
    assert a is not None
    metrics = inst.update({{"states": [], "actions": [], "rewards": []}})
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
"""
)

# ---------------- Config example ----------------
S_CFG = "# BEGIN: CODEX_IFACE_CONFIG"
CFG = (
    S_CFG
    + """
# Example mapping of interface groups to concrete implementations
tokenizer:
  path: yourpkg.tokenizers.hf:HFTokenizer   # TODO: replace with actual module:class
  kwargs: {}
reward_model:
  path: yourpkg.rewards.simple:SimpleReward
  kwargs: {}
rl_agent:
  path: yourpkg.rl.ppo:PPOAgent
  kwargs: {}
# END: CODEX_IFACE_CONFIG
"""
)

# ---------------- Docs ----------------
S_DOCS = "<!-- BEGIN: CODEX_IFACE_DOCS -->"
DOCS = f"""{S_DOCS}
# Interfaces & Extensibility

This project defines abstract interfaces to allow **swappable implementations** without code changes.

## Interfaces
- `TokenizerAdapter` — encode/decode, vocab_size/pad_id/eos_id, optional batch_encode.
- `RewardModel` — evaluate(prompt, completion, metadata?), learn(data)->metrics, optional batch_evaluate.
- `RLAgent` — act, update(trajectory)->metrics, save/load.

## Swapping Implementations
1. Provide implementation import paths (e.g., `pkg.module:Class`) via environment:
   - `CODEX_TOKENIZER_PATH`, `CODEX_REWARD_PATH`, `CODEX_RL_PATH`
2. Or maintain a config like `configs/interfaces.yaml` and load them at runtime.

## Optional Plugins (entry points)
Projects can expose entry points under:
- `codex_ml.tokenizers`, `codex_ml.reward_models`, `codex_ml.rl_agents`

> Entry-point stubs are commented in `pyproject.toml` to avoid unintended side effects. Enable explicitly if desired.

## Testing Compatibility
- Run `pytest -q -k interfaces` after setting env vars to your implementations.
- Tests assert basic contract compliance.

> **Policy:** DO NOT ACTIVATE ANY GitHub Actions Online files. All validations run locally in the Codex environment.
"""

# ---------------- pyproject entry-point stub ----------------
S_TOML = "# BEGIN: CODEX_IFACE_ENTRYPOINTS"
TOML = f"""{S_TOML}
# [project.entry-points."codex_ml.tokenizers"]
# mytokenizer = "yourpkg.tokenizers.hf:HFTokenizer"
# [project.entry-points."codex_ml.reward_models"]
# simple = "yourpkg.rewards.simple:SimpleReward"
# [project.entry-points."codex_ml.rl_agents"]
# ppo = "yourpkg.rl.ppo:PPOAgent"
# END: CODEX_IFACE_ENTRYPOINTS
"""


def apply():
    try:
        upsert(
            REPO / "src" / "codex_ml" / "interfaces" / "tokenizer.py",
            TOKENIZER,
            S_TOKEN,
        )
        upsert(
            REPO / "src" / "codex_ml" / "interfaces" / "reward_model.py",
            REWARD,
            S_REWARD,
        )
        upsert(REPO / "src" / "codex_ml" / "interfaces" / "rl.py", RL, S_RL)
        upsert(REPO / "src" / "codex_ml" / "interfaces" / "__init__.py", INIT, S_INIT)
        upsert(REPO / "tests" / "test_interfaces_compat.py", TESTS, S_TESTS)
        upsert(REPO / "configs" / "interfaces.example.yaml", CFG, S_CFG)
        upsert(REPO / "docs" / "architecture" / "interfaces.md", DOCS, S_DOCS)
        # Append entry-point stub to pyproject.toml (create if absent)
        pt = REPO / "pyproject.toml"
        if pt.exists():
            txt = pt.read_text(encoding="utf-8")
            if S_TOML not in txt:
                txt = (txt + ("\n" if not txt.endswith("\n") else "")) + TOML + "\n"
                pt.write_text(txt, encoding="utf-8")
                log_change("edit", pt, "append commented entry-point groups", TOML)
        else:
            pt.write_text(TOML + "\n", encoding="utf-8")
            log_change(
                "create",
                pt,
                "create minimal pyproject with commented entry-point stub",
                TOML,
            )
    except Exception as e:
        q5("3: Best-Effort Construction — write files", str(e), f"path={REPO}")


def _scan_repo():
    # Best-effort: list likely modules for future mapping
    patterns = ["token", "reward", "rl", "ppo", "agent"]
    found = []
    for p in REPO.rglob("*.py"):
        rel = str(p.relative_to(REPO))
        if any(k in rel.lower() for k in patterns):
            found.append(rel)
    with RESULTS.open("a", encoding="utf-8") as fh:
        fh.write(f"\n# Repo scan {ts()}\n")
        for f in sorted(found)[:200]:
            fh.write(f"- {f}\n")


def validate():
    _scan_repo()
    with RESULTS.open("a", encoding="utf-8") as fh:
        fh.write(f"\n# Validation {ts()}\n")
        steps = [
            ("mypy interfaces", ["mypy", "src/codex_ml/interfaces"]),
            (
                "pytest interfaces",
                ["pytest", "tests/test_interfaces_compat.py", "-q", "--maxfail=1"],
            ),
        ]
        for name, cmd in steps:
            fh.write(f"\n## {name}\n```\n")
            try:
                p = subprocess.run(cmd, capture_output=True, text=True)
                fh.write(p.stdout + p.stderr + f"\n(exit={p.returncode})\n")
                if p.returncode != 0:
                    q5(
                        f"6: Finalization — {name}",
                        f"exit {p.returncode}",
                        " ".join(cmd),
                    )
            except Exception as e:
                fh.write(f"ERROR: {e}\n")
                q5(f"6: Finalization — {name}", str(e), " ".join(cmd))
            fh.write("\n```\n")


def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--apply",
        action="store_true",
        help="create interfaces, compat tests, docs, and entry-point stubs",
    )
    ap.add_argument("--validate", action="store_true", help="run local validations (mypy/pytest)")
    args = ap.parse_args()
    if args.apply:
        apply()
    if args.validate:
        validate()
    if not (args.apply or args.validate):
        print("Usage: --apply [--validate]")


if __name__ == "__main__":
    main()
