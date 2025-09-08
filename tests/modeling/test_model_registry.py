from codex_ml.models.registry import get_model


def test_get_model_instantiates_minilm():
    model = get_model("MiniLM", {"vocab_size": 32})
    assert model.__class__.__name__ == "MiniLM"
