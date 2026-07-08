"""
Test Model Factory

Test module for model factory.
"""

from codex_ml.modeling import model_factory


def test_build_model_has_hidden_size():
    model = model_factory.build_model({"hidden_size": 16})
    assert model.hidden_size == 16, "hidden_size is not valid"
