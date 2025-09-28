from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("transformers")
peft = pytest.importorskip("peft")

from codex_ml.models.peft_hooks import LoraBuildCfg, build_lora


def _tiny_torch_model():
    from transformers import AutoConfig, AutoModelForSequenceClassification

    cfg = AutoConfig(
        hidden_size=32,
        num_hidden_layers=1,
        num_attention_heads=4,
        intermediate_size=64,
        vocab_size=200,
    )
    model = AutoModelForSequenceClassification.from_config(cfg)
    model.eval()
    return model


@pytest.mark.skipif(peft is None, reason="peft not installed")
def test_lora_applies_and_forwards():
    model = _tiny_torch_model()
    wrapped = build_lora(model, LoraBuildCfg(r=2, target_modules=["query", "value"]))
    # forward pass on toy inputs
    input_ids = torch.randint(0, 199, (2, 8))
    attention_mask = torch.ones_like(input_ids)
    out = wrapped(input_ids=input_ids, attention_mask=attention_mask)
    assert hasattr(out, "logits")
    assert out.logits.shape[0] == 2

