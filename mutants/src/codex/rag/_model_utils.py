"""Centralized safe SentenceTransformer loading with meta tensor fallback.

This module provides a single entry point for loading SentenceTransformer models
across the RAG subsystem (indexer, retriever, embeddings). It handles:

1. Standard loading with device='cpu'
2. Meta tensor detection and to_empty() fallback
3. HF_TOKEN authentication
4. Consistent error handling and logging

Usage:
    from codex.rag._model_utils import safe_load_sentence_transformer
    model = safe_load_sentence_transformer("all-MiniLM-L6-v2", cache_dir=os.path.join(tempfile.gettempdir(), "models"))
"""

from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def safe_load_sentence_transformer(  # nosec B107
    model_name: str,
    cache_dir: Optional[str] = None,
    use_auth_token_env_key: str = "HF_TOKEN",
) -> object:
    """Load a SentenceTransformer model safely, handling meta tensors.

    Attempts to load the model on CPU directly. If PyTorch creates meta tensors
    (common in PyTorch >= 2.0), falls back to loading on the meta device and
    materializing with ``to_empty(device='cpu')``.

    Args:
        model_name: HuggingFace model name or local path.
        cache_dir: Optional directory for cached model files.
        use_auth_token_env_key: Environment variable name for HF auth token.

    Returns:
        A ready-to-use ``SentenceTransformer`` model on CPU in eval mode.

    Raises:
        ImportError: If ``sentence-transformers`` is not installed.
        RuntimeError: If the model cannot be loaded or materialized.
    """
    from sentence_transformers import SentenceTransformer

    from codex.rag.utils import safe_model_to_device

    use_auth_token = os.environ.get(use_auth_token_env_key, False)
    token_value = use_auth_token if use_auth_token else None

    try:
        model = SentenceTransformer(
            model_name,
            device="cpu",
            cache_folder=cache_dir,
            trust_remote_code=False,
            use_auth_token=token_value,
        )

        # Handle meta tensors that PyTorch >=2.0 may create even with device='cpu'
        model = safe_model_to_device(model, "cpu")
        model.eval()
        logger.info("Model %s loaded on CPU (direct, auth=%s)", model_name, bool(use_auth_token))
        return model

    except NotImplementedError as exc:
        logger.warning("Meta tensor detected; attempting meta→to_empty: %s", exc)
        model = SentenceTransformer(
            model_name,
            device="meta",
            cache_folder=cache_dir,
            trust_remote_code=False,
            use_auth_token=token_value,
        )
        if not hasattr(model, "to_empty"):
            raise RuntimeError(
                "PyTorch lacks torch.nn.Module.to_empty(). "
                "Upgrade PyTorch to version with to_empty() support. "
                f"Original error: {exc}"
            ) from exc

        # Materialize meta tensors to CPU
        model = model.to_empty(device="cpu")
        model.eval()

        # CRITICAL: Verify no meta tensors remain
        meta_params = []
        for name, param in model.named_parameters():
            if param.is_meta:
                meta_params.append(name)

        if meta_params:
            raise RuntimeError(
                f"Meta tensors still present after to_empty(): {meta_params[:5]}... "
                "Model may not be fully materialized."
            ) from exc

        logger.info("Model %s materialized via to_empty() and verified", model_name)
        return model
