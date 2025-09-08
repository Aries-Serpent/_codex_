from codex_ml.models import minilm
from codex_ml.models.registry import get_model


def test_get_model_returns_minilm_instance():
    model = get_model("MiniLM", {"vocab_size": 128})
    assert isinstance(model, minilm.MiniLM)
