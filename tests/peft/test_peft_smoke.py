from __future__ import annotations
import torch

from src.codex_ml.peft.peft_registry import get_peft_registry


def test_peft_registry_lists_expected_adapters():
    reg = get_peft_registry()
    names = set(reg.list_adapters())
    # At least our newly added adapters should be present
    assert {"prefix_tuning", "ia3", "adalora"}.issubset(names)


def test_peft_get_trainable_parameters_works_on_plain_model():
    # Even without applying adapters, get_trainable_parameters should work on a plain model
    model = torch.nn.Linear(8, 4)
    for name in {"prefix_tuning", "ia3", "adalora"}:
        adapter = get_peft_registry().get(name)
        n = adapter.get_trainable_parameters(model)
        assert isinstance(n, int)
        assert n > 0
