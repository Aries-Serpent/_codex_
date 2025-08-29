import warnings
import pytest

from codex_ml.interfaces import get, register


def test_registry_register_get():
    @register("dummy")
    class Dummy:
        pass

    assert get("dummy") is Dummy


def test_duplicate_registration_warns():
    @register("dup")
    class A:
        pass

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        @register("dup")
        class B:
            pass

    assert any("duplicate" in str(item.message) for item in w)
    assert get("dup") is B


def test_missing_key_raises():
    with pytest.raises(KeyError):
        get("__missing__")
