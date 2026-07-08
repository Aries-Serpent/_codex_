"""
Test Track A

Test module for track a.
"""

from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("tokenizers")
pytest.importorskip("transformers")

accelerate_available = importlib.util.find_spec("accelerate") is not None

from fastapi.testclient import TestClient
from tokenizers import Tokenizer
from tokenizers.models import WordLevel
from tokenizers.pre_tokenizers import Whitespace

from cli import train_codex
from transformers import AutoModelForCausalLM, GPT2Config

api_app = importlib.import_module("codex.api.app")
from codex_ml.security import DenylistEnforcer, DenylistViolation
from codex_ml.utils import checkpointing
from src.tokenization.loader import load_tokenizer


@pytest.fixture()
def tokenizer_path(tmp_path: Path) -> Path:
    tokenizer = Tokenizer(WordLevel({"hello": 0, "world": 1, "codex": 2}, unk_token="[UNK]"))
    tokenizer.pre_tokenizer = Whitespace()
    out = tmp_path / "tokenizer.json"
    tokenizer.save(str(out))
    return out


def test_load_tokenizer_from_file(tokenizer_path: Path) -> None:
    tokenizer = load_tokenizer({"tokenizer_file": tokenizer_path})
    ids = tokenizer("hello world", return_attention_mask=False)["input_ids"]
    assert ids[0] == 0 and ids[1] == 1, "Condition must be true"
    assert tokenizer.pad_token_id is not None, "pad_token_id must be initialized"


def test_predict_endpoint_generates_text(tokenizer_path: Path) -> None:
    tokenizer = load_tokenizer({"tokenizer_file": tokenizer_path})
    model = AutoModelForCausalLM.from_config(
        GPT2Config(vocab_size=tokenizer.vocab_size, n_embd=32, n_layer=1, n_head=1)
    )
    model.eval()
    enforcer = DenylistEnforcer.from_yaml(Path("policies/denylist.yaml"))
    api_app.configure_runtime(model=model, tokenizer=tokenizer, enforcer=enforcer)

    client = TestClient(api_app.app)
    response = client.post("/predict", json={"prompt": "hello"})
    assert response.status_code == 200, "Response must not be empty"
    payload = response.json()
    assert payload["output"].strip() != "", "Condition must be true"


def test_denylist_blocks_prompt() -> None:
    enforcer = DenylistEnforcer.from_yaml(Path("policies/denylist.yaml"))
    with pytest.raises(DenylistViolation):
        enforcer.ensure_allowed("my ssn is 123-45-6789")


@pytest.mark.skipif(not accelerate_available, reason="accelerate is required for Trainer-based CLI")
def test_training_cli_checkpoint_cycle(tmp_path: Path, tokenizer_path: Path) -> None:
    train_file = tmp_path / "train.txt"
    train_file.write_text("hello codex\nhello world\n", encoding="utf-8")

    result = train_codex.run_training(
        {
            "train_file": str(train_file),
            "output_dir": str(tmp_path / "run1"),
            "tokenizer_file": str(tokenizer_path),
            "num_train_epochs": 1,
            "max_steps": 2,
        }
    )
    assert result.checkpoint_path.exists(), "Result must not be empty"
    payload = checkpointing.load_training_checkpoint(result.checkpoint_path)
    assert "model_state_dict" in payload, "Condition must be true"

    resumed = train_codex.run_training(
        {
            "train_file": str(train_file),
            "output_dir": str(tmp_path / "run2"),
            "tokenizer_file": str(tokenizer_path),
            "max_steps": 1,
            "codex_resume_checkpoint": str(result.checkpoint_path),
        }
    )
    assert resumed.checkpoint_path.exists(), "Condition must be true"
