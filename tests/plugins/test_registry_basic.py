from codex_ml.plugins.registry import Registry


def test_register_and_get() -> None:
    reg = Registry("x")

    @reg.register("Foo")
    class Foo:
        pass

    assert "foo" in reg.names()
    item = reg.get("foo")
    assert item is not None
    assert item.obj is Foo


def test_case_insensitive_override() -> None:
    reg = Registry("x")

    @reg.register("a")
    class A:
        pass

    @reg.register("A")
    class B:
        pass

    assert reg.get("a").obj is B
