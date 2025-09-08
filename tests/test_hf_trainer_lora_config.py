import types
from pathlib import Path

import training.engine_hf_trainer as hf


def test_run_hf_trainer_passes_lora_params(monkeypatch, tmp_path):
    captured = {}

    class DummyTokenizer:
        eos_token = "</s>"
        pad_token = None

        def __call__(self, text, truncation=True):
            return {"input_ids": [0]}

    class DummyModel:
        def to(self, *args, **kwargs):
            return self

    dummy_ds = types.SimpleNamespace(map=lambda *a, **k: dummy_ds)

    monkeypatch.setattr(
        hf, "AutoTokenizer", types.SimpleNamespace(from_pretrained=lambda *a, **k: DummyTokenizer())
    )
    monkeypatch.setattr(
        hf,
        "AutoModelForCausalLM",
        types.SimpleNamespace(from_pretrained=lambda *a, **k: DummyModel()),
    )
    monkeypatch.setattr(hf, "Dataset", types.SimpleNamespace(from_dict=lambda d: dummy_ds))
    monkeypatch.setattr(hf, "DataCollatorForLanguageModeling", lambda tokenizer, mlm: None)

    class DummyTrainer:
        def __init__(self, *a, **k):
            self.state = types.SimpleNamespace(global_step=0)

        def train(self, resume_from_checkpoint=None, **kwargs):
            class R:
                metrics: dict = {}

            return R()

        def save_model(self, *a, **k):
            return None

    monkeypatch.setattr(hf, "Trainer", DummyTrainer)
    monkeypatch.setattr(hf, "split_dataset", lambda *a, **k: (a[0], None))
    monkeypatch.setattr(hf, "_codex_logging_bootstrap", lambda *a, **k: hf.CodexLoggers())

    def fake_apply_lora(model, cfg):
        captured.update(cfg)
        return model

    monkeypatch.setattr(hf, "apply_lora", fake_apply_lora)

    hf.run_hf_trainer(
        texts=["hi"],
        output_dir=Path(tmp_path),
        lora_r=8,
        lora_alpha=32,
        lora_dropout=0.05,
        val_split=0.0,
        distributed=False,
    )

    assert captured == {"r": 8, "lora_alpha": 32, "lora_dropout": 0.05}
