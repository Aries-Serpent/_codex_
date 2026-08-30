"""Supplementary tests for agents/agent_memory.py targeting Phase 9.1 gaps.

Targets uncovered branches: retrieve_content, consolidate_memories, statistics(),
search()/filter() variants, retrieve_similar_context empty-keyword path, and
invalidate_stale_contexts decay/delete paths.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agents.agent_memory import (
    AgentMemory,
    AgentMemorySystem,
    ContextFrame,
    MemoryEntry,
    PatternLibrary,
)


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "phase91.db"


def test_agent_memory_rejects_path_outside_allowed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError):
        AgentMemory(db_path=Path("/etc/never_allowed.db"))


def test_agent_memory_env_default_used(tmp_path, monkeypatch):
    target = tmp_path / "envdb.sqlite"
    monkeypatch.setenv("CODEX_LOG_DB_PATH", str(target))
    monkeypatch.chdir(tmp_path)
    mem = AgentMemory()
    assert mem.db_path == target.resolve(), "db_path is not valid"


def test_retrieve_content_paths(db_path):
    mem = AgentMemory(db_path=db_path)
    mem.store_memory(memory_id="rc1", category="c", content="payload")
    assert mem.retrieve_content("rc1") == "payload", "Content must not be empty"
    assert mem.retrieve_content(None) is None, "Content must not be empty"
    assert mem.retrieve_content("missing") is None, "Content must not be empty"


def test_consolidate_memories_decays_low_and_deletes_very_low(db_path):
    mem = AgentMemory(db_path=db_path)
    mem.store_memory(
        memory_id="low",
        category="c",
        content="x",
        confidence=0.25,
        created_at="2000-01-01T00:00:00Z",
    )
    mem.store_memory(
        memory_id="hi",
        category="c",
        content="y",
        confidence=0.9,
        created_at="2000-01-01T00:00:00Z",
    )
    n = mem.consolidate_memories()
    assert n == 2, "n is not valid"
    assert mem.retrieve_memory(memory_id="low") is None, "Condition must be true"
    hi = mem.retrieve_memory(memory_id="hi")
    assert hi is not None and hi.confidence < 0.9, "hi must be initialized"


def test_statistics_alias_matches_get_memory_stats(db_path):
    mem = AgentMemory(db_path=db_path)
    mem.store_memory(memory_id="s1", category="fact", content="a", confidence=0.8)
    assert mem.statistics() == mem.get_memory_stats(), "Condition must be true"


def test_search_query_filter_and_filter_with_criteria(db_path):
    mem = AgentMemory(db_path=db_path)
    mem.store_memory(memory_id="a", category="fact", content="ALPHA bravo", confidence=0.9)
    mem.store_memory(memory_id="b", category="decision", content="charlie", confidence=0.9)
    text = mem.search(query="alpha")
    assert [m.memory_id for m in text] == ["a"], "Condition must be true"
    assert mem.search(query="zzz") == [], "Condition must be true"
    # search() without query falls back to all.
    assert {m.memory_id for m in mem.search()} == {"a", "b"}
    # filter() with criteria mapping "type" -> category.
    assert [m.memory_id for m in mem.filter({"type": "fact"})] == ["a"], "Condition must be true"
    # filter() with no criteria.
    assert {m.memory_id for m in mem.filter(None)} == {"a", "b"}


def test_retrieve_similar_context_empty_keywords_fallback(db_path):
    system = AgentMemorySystem(agent_id="phase9", db_path=db_path)
    system.memory.store_memory(
        memory_id="m1",
        category="fact",
        content="anything",
        confidence=0.9,
    )
    # All words too short (<=3 chars) -> fallback branch.
    res = system.retrieve_similar_context("a b c", limit=5)
    assert isinstance(res, list)
    assert any(r["memory_id"] == "m1" for r in res), "Condition must be true"


def test_invalidate_stale_contexts_decay_and_delete(db_path):
    system = AgentMemorySystem(agent_id="phase9b", db_path=db_path)
    system.memory.store_memory(
        memory_id="old-low",
        category="c",
        content="x",
        confidence=0.25,
        created_at="2000-01-01T00:00:00Z",
    )
    system.memory.store_memory(
        memory_id="old-hi",
        category="c",
        content="y",
        confidence=0.9,
        created_at="2000-01-01T00:00:00Z",
    )
    n = system.invalidate_stale_contexts(age_days=1)
    assert n == 2, "n is not valid"
    assert system.memory.retrieve_memory(memory_id="old-low") is None, "Condition must be true"
    hi = system.memory.retrieve_memory(memory_id="old-hi")
    assert hi is not None and hi.confidence < 0.9, "hi must be initialized"


def test_get_pattern_library_returns_builtins(db_path):
    system = AgentMemorySystem(agent_id="phase9c", db_path=db_path)
    patterns = system.get_pattern_library()
    ids = {p["pattern_id"] for p in patterns}
    assert {"code_review_fix", "security_fix", "test_failure_debug"} <= ids


def test_record_decision_without_active_frame_records_none_frame(db_path):
    system = AgentMemorySystem(agent_id="phase9d", db_path=db_path)
    e = system.record_decision("d", alternatives=[], confidence=0.8, reasoning="r")
    assert e.context["task_frame"] is None, "Condition must be true"
    lesson = system.record_lesson("l", success=False)
    assert lesson.confidence == 0.7, "confidence is not valid"


def test_complete_task_no_frame_is_noop(db_path):
    system = AgentMemorySystem(agent_id="phase9e", db_path=db_path)
    system.complete_task(success=True, summary="ignored")
    assert system.current_frame is None, "current_frame is not valid"


def test_pattern_library_no_tag_match_uses_all_patterns():
    lib = PatternLibrary()
    lib.add_pattern(
        pattern_id="p",
        name="P",
        description="d",
        triggers=["alpha"],
        recommended_actions=["a"],
        success_rate=0.9,
        examples=[],
        tags=["x"],
    )
    # tags=None branch: candidates = all patterns.
    matches = lib.match_patterns("alpha story")
    assert matches and matches[0]["pattern"]["pattern_id"] == "p", "matches is not valid"


def test_memory_entry_and_context_frame_serialization():
    e = MemoryEntry(memory_id="m", category="c", content="x", context={"k": 1})
    assert MemoryEntry.from_dict(e.to_dict()).memory_id == "m", "memory_id is not valid"
    cf = ContextFrame(frame_id="f", task_description="t", start_time="now")
    assert cf.to_dict()["status"] == "active", "Condition must be true"
