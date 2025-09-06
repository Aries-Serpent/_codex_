from __future__ import annotations

import argparse
import types

from training import engine_hf_trainer as eng


def _dummy_tokenizer():
    tok = types.SimpleNamespace(
        pad_token_id=0,
        pad_token="<pad>",
        eos_token_id=0,
        bos_token_id=0,
        __call__=lambda texts, return_tensors=None, padding=True, truncation=True, max_length=8: {
            "input_ids": [[0]],
            "attention_mask": [[1]],
        },
    )
    tok.add_special_tokens = lambda *a, **k: None
    return tok


def test_engine_bootstrap(monkeypatch, tmp_path):
    calls: list[bool] = []

    def fake_bootstrap(args):
        calls.append(True)
        return eng.CodexLoggers()

    monkeypatch.setattr(eng, "_codex_logging_bootstrap", fake_bootstrap)

    # Stub heavy dependencies
    monkeypatch.setattr(eng, "split_dataset", lambda *a, **k: ([], None))
    monkeypatch.setattr(eng, "prepare_dataset", lambda *a, **k: [])
    monkeypatch.setattr(
        eng,
        "AutoTokenizer",
        types.SimpleNamespace(from_pretrained=lambda *a, **k: _dummy_tokenizer()),
    )
    monkeypatch.setattr(
        eng,
        "AutoModelForCausalLM",
        types.SimpleNamespace(
            from_pretrained=lambda *a, **k: types.SimpleNamespace(
                resize_token_embeddings=lambda *a, **k: None,
                to=lambda *a, **k: None,
            )
        ),
    )
    monkeypatch.setattr(eng, "DataCollatorForLanguageModeling", lambda *a, **k: lambda x: x)
    monkeypatch.setattr(
        eng, "TrainingArguments", lambda **k: types.SimpleNamespace(output_dir=tmp_path)
    )

    class DummyTrainer:
        def __init__(self, *a, **k):
            self.state = types.SimpleNamespace(global_step=0)

        def train(self, resume_from_checkpoint=None):
            return types.SimpleNamespace(metrics={"loss": 0.0})

        def save_model(self):
            pass

    monkeypatch.setattr(eng, "Trainer", DummyTrainer)
    monkeypatch.setattr(eng, "_make_accelerator", lambda **k: None)

    texts = ["hello"]
    log_args = argparse.Namespace(enable_wandb=True)
    eng.run_hf_trainer(texts=texts, output_dir=tmp_path, log_args=log_args)
    assert calls, "bootstrap should be called when flags enabled"
