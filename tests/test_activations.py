# BEGIN: CODEX_TEST_ACT
from codex_ml.models.activations import get_activation

def test_activation_registry_smoke():
    for n in ["relu","gelu","silu","swiglu"]:
        act = get_activation(n)
        assert act is not None
# END: CODEX_TEST_ACT
