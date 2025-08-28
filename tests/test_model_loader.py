from src.codex_ml.utils.modeling import load_model_and_tokenizer


def test_loader_smoke_cpu():
    model, tk = load_model_and_tokenizer(
        "sshleifer/tiny-gpt2", dtype="fp32", device_map="auto"
    )
    assert model is not None and tk is not None
