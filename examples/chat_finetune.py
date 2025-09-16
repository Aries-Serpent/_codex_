"""Demonstrate chat fine-tuning with a custom trainer registration."""

from __future__ import annotations

import json
from typing import Any

from codex_ml.registry import register_trainer
from codex_ml.training import run_functional_training


def toy_chat_trainer(model, tokenizer, train_ds, val_ds, cfg):  # noqa: D401
    """Toy trainer that echoes the batch size instead of training."""

    return {
        "model": getattr(model, "__class__", type(model)).__name__,
        "tokens": int(len(train_ds["data"]["input_ids"])),
        "cfg": getattr(cfg, "__dict__", {}),
    }


def main() -> None:
    register_trainer("toy-chat", toy_chat_trainer, override=True)
    config: dict[str, Any] = {
        "model": "MiniLM",
        "training": {
            "texts": ["<s>User: hi</s><s>Assistant: hello!</s>"],
            "trainer": "toy-chat",
            "checkpoint_dir": "runs/chat-toy/checkpoints",
        },
        "tracking": {
            "output_dir": "runs/chat-toy",
            "run_name": "toy-chat",
        },
    }
    result = run_functional_training(config)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
