"""Tests for quantum/physics-inspired context reconstruction (Pre-commit 5, S108).

Source: comment-3977050660 Phase 3 Pre-commit 5.

Validates:
- Wave collapse pattern selection by keyword overlap
- Entropy minimisation from status file parsing
- AfterMath lesson storage on reconstruction
- Pattern promotion (reconstruction event → new pattern candidate)
- "continue with next phase task" trigger is always emitted on reconstruction
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from codex.cognitive.session_hook import SessionContextInjector

# ---------------------------------------------------------------------------
# Fixture: failing API + seeded tmp pattern library
# ---------------------------------------------------------------------------


@pytest.fixture()
def _seeded_tmp(tmp_path):
    """Seed pattern library and status file under tmp_path."""
    brain_dir = tmp_path / ".codex" / "cognitive_brain"
    brain_dir.mkdir(parents=True)
    (brain_dir / "P-043.md").write_text(
        "P-043: Full HF mock pattern for training tests. huggingface training."
    )
    (brain_dir / "P-038.md").write_text(
        "P-038: -p no:rerunfailures in sharded runs prevents server-thread crash."
    )

    codex_dir = tmp_path / ".codex"
    (codex_dir / "COGNITIVE_BRAIN_STATUS_S107.md").write_text(
        "- HF_REVISION leak root cause documented\n"
        "- Shard crash pattern P-038 active\n"
        "- Session S107 complete\n"
    )
    return tmp_path


@pytest.fixture()
def failing_injector(_seeded_tmp):
    """SessionContextInjector whose API always raises."""
    mock_api = MagicMock()
    mock_api.get_session_context.side_effect = RuntimeError("Simulated failure")
    mock_api.store_memory.return_value = None

    injector = SessionContextInjector(
        brain_api=mock_api,
        cache_path=_seeded_tmp / ".codex" / ".session_context_cache.json",
    )
    return injector, mock_api, _seeded_tmp


# ---------------------------------------------------------------------------
# Core reconstruction tests
# ---------------------------------------------------------------------------


def test_reconstruction_emits_continuation_trigger(failing_injector):
    injector, _, tmp_path = failing_injector
    with patch(
        "codex.cognitive.session_hook.Path",
        side_effect=lambda p: (
            tmp_path / p if isinstance(p, str) and not p.startswith("/") else Path(p)
        ),
    ):
        payload = injector.inject({"session_number": 108, "pr_title": "huggingface fix"})
    assert payload.continuation_trigger == "continue with next phase task", "continuation_trigger is not valid"


def test_reconstruction_stores_lesson_in_memory(failing_injector):
    injector, mock_api, tmp_path = failing_injector
    with patch(
        "codex.cognitive.session_hook.Path",
        side_effect=lambda p: (
            tmp_path / p if isinstance(p, str) and not p.startswith("/") else Path(p)
        ),
    ):
        injector.inject({"session_number": 108, "pr_title": "training pipeline"})
    mock_api.store_memory.assert_called_once()
    lesson = mock_api.store_memory.call_args[0][0]
    assert "LESSON" in lesson, "Condition must be true"
    assert "quantum" in lesson.lower(), "Condition must be true"


def test_keyword_wave_collapse_surfaces_hf_pattern(failing_injector):
    injector, _, tmp_path = failing_injector
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
                "pr_body": "fix hf mock",
            }
        )
    assert "P-043" in payload.injected_patterns, "Condition must be true"


def test_reconstruction_flag_set_correctly(failing_injector):
    injector, _, tmp_path = failing_injector
    with patch(
        "codex.cognitive.session_hook.Path",
        side_effect=lambda p: (
            tmp_path / p if isinstance(p, str) and not p.startswith("/") else Path(p)
        ),
    ):
        payload = injector.inject({"session_number": 108, "pr_title": "misc"})
    assert payload.reconstructed is True, "reconstructed is not valid"
    assert "quantum" in payload.reconstruction_method, "Condition must be true"


def test_status_file_entropy_minimization(failing_injector):
    injector, _, tmp_path = failing_injector
    with patch(
        "codex.cognitive.session_hook.Path",
        side_effect=lambda p: (
            tmp_path / p if isinstance(p, str) and not p.startswith("/") else Path(p)
        ),
    ):
        payload = injector.inject({"session_number": 108, "pr_title": "misc"})
    assert any("HF_REVISION" in f or "S107" in f for f in payload.store_memory_facts), "Condition must be true"


def test_reconstruction_session_id_is_hashed(failing_injector):
    """Reconstructed session_id contains 'reconstructed-' prefix."""
    injector, _, tmp_path = failing_injector
    with patch(
        "codex.cognitive.session_hook.Path",
        side_effect=lambda p: (
            tmp_path / p if isinstance(p, str) and not p.startswith("/") else Path(p)
        ),
    ):
        payload = injector.inject({"session_number": 108, "pr_title": "misc"})
    assert payload.session_id.startswith("reconstructed-"), "Condition must be true"


def test_reconstruction_never_raises_even_with_empty_pattern_library(tmp_path):
    """Reconstruction must not raise even with no pattern files or status files."""
    mock_api = MagicMock()
    mock_api.get_session_context.side_effect = RuntimeError("failure")
    mock_api.store_memory.side_effect = RuntimeError("store_memory also fails")

    injector = SessionContextInjector(
        brain_api=mock_api,
        cache_path=tmp_path / "nonexistent_cache.json",
    )
    # Should not raise
    payload = injector.inject({"session_number": 108, "pr_title": "misc"})
    assert payload.reconstructed is True, "reconstructed is not valid"


def test_sharded_pr_surfaces_p038_pattern(failing_injector):
    """Shard-related keywords in PR title should match P-038.md."""
    injector, _, tmp_path = failing_injector
    with patch(
        "codex.cognitive.session_hook.Path",
        side_effect=lambda p: (
            tmp_path / p if isinstance(p, str) and not p.startswith("/") else Path(p)
        ),
    ):
        payload = injector.inject(
            {
                "session_number": 108,
                "pr_title": "sharded runs pytest rerunfailures crash",
                "pr_body": "fix sharded server thread",
            }
        )
    assert "P-038" in payload.injected_patterns, "Condition must be true"
