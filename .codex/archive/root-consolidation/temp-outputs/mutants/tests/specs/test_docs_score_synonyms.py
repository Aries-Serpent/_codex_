"""
Test Docs Score Synonyms

Test module for docs score synonyms.
"""

from __future__ import annotations

import pytest

pytest.importorskip("jinja2")
pytest.importorskip("yaml")

# Skip entire module - functions _docs_score and _expand_doc_tokens removed from audit_runner
pytestmark = pytest.mark.skip(
    reason="Functions _docs_score and _expand_doc_tokens removed from scripts.space_traversal.audit_runner"
)

# Minimal tests for docs scoring synonyms/variants (offline-safe)
# from scripts.space_traversal.audit_runner import _docs_score, _expand_doc_tokens


def test_expand_tokens_variants_include_synonyms():
    toks = _expand_doc_tokens("tokenization", ["token"])  # noqa: F821 - skipped module
    # Expect base token and known synonym variants
    assert "token" in toks, "Condition must be true"
    assert "sentencepiece" in toks, "Condition must be true"
    # naive pluralization present
    assert "tokens" in toks, "Condition must be true"


def test_docs_score_hits_synonym_in_doc():
    cache = {
        "docs/tokenization.md": "We integrate SentencePiece for subword models.",
        "README.md": "Setup instructions",
    }
    score = _docs_score("tokenization", cache, ["token"])  # noqa: F821 - skipped module
    # one doc hit among small corpus => positive score
    assert score > 0.0, "score must be greater than zero"


def test_docs_score_variants_plural_checkpoint():
    cache = {"docs/checkpoints.md": "How to manage checkpoints safely."}
    score = _docs_score("checkpointing", cache, ["checkpoint"])  # noqa: F821 - skipped module
    assert score > 0.0, "score must be greater than zero"
