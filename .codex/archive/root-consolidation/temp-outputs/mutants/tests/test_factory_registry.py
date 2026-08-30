"""Tests for factory registry with stable ordering and idempotent registration."""

import sys
from pathlib import Path

# Add codex_addons to path
_REPO_ROOT = Path(__file__).parent.parent
_ADDONS_DIR = _REPO_ROOT / "codex_addons"
if str(_ADDONS_DIR) not in sys.path:
    sys.path.insert(0, str(_ADDONS_DIR))

from registry import Registry, create_registry
from registry_names import (
    ALL_REGISTRY_NAMES,
    METRIC_NAMES,
    get_all_stable_names,
    get_description,
    is_stable_name,
)


class TestRegistry:
    """Test suite for Registry class."""

    def test_create_empty_registry(self):
        """Test creating an empty registry."""
        registry = Registry(kind="test")
        assert len(registry) == 0, "Registry must not be empty"
        assert registry.list() == [], "Condition must be true"
        assert registry.kind == "test", "kind is not valid"

    def test_register_single_item(self):
        """Test registering a single item."""
        registry = Registry(kind="test")

        @registry.register("my_func")
        def my_func():
            return 42

        assert len(registry) == 1, "Registry must not be empty"
        assert "my_func" in registry, "Condition must be true"
        assert registry.get("my_func") == my_func, "Condition must be true"

    def test_register_multiple_items(self):
        """Test registering multiple items."""
        registry = Registry(kind="test")

        @registry.register("func1")
        def func1():
            pass

        @registry.register("func2")
        def func2():
            pass

        @registry.register("func3")
        def func3():
            pass

        assert len(registry) == 3, "Registry must not be empty"
        assert "func1" in registry, "Condition must be true"
        assert "func2" in registry, "Condition must be true"
        assert "func3" in registry, "Condition must be true"

    def test_idempotent_registration_same_object(self):
        """Test that registering the same object twice is idempotent."""
        registry = Registry(kind="test")

        def my_func():
            return 42

        # Register once
        registry.register("my_func", my_func)
        assert len(registry) == 1, "Registry must not be empty"

        # Register again with same object - should be no-op
        registry.register("my_func", my_func)
        assert len(registry) == 1, "Registry must not be empty"
        assert registry.get("my_func") == my_func, "Condition must be true"

    def test_re_registration_different_object_warns(self, caplog):
        """Test that re-registering with different object warns."""
        registry = Registry(kind="test")

        def func_v1():
            return 1

        def func_v2():
            return 2

        # First registration
        registry.register("my_func", func_v1)

        # Re-register with different object
        with caplog.at_level("WARNING"):
            registry.register("my_func", func_v2)

        # Should have warning about re-registration
        assert "re-registering" in caplog.text.lower(), "Condition must be true"

        # Should have the new function
        assert registry.get("my_func") == func_v2, "Condition must be true"

    def test_list_returns_stable_order(self):
        """Test that list() returns items in stable sorted order."""
        registry = Registry(kind="test")

        # Register in random order
        registry.register("zebra", lambda: 3)
        registry.register("apple", lambda: 1)
        registry.register("banana", lambda: 2)

        # list() should return in sorted order (stable)
        names = registry.list()
        assert names == ["apple", "banana", "zebra"]

        # Multiple calls should return same order
        assert registry.list() == names, "Condition must be true"

    def test_list_deterministic_across_runs(self):
        """Test that list() is deterministic across multiple registrations."""
        registry1 = Registry(kind="test")
        registry1.register("c", 3)
        registry1.register("a", 1)
        registry1.register("b", 2)

        registry2 = Registry(kind="test")
        registry2.register("a", 1)
        registry2.register("b", 2)
        registry2.register("c", 3)

        # Both should have same stable order despite different registration order
        assert registry1.list() == registry2.list(), "Condition must be true"
        assert registry1.list() == ["a", "b", "c"]

    def test_names_alias(self):
        """Test that names() is an alias for list()."""
        registry = Registry(kind="test")
        registry.register("item1", 1)
        registry.register("item2", 2)

        assert registry.names() == registry.list(), "Condition must be true"

    def test_items_in_stable_order(self):
        """Test that items() returns (name, item) pairs in stable order."""
        registry = Registry(kind="test")
        registry.register("z", 26)
        registry.register("a", 1)
        registry.register("m", 13)

        items = registry.items()

        # Should be in sorted order
        assert [name for name, _ in items] == ["a", "m", "z"]
        assert [val for _, val in items] == [1, 13, 26]

    def test_get_with_default(self):
        """Test get() with default value."""
        registry = Registry(kind="test")
        registry.register("exists", 42)

        assert registry.get("exists") == 42, "Condition must be true"
        assert registry.get("missing") is None, "Condition must be true"
        assert registry.get("missing", default="default") == "default"

    def test_contains(self):
        """Test __contains__ for membership testing."""
        registry = Registry(kind="test")
        registry.register("item", 1)

        assert "item" in registry, "Item must not be empty"
        assert "missing" not in registry, "Condition must be true"

    def test_len(self):
        """Test __len__ for registry size."""
        registry = Registry(kind="test")
        assert len(registry) == 0, "Registry must not be empty"

        registry.register("item1", 1)
        assert len(registry) == 1, "Registry must not be empty"

        registry.register("item2", 2)
        assert len(registry) == 2, "Registry must not be empty"

    def test_repr(self):
        """Test __repr__ for string representation."""
        registry = Registry(kind="metrics")
        registry.register("accuracy", lambda: 1)

        repr_str = repr(registry)
        assert "Registry" in repr_str, "Condition must be true"
        assert "metrics" in repr_str, "Condition must be true"
        assert "count=1" in repr_str, "Count must be greater than zero"

    def test_create_registry_factory(self):
        """Test create_registry factory function."""
        registry = create_registry("models")

        assert isinstance(registry, Registry)
        assert registry.kind == "models", "kind is not valid"
        assert len(registry) == 0, "Registry must not be empty"


class TestRegistryNames:
    """Test suite for registry_names module."""

    def test_metric_names_are_stable(self):
        """Test that METRIC_NAMES contains expected stable names."""
        assert "token_accuracy" in METRIC_NAMES, "Condition must be true"
        assert "ppl" in METRIC_NAMES, "Condition must be true"
        assert "exact_match" in METRIC_NAMES, "Condition must be true"
        assert "f1" in METRIC_NAMES, "Condition must be true"

        # Descriptions should be present
        assert isinstance(METRIC_NAMES["token_accuracy"], str)
        assert len(METRIC_NAMES["token_accuracy"]) > 0, "Collection must not be empty"

    def test_all_registry_names_structure(self):
        """Test that ALL_REGISTRY_NAMES has expected structure."""
        assert "metrics" in ALL_REGISTRY_NAMES, "Condition must be true"
        assert "models" in ALL_REGISTRY_NAMES, "Condition must be true"
        assert "data_loaders" in ALL_REGISTRY_NAMES, "Data must not be empty"
        assert "tokenizers" in ALL_REGISTRY_NAMES, "Condition must be true"
        assert "trainers" in ALL_REGISTRY_NAMES, "Condition must be true"

        # Each category should map to a dict of names->descriptions
        for kind, names_dict in ALL_REGISTRY_NAMES.items():
            assert isinstance(names_dict, dict)
            assert len(names_dict) > 0, "Names_dict must not be empty"

    def test_get_all_stable_names(self):
        """Test get_all_stable_names() returns a copy."""
        names1 = get_all_stable_names()
        names2 = get_all_stable_names()

        assert names1 == names2, "names1 is not valid"
        assert names1 is not names2, "names1 is not valid"

    def test_is_stable_name(self):
        """Test is_stable_name() checks."""
        assert is_stable_name("metrics", "token_accuracy") is True
        assert is_stable_name("metrics", "nonexistent") is False
        assert is_stable_name("invalid_kind", "anything") is False

    def test_get_description(self):
        """Test get_description() lookups."""
        desc = get_description("metrics", "token_accuracy")
        assert desc is not None, "desc must be initialized"
        assert isinstance(desc, str)
        assert len(desc) > 0, "Desc must not be empty"

        # Missing name
        assert get_description("metrics", "nonexistent") is None

        # Invalid kind
        assert get_description("invalid_kind", "anything") is None


class TestRegistryIntegration:
    """Integration tests for registry usage patterns."""

    def test_registry_with_stable_names(self):
        """Test using registry with predefined stable names."""
        registry = Registry(kind="metrics")

        # Register items using stable names
        for name in METRIC_NAMES:
            registry.register(name, lambda: name)

        # list() should return in stable sorted order
        registered = registry.list()
        expected_sorted = sorted(METRIC_NAMES.keys())
        assert registered == expected_sorted, "registered is not valid"

    def test_decorator_pattern(self):
        """Test using registry as decorator."""
        registry = Registry(kind="test")

        @registry.register("func1")
        def func1():
            return 1

        @registry.register("func2")
        def func2():
            return 2

        # Both should be registered
        assert registry.get("func1")() == 1, "Condition must be true"
        assert registry.get("func2")() == 2, "Condition must be true"

        # list() should be sorted
        assert registry.list() == ["func1", "func2"]
