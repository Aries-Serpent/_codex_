"""
Canonical registry names for codex_addons.

This module defines stable, frozen registry names used across the
codex_addons plugin system. These names form part of the public API
and should not be changed without a deprecation cycle.
"""
from __future__ import annotations

from typing import Final

# Metric registry names (stable)
METRIC_NAMES: Final[dict[str, str]] = {
    "token_accuracy": "Token-level accuracy",
    "ppl": "Perplexity",
    "exact_match": "Exact match ratio",
    "f1": "F1 score",
    "bleu": "BLEU score (requires optional extras)",
    "rouge": "ROUGE score (requires optional extras)",
}

# Model registry names (stable)
MODEL_NAMES: Final[dict[str, str]] = {
    "minilm": "MiniLM base model",
    "bert_base_uncased": "BERT base uncased",
    "gpt2": "GPT-2 base model",
}

# Data loader registry names (stable)
DATA_LOADER_NAMES: Final[dict[str, str]] = {
    "lines": "Line-by-line text loader",
    "jsonl": "JSON Lines loader",
    "csv": "CSV loader",
    "parquet": "Parquet loader",
}

# Tokenizer registry names (stable)
TOKENIZER_NAMES: Final[dict[str, str]] = {
    "hf": "Hugging Face tokenizer",
    "sentencepiece": "SentencePiece tokenizer",
}

# Trainer registry names (stable)
TRAINER_NAMES: Final[dict[str, str]] = {
    "functional": "Functional training loop",
    "hf_trainer": "Hugging Face Trainer",
}

# All stable registry names (for reference)
ALL_REGISTRY_NAMES: Final[dict[str, dict[str, str]]] = {
    "metrics": METRIC_NAMES,
    "models": MODEL_NAMES,
    "data_loaders": DATA_LOADER_NAMES,
    "tokenizers": TOKENIZER_NAMES,
    "trainers": TRAINER_NAMES,
}


def get_all_stable_names() -> dict[str, dict[str, str]]:
    """Get all stable registry names across all registries.
    
    Returns:
        Dictionary mapping registry kind to name->description mappings
    """
    return ALL_REGISTRY_NAMES.copy()


def is_stable_name(kind: str, name: str) -> bool:
    """Check if a name is in the stable registry for a given kind.
    
    Args:
        kind: Registry kind (e.g., 'metrics', 'models')
        name: Name to check
        
    Returns:
        True if name is in the stable registry for this kind
    """
    if kind not in ALL_REGISTRY_NAMES:
        return False
    return name in ALL_REGISTRY_NAMES[kind]


def get_description(kind: str, name: str) -> str | None:
    """Get description for a stable registry name.
    
    Args:
        kind: Registry kind (e.g., 'metrics', 'models')
        name: Name to look up
        
    Returns:
        Description string if found, None otherwise
    """
    if kind not in ALL_REGISTRY_NAMES:
        return None
    return ALL_REGISTRY_NAMES[kind].get(name)
