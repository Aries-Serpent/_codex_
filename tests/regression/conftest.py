"""Shared fixtures for the regression test suite.

All fixtures in this module are available to every test file under
``tests/regression/``.  Fixtures are designed to be:

- Fast (no network I/O, no GPU required)
- Deterministic (fixed seeds)
- Self-contained (no side-effects beyond the tmp_path sandbox)
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

# ── Ensure ``src/`` is importable in all pytest invocation contexts ─────────
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


# ── Pipeline corpus & demo fixtures ─────────────────────────────────────────

CORPUS: list[str] = [
    "machine learning enables intelligent systems",
    "deep learning uses neural networks",
    "natural language processing understands text",
    "reinforcement learning optimises rewards",
    "supervised learning maps inputs to outputs",
]

DEMOS: list[dict[str, Any]] = [
    {"input": "explain machine learning", "completion": "machine learning"},
    {"input": "what is deep learning", "completion": "deep learning neural"},
    {"input": "define NLP", "completion": "natural language processing"},
]

PREFS: list[tuple[str, str, str, int]] = [
    ("machine learning is helpful", "machine learning is bad", "machine", 1),
    ("deep learning rocks", "deep learning sucks", "deep", 1),
    ("reinforcement works well", "reinforcement fails often", "reinforcement", 0),
]


@pytest.fixture(scope="session")
def corpus() -> list[str]:
    """Fixed training corpus for pipeline stability tests."""
    return CORPUS[:]


@pytest.fixture(scope="session")
def demos() -> list[dict[str, Any]]:
    """Fixed demonstration examples for SFT."""
    return DEMOS[:]


@pytest.fixture(scope="session")
def prefs() -> list[tuple[str, str, str, int]]:
    """Fixed preference pairs for RLHF."""
    return PREFS[:]


@pytest.fixture(scope="session")
def pretrained_model(corpus):
    """A pre-trained ModelHandle using a fixed seed — reused across tests."""
    from codex_ml.symbolic_pipeline import PretrainCfg, pretrain

    cfg = PretrainCfg(epochs=1, seed=42)
    return pretrain(corpus, cfg)


@pytest.fixture(scope="session")
def pipeline_result(corpus, demos, prefs):
    """Full pipeline run result dict — computed once per session."""
    from codex_ml.symbolic_pipeline import (
        PretrainCfg,
        RewardModelCfg,
        RLHFCfg,
        SFTCfg,
        run_codex_symbolic_pipeline,
    )

    return run_codex_symbolic_pipeline(
        corpus=corpus,
        demos=demos,
        prefs=prefs,
        pre_cfg=PretrainCfg(epochs=1, seed=42),
        sft_cfg=SFTCfg(epochs=1, seed=42),
        rm_cfg=RewardModelCfg(epochs=2, seed=42),
        rlhf_cfg=RLHFCfg(epochs=1, seed=42),
    )


@pytest.fixture()
def base_train_config() -> dict[str, Any]:
    """Minimal valid TrainConfig keyword arguments."""
    return {
        "model_name": "test-model",
        "learning_rate": 1e-3,
        "batch_size": 4,
        "epochs": 1,
        "seed": 42,
    }


@pytest.fixture()
def dashboard_client():
    """FastAPI TestClient for the monitoring dashboard API."""
    from fastapi.testclient import TestClient

    from monitoring.dashboard_api import app

    with TestClient(app, raise_server_exceptions=True) as client:
        yield client


@pytest.fixture()
def checkpoint_dir(tmp_path: Path) -> Path:
    """An empty directory for checkpoint round-trip tests."""
    d = tmp_path / "checkpoints"
    d.mkdir()
    return d


@pytest.fixture()
def sample_checkpoint_meta() -> dict[str, Any]:
    """Canonical checkpoint metadata used in round-trip tests."""
    return {
        "epoch": 3,
        "step": 150,
        "best_metric": 0.923,
        "model_name": "test-model",
        "schema_version": "1.0",
        "seed": 42,
    }
