from codex_ml.plugins.registry import Registry


def test_factory_and_class() -> None:
    reg = Registry("x")

    @reg.register("cls")
    class C:
        def __init__(self, value: int) -> None:
            self.value = value

    @reg.register("factory")
    def make(value: int):
        class D:
            def __init__(self, v: int) -> None:
                self.value = v

        return D(value)

    c = reg.resolve_and_instantiate("cls", 1)
    f = reg.resolve_and_instantiate("factory", 2)
    assert c.value == 1
    assert f.value == 2
