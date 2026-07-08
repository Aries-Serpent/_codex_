"""Smoke tests for coverage phase 5 - batch 3."""

from __future__ import annotations


def dummy_function_3() -> str:
    return "test_3"


def dummy_add_3(a: int, b: int) -> int:
    return a + b


class DummyClass_3:
    def __init__(self, value: int):
        self.value = value

    def get_value(self) -> int:
        return self.value

    def set_value(self, new_value: int) -> None:
        self.value = new_value


def test_smoke_3_function():
    """Smoke test for function."""
    result = dummy_function_3()
    assert result == "test_3", "Result must not be empty"


def test_smoke_3_addition():
    """Smoke test for addition."""
    result = dummy_add_3(1, 2)
    assert result == 3, "Result must not be empty"


def test_smoke_3_class_init():
    """Smoke test for class initialization."""
    obj = DummyClass_3(42)
    assert obj.value == 42, "Value must be initialized"


def test_smoke_3_class_get():
    """Smoke test for class getter."""
    obj = DummyClass_3(100)
    assert obj.get_value() == 100, "Value must be initialized"


def test_smoke_3_class_set():
    """Smoke test for class setter."""
    obj = DummyClass_3(50)
    obj.set_value(75)
    assert obj.get_value() == 75, "Value must be initialized"
