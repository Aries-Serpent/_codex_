"""Smoke tests for coverage phase 5 - batch 1."""

from __future__ import annotations


def dummy_function_1() -> str:
    return "test_1"


def dummy_add_1(a: int, b: int) -> int:
    return a + b


class DummyClass_1:
    def __init__(self, value: int):
        self.value = value

    def get_value(self) -> int:
        return self.value

    def set_value(self, new_value: int) -> None:
        self.value = new_value


def test_smoke_1_function():
    """Smoke test for function."""
    result = dummy_function_1()
    assert result == "test_1", "Result must not be empty"


def test_smoke_1_addition():
    """Smoke test for addition."""
    result = dummy_add_1(1, 2)
    assert result == 3, "Result must not be empty"


def test_smoke_1_class_init():
    """Smoke test for class initialization."""
    obj = DummyClass_1(42)
    assert obj.value == 42, "Value must be initialized"


def test_smoke_1_class_get():
    """Smoke test for class getter."""
    obj = DummyClass_1(100)
    assert obj.get_value() == 100, "Value must be initialized"


def test_smoke_1_class_set():
    """Smoke test for class setter."""
    obj = DummyClass_1(50)
    obj.set_value(75)
    assert obj.get_value() == 75, "Value must be initialized"
