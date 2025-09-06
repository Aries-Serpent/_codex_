from __future__ import annotations

import pytest
import torch

from codex_ml.models.decoder_only import DecoderOnlyLM, ModelConfig
from codex_ml.models.generate import generate


def _tiny_model() -> DecoderOnlyLM:
    cfg = ModelConfig(vocab_size=64, d_model=32, n_heads=4, n_layers=2, max_seq_len=32)
    return DecoderOnlyLM(cfg)


def test_forward_shapes() -> None:
    model = _tiny_model()
    x = torch.randint(0, model.cfg.vocab_size, (2, 8))
    out = model(x)
    assert out["logits"].shape == (2, 8, model.cfg.vocab_size)


def test_determinism_seed() -> None:
    torch.manual_seed(0)
    m1 = _tiny_model()
    x = torch.randint(0, m1.cfg.vocab_size, (1, 8))
    torch.manual_seed(0)
    m2 = _tiny_model()
    assert torch.allclose(m1(x)["logits"], m2(x)["logits"])


def test_param_count() -> None:
    m = _tiny_model()
    cfg = m.cfg
    total = sum(p.numel() for p in m.parameters())
    expected = cfg.vocab_size * cfg.d_model
    expected += cfg.max_seq_len * cfg.d_model if m.pos_emb is not None else 0
    per_layer = 3 * cfg.d_model * cfg.d_model + cfg.d_model * cfg.d_model
    per_layer += 2 * cfg.ffn_mult * cfg.d_model * cfg.d_model
    per_layer += 4 * cfg.d_model
    expected += cfg.n_layers * per_layer
    expected += 2 * cfg.d_model
    assert total == expected


def test_kv_cache_equivalence() -> None:
    m = _tiny_model()
    x = torch.randint(0, m.cfg.vocab_size, (1, 5))
    full = m(x)["logits"][:, -1, :]
    first = m(x[:, :-1], use_cache=True)
    second = m(x[:, -1:], past_key_values=first["past_key_values"], use_cache=True)["logits"][
        :, -1, :
    ]
    assert torch.allclose(full, second, atol=1e-5)


def test_serialization_round_trip(tmp_path) -> None:
    m = _tiny_model()
    path = tmp_path / "model.pt"
    torch.save(m.state_dict(), path)
    m2 = _tiny_model()
    m2.load_state_dict(torch.load(path))
    x = torch.randint(0, m.cfg.vocab_size, (1, 4))
    assert torch.allclose(m(x)["logits"], m2(x)["logits"])


def test_generate_smoke() -> None:
    m = _tiny_model()
    prompt = torch.randint(0, m.cfg.vocab_size, (1, 3))
    out = generate(m, None, prompt, max_new_tokens=5)
    assert out.size(1) >= 3


def test_lora_attach() -> None:
    pytest.importorskip("peft")
    from peft import LoraConfig, get_peft_model

    m = _tiny_model()
    cfg = LoraConfig(r=2, lora_alpha=4, lora_dropout=0.0, target_modules=["qkv"])
    m = get_peft_model(m, cfg)
    names = [n for n, p in m.named_parameters() if "lora_" in n]
    assert names
