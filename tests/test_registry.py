import sys
import types
from importlib.metadata import EntryPoint

import pytest

# Provide a lightweight OmegaConf stub so importing codex_ml does not require the
# optional dependency in minimal test environments.
if "omegaconf" not in sys.modules:  # pragma: no cover - only used when optional dep missing
    omegaconf = types.ModuleType("omegaconf")

    class DictConfig(dict):
        pass

    class _OmegaConf:
        @staticmethod
        def create(*args, **kwargs):  # noqa: ARG002
            return {}

        @staticmethod
        def from_dotlist(items):  # noqa: ARG002
            return {}

        @staticmethod
        def structured(cfg_cls):
            return cfg_cls

        @staticmethod
        def set_struct(schema, flag):  # noqa: ARG002
            return schema

        @staticmethod
        def load(path):  # noqa: ARG002
            return {}

        @staticmethod
        def merge(*configs):  # noqa: ARG002
            return {}

        @staticmethod
        def to_object(cfg):
            return cfg

    omegaconf.DictConfig = DictConfig
    omegaconf.OmegaConf = _OmegaConf
    sys.modules["omegaconf"] = omegaconf

if "torch" not in sys.modules:  # pragma: no cover - only used when torch is unavailable
    torch = types.ModuleType("torch")

    class _Tensor:
        def __init__(self, data=None):  # noqa: D401, ARG002
            self._data = data

        def argmax(self, dim=-1):  # noqa: D401, ARG002
            return self

        def float(self):  # noqa: D401
            return self

        def sum(self):  # noqa: D401
            return self

        def item(self):  # noqa: D401
            return 0.0

        def numel(self):  # noqa: D401
            return 0

    torch.Tensor = _Tensor
    torch.tensor = _Tensor
    sys.modules["torch"] = torch

if (
    "transformers" not in sys.modules
):  # pragma: no cover - only used when transformers is unavailable
    transformers = types.ModuleType("transformers")

    class _DummyModel:
        def to(self, *args, **kwargs):  # noqa: ARG002
            return self

    class AutoModelForCausalLM:
        @staticmethod
        def from_pretrained(name, local_files_only=True):  # noqa: ARG002
            return _DummyModel()

    class PreTrainedModel(_DummyModel):
        pass

    transformers.AutoModelForCausalLM = AutoModelForCausalLM
    transformers.PreTrainedModel = PreTrainedModel
    sys.modules["transformers"] = transformers

from codex_ml.registry.base import (
    Registry,
    RegistryConflictError,
    RegistryLoadError,
    RegistryNotFoundError,
)


def test_registry_register_get_roundtrip():
    reg = Registry("demo")

    @reg.register("toy")
    def _build():  # pragma: no cover - trivial
        return 41

    assert callable(reg.get("toy"))
    assert reg.get("toy")() == 41
    assert "toy" in reg.list()


def test_registry_direct_registration():
    reg = Registry("demo")

    def build():
        return 99

    reg.register("direct", build)
    assert reg.get("direct") is build


def test_registry_duplicate_registration_conflict():
    reg = Registry("demo")
    reg.register("dup")(lambda: 1)
    with pytest.raises(RegistryConflictError):
        reg.register("dup")(lambda: 2)


def test_registry_override_replaces():
    reg = Registry("demo")
    reg.register("item")(lambda: 1)
    reg.register("item", override=True)(lambda: 2)
    assert reg.get("item")() == 2


def test_registry_missing_key_raises():
    reg = Registry("demo")
    with pytest.raises(RegistryNotFoundError):
        reg.get("unknown")


def test_registry_entry_point_loading(monkeypatch):
    def fake_entry_points(*, group=None):
        if group != "codex_ml.tests":
            return ()
        ep = EntryPoint(name="toy", value="examples.plugins.toy_metric:build", group=group)
        return (ep,)

    monkeypatch.setattr("codex_ml.registry.base.metadata.entry_points", fake_entry_points)
    reg = Registry("metric", entry_point_group="codex_ml.tests")
    fn = reg.get("toy")
    assert callable(fn)
    assert fn() == {"name": "toy_metric"}


def test_registry_bubbles_entry_point_failure(monkeypatch):
    def fake_entry_points(*, group=None):
        if group != "codex_ml.tests":
            return ()
        ep = EntryPoint(name="broken", value="examples.plugins.broken:missing", group=group)
        return (ep,)

    monkeypatch.setattr("codex_ml.registry.base.metadata.entry_points", fake_entry_points)
    reg = Registry("metric", entry_point_group="codex_ml.tests")
    with pytest.raises(RegistryLoadError):
        reg.get("broken")
