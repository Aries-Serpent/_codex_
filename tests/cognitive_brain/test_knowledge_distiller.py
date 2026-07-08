"""Tests for src/codex/cognitive/knowledge_distiller.py — Phase 10B coverage.

Covers KnowledgeType, KnowledgePriority, KnowledgeItem, SessionSummary,
KnowledgeStore, LearningExtractor, DecisionExtractor, and KnowledgeDistiller.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from codex.cognitive.knowledge_distiller import (
    DecisionExtractor,
    KnowledgeDistiller,
    KnowledgeItem,
    KnowledgePriority,
    KnowledgeStore,
    KnowledgeType,
    LearningExtractor,
    SessionSummary,
)

# ---------------------------------------------------------------------------
# KnowledgeType / KnowledgePriority enums
# ---------------------------------------------------------------------------


class TestKnowledgeType:
    def test_members(self):
        assert KnowledgeType.FACTUAL.value == "factual", "Value must be initialized"
        assert KnowledgeType.PROCEDURAL.value == "procedural", "Value must be initialized"
        assert KnowledgeType.CONTEXTUAL.value == "contextual", "Value must be initialized"
        assert KnowledgeType.DECISION.value == "decision", "Value must be initialized"
        assert KnowledgeType.PATTERN.value == "pattern", "Value must be initialized"

    def test_from_value(self):
        assert KnowledgeType("factual") is KnowledgeType.FACTUAL, "Condition must be true"


class TestKnowledgePriority:
    def test_ordering(self):
        vals = [p.value for p in KnowledgePriority]
        assert "critical" in vals, "Condition must be true"
        assert "low" in vals, "Condition must be true"


# ---------------------------------------------------------------------------
# KnowledgeItem
# ---------------------------------------------------------------------------


class TestKnowledgeItem:
    @pytest.fixture()
    def item(self):
        now = datetime.now(timezone.utc)
        return KnowledgeItem(
            id="KN-00001",
            knowledge_type=KnowledgeType.FACTUAL,
            priority=KnowledgePriority.HIGH,
            content="Use strftime for timestamps",
            source="commit_message",
            session_id="S100",
            created_at=now,
            last_accessed=now,
            access_count=3,
            tags=["timestamp", "convention"],
            related_files=["tools/ledger.py"],
            confidence=0.95,
        )

    def test_to_dict_keys(self, item):
        d = item.to_dict()
        expected_keys = {
            "id",
            "knowledge_type",
            "priority",
            "content",
            "source",
            "session_id",
            "created_at",
            "last_accessed",
            "access_count",
            "tags",
            "related_files",
            "confidence",
        }
        assert expected_keys == set(d.keys()), "expected_keys is not valid"

    def test_roundtrip(self, item):
        d = item.to_dict()
        restored = KnowledgeItem.from_dict(d)
        assert restored.id == item.id, "Item must not be empty"
        assert restored.knowledge_type == item.knowledge_type, "Item must not be empty"
        assert restored.priority == item.priority, "Item must not be empty"
        assert restored.confidence == item.confidence, "Item must not be empty"
        assert restored.tags == item.tags, "Item must not be empty"

    def test_defaults(self):
        now = datetime.now(timezone.utc)
        item = KnowledgeItem(
            id="KN-00002",
            knowledge_type=KnowledgeType.PATTERN,
            priority=KnowledgePriority.LOW,
            content="test",
            source="test",
            session_id="S1",
            created_at=now,
            last_accessed=now,
        )
        assert item.access_count == 0, "Item must not be empty"
        assert item.tags == [], "Item must not be empty"
        assert item.confidence == 1.0, "Item must not be empty"


# ---------------------------------------------------------------------------
# SessionSummary
# ---------------------------------------------------------------------------


class TestSessionSummary:
    def test_to_dict(self):
        now = datetime.now(timezone.utc)
        s = SessionSummary(
            session_id="S42",
            start_time=now,
            end_time=None,
            files_modified=["a.py"],
            patterns_used=["p1"],
            decisions_made=["d1"],
            issues_resolved=["i1"],
            learnings=["l1"],
            pending_work=["w1"],
        )
        d = s.to_dict()
        assert d["session_id"] == "S42", "Condition must be true"
        assert d["end_time"] is None, "Condition must be true"
        assert d["files_modified"] == ["a.py"], "Condition must be true"


# ---------------------------------------------------------------------------
# KnowledgeStore
# ---------------------------------------------------------------------------


class TestKnowledgeStore:
    @pytest.fixture()
    def store(self, tmp_path):
        return KnowledgeStore(store_path=tmp_path / "store.json")

    def _make_item(self, item_id="KN-00001", priority=KnowledgePriority.HIGH):
        now = datetime.now(timezone.utc)
        return KnowledgeItem(
            id=item_id,
            knowledge_type=KnowledgeType.FACTUAL,
            priority=priority,
            content="test content",
            source="test",
            session_id="S1",
            created_at=now,
            last_accessed=now,
        )

    def test_add_and_get(self, store):
        item = self._make_item()
        store.add(item)
        retrieved = store.get("KN-00001")
        assert retrieved is not None, "retrieved must be initialized"
        assert retrieved.content == "test content", "Content must not be empty"
        assert retrieved.access_count == 1, "Count must be greater than zero"

    def test_get_missing(self, store):
        assert store.get("nonexistent") is None, "st is not valid"

    def test_persistence(self, tmp_path):
        path = tmp_path / "store.json"
        store1 = KnowledgeStore(store_path=path)
        store1.add(self._make_item())

        store2 = KnowledgeStore(store_path=path)
        assert store2.get("KN-00001") is not None, "st must be initialized"

    def test_search_by_content(self, store):
        store.add(self._make_item("KN-1"))
        results = store.search("test content")
        assert len(results) >= 1, "Results must not be empty"

    def test_search_by_type(self, store):
        store.add(self._make_item("KN-1"))
        results = store.search("test", knowledge_type=KnowledgeType.FACTUAL)
        assert len(results) >= 1, "Results must not be empty"

    def test_search_filters_type(self, store):
        store.add(self._make_item("KN-1"))
        results = store.search("test", knowledge_type=KnowledgeType.PATTERN)
        assert len(results) == 0, "Results must not be empty"

    def test_get_by_type(self, store):
        store.add(self._make_item("KN-1"))
        items = store.get_by_type(KnowledgeType.FACTUAL)
        assert len(items) == 1, "Items must not be empty"

    def test_get_critical(self, store):
        store.add(self._make_item("KN-1", KnowledgePriority.CRITICAL))
        assert len(store.get_critical()) == 1, "Collection must not be empty"

    def test_count(self, store):
        assert store.count() == 0, "Count must be greater than zero"
        store.add(self._make_item("KN-1"))
        assert store.count() == 1, "Count must be greater than zero"

    def test_prune_low_priority(self, store):
        item = self._make_item("KN-1", KnowledgePriority.LOW)
        # Force old last_accessed
        from datetime import timedelta

        item.last_accessed = datetime.now(timezone.utc) - timedelta(days=60)
        store._knowledge[item.id] = item
        removed = store.prune_low_priority(max_age_days=30)
        assert removed == 1, "removed is not valid"
        assert store.count() == 0, "Count must be greater than zero"

    def test_corrupt_store_file(self, tmp_path):
        path = tmp_path / "store.json"
        path.write_text("{bad json")
        store = KnowledgeStore(store_path=path)
        assert store.count() == 0, "Count must be greater than zero"


# ---------------------------------------------------------------------------
# LearningExtractor
# ---------------------------------------------------------------------------


class TestLearningExtractor:
    @pytest.fixture()
    def extractor(self):
        return LearningExtractor()

    def test_extract_from_text(self, extractor):
        text = "The issue was broken imports.\nResolved by adding __init__.py."
        results = extractor.extract_from_text(text)
        assert len(results) >= 1, "Results must not be empty"
        assert any("issue" in r.lower() or "resolved" in r.lower() for r in results), "Result must not be empty"

    def test_extract_from_commit_messages(self, extractor):
        msgs = ["Fix broken import in training module", "Add new config option"]
        results = extractor.extract_from_commit_messages(msgs)
        assert len(results) >= 2, "Results must not be empty"
        assert any("Fix pattern:" in r for r in results), "Result must not be empty"
        assert any("Implementation:" in r for r in results), "Result must not be empty"

    def test_no_matches(self, extractor):
        text = "Nothing notable here."
        assert extractor.extract_from_text(text) == [], "extract is not valid"


# ---------------------------------------------------------------------------
# DecisionExtractor
# ---------------------------------------------------------------------------


class TestDecisionExtractor:
    @pytest.fixture()
    def extractor(self):
        return DecisionExtractor()

    def test_extract_decisions(self, extractor):
        text = "We decided to use Ruff for linting.\nChoosing extractive strategy."
        results = extractor.extract_from_text(text)
        assert len(results) >= 1, "Results must not be empty"

    def test_no_decisions(self, extractor):
        assert extractor.extract_from_text("Just some code.") == [], "extract is not valid"


# ---------------------------------------------------------------------------
# KnowledgeDistiller
# ---------------------------------------------------------------------------


class TestKnowledgeDistiller:
    @pytest.fixture()
    def distiller(self, tmp_path):
        return KnowledgeDistiller(store_path=tmp_path / "store.json")

    def test_distill_from_session_commits(self, distiller):
        items = distiller.distill_from_session(
            session_id="S100",
            files_modified=["a.py", "b.py"],
            commit_messages=["Fix broken import in module X"],
        )
        assert len(items) >= 1, "Items must not be empty"
        assert items[0].knowledge_type == KnowledgeType.PROCEDURAL, "Item must not be empty"

    def test_distill_from_session_notes(self, distiller):
        items = distiller.distill_from_session(
            session_id="S101",
            files_modified=[],
            commit_messages=[],
            session_notes="The issue was a race condition.\nResolved by adding a lock.",
        )
        assert len(items) >= 1, "Items must not be empty"

    def test_unique_ids(self, distiller):
        items1 = distiller.distill_from_session("S1", [], ["Fix A"])
        items2 = distiller.distill_from_session("S2", [], ["Fix B"])
        all_ids = [i.id for i in items1 + items2]
        assert len(all_ids) == len(set(all_ids)), "All_ids must not be empty"
