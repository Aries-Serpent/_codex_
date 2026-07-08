"""End-to-end tests for RAG indexing and retrieval pipeline behavior.

Uses fake FAISS and SentenceTransformer implementations for offline determinism.
"""

from __future__ import annotations

import sys
import types
from dataclasses import dataclass
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")

_TORCH_312_BUG: bool = False
try:
    import torch as _torch

    _TORCH_312_BUG = sys.version_info >= (3, 12) and tuple(
        int(x) for x in _torch.__version__.split(".")[:2]
    ) < (2, 7)
except ImportError:
    _TORCH_312_BUG = False  # torch not installed; PyTorch 2.x isinstance bug cannot apply

_codex_rag = pytest.importorskip("codex.rag", reason="codex.rag not importable in this environment")
indexer = _codex_rag.indexer
_codex_rag_retriever = pytest.importorskip(
    "codex.rag.retriever", reason="codex.rag.retriever not importable"
)
Retriever = _codex_rag_retriever.Retriever


@dataclass
class FakeFaissIndex:
    """In-memory FAISS-like index for deterministic tests."""

    dimension: int
    vectors: list[np.ndarray]

    def add(self, vectors: np.ndarray) -> None:
        for vec in vectors:
            self.vectors.append(np.array(vec))

    @property
    def ntotal(self) -> int:
        return len(self.vectors)

    def search(self, queries: np.ndarray, top_k: int):
        data = np.vstack(self.vectors) if self.vectors else np.zeros((0, self.dimension))
        distances = []
        indices = []
        for query in queries:
            if len(data) == 0:
                distances.append(np.array([np.inf] * top_k))
                indices.append(np.array([-1] * top_k))
                continue
            l2 = np.sum((data - query) ** 2, axis=1)
            order = np.argsort(l2)[:top_k]
            distances.append(l2[order])
            indices.append(order)
        return np.array(distances), np.array(indices)


class FakeFaissModule:
    """Minimal FAISS API used by the indexer and retriever."""

    def IndexFlatL2(self, dimension: int) -> FakeFaissIndex:
        return FakeFaissIndex(dimension=dimension, vectors=[])

    def write_index(self, index: FakeFaissIndex, path: str) -> None:
        with open(path, "wb") as handle:
            np.save(
                handle,
                np.vstack(index.vectors) if index.vectors else np.zeros((0, index.dimension)),
            )

    def read_index(self, path: str) -> FakeFaissIndex:
        with open(path, "rb") as handle:
            data = np.load(handle)
        dimension = data.shape[1] if data.size else 3
        index = FakeFaissIndex(dimension=dimension, vectors=[])
        if data.size:
            index.add(data)
        return index


@dataclass
class SentenceTransformerSpy:
    """Capture SentenceTransformer initialization and encode calls."""

    calls: list[tuple[str, dict]]


@pytest.fixture()
def sentence_transformer_spy(monkeypatch: pytest.MonkeyPatch) -> SentenceTransformerSpy:
    """Provide a fake SentenceTransformer for embedding generation."""
    calls: list[tuple[str, dict]] = []

    class FakeSentenceTransformer:
        def __init__(self, model_name: str, **kwargs):
            self.model_name = model_name
            self.kwargs = kwargs
            calls.append((model_name, kwargs))

        def encode(self, texts, **kwargs):
            return np.array([[float(len(text)) % 5, 0.0, 1.0] for text in texts])

        def eval(self):
            return self

        def to(self, device):
            """Mock .to() method for device placement."""
            return self

        def to_empty(self, device):
            """Mock .to_empty() method for meta tensor handling."""
            return self

    fake_module = types.SimpleNamespace(SentenceTransformer=FakeSentenceTransformer)
    monkeypatch.setitem(sys.modules, "sentence_transformers", fake_module)
    # Also patch the module-level SentenceTransformer variable in retriever module
    from codex.rag import retriever as retriever_module

    monkeypatch.setattr(retriever_module, "SentenceTransformer", FakeSentenceTransformer)
    return SentenceTransformerSpy(calls=calls)


@pytest.fixture()
def fake_faiss(monkeypatch: pytest.MonkeyPatch) -> FakeFaissModule:
    """Provide a fake FAISS module for index persistence tests."""
    fake_module = FakeFaissModule()
    monkeypatch.setattr(indexer, "faiss", fake_module)
    return fake_module


@pytest.fixture()
def sample_text() -> str:
    """Provide sample text content for chunking and embedding."""
    return "Hello world. This is a test document for the RAG pipeline."


@pytest.mark.timeout(60)
def test_chunk_text_adjusts_overlap(sample_text: str) -> None:
    """Chunking should adjust overlap when it exceeds chunk size."""
    chunks = indexer.chunk_text(sample_text, chunk_size=10, overlap=128)
    assert chunks, "chunks is not valid"
    assert all(len(chunk[2]) <= 10 for chunk in chunks), "Collection must not be empty"


@pytest.mark.timeout(60)
@pytest.mark.skipif(
    _TORCH_312_BUG,
    reason="PyTorch 2.x + Python 3.12: isinstance() union-type bug in model device placement",
)
def test_embed_chunks_returns_embeddings(
    sentence_transformer_spy: SentenceTransformerSpy,
) -> None:
    """Embedding generation should return deterministic numpy arrays."""
    chunks = [(0, 5, "hello"), (6, 11, "world")]
    embeddings = indexer.embed_chunks(chunks, model_profile={"model_name": "fake"})
    assert embeddings.shape == (2, 3)
    assert sentence_transformer_spy.calls, "sentence_transf is not valid"


@pytest.mark.timeout(60)
@pytest.mark.skipif(
    _TORCH_312_BUG,
    reason="PyTorch 2.x + Python 3.12: isinstance() union-type bug in model device placement",
)
def test_persist_and_load_index_roundtrip(
    fake_faiss: FakeFaissModule,
    sentence_transformer_spy: SentenceTransformerSpy,
    tmp_path: Path,
) -> None:
    """Persisted indices should load with metadata intact."""
    chunks = [(0, 5, "hello"), (6, 11, "world")]
    embeddings = indexer.embed_chunks(chunks, model_profile={"model_name": "fake"})
    index_path = indexer.persist_index(
        index_name="demo",
        embeddings=embeddings,
        chunks=chunks,
        tenant_id="tenant",
        index_dir=str(tmp_path),
    )
    index, chunk_meta, meta = indexer.load_index(
        index_name="demo",
        tenant_id="tenant",
        index_dir=str(tmp_path),
    )
    assert index.ntotal == len(chunks), "Chunks must not be empty"
    assert len(chunk_meta) == len(chunks), "Chunk_meta must not be empty"
    assert meta.get("index_name") == "demo", "Condition must be true"
    assert (index_path / "metadata.json").exists(), "Data must not be empty"


@pytest.mark.timeout(60)
def test_build_index_from_files_missing_files(tmp_path: Path) -> None:
    """Building an index with only missing files should raise a ValueError."""
    missing = tmp_path / "missing.txt"
    with pytest.raises(ValueError, match="No valid input files found"):
        indexer.build_index_from_files([missing], index_name="demo")


@pytest.mark.timeout(60)
def test_build_index_from_files_empty_file(
    tmp_path: Path,
    sentence_transformer_spy: SentenceTransformerSpy,
) -> None:
    """Empty files should raise a ValueError when no chunks are generated."""
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="Input files contain no text content"):
        indexer.build_index_from_files([empty_file], index_name="demo")


@pytest.mark.timeout(60)
@pytest.mark.skipif(
    _TORCH_312_BUG,
    reason="PyTorch 2.x + Python 3.12: isinstance() union-type bug in model device placement",
)
def test_retriever_query_returns_results(
    fake_faiss: FakeFaissModule,
    sentence_transformer_spy: SentenceTransformerSpy,
    tmp_path: Path,
) -> None:
    """Retrieval should return scored results with provenance fields."""
    chunks = [(0, 5, "hello"), (6, 11, "world")]
    embeddings = indexer.embed_chunks(chunks, model_profile={"model_name": "fake"})
    indexer.persist_index(
        index_name="demo",
        embeddings=embeddings,
        chunks=chunks,
        tenant_id="tenant",
        index_dir=str(tmp_path),
    )
    retriever = Retriever(index_dir=str(tmp_path), index_name="demo", tenant_id="tenant")
    results = retriever.query("hello", top_k=2)
    assert results, "Result must not be empty"
    first = results[0]
    assert {"text", "file", "start_line", "end_line", "score", "generated_at"}.issubset(first)


@pytest.mark.timeout(60)
@pytest.mark.skipif(
    _TORCH_312_BUG,
    reason="PyTorch 2.x + Python 3.12: isinstance() union-type bug in model device placement",
)
def test_retriever_query_min_score_filters(
    fake_faiss: FakeFaissModule,
    sentence_transformer_spy: SentenceTransformerSpy,
    tmp_path: Path,
) -> None:
    """min_score should filter out results beyond the threshold."""
    chunks = [(0, 5, "hello"), (6, 11, "world")]
    embeddings = indexer.embed_chunks(chunks, model_profile={"model_name": "fake"})
    indexer.persist_index(
        index_name="demo",
        embeddings=embeddings,
        chunks=chunks,
        tenant_id="tenant",
        index_dir=str(tmp_path),
    )
    retriever = Retriever(index_dir=str(tmp_path), index_name="demo", tenant_id="tenant")
    # Query with a very strict min_score threshold that filters out all results
    # min_score acts as maximum L2 distance (lower is better)
    # Use a negative value to ensure all results are filtered
    results = retriever.query("hello", top_k=2, min_score=-1.0)
    assert results == [], "Result must not be empty"


@pytest.mark.timeout(60)
@pytest.mark.skipif(
    _TORCH_312_BUG,
    reason="PyTorch 2.x + Python 3.12: isinstance() union-type bug in model device placement",
)
def test_retriever_query_empty_index_returns_empty(
    fake_faiss: FakeFaissModule,
    sentence_transformer_spy: SentenceTransformerSpy,
    tmp_path: Path,
) -> None:
    """Queries against missing indices should return empty lists."""
    retriever = Retriever(index_dir=str(tmp_path), index_name="missing", tenant_id="tenant")
    retriever.faiss_index = None
    assert retriever.query("hello") == [], "Condition must be true"
