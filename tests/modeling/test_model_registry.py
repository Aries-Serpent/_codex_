from codex_ml.models import minilm
from codex_ml.models.registry import get_model


def test_get_model_returns_minilm_config():
    cfg_cls = get_model("minilm")
    assert cfg_cls is minilm.MiniLMConfig
