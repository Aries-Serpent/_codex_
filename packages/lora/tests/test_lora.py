from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from codex_lora import LoraConfig, apply_lora, load_lora


class RecordingBackend:
    def __init__(self) -> None:
        self.calls: list[tuple[object, ...]] = []

    def apply(self, model, config, *, adapter_name=None):
        self.calls.append(("apply", model, config, adapter_name))
        return {"adapted": model}

    def load(self, model, path, *, adapter_name=None):
        self.calls.append(("load", model, path, adapter_name))
        return {"loaded": path}


def test_config_maps_to_peft_without_importing_it() -> None:
    config = LoraConfig(
        rank=4,
        alpha=8,
        dropout=0.1,
        target_modules=["q_proj"],
        extra={"modules_to_save": ["head"]},
    )
    assert config.as_backend_kwargs() == {
        "r": 4,
        "lora_alpha": 8,
        "lora_dropout": 0.1,
        "bias": "none",
        "task_type": "CAUSAL_LM",
        "target_modules": ["q_proj"],
        "modules_to_save": ["head"],
    }


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"rank": 0}, "rank"),
        ({"alpha": 0}, "alpha"),
        ({"dropout": 1.0}, "dropout"),
        ({"target_modules": []}, "target_modules"),
        ({"extra": {"r": 2}}, "reserved"),
    ],
)
def test_config_validation(kwargs, message) -> None:
    with pytest.raises(ValueError, match=message):
        LoraConfig(**kwargs)


def test_services_delegate_to_explicit_backend() -> None:
    backend = RecordingBackend()
    model = object()
    config = LoraConfig(rank=2)

    assert apply_lora(model, config, backend=backend, adapter_name="train") == {"adapted": model}
    assert load_lora(model, "/adapter", backend=backend) == {"loaded": "/adapter"}
    assert backend.calls == [
        ("apply", model, config, "train"),
        ("load", model, "/adapter", None),
    ]


def test_load_rejects_empty_path_before_backend_call() -> None:
    backend = RecordingBackend()
    with pytest.raises(ValueError, match="path"):
        load_lora(object(), " ", backend=backend)
    assert backend.calls == []


def test_import_does_not_load_heavy_dependencies() -> None:
    package_src = Path(__file__).parents[1] / "src"
    script = """
import json, sys
import codex_lora
print(json.dumps(sorted(name for name in ("torch", "transformers", "peft")
                        if name in sys.modules)))
"""
    env = {**os.environ, "PYTHONPATH": str(package_src)}
    result = subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    assert json.loads(result.stdout) == []
