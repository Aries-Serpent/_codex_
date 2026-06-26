"""Tests for FeastCompatibleStore — the Parquet-backed feature store shim.

Covers apply, list_feature_views, list_entities, get_online_features,
materialize, get_feature_view, Entity, FeatureView, and FeatureServiceResult.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

# ── Import helpers ──────────────────────────────────────────────────────────


def _import():
    return pytest.importorskip(
        "codex_ml.features.feast_compat",
        reason="codex_ml.features.feast_compat not importable",
    )


# ── Entity ──────────────────────────────────────────────────────────────────


class TestEntity:
    def test_basic_creation(self):
        mod = _import()
        e = mod.Entity(name="user", join_key="user_id", value_type="STRING")
        assert e.name == "user", "name is not valid"
        assert e.join_key == "user_id", "join_key is not valid"

    def test_default_join_key(self):
        mod = _import()
        e = mod.Entity(name="item", join_key="item_id")
        assert e.join_key == "item_id", "Item must not be empty"

    def test_default_value_type(self):
        mod = _import()
        e = mod.Entity(name="item", join_key="item_id")
        assert e.value_type == "STRING", "Value must be initialized"


# ── FeatureView ─────────────────────────────────────────────────────────────


class TestFeatureView:
    def test_basic_creation(self):
        mod = _import()
        fv = mod.FeatureView(
            name="user_profile",
            entities=["user"],
            features=["age", "score"],
            ttl_seconds=3600,
        )
        assert fv.name == "user_profile", "name is not valid"
        assert len(fv.features) == 2, "Collection must not be empty"

    def test_default_ttl(self):
        mod = _import()
        fv = mod.FeatureView(name="v", entities=["e"], features=["f"])
        assert fv.ttl_seconds == 3600, "ttl_seconds is not valid"

    def test_source_optional(self):
        mod = _import()
        fv = mod.FeatureView(name="v", entities=["e"], features=["f"])
        assert fv.source is None, "source is not valid"


# ── FeatureServiceResult ─────────────────────────────────────────────────────


class TestFeatureServiceResult:
    def _make_result(self, mod, fresh=True):
        now = datetime.now(timezone.utc).isoformat()
        return mod.FeatureServiceResult(
            feature_view="v",
            entity_values={"user_id": "u1"},
            feature_values={"v__score": 0.9},
            retrieved_at=now,
            ttl_seconds=3600 if fresh else 0,
        )

    def test_is_fresh(self):
        mod = _import()
        r = self._make_result(mod, fresh=True)
        assert r.is_fresh, "Condition must be true"

    def test_not_fresh_when_ttl_zero(self):
        mod = _import()
        r = self._make_result(mod, fresh=False)
        assert not r.is_fresh, "Condition must be true"


# ── FeastCompatibleStore ─────────────────────────────────────────────────────


class TestFeastCompatibleStore:
    """Tests for the Parquet-backed FeastCompatibleStore shim."""

    def test_apply_registers_feature_view(self, tmp_path):
        mod = _import()
        with patch(
            "codex_ml.features.feast_compat.FeastCompatibleStore.__init__",
            lambda self, **kw: _init_store(self),
        ):
            store = mod.FeastCompatibleStore.__new__(mod.FeastCompatibleStore)
            _init_store(store)
            fv = mod.FeatureView(name="profile", entities=["user"], features=["age"])
            store.apply([fv])
            assert "profile" in [v.name for v in store.list_feature_views()], "Condition must be true"

    def test_apply_registers_entity(self, tmp_path):
        mod = _import()
        store = mod.FeastCompatibleStore.__new__(mod.FeastCompatibleStore)
        _init_store(store)
        e = mod.Entity(name="user", join_key="user_id")
        store.apply([e])
        assert "user" in [en.name for en in store.list_entities()], "Condition must be true"

    def test_apply_skips_unknown_type(self, tmp_path):
        mod = _import()
        store = mod.FeastCompatibleStore.__new__(mod.FeastCompatibleStore)
        _init_store(store)
        # Should not raise; just logs a warning
        store.apply(["not_a_view_or_entity"])  # type: ignore[list-item]

    def test_list_feature_views_empty(self):
        mod = _import()
        store = mod.FeastCompatibleStore.__new__(mod.FeastCompatibleStore)
        _init_store(store)
        assert store.list_feature_views() == [], "st is not valid"

    def test_list_entities_empty(self):
        mod = _import()
        store = mod.FeastCompatibleStore.__new__(mod.FeastCompatibleStore)
        _init_store(store)
        assert store.list_entities() == [], "st is not valid"

    def test_get_feature_view_found(self):
        mod = _import()
        store = mod.FeastCompatibleStore.__new__(mod.FeastCompatibleStore)
        _init_store(store)
        fv = mod.FeatureView(name="v1", entities=["e"], features=["f"])
        store.apply([fv])
        assert store.get_feature_view("v1").name == "v1", "name is not valid"

    def test_get_feature_view_not_found_raises_key_error(self):
        mod = _import()
        store = mod.FeastCompatibleStore.__new__(mod.FeastCompatibleStore)
        _init_store(store)
        with pytest.raises(KeyError, match="no_such"):
            store.get_feature_view("no_such")

    def test_get_online_features_empty_entity_rows_raises(self):
        mod = _import()
        store = mod.FeastCompatibleStore.__new__(mod.FeastCompatibleStore)
        _init_store(store)
        fv = mod.FeatureView(name="v", entities=["e"], features=["f"])
        store.apply([fv])
        with pytest.raises(ValueError, match="entity_rows"):
            store.get_online_features(features=["v:f"], entity_rows=[])

    def test_get_online_features_bad_ref_format(self):
        mod = _import()
        store = mod.FeastCompatibleStore.__new__(mod.FeastCompatibleStore)
        _init_store(store)
        fv = mod.FeatureView(name="v", entities=["e"], features=["f"])
        store.apply([fv])
        with pytest.raises(ValueError, match="view:feature"):
            store.get_online_features(features=["badformat"], entity_rows=[{"k": "v"}])

    def test_get_online_features_unregistered_view_raises(self):
        mod = _import()
        store = mod.FeastCompatibleStore.__new__(mod.FeastCompatibleStore)
        _init_store(store)
        with pytest.raises(KeyError, match="unknown_view"):
            store.get_online_features(
                features=["unknown_view:f"],
                entity_rows=[{"k": "v"}],
            )

    def test_get_online_features_native_store_miss(self):
        mod = _import()
        store = mod.FeastCompatibleStore.__new__(mod.FeastCompatibleStore)
        _init_store(store)
        fv = mod.FeatureView(name="v", entities=["e"], features=["age"])
        store.apply([fv])
        # Native store returns None → features should be None
        store._native.get_feature_group.return_value = None
        result = store.get_online_features(features=["v:age"], entity_rows=[{"user_id": "u1"}])
        assert result.feature_values["v__age"] is None, "Result must not be empty"

    def test_get_online_features_native_store_hit(self):
        mod = _import()
        store = mod.FeastCompatibleStore.__new__(mod.FeastCompatibleStore)
        _init_store(store)
        fv = mod.FeatureView(name="v", entities=["e"], features=["age"])
        store.apply([fv])
        store._native.get_feature_group.return_value = {"age": 42}
        result = store.get_online_features(features=["v:age"], entity_rows=[{"user_id": "u1"}])
        assert result.feature_values["v__age"] == 42, "Result must not be empty"

    def test_get_online_features_native_store_exception(self):
        mod = _import()
        store = mod.FeastCompatibleStore.__new__(mod.FeastCompatibleStore)
        _init_store(store)
        fv = mod.FeatureView(name="v", entities=["e"], features=["f"])
        store.apply([fv])
        store._native.get_feature_group.side_effect = RuntimeError("no parquet")
        # Should gracefully return None values (no exception bubbling)
        result = store.get_online_features(features=["v:f"], entity_rows=[{"k": "1"}])
        assert result.feature_values["v__f"] is None, "Result must not be empty"

    def test_materialize_all_views(self, tmp_path):
        mod = _import()
        store = mod.FeastCompatibleStore.__new__(mod.FeastCompatibleStore)
        _init_store(store)
        fv = mod.FeatureView(name="v", entities=["e"], features=["score"])
        store.apply([fv])
        store._native.materialize_feature_group.return_value = tmp_path / "v.parquet"
        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, tzinfo=timezone.utc)
        result = store.materialize(start, end)
        assert "v" in result, "Result must not be empty"

    def test_materialize_skips_unknown_views(self):
        mod = _import()
        store = mod.FeastCompatibleStore.__new__(mod.FeastCompatibleStore)
        _init_store(store)
        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, tzinfo=timezone.utc)
        # Specifying a view that is not registered should skip gracefully
        result = store.materialize(start, end, feature_views=["not_registered"])
        assert "not_registered" not in result, "Result must not be empty"

    def test_materialize_handles_exception(self):
        mod = _import()
        store = mod.FeastCompatibleStore.__new__(mod.FeastCompatibleStore)
        _init_store(store)
        fv = mod.FeatureView(name="v", entities=["e"], features=["f"])
        store.apply([fv])
        store._native.materialize_feature_group.side_effect = IOError("disk full")
        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, tzinfo=timezone.utc)
        result = store.materialize(start, end)
        assert "v" not in result, "Result must not be empty"


# ── Helpers ──────────────────────────────────────────────────────────────────


def _init_store(store) -> None:
    """Manually initialize a FeastCompatibleStore with a mocked native store."""
    from pathlib import Path

    store._repo_path = Path(".feature_store")
    store._native = MagicMock()
    store._views = {}
    store._entities = {}
