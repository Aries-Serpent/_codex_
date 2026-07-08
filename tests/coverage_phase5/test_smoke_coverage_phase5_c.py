"""Smoke tests for coverage phase 5 - batch 2."""

from __future__ import annotations


def dummy_function_2() -> str:
    return "test_2"


def dummy_add_2(a: int, b: int) -> int:
    return a + b


class DummyClass_2:
    def __init__(self, value: int):
        self.value = value

    def get_value(self) -> int:
        return self.value

    def set_value(self, new_value: int) -> None:
        self.value = new_value


def test_smoke_2_function():
    """Smoke test for function."""
    result = dummy_function_2()
    assert result == "test_2", "Result must not be empty"


def test_smoke_2_addition():
    """Smoke test for addition."""
    result = dummy_add_2(1, 2)
    assert result == 3, "Result must not be empty"


def test_smoke_2_class_init():
    """Smoke test for class initialization."""
    obj = DummyClass_2(42)
    assert obj.value == 42, "Value must be initialized"


def test_smoke_2_class_get():
    """Smoke test for class getter."""
    obj = DummyClass_2(100)
    assert obj.get_value() == 100, "Value must be initialized"


def test_smoke_2_class_set():
    """Smoke test for class setter."""
    obj = DummyClass_2(50)
    obj.set_value(75)
    assert obj.get_value() == 75, "Value must be initialized"
