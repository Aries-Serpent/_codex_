from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List

import pytest


def _resolve_model_name(model_name: str) -> str:
    """Ensure model name uses the sentence-transformers namespace."""
    if "/" in model_name:
        return model_name
    return f"sentence-transformers/{model_name}"


def has_meta_tensors(model) -> List[str]:
    """Return parameter names that are on the meta device."""
    meta_params: List[str] = []
    for name, param in model.named_parameters():
        if getattr(param, "device", None) is not None and param.device.type == "meta":
            meta_params.append(name)
    return meta_params


@pytest.fixture
def small_model_name() -> str:
    """Return a fast, small model name for regression tests."""
    return "all-MiniLM-L6-v2"


@pytest.fixture
def temp_cache_dir(tmp_path: Path) -> Path:
    """Create a temporary cache directory for model downloads."""
    cache_dir = tmp_path / "model-cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


pytestmark = [pytest.mark.regression, pytest.mark.timeout(300)]


@pytest.mark.timeout(300)
def test_embeddings_no_meta_tensors(
    tmp_path: Path, small_model_name: str, temp_cache_dir: Path
) -> None:
    """
    Verify LocalSentenceTransformerProvider initializes without meta tensors.

    This guards against regressions where specifying device='cpu' or redundant
    .to('cpu') calls can yield meta device parameters in sentence-transformers 3.x.
    """
    pytest.importorskip("sentence_transformers")
    torch = pytest.importorskip("torch")

    from codex.rag.embeddings import LocalSentenceTransformerProvider

    model = LocalSentenceTransformerProvider(
        model_name=_resolve_model_name(small_model_name),
        cache_dir=str(temp_cache_dir),
    )

    meta_params = has_meta_tensors(model.model)
    assert not meta_params, f"Found meta tensors in embeddings model: {meta_params}"

    embedding = model.model.encode("Meta tensor regression check", convert_to_tensor=True)
    assert isinstance(embedding, torch.Tensor), "Expected tensor embedding output"
    assert embedding.device.type == "cpu", "Embedding tensor should be on CPU"


@pytest.mark.timeout(300)
def test_indexer_no_meta_tensors(
    tmp_path: Path, small_model_name: str, temp_cache_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Verify the indexer embedding path loads sentence-transformers without meta tensors.
    """
    st_module = pytest.importorskip("sentence_transformers")

    from codex.rag import indexer

    captured_models: List[object] = []
    original_cls = st_module.SentenceTransformer

    def _capturing_sentence_transformer(*args, **kwargs):
        model = original_cls(*args, **kwargs)
        captured_models.append(model)
        return model

    monkeypatch.setattr(st_module, "SentenceTransformer", _capturing_sentence_transformer)

    chunks = [(0, 10, "Indexing text for meta tensor regression")]
    embeddings = indexer.embed_chunks(
        chunks,
        model_profile={
            "model_name": _resolve_model_name(small_model_name),
            "cache_dir": str(temp_cache_dir),
        },
    )

    assert embeddings.shape[0] == 1, "Expected one embedding from indexer"
    assert captured_models, "Expected indexer to instantiate SentenceTransformer"

    meta_params = has_meta_tensors(captured_models[0])
    assert not meta_params, f"Found meta tensors in indexer model: {meta_params}"


@pytest.mark.timeout(300)
def test_retriever_no_meta_tensors(
    tmp_path: Path, small_model_name: str, temp_cache_dir: Path
) -> None:
    """
    Verify Retriever loads embedding model without meta tensors.
    """
    pytest.importorskip("sentence_transformers")
    pytest.importorskip("faiss")

    from codex.rag.retriever import Retriever

    retriever = Retriever(
        index_dir=str(tmp_path / "indices"),
        index_name="missing",
        tenant_id="default",
        model_name=_resolve_model_name(small_model_name),
        cache_dir=str(temp_cache_dir),
    )

    meta_params = has_meta_tensors(retriever.model)
    assert not meta_params, f"Found meta tensors in retriever model: {meta_params}"


@pytest.mark.timeout(300)
def test_sentence_transformer_direct_init(
    tmp_path: Path, small_model_name: str, temp_cache_dir: Path
) -> None:
    """Direct SentenceTransformer init should avoid meta tensors without device args."""
    st_module = pytest.importorskip("sentence_transformers")
    torch = pytest.importorskip("torch")

    model = st_module.SentenceTransformer(
        _resolve_model_name(small_model_name),
        cache_folder=str(temp_cache_dir),
        trust_remote_code=False,
    )
    model.eval()

    meta_params = has_meta_tensors(model)
    assert not meta_params, f"Found meta tensors in direct init: {meta_params}"

    embedding = model.encode("Direct init regression", convert_to_tensor=True)
    assert isinstance(embedding, torch.Tensor), "Expected tensor embedding output"
    assert embedding.device.type == "cpu", "Direct init embedding should be on CPU"


@pytest.mark.timeout(300)
def test_model_inference_cpu_only(
    tmp_path: Path, small_model_name: str, temp_cache_dir: Path
) -> None:
    """
    Verify embeddings and retriever models produce CPU outputs without device transfers.
    """
    st_module = pytest.importorskip("sentence_transformers")
    torch = pytest.importorskip("torch")
    pytest.importorskip("faiss")

    from codex.rag.retriever import Retriever

    model = st_module.SentenceTransformer(
        _resolve_model_name(small_model_name),
        cache_folder=str(temp_cache_dir),
        trust_remote_code=False,
    )
    model.eval()

    embedding = model.encode("CPU inference check", convert_to_tensor=True)
    assert embedding.device.type == "cpu", "SentenceTransformer output should be on CPU"

    retriever = Retriever(
        index_dir=str(tmp_path / "indices"),
        index_name="missing",
        tenant_id="default",
        model_name=_resolve_model_name(small_model_name),
        cache_dir=str(temp_cache_dir),
    )
    retriever_embedding = retriever.model.encode("Retriever CPU output", convert_to_tensor=True)
    assert retriever_embedding.device.type == "cpu", "Retriever output should be on CPU"


@pytest.mark.timeout(300)
def test_no_redundant_device_transfers() -> None:
    """Ensure RAG code does not call model.to() explicitly."""
    rag_dir = Path(__file__).resolve().parents[1] / "src" / "codex" / "rag"
    python_files = list(rag_dir.glob("*.py"))

    assert python_files, "Expected RAG Python files to scan for device transfers"

    for path in python_files:
        content = path.read_text(encoding="utf-8")
        assert not re.search(r"\.to\(\s*['\"]cpu['\"]\s*\)", content), (
            f"Found explicit .to('cpu') in {path}"
        )
        assert not re.search(r"\.to\(\s*['\"]cuda['\"]\s*\)", content), (
            f"Found explicit .to('cuda') in {path}"
        )


@pytest.mark.timeout(300)
def test_sentence_transformers_version() -> None:
    """Validate sentence-transformers version is at least 3.3.0."""
    st_module = pytest.importorskip("sentence_transformers")
    from packaging.version import parse as parse_version

    version = parse_version(st_module.__version__)
    assert version >= parse_version("3.3.0"), (
        f"sentence-transformers version too old: {st_module.__version__}"
    )
