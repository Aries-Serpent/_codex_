from codex_ml.peft.peft_adapter import apply_lora


class DummyModel:
    def parameters(self):
        return []


def test_apply_lora_without_peft(monkeypatch):
    model = DummyModel()
    out = apply_lora(model, {"lora_alpha": 32, "task_type": "SEQ_CLS"}, r=4)
    assert out is model
    assert hasattr(out, "peft_config")
    assert out.peft_config["r"] == 4
    assert out.peft_config["lora_alpha"] == 32
    assert out.peft_config["task_type"] == "SEQ_CLS"
