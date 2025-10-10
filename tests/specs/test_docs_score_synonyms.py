from __future__ import annotations

# Minimal tests for docs scoring synonyms/variants (offline-safe)
from scripts.space_traversal.audit_runner import _docs_score, _expand_doc_tokens


def test_expand_tokens_variants_include_synonyms():
    toks = _expand_doc_tokens("tokenization", ["token"])
    # Expect base token and known synonym variants
    assert "token" in toks
    assert "sentencepiece" in toks
    # naive pluralization present
    assert "tokens" in toks


def test_docs_score_hits_synonym_in_doc():
    cache = {
        "docs/tokenization.md": "We integrate SentencePiece for subword models.",
        "README.md": "Setup instructions",
    }
    score = _docs_score("tokenization", cache, ["token"])
    # one doc hit among small corpus => positive score
    assert score > 0.0


def test_docs_score_variants_plural_checkpoint():
    cache = {"docs/checkpoints.md": "How to manage checkpoints safely."}
    score = _docs_score("checkpointing", cache, ["checkpoint"])
    assert score > 0.0
