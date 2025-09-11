from codex.training import run_functional_training


def test_run_functional_training_use_fast_flag(monkeypatch):
    called = {}

    def fake_load_tokenizer(name, path, *, use_fast=True):
        called["use_fast"] = use_fast

        class DummyTokenizer:
            vocab_size = 0

            def encode(self, text):  # pragma: no cover - minimal
                return []

        return DummyTokenizer()

    def fake_pipeline(**kwargs):  # pragma: no cover - stub
        return {}

    monkeypatch.setattr("codex.training.load_tokenizer", fake_load_tokenizer)
    monkeypatch.setattr("codex.training.run_codex_symbolic_pipeline", fake_pipeline)

    run_functional_training(["hi"], [], [], tokenizer_name="gpt2", use_fast_tokenizer=False)
    assert called["use_fast"] is False
