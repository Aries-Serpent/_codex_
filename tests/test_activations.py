"""
Test Activations

Test module for activations.
"""
import pytest
from codex_ml.models.activations import get_activation

# BEGIN: CODEX_TEST_ACT


def test_activation_registry_smoke():
    for n in ["relu", "gelu", "silu", "swiglu"]:
        act = get_activation(n)
        assert act is not None, "act must be initialized"


# END: CODEX_TEST_ACT
