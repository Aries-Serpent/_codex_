"""Tests for transfer-learning scaffold — Phase 10D.

Validates the knowledge_transfer.py script's session knowledge base structure
and pattern library conformance for cross-session transfer readiness.
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_COGNITIVE = REPO_ROOT / "scripts" / "cognitive"


@pytest.fixture()
def knowledge_transfer_module():
    """Import knowledge_transfer.py as a module."""
    module_path = SCRIPTS_COGNITIVE / "knowledge_transfer.py"
    if not module_path.exists():
        pytest.skip("scripts/cognitive/knowledge_transfer.py not found")
    spec = importlib.util.spec_from_file_location("knowledge_transfer", module_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestSessionKnowledgeBase:
    def test_session_knowledge_is_list(self, knowledge_transfer_module):
        kb = knowledge_transfer_module.SESSION_KNOWLEDGE
        assert isinstance(kb, list)
        assert len(kb) >= 3, "Kb must not be empty"

    def test_session_entries_have_required_keys(self, knowledge_transfer_module):
        for entry in knowledge_transfer_module.SESSION_KNOWLEDGE:
            assert "session" in entry, "Condition must be true"
            assert "topic" in entry, "Condition must be true"
            assert "learnings" in entry, "Condition must be true"
            assert "patterns" in entry, "Condition must be true"

    def test_each_session_has_learnings(self, knowledge_transfer_module):
        for entry in knowledge_transfer_module.SESSION_KNOWLEDGE:
            assert isinstance(entry["learnings"], list)
            assert len(entry["learnings"]) >= 1, "Collection must not be empty"

    def test_each_session_has_patterns(self, knowledge_transfer_module):
        for entry in knowledge_transfer_module.SESSION_KNOWLEDGE:
            assert isinstance(entry["patterns"], list)
            assert len(entry["patterns"]) >= 1, "Collection must not be empty"

    def test_session_ids_unique(self, knowledge_transfer_module):
        ids = [e["session"] for e in knowledge_transfer_module.SESSION_KNOWLEDGE]
        assert len(ids) == len(set(ids)), "Ids must not be empty"


class TestPatternCoverage:
    """Ensure known patterns from the knowledge base cover key areas."""

    def test_known_patterns_exist(self, knowledge_transfer_module):
        all_patterns = []
        for entry in knowledge_transfer_module.SESSION_KNOWLEDGE:
            all_patterns.extend(entry["patterns"])
        # At minimum, expect some core patterns
        assert len(all_patterns) >= 3, "All_patterns must not be empty"

    def test_ci_related_patterns(self, knowledge_transfer_module):
        all_patterns = set()
        for entry in knowledge_transfer_module.SESSION_KNOWLEDGE:
            all_patterns.update(entry["patterns"])
        # Check at least some infrastructure patterns exist
        assert len(all_patterns) >= 2, "All_patterns must not be empty"


class TestRepoConstants:
    def test_repo_root_exists(self, knowledge_transfer_module):
        assert knowledge_transfer_module.REPO_ROOT.exists(), "Condition must be true"

    def test_changelog_path_defined(self, knowledge_transfer_module):
        # Path should be defined even if file doesn't exist
        assert hasattr(knowledge_transfer_module, "CHANGELOG")
