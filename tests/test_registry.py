from codex_ml.interfaces import get, register


def test_registry_register_get():
    @register("dummy")
    class Dummy:
        pass

    assert get("dummy") is Dummy
