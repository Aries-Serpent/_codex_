"""Behavior tests for RAG index persistence and tenant lifecycle branches."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from aries_serpent_core.rag import indexer


class _FakeFaissIndex:
    def __init__(self, dimension: int = 2) -> None:
        self.d = dimension
        self.ntotal = 0
        self.vectors: list[np.ndarray] = []

    def add(self, embeddings) -> None:
        self.vectors = [np.asarray(row, dtype=np.float32) for row in embeddings]
        self.ntotal = len(self.vectors)

    def reconstruct(self, position: int):
        return self.vectors[position]


class _FakeFaiss:
    def __init__(self) -> None:
        self.written = []
        self.index = _FakeFaissIndex()

    def IndexFlatL2(self, dimension: int):
        self.index = _FakeFaissIndex(dimension)
        return self.index

    def write_index(self, value, path: str) -> None:
        self.written.append((value, path))
        Path(path).write_bytes(b"faiss")

    def read_index(self, path: str):
        assert Path(path).is_file()
        return self.index


def test_chunk_text_covers_validation_and_sentence_boundaries() -> None:
    assert indexer.chunk_text("") == []
    with pytest.raises(ValueError):
        indexer.chunk_text("text", chunk_size=0)
    with pytest.raises(ValueError):
        indexer.chunk_text("text", overlap=-1)
    with pytest.raises(ValueError):
        indexer.chunk_text("text", chunk_size=8, overlap=8)

    chunks = indexer.chunk_text("one. two! three? four", chunk_size=10, overlap=128)
    assert chunks
    assert "one." in chunks[0][2]


def test_persist_load_and_list_index_lifecycle(tmp_path, monkeypatch) -> None:
    fake_faiss = _FakeFaiss()
    monkeypatch.setattr(indexer, "faiss", fake_faiss)
    chunks = [(0, 5, "hello"), (5, 10, "world")]
    embeddings = np.array([[1, 2], [3, 4]], dtype=np.float64)

    path = indexer.persist_index(
        "docs",
        embeddings,
        chunks,
        metadata={"source": "unit"},
        tenant_id="tenant",
        index_dir=str(tmp_path),
    )

    assert path.is_dir()
    assert fake_faiss.written
    loaded, loaded_chunks, metadata = indexer.load_index(
        "docs", tenant_id="tenant", index_dir=str(tmp_path)
    )
    assert loaded.ntotal == 2
    assert [row["text"] for row in loaded_chunks] == ["hello", "world"]
    assert metadata["source"] == "unit"
    assert indexer.list_indices("tenant", str(tmp_path)) == ["docs"]
    assert indexer.get_index_metadata("docs", "tenant", str(tmp_path))["num_vectors"] == 2
    assert indexer.delete_index("docs", "tenant", str(tmp_path))

    with pytest.raises(FileNotFoundError):
        indexer.delete_index("missing", "tenant", str(tmp_path))


def test_load_index_defaults_missing_json_to_empty_values(tmp_path, monkeypatch) -> None:
    fake_faiss = _FakeFaiss()
    monkeypatch.setattr(indexer, "faiss", fake_faiss)
    path = tmp_path / "tenant" / "bare"
    path.mkdir(parents=True)
    (path / "index.faiss").write_bytes(b"faiss")

    loaded, chunks, metadata = indexer.load_index("bare", "tenant", str(tmp_path))
    assert loaded is fake_faiss.index
    assert chunks == []
    assert metadata == {}

    (path / "metadata.json").write_text("[]")
    with pytest.raises(TypeError, match="JSON object"):
        indexer.get_index_metadata("bare", "tenant", str(tmp_path))


def test_build_index_from_files_covers_empty_and_encoding_failures(tmp_path, monkeypatch) -> None:
    empty = tmp_path / "empty.txt"
    empty.write_text("")
    with pytest.raises(ValueError, match="no text content"):
        indexer.build_index_from_files([empty], "docs", index_dir=str(tmp_path))

    invalid = tmp_path / "invalid.txt"
    invalid.write_bytes(b"\xff")
    with pytest.raises(ValueError, match="file.*failed to process"):
        indexer.build_index_from_files([invalid], "docs", index_dir=str(tmp_path))


def test_build_index_from_files_falls_back_to_offline_provider(tmp_path, monkeypatch) -> None:
    source = tmp_path / "source.txt"
    source.write_text("hello world")

    monkeypatch.setattr(
        indexer, "embed_chunks", lambda _chunks: (_ for _ in ()).throw(ImportError())
    )

    class Provider:
        __class__ = type("TfidfEmbeddingProvider", (), {})

        @staticmethod
        def encode(_texts):
            return np.array([[1.0, 0.0]], dtype=np.float32)

    monkeypatch.setattr(
        "aries_serpent_core.rag.embeddings.create_embedding_provider",
        lambda **_kwargs: Provider(),
    )
    fake_faiss = _FakeFaiss()
    monkeypatch.setattr(indexer, "faiss", fake_faiss)

    path = indexer.build_index_from_files([source], "docs", index_dir=str(tmp_path))
    metadata = json.loads((path / "metadata.json").read_text())
    assert metadata["embedding_provider"] == "TfidfEmbeddingProvider"
    assert metadata["total_chunks"] == 1


def test_tenant_create_update_and_delete_outcomes(tmp_path, monkeypatch) -> None:
    source = tmp_path / "source.txt"
    source.write_text("content")

    def fake_build(**kwargs):
        created_path = Path(kwargs["index_dir"]) / kwargs["tenant_id"] / kwargs["index_name"]
        created_path.mkdir(parents=True, exist_ok=True)
        return created_path

    monkeypatch.setattr(indexer, "build_index_from_files", fake_build)

    missing_files = indexer.manage_tenant_indices(
        "tenant", "create", ["docs"], index_dir=str(tmp_path / "indices")
    )
    assert not missing_files.success

    created = indexer.manage_tenant_indices(
        "tenant",
        indexer.IndexOperation.CREATE,
        ["docs"],
        index_dir=str(tmp_path / "indices"),
        files=[source],
    )
    assert created.success
    assert created.details == {"created_indices": ["docs"]}

    updated = indexer.manage_tenant_indices(
        "tenant",
        "update",
        ["docs"],
        index_dir=str(tmp_path / "indices"),
        files=[source],
    )
    assert updated.success

    deleted = indexer.manage_tenant_indices(
        "tenant", "delete", ["docs"], index_dir=str(tmp_path / "indices")
    )
    assert deleted.success

    no_delete = indexer.manage_tenant_indices(
        "tenant", "delete", ["missing"], index_dir=str(tmp_path / "indices")
    )
    assert not no_delete.success


def test_tenant_merge_and_list_cover_partial_metadata(tmp_path, monkeypatch) -> None:
    tenant_dir = tmp_path / "tenant"
    complete = tenant_dir / "complete"
    complete.mkdir(parents=True)
    (complete / "index.faiss").write_bytes(b"faiss")
    (complete / "metadata.json").write_text(
        json.dumps({"num_vectors": 1, "dimension": 2, "created_at": "now"})
    )
    partial = tenant_dir / "partial"
    partial.mkdir()
    (partial / "index.faiss").write_bytes(b"faiss")

    listed_missing = indexer.manage_tenant_indices("missing", "list", [], index_dir=str(tmp_path))
    assert listed_missing.success and listed_missing.details == {"indices": []}

    listed = indexer.manage_tenant_indices("tenant", "list", [], index_dir=str(tmp_path))
    assert listed.success
    assert {row["name"] for row in listed.details["indices"]} == {"complete", "partial"}

    fake_index = _FakeFaissIndex()
    fake_index.add(np.array([[1.0, 2.0]], dtype=np.float32))
    monkeypatch.setattr(
        indexer,
        "load_index",
        lambda name, *_args, **_kwargs: (
            fake_index,
            [{"start": 0, "end": 5, "text": name}],
            {"source": name},
        ),
    )
    captured = {}

    def persist(**kwargs):
        captured.update(kwargs)
        return tmp_path / kwargs["index_name"]

    monkeypatch.setattr(indexer, "persist_index", persist)
    merged = indexer.manage_tenant_indices(
        "tenant",
        "merge",
        ["complete", "partial"],
        index_dir=str(tmp_path),
        merge_name="merged",
    )
    assert merged.success
    assert captured["metadata"]["merged_from"] == ["complete", "partial"]
    assert len(captured["chunks"]) == 2


def test_tenant_lifecycle_rejects_invalid_inputs(tmp_path, monkeypatch) -> None:
    invalid = indexer.manage_tenant_indices("tenant", "unknown", ["docs"], index_dir=str(tmp_path))
    assert not invalid.success

    merge_missing = indexer.manage_tenant_indices(
        "tenant", "merge", ["docs"], index_dir=str(tmp_path)
    )
    assert not merge_missing.success

    missing_update = indexer.manage_tenant_indices(
        "tenant", "update", ["docs"], index_dir=str(tmp_path)
    )
    assert not missing_update.success

    monkeypatch.setattr(
        indexer, "load_index", lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("bad"))
    )
    failed_merge = indexer.manage_tenant_indices(
        "tenant",
        "merge",
        ["bad"],
        index_dir=str(tmp_path),
        merge_name="merged",
    )
    assert not failed_merge.success


def test_embed_chunks_covers_empty_filter_and_encode_errors(monkeypatch) -> None:
    assert indexer.embed_chunks([]).size == 0

    monkeypatch.setattr(indexer.importlib.util, "find_spec", lambda _name: object())

    from aries_serpent_core.rag import _model_utils

    class Model:
        max_seq_length = 128

        def encode(self, *_args, **_kwargs):
            raise IndexError("bad token")

    monkeypatch.setattr(_model_utils, "safe_load_sentence_transformer", lambda *_args: Model())
    with pytest.raises(ValueError, match="No valid text"):
        indexer.embed_chunks([(0, 1, " ")])
    with pytest.raises(RuntimeError, match="IndexError"):
        indexer.embed_chunks([(0, 4, "text")])


def test_embed_chunks_reraises_model_load_errors(monkeypatch) -> None:
    monkeypatch.setattr(indexer.importlib.util, "find_spec", lambda _name: object())

    from aries_serpent_core.rag import _model_utils

    monkeypatch.setattr(
        _model_utils,
        "safe_load_sentence_transformer",
        lambda *_args: (_ for _ in ()).throw(RuntimeError("load failed")),
    )

    with pytest.raises(RuntimeError, match="load failed"):
        indexer.embed_chunks([(0, 4, "text")])


def test_persist_and_load_require_faiss_and_matching_lengths(tmp_path, monkeypatch) -> None:
    with pytest.raises(ValueError, match="empty embeddings"):
        indexer.persist_index("docs", np.array([]), [], index_dir=str(tmp_path))
    with pytest.raises(ValueError, match="Mismatch"):
        indexer.persist_index(
            "docs",
            np.array([[1.0]]),
            [],
            index_dir=str(tmp_path),
        )

    monkeypatch.setattr(indexer, "faiss", None)
    with pytest.raises(ImportError, match="faiss-cpu"):
        indexer.persist_index(
            "docs",
            np.array([[1.0]]),
            [(0, 1, "x")],
            index_dir=str(tmp_path),
        )
    with pytest.raises(ImportError, match="faiss-cpu"):
        indexer.load_index("docs", index_dir=str(tmp_path))


def test_load_and_list_cover_missing_artifacts_and_non_indices(tmp_path, monkeypatch) -> None:
    fake_faiss = _FakeFaiss()
    monkeypatch.setattr(indexer, "faiss", fake_faiss)

    tenant = tmp_path / "tenant"
    tenant.mkdir()
    with pytest.raises(FileNotFoundError, match="Index not found"):
        indexer.load_index("missing", "tenant", str(tmp_path))

    no_faiss = tenant / "no_faiss"
    no_faiss.mkdir()
    with pytest.raises(FileNotFoundError, match="FAISS index file"):
        indexer.load_index("no_faiss", "tenant", str(tmp_path))

    (tenant / "ordinary.txt").write_text("not an index")
    (tenant / "empty_dir").mkdir()
    metadata_only = tenant / "metadata_only"
    metadata_only.mkdir()
    (metadata_only / "metadata.json").write_text("{}")
    symlink = tenant / "linked"
    symlink.symlink_to(no_faiss, target_is_directory=True)

    assert indexer.list_indices("tenant", str(tmp_path)) == ["metadata_only"]
    with pytest.raises(FileNotFoundError, match="metadata not found"):
        indexer.get_index_metadata("no_faiss", "tenant", str(tmp_path))


def test_merge_wrapper_and_failed_tenant_operations(tmp_path, monkeypatch) -> None:
    captured = {}
    real_manage = indexer.manage_tenant_indices

    def manage(*_args, **kwargs):
        captured.update(kwargs)
        return SimpleNamespace(success=True)

    monkeypatch.setattr(indexer, "manage_tenant_indices", manage)
    result = indexer.merge_indices(["a", "b"], "merged", "tenant", str(tmp_path))
    assert result.success
    assert captured["merge_name"] == "merged"

    monkeypatch.setattr(indexer, "manage_tenant_indices", real_manage)
    monkeypatch.setattr(
        indexer,
        "build_index_from_files",
        lambda **_kwargs: (_ for _ in ()).throw(OSError("write failed")),
    )
    failed_create = indexer.manage_tenant_indices(
        "tenant",
        "create",
        ["docs"],
        index_dir=str(tmp_path),
        files=[tmp_path / "source"],
    )
    assert not failed_create.success
