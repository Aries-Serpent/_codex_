from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from codex_lora import (
    LoraArtifact,
    LoraArtifactMetadata,
    LoraConfig,
    OptionalDependencyError,
    PeftBackend,
    activate_lora,
    apply_lora,
    delete_lora,
    disable_lora,
    load_lora,
    prepare_lora_training,
    read_lora_artifact,
    save_lora,
)


class RecordingBackend:
    def __init__(self) -> None:
        self.calls: list[tuple[object, ...]] = []

    def apply(self, model, config, *, adapter_name=None):
        self.calls.append(("apply", model, config, adapter_name))
        return {"adapted": model}

    def load(self, model, path, *, adapter_name=None):
        self.calls.append(("load", model, path, adapter_name))
        return {"loaded": path}


class LifecycleBackend(RecordingBackend):
    def __init__(self) -> None:
        super().__init__()
        self.training_kwargs: dict[str, object] | None = None

    def save(self, model, path, *, adapter_name=None):
        self.calls.append(("save", model, path, adapter_name))
        Path(path).mkdir()

    def activate(self, model, adapter_name):
        self.calls.append(("activate", model, adapter_name))
        return model

    def disable(self, model):
        self.calls.append(("disable", model))
        return model

    def delete(self, model, adapter_name):
        self.calls.append(("delete", model, adapter_name))
        return model

    def prepare_for_training(
        self, model, *, gradient_checkpointing=False, gradient_checkpointing_kwargs=None
    ):
        self.training_kwargs = {
            "gradient_checkpointing": gradient_checkpointing,
            "gradient_checkpointing_kwargs": gradient_checkpointing_kwargs,
        }
        return model


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


def test_artifact_metadata_is_bounded_and_immutable() -> None:
    metadata = LoraArtifactMetadata(adapter_name=" train ", metadata={"source": "unit-test"})

    assert metadata.adapter_name == "train"
    assert metadata.as_dict() == {
        "format_version": 1,
        "adapter_name": "train",
        "metadata": {"source": "unit-test"},
    }
    with pytest.raises(TypeError):
        metadata.metadata["source"] = "changed"  # type: ignore[index]
    with pytest.raises(ValueError, match="at most"):
        LoraArtifactMetadata(metadata={str(index): "value" for index in range(33)})
    with pytest.raises(ValueError, match="values"):
        LoraArtifactMetadata(metadata={"invalid": 1})  # type: ignore[dict-item]


def test_adapter_lifecycle_persists_and_restores_bounded_metadata(tmp_path) -> None:
    backend = LifecycleBackend()
    model = object()
    artifact = save_lora(
        model,
        tmp_path / "adapter",
        backend=backend,
        adapter_name="train",
        metadata={"run": "42"},
    )

    assert artifact == LoraArtifact(
        str(tmp_path / "adapter"),
        LoraArtifactMetadata(adapter_name="train", metadata={"run": "42"}),
    )
    assert read_lora_artifact(tmp_path / "adapter") == artifact
    assert load_lora(model, tmp_path / "adapter", backend=backend) == {
        "loaded": str(tmp_path / "adapter")
    }
    assert backend.calls[-1] == ("load", model, str(tmp_path / "adapter"), "train")

    assert activate_lora(model, "train", backend=backend) is model
    assert disable_lora(model, backend=backend) is model
    assert delete_lora(model, "train", backend=backend) is model
    assert [call[0] for call in backend.calls[-3:]] == ["activate", "disable", "delete"]


def test_lifecycle_requires_backend_capability(tmp_path) -> None:
    with pytest.raises(TypeError, match="lifecycle"):
        save_lora(object(), tmp_path / "adapter", backend=RecordingBackend())  # type: ignore[arg-type]


def test_training_hook_delegates_without_mutating_kwargs() -> None:
    backend = LifecycleBackend()
    kwargs = {"use_reentrant": False}
    model = object()

    assert (
        prepare_lora_training(
            model,
            backend=backend,
            gradient_checkpointing=True,
            gradient_checkpointing_kwargs=kwargs,
        )
        is model
    )
    assert kwargs == {"use_reentrant": False}
    assert backend.training_kwargs == {
        "gradient_checkpointing": True,
        "gradient_checkpointing_kwargs": kwargs,
    }
    assert backend.training_kwargs["gradient_checkpointing_kwargs"] is not kwargs


def test_peft_backend_maps_lifecycle_and_training_hooks(monkeypatch) -> None:
    calls: list[tuple[object, ...]] = []

    class FakePeftModel:
        @staticmethod
        def from_pretrained(model, path, **kwargs):
            calls.append(("from_pretrained", model, path, kwargs))
            return "loaded-model"

    def get_peft_model(model, config, **kwargs):
        calls.append(("apply", model, config, kwargs))
        return "adapted-model"

    def prepare_model_for_kbit_training(model, **kwargs):
        calls.append(("prepare", model, kwargs))
        return "prepared-model"

    backend = PeftBackend()
    monkeypatch.setattr(
        backend,
        "_module",
        lambda: SimpleNamespace(
            LoraConfig=lambda **kwargs: ("config", kwargs),
            PeftModel=FakePeftModel,
            get_peft_model=get_peft_model,
            prepare_model_for_kbit_training=prepare_model_for_kbit_training,
        ),
    )
    model = object()

    assert backend.apply(model, LoraConfig(rank=2), adapter_name="train") == "adapted-model"
    assert backend.load(model, "/adapter", adapter_name="train") == "loaded-model"
    assert (
        backend.prepare_for_training(
            model,
            gradient_checkpointing=True,
            gradient_checkpointing_kwargs={"use_reentrant": False},
        )
        == "prepared-model"
    )
    assert calls == [
        (
            "apply",
            model,
            (
                "config",
                {
                    "r": 2,
                    "lora_alpha": 16,
                    "lora_dropout": 0.05,
                    "bias": "none",
                    "task_type": "CAUSAL_LM",
                },
            ),
            {"adapter_name": "train"},
        ),
        ("from_pretrained", model, "/adapter", {"adapter_name": "train"}),
        (
            "prepare",
            model,
            {"use_gradient_checkpointing": True, "use_reentrant": False},
        ),
    ]


def test_peft_backend_lifecycle_uses_standard_model_methods() -> None:
    calls: list[tuple[object, ...]] = []

    class FakeModel:
        def save_pretrained(self, path, **kwargs):
            calls.append(("save", path, kwargs))

        def set_adapter(self, adapter_name):
            calls.append(("activate", adapter_name))

        def disable_adapter_layers(self):
            calls.append(("disable",))

        def delete_adapter(self, adapter_name):
            calls.append(("delete", adapter_name))

    model = FakeModel()
    backend = PeftBackend()

    assert backend.save(model, "/adapter", adapter_name="train") is None
    assert backend.activate(model, "train") is model
    assert backend.disable(model) is model
    assert backend.delete(model, "train") is model
    assert calls == [
        ("save", "/adapter", {"selected_adapters": ["train"]}),
        ("activate", "train"),
        ("disable",),
        ("delete", "train"),
    ]


def test_peft_backend_loads_into_an_existing_peft_model() -> None:
    calls: list[tuple[object, ...]] = []

    class ExistingPeftModel:
        def load_adapter(self, path, **kwargs):
            calls.append((path, kwargs))

    model = ExistingPeftModel()
    assert PeftBackend().load(model, "/adapter", adapter_name="inference") is model
    assert calls == [("/adapter", {"adapter_name": "inference"})]


def test_missing_peft_is_reported_as_optional_dependency(monkeypatch) -> None:
    import codex_lora.adapters as adapters

    def missing_peft(name):
        raise ImportError(name)

    monkeypatch.setattr(adapters, "import_module", missing_peft)
    with pytest.raises(OptionalDependencyError, match=r"codex-ml-lora\[peft\]"):
        PeftBackend().apply(object(), LoraConfig())


def test_installed_peft_has_required_parity_symbols() -> None:
    peft = pytest.importorskip("peft")
    assert callable(peft.get_peft_model)
    assert callable(peft.prepare_model_for_kbit_training)
    assert callable(peft.PeftModel.from_pretrained)


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
