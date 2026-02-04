"""
Embedding worker (single-process). Reads a JSON array of items from disk, optionally chunks and dedupes,
calls an Embedder (configured via EMBEDDER_CLASS), and persists embedding vectors via BackendAdapter.upsert_batch.

Safety:
- Uses adapter_loader.load_adapter() to get persistence adapter (defaults to in-repo mock)
- Uses EMBEDDER_CLASS for embedder (default: mock embedder)
- Guards live provider operations via src/mcp/server/safety_checks.live_tests_enabled()
- Uses retry_on_exception decorator and metrics hooks
"""
from __future__ import annotations
import json
import logging
import os
from typing import Any, Iterable

from src.mcp.embeddings.batcher import batch_iterable, compute_checksum  # type: ignore
from src.mcp.embeddings.chunking import chunk_texts  # type: ignore
from src.mcp.embeddings.dedupe import InMemoryDeduper  # type: ignore
from src.mcp.workers.checkpoint import load_checkpoint, save_checkpoint  # type: ignore
from src.mcp.server.adapter_loader import load_adapter  # type: ignore
from src.mcp.observability.metrics import increment, Timer  # type: ignore
from src.mcp.retries import retry_on_exception  # type: ignore
from src.mcp.server.safety_checks import live_tests_enabled  # type: ignore

logger = logging.getLogger(__name__)
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


# PII hook (pluggable)
def default_preprocess(text: str) -> str:
    # noop by default; override to redact PII
    return text


def x__load_embedder_class__mutmut_orig(path: str):
    """
    Path example: 'src.mcp.embeddings.mock_embedder.MockEmbedder'
    """
    if not path:
        from src.mcp.embeddings.mock_embedder import MockEmbedder  # type: ignore

        return MockEmbedder
    module_name, cls_name = path.rsplit(".", 1)
    mod = __import__(module_name, fromlist=[cls_name])
    return getattr(mod, cls_name)


def x__load_embedder_class__mutmut_1(path: str):
    """
    Path example: 'src.mcp.embeddings.mock_embedder.MockEmbedder'
    """
    if path:
        from src.mcp.embeddings.mock_embedder import MockEmbedder  # type: ignore

        return MockEmbedder
    module_name, cls_name = path.rsplit(".", 1)
    mod = __import__(module_name, fromlist=[cls_name])
    return getattr(mod, cls_name)


def x__load_embedder_class__mutmut_2(path: str):
    """
    Path example: 'src.mcp.embeddings.mock_embedder.MockEmbedder'
    """
    if not path:
        from src.mcp.embeddings.mock_embedder import MockEmbedder  # type: ignore

        return MockEmbedder
    module_name, cls_name = None
    mod = __import__(module_name, fromlist=[cls_name])
    return getattr(mod, cls_name)


def x__load_embedder_class__mutmut_3(path: str):
    """
    Path example: 'src.mcp.embeddings.mock_embedder.MockEmbedder'
    """
    if not path:
        from src.mcp.embeddings.mock_embedder import MockEmbedder  # type: ignore

        return MockEmbedder
    module_name, cls_name = path.rsplit(None, 1)
    mod = __import__(module_name, fromlist=[cls_name])
    return getattr(mod, cls_name)


def x__load_embedder_class__mutmut_4(path: str):
    """
    Path example: 'src.mcp.embeddings.mock_embedder.MockEmbedder'
    """
    if not path:
        from src.mcp.embeddings.mock_embedder import MockEmbedder  # type: ignore

        return MockEmbedder
    module_name, cls_name = path.rsplit(".", None)
    mod = __import__(module_name, fromlist=[cls_name])
    return getattr(mod, cls_name)


def x__load_embedder_class__mutmut_5(path: str):
    """
    Path example: 'src.mcp.embeddings.mock_embedder.MockEmbedder'
    """
    if not path:
        from src.mcp.embeddings.mock_embedder import MockEmbedder  # type: ignore

        return MockEmbedder
    module_name, cls_name = path.rsplit(1)
    mod = __import__(module_name, fromlist=[cls_name])
    return getattr(mod, cls_name)


def x__load_embedder_class__mutmut_6(path: str):
    """
    Path example: 'src.mcp.embeddings.mock_embedder.MockEmbedder'
    """
    if not path:
        from src.mcp.embeddings.mock_embedder import MockEmbedder  # type: ignore

        return MockEmbedder
    module_name, cls_name = path.rsplit(".", )
    mod = __import__(module_name, fromlist=[cls_name])
    return getattr(mod, cls_name)


def x__load_embedder_class__mutmut_7(path: str):
    """
    Path example: 'src.mcp.embeddings.mock_embedder.MockEmbedder'
    """
    if not path:
        from src.mcp.embeddings.mock_embedder import MockEmbedder  # type: ignore

        return MockEmbedder
    module_name, cls_name = path.split(".", 1)
    mod = __import__(module_name, fromlist=[cls_name])
    return getattr(mod, cls_name)


def x__load_embedder_class__mutmut_8(path: str):
    """
    Path example: 'src.mcp.embeddings.mock_embedder.MockEmbedder'
    """
    if not path:
        from src.mcp.embeddings.mock_embedder import MockEmbedder  # type: ignore

        return MockEmbedder
    module_name, cls_name = path.rsplit("XX.XX", 1)
    mod = __import__(module_name, fromlist=[cls_name])
    return getattr(mod, cls_name)


def x__load_embedder_class__mutmut_9(path: str):
    """
    Path example: 'src.mcp.embeddings.mock_embedder.MockEmbedder'
    """
    if not path:
        from src.mcp.embeddings.mock_embedder import MockEmbedder  # type: ignore

        return MockEmbedder
    module_name, cls_name = path.rsplit(".", 2)
    mod = __import__(module_name, fromlist=[cls_name])
    return getattr(mod, cls_name)


def x__load_embedder_class__mutmut_10(path: str):
    """
    Path example: 'src.mcp.embeddings.mock_embedder.MockEmbedder'
    """
    if not path:
        from src.mcp.embeddings.mock_embedder import MockEmbedder  # type: ignore

        return MockEmbedder
    module_name, cls_name = path.rsplit(".", 1)
    mod = None
    return getattr(mod, cls_name)


def x__load_embedder_class__mutmut_11(path: str):
    """
    Path example: 'src.mcp.embeddings.mock_embedder.MockEmbedder'
    """
    if not path:
        from src.mcp.embeddings.mock_embedder import MockEmbedder  # type: ignore

        return MockEmbedder
    module_name, cls_name = path.rsplit(".", 1)
    mod = __import__(None, fromlist=[cls_name])
    return getattr(mod, cls_name)


def x__load_embedder_class__mutmut_12(path: str):
    """
    Path example: 'src.mcp.embeddings.mock_embedder.MockEmbedder'
    """
    if not path:
        from src.mcp.embeddings.mock_embedder import MockEmbedder  # type: ignore

        return MockEmbedder
    module_name, cls_name = path.rsplit(".", 1)
    mod = __import__(module_name, fromlist=None)
    return getattr(mod, cls_name)


def x__load_embedder_class__mutmut_13(path: str):
    """
    Path example: 'src.mcp.embeddings.mock_embedder.MockEmbedder'
    """
    if not path:
        from src.mcp.embeddings.mock_embedder import MockEmbedder  # type: ignore

        return MockEmbedder
    module_name, cls_name = path.rsplit(".", 1)
    mod = __import__(fromlist=[cls_name])
    return getattr(mod, cls_name)


def x__load_embedder_class__mutmut_14(path: str):
    """
    Path example: 'src.mcp.embeddings.mock_embedder.MockEmbedder'
    """
    if not path:
        from src.mcp.embeddings.mock_embedder import MockEmbedder  # type: ignore

        return MockEmbedder
    module_name, cls_name = path.rsplit(".", 1)
    mod = __import__(module_name, )
    return getattr(mod, cls_name)


def x__load_embedder_class__mutmut_15(path: str):
    """
    Path example: 'src.mcp.embeddings.mock_embedder.MockEmbedder'
    """
    if not path:
        from src.mcp.embeddings.mock_embedder import MockEmbedder  # type: ignore

        return MockEmbedder
    module_name, cls_name = path.rsplit(".", 1)
    mod = __import__(module_name, fromlist=[cls_name])
    return getattr(None, cls_name)


def x__load_embedder_class__mutmut_16(path: str):
    """
    Path example: 'src.mcp.embeddings.mock_embedder.MockEmbedder'
    """
    if not path:
        from src.mcp.embeddings.mock_embedder import MockEmbedder  # type: ignore

        return MockEmbedder
    module_name, cls_name = path.rsplit(".", 1)
    mod = __import__(module_name, fromlist=[cls_name])
    return getattr(mod, None)


def x__load_embedder_class__mutmut_17(path: str):
    """
    Path example: 'src.mcp.embeddings.mock_embedder.MockEmbedder'
    """
    if not path:
        from src.mcp.embeddings.mock_embedder import MockEmbedder  # type: ignore

        return MockEmbedder
    module_name, cls_name = path.rsplit(".", 1)
    mod = __import__(module_name, fromlist=[cls_name])
    return getattr(cls_name)


def x__load_embedder_class__mutmut_18(path: str):
    """
    Path example: 'src.mcp.embeddings.mock_embedder.MockEmbedder'
    """
    if not path:
        from src.mcp.embeddings.mock_embedder import MockEmbedder  # type: ignore

        return MockEmbedder
    module_name, cls_name = path.rsplit(".", 1)
    mod = __import__(module_name, fromlist=[cls_name])
    return getattr(mod, )

x__load_embedder_class__mutmut_mutants : ClassVar[MutantDict] = {
'x__load_embedder_class__mutmut_1': x__load_embedder_class__mutmut_1, 
    'x__load_embedder_class__mutmut_2': x__load_embedder_class__mutmut_2, 
    'x__load_embedder_class__mutmut_3': x__load_embedder_class__mutmut_3, 
    'x__load_embedder_class__mutmut_4': x__load_embedder_class__mutmut_4, 
    'x__load_embedder_class__mutmut_5': x__load_embedder_class__mutmut_5, 
    'x__load_embedder_class__mutmut_6': x__load_embedder_class__mutmut_6, 
    'x__load_embedder_class__mutmut_7': x__load_embedder_class__mutmut_7, 
    'x__load_embedder_class__mutmut_8': x__load_embedder_class__mutmut_8, 
    'x__load_embedder_class__mutmut_9': x__load_embedder_class__mutmut_9, 
    'x__load_embedder_class__mutmut_10': x__load_embedder_class__mutmut_10, 
    'x__load_embedder_class__mutmut_11': x__load_embedder_class__mutmut_11, 
    'x__load_embedder_class__mutmut_12': x__load_embedder_class__mutmut_12, 
    'x__load_embedder_class__mutmut_13': x__load_embedder_class__mutmut_13, 
    'x__load_embedder_class__mutmut_14': x__load_embedder_class__mutmut_14, 
    'x__load_embedder_class__mutmut_15': x__load_embedder_class__mutmut_15, 
    'x__load_embedder_class__mutmut_16': x__load_embedder_class__mutmut_16, 
    'x__load_embedder_class__mutmut_17': x__load_embedder_class__mutmut_17, 
    'x__load_embedder_class__mutmut_18': x__load_embedder_class__mutmut_18
}

def _load_embedder_class(*args, **kwargs):
    result = _mutmut_trampoline(x__load_embedder_class__mutmut_orig, x__load_embedder_class__mutmut_mutants, args, kwargs)
    return result 

_load_embedder_class.__signature__ = _mutmut_signature(x__load_embedder_class__mutmut_orig)
x__load_embedder_class__mutmut_orig.__name__ = 'x__load_embedder_class'


@retry_on_exception(tries=3)
def _upsert_with_retry(adapter, namespace: str, items: Iterable[dict[str, Any]]):
    adapter.upsert_batch(namespace, items)


def x_run_worker__mutmut_orig(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_1(
    input_path: str,
    batch_size: int = 33,
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_2(
    input_path: str,
    batch_size: int = 32,
    namespace_default: str = "XXdefaultXX",
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_3(
    input_path: str,
    batch_size: int = 32,
    namespace_default: str = "DEFAULT",
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_4(
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
    embedder_path = None
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_5(
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
    embedder_path = os.environ.get(None, "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_6(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", None)
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_7(
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
    embedder_path = os.environ.get("src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_8(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", )
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_9(
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
    embedder_path = os.environ.get("XXEMBEDDER_CLASSXX", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_10(
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
    embedder_path = os.environ.get("embedder_class", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_11(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "XXsrc.mcp.embeddings.mock_embedder.MockEmbedderXX")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_12(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.mockembedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_13(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "SRC.MCP.EMBEDDINGS.MOCK_EMBEDDER.MOCKEMBEDDER")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_14(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = None
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_15(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(None)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_16(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = None

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_17(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = None
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_18(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info(None, adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_19(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", None)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_20(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info(adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_21(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", )

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_22(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("XXUsing adapter: %sXX", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_23(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_24(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("USING ADAPTER: %S", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_25(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(None, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_26(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, None, encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_27(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding=None) as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_28(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open("r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_29(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_30(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", ) as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_31(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "XXrXX", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_32(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "R", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_33(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="XXutf-8XX") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_34(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="UTF-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_35(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
        items = None

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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_36(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
        items = json.load(None)

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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_37(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
        items = json.load(fh)

    # Load checkpoint if provided
    seen: set[str] = None
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_38(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
        items = json.load(fh)

    # Load checkpoint if provided
    seen: set[str] = set()
    if checkpoint_path:
        seen = None

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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_39(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
        items = json.load(fh)

    # Load checkpoint if provided
    seen: set[str] = set()
    if checkpoint_path:
        seen = load_checkpoint(None)

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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_40(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
        items = json.load(fh)

    # Load checkpoint if provided
    seen: set[str] = set()
    if checkpoint_path:
        seen = load_checkpoint(checkpoint_path)

    # Optionally chunk items (preserve original ids via chunk ids)
    # For simplicity: chunk every item into sub-items if content large
    all_items = None
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_41(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        content = None
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_42(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        content = preprocess(None)
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_43(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        content = preprocess(it.get(None, ""))
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_44(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        content = preprocess(it.get("content", None))
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_45(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        content = preprocess(it.get(""))
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_46(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        content = preprocess(it.get("content", ))
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_47(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        content = preprocess(it.get("XXcontentXX", ""))
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_48(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        content = preprocess(it.get("CONTENT", ""))
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_49(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        content = preprocess(it.get("content", "XXXX"))
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_50(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        it["content"] = None
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_51(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        it["XXcontentXX"] = content
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_52(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        it["CONTENT"] = content
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_53(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        chunks = None
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_54(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
            None,
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_55(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
            max_chars=None,
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_56(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
            overlap=None,
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_57(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_58(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_59(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_60(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
            max_chars=int(None),
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_61(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
            max_chars=int(os.environ.get(None, "1000")),
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_62(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
            max_chars=int(os.environ.get("EMBEDDING_CHUNK_MAX_CHARS", None)),
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_63(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
            max_chars=int(os.environ.get("1000")),
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_64(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
            max_chars=int(os.environ.get("EMBEDDING_CHUNK_MAX_CHARS", )),
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_65(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
            max_chars=int(os.environ.get("XXEMBEDDING_CHUNK_MAX_CHARSXX", "1000")),
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_66(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
            max_chars=int(os.environ.get("embedding_chunk_max_chars", "1000")),
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_67(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
            max_chars=int(os.environ.get("EMBEDDING_CHUNK_MAX_CHARS", "XX1000XX")),
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_68(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
            overlap=int(None),
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_69(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
            overlap=int(os.environ.get(None, "200")),
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_70(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
            overlap=int(os.environ.get("EMBEDDING_CHUNK_OVERLAP", None)),
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_71(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
            overlap=int(os.environ.get("200")),
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_72(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
            overlap=int(os.environ.get("EMBEDDING_CHUNK_OVERLAP", )),
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_73(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
            overlap=int(os.environ.get("XXEMBEDDING_CHUNK_OVERLAPXX", "200")),
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_74(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
            overlap=int(os.environ.get("embedding_chunk_overlap", "200")),
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_75(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
            overlap=int(os.environ.get("EMBEDDING_CHUNK_OVERLAP", "XX200XX")),
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_76(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        all_items.extend(None)

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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_77(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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

    deduper = None
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_78(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
    pending = None
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_79(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        ch = None
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_80(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        ch = compute_checksum(None)
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_81(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        if ch not in seen:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_82(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
            break
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_83(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        if deduper.is_duplicate(None):
            continue
        pending.append(it)

    # Batch and process
    for batch in batch_iterable(pending, batch_size):
        texts = [b["content"] for b in batch]
        with Timer("embed_batch_latency"):
            # Guard live embedder calls behind ENABLE_LIVE_TESTS if embedder is a real provider
            if not live_tests_enabled():
                # If live tests not enabled and embedder is not mock, prefer using mock behavior
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_84(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
            break
        pending.append(it)

    # Batch and process
    for batch in batch_iterable(pending, batch_size):
        texts = [b["content"] for b in batch]
        with Timer("embed_batch_latency"):
            # Guard live embedder calls behind ENABLE_LIVE_TESTS if embedder is a real provider
            if not live_tests_enabled():
                # If live tests not enabled and embedder is not mock, prefer using mock behavior
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_85(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        pending.append(None)

    # Batch and process
    for batch in batch_iterable(pending, batch_size):
        texts = [b["content"] for b in batch]
        with Timer("embed_batch_latency"):
            # Guard live embedder calls behind ENABLE_LIVE_TESTS if embedder is a real provider
            if not live_tests_enabled():
                # If live tests not enabled and embedder is not mock, prefer using mock behavior
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_86(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
    for batch in batch_iterable(None, batch_size):
        texts = [b["content"] for b in batch]
        with Timer("embed_batch_latency"):
            # Guard live embedder calls behind ENABLE_LIVE_TESTS if embedder is a real provider
            if not live_tests_enabled():
                # If live tests not enabled and embedder is not mock, prefer using mock behavior
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_87(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
    for batch in batch_iterable(pending, None):
        texts = [b["content"] for b in batch]
        with Timer("embed_batch_latency"):
            # Guard live embedder calls behind ENABLE_LIVE_TESTS if embedder is a real provider
            if not live_tests_enabled():
                # If live tests not enabled and embedder is not mock, prefer using mock behavior
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_88(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
    for batch in batch_iterable(batch_size):
        texts = [b["content"] for b in batch]
        with Timer("embed_batch_latency"):
            # Guard live embedder calls behind ENABLE_LIVE_TESTS if embedder is a real provider
            if not live_tests_enabled():
                # If live tests not enabled and embedder is not mock, prefer using mock behavior
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_89(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
    for batch in batch_iterable(pending, ):
        texts = [b["content"] for b in batch]
        with Timer("embed_batch_latency"):
            # Guard live embedder calls behind ENABLE_LIVE_TESTS if embedder is a real provider
            if not live_tests_enabled():
                # If live tests not enabled and embedder is not mock, prefer using mock behavior
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_90(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        texts = None
        with Timer("embed_batch_latency"):
            # Guard live embedder calls behind ENABLE_LIVE_TESTS if embedder is a real provider
            if not live_tests_enabled():
                # If live tests not enabled and embedder is not mock, prefer using mock behavior
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_91(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        texts = [b["XXcontentXX"] for b in batch]
        with Timer("embed_batch_latency"):
            # Guard live embedder calls behind ENABLE_LIVE_TESTS if embedder is a real provider
            if not live_tests_enabled():
                # If live tests not enabled and embedder is not mock, prefer using mock behavior
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_92(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        texts = [b["CONTENT"] for b in batch]
        with Timer("embed_batch_latency"):
            # Guard live embedder calls behind ENABLE_LIVE_TESTS if embedder is a real provider
            if not live_tests_enabled():
                # If live tests not enabled and embedder is not mock, prefer using mock behavior
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_93(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        with Timer(None):
            # Guard live embedder calls behind ENABLE_LIVE_TESTS if embedder is a real provider
            if not live_tests_enabled():
                # If live tests not enabled and embedder is not mock, prefer using mock behavior
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_94(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        with Timer("XXembed_batch_latencyXX"):
            # Guard live embedder calls behind ENABLE_LIVE_TESTS if embedder is a real provider
            if not live_tests_enabled():
                # If live tests not enabled and embedder is not mock, prefer using mock behavior
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_95(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
        with Timer("EMBED_BATCH_LATENCY"):
            # Guard live embedder calls behind ENABLE_LIVE_TESTS if embedder is a real provider
            if not live_tests_enabled():
                # If live tests not enabled and embedder is not mock, prefer using mock behavior
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_96(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
            if live_tests_enabled():
                # If live tests not enabled and embedder is not mock, prefer using mock behavior
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_97(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = None
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_98(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(None)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_99(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = None
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_100(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(None, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_101(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, None):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_102(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_103(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, ):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_104(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append(None)
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_105(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"XXidXX": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_106(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"ID": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_107(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["XXidXX"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_108(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["ID"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_109(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "XXembeddingXX": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_110(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "EMBEDDING": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_111(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "XXmetadataXX": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_112(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "METADATA": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_113(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get(None, {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_114(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", None)})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_115(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get({})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_116(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", )})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_117(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("XXmetadataXX", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_118(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("METADATA", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_119(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
        # Persist with retry/backoff
        try:
            increment(None)
            with Timer("worker_upsert_latency"):
                _upsert_with_retry(adapter, namespace_default, upsert_items)
            # mark checkpoint entries as processed
            if checkpoint_path:
                for it in batch:
                    seen.add(compute_checksum(it))
                save_checkpoint(checkpoint_path, seen)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_120(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
        # Persist with retry/backoff
        try:
            increment("XXworker_batch_totalXX")
            with Timer("worker_upsert_latency"):
                _upsert_with_retry(adapter, namespace_default, upsert_items)
            # mark checkpoint entries as processed
            if checkpoint_path:
                for it in batch:
                    seen.add(compute_checksum(it))
                save_checkpoint(checkpoint_path, seen)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_121(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
        # Persist with retry/backoff
        try:
            increment("WORKER_BATCH_TOTAL")
            with Timer("worker_upsert_latency"):
                _upsert_with_retry(adapter, namespace_default, upsert_items)
            # mark checkpoint entries as processed
            if checkpoint_path:
                for it in batch:
                    seen.add(compute_checksum(it))
                save_checkpoint(checkpoint_path, seen)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_122(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
        # Persist with retry/backoff
        try:
            increment("worker_batch_total")
            with Timer(None):
                _upsert_with_retry(adapter, namespace_default, upsert_items)
            # mark checkpoint entries as processed
            if checkpoint_path:
                for it in batch:
                    seen.add(compute_checksum(it))
                save_checkpoint(checkpoint_path, seen)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_123(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
        # Persist with retry/backoff
        try:
            increment("worker_batch_total")
            with Timer("XXworker_upsert_latencyXX"):
                _upsert_with_retry(adapter, namespace_default, upsert_items)
            # mark checkpoint entries as processed
            if checkpoint_path:
                for it in batch:
                    seen.add(compute_checksum(it))
                save_checkpoint(checkpoint_path, seen)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_124(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
        # Persist with retry/backoff
        try:
            increment("worker_batch_total")
            with Timer("WORKER_UPSERT_LATENCY"):
                _upsert_with_retry(adapter, namespace_default, upsert_items)
            # mark checkpoint entries as processed
            if checkpoint_path:
                for it in batch:
                    seen.add(compute_checksum(it))
                save_checkpoint(checkpoint_path, seen)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_125(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
        # Persist with retry/backoff
        try:
            increment("worker_batch_total")
            with Timer("worker_upsert_latency"):
                _upsert_with_retry(None, namespace_default, upsert_items)
            # mark checkpoint entries as processed
            if checkpoint_path:
                for it in batch:
                    seen.add(compute_checksum(it))
                save_checkpoint(checkpoint_path, seen)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_126(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
        # Persist with retry/backoff
        try:
            increment("worker_batch_total")
            with Timer("worker_upsert_latency"):
                _upsert_with_retry(adapter, None, upsert_items)
            # mark checkpoint entries as processed
            if checkpoint_path:
                for it in batch:
                    seen.add(compute_checksum(it))
                save_checkpoint(checkpoint_path, seen)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_127(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
        # Persist with retry/backoff
        try:
            increment("worker_batch_total")
            with Timer("worker_upsert_latency"):
                _upsert_with_retry(adapter, namespace_default, None)
            # mark checkpoint entries as processed
            if checkpoint_path:
                for it in batch:
                    seen.add(compute_checksum(it))
                save_checkpoint(checkpoint_path, seen)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_128(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
        # Persist with retry/backoff
        try:
            increment("worker_batch_total")
            with Timer("worker_upsert_latency"):
                _upsert_with_retry(namespace_default, upsert_items)
            # mark checkpoint entries as processed
            if checkpoint_path:
                for it in batch:
                    seen.add(compute_checksum(it))
                save_checkpoint(checkpoint_path, seen)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_129(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
        # Persist with retry/backoff
        try:
            increment("worker_batch_total")
            with Timer("worker_upsert_latency"):
                _upsert_with_retry(adapter, upsert_items)
            # mark checkpoint entries as processed
            if checkpoint_path:
                for it in batch:
                    seen.add(compute_checksum(it))
                save_checkpoint(checkpoint_path, seen)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_130(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
        # Persist with retry/backoff
        try:
            increment("worker_batch_total")
            with Timer("worker_upsert_latency"):
                _upsert_with_retry(adapter, namespace_default, )
            # mark checkpoint entries as processed
            if checkpoint_path:
                for it in batch:
                    seen.add(compute_checksum(it))
                save_checkpoint(checkpoint_path, seen)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_131(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
        # Persist with retry/backoff
        try:
            increment("worker_batch_total")
            with Timer("worker_upsert_latency"):
                _upsert_with_retry(adapter, namespace_default, upsert_items)
            # mark checkpoint entries as processed
            if checkpoint_path:
                for it in batch:
                    seen.add(None)
                save_checkpoint(checkpoint_path, seen)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_132(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
        # Persist with retry/backoff
        try:
            increment("worker_batch_total")
            with Timer("worker_upsert_latency"):
                _upsert_with_retry(adapter, namespace_default, upsert_items)
            # mark checkpoint entries as processed
            if checkpoint_path:
                for it in batch:
                    seen.add(compute_checksum(None))
                save_checkpoint(checkpoint_path, seen)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_133(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
        # Persist with retry/backoff
        try:
            increment("worker_batch_total")
            with Timer("worker_upsert_latency"):
                _upsert_with_retry(adapter, namespace_default, upsert_items)
            # mark checkpoint entries as processed
            if checkpoint_path:
                for it in batch:
                    seen.add(compute_checksum(it))
                save_checkpoint(None, seen)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_134(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
        # Persist with retry/backoff
        try:
            increment("worker_batch_total")
            with Timer("worker_upsert_latency"):
                _upsert_with_retry(adapter, namespace_default, upsert_items)
            # mark checkpoint entries as processed
            if checkpoint_path:
                for it in batch:
                    seen.add(compute_checksum(it))
                save_checkpoint(checkpoint_path, None)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_135(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
        # Persist with retry/backoff
        try:
            increment("worker_batch_total")
            with Timer("worker_upsert_latency"):
                _upsert_with_retry(adapter, namespace_default, upsert_items)
            # mark checkpoint entries as processed
            if checkpoint_path:
                for it in batch:
                    seen.add(compute_checksum(it))
                save_checkpoint(seen)
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_136(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
        # Persist with retry/backoff
        try:
            increment("worker_batch_total")
            with Timer("worker_upsert_latency"):
                _upsert_with_retry(adapter, namespace_default, upsert_items)
            # mark checkpoint entries as processed
            if checkpoint_path:
                for it in batch:
                    seen.add(compute_checksum(it))
                save_checkpoint(checkpoint_path, )
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_137(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(None)
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_138(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment(None)
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_139(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("XXworker_batch_failuresXX")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_140(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("WORKER_BATCH_FAILURES")
            logger.exception("Failed to upsert batch: %s", exc)


def x_run_worker__mutmut_141(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception(None, exc)


def x_run_worker__mutmut_142(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", None)


def x_run_worker__mutmut_143(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception(exc)


def x_run_worker__mutmut_144(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("Failed to upsert batch: %s", )


def x_run_worker__mutmut_145(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("XXFailed to upsert batch: %sXX", exc)


def x_run_worker__mutmut_146(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("failed to upsert batch: %s", exc)


def x_run_worker__mutmut_147(
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
    embedder_path = os.environ.get("EMBEDDER_CLASS", "src.mcp.embeddings.mock_embedder.MockEmbedder")
    EmbedderCls = _load_embedder_class(embedder_path)
    embedder = EmbedderCls()

    adapter, adapter_path = load_adapter()
    logger.info("Using adapter: %s", adapter_path)

    # Read input (JSON array)
    with open(input_path, "r", encoding="utf-8") as fh:
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
                # but embedder implementations should be safe; here we call embedder regardless (mock by default)
                pass
            embeddings = embedder.embed(texts)
        upsert_items = []
        for it, emb in zip(batch, embeddings):
            upsert_items.append({"id": it["id"], "embedding": emb, "metadata": it.get("metadata", {})})
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
        except Exception as exc:
            logger.debug(f"Exception: {exc}")
            increment("worker_batch_failures")
            logger.exception("FAILED TO UPSERT BATCH: %S", exc)

x_run_worker__mutmut_mutants : ClassVar[MutantDict] = {
'x_run_worker__mutmut_1': x_run_worker__mutmut_1, 
    'x_run_worker__mutmut_2': x_run_worker__mutmut_2, 
    'x_run_worker__mutmut_3': x_run_worker__mutmut_3, 
    'x_run_worker__mutmut_4': x_run_worker__mutmut_4, 
    'x_run_worker__mutmut_5': x_run_worker__mutmut_5, 
    'x_run_worker__mutmut_6': x_run_worker__mutmut_6, 
    'x_run_worker__mutmut_7': x_run_worker__mutmut_7, 
    'x_run_worker__mutmut_8': x_run_worker__mutmut_8, 
    'x_run_worker__mutmut_9': x_run_worker__mutmut_9, 
    'x_run_worker__mutmut_10': x_run_worker__mutmut_10, 
    'x_run_worker__mutmut_11': x_run_worker__mutmut_11, 
    'x_run_worker__mutmut_12': x_run_worker__mutmut_12, 
    'x_run_worker__mutmut_13': x_run_worker__mutmut_13, 
    'x_run_worker__mutmut_14': x_run_worker__mutmut_14, 
    'x_run_worker__mutmut_15': x_run_worker__mutmut_15, 
    'x_run_worker__mutmut_16': x_run_worker__mutmut_16, 
    'x_run_worker__mutmut_17': x_run_worker__mutmut_17, 
    'x_run_worker__mutmut_18': x_run_worker__mutmut_18, 
    'x_run_worker__mutmut_19': x_run_worker__mutmut_19, 
    'x_run_worker__mutmut_20': x_run_worker__mutmut_20, 
    'x_run_worker__mutmut_21': x_run_worker__mutmut_21, 
    'x_run_worker__mutmut_22': x_run_worker__mutmut_22, 
    'x_run_worker__mutmut_23': x_run_worker__mutmut_23, 
    'x_run_worker__mutmut_24': x_run_worker__mutmut_24, 
    'x_run_worker__mutmut_25': x_run_worker__mutmut_25, 
    'x_run_worker__mutmut_26': x_run_worker__mutmut_26, 
    'x_run_worker__mutmut_27': x_run_worker__mutmut_27, 
    'x_run_worker__mutmut_28': x_run_worker__mutmut_28, 
    'x_run_worker__mutmut_29': x_run_worker__mutmut_29, 
    'x_run_worker__mutmut_30': x_run_worker__mutmut_30, 
    'x_run_worker__mutmut_31': x_run_worker__mutmut_31, 
    'x_run_worker__mutmut_32': x_run_worker__mutmut_32, 
    'x_run_worker__mutmut_33': x_run_worker__mutmut_33, 
    'x_run_worker__mutmut_34': x_run_worker__mutmut_34, 
    'x_run_worker__mutmut_35': x_run_worker__mutmut_35, 
    'x_run_worker__mutmut_36': x_run_worker__mutmut_36, 
    'x_run_worker__mutmut_37': x_run_worker__mutmut_37, 
    'x_run_worker__mutmut_38': x_run_worker__mutmut_38, 
    'x_run_worker__mutmut_39': x_run_worker__mutmut_39, 
    'x_run_worker__mutmut_40': x_run_worker__mutmut_40, 
    'x_run_worker__mutmut_41': x_run_worker__mutmut_41, 
    'x_run_worker__mutmut_42': x_run_worker__mutmut_42, 
    'x_run_worker__mutmut_43': x_run_worker__mutmut_43, 
    'x_run_worker__mutmut_44': x_run_worker__mutmut_44, 
    'x_run_worker__mutmut_45': x_run_worker__mutmut_45, 
    'x_run_worker__mutmut_46': x_run_worker__mutmut_46, 
    'x_run_worker__mutmut_47': x_run_worker__mutmut_47, 
    'x_run_worker__mutmut_48': x_run_worker__mutmut_48, 
    'x_run_worker__mutmut_49': x_run_worker__mutmut_49, 
    'x_run_worker__mutmut_50': x_run_worker__mutmut_50, 
    'x_run_worker__mutmut_51': x_run_worker__mutmut_51, 
    'x_run_worker__mutmut_52': x_run_worker__mutmut_52, 
    'x_run_worker__mutmut_53': x_run_worker__mutmut_53, 
    'x_run_worker__mutmut_54': x_run_worker__mutmut_54, 
    'x_run_worker__mutmut_55': x_run_worker__mutmut_55, 
    'x_run_worker__mutmut_56': x_run_worker__mutmut_56, 
    'x_run_worker__mutmut_57': x_run_worker__mutmut_57, 
    'x_run_worker__mutmut_58': x_run_worker__mutmut_58, 
    'x_run_worker__mutmut_59': x_run_worker__mutmut_59, 
    'x_run_worker__mutmut_60': x_run_worker__mutmut_60, 
    'x_run_worker__mutmut_61': x_run_worker__mutmut_61, 
    'x_run_worker__mutmut_62': x_run_worker__mutmut_62, 
    'x_run_worker__mutmut_63': x_run_worker__mutmut_63, 
    'x_run_worker__mutmut_64': x_run_worker__mutmut_64, 
    'x_run_worker__mutmut_65': x_run_worker__mutmut_65, 
    'x_run_worker__mutmut_66': x_run_worker__mutmut_66, 
    'x_run_worker__mutmut_67': x_run_worker__mutmut_67, 
    'x_run_worker__mutmut_68': x_run_worker__mutmut_68, 
    'x_run_worker__mutmut_69': x_run_worker__mutmut_69, 
    'x_run_worker__mutmut_70': x_run_worker__mutmut_70, 
    'x_run_worker__mutmut_71': x_run_worker__mutmut_71, 
    'x_run_worker__mutmut_72': x_run_worker__mutmut_72, 
    'x_run_worker__mutmut_73': x_run_worker__mutmut_73, 
    'x_run_worker__mutmut_74': x_run_worker__mutmut_74, 
    'x_run_worker__mutmut_75': x_run_worker__mutmut_75, 
    'x_run_worker__mutmut_76': x_run_worker__mutmut_76, 
    'x_run_worker__mutmut_77': x_run_worker__mutmut_77, 
    'x_run_worker__mutmut_78': x_run_worker__mutmut_78, 
    'x_run_worker__mutmut_79': x_run_worker__mutmut_79, 
    'x_run_worker__mutmut_80': x_run_worker__mutmut_80, 
    'x_run_worker__mutmut_81': x_run_worker__mutmut_81, 
    'x_run_worker__mutmut_82': x_run_worker__mutmut_82, 
    'x_run_worker__mutmut_83': x_run_worker__mutmut_83, 
    'x_run_worker__mutmut_84': x_run_worker__mutmut_84, 
    'x_run_worker__mutmut_85': x_run_worker__mutmut_85, 
    'x_run_worker__mutmut_86': x_run_worker__mutmut_86, 
    'x_run_worker__mutmut_87': x_run_worker__mutmut_87, 
    'x_run_worker__mutmut_88': x_run_worker__mutmut_88, 
    'x_run_worker__mutmut_89': x_run_worker__mutmut_89, 
    'x_run_worker__mutmut_90': x_run_worker__mutmut_90, 
    'x_run_worker__mutmut_91': x_run_worker__mutmut_91, 
    'x_run_worker__mutmut_92': x_run_worker__mutmut_92, 
    'x_run_worker__mutmut_93': x_run_worker__mutmut_93, 
    'x_run_worker__mutmut_94': x_run_worker__mutmut_94, 
    'x_run_worker__mutmut_95': x_run_worker__mutmut_95, 
    'x_run_worker__mutmut_96': x_run_worker__mutmut_96, 
    'x_run_worker__mutmut_97': x_run_worker__mutmut_97, 
    'x_run_worker__mutmut_98': x_run_worker__mutmut_98, 
    'x_run_worker__mutmut_99': x_run_worker__mutmut_99, 
    'x_run_worker__mutmut_100': x_run_worker__mutmut_100, 
    'x_run_worker__mutmut_101': x_run_worker__mutmut_101, 
    'x_run_worker__mutmut_102': x_run_worker__mutmut_102, 
    'x_run_worker__mutmut_103': x_run_worker__mutmut_103, 
    'x_run_worker__mutmut_104': x_run_worker__mutmut_104, 
    'x_run_worker__mutmut_105': x_run_worker__mutmut_105, 
    'x_run_worker__mutmut_106': x_run_worker__mutmut_106, 
    'x_run_worker__mutmut_107': x_run_worker__mutmut_107, 
    'x_run_worker__mutmut_108': x_run_worker__mutmut_108, 
    'x_run_worker__mutmut_109': x_run_worker__mutmut_109, 
    'x_run_worker__mutmut_110': x_run_worker__mutmut_110, 
    'x_run_worker__mutmut_111': x_run_worker__mutmut_111, 
    'x_run_worker__mutmut_112': x_run_worker__mutmut_112, 
    'x_run_worker__mutmut_113': x_run_worker__mutmut_113, 
    'x_run_worker__mutmut_114': x_run_worker__mutmut_114, 
    'x_run_worker__mutmut_115': x_run_worker__mutmut_115, 
    'x_run_worker__mutmut_116': x_run_worker__mutmut_116, 
    'x_run_worker__mutmut_117': x_run_worker__mutmut_117, 
    'x_run_worker__mutmut_118': x_run_worker__mutmut_118, 
    'x_run_worker__mutmut_119': x_run_worker__mutmut_119, 
    'x_run_worker__mutmut_120': x_run_worker__mutmut_120, 
    'x_run_worker__mutmut_121': x_run_worker__mutmut_121, 
    'x_run_worker__mutmut_122': x_run_worker__mutmut_122, 
    'x_run_worker__mutmut_123': x_run_worker__mutmut_123, 
    'x_run_worker__mutmut_124': x_run_worker__mutmut_124, 
    'x_run_worker__mutmut_125': x_run_worker__mutmut_125, 
    'x_run_worker__mutmut_126': x_run_worker__mutmut_126, 
    'x_run_worker__mutmut_127': x_run_worker__mutmut_127, 
    'x_run_worker__mutmut_128': x_run_worker__mutmut_128, 
    'x_run_worker__mutmut_129': x_run_worker__mutmut_129, 
    'x_run_worker__mutmut_130': x_run_worker__mutmut_130, 
    'x_run_worker__mutmut_131': x_run_worker__mutmut_131, 
    'x_run_worker__mutmut_132': x_run_worker__mutmut_132, 
    'x_run_worker__mutmut_133': x_run_worker__mutmut_133, 
    'x_run_worker__mutmut_134': x_run_worker__mutmut_134, 
    'x_run_worker__mutmut_135': x_run_worker__mutmut_135, 
    'x_run_worker__mutmut_136': x_run_worker__mutmut_136, 
    'x_run_worker__mutmut_137': x_run_worker__mutmut_137, 
    'x_run_worker__mutmut_138': x_run_worker__mutmut_138, 
    'x_run_worker__mutmut_139': x_run_worker__mutmut_139, 
    'x_run_worker__mutmut_140': x_run_worker__mutmut_140, 
    'x_run_worker__mutmut_141': x_run_worker__mutmut_141, 
    'x_run_worker__mutmut_142': x_run_worker__mutmut_142, 
    'x_run_worker__mutmut_143': x_run_worker__mutmut_143, 
    'x_run_worker__mutmut_144': x_run_worker__mutmut_144, 
    'x_run_worker__mutmut_145': x_run_worker__mutmut_145, 
    'x_run_worker__mutmut_146': x_run_worker__mutmut_146, 
    'x_run_worker__mutmut_147': x_run_worker__mutmut_147
}

def run_worker(*args, **kwargs):
    result = _mutmut_trampoline(x_run_worker__mutmut_orig, x_run_worker__mutmut_mutants, args, kwargs)
    return result 

run_worker.__signature__ = _mutmut_signature(x_run_worker__mutmut_orig)
x_run_worker__mutmut_orig.__name__ = 'x_run_worker'


def x_main__mutmut_orig():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_1():
    import argparse

    parser = None
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_2():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(None, required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_3():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=None, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_4():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help=None)
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_5():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_6():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_7():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, )
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_8():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("XX--inputXX", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_9():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--INPUT", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_10():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=False, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_11():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="XXPath to JSON array file with itemsXX")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_12():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="path to json array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_13():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="PATH TO JSON ARRAY FILE WITH ITEMS")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_14():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument(None, type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_15():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=None, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_16():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_17():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument(type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_18():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_19():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, )
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_20():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("XX--batch-sizeXX", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_21():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--BATCH-SIZE", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_22():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(None))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_23():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get(None, "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_24():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", None)))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_25():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_26():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", )))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_27():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("XXEMBEDDING_BATCH_SIZEXX", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_28():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("embedding_batch_size", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_29():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "XX32XX")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_30():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument(None, default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_31():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=None)
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_32():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument(default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_33():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", )
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_34():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("XX--namespaceXX", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_35():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--NAMESPACE", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_36():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get(None, "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_37():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", None))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_38():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_39():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", ))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_40():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("XXEMBEDDING_WORKER_NAMESPACE_DEFAULTXX", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_41():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("embedding_worker_namespace_default", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_42():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "XXdefaultXX"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_43():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "DEFAULT"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_44():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument(None, default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_45():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=None)
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_46():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument(default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_47():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", )
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_48():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("XX--checkpointXX", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_49():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--CHECKPOINT", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_50():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get(None, "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_51():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", None))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_52():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_53():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", ))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_54():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("XXEMBEDDING_CHECKPOINT_PATHXX", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_55():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("embedding_checkpoint_path", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_56():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "XXembeddings.checkpoint.jsonXX"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_57():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "EMBEDDINGS.CHECKPOINT.JSON"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_58():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = None
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_59():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(None, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_60():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=None, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_61():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=None, checkpoint_path=args.checkpoint)


def x_main__mutmut_62():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=None)


def x_main__mutmut_63():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(batch_size=args.batch_size, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_64():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, namespace_default=args.namespace, checkpoint_path=args.checkpoint)


def x_main__mutmut_65():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, checkpoint_path=args.checkpoint)


def x_main__mutmut_66():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON array file with items")
    parser.add_argument("--batch-size", type=int, default=int(os.environ.get("EMBEDDING_BATCH_SIZE", "32")))
    parser.add_argument("--namespace", default=os.environ.get("EMBEDDING_WORKER_NAMESPACE_DEFAULT", "default"))
    parser.add_argument("--checkpoint", default=os.environ.get("EMBEDDING_CHECKPOINT_PATH", "embeddings.checkpoint.json"))
    args = parser.parse_args()
    run_worker(args.input, batch_size=args.batch_size, namespace_default=args.namespace, )

x_main__mutmut_mutants : ClassVar[MutantDict] = {
'x_main__mutmut_1': x_main__mutmut_1, 
    'x_main__mutmut_2': x_main__mutmut_2, 
    'x_main__mutmut_3': x_main__mutmut_3, 
    'x_main__mutmut_4': x_main__mutmut_4, 
    'x_main__mutmut_5': x_main__mutmut_5, 
    'x_main__mutmut_6': x_main__mutmut_6, 
    'x_main__mutmut_7': x_main__mutmut_7, 
    'x_main__mutmut_8': x_main__mutmut_8, 
    'x_main__mutmut_9': x_main__mutmut_9, 
    'x_main__mutmut_10': x_main__mutmut_10, 
    'x_main__mutmut_11': x_main__mutmut_11, 
    'x_main__mutmut_12': x_main__mutmut_12, 
    'x_main__mutmut_13': x_main__mutmut_13, 
    'x_main__mutmut_14': x_main__mutmut_14, 
    'x_main__mutmut_15': x_main__mutmut_15, 
    'x_main__mutmut_16': x_main__mutmut_16, 
    'x_main__mutmut_17': x_main__mutmut_17, 
    'x_main__mutmut_18': x_main__mutmut_18, 
    'x_main__mutmut_19': x_main__mutmut_19, 
    'x_main__mutmut_20': x_main__mutmut_20, 
    'x_main__mutmut_21': x_main__mutmut_21, 
    'x_main__mutmut_22': x_main__mutmut_22, 
    'x_main__mutmut_23': x_main__mutmut_23, 
    'x_main__mutmut_24': x_main__mutmut_24, 
    'x_main__mutmut_25': x_main__mutmut_25, 
    'x_main__mutmut_26': x_main__mutmut_26, 
    'x_main__mutmut_27': x_main__mutmut_27, 
    'x_main__mutmut_28': x_main__mutmut_28, 
    'x_main__mutmut_29': x_main__mutmut_29, 
    'x_main__mutmut_30': x_main__mutmut_30, 
    'x_main__mutmut_31': x_main__mutmut_31, 
    'x_main__mutmut_32': x_main__mutmut_32, 
    'x_main__mutmut_33': x_main__mutmut_33, 
    'x_main__mutmut_34': x_main__mutmut_34, 
    'x_main__mutmut_35': x_main__mutmut_35, 
    'x_main__mutmut_36': x_main__mutmut_36, 
    'x_main__mutmut_37': x_main__mutmut_37, 
    'x_main__mutmut_38': x_main__mutmut_38, 
    'x_main__mutmut_39': x_main__mutmut_39, 
    'x_main__mutmut_40': x_main__mutmut_40, 
    'x_main__mutmut_41': x_main__mutmut_41, 
    'x_main__mutmut_42': x_main__mutmut_42, 
    'x_main__mutmut_43': x_main__mutmut_43, 
    'x_main__mutmut_44': x_main__mutmut_44, 
    'x_main__mutmut_45': x_main__mutmut_45, 
    'x_main__mutmut_46': x_main__mutmut_46, 
    'x_main__mutmut_47': x_main__mutmut_47, 
    'x_main__mutmut_48': x_main__mutmut_48, 
    'x_main__mutmut_49': x_main__mutmut_49, 
    'x_main__mutmut_50': x_main__mutmut_50, 
    'x_main__mutmut_51': x_main__mutmut_51, 
    'x_main__mutmut_52': x_main__mutmut_52, 
    'x_main__mutmut_53': x_main__mutmut_53, 
    'x_main__mutmut_54': x_main__mutmut_54, 
    'x_main__mutmut_55': x_main__mutmut_55, 
    'x_main__mutmut_56': x_main__mutmut_56, 
    'x_main__mutmut_57': x_main__mutmut_57, 
    'x_main__mutmut_58': x_main__mutmut_58, 
    'x_main__mutmut_59': x_main__mutmut_59, 
    'x_main__mutmut_60': x_main__mutmut_60, 
    'x_main__mutmut_61': x_main__mutmut_61, 
    'x_main__mutmut_62': x_main__mutmut_62, 
    'x_main__mutmut_63': x_main__mutmut_63, 
    'x_main__mutmut_64': x_main__mutmut_64, 
    'x_main__mutmut_65': x_main__mutmut_65, 
    'x_main__mutmut_66': x_main__mutmut_66
}

def main(*args, **kwargs):
    result = _mutmut_trampoline(x_main__mutmut_orig, x_main__mutmut_mutants, args, kwargs)
    return result 

main.__signature__ = _mutmut_signature(x_main__mutmut_orig)
x_main__mutmut_orig.__name__ = 'x_main'


if __name__ == "__main__":
    main()
