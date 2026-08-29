"""
Test Registry Basic

Test module for registry basic.
"""

from codex_ml.registry import Registry


def test_register_and_get_roundtrip():
    reg = Registry(component="basic")

    @reg.register("inc_basic")
    def inc(x):
        return x + 1

    g = reg.get("inc_basic")
    assert g(1) == 2, "Condition must be true"
