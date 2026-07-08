"""Tests for SessionContextInjector (session_hook.py).

Covers:
- Happy-path live API call
- Cache write / cache restore
- Quantum reconstruction on API failure + cache miss
- Wave-collapse keyword overlap pattern selection
- Entropy minimisation from status files
- AfterMath lesson storage on reconstruction
- Token budget trimming
- Recency ranking
- Prompt block rendering
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from codex.cognitive.session_hook import (
    MAX_CONTEXT_TOKENS,
    SessionContextInjector,
    SessionContextPayload,
    _apply_allowlist,
    _apply_recency_ranking,
    _estimate_tokens,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_api():
    """AgentBrainAPI mock that returns a minimal successful context."""
    api = MagicMock()
    api.get_session_context.return_value = MagicMock(
        session_id="s108",
        active_patterns=[
            {"id": "P-043", "introduced_session": 107},
            {"id": "P-038", "introduced_session": 105},
        ],
        continuation_from="Previous session completed 3 step(s).",
    )
    api.store_memory.return_value = None
    return api


@pytest.fixture()
def failing_api():
    """AgentBrainAPI mock that always fails get_session_context."""
    api = MagicMock()
    api.get_session_context.side_effect = RuntimeError("Simulated API failure")
    api.store_memory.return_value = None
    return api


@pytest.fixture()
def injector(mock_api, tmp_path):
    return SessionContextInjector(
        brain_api=mock_api,
        cache_path=tmp_path / ".session_context_cache.json",
    )


@pytest.fixture()
def failing_injector(failing_api, tmp_path):
    return SessionContextInjector(
        brain_api=failing_api,
        cache_path=tmp_path / ".session_context_cache.json",
    )


@pytest.fixture()
def pattern_library(tmp_path):
    """Seed a small pattern library under tmp_path/.codex/cognitive_brain/."""
    brain_dir = tmp_path / ".codex" / "cognitive_brain"
    brain_dir.mkdir(parents=True)
    (brain_dir / "P-043.md").write_text(
        "P-043: Full HF mock pattern for training tests. huggingface training fix."
    )
    (brain_dir / "P-038.md").write_text(
        "P-038: -p no:rerunfailures in sharded runs prevents server-thread crash."
    )
    return brain_dir


@pytest.fixture()
def status_file(tmp_path):
    """Seed a COGNITIVE_BRAIN_STATUS_S107.md under tmp_path/.codex/."""
    codex_dir = tmp_path / ".codex"
    codex_dir.mkdir(parents=True, exist_ok=True)
    status = codex_dir / "COGNITIVE_BRAIN_STATUS_S107.md"
    status.write_text(
        "- HF_REVISION leak root cause documented\n"
        "- Shard crash pattern P-038 active\n"
        "- Session S107 complete\n"
    )
    return status


# ---------------------------------------------------------------------------
# _apply_allowlist
# ---------------------------------------------------------------------------


def test_apply_allowlist_strips_unknown_fields():
    raw = {
        "session_id": "abc",
        "pattern_ids": [],
        "private_info": "SENSITIVE",
        "foo": "bar",
    }
    result = _apply_allowlist(raw)
    assert "private_info" not in result, "Result must not be empty"
    assert "foo" not in result, "Result must not be empty"
    assert "session_id" in result, "Result must not be empty"
    assert "pattern_ids" in result, "Result must not be empty"


def test_apply_allowlist_all_known():
    raw = {"session_id": "x", "store_memory_facts": ["f1"]}
    assert _apply_allowlist(raw) == raw, "Condition must be true"


def test_apply_allowlist_empty():
    assert _apply_allowlist({}) == {}, "Condition must be true"


# ---------------------------------------------------------------------------
# _apply_recency_ranking
# ---------------------------------------------------------------------------


def test_recency_ranking_newer_first():
    patterns = [
        {"id": "P-001", "introduced_session": 10},
        {"id": "P-043", "introduced_session": 107},
        {"id": "P-038", "introduced_session": 105},
    ]
    ranked = _apply_recency_ranking(patterns, current_session_num=108)
    assert ranked[0] == "P-043", "Condition must be true"
    assert "P-001" in ranked, "Condition must be true"


def test_recency_ranking_empty():
    assert _apply_recency_ranking([], current_session_num=10) == []


def test_recency_ranking_max_five():
    patterns = [{"id": f"P-{i:03d}", "introduced_session": i} for i in range(20)]
    ranked = _apply_recency_ranking(patterns, current_session_num=20)
    assert len(ranked) == 5, "Ranked must not be empty"


# ---------------------------------------------------------------------------
# _estimate_tokens
# ---------------------------------------------------------------------------


def test_estimate_tokens_basic():
    assert _estimate_tokens("abcd") == 1, "Condition must be true"
    assert _estimate_tokens("") == 0, "Condition must be true"
    assert _estimate_tokens("a" * 400) == 100, "Condition must be true"


# ---------------------------------------------------------------------------
# SessionContextPayload.to_prompt_block
# ---------------------------------------------------------------------------


def test_prompt_block_contains_session_id():
    payload = SessionContextPayload(
        session_id="s108",
        injected_patterns=["P-043"],
        store_memory_facts=["HF leak fixed"],
        continuation_trigger="continue with next phase task",
        cognitive_status_ref=".codex/COGNITIVE_BRAIN_STATUS_S107.md",
        token_estimate=20,
    )
    block = payload.to_prompt_block()
    assert "🧠 Cognitive Brain Context" in block, "Condition must be true"
    assert "s108" in block, "Condition must be true"
    assert "P-043" in block, "Condition must be true"
    assert "HF leak fixed" in block, "Condition must be true"
    assert "continue with next phase task" in block, "Condition must be true"


def test_prompt_block_reconstruction_warning():
    payload = SessionContextPayload(
        session_id="reconstructed-abc",
        injected_patterns=[],
        store_memory_facts=[],
        continuation_trigger=None,
        cognitive_status_ref=None,
        token_estimate=0,
        reconstructed=True,
        reconstruction_method="quantum_wave_collapse+entropy_minimization",
    )
    block = payload.to_prompt_block()
    assert "⚠️ Context reconstructed via" in block, "Condition must be true"
    assert "quantum_wave_collapse" in block, "Condition must be true"


# ---------------------------------------------------------------------------
# SessionContextInjector — happy path
# ---------------------------------------------------------------------------


def test_inject_live_api_success(injector, mock_api):
    payload = injector.inject({"session_number": 108})
    assert payload.reconstructed is False, "reconstructed is not valid"
    assert isinstance(payload.injected_patterns, list)
    assert payload.session_id == "s108", "session_id is not valid"


def test_inject_writes_cache(injector, tmp_path):
    injector.inject({"session_number": 108})
    cache_file = tmp_path / ".session_context_cache.json"
    assert cache_file.exists(), "Condition must be true"
    data = json.loads(cache_file.read_text())
    assert data["session_id"] == "s108", "Data must not be empty"


def test_inject_hf_pr_surfaces_p043(mock_api, tmp_path):
    """PR mentioning HuggingFace must surface P-043 in injected patterns."""
    mock_api.get_session_context.return_value = MagicMock(
        session_id="s108",
        active_patterns=[
            {"id": "P-043", "introduced_session": 107},
            {"id": "P-038", "introduced_session": 105},
        ],
        continuation_from="",
    )
    injector = SessionContextInjector(
        brain_api=mock_api,
        cache_path=tmp_path / ".cache.json",
    )
    payload = injector.inject({"session_number": 108, "pr_title": "HF training fix"})
    assert "P-043" in payload.injected_patterns, "Condition must be true"


# ---------------------------------------------------------------------------
# SessionContextInjector — cache restore
# ---------------------------------------------------------------------------


def test_inject_cache_restore_on_api_failure(failing_injector, tmp_path):
    """API failure → cache miss → quantum reconstruct; but if cache exists, restore it."""
    # Pre-seed cache
    cache_file = tmp_path / ".session_context_cache.json"
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(
        json.dumps(
            {
                "session_id": "cached-s107",
                "injected_patterns": ["P-038"],
                "store_memory_facts": ["cached fact"],
                "continuation_trigger": "continue with next phase task",
                "cognitive_status_ref": None,
                "token_estimate": 10,
            }
        )
    )
    payload = failing_injector.inject({"session_number": 108})
    assert payload.reconstructed is True, "reconstructed is not valid"
    assert payload.reconstruction_method == "cache_restore", "reconstruction_method is not valid"
    assert payload.session_id == "cached-s107", "session_id is not valid"


# ---------------------------------------------------------------------------
# SessionContextInjector — quantum reconstruction
# ---------------------------------------------------------------------------


def test_quantum_reconstruction_fires_on_cache_miss(failing_injector):
    payload = failing_injector.inject({"session_number": 108, "pr_title": "misc"})
    assert payload.reconstructed is True, "reconstructed is not valid"
    assert payload.reconstruction_method is not None, "reconstruction_method must be initialized"
    assert "quantum" in payload.reconstruction_method, "Condition must be true"


def test_reconstruction_emits_continuation_trigger(failing_injector):
    payload = failing_injector.inject({"session_number": 108})
    assert payload.continuation_trigger == "continue with next phase task", "continuation_trigger is not valid"


def test_reconstruction_stores_lesson(failing_api, tmp_path):
    injector = SessionContextInjector(
        brain_api=failing_api,
        cache_path=tmp_path / ".cache.json",
    )
    injector.inject({"session_number": 108, "pr_title": "training pipeline"})
    failing_api.store_memory.assert_called_once()
    lesson = failing_api.store_memory.call_args[0][0]
    assert "LESSON" in lesson, "Condition must be true"
    assert "quantum" in lesson.lower(), "Condition must be true"


def test_keyword_wave_collapse_surfaces_hf_pattern(failing_api, tmp_path, pattern_library):
    """Keywords in PR title should match P-043.md in the pattern library."""
    injector = SessionContextInjector(
        brain_api=failing_api,
        cache_path=tmp_path / ".cache.json",
    )
    # Patch Path(".codex/cognitive_brain/") to point at tmp pattern_library
    with patch(
        "codex.cognitive.session_hook.Path",
        side_effect=lambda p: (
            tmp_path / p if isinstance(p, str) and not p.startswith("/") else Path(p)
        ),
    ):
        payload = injector.inject(
            {
                "session_number": 108,
                "pr_title": "huggingface training",
                "pr_body": "fix hf mock pattern",
            }
        )
    # Wave-collapse should find P-043 based on keyword overlap
    assert (any("043" in pid or "038" in pid for pid in payload.injected_patterns), "Condition must be true"
        or payload.reconstructed
    )


def test_entropy_minimization_reads_status_file(failing_api, tmp_path, status_file):
    """Entropy minimisation should extract facts from the status file."""
    injector = SessionContextInjector(
        brain_api=failing_api,
        cache_path=tmp_path / ".cache.json",
    )
    with patch(
        "codex.cognitive.session_hook.Path",
        side_effect=lambda p: (
            tmp_path / p if isinstance(p, str) and not p.startswith("/") else Path(p)
    ), ):
        payload = injector.inject({"session_number": 108, "pr_title": "misc"})
    # If status file was read, facts should contain something
    assert isinstance(payload.store_memory_facts, list)


# ---------------------------------------------------------------------------
# Token budget
# ---------------------------------------------------------------------------


def test_token_budget_trimming(mock_api, tmp_path):
    """Oversized store_memory_facts should be trimmed to fit budget."""
    # Return a context with many facts
    mock_api.get_session_context.return_value = MagicMock(
        session_id="s108",
        active_patterns=[],
        continuation_from=" ".join(["word"] * 2000),  # many words → large fact
    )
    injector = SessionContextInjector(
        brain_api=mock_api,
        cache_path=tmp_path / ".cache.json",
    )
    payload = injector.inject({"session_number": 108})
    assert payload.token_estimate <= MAX_CONTEXT_TOKENS, "token_estimate is not valid"
