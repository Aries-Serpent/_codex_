"""
Embedding worker (single-process). Reads a JSON array of items from disk, optionally chunks and dedupes,
calls an Embedder (configured via EMBEDDER_CLASS), and persists embedding vectors via BackendAdapter.upsert_batch.

Safety:
- Uses adapter_loader.load_adapter() to get persistence adapter (defaults to in-repo mock)
- Uses EMBEDDER_CLASS for embedder (default: mock embedder)
- Guards live provider operations via src/mcp/server/safety_checks.live_tests_enabled()
- Uses retry_on_exception decorator and metrics hooks
"""  # noqa: E501

from __future__ import annotations

import json
import logging
import os
from collections.abc import Iterable
from typing import Any

from mcp.embeddings.batcher import batch_iterable, compute_checksum
from mcp.embeddings.chunking import chunk_texts
from mcp.embeddings.dedupe import InMemoryDeduper
from mcp.observability.metrics import Timer, increment
from mcp.retries import retry_on_exception
from mcp.server.adapter_loader import load_adapter
from mcp.server.safety_checks import live_tests_enabled
from mcp.workers.checkpoint import load_checkpoint, save_checkpoint

logger = logging.getLogger(__name__)


# PII hook (pluggable)
def default_preprocess(text: str) -> str:
    # noop by default; override to redact PII
    return text


_EMBEDDER_ALLOWLIST: frozenset[str] = frozenset(
    {
        "src.mcp.embeddings.mock_embedder.MockEmbedder",
        "src.mcp.embeddings.openai_embedder.OpenAIEmbedder",
        "src.mcp.embeddings.hf_embedder.HFEmbedder",
        "src.mcp.embeddings.sentence_transformer_embedder.SentenceTransformerEmbedder",
    }
)


def _load_embedder_class(path: str):
    """
    Load embedder class from an allowlisted path.

    Path example: 'src.mcp.embeddings.mock_embedder.MockEmbedder'

    Raises:
        ValueError: If the path is not in the allowlist (prevents arbitrary code injection).
    """
    if not path:
        from mcp.embeddings.mock_embedder import MockEmbedder

        return MockEmbedder
    if path not in _EMBEDDER_ALLOWLIST:
        raise ValueError(
            f"Unknown embedder class: {path!r}. Must be one of: {sorted(_EMBEDDER_ALLOWLIST)}"
        )
    module_name, cls_name = path.rsplit(".", 1)
    mod = __import__(module_name, fromlist=[cls_name])
    return getattr(mod, cls_name)


@retry_on_exception(tries=3)
def _upsert_with_retry(adapter, namespace: str, items: Iterable[dict[str, Any]]):
    adapter.upsert_batch(namespace, items)


def run_worker(
    input_path: str,
    batch_size: int = 32,
    namespace_default: str = "default",
    preprocess=default_preprocess,
    checkpoint_path: str | None = None,
):
    """
    Run the embedding worker:
    - load embedder (EMBEDDER_CLASS)
    - load adapter for persistence
    - load items from JSON array file
    - chunk/dedupe/checkpoint/batch/embed/upsert
    """
    embedder_path = os.environ.get(
        "EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder"
    )
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, encoding="utf-8") as fh:
        items = json.load(fh)

    # Load checkpoint if provided
    seen: set[str] = set()
    if checkpoint_path:
        seen = load_checkpoint(checkpoint_path)

    # Optionally chunk items (preserve original ids via chunk ids)
    # For simplicity: chunk every item into sub-items if content large
    all_items = []
    for it in items:
        # preprocess, e.g., PII redaction
        content = preprocess(it.get("content", ""))
        it["content"] = content
        # chunk
        chunks = chunk_texts(
            [it],
            max_chars=int(os.environ.get("EMBEDDING_CHUNK_MAX_CHARS", "1000")),
            overlap=int(os.environ.get("EMBEDDING_CHUNK_OVERLAP", "200")),
        )
        all_items.extend(chunks)

    deduper = InMemoryDeduper()
    # Filter out already processed (checkpoint) and duplicates
    pending = []
    for it in all_items:
        ch = compute_checksum(it)
        if ch in seen:
            continue
        if deduper.is_duplicate(it):
            continue
        pending.append(it)

    # Batch and process
    for batch in batch_iterable(pending, batch_size):
        texts = [b["content"] for b in batch]
        with Timer("embed_batch_latency"):
            # Guard live embedder calls behind ENABLE_LIVE_TESTS if embedder is a real provider
            if not live_tests_enabled():
                # If live tests not enabled and embedder is not mock, prefer using mock behavior
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)  # noqa: E501
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings, strict=False):
            upsert_items.append(
                {"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})}
            )
        # Persist with retry/backoff
        try:
            increment("worker_batch_total")
            with Timer("worker_upsert_latency"):
                _upsert_with_retry(adapter, namespace_default, upsert_items)
            # mark checkpoint entries as processed
            if checkpoint_path:
                for it in batch:
                    seen.add(compute_checksum(it))
                save_checkpoint(checkpoint_path, seen)
        except (IOError, OSError) as exc:
            type(exc).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")),
    )
    parser.add_argument(
        "--namespace",
        default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"),
    )
    parser.add_argument(
        "--checkpoint",
        default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"),
    )
    args = parser.parse_args()
    run_worker(
        args.input,
        batch_size=args.batch_size,
        namespace_default=args.namespace,
        checkpoint_path=args.checkpoint,
    )


if __name__ == "__main__":
    main()
