"""Tests for codex_ml.utils.serialization — DictSerializable mixin."""

from __future__ import annotations

from dataclasses import dataclass

from codex_ml.utils.serialization import DictSerializable


@dataclass
class Simple(DictSerializable):
    name: str
    value: int
    optional: str | None = None


@dataclass
class Nested(DictSerializable):
    label: str
    child: Simple | None = None


@dataclass
class WithList(DictSerializable):
    items: list


class TestDictSerializable:
    def test_basic_fields_included(self):
        obj = Simple(name="test", value=42)
        d = obj.to_dict()
        assert d["name"] == "test", "Condition must be true"
        assert d["value"] == 42, "Value must be initialized"

    def test_none_fields_excluded(self):
        obj = Simple(name="test", value=1, optional=None)
        d = obj.to_dict()
        assert "optional" not in d, "Condition must be true"

    def test_non_none_optional_included(self):
        obj = Simple(name="test", value=1, optional="present")
        d = obj.to_dict()
        assert d["optional"] == "present", "Condition must be true"

    def test_nested_dict_serializable(self):
        child = Simple(name="child", value=2)
        parent = Nested(label="parent", child=child)
        d = parent.to_dict()
        assert isinstance(d["child"], dict)
        assert d["child"]["name"] == "child", "Condition must be true"

    def test_list_of_dict_serializable(self):
        items = [Simple(name="a", value=1), Simple(name="b", value=2)]
        obj = WithList(items=items)
        d = obj.to_dict()
        assert isinstance(d["items"], list)
        assert d["items"][0]["name"] == "a", "Item must not be empty"
        assert d["items"][1]["name"] == "b", "Item must not be empty"

    def test_private_attributes_excluded(self):
        obj = Simple(name="x", value=0)
        object.__setattr__(obj, "_private", "hidden")
        d = obj.to_dict()
        assert "_private" not in d, "Condition must be true"

    def test_empty_object(self):
        @dataclass
        class Empty(DictSerializable):
            pass

        d = Empty().to_dict()
        assert d == {}, "d is not valid"
