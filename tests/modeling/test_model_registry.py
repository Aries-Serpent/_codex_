from codex_ml.models import minilm
from codex_ml.models.registry import get_model


def test_get_model_returns_minilm_instance():
    # Use a small vocab size to keep the model lightweight for tests
    model = get_model("MiniLM", {"vocab_size": 64})
    assert isinstance(model, minilm.MiniLM)
